import json
from copy import deepcopy
from pathlib import Path

import pytest

from synccut.preflight import (
    format_preflight,
    inspect_preflight,
    inspect_preflight_file,
    preflight_to_dict,
)
from synccut.validators import SyncCutError


def valid_props() -> dict:
    return {
        "metadata": {
            "generated_by": "synccut export-remotion",
            "source_timeline": "timeline.json",
            "fps": 30,
            "duration_sec": 4.0,
            "duration_frames": 120,
            "total_scenes": 3,
            "total_sections": 2,
        },
        "composition": {
            "id": "SyncCutVideo",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration_frames": 120,
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
            },
            {
                "section_key": "02_BODY",
                "section": "BODY",
                "section_order": 2,
                "start_frame": 60,
                "end_frame": 120,
                "duration_frames": 60,
                "audio": {
                    "path": "examples/audio/02_BODY.mp3",
                    "public_path": "audio/02_BODY.mp3",
                },
            },
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
                "visual_type": "B_ROLL",
                "visual": {"type": "B_ROLL", "prompt": "B-roll", "data": None},
                "dialogue": {"text": "World.", "paragraphs": ["World."]},
                "audio": {"path": "examples/audio/01_HOOK.mp3"},
            },
            {
                "id": "scene_003",
                "scene_order": 3,
                "section_key": "02_BODY",
                "start_frame": 60,
                "end_frame": 120,
                "duration_frames": 60,
                "visual_type": "CHART",
                "visual": {"type": "CHART", "prompt": "Chart", "data": {"x": 1}},
                "dialogue": {"text": "Chart.", "paragraphs": ["Chart."]},
                "audio": {"path": "examples/audio/02_BODY.mp3"},
            },
        ],
        "assets": {
            "audio": [
                {
                    "section_key": "01_HOOK",
                    "path": "examples/audio/01_HOOK.mp3",
                    "public_path": "audio/01_HOOK.mp3",
                },
                {
                    "section_key": "02_BODY",
                    "path": "examples/audio/02_BODY.mp3",
                    "public_path": "audio/02_BODY.mp3",
                },
            ],
            "visuals": [],
        },
        "warnings": [],
    }


def preflight(props: dict, tmp_path: Path):
    return inspect_preflight(props, tmp_path / "remotion" / "props.json")


def write_public_file(public_dir: Path, public_path: str, content: bytes = b"asset") -> Path:
    target = public_dir / public_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return target


def write_default_audio_files(public_dir: Path) -> None:
    write_public_file(public_dir, "audio/01_HOOK.mp3")
    write_public_file(public_dir, "audio/02_BODY.mp3")


def verified_preflight(props: dict, tmp_path: Path, public_dir: Path):
    return inspect_preflight(
        props,
        tmp_path / "remotion" / "props.json",
        verify_files=True,
        public_dir=public_dir,
    )


def issue_codes(summary) -> tuple[list[str], list[str]]:
    return [issue.code for issue in summary.warnings], [issue.code for issue in summary.errors]


def test_prepared_audio_with_missing_visual_assets_reports_warning_no_errors(tmp_path) -> None:
    summary = preflight(valid_props(), tmp_path)

    assert summary.status == "warning"
    assert summary.audio_prepared == 2
    assert summary.audio_missing_public_path == 0
    assert summary.visual_target_scenes == 2
    assert summary.visual_prepared == 0
    assert summary.visual_missing == 2
    assert summary.visual_unsupported == 0
    assert [issue.code for issue in summary.warnings] == ["visual_missing", "visual_missing"]
    assert summary.errors == []


def test_prepared_section_audio_counted_by_section(tmp_path) -> None:
    props = valid_props()
    props["sections"].append(
        {
            "section_key": "03_END",
            "start_frame": 120,
            "end_frame": 150,
            "duration_frames": 30,
            "audio": {"path": "examples/audio/03_END.mp3", "public_path": "audio/03_END.mp3"},
        }
    )
    props["composition"]["duration_frames"] = 150
    props["metadata"]["duration_frames"] = 150
    props["metadata"]["duration_sec"] = 5.0
    props["metadata"]["total_sections"] = 3
    props["assets"]["audio"].append(
        {
            "section_key": "03_END",
            "path": "examples/audio/03_END.mp3",
            "public_path": "audio/03_END.mp3",
        }
    )

    summary = preflight(props, tmp_path)

    assert summary.audio_prepared == 3
    assert summary.audio_missing_public_path == 0


def test_missing_section_audio_public_path_is_error(tmp_path) -> None:
    props = valid_props()
    del props["sections"][0]["audio"]["public_path"]

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert summary.audio_prepared == 1
    assert summary.audio_missing_public_path == 1
    assert "missing_audio_public_path" in [issue.code for issue in summary.errors]
    assert summary.errors[0].message == "sections[0].audio.public_path must be a non-empty string"


def test_missing_root_audio_public_path_is_error(tmp_path) -> None:
    props = valid_props()
    del props["assets"]["audio"][0]["public_path"]

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert summary.audio_missing_public_path == 1
    assert any(
        issue.message == "assets.audio[0].public_path must be a non-empty string"
        for issue in summary.errors
    )


def test_scene_audio_may_remain_path_only_when_section_audio_is_prepared(tmp_path) -> None:
    props = valid_props()
    for scene in props["scenes"]:
        scene["audio"] = {"path": scene["audio"]["path"]}

    summary = preflight(props, tmp_path)

    assert summary.status == "warning"
    assert not any(issue.code == "missing_audio_public_path" for issue in summary.errors)


def test_missing_ai_and_b_roll_visual_assets_are_warnings(tmp_path) -> None:
    summary = preflight(valid_props(), tmp_path)

    assert [issue.message for issue in summary.warnings] == [
        "scene_001 AI_VIDEO missing visual asset; placeholder will render",
        "scene_002 B_ROLL missing visual asset; placeholder will render",
    ]


def test_prepared_visual_assets_produce_no_visual_warning(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "visuals/scene_001.png"
    props["scenes"][1]["visual"]["asset_status"] = "prepared"
    props["scenes"][1]["visual"]["public_path"] = "visuals/scene_002.mp4"

    summary = preflight(props, tmp_path)

    assert summary.status == "ok"
    assert summary.visual_prepared == 2
    assert summary.visual_missing == 0
    assert summary.warnings == []
    assert summary.errors == []


def test_unsupported_visual_public_paths_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "assets/scene_001.gif"

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert summary.visual_unsupported == 1
    assert any(
        issue.code == "visual_unsupported"
        and issue.message == "scene_001 AI_VIDEO unsupported visual asset path assets/scene_001.gif"
        for issue in summary.errors
    )


def test_root_props_warnings_carried_as_warnings_first(tmp_path) -> None:
    props = valid_props()
    props["warnings"] = ["section gap"]

    summary = preflight(props, tmp_path)

    assert summary.warnings[0].code == "props_warning"
    assert summary.warnings[0].message == "section gap"
    assert summary.warnings[1].code == "visual_missing"


def test_missing_or_malformed_composition_produces_errors(tmp_path) -> None:
    props = valid_props()
    props["composition"] = "bad"

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert "invalid_composition" in [issue.code for issue in summary.errors]


def test_non_positive_fps_and_duration_frames_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["composition"]["fps"] = 0
    props["composition"]["duration_frames"] = -1

    summary = preflight(props, tmp_path)

    messages = [issue.message for issue in summary.errors]
    assert "composition.fps must be a positive integer" in messages
    assert "composition.duration_frames must be a positive integer" in messages
    assert summary.fps is None
    assert summary.duration_frames is None


@pytest.mark.parametrize("value", [None, {}, "bad"])
def test_missing_or_non_array_scenes_fails_clearly(tmp_path, value) -> None:
    props = valid_props()
    if value is None:
        del props["scenes"]
    else:
        props["scenes"] = value

    with pytest.raises(SyncCutError, match="scenes must be an array"):
        preflight(props, tmp_path)


@pytest.mark.parametrize("value", [None, {}, "bad"])
def test_missing_or_non_array_sections_fails_clearly(tmp_path, value) -> None:
    props = valid_props()
    if value is None:
        del props["sections"]
    else:
        props["sections"] = value

    with pytest.raises(SyncCutError, match="sections must be an array"):
        preflight(props, tmp_path)


def test_negative_scene_and_section_frames_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["start_frame"] = -1
    props["scenes"][0]["start_frame"] = -1

    summary = preflight(props, tmp_path)

    messages = [issue.message for issue in summary.errors]
    assert "sections[0].start_frame must be non-negative" in messages
    assert "scenes[0].start_frame must be non-negative" in messages


def test_scene_and_section_end_frame_beyond_composition_duration_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["sections"][1]["end_frame"] = 121
    props["scenes"][2]["end_frame"] = 121

    summary = preflight(props, tmp_path)

    messages = [issue.message for issue in summary.errors]
    assert "sections[1].end_frame must be <= composition.duration_frames" in messages
    assert "scenes[2].end_frame must be <= composition.duration_frames" in messages


def test_scene_and_section_duration_mismatch_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["duration_frames"] = 59
    props["scenes"][0]["duration_frames"] = 29

    summary = preflight(props, tmp_path)

    messages = [issue.message for issue in summary.errors]
    assert "sections[0].duration_frames must equal end_frame - start_frame" in messages
    assert "scenes[0].duration_frames must equal end_frame - start_frame" in messages


def test_metadata_total_scene_and_section_mismatches_produce_errors(tmp_path) -> None:
    props = valid_props()
    props["metadata"]["total_scenes"] = 99
    props["metadata"]["total_sections"] = 99

    summary = preflight(props, tmp_path)

    messages = [issue.message for issue in summary.errors]
    assert "metadata.total_scenes must match scenes length" in messages
    assert "metadata.total_sections must match sections length" in messages


def test_target_visual_shape_error_is_reported_not_raised(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["type"] = "B_ROLL"

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert any(issue.code == "invalid_visual_readiness" for issue in summary.errors)


def test_text_output_stable(tmp_path) -> None:
    props = valid_props()
    props["warnings"] = ["section gap"]
    summary = preflight(props, tmp_path)

    assert format_preflight(summary) == (
        f"Preflight: {tmp_path / 'remotion' / 'props.json'}\n"
        "status: warning\n"
        "scenes: 3\n"
        "sections: 2\n"
        "duration_sec: 4.0\n"
        "duration_frames: 120\n"
        "fps: 30\n"
        "audio_prepared: 2\n"
        "audio_missing_public_path: 0\n"
        "visual_target_scenes: 2\n"
        "visual_prepared: 0\n"
        "visual_missing: 2\n"
        "visual_unsupported: 0\n"
        "warnings: 3\n"
        "errors: 0\n"
        "\n"
        "Warnings:\n"
        "warning props_warning section gap\n"
        "warning visual_missing scene_001 AI_VIDEO missing visual asset; placeholder will render\n"
        "warning visual_missing scene_002 B_ROLL missing visual asset; placeholder will render\n"
        "\n"
        "Errors:\n"
        "none\n"
    )


def test_json_dictionary_output_deterministic(tmp_path) -> None:
    props = valid_props()
    props["warnings"] = ["section gap"]
    summary = preflight(props, tmp_path)

    assert preflight_to_dict(summary) == {
        "path": str(tmp_path / "remotion" / "props.json"),
        "status": "warning",
        "scenes": 3,
        "sections": 2,
        "duration_sec": 4.0,
        "duration_frames": 120,
        "fps": 30,
        "audio_prepared": 2,
        "audio_missing_public_path": 0,
        "visual_target_scenes": 2,
        "visual_prepared": 0,
        "visual_missing": 2,
        "visual_unsupported": 0,
        "warnings": [
            {"level": "warning", "code": "props_warning", "message": "section gap"},
            {
                "level": "warning",
                "code": "visual_missing",
                "message": "scene_001 AI_VIDEO missing visual asset; placeholder will render",
            },
            {
                "level": "warning",
                "code": "visual_missing",
                "message": "scene_002 B_ROLL missing visual asset; placeholder will render",
            },
        ],
        "errors": [],
    }


def test_file_helper_does_not_modify_props_file(tmp_path) -> None:
    props = valid_props()
    props_path = tmp_path / "remotion" / "props.json"
    props_path.parent.mkdir(parents=True)
    original = json.dumps(props, indent=2) + "\n"
    props_path.write_text(original, encoding="utf-8")

    summary = inspect_preflight_file(props_path)

    assert summary.scenes == 3
    assert props_path.read_text(encoding="utf-8") == original


def test_file_helper_verify_files_false_does_not_modify_props_file(tmp_path) -> None:
    props = valid_props()
    props_path = tmp_path / "remotion" / "props.json"
    props_path.parent.mkdir(parents=True)
    original = json.dumps(props, indent=2) + "\n"
    props_path.write_text(original, encoding="utf-8")

    summary = inspect_preflight_file(props_path, verify_files=False)

    assert summary.scenes == 3
    assert summary.verify_files is False
    assert summary.file_errors == 0
    assert props_path.read_text(encoding="utf-8") == original


def test_verify_files_requires_public_dir_at_helper_level(tmp_path) -> None:
    with pytest.raises(SyncCutError, match="--public-dir is required"):
        inspect_preflight(valid_props(), tmp_path / "props.json", verify_files=True)


def test_verify_existing_section_and_root_audio_files_have_no_file_error(tmp_path) -> None:
    props = valid_props()
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "warning"
    assert summary.verify_files is True
    assert summary.public_dir == public_dir
    assert summary.file_errors == 0
    assert not any(issue.code.startswith("missing_public_file") for issue in summary.errors)


def test_verify_existing_prepared_visual_scene_file_has_no_file_error(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "visuals/scene_001.png"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)
    write_public_file(public_dir, "visuals/scene_001.png", b"png")

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.visual_prepared == 1
    assert summary.file_errors == 0
    assert not any(issue.code == "missing_public_file" for issue in summary.errors)


def test_verify_existing_root_visual_asset_file_has_no_file_error(tmp_path) -> None:
    props = valid_props()
    props["assets"]["visuals"] = [
        {
            "scene_id": "scene_001",
            "visual_type": "AI_VIDEO",
            "public_path": "visuals/scene_001.png",
            "asset_status": "prepared",
            "asset_source": "local",
        }
    ]
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)
    write_public_file(public_dir, "visuals/scene_001.png", b"png")

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.file_errors == 0
    assert not any(issue.code == "missing_public_file" for issue in summary.errors)


def test_missing_section_audio_file_is_file_error(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["public_path"] = "audio/missing-section.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(
        issue.code == "missing_public_file"
        and "sections[0].audio public_path audio/missing-section.mp3 missing under" in issue.message
        for issue in summary.errors
    )


def test_missing_root_audio_file_is_file_error(tmp_path) -> None:
    props = valid_props()
    props["assets"]["audio"][0]["public_path"] = "audio/missing-root.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(
        issue.code == "missing_public_file"
        and "assets.audio[0] public_path audio/missing-root.mp3 missing under" in issue.message
        for issue in summary.errors
    )


def test_directory_instead_of_public_file_is_file_error(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["public_path"] = "audio/as-directory.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)
    (public_dir / "audio" / "as-directory.mp3").mkdir(parents=True)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(issue.code == "public_path_is_directory" for issue in summary.errors)


def test_absolute_public_path_is_invalid_file_error(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["public_path"] = str(tmp_path / "outside.mp3")
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(issue.code == "invalid_public_path" for issue in summary.errors)


def test_parent_segment_public_path_is_invalid_file_error(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["public_path"] = "audio/../outside.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(issue.code == "invalid_public_path" for issue in summary.errors)


def test_prepared_visual_scene_missing_file_is_file_error(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "visuals/scene_001.png"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert any(
        issue.code == "missing_public_file"
        and "scene scene_001 AI_VIDEO public_path visuals/scene_001.png missing under" in issue.message
        for issue in summary.errors
    )


def test_missing_visual_scene_remains_warning_without_file_error(tmp_path) -> None:
    props = valid_props()
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "warning"
    assert summary.file_errors == 0
    assert [issue.code for issue in summary.warnings] == ["visual_missing", "visual_missing"]


def test_unsupported_visual_path_does_not_get_duplicate_file_error(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "assets/scene_001.gif"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 0
    assert [issue.code for issue in summary.errors] == ["visual_unsupported"]


def test_scene_audio_public_path_is_ignored_by_file_verification(tmp_path) -> None:
    props = valid_props()
    props["scenes"][0]["audio"]["public_path"] = "/tmp/not-public.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.file_errors == 0
    assert not any(issue.code == "invalid_public_path" for issue in summary.errors)


def test_original_path_fields_outside_public_dir_are_ignored(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["path"] = "/outside/source.mp3"
    props["assets"]["audio"][0]["path"] = "/outside/source.mp3"
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.file_errors == 0
    assert not any(issue.code == "invalid_public_path" for issue in summary.errors)


def test_assets_visuals_missing_public_path_is_deterministic_file_error(tmp_path) -> None:
    props = valid_props()
    props["assets"]["visuals"] = [{"scene_id": "scene_001", "visual_type": "AI_VIDEO"}]
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert summary.errors[-1].code == "invalid_public_path"
    assert summary.errors[-1].message == "assets.visuals[0] public_path must be a non-empty string"


def test_assets_visuals_malformed_value_is_deterministic_file_error(tmp_path) -> None:
    props = valid_props()
    props["assets"]["visuals"] = ["bad"]
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)

    assert summary.status == "error"
    assert summary.file_errors == 1
    assert summary.errors[-1].code == "invalid_public_path"
    assert summary.errors[-1].message == "assets.visuals[0] public_path must be a non-empty string"


def test_text_output_with_verification_includes_file_fields(tmp_path) -> None:
    props = valid_props()
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)
    output = format_preflight(summary)

    assert "verify_files: true\n" in output
    assert f"public_dir: {public_dir}\n" in output
    assert "file_errors: 0\n" in output


def test_json_output_with_verification_includes_file_fields(tmp_path) -> None:
    props = valid_props()
    public_dir = tmp_path / "remotion" / "public"
    write_default_audio_files(public_dir)

    summary = verified_preflight(props, tmp_path, public_dir)
    output = preflight_to_dict(summary)

    assert output["verify_files"] is True
    assert output["public_dir"] == str(public_dir)
    assert output["file_errors"] == 0


def test_file_error_ordering_is_deterministic(tmp_path) -> None:
    props = valid_props()
    props["sections"][0]["audio"]["public_path"] = "audio/missing-section.mp3"
    props["assets"]["audio"][0]["public_path"] = "audio/missing-root.mp3"
    props["scenes"][0]["visual"]["asset_status"] = "prepared"
    props["scenes"][0]["visual"]["public_path"] = "visuals/missing-scene.png"
    props["assets"]["visuals"] = [{"public_path": "visuals/missing-root-visual.png"}]
    public_dir = tmp_path / "remotion" / "public"
    write_public_file(public_dir, "audio/02_BODY.mp3")

    summary = verified_preflight(props, tmp_path, public_dir)

    assert [issue.message for issue in summary.errors if issue.code == "missing_public_file"] == [
        f"sections[0].audio public_path audio/missing-section.mp3 missing under {public_dir}",
        f"assets.audio[0] public_path audio/missing-root.mp3 missing under {public_dir}",
        f"scene scene_001 AI_VIDEO public_path visuals/missing-scene.png missing under {public_dir}",
        f"assets.visuals[0] public_path visuals/missing-root-visual.png missing under {public_dir}",
    ]


def test_non_string_root_warning_is_structural_error(tmp_path) -> None:
    props = valid_props()
    props["warnings"] = ["ok", 123]

    summary = preflight(props, tmp_path)

    assert summary.status == "error"
    assert summary.warnings[0].code == "props_warning"
    assert any(issue.message == "warnings[1] must be a string" for issue in summary.errors)


def test_duration_sec_derived_when_metadata_duration_absent(tmp_path) -> None:
    props = valid_props()
    del props["metadata"]["duration_sec"]

    summary = preflight(props, tmp_path)

    assert summary.duration_sec == 4.0


def test_input_props_not_mutated(tmp_path) -> None:
    props = valid_props()
    original = deepcopy(props)

    preflight(props, tmp_path)

    assert props == original
