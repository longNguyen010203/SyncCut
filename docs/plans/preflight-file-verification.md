# Add optional file verification to preflight

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already produce a props-only preflight report with:

    .venv/bin/synccut preflight remotion/props.json

That report checks whether `remotion/props.json` is structurally coherent, has prepared audio public paths, and has expected visual asset readiness metadata. It deliberately does not touch the filesystem. The next useful step is an explicit opt-in verification mode that confirms already-prepared Remotion public paths actually resolve to files under a local `remotion/public` directory.

After this phase, a user should be able to run:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

and receive the normal preflight report plus deterministic file verification errors when prepared audio or visual public paths are missing, point outside `remotion/public`, or point to directories instead of files. The command must remain read-only. It must not render video, invoke Remotion, npm, Chrome, Node, or ffmpeg, copy assets, generate or download media, probe/decode/transcode files, modify `remotion/props.json`, parse DOCX, or add GUI or web app behavior.

## Progress

- [x] (2026-05-12T09:27:34+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/preflight-render-readiness.md`, `docs/plans/remotion-audio-assets.md`, `docs/plans/remotion-visual-asset-strategy.md`, and `docs/plans/visual-asset-readiness-report.md`.
- [x] (2026-05-12T09:27:34+07:00) Inspected `synccut/preflight.py`, `synccut/cli.py`, `synccut/remotion_assets.py`, `synccut/visual_assets.py`, `tests/test_preflight.py`, `tests/test_cli.py`, `remotion/props.json`, and `.gitignore`.
- [x] (2026-05-12T09:27:34+07:00) Created this ExecPlan for optional preflight file verification.
- [x] (2026-05-12T09:36:55+07:00) Implemented Milestone 1: extended the pure preflight helper with optional file verification and focused tests.
- [x] (2026-05-12T09:41:24+07:00) Implemented Milestone 2: wired `--verify-files` and `--public-dir` into the `synccut preflight` CLI and added CLI tests.
- [x] (2026-05-12T13:33:25+07:00) Completed Milestone 3: validated file verification against fresh generated props, prepared public audio assets, pytest, Remotion typecheck, and artifact status.

## Surprises & Discoveries

- Observation: The current preflight helper is intentionally props-only.
  Evidence: `synccut/preflight.py` exposes `inspect_preflight(props, props_path)` and `inspect_preflight_file(props_path)` with no `public_dir` parameter, and it never calls `Path.exists()`, `Path.is_file()`, or media tooling.
- Observation: The current CLI exits nonzero for preflight error status after printing the report.
  Evidence: `synccut/cli.py` calls `inspect_preflight_file`, prints either `format_preflight(summary)` or JSON, and raises `typer.Exit(1)` when `summary.status == "error"`.
- Observation: Audio public paths are written into root audio assets, sections, and scenes, but Remotion playback is section-driven.
  Evidence: `synccut/remotion_assets.py` updates `assets.audio`, `sections[].audio`, and `scenes[].audio`, while prior Remotion work mounts one audio track per section using `section.audio.public_path`.
- Observation: Visual readiness already validates public path shape without checking disk.
  Evidence: `synccut/visual_assets.py` has `classify_visual_public_path(value)` and `inspect_visual_asset_readiness(props, props_path)`, which accept safe paths under `visuals/` with supported extensions and do not inspect the filesystem.
- Observation: The current generated `remotion/props.json` is a clean validation sample with prepared audio and no prepared visual assets.
  Evidence: Inspecting the file showed 33 scenes, 7 sections, 7 root audio assets, section audio public paths such as `audio/01_HOOK.mp3`, `assets.visuals: []`, and no scene visual public paths.
- Observation: Generated assets are already excluded broadly.
  Evidence: `.gitignore` contains `remotion/public`, `remotion/out/`, `timeline.json`, `assets/visuals/`, `__pycache__/`, and `.pytest_cache/`.
- Observation: Milestone 1 did not require CLI or Remotion changes.
  Evidence: Only `synccut/preflight.py`, `tests/test_preflight.py`, and this plan were edited. `synccut/cli.py`, Remotion files, generated props, and asset directories were not changed.
- Observation: The existing props-only output stayed compatible while verification output gained only opt-in fields.
  Evidence: Existing tests for stable text and JSON output still pass, and new verification tests assert `verify_files`, `public_dir`, and `file_errors` appear only when `verify_files=True`.
- Observation: Milestone 2 did not require helper, Remotion, props, or asset changes.
  Evidence: Only `synccut/cli.py`, `tests/test_cli.py`, and this plan were edited for Milestone 2. `.venv/bin/python -m pytest` collected 208 tests and all 208 passed.
- Observation: Typer accepted the optional `Path | None` `--public-dir` option with the existing annotation style.
  Evidence: CLI tests invoke `synccut preflight ... --verify-files --public-dir <tmp_public>` and `synccut preflight ... --public-dir <tmp_public>` successfully through `CliRunner`.
- Observation: Real generated props plus prepared audio produce the expected warning-only verified preflight state.
  Evidence: `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The verified JSON report includes the new verification keys only in verified mode.
  Evidence: `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public --json` returned parseable JSON with `verify_files: true`, `public_dir: "remotion/public"`, and `file_errors: 0`.

## Decision Log

- Decision: Keep the default preflight behavior byte-for-byte compatible when file verification is not requested.
  Rationale: Existing tests and users rely on `synccut preflight remotion/props.json` being a props-only report. The new feature is explicitly opt-in, so text and JSON output should not gain verification fields unless `verify_files` is enabled.
  Date/Author: 2026-05-12 / Codex
- Decision: Require `--public-dir` when `--verify-files` is set.
  Rationale: File verification must be explicit about which Remotion public directory is authoritative. Requiring the path avoids hidden assumptions about the current working directory or project layout.
  Date/Author: 2026-05-12 / Codex
- Decision: Treat `--public-dir` without `--verify-files` as a CLI usage error.
  Rationale: Silently ignoring a public directory path would be misleading. The option only has meaning when file verification is active.
  Date/Author: 2026-05-12 / Codex
- Decision: Verify only public paths that are supposed to be renderable by Remotion.
  Rationale: The purpose is to check prepared render inputs under `remotion/public`, not source files. Original paths such as `examples/audio/...` and `assets/visuals/...` are source references and should not be verified by this mode.
  Date/Author: 2026-05-12 / Codex
- Decision: Missing `AI_VIDEO` and `B_ROLL` visual assets remain warnings, not file errors.
  Rationale: Remotion components intentionally fall back to placeholders when optional visuals are missing. File verification should only error when props claim an asset is prepared and the prepared public file cannot be used.
  Date/Author: 2026-05-12 / Codex
- Decision: Treat malformed `assets.visuals` entries as file verification errors only in verification mode.
  Rationale: Root visual asset entries are an audit list for prepared files. Props-only preflight did not validate them, so the narrowest compatible behavior is to report malformed or missing root visual public paths only when `verify_files=True`.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep option validation in the CLI before calling the helper.
  Rationale: `--public-dir` without `--verify-files` is a command usage problem, not a props inspection problem. Handling it in `synccut/cli.py` keeps helper behavior focused on preflight inspection and keeps CLI error messages stable.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documents and inspecting the current preflight helper, CLI wiring, audio asset preparation helper, visual asset helper, tests, sample props, and ignore rules. No source code, tests, props, assets, package files, or command behavior has been changed yet for this phase.

The recommended implementation is additive. Extend `synccut/preflight.py` with optional parameters and file checking helpers, keep `verify_files=False` output unchanged, then wire CLI options in `synccut/cli.py`. Final validation should regenerate props and audio assets, run props-only preflight, run verified preflight against `remotion/public`, run pytest, and confirm no generated artifacts are commit candidates.

Milestone 1 is complete. `synccut/preflight.py` now accepts `verify_files` and `public_dir` in `inspect_preflight` and `inspect_preflight_file`, while existing calls without those arguments still work. `PreflightSummary` now carries `verify_files`, `public_dir`, and `file_errors`. When verification is disabled, `format_preflight` and `preflight_to_dict` preserve the previous props-only output shape. When verification is enabled, the helper requires a public directory, verifies only Remotion public paths, appends file errors after existing props and visual errors in deterministic order, and reports missing files, directories, invalid public paths, and paths outside the public directory without opening or probing media.

Milestone 1 tests passed. `tests/test_preflight.py` now covers default compatibility, read-only file helper behavior with verification disabled, helper-level missing public directory errors, successful section/root audio verification, successful prepared scene/root visual verification, missing section and root audio files, directory targets, absolute paths, `..` path segments, missing prepared visual files, missing visual placeholder behavior, unsupported visual path de-duplication, ignored scene audio public paths, ignored original source paths, malformed `assets.visuals`, verification text and JSON fields, and deterministic file error ordering. From the repository root, `.venv/bin/python -m pytest` collected 201 tests and all 201 passed. No CLI options, Remotion/npm/Chrome/Node invocation, media probing, ffmpeg, asset copying, final render, AI generation, B-roll download, GUI, or web app behavior was added.

Milestone 2 is complete. `synccut/cli.py` now adds `--verify-files` and `--public-dir` to the existing `synccut preflight` command. When neither option is set, the command still calls `inspect_preflight_file(props_json)` and preserves the existing props-only text and JSON behavior. When both options are set, it calls `inspect_preflight_file(props_json, verify_files=True, public_dir=public_dir)`. It rejects `--verify-files` without `--public-dir` with `Error: --public-dir is required when --verify-files is set`, rejects `--public-dir` without `--verify-files` with `Error: --public-dir can only be used with --verify-files`, catches `SyncCutError` as before, prints reports before exiting nonzero for `summary.status == "error"`, and remains read-only.

Milestone 2 tests passed. `tests/test_cli.py` now covers verified preflight text output, verified JSON output, missing verified files causing a nonzero exit after printing the report, option mismatch errors without tracebacks, malformed props in verified mode without traceback, and read-only behavior in verified mode. Existing props-only preflight CLI tests still pass unchanged. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. No file verification for `inspect-visual-assets`, asset copying, Remotion/npm/Chrome/Node invocation, media probing/transcoding, ffmpeg, final render, AI generation, B-roll download, GUI, or web app behavior was added.

Milestone 3 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Props-only preflight remained unchanged. `.venv/bin/synccut preflight remotion/props.json` reported `status: warning`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `fps: 30`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, and `errors: 0`. The warnings were the known root props warning plus 17 `visual_missing` warnings in scene order. The errors section printed `none`.

Verified preflight matched the expected clean result. `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public` reported the same warning-only summary and added `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The warnings remained the known root props warning plus the 17 `AI_VIDEO` and `B_ROLL` placeholder warnings. The errors section printed `none`.

Verified JSON preflight matched the text report. `.venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public --json` returned parseable JSON with `path: "remotion/props.json"`, `status: "warning"`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `fps: 30`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, 18 warning objects, an empty `errors` array, `verify_files: true`, `public_dir: "remotion/public"`, and `file_errors: 0`.

The prepared public audio files found were:

    remotion/public/audio/01_HOOK.mp3
    remotion/public/audio/02_INTRO.mp3
    remotion/public/audio/03_MECHANISM_1.mp3
    remotion/public/audio/04_MECHANISM_2.mp3
    remotion/public/audio/05_MECHANISM_3.mp3
    remotion/public/audio/06_MECHANISM_4.mp3
    remotion/public/audio/07_CONCLUSION.mp3

Final validation passed. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`.

Generated artifact and commit policy for Phase 12: `timeline.json` was regenerated and is ignored; `remotion/public/` contains prepared audio and remains ignored; `remotion/out/` remains ignored if prior preview artifacts exist; `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, and Python `__pycache__/` directories are ignored. `git status --short --ignored` showed commit candidates `synccut/preflight.py`, `synccut/cli.py`, `tests/test_preflight.py`, `tests/test_cli.py`, and `docs/plans/preflight-file-verification.md`, plus ignored generated artifacts. Do not commit `timeline.json`, `remotion/public/*`, `remotion/out/*`, `assets/visuals/*`, `remotion/props.json` if it only changed because of generated validation, `.pytest_cache/`, or `__pycache__/`.

Phase 12 outcome: `synccut preflight` now has an opt-in file verification mode. The default props-only command remains unchanged. The verified command checks only prepared Remotion public paths under the supplied public directory, reports file verification errors deterministically, preserves warning-only status for missing optional AI/B-roll visuals, and remains read-only. No file verification for `inspect-visual-assets`, asset copying changes, Remotion/npm/Chrome/Node invocation, media probing/transcoding, ffmpeg, final render, AI generation, B-roll download, GUI, or web app behavior was added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ Typer CLI package under `synccut/`. The Remotion project lives under `remotion/` and reads `remotion/props.json`.

The current production workflow relevant to this phase is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json

The command being extended is:

    .venv/bin/synccut preflight remotion/props.json

Preflight means a read-only readiness report. It checks already-exported Remotion props before a future full render attempt. It is not a renderer, not an asset preparer, and not a media validator.

A public path means a path string relative to `remotion/public`, such as `audio/01_HOOK.mp3` or `visuals/scene_001.png`. Remotion components use these values with `staticFile(...)`. A source path means an original file path such as `examples/audio/01_HOOK.mp3` or `assets/visuals/scene_001.png`; source paths are not public paths and are not used directly by Remotion.

The files most relevant to this phase are:

    synccut/preflight.py
    synccut/cli.py
    synccut/remotion_assets.py
    synccut/visual_assets.py
    tests/test_preflight.py
    tests/test_cli.py
    remotion/props.json
    .gitignore

`synccut/preflight.py` currently defines `PreflightIssue`, `PreflightSummary`, `inspect_preflight`, `inspect_preflight_file`, `format_preflight`, and `preflight_to_dict`. `synccut/cli.py` exposes `synccut preflight` and keeps CLI logic thin by delegating to `inspect_preflight_file`.

## Current Preflight Behavior

The current preflight command is props-only. It reads `remotion/props.json`, validates composition fields, metadata consistency, section timing, scene timing, section audio public paths, root audio public paths, root warning strings, and visual readiness for `AI_VIDEO` and `B_ROLL` scenes. It returns a status:

- `ok` when there are no warnings and no errors.
- `warning` when there are warnings and no errors.
- `error` when there is at least one error.

Missing section audio public paths and missing root audio public paths are errors. Missing `AI_VIDEO` and `B_ROLL` visual public paths are warnings because placeholders can render. Unsupported or malformed visual public paths are errors because props claim a prepared asset but the path is unsafe or unsupported.

The current text output has this shape:

    Preflight: remotion/props.json
    status: warning
    scenes: 33
    sections: 7
    duration_sec: 752.79
    duration_frames: 22584
    fps: 30
    audio_prepared: 7
    audio_missing_public_path: 0
    visual_target_scenes: 17
    visual_prepared: 0
    visual_missing: 17
    visual_unsupported: 0
    warnings: 18
    errors: 0

    Warnings:
    warning props_warning section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031
    warning visual_missing scene_001 AI_VIDEO missing visual asset; placeholder will render

    Errors:
    none

The current JSON output is the same data as a deterministic object printed with two-space indentation.

## New CLI Options

Add two options to the existing `synccut preflight` command:

    --verify-files
    --public-dir remotion/public

The intended invocation is:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

`--verify-files` enables filesystem checks. `--public-dir` identifies the local Remotion public directory that public paths should resolve under.

`--public-dir` should be required when `--verify-files` is set. If a user runs `synccut preflight remotion/props.json --verify-files` without `--public-dir`, print a clear `Error: --public-dir is required when --verify-files is set` message to stderr and exit 1 without a traceback.

If a user passes `--public-dir` without `--verify-files`, treat it as a usage error with `Error: --public-dir can only be used with --verify-files` and exit 1. This keeps the CLI from accepting a path that has no effect.

Both options must work with `--json`:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public --json

For `ok` and `warning` status, the CLI exits 0. For `error` status, the CLI prints the report and exits 1, matching existing preflight behavior.

## What File References To Verify

When `verify_files=True`, verify only public paths that Remotion is expected to use.

Verify section audio public paths:

    props["sections"][*]["audio"]["public_path"]

Every section audio public path that is a non-empty string should resolve to a file under `public_dir`. Missing section public paths are already props-only preflight errors, so the file verifier should not add duplicate invalid path errors for absent values.

Verify root audio asset public paths:

    props["assets"]["audio"][*]["public_path"]

Every root audio asset public path that is a non-empty string should resolve to a file under `public_dir`. Missing root audio public paths are already props-only errors, so skip duplicate file-path errors for absent values.

Verify prepared scene visual public paths for target visual scenes:

    props["scenes"][*]["visual"]["public_path"]

Only `AI_VIDEO` and `B_ROLL` scenes are target visual scenes. Only verify a scene visual file when visual readiness classifies that scene as `prepared`, which requires `asset_status == "prepared"` and a valid public path under `visuals/`. Missing visual assets stay warnings and do not produce file errors. Unsupported visual public paths already produce visual readiness errors and should not receive duplicate missing-file errors.

Verify root visual asset public paths when present:

    props["assets"]["visuals"][*]["public_path"]

If `assets.visuals` exists and contains prepared visual entries, verify each non-empty `public_path`. These entries are an audit list written by `prepare-visual-assets`; they should be consistent with files under `remotion/public/visuals/`. If an entry is missing a public path or has an invalid public path, report a file verification error for that entry.

Do not verify scene audio public paths. Remotion audio playback is section-driven in this project, so `scenes[].audio.public_path` is redundant metadata for this phase. If section audio is prepared, scene audio may remain path-only without blocking preflight.

Do not verify original source path fields such as:

    examples/audio/01_HOOK.mp3
    assets/visuals/scene_001.png

Those paths are not Remotion public paths. They may point outside `remotion/public` by design.

## Safe Path Resolution

File verification must treat every public path as untrusted input from JSON.

A public path is valid for verification only when:

- it is a non-empty string;
- it is relative, not absolute;
- it does not contain `..` as a path segment;
- it can be joined to `public_dir`;
- its resolved absolute path remains inside the resolved `public_dir`.

Use `pathlib.Path` for all path work. Do not use string concatenation to build filesystem paths.

The helper should resolve paths with a pattern like this in spirit:

    public_root = public_dir.resolve()
    relative_path = Path(public_path)
    candidate = (public_root / relative_path).resolve()
    candidate.relative_to(public_root)

Do not require the target file to exist before doing the inside-public-dir check, because missing files are one of the expected errors to report. In Python, `Path.resolve(strict=False)` can resolve a path even when the final file does not exist.

Reject absolute paths with `invalid_public_path`. Reject paths containing `..` with `invalid_public_path`. If the final resolved path cannot be expressed relative to `public_root`, report `public_path_outside_public_dir`.

The path-shape verification here is generic for public files. Visual-specific extension validation remains in `synccut.visual_assets.classify_visual_public_path` for scene visual readiness.

## File Existence Checks

Verification is intentionally shallow. It should only check filesystem existence and file-ness:

- If the resolved path does not exist, add an error with code `missing_public_file`.
- If the resolved path exists but is a directory, add an error with code `public_path_is_directory`.
- If the resolved path exists and is a regular file, it passes verification.

Do not open, decode, probe, normalize, transcode, inspect, or hash media files. Do not call ffmpeg, ffprobe, Remotion, Node, npm, Chrome, or any external media command.

## Status and Output Effects

Verification errors are preflight errors. If file verification finds any problem, `summary.status` must become `error` and the CLI must exit 1 after printing the report.

When `verify_files=False`, the default text and JSON output must remain compatible with the existing props-only command. This means no new `verify_files`, `public_dir`, or `file_errors` lines or JSON keys are printed in default mode. The dataclass may contain these fields internally, but formatting should omit them unless verification is enabled.

When `verify_files=True`, add these lines to text output after the existing `errors: <count>` summary line and before the blank line:

    verify_files: true
    public_dir: remotion/public
    file_errors: 0

If verification is active and errors are found, `file_errors` should be the number of file verification errors added to `summary.errors`.

When `verify_files=True`, add these keys to JSON output:

    "verify_files": true
    "public_dir": "remotion/public"
    "file_errors": 0

When verification is disabled, omit those JSON keys to preserve the existing machine-readable shape.

Use stable issue codes:

- `missing_public_file`
- `invalid_public_path`
- `public_path_outside_public_dir`
- `public_path_is_directory`

Issue messages should include enough context to find the bad reference. Use concise messages like:

    section 01_HOOK audio public_path audio/01_HOOK.mp3 missing under remotion/public
    root audio 01_HOOK public_path audio/01_HOOK.mp3 is a directory under remotion/public
    scene scene_001 AI_VIDEO public_path visuals/scene_001.png missing under remotion/public
    root visual scene_001 public_path /tmp/scene_001.png is not a relative public path

Append file verification errors after existing props and visual readiness errors. Keep the order deterministic:

1. section audio public paths in section order;
2. root audio assets in array order;
3. prepared scene visual public paths in scene order;
4. root `assets.visuals` entries in array order.

## Helper and Data Model Design

Extend `synccut/preflight.py` without changing existing default call behavior.

Add fields to `PreflightSummary`:

    verify_files: bool
    public_dir: Path | None
    file_errors: int

To preserve simple construction in tests, place these fields after the existing warnings and errors fields or give them explicit defaults if practical. The important behavior is that `inspect_preflight(..., verify_files=False)` and `inspect_preflight_file(..., verify_files=False)` keep returning a usable summary without requiring callers to pass new arguments.

Update helper signatures to:

    inspect_preflight(
        props: dict[str, Any],
        props_path: Path,
        verify_files: bool = False,
        public_dir: Path | None = None,
    ) -> PreflightSummary

    inspect_preflight_file(
        props_path: Path,
        verify_files: bool = False,
        public_dir: Path | None = None,
    ) -> PreflightSummary

The file helper should keep using `load_remotion_props` from `synccut.remotion_assets` and should not modify the file.

Add private helper functions in `synccut/preflight.py`:

    _file_verification_checks(props, public_dir, scenes, sections, visual_summary) -> tuple[list[PreflightIssue], int]
    _verify_public_file(public_path, public_dir, context) -> PreflightIssue | None
    _resolve_public_path(public_path, public_dir) -> Path | PreflightIssue

The exact private function names can differ, but the behavior should be testable and deterministic.

Use the existing visual readiness result from `inspect_visual_asset_readiness(props, props_path)` so the file verifier can verify only scene visual items with status `prepared`. This avoids repeating scene target selection or visual public path rules.

For root `assets.visuals`, inspect the array directly. If `assets.visuals` is absent, treat it as an empty list for file verification because clean exported props may include an empty list and visual assets are optional. If it exists but is not a list, the existing structural checks do not currently validate it; add a file verification error with `invalid_public_path` or a structural preflight error only when verification is active. Keep this narrow so props-only behavior stays unchanged.

Update `format_preflight(summary)` so it includes verification lines only when `summary.verify_files` is true. Update `preflight_to_dict(summary)` so it includes verification keys only when `summary.verify_files` is true.

## CLI Behavior

In `synccut/cli.py`, update the existing `preflight` command only. Keep the CLI thin.

The Typer command should accept:

    props_json: Path
    --json
    --verify-files
    --public-dir PATH

Implementation behavior:

1. If `verify_files` is true and `public_dir` is absent, print `Error: --public-dir is required when --verify-files is set` to stderr and exit 1.
2. If `verify_files` is false and `public_dir` is present, print `Error: --public-dir can only be used with --verify-files` to stderr and exit 1.
3. Call `inspect_preflight_file(props_json, verify_files=verify_files, public_dir=public_dir)`.
4. Catch `SyncCutError`, print `Error: <message>` to stderr, and exit 1 without a Python traceback.
5. Print formatted text by default.
6. Print `json.dumps(preflight_to_dict(summary), indent=2)` plus a trailing newline when `--json` is set.
7. Exit 1 when `summary.status == "error"`, otherwise exit 0.

The command must be read-only. It must not write props, copy assets, invoke Remotion, run npm, launch Chrome, call ffmpeg, or probe media.

## Tests to Write

Add focused helper tests in `tests/test_preflight.py`.

Cover default compatibility:

- Props-only `format_preflight` output remains unchanged when `verify_files=False`.
- Props-only `preflight_to_dict` output remains unchanged when `verify_files=False`.
- `inspect_preflight_file(..., verify_files=False)` remains read-only.

Cover successful verification:

- Prepared section audio and root audio files under a temporary public directory produce `file_errors: 0`.
- A prepared visual public path for an `AI_VIDEO` or `B_ROLL` scene produces `file_errors: 0` when the file exists.
- A root `assets.visuals` public path produces `file_errors: 0` when the file exists.

Cover file errors:

- Missing section audio file reports `missing_public_file` and status `error`.
- Missing root audio file reports `missing_public_file` and status `error`.
- Existing directory for a public path reports `public_path_is_directory`.
- Absolute public path reports `invalid_public_path`.
- Public path containing `..` reports `invalid_public_path`.
- A path that resolves outside `public_dir` reports `public_path_outside_public_dir` if a test can create that condition without relying on platform-specific behavior; otherwise cover the helper directly with the nearest deterministic case.
- Prepared visual scene with a valid public path but missing file reports `missing_public_file`.
- Missing visual scene with `asset_status: "missing"` does not produce a file error.
- Unsupported visual path remains the existing visual readiness error and does not get an additional missing-file error.
- Scene audio public paths are ignored by file verification.
- Original `path` fields outside `public_dir` are ignored.

Cover output:

- Text output with verification enabled includes `verify_files: true`, `public_dir: <path>`, and `file_errors: <count>`.
- JSON output with verification enabled includes `verify_files`, `public_dir`, and `file_errors`.
- Error issue ordering is deterministic.

Add CLI tests in `tests/test_cli.py`.

Cover:

- `synccut preflight props.json --verify-files --public-dir <tmp_public>` exits 0 for warning-only props with all expected files present and prints verification fields.
- `synccut preflight props.json --verify-files --public-dir <tmp_public> --json` exits 0 and returns parseable JSON with verification fields.
- Missing verified file exits nonzero after printing the report.
- `--verify-files` without `--public-dir` exits nonzero with `Error:` and no traceback.
- `--public-dir` without `--verify-files` exits nonzero with `Error:` and no traceback.
- Malformed props still fail with `Error:` and no traceback.
- The command is read-only by comparing props file contents before and after.

Existing CLI tests for the props-only preflight output should continue to pass unchanged.

## Milestones

Milestone 1 extends the pure helper layer. Edit only `synccut/preflight.py`, `tests/test_preflight.py`, and this plan. Add optional `verify_files` and `public_dir` parameters, add verification fields to `PreflightSummary`, implement safe public path resolution and shallow file checks, and add helper tests. Do not edit `synccut/cli.py` yet. Do not modify Remotion files or generated props. Validate with:

    .venv/bin/python -m pytest

Acceptance for Milestone 1 is that all tests pass, default props-only helper output remains unchanged, and direct helper tests prove file verification can report missing files, directories, unsafe public paths, and successful existing files.

Milestone 2 wires the CLI. Edit only `synccut/cli.py`, `tests/test_cli.py`, and this plan unless Milestone 1 exposed a clear helper bug. Add `--verify-files` and `--public-dir`, require them together as described above, pass options to `inspect_preflight_file`, preserve existing `--json` behavior, and keep error handling traceback-free. Validate with:

    .venv/bin/python -m pytest

Acceptance for Milestone 2 is that the CLI remains read-only, props-only command output still matches existing tests, verified mode outputs verification fields, verified missing files cause exit 1 after printing the report, and malformed props still produce `Error:` without traceback.

Milestone 3 validates against real generated props and prepared assets. Do not change source code unless a clear bug is discovered. From the repository root, run:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public --json
    .venv/bin/python -m pytest

From `remotion/`, run:

    npm run typecheck

Acceptance for Milestone 3 is that props-only preflight still reports the clean warning-only state, verified preflight reports the same warning-only visual state plus `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0` for prepared audio files, pytest passes, Remotion typecheck passes, and generated artifacts are not commit candidates.

## Validation and Acceptance

The finished feature is accepted when these commands demonstrate the behavior.

From the repository root, regenerate data:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Run props-only preflight:

    .venv/bin/synccut preflight remotion/props.json

Expected behavior: output remains the existing props-only report. For clean generated props with prepared audio and no local visual files, it should be `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `errors: 0`, and warnings for the known root props warning plus missing visual placeholders.

Run verified preflight:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected behavior: the report includes `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0` when `remotion/public/audio/*.mp3` files prepared by `prepare-remotion-assets` exist. The status should remain `warning` because missing `AI_VIDEO` and `B_ROLL` visuals still render placeholders and are not file errors.

Run JSON verified preflight:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public --json

Expected behavior: the output is parseable JSON with the existing preflight fields plus `verify_files: true`, `public_dir: "remotion/public"`, and `file_errors: 0`.

Run tests:

    .venv/bin/python -m pytest

Expected behavior: all tests pass.

Run Remotion typecheck from `remotion/`:

    npm run typecheck

Expected behavior: TypeScript typecheck passes. This phase should not edit Remotion source, but typecheck confirms generated props and Remotion code still agree.

## Idempotence and Recovery

The feature is read-only at runtime. Running `synccut preflight` with or without file verification must not modify `remotion/props.json`, `remotion/public`, or any source file.

The validation commands are safe to rerun. `build-timeline`, `export-remotion`, and `prepare-remotion-assets` intentionally regenerate local artifacts. If validation leaves generated changes, clean them by regenerating clean props:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not use destructive git commands. Do not delete ignored artifacts unless the user explicitly asks.

If verified preflight reports missing public files after `prepare-remotion-assets`, inspect `remotion/public/audio/` with:

    find remotion/public/audio -maxdepth 1 -type f | sort

Do not add workaround code that copies assets inside preflight. Asset copying belongs to `prepare-remotion-assets` and `prepare-visual-assets`.

## Artifacts and Commit Policy

Do not commit generated artifacts:

- `timeline.json`
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.pytest_cache/`
- `__pycache__/`

Do not commit `remotion/props.json` if it only changed because of validation regeneration. `remotion/props.json` is useful sample data in earlier phases, but this phase should not require committing a regenerated copy unless the user explicitly approves it.

Expected commit candidates after implementation are:

- `docs/plans/preflight-file-verification.md`
- `synccut/preflight.py`
- `synccut/cli.py`
- `tests/test_preflight.py`
- `tests/test_cli.py`

No Remotion rendering source, package script, Python asset preparation behavior, exporter behavior, or validator behavior should change unless a clear bug is discovered and documented in this plan.

## Explicit Exclusions

Do not implement any of the following in this phase:

- full MP4 render or final assembly;
- Remotion, npm, Chrome, or Node invocation from Python;
- ffmpeg or ffprobe calls;
- media probing, decoding, transcoding, trimming, or normalization;
- asset copying inside preflight;
- AI image or video generation;
- B-roll download, scraping, or external fetch;
- DOCX parsing;
- GUI or web app behavior;
- `--verify-files` support for `inspect-visual-assets`;
- automatic defaulting to a hidden public directory;
- changes to `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, or props-only preflight behavior.

## Notes

2026-05-12: Created this plan to add explicit, opt-in file verification to `synccut preflight`. The plan preserves existing props-only behavior by default and documents a narrow, read-only verification mode for Remotion public paths under a user-supplied `--public-dir`.
