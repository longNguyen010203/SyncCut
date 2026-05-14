# Audio and alignment generation design

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to design and implement the local, provider-agnostic audio/alignment generation foundation from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut v0.1.0 can build timelines and render videos when section narration audio files and alignment JSON files already exist. The next useful step is to make it easier to prepare those inputs from an existing `scenes.json` without immediately integrating with an external text-to-speech provider. After this plan is complete, a user should be able to run a local SyncCut command that reads `scenes.json`, groups narration by section, and writes a predictable narration package that a later provider such as ElevenLabs can consume.

This phase deliberately does not generate audio, call ElevenLabs, require API keys, or create alignment timings from audio. It establishes a stable local contract: section narration text, output naming, hashes for cache safety, dry-run reporting, and overwrite policy. The observable result is a command that produces a manifest and per-section text files from the sample scenes and can be validated with tests.

## Progress

- [x] (2026-05-14T15:20:00+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `README.md` context from Phase 26, `pyproject.toml`, `synccut/cli.py`, `synccut/scenes_loader.py`, `synccut/alignment_loader.py`, `synccut/timeline_builder.py`, `synccut/models.py`, `examples/scenes.json`, current example audio/alignment filenames, `.gitignore`, and `git status --short --ignored`.
- [x] (2026-05-14T15:20:00+07:00) Created this Phase 29 ExecPlan.
- [x] (2026-05-14T15:35:00+07:00) Milestone 1: Audited current scenes, audio, alignment, and timeline input contract without editing source.
- [x] (2026-05-14T15:50:00+07:00) Milestone 2: Finalized the narration package command contract, manifest shape, hash/cache behavior, dry-run behavior, overwrite behavior, provider boundary, implementation files, and tests.
- [x] (2026-05-14T16:10:00+07:00) Milestone 3: Implemented the local narration package command and focused tests.
- [x] (2026-05-14T16:25:00+07:00) Milestone 4: Validated `prepare-narration` with the sample workflow, idempotent rerun, unchanged build-timeline behavior, and Remotion typecheck.
- [x] (2026-05-14T16:40:00+07:00) Milestone 5: Completed docs/ignore decision, cleaned generated narration validation output, ran final validation, reviewed artifacts, and recorded commit recommendation.

## Surprises & Discoveries

- Observation: Current build-timeline still requires prepared section audio and prepared section alignment files.
  Evidence: `synccut/cli.py` calls `load_section_assets(scenes, audio_dir, alignment_dir)` before `build_timeline_data`. `synccut/alignment_loader.py` discovers audio with `<section_key>.mp3` or `<section_key>*.mp3`, and discovers alignment with `<section_key>_alignment*.json`.
- Observation: `scenes.json` already contains enough narration text to build a section-level narration package.
  Evidence: Each scene in `examples/scenes.json` has `section_key`, `section`, `section_order`, `scene_id`, `scene_order`, `dialogue.text`, and `dialogue.paragraphs`. `synccut/scenes_loader.py` validates and normalizes these into `Scene` objects.
- Observation: The current examples use `*_alignment_tmp.json` for alignment filenames.
  Evidence: Example alignment files include `examples/alignments/01_HOOK_alignment_tmp.json` through `examples/alignments/07_CONCLUSION_alignment_tmp.json`.
- Observation: There is currently no ignored path for a generated narration package.
  Evidence: `.gitignore` ignores `timeline.json`, `examples`, `assets/visuals/`, `remotion/public`, `remotion/out/`, virtualenvs, node modules, and caches, but does not list `generated/` or `narration/`.
- Observation: Current tracked working tree is clean at plan creation time.
  Evidence: `git status --short --ignored` showed only ignored generated/local paths: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: The sample `scenes.json` has 33 scenes across 7 sections.
  Evidence: `metadata.total_scenes` is `33`. The repeated `section_key` fields group into `01_HOOK`, `02_INTRO`, `03_MECHANISM_1`, `04_MECHANISM_2`, `05_MECHANISM_3`, `06_MECHANISM_4`, and `07_CONCLUSION`.
- Observation: Scene section identity and ordering fields are already explicit.
  Evidence: Each audited scene contains `scene_id`, `scene_order`, `section`, `section_order`, and `section_key`. The section display/name field is `section`, and the stable section identifier used for filenames and grouping is `section_key`.
- Observation: Narration text exists at both scene and paragraph levels.
  Evidence: Each audited scene has `dialogue.text` and `dialogue.paragraphs`. `synccut/scenes_loader.py` requires `dialogue.text`; if `dialogue.paragraphs` is omitted or null, it uses `[text]`, but if present it must be a non-empty array of non-empty strings.
- Observation: Paragraph boundaries are useful but not always identical to `dialogue.text` sentence grouping.
  Evidence: Scene `scene_001` has one `dialogue.text` string and two `dialogue.paragraphs`; scene `scene_006` has one long `dialogue.text` and three paragraphs. Narration extraction should preserve paragraph boundaries rather than flattening everything into one line.
- Observation: Current section audio naming is exact-first with a fallback.
  Evidence: `discover_audio_file` first checks `<audio_dir>/<section_key>.mp3`; if absent, it accepts exactly one matching `<section_key>*.mp3`. Current examples are exact names: `01_HOOK.mp3`, `02_INTRO.mp3`, `03_MECHANISM_1.mp3`, `04_MECHANISM_2.mp3`, `05_MECHANISM_3.mp3`, `06_MECHANISM_4.mp3`, and `07_CONCLUSION.mp3`.
- Observation: Current section alignment naming accepts the existing temporary suffix.
  Evidence: `discover_alignment_file` accepts exactly one `<section_key>_alignment*.json`. Current examples are `01_HOOK_alignment_tmp.json`, `02_INTRO_alignment_tmp.json`, `03_MECHANISM_1_alignment_tmp.json`, `04_MECHANISM_2_alignment_tmp.json`, `05_MECHANISM_3_alignment_tmp.json`, `06_MECHANISM_4_alignment_tmp.json`, and `07_CONCLUSION_alignment_tmp.json`.
- Observation: `build-timeline` loads audio/alignment assets before it builds any timeline entries.
  Evidence: In `synccut/cli.py`, `build_timeline` loads scenes, then calls `load_section_assets(scenes, audio_dir, alignment_dir)`, then calls `build_timeline_data(scenes, sections, scenes_json)`. In `synccut/timeline_builder.py`, every timeline scene requires a matching `SectionAsset`, and missing section assets raise `SyncCutError`.
- Observation: Narration extraction can be section-local and deterministic.
  Evidence: `load_section_assets` already groups sections by scene `section_key` and sorts by `(section_order, section_key)`. `build_timeline` sorts scenes by `(section_order, section_key, scene_order)`. A narration package should use the same ordering rule.
- Observation: `generated/` and `generated/narration/` are not ignored today.
  Evidence: `.gitignore` does not list `generated/`; `git status --short --ignored` did not show `generated/` because no generated narration package exists.
- Observation: A full 64-character SHA-256 hash is better than a short hash for the manifest.
  Evidence: The manifest is a machine-readable cache contract for future providers, not a compact human status line. Full hashes avoid accidental ambiguity and still remain readable enough in JSON.
- Observation: Storing both `narration_text` and `text_path` is intentionally redundant.
  Evidence: Future providers can consume `text_path` directly, while reviewers and tests can inspect one manifest file without opening every section text file. The redundancy is safe because tests can require exact equality between each text file and the manifest text.
- Observation: Generated package output should be local by default and not committed accidentally.
  Evidence: The chosen sample validation path is `generated/narration`, but `.gitignore` does not currently ignore `generated/`. Milestone 5 should add an ignore rule if generated validation output is kept as a normal workflow artifact; otherwise generated output must be cleaned before final review.
- Observation: The implementation matched the Milestone 2 design without requiring schema or dependency changes.
  Evidence: Added `synccut/narration_package.py`, wired `prepare-narration` in `synccut/cli.py`, added tests in `tests/test_narration_package.py` and `tests/test_cli.py`, and did not edit timeline schema, Remotion props schema, README, `.gitignore`, or package dependencies.
- Observation: The file-count summary treats the manifest as a planned package file.
  Evidence: Tests expect one-section package creation to report `written: 2` and dry-run `would_create: 2`, covering the section text file plus `narration_manifest.json`.
- Observation: Full test coverage increased with focused narration package tests.
  Evidence: `.venv/bin/python -m pytest` collected 227 tests and passed all 227.
- Observation: Dry-run reports the full package plan and writes nothing.
  Evidence: `.venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration --dry-run` reported `sections: 7`, `scenes: 33`, `would_create: 8`, `would_reuse: 0`, `would_block: 0`, and manifest path `generated/narration/narration_manifest.json`. A subsequent `find generated/narration -maxdepth 1 -type f` reported that the directory did not exist.
- Observation: Real sample package generation produced the expected file set.
  Evidence: `find generated/narration -maxdepth 1 -type f | sort` showed seven section text files, `01_HOOK.txt` through `07_CONCLUSION.txt`, plus `narration_manifest.json`.
- Observation: The sample manifest has the expected metadata and section fields.
  Evidence: `generated/narration/narration_manifest.json` reported `schema_version: 0.1`, `generated_by: synccut prepare-narration`, `source_scenes: examples/scenes.json`, `total_sections: 7`, and `total_scenes: 33`. The `01_HOOK` section included `section_key`, `section`, `section_order`, `scene_ids`, `scene_count`, `text_path`, `narration_text`, `text_hash`, `expected_audio_path: 01_HOOK.mp3`, and `expected_alignment_path: 01_HOOK_alignment_tmp.json`.
- Observation: The sample text output preserves readable paragraph boundaries.
  Evidence: `sed -n '1,120p' generated/narration/01_HOOK.txt` showed the three HOOK scenes' narration with blank lines between paragraphs and scene text.
- Observation: Idempotent rerun reused all planned files.
  Evidence: A second `prepare-narration examples/scenes.json --out-dir generated/narration` reported `written: 0` and `reused: 8`.
- Observation: Existing `build-timeline` behavior remains intact.
  Evidence: `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` succeeded with 7 sections, 33 scenes, duration 752.79, and `warnings: 0`; `validate-timeline timeline.json` reported `warnings: 0`.
- Observation: Remotion typecheck still passes.
  Evidence: `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`.
- Observation: A short README command note is enough for Phase 29.
  Evidence: README already has a Python command summary, so adding a single `prepare-narration` bullet documents the new command without over-documenting the manifest shape or future provider details.
- Observation: `generated/` should be ignored as a local output root.
  Evidence: Milestone 4 created `generated/narration/` as validation output. Adding `generated/` to `.gitignore` prevents future local narration packages from becoming commit candidates while preserving the ability to add explicit fixtures elsewhere if needed.
- Observation: Targeted cleanup removed sample narration output.
  Evidence: `rm -rf generated/narration` followed by `rmdir generated` removed the generated validation package directory. No generated narration output remained in the final focused status.
- Observation: Final validation passed.
  Evidence: `.venv/bin/python -m pytest` passed with 227 tests, and `cd remotion && npm run typecheck` passed.
- Observation: Final artifact status has only expected non-generated candidates.
  Evidence: `git status --short --ignored` showed modified `.gitignore`, `README.md`, `synccut/cli.py`, and `tests/test_cli.py`, plus untracked `docs/plans/audio-alignment-generation-design.md`, `synccut/narration_package.py`, and `tests/test_narration_package.py`. Ignored local/generated paths include `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `__pycache__/`, and `timeline.json`.

## Decision Log

- Decision: Phase 29 will not focus on DOCX or script input.
  Rationale: The user confirmed that `scenes.json` can be created quickly with AI. The next bottleneck is prepared narration audio and alignment assets, so this plan starts from `scenes.json`.
  Date/Author: 2026-05-14 / Codex
- Decision: Phase 29 will be provider-agnostic and local-only.
  Rationale: The user explicitly reserved ElevenLabs integration for Phase 30 and said not to call ElevenLabs or require API keys in this phase.
  Date/Author: 2026-05-14 / Codex
- Decision: The likely command name for implementation is `prepare-narration`.
  Rationale: It matches existing `prepare-remotion-assets` and `prepare-visual-assets` naming while accurately describing that the command prepares local narration text and manifest artifacts, not audio or alignment files.
  Date/Author: 2026-05-14 / Codex
- Decision: The implementation should prefer a generated package under `generated/narration/` for manual validation, with `.gitignore` updated if that path is used.
  Rationale: The command writes local planning artifacts that should not be accidentally committed by default. `generated/narration/` is explicit and leaves room for later generated audio/alignment packages without overloading existing `examples/`.
  Date/Author: 2026-05-14 / Codex
- Decision: Preserve the existing `build-timeline` contract in Phase 29.
  Rationale: The audit confirmed that `build-timeline` currently requires `scenes.json`, an audio directory, and an alignment directory. Phase 29 should add a local planning/preparation command for future generation, not change timeline building or make narration packages a timeline input.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 2 should design the narration package from `scenes.json`, not real audio or alignment generation.
  Rationale: `scenes.json` contains enough section, scene, and dialogue data to create a provider-ready text package. Audio synthesis and timed alignment data require provider behavior and are explicitly deferred to Phase 30.
  Date/Author: 2026-05-14 / Codex
- Decision: The command name is `prepare-narration`.
  Rationale: The command prepares local narration text and a manifest for future provider use. The name fits the existing `prepare-remotion-assets` and `prepare-visual-assets` command family while avoiding claims that it generates audio or alignment.
  Date/Author: 2026-05-14 / Codex
- Decision: The CLI shape is `synccut prepare-narration SCENES_JSON --out-dir generated/narration [--dry-run] [--overwrite]`.
  Rationale: `SCENES_JSON` should be a required positional argument, like `build-timeline`. `--out-dir` should be required so users consciously choose where generated planning artifacts go. `--dry-run` and `--overwrite` are the only options needed for safe local planning.
  Date/Author: 2026-05-14 / Codex
- Decision: `--dry-run` writes nothing and reports what would happen.
  Rationale: Dry-run is useful before provider generation and before overwriting files. It should compute sections, hashes, and planned paths, then report `would_create`, `would_reuse`, and `would_block` counts without creating `out_dir`, text files, or the manifest.
  Date/Author: 2026-05-14 / Codex
- Decision: Existing differing files block by default, and `--overwrite` replaces only planned package files inside `out_dir`.
  Rationale: Narration text and manifest files are local planning artifacts that may be hand-reviewed. Safe default behavior prevents accidental replacement. `--overwrite` is explicit and scoped to the manifest and `<section_key>.txt` files produced by this command.
  Date/Author: 2026-05-14 / Codex
- Decision: Sections are grouped by `section_key`, sections are sorted by `(section_order, section_key)`, and scenes within each section are sorted by `(scene_order, scene_id)`.
  Rationale: This matches the current asset loading and timeline-building ordering patterns and gives deterministic output even if input scene order is shuffled.
  Date/Author: 2026-05-14 / Codex
- Decision: Narration text is assembled from `dialogue.paragraphs`, not by rewriting `dialogue.text`.
  Rationale: `dialogue.paragraphs` preserves provider-friendly narration boundaries. Paragraphs are joined with blank lines, and scenes are also joined with blank lines. The command does no text rewriting, summarization, translation, or AI generation.
  Date/Author: 2026-05-14 / Codex
- Decision: The manifest stores relative paths and full hashes.
  Rationale: Relative paths keep the package portable. `text_hash` uses `sha256:<full64hex>` from the exact `narration_text` encoded as UTF-8, which is stable for cache safety.
  Date/Author: 2026-05-14 / Codex
- Decision: Expected future output names are `<section_key>.mp3` and `<section_key>_alignment_tmp.json`.
  Rationale: `<section_key>.mp3` matches the current exact audio discovery path. `<section_key>_alignment_tmp.json` matches current examples and the current `<section_key>_alignment*.json` discovery rule, preserving compatibility until a later phase explicitly changes naming.
  Date/Author: 2026-05-14 / Codex
- Decision: Phase 30 provider integration consumes the manifest and text files but is not implemented here.
  Rationale: The manifest gives Phase 30 section metadata, narration text, `text_path`, expected output paths, and `text_hash`. This phase remains local-only and does not add an ElevenLabs client, API keys, network calls, audio synthesis, or alignment generation.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 3 implementation files are `synccut/narration_package.py`, `synccut/cli.py`, `tests/test_narration_package.py`, `tests/test_cli.py`, and this plan.
  Rationale: The core behavior should be testable without Typer in a new pure module. CLI code should remain thin. Existing CLI tests should cover command wiring and output.
  Date/Author: 2026-05-14 / Codex
- Decision: `.gitignore` should be decided in Milestone 5 unless generated output is required before then.
  Rationale: Milestone 3 can implement behavior and tests without creating persistent generated sample output. Milestone 4 will create sample output for validation, and Milestone 5 can either clean it or add a narrow ignore rule such as `generated/`.
  Date/Author: 2026-05-14 / Codex
- Decision: Add a concise README command-summary note for `prepare-narration`.
  Rationale: The command is now user-facing. README should mention that it creates a local narration manifest/text package and explicitly does not call ElevenLabs or generate audio/alignment yet. A single bullet is enough because detailed manifest behavior lives in this plan and command help.
  Date/Author: 2026-05-14 / Codex
- Decision: Add `generated/` to `.gitignore`.
  Rationale: Phase 29 validation uses `generated/narration/`, and future local generation packages should not appear as commit candidates by default. Tests use temporary directories, so this ignore rule does not hide intended tracked fixtures.
  Date/Author: 2026-05-14 / Codex
- Decision: Clean generated narration validation output before final review.
  Rationale: The generated sample package proved the behavior in Milestone 4 but is not intended as a tracked fixture or release artifact.
  Date/Author: 2026-05-14 / Codex

## Outcomes & Retrospective

This plan has been created but not implemented. No source code, tests, README, schemas, command behavior, generated audio, generated alignment, external API calls, media, render outputs, commits, tags, or pushes were created while authoring the plan.

The intended outcome is a safe local foundation for Phase 30. Phase 29 should produce a deterministic narration package from `scenes.json`, plus tests and documentation for the command behavior. It should leave the existing timeline build workflow unchanged: `build-timeline` still consumes prepared audio and alignment files.

Milestone 1 is complete. The audit confirmed that `examples/scenes.json` has 33 scenes across 7 section keys, with all required fields for section-level narration extraction: `section_key`, `section`, `section_order`, `scene_id`, `scene_order`, `dialogue.text`, and `dialogue.paragraphs`. Paragraph arrays exist in the sample and should be preserved in Milestone 2's package design because they provide useful provider-facing narration boundaries.

The current asset contract is exact and compatible with the planned output names. Audio discovery prefers `<section_key>.mp3` and falls back to one `<section_key>*.mp3`; alignment discovery accepts one `<section_key>_alignment*.json`. The current examples use exact audio names and `_alignment_tmp.json` alignment names. `build-timeline` still depends on prepared audio and alignment assets, so Phase 29 must add a preparatory command without changing that contract.

Artifact review found no current ignore rule for `generated/` or `generated/narration/`, so Milestone 2 must decide whether generated narration validation output should be cleaned each time or whether `.gitignore` should be updated in Milestone 5. The next step is Milestone 2: design the narration package and generation contract in detail before any implementation.

Milestone 2 is complete. The final implementation design is:

- Command: `synccut prepare-narration SCENES_JSON --out-dir generated/narration [--dry-run] [--overwrite]`.
- Generated files: `narration_manifest.json` plus one `<section_key>.txt` file per section.
- Expected future provider outputs recorded in the manifest: `<section_key>.mp3` and `<section_key>_alignment_tmp.json`.
- Manifest hash: `sha256:<full64hex>` of exact `narration_text` encoded as UTF-8.
- Paths in manifest: relative to the package root.
- Idempotence: create missing files, reuse identical files, block differing files unless `--overwrite` is passed, and replace only planned package files on overwrite.
- Dry-run: write nothing and report planned create/reuse/block counts.
- Provider boundary: no ElevenLabs, no API keys, no network, no audio, and no generated alignment in Phase 29.

The next step is Milestone 3: implement `synccut/narration_package.py`, wire `prepare-narration` into `synccut/cli.py`, add focused tests in `tests/test_narration_package.py` and `tests/test_cli.py`, and update this plan with implementation evidence.

Milestone 3 is complete. Implementation summary:

- Added `synccut/narration_package.py` with pure, testable package logic.
- Added `NarrationSection` and `NarrationPackageResult` dataclasses.
- Implemented deterministic section grouping by `section_key`, section sorting by `(section_order, section_key)`, scene sorting by `(scene_order, scene_id)`, paragraph-preserving narration assembly, full SHA-256 text hashes, and expected future audio/alignment paths.
- Implemented deterministic manifest generation with `indent=2`, `ensure_ascii=False`, and a trailing newline.
- Implemented create/reuse/block/overwrite behavior for planned package files.
- Implemented dry-run behavior that writes nothing and reports create/reuse/block counts.
- Added `synccut prepare-narration SCENES_JSON --out-dir OUT_DIR [--dry-run] [--overwrite]` in `synccut/cli.py`.
- Added focused unit tests in `tests/test_narration_package.py`.
- Added CLI tests for success output, dry-run output, and blocked output in `tests/test_cli.py`.

Validation result: `.venv/bin/python -m pytest` passed with 227 tests. No ElevenLabs calls, API keys, audio generation, alignment generation, media downloads, ffmpeg/ffprobe, media probing, rendering, DOCX parsing, B-roll downloading, timeline schema changes, Remotion props schema changes, README edits, `.gitignore` edits, commits, tags, pushes, or Phase 30 work were performed.

The next step is Milestone 4: validate the new command against the sample under a local generated path, confirm the manifest/text output, confirm `build-timeline` remains unchanged, and run Remotion typecheck.

Milestone 4 is complete. Sample validation summary:

- `.venv/bin/python -m pytest` passed with 227 tests.
- Dry-run against `examples/scenes.json` wrote no files and reported 7 sections, 33 scenes, 8 planned creations, 0 planned reuses, and 0 planned blocks.
- Real package generation wrote `generated/narration/narration_manifest.json` and 7 section text files.
- Manifest inspection confirmed the expected metadata and section fields, including full text hashes, relative text paths, expected audio paths, and expected `_alignment_tmp.json` paths.
- `01_HOOK.txt` preserved readable narration paragraph boundaries.
- Idempotent rerun reported `written: 0` and `reused: 8`.
- Existing `build-timeline` with `examples/audio` and `examples/alignments` still works and `validate-timeline` reports `warnings: 0`.
- `cd remotion && npm run typecheck` passed.

Generated local validation artifacts now exist at `generated/narration/`, and `timeline.json` was regenerated. Milestone 5 should decide whether to ignore or remove `generated/narration/`, should treat `timeline.json` as generated/ignored, and should perform final artifact review. No README or `.gitignore` edits were made in Milestone 4.

Milestone 5 is complete. Phase 29 final summary:

- Implemented `synccut prepare-narration SCENES_JSON --out-dir OUT_DIR [--dry-run] [--overwrite]`.
- Added provider-agnostic narration package logic in `synccut/narration_package.py`.
- Added tests for grouping, ordering, paragraph-preserving text assembly, full SHA-256 hashes, manifest fields, write/reuse/block/overwrite behavior, dry-run behavior, and CLI output.
- Added a concise README command-summary note.
- Added `generated/` to `.gitignore` for local narration package outputs.
- Cleaned `generated/narration/` and removed the empty `generated/` directory after validation.
- Final validation passed: 227 Python tests and Remotion typecheck.

Acceptance criteria status: met. The plan defines and implements a local provider-agnostic audio/alignment generation foundation without external API integration. It keeps ElevenLabs for Phase 30, uses safe cache/overwrite/dry-run policy, leaves the existing `build-timeline` contract unchanged, avoids schema changes, and keeps generated artifacts out of commit candidates.

Final commit candidates:

- `.gitignore`
- `README.md`
- `synccut/cli.py`
- `synccut/narration_package.py`
- `tests/test_cli.py`
- `tests/test_narration_package.py`
- `docs/plans/audio-alignment-generation-design.md`

Recommended commit message:

    Add narration package preparation command

The next step is to ask the user before beginning Phase 30 ElevenLabs integration. Do not start Phase 30 automatically.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python 3.11+ CLI package declared in `pyproject.toml`, with Typer as the CLI framework and pytest as the development test runner. The console command is `synccut`, implemented in `synccut/cli.py`.

Current inputs are prepared manually or externally. The file `examples/scenes.json` contains ordered scenes with narration dialogue and visual metadata. The directory `examples/audio/` contains one MP3 per section, such as `01_HOOK.mp3`. The directory `examples/alignments/` contains one alignment JSON per section, such as `01_HOOK_alignment_tmp.json`. An alignment JSON describes timestamps for the narration text; SyncCut uses those timestamps to place scenes on the global timeline.

The loader in `synccut/scenes_loader.py` reads and validates `scenes.json`. Each loaded `Scene` has `scene_id`, `scene_order`, `section`, `section_order`, `section_key`, `dialogue.text`, `dialogue.paragraphs`, and visual metadata. If `dialogue.paragraphs` is missing, the loader treats `dialogue.text` as a single paragraph.

The loader in `synccut/alignment_loader.py` discovers assets by section key. Audio discovery first looks for exactly `<section_key>.mp3`, and then falls back to one matching `<section_key>*.mp3`. Alignment discovery looks for one matching `<section_key>_alignment*.json`. The function `load_section_assets` groups scenes by section key, discovers one audio file and one alignment file for each section, and returns `SectionAsset` objects.

The timeline builder in `synccut/timeline_builder.py` receives loaded scenes and loaded section assets. It matches each scene's dialogue text to the section alignment timestamps, computes global scene timing from section-local timestamps, and writes `timeline.json`. The current `build-timeline` command therefore still depends on audio and alignment files already being present.

In this plan, a "narration package" means a local directory containing plain text and JSON metadata that a future audio/alignment provider can consume. It is not audio, and it is not an alignment result. It is a deterministic description of what audio and alignment outputs should exist for each section.

In this plan, a "provider" means future code that turns section narration text into audio and alignment data. ElevenLabs is one future provider, but this phase must not implement or call it.

In this plan, a "text hash" means a deterministic short identifier derived from the exact section narration text. It is used to tell whether existing generated output still corresponds to the current input text. Use Python's standard `hashlib.sha256`, not a third-party dependency.

## Plan of Work

Milestone 1 audits the current contract without editing source. Inspect `examples/scenes.json`, example audio filenames, example alignment filenames, `synccut/scenes_loader.py`, `synccut/alignment_loader.py`, and `synccut/timeline_builder.py`. Record how section keys are represented, how dialogue is stored, and what prepared inputs `build-timeline` requires. Confirm that Phase 29 should not change the existing build-timeline input contract.

Milestone 2 finalizes the local narration package design before implementation. The command is `prepare-narration`. It reads `scenes.json`, groups scenes by `section_key` sorted by `(section_order, section_key)`, and preserves scenes within each section sorted by `(scene_order, scene_id)`. The section narration text is assembled from scene dialogue in scene order. Each scene contributes its `dialogue.paragraphs` joined with blank lines, and scenes are joined with blank lines. This keeps paragraph boundaries visible for a future provider while preserving the scene text exactly as loaded. The command must not rewrite, summarize, translate, or generate text.

The manifest is JSON and includes a top-level metadata object and a sections array. The top-level metadata includes `schema_version`, `generated_by`, `source_scenes`, `total_sections`, and `total_scenes`. Each section entry includes `section_key`, `section`, `section_order`, `scene_ids`, `scene_count`, `text_path`, `narration_text`, `text_hash`, `expected_audio_path`, and `expected_alignment_path`.

The output naming policy is stable. Future audio uses `<section_key>.mp3`, matching current `discover_audio_file`. Future alignment uses `<section_key>_alignment_tmp.json` for compatibility with the current example naming and the existing `<section_key>_alignment*.json` discovery rule. The manifest is named `narration_manifest.json`. Per-section text files are named `<section_key>.txt`.

The cache policy uses `sha256` of the exact section narration text encoded as UTF-8. The manifest stores the full value as `sha256:<64 lowercase hex characters>`. Existing files are not overwritten by default. If the command would overwrite a different file, it fails clearly unless the user passes `--overwrite`. If an existing file is identical, rerunning is safe and reports it as reused. Dry-run mode computes the same package and reports what would be created, reused, or blocked, but writes nothing.

Milestone 3 implements the local command:

    .venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration

The command should live in `synccut/cli.py`, but the core logic should be in a new small module such as `synccut/narration_package.py` so it can be tested as pure functions. The command should read scenes through `load_scenes`, group by section, write section text files and `narration_manifest.json`, and print a concise human summary. Optional flags should be minimal; likely `--dry-run` and `--overwrite`. Do not add provider selection, ElevenLabs options, API keys, audio generation, or alignment generation in this phase.

Milestone 3 should add focused tests. Add tests for grouping by `section_key` and ordering, text assembly from paragraphs, text hash stability, manifest fields, package write success, rerun reusing identical files, changed existing file blocking without `--overwrite`, overwrite replacing changed files, dry-run writing no files, CLI success output, CLI dry-run output, and CLI blocked output/error. Keep tests on synthetic fixtures where possible. Do not weaken existing timeline tests.

Milestone 4 validates the new command on the sample. Run the Python test suite, then run the new command against `examples/scenes.json` into a generated local path. Inspect the generated manifest and at least one section text file enough to confirm section ids, scene ids, expected paths, and hashes. Confirm `build-timeline` remains unchanged by running it with existing example audio and alignments. Run Remotion typecheck. Do not run Remotion render.

Milestone 5 handles docs, cleanup, and final review. Add a brief README note only if needed, making clear that this is a local narration planning foundation and not real ElevenLabs/audio/alignment generation yet. If `generated/narration/` is used for validation, update `.gitignore` to ignore `generated/` or `generated/narration/`, unless the generated outputs are cleaned and no ignore rule is necessary. Clean generated local outputs before final review unless intentionally adding small text fixtures. Run final pytest and Remotion typecheck. Review `git status --short --ignored` and recommend a commit message.

## Concrete Steps

For Milestone 1, run these read-only commands from the repository root:

    sed -n '1,260p' examples/scenes.json
    rg --files examples/audio examples/alignments | sort
    sed -n '1,260p' synccut/scenes_loader.py
    sed -n '1,260p' synccut/alignment_loader.py
    sed -n '1,280p' synccut/timeline_builder.py
    git status --short --ignored

Record the findings in this plan. The expected finding is that the current sample has seven sections, one audio MP3 per section, and one alignment JSON per section, and that current timeline generation still depends on those prepared files.

For Milestone 2, update this plan before editing source. The update must define the exact command name, manifest fields, file names, dry-run output behavior, overwrite behavior, and tests to add. Do not implement code until the design is recorded.

For Milestone 3, implement the chosen design. Expected files are likely:

    synccut/cli.py
    synccut/narration_package.py
    tests/test_narration_package.py
    tests/test_cli.py
    docs/plans/audio-alignment-generation-design.md
    .gitignore, only if generated validation output will be kept ignored instead of always cleaned

If a different module name is chosen, record the reason in the Decision Log. Keep `synccut/cli.py` thin: it should parse options, call the pure module, print a summary, and translate `SyncCutError` into clear CLI errors.

For Milestone 4, run:

    .venv/bin/python -m pytest
    .venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration
    sed -n '1,220p' generated/narration/narration_manifest.json
    sed -n '1,120p' generated/narration/01_HOOK.txt
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    cd remotion
    npm run typecheck
    cd ..

If the final command name differs from `prepare-narration`, update these commands in this plan before running them. Do not run `prepare-visual-assets`, do not render, and do not call external services.

For Milestone 5, run:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck
    cd ..
    git status --short --ignored

If validation generated `remotion/props.json` or other tracked generated outputs, restore or clean them only if they were generated for validation and are not part of the intended change. Do not use destructive cleanup commands without explicit approval. Generated narration package files should not be committed unless they are intentionally small fixtures added under `tests/fixtures/`.

## Validation and Acceptance

This phase is accepted when a provider-agnostic narration package can be generated from `scenes.json` without any external API. A human should be able to run:

    .venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration

and observe a summary similar to:

    Prepared narration package generated/narration
    sections: 7
    scenes: 33
    manifest: generated/narration/narration_manifest.json
    text_created: 7
    text_reused: 0
    blocked: 0
    Next: provide the manifest to an audio/alignment provider

Dry-run output should be similar but must make the non-writing behavior explicit:

    Dry run: narration package generated/narration
    sections: 7
    scenes: 33
    would_create: 8
    would_reuse: 0
    would_block: 0

If files differ and `--overwrite` is not set, the command should exit non-zero with a clear error that names the conflicting file and mentions `--overwrite`.

The exact wording may be adjusted during implementation if tests record the final text, but it must be concise and human-readable. The generated manifest must list each section, its scenes, its narration text, its text file, a stable full SHA-256 text hash, and expected future audio/alignment paths. Per-section text files must preserve readable narration text.

Run `.venv/bin/python -m pytest` and expect all tests to pass. Existing tests for `build-timeline`, timeline validation, Remotion export, preflight, visual assets, and CLI behavior must continue to pass. Run `cd remotion && npm run typecheck && cd ..` and expect TypeScript typecheck to pass. Existing `build-timeline` must still work with `examples/audio` and `examples/alignments`; this phase must not make generated narration packages a required input for timeline building.

No audio files, alignment timing files, external provider calls, API keys, renders, media downloads, ffmpeg, ffprobe, probing, transcoding, DOCX parsing, B-roll downloading, or visual duration probing are part of acceptance.

## Idempotence and Recovery

The narration package command must be safe to rerun. If output files already exist and match the content it would write, the command reports them as reused. If output files already exist and differ, the command fails clearly by default and tells the user to pass `--overwrite`. `--overwrite` replaces only planned files inside the requested output directory: `narration_manifest.json` and `<section_key>.txt` files for the sections in the current package.

Dry-run mode must not write files or create directories. It computes section grouping, hashes, and intended paths, then reports what would be created, reused, or blocked. Dry-run should be useful before running a provider in Phase 30.

If a generated package is created during validation, it should live under an ignored local path such as `generated/narration/` or be removed during final cleanup. Do not commit generated audio, generated alignment, local media, or render outputs. Do not mutate `examples/scenes.json`.

If implementation reveals that `prepare-narration` is a confusing command name, stop and record the alternative in the Decision Log before changing code. If a test failure suggests that this phase would require changing the timeline schema or Remotion props schema, stop and ask for explicit approval before proceeding.

## Artifacts and Notes

Current example naming:

    examples/audio/01_HOOK.mp3
    examples/audio/02_INTRO.mp3
    examples/audio/03_MECHANISM_1.mp3
    examples/audio/04_MECHANISM_2.mp3
    examples/audio/05_MECHANISM_3.mp3
    examples/audio/06_MECHANISM_4.mp3
    examples/audio/07_CONCLUSION.mp3

    examples/alignments/01_HOOK_alignment_tmp.json
    examples/alignments/02_INTRO_alignment_tmp.json
    examples/alignments/03_MECHANISM_1_alignment_tmp.json
    examples/alignments/04_MECHANISM_2_alignment_tmp.json
    examples/alignments/05_MECHANISM_3_alignment_tmp.json
    examples/alignments/06_MECHANISM_4_alignment_tmp.json
    examples/alignments/07_CONCLUSION_alignment_tmp.json

Suggested manifest shape for Milestone 2 discussion:

    {
      "metadata": {
        "schema_version": "0.1",
        "generated_by": "synccut prepare-narration",
        "source_scenes": "examples/scenes.json",
        "total_sections": 7,
        "total_scenes": 33
      },
      "sections": [
        {
          "section_key": "01_HOOK",
          "section": "HOOK",
          "section_order": 1,
          "scene_ids": ["scene_001", "scene_002", "scene_003"],
          "scene_count": 3,
          "text_path": "01_HOOK.txt",
          "narration_text": "Every iPhone...\n\nThey all come from the same place.\n\nOne company...",
          "text_hash": "sha256:<full64hex>",
          "expected_audio_path": "01_HOOK.mp3",
          "expected_alignment_path": "01_HOOK_alignment_tmp.json"
        }
      ]
    }

The final design stores both full narration text inline and per-section text files. Tests must verify they match exactly.

## Interfaces and Dependencies

Use only Python standard library modules and existing project dependencies. Use `json`, `hashlib`, `dataclasses`, `pathlib.Path`, and existing SyncCut validators. Do not add dependencies.

The likely new module is `synccut/narration_package.py`. It should expose pure functions and data classes such as:

    @dataclass(frozen=True)
    class NarrationSection:
        section_key: str
        section: str
        section_order: int
        scene_ids: list[str]
        narration_text: str
        text_hash: str
        text_path: str
        expected_audio_path: str
        expected_alignment_path: str

    @dataclass(frozen=True)
    class NarrationPackageResult:
        out_dir: Path
        manifest_path: Path
        sections: list[NarrationSection]
        written: int
        reused: int
        skipped: int
        dry_run: bool

    def build_narration_sections(scenes: list[Scene]) -> list[NarrationSection]:
        ...

    def prepare_narration_package(
        scenes_path: Path,
        out_dir: Path,
        *,
        dry_run: bool = False,
        overwrite: bool = False,
    ) -> NarrationPackageResult:
        ...

The final signatures may differ if Milestone 2 justifies a better design, but the module must remain testable without invoking Typer. CLI code in `synccut/cli.py` should call the module and print a short summary.

No ElevenLabs client, provider registry, network request, API key handling, audio synthesis, alignment generation, media probing, ffmpeg, ffprobe, render scripts, DOCX parsing, B-roll downloader, or visual asset duration handling should be implemented in Phase 29. Phase 30 will use the Phase 29 manifest and text package as its input contract for ElevenLabs audio and alignment provider work.

## Change Note

Created this plan on 2026-05-14 for Phase 29 after v0.1.0 release, onboarding hardening, CI, and CLI UX polish. The plan intentionally stops at local narration package design and implementation, with external provider integration deferred to Phase 30.
