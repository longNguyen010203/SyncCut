import json
from pathlib import Path
from typing import Annotated

import typer

from synccut.alignment_loader import load_section_assets
from synccut.remotion_assets import prepare_remotion_assets_file
from synccut.remotion_exporter import export_remotion_props_file
from synccut.scenes_loader import load_scenes
from synccut.timeline_builder import build_timeline as build_timeline_data
from synccut.timeline_inspector import build_timeline_overview
from synccut.timeline_validator import load_timeline_json, validate_timeline
from synccut.validators import SyncCutError
from synccut.visual_assets import (
    format_visual_asset_readiness,
    inspect_visual_asset_readiness_file,
    prepare_visual_assets_file,
    visual_asset_readiness_to_dict,
)

app = typer.Typer(help="Build structured video production timelines.")


@app.callback()
def main() -> None:
    """Build structured video production timelines."""


@app.command("build-timeline")
def build_timeline(
    scenes_json: Annotated[Path, typer.Argument(help="Path to scenes.json.")],
    audio_dir: Annotated[Path, typer.Option(help="Directory containing section audio files.")],
    alignment_dir: Annotated[
        Path, typer.Option(help="Directory containing section alignment JSON files.")
    ],
    out: Annotated[Path, typer.Option(help="Path to write timeline.json.")],
) -> None:
    """Build timeline.json from scenes, audio references, and alignment timestamps."""
    try:
        _, scenes = load_scenes(scenes_json)
        sections = load_section_assets(scenes, audio_dir, alignment_dir)
        timeline = build_timeline_data(scenes, sections, scenes_json)
        out.write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc


@app.command("validate-timeline")
def validate_timeline_cmd(
    timeline_json: Annotated[Path, typer.Argument(help="Path to timeline.json.")],
) -> None:
    """Validate timeline.json structure and timing."""
    try:
        data = load_timeline_json(timeline_json)
        result = validate_timeline(data, path=str(timeline_json))
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    if not result.ok:
        for error in result.errors:
            typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(1)

    typer.echo(f"OK {timeline_json}")
    typer.echo(f"scenes: {result.total_scenes}")
    typer.echo(f"sections: {result.total_sections}")
    typer.echo(f"duration_sec: {result.total_duration_sec}")
    warnings = [*data.get("warnings", []), *result.warnings]
    typer.echo(f"warnings: {len(warnings)}")
    for warning in warnings:
        typer.echo(f"Warning: {warning}")


@app.command("inspect")
def inspect_timeline_cmd(
    timeline_json: Annotated[Path, typer.Argument(help="Path to timeline.json.")],
) -> None:
    """Print a readable timeline overview grouped by section."""
    try:
        data = load_timeline_json(timeline_json)
        overview = build_timeline_overview(data, path=timeline_json)
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(overview, nl=False)


@app.command("export-remotion")
def export_remotion_cmd(
    timeline_json: Annotated[Path, typer.Argument(help="Path to timeline.json.")],
    out: Annotated[Path, typer.Option(help="Path to write Remotion props JSON.")],
) -> None:
    """Export Remotion-friendly props JSON from timeline.json."""
    try:
        props = export_remotion_props_file(timeline_json, out)
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Exported {out}")
    typer.echo(f"scenes: {props['metadata']['total_scenes']}")
    typer.echo(f"sections: {props['metadata']['total_sections']}")
    typer.echo(f"fps: {props['metadata']['fps']}")
    typer.echo(f"duration_frames: {props['metadata']['duration_frames']}")
    typer.echo(f"warnings: {len(props['warnings'])}")


@app.command("prepare-remotion-assets")
def prepare_remotion_assets_cmd(
    props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
    out_dir: Annotated[Path, typer.Option(help="Remotion public directory.")],
) -> None:
    """Copy Remotion assets into the public directory and update props JSON."""
    try:
        result = prepare_remotion_assets_file(props_json, out_dir)
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Prepared Remotion assets for {props_json}")
    typer.echo(f"audio_copied: {result.copied}")
    typer.echo(f"audio_reused: {result.reused}")
    typer.echo(f"audio_overwritten: {result.overwritten}")
    typer.echo(f"audio_assets: {len(result.audio_assets)}")
    typer.echo(f"public_dir: {out_dir}")


@app.command("prepare-visual-assets")
def prepare_visual_assets_cmd(
    props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
    assets_dir: Annotated[Path, typer.Option(help="Directory containing local visual assets.")],
    out_dir: Annotated[Path, typer.Option(help="Remotion public directory.")],
) -> None:
    """Copy local visual assets into the public directory and update props JSON."""
    try:
        result = prepare_visual_assets_file(props_json, assets_dir, out_dir)
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Prepared Remotion visual assets for {props_json}")
    typer.echo(f"visual_copied: {result.copied}")
    typer.echo(f"visual_reused: {result.reused}")
    typer.echo(f"visual_overwritten: {result.overwritten}")
    typer.echo(f"visual_missing: {result.missing}")
    typer.echo(f"visual_assets: {len(result.visual_assets)}")
    typer.echo(f"public_dir: {out_dir}")


@app.command("inspect-visual-assets")
def inspect_visual_assets_cmd(
    props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Print machine-readable JSON.")
    ] = False,
) -> None:
    """Report AI_VIDEO and B_ROLL visual asset readiness from Remotion props."""
    try:
        summary = inspect_visual_asset_readiness_file(props_json)
    except SyncCutError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

    if json_output:
        typer.echo(json.dumps(visual_asset_readiness_to_dict(summary), indent=2))
        return

    typer.echo(format_visual_asset_readiness(summary), nl=False)


if __name__ == "__main__":
    app()
