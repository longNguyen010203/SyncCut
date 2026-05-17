import json
from pathlib import Path

import pytest

from synccut.pipeline import run_pipeline_check
from synccut.preflight import PreflightIssue, PreflightSummary
from synccut.validators import SyncCutError


def write_fixture(root: Path, *, visual_suffix: str = ".png") -> tuple[Path, Path, Path, Path]:
    scenes_json = root / "scenes.json"
    audio_dir = root / "audio"
    alignment_dir = root / "alignments"
    visual_dir = root / "assets" / "visuals"
    audio_dir.mkdir(parents=True)
    alignment_dir.mkdir(parents=True)
    visual_dir.mkdir(parents=True)

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
    (audio_dir / "01_HOOK.mp3").write_bytes(b"audio")
    (alignment_dir / "01_HOOK_alignment_tmp.json").write_text(
        json.dumps(
            {
                "total_duration_sec": 2.0,
                "paragraphs": [
                    {
                        "paragraph": "Hello world.",
                        "start": 0.0,
                        "end": 2.0,
                        "sentences": [],
                    }
                ],
                "words": [],
            }
        ),
        encoding="utf-8",
    )
    (visual_dir / f"scene_001{visual_suffix}").write_bytes(b"visual")
    return scenes_json, audio_dir, alignment_dir, visual_dir


def run_fixture_pipeline(root: Path, **kwargs):
    scenes_json, audio_dir, alignment_dir, visual_dir = write_fixture(root, **kwargs.pop("fixture", {}))
    return run_pipeline_check(
        scenes_json,
        audio_dir=audio_dir,
        alignment_dir=alignment_dir,
        visual_assets_dir=visual_dir,
        timeline_out=root / "timeline.json",
        props_out=root / "remotion" / "props.json",
        public_dir=root / "remotion" / "public",
        generated_dir=root / "generated",
        **kwargs,
    )


def test_successful_pipeline_writes_ordered_report(tmp_path) -> None:
    result = run_fixture_pipeline(tmp_path)

    assert [step.name for step in result.steps] == [
        "build_timeline",
        "validate_timeline",
        "export_remotion",
        "prepare_remotion_assets",
        "visual_manifest_markdown",
        "visual_manifest_json",
        "inspect_visual_duration",
        "prepare_visual_assets",
        "inspect_visual_assets",
        "preflight",
    ]
    assert result.report_path == tmp_path / "generated" / "pipeline_check_report.json"
    assert result.summary["fail"] == 0
    assert result.summary["total"] == 10

    report = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == "0.1"
    assert report["metadata"]["generated_by"] == "synccut pipeline-check"
    assert report["metadata"]["scenes_json"] == str(tmp_path / "scenes.json")
    assert report["summary"] == result.summary
    assert report["steps"][0]["name"] == "build_timeline"
    assert report["steps"][0]["status"] == "PASS"
    assert report["next_steps"] == [
        "cd remotion",
        "npm run typecheck",
        "npm run render:smoke:local",
        "npm run render:final:local",
    ]
    assert result.report_path.read_text(encoding="utf-8").endswith("\n")


def test_skip_visual_duration_records_skip_and_does_not_call_duration(tmp_path, monkeypatch) -> None:
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("visual duration should be skipped")

    monkeypatch.setattr("synccut.pipeline.write_visual_duration_report_file", fail_if_called)

    result = run_fixture_pipeline(tmp_path, skip_visual_duration=True)

    duration_step = next(step for step in result.steps if step.name == "inspect_visual_duration")
    assert duration_step.status == "SKIP"
    assert "skipped by option" in duration_step.message


def test_missing_ffprobe_records_warning_and_continues(tmp_path, monkeypatch) -> None:
    def missing_ffprobe(*_args, **_kwargs):
        raise SyncCutError("ffprobe executable not found; pass --ffprobe-bin")

    monkeypatch.setattr("synccut.pipeline.write_visual_duration_report_file", missing_ffprobe)

    result = run_fixture_pipeline(tmp_path)

    duration_step = next(step for step in result.steps if step.name == "inspect_visual_duration")
    assert duration_step.status == "WARN"
    assert "ffprobe" in duration_step.message
    assert result.summary["fail"] == 0
    assert result.steps[-1].name == "preflight"


def test_no_prepare_visual_assets_skips_prep_and_allows_warning_preflight(tmp_path) -> None:
    result = run_fixture_pipeline(tmp_path, prepare_visual_assets=False)

    prep_step = next(step for step in result.steps if step.name == "prepare_visual_assets")
    preflight_step = next(step for step in result.steps if step.name == "preflight")

    assert prep_step.status == "SKIP"
    assert preflight_step.status == "WARN"
    assert preflight_step.counts["visual_missing"] == 1


def test_preflight_failure_raises_clear_error_and_writes_failure_report(tmp_path, monkeypatch) -> None:
    def failing_preflight(props_path: Path, *, verify_files: bool, public_dir: Path):
        return PreflightSummary(
            props_path=props_path,
            status="error",
            scenes=1,
            sections=1,
            duration_sec=2.0,
            duration_frames=60,
            fps=30,
            audio_prepared=0,
            audio_missing_public_path=1,
            visual_target_scenes=0,
            visual_prepared=0,
            visual_missing=0,
            visual_unsupported=0,
            warnings=[],
            errors=[
                PreflightIssue(
                    level="error",
                    code="missing_audio_public_path",
                    message="sections[0].audio.public_path must be a non-empty string",
                )
            ],
            verify_files=verify_files,
            public_dir=public_dir,
            file_errors=0,
        )

    monkeypatch.setattr("synccut.pipeline.inspect_preflight_file", failing_preflight)

    with pytest.raises(SyncCutError, match="preflight failed"):
        run_fixture_pipeline(tmp_path)

    report = json.loads((tmp_path / "generated" / "pipeline_check_report.json").read_text())
    assert report["summary"]["fail"] == 1
    assert report["steps"][-1]["status"] == "FAIL"
    assert "preflight failed" in report["steps"][-1]["message"]


def test_pipeline_does_not_call_provider_downloader_or_render_functions(tmp_path, monkeypatch) -> None:
    import synccut.audio_generation
    import synccut.broll_downloader

    monkeypatch.setattr(
        synccut.audio_generation,
        "generate_audio_from_manifest",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("provider called")),
    )
    monkeypatch.setattr(
        synccut.broll_downloader,
        "download_broll_from_manifest",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("downloader called")),
    )

    result = run_fixture_pipeline(tmp_path)

    assert result.summary["fail"] == 0
