import pytest

from synccut.timeline_inspector import build_timeline_overview, section_overview_rows
from synccut.validators import SyncCutError


def timeline_fixture() -> dict:
    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_by": "synccut build-timeline",
            "source_scenes": "scenes.json",
            "total_scenes": 3,
            "total_sections": 2,
            "total_duration_sec": 8.0,
        },
        "sections": [
            {
                "section_key": "02_BODY",
                "section": "BODY",
                "section_order": 2,
                "audio_path": "audio/02_BODY.mp3",
                "alignment_path": "alignments/02_BODY_alignment_tmp.json",
                "local_duration_sec": 4.0,
                "global_start_sec": 4.0,
                "global_end_sec": 8.0,
            },
            {
                "section_key": "01_HOOK",
                "section": "HOOK",
                "section_order": 1,
                "audio_path": "audio/01_HOOK.mp3",
                "alignment_path": "alignments/01_HOOK_alignment_tmp.json",
                "local_duration_sec": 4.0,
                "global_start_sec": 0.0,
                "global_end_sec": 4.0,
            },
        ],
        "timeline": [
            scene_entry(
                "scene_003",
                "02_BODY",
                "BODY",
                2,
                3,
                4.0,
                8.0,
                "TABLE",
                "sentence",
            ),
            scene_entry(
                "scene_002",
                "01_HOOK",
                "HOOK",
                1,
                2,
                2.0,
                4.0,
                "B_ROLL",
                "word_span",
            ),
            scene_entry(
                "scene_001",
                "01_HOOK",
                "HOOK",
                1,
                1,
                0.0,
                2.0,
                "AI_VIDEO",
                "paragraph",
            ),
        ],
        "warnings": ["top-level warning"],
    }


def scene_entry(
    scene_id: str,
    section_key: str,
    section: str,
    section_order: int,
    scene_order: int,
    start: float,
    end: float,
    visual_type: str,
    match_method: str,
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
            "path": f"alignments/{section_key}_alignment_tmp.json",
            "match_method": match_method,
            "matched_units": ["paragraph:0"],
        },
        "dialogue": {"text": "Dialogue.", "paragraphs": ["Dialogue."]},
        "visual": {"type": visual_type, "prompt": None, "data": None},
        "warnings": [],
    }


def test_overview_includes_path_scenes_sections_duration_warning_count(tmp_path) -> None:
    path = tmp_path / "timeline.json"

    output = build_timeline_overview(timeline_fixture(), path=path)

    assert f"Timeline: {path}" in output
    assert "Scenes: 3" in output
    assert "Sections: 2" in output
    assert "Duration: 8.000s" in output
    assert "Warnings: 1" in output


def test_output_groups_scenes_under_correct_section() -> None:
    output = build_timeline_overview(timeline_fixture())

    hook_index = output.index("[01_HOOK] HOOK")
    first_scene_index = output.index("scene_001")
    second_scene_index = output.index("scene_002")
    body_index = output.index("[02_BODY] BODY")
    third_scene_index = output.index("scene_003")

    assert hook_index < first_scene_index < second_scene_index < body_index < third_scene_index


def test_output_includes_scene_id_timing_visual_type_and_match_method() -> None:
    output = build_timeline_overview(timeline_fixture())

    assert "scene_002 2.000s-4.000s 2.000s B_ROLL word_span" in output


def test_output_ordering_is_deterministic_when_input_arrays_are_shuffled() -> None:
    rows = section_overview_rows(timeline_fixture())

    assert rows[0].startswith("[01_HOOK]")
    assert rows[1].strip().startswith("scene_001")
    assert rows[2].strip().startswith("scene_002")
    assert rows[4].startswith("[02_BODY]")
    assert rows[5].strip().startswith("scene_003")


def test_malformed_minimal_input_fails_clearly() -> None:
    with pytest.raises(SyncCutError, match="timeline is not valid enough to inspect"):
        build_timeline_overview({"metadata": {}})
