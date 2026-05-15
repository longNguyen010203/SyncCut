import json
from pathlib import Path

import pytest

from synccut.validators import SyncCutError
from synccut.visual_manifest import (
    build_visual_manifest,
    format_visual_manifest_markdown,
    visual_manifest_to_dict,
    write_visual_manifest_file,
)


def write_asset(path: Path, content: bytes = b"asset") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def valid_props() -> dict:
    return {
        "metadata": {
            "generated_by": "synccut export-remotion",
            "fps": 30,
            "duration_sec": 6.0,
            "duration_frames": 180,
            "total_scenes": 4,
            "total_sections": 2,
        },
        "composition": {"id": "SyncCutVideo", "fps": 30, "duration_frames": 180},
        "sections": [],
        "scenes": [
            {
                "id": "scene_001",
                "scene_order": 1,
                "section": "HOOK",
                "section_order": 1,
                "section_key": "01_HOOK",
                "duration_sec": 2.5,
                "duration_frames": 75,
                "visual_type": "AI_VIDEO",
                "visual": {
                    "type": "AI_VIDEO",
                    "prompt": "Wafer close-up",
                    "data": {"description": "fallback description"},
                },
            },
            {
                "id": "scene_002",
                "scene_order": 2,
                "section": "HOOK",
                "section_order": 1,
                "section_key": "01_HOOK",
                "duration_sec": 1.5,
                "duration_frames": 45,
                "visual_type": "TABLE",
                "visual": {"type": "TABLE", "prompt": "Table", "data": {"rows": []}},
            },
            {
                "id": "scene_003",
                "scene_order": 3,
                "section": "INTRO",
                "section_order": 2,
                "section_key": "02_INTRO",
                "duration_sec": 3.0,
                "duration_frames": 90,
                "visual_type": "B_ROLL",
                "visual": {"type": "B_ROLL", "prompt": None, "data": {"query": "factory"}},
            },
            {
                "id": "scene_004",
                "scene_order": 4,
                "section": "INTRO",
                "section_order": 2,
                "section_key": "02_INTRO",
                "duration_sec": 4.0,
                "duration_frames": 120,
                "visual_type": "AI_VIDEO",
                "visual": {
                    "type": "AI_VIDEO",
                    "prompt": "Prepared prompt",
                    "data": None,
                    "public_path": "visuals/scene_004.mp4",
                    "asset_status": "prepared",
                    "asset_source": "local",
                },
            },
        ],
        "assets": {"audio": [], "visuals": []},
        "warnings": [],
    }


def write_props(path: Path, props: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(props if props is not None else valid_props()), encoding="utf-8")
    return path


def build_manifest(tmp_path: Path):
    return build_visual_manifest(
        valid_props(),
        tmp_path / "remotion" / "props.json",
        assets_dir=tmp_path / "assets" / "visuals",
    )


def test_manifest_targets_only_ai_video_and_b_roll_and_preserves_order(tmp_path) -> None:
    manifest = build_manifest(tmp_path)

    assert [scene.scene_id for scene in manifest.scenes] == [
        "scene_001",
        "scene_003",
        "scene_004",
    ]
    assert [scene.visual_type for scene in manifest.scenes] == ["AI_VIDEO", "B_ROLL", "AI_VIDEO"]


def test_manifest_includes_section_duration_prompt_and_expected_names(tmp_path) -> None:
    manifest = build_manifest(tmp_path)
    scene = manifest.scenes[0]

    assert scene.section_key == "01_HOOK"
    assert scene.section == "HOOK"
    assert scene.section_order == 1
    assert scene.scene_order == 1
    assert scene.duration_sec == 2.5
    assert scene.duration_frames == 75
    assert scene.prompt == "Wafer close-up"
    assert scene.search_query_seed == "Wafer close-up"
    assert scene.visual_data == {"description": "fallback description"}
    assert scene.expected_asset_stem == str(tmp_path / "assets" / "visuals" / "scene_001")
    assert scene.supported_extensions == [".jpeg", ".jpg", ".mov", ".mp4", ".png", ".webm", ".webp"]
    assert str(tmp_path / "assets" / "visuals" / "scene_001.mp4") in scene.expected_filenames


def test_search_query_seed_uses_existing_data_query_when_prompt_absent(tmp_path) -> None:
    manifest = build_manifest(tmp_path)

    assert manifest.scenes[1].scene_id == "scene_003"
    assert manifest.scenes[1].search_query_seed == "factory"


def test_local_missing_when_no_matching_file_exists(tmp_path) -> None:
    manifest = build_manifest(tmp_path)

    assert manifest.scenes[0].local_asset_status == "missing"
    assert manifest.scenes[0].local_asset_path is None
    assert manifest.summary.local_missing == 3


def test_local_found_for_one_supported_file(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.MP4")

    manifest = build_manifest(tmp_path)

    assert manifest.scenes[0].local_asset_status == "found"
    assert manifest.scenes[0].local_asset_path == str(
        tmp_path / "assets" / "visuals" / "scene_001.MP4"
    )
    assert manifest.summary.local_found == 1


def test_duplicate_supported_for_multiple_supported_files(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.mp4")
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.png")

    manifest = build_manifest(tmp_path)

    assert manifest.scenes[0].local_asset_status == "duplicate_supported"
    assert manifest.scenes[0].local_asset_path is None
    assert len(manifest.scenes[0].local_supported_paths) == 2
    assert manifest.summary.local_duplicate_supported == 1


def test_unsupported_only_for_matching_unsupported_suffixes(tmp_path) -> None:
    write_asset(tmp_path / "assets" / "visuals" / "scene_001.txt")

    manifest = build_manifest(tmp_path)

    assert manifest.scenes[0].local_asset_status == "unsupported_only"
    assert manifest.scenes[0].local_unsupported_paths == [
        str(tmp_path / "assets" / "visuals" / "scene_001.txt")
    ]
    assert manifest.summary.local_unsupported_only == 1


def test_prepared_public_path_and_asset_fields_carried_through(tmp_path) -> None:
    manifest = build_manifest(tmp_path)
    scene = manifest.scenes[2]

    assert scene.prepared_status == "prepared"
    assert scene.public_path == "visuals/scene_004.mp4"
    assert scene.asset_status == "prepared"
    assert scene.asset_source == "local"
    assert manifest.summary.prepared == 1
    assert manifest.summary.missing == 2


def test_markdown_includes_title_summary_naming_policy_and_table(tmp_path) -> None:
    manifest = build_manifest(tmp_path)

    output = format_visual_manifest_markdown(manifest)

    assert output.startswith("# Visual Asset Manifest\n")
    assert "- target_scenes: 3" in output
    assert "- prepared: 1" in output
    assert "assets/visuals/<scene_id>.<supported_ext>" in output
    assert "Supported extensions: .jpeg, .jpg, .mov, .mp4, .png, .webm, .webp" in output
    assert "| scene_id | section_key | visual_type | duration_sec |" in output
    assert "| scene_001 | 01_HOOK | AI_VIDEO | 2.5 | missing | missing |" in output


def test_json_dict_is_parseable_and_deterministic(tmp_path) -> None:
    manifest = build_visual_manifest(
        valid_props(),
        tmp_path / "remotion" / "props.json",
        assets_dir=tmp_path / "assets" / "visuals",
        output_format="json",
    )

    data = visual_manifest_to_dict(manifest)
    encoded = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    parsed = json.loads(encoded)

    assert parsed["schema_version"] == "0.1"
    assert parsed["metadata"]["generated_by"] == "synccut visual-manifest"
    assert parsed["summary"]["target_scenes"] == 3
    assert parsed["summary"]["prepared"] == 1
    assert parsed["supported_extensions"] == [
        ".jpeg",
        ".jpg",
        ".mov",
        ".mp4",
        ".png",
        ".webm",
        ".webp",
    ]
    assert parsed["scenes"][0]["scene_id"] == "scene_001"
    assert parsed["scenes"][0]["expected_filenames"][0].endswith("scene_001.jpeg")


def test_dry_run_writes_no_file(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_manifest.md"

    result = write_visual_manifest_file(props_path, out_path=out_path, dry_run=True)

    assert result.status == "would_create"
    assert not out_path.exists()
    assert not out_path.parent.exists()


def test_identical_output_reuses_existing_file(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_manifest.md"

    first = write_visual_manifest_file(props_path, out_path=out_path)
    second = write_visual_manifest_file(props_path, out_path=out_path)

    assert first.status == "written"
    assert second.status == "reused"


def test_differing_output_blocks_and_mentions_overwrite(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_manifest.md"
    out_path.parent.mkdir(parents=True)
    out_path.write_text("changed\n", encoding="utf-8")

    with pytest.raises(SyncCutError, match="--overwrite"):
        write_visual_manifest_file(props_path, out_path=out_path)


def test_overwrite_replaces_requested_output_only(tmp_path) -> None:
    props_path = write_props(tmp_path / "remotion" / "props.json")
    out_path = tmp_path / "generated" / "visual_manifest.md"
    other_path = tmp_path / "generated" / "other.md"
    out_path.parent.mkdir(parents=True)
    out_path.write_text("changed\n", encoding="utf-8")
    other_path.write_text("keep\n", encoding="utf-8")

    result = write_visual_manifest_file(props_path, out_path=out_path, overwrite=True)

    assert result.status == "written"
    assert out_path.read_text(encoding="utf-8").startswith("# Visual Asset Manifest")
    assert other_path.read_text(encoding="utf-8") == "keep\n"
