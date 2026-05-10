import json

import pytest

from synccut.alignment_loader import (
    discover_alignment_file,
    discover_audio_file,
    load_alignment,
    load_section_assets,
)
from synccut.models import Dialogue, Scene, Visual
from synccut.validators import SyncCutError


def alignment_payload() -> dict:
    return {
        "total_duration_sec": 2.5,
        "paragraphs": [
            {
                "paragraph": "Hello world.",
                "start": 0.0,
                "end": 1.2,
                "sentences": [
                    {
                        "sentence": "Hello world.",
                        "start": 0.0,
                        "end": 1.2,
                        "words": [
                            {"word": "Hello", "start": 0.0, "end": 0.5},
                            {"word": "world.", "start": 0.6, "end": 1.2},
                        ],
                    }
                ],
            }
        ],
        "words": [
            {"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "world.", "start": 0.6, "end": 1.2},
        ],
    }


def write_alignment(tmp_path, name: str = "01_HOOK_alignment_tmp.json", payload: dict | None = None):
    path = tmp_path / name
    path.write_text(json.dumps(payload if payload is not None else alignment_payload()), encoding="utf-8")
    return path


def make_scene(section_key: str, section: str, section_order: int, scene_order: int) -> Scene:
    return Scene(
        scene_id=f"scene_{scene_order:03d}",
        scene_order=scene_order,
        section=section,
        section_order=section_order,
        section_key=section_key,
        dialogue=Dialogue(text="Hello world.", paragraphs=["Hello world."]),
        visual=Visual(type="AI_VIDEO", prompt=None, data=None),
    )


def test_valid_alignment_loading(tmp_path) -> None:
    path = write_alignment(tmp_path)

    alignment = load_alignment(path)

    assert alignment.path == str(path)
    assert alignment.total_duration_sec == 2.5
    assert alignment.paragraphs[0].text == "Hello world."
    assert alignment.paragraphs[0].sentences[0].text == "Hello world."
    assert alignment.words[1].text == "world."


def test_malformed_json_fails_clearly(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(SyncCutError, match="malformed JSON"):
        load_alignment(path)


def test_missing_paragraphs_fails_clearly(tmp_path) -> None:
    payload = alignment_payload()
    payload.pop("paragraphs")
    path = write_alignment(tmp_path, payload=payload)

    with pytest.raises(SyncCutError, match="missing required field 'paragraphs'"):
        load_alignment(path)


def test_non_positive_total_duration_fails_clearly(tmp_path) -> None:
    payload = alignment_payload()
    payload["total_duration_sec"] = 0
    path = write_alignment(tmp_path, payload=payload)

    with pytest.raises(SyncCutError, match="total_duration_sec must be positive"):
        load_alignment(path)


def test_empty_paragraphs_fails_clearly(tmp_path) -> None:
    payload = alignment_payload()
    payload["paragraphs"] = []
    path = write_alignment(tmp_path, payload=payload)

    with pytest.raises(SyncCutError, match="paragraphs must not be empty"):
        load_alignment(path)


def test_missing_paragraph_timing_fails_clearly(tmp_path) -> None:
    payload = alignment_payload()
    payload["paragraphs"][0].pop("start")
    path = write_alignment(tmp_path, payload=payload)

    with pytest.raises(SyncCutError, match="missing required field 'start'"):
        load_alignment(path)


def test_reversed_paragraph_timing_fails_clearly(tmp_path) -> None:
    payload = alignment_payload()
    payload["paragraphs"][0]["start"] = 2.0
    payload["paragraphs"][0]["end"] = 1.0
    path = write_alignment(tmp_path, payload=payload)

    with pytest.raises(SyncCutError, match="end must be greater than or equal to start"):
        load_alignment(path)


def test_exact_audio_discovery(tmp_path) -> None:
    audio = tmp_path / "01_HOOK.mp3"
    audio.write_bytes(b"placeholder")

    assert discover_audio_file("01_HOOK", tmp_path) == audio


def test_fallback_audio_discovery(tmp_path) -> None:
    audio = tmp_path / "01_HOOK_take1.mp3"
    audio.write_bytes(b"placeholder")

    assert discover_audio_file("01_HOOK", tmp_path) == audio


def test_missing_audio_fails_clearly(tmp_path) -> None:
    with pytest.raises(SyncCutError, match="no audio file found"):
        discover_audio_file("01_HOOK", tmp_path)


def test_ambiguous_audio_fails_clearly(tmp_path) -> None:
    (tmp_path / "01_HOOK_a.mp3").write_bytes(b"a")
    (tmp_path / "01_HOOK_b.mp3").write_bytes(b"b")

    with pytest.raises(SyncCutError, match="01_HOOK_a.mp3, 01_HOOK_b.mp3"):
        discover_audio_file("01_HOOK", tmp_path)


def test_section_key_alignment_discovery(tmp_path) -> None:
    alignment = write_alignment(tmp_path)

    assert discover_alignment_file("01_HOOK", tmp_path) == alignment


def test_missing_alignment_fails_clearly(tmp_path) -> None:
    with pytest.raises(SyncCutError, match="no alignment file found"):
        discover_alignment_file("01_HOOK", tmp_path)


def test_ambiguous_alignment_fails_clearly(tmp_path) -> None:
    write_alignment(tmp_path, name="01_HOOK_alignment_a.json")
    write_alignment(tmp_path, name="01_HOOK_alignment_b.json")

    with pytest.raises(SyncCutError, match="01_HOOK_alignment_a.json, 01_HOOK_alignment_b.json"):
        discover_alignment_file("01_HOOK", tmp_path)


def test_load_section_assets_returns_sorted_unique_section_assets(tmp_path) -> None:
    audio_dir = tmp_path / "audio"
    alignment_dir = tmp_path / "alignments"
    audio_dir.mkdir()
    alignment_dir.mkdir()
    for section_key in ["01_HOOK", "02_INTRO"]:
        (audio_dir / f"{section_key}.mp3").write_bytes(b"placeholder")
        write_alignment(alignment_dir, name=f"{section_key}_alignment_tmp.json")

    scenes = [
        make_scene("02_INTRO", "INTRO", 2, 2),
        make_scene("01_HOOK", "HOOK", 1, 1),
        make_scene("01_HOOK", "HOOK", 1, 3),
    ]

    assets = load_section_assets(scenes, audio_dir, alignment_dir)

    assert [asset.section_key for asset in assets] == ["01_HOOK", "02_INTRO"]
    assert assets[0].section == "HOOK"
    assert assets[0].section_order == 1
    assert assets[0].audio_path == str(audio_dir / "01_HOOK.mp3")
    assert assets[0].alignment.total_duration_sec == 2.5


def test_placeholder_mp3_files_work_without_audio_decoding(tmp_path) -> None:
    audio = tmp_path / "01_HOOK.mp3"
    audio.write_bytes(b"not a real mp3")

    assert discover_audio_file("01_HOOK", tmp_path) == audio
