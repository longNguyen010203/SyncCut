# Add local visual asset references for AI_VIDEO and B_ROLL

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can now generate timed Remotion props, prepare audio files for Remotion, render data-driven visual components for structured scene types, and run a short local render smoke test when Chrome launch is permitted. The remaining placeholder-only scene types are `AI_VIDEO` and `B_ROLL`, which currently carry prompts but no local visual media references.

This phase should add a deterministic local-file strategy so those two scene types can reference files under `remotion/public/visuals/` when a developer has already supplied them. The visible result should be simple: if an `AI_VIDEO` or `B_ROLL` scene has a supported `visual.public_path`, the Remotion component renders that local image or video; if the field is missing, unsupported, or malformed, the component keeps showing the existing metadata placeholder. This phase must not generate AI video, call image or video generation APIs, download B-roll, scrape external media, call ffmpeg directly, assemble the full final MP4, add Python commands that invoke Remotion rendering, parse DOCX, or add GUI or web app behavior.

## Progress

- [x] (2026-05-11T00:00:00Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, `docs/plans/export-remotion-props.md`, `docs/plans/remotion-project-skeleton.md`, `docs/plans/remotion-audio-assets.md`, `docs/plans/remotion-basic-visual-components.md`, `docs/plans/remotion-preview-environment.md`, `docs/plans/remotion-render-smoke.md`, `remotion/README.md`, and `remotion/package.json`.
- [x] (2026-05-11T00:00:00Z) Inspected `remotion/src/types.ts`, `remotion/src/components/AiVideoScene.tsx`, `remotion/src/components/BRollScene.tsx`, `remotion/src/components/PlaceholderScene.tsx`, `remotion/src/components/SceneRenderer.tsx`, `remotion/props.json`, `synccut/remotion_exporter.py`, `synccut/remotion_assets.py`, and `.gitignore`.
- [x] (2026-05-11T00:00:00Z) Checked the installed Remotion runtime exports and confirmed `Img`, `Video`, `OffthreadVideo`, and `staticFile` are available from the installed `remotion` package.
- [x] (2026-05-11T00:00:00Z) Created this ExecPlan for the local visual asset strategy.
- [x] (2026-05-11T14:39:46Z) Implemented Milestone 1: added optional visual asset fields, safe public path classification, and shared Remotion asset rendering with placeholder fallback for `AI_VIDEO` and `B_ROLL`.
- [x] (2026-05-11T14:48:31Z) Validated Milestone 1 with a synthetic local image asset at `remotion/public/visuals/scene_001.png` and a temporary `scene_001` props patch.
- [x] (2026-05-11T14:56:00Z) Implemented Milestone 2: added strict local visual asset preparation helpers, the `prepare-visual-assets` CLI command, and focused helper/CLI tests.
- [x] (2026-05-11T15:06:36Z) Completed Milestone 3: validated the full local visual asset workflow with synthetic `scene_001` and `scene_003` assets, Remotion typecheck, local still/smoke renders, and the Python test suite.

## Surprises & Discoveries

- Observation: `AI_VIDEO` and `B_ROLL` currently have prompt text and `visual.data` set to null in generated props.
  Evidence: Inspecting `remotion/props.json` showed `scene_001` as `AI_VIDEO` with a prompt and `data: null`, and `scene_003` as `B_ROLL` with a prompt and `data: null`.
- Observation: The current exporter already reserves `assets.visuals`, but leaves it empty.
  Evidence: `synccut/remotion_exporter.py` returns `"assets": {"audio": _audio_assets(sections), "visuals": []}`, and the generated `remotion/props.json` has `assets.visuals: []`.
- Observation: The current Remotion wrappers for `AI_VIDEO` and `B_ROLL` are intentionally thin placeholders.
  Evidence: `remotion/src/components/AiVideoScene.tsx` and `remotion/src/components/BRollScene.tsx` only render `PlaceholderScene` with different labels and accent colors.
- Observation: The installed Remotion package can render static images and local video references without adding a new dependency.
  Evidence: A local Node check from `remotion/` reported `{"Img":true,"Video":true,"OffthreadVideo":true,"staticFile":true}` from `require("remotion")`.
- Observation: Generated media and prepared public assets are already ignored broadly.
  Evidence: `.gitignore` contains `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`.
- Observation: Milestone 1 did not require dependency or dispatch changes.
  Evidence: The implementation added `remotion/src/components/visualAsset.ts` and `remotion/src/components/VisualAssetScene.tsx`, updated `AiVideoScene.tsx`, `BRollScene.tsx`, and `types.ts`, and left `SceneRenderer.tsx`, `Video.tsx`, package scripts, package dependencies, and Python files unchanged.
- Observation: The first synthetic PNG file was recognized by the `file` command but failed to load in Chromium during Remotion still rendering.
  Evidence: The permitted `npm run still:local` run failed with `CancelledError Error: Error loading image with src: http://localhost:3000/public/visuals/scene_001.png`. Replacing it with a generated PNG written with explicit PNG chunks and CRCs produced a 9.7K `scene_001.png`, after which `npm run still:local` succeeded.
- Observation: The known sandbox browser-launch limitation still applies to local Chrome render commands.
  Evidence: `npm run still:local` first failed with `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[46:46:0511/214617.419307:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. `npm run render:smoke:local` first failed with the same `SIGTRAP` signature and `[48:48:0511/214732.447065:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. Both commands succeeded when Chrome launch was permitted.
- Observation: The synthetic `visual.public_path` support renders in both still and smoke validation when Chrome can launch.
  Evidence: After patching `scene_001.visual.public_path` to `visuals/scene_001.png`, `npm run still:local` rendered `out/preview.png`, and `npm run render:smoke:local` rendered frames `0-149`, encoded 150 frames, and wrote `out/smoke.mp4 272.5 kB`.
- Observation: The visual asset helper can be implemented without touching the existing audio asset helper or exporter.
  Evidence: Milestone 2 added `synccut/visual_assets.py` and imported only `prepare_visual_assets_file` in `synccut/cli.py`; `synccut/remotion_exporter.py` and `synccut/remotion_assets.py` were not edited.
- Observation: Regenerating `remotion/props.json` removed the temporary synthetic visual path patch while preserving prepared audio paths.
  Evidence: After running `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` and `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public`, inspecting `scene_001.visual` showed only `type`, `prompt`, and `data`, with no `public_path`, `asset_status`, or `asset_source`.
- Observation: Milestone 3 synthetic visual preparation reported one overwrite because a previous ignored validation artifact already existed.
  Evidence: `prepare-visual-assets` reported `visual_copied: 1`, `visual_reused: 0`, `visual_overwritten: 1`, `visual_missing: 15`, and `visual_assets: 2`. `scene_001.png` existed from Milestone 1 synthetic validation and was overwritten; `scene_003.png` was newly copied.
- Observation: The full workflow prepared both an `AI_VIDEO` scene and a `B_ROLL` scene without changing prompt or data fields.
  Evidence: The inspection snippet reported `scene_001 AI_VIDEO` and `scene_003 B_ROLL`, each with `public_path` under `visuals/`, `asset_status: prepared`, `asset_source: local`, `prompt_present: True`, and `data: None`.
- Observation: The final git status clearly separates commit candidates from generated artifacts.
  Evidence: `git status --short --ignored` showed source and plan changes, `M remotion/props.json`, and untracked `assets/`; ignored artifacts included `.pytest_cache/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: The suggested synthetic source directory was not ignored before final review.
  Evidence: After Milestone 3, `git status --short --ignored` showed `?? assets/`, meaning `assets/visuals/scene_001.png` and `assets/visuals/scene_003.png` were not excluded from commit by `.gitignore`. A narrow `assets/visuals/` ignore rule was added during final review.

## Decision Log

- Decision: Start with Remotion-side optional `visual.public_path` support instead of changing `export-remotion`.
  Rationale: `export-remotion` is a stable data export command and should not guess whether external AI video or B-roll assets exist. Optional TypeScript support lets hand-authored or future prepared props render local assets while keeping existing props valid.
  Date/Author: 2026-05-11 / Codex
- Decision: Keep local media under `remotion/public/visuals/` and reference it with paths like `visuals/scene_001.mp4`.
  Rationale: Remotion serves static files from the project `public/` directory through `staticFile()`. A dedicated `visuals/` subdirectory mirrors the existing `public/audio/` convention and keeps generated visual media out of source directories.
  Date/Author: 2026-05-11 / Codex
- Decision: Use `visual.public_path`, `visual.asset_status`, and `visual.asset_source` as the scene-level props extension.
  Rationale: The scene renderer needs a direct public path on the scene visual object. Status and source fields make the asset state inspectable without requiring a separate manifest for the initial Remotion fallback support.
  Date/Author: 2026-05-11 / Codex
- Decision: If a Python command is added later, make it separate from `prepare-remotion-assets`.
  Rationale: `prepare-remotion-assets` currently prepares section audio. A separate `prepare-visual-assets` command keeps file-copying side effects explicit, avoids changing existing audio workflow behavior, and lets missing visual assets remain non-fatal.
  Date/Author: 2026-05-11 / Codex
- Decision: Treat missing visual assets as a fallback condition, not an error, for the visual asset command.
  Rationale: `AI_VIDEO` and `B_ROLL` are intentionally optional at this stage. A developer should be able to preview the timeline with placeholders even before local visual media has been supplied.
  Date/Author: 2026-05-11 / Codex
- Decision: Add a shared `VisualAssetScene.tsx` for both `AI_VIDEO` and `B_ROLL`.
  Rationale: The two visual types need identical local asset rendering and fallback rules, with only labels and accent colors differing. A shared component keeps validation and Remotion media handling in one place while preserving existing wrapper semantics.
  Date/Author: 2026-05-11 / Codex
- Decision: Use `OffthreadVideo` from the installed `remotion` package for local video public paths.
  Rationale: Local inspection already confirmed the installed package exports `OffthreadVideo`, and `npm run typecheck` passed with this import. No `@remotion/media` dependency or package change is needed for this milestone.
  Date/Author: 2026-05-11 / Codex
- Decision: Keep the synthetic validation asset and props patch as local validation artifacts only.
  Rationale: `remotion/public/visuals/scene_001.png` is generated test media, and the `remotion/props.json` change is a temporary sample patch proving optional public path rendering. Neither should be committed unless the user explicitly approves committing sample visual asset references later.
  Date/Author: 2026-05-11 / Codex
- Decision: Implement `assets.visuals` as a deterministic audit list of prepared visual assets.
  Rationale: The root props object already reserves `assets.visuals`. Replacing it with scene-order prepared entries gives tests and future inspection a stable summary while keeping rendering driven by `scene.visual.public_path`.
  Date/Author: 2026-05-11 / Codex
- Decision: Store missing visual asset state on target scenes as `asset_status: "missing"` and `asset_source: "local"`.
  Rationale: Missing local assets are expected at this phase and should not fail previews. Recording missing status makes the file preparation outcome explicit while leaving `visual.public_path` absent so Remotion falls back to placeholders.
  Date/Author: 2026-05-11 / Codex
- Decision: Normalize destination visual asset suffixes to lowercase.
  Rationale: Extension matching is case-insensitive, but lowercase public paths such as `visuals/scene_002.mp4` are deterministic and match the Remotion helper's extension handling.
  Date/Author: 2026-05-11 / Codex
- Decision: Ignore `assets/visuals/` as generated local synthetic/source media.
  Rationale: The validation workflow creates local source media under `assets/visuals/`, and the phase explicitly says generated synthetic assets should not be committed. Ignoring this narrow directory prevents accidental commits without hiding project source files or Remotion sample props.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

This plan has been created after reading the required project documents and inspecting the current Remotion components, generated props, Python Remotion exporter, audio asset helper, and artifact ignore rules. No source code, package file, Python CLI behavior, Remotion rendering source, generated media, or `.gitignore` entry has been changed for this phase yet.

The current recommended direction is to implement this phase in small steps. First add Remotion-only support for optional visual public paths with safe placeholder fallback. Then, only if the user approves the next milestone, add a strictly local Python command that copies user-provided media files by scene id into `remotion/public/visuals/` and annotates props. Final validation should use synthetic local assets and the existing typecheck and local smoke-render workflows.

Milestone 1 is complete. `remotion/src/types.ts` now allows `SyncCutVisual.public_path`, `SyncCutVisual.asset_status`, and `SyncCutVisual.asset_source` while keeping current generated props valid when those fields are absent. `remotion/src/components/visualAsset.ts` classifies untrusted public path values and returns image or video assets only for non-empty strings under `visuals/`, with no `..` segment and a supported case-insensitive extension. It does not check filesystem existence. `remotion/src/components/VisualAssetScene.tsx` renders valid image public paths with `<Img src={staticFile(publicPath)} />`, valid video public paths with muted `<OffthreadVideo src={staticFile(publicPath)} />`, and otherwise falls back to `PlaceholderScene`. `AiVideoScene.tsx` and `BRollScene.tsx` now preserve the existing placeholder labels and accent semantics while using the shared renderer for optional local assets.

Milestone 1 validation passed. From `remotion/`, `npm run typecheck` completed successfully. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and all 114 passed. No Python source files, `SceneRenderer.tsx`, `Video.tsx`, package scripts, dependencies, `.gitignore`, visual asset copy command, AI video generation, B-roll download, external fetch or scrape, ffmpeg, media probing or transcoding, final full MP4 render, Python Remotion wrapper, GUI, or web app behavior was added.

Milestone 1 synthetic asset validation is complete. `remotion/public/visuals/` was created locally, and a generated local PNG was written to `remotion/public/visuals/scene_001.png`. `remotion/props.json` was temporarily patched only for validation so `scene_001.visual` now includes `public_path: "visuals/scene_001.png"`, `asset_status: "prepared"`, and `asset_source: "local"`. This props patch is a generated/sample test change and should not be committed unless later explicitly approved.

The validation commands passed. From `remotion/`, `npm run typecheck` passed with the patched props. `npm run still:local` first hit the known sandbox browser-launch failure, then succeeded with Chrome launch permission and wrote `remotion/out/preview.png`, which was 633K at inspection time. `npm run render:smoke:local` first hit the same sandbox browser-launch failure, then succeeded with Chrome launch permission, rendered frames `0-149`, encoded 150 frames, and wrote `remotion/out/smoke.mp4`, which was 267K at inspection time. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and all 114 passed.

Generated artifacts from this validation are `remotion/public/visuals/scene_001.png`, `remotion/out/preview.png`, and `remotion/out/smoke.mp4`. `git status --short` showed the intentional source and plan changes plus `M remotion/props.json`; it did not show `remotion/public/visuals/scene_001.png` or `remotion/out/*` because `remotion/public` and `remotion/out/` are ignored. Do not commit the synthetic PNG, render outputs, or the temporary `remotion/props.json` patch unless the user explicitly approves them.

Milestone 2 is complete. `synccut/visual_assets.py` now provides `PreparedVisualAsset`, `VisualAssetPrepareResult`, `load_visual_props`, `prepare_visual_assets`, and `prepare_visual_assets_file`. The helper reads Remotion props, targets only `AI_VIDEO` and `B_ROLL` scenes, matches local files by exact scene id under `assets_dir`, supports `.png`, `.jpg`, `.jpeg`, `.webp`, `.mp4`, `.webm`, and `.mov` with case-insensitive extension matching, copies matched assets into `<out_dir>/visuals/`, writes `visual.public_path`, `visual.asset_status`, and `visual.asset_source` on target scenes, records missing local assets as missing without failing, and writes deterministic `assets.visuals` entries for prepared assets. It uses only the local filesystem and standard-library modules, does not inspect or decode media, and does not touch Remotion rendering or existing exporter/audio behavior.

The CLI command `synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` is now wired in `synccut/cli.py`. The CLI remains thin: it delegates to `prepare_visual_assets_file`, catches `SyncCutError`, prints `Error: ...` without tracebacks for expected failures, and prints a stable summary with copied, reused, overwritten, missing, prepared asset count, and public directory fields.

Milestone 2 tests passed. `tests/test_visual_assets.py` covers image and video copying, missing assets, duplicate supported candidate failures, unsupported files, idempotent reuse, overwrite behavior, preservation of `visual.prompt` and `visual.data`, unchanged non-target scenes, deterministic `assets.visuals`, and two-space JSON writing with a trailing newline. `tests/test_cli.py` covers CLI success, stable summary output, malformed props failure, duplicate visual asset failure, and no traceback for expected errors. From the repository root, `.venv/bin/python -m pytest` collected 128 tests and all 128 passed. From `remotion/`, `npm run typecheck` passed.

Cleanup for the previous synthetic validation is complete for tracked props. `remotion/props.json` was regenerated with `export-remotion` and then prepared with `prepare-remotion-assets`; `scene_001.visual` no longer contains the temporary synthetic `public_path`, `asset_status`, or `asset_source` fields. The ignored files `remotion/public/visuals/scene_001.png`, `remotion/out/preview.png`, and `remotion/out/smoke.mp4` remain local generated artifacts and should not be committed. `git status --short` does not show those ignored artifacts or a modified `remotion/props.json`.

Milestone 3 is complete, and the full local visual asset workflow has been validated with synthetic local media. Fresh data was regenerated from the repository root. `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Two synthetic source assets were generated locally without network access: `assets/visuals/scene_001.png` at 38K and `assets/visuals/scene_003.png` at 23K. They were generated PNG files, not downloaded media. Running `.venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` reported `Prepared Remotion visual assets for remotion/props.json`, `visual_copied: 1`, `visual_reused: 0`, `visual_overwritten: 1`, `visual_missing: 15`, `visual_assets: 2`, and `public_dir: remotion/public`. The overwrite was expected because `remotion/public/visuals/scene_001.png` already existed from earlier synthetic validation.

Prepared output files were present at `remotion/public/visuals/scene_001.png` and `remotion/public/visuals/scene_003.png`. The props inspection reported:

    scene_001 AI_VIDEO
      public_path: visuals/scene_001.png
      asset_status: prepared
      asset_source: local
      prompt_present: True
      data: None
    scene_003 B_ROLL
      public_path: visuals/scene_003.png
      asset_status: prepared
      asset_source: local
      prompt_present: True
      data: None

`assets.visuals` contains deterministic entries for `scene_001` and `scene_003`, in scene order. Each entry includes `scene_id`, `visual_type`, an absolute local source `path`, `public_path`, `asset_status: prepared`, and `asset_source: local`.

Final validation passed. From `remotion/`, `npm run typecheck` completed successfully. `npm run still:local` first failed with the known sandbox browser-launch error `Error: Failed to launch the browser process!`, `Error: Closed with null signal: SIGTRAP`, and `[46:46:0511/220309.634058:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. Rerunning with Chrome launch permission succeeded and wrote `remotion/out/preview.png`, which was 1.1M at inspection time. `npm run render:smoke:local` first failed with the same sandbox browser-launch signature and `[48:48:0511/220556.815426:ERROR:socket.cc(45)] setsockopt: Operation not permitted (1)`. Rerunning with Chrome launch permission succeeded, rendered frames `0-149`, encoded 150 frames, and wrote `remotion/out/smoke.mp4`, which was 261K at inspection time. From the repository root, `.venv/bin/python -m pytest` collected 128 tests and all 128 passed.

Final generated artifact and commit policy: do not commit `assets/visuals/scene_001.png`, `assets/visuals/scene_003.png`, `remotion/public/visuals/*`, `remotion/out/*`, `timeline.json`, `.pytest_cache/`, or `__pycache__/`. During final review, `.gitignore` was updated to ignore `assets/visuals/` because that generated source media directory was otherwise visible as untracked `assets/`. Do not commit `remotion/props.json` when it contains temporary synthetic local visual public paths and absolute local source paths in `assets.visuals`; after final review cleanup, `remotion/props.json` was regenerated and audio-prepared so those temporary visual fields are absent. Commit candidates for the phase are the plan file, `.gitignore`, Remotion type/component changes from Milestone 1, `synccut/visual_assets.py`, the `prepare-visual-assets` CLI wiring in `synccut/cli.py`, and the new/updated tests. No external media acquisition, AI video generation, B-roll download, scraping or fetching, ffmpeg, media probing or transcoding, Remotion rendering from Python, final full MP4 render, GUI, or web app behavior was added.

Phase 9 outcome: SyncCut now has a complete local visual asset strategy for `AI_VIDEO` and `B_ROLL`. Remotion can render optional local public image/video paths with placeholder fallback, the Python CLI can prepare strictly local scene-id-matched visual assets into `remotion/public/visuals/`, and the full workflow has been validated with synthetic local assets. The strategy remains deterministic, local-file based, and compatible with missing assets.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The existing Python workflow is:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

The existing Remotion validation and smoke workflow is:

    cd remotion
    npm run typecheck
    npm run still:local
    npm run render:smoke:local

The local render commands use `/usr/bin/google-chrome` and may require browser launch permission in sandboxed environments. The default `npm run still` can fail in this environment because Remotion tries to download Chrome Headless Shell from `remotion.media`, and Studio can fail because Node cannot read network interfaces.

The Remotion app consumes `remotion/props.json` through `remotion/src/props.ts`. `remotion/src/Root.tsx` registers one composition from `defaultProps.composition`. `remotion/src/Video.tsx` renders section audio and maps each scene to a Remotion `Sequence` using exported frame timing. `remotion/src/components/SceneRenderer.tsx` dispatches each visual type to a component. `COMPARISON_CARD`, `TABLE`, `CHART`, `TIMELINE`, and `SHARE_BREAKDOWN` now render basic data-driven visuals from `visual.data`. `AI_VIDEO` and `B_ROLL` still render `PlaceholderScene`.

A Remotion public path is a string relative to `remotion/public/`. For example, a file at `remotion/public/visuals/scene_001.mp4` is referenced from React with `staticFile("visuals/scene_001.mp4")`. Do not pass an original source path such as `assets/visuals/scene_001.mp4` or `examples/...` to `staticFile()`.

## Current AI_VIDEO and B_ROLL Props Shape

The current `remotion/props.json` has `AI_VIDEO` and `B_ROLL` scenes shaped like this:

    {
      "id": "scene_001",
      "visual_type": "AI_VIDEO",
      "visual": {
        "type": "AI_VIDEO",
        "prompt": "Extreme close-up of a silicon wafer rotating slowly under blue cleanroom light...",
        "data": null
      }
    }

    {
      "id": "scene_003",
      "visual_type": "B_ROLL",
      "visual": {
        "type": "B_ROLL",
        "prompt": "Aerial shot of TSMC's Hsinchu Science Park campus at dusk...",
        "data": null
      }
    }

The current root `assets.visuals` array exists but is empty:

    {
      "assets": {
        "audio": [
          {"section_key": "01_HOOK", "path": "examples/audio/01_HOOK.mp3", "public_path": "audio/01_HOOK.mp3"}
        ],
        "visuals": []
      }
    }

This phase should preserve the existing prompt and data fields. A local asset extension should be additive and optional so current props continue to type-check and render placeholders.

## Proposed Public Directory and Path Convention

Use this Remotion public asset directory:

    remotion/public/visuals/

Use scene-id-based destination filenames:

    remotion/public/visuals/<scene_id>.mp4
    remotion/public/visuals/<scene_id>.webm
    remotion/public/visuals/<scene_id>.mov
    remotion/public/visuals/<scene_id>.png
    remotion/public/visuals/<scene_id>.jpg
    remotion/public/visuals/<scene_id>.jpeg
    remotion/public/visuals/<scene_id>.webp

The corresponding public paths are:

    visuals/<scene_id>.mp4
    visuals/<scene_id>.png
    visuals/<scene_id>.jpg

Only use the public path inside Remotion components. `remotion/public/visuals/` is generated media and should not be committed. The current `.gitignore` already ignores `remotion/public`, which covers both `remotion/public/audio/` and `remotion/public/visuals/`.

## Proposed Props Extension

Extend `SyncCutVisual` in `remotion/src/types.ts` later as:

    export type VisualAssetStatus = "prepared" | "missing" | "unsupported";
    export type VisualAssetSource = "local";

    export interface SyncCutVisual {
      type: VisualType;
      prompt: string | null;
      data: JsonValue;
      public_path?: string;
      asset_status?: VisualAssetStatus;
      asset_source?: VisualAssetSource;
    }

For scenes with a prepared local asset, props should look like:

    {
      "visual": {
        "type": "B_ROLL",
        "prompt": "Aerial shot of TSMC's Hsinchu Science Park campus at dusk...",
        "data": null,
        "public_path": "visuals/scene_003.mp4",
        "asset_status": "prepared",
        "asset_source": "local"
      }
    }

For missing assets, omit `public_path` and optionally set:

    {
      "asset_status": "missing",
      "asset_source": "local"
    }

The initial Remotion-only milestone does not require `asset_status` or `asset_source` to exist. It only needs to understand `public_path` when present. If the Python visual asset command is added later, it should populate `asset_status` and `asset_source` deterministically.

If a visual asset command also updates `assets.visuals`, use entries like:

    {
      "scene_id": "scene_003",
      "visual_type": "B_ROLL",
      "path": "assets/visuals/scene_003.mp4",
      "public_path": "visuals/scene_003.mp4",
      "asset_status": "prepared",
      "asset_source": "local"
    }

The scene-level `visual.public_path` is still the field Remotion components should consume. `assets.visuals` is an audit list for inspection and tests, not the rendering lookup path.

## Whether to Change Existing Commands

Do not change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, or the render smoke behavior for Milestone 1. The first implementation step should be Remotion-only: types, a helper to classify public asset paths, and `AI_VIDEO` / `B_ROLL` components that render local assets when `visual.public_path` exists.

Do not change `export-remotion` to generate placeholder visual paths. The exporter should continue preserving the planning data and should not assume local assets exist.

Do not change `prepare-remotion-assets` to handle visuals. Its name and current implementation are focused on audio. If local visual copying is approved, add a separate command:

    synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

This command name is intentionally different from `prepare-remotion-assets` so users can choose whether they want only audio preparation or optional local visual asset preparation.

## Asset Matching Rules for the Optional Command

The optional command should be strictly local-file based. It must not download, generate, scrape, transcode, probe, or decode media.

Inputs:

    props_path: remotion/props.json
    assets_dir: assets/visuals
    out_dir: remotion/public

Only consider scenes where `scene.visual_type` is `AI_VIDEO` or `B_ROLL`. Match candidate files by exact scene id:

    <assets_dir>/<scene_id>.mp4
    <assets_dir>/<scene_id>.webm
    <assets_dir>/<scene_id>.mov
    <assets_dir>/<scene_id>.png
    <assets_dir>/<scene_id>.jpg
    <assets_dir>/<scene_id>.jpeg
    <assets_dir>/<scene_id>.webp

Supported image extensions are `.png`, `.jpg`, `.jpeg`, and `.webp`. Supported video extensions are `.mp4`, `.webm`, and `.mov`. Extension matching should be case-insensitive, but destination filenames should use the exact lowercase extension convention if feasible. If preserving the original suffix is simpler, preserve it and classify by lowercase suffix.

If no file exists for a scene, do not fail. Leave `visual.public_path` absent, set `visual.asset_status` to `"missing"` if the command is writing status fields, and allow Remotion to fall back to `PlaceholderScene`.

If exactly one supported file exists for a scene, copy it to:

    <out_dir>/visuals/<scene_id><suffix>

Set:

    visual.public_path = "visuals/<scene_id><suffix>"
    visual.asset_status = "prepared"
    visual.asset_source = "local"

If more than one supported file exists for the same scene id, fail clearly with `SyncCutError`. This prevents nondeterministic selection between, for example, `scene_003.mp4` and `scene_003.png`.

If an unsupported file exists with the scene id, such as `scene_003.txt`, ignore it unless no supported file exists and status fields are being written. In that case, record `asset_status: "unsupported"` only if the behavior is useful and tested; otherwise treat it like missing and keep the placeholder fallback.

Copying should be idempotent, mirroring the audio helper. If the destination does not exist, copy with `shutil.copy2` and count it as copied. If the destination exists and bytes are identical, reuse it and count it as reused. If the destination exists and bytes differ, overwrite it and count it as overwritten. If two different source paths would map to the same destination filename, fail clearly.

## Remotion Rendering Strategy

Add a small Remotion helper later, for example `remotion/src/components/visualAsset.ts`, with functions that accept `scene.visual.public_path` as untrusted input and return one of:

    {kind: "image", publicPath: string}
    {kind: "video", publicPath: string}
    null

The helper should return null when the path is missing, not a string, empty, not under `visuals/`, or has an unsupported extension. It should not check filesystem existence because Remotion components run in the browser/render context and should not perform Node filesystem reads. Missing files during render should be treated as a validation problem caught by smoke tests, not by component-side filesystem access.

Use these Remotion primitives from the installed `remotion` package:

    import {Img, OffthreadVideo, staticFile} from "remotion";

Images should render with:

    <Img src={staticFile(publicPath)} />

Videos should prefer:

    <OffthreadVideo src={staticFile(publicPath)} muted />

If `OffthreadVideo` creates an unexpected local render problem during implementation, record the exact error and consider `Video` from `remotion` as the fallback. The installed package exports both. Do not add `@remotion/media` unless local type-checking proves the installed `remotion` export is unavailable, which is not the case at plan creation.

The asset scene should use full-frame deterministic layout. A good rendering shape is an `AbsoluteFill` with a dark background, the image or video filling the frame with `objectFit: "cover"` or `"contain"`, and a small metadata strip showing scene id, visual type, section key, and `visual.public_path`. Keep styles inline or in local style objects. Do not use CSS animation, browser effects, network fetches, or external UI libraries.

If `visual.public_path` is absent or unsupported, render the existing `PlaceholderScene` unchanged except for a clearer label such as `AI Video Placeholder` or `B-roll Placeholder`.

## AI_VIDEO and B_ROLL Differences

`AI_VIDEO` and `B_ROLL` should use the same local path mechanics and fallback behavior. The difference is semantic:

`AI_VIDEO` means a future external process may generate or provide media based on the prompt. This phase must not generate that media. The component should only render a local file that already exists and is referenced by props.

`B_ROLL` means a future user or asset process may provide licensed footage or images. This phase must not download or scrape that media. The component should only render a local file that already exists and is referenced by props.

The two wrapper components may keep their current labels and accent colors. If a shared `VisualAssetScene` component is added, pass different labels such as `AI Video Asset` and `B-roll Asset` plus the existing accents.

## Plan of Work

Milestone 1 should stay entirely inside `remotion/` and this plan. Update `remotion/src/types.ts` to accept optional visual asset fields. Add a small helper under `remotion/src/components/` to classify supported public asset paths. Add a shared asset frame component only if it reduces duplication between `AiVideoScene.tsx` and `BRollScene.tsx`. Update `AiVideoScene.tsx` and `BRollScene.tsx` so they render a local asset when `scene.visual.public_path` is valid and fall back to `PlaceholderScene` otherwise. Do not change `SceneRenderer.tsx`, `Video.tsx`, Python files, package dependencies, or scripts.

Milestone 2 is optional and should happen only after Milestone 1 is reviewed. Add pure Python helpers for local visual asset preparation, likely in a new `synccut/visual_assets.py` or by extending a clearly named asset module without disturbing audio helpers. Add a thin Typer command named `prepare-visual-assets`. Write focused tests for matching, copying, idempotence, missing assets, duplicate candidate collisions, unsupported extension behavior, props updates, deterministic JSON writing, and expected CLI failures without tracebacks.

Milestone 3 should validate the full local visual asset workflow with synthetic local assets. Regenerate props and audio assets, create or use small local image/video test files outside tracked source where practical, run the optional visual asset command if implemented, run `npm run typecheck`, and run `npm run render:smoke:local` when Chrome launch is permitted. Record artifact sizes and exact environment failures if browser launch is blocked.

## Milestone 1: Remotion Types and Fallback Asset Rendering

At the end of this milestone, current `remotion/props.json` should still type-check even though it has no visual public paths. If a developer manually adds `"public_path": "visuals/scene_001.png"` to an `AI_VIDEO` or `B_ROLL` scene and places the file under `remotion/public/visuals/`, the component should render that local asset. If the field is missing or unsupported, the existing placeholder should remain.

Edit only:

    remotion/src/types.ts
    remotion/src/components/AiVideoScene.tsx
    remotion/src/components/BRollScene.tsx
    remotion/src/components/visualAsset.ts
    optionally remotion/src/components/VisualAssetScene.tsx
    docs/plans/remotion-visual-asset-strategy.md

Do not edit Python source files, `SceneRenderer.tsx`, `Video.tsx`, package scripts, or dependencies.

Validation:

    cd remotion
    npm run typecheck
    cd ..
    .venv/bin/python -m pytest

Acceptance: TypeScript passes with base props that do not have `visual.public_path`, Python tests still pass, `AI_VIDEO` and `B_ROLL` still fall back to placeholders by default, and the plan records the milestone result.

## Milestone 2: Optional Local Visual Asset Copy Command

At the end of this milestone, if approved, a developer should be able to run:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

The command should copy only local files that already exist under `assets/visuals/`, matching by `scene_id`, into `remotion/public/visuals/`. It should update `remotion/props.json` in place with `visual.public_path` for matched `AI_VIDEO` and `B_ROLL` scenes, preserve original prompt and data fields, and leave missing assets as safe placeholder fallbacks.

The command summary should be stable, for example:

    Prepared Remotion visual assets for remotion/props.json
    visual_copied: 2
    visual_reused: 0
    visual_overwritten: 0
    visual_missing: 15
    visual_assets: 2
    public_dir: remotion/public

Expected tests:

- valid local image copy creates `public/visuals/<scene_id>.png` and adds `visual.public_path`
- valid local video copy creates `public/visuals/<scene_id>.mp4` and adds `visual.public_path`
- missing assets do not fail and keep placeholders possible
- duplicate supported files for one scene id fail clearly
- unsupported files do not get copied or rendered
- rerunning with identical destination reuses the file
- rerunning with changed source overwrites and reports overwrite count
- props preserve original `visual.prompt` and `visual.data`
- optional `assets.visuals` entries are deterministic if implemented
- CLI expected failures print `Error:` without traceback
- JSON writing uses two-space indentation and a trailing newline

Validation:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck

Do not add any AI generation, B-roll download, scraping, media decoding, transcoding, ffmpeg call, Remotion render invocation from Python, or final MP4 behavior.

## Milestone 3: Synthetic Asset Validation and Smoke Render

At the end of this milestone, the local visual asset strategy should be demonstrated with synthetic local assets and documented artifact policy. Use small local files; do not fetch external media. Prefer assets created in a temporary or ignored location. If a checked-in test fixture is needed, keep it tiny and non-production, but generated media under `remotion/public/visuals/` should not be committed.

Suggested validation sequence from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

If Milestone 2 exists, prepare visual assets:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

Then validate Remotion:

    cd remotion
    npm run typecheck
    npm run still:local
    npm run render:smoke:local

If local Chrome launch is blocked by the sandbox, record the exact error and rerun with browser launch permission if available. Do not add workaround code. From the repository root, run:

    .venv/bin/python -m pytest

Record copied visual files, generated render artifacts, typecheck result, smoke render result, and pytest result in this plan.

## Validation and Acceptance

The Remotion-only acceptance criteria are:

- `SyncCutVisual` supports optional visual asset fields while current props without those fields still type-check.
- `AiVideoScene.tsx` and `BRollScene.tsx` render a supported local `visual.public_path` through `staticFile()`.
- Missing, empty, non-string, non-`visuals/`, or unsupported public paths fall back to `PlaceholderScene`.
- No new runtime dependency is added.
- `SceneRenderer.tsx` still dispatches all seven supported visual types.
- `Video.tsx` still preserves section audio behavior.
- `cd remotion && npm run typecheck` passes.
- `.venv/bin/python -m pytest` passes.

If the Python copy command is implemented, acceptance additionally requires:

- The command is separate from `export-remotion` and `prepare-remotion-assets`.
- The command is thin at the CLI layer and delegates to testable pure helpers.
- Copy behavior is idempotent and deterministic.
- Missing visual assets are handled as placeholder fallbacks, not fatal errors.
- Duplicate supported files for the same scene id fail clearly.
- Original prompt/data fields are preserved while public path metadata is added.
- Focused helper and CLI tests cover success and expected failure paths.

Smoke render validation is optional when the environment blocks browser launch, but exact failures must be recorded. Do not treat the known Chrome sandbox or network limitations as Remotion component failures.

## Idempotence and Recovery

The Remotion-only milestone is safe to rerun because it only changes TypeScript source and does not require generated media. If a manually added `visual.public_path` points at a missing file, remove that field or place the file under `remotion/public/visuals/`; the component fallback behavior should keep previews from crashing on unsupported values.

The optional visual asset command should be safe to rerun. It should create `remotion/public/visuals/` if missing, reuse identical copied files, overwrite changed destination files, and write deterministic JSON. If the command fails because two source files match the same scene id, remove or rename one candidate and rerun. If props become unsuitable during manual experimentation, regenerate them with:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not use destructive git commands for recovery unless explicitly requested by the user.

## Generated Artifacts and Commit Policy

Do not commit generated visual media or render output:

- `remotion/public/visuals/*`
- `remotion/public/audio/*.mp3`
- `remotion/out/preview.png`
- `remotion/out/smoke.mp4`
- `timeline.json`
- `__pycache__/`
- `.pytest_cache/`

The current `.gitignore` already ignores `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`. If implementation discovers a generated asset path that is not ignored, update `.gitignore` narrowly and record the decision here.

`remotion/props.json` is sample input for the Remotion project and may be committed when intentionally regenerated. If a future visual asset command writes local `visual.public_path` values into `remotion/props.json`, decide during final review whether that sample props file should include those paths. Do not commit `remotion/public/visuals/*`, so committed sample props with visual public paths should only reference assets that future developers can recreate or should be avoided.

## Explicit Exclusions

This phase must not:

- generate AI video
- call image or video generation APIs
- download B-roll
- scrape or fetch external media
- add external asset acquisition
- call ffmpeg directly
- decode, probe, trim, transcode, or normalize media
- assemble the full final MP4
- add Python commands that invoke Remotion rendering
- parse DOCX
- add GUI or web app behavior
- change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, or render smoke behavior unless a clear bug is found and recorded
- add heavy chart or media management dependencies
- require visual assets to exist for type-checking

## Interfaces and Dependencies

Use the installed `remotion` package for React media primitives. At plan creation, the installed package exports `Img`, `Video`, `OffthreadVideo`, and `staticFile`. Prefer `Img` for images and `OffthreadVideo` for videos. Use `Video` only if implementation discovers a clear local issue with `OffthreadVideo` and records the exact reason in this plan. Do not add `@remotion/media` unless the installed package unexpectedly lacks the required exports in a future environment.

Use only standard-library Python modules if the optional local-copy command is implemented: `json`, `pathlib.Path`, `shutil.copy2`, `filecmp`, `dataclasses`, and existing `SyncCutError` validation helpers. Keep CLI logic in `synccut/cli.py` thin by delegating to helper functions.

Expected TypeScript helper shape:

    export type VisualAssetKind = "image" | "video";

    export interface PreparedVisualAsset {
      kind: VisualAssetKind;
      publicPath: string;
    }

    export const getPreparedVisualAsset = (value: unknown): PreparedVisualAsset | null => {
      // validate string, visuals/ prefix, and supported extension
    };

Expected optional Python helper shape:

    @dataclass(frozen=True)
    class PreparedVisualAsset:
        scene_id: str
        visual_type: str
        source_path: str
        destination_path: str
        public_path: str

    @dataclass(frozen=True)
    class VisualAssetPrepareResult:
        props_path: Path
        public_dir: Path
        visuals_dir: Path
        copied: int
        reused: int
        overwritten: int
        missing: int
        visual_assets: list[PreparedVisualAsset]

    def prepare_visual_assets_file(
        props_path: Path,
        assets_dir: Path,
        out_dir: Path,
    ) -> VisualAssetPrepareResult:
        ...

## Revision Notes

2026-05-11 / Codex: Initial ExecPlan created from the requested phase scope after reading the required docs, prior plans, current Remotion files, generated props, Python exporter and asset helper, and ignore rules. The plan chooses Remotion-only optional public path support as the first milestone and defers any local-copy Python command to a separate optional milestone to preserve existing command behavior.

2026-05-11 / Codex: Final review cleanup added a narrow `assets/visuals/` ignore rule because Milestone 3 created generated synthetic source assets there and `git status` showed them as untracked rather than ignored.
