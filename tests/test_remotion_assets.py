import json
from pathlib import Path

import pytest

from synccut.remotion_assets import (
    prepare_remotion_assets_file,
    prepare_remotion_audio_assets,
)
from synccut.validators import SyncCutError


def write_audio(path: Path, content: bytes = b"audio") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def valid_props(audio_path: str = "source/01_HOOK.mp3") -> dict:
    return {
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
                "dialogue": {"text": "Dialogue", "paragraphs": ["Dialogue"]},
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


def prepare(props: dict, tmp_path: Path) -> tuple[dict, object]:
    return prepare_remotion_audio_assets(props, tmp_path / "remotion" / "props.json", tmp_path / "public")


def test_valid_audio_copy_creates_public_audio_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3", b"hook")

    _, result = prepare(valid_props(), tmp_path)

    destination = tmp_path / "public" / "audio" / "01_HOOK.mp3"
    assert destination.read_bytes() == b"hook"
    assert result.copied == 1
    assert result.reused == 0
    assert result.overwritten == 0
    assert result.audio_assets[0].public_path == "audio/01_HOOK.mp3"


def test_output_props_preserve_original_path_and_add_public_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3")

    updated, _ = prepare(valid_props(), tmp_path)

    assert updated["assets"]["audio"][0]["path"] == "source/01_HOOK.mp3"
    assert updated["assets"]["audio"][0]["public_path"] == "audio/01_HOOK.mp3"


def test_assets_sections_and_scenes_audio_are_updated_consistently(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3")

    updated, _ = prepare(valid_props(), tmp_path)

    assert updated["assets"]["audio"][0]["public_path"] == "audio/01_HOOK.mp3"
    assert updated["sections"][0]["audio"]["public_path"] == "audio/01_HOOK.mp3"
    assert updated["scenes"][0]["audio"]["public_path"] == "audio/01_HOOK.mp3"


def test_rerunning_with_identical_destination_reuses_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3", b"same")
    props = valid_props()

    prepare(props, tmp_path)
    _, result = prepare(props, tmp_path)

    assert result.copied == 0
    assert result.reused == 1
    assert result.overwritten == 0


def test_rerunning_with_changed_source_overwrites_destination(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    source = write_audio(tmp_path / "source" / "01_HOOK.mp3", b"old")
    props = valid_props()

    prepare(props, tmp_path)
    source.write_bytes(b"new")
    _, result = prepare(props, tmp_path)

    assert (tmp_path / "public" / "audio" / "01_HOOK.mp3").read_bytes() == b"new"
    assert result.copied == 0
    assert result.reused == 0
    assert result.overwritten == 1


def test_missing_source_audio_fails_clearly(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SyncCutError, match="source audio file not found"):
        prepare(valid_props(), tmp_path)


def test_malformed_props_missing_assets_audio_fails_clearly(tmp_path) -> None:
    with pytest.raises(SyncCutError, match="assets.audio must be an array"):
        prepare_remotion_audio_assets({"assets": {}}, tmp_path / "props.json", tmp_path / "public")


def test_collision_with_two_different_sources_mapping_to_same_destination_fails(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "first.mp3", b"first")
    write_audio(tmp_path / "source" / "second.mp3", b"second")
    props = valid_props("source/first.mp3")
    props["assets"]["audio"].append({"section_key": "01_HOOK", "path": "source/second.mp3"})

    with pytest.raises(SyncCutError, match="audio destination collision"):
        prepare(props, tmp_path)


def test_duplicate_entries_with_same_source_path_do_not_copy_twice(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3", b"hook")
    props = valid_props()
    props["assets"]["audio"].append({"section_key": "01_HOOK", "path": "source/01_HOOK.mp3"})

    _, result = prepare(props, tmp_path)

    assert result.copied == 1
    assert result.reused == 0
    assert result.overwritten == 0
    assert len(result.audio_assets) == 2


def test_prepare_remotion_assets_file_writes_two_space_json_with_trailing_newline(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    write_audio(tmp_path / "source" / "01_HOOK.mp3")
    props_path = tmp_path / "remotion" / "props.json"
    props_path.parent.mkdir(parents=True)
    props_path.write_text(json.dumps(valid_props()), encoding="utf-8")

    result = prepare_remotion_assets_file(props_path, tmp_path / "remotion" / "public")

    text = props_path.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert '\n  "metadata": {' in text
    written = json.loads(text)
    assert written["assets"]["audio"][0]["public_path"] == "audio/01_HOOK.mp3"
    assert result.copied == 1
