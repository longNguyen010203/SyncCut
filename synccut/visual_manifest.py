from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string
from synccut.visual_assets import (
    SUPPORTED_VISUAL_EXTENSIONS,
    TARGET_VISUAL_TYPES,
    classify_visual_public_path,
    inspect_visual_asset_readiness,
    load_visual_props,
)

MANIFEST_SCHEMA_VERSION = "0.1"
MANIFEST_GENERATOR = "synccut visual-manifest"
DEFAULT_ASSETS_DIR = Path("assets/visuals")
DEFAULT_MARKDOWN_OUT = Path("generated/visual_manifest.md")
DEFAULT_JSON_OUT = Path("generated/visual_manifest.json")
SUPPORTED_MANIFEST_FORMATS = {"markdown", "json"}


@dataclass(frozen=True)
class VisualManifestScene:
    scene_id: str
    section_key: str | None
    section: str | None
    section_order: int | None
    scene_order: int | None
    visual_type: str
    duration_sec: float | None
    duration_frames: int | None
    assets_dir: str
    expected_asset_stem: str
    supported_extensions: list[str]
    expected_filenames: list[str]
    prepared_status: str
    public_path: str | None
    asset_status: str | None
    asset_source: str | None
    local_asset_status: str
    local_asset_path: str | None
    local_supported_paths: list[str]
    local_unsupported_paths: list[str]
    prompt: str | None
    search_query_seed: str | None
    visual_data: Any
    notes: str


@dataclass(frozen=True)
class VisualManifestSummary:
    target_scenes: int
    prepared: int
    missing: int
    unsupported: int
    local_found: int
    local_missing: int
    local_duplicate_supported: int
    local_unsupported_only: int


@dataclass(frozen=True)
class VisualManifest:
    props_path: Path
    assets_dir: Path
    output_format: str
    scenes: list[VisualManifestScene]
    summary: VisualManifestSummary


@dataclass(frozen=True)
class VisualManifestWriteResult:
    manifest: VisualManifest
    out_path: Path
    output_format: str
    status: str
    dry_run: bool


def default_visual_manifest_out(output_format: str) -> Path:
    normalized = _normalize_format(output_format)
    if normalized == "json":
        return DEFAULT_JSON_OUT
    return DEFAULT_MARKDOWN_OUT


def build_visual_manifest(
    props: dict[str, Any],
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    output_format: str = "markdown",
) -> VisualManifest:
    normalized_format = _normalize_format(output_format)
    source_props = require_mapping(props, context=str(props_path))
    readiness = inspect_visual_asset_readiness(source_props, props_path)
    readiness_by_scene_id = {item.scene_id: item for item in readiness.items}

    scenes_value = source_props.get("scenes")
    if not isinstance(scenes_value, list):
        raise SyncCutError(f"{props_path}: scenes must be an array")

    scenes: list[VisualManifestScene] = []
    for index, scene_value in enumerate(scenes_value):
        context = f"{props_path}: scenes[{index}]"
        scene = require_mapping(scene_value, context=context)
        visual_type = scene.get("visual_type")
        if visual_type not in TARGET_VISUAL_TYPES:
            continue

        scene_id = require_non_empty_string(scene.get("id"), context=f"{context}.id")
        visual = require_mapping(scene.get("visual"), context=f"{context}.visual")
        if visual.get("type") != visual_type:
            raise SyncCutError(f"{context}.visual.type must match visual_type")

        readiness_item = readiness_by_scene_id[scene_id]
        local_status = _inspect_local_asset(assets_dir, scene_id)
        prompt = visual.get("prompt") if isinstance(visual.get("prompt"), str) else None
        visual_data = _json_safe_value(visual.get("data"))

        scene_manifest = VisualManifestScene(
            scene_id=scene_id,
            section_key=_optional_string(scene.get("section_key")),
            section=_optional_string(scene.get("section")),
            section_order=_optional_int(scene.get("section_order")),
            scene_order=_optional_int(scene.get("scene_order")),
            visual_type=visual_type,
            duration_sec=_optional_number(scene.get("duration_sec")),
            duration_frames=_optional_int(scene.get("duration_frames")),
            assets_dir=str(assets_dir),
            expected_asset_stem=str(assets_dir / scene_id),
            supported_extensions=_sorted_extensions(),
            expected_filenames=[str(assets_dir / f"{scene_id}{ext}") for ext in _sorted_extensions()],
            prepared_status=readiness_item.status,
            public_path=readiness_item.public_path,
            asset_status=_optional_string(visual.get("asset_status")),
            asset_source=_optional_string(visual.get("asset_source")),
            local_asset_status=local_status["status"],
            local_asset_path=local_status["asset_path"],
            local_supported_paths=local_status["supported_paths"],
            local_unsupported_paths=local_status["unsupported_paths"],
            prompt=prompt,
            search_query_seed=_search_query_seed(visual),
            visual_data=visual_data,
            notes=_scene_notes(readiness_item.status, local_status["status"]),
        )
        scenes.append(scene_manifest)

    summary = _build_summary(scenes)
    return VisualManifest(
        props_path=props_path,
        assets_dir=assets_dir,
        output_format=normalized_format,
        scenes=scenes,
        summary=summary,
    )


def build_visual_manifest_file(
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    output_format: str = "markdown",
) -> VisualManifest:
    props = load_visual_props(props_path)
    return build_visual_manifest(
        props,
        props_path,
        assets_dir=assets_dir,
        output_format=output_format,
    )


def write_visual_manifest_file(
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    out_path: Path | None = None,
    output_format: str = "markdown",
    dry_run: bool = False,
    overwrite: bool = False,
) -> VisualManifestWriteResult:
    normalized_format = _normalize_format(output_format)
    resolved_out_path = out_path if out_path is not None else default_visual_manifest_out(normalized_format)
    manifest = build_visual_manifest_file(
        props_path,
        assets_dir=assets_dir,
        output_format=normalized_format,
    )
    content = format_visual_manifest(manifest)

    status = _planned_write_status(resolved_out_path, content)
    if dry_run:
        return VisualManifestWriteResult(
            manifest=manifest,
            out_path=resolved_out_path,
            output_format=normalized_format,
            status=f"would_{status}",
            dry_run=True,
        )

    if status == "block" and not overwrite:
        raise SyncCutError(
            f"{resolved_out_path}: output exists and differs; rerun with --overwrite to replace"
        )

    if status in {"create", "block"}:
        try:
            resolved_out_path.parent.mkdir(parents=True, exist_ok=True)
            resolved_out_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise SyncCutError(f"{resolved_out_path}: failed to write visual manifest: {exc}") from exc
        status = "written"
    else:
        status = "reused"

    return VisualManifestWriteResult(
        manifest=manifest,
        out_path=resolved_out_path,
        output_format=normalized_format,
        status=status,
        dry_run=False,
    )


def format_visual_manifest(manifest: VisualManifest) -> str:
    if manifest.output_format == "json":
        return json.dumps(visual_manifest_to_dict(manifest), indent=2, ensure_ascii=False) + "\n"
    return format_visual_manifest_markdown(manifest)


def format_visual_manifest_markdown(manifest: VisualManifest) -> str:
    summary = manifest.summary
    lines = [
        "# Visual Asset Manifest",
        "",
        f"Source props: {manifest.props_path}",
        f"Assets dir: {manifest.assets_dir}",
        "Format: markdown",
        "",
        "## Summary",
        "",
        f"- target_scenes: {summary.target_scenes}",
        f"- prepared: {summary.prepared}",
        f"- missing: {summary.missing}",
        f"- unsupported: {summary.unsupported}",
        f"- local_found: {summary.local_found}",
        f"- local_missing: {summary.local_missing}",
        f"- local_duplicate_supported: {summary.local_duplicate_supported}",
        f"- local_unsupported_only: {summary.local_unsupported_only}",
        "",
        "## Naming Policy",
        "",
        "Use one supported file per target scene:",
        "",
        "    assets/visuals/<scene_id>.<supported_ext>",
        "",
        f"Supported extensions: {', '.join(_sorted_extensions())}",
        "",
        "## Scenes",
        "",
        (
            "| scene_id | section_key | visual_type | duration_sec | prepared_status | "
            "local_asset_status | expected_asset_stem | search_query_seed |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scene in manifest.scenes:
        lines.append(
            " | ".join(
                [
                    "| " + scene.scene_id,
                    _markdown_value(scene.section_key),
                    scene.visual_type,
                    _markdown_value(scene.duration_sec),
                    scene.prepared_status,
                    scene.local_asset_status,
                    scene.expected_asset_stem,
                    _markdown_value(scene.search_query_seed),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def visual_manifest_to_dict(manifest: VisualManifest) -> dict[str, Any]:
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "metadata": {
            "generated_by": MANIFEST_GENERATOR,
            "source_props": str(manifest.props_path),
            "assets_dir": str(manifest.assets_dir),
            "format": manifest.output_format,
        },
        "summary": _summary_to_dict(manifest.summary),
        "supported_extensions": _sorted_extensions(),
        "scenes": [_scene_to_dict(scene) for scene in manifest.scenes],
    }


def _scene_to_dict(scene: VisualManifestScene) -> dict[str, Any]:
    return {
        "scene_id": scene.scene_id,
        "section_key": scene.section_key,
        "section": scene.section,
        "section_order": scene.section_order,
        "scene_order": scene.scene_order,
        "visual_type": scene.visual_type,
        "duration_sec": scene.duration_sec,
        "duration_frames": scene.duration_frames,
        "assets_dir": scene.assets_dir,
        "expected_asset_stem": scene.expected_asset_stem,
        "supported_extensions": scene.supported_extensions,
        "expected_filenames": scene.expected_filenames,
        "prepared_status": scene.prepared_status,
        "public_path": scene.public_path,
        "asset_status": scene.asset_status,
        "asset_source": scene.asset_source,
        "local_asset_status": scene.local_asset_status,
        "local_asset_path": scene.local_asset_path,
        "local_supported_paths": scene.local_supported_paths,
        "local_unsupported_paths": scene.local_unsupported_paths,
        "prompt": scene.prompt,
        "search_query_seed": scene.search_query_seed,
        "visual_data": scene.visual_data,
        "notes": scene.notes,
    }


def _summary_to_dict(summary: VisualManifestSummary) -> dict[str, int]:
    return {
        "target_scenes": summary.target_scenes,
        "prepared": summary.prepared,
        "missing": summary.missing,
        "unsupported": summary.unsupported,
        "local_found": summary.local_found,
        "local_missing": summary.local_missing,
        "local_duplicate_supported": summary.local_duplicate_supported,
        "local_unsupported_only": summary.local_unsupported_only,
    }


def _inspect_local_asset(assets_dir: Path, scene_id: str) -> dict[str, Any]:
    supported: list[Path] = []
    unsupported: list[Path] = []

    if assets_dir.exists() and not assets_dir.is_dir():
        raise SyncCutError(f"{assets_dir}: visual assets path must be a directory")

    if assets_dir.exists():
        try:
            entries = list(assets_dir.iterdir())
        except OSError as exc:
            raise SyncCutError(f"{assets_dir}: failed to read visual assets directory: {exc}") from exc

        for path in entries:
            if not path.is_file() or path.stem != scene_id:
                continue
            if path.suffix.lower() in SUPPORTED_VISUAL_EXTENSIONS:
                supported.append(path)
            else:
                unsupported.append(path)

    supported_paths = [str(path) for path in sorted(supported, key=lambda item: item.name.lower())]
    unsupported_paths = [
        str(path) for path in sorted(unsupported, key=lambda item: item.name.lower())
    ]
    if len(supported_paths) == 1:
        return {
            "status": "found",
            "asset_path": supported_paths[0],
            "supported_paths": supported_paths,
            "unsupported_paths": unsupported_paths,
        }
    if len(supported_paths) > 1:
        return {
            "status": "duplicate_supported",
            "asset_path": None,
            "supported_paths": supported_paths,
            "unsupported_paths": unsupported_paths,
        }
    if unsupported_paths:
        return {
            "status": "unsupported_only",
            "asset_path": None,
            "supported_paths": [],
            "unsupported_paths": unsupported_paths,
        }
    return {
        "status": "missing",
        "asset_path": None,
        "supported_paths": [],
        "unsupported_paths": [],
    }


def _build_summary(scenes: list[VisualManifestScene]) -> VisualManifestSummary:
    return VisualManifestSummary(
        target_scenes=len(scenes),
        prepared=sum(1 for scene in scenes if scene.prepared_status == "prepared"),
        missing=sum(1 for scene in scenes if scene.prepared_status == "missing"),
        unsupported=sum(1 for scene in scenes if scene.prepared_status == "unsupported"),
        local_found=sum(1 for scene in scenes if scene.local_asset_status == "found"),
        local_missing=sum(1 for scene in scenes if scene.local_asset_status == "missing"),
        local_duplicate_supported=sum(
            1 for scene in scenes if scene.local_asset_status == "duplicate_supported"
        ),
        local_unsupported_only=sum(
            1 for scene in scenes if scene.local_asset_status == "unsupported_only"
        ),
    )


def _search_query_seed(visual: dict[str, Any]) -> str | None:
    for value in [
        visual.get("prompt"),
        visual.get("description"),
        _description_from_visual_data(visual.get("data")),
        _query_from_visual_data(visual.get("data")),
    ]:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _description_from_visual_data(value: Any) -> str | None:
    if isinstance(value, dict):
        description = value.get("description")
        if isinstance(description, str):
            return description
    return None


def _query_from_visual_data(value: Any) -> str | None:
    if isinstance(value, dict):
        query = value.get("query")
        if isinstance(query, str):
            return query
    return None


def _json_safe_value(value: Any) -> Any:
    try:
        json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return None
    return value


def _scene_notes(prepared_status: str, local_asset_status: str) -> str:
    if prepared_status == "prepared":
        return "Prepared in props."
    if local_asset_status == "found":
        return "Local source file found; run prepare-visual-assets to prepare it."
    if local_asset_status == "duplicate_supported":
        return "Multiple supported local files match this scene; keep exactly one."
    if local_asset_status == "unsupported_only":
        return "Only unsupported local files match this scene."
    return "Needs a local visual asset or future downloader result."


def _planned_write_status(path: Path, content: str) -> str:
    if not path.exists():
        return "create"
    if path.read_text(encoding="utf-8") == content:
        return "reuse"
    return "block"


def _normalize_format(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in SUPPORTED_MANIFEST_FORMATS:
        expected = ", ".join(sorted(SUPPORTED_MANIFEST_FORMATS))
        raise SyncCutError(f"unsupported visual manifest format '{value}'; expected one of {expected}")
    return normalized


def _sorted_extensions() -> list[str]:
    return sorted(SUPPORTED_VISUAL_EXTENSIONS)


def _optional_string(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _optional_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _markdown_value(value: Any) -> str:
    if value is None:
        return "-"
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text
