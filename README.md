# SyncCut

SyncCut is a Python CLI plus a Remotion renderer for turning prepared scene, narration audio, and alignment data into a renderable video. The Python side builds and validates structured timeline data; the Remotion side consumes `remotion/props.json` and prepared public assets to preview or locally render the video.

The v0.1.0 MVP is a prepared-input-to-video pipeline. It assumes scenes, audio, and alignment files already exist, then produces timeline data, Remotion props, public assets, preflight reports, and local Remotion render outputs.

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

- Python 3.11 or newer, matching `requires-python = ">=3.11"` in `pyproject.toml`.
- Node and npm for the Remotion project under `remotion/`; this repo uses Remotion 4, React 18, and TypeScript 5.
- Local Chrome at `/usr/bin/google-chrome` for the local Remotion render scripts in this environment.
- Prepared inputs: `scenes.json`, section audio files, and matching alignment JSON files.
- Local AI video and B-roll visual assets are optional. Missing local visuals produce warnings/placeholders unless you are validating the full visual sample.

## Setup

From a fresh clone, run these commands from the repository root unless a command explicitly changes into `remotion/`:

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install -e '.[dev]'
cd remotion
npm install
cd ..
```

## Quick Start

This no-visual quick start builds the sample timeline, exports Remotion props, prepares audio, and verifies public files. It does not require local AI video or B-roll files.

```bash
.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
.venv/bin/synccut validate-timeline timeline.json
.venv/bin/synccut export-remotion timeline.json --out remotion/props.json
.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
```

Expected no-visual state: `preflight` may report `status: warning` because optional `AI_VIDEO` and `B_ROLL` local visuals are missing, but `errors` and `file_errors` should be `0`. Prepare the full local visual sample only when you have files under `assets/visuals/`; that workflow is summarized in [Local Visual Assets](#local-visual-assets).

After preflight, validate the Remotion project:

```bash
cd remotion
npm run typecheck
```

`npm run render:smoke:local` writes a short ignored preview video to `remotion/out/smoke.mp4`. Use render commands only after preflight and typecheck pass.

## Pipeline Overview

The normal data flow is:

```text
scenes.json + section audio + alignment JSON
  -> timeline.json
  -> validate / inspect
  -> remotion/props.json
  -> prepare-remotion-assets
  -> remotion/public/audio/*
  -> optional prepare-visual-assets
  -> remotion/public/visuals/*
  -> preflight
  -> Remotion render
  -> remotion/out/*
```

Key generated artifacts:

- `timeline.json`: generated timeline output from `build-timeline`.
- `remotion/props.json`: generated Remotion props exported from `timeline.json`; tracked as sample input only when intentionally refreshed.
- `remotion/public/audio/*`: prepared local public copies of section audio.
- `remotion/public/visuals/*`: prepared local public copies of optional AI video and B-roll assets.
- `remotion/out/*`: Remotion still, smoke, segment, and final render outputs.
- Caches: Python, pytest, Node, and Remotion tooling caches created while developing or rendering.

## v0.1.0 Release Evidence

The v0.1.0 release was validated with the TSMC sample after timing and visual-duration polish. The post-polish final render completed `22584/22584` frames to `remotion/out/final.mp4`, and human re-review accepted the previous conclusion timing gap and short-video duration issues as resolved. The release decision recorded in docs is `release-ready-with-known-warnings`.

No local media, prepared public assets, or render outputs are bundled with the release. See [docs/final-render-quality-review.md](docs/final-render-quality-review.md) and [docs/plans/v0.1.0-release-checklist.md](docs/plans/v0.1.0-release-checklist.md) for release evidence.

## Input Expectations

`scenes.json` contains ordered scenes, section keys, dialogue, and visual metadata. Section audio files are matched by section key, for example `01_HOOK.mp3`. Alignment JSON files are also matched by section key, for example `01_HOOK_alignment_tmp.json`, and provide paragraph, sentence, and word timestamps.

See [docs/schemas.md](docs/schemas.md) for data shapes and [docs/matching.md](docs/matching.md) for matching rules.

## Python Command Summary

- `build-timeline`: build `timeline.json` from scenes, audio references, and alignment timestamps.
- `validate-timeline`: validate `timeline.json` structure and timing.
- `inspect`: print a readable timeline overview grouped by section.
- `prepare-narration`: create a local narration manifest/text package from `scenes.json` for future audio/alignment providers; it does not call ElevenLabs or generate audio/alignment.
- `generate-audio`: consume a narration manifest with provider `elevenlabs` to create section audio plus alignment; `ELEVENLABS_API_KEY` is read from the environment for real generation, while `--dry-run` needs no key and writes nothing.
- `export-remotion`: export Remotion props from `timeline.json`.
- `prepare-remotion-assets`: copy section audio into `remotion/public/audio/` and update props.
- `visual-manifest`: create a local Markdown or JSON planning manifest for optional AI/B-roll visual assets; it does not download, generate, copy, or prepare media.
- `download-broll`: consume a visual manifest JSON and download missing local B-roll assets with provider `pexels`; `--dry-run` needs no key and writes nothing, while real runs read `PEXELS_API_KEY` from the environment.
- `inspect-visual-duration`: report local AI/B-roll duration and resolution readiness with `ffprobe` video metadata inspection only.
- `prepare-visual-assets`: copy local AI/B-roll visual assets into `remotion/public/visuals/` and update props.
- `inspect-visual-assets`: report AI/B-roll visual asset readiness from props.
- `preflight`: report full-render readiness from props, optionally verifying public files.

Run `.venv/bin/synccut --help` or `.venv/bin/synccut <command> --help` for exact options.

## Remotion Workflow

See [remotion/README.md](remotion/README.md) for detailed Remotion notes.

Run render workflow commands from `remotion/` after exporting props, preparing assets, running preflight, and passing typecheck:

```bash
cd remotion
npm run typecheck
npm run still:local
npm run render:smoke:local
npm run render:segment:local
npm run render:final:local
```

- `still:local` writes `remotion/out/preview.png`.
- `render:smoke:local` renders frames `0-149` to `remotion/out/smoke.mp4`.
- `render:segment:local` renders frames `0-899` to `remotion/out/segment.mp4`.
- `render:final:local` renders the full composition to `remotion/out/final.mp4`.

The local render scripts use `/usr/bin/google-chrome` with `--chrome-mode=chrome-for-testing`. In sandboxed environments, Chrome launch may fail with `SIGTRAP` or `setsockopt: Operation not permitted`; rerun with browser launch permission if available. Do not add workaround code unless you are intentionally changing the render environment. The default Remotion browser download path can fail with `remotion.media` DNS errors; the local scripts avoid that download path when Chrome is available.

## Local Visual Assets

AI video and B-roll scenes can use optional local files named by scene id under `assets/visuals/`:

```text
assets/visuals/<scene_id>.<supported_ext>
```

Supported local visual extensions are `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`.

Use exactly one supported file per target scene id. Local visual media is not bundled with the release and should not be committed.

After exporting `remotion/props.json`, generate a planning manifest when you need a human-readable asset brief or a JSON handoff for future B-roll tooling:

```bash
.venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.md
.venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json
```

The manifest reports prepared props readiness separately from local `assets/visuals/` source-file availability. It is read-only: it does not download, generate, copy, or prepare media.

To plan downloads for missing visual scenes, use the JSON manifest with `download-broll`. Pexels is the first implemented provider. Dry-run is safe and requires no API key; real runs require `PEXELS_API_KEY` and write local ignored files under `assets/visuals/` by default.

```bash
.venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir assets/visuals --limit 1 --dry-run
```

`download-broll` does not mutate `remotion/props.json`, run `prepare-visual-assets`, probe media, or render.

To inspect local visual duration and resolution readiness before preparing assets or rendering, run:

```bash
.venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.md
```

`inspect-visual-duration` uses `ffprobe` for video metadata inspection only. It does not modify media, mutate props, prepare assets, or render. If `ffprobe` is missing, install FFmpeg tools or pass `--ffprobe-bin`; reports are written under ignored `generated/`.

After preparing audio, inspect, prepare, and verify visuals:

```bash
.venv/bin/synccut inspect-visual-assets remotion/props.json
.venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
.venv/bin/synccut inspect-visual-assets remotion/props.json
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
```

For the full TSMC visual sample, the expected prepared state is `visual_prepared: 17`, `visual_missing: 0`, `errors: 0`, `file_errors: 0`, and `status: ok`. See [docs/tsmc-visual-asset-manifest.md](docs/tsmc-visual-asset-manifest.md) for the scene list.

Missing `AI_VIDEO` and `B_ROLL` visual files are non-fatal in no-visual validation because Remotion renders placeholders. Unsupported files, duplicate supported files for one scene id, or malformed prepared paths are reported by `inspect-visual-assets`, `prepare-visual-assets`, and `preflight`.

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

Generated, local media, and render artifacts are ignored and should not be committed. Treat the generated paths by role:

- `assets/visuals/*`: local-only source media for optional AI video and B-roll scenes.
- `remotion/public/*`: prepared local public media copied from audio and visual inputs.
- `remotion/out/*`: local Remotion render output.
- `timeline.json`: generated timeline output.
- `remotion/props.json`: generated sample props. Do not commit it after local validation regeneration unless a sample props refresh is explicitly approved.

Common ignored paths include:

- `timeline.json`
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.venv/`
- `remotion/node_modules/`
- Python, pytest, and Node caches
- `remotion/props.json` if it only changed because of local validation regeneration

When `git status` looks dirty after validation, check the state with:

```bash
git status --short
```

If `remotion/props.json` changed only because you regenerated the sample locally, restore it with:

```bash
git restore remotion/props.json
```

Do not restore source or documentation files unless that change is unintentional.

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

GitHub Actions runs the Python test suite and Remotion typecheck on `push` and `pull_request`. CI intentionally does not render video, does not require local visual assets, and does not upload generated media or render outputs. Local render workflows remain documented in [remotion/README.md](remotion/README.md).

Check CLI help:

```bash
.venv/bin/synccut --help
.venv/bin/synccut build-timeline --help
.venv/bin/synccut preflight --help
```

## Roadmap

See [docs/future-phases.md](docs/future-phases.md) for future ideas such as DOCX parsing, richer asset management, media generation, and assembly work. Those are intentionally outside the current MVP.
