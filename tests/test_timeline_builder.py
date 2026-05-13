from pathlib import Path

import pytest

from synccut.models import (
    AlignmentParagraph,
    AlignmentSection,
    Dialogue,
    Scene,
    SectionAsset,
    TimedText,
    Visual,
)
from synccut.timeline_builder import build_timeline, match_scene_to_alignment
from synccut.validators import SyncCutError


def scene(
    scene_id: str,
    text: str,
    paragraphs: list[str] | None = None,
    *,
    scene_order: int = 1,
    section_key: str = "01_HOOK",
    section: str = "HOOK",
    section_order: int = 1,
    visual_type: str = "AI_VIDEO",
    visual_data=None,
) -> Scene:
    return Scene(
        scene_id=scene_id,
        scene_order=scene_order,
        section=section,
        section_order=section_order,
        section_key=section_key,
        dialogue=Dialogue(text=text, paragraphs=paragraphs or [text]),
        visual=Visual(type=visual_type, prompt="Visual prompt", data=visual_data),
    )


def alignment(
    *,
    duration: float = 10.0,
    paragraphs: list[AlignmentParagraph] | None = None,
    words: list[TimedText] | None = None,
    path: str = "alignments/01_HOOK_alignment_tmp.json",
) -> AlignmentSection:
    return AlignmentSection(
        path=path,
        total_duration_sec=duration,
        paragraphs=paragraphs or [],
        words=words or [],
    )


def paragraph(text: str, start: float, end: float, sentences: list[TimedText] | None = None):
    return AlignmentParagraph(text=text, start=start, end=end, sentences=sentences or [])


def section_asset(
    section_key: str,
    section: str,
    section_order: int,
    alignment_section: AlignmentSection,
) -> SectionAsset:
    return SectionAsset(
        section_key=section_key,
        section=section,
        section_order=section_order,
        audio_path=f"audio/{section_key}.mp3",
        alignment_path=alignment_section.path,
        alignment=alignment_section,
    )


def test_paragraph_matching() -> None:
    item = scene("scene_001", "Hello world.")
    aligned = alignment(paragraphs=[paragraph("Hello world.", 1.0, 2.5)])

    match = match_scene_to_alignment(item, aligned)

    assert match.match_method == "paragraph"
    assert match.local_start_sec == 1.0
    assert match.local_end_sec == 2.5
    assert match.matched_units == ["paragraph:0"]


def test_sentence_fallback_when_boundaries_differ() -> None:
    item = scene(
        "scene_001",
        "Hello world. More words.",
        ["Hello world.", "More words."],
    )
    aligned = alignment(
        paragraphs=[
            paragraph(
                "Hello world. More words.",
                0.0,
                3.0,
                [
                    TimedText("Hello world.", 0.0, 1.0),
                    TimedText("More words.", 1.2, 3.0),
                ],
            )
        ]
    )

    match = match_scene_to_alignment(item, aligned)

    assert match.match_method == "sentence"
    assert match.local_start_sec == 0.0
    assert match.local_end_sec == 3.0
    assert match.matched_units == ["sentence:0:0", "sentence:0:1"]


def test_sentence_fallback_is_preferred_over_paragraph_substring() -> None:
    item = scene("scene_001", "Hello world.")
    aligned = alignment(
        paragraphs=[
            paragraph(
                "Intro. Hello world. Outro.",
                0.0,
                3.0,
                [
                    TimedText("Intro.", 0.0, 0.5),
                    TimedText("Hello world.", 0.75, 1.5),
                    TimedText("Outro.", 2.0, 3.0),
                ],
            )
        ]
    )

    match = match_scene_to_alignment(item, aligned)

    assert match.match_method == "sentence"
    assert match.local_start_sec == 0.75
    assert match.local_end_sec == 1.5


def test_single_paragraph_substring_falls_back_to_alignment_paragraph() -> None:
    item = scene("scene_001", "Hello world.")
    aligned = alignment(
        paragraphs=[
            paragraph("Intro. Hello world. Outro.", 0.0, 3.0),
        ]
    )

    match = match_scene_to_alignment(item, aligned)

    assert match.match_method == "paragraph"
    assert match.local_start_sec == 0.0
    assert match.local_end_sec == 3.0
    assert match.matched_units == ["paragraph:0"]


def test_word_span_fallback_for_small_synthetic_case() -> None:
    item = scene("scene_001", "target words")
    aligned = alignment(
        paragraphs=[paragraph("unrelated paragraph", 0.0, 1.0)],
        words=[
            TimedText("intro", 0.0, 0.2),
            TimedText("target", 0.3, 0.6),
            TimedText("words", 0.7, 1.0),
        ],
    )

    match = match_scene_to_alignment(item, aligned)

    assert match.match_method == "word_span"
    assert match.local_start_sec == 0.3
    assert match.local_end_sec == 1.0
    assert match.matched_units == ["word:1", "word:2"]


def test_failure_on_unmatched_dialogue() -> None:
    item = scene("scene_404", "missing words")
    aligned = alignment(paragraphs=[paragraph("other words", 0.0, 1.0)])

    with pytest.raises(SyncCutError, match="scene_404 in 01_HOOK"):
        match_scene_to_alignment(item, aligned)


def test_cumulative_section_offsets_across_two_sections() -> None:
    scenes = [
        scene("scene_002", "Intro line.", section_key="02_INTRO", section="INTRO", section_order=2, scene_order=2),
        scene("scene_001", "Hook line.", section_key="01_HOOK", section="HOOK", section_order=1, scene_order=1),
    ]
    sections = [
        section_asset(
            "02_INTRO",
            "INTRO",
            2,
            alignment(
                duration=7.0,
                paragraphs=[paragraph("Intro line.", 1.0, 3.0)],
                path="alignments/02_INTRO_alignment_tmp.json",
            ),
        ),
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=5.0,
                paragraphs=[paragraph("Hook line.", 0.5, 1.5)],
                path="alignments/01_HOOK_alignment_tmp.json",
            ),
        ),
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))

    assert output["metadata"]["total_duration_sec"] == 12.0
    assert output["sections"][0]["global_start_sec"] == 0.0
    assert output["sections"][0]["global_end_sec"] == 5.0
    assert output["sections"][1]["global_start_sec"] == 5.0
    assert output["sections"][1]["global_end_sec"] == 12.0
    assert output["timeline"][1]["timing"]["start_sec"] == 6.0
    assert output["timeline"][1]["timing"]["end_sec"] == 8.0


def test_correct_global_start_end_duration_math() -> None:
    item = scene("scene_001", "Hook line.")
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(duration=5.0, paragraphs=[paragraph("Hook line.", 0.5, 2.25)]),
        )
    ]

    output = build_timeline([item], sections, Path("scenes.json"))
    timing = output["timeline"][0]["timing"]

    assert timing == {
        "start_sec": 0.5,
        "end_sec": 2.25,
        "duration_sec": 1.75,
        "local_start_sec": 0.5,
        "local_end_sec": 2.25,
    }


def test_preserving_dialogue_data() -> None:
    item = scene("scene_001", "Hello. World.", ["Hello.", "World."])
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                paragraphs=[
                    paragraph("Hello.", 0.0, 1.0),
                    paragraph("World.", 1.2, 2.0),
                ]
            ),
        )
    ]

    output = build_timeline([item], sections, Path("scenes.json"))

    assert output["timeline"][0]["dialogue"] == {
        "text": "Hello. World.",
        "paragraphs": ["Hello.", "World."],
    }


def test_preserving_visual_data() -> None:
    item = scene("scene_001", "Hook line.", visual_data={"title": "A chart"})
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(duration=5.0, paragraphs=[paragraph("Hook line.", 0.0, 1.0)]),
        )
    ]

    output = build_timeline([item], sections, Path("scenes.json"))

    assert output["timeline"][0]["visual"] == {
        "type": "AI_VIDEO",
        "prompt": "Visual prompt",
        "data": {"title": "A chart"},
    }


def test_b_roll_remains_normalized_in_output() -> None:
    item = scene("scene_001", "Hook line.", visual_type="B_ROLL")
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(duration=5.0, paragraphs=[paragraph("Hook line.", 0.0, 1.0)]),
        )
    ]

    output = build_timeline([item], sections, Path("scenes.json"))

    assert output["timeline"][0]["visual"]["type"] == "B_ROLL"


def test_output_json_shape() -> None:
    item = scene("scene_001", "Hook line.")
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(duration=5.0, paragraphs=[paragraph("Hook line.", 0.0, 1.0)]),
        )
    ]

    output = build_timeline([item], sections, Path("scenes.json"))

    assert set(output) == {"metadata", "sections", "timeline", "warnings"}
    assert output["metadata"]["generated_by"] == "synccut build-timeline"
    assert output["timeline"][0]["audio"] == {"path": "audio/01_HOOK.mp3"}
    assert output["timeline"][0]["alignment"]["match_method"] == "paragraph"
    assert output["timeline"][0]["alignment"]["matched_units"] == ["paragraph:0"]
    assert output["warnings"] == []
    assert output["timeline"][0]["warnings"] == []


def test_deterministic_ordering_by_section_and_scene_order() -> None:
    scenes = [
        scene("scene_003", "Second section.", section_key="02_INTRO", section="INTRO", section_order=2, scene_order=3),
        scene("scene_002", "Second hook.", section_key="01_HOOK", section="HOOK", section_order=1, scene_order=2),
        scene("scene_001", "First hook.", section_key="01_HOOK", section="HOOK", section_order=1, scene_order=1),
    ]
    sections = [
        section_asset(
            "02_INTRO",
            "INTRO",
            2,
            alignment(
                duration=3.0,
                paragraphs=[paragraph("Second section.", 0.0, 1.0)],
                path="alignments/02_INTRO_alignment_tmp.json",
            ),
        ),
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=3.0,
                paragraphs=[
                    paragraph("First hook.", 0.0, 1.0),
                    paragraph("Second hook.", 1.1, 2.0),
                ],
                path="alignments/01_HOOK_alignment_tmp.json",
            ),
        ),
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))

    assert [entry["scene_id"] for entry in output["timeline"]] == [
        "scene_001",
        "scene_002",
        "scene_003",
    ]


def test_repeated_text_does_not_match_backwards() -> None:
    scenes = [
        scene("scene_001", "Repeat.", scene_order=1),
        scene("scene_002", "Repeat.", scene_order=2),
    ]
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=5.0,
                paragraphs=[
                    paragraph("Repeat.", 0.0, 1.0),
                    paragraph("Repeat.", 2.0, 3.0),
                ],
            ),
        )
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))

    assert output["timeline"][0]["timing"]["local_start_sec"] == 0.0
    assert output["timeline"][1]["timing"]["local_start_sec"] == 2.0


def test_suspicious_same_section_gap_extends_previous_scene() -> None:
    scenes = [
        scene("scene_001", "First.", scene_order=1),
        scene("scene_002", "Second.", scene_order=2),
    ]
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=4.0,
                paragraphs=[
                    paragraph("First.", 0.0, 1.0),
                    paragraph("Second.", 2.115, 3.0),
                ],
            ),
        )
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))
    first = output["timeline"][0]["timing"]
    second = output["timeline"][1]["timing"]

    assert first["start_sec"] == 0.0
    assert first["end_sec"] == 2.115
    assert first["duration_sec"] == 2.115
    assert first["local_end_sec"] == 2.115
    assert second["start_sec"] == 2.115
    assert second["local_start_sec"] == 2.115
    assert first["end_sec"] <= second["start_sec"]


def test_suspicious_gap_smoothing_does_not_move_next_scene_start() -> None:
    scenes = [
        scene("scene_001", "First.", scene_order=1),
        scene("scene_002", "Second.", scene_order=2),
    ]
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=5.0,
                paragraphs=[
                    paragraph("First.", 0.0, 1.0),
                    paragraph("Second.", 2.25, 3.0),
                ],
            ),
        )
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))
    second = output["timeline"][1]["timing"]

    assert second["start_sec"] == 2.25
    assert second["local_start_sec"] == 2.25


def test_suspicious_gap_smoothing_does_not_merge_section_boundaries() -> None:
    scenes = [
        scene("scene_001", "First.", section_key="01_HOOK", section="HOOK", section_order=1, scene_order=1),
        scene("scene_002", "Second.", section_key="02_INTRO", section="INTRO", section_order=2, scene_order=2),
    ]
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=5.0,
                paragraphs=[paragraph("First.", 0.0, 1.0)],
                path="alignments/01_HOOK_alignment_tmp.json",
            ),
        ),
        section_asset(
            "02_INTRO",
            "INTRO",
            2,
            alignment(
                duration=3.0,
                paragraphs=[paragraph("Second.", 0.0, 1.0)],
                path="alignments/02_INTRO_alignment_tmp.json",
            ),
        ),
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))

    assert output["timeline"][0]["timing"]["end_sec"] == 1.0
    assert output["timeline"][0]["timing"]["local_end_sec"] == 1.0
    assert output["timeline"][1]["timing"]["start_sec"] == 5.0


def test_contiguous_same_section_scenes_remain_unchanged() -> None:
    scenes = [
        scene("scene_001", "First.", scene_order=1),
        scene("scene_002", "Second.", scene_order=2),
    ]
    sections = [
        section_asset(
            "01_HOOK",
            "HOOK",
            1,
            alignment(
                duration=3.0,
                paragraphs=[
                    paragraph("First.", 0.0, 1.0),
                    paragraph("Second.", 1.0, 2.0),
                ],
            ),
        )
    ]

    output = build_timeline(scenes, sections, Path("scenes.json"))

    assert output["timeline"][0]["timing"] == {
        "start_sec": 0.0,
        "end_sec": 1.0,
        "duration_sec": 1.0,
        "local_start_sec": 0.0,
        "local_end_sec": 1.0,
    }
    assert output["timeline"][1]["timing"] == {
        "start_sec": 1.0,
        "end_sec": 2.0,
        "duration_sec": 1.0,
        "local_start_sec": 1.0,
        "local_end_sec": 2.0,
    }
