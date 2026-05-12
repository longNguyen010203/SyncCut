# Add a local Remotion final render workflow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already build Remotion props, prepare public audio files, validate props with optional public-file verification, render a five-second smoke clip, and render a 30-second local segment with local Chrome. The next local developer workflow is a full Remotion composition render from the existing `remotion/props.json` to `remotion/out/final.mp4`.

After this phase, a developer should be able to run a verified preflight check from the repository root, then run:

    cd remotion
    npm run render:final:local

and produce `remotion/out/final.mp4` for the full current `SyncCutVideo` composition when local Chrome launch is permitted. This is a local Remotion render workflow only. It must not add Python commands that invoke Remotion, call Remotion from Python, call ffmpeg directly, generate AI video, download B-roll, fetch or scrape external media, probe/decode/transcode media, parse DOCX, add GUI or web app behavior, add dependencies, add `remotion.config.ts`, or change existing Python CLI behavior.

## Progress

- [x] (2026-05-12T14:21:13+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/remotion-render-smoke.md`, `docs/plans/remotion-segment-render.md`, `docs/plans/remotion-preview-environment.md`, `docs/plans/preflight-render-readiness.md`, `docs/plans/preflight-file-verification.md`, `remotion/README.md`, `remotion/package.json`, and `.gitignore`.
- [x] (2026-05-12T14:21:13+07:00) Inspected `remotion/package.json`, `remotion/README.md`, `remotion/src/index.ts`, `remotion/src/Root.tsx`, `remotion/src/Video.tsx`, and `remotion/props.json`.
- [x] (2026-05-12T14:21:13+07:00) Created this ExecPlan for the local Remotion final render workflow.
- [x] (2026-05-12T14:28:42+07:00) Implemented Milestone 1: added the fixed local final render script and README documentation.
- [x] (2026-05-12T15:08:26+07:00) Completed Milestone 2: validated fresh generated props, verified preflight, Remotion typecheck, full local final render, pytest, and artifact status.
- [ ] Implement Milestone 3: final review of scope, artifacts, validation, and commit policy.

## Surprises & Discoveries

- Observation: The current working tree is clean at plan creation.
  Evidence: `git status --short` printed no changes.
- Observation: The Remotion app already has verified local Chrome render scripts for smaller ranges.
  Evidence: `remotion/package.json` contains `render:smoke:local` for `--frames=0-149` and `render:segment:local` for `--frames=0-899`, both using `/usr/bin/google-chrome`, `--chrome-mode=chrome-for-testing`, `--concurrency=1`, and `--timeout=60000`.
- Observation: The current composition duration is about 12.5 minutes.
  Evidence: Inspecting `remotion/props.json` reported `composition.fps: 30`, `composition.duration_frames: 22584`, and `metadata.duration_sec: 752.79`.
- Observation: The root composition already derives all render metadata from `remotion/props.json`.
  Evidence: `remotion/src/Root.tsx` registers exactly one `Composition` with `id`, `durationInFrames`, `fps`, `width`, `height`, and `defaultProps` from `defaultProps.composition`.
- Observation: The video component already renders the exported timeline and section audio.
  Evidence: `remotion/src/Video.tsx` mounts `<SectionAudio sections={sections} />` and maps each scene to a Remotion `Sequence` using `scene.start_frame` and `scene.duration_frames`.
- Observation: Full render output is already ignored by the existing generated artifact policy.
  Evidence: `.gitignore` contains `remotion/out/`, so `remotion/out/final.mp4` will be excluded from commit.
- Observation: Prior render validation established a recurring sandbox limitation.
  Evidence: Earlier still, smoke, and segment renders failed in the default sandbox with Chrome launch errors such as `SIGTRAP` and `setsockopt: Operation not permitted`, then succeeded when Chrome launch permission was granted.
- Observation: Milestone 1 did not require dependency, lockfile, Python, Remotion component, props, or render artifact changes.
  Evidence: Only `remotion/package.json`, `remotion/README.md`, and this plan were edited. The new script is script-only, so `package-lock.json` did not need an update.
- Observation: Milestone 1 validation passed without rendering or launching Chrome.
  Evidence: From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed.
- Observation: Fresh generated props and prepared public audio passed verified preflight before final rendering.
  Evidence: `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The sandbox still blocks local Chrome launch for the final render command.
  Evidence: The first `npm run render:final:local` attempt failed with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and Chrome stderr `[48:48:0512/143307.894053:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`.
- Observation: The same final render command succeeds when Chrome launch is permitted.
  Evidence: The permitted rerun selected `Composition SyncCutVideo`, rendered the full `22584/22584` frames with no `--frames` flag, encoded `22584/22584`, and printed `+ out/final.mp4 46.2 MB`. `ls -lh out/final.mp4` reported `45M`.
- Observation: The final render did not require timeout, dependency, source, or Remotion component changes.
  Evidence: No delay-render timeout occurred, `--timeout=60000` remained unchanged, and no source code or package dependencies were edited during Milestone 2.

## Decision Log

- Decision: Add one fixed npm script named `render:final:local`.
  Rationale: Smoke and segment render workflows already use fixed, reproducible scripts. A fixed final render script keeps the local workflow simple and avoids building wrapper logic around Remotion.
  Date/Author: 2026-05-12 / Codex
- Decision: Do not include a `--frames` flag in the final render command.
  Rationale: The purpose of this phase is to render the full current Remotion composition. `remotion/src/Root.tsx` already supplies the full duration from `props.composition.duration_frames`, so omitting `--frames` is the clearest way to render the full composition.
  Date/Author: 2026-05-12 / Codex
- Decision: Use the same local Chrome flags as the verified still, smoke, and segment workflows.
  Rationale: The default Remotion browser download path can fail on `remotion.media` DNS, while `/usr/bin/google-chrome` with `--chrome-mode=chrome-for-testing` has worked in this environment when browser launch is permitted.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep `--concurrency=1` for the first final render workflow.
  Rationale: Full composition rendering is longer and heavier than smoke or segment rendering. Concurrency 1 reduces local resource pressure and matches the already verified render scripts.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep `--timeout=60000` unless validation shows delay-render timeout failures.
  Rationale: Remotion's timeout flag controls how long it waits for delayed rendering operations, not the total render duration. Smoke and segment renders succeeded with 60000 ms, and there is no current evidence that the full render needs a larger delay-render timeout.
  Date/Author: 2026-05-12 / Codex
- Decision: Recommend verified preflight before rendering, but keep it manual and outside the npm script.
  Rationale: Preflight is the correct readiness check, but the npm script should stay a Remotion-only command. Calling Python from npm would couple the Remotion package to the repository virtual environment and would blur the boundary that Python must not invoke Remotion.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documents and inspecting the current Remotion scripts, README, entrypoint, root composition, video component, generated props, and ignore rules. No source code, package file, README, generated artifact, Python CLI behavior, Remotion render script, dependency, or Remotion config has been changed yet for this phase.

The recommended implementation is intentionally small. Add one package script under `remotion/`, document it in `remotion/README.md`, validate with typecheck, pytest, verified preflight, and then either attempt the full render or explicitly record why it was not attempted. Do not edit Python source, Remotion rendering components, generated props schema, package dependencies, `package-lock.json`, or `remotion.config.ts` unless a clear bug or tool-driven rewrite is discovered.

Milestone 1 is complete. `remotion/package.json` now contains `render:final:local`, which runs `remotion render src/index.ts SyncCutVideo out/final.mp4 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000`. The command intentionally has no `--frames` flag, so it renders the full composition duration from `remotion/src/Root.tsx` and `remotion/props.json`. `remotion/README.md` now has a "Final Render" section after "Segment Render". It recommends verified preflight from the repository root, documents `cd remotion` and `npm run render:final:local`, states that the output is `out/final.mp4`, states that the current sample is around 22584 frames at 30 fps and 752.79 seconds, records the local Chrome path and browser mode, mentions sandbox browser-launch permission, warns that runtime can be long, and says not to commit `out/final.mp4`.

Milestone 1 validation passed without rendering. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. No Python source, Remotion rendering source, `remotion/props.json`, dependency, `package-lock.json`, `remotion.config.ts`, direct ffmpeg call, media probing/transcoding, AI generation, B-roll download, DOCX parsing, GUI/web app behavior, Chrome invocation, or render artifact was added.

Milestone 2 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Verified preflight before rendering matched the expected warning-only result. It reported `status: warning`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `fps: 30`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The warnings were the known root props warning plus 17 missing optional `AI_VIDEO` and `B_ROLL` visual asset warnings. The errors section printed `none`.

Remotion validation passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. The first `npm run render:final:local` run failed in the sandbox with the known browser-launch error: `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[48:48:0512/143307.894053:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. The rerun with Chrome launch permission succeeded. It bundled the project, copied the 12.1 MB public directory, selected `Composition SyncCutVideo`, rendered and encoded the full `22584/22584` frames, and wrote `out/final.mp4`. Remotion printed `out/final.mp4 46.2 MB`; `ls -lh out/final.mp4` reported a 45M file.

Final Python validation passed. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. `git status --short --ignored` showed commit candidates `remotion/README.md`, `remotion/package.json`, and `docs/plans/remotion-final-render.md`; ignored generated artifacts included `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.

Generated artifact and commit policy after Milestone 2: do not commit `timeline.json`, `remotion/public/*`, `remotion/out/final.mp4`, any other `remotion/out/*` preview outputs, `assets/visuals/*`, `.pytest_cache/`, or `__pycache__/`. Do not commit `remotion/props.json` if it only changed because of validation regeneration. Commit candidates remain `docs/plans/remotion-final-render.md`, `remotion/package.json`, and `remotion/README.md`. No source changes were needed during validation, and no Python command invoking Remotion, direct ffmpeg call, media probing/transcoding, AI generation, B-roll download, DOCX parsing, GUI/web app, dependency change, `remotion.config.ts`, timeout change, or Remotion component change was added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The Python CLI creates and prepares data for Remotion. It should not invoke Remotion rendering in this phase. The relevant repository-root data workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The optional local visual asset workflow may also be run before final rendering if local files for `AI_VIDEO` and `B_ROLL` scenes exist:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

Missing `AI_VIDEO` and `B_ROLL` visual assets are warnings, not errors, because the Remotion components render placeholders when local visual files are absent. Missing prepared audio public files are errors because the final render would omit narration.

The Remotion app consumes `remotion/props.json`. `remotion/src/index.ts` registers `RemotionRoot`. `remotion/src/Root.tsx` registers one composition using `defaultProps.composition.id`, `duration_frames`, `fps`, `width`, and `height`. The composition id is currently `SyncCutVideo`. `remotion/src/Video.tsx` renders section audio and maps every scene to a Remotion `Sequence` using exported `scene.start_frame` and `scene.duration_frames`.

Current generated props have:

    composition.id: SyncCutVideo
    composition.width: 1920
    composition.height: 1080
    composition.fps: 30
    composition.duration_frames: 22584
    metadata.duration_sec: 752.79
    metadata.total_scenes: 33
    metadata.total_sections: 7
    assets.audio: 7
    assets.visuals: 0

Current Remotion scripts in `remotion/package.json` are:

    "studio": "remotion studio src/index.ts"
    "typecheck": "tsc --noEmit"
    "still": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0"
    "still:local": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing"
    "render:smoke:local": "remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"
    "render:segment:local": "remotion render src/index.ts SyncCutVideo out/segment.mp4 --frames=0-899 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

Current generated-artifact ignores include:

    remotion/public
    remotion/out/
    timeline.json
    assets/visuals/
    __pycache__/
    .pytest_cache/

`remotion/out/final.mp4` is therefore already ignored.

## Existing Smoke and Segment Render Workflows

The smoke render workflow is:

    cd remotion
    npm run render:smoke:local

It runs:

    remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

Frames `0-149` are inclusive. At 30 fps, 150 frames equals 5 seconds. This proves Remotion can bundle the app, load props, use public assets, launch Chrome, render a short frame range, encode video, and write a small artifact.

The segment render workflow is:

    cd remotion
    npm run render:segment:local

It runs:

    remotion render src/index.ts SyncCutVideo out/segment.mp4 --frames=0-899 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

Frames `0-899` are inclusive. At 30 fps, 900 frames equals 30 seconds. This provides more confidence than smoke rendering without rendering the full composition.

Both workflows use local Chrome to avoid the default Chrome Headless Shell download path, which can fail in this environment with `getaddrinfo EAI_AGAIN remotion.media`.

## Why Final Render Is Now Appropriate

The project now has multiple layers of readiness checks before a full render attempt:

- `validate-timeline` confirms the source timeline structure and timing before export.
- `export-remotion` creates `remotion/props.json`.
- `prepare-remotion-assets` copies section audio into `remotion/public/audio/` and annotates props with public audio paths.
- `preflight --verify-files --public-dir remotion/public` checks props structure, prepared audio readiness, optional visual readiness, and existence of prepared public files.
- `npm run typecheck` confirms the Remotion TypeScript app compiles.
- `npm run render:smoke:local` and `npm run render:segment:local` have already proven shorter local renders when Chrome launch is permitted.

A final local render script is therefore appropriate as the next local developer workflow. It is still not a Python command, not ffmpeg assembly, and not an automated production pipeline. It is a manual Remotion render command exposed through npm for consistency with the smaller workflows.

## Proposed Final Render Command

Add this script to `remotion/package.json`:

    "render:final:local": "remotion render src/index.ts SyncCutVideo out/final.mp4 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

This command renders:

- Remotion command: `render`
- entrypoint: `src/index.ts`
- composition id: `SyncCutVideo`
- output: `out/final.mp4`
- frame range: none, so Remotion renders the full composition duration from `Root.tsx`
- local browser: `--browser-executable=/usr/bin/google-chrome`
- browser mode: `--chrome-mode=chrome-for-testing`
- concurrency: `--concurrency=1`
- delay-render timeout: `--timeout=60000`

Do not add `--frames` to this command. The absence of `--frames` is intentional and means "render the full current composition."

## Timeout Choice

Use `--timeout=60000` for the initial final render script. In Remotion, this timeout is for waiting on delayed render operations, not a maximum wall-clock duration for the whole video render. The existing smoke and segment workflows use the same value successfully, and the current app does not perform remote fetches or complex delayed loading.

If Milestone 2 fails with an explicit Remotion delay-render timeout, record the exact error before changing the script. A larger value such as `--timeout=120000` can be considered only with that evidence. Do not increase timeout preemptively just because the final video is longer.

## Preflight Before Rendering

Run verified preflight manually before final rendering:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Do not call preflight from `render:final:local`. Keeping preflight manual has three benefits:

- It avoids coupling `remotion/package.json` to `.venv`.
- It keeps npm scripts focused on Remotion rendering.
- It preserves the boundary that Python prepares and reports data, while Remotion renders when the developer explicitly runs npm commands.

Expected clean preflight state before final rendering is `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The warning status is acceptable because missing optional AI/B-roll local visuals render placeholders.

## Runtime and Local Machine Constraints

The current composition is 22584 frames at 30 fps, about 752.79 seconds or 12.5 minutes of video. A full local render can take much longer than the video duration, especially with `--concurrency=1`. The 900-frame segment render previously produced a 1.8 MB file and took long enough to show browser permission behavior. A full render is about 25.1 times more frames than that segment, so a run on the same machine may take tens of minutes and produce a much larger MP4.

Milestone 2 may attempt the full render if the environment and time budget permit. If the render is too slow, blocked, or impractical, record the exact reason and do not add workaround code. At minimum, Milestone 2 must run verified preflight, Remotion typecheck, and pytest.

## Browser and Sandbox Behavior

The script uses local Chrome:

    /usr/bin/google-chrome

with:

    --chrome-mode=chrome-for-testing

This avoids the default Remotion Chrome Headless Shell download path that can fail with `getaddrinfo EAI_AGAIN remotion.media`.

Known sandbox behavior: local Chrome may fail to launch with `SIGTRAP` and `setsockopt: Operation not permitted`. This is an environment permission issue, not necessarily a Remotion component bug. If that happens during validation, rerun with Chrome launch permission if available and record both outcomes. Do not add `remotion.config.ts`, Chrome sandbox workarounds, dependency changes, or unrelated render code.

Studio remains separate. Do not add `studio:local`, GUI behavior, or web app behavior in this phase.

## Plan of Work

Milestone 1 should make only documentation and script changes. Edit `remotion/package.json` to add `render:final:local`. Edit `remotion/README.md` to add a concise "Final Render" section after the segment render section. The README section should explain when to use final render, show the verified preflight command, show `cd remotion` and `npm run render:final:local`, state that the output is `out/final.mp4`, state that this renders the full composition, mention local Chrome and sandbox permission behavior, warn that runtime can be long, and state that `out/final.mp4` must not be committed. Do not edit `package-lock.json` unless npm rewrites it for a concrete reason.

Milestone 2 should validate the workflow. Regenerate timeline and props, prepare audio assets, run verified preflight, run Remotion typecheck, and run pytest. Attempt the full render only if practical in the local environment. If it is attempted and succeeds, confirm `remotion/out/final.mp4` exists and record its size. If it is blocked by sandbox browser permissions, rerun with Chrome launch permission if available. If it is not attempted because of expected long runtime, record that explicitly in this plan.

Milestone 3 should be a final review. Confirm the change stayed within local Remotion workflow scope, Python CLI behavior is unchanged, no Remotion rendering source or dependencies changed, generated artifacts are ignored, and commit candidates are only the plan, README, and package script. Rerun `pytest` and Remotion typecheck.

## Concrete Steps

For Milestone 1, edit `remotion/package.json` and add:

    "render:final:local": "remotion render src/index.ts SyncCutVideo out/final.mp4 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

Place it near the existing `render:smoke:local` and `render:segment:local` scripts.

Then edit `remotion/README.md` and add a "Final Render" section after "Segment Render". Include these commands:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

    cd remotion
    npm run render:final:local

Document that the output is:

    out/final.mp4

and that it renders the full `SyncCutVideo` composition, currently around 22584 frames at 30 fps.

For Milestone 1 validation, do not render. Run:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

For Milestone 2 validation, regenerate and verify data from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Then run:

    cd remotion
    npm run typecheck
    npm run render:final:local

If the render succeeds, inspect:

    ls -lh out/final.mp4

Then from the repository root run:

    .venv/bin/python -m pytest
    git status --short --ignored

## Validation and Acceptance

Acceptance for Milestone 1:

- `remotion/package.json` contains `render:final:local` with no `--frames` flag.
- `remotion/README.md` documents verified preflight, the final render command, `out/final.mp4`, the full-composition scope, local Chrome usage, sandbox permission behavior, expected long runtime, and artifact policy.
- `npm run typecheck` passes from `remotion/`.
- `.venv/bin/python -m pytest` passes from the repository root.
- No Python source, Remotion rendering source, dependencies, `package-lock.json`, generated props, generated assets, `remotion.config.ts`, or final output is changed by Milestone 1.

Acceptance for Milestone 2:

- Fresh `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` complete successfully.
- Verified preflight reports `status: warning`, prepared audio with `audio_missing_public_path: 0`, and `file_errors: 0` for clean generated props.
- `npm run typecheck` passes.
- `.venv/bin/python -m pytest` passes.
- If `npm run render:final:local` is attempted and Chrome launch is permitted, Remotion renders the full composition and writes `remotion/out/final.mp4`; record the file size.
- If full render is too slow or blocked by environment, record the exact limitation. Do not add workaround code.

Acceptance for Milestone 3:

- The final review confirms the phase stayed within a local Remotion workflow.
- `render:final:local` renders the full composition by omitting `--frames`.
- The script uses local Chrome flags and avoids the default `remotion.media` browser download path.
- Preflight remains a manual command outside the npm script.
- Python CLI behavior remains unchanged.
- Remotion rendering components remain unchanged unless a clear bug was discovered and documented.
- Generated outputs remain ignored and are not commit candidates.

## Explicit Exclusions

Do not implement or add any of the following in this phase:

- Python commands that invoke Remotion.
- Remotion invocation from Python.
- Direct ffmpeg or ffprobe calls.
- Media probing, decoding, transcoding, trimming, or normalization.
- AI video generation.
- B-roll downloading.
- Fetching or scraping external media.
- DOCX parsing.
- GUI or web app behavior.
- `remotion.config.ts`.
- Package dependencies.
- Remotion rendering component changes unless a clear bug is discovered.
- Changes to `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, or `preflight` behavior.

## Idempotence and Recovery

The final render script is safe to rerun. It overwrites `remotion/out/final.mp4` with a new generated MP4. That file is ignored by `.gitignore` and should not be committed.

If validation data is stale, rerun the repository-root regeneration commands. If verified preflight reports missing public audio files, rerun:

    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

If verified preflight reports missing optional `AI_VIDEO` or `B_ROLL` visual assets, the render can still proceed with placeholders. If it reports unsupported prepared visual paths or missing prepared visual files, fix those with the existing local visual asset workflow before rendering:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

If Chrome launch fails with `SIGTRAP` and `setsockopt: Operation not permitted`, rerun with browser launch permission if available. Do not add repository code or config to bypass local sandbox policy.

## Artifacts and Notes

Generated artifacts that must not be committed:

    timeline.json
    remotion/public/*
    remotion/out/preview.png
    remotion/out/smoke.mp4
    remotion/out/segment.mp4
    remotion/out/final.mp4
    assets/visuals/*
    __pycache__/
    .pytest_cache/

Expected commit candidates after implementation are:

    docs/plans/remotion-final-render.md
    remotion/package.json
    remotion/README.md

`remotion/props.json` may change if validation regenerates sample props. Do not commit it if it only changed because of generated validation. Commit it only if the project intentionally updates the sample props and the diff is reviewed.
