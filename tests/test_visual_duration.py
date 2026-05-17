import json
from pathlib import Path

import pytest

from synccut.validators import SyncCutError
from synccut.visual_duration import (
    VisualDurationProbe,
    build_visual_duration_report,
    format_visual_duration_report,
    format_visual_duration_report_markdown,
    visual_duration_report_to_dict,
    write_visual_duration_report_file,
)


def write_asset(path: Path, content: bytes = b"asset") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def valid_props() -> dict:
    return {
        "metadata": {"generated_by": "synccut export-remotion"},
        "scenes": [
            {
                "id": "scene_001",
                "scene_order": 1,
                "section": "HOOK",
                "section_key": "01_HOOK",
                "duration_sec": 5.0,
                "duration_frames": 150,
                "visual_type": "AI_VIDEO",
                "visual": {"type": "AI_VIDEO", "prompt": "Video"},
            },
            {
                "id": "scene_002",
                "scene_order": 2,
                "section": "HOOK",
                "section_key": "01_HOOK",
                "duration_sec": 4.0,
                "duration_frames": 120,
                "visual_type": "TABLE",
                "visual": {"type": "TABLE", "prompt": "Table"},
            },
            {
                "id": "scene_003",
                "scene_order": 3,
                "section": "BODY",
                "section_key": "02_BODY",
                "duration_sec": 3.0,
                "duration_frames": 90,
                "visual_type": "B_ROLL",
                "visual": {"type": "B_ROLL", "prompt": "B-roll"},
            },
        ],
    }


def write_props(path: Path, props: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(props if props is not None else valid_props()), encoding="utf-8")
    return path


def build_report(tmp_path: Path, *, probe=None, props: dict | None = None):
    return build_visual_duration_report(
        props if props is not None else valid_props(),
        tmp_path / "remotion" / "props.json",
        assets_dir=tmp_path / "assets" / "visuals",
        probe_runner=probe,
    )


def probe(duration: float, *, width: int = 1920, height: int = 1080, codec: str = "h264"):
    def runner(_path: Path, _ffprobe_bin: str, _timeout: int) -> VisualDurationProbe:
        return VisualDurationProbe(duration_sec=duration, width=width, height=height, codec=codec)

    return runner


def test_targets_only_ai_video_and_b_roll_and_preserves_order(tmp_path) -> None:
    report = build_report(tmp_path)

    assert [scene.scene_id for scene in report.scenes] == ["scene_001", "scene_003"]
    assert [scene.visual_type for scene in report.scenes] == ["AI_VIDEO", "B_ROLL"]


def test_missing_local_file_becomes_missing(tmp_path) -> None:
    report = build_report(tmp_path)

    assert report.scenes[0].status == "missing"
    assert report.scenes[0].asset_path is None
    assert report.summary.missing == 2


def test_unsupported_only_same_stem_file_becomes_unsupported(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.txt")

    report = build_report(tmp_path)

    assert report.scenes[0].status == "unsupported"
    assert report.summary.unsupported == 1


def test_duplicate_supported_files_become_duplicate_supported(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")

    report = build_report(tmp_path)

    assert report.scenes[0].status == "duplicate_supported"
    assert report.summary.duplicate_supported == 1


def test_image_file_is_image_ok_and_does_not_probe(tmp_path) -> None:
    calls: list[Path] = []
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")

    def failing_probe(path: Path, _ffprobe_bin: str, _timeout: int) -> VisualDurationProbe:
        calls.append(path)
        raise AssertionError("image should not be probed")

    report = build_report(tmp_path, probe=failing_probe)

    assert calls == []
    assert report.scenes[0].status == "image_ok"
    assert report.scenes[0].asset_kind == "image"
    assert report.scenes[0].asset_duration_sec is None
    assert report.scenes[0].notes == "Image asset is duration-independent."


def test_video_near_scene_duration_is_video_ok(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(5.1))

    scene = report.scenes[0]
    assert scene.status == "video_ok"
    assert scene.warnings == []
    assert scene.asset_duration_sec == 5.1
    assert scene.width == 1920
    assert scene.height == 1080
    assert scene.aspect_ratio == 1.7778
    assert scene.codec == "h264"


def test_video_shorter_reports_loops_warning(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(3.0))

    scene = report.scenes[0]
    assert scene.status == "video_short_loops"
    assert scene.warnings == ["loops"]
    assert scene.loops_needed == 1.6667


def test_video_very_short_reports_repetitive_warning(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(1.0))

    scene = report.scenes[0]
    assert scene.status == "video_very_short_repetitive"
    assert scene.warnings == ["loops", "repetitive_loop"]
    assert scene.loops_needed == 5.0


def test_video_longer_reports_trimmed_warning(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(8.0))

    scene = report.scenes[0]
    assert scene.status == "video_long_trimmed"
    assert scene.warnings == ["trimmed"]


def test_aspect_ratio_outside_threshold_adds_warning_without_replacing_status(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(5.0, width=1080, height=1920))

    scene = report.scenes[0]
    assert scene.status == "video_ok"
    assert scene.warnings == ["aspect_ratio_warning"]
    assert report.summary.aspect_ratio_warning == 1


def test_unreadable_probe_result_becomes_unreadable(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=lambda *_args: None)

    scene = report.scenes[0]
    assert scene.status == "unreadable"
    assert scene.warnings == ["unreadable_metadata"]
    assert report.summary.unreadable == 1


def test_zero_duration_probe_result_becomes_unreadable(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, probe=probe(0.0))

    scene = report.scenes[0]
    assert scene.status == "unreadable"
    assert scene.warnings == ["unreadable_metadata"]


def test_invalid_scene_duration_becomes_unreadable_without_probe(tmp_path) -> None:
    props = valid_props()
    del props["scenes"][0]["duration_sec"]
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")

    report = build_report(tmp_path, props=props, probe=probe(5.0))

    assert report.scenes[0].status == "unreadable"
    assert "unreadable_metadata" in report.scenes[0].warnings
    assert "missing_scene_duration" in report.scenes[0].notes


def test_missing_ffprobe_error_occurs_only_for_video_probe(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")
    image_report = build_report(
        tmp_path,
        probe=lambda *_args: (_ for _ in ()).throw(SyncCutError("ffprobe should not run")),
    )
    assert image_report.scenes[0].status == "image_ok"

    (tmp_path / "assets" / "visuals" / "scene_001.png").unlink()
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")
    with pytest.raises(SyncCutError, match="--ffprobe-bin"):
        build_report(
            tmp_path,
            probe=lambda *_args: (_ for _ in ()).throw(
                SyncCutError("ffprobe executable not found; pass --ffprobe-bin")
            ),
        )


def test_json_is_deterministic_and_parseable(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")
    report = build_visual_duration_report(
        valid_props(),
        tmp_path / "remotion" / "props.json",
        assets_dir=tmp_path / "assets" / "visuals",
        output_format="json",
        probe_runner=probe(5.0),
    )

    encoded = format_visual_duration_report(report)
    parsed = json.loads(encoded)

    assert encoded.endswith("\n")
    assert parsed["schema_version"] == "0.1"
    assert parsed["metadata"]["generated_by"] == "synccut inspect-visual-duration"
    assert parsed["summary"]["target_scenes"] == 2
    assert parsed["summary"]["video_ok"] == 1
    assert parsed["scenes"][0]["scene_id"] == "scene_001"
    assert parsed == visual_duration_report_to_dict(report)


def test_markdown_includes_title_summary_and_table(tmp_path) -> None:
    report = build_report(tmp_path)

    output = format_visual_duration_report_markdown(report)

    assert output.startswith("# Visual Duration Report\n")
    assert "## Summary" in output
    assert "- target_scenes: 2" in output
    assert "| scene_id | section_key | visual_type | scene_sec | asset | kind |" in output
    assert "| scene_001 | 01_HOOK | AI_VIDEO | 5 | - | - |" in output


def test_identical_report_reuses_existing_file(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_duration_report.md"

    assets_dir = tmp_path / "assets" / "visuals"
    first = write_visual_duration_report_file(props_path, assets_dir=assets_dir, out_path=out_path)
    second = write_visual_duration_report_file(props_path, assets_dir=assets_dir, out_path=out_path)

    assert first.status == "written"
    assert second.status == "reused"


def test_differing_report_blocks_and_mentions_overwrite(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_duration_report.md"
    out_path.parent.mkdir(parents=True)
    out_path.write_text("changed\n", encoding="utf-8")

    with pytest.raises(SyncCutError, match="--overwrite"):
        write_visual_duration_report_file(
            props_path,
            assets_dir=tmp_path / "assets" / "visuals",
            out_path=out_path,
        )


def test_overwrite_replaces_requested_report(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_duration_report.md"
    other_path = tmp_path / "generated" / "other.md"
    out_path.parent.mkdir(parents=True)
    out_path.write_text("changed\n", encoding="utf-8")
    other_path.write_text("keep\n", encoding="utf-8")

    result = write_visual_duration_report_file(
        props_path,
        assets_dir=tmp_path / "assets" / "visuals",
        out_path=out_path,
        overwrite=True,
    )

    assert result.status == "written"
    assert out_path.read_text(encoding="utf-8").startswith("# Visual Duration Report")
    assert other_path.read_text(encoding="utf-8") == "keep\n"
