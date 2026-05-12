from __future__ import annotations

import filecmp
import json
import shutil
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string

TARGET_VISUAL_TYPES = {"AI_VIDEO", "B_ROLL"}
SUPPORTED_VISUAL_EXTENSIONS = {".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp"}


@dataclass(frozen=True)
class PreparedVisualAsset:
    scene_id: str
    visual_type: str
    source_path: str
    destination_path: str
    public_path: str


@dataclass(frozen=True)
class VisualAssetPrepareResult:
    props_path: Path
    public_dir: Path
    visuals_dir: Path
    copied: int
    reused: int
    overwritten: int
    missing: int
    visual_assets: list[PreparedVisualAsset]


@dataclass(frozen=True)
class VisualAssetReadinessItem:
    scene_id: str
    visual_type: str
    status: str
    public_path: str | None


@dataclass(frozen=True)
class VisualAssetReadinessSummary:
    props_path: Path
    items: list[VisualAssetReadinessItem]
    prepared: int
    missing: int
    unsupported: int


def load_visual_props(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to read Remotion props: {exc}") from exc

    return require_mapping(data, context=str(path))


def prepare_visual_assets(
    props: dict[str, Any], props_path: Path, assets_dir: Path, out_dir: Path
) -> tuple[dict[str, Any], VisualAssetPrepareResult]:
    source_props = require_mapping(props, context=str(props_path))
    scenes = _target_scenes(source_props, props_path)

    updated_props = deepcopy(source_props)
    output_visuals_dir = out_dir / "visuals"
    try:
        output_visuals_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SyncCutError(
            f"{output_visuals_dir}: failed to create visual asset directory: {exc}"
        ) from exc

    copied = 0
    reused = 0
    overwritten = 0
    missing = 0
    prepared_assets: list[PreparedVisualAsset] = []
    prepared_by_scene_id: dict[str, PreparedVisualAsset | None] = {}

    for scene in scenes:
        asset = _prepare_scene_asset(
            scene=scene,
            assets_dir=assets_dir,
            output_visuals_dir=output_visuals_dir,
        )
        prepared_by_scene_id[scene["id"]] = asset

        if asset is None:
            missing += 1
            continue

        destination_path = Path(asset.destination_path)
        if not destination_path.exists():
            _copy_visual(Path(asset.source_path), destination_path)
            copied += 1
        elif filecmp.cmp(asset.source_path, destination_path, shallow=False):
            reused += 1
        else:
            _copy_visual(Path(asset.source_path), destination_path)
            overwritten += 1

        prepared_assets.append(asset)

    _apply_visual_asset_metadata(updated_props, prepared_by_scene_id, prepared_assets)

    return updated_props, VisualAssetPrepareResult(
        props_path=props_path,
        public_dir=out_dir,
        visuals_dir=output_visuals_dir,
        copied=copied,
        reused=reused,
        overwritten=overwritten,
        missing=missing,
        visual_assets=prepared_assets,
    )


def prepare_visual_assets_file(
    props_path: Path, assets_dir: Path, out_dir: Path
) -> VisualAssetPrepareResult:
    props = load_visual_props(props_path)
    updated_props, result = prepare_visual_assets(props, props_path, assets_dir, out_dir)
    try:
        props_path.write_text(json.dumps(updated_props, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SyncCutError(f"{props_path}: failed to write Remotion props: {exc}") from exc
    return result


def inspect_visual_asset_readiness(
    props: dict[str, Any], props_path: Path
) -> VisualAssetReadinessSummary:
    source_props = require_mapping(props, context=str(props_path))
    scenes = _target_scene_entries(source_props, props_path)

    items: list[VisualAssetReadinessItem] = []
    prepared = 0
    missing = 0
    unsupported = 0

    for scene in scenes:
        visual = require_mapping(scene["visual"], context=f"{scene['context']}.visual")
        public_path_value = visual.get("public_path")
        valid_public_path = classify_visual_public_path(public_path_value)
        status = _readiness_status(visual.get("asset_status"), public_path_value, valid_public_path)
        if status == "prepared":
            prepared += 1
        elif status == "unsupported":
            unsupported += 1
        else:
            missing += 1

        items.append(
            VisualAssetReadinessItem(
                scene_id=scene["id"],
                visual_type=scene["visual_type"],
                status=status,
                public_path=public_path_value if isinstance(public_path_value, str) else None,
            )
        )

    return VisualAssetReadinessSummary(
        props_path=props_path,
        items=items,
        prepared=prepared,
        missing=missing,
        unsupported=unsupported,
    )


def inspect_visual_asset_readiness_file(props_path: Path) -> VisualAssetReadinessSummary:
    props = load_visual_props(props_path)
    return inspect_visual_asset_readiness(props, props_path)


def format_visual_asset_readiness(summary: VisualAssetReadinessSummary) -> str:
    lines = [
        f"Visual assets: {summary.props_path}",
        f"target_scenes: {len(summary.items)}",
        f"prepared: {summary.prepared}",
        f"missing: {summary.missing}",
        f"unsupported: {summary.unsupported}",
    ]
    if summary.items:
        lines.append("")
        for item in summary.items:
            public_path = item.public_path if item.public_path is not None else "-"
            lines.append(f"{item.scene_id} {item.visual_type} {item.status} {public_path}")
    return "\n".join(lines) + "\n"


def visual_asset_readiness_to_dict(
    summary: VisualAssetReadinessSummary,
) -> dict[str, Any]:
    return {
        "path": str(summary.props_path),
        "target_scenes": len(summary.items),
        "prepared": summary.prepared,
        "missing": summary.missing,
        "unsupported": summary.unsupported,
        "items": [
            {
                "scene_id": item.scene_id,
                "visual_type": item.visual_type,
                "status": item.status,
                "public_path": item.public_path,
            }
            for item in summary.items
        ],
    }


def classify_visual_public_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    public_path = value.strip()
    if not public_path or not public_path.startswith("visuals/") or ".." in public_path:
        return None

    suffix = Path(public_path).suffix.lower()
    if suffix not in SUPPORTED_VISUAL_EXTENSIONS:
        return None
    return public_path


def _target_scenes(props: dict[str, Any], props_path: Path) -> list[dict[str, Any]]:
    return [
        {
            "id": scene["id"],
            "visual_type": scene["visual_type"],
            "scene_order": scene.get("scene_order"),
        }
        for scene in _target_scene_entries(props, props_path)
    ]


def _target_scene_entries(props: dict[str, Any], props_path: Path) -> list[dict[str, Any]]:
    scenes_value = props.get("scenes")
    if not isinstance(scenes_value, list):
        raise SyncCutError(f"{props_path}: scenes must be an array")

    scenes: list[dict[str, Any]] = []
    for index, scene_value in enumerate(scenes_value):
        context = f"{props_path}: scenes[{index}]"
        scene = require_mapping(scene_value, context=context)
        visual_type = scene.get("visual_type")
        if visual_type not in TARGET_VISUAL_TYPES:
            continue

        scene_id = require_non_empty_string(scene.get("id"), context=f"{context}.id")
        visual = require_mapping(scene.get("visual"), context=f"{context}.visual")
        if visual.get("type") != visual_type:
            raise SyncCutError(
                f"{context}.visual.type must match visual_type for visual asset preparation"
            )

        scenes.append(
            {
                "id": scene_id,
                "visual_type": visual_type,
                "scene_order": scene.get("scene_order"),
                "visual": visual,
                "context": context,
            }
        )

    return scenes


def _readiness_status(
    asset_status: Any, public_path_value: Any, valid_public_path: str | None
) -> str:
    public_path_present = isinstance(public_path_value, str) and bool(public_path_value.strip())
    if asset_status == "unsupported":
        return "unsupported"
    if asset_status == "prepared":
        return "prepared" if valid_public_path is not None else "unsupported"
    if public_path_present and valid_public_path is None:
        return "unsupported"
    return "missing"


def _prepare_scene_asset(
    *,
    scene: dict[str, Any],
    assets_dir: Path,
    output_visuals_dir: Path,
) -> PreparedVisualAsset | None:
    scene_id = scene["id"]
    candidates = _matching_supported_files(assets_dir, scene_id)
    if not candidates:
        return None
    if len(candidates) > 1:
        paths = ", ".join(str(path) for path in candidates)
        raise SyncCutError(f"multiple supported visual assets for {scene_id}: {paths}")

    source_path = candidates[0].resolve()
    suffix = source_path.suffix.lower()
    destination_filename = f"{scene_id}{suffix}"
    destination_path = output_visuals_dir / destination_filename
    public_path = f"visuals/{destination_filename}"

    return PreparedVisualAsset(
        scene_id=scene_id,
        visual_type=scene["visual_type"],
        source_path=str(source_path),
        destination_path=str(destination_path),
        public_path=public_path,
    )


def _matching_supported_files(assets_dir: Path, scene_id: str) -> list[Path]:
    if not assets_dir.exists():
        return []
    if not assets_dir.is_dir():
        raise SyncCutError(f"{assets_dir}: visual assets path must be a directory")

    matches: list[Path] = []
    try:
        entries = list(assets_dir.iterdir())
    except OSError as exc:
        raise SyncCutError(f"{assets_dir}: failed to read visual assets directory: {exc}") from exc

    for path in entries:
        if not path.is_file():
            continue
        if path.stem != scene_id:
            continue
        if path.suffix.lower() in SUPPORTED_VISUAL_EXTENSIONS:
            matches.append(path)

    return sorted(matches, key=lambda path: path.name.lower())


def _copy_visual(source_path: Path, destination_path: Path) -> None:
    try:
        shutil.copy2(source_path, destination_path)
    except OSError as exc:
        raise SyncCutError(
            f"{source_path}: failed to copy visual asset to {destination_path}: {exc}"
        ) from exc


def _apply_visual_asset_metadata(
    props: dict[str, Any],
    prepared_by_scene_id: dict[str, PreparedVisualAsset | None],
    prepared_assets: list[PreparedVisualAsset],
) -> None:
    for scene in props.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        scene_id = scene.get("id")
        if scene_id not in prepared_by_scene_id:
            continue
        visual = scene.get("visual")
        if not isinstance(visual, dict):
            continue

        asset = prepared_by_scene_id[scene_id]
        if asset is None:
            visual.pop("public_path", None)
            visual["asset_status"] = "missing"
            visual["asset_source"] = "local"
            continue

        visual["public_path"] = asset.public_path
        visual["asset_status"] = "prepared"
        visual["asset_source"] = "local"

    assets = props.setdefault("assets", {})
    if isinstance(assets, dict):
        assets["visuals"] = [
            {
                "scene_id": asset.scene_id,
                "visual_type": asset.visual_type,
                "path": asset.source_path,
                "public_path": asset.public_path,
                "asset_status": "prepared",
                "asset_source": "local",
            }
            for asset in prepared_assets
        ]
