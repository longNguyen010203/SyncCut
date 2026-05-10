import json
from copy import deepcopy

import pytest

from synccut.scenes_loader import load_scenes
from synccut.validators import SyncCutError


def valid_payload() -> dict:
    return {
        "metadata": {"schema_version": "1.1", "total_scenes": 1},
        "scenes": [
            {
                "scene_id": "scene_001",
                "scene_order": 1,
                "section": "HOOK",
                "section_order": 1,
                "section_key": "01_HOOK",
                "dialogue": {
                    "text": "Every iPhone in your pocket.",
                    "paragraphs": ["Every iPhone in your pocket."],
                },
                "visual": {
                    "type": "AI_VIDEO",
                    "prompt": "Close-up of a silicon wafer.",
                    "data": {"camera": "macro"},
                },
            }
        ],
    }


def write_json(tmp_path, payload: dict):
    path = tmp_path / "scenes.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_valid_scenes_json_loads_successfully(tmp_path) -> None:
    path = write_json(tmp_path, valid_payload())

    metadata, scenes = load_scenes(path)

    assert metadata["schema_version"] == "1.1"
    assert len(scenes) == 1
    assert scenes[0].scene_id == "scene_001"
    assert scenes[0].dialogue.text == "Every iPhone in your pocket."
    assert scenes[0].dialogue.paragraphs == ["Every iPhone in your pocket."]
    assert scenes[0].visual.prompt == "Close-up of a silicon wafer."
    assert scenes[0].visual.data == {"camera": "macro"}


def test_missing_metadata_fails_clearly(tmp_path) -> None:
    payload = valid_payload()
    payload.pop("metadata")
    path = write_json(tmp_path, payload)

    with pytest.raises(SyncCutError, match="missing metadata"):
        load_scenes(path)


def test_missing_scenes_fails_clearly(tmp_path) -> None:
    payload = valid_payload()
    payload.pop("scenes")
    path = write_json(tmp_path, payload)

    with pytest.raises(SyncCutError, match="missing scenes"):
        load_scenes(path)


def test_empty_scenes_fails_clearly(tmp_path) -> None:
    payload = valid_payload()
    payload["metadata"]["total_scenes"] = 0
    payload["scenes"] = []
    path = write_json(tmp_path, payload)

    with pytest.raises(SyncCutError, match="scenes must not be empty"):
        load_scenes(path)


@pytest.mark.parametrize(
    "field",
    ["scene_id", "scene_order", "section", "section_order", "dialogue", "visual"],
)
def test_missing_required_scene_fields_fail_clearly(tmp_path, field: str) -> None:
    payload = valid_payload()
    payload["scenes"][0].pop(field)
    path = write_json(tmp_path, payload)

    with pytest.raises(SyncCutError, match=f"missing required field '{field}'"):
        load_scenes(path)


def test_b_roll_normalizes_to_b_roll(tmp_path) -> None:
    payload = valid_payload()
    payload["scenes"][0]["visual"]["type"] = "B-ROLL"
    path = write_json(tmp_path, payload)

    _, scenes = load_scenes(path)

    assert scenes[0].visual.type == "B_ROLL"


def test_unsupported_visual_type_fails_clearly(tmp_path) -> None:
    payload = valid_payload()
    payload["scenes"][0]["visual"]["type"] = "PHOTO"
    path = write_json(tmp_path, payload)

    with pytest.raises(SyncCutError, match="unsupported visual type 'PHOTO'"):
        load_scenes(path)


def test_section_key_is_inferred_when_missing(tmp_path) -> None:
    payload = valid_payload()
    payload["scenes"][0].pop("section_key")
    payload["scenes"][0]["section"] = "Mechanism 1"
    payload["scenes"][0]["section_order"] = 3
    path = write_json(tmp_path, payload)

    _, scenes = load_scenes(path)

    assert scenes[0].section_key == "03_MECHANISM_1"


def test_input_json_file_content_is_not_mutated(tmp_path) -> None:
    payload = valid_payload()
    payload["scenes"][0]["visual"]["type"] = "B-ROLL"
    original_payload = deepcopy(payload)
    path = write_json(tmp_path, payload)
    original_content = path.read_text(encoding="utf-8")

    load_scenes(path)

    assert path.read_text(encoding="utf-8") == original_content
    assert json.loads(path.read_text(encoding="utf-8")) == original_payload
