# Add a local Remotion segment render workflow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already render a five-second Remotion smoke clip with local Chrome using `npm run render:smoke:local`. That proves the composition can render a tiny range, but it is too short to exercise much of the exported timeline. The next useful local developer workflow is a longer, still-bounded segment render: render the first 30 seconds of the current Remotion composition to `remotion/out/segment.mp4`.

After this phase, a developer should be able to regenerate props and assets, run a verified preflight check, then run:

    cd remotion
    npm run render:segment:local

and receive a local segment render for frames `0-899`. At 30 fps, that is 900 frames, or 30 seconds. This is not the final video and must not render the full composition. This phase must not add Python commands that invoke Remotion, call Remotion from Python, call ffmpeg directly, generate AI video, download B-roll, fetch external media, probe/decode/transcode media, parse DOCX, add GUI or web app behavior, or change existing Python CLI behavior.

## Progress

- [x] (2026-05-12T13:51:02+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/remotion-render-smoke.md`, `docs/plans/remotion-preview-environment.md`, `docs/plans/preflight-render-readiness.md`, `docs/plans/preflight-file-verification.md`, `remotion/README.md`, `remotion/package.json`, and `.gitignore`.
- [x] (2026-05-12T13:51:02+07:00) Inspected `remotion/package.json`, `remotion/README.md`, `remotion/src/index.ts`, `remotion/src/Root.tsx`, `remotion/src/Video.tsx`, and `remotion/props.json`.
- [x] (2026-05-12T13:51:02+07:00) Created this ExecPlan for the local Remotion segment render workflow.
- [x] (2026-05-12T13:58:02+07:00) Implemented Milestone 1: added the fixed local segment render script and README documentation.
- [x] (2026-05-12T14:03:52+07:00) Completed Milestone 2: validated the segment render workflow against fresh generated props, prepared public assets, verified preflight, Remotion typecheck, segment render, pytest, and artifact status.
- [ ] Complete Milestone 3: final review of scope, artifacts, validation, and commit policy.

## Surprises & Discoveries

- Observation: The Remotion project already has a verified local Chrome smoke render script.
  Evidence: `remotion/package.json` contains `render:smoke:local`, which renders `out/smoke.mp4` with `--frames=0-149`, `--browser-executable=/usr/bin/google-chrome`, `--chrome-mode=chrome-for-testing`, `--concurrency=1`, and `--timeout=60000`.
- Observation: The README already documents the smoke render as a non-final local workflow.
  Evidence: `remotion/README.md` has a "Render Smoke Test" section that says `npm run render:smoke:local` renders frames `0-149` to `out/smoke.mp4`, uses local Chrome, may require browser launch permission, and is not the final MP4.
- Observation: The current composition is large enough that a full render remains out of scope.
  Evidence: Inspecting `remotion/props.json` showed `composition.fps: 30`, `composition.duration_frames: 22584`, and `metadata.duration_sec: 752.79`, which is about 12.5 minutes.
- Observation: Generated render outputs are already ignored.
  Evidence: `.gitignore` contains `remotion/out/`, so `remotion/out/segment.mp4` will be excluded from commit along with `preview.png` and `smoke.mp4`.
- Observation: The current working tree has no tracked or untracked commit candidates before this plan.
  Evidence: `git status --short --ignored` showed only ignored generated or dependency directories such as `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: Milestone 1 did not require dependency, lockfile, Python, or Remotion component changes.
  Evidence: Only `remotion/package.json`, `remotion/README.md`, and this plan were edited. `package-lock.json`, Python source, Remotion rendering source, `remotion/props.json`, and generated artifacts were not changed.
- Observation: Fresh generated props and prepared public audio pass verified preflight before segment rendering.
  Evidence: `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The segment render hits the same sandbox browser-launch limitation as still and smoke renders, then succeeds when Chrome launch is permitted.
  Evidence: The first `npm run render:segment:local` attempt failed with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[48:48:0512/140156.317689:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. Rerunning the same script with Chrome launch permission rendered 900 frames, encoded 900 frames, and printed `out/segment.mp4 1.9 MB`.

## Decision Log

- Decision: Add one fixed npm script named `render:segment:local`.
  Rationale: A fixed script is reproducible and easy to compare across runs. Frames `0-899` provide a 30-second validation segment that is longer than smoke but far smaller than the 22584-frame composition.
  Date/Author: 2026-05-12 / Codex
- Decision: Do not make npm extra arguments the supported override path for the segment script.
  Rationale: `npm run script -- --frames=900-1799` would append a second `--frames` flag after the script's fixed `--frames=0-899`. Depending on how the Remotion CLI resolves duplicate flags would be brittle. For alternate frame ranges, document a full manual Remotion CLI command instead.
  Date/Author: 2026-05-12 / Codex
- Decision: Recommend preflight before rendering, but keep it manual and outside the npm script.
  Rationale: `synccut preflight --verify-files` is the right readiness check, but the segment script should remain a local Remotion render command only. This avoids coupling npm scripts to the Python virtual environment and keeps Python from invoking Remotion.
  Date/Author: 2026-05-12 / Codex
- Decision: Use the same local Chrome flags as the smoke render.
  Rationale: The default Remotion browser download path can fail on `remotion.media` DNS, while `/usr/bin/google-chrome` with `--chrome-mode=chrome-for-testing` has already worked when browser launch is permitted.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep `--timeout=60000`.
  Rationale: The timeout controls Remotion delay-render waits, not total video duration. The existing smoke command uses 60000 ms successfully, and there is no current evidence that a longer segment needs a higher delay-render timeout.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documents and inspecting the current Remotion package scripts, README, entrypoint, root composition, video component, generated props, and ignore rules. No source code, package file, README, generated artifact, or Python CLI behavior has been changed yet for this phase.

The recommended implementation is intentionally small. Add one package script under `remotion/`, document it in `remotion/README.md`, validate it after regenerating props and assets, and record the browser-launch behavior. Do not change Remotion components, Python source, generated props schema, package dependencies, `remotion.config.ts`, or existing commands.

Milestone 1 is complete. `remotion/package.json` now contains `render:segment:local`, which runs `remotion render src/index.ts SyncCutVideo out/segment.mp4 --frames=0-899 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000`. `remotion/README.md` now has a "Segment Render" section after the smoke render section. It recommends verified preflight from the repository root, documents `cd remotion` and `npm run render:segment:local`, states that the output is `out/segment.mp4`, states that frames `0-899` are 900 frames and 30 seconds at 30 fps, records the local Chrome path and browser mode, mentions sandbox browser-launch permission, says the segment is not the final MP4, says not to commit `out/segment.mp4`, and gives a full manual Remotion CLI command for custom frame ranges instead of npm extra args.

Milestone 1 validation passed without rendering. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. No `package-lock.json` change, Python source change, Remotion rendering source change, props change, dependency change, `remotion.config.ts`, full final render, Python Remotion invocation, direct ffmpeg call, media probing/transcoding, AI generation, B-roll download, DOCX parsing, GUI/web app behavior, or frame override wrapper was added.

Milestone 2 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Verified preflight before rendering matched the expected clean warning-only result. It reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The warnings were the known root props warning plus 17 missing optional `AI_VIDEO` and `B_ROLL` visual asset warnings. The errors section printed `none`.

Remotion validation passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. The first `npm run render:segment:local` run failed in the sandbox with the known browser-launch error: `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[48:48:0512/140156.317689:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. The rerun with Chrome launch permission succeeded, copied the 12.1 MB public directory, selected composition `SyncCutVideo`, rendered frames `0-899` as 900 frames, encoded 900 frames, and wrote `out/segment.mp4`. `ls -lh out/segment.mp4` reported a 1.8M file.

Final Python validation passed. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. `git status --short --ignored` showed commit candidates `remotion/README.md`, `remotion/package.json`, and `docs/plans/remotion-segment-render.md`; ignored generated artifacts included `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.

Generated artifact and commit policy after Milestone 2: do not commit `timeline.json`, `remotion/public/*`, `remotion/out/segment.mp4`, any other `remotion/out/*` preview outputs, `assets/visuals/*`, `.pytest_cache/`, or `__pycache__/`. Do not commit `remotion/props.json` if it only changed because of validation regeneration. Commit candidates remain `docs/plans/remotion-segment-render.md`, `remotion/package.json`, and `remotion/README.md`. No source changes were needed during validation, and no full final render, Python command invoking Remotion, direct ffmpeg call, media probing/transcoding, AI generation, B-roll download, DOCX parsing, GUI/web app, frame override wrapper, or Remotion component change was added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The Python CLI creates and prepares data for Remotion. It should not invoke Remotion rendering in this phase. The relevant repository-root data workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The Remotion app consumes `remotion/props.json`. `remotion/src/index.ts` registers `RemotionRoot`. `remotion/src/Root.tsx` registers one composition using `defaultProps.composition.id`, `duration_frames`, `fps`, `width`, and `height`. The composition id is currently `SyncCutVideo`. `remotion/src/Video.tsx` renders section audio and maps every scene to a Remotion `Sequence` using exported `scene.start_frame` and `scene.duration_frames`.

Current generated props have:

    composition.id: SyncCutVideo
    composition.fps: 30
    composition.duration_frames: 22584
    metadata.duration_sec: 752.79
    metadata.total_scenes: 33
    metadata.total_sections: 7
    assets.audio: 7
    assets.visuals: 0

The current Remotion scripts are:

    "studio": "remotion studio src/index.ts"
    "typecheck": "tsc --noEmit"
    "still": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0"
    "still:local": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing"
    "render:smoke:local": "remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

The current `.gitignore` excludes generated and local dependency output:

    examples
    assets/visuals/
    .venv
    remotion/node_modules
    remotion/public
    remotion/out/
    timeline.json
    __pycache__/
    .pytest_cache/

`remotion/out/segment.mp4` is therefore already ignored.

## Existing Smoke Render Workflow

The smoke render workflow is:

    cd remotion
    npm run render:smoke:local

It runs:

    remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

Frames `0-149` are inclusive. At 30 fps, 150 frames equals 5 seconds. The smoke render is useful because it proves Remotion can bundle the app, load props, use local public assets, launch Chrome, render a short frame range, encode a video, and write an artifact. It is deliberately not the final video.

## Why Segment Render Is Useful

A 30-second segment render provides more confidence than the five-second smoke clip without paying the cost of a full 12.5-minute render. It can exercise more scene transitions, more SectionAudio duration, more placeholder/data-driven visuals, and more of the real composition timing. It is still bounded enough to remain a local developer validation step.

The segment render should not be treated as final assembly. It is a preview artifact to catch obvious rendering, asset, timing, or browser issues before a future full render workflow is designed.

## Proposed Segment Command

Add this script to `remotion/package.json`:

    "render:segment:local": "remotion render src/index.ts SyncCutVideo out/segment.mp4 --frames=0-899 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

This command renders:

- Remotion command: `render`
- entrypoint: `src/index.ts`
- composition id: `SyncCutVideo`
- output: `out/segment.mp4`
- frame range: `--frames=0-899`
- local browser: `--browser-executable=/usr/bin/google-chrome`
- browser mode: `--chrome-mode=chrome-for-testing`
- concurrency: `--concurrency=1`
- delay-render timeout: `--timeout=60000`

The frame range is inclusive. At 30 fps, frames `0-899` are 900 frames, which is 30 seconds.

## Frame Range Overrides

Do not make `npm run render:segment:local -- --frames=900-1799` the documented override mechanism. Because the script itself already contains `--frames=0-899`, appending another `--frames` creates duplicate flags. That may work in some CLI parsers, but it is ambiguous and not a stable project interface.

For alternate frame ranges, document the full manual Remotion CLI command from `remotion/`, replacing only the output path and `--frames` value:

    ./node_modules/.bin/remotion render src/index.ts SyncCutVideo out/segment-900-1799.mp4 --frames=900-1799 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

This keeps the package script reproducible while still giving developers a precise path for custom local segments.

## Preflight Before Rendering

Recommend running verified preflight manually before rendering:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Do not call preflight from the npm script. Keeping preflight manual has three benefits:

- It avoids coupling `remotion/package.json` to the repository Python virtual environment.
- It keeps the npm script focused on Remotion rendering only.
- It keeps Python from invoking or orchestrating Remotion.

Expected clean preflight state before a segment render is `status: warning` with `file_errors: 0`, where warnings are the known root timing warning plus missing optional `AI_VIDEO` and `B_ROLL` visual assets that will render placeholders.

## Browser and Sandbox Behavior

The segment script uses local Chrome because the default Remotion browser download path can fail in this environment with `getaddrinfo EAI_AGAIN remotion.media`.

The local Chrome path is:

    /usr/bin/google-chrome

Known sandbox behavior: local Chrome may fail to launch with `SIGTRAP` and `setsockopt: Operation not permitted`. This is an environment permission issue, not necessarily a Remotion component bug. If that happens during validation, rerun with Chrome launch permission if available and record both outcomes in this plan. Do not add unrelated workaround code.

Studio remains separate. Do not add `studio:local`, `remotion.config.ts`, or a GUI workflow in this phase.

## Plan of Work

Milestone 1 should make only documentation and script changes. Edit `remotion/package.json` to add `render:segment:local`. Edit `remotion/README.md` to add a concise "Segment Render" section after the smoke render section. The README section should explain when to use segment render, show `cd remotion` and `npm run render:segment:local`, state that it renders frames `0-899` to `out/segment.mp4`, state that this is 30 seconds at 30 fps, mention the local Chrome path and sandbox permission caveat, recommend verified preflight before rendering, and state that `out/segment.mp4` should not be committed. Do not edit `package-lock.json` unless npm rewrites it for a concrete reason.

Milestone 2 should validate the workflow. Regenerate timeline and props, prepare audio assets, run verified preflight, run Remotion typecheck, then run `npm run render:segment:local`. If browser launch is blocked by the sandbox, record the exact error and rerun with Chrome launch permission if available. Confirm `remotion/out/segment.mp4` exists and record its size. Run the Python test suite. Do not modify source unless a clear bug is discovered.

Milestone 3 should be a final review. Confirm the change stayed Remotion-docs/script-only, Python CLI behavior is unchanged, no full render was performed, generated artifacts are ignored, and commit candidates are only the plan, README, and package script. Rerun `pytest` and Remotion typecheck.

## Validation and Acceptance

From the repository root, regenerate and prepare data:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected preflight result for clean generated props: `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

From `remotion/`, run:

    npm run typecheck
    npm run render:segment:local

Expected result when Chrome launch is permitted: Remotion renders frames `0-899`, encodes 900 frames, and writes `out/segment.mp4`. Confirm with:

    ls -lh out/segment.mp4

From the repository root, run:

    .venv/bin/python -m pytest

Expected result: all Python tests pass.

Acceptance for the phase is:

- `remotion/package.json` contains `render:segment:local` with the exact fixed frame range and local Chrome flags.
- `remotion/README.md` documents the segment render workflow and artifact policy.
- Verified preflight runs before rendering and reports no file errors for prepared audio.
- `npm run typecheck` passes.
- `npm run render:segment:local` either succeeds and writes `remotion/out/segment.mp4`, or fails only due the known browser-launch sandbox issue and succeeds when Chrome launch permission is granted.
- `.venv/bin/python -m pytest` passes.
- No Python source or Remotion rendering source is changed.

## Idempotence and Recovery

The script is safe to rerun. It overwrites `remotion/out/segment.mp4` with a new generated segment artifact. That file is ignored by `.gitignore` and should not be committed.

If validation data is stale, rerun the repository-root regeneration commands. If verified preflight reports missing public audio files, rerun:

    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

If a local visual asset is missing, this phase does not require fixing it because missing optional `AI_VIDEO` and `B_ROLL` assets render placeholders. If a visual asset is marked prepared but missing on disk, fix that with the existing `prepare-visual-assets` workflow or remove the prepared public path before rendering; do not add asset copying to the segment script.

If Chrome fails with `SIGTRAP` or `setsockopt: Operation not permitted`, record the error and rerun with Chrome launch permission if available. Do not add `--no-sandbox` or other browser workarounds unless a future phase explicitly approves them.

## Artifacts and Commit Policy

Commit candidates for this phase should be:

- `docs/plans/remotion-segment-render.md`
- `remotion/package.json`
- `remotion/README.md`

Do not commit generated artifacts:

- `remotion/out/segment.mp4`
- `remotion/out/smoke.mp4`
- `remotion/out/preview.png`
- `timeline.json`
- `remotion/public/*`
- `assets/visuals/*`
- `.pytest_cache/`
- `__pycache__/`

Do not commit `remotion/props.json` if it only changed because of validation regeneration. Do not commit `package-lock.json` unless npm rewrites it for a concrete reason; a script-only manual edit should not require a lockfile change.

## Explicit Exclusions

Do not implement any of the following in this phase:

- full final MP4 rendering;
- render ranges that cover the full composition;
- Python commands that invoke Remotion;
- Remotion invocation from Python;
- direct ffmpeg or ffprobe calls;
- media probing, decoding, transcoding, trimming, or normalization;
- AI image or video generation;
- B-roll download, scraping, or external fetch;
- DOCX parsing;
- GUI or web app behavior;
- `remotion.config.ts`;
- package dependencies;
- Remotion component changes;
- changes to `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, or `preflight` behavior.

## Notes

2026-05-12: Created this plan to add a local 30-second Remotion segment render workflow. The plan keeps rendering under the standalone Remotion npm package, recommends manual verified preflight before rendering, and preserves Python CLI boundaries.
