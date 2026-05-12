# Add a full render readiness preflight report

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can now build a timed timeline, validate it, export `remotion/props.json`, prepare section audio for Remotion, optionally prepare local visual files for `AI_VIDEO` and `B_ROLL`, and inspect visual asset readiness. Before anyone attempts a future full render, they need one read-only command that answers whether the current Remotion props are ready enough for that render attempt.

After this phase, a user should be able to run:

    .venv/bin/synccut preflight remotion/props.json

and receive a stable report summarizing composition timing, scene and section counts, audio public path readiness, visual asset readiness, root warnings, and structural problems. The command must not render video, invoke Remotion, copy files, generate or download assets, call ffmpeg, probe/decode/transcode media, modify `remotion/props.json`, parse DOCX, add GUI or web app behavior, or change existing command behavior.

## Progress

- [x] (2026-05-12T01:29:40Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, and the prior phase ExecPlans through `docs/plans/visual-asset-readiness-report.md`.
- [x] (2026-05-12T01:29:40Z) Inspected `synccut/remotion_exporter.py`, `synccut/remotion_assets.py`, `synccut/visual_assets.py`, `synccut/timeline_validator.py`, `synccut/cli.py`, `tests/test_visual_assets.py`, `tests/test_cli.py`, `remotion/props.json`, `remotion/package.json`, and `remotion/README.md`.
- [x] (2026-05-12T01:29:40Z) Created this ExecPlan for the read-only full render readiness preflight report.
- [x] (2026-05-12T01:40:39Z) Implemented Milestone 1: added the pure props-only preflight helper module and focused tests.
- [x] (2026-05-12T02:04:40Z) Implemented Milestone 2: wired the `synccut preflight` CLI command with text and JSON output.
- [x] (2026-05-12T02:10:21Z) Completed Milestone 3: validated preflight against fresh generated real props, pytest, Remotion typecheck, and artifact status.

## Surprises & Discoveries

- Observation: The working tree was clean at plan creation.
  Evidence: `git status --short` printed no changes.
- Observation: `remotion/props.json` is currently clean after prior validation and has prepared section audio but no prepared local visual assets.
  Evidence: Inspecting the file reported 33 scenes, 7 sections, 7 root audio assets, `assets.visuals: []`, first section audio with `public_path: "audio/01_HOOK.mp3"`, first scene audio with the same public path, and first `AI_VIDEO` visual without `public_path`, `asset_status`, or `asset_source`.
- Observation: The visual readiness helper already provides the exact props-only classification needed for preflight.
  Evidence: `synccut/visual_assets.py` exposes `inspect_visual_asset_readiness(props, props_path)`, `format_visual_asset_readiness(summary)`, `visual_asset_readiness_to_dict(summary)`, and `classify_visual_public_path(value)`, and it targets only `AI_VIDEO` and `B_ROLL`.
- Observation: Audio preparation writes `public_path` in three places, but Remotion playback is section-driven.
  Evidence: `synccut/remotion_assets.py` updates `assets.audio`, `sections[].audio`, and `scenes[].audio`; `remotion/README.md` and prior plans describe Remotion mounting one audio track per section.
- Observation: Milestone 1 did not require CLI, Remotion, props, asset, or filesystem verification changes.
  Evidence: Only `synccut/preflight.py`, `tests/test_preflight.py`, and this ExecPlan were edited. `.venv/bin/python -m pytest` collected 176 tests and all 176 passed.
- Observation: The existing visual readiness helper intentionally raises `SyncCutError` for malformed target scene visual shapes.
  Evidence: `inspect_visual_asset_readiness` validates `scene.visual.type` for `AI_VIDEO` and `B_ROLL`. Milestone 1 catches that expected error inside preflight and records an `invalid_visual_readiness` report error so ordinary preflight output can still summarize the file.
- Observation: Milestone 2 needed no preflight helper changes.
  Evidence: Only `synccut/cli.py`, `tests/test_cli.py`, and this ExecPlan were edited for Milestone 2. `.venv/bin/python -m pytest` collected 181 tests and all 181 passed.
- Observation: Fresh clean props produce the expected warning-only preflight state.
  Evidence: After regenerating `timeline.json`, exporting `remotion/props.json`, and running `prepare-remotion-assets`, `synccut preflight remotion/props.json` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, and `errors: 0`.
- Observation: Milestone 3 validation did not require source changes.
  Evidence: The only source/test changes remain the Milestone 1 and 2 files. Final validation passed with `.venv/bin/python -m pytest` collecting 181 tests and passing all 181, and `npm run typecheck` passing from `remotion/`.

## Decision Log

- Decision: Implement the first preflight as a props-only report.
  Rationale: The user requested a full render readiness report from `remotion/props.json`, and the existing visual readiness command is also props-only. Filesystem verification would require local `remotion/public` assumptions and should be an explicit future `--verify-files` mode, not default behavior.
  Date/Author: 2026-05-12 / Codex
- Decision: Treat missing section or root audio `public_path` as an error.
  Rationale: Remotion section audio uses `section.audio.public_path`. If section audio is not prepared, a future full render would omit narration. Root `assets.audio` missing public paths also means the asset preparation step is incomplete or inconsistent.
  Date/Author: 2026-05-12 / Codex
- Decision: Treat missing `AI_VIDEO` and `B_ROLL` visual assets as warnings, not errors.
  Rationale: The Remotion components intentionally fall back to `PlaceholderScene` when optional visual assets are missing, so the composition can still render. The report should make placeholders visible without blocking render attempts.
  Date/Author: 2026-05-12 / Codex
- Decision: Treat unsupported visual public paths as errors.
  Rationale: An unsupported or unsafe `visual.public_path` means props claim to have a local visual asset but Remotion will reject it and fall back. That is more serious than no asset at all because it indicates a malformed prepared state.
  Date/Author: 2026-05-12 / Codex
- Decision: Add `--json` to the preflight command if it remains a thin serialization of the helper summary.
  Rationale: The report is naturally structured and useful for future CI or scripts. A simple boolean option matches `inspect-visual-assets --json` without adding format negotiation.
  Date/Author: 2026-05-12 / Codex
- Decision: Reuse `load_remotion_props` from `synccut.remotion_assets` for the file helper.
  Rationale: That helper already reads Remotion props JSON, reports file and JSON failures as `SyncCutError`, and does not modify files. Reusing it keeps preflight focused on inspection instead of duplicating JSON loading.
  Date/Author: 2026-05-12 / Codex
- Decision: Collect composition, metadata, section, scene, audio, warning, and visual readiness problems as report issues after the root `scenes` and `sections` arrays are confirmed.
  Rationale: Preflight is a report command, so users should see all ordinary readiness problems at once. Missing or non-array `scenes` and `sections` still raise `SyncCutError` because the report cannot compute basic counts or visual readiness without them.
  Date/Author: 2026-05-12 / Codex
- Decision: Convert visual readiness helper `SyncCutError` failures into an `invalid_visual_readiness` preflight error after scene-level structural checks run.
  Rationale: A malformed target visual should make preflight status `error`, but it should not prevent the rest of the props summary from being displayed. This keeps preflight report-oriented while still preserving clear failure information.
  Date/Author: 2026-05-12 / Codex
- Decision: Have the CLI print the preflight report before exiting non-zero for `summary.status == "error"`.
  Rationale: The command is a report command. Users need the structured report even when the result is not render-ready, while the non-zero exit code still makes error status usable in automation.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documents and inspecting the current Python exporter, asset preparation helpers, visual readiness helper, CLI, tests, Remotion sample props, Remotion scripts, and Remotion README. No source code, tests, generated props, assets, package scripts, Remotion files, or command behavior has been changed yet for this phase.

Milestone 1 is complete. `synccut/preflight.py` now defines `PreflightIssue` and `PreflightSummary` plus pure read-only helpers: `inspect_preflight`, `inspect_preflight_file`, `format_preflight`, and `preflight_to_dict`. The helper validates composition fields, optional metadata consistency, section frame timing, scene frame timing, section audio public paths, root `assets.audio` public paths, root warning strings, and visual readiness from `inspect_visual_asset_readiness`. It reports `ok`, `warning`, or `error` status, derives `duration_sec` from composition timing when metadata duration is absent, treats missing AI/B-roll visual assets as warnings, treats unsupported visual public paths as errors, and does not check filesystem existence.

Milestone 1 tests passed. `tests/test_preflight.py` covers prepared audio with missing visual warnings, section audio prepared counts, missing section and root audio public paths, scene audio remaining path-only, missing and prepared AI/B-roll visuals, unsupported visual public paths, carried root warnings, malformed composition, non-positive fps and duration frames, missing/non-array scenes and sections `SyncCutError` failures, negative frames, frame bounds, duration mismatches, metadata count mismatches, target visual shape failures reported as preflight errors, stable text output, deterministic JSON dictionary output, file-helper read-only behavior, non-string root warnings, duration derivation, and input immutability. From the repository root, `.venv/bin/python -m pytest` collected 176 tests and all 176 passed. No `preflight` CLI command, `--json` CLI option, filesystem verification, asset copying, Remotion invocation, npm/Chrome use, AI generation, B-roll download, ffmpeg, media probing/transcoding, final render, GUI, or web app behavior was added.

Milestone 2 is complete. `synccut/cli.py` now exposes `synccut preflight remotion/props.json` and `synccut preflight remotion/props.json --json`. The command is thin: it calls `inspect_preflight_file`, catches `SyncCutError` as `Error: ...` with exit code 1 and no traceback, prints `format_preflight(summary)` by default, prints `json.dumps(preflight_to_dict(summary), indent=2)` for `--json`, exits 0 for `ok` and `warning`, and exits 1 after printing the report for `error` status. The command does not write props, copy assets, verify files, invoke Remotion, run npm or Chrome, or call media tooling.

Milestone 2 tests passed. `tests/test_cli.py` now covers warning-status preflight text output with exit 0, `--json` output with parseable deterministic JSON, error-status exit 1 after printing the report, malformed props returning `Error:` without traceback, and read-only behavior by comparing props file contents before and after command execution. From the repository root, `.venv/bin/python -m pytest` collected 181 tests and all 181 passed. Existing CLI tests for build, validate, inspect, export, audio asset preparation, visual asset preparation, and visual readiness still pass.

Milestone 3 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

The real preflight text report matched the expected clean-props result. `.venv/bin/synccut preflight remotion/props.json` reported `status: warning`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `fps: 30`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, and `errors: 0`. The warning rows included the known root props warning for the `07_CONCLUSION` gap followed by 17 `visual_missing` warnings in scene order for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`. The errors section printed `none`.

The real preflight JSON report matched the text summary. `.venv/bin/synccut preflight remotion/props.json --json` returned parseable JSON with `path: "remotion/props.json"`, `status: "warning"`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `fps: 30`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, 18 warning objects, and an empty `errors` array.

Final validation passed. From the repository root, `.venv/bin/python -m pytest` collected 181 tests and all 181 passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`.

Generated artifact and commit policy for Phase 11: `timeline.json` was regenerated and is ignored; `remotion/public/` contains prepared audio and remains ignored; `remotion/out/` remains ignored if prior preview artifacts exist; `.pytest_cache/`, `.venv/`, Python `__pycache__/`, `assets/`, `examples/`, and `remotion/node_modules/` are ignored. `git status --short --ignored` showed commit candidates `synccut/cli.py`, `tests/test_cli.py`, `docs/plans/preflight-render-readiness.md`, `synccut/preflight.py`, and `tests/test_preflight.py`, plus ignored generated artifacts. Do not commit `timeline.json`, `remotion/public/*`, `remotion/out/*`, `assets/visuals/*`, `.pytest_cache/`, or `__pycache__/`. Do not commit `remotion/props.json` if it only changed due generated validation.

Phase 11 outcome: SyncCut now has a read-only props-only full render readiness preflight report. The helper and CLI summarize structural props health, prepared section audio, root audio public paths, visual asset readiness, and warnings without checking filesystem existence, copying assets, invoking Remotion, running npm or Chrome, generating media, downloading B-roll, calling ffmpeg, probing/transcoding media, rendering final video, or adding GUI/web app behavior.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ Typer CLI package under `synccut/`. The Remotion app lives under `remotion/`, but this phase should not edit Remotion rendering code unless a clear bug is discovered.

The current Python workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json

The new command for this phase is:

    .venv/bin/synccut preflight remotion/props.json

A preflight report is a read-only readiness check. It looks at already exported and prepared Remotion props and reports whether the data is coherent enough to justify trying a future full render. It does not render anything and does not prove that files exist on disk.

The most relevant source files are:

    synccut/cli.py
    synccut/preflight.py
    synccut/remotion_assets.py
    synccut/remotion_exporter.py
    synccut/timeline_validator.py
    synccut/visual_assets.py
    synccut/validators.py
    tests/test_cli.py
    tests/test_preflight.py
    tests/test_visual_assets.py

`synccut/preflight.py` now exists after Milestone 1 and contains the pure helper layer. Keep `synccut/cli.py` thin in Milestone 2 by delegating to that helper module.

## Input

The command accepts one input file:

    remotion/props.json

The file must be a JSON object. It is produced by `synccut export-remotion` and may later be updated in place by `prepare-remotion-assets` and `prepare-visual-assets`.

The expected top-level props shape is:

    {
      "metadata": {...},
      "composition": {...},
      "sections": [...],
      "scenes": [...],
      "assets": {
        "audio": [...],
        "visuals": [...]
      },
      "warnings": [...]
    }

The current generated sample has 33 scenes, 7 sections, `composition.id: "SyncCutVideo"`, `composition.fps: 30`, `composition.duration_frames: 22584`, 7 prepared root audio assets, and `assets.visuals: []`.

## What Preflight Checks From Props Only

Preflight should inspect these facts from the props JSON:

Composition:

- `composition` exists and is an object.
- `composition.id` is a non-empty string.
- `composition.width` and `composition.height` are positive integers.
- `composition.fps` is a positive integer.
- `composition.duration_frames` is a positive integer.

Metadata:

- `metadata` exists and is an object when present in exported props.
- `metadata.duration_sec` is a positive number when present.
- `metadata.duration_frames` should match `composition.duration_frames` when present.
- `metadata.fps` should match `composition.fps` when present.
- `metadata.total_scenes` should match `len(scenes)` when present.
- `metadata.total_sections` should match `len(sections)` when present.

Sections:

- `sections` exists and is an array.
- Every section is an object.
- Every section has non-empty `section_key`.
- Every section has integer `start_frame`, `end_frame`, and `duration_frames`.
- Section frames are non-negative.
- `duration_frames` is positive.
- `end_frame - start_frame == duration_frames`.
- `end_frame <= composition.duration_frames`.
- `section.audio` exists as an object.
- `section.audio.path` is a non-empty string.
- `section.audio.public_path` is a non-empty string.

Scenes:

- `scenes` exists and is an array.
- Every scene is an object.
- Every scene has non-empty `id` and `section_key`.
- Every scene has supported `visual_type`, using the existing supported values `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`.
- Every scene has integer `start_frame`, `end_frame`, and `duration_frames`.
- Scene frames are non-negative.
- `duration_frames` is positive.
- `end_frame - start_frame == duration_frames`.
- `end_frame <= composition.duration_frames`.
- `scene.visual` exists as an object.
- `scene.visual.type` matches `scene.visual_type`.
- `scene.dialogue` exists as an object with non-empty `text` when present in exported props.

Audio assets:

- `assets` exists and is an object.
- `assets.audio` exists and is an array.
- Every root audio asset has non-empty `section_key`, `path`, and `public_path`.
- Root audio assets should correspond to section keys, but the first implementation can report this as an error only when a root audio entry is malformed. Cross-reference mismatch can be a future stricter check if needed.

Visual assets:

- Reuse `inspect_visual_asset_readiness(props, props_path)` from `synccut.visual_assets`.
- Count target visual scenes, prepared target visuals, missing target visuals, and unsupported target visuals.
- Missing target visuals become warnings because `AI_VIDEO` and `B_ROLL` fallback placeholders can render.
- Unsupported target visuals become errors because a malformed prepared public path indicates bad props.

Warnings:

- Carry root `warnings` strings from `props["warnings"]` into preflight as warnings only.
- Non-string warning entries are structural errors because the report cannot display them consistently.

## What Preflight Does Not Check By Default

The first version must not:

- Check whether `remotion/public/audio/*.mp3` files exist.
- Check whether `remotion/public/visuals/*` files exist.
- Open, decode, probe, trim, normalize, or transcode audio or video.
- Invoke Remotion, Node, npm, Chrome, Studio, or render scripts.
- Call ffmpeg directly.
- Generate AI video.
- Download B-roll.
- Fetch, scrape, or call external media APIs.
- Modify `remotion/props.json`.
- Copy assets.
- Parse DOCX.
- Add GUI or web app behavior.

Filesystem verification can be added later as an explicit option such as `--verify-files --public-dir remotion/public`. Do not add that option in this phase.

## Status Levels

The preflight summary should have one of three statuses:

`ok` means there are no warnings and no errors.

`warning` means there are one or more warnings and no errors. This includes clean exported props with missing optional AI/B-roll visuals but prepared audio.

`error` means there is one or more error. Missing audio public paths, unsupported visual public paths, and structural invalid props should produce this status.

For CLI exit behavior, use exit code 0 for `ok` and `warning`, and exit code 1 for `error` or expected load failures such as malformed JSON. The report should still print before exiting 1 when the JSON can be loaded and summarized.

## Summary Fields

The text and JSON output should include these summary values:

- `status`
- `scenes`
- `sections`
- `duration_sec`
- `duration_frames`
- `fps`
- `audio_prepared`
- `audio_missing_public_path`
- `visual_target_scenes`
- `visual_prepared`
- `visual_missing`
- `visual_unsupported`
- `warnings`
- `errors`

Define `audio_prepared` as the number of sections whose `section.audio.public_path` is a non-empty string. This matches the Remotion rendering strategy, which mounts one audio track per section.

Define `audio_missing_public_path` as the number of missing public path problems across section audio entries and root `assets.audio` entries. A fully prepared current sample should report `audio_prepared: 7` and `audio_missing_public_path: 0`.

Use `duration_sec` from `metadata.duration_sec` when it is numeric. If it is absent or invalid, derive a display value from `composition.duration_frames / composition.fps` only when both composition values are valid, and still record a warning or error for the invalid metadata field according to the structural rule that failed.

## Proposed Text Output

The default output should be stable, concise, and line-oriented:

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

If there are no warnings, print:

    Warnings:
    none

If there are no errors, print:

    Errors:
    none

Issue lines should use this shape:

    <level> <code> <message>

Use fixed lowercase levels `warning` and `error`. Keep code strings stable so tests can assert them. Good codes include `props_warning`, `visual_missing`, `visual_unsupported`, `missing_audio_public_path`, `invalid_composition`, `invalid_scene_timing`, and `invalid_section_timing`.

## JSON Output

Add a simple `--json` option:

    .venv/bin/synccut preflight remotion/props.json --json

The JSON output should be deterministic, two-space indented, and have a trailing newline. Use this shape:

    {
      "path": "remotion/props.json",
      "status": "warning",
      "scenes": 33,
      "sections": 7,
      "duration_sec": 752.79,
      "duration_frames": 22584,
      "fps": 30,
      "audio_prepared": 7,
      "audio_missing_public_path": 0,
      "visual_target_scenes": 17,
      "visual_prepared": 0,
      "visual_missing": 17,
      "visual_unsupported": 0,
      "warnings": [
        {
          "level": "warning",
          "code": "visual_missing",
          "message": "scene_001 AI_VIDEO missing visual asset; placeholder will render"
        }
      ],
      "errors": []
    }

The JSON option must not change classification rules or exit code behavior.

## Helper and Data Model Design

Create `synccut/preflight.py`. Keep the implementation pure and testable. Use standard-library dataclasses and pathlib.

Define:

    @dataclass(frozen=True)
    class PreflightIssue:
        level: str
        code: str
        message: str

    @dataclass(frozen=True)
    class PreflightSummary:
        props_path: Path
        status: str
        scenes: int
        sections: int
        duration_sec: float | None
        duration_frames: int | None
        fps: int | None
        audio_prepared: int
        audio_missing_public_path: int
        visual_target_scenes: int
        visual_prepared: int
        visual_missing: int
        visual_unsupported: int
        warnings: list[PreflightIssue]
        errors: list[PreflightIssue]

Add public helper functions:

    def inspect_preflight(props: dict[str, Any], props_path: Path) -> PreflightSummary

    def inspect_preflight_file(props_path: Path) -> PreflightSummary

    def format_preflight(summary: PreflightSummary) -> str

    def preflight_to_dict(summary: PreflightSummary) -> dict[str, Any]

For loading JSON, reuse `load_remotion_props` from `synccut.remotion_assets` or create an internal wrapper that calls it. The audio helper name is not ideal for a general preflight module, but it already loads a Remotion props JSON object and raises `SyncCutError` with stable messages.

For visual readiness, call `inspect_visual_asset_readiness(props, props_path)` from `synccut.visual_assets` on the already loaded props. Catch `SyncCutError` from that helper and convert it to preflight structural errors only if doing so preserves a useful report. If the props are too malformed to identify scenes safely, it is acceptable for `inspect_preflight_file` to raise `SyncCutError` and let the CLI print `Error: ...`.

Private helpers should validate JSON values without throwing raw `KeyError` or `TypeError`. Add small local helpers for object, array, non-empty string, positive integer, non-negative integer, and number checks as needed. Do not import Remotion TypeScript code or run Node.

## CLI Behavior

Update `synccut/cli.py` in Milestone 2 with:

    @app.command("preflight")
    def preflight_cmd(
        props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
        json_output: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON.")] = False,
    ) -> None:
        ...

The command should:

- Call `inspect_preflight_file(props_json)`.
- Print `json.dumps(preflight_to_dict(summary), indent=2)` when `--json` is set.
- Print `format_preflight(summary)` by default.
- Catch `SyncCutError`, print `Error: <message>` to stderr, exit code 1, and show no Python traceback.
- Exit code 1 when `summary.status == "error"`.
- Exit code 0 when `summary.status` is `ok` or `warning`.
- Never write props or generated artifacts.

Do not change existing command behavior for `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, or `inspect-visual-assets`.

## Tests to Write

Add `tests/test_preflight.py` for pure helper behavior. Cover:

- Fully prepared audio with no visual assets reports status `warning`, visual missing warnings, no errors.
- Prepared section audio is counted by section.
- Missing `sections[].audio.public_path` is an error.
- Missing root `assets.audio[].public_path` is an error.
- Scene audio may remain path-only when section audio is prepared and should not add an error.
- Missing AI/B-roll visual assets are warnings.
- Prepared visual assets produce no visual warning.
- Unsupported visual public paths produce errors.
- Root props warnings are carried as warnings.
- Missing or malformed `composition` produces errors.
- Non-positive `composition.fps` and `composition.duration_frames` produce errors.
- Missing `scenes` or non-array `scenes` fails clearly.
- Missing `sections` or non-array `sections` fails clearly.
- Negative scene or section frames produce errors.
- Scene or section `end_frame` beyond composition duration produces errors.
- Scene or section `duration_frames` inconsistent with `end_frame - start_frame` produces errors.
- Metadata scene and section count mismatches produce errors.
- Text output is stable.
- JSON dictionary output is deterministic.
- File helper does not modify props file.

Update `tests/test_cli.py` in Milestone 2. Cover:

- `synccut preflight props.json` success with warning status exits 0 and prints stable text.
- `synccut preflight props.json --json` prints parseable JSON with expected summary and issue arrays.
- Error status exits non-zero after printing a report.
- Malformed props returns non-zero with `Error:` and no traceback.
- Command is read-only by comparing props file contents before and after.
- Existing CLI tests still pass.

Use tiny synthetic props fixtures. Do not rely on large media files, Remotion, npm, Chrome, or actual public asset files.

## Plan of Work

Milestone 1 adds the pure preflight helper module. Create `synccut/preflight.py`, define the dataclasses and helper functions, implement props-only structural checks, audio readiness checks, visual readiness integration, root warning carryover, text formatting, JSON conversion, and focused pure tests in `tests/test_preflight.py`. At the end of this milestone, `.venv/bin/python -m pytest` should pass, and no CLI command should exist yet.

Milestone 2 wires the Typer CLI command. Update `synccut/cli.py` to import and call the preflight helpers. Add CLI tests in `tests/test_cli.py` for text output, JSON output, error exit behavior, malformed props, and read-only behavior. At the end of this milestone, `.venv/bin/python -m pytest` should pass, and the command should be usable from the repository root.

Milestone 3 validates with real generated props. Regenerate `timeline.json`, validate it, export `remotion/props.json`, prepare audio assets, and run both text and JSON preflight. The expected clean current sample should have 33 scenes, 7 sections, prepared audio count 7, audio missing public path count 0, 17 target visual scenes, visual prepared 0, visual missing 17, visual unsupported 0, at least one root warning from the known `07_CONCLUSION` gap, status `warning`, and no errors. Run the full pytest suite and Remotion typecheck to prove no Python or Remotion regressions.

## Concrete Steps

From the repository root, inspect status before implementation:

    git status --short

Milestone 1 implementation:

    # edit synccut/preflight.py and tests/test_preflight.py
    .venv/bin/python -m pytest

Milestone 2 implementation:

    # edit synccut/cli.py and tests/test_cli.py
    .venv/bin/python -m pytest

Milestone 3 real-data validation:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --json
    .venv/bin/python -m pytest

Then run Remotion typecheck:

    cd remotion
    npm run typecheck
    cd ..

Do not run Remotion render scripts from Python. Do not add preflight commands that run npm.

## Validation and Acceptance

Acceptance for the completed phase:

- Running `.venv/bin/synccut preflight remotion/props.json` prints the stable text report and does not modify the file.
- Running `.venv/bin/synccut preflight remotion/props.json --json` prints parseable deterministic JSON and does not modify the file.
- Clean current sample props after audio preparation report status `warning`, because AI/B-roll local visuals are missing but placeholders can render.
- The same clean sample reports no errors when audio public paths are prepared.
- A props file missing section audio public paths reports status `error` and exits non-zero.
- A props file with malformed visual public paths reports status `error` and exits non-zero.
- `.venv/bin/python -m pytest` passes.
- From `remotion/`, `npm run typecheck` passes.
- Existing commands keep their behavior.

The expected real clean-props report summary after Milestone 3 should be close to:

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

The exact warning count may change if the generated props warnings change, but missing visual warnings should account for 17 warnings on the current sample.

## Idempotence and Recovery

The helper and CLI are read-only, so rerunning them should produce the same output for the same props file.

Generated validation artifacts are safe to recreate. `timeline.json`, `remotion/public/`, and `remotion/out/` are generated or ignored artifacts and should not be committed. If `remotion/props.json` is changed only because validation regenerated it, treat it as sample generated data and do not commit it unless the user explicitly approves.

If tests fail after adding the helper, fix the helper or tests before wiring the CLI. If the CLI fails on malformed props with a traceback, catch the relevant `SyncCutError` in `synccut/cli.py` and rerun tests. If real generated props produce an unexpected error, inspect whether the props file is stale or lacks `prepare-remotion-assets`; regenerate and prepare audio before changing code.

## Artifacts and Notes

Do not commit generated artifacts:

    timeline.json
    remotion/public/*
    remotion/out/*
    assets/visuals/*
    __pycache__/
    .pytest_cache/

Commit candidates after the phase should be:

    docs/plans/preflight-render-readiness.md
    synccut/preflight.py
    synccut/cli.py
    tests/test_preflight.py
    tests/test_cli.py

No Remotion rendering source files, package scripts, Python render wrappers, generated media, or final video artifacts should be part of this phase.

Plan creation note: this ExecPlan was added on 2026-05-12 after reading the requested repository documentation and inspecting the current exporter, audio asset helper, visual asset helper, CLI, tests, sample props, Remotion package scripts, and Remotion README. The purpose of this revision is to define the next phase only; implementation is intentionally left for later milestones.

## Interfaces and Dependencies

Use only the Python standard library, existing SyncCut validation helpers, and existing project modules. Do not add Python dependencies.

Use `SyncCutError` from `synccut.validators` for expected user-facing failures. Use `load_remotion_props` from `synccut.remotion_assets` or an equivalent wrapper for reading JSON. Reuse `inspect_visual_asset_readiness` from `synccut.visual_assets` rather than duplicating visual classification rules.

At the end of implementation, these public Python interfaces should exist:

    synccut.preflight.PreflightIssue
    synccut.preflight.PreflightSummary
    synccut.preflight.inspect_preflight(props: dict[str, Any], props_path: Path) -> PreflightSummary
    synccut.preflight.inspect_preflight_file(props_path: Path) -> PreflightSummary
    synccut.preflight.format_preflight(summary: PreflightSummary) -> str
    synccut.preflight.preflight_to_dict(summary: PreflightSummary) -> dict[str, Any]

At the end of CLI wiring, this public command should exist:

    .venv/bin/synccut preflight remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --json

The command must remain read-only and must not invoke Remotion, npm, Chrome, ffmpeg, AI/video APIs, media downloaders, or filesystem copy helpers.
