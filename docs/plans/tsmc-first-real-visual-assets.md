# Produce and validate the first real local TSMC visual assets

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to produce, place, validate, and review the first real local visual assets for the TSMC sample from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already render the TSMC sample end to end, but `AI_VIDEO` and `B_ROLL` scenes still render placeholders unless local visual files are present. This phase replaces placeholders for a small first subset of target scenes with real local files supplied outside SyncCut, then proves the existing asset workflow can copy those files into Remotion's public directory, annotate `remotion/props.json`, report readiness, pass verified preflight, type-check the Remotion project, and optionally render a short preview segment.

After this phase, a maintainer should be able to place a small number of real visual files under `assets/visuals/`, run `synccut prepare-visual-assets`, see the selected scenes reported as prepared, and confirm the remaining missing `AI_VIDEO` and `B_ROLL` assets are warnings rather than blockers. This phase must not add source-code features, change command behavior, change schemas, call ffmpeg or ffprobe, probe or transcode media, download or scrape B-roll, generate AI media inside the repo, invoke Remotion from Python, add a GUI or web app, or commit large media by default.

## Progress

- [x] (2026-05-12T20:50:19+07:00) Read the requested project guidance and current Remotion/asset documentation, inspected the current target scenes in `remotion/props.json`, inspected the local visual asset helpers and preflight helpers, inspected the Remotion visual asset components, and created this ExecPlan.
- [x] (2026-05-12T20:57:20+07:00) Completed Milestone 1: selected `scene_001`, `scene_003`, and `scene_004` as the required first real subset, marked `scene_006` and `scene_008` as optional next targets, and updated `docs/tsmc-visual-asset-manifest.md` with planned status and production notes without creating media files.
- [x] (2026-05-12T21:27:17+07:00) Completed Milestone 2: validated the first three local `.mp4` assets under `assets/visuals/`, prepared them into `remotion/public/visuals/`, confirmed readiness and verified preflight counts, ran Remotion typecheck, ran Python tests, and updated the manifest to `prepared-local`.
- [x] (2026-05-12T21:46:25+07:00) Completed Milestone 3: regenerated props and assets, prepared the three visual files, verified preflight, ran Remotion typecheck, rendered the 0-899 frame segment with local Chrome after sandbox escalation, ran Python tests, and recorded artifact status.
- [x] (2026-05-12T21:53:48+07:00) Completed Milestone 4: cleaned `remotion/props.json`, verified clean visual readiness and verified preflight, reran Remotion typecheck and Python tests, reviewed artifacts, and wrote the final commit recommendation.

## Surprises & Discoveries

- Observation: The user-suggested `scene_005` and `scene_007` are not visual-asset targets in the current props.
  Evidence: `remotion/props.json` shows `scene_005` has `visual_type` `CHART` and `scene_007` has `visual_type` `TABLE`. The existing `synccut prepare-visual-assets` command only considers `AI_VIDEO` and `B_ROLL` scenes.
- Observation: The current TSMC sample has 17 visual-asset target scenes.
  Evidence: Inspecting `remotion/props.json` found 6 `AI_VIDEO` scenes and 11 `B_ROLL` scenes: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: The current Remotion components already support local visual public paths.
  Evidence: `remotion/src/components/VisualAssetScene.tsx` uses `staticFile(publicPath)` and renders images with `Img` or videos with `OffthreadVideo`, falling back to `PlaceholderScene` when `visual.public_path` is absent or unsupported.
- Observation: Milestone 1 did not require any media generation or validation runs.
  Evidence: The only requested changes were to `docs/tsmc-visual-asset-manifest.md` and this ExecPlan. No files were created under `assets/visuals/`, no source files changed, and no render commands were run.
- Observation: The first selected real subset exists locally with exactly one supported file per selected scene id.
  Evidence: Inspection of `assets/visuals/` found `assets/visuals/scene_001.mp4`, `assets/visuals/scene_003.mp4`, and `assets/visuals/scene_004.mp4`; no duplicate supported files were found for these selected scene ids. Optional `scene_006` and `scene_008` assets were not present and were not required for this milestone.
- Observation: `prepare-visual-assets` reused existing prepared public copies for the selected assets.
  Evidence: The command reported `visual_copied: 0`, `visual_reused: 3`, `visual_overwritten: 0`, `visual_missing: 14`, and `visual_assets: 3`.
- Observation: Verified preflight passed with warnings only after preparing the first subset.
  Evidence: Preflight reported `status: warning`, `visual_prepared: 3`, `visual_missing: 14`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: `remotion/props.json` was cleaned after validation so it is not a commit candidate.
  Evidence: After artifact review showed `remotion/props.json` modified by visual preparation, `export-remotion` and `prepare-remotion-assets` were rerun without `prepare-visual-assets`. A follow-up readiness report returned to `prepared: 0`, `missing: 17`, `unsupported: 0`, and `git status --short --ignored` no longer listed `remotion/props.json`.
- Observation: The first segment render attempt failed only because local Chrome was blocked by sandbox permissions.
  Evidence: `npm run render:segment:local` exited with `Error: Failed to launch the browser process!`, `Closed with null signal: SIGTRAP`, and `[ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`.
- Observation: The same segment render succeeded when rerun with Chrome launch permission.
  Evidence: The escalated `npm run render:segment:local` rendered frames `0-899`, encoded `900/900`, and wrote `out/segment.mp4`. `ls -lh out/segment.mp4` reported `33M`.
- Observation: The segment render copied a larger public directory than prior audio-only runs because the prepared visual assets were included.
  Evidence: Render output reported public dir copy progress up to `41.7 MB` before rendering, and the final segment output was reported by Remotion as `34.3 MB`.
- Observation: Final cleanup restored `remotion/props.json` to an audio-prepared, no-visual-path sample state.
  Evidence: After rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` without `prepare-visual-assets`, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`; `git status --short --ignored` did not list `remotion/props.json`.
- Observation: Final artifact review shows only documentation commit candidates.
  Evidence: `git status --short --ignored` listed `docs/tsmc-visual-asset-manifest.md` modified and `docs/plans/tsmc-first-real-visual-assets.md` untracked. Generated/local paths were ignored: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `synccut/__pycache__/`, `tests/__pycache__/`, and `timeline.json`.

## Decision Log

- Decision: Treat `scene_001`, `scene_003`, and `scene_004` as the required first real subset.
  Rationale: They are the first three target scenes in props order and cover both supported placeholder types: one `AI_VIDEO` and two `B_ROLL` scenes. A three-scene subset is small enough to validate quickly while demonstrating the full path from local files to Remotion rendering.
  Date/Author: 2026-05-12 / Codex
- Decision: If the subset expands to four or five scenes, use `scene_006` and `scene_008`, not `scene_005` or `scene_007`.
  Rationale: `scene_006` and `scene_008` are the next `B_ROLL` and `AI_VIDEO` targets in scene order. `scene_005` and `scene_007` are data-driven `CHART` and `TABLE` scenes already rendered from `visual.data`, so the local visual asset copy command will ignore them.
  Date/Author: 2026-05-12 / Codex
- Decision: Prefer `.mp4` for the first real assets, while allowing supported image formats if production only supplies stills.
  Rationale: The manifest prompts for these scenes describe motion or montage-like footage. Video files best exercise the current `OffthreadVideo` path, but the existing command and Remotion renderer also support `.png`, `.jpg`, `.jpeg`, and `.webp` for still assets.
  Date/Author: 2026-05-12 / Codex
- Decision: Keep real asset production outside SyncCut and outside this repository's implementation work.
  Rationale: The phase is about local asset placement and validation. SyncCut should copy and reference local files only; it must not generate, download, scrape, probe, transcode, normalize, or license media.
  Date/Author: 2026-05-12 / Codex
- Decision: Use `planned`, `optional-planned`, and `needed` as the manifest status convention.
  Rationale: `planned` identifies the selected required first subset, `optional-planned` identifies the next recommended two targets if the subset expands, and `needed` remains the default for the rest of the 17 known target scenes. This keeps the manifest text-only while making production priority clear.
  Date/Author: 2026-05-12 / Codex
- Decision: Record the selected prepared files with provenance `unknown-local`.
  Rationale: The local files were present under `assets/visuals/` and validated successfully, but this milestone did not establish whether they are original/manual, external-generated, or licensed/manual-source. `unknown-local` accurately records that they are local and prepared without inventing provenance.
  Date/Author: 2026-05-12 / Codex
- Decision: Clean `remotion/props.json` after validation rather than leaving prepared visual paths as a commit candidate.
  Rationale: The milestone needed to validate the workflow, but the user explicitly stated that `remotion/props.json` should not be committed unless approved and that commit candidates should be docs only. Regenerating props and audio preparation preserves a clean sample props state while the ignored local assets remain available for future preparation.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the relevant project guidance and inspecting the current props, asset helpers, preflight helpers, and Remotion visual asset components. No source code, schema, command behavior, media file, generated artifact, render output, commit, or tag has been changed.

The immediate next milestone is a documentation-only asset brief. It should update `docs/tsmc-visual-asset-manifest.md` to mark the selected first subset as planned and record concise production notes. Actual real media placement happens later, after a human or an external production tool creates files outside SyncCut and places them under `assets/visuals/`.

Milestone 1 is complete. `docs/tsmc-visual-asset-manifest.md` now marks `scene_001`, `scene_003`, and `scene_004` as `planned`, marks `scene_006` and `scene_008` as `optional-planned`, and defines the status convention used by the table. The selected rows now include expected `.mp4` filenames, video-preferred guidance, provenance placeholders, and concise production notes. The manifest also explicitly notes that `scene_005` and `scene_007` are `CHART` and `TABLE` data-driven scenes, not `prepare-visual-assets` targets.

No media files were created, no files under `assets/visuals/` were created, no source files or schemas were edited, no command behavior changed, no Remotion props were edited, no render was run, and no commit was made. The next step waits for the user or an external production process to place real local assets under `assets/visuals/`.

Milestone 2 is complete. The required selected files were present as `assets/visuals/scene_001.mp4`, `assets/visuals/scene_003.mp4`, and `assets/visuals/scene_004.mp4`, with no duplicate supported files for those scene ids. Optional `scene_006` and `scene_008` were not present and were correctly treated as optional.

The clean regeneration workflow succeeded. `build-timeline` wrote `timeline.json`; `validate-timeline` passed with the known `07_CONCLUSION` gap warning; `export-remotion` wrote `remotion/props.json` with 33 scenes, 7 sections, 30 fps, 22584 frames, and 1 warning; and `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`.

Before visual preparation, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. After running `prepare-visual-assets`, the command reported `visual_copied: 0`, `visual_reused: 3`, `visual_overwritten: 0`, `visual_missing: 14`, `visual_assets: 3`, and `public_dir: remotion/public`. The follow-up readiness report showed `scene_001`, `scene_003`, and `scene_004` prepared with public paths `visuals/scene_001.mp4`, `visuals/scene_003.mp4`, and `visuals/scene_004.mp4`.

Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 3`, `visual_missing: 14`, `visual_unsupported: 0`, `warnings: 15`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The remaining warnings are the known root props warning plus 14 missing optional visual assets that still render placeholders.

Remotion typecheck passed from `remotion/` with `npm run typecheck`. Python tests passed from the repository root with `.venv/bin/python -m pytest`, collecting 208 tests and passing all 208 in 0.51s.

`docs/tsmc-visual-asset-manifest.md` now marks the three selected rows as `prepared-local`, records their actual filenames, and uses provenance `unknown-local` because the local files were validated but their production source was not established in this milestone. No Python source, Remotion source, schemas, or command behavior changed. No render was run. No commit or tag was created. Generated and local asset artifacts remain ignored and should not be committed.

Artifact review initially showed `remotion/props.json` as a generated non-ignored change because `prepare-visual-assets` annotated the three prepared visual paths. To keep commit candidates docs-only, `export-remotion` and `prepare-remotion-assets` were rerun without visual preparation. Current `inspect-visual-assets remotion/props.json` is therefore back to the clean sample state: `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. The validated source assets remain under ignored `assets/visuals/`, and prepared public copies remain under ignored `remotion/public/visuals/`.

Milestone 3 is complete. The validation workflow regenerated `timeline.json`, validated it with the known `07_CONCLUSION` gap warning, exported `remotion/props.json`, prepared 7 audio assets, and prepared the three local visual assets again. `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 3`, `visual_overwritten: 0`, `visual_missing: 14`, and `visual_assets: 3`.

Before rendering, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 3`, `missing: 14`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 3`, `visual_missing: 14`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

Remotion typecheck passed with `npm run typecheck`. The first `npm run render:segment:local` attempt failed due sandbox browser-launch limits with `SIGTRAP` and `setsockopt: Operation not permitted`. The same command was rerun with Chrome launch permission and succeeded, rendering the fixed 900-frame local segment to `remotion/out/segment.mp4`. The output file exists and `ls -lh out/segment.mp4` reported `33M`; Remotion reported `out/segment.mp4 34.3 MB` at completion. The optional still check was not run because the segment render already validated the preview path for the prepared assets.

Python tests passed after the render preview: `.venv/bin/python -m pytest` collected 208 tests and all 208 passed in 0.51s.

Artifact review after Milestone 3 showed documentation changes plus generated artifacts. `git status --short --ignored` listed `docs/tsmc-visual-asset-manifest.md` modified, `docs/plans/tsmc-first-real-visual-assets.md` untracked, and `remotion/props.json` modified because visual preparation annotated the three prepared public paths for the preview. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `synccut/__pycache__/`, `tests/__pycache__/`, and `timeline.json`. Do not commit `remotion/props.json`, `remotion/out/segment.mp4`, `remotion/public/visuals/*`, `assets/visuals/*`, or other ignored generated artifacts unless explicitly approved.

Milestone 4 is complete. `remotion/props.json` was cleaned from prepared visual paths by rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` without rerunning `prepare-visual-assets`. The cleanup validation matched expectations: `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

Final validation passed. `npm run typecheck` from `remotion/` completed successfully. `.venv/bin/python -m pytest` collected 208 tests and all 208 passed in 0.54s.

The final review checklist is satisfied. The work stayed within Phase 18 scope. Real files were supplied locally under `assets/visuals/`; SyncCut did not generate AI media; SyncCut did not download, fetch, or scrape B-roll or other external media; no direct `ffmpeg` or `ffprobe` commands were called; no media probing, transcoding, or normalization was performed; no Python source, Remotion source, schema, or command behavior changed; the prepared subset `scene_001`, `scene_003`, and `scene_004` was validated; readiness after preparation reached `prepared: 3`, `missing: 14`, and `unsupported: 0`; preflight after preparation had `errors: 0` and `file_errors: 0`; segment render preview succeeded with Chrome launch permission; clean props were restored after preview validation; generated media, public copies, render artifacts, and `timeline.json` remain ignored; and the manifest records `scene_001`, `scene_003`, and `scene_004` as `prepared-local`.

Risks remain outside SyncCut's code path. The manifest records provenance as `unknown-local`, so a human still needs to confirm whether each asset is original/manual, external-generated, or licensed/manual-source before public release. The clean committed `remotion/props.json` does not include prepared visual public paths, so anyone who wants to preview these assets must rerun `prepare-visual-assets` locally. Chrome rendering can still require sandbox/browser-launch permission, as shown by the initial `SIGTRAP` and `setsockopt: Operation not permitted` failure before the successful escalated segment render.

Final artifact review is clean for commit. `git status --short --ignored` shows only documentation commit candidates: `docs/tsmc-visual-asset-manifest.md` and `docs/plans/tsmc-first-real-visual-assets.md`. Ignored generated/local artifacts include `assets/visuals/*`, `remotion/public/*`, `remotion/out/*`, `timeline.json`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories. `remotion/props.json` is not a commit candidate and should not be committed for this phase.

Recommendation: commit only `docs/tsmc-visual-asset-manifest.md` and `docs/plans/tsmc-first-real-visual-assets.md`. Recommended commit message: `Document first TSMC real visual asset validation`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI package under `synccut/` and a standalone Remotion project under `remotion/`.

The Python CLI command `synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` is the existing local visual asset preparation command. It reads `remotion/props.json`, considers only scenes whose `visual_type` is `AI_VIDEO` or `B_ROLL`, looks for exactly one supported file named after the scene id under `assets/visuals/`, copies it into `remotion/public/visuals/`, and annotates the scene's `visual` object with a Remotion public path such as `visuals/scene_001.mp4`. A "public path" means a path relative to Remotion's `public` directory that can be used by Remotion's `staticFile()` helper.

The readiness command `synccut inspect-visual-assets remotion/props.json` reports how many `AI_VIDEO` and `B_ROLL` scenes are `prepared`, `missing`, or `unsupported`. `prepared` means the scene has `visual.asset_status` set to `prepared` and a safe supported `visual.public_path`. `missing` means no local visual has been prepared and the Remotion component will render a placeholder. `unsupported` means the props claim an asset but the public path is unsafe or unsupported.

The preflight command `synccut preflight remotion/props.json --verify-files --public-dir remotion/public` checks render readiness from props and, when `--verify-files` is set, confirms prepared public paths resolve to actual files under `remotion/public`. Missing optional `AI_VIDEO` and `B_ROLL` assets are warnings because placeholders can render. Prepared but missing or malformed public files are errors.

The Remotion components `remotion/src/components/AiVideoScene.tsx` and `remotion/src/components/BRollScene.tsx` are thin wrappers around `remotion/src/components/VisualAssetScene.tsx`. `VisualAssetScene.tsx` validates `scene.visual.public_path`, loads images through `Img` and videos through `OffthreadVideo`, and falls back to `PlaceholderScene` when no supported local asset is available.

The current TSMC visual asset manifest is `docs/tsmc-visual-asset-manifest.md`. It is a text-only production document for target scene IDs, expected filenames, prompt summaries, status, and notes. Actual asset files live under `assets/visuals/`, which is ignored by git. Prepared public copies live under `remotion/public/visuals/`, which is also ignored by git.

## Selected Target Scenes

The first required subset is three scenes:

- `scene_001` is an `AI_VIDEO` scene in section `01_HOOK`. The prompt asks for an extreme close-up of a silicon wafer rotating under blue cleanroom light, with mirror-like reflections and an advanced semiconductor mood. The expected filename is `assets/visuals/scene_001.mp4`. The recommended asset type is video because the prompt describes rotation and motion. A still image such as `assets/visuals/scene_001.png` is acceptable only if a true video is not yet available, but only one supported file may exist for the scene at validation time.
- `scene_003` is a `B_ROLL` scene in section `01_HOOK`. The prompt asks for an aerial shot of TSMC's Hsinchu Science Park campus at dusk with fabrication halls, mountains, and coastal context. The expected filename is `assets/visuals/scene_003.mp4`. The recommended asset type is licensed or original video. Source licensing is handled outside SyncCut.
- `scene_004` is a `B_ROLL` scene in section `02_INTRO`. The prompt asks for a news-style montage including Jensen Huang holding a chip, an iPhone launch, a military satellite, and a self-driving car. The expected filename is `assets/visuals/scene_004.mp4`. The recommended asset type is video. This asset may require manual editorial assembly and careful rights review outside SyncCut.

If the phase expands to five scenes, add these two actual target scenes:

- `scene_006` is a `B_ROLL` scene in section `02_INTRO`. The prompt asks for a grain of sand falling into a researcher's hand, cutting to a gleaming silicon wafer under lab light. The expected filename is `assets/visuals/scene_006.mp4`. The recommended asset type is video, although a strong still can be used for an early validation pass.
- `scene_008` is an `AI_VIDEO` scene in section `03_MECHANISM_1`. The prompt asks for stylized black-and-white 1987 footage of a Taiwanese government minister and a silver-haired engineer shaking hands over a contract. The expected filename is `assets/visuals/scene_008.mp4`. The recommended asset type is externally produced video or a manually created still/video illustration. SyncCut must not generate it.

`scene_005` and `scene_007` are intentionally excluded from this asset subset. They are `CHART` and `TABLE` scenes, not `AI_VIDEO` or `B_ROLL`. They are already rendered by data-driven Remotion components from `visual.data`, and `prepare-visual-assets` will not copy files for them.

## Asset Production Boundary

SyncCut is not the production tool for these real assets. A human editor or an external tool may create or source assets outside this repository, but the repository work must only validate and reference files that already exist locally.

Do not generate AI video or images inside this repo. Do not call image or video generation APIs. Do not download, scrape, or fetch B-roll. Do not call `ffmpeg`, `ffprobe`, or any media probing, transcoding, normalization, or trimming command. Do not add Python code that invokes Remotion. Do not change the timeline or Remotion props schemas. Do not add a GUI or web app.

For provenance, update `docs/tsmc-visual-asset-manifest.md` with brief source notes such as `original/manual`, `external-generated`, or `licensed/manual-source`. Avoid storing sensitive license details, API credentials, raw generation prompts beyond the existing prompt summary, or large media metadata in the repo. The manifest should remain text-only.

## Plan of Work

Milestone 1 is documentation-only. Update `docs/tsmc-visual-asset-manifest.md` so `scene_001`, `scene_003`, and `scene_004` are marked as `planned` instead of `needed`, and add production notes that identify the intended asset type, expected filename, and provenance category to fill in later. If the user wants a five-scene subset, also mark `scene_006` and `scene_008` as planned. Do not create or edit any file under `assets/visuals/`.

Milestone 2 begins only after real local files have been placed under `assets/visuals/` by the user or another external process. Regenerate `timeline.json`, `remotion/props.json`, and audio public assets; inspect visual readiness before preparing visuals; verify that the intended real files exist locally; run `prepare-visual-assets`; inspect visual readiness again; run verified preflight; run Remotion typecheck; run Python tests; and record exact counts and artifact status. If stale synthetic assets from earlier validation still exist under `assets/visuals/`, review the directory before running `prepare-visual-assets` and ensure only intended real files for the selected scene IDs are used. Do not delete files automatically unless the user explicitly asks; local ignored asset cleanup is a human-controlled step.

Milestone 3 is optional preview rendering. If Chrome launch permission and time allow, render a still, smoke video, or segment video using the existing npm scripts from `remotion/`. Prefer `npm run render:smoke:local` or `npm run render:segment:local` for this phase. Do not render the final full video unless explicitly requested later. Record the command, result, output path, and file size if output is created. Generated render outputs under `remotion/out/` must remain uncommitted.

Milestone 4 is final review. Confirm no source code, schema, or command behavior changed; no generation/download/probing/transcoding happened; generated media and public copies are ignored; `remotion/props.json` is not recommended for commit unless there is an intentional sample refresh; and the only normal commit candidates are text documentation such as this plan and the manifest.

## Concrete Steps

From the repository root, validate the clean starting point before real visual asset preparation:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json

Expected clean visual readiness before placing or preparing the first real subset:

    target_scenes: 17
    prepared: 0
    missing: 17
    unsupported: 0

Place real files manually under `assets/visuals/` using exactly one supported file per selected scene id. For the three-scene subset, the preferred files are:

    assets/visuals/scene_001.mp4
    assets/visuals/scene_003.mp4
    assets/visuals/scene_004.mp4

If using image files for early validation, replace `.mp4` with one of `.png`, `.jpg`, `.jpeg`, or `.webp`. Do not keep both `scene_001.mp4` and `scene_001.png` at the same time, because duplicate supported files for one scene id should fail clearly.

Prepare and validate visual readiness:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected result for exactly three valid prepared assets:

    inspect-visual-assets:
      target_scenes: 17
      prepared: 3
      missing: 14
      unsupported: 0

    preflight:
      status: warning
      visual_prepared: 3
      visual_missing: 14
      visual_unsupported: 0
      errors: 0
      verify_files: true
      file_errors: 0

Expected result for exactly five valid prepared assets:

    inspect-visual-assets:
      target_scenes: 17
      prepared: 5
      missing: 12
      unsupported: 0

    preflight:
      status: warning
      visual_prepared: 5
      visual_missing: 12
      visual_unsupported: 0
      errors: 0
      verify_files: true
      file_errors: 0

Run project validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

Optional short preview, only if Chrome launch permission and time allow:

    cd remotion
    npm run still:local
    npm run render:smoke:local
    npm run render:segment:local
    cd ..

Run artifact review:

    git status --short --ignored

The expected non-ignored commit candidates should be text documentation only. Ignored generated or local asset paths may include `assets/visuals/`, `remotion/public/`, `remotion/out/`, `timeline.json`, `.venv/`, `remotion/node_modules/`, `__pycache__/`, and `.pytest_cache/`.

## Validation and Acceptance

The phase is accepted when `scene_001`, `scene_003`, and `scene_004` have real local files under `assets/visuals/`, `prepare-visual-assets` copies them into `remotion/public/visuals/`, and `inspect-visual-assets` reports `prepared: 3`, `missing: 14`, and `unsupported: 0`. If the subset is expanded to `scene_006` and `scene_008`, the accepted counts become `prepared: 5`, `missing: 12`, and `unsupported: 0`.

Verified preflight must report `errors: 0` and `file_errors: 0`. It may still report `status: warning` because the remaining unprepared `AI_VIDEO` and `B_ROLL` scenes are optional placeholder-backed visuals. Missing remaining target scenes should stay warnings, not errors.

`npm run typecheck` from `remotion/` must pass. `.venv/bin/python -m pytest` from the repository root must pass. If optional preview rendering is run, `still:local`, `render:smoke:local`, or `render:segment:local` should use existing local Chrome scripts and produce ignored files under `remotion/out/`. If Chrome launch fails due sandbox permission, record the exact error and do not add workaround code.

No source files under `synccut/` or `remotion/src/` should change. No schema files should change. No command behavior should change. No media files should be staged or recommended for commit.

## Idempotence and Recovery

The workflow is safe to rerun. `prepare-visual-assets` is deterministic: if a destination file is absent, it copies; if the destination exists with identical bytes, it reuses; if the destination exists with different bytes, it overwrites and reports the overwrite count. Re-running `build-timeline`, `export-remotion`, and `prepare-remotion-assets` restores a clean props baseline before visual preparation.

If `prepare-visual-assets` fails because two supported files exist for the same scene id, remove or move one of the local ignored files outside the repo and rerun. For example, do not keep both `assets/visuals/scene_003.mp4` and `assets/visuals/scene_003.png`.

If preflight reports `missing_public_file`, confirm that `prepare-visual-assets` was run after the real asset was placed and that `remotion/public/visuals/<scene_id>.<ext>` exists. If preflight reports an unsupported visual path, regenerate props and rerun asset preparation rather than editing `remotion/props.json` by hand.

If a render command fails because Chrome launch is blocked, record the exact error. Do not change source code or add workarounds in this phase.

## Artifacts and Notes

The source asset directory is:

    assets/visuals/

The prepared public copy directory is:

    remotion/public/visuals/

Both directories are ignored by git and should not be committed by default. Render outputs under `remotion/out/` and generated `timeline.json` are also ignored. `remotion/props.json` may be rewritten during validation, but it should not be committed unless an intentional sample props refresh is explicitly approved.

The text-only production manifest is:

    docs/tsmc-visual-asset-manifest.md

It may be committed if updated with planned or validated status and source notes. It must not embed binary media, private license data, API credentials, or generated media payloads.

## Interfaces and Dependencies

No new Python or npm dependencies are required.

The existing Python command interface used by this phase is:

    synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    synccut inspect-visual-assets remotion/props.json
    synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The existing Remotion public asset interface used by this phase is `staticFile(publicPath)`, where `publicPath` is a safe path such as `visuals/scene_001.mp4`. In the current app, `VisualAssetScene.tsx` loads image assets with `Img` and video assets with `OffthreadVideo`. These components should not be edited for this phase unless a clear rendering bug is discovered and the user approves a scope change.

The supported visual asset extensions are:

    .png
    .jpg
    .jpeg
    .webp
    .mp4
    .webm
    .mov

Matching is by exact scene id and case-insensitive extension. A scene id with more than one supported local file is an error. Unsupported local files are ignored.
