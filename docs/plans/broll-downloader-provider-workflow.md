# B-roll downloader provider workflow

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, and validate a safe B-roll downloader workflow from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can now create a local visual manifest from `remotion/props.json`. That manifest says which `AI_VIDEO` and `B_ROLL` scenes need optional local visual assets, which local source files already exist under `assets/visuals/`, and which prompt or search seed should be used later. Phase 32 adds the next local workflow step: use that JSON manifest to plan and, only when explicitly run with credentials, download one provider video file per selected missing scene.

After this phase is complete, a user should be able to run:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json
    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir assets/visuals --limit 1 --dry-run

and see which scene would be searched and downloaded, without needing an API key and without writing media. With explicit user approval, a later real run can use `PEXELS_API_KEY` and write a local ignored file such as `assets/visuals/scene_001.mp4`. The command must never mutate `remotion/props.json`, must never run `prepare-visual-assets`, must never render, and must never use ffmpeg/ffprobe or media probing.

## Progress

- [x] (2026-05-15T00:55:00+07:00) Read `.agent/PLANS.md`, README, Phase 31 visual manifest plan and implementation, Phase 30 provider plan, visual asset helpers, visual manifest tests, `.gitignore`, and current `git status --short --ignored`.
- [x] (2026-05-15T00:55:00+07:00) Reviewed current official Pexels API documentation for authentication, video search, response shape, rate limits, and attribution guidance.
- [x] (2026-05-15T00:55:00+07:00) Reviewed current official Pixabay API documentation for authentication, video search, response shape, rate limits, hotlinking, and attribution/source guidance.
- [x] (2026-05-15T00:55:00+07:00) Created this Phase 32 ExecPlan.
- [x] (2026-05-15T01:20:00+07:00) Milestone 1: API and current visual manifest audit.
- [x] (2026-05-15T01:35:00+07:00) Milestone 2: downloader design.
- [x] (2026-05-15T02:05:00+07:00) Milestone 3: implement downloader with mocked tests only.
- [x] (2026-05-15T02:25:00+07:00) Milestone 4: local validation without real API by default.
- [x] (2026-05-17T00:00:00+07:00) Milestone 5: docs, cleanup, final review.

## Surprises & Discoveries

- Observation: Phase 31 JSON manifest is already suitable as the downloader input.
  Evidence: `synccut/visual_manifest.py` emits `schema_version`, `metadata`, `summary`, `supported_extensions`, and a `scenes` array with `scene_id`, `visual_type`, `prepared_status`, `local_asset_status`, `expected_asset_stem`, `expected_filenames`, `prompt`, and `search_query_seed`.
- Observation: Current local asset naming already matches the intended downloader output.
  Evidence: `synccut/visual_assets.py` discovers files by exact `scene_id` stem under `assets/visuals/`, accepts `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`, and expects exactly one supported file per target scene.
- Observation: Pexels has a focused video search endpoint and includes multiple downloadable video files in each video result.
  Evidence: Official Pexels docs describe `GET https://api.pexels.com/v1/videos/search`, required `query`, optional `orientation`, `size`, `page`, and `per_page`, and video resource fields including `url`, `duration`, `user`, and `video_files` with `quality`, `file_type`, dimensions, fps, and `link`.
- Observation: Pexels authentication is header-based and rate-limited.
  Evidence: Official Pexels docs say requests require an `Authorization` header with the API key, show successful response rate-limit headers, and state default limits of 200 requests per hour and 20,000 per month.
- Observation: Pexels attribution is encouraged even when the license allows free use.
  Evidence: Official Pexels API guidelines ask API users to show a prominent link to Pexels and always credit photographers when possible.
- Observation: Pixabay has a video search endpoint with nested rendition URLs and explicit rate/hotlinking guidance.
  Evidence: Official Pixabay docs describe `GET https://pixabay.com/api/videos/`, required `key`, query parameter `q`, optional `video_type`, `min_width`, `min_height`, `safesearch`, `order`, `page`, and `per_page`, plus response `hits[].videos.large|medium|small|tiny.url`.
- Observation: Pixabay rate limits and caching requirements need to shape any future provider implementation.
  Evidence: Official Pixabay docs state a default limit of 100 requests per 60 seconds, require search requests to be cached for 24 hours, and prohibit systematic mass downloads.
- Observation: Pixabay discourages permanent hotlinking and recommends storing videos locally.
  Evidence: Official Pixabay docs say permanent image hotlinking is not allowed and recommend storing videos on the user's server.
- Observation: Implementing both Pexels and Pixabay in one first code milestone would increase surface area without improving the first safe workflow.
  Evidence: Pexels and Pixabay differ in authentication location, search parameters, response structure, attribution/source fields, rate-limit expectations, and video rendition naming. A provider interface plus one initial real provider is lower risk.
- Observation: The Phase 31 JSON manifest contract is explicit enough for Phase 32 to avoid reading or mutating `remotion/props.json`.
  Evidence: `visual_manifest_to_dict()` emits top-level `schema_version`, `metadata`, `summary`, `supported_extensions`, and `scenes`. Each scene includes `scene_id`, `section_key`, `section`, `section_order`, `scene_order`, `visual_type`, `duration_sec`, `duration_frames`, `assets_dir`, `expected_asset_stem`, `supported_extensions`, `expected_filenames`, `prepared_status`, `public_path`, `asset_status`, `asset_source`, `local_asset_status`, `local_asset_path`, local supported/unsupported path lists, `prompt`, `search_query_seed`, `visual_data`, and `notes`.
- Observation: Empty downloader queries should be treated as ineligible, not inferred.
  Evidence: `_search_query_seed()` returns a stripped string from `visual.prompt`, `visual.description`, `visual.data.description`, or `visual.data.query`; otherwise it returns `None`. Phase 32 should not generate or rewrite queries.
- Observation: Default downloader eligibility should require both props readiness and local source-file readiness to be missing.
  Evidence: `prepared_status` tracks Remotion props readiness from `inspect_visual_asset_readiness`, while `local_asset_status` separately tracks direct child files under `assets/visuals/`. A scene with `prepared_status == "prepared"` already has a public path in props, and a scene with `local_asset_status == "found"` already has a source asset ready for `prepare-visual-assets`.
- Observation: Local source-file conflicts are already well-defined.
  Evidence: Phase 31 manifest inspection reports `duplicate_supported` for multiple supported files sharing a scene stem, `unsupported_only` for matching unsupported suffixes only, and `missing` for no matching direct child files. Phase 32 should skip or block those conflict states rather than overwrite or hide them.
- Observation: `prepare-visual-assets` mutates props and copies files, so the downloader must stay separate.
  Evidence: `prepare_visual_assets_file()` writes updated props JSON after copying to `remotion/public/visuals/`; Phase 32 is a source-file downloader and must not call it.
- Observation: The current README still says the MVP does not download B-roll.
  Evidence: README's MVP non-goals list includes no B-roll downloading, scraping, or external media fetching. Phase 32 is post-v0.1.0 roadmap work; Milestone 5 can add a short note only after implementation is ready.
- Observation: Current working tree has only the Phase 32 plan as a non-ignored candidate during this audit.
  Evidence: `git status --short --ignored` reports `?? docs/plans/broll-downloader-provider-workflow.md` plus ignored local artifacts and caches.
- Observation: Pexels remains a suitable first provider after re-checking official docs.
  Evidence: The docs provide a video-specific search endpoint, header authentication, landscape/size filtering, MP4 video file links with dimensions and fps, provider page URLs, creator metadata, and request quota headers. These map cleanly to a fakeable provider interface and metadata record.
- Observation: Pexels implementation risks are manageable but should be explicit.
  Evidence: Results can include multiple `video_files` with different orientation/size/quality, so selection must be deterministic; `video_files.link` URLs should be treated as provider download URLs; rate-limit headers should be captured when available but not required for MVP behavior.
- Observation: Pixabay remains best as an audited future provider for now.
  Evidence: Pixabay uses an API key query parameter rather than a header, has provider-specific cache requirements, returns nested `videos.large|medium|small|tiny` renditions, and has hotlinking/source guidance that differs from Pexels. It fits the same conceptual interface but would add enough branching to make Milestone 3 larger.
- Observation: Standard library HTTP remains sufficient for the first implementation.
  Evidence: Pexels search and download are simple HTTP GET requests with JSON responses and binary file downloads; no OAuth flow, streaming SDK, or multipart upload is required.
- Observation: The safest explicit scene-selection order is manifest order, even for repeatable `--scene-id`.
  Evidence: Phase 31 preserves props scene order in the manifest, and keeping all selected scenes in manifest order makes limit, explicit selection, output metadata, and tests deterministic without making user-provided option order semantically meaningful.
- Observation: Overwrite semantics are the highest-risk part of the downloader because local media may be user-curated.
  Evidence: Existing visual asset preparation fails on duplicate supported files rather than choosing between them. Phase 32 should follow the same conservative principle: `--overwrite` may replace only the exact planned `<scene_id>.mp4`, and any other same-stem file should block until the user cleans it manually.
- Observation: Reuse should happen before provider search when metadata is sufficient.
  Evidence: Reusing a prior completed download by matching metadata plus an existing local file avoids unnecessary provider API calls, respects rate limits, and keeps reruns idempotent.
- Observation: Pexels candidate selection can be deterministic without media probing.
  Evidence: Pexels response metadata includes result order, `video_files`, dimensions, `quality`, `file_type`, and provider-reported duration. Phase 32 can choose MP4 landscape candidates from metadata only and leave actual duration/readiness checks to Phase 33.
- Observation: The implementation stayed within the Milestone 2 scope.
  Evidence: Added `synccut/broll_downloader.py`, `synccut/pexels_provider.py`, CLI wiring in `synccut/cli.py`, and mocked tests in `tests/test_broll_downloader.py` plus CLI tests. No README, `.gitignore`, Remotion props, generated manifest, or media output changes were made.
- Observation: Pexels provider implementation is real but not exercised against the network in tests.
  Evidence: `PexelsVideoClient` uses stdlib `urllib.request`, `Authorization` header, `https://api.pexels.com/v1/videos/search`, `orientation=landscape`, and `per_page=10`; tests inject fake clients and do not call real Pexels or Pixabay APIs.
- Observation: Pixabay is explicitly rejected for now.
  Evidence: `download_broll_from_manifest(... provider_name="pixabay" ...)` raises a user-facing not-implemented error, with a test covering that behavior.
- Observation: Test coverage now includes downloader selection, dry-run, conflict, reuse, fake download, metadata, and CLI paths.
  Evidence: `.venv/bin/python -m pytest` passed with `288 passed`.
- Observation: The only design adjustment was CLI reporting for blocked scene reasons.
  Evidence: The CLI prints a `Blocked:` section for blocked results so local conflict output includes the underlying `--overwrite` guidance while still returning a completed report.
- Observation: Local validation passed without real provider access.
  Evidence: `.venv/bin/python -m pytest` passed with `288 passed`; `npm run typecheck` passed in `remotion/`.
- Observation: Sample timeline and props regenerated cleanly for validation.
  Evidence: `build-timeline` reported `sections: 7`, `scenes: 33`, `duration_sec: 752.79`, and `warnings: 0`; `export-remotion` reported `scenes: 33`, `sections: 7`, `duration_frames: 22584`, and `warnings: 0`.
- Observation: The sample visual manifest was valid but had no missing local assets to download.
  Evidence: `visual-manifest` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, `local_found: 17`, `local_missing: 0`, `local_duplicate_supported: 0`, and `local_unsupported_only: 0`.
- Observation: Downloader dry-run remained safe and side-effect free.
  Evidence: `download-broll generated/visual_manifest.json --provider pexels --assets-dir generated/broll-assets --limit 1 --dry-run` reported `provider: pexels`, `selected: 0`, `would_download: 0`, `blocked: 0`, and `skipped: 17`. `test ! -e generated/broll-assets` and `test ! -e generated/broll_download_manifest.json` passed.
- Observation: The zero selected count was expected for the current workspace.
  Evidence: The local `assets/visuals` pack already contains one supported file for each of the 17 target scenes, so default eligibility excludes them as `local_asset_found`.
- Observation: Cleanup completed and sample props were restored.
  Evidence: Removed `generated/visual_manifest.json`, confirmed downloader output paths absent, removed empty `generated/`, and restored `remotion/props.json`. The first `git restore remotion/props.json` was blocked by sandbox index-lock restrictions, then succeeded with explicit escalation for the requested restore.
- Observation: README needed a concise post-MVP command note.
  Evidence: README already documented `visual-manifest`, but did not mention `download-broll`. Added a short command-summary bullet and local visual workflow note covering Pexels, dry-run, `PEXELS_API_KEY`, ignored `assets/visuals/` output, and no props/prep/probe/render side effects.
- Observation: `.gitignore` already covers Phase 32 generated/local paths.
  Evidence: `.gitignore` includes `generated/` and `assets/visuals/`, plus existing ignored render/public/cache paths. No `.gitignore` change was needed.
- Observation: Final validation passed.
  Evidence: `.venv/bin/python -m pytest` passed with `288 passed`; `cd remotion && npm run typecheck` passed.
- Observation: Final cleanup/artifact review found no generated downloader outputs or props changes.
  Evidence: `test ! -e generated/visual_manifest.json`, `test ! -e generated/broll-assets`, and `test ! -e generated/broll_download_manifest.json` passed. `git status --short --ignored` showed expected source/test/docs candidates plus ignored `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `__pycache__/`, and `timeline.json`.
- Observation: Final commit candidates are source/tests/docs only.
  Evidence: Non-ignored candidates are `README.md`, `synccut/cli.py`, `tests/test_cli.py`, `docs/plans/broll-downloader-provider-workflow.md`, `synccut/broll_downloader.py`, `synccut/pexels_provider.py`, and `tests/test_broll_downloader.py`.

## Decision Log

- Decision: Use `download-broll` as the Phase 32 command name.
  Rationale: The command consumes a visual manifest and downloads stock B-roll-style videos for target scenes. The name is specific enough to distinguish it from `prepare-visual-assets` and future visual duration/readiness work.
  Date/Author: 2026-05-15 / Codex
- Decision: Use Phase 31 JSON manifest as the only input for downloader scene selection.
  Rationale: It contains scene ids, target visual types, local prepared/source availability, expected filenames, and search seeds. Using it avoids mutating `remotion/props.json` and keeps the downloader decoupled from rendering.
  Date/Author: 2026-05-15 / Codex
- Decision: Implement Pexels first in Milestone 3 with a provider interface that can support Pixabay later.
  Rationale: Pexels has a straightforward video search endpoint, explicit landscape orientation support, and MP4 `video_files`. Auditing Pixabay is still required, but implementing both providers at once would make Phase 32 larger and riskier.
  Date/Author: 2026-05-15 / Codex
- Decision: Keep Pixabay as an audited, designed, not-yet-implemented provider unless Milestone 2 uncovers a Pexels blocker.
  Rationale: The user explicitly allowed implementing one provider first if both are too large. Pexels-first is enough to validate the provider workflow and downloader safety rules.
  Date/Author: 2026-05-15 / Codex
- Decision: API keys come only from environment variables.
  Rationale: Provider keys are secrets. There must be no `--api-key` option, no committed key file, no generated key config, and no key printing.
  Date/Author: 2026-05-15 / Codex
- Decision: Dry-run must not read API keys, call providers, create asset directories, or download media.
  Rationale: Dry-run should be a safe planning mode that works without credentials, network, cost, or filesystem side effects.
  Date/Author: 2026-05-15 / Codex
- Decision: Do not probe or enforce media duration in Phase 32.
  Rationale: Phase 33 is reserved for visual duration/readiness handling. Phase 32 may record provider-reported duration metadata, but it must not run ffmpeg/ffprobe or make duration suitability decisions based on probing downloaded media.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 1 confirms Phase 31 JSON manifest remains the sole downloader input.
  Rationale: The manifest already contains the scene identifiers, target type, read-only search seed, expected naming, prepared props readiness, and local source-file availability needed by the downloader.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 1 confirms Pexels-first implementation and Pixabay as future/audited provider.
  Rationale: Pexels has the lower-risk first implementation path. Pixabay is documented enough to design the interface, but implementing it in the first code milestone would add query-auth, cache, rendition-selection, and attribution differences before the workflow is proven.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 1 confirms default eligible scenes are missing target scenes with a non-empty query.
  Rationale: The downloader should select only `AI_VIDEO`/`B_ROLL` manifest scenes where `prepared_status == "missing"`, `local_asset_status == "missing"`, and `search_query_seed` is non-empty. Scenes with found, duplicate, or unsupported local files should be skipped or blocked with a reason.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 1 confirms API-key behavior remains environment-only and dry-run remains side-effect free.
  Rationale: `PEXELS_API_KEY` is required only for real Pexels runs; dry-run must not read environment variables, call providers, create directories, write metadata/media, or download files. There will be no `--api-key` option or key config file.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 1 confirms Phase 32 will not mutate props, prepare visual assets, probe media, or render.
  Rationale: `prepare-visual-assets` is the existing props/public-copy step, while Phase 32 should only plan/download local ignored source assets. Media duration/readiness and Remotion quality work belong to later phases.
  Date/Author: 2026-05-15 / Codex
- Decision: Final command shape is `synccut download-broll VISUAL_MANIFEST_JSON --provider pexels --assets-dir assets/visuals [--metadata-out generated/broll_download_manifest.json] [--dry-run] [--overwrite] [--limit N] [--scene-id SCENE_ID]...`.
  Rationale: This matches the Phase 31 handoff artifact, keeps provider selection explicit, writes local source assets to the existing visual asset directory, and gives users safe dry-run and bounded selection controls.
  Date/Author: 2026-05-15 / Codex
- Decision: Milestone 3 will implement provider `pexels` only; `pixabay` will be rejected with a clear "not implemented yet" error.
  Rationale: Pexels is enough to prove the downloader workflow. Keeping Pixabay audited but unimplemented reduces first-pass scope and avoids mixing two distinct authentication/response/cache contracts in one milestone.
  Date/Author: 2026-05-15 / Codex
- Decision: There will be no `--api-key` CLI option.
  Rationale: Real Pexels runs read `PEXELS_API_KEY` from the environment only. Dry-run does not read it. The key is never printed, persisted, or accepted through project config.
  Date/Author: 2026-05-15 / Codex
- Decision: `--limit` and `--scene-id` are mutually exclusive.
  Rationale: Rejecting both together avoids ambiguous selection semantics and keeps CLI behavior easy to explain.
  Date/Author: 2026-05-15 / Codex
- Decision: Explicit `--scene-id` output order follows manifest scene order, not option order.
  Rationale: Manifest order is already deterministic and corresponds to video order. This keeps metadata and summary output stable across command invocations.
  Date/Author: 2026-05-15 / Codex
- Decision: Default eligible scenes require `visual_type` `AI_VIDEO` or `B_ROLL`, `prepared_status == "missing"`, `local_asset_status == "missing"`, and non-empty `search_query_seed`.
  Rationale: The downloader should fill only absent optional local assets. Already prepared scenes, local source files, duplicate/unsupported local files, and missing queries should not trigger provider calls.
  Date/Author: 2026-05-15 / Codex
- Decision: Ineligible/skip reasons are `non_target`, `already_prepared`, `local_asset_found`, `local_duplicate_supported`, `local_unsupported_only`, `no_search_query`, `unsupported_prepared_status`, and `scene_id_not_found`.
  Rationale: These reasons map directly to manifest state and make dry-run/action output auditable.
  Date/Author: 2026-05-15 / Codex
- Decision: Before a real write, inspect direct child files in `assets_dir` whose stem equals the selected scene id.
  Rationale: This mirrors Phase 31 local asset inspection and avoids overwriting or masking existing local media. It does not recurse and does not probe file contents.
  Date/Author: 2026-05-15 / Codex
- Decision: `--overwrite` replaces only the planned `assets_dir/<scene_id>.mp4`; if any other same-stem supported or unsupported file exists, block and ask the user to clean it manually.
  Rationale: Deleting or choosing among local user media is risky. The downloader should not remove unplanned files.
  Date/Author: 2026-05-15 / Codex
- Decision: Reuse is checked before provider search when metadata and file match.
  Rationale: If metadata proves the same `scene_id`, `provider`, `query`, `provider_asset_id`, and `asset_path`, and the file exists, the command can report `reused` without using provider quota.
  Date/Author: 2026-05-15 / Codex
- Decision: Pexels search uses `query = search_query_seed`, `orientation=landscape`, and `per_page=10`.
  Rationale: This biases toward 16:9-ish B-roll without adding duration/media probing. The fixed small page size reduces API use and keeps tests deterministic.
  Date/Author: 2026-05-15 / Codex
- Decision: Candidate acceptance requires `video/mp4`; prefer landscape files, larger width, then `hd` quality when tied.
  Rationale: Existing visual asset support accepts `.mp4`, and Remotion already handles local videos. Metadata-based selection avoids ffmpeg/ffprobe and keeps Phase 33 responsible for duration/readiness work.
  Date/Author: 2026-05-15 / Codex
- Decision: No acceptable Pexels candidate records a per-scene blocked result with reason `no_acceptable_candidate` and continues other selected scenes.
  Rationale: One weak search result should not abort a whole batch. Users can adjust search seeds or try a future provider later.
  Date/Author: 2026-05-15 / Codex
- Decision: Metadata output defaults to `generated/broll_download_manifest.json`.
  Rationale: `generated/` is ignored and already used by prior phases for local planning artifacts. Metadata should preserve provider, attribution, selected source, and reuse keys without being committed by default.
  Date/Author: 2026-05-15 / Codex
- Decision: Provider orchestration lives in `synccut/broll_downloader.py`; real Pexels HTTP client lives in `synccut/pexels_provider.py`.
  Rationale: Separating orchestration from HTTP keeps tests fakeable and avoids real provider calls in CLI/unit tests.
  Date/Author: 2026-05-15 / Codex
- Decision: Keep blocked scene conflicts as reportable results instead of raising when the command can finish a batch.
  Rationale: A batch downloader should continue across scenes and write/report metadata for non-dry-run attempts. CLI output now prints blocked reasons, including `--overwrite` guidance for local-file conflicts.
  Date/Author: 2026-05-15 / Codex
- Decision: Update README with a concise `download-broll` note.
  Rationale: The command is now user-facing enough to mention alongside `visual-manifest`, but README should avoid duplicating full provider API details.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not edit `.gitignore`.
  Rationale: `generated/` covers visual manifests and downloader metadata, and `assets/visuals/` covers local downloaded media. The implementation introduced no new unignored generated path.
  Date/Author: 2026-05-17 / Codex

## Outcomes & Retrospective

This plan has been created but not implemented. No source code, tests, README, `.gitignore`, generated manifests, downloaded media, copied assets, API calls, ffmpeg/ffprobe work, media probing/transcoding/normalization, Remotion renders, props mutations, commits, tags, or pushes were performed while authoring the plan.

The intended outcome is a safe, provider-based downloader foundation. At completion, `synccut download-broll` should read a Phase 31 visual manifest JSON, select scenes that are missing local source files, plan or perform a provider search, write one local ignored media file per selected scene only when explicitly run with credentials, and record metadata/attribution needed for review and later preparation.

Milestone 1 audit is complete. The Phase 31 manifest is sufficient as a stable handoff, local asset naming and conflict states are already deterministic, Pexels remains the recommended initial provider, Pixabay remains audited for a later provider implementation, and no blocker was found for a stdlib `urllib.request` Pexels client with fake-client tests. Next step: Milestone 2 should turn these audit findings into the exact downloader command/options, provider interface, selection rules, metadata schema, and test list before code changes.

Milestone 2 design is complete. The final implementation plan is a Pexels-only first downloader with a provider interface, dry-run that performs no environment reads/network/filesystem writes, manifest-order scene selection, conservative local-file conflict handling, reuse-before-search based on metadata, deterministic Pexels MP4 candidate selection from provider metadata only, and mocked tests that never hit real APIs. Next step: Milestone 3 should implement only this contract in `synccut/broll_downloader.py`, `synccut/pexels_provider.py`, `synccut/cli.py`, and focused tests.

Milestone 3 implementation is complete. `synccut download-broll` now consumes Phase 31 visual manifest JSON, supports provider `pexels`, rejects `pixabay` as not implemented yet, supports dry-run, limit, repeatable scene selection, conservative overwrite handling, metadata reuse before provider search, fakeable provider clients, and deterministic metadata output. `PexelsVideoClient` is implemented with stdlib `urllib.request`, but no real API call was made. Tests were added for the core downloader and CLI behavior, and `.venv/bin/python -m pytest` passed with `288 passed`. Next step: Milestone 4 should validate local dry-run behavior with a sample generated visual manifest, still without real provider calls.

Milestone 4 local validation is complete. The full Python suite passed, sample timeline/props generation completed with zero warnings, visual manifest generation produced 17 target scenes, and the downloader dry-run required no API key, made no provider call, created no `generated/broll-assets` directory, wrote no downloader metadata, and downloaded no media. Because all current sample target scenes already have local source assets under `assets/visuals`, dry-run selected zero eligible downloads and skipped 17 scenes. Remotion typecheck passed. Generated validation files were cleaned, `remotion/props.json` was restored, and no real API call, download, visual preparation, render, media probe, or props mutation remains. Next step: Milestone 5 docs/cleanup/final review.

Milestone 5 final review is complete. README now contains a concise `download-broll` note, `.gitignore` required no change, final pytest and Remotion typecheck passed, generated downloader outputs are absent, `remotion/props.json` is not modified, and no API-key/config files or downloaded media are commit candidates. Phase 32 acceptance criteria are satisfied: the workflow consumes Phase 31 JSON manifests, implements Pexels as the first provider, rejects Pixabay as not implemented yet, supports safe dry-run/no-overwrite/reuse/metadata behavior, tests use fake clients without real API calls, and no ffmpeg/ffprobe/probing/rendering/props mutation is involved. Recommended commit message: `Add Pexels B-roll downloader workflow`. Next step: ask the user before starting Phase 33 visual duration/readiness handling.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python CLI under `synccut/`. The Remotion app lives under `remotion/`, but Phase 32 should not edit Remotion source, run Remotion renders, or mutate `remotion/props.json`.

Phase 31 added a command that writes a visual manifest:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json

The JSON manifest has this high-level shape:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut visual-manifest",
        "source_props": "remotion/props.json",
        "assets_dir": "assets/visuals",
        "format": "json"
      },
      "summary": {...},
      "supported_extensions": [".jpeg", ".jpg", ".mov", ".mp4", ".png", ".webm", ".webp"],
      "scenes": [
        {
          "scene_id": "scene_001",
          "visual_type": "AI_VIDEO",
          "prepared_status": "missing",
          "local_asset_status": "missing",
          "expected_asset_stem": "assets/visuals/scene_001",
          "expected_filenames": [...],
          "prompt": "...",
          "search_query_seed": "..."
        }
      ]
    }

The downloader should not read `remotion/props.json` directly. It should trust the manifest as the handoff artifact. A target scene is a manifest scene whose `visual_type` is `AI_VIDEO` or `B_ROLL`. In this phase, a scene is eligible for default download only when `prepared_status` is `missing`, `local_asset_status` is `missing`, and `search_query_seed` is a non-empty string. Scenes with `local_asset_status` `found`, `duplicate_supported`, or `unsupported_only` should be skipped or reported as blocked because downloading would risk overwriting or hiding an existing local asset problem.

The existing local asset convention is:

    assets/visuals/<scene_id>.<supported_ext>

`prepare-visual-assets` later copies those files into `remotion/public/visuals/` and annotates props. Phase 32 must not run that command. It only creates or reports local source files.

Important existing files:

    synccut/visual_manifest.py
    synccut/visual_assets.py
    synccut/cli.py
    tests/test_visual_manifest.py
    tests/test_visual_assets.py
    tests/test_cli.py
    .gitignore

Likely new implementation files:

    synccut/broll_downloader.py
    synccut/pexels_provider.py
    tests/test_broll_downloader.py

Potential future file if Pixabay is implemented later:

    synccut/pixabay_provider.py

Generated and local-only paths must stay out of commits:

    generated/
    assets/visuals/
    remotion/public/
    remotion/out/
    timeline.json
    .venv/
    remotion/node_modules/
    .pytest_cache/
    __pycache__/

## Provider API Audit Embedded In This Plan

Pexels official API facts used by this plan:

- API documentation URL: `https://www.pexels.com/api/documentation/`.
- Video endpoints live under `https://api.pexels.com/v1/videos/`; older `https://api.pexels.com/videos/` paths are deprecated.
- Video search endpoint: `GET https://api.pexels.com/v1/videos/search`.
- Authentication: every request includes an `Authorization` header containing the API key.
- Relevant search parameters: required `query`; optional `orientation` with values such as `landscape`, `portrait`, or `square`; optional `size`; `page`; and `per_page` with a maximum of 80.
- Response includes a `videos` array. A video includes `id`, `width`, `height`, `url`, `image`, `duration`, `user`, `video_files`, and `video_pictures`.
- Each `video_files` entry includes `quality`, `file_type`, `width`, `height`, `fps`, and `link`.
- Rate limits are 200 requests per hour and 20,000 requests per month by default, with successful response headers including `X-Ratelimit-Limit`, `X-Ratelimit-Remaining`, and `X-Ratelimit-Reset`.
- Attribution/source guidance asks API users to show a prominent Pexels link and credit creators when possible. The downloader metadata must retain provider, Pexels page URL, creator name, creator URL, and the provider asset id.

Pixabay official API facts used by this plan:

- API documentation URL: `https://pixabay.com/api/docs/`.
- Video search endpoint: `GET https://pixabay.com/api/videos/`.
- Authentication: `key` query parameter is required.
- Relevant search parameters: `q` for search term, `video_type`, `category`, `min_width`, `min_height`, `editors_choice`, `safesearch`, `order`, `page`, and `per_page`.
- The `q` search term may not exceed 100 characters.
- Response includes `total`, `totalHits`, and `hits`.
- Each hit can include `id`, `pageURL`, `type`, `tags`, `duration`, `videos`, `views`, `downloads`, `likes`, `comments`, `user_id`, `user`, and `userImageURL`.
- `videos` contains renditions such as `large`, `medium`, `small`, and `tiny`, each with `url`, `width`, `height`, `size`, and `thumbnail`. The docs say `medium`, `small`, and `tiny` are available for all videos; `large` can have an empty URL.
- Rate limit is 100 requests per 60 seconds by default. Search requests must be cached for 24 hours. Systematic mass downloads are not allowed.
- Returned image URLs are only for temporary display, permanent image hotlinking is not allowed, and videos are recommended to be stored locally. Downloader metadata must retain provider, Pixabay page URL, creator name/id, tags, source URL, and the provider asset id.

## Plan of Work

### Milestone 1: API and current visual manifest audit

Audit without editing source. Confirm the current Phase 31 JSON manifest fields and verify scene eligibility rules. Read `synccut/visual_manifest.py`, `tests/test_visual_manifest.py`, `synccut/visual_assets.py`, `tests/test_visual_assets.py`, `synccut/cli.py`, and `README.md`. Confirm that `assets/visuals/<scene_id>.<ext>` remains the expected local naming policy and that `prepare-visual-assets` requires exactly one supported file per target scene.

Audit official Pexels and Pixabay docs again if needed, but do not call either API. Record authentication, endpoints, response shape, downloadable URL fields, rate limits, caching/attribution/license notes, and implementation risks in `Surprises & Discoveries`. Confirm dry-run and tests must not call providers.

### Milestone 2: Downloader design

Finalize the implementation contract before coding. The command shape is:

    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir assets/visuals --dry-run
    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir assets/visuals --limit 1

Final design should include:

- command name: `download-broll`
- positional input: Phase 31 `VISUAL_MANIFEST_JSON`
- `--provider pexels`, with `pixabay` rejected until implemented unless Milestone 2 changes scope deliberately
- `--assets-dir assets/visuals` default
- `--metadata-out generated/broll_download_manifest.json` default
- `--dry-run`
- `--overwrite`
- `--limit N`
- repeatable `--scene-id SCENE_ID`
- reject `--limit` with `--scene-id` together unless a clear deterministic order is documented
- no `--api-key` option
- Pexels key from `PEXELS_API_KEY`; Pixabay future key from `PIXABAY_API_KEY`
- dry-run does not read environment variables, create `assets_dir`, call providers, or write metadata/media
- non-dry-run fails before provider calls if selected provider key is missing
- default scene eligibility: `visual_type` in `AI_VIDEO`/`B_ROLL`, `prepared_status == "missing"`, `local_asset_status == "missing"`, non-empty `search_query_seed`
- skip or report ineligible scenes with reasons, including already local, duplicate supported, unsupported local, no query, unsupported prepared status, and non-target type
- real run creates `assets_dir` only when writing a downloaded file
- never overwrite an existing `assets/visuals/<scene_id>.*` file by default
- block when any supported or unsupported local file with the same scene stem already exists unless `--overwrite`
- if metadata proves the same provider/query/scene/asset output was already written and file exists, report reuse before provider search
- write media through a temporary sibling file then rename
- save Pexels downloads as `<scene_id>.mp4` only when the selected candidate is `video/mp4`
- do not accept unknown file types in the first implementation
- do not infer duration suitability or run media probing
- record provider-reported duration in metadata if available, but do not enforce it
- provider candidate selection is deterministic: search with `orientation=landscape`, `per_page` small and fixed, choose the first acceptable video result in provider order, then choose the best acceptable MP4 file by landscape ratio and larger width, preferring HD when available
- if no acceptable candidate exists, report the scene as blocked or skipped with a clear reason
- final Milestone 2 choices:
  - `--limit` and `--scene-id` are mutually exclusive
  - repeatable `--scene-id` results are emitted in manifest order
  - unsupported provider `pixabay` exits with "provider pixabay is not implemented yet"
  - ineligible reasons are `non_target`, `already_prepared`, `local_asset_found`, `local_duplicate_supported`, `local_unsupported_only`, `no_search_query`, `unsupported_prepared_status`, and `scene_id_not_found`
  - real writes inspect only direct children of `assets_dir` with matching scene stem
  - `--overwrite` may replace only the planned `<scene_id>.mp4`
  - other same-stem files still block even with `--overwrite`
  - dry-run creates no `assets_dir`, no metadata, and no generated files
  - non-dry-run without an injected fake client fails before provider/network if `PEXELS_API_KEY` is missing

Metadata shape should be deterministic JSON with two-space indentation, `ensure_ascii=False`, and trailing newline:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut download-broll",
        "source_visual_manifest": "generated/visual_manifest.json",
        "provider": "pexels",
        "assets_dir": "assets/visuals"
      },
      "summary": {
        "selected": 1,
        "written": 1,
        "reused": 0,
        "blocked": 0,
        "skipped": 0
      },
      "scenes": [
        {
          "scene_id": "scene_001",
          "status": "written",
          "query": "...",
          "provider": "pexels",
          "provider_asset_id": "1448735",
          "provider_asset_url": "https://www.pexels.com/video/...",
          "creator_name": "...",
          "creator_url": "...",
          "download_url": "...",
          "asset_path": "assets/visuals/scene_001.mp4",
          "file_type": "video/mp4",
          "width": 1920,
          "height": 1080,
          "provider_duration_sec": 32,
          "attribution": "Video by ... on Pexels"
        }
      ]
    }

Provider interface design should be fakeable. A simple shape is enough:

    @dataclass(frozen=True)
    class BrollCandidate:
        provider: str
        provider_asset_id: str
        provider_asset_url: str
        creator_name: str | None
        creator_url: str | None
        download_url: str
        file_type: str
        width: int | None
        height: int | None
        duration_sec: int | None
        attribution: str

    class BrollProviderClient:
        def search(self, query: str, *, per_page: int) -> list[BrollCandidate]: ...
        def download(self, candidate: BrollCandidate) -> bytes: ...

The real Pexels implementation should use standard library `urllib.request`. Add no dependency unless Milestone 2 records a concrete blocker.

Final metadata shape for Milestone 3 is:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut download-broll",
        "source_visual_manifest": "generated/visual_manifest.json",
        "provider": "pexels",
        "assets_dir": "assets/visuals"
      },
      "summary": {
        "selected": 1,
        "written": 1,
        "reused": 0,
        "blocked": 0,
        "skipped": 0
      },
      "scenes": [
        {
          "scene_id": "scene_001",
          "status": "written",
          "reason": null,
          "query": "semiconductor wafer factory",
          "provider": "pexels",
          "provider_asset_id": "12345",
          "provider_asset_url": "https://www.pexels.com/video/12345/",
          "creator_name": "Creator Name",
          "creator_url": "https://www.pexels.com/@creator",
          "download_url": "https://...",
          "asset_path": "assets/visuals/scene_001.mp4",
          "file_type": "video/mp4",
          "width": 1920,
          "height": 1080,
          "provider_duration_sec": 12,
          "attribution": "Video by Creator Name on Pexels"
        }
      ]
    }

Metadata JSON must use `indent=2`, `ensure_ascii=False`, a trailing newline, and deterministic scene order. Reuse requires an existing scene metadata entry with matching `scene_id`, `provider`, `query`, `provider_asset_id`, and `asset_path`, plus an existing file at `asset_path`. If the metadata/file match is present, no provider search or download is needed.

Final provider abstraction for Milestone 3:

    @dataclass(frozen=True)
    class BrollCandidate:
        provider: str
        provider_asset_id: str
        provider_asset_url: str
        creator_name: str | None
        creator_url: str | None
        download_url: str
        file_type: str
        width: int | None
        height: int | None
        duration_sec: int | None
        attribution: str

    class BrollProviderClient(Protocol):
        def search(self, query: str, *, per_page: int = 10) -> list[BrollCandidate]: ...
        def download(self, candidate: BrollCandidate) -> bytes: ...

Orchestration tests should inject a fake `BrollProviderClient`. CLI tests should cover validation/dry-run directly and monkeypatch orchestration or provider creation for network-free success tests.

Final Pexels implementation contract:

- module: `synccut/pexels_provider.py`
- HTTP library: standard library `urllib.request`
- API key source: `PEXELS_API_KEY`, read only immediately before a real request
- search endpoint: `https://api.pexels.com/v1/videos/search`
- header: `Authorization: <key>`
- query parameters: `query`, `orientation=landscape`, `per_page=10`
- normalize each Pexels video result and acceptable MP4 file into `BrollCandidate`
- download `candidate.download_url` as bytes
- safe errors for missing key, HTTP/network failure, invalid JSON, missing `videos`, no usable `video_files`, and empty download bytes
- never include the API key in exceptions, logs, metadata, or output

Final tests for Milestone 3:

- eligible scene selection from Phase 31-style manifest
- skip non-target scenes if present
- skip already prepared scene
- skip local found scene
- skip duplicate-supported scene
- skip unsupported-only scene
- skip no-query scene
- explicit `--scene-id` unknown reports `scene_id_not_found`
- `--limit` selects first N eligible scenes
- repeatable `--scene-id` selects explicit eligible scenes in manifest order
- `--limit` plus `--scene-id` rejected
- dry-run writes no files, creates no `assets_dir`, calls no provider, and reads no environment
- missing `PEXELS_API_KEY` blocks before provider call
- fake Pexels candidate writes `<scene_id>.mp4`
- metadata file is written with deterministic fields and attribution
- reuse before provider call when metadata/file match
- existing same-stem local file without matching metadata blocks and mentions `--overwrite`
- `--overwrite` replaces only planned `<scene_id>.mp4`
- multiple same-stem conflicts block even with overwrite if not only the planned path
- no acceptable candidate records blocked reason `no_acceptable_candidate`
- unsupported provider `pixabay` rejected as not implemented
- CLI dry-run output includes provider, selected/would-download counts, and no key requirement
- CLI missing API key output mentions `PEXELS_API_KEY`
- CLI conflict output mentions `--overwrite`
- CLI success output is network-free through monkeypatch/fake orchestration

Implementation files for Milestone 3:

    synccut/broll_downloader.py
    synccut/pexels_provider.py
    synccut/cli.py
    tests/test_broll_downloader.py
    tests/test_cli.py
    docs/plans/broll-downloader-provider-workflow.md

No README or `.gitignore` changes are planned for Milestone 3.

### Milestone 3: Implement downloader with mocked tests only

Expected files:

    synccut/broll_downloader.py
    synccut/pexels_provider.py
    synccut/cli.py
    tests/test_broll_downloader.py
    tests/test_cli.py
    docs/plans/broll-downloader-provider-workflow.md

Do not implement Pixabay in Milestone 3 unless Milestone 2 records a deliberate scope change and the user has accepted that scope. The default implementation is Pexels only with a provider abstraction ready for later Pixabay.

Implementation requirements:

- load and validate Phase 31 JSON manifest
- select default eligible scenes only
- support `--limit` and repeatable `--scene-id`
- reject `--limit` plus `--scene-id` together
- support dry-run with no filesystem writes, no environment reads, no provider calls
- support no-overwrite and `--overwrite`
- support metadata-based reuse when planned file exists and metadata entry matches provider, query, scene id, provider asset id, and asset path
- use fake provider clients in tests
- never call real Pexels/Pixabay in tests
- never write to `examples/audio`, `examples/alignments`, `remotion/public`, or `remotion/out`
- never mutate `remotion/props.json`
- never run `prepare-visual-assets`
- never use ffmpeg/ffprobe or media probing

Tests to add:

- load Phase 31-style manifest and select only eligible missing AI/B-roll scenes
- skip scenes with local found assets
- skip/block duplicate-supported and unsupported-only local states
- skip scenes with empty search seed
- dry-run writes nothing, creates no assets dir, calls no provider, and reads no API key
- missing `PEXELS_API_KEY` blocks before provider call in non-dry-run when no injected client is used
- fake provider search and fake download write `assets_dir/<scene_id>.mp4`
- metadata JSON records provider asset, creator, attribution, query, file path, and provider-reported duration
- reuse when file and metadata match
- block when local file exists without matching metadata
- overwrite replaces only planned output
- limit selects first N eligible scenes
- scene-id selects requested scenes
- reject limit plus scene-id
- unsupported provider is rejected
- no acceptable candidate is reported clearly
- CLI dry-run output
- CLI missing API key output mentions `PEXELS_API_KEY`
- CLI conflict output mentions `--overwrite`
- CLI success output can use a monkeypatched orchestration result to stay network-free

### Milestone 4: Local validation without real API by default

Run from repository root:

    .venv/bin/python -m pytest

Prepare sample props and a JSON manifest if needed:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json

Validate dry-run into an ignored/generated asset directory:

    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir generated/broll-assets --limit 1 --dry-run

Expected dry-run behavior:

- no API key required
- no provider API call
- no `generated/broll-assets` directory created
- no media downloaded
- output reports selected scene count and would-download count

Run Remotion typecheck:

    cd remotion && npm run typecheck && cd ..

Do not run a real API smoke test unless the user explicitly approves it. If approved later, use `--limit 1`, write under `generated/`, never print the API key, record provider rate/license notes, and clean generated smoke outputs unless the user asks to keep them.

### Milestone 5: Docs, cleanup, final review

README update is optional and should be concise if the command is ready for user-facing use. It should say that `download-broll` consumes a visual manifest JSON, supports provider `pexels`, dry-run is safe and keyless, real runs require `PEXELS_API_KEY`, and downloaded media should remain local/ignored.

`.gitignore` should not need changes because `generated/` and `assets/visuals/` are already ignored. Change it only if implementation introduces a new generated path outside current ignore policy.

Cleanup:

- remove `generated/visual_manifest.json` if created for validation
- remove `generated/broll-assets` if created for validation or smoke tests
- remove `generated/broll_download_manifest.json` if created for validation or smoke tests
- restore `remotion/props.json` if it changed only because sample props were regenerated
- leave `timeline.json` ignored unless normal cleanup policy removes it

Final validation:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

Expected commit candidates after implementation:

    synccut/broll_downloader.py
    synccut/pexels_provider.py
    synccut/cli.py
    tests/test_broll_downloader.py
    tests/test_cli.py
    docs/plans/broll-downloader-provider-workflow.md
    README.md only if updated

Not expected as commit candidates:

    generated/*
    assets/visuals/*
    remotion/props.json
    remotion/public/*
    remotion/out/*
    downloaded media
    API key files
    .venv/
    remotion/node_modules/
    caches

Recommended commit message:

    Add Pexels B-roll downloader workflow

After Phase 32, ask the user before starting Phase 33 visual duration/readiness handling.

## Concrete Steps

Milestone 1 audit commands:

    sed -n '1,320p' synccut/visual_manifest.py
    sed -n '1,260p' synccut/visual_assets.py
    sed -n '1,360p' synccut/cli.py
    sed -n '1,260p' tests/test_visual_manifest.py
    sed -n '1,260p' tests/test_visual_assets.py
    sed -n '1,360p' tests/test_cli.py
    git status --short --ignored

Milestone 4 validation commands:

    .venv/bin/python -m pytest
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json
    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir generated/broll-assets --limit 1 --dry-run
    cd remotion && npm run typecheck && cd ..

Milestone 5 final validation commands:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

## Validation and Acceptance

Acceptance criteria:

- `synccut download-broll` exists.
- The command consumes Phase 31 visual manifest JSON.
- The command supports provider `pexels` with a provider abstraction that can later support `pixabay`.
- The command selects missing `AI_VIDEO` and `B_ROLL` scenes with search seeds and no local source files.
- Dry-run requires no API key, makes no network call, writes no media, creates no asset directory, and reports selected/would-download counts.
- Real non-dry-run Pexels use requires `PEXELS_API_KEY` from the environment only.
- No API key is accepted as a CLI option, printed, or written to disk.
- Existing local assets are not overwritten by default.
- Downloaded files are named `assets/visuals/<scene_id>.mp4` or another explicitly supported provider file suffix.
- Metadata/attribution JSON is written for real downloads.
- Tests use fake provider clients and never call real APIs.
- Python tests pass.
- Remotion typecheck passes.
- No ffmpeg/ffprobe/probing/transcoding/normalization/rendering is used.
- `remotion/props.json` is not mutated by the downloader.
- Generated/downloaded validation artifacts are ignored or cleaned before final review.

## Idempotence and Recovery

The command must be safe to rerun. Dry-run is side-effect free. A real run should reuse an existing file only when metadata proves it was downloaded for the same scene, provider, query, provider asset, and path. If a matching local file exists without matching metadata, the command must block and mention `--overwrite`. With `--overwrite`, it may replace only the planned output file for the selected scene and update metadata for that scene.

All media writes must use a temporary sibling file and rename into place after the download bytes are fully written. If a provider response is malformed or a download fails, do not leave a partial final media file. If validation regenerates `remotion/props.json`, restore it before final review unless the user explicitly approves a sample props refresh.

## Artifacts and Notes

Generated local planning and metadata outputs:

    generated/visual_manifest.json
    generated/broll_download_manifest.json
    generated/broll-assets/

These should not be committed.

Real local downloaded assets:

    assets/visuals/<scene_id>.mp4

These are local-only source media and should not be committed.

Provider attribution metadata is important. Even when a provider license permits broad use, metadata should preserve provider name, provider asset page URL, creator name, creator URL if available, query, provider asset id, and selected download URL. This helps later human review and video description attribution.

## Interfaces and Dependencies

Use Python standard library `urllib.request` for the first real Pexels client unless Milestone 2 records a concrete blocker. Do not add a third-party HTTP dependency by default.

In `synccut/broll_downloader.py`, define provider-agnostic dataclasses and orchestration functions. Suggested public objects:

    BrollCandidate
    BrollDownloadSceneResult
    BrollDownloadResult
    download_broll_from_manifest(...)

In `synccut/pexels_provider.py`, define:

    PexelsVideoClient

The real Pexels client should read `PEXELS_API_KEY` only immediately before a real network request, send it in the `Authorization` header, query `https://api.pexels.com/v1/videos/search`, normalize results into `BrollCandidate`, and download the selected candidate URL as bytes. Tests should inject fake clients into `download_broll_from_manifest` rather than hitting the network.

Do not implement `synccut/pixabay_provider.py` in Milestone 3 unless the Milestone 2 design deliberately changes scope and records why. Pixabay is audited here so that its future implementation can conform to the same provider interface.

## Change Note

Revision 2026-05-15: Initial Phase 32 ExecPlan created. The plan uses Phase 31 visual manifest JSON as input, audits Pexels and Pixabay official API contracts, chooses Pexels-first implementation with a future-ready provider interface, requires env-var-only API keys, defines dry-run/no-overwrite/metadata behavior, forbids media probing/rendering/props mutation, and keeps real API smoke tests user-approved only.
