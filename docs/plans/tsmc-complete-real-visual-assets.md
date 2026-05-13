# Complete the real local TSMC visual asset set

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to complete the remaining TSMC local visual assets from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already render the TSMC sample with locally supplied visual assets for `AI_VIDEO` and `B_ROLL` scenes. Earlier phases validated eight of the seventeen target visual scenes. This phase completes the local visual asset pack by planning, validating, and reviewing the remaining nine target scenes so `inspect-visual-assets` can eventually report `prepared: 17`, `missing: 0`, and `unsupported: 0`.

After this phase, a maintainer should be able to place one local supported file for every target scene under `assets/visuals/`, run the existing asset preparation and preflight commands, verify that all 17 target visuals are prepared, and optionally render an existing preview or final render script. This phase must not add source-code features, change command behavior, change schemas, generate AI media inside the repo, download or scrape media, call ffmpeg or ffprobe, probe or transcode media, add render scripts, commit binary media, commit generated public assets, commit render outputs, or commit `remotion/props.json` unless explicitly approved.

## Progress

- [x] (2026-05-13T09:34:00+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `README.md`, `remotion/README.md`, `docs/tsmc-visual-asset-manifest.md`, `docs/plans/tsmc-expand-real-visual-assets.md`, `docs/plans/tsmc-first-real-visual-assets.md`, `docs/plans/tsmc-visual-asset-pack.md`, `remotion/props.json`, and `.gitignore`.
- [x] (2026-05-13T09:34:00+07:00) Inspected current target scene prompts from `remotion/props.json`, current manifest statuses, and ignored artifact policy.
- [x] (2026-05-13T09:34:00+07:00) Created this ExecPlan for completing the remaining nine TSMC local visual assets.
- [x] (2026-05-13T09:39:38+07:00) Completed Milestone 1: updated `docs/tsmc-visual-asset-manifest.md` as a documentation-only asset brief for the nine remaining Phase 20 targets, preserving the existing eight `prepared-local` rows and creating no media files.
- [x] (2026-05-13T10:06:43+07:00) Completed Milestone 2: validated exactly one supported `.mp4` file for all 17 target scenes, prepared all 17 visual assets, reached zero visual-missing warnings, passed verified preflight/typecheck/pytest, and updated the nine remaining manifest rows to `prepared-local`.
- [x] (2026-05-13T10:16:19+07:00) Completed Milestone 3: confirmed the prepared 17-scene visual state, ran typecheck, rendered the existing 900-frame segment preview with Chrome launch permission after sandbox failure, skipped full final render as impractical for this milestone, and reran pytest/artifact review.
- [x] (2026-05-13T10:21:38+07:00) Completed Milestone 4: cleaned `remotion/props.json` back to sample props without prepared visual paths, verified clean readiness/preflight, reran typecheck and pytest, reviewed artifacts, and recommended committing documentation only.

## Surprises & Discoveries

- Observation: The current manifest records eight scenes as already validated `prepared-local`.
  Evidence: `docs/tsmc-visual-asset-manifest.md` marks `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` as `prepared-local`.
- Observation: The remaining Phase 20 targets are exactly nine scenes.
  Evidence: The remaining `needed` rows in `docs/tsmc-visual-asset-manifest.md` are `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: The current props still define 17 AI/B-roll target scenes.
  Evidence: Inspecting `remotion/props.json` found the same target set in scene order: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: The working tree currently has only ignored generated/local paths before this plan is added.
  Evidence: `git status --short --ignored` showed ignored paths including `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.
- Observation: Milestone 1 was a pure documentation update.
  Evidence: Only `docs/tsmc-visual-asset-manifest.md` and this ExecPlan were edited. No files were created or changed under `assets/visuals/`, no source files changed, `remotion/props.json` was not edited, and no render or media command was run.
- Observation: All 17 target scenes now have exactly one supported local file, and all 17 use `.mp4`.
  Evidence: The supported-extension check found one file each for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`, with no missing scene ids and no duplicate supported files.
- Observation: Visual preparation reused existing public copies for every local visual.
  Evidence: `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`.
- Observation: Visual readiness reached complete coverage with no visual-missing warnings.
  Evidence: `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`; verified preflight reported `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The first segment render attempt was blocked by the known Chrome sandbox/browser permission issue.
  Evidence: `npm run render:segment:local` failed with `Failed to launch the browser process`, `Closed with null signal: SIGTRAP`, and `[ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`.
- Observation: The same segment render command succeeded when rerun with Chrome launch permission.
  Evidence: The permitted run copied the larger public directory up to `220.6 MB`, rendered and encoded all `900/900` frames, and wrote `out/segment.mp4`; Remotion reported `out/segment.mp4 34.3 MB`, and `ls -lh out/segment.mp4` reported `33M`.
- Observation: Full render was not attempted in Milestone 3.
  Evidence: The current full composition is `22584` frames, while the 900-frame segment render took several minutes and copied a `220.6 MB` public directory. Starting `render:final:local` would be substantially longer and was not practical for this validation milestone.
- Observation: Clean props were restored after preview validation.
  Evidence: After regenerating `remotion/props.json` and preparing audio only, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`; `git status --short docs/plans/tsmc-complete-real-visual-assets.md docs/tsmc-visual-asset-manifest.md remotion/props.json` did not list `remotion/props.json`.
- Observation: Final clean verified preflight returned no errors or file errors.
  Evidence: Clean verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

## Decision Log

- Decision: Complete the visual asset pack by targeting all nine remaining `needed` rows from the manifest.
  Rationale: The previous phase validated the first eight target scenes. The remaining nine are the only scenes still expected to produce visual-missing warnings once props are prepared with local visual assets.
  Date/Author: 2026-05-13 / Codex
- Decision: Continue to prefer `.mp4` for every remaining target, while accepting any single supported extension during validation.
  Rationale: The prompts describe motion, montage, maps, presentations, or cinematic shots. `.mp4` best exercises the existing Remotion video path, but the current command also supports `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`, so validation should use the actual single supported file that was supplied.
  Date/Author: 2026-05-13 / Codex
- Decision: Keep Phase 20 as local asset workflow and documentation, not media acquisition or generation.
  Rationale: SyncCut already has deterministic copy, readiness, preflight, and render workflows. Media production, licensing, and generation must happen outside the repo so this phase does not add network, AI, ffmpeg, probing, or schema risk.
  Date/Author: 2026-05-13 / Codex
- Decision: Treat full render as optional and heavier than segment preview.
  Rationale: A full render can take a long time and produce a large ignored output. `render:segment:local` is a smaller validation target, while `render:final:local` should be attempted only when time and Chrome launch permission are available or the user explicitly requests it.
  Date/Author: 2026-05-13 / Codex
- Decision: Remove `optional-planned` from the manifest status list for Phase 20.
  Rationale: No current manifest row uses `optional-planned` after the first eight scenes were validated and the remaining nine were selected for active production. Keeping only statuses that are currently meaningful reduces ambiguity for the final completion phase.
  Date/Author: 2026-05-13 / Codex
- Decision: Mark `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033` as `prepared-local` with provenance `unknown-local`.
  Rationale: All nine remaining files were present, prepared, and verified successfully. The exact production provenance was not supplied in this validation task, so `unknown-local` is the accurate manifest category.
  Date/Author: 2026-05-13 / Codex
- Decision: No selected assets were skipped or replaced during Milestone 2.
  Rationale: Each of the 17 expected scene ids had exactly one supported `.mp4` source file, and the preparation command accepted all 17.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested guidance, current TSMC visual manifest, prior asset-pack plans, current props, Remotion workflow notes, and ignore rules. No source code, schemas, Remotion rendering code, media files, generated public assets, render outputs, command behavior, commits, or tags were changed.

The planned outcome is the final local visual asset completion path for the TSMC sample. Success means all 17 `AI_VIDEO` and `B_ROLL` target scenes have exactly one supported local source file, the existing preparation command reports 17 prepared visual assets, readiness reports no missing or unsupported visual assets, verified preflight has no errors or file errors, and generated media/public/render artifacts remain ignored.

Milestone 1 is complete. `docs/tsmc-visual-asset-manifest.md` now preserves `prepared-local` status for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`, and marks `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033` as `planned`. Each remaining Phase 20 row keeps the expected `.mp4` filename, states that video is preferred while a supported still is acceptable for validation if needed, includes the provenance placeholder `TBD: original/manual, external-generated, licensed/manual-source, or unknown-local`, and includes a concise production direction based on the current `remotion/props.json` prompt summary.

The manifest remains text-only. No binary media, private license details, API keys, raw external generation payloads, generated media, downloaded assets, source-code changes, schema changes, command behavior changes, `remotion/props.json` edits, renders, commits, or tags were created. The next step waits for real local files for the nine remaining scenes to be placed under `assets/visuals/` by a human or external production process before Milestone 2 validation.

Milestone 2 is complete. The local asset inspection confirmed all 17 expected source files and no duplicates:

    assets/visuals/scene_001.mp4
    assets/visuals/scene_003.mp4
    assets/visuals/scene_004.mp4
    assets/visuals/scene_006.mp4
    assets/visuals/scene_008.mp4
    assets/visuals/scene_010.mp4
    assets/visuals/scene_013.mp4
    assets/visuals/scene_015.mp4
    assets/visuals/scene_017.mp4
    assets/visuals/scene_020.mp4
    assets/visuals/scene_022.mp4
    assets/visuals/scene_025.mp4
    assets/visuals/scene_027.mp4
    assets/visuals/scene_029.mp4
    assets/visuals/scene_030.mp4
    assets/visuals/scene_031.mp4
    assets/visuals/scene_033.mp4

The validation workflow regenerated `timeline.json`, validated the timeline with the known `07_CONCLUSION` gap warning, exported `remotion/props.json`, and prepared audio with `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`. Before visual preparation, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.

After running `prepare-visual-assets`, the command reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`. `inspect-visual-assets` then reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`, with prepared public paths for every `AI_VIDEO` and `B_ROLL` target scene.

Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 1`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The only remaining warning is the known root props warning for the `07_CONCLUSION` gap; there are no visual-missing warnings.

Remotion typecheck passed with `npm run typecheck`. Python validation passed with `.venv/bin/python -m pytest`, collecting and passing 208 tests.

`docs/tsmc-visual-asset-manifest.md` now marks all 17 target scenes as `prepared-local`. The nine Phase 20 scenes `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033` now record actual `.mp4` filenames and provenance `unknown-local`. The existing prepared-local records for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015` were preserved.

Artifact policy remains unchanged. `assets/visuals/*`, `remotion/public/visuals/*`, `timeline.json`, and generated caches are ignored and should not be committed. `remotion/props.json` was modified by validation and `prepare-visual-assets`; it should not be committed unless explicitly approved, and it should be cleaned during Milestone 4. Normal commit candidates for this milestone are documentation only: `docs/plans/tsmc-complete-real-visual-assets.md` and `docs/tsmc-visual-asset-manifest.md`.

Milestone 3 is complete. Before rendering, the current prepared state was reconfirmed: `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`; the only warning was the known `07_CONCLUSION` gap.

Remotion typecheck passed with `npm run typecheck`. The first `npm run render:segment:local` attempt failed at browser launch with `SIGTRAP` and `setsockopt: Operation not permitted (1)`, matching the known sandbox permission limitation. Rerunning the same script with Chrome launch permission succeeded: Remotion rendered and encoded `900/900` frames and wrote `remotion/out/segment.mp4`. Remotion reported `out/segment.mp4 34.3 MB`; `ls -lh out/segment.mp4` reported `33M`.

The full final render was not attempted in Milestone 3. The full composition is `22584` frames, and the successful 900-frame segment render already took several minutes while copying a `220.6 MB` public directory. Running `npm run render:final:local` would be substantially longer and was not practical for this milestone's validation time budget. No workaround code, render scripts, source changes, or configuration changes were added.

Python validation passed after the segment preview with `.venv/bin/python -m pytest`, collecting and passing 208 tests. `git status --short --ignored` showed `docs/tsmc-visual-asset-manifest.md` modified from earlier manifest updates, `docs/plans/tsmc-complete-real-visual-assets.md` as a new documentation file, and `remotion/props.json` modified by prepared visual validation. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.

No Python source, Remotion source, schemas, command behavior, render scripts, media files, commits, or tags were changed in Milestone 3. No media was downloaded, fetched, scraped, generated, probed, transcoded, normalized, or processed with ffmpeg/ffprobe. `remotion/props.json` remains intentionally prepared for the current preview state and should be cleaned during Milestone 4.

Milestone 4 is complete. The final cleanup regenerated the timeline, validated it with the known `07_CONCLUSION` gap warning, exported clean `remotion/props.json`, and prepared audio assets only. `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`. No visual asset preparation was run after cleanup.

The clean readiness checks passed in the expected placeholder state. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The warnings are expected in clean props: one root warning for the `07_CONCLUSION` timing gap and 17 placeholder warnings because local visual public paths are intentionally absent from the regenerated sample props.

Final validation passed. `cd remotion && npm run typecheck` passed. `.venv/bin/python -m pytest` collected and passed 208 tests. The final artifact review showed documentation-only commit candidates: modified `docs/tsmc-visual-asset-manifest.md` and new `docs/plans/tsmc-complete-real-visual-assets.md`. `remotion/props.json` is not a commit candidate after cleanup. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.

Final Phase 20 review result: the phase stayed within scope. All 17 target visual scenes have exactly one local supported `.mp4` source file under `assets/visuals/`; SyncCut did not generate AI media, download/fetch/scrape external media, call ffmpeg/ffprobe, probe/transcode/normalize media, change source code, change schemas, change command behavior, add render scripts, commit media, or tag a release. All 17 prepared-local scenes were validated in Milestone 2, where `inspect-visual-assets` reached `prepared: 17`, `missing: 0`, `unsupported: 0`, and verified preflight reached `visual_missing: 0`, `errors: 0`, and `file_errors: 0`. Milestone 3 confirmed the complete prepared set through a segment render preview that succeeded with Chrome launch permission; full final render was intentionally skipped as impractical for this milestone budget.

Risks remain operational rather than code-related: the local `.mp4` files are ignored and must be preserved outside git; provenance is recorded as `unknown-local` where exact source details were not supplied; future render attempts still depend on Chrome launch permission and local machine capacity; and `remotion/props.json` should not be committed after running `prepare-visual-assets` unless a future task explicitly approves a sample props refresh.

Commit recommendation: commit documentation only. Recommended commit candidates are `docs/tsmc-visual-asset-manifest.md` and `docs/plans/tsmc-complete-real-visual-assets.md`. Do not commit `assets/visuals/*`, `remotion/public/*`, `remotion/out/*`, `timeline.json`, caches, or regenerated `remotion/props.json`. Recommended commit message: `Document completed TSMC visual asset pack`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The source directory for manually supplied local visual files is `assets/visuals/`. A local source file should be named by scene id, such as `assets/visuals/scene_017.mp4`. The prepared public directory for Remotion is `remotion/public/visuals/`. The existing command `synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` copies source files into that public directory and annotates `remotion/props.json` with public paths such as `visuals/scene_017.mp4`.

A target scene means a scene in `remotion/props.json` whose `visual_type` is `AI_VIDEO` or `B_ROLL`. Those are the only scene types considered by `prepare-visual-assets`. Other scene types, such as `CHART` and `TABLE`, render from structured `visual.data` and are not part of this local visual asset pack.

A public path means a path relative to `remotion/public/`, for example `visuals/scene_017.mp4`. Remotion uses this path with `staticFile()` to load images or videos. The Remotion asset components already support local visual paths and fall back to placeholders when no prepared path exists.

The supported local visual extensions are `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, and `.mov`. The match is case-insensitive. Each target scene must have exactly one supported file. If both `assets/visuals/scene_017.mp4` and `assets/visuals/scene_017.png` exist, the workflow should stop and report the duplicate instead of preparing ambiguous assets.

`assets/visuals/`, `remotion/public/`, `remotion/out/`, and `timeline.json` are ignored by git. `remotion/props.json` can be modified during validation but should not be committed unless explicitly approved.

## Current Context

Phase 18 validated the first three local visual assets: `scene_001`, `scene_003`, and `scene_004`. Phase 19 expanded the validated set to eight scenes by adding `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`. The manifest records all eight as `prepared-local`, with actual filenames under `assets/visuals/` and provenance `unknown-local`.

Phase 20 completes the remaining nine targets:

- `scene_017`
- `scene_020`
- `scene_022`
- `scene_025`
- `scene_027`
- `scene_029`
- `scene_030`
- `scene_031`
- `scene_033`

When all 17 target scenes are present and prepared, `inspect-visual-assets remotion/props.json` should report `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight should report `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, and `file_errors: 0`. The overall preflight status may be `warning` if unrelated root props warnings remain, such as the known `07_CONCLUSION` timing gap warning, but visual asset readiness itself should be complete.

## Remaining Target Scene Table

The remaining Phase 20 targets are listed below. Current manifest status is the status before Milestone 1 updates.

| scene_id | section_key | visual_type | current manifest status | expected filename | recommended asset type | production brief | provenance placeholder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `scene_017` | `04_MECHANISM_2` | `B_ROLL` | `needed` | `assets/visuals/scene_017.mp4` | Video preferred; motion graphic ideal. | Show the EUV process: 13.5nm light in a vacuum chamber, mirrors, tin plasma, wafer projection, and a circuit pattern forming. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_020` | `05_MECHANISM_3` | `B_ROLL` | `needed` | `assets/visuals/scene_020.mp4` | Video preferred; montage or licensed clips. | Quick cuts of semiconductor/product leaders or presentations freezing to grayscale with manufacturing attribution to TSMC. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_022` | `05_MECHANISM_3` | `B_ROLL` | `needed` | `assets/visuals/scene_022.mp4` | Video preferred; locally built motion graphic acceptable. | Animate major company logos or generic labeled nodes converging toward a central TSMC point like planets orbiting a star. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_025` | `06_MECHANISM_4` | `AI_VIDEO` | `needed` | `assets/visuals/scene_025.mp4` | Video preferred; stylized geopolitical motion graphic. | Satellite-style Taiwan view with the Taiwan Strait, stylized warships on one side, and Taiwan glowing with data-center-like blue light. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_027` | `06_MECHANISM_4` | `B_ROLL` | `needed` | `assets/visuals/scene_027.mp4` | Video preferred; licensed/manual-source likely. | TSMC Arizona fab construction in Phoenix with desert setting, white structures, workers in hard hats, and US/Taiwan flag context. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_029` | `06_MECHANISM_4` | `B_ROLL` | `needed` | `assets/visuals/scene_029.mp4` | Video preferred; map/motion graphic acceptable. | Split-screen ASML/EUV export restriction visual with a world map, red restriction lines, and China highlighted as restricted. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_030` | `07_CONCLUSION` | `AI_VIDEO` | `needed` | `assets/visuals/scene_030.mp4` | Video preferred; cinematic still acceptable for validation. | Slow sunrise aerial over the Taiwan Strait, calm water, golden light, and Taiwan visible at the edge. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_031` | `07_CONCLUSION` | `B_ROLL` | `needed` | `assets/visuals/scene_031.mp4` | Video preferred; staged or licensed event footage. | Morris Chang-like elderly speaker at a podium before engineers and executives, with a trust/innovation/customer slide. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |
| `scene_033` | `07_CONCLUSION` | `AI_VIDEO` | `needed` | `assets/visuals/scene_033.mp4` | Video preferred; still fallback can work. | Final cleanroom wafer shot reflecting overhead lights, slow zoom, fade to black, and final closing-title mood. | TBD: `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. |

## Completion Rationale

The previous local asset phases intentionally stopped before completing all target scenes so the workflow could be validated in small, reversible steps. Phase 20 is the completion phase: it aims to remove every visual-missing warning for `AI_VIDEO` and `B_ROLL` scenes while staying within the existing local-file workflow.

Completing all 17 visuals matters because it gives the TSMC sample a full local visual pass without relying on placeholder cards for AI/B-roll scenes. It also gives preflight a cleaner signal: remaining warnings should be unrelated timeline warnings, not missing visual asset warnings.

## Asset Production Boundary

Real assets are produced manually or by external tools outside SyncCut. SyncCut only validates, copies, and references local files that already exist under `assets/visuals/`.

Do not generate AI media inside this repository. Do not call image or video generation APIs from this repository. Do not download, fetch, scrape, or license B-roll inside this repository. Do not call `ffmpeg` or `ffprobe`. Do not probe, decode, transcode, normalize, trim, or inspect media contents. Do not edit Python source, Remotion source, schemas, npm scripts, command behavior, or render scripts. Do not commit binary visual assets, generated public copies, render outputs, or temporary prepared `remotion/props.json` changes.

When provenance is known, record it in `docs/tsmc-visual-asset-manifest.md` using a concise category. Valid categories are `original/manual`, `external-generated`, `licensed/manual-source`, or `unknown-local`. Avoid private license details, credentials, raw generation payloads, or embedded media.

## Plan of Work

Milestone 1 is documentation-only. Update `docs/tsmc-visual-asset-manifest.md` so `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033` are marked `planned`. Preserve the existing `prepared-local` status for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, and `scene_015`. Add or refine production notes for the nine remaining targets with expected filenames, video-preferred guidance, and provenance placeholders. Do not create media files and do not touch `assets/visuals/`.

Milestone 2 begins only after the user or an external process places real files for the remaining scenes under `assets/visuals/`. Inspect `assets/visuals/` and confirm that all 17 target scenes have exactly one supported local file each. Stop and report missing files or duplicates before running preparation. Regenerate timeline and props, prepare audio, inspect visual readiness before visual preparation, run `prepare-visual-assets`, inspect visual readiness after preparation, run verified preflight, run Remotion typecheck, and run Python tests. If a remaining scene prepares successfully, update its manifest status to `prepared-local`, record the actual filename used, and set provenance to the known category or `unknown-local`.

Milestone 3 is render preview. Use only existing render commands. Prefer `npm run render:segment:local` from `remotion/` first because it validates the full prepared asset set in a bounded 900-frame render. If the user explicitly approves and time allows, run `npm run render:final:local` to validate the full composition. If Chrome launch is blocked by sandbox permissions, record the exact error and rerun with Chrome launch permission if available. Do not add workaround code, do not add render scripts, and do not call Remotion from Python. Record output paths and sizes if preview or full render outputs are produced.

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

After all 17 expected local source files exist, run:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected readiness after visual preparation is:

    target_scenes: 17
    prepared: 17
    missing: 0
    unsupported: 0

Expected verified preflight fields after visual preparation are:

    visual_prepared: 17
    visual_missing: 0
    visual_unsupported: 0
    errors: 0
    verify_files: true
    file_errors: 0

The overall preflight status may be `warning` if unrelated root props warnings remain. With the current sample, the known unrelated warning is the `07_CONCLUSION` gap warning.

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

Optional full render only when explicitly approved or practical:

    cd remotion
    npm run render:final:local
    ls -lh out/final.mp4
    cd ..

Artifact review:

    git status --short --ignored

## Validation and Acceptance

Milestone 1 is accepted when `docs/tsmc-visual-asset-manifest.md` marks the nine remaining targets as `planned`, keeps the previous eight rows as `prepared-local`, and records expected filenames, production notes, and provenance placeholders without creating media files.

Milestone 2 is accepted when all 17 target scenes have exactly one supported local file, `prepare-visual-assets` prepares 17 visual assets, `inspect-visual-assets` reports `prepared: 17`, `missing: 0`, and `unsupported: 0`, verified preflight reports `visual_missing: 0`, `errors: 0`, and `file_errors: 0`, Remotion typecheck passes, and pytest passes.

Milestone 3 is accepted when the existing segment preview succeeds and writes an ignored `remotion/out/segment.mp4`, or fails only because of documented browser-launch sandbox limits. If full render is attempted, it is accepted when `remotion/out/final.mp4` is produced or when an exact environment/runtime limitation is recorded. Successful previews should record output size. Sandbox failures should record the exact error and should not trigger code or configuration changes.

Milestone 4 is accepted when `remotion/props.json` is cleaned from local visual public paths, clean `inspect-visual-assets` returns the baseline missing-only state, clean verified preflight has `errors: 0` and `file_errors: 0`, generated artifacts remain ignored, and commit candidates are documentation only.

## Risks

Duplicate files are the most likely local workflow error. If more than one supported file exists for the same scene id, stop before preparation and report the duplicates.

Unsupported extensions are ignored by `prepare-visual-assets`. If a scene appears missing even though a file exists, check whether the extension is one of `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, or `.mov`.

Large media files may slow public directory copying and rendering. The local source and prepared public files should remain ignored unless a separate explicit media commit policy is approved.

Rights and provenance may be ambiguous. Use `unknown-local` when the local file is available but its production source is not established, and do not include private license details or credentials in docs.

Chrome can fail to launch in sandboxed environments. The known failure mode is `SIGTRAP` with `setsockopt: Operation not permitted`. Record the error and rerun with Chrome launch permission if available; do not add workaround code.

`remotion/props.json` will be modified by `prepare-visual-assets`. Clean it during Milestone 4 before final artifact review unless the user explicitly approves committing prepared local visual paths.

The full final render can take longer than a segment render and can produce a large ignored output. Prefer segment render first, and only attempt final render when the user approves or the environment and time budget make it practical.

## Explicit Exclusions

Do not edit Python source. Do not edit Remotion source. Do not edit schemas. Do not change command behavior. Do not add or change render scripts. Do not generate AI media inside the repo. Do not download, fetch, or scrape B-roll or other media inside the repo. Do not call `ffmpeg` or `ffprobe`. Do not probe, transcode, normalize, trim, or inspect media contents. Do not commit binary media. Do not commit generated public assets. Do not commit render outputs. Do not commit `remotion/props.json` unless explicitly approved. Do not commit or tag unless explicitly asked.

## Idempotence and Recovery

The workflow is safe to rerun. `build-timeline`, `export-remotion`, and `prepare-remotion-assets` restore a clean props baseline. `prepare-visual-assets` can be rerun after local files change; it copies missing files, reuses identical destination files, and overwrites changed destination files while reporting counts.

If preparation fails due duplicates, remove or move the duplicate ignored local file outside `assets/visuals/`, then rerun. Do not delete local assets automatically unless the user explicitly asks. If verified preflight reports `missing_public_file`, rerun `prepare-visual-assets` and confirm the copied file exists under `remotion/public/visuals/`. If `remotion/props.json` is accidentally left modified after validation, rerun `export-remotion` and `prepare-remotion-assets` without `prepare-visual-assets` to restore the clean sample state.

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
    assets/visuals/scene_017.<supported-ext>
    assets/visuals/scene_020.<supported-ext>
    assets/visuals/scene_022.<supported-ext>
    assets/visuals/scene_025.<supported-ext>
    assets/visuals/scene_027.<supported-ext>
    assets/visuals/scene_029.<supported-ext>
    assets/visuals/scene_030.<supported-ext>
    assets/visuals/scene_031.<supported-ext>
    assets/visuals/scene_033.<supported-ext>

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

    docs/plans/tsmc-complete-real-visual-assets.md
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
    npm run render:final:local

No Python command should invoke Remotion. Remotion rendering remains a local developer workflow under `remotion/`.

## Change Note

Created on 2026-05-13 to plan Phase 20. The plan is documentation-only at creation time and records how to complete the final nine local TSMC visual assets while preserving the existing source-code and artifact boundaries.
