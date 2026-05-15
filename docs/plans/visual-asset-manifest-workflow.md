# Visual asset manifest workflow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, and validate the local visual asset manifest workflow from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can already export Remotion props, prepare optional local `AI_VIDEO` and `B_ROLL` visual assets, inspect prepared visual readiness, and run preflight checks. The remaining visual pipeline needs a local manifest command that turns the visual metadata already present in exported props into a clear human review document and a machine-readable input for future download providers.

After this phase, a user should be able to run a command like:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.md
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json

and answer:

- which scenes need local visual assets
- what filename stem or filename each scene should use
- which scenes are already prepared in props
- which scenes have local supported files waiting to be prepared
- which scenes are missing
- which scenes have unsupported or ambiguous local asset files
- what prompt, keyword seed, or visual description should be used by a later B-roll search/download provider

This phase is local manifest generation only. It must not call Pexels, Pixabay, AI media providers, ffmpeg, ffprobe, Remotion render commands, or any media probing/transcoding/normalization tool. It must not download, generate, copy, or prepare media. It must not mutate `remotion/props.json`.

## Progress

- [x] (2026-05-14T19:25:00+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, root `README.md`, prior visual readiness/preflight/CLI polish plans, `synccut/visual_assets.py`, `synccut/preflight.py`, `synccut/remotion_exporter.py`, `synccut/cli.py`, visual/preflight/CLI tests, `.gitignore`, and current `git status --short --ignored`.
- [x] (2026-05-14T19:25:00+07:00) Created this Phase 31 ExecPlan for a local visual asset manifest workflow.
- [x] (2026-05-14T19:42:00+07:00) Milestone 1: audited current visual asset preparation, readiness inspection, preflight behavior, exported props metadata, tests, and artifact policy without source changes.
- [x] (2026-05-14T19:55:00+07:00) Milestone 2: finalized visual manifest command design, output model, status vocabulary, local source-file inspection policy, idempotent write policy, and implementation/test scope.
- [x] (2026-05-14T20:20:00+07:00) Milestone 3: implemented `synccut visual-manifest`, local source-file manifest generation, Markdown/JSON outputs, idempotent write handling, and focused tests.
- [x] (2026-05-15T00:20:00+07:00) Milestone 4: validated `visual-manifest` against the current TSMC sample with Markdown and JSON outputs, dry-run, pytest, Remotion typecheck, cleanup, and props restore.
- [x] (2026-05-15T00:38:00+07:00) Milestone 5: completed README docs note, ignore decision, final pytest/typecheck, artifact review, and commit recommendation.

## Surprises & Discoveries

- Observation: The existing target visual scene set is already centralized.
  Evidence: `synccut/visual_assets.py` defines `TARGET_VISUAL_TYPES = {"AI_VIDEO", "B_ROLL"}`.
- Observation: Supported local visual extensions are already centralized and match the previous prepared visual workflow.
  Evidence: `synccut/visual_assets.py` defines `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp` as supported extensions.
- Observation: Existing `inspect-visual-assets` reports props readiness, not local source-file availability.
  Evidence: `inspect_visual_asset_readiness` classifies scene-level `visual.public_path` and `visual.asset_status` from props; it does not inspect `assets/visuals/`.
- Observation: `prepare-visual-assets` discovers source files by exact scene-id stem in the direct `assets_dir` children.
  Evidence: `_matching_supported_files(assets_dir, scene_id)` ignores subdirectories, requires `path.stem == scene_id`, and keeps only suffixes in `SUPPORTED_VISUAL_EXTENSIONS`.
- Observation: Missing local visual files are not errors during preparation.
  Evidence: `_prepare_scene_asset` returns `None` when no supported candidate exists; `_apply_visual_asset_metadata` removes `public_path`, sets `asset_status: "missing"`, and sets `asset_source: "local"`.
- Observation: Duplicate supported local files are fatal during preparation.
  Evidence: `_prepare_scene_asset` raises `SyncCutError("multiple supported visual assets for ...")` when more than one supported candidate matches the same scene id.
- Observation: Unsupported local suffixes are currently invisible to the preparation selector.
  Evidence: `_matching_supported_files` filters unsupported suffixes out, so a file like `scene_001.txt` makes the scene behave as missing; tests assert unsupported files are not copied or marked prepared.
- Observation: `prepare-visual-assets` mutates both public files and props, so it is intentionally out of scope for the manifest command.
  Evidence: `prepare_visual_assets_file` writes updated props JSON, `_copy_visual` copies into `out_dir / "visuals"`, and `_apply_visual_asset_metadata` updates scene visual fields plus root `assets.visuals`.
- Observation: `remotion/props.json` is the strongest Phase 31 input candidate.
  Evidence: `synccut/remotion_exporter.py` writes scene ids, section keys, section names, order, durations, frames, `visual_type`, and the full `visual` object including prompts/data into each scene.
- Observation: The current sample props contain 17 target visual scenes.
  Evidence: `rg '"visual_type": "(AI_VIDEO|B_ROLL)"' remotion/props.json` returned 17 matches.
- Observation: The current sample props are clean with respect to visual preparation.
  Evidence: Searching `remotion/props.json` for `asset_status`, `asset_source`, and visual public paths found only audio `public_path` entries; the visible target scene visual objects contain `type`, `prompt`, and `data` but no prepared visual fields.
- Observation: Exported scene visual metadata is sufficient for a manifest without schema changes.
  Evidence: `_map_scene` in `synccut/remotion_exporter.py` emits `id`, `scene_order`, `section`, `section_order`, `section_key`, `start_sec`, `end_sec`, `duration_sec`, `start_frame`, `end_frame`, `duration_frames`, `visual_type`, and a deepcopy of the original `visual` object.
- Observation: Prompt/search metadata is available as existing props text, but there is no separate normalized keyword field.
  Evidence: Target scenes in `remotion/props.json` contain `visual.prompt` strings and `visual.data`; B-roll/AI search terms would need to use existing prompt text or a future explicit field, not invented keywords in Phase 31.
- Observation: Preflight treats missing target visuals as warning-only when no blocking errors or file errors exist.
  Evidence: `inspect_preflight` converts missing visual readiness items into `warning visual_missing ... placeholder will render`; `format_preflight` adds a note that missing AI_VIDEO/B_ROLL visuals are warning-only when `errors` is empty and `file_errors` is zero.
- Observation: `inspect-visual-assets` already explains optional placeholders in human output.
  Evidence: `format_visual_asset_readiness` adds `Note: Missing AI_VIDEO/B_ROLL visuals are optional; Remotion will render placeholders unless visual assets are prepared.` when `missing > 0`.
- Observation: Current tests lock in the props-only readiness boundary.
  Evidence: `test_assets_visuals_does_not_affect_scene_readiness_when_scene_fields_are_missing` asserts root `assets.visuals` does not make a scene prepared if the scene-level visual fields are missing.
- Observation: The current repository already ignores generated and local media paths relevant to Phase 31.
  Evidence: `.gitignore` ignores `generated/`, `assets/visuals/`, `remotion/public/`, `remotion/out/`, `timeline.json`, `.venv/`, Remotion dependencies, and caches.
- Observation: The current visible working tree has no uncommitted Phase 30 source/test/doc files.
  Evidence: `git status --short --ignored` showed only `?? docs/plans/visual-asset-manifest-workflow.md` plus ignored generated/local paths. Phase 31 should still avoid reverting or conflating any unrelated user changes if they appear later.
- Observation: Props are sufficient for the first manifest's prompt/search seed, but not for curated downloader keywords.
  Evidence: Target scene visual objects contain `visual.prompt` strings and sometimes `visual.data`, but there is no separate normalized keyword or stock-search field. The first manifest should copy existing text only and leave curated query generation to Phase 32 or later.
- Observation: Keeping prepared readiness separate from local availability avoids a misleading "ready" state.
  Evidence: Remotion renders prepared media from scene-level `visual.public_path`; a local `assets/visuals/scene_001.mp4` file is only a source candidate until `prepare-visual-assets` annotates props and copies it into `remotion/public/visuals/`.
- Observation: `generated/` remains sufficient for validation manifest outputs.
  Evidence: `.gitignore` already contains `generated/`, so `generated/visual_manifest.md` and `generated/visual_manifest.json` need no new ignore rule.
- Observation: Milestone 3 implementation did not need schema, README, `.gitignore`, Remotion, or media changes.
  Evidence: Edits were limited to `synccut/visual_manifest.py`, `synccut/cli.py`, `tests/test_visual_manifest.py`, `tests/test_cli.py`, and this plan.
- Observation: The implemented command can use existing props directly without mutating them.
  Evidence: `write_visual_manifest_file` reads props through `load_visual_props`, builds a separate manifest model, and writes only the requested manifest output path unless `dry_run=True`.
- Observation: The local source-file inspection remains metadata-only.
  Evidence: `_inspect_local_asset` inspects direct child path names and suffixes under `assets_dir`; it does not read, copy, probe, transcode, or normalize media contents.
- Observation: The initial implementation matched the Milestone 2 design closely.
  Evidence: No deviations were needed for command name, options, status vocabulary, prompt/search seed policy, output formats, or write policy.
- Observation: The current sample has all 17 target visual source files present locally, but clean props remain unprepared.
  Evidence: Both Markdown and JSON `visual-manifest` runs reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, `local_found: 17`, `local_missing: 0`, `local_duplicate_supported: 0`, and `local_unsupported_only: 0`.
- Observation: The manifest output clearly exposes Phase 32 handoff data.
  Evidence: `generated/visual_manifest.json` included `schema_version: "0.1"`, source props, assets dir, summary counts, supported extensions, scene entries with expected filenames, `local_asset_path`, prompt, `search_query_seed`, and notes.
- Observation: The Markdown output is human-readable for the TSMC sample.
  Evidence: `generated/visual_manifest.md` included title, source/assets summary, counts, naming policy, supported extensions, and a table with scene ids, section keys, visual type, duration, prepared status, local asset status, expected stem, and prompt/search seed.
- Observation: Dry-run does not create the requested output.
  Evidence: `visual-manifest ... --out generated/visual_manifest_dryrun.md --dry-run` reported `status: would_create`, and `test ! -e generated/visual_manifest_dryrun.md` succeeded.
- Observation: Sample props regeneration modified `remotion/props.json` only as a validation artifact.
  Evidence: `git diff -- remotion/props.json` showed regenerated clean export differences, including removal of tracked audio `public_path` fields and the already-fixed conclusion timing warning. The file was restored after validation.
- Observation: Restoring generated props required elevated git access in this sandbox.
  Evidence: plain `git restore remotion/props.json` failed with `Unable to create ... .git/index.lock: Read-only file system`; the elevated retry succeeded.
- Observation: README needed a concise user-facing note for the new command.
  Evidence: The README already documented local visual assets and current inspect/prepare/preflight commands, but did not mention `visual-manifest`; Milestone 5 added a short command summary and local visual workflow note without documenting the full JSON schema.
- Observation: No `.gitignore` change was needed.
  Evidence: `.gitignore` already contains `generated/`, `assets/visuals/`, `remotion/public`, `remotion/out/`, `timeline.json`, `.venv`, dependency directories, and caches.
- Observation: Final validation passed without source changes after Milestone 4.
  Evidence: `.venv/bin/python -m pytest` passed with 267 tests and `cd remotion && npm run typecheck` passed.
- Observation: Final artifact status is limited to expected docs/source/test changes.
  Evidence: `git status --short --ignored` showed commit candidates `README.md`, `synccut/cli.py`, `tests/test_cli.py`, `docs/plans/visual-asset-manifest-workflow.md`, `synccut/visual_manifest.py`, and `tests/test_visual_manifest.py`; ignored/local paths remained under `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `__pycache__/`, and `timeline.json`.

## Decision Log

- Decision: Use `remotion/props.json` as the primary input for Phase 31.
  Rationale: Props contain render-oriented timing, section, visual prompt, scene order, and prepared public-path metadata. The existing visual readiness and preflight helpers already operate on props. A timeline input can be considered later only if a concrete user workflow needs it.
  Date/Author: 2026-05-14 / Codex
- Decision: Add a new command named `visual-manifest`.
  Rationale: The command is a reporting/planning command, not asset preparation. The name distinguishes it from `prepare-visual-assets` and `inspect-visual-assets` while matching the user's requested workflow.
  Date/Author: 2026-05-14 / Codex
- Decision: Support both Markdown and JSON outputs.
  Rationale: Markdown is useful for human asset review and assignment. JSON is the stable handoff format for Phase 32 download providers. Both can be produced deterministically from the same manifest model without changing schemas.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep Phase 31 read-only with respect to props and media.
  Rationale: Manifest generation should reveal what exists and what is missing. Copying, downloading, preparing, or rendering belongs to existing commands or later phases.
  Date/Author: 2026-05-14 / Codex
- Decision: Record local source-file availability separately from prepared props readiness.
  Rationale: A scene can be missing from props but have a valid local file under `assets/visuals/` that has not yet been prepared. The manifest should expose both facts without overloading the existing prepared/missing/unsupported readiness terms.
  Date/Author: 2026-05-14 / Codex
- Decision: Preserve `remotion/props.json` as the primary input after Milestone 1 audit.
  Rationale: Exported props are the only current single artifact with target scene identity, timing, section metadata, prompt/data metadata, and prepared visual fields. Using props avoids timeline schema changes and aligns with existing visual readiness and preflight commands.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep `visual-manifest` read-only and separate from preparation.
  Rationale: `prepare-visual-assets` copies files and mutates props, while Phase 31 is meant to explain the current state and produce a planning artifact. The manifest command must not copy, download, prepare, or render assets.
  Date/Author: 2026-05-14 / Codex
- Decision: Treat local source-file availability as a manifest concept, not as a replacement for prepared readiness.
  Rationale: Current render readiness depends on scene-level props public paths. Local files under `assets/visuals/` can be useful for planning and downloader avoidance, but they do not make Remotion prepared until the existing preparation command runs.
  Date/Author: 2026-05-14 / Codex
- Decision: Finalize the command as `synccut visual-manifest PROPS_JSON`.
  Rationale: The command is a local reporting/planning workflow for visual assets and should be distinct from `inspect-visual-assets` and `prepare-visual-assets`.
  Date/Author: 2026-05-14 / Codex
- Decision: Use these CLI options: `--assets-dir assets/visuals`, `--out`, `--format markdown|json`, `--dry-run`, and `--overwrite`.
  Rationale: This matches the existing asset layout, supports human and downloader outputs, and follows the safe write patterns already used by narration/audio generation commands.
  Date/Author: 2026-05-14 / Codex
- Decision: Default output path depends on format when `--out` is omitted.
  Rationale: `generated/visual_manifest.md` is the natural default for Markdown and `generated/visual_manifest.json` is the natural default for JSON. Both live under the ignored `generated/` directory.
  Date/Author: 2026-05-14 / Codex
- Decision: The manifest includes only `AI_VIDEO` and `B_ROLL` scene entries.
  Rationale: Those are the current local media-backed visual types. Data-driven scene types such as `TABLE`, `CHART`, `COMPARISON_CARD`, `SHARE_BREAKDOWN`, and `TIMELINE` do not need local media assets and should not clutter the scene table.
  Date/Author: 2026-05-14 / Codex
- Decision: Use `prepared_status` and `local_asset_status` as separate fields.
  Rationale: `prepared_status` describes render readiness from props, while `local_asset_status` describes unprepared source-file availability under `assets/visuals/`.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep prompt/search extraction deterministic.
  Rationale: Phase 31 must not use AI rewriting, web search, or external provider logic. `search_query_seed` should come from existing `visual.prompt` first, then existing description-like fields only if present.
  Date/Author: 2026-05-14 / Codex
- Decision: Implement a new `synccut/visual_manifest.py` module and reuse `synccut.visual_assets` constants and public readiness helpers.
  Rationale: The manifest command needs richer local source-file reporting and Markdown/JSON formatting than the existing readiness helper, but it should not duplicate target visual type and extension definitions.
  Date/Author: 2026-05-14 / Codex
- Decision: Add a concise README note for `visual-manifest`.
  Rationale: The command is user-facing and belongs in the local visual asset workflow. The README note keeps onboarding accurate without duplicating the JSON schema or implementation details.
  Date/Author: 2026-05-15 / Codex
- Decision: Leave `.gitignore` unchanged.
  Rationale: The new validation outputs live under `generated/`, which is already ignored. No new generated path outside the existing artifact policy was introduced.
  Date/Author: 2026-05-15 / Codex

## Outcomes & Retrospective

This plan has been created after inspecting the current visual asset readiness, preflight, Remotion export, CLI, tests, prior visual plans, and artifact ignore policy. No source code, tests, README files, generated props, media files, renderer files, schemas, downloads, or render outputs have been changed for Phase 31 yet.

Milestone 1 is complete. The audit confirmed that SyncCut's current visual asset workflow is split into two layers: `prepare-visual-assets` reads local files from `assets/visuals/`, copies exactly one supported file per target scene into `remotion/public/visuals/`, and mutates `remotion/props.json`; `inspect-visual-assets` and `preflight` inspect prepared props readiness and do not report unprepared local source-file availability. The target asset types are exactly `AI_VIDEO` and `B_ROLL`, and supported suffixes are `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`.

The sample `remotion/props.json` contains 17 target visual scenes with scene ids, section keys, section names, scene/section order, start/end/duration seconds, frame timing, `visual_type`, and `visual.prompt`/`visual.data`. It currently has clean audio public paths but no visual `asset_status`, `asset_source`, or visual `public_path` fields. There is prompt text available for search seed use, but no separate normalized keyword field.

The key Phase 31 gap is local source-file visibility. Existing readiness reports can say a scene is missing because props are not prepared, but they cannot say whether `assets/visuals/scene_001.mp4` already exists locally, whether there are duplicate supported candidates, or whether only unsupported local suffixes exist. The manifest should therefore report prepared props readiness and local source-file status as separate concepts.

Artifact review for Milestone 1 found only this Phase 31 plan as an untracked non-ignored file. Ignored/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`. No source, tests, README, `.gitignore`, generated visual manifest, media file, or `remotion/props.json` changes were made. The next step is Milestone 2: finalize the manifest command, field schema, output formats, overwrite/dry-run behavior, and tests before coding.

Milestone 2 is complete. The final design is a read-only `visual-manifest` command that reads `remotion/props.json`, optionally inspects direct child files under `assets/visuals/`, and writes either Markdown or JSON into `generated/`. It includes only `AI_VIDEO` and `B_ROLL` scenes in props order, reports props-level prepared readiness separately from local source-file availability, copies prompt/search seed text from existing props only, and uses an idempotent output policy: create missing outputs, reuse identical outputs, block differing outputs unless `--overwrite`, and write nothing for `--dry-run`.

The next step is Milestone 3: implement `synccut/visual_manifest.py`, wire `synccut/cli.py`, add focused unit/CLI tests, and update this plan with implementation evidence.

Milestone 3 is complete. `synccut/visual_manifest.py` now defines pure/testable manifest helpers and dataclasses, builds target scene entries from Remotion props, preserves props scene order, reuses `TARGET_VISUAL_TYPES`, `SUPPORTED_VISUAL_EXTENSIONS`, `classify_visual_public_path`, and `inspect_visual_asset_readiness`, inspects direct child local source files by scene-id stem, produces deterministic Markdown and JSON, and implements `dry_run`, no-overwrite blocking, identical-output reuse, and `--overwrite` replacement for the requested output file only.

`synccut/cli.py` now exposes `synccut visual-manifest PROPS_JSON` with `--assets-dir`, `--out`, `--format markdown|json`, `--dry-run`, and `--overwrite`. The command prints concise summary counts and a next-step hint, and uses the existing `Error: ...` CLI style for conflicts and validation failures.

`tests/test_visual_manifest.py` now covers target filtering, scene order, section/duration/visual fields, prompt/search seed extraction, deterministic expected naming, missing/found/duplicate/unsupported local source states, prepared props fields, Markdown output, JSON output, dry-run behavior, identical-output reuse, conflict blocking, and overwrite replacement. `tests/test_cli.py` now covers Markdown success output, JSON success output, dry-run output, and conflict output.

Validation passed: `.venv/bin/python -m pytest` collected 267 tests and all 267 passed. No generated visual manifest output was created in the repository root, no media/download/render work was performed, and `remotion/props.json` was not mutated. The next step is Milestone 4: validate the command against the real sample workflow and generated outputs under `generated/`.

Milestone 4 is complete. Validation summary:

- `.venv/bin/python -m pytest` passed with 267 tests.
- `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` succeeded with 7 sections, 33 scenes, `duration_sec: 752.79`, and `warnings: 0`.
- `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` succeeded with 33 scenes, 7 sections, 30 fps, 22584 frames, and `warnings: 0`.
- Markdown manifest generation succeeded at `generated/visual_manifest.md`.
- JSON manifest generation succeeded at `generated/visual_manifest.json`.
- Both manifest commands reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, `local_found: 17`, `local_missing: 0`, `local_duplicate_supported: 0`, and `local_unsupported_only: 0`.
- Manifest inspection confirmed expected stems such as `assets/visuals/scene_001`, supported extensions, prompt/search seed metadata from props, and JSON fields suitable for Phase 32 downloader input.
- Dry-run validation succeeded and did not create `generated/visual_manifest_dryrun.md`.
- `cd remotion && npm run typecheck` passed.
- Generated manifest outputs were removed with targeted cleanup. `generated/` was removed only because it was empty.
- `remotion/props.json` was restored after validation because sample props refresh was not approved. The first restore attempt hit sandbox index-lock restrictions; the elevated retry succeeded.
- `git status --short generated ... remotion/props.json timeline.json` and `git diff -- remotion/props.json` produced no output after cleanup/restore.

No `prepare-visual-assets` run, asset copy, media download, image/video generation, ffmpeg/ffprobe call, probing/transcoding/normalization, Remotion render, schema change, or props mutation remains from Milestone 4. The next step is Milestone 5: docs decision, final cleanup review, final validation, and commit recommendation.

Milestone 5 is complete. Final Phase 31 summary:

- `synccut visual-manifest` is implemented as a read-only local manifest workflow.
- Markdown and JSON outputs are supported.
- The command reports target `AI_VIDEO`/`B_ROLL` scenes, expected local naming, props prepared status, local source-file availability, supported/unsupported/duplicate local file states, durations, and prompt/search seed metadata.
- It does not download, generate, copy, prepare, probe, transcode, normalize, or render media.
- README now includes a concise `visual-manifest` note in the Python command summary and local visual asset workflow.
- `.gitignore` needed no changes because `generated/` was already ignored.
- Final `.venv/bin/python -m pytest` passed with 267 tests.
- Final Remotion typecheck passed with `tsc --noEmit`.
- Generated manifest outputs are absent.
- `remotion/props.json` is not modified.
- `timeline.json`, local visual media, public assets, render outputs, dependency directories, and caches remain ignored/generated/local-only artifacts.

Acceptance criteria status: complete. The local visual manifest workflow exists, supports Markdown and JSON, captures target visual scenes with prepared and local-source status, includes prompt/search metadata from props, avoids media generation/download/preparation/rendering, and is validated by tests and sample workflow evidence.

Final commit candidates:

    README.md
    synccut/cli.py
    synccut/visual_manifest.py
    tests/test_cli.py
    tests/test_visual_manifest.py
    docs/plans/visual-asset-manifest-workflow.md

Recommended commit message:

    Add visual asset manifest workflow

Next step: ask the user before starting Phase 32 B-roll downloader work.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python Typer CLI under `synccut/`; the Remotion app lives under `remotion/`.

Current relevant commands are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

`prepare-visual-assets` copies local files into `remotion/public/visuals/` and annotates `remotion/props.json`. `inspect-visual-assets` reports whether props already contain renderable prepared visual paths for `AI_VIDEO` and `B_ROLL` scenes. `preflight` reports full render readiness and treats missing optional visuals as warning-only when placeholders can render.

The new command in this plan should sit before `prepare-visual-assets` and before future downloader commands. It should inspect exported props plus local `assets/visuals/` source files and write a text or JSON manifest into `generated/`.

The relevant source files are:

    synccut/visual_assets.py
    synccut/preflight.py
    synccut/remotion_exporter.py
    synccut/cli.py
    tests/test_visual_assets.py
    tests/test_preflight.py
    tests/test_cli.py

Likely new files are:

    synccut/visual_manifest.py
    tests/test_visual_manifest.py

Generated and local-only paths must remain out of commits:

    generated/
    assets/visuals/
    remotion/public/
    remotion/out/
    timeline.json
    .venv/
    remotion/node_modules/
    .pytest_cache/
    __pycache__/

## Plan of Work

### Milestone 1: Current visual asset workflow audit

Audit the current visual asset discovery, preparation, inspection, and preflight behavior without editing source. Confirm:

- target visual scene types are `AI_VIDEO` and `B_ROLL`
- supported extensions are `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, and `.mov`
- `inspect-visual-assets` reports props-level `prepared`, `missing`, and `unsupported` counts
- `prepare-visual-assets` expects one supported file named with the scene id stem under `assets/visuals/`
- duplicate supported files for a scene are preparation errors
- unsupported local source files are not currently surfaced by props-only readiness
- exported props contain visual prompt/data fields and scene timing fields needed for a richer manifest
- `.gitignore` already covers `generated/` and local media/output paths

Record findings in this plan under `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective`.

### Milestone 2: Manifest design

Design the command and output contract before coding. The intended command shape is:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.md
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json

Final CLI contract:

- command name: `visual-manifest`
- positional input: `PROPS_JSON`, usually `remotion/props.json`
- `--assets-dir PATH`, default `assets/visuals`
- `--format markdown|json`, default `markdown`
- `--out PATH`, optional
- default output path when `--out` is omitted:
  - `generated/visual_manifest.md` for Markdown
  - `generated/visual_manifest.json` for JSON
- `--dry-run` prints the planned summary and intended output path, writes nothing, and creates no `generated/` directory
- `--overwrite` replaces a differing output file
- default no-overwrite behavior: write missing output, reuse identical output, and block differing output with `SyncCutError` mentioning `--overwrite`

Concise success output:

    Wrote visual manifest generated/visual_manifest.md
    format: markdown
    target_scenes: 17
    prepared: 0
    missing: 17
    unsupported: 0
    local_found: 0
    local_missing: 17
    local_duplicate_supported: 0
    local_unsupported_only: 0
    Next: review the manifest or run synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

When content is identical, use `Reused visual manifest <out>` with the same counts. Dry-run output starts with `Dry run: visual manifest <out>` and uses the same summary counts. Conflict errors must include the output path and `--overwrite`.

JSON schema stability: include `schema_version: "0.1"` and treat field additions as additive. Do not change Remotion props or timeline schemas.

Planned manifest fields:

- `scene_id`
- `section_key`
- `section`
- `section_order`
- `scene_order`
- `visual_type`
- `duration_sec`
- `duration_frames`
- `expected_asset_stem`, for example `assets/visuals/scene_001`
- `expected_filenames`, one per supported extension or a concise supported-extension list plus stem
- `assets_dir`
- `prepared_status`, from current props readiness: `prepared`, `missing`, or `unsupported`
- `local_asset_status`, such as `found`, `missing`, `duplicate_supported`, or `unsupported_only`
- `local_asset_path`, when exactly one supported local file exists
- `local_supported_paths`, for duplicate reporting
- `local_unsupported_paths`, for unsupported local source files with the scene id stem
- `public_path`, when props already contain a prepared public visual path
- `asset_source` and `asset_status` from props when present
- `prompt`, copied from `scene.visual.prompt` when present
- `keyword` or `search_query_seed`, derived only from existing props text without AI rewriting
- `visual_data`, only if already present and JSON-serializable
- `notes`, for human/provider guidance

Final status vocabulary:

- `prepared_status`: `prepared`, `missing`, or `unsupported`
- `local_asset_status`: `found`, `missing`, `duplicate_supported`, `unsupported_only`, or `not_checked`

Use `not_checked` only when local source inspection is intentionally skipped because `assets_dir` cannot be inspected in dry-run/error-tolerant reporting. The normal command should still validate `assets_dir` if it exists and should report missing when it does not exist.

Prompt/search extraction policy:

- no AI rewriting
- no web/API lookup
- no translation or summarization
- `prompt` copies `scene.visual.prompt` when it is a string, otherwise `null`
- `search_query_seed` uses the first available string from:
  1. `scene.visual.prompt`
  2. `scene.visual.description`
  3. `scene.visual.data.description` when `data` is an object
  4. `scene.visual.data.query` when `data` is an object
  5. `null`
- `visual_data` is included only when `scene.visual.data` is JSON-safe: object, array, string, number, bool, or null

Markdown layout:

    # Visual Asset Manifest

    Source props: remotion/props.json
    Assets dir: assets/visuals
    Format: markdown

    ## Summary

    - target_scenes: 17
    - prepared: 0
    - missing: 17
    - unsupported: 0
    - local_found: 0
    - local_missing: 17
    - local_duplicate_supported: 0
    - local_unsupported_only: 0

    ## Naming Policy

    Use one supported file per target scene:
    assets/visuals/<scene_id>.<supported_ext>

    Supported extensions: .jpeg, .jpg, .mov, .mp4, .png, .webm, .webp

    ## Scenes

    | scene_id | section_key | visual_type | duration_sec | prepared_status | local_asset_status | expected_asset_stem | search_query_seed |

Keep Markdown deterministic. Use stable extension ordering, stable props scene order, and no terminal-width-dependent alignment.

JSON layout:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut visual-manifest",
        "source_props": "remotion/props.json",
        "assets_dir": "assets/visuals",
        "format": "json"
      },
      "summary": {
        "target_scenes": 17,
        "prepared": 0,
        "missing": 17,
        "unsupported": 0,
        "local_found": 0,
        "local_missing": 17,
        "local_duplicate_supported": 0,
        "local_unsupported_only": 0
      },
      "supported_extensions": [".jpeg", ".jpg", ".mov", ".mp4", ".png", ".webm", ".webp"],
      "scenes": []
    }

JSON formatting must use two-space indentation, `ensure_ascii=False`, and a trailing newline.

Local source-file inspection policy:

- inspect direct child files under `assets_dir` only
- do not recurse into subdirectories
- do not create `assets_dir` if it is missing
- candidate source files have `path.stem == scene_id`
- supported suffixes use `SUPPORTED_VISUAL_EXTENSIONS`
- exactly one supported candidate means `local_asset_status: found`
- multiple supported candidates means `local_asset_status: duplicate_supported`
- zero supported candidates plus at least one unsupported stem match means `local_asset_status: unsupported_only`
- no matching stem candidates means `local_asset_status: missing`
- do not read, probe, decode, transcode, normalize, copy, or modify file contents

Implementation files for Milestone 3:

    synccut/visual_manifest.py
    synccut/cli.py
    tests/test_visual_manifest.py
    tests/test_cli.py
    docs/plans/visual-asset-manifest-workflow.md

Milestone 3 should import `TARGET_VISUAL_TYPES`, `SUPPORTED_VISUAL_EXTENSIONS`, and existing readiness helpers from `synccut.visual_assets` where useful. It should not rely on private helper names unless the implementation deliberately promotes a small public helper. A separate `synccut/visual_manifest.py` module is preferred so the richer reporting/writing logic does not bloat `visual_assets.py`.

Tests for Milestone 3:

- targets only `AI_VIDEO` and `B_ROLL`
- preserves props scene order
- includes section, duration, visual type, prompt, and visual data fields
- includes deterministic expected stem and supported extensions
- uses prompt/search seed from existing visual fields only
- reports `local_asset_status: missing` when no matching local asset exists
- reports `local_asset_status: found` for exactly one supported file
- reports `local_asset_status: duplicate_supported` for multiple supported files
- reports `local_asset_status: unsupported_only` for matching unsupported suffixes
- carries through prepared `public_path`, `asset_status`, and `asset_source` from props
- Markdown includes title, summary counts, naming policy, supported extensions, and scene table
- JSON is parseable, deterministic, and has expected metadata/summary/scene fields
- dry-run writes no file and creates no output directory
- identical output rerun reports reuse
- differing existing output blocks and mentions `--overwrite`
- overwrite replaces only the requested output file
- CLI success output includes counts and next step
- CLI dry-run output includes intended path and counts
- CLI conflict output exits non-zero and mentions `--overwrite`

The JSON output must not include API keys, provider credentials, downloaded media metadata, raw external provider payloads, or private license details.

### Milestone 3: Implement local visual manifest command

Expected files:

    synccut/visual_manifest.py
    synccut/cli.py
    tests/test_visual_manifest.py
    tests/test_cli.py
    docs/plans/visual-asset-manifest-workflow.md

Implementation requirements:

- Load `remotion/props.json` with existing JSON/props loading patterns where possible.
- Reuse `TARGET_VISUAL_TYPES`, `SUPPORTED_VISUAL_EXTENSIONS`, visual readiness classification, and safe path conventions from `synccut/visual_assets.py`.
- Inspect only `AI_VIDEO` and `B_ROLL` scenes.
- Preserve props scene order.
- Check local `assets_dir` for direct child files whose stem equals `scene_id`.
- Report exactly one supported local source file as local found.
- Report multiple supported source files as duplicate/ambiguous.
- Report files with the right stem but unsupported suffixes as unsupported local assets.
- Generate deterministic Markdown and JSON.
- Do not copy assets.
- Do not run `prepare-visual-assets`.
- Do not mutate `remotion/props.json`.
- Do not download media.
- Do not generate media.
- Do not probe/transcode/normalize media.
- Add focused unit and CLI tests.

Suggested tests:

- manifest targets only `AI_VIDEO` and `B_ROLL`
- scene order is preserved
- exported prompts and durations are included
- expected asset stem and supported extensions are deterministic
- missing local assets are reported
- one supported local file is reported as found
- duplicate supported local files are reported as ambiguous
- unsupported local files are reported
- prepared props public path is carried through
- Markdown output includes summary and scene rows
- JSON output is deterministic and parseable
- dry-run writes no file
- existing identical output is reused
- existing differing output blocks without `--overwrite`
- overwrite replaces only the requested output file
- CLI output reports counts and next step
- CLI errors mention `--overwrite` for output conflicts

### Milestone 4: Validate with sample

Run:

    .venv/bin/python -m pytest

Build or refresh sample props only if needed for validation:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

Run the new command:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.md
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json

Inspect generated outputs enough to confirm:

- target scene count matches the expected `AI_VIDEO` and `B_ROLL` count
- prepared/missing/unsupported props readiness counts are correct
- local found/missing/unsupported/duplicate source-file status is clear
- expected filename stems and supported extensions are clear
- prompt/search seed metadata appears when available in props
- JSON output is useful as Phase 32 downloader input

Run:

    cd remotion && npm run typecheck && cd ..

Do not run `prepare-visual-assets` unless a specific bug requires it and the reason is recorded. Do not render.

### Milestone 5: Docs, cleanup, final review

Decide whether README needs one concise note. If added, it should say only that `visual-manifest` creates a local Markdown/JSON planning manifest for optional AI/B-roll visual assets and does not download or generate media.

Confirm `.gitignore` already covers `generated/`; change `.gitignore` only if a new generated path outside the current ignore policy is introduced.

Cleanup validation outputs:

- remove `generated/visual_manifest.md`
- remove `generated/visual_manifest.json`
- remove `generated/` only if empty and removal is safe
- restore `remotion/props.json` if it changed only because sample props were regenerated and sample props refresh is not approved

Run final validation:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

Expected commit candidates are source/tests/docs only:

    synccut/visual_manifest.py
    synccut/cli.py
    tests/test_visual_manifest.py
    tests/test_cli.py
    docs/plans/visual-asset-manifest-workflow.md
    README.md only if updated
    .gitignore only if needed

Not expected as commit candidates:

    generated/visual_manifest.md
    generated/visual_manifest.json
    timeline.json
    remotion/props.json
    remotion/public/*
    remotion/out/*
    assets/visuals/*
    downloaded media
    generated media
    API key files
    caches
    .venv/
    remotion/node_modules/

Recommended commit message:

    Add visual asset manifest workflow

After this phase, ask the user before starting Phase 32 B-roll downloader work.

## Concrete Steps

Milestone 1 audit commands:

    sed -n '1,320p' synccut/visual_assets.py
    sed -n '1,260p' synccut/preflight.py
    sed -n '1,300p' synccut/remotion_exporter.py
    sed -n '1,360p' synccut/cli.py
    sed -n '1,260p' tests/test_visual_assets.py
    sed -n '1,260p' tests/test_preflight.py
    sed -n '1,320p' tests/test_cli.py
    sed -n '1,220p' remotion/props.json
    git status --short --ignored

Milestone 4 validation commands:

    .venv/bin/python -m pytest
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.md
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json
    cd remotion && npm run typecheck && cd ..

Milestone 5 final validation commands:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

## Validation and Acceptance

Acceptance criteria:

- A `visual-manifest` command exists and is documented in this plan.
- The command reads `remotion/props.json` and optional local source files under `assets/visuals/`.
- The command does not mutate props, copy assets, prepare assets, download assets, generate media, probe media, or render.
- Markdown output is useful for human review.
- JSON output is deterministic and useful for Phase 32 downloader input.
- Manifest entries include target visual scenes, expected naming, prepared readiness, local file availability, supported/unsupported local asset status, durations, and prompt/search seed metadata when available.
- Missing optional visuals remain non-fatal.
- Existing tests pass.
- Remotion typecheck passes.
- Generated manifest outputs remain ignored or are cleaned before final review.
- Commit candidates are source/tests/docs only.

## Idempotence and Recovery

The command should be safe to rerun. If the requested output does not exist, it writes the manifest. If the output exists and content matches, it reports reuse. If the output exists and content differs, it blocks with a clear message that mentions `--overwrite`. With `--overwrite`, it replaces only the requested manifest output file. `--dry-run` writes nothing and should not create `generated/`.

If validation regenerates `remotion/props.json`, restore it before final review unless the user explicitly approves a sample props refresh. Do not use broad cleanup commands. Remove only generated manifest files created for validation.

## Artifacts and Notes

Generated validation outputs:

    generated/visual_manifest.md
    generated/visual_manifest.json
    timeline.json

These should not be committed.

Local source media:

    assets/visuals/

This directory is local-only and ignored. The manifest may reference files there, but Phase 31 must not create, delete, modify, copy, download, or inspect media contents.

Prepared/public/render artifacts:

    remotion/public/
    remotion/out/

These are ignored and should not be commit candidates.

## Interfaces and Dependencies

The new command should be added to `synccut/cli.py` and delegate to pure/testable functions in `synccut/visual_manifest.py`. It should reuse constants and validation behavior from `synccut/visual_assets.py` instead of duplicating supported visual types and extensions.

No new third-party dependency is expected. No schema migration is expected. No Remotion source change is expected.

The JSON manifest should use ordinary JSON data types and stable field names so Phase 32 can consume it without scraping Markdown. Include `schema_version: "0.1"` in the JSON metadata.

## Change Note

Revision 2026-05-14: Initial Phase 31 ExecPlan created. The plan chooses `remotion/props.json` as input, designs a read-only `visual-manifest` command, requires Markdown and JSON outputs, keeps downloads/generation/rendering out of scope, and prepares a local manifest contract for future Phase 32 downloader work.
