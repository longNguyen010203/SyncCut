import json
from pathlib import Path
from typing import Annotated

import typer

from synccut.alignment_loader import load_section_assets
from synccut.scenes_loader import load_scenes
from synccut.timeline_builder import build_timeline as build_timeline_data
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


if __name__ == "__main__":
    app()
