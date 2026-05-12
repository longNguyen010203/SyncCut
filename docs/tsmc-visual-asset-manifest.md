# TSMC Visual Asset Manifest

## Purpose

This is the local visual asset manifest for the SyncCut TSMC sample. It maps `AI_VIDEO` and `B_ROLL` target scene IDs from `remotion/props.json` to the expected local filenames under `assets/visuals/`.

This document is text-only. It does not contain binary media, generated images, downloaded B-roll, or embedded assets.

## Artifact Policy

Actual source assets live under:

```text
assets/visuals/
```

Prepared Remotion public copies live under:

```text
remotion/public/visuals/
```

Both directories are ignored and should not be committed by default. Do not commit `remotion/props.json` if it changed only because of local validation regeneration or temporary visual asset preparation.

## Naming Convention

Use one supported local asset per target scene:

```text
assets/visuals/<scene_id>.<ext>
```

Supported extensions:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.mp4`
- `.webm`
- `.mov`

Use exactly one supported asset per `scene_id`. Duplicate supported files for the same scene, such as both `assets/visuals/scene_003.mp4` and `assets/visuals/scene_003.png`, should make `prepare-visual-assets` fail until the duplicate is resolved.

Status values in this manifest:

- `prepared-local`: a local file has been placed, copied into `remotion/public/visuals/`, and validated by `prepare-visual-assets`, `inspect-visual-assets`, and verified preflight.
- `planned`: selected for the first real local asset subset.
- `optional-planned`: recommended next target if the first subset expands from three scenes to five scenes.
- `needed`: known target scene, not yet selected for the first subset.

## Workflow Commands

Regenerate props and prepared audio from the repository root:

```bash
.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
.venv/bin/synccut export-remotion timeline.json --out remotion/props.json
.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
```

Inspect visual readiness before or after preparing local visual assets:

```bash
.venv/bin/synccut inspect-visual-assets remotion/props.json
```

Prepare local visual assets:

```bash
.venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
```

Verify prepared public files:

```bash
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
```

## Target Scenes

| scene_id | section_key | visual_type | recommended_filename | status | prompt_summary | notes |
| --- | --- | --- | --- | --- | --- | --- |
| `scene_001` | `01_HOOK` | `AI_VIDEO` | `assets/visuals/scene_001.mp4` | prepared-local | Silicon wafer rotating under blue cleanroom light with reflected engineers. | Actual filename: `assets/visuals/scene_001.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: close macro wafer shot with cleanroom reflections and slow controlled motion. |
| `scene_003` | `01_HOOK` | `B_ROLL` | `assets/visuals/scene_003.mp4` | prepared-local | TSMC Hsinchu campus aerial at dusk with fabrication halls and coastline. | Actual filename: `assets/visuals/scene_003.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: wide establishing campus/fab exterior with dusk lighting and geographic context. |
| `scene_004` | `02_INTRO` | `B_ROLL` | `assets/visuals/scene_004.mp4` | prepared-local | Montage linking NVIDIA, iPhone launch, satellite, and self-driving car imagery. | Actual filename: `assets/visuals/scene_004.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: concise news/product montage that visually connects advanced chips to consumer, defense, and autonomous systems. |
| `scene_006` | `02_INTRO` | `B_ROLL` | `assets/visuals/scene_006.mp4` | optional-planned | Grain of sand in hand cutting to a gleaming silicon wafer. | Next recommended target after the first three. Video preferred. Provenance TBD: original/manual, external-generated, or licensed/manual-source. Production direction: tactile sand-to-wafer contrast with clean macro lighting. |
| `scene_008` | `03_MECHANISM_1` | `AI_VIDEO` | `assets/visuals/scene_008.mp4` | optional-planned | Stylized 1987 handshake over a contract in Hsinchu. | Next recommended target after the first three. Video preferred. Provenance TBD: original/manual, external-generated, or licensed/manual-source. Production direction: clearly stylized historical reenactment; avoid claiming archival authenticity unless sourced. |
| `scene_010` | `03_MECHANISM_1` | `B_ROLL` | `assets/visuals/scene_010.mp4` | needed | Whiteboard diagrams separating design from manufacturing, chip design office. | Can be staged/local office footage or simple motion graphic. |
| `scene_013` | `04_MECHANISM_2` | `AI_VIDEO` | `assets/visuals/scene_013.mp4` | needed | Abstract transistor shrinking from visible scale to nanometers with node countdown. | Motion graphic candidate created outside SyncCut. |
| `scene_015` | `04_MECHANISM_2` | `B_ROLL` | `assets/visuals/scene_015.mp4` | needed | Semiconductor cleanroom with engineers in bunny suits and large machines. | Use licensed cleanroom footage or approved local material. |
| `scene_017` | `04_MECHANISM_2` | `B_ROLL` | `assets/visuals/scene_017.mp4` | needed | EUV process animation with light, mirrors, tin plasma, and wafer projection. | Motion graphic or licensed explainer asset produced outside SyncCut. |
| `scene_020` | `05_MECHANISM_3` | `B_ROLL` | `assets/visuals/scene_020.mp4` | needed | Quick cuts of chip company leaders and product launches with TSMC attribution. | Manually sourced/licensed clips or locally created montage. |
| `scene_022` | `05_MECHANISM_3` | `B_ROLL` | `assets/visuals/scene_022.mp4` | needed | Logos converging on TSMC like planets orbiting one central point. | Prefer locally built motion graphic; confirm logo usage rights. |
| `scene_025` | `06_MECHANISM_4` | `AI_VIDEO` | `assets/visuals/scene_025.mp4` | needed | Satellite-style Taiwan view with strait, stylized warships, and glowing island. | External motion graphic candidate; avoid using unlicensed satellite imagery. |
| `scene_027` | `06_MECHANISM_4` | `B_ROLL` | `assets/visuals/scene_027.mp4` | needed | TSMC Arizona fab construction in Phoenix with flags and workers. | Manually sourced/licensed construction footage or approved local imagery. |
| `scene_029` | `06_MECHANISM_4` | `B_ROLL` | `assets/visuals/scene_029.mp4` | needed | ASML headquarters split with EUV restriction world map. | Prefer locally built map/motion graphic; validate any ASML imagery rights. |
| `scene_030` | `07_CONCLUSION` | `AI_VIDEO` | `assets/visuals/scene_030.mp4` | needed | Slow sunrise aerial over the Taiwan Strait with Taiwan visible. | External footage/generation candidate; still fallback can work if cinematic. |
| `scene_031` | `07_CONCLUSION` | `B_ROLL` | `assets/visuals/scene_031.mp4` | needed | Morris Chang-like speaker at podium with engineering audience and trust slide. | Use licensed event footage or staged/illustrative local asset; avoid misleading archival claims. |
| `scene_033` | `07_CONCLUSION` | `AI_VIDEO` | `assets/visuals/scene_033.mp4` | needed | Final cleanroom wafer shot reflecting overhead lights and fading to black. | External AI/video production candidate; still fallback can be `scene_033.png`. |

## Production Notes

`scene_005` and `scene_007` are intentionally not local visual asset targets. They are `CHART` and `TABLE` scenes rendered from structured `visual.data`, so `prepare-visual-assets` will not copy files for them.

AI_VIDEO assets can later be generated externally by Long or another tool, then saved locally under `assets/visuals/` using the filenames above. SyncCut does not generate those files.

B_ROLL assets can later be sourced manually, with licensing and source tracking handled outside SyncCut. SyncCut does not download, scrape, fetch, or license B-roll.

SyncCut only copies and references local files. The asset preparation command copies supported local files from `assets/visuals/` to `remotion/public/visuals/` and annotates `remotion/props.json` with Remotion-safe public paths.
