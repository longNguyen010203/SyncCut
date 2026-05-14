# Post-polish final render and playback review

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to regenerate the post-polish TSMC sample, render the final video, collect human playback review, clean generated state, and make a release recommendation from this file without reading earlier conversation.

## Purpose / Big Picture

Phase 23 fixed the two known human playback issues from the previous render: the `07_CONCLUSION` timing gap is smoothed by the timeline builder, and prepared AI_VIDEO/B_ROLL video assets explicitly loop in Remotion when their source videos are shorter than their scene duration. This phase proves those fixes in the final release path. After completing this plan, a maintainer should have a newly rendered `remotion/out/final.mp4`, verified post-polish preflight evidence, human playback re-review notes, and a clear decision about whether the TSMC sample is `release-ready-with-known-warnings`, still `needs-polish`, or `blocked`.

This phase is validation and review only. It must not add product features, change schemas, change command behavior, add render scripts, call ffmpeg or ffprobe, probe or transcode media, generate or download media, commit binary media, commit generated public assets, commit render outputs, commit `remotion/props.json` unless explicitly approved, or tag `v0.1.0` unless the user explicitly requests it after review.

## Progress

- [x] (2026-05-13T23:02:00+07:00) Read the requested repository instructions, release docs, Phase 21 quality review, Phase 22 issue inventory, Phase 23 timing/loop plan, visual asset manifest, Remotion README/package scripts, current Remotion visual asset component, timeline builder, and `.gitignore` context needed to create this plan.
- [x] (2026-05-13T23:02:00+07:00) Confirmed current Phase 23 source-level fixes are present in the worktree: `VisualAssetScene.tsx` renders prepared video assets with Remotion `Video` and `loop`, and `timeline_builder.py` smooths suspicious same-section gaps using `SUSPICIOUS_GAP_SEC`.
- [x] (2026-05-13T23:02:00+07:00) Created this Phase 24 ExecPlan.
- [x] (2026-05-13T23:21:59+07:00) Milestone 1: Confirmed all 17 local visual source files, regenerated post-polish timeline and props, prepared audio and visuals, verified visual readiness and preflight status `ok`, passed Remotion typecheck, passed pytest, and left `remotion/props.json` intentionally prepared for Milestone 2 render.
- [x] (2026-05-14T09:27:00+07:00) Milestone 2: Rendered the full post-polish final MP4 with the existing `render:final:local` script after rerunning with Chrome launch permission, recorded output size, passed pytest, and reviewed artifact status.
- [x] (2026-05-14T09:45:00+07:00) Milestone 3: Recorded user human playback re-review findings, marked `P22-001` and `P22-002` resolved/acceptable, and updated the release decision to `release-ready-with-known-warnings`.
- [x] (2026-05-14T10:02:00+07:00) Milestone 4: Cleaned generated props back to audio-only prepared state, verified warning-only clean visual state, passed Remotion typecheck and pytest, reviewed ignored artifacts, and recorded commit recommendation.

## Surprises & Discoveries

- Observation: The previous final render evidence is now stale for release decision purposes.
  Evidence: `docs/final-render-quality-review.md` records a final render that still had the known `07_CONCLUSION` gap and short video duration behavior. Phase 23 changed the timeline builder and Remotion video branch after that render.
- Observation: Phase 23 fixed the two known playback issues at source level but did not refresh committed sample props.
  Evidence: `docs/plans/timing-and-visual-duration-polish.md` records zero-warning regenerated timeline/export validation and a successful segment render, but it also records that `remotion/props.json` was restored out of commit candidates because generated sample props were not approved for commit.
- Observation: The local final render command already exists and renders the full composition.
  Evidence: `remotion/package.json` defines `render:final:local` as `remotion render src/index.ts SyncCutVideo out/final.mp4 --browser-executable=/usr/bin/google-chrome --chrome-mode=chrome-for-testing --concurrency=1 --timeout=60000`, with no `--frames` flag.
- Observation: The complete local visual source set is documented as prepared-local.
  Evidence: `docs/tsmc-visual-asset-manifest.md` lists all 17 AI_VIDEO/B_ROLL target scenes as `prepared-local`, with expected filenames under `assets/visuals/<scene_id>.mp4`.
- Observation: The local asset source set is present and unambiguous for post-polish readiness.
  Evidence: The Milestone 1 asset check reported `missing: []` and `duplicates: []`. It found exactly one `.mp4` for each target scene: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: Post-polish timeline and Remotion export readiness are clean.
  Evidence: `validate-timeline timeline.json` reported `warnings: 0`. `export-remotion timeline.json --out remotion/props.json` reported 33 scenes, 7 sections, 30 fps, 22584 frames, and `warnings: 0`.
- Observation: Post-polish prepared visual readiness and verified preflight are clean.
  Evidence: `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: ok`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `warnings: 0`, `errors: 0`, and `file_errors: 0`.
- Observation: The first Milestone 2 Chrome launch was blocked by the sandbox, but the same render command succeeded with Chrome launch permission.
  Evidence: The first `cd remotion && npm run render:final:local` failed before rendering with `Failed to launch browser process`, `SIGTRAP`, and `setsockopt: Operation not permitted (1)`. The rerun of the same npm script with permission completed successfully with exit code 0.
- Observation: The post-polish final render completed, but the explicit video-loop path made the full render materially slower than earlier validation renders.
  Evidence: The permitted render started around 2026-05-14 07:24 +07 and completed around 2026-05-14 09:27 +07. Remotion rendered and encoded all `22584/22584` frames and reported `out/final.mp4 615.1 MB`.
- Observation: The final MP4 exists as an ignored render artifact.
  Evidence: `ls -lh remotion/out/final.mp4` reported `-rw-rw-r-- ... 587M May 14 09:27 out/final.mp4`. `git status --short --ignored` lists `!! remotion/out/`, so the final MP4 is ignored and must not be committed.
- Observation: Human post-polish re-review confirmed the two known Phase 22 issues are now acceptable/resolved.
  Evidence: The user reviewed the new post-polish `remotion/out/final.mp4` and reported that `P22-001`, the `07_CONCLUSION` gap, is now acceptable/resolved, and that `P22-002`, the short AI_VIDEO/B_ROLL visual-duration issue, is now acceptable/resolved because videos loop through scene duration.
- Observation: No new blocker was reported in the human post-polish re-review.
  Evidence: The user explicitly reported no new blocker issue and noted that the playback pass is still human review, not exhaustive QA.
- Observation: Clean generated props now intentionally omit visual public paths again.
  Evidence: After rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` without `prepare-visual-assets`, `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.
- Observation: Clean verified preflight is warning-only because visual public paths are intentionally absent from clean props.
  Evidence: `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `errors: 0`, `file_errors: 0`, `visual_prepared: 0`, and `visual_missing: 17`.
- Observation: `remotion/props.json` remains a modified generated file after cleanup and should not be committed unless explicitly approved.
  Evidence: `git status --short --ignored` lists ` M remotion/props.json`, while generated/local paths remain ignored, including `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories.

## Decision Log

- Decision: Treat Phase 24 as validation/review only, not as a feature or bug-fix phase.
  Rationale: Phase 23 already implemented the timing and visual-duration fixes. Phase 24's purpose is to regenerate, rerender, and have a human verify whether those fixes are good enough for release.
  Date/Author: 2026-05-13 / Codex
- Decision: Use the existing Remotion `render:final:local` script for the full render.
  Rationale: The repository already has a documented local final render workflow that uses local Chrome and renders the full composition. Adding scripts or invoking Remotion from Python is explicitly out of scope.
  Date/Author: 2026-05-13 / Codex
- Decision: Keep `remotion/props.json` generated and uncommitted unless the user explicitly approves a sample props refresh.
  Rationale: The artifact policy says generated props should not be committed when changed only by validation regeneration. Phase 23 also left tracked sample props unchanged by design.
  Date/Author: 2026-05-13 / Codex
- Decision: Update `docs/final-render-quality-review.md` as the human re-review record.
  Rationale: That file already contains the previous final render evidence, issue log, release decision, and next action. Appending post-polish evidence there keeps release quality history in one text-only document.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reviewing the current project instructions, release documentation, Phase 21 render evidence, Phase 22 human findings, Phase 23 source fixes and validation evidence, Remotion render scripts, the visual asset manifest, and the current artifact policy. No source code, schemas, command behavior, media, render output, generated props, commit, or tag was changed while creating the plan.

The intended outcome is a post-polish release-quality evidence package. Milestone 1 should prove that the regenerated timeline/export no longer emits warnings and that all 17 visuals can be prepared with verified public files. Milestone 2 should produce a fresh final MP4 using the post-polish code path. Milestone 3 should record human playback findings, specifically whether `P22-001` and `P22-002` are resolved. Milestone 4 should clean generated props, confirm ignored artifacts stay out of commit candidates, and recommend the next commit or release action.

Milestone 1 is complete. The local asset check found all 17 expected target visual files under `assets/visuals/` with exactly one supported file per scene id and no duplicates. Fresh post-polish generation produced a timeline with `validate-timeline` warnings `0` and a Remotion export with warnings `0`. Audio preparation reused 7 public audio assets, and visual preparation reused all 17 visual assets.

Readiness for the post-polish final render is clean. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: ok`, `visual_prepared: 17`, `visual_missing: 0`, `errors: 0`, and `file_errors: 0`. `cd remotion && npm run typecheck` passed, and `.venv/bin/python -m pytest` collected 212 tests and all 212 passed.

Artifact review after Milestone 1 shows `remotion/props.json` is modified because it is intentionally prepared with audio and visual public paths for the Milestone 2 final render. It must not be committed. Generated/local paths remain ignored, including `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories. The next step is Milestone 2: render the full post-polish final video with the existing `render:final:local` script.

Milestone 2 is complete. Before rendering, prepared state was re-confirmed: `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`, and verified preflight reported `status: ok`, `visual_prepared: 17`, `visual_missing: 0`, `errors: 0`, and `file_errors: 0`.

The first local Chrome launch failed under sandboxing with `SIGTRAP` and `setsockopt: Operation not permitted (1)`, matching the known environment behavior. The same existing `render:final:local` command was rerun with Chrome launch permission and completed successfully. Remotion rendered and encoded all `22584/22584` frames, reported `out/final.mp4 615.1 MB`, and `ls -lh out/final.mp4` reported `587M`. No render media error or invalid-video failure occurred.

Post-render validation remains green. `.venv/bin/python -m pytest` collected 212 tests and all 212 passed. Artifact review shows `remotion/props.json` remains modified because it is still intentionally prepared for Milestone 3 human playback review and Milestone 4 cleanup; it must not be committed. `docs/plans/post-polish-final-render-review.md` is a docs commit candidate. Generated/local paths remain ignored, including `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories. The next step is Milestone 3: human playback re-review of the new post-polish `remotion/out/final.mp4`.

Milestone 3 is complete. The user reviewed the new post-polish `remotion/out/final.mp4` and confirmed both known issues are acceptable/resolved: `P22-001`, the `07_CONCLUSION` gap, and `P22-002`, the short AI_VIDEO/B_ROLL visual-duration issue after explicit video looping. No new blocker was reported. The review remains a human pass rather than exhaustive QA, so normal future-polish risk remains.

The release decision in `docs/final-render-quality-review.md` is now `release-ready-with-known-warnings`. The rationale is that the post-polish render succeeded, the two known issues were confirmed acceptable/resolved, and no new blocker was reported. The next step is Milestone 4: clean generated props, verify artifact status, and recommend the docs/source evidence commit. No tag should be created in this phase unless the user explicitly requests it later.

Milestone 4 is complete. Generated props were cleaned back to audio-only prepared state by rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets`, and `prepare-visual-assets` was intentionally not rerun. `validate-timeline timeline.json` reported `warnings: 0`; `export-remotion timeline.json --out remotion/props.json` reported 33 scenes, 7 sections, 30 fps, 22584 frames, and `warnings: 0`; and audio preparation reused 7 public audio assets.

The clean visual state matches the artifact policy. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, and `file_errors: 0`. The warnings are expected because clean props intentionally omit local visual public paths after cleanup.

Final validation passed. `cd remotion && npm run typecheck` passed, and `.venv/bin/python -m pytest` collected 212 tests and all 212 passed. Phase 24 final render evidence remains: the post-polish full render completed all `22584/22584` frames, produced `remotion/out/final.mp4`, and the user confirmed both known issues are acceptable/resolved. The release decision remains `release-ready-with-known-warnings`; no tag should be created unless explicitly requested later.

Artifact review shows the only intended tracked text/doc candidate for Phase 24 is this plan plus `docs/final-render-quality-review.md`. `remotion/props.json` is modified by generated validation cleanup and should not be committed unless the user explicitly approves refreshing sample props. Ignored generated/local paths include `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories. No binary media or render output should be staged.

Commit recommendation: if Phase 23 source/test/docs changes and Phase 24 review docs are committed together, use `Polish timing gaps and verify post-polish final render`. If Phase 23 has already been committed separately, use `Document post-polish final render review`. Do not tag `v0.1.0` until the user explicitly approves a release/tagging phase.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI in `synccut/` and a Remotion project in `remotion/`. The Python CLI builds `timeline.json` from `examples/scenes.json`, section audio in `examples/audio`, and alignment JSON in `examples/alignments`; validates and inspects the timeline; exports `remotion/props.json`; prepares audio into `remotion/public/audio`; prepares optional local visuals into `remotion/public/visuals`; and runs preflight checks. The Remotion project consumes `remotion/props.json` and renders the `SyncCutVideo` composition.

The old final output at `remotion/out/final.mp4` was produced before Phase 23 and should be treated as stale for release decision. A new final render must be produced after regenerating props with the Phase 23 code. Render outputs under `remotion/out/` are generated artifacts and must not be committed.

`P22-001` is the human playback issue for the `07_CONCLUSION` timing gap between `scene_030` and `scene_031`. Phase 23 addressed it in `synccut/timeline_builder.py` by extending a previous scene over a suspicious same-section positive gap without moving the next scene start. `tests/test_timeline_builder.py` contains focused tests showing same-section gap closure, next-scene start preservation, no section-boundary merging, and unchanged contiguous scenes.

`P22-002` is the human playback issue where many prepared AI_VIDEO/B_ROLL videos are shorter than narration. Phase 23 addressed it in `remotion/src/components/VisualAssetScene.tsx` by rendering prepared video assets with Remotion `Video` and the `loop` prop. Prepared images still use `Img`, and missing or unsupported assets still fall back to `PlaceholderScene`.

The TSMC sample has 17 target visual scenes: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`. A target visual scene means its visual type is `AI_VIDEO` or `B_ROLL`. The expected local files are under `assets/visuals/`, and prepared public copies go under `remotion/public/visuals/`. Both directories are ignored.

The existing final render script is `npm run render:final:local` from the `remotion/` directory. It uses `/usr/bin/google-chrome`, `--chrome-mode=chrome-for-testing`, `--concurrency=1`, and `--timeout=60000`. It has no `--frames` flag, so it renders the full composition to `remotion/out/final.mp4`. In this environment, Chrome launch can fail under sandboxing with `SIGTRAP` and `setsockopt: Operation not permitted`; when that happens, rerun the same command with Chrome launch permission if available and do not add workaround code.

## Plan of Work

Milestone 1 is post-polish readiness validation. Confirm the local visual source set still has exactly one supported file for each of the 17 target scenes. Regenerate `timeline.json`, validate it, export `remotion/props.json`, prepare audio, prepare visuals, inspect visual readiness, run verified preflight, run Remotion typecheck, and run Python tests. Acceptance for Milestone 1 is that `validate-timeline` and `export-remotion` report zero warnings, `inspect-visual-assets` reports all 17 target scenes prepared, verified preflight reports `status: ok` with zero errors and file errors, typecheck passes, and pytest passes. Do not render in this milestone.

Milestone 2 is the full post-polish final render. Confirm prepared state first with `inspect-visual-assets` and verified preflight, then run `npm run render:final:local` from `remotion/`. If sandbox policy blocks Chrome launch, record the exact error and rerun with Chrome launch permission if available. If render succeeds, run `ls -lh out/final.mp4` and record the size. Do not commit `out/final.mp4`.

Milestone 3 is human playback re-review. A human opens the new `remotion/out/final.mp4`, watches and listens manually, and updates `docs/final-render-quality-review.md`. The review must explicitly say whether `P22-001` is resolved or still present, whether `P22-002` is resolved or still present, and whether any new issues appeared. The release decision must be one of `release-ready-with-known-warnings`, `needs-polish`, or `blocked`.

Milestone 4 is cleanup and final review. Regenerate clean timeline/props and prepare audio only. Do not run `prepare-visual-assets` after cleanup. Verify clean props have no prepared visuals and only expected optional missing-visual warnings. Review `git status --short --ignored`. Commit candidates should normally be docs only for this validation phase, unless a source bug was discovered and the user explicitly approved a fix. Do not tag `v0.1.0` unless explicitly requested after the human review decision.

## Concrete Steps

Run commands from the repository root unless a command explicitly changes into `remotion/`.

For Milestone 1, first confirm local visual source files:

    .venv/bin/python -c "from pathlib import Path; ids=['scene_001','scene_003','scene_004','scene_006','scene_008','scene_010','scene_013','scene_015','scene_017','scene_020','scene_022','scene_025','scene_027','scene_029','scene_030','scene_031','scene_033']; exts={'.png','.jpg','.jpeg','.webp','.mp4','.webm','.mov'}; base=Path('assets/visuals'); found=[]; [found.append((sid,[p for p in base.iterdir() if p.is_file() and p.stem==sid and p.suffix.lower() in exts])) for sid in ids]; print('missing:', [sid for sid,files in found if not files]); print('duplicates:', [(sid,[str(f) for f in files]) for sid,files in found if len(files)>1]); print('files:', [(sid,str(files[0])) for sid,files in found if len(files)==1])"

If any target scene is missing or has duplicate supported files, stop and report the exact scene ids. Do not delete or replace local assets automatically.

Regenerate and prepare post-polish props:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected Milestone 1 readiness output includes:

    validate-timeline:
    warnings: 0

    export-remotion:
    warnings: 0

    inspect-visual-assets:
    target_scenes: 17
    prepared: 17
    missing: 0
    unsupported: 0

    preflight:
    status: ok
    visual_prepared: 17
    visual_missing: 0
    visual_unsupported: 0
    errors: 0
    file_errors: 0

Run typecheck and tests:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

For Milestone 2, confirm prepared state before rendering:

    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Then render:

    cd remotion
    npm run render:final:local
    ls -lh out/final.mp4
    cd ..

If Chrome launch is blocked by sandboxing, record the exact `SIGTRAP` and `setsockopt` output and rerun the same command with Chrome launch permission if available. Do not add workaround code, flags, scripts, or Python wrappers.

For Milestone 3, update `docs/final-render-quality-review.md`. Add a post-polish section with the render command, output path, output size, readiness summary, playback checklist, issue updates, and release decision. The human review checklist should include:

- video opens and plays
- narration audio is audible
- `P22-001` conclusion gap is no longer noticeable or is still present
- `P22-002` short videos now loop acceptably through scene duration or still cause visible mismatch
- no black screens
- no AI_VIDEO/B_ROLL placeholder cards
- final section renders
- no new blocker issues
- release decision is updated

For Milestone 4, clean generated props:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not run `prepare-visual-assets` after cleanup. Verify clean state:

    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    git status --short --ignored

Expected clean state is warning-only because clean props intentionally omit visual public paths:

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
    file_errors: 0

## Validation and Acceptance

Milestone 1 is accepted when all readiness commands pass and the post-polish props are verified as render-ready: timeline validation warnings are zero, Remotion export warnings are zero, 17 visual assets are prepared, preflight is `ok`, typecheck passes, and pytest passes.

Milestone 2 is accepted when `npm run render:final:local` either succeeds and produces `remotion/out/final.mp4` with a recorded size, or fails for a clearly recorded environment limitation. A Chrome sandbox failure alone is not a product blocker if rerunning with permission succeeds. Any render failure after Chrome launch must be recorded exactly and treated as a release blocker until reviewed.

Milestone 3 is accepted when a human playback re-review updates `docs/final-render-quality-review.md` with the status of `P22-001`, the status of `P22-002`, any new issues, and one release decision. `release-ready-with-known-warnings` is acceptable only if remaining issues are minor and explicitly accepted. `needs-polish` is required if timing, visual duration, visual quality, audio alignment, black-screen, placeholder, or final-section issues still need correction. `blocked` is required if the output cannot play or audio is unusable.

Milestone 4 is accepted when generated props have been cleaned, `remotion/props.json` is not a commit candidate unless explicitly approved, generated media/public/render artifacts remain ignored, and the final recommendation says exactly what should be committed and whether a release tag should wait.

## Idempotence and Recovery

The generation and preparation commands are safe to rerun. `build-timeline` rewrites ignored `timeline.json`; `export-remotion` rewrites `remotion/props.json`; `prepare-remotion-assets` and `prepare-visual-assets` copy or reuse ignored files under `remotion/public/`. If validation state becomes inconsistent, rerun the commands sequentially in the order shown. Do not run audio and visual preparation concurrently because both mutate `remotion/props.json`.

If `prepare-visual-assets` reports missing or duplicate assets, stop and report the exact files. Do not create, delete, download, generate, scrape, transcode, or normalize media in this phase.

If the final render fails before Chrome opens with `SIGTRAP` or `setsockopt: Operation not permitted`, rerun the same command with Chrome launch permission if available. If rendering fails because a media asset is invalid, record the exact Remotion error and stop; do not use ffmpeg, ffprobe, or probing tools to inspect the media in this phase.

If human review finds a new bug requiring source changes, record it in `docs/final-render-quality-review.md` and stop. A later explicitly approved polish phase should handle fixes. This phase should not quietly change Python or Remotion source.

## Artifacts and Notes

Do not commit generated or local media artifacts:

- `timeline.json`
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.venv/`
- `remotion/node_modules/`
- Python, pytest, and Node caches
- `remotion/props.json` if it only changed because of local validation regeneration or visual preparation

Normal commit candidates for this validation/review phase should be text docs only, most likely `docs/plans/post-polish-final-render-review.md` and `docs/final-render-quality-review.md`. If the user later approves committing Phase 23 source changes in the same commit, include only the already reviewed source/tests/docs files from Phase 23 and keep generated media out of the commit.

Evidence to record during implementation should be concise: command names, pass/fail status, key counts, render output size, Chrome sandbox behavior, human review findings, release decision, and `git status --short --ignored` summary.

## Interfaces and Dependencies

Use existing SyncCut and Remotion interfaces only. The Python CLI executable is `.venv/bin/synccut`. The relevant commands are `build-timeline`, `validate-timeline`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, and `preflight`. The Remotion commands are npm scripts under `remotion/package.json`: `typecheck` and `render:final:local`.

The render implementation is `remotion/src/components/VisualAssetScene.tsx`, which should already use Remotion `Video` with `loop` for prepared video assets and `Img` for images. The timing implementation is `synccut/timeline_builder.py`, which should already smooth suspicious same-section gaps. This phase should validate those interfaces; it should not redesign them.

No new Python modules, TypeScript components, schemas, npm scripts, package dependencies, external media APIs, ffmpeg commands, ffprobe commands, media probes, media transcoders, downloaders, scrapers, GUI behavior, or web app behavior should be introduced.

## Change Note

2026-05-13 / Codex: Created this ExecPlan for Phase 24 post-polish final render and playback re-review. The plan records the post-Phase 23 context, validation-only scope, render and review milestones, exact commands, expected outputs, artifact policy, recovery guidance, and explicit exclusions.

2026-05-13 / Codex: Updated after Milestone 1 readiness validation. The plan now records the 17-file local asset check, zero-warning timeline/export results, full visual preparation counts, verified preflight `status: ok`, typecheck and pytest results, artifact status, and the fact that `remotion/props.json` is intentionally prepared for Milestone 2 and must not be committed.

2026-05-14 / Codex: Updated after Milestone 2 final render validation. The plan now records the expected sandbox-blocked first Chrome launch, the permitted full render success, all `22584/22584` frames rendered and encoded, output sizes from Remotion and `ls`, pytest result, artifact status, and the fact that `remotion/props.json` remains prepared for Milestone 3 and must not be committed.
