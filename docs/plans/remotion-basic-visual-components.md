# Build basic Remotion visual components

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can now build a timed timeline, export `remotion/props.json`, prepare section audio under `remotion/public/audio/`, and show placeholder scenes in a Remotion project. The next useful step is to make the Remotion preview more representative by rendering simple visuals from the structured `visual.data` already present in props.

After this phase, scenes with `COMPARISON_CARD`, `TABLE`, `CHART`, `TIMELINE`, and `SHARE_BREAKDOWN` visual types should render basic data-driven frames instead of generic placeholder panels. Scenes with `AI_VIDEO` and `B_ROLL` should remain placeholders because this phase must not generate AI video, download B-roll, or add external asset management. A user should be able to run `npm run typecheck` from `remotion/` and, where the environment supports Remotion preview, open Studio or render a still to see real comparison cards, tables, charts, timelines, and share breakdowns driven entirely by `remotion/props.json`.

## Progress

- [x] (2026-05-11T07:11:52Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, `docs/plans/export-remotion-props.md`, `docs/plans/remotion-project-skeleton.md`, and `docs/plans/remotion-audio-assets.md`.
- [x] (2026-05-11T07:11:52Z) Inspected `remotion/src/types.ts`, `PlaceholderScene.tsx`, `ComparisonCardScene.tsx`, `TableScene.tsx`, `ChartScene.tsx`, `TimelineScene.tsx`, `ShareBreakdownScene.tsx`, `SceneRenderer.tsx`, AI/B-roll wrappers, and the current `remotion/props.json` visual data shapes.
- [x] (2026-05-11T07:11:52Z) Created this ExecPlan for basic data-driven Remotion visual components.
- [x] (2026-05-11T07:22:58Z) Implemented Milestone 1: added safe visual data helper utilities and a shared scene layout primitive.
- [x] (2026-05-11T07:27:36Z) Implemented Milestone 2: replaced `COMPARISON_CARD` and `TABLE` placeholders with basic data-driven components.
- [x] (2026-05-11T07:34:47Z) Implemented Milestone 3: replaced `CHART`, `TIMELINE`, and `SHARE_BREAKDOWN` placeholders with basic data-driven components.
- [x] (2026-05-11T07:43:23Z) Completed Milestone 4: validated against real generated props and documented still-frame environment limitations.

## Surprises & Discoveries

- Observation: The current `remotion/props.json` already contains useful structured visual data for the target components.
  Evidence: Inspecting props showed `COMPARISON_CARD: 5`, `TABLE: 4`, `CHART: 4`, `TIMELINE: 1`, `SHARE_BREAKDOWN: 2`, `AI_VIDEO: 6`, and `B_ROLL: 11`.
- Observation: Target visual data shapes are regular enough to render without schema changes.
  Evidence: comparison card data uses `headline`, `left`, `right`, and `footer`; table data uses `title`, `columns`, and `rows`; chart data uses `title`, `chart_type`, labels, `series[].points[]`, and annotations; timeline data uses `title` and `events`; share breakdown data uses `title`, `unit`, and `items`.
- Observation: The current visual components are thin wrappers around `PlaceholderScene`.
  Evidence: `ComparisonCardScene.tsx`, `TableScene.tsx`, `ChartScene.tsx`, `TimelineScene.tsx`, and `ShareBreakdownScene.tsx` import only `PlaceholderScene` plus types and return placeholder labels with accent colors.
- Observation: The current Remotion package already has React, React DOM, Remotion runtime, Remotion CLI, and TypeScript; no charting dependency is needed for this phase.
  Evidence: `remotion/package.json` contains the dependencies needed for React/Remotion components, and simple CSS/SVG drawing is enough for the requested basic visuals.
- Observation: Still rendering has a known environment limitation unrelated to visual component code.
  Evidence: Earlier validation recorded `npm run still` failing while downloading Chrome Headless Shell with `Error: getaddrinfo EAI_AGAIN remotion.media`. If this repeats, record it and rely on `npm run typecheck` plus code and props inspection.
- Observation: Milestone 1 did not require changes to scene dispatch or existing visual wrappers.
  Evidence: `remotion/src/components/visualData.ts` and `remotion/src/components/DataSceneFrame.tsx` were added, `SceneRenderer.tsx` and the placeholder wrapper files were left unchanged, and `npm run typecheck` passed.
- Observation: Milestone 2 did not require helper changes or dispatch changes.
  Evidence: `ComparisonCardScene.tsx` and `TableScene.tsx` now import the Milestone 1 parsers and `DataSceneFrame`; `SceneRenderer.tsx`, chart, timeline, share breakdown, AI video, and B-roll components were not edited.
- Observation: Milestone 3 also did not require parser, layout shell, or dispatch changes.
  Evidence: `ChartScene.tsx`, `TimelineScene.tsx`, and `ShareBreakdownScene.tsx` now use the existing Milestone 1 parsers and `DataSceneFrame`; `visualData.ts`, `DataSceneFrame.tsx`, `SceneRenderer.tsx`, AI video, and B-roll components were not edited.
- Observation: Fresh generated props contain data for every target visual scene.
  Evidence: The Milestone 4 inspection reported `target_missing_data: []` with visual counts `AI_VIDEO: 6`, `B_ROLL: 11`, `CHART: 4`, `COMPARISON_CARD: 5`, `SHARE_BREAKDOWN: 2`, `TABLE: 4`, and `TIMELINE: 1`.
- Observation: Still rendering remains blocked by the same environment network limitation as earlier phases.
  Evidence: `npm run still` attempted to download Chrome Headless Shell from `https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`, `code: 'EAI_AGAIN'`, `syscall: 'getaddrinfo'`, and `hostname: 'remotion.media'`.

## Decision Log

- Decision: Keep all changes in the Remotion project and this ExecPlan unless a clear bug is found.
  Rationale: The requested phase is a rendering-component phase. The existing Python CLI already exports the necessary props data and should remain stable.
  Date/Author: 2026-05-11 / Codex
- Decision: Use small local TypeScript helpers instead of adding a validation library or chart library.
  Rationale: The data shapes are simple and this phase prioritizes deterministic, robust, reviewable rendering. Runtime schema libraries or chart packages would add dependency surface without clear need.
  Date/Author: 2026-05-11 / Codex
- Decision: Fall back to `PlaceholderScene` when `visual.data` is missing or malformed.
  Rationale: Remotion rendering should not crash because one scene has unexpected data. The placeholder already shows scene metadata, dialogue, visual prompt, and a compact visual data summary, which is the right graceful degradation.
  Date/Author: 2026-05-11 / Codex
- Decision: Keep `AI_VIDEO` and `B_ROLL` as placeholders.
  Rationale: Rendering those types would require generated or downloaded media assets, which are explicitly excluded from this phase.
  Date/Author: 2026-05-11 / Codex
- Decision: Add `DataSceneFrame.tsx` during Milestone 1 instead of waiting for the first real visual component.
  Rationale: The target components all need the same full-frame shell, title treatment, and compact scene metadata strip. Creating the shell now keeps later component milestones focused on data rendering while staying inside the requested shared layout primitive scope.
  Date/Author: 2026-05-11 / Codex
- Decision: Limit table rendering to the first six rows and show a `+N more rows` note.
  Rationale: The current table data can include enough text to crowd a 1920x1080 frame. A fixed visible-row cap keeps rendering deterministic and avoids overlap while still making overflow explicit.
  Date/Author: 2026-05-11 / Codex
- Decision: Render `pie` chart data as ranked horizontal bars in this basic phase.
  Rationale: The phase explicitly allows pie/share-like data to render as bars and forbids adding chart libraries. Horizontal bars preserve labels and numeric values clearly while keeping the implementation deterministic and reviewable.
  Date/Author: 2026-05-11 / Codex
- Decision: Scale share breakdown bars against the largest raw value while displaying unnormalized raw values.
  Rationale: This gives a readable visual comparison without changing the data semantics. The component labels the total as `raw total` and displays each value with its unit so viewers can see that values were not normalized.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. `remotion/src/components/visualData.ts` now provides framework-independent helpers for untrusted `JsonValue` data: record, string, number, array, keyed getter, cell stringification, and truncation helpers. It also defines parsed interfaces and parser functions for `ComparisonData`, `TableData`, `ChartData`, `TimelineData`, and `ShareBreakdownData`. The parsers return parsed display data or null and do not throw for malformed `visual.data`.

Milestone 1 also added `remotion/src/components/DataSceneFrame.tsx`, a reusable full-frame Remotion layout shell for later data-driven scenes. It accepts `scene`, optional `section`, `title`, `kicker`, `accentColor`, and `children`, uses inline style objects, and shows a compact footer with scene id, visual type, and frame range. No existing visual component internals, `SceneRenderer` dispatch, Python source files, Python CLI behavior, runtime dependencies, AI video generation, B-roll downloading, ffmpeg behavior, MP4 assembly, DOCX parsing, GUI, or web app behavior were changed.

Milestone 1 verification passed. From `remotion/`, `npm run typecheck` completed successfully. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and passed all 114.

Milestone 2 is complete. `remotion/src/components/ComparisonCardScene.tsx` now calls `parseComparisonData(scene.visual.data)`, falls back to `PlaceholderScene` with `Comparison Card Data Missing` when data is malformed, and otherwise renders a data-driven comparison frame using `DataSceneFrame`. The rendered frame includes a headline or footer-derived title, two side-by-side panels, left and right labels and values, and an optional footer caption. Long values are truncated through `truncateText` and wrapped inside stable panel dimensions.

`remotion/src/components/TableScene.tsx` now calls `parseTableData(scene.visual.data)`, falls back to `PlaceholderScene` with `Table Data Missing` when data is malformed, and otherwise renders a data-driven table frame using `DataSceneFrame`. The rendered frame includes the table title, header cells from columns, body rows from parsed string cell values, a fixed first-six-row display limit, and a `+N more rows` note when rows are hidden. Table cells use stable grid columns and overflow-safe text wrapping. No helper files, scene dispatch, Python source files, Python CLI behavior, dependencies, chart/timeline/share breakdown rendering, AI video generation, B-roll downloading, ffmpeg behavior, MP4 assembly, GUI, or web app behavior were changed.

Milestone 2 verification passed. From `remotion/`, `npm run typecheck` completed successfully. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and passed all 114.

Milestone 3 is complete. `remotion/src/components/ChartScene.tsx` now calls `parseChartData(scene.visual.data)`, falls back to `PlaceholderScene` with `Chart Data Missing` when data is malformed, and otherwise renders a data-driven chart frame using `DataSceneFrame`. For line-like chart data it renders an SVG chart with axes, labels, a polyline, point markers, point values, optional axis labels, first-series metadata, annotations, and a small note for additional series. For `pie` chart data it renders ranked horizontal bars from the first series numeric points. No charting library, animation, media loading, or props schema change was added.

`remotion/src/components/TimelineScene.tsx` now calls `parseTimelineData(scene.visual.data)`, falls back to `PlaceholderScene` with `Timeline Data Missing` when data is malformed, and otherwise renders milestone cards from `events`, including event order, date, and label in a deterministic wrapped grid through `DataSceneFrame`.

`remotion/src/components/ShareBreakdownScene.tsx` now calls `parseShareBreakdownData(scene.visual.data)`, falls back to `PlaceholderScene` with `Share Breakdown Data Missing` when data is malformed, and otherwise renders input-order share rows with labels, raw numeric values plus unit, bars scaled to the largest raw value, item count, and raw total through `DataSceneFrame`. No helper files, layout files, scene dispatch, Python source files, Python CLI behavior, dependencies, AI video behavior, B-roll behavior, ffmpeg behavior, MP4 assembly, audio decoding/transcoding, DOCX parsing, GUI, or web app behavior were changed.

Milestone 3 verification passed. From `remotion/`, `npm run typecheck` completed successfully. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and passed all 114.

Milestone 4 is complete. Fresh example data was regenerated with `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json`, which completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Visual props inspection passed. The fresh props reported these counts: `AI_VIDEO: 6`, `B_ROLL: 11`, `CHART: 4`, `COMPARISON_CARD: 5`, `SHARE_BREAKDOWN: 2`, `TABLE: 4`, and `TIMELINE: 1`. The target data check reported `target_missing_data: []`, `total_scenes: 33`, and `duration_frames: 22584`, proving every scene targeted by the new basic visual components has a non-null `visual.data` payload in the generated sample props.

Final phase validation passed where the environment supports it. From `remotion/`, `npm run typecheck` completed successfully. `npm run still` did not generate `remotion/out/preview.png` because Remotion attempted to download Chrome Headless Shell from `remotion.media` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`; no workaround code was added. From the repository root, `.venv/bin/python -m pytest` collected 114 tests and passed all 114. No Python CLI changes, ffmpeg behavior, MP4 assembly, audio decoding/transcoding, DOCX parsing, AI video generation, B-roll downloading, GUI, or web app behavior were added.

Generated artifacts and commit policy for this phase are unchanged. `timeline.json` is regenerated data and should not be committed unless explicitly requested. `remotion/props.json` is the sample props file consumed by the Remotion project and may be committed when intentionally updated. `remotion/public/audio/*.mp3` are generated copied audio assets and should remain excluded from commit. `remotion/out/preview.png` was not generated; if produced in another environment, it should be treated as a generated preview artifact and excluded unless explicitly requested.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`. The Python CLI commands already exist and must not be changed in this phase unless a clear bug is discovered:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

The Remotion project consumes `remotion/props.json` through `remotion/src/props.ts`. `remotion/src/Root.tsx` registers one composition using `defaultProps.composition`. `remotion/src/Video.tsx` renders section audio and maps each scene to a Remotion `Sequence` using `scene.start_frame` and `scene.duration_frames`. `remotion/src/components/SceneRenderer.tsx` dispatches each normalized visual type to a scene component.

The current Remotion source files most relevant to this phase are:

    remotion/src/types.ts
    remotion/src/components/SceneRenderer.tsx
    remotion/src/components/PlaceholderScene.tsx
    remotion/src/components/AiVideoScene.tsx
    remotion/src/components/BRollScene.tsx
    remotion/src/components/ComparisonCardScene.tsx
    remotion/src/components/TableScene.tsx
    remotion/src/components/ChartScene.tsx
    remotion/src/components/TimelineScene.tsx
    remotion/src/components/ShareBreakdownScene.tsx

Important terms used in this plan:

Remotion is the React-based video project under `remotion/`. A Remotion frame is an integer timeline position; at the current 30 fps, frame 30 is one second after frame 0. A scene component is a React component that renders one exported scene inside the `Sequence` already created by `Video.tsx`. A visual type is the normalized string on `scene.visual_type`, one of `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, or `TIMELINE`. `visual.data` is JSON exported from the original scene planning data and typed in TypeScript as `JsonValue`, meaning it can be an object, array, string, number, boolean, or null.

## Current Visual Props Shape

The current `remotion/props.json` has 33 scenes. The current visual type counts are:

    AI_VIDEO: 6
    B_ROLL: 11
    CHART: 4
    COMPARISON_CARD: 5
    TABLE: 4
    TIMELINE: 1
    SHARE_BREAKDOWN: 2

The `COMPARISON_CARD` scenes have data shaped like:

    {
      "headline": "Business Models",
      "left": {
        "label": "Traditional model (Intel, 1987)",
        "value": "Design your own chips. Build your own fabs. Sell your own products."
      },
      "right": {
        "label": "Morris Chang's idea",
        "value": "Build fabs only. Make chips for anyone. Own no designs. Compete with no customers."
      },
      "footer": "Vertical Integration vs. Pure-play Foundry"
    }

Some comparison headlines can be null. Components must handle null or missing text.

The `TABLE` scenes have data shaped like:

    {
      "title": "Core mechanisms this video unpacks",
      "columns": ["Mechanism", "Description"],
      "rows": [
        ["1. The Foundry Singularity", "Why TSMC's business model created an irreversible monopoly"],
        ["2. The Physics Wall", "Why manufacturing at atomic scale is harder than rocket science"]
      ]
    }

Rows are arrays of cell values aligned to columns. Components should accept string or number cells and stringify other simple values safely if needed.

The `CHART` scenes have data shaped like:

    {
      "title": "Global Foundry Revenue ($B)",
      "chart_type": "line",
      "x_label": "Year",
      "y_label": "Revenue ($B)",
      "series": [
        {
          "name": "TSMC Revenue",
          "points": [
            {"x": "2010", "y": 13.3},
            {"x": "2015", "y": 26.9},
            {"x": "2020", "y": 47.8}
          ]
        }
      ],
      "annotations": [
        {"x": "General Area", "label": "Note: Compound growth ~10% per year for 15 years"}
      ]
    }

The sample chart types include `pie` and `line`, but this phase should not add a full charting library. Render a simple deterministic SVG or CSS chart based on numeric point values. For `pie`, a ranked bar chart or share-style bar display is acceptable because the phase goal is basic data-driven rendering, not final chart fidelity.

The `TIMELINE` scene has data shaped like:

    {
      "title": "TSMC's rise",
      "events": [
        {"date": "1987", "label": "TSMC founded with Taiwanese government backing"},
        {"date": "1994", "label": "First major Apple production win"}
      ]
    }

The `SHARE_BREAKDOWN` scenes have data shaped like:

    {
      "title": "TSMC's Top Customer Concentration 2024",
      "unit": "%",
      "items": [
        {"label": "Apple", "value": 25},
        {"label": "NVIDIA", "value": 11},
        {"label": "All Others", "value": 37}
      ]
    }

The `AI_VIDEO` and `B_ROLL` scenes currently have `visual.prompt` strings and `visual.data` null. They should remain metadata placeholders in this phase.

## Component Scope

These visual types become basic real components in this phase:

- `COMPARISON_CARD`
- `TABLE`
- `CHART`
- `TIMELINE`
- `SHARE_BREAKDOWN`

These visual types remain placeholders:

- `AI_VIDEO`
- `B_ROLL`

Do not change `SceneRenderer.tsx` dispatch behavior except as needed to pass through existing props. It already dispatches all seven supported visual types. The implementation work should replace the internals of the five target wrapper files and add shared helpers/components as needed.

## Proposed Component Architecture

Add a helper file such as `remotion/src/components/visualData.ts`. This file should contain only deterministic TypeScript functions that safely inspect `JsonValue`. It should not import React or Remotion unless a narrow type need appears. Suggested helpers:

    isRecord(value: JsonValue): value is Record<string, JsonValue>
    asString(value: JsonValue | undefined): string | null
    asNumber(value: JsonValue | undefined): number | null
    asArray(value: JsonValue | undefined): JsonValue[]
    getString(object: Record<string, JsonValue>, key: string): string | null
    getNumber(object: Record<string, JsonValue>, key: string): number | null
    getRecord(object: Record<string, JsonValue>, key: string): Record<string, JsonValue> | null
    getArray(object: Record<string, JsonValue>, key: string): JsonValue[]
    stringifyCell(value: JsonValue | undefined): string
    truncateText(value: string, maxLength: number): string

Add small parsing helpers for the target data shapes in the same file or a second file if it improves readability:

    parseComparisonData(data: JsonValue): ComparisonData | null
    parseTableData(data: JsonValue): TableData | null
    parseChartData(data: JsonValue): ChartData | null
    parseTimelineData(data: JsonValue): TimelineData | null
    parseShareBreakdownData(data: JsonValue): ShareBreakdownData | null

The parsed interfaces can live in `visualData.ts` near the parser functions. They should use plain string and number fields after validation so components remain simple. For example, `ChartPoint` should have `x: string` and `y: number`.

Optionally add a shared layout file such as `remotion/src/components/visualStyles.ts` or `DataSceneFrame.tsx` if the first component reveals repeated frame shell styles. Keep it local and small. A common frame shell may accept `scene`, `section`, `title`, `kicker`, `accentColor`, and children, and can display a compact metadata line. Do not add a global stylesheet or external UI library.

`PlaceholderScene` should remain available and should be used as the fallback when data is invalid. If useful, export its existing truncation or summary behavior through the new helper file, but avoid refactoring it unless needed by this phase.

## Safe Data Extraction Strategy

Every component must treat `scene.visual.data` as untrusted JSON. It must not assume an object shape without checking. A malformed data object should not throw during rendering. The flow for each component should be:

1. Call a parser helper with `scene.visual.data`.
2. If the parser returns null, render `PlaceholderScene` with a label such as `Comparison Card Data Missing` or `Chart Data Missing`.
3. If the parser returns data, render the basic visual.

The parser helpers should be strict enough to avoid broken visuals but forgiving enough to display partial data when safe. For example, a table with a title, at least one column, and at least one row can render even if some cells are missing; missing cells should render as an empty string. A chart should require at least one numeric point. A share breakdown should require at least one item with a label and numeric value.

Do not throw exceptions from component render paths for bad data. Do not use browser-only runtime effects such as `useEffect`, DOM measurement, `window`, `document`, network fetches, random numbers, timers, CSS transitions, or CSS animations. Remotion renders frame by frame, so render output should be deterministic for a given props object and frame.

## Design Style Constraints

The components should be readable at 1920 by 1080. Use inline styles or local style objects, as the current placeholders do. No external UI library is needed. Keep cards at an 8px border radius or less. Do not use CSS animations or browser transitions. Do not use viewport-scaled font sizes. Use stable dimensions, constrained grids, and overflow-safe text so long labels do not overlap.

The visual language should stay quiet and production-tool oriented rather than marketing-like. Use dark backgrounds compatible with the current `Video.tsx` backdrop, high-contrast text, restrained accent colors, and clear hierarchy. Avoid decorative gradient orbs, bokeh backgrounds, and one-note color palettes. The purpose is to make the exported data inspectable in video form, not to create final branded motion graphics.

Each basic component should include a compact scene metadata strip or footer with at least `scene.id`, `scene.section_key`, and frame range. This preserves the diagnostic value of the placeholder phase while making the main visual data-driven.

## Component-Specific Behavior

`ComparisonCardScene.tsx` should parse `headline`, `left.label`, `left.value`, `right.label`, `right.value`, and `footer`. It should render two side-by-side panels on desktop-sized frames, each with a label and value. Use headline as the title when present; otherwise use `scene.visual_type` or the footer. Show footer as a small caption if present. If either side is missing a label and value, fall back to `PlaceholderScene`.

`TableScene.tsx` should parse `title`, `columns`, and `rows`. It should render a simple table with a title, header row, and body rows. It should support two or more columns, clamp or truncate long cell text, and cap visible rows only if needed for readability. If the data has more rows than can fit, show the first rows that fit and a small note such as `+2 more rows`. If there are no columns or no rows, fall back to `PlaceholderScene`.

`ChartScene.tsx` should parse `title`, `chart_type`, optional axis labels, `series`, points, and annotations. It should render a simple SVG or CSS chart without external libraries. For line charts, draw a polyline based on normalized numeric `y` values and label the x positions. For pie or share-like charts, render horizontal bars using the numeric `y` values. If multiple series exist, render the first series clearly and optionally list other series names as metadata; do not build a complex legend unless it remains simple. If there are no numeric points, fall back to `PlaceholderScene`.

`TimelineScene.tsx` should parse `title` and `events`. It should render a horizontal milestone line with event dates and labels. If there are too many events for the width, keep the layout deterministic by wrapping into two rows or using compact cards above and below the line. If there are no events, fall back to `PlaceholderScene`.

`ShareBreakdownScene.tsx` should parse `title`, `unit`, and `items`. It should render percentage/share blocks or horizontal bars sorted in input order. Values should be numeric; if the unit is `%`, display values like `25%`. It may also show a total if useful, but it should not normalize values unless clearly labeled. If there are no valid items, fall back to `PlaceholderScene`.

`AiVideoScene.tsx` and `BRollScene.tsx` should remain thin wrappers around `PlaceholderScene`, with their existing labels and accent colors. Do not introduce media loading or asset path requirements for these types.

## Plan of Work

First, add visual data helper utilities under `remotion/src/components/visualData.ts`. Define the parsed interfaces and parser functions for the five target data shapes. Add a small number of helper functions for strings, numbers, arrays, object records, cell stringification, and truncation. Keep this file framework-independent and covered by TypeScript type-checking.

Second, optionally add a shared frame component under `remotion/src/components/DataSceneFrame.tsx` if it reduces repeated layout code. This component should use `AbsoluteFill` from `remotion` and type imports from React/SyncCut only. It should provide a consistent full-frame shell for data-driven visuals and a compact metadata strip.

Third, replace `ComparisonCardScene.tsx` and `TableScene.tsx` internals. Each file should parse data, fall back to `PlaceholderScene` if needed, and otherwise render the basic visual. Run `npm run typecheck` from `remotion/` after this milestone.

Fourth, replace `ChartScene.tsx`, `TimelineScene.tsx`, and `ShareBreakdownScene.tsx` internals. Reuse the same helpers and frame shell. Run `npm run typecheck` again.

Fifth, validate with the current real `remotion/props.json`. If it is stale or missing, regenerate it with the existing Python commands, then run `prepare-remotion-assets` if audio paths need to remain prepared. Run `npm run typecheck` from `remotion/` and `.venv/bin/python -m pytest` from the repository root. Optionally run `npm run still`; if it fails because Chrome Headless Shell cannot be downloaded or because the environment cannot support Remotion preview, record the exact error in this plan and do not add workaround code.

## Concrete Steps

Milestone 1 creates helper infrastructure only. Edit `remotion/src/components/visualData.ts` and, if useful, `remotion/src/components/DataSceneFrame.tsx`. Do not change scene dispatch or Python files. From `remotion/`, run:

    npm run typecheck

Expect TypeScript to complete with no errors.

Milestone 2 updates comparison and table rendering. Edit only Remotion component files and this plan. From `remotion/`, run:

    npm run typecheck

If type-checking fails, fix the TypeScript issue without changing the Python CLI.

Milestone 3 updates chart, timeline, and share breakdown rendering. From `remotion/`, run:

    npm run typecheck

Use the current `remotion/props.json` examples to spot-check that all target data shapes have valid parser outputs. A small one-off Node or TypeScript inspection command is acceptable, but do not add a new package script unless a future milestone explicitly requires it.

Milestone 4 validates the full phase. From the repository root, run:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Then run:

    cd remotion
    npm run typecheck
    npm run still
    cd ..
    .venv/bin/python -m pytest

If `npm run still` fails with the known Chrome Headless Shell download error, record the exact error under `Surprises & Discoveries` and `Outcomes & Retrospective`; do not add Chromium download workarounds, MP4 scripts, or ffmpeg-related behavior.

## Validation and Acceptance

This phase is accepted when:

- `COMPARISON_CARD` scenes render side-by-side comparison content from `visual.data`.
- `TABLE` scenes render table title, columns, and rows from `visual.data`.
- `CHART` scenes render a simple chart from numeric `series[].points[]`.
- `TIMELINE` scenes render milestone events from `visual.data.events`.
- `SHARE_BREAKDOWN` scenes render item labels and numeric shares from `visual.data.items`.
- `AI_VIDEO` and `B_ROLL` remain placeholder wrappers and do not load or generate media.
- Components never crash on missing or malformed `visual.data`; they fall back to `PlaceholderScene`.
- `SceneRenderer.tsx` still dispatches all seven supported normalized visual types.
- `Video.tsx` still uses exported frame timing and section audio behavior from previous phases.
- No Python CLI behavior changes.
- No ffmpeg call, final MP4 assembly, DOCX parsing, AI video generation, B-roll download, external asset management, GUI, or web app behavior is added.
- `npm run typecheck` passes from `remotion/`.
- `.venv/bin/python -m pytest` passes from the repository root after final validation.

Optional still-frame validation is useful but not required in this environment. If `npm run still` succeeds, record the generated artifact path, normally `remotion/out/preview.png`. If it fails due to the known `remotion.media` DNS or Chrome Headless Shell limitation, record the exact error and continue to rely on type-checking and tests.

## Idempotence and Recovery

All component changes should be deterministic and safe to rerun. The Remotion app reads `remotion/props.json`; it does not mutate props or generated assets. The Python commands listed above can regenerate `timeline.json`, `remotion/props.json`, and `remotion/public/audio/` when needed.

If a component renders poorly because a parser is too strict, loosen the parser narrowly and record the reason in `Decision Log`. If a component crashes on malformed data, treat it as a bug in the component and fix it by adding a guard or fallback. If a Remotion preview command fails due to environment limitations, do not change application code unless the error points to a real TypeScript or React bug.

Generated artifacts should be handled as follows:

- `timeline.json` is generated and should not be committed unless a later instruction changes artifact policy.
- `remotion/props.json` is sample Remotion props and may be committed when intentionally updated for the Remotion project.
- `remotion/public/audio/*.mp3` are generated copied media files and should not be committed.
- `remotion/out/preview.png`, if produced by `npm run still`, is a generated preview and should not be committed unless explicitly requested.
- `remotion/node_modules/` should not be committed.

## Artifacts and Notes

The current props inspection found these representative data examples:

    COMPARISON_CARD scene_009:
      headline: Business Models
      left.label: Traditional model (Intel, 1987)
      right.label: Morris Chang's idea
      footer: Vertical Integration vs. Pure-play Foundry

    TABLE scene_007:
      title: Core mechanisms this video unpacks
      columns: Mechanism, Description
      rows: 4

    CHART scene_012:
      title: Global Foundry Revenue ($B)
      chart_type: line
      first series: TSMC Revenue
      numeric points: 2010=13.3, 2015=26.9, 2020=47.8, 2022=75.9, 2024E=93

    TIMELINE scene_011:
      title: TSMC's rise
      events: 7

    SHARE_BREAKDOWN scene_019:
      title: TSMC's Top Customer Concentration 2024
      unit: %
      items: Apple=25, NVIDIA=11, AMD=8, Qualcomm=7, Broadcom=6, MediaTek=6, All Others=37

The current known still-render limitation from previous phases is:

    Error: getaddrinfo EAI_AGAIN remotion.media

If the same limitation appears again during this phase, record it as an environment limitation rather than a component failure.

## Interfaces and Dependencies

Do not add new runtime dependencies for this phase unless implementation proves a clear need and the decision is recorded. Prefer React, Remotion, TypeScript, inline styles, and simple SVG.

The current `JsonValue` type in `remotion/src/types.ts` is:

    export type JsonValue =
      | string
      | number
      | boolean
      | null
      | JsonValue[]
      | {[key: string]: JsonValue};

The helper parsers should accept `JsonValue` and return parsed data or null. Suggested interfaces:

    export interface ComparisonData {
      headline: string | null;
      left: {label: string; value: string};
      right: {label: string; value: string};
      footer: string | null;
    }

    export interface TableData {
      title: string | null;
      columns: string[];
      rows: string[][];
    }

    export interface ChartPoint {
      x: string;
      y: number;
    }

    export interface ChartSeries {
      name: string | null;
      points: ChartPoint[];
    }

    export interface ChartData {
      title: string | null;
      chartType: string | null;
      xLabel: string | null;
      yLabel: string | null;
      series: ChartSeries[];
      annotations: string[];
    }

    export interface TimelineData {
      title: string | null;
      events: {date: string; label: string}[];
    }

    export interface ShareBreakdownData {
      title: string | null;
      unit: string | null;
      items: {label: string; value: number}[];
    }

The scene component props should remain compatible with the current wrappers:

    {
      scene: SyncCutScene;
      section?: SyncCutSection;
    }

Revision note: Initial plan created on 2026-05-11 by Codex after reading the required project docs and previous phase plans, inspecting the current Remotion source files, checking the current `remotion/props.json` visual data shapes, and applying the local Remotion best-practices guidance. The plan keeps this phase Remotion-only, adds safe JSON parsing helpers, replaces five visual placeholders with basic data-driven components, and leaves AI video and B-roll as metadata placeholders.
