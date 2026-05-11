# Stabilize Remotion preview and still validation

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can build and validate `timeline.json`, export `remotion/props.json`, prepare Remotion audio assets, and render basic data-driven Remotion scene components. The Remotion TypeScript project type-checks, and the Python test suite passes. The remaining preview problem is environmental: `npm run still` repeatedly fails because Remotion cannot download Chrome Headless Shell from `remotion.media`, and Studio startup has also been limited by the local environment's network interface behavior.

This phase creates a documented, reliable preview strategy for the existing Remotion project without building a final render pipeline. The expected outcome is a small set of documented commands, generated-artifact rules, and, only if verified, simple package scripts or a tiny Remotion config that let developers use an already installed Chrome or clearly understand when network access is required. This phase must not assemble a final MP4, call ffmpeg directly, add Python commands that invoke Remotion, generate AI video, download B-roll, parse DOCX, add GUI or web app behavior, or change existing Python CLI behavior.

## Progress

- [x] (2026-05-11T00:00:00Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, `docs/plans/export-remotion-props.md`, `docs/plans/remotion-project-skeleton.md`, `docs/plans/remotion-audio-assets.md`, and `docs/plans/remotion-basic-visual-components.md`.
- [x] (2026-05-11T00:00:00Z) Inspected `remotion/package.json`, `remotion/src/Root.tsx`, `remotion/src/Video.tsx`, `remotion/props.json`, `.gitignore`, and the current npm scripts.
- [x] (2026-05-11T00:00:00Z) Researched installed Remotion CLI/config options locally in `node_modules`, checked local Chrome availability, and verified Remotion option names with Context7 documentation.
- [x] (2026-05-11T00:00:00Z) Created this ExecPlan for the Remotion preview environment strategy.
- [x] (2026-05-11T00:00:00Z) Implemented Milestone 1: added concise command-oriented Remotion preview documentation in `remotion/README.md`.
- [x] (2026-05-11T00:00:00Z) Implemented Milestone 2: verified local Chrome still-frame rendering, added `still:local`, and documented the result.
- [x] (2026-05-11T00:00:00Z) Implemented Milestone 3: tested Studio diagnostic startup flags and documented the persistent environment failure.
- [x] (2026-05-11T00:00:00Z) Completed Milestone 4: regenerated fresh data and assets, ran final Remotion/Python validation, inspected generated artifacts, and recorded commit policy.

## Surprises & Discoveries

- Observation: The current Remotion package versions are `remotion` 4.0.459 and `@remotion/cli` 4.0.459.
  Evidence: Local Node package inspection from `remotion/` reported version `4.0.459` for both packages.
- Observation: Current npm scripts are minimal and do not yet distinguish default browser-download rendering from local-browser rendering.
  Evidence: `remotion/package.json` defines `studio` as `remotion studio src/index.ts`, `typecheck` as `tsc --noEmit`, and `still` as `remotion still src/index.ts SyncCutVideo out/preview.png --frame=0`.
- Observation: A local Chrome executable is available in this environment.
  Evidence: `command -v google-chrome google-chrome-stable` found `/usr/bin/google-chrome` and `/usr/bin/google-chrome-stable`; `/usr/bin/google-chrome --version` printed `Google Chrome 127.0.6533.88`.
- Observation: The installed Remotion CLI supports a `--browser-executable` flag for still/render browser selection.
  Evidence: `node_modules/@remotion/renderer/dist/options/browser-executable.js` defines CLI flag `browser-executable` and describes it as a custom Chrome or Chromium executable path that prevents downloading another browser when a suitable local browser is provided.
- Observation: The installed Remotion CLI supports a `--chrome-mode` flag with local valid values `headless-shell` and `chrome-for-testing`.
  Evidence: `node_modules/@remotion/renderer/dist/options/chrome-mode.js` defines CLI flag `chrome-mode` and `validChromeModeOptions = ["headless-shell", "chrome-for-testing"]`.
- Observation: Remotion config files are supported as `remotion.config.ts` or `remotion.config.js`.
  Evidence: `node_modules/@remotion/cli/dist/get-config-file-name.js` checks for `remotion.config.ts` and then `remotion.config.js` at the Remotion root, or a CLI `--config` override.
- Observation: Remotion config can set browser executable and Chrome mode.
  Evidence: `node_modules/@remotion/cli/dist/config/index.d.ts` and `index.js` expose `Config.setBrowserExecutable()` and `Config.setChromeMode()`. Context7 Remotion documentation also confirms `Config.setBrowserExecutable('/usr/bin/google-chrome-stable')` and `Config.setChromeMode('chrome-for-testing')`.
- Observation: Context7 documentation appears broader than the installed local type definitions for `setChromeMode`.
  Evidence: Context7 returned a signature mentioning values such as `system` and `chromium`, while the installed Remotion 4.0.459 option file accepts only `headless-shell` and `chrome-for-testing`. Implementation must follow the installed package.
- Observation: Studio has CLI/config options that may help normal browser opening but may not solve the observed startup failure.
  Evidence: The installed options include Studio `--browser`, `--no-open`, and `--ipv4`. However, `node_modules/@remotion/renderer/dist/port-config.js` calls `os.networkInterfaces()` before deciding the host, and the prior Studio failure was `uv_interface_addresses returned Unknown system error 1` from Node's `os.networkInterfaces()`.
- Observation: Asking Remotion for CLI help can itself trigger environment failures.
  Evidence: `npm exec -- remotion still --help` attempted to download Chrome Headless Shell and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`. `npm exec -- remotion studio --help` reached Studio startup and failed with `uv_interface_addresses returned Unknown system error 1`.
- Observation: The local Chrome still command avoids the `remotion.media` Chrome Headless Shell download path.
  Evidence: Running `npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing` did not print any Chrome Headless Shell download message and, when Chrome was allowed to launch, rendered `out/preview.png`.
- Observation: The sandboxed local Chrome attempt failed because the environment blocked browser launch.
  Evidence: The first command attempt exited non-zero with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and Chrome stderr `[46:46:0511/150843.137526:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`.
- Observation: Rerunning the same command with permission to launch Chrome outside the sandbox succeeded.
  Evidence: The rerun completed with `Composition SyncCutVideo`, `Format png`, `Output out/preview.png`, `Rendered 1/1`, and `+ out/preview.png`. `ls -lh out/preview.png` reported a 129K PNG.
- Observation: The Studio diagnostic flags do not avoid the local network-interface failure in this environment.
  Evidence: Running `npm run studio -- --no-open --ipv4` exited non-zero before printing a Studio URL with `SystemError [ERR_SYSTEM_ERROR]: A system error occurred: uv_interface_addresses returned Unknown system error 1 (Unknown system error 1)`, originating from `Object.networkInterfaces (node:os:223:16)`, `@remotion/renderer/dist/port-config.js:14:44`, `start-server.js:21:51`, and `start-studio.js:65:57`.
- Observation: Final validation reproduced the expected default still failure and verified the local still path.
  Evidence: `npm run still` attempted `https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`. `npm run still:local` first failed in the sandbox with `SIGTRAP` and `setsockopt: Operation not permitted`, then succeeded when Chrome launch was permitted, rendering `out/preview.png`.
- Observation: Final Studio validation still cannot host Studio in this environment.
  Evidence: `npm run studio -- --no-open --ipv4` failed again with `uv_interface_addresses returned Unknown system error 1` from Node `os.networkInterfaces()` through Remotion `port-config.js`.

## Decision Log

- Decision: Prefer a docs-first strategy and add scripts only after they are verified against the installed Remotion CLI.
  Rationale: The current problem is environmental, not application logic. Documentation can make the workflow explicit without adding brittle machine-specific behavior. Scripts are useful only if they improve repeatability in this repository.
  Date/Author: 2026-05-11 / Codex
- Decision: Treat `/usr/bin/google-chrome` as an environment-specific discovery, not a portable default to blindly bake into project config.
  Rationale: The path exists on this Linux machine but may not exist on other developer machines or CI. A committed config that always points to it could break otherwise valid environments.
  Date/Author: 2026-05-11 / Codex
- Decision: Do not add a final MP4 render script in this phase.
  Rationale: The user explicitly excluded final MP4 assembly. The still-frame and Studio workflows are enough to validate preview rendering without expanding the pipeline.
  Date/Author: 2026-05-11 / Codex
- Decision: Do not route Remotion rendering through Python.
  Rationale: The user explicitly excluded Python commands that invoke Remotion rendering. The Python CLI remains responsible for timeline, props, and asset preparation only.
  Date/Author: 2026-05-11 / Codex
- Decision: Put Milestone 1 documentation in `remotion/README.md`.
  Rationale: The guidance is specific to the standalone Remotion package, its npm scripts, and local preview artifacts. Keeping it in the Remotion directory makes it easy to find while working from `remotion/`.
  Date/Author: 2026-05-11 / Codex
- Decision: Add a `still:local` package script after verifying the exact local Chrome command.
  Rationale: The command succeeds when Chrome launch is permitted, avoids the blocked `remotion.media` download, and is useful enough to expose as a repeatable Remotion package script. It remains separate from the portable default `still` script and does not render a final video.
  Date/Author: 2026-05-11 / Codex
- Decision: Do not add a `studio:local` package script for Milestone 3.
  Rationale: The tested diagnostic command did not start Studio or print a local URL. Adding a script would imply reliability that this environment does not currently have.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

This plan has been created after local repository inspection and Remotion option research. No source code, package file, generated artifact, or Python CLI behavior has been changed yet.

Milestone 1 is complete. `remotion/README.md` now documents the purpose of the Remotion project, the repository-root data regeneration workflow, `npm run typecheck`, default still rendering, local Chrome still rendering with `--browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing`, Studio startup and the `--no-open --ipv4` diagnostic variant, the known `uv_interface_addresses returned Unknown system error 1` limitation, generated artifact policy, and the fact that this phase does not assemble a final MP4. No Python source files, Remotion rendering source files, package scripts, Remotion config, ffmpeg behavior, Python Remotion wrapper, AI video generation, or B-roll downloading were added.

Milestone 2 is complete. The local Chrome still-frame path was tested from `remotion/` with `npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing`. The first sandboxed attempt failed with `SIGTRAP` and `setsockopt: Operation not permitted`, showing that the environment blocked Chrome launch. The same command succeeded when Chrome launch was permitted, did not download from `remotion.media`, and generated `remotion/out/preview.png` at 129K. `remotion/package.json` now has a `still:local` script with the verified command, and `remotion/README.md` documents `npm run still:local` plus the browser-launch limitation. No lockfile change was needed because only npm scripts changed. No Python source files, Remotion rendering source files, Remotion config, ffmpeg behavior, final MP4 rendering, Python Remotion wrapper, AI video generation, or B-roll downloading were added.

Milestone 3 is complete. The Studio diagnostic command `npm run studio -- --no-open --ipv4` was tested from `remotion/` and failed before serving a URL with the known network-interface error: `uv_interface_addresses returned Unknown system error 1`. Because the command did not start reliably, no `studio:local` script was added. `remotion/README.md` now states that this environment still cannot host Studio reliably with the diagnostic flags. No Python source files, Remotion rendering source files, Remotion config, ffmpeg behavior, final MP4 rendering, Python Remotion wrapper, AI video generation, B-roll downloading, or GUI/web app behavior beyond the existing Remotion Studio command were added.

Milestone 4 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Final Remotion validation matched expectations. From `remotion/`, `npm run typecheck` passed. `npm run still` failed with the known browser download DNS error: it attempted to download Chrome Headless Shell from `remotion.media` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`. `npm run still:local` used `/usr/bin/google-chrome` and avoided the `remotion.media` download path; the sandboxed attempt failed with `SIGTRAP` and `setsockopt: Operation not permitted`, and the permitted rerun succeeded with `Composition SyncCutVideo`, `Format png`, `Output out/preview.png`, and `Rendered 1/1`. `npm run studio -- --no-open --ipv4` failed with the known `uv_interface_addresses returned Unknown system error 1` network-interface error before serving a URL.

Final Python validation passed. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and all 114 passed. Generated artifacts observed were `remotion/out/preview.png` at 129K, `timeline.json`, and the copied audio files under `remotion/public/audio/`: `01_HOOK.mp3`, `02_INTRO.mp3`, `03_MECHANISM_1.mp3`, `04_MECHANISM_2.mp3`, `05_MECHANISM_3.mp3`, `06_MECHANISM_4.mp3`, and `07_CONCLUSION.mp3`.

Commit policy for this phase: commit `remotion/README.md`, commit `remotion/package.json` with the `still:local` script, and commit `docs/plans/remotion-preview-environment.md`. Do not commit `timeline.json`, `remotion/out/preview.png`, `remotion/public/audio/*.mp3`, `synccut/__pycache__/`, or `tests/__pycache__/`. `git status --short` showed `M remotion/package.json`, untracked `docs/plans/remotion-preview-environment.md`, untracked `remotion/README.md`, untracked `remotion/out/`, untracked `synccut/__pycache__/`, untracked `tests/__pycache__/`, and untracked `timeline.json`; `remotion/public/audio` remains ignored by the current `.gitignore`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The existing Python workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

The Remotion project consumes `remotion/props.json` through `remotion/src/props.ts`. `remotion/src/Root.tsx` registers one composition from `defaultProps.composition`. `remotion/src/Video.tsx` renders section audio and maps each scene to a Remotion `Sequence` using exported frame timing. Scene components render placeholders or basic data-driven visuals from `scene.visual.data`.

The relevant Remotion files are:

    remotion/package.json
    remotion/package-lock.json
    remotion/src/index.ts
    remotion/src/Root.tsx
    remotion/src/Video.tsx
    remotion/src/props.ts
    remotion/src/types.ts
    remotion/src/components/
    remotion/props.json

The relevant generated artifacts are:

    timeline.json
    remotion/props.json
    remotion/public/audio/*.mp3
    remotion/out/preview.png

## Current Preview and Still Scripts

`remotion/package.json` currently defines:

    "studio": "remotion studio src/index.ts"
    "typecheck": "tsc --noEmit"
    "still": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0"

`npm run typecheck` is the reliable non-browser validation command. `npm run still` is the intended one-frame render smoke test, but in this environment it fails before producing `remotion/out/preview.png` because Remotion tries to download Chrome Headless Shell and DNS lookup for `remotion.media` fails.

## Known Environment Failures

The known still-frame failure is:

    Downloading Chrome Headless Shell https://www.remotion.dev/chrome-headless-shell
    Downloading from: https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear
    Error: getaddrinfo EAI_AGAIN remotion.media
    code: 'EAI_AGAIN'
    syscall: 'getaddrinfo'
    hostname: 'remotion.media'

This indicates a browser acquisition problem, not a props, TypeScript, React, audio, or visual component problem.

The known Studio startup limitation is:

    SystemError [ERR_SYSTEM_ERROR]: A system error occurred: uv_interface_addresses returned Unknown system error 1
    at Object.networkInterfaces (node:os:223:16)

This indicates a Node or sandbox network-interface issue while Remotion starts the preview server. It is separate from the Chrome Headless Shell download failure. Studio flags such as `--ipv4` and `--no-open` can be tested, but they may not solve the failure because Remotion still calls `os.networkInterfaces()`.

## Current Remotion Version and Options

The installed Remotion version is 4.0.459 for both `remotion` and `@remotion/cli`.

The installed CLI/config options relevant to this phase are:

- `--browser-executable=<absolute-path>`: custom Chrome or Chromium executable for still/render browser selection.
- `--chrome-mode=headless-shell|chrome-for-testing`: browser mode selection. The installed local version accepts only these two values.
- `--browser=<path-or-name>`: Studio browser tab opening selection, not the same as render browser selection.
- `--no-open`: prevent Studio from opening a browser window.
- `--ipv4`: force Remotion Studio to bind to an IPv4 interface.
- `remotion.config.ts` or `remotion.config.js`: project config files loaded from the Remotion root.
- `Config.setBrowserExecutable(path)`: config equivalent for browser executable.
- `Config.setChromeMode(mode)`: config equivalent for Chrome mode.
- `Config.setShouldOpenBrowser(false)`: config equivalent for avoiding Studio browser auto-open.
- `Config.setIPv4(true)`: config equivalent for IPv4 binding preference.

Implementation must prefer installed local package behavior over memory or broader docs if they disagree.

## Local Chrome Availability

This environment has:

    /usr/bin/google-chrome
    /usr/bin/google-chrome-stable
    Google Chrome 127.0.6533.88

This makes a local-browser still-frame workflow plausible:

    cd remotion
    npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing

This command must be verified in a milestone before adding a package script. If it succeeds, the script can be added. If it fails due sandbox, Chrome sandboxing, missing system libraries, or another environment issue, record the exact error and keep the documentation honest instead of adding unrelated workarounds.

## Recommended Preview Workflow

The preview workflow should stay explicit:

1. Regenerate timeline and props from the repository root.
2. Prepare audio assets into `remotion/public/audio/`.
3. Run `npm run typecheck` from `remotion/`.
4. Try Studio only when the environment supports a local preview server.

The baseline commands are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    cd remotion
    npm run typecheck
    npm run studio

If Studio fails with `uv_interface_addresses returned Unknown system error 1`, record that the environment cannot currently host Studio. Do not treat that as a rendering component failure.

A documented Studio diagnostic command can be:

    npm run studio -- --no-open --ipv4

Add a `studio:local` script only if this command is verified to start Studio reliably in the target environment. Do not add a script that pretends to fix the known network-interface failure without evidence.

## Recommended Still-Frame Workflow

The still-frame workflow should have two levels:

The default command remains:

    cd remotion
    npm run still

This is portable but may download Chrome Headless Shell if Remotion does not find a usable browser.

For environments with local Chrome, use:

    cd remotion
    npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing

If verified, add a package script such as:

    "still:local": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing"

Only add this script if `/usr/bin/google-chrome` is present and the command succeeds or fails for a clearly documented non-download environment reason. If the command still tries to download from `remotion.media`, the flag usage is wrong and must be corrected before adding a script.

Do not add any script that renders a final video file.

## Remotion Config Strategy

Do not add a committed `remotion.config.ts` just to hard-code `/usr/bin/google-chrome`.

A config file is appropriate only if it stays portable, for example by reading an environment variable:

    import {Config} from "@remotion/cli/config";

    const browserExecutable = process.env.REMOTION_BROWSER_EXECUTABLE;
    if (browserExecutable) {
      Config.setBrowserExecutable(browserExecutable);
      Config.setChromeMode("chrome-for-testing");
    }

This approach avoids a Linux-only path in committed config. However, adding config is optional and should be done only if it materially improves the workflow after the direct CLI flag is tested.

If no config file is added, document the CLI flag workflow instead.

## Regenerating Props and Audio Before Preview

Preview should always use current generated data:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

This keeps `remotion/props.json` aligned with the current Python exporter and ensures `section.audio.public_path` exists for Remotion audio playback.

Do not add a Python command that wraps these Remotion preview steps.

## Validation Commands

Use these commands after any implementation in this phase:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

For environment validation, use:

    cd remotion
    npm run still
    npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing
    npm run studio -- --no-open --ipv4

Record exact errors for still or Studio failures. Do not add unrelated workarounds for Chrome download, network-interface, sandbox, or system-library errors.

## Generated Artifacts Policy

`timeline.json` is generated by `build-timeline` and should not be committed unless explicitly requested.

`remotion/props.json` is sample data consumed by the Remotion project. It can be committed when intentionally updated, especially when it demonstrates current props schema fields such as audio `public_path`.

`remotion/public/audio/*.mp3` is copied generated media and should not be committed. `.gitignore` currently ignores `remotion/public`, which covers these files.

`remotion/out/` and preview images such as `remotion/out/preview.png` are generated preview artifacts and should not be committed. If `.gitignore` does not exclude `remotion/out/`, add that ignore rule during implementation.

`remotion/node_modules/` is dependency output and should remain excluded. The current `.gitignore` excludes `remotion/node_modules`.

Python `__pycache__/` directories should not be committed. If current ignore rules do not exclude them, add an appropriate ignore rule during implementation.

## Milestones

### Milestone 1: Document the preview environment workflow

Create or update lightweight documentation for Remotion preview validation. The document should explain the normal data regeneration workflow, `npm run typecheck`, default `npm run still`, local Chrome still validation, Studio limitations, and generated-artifact policy. A good target is either a short `remotion/README.md` or a focused docs file linked from this plan. Keep it concise and command-oriented.

Validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

### Milestone 2: Verify local Chrome still-frame rendering path

From `remotion/`, test:

    npm run still -- --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing

If it succeeds, record the generated `remotion/out/preview.png` artifact and add a simple `still:local` script using the verified flags. If it fails, record the exact error in this plan and do not add a misleading script. If the failure is due a known environment limitation, leave the docs with the manual command and expected limitation.

Validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

### Milestone 3: Evaluate Studio startup flags without changing app rendering

From `remotion/`, test:

    npm run studio -- --no-open --ipv4

If Studio starts reliably, document the URL and optionally add `studio:local` with the verified flags. If it fails with the existing `uv_interface_addresses` error, record the exact limitation and do not add workaround code. Do not add a GUI or web app; Remotion Studio is the existing development preview tool.

Validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

### Milestone 4: Final validation and artifact review

Regenerate fresh data and assets:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Then run:

    cd remotion
    npm run typecheck
    npm run still
    cd ..
    .venv/bin/python -m pytest

If local still or Studio validation is supported, run the verified commands too. Record all results in this plan, including whether `remotion/out/preview.png` was generated and which artifacts should be excluded from commit.

## Explicit Exclusions

This phase must not:

- Assemble a final MP4.
- Call ffmpeg directly.
- Add Python commands that invoke Remotion rendering.
- Change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, or `prepare-remotion-assets` behavior unless a clear bug is discovered.
- Generate AI video.
- Download B-roll.
- Add external asset management.
- Parse DOCX.
- Add GUI or web app behavior.
- Add real chart/table feature work beyond the existing basic visual components.
- Add audio decoding, transcoding, trimming, normalization, or probing.
- Commit binary preview output or copied audio assets unless explicitly requested.

## Revision Note

2026-05-11: Initial ExecPlan created after reading the required project documents, inspecting the current Remotion project and generated props, checking local Chrome availability, inspecting installed Remotion 4.0.459 CLI/config option files, and verifying relevant Remotion option names with Context7.

2026-05-11: Milestone 1 completed by adding `remotion/README.md` with preview, still, Studio, data regeneration, and artifact policy commands. No scripts or config were added.

2026-05-11: Milestone 2 completed by verifying the local Chrome still command, adding `npm run still:local`, documenting the sandbox browser-launch failure and successful local render, and noting generated `remotion/out/preview.png` as a non-commit artifact.

2026-05-11: Milestone 3 completed by testing `npm run studio -- --no-open --ipv4`, documenting the persistent `uv_interface_addresses` environment failure, and deciding not to add a `studio:local` script.

2026-05-11: Milestone 4 completed by regenerating fresh data and assets, validating typecheck, default still, local Chrome still, Studio diagnostics, pytest, generated artifacts, and commit policy. No source code changes were made during this milestone.
