from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from synccut.models import Scene
from synccut.scenes_loader import load_scenes
from synccut.validators import SyncCutError


MANIFEST_FILENAME = "narration_manifest.json"
PACKAGE_SCHEMA_VERSION = "0.1"
PACKAGE_GENERATOR = "synccut prepare-narration"


@dataclass(frozen=True)
class NarrationSection:
    section_key: str
    section: str
    section_order: int
    scene_ids: list[str]
    scene_count: int
    text_path: str
    narration_text: str
    text_hash: str
    expected_audio_path: str
    expected_alignment_path: str


@dataclass(frozen=True)
class NarrationPackageResult:
    out_dir: Path
    manifest_path: Path
    sections: list[NarrationSection]
    total_scenes: int
    written: int
    reused: int
    blocked: int
    dry_run: bool

    @property
    def created(self) -> int:
        return self.written


def build_narration_sections(scenes: list[Scene]) -> list[NarrationSection]:
    section_groups: dict[str, list[Scene]] = {}
    for scene in scenes:
        section_groups.setdefault(scene.section_key, []).append(scene)

    sections: list[NarrationSection] = []
    for section_key, section_scenes in section_groups.items():
        sorted_scenes = sorted(section_scenes, key=lambda item: (item.scene_order, item.scene_id))
        first_scene = sorted_scenes[0]
        narration_text = "\n\n".join(_scene_narration_text(scene) for scene in sorted_scenes)

        _validate_package_filename(f"{section_key}.txt", section_key=section_key)
        _validate_package_filename(f"{section_key}.mp3", section_key=section_key)
        _validate_package_filename(
            f"{section_key}_alignment_tmp.json",
            section_key=section_key,
        )

        sections.append(
            NarrationSection(
                section_key=section_key,
                section=first_scene.section,
                section_order=first_scene.section_order,
                scene_ids=[scene.scene_id for scene in sorted_scenes],
                scene_count=len(sorted_scenes),
                text_path=f"{section_key}.txt",
                narration_text=narration_text,
                text_hash=_text_hash(narration_text),
                expected_audio_path=f"{section_key}.mp3",
                expected_alignment_path=f"{section_key}_alignment_tmp.json",
            )
        )

    return sorted(sections, key=lambda item: (item.section_order, item.section_key))


def prepare_narration_package(
    scenes_path: Path,
    out_dir: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
) -> NarrationPackageResult:
    _, scenes = load_scenes(scenes_path)
    sections = build_narration_sections(scenes)
    manifest_path = out_dir / MANIFEST_FILENAME
    planned_files = _planned_files(
        scenes_path=scenes_path,
        out_dir=out_dir,
        manifest_path=manifest_path,
        sections=sections,
        total_scenes=len(scenes),
    )

    existing_same = 0
    existing_different: list[Path] = []
    missing = 0
    for path, content in planned_files.items():
        if not path.exists():
            missing += 1
            continue
        if path.read_text(encoding="utf-8") == content:
            existing_same += 1
        else:
            existing_different.append(path)

    if dry_run:
        return NarrationPackageResult(
            out_dir=out_dir,
            manifest_path=manifest_path,
            sections=sections,
            total_scenes=len(scenes),
            written=missing,
            reused=existing_same,
            blocked=len(existing_different),
            dry_run=True,
        )

    if existing_different and not overwrite:
        conflicts = ", ".join(str(path) for path in existing_different)
        raise SyncCutError(
            f"output exists and differs: {conflicts}; rerun with --overwrite to replace"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for path, content in planned_files.items():
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        path.write_text(content, encoding="utf-8")
        written += 1

    return NarrationPackageResult(
        out_dir=out_dir,
        manifest_path=manifest_path,
        sections=sections,
        total_scenes=len(scenes),
        written=written,
        reused=existing_same,
        blocked=0,
        dry_run=False,
    )


def narration_manifest(
    *,
    scenes_path: Path,
    sections: list[NarrationSection],
    total_scenes: int,
) -> dict:
    return {
        "metadata": {
            "schema_version": PACKAGE_SCHEMA_VERSION,
            "generated_by": PACKAGE_GENERATOR,
            "source_scenes": str(scenes_path),
            "total_sections": len(sections),
            "total_scenes": total_scenes,
        },
        "sections": [
            {
                "section_key": section.section_key,
                "section": section.section,
                "section_order": section.section_order,
                "scene_ids": section.scene_ids,
                "scene_count": section.scene_count,
                "text_path": section.text_path,
                "narration_text": section.narration_text,
                "text_hash": section.text_hash,
                "expected_audio_path": section.expected_audio_path,
                "expected_alignment_path": section.expected_alignment_path,
            }
            for section in sections
        ],
    }


def _planned_files(
    *,
    scenes_path: Path,
    out_dir: Path,
    manifest_path: Path,
    sections: list[NarrationSection],
    total_scenes: int,
) -> dict[Path, str]:
    planned = {
        out_dir / section.text_path: section.narration_text + "\n"
        for section in sections
    }
    manifest = narration_manifest(
        scenes_path=scenes_path,
        sections=sections,
        total_scenes=total_scenes,
    )
    planned[manifest_path] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return planned


def _scene_narration_text(scene: Scene) -> str:
    return "\n\n".join(scene.dialogue.paragraphs)


def _text_hash(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _validate_package_filename(filename: str, *, section_key: str) -> None:
    path = Path(filename)
    if path.name != filename or path.is_absolute() or ".." in path.parts:
        raise SyncCutError(f"{section_key}: section_key cannot be used as a safe filename")
