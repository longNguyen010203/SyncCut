from __future__ import annotations

from pathlib import Path
from typing import Any

from synccut.timeline_validator import validate_timeline
from synccut.validators import SyncCutError


def build_timeline_overview(data: dict, path: Path | None = None) -> str:
    result = validate_timeline(data, path=str(path) if path is not None else None)
    if not result.ok:
        details = "; ".join(result.errors[:3])
        raise SyncCutError(f"timeline is not valid enough to inspect: {details}")

    label = str(path) if path is not None else "<memory>"
    lines = [
        f"Timeline: {label}",
        f"Scenes: {result.total_scenes}",
        f"Sections: {result.total_sections}",
        f"Duration: {_fmt_seconds(result.total_duration_sec)}",
        f"Warnings: {len(data.get('warnings', [])) + len(result.warnings)}",
        "",
    ]
    lines.extend(section_overview_rows(data))
    return "\n".join(lines).rstrip() + "\n"


def section_overview_rows(data: dict) -> list[str]:
    sections = sorted(
        data.get("sections", []),
        key=lambda section: (
            _sort_number(section.get("section_order")),
            str(section.get("section_key", "")),
        ),
    )
    scenes_by_section = _scenes_by_section(data.get("timeline", []))

    rows: list[str] = []
    for section in sections:
        section_key = str(section["section_key"])
        section_scenes = scenes_by_section.get(section_key, [])
        rows.append(
            f"[{section_key}] {section['section']} "
            f"{_fmt_seconds(section['global_start_sec'])}-{_fmt_seconds(section['global_end_sec'])} "
            f"({_fmt_seconds(section['local_duration_sec'])}), {len(section_scenes)} scenes"
        )
        for scene in section_scenes:
            timing = scene["timing"]
            rows.append(
                f"  {scene['scene_id']} "
                f"{_fmt_seconds(timing['start_sec'])}-{_fmt_seconds(timing['end_sec'])} "
                f"{_fmt_seconds(timing['duration_sec'])} "
                f"{scene['visual']['type']} "
                f"{scene['alignment']['match_method']}"
            )
        rows.append("")
    if rows and rows[-1] == "":
        rows.pop()
    return rows


def _scenes_by_section(timeline: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for scene in timeline:
        grouped.setdefault(str(scene["section_key"]), []).append(scene)
    for section_key, scenes in grouped.items():
        grouped[section_key] = sorted(
            scenes,
            key=lambda scene: (
                _sort_number(scene["timing"].get("start_sec")),
                _sort_number(scene.get("scene_order")),
                str(scene.get("scene_id", "")),
            ),
        )
    return grouped


def _fmt_seconds(value: Any) -> str:
    if value is None:
        return "unknown"
    return f"{float(value):.3f}s"


def _sort_number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)
