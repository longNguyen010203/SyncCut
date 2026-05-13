# Final release render and quality review

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to prepare the final TSMC sample render, record review evidence, and clean generated state from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut v0.1 already has a working Python timeline pipeline, Remotion rendering workflows, public-file preflight checks, and a complete local visual asset pack for the TSMC sample. This phase is the final release render and quality review pass: prepare all 17 local TSMC visual assets again, prove the props are ready with verified preflight, render the full video using the existing Remotion final render script, and record whether the resulting video is ready for v0.1.0 tagging or needs polish.

After this phase, a maintainer should have a text record of the exact validation commands, final render result, output path and size, manual quality review notes, release decision, and artifact cleanup status. This phase is validation and review only. It must not add features, change source code, change schemas, change command behavior, add render scripts, generate or download media, call ffmpeg or ffprobe, probe or transcode media, commit binary media, commit generated public assets, commit render outputs, commit `remotion/props.json` unless explicitly approved, or tag a release.

## Progress

- [x] (2026-05-13T10:29:34+07:00) Read the requested project references: `AGENTS.md`, `.agent/PLANS.md`, `README.md`, `remotion/README.md`, `docs/tsmc-visual-asset-manifest.md`, `docs/plans/v0.1-release-hardening.md`, `docs/plans/tsmc-complete-real-visual-assets.md`, `remotion/package.json`, `remotion/props.json`, and `.gitignore`.
- [x] (2026-05-13T10:29:34+07:00) Confirmed the current clean props orientation: composition `SyncCutVideo`, 30 fps, 22584 frames, 33 scenes, 7 sections, 17 AI/B-roll target scenes, and the known `07_CONCLUSION` gap warning.
- [x] (2026-05-13T10:29:34+07:00) Created this ExecPlan for Phase 21 final release render and quality review.
- [x] (2026-05-13T10:37:53+07:00) Completed Milestone 1: confirmed all 17 local source assets with no duplicates, prepared all 17 visual assets, verified preflight with zero errors and file errors, passed Remotion typecheck and pytest, and left `remotion/props.json` intentionally prepared for the next render milestone.
- [x] (2026-05-13T17:03:39+07:00) Completed Milestone 2: retried the full final render with the existing `npm run render:final:local` script after the `scene_033` asset replacement, reran with Chrome launch permission after the expected sandbox failure, rendered all 22584 frames successfully, and produced `remotion/out/final.mp4`.
- [x] (2026-05-13T12:46:02+07:00) Render attempt recorded for Milestone 2: the sandboxed attempt failed at Chrome launch, the permitted Chrome attempt advanced to frame 21393, and the render then failed on `visuals/scene_033.mp4` with Remotion's compositor reporting `moov atom not found`.
- [x] (2026-05-13T14:22:45+07:00) Completed the focused Phase 21 recovery readiness step: confirmed the user-replaced `assets/visuals/scene_033.mp4` is the only supported local file for `scene_033`, regenerated props and public assets, prepared all 17 visual assets, verified preflight with zero errors and file errors, and passed Remotion typecheck and pytest. No final render was run in this recovery step.
- [x] (2026-05-13T17:15:11+07:00) Completed Milestone 3: created `docs/final-render-quality-review.md` with render evidence, quality-review checklist notes, known limitations of this non-interactive review environment, and a conservative `needs-polish` release decision pending human playback review.
- [x] (2026-05-13T17:23:59+07:00) Completed Milestone 4: cleaned `remotion/props.json` back to the no-visual-prep sample state, verified clean visual readiness and verified preflight, passed Remotion typecheck and pytest, reviewed artifacts, and confirmed docs-only commit candidates.

## Surprises & Discoveries

- Observation: The current checked props are clean rather than visually prepared.
  Evidence: `remotion/props.json` has 17 AI/B-roll target scenes and the known root warning, but Phase 20 cleanup restored props without prepared visual paths.
- Observation: The final render script already exists and renders the full composition.
  Evidence: `remotion/package.json` defines `render:final:local` as `remotion render src/index.ts SyncCutVideo out/final.mp4 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000`, with no `--frames` flag.
- Observation: Generated/local artifacts are currently ignored rather than commit candidates.
  Evidence: `git status --short --ignored` showed ignored `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.
- Observation: All 17 local visual source assets are present with exactly one supported file per target scene.
  Evidence: The local source check found no missing ids and no duplicates. It found one `.mp4` each for `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: Visual asset preparation reused every existing public copy and prepared the full set.
  Evidence: `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`.
- Observation: Final render readiness has only the known timeline warning.
  Evidence: `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 1`, `errors: 0`, `verify_files: true`, and `file_errors: 0`; the single warning is the known `07_CONCLUSION` gap.
- Observation: The first final render attempt was blocked by the sandbox before rendering.
  Evidence: Running `npm run render:final:local` from `remotion/` without extra permission failed during browser launch with `Closed with null signal: SIGTRAP` and Chromium logged `setsockopt: Operation not permitted (1)`.
- Observation: The permitted Chrome final render attempt launched and rendered most of the composition, but failed near the final section on one prepared visual asset.
  Evidence: The rerun with Chrome launch permission bundled successfully, copied the 220.6 MB public directory, selected composition `SyncCutVideo`, output `out/final.mp4`, concurrency `1x`, and rendered through frame 21393 of 22584 before failing. Remotion's internal compositor request for `visuals/scene_033.mp4` returned a 500; the error included `moov atom not found` and `Invalid data found when processing input` for a temporary copy of the scene 033 MP4. The final render command exited with code 1, so no successful final output size was recorded.
- Observation: The final render failure is being treated as an invalid local input asset for `scene_033`, not as a SyncCut source-code issue.
  Evidence: The render reached frame 21393 and failed only when Remotion attempted to load `visuals/scene_033.mp4`; the error was `moov atom not found` / `Invalid data found when processing input`, which indicates a bad MP4 container for that local asset. No Python or Remotion source changes were made.
- Observation: The user replaced `assets/visuals/scene_033.mp4`, and the replacement passed filename/extension readiness.
  Evidence: The renewed local asset check found no missing ids and no duplicate supported files across all 17 target scenes. `scene_033` has exactly one supported local file: `assets/visuals/scene_033.mp4`.
- Observation: Renewed final render readiness is clean after the `scene_033` replacement.
  Evidence: After regeneration and asset preparation, `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`; the only warning remains the known `07_CONCLUSION` gap.
- Observation: The final render retry after replacement succeeded.
  Evidence: The sandboxed retry failed at browser launch with the expected `Closed with null signal: SIGTRAP` and `setsockopt: Operation not permitted (1)` message. The same existing `npm run render:final:local` command then ran with Chrome launch permission, rendered all 22584 frames, encoded all 22584 frames, and wrote `out/final.mp4`. Remotion reported `out/final.mp4 253.4 MB`; `ls -lh out/final.mp4` reported `242M`.
- Observation: The final render quality review was documented, but playback-specific pass/fail claims require a human reviewer.
  Evidence: `docs/final-render-quality-review.md` records the render command, output path, output size, validation summary, checklist, known issues, and release decision. Codex can verify render evidence from commands, but cannot directly watch or listen to GUI playback from this environment, so playback checks are marked as needing human review.
- Observation: The release decision is conservative.
  Evidence: `docs/final-render-quality-review.md` records `needs-polish` because render and preflight evidence are good, but the decision should not be upgraded to `release-ready` or `release-ready-with-known-warnings` until a human reviewer watches and listens to `remotion/out/final.mp4`.
- Observation: Final cleanup restored clean props and left generated artifacts ignored.
  Evidence: After rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` without rerunning `prepare-visual-assets`, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. `git status --short --ignored` showed only the two docs files as commit candidates; `remotion/props.json` was not modified.

## Decision Log

- Decision: Use only the existing Remotion final render script for the full release render.
  Rationale: `render:final:local` already points at `SyncCutVideo`, writes `out/final.mp4`, uses local Chrome, and omits `--frames`, so adding or changing scripts would violate the validation-only scope.
  Date/Author: 2026-05-13 / Codex
- Decision: Keep quality review notes in a text document only if the final render is produced or there are useful review findings to preserve.
  Rationale: The plan itself can record command evidence, but a separate `docs/final-render-quality-review.md` is useful when there is a rendered artifact to review manually. It must remain text-only and must not embed media.
  Date/Author: 2026-05-13 / Codex
- Decision: Clean `remotion/props.json` after final render validation unless the user explicitly approves committing prepared sample props.
  Rationale: `prepare-visual-assets` mutates `remotion/props.json` with local `visual.public_path` fields. Those fields point to ignored local media and should not become a commit candidate by accident.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested repository guidance, current release documentation, current TSMC visual manifest, Phase 20 completion evidence, Remotion scripts, current clean props, and ignore rules. No render was run, no source code changed, no schemas changed, no command behavior changed, no media was generated or downloaded, no ffmpeg or ffprobe command was called, no generated artifact was committed, and no tag was created.

The intended outcome is a documented final release render evidence trail. Success means all 17 local visual assets are prepared before render, verified preflight has zero errors and zero file errors, typecheck and pytest pass, the full render either succeeds or records an exact environment limitation, manual review notes are captured when a render exists, generated artifacts remain ignored, and clean props are restored before the final review.

Milestone 1 is complete. The local asset gate confirmed one supported `.mp4` file for each of the 17 target scenes and found no missing or duplicate supported files. The regeneration and preparation sequence completed successfully: `build-timeline` rewrote `timeline.json`, `validate-timeline` passed with the known `07_CONCLUSION` gap warning, `export-remotion` wrote `remotion/props.json` with 33 scenes, 7 sections, 30 fps, 22584 frames, and 1 warning, `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`, and `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`.

Readiness before the full render matches the expected final prepared state. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 1`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The only warning is the known root props warning: `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.

Validation passed. `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`. `.venv/bin/python -m pytest` collected and passed 208 tests.

Artifact status is expected for the handoff to Milestone 2. `git status --short --ignored` shows `remotion/props.json` modified because it is intentionally prepared with local visual public paths for the upcoming full render, and `docs/plans/final-release-render-quality-review.md` as a new documentation file. Ignored generated/local paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`. Do not commit `remotion/props.json` in this prepared state unless explicitly approved; it should remain prepared for Milestone 2 and be cleaned during Milestone 4.

The first Milestone 2 render attempt was completed as a failed render-validation attempt. The prepared state before that render was correct: `inspect-visual-assets` reported 17 prepared target scenes, 0 missing, and 0 unsupported; verified preflight reported 17 prepared visuals, 0 missing visuals, 0 errors, 0 file errors, and only the known `07_CONCLUSION` gap warning.

The first `npm run render:final:local` attempt failed before rendering because Chrome launch was blocked by the sandbox. The exact browser-launch failure included `Closed with null signal: SIGTRAP` and `setsockopt: Operation not permitted (1)`. The same existing npm script was then rerun with Chrome launch permission. That permitted render progressed through frame 21393 of 22584 before failing while loading `visuals/scene_033.mp4`. The relevant render error was Remotion's compositor invoking its bundled ffprobe internally and reporting `moov atom not found` and `Invalid data found when processing input` for a temporary copy of the scene 033 MP4; the proxied public asset request returned HTTP 500. No workaround code was added, no render script was changed, and no direct ffmpeg or ffprobe command was run.

No successful `out/final.mp4` size was recorded because the final render exited with code 1. `.venv/bin/python -m pytest` still passed with 208 tests. Artifact status after the failed render is expected for this milestone: `remotion/props.json` remains modified and intentionally prepared for follow-up review, `docs/plans/final-release-render-quality-review.md` is the documentation commit candidate, and generated/local paths remain ignored, including `remotion/out/`, `remotion/public/`, `assets/`, `timeline.json`, `.pytest_cache/`, `.venv/`, `remotion/node_modules/`, and Python `__pycache__/` directories. `remotion/out/final.mp4`, if present as a partial or failed render artifact, is ignored and must not be committed. `remotion/props.json` remains prepared and should be cleaned in Milestone 4 after the asset issue is reviewed or as directed.

The focused recovery readiness step after the failed render is complete. The old `scene_033.mp4` render failure is recorded as an input asset issue. After the user replaced `assets/visuals/scene_033.mp4`, the local asset check found all 17 target scenes present with exactly one supported file each, including `scene_033: assets/visuals/scene_033.mp4`. The replacement was validated by path and extension only; no media probing, transcoding, ffmpeg, or ffprobe command was run.

The renewed preparation and readiness sequence passed. `build-timeline` regenerated `timeline.json`; `validate-timeline` passed with the known `07_CONCLUSION` gap warning; `export-remotion` wrote `remotion/props.json` with 33 scenes, 7 sections, 30 fps, 22584 frames, and 1 warning; `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`; and `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`.

Readiness after replacement matches the expected final prepared state. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 1`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The single warning is still the known `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.

Validation after replacement passed. `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`. `.venv/bin/python -m pytest` collected and passed 208 tests. Artifact status remains expected: `remotion/props.json` is modified because it is intentionally prepared for the next final render retry, `docs/plans/final-release-render-quality-review.md` is the documentation commit candidate, and generated/local paths are ignored, including `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`. Do not commit `remotion/props.json`; it remains prepared for the next final render retry and should be cleaned in Milestone 4.

Milestone 2 is now complete after the replacement retry. Before rendering, readiness was reconfirmed: `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`; verified preflight reported `status: warning`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 1`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The single warning was still the known `07_CONCLUSION` gap.

The sandboxed `npm run render:final:local` retry failed before rendering with the expected browser-launch error: `Closed with null signal: SIGTRAP` and Chromium `setsockopt: Operation not permitted (1)`. The same npm script was rerun with Chrome launch permission. The permitted run used the existing script unchanged, copied a 247.6 MB public directory, rendered all 22584 frames, encoded all 22584 frames, and wrote `remotion/out/final.mp4`. Remotion reported the output as `253.4 MB`; `ls -lh out/final.mp4` reported `242M`. The retry passed the previous failure point at frame 21393, so the replaced `scene_033` asset cleared the earlier blocker.

Post-render validation passed. `.venv/bin/python -m pytest` collected and passed 208 tests. Artifact status remains expected: `remotion/props.json` is modified because it remains intentionally prepared for Milestone 3 quality review, `docs/plans/final-release-render-quality-review.md` is the documentation commit candidate, and generated/local paths are ignored, including `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`. `remotion/out/final.mp4` is ignored and must not be committed. `remotion/props.json` remains prepared and should be cleaned in Milestone 4.

Milestone 3 is complete as a documented quality-review note. `docs/final-render-quality-review.md` was created as a text-only review artifact because the final render succeeded. It records the render command, output path, output size, validation summary, checklist, issues found, release decision, and next recommended action.

The key quality-review finding is a limitation of this non-interactive agent environment: Codex can confirm the render completed and can record validation evidence, but cannot directly watch or listen to GUI playback. For that reason, playback-specific checklist items such as video opens and plays, narration audibility, audio/section alignment, first 30 seconds, black screens, visual placeholder absence, visual quality, and transitions are marked as needing human review rather than claimed as passing. Render-evidence checks passed: the render completed all `22584` frames, and the duration matches 22584 frames at 30 fps, approximately 752.8 seconds.

The release decision recorded in `docs/final-render-quality-review.md` is `needs-polish`. This is conservative: render and preflight evidence are good, and the known `07_CONCLUSION` gap is the only automated warning, but the release decision should not be upgraded until a human reviewer plays `remotion/out/final.mp4` and confirms audio and visual quality. Milestone 4 should clean `remotion/props.json` back to the no-visual-prep sample state and recommend docs-only commit candidates.

Milestone 4 is complete. `remotion/props.json` was cleaned by regenerating `timeline.json`, validating the timeline, exporting Remotion props, and preparing audio assets only. `prepare-visual-assets` was intentionally not rerun after cleanup. `validate-timeline` passed with the known `07_CONCLUSION` gap warning. `export-remotion` wrote 33 scenes, 7 sections, 30 fps, 22584 frames, and 1 warning. `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, and `audio_assets: 7`.

Clean props verification matched expectations. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, `public_dir: remotion/public`, and `file_errors: 0`. The warnings are expected in clean props: the known `07_CONCLUSION` gap plus 17 optional missing AI/B-roll visual public paths that would render placeholders unless visual assets are prepared again.

Final validation passed. `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`. `.venv/bin/python -m pytest` collected and passed 208 tests.

Artifact review is clean. `git status --short --ignored` shows no source, schema, command behavior, Remotion source, render script, or `remotion/props.json` changes. Generated/local artifacts are ignored, including `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`. `remotion/out/final.mp4` remains ignored and must not be committed. The only commit candidates are docs: `docs/plans/final-release-render-quality-review.md` and `docs/final-render-quality-review.md`.

Final Phase 21 summary: the work stayed within validation/review scope. The full final render succeeded after replacing the invalid `scene_033` asset. No Python source, Remotion source, schemas, command behavior, render scripts, media generation/download/scrape, ffmpeg/ffprobe command, probing, transcoding, binary commit, or tag was introduced. The quality review doc is text-only. The release decision remains `needs-polish` because human playback review is not complete and the known `07_CONCLUSION` gap remains. Blockers for tagging are human playback review and the known gap decision. Recommendation: commit docs evidence only and do not tag v0.1.0 yet. Recommended commit message: `Document final release render quality review`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. The Python CLI lives under `synccut/`. It builds `timeline.json`, exports `remotion/props.json`, prepares audio and optional visual assets into `remotion/public/`, and reports readiness with `inspect-visual-assets` and `preflight`. The Remotion project lives under `remotion/`. It consumes `remotion/props.json` and renders the composition `SyncCutVideo` from `src/index.ts`.

A target visual scene means a scene whose `visual_type` is `AI_VIDEO` or `B_ROLL`. These are the only scenes prepared by `synccut prepare-visual-assets`. The TSMC sample has 17 target visual scenes. The complete local source asset set is expected under `assets/visuals/`, one supported file per scene id. Phase 20 validated that all 17 target scenes had exactly one local supported `.mp4` file and that `prepare-visual-assets` could prepare all of them.

A public asset is a file under `remotion/public/` referenced by a Remotion-safe path such as `audio/01_HOOK.mp3` or `visuals/scene_001.mp4`. Verified preflight checks those public paths when run with `--verify-files --public-dir remotion/public`.

The current clean sample props are intentionally not visually prepared. Clean props should report 17 missing optional AI/B-roll visual assets because `visual.public_path` fields are absent. That clean state is expected before and after local render validation. During Milestone 1 and Milestone 2, props will be temporarily modified by `prepare-visual-assets` so all 17 visuals can render from local public files.

The full render output is `remotion/out/final.mp4`. It is a generated artifact and ignored by git. Do not commit it.

## Plan of Work

Milestone 1 is the final render readiness check. Confirm that all 17 local source visual files still exist under `assets/visuals/` and that each target scene has exactly one supported file. Regenerate `timeline.json`, validate it, export clean props, prepare audio assets, run `prepare-visual-assets`, inspect visual readiness, run verified preflight, run Remotion typecheck, and run Python tests. Do not render in this milestone. Acceptance for this milestone is that `inspect-visual-assets` reports `prepared: 17`, `missing: 0`, `unsupported: 0`, verified preflight reports `errors: 0` and `file_errors: 0`, `npm run typecheck` passes, and pytest passes.

Milestone 2 is the full final render. From `remotion/`, run `npm run render:final:local`. This existing script uses local Chrome at `/usr/bin/google-chrome`, uses `--chrome-mode=chrome-for-testing`, sets `--concurrency=1`, sets `--timeout=60000`, writes `out/final.mp4`, and renders the full composition because it has no `--frames` flag. If Chrome launch fails because of sandbox permissions, record the exact error and rerun with Chrome launch permission if available. If the render succeeds, run `ls -lh out/final.mp4` and record the output size. Do not commit the output.

Milestone 3 is manual quality review. Review `remotion/out/final.mp4` manually using a local video player or any available safe local preview method. Record review notes in this plan, and create `docs/final-render-quality-review.md` only if a separate text-only quality review artifact is useful. The review should decide one of: `release-ready`, `release-ready-with-known-warnings`, or `needs-polish`. Do not edit media, source code, schemas, commands, render scripts, or props in this milestone.

Milestone 4 is final cleanup and commit recommendation. Regenerate clean props and audio only, without rerunning `prepare-visual-assets`, so `remotion/props.json` returns to the no-visual-prep sample state. Verify clean `inspect-visual-assets` and verified preflight, run typecheck and pytest, review `git status --short --ignored`, and recommend committing docs only. Do not delete ignored local source assets or render outputs unless explicitly asked.

## Concrete Steps

From the repository root, confirm local visual sources before preparation:

    .venv/bin/python -c "from pathlib import Path; ids=['scene_001','scene_003','scene_004','scene_006','scene_008','scene_010','scene_013','scene_015','scene_017','scene_020','scene_022','scene_025','scene_027','scene_029','scene_030','scene_031','scene_033']; exts={'.png','.jpg','.jpeg','.webp','.mp4','.webm','.mov'}; base=Path('assets/visuals'); missing=[]; dupes=[]; found=[]; [found.append((sid,[p for p in base.iterdir() if p.is_file() and p.stem==sid and p.suffix.lower() in exts])) for sid in ids]; missing=[sid for sid,files in found if not files]; dupes=[(sid,[str(f) for f in files]) for sid,files in found if len(files)>1]; print('missing:', missing); print('duplicates:', dupes); print('files:', [(sid, str(files[0])) for sid,files in found if len(files)==1])"

If the command reports any missing ids or duplicates, stop and resolve the local files outside this plan before continuing.

Regenerate timeline, props, audio, and visual public assets:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected readiness before render:

    inspect-visual-assets:
    target_scenes: 17
    prepared: 17
    missing: 0
    unsupported: 0

    preflight:
    visual_prepared: 17
    visual_missing: 0
    visual_unsupported: 0
    errors: 0
    verify_files: true
    file_errors: 0

The overall preflight status may be `warning` because the current sample has the known root warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.

Run validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

Run the full final render only in Milestone 2:

    cd remotion
    npm run render:final:local
    ls -lh out/final.mp4
    cd ..

After render and quality review, clean props before final review:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not run `prepare-visual-assets` after this cleanup. Verify clean state:

    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected clean state:

    inspect-visual-assets:
    target_scenes: 17
    prepared: 0
    missing: 17
    unsupported: 0

    preflight:
    status: warning
    visual_prepared: 0
    visual_missing: 17
    errors: 0
    verify_files: true
    file_errors: 0

Run final validation and artifact review:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest
    git status --short --ignored

## Manual Quality Review Checklist

Review `remotion/out/final.mp4` only after a successful full render. Record evidence and notes in the living sections above or in `docs/final-render-quality-review.md` if a separate text document is created.

Check that the video opens and plays. Check that narration audio is audible. Check that audio roughly aligns with section changes. Check that there are no obvious black screens or missing placeholder cards for `AI_VIDEO` and `B_ROLL` scenes now that all 17 local visual assets are prepared. Check that the first 30 seconds look correct because this range has been used for segment validation before. Check that section transitions are acceptable. Check that the final section renders. Check that the full duration is approximately 752.79 seconds, or 22584 frames at 30 fps. Record whether the known `07_CONCLUSION` timing gap is acceptable or needs a later timeline polish phase. List visual quality issues by scene id where possible. Record the release decision as `release-ready`, `release-ready-with-known-warnings`, or `needs-polish`.

If creating `docs/final-render-quality-review.md`, keep it text-only. Include the render command, output path, output size, validation summary, manual review checklist, issues found, release decision, and reviewer/date. Do not embed media, screenshots, raw generated assets, credentials, or private license details.

## Validation and Acceptance

Milestone 1 is accepted when all 17 local visual files are found with no duplicates, `prepare-visual-assets` prepares 17 assets, `inspect-visual-assets` reports `prepared: 17`, `missing: 0`, and `unsupported: 0`, verified preflight reports `errors: 0` and `file_errors: 0`, Remotion typecheck passes, and pytest passes.

Milestone 2 is accepted when `npm run render:final:local` either succeeds and produces `remotion/out/final.mp4` with a recorded file size, or fails with an exact recorded environment limitation such as Chrome sandbox launch failure. If Chrome launch is blocked and permission can be granted, rerun the same command with permission and record both outcomes.

Milestone 3 is accepted when manual review notes are recorded and a release decision is stated. A successful render does not automatically mean release-ready; visible quality issues may require a later polish phase.

Milestone 4 is accepted when `remotion/props.json` is cleaned back to the no-visual-prep state, clean verified preflight has `errors: 0` and `file_errors: 0`, generated artifacts remain ignored, `remotion/props.json` is not a required commit candidate, and commit recommendations are docs only.

## Idempotence and Recovery

The timeline, export, audio preparation, visual preparation, and preflight commands are safe to rerun. `prepare-remotion-assets` and `prepare-visual-assets` may reuse or overwrite generated files under `remotion/public/`; that directory is ignored. If `prepare-visual-assets` fails because of duplicate files for a scene id, remove or rename the duplicate local source outside this plan and rerun the command. Do not use ffmpeg, ffprobe, media probing, or transcoding to fix assets in this repository.

If `npm run render:final:local` fails because Chrome cannot launch in a sandbox, record the exact error and rerun with Chrome launch permission if available. Do not add workaround code or modify Remotion configuration. If the render fails because of time or local resources, record the exact failure and treat it as an environment limitation unless the error points to a clear source bug that should be reviewed separately.

If `remotion/props.json` remains modified after preparation, clean it with the cleanup commands in Milestone 4. Do not run `git reset`, `git checkout`, `git clean`, or destructive cleanup commands unless explicitly approved.

## Artifacts and Notes

Generated or local-only artifacts must not be committed:

- `timeline.json`
- `assets/visuals/*`
- `remotion/public/*`
- `remotion/out/final.mp4`
- `remotion/out/segment.mp4`
- `remotion/out/smoke.mp4`
- `remotion/out/preview.png`
- `.venv/`
- `remotion/node_modules/`
- Python, pytest, and Node caches

Normal commit candidates for this phase should be text documentation only:

- `docs/plans/final-release-render-quality-review.md`
- optionally `docs/final-render-quality-review.md` if created during manual review

`remotion/props.json` should be cleaned before final review and should not be committed unless explicitly approved as an intentional sample props refresh.

## Interfaces and Dependencies

This phase uses existing interfaces only. The Python CLI is invoked through `.venv/bin/synccut`. The relevant existing commands are `build-timeline`, `validate-timeline`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, and `preflight`. The Remotion project is invoked through npm scripts in `remotion/package.json`; the relevant existing scripts are `typecheck` and `render:final:local`.

No source modules, function signatures, schemas, package dependencies, npm scripts, or Remotion components should be changed in this phase. No Python command should invoke Remotion. No direct ffmpeg or ffprobe command should be added or run. No media generation, download, scraping, probing, decoding, transcoding, or normalization should happen inside this repository.

## Change Note

2026-05-13 / Codex: Created this ExecPlan for Phase 21 final release render and quality review. The plan records the validation-only scope, exact preparation and render commands, expected readiness outputs, manual review checklist, cleanup steps, artifact policy, and explicit exclusions.
