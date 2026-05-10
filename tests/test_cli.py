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


def write_tiny_timeline(root: Path) -> Path:
    timeline_json = root / "timeline.json"
    timeline_json.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_scenes": 1,
                    "total_sections": 1,
                    "total_duration_sec": 2.0,
                },
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "section": "HOOK",
                        "section_order": 1,
                        "audio_path": "audio/01_HOOK.mp3",
                        "alignment_path": "alignments/01_HOOK_alignment.json",
                        "local_duration_sec": 2.0,
                        "global_start_sec": 0.0,
                        "global_end_sec": 2.0,
                    }
                ],
                "timeline": [
                    {
                        "scene_id": "scene_001",
                        "scene_order": 1,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "timing": {
                            "start_sec": 0.25,
                            "end_sec": 1.25,
                            "duration_sec": 1.0,
                            "local_start_sec": 0.25,
                            "local_end_sec": 1.25,
                        },
                        "audio": {"path": "audio/01_HOOK.mp3"},
                        "alignment": {
                            "path": "alignments/01_HOOK_alignment.json",
                            "match_method": "paragraph",
                            "matched_units": ["paragraph[0]"],
                        },
                        "dialogue": {
                            "text": "Hello world.",
                            "paragraphs": ["Hello world."],
                        },
                        "visual": {
                            "type": "B_ROLL",
                            "prompt": "A simple shot.",
                            "data": {"kind": "fixture"},
                        },
                        "warnings": [],
                    }
                ],
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    return timeline_json


def write_timeline_with_gap_warning(root: Path) -> Path:
    timeline_json = root / "timeline-with-gap.json"
    timeline_json.write_text(
        json.dumps(
            {
                "metadata": {
                    "total_scenes": 2,
                    "total_sections": 1,
                    "total_duration_sec": 6.0,
                },
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "section": "HOOK",
                        "section_order": 1,
                        "audio_path": "audio/01_HOOK.mp3",
                        "alignment_path": "alignments/01_HOOK_alignment.json",
                        "local_duration_sec": 6.0,
                        "global_start_sec": 0.0,
                        "global_end_sec": 6.0,
                    }
                ],
                "timeline": [
                    {
                        "scene_id": "scene_001",
                        "scene_order": 1,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "timing": {
                            "start_sec": 0.0,
                            "end_sec": 1.0,
                            "duration_sec": 1.0,
                            "local_start_sec": 0.0,
                            "local_end_sec": 1.0,
                        },
                        "audio": {"path": "audio/01_HOOK.mp3"},
                        "alignment": {
                            "path": "alignments/01_HOOK_alignment.json",
                            "match_method": "paragraph",
                            "matched_units": ["paragraph[0]"],
                        },
                        "dialogue": {"text": "First.", "paragraphs": ["First."]},
                        "visual": {"type": "AI_VIDEO", "prompt": "", "data": {}},
                        "warnings": [],
                    },
                    {
                        "scene_id": "scene_002",
                        "scene_order": 2,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "timing": {
                            "start_sec": 3.0,
                            "end_sec": 4.0,
                            "duration_sec": 1.0,
                            "local_start_sec": 3.0,
                            "local_end_sec": 4.0,
                        },
                        "audio": {"path": "audio/01_HOOK.mp3"},
                        "alignment": {
                            "path": "alignments/01_HOOK_alignment.json",
                            "match_method": "sentence",
                            "matched_units": ["sentence[0]"],
                        },
                        "dialogue": {"text": "Second.", "paragraphs": ["Second."]},
                        "visual": {"type": "CHART", "prompt": "", "data": {}},
                        "warnings": [],
                    },
                ],
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    return timeline_json


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


def test_validate_timeline_cli_succeeds_on_valid_timeline(tmp_path) -> None:
    timeline_json = write_tiny_timeline(tmp_path)

    result = CliRunner().invoke(app, ["validate-timeline", str(timeline_json)])

    assert result.exit_code == 0
    assert f"OK {timeline_json}" in result.output
    assert "scenes: 1" in result.output
    assert "sections: 1" in result.output
    assert "duration_sec: 2.0" in result.output
    assert "warnings: 0" in result.output


def test_validate_timeline_cli_prints_warnings_but_exits_zero(tmp_path) -> None:
    timeline_json = write_timeline_with_gap_warning(tmp_path)

    result = CliRunner().invoke(app, ["validate-timeline", str(timeline_json)])

    assert result.exit_code == 0
    assert "warnings: 1" in result.output
    assert "Warning:" in result.output
    assert "gap of 2.000s" in result.output


def test_validate_timeline_cli_prints_top_level_warnings(tmp_path) -> None:
    timeline_json = write_tiny_timeline(tmp_path)
    data = json.loads(timeline_json.read_text(encoding="utf-8"))
    data["warnings"] = ["source timeline warning"]
    timeline_json.write_text(json.dumps(data), encoding="utf-8")

    result = CliRunner().invoke(app, ["validate-timeline", str(timeline_json)])

    assert result.exit_code == 0
    assert "warnings: 1" in result.output
    assert "Warning: source timeline warning" in result.output


def test_validate_timeline_cli_fails_on_invalid_timeline(tmp_path) -> None:
    timeline_json = tmp_path / "timeline.json"
    timeline_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(app, ["validate-timeline", str(timeline_json)])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "missing sections" in result.output
    assert "Traceback" not in result.output


def test_inspect_cli_succeeds_on_valid_timeline(tmp_path) -> None:
    timeline_json = write_tiny_timeline(tmp_path)

    result = CliRunner().invoke(app, ["inspect", str(timeline_json)])

    assert result.exit_code == 0
    assert f"Timeline: {timeline_json}" in result.output
    assert "Scenes: 1" in result.output
    assert "Sections: 1" in result.output
    assert "Duration: 2.000s" in result.output
    assert "scene_001" in result.output


def test_inspect_cli_fails_on_malformed_input(tmp_path) -> None:
    timeline_json = tmp_path / "timeline.json"
    timeline_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(app, ["inspect", str(timeline_json)])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "timeline is not valid enough to inspect" in result.output
    assert "Traceback" not in result.output
