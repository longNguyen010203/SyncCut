import json
from pathlib import Path

from typer.testing import CliRunner

from synccut.audio_generation import AudioGenerationResult, AudioGenerationSectionResult
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


def write_tiny_narration_manifest(root: Path) -> Path:
    manifest_path = root / "generated" / "narration" / "narration_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "metadata": {
                    "schema_version": "0.1",
                    "generated_by": "synccut prepare-narration",
                    "source_scenes": "scenes.json",
                    "total_sections": 1,
                    "total_scenes": 1,
                },
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "section": "HOOK",
                        "section_order": 1,
                        "scene_ids": ["scene_001"],
                        "scene_count": 1,
                        "text_path": "01_HOOK.txt",
                        "narration_text": "Hello world.",
                        "text_hash": "sha256:" + "1" * 64,
                        "expected_audio_path": "01_HOOK.mp3",
                        "expected_alignment_path": "01_HOOK_alignment_tmp.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return manifest_path


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


def write_tiny_preflight_props(root: Path) -> Path:
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
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "section": "HOOK",
                        "section_order": 1,
                        "start_frame": 0,
                        "end_frame": 60,
                        "duration_frames": 60,
                        "audio": {
                            "path": "examples/audio/01_HOOK.mp3",
                            "public_path": "audio/01_HOOK.mp3",
                        },
                    }
                ],
                "scenes": [
                    {
                        "id": "scene_001",
                        "scene_order": 1,
                        "section_key": "01_HOOK",
                        "start_frame": 0,
                        "end_frame": 30,
                        "duration_frames": 30,
                        "visual_type": "AI_VIDEO",
                        "visual": {"type": "AI_VIDEO", "prompt": "Prompt", "data": None},
                        "dialogue": {"text": "Hello.", "paragraphs": ["Hello."]},
                        "audio": {"path": "examples/audio/01_HOOK.mp3"},
                    },
                    {
                        "id": "scene_002",
                        "scene_order": 2,
                        "section_key": "01_HOOK",
                        "start_frame": 30,
                        "end_frame": 60,
                        "duration_frames": 30,
                        "visual_type": "TABLE",
                        "visual": {"type": "TABLE", "prompt": "Table", "data": {"rows": []}},
                        "dialogue": {"text": "Table.", "paragraphs": ["Table."]},
                        "audio": {"path": "examples/audio/01_HOOK.mp3"},
                    },
                ],
                "assets": {
                    "audio": [
                        {
                            "section_key": "01_HOOK",
                            "path": "examples/audio/01_HOOK.mp3",
                            "public_path": "audio/01_HOOK.mp3",
                        }
                    ],
                    "visuals": [],
                },
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    return props_json


def write_preflight_public_audio(root: Path) -> Path:
    public_dir = root / "remotion" / "public"
    audio_path = public_dir / "audio" / "01_HOOK.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(b"audio")
    return public_dir


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
    assert f"Built timeline {out}" in result.output
    assert "sections: 1" in result.output
    assert "scenes: 1" in result.output
    assert "duration_sec: 2.0" in result.output
    assert "warnings: 0" in result.output
    assert f"Next: synccut validate-timeline {out}" in result.output
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


def test_cli_help_clarifies_asset_preparation_and_preflight_options() -> None:
    runner = CliRunner()

    audio_help = runner.invoke(app, ["prepare-remotion-assets", "--help"])
    assert audio_help.exit_code == 0
    assert "audio assets" in audio_help.output

    visual_help = runner.invoke(app, ["prepare-visual-assets", "--help"])
    assert visual_help.exit_code == 0
    assert "assets/visuals/<scene_id>.<ext>" in visual_help.output
    assert "supported file per target scene" in visual_help.output

    preflight_help = runner.invoke(app, ["preflight", "--help"])
    assert preflight_help.exit_code == 0
    assert "Verify prepared public audio/visual files exist" in preflight_help.output
    assert "requires --public-dir" in preflight_help.output


def test_prepare_narration_cli_succeeds_and_prints_summary(tmp_path) -> None:
    scenes_json, _, _ = write_tiny_fixture(tmp_path)
    out_dir = tmp_path / "generated" / "narration"

    result = CliRunner().invoke(
        app,
        ["prepare-narration", str(scenes_json), "--out-dir", str(out_dir)],
    )

    assert result.exit_code == 0
    assert (out_dir / "narration_manifest.json").exists()
    assert (out_dir / "01_HOOK.txt").read_text(encoding="utf-8") == "Hello world.\n"
    assert f"Prepared narration package {out_dir}" in result.output
    assert "sections: 1" in result.output
    assert "scenes: 1" in result.output
    assert "written: 2" in result.output
    assert "reused: 0" in result.output
    assert f"manifest: {out_dir / 'narration_manifest.json'}" in result.output
    assert "Next: provide this narration package to an audio/alignment provider" in result.output


def test_prepare_narration_cli_dry_run_writes_nothing(tmp_path) -> None:
    scenes_json, _, _ = write_tiny_fixture(tmp_path)
    out_dir = tmp_path / "generated" / "narration"

    result = CliRunner().invoke(
        app,
        ["prepare-narration", str(scenes_json), "--out-dir", str(out_dir), "--dry-run"],
    )

    assert result.exit_code == 0
    assert not out_dir.exists()
    assert f"Dry run: narration package {out_dir}" in result.output
    assert "sections: 1" in result.output
    assert "scenes: 1" in result.output
    assert "would_create: 2" in result.output
    assert "would_reuse: 0" in result.output
    assert "would_block: 0" in result.output


def test_prepare_narration_cli_blocks_different_existing_file(tmp_path) -> None:
    scenes_json, _, _ = write_tiny_fixture(tmp_path)
    out_dir = tmp_path / "generated" / "narration"

    first = CliRunner().invoke(
        app,
        ["prepare-narration", str(scenes_json), "--out-dir", str(out_dir)],
    )
    assert first.exit_code == 0
    (out_dir / "01_HOOK.txt").write_text("changed\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        ["prepare-narration", str(scenes_json), "--out-dir", str(out_dir)],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "output exists and differs" in result.output
    assert "--overwrite" in result.output
    assert "Traceback" not in result.output


def test_generate_audio_cli_dry_run_output_writes_nothing(tmp_path) -> None:
    manifest_path = write_tiny_narration_manifest(tmp_path)
    audio_dir = tmp_path / "generated" / "audio"
    alignment_dir = tmp_path / "generated" / "alignments"

    result = CliRunner().invoke(
        app,
        [
            "generate-audio",
            str(manifest_path),
            "--provider",
            "elevenlabs",
            "--audio-dir",
            str(audio_dir),
            "--alignment-dir",
            str(alignment_dir),
            "--voice-id",
            "voice",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert not audio_dir.exists()
    assert not alignment_dir.exists()
    assert f"Dry run: audio generation {manifest_path}" in result.output
    assert "provider: elevenlabs" in result.output
    assert "sections: 1" in result.output
    assert "would_generate: 1" in result.output
    assert "would_reuse: 0" in result.output
    assert "would_block: 0" in result.output
    assert f"audio_dir: {audio_dir}" in result.output
    assert f"alignment_dir: {alignment_dir}" in result.output


def test_generate_audio_cli_success_output_uses_orchestration_result(
    tmp_path, monkeypatch
) -> None:
    manifest_path = write_tiny_narration_manifest(tmp_path)
    audio_dir = tmp_path / "generated" / "audio"
    alignment_dir = tmp_path / "generated" / "alignments"
    metadata_path = tmp_path / "generated" / "audio_generation_manifest.json"

    def fake_generate_audio_from_manifest(*_args, **_kwargs) -> AudioGenerationResult:
        return AudioGenerationResult(
            provider="elevenlabs",
            sections=[
                AudioGenerationSectionResult(
                    section_key="01_HOOK",
                    status="written",
                    audio_path=audio_dir / "01_HOOK.mp3",
                    alignment_path=alignment_dir / "01_HOOK_alignment_tmp.json",
                    text_hash="sha256:" + "1" * 64,
                )
            ],
            metadata_path=metadata_path,
            dry_run=False,
            written=1,
            reused=0,
            blocked=0,
        )

    monkeypatch.setattr(
        "synccut.cli.generate_audio_from_manifest",
        fake_generate_audio_from_manifest,
    )

    result = CliRunner().invoke(
        app,
        [
            "generate-audio",
            str(manifest_path),
            "--provider",
            "elevenlabs",
            "--audio-dir",
            str(audio_dir),
            "--alignment-dir",
            str(alignment_dir),
            "--voice-id",
            "voice",
            "--metadata-out",
            str(metadata_path),
        ],
    )

    assert result.exit_code == 0
    assert f"Generated audio and alignment {manifest_path}" in result.output
    assert "provider: elevenlabs" in result.output
    assert "sections: 1" in result.output
    assert "written: 1" in result.output
    assert "reused: 0" in result.output
    assert "blocked: 0" in result.output
    assert f"metadata: {metadata_path}" in result.output
    assert (
        f"--audio-dir {audio_dir} --alignment-dir {alignment_dir} --out timeline.json"
        in result.output
    )


def test_generate_audio_cli_missing_api_key_mentions_env_var(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    manifest_path = write_tiny_narration_manifest(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "generate-audio",
            str(manifest_path),
            "--provider",
            "elevenlabs",
            "--audio-dir",
            str(tmp_path / "audio"),
            "--alignment-dir",
            str(tmp_path / "alignments"),
            "--voice-id",
            "voice",
            "--limit",
            "1",
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "ELEVENLABS_API_KEY" in result.output
    assert "Traceback" not in result.output


def test_generate_audio_cli_conflict_mentions_overwrite(tmp_path) -> None:
    manifest_path = write_tiny_narration_manifest(tmp_path)
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    (audio_dir / "01_HOOK.mp3").write_bytes(b"existing")

    result = CliRunner().invoke(
        app,
        [
            "generate-audio",
            str(manifest_path),
            "--provider",
            "elevenlabs",
            "--audio-dir",
            str(audio_dir),
            "--alignment-dir",
            str(tmp_path / "alignments"),
            "--voice-id",
            "voice",
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "--overwrite" in result.output
    assert "Traceback" not in result.output


def test_generate_audio_cli_invalid_provider_exits_nonzero(tmp_path) -> None:
    manifest_path = write_tiny_narration_manifest(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "generate-audio",
            str(manifest_path),
            "--provider",
            "other",
            "--audio-dir",
            str(tmp_path / "audio"),
            "--alignment-dir",
            str(tmp_path / "alignments"),
            "--voice-id",
            "voice",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "unsupported audio provider" in result.output
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
    assert (
        f"Next: synccut export-remotion {timeline_json} --out remotion/props.json"
        in result.output
    )


def test_validate_timeline_cli_prints_warnings_but_exits_zero(tmp_path) -> None:
    timeline_json = write_timeline_with_gap_warning(tmp_path)

    result = CliRunner().invoke(app, ["validate-timeline", str(timeline_json)])

    assert result.exit_code == 0
    assert "warnings: 1" in result.output
    assert "Warning:" in result.output
    assert "gap of 2.000s" in result.output
    assert (
        f"Next: synccut export-remotion {timeline_json} --out remotion/props.json"
        in result.output
    )


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
    assert f"Next: synccut prepare-remotion-assets {out} --out-dir remotion/public" in result.output
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
    assert (
        f"Next: synccut preflight {props_json} --verify-files --public-dir remotion/public"
        in result.output
    )


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


def test_visual_manifest_cli_markdown_success_output(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    out_path = tmp_path / "generated" / "visual_manifest.md"

    result = CliRunner().invoke(
        app,
        [
            "visual-manifest",
            str(props_json),
            "--assets-dir",
            str(tmp_path / "assets" / "visuals"),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 0
    assert out_path.read_text(encoding="utf-8").startswith("# Visual Asset Manifest\n")
    assert f"Visual manifest {out_path}" in result.output
    assert "format: markdown" in result.output
    assert "target_scenes: 1" in result.output
    assert "prepared: 0" in result.output
    assert "missing: 1" in result.output
    assert "unsupported: 0" in result.output
    assert "local_found: 0" in result.output
    assert "local_missing: 1" in result.output
    assert "Next: add visual files under assets/visuals/<scene_id>.<ext>" in result.output


def test_visual_manifest_cli_json_success_output(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.png").write_bytes(b"image")
    out_path = tmp_path / "generated" / "visual_manifest.json"

    result = CliRunner().invoke(
        app,
        [
            "visual-manifest",
            str(props_json),
            "--assets-dir",
            str(assets_dir),
            "--out",
            str(out_path),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["schema_version"] == "0.1"
    assert output["summary"]["target_scenes"] == 1
    assert output["summary"]["local_found"] == 1
    assert output["scenes"][0]["local_asset_status"] == "found"
    assert f"Visual manifest {out_path}" in result.output
    assert "format: json" in result.output
    assert "local_found: 1" in result.output


def test_visual_manifest_cli_dry_run_writes_nothing(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    out_path = tmp_path / "generated" / "visual_manifest.md"

    result = CliRunner().invoke(
        app,
        [
            "visual-manifest",
            str(props_json),
            "--out",
            str(out_path),
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert not out_path.exists()
    assert not out_path.parent.exists()
    assert f"Dry run: visual manifest {out_path}" in result.output
    assert "status: would_create" in result.output
    assert "target_scenes: 1" in result.output


def test_visual_manifest_cli_conflict_output_mentions_overwrite(tmp_path) -> None:
    props_json = write_tiny_visual_props(tmp_path)
    out_path = tmp_path / "generated" / "visual_manifest.md"
    out_path.parent.mkdir(parents=True)
    out_path.write_text("changed\n", encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "visual-manifest",
            str(props_json),
            "--out",
            str(out_path),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "--overwrite" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_warning_status_exits_zero_and_prints_stable_text(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)

    result = CliRunner().invoke(app, ["preflight", str(props_json)])

    assert result.exit_code == 0
    assert result.output == (
        f"Preflight: {props_json}\n"
        "status: warning\n"
        "scenes: 2\n"
        "sections: 1\n"
        "duration_sec: 2.0\n"
        "duration_frames: 60\n"
        "fps: 30\n"
        "audio_prepared: 1\n"
        "audio_missing_public_path: 0\n"
        "visual_target_scenes: 1\n"
        "visual_prepared: 0\n"
        "visual_missing: 1\n"
        "visual_unsupported: 0\n"
        "warnings: 1\n"
        "errors: 0\n"
        "\n"
        "Note: Missing AI_VIDEO/B_ROLL visuals are warning-only; Remotion will render "
        "placeholders unless visual assets are prepared.\n"
        "\n"
        "Warnings:\n"
        "warning visual_missing scene_001 AI_VIDEO missing visual asset; placeholder will render\n"
        "\n"
        "Errors:\n"
        "none\n"
    )


def test_preflight_cli_json_exits_zero_and_prints_parseable_json(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)

    result = CliRunner().invoke(app, ["preflight", str(props_json), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["path"] == str(props_json)
    assert data["status"] == "warning"
    assert data["scenes"] == 2
    assert data["sections"] == 1
    assert data["audio_prepared"] == 1
    assert data["visual_missing"] == 1
    assert data["warnings"] == [
        {
            "level": "warning",
            "code": "visual_missing",
            "message": "scene_001 AI_VIDEO missing visual asset; placeholder will render",
        }
    ]
    assert data["errors"] == []
    assert "verify_files" not in data
    assert "public_dir" not in data
    assert "file_errors" not in data


def test_preflight_cli_verify_files_exits_zero_and_prints_file_fields(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    public_dir = write_preflight_public_audio(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "preflight",
            str(props_json),
            "--verify-files",
            "--public-dir",
            str(public_dir),
        ],
    )

    assert result.exit_code == 0
    assert f"Preflight: {props_json}" in result.output
    assert "status: warning" in result.output
    assert "verify_files: true" in result.output
    assert f"public_dir: {public_dir}" in result.output
    assert "file_errors: 0" in result.output
    assert "Missing AI_VIDEO/B_ROLL visuals are warning-only" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_verify_files_json_exits_zero_and_prints_file_fields(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    public_dir = write_preflight_public_audio(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "preflight",
            str(props_json),
            "--verify-files",
            "--public-dir",
            str(public_dir),
            "--json",
        ],
    )

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] == "warning"
    assert data["verify_files"] is True
    assert data["public_dir"] == str(public_dir)
    assert data["file_errors"] == 0


def test_preflight_cli_verify_files_missing_file_exits_nonzero_after_report(
    tmp_path,
) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    public_dir = tmp_path / "remotion" / "public"

    result = CliRunner().invoke(
        app,
        [
            "preflight",
            str(props_json),
            "--verify-files",
            "--public-dir",
            str(public_dir),
        ],
    )

    assert result.exit_code == 1
    assert f"Preflight: {props_json}" in result.output
    assert "status: error" in result.output
    assert "file_errors: 2" in result.output
    assert "error missing_public_file sections[0].audio public_path audio/01_HOOK.mp3" in result.output
    assert "error missing_public_file assets.audio[0] public_path audio/01_HOOK.mp3" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_verify_files_without_public_dir_fails_without_traceback(
    tmp_path,
) -> None:
    props_json = write_tiny_preflight_props(tmp_path)

    result = CliRunner().invoke(app, ["preflight", str(props_json), "--verify-files"])

    assert result.exit_code == 1
    assert "Error: --public-dir is required when --verify-files is set" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_public_dir_without_verify_files_fails_without_traceback(
    tmp_path,
) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    public_dir = tmp_path / "remotion" / "public"

    result = CliRunner().invoke(
        app,
        ["preflight", str(props_json), "--public-dir", str(public_dir)],
    )

    assert result.exit_code == 1
    assert "Error: --public-dir can only be used with --verify-files" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_error_status_exits_nonzero_after_printing_report(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    data = json.loads(props_json.read_text(encoding="utf-8"))
    del data["sections"][0]["audio"]["public_path"]
    props_json.write_text(json.dumps(data), encoding="utf-8")

    result = CliRunner().invoke(app, ["preflight", str(props_json)])

    assert result.exit_code == 1
    assert f"Preflight: {props_json}" in result.output
    assert "status: error" in result.output
    assert "audio_missing_public_path: 1" in result.output
    assert (
        "error missing_audio_public_path "
        "sections[0].audio.public_path must be a non-empty string"
    ) in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_malformed_props_returns_error_without_traceback(tmp_path) -> None:
    props_json = tmp_path / "props.json"
    props_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(app, ["preflight", str(props_json)])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "scenes must be an array" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_verify_files_malformed_props_returns_error_without_traceback(
    tmp_path,
) -> None:
    props_json = tmp_path / "props.json"
    props_json.write_text(json.dumps({"metadata": {}}), encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "preflight",
            str(props_json),
            "--verify-files",
            "--public-dir",
            str(tmp_path / "public"),
        ],
    )

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "scenes must be an array" in result.output
    assert "Traceback" not in result.output


def test_preflight_cli_read_only(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    original = props_json.read_text(encoding="utf-8")

    result = CliRunner().invoke(app, ["preflight", str(props_json)])

    assert result.exit_code == 0
    assert props_json.read_text(encoding="utf-8") == original


def test_preflight_cli_verify_files_read_only(tmp_path) -> None:
    props_json = write_tiny_preflight_props(tmp_path)
    public_dir = write_preflight_public_audio(tmp_path)
    original = props_json.read_text(encoding="utf-8")

    result = CliRunner().invoke(
        app,
        [
            "preflight",
            str(props_json),
            "--verify-files",
            "--public-dir",
            str(public_dir),
        ],
    )

    assert result.exit_code == 0
    assert props_json.read_text(encoding="utf-8") == original
