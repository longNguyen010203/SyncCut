# Add a visual asset readiness report command

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can now prepare local visual files for `AI_VIDEO` and `B_ROLL` scenes by copying user-supplied files into `remotion/public/visuals/` and annotating `remotion/props.json`. Remotion can render those local visual assets when `scene.visual.public_path` is valid, and it falls back to a metadata placeholder when the field is missing or unsupported. The missing operator tool is a read-only report that answers, before preview or later final assembly, how many AI video and B-roll scenes are prepared, missing, or unsupported.

After this phase, a user should be able to run:

    .venv/bin/synccut inspect-visual-assets remotion/props.json

and receive a stable text report listing readiness counts and one line per `AI_VIDEO` or `B_ROLL` scene. The command must not modify `remotion/props.json`, copy files, generate media, download B-roll, call AI/image/video APIs, call ffmpeg, probe/decode/transcode media, invoke Remotion, parse DOCX, add GUI or web app behavior, or change existing command behavior.

## Progress

- [x] (2026-05-11T15:24:08Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, and all prior phase ExecPlans through `docs/plans/remotion-visual-asset-strategy.md`.
- [x] (2026-05-11T15:24:08Z) Inspected `synccut/visual_assets.py`, `synccut/cli.py`, `tests/test_visual_assets.py`, `tests/test_cli.py`, `remotion/src/components/visualAsset.ts`, and `remotion/props.json`.
- [x] (2026-05-11T15:24:08Z) Created this ExecPlan for the read-only visual asset readiness report.
- [x] (2026-05-11T15:37:44Z) Implemented Milestone 1: added pure read-only readiness dataclasses, props classification, text formatting, JSON conversion, and focused helper tests.
- [x] (2026-05-11T15:42:27Z) Implemented Milestone 2: wired the `inspect-visual-assets` CLI command with default text output, `--json` output, and focused CLI tests.
- [x] (2026-05-11T15:53:11Z) Completed Milestone 3: validated `inspect-visual-assets` with fresh generated props, optional synthetic prepared assets, pytest, and Remotion typecheck.

## Surprises & Discoveries

- Observation: The current working tree was clean before this plan was created.
  Evidence: `git status --short` printed no changes after the Phase 9 final review cleanup.
- Observation: The current sample `remotion/props.json` is clean and contains no temporary synthetic visual public paths.
  Evidence: Inspecting `scene_001` and `scene_003` showed only `type`, `prompt`, and `data` inside `visual`, and root `assets.visuals` was `[]`.
- Observation: The TypeScript Remotion helper and Python visual asset preparation helper already share the same supported extension set.
  Evidence: `remotion/src/components/visualAsset.ts` accepts `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, and `.mov`; `synccut/visual_assets.py` uses the same set in `SUPPORTED_VISUAL_EXTENSIONS`.
- Observation: Existing visual asset preparation already centralizes Remotion props loading and target scene selection.
  Evidence: `synccut/visual_assets.py` has `load_visual_props(path)` and `_target_scenes(props, props_path)`, and the helper targets only `AI_VIDEO` and `B_ROLL` scenes.
- Observation: Milestone 1 did not need CLI or Remotion changes.
  Evidence: Only `synccut/visual_assets.py`, `tests/test_visual_assets.py`, and this plan were edited. `synccut/cli.py`, Remotion files, package scripts, and generated props were not changed.
- Observation: The file-level readiness helper is read-only.
  Evidence: The new test `test_file_helper_does_not_modify_props_file` writes formatted props, calls `inspect_visual_asset_readiness_file`, and asserts the file contents are unchanged.
- Observation: The Typer CLI accepts `json_output` for the `--json` option name without exposing that internal Python variable name to users.
  Evidence: The test `test_inspect_visual_assets_cli_json_prints_parseable_counts_and_items` invokes `inspect-visual-assets ... --json` and parses the output successfully.
- Observation: Milestone 2 did not require changes to readiness helper behavior.
  Evidence: Only `synccut/cli.py`, `tests/test_cli.py`, and this plan were edited for Milestone 2; `synccut/visual_assets.py`, Remotion files, props, and generated assets were not changed.
- Observation: Clean generated props report all target visual assets as missing.
  Evidence: After fresh `export-remotion` and `prepare-remotion-assets`, `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.
- Observation: Synthetic preparation changes readiness exactly as expected and is easy to clean up.
  Evidence: After generating local PNGs for `scene_001` and `scene_003` and running `prepare-visual-assets`, `inspect-visual-assets` reported `prepared: 2`, `missing: 15`, and `unsupported: 0`. Rerunning `export-remotion` and `prepare-remotion-assets` restored clean props with `prepared: 0`, `missing: 17`, and `assets.visuals: []`.

## Decision Log

- Decision: Implement the readiness report as read-only functions in `synccut/visual_assets.py`.
  Rationale: Visual asset preparation and visual asset readiness share the same props shape, supported visual types, and supported public path rules. Adding read-only functions to the same module keeps the behavior discoverable without changing the existing preparation command.
  Date/Author: 2026-05-11 / Codex
- Decision: Base the first report on props fields only, without filesystem checks.
  Rationale: The user asked for a lightweight readiness report from Remotion props. Checking disk existence would make results depend on the local checkout, public directory, and prepared files, and is better as a future explicit `--verify-files` option.
  Date/Author: 2026-05-11 / Codex
- Decision: Include a simple `--json` option in the implementation plan.
  Rationale: The summary and item data are small and already structured. A JSON mode is easy to test, makes the report useful for future automation, and does not require changing the default human-readable output.
  Date/Author: 2026-05-11 / Codex
- Decision: Treat `asset_status: "prepared"` plus a valid non-empty public path as prepared.
  Rationale: A status field alone is not enough for Remotion rendering; the component needs a safe `visual.public_path`. Requiring both prevents false-ready reports.
  Date/Author: 2026-05-11 / Codex
- Decision: Preserve the original string value in report items even when a public path is unsupported.
  Rationale: Operators need to see the malformed value that caused the unsupported classification, for example `assets/scene_002.gif`. Non-string or absent values still display as `-` in text output and `null` in JSON output.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested project documents and inspecting the current visual asset code, CLI, tests, Remotion path helper, and generated props. No source code, tests, props, generated assets, package scripts, or command behavior have been changed yet for this phase.

Milestone 1 is complete. `synccut/visual_assets.py` now has `VisualAssetReadinessItem` and `VisualAssetReadinessSummary` dataclasses plus pure read-only helpers: `inspect_visual_asset_readiness`, `inspect_visual_asset_readiness_file`, `format_visual_asset_readiness`, `visual_asset_readiness_to_dict`, and `classify_visual_public_path`. The helpers inspect only `AI_VIDEO` and `B_ROLL` scenes, preserve props scene order, ignore root `assets.visuals` for readiness, classify safe public paths under `visuals/` with supported image/video extensions, treat `prepared` without a valid public path as unsupported, and do not check filesystem existence.

Milestone 1 tests passed. `tests/test_visual_assets.py` now covers clean missing props, prepared classification, prepared-without-path unsupported classification, explicit unsupported status, public paths outside `visuals/`, `..` paths, unsupported `.gif` extension, case-insensitive supported extensions, ignored non-target visual types, scene order preservation, ignored root `assets.visuals`, stable text output, zero-target text output, deterministic JSON dictionary output, malformed missing `scenes` errors, and file-helper read-only behavior. From the repository root, `.venv/bin/python -m pytest` collected 144 tests and all 144 passed. No CLI command, `--json` CLI option, filesystem verification, asset copying, Remotion invocation, AI video generation, B-roll download, ffmpeg, media probing/transcoding, GUI, or web app behavior was added.

Milestone 2 is complete. `synccut/cli.py` now exposes `synccut inspect-visual-assets remotion/props.json` and `synccut inspect-visual-assets remotion/props.json --json`. The command is thin: it calls `inspect_visual_asset_readiness_file`, catches `SyncCutError` as `Error: ...` with exit code 1, prints `format_visual_asset_readiness(summary)` by default, and prints `json.dumps(visual_asset_readiness_to_dict(summary), indent=2)` for `--json`. It does not write props, copy assets, invoke Remotion, or perform filesystem verification.

Milestone 2 tests passed. `tests/test_cli.py` now covers stable text output, parseable JSON output with expected counts and items, malformed props failures with `Error:` and no traceback, and read-only behavior by comparing file contents before and after the CLI invocation. From the repository root, `.venv/bin/python -m pytest` collected 148 tests and all 148 passed. No `--verify-files`, `--public-dir`, asset copying, Remotion invocation, AI generation, B-roll download, ffmpeg, media probing/transcoding, GUI, or web app behavior was added.

Milestone 3 is complete. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Clean-props readiness validation passed. `.venv/bin/synccut inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Item rows included only `AI_VIDEO` and `B_ROLL` scenes in props order: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`. `.venv/bin/synccut inspect-visual-assets remotion/props.json --json` returned parseable JSON with the same counts and 17 item objects with `public_path: null`.

Optional synthetic prepared validation was performed and cleaned up. Two local generated PNGs were written under `assets/visuals/` for `scene_001` and `scene_003`. Running `.venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` reported `visual_copied: 0`, `visual_reused: 0`, `visual_overwritten: 2`, `visual_missing: 15`, `visual_assets: 2`, and `public_dir: remotion/public`; the overwrite count occurred because earlier ignored validation artifacts already existed under `remotion/public/visuals/`. Running `inspect-visual-assets` afterward reported `prepared: 2`, `missing: 15`, and `unsupported: 0`, with `scene_001` and `scene_003` prepared. Clean props were then regenerated with `export-remotion` and `prepare-remotion-assets`; a final readiness check again reported `prepared: 0`, `missing: 17`, `unsupported: 0`, and `assets.visuals: []`.

Final validation passed. From the repository root, `.venv/bin/python -m pytest` collected 148 tests and all 148 passed. From `remotion/`, `npm run typecheck` completed successfully. `git status --short --ignored` showed source/test/plan changes plus ignored generated artifacts: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.

Final generated artifact and commit policy: do not commit `timeline.json`, `assets/visuals/*`, `remotion/public/*`, `remotion/out/*`, `.pytest_cache/`, or `__pycache__/`. Do not commit `remotion/props.json` if it only changed due generated validation; after cleanup it contains no temporary visual public paths. Commit candidates for this phase are `docs/plans/visual-asset-readiness-report.md`, `synccut/visual_assets.py`, `synccut/cli.py`, `tests/test_visual_assets.py`, and `tests/test_cli.py`.

Phase 10 outcome: SyncCut now has a read-only visual asset readiness report for `AI_VIDEO` and `B_ROLL` scenes. The command reports stable text by default, JSON with `--json`, preserves scene order, relies on scene-level props fields, and does not copy assets, verify files, invoke Remotion, generate or download media, call ffmpeg, probe/transcode media, render the final MP4, or add GUI/web app behavior.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ Typer CLI project. The Remotion project lives under `remotion/`, but this phase is a Python CLI inspection phase and should not edit Remotion rendering code unless a clear bug is discovered.

The existing Python commands relevant to this phase are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

`export-remotion` creates `remotion/props.json`. `prepare-remotion-assets` copies section audio and adds audio public paths. `prepare-visual-assets` copies local visual files for `AI_VIDEO` and `B_ROLL` scenes and adds visual readiness fields. The new command for this phase is:

    .venv/bin/synccut inspect-visual-assets remotion/props.json

The existing files most relevant to implementation are:

    synccut/visual_assets.py
    synccut/cli.py
    tests/test_visual_assets.py
    tests/test_cli.py
    remotion/src/components/visualAsset.ts
    remotion/props.json

Important terms used in this plan:

A visual asset is a local image or video file intended to stand in for an `AI_VIDEO` or `B_ROLL` scene. It is not generated or downloaded by this phase.

A public path is a string relative to `remotion/public/`, such as `visuals/scene_001.png`. Remotion components pass that string to `staticFile()` in React. The readiness report should inspect this string but should not try to load or render it.

Readiness means whether the props fields indicate the scene has a renderable local visual path. Readiness is not proof that the file exists on disk in this first implementation.

## Current Visual Asset Props Fields

The current Remotion props shape for a visual scene includes:

    {
      "id": "scene_001",
      "visual_type": "AI_VIDEO",
      "visual": {
        "type": "AI_VIDEO",
        "prompt": "Extreme close-up of a silicon wafer...",
        "data": null,
        "public_path": "visuals/scene_001.png",
        "asset_status": "prepared",
        "asset_source": "local"
      }
    }

The fields are:

`visual.public_path`, an optional string that should point under `visuals/` and have a supported image or video extension.

`visual.asset_status`, an optional string written by `prepare-visual-assets`. Known values are `prepared`, `missing`, and `unsupported`.

`visual.asset_source`, an optional string. The current local workflow uses `local`.

`assets.visuals`, a root-level audit array written by `prepare-visual-assets` for prepared assets. Each entry contains `scene_id`, `visual_type`, source `path`, `public_path`, `asset_status`, and `asset_source`. Remotion rendering should still use the scene-level `visual.public_path`, not this audit array.

The clean sample `remotion/props.json` generated by `export-remotion` currently has no visual public paths and `assets.visuals: []`.

## Inspected Scene Types

Inspect only scenes whose `visual_type` is:

- `AI_VIDEO`
- `B_ROLL`

Ignore all other visual types for readiness counts and item rows. `COMPARISON_CARD`, `TABLE`, `CHART`, `TIMELINE`, and `SHARE_BREAKDOWN` are data-driven Remotion components and do not need local AI/B-roll media files.

The report should preserve the scene order in `props["scenes"]`. Do not sort by id or visual type because the existing props order follows timeline order.

## Readiness Classification Rules

A scene is `prepared` when all of these are true:

- `scene.visual.asset_status` equals `"prepared"`
- `scene.visual.public_path` is a non-empty string
- the public path starts with `visuals/`
- the public path does not contain `..`
- the public path has one of the supported extensions, case-insensitive: `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, or `.mov`

A scene is `unsupported` when either of these is true:

- `scene.visual.asset_status` equals `"unsupported"`
- `scene.visual.public_path` exists but is malformed, outside `visuals/`, contains `..`, or has an unsupported extension

A scene is `missing` otherwise. This includes clean exported props with no `visual.public_path`, and props where `asset_status` is `"missing"`.

This design deliberately treats `asset_status: "prepared"` without a valid public path as `unsupported`, not prepared. The goal is to report whether Remotion has enough safe props data to render a local asset.

## Filesystem Checks

Do not check actual file existence in the first implementation. The default report should be based on props fields only.

A future option could be:

    .venv/bin/synccut inspect-visual-assets remotion/props.json --public-dir remotion/public --verify-files

That future mode could verify that each prepared public path resolves to an existing file under `remotion/public/`. It is intentionally out of scope for the first implementation because it adds local filesystem assumptions and extra failure modes. Do not add `--public-dir` or `--verify-files` unless the user explicitly asks in a later milestone.

## Proposed Text Output

The default output should be concise, stable, and testable. Use this shape:

    Visual assets: remotion/props.json
    target_scenes: 17
    prepared: 2
    missing: 15
    unsupported: 0

    scene_001 AI_VIDEO prepared visuals/scene_001.png
    scene_003 B_ROLL prepared visuals/scene_003.png
    scene_004 B_ROLL missing -
    scene_006 AI_VIDEO unsupported assets/scene_006.gif

The item columns are:

- scene id
- visual type
- readiness status
- public path, or `-` when absent

Use plain spaces, not tables with dynamic alignment, so tests can assert exact lines without terminal-width concerns. Keep one blank line between summary counts and item rows. If there are zero target scenes, print summary counts and no item rows.

## Proposed JSON Output

Add `--json` if it stays simple. The JSON output should be deterministic, two-space indented, and should not include fields whose values are derived from local filesystem checks. Example:

    {
      "path": "remotion/props.json",
      "target_scenes": 17,
      "prepared": 2,
      "missing": 15,
      "unsupported": 0,
      "items": [
        {
          "scene_id": "scene_001",
          "visual_type": "AI_VIDEO",
          "status": "prepared",
          "public_path": "visuals/scene_001.png"
        }
      ]
    }

Do not name the option `--format` unless there is a concrete need for more formats. A boolean `--json` keeps CLI behavior small and easy to test.

## Helper and Data Model Design

Extend `synccut/visual_assets.py` with read-only dataclasses:

    @dataclass(frozen=True)
    class VisualAssetReadinessItem:
        scene_id: str
        visual_type: str
        status: str
        public_path: str | None

    @dataclass(frozen=True)
    class VisualAssetReadinessSummary:
        props_path: Path
        items: list[VisualAssetReadinessItem]
        prepared: int
        missing: int
        unsupported: int

Use status strings `"prepared"`, `"missing"`, and `"unsupported"`. A string literal type is optional; dataclasses are enough if tests cover values.

Add helper functions:

    def inspect_visual_asset_readiness(
        props: dict[str, Any],
        props_path: Path,
    ) -> VisualAssetReadinessSummary:
        ...

    def inspect_visual_asset_readiness_file(
        props_path: Path,
    ) -> VisualAssetReadinessSummary:
        ...

    def format_visual_asset_readiness(summary: VisualAssetReadinessSummary) -> str:
        ...

    def visual_asset_readiness_to_dict(summary: VisualAssetReadinessSummary) -> dict[str, Any]:
        ...

The file helper should use the existing `load_visual_props(path)` function. The inspection helper should validate just enough structure to avoid raw `KeyError` or `TypeError`. Reuse `require_mapping` and `require_non_empty_string` where useful. If `props["scenes"]` is missing or not an array, raise `SyncCutError` with a clear message matching the style already used by `prepare-visual-assets`.

Add a private helper for public path validation that mirrors `remotion/src/components/visualAsset.ts`:

    def classify_visual_public_path(value: Any) -> str | None:
        ...

This should return the normalized public path string when valid and `None` otherwise. It should reject non-strings, empty strings, paths not starting with `visuals/`, paths containing `..`, and unsupported extensions. It does not need to return image/video kind for readiness, but tests should prove the same extensions are accepted.

## CLI Behavior

Add a Typer command in `synccut/cli.py`:

    @app.command("inspect-visual-assets")
    def inspect_visual_assets_cmd(
        props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
        json_output: Annotated[bool, typer.Option("--json", help="Print machine-readable JSON.")] = False,
    ) -> None:
        ...

The CLI should be thin:

- call `inspect_visual_asset_readiness_file(props_json)`
- catch `SyncCutError`
- print `Error: ...` and exit 1 for expected failures
- print either `format_visual_asset_readiness(summary)` or `json.dumps(visual_asset_readiness_to_dict(summary), indent=2) + "\n"`

The command must not write to `props_json`, `remotion/public`, `timeline.json`, or any other file.

## Tests to Write

Add helper tests in `tests/test_visual_assets.py`:

- clean props with one `AI_VIDEO` and one `B_ROLL` scene and no public paths reports both as missing
- prepared scene requires `asset_status: "prepared"` plus valid `visual.public_path`
- `asset_status: "prepared"` with missing public path reports unsupported
- `asset_status: "unsupported"` reports unsupported
- public path outside `visuals/` reports unsupported
- public path containing `..` reports unsupported
- unsupported extension such as `.gif` reports unsupported
- supported extensions are accepted case-insensitively
- non-target visual types are ignored
- scene order is preserved
- `assets.visuals` does not affect scene readiness when scene-level fields are missing
- formatted text output is stable
- JSON dictionary output is deterministic
- malformed props missing `scenes` fails clearly
- file helper does not modify the props file

Add CLI tests in `tests/test_cli.py`:

- `inspect-visual-assets` success prints the stable text summary and item rows
- `inspect-visual-assets --json` prints parseable JSON with expected counts and items
- malformed props returns non-zero with `Error:` and no traceback
- command is read-only by comparing the props file contents before and after invocation

Use small synthetic props dictionaries and temporary files. Do not rely on real media files.

## Plan of Work

Milestone 1 adds pure read-only readiness helpers. Implement dataclasses, classification, summary construction, text formatting, and JSON conversion in `synccut/visual_assets.py`. Add focused unit tests in `tests/test_visual_assets.py`. Run `.venv/bin/python -m pytest`.

Milestone 2 wires the CLI command. Update `synccut/cli.py` with the thin `inspect-visual-assets` command, add CLI tests in `tests/test_cli.py`, and rerun `.venv/bin/python -m pytest`.

Milestone 3 validates with real generated props. Regenerate `timeline.json`, `remotion/props.json`, and audio assets from examples. Run `inspect-visual-assets` on clean props and expect all target scenes to be missing. Optionally run `prepare-visual-assets` with local synthetic assets and then run `inspect-visual-assets` again to prove prepared counts change, but do not commit those generated props or media. Finish with `.venv/bin/python -m pytest` and `cd remotion && npm run typecheck` because the phase should not break the Remotion project.

## Milestone 1: Pure Readiness Helpers

At the end of this milestone, Python tests should be able to classify a Remotion props dictionary without touching the filesystem. No CLI command is needed yet.

Edit only:

    synccut/visual_assets.py
    tests/test_visual_assets.py
    docs/plans/visual-asset-readiness-report.md

Validation:

    .venv/bin/python -m pytest

Acceptance: helper tests pass, clean props are reported as missing, prepared props require a safe public path, malformed paths report unsupported, non-target scenes are ignored, and formatting functions produce stable output.

## Milestone 2: CLI Wiring

At the end of this milestone, users can run:

    .venv/bin/synccut inspect-visual-assets remotion/props.json

and optionally:

    .venv/bin/synccut inspect-visual-assets remotion/props.json --json

Edit only:

    synccut/cli.py
    tests/test_cli.py
    docs/plans/visual-asset-readiness-report.md

Validation:

    .venv/bin/python -m pytest

Acceptance: the CLI prints stable text by default, prints deterministic JSON with `--json`, handles malformed props with `Error:` and no traceback, and leaves the props file unchanged.

## Milestone 3: Real Props Validation

At the end of this milestone, the command should be validated against real generated example props.

Run from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut inspect-visual-assets remotion/props.json --json

Expected clean-props result: target scene count equals the number of `AI_VIDEO` plus `B_ROLL` scenes in props, prepared is `0`, unsupported is `0`, and missing equals target scene count. At the time this plan was written, the sample props had 6 `AI_VIDEO` scenes and 11 `B_ROLL` scenes, so the expected target count is 17.

If validating after local synthetic visual preparation, record both before and after summaries. Do not commit generated `assets/visuals/*`, `remotion/public/visuals/*`, `remotion/out/*`, `timeline.json`, or `remotion/props.json` containing temporary local visual paths.

Final validation:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck

## Validation and Acceptance

This phase is accepted when:

- `inspect-visual-assets` is read-only and does not modify `remotion/props.json`
- only `AI_VIDEO` and `B_ROLL` scenes are inspected
- prepared, missing, and unsupported counts match the classification rules
- unsafe or unsupported public paths are reported as unsupported
- missing assets are reported as missing, not as command failures
- text output is stable and human-readable
- `--json` output is valid JSON and stable
- existing commands keep their behavior
- `.venv/bin/python -m pytest` passes
- `cd remotion && npm run typecheck` passes during final validation

## Idempotence and Recovery

The command is read-only and should be safe to run repeatedly. If it reports all visual assets as missing after a clean export, that is expected because `export-remotion` does not create visual public paths. To change readiness, run `prepare-visual-assets` separately with local media files, then rerun `inspect-visual-assets`.

If a test or validation run leaves temporary visual public paths in `remotion/props.json`, regenerate clean props with:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not use destructive git commands for cleanup unless explicitly requested.

## Generated Artifacts and Commit Policy

This phase should not require generated media. If real-props validation regenerates data, do not commit:

- `timeline.json`
- `assets/visuals/*`
- `remotion/public/visuals/*`
- `remotion/public/audio/*.mp3`
- `remotion/out/*`
- `.pytest_cache/`
- `__pycache__/`

Commit candidates for this phase should be limited to:

- `docs/plans/visual-asset-readiness-report.md`
- `synccut/visual_assets.py`
- `synccut/cli.py`
- `tests/test_visual_assets.py`
- `tests/test_cli.py`

Do not commit `remotion/props.json` if it only changed because of temporary local visual readiness validation.

## Explicit Exclusions

This phase must not:

- copy visual assets
- generate AI video
- call image or video generation APIs
- download B-roll
- scrape or fetch external media
- call ffmpeg directly
- probe, decode, trim, transcode, or normalize media
- invoke Remotion from Python
- assemble the final full MP4
- parse DOCX
- add GUI or web app behavior
- change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, or `prepare-visual-assets` behavior unless a clear bug is found and recorded
- require local media files to exist for the default report

## Interfaces and Dependencies

Use only the Python standard library and existing project helpers. The likely imports are `dataclasses.dataclass`, `json`, `pathlib.Path`, and `typing.Any`. Reuse `SyncCutError`, `require_mapping`, and `require_non_empty_string` from `synccut.validators`.

Do not add package dependencies. Do not use Context7 for this internal SyncCut logic.

The implementation should keep CLI code in `synccut/cli.py` as presentation only. Classification, summarization, text formatting, and JSON conversion should live in `synccut/visual_assets.py` so tests can cover them without invoking Typer.

## Revision Notes

2026-05-11 / Codex: Initial ExecPlan created for a read-only `inspect-visual-assets` command after reading the required docs and inspecting the current visual asset preparation helper, CLI, tests, Remotion public path helper, and clean sample props.
