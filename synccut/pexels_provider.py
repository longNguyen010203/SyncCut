from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from synccut.broll_downloader import BrollCandidate
from synccut.validators import SyncCutError, require_mapping


PEXELS_VIDEO_SEARCH_URL = "https://api.pexels.com/v1/videos/search"


class PexelsVideoClient:
    def __init__(self, *, api_key: str, timeout_sec: float = 60.0) -> None:
        if not api_key.strip():
            raise SyncCutError("PEXELS_API_KEY is required for Pexels B-roll download")
        self._api_key = api_key
        self._timeout_sec = timeout_sec

    def search(self, query: str, *, per_page: int = 10) -> list[BrollCandidate]:
        params = urllib.parse.urlencode(
            {
                "query": query,
                "orientation": "landscape",
                "per_page": str(per_page),
            }
        )
        request = urllib.request.Request(
            f"{PEXELS_VIDEO_SEARCH_URL}?{params}",
            method="GET",
            headers={
                "Accept": "application/json",
                "Authorization": self._api_key,
            },
        )
        raw = self._read_json(request, label="Pexels video search")
        root = require_mapping(raw, context="Pexels video search response")
        videos = root.get("videos")
        if not isinstance(videos, list):
            raise SyncCutError("Pexels video search response.videos must be an array")

        candidates: list[BrollCandidate] = []
        for video in videos:
            candidates.extend(_candidate_from_video(video))
        return candidates

    def download(self, candidate: BrollCandidate) -> bytes:
        request = urllib.request.Request(
            candidate.download_url,
            method="GET",
            headers={"Accept": candidate.file_type or "application/octet-stream"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_sec) as response:
                status = getattr(response, "status", 200)
                body = response.read()
        except urllib.error.HTTPError as exc:
            message = _safe_http_error_message(exc)
            raise SyncCutError(f"Pexels download failed with HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise SyncCutError(f"Pexels download network error: {_safe_reason(exc.reason)}") from exc
        except OSError as exc:
            raise SyncCutError(f"Pexels download network error: {_safe_reason(exc)}") from exc

        if status < 200 or status >= 300:
            raise SyncCutError(f"Pexels download failed with HTTP {status}")
        if not body:
            raise SyncCutError("Pexels download returned empty content")
        return body

    def _read_json(self, request: urllib.request.Request, *, label: str) -> Any:
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_sec) as response:
                status = getattr(response, "status", 200)
                body = response.read()
        except urllib.error.HTTPError as exc:
            message = _safe_http_error_message(exc)
            raise SyncCutError(f"{label} failed with HTTP {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise SyncCutError(f"{label} network error: {_safe_reason(exc.reason)}") from exc
        except OSError as exc:
            raise SyncCutError(f"{label} network error: {_safe_reason(exc)}") from exc

        if status < 200 or status >= 300:
            raise SyncCutError(f"{label} failed with HTTP {status}")
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SyncCutError(f"{label} response was not valid JSON") from exc


def _candidate_from_video(raw: Any) -> list[BrollCandidate]:
    if not isinstance(raw, dict):
        return []
    provider_asset_id = raw.get("id")
    provider_asset_url = raw.get("url")
    video_files = raw.get("video_files")
    if not isinstance(provider_asset_id, (int, str)):
        return []
    if not isinstance(provider_asset_url, str) or not provider_asset_url.strip():
        return []
    if not isinstance(video_files, list):
        return []

    user = raw.get("user") if isinstance(raw.get("user"), dict) else {}
    creator_name = user.get("name") if isinstance(user.get("name"), str) else None
    creator_url = user.get("url") if isinstance(user.get("url"), str) else None
    attribution = (
        f"Video by {creator_name} on Pexels"
        if creator_name
        else "Video provided by Pexels"
    )
    duration = raw.get("duration")
    duration_sec = duration if isinstance(duration, int) and not isinstance(duration, bool) else None

    candidates: list[BrollCandidate] = []
    for raw_file in video_files:
        if not isinstance(raw_file, dict):
            continue
        link = raw_file.get("link")
        file_type = raw_file.get("file_type")
        if not isinstance(link, str) or not link.strip():
            continue
        if not isinstance(file_type, str) or not file_type.strip():
            continue
        candidates.append(
            BrollCandidate(
                provider="pexels",
                provider_asset_id=str(provider_asset_id),
                provider_asset_url=provider_asset_url,
                creator_name=creator_name,
                creator_url=creator_url,
                download_url=link,
                file_type=file_type,
                width=_optional_int(raw_file.get("width")),
                height=_optional_int(raw_file.get("height")),
                duration_sec=duration_sec,
                attribution=attribution,
                quality=raw_file.get("quality") if isinstance(raw_file.get("quality"), str) else None,
            )
        )
    return candidates


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


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
