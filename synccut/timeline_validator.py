from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synccut.validators import SUPPORTED_VISUAL_TYPES, SyncCutError

TIMING_TOLERANCE_SEC = 0.001
SUSPICIOUS_GAP_SEC = 1.0
MATCH_METHODS = {"paragraph", "sentence", "word_span"}


@dataclass(frozen=True)
class TimelineValidationResult:
    path: str | None
    errors: list[str]
    warnings: list[str]
    total_scenes: int
    total_sections: int
    total_duration_sec: float | None

    @property
    def ok(self) -> bool:
        return not self.errors


def load_timeline_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc

    if not isinstance(raw, dict):
        raise SyncCutError(f"{path}: timeline JSON root must be an object")
    return raw


def validate_timeline_file(path: Path) -> TimelineValidationResult:
    data = load_timeline_json(path)
    return validate_timeline(data, path=str(path))


def validate_timeline(data: dict[str, Any], path: str | None = None) -> TimelineValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return TimelineValidationResult(
            path=path,
            errors=["timeline JSON root must be an object"],
            warnings=[],
            total_scenes=0,
            total_sections=0,
            total_duration_sec=None,
        )

    metadata = _require_object(data, "metadata", errors)
    sections = _require_array(data, "sections", errors)
    timeline = _require_array(data, "timeline", errors)
    top_warnings = _require_array(data, "warnings", errors)

    total_scenes = 0
    total_sections = 0
    total_duration_sec: float | None = None

    if metadata is not None:
        total_scenes = _metadata_count(metadata, "total_scenes", errors)
        total_sections = _metadata_count(metadata, "total_sections", errors)
        total_duration_sec = _metadata_number(metadata, "total_duration_sec", errors)

    if sections is not None:
        if not sections:
            errors.append("sections must not be empty")
        _validate_sections(sections, errors)

    if timeline is not None:
        if not timeline:
            errors.append("timeline must not be empty")
        _validate_timeline_entries(timeline, errors)
        _validate_overlaps_and_gaps(timeline, errors, warnings)

    if top_warnings is not None:
        for index, warning in enumerate(top_warnings):
            if not isinstance(warning, str):
                errors.append(f"warnings[{index}] must be a string")

    if metadata is not None and timeline is not None and total_scenes != len(timeline):
        errors.append(
            f"metadata.total_scenes is {total_scenes} but timeline contains {len(timeline)} entries"
        )

    if metadata is not None and sections is not None and total_sections != len(sections):
        errors.append(
            f"metadata.total_sections is {total_sections} but sections contains {len(sections)} entries"
        )

    if sections and total_duration_sec is not None:
        sorted_sections = sorted(
            [section for section in sections if isinstance(section, dict)],
            key=lambda section: (
                _sort_number(section.get("section_order")),
                str(section.get("section_key", "")),
            ),
        )
        if sorted_sections:
            final_end = _as_number(sorted_sections[-1].get("global_end_sec"))
            if final_end is not None and abs(total_duration_sec - final_end) > TIMING_TOLERANCE_SEC:
                errors.append(
                    "metadata.total_duration_sec must match the final section global_end_sec"
                )

    return TimelineValidationResult(
        path=path,
        errors=errors,
        warnings=warnings,
        total_scenes=len(timeline) if isinstance(timeline, list) else total_scenes,
        total_sections=len(sections) if isinstance(sections, list) else total_sections,
        total_duration_sec=total_duration_sec,
    )


def _require_object(data: dict[str, Any], key: str, errors: list[str]) -> dict[str, Any] | None:
    if key not in data:
        errors.append(f"missing {key}")
        return None
    value = data[key]
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return None
    return value


def _require_array(data: dict[str, Any], key: str, errors: list[str]) -> list[Any] | None:
    if key not in data:
        errors.append(f"missing {key}")
        return None
    value = data[key]
    if not isinstance(value, list):
        errors.append(f"{key} must be an array")
        return None
    return value


def _metadata_count(metadata: dict[str, Any], key: str, errors: list[str]) -> int:
    if key not in metadata:
        errors.append(f"metadata.{key} is required")
        return 0
    value = metadata[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"metadata.{key} must be a non-negative integer")
        return 0
    return value


def _metadata_number(metadata: dict[str, Any], key: str, errors: list[str]) -> float | None:
    if key not in metadata:
        errors.append(f"metadata.{key} is required")
        return None
    value = _as_number(metadata[key])
    if value is None or value < 0:
        errors.append(f"metadata.{key} must be a non-negative number")
        return None
    return value


def _validate_sections(sections: list[Any], errors: list[str]) -> None:
    required = [
        "section_key",
        "section",
        "section_order",
        "audio_path",
        "alignment_path",
        "local_duration_sec",
        "global_start_sec",
        "global_end_sec",
    ]
    for index, item in enumerate(sections):
        context = f"sections[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        for key in required:
            if key not in item:
                errors.append(f"{context}.{key} is required")
        _non_empty_string(item, "section_key", f"{context}.section_key", errors)
        _non_empty_string(item, "section", f"{context}.section", errors)
        _non_empty_string(item, "audio_path", f"{context}.audio_path", errors)
        _non_empty_string(item, "alignment_path", f"{context}.alignment_path", errors)
        _integer(item, "section_order", f"{context}.section_order", errors)

        start = _number(item, "global_start_sec", f"{context}.global_start_sec", errors)
        end = _number(item, "global_end_sec", f"{context}.global_end_sec", errors)
        duration = _number(item, "local_duration_sec", f"{context}.local_duration_sec", errors)
        if duration is not None and duration <= 0:
            errors.append(f"{context}.local_duration_sec must be positive")
        if start is not None and end is not None and end < start:
            errors.append(f"{context}.global_end_sec must be greater than or equal to global_start_sec")
        if start is not None and end is not None and duration is not None:
            if abs(duration - (end - start)) > TIMING_TOLERANCE_SEC:
                errors.append(f"{context}.local_duration_sec must match global_end_sec - global_start_sec")


def _validate_timeline_entries(timeline: list[Any], errors: list[str]) -> None:
    required = [
        "scene_id",
        "scene_order",
        "section",
        "section_order",
        "section_key",
        "timing",
        "audio",
        "alignment",
        "dialogue",
        "visual",
        "warnings",
    ]
    for index, item in enumerate(timeline):
        context = f"timeline[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{context} must be an object")
            continue
        for key in required:
            if key not in item:
                errors.append(f"{context}.{key} is required")
        _non_empty_string(item, "scene_id", f"{context}.scene_id", errors)
        _non_empty_string(item, "section", f"{context}.section", errors)
        _non_empty_string(item, "section_key", f"{context}.section_key", errors)
        _integer(item, "scene_order", f"{context}.scene_order", errors)
        _integer(item, "section_order", f"{context}.section_order", errors)
        _validate_scene_timing(item.get("timing"), context, errors)
        _validate_audio(item.get("audio"), context, errors)
        _validate_alignment(item.get("alignment"), context, errors)
        _validate_dialogue(item.get("dialogue"), context, errors)
        _validate_visual(item.get("visual"), context, errors)
        _validate_warnings(item.get("warnings"), context, errors)


def _validate_scene_timing(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context}.timing must be an object")
        return
    required = ["start_sec", "end_sec", "duration_sec", "local_start_sec", "local_end_sec"]
    for key in required:
        if key not in value:
            errors.append(f"{context}.timing.{key} is required")
    start = _number(value, "start_sec", f"{context}.timing.start_sec", errors)
    end = _number(value, "end_sec", f"{context}.timing.end_sec", errors)
    duration = _number(value, "duration_sec", f"{context}.timing.duration_sec", errors)
    _number(value, "local_start_sec", f"{context}.timing.local_start_sec", errors)
    _number(value, "local_end_sec", f"{context}.timing.local_end_sec", errors)
    if duration is not None and duration <= 0:
        errors.append(f"{context}.timing.duration_sec must be positive")
    if start is not None and end is not None and end < start:
        errors.append(f"{context}.timing.end_sec must be greater than or equal to start_sec")
    if start is not None and end is not None and duration is not None:
        if abs(duration - (end - start)) > TIMING_TOLERANCE_SEC:
            errors.append(f"{context}.timing.duration_sec must match end_sec - start_sec")


def _validate_audio(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context}.audio must be an object")
        return
    _non_empty_string(value, "path", f"{context}.audio.path", errors)


def _validate_alignment(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context}.alignment must be an object")
        return
    _non_empty_string(value, "path", f"{context}.alignment.path", errors)
    method = value.get("match_method")
    if not isinstance(method, str) or method not in MATCH_METHODS:
        errors.append(f"{context}.alignment.match_method must be one of paragraph, sentence, word_span")
    matched_units = value.get("matched_units")
    if not isinstance(matched_units, list):
        errors.append(f"{context}.alignment.matched_units must be an array")


def _validate_dialogue(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context}.dialogue must be an object")
        return
    _non_empty_string(value, "text", f"{context}.dialogue.text", errors)
    paragraphs = value.get("paragraphs")
    if not isinstance(paragraphs, list):
        errors.append(f"{context}.dialogue.paragraphs must be an array")
        return
    for index, paragraph in enumerate(paragraphs):
        if not isinstance(paragraph, str) or not paragraph.strip():
            errors.append(f"{context}.dialogue.paragraphs[{index}] must be a non-empty string")


def _validate_visual(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{context}.visual must be an object")
        return
    visual_type = value.get("type")
    if not isinstance(visual_type, str) or visual_type not in SUPPORTED_VISUAL_TYPES:
        errors.append(f"{context}.visual.type must be a supported normalized visual type")


def _validate_warnings(value: Any, context: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{context}.warnings must be an array")
        return
    for index, warning in enumerate(value):
        if not isinstance(warning, str):
            errors.append(f"{context}.warnings[{index}] must be a string")


def _validate_overlaps_and_gaps(
    timeline: list[Any], errors: list[str], warnings: list[str]
) -> None:
    grouped: dict[str, list[tuple[int, dict[str, Any], float, float]]] = {}
    for index, item in enumerate(timeline):
        if not isinstance(item, dict):
            continue
        timing = item.get("timing")
        if not isinstance(timing, dict):
            continue
        start = _as_number(timing.get("start_sec"))
        end = _as_number(timing.get("end_sec"))
        section_key = item.get("section_key")
        if start is None or end is None or not isinstance(section_key, str):
            continue
        grouped.setdefault(section_key, []).append((index, item, start, end))

    for section_key, entries in grouped.items():
        ordered = sorted(entries, key=lambda entry: (entry[2], entry[0]))
        previous_index, previous_item, _previous_start, previous_end = ordered[0]
        for index, item, start, end in ordered[1:]:
            current_scene = str(item.get("scene_id", f"timeline[{index}]"))
            previous_scene = str(previous_item.get("scene_id", f"timeline[{previous_index}]"))
            if start < previous_end - TIMING_TOLERANCE_SEC:
                errors.append(
                    f"timeline[{index}] overlaps previous scene in section {section_key}"
                )
            else:
                gap = start - previous_end
                if gap > SUSPICIOUS_GAP_SEC:
                    warnings.append(
                        f"section {section_key} has a gap of {gap:.3f}s between {previous_scene} and {current_scene}"
                    )
            if end > previous_end:
                previous_index, previous_item, previous_end = index, item, end


def _non_empty_string(data: dict[str, Any], key: str, context: str, errors: list[str]) -> str | None:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context} must be a non-empty string")
        return None
    return value


def _integer(data: dict[str, Any], key: str, context: str, errors: list[str]) -> int | None:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{context} must be an integer")
        return None
    return value


def _number(data: dict[str, Any], key: str, context: str, errors: list[str]) -> float | None:
    value = _as_number(data.get(key))
    if value is None:
        errors.append(f"{context} must be numeric")
        return None
    return value


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _sort_number(value: Any) -> float:
    number = _as_number(value)
    return number if number is not None else 0.0
