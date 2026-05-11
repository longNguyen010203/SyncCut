import json
from pathlib import Path

import pytest

from synccut.validators import SyncCutError
from synccut.visual_assets import prepare_visual_assets, prepare_visual_assets_file


def write_asset(path: Path, content: bytes = b"visual") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def valid_props() -> dict:
    return {
        "metadata": {
            "generated_by": "synccut export-remotion",
            "source_timeline": "timeline.json",
            "fps": 30,
            "duration_sec": 3.0,
            "duration_frames": 90,
            "total_scenes": 3,
            "total_sections": 1,
        },
        "composition": {
            "id": "SyncCutVideo",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "duration_frames": 90,
        },
        "sections": [],
        "scenes": [
            {
                "id": "scene_001",
                "scene_order": 1,
                "visual_type": "AI_VIDEO",
                "visual": {
                    "type": "AI_VIDEO",
                    "prompt": "AI prompt",
                    "data": {"keep": "this"},
                },
            },
            {
                "id": "scene_002",
                "scene_order": 2,
                "visual_type": "B_ROLL",
                "visual": {"type": "B_ROLL", "prompt": "B-roll prompt", "data": None},
            },
            {
                "id": "scene_003",
                "scene_order": 3,
                "visual_type": "CHART",
                "visual": {"type": "CHART", "prompt": "Chart prompt", "data": {"x": 1}},
            },
        ],
        "assets": {"audio": [], "visuals": []},
        "warnings": [],
    }


def prepare(props: dict, tmp_path: Path) -> tuple[dict, object]:
    return prepare_visual_assets(
        props,
        tmp_path / "remotion" / "props.json",
        tmp_path / "assets" / "visuals",
        tmp_path / "remotion" / "public",
    )


def test_valid_local_image_copy_creates_public_visual_file_and_public_path(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png", b"image")

    updated, result = prepare(valid_props(), tmp_path)

    destination = tmp_path / "remotion" / "public" / "visuals" / "scene_001.png"
    assert destination.read_bytes() == b"image"
    assert updated["scenes"][0]["visual"]["public_path"] == "visuals/scene_001.png"
    assert updated["scenes"][0]["visual"]["asset_status"] == "prepared"
    assert updated["scenes"][0]["visual"]["asset_source"] == "local"
    assert result.copied == 1
    assert result.missing == 1


def test_valid_local_video_copy_creates_public_visual_file_and_public_path(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_002.MP4", b"video")

    updated, result = prepare(valid_props(), tmp_path)

    destination = tmp_path / "remotion" / "public" / "visuals" / "scene_002.mp4"
    assert destination.read_bytes() == b"video"
    assert updated["scenes"][1]["visual"]["public_path"] == "visuals/scene_002.mp4"
    assert result.copied == 1
    assert result.visual_assets[0].public_path == "visuals/scene_002.mp4"


def test_missing_assets_do_not_fail_and_set_missing_local_status(tmp_path) -> None:
    updated, result = prepare(valid_props(), tmp_path)

    assert result.missing == 2
    assert updated["scenes"][0]["visual"]["asset_status"] == "missing"
    assert updated["scenes"][0]["visual"]["asset_source"] == "local"
    assert "public_path" not in updated["scenes"][0]["visual"]
    assert updated["scenes"][1]["visual"]["asset_status"] == "missing"


def test_duplicate_supported_files_for_one_scene_id_fail_clearly(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png", b"image")
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4", b"video")

    with pytest.raises(SyncCutError, match="multiple supported visual assets for scene_001"):
        prepare(valid_props(), tmp_path)


def test_unsupported_files_do_not_get_copied_or_marked_prepared(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.txt", b"not-media")

    updated, result = prepare(valid_props(), tmp_path)

    assert result.copied == 0
    assert result.visual_assets == []
    assert updated["scenes"][0]["visual"]["asset_status"] == "missing"
    assert not (tmp_path / "remotion" / "public" / "visuals" / "scene_001.txt").exists()


def test_rerunning_with_identical_destination_reuses_file(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png", b"same")
    props = valid_props()

    prepare(props, tmp_path)
    _, result = prepare(props, tmp_path)

    assert result.copied == 0
    assert result.reused == 1
    assert result.overwritten == 0


def test_rerunning_with_changed_source_overwrites_destination(tmp_path) -> None:
    source = write_asset(tmp_path / "assets" / "visuals" / "scene_001.png", b"old")
    props = valid_props()

    prepare(props, tmp_path)
    source.write_bytes(b"new")
    _, result = prepare(props, tmp_path)

    assert (tmp_path / "remotion" / "public" / "visuals" / "scene_001.png").read_bytes() == b"new"
    assert result.copied == 0
    assert result.reused == 0
    assert result.overwritten == 1


def test_props_preserve_original_visual_prompt_and_data(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")

    updated, _ = prepare(valid_props(), tmp_path)

    assert updated["scenes"][0]["visual"]["prompt"] == "AI prompt"
    assert updated["scenes"][0]["visual"]["data"] == {"keep": "this"}


def test_non_ai_video_and_b_roll_scenes_remain_unchanged(tmp_path) -> None:
    props = valid_props()
    original_chart = props["scenes"][2].copy()

    updated, _ = prepare(props, tmp_path)

    assert updated["scenes"][2] == original_chart


def test_assets_visuals_entries_are_deterministic_scene_order(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_002.mp4", b"video")
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png", b"image")

    updated, result = prepare(valid_props(), tmp_path)

    assert [asset.scene_id for asset in result.visual_assets] == ["scene_001", "scene_002"]
    assert [entry["scene_id"] for entry in updated["assets"]["visuals"]] == [
        "scene_001",
        "scene_002",
    ]
    assert updated["assets"]["visuals"][0]["public_path"] == "visuals/scene_001.png"
    assert updated["assets"]["visuals"][1]["public_path"] == "visuals/scene_002.mp4"


def test_prepare_visual_assets_file_writes_two_space_json_with_trailing_newline(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")
    props_path = tmp_path / "remotion" / "props.json"
    props_path.parent.mkdir(parents=True)
    props_path.write_text(json.dumps(valid_props()), encoding="utf-8")

    result = prepare_visual_assets_file(
        props_path,
        tmp_path / "assets" / "visuals",
        tmp_path / "remotion" / "public",
    )

    text = props_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '\n  "metadata": {' in text
    written = json.loads(text)
    assert written["scenes"][0]["visual"]["public_path"] == "visuals/scene_001.png"
    assert result.copied == 1
