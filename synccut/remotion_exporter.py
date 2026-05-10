from __future__ import annotations

import json
import math
from copy import deepcopy
from pathlib import Path
from typing import Any

from synccut.timeline_validator import load_timeline_json, validate_timeline
from synccut.validators import SyncCutError

DEFAULT_FPS = 30
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_COMPOSITION_ID = "SyncCutVideo"


def seconds_to_frame(seconds: float, fps: int = DEFAULT_FPS) -> int:
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)):
        raise SyncCutError("seconds must be numeric")
    if isinstance(fps, bool) or not isinstance(fps, int) or fps <= 0:
        raise SyncCutError("fps must be a positive integer")
    return math.floor(float(seconds) * fps + 0.5)


def build_remotion_props(
    data: dict, source_timeline_path: Path, fps: int = DEFAULT_FPS
) -> dict[str, Any]:
    result = validate_timeline(data, path=str(source_timeline_path))
    if not result.ok:
        details = "; ".join(result.errors)
        raise SyncCutError(f"{source_timeline_path}: invalid timeline: {details}")

    metadata = data["metadata"]
    duration_sec = metadata["total_duration_sec"]
    duration_frames = seconds_to_frame(duration_sec, fps)
    sections = [_map_section(section, fps) for section in _sorted_sections(data["sections"])]
    scenes = [_map_scene(scene, fps) for scene in _sorted_scenes(data["timeline"])]

    return {
        "metadata": {
            "generated_by": "synccut export-remotion",
            "source_timeline": str(source_timeline_path),
            "fps": fps,
            "duration_sec": duration_sec,
            "duration_frames": duration_frames,
            "total_scenes": metadata["total_scenes"],
            "total_sections": metadata["total_sections"],
        },
        "composition": {
            "id": DEFAULT_COMPOSITION_ID,
            "width": DEFAULT_WIDTH,
            "height": DEFAULT_HEIGHT,
            "fps": fps,
            "duration_frames": duration_frames,
        },
        "sections": sections,
        "scenes": scenes,
        "assets": {
            "audio": _audio_assets(sections),
            "visuals": [],
        },
        "warnings": _merged_warnings(data.get("warnings", []), result.warnings),
    }


def export_remotion_props_file(timeline_path: Path, out_path: Path) -> dict[str, Any]:
    data = load_timeline_json(timeline_path)
    props = build_remotion_props(data, timeline_path)
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(props, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SyncCutError(f"{out_path}: failed to write Remotion props: {exc}") from exc
    return props


def _map_section(section: dict[str, Any], fps: int) -> dict[str, Any]:
    start_sec = section["global_start_sec"]
    end_sec = section["global_end_sec"]
    start_frame = seconds_to_frame(start_sec, fps)
    end_frame = seconds_to_frame(end_sec, fps)
    duration_frames = end_frame - start_frame
    if duration_frames <= 0:
        raise SyncCutError(
            f"section {section['section_key']} has non-positive frame duration "
            f"from {start_sec} to {end_sec}"
        )

    return {
        "section_key": section["section_key"],
        "section": section["section"],
        "section_order": section["section_order"],
        "start_sec": start_sec,
        "end_sec": end_sec,
        "duration_sec": section["local_duration_sec"],
        "start_frame": start_frame,
        "end_frame": end_frame,
        "duration_frames": duration_frames,
        "audio": {"path": section["audio_path"]},
        "alignment": {"path": section["alignment_path"]},
    }


def _map_scene(scene: dict[str, Any], fps: int) -> dict[str, Any]:
    timing = scene["timing"]
    start_sec = timing["start_sec"]
    end_sec = timing["end_sec"]
    start_frame = seconds_to_frame(start_sec, fps)
    end_frame = seconds_to_frame(end_sec, fps)
    duration_frames = end_frame - start_frame
    if duration_frames <= 0:
        raise SyncCutError(
            f"scene {scene['scene_id']} has non-positive frame duration "
            f"from {start_sec} to {end_sec}"
        )

    visual = deepcopy(scene["visual"])
    return {
        "id": scene["scene_id"],
        "scene_order": scene["scene_order"],
        "section": scene["section"],
        "section_order": scene["section_order"],
        "section_key": scene["section_key"],
        "start_sec": start_sec,
        "end_sec": end_sec,
        "duration_sec": timing["duration_sec"],
        "local_start_sec": timing["local_start_sec"],
        "local_end_sec": timing["local_end_sec"],
        "start_frame": start_frame,
        "end_frame": end_frame,
        "duration_frames": duration_frames,
        "visual_type": visual["type"],
        "visual": visual,
        "dialogue": deepcopy(scene["dialogue"]),
        "audio": deepcopy(scene["audio"]),
        "alignment": deepcopy(scene["alignment"]),
        "warnings": deepcopy(scene["warnings"]),
    }


def _sorted_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        sections,
        key=lambda section: (section["section_order"], section["section_key"]),
    )


def _sorted_scenes(scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        scenes,
        key=lambda scene: (
            scene["section_order"],
            scene["section_key"],
            scene["timing"]["start_sec"],
            scene["scene_order"],
            scene["scene_id"],
        ),
    )


def _audio_assets(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    assets: list[dict[str, Any]] = []
    for section in sections:
        path = section["audio"]["path"]
        if path in seen:
            continue
        seen.add(path)
        assets.append({"section_key": section["section_key"], "path": path})
    return assets


def _merged_warnings(*warning_groups: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for warnings in warning_groups:
        for warning in warnings:
            if warning in seen:
                continue
            seen.add(warning)
            merged.append(warning)
    return merged
