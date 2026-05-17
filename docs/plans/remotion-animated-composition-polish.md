# Phase 35: Remotion animated composition polish

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, validate, and review the Remotion-only animated composition polish from this file without reading earlier conversation.

## Purpose / Big Picture

Phase 35 improves the perceived production quality of SyncCut videos by adding Remotion-rendered animation, layered composition, subtle motion graphics, scene transitions, and typography polish. The goal is for rendered videos to feel less static even when the source visual asset is a still image, a simple looped video, a data card, or a placeholder.

This phase is Remotion-side visual and UI composition polish only. It must not change Python pipeline commands, timeline generation, audio or alignment generation, B-roll or AI video source assets, generated media, or provider behavior. It should add deterministic lightweight animation inside the existing Remotion composition using React, TypeScript, and Remotion frame APIs.

The preferred direction is an animated Remotion/CSS/React background and composition layer polish, not a new media background video file. The output should remain compatible with the current `remotion/props.json` shape and the existing `SyncCutVideo` composition.

## Progress

- [x] (2026-05-17T00:00:00+07:00) Created this Phase 35 ExecPlan after reading the requested project instructions, Remotion best-practice guidance, existing Phase 34 and visual readiness plans, final render review docs, Remotion package scripts, current Remotion source files, sample props, and current git status.
- [x] (2026-05-17T00:00:00+07:00) Milestone 1: Remotion visual audit complete. Confirmed current composition structure, static areas, absence of frame-driven motion, usable props fields, safe insertion points, render script classification, and Remotion-only constraints.
- [x] (2026-05-17T00:00:00+07:00) Milestone 2: Remotion animated composition polish design complete. Chose exact component boundaries, frame-driven background and scene transition behavior, label fallbacks, shared visual/data/placeholder polish strategy, dependency policy, and validation path.
- [x] (2026-05-17T00:00:00+07:00) Milestone 3: Implemented Remotion animated composition polish and passed `npm run typecheck`.
- [x] (2026-05-17T21:35:00+07:00) Milestone 4: Local validation complete. Remotion typecheck passed, smoke render succeeded after the expected Chrome sandbox permission retry, and `remotion/out/smoke.mp4` was left as an ignored playback-review artifact.
- [x] (2026-05-17T21:45:00+07:00) Milestone 5: Final review and cleanup complete. GUI playback could not be observed from this environment because no default MP4 application is registered, no tuning was made without visual evidence, final typecheck passed, and artifact status is clean aside from expected Remotion source/plan commit candidates and ignored smoke output.

## Surprises & Discoveries

- Observation: The current composition has a static top-level background.
  Evidence: `remotion/src/Video.tsx` renders an `AbsoluteFill` with `backgroundColor: "#101316"` and maps scene `Sequence`s directly to `SceneRenderer`.
- Observation: Scene timing and audio are already driven by exported props.
  Evidence: `Video.tsx` uses each scene's `start_frame` and `duration_frames`, while `SectionAudio.tsx` sequences section audio by section frame ranges.
- Observation: Prepared visual assets already support looped video and static images.
  Evidence: `VisualAssetScene.tsx` uses Remotion `Video` with `muted` and `loop` for prepared video assets, and `Img` for prepared image assets.
- Observation: AI_VIDEO and B_ROLL scenes already flow through a shared component.
  Evidence: `AiVideoScene.tsx` and `BRollScene.tsx` both render `VisualAssetScene` with different labels and accent colors.
- Observation: Data scenes already share a stable layout wrapper.
  Evidence: `ChartScene`, `ComparisonCardScene`, `TableScene`, `TimelineScene`, and `ShareBreakdownScene` use `DataSceneFrame` when valid structured visual data is available.
- Observation: Placeholder scenes contain useful existing text but are static.
  Evidence: `PlaceholderScene.tsx` renders prompt, dialogue, visual data, and audio metadata without motion.
- Observation: Props contain enough fields for small typography overlays without schema changes.
  Evidence: `remotion/props.json` scene entries include `id`, `section`, `section_key`, `scene_order`, `visual_type`, `duration_sec`, `duration_frames`, `visual.prompt`, and `dialogue.text`.
- Observation: Current Remotion scripts already provide typecheck, smoke render, segment render, and final render.
  Evidence: `remotion/package.json` defines `typecheck`, `render:smoke:local`, `render:segment:local`, and `render:final:local`.
- Observation: The requested `docs/plans/final-render-quality-review.md` path does not exist, but the repository has `docs/final-render-quality-review.md` and `docs/plans/final-release-render-quality-review.md`.
  Evidence: `rg --files docs | rg 'final.*render|render.*quality|quality.*review'` found those files.
- Observation: Remotion animation should be frame-driven, not CSS keyframe-driven.
  Evidence: Remotion best-practice guidance says to use `useCurrentFrame`, `interpolate`, `spring`, and deterministic frame math because CSS keyframes and transitions do not render reliably in Remotion output.
- Observation: The working tree is clean except ignored local/generated paths.
  Evidence: `git status --short --ignored` reported only ignored `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: Composition registration is straightforward and props-driven.
  Evidence: `remotion/src/index.ts` registers `RemotionRoot`; `Root.tsx` defines one `Composition` whose id, width, height, fps, and duration come from `defaultProps.composition`; `props.ts` imports `../props.json` and casts it to `SyncCutProps`.
- Observation: Top-level scene sequencing has no transition wrapper today.
  Evidence: `Video.tsx` maps each scene to a Remotion `Sequence` using `from={scene.start_frame}` and `durationInFrames={scene.duration_frames}`, then renders `SceneRenderer` directly.
- Observation: Section audio sequencing is already isolated from visuals.
  Evidence: `SectionAudio.tsx` maps sections with `audio.public_path` to `Sequence` components with `layout="none"` and Remotion `Audio` via `staticFile(publicPath)`.
- Observation: Scene dispatch is centralized and safe to wrap once.
  Evidence: `SceneRenderer.tsx` switches on `scene.visual_type` and returns AI video, B-roll, chart, comparison, table, share breakdown, timeline, or unknown placeholder components.
- Observation: Current static elements are broad rather than isolated.
  Evidence: `Video.tsx` has a flat background and static footer; `VisualAssetScene.tsx` has a static media frame, tint, header, and metadata strip; `DataSceneFrame.tsx` has static header/content/footer; `PlaceholderScene.tsx` has a static centered panel and diagnostic grid.
- Observation: Current visual media playback is compatible with the desired polish scope.
  Evidence: `VisualAssetScene.tsx` obtains a prepared asset from `scene.visual.public_path`, validates it with `getPreparedVisualAsset`, renders image assets with `Img`, renders video assets with muted looping `Video`, and falls back to `PlaceholderScene` when absent.
- Observation: Data card content is static but already uses shared structure.
  Evidence: chart, comparison, table, share breakdown, and timeline scene components parse `scene.visual.data` and render through `DataSceneFrame`; invalid data falls back to `PlaceholderScene`.
- Observation: No current Remotion source component uses frame-driven animation APIs.
  Evidence: `rg "useCurrentFrame|interpolate|spring|transition|animation|keyframes" remotion/src` returned no matches.
- Observation: No existing CSS keyframe/transition animation needs removal.
  Evidence: The same search returned no `transition`, `animation`, or `keyframes` matches in `remotion/src`; styling is static inline CSSProperties and SVG attributes.
- Observation: Section-level metadata is available for typography and fallback labels.
  Evidence: `SyncCutSection` includes `section_key`, `section`, `section_order`, frame/sec start/end, duration fields, audio, and alignment path.
- Observation: Scene fields are rich enough for small labels but should not become captions.
  Evidence: `SyncCutScene` includes `id`, `scene_order`, `section`, `section_key`, `visual_type`, duration and frame fields, `visual.prompt`, `dialogue.text`, and warnings. These support section labels and optional short source-derived text, but full dialogue captions are out of scope.
- Observation: The checked props are audio-prepared and not visually prepared.
  Evidence: The sampled `remotion/props.json` shows section audio `public_path` fields and scene visual prompt/data fields; early AI_VIDEO/B_ROLL scenes have prompts but no sampled `visual.public_path` in the first 260 lines.
- Observation: Safe insertion points are clear.
  Evidence: `AnimatedBackground` can sit in `Video.tsx` behind scene sequences; a scene wrapper can sit inside each scene `Sequence` around `SceneRenderer`; section labels can live in that wrapper; asset-frame polish can be contained in `VisualAssetScene`; shared data/placeholder polish can be contained in `DataSceneFrame` and `PlaceholderScene`.
- Observation: Render scripts have different approval levels.
  Evidence: `npm run typecheck` only runs `tsc --noEmit`; `render:smoke:local` renders frames `0-149` to `remotion/out/smoke.mp4`; `render:segment:local` renders frames `0-899` to `remotion/out/segment.mp4`; `render:final:local` renders the full composition to `remotion/out/final.mp4`.
- Observation: The design can avoid `SceneRenderer.tsx` changes.
  Evidence: `Video.tsx` can wrap each `SceneRenderer` call with a new `SceneShell` inside the existing `Sequence`, so visual type dispatch does not need to know about transitions.
- Observation: Short scenes require guarded interpolation input ranges.
  Evidence: The sample props include a `COMPARISON_CARD` scene of 115 frames and other scenes can be shorter in future inputs; the transition formula must avoid equal or descending frame stops when `durationFrames` is very small.
- Observation: The animated background must be low-contrast because it will sit behind all scenes.
  Evidence: Visual asset scenes and data frames already use dark overlays and dense foreground content, so background motion should remain subtle and should not compete with text or media.
- Observation: Existing dependencies are sufficient.
  Evidence: `remotion/package.json` already includes `react`, `react-dom`, `remotion`, TypeScript, and Remotion CLI packages. No animation library is needed for frame-driven transforms and opacity.
- Observation: The implementation stayed within the intended Remotion-only file set.
  Evidence: Added `remotion/src/components/AnimatedBackground.tsx`, `SceneShell.tsx`, and `SectionLabel.tsx`; updated `Video.tsx`, `VisualAssetScene.tsx`, `DataSceneFrame.tsx`, and `PlaceholderScene.tsx`; updated this plan.
- Observation: TypeScript accepted the new animation components.
  Evidence: `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`.
- Observation: The short-scene guard was implemented in both shell and shared frame polish.
  Evidence: `SceneShell`, `DataSceneFrame`, and `PlaceholderScene` all guard `scene.duration_frames` with `Math.max(1, ...)` and compute bounded transition frames before interpolation.
- Observation: No implementation deviation required new dependencies, schema changes, source media changes, or render script changes.
  Evidence: The code uses existing Remotion APIs and React inline styles only; no package files, props, Python source, media paths, or render scripts changed.
- Observation: The first smoke render attempt hit the known local Chrome sandbox launch limitation.
  Evidence: `npm run render:smoke:local` failed before rendering with `Closed with null signal: SIGTRAP` and Chromium `setsockopt: Operation not permitted (1)`.
- Observation: The permitted smoke render completed successfully.
  Evidence: Rerunning the same `npm run render:smoke:local` command with Chrome launch permission rendered and encoded `150/150` frames and reported `out/smoke.mp4 699.1 kB`.
- Observation: The smoke render output exists as an ignored artifact.
  Evidence: `ls -lh remotion/out/smoke.mp4` reported `683K`, and `git status --short --ignored` lists `!! remotion/out/`.
- Observation: No source media, props, Python, README, generated report, or render-final artifacts became commit candidates during validation.
  Evidence: Focused status listed only modified Remotion source files plus the new plan and new Remotion components.
- Observation: Local GUI playback could not be performed by the agent environment.
  Evidence: `xdg-open remotion/out/smoke.mp4` failed with `Failed to find default application for content type 'video/mp4'`.
- Observation: No final tuning was made in Milestone 5.
  Evidence: Without observable playback evidence, no source changes were made beyond the already implemented Milestone 3 Remotion polish and this plan update.
- Observation: Final Remotion validation remains green.
  Evidence: `cd remotion && npm run typecheck` passed with `tsc --noEmit` after Milestone 5 review.
- Observation: The smoke artifact remains available for user playback review and is ignored.
  Evidence: `ls -lh remotion/out/smoke.mp4` reported `683K`; `git status --short --ignored` lists `!! remotion/out/`.

## Decision Log

- Decision: Keep Phase 35 Remotion-only.
  Rationale: The user's scope explicitly excludes Python pipeline behavior, source media changes, provider calls, downloads, ffmpeg, and render automation changes.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not add a media background video.
  Rationale: The user preferred a Remotion-rendered animated background over introducing a new background video asset.
  Date/Author: 2026-05-17 / Codex
- Decision: Use frame-driven Remotion animation APIs only.
  Rationale: `useCurrentFrame`, `interpolate`, `spring`, and deterministic math are compatible with rendered output; CSS keyframes and transitions are not reliable for Remotion renders.
  Date/Author: 2026-05-17 / Codex
- Decision: Preserve existing asset rendering compatibility.
  Rationale: Prepared source videos/images should remain the core visual asset. The phase should polish the composition around them without changing source files or public-path semantics.
  Date/Author: 2026-05-17 / Codex
- Decision: Avoid full subtitles and complex infographic systems in this phase.
  Rationale: The user requested visual/UI composition polish and explicitly excluded full subtitles, word-level captions, and complex infographic systems.
  Date/Author: 2026-05-17 / Codex
- Decision: Keep `npm run typecheck` as the default validation command until a later validation milestone explicitly approves a smoke or segment render.
  Rationale: Typecheck is non-rendering and safe for the audit/design phases. Smoke and segment renders create ignored video outputs and should wait for validation scope; final render requires explicit approval.
  Date/Author: 2026-05-17 / Codex
- Decision: Add future polish at composition boundaries before changing individual data renderers.
  Rationale: `Video.tsx`, a scene wrapper, and shared scene frame components provide broad improvement with less risk than modifying every data visualization implementation first.
  Date/Author: 2026-05-17 / Codex
- Decision: Milestone 3 will create `AnimatedBackground`, `SceneShell`, and `SectionLabel`, then update `Video.tsx`, `VisualAssetScene.tsx`, `DataSceneFrame.tsx`, and `PlaceholderScene.tsx`.
  Rationale: These files cover the global background, all scene transitions, AI_VIDEO/B_ROLL presentation, structured data cards, and fallbacks without touching Python or props generation.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not update `SceneRenderer.tsx` unless implementation reveals a type or composition issue.
  Rationale: Wrapping `SceneRenderer` in `Video.tsx` keeps visual dispatch unchanged and reduces behavioral risk.
  Date/Author: 2026-05-17 / Codex
- Decision: `AnimatedBackground` will use only `useCurrentFrame`, `useVideoConfig`, `interpolate`, deterministic math, and inline styles.
  Rationale: This satisfies Remotion render requirements while avoiding media files, randomness, CSS keyframes, CSS transitions, and new dependencies.
  Date/Author: 2026-05-17 / Codex
- Decision: `SceneShell` will own scene-local fade, scale, slight translate, and the `SectionLabel` overlay.
  Rationale: A single wrapper can make all scenes feel animated without duplicating transition code in each visual type.
  Date/Author: 2026-05-17 / Codex
- Decision: `SectionLabel` will show section and visual metadata only, not captions.
  Rationale: Small section labels improve orientation, while full dialogue captions and word-level subtitles are explicitly out of scope.
  Date/Author: 2026-05-17 / Codex
- Decision: `VisualAssetScene` polish will preserve existing `Img`/`Video` paths and loop semantics.
  Rationale: The phase should polish the frame around source media, not change source media handling, media duration policy, or public path semantics.
  Date/Author: 2026-05-17 / Codex
- Decision: Data and placeholder polish will prioritize readability over motion density.
  Rationale: Existing data-card scenes can contain dense text, tables, chart labels, or diagnostic information, so motion must be subtle and should not hide content.
  Date/Author: 2026-05-17 / Codex
- Decision: Use existing dependencies only.
  Rationale: Remotion frame APIs are enough; adding Framer Motion or another animation library would increase scope and risk without clear benefit.
  Date/Author: 2026-05-17 / Codex
- Decision: Milestone 4 validation will require typecheck and treat smoke render as optional/user-approved; final render remains explicitly disallowed without approval.
  Rationale: Typecheck is sufficient for default non-rendering validation, while render commands create ignored video artifacts and can be sandbox-sensitive.
  Date/Author: 2026-05-17 / Codex
- Decision: Use `SceneShell` in `Video.tsx` rather than changing `SceneRenderer`.
  Rationale: This preserves the existing visual type switch and applies transition/label behavior uniformly to every scene.
  Date/Author: 2026-05-17 / Codex
- Decision: Keep the existing top-level metadata footer for now.
  Rationale: It remains useful diagnostic context and did not conflict with the new scene label during typecheck-level implementation; playback review can decide whether to tune or remove it.
  Date/Author: 2026-05-17 / Codex
- Decision: Place `SectionLabel` in the upper-right rather than upper-left.
  Rationale: Existing visual asset scenes already use upper-left title/header space; upper-right is less likely to cover the primary scene title while remaining visible.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not add a README note in Phase 35.
  Rationale: This phase changes rendered Remotion composition polish only and does not alter user-facing CLI workflow, provider behavior, or runbook commands.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not tune visual parameters without actual playback evidence.
  Rationale: The smoke render exists, but this environment could not open/play it for visual review. Tuning opacity, scale, labels, or glow without observation would be speculative.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not run final render in Phase 35 Milestone 5.
  Rationale: The user explicitly allowed only smoke render unless full final render is separately approved.
  Date/Author: 2026-05-17 / Codex

## Outcomes & Retrospective

This plan has been created without implementing any Remotion source changes, Python changes, README changes, media changes, downloads, ffmpeg usage, provider calls, render runs, commits, tags, or pushes.

The intended outcome is a small, safe Remotion polish package: an animated background, animated scene wrapper, subtle visual-frame motion, scene transitions, and a small section label overlay. Success means the composition has visible frame-driven motion even when source visuals are static, while existing B-roll/AI video and data-card rendering remains compatible.

Known constraint: this phase should not solve asset quality, asset duration, B-roll downloading, audio generation, or final render release review. It should make the presentation layer feel more polished and professional.

Milestone 1 audit summary: the Remotion app has one props-driven `SyncCutVideo` composition registered from `Root.tsx`; `Video.tsx` sequences audio and scenes; `SectionAudio.tsx` handles section audio independently; `SceneRenderer.tsx` centralizes visual type dispatch; AI_VIDEO and B_ROLL share `VisualAssetScene`; structured visual types share `DataSceneFrame`; missing/invalid content uses `PlaceholderScene`. The current visual presentation is static: flat top-level background, no scene transition wrapper, static media frame and metadata strips, static data cards, static placeholder cards, and a static footer. No current source uses `useCurrentFrame`, `interpolate`, `spring`, CSS transitions, CSS animations, or keyframes.

Milestone 1 identified the primary safe insertion points for Milestone 2 design: `AnimatedBackground` in `Video.tsx`, `SceneShell` or `SceneTransition` inside each scene `Sequence`, `SectionLabel` in the scene wrapper, media-frame polish in `VisualAssetScene`, and shared entrance/layer polish in `DataSceneFrame` and `PlaceholderScene`. Existing props provide scene and section labels, visual type, frame/duration data, prompts, dialogue text, and section metadata; implementation should defensively fall back to scene ids, visual type labels, or no optional text if any field is absent.

Milestone 1 did not edit Remotion source, Python source, tests, README, `.gitignore`, props, media, generated artifacts, or render outputs. The next step is Milestone 2: finalize the minimal animation package, component boundaries, frame formulas, fallback behavior, and validation plan.

Milestone 2 design summary: Milestone 3 should implement a minimal Remotion-only polish package by adding `AnimatedBackground`, `SceneShell`, and `SectionLabel`, and by updating `Video.tsx`, `VisualAssetScene.tsx`, `DataSceneFrame.tsx`, and `PlaceholderScene.tsx`. The design keeps `SceneRenderer.tsx`, props schema, Python source, source media, render scripts, and provider code unchanged. Motion is frame-driven, deterministic, low-contrast, and implemented with existing React/Remotion/TypeScript dependencies only.

The implementation target for Milestone 3 is to make every scene pass through `SceneShell`, place an animated background behind scene sequences, keep section audio untouched, preserve existing media rendering, add subtle frame/card motion around visual assets, and add shared entrance/layer polish to data and placeholder scenes. The next step is Milestone 3 implementation.

Milestone 3 implementation summary: the Remotion source now includes a frame-driven `AnimatedBackground`, a scene-local `SceneShell`, and a compact upper-right `SectionLabel`. `Video.tsx` renders the animated background behind existing scene sequences and wraps each `SceneRenderer` output in `SceneShell`, without changing sequence start/duration or section audio. `VisualAssetScene` keeps the existing `Img`/looping `Video` behavior and adds subtle deterministic media-layer scale/drift plus a soft frame glow. `DataSceneFrame` and `PlaceholderScene` add modest entrance motion and layered depth while preserving data and diagnostic readability.

Milestone 3 validation: `cd remotion && npm run typecheck` passed after the final SectionLabel placement adjustment. No render was run. No Python source, Python tests, README, `.gitignore`, props, source media, generated media, provider code, package dependencies, or render scripts were changed. The next step is Milestone 4 local validation, including typecheck and optional smoke render only if approved.

Milestone 4 local validation summary: `cd remotion && npm run typecheck` passed. The first `npm run render:smoke:local` attempt failed at Chrome launch with the expected sandbox error: `Closed with null signal: SIGTRAP` and `setsockopt: Operation not permitted (1)`. The same smoke render command was rerun with Chrome launch permission and completed successfully, rendering and encoding `150/150` frames to `remotion/out/smoke.mp4`; Remotion reported `699.1 kB`, and `ls -lh` reported `683K`.

Artifact review after Milestone 4: `remotion/out/smoke.mp4` is under ignored `remotion/out/` and was intentionally left for Milestone 5 playback review. `git status --short --ignored` shows `remotion/out/`, `remotion/public/`, `assets/`, `.venv/`, caches, and `timeline.json` as ignored local artifacts. The focused status shows only Remotion source files and this plan as commit candidates. Source media under `assets/visuals`, `remotion/props.json`, Python source, Python tests, README, `.gitignore`, generated reports, and final render output are not commit candidates. Python tests were not required because no Python files changed.

Next step: Milestone 5 playback review and final polish cleanup. Review `remotion/out/smoke.mp4`, tune only if needed, rerun Remotion typecheck, confirm final artifact status, and do not run a full final render without explicit approval.

Milestone 5 final review summary: `remotion/out/smoke.mp4` exists and remains available for user playback review, but the agent could not open/play it because the environment has no default MP4 application registered. Therefore, no visual claims are made about animation strength, scene transition quality, section label readability, foreground distraction, or data/placeholder readability beyond the successful smoke render and typecheck evidence. No final tuning was made because playback was not observable.

Final validation passed. `cd remotion && npm run typecheck` completed successfully. Python tests were not required because no Python files changed. No smoke rerender was needed because no tuning was made. No final render was run.

Final artifact/status summary: expected commit candidates are the Remotion source files and this plan. `README.md`, Python source, Python tests, `.gitignore`, `remotion/props.json`, `assets/visuals`, generated reports, provider artifacts, downloaded/generated media, and final render output are not commit candidates. `remotion/out/smoke.mp4` remains an ignored local artifact for playback review.

Phase 35 acceptance criteria status: the Remotion source has a small frame-driven animated polish package, no new media files, no source asset changes, no Python pipeline changes, no provider/API/download behavior, no ffmpeg/media transform, and Remotion typecheck passes. The residual issue is that human/GUI playback review of `remotion/out/smoke.mp4` remains needed to judge whether the animation feels too strong, too weak, or distracts from foreground content.

Recommended commit message: `Polish Remotion composition animation`.

Next step: ask the user before running a full final render or starting the next phase.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. The Remotion project lives under `remotion/` and consumes `remotion/props.json` through `remotion/src/props.ts`. `remotion/src/index.ts` registers `RemotionRoot`; `remotion/src/Root.tsx` defines the `SyncCutVideo` composition; `remotion/src/Video.tsx` renders section audio and scene sequences.

Important existing files:

- `remotion/src/Video.tsx`: top-level composition layout, scene sequencing, static global background, footer.
- `remotion/src/components/SceneRenderer.tsx`: visual type switch.
- `remotion/src/components/VisualAssetScene.tsx`: prepared AI_VIDEO/B_ROLL image/video rendering and fallback to `PlaceholderScene`.
- `remotion/src/components/DataSceneFrame.tsx`: shared wrapper for structured data scenes.
- `remotion/src/components/PlaceholderScene.tsx`: fallback card for missing or unsupported visual data/assets.
- `remotion/src/components/*Scene.tsx`: data-specific renderers.
- `remotion/src/types.ts`: exported props and scene/section types.
- `remotion/package.json`: typecheck and render scripts.

Current useful props fields include `scene.id`, `scene.section`, `scene.section_key`, `scene.visual_type`, `scene.duration_frames`, `scene.duration_sec`, `scene.visual.prompt`, and `scene.dialogue.text`. The phase should use these fields defensively and render clean fallbacks when any optional field is absent.

The current visual behavior is functional but mostly static. Prepared videos loop inside their scene duration, images remain static for the scene duration, data cards display static information, and placeholders show static diagnostic content. The top-level background is a flat dark color.

## Plan of Work

Milestone 1 is the Remotion visual audit. Inspect the current Remotion source structure and record how compositions, scene sequences, audio, visual assets, data scenes, placeholders, props, and render scripts work. Identify static elements, current background behavior, safe transition insertion points, usable typography fields, and likely files to change. Do not edit source in this milestone.

Milestone 2 is the polish design. Choose the smallest safe package that materially improves motion and production feel. The recommended package is:

- `AnimatedBackground`: a deterministic full-frame animated background using Remotion frame values, layered gradients, subtle luminous planes, grid/noise/vignette styling, and no media files.
- `SceneTransition` or `SceneShell`: a wrapper that applies scene-local fade/scale/slide transitions based on `useCurrentFrame()` and `scene.duration_frames`.
- `SectionLabel`: a small overlay using `section_key`, `section`, and visual type.
- `VisualAssetScene` polish: subtle entrance and low-amplitude frame/container motion around the existing media asset.
- `DataSceneFrame` and `PlaceholderScene` polish: shared entrance motion and improved layering without changing data semantics.

Milestone 3 is implementation. Add or update Remotion/React/TypeScript files only. Do not change Python code, pipeline commands, schemas, props generation, source assets, media files, or providers. Keep animations deterministic and small enough that they support narration rather than distract from it. Preserve compatibility with the existing `remotion/props.json`.

Milestone 4 is local validation. Run Remotion typecheck. Optionally run the existing smoke render script if the user approves or if the milestone explicitly decides it is safe; do not run the final render without explicit approval. Record whether Python tests are unnecessary because no Python files changed, or run them if any Python file is touched due to an approved bug fix.

Milestone 5 is playback review and final polish cleanup. If a smoke or segment render exists, review the output for readability, transition quality, section label clarity, animation strength, and whether the video still feels static. Make small tuning changes if needed, rerun typecheck, confirm no source media or generated/provider artifacts changed, and recommend a commit message. Ask the user before any full final render or next phase.

## Concrete Steps

Milestone 1 audit commands:

    sed -n '1,260p' remotion/src/Video.tsx
    sed -n '1,260p' remotion/src/Root.tsx
    sed -n '1,260p' remotion/src/types.ts
    sed -n '1,260p' remotion/src/components/SceneRenderer.tsx
    sed -n '1,260p' remotion/src/components/VisualAssetScene.tsx
    sed -n '1,260p' remotion/src/components/DataSceneFrame.tsx
    sed -n '1,260p' remotion/src/components/PlaceholderScene.tsx
    rg --files remotion/src
    sed -n '1,220p' remotion/package.json
    sed -n '1,220p' remotion/props.json
    git status --short --ignored

Milestone 2 design output should update this plan with exact files, component boundaries, animation formulas, fallback behavior, and validation commands before implementation.

Milestone 3 implementation should likely create or update:

- `remotion/src/components/AnimatedBackground.tsx`
- `remotion/src/components/SceneShell.tsx`
- `remotion/src/components/SectionLabel.tsx`
- `remotion/src/Video.tsx`
- `remotion/src/components/VisualAssetScene.tsx`
- `remotion/src/components/DataSceneFrame.tsx`
- `remotion/src/components/PlaceholderScene.tsx`
- `docs/plans/remotion-animated-composition-polish.md`

Milestone 3 should not update `remotion/src/components/SceneRenderer.tsx` unless implementation reveals a clear issue. `Video.tsx` should keep the existing scene `Sequence` mapping and render:

    <AnimatedBackground />
    <SectionAudio sections={sections} />
    <Sequence ...>
      <SceneShell scene={scene}>
        <SceneRenderer scene={scene} sections={sections} />
      </SceneShell>
    </Sequence>

`AnimatedBackground` design:

- Full-screen dark background rendered as React/CSS layers, not a media file.
- Use `useCurrentFrame()` and `useVideoConfig()` to derive slow global motion across the full composition.
- Use `interpolate()` with clamped ranges for opacity and movement where helpful.
- Use deterministic math such as `Math.sin(frame / n)` for very slow x/y drift, scale, and opacity modulation.
- Layer a dark base, two or three large soft luminous gradient planes, a subtle grid or radial overlay if lightweight, and a vignette/edge gradient.
- Keep opacity low enough that foreground text remains readable and the background does not distract from narration.
- Do not use CSS keyframes, CSS transitions, randomness, external assets, background video, or browser-only APIs.

`SceneShell` transition design:

- Wrap every scene render inside the existing scene `Sequence`.
- Use local `useCurrentFrame()`; because the shell is inside a scene `Sequence`, frame `0` is the scene start.
- Read `scene.duration_frames` and guard it with `Math.max(1, scene.duration_frames)`.
- Compute:

    const durationFrames = Math.max(1, scene.duration_frames);
    const transitionFrames = Math.max(
      1,
      Math.min(12, Math.max(4, Math.floor(durationFrames / 4)))
    );
    const exitStart = Math.max(transitionFrames + 1, durationFrames - transitionFrames);

- Opacity:

    interpolate(
      frame,
      [0, transitionFrames, exitStart, durationFrames],
      [0, 1, 1, 0],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
    )

- Scale:

    interpolate(
      frame,
      [0, transitionFrames],
      [0.985, 1],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
    )

- Translate Y:

    interpolate(
      frame,
      [0, transitionFrames],
      [10, 0],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
    )

- For extremely short scenes where the computed stops still become cramped, preserve clamped opacity and scale and prefer a quick fade over complex movement.
- Add a low-opacity scene-local overlay only if it improves depth without obscuring scene content.

`SectionLabel` design:

- Render as a small overlay in a safe corner, preferably top-left with enough inset to avoid the visual asset header and data-card content.
- Content:
  - primary: `scene.section_key` and `scene.section`
  - secondary: `scene.visual_type`
  - optional small sequence marker: `scene.scene_order`
- Fallbacks:
  - if section text is unavailable, use `scene.section_key`
  - if `section_key` is unavailable, use `scene.visual_type`
  - if all optional fields are unavailable, use `scene.id`
- Animate with the same frame-driven fade/slide timing as the shell, but keep movement small.
- Do not render dialogue text, word-level captions, or full subtitles.
- Keep text compact and semi-transparent enough to orient without covering the main visual.

`VisualAssetScene` polish strategy:

- Keep existing `Img` and `Video` rendering as the core asset.
- Keep `Video` muted and looped; do not alter loop semantics.
- Do not inspect media metadata, crop, trim, transcode, or rewrite public paths.
- Add a frame/container layer with subtle border, shadow, and foreground depth.
- Add a gentle continuous wrapper motion using frame-driven scale/pan so prepared images do not feel frozen.
- Keep motion small, such as scale around `1.0` to `1.018` and horizontal/vertical drift of only a few pixels.
- Preserve or simplify existing header/metadata overlays so they remain readable over images and videos.
- Use the existing `accentColor`, `assetLabel`, scene id, visual type, section key, and asset public path.

`DataSceneFrame` polish strategy:

- Add entrance motion to the overall shell rather than each chart/table row in this phase.
- Add layered card/background styling and subtle accent glow while preserving existing layout dimensions.
- Keep text and numeric values stable and readable.
- Avoid animating chart paths, bars, table rows, or dense labels unless Milestone 3 finds a very small safe improvement.

`PlaceholderScene` polish strategy:

- Match the new scene shell feel with entrance motion and layered card styling.
- Preserve diagnostic usefulness: scene id, visual type, section label, frames, seconds, prompt, dialogue, visual data, and audio metadata should remain readable.
- Do not hide missing/unsupported status behind decorative polish.

Milestone 3 should not touch:

- `synccut/*`
- Python tests
- README unless later explicitly needed
- `assets/visuals/*`
- generated media
- provider/API code
- Remotion render scripts unless a clear typecheck/build bug is discovered and recorded

Frame-driven animation guidance:

- Use `useCurrentFrame()` inside components that animate.
- Use `interpolate()` with `extrapolateLeft: "clamp"` and `extrapolateRight: "clamp"` for entrance/exit motion.
- Use `spring()` only where its deterministic easing improves readability.
- For short scenes, compute transition frame windows with `Math.min(12, Math.max(4, Math.floor(scene.duration_frames / 4)))`.
- Avoid CSS keyframes and CSS transitions.
- Avoid animation that depends on wall-clock time, randomness, browser APIs, or media metadata.

Suggested scene transition formula:

    const frame = useCurrentFrame();
    const transitionFrames = Math.min(12, Math.max(4, Math.floor(durationFrames / 4)));
    const opacity = interpolate(
      frame,
      [0, transitionFrames, Math.max(transitionFrames + 1, durationFrames - transitionFrames), durationFrames],
      [0, 1, 1, 0],
      {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
    );

Milestone 4 validation:

    cd remotion
    npm run typecheck
    cd ..

Optional smoke render, only if approved or explicitly chosen during Milestone 4:

    cd remotion
    npm run render:smoke:local
    cd ..

Do not run:

    npm run render:final:local

unless the user explicitly approves a full final render.

## Validation and Acceptance

The plan is accepted when this file exists and captures the Remotion-only scope, design direction, validation path, and exclusions clearly.

Milestone 1 is accepted when the current Remotion structure, static elements, props fields, background behavior, existing asset compatibility, likely change points, and render scripts are recorded in this plan.

Milestone 2 is accepted when the plan records exact component boundaries, files to change, animation timing formulas, fallback behavior for missing fields, dependency decisions, and validation commands.

Milestone 3 is accepted when the Remotion source implements the chosen polish package, does not change Python behavior or source assets, remains compatible with existing props, and typecheck is ready to run.

Milestone 4 is accepted when `cd remotion && npm run typecheck` passes. If a smoke render is run, record command, result, output path, ignored artifact status, and any visual observations. If no Python files changed, Python tests are not required; if any Python file changes, run `.venv/bin/python -m pytest`.

Milestone 5 is accepted when final typecheck passes, any small visual tuning is complete, no source media or generated/provider/API artifacts are commit candidates, and the plan records review notes, final status, known residual issues, and a recommended commit message.

Overall acceptance criteria:

- A small safe Remotion-only animated polish package is implemented.
- Rendered composition has visible animation even when source visuals are static.
- Existing B-roll/AI video image/video rendering remains compatible.
- No B-roll or AI source assets are changed.
- No new media files are added.
- No Python pipeline behavior changes.
- No provider/API/download behavior is added or called.
- No ffmpeg or media transformation is used.
- Remotion typecheck passes.
- Smoke/segment render is optional and recorded if run.
- Final render is not run unless explicitly approved.

## Idempotence and Recovery

The Remotion source changes should be deterministic and safe to rerun. Typecheck should not create committed artifacts. Smoke or segment renders, if run, write under ignored Remotion output paths and must not be committed.

If typecheck fails, fix the TypeScript or React issue in the smallest relevant Remotion file and rerun typecheck. If an animation looks too strong during smoke review, reduce motion amplitude, opacity, scale, or transition duration rather than adding new systems. If props fields are missing, components should fall back to scene ids, visual type labels, or no optional text instead of throwing.

If a render script fails because Chrome launch is blocked by the environment, record the exact error and do not add workaround scripts. If a render fails because a source asset is invalid, stop and report it; do not edit, transcode, replace, or normalize source media in this phase.

To recover from accidental generated artifacts, remove only known generated outputs after confirming they are not user media. Do not broad-clean `assets/visuals`, `remotion/public`, or `remotion/out` without explicit approval.

## Artifacts and Notes

Expected tracked commit candidates after implementation:

- Remotion source files under `remotion/src/`
- `docs/plans/remotion-animated-composition-polish.md`

Possible tracked commit candidates only if justified later:

- `README.md`, if a concise note about animated Remotion polish is useful.

Not expected as commit candidates:

- `synccut/*`
- Python tests
- `assets/visuals/*`
- generated media
- downloaded media
- API keys or provider config files
- `remotion/props.json`
- `remotion/public/*`
- `remotion/out/*`
- `timeline.json`
- `.venv/*`
- `remotion/node_modules/*`
- caches

Recommended commit message after successful completion:

    Polish Remotion composition animation

## Interfaces and Dependencies

Use existing dependencies only unless Milestone 2 records a clear reason otherwise. Current Remotion dependencies already include `react`, `react-dom`, `remotion`, TypeScript, and the Remotion CLI.

Use these Remotion APIs for animation:

- `useCurrentFrame`
- `useVideoConfig`
- `interpolate`
- `spring`
- `Easing`
- `AbsoluteFill`
- `Sequence`
- existing `Img`, `Video`, and `staticFile` behavior

Do not add animation libraries, browser-only runtime dependencies, external media sources, or network calls. Do not add a background video file. Do not change the props schema. Components must accept the current `SyncCutScene`, `SyncCutSection`, and `SyncCutRemotionProps` shapes from `remotion/src/types.ts`.
