# ElevenLabs audio and alignment provider

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to implement the ElevenLabs audio/alignment provider from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can now prepare a local narration package from `scenes.json`, but it still needs externally prepared section audio files and section alignment JSON files before `synccut build-timeline` can run. This phase adds a provider path that consumes the Phase 29 narration package and generates both audio and alignment outputs for each section. After implementation, a user with an ElevenLabs API key should be able to run one SyncCut command against `generated/narration/narration_manifest.json` and receive `<section_key>.mp3` files plus `<section_key>_alignment_tmp.json` files compatible with the current timeline builder.

The primary provider route is ElevenLabs Text to Speech with timestamps. The endpoint returns base64 audio and character-level timing data in the same response, which means Phase 30 can generate speech and derive SyncCut-compatible paragraph timing without a separate forced-alignment pass. ElevenLabs Forced Alignment remains documented as a fallback or future recovery path for already-existing audio, not the primary Phase 30 workflow.

## Progress

- [x] (2026-05-14T17:00:00+07:00) Created this Phase 30 ExecPlan after reviewing the Phase 29 narration package contract, current SyncCut audio/alignment loading behavior, and official ElevenLabs authentication, Text to Speech with timestamps, and Forced Alignment documentation.
- [x] (2026-05-14T17:25:00+07:00) Milestone 1: Audited the Phase 29 manifest contract, current SyncCut alignment compatibility target, official ElevenLabs TTS-with-timestamps/authentication/Forced Alignment contracts, API-key safety, real API smoke-test boundary, and dependency posture without editing source.
- [x] (2026-05-14T17:45:00+07:00) Milestone 2: Finalized the command shape, provider request contract, environment variable behavior, response normalization algorithm, output file naming, metadata shape, cache/resume/no-overwrite policy, section filtering design, implementation files, and tests without editing source.
- [x] (2026-05-14T18:20:00+07:00) Milestone 3: Implemented the ElevenLabs provider foundation, provider-agnostic audio generation orchestration, CLI command, and mocked tests only.
- [x] (2026-05-14T18:40:00+07:00) Milestone 4: Validated local dry-run behavior, section selection, mutual exclusion, existing timeline workflow, Remotion typecheck, and targeted cleanup without calling ElevenLabs.
- [x] (2026-05-14T19:00:00+07:00) Milestone 5: Completed README docs decision, ignore decision, final pytest/typecheck, cleanup/artifact review, and commit recommendation.

## Surprises & Discoveries

- Observation: Phase 29 already provides the exact cache key needed by a provider.
  Evidence: `synccut/narration_package.py` writes `text_hash` as `sha256:<full64hex>` for each section and records `expected_audio_path` and `expected_alignment_path`.
- Observation: Current audio discovery and alignment discovery already match the Phase 29 expected output names.
  Evidence: `synccut/alignment_loader.py` first looks for `<section_key>.mp3` and accepts one `<section_key>*.mp3` fallback. It discovers alignments through `<section_key>_alignment*.json`, so `<section_key>_alignment_tmp.json` is compatible.
- Observation: Existing alignment JSON does not require sentence or word timing to build timelines when paragraph matching succeeds.
  Evidence: `load_alignment` requires `total_duration_sec` and a non-empty `paragraphs` array with `paragraph`, `start`, and `end`. `sentences` and root `words` may be empty arrays.
- Observation: ElevenLabs Text to Speech with timestamps returns `audio_base64`, `alignment`, and `normalized_alignment`.
  Evidence: Official docs for `POST /v1/text-to-speech/:voice_id/with-timestamps` describe base64 audio and character arrays with `character_start_times_seconds` and `character_end_times_seconds`.
- Observation: ElevenLabs authentication uses an `xi-api-key` header.
  Evidence: Official authentication docs state every request should include the API key in the `xi-api-key` header and warn that the key is secret.
- Observation: The TTS-with-timestamps endpoint defaults to `model_id` `eleven_multilingual_v2` and `output_format` `mp3_44100_128`.
  Evidence: Official endpoint docs list those defaults. This matches SyncCut's current MP3 output naming.
- Observation: Forced Alignment is useful but not the Phase 30 primary path.
  Evidence: Official Forced Alignment docs describe a separate multipart endpoint that accepts an audio file and text, then returns character and word timing. That is a fallback for already-existing audio or future repair workflows, not needed when TTS and timestamps are generated together.
- Observation: Phase 29's manifest has all fields Phase 30 needs to make deterministic provider requests and cache decisions.
  Evidence: `synccut/narration_package.py` writes top-level `metadata` with `schema_version`, `generated_by`, `source_scenes`, `total_sections`, and `total_scenes`. Each section has `section_key`, `section`, `section_order`, `scene_ids`, `scene_count`, `text_path`, inline `narration_text`, `text_hash`, `expected_audio_path`, and `expected_alignment_path`.
- Observation: Provider code should prefer inline `narration_text` from the manifest as the canonical input, while validating `text_path` when available.
  Evidence: The manifest already stores the exact text hash over inline `narration_text`. The text files are useful for human review and provider interoperability, but using the manifest text avoids path ambiguity and keeps the cache key tied to the exact text being sent.
- Observation: The current example alignment format is richer than the minimum loader requirement.
  Evidence: `examples/alignments/01_HOOK_alignment_tmp.json` includes `total_duration_sec`, `total_words`, `total_sentences`, `total_paragraphs`, paragraph objects with `paragraph`, `paragraph_index`, `start`, `end`, `duration`, nested `sentences`, nested sentence `words`, and root `words`. `load_alignment` only requires `total_duration_sec` and non-empty `paragraphs` with `paragraph`, `start`, and `end`; `sentences` and root `words` are optional arrays.
- Observation: Timeline building does not require character-level timing and can work with paragraph-level timing only.
  Evidence: `timeline_builder._match_scene_to_alignment` tries paragraph matching first, then sentence matching, paragraph substring matching, and word-span matching. If generated paragraph text matches `scene.dialogue.paragraphs`, paragraph timings are enough.
- Observation: The minimum Phase 30 normalized alignment file can be small and schema-compatible.
  Evidence: A valid generated file can contain `total_duration_sec`, `paragraphs` with exact paragraph text, `start`, `end`, and `sentences: []`, plus root `words: []`. This is enough for `load_alignment` and paragraph matching.
- Observation: ElevenLabs TTS-with-timestamps can likely be normalized into SyncCut's current format without a schema change, but text normalization must be handled conservatively.
  Evidence: The official response has both `alignment` for original text and `normalized_alignment` for normalized text. SyncCut needs paragraph strings to match the original `scenes.json` dialogue, so implementation should use `alignment` tied to original text and fail clearly if it cannot map the original narration text back to returned character timings.
- Observation: `pyproject.toml` has no HTTP client dependency today.
  Evidence: Runtime dependencies list only `typer>=0.12`, and dev dependencies list only `pytest>=8`. A Phase 30 implementation can start with `urllib.request` from the Python standard library and mocked tests, avoiding a dependency addition unless Milestone 2 records a specific need.
- Observation: `.gitignore` already ignores `generated/`.
  Evidence: `.gitignore` contains `generated/`, so dry-run or optional smoke-test outputs under `generated/` should not become commit candidates.
- Observation: Supporting both `--limit` and repeatable `--section-key` is useful, but allowing both in the same command is ambiguous.
  Evidence: `--limit 1` is the preferred smoke-test guard for the first N manifest sections, while `--section-key` is the precise resume/debug selector. Combining them would raise unclear questions about whether the limit applies before or after filtering.
- Observation: One metadata manifest is enough for Phase 30 cache/resume behavior.
  Evidence: The command only needs to know whether each section's audio/alignment files match a text hash and provider configuration. A single JSON file at `generated/audio_generation_manifest.json` can hold all section entries and is already under an ignored generated output root.
- Observation: `urllib.request` remains sufficient for the planned real client.
  Evidence: The provider request is one JSON POST with headers, query parameters, timeout, and JSON response parsing. No streaming, multipart upload, retry framework, or SDK-specific object model is required for the primary TTS-with-timestamps path.
- Observation: Metadata timestamps make tests less deterministic if asserted literally.
  Evidence: `generated_at` is useful for real generation evidence, but tests should assert that it exists and is a valid ISO-8601 UTC string or use fake clocks rather than comparing wall-clock values.
- Observation: The implementation stayed within the Milestone 2 module split.
  Evidence: Added `synccut/audio_generation.py` for manifest loading, selection, cache decisions, response normalization, safe writes, and metadata; added `synccut/elevenlabs_provider.py` for the real HTTP client wrapper; wired `synccut/cli.py`; added `tests/test_audio_generation.py`; and extended `tests/test_cli.py`.
- Observation: Mocked provider tests are enough to validate the local contract without touching ElevenLabs.
  Evidence: `tests/test_audio_generation.py` uses fake clients that return base64 bytes and character arrays, then verifies MP3 output bytes, SyncCut alignment JSON, `load_alignment` compatibility, reuse/block/overwrite behavior, selection behavior, and malformed response errors.
- Observation: Missing API key behavior is verified without a real request.
  Evidence: Tests call `generate_audio_from_manifest` without an injected client and with a controlled missing `ELEVENLABS_API_KEY`; the command raises `SyncCutError` before output directories are created.
- Observation: Full Python test coverage now includes the provider foundation.
  Evidence: `.venv/bin/python -m pytest` collected 249 tests and all 249 passed.
- Observation: Local dry-run validation did not require credentials or create audio/alignment output directories.
  Evidence: `generate-audio ... --dry-run` reported `sections: 7`, `would_generate: 7`, `would_reuse: 0`, and `would_block: 0`. `test -d generated/audio` and `test -d generated/alignments` both returned non-zero after the dry runs.
- Observation: Section filtering behaves correctly in dry-run mode.
  Evidence: `generate-audio ... --limit 1 --dry-run` reported `sections: 1` and `would_generate: 1`. `generate-audio ... --section-key 01_HOOK --dry-run` also reported one selected section.
- Observation: Mutual exclusion is enforced before any provider work.
  Evidence: `generate-audio ... --limit 1 --section-key 01_HOOK --dry-run` exited non-zero with `Error: --limit cannot be used with --section-key`.
- Observation: Existing timeline generation remains unchanged.
  Evidence: `build-timeline` on `examples/scenes.json` with `examples/audio` and `examples/alignments` produced 7 sections, 33 scenes, duration 752.79, and `warnings: 0`; `validate-timeline timeline.json` reported `warnings: 0`.
- Observation: Remotion typecheck still passes.
  Evidence: `cd remotion && npm run typecheck` completed with `tsc --noEmit`.
- Observation: Targeted cleanup removed only the validation narration package.
  Evidence: Before cleanup, `generated/narration` contained the manifest and seven section text files. `generated/audio` and `generated/alignments` did not exist. After `rm -rf generated/narration` and `rmdir generated`, the validation package was removed.
- Observation: README needed only one concise command note.
  Evidence: The existing Python command summary already documented `prepare-narration`; adding one `generate-audio` bullet covers provider `elevenlabs`, `ELEVENLABS_API_KEY`, and dry-run behavior without duplicating provider docs.
- Observation: No `.gitignore` update was needed.
  Evidence: `.gitignore` already contains `generated/`; implementation did not introduce a new output root outside ignored generated/local paths.
- Observation: Final validation passed.
  Evidence: `.venv/bin/python -m pytest` collected 249 tests and all passed; `cd remotion && npm run typecheck` completed with `tsc --noEmit`.
- Observation: Final artifact review found no generated audio/alignment/narration outputs.
  Evidence: `test -e generated/narration`, `test -e generated/audio`, and `test -e generated/alignments` all returned non-zero. Focused status showed source/tests/docs candidates only, plus ignored caches/local media.

## Decision Log

- Decision: Use ElevenLabs Text to Speech with timestamps as the Phase 30 primary provider route.
  Rationale: It returns generated speech and timing data together, reducing drift between audio and alignment and avoiding a second provider call.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep API credentials environment-only through `ELEVENLABS_API_KEY`.
  Rationale: API keys are secrets. Avoiding CLI key options and config files reduces accidental leaks through shell history, logs, committed files, and generated manifests.
  Date/Author: 2026-05-14 / Codex
- Decision: Preserve the existing `build-timeline` contract.
  Rationale: Phase 30 should produce files that the existing audio/alignment discovery can load; it should not change timeline schema, Remotion props schema, or the `build-timeline` input model.
  Date/Author: 2026-05-14 / Codex
- Decision: Tests must use fake provider responses and must never call ElevenLabs.
  Rationale: CI and local tests must be deterministic, free, safe without credentials, and network-independent.
  Date/Author: 2026-05-14 / Codex
- Decision: Default behavior is no-overwrite with explicit resume/reuse.
  Rationale: Generated audio can cost money and may be manually reviewed. Existing files should be reused only when metadata proves they match the same text hash and provider configuration; otherwise the command should block unless `--overwrite` is provided.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 1 confirms TTS-with-timestamps remains the primary path.
  Rationale: The API returns audio and original-text character timestamps together, which is the simplest route to synchronized section MP3 files and SyncCut-compatible alignment JSON.
  Date/Author: 2026-05-14 / Codex
- Decision: Forced Alignment remains fallback/future work.
  Rationale: Forced Alignment requires an existing audio file and separate text upload. It is valuable for repair or external-audio workflows, but Phase 30's goal is to generate audio and alignment together.
  Date/Author: 2026-05-14 / Codex
- Decision: `ELEVENLABS_API_KEY` is the only approved API-key source.
  Rationale: Environment-only credentials keep secrets out of CLI arguments, config files, manifests, and source control. The implementation should never print the key.
  Date/Author: 2026-05-14 / Codex
- Decision: Dry-run must not require or read `ELEVENLABS_API_KEY`.
  Rationale: Dry-run is a planning/reporting mode and must prove output decisions without credentials, network access, cost, or side effects.
  Date/Author: 2026-05-14 / Codex
- Decision: No real ElevenLabs calls are allowed without explicit user approval.
  Rationale: Real calls can consume credits, depend on network and account state, and create generated media. Milestones 1 through 4 should use docs, dry-run, and mocked tests only unless the user separately approves a smoke test.
  Date/Author: 2026-05-14 / Codex
- Decision: The current timeline schema, Remotion props schema, and `build-timeline` contract remain unchanged.
  Rationale: The audit found an alignment output shape that is compatible with current loading and paragraph matching. Phase 30 should generate compatible files rather than changing downstream schemas.
  Date/Author: 2026-05-14 / Codex
- Decision: Start with Python standard library HTTP unless Milestone 2 identifies a concrete blocker.
  Rationale: The current project has no HTTP dependency and needs one JSON POST endpoint. `urllib.request` is sufficient for a minimal client behind a fakeable abstraction.
  Date/Author: 2026-05-14 / Codex
- Decision: The command name is `generate-audio`.
  Rationale: The command produces both audio and alignment files, but the user's mental model starts with generating narration audio from the narration package. The command summary and help text must explicitly say it also writes alignment JSON.
  Date/Author: 2026-05-14 / Codex
- Decision: The CLI shape is `synccut generate-audio MANIFEST --provider elevenlabs --audio-dir DIR --alignment-dir DIR --voice-id VOICE_ID [--model-id MODEL] [--output-format FORMAT] [--metadata-out PATH] [--dry-run] [--overwrite] [--limit N | --section-key KEY ...]`.
  Rationale: The manifest path is the required positional input. Provider, voice, audio output, and alignment output are required to make the command explicit. Defaults should cover stable ElevenLabs model/output choices and metadata location.
  Date/Author: 2026-05-14 / Codex
- Decision: Default `model_id` is `eleven_multilingual_v2`, default `output_format` is `mp3_44100_128`, and default metadata path is `generated/audio_generation_manifest.json`.
  Rationale: These match the official endpoint defaults and SyncCut's MP3 discovery behavior. The generated metadata path is local and ignored by `.gitignore`.
  Date/Author: 2026-05-14 / Codex
- Decision: Support both `--limit` and repeatable `--section-key`, but reject using them together.
  Rationale: `--limit` is ideal for first-section smoke tests; `--section-key` is ideal for precise retries. Rejecting their combination keeps selection deterministic and easy to explain.
  Date/Author: 2026-05-14 / Codex
- Decision: The real ElevenLabs client will use `urllib.request` and no new dependency.
  Rationale: Python's standard library can issue the required POST, set `xi-api-key`, encode JSON, add `output_format` as a query parameter, handle a timeout, and parse the JSON response.
  Date/Author: 2026-05-14 / Codex
- Decision: Real client requests use `POST /v1/text-to-speech/{voice_id}/with-timestamps`, `xi-api-key`, JSON body `{"text": ..., "model_id": ...}`, and `output_format` as a query parameter.
  Rationale: This is the official TTS-with-timestamps contract and keeps output format explicit without adding provider-specific complexity.
  Date/Author: 2026-05-14 / Codex
- Decision: Provider errors become `SyncCutError` messages that omit secrets and avoid dumping raw response bodies.
  Rationale: CLI failures should be actionable but safe. The message should include the section key, HTTP status or provider error label when available, and a short sanitized message.
  Date/Author: 2026-05-14 / Codex
- Decision: Normalize from `alignment`, not `normalized_alignment`.
  Rationale: SyncCut paragraph matching needs original `scenes.json` text. `normalized_alignment` may reflect provider-normalized text and can break exact paragraph matching.
  Date/Author: 2026-05-14 / Codex
- Decision: Generated alignment JSON will contain paragraph timing only, with `sentences: []` and root `words: []`.
  Rationale: This is the minimum compatible structure accepted by `alignment_loader.load_alignment` and preferred by `timeline_builder` paragraph matching. Sentence and word timing can be added later only if needed.
  Date/Author: 2026-05-14 / Codex
- Decision: Output files are `<section_key>.mp3` in `--audio-dir`, `<section_key>_alignment_tmp.json` in `--alignment-dir`, and one metadata JSON manifest.
  Rationale: These names are compatible with current discovery rules and Phase 29's expected output fields.
  Date/Author: 2026-05-14 / Codex
- Decision: Cache/reuse requires audio file, alignment file, and metadata entry to match `text_hash`, provider, voice ID, model ID, and output format.
  Rationale: All five fields affect generated output. Missing or mismatched metadata means the command cannot prove the files are safe to reuse.
  Date/Author: 2026-05-14 / Codex
- Decision: Implementation should use two new modules: `synccut/audio_generation.py` and `synccut/elevenlabs_provider.py`.
  Rationale: The orchestration/cache/normalization logic is provider-agnostic enough to keep separate from the HTTP client. Separating modules keeps tests focused and `synccut/cli.py` thin.
  Date/Author: 2026-05-14 / Codex
- Decision: CLI success output is covered with a monkeypatched orchestration function, while real generation behavior is covered in unit tests.
  Rationale: This keeps CLI tests deterministic and network-free while still validating the real command output shape. The orchestration tests cover actual file writes using fake clients and temporary directories.
  Date/Author: 2026-05-14 / Codex
- Decision: The first implementation keeps generated alignment minimal: paragraph timings only, empty `sentences`, and empty root `words`.
  Rationale: This matches the current compatibility target and keeps Phase 30 focused. Sentence/word derivation can be added later if a real provider output review proves it is needed.
  Date/Author: 2026-05-14 / Codex
- Decision: Update README with a single `generate-audio` command-summary bullet.
  Rationale: The command is now user-facing enough to mention, but the README should not duplicate ElevenLabs API docs or include any key material.
  Date/Author: 2026-05-14 / Codex
- Decision: Do not change `.gitignore`.
  Rationale: `generated/` is already ignored from Phase 29, and no new generated path outside that root was introduced.
  Date/Author: 2026-05-14 / Codex
- Decision: Do not run a real ElevenLabs smoke test by default.
  Rationale: No explicit approval was given. Real calls may consume credits and should use `--limit 1` with temporary generated output directories only after user approval.
  Date/Author: 2026-05-14 / Codex

## Outcomes & Retrospective

This plan has been created but not implemented. No source code, tests, README, schemas, command behavior, generated audio, generated alignment, real ElevenLabs API calls, media downloads, ffmpeg/ffprobe work, renders, commits, tags, or pushes were performed while authoring the plan.

The intended outcome is a safe, testable provider integration. At completion, `synccut generate-audio` should read a Phase 29 narration manifest, create MP3 audio files and SyncCut alignment JSON files for selected sections, record generation metadata, support dry-run and resume behavior, and leave the existing timeline-building workflow unchanged.

Milestone 1 is complete. The audit confirmed that Phase 29's narration manifest is sufficient for Phase 30: section text is available inline as `narration_text`, the stable cache key is available as `text_hash`, and expected output names already match current audio and alignment discovery. Provider code should treat inline `narration_text` as canonical and may use `text_path` as a consistency check or human-facing reference.

The current SyncCut compatibility target is paragraph-level alignment JSON. Existing examples contain sentence and word detail, but `alignment_loader.load_alignment` only requires section duration plus paragraph text/start/end timings, and `timeline_builder` matches paragraphs before falling back to sentences or words. Therefore Phase 30 can normalize ElevenLabs character timestamps into paragraph entries without changing schemas. The main compatibility risk is provider text normalization: SyncCut needs paragraph strings to match the original narration text, so implementation should use ElevenLabs `alignment` for original text and fail clearly if returned character timing cannot be mapped to the manifest text.

Official ElevenLabs docs confirm the API safety and provider boundary. Text to Speech with timestamps remains the primary route because it returns `audio_base64` and character timing in one response. Forced Alignment remains future fallback because it aligns already-existing audio and text. API keys must come from `ELEVENLABS_API_KEY`, dry-run must not need a key, and any real API smoke test must be explicitly approved, use `--limit 1`, and write only to temporary generated output directories because it may consume account credits.

Dependency audit found no current HTTP dependency in `pyproject.toml`. Milestone 2 should design the client around standard library HTTP and fakeable provider interfaces unless a concrete implementation blocker justifies adding a dependency. The next step is Milestone 2: finalize provider/output/cache design, CLI options, metadata layout, response normalization details, and tests.

Milestone 2 is complete. The final implementation contract is:

- Command: `synccut generate-audio MANIFEST --provider elevenlabs --audio-dir DIR --alignment-dir DIR --voice-id VOICE_ID`.
- Defaults: `--model-id eleven_multilingual_v2`, `--output-format mp3_44100_128`, and `--metadata-out generated/audio_generation_manifest.json`.
- Optional controls: `--dry-run`, `--overwrite`, `--limit N`, and repeatable `--section-key KEY`. `--limit` and `--section-key` are mutually exclusive.
- Credentials: non-dry-run ElevenLabs generation reads `ELEVENLABS_API_KEY` immediately before a real request and fails before network if missing. Dry-run does not read the environment or create a client.
- Provider request: standard library `urllib.request` POST to `/v1/text-to-speech/{voice_id}/with-timestamps`, `xi-api-key` header, JSON body with `text` and `model_id`, `output_format` query parameter, and a finite timeout.
- Normalization: decode `audio_base64`, use `alignment.characters`, `character_start_times_seconds`, and `character_end_times_seconds`, verify shape and text compatibility, split manifest `narration_text` on blank-line paragraph boundaries, derive paragraph start/end from non-whitespace character timing, set `sentences: []`, set root `words: []`, and fail clearly instead of inventing timing.
- Outputs: `<section_key>.mp3`, `<section_key>_alignment_tmp.json`, and a single metadata JSON manifest with deterministic formatting.
- Cache policy: reuse only when audio, alignment, and metadata all match `text_hash`, provider, voice ID, model ID, and output format; block conflicts unless `--overwrite`; write temp files then rename.
- Implementation files: `synccut/audio_generation.py`, `synccut/elevenlabs_provider.py`, `synccut/cli.py`, `tests/test_audio_generation.py`, `tests/test_cli.py`, and this plan.

The next step is Milestone 3: implement the focused provider with mocked tests only. Do not call ElevenLabs during implementation or tests.

Milestone 3 is complete. Implementation summary:

- Added `synccut/elevenlabs_provider.py` with `ElevenLabsTimestampsResponse` and `ElevenLabsTimestampsClient`.
- The real client uses Python standard library `urllib.request`, posts to the ElevenLabs TTS-with-timestamps endpoint, sends `xi-api-key`, writes `text` and `model_id` in the JSON body, passes `output_format` as a query parameter, validates response shape, and converts HTTP/network/JSON errors into safe `SyncCutError` messages.
- Added `synccut/audio_generation.py` with Phase 29 manifest loading, section selection, dry-run planning, no-overwrite conflict detection, reuse/resume checks from metadata, fakeable client injection, base64 audio decoding, paragraph-only SyncCut alignment normalization, atomic output writes, and metadata writes.
- Added `synccut generate-audio` to `synccut/cli.py` with required provider/audio/alignment/voice options, defaults for model/output/metadata, dry-run, overwrite, limit, and repeatable section-key filtering.
- Added `tests/test_audio_generation.py` with mocked provider coverage for manifest loading, dry-run, missing API key, fake MP3/alignment writing, `load_alignment` compatibility, reuse, conflict, overwrite, section selection, invalid provider, malformed provider response, and text mismatch.
- Extended `tests/test_cli.py` with deterministic CLI coverage for dry-run output, monkeypatched success output, missing API key output, conflict output, and invalid provider output.

Validation result: `.venv/bin/python -m pytest` passed with 249 tests. No real ElevenLabs API call was made. No API key was required or read in dry-run tests. No production audio or alignment was generated into `examples/audio` or `examples/alignments`. No README, `.gitignore`, `pyproject.toml`, timeline schema, Remotion props schema, build-timeline contract, ffmpeg/ffprobe, media probing, rendering, commits, tags, pushes, or Phase 31 work were performed.

The next step is Milestone 4: validate the command locally without a real API call by using dry-run against a sample narration manifest, confirm existing build-timeline behavior remains unchanged, run Remotion typecheck, and keep any generated local validation outputs under ignored/generated paths or clean them.

Milestone 4 is complete. Local validation summary:

- `.venv/bin/python -m pytest` passed with 249 tests.
- `.venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration` succeeded and wrote 8 package files for 7 sections and 33 scenes.
- Full dry-run generation against the sample narration manifest reported `provider: elevenlabs`, `sections: 7`, `would_generate: 7`, `would_reuse: 0`, `would_block: 0`, and did not create `generated/audio` or `generated/alignments`.
- `--limit 1 --dry-run` reported one selected section and one planned generation.
- `--section-key 01_HOOK --dry-run` reported one selected section and one planned generation.
- Combining `--limit 1` and `--section-key 01_HOOK` exited non-zero with a clear mutual-exclusion error.
- Existing `build-timeline` and `validate-timeline` with `examples/audio` and `examples/alignments` still pass with `warnings: 0`.
- Remotion typecheck passed.
- Cleanup removed `generated/narration`; no generated narration/audio/alignment output remains from this milestone.

No real ElevenLabs API call was made, no API key was required during dry-run, and no production audio or alignment was generated. The optional real API smoke test remains user-approved only and should use `--limit 1` plus temporary generated output directories if approved later. The next step is Milestone 5: docs decision, final validation, cleanup review, artifact review, and commit recommendation.

Milestone 5 is complete. Phase 30 final summary:

- Implemented `synccut generate-audio` for provider `elevenlabs`.
- Added a real ElevenLabs TTS-with-timestamps client wrapper using the Python standard library.
- Added provider-agnostic orchestration for Phase 29 narration manifests.
- Added dry-run behavior that writes nothing, does not read `ELEVENLABS_API_KEY`, and does not call a provider.
- Added environment-only API key handling for non-dry-run real generation.
- Added section selection with `--limit` or repeatable `--section-key`, with mutual exclusion.
- Added paragraph-level SyncCut alignment JSON normalization from character timestamps.
- Added metadata/cache/reuse/block/overwrite behavior.
- Added mocked tests covering provider behavior, alignment compatibility, CLI output, and safe errors.
- Added a concise README command-summary note for `generate-audio`.

Acceptance criteria status: met for the provider foundation. The implementation chooses TTS-with-timestamps as the primary route, maps Phase 29 manifests to audio/alignment outputs, defines and implements no-overwrite/cache/resume behavior, handles API keys safely, uses mocked tests without real API calls, and leaves schemas/build-timeline/Remotion props unchanged.

Real API smoke test status: not run by default. If the user wants it later, run one section only, with an environment-provided `ELEVENLABS_API_KEY`, temporary generated output directories, and no committed media:

    .venv/bin/synccut generate-audio generated/narration/narration_manifest.json --provider elevenlabs --audio-dir generated/elevenlabs-audio --alignment-dir generated/elevenlabs-alignments --voice-id <voice_id> --limit 1

Final validation passed: 249 Python tests and Remotion typecheck. Cleanup/artifact review found no generated narration, audio, or alignment outputs left behind. Commit candidates are expected source/tests/docs only:

- `README.md`
- `synccut/audio_generation.py`
- `synccut/elevenlabs_provider.py`
- `synccut/cli.py`
- `tests/test_audio_generation.py`
- `tests/test_cli.py`
- `docs/plans/elevenlabs-audio-alignment-provider.md`

Recommended commit message:

    Add ElevenLabs audio generation provider

Next step: ask the user whether to run an optional one-section real ElevenLabs smoke test first, or commit the provider foundation before Phase 31. Do not start Phase 31 automatically.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python CLI package using Typer and pytest. The CLI entry point is `synccut/cli.py`. Current timeline generation still starts with prepared section assets:

    synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json

Phase 29 added:

    synccut prepare-narration SCENES_JSON --out-dir generated/narration

That command writes `generated/narration/narration_manifest.json` and one `<section_key>.txt` file per section. The manifest contains `metadata` and `sections`. Each section includes `section_key`, display `section`, `section_order`, `scene_ids`, `scene_count`, `text_path`, `narration_text`, `text_hash`, `expected_audio_path`, and `expected_alignment_path`. The text hash is a full SHA-256 digest formatted as `sha256:<64 lowercase hex characters>`.

Current SyncCut asset loading lives in `synccut/alignment_loader.py`. Audio discovery checks `<section_key>.mp3` first and then allows exactly one `<section_key>*.mp3`. Alignment discovery allows exactly one `<section_key>_alignment*.json`. The alignment JSON loader requires:

    {
      "total_duration_sec": 12.34,
      "paragraphs": [
        {
          "paragraph": "Narration paragraph text",
          "start": 0.0,
          "end": 2.5,
          "sentences": []
        }
      ],
      "words": []
    }

`sentences` and `words` can be empty. The timeline builder in `synccut/timeline_builder.py` first attempts paragraph matching against scene `dialogue.paragraphs`. Therefore Phase 30 can produce paragraph-level alignment from character timestamps, provided the `paragraph` strings match the narration package text pieces used to generate the audio.

The official ElevenLabs Text to Speech with timestamps endpoint is:

    POST https://api.elevenlabs.io/v1/text-to-speech/:voice_id/with-timestamps

It accepts JSON with required `text`, optional `model_id`, optional `voice_settings`, and related options. It also has an `output_format` query parameter that defaults to `mp3_44100_128`. The response includes `audio_base64`, `alignment`, and `normalized_alignment`. The `alignment` object contains `characters`, `character_start_times_seconds`, and `character_end_times_seconds` for the original text. SyncCut should use `alignment` as the primary timing source because it is tied to the original text. If `alignment` is missing, malformed, or cannot be mapped back to the manifest text, the command should fail clearly rather than invent timing.

The official ElevenLabs Forced Alignment endpoint is:

    POST https://api.elevenlabs.io/v1/forced-alignment

It accepts multipart audio plus text and returns timed characters and words. Phase 30 should not use this endpoint by default. It is reserved for future fallback workflows where audio already exists or timestamp generation needs repair.

## Plan of Work

Milestone 1 audits the current repository and official API contracts before writing code. Read `synccut/narration_package.py`, `synccut/cli.py`, `synccut/alignment_loader.py`, `synccut/timeline_builder.py`, `synccut/models.py`, and the Phase 29 tests. Confirm the manifest fields and exact loader requirements. Re-check official ElevenLabs docs for Text to Speech with timestamps, authentication, model/output parameters, response shape, and Forced Alignment. Record whether character-level timestamps can be normalized into the current paragraph-based alignment JSON without schema changes.

Milestone 2 finalizes provider behavior before code. The command is:

    synccut generate-audio generated/narration/narration_manifest.json --provider elevenlabs --audio-dir generated/audio --alignment-dir generated/alignments --voice-id <voice_id>

It generates section audio and section alignment files. Required inputs are the narration manifest path, `--provider elevenlabs`, `--voice-id`, `--audio-dir`, and `--alignment-dir`. Optional inputs are `--model-id` with default `eleven_multilingual_v2`, `--output-format` with default `mp3_44100_128`, `--metadata-out` with default `generated/audio_generation_manifest.json`, `--dry-run`, `--overwrite`, `--limit N`, and repeatable `--section-key KEY`. `--limit` selects the first N sections in manifest order. `--section-key` selects explicit sections in the order requested after validating that each key exists. If both `--limit` and `--section-key` are passed, the command exits with a clear error.

The metadata layout is one JSON file at `--metadata-out`. The default is `generated/audio_generation_manifest.json`. Metadata records provider, voice ID, model ID, output format, source narration manifest path, audio output directory, alignment output directory, generation command identity, and one section entry per selected section. Each section entry records `section_key`, status, `text_hash`, provider, voice ID, model ID, output format, audio path, alignment path, and `generated_at` when a section is written or reused from a prior matching generation. Tests should not compare real wall-clock timestamps literally; they should assert existence and parseability or inject a fake clock.

Milestone 3 implements only the focused provider foundation. Keep CLI code thin. Add provider-agnostic orchestration in `synccut/audio_generation.py` and the ElevenLabs HTTP client in `synccut/elevenlabs_provider.py`. Use Python standard library HTTP facilities, especially `urllib.request`, `urllib.parse`, and `json`, rather than adding a dependency. Add a small client abstraction so tests can inject fake responses without network.

The implementation must decode `audio_base64` to bytes for `<section_key>.mp3`. It must convert ElevenLabs character timing into current SyncCut alignment JSON. The normalizer should map the exact Phase 29 `narration_text` into paragraphs by splitting on blank lines in the same way the narration package wrote text. For each paragraph, find the character span in the original text and derive paragraph `start` from the first non-whitespace character timestamp and paragraph `end` from the last non-whitespace character timestamp. Keep `sentences` as an empty array unless a tested sentence splitter is explicitly added. Keep root `words` as an empty array unless the implementation adds a deterministic word timing derivation from characters. The minimum compatible output is paragraph timing.

The implementation must verify `alignment.characters`, `alignment.character_start_times_seconds`, and `alignment.character_end_times_seconds` are present, are arrays, and have the same length. The joined `characters` string must be compatible with the section `narration_text`. Compatibility should be exact for the initial implementation after normalizing only line endings if needed. If exact compatibility fails, raise `SyncCutError` with a message naming the section and saying the provider alignment text does not match the narration text. Do not silently switch to `normalized_alignment`.

The implementation must read `ELEVENLABS_API_KEY` only for a non-dry-run real ElevenLabs request. If the value is missing or empty, raise `SyncCutError` before creating a request. Never include the key in errors, metadata, logs, or test fixtures.

Milestone 4 validates without real API calls by default. Run the Python tests and Remotion typecheck. Run a dry-run command against a real generated narration manifest and confirm no network call occurs and no files are written. Use mocked tests to prove fake provider responses write audio and alignment to temporary directories. Confirm `build-timeline` still works with existing `examples/audio` and `examples/alignments`. Do not call ElevenLabs unless the user explicitly approves a real smoke test.

Milestone 5 updates documentation and reviews artifacts. Add a short README note only if the command is ready for user-facing use. Update `.gitignore` only if generated metadata or local generation output introduces a new unignored local artifact path. Clean any local test outputs. Run final pytest and Remotion typecheck. Review `git status --short --ignored` and recommend a commit message. Ask the user before starting Phase 31.

## Concrete Steps

Milestone 1 commands from the repository root:

    sed -n '1,260p' synccut/narration_package.py
    sed -n '1,320p' synccut/cli.py
    sed -n '1,260p' synccut/alignment_loader.py
    sed -n '1,320p' synccut/timeline_builder.py
    sed -n '1,260p' synccut/models.py
    sed -n '1,260p' tests/test_narration_package.py
    sed -n '1,260p' tests/test_cli.py
    git status --short --ignored

Milestone 1 should also re-check these official docs and record their current behavior in this plan:

    https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps
    https://elevenlabs.io/docs/api-reference/authentication
    https://elevenlabs.io/docs/api-reference/forced-alignment/create

Milestone 2 should update this plan only. It should not edit source code. It must finalize the command name, options, metadata path, cache rules, API request fields, response normalization rules, and test list before implementation.

Milestone 3 should add or update these likely files:

    synccut/audio_generation.py
    synccut/elevenlabs_provider.py
    synccut/cli.py
    tests/test_audio_generation.py
    tests/test_cli.py
    docs/plans/elevenlabs-audio-alignment-provider.md

If implementation can remain simpler with one new provider module, record that decision before coding. If a new dependency is proposed, stop and record why it is necessary before editing `pyproject.toml`.

Milestone 3 should add these focused tests:

    tests/test_audio_generation.py::test_loads_phase29_manifest_sections
    tests/test_audio_generation.py::test_dry_run_writes_nothing_and_does_not_call_client_or_env
    tests/test_audio_generation.py::test_missing_api_key_blocks_before_client_call
    tests/test_audio_generation.py::test_fake_provider_writes_mp3_and_alignment_json
    tests/test_audio_generation.py::test_generated_alignment_is_accepted_by_load_alignment
    tests/test_audio_generation.py::test_reuses_outputs_when_files_and_metadata_match
    tests/test_audio_generation.py::test_blocks_when_outputs_exist_without_matching_metadata
    tests/test_audio_generation.py::test_overwrite_replaces_planned_outputs
    tests/test_audio_generation.py::test_limit_selects_first_n_sections
    tests/test_audio_generation.py::test_section_key_selects_requested_sections
    tests/test_audio_generation.py::test_rejects_limit_and_section_key_together
    tests/test_audio_generation.py::test_invalid_provider_is_rejected
    tests/test_audio_generation.py::test_invalid_response_shape_is_rejected
    tests/test_cli.py::test_generate_audio_success_output
    tests/test_cli.py::test_generate_audio_dry_run_output
    tests/test_cli.py::test_generate_audio_missing_api_key_output
    tests/test_cli.py::test_generate_audio_conflict_mentions_overwrite

Milestone 4 validation commands from the repository root:

    .venv/bin/python -m pytest
    .venv/bin/synccut prepare-narration examples/scenes.json --out-dir generated/narration
    .venv/bin/synccut generate-audio generated/narration/narration_manifest.json --provider elevenlabs --audio-dir generated/audio --alignment-dir generated/alignments --voice-id dummy --dry-run
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    cd remotion
    npm run typecheck
    cd ..

The `generate-audio --dry-run` command must not read `ELEVENLABS_API_KEY`, make a network call, create output files, or modify existing examples.

Optional real API smoke test commands must not be run unless the user explicitly approves them in a later milestone. If approved, use one section and temporary output directories:

    ELEVENLABS_API_KEY=<set in environment, never printed>
    .venv/bin/synccut generate-audio generated/narration/narration_manifest.json --provider elevenlabs --audio-dir generated/elevenlabs-audio --alignment-dir generated/elevenlabs-alignments --voice-id <voice_id> --limit 1

Milestone 5 final validation commands:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck
    cd ..
    git status --short --ignored

## Validation and Acceptance

The feature is accepted when a user can prepare narration, dry-run generation, and, with explicit API credentials and approval, generate compatible section assets.

Tests must cover:

- Loading and validating the Phase 29 manifest.
- Rejecting missing or unsupported providers.
- Rejecting missing `ELEVENLABS_API_KEY` before real network calls when not in dry-run.
- Dry-run planning that writes nothing and performs no provider calls.
- Section filtering with `--limit` or `--section-key`, depending on the Milestone 2 design.
- No-overwrite behavior when audio, alignment, or metadata exists and does not match.
- Reuse/resume behavior when audio, alignment, and metadata match `text_hash`, provider, voice, model, and output format.
- Overwrite behavior replacing only planned outputs.
- Decoding mocked `audio_base64` into an MP3 output path.
- Normalizing mocked character timestamps into alignment JSON accepted by `load_alignment`.
- CLI success output, dry-run output, blocked output, missing API key output, and provider error output.

Additional error cases to cover are unsupported provider, missing required manifest field, HTTP/network failure from the real-client wrapper, non-2xx provider response, invalid JSON response, missing `audio_base64`, invalid base64, mismatched alignment arrays, alignment text mismatch, output conflict without `--overwrite`, and passing both `--limit` and `--section-key`.

Run:

    .venv/bin/python -m pytest

Expected result: all tests pass, including new mocked provider tests. No test may call the real ElevenLabs API.

Run:

    cd remotion
    npm run typecheck
    cd ..

Expected result: TypeScript typecheck passes. This phase should not require Remotion source changes.

For a mocked or temp generated alignment file, run `load_alignment` through tests or a small test fixture and expect it to accept `total_duration_sec`, `paragraphs`, and empty `words`. For an end-to-end local smoke without provider calls, existing examples must still pass:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json

Expected result: build succeeds and validation reports zero errors.

## Idempotence and Recovery

All generation behavior must be safe to rerun. If an output file does not exist, the command may create it. If an output file exists and metadata proves it matches the same `text_hash`, provider, voice ID, model ID, and output format, the command should reuse it and report reuse. If files exist but metadata is missing or mismatched, the command must block by default and mention `--overwrite`. If `--overwrite` is passed, replace only files that are part of the planned section outputs and metadata. Do not delete or rewrite unrelated files in `audio-dir`, `alignment-dir`, or `generated/`.

The exact cache rule is: reuse a section only when the final audio file exists, the final alignment file exists, and the metadata manifest has a section entry with matching `section_key`, `text_hash`, `provider`, `voice_id`, `model_id`, `output_format`, `audio_path`, and `alignment_path`. If any output exists without a matching metadata entry, treat it as a conflict. If metadata exists but files are missing, treat the missing files as needing generation unless another output conflict is present.

Partial generation must be resumable. After each successful section, write or update metadata atomically enough that an interrupted run can skip completed matching sections later. If a section fails due to HTTP or response shape error, leave successful previous sections intact and report which section failed. Do not leave a corrupt partial MP3 or JSON file under the final output name; write to a temporary sibling name first and rename after validation.

Dry-run must be side-effect free. It must not create directories, write metadata, write audio, write alignment, read `ELEVENLABS_API_KEY`, or call a provider.

If a real API smoke test is approved later, keep outputs in `generated/` unless the user explicitly approves writing into `examples/audio` and `examples/alignments`. Never print the API key. If the user cancels or an API call fails, clean only temporary files created by the command and keep metadata clear about incomplete sections.

## Artifacts and Notes

Official API facts used by this plan:

- ElevenLabs Text to Speech with timestamps endpoint: `POST /v1/text-to-speech/:voice_id/with-timestamps`.
- Text-to-speech response includes `audio_base64`, `alignment`, and `normalized_alignment`.
- The `alignment` object contains `characters`, `character_start_times_seconds`, and `character_end_times_seconds` for the original text.
- The endpoint accepts required `text`, optional `model_id`, optional `voice_settings`, and an `output_format` query parameter defaulting to `mp3_44100_128`.
- ElevenLabs API keys are sent in the `xi-api-key` header.
- ElevenLabs Forced Alignment is a separate multipart endpoint that accepts an audio file and text, then returns timed characters and words.

Example target generated alignment JSON for SyncCut:

    {
      "total_duration_sec": 4.25,
      "paragraphs": [
        {
          "paragraph": "First narration paragraph.",
          "start": 0.0,
          "end": 1.8,
          "sentences": []
        },
        {
          "paragraph": "Second narration paragraph.",
          "start": 2.0,
          "end": 4.25,
          "sentences": []
        }
      ],
      "words": []
    }

Example successful human output shape:

    Generated audio and alignment generated/narration/narration_manifest.json
    provider: elevenlabs
    sections: 7
    written: 14
    reused: 0
    skipped: 0
    metadata: generated/audio_generation_manifest.json
    Next: synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json

Example dry-run output shape:

    Dry run: audio generation generated/narration/narration_manifest.json
    provider: elevenlabs
    sections: 7
    would_generate: 7
    would_reuse: 0
    would_block: 0
    audio_dir: generated/audio
    alignment_dir: generated/alignments

Example metadata shape:

    {
      "metadata": {
        "schema_version": "0.1",
        "generated_by": "synccut generate-audio",
        "provider": "elevenlabs",
        "source_manifest": "generated/narration/narration_manifest.json",
        "audio_dir": "generated/audio",
        "alignment_dir": "generated/alignments",
        "model_id": "eleven_multilingual_v2",
        "output_format": "mp3_44100_128"
      },
      "sections": [
        {
          "section_key": "01_HOOK",
          "status": "written",
          "text_hash": "sha256:...",
          "provider": "elevenlabs",
          "voice_id": "voice_123",
          "model_id": "eleven_multilingual_v2",
          "output_format": "mp3_44100_128",
          "audio_path": "generated/audio/01_HOOK.mp3",
          "alignment_path": "generated/alignments/01_HOOK_alignment_tmp.json",
          "generated_at": "2026-05-14T10:45:00Z"
        }
      ]
    }

Metadata should use deterministic JSON formatting with `indent=2`, `ensure_ascii=False`, and a trailing newline. Paths should be stringified consistently as the user passed them or as paths relative to the current working directory when practical; do not mix absolute paths into metadata unless the user passed absolute paths.

Example blocked output shape:

    Error: 01_HOOK: output exists but metadata does not match text_hash/provider/voice/model/output_format; rerun with --overwrite to replace

## Interfaces and Dependencies

Use the existing `SyncCutError` exception from `synccut/validators.py` for clear CLI failures. Keep `synccut/cli.py` thin: it should parse paths/options, call provider orchestration, print summaries, and convert `SyncCutError` into exit code 1.

Add a provider-agnostic orchestration module. Suggested interface:

    @dataclass(frozen=True)
    class AudioGenerationSectionResult:
        section_key: str
        status: str
        audio_path: Path
        alignment_path: Path
        text_hash: str

    @dataclass(frozen=True)
    class AudioGenerationResult:
        provider: str
        sections: list[AudioGenerationSectionResult]
        metadata_path: Path
        dry_run: bool
        generated: int
        reused: int
        blocked: int

    def generate_audio_from_manifest(
        manifest_path: Path,
        *,
        provider: str,
        audio_dir: Path,
        alignment_dir: Path,
        voice_id: str,
        model_id: str,
        output_format: str,
        metadata_path: Path,
        dry_run: bool = False,
        overwrite: bool = False,
        limit: int | None = None,
        section_keys: list[str] | None = None,
        api_key_getter: Callable[[str], str | None] | None = None,
        clock: Callable[[], datetime] | None = None,
        client: ElevenLabsTimestampsClient | None = None,
    ) -> AudioGenerationResult:
        ...

Add an ElevenLabs client abstraction that can be faked in tests. Suggested interface:

    @dataclass(frozen=True)
    class ElevenLabsTimestampsResponse:
        audio_base64: str
        alignment: dict
        normalized_alignment: dict | None

    class ElevenLabsTimestampsClient:
        def synthesize_with_timestamps(
            self,
            *,
            text: str,
            voice_id: str,
            model_id: str,
            output_format: str,
        ) -> ElevenLabsTimestampsResponse:
            ...

The client constructor, not the method, may receive the API key and timeout. The orchestration layer should create the real client only after dry-run has been ruled out and after `ELEVENLABS_API_KEY` has been verified.

The real client should read the API key from `ELEVENLABS_API_KEY` only when it is about to make a real request. It should send the key in the `xi-api-key` header. It should use standard library HTTP unless Milestone 2 records an approved dependency change. It must never log the key.

Do not add the official ElevenLabs SDK by default. A new dependency would require a documented decision because the standard library is sufficient for a single POST request and tests should use fake clients.

Do not change:

- timeline JSON schema
- Remotion props schema
- `build-timeline` required inputs
- current audio/alignment discovery rules
- Remotion render scripts
- visual asset workflows

## Milestones

Milestone 1: API and current contract audit.

Audit the Phase 29 manifest and current SyncCut alignment requirements. Confirm that generated audio files named `<section_key>.mp3` and alignment files named `<section_key>_alignment_tmp.json` will be found by existing discovery. Confirm that paragraph-only alignment JSON is enough for current timeline matching when paragraph text matches. Re-check official ElevenLabs authentication and TTS-with-timestamps docs. Record whether `alignment` maps to original text and how `normalized_alignment` should be treated. Do not edit source.

Milestone 2: Provider, output, cache, and CLI design.

Finalize the `generate-audio` command, options, metadata path, no-overwrite policy, resume policy, and normalization algorithm. Decide whether to implement `--limit`, repeatable `--section-key`, or both. Decide whether metadata is one manifest, per-section sidecars, or both. Record exact files to edit and exact tests to add. Do not edit source.

Milestone 3: Implement provider with mocked tests only.

Add the provider orchestration and ElevenLabs client abstraction. Add CLI wiring. Implement dry-run without network. Implement no-overwrite, overwrite, and reuse behavior. Implement character-timing-to-paragraph-alignment normalization. Add tests with fake responses only. Run `.venv/bin/python -m pytest`. Do not call ElevenLabs.

Milestone 4: Local validation without real API by default.

Validate dry-run against a real Phase 29 narration package. Validate mocked output in tests and temp directories. Confirm existing examples still build and validate. Run Remotion typecheck. Do not perform a real API smoke test unless the user explicitly approves it. If the user approves a real test, use `--limit 1`, temporary generated output directories, and an environment variable API key.

Milestone 5: Docs, cleanup, final review.

Update README only if the command is ready for user-facing use. Update `.gitignore` only if new generated output paths need it. Clean generated local validation outputs unless intentionally retained as fixtures. Run final pytest and Remotion typecheck. Review `git status --short --ignored`. Confirm commit candidates are source/tests/docs only. Recommend a commit message such as:

    Add ElevenLabs audio generation provider

Ask the user before Phase 31 visual asset manifest workflow.

## Explicit Exclusions

Do not call ElevenLabs while creating or implementing this plan unless a later milestone explicitly receives user approval for a real API smoke test.

Do not commit API keys, create API key config files, print API keys, or add a CLI `--api-key` option.

Do not generate production audio into `examples/audio` or production alignment into `examples/alignments` unless explicitly approved. Prefer `generated/` for validation output.

Do not overwrite existing audio or alignment outputs by default.

Do not use ffmpeg or ffprobe. Do not probe, transcode, or normalize media. Do not download B-roll. Do not render. Do not change timeline schema or Remotion props schema. Do not start visual manifest, downloader, visual duration, or Remotion visual quality work. Do not commit, tag, or push.

## Change Note

Created on 2026-05-14 to define Phase 30. The plan is intentionally design-first and network-safe. It chooses ElevenLabs Text to Speech with timestamps as the primary route, reserves Forced Alignment for future fallback, and defines mocked tests as the default validation strategy.
