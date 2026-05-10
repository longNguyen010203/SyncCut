import json
from pathlib import Path
from typing import Annotated

import typer

from synccut.alignment_loader import load_section_assets
from synccut.scenes_loader import load_scenes
from synccut.timeline_builder import build_timeline as build_timeline_data
from synccut.timeline_inspector import build_timeline_overview
from synccut.timeline_validator import load_timeline_json, validate_timeline
from synccut.validators import SyncCutError

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


if __name__ == "__main__":
    app()
