import hashlib
import json
from pathlib import Path

import pytest

from synccut.models import Dialogue, Scene, Visual
from synccut.narration_package import (
    build_narration_sections,
    narration_manifest,
    prepare_narration_package,
)
from synccut.validators import SyncCutError


def scene(
    scene_id: str,
    scene_order: int,
    section: str,
    section_order: int,
    section_key: str,
    paragraphs: list[str],
) -> Scene:
    return Scene(
        scene_id=scene_id,
        scene_order=scene_order,
        section=section,
        section_order=section_order,
        section_key=section_key,
        dialogue=Dialogue(text=" ".join(paragraphs), paragraphs=paragraphs),
        visual=Visual(type="AI_VIDEO", prompt=None, data=None),
    )


def write_scenes_json(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "metadata": {"schema_version": "1.1", "total_scenes": 3},
                "scenes": [
                    {
                        "scene_id": "scene_003",
                        "scene_order": 3,
                        "section": "INTRO",
                        "section_order": 2,
                        "section_key": "02_INTRO",
                        "dialogue": {
                            "text": "Third scene.",
                            "paragraphs": ["Third scene."],
                        },
                        "visual": {"type": "AI_VIDEO", "prompt": None, "data": None},
                    },
                    {
                        "scene_id": "scene_002",
                        "scene_order": 2,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "dialogue": {
                            "text": "Second paragraph text.",
                            "paragraphs": ["Second", "paragraph text."],
                        },
                        "visual": {"type": "B-ROLL", "prompt": None, "data": None},
                    },
                    {
                        "scene_id": "scene_001",
                        "scene_order": 1,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "dialogue": {
                            "text": "First scene.",
                            "paragraphs": ["First scene."],
                        },
                        "visual": {"type": "AI_VIDEO", "prompt": None, "data": None},
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_build_sections_groups_by_section_key_and_preserves_order() -> None:
    sections = build_narration_sections(
        [
            scene("scene_003", 3, "INTRO", 2, "02_INTRO", ["Third."]),
            scene("scene_002", 2, "HOOK", 1, "01_HOOK", ["Second."]),
            scene("scene_001", 1, "HOOK", 1, "01_HOOK", ["First."]),
        ]
    )

    assert [section.section_key for section in sections] == ["01_HOOK", "02_INTRO"]
    assert sections[0].scene_ids == ["scene_001", "scene_002"]
    assert sections[1].scene_ids == ["scene_003"]


def test_text_assembly_uses_paragraphs_and_blank_lines() -> None:
    sections = build_narration_sections(
        [
            scene("scene_001", 1, "HOOK", 1, "01_HOOK", ["First paragraph.", "Second paragraph."]),
            scene("scene_002", 2, "HOOK", 1, "01_HOOK", ["Next scene."]),
        ]
    )

    assert sections[0].narration_text == (
        "First paragraph.\n\nSecond paragraph.\n\nNext scene."
    )


def test_hash_is_stable_full_sha256_format() -> None:
    section = build_narration_sections(
        [scene("scene_001", 1, "HOOK", 1, "01_HOOK", ["Hello."])]
    )[0]

    expected = hashlib.sha256("Hello.".encode("utf-8")).hexdigest()
    assert section.text_hash == f"sha256:{expected}"
    assert len(section.text_hash) == len("sha256:") + 64


def test_manifest_includes_expected_metadata_and_section_fields(tmp_path) -> None:
    sections = build_narration_sections(
        [scene("scene_001", 1, "HOOK", 1, "01_HOOK", ["Hello."])]
    )

    manifest = narration_manifest(
        scenes_path=tmp_path / "scenes.json",
        sections=sections,
        total_scenes=1,
    )

    assert manifest["metadata"] == {
        "schema_version": "0.1",
        "generated_by": "synccut prepare-narration",
        "source_scenes": str(tmp_path / "scenes.json"),
        "total_sections": 1,
        "total_scenes": 1,
    }
    assert manifest["sections"][0]["section_key"] == "01_HOOK"
    assert manifest["sections"][0]["scene_ids"] == ["scene_001"]
    assert manifest["sections"][0]["text_path"] == "01_HOOK.txt"
    assert manifest["sections"][0]["narration_text"] == "Hello."
    assert manifest["sections"][0]["expected_audio_path"] == "01_HOOK.mp3"
    assert manifest["sections"][0]["expected_alignment_path"] == "01_HOOK_alignment_tmp.json"


def test_prepare_writes_manifest_and_text_files(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"

    result = prepare_narration_package(scenes_json, out_dir)

    assert result.written == 3
    assert result.reused == 0
    assert result.blocked == 0
    assert (out_dir / "01_HOOK.txt").read_text(encoding="utf-8") == (
        "First scene.\n\nSecond\n\nparagraph text.\n"
    )
    assert (out_dir / "02_INTRO.txt").read_text(encoding="utf-8") == "Third scene.\n"
    manifest = json.loads((out_dir / "narration_manifest.json").read_text(encoding="utf-8"))
    assert manifest["metadata"]["total_sections"] == 2
    assert manifest["metadata"]["total_scenes"] == 3


def test_rerun_reuses_identical_files(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"
    prepare_narration_package(scenes_json, out_dir)

    result = prepare_narration_package(scenes_json, out_dir)

    assert result.written == 0
    assert result.reused == 3
    assert result.blocked == 0


def test_changed_existing_file_blocks_without_overwrite(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"
    prepare_narration_package(scenes_json, out_dir)
    (out_dir / "01_HOOK.txt").write_text("changed\n", encoding="utf-8")

    with pytest.raises(SyncCutError, match="output exists and differs"):
        prepare_narration_package(scenes_json, out_dir)


def test_overwrite_replaces_changed_files(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"
    prepare_narration_package(scenes_json, out_dir)
    (out_dir / "01_HOOK.txt").write_text("changed\n", encoding="utf-8")

    result = prepare_narration_package(scenes_json, out_dir, overwrite=True)

    assert result.written == 1
    assert result.reused == 2
    assert (out_dir / "01_HOOK.txt").read_text(encoding="utf-8") == (
        "First scene.\n\nSecond\n\nparagraph text.\n"
    )


def test_dry_run_writes_no_files_and_reports_counts(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"

    result = prepare_narration_package(scenes_json, out_dir, dry_run=True)

    assert result.dry_run is True
    assert result.written == 3
    assert result.reused == 0
    assert result.blocked == 0
    assert not out_dir.exists()


def test_dry_run_reports_blocked_different_files_without_raising(tmp_path) -> None:
    scenes_json = write_scenes_json(tmp_path / "scenes.json")
    out_dir = tmp_path / "generated" / "narration"
    out_dir.mkdir(parents=True)
    (out_dir / "01_HOOK.txt").write_text("changed\n", encoding="utf-8")

    result = prepare_narration_package(scenes_json, out_dir, dry_run=True)

    assert result.written == 2
    assert result.reused == 0
    assert result.blocked == 1
