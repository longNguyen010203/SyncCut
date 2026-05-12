# SyncCut v0.1 Release Checklist

## Purpose

Use this checklist to verify v0.1 release readiness for the SyncCut MVP before tagging, packaging, or handing the repository to a new user.

## Scope Of v0.1

v0.1 covers the prepared-input workflow from `scenes.json`, section audio files, and alignment JSON files to a Remotion-renderable video project.

Confirm v0.1 does not include:

- [ ] DOCX parsing.
- [ ] AI image or video generation.
- [ ] B-roll downloading, fetching, or scraping.
- [ ] Direct `ffmpeg` or `ffprobe` calls.
- [ ] Media probing, decoding, transcoding, or normalization.
- [ ] GUI or web app behavior.
- [ ] Python commands that invoke Remotion rendering.

## Packaging Metadata

Confirm `pyproject.toml`:

- [ ] Project name is `synccut`.
- [ ] Version is `0.1.0`.
- [ ] `requires-python` is `>=3.11`.
- [ ] Runtime dependency includes `typer`.
- [ ] Dev extra includes `pytest`.
- [ ] Console script is `synccut = "synccut.cli:app"`.

Confirm editable install works:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

## Python Validation

Run from the repository root:

```bash
.venv/bin/python -m pytest
.venv/bin/synccut --help
.venv/bin/synccut build-timeline --help
.venv/bin/synccut preflight --help
```

Expected result:

- [ ] Tests pass.
- [ ] CLI help lists the expected commands.
- [ ] `build-timeline` help shows `SCENES_JSON`, `--audio-dir`, `--alignment-dir`, and `--out`.
- [ ] `preflight` help shows `PROPS_JSON`, `--json`, `--verify-files`, and `--public-dir`.

## Example Workflow Validation

Run from the repository root:

```bash
.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
.venv/bin/synccut validate-timeline timeline.json
.venv/bin/synccut inspect timeline.json
.venv/bin/synccut export-remotion timeline.json --out remotion/props.json
.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
.venv/bin/synccut inspect-visual-assets remotion/props.json
.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
```

Expected current sample result:

- [ ] `validate-timeline` passes.
- [ ] The known `07_CONCLUSION` gap warning is present.
- [ ] `preflight` status is `warning`, not `error`.
- [ ] Section audio is prepared.
- [ ] `file_errors` is `0`.
- [ ] `visual_missing` warnings for optional `AI_VIDEO` and `B_ROLL` placeholders are allowed.

## Remotion Validation

Install Remotion dependencies if needed:

```bash
cd remotion
npm install
```

Run:

```bash
npm run typecheck
```

Optional checks when Chrome launch permission and runtime are available:

```bash
npm run still:local
npm run render:smoke:local
npm run render:segment:local
npm run render:final:local
```

Expected result:

- [ ] TypeScript typecheck passes.
- [ ] Optional render outputs are generated under `remotion/out/` only.
- [ ] Browser launch failures in sandboxed environments are recorded, not worked around with source changes.

## Artifact Cleanup Before Commit Or Release

Do not commit:

- [ ] `timeline.json`
- [ ] `remotion/public/*`
- [ ] `remotion/out/*`
- [ ] `assets/visuals/*`
- [ ] `.venv/`
- [ ] `remotion/node_modules/`
- [ ] `__pycache__/`
- [ ] `.pytest_cache/`
- [ ] `remotion/props.json` if it changed only because of validation regeneration.

## Git Review

Run:

```bash
git status --short --ignored
git diff -- README.md docs/release-checklist-v0.1.md docs/plans/release-packaging-and-docs.md
```

Confirm:

- [ ] Only intended documentation changes are staged.
- [ ] Generated artifacts are ignored or absent.
- [ ] No source files changed unless an explicitly reviewed bug fix was required.

## Forbidden Behavior Checklist

Confirm no release change added:

- [ ] Python Remotion wrapper.
- [ ] Direct `ffmpeg` or `ffprobe` calls.
- [ ] Media probing, decoding, or transcoding.
- [ ] DOCX parsing.
- [ ] AI generation.
- [ ] B-roll downloading, fetching, or scraping.
- [ ] GUI or web app behavior.
- [ ] Schema changes.
- [ ] Command behavior changes.

## Suggested Release Commit

This phase should be documentation-only.

Suggested commit message:

```text
Add release documentation for SyncCut MVP
```
