# Add timeline validation and inspection commands

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement these commands from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can now build `timeline.json` from scenes, audio references, and alignment data. The next useful capability is to check that a timeline file is structurally valid and to inspect its contents without rendering video. After this change, a user can run `synccut validate-timeline timeline.json` to catch broken timing, missing references, unsupported visual types, overlaps, and suspicious gaps, and can run `synccut inspect timeline.json` to see a readable overview grouped by section.

This phase must remain a timeline validation and reporting phase only. It must not parse DOCX, call Remotion, call ffmpeg, generate AI video, download B-roll, assemble video, or add GUI or web app behavior.

## Progress

- [x] (2026-05-10T15:29:14Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/testing.md`, and `docs/plans/build-timeline-mvp.md`.
- [x] (2026-05-10T15:29:14Z) Inspected the current implementation file layout and confirmed the build-timeline MVP modules are present.
- [x] (2026-05-10T15:29:14Z) Created this ExecPlan for `validate-timeline` and `inspect`.
- [x] (2026-05-10T15:40:39Z) Implemented timeline JSON loading and validation helpers in `synccut/timeline_validator.py`.
- [x] (2026-05-10T15:54:27Z) Implemented pure timeline inspection summary and grouped overview formatting in `synccut/timeline_inspector.py`.
- [x] (2026-05-10T16:08:43Z) Wired `synccut validate-timeline` and `synccut inspect` into the Typer CLI while keeping CLI logic thin.
- [x] (2026-05-10T16:08:43Z) Added CLI tests for validate success, validation warnings, top-level timeline warnings, invalid validation, inspect success, and inspect malformed-input failure.
- [x] (2026-05-10T16:20:12Z) Ran final validation commands after CLI wiring against a freshly generated `timeline.json` from `examples/`.

## Surprises & Discoveries

- Observation: At plan creation time, `timeline.json` was not present in the repository root even though the completed build-timeline MVP can generate it.
  Evidence: A local check printed `timeline.json missing`. Implementation should generate a fresh timeline from examples when an end-to-end validation artifact is needed.
- Observation: The existing build-timeline MVP source modules are already separated by responsibility.
  Evidence: The tree contains `synccut/scenes_loader.py`, `synccut/alignment_loader.py`, `synccut/timeline_builder.py`, `synccut/validators.py`, and a thin `synccut/cli.py`.
- Observation: The real generated example timeline is structurally valid under the pure validator and contains one suspicious gap warning.
  Evidence: `validate_timeline_file(Path("timeline.json"))` returned `ok: True`, `errors: 0`, `warnings: 1`, `scenes: 33`, `sections: 7`, and the warning `section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.
- Observation: The generated example timeline overview starts with `scene_001` matched by `sentence`.
  Evidence: `build_timeline_overview` printed `scene_001 0.000s-9.137s 9.137s AI_VIDEO sentence`, which matches the known example boundary mismatch from the build-timeline MVP.
- Observation: The CLI `validate-timeline` command reports the same known generated-example gap warning and exits successfully.
  Evidence: `.venv/bin/synccut validate-timeline timeline.json` printed `warnings: 1` and `Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031`.

## Decision Log

- Decision: Implement validation and inspection as additive modules rather than changing `timeline_builder.py`.
  Rationale: The build-timeline MVP is complete and tested. Validation and inspection consume `timeline.json`; they should not change timeline generation unless a clear bug is discovered.
  Date/Author: 2026-05-10 / Codex
- Decision: Treat overlaps as validation errors and suspicious gaps as warnings.
  Rationale: Overlaps mean two scenes in the same section occupy the same global time range and can break downstream rendering. Gaps can be intentional pauses, so the validator should report them without failing by default.
  Date/Author: 2026-05-10 / Codex
- Decision: Use one second as the default suspicious-gap threshold.
  Rationale: The current command targets do not include options. A fixed, documented default keeps scope small and still catches unusually large empty spaces between consecutive scenes in the same section.
  Date/Author: 2026-05-10 / Codex
- Decision: Check path presence as string fields but do not require referenced audio or alignment files to exist on disk.
  Rationale: The command validates `timeline.json` structure. A timeline may be moved separately from its original input directories. Disk existence checks would make inspection less portable and would expand scope into asset verification.
  Date/Author: 2026-05-10 / Codex
- Decision: Make JSON loading raise `SyncCutError`, but make timeline schema validation return a `TimelineValidationResult` with collected errors and warnings.
  Rationale: File-not-found and malformed JSON prevent validation from starting and should be handled like other user-facing load errors. Once a JSON object is available, collecting multiple schema errors is more useful than failing at the first one.
  Date/Author: 2026-05-10 / Codex
- Decision: Use `TimelineValidationResult.ok` as the success indicator.
  Rationale: This keeps the future CLI simple and lets tests assert the same behavior without duplicating error-count logic.
  Date/Author: 2026-05-10 / Codex
- Decision: Make the inspector call `validate_timeline` and raise `SyncCutError` with collected validation details when the timeline is not safe to inspect.
  Rationale: The inspector should be pure and should not crash with raw `KeyError` or `TypeError` on malformed input. Reusing the validator keeps structural rules centralized and gives the future CLI a known user-facing exception.
  Date/Author: 2026-05-10 / Codex
- Decision: Format all displayed seconds with three decimal places.
  Rationale: The generated timeline uses fractional seconds, and fixed precision keeps the overview deterministic and easy to scan.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep CLI validation output as a thin presentation of `TimelineValidationResult`.
  Rationale: The validator already owns structural checks, summary counts, and suspicious-gap detection. The CLI only loads the result, prints `OK` or `Error:` lines, and exits with the appropriate status.
  Date/Author: 2026-05-10 / Codex
- Decision: Have the `inspect` command call `load_timeline_json` and `build_timeline_overview` directly.
  Rationale: This preserves the pure inspector module as the source of formatting behavior and keeps malformed-file handling consistent with validation.
  Date/Author: 2026-05-10 / Codex
- Decision: Have `validate-timeline` print both top-level timeline warnings and warnings discovered by validation.
  Rationale: Existing `timeline.json` files can carry producer warnings in the root `warnings` array, while validation can discover additional suspicious gaps. CLI users should see both without either category causing a non-zero exit.
  Date/Author: 2026-05-10 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. The repository now has `synccut/timeline_validator.py` with `load_timeline_json`, `validate_timeline`, and `validate_timeline_file`, plus a `TimelineValidationResult` dataclass. The validator checks required top-level keys, metadata counts, section timing, scene timing, audio and alignment path fields, dialogue and visual fields, overlap errors, and suspicious-gap warnings. Focused tests in `tests/test_timeline_validator.py` cover valid timelines, malformed JSON, missing files, missing root sections, count mismatches, invalid timing, overlaps, warnings, missing paths, and unsupported visual types.

Verification for Milestone 1 passed with `.venv/bin/python -m pytest`, which collected 64 tests and all passed. A freshly generated example timeline validated with no errors and one suspicious-gap warning.

Milestone 2 is complete. The repository now has `synccut/timeline_inspector.py` with `build_timeline_overview` and `section_overview_rows`. The inspector validates the timeline before formatting, raises `SyncCutError` instead of crashing on malformed input, and produces deterministic text grouped by section. It prints the source path when provided, total scenes, total sections, duration, warning count, section rows, and scene rows with scene id, timing, visual type, and match method.

Verification for Milestone 2 passed with `.venv/bin/python -m pytest`, which collected 69 tests and all passed. A pure-inspector check against the generated example timeline printed the expected summary and the first grouped section rows.

Milestone 3 is complete. `synccut/cli.py` now exposes `validate-timeline` and `inspect` in addition to the existing `build-timeline` command. `validate-timeline` prints a stable success summary, emits top-level timeline warnings and suspicious-gap warnings without failing, prints collected validation errors as `Error:` lines, and suppresses Python tracebacks for expected `SyncCutError` failures. `inspect` loads timeline JSON, delegates formatting to `build_timeline_overview`, and reports malformed input concisely.

Verification for Milestone 3 passed with `.venv/bin/python -m pytest`, which collected 75 tests and all passed. CLI tests now cover valid timeline validation, validation warnings, top-level timeline warnings, invalid validation, inspect success, and inspect malformed-input failure.

Milestone 4 is complete. A fresh `timeline.json` was generated from `examples/scenes.json`, `examples/audio`, and `examples/alignments` using the existing `build-timeline` command. The full pytest suite passed, the real generated timeline validated successfully through the CLI, and `synccut inspect timeline.json` printed the expected grouped overview for all seven sections and thirty-three scenes.

Final verification for this phase passed with `.venv/bin/python -m pytest`, which collected 75 tests and all passed. Real-example validation output was `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, and `warnings: 1`, with the known `07_CONCLUSION` gap warning. No source changes were needed during Milestone 4.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. The completed build-timeline MVP already provides:

- `synccut/cli.py`, the Typer command module. It currently exposes `build-timeline`, which should remain thin and should not be rewritten for this phase.
- `synccut/scenes_loader.py`, which reads and validates `scenes.json`.
- `synccut/alignment_loader.py`, which discovers audio and alignment files and loads alignment JSON.
- `synccut/timeline_builder.py`, which matches scenes to alignment timing and creates the timeline dictionary.
- `synccut/models.py`, which defines shared dataclasses for scenes, alignments, section assets, and match results.
- `synccut/validators.py`, which defines `SyncCutError`, visual type normalization, text normalization, and shared validation helpers.
- `tests/`, which already covers package import, CLI build behavior, scene loading, alignment loading, and timeline building.

The completed build-timeline command is:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json

The new commands are:

    synccut validate-timeline timeline.json
    synccut inspect timeline.json

A timeline file is a JSON object produced by the build-timeline MVP. It has four top-level keys:

- `metadata`, an object with generation details and counts.
- `sections`, an array of section entries with section order, global section timing, audio path, and alignment path.
- `timeline`, an array of scene entries with scene identity, timing, dialogue, visual data, audio reference, alignment match metadata, and warnings.
- `warnings`, an array of top-level warning strings.

Timing values are seconds. Global timing means seconds from the beginning of the full video. Local timing means seconds within one narration section.

Validation means reading `timeline.json` and checking whether required fields exist, field types are sensible, timing math is coherent, and scene ranges do not overlap. Inspection means printing a human-readable summary and grouped timeline overview to the terminal. Neither command should modify the timeline file.

## Expected timeline validation behavior

`synccut validate-timeline timeline.json` should exit with status 0 for a structurally valid timeline. It should print a concise success summary such as:

    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79
    warnings: 0

If validation errors are found, the command should print each error clearly and exit with status 1. Error messages should include enough location context for a user to fix the file, for example:

    Error: timeline[3].timing.duration_sec must be positive
    Error: timeline[4] overlaps previous scene in section 01_HOOK
    Error: timeline[7].audio.path must be a non-empty string

Warnings should be printed but should not cause failure by default. Suspicious gaps should be warnings, for example:

    Warning: section 02_INTRO has a gap of 3.25s between scene_004 and scene_005

The validator should check at least these conditions:

- The file exists and contains valid JSON.
- The root JSON value is an object.
- `metadata`, `sections`, `timeline`, and `warnings` exist.
- `metadata.total_scenes`, `metadata.total_sections`, and `metadata.total_duration_sec` exist and are numeric where appropriate.
- `sections` is a non-empty array for non-empty timelines.
- `timeline` is a non-empty array for MVP output.
- `metadata.total_scenes` equals the number of timeline entries.
- `metadata.total_sections` equals the number of section entries.
- Each section has `section_key`, `section`, `section_order`, `audio_path`, `alignment_path`, `local_duration_sec`, `global_start_sec`, and `global_end_sec`.
- Each section timing has numeric start and end values, positive duration, and `global_end_sec >= global_start_sec`.
- Each timeline entry has `scene_id`, `scene_order`, `section`, `section_order`, `section_key`, `timing`, `audio`, `alignment`, `dialogue`, `visual`, and `warnings`.
- Each scene timing has numeric `start_sec`, `end_sec`, `duration_sec`, `local_start_sec`, and `local_end_sec`.
- Each scene duration is positive.
- `end_sec >= start_sec`.
- `duration_sec` is close to `end_sec - start_sec`. Use a small tolerance such as `0.001` seconds to avoid false failures from floating-point arithmetic.
- `audio.path` is a non-empty string.
- `alignment.path` is a non-empty string.
- `alignment.match_method` is one of `paragraph`, `sentence`, or `word_span`.
- `alignment.matched_units` is an array.
- `dialogue.text` is a non-empty string.
- `dialogue.paragraphs` is an array of non-empty strings.
- `visual.type` is one of `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, or `TIMELINE`.
- Scene entries are grouped and evaluated by `section_key`, sorted by `start_sec` for overlap and gap checks.
- Any scene in the same section whose `start_sec` is before the previous scene's `end_sec` is an overlap error.
- Any gap greater than one second between consecutive scenes in the same section is a suspicious-gap warning.
- `metadata.total_duration_sec` is close to the last section `global_end_sec` when sections exist.

The validator should return structured results from pure functions so tests can assert errors and warnings without invoking the CLI.

## Expected inspect behavior

`synccut inspect timeline.json` should validate enough structure to avoid crashing, then print a readable overview grouped by section. It should not fail on warnings unless the timeline is too malformed to inspect.

The output should include:

- Source file path.
- Total scenes.
- Total sections.
- Total duration in seconds.
- Top-level warning count.
- A section-by-section listing.
- For each section, its key, name, global start/end, duration, and scene count.
- For each scene, scene id, global start/end, duration, visual type, and match method.

Example shape:

    Timeline: timeline.json
    Scenes: 33
    Sections: 7
    Duration: 752.79s
    Warnings: 0

    [01_HOOK] HOOK 0.000s-18.390s (18.390s), 3 scenes
      scene_001 0.000s-9.137s 9.137s AI_VIDEO sentence
      scene_002 9.137s-13.824s 4.687s COMPARISON_CARD paragraph

The exact spacing can vary, but tests should assert stable important substrings rather than every column position. The output should be deterministic: sections sorted by `section_order` and `section_key`, scenes sorted by `start_sec` within each section.

## Plan of Work

Milestone 1 creates a pure validation module. This milestone is complete: `synccut/timeline_validator.py` loads JSON from a `Path`, validates timeline structure, and returns a result object containing errors, warnings, and summary counts. Validation is independent of Typer. Unit tests prove valid timelines pass and malformed timelines produce precise errors.

Milestone 2 creates a pure inspection module. This milestone is complete: `synccut/timeline_inspector.py` accepts a timeline dictionary and returns formatted text. Output formatting remains outside `synccut/cli.py` and can be tested without running the CLI. Tests prove output includes metadata summary, grouped section rows, scene rows, deterministic ordering, and clear failure for malformed input.

Milestone 3 wires the CLI. This milestone is complete: `synccut/cli.py` has `validate-timeline` and `inspect` commands. The CLI calls the pure modules, prints summaries or errors, exits with the correct status, and leaves the existing `build-timeline` behavior unchanged. CLI tests exercise success and failure paths.

Milestone 4 validates with real generated data. This milestone is complete: a fresh `timeline.json` was generated from `examples/` using the existing build command, then `validate-timeline` and `inspect` were run against it. The command output is recorded in this plan, and `.venv/bin/python -m pytest` passes.

## Concrete Steps

Run all commands from the repository root:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut

Inspect the current implementation before editing:

    find synccut tests docs/plans -maxdepth 2 -type f -print | sort

Create `synccut/timeline_validator.py`. Suggested public functions are:

    load_timeline_json(path: Path) -> dict
    validate_timeline(data: dict) -> TimelineValidationResult
    validate_timeline_file(path: Path) -> TimelineValidationResult

Add a dataclass such as:

    @dataclass(frozen=True)
    class TimelineValidationResult:
        path: str | None
        errors: list[str]
        warnings: list[str]
        total_scenes: int
        total_sections: int
        total_duration_sec: float | None

The exact fields can change if the implementation stays easy to test and the CLI can print the required summary.

Create `synccut/timeline_inspector.py`. Suggested public functions are:

    build_timeline_overview(data: dict, path: Path | None = None) -> str
    section_overview_rows(data: dict) -> list[str]

Update `synccut/cli.py` by adding two commands:

    @app.command("validate-timeline")
    def validate_timeline_cmd(timeline_json: Path) -> None:
        ...

    @app.command("inspect")
    def inspect_timeline_cmd(timeline_json: Path) -> None:
        ...

The command function names may differ, but the command names must be exactly `validate-timeline` and `inspect`.

Add tests:

- `tests/test_timeline_validator.py` for pure validation behavior.
- `tests/test_timeline_inspector.py` for pure inspection formatting.
- Extend or add CLI tests for `validate-timeline` and `inspect`.

Run the test suite:

    .venv/bin/python -m pytest

If `.venv` does not exist in a future environment, use the available Python interpreter and record the command and result in `Surprises & Discoveries`.

Generate a fresh real timeline:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Validate it:

    .venv/bin/synccut validate-timeline timeline.json

Inspect it:

    .venv/bin/synccut inspect timeline.json

The inspect output may be long. Capture only the first portion if recording evidence in this plan, for example:

    .venv/bin/synccut inspect timeline.json | sed -n '1,80p'

If the shell or sandbox does not allow pipes in the final command, run inspect directly and summarize the relevant first lines manually.

## Validation and Acceptance

This phase is accepted when all of the following are true:

- `synccut validate-timeline timeline.json` exists.
- `synccut inspect timeline.json` exists.
- Valid generated timelines pass validation with exit status 0.
- Invalid timeline JSON fails validation with exit status 1 and a concise error message.
- Missing `metadata`, `sections`, or `timeline` is detected.
- Invalid timing fields are detected.
- Negative or zero scene durations are detected.
- Scene overlap within a section is detected as an error.
- Suspicious gaps within a section are detected as warnings.
- Missing `audio.path` or `alignment.path` is detected.
- Unsupported `visual.type` is detected.
- Inspect output summarizes scenes, sections, duration, and warning count.
- Inspect output prints a readable timeline overview grouped by section.
- The existing `build-timeline` behavior still passes its tests.
- The full test suite passes with `.venv/bin/python -m pytest`.

Expected real-example validation output should be close to:

    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79

The exact text can be adjusted, but it must be stable enough for CLI tests to assert important substrings.

## Idempotence and Recovery

Both new commands are read-only with respect to `timeline.json`. `validate-timeline` and `inspect` must not rewrite, normalize, or mutate the file they read.

Generating `timeline.json` from examples for validation is safe to repeat because the existing build command intentionally overwrites the output file. If a generated `timeline.json` should not remain in the repository root, remove only that generated artifact after recording validation evidence. Do not remove source files, docs, examples, or tests.

If validation logic initially rejects the real generated timeline, first determine whether the timeline is actually invalid or whether the new validator is too strict. Fix the validator if it conflicts with the schema already produced by the completed build-timeline MVP. Only change build-timeline behavior if there is a clear bug, and record that decision in this plan.

Do not use destructive git commands. Do not run `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, or `git rebase` unless the user explicitly asks.

## Artifacts and Notes

At plan creation, the repository implementation files relevant to this phase were:

    synccut/__init__.py
    synccut/alignment_loader.py
    synccut/cli.py
    synccut/models.py
    synccut/scenes_loader.py
    synccut/timeline_builder.py
    synccut/validators.py
    tests/test_alignment_loader.py
    tests/test_cli.py
    tests/test_package.py
    tests/test_scenes_loader.py
    tests/test_timeline_builder.py

At plan creation, `timeline.json` was not present in the repository root. A future implementation run should generate it from `examples/` before real-command validation.

Milestone 1 verification transcript:

    $ .venv/bin/python -m pytest
    collected 64 items
    tests/test_alignment_loader.py ................                          [ 25%]
    tests/test_cli.py ..                                                     [ 28%]
    tests/test_package.py ...                                                [ 32%]
    tests/test_scenes_loader.py ..............                               [ 54%]
    tests/test_timeline_builder.py ..............                            [ 76%]
    tests/test_timeline_validator.py ...............                         [100%]
    64 passed in 0.32s

Milestone 1 real timeline validation check:

    $ .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

    $ .venv/bin/python - <<'PY'
    from pathlib import Path
    from synccut.timeline_validator import validate_timeline_file
    result = validate_timeline_file(Path('timeline.json'))
    print('ok:', result.ok)
    print('errors:', len(result.errors))
    print('warnings:', len(result.warnings))
    print('scenes:', result.total_scenes)
    print('sections:', result.total_sections)
    print('duration:', result.total_duration_sec)
    if result.errors:
        print(result.errors[:3])
    if result.warnings:
        print(result.warnings[:3])
    PY
    ok: True
    errors: 0
    warnings: 1
    scenes: 33
    sections: 7
    duration: 752.79
    ['section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031']

Milestone 2 verification transcript:

    $ .venv/bin/python -m pytest
    collected 69 items
    tests/test_alignment_loader.py ................                          [ 23%]
    tests/test_cli.py ..                                                     [ 26%]
    tests/test_package.py ...                                                [ 30%]
    tests/test_scenes_loader.py ..............                               [ 50%]
    tests/test_timeline_builder.py ..............                            [ 71%]
    tests/test_timeline_inspector.py .....                                   [ 78%]
    tests/test_timeline_validator.py ...............                         [100%]
    69 passed in 0.28s

Milestone 2 real timeline inspection check:

    $ .venv/bin/python - <<'PY'
    import json
    from pathlib import Path
    from synccut.timeline_inspector import build_timeline_overview
    path = Path('timeline.json')
    data = json.loads(path.read_text())
    print('\n'.join(build_timeline_overview(data, path=path).splitlines()[:12]))
    PY
    Timeline: timeline.json
    Scenes: 33
    Sections: 7
    Duration: 752.790s
    Warnings: 1

    [01_HOOK] HOOK 0.000s-18.390s (18.390s), 3 scenes
      scene_001 0.000s-9.137s 9.137s AI_VIDEO sentence
      scene_002 9.346s-13.154s 3.808s COMPARISON_CARD paragraph
      scene_003 13.328s-18.390s 5.062s B_ROLL paragraph

    [02_INTRO] INTRO 18.390s-77.787s (59.397s), 4 scenes

The completed build-timeline MVP plan is `docs/plans/build-timeline-mvp.md`. It records that `build-timeline` produced 33 scenes, 7 sections, and total duration 752.79 seconds from the example data during its final validation.

Milestone 3 verification transcript:

    $ .venv/bin/python -m pytest
    collected 75 items
    tests/test_alignment_loader.py ................                          [ 21%]
    tests/test_cli.py ........                                               [ 32%]
    tests/test_package.py ...                                                [ 36%]
    tests/test_scenes_loader.py ..............                               [ 54%]
    tests/test_timeline_builder.py ..............                            [ 73%]
    tests/test_timeline_inspector.py .....                                   [ 80%]
    tests/test_timeline_validator.py ...............                         [100%]
    75 passed in 0.23s

Milestone 4 verification transcript:

    $ .venv/bin/python -m pytest
    collected 75 items
    tests/test_alignment_loader.py ................                          [ 21%]
    tests/test_cli.py ........                                               [ 32%]
    tests/test_package.py ...                                                [ 36%]
    tests/test_scenes_loader.py ..............                               [ 54%]
    tests/test_timeline_builder.py ..............                            [ 73%]
    tests/test_timeline_inspector.py .....                                   [ 80%]
    tests/test_timeline_validator.py ...............                         [100%]
    75 passed in 0.21s

Milestone 4 real timeline generation:

    $ .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Milestone 4 real timeline validation:

    $ .venv/bin/synccut validate-timeline timeline.json
    OK timeline.json
    scenes: 33
    sections: 7
    duration_sec: 752.79
    warnings: 1
    Warning: section 07_CONCLUSION has a gap of 1.115s between scene_030 and scene_031

Milestone 4 real timeline inspection:

    $ .venv/bin/synccut inspect timeline.json
    Timeline: timeline.json
    Scenes: 33
    Sections: 7
    Duration: 752.790s
    Warnings: 1

    [01_HOOK] HOOK 0.000s-18.390s (18.390s), 3 scenes
      scene_001 0.000s-9.137s 9.137s AI_VIDEO sentence
      scene_002 9.346s-13.154s 3.808s COMPARISON_CARD paragraph
      scene_003 13.328s-18.390s 5.062s B_ROLL paragraph

    [02_INTRO] INTRO 18.390s-77.787s (59.397s), 4 scenes
      scene_004 18.390s-32.287s 13.897s B_ROLL sentence
      scene_005 32.671s-44.791s 12.120s CHART sentence
      scene_006 45.174s-67.350s 22.176s B_ROLL sentence
      scene_007 67.675s-77.787s 10.112s TABLE sentence

    [03_MECHANISM_1] MECHANISM 1 — THE FOUNDRY SINGULARITY 77.787s-161.890s (84.103s), 5 scenes
      scene_008 77.787s-90.999s 13.212s AI_VIDEO sentence
      scene_009 91.382s-106.522s 15.140s COMPARISON_CARD sentence
      scene_010 107.125s-130.693s 23.568s B_ROLL sentence
      scene_011 131.076s-144.869s 13.793s TIMELINE sentence
      scene_012 145.113s-161.890s 16.777s CHART sentence

    [04_MECHANISM_2] MECHANISM 2 — THE PHYSICS WALL 161.890s-307.850s (145.960s), 6 scenes
      scene_013 161.890s-180.652s 18.762s AI_VIDEO sentence
      scene_014 180.826s-200.760s 19.934s TABLE sentence
      scene_015 201.085s-223.110s 22.025s B_ROLL sentence
      scene_016 223.551s-245.958s 22.407s COMPARISON_CARD sentence
      scene_017 246.202s-276.202s 30.000s B_ROLL sentence
      scene_018 276.376s-307.850s 31.474s CHART sentence

    [05_MECHANISM_3] MECHANISM 3 — THE CUSTOMER TRAP 307.850s-460.080s (152.230s), 6 scenes
      scene_019 307.850s-328.132s 20.282s SHARE_BREAKDOWN sentence
      scene_020 328.457s-353.326s 24.869s B_ROLL sentence
      scene_021 353.419s-375.269s 21.850s COMPARISON_CARD sentence
      scene_022 375.315s-400.462s 25.147s B_ROLL sentence
      scene_023 400.497s-423.485s 22.988s TABLE sentence
      scene_024 423.636s-460.080s 36.444s CHART sentence

    [06_MECHANISM_4] MECHANISM 4 — THE GEOGRAPHIC CHOKEPOINT 460.080s-604.043s (143.963s), 5 scenes
      scene_025 460.080s-477.669s 17.589s AI_VIDEO sentence
      scene_026 477.843s-507.170s 29.327s COMPARISON_CARD sentence
      scene_027 507.344s-531.330s 23.986s B_ROLL sentence
      scene_028 531.574s-561.388s 29.814s TABLE sentence
      scene_029 561.899s-604.043s 42.144s B_ROLL sentence

    [07_CONCLUSION] CONCLUSION 604.043s-752.790s (148.747s), 4 scenes
      scene_030 604.043s-634.868s 30.825s AI_VIDEO sentence
      scene_031 635.983s-670.835s 34.852s B_ROLL sentence
      scene_032 671.532s-712.399s 40.867s SHARE_BREAKDOWN sentence
      scene_033 713.095s-752.790s 39.695s AI_VIDEO sentence

## Interfaces and Dependencies

Use Python 3.11 or newer.

Use `pathlib.Path` for file paths.

Use standard-library `json` for JSON parsing.

Use Typer for the CLI commands already exposed by `synccut/cli.py`.

Use pytest for tests. Tests should run with:

    .venv/bin/python -m pytest

Use existing `SyncCutError` for expected user-facing errors when appropriate. Validation functions may also return errors as strings inside a result object; the CLI should decide whether to print them and exit non-zero.

Do not add Pydantic unless validation complexity becomes clearly useful enough to justify it. Do not add ffmpeg, Remotion, browser, video, AI-generation, or download dependencies for this phase.

The final public command surface must include:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json
    synccut validate-timeline timeline.json
    synccut inspect timeline.json

The final new module functions should be pure or mostly pure where practical so tests can validate behavior without shelling out to the CLI.

## Revision Note

2026-05-10 / Codex: Initial ExecPlan created after reading the required project instructions, schema and testing docs, and the completed build-timeline MVP plan. The plan defines additive timeline validation and inspection commands, expected checks, output behavior, module boundaries, tests, validation commands, and explicit future-phase exclusions.

2026-05-10 / Codex: Updated after Milestone 1 implementation. The repository now has pure timeline JSON loading and validation helpers, focused validator tests, a passing `.venv/bin/python -m pytest` run, and a pure-validator check against a freshly generated example timeline. The update records the result-object decision and the observed suspicious-gap warning in the generated example timeline.

2026-05-10 / Codex: Updated after Milestone 2 implementation. The repository now has pure timeline inspection formatting, focused inspector tests, a passing `.venv/bin/python -m pytest` run, and a pure-inspector check against the generated example timeline. The update records the validation-before-formatting and fixed-seconds formatting decisions.

2026-05-10 / Codex: Updated after Milestone 3 implementation. The Typer CLI now exposes `validate-timeline` and `inspect`, delegates validation and formatting to the pure modules, handles expected failures without tracebacks, and has CLI tests for success, top-level warnings, validation warnings, and malformed input. The full pytest suite passed with 75 tests.

2026-05-10 / Codex: Updated after Milestone 4 validation. A fresh real `timeline.json` was generated from `examples/`, `validate-timeline` passed with 33 scenes, 7 sections, duration 752.79, and the known 1.115s `07_CONCLUSION` gap warning, `inspect` printed the grouped overview, and the full pytest suite passed with 75 tests. This completes the validation and inspection phase.
