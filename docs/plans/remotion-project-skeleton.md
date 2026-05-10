# Create a minimal Remotion project skeleton

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can already export `remotion/props.json` from a validated `timeline.json`, but there is not yet a Remotion app that can consume that file. This phase adds a minimal TypeScript Remotion project under `remotion/` that registers one composition from `props.composition`, displays each exported scene at its exported frame range, and renders placeholder visuals based on `visual_type`.

After this change, a user can generate `remotion/props.json` with the existing Python CLI, run the Remotion project from the `remotion/` directory, and see a placeholder video timeline in Remotion Studio. The placeholders should show enough scene metadata to verify that frame timing, dialogue, sections, visual prompts, and visual data are flowing into React components. This phase does not call ffmpeg directly, assemble a final MP4, parse DOCX, generate AI video, download B-roll, build a GUI, or change the Python CLI behavior.

## Progress

- [x] (2026-05-10T17:48:37Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, and `docs/plans/export-remotion-props.md`.
- [x] (2026-05-10T17:48:37Z) Inspected the current repository structure and confirmed `remotion/` exists but contains no Remotion project files.
- [x] (2026-05-10T17:48:37Z) Checked Remotion project conventions with the local Remotion best-practices skill and Context7 documentation: use `registerRoot()` in `src/index.ts`, `Composition` in `src/Root.tsx`, and `Sequence` for frame-timed scene display.
- [x] (2026-05-10T17:48:37Z) Created this ExecPlan for the Remotion project skeleton.
- [x] (2026-05-10T18:04:03Z) Implemented Milestone 1: generated `remotion/props.json`, created the standalone Remotion package shell, added TypeScript config, entry point, prop loader, shared types, and a tiny `Root.tsx` stub needed for the entry import.
- [x] (2026-05-10T18:15:48Z) Implemented Milestone 2: replaced the `Root.tsx` stub with the real composition, added `Video.tsx`, added scene dispatch, and added placeholder wrappers for all supported visual types.
- [x] (2026-05-10T18:20:12Z) Completed Milestone 3 validation: `npm run typecheck` passed, `npm run still` reached Remotion but failed while downloading Chrome Headless Shell due DNS `EAI_AGAIN remotion.media`, and `.venv/bin/python -m pytest` passed.
- [x] (2026-05-10T18:30:11Z) Completed Milestone 4: regenerated `timeline.json` and `remotion/props.json` from examples, validated timeline and props counts, ran Remotion type-check, attempted Studio startup, and reran the Python pytest suite.

## Surprises & Discoveries

- Observation: The `remotion/` directory already exists but is empty.
  Evidence: `find remotion -maxdepth 4 -type f | sort` printed no files, and `ls -la remotion` showed only `.` and `..`.
- Observation: The Python exporter already defines the Remotion props schema and fixed composition defaults.
  Evidence: `synccut/remotion_exporter.py` defines `DEFAULT_COMPOSITION_ID = "SyncCutVideo"`, `DEFAULT_FPS = 30`, `DEFAULT_WIDTH = 1920`, `DEFAULT_HEIGHT = 1080`, and exports `composition`, `sections`, `scenes`, `assets`, and `warnings`.
- Observation: The repository has no Node package at the root and no existing frontend toolchain.
  Evidence: `pyproject.toml` only declares the Python package and dependencies; no root `package.json` was listed by repository inspection.
- Observation: Remotion docs use `registerRoot(RemotionRoot)` from a `src/index.ts` entry file and `Composition` inside `Root.tsx`.
  Evidence: Context7 Remotion documentation examples show `import {registerRoot} from "remotion"; import {RemotionRoot} from "./Root"; registerRoot(RemotionRoot);` and a `Composition` with `id`, `component`, `durationInFrames`, `fps`, `width`, `height`, and `defaultProps`.
- Observation: The first sandboxed `npm install` did not produce output or create `node_modules`; rerunning with approved network access completed normally.
  Evidence: After the sandboxed install attempt, `find node_modules -maxdepth 1 -type d` reported `find: 'node_modules': No such file or directory`. The approved `npm install` then reported `added 11 packages, and audited 12 packages in 3s` and `found 0 vulnerabilities`.
- Observation: `npm install` resolved Remotion 4.0.459 while keeping the package manifest on the broad `^4.0.0` Remotion range.
  Evidence: `remotion/package-lock.json` lists `node_modules/remotion` with version `4.0.459`.
- Observation: The real `Root.tsx`, `Video.tsx`, dispatcher, and placeholder components type-check against the generated example `remotion/props.json` without requiring changes to the Python exporter schema.
  Evidence: From `remotion/`, `npm run typecheck` completed with no TypeScript errors after Milestone 2 implementation.
- Observation: The initial `npm run still` command failed before Remotion could run because no `remotion` executable existed in `node_modules/.bin`.
  Evidence: `npm run still` printed `sh: 1: remotion: not found`; `node -p "require('./node_modules/remotion/package.json').bin"` returned `undefined`; `find node_modules/.bin` listed `loose-envify`, `tsc`, and `tsserver`, but not `remotion`.
- Observation: Installing `@remotion/cli` supplied the Remotion CLI but introduced current Remotion composition typings that required explicit props typing.
  Evidence: After `npm install --save-dev @remotion/cli@^4.0.0`, `npm run typecheck` first reported `Type '({ metadata, scenes, sections }: SyncCutProps) => JSX.Element' is not assignable to type 'LooseComponentType<Record<string, unknown>>'`, then `Expected 2 type arguments, but got 1`. Adding `Composition<any, SyncCutProps>` and making `SyncCutProps` record-compatible fixed type-checking.
- Observation: `npm run still` did not produce `remotion/out/preview.png` because Remotion could not download Chrome Headless Shell in this environment.
  Evidence: The command printed `Downloading Chrome Headless Shell https://www.remotion.dev/chrome-headless-shell`, then failed with `Error: getaddrinfo EAI_AGAIN remotion.media`, including `code: 'EAI_AGAIN'`, `syscall: 'getaddrinfo'`, and `hostname: 'remotion.media'`.
- Observation: Fresh real-example data still matches the expected export shape and frame counts.
  Evidence: After regenerating, `timeline.json` reported 33 scenes, 7 sections, and 752.79 seconds. `remotion/props.json` reported 33 scenes, 7 sections, fps 30, duration 22584 frames, first scene `scene_001`, last scene `scene_033`, and one exported warning from validation.
- Observation: Studio startup could not be manually verified in this sandbox because Remotion failed while reading network interfaces.
  Evidence: `timeout 8s npm run studio` failed with `SystemError [ERR_SYSTEM_ERROR]: A system error occurred: uv_interface_addresses returned Unknown system error 1`, originating from `node:os:223:16` and Remotion's `port-config.js`.

## Decision Log

- Decision: Put a standalone Node/Remotion package under `remotion/` instead of adding Node dependencies to the repository root.
  Rationale: SyncCut's Python package and CLI should remain unchanged. A standalone Remotion package keeps rendering concerns isolated and lets users install Node dependencies only when they are working on Remotion.
  Date/Author: 2026-05-10 / Codex
- Decision: Load the default props by importing `../props.json` from `remotion/src/props.ts`.
  Rationale: The completed Python command writes `remotion/props.json`. Importing it through a typed module is simple for Studio previews, avoids runtime filesystem reads in React components, and works with TypeScript when `resolveJsonModule` is enabled.
  Date/Author: 2026-05-10 / Codex
- Decision: Register exactly one composition whose id, width, height, fps, and duration come from `props.composition`.
  Rationale: The exported props file already carries the composition metadata. The Remotion app should consume it rather than duplicating constants that could drift from the exporter.
  Date/Author: 2026-05-10 / Codex
- Decision: Render scenes with Remotion `Sequence` using `from={scene.start_frame}` and `durationInFrames={scene.duration_frames}`.
  Rationale: The exporter has already converted global seconds into frame numbers. The Remotion app should trust those fields and should not recompute timing from seconds, alignment text, or audio.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep all visual renderers placeholder-based in this phase.
  Rationale: The requested phase is a skeleton that proves data and timing flow. Real AI video assets, B-roll footage, chart rendering, table rendering, and final visual design belong to later phases.
  Date/Author: 2026-05-10 / Codex
- Decision: Do not add a package script that renders an MP4 in this phase.
  Rationale: The user explicitly excluded final MP4 assembly, and Remotion media rendering may invoke ffmpeg internally. Studio preview, type-checking, and still-frame rendering are enough to validate the skeleton without creating a final video artifact.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep audio visible as metadata and do not mount audio tracks by default.
  Rationale: The exported `assets.audio` and scene `audio.path` values are references created by the Python pipeline. Proper multi-section audio placement and public asset path handling need a dedicated follow-up. For this phase, showing audio paths in placeholders proves the data is available without processing media.
  Date/Author: 2026-05-10 / Codex
- Decision: Add `remotion/src/Root.tsx` as a tiny `RemotionRoot` stub that returns `null` during Milestone 1.
  Rationale: `src/index.ts` must import and register a root component to type-check, but the user explicitly asked not to implement the real `Root.tsx` composition until a later milestone unless a stub was needed. Returning `null` keeps the shell compilable without adding composition or rendering behavior.
  Date/Author: 2026-05-10 / Codex
- Decision: Let `npm install` create `remotion/package-lock.json`.
  Rationale: The user required dependency installation when dependencies were not installed. The lockfile records the exact dependency versions used for successful validation and keeps the standalone Remotion package reproducible.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep placeholder layout styling inline in `PlaceholderScene.tsx`.
  Rationale: The phase requires no external UI libraries and no GUI/web app. Inline style objects keep the rendering self-contained, avoid CSS animation risk, and make the placeholder frame deterministic for Remotion.
  Date/Author: 2026-05-10 / Codex
- Decision: Add a small persistent metadata line in `Video.tsx`.
  Rationale: The plan allowed a subtle metadata layer. Showing total scenes, total sections, and total frames helps confirm the composition is using exported props without adding controls or changing scene timing.
  Date/Author: 2026-05-10 / Codex
- Decision: Add `@remotion/cli` as a development dependency.
  Rationale: The required `studio` and `still` scripts call a `remotion` binary, but the installed `remotion` runtime package does not expose that binary. Adding the CLI package is a clear package bug fix needed to run the validation command without adding render scripts or changing application behavior.
  Date/Author: 2026-05-10 / Codex
- Decision: Make `SyncCutProps` compatible with Remotion's `Record<string, unknown>` props constraint and type the composition as `Composition<any, SyncCutProps>`.
  Rationale: The current Remotion CLI typings require a schema type and props type, and composition props must satisfy a record-like constraint. This keeps the component typed with the existing exported props shape while preserving the runtime behavior required by the plan.
  Date/Author: 2026-05-10 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. The repository now has a standalone Remotion package shell under `remotion/` with `package.json`, `package-lock.json`, `tsconfig.json`, `src/index.ts`, `src/Root.tsx`, `src/props.ts`, and `src/types.ts`. The generated `remotion/props.json` exists and was created by the existing Python `export-remotion` command from a fresh example timeline.

Validation for Milestone 1 passed. From `remotion/`, `npm run typecheck` completed with no TypeScript errors. From the repository root, `.venv/bin/python -m pytest` collected 101 tests and all passed. No Python source files or existing Python CLI command behavior were changed. The real composition, video component, scene dispatch, placeholder visual components, audio playback, and Remotion rendering logic remain for later milestones.

Milestone 2 is complete. `remotion/src/Root.tsx` now registers one Remotion composition using `defaultProps.composition` for id, width, height, fps, and duration. `remotion/src/Video.tsx` accepts `SyncCutProps`, uses `AbsoluteFill`, and maps every exported scene to a `Sequence` using `scene.start_frame` and `scene.duration_frames` without recomputing timing from seconds. `SceneRenderer.tsx` dispatches all seven normalized visual types to thin placeholder wrapper components. `PlaceholderScene.tsx` renders a full-frame readable placeholder with scene id, visual type, section key, frame and second ranges, dialogue excerpt, visual prompt or data summary, and the audio path as metadata only.

Validation for Milestone 2 passed. From `remotion/`, `npm run typecheck` completed with no TypeScript errors. From the repository root, `.venv/bin/python -m pytest` collected 101 tests and all passed. No Python source files or existing Python CLI command behavior were changed. No audio playback, final MP4 render, ffmpeg call, AI video generation, B-roll download, external asset download, GUI, or web app behavior was added.

Milestone 3 is complete. The lightweight Remotion validation commands were run from `remotion/`. A clear package bug was found and fixed: `@remotion/cli` was added so the existing `studio` and `still` scripts have a `remotion` executable. Current Remotion typings also required a narrow type fix in `Root.tsx` and `types.ts`. After those fixes, `npm run typecheck` completed with no TypeScript errors.

The still-frame render was attempted but did not generate `remotion/out/preview.png` because this environment could not resolve `remotion.media` while Remotion was downloading Chrome Headless Shell. The exact failure was `Error: getaddrinfo EAI_AGAIN remotion.media` with `code: 'EAI_AGAIN'`, `syscall: 'getaddrinfo'`, and `hostname: 'remotion.media'`. No workaround was added. From the repository root, `.venv/bin/python -m pytest` collected 101 tests and all passed. No Python source files or existing Python CLI command behavior were changed. No MP4 render script, ffmpeg call, audio playback, AI video generation, B-roll downloading, real chart/table rendering, GUI, or web app behavior was added.

Milestone 4 is complete. A fresh `timeline.json` was generated from `examples/scenes.json`, `examples/audio`, and `examples/alignments` using the existing `build-timeline` command. `validate-timeline` accepted the generated timeline with 33 scenes, 7 sections, duration 752.79 seconds, and one validation warning: `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `export-remotion` wrote `remotion/props.json` with 33 scenes, 7 sections, fps 30, duration 22584 frames, and one warning.

Final validation for this phase passed where the environment supports it. From `remotion/`, `npm run typecheck` completed with no TypeScript errors against the fresh props file. Studio startup was attempted with `timeout 8s npm run studio`, but manual preview could not be verified because the environment returned `uv_interface_addresses returned Unknown system error 1` while Remotion was resolving network interfaces for the preview server. The Milestone 3 still-frame limitation remains: no `remotion/out/preview.png` exists because Chrome Headless Shell download failed with DNS `EAI_AGAIN remotion.media`. From the repository root, `.venv/bin/python -m pytest` collected 101 tests and all passed. No Python source files or existing Python CLI command behavior were changed, and no excluded future-phase behavior was added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is currently a Python 3.11+ Typer CLI package with tests run by pytest. The existing Python files include `synccut/cli.py`, `synccut/remotion_exporter.py`, `synccut/timeline_validator.py`, and related timeline-building modules. Do not change these files during this phase unless a clear bug is discovered and recorded in this plan.

The completed commands are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

The new work is a Remotion project. Remotion is a React and TypeScript framework for video compositions. A composition is a named video entry that has width, height, frames per second, duration in frames, and a React component to render. A sequence is a Remotion component that shows its children only for a specific frame range. A frame is an integer position on the video timeline; at 30 fps, frame 30 is one second after frame 0.

At plan creation, the `remotion/` directory was empty. After Milestone 1, it contains the package shell and generated props file. The full target structure for this phase is:

    remotion/
      package.json
      package-lock.json
      props.json
      tsconfig.json
      src/
        index.ts
        Root.tsx
        Video.tsx
        types.ts
        props.ts
        components/
          SceneRenderer.tsx
          PlaceholderScene.tsx
          AiVideoScene.tsx
          BRollScene.tsx
          ChartScene.tsx
          ComparisonCardScene.tsx
          TableScene.tsx
          ShareBreakdownScene.tsx
          TimelineScene.tsx

The user-suggested structure did not list `src/index.ts`, but Remotion needs an entry file that calls `registerRoot()`. Add it as part of the minimal skeleton.

## Expected remotion/props.json Input Structure

The app consumes `remotion/props.json`, which is generated by the existing Python command `synccut export-remotion timeline.json --out remotion/props.json`. The Remotion app must not mutate this file. The expected root object has:

    {
      "metadata": {
        "generated_by": "synccut export-remotion",
        "source_timeline": "timeline.json",
        "fps": 30,
        "duration_sec": 752.79,
        "duration_frames": 22584,
        "total_scenes": 33,
        "total_sections": 7
      },
      "composition": {
        "id": "SyncCutVideo",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration_frames": 22584
      },
      "sections": [
        {
          "section_key": "01_HOOK",
          "section": "HOOK",
          "section_order": 1,
          "start_sec": 0.0,
          "end_sec": 18.39,
          "duration_sec": 18.39,
          "start_frame": 0,
          "end_frame": 552,
          "duration_frames": 552,
          "audio": {"path": "examples/audio/01_HOOK.mp3"},
          "alignment": {"path": "examples/alignments/01_HOOK_alignment_tmp.json"}
        }
      ],
      "scenes": [
        {
          "id": "scene_001",
          "scene_order": 1,
          "section": "HOOK",
          "section_order": 1,
          "section_key": "01_HOOK",
          "start_sec": 0.0,
          "end_sec": 9.137,
          "duration_sec": 9.137,
          "local_start_sec": 0.0,
          "local_end_sec": 9.137,
          "start_frame": 0,
          "end_frame": 274,
          "duration_frames": 274,
          "visual_type": "AI_VIDEO",
          "visual": {
            "type": "AI_VIDEO",
            "prompt": "Original prompt or null",
            "data": null
          },
          "dialogue": {
            "text": "Original dialogue",
            "paragraphs": ["Original dialogue paragraph"]
          },
          "audio": {"path": "examples/audio/01_HOOK.mp3"},
          "alignment": {
            "path": "examples/alignments/01_HOOK_alignment_tmp.json",
            "match_method": "sentence",
            "matched_units": ["sentence:0"]
          },
          "warnings": []
        }
      ],
      "assets": {
        "audio": [
          {"section_key": "01_HOOK", "path": "examples/audio/01_HOOK.mp3"}
        ],
        "visuals": []
      },
      "warnings": []
    }

The supported normalized visual types are `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`. The Remotion app should not accept or normalize `B-ROLL`; normalized props must already use `B_ROLL`.

## Interfaces and Dependencies

Create `remotion/package.json` as a standalone Node package. Use React, Remotion, TypeScript, and their type packages. Keep dependency versions reasonably current for the implementation date, but do not research or pin unrelated packages. If using Context7 or local package metadata reveals a specific current Remotion major version, use that major version consistently for `remotion` and any Remotion companion packages.

The package scripts should be:

    {
      "scripts": {
        "studio": "remotion studio src/index.ts",
        "typecheck": "tsc --noEmit",
        "still": "remotion still src/index.ts SyncCutVideo out/preview.png --frame=0"
      }
    }

Do not add a `render` script that creates an MP4 in this phase. If a future phase needs rendering, it should add an explicit script and plan entry.

Create `remotion/tsconfig.json` with TypeScript settings suitable for React JSX and JSON imports. It must enable `resolveJsonModule`, `esModuleInterop`, strict type-checking, and no emit. A reasonable target is modern browser JavaScript because Remotion bundles the app.

Create `remotion/src/types.ts` with these exported types:

    export type VisualType =
      | "AI_VIDEO"
      | "B_ROLL"
      | "CHART"
      | "COMPARISON_CARD"
      | "TABLE"
      | "SHARE_BREAKDOWN"
      | "TIMELINE";

    export type JsonValue =
      | string
      | number
      | boolean
      | null
      | JsonValue[]
      | {[key: string]: JsonValue};

    export interface SyncCutProps { ... }

The `SyncCutProps` interface must include `metadata`, `composition`, `sections`, `scenes`, `assets`, and `warnings`, matching the `props.json` shape above. Use explicit interfaces for `SyncCutScene`, `SyncCutSection`, `SyncCutVisual`, `SyncCutDialogue`, `SyncCutAudioRef`, and `SyncCutAlignmentRef`. Keep fields required when the exporter always writes them. Use `JsonValue` for `visual.data`.

Create `remotion/src/props.ts` with:

    import propsJson from "../props.json";
    import type {SyncCutProps} from "./types";

    export const defaultProps = propsJson as SyncCutProps;

This is a compile-time import for the default Studio data. It means `remotion/props.json` must exist before running `npm run typecheck` or `npm run studio`. If the file is missing, the implementation instructions below generate it from examples.

Create `remotion/src/index.ts` with Remotion registration:

    import {registerRoot} from "remotion";
    import {RemotionRoot} from "./Root";

    registerRoot(RemotionRoot);

Create `remotion/src/Root.tsx`. It should import `Composition` from `remotion`, `Video` from `./Video`, and `defaultProps` from `./props`. Register one composition:

    <Composition
      id={defaultProps.composition.id}
      component={Video}
      durationInFrames={defaultProps.composition.duration_frames}
      fps={defaultProps.composition.fps}
      width={defaultProps.composition.width}
      height={defaultProps.composition.height}
      defaultProps={defaultProps}
    />

Use the exported composition id from props. Do not hard-code `SyncCutVideo` in `Root.tsx` except as a fallback if TypeScript requires an initial value, and record that decision if it becomes necessary.

Create `remotion/src/Video.tsx`. It should accept `SyncCutProps`, render a full-frame background using `AbsoluteFill`, and map every `scene` to:

    <Sequence
      key={scene.id}
      from={scene.start_frame}
      durationInFrames={scene.duration_frames}
    >
      <SceneRenderer scene={scene} sections={sections} />
    </Sequence>

It should also render a subtle persistent metadata layer if useful, but avoid clutter. The main proof of correctness is that each scene appears only during its own exported frame range. Do not use CSS animations or transitions; Remotion renders frame-by-frame and animation should come from frame-aware Remotion APIs in later phases.

Create `remotion/src/components/SceneRenderer.tsx`. It should dispatch by `scene.visual_type`:

    AI_VIDEO -> AiVideoScene
    B_ROLL -> BRollScene
    CHART -> ChartScene
    COMPARISON_CARD -> ComparisonCardScene
    TABLE -> TableScene
    SHARE_BREAKDOWN -> ShareBreakdownScene
    TIMELINE -> TimelineScene

For an unknown value, call `PlaceholderScene` with a clear fallback label. This fallback is defensive only; a valid props file should never contain an unknown visual type.

Create `remotion/src/components/PlaceholderScene.tsx`. This component should accept at least `scene`, `label`, and optional `accentColor`. It should show:

- scene id
- visual type
- section key
- timing range in frames and seconds
- a dialogue excerpt
- a visual prompt excerpt when present
- a compact visual data summary
- an audio path string, labeled as metadata only

Use plain React and inline styles or a small local style object. Keep the layout full-frame and readable at 1920x1080. Do not create a decorative web app or controls. This is a video frame, not a GUI.

Create the seven concrete placeholder components. Each should be a thin wrapper around `PlaceholderScene` with a distinct label and accent color:

    AiVideoScene.tsx -> "AI Video Placeholder"
    BRollScene.tsx -> "B-roll Placeholder"
    ChartScene.tsx -> "Chart Placeholder"
    ComparisonCardScene.tsx -> "Comparison Card Placeholder"
    TableScene.tsx -> "Table Placeholder"
    ShareBreakdownScene.tsx -> "Share Breakdown Placeholder"
    TimelineScene.tsx -> "Timeline Placeholder"

The placeholder components must not generate assets, fetch media, download stock footage, draw real charts, or parse complex visual data beyond summarizing it as text. The summary can use `JSON.stringify(scene.visual.data)` with truncation for readability.

## Timing Usage

Use frame timing from the exported props as the source of truth. The Remotion app must not recompute frames from seconds. For each scene:

    Sequence.from = scene.start_frame
    Sequence.durationInFrames = scene.duration_frames

The app may display `scene.end_frame`, but Remotion `Sequence` only needs the start frame and duration. Do not use `scene.end_frame - scene.start_frame` in React unless it is for a defensive warning; the exporter has already computed and validated `duration_frames`.

The root composition must use:

    durationInFrames = props.composition.duration_frames
    fps = props.composition.fps
    width = props.composition.width
    height = props.composition.height

If TypeScript validation catches a zero or negative scene duration in props, fail type-checking only if the data is statically impossible to type. Runtime schema validation is not required in this phase; the Python exporter and validator already own data validation.

## Audio Handling Strategy

For this phase, audio should remain metadata-only. The placeholder should display the section or scene audio path so users can verify that audio references are present. Do not mount Remotion `<Audio>` elements by default because the exported paths point to files such as `examples/audio/01_HOOK.mp3`, not necessarily files copied into Remotion's `public/` directory, and correct multi-section offset handling should be planned separately.

If an implementer finds a very small and idiomatic way to play audio without moving or processing assets, they must first update this plan's `Decision Log` with the exact behavior. The default plan is no audio playback.

## Plan of Work

Milestone 1 creates the Remotion project shell. This milestone is complete: `remotion/package.json`, `remotion/package-lock.json`, `remotion/tsconfig.json`, `remotion/src/index.ts`, `remotion/src/Root.tsx`, `remotion/src/types.ts`, and `remotion/src/props.ts` exist. The project installed Node dependencies, imports `props.json`, and type-checks the exported prop shape. No visual components were added; `Root.tsx` is only a minimal stub so the entry point can compile.

Milestone 2 creates the composition and placeholder renderer. This milestone is complete: `Root.tsx` registers the composition from `props.composition`, `Video.tsx` maps scenes to Remotion `Sequence` components, `SceneRenderer.tsx` dispatches by all seven supported visual types, and every visual type has a placeholder component. Starting Remotion Studio should show the placeholder for the scene active at the current frame.

Milestone 3 adds lightweight validation commands. This milestone is complete: `npm run typecheck` passes from the `remotion/` directory. `npm run still` was attempted, but Remotion could not download Chrome Headless Shell because DNS resolution for `remotion.media` failed with `EAI_AGAIN`; no preview PNG was generated. This still render is a sanity check only; it is not final video assembly.

Milestone 4 validates with real generated data. This milestone is complete: a fresh `timeline.json` and `remotion/props.json` were generated from `examples/`, the Python pytest suite passed, and Remotion type-checking passed. The Remotion app could not be manually opened in Studio in this environment because startup failed while reading network interfaces; this is recorded as an environment limitation rather than worked around in code.

## Concrete Steps

Run commands from the repository root unless the command explicitly changes directory:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut

Before editing, inspect current files:

    rg --files -g '!**/__pycache__/**' | sort
    find remotion -maxdepth 4 -type f | sort

Generate or refresh the props file required by the Remotion app:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

Create `remotion/package.json`, `remotion/tsconfig.json`, and the `remotion/src/` files listed in this plan. Keep every file additive inside `remotion/`. Do not edit Python source files for ordinary skeleton work.

Install dependencies from the `remotion/` directory:

    cd remotion
    npm install

If the environment blocks network access, request approval for `npm install` and record the result in `Surprises & Discoveries`. Do not vendor dependencies into the repository.

Run TypeScript validation:

    npm run typecheck

Expected success is no TypeScript errors and exit status 0. If TypeScript complains that `../props.json` is missing, return to the repository root and run the existing `export-remotion` command above.

Run a still-frame validation if the environment supports Remotion rendering:

    npm run still

Expected success is that Remotion creates `remotion/out/preview.png`. This proves the composition can be bundled and a frame can be rendered. If Chromium or system dependencies are unavailable, record the exact error and rely on `npm run typecheck` plus Studio startup as the validation for this phase.

Start Studio for manual inspection:

    npm run studio

Expected behavior is that Remotion Studio opens the `SyncCutVideo` composition. Scrubbing the timeline should show different placeholders at scene boundaries. Scene `scene_001` should begin at frame 0. The final composition duration should match `props.composition.duration_frames`.

Return to the repository root and run the Python tests to verify existing CLI behavior was not changed:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut
    .venv/bin/python -m pytest

Expected success is that all existing pytest tests pass. At plan creation, the suite contained tests for build-timeline, validation, inspection, and Remotion props export.

## Validation and Acceptance

This phase is accepted when all of the following are true:

- `remotion/package.json` exists and defines `studio`, `typecheck`, and `still` scripts.
- `remotion/tsconfig.json` exists and supports React JSX plus JSON imports.
- `remotion/src/index.ts` calls `registerRoot(RemotionRoot)`.
- `remotion/src/Root.tsx` registers one composition using `props.composition.id`, `width`, `height`, `fps`, and `duration_frames`.
- `remotion/src/types.ts` defines TypeScript types for the exported props shape and all seven normalized visual types.
- `remotion/src/props.ts` imports `../props.json` and exports it as `SyncCutProps`.
- `remotion/src/Video.tsx` renders each scene in a `Sequence` from `scene.start_frame` for `scene.duration_frames`.
- `SceneRenderer.tsx` dispatches every supported visual type to a distinct placeholder component.
- Placeholder components exist for `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`.
- Placeholder frames show scene id, visual type, section key, dialogue excerpt, and prompt or data summary.
- Audio references are visible as metadata but not processed or mounted as final audio.
- No Python CLI command behavior changes unless a clear bug is found and documented.
- No ffmpeg command is called directly.
- No final MP4 is assembled.
- No DOCX parsing, AI video generation, B-roll downloading, external asset downloading, GUI, or web app is added.
- `npm run typecheck` passes from `remotion/`.
- `.venv/bin/python -m pytest` passes from the repository root.
- If available, `npm run still` renders `remotion/out/preview.png`; if unavailable due to environment limits, the limitation is documented with the exact error.

## Idempotence and Recovery

All planned source changes are additive inside `remotion/` plus this plan file. Re-running `synccut export-remotion timeline.json --out remotion/props.json` is safe because the existing exporter intentionally overwrites the props file. Re-running `npm install` is safe and updates `package-lock.json` if dependency resolution changes; commit or review lockfile changes according to normal project practice when implementation is complete.

If TypeScript fails because props fields do not match the expected shape, inspect `synccut/remotion_exporter.py` and `tests/test_remotion_exporter.py` before changing the Remotion types. The exporter schema is the contract for this phase. Only change the Python exporter if the props file is clearly invalid for its documented contract, and record the bug and fix in this plan.

If Remotion Studio fails because `remotion/props.json` is absent, generate it with the existing CLI. If Node dependencies cannot install due to restricted network access, request approval for `npm install` and record the result. If still rendering fails due to browser or graphics environment limits, keep the code type-safe and record the limitation rather than adding unrelated rendering workarounds.

Do not use destructive git commands. Do not run `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, or `git rebase` unless the user explicitly asks.

## Explicit Exclusions

This phase must not:

- call ffmpeg directly
- assemble a final MP4
- add a Python command that invokes Remotion
- change `build-timeline`, `validate-timeline`, `inspect`, or `export-remotion` behavior unless fixing a clear documented bug
- parse DOCX
- generate AI video
- download B-roll or any external visual assets
- copy or transcode audio files
- build a GUI or web app
- implement real charts, tables, comparison cards, share breakdowns, or timeline graphics beyond placeholders
- introduce configurable FPS, width, height, or composition ids in the Python CLI
- add future asset-management logic

## Artifacts and Notes

At plan creation, `remotion/` contained no files. The current Python exporter writes the composition id `SyncCutVideo`, width `1920`, height `1080`, fps `30`, and a real-example duration of `22584` frames for `752.79` seconds.

Milestone 3 did not create `remotion/out/preview.png`. The still-frame command failed before rendering while trying to download Chrome Headless Shell:

    $ npm run still
    > synccut-remotion@0.1.0 still
    > remotion still src/index.ts SyncCutVideo out/preview.png --frame=0
    Downloading Chrome Headless Shell https://www.remotion.dev/chrome-headless-shell
    Downloading from: https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear
    Error: getaddrinfo EAI_AGAIN remotion.media

Milestone 3 successful validation commands:

    $ npm run typecheck
    > synccut-remotion@0.1.0 typecheck
    > tsc --noEmit

    $ .venv/bin/python -m pytest
    101 passed in 0.26s

Milestone 4 fresh real-data validation:

    $ .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    # Command exited successfully and wrote timeline.json.

    $ .venv/bin/synccut validate-timeline timeline.json
    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79
    warnings: 1
    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

    $ .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    Exported remotion/props.json
    scenes: 33
    sections: 7
    fps: 30
    duration_frames: 22584
    warnings: 1

    $ npm run typecheck
    > synccut-remotion@0.1.0 typecheck
    > tsc --noEmit

    $ timeout 8s npm run studio
    SystemError [ERR_SYSTEM_ERROR]: A system error occurred: uv_interface_addresses returned Unknown system error 1 (Unknown system error 1)

    $ .venv/bin/python -m pytest
    101 passed in 0.35s

The freshly generated `remotion/props.json` contains 33 scenes, 7 sections, fps 30, duration 22584 frames, first scene `scene_001`, last scene `scene_033`, and one warning. `remotion/out/preview.png` was not generated during this phase.

Important Remotion conventions used by this plan:

    src/index.ts calls registerRoot(RemotionRoot)
    src/Root.tsx contains a Composition
    Composition.defaultProps provides the props consumed by the Video component
    Sequence shows children for a frame range
    CSS transitions and CSS animations should not be used for video animation

This plan intentionally uses Remotion Studio and still-frame rendering as validation. It does not define an MP4 render command.

Revision note: Initial plan created on 2026-05-10 by Codex after reading required project docs, prior phase plans, current source files, current repository structure, the Remotion best-practices skill, and Context7 Remotion documentation. The plan is limited to creating a minimal Remotion skeleton that consumes `remotion/props.json`.

Revision note: Milestone 1 implemented on 2026-05-10 by Codex. The update records the generated props file, standalone package shell, dependency install result, TypeScript validation, pytest validation, and the decision to use a null `Root.tsx` stub until the composition milestone.

Revision note: Milestone 2 implemented on 2026-05-10 by Codex. The update records the real composition, scene sequence mapping, visual-type dispatcher, placeholder wrappers, inline placeholder layout decision, TypeScript validation, and pytest validation.

Revision note: Milestone 3 completed on 2026-05-10 by Codex. The update records the Remotion CLI dependency fix, current Remotion typing fix, successful type-check and pytest results, and the exact still-frame failure caused by `EAI_AGAIN remotion.media`.

Revision note: Milestone 4 completed on 2026-05-10 by Codex. The update records the fresh build-timeline, validate-timeline, export-remotion, Remotion type-check, Studio startup attempt, Python pytest result, the continuing still-frame limitation, and the final outcome for the Remotion project skeleton phase.
