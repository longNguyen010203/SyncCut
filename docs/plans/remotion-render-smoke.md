# Add a short Remotion render smoke workflow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can now generate Remotion props, prepare section audio, type-check the Remotion project, render still frames with local Chrome when browser launch is permitted, and document the environment limitations. The next useful proof is a short video render smoke test: render only the first few seconds of the existing Remotion composition to confirm that Remotion can bundle the app, launch Chrome, render multiple frames, include the prepared section audio path, and write a video file without attempting the full 12 to 15 minute final output.

After this phase, a developer should have a documented command and, if verified, an npm script that renders a short video segment such as `remotion/out/smoke.mp4` from frames `0-149`. At 30 fps, frames `0-149` are 150 frames, or 5 seconds. This phase deliberately does not render the full final MP4, call ffmpeg directly, add a Python wrapper around Remotion, generate AI video, download B-roll, parse DOCX, add GUI or web app behavior, or change the existing Python CLI behavior.

## Progress

- [x] (2026-05-11T00:00:00Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, `docs/plans/export-remotion-props.md`, `docs/plans/remotion-project-skeleton.md`, `docs/plans/remotion-audio-assets.md`, `docs/plans/remotion-basic-visual-components.md`, `docs/plans/remotion-preview-environment.md`, `remotion/README.md`, and `remotion/package.json`.
- [x] (2026-05-11T00:00:00Z) Inspected installed Remotion 4.0.459 CLI option files for frame-range, duration, timeout, concurrency, browser executable, and Chrome mode behavior.
- [x] (2026-05-11T00:00:00Z) Verified that the local Remotion binary exists at `remotion/node_modules/.bin/remotion` and that `.gitignore` currently ignores `remotion/node_modules` and `remotion/public` but not `remotion/out` or `timeline.json`.
- [x] (2026-05-11T00:00:00Z) Created this ExecPlan for the short Remotion render smoke workflow.
- [x] (2026-05-11T00:00:00Z) Implemented Milestone 1: regenerated fresh data and assets, verified the manual local render smoke command, confirmed `out/smoke.mp4`, and ran typecheck plus pytest.
- [x] (2026-05-11T00:00:00Z) Implemented Milestone 2: added the verified `render:smoke:local` script, documented the smoke workflow, ignored generated artifacts, and reran validation.
- [x] (2026-05-11T00:00:00Z) Completed Milestone 3: regenerated fresh data and assets, reran final Remotion and Python validation, inspected generated artifacts, and recorded commit policy.

## Surprises & Discoveries

- Observation: The installed Remotion CLI supports short video rendering with `--frames`, not `--frame-range`.
  Evidence: `remotion/node_modules/@remotion/renderer/dist/options/frames.js` defines CLI flag `frames` and accepts a single number or a range such as `0-9`; `remotion/node_modules/@remotion/cli/dist/render.js` rejects `--frame` for render and says to use `--frames`.
- Observation: The `--frames` range is inclusive.
  Evidence: Context7 Remotion documentation states that `Config.setFrameRange([0, 20])` renders the first 21 frames, and local Remotion option text describes a range such as `0-9` as a subset of frames. Therefore `--frames=0-149` produces 150 frames.
- Observation: The installed Remotion CLI also supports `--duration`, `--timeout`, and `--concurrency`.
  Evidence: Local option files define `override-duration.js` with CLI flag `duration`, `timeout.js` with CLI flag `timeout` and default `30000`, and `concurrency.js` with CLI flag `concurrency`.
- Observation: The local browser strategy from Phase 7 remains relevant for video rendering.
  Evidence: Local option files define `browser-executable` and `chrome-mode`, and Phase 7 proved `npm run still:local` avoids the `remotion.media` download path when Chrome launch is permitted.
- Observation: A render smoke test will create a video artifact, but it is not the final SyncCut MP4.
  Evidence: The proposed output is `remotion/out/smoke.mp4` for frames `0-149`, while the current composition duration is 22584 frames. The smoke artifact is only a short validation clip.
- Observation: Fresh data regeneration for Milestone 1 succeeded with the known validation warning.
  Evidence: `validate-timeline` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and `Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `export-remotion` reported `duration_frames: 22584`, and `prepare-remotion-assets` reported `audio_reused: 7`, `audio_copied: 0`, `audio_overwritten: 0`.
- Observation: The manual render command is valid and avoids the `remotion.media` download path, but Chrome launch is blocked by the default sandbox.
  Evidence: Running `./node_modules/.bin/remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000` first failed with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and Chrome stderr `[36:36:0511/202541.799416:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. It did not attempt to download from `remotion.media`.
- Observation: The same manual render command succeeds when Chrome launch is permitted.
  Evidence: The permitted rerun rendered `Rendered 149/150`, encoded `Encoded 150/150`, and printed `+ out/smoke.mp4 311.7 kB`. `ls -lh out/smoke.mp4` reported `305K`.
- Observation: The new npm script behaves the same as the verified manual command.
  Evidence: `npm run render:smoke:local` first failed in the sandbox with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[48:48:0511/203347.733935:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. Rerunning the same script with Chrome launch permission succeeded, rendered `149/150`, encoded `150/150`, and printed `out/smoke.mp4 311.7 kB`.
- Observation: The generated artifact ignore rules now hide expected render and Python cache outputs from normal status.
  Evidence: `git status --short` after validation showed only `M .gitignore`, `M remotion/README.md`, `M remotion/package.json`, and `?? docs/plans/remotion-render-smoke.md`. `git status --ignored --short remotion/out timeline.json synccut/__pycache__ tests/__pycache__ .pytest_cache` showed those paths as ignored.
- Observation: Final validation reproduced the known sandbox Chrome-launch limitation for both local still and smoke render commands, and both succeeded with Chrome launch permission.
  Evidence: `npm run still:local` first failed with `SIGTRAP` and `[46:46:0511/204322.725319:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`, then succeeded with `Rendered 1/1` and `+ out/preview.png`. `npm run render:smoke:local` first failed with `SIGTRAP` and `[48:48:0511/204408.627796:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`, then succeeded with `Rendered 149/150`, `Encoded 150/150`, and `out/smoke.mp4 311.7 kB`.
- Observation: Final generated render artifacts are small and ignored.
  Evidence: `ls -lh remotion/out/preview.png remotion/out/smoke.mp4` reported `129K` for `preview.png` and `305K` for `smoke.mp4`; `git status --ignored --short` showed `!! remotion/out/`.

## Decision Log

- Decision: Use `--frames=0-149` for the initial render smoke segment.
  Rationale: The current composition is 30 fps, so 150 frames is 5 seconds. This is long enough to exercise multi-frame rendering and early section audio while remaining much smaller than the full 22584-frame composition.
  Date/Author: 2026-05-11 / Codex
- Decision: Use local Chrome flags for the render smoke command.
  Rationale: The default still command fails in this environment when it tries to download Chrome Headless Shell from `remotion.media`. Phase 7 verified that `/usr/bin/google-chrome` with `--chrome-mode=chrome-for-testing` can render a still when Chrome launch is permitted.
  Date/Author: 2026-05-11 / Codex
- Decision: Keep audio enabled in the smoke render unless a clear render issue requires a documented adjustment.
  Rationale: The current Remotion app mounts section audio from `remotion/public/audio` using section timing. A short video smoke test should verify the same composition behavior users will preview, including audio references. If audio is the cause of a render failure, record the exact error before deciding whether a muted smoke script is needed.
  Date/Author: 2026-05-11 / Codex
- Decision: Add no script until the exact render command is verified.
  Rationale: Phase 7 only added `still:local` after the local Chrome command succeeded. The render smoke script should follow the same standard so package scripts do not imply behavior that has not worked in this environment.
  Date/Author: 2026-05-11 / Codex
- Decision: Do not add `remotion.config.ts` for this phase.
  Rationale: The preview strategy intentionally avoided machine-specific committed config. The render smoke path can use explicit CLI flags and a package script without adding config that hard-codes local browser behavior.
  Date/Author: 2026-05-11 / Codex
- Decision: Add `render:smoke:local` to `remotion/package.json` after Milestone 1 verified the command.
  Rationale: The command rendered the 150-frame smoke clip successfully when Chrome launch was permitted and avoided the blocked `remotion.media` browser download path. A script makes the verified workflow repeatable without adding Python wrapping or Remotion config.
  Date/Author: 2026-05-11 / Codex
- Decision: Add `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/` to `.gitignore`.
  Rationale: `remotion/out/` contains generated still and smoke render artifacts, `timeline.json` is regenerated CLI output, and Python cache directories are test/runtime output. These should not be committed, while `remotion/props.json`, `remotion/README.md`, and plan files remain trackable.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

This plan has been created after reading the required project documents, inspecting the current Remotion package and README, and researching installed Remotion CLI behavior locally. No source code, package script, README, gitignore, generated artifact, or Python CLI behavior has been changed yet for this phase.

Milestone 1 is complete. Fresh timeline and props data were regenerated from examples, `validate-timeline` passed with the known one-gap warning, `export-remotion` wrote `remotion/props.json` with 33 scenes and 22584 frames, and `prepare-remotion-assets` reused all seven prepared audio files. The manual local render smoke command was tested exactly as planned. The sandboxed run failed with the known browser-launch permission signature, `SIGTRAP` and `setsockopt: Operation not permitted`, without trying to download Chrome Headless Shell from `remotion.media`. The same command succeeded when Chrome launch was permitted, rendered frames `0-149` as 150 frames, encoded `out/smoke.mp4`, and produced a 305K file. From `remotion/`, `npm run typecheck` passed. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and all passed. No source code, package script, README, `.gitignore`, Remotion config, Python CLI behavior, final full MP4 render, direct ffmpeg call, Python Remotion wrapper, AI video generation, or B-roll downloading was added in this milestone.

Milestone 2 is complete. `remotion/package.json` now contains `render:smoke:local`, which runs the verified local Chrome render command for frames `0-149` into `out/smoke.mp4`. `remotion/README.md` now has a concise "Render Smoke Test" section documenting `cd remotion`, `npm run render:smoke:local`, the output path, the 150-frame five-second range, the local Chrome path, the sandbox browser-launch caveat, and that the smoke clip is not the final MP4. `.gitignore` now excludes `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/` while leaving `remotion/props.json`, `docs/plans/*.md`, and `remotion/README.md` trackable. Validation passed: `npm run typecheck` completed successfully, `npm run render:smoke:local` hit the known sandbox browser-launch failure and then succeeded with Chrome launch permission, and `.venv/bin/python -m pytest` collected 114 tests and all passed. The generated `remotion/out/smoke.mp4` exists at 305K and is ignored. No Python source files, Remotion rendering source files, `remotion.config.ts`, final full MP4 render, direct ffmpeg call, Python Remotion wrapper, AI video generation, or B-roll downloading were added.

Milestone 3 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Final Remotion validation passed with the documented environment caveat. From `remotion/`, `npm run typecheck` passed. `npm run still:local` failed in the sandbox with `SIGTRAP` and `setsockopt: Operation not permitted`, then succeeded with Chrome launch permission and rendered `out/preview.png`. `npm run render:smoke:local` failed in the sandbox with the same Chrome launch permission error, then succeeded with Chrome launch permission, rendered frames `0-149` as 150 frames, encoded `out/smoke.mp4`, and printed `out/smoke.mp4 311.7 kB`.

Final Python validation passed. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and all 114 passed. Generated artifacts observed were `remotion/out/preview.png` at 129K, `remotion/out/smoke.mp4` at 305K, and the copied audio files under `remotion/public/audio/`: `01_HOOK.mp3`, `02_INTRO.mp3`, `03_MECHANISM_1.mp3`, `04_MECHANISM_2.mp3`, `05_MECHANISM_3.mp3`, `06_MECHANISM_4.mp3`, and `07_CONCLUSION.mp3`.

Final artifact policy is enforced by `.gitignore`. `git status --short` showed only the intended commit candidates: `M .gitignore`, `M remotion/README.md`, `M remotion/package.json`, and `?? docs/plans/remotion-render-smoke.md`. `git status --ignored --short remotion/out timeline.json remotion/public/audio synccut/__pycache__ tests/__pycache__ .pytest_cache` showed `.pytest_cache/`, `remotion/out/`, `remotion/public/`, `synccut/__pycache__/`, `tests/__pycache__/`, and `timeline.json` as ignored. Commit policy for this phase is: commit `docs/plans/remotion-render-smoke.md`, `remotion/package.json`, `remotion/README.md`, and `.gitignore`; do not commit `remotion/out/preview.png`, `remotion/out/smoke.mp4`, `timeline.json`, `remotion/public/audio/*.mp3`, `__pycache__/`, or `.pytest_cache/`. No `remotion.config.ts`, final full MP4 render, direct ffmpeg call, Python Remotion wrapper, AI video generation, B-roll downloading, GUI, or web app behavior was added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The Python CLI creates data for Remotion but should not invoke Remotion rendering in this phase. The existing Python workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

The Remotion project consumes `remotion/props.json` through `remotion/src/props.ts`. `remotion/src/Root.tsx` registers one composition whose id is `SyncCutVideo`, width is 1920, height is 1080, fps is 30, and duration comes from `props.composition.duration_frames`. `remotion/src/Video.tsx` maps every scene to a Remotion `Sequence` using `scene.start_frame` and `scene.duration_frames`, and it mounts section audio through `remotion/src/components/SectionAudio.tsx`.

Current Remotion scripts in `remotion/package.json` are:

    "studio": "remotion studio src/index.ts"
    "typecheck": "tsc --noEmit"
    "still": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0"
    "still:local": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing"

Phase 7 established these browser facts:

- `npm run still` can fail because Remotion tries to download Chrome Headless Shell from `remotion.media` and DNS lookup fails with `getaddrinfo EAI_AGAIN remotion.media`.
- `npm run still:local` uses `/usr/bin/google-chrome` and avoids the `remotion.media` download path.
- In the sandbox, local Chrome launch can fail with `SIGTRAP` and `setsockopt: Operation not permitted`; rerunning with Chrome launch permission succeeded.
- `npm run studio -- --no-open --ipv4` still fails in this environment with `uv_interface_addresses returned Unknown system error 1` from Node `os.networkInterfaces()`.

The current working tree already contains uncommitted Phase 7 changes and generated artifacts. Do not revert them. At plan creation, `git status --short` showed `M remotion/package.json`, untracked `docs/plans/remotion-preview-environment.md`, untracked `remotion/README.md`, untracked `remotion/out/`, untracked `synccut/__pycache__/`, untracked `tests/__pycache__/`, and untracked `timeline.json`.

## What Render Smoke Means

A render smoke test is a deliberately small render that proves the rendering pipeline can run end-to-end for the current Remotion composition. In this phase, "end-to-end" means Remotion can bundle the React app, load `remotion/props.json`, read static assets from `remotion/public`, launch a browser, render a short range of frames, encode a small video file, and write it under `remotion/out/`.

It does not mean the final video is complete. It does not mean all scenes, all section audio, all visual types, or production encoding settings are validated. It does not create the final MP4 deliverable.

## Why Full Final MP4 Is Out of Scope

The current composition is around 22584 frames. At 30 fps, that is about 752.8 seconds, or roughly 12.5 minutes. Rendering that full composition would be slow, would produce a large generated artifact, and would move this phase from environment validation toward final assembly. The user explicitly requested a short proof-of-concept or smoke test and explicitly excluded full final MP4 rendering.

The smoke render must therefore use a short frame range such as frames `0-149` or `0-299`. If frame-range rendering is unavailable or fails due a Remotion CLI bug, do not fall back to full rendering. Record the failure and stop.

## Installed Remotion CLI Options

The installed Remotion version is 4.0.459 for both `remotion` and `@remotion/cli`. The local binary exists at `remotion/node_modules/.bin/remotion`.

The installed CLI options relevant to this phase are:

- `render`: command used for video output, with shape `remotion render src/index.ts SyncCutVideo out/smoke.mp4`.
- `--frames=0-149`: render an inclusive frame range. This is the main option for short segment rendering.
- `--duration=<frames>`: override composition duration in frames. This exists but is less precise than `--frames` for a smoke segment because it changes the selected composition metadata rather than explicitly choosing a render range.
- `--timeout=<milliseconds>`: increase the delay-render timeout if asset loading needs more than the default 30000 ms.
- `--concurrency=<number-or-percent>`: limit render concurrency. For this smoke test, `--concurrency=1` is acceptable to reduce resource pressure.
- `--browser-executable=/usr/bin/google-chrome`: use the locally installed Chrome executable.
- `--chrome-mode=chrome-for-testing`: use Chrome for Testing mode instead of the default headless shell path.

The installed CLI does not expose a `--frame-range` flag in the inspected option files. Use `--frames`.

## Proposed Smoke Command

The initial manual command to verify is:

    cd remotion
    ./node_modules/.bin/remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

The proposed script, only after that command is verified, is:

    "render:smoke:local": "remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

The output path is `remotion/out/smoke.mp4`. Keep all smoke output under `remotion/out/`.

## Audio Strategy

The smoke render should include audio by default. The Remotion app already mounts one audio track per section when `section.audio.public_path` exists, and the data regeneration workflow prepares these paths by copying source audio to `remotion/public/audio/`.

For frames `0-149`, the render should include the first five seconds of the first section's audio if the environment and encoder support audio. Do not add fades, audio trimming, transcoding, probing, or a separate audio workflow. Do not call ffmpeg directly. If Remotion rendering fails specifically because of audio handling, record the exact error in this plan before deciding whether a muted smoke render is appropriate.

## Plan of Work

First, verify the render command manually from `remotion/`. If the sandbox blocks Chrome launch with the same `SIGTRAP` or `setsockopt: Operation not permitted` error seen in Phase 7, rerun the same command with permission to launch Chrome and record both outcomes. If the command tries to download from `remotion.media`, the browser flags are wrong or not being honored; correct the command before adding a script.

If the local render command succeeds, update `remotion/package.json` with `render:smoke:local`. Do not update `package-lock.json` for a script-only change unless npm rewrites it for a concrete reason. Update `remotion/README.md` with a short "Render Smoke" section that shows `npm run render:smoke:local`, states that it renders frames `0-149` to `out/smoke.mp4`, and repeats that the artifact is not the final video and should not be committed.

Add `remotion/out/` to `.gitignore` because Phase 7 already produced `remotion/out/preview.png` and this phase will produce `remotion/out/smoke.mp4`. If `timeline.json` and Python `__pycache__/` are still unignored, either add them to `.gitignore` in the same artifact-policy change or explicitly record why they remain manual cleanup items. Do not remove generated artifacts with destructive commands unless the user asks.

Do not edit Python source files, Remotion rendering components, `remotion/src/Root.tsx`, `remotion/src/Video.tsx`, `remotion/src/components/*`, or `remotion.config.ts`.

## Milestones

### Milestone 1: Verify the manual local render smoke command

Regenerate fresh data and assets from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Then run the manual render command from `remotion/`:

    ./node_modules/.bin/remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000

If it succeeds, confirm the artifact exists:

    ls -lh out/smoke.mp4

If it fails, record the exact error in `Surprises & Discoveries` and do not add the npm script. If it fails only because Chrome launch is blocked by sandbox permissions, rerun the same command with Chrome launch permission and record both the sandbox failure and permitted result.

Validation:

    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

### Milestone 2: Add the verified npm script and documentation

Only if Milestone 1 verifies the local render command, update `remotion/package.json` with:

    "render:smoke:local": "remotion render src/index.ts SyncCutVideo out/smoke.mp4 --frames=0-149 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000"

Update `remotion/README.md` with a concise render smoke section. The section should explain that `npm run render:smoke:local` renders a five-second smoke clip to `out/smoke.mp4`, uses local Chrome, may require browser launch permission, and is not the final MP4.

Update `.gitignore` to exclude `remotion/out/`. Prefer also excluding `timeline.json`, `__pycache__/`, and `.pytest_cache/` if they are still showing up as generated untracked artifacts during validation. Do not exclude `remotion/props.json`, because it is sample input for the Remotion project and may be committed when intentionally regenerated.

Validation:

    cd remotion
    npm run typecheck
    npm run render:smoke:local
    cd ..
    .venv/bin/python -m pytest

If `npm run render:smoke:local` hits a sandbox browser-launch permission issue, rerun with permission and record both outcomes.

### Milestone 3: Final validation and artifact policy review

Run the full data regeneration and validation sequence:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    cd remotion
    npm run typecheck
    npm run still:local
    npm run render:smoke:local
    cd ..
    .venv/bin/python -m pytest

Inspect artifacts:

    ls -lh remotion/out/preview.png remotion/out/smoke.mp4
    find remotion/public/audio -maxdepth 1 -type f | sort
    git status --short

Record the final results in this plan. Commit policy should be: commit this plan, `remotion/package.json`, `remotion/README.md`, and `.gitignore` if it is updated. Do not commit `remotion/out/smoke.mp4`, `remotion/out/preview.png`, `timeline.json`, `remotion/public/audio/*.mp3`, or Python cache directories.

## Validation and Acceptance

This phase is accepted when a developer can run a documented command that renders a short video smoke artifact or, if the environment blocks browser launch, can see the exact recorded limitation and know that the command was verified when browser launch was permitted.

The primary expected success output is:

    remotion/out/smoke.mp4

The smoke file should be small compared with a full render, should correspond to frames `0-149`, and should be treated as generated output. TypeScript validation must pass with:

    cd remotion
    npm run typecheck

Python validation must pass with:

    .venv/bin/python -m pytest

Do not require Studio validation for this phase; Studio remains blocked in this environment by the separate `uv_interface_addresses` issue.

## Generated Artifacts Policy

Do not commit these generated artifacts:

- `remotion/out/smoke.mp4`
- `remotion/out/preview.png`
- `timeline.json`
- `remotion/public/audio/*.mp3`
- `synccut/__pycache__/`
- `tests/__pycache__/`
- `.pytest_cache/`

The directory `remotion/public/` is already ignored. Add `remotion/out/` to `.gitignore` during implementation if it is not already ignored. `remotion/props.json` is sample input for the Remotion project and may be committed when intentionally regenerated; do not add it to `.gitignore`.

## Idempotence and Recovery

The data regeneration commands are idempotent: rerunning them overwrites `timeline.json` and `remotion/props.json`, and `prepare-remotion-assets` reuses existing copied audio when the bytes match.

The smoke render command overwrites `remotion/out/smoke.mp4` by default because the current Remotion render command path accepts overwrite behavior unless `--no-overwrite` is used. If a render fails halfway, rerun the same command after resolving the environment issue. Do not delete artifacts with destructive commands unless the user explicitly asks.

If the default browser path tries to download from `remotion.media`, use the local Chrome command. If local Chrome fails with `SIGTRAP` or `setsockopt: Operation not permitted`, rerun with browser launch permission. If Studio fails with `uv_interface_addresses returned Unknown system error 1`, treat it as unrelated to the render smoke path.

## Explicit Exclusions

This phase must not:

- Render the full final MP4.
- Call ffmpeg directly.
- Add Python commands that invoke Remotion rendering.
- Change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, or `prepare-remotion-assets` behavior unless a clear bug is discovered.
- Generate AI video.
- Download B-roll.
- Add external asset management.
- Parse DOCX.
- Add GUI or web app behavior beyond existing Remotion CLI commands.
- Add `remotion.config.ts`.
- Change Remotion rendering source unless a clear render smoke bug is discovered.
- Commit generated video or image output.

## Revision Note

2026-05-11: Initial ExecPlan created after reading required repository docs, current Remotion docs and package scripts, Phase 7 preview strategy, and installed Remotion 4.0.459 CLI option files. The plan proposes a verified local Chrome smoke render using `--frames=0-149` and defers all script and documentation changes until the command is proven.

2026-05-11: Milestone 1 completed by verifying the manual local Chrome smoke render command. The command is valid and produced `remotion/out/smoke.mp4` when Chrome launch was permitted; no script or documentation workflow changes were added yet.

2026-05-11: Milestone 2 completed by adding the verified `render:smoke:local` script, documenting the smoke workflow, ignoring generated render/timeline/cache artifacts, and validating the script with the known sandbox caveat plus permitted Chrome launch.

2026-05-11: Milestone 3 completed by regenerating fresh data and assets, validating typecheck, local still rendering, local smoke rendering, pytest, generated artifact sizes, ignored artifact status, and final commit policy. No additional implementation changes were made during this milestone.
