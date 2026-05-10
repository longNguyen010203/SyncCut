import json

import pytest

from synccut.timeline_validator import (
    load_timeline_json,
    validate_timeline,
    validate_timeline_file,
)
from synccut.validators import SyncCutError


def valid_timeline() -> dict:
    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_by": "synccut build-timeline",
            "source_scenes": "scenes.json",
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
                "alignment_path": "alignments/01_HOOK_alignment_tmp.json",
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
                    "start_sec": 0.0,
                    "end_sec": 2.0,
                    "duration_sec": 2.0,
                    "local_start_sec": 0.0,
                    "local_end_sec": 2.0,
                },
                "audio": {"path": "audio/01_HOOK.mp3"},
                "alignment": {
                    "path": "alignments/01_HOOK_alignment_tmp.json",
                    "match_method": "paragraph",
                    "matched_units": ["paragraph:0"],
                },
                "dialogue": {
                    "text": "Hello world.",
                    "paragraphs": ["Hello world."],
                },
                "visual": {
                    "type": "AI_VIDEO",
                    "prompt": "Prompt.",
                    "data": None,
                },
                "warnings": [],
            }
        ],
        "warnings": [],
    }


def write_timeline(tmp_path, data: dict):
    path = tmp_path / "timeline.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def first_entry(data: dict) -> dict:
    return data["timeline"][0]


def test_valid_timeline_passes(tmp_path) -> None:
    path = write_timeline(tmp_path, valid_timeline())

    result = validate_timeline_file(path)

    assert result.ok
    assert result.errors == []
    assert result.warnings == []
    assert result.total_scenes == 1
    assert result.total_sections == 1
    assert result.total_duration_sec == 2.0


def test_missing_metadata_fails() -> None:
    data = valid_timeline()
    data.pop("metadata")

    result = validate_timeline(data)

    assert not result.ok
    assert "missing metadata" in result.errors


def test_missing_sections_fails() -> None:
    data = valid_timeline()
    data.pop("sections")

    result = validate_timeline(data)

    assert not result.ok
    assert "missing sections" in result.errors


def test_missing_timeline_fails() -> None:
    data = valid_timeline()
    data.pop("timeline")

    result = validate_timeline(data)

    assert not result.ok
    assert "missing timeline" in result.errors


def test_invalid_json_file_loading_fails_clearly(tmp_path) -> None:
    path = tmp_path / "timeline.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(SyncCutError, match="malformed JSON"):
        load_timeline_json(path)


def test_missing_file_loading_fails_clearly(tmp_path) -> None:
    with pytest.raises(SyncCutError, match="file not found"):
        load_timeline_json(tmp_path / "missing.json")


def test_non_object_root_loading_fails_clearly(tmp_path) -> None:
    path = tmp_path / "timeline.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(SyncCutError, match="root must be an object"):
        load_timeline_json(path)


def test_total_scenes_mismatch_fails() -> None:
    data = valid_timeline()
    data["metadata"]["total_scenes"] = 2

    result = validate_timeline(data)

    assert any("metadata.total_scenes is 2" in error for error in result.errors)


def test_invalid_section_timing_fails() -> None:
    data = valid_timeline()
    data["sections"][0]["global_end_sec"] = 1.0

    result = validate_timeline(data)

    assert any("local_duration_sec must match" in error for error in result.errors)


def test_invalid_scene_duration_fails() -> None:
    data = valid_timeline()
    first_entry(data)["timing"]["duration_sec"] = 0

    result = validate_timeline(data)

    assert any("timeline[0].timing.duration_sec must be positive" == error for error in result.errors)


def test_scene_overlap_fails() -> None:
    data = valid_timeline()
    second = json.loads(json.dumps(first_entry(data)))
    second["scene_id"] = "scene_002"
    second["scene_order"] = 2
    second["timing"] = {
        "start_sec": 1.0,
        "end_sec": 2.5,
        "duration_sec": 1.5,
        "local_start_sec": 1.0,
        "local_end_sec": 2.5,
    }
    data["timeline"].append(second)
    data["metadata"]["total_scenes"] = 2

    result = validate_timeline(data)

    assert any("overlaps previous scene in section 01_HOOK" in error for error in result.errors)


def test_suspicious_gap_produces_warning_but_no_error() -> None:
    data = valid_timeline()
    first_entry(data)["timing"] = {
        "start_sec": 0.0,
        "end_sec": 1.0,
        "duration_sec": 1.0,
        "local_start_sec": 0.0,
        "local_end_sec": 1.0,
    }
    second = json.loads(json.dumps(first_entry(data)))
    second["scene_id"] = "scene_002"
    second["scene_order"] = 2
    second["timing"] = {
        "start_sec": 2.5,
        "end_sec": 3.0,
        "duration_sec": 0.5,
        "local_start_sec": 2.5,
        "local_end_sec": 3.0,
    }
    data["timeline"].append(second)
    data["metadata"]["total_scenes"] = 2
    data["sections"][0]["local_duration_sec"] = 3.0
    data["sections"][0]["global_end_sec"] = 3.0
    data["metadata"]["total_duration_sec"] = 3.0

    result = validate_timeline(data)

    assert result.ok
    assert any("gap of 1.500s" in warning for warning in result.warnings)


def test_missing_audio_path_fails() -> None:
    data = valid_timeline()
    first_entry(data)["audio"].pop("path")

    result = validate_timeline(data)

    assert any("timeline[0].audio.path must be a non-empty string" == error for error in result.errors)


def test_missing_alignment_path_fails() -> None:
    data = valid_timeline()
    first_entry(data)["alignment"].pop("path")

    result = validate_timeline(data)

    assert any("timeline[0].alignment.path must be a non-empty string" == error for error in result.errors)


def test_unsupported_visual_type_fails() -> None:
    data = valid_timeline()
    first_entry(data)["visual"]["type"] = "B-ROLL"

    result = validate_timeline(data)

    assert any("timeline[0].visual.type must be a supported normalized visual type" == error for error in result.errors)
