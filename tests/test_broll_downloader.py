import json
from pathlib import Path

import pytest

from synccut.broll_downloader import (
    BrollCandidate,
    download_broll_from_manifest,
)
from synccut.validators import SyncCutError


class FakeProvider:
    def __init__(self, candidates=None, content: bytes = b"video") -> None:
        self.candidates = candidates if candidates is not None else [candidate()]
        self.content = content
        self.search_calls: list[tuple[str, int]] = []
        self.download_calls: list[BrollCandidate] = []

    def search(self, query: str, *, per_page: int = 10) -> list[BrollCandidate]:
        self.search_calls.append((query, per_page))
        return self.candidates

    def download(self, candidate: BrollCandidate) -> bytes:
        self.download_calls.append(candidate)
        return self.content


def candidate(**overrides) -> BrollCandidate:
    values = {
        "provider": "pexels",
        "provider_asset_id": "123",
        "provider_asset_url": "https://www.pexels.com/video/123/",
        "creator_name": "Creator",
        "creator_url": "https://www.pexels.com/@creator",
        "download_url": "https://videos.example/123.mp4",
        "file_type": "video/mp4",
        "width": 1920,
        "height": 1080,
        "duration_sec": 12,
        "attribution": "Video by Creator on Pexels",
        "quality": "hd",
    }
    values.update(overrides)
    return BrollCandidate(**values)


def scene(
    scene_id: str,
    *,
    visual_type: str = "AI_VIDEO",
    prepared_status: str = "missing",
    local_asset_status: str = "missing",
    search_query_seed: str | None = "factory shot",
) -> dict:
    return {
        "scene_id": scene_id,
        "section_key": "01_HOOK",
        "section": "HOOK",
        "section_order": 1,
        "scene_order": int(scene_id.split("_")[-1]) if scene_id.split("_")[-1].isdigit() else 1,
        "visual_type": visual_type,
        "duration_sec": 2.0,
        "duration_frames": 60,
        "assets_dir": "assets/visuals",
        "expected_asset_stem": f"assets/visuals/{scene_id}",
        "supported_extensions": [".mp4"],
        "expected_filenames": [f"assets/visuals/{scene_id}.mp4"],
        "prepared_status": prepared_status,
        "public_path": None,
        "asset_status": None,
        "asset_source": None,
        "local_asset_status": local_asset_status,
        "local_asset_path": None,
        "local_supported_paths": [],
        "local_unsupported_paths": [],
        "prompt": search_query_seed,
        "search_query_seed": search_query_seed,
        "visual_data": None,
        "notes": "test",
    }


def write_manifest(path: Path, scenes: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "metadata": {
                    "generated_by": "synccut visual-manifest",
                    "source_props": "remotion/props.json",
                    "assets_dir": "assets/visuals",
                    "format": "json",
                },
                "summary": {"target_scenes": len(scenes)},
                "supported_extensions": [".mp4"],
                "scenes": scenes,
            }
        ),
        encoding="utf-8",
    )
    return path


def test_eligible_scene_selection_and_dry_run_writes_nothing(tmp_path) -> None:
    manifest = write_manifest(
        tmp_path / "generated" / "visual_manifest.json",
        [scene("scene_001"), scene("scene_002")],
    )
    assets_dir = tmp_path / "assets" / "visuals"
    fake = FakeProvider()

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=tmp_path / "generated" / "broll_download_manifest.json",
        dry_run=True,
        provider_client=fake,
        api_key_getter=lambda _name: pytest.fail("dry-run should not read env"),
    )

    assert result.selected == 2
    assert result.would_download == 2
    assert result.written == 0
    assert not assets_dir.exists()
    assert fake.search_calls == []
    assert fake.download_calls == []


@pytest.mark.parametrize(
    ("raw_scene", "reason"),
    [
        (scene("scene_001", visual_type="TABLE"), "non_target"),
        (scene("scene_001", prepared_status="prepared"), "already_prepared"),
        (scene("scene_001", local_asset_status="found"), "local_asset_found"),
        (scene("scene_001", local_asset_status="duplicate_supported"), "local_duplicate_supported"),
        (scene("scene_001", local_asset_status="unsupported_only"), "local_unsupported_only"),
        (scene("scene_001", search_query_seed=None), "no_search_query"),
    ],
)
def test_skips_ineligible_scenes(tmp_path, raw_scene, reason) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [raw_scene])

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=tmp_path / "assets",
        metadata_out=tmp_path / "metadata.json",
        dry_run=True,
    )

    assert result.selected == 0
    assert result.skipped == 1
    assert result.scenes[0].reason == reason


def test_explicit_scene_id_unknown_reports_scene_id_not_found(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=tmp_path / "assets",
        metadata_out=tmp_path / "metadata.json",
        dry_run=True,
        scene_ids=["scene_999"],
    )

    assert result.skipped == 1
    assert result.scenes[0].scene_id == "scene_999"
    assert result.scenes[0].reason == "scene_id_not_found"


def test_limit_and_scene_id_selection(tmp_path) -> None:
    manifest = write_manifest(
        tmp_path / "manifest.json",
        [scene("scene_001"), scene("scene_002"), scene("scene_003")],
    )

    limited = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=tmp_path / "assets",
        metadata_out=tmp_path / "metadata.json",
        dry_run=True,
        limit=2,
    )
    explicit = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=tmp_path / "assets",
        metadata_out=tmp_path / "metadata.json",
        dry_run=True,
        scene_ids=["scene_003", "scene_001"],
    )

    assert [item.scene_id for item in limited.scenes] == ["scene_001", "scene_002"]
    assert [item.scene_id for item in explicit.scenes] == ["scene_001", "scene_003"]
    with pytest.raises(SyncCutError, match="--limit cannot be used with --scene-id"):
        download_broll_from_manifest(
            manifest,
            provider_name="pexels",
            assets_dir=tmp_path / "assets",
            metadata_out=tmp_path / "metadata.json",
            dry_run=True,
            limit=1,
            scene_ids=["scene_001"],
        )


def test_missing_pexels_api_key_blocks_before_provider_call(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])

    with pytest.raises(SyncCutError, match="PEXELS_API_KEY"):
        download_broll_from_manifest(
            manifest,
            provider_name="pexels",
            assets_dir=tmp_path / "assets",
            metadata_out=tmp_path / "metadata.json",
            api_key_getter=lambda _name: None,
        )


def test_fake_provider_writes_mp4_and_metadata(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])
    assets_dir = tmp_path / "assets" / "visuals"
    metadata = tmp_path / "generated" / "broll_download_manifest.json"

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=metadata,
        provider_client=FakeProvider(),
    )

    assert result.written == 1
    assert (assets_dir / "scene_001.mp4").read_bytes() == b"video"
    data = json.loads(metadata.read_text(encoding="utf-8"))
    entry = data["scenes"][0]
    assert data["summary"]["written"] == 1
    assert entry["provider_asset_id"] == "123"
    assert entry["creator_name"] == "Creator"
    assert entry["attribution"] == "Video by Creator on Pexels"
    assert entry["query"] == "factory shot"
    assert entry["asset_path"] == str(assets_dir / "scene_001.mp4")
    assert entry["provider_duration_sec"] == 12


def test_reuse_before_provider_call_when_metadata_and_file_match(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])
    assets_dir = tmp_path / "assets" / "visuals"
    asset_path = assets_dir / "scene_001.mp4"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_bytes(b"existing")
    metadata = tmp_path / "metadata.json"
    metadata.write_text(
        json.dumps(
            {
                "schema_version": "0.1",
                "metadata": {"provider": "pexels"},
                "summary": {},
                "scenes": [
                    {
                        "scene_id": "scene_001",
                        "status": "written",
                        "query": "factory shot",
                        "provider": "pexels",
                        "provider_asset_id": "123",
                        "provider_asset_url": "https://www.pexels.com/video/123/",
                        "creator_name": "Creator",
                        "creator_url": "https://www.pexels.com/@creator",
                        "download_url": "https://videos.example/123.mp4",
                        "asset_path": str(asset_path),
                        "file_type": "video/mp4",
                        "width": 1920,
                        "height": 1080,
                        "provider_duration_sec": 12,
                        "attribution": "Video by Creator on Pexels",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    fake = FakeProvider()

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=metadata,
        provider_client=fake,
    )

    assert result.reused == 1
    assert fake.search_calls == []
    assert fake.download_calls == []


def test_existing_local_file_blocks_without_matching_metadata(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.mp4").write_bytes(b"existing")

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=tmp_path / "metadata.json",
        provider_client=FakeProvider(),
    )

    assert result.blocked == 1
    assert "--overwrite" in (result.scenes[0].reason or "")


def test_overwrite_replaces_planned_mp4_only(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.mp4").write_bytes(b"old")

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=tmp_path / "metadata.json",
        provider_client=FakeProvider(content=b"new"),
        overwrite=True,
    )

    assert result.written == 1
    assert (assets_dir / "scene_001.mp4").read_bytes() == b"new"


def test_other_same_stem_files_block_even_with_overwrite(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])
    assets_dir = tmp_path / "assets" / "visuals"
    assets_dir.mkdir(parents=True)
    (assets_dir / "scene_001.mp4").write_bytes(b"old")
    (assets_dir / "scene_001.mov").write_bytes(b"other")

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=assets_dir,
        metadata_out=tmp_path / "metadata.json",
        provider_client=FakeProvider(),
        overwrite=True,
    )

    assert result.blocked == 1
    assert result.scenes[0].reason == "same_stem_conflict; remove other same-stem files manually before overwrite"


def test_no_acceptable_candidate_records_blocked(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])

    result = download_broll_from_manifest(
        manifest,
        provider_name="pexels",
        assets_dir=tmp_path / "assets",
        metadata_out=tmp_path / "metadata.json",
        provider_client=FakeProvider(candidates=[candidate(file_type="video/webm")]),
    )

    assert result.blocked == 1
    assert result.scenes[0].reason == "no_acceptable_candidate"


def test_pixabay_and_unknown_provider_rejected(tmp_path) -> None:
    manifest = write_manifest(tmp_path / "manifest.json", [scene("scene_001")])

    with pytest.raises(SyncCutError, match="provider pixabay is not implemented yet"):
        download_broll_from_manifest(
            manifest,
            provider_name="pixabay",
            assets_dir=tmp_path / "assets",
            metadata_out=tmp_path / "metadata.json",
            dry_run=True,
        )
    with pytest.raises(SyncCutError, match="unsupported B-roll provider"):
        download_broll_from_manifest(
            manifest,
            provider_name="other",
            assets_dir=tmp_path / "assets",
            metadata_out=tmp_path / "metadata.json",
            dry_run=True,
        )
