# Prepare Remotion audio assets

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

SyncCut can build `timeline.json`, validate it, export `remotion/props.json`, and preview placeholder scenes in a Remotion project. The missing piece is audio asset preparation: the exported props still point at original section audio files such as `examples/audio/01_HOOK.mp3`, but Remotion expects local static assets to live under the Remotion project `public/` directory so they can be referenced with `staticFile()`.

After this change, a user can run `synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public`, which copies every referenced section audio file into `remotion/public/audio/` and updates `remotion/props.json` with Remotion-safe `public_path` values such as `audio/01_HOOK.mp3`. Then `npm run studio` from `remotion/` can mount one section audio track per section using Remotion's frame timing. This phase does not call ffmpeg directly, assemble a final MP4, parse DOCX, generate AI video, download B-roll, add GUI or web app behavior, or change existing `build-timeline`, `validate-timeline`, `inspect`, or `export-remotion` behavior.

## Progress

- [x] (2026-05-11T00:00:00Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, `docs/plans/validate-and-inspect-timeline.md`, `docs/plans/export-remotion-props.md`, and `docs/plans/remotion-project-skeleton.md`.
- [x] (2026-05-11T00:00:00Z) Inspected the current repository structure, Python exporter, CLI, Remotion `Video.tsx`, Remotion types, and generated `remotion/props.json` audio shape.
- [x] (2026-05-11T00:00:00Z) Checked Remotion audio and static asset conventions with the Remotion best-practices skill and Context7 documentation.
- [x] (2026-05-11T00:00:00Z) Created this ExecPlan for Remotion audio asset preparation.
- [x] (2026-05-11T06:24:24Z) Implemented Milestone 1: added pure Python audio asset preparation helpers in `synccut/remotion_assets.py` and focused tests in `tests/test_remotion_assets.py`.
- [x] (2026-05-11T06:28:47Z) Implemented Milestone 2: wired the `prepare-remotion-assets` CLI command and added focused CLI tests for success and expected failures.
- [x] (2026-05-11T06:38:02Z) Implemented Milestone 3: updated the Remotion app to type and mount section audio from prepared public paths.
- [x] (2026-05-11T06:46:25Z) Completed Milestone 4: validated the full audio asset workflow with fresh generated example data and documented results.

## Surprises & Discoveries

- Observation: Current Remotion props already include deduplicated section audio references, but only as original source paths.
  Evidence: `remotion/props.json` contains `assets.audio` entries such as `{"section_key": "01_HOOK", "path": "examples/audio/01_HOOK.mp3"}` and `sections[].audio` entries such as `{"path": "examples/audio/01_HOOK.mp3"}`. No `public_path` field exists yet.
- Observation: The Remotion app currently shows audio paths as metadata only and does not mount audio.
  Evidence: `remotion/src/Video.tsx` imports only `AbsoluteFill` and `Sequence` from `remotion`, and `PlaceholderScene.tsx` displays `scene.audio.path` as `Audio Metadata`. There is no `<Audio>` component and no `staticFile()` call.
- Observation: The current Remotion package has `remotion` and `@remotion/cli` installed but does not have `@remotion/media`.
  Evidence: `remotion/package.json` lists `react`, `react-dom`, `remotion`, and dev dependencies including `@remotion/cli`, but not `@remotion/media`.
- Observation: Remotion static assets are referenced relative to the Remotion project `public/` directory.
  Evidence: Remotion documentation shows `staticFile("audio/music.mp3")` for `public/audio/music.mp3`; it also documents `<Audio src={staticFile("audio.mp3")} />` and timed audio either with `<Audio from={...} durationInFrames={...} />` or by wrapping audio in a `<Sequence>`.
- Observation: Milestone 1 did not require changes to existing exporter or CLI behavior.
  Evidence: `synccut/remotion_assets.py` is additive, `synccut/cli.py` was not edited, and `.venv/bin/python -m pytest` collected 111 tests with all passing.
- Observation: CLI wiring reused the Milestone 1 file helper without needing new asset logic in `synccut/cli.py`.
  Evidence: `prepare-remotion-assets` delegates to `prepare_remotion_assets_file`, prints only result fields, and `.venv/bin/python -m pytest` collected 114 tests with all passing.
- Observation: The installed Remotion package exports a typed `Audio` component from `remotion`.
  Evidence: A local Node check reported `{"Audio":true,"Html5Audio":true,"staticFile":true}`, and `node_modules/remotion/dist/cjs/index.d.ts` exports `Audio`. Milestone 3 did not need a new `@remotion/media` dependency.
- Observation: Still rendering remains blocked by the environment's inability to download Chrome Headless Shell.
  Evidence: `npm run still` attempted to download `https://remotion.media/chromium-headless-shell-linux-x64-149.0.7790.0.zip?clear` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`.

## Decision Log

- Decision: Add a new command named `prepare-remotion-assets` instead of changing `export-remotion`.
  Rationale: `export-remotion` is already complete and data-only. A separate command keeps existing behavior backward-compatible, makes the file-copying side effect explicit, and gives users a clear two-step workflow: export props, then prepare local Remotion assets.
  Date/Author: 2026-05-11 / Codex
- Decision: Make `prepare-remotion-assets` overwrite the input props file in place by default.
  Rationale: `remotion/src/props.ts` imports `../props.json`, so writing `props.with-assets.json` would require either changing the Remotion import target or passing custom props at runtime. In-place update is the simplest workflow: after export, run one command and Studio reads the same `remotion/props.json`.
  Date/Author: 2026-05-11 / Codex
- Decision: Preserve original audio paths and add `public_path` fields.
  Rationale: The original `path` remains useful for traceability and idempotent recopying. The new `public_path` is the Remotion-safe path passed to `staticFile()`, for example `audio/01_HOOK.mp3`.
  Date/Author: 2026-05-11 / Codex
- Decision: Copy files into `remotion/public/audio/`.
  Rationale: Remotion's `staticFile()` resolves paths from the project `public/` directory. Keeping audio under `public/audio/` is conventional, deterministic, and easy to inspect.
  Date/Author: 2026-05-11 / Codex
- Decision: Mount one audio track per section, not one per scene.
  Rationale: The source audio files are section narration files and section timings already exist in props. One track per section avoids duplicated playback and aligns naturally with `section.start_frame`.
  Date/Author: 2026-05-11 / Codex
- Decision: Do not inspect, decode, trim, or transcode audio.
  Rationale: The project rules forbid ffmpeg unless explicitly requested, and the timeline already treats alignment duration as source of truth. This phase only makes existing files available to Remotion.
  Date/Author: 2026-05-11 / Codex
- Decision: Deep-copy props before adding `public_path` fields in the helper.
  Rationale: Returning an updated props dictionary without mutating the caller's object keeps the function easier to test and avoids accidental side effects in future CLI or library use. The file-oriented helper still writes the updated dictionary back to `props_path`.
  Date/Author: 2026-05-11 / Codex
- Decision: Count identical duplicate entries as a single copy operation, not as reused files.
  Rationale: Duplicate entries that map to the same source and destination should not perform or count a second filesystem operation. The result still reports both logical prepared audio entries in `audio_assets`.
  Date/Author: 2026-05-11 / Codex
- Decision: Import `Audio` from `remotion` for Milestone 3 instead of adding `@remotion/media`.
  Rationale: The installed Remotion version already exposes a typed `Audio` component from the base package, so adding another package would be unnecessary churn. The implementation still uses `staticFile(section.audio.public_path)` and section-level `Sequence` timing.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. The repository now has `synccut/remotion_assets.py` with `PreparedAudioAsset`, `RemotionAssetPrepareResult`, `load_remotion_props`, `prepare_remotion_audio_assets`, and `prepare_remotion_assets_file`. The helper validates `assets.audio`, resolves relative source paths from the current working directory, requires existing suffixed source files, creates `<out-dir>/audio`, copies with `shutil.copy2`, reports copied/reused/overwritten counts, detects destination collisions, preserves original `path` fields, and adds `public_path` to `assets.audio`, matching `sections[].audio`, and matching `scenes[].audio`.

Milestone 1 verification passed. `tests/test_remotion_assets.py` covers valid copy behavior, public path updates, consistent updates across assets/sections/scenes, idempotent reuse, overwrite behavior, missing source errors, malformed props errors, destination collision errors, duplicate entries, and deterministic file writing. The full suite passed with `.venv/bin/python -m pytest`, collecting 111 tests and passing all 111. No CLI command, Remotion TypeScript file, ffmpeg behavior, audio decoding/transcoding, final MP4 assembly, DOCX parsing, AI video generation, B-roll downloading, GUI, or web app behavior was added.

Milestone 2 is complete. `synccut/cli.py` now exposes `synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public`. The command is thin: it calls `prepare_remotion_assets_file`, catches `SyncCutError`, prints `Error: ...` without tracebacks for expected failures, and prints a stable success summary with copied, reused, overwritten, audio asset count, and public directory fields.

Milestone 2 verification passed. `tests/test_cli.py` now covers successful asset preparation from tiny props and byte audio files, confirms the copied file exists under `public/audio`, confirms `public_path` fields are written to assets, sections, and scenes, checks stable CLI output, and verifies malformed props and missing source audio fail with `Error:` and no traceback. The full suite passed with `.venv/bin/python -m pytest`, collecting 114 tests and passing all 114. Existing `build-timeline`, `validate-timeline`, `inspect`, and `export-remotion` tests continued to pass. No Remotion TypeScript file, `@remotion/media` dependency, audio playback, ffmpeg behavior, audio decoding/transcoding, final MP4 assembly, DOCX parsing, AI video generation, B-roll downloading, GUI, or web app behavior was added.

Milestone 3 is complete. `remotion/src/types.ts` now treats `public_path` as optional on section and scene audio refs, and also on `assets.audio` entries. `remotion/src/components/SectionAudio.tsx` mounts one Remotion `<Audio>` track per section only when `section.audio.public_path` exists, wraps each track in a `Sequence` from `section.start_frame` with `durationInFrames={section.duration_frames}` and `layout="none"`, and passes only `staticFile(publicPath)` to the audio source. `remotion/src/Video.tsx` includes `SectionAudio` once at the composition level. The implementation does not use scene audio timing, original source paths with `staticFile()`, fades, volume automation, media probing, trimming, decoding, transcoding, MP4 rendering, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, real chart/table rendering, GUI, or web app behavior.

Milestone 3 verification passed. `npm run typecheck` from `remotion/` completed successfully, and `.venv/bin/python -m pytest` from the repository root collected 114 tests and passed all 114. No Python source files were edited for this milestone, and no package dependency change was needed because the installed `remotion` package exports `Audio`.

Milestone 4 is complete. Fresh example data was generated with `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json`, which completed successfully and wrote `timeline.json`. `.venv/bin/synccut validate-timeline timeline.json` reported `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, `warnings: 1`, and the known warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`. `.venv/bin/synccut export-remotion timeline.json --out remotion/props.json` reported `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 1`.

Audio asset preparation was validated against the fresh props. `.venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` reported `audio_copied: 7`, `audio_reused: 0`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`. The copied audio files were:

    remotion/public/audio/01_HOOK.mp3
    remotion/public/audio/02_INTRO.mp3
    remotion/public/audio/03_MECHANISM_1.mp3
    remotion/public/audio/04_MECHANISM_2.mp3
    remotion/public/audio/05_MECHANISM_3.mp3
    remotion/public/audio/06_MECHANISM_4.mp3
    remotion/public/audio/07_CONCLUSION.mp3

Prepared props inspection passed. `remotion/props.json` parsed successfully and was pretty-printed to `/tmp/synccut_props_pretty.json`. The inspection script reported `audio_assets: 7`, `sections: 7`, `scenes: 33`, first audio asset `{'section_key': '01_HOOK', 'path': 'examples/audio/01_HOOK.mp3', 'public_path': 'audio/01_HOOK.mp3'}`, first section audio `{'path': 'examples/audio/01_HOOK.mp3', 'public_path': 'audio/01_HOOK.mp3'}`, first scene audio `{'path': 'examples/audio/01_HOOK.mp3', 'public_path': 'audio/01_HOOK.mp3'}`, and `missing_public_paths: []`.

Final phase validation passed except for the known still-render environment limitation. `npm run typecheck` from `remotion/` completed successfully. `npm run still` did not render `out/preview.png` because Remotion tried to download Chrome Headless Shell from `remotion.media` and failed with `Error: getaddrinfo EAI_AGAIN remotion.media`; no workaround code was added. `.venv/bin/python -m pytest` from the repository root collected 114 tests and passed all 114. This phase now has a complete deterministic workflow from exported props to copied public audio assets to a Remotion app that can mount section audio when the environment can run Remotion preview/rendering.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ Typer CLI package with a separate Remotion project under `remotion/`.

The existing Python commands are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

The current Python source files relevant to this phase are:

    synccut/cli.py
    synccut/remotion_exporter.py
    synccut/timeline_validator.py
    synccut/validators.py

The current Remotion source files relevant to this phase are:

    remotion/package.json
    remotion/src/Video.tsx
    remotion/src/types.ts
    remotion/src/props.ts

The current generated Remotion props file is `remotion/props.json`. It is imported by `remotion/src/props.ts`, which exports `defaultProps`. `Root.tsx` registers one composition using `defaultProps.composition`, and `Video.tsx` renders placeholder scenes from `defaultProps.scenes`.

Important terms used in this plan:

An original audio path is the path currently exported from the timeline, such as `examples/audio/01_HOOK.mp3`. This path is meaningful to the Python CLI because it points to the file discovered during timeline construction.

A Remotion public path is a path relative to `remotion/public/`, such as `audio/01_HOOK.mp3`. This is the string passed to Remotion `staticFile()`.

The public directory is the Remotion project's static asset directory. A file at `remotion/public/audio/01_HOOK.mp3` is referenced in React as `staticFile("audio/01_HOOK.mp3")`.

## Current Props Audio Shape

The current `synccut export-remotion` output has audio data in three places:

    {
      "sections": [
        {
          "section_key": "01_HOOK",
          "start_frame": 0,
          "duration_frames": 552,
          "audio": {"path": "examples/audio/01_HOOK.mp3"}
        }
      ],
      "scenes": [
        {
          "id": "scene_001",
          "section_key": "01_HOOK",
          "audio": {"path": "examples/audio/01_HOOK.mp3"}
        }
      ],
      "assets": {
        "audio": [
          {"section_key": "01_HOOK", "path": "examples/audio/01_HOOK.mp3"}
        ],
        "visuals": []
      }
    }

The `path` fields are source paths. They are not safe to pass directly to `staticFile()` because they are not relative to `remotion/public/`.

## Proposed Props Audio Shape

After running the new preparation command, the same props file should keep original paths and add Remotion public paths:

    {
      "sections": [
        {
          "section_key": "01_HOOK",
          "start_frame": 0,
          "duration_frames": 552,
          "audio": {
            "path": "examples/audio/01_HOOK.mp3",
            "public_path": "audio/01_HOOK.mp3"
          }
        }
      ],
      "scenes": [
        {
          "id": "scene_001",
          "section_key": "01_HOOK",
          "audio": {
            "path": "examples/audio/01_HOOK.mp3",
            "public_path": "audio/01_HOOK.mp3"
          }
        }
      ],
      "assets": {
        "audio": [
          {
            "section_key": "01_HOOK",
            "path": "examples/audio/01_HOOK.mp3",
            "public_path": "audio/01_HOOK.mp3"
          }
        ],
        "visuals": []
      }
    }

Updating all three locations keeps the props easy to inspect and avoids future confusion when scene placeholders display audio metadata. The Remotion audio mounting implementation should use `sections[].audio.public_path`, because there should be exactly one audio track per section.

## Remotion Public Asset Requirements

The implementation should create this directory when missing:

    remotion/public/audio/

Files copied there are referenced with `staticFile()` using the path relative to `remotion/public/`:

    staticFile("audio/01_HOOK.mp3")

The Remotion app should not attempt to read files directly from `examples/audio/` at runtime. Browser-based preview and rendering need paths that Remotion can serve from the project public directory.

## Command Shape

Add this public command:

    synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

The command should:

- read `remotion/props.json`
- validate enough structure to ensure it is Remotion props, not arbitrary JSON
- find `assets.audio` entries
- copy each source audio file into `<out-dir>/audio/`
- add or update `public_path` fields in `assets.audio`, `sections[].audio`, and `scenes[].audio`
- overwrite the input props file with deterministic two-space JSON and a trailing newline
- print a concise summary

Example success output:

    Prepared Remotion assets for remotion/props.json
    audio_copied: 7
    audio_reused: 0
    public_dir: remotion/public

Keep the existing `export-remotion` command unchanged. Users who want clean base props can rerun export. Users who want assets ready for Studio can run `prepare-remotion-assets`.

Do not add an `--out` props option in the first implementation. In-place update is sufficient and keeps `remotion/src/props.ts` stable. A future phase can add `--props-out` if there is a real need for parallel base and prepared props files.

## Audio Path Mapping

For each `assets.audio[]` entry, read:

    section_key = entry["section_key"]
    source_path = Path(entry["path"])

Resolve `source_path` relative to the current working directory if it is not absolute. Because existing SyncCut commands are run from the repository root, `examples/audio/01_HOOK.mp3` resolves correctly from the root.

Generate the destination filename from the section key and original extension:

    destination_filename = "<section_key><original_suffix>"
    destination_path = out_dir / "audio" / destination_filename
    public_path = "audio/<destination_filename>"

For the current example data:

    examples/audio/01_HOOK.mp3 -> remotion/public/audio/01_HOOK.mp3 -> audio/01_HOOK.mp3
    examples/audio/02_INTRO.mp3 -> remotion/public/audio/02_INTRO.mp3 -> audio/02_INTRO.mp3

Using `section_key` in the destination filename gives deterministic names and avoids most collisions even if two source files share the same basename.

## Idempotent Copy Behavior

The command must be safe to run repeatedly. It should create `remotion/public/audio/` if missing. It should copy with standard-library file operations such as `shutil.copy2`, preserving metadata when practical, and it should not decode or transform audio.

If the destination file does not exist, copy it and count it as copied.

If the destination file already exists and its bytes are identical to the source, leave it in place and count it as reused.

If the destination file already exists but bytes differ, overwrite it with the source and count it as copied. This makes reruns deterministic when a source audio file changes. Record this overwrite behavior in the command summary if practical, for example by counting `audio_overwritten`.

Do not delete extra files in `remotion/public/audio/`. Cleanup of stale assets is a separate asset-management problem and is out of scope.

## Collision Handling

The primary destination filename is `<section_key><suffix>`, for example `01_HOOK.mp3`. Section keys should be unique in valid props.

The command must detect if two distinct source audio entries map to the same destination filename. If they have the same source path, treat them as a duplicate reference and reuse one copied file. If they have different source paths, fail with `SyncCutError` and a clear message such as:

    audio destination collision for audio/01_HOOK.mp3: examples/audio/01_HOOK.mp3 and other/01_HOOK.wav

Do not silently append counters or random strings. Deterministic failure is safer than creating surprising asset paths.

If a source file has no suffix, use the original basename after sanitizing only if necessary, but prefer failing with a clear error until a real suffix-less audio case exists. The example and MVP audio files use `.mp3`.

## Python Implementation Plan

Create `synccut/remotion_assets.py`. Keep it independent of Remotion rendering and ffmpeg. Suggested public functions are:

    def load_remotion_props(path: Path) -> dict[str, Any]: ...
    def prepare_remotion_audio_assets(props: dict[str, Any], props_path: Path, out_dir: Path) -> tuple[dict[str, Any], RemotionAssetPrepareResult]: ...
    def prepare_remotion_assets_file(props_path: Path, out_dir: Path) -> RemotionAssetPrepareResult: ...

Suggested result dataclass:

    @dataclass(frozen=True)
    class RemotionAssetPrepareResult:
        props_path: Path
        public_dir: Path
        audio_dir: Path
        copied: int
        reused: int
        overwritten: int
        audio_assets: list[PreparedAudioAsset]

    @dataclass(frozen=True)
    class PreparedAudioAsset:
        section_key: str
        source_path: str
        destination_path: str
        public_path: str

`prepare_remotion_audio_assets` should be mostly pure except for file copying. It receives a props dictionary, copies files, and returns an updated props dictionary plus a result. `prepare_remotion_assets_file` should load JSON, call the helper, and write updated props JSON back to `props_path`.

Add `synccut prepare-remotion-assets` to `synccut/cli.py` as thin orchestration only:

    @app.command("prepare-remotion-assets")
    def prepare_remotion_assets_cmd(
        props_json: Annotated[Path, typer.Argument(help="Path to remotion/props.json.")],
        out_dir: Annotated[Path, typer.Option(help="Remotion public directory.")],
    ) -> None:
        ...

The CLI should catch `SyncCutError`, print `Error: ...`, and exit 1, matching existing command style.

## Remotion Implementation Plan

Update `remotion/package.json` to add `@remotion/media` as a runtime dependency because Remotion documentation recommends `<Audio>` from `@remotion/media`.

Update `remotion/src/types.ts` so `SyncCutAudioRef` has:

    path: string;
    public_path?: string;

Keep `public_path` optional so the Remotion app still type-checks against base props that have not yet been prepared. This preserves the existing `export-remotion` output contract.

Create a small component such as `remotion/src/components/SectionAudio.tsx`:

    import {Audio} from "@remotion/media";
    import {Sequence, staticFile} from "remotion";
    import type {SyncCutSection} from "../types";

    export const SectionAudio = ({sections}: {sections: SyncCutSection[]}) => (
      <>
        {sections
          .filter((section) => section.audio.public_path)
          .map((section) => (
            <Sequence
              key={section.section_key}
              from={section.start_frame}
              durationInFrames={section.duration_frames}
              layout="none"
            >
              <Audio
                src={staticFile(section.audio.public_path as string)}
              />
            </Sequence>
          ))}
      </>
    );

Then update `remotion/src/Video.tsx` to render `<SectionAudio sections={sections} />` inside the root `AbsoluteFill`, before or after the scene sequences. This creates one audio track per section, aligned to `section.start_frame`, and limited to `section.duration_frames`. Do not use scene timing for audio.

Do not use audio fades, volume automation, trimming, waveform display, or media probing in this phase.

## Tests to Write

Add `tests/test_remotion_assets.py` with small synthetic props dictionaries and temporary files. Use tiny byte files with `.mp3` extensions; do not require real audio decoding.

Cover:

- valid audio copy creates `public/audio/<section_key>.mp3`
- output props preserve original `path` and add `public_path`
- `assets.audio`, matching `sections[].audio`, and matching `scenes[].audio` are updated consistently
- rerunning with identical destination reuses the file and remains deterministic
- rerunning with changed source overwrites destination and reports overwrite count
- missing source audio fails clearly
- malformed props missing `assets.audio` fails clearly
- collision with two different sources mapping to the same destination fails clearly
- duplicate entries with same source path do not copy twice
- command writes two-space JSON with trailing newline
- CLI success and failure behavior through Typer test runner, if practical

Update `tests/test_cli.py` only for the new command. Do not change existing CLI command tests unless a clear shared helper extraction is useful.

For Remotion TypeScript validation, `npm run typecheck` is enough for this phase. There is no Jest or browser test setup in the Remotion project.

## Validation Commands

Run all commands from the repository root unless noted:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut

Generate fresh props:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

Prepare audio:

    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Inspect expected files:

    find remotion/public/audio -maxdepth 1 -type f | sort

Expected files for current examples are:

    remotion/public/audio/01_HOOK.mp3
    remotion/public/audio/02_INTRO.mp3
    remotion/public/audio/03_MECHANISM_1.mp3
    remotion/public/audio/04_MECHANISM_2.mp3
    remotion/public/audio/05_MECHANISM_3.mp3
    remotion/public/audio/06_MECHANISM_4.mp3
    remotion/public/audio/07_CONCLUSION.mp3

Inspect props:

    .venv/bin/python -m json.tool remotion/props.json >/tmp/synccut_props_pretty.json

Run Python tests:

    .venv/bin/python -m pytest

Run Remotion type-check:

    cd remotion
    npm install
    npm run typecheck

If environment permits, run a still-frame check:

    npm run still

The current environment previously failed still rendering because Chrome Headless Shell download could not resolve `remotion.media`. If that happens again, record the exact error and rely on `npm run typecheck` plus file and props inspection.

## Milestones

Milestone 1 creates Python asset-preparation helpers. This milestone is complete: `synccut/remotion_assets.py` can load Remotion props, copy audio files into a temporary public directory, update a props dictionary with `public_path` fields, and return structured copy counts. Unit tests prove copying, idempotency, overwrite behavior, missing file errors, malformed props errors, collision errors, duplicate entry behavior, and deterministic JSON writing.

Milestone 2 wires the CLI. This milestone is complete: `synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` exists, keeps CLI logic thin, formats expected errors without tracebacks, writes prepared props back to the same file, and has CLI tests for success and failure. Existing `build-timeline`, `validate-timeline`, `inspect`, and `export-remotion` tests still pass.

Milestone 3 updates the Remotion app. This milestone is complete: `SyncCutAudioRef.public_path` is typed as optional, `SectionAudio.tsx` mounts one audio track per prepared section using `Sequence` and `staticFile(section.audio.public_path)`, and `Video.tsx` includes `SectionAudio`. No `@remotion/media` dependency was added because the installed `remotion` package exports `Audio`. `npm run typecheck` passes with base props that do not yet have `public_path` because the field is optional.

Milestone 4 validates with real generated data. This milestone is complete: fresh example props were exported, seven audio assets were copied into `remotion/public/audio/`, props contain matching `public_path` fields across `assets.audio`, `sections[].audio`, and `scenes[].audio`, Python tests pass, Remotion type-check passes, and the still-render Chrome Headless Shell download limitation is recorded.

## Validation and Acceptance

This phase is accepted when all of the following are true:

- `synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public` exists.
- The command reads existing Remotion props and does not require `timeline.json`.
- The command creates `remotion/public/audio/` if missing.
- The command copies all referenced section audio assets from `assets.audio`.
- Prepared props preserve original `path` and add `public_path`.
- `public_path` values are relative to `remotion/public/`, for example `audio/01_HOOK.mp3`.
- `assets.audio`, `sections[].audio`, and `scenes[].audio` are updated consistently.
- Running the command repeatedly is safe and deterministic.
- Duplicate source references are handled without duplicate copies.
- Destination collisions from distinct source files fail clearly.
- Missing audio files fail clearly.
- Existing `export-remotion` behavior remains backward-compatible and data-only.
- Remotion mounts one audio track per section using section `start_frame` and `duration_frames`.
- Remotion uses `staticFile(public_path)` rather than source paths.
- No direct ffmpeg command is called.
- No final MP4 is assembled.
- No DOCX parsing, AI video generation, B-roll downloading, real chart/table rendering, GUI, or web app behavior is added.
- `.venv/bin/python -m pytest` passes.
- `npm run typecheck` passes from `remotion/`.

## Idempotence and Recovery

The new command is intentionally idempotent. Running it multiple times should not change props except for stable JSON formatting and should not recopy identical files unnecessarily. If a destination file differs from the current source file, overwrite it deterministically.

If the user wants to return to base props without `public_path` fields, rerun:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

If prepared assets become stale, rerun:

    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

Do not delete or clean `remotion/public/audio/` automatically. Stale asset cleanup is out of scope. Do not use destructive git commands. Do not run `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, or `git rebase` unless the user explicitly asks.

## Explicit Exclusions

This phase must not:

- call ffmpeg directly
- inspect, decode, trim, normalize, or transcode audio
- assemble a final MP4
- parse DOCX
- generate AI video
- download B-roll or other external visual assets
- implement real charts, tables, comparison cards, share breakdowns, or timeline graphics
- add GUI or web app behavior
- add a Python command that invokes Remotion rendering
- change existing `build-timeline`, `validate-timeline`, `inspect`, or `export-remotion` behavior except for clearly documented backward-compatible shared helper changes
- delete stale assets from `remotion/public/audio/`
- add non-deterministic file names

## Artifacts and Notes

The current generated `remotion/props.json` has seven audio assets for the real examples:

    examples/audio/01_HOOK.mp3
    examples/audio/02_INTRO.mp3
    examples/audio/03_MECHANISM_1.mp3
    examples/audio/04_MECHANISM_2.mp3
    examples/audio/05_MECHANISM_3.mp3
    examples/audio/06_MECHANISM_4.mp3
    examples/audio/07_CONCLUSION.mp3

After implementation, these should appear under:

    remotion/public/audio/01_HOOK.mp3
    remotion/public/audio/02_INTRO.mp3
    remotion/public/audio/03_MECHANISM_1.mp3
    remotion/public/audio/04_MECHANISM_2.mp3
    remotion/public/audio/05_MECHANISM_3.mp3
    remotion/public/audio/06_MECHANISM_4.mp3
    remotion/public/audio/07_CONCLUSION.mp3

The Remotion app should import:

    import {Audio} from "@remotion/media";
    import {Sequence, staticFile} from "remotion";

The intended mounting shape is:

    <Sequence from={section.start_frame} durationInFrames={section.duration_frames} layout="none">
      <Audio src={staticFile(section.audio.public_path)} />
    </Sequence>

Use `layout="none"` because audio has no visual layout and should not affect the absolute scene fills.

Revision note: Initial plan created on 2026-05-11 by Codex after reading required project docs, previous phase plans, current Python and Remotion source, generated props, the Remotion best-practices skill, and Context7 Remotion documentation. The plan chooses a separate `prepare-remotion-assets` command that copies section audio into `remotion/public/audio/`, updates props in place with `public_path` fields, and mounts one Remotion audio track per section.

Revision note: Milestone 1 implemented on 2026-05-11 by Codex. The update records the additive Python helper module, focused test coverage, copy/counting behavior, full pytest result, and the fact that CLI and Remotion TypeScript integration remain for later milestones.

Revision note: Milestone 2 implemented on 2026-05-11 by Codex. The update records the thin CLI command, stable success summary, expected failure behavior, CLI test coverage, full pytest result, and the fact that Remotion TypeScript audio mounting remains for a later milestone.
