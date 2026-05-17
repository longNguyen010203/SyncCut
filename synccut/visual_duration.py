from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string
from synccut.visual_assets import (
    SUPPORTED_VISUAL_EXTENSIONS,
    TARGET_VISUAL_TYPES,
    load_visual_props,
)

REPORT_SCHEMA_VERSION = "0.1"
REPORT_GENERATOR = "synccut inspect-visual-duration"
DEFAULT_ASSETS_DIR = Path("assets/visuals")
DEFAULT_MARKDOWN_OUT = Path("generated/visual_duration_report.md")
DEFAULT_JSON_OUT = Path("generated/visual_duration_report.json")
SUPPORTED_REPORT_FORMATS = {"markdown", "json"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
EQUAL_DURATION_TOLERANCE_SEC = 0.25


@dataclass(frozen=True)
class VisualDurationProbe:
    duration_sec: float
    width: int | None = None
    height: int | None = None
    codec: str | None = None


@dataclass(frozen=True)
class VisualDurationSceneResult:
    scene_id: str
    section_key: str | None
    section: str | None
    visual_type: str
    scene_duration_sec: float | None
    scene_duration_frames: int | None
    asset_path: str | None
    asset_kind: str | None
    status: str
    warnings: list[str]
    asset_duration_sec: float | None
    loops_needed: float | None
    width: int | None
    height: int | None
    aspect_ratio: float | None
    codec: str | None
    notes: str


@dataclass(frozen=True)
class VisualDurationSummary:
    target_scenes: int
    images: int
    videos: int
    missing: int
    unsupported: int
    duplicate_supported: int
    unreadable: int
    image_ok: int
    video_ok: int
    video_short_loops: int
    video_very_short_repetitive: int
    video_long_trimmed: int
    aspect_ratio_warning: int


@dataclass(frozen=True)
class VisualDurationReport:
    props_path: Path
    assets_dir: Path
    output_format: str
    ffprobe_bin: str
    ffprobe_timeout_sec: int
    max_loops_before_warning: float
    min_duration_ratio: float
    aspect_min: float
    aspect_max: float
    scenes: list[VisualDurationSceneResult]
    summary: VisualDurationSummary


@dataclass(frozen=True)
class VisualDurationWriteResult:
    report: VisualDurationReport
    out_path: Path
    output_format: str
    status: str


ProbeRunner = Callable[[Path, str, int], VisualDurationProbe | None]


def default_visual_duration_out(output_format: str) -> Path:
    normalized = _normalize_format(output_format)
    if normalized == "json":
        return DEFAULT_JSON_OUT
    return DEFAULT_MARKDOWN_OUT


def build_visual_duration_report(
    props: dict[str, Any],
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    output_format: str = "markdown",
    ffprobe_bin: str = "ffprobe",
    ffprobe_timeout_sec: int = 15,
    max_loops_before_warning: float = 3,
    min_duration_ratio: float = 0.4,
    aspect_min: float = 1.55,
    aspect_max: float = 1.90,
    probe_runner: ProbeRunner | None = None,
) -> VisualDurationReport:
    normalized_format = _normalize_format(output_format)
    source_props = require_mapping(props, context=str(props_path))
    scenes_value = source_props.get("scenes")
    if not isinstance(scenes_value, list):
        raise SyncCutError(f"{props_path}: scenes must be an array")
    if ffprobe_timeout_sec <= 0:
        raise SyncCutError("--ffprobe-timeout must be greater than 0")
    if max_loops_before_warning <= 0:
        raise SyncCutError("--max-loops-before-warning must be greater than 0")
    if min_duration_ratio <= 0:
        raise SyncCutError("--min-duration-ratio must be greater than 0")
    if aspect_min <= 0 or aspect_max <= 0 or aspect_min >= aspect_max:
        raise SyncCutError("--aspect-min must be greater than 0 and less than --aspect-max")

    if assets_dir.exists() and not assets_dir.is_dir():
        raise SyncCutError(f"{assets_dir}: visual assets path must be a directory")

    runner = probe_runner or probe_video_with_ffprobe
    results: list[VisualDurationSceneResult] = []
    for index, scene_value in enumerate(scenes_value):
        context = f"{props_path}: scenes[{index}]"
        scene = require_mapping(scene_value, context=context)
        visual_type = scene.get("visual_type")
        if visual_type not in TARGET_VISUAL_TYPES:
            continue

        scene_id = require_non_empty_string(scene.get("id"), context=f"{context}.id")
        local_asset = _inspect_local_asset(assets_dir, scene_id)
        results.append(
            _build_scene_result(
                scene=scene,
                context=context,
                scene_id=scene_id,
                visual_type=str(visual_type),
                local_asset=local_asset,
                ffprobe_bin=ffprobe_bin,
                ffprobe_timeout_sec=ffprobe_timeout_sec,
                max_loops_before_warning=max_loops_before_warning,
                min_duration_ratio=min_duration_ratio,
                aspect_min=aspect_min,
                aspect_max=aspect_max,
                probe_runner=runner,
            )
        )

    return VisualDurationReport(
        props_path=props_path,
        assets_dir=assets_dir,
        output_format=normalized_format,
        ffprobe_bin=ffprobe_bin,
        ffprobe_timeout_sec=ffprobe_timeout_sec,
        max_loops_before_warning=max_loops_before_warning,
        min_duration_ratio=min_duration_ratio,
        aspect_min=aspect_min,
        aspect_max=aspect_max,
        scenes=results,
        summary=_build_summary(results),
    )


def build_visual_duration_report_file(
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    output_format: str = "markdown",
    ffprobe_bin: str = "ffprobe",
    ffprobe_timeout_sec: int = 15,
    max_loops_before_warning: float = 3,
    min_duration_ratio: float = 0.4,
    aspect_min: float = 1.55,
    aspect_max: float = 1.90,
    probe_runner: ProbeRunner | None = None,
) -> VisualDurationReport:
    props = load_visual_props(props_path)
    return build_visual_duration_report(
        props,
        props_path,
        assets_dir=assets_dir,
        output_format=output_format,
        ffprobe_bin=ffprobe_bin,
        ffprobe_timeout_sec=ffprobe_timeout_sec,
        max_loops_before_warning=max_loops_before_warning,
        min_duration_ratio=min_duration_ratio,
        aspect_min=aspect_min,
        aspect_max=aspect_max,
        probe_runner=probe_runner,
    )


def write_visual_duration_report_file(
    props_path: Path,
    *,
    assets_dir: Path = DEFAULT_ASSETS_DIR,
    out_path: Path | None = None,
    output_format: str = "markdown",
    overwrite: bool = False,
    ffprobe_bin: str = "ffprobe",
    ffprobe_timeout_sec: int = 15,
    max_loops_before_warning: float = 3,
    min_duration_ratio: float = 0.4,
    aspect_min: float = 1.55,
    aspect_max: float = 1.90,
    probe_runner: ProbeRunner | None = None,
) -> VisualDurationWriteResult:
    normalized_format = _normalize_format(output_format)
    resolved_out_path = out_path if out_path is not None else default_visual_duration_out(normalized_format)
    report = build_visual_duration_report_file(
        props_path,
        assets_dir=assets_dir,
        output_format=normalized_format,
        ffprobe_bin=ffprobe_bin,
        ffprobe_timeout_sec=ffprobe_timeout_sec,
        max_loops_before_warning=max_loops_before_warning,
        min_duration_ratio=min_duration_ratio,
        aspect_min=aspect_min,
        aspect_max=aspect_max,
        probe_runner=probe_runner,
    )
    content = format_visual_duration_report(report)
    status = _planned_write_status(resolved_out_path, content)
    if status == "block" and not overwrite:
        raise SyncCutError(
            f"{resolved_out_path}: output exists and differs; rerun with --overwrite to replace"
        )

    if status in {"create", "block"}:
        try:
            resolved_out_path.parent.mkdir(parents=True, exist_ok=True)
            resolved_out_path.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise SyncCutError(
                f"{resolved_out_path}: failed to write visual duration report: {exc}"
            ) from exc
        status = "written"
    else:
        status = "reused"

    return VisualDurationWriteResult(
        report=report,
        out_path=resolved_out_path,
        output_format=normalized_format,
        status=status,
    )


def format_visual_duration_report(report: VisualDurationReport) -> str:
    if report.output_format == "json":
        return json.dumps(visual_duration_report_to_dict(report), indent=2, ensure_ascii=False) + "\n"
    return format_visual_duration_report_markdown(report)


def format_visual_duration_report_markdown(report: VisualDurationReport) -> str:
    summary = report.summary
    lines = [
        "# Visual Duration Report",
        "",
        f"Source props: {report.props_path}",
        f"Assets dir: {report.assets_dir}",
        f"ffprobe: {report.ffprobe_bin}",
        "",
        "## Thresholds",
        "",
        f"- max_loops_before_warning: {report.max_loops_before_warning:g}",
        f"- min_duration_ratio: {report.min_duration_ratio:g}",
        f"- aspect_min: {report.aspect_min:g}",
        f"- aspect_max: {report.aspect_max:g}",
        "",
        "## Summary",
        "",
    ]
    for key, value in _summary_to_dict(summary).items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Scenes",
            "",
            (
                "| scene_id | section_key | visual_type | scene_sec | asset | kind | "
                "asset_sec | loops | dimensions | status | warnings | notes |"
            ),
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scene in report.scenes:
        dimensions = (
            f"{scene.width}x{scene.height}"
            if scene.width is not None and scene.height is not None
            else "-"
        )
        lines.append(
            " | ".join(
                [
                    "| " + scene.scene_id,
                    _markdown_value(scene.section_key),
                    scene.visual_type,
                    _markdown_value(scene.scene_duration_sec),
                    _markdown_value(scene.asset_path),
                    _markdown_value(scene.asset_kind),
                    _markdown_value(scene.asset_duration_sec),
                    _markdown_value(scene.loops_needed),
                    dimensions,
                    scene.status,
                    ", ".join(scene.warnings) if scene.warnings else "-",
                    _markdown_value(scene.notes),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def visual_duration_report_to_dict(report: VisualDurationReport) -> dict[str, Any]:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "metadata": {
            "generated_by": REPORT_GENERATOR,
            "source_props": str(report.props_path),
            "assets_dir": str(report.assets_dir),
            "format": report.output_format,
            "ffprobe_bin": report.ffprobe_bin,
            "ffprobe_timeout_sec": report.ffprobe_timeout_sec,
            "thresholds": {
                "max_loops_before_warning": report.max_loops_before_warning,
                "min_duration_ratio": report.min_duration_ratio,
                "aspect_min": report.aspect_min,
                "aspect_max": report.aspect_max,
            },
        },
        "summary": _summary_to_dict(report.summary),
        "scenes": [_scene_to_dict(scene) for scene in report.scenes],
    }


def probe_video_with_ffprobe(
    asset_path: Path, ffprobe_bin: str = "ffprobe", timeout_sec: int = 15
) -> VisualDurationProbe | None:
    command = [
        ffprobe_bin,
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_streams",
        "-show_format",
        str(asset_path),
    ]
    try:
        completed = subprocess.run(
            command,
            shell=False,
            timeout=timeout_sec,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SyncCutError(
            f"{ffprobe_bin}: ffprobe executable not found; install FFmpeg tools or pass --ffprobe-bin"
        ) from exc
    except subprocess.TimeoutExpired:
        return None

    if completed.returncode != 0:
        return None

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None

    return _probe_from_ffprobe_json(data)


def _build_scene_result(
    *,
    scene: dict[str, Any],
    context: str,
    scene_id: str,
    visual_type: str,
    local_asset: dict[str, Any],
    ffprobe_bin: str,
    ffprobe_timeout_sec: int,
    max_loops_before_warning: float,
    min_duration_ratio: float,
    aspect_min: float,
    aspect_max: float,
    probe_runner: ProbeRunner,
) -> VisualDurationSceneResult:
    base = {
        "scene_id": scene_id,
        "section_key": _optional_string(scene.get("section_key")),
        "section": _optional_string(scene.get("section")),
        "visual_type": visual_type,
        "scene_duration_sec": _optional_number(scene.get("duration_sec")),
        "scene_duration_frames": _optional_int(scene.get("duration_frames")),
    }

    status = local_asset["status"]
    if status == "missing":
        return _scene_result(**base, status="missing", notes="No local visual asset found.")
    if status == "unsupported":
        return _scene_result(
            **base,
            status="unsupported",
            notes="Only unsupported same-stem local files were found.",
        )
    if status == "duplicate_supported":
        return _scene_result(
            **base,
            status="duplicate_supported",
            notes="Multiple supported same-stem local files were found; keep exactly one.",
        )

    asset_path = Path(local_asset["asset_path"])
    suffix = asset_path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return _scene_result(
            **base,
            asset_path=str(asset_path),
            asset_kind="image",
            status="image_ok",
            notes="Image asset is duration-independent.",
        )
    if suffix not in VIDEO_EXTENSIONS:
        return _scene_result(
            **base,
            asset_path=str(asset_path),
            status="unsupported",
            notes="Supported asset has an unexpected non-video/non-image suffix.",
        )

    scene_duration = base["scene_duration_sec"]
    if scene_duration is None or scene_duration <= 0:
        return _scene_result(
            **base,
            asset_path=str(asset_path),
            asset_kind="video",
            status="unreadable",
            warnings=["unreadable_metadata"],
            notes=f"{context}: missing_scene_duration.",
        )

    probe = probe_runner(asset_path, ffprobe_bin, ffprobe_timeout_sec)
    if probe is None or probe.duration_sec <= 0:
        return _scene_result(
            **base,
            asset_path=str(asset_path),
            asset_kind="video",
            status="unreadable",
            warnings=["unreadable_metadata"],
            notes="Video metadata is unreadable.",
        )

    return _video_scene_result(
        **base,
        asset_path=str(asset_path),
        scene_duration=scene_duration,
        probe=probe,
        max_loops_before_warning=max_loops_before_warning,
        min_duration_ratio=min_duration_ratio,
        aspect_min=aspect_min,
        aspect_max=aspect_max,
    )


def _video_scene_result(
    *,
    scene_id: str,
    section_key: str | None,
    section: str | None,
    visual_type: str,
    scene_duration_sec: float | None,
    scene_duration_frames: int | None,
    asset_path: str,
    scene_duration: float,
    probe: VisualDurationProbe,
    max_loops_before_warning: float,
    min_duration_ratio: float,
    aspect_min: float,
    aspect_max: float,
) -> VisualDurationSceneResult:
    asset_duration = probe.duration_sec
    warnings: list[str] = []
    loops_needed: float | None = None

    if abs(asset_duration - scene_duration) <= EQUAL_DURATION_TOLERANCE_SEC:
        status = "video_ok"
        notes = "Video duration is close to scene duration."
    elif asset_duration < scene_duration:
        loops_needed = scene_duration / asset_duration
        if loops_needed > max_loops_before_warning or asset_duration / scene_duration < min_duration_ratio:
            status = "video_very_short_repetitive"
            warnings.extend(["loops", "repetitive_loop"])
            notes = "Video is much shorter than scene duration and may look repetitive."
        else:
            status = "video_short_loops"
            warnings.append("loops")
            notes = "Video is shorter than scene duration and will loop."
    else:
        status = "video_long_trimmed"
        warnings.append("trimmed")
        notes = "Video is longer than scene duration and will be trimmed by Remotion timing."

    aspect_ratio = _aspect_ratio(probe.width, probe.height)
    if aspect_ratio is not None and (aspect_ratio < aspect_min or aspect_ratio > aspect_max):
        warnings.append("aspect_ratio_warning")

    return VisualDurationSceneResult(
        scene_id=scene_id,
        section_key=section_key,
        section=section,
        visual_type=visual_type,
        scene_duration_sec=scene_duration_sec,
        scene_duration_frames=scene_duration_frames,
        asset_path=asset_path,
        asset_kind="video",
        status=status,
        warnings=warnings,
        asset_duration_sec=asset_duration,
        loops_needed=_round_optional(loops_needed),
        width=probe.width,
        height=probe.height,
        aspect_ratio=_round_optional(aspect_ratio),
        codec=probe.codec,
        notes=notes,
    )


def _probe_from_ffprobe_json(data: Any) -> VisualDurationProbe | None:
    if not isinstance(data, dict):
        return None
    streams = data.get("streams")
    if not isinstance(streams, list):
        return None
    video_stream = next(
        (stream for stream in streams if isinstance(stream, dict) and stream.get("codec_type") == "video"),
        None,
    )
    if video_stream is None:
        return None

    format_value = data.get("format")
    duration = None
    if isinstance(format_value, dict):
        duration = _parse_positive_number(format_value.get("duration"))
    if duration is None:
        duration = _parse_positive_number(video_stream.get("duration"))
    if duration is None:
        return None

    return VisualDurationProbe(
        duration_sec=duration,
        width=_optional_int(video_stream.get("width")),
        height=_optional_int(video_stream.get("height")),
        codec=_optional_string(video_stream.get("codec_name")),
    )


def _inspect_local_asset(assets_dir: Path, scene_id: str) -> dict[str, Any]:
    supported: list[Path] = []
    unsupported: list[Path] = []
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

    supported_paths = sorted(supported, key=lambda item: item.name.lower())
    unsupported_paths = sorted(unsupported, key=lambda item: item.name.lower())
    if len(supported_paths) == 1:
        return {"status": "found", "asset_path": str(supported_paths[0])}
    if len(supported_paths) > 1:
        return {"status": "duplicate_supported"}
    if unsupported_paths:
        return {"status": "unsupported"}
    return {"status": "missing"}


def _scene_result(
    *,
    scene_id: str,
    section_key: str | None,
    section: str | None,
    visual_type: str,
    scene_duration_sec: float | None,
    scene_duration_frames: int | None,
    status: str,
    notes: str,
    asset_path: str | None = None,
    asset_kind: str | None = None,
    warnings: list[str] | None = None,
) -> VisualDurationSceneResult:
    return VisualDurationSceneResult(
        scene_id=scene_id,
        section_key=section_key,
        section=section,
        visual_type=visual_type,
        scene_duration_sec=scene_duration_sec,
        scene_duration_frames=scene_duration_frames,
        asset_path=asset_path,
        asset_kind=asset_kind,
        status=status,
        warnings=warnings or [],
        asset_duration_sec=None,
        loops_needed=None,
        width=None,
        height=None,
        aspect_ratio=None,
        codec=None,
        notes=notes,
    )


def _scene_to_dict(scene: VisualDurationSceneResult) -> dict[str, Any]:
    return {
        "scene_id": scene.scene_id,
        "section_key": scene.section_key,
        "section": scene.section,
        "visual_type": scene.visual_type,
        "scene_duration_sec": scene.scene_duration_sec,
        "scene_duration_frames": scene.scene_duration_frames,
        "asset_path": scene.asset_path,
        "asset_kind": scene.asset_kind,
        "status": scene.status,
        "warnings": scene.warnings,
        "asset_duration_sec": scene.asset_duration_sec,
        "loops_needed": scene.loops_needed,
        "width": scene.width,
        "height": scene.height,
        "aspect_ratio": scene.aspect_ratio,
        "codec": scene.codec,
        "notes": scene.notes,
    }


def _build_summary(scenes: list[VisualDurationSceneResult]) -> VisualDurationSummary:
    return VisualDurationSummary(
        target_scenes=len(scenes),
        images=sum(1 for scene in scenes if scene.asset_kind == "image"),
        videos=sum(1 for scene in scenes if scene.asset_kind == "video"),
        missing=sum(1 for scene in scenes if scene.status == "missing"),
        unsupported=sum(1 for scene in scenes if scene.status == "unsupported"),
        duplicate_supported=sum(1 for scene in scenes if scene.status == "duplicate_supported"),
        unreadable=sum(1 for scene in scenes if scene.status == "unreadable"),
        image_ok=sum(1 for scene in scenes if scene.status == "image_ok"),
        video_ok=sum(1 for scene in scenes if scene.status == "video_ok"),
        video_short_loops=sum(1 for scene in scenes if scene.status == "video_short_loops"),
        video_very_short_repetitive=sum(
            1 for scene in scenes if scene.status == "video_very_short_repetitive"
        ),
        video_long_trimmed=sum(1 for scene in scenes if scene.status == "video_long_trimmed"),
        aspect_ratio_warning=sum(
            1 for scene in scenes if "aspect_ratio_warning" in scene.warnings
        ),
    )


def _summary_to_dict(summary: VisualDurationSummary) -> dict[str, int]:
    return {
        "target_scenes": summary.target_scenes,
        "images": summary.images,
        "videos": summary.videos,
        "missing": summary.missing,
        "unsupported": summary.unsupported,
        "duplicate_supported": summary.duplicate_supported,
        "unreadable": summary.unreadable,
        "image_ok": summary.image_ok,
        "video_ok": summary.video_ok,
        "video_short_loops": summary.video_short_loops,
        "video_very_short_repetitive": summary.video_very_short_repetitive,
        "video_long_trimmed": summary.video_long_trimmed,
        "aspect_ratio_warning": summary.aspect_ratio_warning,
    }


def _planned_write_status(path: Path, content: str) -> str:
    if not path.exists():
        return "create"
    if path.read_text(encoding="utf-8") == content:
        return "reuse"
    return "block"


def _normalize_format(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in SUPPORTED_REPORT_FORMATS:
        expected = ", ".join(sorted(SUPPORTED_REPORT_FORMATS))
        raise SyncCutError(f"unsupported visual duration format '{value}'; expected one of {expected}")
    return normalized


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


def _parse_positive_number(value: Any) -> float | None:
    if isinstance(value, str):
        try:
            value = float(value)
        except ValueError:
            return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    numeric = float(value)
    if numeric <= 0:
        return None
    return numeric


def _aspect_ratio(width: int | None, height: int | None) -> float | None:
    if width is None or height is None or width <= 0 or height <= 0:
        return None
    return width / height


def _round_optional(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 4)


def _markdown_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
    else:
        text = str(value)
    return text.replace("|", "\\|").replace("\n", " ")
