# Timing and visual-duration polish

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to investigate, implement, validate, and review the timing and visual-duration polish from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut has reached a full local final render for the TSMC sample, but human playback review found two release-polish issues. The first is a known 1.115 second gap in section `07_CONCLUSION` between `scene_030` and `scene_031`. The second is that many prepared local AI_VIDEO and B_ROLL video files are shorter than the narration and scene duration, so the visual ends before the scene audio does. After this plan is complete, the final TSMC render should have smoother conclusion timing and AI_VIDEO/B_ROLL video assets should explicitly loop for the whole Remotion scene duration when their source files are short.

The user-visible outcome is a cleaner preview and final render. A contributor can see it working by preparing the local visual assets, running verified preflight, rendering at least the segment preview, and observing that video assets continue moving through the full scene instead of ending early. The `07_CONCLUSION` timing warning should also be gone or intentionally reduced/handled and documented.

## Progress

- [x] (2026-05-13T21:50:00+07:00) Read `.agent/PLANS.md`, the Phase 22 review docs, Remotion visual components, Remotion props/types, timeline validation/inspection/export code, Remotion package scripts, and README context needed to create this plan.
- [x] (2026-05-13T21:50:00+07:00) Confirmed current evidence for `P22-001`: `remotion/props.json` has `scene_030` ending at `634.868s` and `scene_031` starting at `635.983s`, producing the known `1.115s` same-section gap.
- [x] (2026-05-13T21:50:00+07:00) Confirmed current evidence for `P22-002`: `remotion/src/components/VisualAssetScene.tsx` renders video assets with `<OffthreadVideo src={staticFile(asset.publicPath)} muted style={styles.media} />` and does not explicitly loop video playback.
- [x] (2026-05-13T21:50:00+07:00) Created this Phase 23 ExecPlan.
- [x] (2026-05-13T21:58:00+07:00) Milestone 1: Regenerated and inspected the current timeline, confirmed the conclusion gap source, inspected the current Remotion video path and type definitions, and chose exact implementation approaches for Milestone 2 and Milestone 3.
- [x] (2026-05-13T22:21:54+07:00) Milestone 2: Implemented explicit Remotion video looping for prepared AI_VIDEO/B_ROLL video assets, validated typecheck and pytest, prepared all 17 visual assets, verified preflight, and rendered the segment preview successfully after rerunning with Chrome launch permission.
- [x] (2026-05-13T22:31:07+07:00) Milestone 3: Added a conservative timeline-builder continuity adjustment for suspicious same-section gaps, added focused tests, regenerated the sample timeline, verified `validate-timeline` now reports zero warnings, exported Remotion props with zero warnings, and confirmed Remotion typecheck still passes.
- [x] (2026-05-13T22:43:00+07:00) Milestone 4: Ran full prepared visual validation with all 17 visuals, verified zero timeline/export/preflight warnings or errors, passed Remotion typecheck, rendered the 900-frame segment preview after Chrome launch permission, and passed pytest.
- [x] (2026-05-13T22:54:14+07:00) Milestone 5: Cleaned validation props, verified clean warning-only visual state, passed Remotion typecheck and pytest, reviewed artifacts, restored generated `remotion/props.json` out of commit candidates, and recorded the source/tests/docs commit recommendation.

## Surprises & Discoveries

- Observation: The current conclusion gap is visible directly in clean Remotion props.
  Evidence: `scene_030` in `remotion/props.json` has `end_sec: 634.868`; `scene_031` has `start_sec: 635.9830000000001`; the difference is `1.115s`.
- Observation: The validator reports same-section gaps greater than one second as warnings, not errors.
  Evidence: `synccut/timeline_validator.py` defines `SUSPICIOUS_GAP_SEC = 1.0` and `_validate_overlaps_and_gaps()` appends warning text such as `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.
- Observation: The current prepared visual video renderer does not request loop behavior.
  Evidence: `remotion/src/components/VisualAssetScene.tsx` imports `OffthreadVideo` from `remotion` and renders it with `src`, `muted`, and `style` only.
- Observation: The installed Remotion package exposes loop support on the main `Video` path but `OffthreadVideo` typed props do not include a regular `loop` prop.
  Evidence: `remotion/node_modules/remotion/dist/cjs/video/props.d.ts` defines `RemotionVideoProps` from native video props, while `RemotionOffthreadVideoProps` is limited to `MandatoryOffthreadVideoProps`, `OptionalOffthreadVideoProps`, and trim props. The implementation of `remotion/dist/cjs/video/Video.js` has loop-specific handling; `OffthreadVideo.js` does not expose the same public `loop` prop.
- Observation: The `07_CONCLUSION` gap comes from alignment timestamps and scene dialogue segmentation, not from Remotion export rounding.
  Evidence: A fresh `timeline.json` has `scene_030` matched to `sentence:0:0` through `sentence:0:4`, with local timing `0.0s-30.825s`. It has `scene_031` matched to `sentence:1:0` through `sentence:1:5`, with local timing `31.94s-66.792s`. `examples/alignments/07_CONCLUSION_alignment_tmp.json` has paragraph 0 ending at `30.825s` and paragraph 1 starting at `31.94s`, so the source gap is `1.115s`.
- Observation: The timeline builder preserves matched alignment spans exactly.
  Evidence: `synccut/timeline_builder.py` sets each scene's `start_sec` and `end_sec` from `match.local_start_sec` and `match.local_end_sec`. `_match_sentences()` returns the first matched sentence start and last matched sentence end. It does not currently smooth same-section gaps between adjacent scene spans.
- Observation: The current Remotion visual asset scene has no `DataSceneFrame` wrapper to preserve.
  Evidence: `remotion/src/components/VisualAssetScene.tsx` renders `AbsoluteFill`, media, tint, header, and metadata directly. The Milestone 2 edit should preserve that layout exactly except for the video component used in the video branch.
- Observation: The planned Remotion `Video` loop implementation typechecked without additional dependencies or schema changes.
  Evidence: After replacing the video branch in `remotion/src/components/VisualAssetScene.tsx`, `cd remotion && npm run typecheck` exited successfully.
- Observation: Browser launch remains sandbox-sensitive, but the segment render works with Chrome permission.
  Evidence: The first `npm run render:segment:local` failed with `SIGTRAP` and `setsockopt: Operation not permitted`. The same command succeeded after rerunning with browser launch permission, rendered and encoded `900/900` frames, and wrote `out/segment.mp4` at `40.7 MB`.
- Observation: Prepared visual preflight still has one unrelated warning after Milestone 2.
  Evidence: Verified preflight reported `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, `file_errors: 0`, and a single warning for the known `07_CONCLUSION` gap that belongs to Milestone 3.
- Observation: The Milestone 3 continuity adjustment removed the real sample's only timeline warning.
  Evidence: After regenerating `timeline.json`, `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, and `warnings: 0`.
- Observation: `scene_030` now absorbs the alignment pause while `scene_031` starts at the same time as before.
  Evidence: Before Milestone 3, `scene_030` ended at global `634.868s` and local `30.825s`, while `scene_031` started at global `635.983s` and local `31.94s`. After Milestone 3, `scene_030` ends at global `635.983s` and local `31.94s`; `scene_031` still starts at global `635.983s` and local `31.94s`.
- Observation: The continuity adjustment is conservative and section-local.
  Evidence: Focused tests cover a `1.115s` same-section gap being closed, the next scene start remaining unchanged, no overlap being introduced, unrelated section boundaries not being merged, and contiguous same-section scenes remaining unchanged.
- Observation: Milestone 4 validation confirmed the combined timing and visual-loop code path with prepared local assets.
  Evidence: Fresh `build-timeline`, `validate-timeline`, `inspect`, and `export-remotion` succeeded. `validate-timeline` reported `warnings: 0`, and `export-remotion` reported `warnings: 0`. After sequential audio and visual preparation, `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: ok`, `audio_prepared: 7`, `visual_prepared: 17`, `visual_missing: 0`, `warnings: 0`, `errors: 0`, and `file_errors: 0`.
- Observation: Audio and visual preparation must be run sequentially when both mutate `remotion/props.json`.
  Evidence: During Milestone 4 validation, running `prepare-remotion-assets` and `prepare-visual-assets` concurrently caused the later write to omit audio `public_path` fields, so preflight reported 14 missing audio public-path errors. Re-running the same two commands sequentially restored the expected prepared state and preflight `status: ok`. This was a validation sequencing mistake, not a source-code bug.
- Observation: Browser launch remains sandbox-sensitive, and the segment render still succeeds with Chrome launch permission.
  Evidence: The first Milestone 4 `npm run render:segment:local` failed with `SIGTRAP` and `setsockopt: Operation not permitted`. The same command succeeded when rerun with browser launch permission, rendered and encoded `900/900` frames, and produced `remotion/out/segment.mp4` with `ls -lh` size `39M` (`40.7 MB` reported by Remotion).
- Observation: Milestone 5 clean props validation matched the intended no-visual-prep state.
  Evidence: After regenerating the timeline, exporting props, and preparing audio only, `validate-timeline` reported `warnings: 0`. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, and `file_errors: 0`.
- Observation: `remotion/props.json` was a generated validation diff after cleanup because the tracked sample props still contain the old `07_CONCLUSION` warning.
  Evidence: `git diff -- remotion/props.json` showed only the regenerated `scene_030` timing/frame change and root warnings changing from the old gap warning to `[]`. Because committing generated sample props was not approved for this phase, the file was restored to the tracked state after validation so it is no longer a commit candidate.

## Decision Log

- Decision: Treat Phase 23 as a polish phase with limited implementation scope.
  Rationale: Human playback review already produced concrete issues. This phase should fix those issues without expanding into media generation, media probing, schema changes, new render scripts, or command behavior changes.
  Date/Author: 2026-05-13 / Codex
- Decision: Implement explicit looping for short video assets rather than verifying or relying on current end-of-video behavior.
  Rationale: The user explicitly chose loop behavior and said there is no need to further verify whether current behavior freezes. The renderer should request loop behavior directly.
  Date/Author: 2026-05-13 / Codex
- Decision: Prefer a Remotion-side video looping fix without props schema changes.
  Rationale: The issue is about rendering local prepared video assets for their full scene duration. The current props already tell Remotion whether an asset is a video through `getPreparedVisualAsset()`, and Remotion already controls scene duration through `Sequence` in `remotion/src/Video.tsx`.
  Date/Author: 2026-05-13 / Codex
- Decision: For the conclusion gap, investigate input timing first and change timeline generation only if it is a clear builder bug.
  Rationale: The gap appears in generated timeline/props and is based on matched dialogue timing. If the source alignment or scene dialogue produces the gap, the least risky fix may be input/timing polish. If the builder is incorrectly leaving a gap that should be closed, that should be fixed with tests.
  Date/Author: 2026-05-13 / Codex
- Decision: Implement Milestone 2 by replacing the `OffthreadVideo` video branch in `remotion/src/components/VisualAssetScene.tsx` with Remotion's typed `Video` component and `loop`.
  Rationale: The installed `remotion` package exports `Video`, and its props are based on native video props that include `loop`. `OffthreadVideo` in this installed package does not expose a normal typed `loop` prop. Using `Video` with `src={staticFile(asset.publicPath)}`, `muted`, `loop`, and the existing `styles.media` is the smallest type-safe renderer change that explicitly loops prepared video assets. Images, placeholders, metadata layout, `staticFile()`, and schema remain unchanged.
  Date/Author: 2026-05-13 / Codex
- Decision: Implement Milestone 3 as a narrow timeline-building continuity polish that absorbs suspicious same-section gaps by extending the previous scene to the next scene start, instead of editing alignment source timestamps.
  Rationale: The 1.115 second gap is real in the alignment input, so changing `examples/alignments/07_CONCLUSION_alignment_tmp.json` would falsify source timing. The user wants smoother continuity, and the visible issue is the scene gap between adjacent visual sequences. Extending the previous same-section scene over a non-overlapping suspicious gap preserves the next scene start, preserves total section duration, avoids schema changes, and should remove the validator warning. This is a timeline generation behavior change and needs focused tests.
  Date/Author: 2026-05-13 / Codex
- Decision: Reuse `SUSPICIOUS_GAP_SEC` from `synccut.timeline_validator` as the builder smoothing threshold.
  Rationale: The polish is specifically meant to absorb gaps that would otherwise be reported by the validator as suspicious. Sharing the threshold keeps generation and validation aligned and avoids inventing a second, slightly different cutoff.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reviewing the current Phase 22 findings, Remotion visual rendering code, Remotion package behavior available in `node_modules`, timeline validation logic, and the current `remotion/props.json`. No code, schema, command behavior, media, render output, generated props, commit, or tag was changed while creating the plan.

The intended outcome is that Phase 23 removes or handles the two release-polish blockers recorded from human review. `P22-001` should no longer surface as an unexplained conclusion gap warning, or it should be explicitly reduced/handled and documented if the source alignment requires it. `P22-002` should be addressed by an explicit Remotion-side looping behavior for prepared video assets so short AI_VIDEO/B_ROLL videos continue through the full scene duration.

Milestone 1 is complete. The investigation regenerated `timeline.json`, reproduced the current warning, and inspected the relevant generated and source JSON. The gap between `scene_030` and `scene_031` is not caused by Remotion export rounding; it is the alignment pause between paragraph 0 ending at `30.825s` and paragraph 1 starting at `31.94s`, carried through exact sentence matching by the timeline builder. The chosen gap-fix direction is to add narrow timeline-building continuity polish that extends a previous same-section scene across suspicious non-overlapping gaps, with tests, instead of editing alignment timestamps.

For video looping, Milestone 1 found that the current video branch uses `OffthreadVideo` without loop behavior, while the installed Remotion `Video` component is type-compatible with native `loop`. The chosen Milestone 2 implementation is to switch only the video asset branch in `remotion/src/components/VisualAssetScene.tsx` to `Video` with `loop`, keeping images, placeholder fallback, muted playback, `staticFile(asset.publicPath)`, and the existing metadata layout unchanged. This is expected to affect every prepared AI_VIDEO and B_ROLL visual asset whose prepared file kind is `video`; prepared still images remain unchanged.

Milestone 2 is complete. `remotion/src/components/VisualAssetScene.tsx` now imports `Video` from `remotion` instead of `OffthreadVideo`, and the video asset branch renders `<Video src={staticFile(asset.publicPath)} muted loop style={styles.media} />`. Image assets still use `Img`, missing or unsupported assets still fall back to `PlaceholderScene`, labels and metadata layout are unchanged, and no schema, package, npm script, Python command behavior, or media file changes were made.

Validation for Milestone 2 passed. `cd remotion && npm run typecheck` succeeded. `.venv/bin/python -m pytest` collected 208 tests and all 208 passed. Fresh props were regenerated and all local visual assets were prepared: `prepare-visual-assets` reported `visual_copied: 0`, `visual_reused: 17`, `visual_overwritten: 0`, `visual_missing: 0`, and `visual_assets: 17`. `inspect-visual-assets` reported `target_scenes: 17`, `prepared: 17`, `missing: 0`, and `unsupported: 0`. Verified preflight reported `status: warning`, `visual_prepared: 17`, `visual_missing: 0`, `visual_unsupported: 0`, `errors: 0`, and `file_errors: 0`; the only warning was the known `07_CONCLUSION` gap.

The optional segment render was attempted. The sandboxed run failed with the known browser-launch signature: closed with `SIGTRAP` and `setsockopt: Operation not permitted`. The same `npm run render:segment:local` command succeeded when rerun with Chrome launch permission, rendered and encoded all `900` frames, and wrote `remotion/out/segment.mp4` at `40.7 MB`. `remotion/props.json` is currently prepared with validation visual public paths and should not be committed; later cleanup is planned in Milestone 5.

Milestone 3 is complete. `synccut/timeline_builder.py` now runs a small post-match continuity adjustment over generated timeline entries. For adjacent scenes in the same section, when the next scene starts after the previous scene and the gap is greater than `SUSPICIOUS_GAP_SEC`, the builder extends the previous scene's `timing.end_sec`, `timing.local_end_sec`, and `timing.duration_sec` to the next scene start. It does not move the next scene start, does not cross section boundaries, does not change section duration, and does not affect contiguous scenes.

Focused tests were added in `tests/test_timeline_builder.py`. They verify that a same-section gap around `1.115s` is closed by extending the previous scene, no overlap is introduced, the adjacent scene start remains unchanged, unrelated section boundaries are not merged, and normal contiguous scenes stay unchanged. `.venv/bin/python -m pytest` collected 212 tests and all 212 passed.

Real sample validation now matches the desired timing-polish result. After regenerating `timeline.json`, `validate-timeline` reported `warnings: 0`. `inspect timeline.json` showed `scene_030 604.043s-635.983s 31.940s` and `scene_031 635.983s-670.835s 34.852s`, so the gap is closed while `scene_031` start remains unchanged. `export-remotion` wrote `remotion/props.json` with `warnings: 0`, and `cd remotion && npm run typecheck` passed. `remotion/props.json` was regenerated for validation and should not be committed unless intentionally approved later.

Milestone 4 is complete. Fresh prepared validation now covers both Phase 23 fixes together. The sample timeline rebuilt successfully, `validate-timeline` reported zero warnings, `inspect timeline.json` showed the smoothed `07_CONCLUSION` timing, and `export-remotion` reported zero warnings. After audio and visual assets were prepared sequentially, `inspect-visual-assets` reported all 17 target scenes prepared with no missing or unsupported visuals. Verified preflight reported `status: ok`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_prepared: 17`, `visual_missing: 0`, `warnings: 0`, `errors: 0`, and `file_errors: 0`.

Remotion typecheck passed. The first segment render attempt hit the expected sandbox browser-launch failure (`SIGTRAP` and `setsockopt: Operation not permitted`), and the rerun with Chrome launch permission succeeded. The successful render encoded `900/900` frames and produced `remotion/out/segment.mp4`, reported by Remotion as `40.7 MB` and by `ls -lh` as `39M`. The full final render was intentionally skipped for this milestone; the segment render validates the combined loop/timing render path, and final render can be left for post-polish release validation.

Python validation passed after the segment render. `.venv/bin/python -m pytest` collected 212 tests and all 212 passed. Artifact review showed source/doc commit candidates for the Phase 23 implementation plus prepared validation artifacts: `remotion/props.json` is currently prepared for validation and must be cleaned in Milestone 5; `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, and caches are ignored and should not be committed.

Milestone 5 is complete. The final cleanup regenerated `timeline.json`, validated the timeline with zero warnings, exported clean Remotion props, and prepared audio assets only. `prepare-visual-assets` was intentionally not run after cleanup. Clean visual readiness reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Verified preflight reported `status: warning` only because clean props intentionally omit local visual public paths; it also reported `errors: 0`, `file_errors: 0`, `visual_prepared: 0`, and `visual_missing: 17`.

Final validation passed. `cd remotion && npm run typecheck` exited successfully. `.venv/bin/python -m pytest` collected 212 tests and all 212 passed. The final artifact review found the expected ignored generated/local paths: `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, Python caches, and pytest cache. `remotion/props.json` initially differed only because regenerated sample props reflect the new smoothed timing and zero warnings; it was restored to the tracked state because this phase did not approve committing generated sample props.

Final Phase 23 review: `P22-002` is fixed by explicit Remotion video looping in `VisualAssetScene.tsx`. `P22-001` is fixed in generated timelines by the timeline-builder same-section suspicious-gap smoothing, and the sample now validates with zero timeline/export warnings when regenerated. Prepared preflight reached `status: ok` in Milestone 4, and the segment preview succeeded with Chrome permission. This phase did not use ffmpeg/ffprobe, did not probe/transcode media, did not generate/download/scrape media, did not change schemas, did not add render scripts, and did not commit binary or generated media.

Remaining risk: the tracked `remotion/props.json` still represents an older generated sample and should not be used as evidence of the new timing behavior until regenerated. That is intentional for this phase's commit policy; the source/tests/docs changes are the commit candidates. Recommended commit candidates are `remotion/src/components/VisualAssetScene.tsx`, `synccut/timeline_builder.py`, `tests/test_timeline_builder.py`, and `docs/plans/timing-and-visual-duration-polish.md`. Recommended commit message: `Polish timing gaps and loop visual asset videos`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a Remotion project under `remotion/`. The Python CLI builds `timeline.json` from `examples/scenes.json`, `examples/audio`, and `examples/alignments`, exports Remotion props to `remotion/props.json`, prepares section audio into `remotion/public/audio`, and can copy local visual assets from `assets/visuals` into `remotion/public/visuals`. Remotion consumes `remotion/props.json` and renders scenes from `remotion/src/Video.tsx`.

The current release decision is `needs-polish`, recorded in `docs/final-render-quality-review.md`. Human playback review recorded two issues. `P22-001` is a medium severity `section_gap` in `07_CONCLUSION` between `scene_030` and `scene_031`. `P22-002` is a high severity `visual_ends_before_audio` issue across multiple AI_VIDEO and B_ROLL scenes whose local video files are shorter than narration.

In Remotion, `remotion/src/Video.tsx` maps every scene to a Remotion `Sequence` with `from={scene.start_frame}` and `durationInFrames={scene.duration_frames}`. That means each scene component only needs to fill the local sequence time. The visual asset path is rendered by `remotion/src/components/VisualAssetScene.tsx`. Images use `<Img>`. Videos currently use `<OffthreadVideo>`. Missing or invalid assets fall back to `PlaceholderScene` through `getPreparedVisualAsset()`.

The current `remotion/props.json` is clean after Phase 21 and does not necessarily contain prepared visual public paths unless `prepare-visual-assets` has been rerun. For render validation in this phase, regenerate the timeline and props, prepare audio, run `prepare-visual-assets`, then run preflight before rendering.

The known conclusion timing values in current props are: `scene_030` starts at `604.043s`, ends at `634.868s`, and has local end `30.825s`; `scene_031` starts at `635.983s`, starts locally at `31.94s`, and ends at `670.835s`. The gap is `635.983 - 634.868 = 1.115s`. The validator warns because this gap is greater than the suspicious-gap threshold of one second.

## Plan of Work

Milestone 1 is complete. The investigation regenerated a fresh `timeline.json`, inspected the `07_CONCLUSION` section with `synccut inspect timeline.json`, compared `scene_030` and `scene_031` generated timing to `examples/scenes.json` and `examples/alignments/07_CONCLUSION_alignment_tmp.json`, and inspected Remotion video component types. The conclusion gap source is the alignment pause between paragraph 0 and paragraph 1. The selected loop implementation is Remotion `Video` with `loop`. The selected gap smoothing direction is a tested timeline-builder post-match continuity adjustment for suspicious same-section gaps.

Milestone 2 implements explicit video looping in Remotion. Edit `remotion/src/components/VisualAssetScene.tsx`. Replace the `OffthreadVideo` import with `Video` from `remotion`, and in the video branch render `Video` with `src={staticFile(asset.publicPath)}`, `muted`, `loop`, and `style={styles.media}`. Images should remain rendered through `Img`. Placeholder fallback should remain unchanged. Do not change `remotion/src/types.ts`, props schema, Python asset preparation, `remotion/src/Video.tsx`, or metadata layout.

Milestone 3 smooths the `07_CONCLUSION` gap. Edit `synccut/timeline_builder.py` only if the tests for the chosen continuity adjustment justify it. After matching scenes within a section, when two adjacent scenes are in the same section, non-overlapping, and separated by a suspicious gap greater than the validator threshold, extend the previous scene's `timing.end_sec`, `timing.local_end_sec`, and `timing.duration_sec` to the next scene's start. Keep the next scene start unchanged. Keep section duration unchanged. Add focused tests showing that a suspicious same-section pause is absorbed and that overlaps are not introduced. The preferred outcome is that `validate-timeline timeline.json` no longer reports `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.

Milestone 4 validates the full prepared visual workflow and render preview. Regenerate timeline and props from examples, prepare audio, prepare all local visuals, run visual readiness, run verified preflight, run Remotion typecheck, run Python tests, and render the existing segment workflow. If segment render passes and time allows, optionally run the existing final render workflow. Do not add render scripts and do not call Remotion from Python.

Milestone 5 cleans up and performs final review. Regenerate clean props and audio without running `prepare-visual-assets`, so `remotion/props.json` is not left with temporary local visual public paths. Confirm generated media and render outputs remain ignored. Commit recommendation should include only source and docs required by the polish, not `remotion/out`, `remotion/public`, `assets/visuals`, `timeline.json`, or validation-only `remotion/props.json`.

## Concrete Steps

For Milestone 1, run investigation from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json

The expected current validation output includes one warning:

    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

Inspect the conclusion entries in `timeline.json`, `remotion/props.json`, `examples/scenes.json`, and `examples/alignments/07_CONCLUSION_alignment_tmp.json`. Use Python JSON reading or shell text inspection only. Do not use ffmpeg, ffprobe, media probing, or media duration checks.

For Milestone 2, edit the chosen Remotion rendering file, most likely `remotion/src/components/VisualAssetScene.tsx`. Then run:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

If typecheck passes and local browser launch is available, prepare the render data and run a segment preview:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    cd remotion
    npm run render:segment:local
    cd ..

For Milestone 3, implement the timing fix in the smallest appropriate place identified by Milestone 1. If Python source changes are needed, add or update focused tests. Then run:

    .venv/bin/python -m pytest
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

The preferred expected result is that `validate-timeline timeline.json` reports no `07_CONCLUSION` gap warning. If another warning remains, record exactly what it is and why it is acceptable or still needs work.

For Milestone 4, run the full prepared validation sequence:

    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    cd remotion
    npm run typecheck
    npm run render:segment:local
    cd ..
    .venv/bin/python -m pytest

If final render is explicitly attempted, use only the existing script:

    cd remotion
    npm run render:final:local
    cd ..

For Milestone 5, clean validation-only prepared props:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    git status --short --ignored

Do not run `prepare-visual-assets` after the final cleanup unless the user explicitly wants prepared props left in the worktree.

## Validation and Acceptance

The work is accepted when AI_VIDEO and B_ROLL prepared video assets explicitly loop for the whole scene duration, image assets and placeholders still render as before, `npm run typecheck` passes from `remotion/`, and `.venv/bin/python -m pytest` passes from the repository root.

Prepared visual preflight should pass with all 17 real local visual assets:

    target_scenes: 17
    prepared: 17
    missing: 0
    unsupported: 0
    errors: 0
    file_errors: 0

The `07_CONCLUSION` gap should be fixed or explicitly documented as accepted. The preferred acceptance output is that `validate-timeline timeline.json` no longer prints:

    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

At least `npm run render:segment:local` should succeed with Chrome launch permission. If Chrome launch is blocked by sandbox, record the exact error and rerun with permission if available. Do not add workaround code. If final render is attempted and succeeds, record `remotion/out/final.mp4` size and keep it ignored.

## Idempotence and Recovery

The generation and preparation commands are safe to rerun. `build-timeline` rewrites generated `timeline.json`; `export-remotion` rewrites `remotion/props.json`; `prepare-remotion-assets` and `prepare-visual-assets` copy or reuse ignored public assets. These generated artifacts should not be committed unless explicitly approved.

If a Remotion loop implementation fails typecheck, revert only the attempted Remotion edit from this phase and try the alternative Remotion-supported approach identified in Milestone 1. Do not change media files to compensate for renderer behavior.

If the conclusion gap fix introduces overlaps, invalid timings, or broader fixture churn, stop and record the failure. Prefer a smaller input/timing adjustment over changing global timeline semantics. If timeline builder logic must change, add focused tests that demonstrate the old gap behavior and the corrected behavior.

If render fails because Chrome launch is blocked, record the exact browser sandbox error and rerun with Chrome launch permission if available. If render fails due a corrupt local asset, treat that as a local asset issue and do not use ffmpeg/ffprobe to inspect it in this phase.

## Artifacts and Notes

Important generated/local paths must remain uncommitted:

- `timeline.json`
- `remotion/props.json` if changed only by local validation regeneration or visual preparation
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.venv/`
- `remotion/node_modules/`
- Python, pytest, and Node caches

Expected source/docs commit candidates after successful implementation are limited to the minimal files touched for this phase. Likely candidates are `remotion/src/components/VisualAssetScene.tsx`, a timing input or timeline-builder file if needed for the conclusion gap, related focused tests if Python behavior changes, and `docs/plans/timing-and-visual-duration-polish.md`. If README or Remotion README user-facing behavior needs a brief loop-behavior note, update only the necessary doc and record the decision here.

## Interfaces and Dependencies

Use existing SyncCut CLI commands only. Do not add a Python command that invokes Remotion. Do not add Remotion npm scripts. Do not add dependencies.

The primary Remotion interface to edit is `remotion/src/components/VisualAssetScene.tsx`. It currently receives `scene`, `section`, labels, and accent color, gets the asset with `getPreparedVisualAsset(scene.visual.public_path)`, renders images with `Img`, videos with `OffthreadVideo`, and falls back to `PlaceholderScene` if no valid local visual exists. The target behavior is that the video branch explicitly loops video media while preserving `muted`, `staticFile(asset.publicPath)`, deterministic styles, labels, metadata strip, and placeholder fallback.

The timeline validation interface is `synccut/timeline_validator.py`. Its gap warning logic is `_validate_overlaps_and_gaps()`, with `SUSPICIOUS_GAP_SEC = 1.0`. The timeline inspection interface is `synccut/timeline_inspector.py`, which prints section and scene intervals. The Remotion export interface is `synccut/remotion_exporter.py`, which maps `timeline.json` scene seconds to frame ranges using `seconds_to_frame()`.

Do not change schemas unless a later explicit decision says it is unavoidable. The current Remotion props already contain `scene.duration_frames`, `scene.visual.public_path`, and enough visual type information to loop videos without schema changes.

## Change Note

2026-05-13 / Codex: Created this ExecPlan for Phase 23 timing and visual-duration polish. The plan records current render-review findings, the known `07_CONCLUSION` gap evidence, the current Remotion video rendering behavior, the chosen explicit loop direction, milestone structure, validation commands, artifact policy, and exclusions.

2026-05-13 / Codex: Updated after Milestone 1 investigation. The plan now records that the conclusion gap comes from source alignment paragraph timing carried through exact sentence matching, chooses Remotion `Video` with `loop` for Milestone 2, and chooses a tested timeline-builder continuity adjustment for suspicious same-section gaps in Milestone 3.

2026-05-13 / Codex: Updated after Milestone 2 implementation. The plan records the `VisualAssetScene.tsx` switch from `OffthreadVideo` to `Video` with `loop`, passing typecheck and pytest, prepared visual preflight results, the sandbox browser-launch failure, and the successful permissioned segment render.

2026-05-13 / Codex: Updated after Milestone 3 implementation. The plan records the timeline-builder continuity adjustment, focused test coverage, zero-warning sample validation, before/after `scene_030` and `scene_031` timing, Remotion typecheck result, and validation artifact status.

2026-05-13 / Codex: Updated after Milestone 4 validation. The plan records full prepared visual validation, zero-warning verified preflight, the sequential preparation correction, Remotion typecheck, sandbox Chrome behavior, successful segment render output, skipped final render, pytest result, and artifact status before Milestone 5 cleanup.

2026-05-13 / Codex: Updated after Milestone 5 cleanup and final review. The plan records clean props validation, warning-only clean visual preflight, final typecheck and pytest results, generated artifact review, restoration of `remotion/props.json` out of commit candidates, risks, and the recommended source/tests/docs commit.
