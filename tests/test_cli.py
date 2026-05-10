import json
from pathlib import Path

from typer.testing import CliRunner

from synccut.cli import app


def write_tiny_fixture(root: Path) -> tuple[Path, Path, Path]:
    scenes_json = root / "scenes.json"
    audio_dir = root / "audio"
    alignment_dir = root / "alignments"
    audio_dir.mkdir()
    alignment_dir.mkdir()

    scenes_json.write_text(
        json.dumps(
            {
                "metadata": {"schema_version": "1.1", "total_scenes": 1},
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "scene_order": 1,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "dialogue": {
                            "text": "Hello world.",
                            "paragraphs": ["Hello world."],
                        },
                        "visual": {
                            "type": "B-ROLL",
                            "prompt": "A simple shot.",
                            "data": {"kind": "fixture"},
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (audio_dir / "01_HOOK.mp3").write_bytes(b"placeholder")
    (alignment_dir / "01_HOOK_alignment_tmp.json").write_text(
        json.dumps(
            {
                "total_duration_sec": 2.0,
                "paragraphs": [
                    {
                        "paragraph": "Hello world.",
                        "start": 0.25,
                        "end": 1.25,
                        "sentences": [],
                    }
                ],
                "words": [],
            }
        ),
        encoding="utf-8",
    )
    return scenes_json, audio_dir, alignment_dir


def test_build_timeline_cli_succeeds_on_tiny_complete_fixture(tmp_path) -> None:
    scenes_json, audio_dir, alignment_dir = write_tiny_fixture(tmp_path)
    out = tmp_path / "timeline.json"

    result = CliRunner().invoke(
        app,
        [
            "build-timeline",
            str(scenes_json),
            "--audio-dir",
            str(audio_dir),
            "--alignment-dir",
            str(alignment_dir),
            "--out",
            str(out),
        ],
    )

    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(data) == {"metadata", "sections", "timeline", "warnings"}
    assert data["metadata"]["total_scenes"] == 1
    assert len(data["timeline"]) == 1
    assert data["timeline"][0]["timing"]["start_sec"] == 0.25
    assert data["timeline"][0]["visual"]["type"] == "B_ROLL"
    assert data["timeline"][0]["dialogue"]["text"] == "Hello world."


def test_build_timeline_cli_fails_clearly_on_invalid_input(tmp_path) -> None:
    scenes_json = tmp_path / "scenes.json"
    scenes_json.write_text(json.dumps({"scenes": []}), encoding="utf-8")
    audio_dir = tmp_path / "audio"
    alignment_dir = tmp_path / "alignments"
    audio_dir.mkdir()
    alignment_dir.mkdir()

    result = CliRunner().invoke(
        app,
        [
            "build-timeline",
            str(scenes_json),
            "--audio-dir",
            str(audio_dir),
            "--alignment-dir",
            str(alignment_dir),
            "--out",
            str(tmp_path / "timeline.json"),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "missing metadata" in result.output
    assert "Traceback" not in result.output
