from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol, Sequence

from synccut.validators import SyncCutError, require_mapping, require_non_empty_string
from synccut.visual_assets import SUPPORTED_VISUAL_EXTENSIONS, TARGET_VISUAL_TYPES


DEFAULT_BROLL_METADATA_PATH = Path("generated/broll_download_manifest.json")
BROLL_METADATA_SCHEMA_VERSION = "0.1"
BROLL_METADATA_GENERATOR = "synccut download-broll"
PEXELS_API_KEY_ENV = "PEXELS_API_KEY"
SUPPORTED_BROLL_PROVIDERS = {"pexels"}
FUTURE_BROLL_PROVIDERS = {"pixabay"}
DEFAULT_SEARCH_PER_PAGE = 10


@dataclass(frozen=True)
class BrollCandidate:
    provider: str
    provider_asset_id: str
    provider_asset_url: str
    creator_name: str | None
    creator_url: str | None
    download_url: str
    file_type: str
    width: int | None
    height: int | None
    duration_sec: int | None
    attribution: str
    quality: str | None = None


class BrollProviderClient(Protocol):
    def search(self, query: str, *, per_page: int = DEFAULT_SEARCH_PER_PAGE) -> list[BrollCandidate]:
        ...

    def download(self, candidate: BrollCandidate) -> bytes:
        ...


@dataclass(frozen=True)
class BrollDownloadSceneResult:
    scene_id: str
    status: str
    reason: str | None
    query: str | None
    provider: str
    provider_asset_id: str | None
    provider_asset_url: str | None
    creator_name: str | None
    creator_url: str | None
    download_url: str | None
    asset_path: Path | None
    file_type: str | None
    width: int | None
    height: int | None
    provider_duration_sec: int | None
    attribution: str | None


@dataclass(frozen=True)
class BrollDownloadResult:
    provider: str
    scenes: list[BrollDownloadSceneResult]
    metadata_path: Path
    dry_run: bool
    selected: int
    written: int
    reused: int
    blocked: int
    skipped: int

    @property
    def would_download(self) -> int:
        return sum(1 for scene in self.scenes if scene.status == "would_download")


@dataclass(frozen=True)
class _ManifestScene:
    scene_id: str
    visual_type: str
    prepared_status: str
    local_asset_status: str
    search_query_seed: str | None


def download_broll_from_manifest(
    visual_manifest_path: Path,
    *,
    provider_name: str,
    assets_dir: Path,
    metadata_out: Path = DEFAULT_BROLL_METADATA_PATH,
    dry_run: bool = False,
    overwrite: bool = False,
    limit: int | None = None,
    scene_ids: Sequence[str] = (),
    provider_client: BrollProviderClient | None = None,
    api_key_getter: Callable[[str], str | None] | None = None,
) -> BrollDownloadResult:
    provider = provider_name.strip().lower()
    _validate_provider(provider)
    if limit is not None and scene_ids:
        raise SyncCutError("--limit cannot be used with --scene-id")
    if limit is not None and limit < 1:
        raise SyncCutError("--limit must be greater than or equal to 1")

    manifest_scenes = _load_manifest_scenes(visual_manifest_path)
    selected, skipped = _select_scenes(manifest_scenes, limit=limit, scene_ids=scene_ids)
    metadata = _load_metadata(metadata_out)

    results: list[BrollDownloadSceneResult] = [*skipped]
    for scene in selected:
        query = scene.search_query_seed or ""
        asset_path = assets_dir / f"{scene.scene_id}.mp4"
        reused = _reuse_result(
            metadata,
            scene_id=scene.scene_id,
            provider=provider,
            query=query,
            asset_path=asset_path,
        )
        if reused is not None:
            results.append(reused)
            continue

        if dry_run:
            results.append(
                _empty_result(
                    scene.scene_id,
                    status="would_download",
                    reason=None,
                    query=query,
                    provider=provider,
                    asset_path=asset_path,
                )
            )
            continue

        conflict = _local_conflict_reason(assets_dir, scene.scene_id, asset_path, overwrite=overwrite)
        if conflict is not None:
            results.append(
                _empty_result(
                    scene.scene_id,
                    status="blocked",
                    reason=conflict,
                    query=query,
                    provider=provider,
                    asset_path=asset_path,
                )
            )
            continue

        client = provider_client or _build_provider_client(provider, api_key_getter=api_key_getter)
        candidates = client.search(query, per_page=DEFAULT_SEARCH_PER_PAGE)
        candidate = _select_candidate(candidates)
        if candidate is None:
            results.append(
                _empty_result(
                    scene.scene_id,
                    status="blocked",
                    reason="no_acceptable_candidate",
                    query=query,
                    provider=provider,
                    asset_path=asset_path,
                )
            )
            continue

        content = client.download(candidate)
        if not content:
            results.append(
                _candidate_result(
                    scene.scene_id,
                    status="blocked",
                    reason="empty_download",
                    query=query,
                    asset_path=asset_path,
                    candidate=candidate,
                )
            )
            continue

        assets_dir.mkdir(parents=True, exist_ok=True)
        _write_bytes_atomic(asset_path, content)
        results.append(
            _candidate_result(
                scene.scene_id,
                status="written",
                reason=None,
                query=query,
                asset_path=asset_path,
                candidate=candidate,
            )
        )

    ordered_results = _sort_results(results, manifest_scenes, scene_ids)
    result = _build_result(
        provider=provider,
        results=ordered_results,
        metadata_out=metadata_out,
        dry_run=dry_run,
    )

    if not dry_run:
        metadata_doc = _metadata_document(
            visual_manifest_path=visual_manifest_path,
            provider=provider,
            assets_dir=assets_dir,
            result=result,
        )
        _write_json_atomic(metadata_out, metadata_doc)

    return result


def _validate_provider(provider: str) -> None:
    if provider in FUTURE_BROLL_PROVIDERS:
        raise SyncCutError(f"provider {provider} is not implemented yet")
    if provider not in SUPPORTED_BROLL_PROVIDERS:
        expected = ", ".join(sorted(SUPPORTED_BROLL_PROVIDERS | FUTURE_BROLL_PROVIDERS))
        raise SyncCutError(f"unsupported B-roll provider '{provider}'; expected one of {expected}")


def _build_provider_client(
    provider: str, *, api_key_getter: Callable[[str], str | None] | None
) -> BrollProviderClient:
    if provider == "pexels":
        api_key_getter = api_key_getter or os.environ.get
        api_key = api_key_getter(PEXELS_API_KEY_ENV)
        if not api_key:
            raise SyncCutError(f"{PEXELS_API_KEY_ENV} is required for Pexels B-roll download")
        from synccut.pexels_provider import PexelsVideoClient

        return PexelsVideoClient(api_key=api_key)
    _validate_provider(provider)
    raise AssertionError("unreachable provider validation state")


def _load_manifest_scenes(path: Path) -> list[_ManifestScene]:
    try:
        root = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SyncCutError(f"{path}: file not found") from exc
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed JSON: {exc.msg}") from exc
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to read visual manifest: {exc}") from exc

    data = require_mapping(root, context=str(path))
    if data.get("schema_version") != "0.1":
        raise SyncCutError(f"{path}: unsupported visual manifest schema_version")
    scenes_raw = data.get("scenes")
    if not isinstance(scenes_raw, list):
        raise SyncCutError(f"{path}: scenes must be an array")

    scenes: list[_ManifestScene] = []
    for index, raw_scene in enumerate(scenes_raw):
        context = f"{path}: scenes[{index}]"
        scene = require_mapping(raw_scene, context=context)
        scenes.append(
            _ManifestScene(
                scene_id=require_non_empty_string(scene.get("scene_id"), context=f"{context}.scene_id"),
                visual_type=require_non_empty_string(
                    scene.get("visual_type"), context=f"{context}.visual_type"
                ),
                prepared_status=require_non_empty_string(
                    scene.get("prepared_status"), context=f"{context}.prepared_status"
                ),
                local_asset_status=require_non_empty_string(
                    scene.get("local_asset_status"), context=f"{context}.local_asset_status"
                ),
                search_query_seed=_optional_query(scene.get("search_query_seed")),
            )
        )
    return scenes


def _select_scenes(
    scenes: list[_ManifestScene],
    *,
    limit: int | None,
    scene_ids: Sequence[str],
) -> tuple[list[_ManifestScene], list[BrollDownloadSceneResult]]:
    requested = set(scene_ids)
    selected: list[_ManifestScene] = []
    skipped: list[BrollDownloadSceneResult] = []
    seen_requested: set[str] = set()

    for scene in scenes:
        if requested and scene.scene_id not in requested:
            continue
        if scene.scene_id in requested:
            seen_requested.add(scene.scene_id)

        reason = _ineligible_reason(scene)
        if reason is not None:
            skipped.append(
                _empty_result(
                    scene.scene_id,
                    status="skipped",
                    reason=reason,
                    query=scene.search_query_seed,
                    provider="pexels",
                    asset_path=None,
                )
            )
            continue
        selected.append(scene)
        if limit is not None and len(selected) >= limit:
            break

    for scene_id in scene_ids:
        if scene_id not in seen_requested:
            skipped.append(
                _empty_result(
                    scene_id,
                    status="skipped",
                    reason="scene_id_not_found",
                    query=None,
                    provider="pexels",
                    asset_path=None,
                )
            )
    return selected, skipped


def _ineligible_reason(scene: _ManifestScene) -> str | None:
    if scene.visual_type not in TARGET_VISUAL_TYPES:
        return "non_target"
    if scene.prepared_status == "prepared":
        return "already_prepared"
    if scene.prepared_status not in {"missing", "unsupported"}:
        return "unsupported_prepared_status"
    if scene.prepared_status == "unsupported":
        return "unsupported_prepared_status"
    if scene.local_asset_status == "found":
        return "local_asset_found"
    if scene.local_asset_status == "duplicate_supported":
        return "local_duplicate_supported"
    if scene.local_asset_status == "unsupported_only":
        return "local_unsupported_only"
    if scene.local_asset_status != "missing":
        return "unsupported_prepared_status"
    if not scene.search_query_seed:
        return "no_search_query"
    return None


def _reuse_result(
    metadata: dict[str, Any],
    *,
    scene_id: str,
    provider: str,
    query: str,
    asset_path: Path,
) -> BrollDownloadSceneResult | None:
    for entry in _metadata_entries(metadata):
        if (
            entry.get("scene_id") == scene_id
            and entry.get("status") in {"written", "reused"}
            and entry.get("provider") == provider
            and entry.get("query") == query
            and entry.get("asset_path") == str(asset_path)
            and isinstance(entry.get("provider_asset_id"), str)
            and asset_path.exists()
        ):
            return BrollDownloadSceneResult(
                scene_id=scene_id,
                status="reused",
                reason=None,
                query=query,
                provider=provider,
                provider_asset_id=_optional_string(entry.get("provider_asset_id")),
                provider_asset_url=_optional_string(entry.get("provider_asset_url")),
                creator_name=_optional_string(entry.get("creator_name")),
                creator_url=_optional_string(entry.get("creator_url")),
                download_url=_optional_string(entry.get("download_url")),
                asset_path=asset_path,
                file_type=_optional_string(entry.get("file_type")),
                width=_optional_int(entry.get("width")),
                height=_optional_int(entry.get("height")),
                provider_duration_sec=_optional_int(entry.get("provider_duration_sec")),
                attribution=_optional_string(entry.get("attribution")),
            )
    return None


def _local_conflict_reason(
    assets_dir: Path,
    scene_id: str,
    planned_path: Path,
    *,
    overwrite: bool,
) -> str | None:
    matches = _same_stem_files(assets_dir, scene_id)
    if not matches:
        return None
    if not overwrite:
        return "local_file_exists; rerun with --overwrite to replace planned output"
    if matches == [planned_path]:
        return None
    return "same_stem_conflict; remove other same-stem files manually before overwrite"


def _same_stem_files(assets_dir: Path, scene_id: str) -> list[Path]:
    if not assets_dir.exists():
        return []
    if not assets_dir.is_dir():
        raise SyncCutError(f"{assets_dir}: visual assets path must be a directory")
    try:
        entries = list(assets_dir.iterdir())
    except OSError as exc:
        raise SyncCutError(f"{assets_dir}: failed to read visual assets directory: {exc}") from exc
    return sorted(
        [path for path in entries if path.is_file() and path.stem == scene_id],
        key=lambda path: path.name.lower(),
    )


def _select_candidate(candidates: list[BrollCandidate]) -> BrollCandidate | None:
    acceptable = [
        candidate
        for candidate in candidates
        if candidate.file_type == "video/mp4" and candidate.download_url.strip()
    ]
    if not acceptable:
        return None
    return sorted(acceptable, key=_candidate_sort_key)[0]


def _candidate_sort_key(candidate: BrollCandidate) -> tuple[int, int, int]:
    landscape_rank = 0 if _is_landscape(candidate) else 1
    width_rank = -(candidate.width or 0)
    quality_rank = 0 if candidate.quality == "hd" else 1
    return (landscape_rank, width_rank, quality_rank)


def _is_landscape(candidate: BrollCandidate) -> bool:
    if candidate.width is None or candidate.height is None:
        return False
    return candidate.width >= candidate.height


def _candidate_result(
    scene_id: str,
    *,
    status: str,
    reason: str | None,
    query: str,
    asset_path: Path,
    candidate: BrollCandidate,
) -> BrollDownloadSceneResult:
    return BrollDownloadSceneResult(
        scene_id=scene_id,
        status=status,
        reason=reason,
        query=query,
        provider=candidate.provider,
        provider_asset_id=candidate.provider_asset_id,
        provider_asset_url=candidate.provider_asset_url,
        creator_name=candidate.creator_name,
        creator_url=candidate.creator_url,
        download_url=candidate.download_url,
        asset_path=asset_path,
        file_type=candidate.file_type,
        width=candidate.width,
        height=candidate.height,
        provider_duration_sec=candidate.duration_sec,
        attribution=candidate.attribution,
    )


def _empty_result(
    scene_id: str,
    *,
    status: str,
    reason: str | None,
    query: str | None,
    provider: str,
    asset_path: Path | None,
) -> BrollDownloadSceneResult:
    return BrollDownloadSceneResult(
        scene_id=scene_id,
        status=status,
        reason=reason,
        query=query,
        provider=provider,
        provider_asset_id=None,
        provider_asset_url=None,
        creator_name=None,
        creator_url=None,
        download_url=None,
        asset_path=asset_path,
        file_type=None,
        width=None,
        height=None,
        provider_duration_sec=None,
        attribution=None,
    )


def _build_result(
    *,
    provider: str,
    results: list[BrollDownloadSceneResult],
    metadata_out: Path,
    dry_run: bool,
) -> BrollDownloadResult:
    return BrollDownloadResult(
        provider=provider,
        scenes=results,
        metadata_path=metadata_out,
        dry_run=dry_run,
        selected=sum(1 for result in results if result.status in {"would_download", "written", "reused", "blocked"}),
        written=sum(1 for result in results if result.status == "written"),
        reused=sum(1 for result in results if result.status == "reused"),
        blocked=sum(1 for result in results if result.status == "blocked"),
        skipped=sum(1 for result in results if result.status == "skipped"),
    )


def _metadata_document(
    *,
    visual_manifest_path: Path,
    provider: str,
    assets_dir: Path,
    result: BrollDownloadResult,
) -> dict[str, Any]:
    return {
        "schema_version": BROLL_METADATA_SCHEMA_VERSION,
        "metadata": {
            "generated_by": BROLL_METADATA_GENERATOR,
            "source_visual_manifest": str(visual_manifest_path),
            "provider": provider,
            "assets_dir": str(assets_dir),
        },
        "summary": {
            "selected": result.selected,
            "written": result.written,
            "reused": result.reused,
            "blocked": result.blocked,
            "skipped": result.skipped,
        },
        "scenes": [_result_to_metadata_entry(scene) for scene in result.scenes],
    }


def _result_to_metadata_entry(result: BrollDownloadSceneResult) -> dict[str, Any]:
    return {
        "scene_id": result.scene_id,
        "status": result.status,
        "reason": result.reason,
        "query": result.query,
        "provider": result.provider,
        "provider_asset_id": result.provider_asset_id,
        "provider_asset_url": result.provider_asset_url,
        "creator_name": result.creator_name,
        "creator_url": result.creator_url,
        "download_url": result.download_url,
        "asset_path": str(result.asset_path) if result.asset_path is not None else None,
        "file_type": result.file_type,
        "width": result.width,
        "height": result.height,
        "provider_duration_sec": result.provider_duration_sec,
        "attribution": result.attribution,
    }


def _load_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SyncCutError(f"{path}: malformed B-roll metadata: {exc.msg}") from exc
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to read B-roll metadata: {exc}") from exc
    return require_mapping(data, context=str(path))


def _metadata_entries(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    entries = metadata.get("scenes", [])
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    _write_text_atomic(path, content)


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to write file: {exc}") from exc


def _write_bytes_atomic(path: Path, content: bytes) -> None:
    tmp_path = path.with_name(f".{path.name}.tmp")
    try:
        tmp_path.write_bytes(content)
        tmp_path.replace(path)
    except OSError as exc:
        raise SyncCutError(f"{path}: failed to write file: {exc}") from exc


def _sort_results(
    results: list[BrollDownloadSceneResult],
    manifest_scenes: list[_ManifestScene],
    scene_ids: Sequence[str],
) -> list[BrollDownloadSceneResult]:
    manifest_order = {scene.scene_id: index for index, scene in enumerate(manifest_scenes)}
    missing_base = len(manifest_order)
    explicit_order = {scene_id: missing_base + index for index, scene_id in enumerate(scene_ids)}
    return sorted(
        results,
        key=lambda result: manifest_order.get(result.scene_id, explicit_order.get(result.scene_id, missing_base)),
    )


def _optional_query(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def _optional_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value
