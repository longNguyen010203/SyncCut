from __future__ import annotations

import re
import string
from typing import Any


SUPPORTED_VISUAL_TYPES = {
    "AI_VIDEO",
    "B_ROLL",
    "CHART",
    "COMPARISON_CARD",
    "TABLE",
    "SHARE_BREAKDOWN",
    "TIMELINE",
}


class SyncCutError(Exception):
    """Expected user-facing SyncCut error."""


def normalize_visual_type(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SyncCutError(f"{context}: visual.type must be a non-empty string")

    normalized = value.strip().upper().replace("-", "_")
    if normalized not in SUPPORTED_VISUAL_TYPES:
        expected = ", ".join(sorted(SUPPORTED_VISUAL_TYPES))
        raise SyncCutError(
            f"{context}: unsupported visual type '{value}'; expected one of {expected}"
        )
    return normalized


def infer_section_key(section_order: int, section: str) -> str:
    section_name = re.sub(r"[^A-Za-z0-9]+", "_", section.strip().upper()).strip("_")
    if not section_name:
        raise SyncCutError("section: cannot infer section_key from an empty section")
    return f"{section_order:02d}_{section_name}"


def require_mapping(value: Any, *, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SyncCutError(f"{context} must be an object")
    return value


def require_non_empty_string(value: Any, *, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SyncCutError(f"{context} must be a non-empty string")
    return value


def require_int(value: Any, *, context: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SyncCutError(f"{context} must be an integer")
    return value


def require_number(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SyncCutError(f"{context} must be numeric")
    return float(value)


def require_present(mapping: dict[str, Any], key: str, *, context: str) -> Any:
    if key not in mapping:
        raise SyncCutError(f"{context}: missing required field '{key}'")
    return mapping[key]


def normalize_match_text(value: str) -> str:
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u27f6": " ",
    }
    normalized = value
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"\s+", " ", normalized.strip().lower())
    return normalized


def normalize_match_word(value: str) -> str:
    normalized = normalize_match_text(value)
    normalized = normalized.strip(string.punctuation)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized
