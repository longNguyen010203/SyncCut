# Expand the real local TSMC visual asset subset to eight scenes

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to expand the prepared TSMC visual asset subset from three scenes to eight scenes from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can render the TSMC sample with local visual assets for `AI_VIDEO` and `B_ROLL` scenes when those assets are manually supplied under `assets/visuals/`. Phase 18 proved the workflow for `scene_001`, `scene_003`, and `scene_004`. Phase 19 expands that validated subset by adding `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`, bringing the intended prepared set to eight of the current 17 target visual scenes.

After this phase, a maintainer should be able to place the five new local files beside the existing three files, run the existing SyncCut asset preparation and readiness commands, see `prepared: 8`, `missing: 9`, and `unsupported: 0`, pass verified preflight with no errors or file errors, and optionally render the existing local segment preview. This phase is intentionally a local asset workflow phase: it must not add source-code features, change command behavior, change schemas, generate AI media inside the repo, download or scrape media, call ffmpeg or ffprobe, probe or transcode media, add render scripts, commit binary media, commit generated public assets, commit render outputs, or commit `remotion/props.json` unless explicitly approved.

## Progress

- [x] (2026-05-12T22:11:30+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `README.md`, `remotion/README.md`, `docs/tsmc-visual-asset-manifest.md`, `docs/plans/tsmc-first-real-visual-assets.md`, `docs/plans/tsmc-visual-asset-pack.md`, `remotion/props.json`, `.gitignore`, and the Remotion best-practices skill.
- [x] (2026-05-12T22:11:30+07:00) Inspected the current manifest statuses and current props prompt summaries for `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`.
- [x] (2026-05-12T22:11:30+07:00) Created this ExecPlan for expanding the real local TSMC visual asset subset to eight scenes.
- [x] (2026-05-12T22:20:39+07:00) Completed Milestone 1: updated `docs/tsmc-visual-asset-manifest.md` as a documentation-only asset brief for `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`, without creating media files.
- [x] (2026-05-13T09:09:47+07:00) Completed Milestone 2: validated exactly one supported `.mp4` file for each of the eight expected scenes, prepared eight visual assets, verified readiness/preflight/typecheck/pytest, and updated the five new manifest rows to `prepared-local`.
- [x] (2026-05-13T09:22:02+07:00) Completed Milestone 3: confirmed the prepared 8-scene visual state, ran typecheck, rendered the existing 900-frame segment preview with Chrome launch permission after sandbox failure, recorded `out/segment.mp4`, and reran pytest/artifact review.
- [x] (2026-05-13T09:26:19+07:00) Completed Milestone 4: regenerated clean props and audio without visual preparation, verified clean readiness/preflight, reran typecheck/pytest, reviewed artifacts, and recorded the documentation-only commit recommendation.

## Surprises & Discoveries

- Observation: The current working tree has no non-ignored commit candidates before this plan is added.
  Evidence: `git status --short --ignored` showed only ignored local/generated paths: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.
- Observation: The five Phase 19 target scenes are the next `AI_VIDEO` and `B_ROLL` scenes in timeline order after the first three prepared-local scenes.
  Evidence: The target order in `remotion/props.json` is `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, followed by later targets. `scene_005` and `scene_007` remain `CHART` and `TABLE` data-driven scenes, not local visual asset targets.
- Observation: The current manifest already identifies `scene_006` and `scene_008` as `optional-planned`, while `scene_010`, `scene_013`, and `scene_015` are still `needed`.
  Evidence: `docs/tsmc-visual-asset-manifest.md` marks `scene_006` and `scene_008` as `optional-planned`, and marks `scene_010`, `scene_013`, and `scene_015` as `needed`.
- Observation: Milestone 1 was a pure documentation update.
  Evidence: Only `docs/tsmc-visual-asset-manifest.md` and this ExecPlan were edited. No files were created or changed under `assets/visuals/`, no source files changed, `remotion/props.json` was not edited, and no render or media command was run.
- Observation: All eight selected scenes now have exactly one supported local file, and all eight use `.mp4`.
  Evidence: The supported-extension check found `assets/visuals/scene_001.mp4`, `scene_003.mp4`, `scene_004.mp4`, `scene_006.mp4`, `scene_008.mp4`, `scene_010.mp4`, `scene_013.mp4`, and `scene_015.mp4`, with no missing selected scenes and no duplicate supported files.
- Observation: Visual preparation was idempotent against existing public copies.
  Evidence: `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 8`, `visual_overwritten: 0`, `visual_missing: 9`, and `visual_assets: 8`.
- Observation: The expanded subset reached the expected warning-only readiness state.
  Evidence: `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 8`, `missing: 9`, and `unsupported: 0`; verified preflight reported `status: warning`, `visual_prepared: 8`, `visual_missing: 9`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The first segment render attempt was blocked by the known Chrome sandbox/browser permission issue.
  Evidence: `npm run render:segment:local` failed with `Failed to launch the browser process`, `Closed with null signal: SIGTRAP`, and `[ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`.
- Observation: The same segment render command succeeded when rerun with Chrome launch permission.
  Evidence: The permitted run rendered and encoded all `900/900` frames and wrote `out/segment.mp4`; Remotion reported `out/segment.mp4 34.3 MB`, and `ls -lh out/segment.mp4` reported `33M`.
- Observation: Clean props were restored after preview validation.
  Evidence: After rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` without `prepare-visual-assets`, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.
- Observation: Final verified preflight is warning-only with no file errors.
  Evidence: Clean verified preflight reported `status: warning`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

## Decision Log

- Decision: Expand the prepared subset to exactly eight target scenes: the existing `scene_001`, `scene_003`, and `scene_004`, plus `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`.
  Rationale: These are the next target `AI_VIDEO` and `B_ROLL` scenes in props order. They keep the phase small enough to validate thoroughly while making the first four sections of the sample less placeholder-heavy.
  Date/Author: 2026-05-12 / Codex
- Decision: Use `planned` for all five new Phase 19 targets during Milestone 1.
  Rationale: The manifest already uses `planned` for actively selected work and `prepared-local` for assets that have been placed, prepared, and validated. Moving `scene_006` and `scene_008` from `optional-planned` to `planned`, and `scene_010`, `scene_013`, and `scene_015` from `needed` to `planned`, clearly marks the Phase 19 production target set.
  Date/Author: 2026-05-12 / Codex
- Decision: Continue to prefer `.mp4` filenames for the new target scenes, while allowing any existing supported extension during validation.
  Rationale: The prompts describe motion or montage, and `.mp4` exercises the current Remotion video path. The existing command also supports `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`; validation should accept whichever single supported local file is actually supplied for each scene.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep production provenance as a manifest note, not as code or schema.
  Rationale: Rights and production source tracking matter, but this phase must not change schemas or command behavior. The manifest can record `unknown-local`, `original/manual`, `external-generated`, or `licensed/manual-source` without touching runtime data structures.
  Date/Author: 2026-05-12 / Codex
- Decision: Generalize the manifest definition of `planned` from "first subset" to "active local asset production in the current phase."
  Rationale: Phase 18 used `planned` for the first real subset. Phase 19 needs the same status for the next active five-scene subset, so the definition now describes current-phase production instead of only the first subset.
  Date/Author: 2026-05-12 / Codex
- Decision: Mark `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `prepared-local` with provenance `unknown-local`.
  Rationale: All five files were present, prepared, and verified successfully. The exact production provenance was not supplied in this validation task, so `unknown-local` is the accurate manifest category.
  Date/Author: 2026-05-13 / Codex
- Decision: No selected assets were skipped or replaced during Milestone 2.
  Rationale: Each of the eight expected scene ids had exactly one supported `.mp4` source file, and the preparation command accepted all eight.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested documentation and inspecting the current manifest, props, Remotion workflow docs, and ignore rules. No source code, schemas, Remotion rendering code, media files, generated artifacts, command behavior, commits, or tags were changed.

The immediate next milestone is documentation-only. It should update `docs/tsmc-visual-asset-manifest.md` to mark `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `planned`, with expected filenames, recommended asset types, production briefs, and provenance placeholders. Actual real media placement happens later, after a human or external production process creates the files outside SyncCut and places them under `assets/visuals/`.

Milestone 1 is complete. `docs/tsmc-visual-asset-manifest.md` now preserves `prepared-local` status for `scene_001`, `scene_003`, and `scene_004`, and marks `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `planned`. Each of the five new Phase 19 rows keeps the expected `.mp4` filename, states that video is preferred while a supported still is acceptable for validation if needed, includes the provenance placeholder `TBD: original/manual, external-generated, licensed/manual-source, or unknown-local`, and includes a concise production direction based on the current `remotion/props.json` prompt summary.

No media files were created, no files under `assets/visuals/` were created or edited, no Python source, Remotion source, schemas, command behavior, or `remotion/props.json` changed, no media was downloaded or generated, no ffmpeg or ffprobe command was called, no render was run, and no commit or tag was created. The next step waits for real local files under `assets/visuals/` before running Milestone 2 validation.

Milestone 2 is complete. The local asset inspection confirmed eight selected source files and no duplicates:

    assets/visuals/scene_001.mp4
    assets/visuals/scene_003.mp4
    assets/visuals/scene_004.mp4
    assets/visuals/scene_006.mp4
    assets/visuals/scene_008.mp4
    assets/visuals/scene_010.mp4
    assets/visuals/scene_013.mp4
    assets/visuals/scene_015.mp4

The validation workflow regenerated `timeline.json`, validated the timeline with the known `07_CONCLUSION` gap warning, exported `remotion/props.json`, and prepared audio with `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`. Before visual preparation, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.

After running `prepare-visual-assets`, the command reported `visual_copied: 0`, `visual_reused: 8`, `visual_overwritten: 0`, `visual_missing: 9`, and `visual_assets: 8`. `inspect-visual-assets` then reported `target_scenes: 17`, `prepared: 8`, `missing: 9`, and `unsupported: 0`, with prepared public paths for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`.

Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 8`, `visual_missing: 9`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The remaining warnings are the known root props warning for the `07_CONCLUSION` gap plus nine expected placeholder-backed visual asset warnings for later target scenes.

Remotion typecheck passed with `npm run typecheck`. Python validation passed with `.venv/bin/python -m pytest`, collecting and passing 208 tests.

`docs/tsmc-visual-asset-manifest.md` now marks the five Phase 19 scenes `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `prepared-local`, records the actual `.mp4` filenames, and records provenance as `unknown-local`. The existing prepared-local records for `scene_001`, `scene_003`, and `scene_004` were preserved.

Artifact policy remains unchanged. `assets/visuals/*`, `remotion/public/visuals/*`, `timeline.json`, and generated caches are ignored and should not be committed. `remotion/props.json` was modified by validation and `prepare-visual-assets`; it should not be committed unless explicitly approved, and it should be cleaned during Milestone 4. Normal commit candidates for this milestone are documentation only: `docs/plans/tsmc-expand-real-visual-assets.md` and `docs/tsmc-visual-asset-manifest.md`.

Milestone 3 is complete. Before rendering, the current prepared state was reconfirmed: `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 8`, `missing: 9`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 8`, `visual_missing: 9`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

Remotion typecheck passed with `npm run typecheck`. The first `npm run render:segment:local` attempt failed at browser launch with `SIGTRAP` and `setsockopt: Operation not permitted (1)`, matching the known sandbox permission limitation. Rerunning the same script with Chrome launch permission succeeded: Remotion rendered and encoded `900/900` frames and wrote `remotion/out/segment.mp4`. Remotion reported `out/segment.mp4 34.3 MB`; `ls -lh out/segment.mp4` reported `33M`.

Python validation passed after the render preview with `.venv/bin/python -m pytest`, collecting and passing 208 tests. `git status --short --ignored` showed `docs/tsmc-visual-asset-manifest.md` modified from earlier manifest updates, `docs/plans/tsmc-expand-real-visual-assets.md` as a new documentation file, and `remotion/props.json` modified by prepared visual validation. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.

No Python source, Remotion source, schemas, command behavior, render scripts, media files, commits, or tags were changed in Milestone 3. No media was downloaded, fetched, scraped, generated, probed, transcoded, normalized, or processed with ffmpeg/ffprobe. `remotion/props.json` remains intentionally prepared for the current preview state and should be cleaned during Milestone 4.

Milestone 4 is complete. `remotion/props.json` was cleaned from prepared visual paths by rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets`, without rerunning `prepare-visual-assets`. The timeline validation still passed with the known `07_CONCLUSION` gap warning. Audio preparation reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`.

The clean visual readiness check reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Clean verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. This confirms that `remotion/props.json` is restored to the sample baseline with audio public paths but without local synthetic or real visual public paths.

Final validation passed. `npm run typecheck` passed from `remotion/`, and `.venv/bin/python -m pytest` passed with 208 tests. The final artifact review showed only documentation commit candidates: `docs/tsmc-visual-asset-manifest.md` and `docs/plans/tsmc-expand-real-visual-assets.md`. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`. `remotion/props.json` is not a commit candidate after cleanup.

Final review checklist result: Phase 19 stayed within scope; real files were supplied locally under `assets/visuals/`; SyncCut did not generate AI media; no B-roll or external media was downloaded, fetched, or scraped; no ffmpeg, ffprobe, probing, transcoding, or normalization was used; no Python source, Remotion source, schemas, or command behavior changed; the prepared subset `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` validated with `prepared: 8`, `missing: 9`, and `unsupported: 0`; preflight after preparation had `errors: 0` and `file_errors: 0`; segment preview succeeded with Chrome permission; clean props were restored; generated media, public assets, render outputs, and timeline artifacts remain ignored; and the manifest records all eight selected scenes as `prepared-local`.

Risks remaining: the local visual files are intentionally ignored and must be preserved outside git or reproduced by the asset production process; provenance remains `unknown-local` until a maintainer records a more specific source category; and later phases should avoid accidentally staging generated props or binary media after visual preparation.

Commit recommendation: commit documentation only. Recommended commit message: `Document expanded TSMC visual asset subset validation`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

`assets/visuals/` is the local source directory for manually supplied visual files. The file naming convention is `assets/visuals/<scene_id>.<ext>`, for example `assets/visuals/scene_006.mp4`. The supported extensions are `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, and `.mov`. There must be exactly one supported file per prepared scene id. If both `scene_006.mp4` and `scene_006.png` exist, the preparation command should fail because the scene is ambiguous.

`remotion/public/visuals/` is the prepared public directory used by Remotion. The command `synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` copies local files into `remotion/public/visuals/` and annotates `remotion/props.json` with public paths such as `visuals/scene_006.mp4`. A public path means a path relative to Remotion's `public` directory. Remotion loads those files with `staticFile("visuals/...")`.

Both `assets/visuals/` and `remotion/public/` are ignored by git. Render outputs under `remotion/out/` and `timeline.json` are also ignored. `remotion/props.json` may be rewritten during validation, but it should not be committed unless explicitly approved.

Phase 18 validated the first real local subset: `scene_001`, `scene_003`, and `scene_004`. The manifest now marks those three rows as `prepared-local`, with actual filenames under `assets/visuals/` and provenance `unknown-local`. Phase 18 also proved that `render:segment:local` can render a 900-frame preview with local Chrome when Chrome launch permission is granted.

## Target Scene Table

The Phase 19 new target scenes are listed below. The current manifest status is the status before Milestone 1 changes.

| scene_id | section_key | visual_type | current manifest status | expected filename | recommended asset type | production brief | provenance placeholder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scene_006` | `02_INTRO` | `B_ROLL` | `optional-planned` | `assets/visuals/scene_006.mp4` | Video preferred; supported still acceptable for validation. | Show a grain of sand falling into a researcher's hand, then cut or visually connect to a gleaming silicon wafer under clean lab light. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_008` | `03_MECHANISM_1` | `AI_VIDEO` | `optional-planned` | `assets/visuals/scene_008.mp4` | Video preferred; stylized still acceptable for validation. | Create a clearly stylized 1987 Hsinchu handshake over a contract with empty industrial land behind the subjects; avoid claiming archival authenticity unless sourced. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_010` | `03_MECHANISM_1` | `B_ROLL` | `needed` | `assets/visuals/scene_010.mp4` | Video preferred. | Show whiteboard circuit diagrams and a marker line separating design from manufacturing, then a modern chip-design office context. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_013` | `04_MECHANISM_2` | `AI_VIDEO` | `needed` | `assets/visuals/scene_013.mp4` | Video preferred; motion graphic ideal. | Visualize a transistor shrinking from visible scale to nanometer scale, with a human-hair comparison and node numbers counting down to 2nm. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_015` | `04_MECHANISM_2` | `B_ROLL` | `needed` | `assets/visuals/scene_015.mp4` | Video preferred. | Show a semiconductor cleanroom with engineers in full suits working around large machines in a pristine white environment. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |

The expected final prepared set after Milestone 2 is:

- `scene_001`
- `scene_003`
- `scene_004`
- `scene_006`
- `scene_008`
- `scene_010`
- `scene_013`
- `scene_015`

If exactly those eight scenes have one supported local file each, the expected readiness result is `target_scenes: 17`, `prepared: 8`, `missing: 9`, and `unsupported: 0`.

## Scene Selection Rationale

The five new scenes are the next `AI_VIDEO` and `B_ROLL` scenes after the first three validated scenes in timeline order. This selection expands coverage through early hook, introduction, mechanism 1, and the beginning of mechanism 2 without requiring the entire 17-scene visual pack to exist.

The phase is small but meaningful. It validates both types of optional local visual scenes again: `AI_VIDEO` scenes `scene_008` and `scene_013`, plus `B_ROLL` scenes `scene_006`, `scene_010`, and `scene_015`. It also brings the prepared target count from 3 to 8, leaving 9 placeholder-backed visual scenes for later phases.

## Asset Production Boundary

Real assets are produced manually or by external tools outside SyncCut. SyncCut only validates, copies, and references local files that already exist under `assets/visuals/`.

Do not generate AI media inside this repository. Do not call image or video generation APIs from the repo. Do not download, fetch, or scrape B-roll or other external media inside the repo. Do not call `ffmpeg` or `ffprobe`. Do not probe, decode, transcode, normalize, or trim media. Do not edit Python source, Remotion source, schemas, npm scripts, command behavior, or render scripts. Do not commit binary visual assets, generated public copies, render outputs, or temporary prepared `remotion/props.json` changes.

When provenance is known, record it in `docs/tsmc-visual-asset-manifest.md` using a concise category. Avoid private license details, credentials, raw external generation payloads, or embedded media.

## Plan of Work

Milestone 1 is documentation-only. Update `docs/tsmc-visual-asset-manifest.md` so `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` are marked `planned`. Preserve the existing `prepared-local` status for `scene_001`, `scene_003`, and `scene_004`. Add or refine production notes for the five new targets with expected filenames, video-preferred guidance, and provenance placeholders. Do not create media files and do not touch `assets/visuals/`.

Milestone 2 begins only after the user or an external process places real files under `assets/visuals/`. Inspect `assets/visuals/` and confirm that all eight expected scenes have exactly one supported local file each. Stop and report missing files or duplicates before running preparation. Regenerate timeline and props, prepare audio, inspect visual readiness before visual preparation, run `prepare-visual-assets`, inspect visual readiness after preparation, run verified preflight, run Remotion typecheck, and run Python tests. If a selected scene prepares successfully, update its manifest status to `prepared-local`, record the actual filename used, and set provenance to the known category or `unknown-local`.

Milestone 3 is optional segment preview. Use only existing render commands. The preferred command is `npm run render:segment:local` from `remotion/`. If Chrome launch is blocked by sandbox permissions, record the exact error and rerun with Chrome launch permission if available. Do not add workaround code, do not add render scripts, and do not render the full final video unless explicitly requested later. Record the output path and size if a preview is produced.

Milestone 4 is final review and cleanup. Regenerate clean props and audio only, without rerunning `prepare-visual-assets`, so `remotion/props.json` does not remain annotated with local prepared visual paths. Verify the clean readiness state and verified preflight, run typecheck and pytest, review `git status --short --ignored`, and recommend committing docs only.

## Concrete Validation Commands

Run these from the repository root to regenerate clean props and audio:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json

Before visual preparation, expected clean readiness is:

    target_scenes: 17
    prepared: 0
    missing: 17
    unsupported: 0

After all eight expected local source files exist, run:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected readiness after visual preparation is:

    target_scenes: 17
    prepared: 8
    missing: 9
    unsupported: 0

Expected verified preflight fields after visual preparation are:

    status: warning
    visual_prepared: 8
    visual_missing: 9
    visual_unsupported: 0
    errors: 0
    verify_files: true
    file_errors: 0

Run Remotion typecheck:

    cd remotion
    npm run typecheck
    cd ..

Run Python tests:

    .venv/bin/python -m pytest

Optional existing segment preview:

    cd remotion
    npm run render:segment:local
    ls -lh out/segment.mp4
    cd ..

Artifact review:

    git status --short --ignored

## Validation and Acceptance

Milestone 1 is accepted when `docs/tsmc-visual-asset-manifest.md` marks `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `planned` and records expected filenames, production notes, and provenance placeholders without creating media files.

Milestone 2 is accepted when all eight expected scenes have exactly one supported local file, `prepare-visual-assets` prepares eight visual assets, `inspect-visual-assets` reports `prepared: 8`, `missing: 9`, and `unsupported: 0`, verified preflight reports `errors: 0` and `file_errors: 0`, Remotion typecheck passes, and pytest passes.

Milestone 3 is accepted when the existing segment preview either succeeds and writes an ignored `remotion/out/segment.mp4`, or fails only because of documented browser-launch sandbox limits. A successful preview should record the output size. A sandbox failure should record the exact error and should not trigger code or configuration changes.

Milestone 4 is accepted when `remotion/props.json` is cleaned from local visual public paths, clean `inspect-visual-assets` returns the baseline missing-only state, clean verified preflight has `errors: 0` and `file_errors: 0`, generated artifacts remain ignored, and commit candidates are documentation only.

## Risks

Duplicate files are the most likely local workflow error. If more than one supported file exists for the same scene id, stop before preparation and report the duplicates.

Unsupported extensions are ignored by `prepare-visual-assets`. If a scene appears missing even though a file exists, check whether the extension is one of `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, or `.mov`.

Large media files may slow rendering and public directory copying. This phase should validate the workflow but should not commit those files.

Rights and provenance may be ambiguous. Use `unknown-local` when the local file is available but its production source is not established, and do not include private license details or credentials in docs.

Chrome can fail to launch in sandboxed environments. The known failure mode is `SIGTRAP` with `setsockopt: Operation not permitted`. Record the error and rerun with Chrome launch permission if available; do not add workaround code.

`remotion/props.json` will be modified by `prepare-visual-assets`. Clean it during Milestone 4 before final artifact review unless the user explicitly approves committing prepared local visual paths.

## Explicit Exclusions

Do not edit Python source. Do not edit Remotion source. Do not edit schemas. Do not change command behavior. Do not add or change render scripts. Do not generate AI media inside the repo. Do not download, fetch, or scrape B-roll or other media inside the repo. Do not call `ffmpeg` or `ffprobe`. Do not probe, transcode, normalize, trim, or inspect media contents. Do not commit binary media. Do not commit generated public assets. Do not commit render outputs. Do not commit `remotion/props.json` unless explicitly approved. Do not commit or tag unless explicitly asked.

## Idempotence and Recovery

The workflow is safe to rerun. `build-timeline`, `export-remotion`, and `prepare-remotion-assets` restore a clean props baseline. `prepare-visual-assets` can be rerun after local files change; it copies missing files, reuses identical destination files, and overwrites changed destination files while reporting counts.

If preparation fails due duplicates, remove or move the duplicate ignored local file outside `assets/visuals/`, then rerun. If verified preflight reports `missing_public_file`, rerun `prepare-visual-assets` and confirm the copied file exists under `remotion/public/visuals/`. If `remotion/props.json` is accidentally left modified after validation, rerun `export-remotion` and `prepare-remotion-assets` without `prepare-visual-assets` to restore the clean sample state.

## Artifacts and Notes

Expected source asset files after Milestone 2 are:

    assets/visuals/scene_001.<supported-ext>
    assets/visuals/scene_003.<supported-ext>
    assets/visuals/scene_004.<supported-ext>
    assets/visuals/scene_006.<supported-ext>
    assets/visuals/scene_008.<supported-ext>
    assets/visuals/scene_010.<supported-ext>
    assets/visuals/scene_013.<supported-ext>
    assets/visuals/scene_015.<supported-ext>

Preferred filenames are `.mp4`, matching the manifest, but validation should use the actual single supported extension present for each scene.

Ignored/generated paths include:

    assets/visuals/
    remotion/public/
    remotion/out/
    timeline.json
    .venv/
    remotion/node_modules/
    .pytest_cache/
    __pycache__/

Normal commit candidates for this phase are expected to be:

    docs/plans/tsmc-expand-real-visual-assets.md
    docs/tsmc-visual-asset-manifest.md

## Interfaces and Dependencies

No new dependencies are required.

This phase uses existing Python CLI commands:

    synccut build-timeline
    synccut validate-timeline
    synccut export-remotion
    synccut prepare-remotion-assets
    synccut prepare-visual-assets
    synccut inspect-visual-assets
    synccut preflight

This phase uses existing Remotion npm scripts:

    npm run typecheck
    npm run render:segment:local

The Remotion rendering path uses local assets from `remotion/public/visuals/` via `staticFile()`. The existing `VisualAssetScene.tsx` component renders images with Remotion `Img`, renders videos with `OffthreadVideo`, and falls back to placeholders when no valid local visual public path is present. No Remotion code should change in this phase.
