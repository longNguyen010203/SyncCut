# Build a local visual asset pack workflow for the TSMC sample

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to complete this phase from this file without reading earlier conversation or external documentation.

## Purpose / Big Picture

The SyncCut v0.1 MVP can already render the TSMC sample, but `AI_VIDEO` and `B_ROLL` scenes still fall back to metadata placeholders unless local visual files are supplied. This phase makes the TSMC sample easier to improve by inventorying every target visual scene, documenting the exact filenames needed under `assets/visuals/`, and validating the existing local visual asset workflow with a tiny ignored synthetic subset.

After this phase, a maintainer should have a text-only manifest at `docs/tsmc-visual-asset-manifest.md` that tells a human or future media-production tool which local files to create for the 17 target scenes. The existing command `synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` should remain the way those files are copied into Remotion's public directory. This phase must not generate AI video or images, download B-roll, scrape or fetch external media, call ffmpeg directly, probe, decode, transcode, or normalize media, change Python command behavior, change timeline or Remotion schemas, add GUI or web app behavior, or commit large generated media assets by default.

## Progress

- [x] (2026-05-12T19:56:49+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, `README.md`, `docs/release-checklist-v0.1.md`, `docs/future-phases.md`, `docs/schemas.md`, `docs/plans/remotion-visual-asset-strategy.md`, `docs/plans/visual-asset-readiness-report.md`, `docs/plans/preflight-render-readiness.md`, `docs/plans/preflight-file-verification.md`, `docs/plans/v0.1-release-hardening.md`, `remotion/README.md`, `remotion/package.json`, and `.gitignore`.
- [x] (2026-05-12T19:56:49+07:00) Inspected `remotion/props.json`, `synccut/visual_assets.py`, `synccut/preflight.py`, `tests/test_visual_assets.py`, `tests/test_preflight.py`, `remotion/src/components/AiVideoScene.tsx`, `remotion/src/components/BRollScene.tsx`, and `remotion/src/components/VisualAssetScene.tsx`.
- [x] (2026-05-12T19:56:49+07:00) Created this ExecPlan for the TSMC visual asset pack workflow.
- [x] (2026-05-12T20:06:12+07:00) Completed Milestone 1: created the text-only TSMC visual asset manifest from the current props inventory.
- [x] (2026-05-12T20:12:46+07:00) Completed Milestone 2: validated the workflow with a tiny ignored synthetic partial asset pack for `scene_001`, `scene_003`, and `scene_004`.
- [x] (2026-05-12T20:24:36+07:00) Completed Milestone 3: reviewed user-facing docs, left README files unchanged, and restored clean props without synthetic visual paths.
- [ ] Milestone 4: final review, validation, and commit policy for the plan and manifest.

## Surprises & Discoveries

- Observation: The current TSMC sample has exactly 17 target visual scenes.
  Evidence: Inspecting `remotion/props.json` found 17 scenes whose `visual_type` is `AI_VIDEO` or `B_ROLL`: `scene_001`, `scene_003`, `scene_004`, `scene_006`, `scene_008`, `scene_010`, `scene_013`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_025`, `scene_027`, `scene_029`, `scene_030`, `scene_031`, and `scene_033`.
- Observation: The existing visual asset command already implements the desired local-file convention.
  Evidence: `synccut/visual_assets.py` targets only `AI_VIDEO` and `B_ROLL`, matches files by exact scene id under `assets_dir`, supports `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`, copies files into `<out_dir>/visuals/`, writes scene-level `visual.public_path`, `visual.asset_status`, and `visual.asset_source`, and writes deterministic root `assets.visuals` entries for prepared assets.
- Observation: Remotion already renders optional local visual assets without schema or dispatch changes.
  Evidence: `AiVideoScene.tsx` and `BRollScene.tsx` delegate to `VisualAssetScene.tsx`; that shared component validates `scene.visual.public_path`, renders images with `<Img src={staticFile(...)} />`, renders videos with muted `<OffthreadVideo src={staticFile(...)} />`, and falls back to `PlaceholderScene` when no valid local public path is present.
- Observation: Generated and local media directories are already ignored.
  Evidence: `.gitignore` includes `assets/visuals/`, `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`.
- Observation: Current release-hardening state has no source or schema changes pending.
  Evidence: `git status --short --ignored` showed only ignored local/generated paths before this plan was created.
- Observation: The target scene distribution is six `AI_VIDEO` scenes and eleven `B_ROLL` scenes.
  Evidence: The current props inventory contains `AI_VIDEO` scenes `scene_001`, `scene_008`, `scene_013`, `scene_025`, `scene_030`, and `scene_033`; it contains `B_ROLL` scenes `scene_003`, `scene_004`, `scene_006`, `scene_010`, `scene_015`, `scene_017`, `scene_020`, `scene_022`, `scene_027`, `scene_029`, and `scene_031`.
- Observation: The current prompts are descriptive enough to drive a production manifest without copying full prompt text.
  Evidence: Each target scene in `remotion/props.json` has a non-empty `visual.prompt` with visual direction, location or subject matter, and motion/style notes; the manifest summarizes these prompts instead of pasting them verbatim.
- Observation: Clean regenerated props report all 17 target visual scenes as missing before local visual preparation.
  Evidence: After `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets`, `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.
- Observation: The three-file synthetic subset prepared exactly three visual assets and left the remainder as placeholder warnings.
  Evidence: After creating `assets/visuals/scene_001.png`, `assets/visuals/scene_003.png`, and `assets/visuals/scene_004.png`, `prepare-visual-assets` reported `visual_copied: 1`, `visual_reused: 0`, `visual_overwritten: 2`, `visual_missing: 14`, and `visual_assets: 3`. `inspect-visual-assets` then reported `prepared: 3`, `missing: 14`, and `unsupported: 0`.
- Observation: The overwrite count came from existing ignored prepared visual files, not from a source bug.
  Evidence: The synthetic source PNGs were newly written under ignored `assets/visuals/`, while `prepare-visual-assets` copied into ignored `remotion/public/visuals/`; two destination files already existed from earlier local visual validation and were overwritten.
- Observation: Verified preflight accepts the synthetic partial pack as render-ready with warnings.
  Evidence: `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `visual_prepared: 3`, `visual_missing: 14`, `visual_unsupported: 0`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.
- Observation: The current root README already contains the required local visual asset instructions.
  Evidence: `README.md` documents `assets/visuals/<scene_id>.mp4`, `assets/visuals/<scene_id>.png`, the supported extension set, the `prepare-visual-assets` command, `inspect-visual-assets`, and the non-fatal placeholder fallback for missing `AI_VIDEO` and `B_ROLL` files.
- Observation: The current Remotion README is sufficient for Remotion-side public asset usage in this phase.
  Evidence: `remotion/README.md` explains regenerated props/audio, verified preflight, local render workflows, and generated artifact policy. The TSMC-specific asset pack details now live in `docs/tsmc-visual-asset-manifest.md`, so duplicating them in the Remotion README is unnecessary.
- Observation: Clean props were restored after synthetic validation.
  Evidence: After rerunning `build-timeline`, `validate-timeline`, `export-remotion`, and `prepare-remotion-assets`, `inspect-visual-assets remotion/props.json` reported `prepared: 0`, `missing: 17`, and `unsupported: 0`; inspecting `scene_001`, `scene_003`, and `scene_004` showed no `visual.public_path`, `asset_status`, or `asset_source`, and root `assets.visuals` was `[]`.
- Observation: The clean verified preflight state is warning-only and has no file errors.
  Evidence: `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `visual_prepared: 0`, `visual_missing: 17`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

## Decision Log

- Decision: Treat this phase as a documentation and workflow-validation phase, not a media-production phase.
  Rationale: The project already has local asset preparation, readiness reporting, and Remotion rendering support. The missing piece is a clear TSMC-specific inventory and validation path for real local media. Generating or sourcing media belongs to a later creative production step.
  Date/Author: 2026-05-12 / Codex
- Decision: Add a text-only manifest at `docs/tsmc-visual-asset-manifest.md`.
  Rationale: The manifest is safe to commit, useful for humans and future tools, and avoids committing binary media. It can list scene ids, visual types, intended filenames, prompts, and production notes without changing the props schema or command behavior.
  Date/Author: 2026-05-12 / Codex
- Decision: Use `assets/visuals/<scene_id>.<ext>` as the source pack convention and `remotion/public/visuals/<scene_id>.<ext>` as prepared output.
  Rationale: This matches the existing `prepare-visual-assets` command and Remotion's `staticFile("visuals/...")` public path convention. Keeping the same convention avoids any Python or Remotion source changes.
  Date/Author: 2026-05-12 / Codex
- Decision: Allow only tiny synthetic local files for workflow validation.
  Rationale: Synthetic files prove that counts, props annotation, verified preflight, and Remotion typecheck still work without requiring real media production, network access, asset downloads, or committed binaries.
  Date/Author: 2026-05-12 / Codex
- Decision: Recommend `.mp4` for every target scene in the initial manifest.
  Rationale: All 17 prompts imply motion or montage, and the existing command supports video files. The manifest still notes that `.png` still images are acceptable local fallbacks where useful.
  Date/Author: 2026-05-12 / Codex
- Decision: Use `.png` for the Milestone 2 synthetic subset even though the manifest recommends `.mp4`.
  Rationale: Tiny valid PNG files are easy to generate locally without media tooling, downloads, AI generation, ffmpeg, or rendering. The copy, readiness, public path, and preflight behavior is the same for supported image assets, so PNGs are sufficient for workflow validation.
  Date/Author: 2026-05-12 / Codex
- Decision: Do not update `README.md` or `remotion/README.md` in Milestone 3.
  Rationale: The root README already documents the visual asset naming convention, preparation command, readiness report, and placeholder fallback. The Remotion README already covers props/public assets and render validation sufficiently. The new TSMC-specific production details belong in `docs/tsmc-visual-asset-manifest.md`.
  Date/Author: 2026-05-12 / Codex
- Decision: Restore clean `remotion/props.json` after the synthetic partial-pack validation.
  Rationale: The synthetic `visual.public_path` values are validation-only and should not become accidental sample props. Clean props keep the repository state aligned with the manifest phase, where real assets are not committed or required.
  Date/Author: 2026-05-12 / Codex

## Outcomes & Retrospective

This plan has been created after reading the requested repository documentation and inspecting the current props, visual asset helper, preflight helper, visual asset tests, preflight tests, Remotion AI/B-roll components, Remotion package scripts, and ignore rules. No source code, schema, Remotion rendering code, package file, generated media, or command behavior has been changed.

The planned outcome is intentionally modest and production-friendly. Success does not require all 17 real assets to exist. Success means every TSMC target scene is inventoried, the expected source filenames are documented, the current local asset workflow is validated with a small ignored synthetic subset, the preflight/readiness reports reflect the prepared subset and missing remainder, and commit guidance clearly excludes binary media and generated props changes unless explicitly approved.

Milestone 1 is complete. `docs/tsmc-visual-asset-manifest.md` now exists as a text-only production manifest for the TSMC sample. It documents the artifact policy, naming convention, supported extensions, regenerate/prepare/inspect/preflight commands, and all 17 target `AI_VIDEO` and `B_ROLL` scenes in timeline order. Each row includes scene id, section key, visual type, recommended local filename, initial `needed` status, a short prompt summary, and production notes. No media files, Python source, Remotion source, schemas, command behavior, generated props, or render output were changed.

The Milestone 1 commit candidates are `docs/plans/tsmc-visual-asset-pack.md` and `docs/tsmc-visual-asset-manifest.md`. Generated visual assets remain intentionally absent; `assets/visuals/` should not be used until Milestone 2 synthetic validation or later real asset production.

Milestone 2 is complete. The clean sample was regenerated from the repository root. `build-timeline` completed successfully, `validate-timeline` reported `OK timeline.json`, 33 scenes, 7 sections, duration `752.79`, and the known `07_CONCLUSION` gap warning. `export-remotion` wrote `remotion/props.json` with 33 scenes, 7 sections, 30 fps, 22584 frames, and 1 warning. `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`.

Before creating synthetic visual assets, `inspect-visual-assets remotion/props.json` reported the expected baseline: `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`.

Three tiny valid PNG files were created locally under ignored `assets/visuals/`: `scene_001.png`, `scene_003.png`, and `scene_004.png`. Each file was 88 bytes. They are synthetic validation placeholders only and should not be committed. Running `prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public` reported `visual_copied: 1`, `visual_reused: 0`, `visual_overwritten: 2`, `visual_missing: 14`, `visual_assets: 3`, and `public_dir: remotion/public`. The overwrite count was expected because ignored prepared visual files already existed under `remotion/public/visuals/` from earlier local validations.

After preparation, `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 3`, `missing: 14`, and `unsupported: 0`. The prepared rows were `scene_001 AI_VIDEO prepared visuals/scene_001.png`, `scene_003 B_ROLL prepared visuals/scene_003.png`, and `scene_004 B_ROLL prepared visuals/scene_004.png`.

Verified preflight passed with warning status. `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 3`, `visual_missing: 14`, `visual_unsupported: 0`, `warnings: 15`, `errors: 0`, `verify_files: true`, and `file_errors: 0`. The warnings were the known root props warning plus 14 missing optional visual asset warnings; `Errors:` printed `none`.

Remotion and Python validation passed. From `remotion/`, `npm run typecheck` completed successfully with `tsc --noEmit`. From the repository root, `.venv/bin/python -m pytest` collected 208 tests and all 208 passed.

Artifact review after Milestone 2 showed `M remotion/props.json`, untracked docs files, and ignored generated/local paths. `remotion/props.json` was modified by validation regeneration and synthetic visual preparation; do not commit it unless explicitly choosing to preserve this prepared synthetic sample. Ignored artifacts include `assets/`, `remotion/public/`, `remotion/out/`, `timeline.json`, `.pytest_cache/`, `.venv/`, `remotion/node_modules/`, and Python `__pycache__/` directories. The intended commit candidates remain `docs/plans/tsmc-visual-asset-pack.md` and `docs/tsmc-visual-asset-manifest.md`.

Milestone 3 is complete. The documentation review found no clear missing or contradictory visual asset instructions in `README.md` or `remotion/README.md`, so neither file was edited. The root README already explains `assets/visuals/<scene_id>.<ext>`, supported extensions, `prepare-visual-assets`, `inspect-visual-assets`, and placeholder fallback. The Remotion README remains focused on regenerated props/audio, preflight before renders, local render commands, and generated artifact policy; the detailed TSMC asset inventory now lives in `docs/tsmc-visual-asset-manifest.md`.

Clean validation state was restored after the Milestone 2 synthetic test. From the repository root, `build-timeline` completed successfully, `validate-timeline` reported `OK timeline.json` with the known `07_CONCLUSION` gap warning, `export-remotion` wrote clean props, and `prepare-remotion-assets` reported `audio_copied: 0`, `audio_reused: 7`, `audio_overwritten: 0`, `audio_assets: 7`, and `public_dir: remotion/public`. No `prepare-visual-assets` command was rerun after this cleanup.

The clean visual readiness report is back to the expected missing-only baseline. `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, and `unsupported: 0`. Direct inspection confirmed `scene_001`, `scene_003`, and `scene_004` no longer have `visual.public_path`, `asset_status`, or `asset_source`, and root `assets.visuals` is `[]`.

The clean verified preflight report is warning-only. `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, `audio_prepared: 7`, `audio_missing_public_path: 0`, `visual_target_scenes: 17`, `visual_prepared: 0`, `visual_missing: 17`, `visual_unsupported: 0`, `warnings: 18`, `errors: 0`, `verify_files: true`, and `file_errors: 0`.

Artifact status after cleanup is acceptable. `git status --short --ignored` shows only `docs/plans/tsmc-visual-asset-pack.md` and `docs/tsmc-visual-asset-manifest.md` as non-ignored commit candidates. `remotion/props.json` is no longer a commit candidate. Ignored local/generated artifacts include `assets/`, `remotion/public/`, `remotion/out/`, `timeline.json`, `.pytest_cache/`, `.venv/`, `remotion/node_modules/`, and Python `__pycache__/` directories.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut has a Python CLI under `synccut/` and a standalone Remotion project under `remotion/`.

The Python CLI builds and prepares data. The relevant commands are:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The Remotion project reads `remotion/props.json`. `AI_VIDEO` scenes use `remotion/src/components/AiVideoScene.tsx`, and `B_ROLL` scenes use `remotion/src/components/BRollScene.tsx`. Both wrappers delegate to `remotion/src/components/VisualAssetScene.tsx`, which renders a local image or video when `scene.visual.public_path` is valid and falls back to `PlaceholderScene` otherwise.

A real visual asset pack in this phase means a local set of already-created image or video files placed under `assets/visuals/` and named by scene id. The pack is local and deterministic. It is not generated by SyncCut, not downloaded, not scraped, not fetched, not probed, not transcoded, and not committed by default.

A public path means a string relative to `remotion/public/`, such as `visuals/scene_003.mp4`. Remotion uses `staticFile("visuals/scene_003.mp4")` to load that file. A source path means a local working file such as `assets/visuals/scene_003.mp4`. Source paths are copied into the Remotion public directory by `prepare-visual-assets`.

## Current Visual Asset Command Behavior

The existing command is:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

The command reads `remotion/props.json`, considers only scenes with `visual_type` equal to `AI_VIDEO` or `B_ROLL`, and looks for exactly one supported file under `assets/visuals/` whose stem matches the scene id. For example, `scene_003.mp4` matches `scene_003`; `scene_003-source.mp4` does not.

Supported extensions are case-insensitive:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.mp4`
- `.webm`
- `.mov`

If exactly one supported file exists for a target scene, the command copies it to `remotion/public/visuals/<scene_id><suffix>`, writes `visual.public_path` as `visuals/<scene_id><suffix>`, writes `visual.asset_status` as `prepared`, and writes `visual.asset_source` as `local`. It also adds a deterministic root `assets.visuals` entry.

If no supported file exists for a target scene, the command does not fail. It removes any previous `visual.public_path` for that target scene, writes `visual.asset_status` as `missing`, and writes `visual.asset_source` as `local`. Remotion then falls back to placeholders, and preflight reports a warning rather than an error.

If more than one supported file exists for the same scene id, the command fails with `SyncCutError`. For example, `assets/visuals/scene_003.png` and `assets/visuals/scene_003.mp4` together are ambiguous and must be resolved manually.

Unsupported files are ignored. For example, `assets/visuals/scene_003.txt` does not prepare anything.

## Current TSMC Target Scene Inventory

The current `remotion/props.json` contains these 17 target scenes. The manifest created in Milestone 1 should use this list as its starting point, preserve scene order, and document one intended source filename for each scene.

`scene_001`, `AI_VIDEO`, section `01_HOOK`. Prompt summary: extreme close-up of a silicon wafer rotating under blue cleanroom light with reflections of engineers in bunny suits. Intended filename: `assets/visuals/scene_001.mp4` for a video, or `assets/visuals/scene_001.png` for a still fallback.

`scene_003`, `B_ROLL`, section `01_HOOK`. Prompt summary: aerial shot of TSMC's Hsinchu Science Park campus at dusk, fabrication halls glowing, Taiwan coastline visible. Intended filename: `assets/visuals/scene_003.mp4` or still fallback `assets/visuals/scene_003.png`.

`scene_004`, `B_ROLL`, section `02_INTRO`. Prompt summary: news montage of NVIDIA, Apple, military satellite, self-driving car, linked by a white chip motif. Intended filename: `assets/visuals/scene_004.mp4` or still fallback `assets/visuals/scene_004.png`.

`scene_006`, `B_ROLL`, section `02_INTRO`. Prompt summary: grain of sand falling into a researcher's hand, cutting to a gleaming silicon wafer with a text-overlay concept. Intended filename: `assets/visuals/scene_006.mp4` or still fallback `assets/visuals/scene_006.png`.

`scene_008`, `AI_VIDEO`, section `03_MECHANISM_1`. Prompt summary: 1987 black-and-white stylized footage of a Taiwanese minister and Morris Chang-like engineer shaking hands over a contract, with empty industrial land behind them. Intended filename: `assets/visuals/scene_008.mp4` or still fallback `assets/visuals/scene_008.png`.

`scene_010`, `B_ROLL`, section `03_MECHANISM_1`. Prompt summary: whiteboard circuit diagrams and a marker line separating design from manufacturing, pulling back to a modern chip design office. Intended filename: `assets/visuals/scene_010.mp4` or still fallback `assets/visuals/scene_010.png`.

`scene_013`, `AI_VIDEO`, section `04_MECHANISM_2`. Prompt summary: abstract transistor shrinking from visible scale to nanometer scale, with a human hair cross-section comparison and node numbers counting down. Intended filename: `assets/visuals/scene_013.mp4` or still fallback `assets/visuals/scene_013.png`.

`scene_015`, `B_ROLL`, section `04_MECHANISM_2`. Prompt summary: semiconductor cleanroom interior with engineers in bunny suits working around car-sized machines in a pristine white environment. Intended filename: `assets/visuals/scene_015.mp4` or still fallback `assets/visuals/scene_015.png`.

`scene_017`, `B_ROLL`, section `04_MECHANISM_2`. Prompt summary: EUV process animation with 13.5nm light, vacuum chamber, mirrors, tin droplet plasma, and wafer projection. Intended filename: `assets/visuals/scene_017.mp4` or still fallback `assets/visuals/scene_017.png`.

`scene_020`, `B_ROLL`, section `05_MECHANISM_3`. Prompt summary: quick cuts of Jensen Huang, Tim Cook, and Lisa Su presentations, each freezing to grayscale with manufacturing attribution text. Intended filename: `assets/visuals/scene_020.mp4` or still fallback `assets/visuals/scene_020.png`.

`scene_022`, `B_ROLL`, section `05_MECHANISM_3`. Prompt summary: company logos such as Apple, NVIDIA, Qualcomm, AMD, Google, and Tesla converging on a central TSMC point. Intended filename: `assets/visuals/scene_022.mp4` or still fallback `assets/visuals/scene_022.png`.

`scene_025`, `AI_VIDEO`, section `06_MECHANISM_4`. Prompt summary: satellite view of Taiwan, Taiwan Strait, stylized warships on the Chinese side, and a glowing island. Intended filename: `assets/visuals/scene_025.mp4` or still fallback `assets/visuals/scene_025.png`.

`scene_027`, `B_ROLL`, section `06_MECHANISM_4`. Prompt summary: TSMC Arizona fab construction in Phoenix, desert floor, hard hats, American and Taiwanese flags. Intended filename: `assets/visuals/scene_027.mp4` or still fallback `assets/visuals/scene_027.png`.

`scene_029`, `B_ROLL`, section `06_MECHANISM_4`. Prompt summary: split screen of ASML headquarters and world map showing EUV machine restrictions with red lines to permitted countries. Intended filename: `assets/visuals/scene_029.mp4` or still fallback `assets/visuals/scene_029.png`.

`scene_030`, `AI_VIDEO`, section `07_CONCLUSION`. Prompt summary: slow aerial shot over the Taiwan Strait at sunrise, calm water, golden light, Taiwan visible at the edge. Intended filename: `assets/visuals/scene_030.mp4` or still fallback `assets/visuals/scene_030.png`.

`scene_031`, `B_ROLL`, section `07_CONCLUSION`. Prompt summary: Morris Chang-like elderly speaker at a podium, audience of engineers and executives, slide about innovation, integrity, and customer trust. Intended filename: `assets/visuals/scene_031.mp4` or still fallback `assets/visuals/scene_031.png`.

`scene_033`, `AI_VIDEO`, section `07_CONCLUSION`. Prompt summary: final shot of a single silicon wafer in an otherwise empty cleanroom, reflecting overhead lights, fading to black. Intended filename: `assets/visuals/scene_033.mp4` or still fallback `assets/visuals/scene_033.png`.

## Manifest Document Design

Milestone 1 should create `docs/tsmc-visual-asset-manifest.md`. This is a text-only production manifest, not a media directory. It should be safe to commit.

The manifest should explain that the binary media files belong under `assets/visuals/` and should not be committed by default. It should list all 17 target scenes in timeline order and include:

- scene id
- visual type
- section key
- intended filename, preferably `.mp4` when motion is useful and `.png` as acceptable still fallback
- current status, initially `missing`
- prompt summary or source note
- optional production note, such as whether the asset should be staged footage, a diagram-like motion graphic, licensed stock, archival-style reenactment, or generated externally outside this repository

The manifest should not embed base64 media, screenshots, or downloaded source URLs. If a human later uses licensed footage, owned footage, or externally generated media, source/license notes can be added as text, but the binary asset should remain local unless a separate explicit commit policy is approved.

## Artifact Policy

Do not commit:

- `assets/visuals/*`
- `remotion/public/visuals/*`
- `remotion/public/audio/*`
- `remotion/out/*`
- `timeline.json`
- `.venv/`
- `remotion/node_modules/`
- `.pytest_cache/`
- Python `__pycache__/`

Usually do not commit `remotion/props.json` after validation because `prepare-visual-assets` may add temporary local `visual.public_path`, `visual.asset_status`, `visual.asset_source`, and root `assets.visuals` entries. Commit `remotion/props.json` only when explicitly choosing to refresh checked-in sample props.

Expected commit candidates for this phase are normally:

- `docs/plans/tsmc-visual-asset-pack.md`
- `docs/tsmc-visual-asset-manifest.md`
- optionally `README.md` or `remotion/README.md` only if Milestone 3 finds current visual asset pack instructions are insufficient

## Plan of Work

Milestone 1 is a read-only inventory and manifest milestone. Use the current `remotion/props.json` to confirm the target scene list and create `docs/tsmc-visual-asset-manifest.md`. The manifest should be text-only, list the 17 target scenes, and specify the intended local source filenames. After creating it, run no media generation and no renders. Validate with:

    git diff -- docs/tsmc-visual-asset-manifest.md docs/plans/tsmc-visual-asset-pack.md

Milestone 2 validates the existing workflow with a tiny partial synthetic pack. Create two or three tiny local test image files under `assets/visuals/`, for example `scene_001.png`, `scene_003.png`, and `scene_025.png`. These files should be simple locally generated PNGs or other tiny files sufficient for the current copy and preflight commands; they must not be downloaded or externally fetched. Regenerate props and audio, run `prepare-visual-assets`, inspect visual readiness, run verified preflight, and run Remotion typecheck. The expected result is that prepared count increases by the number of synthetic assets, missing count decreases from 17 accordingly, verified preflight remains warning-only with `file_errors: 0`, and no binary asset is a commit candidate because `assets/visuals/` and `remotion/public/` are ignored.

Milestone 3 is a documentation check. Read `README.md` and `remotion/README.md` and decide whether the existing local visual asset instructions are enough. If they are enough, update only this plan to record that no README change is needed. If they are missing important asset-pack instructions, make a concise docs-only update that points to `docs/tsmc-visual-asset-manifest.md` and repeats the prepare/inspect/preflight commands without duplicating the whole manifest.

Milestone 4 is final review. Regenerate clean props and prepared audio so `remotion/props.json` is not left with temporary synthetic visual public paths unless the user explicitly wants that sample change. Run Python tests and Remotion typecheck. Run visual readiness and verified preflight on clean props and record whether the sample is all missing again or has an intentional prepared subset. Run `git status --short --ignored` and confirm no binary visual media or generated render output is a commit candidate.

## Concrete Validation Workflow

The full validation workflow for a clean sample starts from the repository root:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json

Before adding any local visual assets, the expected TSMC sample readiness is:

    target_scenes: 17
    prepared: 0
    missing: 17
    unsupported: 0

After creating a tiny local partial pack under `assets/visuals/`, run:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

For a two-asset synthetic pack, expected readiness is:

    target_scenes: 17
    prepared: 2
    missing: 15
    unsupported: 0

Verified preflight should remain `status: warning` because the remaining missing `AI_VIDEO` and `B_ROLL` visuals are optional placeholder warnings. It should report `file_errors: 0` when prepared synthetic files exist under `remotion/public/visuals/`.

Run Python and Remotion validation:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck
    cd ..

Optional render validation may be run only if browser launch permission and time permit:

    cd remotion
    npm run still:local
    npm run render:smoke:local
    npm run render:segment:local
    cd ..

Do not run a final render for this phase unless explicitly requested. Do not call ffmpeg directly.

## Validation and Acceptance

This phase is accepted when:

- `docs/tsmc-visual-asset-manifest.md` exists and lists all 17 target scenes with intended filenames and production notes.
- No Python command behavior has changed.
- No timeline or Remotion schema has changed.
- No Remotion rendering source has changed unless a clear docs/validation bug is discovered and explicitly recorded.
- The existing visual asset workflow is validated with a small ignored synthetic subset or, if synthetic validation is skipped, the exact reason is recorded.
- `inspect-visual-assets` reports the expected prepared/missing/unsupported counts before and after any synthetic partial pack.
- `preflight --verify-files --public-dir remotion/public` reports `file_errors: 0` for prepared assets that exist.
- `.venv/bin/python -m pytest` passes.
- `cd remotion && npm run typecheck` passes.
- `git status --short --ignored` shows no binary media assets, generated public assets, render outputs, or temporary props changes as commit candidates.

## Idempotence and Recovery

The workflow is safe to repeat. Regenerating `timeline.json`, `remotion/props.json`, and prepared audio resets the baseline. Running `prepare-visual-assets` again is idempotent: unchanged destination files are reused, changed files are overwritten, missing files remain warnings, and duplicate supported source files for one scene id fail clearly.

If a synthetic validation leaves temporary visual public paths in `remotion/props.json`, restore clean sample props by running:

    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public

If duplicate source files exist for a scene, remove or rename all but one supported file. For example, do not keep both `assets/visuals/scene_003.png` and `assets/visuals/scene_003.mp4` when running `prepare-visual-assets`.

Do not use `git clean`, `git checkout`, or destructive cleanup commands unless explicitly requested. Generated assets are ignored and can remain local.

## Explicit Exclusions

This phase must not:

- generate AI video or images
- call image or video generation APIs
- download B-roll
- scrape or fetch external media
- call ffmpeg or ffprobe directly
- probe, decode, transcode, normalize, or trim media
- add Python commands that invoke Remotion rendering
- change `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, or `preflight` behavior unless a clear docs/validation bug is found
- change timeline or Remotion schemas
- add GUI or web app behavior
- commit `assets/visuals/*`, `remotion/public/*`, `remotion/out/*`, or temporary generated props changes by default

## Artifacts and Notes

The target scene inventory was derived from the current `remotion/props.json` with a local Python JSON inspection. The inspection reported 17 target scenes and preserved timeline order. The prompt summaries in this plan are shortened from existing props prompts so the plan remains readable.

The Remotion best-practice constraints relevant here are already satisfied by the current implementation: assets live under `remotion/public/`, Remotion references them with `staticFile()`, images render with `<Img>`, videos render with `OffthreadVideo`, and no CSS animations are required for this asset-pack phase.

## Interfaces and Dependencies

This phase should not add dependencies. It uses the existing Python CLI and Remotion package.

The existing Python interface is:

    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public

The existing report interface is:

    .venv/bin/synccut inspect-visual-assets remotion/props.json

The existing verified preflight interface is:

    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

The manifest interface to create in Milestone 1 is:

    docs/tsmc-visual-asset-manifest.md

That manifest should remain text-only and should not introduce a machine-readable schema. A future phase can add a structured manifest if the workflow needs automation beyond the existing scene-id file convention.
