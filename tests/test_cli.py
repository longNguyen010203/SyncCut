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


def write_tiny_remotion_props(root: Path, audio_path: str) -> Path:
    props_json = root / "remotion" / "props.json"
    props_json.parent.mkdir(parents=True, exist_ok=True)
    props_json.write_text(
        json.dumps(
            {
                "metadata": {
                    "generated_by": "synccut export-remotion",
                    "source_timeline": "timeline.json",
                    "fps": 30,
                    "duration_sec": 2.0,
                    "duration_frames": 60,
                    "total_scenes": 1,
                    "total_sections": 1,
                },
                "composition": {
                    "id": "SyncCutVideo",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "duration_frames": 60,
                },
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "section": "HOOK",
                        "section_order": 1,
                        "start_sec": 0.0,
                        "end_sec": 2.0,
                        "duration_sec": 2.0,
                        "start_frame": 0,
                        "end_frame": 60,
                        "duration_frames": 60,
                        "audio": {"path": audio_path},
                        "alignment": {"path": "alignments/01_HOOK_alignment.json"},
                    }
                ],
                "scenes": [
                    {
                        "id": "scene_001",
                        "scene_order": 1,
                        "section": "HOOK",
                        "section_order": 1,
                        "section_key": "01_HOOK",
                        "start_sec": 0.0,
                        "end_sec": 2.0,
                        "duration_sec": 2.0,
                        "local_start_sec": 0.0,
                        "local_end_sec": 2.0,
                        "start_frame": 0,
                        "end_frame": 60,
                        "duration_frames": 60,
                        "visual_type": "AI_VIDEO",
                        "visual": {"type": "AI_VIDEO", "prompt": "Prompt", "data": None},
                        "dialogue": {"text": "Hello.", "paragraphs": ["Hello."]},
                        "audio": {"path": audio_path},
                        "alignment": {
                            "path": "alignments/01_HOOK_alignment.json",
                            "match_method": "paragraph",
                            "matched_units": ["paragraph:0"],
                        },
                        "warnings": [],
                    }
                ],
                "assets": {
                    "audio": [{"section_key": "01_HOOK", "path": audio_path}],
                    "visuals": [],
                },
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    return props_json


def write_tiny_visual_props(root: Path) -> Path:
    props_json = root / "remotion" / "props.json"
    props_json.parent.mkdir(parents=True, exist_ok=True)
    props_json.write_text(
        json.dumps(
            {
                "metadata": {
                    "generated_by": "synccut export-remotion",
                    "source_timeline": "timeline.json",
                    "fps": 30,
                    "duration_sec": 2.0,
                    "duration_frames": 60,
                    "total_scenes": 2,
                    "total_sections": 1,
                },
                "composition": {
                    "id": "SyncCutVideo",
                    "width": 1920,
                    "height": 1080,
                    "fps": 30,
                    "duration_frames": 60,
                },
                "sections": [],
                "scenes": [
                    {
                        "id": "scene_001",
                        "scene_order": 1,
                        "visual_type": "AI_VIDEO",
                        "visual": {"type": "AI_VIDEO", "prompt": "Prompt", "data": None},
                    },
                    {
                        "id": "scene_002",
                        "scene_order": 2,
                        "visual_type": "TABLE",
                        "visual": {"type": "TABLE", "prompt": "Table", "data": {"rows": []}},
                    },
                ],
                "assets": {"audio": [], "visuals": []},
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    return props_json


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


def test_export_remotion_cli_succeeds_on_tiny_complete_timeline(tmp_path) -> None:
    timeline_json = write_tiny_timeline(tmp_path)
    out = tmp_path / "remotion" / "props.json"

    result = CliRunner().invoke(app, ["export-remotion", str(timeline_json), "--out", str(out)])

    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert set(data) == {"metadata", "composition", "sections", "scenes", "assets", "warnings"}
    assert f"Exported {out}" in result.output
    assert "scenes: 1" in result.output
    assert "sections: 1" in result.output
    assert "fps: 30" in result.output
    assert "duration_frames: 60" in result.output
    assert data["metadata"]["duration_frames"] == 60
    assert data["scenes"][0]["id"] == "scene_001"


def test_export_remotion_cli_fails_clearly_on_invalid_timeline(tmp_path) -> None:
    timeline_json = tmp_path / "timeline.json"
    timeline_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["export-remotion", str(timeline_json), "--out", str(tmp_path / "props.json")],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "invalid timeline" in result.output
    assert "Traceback" not in result.output


def test_prepare_remotion_assets_cli_succeeds_on_tiny_props_fixture(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    audio_path = tmp_path / "audio" / "01_HOOK.mp3"
    audio_path.parent.mkdir()
    audio_path.write_bytes(b"audio")
    props_json = write_tiny_remotion_props(tmp_path, "audio/01_HOOK.mp3")
    out_dir = tmp_path / "remotion" / "public"

    result = CliRunner().invoke(
        app,
        ["prepare-remotion-assets", str(props_json), "--out-dir", str(out_dir)],
    )

    assert result.exit_code == 0
    assert (out_dir / "audio" / "01_HOOK.mp3").read_bytes() == b"audio"
    data = json.loads(props_json.read_text(encoding="utf-8"))
    assert data["assets"]["audio"][0]["public_path"] == "audio/01_HOOK.mp3"
    assert data["sections"][0]["audio"]["public_path"] == "audio/01_HOOK.mp3"
    assert data["scenes"][0]["audio"]["public_path"] == "audio/01_HOOK.mp3"
    assert f"Prepared Remotion assets for {props_json}" in result.output
    assert "audio_copied: 1" in result.output
    assert "audio_reused: 0" in result.output
    assert "audio_overwritten: 0" in result.output
    assert "audio_assets: 1" in result.output
    assert f"public_dir: {out_dir}" in result.output


def test_prepare_remotion_assets_cli_fails_on_malformed_props(tmp_path) -> None:
    props_json = tmp_path / "props.json"
    props_json.write_text(json.dumps({"assets": {}}), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["prepare-remotion-assets", str(props_json), "--out-dir", str(tmp_path / "public")],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "assets.audio must be an array" in result.output
    assert "Traceback" not in result.output


def test_prepare_remotion_assets_cli_fails_on_missing_source_audio(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    props_json = write_tiny_remotion_props(tmp_path, "audio/missing.mp3")

    result = CliRunner().invoke(
        app,
        [
            "prepare-remotion-assets",
            str(props_json),
            "--out-dir",
            str(tmp_path / "remotion" / "public"),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "source audio file not found" in result.output
    assert "Traceback" not in result.output


def test_prepare_visual_assets_cli_succeeds_on_tiny_props_fixture(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.png").write_bytes(b"image")
    out_dir = tmp_path / "remotion" / "public"

    result = CliRunner().invoke(
        app,
        [
            "prepare-visual-assets",
            str(props_json),
            "--assets-dir",
            str(assets_dir),
            "--out-dir",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "visuals" / "scene_001.png").read_bytes() == b"image"
    data = json.loads(props_json.read_text(encoding="utf-8"))
    assert data["scenes"][0]["visual"]["public_path"] == "visuals/scene_001.png"
    assert data["scenes"][0]["visual"]["asset_status"] == "prepared"
    assert data["scenes"][0]["visual"]["asset_source"] == "local"
    assert data["assets"]["visuals"][0]["scene_id"] == "scene_001"
    assert f"Prepared Remotion visual assets for {props_json}" in result.output
    assert "visual_copied: 1" in result.output
    assert "visual_reused: 0" in result.output
    assert "visual_overwritten: 0" in result.output
    assert "visual_missing: 0" in result.output
    assert "visual_assets: 1" in result.output
    assert f"public_dir: {out_dir}" in result.output


def test_prepare_visual_assets_cli_fails_on_malformed_props(tmp_path) -> None:
    props_json = tmp_path / "props.json"
    props_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "prepare-visual-assets",
            str(props_json),
            "--assets-dir",
            str(tmp_path / "assets" / "visuals"),
            "--out-dir",
            str(tmp_path / "public"),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "scenes must be an array" in result.output
    assert "Traceback" not in result.output


def test_prepare_visual_assets_cli_fails_on_duplicate_supported_files(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.png").write_bytes(b"image")
    (assets_dir / "scene_001.mp4").write_bytes(b"video")

    result = CliRunner().invoke(
        app,
        [
            "prepare-visual-assets",
            str(props_json),
            "--assets-dir",
            str(assets_dir),
            "--out-dir",
            str(tmp_path / "remotion" / "public"),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "multiple supported visual assets for scene_001" in result.output
    assert "Traceback" not in result.output


def test_inspect_visual_assets_cli_success_prints_stable_text_summary_and_rows(
    tmp_path,
) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    data = json.loads(props_json.read_text(encoding="utf-8"))
    data["scenes"][0]["visual"]["asset_status"] = "prepared"
    data["scenes"][0]["visual"]["public_path"] = "visuals/scene_001.png"
    props_json.write_text(json.dumps(data), encoding="utf-8")

    result = CliRunner().invoke(app, ["inspect-visual-assets", str(props_json)])

    assert result.exit_code == 0
    assert result.output == (
        f"Visual assets: {props_json}\n"
        "target_scenes: 1\n"
        "prepared: 1\n"
        "missing: 0\n"
        "unsupported: 0\n"
        "\n"
        "scene_001 AI_VIDEO prepared visuals/scene_001.png\n"
    )


def test_inspect_visual_assets_cli_json_prints_parseable_counts_and_items(
    tmp_path,
) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    data = json.loads(props_json.read_text(encoding="utf-8"))
    data["scenes"][0]["visual"]["public_path"] = "assets/scene_001.gif"
    props_json.write_text(json.dumps(data), encoding="utf-8")

    result = CliRunner().invoke(app, ["inspect-visual-assets", str(props_json), "--json"])

    assert result.exit_code == 0
    output = json.loads(result.output)
    assert output == {
        "path": str(props_json),
        "target_scenes": 1,
        "prepared": 0,
        "missing": 0,
        "unsupported": 1,
        "items": [
            {
                "scene_id": "scene_001",
                "visual_type": "AI_VIDEO",
                "status": "unsupported",
                "public_path": "assets/scene_001.gif",
            }
        ],
    }


def test_inspect_visual_assets_cli_fails_on_malformed_props(tmp_path) -> None:
    props_json = tmp_path / "props.json"
    props_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(app, ["inspect-visual-assets", str(props_json)])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "scenes must be an array" in result.output
    assert "Traceback" not in result.output


def test_inspect_visual_assets_cli_is_read_only(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    before = props_json.read_text(encoding="utf-8")

    result = CliRunner().invoke(app, ["inspect-visual-assets", str(props_json)])

    assert result.exit_code == 0
    assert props_json.read_text(encoding="utf-8") == before
