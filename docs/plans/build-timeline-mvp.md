# Build the build-timeline MVP

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement the MVP from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut needs a first working CLI command that turns prepared narration planning data into a timed production timeline. After this work, a user can run `synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` and receive a `timeline.json` file where each scene has global start and end seconds, references to its section audio and alignment file, the original dialogue, and normalized visual metadata.

This MVP deliberately does not parse DOCX, render video, call Remotion, call ffmpeg, generate AI video, download B-roll, or assemble an MP4. It treats `scenes.json` as an immutable input file and uses existing alignment JSON timestamps as the source of truth for timing.

## Progress

- [x] (2026-05-09T08:15:19Z) Read `AGENTS.md`, `.agent/PLANS.md`, `docs/architecture.md`, `docs/schemas.md`, `docs/matching.md`, `docs/testing.md`, and `docs/future-phases.md`.
- [x] (2026-05-09T08:15:19Z) Inspected current repository structure, including `examples/scenes.json`, `examples/audio/`, and `examples/alignments/`.
- [x] (2026-05-09T08:15:19Z) Created this ExecPlan for the `build-timeline` MVP.
- [x] (2026-05-10T08:14:52Z) Implemented package and CLI scaffolding without adding future-phase behavior: `pyproject.toml`, `synccut/__init__.py`, `synccut/cli.py`, and `tests/test_package.py`.
- [x] (2026-05-10T08:26:04Z) Implemented scene loading, normalization, and validation in `synccut/models.py`, `synccut/validators.py`, `synccut/scenes_loader.py`, and `tests/test_scenes_loader.py`.
- [x] (2026-05-10T08:35:00Z) Implemented audio and alignment discovery plus alignment validation in `synccut/alignment_loader.py`, extended models and validators, and added `tests/test_alignment_loader.py`.
- [x] (2026-05-10T08:44:37Z) Implemented strict scene-to-alignment matching and timeline JSON construction in `synccut/timeline_builder.py`, extended models and validators, and added `tests/test_timeline_builder.py`.
- [x] (2026-05-10T08:57:09Z) Wired the Typer CLI to load scenes, load section assets, build the timeline dictionary, write `timeline.json`, and report known SyncCut errors without tracebacks; added `tests/test_cli.py`.
- [x] (2026-05-10T08:57:09Z) Ran full MVP validation commands: pytest passed, the real example command wrote `timeline.json`, JSON validation passed, and inspection confirmed 33 scenes, 7 sections, and final scene end equal to total duration.

## Surprises & Discoveries

- Observation: The repository already contains empty `synccut/` and `tests/` directories, plus real example fixtures under `examples/`.
  Evidence: `find . -maxdepth 4 -type f -print` showed `examples/scenes.json`, five `examples/audio/*.mp3` files, and five `examples/alignments/*_alignment_tmp.json` files, while `ls -la synccut` and `ls -la tests` showed no Python files yet.
- Observation: The example alignment JSON has both compact normalized fields and raw alignment fields, but the MVP only needs the top-level `total_duration_sec`, `paragraphs`, nested `sentences`, and `words`.
  Evidence: `jq 'keys' examples/alignments/01_HOOK_alignment_tmp.json` returned `normalized_alignment`, `paragraphs`, `raw_alignment`, `total_duration_sec`, `total_paragraphs`, `total_sentences`, `total_words`, and `words`.
- Observation: Example scene visual data includes the non-normalized visual type `B-ROLL`, so visual type normalization is required for real input, not just for tests.
  Evidence: `examples/scenes.json` contains scene `scene_003` with `"visual": { "type": "B-ROLL", ... }`.
- Observation: By Milestone 1 implementation time, the example data contained seven complete sections rather than the five sections observed when this plan was first drafted.
  Evidence: `examples/scenes.json` has 33 scenes across `01_HOOK`, `02_INTRO`, `03_MECHANISM_1`, `04_MECHANISM_2`, `05_MECHANISM_3`, `06_MECHANISM_4`, and `07_CONCLUSION`; `examples/audio/` and `examples/alignments/` contain matching files for all seven section keys.
- Observation: The shell environment does not provide a bare `python` executable, and system Python does not have pytest or Typer installed.
  Evidence: `python -m pytest` failed with `zsh:1: command not found: python`; `python3 -m pytest` failed with `/usr/bin/python3: No module named pytest`; `python3 -c 'import typer'` failed with `ModuleNotFoundError: No module named 'typer'`.
- Observation: System Python is externally managed, so project dependencies had to be installed into a local virtual environment.
  Evidence: `python3 -m pip install -e '.[dev]'` failed with `error: externally-managed-environment`; `python3 -m venv .venv` succeeded, then `.venv/bin/python -m pip install -e '.[dev]'` succeeded after network access was approved.
- Observation: A Typer app with a single registered command and no callback presented that command as the root command, which did not match the required `synccut build-timeline ...` invocation shape.
  Evidence: `.venv/bin/synccut --help` initially showed `Usage: synccut [OPTIONS] SCENES_JSON` rather than `Usage: synccut [OPTIONS] COMMAND [ARGS]...`; adding a lightweight `@app.callback()` made `.venv/bin/synccut --help` list `build-timeline` under Commands.
- Observation: The real example data exercises sentence fallback immediately.
  Evidence: A Milestone 4 smoke check built the example timeline in memory and reported `scene_001 sentence`, because the scene has two dialogue paragraphs while the first alignment section stores the same text as one paragraph with multiple sentences.

## Decision Log

- Decision: Use section-local alignment timestamps and accumulate section durations from `total_duration_sec` to compute global timing.
  Rationale: The project rules state that alignment timestamps are section-local and that alignment duration is the MVP source of truth. This avoids ffmpeg or ffprobe and keeps audio decoding out of scope.
  Date/Author: 2026-05-09 / Codex
- Decision: Treat audio files as required references but do not decode or measure them.
  Rationale: The MVP must load matching audio files, but the project explicitly forbids using ffmpeg/ffprobe unless requested. Placeholder `.mp3` files must also work in tests.
  Date/Author: 2026-05-09 / Codex
- Decision: Keep matching strict by default and raise clear errors for missing, ambiguous, or unmatched data.
  Rationale: The matching rules say not to silently invent timing. Strict failures prevent a plausible-looking timeline with fabricated or wrong scene timings.
  Date/Author: 2026-05-09 / Codex
- Decision: Create a small Python package with thin Typer CLI code and pure timeline-building functions.
  Rationale: The architecture document names this separation, and it makes scene loading, file discovery, matching, and timeline generation independently testable.
  Date/Author: 2026-05-09 / Codex
- Decision: Add minimal packaging only if needed to expose the target `synccut` command.
  Rationale: The current repository has no `pyproject.toml`; the command target requires a console entry point or an equivalent documented invocation. A minimal `pyproject.toml` with Typer and pytest dependencies is enough for the MVP.
  Date/Author: 2026-05-09 / Codex
- Decision: Expose the console script as `synccut = "synccut.cli:app"` and register a Typer subcommand named `build-timeline`.
  Rationale: Typer supports using an explicit `typer.Typer()` app as the package script entry point, and this keeps CLI wiring ready for later milestones without adding loader or timeline behavior now.
  Date/Author: 2026-05-10 / Codex
- Decision: Make the scaffolded `build-timeline` command fail with a clear not-implemented Typer error for now.
  Rationale: Milestone 1 requires CLI scaffolding only. A visible placeholder confirms the command is registered while preventing accidental partial MVP behavior before scene loading, alignment loading, and timeline generation exist.
  Date/Author: 2026-05-10 / Codex
- Decision: Add a no-op Typer callback to force SyncCut to behave as a multi-command CLI even while only `build-timeline` exists.
  Rationale: The target command includes a subcommand name. The callback keeps `synccut build-timeline ...` as the public shape now and leaves room for future commands without changing the root CLI behavior later.
  Date/Author: 2026-05-10 / Codex
- Decision: Represent loaded scene data with frozen standard-library dataclasses.
  Rationale: Milestone 2 only needs simple validated containers for scenes, dialogue, and visual metadata. Dataclasses keep the package dependency-free beyond Typer and make mutation by later pipeline steps less likely.
  Date/Author: 2026-05-10 / Codex
- Decision: When `dialogue.paragraphs` is missing or null, use `dialogue.text` as a single paragraph.
  Rationale: The plan allows this fallback for matching, and it lets valid scene input with complete dialogue text proceed without inventing timing or changing the input file.
  Date/Author: 2026-05-10 / Codex
- Decision: Allow missing `visual.prompt` and `visual.data` to load as null-equivalent values while requiring `visual.type`.
  Rationale: The MVP needs to preserve prompt and data when present, but structured visual types such as charts can reasonably contain null prompt or data. Strict type validation remains focused on the fields required to identify and match scenes.
  Date/Author: 2026-05-10 / Codex
- Decision: Represent alignment paragraphs, sentences, words, and section assets with frozen dataclasses alongside scene dataclasses.
  Rationale: Milestone 3 needs validated containers for alignment timing and discovered file references before timeline matching exists. Keeping these as dataclasses preserves the same simple dependency-free model style used for scenes.
  Date/Author: 2026-05-10 / Codex
- Decision: Store discovered audio and alignment paths as strings in `SectionAsset` and `AlignmentSection`.
  Rationale: The future `timeline.json` output needs JSON-serializable path values, and loader tests can still compare these string paths deterministically without decoding audio or building a timeline.
  Date/Author: 2026-05-10 / Codex
- Decision: Validate nested sentence word arrays when present but only expose the top-level alignment `words` list on `AlignmentSection`.
  Rationale: The MVP matching rules name top-level words as useful alignment data. Nested sentence words still need validation because malformed timing should fail early, but exposing duplicate word collections is unnecessary until the matching implementation proves it needs them.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep `match_scene_to_alignment(scene, alignment)` as the public one-scene matcher and use an internal matcher parameter for previous local end during timeline construction.
  Rationale: The requested public signature has no previous-end argument, but `build_timeline` must prevent repeated text from matching backwards across scenes. An internal helper lets tests use the public API while `build_timeline` carries per-section state.
  Date/Author: 2026-05-10 / Codex
- Decision: Normalize matching text by replacing curly quotes with straight quotes, replacing dash variants with a plain hyphen, removing the bridge marker `⟶`, lowercasing, trimming, and collapsing whitespace.
  Rationale: This follows the MVP matching rules and keeps matching tolerant of typography differences without changing output dialogue text.
  Date/Author: 2026-05-10 / Codex
- Decision: Sort timeline entries by `section_order`, `section_key`, and `scene_order`.
  Rationale: This gives deterministic output and aligns with the requirement to preserve scene order by section and scene order, even if callers pass scenes or sections in a different order.
  Date/Author: 2026-05-10 / Codex
- Decision: Keep `synccut/cli.py` as a thin orchestration layer that only calls `load_scenes`, `load_section_assets`, and `build_timeline`, then writes JSON.
  Rationale: Timeline logic is already testable in loader and builder modules. Keeping the CLI thin avoids duplicating behavior and preserves the architecture boundary.
  Date/Author: 2026-05-10 / Codex
- Decision: Overwrite the output path when `--out` already exists.
  Rationale: The ExecPlan permits overwriting and does not require `--force`. Adding a new option would expand scope unnecessarily for the MVP.
  Date/Author: 2026-05-10 / Codex
- Decision: Format known `SyncCutError` failures as `Error: ...` on stderr and exit with status 1.
  Rationale: This gives concise user-facing CLI failures without a Python traceback while preserving tracebacks for unexpected programming errors during development.
  Date/Author: 2026-05-10 / Codex

## Outcomes & Retrospective

Milestone 1 is complete. The repository now has minimal Python packaging, an importable `synccut` package, a Typer app with the `build-timeline` command registered, and a smoke test proving package import and CLI help loading. No scene loading, alignment loading, timeline generation, Remotion, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, or web app logic has been implemented.

Verification for Milestone 1 passed with the local virtual environment: `.venv/bin/python -m pytest` collected 3 tests and all passed. The requested bare command `python -m pytest` was attempted first but could not run because this shell has no `python` executable on PATH.

Milestone 2 is complete. The repository now has scene/domain dataclasses, scene-only validation helpers, and `load_scenes(path: Path) -> tuple[dict, list[Scene]]`. The loader validates the top-level `metadata` and `scenes` structure, rejects empty scene arrays, validates required scene fields, normalizes `B-ROLL` to `B_ROLL`, rejects unsupported visual types, infers missing `section_key` values from `section_order` and `section`, preserves dialogue and visual data, and does not write back to `scenes.json`.

Verification for Milestone 2 passed with the local virtual environment: `.venv/bin/python -m pytest` collected 17 tests and all passed. The CLI `build-timeline` behavior remains a scaffolded placeholder; no audio discovery, alignment loading, or timeline generation was added.

Milestone 3 is complete. The repository now has `synccut/alignment_loader.py` with `discover_audio_file`, `discover_alignment_file`, `load_alignment`, and `load_section_assets`. Audio discovery prefers exact `<section_key>.mp3`, falls back to one `<section_key>*.mp3` match, and reports missing or ambiguous files clearly without inspecting audio contents. Alignment discovery uses `<section_key>_alignment*.json`; alignment loading validates malformed JSON, positive `total_duration_sec`, non-empty paragraphs, paragraph timing, optional sentences, and optional words. Section assets are derived uniquely from scenes and sorted by `section_order` and `section_key`.

Verification for Milestone 3 passed with the local virtual environment: `.venv/bin/python -m pytest` collected 33 tests and all passed. A real fixture smoke check loaded `examples/scenes.json` and returned seven sorted section assets: `01_HOOK`, `02_INTRO`, `03_MECHANISM_1`, `04_MECHANISM_2`, `05_MECHANISM_3`, `06_MECHANISM_4`, and `07_CONCLUSION`. The CLI `build-timeline` behavior remains a scaffolded placeholder; no scene-to-alignment matching or timeline generation was added.

Milestone 4 is complete. The repository now has `synccut/timeline_builder.py` with `match_scene_to_alignment` and `build_timeline`. Matching is strict and section-local, tries paragraph matching, then sentence fallback, then word-span fallback, and raises `SyncCutError` with scene id and section key when matching fails. Timeline construction computes section offsets from sorted section assets and alignment durations, tracks previous local end per section to avoid repeated text matching backwards, preserves dialogue and visual data, emits normalized visual types, and returns a JSON-serializable dictionary with `metadata`, `sections`, `timeline`, and `warnings`.

Verification for Milestone 4 passed with the local virtual environment: `.venv/bin/python -m pytest` collected 45 tests and all passed. A real fixture smoke check loaded scenes and section assets from `examples/`, built the timeline in memory without writing a file, and reported 33 scenes, 7 sections, total duration 752.79 seconds, `scene_001` matched by sentence fallback, and final scene `scene_033` ending at 752.79 seconds. The CLI `build-timeline` behavior remains a scaffolded placeholder; no file-writing command behavior was added.

Milestone 5 is complete. The Typer CLI now implements the target `synccut build-timeline` command by loading scenes, discovering and loading section assets, building the timeline dictionary, and writing deterministic human-readable JSON with two-space indentation to `--out`. Known SyncCut validation errors are caught and displayed as concise CLI errors without tracebacks. The command intentionally overwrites the output file because the ExecPlan allows this and no `--force` option is required.

Verification for Milestone 5 passed with the local virtual environment: `.venv/bin/python -m pytest` collected 47 tests and all passed. The real example command `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` exited successfully. JSON validation with `.venv/bin/python -m json.tool timeline.json >/tmp/synccut_timeline_pretty.json` passed. Inspection showed `total_scenes: 33`, `total_sections: 7`, `total_duration_sec: 752.79`, `timeline_entries: 33`, first scene `scene_001` starting at 0.0 and ending at 9.137, and last scene `scene_033` ending at 752.79.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. At the time this plan was written, the repository contains documentation and example data but no source implementation. The files that define the requested behavior are:

- `AGENTS.md`, which defines project rules, MVP scope, preferred modules, visual type normalization, timing rules, matching rules, and testing expectations.
- `.agent/PLANS.md`, which defines how this ExecPlan must be written and maintained.
- `docs/architecture.md`, which describes the MVP pipeline: `scenes.json + audio/ + alignments/ -> synccut build-timeline -> timeline.json`.
- `docs/schemas.md`, which describes the expected shapes of `scenes.json`, alignment JSON, and `timeline.json`.
- `docs/matching.md`, which describes section-key discovery, audio and alignment file matching, text normalization, and timing math.
- `docs/testing.md`, which lists focused pytest coverage for scene loading, alignment loading, and timeline building.
- `docs/future-phases.md`, which names later Remotion, ffmpeg, validation, and asset-management work that must not be implemented in this MVP.
- `examples/scenes.json`, a real sample input with 33 scenes and metadata.
- `examples/audio/`, which contains seven section audio files named `01_HOOK.mp3`, `02_INTRO.mp3`, `03_MECHANISM_1.mp3`, `04_MECHANISM_2.mp3`, `05_MECHANISM_3.mp3`, `06_MECHANISM_4.mp3`, and `07_CONCLUSION.mp3`.
- `examples/alignments/`, which contains seven matching alignment files named like `01_HOOK_alignment_tmp.json`, one for each section key.

Important terms used in this plan:

A scene is one visual/narration unit from `scenes.json`. Each scene has a `scene_id`, ordering fields, a `section_key`, dialogue text, dialogue paragraphs, and visual instructions.

A section is a larger narration block such as `01_HOOK` or `02_INTRO`. Multiple scenes can share one section. Each section has one audio file and one alignment JSON file.

An alignment JSON file contains timestamps for spoken text. Its timestamps are local to the section, meaning the first word in each section starts near zero. The MVP converts these local timestamps to whole-video global timestamps by adding the total duration of all previous sections.

Global timing means seconds from the start of the full video. If section `02_INTRO` starts after the 18.39-second `01_HOOK` section, then a local timestamp of 2.0 seconds inside `02_INTRO` becomes global timestamp 20.39 seconds.

A dialogue match is the process of finding where a scene's dialogue appears in the alignment file for the same section. The match determines the scene's local start and end.

After Milestone 5, the current repository structure relevant to implementation is:

    synccut/
      __init__.py
      alignment_loader.py
      cli.py
      models.py
      scenes_loader.py
      timeline_builder.py
      validators.py
    tests/
      test_alignment_loader.py
      test_cli.py
      test_package.py
      test_scenes_loader.py
      test_timeline_builder.py
    pyproject.toml

The MVP implementation files are now present. Future phases should not add Remotion, ffmpeg, DOCX parsing, AI video generation, B-roll downloading, GUI, or web app logic unless explicitly requested.

Only create or edit these implementation and test files unless a later discovery makes another file necessary. Do not rewrite existing documentation except to keep this ExecPlan current.

## Expected Input Structure

The CLI accepts a positional `scenes_json` path and three options:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json

`scenes.json` must be a JSON object with a `metadata` object and a `scenes` array. `metadata.schema_version` should exist, and `metadata.total_scenes` must be numeric when present. `metadata.total_scenes` should equal the number of scene objects. Treat the file as read-only and do not write normalized content back to it.

Each scene must include:

- `scene_id`, a non-empty string.
- `scene_order`, a number used to order scenes.
- `section`, a non-empty string such as `HOOK`.
- `section_order`, a number used to order sections.
- `section_key`, a non-empty string such as `01_HOOK`. If it is missing, infer it from `section_order` and `section` by zero-padding `section_order` to two digits and appending an underscore plus an uppercase, underscore-normalized section name.
- `dialogue.text`, a non-empty string.
- `dialogue.paragraphs`, a non-empty array of non-empty strings when present. If it is absent, use `dialogue.text` as a single paragraph for matching.
- `visual.type`, a supported visual type. Supported normalized values are `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, and `TIMELINE`. Normalize input `B-ROLL` to `B_ROLL` internally and in generated output.
- `visual.prompt`, which may be a string or null.
- `visual.data`, which may be any JSON value or null and must be preserved.

Alignment JSON files must be JSON objects. The MVP uses:

- `total_duration_sec`, a positive number representing the full section duration.
- `paragraphs`, a non-empty array. Each paragraph must have `paragraph`, `start`, and `end`. `duration` is useful but can be recomputed as `end - start` if absent.
- Nested `paragraphs[].sentences`, when present, where each sentence has `sentence`, `start`, and `end`.
- `words`, when present, as a top-level word array. Each word must have `word`, `start`, and `end`. Nested sentence word arrays may also be used for word-span fallback.

Audio files are expected under `--audio-dir`. The preferred audio name for a section is `<section_key>.mp3`, such as `01_HOOK.mp3`.

Alignment files are expected under `--alignment-dir`. The preferred alignment pattern for a section is `<section_key>_alignment*.json`, such as `01_HOOK_alignment_tmp.json`.

## Expected timeline.json Output

The generated file must be deterministic, human-readable JSON with stable key ordering as far as practical. Use two-space indentation. The output should include top-level metadata, section references, timeline entries, and warnings. A concrete shape to implement is:

    {
      "metadata": {
        "schema_version": "1.0",
        "generated_by": "synccut build-timeline",
        "source_scenes": "examples/scenes.json",
        "total_scenes": 33,
        "total_sections": 5,
        "total_duration_sec": 123.456
      },
      "sections": [
        {
          "section_key": "01_HOOK",
          "section": "HOOK",
          "section_order": 1,
          "audio_path": "examples/audio/01_HOOK.mp3",
          "alignment_path": "examples/alignments/01_HOOK_alignment_tmp.json",
          "local_duration_sec": 18.39,
          "global_start_sec": 0.0,
          "global_end_sec": 18.39
        }
      ],
      "timeline": [
        {
          "scene_id": "scene_001",
          "scene_order": 1,
          "section": "HOOK",
          "section_order": 1,
          "section_key": "01_HOOK",
          "timing": {
            "start_sec": 0.0,
            "end_sec": 9.137,
            "duration_sec": 9.137,
            "local_start_sec": 0.0,
            "local_end_sec": 9.137
          },
          "audio": {
            "path": "examples/audio/01_HOOK.mp3"
          },
          "alignment": {
            "path": "examples/alignments/01_HOOK_alignment_tmp.json",
            "match_method": "paragraph",
            "matched_units": ["paragraph:0"]
          },
          "dialogue": {
            "text": "Every iPhone in your pocket...",
            "paragraphs": ["Every iPhone in your pocket..."]
          },
          "visual": {
            "type": "AI_VIDEO",
            "prompt": "Extreme close-up...",
            "data": null
          },
          "warnings": []
        }
      ],
      "warnings": []
    }

Paths may be written as strings relative to the current working directory when possible. If relative path computation is awkward because files are outside the working directory, absolute paths are acceptable, but tests should prefer temporary directories and assert behavior rather than exact absolute prefixes.

`metadata.total_duration_sec` must equal the end time of the final section, computed as the sum of alignment `total_duration_sec` values in section order. Each timeline entry's `duration_sec` must equal `end_sec - start_sec`. Use alignment duration as source of truth even if an audio file has a different real duration.

## Modules to Create or Edit

Create `pyproject.toml` if the repository still lacks one at implementation time. It should declare Python 3.11+, the `synccut` package, Typer as a runtime dependency, pytest as a test dependency or development dependency, and a console script named `synccut` that points to the CLI entry point. Keep this packaging minimal.

Create `synccut/__init__.py` with package metadata only if needed. It should not contain business logic.

Create `synccut/models.py` for lightweight shared data structures. Use standard-library `dataclasses` unless validation complexity clearly justifies Pydantic. Suggested dataclasses are `Scene`, `Dialogue`, `Visual`, `AlignmentSection`, `SectionAsset`, `MatchResult`, and `TimelineBuildResult`. These objects should represent already-validated internal data, not raw JSON.

Create `synccut/validators.py` for reusable validation and normalization helpers. Include visual type normalization, section key inference, text normalization, positive-number checks, and clear exception helpers.

Create `synccut/scenes_loader.py` for `load_scenes(path: Path) -> tuple[dict, list[Scene]]`. This module should read JSON, validate required fields, normalize `B-ROLL` to `B_ROLL`, infer missing `section_key` when possible, preserve dialogue and visual data, sort or validate scene order, and never mutate the input file.

Create `synccut/alignment_loader.py` for discovering and loading section assets. Suggested functions are `discover_audio_file(section_key: str, audio_dir: Path) -> Path`, `discover_alignment_file(section_key: str, alignment_dir: Path) -> Path`, `load_alignment(path: Path) -> AlignmentSection`, and `load_section_assets(scenes: list[Scene], audio_dir: Path, alignment_dir: Path) -> list[SectionAsset]`.

Create `synccut/timeline_builder.py` for pure timeline logic. Suggested functions are `build_timeline(scenes: list[Scene], sections: list[SectionAsset], source_scenes_path: Path) -> dict`, `match_scene_to_alignment(scene: Scene, alignment: AlignmentSection) -> MatchResult`, and small private helpers for paragraph, sentence, and word-span matching.

Create `synccut/cli.py` for Typer command wiring only. It should parse arguments, call loaders and builder functions, write JSON to `--out`, and translate known validation errors into clear CLI errors. Keep timeline logic out of this file.

Create tests in `tests/test_scenes_loader.py`, `tests/test_alignment_loader.py`, and `tests/test_timeline_builder.py`. Use small synthetic JSON fixtures in temporary directories. Do not rely on large production media files. Placeholder `.mp3` files are valid in tests because the MVP only checks discovery.

## Matching Strategy for Scenes to Alignment

Always match within the scene's own `section_key`. Never search another section for a scene's dialogue. First group scenes by section in ascending `section_order`, then `section_key`, then `scene_order`.

Normalize text before comparison by trimming leading and trailing whitespace, collapsing repeated whitespace to a single space, lowercasing, converting curly quotes to straight quotes, converting em dashes and en dashes to a plain hyphen or space consistently, and ignoring the arrow marker `⟶`. Preserve original text in output; normalization is only for matching.

The matching order is strict:

First, try paragraph matching. A scene may contain multiple dialogue paragraphs. Match each normalized scene paragraph against the normalized alignment paragraph text. If every scene paragraph can be matched to alignment paragraphs in order, the scene local start is the `start` of the first matched alignment paragraph and local end is the `end` of the last matched alignment paragraph. If the scene has one paragraph that is a contiguous substring of one alignment paragraph, accept that alignment paragraph only when sentence fallback cannot provide a narrower exact match. Record `match_method` as `paragraph`.

Second, try sentence fallback. Split or use alignment `sentences` nested inside paragraphs. Match the scene dialogue text, or each scene paragraph, against contiguous alignment sentences in order. This is needed because example `scene_001` has two scene paragraphs while the alignment may combine the same spoken text into one paragraph with multiple sentences. If the ordered sentences cover the normalized scene text, local start is the first sentence start and local end is the last sentence end. Record `match_method` as `sentence`.

Third, use word-span fallback only if paragraph and sentence matching fail. Word-span fallback means comparing normalized words from the scene dialogue to a contiguous span of alignment words. Strip surrounding punctuation for comparison but preserve timing from original alignment word objects. If exactly one contiguous word span matches, use its first word start and last word end. If no spans or multiple equally valid spans match, fail clearly. Record `match_method` as `word_span`.

Matching must be deterministic. If multiple candidate matches exist for the same scene, prefer the earliest candidate that occurs after the previous matched scene in the same section. Track the previous scene's local end per section to avoid matching repeated text backwards. If this still leaves ambiguity, raise an error instead of guessing.

Do not silently invent timing. If a scene cannot be matched to alignment data after all allowed strategies, raise a validation error that includes the `scene_id`, `section_key`, and a short excerpt of the dialogue.

## Audio and Alignment File Discovery Strategy

Derive the set of sections from loaded scenes. For each unique `section_key`, keep the first associated `section` and `section_order`, then sort sections by `section_order` and `section_key`.

For audio discovery, first check for the exact path `audio_dir / f"{section_key}.mp3"`. If it exists, use it. If it does not exist, search for `audio_dir.glob(f"{section_key}*.mp3")`. If there is exactly one fallback match, use it. If there are no matches, raise an error that says no audio file was found for that section. If there is more than one fallback match, raise an ambiguous audio error listing the matching filenames. Do not inspect the audio file contents.

For alignment discovery, search for `alignment_dir.glob(f"{section_key}_alignment*.json")`. If there is exactly one match, use it. If there are no matches, raise an error that says no alignment file was found for that section. If there is more than one match, raise an ambiguous alignment error listing the matching filenames.

Load each alignment file once per section. Validate that `total_duration_sec` is positive and that timing fields are numeric with `end >= start`. Build section offsets by accumulating sorted section durations:

    offset = 0.0 for the first section
    global_start_sec = offset
    global_end_sec = offset + total_duration_sec
    offset = global_end_sec for the next section

Use these section offsets for every scene in the section:

    scene_start = section_offset + local_start
    scene_end = section_offset + local_end
    duration = scene_end - scene_start

## Error Handling

Create a project exception such as `SyncCutError` or `ValidationError` in `validators.py` or `models.py`. Raise this exception for expected user-facing errors, including missing files, malformed JSON, invalid schemas, unsupported visual types, ambiguous discovery, invalid alignment timing, and unmatched dialogue.

The Typer CLI should catch known SyncCut errors and display concise messages without a Python traceback. It should exit with a non-zero status. Unexpected programming errors may still raise tracebacks during development.

Error messages should include the file path or scene identity needed to fix the problem. Good examples:

    scenes.json: metadata.total_scenes is 33 but scenes contains 32 items
    scene_003: unsupported visual type 'PHOTO'; expected one of AI_VIDEO, B_ROLL, CHART, COMPARISON_CARD, TABLE, SHARE_BREAKDOWN, TIMELINE
    01_HOOK: ambiguous audio files in examples/audio: 01_HOOK.mp3, 01_HOOK_take2.mp3
    scene_017 in 03_MECHANISM_1: could not match dialogue to alignment text

Warnings should be reserved for non-fatal normalization or recoverable conditions. In the initial MVP, it is acceptable for `warnings` arrays to be empty because strict errors handle invalid data. If a warning is emitted, it must also be represented in `timeline.json`.

## Tests to Write

`tests/test_scenes_loader.py` should cover valid scene loading, missing metadata, missing `scenes`, empty `scenes`, missing required scene fields, visual type normalization from `B-ROLL` to `B_ROLL`, unsupported visual types, section key inference from `section_order` and `section`, and proof that the input JSON file content is not mutated.

`tests/test_alignment_loader.py` should cover valid alignment loading, malformed JSON, missing `paragraphs`, missing timing fields, invalid negative or reversed timing, exact audio discovery, fallback audio discovery, missing audio, ambiguous audio matches, section-key alignment discovery, missing alignment, and ambiguous alignment matches.

`tests/test_timeline_builder.py` should cover paragraph matching, sentence fallback when scene paragraphs and alignment paragraphs do not have the same boundaries, word-span fallback for a small synthetic case, failure on unmatched dialogue, cumulative section offsets across at least two sections, correct global start/end/duration math, preservation of dialogue data, preservation and normalization of visual data, missing audio or alignment at build time, output JSON shape, and deterministic ordering by section and scene order.

Add at least one CLI-level test if practical using Typer's test runner. This should invoke `build-timeline` on a tiny temporary fixture and assert that the output file exists and contains expected timing. If Typer test-runner setup adds too much friction, keep CLI code thin and cover the behavior through loader and builder tests, then validate the real CLI manually with the example command.

## Plan of Work

Milestone 1 establishes the package skeleton and test runner. This milestone is complete: `pyproject.toml` declares the package, Typer dependency, pytest development dependency, and `synccut` console script; `synccut/__init__.py` makes the package importable; `synccut/cli.py` defines a Typer app and a placeholder `build-timeline` command; `tests/test_package.py` verifies package import and CLI help loading. No MVP data processing exists yet.

Milestone 2 implements scene loading. This milestone is complete: the dataclasses and validation helpers parse `scenes.json` into normalized internal objects. The acceptance proof is that focused scene-loader tests pass, visual type `B-ROLL` appears internally as `B_ROLL`, missing `section_key` values are inferred, and the original input file bytes remain unchanged.

Milestone 3 implements audio and alignment loading. This milestone is complete: deterministic section discovery, audio path discovery, alignment path discovery, and alignment JSON validation exist. The acceptance proof is that alignment-loader tests cover exact matches, fallback matches, missing files, ambiguous files, positive duration validation, non-empty paragraphs, invalid timing, sorted unique section assets, and placeholder `.mp3` files.

Milestone 4 implements timeline matching and timeline JSON construction. This milestone is complete: paragraph, sentence, and word-span matching run in that order; section offsets are computed from alignment durations; and the expected output object is produced. The acceptance proof is that timeline-builder tests demonstrate global timing, repeated-text previous-end behavior, preserved dialogue and visual data, visual normalization, output shape, deterministic ordering, and strict failure for unmatched dialogue.

Milestone 5 completes the Typer CLI wiring and validates the example data. This milestone is complete: `synccut/cli.py` calls the scene loader, alignment loader, and timeline builder, writes JSON, and formats known errors. The acceptance proof is that the target command writes `timeline.json` from `examples/`, JSON validation succeeds, inspection confirms the expected counts and timing, and the test suite passes.

Milestone 6 updates this ExecPlan's living sections. Record final test output, any deviations from the original design, and the exact changed files. Do not create a git commit unless explicitly asked.

## Concrete Steps

Run all commands from the repository root:

    cd /home/longnguyen/Desktop/AI/Codex/SyncCut

Before implementation, inspect the current tree:

    find . -maxdepth 3 -type f -print

Current implementation state after Milestone 1 is that `pyproject.toml`, `synccut/__init__.py`, `synccut/cli.py`, and `tests/test_package.py` exist. Later implementation should add the loader, model, validator, and timeline-builder modules without removing the scaffold.

The package skeleton and minimal packaging files have already been created. If `pyproject.toml` needs later edits, edit it conservatively instead of replacing it. It should continue to support Python 3.11+, Typer, pytest, and the `synccut` console script.

Implement `synccut/models.py`, `synccut/validators.py`, `synccut/scenes_loader.py`, `synccut/alignment_loader.py`, and `synccut/timeline_builder.py` in that order. Then update the existing `synccut/cli.py` placeholder to call those modules. Keep functions small enough that unit tests can call them without invoking the CLI.

Add tests in `tests/` as described above. Prefer pytest `tmp_path` fixtures and tiny JSON dictionaries written inside tests. Placeholder audio files can be created by writing a few bytes to a `.mp3` path because the MVP does not decode audio.

Run the full test suite. In an environment with a `python` executable, use:

    python -m pytest

In the current Milestone 1 environment, use the local virtual environment because bare `python` is not on PATH:

    .venv/bin/python -m pytest

If the console command is not available until the package is installed, install the package in editable mode in the active environment:

    python -m pip install -e .

In the current Milestone 1 environment, system Python is externally managed, so installation was performed with:

    python3 -m venv .venv
    .venv/bin/python -m pip install -e '.[dev]'

Then run the example command:

    synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Inspect the first part of the generated output:

    python -m json.tool timeline.json | sed -n '1,120p'

Expected observations are that `timeline.json` exists, top-level `metadata.total_scenes` is 33 for the provided example, the first section starts at 0.0, scene timings are global seconds, and visual type `B-ROLL` from input appears as `B_ROLL` in output.

If the implementation environment should not leave generated files in the repository, remove only generated `timeline.json` after validation. Do not remove source, docs, examples, or tests.

## Validation and Acceptance

The MVP is accepted when all of the following are true:

`python -m pytest` exits successfully. The exact number of tests will depend on implementation, but the suite must include coverage for scene loading, alignment loading, timeline building, and preferably the CLI command.

The command below exits successfully:

    synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

The generated `timeline.json` is valid JSON and contains:

- `metadata.generated_by` equal to `synccut build-timeline`.
- `metadata.total_scenes` equal to 33 for `examples/scenes.json`.
- A `sections` array with one entry per discovered section.
- A `timeline` array with one entry per input scene.
- For every timeline scene, `timing.start_sec`, `timing.end_sec`, `timing.duration_sec`, `timing.local_start_sec`, and `timing.local_end_sec`.
- For every timeline scene, an `audio.path` and `alignment.path`.
- For every timeline scene, `alignment.match_method` equal to one of `paragraph`, `sentence`, or `word_span`.
- Dialogue and visual data preserved from input, except visual type normalization from `B-ROLL` to `B_ROLL`.
- No invented timing for unmatched dialogue.

A quick JSON validation command should succeed:

    python -m json.tool timeline.json >/tmp/synccut_timeline_pretty.json

If a scene is intentionally changed in a test fixture so its dialogue does not occur in the alignment, the builder or CLI must fail clearly with a message containing the scene id and section key.

## Idempotence and Recovery

The implementation should be safe to run repeatedly. Re-running `synccut build-timeline ... --out timeline.json` may overwrite the output file, but it must not modify `scenes.json`, audio files, or alignment files.

If tests fail, fix the implementation and rerun `python -m pytest`. Do not delete tests to make the suite pass. If example validation creates `timeline.json`, it is a generated artifact and can be removed after verification.

If package installation with `python -m pip install -e .` fails because dependencies are missing or network access is unavailable, record the failure in `Surprises & Discoveries`. The code should still be structured so tests can run in an environment where Typer and pytest are installed.

Do not use destructive git commands. Do not run `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, or `git rebase` unless the user explicitly asks.

## Artifacts and Notes

Repository inspection at plan creation showed:

    ./examples/scenes.json
    ./examples/alignments/01_HOOK_alignment_tmp.json
    ./examples/alignments/02_INTRO_alignment_tmp.json
    ./examples/alignments/03_MECHANISM_1_alignment_tmp.json
    ./examples/alignments/04_MECHANISM_2_alignment_tmp.json
    ./examples/alignments/05_MECHANISM_3_alignment_tmp.json
    ./examples/alignments/06_MECHANISM_4_alignment_tmp.json
    ./examples/alignments/07_CONCLUSION_alignment_tmp.json
    ./examples/audio/01_HOOK.mp3
    ./examples/audio/02_INTRO.mp3
    ./examples/audio/03_MECHANISM_1.mp3
    ./examples/audio/04_MECHANISM_2.mp3
    ./examples/audio/05_MECHANISM_3.mp3
    ./examples/audio/06_MECHANISM_4.mp3
    ./examples/audio/07_CONCLUSION.mp3

Example `scenes.json` metadata at plan creation:

    {
      "project_id": "tsmc_the_sand_alchemists",
      "title": "The Sand Alchemists: How TSMC Quietly Controls the Global Economy",
      "language": "American English",
      "runtime": "12–15 minutes",
      "source_docx": "TSMC_TheSandAlchemists_USMarketData.docx",
      "total_scenes": 33,
      "schema_version": "1.1"
    }

Example alignment fields at plan creation:

    total_duration_sec: 18.39
    total_paragraphs: 3
    top-level keys include paragraphs, words, total_duration_sec, total_words, total_sentences, total_paragraphs

Milestone 1 verification transcript:

    $ python -m pytest
    zsh:1: command not found: python

    $ python3 -m pytest
    /usr/bin/python3: No module named pytest

    $ .venv/bin/python -m pytest
    collected 3 items
    tests/test_package.py ...                                                [100%]
    3 passed in 0.17s

Milestone 1 CLI shape check:

    $ .venv/bin/synccut --help
    Usage: synccut [OPTIONS] COMMAND [ARGS]...
    Commands:
      build-timeline  Build timeline.json from scenes, audio references, and alignment timestamps.

    $ .venv/bin/synccut build-timeline --help
    Usage: synccut build-timeline [OPTIONS] SCENES_JSON
    Options include --audio-dir, --alignment-dir, and --out.

Milestone 2 verification transcript:

    $ .venv/bin/python -m pytest
    collected 17 items
    tests/test_package.py ...                                                [ 17%]
    tests/test_scenes_loader.py ..............                               [100%]
    17 passed in 0.20s

Milestone 3 verification transcript:

    $ .venv/bin/python -m pytest
    collected 33 items
    tests/test_alignment_loader.py ................                          [ 48%]
    tests/test_package.py ...                                                [ 57%]
    tests/test_scenes_loader.py ..............                               [100%]
    33 passed in 0.23s

Milestone 3 real fixture smoke check:

    $ .venv/bin/python -c 'from pathlib import Path; from synccut.scenes_loader import load_scenes; from synccut.alignment_loader import load_section_assets; _, scenes = load_scenes(Path("examples/scenes.json")); assets = load_section_assets(scenes, Path("examples/audio"), Path("examples/alignments")); print(len(assets)); print([a.section_key for a in assets])'
    7
    ['01_HOOK', '02_INTRO', '03_MECHANISM_1', '04_MECHANISM_2', '05_MECHANISM_3', '06_MECHANISM_4', '07_CONCLUSION']

Milestone 4 verification transcript:

    $ .venv/bin/python -m pytest
    collected 45 items
    tests/test_alignment_loader.py ................                          [ 35%]
    tests/test_package.py ...                                                [ 42%]
    tests/test_scenes_loader.py ..............                               [ 73%]
    tests/test_timeline_builder.py ............                              [100%]
    45 passed in 0.26s

Milestone 4 real fixture smoke check:

    $ .venv/bin/python -c 'from pathlib import Path; from synccut.scenes_loader import load_scenes; from synccut.alignment_loader import load_section_assets; from synccut.timeline_builder import build_timeline; _, scenes = load_scenes(Path("examples/scenes.json")); sections = load_section_assets(scenes, Path("examples/audio"), Path("examples/alignments")); timeline = build_timeline(scenes, sections, Path("examples/scenes.json")); print(timeline["metadata"]["total_scenes"]); print(timeline["metadata"]["total_sections"]); print(round(timeline["metadata"]["total_duration_sec"], 3)); print(timeline["timeline"][0]["scene_id"], timeline["timeline"][0]["alignment"]["match_method"]); print(timeline["timeline"][-1]["scene_id"], timeline["timeline"][-1]["timing"]["end_sec"])'
    33
    7
    752.79
    scene_001 sentence
    scene_033 752.79

Milestone 5 verification transcript:

    $ .venv/bin/python -m pytest
    collected 47 items
    tests/test_alignment_loader.py ................                          [ 34%]
    tests/test_cli.py ..                                                     [ 38%]
    tests/test_package.py ...                                                [ 44%]
    tests/test_scenes_loader.py ..............                               [ 74%]
    tests/test_timeline_builder.py ............                              [100%]
    47 passed in 0.33s

    $ .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

    $ .venv/bin/python -m json.tool timeline.json >/tmp/synccut_timeline_pretty.json

    $ .venv/bin/python - <<'PY'
    import json
    from pathlib import Path
    data = json.loads(Path("timeline.json").read_text())
    print("total_scenes:", data["metadata"]["total_scenes"])
    print("total_sections:", data["metadata"]["total_sections"])
    print("total_duration_sec:", data["metadata"]["total_duration_sec"])
    print("timeline_entries:", len(data["timeline"]))
    print("first_scene:", data["timeline"][0]["scene_id"], data["timeline"][0]["timing"])
    print("last_scene:", data["timeline"][-1]["scene_id"], data["timeline"][-1]["timing"])
    PY
    total_scenes: 33
    total_sections: 7
    total_duration_sec: 752.79
    timeline_entries: 33
    first_scene: scene_001 {'start_sec': 0.0, 'end_sec': 9.137, 'duration_sec': 9.137, 'local_start_sec': 0.0, 'local_end_sec': 9.137}
    last_scene: scene_033 {'start_sec': 713.095, 'end_sec': 752.79, 'duration_sec': 39.694999999999936, 'local_start_sec': 109.052, 'local_end_sec': 148.747}

Future-phase exclusions are explicit. Do not add DOCX parsing, Remotion export, Remotion rendering, ffmpeg assembly, AI video generation, B-roll downloading, GUI code, web app code, or final MP4 assembly while implementing this plan.

## Interfaces and Dependencies

Use Python 3.11 or newer.

Use `pathlib.Path` for filesystem paths.

Use standard-library `json` for JSON parsing and writing.

Use Typer for the CLI. The end-user command must be:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json

Use pytest for tests. Tests must be runnable with:

    python -m pytest

Prefer dataclasses and explicit validation helpers. Use Pydantic only if schema validation becomes clearly useful enough to justify the dependency. Do not add ffmpeg, Remotion, browser, video, AI-generation, or download dependencies for this MVP.

The following functions or equivalents should exist at the end of implementation:

    synccut.scenes_loader.load_scenes(path: Path) -> tuple[dict, list[Scene]]
    synccut.alignment_loader.discover_audio_file(section_key: str, audio_dir: Path) -> Path
    synccut.alignment_loader.discover_alignment_file(section_key: str, alignment_dir: Path) -> Path
    synccut.alignment_loader.load_alignment(path: Path) -> AlignmentSection
    synccut.alignment_loader.load_section_assets(scenes: list[Scene], audio_dir: Path, alignment_dir: Path) -> list[SectionAsset]
    synccut.timeline_builder.match_scene_to_alignment(scene: Scene, alignment: AlignmentSection) -> MatchResult
    synccut.timeline_builder.build_timeline(scenes: list[Scene], sections: list[SectionAsset], source_scenes_path: Path) -> dict

The exact dataclass field names may change during implementation if tests and output behavior remain clear, but the module responsibilities and CLI behavior should remain as described here.

## Revision Note

2026-05-09 / Codex: Initial ExecPlan created after reading required project instructions and documentation. The plan records current repository orientation, expected input and output shapes, implementation modules, matching and discovery strategies, error handling, tests, validation commands, milestones, and explicit MVP exclusions.

2026-05-10 / Codex: Updated after Milestone 1 implementation. The repository now has minimal packaging, an importable package, Typer CLI scaffolding, and smoke tests. The update also records that the example fixture set now has seven complete sections and that tests pass through the local `.venv` because bare `python` is unavailable in this shell.

2026-05-10 / Codex: Updated after Milestone 2 implementation. The repository now has scene dataclasses, scene validation helpers, `load_scenes`, and focused scene-loader tests. The update records the dataclass and fallback decisions, the continued CLI placeholder boundary, and the passing `.venv/bin/python -m pytest` result.

2026-05-10 / Codex: Updated after Milestone 3 implementation. The repository now has audio discovery, alignment discovery, alignment JSON loading and validation, sorted section asset derivation, and focused alignment-loader tests. The update records model/path decisions, the continued CLI placeholder boundary, the passing `.venv/bin/python -m pytest` result, and a smoke check against the complete example fixture set.

2026-05-10 / Codex: Updated after Milestone 4 implementation. The repository now has strict scene-to-alignment matching, text normalization, previous-end tracking during timeline construction, section offset calculation, timeline JSON dictionary construction, and focused timeline-builder tests. The update records matching decisions, the continued CLI placeholder boundary, the passing `.venv/bin/python -m pytest` result, and an in-memory smoke check against the complete example fixture set.

2026-05-10 / Codex: Updated after Milestone 5 implementation. The repository now has the target Typer command wired to the existing loaders and timeline builder, CLI tests for success and known validation failure, deterministic JSON file output, and real-example validation. The update records CLI boundary and overwrite decisions, the passing `.venv/bin/python -m pytest` result, JSON validation, and inspection output for `timeline.json`.
