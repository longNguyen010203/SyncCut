from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from synccut.alignment_loader import load_section_assets
from synccut.preflight import inspect_preflight_file
from synccut.remotion_assets import prepare_remotion_assets_file
from synccut.remotion_exporter import export_remotion_props_file
from synccut.scenes_loader import load_scenes
from synccut.timeline_builder import build_timeline
from synccut.timeline_validator import load_timeline_json, validate_timeline
from synccut.validators import SyncCutError
from synccut.visual_assets import inspect_visual_asset_readiness_file, prepare_visual_assets_file
from synccut.visual_duration import write_visual_duration_report_file
from synccut.visual_manifest import write_visual_manifest_file

PIPELINE_SCHEMA_VERSION = "0.1"
PIPELINE_GENERATOR = "synccut pipeline-check"
DEFAULT_PIPELINE_REPORT = "pipeline_check_report.json"
NEXT_STEPS = [
    "cd remotion",
    "npm run typecheck",
    "npm run render:smoke:local",
    "npm run render:final:local",
]

STATUS_PASS = "PASS"
STATUS_WARN = "WARN"
STATUS_SKIP = "SKIP"
STATUS_FAIL = "FAIL"


@dataclass(frozen=True)
class PipelineStepResult:
    name: str
    status: str
    message: str
    paths: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    counts: dict[str, int | float | str | None] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineCheckResult:
    metadata: dict[str, Any]
    steps: list[PipelineStepResult]
    summary: dict[str, int]
    report_path: Path
    next_steps: list[str]


def run_pipeline_check(
    scenes_json: Path,
    *,
    audio_dir: Path,
    alignment_dir: Path,
    visual_assets_dir: Path = Path("assets/visuals"),
    timeline_out: Path = Path("timeline.json"),
    props_out: Path = Path("remotion/props.json"),
    public_dir: Path = Path("remotion/public"),
    generated_dir: Path = Path("generated"),
    skip_visual_duration: bool = False,
    overwrite_reports: bool = True,
    prepare_visual_assets: bool = True,
    pipeline_report_out: Path | None = None,
) -> PipelineCheckResult:
    """Run the local deterministic readiness pipeline and write a JSON report."""
    metadata = _metadata(
        scenes_json=scenes_json,
        audio_dir=audio_dir,
        alignment_dir=alignment_dir,
        visual_assets_dir=visual_assets_dir,
        timeline_out=timeline_out,
        props_out=props_out,
        public_dir=public_dir,
        generated_dir=generated_dir,
        skip_visual_duration=skip_visual_duration,
        overwrite_reports=overwrite_reports,
        prepare_visual_assets=prepare_visual_assets,
    )
    report_path = pipeline_report_out or (generated_dir / DEFAULT_PIPELINE_REPORT)
    steps: list[PipelineStepResult] = []

    try:
        steps.append(_build_timeline_step(scenes_json, audio_dir, alignment_dir, timeline_out))
        steps.append(_validate_timeline_step(timeline_out))
        steps.append(_export_remotion_step(timeline_out, props_out))
        steps.append(_prepare_audio_step(props_out, public_dir))
        steps.append(
            _visual_manifest_step(
                props_out,
                visual_assets_dir,
                generated_dir / "visual_manifest.md",
                "markdown",
                overwrite_reports,
            )
        )
        steps.append(
            _visual_manifest_step(
                props_out,
                visual_assets_dir,
                generated_dir / "visual_manifest.json",
                "json",
                overwrite_reports,
            )
        )
        steps.append(
            _visual_duration_step(
                props_out,
                visual_assets_dir,
                generated_dir / "visual_duration_report.md",
                skip_visual_duration,
                overwrite_reports,
            )
        )
        if prepare_visual_assets:
            steps.append(_prepare_visual_assets_step(props_out, visual_assets_dir, public_dir))
        else:
            steps.append(
                PipelineStepResult(
                    name="prepare_visual_assets",
                    status=STATUS_SKIP,
                    message="Visual asset preparation disabled; placeholders may render.",
                    paths={"assets_dir": str(visual_assets_dir), "public_dir": str(public_dir)},
                )
            )
        steps.append(_inspect_visual_assets_step(props_out))
        steps.append(_preflight_step(props_out, public_dir))
    except SyncCutError as exc:
        fail_step = PipelineStepResult(
            name="pipeline_check",
            status=STATUS_FAIL,
            message=str(exc),
        )
        failed_steps = [*steps, fail_step]
        result = PipelineCheckResult(
            metadata=metadata,
            steps=failed_steps,
            summary=_summary(failed_steps),
            report_path=report_path,
            next_steps=NEXT_STEPS,
        )
        _write_pipeline_report(result)
        raise

    result = PipelineCheckResult(
        metadata=metadata,
        steps=steps,
        summary=_summary(steps),
        report_path=report_path,
        next_steps=NEXT_STEPS,
    )
    _write_pipeline_report(result)
    return result


def pipeline_report_to_dict(result: PipelineCheckResult) -> dict[str, Any]:
    return {
        "schema_version": PIPELINE_SCHEMA_VERSION,
        "metadata": {
            "generated_by": PIPELINE_GENERATOR,
            **result.metadata,
        },
        "steps": [_step_to_dict(step) for step in result.steps],
        "summary": result.summary,
        "next_steps": result.next_steps,
    }


def format_pipeline_summary(result: PipelineCheckResult) -> str:
    lines = ["Pipeline check"]
    for step in result.steps:
        lines.append(f"{step.status} {step.name}: {step.message}")
    lines.extend(
        [
            "Pipeline check complete",
            f"passed: {result.summary['pass']}",
            f"warnings: {result.summary['warn']}",
            f"skipped: {result.summary['skip']}",
            f"failed: {result.summary['fail']}",
            f"report: {result.report_path}",
            "Next: cd remotion && npm run typecheck",
            "Next: cd remotion && npm run render:smoke:local",
            "Next: cd remotion && npm run render:final:local",
        ]
    )
    return "\n".join(lines) + "\n"


def _build_timeline_step(
    scenes_json: Path, audio_dir: Path, alignment_dir: Path, timeline_out: Path
) -> PipelineStepResult:
    _, scenes = load_scenes(scenes_json)
    sections = load_section_assets(scenes, audio_dir, alignment_dir)
    timeline = build_timeline(scenes, sections, scenes_json)
    try:
        timeline_out.parent.mkdir(parents=True, exist_ok=True)
        timeline_out.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SyncCutError(f"{timeline_out}: failed to write timeline: {exc}") from exc

    metadata = timeline["metadata"]
    return PipelineStepResult(
        name="build_timeline",
        status=STATUS_PASS,
        message=f"Built timeline {timeline_out}",
        paths={"out": str(timeline_out)},
        warnings=list(timeline.get("warnings", [])),
        counts={
            "sections": metadata.get("total_sections"),
            "scenes": metadata.get("total_scenes"),
            "duration_sec": metadata.get("total_duration_sec"),
        },
    )


def _validate_timeline_step(timeline_out: Path) -> PipelineStepResult:
    data = load_timeline_json(timeline_out)
    result = validate_timeline(data, path=str(timeline_out))
    if not result.ok:
        raise SyncCutError(f"{timeline_out}: timeline validation failed: {'; '.join(result.errors)}")
    warnings = [*data.get("warnings", []), *result.warnings]
    status = STATUS_WARN if warnings else STATUS_PASS
    return PipelineStepResult(
        name="validate_timeline",
        status=status,
        message=f"Validated timeline {timeline_out}",
        paths={"timeline": str(timeline_out)},
        warnings=warnings,
        counts={
            "sections": result.total_sections,
            "scenes": result.total_scenes,
            "duration_sec": result.total_duration_sec,
        },
    )


def _export_remotion_step(timeline_out: Path, props_out: Path) -> PipelineStepResult:
    props = export_remotion_props_file(timeline_out, props_out)
    warnings = list(props.get("warnings", []))
    status = STATUS_WARN if warnings else STATUS_PASS
    metadata = props.get("metadata", {})
    composition = props.get("composition", {})
    return PipelineStepResult(
        name="export_remotion",
        status=status,
        message=f"Exported Remotion props {props_out}",
        paths={"timeline": str(timeline_out), "props": str(props_out)},
        warnings=warnings,
        counts={
            "sections": metadata.get("total_sections"),
            "scenes": metadata.get("total_scenes"),
            "fps": composition.get("fps"),
            "duration_frames": composition.get("duration_frames"),
        },
    )


def _prepare_audio_step(props_out: Path, public_dir: Path) -> PipelineStepResult:
    result = prepare_remotion_assets_file(props_out, public_dir)
    return PipelineStepResult(
        name="prepare_remotion_assets",
        status=STATUS_PASS,
        message=f"Prepared Remotion audio assets in {public_dir}",
        paths={"props": str(props_out), "public_dir": str(public_dir), "audio_dir": str(result.audio_dir)},
        counts={
            "audio_copied": result.copied,
            "audio_reused": result.reused,
            "audio_overwritten": result.overwritten,
            "audio_assets": len(result.audio_assets),
        },
    )


def _visual_manifest_step(
    props_out: Path,
    visual_assets_dir: Path,
    out_path: Path,
    output_format: str,
    overwrite_reports: bool,
) -> PipelineStepResult:
    result = write_visual_manifest_file(
        props_out,
        assets_dir=visual_assets_dir,
        out_path=out_path,
        output_format=output_format,
        overwrite=overwrite_reports,
    )
    summary = result.manifest.summary
    return PipelineStepResult(
        name=f"visual_manifest_{output_format}",
        status=STATUS_PASS,
        message=f"Visual manifest {result.status}: {out_path}",
        paths={"props": str(props_out), "assets_dir": str(visual_assets_dir), "out": str(out_path)},
        counts={
            "target_scenes": summary.target_scenes,
            "prepared": summary.prepared,
            "missing": summary.missing,
            "unsupported": summary.unsupported,
            "local_found": summary.local_found,
            "local_missing": summary.local_missing,
        },
    )


def _visual_duration_step(
    props_out: Path,
    visual_assets_dir: Path,
    out_path: Path,
    skip_visual_duration: bool,
    overwrite_reports: bool,
) -> PipelineStepResult:
    if skip_visual_duration:
        return PipelineStepResult(
            name="inspect_visual_duration",
            status=STATUS_SKIP,
            message="Visual duration inspection skipped by option.",
            paths={"props": str(props_out), "assets_dir": str(visual_assets_dir), "out": str(out_path)},
        )

    try:
        result = write_visual_duration_report_file(
            props_out,
            assets_dir=visual_assets_dir,
            out_path=out_path,
            output_format="markdown",
            overwrite=overwrite_reports,
        )
    except SyncCutError as exc:
        if _is_ffprobe_unavailable_error(str(exc)):
            return PipelineStepResult(
                name="inspect_visual_duration",
                status=STATUS_WARN,
                message=(
                    "Visual duration report skipped because ffprobe is unavailable; "
                    "install FFmpeg tools or use inspect-visual-duration with --ffprobe-bin."
                ),
                paths={
                    "props": str(props_out),
                    "assets_dir": str(visual_assets_dir),
                    "out": str(out_path),
                },
                warnings=[str(exc)],
            )
        raise

    summary = result.report.summary
    warnings = []
    warning_count = (
        summary.video_short_loops
        + summary.video_very_short_repetitive
        + summary.video_long_trimmed
        + summary.aspect_ratio_warning
        + summary.unreadable
    )
    if warning_count:
        warnings.append(f"visual_duration_warnings: {warning_count}")
    return PipelineStepResult(
        name="inspect_visual_duration",
        status=STATUS_WARN if warnings else STATUS_PASS,
        message=f"Visual duration report {result.status}: {out_path}",
        paths={"props": str(props_out), "assets_dir": str(visual_assets_dir), "out": str(out_path)},
        warnings=warnings,
        counts={
            "target_scenes": summary.target_scenes,
            "images": summary.images,
            "videos": summary.videos,
            "missing": summary.missing,
            "unsupported": summary.unsupported,
            "unreadable": summary.unreadable,
        },
    )


def _prepare_visual_assets_step(
    props_out: Path, visual_assets_dir: Path, public_dir: Path
) -> PipelineStepResult:
    result = prepare_visual_assets_file(props_out, visual_assets_dir, public_dir)
    status = STATUS_WARN if result.missing else STATUS_PASS
    warnings = [f"missing local visual assets: {result.missing}"] if result.missing else []
    return PipelineStepResult(
        name="prepare_visual_assets",
        status=status,
        message=f"Prepared visual assets in {public_dir}",
        paths={
            "props": str(props_out),
            "assets_dir": str(visual_assets_dir),
            "public_dir": str(public_dir),
            "visuals_dir": str(result.visuals_dir),
        },
        warnings=warnings,
        counts={
            "visual_copied": result.copied,
            "visual_reused": result.reused,
            "visual_overwritten": result.overwritten,
            "visual_missing": result.missing,
            "visual_assets": len(result.visual_assets),
        },
    )


def _inspect_visual_assets_step(props_out: Path) -> PipelineStepResult:
    summary = inspect_visual_asset_readiness_file(props_out)
    warnings = []
    if summary.missing:
        warnings.append("Missing optional AI_VIDEO/B_ROLL visuals will render placeholders.")
    if summary.unsupported:
        raise SyncCutError(f"{props_out}: unsupported prepared visual assets: {summary.unsupported}")
    return PipelineStepResult(
        name="inspect_visual_assets",
        status=STATUS_WARN if warnings else STATUS_PASS,
        message=f"Inspected visual assets for {props_out}",
        paths={"props": str(props_out)},
        warnings=warnings,
        counts={
            "target_scenes": len(summary.items),
            "prepared": summary.prepared,
            "missing": summary.missing,
            "unsupported": summary.unsupported,
        },
    )


def _preflight_step(props_out: Path, public_dir: Path) -> PipelineStepResult:
    summary = inspect_preflight_file(props_out, verify_files=True, public_dir=public_dir)
    warnings = [issue.message for issue in summary.warnings]
    if summary.errors or summary.file_errors:
        error_text = "; ".join(issue.message for issue in summary.errors)
        if summary.file_errors and not error_text:
            error_text = f"{summary.file_errors} public file verification errors"
        raise SyncCutError(f"{props_out}: preflight failed: {error_text}")
    return PipelineStepResult(
        name="preflight",
        status=STATUS_WARN if warnings else STATUS_PASS,
        message=f"Verified preflight status {summary.status}",
        paths={"props": str(props_out), "public_dir": str(public_dir)},
        warnings=warnings,
        counts={
            "scenes": summary.scenes,
            "sections": summary.sections,
            "audio_prepared": summary.audio_prepared,
            "audio_missing_public_path": summary.audio_missing_public_path,
            "visual_prepared": summary.visual_prepared,
            "visual_missing": summary.visual_missing,
            "visual_unsupported": summary.visual_unsupported,
            "errors": len(summary.errors),
            "file_errors": summary.file_errors,
        },
    )


def _write_pipeline_report(result: PipelineCheckResult) -> None:
    content = json.dumps(pipeline_report_to_dict(result), indent=2, ensure_ascii=False) + "\n"
    try:
        result.report_path.parent.mkdir(parents=True, exist_ok=True)
        result.report_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise SyncCutError(f"{result.report_path}: failed to write pipeline report: {exc}") from exc


def _summary(steps: list[PipelineStepResult]) -> dict[str, int]:
    return {
        "total": len(steps),
        "pass": sum(1 for step in steps if step.status == STATUS_PASS),
        "warn": sum(1 for step in steps if step.status == STATUS_WARN),
        "skip": sum(1 for step in steps if step.status == STATUS_SKIP),
        "fail": sum(1 for step in steps if step.status == STATUS_FAIL),
    }


def _metadata(
    *,
    scenes_json: Path,
    audio_dir: Path,
    alignment_dir: Path,
    visual_assets_dir: Path,
    timeline_out: Path,
    props_out: Path,
    public_dir: Path,
    generated_dir: Path,
    skip_visual_duration: bool,
    overwrite_reports: bool,
    prepare_visual_assets: bool,
) -> dict[str, Any]:
    return {
        "scenes_json": str(scenes_json),
        "audio_dir": str(audio_dir),
        "alignment_dir": str(alignment_dir),
        "visual_assets_dir": str(visual_assets_dir),
        "timeline_out": str(timeline_out),
        "props_out": str(props_out),
        "public_dir": str(public_dir),
        "generated_dir": str(generated_dir),
        "prepare_visual_assets": prepare_visual_assets,
        "skip_visual_duration": skip_visual_duration,
        "overwrite_reports": overwrite_reports,
    }


def _step_to_dict(step: PipelineStepResult) -> dict[str, Any]:
    return {
        "name": step.name,
        "status": step.status,
        "message": step.message,
        "paths": step.paths,
        "warnings": step.warnings,
        "counts": step.counts,
    }


def _is_ffprobe_unavailable_error(message: str) -> bool:
    lowered = message.lower()
    return "ffprobe" in lowered or "--ffprobe-bin" in lowered
