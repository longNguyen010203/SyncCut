from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from synccut.models import AlignmentParagraph, AlignmentSection, Scene, SectionAsset, TimedText
from synccut.validators import (
    SyncCutError,
    require_mapping,
    require_non_empty_string,
    require_number,
    require_present,
)


def discover_audio_file(section_key: str, audio_dir: Path) -> Path:
    exact = audio_dir / f"{section_key}.mp3"
    if exact.exists():
        return exact

    matches = sorted(audio_dir.glob(f"{section_key}*.mp3"))
    if not matches:
        raise SyncCutError(f"{section_key}: no audio file found in {audio_dir}")
    if len(matches) > 1:
        filenames = ", ".join(path.name for path in matches)
        raise SyncCutError(f"{section_key}: ambiguous audio files in {audio_dir}: {filenames}")
    return matches[0]


def discover_alignment_file(section_key: str, alignment_dir: Path) -> Path:
    matches = sorted(alignment_dir.glob(f"{section_key}_alignment*.json"))
    if not matches:
        raise SyncCutError(f"{section_key}: no alignment file found in {alignment_dir}")
    if len(matches) > 1:
        filenames = ", ".join(path.name for path in matches)
        raise SyncCutError(
            f"{section_key}: ambiguous alignment files in {alignment_dir}: {filenames}"
        )
    return matches[0]


def load_alignment(path: Path) -> AlignmentSection:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc

    root = require_mapping(raw, context=str(path))
    duration = require_number(
        require_present(root, "total_duration_sec", context=str(path)),
        context=f"{path}: total_duration_sec",
    )
    if duration <= 0:
        raise SyncCutError(f"{path}: total_duration_sec must be positive")

    paragraphs = _load_paragraphs(
        require_present(root, "paragraphs", context=str(path)),
        path=path,
    )
    words = _load_words(root.get("words", []), context=f"{path}: words")

    return AlignmentSection(
        path=str(path),
        total_duration_sec=duration,
        paragraphs=paragraphs,
        words=words,
    )


def load_section_assets(
    scenes: list[Scene], audio_dir: Path, alignment_dir: Path
) -> list[SectionAsset]:
    sections: dict[str, tuple[str, int]] = {}
    for scene in scenes:
        sections.setdefault(scene.section_key, (scene.section, scene.section_order))

    assets: list[SectionAsset] = []
    for section_key, (section, section_order) in sorted(
        sections.items(), key=lambda item: (item[1][1], item[0])
    ):
        audio_path = discover_audio_file(section_key, audio_dir)
        alignment_path = discover_alignment_file(section_key, alignment_dir)
        alignment = load_alignment(alignment_path)
        assets.append(
            SectionAsset(
                section_key=section_key,
                section=section,
                section_order=section_order,
                audio_path=str(audio_path),
                alignment_path=str(alignment_path),
                alignment=alignment,
            )
        )
    return assets


def _load_paragraphs(value: Any, *, path: Path) -> list[AlignmentParagraph]:
    if not isinstance(value, list):
        raise SyncCutError(f"{path}: paragraphs must be an array")
    if not value:
        raise SyncCutError(f"{path}: paragraphs must not be empty")

    return [
        _load_paragraph(paragraph, context=f"{path}: paragraphs[{index}]")
        for index, paragraph in enumerate(value)
    ]


def _load_paragraph(value: Any, *, context: str) -> AlignmentParagraph:
    raw = require_mapping(value, context=context)
    text = require_non_empty_string(
        require_present(raw, "paragraph", context=context),
        context=f"{context}.paragraph",
    )
    start, end = _load_timing(raw, context=context)
    sentences = _load_sentences(raw.get("sentences", []), context=f"{context}.sentences")
    return AlignmentParagraph(text=text, start=start, end=end, sentences=sentences)


def _load_sentences(value: Any, *, context: str) -> list[TimedText]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SyncCutError(f"{context} must be an array")

    sentences: list[TimedText] = []
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        raw = require_mapping(item, context=item_context)
        text = require_non_empty_string(
            require_present(raw, "sentence", context=item_context),
            context=f"{item_context}.sentence",
        )
        start, end = _load_timing(raw, context=item_context)
        sentences.append(TimedText(text=text, start=start, end=end))
        _load_words(raw.get("words", []), context=f"{item_context}.words")
    return sentences


def _load_words(value: Any, *, context: str) -> list[TimedText]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise SyncCutError(f"{context} must be an array")

    words: list[TimedText] = []
    for index, item in enumerate(value):
        item_context = f"{context}[{index}]"
        raw = require_mapping(item, context=item_context)
        text = require_non_empty_string(
            require_present(raw, "word", context=item_context),
            context=f"{item_context}.word",
        )
        start, end = _load_timing(raw, context=item_context)
        words.append(TimedText(text=text, start=start, end=end))
    return words


def _load_timing(raw: dict[str, Any], *, context: str) -> tuple[float, float]:
    start = require_number(
        require_present(raw, "start", context=context),
        context=f"{context}.start",
    )
    end = require_number(
        require_present(raw, "end", context=context),
        context=f"{context}.end",
    )
    if end < start:
        raise SyncCutError(f"{context}: end must be greater than or equal to start")
    return start, end
