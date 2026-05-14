import base64
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from synccut.alignment_loader import load_alignment
from synccut.audio_generation import (
    alignment_json_from_response,
    generate_audio_from_manifest,
    load_narration_manifest_sections,
)
from synccut.elevenlabs_provider import ElevenLabsTimestampsResponse
from synccut.validators import SyncCutError


class FakeClient:
    def __init__(self, *, audio: bytes = b"mp3") -> None:
        self.audio = audio
        self.calls: list[dict[str, str]] = []

    def synthesize_with_timestamps(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str,
        output_format: str,
    ) -> ElevenLabsTimestampsResponse:
        self.calls.append(
            {
                "text": text,
                "voice_id": voice_id,
                "model_id": model_id,
                "output_format": output_format,
            }
        )
        return ElevenLabsTimestampsResponse(
            audio_base64=base64.b64encode(self.audio).decode("ascii"),
            alignment=alignment_for_text(text),
            normalized_alignment=None,
        )


class MissingAudioResponseClient:
    def synthesize_with_timestamps(self, **_kwargs):
        class Response:
            alignment = alignment_for_text("Hello world.")

        return Response()


class ArrayMismatchClient:
    def synthesize_with_timestamps(self, **_kwargs) -> ElevenLabsTimestampsResponse:
        return ElevenLabsTimestampsResponse(
            audio_base64=base64.b64encode(b"mp3").decode("ascii"),
            alignment={
                "characters": ["H", "i"],
                "character_start_times_seconds": [0.0],
                "character_end_times_seconds": [0.1, 0.2],
            },
            normalized_alignment=None,
        )


class TextMismatchClient:
    def synthesize_with_timestamps(self, **_kwargs) -> ElevenLabsTimestampsResponse:
        return ElevenLabsTimestampsResponse(
            audio_base64=base64.b64encode(b"mp3").decode("ascii"),
            alignment=alignment_for_text("Different text."),
            normalized_alignment=None,
        )


def alignment_for_text(text: str) -> dict:
    return {
        "characters": list(text),
        "character_start_times_seconds": [index * 0.1 for index, _ in enumerate(text)],
        "character_end_times_seconds": [
            (index + 1) * 0.1 for index, _ in enumerate(text)
        ],
    }


def write_manifest(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "metadata": {
            "schema_version": "0.1",
            "generated_by": "synccut prepare-narration",
            "source_scenes": "examples/scenes.json",
            "total_sections": 2,
            "total_scenes": 3,
        },
        "sections": [
            {
                "section_key": "01_HOOK",
                "section": "HOOK",
                "section_order": 1,
                "scene_ids": ["scene_001", "scene_002"],
                "scene_count": 2,
                "text_path": "01_HOOK.txt",
                "narration_text": "Hello world.\n\nSecond paragraph.",
                "text_hash": "sha256:" + "1" * 64,
                "expected_audio_path": "01_HOOK.mp3",
                "expected_alignment_path": "01_HOOK_alignment_tmp.json",
            },
            {
                "section_key": "02_INTRO",
                "section": "INTRO",
                "section_order": 2,
                "scene_ids": ["scene_003"],
                "scene_count": 1,
                "text_path": "02_INTRO.txt",
                "narration_text": "Intro text.",
                "text_hash": "sha256:" + "2" * 64,
                "expected_audio_path": "02_INTRO.mp3",
                "expected_alignment_path": "02_INTRO_alignment_tmp.json",
            },
        ],
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def fixed_clock() -> datetime:
    return datetime(2026, 5, 14, 10, 45, tzinfo=UTC)


def test_loads_phase29_manifest_sections(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "generated" / "narration" / "narration_manifest.json")

    sections = load_narration_manifest_sections(manifest_path)

    assert [section.section_key for section in sections] == ["01_HOOK", "02_INTRO"]
    assert sections[0].narration_text == "Hello world.\n\nSecond paragraph."
    assert sections[0].text_hash == "sha256:" + "1" * 64
    assert sections[0].expected_audio_path == "01_HOOK.mp3"
    assert sections[0].expected_alignment_path == "01_HOOK_alignment_tmp.json"


def test_dry_run_writes_nothing_and_does_not_call_client_or_env(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    client = FakeClient()

    def fail_env(_name: str) -> str | None:
        raise AssertionError("dry-run should not read environment")

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        dry_run=True,
        client=client,
        api_key_getter=fail_env,
    )

    assert result.dry_run is True
    assert result.written == 2
    assert result.reused == 0
    assert result.blocked == 0
    assert client.calls == []
    assert not (tmp_path / "audio").exists()
    assert not (tmp_path / "alignments").exists()


def test_missing_api_key_blocks_before_client_call(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="ELEVENLABS_API_KEY"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=tmp_path / "generated" / "audio_generation_manifest.json",
            api_key_getter=lambda _name: None,
        )

    assert not (tmp_path / "audio").exists()


def test_fake_provider_writes_mp3_and_alignment_json(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    client = FakeClient(audio=b"fake-mp3")
    metadata_path = tmp_path / "generated" / "audio_generation_manifest.json"

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        metadata_path=metadata_path,
        client=client,
        limit=1,
        clock=fixed_clock,
    )

    assert result.written == 1
    assert result.reused == 0
    assert (tmp_path / "audio" / "01_HOOK.mp3").read_bytes() == b"fake-mp3"
    alignment = json.loads(
        (tmp_path / "alignments" / "01_HOOK_alignment_tmp.json").read_text(
            encoding="utf-8"
        )
    )
    assert alignment["paragraphs"][0]["paragraph"] == "Hello world."
    assert alignment["paragraphs"][1]["paragraph"] == "Second paragraph."
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["sections"][0]["generated_at"] == "2026-05-14T10:45:00Z"


def test_generated_alignment_is_accepted_by_load_alignment(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        metadata_path=tmp_path / "metadata.json",
        client=FakeClient(),
        limit=1,
    )

    alignment = load_alignment(tmp_path / "alignments" / "01_HOOK_alignment_tmp.json")

    assert alignment.total_duration_sec > 0
    assert [paragraph.text for paragraph in alignment.paragraphs] == [
        "Hello world.",
        "Second paragraph.",
    ]
    assert alignment.words == []


def test_reuses_outputs_when_files_and_metadata_match(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    metadata_path = tmp_path / "metadata.json"
    generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        metadata_path=metadata_path,
        client=FakeClient(),
        limit=1,
        clock=fixed_clock,
    )
    client = FakeClient()

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        metadata_path=metadata_path,
        client=client,
        limit=1,
    )

    assert result.written == 0
    assert result.reused == 1
    assert client.calls == []


def test_blocks_when_outputs_exist_but_metadata_missing(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    audio_path = tmp_path / "audio" / "01_HOOK.mp3"
    audio_path.parent.mkdir()
    audio_path.write_bytes(b"existing")

    with pytest.raises(SyncCutError, match="--overwrite"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=tmp_path / "metadata.json",
            client=FakeClient(),
            limit=1,
        )


def test_blocks_when_metadata_mismatches_text_hash(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    audio_path = tmp_path / "audio" / "01_HOOK.mp3"
    alignment_path = tmp_path / "alignments" / "01_HOOK_alignment_tmp.json"
    audio_path.parent.mkdir()
    alignment_path.parent.mkdir()
    audio_path.write_bytes(b"existing")
    alignment_path.write_text("{}", encoding="utf-8")
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(
        json.dumps(
            {
                "metadata": {},
                "sections": [
                    {
                        "section_key": "01_HOOK",
                        "text_hash": "sha256:" + "9" * 64,
                        "provider": "elevenlabs",
                        "voice_id": "voice",
                        "model_id": "eleven_multilingual_v2",
                        "output_format": "mp3_44100_128",
                        "audio_path": str(audio_path),
                        "alignment_path": str(alignment_path),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(SyncCutError, match="--overwrite"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=metadata_path,
            client=FakeClient(),
            limit=1,
        )


def test_overwrite_replaces_planned_outputs(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")
    audio_path = tmp_path / "audio" / "01_HOOK.mp3"
    alignment_path = tmp_path / "alignments" / "01_HOOK_alignment_tmp.json"
    audio_path.parent.mkdir()
    alignment_path.parent.mkdir()
    audio_path.write_bytes(b"existing")
    alignment_path.write_text("{}", encoding="utf-8")

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        metadata_path=tmp_path / "metadata.json",
        client=FakeClient(audio=b"new"),
        limit=1,
        overwrite=True,
    )

    assert result.written == 1
    assert audio_path.read_bytes() == b"new"
    assert json.loads(alignment_path.read_text(encoding="utf-8"))["paragraphs"]


def test_limit_selects_first_n_sections(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        dry_run=True,
        limit=1,
    )

    assert [section.section_key for section in result.sections] == ["01_HOOK"]


def test_section_key_selects_requested_sections(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    result = generate_audio_from_manifest(
        manifest_path,
        provider="elevenlabs",
        audio_dir=tmp_path / "audio",
        alignment_dir=tmp_path / "alignments",
        voice_id="voice",
        dry_run=True,
        section_keys=["02_INTRO"],
    )

    assert [section.section_key for section in result.sections] == ["02_INTRO"]


def test_rejects_limit_and_section_key_together(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="--limit"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            dry_run=True,
            limit=1,
            section_keys=["01_HOOK"],
        )


def test_invalid_provider_is_rejected(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="unsupported audio provider"):
        generate_audio_from_manifest(
            manifest_path,
            provider="other",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            dry_run=True,
        )


def test_invalid_response_missing_audio_base64_rejected(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="missing audio_base64"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=tmp_path / "metadata.json",
            client=MissingAudioResponseClient(),
            limit=1,
        )


def test_invalid_response_alignment_array_mismatch_rejected(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="arrays must match length"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=tmp_path / "metadata.json",
            client=ArrayMismatchClient(),
            limit=1,
        )


def test_text_mismatch_rejected(tmp_path) -> None:
    manifest_path = write_manifest(tmp_path / "narration_manifest.json")

    with pytest.raises(SyncCutError, match="does not match narration text"):
        generate_audio_from_manifest(
            manifest_path,
            provider="elevenlabs",
            audio_dir=tmp_path / "audio",
            alignment_dir=tmp_path / "alignments",
            voice_id="voice",
            metadata_path=tmp_path / "metadata.json",
            client=TextMismatchClient(),
            limit=1,
        )


def test_alignment_normalization_uses_paragraph_boundaries() -> None:
    data = alignment_json_from_response(
        "First paragraph.\n\nSecond paragraph.",
        alignment_for_text("First paragraph.\n\nSecond paragraph."),
        section_key="01_HOOK",
    )

    assert [paragraph["paragraph"] for paragraph in data["paragraphs"]] == [
        "First paragraph.",
        "Second paragraph.",
    ]
    assert data["words"] == []
