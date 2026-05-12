# SyncCut

SyncCut is a Python CLI plus a Remotion project for turning prepared scene, narration audio, and alignment data into a renderable video timeline. The Python side builds and validates structured timeline data; the Remotion side consumes `remotion/props.json` to preview or locally render the video.

## What The MVP Does

- Builds `timeline.json` from `scenes.json`, section audio files, and alignment JSON files.
- Validates and inspects generated timelines.
- Exports Remotion-friendly props to `remotion/props.json`.
- Copies section audio into `remotion/public/audio/` and annotates props with public paths.
- Optionally copies local AI/B-roll visual files into `remotion/public/visuals/`.
- Reports AI/B-roll visual asset readiness.
- Runs props-only or public-file preflight checks before rendering.
- Supports Remotion typecheck, still, smoke, segment, and full local render workflows from `remotion/`.

## What The MVP Does Not Do

- No DOCX parsing.
- No AI image or video generation.
- No B-roll downloading, scraping, or external media fetching.
- No direct `ffmpeg` or `ffprobe` calls.
- No media probing, decoding, transcoding, or normalization.
- No GUI or web app.
- No Python command that renders through Remotion.

## Prerequisites

- Python 3.11 or newer.
- Node and npm for the Remotion project under `remotion/`.
- Local Chrome at `/usr/bin/google-chrome` for the local Remotion render scripts in this environment.
- Prepared inputs: `scenes.json`, section audio files, and matching alignment JSON files.

## Setup

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
cd remotion
npm install
cd ..
```

## Quick Start

Run the example workflow from the repository root:

```bash
.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
.venv/bin/synccut validate-timeline timeline.json
.venv/bin/synccut inspect timeline.json
.venv/bin/synccut export-remotion timeline.json --out remotion/props.json
.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
.venv/bin/synccut inspect-visual-assets remotion/props.json
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
cd remotion
npm run typecheck
npm run render:smoke:local
```

`render:smoke:local` writes a short ignored preview video to `remotion/out/smoke.mp4`. Use segment or final render commands only after preflight and smoke rendering pass.

## Input Expectations

`scenes.json` contains ordered scenes, section keys, dialogue, and visual metadata. Section audio files are matched by section key, for example `01_HOOK.mp3`. Alignment JSON files are also matched by section key, for example `01_HOOK_alignment_tmp.json`, and provide paragraph, sentence, and word timestamps.

See [docs/schemas.md](docs/schemas.md) for data shapes and [docs/matching.md](docs/matching.md) for matching rules.

## Python Command Summary

- `build-timeline`: build `timeline.json` from scenes, audio references, and alignment timestamps.
- `validate-timeline`: validate `timeline.json` structure and timing.
- `inspect`: print a readable timeline overview grouped by section.
- `export-remotion`: export Remotion props from `timeline.json`.
- `prepare-remotion-assets`: copy section audio into `remotion/public/audio/` and update props.
- `prepare-visual-assets`: copy local AI/B-roll visual assets into `remotion/public/visuals/` and update props.
- `inspect-visual-assets`: report AI/B-roll visual asset readiness from props.
- `preflight`: report full-render readiness from props, optionally verifying public files.

Run `.venv/bin/synccut --help` or `.venv/bin/synccut <command> --help` for exact options.

## Remotion Workflow

See [remotion/README.md](remotion/README.md) for detailed Remotion notes.

Common commands from `remotion/`:

```bash
npm run typecheck
npm run still:local
npm run render:smoke:local
npm run render:segment:local
npm run render:final:local
```

The local render scripts use `/usr/bin/google-chrome` with `--chrome-mode=chrome-for-testing`. In sandboxed environments, Chrome launch may require permission. The default Remotion browser download path can fail with `remotion.media` DNS errors; the local scripts avoid that download path when Chrome is available.

## Local Visual Assets

AI video and B-roll scenes can use optional local files named by scene id:

```text
assets/visuals/<scene_id>.mp4
assets/visuals/<scene_id>.png
```

Supported local visual extensions are `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`.

Prepare local visual assets with:

```bash
.venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
```

Missing `AI_VIDEO` and `B_ROLL` visual files are non-fatal because Remotion renders placeholders. Unsupported or malformed prepared paths are reported by `inspect-visual-assets` and `preflight`.

## Preflight And Troubleshooting

Props-only readiness report:

```bash
.venv/bin/synccut preflight remotion/props.json
```

Verified public-file readiness report:

```bash
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
```

Warnings mean rendering can still proceed with known fallbacks, such as missing optional AI/B-roll visuals. Errors mean a render should not be attempted until the issue is fixed, such as missing prepared audio public paths or missing verified public files.

Common environment issues:

- Chrome may fail with `SIGTRAP` or `setsockopt: Operation not permitted` when sandbox policy blocks browser launch.
- `npm run still` may fail while downloading Chrome Headless Shell from `remotion.media`; use `npm run still:local` when local Chrome is available.

## Artifact Policy

Do not commit generated or local-only artifacts:

- `timeline.json`
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.venv/`
- `remotion/node_modules/`
- Python, pytest, and Node caches
- `remotion/props.json` if it only changed because of local validation regeneration

`remotion/props.json` may be committed only when intentionally refreshed as sample Remotion input.

## Development

Run Python tests:

```bash
.venv/bin/python -m pytest
```

Run Remotion typecheck:

```bash
cd remotion
npm run typecheck
```

Check CLI help:

```bash
.venv/bin/synccut --help
.venv/bin/synccut build-timeline --help
.venv/bin/synccut preflight --help
```

## Roadmap

See [docs/future-phases.md](docs/future-phases.md) for future ideas such as DOCX parsing, richer asset management, media generation, and assembly work. Those are intentionally outside the current MVP.
