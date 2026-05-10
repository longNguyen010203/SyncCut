import copy
import json
from pathlib import Path

import pytest

from synccut.remotion_exporter import (
    DEFAULT_COMPOSITION_ID,
    DEFAULT_FPS,
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    build_remotion_props,
    export_remotion_props_file,
    seconds_to_frame,
)
from synccut.validators import SyncCutError


def scene_entry(
    scene_id: str,
    section_key: str,
    section: str,
    section_order: int,
    scene_order: int,
    start: float,
    end: float,
    visual_type: str = "AI_VIDEO",
) -> dict:
    return {
        "scene_id": scene_id,
        "scene_order": scene_order,
        "section": section,
        "section_order": section_order,
        "section_key": section_key,
        "timing": {
            "start_sec": start,
            "end_sec": end,
            "duration_sec": end - start,
            "local_start_sec": start,
            "local_end_sec": end,
        },
        "audio": {"path": f"audio/{section_key}.mp3"},
        "alignment": {
            "path": f"alignments/{section_key}_alignment.json",
            "match_method": "paragraph",
            "matched_units": [f"{scene_id}:paragraph"],
        },
        "dialogue": {
            "text": f"Dialogue for {scene_id}.",
            "paragraphs": [f"Dialogue for {scene_id}."],
        },
        "visual": {
            "type": visual_type,
            "prompt": f"Prompt for {scene_id}.",
            "data": {"scene": scene_id},
        },
        "warnings": [f"{scene_id} warning"],
    }


def section_entry(
    section_key: str,
    section: str,
    section_order: int,
    start: float,
    end: float,
    audio_path: str | None = None,
) -> dict:
    return {
        "section_key": section_key,
        "section": section,
        "section_order": section_order,
        "audio_path": audio_path or f"audio/{section_key}.mp3",
        "alignment_path": f"alignments/{section_key}_alignment.json",
        "local_duration_sec": end - start,
        "global_start_sec": start,
        "global_end_sec": end,
    }


def valid_timeline() -> dict:
    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_by": "synccut build-timeline",
            "source_scenes": "scenes.json",
            "total_scenes": 2,
            "total_sections": 2,
            "total_duration_sec": 4.0,
        },
        "sections": [
            section_entry("01_HOOK", "HOOK", 1, 0.0, 2.0),
            section_entry("02_BODY", "BODY", 2, 2.0, 4.0),
        ],
        "timeline": [
            scene_entry("scene_001", "01_HOOK", "HOOK", 1, 1, 0.0, 2.0, "AI_VIDEO"),
            scene_entry("scene_002", "02_BODY", "BODY", 2, 2, 2.0, 4.0, "B_ROLL"),
        ],
        "warnings": ["top-level warning"],
    }


def build_props(data: dict | None = None, path: Path | None = None) -> dict:
    return build_remotion_props(data or valid_timeline(), path or Path("timeline.json"))


def test_seconds_to_frame_uses_nearest_frame_rounding() -> None:
    assert seconds_to_frame(0.0) == 0
    assert seconds_to_frame(9.137) == 274
    assert seconds_to_frame(752.79) == 22584


@pytest.mark.parametrize("value", [True, False, "1.0", None, object()])
def test_seconds_to_frame_rejects_booleans_and_non_numeric_values(value) -> None:
    with pytest.raises(SyncCutError, match="seconds must be numeric"):
        seconds_to_frame(value)


def test_metadata_and_composition_are_exported() -> None:
    props = build_props(path=Path("nested/timeline.json"))

    assert props["metadata"] == {
        "generated_by": "synccut export-remotion",
        "source_timeline": "nested/timeline.json",
        "fps": DEFAULT_FPS,
        "duration_sec": 4.0,
        "duration_frames": 120,
        "total_scenes": 2,
        "total_sections": 2,
    }
    assert props["composition"] == {
        "id": DEFAULT_COMPOSITION_ID,
        "width": DEFAULT_WIDTH,
        "height": DEFAULT_HEIGHT,
        "fps": DEFAULT_FPS,
        "duration_frames": 120,
    }


def test_section_mapping_preserves_fields_and_computes_frames() -> None:
    section = build_props()["sections"][0]

    assert section["section_key"] == "01_HOOK"
    assert section["section"] == "HOOK"
    assert section["section_order"] == 1
    assert section["start_sec"] == 0.0
    assert section["end_sec"] == 2.0
    assert section["duration_sec"] == 2.0
    assert section["start_frame"] == 0
    assert section["end_frame"] == 60
    assert section["duration_frames"] == 60


def test_scene_mapping_preserves_fields_and_computes_frames() -> None:
    scene = build_props()["scenes"][0]

    assert scene["id"] == "scene_001"
    assert scene["scene_order"] == 1
    assert scene["section"] == "HOOK"
    assert scene["section_order"] == 1
    assert scene["section_key"] == "01_HOOK"
    assert scene["start_sec"] == 0.0
    assert scene["end_sec"] == 2.0
    assert scene["duration_sec"] == 2.0
    assert scene["local_start_sec"] == 0.0
    assert scene["local_end_sec"] == 2.0
    assert scene["start_frame"] == 0
    assert scene["end_frame"] == 60
    assert scene["duration_frames"] == 60
    assert scene["visual_type"] == "AI_VIDEO"
    assert scene["visual"] == scene_entry("scene_001", "01_HOOK", "HOOK", 1, 1, 0.0, 2.0)[
        "visual"
    ]
    assert scene["dialogue"]["text"] == "Dialogue for scene_001."
    assert scene["audio"] == {"path": "audio/01_HOOK.mp3"}
    assert scene["alignment"]["path"] == "alignments/01_HOOK_alignment.json"
    assert scene["warnings"] == ["scene_001 warning"]


@pytest.mark.parametrize(
    "visual_type",
    [
        "AI_VIDEO",
        "B_ROLL",
        "CHART",
        "COMPARISON_CARD",
        "TABLE",
        "SHARE_BREAKDOWN",
        "TIMELINE",
    ],
)
def test_supported_visual_types_are_accepted_and_preserved(visual_type: str) -> None:
    data = valid_timeline()
    data["timeline"] = [
        scene_entry("scene_001", "01_HOOK", "HOOK", 1, 1, 0.0, 2.0, visual_type),
        scene_entry("scene_002", "02_BODY", "BODY", 2, 2, 2.0, 4.0, "AI_VIDEO"),
    ]

    scene = build_props(data)["scenes"][0]

    assert scene["visual_type"] == visual_type
    assert scene["visual"]["type"] == visual_type


def test_assets_audio_is_unique_sorted_and_visuals_is_empty() -> None:
    data = valid_timeline()
    data["sections"] = [
        section_entry("03_END", "END", 3, 4.0, 6.0, audio_path="audio/end.mp3"),
        section_entry("02_BODY", "BODY", 2, 2.0, 4.0, audio_path="audio/shared.mp3"),
        section_entry("01_HOOK", "HOOK", 1, 0.0, 2.0, audio_path="audio/shared.mp3"),
    ]
    data["metadata"]["total_sections"] = 3
    data["metadata"]["total_duration_sec"] = 6.0

    props = build_props(data)

    assert props["assets"]["audio"] == [
        {"section_key": "01_HOOK", "path": "audio/shared.mp3"},
        {"section_key": "03_END", "path": "audio/end.mp3"},
    ]
    assert props["assets"]["visuals"] == []


def test_top_level_and_validation_warnings_are_merged_without_duplicates() -> None:
    data = valid_timeline()
    data["timeline"][0]["timing"] = {
        "start_sec": 0.0,
        "end_sec": 1.0,
        "duration_sec": 1.0,
        "local_start_sec": 0.0,
        "local_end_sec": 1.0,
    }
    data["timeline"][1]["timing"] = {
        "start_sec": 2.5,
        "end_sec": 4.0,
        "duration_sec": 1.5,
        "local_start_sec": 2.5,
        "local_end_sec": 4.0,
    }
    gap_warning = "section 01_HOOK has a gap of 1.500s between scene_001 and scene_002"
    data["timeline"][1]["section_key"] = "01_HOOK"
    data["timeline"][1]["section"] = "HOOK"
    data["timeline"][1]["section_order"] = 1
    data["timeline"][1]["audio"] = {"path": "audio/01_HOOK.mp3"}
    data["timeline"][1]["alignment"]["path"] = "alignments/01_HOOK_alignment.json"
    data["warnings"] = ["top-level warning", gap_warning]
    data["metadata"]["total_sections"] = 2

    props = build_props(data)

    assert props["warnings"] == ["top-level warning", gap_warning]


def test_shuffled_sections_and_scenes_export_in_deterministic_order() -> None:
    data = valid_timeline()
    data["sections"] = list(reversed(data["sections"]))
    data["timeline"] = list(reversed(data["timeline"]))

    props = build_props(data)

    assert [section["section_key"] for section in props["sections"]] == [
        "01_HOOK",
        "02_BODY",
    ]
    assert [scene["id"] for scene in props["scenes"]] == ["scene_001", "scene_002"]


def test_invalid_timeline_raises_synccut_error_clearly() -> None:
    with pytest.raises(SyncCutError, match="invalid timeline: missing metadata"):
        build_remotion_props({"sections": [], "timeline": [], "warnings": []}, Path("bad.json"))


def test_positive_duration_scene_that_rounds_to_zero_frames_fails() -> None:
    data = valid_timeline()
    data["timeline"][0]["timing"] = {
        "start_sec": 0.0,
        "end_sec": 0.01,
        "duration_sec": 0.01,
        "local_start_sec": 0.0,
        "local_end_sec": 0.01,
    }

    with pytest.raises(SyncCutError, match="scene scene_001 has non-positive frame duration"):
        build_props(data)


def test_positive_duration_section_that_rounds_to_zero_frames_fails() -> None:
    data = valid_timeline()
    data["metadata"]["total_duration_sec"] = 0.01
    data["metadata"]["total_sections"] = 1
    data["metadata"]["total_scenes"] = 1
    data["sections"] = [section_entry("01_HOOK", "HOOK", 1, 0.0, 0.01)]
    data["timeline"] = [
        scene_entry("scene_001", "01_HOOK", "HOOK", 1, 1, 0.0, 0.01, "AI_VIDEO")
    ]

    with pytest.raises(SyncCutError, match="section 01_HOOK has non-positive frame duration"):
        build_props(data)


def test_export_remotion_props_file_writes_two_space_json_and_returns_props(tmp_path) -> None:
    data = valid_timeline()
    timeline_path = tmp_path / "timeline.json"
    out_path = tmp_path / "nested" / "props.json"
    timeline_path.write_text(json.dumps(data), encoding="utf-8")

    returned = export_remotion_props_file(timeline_path, out_path)

    assert out_path.exists()
    text = out_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '\n  "metadata": {' in text
    written = json.loads(text)
    assert returned == written


def test_build_remotion_props_does_not_mutate_input() -> None:
    data = valid_timeline()
    original = copy.deepcopy(data)

    build_props(data)

    assert data == original
