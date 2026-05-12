# Prepare release packaging and user-facing documentation

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this release documentation phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut now has an end-to-end MVP pipeline: it builds a timed `timeline.json`, validates and inspects that timeline, exports Remotion props, prepares audio and local visual assets, reports visual readiness, runs preflight checks, and documents local Remotion still, smoke, segment, and final render workflows. The repository still needs a clear root entrypoint for a new developer or user who has not followed the phase-by-phase implementation history.

After this phase, a new user should be able to open `README.md`, understand what SyncCut does and does not do, install the Python CLI in editable mode, install Remotion dependencies, run the example workflow from `examples/`, validate readiness, and choose a Remotion preview or render command. The work is documentation and packaging review only unless a clear packaging or docs bug is discovered. It must not add product features, change command behavior, change schemas, invoke Remotion from Python, parse DOCX, generate AI video, download B-roll, add GUI or web app behavior, or commit generated artifacts.

## Progress

- [x] (2026-05-12T15:27:49+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `pyproject.toml`, `README.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, all requested prior ExecPlans through `docs/plans/remotion-final-render.md`, `remotion/README.md`, `remotion/package.json`, and `.gitignore`.
- [x] (2026-05-12T15:27:49+07:00) Inspected `synccut/cli.py`, public helper modules under `synccut/`, `tests/test_cli.py`, `examples/`, and `remotion/props.json`.
- [x] (2026-05-12T15:27:49+07:00) Checked the installed CLI help for `synccut`, `synccut build-timeline`, and `synccut preflight` to confirm public command names and option spelling.
- [x] (2026-05-12T15:27:49+07:00) Created this ExecPlan for release packaging and user-facing documentation.
- [x] (2026-05-12T15:37:23+07:00) Implemented Milestone 1: wrote the root README as the main user-facing entrypoint and linked to Remotion-specific docs.
- [x] (2026-05-12T15:37:23+07:00) Ran Milestone 1 validation: Python tests, Remotion typecheck, and CLI help checks all passed.
- [x] (2026-05-12T15:43:38+07:00) Completed Milestone 2: intentionally deferred `docs/commands.md` because the README stayed readable and CLI help is authoritative for exact options.
- [x] (2026-05-12T15:48:01+07:00) Implemented Milestone 3: added `docs/release-checklist-v0.1.md` with packaging, validation, artifact, git review, forbidden behavior, and suggested commit checks.
- [x] (2026-05-12T15:54:42+07:00) Completed Milestone 4: reviewed packaging metadata, ran Python tests, Remotion typecheck, CLI help checks, example workflow through verified preflight, and final artifact review.

## Surprises & Discoveries

- Observation: The root `README.md` exists but is empty.
  Evidence: Reading `README.md` returned no content, while `pyproject.toml` already points `project.readme` at `README.md`.
- Observation: Packaging metadata already declares an editable-installable Python package and console script.
  Evidence: `pyproject.toml` contains project name `synccut`, version `0.1.0`, `requires-python = ">=3.11"`, dependency `typer>=0.12`, optional dev dependency `pytest>=8`, and script `synccut = "synccut.cli:app"`.
- Observation: The current CLI exposes eight user-facing commands.
  Evidence: `.venv/bin/synccut --help` listed `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, and `preflight`.
- Observation: The current Remotion package exposes five validation or render workflows.
  Evidence: `remotion/package.json` defines `typecheck`, `still`, `still:local`, `render:smoke:local`, `render:segment:local`, and `render:final:local`, plus `studio`.
- Observation: Generated artifacts are already broadly ignored.
  Evidence: `.gitignore` contains `examples`, `assets/visuals/`, `.venv`, `remotion/node_modules`, `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`.
- Observation: The requested matching documentation link is valid in the current repository.
  Evidence: `docs/matching.md` exists, so the root README links to both `docs/schemas.md` and `docs/matching.md`.
- Observation: The root README stayed readable with short command summaries rather than full option documentation.
  Evidence: Milestone 1 added a concise command summary and points users to `.venv/bin/synccut --help` or `.venv/bin/synccut <command> --help` for exact options. A separate `docs/commands.md` remains optional for Milestone 2 rather than required to keep the README usable.
- Observation: Milestone 2 did not reveal a readability problem that would justify adding another documentation file now.
  Evidence: Reviewing `README.md` showed one short command-summary section, a single quick-start workflow, and explicit pointers to CLI help for exact options. The README does not contain per-command transcripts or long option tables.
- Observation: Milestone 3 did not require README or packaging edits.
  Evidence: The release checklist could reference the current README workflow, `pyproject.toml` metadata, and existing npm scripts without finding a broken link, contradiction, or packaging bug.
- Observation: Packaging metadata already matches the v0.1 checklist.
  Evidence: `pyproject.toml` declares project name `synccut`, version `0.1.0`, `requires-python = ">=3.11"`, dependency `typer>=0.12`, dev extra `pytest>=8`, and console script `synccut = "synccut.cli:app"`.
- Observation: The documented example workflow still reaches the expected warning-only render readiness state.
  Evidence: Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: Generated artifacts remain excluded from commit candidates.
  Evidence: `git status --short --ignored` showed only `README.md`, `docs/plans/release-packaging-and-docs.md`, and `docs/release-checklist-v0.1.md` as non-ignored changes. It showed `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, test `__pycache__/`, and `timeline.json` as ignored.

## Decision Log

- Decision: Make `README.md` the primary user-facing entrypoint.
  Rationale: `pyproject.toml` already uses `README.md` as package readme metadata, and the file is currently empty. A complete root README gives both package users and repository visitors one obvious starting point.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep Remotion render details in `remotion/README.md` and summarize them from the root README.
  Rationale: The Remotion project is a standalone npm package under `remotion/`. The root README should explain how it fits into the SyncCut workflow, while the detailed browser, sandbox, and render-script notes already live where Remotion developers work.
  Date/Author: 2026-05-12 / Codex
- Decision: Plan a separate `docs/commands.md` command reference only if the root README becomes too dense.
  Rationale: A concise README is more useful for first-time users. A separate command reference is justified when examples, expected outputs, and options would otherwise make the README hard to scan.
  Date/Author: 2026-05-12 / Codex
- Decision: Add `docs/release-checklist-v0.1.md` as a release readiness artifact.
  Rationale: The project now has Python, Remotion, generated assets, and ignored render outputs. A checklist makes the v0.1 release process repeatable without changing command behavior.
  Date/Author: 2026-05-12 / Codex
- Decision: Do not change `pyproject.toml` unless validation proves a packaging bug.
  Rationale: The existing metadata already matches the current package name, version, Python requirement, dependencies, dev dependency, package discovery, and console entry point. Unnecessary metadata churn would expand the scope of a docs-focused phase.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep Milestone 1 command descriptions in the README to one line per command and defer full examples to CLI help or a possible `docs/commands.md`.
  Rationale: The README's job is to orient new users quickly. Full command transcripts for every command would make it less scannable and duplicate the Typer-generated help.
  Date/Author: 2026-05-12 / Codex
- Decision: Do not create `docs/commands.md` in Milestone 2.
  Rationale: The root README stayed readable with short command summaries, and Typer-generated CLI help is the authoritative source for current command options. A separate command reference can be added later if command examples, options, or troubleshooting notes grow beyond what the README can carry cleanly.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep the v0.1 checklist procedural rather than explanatory.
  Rationale: `README.md` already explains the workflow. The checklist should be fast for maintainers to execute before release, so it uses commands and checkboxes instead of repeating detailed background.
  Date/Author: 2026-05-12 / Codex
- Decision: Leave `pyproject.toml` unchanged.
  Rationale: The packaging metadata review found no mismatch with the release checklist or current command behavior. Changing metadata would add unnecessary scope to a docs and release-readiness phase.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documentation, prior plans, packaging metadata, Remotion documentation, CLI source, tests, examples, generated props, and current command help. No root README, command reference, release checklist, packaging metadata, Python source, Remotion source, command behavior, schema, generated artifact, or render output has been changed yet for this phase.

Milestone 1 is complete. `README.md` now serves as the root user-facing entrypoint. It explains that SyncCut is a Python CLI plus Remotion project, lists what the MVP does, lists explicit exclusions, documents prerequisites and setup, provides the example quick-start workflow, links to `docs/schemas.md` and `docs/matching.md`, summarizes all eight Python commands, links to `remotion/README.md`, summarizes Remotion validation and render scripts, explains local visual asset preparation and placeholder fallback behavior, documents props-only and verified preflight, records common Chrome/browser environment issues, states generated artifact policy, and gives development validation commands.

The README stayed concise enough that Milestone 2 can decide whether `docs/commands.md` adds enough value for detailed command examples. It is not strictly required just to keep the README readable. No Python source, Remotion source, schemas, `pyproject.toml`, command behavior, render output, or generated artifacts were changed during Milestone 1.

Milestone 1 validation passed. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. The CLI help checks `.venv/bin/synccut --help`, `.venv/bin/synccut build-timeline --help`, and `.venv/bin/synccut preflight --help` all exited successfully and showed the command names and options documented in the README.

Milestone 2 is complete. No `docs/commands.md` file was created. The current command reference strategy is to keep the root README's one-line command summary, direct users to `.venv/bin/synccut --help` and `.venv/bin/synccut <command> --help` for exact options, and reserve `docs/commands.md` for a later phase if command examples, option details, expected outputs, or troubleshooting notes become too large for the README. No README, source, schema, packaging, Remotion, command behavior, or generated artifact changes were made during Milestone 2.

Milestone 3 is complete. `docs/release-checklist-v0.1.md` now provides a practical maintainer checklist for v0.1 release readiness. It covers MVP scope, explicit exclusions, packaging metadata, editable install, Python tests and CLI help, example workflow validation, expected current sample warnings, Remotion typecheck and optional render checks, generated artifact cleanup, git review commands, forbidden behavior checks, and the suggested documentation commit message `Add release documentation for SyncCut MVP`. No README, `pyproject.toml`, Python source, Remotion source, schema, command behavior, render output, or generated artifact changes were made during Milestone 3.

Milestone 4 is complete. Packaging metadata review found no required changes: `pyproject.toml` uses project name `synccut`, version `0.1.0`, `requires-python = ">=3.11"`, runtime dependency `typer>=0.12`, dev extra `pytest>=8`, and console script `synccut = "synccut.cli:app"`.

Validation passed. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. CLI help checks passed: `.venv/bin/synccut --help` listed the expected eight commands, `.venv/bin/synccut build-timeline --help` showed required `SCENES_JSON`, `--audio-dir`, `--alignment-dir`, and `--out`, and `.venv/bin/synccut preflight --help` showed `PROPS_JSON`, `--json`, `--verify-files`, and `--public-dir`.

The optional example workflow through verified preflight was run without rendering. `build-timeline` completed successfully and wrote `timeline.json`. `validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `inspect timeline.json` printed a 33-scene, 7-section overview. `export-remotion` reported `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The warnings were the known root props warning plus 17 optional visual placeholder warnings; `Errors:` printed `none`.

Final artifact review passed. `git status --short --ignored` showed commit candidates `README.md`, `docs/plans/release-packaging-and-docs.md`, and `docs/release-checklist-v0.1.md`. Generated or local-only artifacts were ignored: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `synccut/__pycache__/`, `tests/__pycache__/`, and `timeline.json`. `remotion/props.json` was not shown as a commit candidate after validation regeneration. No Python source, Remotion source, schema, command behavior, render output, or packaging metadata changes were made during Milestone 4.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python CLI package plus a standalone Remotion project. The Python package lives under `synccut/`. The Remotion project lives under `remotion/`. Example input files live under `examples/`, but that directory is currently ignored by git, so release documentation must clearly distinguish sample local fixtures from committed package files.

The root package metadata is in `pyproject.toml`. It declares `synccut` version `0.1.0`, requires Python 3.11 or newer, depends on Typer, exposes the console script `synccut`, and has an optional `dev` extra for pytest. The packaging backend is setuptools. A new developer should be able to create a virtual environment and install the package with:

    python3 -m venv .venv
    .venv/bin/python -m pip install -e '.[dev]'

The current Python command surface is implemented in `synccut/cli.py`. The CLI is deliberately thin: commands load files, call reusable helper modules, write JSON when required, and format expected `SyncCutError` failures without tracebacks. The current commands are:

    synccut build-timeline SCENES_JSON --audio-dir AUDIO_DIR --alignment-dir ALIGNMENT_DIR --out timeline.json
    synccut validate-timeline timeline.json
    synccut inspect timeline.json
    synccut export-remotion timeline.json --out remotion/props.json
    synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    synccut inspect-visual-assets remotion/props.json
    synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The reusable Python modules behind those commands are:

- `synccut/scenes_loader.py`, which reads and validates `scenes.json`.
- `synccut/alignment_loader.py`, which discovers section audio and alignment JSON files.
- `synccut/timeline_builder.py`, which matches dialogue to alignment timing and builds `timeline.json`.
- `synccut/timeline_validator.py`, which validates `timeline.json`.
- `synccut/timeline_inspector.py`, which prints a readable timeline overview.
- `synccut/remotion_exporter.py`, which exports Remotion-friendly props.
- `synccut/remotion_assets.py`, which copies section audio into Remotion `public/audio/` and annotates props.
- `synccut/visual_assets.py`, which prepares local AI/B-roll visual assets and reports visual readiness.
- `synccut/preflight.py`, which reports props-only and optional public-file render readiness.

The Remotion project under `remotion/` consumes `remotion/props.json` from `remotion/src/props.ts`. `remotion/src/Root.tsx` registers the `SyncCutVideo` composition using width, height, fps, and duration from the props file. `remotion/src/Video.tsx` maps scenes to Remotion `Sequence` components using exported frame timing and mounts section audio from prepared public paths. Data-driven Remotion components render `COMPARISON_CARD`, `TABLE`, `CHART`, `TIMELINE`, and `SHARE_BREAKDOWN`; `AI_VIDEO` and `B_ROLL` can render optional local public visual assets and otherwise fall back to placeholders.

The Remotion npm scripts in `remotion/package.json` are:

    npm run typecheck
    npm run still
    npm run still:local
    npm run render:smoke:local
    npm run render:segment:local
    npm run render:final:local
    npm run studio

The local render scripts use `/usr/bin/google-chrome` and `--chrome-mode=chrome-for-testing` because the default Remotion browser download path can fail in this environment with DNS errors for `remotion.media`. Studio can fail in this environment with `uv_interface_addresses returned Unknown system error 1`. These are environment limitations, not SyncCut Python pipeline failures.

Generated artifacts include `timeline.json`, copied files under `remotion/public/`, render outputs under `remotion/out/`, synthetic local files under `assets/visuals/`, Python caches, and Remotion `node_modules/`. These should not be committed. `remotion/props.json` is sample input for the Remotion project and may be committed only when intentionally refreshed as sample data, not merely because validation regenerated it.

## Current End-to-End MVP Capability

The MVP starts from three kinds of prepared local input:

1. A `scenes.json` file with scene order, section information, dialogue text, and visual metadata.
2. Section narration audio files such as `01_HOOK.mp3`.
3. Section alignment JSON files with paragraph, sentence, and word timestamps.

The Python CLI builds `timeline.json` by matching each scene's dialogue to section-local alignment timestamps, then converting those section-local times into global timeline times. It validates the timeline, prints a readable overview, exports Remotion props, prepares audio public assets, optionally prepares local visual public assets for `AI_VIDEO` and `B_ROLL`, reports readiness, and performs a render preflight without invoking Remotion.

The Remotion project then type-checks and can render stills, short smoke clips, longer segments, or the full composition using npm scripts. Remotion rendering is intentionally driven from npm, not from Python.

The MVP does not parse DOCX, invent alignment timing, decode or transcode audio, call ffmpeg directly, generate AI video, download B-roll, scrape or fetch external media, provide a GUI/web app, or automatically assemble a final video from Python.

## Root README Structure

Milestone 1 should replace the currently empty `README.md` with a concise but complete user-facing entrypoint. It should use plain Markdown and include these sections:

- Project overview: explain SyncCut in one paragraph as a Python CLI and Remotion project for turning prepared scene, audio, and alignment data into a renderable video timeline.
- MVP capabilities: list what currently works, including timeline build, validation, Remotion export, asset preparation, readiness reports, and local Remotion renders.
- Explicit exclusions: state that the MVP does not parse DOCX, call ffmpeg directly, generate AI video, download B-roll, fetch external media, or provide a GUI/web app.
- Prerequisites: Python 3.11 or newer, a virtual environment, Node/npm for `remotion/`, local Chrome at `/usr/bin/google-chrome` for local render scripts in this environment, and prepared input data.
- Setup: show virtual environment creation, editable install with dev dependencies, and Remotion `npm install`.
- Quick start with examples: show the exact end-to-end commands from root through Remotion typecheck and smoke render.
- Input file expectations: summarize `scenes.json`, audio file, and alignment JSON requirements, linking to `docs/schemas.md` and `docs/matching.md`.
- Command reference summary: list each Python CLI command with one-line purpose and a short example.
- Remotion workflow: link to `remotion/README.md` and summarize typecheck, still, smoke, segment, and final render commands.
- Visual asset workflow: explain `assets/visuals/<scene_id>.<ext>` local matching, `prepare-visual-assets`, `inspect-visual-assets`, and placeholder fallback behavior.
- Preflight and troubleshooting: show props-only and verified preflight, explain warning vs error at a high level, and mention common browser environment failures.
- Artifact policy: list generated files and directories that should not be committed.
- Development and testing: show `.venv/bin/python -m pytest` and `cd remotion && npm run typecheck`.
- Roadmap: link to `docs/future-phases.md` for future DOCX, media generation, and assembly ideas.

Keep Remotion-specific browser and render detail in `remotion/README.md` and link to it from the root README rather than duplicating every known environment note.

## Command Reference Document

Milestone 2 should decide whether to add `docs/commands.md`. Add it if the README command section becomes too long or if the command examples need more detail than the README can carry cleanly.

If created, `docs/commands.md` should be a stable command reference with one section per Python command. Each section should include purpose, inputs, outputs or side effects, a canonical command example, expected successful summary output where useful, and common expected errors. The commands to document are:

- `build-timeline`, which reads scenes, audio references, and alignment JSON and writes `timeline.json`.
- `validate-timeline`, which validates `timeline.json` and exits nonzero on errors.
- `inspect`, which prints a section-grouped timeline overview.
- `export-remotion`, which writes Remotion props JSON.
- `prepare-remotion-assets`, which copies section audio into `remotion/public/audio/` and updates props.
- `prepare-visual-assets`, which copies local AI/B-roll visual assets into `remotion/public/visuals/` and updates props.
- `inspect-visual-assets`, which read-only reports AI/B-roll readiness from props and supports `--json`.
- `preflight`, which read-only reports render readiness from props, supports `--json`, and optionally verifies public files with `--verify-files --public-dir`.

If `docs/commands.md` is created, the root README should link to it and keep only the short command summary.

## Release Checklist Document

Milestone 3 should add `docs/release-checklist-v0.1.md`. The checklist should be user-facing for maintainers and should not modify behavior. It should cover:

- Confirm packaging metadata: name `synccut`, version `0.1.0`, Python requirement `>=3.11`, Typer dependency, pytest dev dependency, and console entry point.
- Confirm local setup: virtual environment and editable install.
- Confirm Python validation: `.venv/bin/python -m pytest`.
- Confirm CLI help: `.venv/bin/synccut --help` and representative subcommand help.
- Confirm example workflow: build, validate, inspect, export, prepare audio assets, inspect visual assets, and verified preflight.
- Confirm Remotion validation: `cd remotion && npm install` when needed, then `npm run typecheck`.
- Confirm optional render checks: `npm run still:local`, `npm run render:smoke:local`, `npm run render:segment:local`, and `npm run render:final:local` only when local Chrome launch is permitted and runtime is acceptable.
- Confirm artifact cleanup policy: do not commit `timeline.json`, `remotion/public/*`, `remotion/out/*`, `assets/visuals/*`, caches, virtualenvs, or `node_modules`.
- Confirm `remotion/props.json` policy: commit only intentional sample updates.
- Confirm no forbidden behavior has been added: no Python Remotion wrapper, direct ffmpeg calls, DOCX parsing, AI generation, B-roll downloading, external media fetching, GUI, or schema changes.

## Packaging Metadata Review

Milestone 4 should review `pyproject.toml` without changing it unless a clear packaging bug is found. The expected current metadata is:

    [project]
    name = "synccut"
    version = "0.1.0"
    requires-python = ">=3.11"
    dependencies = ["typer>=0.12"]

    [project.optional-dependencies]
    dev = ["pytest>=8"]

    [project.scripts]
    synccut = "synccut.cli:app"

The package should remain editable-installable with:

    .venv/bin/python -m pip install -e '.[dev]'

Do not add packaging tools, release automation, publishing configuration, CI, or dependency changes unless validation reveals that the current metadata cannot install or expose the CLI.

## Plan of Work

First, update `README.md` from empty to a full root user guide using the structure above. Keep it concise and command-oriented. Prefer linking to deeper docs rather than copying full schemas or every Remotion environment transcript.

Second, decide whether to add `docs/commands.md`. If created, make it a dedicated Python CLI reference and link it from `README.md`. If not created, record in this plan why the README command section is enough.

Third, add `docs/release-checklist-v0.1.md` with a practical release checklist for maintainers. It should be possible to follow the checklist without changing source code or committing generated artifacts.

Fourth, run validation. At minimum, run Python tests, Remotion typecheck, and CLI help commands. Optionally run the full example workflow through verified preflight without rendering. Do not run a full render unless explicitly needed and already documented; render outputs must remain ignored if generated.

## Concrete Steps

Milestone 1 commands and edits:

1. From the repository root, edit `README.md`.
2. Include setup commands:

       python3 -m venv .venv
       .venv/bin/python -m pip install -e '.[dev]'
       cd remotion
       npm install

3. Include the minimal end-to-end workflow:

       .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
       .venv/bin/synccut validate-timeline timeline.json
       .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
       .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
       .venv/bin/synccut inspect-visual-assets remotion/props.json
       .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
       cd remotion
       npm run typecheck
       npm run render:smoke:local

4. Mention `npm run render:segment:local` and `npm run render:final:local` as longer local workflows, with a warning that they can take longer and require Chrome launch permission.

Milestone 2 commands and edits:

1. If needed, create `docs/commands.md`.
2. If `docs/commands.md` is created, add a link from `README.md`.
3. Do not change CLI behavior or command output.

Milestone 3 commands and edits:

1. Create `docs/release-checklist-v0.1.md`.
2. Keep it as a release operator checklist, not a product roadmap.
3. Do not add release automation or publishing scripts in this phase.

Milestone 4 validation:

1. From the repository root, run:

       .venv/bin/python -m pytest

   Expect all current tests to pass. The most recent known count is 208 tests.

2. From the Remotion project, run:

       cd remotion
       npm run typecheck

   Expect TypeScript to complete with `tsc --noEmit` and no errors.

3. From the repository root, run CLI help checks:

       .venv/bin/synccut --help
       .venv/bin/synccut build-timeline --help
       .venv/bin/synccut preflight --help

   Expect the documented command names and options to appear.

4. Optionally, run the example workflow through verified preflight:

       .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
       .venv/bin/synccut validate-timeline timeline.json
       .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
       .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
       .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

   Expected preflight status for the current sample is `warning`, with prepared audio, no audio missing public paths, no file errors, and visual warnings for missing optional `AI_VIDEO` and `B_ROLL` local assets.

## Validation and Acceptance

This phase is accepted when a new user can read the root README and perform the documented install and workflow without needing prior phase history. The documentation must clearly explain both what the MVP does and what it deliberately does not do.

Concrete acceptance criteria:

- `README.md` is no longer empty and includes overview, setup, quick start, command summary, Remotion workflow, asset policy, troubleshooting, development tests, and future-phase links.
- `docs/commands.md` exists if the command reference is split out, or the plan records that it was not needed because the README stayed readable.
- `docs/release-checklist-v0.1.md` exists and describes release validation and artifact policy.
- `pyproject.toml` is reviewed. If unchanged, this plan records that no metadata change was needed.
- `.venv/bin/python -m pytest` passes.
- `cd remotion && npm run typecheck` passes.
- CLI help commands confirm the docs match the installed command names and options.
- No generated artifacts are committed or recommended for commit.
- No Python source, Remotion component source, schema, or command behavior changes occur unless a clear bug is discovered and documented.

## Idempotence and Recovery

The documentation edits are safe to repeat. Re-running the example workflow overwrites generated `timeline.json` and `remotion/props.json`, reuses or updates copied public assets, and may create ignored artifacts. If validation regenerates files only for local testing, do not commit them unless they are intentionally maintained sample files.

If `npm install` is unavailable because dependencies are already installed or network is blocked, record the exact limitation in this plan and continue with `npm run typecheck` if `remotion/node_modules/` already exists. Do not vendor dependencies.

If a Remotion render command fails because Chrome launch is blocked by sandbox permissions, record the error and do not add workaround code. This release documentation phase does not require rendering a new full video.

If a packaging review finds a real issue in `pyproject.toml`, document the issue in `Surprises & Discoveries`, record the decision in `Decision Log`, and keep the fix narrowly scoped to packaging metadata.

## Artifacts and Notes

Current CLI help confirmed this command list:

    build-timeline
    validate-timeline
    inspect
    export-remotion
    prepare-remotion-assets
    prepare-visual-assets
    inspect-visual-assets
    preflight

Current `synccut build-timeline --help` confirmed required options:

    SCENES_JSON
    --audio-dir PATH
    --alignment-dir PATH
    --out PATH

Current `synccut preflight --help` confirmed options:

    PROPS_JSON
    --json
    --verify-files
    --public-dir PATH

Current Remotion scripts confirmed in `remotion/package.json`:

    studio
    typecheck
    still
    still:local
    render:smoke:local
    render:segment:local
    render:final:local

Known generated outputs and local-only directories:

    timeline.json
    remotion/public/
    remotion/out/
    assets/visuals/
    remotion/node_modules/
    .venv/
    __pycache__/
    .pytest_cache/

## Interfaces and Dependencies

Do not add new runtime dependencies in this phase. The Python package should continue to depend on Typer for CLI behavior and pytest as a development extra. The Remotion project should continue to use its existing React, Remotion, TypeScript, and type dependencies.

The root README and optional docs should document these public interfaces without changing them:

- Console entry point: `synccut`, provided by `pyproject.toml`.
- Python test command: `.venv/bin/python -m pytest`.
- Remotion typecheck command: `cd remotion && npm run typecheck`.
- Remotion local render commands: npm scripts in `remotion/package.json`.

The documentation should use repository-relative paths such as `docs/schemas.md`, `docs/matching.md`, `remotion/README.md`, and `docs/future-phases.md` so links work from a local checkout.
