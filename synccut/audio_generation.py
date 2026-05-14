from __future__ import annotations

import base64
import binascii
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Protocol

from synccut.elevenlabs_provider import (
    ELEVENLABS_API_KEY_ENV,
    ElevenLabsTimestampsClient,
    ElevenLabsTimestampsResponse,
)
from synccut.validators import (
    SyncCutError,
    require_int,
    require_mapping,
    require_non_empty_string,
    require_present,
)


DEFAULT_PROVIDER = "elevenlabs"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_METADATA_PATH = Path("generated/audio_generation_manifest.json")
METADATA_SCHEMA_VERSION = "0.1"
METADATA_GENERATOR = "synccut generate-audio"


class TimestampsClient(Protocol):
    def synthesize_with_timestamps(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str,
        output_format: str,
    ) -> ElevenLabsTimestampsResponse:
        ...


@dataclass(frozen=True)
class NarrationManifestSection:
    section_key: str
    section: str
    section_order: int
    scene_ids: list[str]
    scene_count: int
    text_path: str
    narration_text: str
    text_hash: str
    expected_audio_path: str
    expected_alignment_path: str


@dataclass(frozen=True)
class AudioGenerationSectionResult:
    section_key: str
    status: str
    audio_path: Path
    alignment_path: Path
    text_hash: str


@dataclass(frozen=True)
class AudioGenerationResult:
    provider: str
    sections: list[AudioGenerationSectionResult]
    metadata_path: Path
    dry_run: bool
    written: int
    reused: int
    blocked: int

    @property
    def generated(self) -> int:
        return self.written


def load_narration_manifest_sections(manifest_path: Path) -> list[NarrationManifestSection]:
    root = _load_json_file(manifest_path, label="narration manifest")
    sections_raw = require_present(root, "sections", context=str(manifest_path))
    if not isinstance(sections_raw, list):
        raise SyncCutError(f"{manifest_path}: sections must be an array")

    sections = [
        _load_manifest_section(item, context=f"{manifest_path}: sections[{index}]")
        for index, item in enumerate(sections_raw)
    ]
    if not sections:
        raise SyncCutError(f"{manifest_path}: sections must not be empty")
    return sections


def generate_audio_from_manifest(
    manifest_path: Path,
    *,
    provider: str,
    audio_dir: Path,
    alignment_dir: Path,
    voice_id: str | None,
    model_id: str = DEFAULT_MODEL_ID,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    metadata_path: Path = DEFAULT_METADATA_PATH,
    dry_run: bool = False,
    overwrite: bool = False,
    limit: int | None = None,
    section_keys: list[str] | None = None,
    api_key_getter: Callable[[str], str | None] | None = None,
    clock: Callable[[], datetime] | None = None,
    client: TimestampsClient | None = None,
) -> AudioGenerationResult:
    if provider != DEFAULT_PROVIDER:
        raise SyncCutError(f"unsupported audio provider '{provider}'; expected elevenlabs")
    if not voice_id:
        raise SyncCutError("--voice-id is required for provider elevenlabs")
    if limit is not None and section_keys:
        raise SyncCutError("--limit cannot be used with --section-key")
    if limit is not None and limit < 1:
        raise SyncCutError("--limit must be greater than or equal to 1")

    sections = _select_sections(
        load_narration_manifest_sections(manifest_path),
        limit=limit,
        section_keys=section_keys or [],
    )
    metadata = _load_generation_metadata(metadata_path)
    plans = [
        _section_plan(
            section=section,
            provider=provider,
            audio_dir=audio_dir,
            alignment_dir=alignment_dir,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
            metadata=metadata,
        )
        for section in sections
    ]

    results: list[AudioGenerationSectionResult] = []
    blocked = 0
    reused = 0
    would_generate = 0
    for plan in plans:
        if plan["status"] == "reused":
            reused += 1
        elif plan["status"] == "blocked":
            blocked += 1
        else:
            would_generate += 1
        results.append(
            AudioGenerationSectionResult(
                section_key=plan["section"].section_key,
                status=plan["status"],
                audio_path=plan["audio_path"],
                alignment_path=plan["alignment_path"],
                text_hash=plan["section"].text_hash,
            )
        )

    if dry_run:
        return AudioGenerationResult(
            provider=provider,
            sections=results,
            metadata_path=metadata_path,
            dry_run=True,
            written=would_generate,
            reused=reused,
            blocked=blocked,
        )

    blocked_plans = [plan for plan in plans if plan["status"] == "blocked"]
    if blocked_plans and not overwrite:
        conflicts = ", ".join(plan["section"].section_key for plan in blocked_plans)
        raise SyncCutError(
            f"{conflicts}: output exists but metadata does not match; "
            "rerun with --overwrite to replace"
        )

    if client is None:
        api_key_getter = api_key_getter or os.environ.get
        api_key = api_key_getter(ELEVENLABS_API_KEY_ENV)
        if not api_key:
            raise SyncCutError(
                f"{ELEVENLABS_API_KEY_ENV} is required for ElevenLabs generation"
            )
        client = ElevenLabsTimestampsClient(api_key_getter=lambda _name: api_key)

    audio_dir.mkdir(parents=True, exist_ok=True)
    alignment_dir.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = _base_metadata(
        provider=provider,
        manifest_path=manifest_path,
        audio_dir=audio_dir,
        alignment_dir=alignment_dir,
        model_id=model_id,
        output_format=output_format,
        existing=metadata,
    )
    metadata_entries = {
        entry.get("section_key"): entry
        for entry in metadata.get("sections", [])
        if isinstance(entry, dict)
    }

    final_results: list[AudioGenerationSectionResult] = []
    written = 0
    reused_count = 0
    now = clock or (lambda: datetime.now(UTC))

    for plan in plans:
        section = plan["section"]
        audio_path = plan["audio_path"]
        alignment_path = plan["alignment_path"]
        if plan["status"] == "reused" and not overwrite:
            reused_count += 1
            final_results.append(
                AudioGenerationSectionResult(
                    section_key=section.section_key,
                    status="reused",
                    audio_path=audio_path,
                    alignment_path=alignment_path,
                    text_hash=section.text_hash,
                )
            )
            continue

        response = client.synthesize_with_timestamps(
            text=section.narration_text,
            voice_id=voice_id,
            model_id=model_id,
            output_format=output_format,
        )
        audio_bytes = _decode_audio(
            _response_audio_base64(response, section_key=section.section_key),
            section_key=section.section_key,
        )
        alignment_json = alignment_json_from_response(
            section.narration_text,
            _response_alignment(response, section_key=section.section_key),
            section_key=section.section_key,
        )

        _write_bytes_atomic(audio_path, audio_bytes)
        _write_json_atomic(alignment_path, alignment_json)
        metadata_entries[section.section_key] = {
            "section_key": section.section_key,
            "status": "written",
            "text_hash": section.text_hash,
            "provider": provider,
            "voice_id": voice_id,
            "model_id": model_id,
            "output_format": output_format,
            "audio_path": str(audio_path),
            "alignment_path": str(alignment_path),
            "generated_at": _format_timestamp(now()),
        }
        metadata["sections"] = [
            metadata_entries[key] for key in sorted(metadata_entries) if key is not None
        ]
        _write_json_atomic(metadata_path, metadata)
        written += 1
        final_results.append(
            AudioGenerationSectionResult(
                section_key=section.section_key,
                status="written",
                audio_path=audio_path,
                alignment_path=alignment_path,
                text_hash=section.text_hash,
            )
        )

    return AudioGenerationResult(
        provider=provider,
        sections=final_results,
        metadata_path=metadata_path,
        dry_run=False,
        written=written,
        reused=reused_count,
        blocked=0,
    )


def alignment_json_from_response(
    narration_text: str,
    alignment: dict[str, Any],
    *,
    section_key: str,
) -> dict[str, Any]:
    raw = require_mapping(alignment, context=f"{section_key}: alignment")
    characters = _required_list(raw, "characters", context=f"{section_key}: alignment")
    starts = _required_list(
        raw,
        "character_start_times_seconds",
        context=f"{section_key}: alignment",
    )
    ends = _required_list(
        raw,
        "character_end_times_seconds",
        context=f"{section_key}: alignment",
    )
    if not (len(characters) == len(starts) == len(ends)):
        raise SyncCutError(f"{section_key}: alignment character timing arrays must match length")
    if not characters:
        raise SyncCutError(f"{section_key}: alignment characters must not be empty")
    if not all(isinstance(character, str) for character in characters):
        raise SyncCutError(f"{section_key}: alignment characters must be strings")

    provider_text = "".join(characters).replace("\r\n", "\n").replace("\r", "\n")
    normalized_narration = narration_text.replace("\r\n", "\n").replace("\r", "\n")
    if provider_text != normalized_narration:
        raise SyncCutError(
            f"{section_key}: provider alignment text does not match narration text"
        )

    paragraphs = []
    max_end = 0.0
    for index, (paragraph, start_index, end_index) in enumerate(
        _paragraph_spans(normalized_narration)
    ):
        non_ws_indexes = [
            char_index
            for char_index in range(start_index, end_index)
            if not normalized_narration[char_index].isspace()
        ]
        if not non_ws_indexes:
            raise SyncCutError(f"{section_key}: paragraph {index} has no timed characters")
        start = _timing_value(starts[non_ws_indexes[0]], context=f"{section_key}: start")
        end = _timing_value(ends[non_ws_indexes[-1]], context=f"{section_key}: end")
        if end < start:
            raise SyncCutError(f"{section_key}: paragraph {index} end is before start")
        max_end = max(max_end, end)
        paragraphs.append(
            {
                "paragraph": paragraph,
                "start": start,
                "end": end,
                "sentences": [],
            }
        )

    if not paragraphs:
        raise SyncCutError(f"{section_key}: no paragraphs found in narration text")

    final_character_end = max(
        _timing_value(value, context=f"{section_key}: end") for value in ends
    )
    return {
        "total_duration_sec": max(max_end, final_character_end),
        "paragraphs": paragraphs,
        "words": [],
    }


def _load_manifest_section(value: Any, *, context: str) -> NarrationManifestSection:
    raw = require_mapping(value, context=context)
    scene_ids_raw = require_present(raw, "scene_ids", context=context)
    if not isinstance(scene_ids_raw, list) or not all(
        isinstance(scene_id, str) and scene_id for scene_id in scene_ids_raw
    ):
        raise SyncCutError(f"{context}.scene_ids must be an array of strings")

    section_key = require_non_empty_string(
        require_present(raw, "section_key", context=context),
        context=f"{context}.section_key",
    )
    text_path = require_non_empty_string(
        require_present(raw, "text_path", context=context),
        context=f"{context}.text_path",
    )
    expected_audio_path = require_non_empty_string(
        require_present(raw, "expected_audio_path", context=context),
        context=f"{context}.expected_audio_path",
    )
    expected_alignment_path = require_non_empty_string(
        require_present(raw, "expected_alignment_path", context=context),
        context=f"{context}.expected_alignment_path",
    )
    _validate_package_filename(text_path, section_key=section_key)
    _validate_package_filename(expected_audio_path, section_key=section_key)
    _validate_package_filename(expected_alignment_path, section_key=section_key)

    return NarrationManifestSection(
        section_key=section_key,
        section=require_non_empty_string(
            require_present(raw, "section", context=context),
            context=f"{context}.section",
        ),
        section_order=require_int(
            require_present(raw, "section_order", context=context),
            context=f"{context}.section_order",
        ),
        scene_ids=scene_ids_raw,
        scene_count=require_int(
            require_present(raw, "scene_count", context=context),
            context=f"{context}.scene_count",
        ),
        text_path=text_path,
        narration_text=require_non_empty_string(
            require_present(raw, "narration_text", context=context),
            context=f"{context}.narration_text",
        ),
        text_hash=require_non_empty_string(
            require_present(raw, "text_hash", context=context),
            context=f"{context}.text_hash",
        ),
        expected_audio_path=expected_audio_path,
        expected_alignment_path=expected_alignment_path,
    )


def _select_sections(
    sections: list[NarrationManifestSection],
    *,
    limit: int | None,
    section_keys: list[str],
) -> list[NarrationManifestSection]:
    if section_keys:
        by_key = {section.section_key: section for section in sections}
        selected = []
        for key in section_keys:
            if key not in by_key:
                raise SyncCutError(f"unknown section key '{key}'")
            selected.append(by_key[key])
        return selected
    if limit is not None:
        return sections[:limit]
    return sections


def _section_plan(
    *,
    section: NarrationManifestSection,
    provider: str,
    audio_dir: Path,
    alignment_dir: Path,
    voice_id: str,
    model_id: str,
    output_format: str,
    metadata: dict[str, Any] | None,
) -> dict[str, Any]:
    audio_path = audio_dir / section.expected_audio_path
    alignment_path = alignment_dir / section.expected_alignment_path
    matching = _matching_metadata_entry(
        section=section,
        metadata=metadata,
        provider=provider,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
        audio_path=audio_path,
        alignment_path=alignment_path,
    )
    audio_exists = audio_path.exists()
    alignment_exists = alignment_path.exists()
    if audio_exists and alignment_exists and matching:
        status = "reused"
    elif audio_exists or alignment_exists:
        status = "blocked"
    else:
        status = "would_generate"
    return {
        "section": section,
        "audio_path": audio_path,
        "alignment_path": alignment_path,
        "status": status,
    }


def _matching_metadata_entry(
    *,
    section: NarrationManifestSection,
    metadata: dict[str, Any] | None,
    provider: str,
    voice_id: str,
    model_id: str,
    output_format: str,
    audio_path: Path,
    alignment_path: Path,
) -> bool:
    if metadata is None:
        return False
    sections_raw = metadata.get("sections", [])
    if not isinstance(sections_raw, list):
        return False
    for entry in sections_raw:
        if not isinstance(entry, dict):
            continue
        if entry.get("section_key") != section.section_key:
            continue
        return (
            entry.get("text_hash") == section.text_hash
            and entry.get("provider") == provider
            and entry.get("voice_id") == voice_id
            and entry.get("model_id") == model_id
            and entry.get("output_format") == output_format
            and entry.get("audio_path") == str(audio_path)
            and entry.get("alignment_path") == str(alignment_path)
        )
    return False


def _base_metadata(
    *,
    provider: str,
    manifest_path: Path,
    audio_dir: Path,
    alignment_dir: Path,
    model_id: str,
    output_format: str,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    entries = existing.get("sections", []) if existing else []
    if not isinstance(entries, list):
        entries = []
    return {
        "metadata": {
            "schema_version": METADATA_SCHEMA_VERSION,
            "generated_by": METADATA_GENERATOR,
            "provider": provider,
            "source_manifest": str(manifest_path),
            "audio_dir": str(audio_dir),
            "alignment_dir": str(alignment_dir),
            "model_id": model_id,
            "output_format": output_format,
        },
        "sections": [entry for entry in entries if isinstance(entry, dict)],
    }


def _load_generation_metadata(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json_file(path, label="audio generation metadata")


def _load_json_file(path: Path, *, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: {label} file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc
    return require_mapping(raw, context=str(path))


def _decode_audio(value: str, *, section_key: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise SyncCutError(f"{section_key}: invalid audio_base64 in provider response") from exc


def _response_audio_base64(response: Any, *, section_key: str) -> str:
    value = getattr(response, "audio_base64", None)
    if not isinstance(value, str) or not value.strip():
        raise SyncCutError(f"{section_key}: provider response missing audio_base64")
    return value


def _response_alignment(response: Any, *, section_key: str) -> dict[str, Any]:
    value = getattr(response, "alignment", None)
    if not isinstance(value, dict):
        raise SyncCutError(f"{section_key}: provider response missing alignment")
    return value


def _required_list(raw: dict[str, Any], key: str, *, context: str) -> list[Any]:
    value = require_present(raw, key, context=context)
    if not isinstance(value, list):
        raise SyncCutError(f"{context}.{key} must be an array")
    return value


def _paragraph_spans(text: str) -> list[tuple[str, int, int]]:
    spans: list[tuple[str, int, int]] = []
    start = 0
    for part in text.split("\n\n"):
        end = start + len(part)
        if part:
            spans.append((part, start, end))
        start = end + 2
    return spans


def _timing_value(value: Any, *, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SyncCutError(f"{context} must be numeric")
    return float(value)


def _validate_package_filename(filename: str, *, section_key: str) -> None:
    path = Path(filename)
    if path.name != filename or path.is_absolute() or ".." in path.parts:
        raise SyncCutError(f"{section_key}: output filename is not safe: {filename}")


def _write_bytes_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
