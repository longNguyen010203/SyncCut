from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from synccut.remotion_assets import load_remotion_props
from synccut.validators import SUPPORTED_VISUAL_TYPES, SyncCutError, require_mapping
from synccut.visual_assets import inspect_visual_asset_readiness


@dataclass(frozen=True)
class PreflightIssue:
    level: str
    code: str
    message: str


@dataclass(frozen=True)
class PreflightSummary:
    props_path: Path
    status: str
    scenes: int
    sections: int
    duration_sec: float | None
    duration_frames: int | None
    fps: int | None
    audio_prepared: int
    audio_missing_public_path: int
    visual_target_scenes: int
    visual_prepared: int
    visual_missing: int
    visual_unsupported: int
    warnings: list[PreflightIssue]
    errors: list[PreflightIssue]


def inspect_preflight(props: dict[str, Any], props_path: Path) -> PreflightSummary:
    source_props = require_mapping(props, context=str(props_path))
    scenes = _require_array(source_props, "scenes", props_path)
    sections = _require_array(source_props, "sections", props_path)

    warnings: list[PreflightIssue] = []
    errors: list[PreflightIssue] = []

    composition = _optional_mapping(source_props.get("composition"))
    if composition is None:
        errors.append(_error("invalid_composition", "composition must be an object"))
        composition = {}

    composition_id = composition.get("id")
    if not _non_empty_string(composition_id):
        errors.append(_error("invalid_composition", "composition.id must be a non-empty string"))

    width = _positive_int(composition.get("width"))
    if width is None:
        errors.append(_error("invalid_composition", "composition.width must be a positive integer"))

    height = _positive_int(composition.get("height"))
    if height is None:
        errors.append(_error("invalid_composition", "composition.height must be a positive integer"))

    fps = _positive_int(composition.get("fps"))
    if fps is None:
        errors.append(_error("invalid_composition", "composition.fps must be a positive integer"))

    duration_frames = _positive_int(composition.get("duration_frames"))
    if duration_frames is None:
        errors.append(
            _error(
                "invalid_composition",
                "composition.duration_frames must be a positive integer",
            )
        )

    duration_sec = _metadata_checks(
        source_props.get("metadata"),
        scenes=scenes,
        sections=sections,
        composition_fps=fps,
        composition_duration_frames=duration_frames,
        warnings=warnings,
        errors=errors,
    )
    if duration_sec is None and duration_frames is not None and fps is not None:
        duration_sec = duration_frames / fps

    _root_warnings(source_props.get("warnings"), warnings, errors)

    audio_prepared, section_audio_missing = _section_checks(
        sections,
        composition_duration_frames=duration_frames,
        errors=errors,
    )
    root_audio_missing = _audio_asset_checks(source_props.get("assets"), errors)

    _scene_checks(scenes, composition_duration_frames=duration_frames, errors=errors)

    try:
        visual_summary = inspect_visual_asset_readiness(source_props, props_path)
    except SyncCutError as exc:
        errors.append(_error("invalid_visual_readiness", str(exc)))
        visual_target_scenes = 0
        visual_prepared = 0
        visual_missing = 0
        visual_unsupported = 0
    else:
        visual_target_scenes = len(visual_summary.items)
        visual_prepared = visual_summary.prepared
        visual_missing = visual_summary.missing
        visual_unsupported = visual_summary.unsupported
        for item in visual_summary.items:
            if item.status == "missing":
                warnings.append(
                    _warning(
                        "visual_missing",
                        f"{item.scene_id} {item.visual_type} missing visual asset; placeholder will render",
                    )
                )
            elif item.status == "unsupported":
                public_path = item.public_path if item.public_path is not None else "-"
                errors.append(
                    _error(
                        "visual_unsupported",
                        f"{item.scene_id} {item.visual_type} unsupported visual asset path {public_path}",
                    )
                )

    status = _status(warnings, errors)
    return PreflightSummary(
        props_path=props_path,
        status=status,
        scenes=len(scenes),
        sections=len(sections),
        duration_sec=duration_sec,
        duration_frames=duration_frames,
        fps=fps,
        audio_prepared=audio_prepared,
        audio_missing_public_path=section_audio_missing + root_audio_missing,
        visual_target_scenes=visual_target_scenes,
        visual_prepared=visual_prepared,
        visual_missing=visual_missing,
        visual_unsupported=visual_unsupported,
        warnings=warnings,
        errors=errors,
    )


def inspect_preflight_file(props_path: Path) -> PreflightSummary:
    props = load_remotion_props(props_path)
    return inspect_preflight(props, props_path)


def format_preflight(summary: PreflightSummary) -> str:
    lines = [
        f"Preflight: {summary.props_path}",
        f"status: {summary.status}",
        f"scenes: {summary.scenes}",
        f"sections: {summary.sections}",
        f"duration_sec: {_format_value(summary.duration_sec)}",
        f"duration_frames: {_format_value(summary.duration_frames)}",
        f"fps: {_format_value(summary.fps)}",
        f"audio_prepared: {summary.audio_prepared}",
        f"audio_missing_public_path: {summary.audio_missing_public_path}",
        f"visual_target_scenes: {summary.visual_target_scenes}",
        f"visual_prepared: {summary.visual_prepared}",
        f"visual_missing: {summary.visual_missing}",
        f"visual_unsupported: {summary.visual_unsupported}",
        f"warnings: {len(summary.warnings)}",
        f"errors: {len(summary.errors)}",
        "",
        "Warnings:",
    ]
    if summary.warnings:
        lines.extend(_format_issue(issue) for issue in summary.warnings)
    else:
        lines.append("none")

    lines.extend(["", "Errors:"])
    if summary.errors:
        lines.extend(_format_issue(issue) for issue in summary.errors)
    else:
        lines.append("none")

    return "\n".join(lines) + "\n"


def preflight_to_dict(summary: PreflightSummary) -> dict[str, Any]:
    return {
        "path": str(summary.props_path),
        "status": summary.status,
        "scenes": summary.scenes,
        "sections": summary.sections,
        "duration_sec": summary.duration_sec,
        "duration_frames": summary.duration_frames,
        "fps": summary.fps,
        "audio_prepared": summary.audio_prepared,
        "audio_missing_public_path": summary.audio_missing_public_path,
        "visual_target_scenes": summary.visual_target_scenes,
        "visual_prepared": summary.visual_prepared,
        "visual_missing": summary.visual_missing,
        "visual_unsupported": summary.visual_unsupported,
        "warnings": [_issue_to_dict(issue) for issue in summary.warnings],
        "errors": [_issue_to_dict(issue) for issue in summary.errors],
    }


def _metadata_checks(
    metadata_value: Any,
    *,
    scenes: list[Any],
    sections: list[Any],
    composition_fps: int | None,
    composition_duration_frames: int | None,
    warnings: list[PreflightIssue],
    errors: list[PreflightIssue],
) -> float | None:
    if metadata_value is None:
        return None
    metadata = _optional_mapping(metadata_value)
    if metadata is None:
        errors.append(_error("invalid_metadata", "metadata must be an object"))
        return None

    duration_sec = _positive_number(metadata.get("duration_sec"))
    if "duration_sec" in metadata and duration_sec is None:
        errors.append(_error("invalid_metadata", "metadata.duration_sec must be a positive number"))

    metadata_duration_frames = _non_negative_int(metadata.get("duration_frames"))
    if "duration_frames" in metadata and metadata_duration_frames is None:
        errors.append(
            _error("invalid_metadata", "metadata.duration_frames must be a non-negative integer")
        )
    elif (
        metadata_duration_frames is not None
        and composition_duration_frames is not None
        and metadata_duration_frames != composition_duration_frames
    ):
        errors.append(
            _error(
                "invalid_metadata",
                "metadata.duration_frames must match composition.duration_frames",
            )
        )

    metadata_fps = _non_negative_int(metadata.get("fps"))
    if "fps" in metadata and metadata_fps is None:
        errors.append(_error("invalid_metadata", "metadata.fps must be a non-negative integer"))
    elif metadata_fps is not None and composition_fps is not None and metadata_fps != composition_fps:
        errors.append(_error("invalid_metadata", "metadata.fps must match composition.fps"))

    total_scenes = _non_negative_int(metadata.get("total_scenes"))
    if "total_scenes" in metadata and total_scenes is None:
        errors.append(
            _error("invalid_metadata", "metadata.total_scenes must be a non-negative integer")
        )
    elif total_scenes is not None and total_scenes != len(scenes):
        errors.append(
            _error("invalid_metadata", "metadata.total_scenes must match scenes length")
        )

    total_sections = _non_negative_int(metadata.get("total_sections"))
    if "total_sections" in metadata and total_sections is None:
        errors.append(
            _error("invalid_metadata", "metadata.total_sections must be a non-negative integer")
        )
    elif total_sections is not None and total_sections != len(sections):
        errors.append(
            _error("invalid_metadata", "metadata.total_sections must match sections length")
        )

    return duration_sec


def _root_warnings(
    warnings_value: Any,
    warnings: list[PreflightIssue],
    errors: list[PreflightIssue],
) -> None:
    if warnings_value is None:
        return
    if not isinstance(warnings_value, list):
        errors.append(_error("invalid_warnings", "warnings must be an array"))
        return
    for index, warning in enumerate(warnings_value):
        if isinstance(warning, str):
            warnings.append(_warning("props_warning", warning))
        else:
            errors.append(
                _error("invalid_warnings", f"warnings[{index}] must be a string")
            )


def _section_checks(
    sections: list[Any],
    *,
    composition_duration_frames: int | None,
    errors: list[PreflightIssue],
) -> tuple[int, int]:
    audio_prepared = 0
    audio_missing = 0
    for index, section_value in enumerate(sections):
        context = f"sections[{index}]"
        section = _mapping_or_error(section_value, context, errors)
        if section is None:
            continue

        if not _non_empty_string(section.get("section_key")):
            errors.append(_error("invalid_section", f"{context}.section_key must be a non-empty string"))

        start = _int_or_error(section.get("start_frame"), f"{context}.start_frame", errors)
        end = _int_or_error(section.get("end_frame"), f"{context}.end_frame", errors)
        duration = _int_or_error(
            section.get("duration_frames"), f"{context}.duration_frames", errors
        )
        _validate_frame_range(
            context,
            start=start,
            end=end,
            duration=duration,
            composition_duration_frames=composition_duration_frames,
            errors=errors,
            code="invalid_section_timing",
        )

        audio = _mapping_or_error(section.get("audio"), f"{context}.audio", errors)
        if audio is None:
            audio_missing += 1
            errors.append(
                _error(
                    "missing_audio_public_path",
                    f"{context}.audio.public_path must be a non-empty string",
                )
            )
            continue
        if not _non_empty_string(audio.get("path")):
            errors.append(_error("invalid_audio", f"{context}.audio.path must be a non-empty string"))
        if _non_empty_string(audio.get("public_path")):
            audio_prepared += 1
        else:
            audio_missing += 1
            errors.append(
                _error(
                    "missing_audio_public_path",
                    f"{context}.audio.public_path must be a non-empty string",
                )
            )

    return audio_prepared, audio_missing


def _audio_asset_checks(assets_value: Any, errors: list[PreflightIssue]) -> int:
    assets = _mapping_or_error(assets_value, "assets", errors)
    if assets is None:
        return 0
    audio_entries = assets.get("audio")
    if not isinstance(audio_entries, list):
        errors.append(_error("invalid_audio", "assets.audio must be an array"))
        return 0

    missing = 0
    for index, entry_value in enumerate(audio_entries):
        context = f"assets.audio[{index}]"
        entry = _mapping_or_error(entry_value, context, errors)
        if entry is None:
            continue
        if not _non_empty_string(entry.get("section_key")):
            errors.append(
                _error("invalid_audio", f"{context}.section_key must be a non-empty string")
            )
        if not _non_empty_string(entry.get("path")):
            errors.append(_error("invalid_audio", f"{context}.path must be a non-empty string"))
        if not _non_empty_string(entry.get("public_path")):
            missing += 1
            errors.append(
                _error(
                    "missing_audio_public_path",
                    f"{context}.public_path must be a non-empty string",
                )
            )
    return missing


def _scene_checks(
    scenes: list[Any],
    *,
    composition_duration_frames: int | None,
    errors: list[PreflightIssue],
) -> None:
    for index, scene_value in enumerate(scenes):
        context = f"scenes[{index}]"
        scene = _mapping_or_error(scene_value, context, errors)
        if scene is None:
            continue
        if not _non_empty_string(scene.get("id")):
            errors.append(_error("invalid_scene", f"{context}.id must be a non-empty string"))
        if not _non_empty_string(scene.get("section_key")):
            errors.append(
                _error("invalid_scene", f"{context}.section_key must be a non-empty string")
            )

        visual_type = scene.get("visual_type")
        if not isinstance(visual_type, str) or visual_type not in SUPPORTED_VISUAL_TYPES:
            errors.append(
                _error(
                    "invalid_scene",
                    f"{context}.visual_type must be one of {', '.join(sorted(SUPPORTED_VISUAL_TYPES))}",
                )
            )

        start = _int_or_error(scene.get("start_frame"), f"{context}.start_frame", errors)
        end = _int_or_error(scene.get("end_frame"), f"{context}.end_frame", errors)
        duration = _int_or_error(scene.get("duration_frames"), f"{context}.duration_frames", errors)
        _validate_frame_range(
            context,
            start=start,
            end=end,
            duration=duration,
            composition_duration_frames=composition_duration_frames,
            errors=errors,
            code="invalid_scene_timing",
        )

        visual = _mapping_or_error(scene.get("visual"), f"{context}.visual", errors)
        if visual is not None and isinstance(visual_type, str) and visual.get("type") != visual_type:
            errors.append(
                _error("invalid_scene", f"{context}.visual.type must match visual_type")
            )

        dialogue = _mapping_or_error(scene.get("dialogue"), f"{context}.dialogue", errors)
        if dialogue is not None and not _non_empty_string(dialogue.get("text")):
            errors.append(
                _error("invalid_scene", f"{context}.dialogue.text must be a non-empty string")
            )


def _validate_frame_range(
    context: str,
    *,
    start: int | None,
    end: int | None,
    duration: int | None,
    composition_duration_frames: int | None,
    errors: list[PreflightIssue],
    code: str,
) -> None:
    if start is not None and start < 0:
        errors.append(_error(code, f"{context}.start_frame must be non-negative"))
    if end is not None and end < 0:
        errors.append(_error(code, f"{context}.end_frame must be non-negative"))
    if duration is not None and duration <= 0:
        errors.append(_error(code, f"{context}.duration_frames must be positive"))
    if start is not None and end is not None and duration is not None:
        if end - start != duration:
            errors.append(_error(code, f"{context}.duration_frames must equal end_frame - start_frame"))
    if end is not None and composition_duration_frames is not None and end > composition_duration_frames:
        errors.append(
            _error(code, f"{context}.end_frame must be <= composition.duration_frames")
        )


def _require_array(props: dict[str, Any], key: str, props_path: Path) -> list[Any]:
    value = props.get(key)
    if not isinstance(value, list):
        raise SyncCutError(f"{props_path}: {key} must be an array")
    return value


def _optional_mapping(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _mapping_or_error(
    value: Any, context: str, errors: list[PreflightIssue]
) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    errors.append(_error("invalid_structure", f"{context} must be an object"))
    return None


def _int_or_error(value: Any, context: str, errors: list[PreflightIssue]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(_error("invalid_timing", f"{context} must be an integer"))
        return None
    return value


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


def _non_negative_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _positive_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    return float(value)


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _status(warnings: list[PreflightIssue], errors: list[PreflightIssue]) -> str:
    if errors:
        return "error"
    if warnings:
        return "warning"
    return "ok"


def _warning(code: str, message: str) -> PreflightIssue:
    return PreflightIssue(level="warning", code=code, message=message)


def _error(code: str, message: str) -> PreflightIssue:
    return PreflightIssue(level="error", code=code, message=message)


def _format_issue(issue: PreflightIssue) -> str:
    return f"{issue.level} {issue.code} {issue.message}"


def _issue_to_dict(issue: PreflightIssue) -> dict[str, str]:
    return {"level": issue.level, "code": issue.code, "message": issue.message}


def _format_value(value: object) -> str:
    return "null" if value is None else str(value)
