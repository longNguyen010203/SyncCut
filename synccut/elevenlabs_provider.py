from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string


ELEVENLABS_API_KEY_ENV = "ELEVENLABS_API_KEY"
ELEVENLABS_TIMESTAMPS_URL = (
    "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
)


@dataclass(frozen=True)
class ElevenLabsTimestampsResponse:
    audio_base64: str
    alignment: dict[str, Any]
    normalized_alignment: dict[str, Any] | None


class ElevenLabsTimestampsClient:
    def __init__(
        self,
        *,
        api_key_getter: Callable[[str], str | None] | None = None,
        timeout_sec: float = 60.0,
    ) -> None:
        self._api_key_getter = api_key_getter or os.environ.get
        self._timeout_sec = timeout_sec

    def synthesize_with_timestamps(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str,
        output_format: str,
    ) -> ElevenLabsTimestampsResponse:
        api_key = self._api_key_getter(ELEVENLABS_API_KEY_ENV)
        if not api_key:
            raise SyncCutError(
                f"{ELEVENLABS_API_KEY_ENV} is required for ElevenLabs generation"
            )

        quoted_voice_id = urllib.parse.quote(voice_id, safe="")
        query = urllib.parse.urlencode({"output_format": output_format})
        url = ELEVENLABS_TIMESTAMPS_URL.format(voice_id=quoted_voice_id)
        url = f"{url}?{query}"
        payload = json.dumps({"text": text, "model_id": model_id}).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "xi-api-key": api_key,
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout_sec) as response:
                status = getattr(response, "status", 200)
                body = response.read()
        except urllib.error.HTTPError as exc:
            message = _safe_http_error_message(exc)
            raise SyncCutError(f"ElevenLabs request failed with HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise SyncCutError(f"ElevenLabs network error: {_safe_reason(exc.reason)}") from exc
        except OSError as exc:
            raise SyncCutError(f"ElevenLabs network error: {_safe_reason(exc)}") from exc

        if status < 200 or status >= 300:
            raise SyncCutError(f"ElevenLabs request failed with HTTP {status}")

        try:
            raw = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SyncCutError("ElevenLabs response was not valid JSON") from exc

        return _load_timestamps_response(raw)


def _load_timestamps_response(raw: Any) -> ElevenLabsTimestampsResponse:
    root = require_mapping(raw, context="ElevenLabs response")
    audio_base64 = require_non_empty_string(
        root.get("audio_base64"),
        context="ElevenLabs response.audio_base64",
    )
    alignment = require_mapping(
        root.get("alignment"),
        context="ElevenLabs response.alignment",
    )
    normalized_raw = root.get("normalized_alignment")
    normalized_alignment = (
        require_mapping(
            normalized_raw,
            context="ElevenLabs response.normalized_alignment",
        )
        if normalized_raw is not None
        else None
    )
    return ElevenLabsTimestampsResponse(
        audio_base64=audio_base64,
        alignment=alignment,
        normalized_alignment=normalized_alignment,
    )


def _safe_http_error_message(exc: urllib.error.HTTPError) -> str:
    try:
        body = exc.read().decode("utf-8", errors="replace")
    except OSError:
        return "provider returned an error response"

    body = body.strip()
    if not body:
        return "provider returned an empty error response"
    return body[:300]


def _safe_reason(value: object) -> str:
    message = str(value).strip()
    return message[:300] if message else "request failed"
