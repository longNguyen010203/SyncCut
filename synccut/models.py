from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Dialogue:
    text: str
    paragraphs: list[str]


@dataclass(frozen=True)
class Visual:
    type: str
    prompt: str | None
    data: Any


@dataclass(frozen=True)
class Scene:
    scene_id: str
    scene_order: int
    section: str
    section_order: int
    section_key: str
    dialogue: Dialogue
    visual: Visual


@dataclass(frozen=True)
class TimedText:
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class AlignmentParagraph:
    text: str
    start: float
    end: float
    sentences: list[TimedText]


@dataclass(frozen=True)
class AlignmentSection:
    path: str
    total_duration_sec: float
    paragraphs: list[AlignmentParagraph]
    words: list[TimedText]


@dataclass(frozen=True)
class SectionAsset:
    section_key: str
    section: str
    section_order: int
    audio_path: str
    alignment_path: str
    alignment: AlignmentSection


@dataclass(frozen=True)
class MatchResult:
    local_start_sec: float
    local_end_sec: float
    match_method: str
    matched_units: list[str]
