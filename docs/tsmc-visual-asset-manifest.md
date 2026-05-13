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
- `planned`: selected for active local asset production in the current phase.
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
| `scene_006` | `02_INTRO` | `B_ROLL` | `assets/visuals/scene_006.mp4` | prepared-local | Grain of sand in hand cutting to a gleaming silicon wafer. | Actual filename: `assets/visuals/scene_006.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: tactile sand-to-wafer contrast with clean macro lighting and a clear material transformation theme. |
| `scene_008` | `03_MECHANISM_1` | `AI_VIDEO` | `assets/visuals/scene_008.mp4` | prepared-local | Stylized 1987 handshake over a contract in Hsinchu. | Actual filename: `assets/visuals/scene_008.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: stylized historical reenactment of a Hsinchu contract handshake; avoid claiming archival authenticity unless sourced. |
| `scene_010` | `03_MECHANISM_1` | `B_ROLL` | `assets/visuals/scene_010.mp4` | prepared-local | Whiteboard diagrams separating design from manufacturing, chip design office. | Actual filename: `assets/visuals/scene_010.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: circuit whiteboard and design-office visuals that make the design/manufacturing split easy to read. |
| `scene_013` | `04_MECHANISM_2` | `AI_VIDEO` | `assets/visuals/scene_013.mp4` | prepared-local | Abstract transistor shrinking from visible scale to nanometers with node countdown. | Actual filename: `assets/visuals/scene_013.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: motion-graphic style scale comparison with node numbers counting down toward 2nm. |
| `scene_015` | `04_MECHANISM_2` | `B_ROLL` | `assets/visuals/scene_015.mp4` | prepared-local | Semiconductor cleanroom with engineers in bunny suits and large machines. | Actual filename: `assets/visuals/scene_015.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: pristine cleanroom environment with suited engineers and large semiconductor tools. |
| `scene_017` | `04_MECHANISM_2` | `B_ROLL` | `assets/visuals/scene_017.mp4` | prepared-local | EUV process animation with light, mirrors, tin plasma, and wafer projection. | Actual filename: `assets/visuals/scene_017.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: scientific motion graphic showing 13.5nm EUV light, vacuum mirrors, tin plasma, wafer projection, and circuit pattern formation. |
| `scene_020` | `05_MECHANISM_3` | `B_ROLL` | `assets/visuals/scene_020.mp4` | prepared-local | Quick cuts of chip company leaders and product launches with TSMC attribution. | Actual filename: `assets/visuals/scene_020.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: editorial montage of semiconductor/product presentations with clear manufacturing attribution to TSMC; confirm rights for any real speaker footage. |
| `scene_022` | `05_MECHANISM_3` | `B_ROLL` | `assets/visuals/scene_022.mp4` | prepared-local | Logos converging on TSMC like planets orbiting one central point. | Actual filename: `assets/visuals/scene_022.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: locally built motion graphic of company logos or generic labeled nodes converging on TSMC; verify logo usage rights if real logos are used. |
| `scene_025` | `06_MECHANISM_4` | `AI_VIDEO` | `assets/visuals/scene_025.mp4` | prepared-local | Satellite-style Taiwan view with strait, stylized warships, and glowing island. | Actual filename: `assets/visuals/scene_025.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: stylized geopolitical map or satellite-like view of Taiwan, the strait, symbolic warships, and a soft blue data-center glow. |
| `scene_027` | `06_MECHANISM_4` | `B_ROLL` | `assets/visuals/scene_027.mp4` | prepared-local | TSMC Arizona fab construction in Phoenix with flags and workers. | Actual filename: `assets/visuals/scene_027.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: desert construction or fab exterior context with hard hats, large white structures, and US/Taiwan flag cues; use licensed or approved material. |
| `scene_029` | `06_MECHANISM_4` | `B_ROLL` | `assets/visuals/scene_029.mp4` | prepared-local | ASML headquarters split with EUV restriction world map. | Actual filename: `assets/visuals/scene_029.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: map or split-screen motion graphic showing EUV export restrictions, permitted routes, and China highlighted as restricted. |
| `scene_030` | `07_CONCLUSION` | `AI_VIDEO` | `assets/visuals/scene_030.mp4` | prepared-local | Slow sunrise aerial over the Taiwan Strait with Taiwan visible. | Actual filename: `assets/visuals/scene_030.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: calm cinematic sunrise over the Taiwan Strait with golden water and Taiwan at the edge; no text overlay needed. |
| `scene_031` | `07_CONCLUSION` | `B_ROLL` | `assets/visuals/scene_031.mp4` | prepared-local | Morris Chang-like speaker at podium with engineering audience and trust slide. | Actual filename: `assets/visuals/scene_031.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: staged or licensed event-style speaker shot with engineers and executives; avoid misleading archival claims. |
| `scene_033` | `07_CONCLUSION` | `AI_VIDEO` | `assets/visuals/scene_033.mp4` | prepared-local | Final cleanroom wafer shot reflecting overhead lights and fading to black. | Actual filename: `assets/visuals/scene_033.mp4`. Provenance: unknown-local. Video preferred and validated locally. Production direction: quiet final wafer shot in an empty cleanroom with mirror reflections, slow zoom, fade to black, and closing-title mood. |

## Production Notes

`scene_005` and `scene_007` are intentionally not local visual asset targets. They are `CHART` and `TABLE` scenes rendered from structured `visual.data`, so `prepare-visual-assets` will not copy files for them.

AI_VIDEO assets can later be generated externally by Long or another tool, then saved locally under `assets/visuals/` using the filenames above. SyncCut does not generate those files.

B_ROLL assets can later be sourced manually, with licensing and source tracking handled outside SyncCut. SyncCut does not download, scrape, fetch, or license B-roll.

SyncCut only copies and references local files. The asset preparation command copies supported local files from `assets/visuals/` to `remotion/public/visuals/` and annotates `remotion/props.json` with Remotion-safe public paths.
