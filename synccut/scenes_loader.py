from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from synccut.models import Dialogue, Scene, Visual
from synccut.validators import (
    SyncCutError,
    infer_section_key,
    normalize_visual_type,
    require_int,
    require_mapping,
    require_non_empty_string,
    require_present,
)


def load_scenes(path: Path) -> tuple[dict[str, Any], list[Scene]]:
    """Load, validate, and normalize scene input without mutating the file."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc

    root = require_mapping(raw, context=str(path))
    metadata = _load_metadata(root, path)
    raw_scenes = _load_scene_array(root, path)
    scenes = [_load_scene(item, index=index, path=path) for index, item in enumerate(raw_scenes)]

    total_scenes = metadata.get("total_scenes")
    if total_scenes is not None:
        if isinstance(total_scenes, bool) or not isinstance(total_scenes, int):
            raise SyncCutError(f"{path}: metadata.total_scenes must be an integer")
        if total_scenes != len(scenes):
            raise SyncCutError(
                f"{path}: metadata.total_scenes is {total_scenes} but scenes contains {len(scenes)} items"
            )

    return metadata, scenes


def _load_metadata(root: dict[str, Any], path: Path) -> dict[str, Any]:
    if "metadata" not in root:
        raise SyncCutError(f"{path}: missing metadata")
    return require_mapping(root["metadata"], context=f"{path}: metadata")


def _load_scene_array(root: dict[str, Any], path: Path) -> list[Any]:
    if "scenes" not in root:
        raise SyncCutError(f"{path}: missing scenes")
    scenes = root["scenes"]
    if not isinstance(scenes, list):
        raise SyncCutError(f"{path}: scenes must be an array")
    if not scenes:
        raise SyncCutError(f"{path}: scenes must not be empty")
    return scenes


def _load_scene(item: Any, *, index: int, path: Path) -> Scene:
    context = f"{path}: scenes[{index}]"
    raw_scene = require_mapping(item, context=context)

    scene_id = require_non_empty_string(
        require_present(raw_scene, "scene_id", context=context),
        context=f"{context}.scene_id",
    )
    scene_order = require_int(
        require_present(raw_scene, "scene_order", context=context),
        context=f"{context}.scene_order",
    )
    section = require_non_empty_string(
        require_present(raw_scene, "section", context=context),
        context=f"{context}.section",
    )
    section_order = require_int(
        require_present(raw_scene, "section_order", context=context),
        context=f"{context}.section_order",
    )
    section_key = _load_section_key(raw_scene, section_order=section_order, section=section, context=context)
    dialogue = _load_dialogue(
        require_present(raw_scene, "dialogue", context=context),
        context=f"{context}.dialogue",
    )
    visual = _load_visual(
        require_present(raw_scene, "visual", context=context),
        context=f"{context}.visual",
    )

    return Scene(
        scene_id=scene_id,
        scene_order=scene_order,
        section=section,
        section_order=section_order,
        section_key=section_key,
        dialogue=dialogue,
        visual=visual,
    )


def _load_section_key(
    raw_scene: dict[str, Any], *, section_order: int, section: str, context: str
) -> str:
    value = raw_scene.get("section_key")
    if value is None:
        return infer_section_key(section_order, section)
    return require_non_empty_string(value, context=f"{context}.section_key")


def _load_dialogue(value: Any, *, context: str) -> Dialogue:
    raw_dialogue = require_mapping(value, context=context)
    text = require_non_empty_string(
        require_present(raw_dialogue, "text", context=context),
        context=f"{context}.text",
    )

    if "paragraphs" not in raw_dialogue or raw_dialogue["paragraphs"] is None:
        paragraphs = [text]
    else:
        raw_paragraphs = raw_dialogue["paragraphs"]
        if not isinstance(raw_paragraphs, list):
            raise SyncCutError(f"{context}.paragraphs must be an array")
        if not raw_paragraphs:
            raise SyncCutError(f"{context}.paragraphs must not be empty")
        paragraphs = [
            require_non_empty_string(paragraph, context=f"{context}.paragraphs[{index}]")
            for index, paragraph in enumerate(raw_paragraphs)
        ]

    return Dialogue(text=text, paragraphs=paragraphs)


def _load_visual(value: Any, *, context: str) -> Visual:
    raw_visual = require_mapping(value, context=context)
    visual_type = normalize_visual_type(
        require_present(raw_visual, "type", context=context),
        context=context,
    )

    prompt = raw_visual.get("prompt")
    if prompt is not None and not isinstance(prompt, str):
        raise SyncCutError(f"{context}.prompt must be a string or null")

    return Visual(
        type=visual_type,
        prompt=prompt,
        data=raw_visual.get("data"),
    )
