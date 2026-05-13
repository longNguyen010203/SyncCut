# Human playback review and timing issue inventory

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to conduct the human playback review, update the review document, classify issues, and decide release readiness from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut has produced a full local final render for the TSMC sample at `remotion/out/final.mp4`. The render completed successfully, but the current release decision remains `needs-polish` because no human has yet watched and listened to the full video. This phase turns that remaining human review into a structured issue inventory: a reviewer plays the final MP4 locally, records timestamped timing and quality issues, classifies their severity and likely source, and decides whether the video is `release-ready-with-known-warnings`, still `needs-polish`, or `blocked`.

After this phase, maintainers should have a text-only review record in `docs/final-render-quality-review.md` that says what was observed, where issues occur, which layer likely owns each issue, and what should happen next. This phase is review and documentation only. It must not edit Python source, Remotion source, schemas, command behavior, render scripts, media files, or generated assets. It must not call ffmpeg or ffprobe, probe or transcode media, generate or download media, commit binary media, rerender unless explicitly approved later, commit, or tag a release.

## Progress

- [x] (2026-05-13T20:41:46+07:00) Read the requested project references: `AGENTS.md`, `.agent/PLANS.md`, `README.md`, `docs/final-render-quality-review.md`, `docs/plans/final-release-render-quality-review.md`, `docs/plans/tsmc-complete-real-visual-assets.md`, `docs/tsmc-visual-asset-manifest.md`, `remotion/README.md`, `remotion/package.json`, and `.gitignore`.
- [x] (2026-05-13T20:41:46+07:00) Confirmed the current context from the docs: Phase 21 produced `remotion/out/final.mp4`, render evidence is good, `remotion/props.json` was cleaned, and the release decision remains `needs-polish` pending human playback review.
- [x] (2026-05-13T20:41:46+07:00) Created this Phase 22 ExecPlan for human playback review and timing issue inventory.
- [x] (2026-05-13T20:51:08+07:00) Milestone 1: Added the structured human review template, issue categories, issue log table, timestamp-to-scene helper notes, and release decision options to `docs/final-render-quality-review.md`.
- [x] (2026-05-13T21:34:41+07:00) Milestone 2: Recorded user-provided human playback findings in `docs/final-render-quality-review.md`, replacing the placeholder issue row with concrete timing and visual-duration issues.
- [x] (2026-05-13T21:37:51+07:00) Milestone 3: Classified `P22-001` and `P22-002`, kept the release decision as `needs-polish`, and defined Phase 23 scope around timing and visual-duration polish.
- [x] (2026-05-13T21:43:15+07:00) Milestone 4: Completed final review and artifact check; commit candidates are docs only and the recommended commit message is `Record human playback timing review findings`.

## Surprises & Discoveries

- Observation: The final render artifact exists outside git and should remain uncommitted.
  Evidence: Phase 21 recorded successful output at `remotion/out/final.mp4`; `.gitignore` ignores `remotion/out/`.
- Observation: The quality review document already exists but intentionally does not claim playback pass/fail results.
  Evidence: `docs/final-render-quality-review.md` records render evidence and marks playback-specific checks as `needs human review`.
- Observation: The current final render evidence is strong enough to start human playback review.
  Evidence: Phase 21 recorded `prepared: 17`, `missing: 0`, `unsupported: 0`, verified preflight `errors: 0` and `file_errors: 0`, Python tests `208 passed`, a successful final render of all `22584` frames, and output size `242M` by `ls`.
- Observation: `remotion/props.json` is clean after Phase 21.
  Evidence: Phase 21 Milestone 4 recorded clean visual readiness as `prepared: 0`, `missing: 17`, and `unsupported: 0` after regenerating props and preparing audio only. If another render is needed later, visual assets must be prepared again first.
- Observation: Milestone 1 required only a documentation template update.
  Evidence: `docs/final-render-quality-review.md` already had render evidence and a manual review checklist; this milestone added the missing structured issue log and timestamp helper without performing playback review.
- Observation: The known `07_CONCLUSION` gap is not very disruptive in playback, but the user wants it smoothed for continuity.
  Evidence: The user reported that the known gap is acceptable enough to watch but should be handled in the next polish phase.
- Observation: Multiple AI_VIDEO and B_ROLL videos are shorter than their narration spans.
  Evidence: The user reported that many prepared visual assets end before narration, which is understandable because the local source videos are shorter than scene audio duration.
- Observation: The first human review pass was useful but not exhaustive.
  Evidence: The user noted that other issues may not have been noticed and should be allowed for future polish or release phases.

## Decision Log

- Decision: Use `docs/final-render-quality-review.md` as the single human playback review record.
  Rationale: The file already contains final render evidence and a checklist. Extending it with a structured issue log keeps release evidence in one text-only place and avoids duplicating review state.
  Date/Author: 2026-05-13 / Codex
- Decision: Treat this phase as documentation and review only, with no rerender by default.
  Rationale: The final MP4 already exists and the next missing evidence is human playback review. Rerendering would be expensive and unnecessary unless the human issue inventory identifies a fix and the user explicitly approves another render.
  Date/Author: 2026-05-13 / Codex
- Decision: Do not use ffmpeg, ffprobe, media probing, or media normalization for review.
  Rationale: The purpose is human playback quality review, not technical media inspection. The user explicitly excluded probing/transcoding and direct ffmpeg/ffprobe calls.
  Date/Author: 2026-05-13 / Codex
- Decision: Keep the release decision as `needs-polish`.
  Rationale: The file renders successfully and no blocker was recorded, but `P22-002` is a high-severity visual-duration mismatch across multiple AI_VIDEO/B_ROLL scenes and should be handled before release tagging.
  Date/Author: 2026-05-13 / Codex
- Decision: Define Phase 23 scope around `P22-001` and `P22-002`.
  Rationale: `P22-001` maps cleanly to timing polish for the conclusion gap, while `P22-002` maps to visual-duration polish for short local videos. These are the concrete release-relevant findings from the first human playback pass.
  Date/Author: 2026-05-13 / Codex
- Decision: Defer other subtle issues to later polish or release phases unless they become blockers.
  Rationale: The user explicitly noted the review may not be exhaustive. The current phase should capture known findings without expanding scope into speculative fixes.
  Date/Author: 2026-05-13 / Codex

## Outcomes & Retrospective

This plan has been created after reviewing the current repository instructions, release docs, Phase 21 render evidence, complete TSMC visual manifest, Remotion render scripts, and artifact policy. No source files, schemas, command behavior, render scripts, media, generated artifacts, commits, or tags were changed while creating this plan.

The expected outcome is a structured text issue inventory and a clear release decision. Success means a human reviewer has watched and listened to `remotion/out/final.mp4`, recorded issue rows with timestamps and scene or section references where possible, classified severity and suspected layer, and updated `docs/final-render-quality-review.md` with a release decision. If the only remaining issues are minor and accepted, the decision can become `release-ready-with-known-warnings`. If timing, audio, visual quality, black-screen, placeholder, or section duration issues need correction, the decision remains `needs-polish`. If the video cannot play or audio is unusable, the decision becomes `blocked`.

Milestone 1 is complete. `docs/final-render-quality-review.md` now contains human playback instructions, issue category definitions, a structured issue log with the required columns, timestamp-to-scene helper commands, and explicit release decision options. No playback review was performed in this milestone. The next step is for a human reviewer to watch and listen to `remotion/out/final.mp4`, replace the placeholder issue-log row with real findings or an `id` of `none`, and update the release decision.

Milestone 2 is complete. The issue log in `docs/final-render-quality-review.md` now records two user-provided playback findings: the known `07_CONCLUSION` gap should be smoothed for continuity, and multiple AI_VIDEO/B_ROLL prepared visual assets are shorter than the narration audio. The release decision remains `needs-polish`. The next phase should focus on timing and visual-duration polish, especially smoothing the conclusion gap and defining how Remotion should handle short video assets through looping, freezing, extending, replacement, or timing adjustment.

Milestone 3 is complete. The recorded issues are classified: `P22-001` is a medium-severity `section_gap` owned by Phase 23 timing polish, and `P22-002` is a high-severity `visual_ends_before_audio` issue owned by Phase 23 visual-duration polish. No blocker issue prevents the file from rendering, but the release decision remains `needs-polish` because the visual-duration mismatch should be handled before release tagging. No code, schema, media, render, or command behavior changes were made in this phase.

Milestone 4 is complete. Final review confirms Phase 22 stayed within documentation/review scope: human playback findings are recorded, the structured issue log exists, `P22-001` records the `07_CONCLUSION` gap, `P22-002` records short AI_VIDEO/B_ROLL videos, issues are classified, and the release decision remains `needs-polish`. Phase 23 scope is clear: conclusion gap smoothing and short-video duration handling.

Artifact review used `git status --short --ignored`. Commit candidates are docs only: `docs/final-render-quality-review.md` and `docs/plans/human-playback-review-timing-inventory.md`. Generated/local artifacts are ignored, including `remotion/out/`, `remotion/public/`, `assets/`, `timeline.json`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and Python `__pycache__/` directories. `remotion/props.json` is not a commit candidate, and no source, schema, command, or render-script files are modified.

Recommended commit: docs only, with message `Record human playback timing review findings`. No release tag is recommended yet because the decision remains `needs-polish`.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a Remotion project under `remotion/`. The Python CLI builds `timeline.json`, exports `remotion/props.json`, prepares public audio and visual paths, and runs readiness checks. The Remotion project consumes `remotion/props.json` and writes generated render artifacts under `remotion/out/`.

The final video to review is `remotion/out/final.mp4`. It was generated in Phase 21 with the existing npm script `render:final:local`, which renders the full `SyncCutVideo` composition. Phase 21 recorded that Remotion rendered and encoded all `22584` frames, with output size `242M` from `ls -lh` and `253.4 MB` reported by Remotion. At 30 frames per second, `22584` frames is about `752.8` seconds.

The current release decision is `needs-polish`, not because the render failed, but because a human has not yet watched and listened to the output. `docs/final-render-quality-review.md` currently records render evidence and marks playback checks as needing human review. This phase updates that file with actual human playback findings.

`remotion/props.json` was cleaned after Phase 21. Clean props intentionally do not contain local visual public paths, so `inspect-visual-assets remotion/props.json` reports `prepared: 0` and `missing: 17`. That clean state is correct for commit review. If a later task needs to rerender, it must regenerate timeline/props/audio and run `prepare-visual-assets` again before rendering.

The known automated warning is `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. This phase must assess whether that gap is noticeable and acceptable during playback.

## Review Targets

A human reviewer should open `remotion/out/final.mp4` locally with a normal video player and watch/listen for release-impacting issues. The review should confirm whether the video opens and plays, narration audio is audible, audio roughly aligns with section changes, the video does not noticeably continue long after audio ends, audio is not cut off by the video ending, no obvious silence or black screen appears, no AI/B-roll placeholder cards are visible now that all 17 visual assets were prepared for the final render, scene transitions are acceptable, the final section renders correctly, and the known `07_CONCLUSION` gap is either acceptable or logged as an issue.

The reviewer should focus on issue discovery rather than subjective polish alone. Any issue that would embarrass a release, confuse a viewer, or point to timing or asset problems should be recorded with a timestamp and severity.

## Timing Issue Categories

Use the following category values in the issue log. `audio_ends_before_visual` means narration stops while visuals continue in a noticeable way. `visual_ends_before_audio` means visuals end or cut away before narration finishes. `section_gap` means there is an obvious gap between sections or scenes. `section_overlap` means audio or visuals from adjacent sections appear to overlap incorrectly. `scene_too_short` means a scene cuts away too quickly for the narration or visual. `scene_too_long` means a scene lingers too long. `audio_silence` means unexpected silence occurs. `black_screen` means the viewer sees black when content should be visible. `placeholder_visible` means an AI/B-roll placeholder card is visible where the real visual asset should appear. `visual_quality` means the asset is low-quality, confusing, off-topic, badly cropped, distorted, or otherwise unsuitable. `transition_issue` means the transition between scenes or sections feels broken, abrupt, or confusing. `narration_alignment` means the narration timing does not match the displayed scene or section. Use `other` only when none of the named categories fits.

The valid category values are:

- `audio_ends_before_visual`
- `visual_ends_before_audio`
- `section_gap`
- `section_overlap`
- `scene_too_short`
- `scene_too_long`
- `audio_silence`
- `black_screen`
- `placeholder_visible`
- `visual_quality`
- `transition_issue`
- `narration_alignment`
- `other`

## Issue Log Format

Milestone 1 adds or updates a structured issue log in `docs/final-render-quality-review.md`. Use this table shape:

| id | timestamp_start | timestamp_end | section_key | scene_id | category | severity | description | suspected_layer | proposed_next_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `P22-001` | `HH:MM:SS` | `HH:MM:SS` | `07_CONCLUSION` | `scene_030` | `section_gap` | `medium` | Example: noticeable pause before next scene. | `timeline` | Decide whether to adjust timeline inputs in a later polish phase. |

Severity values are `low`, `medium`, `high`, and `blocker`. `low` means it is acceptable or cosmetic. `medium` means it should be considered before release but may be acceptable with a note. `high` means release should wait for a fix unless explicitly waived. `blocker` means the video cannot be released as-is, such as unplayable video, missing audio, a long black screen, or unusable final section.

Suspected layer values should be ordinary and practical. Use `input` for source scene/audio/alignment data problems. Use `timeline` for timing generated from current inputs. Use `remotion` for rendering or component behavior. Use `asset` for visual or audio file quality problems. Use `unknown` when the reviewer cannot reasonably infer the layer.

If no issues are found, leave the table with a single row whose `id` is `none`, category is `other`, severity is `low`, description says `No playback issues found during human review`, and proposed action says `Proceed with known warnings only`.

## Manual Review Method

The human reviewer should open `remotion/out/final.mp4` locally. A normal desktop video player is enough. Do not use ffmpeg or ffprobe. Do not probe, transcode, normalize, or modify the media.

The reviewer should record timestamps in `HH:MM:SS` where possible. If an issue spans time, record both start and end. If the reviewer can identify the scene id from on-screen context or nearby timing, fill `scene_id`. If not, fill `unknown` initially and use the timestamp-to-scene helper notes below.

For mapping a timestamp to the likely scene, use SyncCut timeline inspection only. It is allowed to run:

    .venv/bin/synccut inspect timeline.json

If `timeline.json` is missing or stale, regenerate and inspect from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut inspect timeline.json

This helper output is for reading timeline timing only. It should not mutate source inputs and does not render. Do not run `prepare-visual-assets`, Remotion render commands, ffmpeg, ffprobe, or media probing commands during this phase unless a later user request explicitly changes scope.

To map a timestamp manually, convert it to seconds. For example, `00:30:15` is 1815 seconds. In the inspect output, find the section or scene whose start and end time contains that second. If exact mapping is still unclear, write `unknown` in `scene_id` and describe the observable issue clearly.

## Release Decision Rules

Use `release-ready-with-known-warnings` if the video plays, audio is audible, section alignment is acceptable, no placeholders or major black screens appear, and all remaining issues are minor and explicitly accepted. The known `07_CONCLUSION` gap can be accepted as a known warning if it is not disruptive during playback.

Use `needs-polish` if there are timing, audio, visual quality, black-screen, placeholder, section duration, or transition issues that should be fixed before tagging. This is the current default until human playback review is complete.

Use `blocked` if the video cannot play, audio is unusable, final output is missing, or there is a blocker-severity issue that prevents meaningful review.

Record the decision in `docs/final-render-quality-review.md` with a short reason. If the decision changes from `needs-polish`, update both the decision line and the next recommended action.

## Plan of Work

Milestone 1 is a documentation template step. Update `docs/final-render-quality-review.md` to add the issue category definitions, the structured issue log table, the timestamp-to-scene helper notes, and the release decision rules. Do not change code or generated artifacts. Acceptance for Milestone 1 is that the review doc is ready for a human to fill in without needing to infer table columns or category meanings.

Milestone 2 is the human playback pass. The human reviewer watches and listens to `remotion/out/final.mp4`, then fills the issue log. If the reviewer has timestamps but not scene ids, use `synccut inspect timeline.json` or regenerate `timeline.json` and inspect it to map timestamps to likely sections and scenes. Acceptance for Milestone 2 is that each observed issue has a row with timestamp, category, severity, suspected layer, and proposed next action, or the table records that no issues were found.

Milestone 3 is classification and next-scope decision. Review the filled issue log, group issues by category and suspected layer, identify which issues must be fixed before tagging, and decide whether the next phase should adjust inputs/timeline, replace visual assets, change Remotion rendering behavior, or simply accept known warnings. Acceptance for Milestone 3 is that `docs/final-render-quality-review.md` contains a release decision and a concrete next recommended action.

Milestone 4 is final review and commit recommendation. Run `git status --short --ignored`, confirm generated artifacts and media are ignored, confirm no source/schema/command/render-script changes were made, and recommend committing docs only. Acceptance for Milestone 4 is that commit candidates are documentation files only and no release tag is recommended unless human review has clearly moved the decision to `release-ready-with-known-warnings`.

## Concrete Steps

For Milestone 1, edit only `docs/final-render-quality-review.md` and `docs/plans/human-playback-review-timing-inventory.md`. Add the structured issue log and review instructions. Then run:

    git diff -- docs/final-render-quality-review.md docs/plans/human-playback-review-timing-inventory.md
    git status --short docs/final-render-quality-review.md docs/plans/human-playback-review-timing-inventory.md

For Milestone 2, the human reviewer opens:

    remotion/out/final.mp4

The reviewer fills the issue log in `docs/final-render-quality-review.md`. If timestamp mapping is needed, run from the repository root:

    .venv/bin/synccut inspect timeline.json

If `timeline.json` needs regeneration for timestamp mapping, run:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut inspect timeline.json

For Milestone 3, update `docs/final-render-quality-review.md` with classification notes and the release decision. Do not edit source files or media.

For Milestone 4, run:

    git status --short --ignored

Expected generated/local ignored paths include:

- `.pytest_cache/`
- `.venv/`
- `assets/`
- `examples/`
- `remotion/node_modules/`
- `remotion/out/`
- `remotion/public/`
- Python `__pycache__/` directories
- `timeline.json`

Expected commit candidates should be docs only, normally:

- `docs/final-render-quality-review.md`
- `docs/plans/human-playback-review-timing-inventory.md`

## Validation and Acceptance

The phase is accepted when `docs/final-render-quality-review.md` contains a structured issue log, playback findings from a human reviewer or an explicit no-issues row, a release decision, and a next recommended action. The plan is also accepted only if no source code, Remotion source, schemas, command behavior, render scripts, generated media, or binary artifacts are commit candidates.

The expected release decision before human playback is `needs-polish`. After human playback, `release-ready-with-known-warnings` is acceptable only if playback confirms video and audio quality and any remaining issues are minor and explicitly accepted. `blocked` is required if the video cannot play or audio is unusable.

No test suite is required for Milestone 1 if only documentation changes are made. If later milestones regenerate `timeline.json` for timestamp mapping, that generated file remains ignored and should not be committed. If any code changes are proposed, stop; that belongs in a later explicitly approved polish phase, not in this review phase.

## Idempotence and Recovery

The documentation updates are safe to repeat. If the issue log is partially filled, leave existing rows intact and append or refine rows rather than deleting evidence. If a timestamp is wrong, correct it in place and note the correction in the plan's living sections if it affects release decision.

If `timeline.json` is missing, it can be regenerated from example inputs using `build-timeline`; this is safe and produces an ignored generated file. If the final MP4 is missing, stop and report that Phase 21 output is unavailable. Do not rerender unless the user explicitly approves a rerender task.

If human playback reveals a source bug, schema issue, or Remotion rendering issue, record it in the issue log and stop at documentation. Do not fix it in this phase. A later polish phase should use the issue inventory as input.

## Artifacts and Notes

The important existing artifact is `remotion/out/final.mp4`. It is generated output, ignored by git, and must not be committed. The important review artifact is `docs/final-render-quality-review.md`, which is text-only and should be committed when complete. This plan file, `docs/plans/human-playback-review-timing-inventory.md`, is also text-only and should be a commit candidate.

Do not commit:

- `remotion/out/final.mp4`
- `remotion/out/*`
- `remotion/public/*`
- `assets/visuals/*`
- `timeline.json`
- `.venv/`
- `remotion/node_modules/`
- caches
- `remotion/props.json` if it only changed because of local regeneration

## Interfaces and Dependencies

This phase uses existing documentation and existing CLI commands only. The review file is `docs/final-render-quality-review.md`. The plan file is `docs/plans/human-playback-review-timing-inventory.md`. Optional timeline mapping uses `.venv/bin/synccut inspect timeline.json` and, if needed, `.venv/bin/synccut build-timeline ... --out timeline.json`.

No new Python modules, Remotion components, npm scripts, schemas, package dependencies, external tools, media APIs, ffmpeg commands, ffprobe commands, media probes, transcoders, or render commands should be introduced in this phase.

## Change Note

2026-05-13 / Codex: Created this ExecPlan for Phase 22 human playback review and timing issue inventory. The plan records the review-only scope, issue categories, issue log format, timestamp-to-scene mapping method, release decision rules, milestones, validation expectations, artifact policy, and explicit exclusions.

2026-05-13 / Codex: Completed Milestone 1 by adding the human playback review instructions, issue categories, structured issue log, timestamp-to-scene helper, and release decision options to `docs/final-render-quality-review.md`. No source, schema, media, render, or command behavior changes were made.

2026-05-13 / Codex: Completed Milestone 2 by recording user-provided human playback findings in `docs/final-render-quality-review.md`. The release decision remains `needs-polish`, and the recommended next phase is timing and visual-duration polish.

2026-05-13 / Codex: Completed Milestone 3 by classifying the recorded playback issues and defining Phase 23 scope as conclusion gap smoothing plus short-video duration handling for AI_VIDEO/B_ROLL assets. No source, schema, media, render, or command behavior changes were made.

2026-05-13 / Codex: Completed Milestone 4 by reviewing artifacts and recording a docs-only commit recommendation. No source, schema, media, render, command behavior, commit, or tag changes were made.
