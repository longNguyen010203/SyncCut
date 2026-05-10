# Export Remotion props from timeline.json

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement this phase from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can already build and validate `timeline.json`. The next useful capability is to transform that validated timeline into a JSON props file that a separate Remotion project can consume later. After this phase, a user can run `synccut export-remotion timeline.json --out remotion/props.json` and receive a deterministic `props.json` containing composition metadata, frame-based scene timing, preserved dialogue, preserved visual instructions, audio references, alignment match metadata, and warnings.

This phase only exports data. It must not render video, call Remotion, call ffmpeg, parse DOCX, generate AI video, download B-roll, assemble video, add a GUI, add a web app, or add new rendering configuration options. The existing `build-timeline`, `validate-timeline`, and `inspect` behavior must remain unchanged unless a clear bug is discovered.

## Progress

- [x] (2026-05-10T16:43:00Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, `docs/future-phases.md`, `docs/plans/build-timeline-mvp.md`, and `docs/plans/validate-and-inspect-timeline.md`.
- [x] (2026-05-10T16:43:00Z) Inspected the current repository structure and confirmed the existing build, validation, and inspection modules are present.
- [x] (2026-05-10T16:43:00Z) Created this ExecPlan for `synccut export-remotion`.
- [x] (2026-05-10T16:58:02Z) Implemented pure Remotion props export helpers in `synccut/remotion_exporter.py`.
- [x] (2026-05-11T00:17:35Z) Added focused pure exporter tests in `tests/test_remotion_exporter.py`.
- [x] (2026-05-11T00:28:44Z) Wired `synccut export-remotion` into the Typer CLI while keeping CLI logic thin.
- [x] (2026-05-11T00:28:44Z) Added CLI tests for export success and expected validation failure.
- [x] (2026-05-11T00:40:18Z) Ran full validation commands and real example export to `remotion/props.json`.

## Surprises & Discoveries

- Observation: `timeline.json` is present in the repository root as a generated artifact.
  Evidence: `rg --files -g '!**/__pycache__/**' | sort` listed `timeline.json`, and `git status --short` showed it as untracked. This file can be used for local inspection but should not be treated as source or committed.
- Observation: The validation and inspection phase is already implemented as reusable pure modules plus thin CLI commands.
  Evidence: `synccut/timeline_validator.py` exposes `load_timeline_json`, `validate_timeline`, and `validate_timeline_file`; `synccut/timeline_inspector.py` exposes `build_timeline_overview`; `synccut/cli.py` only orchestrates loading, formatting, writing, and user-facing errors.
- Observation: The project already has a console script entry point.
  Evidence: `pyproject.toml` contains `synccut = "synccut.cli:app"`.
- Observation: The pure exporter can transform the existing generated example timeline without invoking the future CLI.
  Evidence: A direct `build_remotion_props` smoke check printed `duration_frames: 22584`, `scenes: 33`, `sections: 7`, `audio_assets: 7`, and `warnings: 1`.
- Observation: Focused Milestone 2 tests did not reveal any required exporter behavior changes.
  Evidence: `.venv/bin/python -m pytest` collected 99 tests and all passed after adding `tests/test_remotion_exporter.py`.
- Observation: CLI wiring did not require changing existing command behavior.
  Evidence: `.venv/bin/python -m pytest` collected 101 tests and all passed after adding `export-remotion` tests; existing `build-timeline`, `validate-timeline`, and `inspect` tests still passed.
- Observation: The real generated Remotion props output matches the expected frame and count values.
  Evidence: Inspecting `remotion/props.json` printed `total_scenes: 33`, `total_sections: 7`, `duration_sec: 752.79`, `duration_frames: 22584`, `scene_entries: 33`, `audio_assets: 7`, and the known `07_CONCLUSION` gap warning.

## Decision Log

- Decision: Use a fixed FPS of 30 for this phase.
  Rationale: The user requested `fps=30` by default and asked not to add CLI options for FPS, width, or height unless strongly justified. A fixed value keeps this phase small and deterministic.
  Date/Author: 2026-05-10 / Codex
- Decision: Use a fixed composition size of 1920 by 1080 for this phase.
  Rationale: The suggested output shape includes width 1920 and height 1080. This is enough for a Remotion project to start rendering later without introducing configuration surface now.
  Date/Author: 2026-05-10 / Codex
- Decision: Convert seconds to frames with nearest-frame rounding using `floor(seconds * fps + 0.5)`.
  Rationale: This produces the suggested examples: `752.79 * 30 = 22583.7` becomes `22584`, and `9.137 * 30 = 274.11` becomes `274`. It avoids Python's banker-rounding edge cases and keeps output deterministic.
  Date/Author: 2026-05-10 / Codex
- Decision: Preserve visual payloads rather than interpreting or rendering them.
  Rationale: This phase exports props only. Remotion rendering, AI video generation, and B-roll downloading remain future work. The exporter should preserve enough information for a future Remotion app to decide how to render each visual type.
  Date/Author: 2026-05-10 / Codex
- Decision: Validate the input timeline before exporting props.
  Rationale: The previous phase already centralizes timeline structure and timing validation. Reusing it prevents the exporter from producing props from a malformed or overlapping timeline.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep output-file writing in `export_remotion_props_file` and all mapping rules in `build_remotion_props`.
  Rationale: `build_remotion_props` can now be tested as a pure function in Milestone 2, while the file helper gives the future CLI one thin call for loading, exporting, creating the output directory, and writing JSON.
  Date/Author: 2026-05-10 / Codex
- Decision: Deduplicate exported warnings and audio assets while preserving first-seen deterministic order.
  Rationale: The plan asks to merge timeline warnings and validation warnings without duplicates, and to include one audio asset per unique section audio path. Preserving first-seen order after sorting sections keeps the output stable.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep `export-remotion` CLI output as a summary of the returned props dictionary.
  Rationale: `export_remotion_props_file` already owns loading, validation, mapping, directory creation, and JSON writing. The CLI should only call it, print stable metadata fields, and format expected `SyncCutError` failures.
  Date/Author: 2026-05-11 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. The repository now has `synccut/remotion_exporter.py` with fixed composition constants, `seconds_to_frame`, pure `build_remotion_props`, and file-oriented `export_remotion_props_file`. The exporter validates timeline input, preserves scene dialogue, visual, audio, alignment, and warnings, converts seconds to frames with `floor(seconds * fps + 0.5)`, sorts sections and scenes deterministically, builds deduplicated audio assets, keeps `assets.visuals` empty, and raises `SyncCutError` for validation failures or non-positive frame durations.

Verification for Milestone 1 passed with `.venv/bin/python -m pytest`, which collected 75 tests and all passed. A direct smoke check against the generated example `timeline.json` produced 22584 duration frames, 33 scenes, 7 sections, 7 audio assets, and 1 warning. No CLI command, Remotion rendering, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, web app, or new options were added.

Milestone 2 is complete. The repository now has `tests/test_remotion_exporter.py` covering `seconds_to_frame`, metadata and composition output, section mapping, scene mapping, all supported visual types, audio asset deduplication and sorting, empty visual assets, warning merging and deduplication, deterministic ordering, invalid timeline failures, positive-duration scene and section zero-frame failures, file export writing, and input immutability. No exporter behavior changes were needed while adding these tests.

Verification for Milestone 2 passed with `.venv/bin/python -m pytest`, which collected 99 tests and all passed. No CLI command, Remotion rendering, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, web app, or new options were added.

Milestone 3 is complete. `synccut/cli.py` now exposes `synccut export-remotion timeline.json --out remotion/props.json`. The command delegates to `export_remotion_props_file`, prints a stable summary containing output path, scene count, section count, FPS, duration frames, and warning count, and formats expected `SyncCutError` failures as `Error: ...` without tracebacks. Existing command behavior for `build-timeline`, `validate-timeline`, and `inspect` was not changed.

Verification for Milestone 3 passed with `.venv/bin/python -m pytest`, which collected 101 tests and all passed. CLI tests now cover successful props export and invalid timeline failure. No Remotion rendering, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, web app, or new options were added.

Milestone 4 is complete. A fresh `timeline.json` was generated from `examples/scenes.json`, `examples/audio`, and `examples/alignments`; the timeline validated successfully; `synccut export-remotion timeline.json --out remotion/props.json` wrote the Remotion props file; `json.tool` accepted the generated props JSON; and a key-field inspection confirmed the expected real-example metadata, composition, scene count, section count, frame duration, audio asset count, and known warning.

Final verification for this phase passed with `.venv/bin/python -m pytest`, which collected 101 tests and all passed. The real example export produced 33 scene entries, 7 sections, 7 audio assets, `duration_sec` 752.79, `duration_frames` 22584, first scene `scene_001` from frame 0 to 274, last scene `scene_033` ending at frame 22584, and the known `07_CONCLUSION` gap warning. No Remotion rendering, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, web app, or new options were added.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ Typer CLI package. The package is installed locally through `pyproject.toml`, which exposes the `synccut` command.

The current source files are:

    synccut/__init__.py
    synccut/alignment_loader.py
    synccut/cli.py
    synccut/models.py
    synccut/scenes_loader.py
    synccut/timeline_builder.py
    synccut/timeline_inspector.py
    synccut/timeline_validator.py
    synccut/validators.py

The current tests are:

    tests/test_alignment_loader.py
    tests/test_cli.py
    tests/test_package.py
    tests/test_scenes_loader.py
    tests/test_timeline_builder.py
    tests/test_timeline_inspector.py
    tests/test_timeline_validator.py

The existing public commands are:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json
    synccut validate-timeline timeline.json
    synccut inspect timeline.json

The new public command for this phase is:

    synccut export-remotion timeline.json --out remotion/props.json

A timeline is the validated JSON object produced by `build-timeline`. It contains global scene timing in seconds, section timing in seconds, audio references, alignment references, dialogue, visual metadata, and warnings. Global timing means seconds from the start of the whole video. Local timing means seconds from the start of one section.

Remotion props means a JSON object meant to be passed into a future Remotion composition. Remotion itself is not used in this phase. No Node process, browser, renderer, or Remotion CLI command should run. The exporter only creates `props.json`.

## Expected Input timeline.json Structure

The input file must be a valid timeline JSON object accepted by `synccut.timeline_validator.validate_timeline`. The exporter should load it with `load_timeline_json(path)`, validate it with `validate_timeline(data, path=str(path))`, and fail if validation has errors. Validation warnings should not block export; they should be copied into the output `warnings` array.

The required top-level keys are:

- `metadata`, an object with `total_scenes`, `total_sections`, and `total_duration_sec`.
- `sections`, a non-empty array.
- `timeline`, a non-empty array of scene entries.
- `warnings`, an array of strings.

Each input section must have:

- `section_key`, such as `01_HOOK`.
- `section`, such as `HOOK`.
- `section_order`, an integer.
- `audio_path`, a non-empty string.
- `alignment_path`, a non-empty string.
- `local_duration_sec`, a positive number.
- `global_start_sec`, a number.
- `global_end_sec`, a number greater than or equal to `global_start_sec`.

Each input timeline scene must have:

- `scene_id`.
- `scene_order`.
- `section`, `section_order`, and `section_key`.
- `timing.start_sec`, `timing.end_sec`, `timing.duration_sec`, `timing.local_start_sec`, and `timing.local_end_sec`.
- `audio.path`.
- `alignment.path`, `alignment.match_method`, and `alignment.matched_units`.
- `dialogue.text` and `dialogue.paragraphs`.
- `visual.type`, `visual.prompt`, and `visual.data`.
- `warnings`, an array.

The exporter must not mutate `timeline.json`.

## Expected Remotion Props Output Structure

The output file should be deterministic, human-readable JSON with two-space indentation and a trailing newline. It should be safe to regenerate and overwrite the output path because the command is an export command and no `--force` option is part of this phase.

The output object should have this shape:

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

The exact string values depend on the input timeline. The key names and nesting should be stable. `metadata.total_sections` should be included even though it was not in the user's minimal suggested shape, because the phase needs to summarize section count and it is already present in `timeline.json`.

## Mapping Rules from Timeline Scenes to Remotion Scenes

The exporter should preserve scene order deterministically. Sort input sections by `section_order` and then `section_key`. Sort input scenes by `section_order`, `section_key`, `timing.start_sec`, `scene_order`, and `scene_id`. The validated timeline produced by `build-timeline` is already deterministic, but sorting again makes the exporter stable if a valid file's arrays are shuffled.

For every input timeline scene, create one output `scenes` entry:

- `id` is copied from input `scene_id`.
- `scene_order`, `section`, `section_order`, and `section_key` are copied unchanged.
- `start_sec`, `end_sec`, `duration_sec`, `local_start_sec`, and `local_end_sec` are copied from `timing`.
- `start_frame`, `end_frame`, and `duration_frames` are calculated from seconds using the frame rules below.
- `visual_type` is copied from `visual.type`.
- `visual` is copied as a deep JSON-compatible value so `type`, `prompt`, and `data` are preserved.
- `dialogue` is copied unchanged.
- `audio` is copied unchanged.
- `alignment` is copied unchanged.
- `warnings` is copied unchanged.

The exporter should not add renderer-specific component names unless tests and the plan are updated to require them. This keeps the first props schema focused on source data and timing.

## Handling Visual Types

The exporter should accept only the normalized visual types that the timeline validator already accepts: `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`. It should not normalize `B-ROLL` here; a valid `timeline.json` must already use `B_ROLL`.

For `AI_VIDEO`, preserve the visual object exactly. The output should carry the prompt and data for a future generated-video renderer, but this command must not generate video or check for generated asset files.

For `B_ROLL`, preserve the visual object exactly. The output should carry the prompt and data for a future stock-footage or asset renderer, but this command must not download B-roll or check for downloaded asset files.

For `CHART`, preserve the visual object exactly. Any chart data in `visual.data` is passed through for a future Remotion chart component.

For `COMPARISON_CARD`, preserve the visual object exactly. Any comparison labels, values, or layout data in `visual.data` is passed through for a future card component.

For `TABLE`, preserve the visual object exactly. Any table rows, columns, or formatting data in `visual.data` is passed through for a future table component.

For `SHARE_BREAKDOWN`, preserve the visual object exactly. Any share labels, numeric values, or display settings in `visual.data` is passed through for a future breakdown component.

For `TIMELINE`, preserve the visual object exactly. Any event or milestone data in `visual.data` is passed through for a future timeline component.

The `assets.visuals` array should be empty in this phase. Do not infer visual file paths from prompts or visual data unless a later phase explicitly defines asset management.

## Timing Conversion Rules

The timeline already stores seconds as global timing for scenes and sections. The exporter must not recompute scene timing from dialogue or alignment text. It should use the existing validated timing values.

For sections:

- `start_sec` comes from input `global_start_sec`.
- `end_sec` comes from input `global_end_sec`.
- `duration_sec` comes from input `local_duration_sec`.

For scenes:

- `start_sec` comes from `timing.start_sec`.
- `end_sec` comes from `timing.end_sec`.
- `duration_sec` comes from `timing.duration_sec`.
- `local_start_sec` comes from `timing.local_start_sec`.
- `local_end_sec` comes from `timing.local_end_sec`.

Do not silently invent or repair timing. If the validated data somehow produces non-positive frame durations, raise `SyncCutError` with the scene id or section key and the timing values.

## Frame Calculation Rules

Use `fps = 30`. A frame number is an integer index in the rendered composition timeline.

Convert seconds to frame numbers with nearest-frame rounding:

    frame = floor(seconds * fps + 0.5)

In Python this can be implemented with `math.floor(value * fps + 0.5)`. Reject booleans and non-numeric values before conversion, although the existing validator should already catch them.

For a scene:

    start_frame = frame(start_sec)
    end_frame = frame(end_sec)
    duration_frames = end_frame - start_frame

For a section:

    start_frame = frame(start_sec)
    end_frame = frame(end_sec)
    duration_frames = end_frame - start_frame

For the full composition:

    duration_frames = frame(metadata.total_duration_sec)

Frame durations must be positive. If `end_frame <= start_frame` for any positive-duration scene or section, raise a clear `SyncCutError`. This avoids creating Remotion props with zero-frame scenes.

The real example has `metadata.total_duration_sec` of `752.79`, so the expected composition duration is `22584` frames at 30 FPS.

## FPS Choice

Use `30` FPS as a constant for this entire phase. Name the constant in the export module, for example `DEFAULT_FPS = 30`. Do not add `--fps`, `--width`, or `--height` options in this phase. The fixed composition should be:

    id: SyncCutVideo
    width: 1920
    height: 1080
    fps: 30

If a future phase needs configurable composition settings, it should add options and tests deliberately.

## Error Handling

Known expected failures should raise `SyncCutError` and should be displayed by the CLI as concise `Error: ...` lines without Python tracebacks.

The command should fail clearly when:

- The input file is missing.
- The input file is malformed JSON.
- The input root is not a JSON object.
- The timeline validator reports errors.
- An output parent directory cannot be created or written.
- Frame conversion would create a non-positive scene or section duration.

Validation warnings should not fail export. They should be copied into output `warnings`. If both top-level timeline warnings and validation warnings exist, include both. Do not duplicate warning strings if the same string appears in both sources; preserving order while removing duplicates is acceptable and deterministic.

The CLI should not catch arbitrary unexpected exceptions. It should catch `SyncCutError` to keep user-facing errors clean and let programming errors surface during development.

## Plan of Work

Milestone 1 creates a pure props export module. This milestone is complete: `synccut/remotion_exporter.py` has constants and pure functions. Public functions are:

    DEFAULT_FPS = 30
    DEFAULT_WIDTH = 1920
    DEFAULT_HEIGHT = 1080
    DEFAULT_COMPOSITION_ID = "SyncCutVideo"

    def seconds_to_frame(seconds: float, fps: int = DEFAULT_FPS) -> int: ...
    def build_remotion_props(data: dict, source_timeline_path: Path, fps: int = DEFAULT_FPS) -> dict: ...
    def export_remotion_props_file(timeline_path: Path, out_path: Path) -> dict: ...

`build_remotion_props` is pure: it receives a timeline dictionary and returns a props dictionary without reading or writing files. It calls `validate_timeline` internally. `export_remotion_props_file` does file I/O by loading `timeline_path`, building props, creating `out_path.parent` if needed, writing JSON, and returning the props dictionary for tests or CLI use.

Milestone 2 adds focused exporter tests. This milestone is complete: `tests/test_remotion_exporter.py` covers frame conversion, metadata and composition output, scene mapping, section mapping, visual preservation for every supported visual type, audio asset deduplication, warnings preservation, deterministic ordering from shuffled input arrays, invalid timeline failure, zero-frame duration failure, file export writing, and input immutability.

Milestone 3 wires the CLI. This milestone is complete: `synccut/cli.py` has a Typer command named `export-remotion`. It accepts a positional `timeline_json: Path` and an `--out` option. The CLI calls `export_remotion_props_file`, prints a concise success summary, catches `SyncCutError`, and does not contain mapping logic.

Milestone 4 validates with real generated data. This milestone is complete: the existing test suite passed, a fresh `timeline.json` was generated from examples, the timeline validated, `remotion/props.json` was exported, `json.tool` accepted the props JSON, and key fields were inspected. Command outputs are recorded in this ExecPlan.

## Concrete Steps

Run all commands from the repository root:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut

Inspect the current files before editing:

    rg --files -g '!**/__pycache__/**' | sort

Implement Milestone 1 by creating `synccut/remotion_exporter.py`. The module should import `json`, `math`, `copy.deepcopy`, `Path`, `Any`, `load_timeline_json`, `validate_timeline`, and `SyncCutError`. Keep data transformation in this module, not in `synccut/cli.py`.

Implement Milestone 2 by creating `tests/test_remotion_exporter.py`. Use small synthetic timeline dictionaries similar to `tests/test_timeline_validator.py`. Do not require real media files. Audio paths are string references only.

Implement Milestone 3 by editing `synccut/cli.py` to import `export_remotion_props_file` and add:

    @app.command("export-remotion")
    def export_remotion_cmd(
        timeline_json: Annotated[Path, typer.Argument(help="Path to timeline.json.")],
        out: Annotated[Path, typer.Option(help="Path to write Remotion props JSON.")],
    ) -> None:
        ...

The command should print a stable summary such as:

    Exported remotion/props.json
    scenes: 33
    sections: 7
    fps: 30
    duration_frames: 22584
    warnings: 1

The exact text can vary, but tests should assert important substrings.

Run the full test suite:

    .venv/bin/python -m pytest

Generate a fresh real timeline:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Validate the timeline:

    .venv/bin/synccut validate-timeline timeline.json

Export Remotion props:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

Validate the generated props JSON:

    .venv/bin/python -m json.tool remotion/props.json >/tmp/synccut_remotion_props_pretty.json

Inspect key fields:

    .venv/bin/python - <<'PY'
    import json
    from pathlib import Path
    data = json.loads(Path("remotion/props.json").read_text())
    print("composition:", data["composition"])
    print("total_scenes:", data["metadata"]["total_scenes"])
    print("duration_frames:", data["metadata"]["duration_frames"])
    print("scene_entries:", len(data["scenes"]))
    print("first_scene:", data["scenes"][0]["id"], data["scenes"][0]["start_frame"], data["scenes"][0]["end_frame"])
    print("last_scene:", data["scenes"][-1]["id"], data["scenes"][-1]["end_frame"])
    print("audio_assets:", len(data["assets"]["audio"]))
    print("warnings:", data["warnings"])
    PY

Expected values for the current real example are:

    total_scenes: 33
    total_sections: 7
    duration_sec: 752.79
    duration_frames: 22584
    scene_entries: 33
    audio_assets: 7
    warnings includes section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

## Tests to Write

Add focused unit tests in `tests/test_remotion_exporter.py`:

- `seconds_to_frame` maps `0.0` to `0`, `9.137` at 30 FPS to `274`, and `752.79` at 30 FPS to `22584`.
- A valid timeline exports metadata with `generated_by`, `source_timeline`, `fps`, `duration_sec`, `duration_frames`, `total_scenes`, and `total_sections`.
- Composition output has `id` `SyncCutVideo`, width `1920`, height `1080`, FPS `30`, and expected duration frames.
- Sections map global timing to section start/end/duration seconds and frames.
- Scenes map `scene_id` to `id` and preserve ordering, timing seconds, frame fields, `visual_type`, `visual`, `dialogue`, `audio`, `alignment`, and warnings.
- Each supported visual type is accepted and preserved: `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`.
- `assets.audio` contains one entry per unique section audio path, sorted by section order and section key.
- `assets.visuals` is an empty array.
- Top-level timeline warnings and validator warnings are copied into output warnings without making export fail.
- Shuffled input sections and scenes still produce deterministic section and scene ordering.
- Invalid timeline input raises `SyncCutError` clearly.
- A positive-duration scene that rounds to zero frames raises `SyncCutError` clearly.

Extend `tests/test_cli.py` with CLI tests:

- `export-remotion` succeeds on a tiny complete timeline fixture.
- The output file exists and is valid JSON.
- Output JSON has expected top-level keys: `metadata`, `composition`, `sections`, `scenes`, `assets`, and `warnings`.
- CLI output contains path, scene count, FPS, and duration frames.
- CLI returns non-zero with `Error:` and no Python traceback for invalid timeline input.

Existing tests for `build-timeline`, `validate-timeline`, and `inspect` must continue to pass unchanged.

## Validation and Acceptance

This phase is accepted when all of the following are true:

- `synccut export-remotion timeline.json --out remotion/props.json` exists.
- The command validates the input timeline before exporting.
- The command writes deterministic, human-readable JSON with two-space indentation.
- The output contains `metadata`, `composition`, `sections`, `scenes`, `assets`, and `warnings`.
- The output uses fixed FPS `30`, width `1920`, height `1080`, and composition id `SyncCutVideo`.
- `metadata.duration_frames` equals `floor(metadata.total_duration_sec * 30 + 0.5)`.
- Each output scene has start/end/duration seconds and start/end/duration frames.
- Each output scene preserves dialogue, visual, audio, alignment, section identity, and warnings.
- Every supported normalized visual type is preserved without rendering, generating, or downloading assets.
- Warnings are copied and do not fail export.
- Invalid timeline input fails with a concise `Error: ...` message and exit code 1.
- The existing `build-timeline`, `validate-timeline`, and `inspect` behavior remains unchanged.
- The full test suite passes with `.venv/bin/python -m pytest`.
- Real example export produces 33 scene entries, 7 sections, 7 audio assets, and `duration_frames` 22584.

## Idempotence and Recovery

The export command is read-only with respect to `timeline.json`. It must not rewrite or normalize the input timeline file.

The export command may create the output parent directory, for example `remotion/`, if it does not exist. It may overwrite `remotion/props.json` because this phase does not define a `--force` option and the command is a deterministic export.

If implementation discovers that the real generated timeline fails validation, first determine whether the existing timeline is malformed or whether the exporter is too strict. Do not change `build-timeline`, `validate-timeline`, or `inspect` unless there is a clear bug, and record any such decision in this plan.

Generated files such as `timeline.json`, `remotion/props.json`, and Python `__pycache__` directories are artifacts. They should not be committed unless the user explicitly asks for generated fixtures.

Do not use destructive git commands. Do not run `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, or `git rebase` unless the user explicitly asks.

## Artifacts and Notes

At plan creation, the repository had these relevant source and test files:

    synccut/__init__.py
    synccut/alignment_loader.py
    synccut/cli.py
    synccut/models.py
    synccut/scenes_loader.py
    synccut/timeline_builder.py
    synccut/timeline_inspector.py
    synccut/timeline_validator.py
    synccut/validators.py
    tests/test_alignment_loader.py
    tests/test_cli.py
    tests/test_package.py
    tests/test_scenes_loader.py
    tests/test_timeline_builder.py
    tests/test_timeline_inspector.py
    tests/test_timeline_validator.py

At plan creation, `git status --short` showed only `timeline.json` as an untracked generated artifact. No source code was edited while creating this plan.

The completed validation and inspection plan recorded a successful real example timeline with 33 scenes, 7 sections, total duration 752.79 seconds, and one non-fatal warning:

    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

The current output of `synccut validate-timeline timeline.json` should remain:

    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79
    warnings: 1
    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

Milestone 1 verification transcript:

    $ .venv/bin/python -m pytest
    collected 75 items
    tests/test_alignment_loader.py ................                          [ 21%]
    tests/test_cli.py ........                                               [ 32%]
    tests/test_package.py ...                                                [ 36%]
    tests/test_scenes_loader.py ..............                               [ 54%]
    tests/test_timeline_builder.py ..............                            [ 73%]
    tests/test_timeline_inspector.py .....                                   [ 80%]
    tests/test_timeline_validator.py ...............                         [100%]
    75 passed in 0.35s

Milestone 1 pure exporter smoke check:

    $ .venv/bin/python - <<'PY'
    import json
    from pathlib import Path
    from synccut.remotion_exporter import build_remotion_props
    props = build_remotion_props(json.loads(Path('timeline.json').read_text()), Path('timeline.json'))
    print('duration_frames:', props['metadata']['duration_frames'])
    print('scenes:', len(props['scenes']))
    print('sections:', len(props['sections']))
    print('audio_assets:', len(props['assets']['audio']))
    print('warnings:', len(props['warnings']))
    PY
    duration_frames: 22584
    scenes: 33
    sections: 7
    audio_assets: 7
    warnings: 1

Milestone 2 verification transcript:

    $ .venv/bin/python -m pytest
    collected 99 items
    tests/test_alignment_loader.py ................                          [ 16%]
    tests/test_cli.py ........                                               [ 24%]
    tests/test_package.py ...                                                [ 27%]
    tests/test_remotion_exporter.py ........................                 [ 51%]
    tests/test_scenes_loader.py ..............                               [ 65%]
    tests/test_timeline_builder.py ..............                            [ 79%]
    tests/test_timeline_inspector.py .....                                   [ 84%]
    tests/test_timeline_validator.py ...............                         [100%]
    99 passed in 0.34s

Milestone 3 verification transcript:

    $ .venv/bin/python -m pytest
    collected 101 items
    tests/test_alignment_loader.py ................                          [ 15%]
    tests/test_cli.py ..........                                             [ 25%]
    tests/test_package.py ...                                                [ 28%]
    tests/test_remotion_exporter.py ........................                 [ 52%]
    tests/test_scenes_loader.py ..............                               [ 66%]
    tests/test_timeline_builder.py ..............                            [ 80%]
    tests/test_timeline_inspector.py .....                                   [ 85%]
    tests/test_timeline_validator.py ...............                         [100%]
    101 passed in 0.35s

Milestone 4 verification transcript:

    $ .venv/bin/python -m pytest
    collected 101 items
    tests/test_alignment_loader.py ................                          [ 15%]
    tests/test_cli.py ..........                                             [ 25%]
    tests/test_package.py ...                                                [ 28%]
    tests/test_remotion_exporter.py ........................                 [ 52%]
    tests/test_scenes_loader.py ..............                               [ 66%]
    tests/test_timeline_builder.py ..............                            [ 80%]
    tests/test_timeline_inspector.py .....                                   [ 85%]
    tests/test_timeline_validator.py ...............                         [100%]
    101 passed in 0.24s

Milestone 4 fresh timeline generation:

    $ .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Milestone 4 timeline validation:

    $ .venv/bin/synccut validate-timeline timeline.json
    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79
    warnings: 1
    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

Milestone 4 Remotion props export:

    $ .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    Exported remotion/props.json
    scenes: 33
    sections: 7
    fps: 30
    duration_frames: 22584
    warnings: 1

Milestone 4 props JSON validation:

    $ .venv/bin/python -m json.tool remotion/props.json >/tmp/synccut_remotion_props_pretty.json

    The command exited with status 0, so `remotion/props.json` is valid JSON.

Milestone 4 props key-field inspection:

    $ .venv/bin/python - <<'PY'
    import json
    from pathlib import Path

    data = json.loads(Path("remotion/props.json").read_text())

    print("composition:", data["composition"])
    print("total_scenes:", data["metadata"]["total_scenes"])
    print("total_sections:", data["metadata"]["total_sections"])
    print("duration_sec:", data["metadata"]["duration_sec"])
    print("duration_frames:", data["metadata"]["duration_frames"])
    print("scene_entries:", len(data["scenes"]))
    print("first_scene:", data["scenes"][0]["id"], data["scenes"][0]["start_frame"], data["scenes"][0]["end_frame"])
    print("last_scene:", data["scenes"][-1]["id"], data["scenes"][-1]["end_frame"])
    print("audio_assets:", len(data["assets"]["audio"]))
    print("warnings:", data["warnings"])
    PY
    composition: {'id': 'SyncCutVideo', 'width': 1920, 'height': 1080, 'fps': 30, 'duration_frames': 22584}
    total_scenes: 33
    total_sections: 7
    duration_sec: 752.79
    duration_frames: 22584
    scene_entries: 33
    first_scene: scene_001 0 274
    last_scene: scene_033 22584
    audio_assets: 7
    warnings: ['section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031']

## Interfaces and Dependencies

Use Python 3.11 or newer.

Use only standard-library modules for the exporter: `json`, `math`, `copy`, `pathlib`, and typing helpers are enough.

Use Typer only in `synccut/cli.py` for command wiring. Do not move export mapping logic into the CLI.

Use pytest for tests. Run tests with:

    .venv/bin/python -m pytest

Use existing validation and error primitives:

    from synccut.timeline_validator import load_timeline_json, validate_timeline
    from synccut.validators import SyncCutError

Do not add Remotion, ffmpeg, browser, video, AI-generation, B-roll download, GUI, web app, or Node dependencies. The word "Remotion" in this phase refers only to the shape of the props JSON intended for a future Remotion project.

The final public command surface after this phase should include:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json
    synccut validate-timeline timeline.json
    synccut inspect timeline.json
    synccut export-remotion timeline.json --out remotion/props.json

## Revision Note

2026-05-10 / Codex: Initial ExecPlan created after reading the required project instructions, schemas, testing guide, future-phases document, and the completed build-timeline and validate/inspect plans. The plan defines the additive `export-remotion` command, expected props schema, visual-type preservation, timing and frame conversion rules, tests, validation commands, and explicit future-phase exclusions.

2026-05-10 / Codex: Updated after Milestone 1 implementation. The repository now has pure Remotion props export helpers in `synccut/remotion_exporter.py`, a passing `.venv/bin/python -m pytest` run, and a pure smoke check against the generated example timeline. The update records the file-I/O boundary and deduplication decisions.

2026-05-11 / Codex: Updated after Milestone 2 implementation. The repository now has focused pure exporter tests in `tests/test_remotion_exporter.py`, covering frame conversion, mapping, preservation, warning merging, ordering, invalid input, zero-frame failures, file writing, and input immutability. The full pytest suite passed with 99 tests.

2026-05-11 / Codex: Updated after Milestone 3 implementation. The Typer CLI now exposes `export-remotion`, delegates to `export_remotion_props_file`, prints a stable summary, handles expected `SyncCutError` failures without tracebacks, and has CLI tests for success and invalid input. The full pytest suite passed with 101 tests.

2026-05-11 / Codex: Updated after Milestone 4 validation. A fresh real `timeline.json` was generated from examples, validated, exported to `remotion/props.json`, accepted by `json.tool`, and inspected. The export produced 33 scenes, 7 sections, 7 audio assets, duration 752.79 seconds, 22584 frames, and the known 1.115s `07_CONCLUSION` gap warning. This completes the Remotion props export phase.
