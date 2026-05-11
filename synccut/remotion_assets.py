from __future__ import annotations

import filecmp
import json
import shutil
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string


@dataclass(frozen=True)
class PreparedAudioAsset:
    section_key: str
    source_path: str
    destination_path: str
    public_path: str


@dataclass(frozen=True)
class RemotionAssetPrepareResult:
    props_path: Path
    public_dir: Path
    audio_dir: Path
    copied: int
    reused: int
    overwritten: int
    audio_assets: list[PreparedAudioAsset]


def load_remotion_props(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to read Remotion props: {exc}") from exc

    return require_mapping(data, context=str(path))


def prepare_remotion_audio_assets(
    props: dict[str, Any], props_path: Path, out_dir: Path
) -> tuple[dict[str, Any], RemotionAssetPrepareResult]:
    source_props = require_mapping(props, context=str(props_path))
    audio_entries = _audio_entries(source_props, props_path)

    updated_props = deepcopy(source_props)
    audio_dir = out_dir / "audio"
    try:
        audio_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SyncCutError(f"{audio_dir}: failed to create audio asset directory: {exc}") from exc

    copied = 0
    reused = 0
    overwritten = 0
    prepared_assets: list[PreparedAudioAsset] = []
    by_destination: dict[str, Path] = {}
    public_paths_by_key_path: dict[tuple[str, str], str] = {}

    for index, entry in enumerate(audio_entries):
        asset = _prepare_audio_entry(
            entry=entry,
            index=index,
            audio_dir=audio_dir,
            by_destination=by_destination,
        )

        destination_path = Path(asset.destination_path)
        if not any(existing.destination_path == asset.destination_path for existing in prepared_assets):
            if not destination_path.exists():
                _copy_audio(Path(asset.source_path), destination_path)
                copied += 1
            elif filecmp.cmp(asset.source_path, destination_path, shallow=False):
                reused += 1
            else:
                _copy_audio(Path(asset.source_path), destination_path)
                overwritten += 1

        prepared_assets.append(asset)
        public_paths_by_key_path[(asset.section_key, entry["path"])] = asset.public_path

    _apply_public_paths(updated_props, public_paths_by_key_path)

    return updated_props, RemotionAssetPrepareResult(
        props_path=props_path,
        public_dir=out_dir,
        audio_dir=audio_dir,
        copied=copied,
        reused=reused,
        overwritten=overwritten,
        audio_assets=prepared_assets,
    )


def prepare_remotion_assets_file(props_path: Path, out_dir: Path) -> RemotionAssetPrepareResult:
    props = load_remotion_props(props_path)
    updated_props, result = prepare_remotion_audio_assets(props, props_path, out_dir)
    try:
        props_path.write_text(json.dumps(updated_props, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SyncCutError(f"{props_path}: failed to write Remotion props: {exc}") from exc
    return result


def _audio_entries(props: dict[str, Any], props_path: Path) -> list[dict[str, Any]]:
    assets = require_mapping(
        props.get("assets"),
        context=f"{props_path}: assets",
    )
    audio = assets.get("audio")
    if not isinstance(audio, list):
        raise SyncCutError(f"{props_path}: assets.audio must be an array")
    return [
        _validate_audio_entry(entry, index=index, props_path=props_path)
        for index, entry in enumerate(audio)
    ]


def _validate_audio_entry(entry: Any, *, index: int, props_path: Path) -> dict[str, str]:
    context = f"{props_path}: assets.audio[{index}]"
    mapping = require_mapping(entry, context=context)
    section_key = require_non_empty_string(
        mapping.get("section_key"), context=f"{context}.section_key"
    )
    path = require_non_empty_string(mapping.get("path"), context=f"{context}.path")
    return {"section_key": section_key, "path": path}


def _prepare_audio_entry(
    *,
    entry: dict[str, str],
    index: int,
    audio_dir: Path,
    by_destination: dict[str, Path],
) -> PreparedAudioAsset:
    section_key = entry["section_key"]
    source_text = entry["path"]
    source_path = _resolve_source_path(source_text)
    if not source_path.exists():
        raise SyncCutError(f"assets.audio[{index}] {source_text}: source audio file not found")
    if not source_path.is_file():
        raise SyncCutError(f"assets.audio[{index}] {source_text}: source audio path is not a file")
    if not source_path.suffix:
        raise SyncCutError(f"assets.audio[{index}] {source_text}: source audio file must have a suffix")

    destination_filename = f"{section_key}{source_path.suffix}"
    destination_path = audio_dir / destination_filename
    public_path = f"audio/{destination_filename}"

    existing_source = by_destination.get(destination_filename)
    if existing_source is not None and existing_source != source_path:
        raise SyncCutError(
            f"audio destination collision for {public_path}: "
            f"{existing_source} and {source_path}"
        )
    by_destination[destination_filename] = source_path

    return PreparedAudioAsset(
        section_key=section_key,
        source_path=str(source_path),
        destination_path=str(destination_path),
        public_path=public_path,
    )


def _resolve_source_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def _copy_audio(source_path: Path, destination_path: Path) -> None:
    try:
        shutil.copy2(source_path, destination_path)
    except OSError as exc:
        raise SyncCutError(
            f"{source_path}: failed to copy audio asset to {destination_path}: {exc}"
        ) from exc


def _apply_public_paths(
    props: dict[str, Any], public_paths_by_key_path: dict[tuple[str, str], str]
) -> None:
    for entry in props["assets"]["audio"]:
        key = (entry["section_key"], entry["path"])
        entry["public_path"] = public_paths_by_key_path[key]

    for section in props.get("sections", []):
        if not isinstance(section, dict):
            continue
        audio = section.get("audio")
        if not isinstance(audio, dict):
            continue
        public_path = public_paths_by_key_path.get((section.get("section_key"), audio.get("path")))
        if public_path is not None:
            audio["public_path"] = public_path

    for scene in props.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        audio = scene.get("audio")
        if not isinstance(audio, dict):
            continue
        public_path = public_paths_by_key_path.get((scene.get("section_key"), audio.get("path")))
        if public_path is not None:
            audio["public_path"] = public_path
