# Visual duration and readiness handling

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, and validate visual duration/readiness reporting from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut can already find optional local `AI_VIDEO` and `B_ROLL` assets, copy them into Remotion public assets, and render them. It can also create a visual manifest and download missing B-roll. What it cannot yet do is inspect local media metadata and explain whether each local asset is suitable for its scene duration before a render.

After this phase, a user should be able to run:

    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.md
    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.json --format json

and answer which video assets are shorter than their scene and will loop, which videos are much shorter and likely repetitive, which videos are longer and will be trimmed by the scene duration, which images are duration-independent, which files have aspect-ratio concerns, and which target scenes are missing, duplicate, unsupported, or unreadable. This is a reporting/readiness workflow only. It must not transcode, trim, crop, normalize, download, generate, copy, prepare, render, or modify media.

The user explicitly approved `ffprobe` for Phase 33. `ffprobe` is a metadata-inspection command from FFmpeg tooling. In this plan it is allowed only to read local metadata such as duration, width, height, and codec from local video files. The companion `ffmpeg` transformation command is not allowed.

## Progress

- [x] (2026-05-17T00:00:00+07:00) Read `.agent/PLANS.md`, README, Phase 31 and Phase 32 plans, visual asset/readiness helpers, preflight helper, Remotion visual component, and current git status.
- [x] (2026-05-17T00:00:00+07:00) Created this Phase 33 ExecPlan.
- [x] (2026-05-17T00:20:00+07:00) Milestone 1: current visual duration/readiness audit.
- [x] (2026-05-17T00:40:00+07:00) Milestone 2: duration/readiness design.
- [x] (2026-05-17T01:10:00+07:00) Milestone 3: implement visual duration readiness command.
- [x] (2026-05-17T01:30:00+07:00) Milestone 4: local validation.
- [x] (2026-05-17T01:50:00+07:00) Milestone 5: docs, cleanup, final review.

## Surprises & Discoveries

- Observation: Remotion already loops prepared video assets.
  Evidence: `remotion/src/components/VisualAssetScene.tsx` renders prepared videos with `<Video src={staticFile(asset.publicPath)} muted loop style={styles.media} />`.
- Observation: Images are currently rendered as static media that naturally cover the whole scene duration.
  Evidence: `VisualAssetScene.tsx` renders images with `<Img src={staticFile(asset.publicPath)} style={styles.media} />`, and the scene duration is controlled by the parent Remotion sequence.
- Observation: Existing visual readiness checks do not inspect media metadata.
  Evidence: `synccut/visual_assets.py` classifies prepared props readiness from `visual.public_path` and local source availability by file stem/suffix. It does not read duration, resolution, aspect ratio, codec, or file readability.
- Observation: Existing preflight catches missing/unsupported prepared paths, but not short or repetitive videos.
  Evidence: `synccut/preflight.py` reports `visual_missing` and `visual_unsupported` based on props readiness, and treats missing optional visuals as warning-only when no blocking errors exist.
- Observation: Phase 31 already provides most of the local source-file discovery policy needed for Phase 33.
  Evidence: `synccut/visual_manifest.py` reports target `AI_VIDEO`/`B_ROLL` scenes, scene duration fields, expected local filenames, prepared status, and local statuses `found`, `missing`, `duplicate_supported`, and `unsupported_only`.
- Observation: The local asset suffix set is centralized.
  Evidence: `synccut/visual_assets.py` defines `SUPPORTED_VISUAL_EXTENSIONS = {".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp"}`.
- Observation: Current git status is clean for non-ignored files after Phase 32.
  Evidence: `git status --short --ignored` showed only ignored local/generated paths such as `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `__pycache__/`, and `timeline.json`.
- Observation: Remotion bounds all visual playback by the scene sequence outside `VisualAssetScene`.
  Evidence: `VisualAssetScene.tsx` renders the media layer only for the active scene component. It does not set duration itself; scene timing comes from Remotion props and parent sequencing. A long video is therefore visible only for the scene's duration.
- Observation: Existing commands cannot report duration, loops, trim behavior, resolution, aspect ratio, codec, or unreadable media metadata.
  Evidence: `inspect-visual-assets` reports prepared/missing/unsupported props readiness. `visual-manifest` reports local availability by stem/suffix and scene durations. `preflight` reports missing/unsupported prepared visual paths. None of those modules call ffprobe or record duration/resolution/aspect/codec fields.
- Observation: Props contain the duration fields needed for comparison.
  Evidence: `remotion/props.json` scene entries include `id`, `section_key`, `section`, `visual_type`, `duration_sec`, `duration_frames`, and the `visual` object. Sample `scene_001` has `duration_sec: 9.137` and `duration_frames: 274`.
- Observation: Local asset discovery policy is already precise enough to reuse.
  Evidence: `TARGET_VISUAL_TYPES` is `{"AI_VIDEO", "B_ROLL"}`. `SUPPORTED_VISUAL_EXTENSIONS` is `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`. Phase 31 local inspection matches only direct child files whose stem equals the scene id and reports found, missing, duplicate-supported, and unsupported-only cases.
- Observation: `ffprobe` is not available in the current local environment.
  Evidence: `command -v ffprobe` exited 1 with no path. `ffprobe -version` exited 127 with `zsh:1: command not found: ffprobe`.
- Observation: No sample media probing was performed.
  Evidence: Because `ffprobe` is not available, no `assets/visuals/*` file was probed in Milestone 1.
- Observation: Tests must not depend on local ffprobe.
  Evidence: The current development environment lacks ffprobe, so Milestone 3 tests need mocked subprocess/probe behavior and explicit coverage for missing executable errors.
- Observation: Missing ffprobe should fail clearly at runtime, while unreadable individual videos should become scene-level readiness results.
  Evidence: Missing executable means no video metadata can be inspected at all. Individual corrupt or invalid files are expected data quality issues and should be reported per scene so one bad asset does not hide the rest of the report.
- Observation: The local missing-ffprobe environment changes the implementation strategy but not the feature contract.
  Evidence: Milestone 2 keeps ffprobe support in the runtime design, but requires mocked probe tests and lazy failure only when a supported video actually needs probing.
- Observation: A single primary status plus a warnings list is the clearest report shape.
  Evidence: Duration readiness and aspect ratio are independent concerns. A video can be short, long, or OK while also having an aspect-ratio warning.
- Observation: Milestone 3 added one focused source module and thin CLI wiring.
  Evidence: `synccut/visual_duration.py` contains report/probe/format/write logic, `synccut/cli.py` wires `inspect-visual-duration`, and tests were added in `tests/test_visual_duration.py` plus focused CLI coverage in `tests/test_cli.py`.
- Observation: The ffprobe wrapper follows the lazy-failure design.
  Evidence: Images, missing assets, unsupported-only assets, and duplicate supported assets do not invoke the probe runner. Supported video files invoke ffprobe metadata inspection; missing executable raises `SyncCutError` naming ffprobe and `--ffprobe-bin`, while nonzero/timeout/invalid metadata is reported as scene-level `unreadable`.
- Observation: Tests remain independent of local ffprobe and real media metadata.
  Evidence: Video readiness tests inject fake probe runners and use tiny dummy files. CLI success tests use image assets to avoid probing. Missing-ffprobe behavior is tested with a deliberately missing executable.
- Observation: One test adjustment was needed to avoid accidental default local asset discovery.
  Evidence: Initial write-policy tests used the default `assets/visuals` path and saw local ignored media in the repository. The tests now pass temp-scoped `assets_dir` paths so they remain isolated.
- Observation: Full pytest passed after implementation.
  Evidence: `.venv/bin/python -m pytest` completed with `311 passed`.
- Observation: Milestone 4 pytest passed.
  Evidence: `.venv/bin/python -m pytest` completed with `311 passed`.
- Observation: `ffprobe` is still unavailable in the local environment.
  Evidence: `command -v ffprobe || true` produced no path. `ffprobe -version || true` printed `zsh:1: command not found: ffprobe`.
- Observation: Sample timeline and props regeneration succeeded for validation.
  Evidence: `build-timeline` reported `sections: 7`, `scenes: 33`, `duration_sec: 752.79`, and `warnings: 0`. `export-remotion` reported `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 0`.
- Observation: Real local duration report generation is blocked by missing ffprobe because current local `assets/visuals` contains supported video assets that require probing.
  Evidence: Both Markdown and JSON `inspect-visual-duration` attempts exited 1 with `Error: ffprobe: ffprobe executable not found; install FFmpeg tools or pass --ffprobe-bin`.
- Observation: The missing-ffprobe failure is clear and consistent with the Milestone 2 design.
  Evidence: The error names `ffprobe` and `--ffprobe-bin`, and tests already cover mocked video probing plus missing executable behavior.
- Observation: Remotion typecheck passed after validation.
  Evidence: `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`.
- Observation: Validation cleanup removed report outputs and restored regenerated props.
  Evidence: `rm -f generated/visual_duration_report.md generated/visual_duration_report.json` ran, `rmdir generated 2>/dev/null || true` ran, `git restore remotion/props.json` succeeded after escalation was required for `.git/index.lock`, and `git status --short assets/visuals remotion/props.json generated` produced no output.
- Observation: No media modification, download, rendering, or transformation occurred.
  Evidence: Validation only ran pytest, ffprobe availability checks, build/export, two read-only report attempts that failed before writing reports, Remotion typecheck, targeted cleanup, and props restore.
- Observation: README received a concise user-facing note for the new command.
  Evidence: The README command summary now lists `inspect-visual-duration`, and the Local Visual Assets section explains that it reports local visual duration/resolution readiness, uses ffprobe only for video metadata inspection, does not mutate media/props or render, and writes reports under ignored `generated/`.
- Observation: `.gitignore` did not need changes.
  Evidence: `.gitignore` already contains `generated/` and `assets/visuals/`, covering report outputs and local visual media.
- Observation: Final pytest passed.
  Evidence: `.venv/bin/python -m pytest` completed with `311 passed`.
- Observation: Final Remotion typecheck passed.
  Evidence: `cd remotion && npm run typecheck` completed successfully with `tsc --noEmit`.
- Observation: Final artifact status is clean for generated reports and props.
  Evidence: `generated/visual_duration_report.md` and `generated/visual_duration_report.json` are absent, `remotion/props.json` is not modified, and no downloaded/transformed media or render artifacts are commit candidates.
- Observation: Final commit candidates are source, tests, README, and the Phase 33 plan.
  Evidence: `git status --short --ignored` shows `README.md`, `synccut/cli.py`, `tests/test_cli.py`, untracked `synccut/visual_duration.py`, untracked `tests/test_visual_duration.py`, and untracked `docs/plans/visual-duration-readiness-handling.md`; ignored local paths remain ignored.

## Decision Log

- Decision: Use a new read-only command named `inspect-visual-duration`.
  Rationale: The command reports duration and readiness metadata; it does not prepare assets, download assets, or run a render. The name makes it distinct from `inspect-visual-assets`, `visual-manifest`, and `preflight`.
  Date/Author: 2026-05-17 / Codex
- Decision: Use `remotion/props.json` as the primary input.
  Rationale: Remotion props contain target scene ids, visual types, scene durations in seconds and frames, section metadata, and visual metadata. Those fields are required to compare local asset duration to scene duration.
  Date/Author: 2026-05-17 / Codex
- Decision: Allow `ffprobe` only for local video metadata inspection.
  Rationale: The user explicitly approved ffprobe for this phase. It is necessary to read video duration/resolution reliably, but Phase 33 must not transform media.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not use `ffmpeg`.
  Rationale: `ffmpeg` is used for media transformation and is out of scope. Phase 33 is reporting/readiness only.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not mutate `remotion/props.json`.
  Rationale: The report can be generated from props plus local assets without changing render inputs. Any future policy that annotates props must be separately approved.
  Date/Author: 2026-05-17 / Codex
- Decision: Support Markdown and JSON report outputs.
  Rationale: Markdown is useful for human review and replacement decisions; JSON is useful for later automated readiness or provider workflows.
  Date/Author: 2026-05-17 / Codex
- Decision: Treat image assets as duration-independent.
  Rationale: Static images can cover the whole scene duration in Remotion without looping or trimming. Resolution/aspect inspection for images can be deferred unless an existing dependency makes it cheap and testable.
  Date/Author: 2026-05-17 / Codex
- Decision: Keep `inspect-visual-duration` read-only after Milestone 1 audit.
  Rationale: The audit confirmed the needed comparison data can be read from props plus local source filenames and ffprobe metadata. There is no need to mutate props, copy assets, prepare assets, or write media.
  Date/Author: 2026-05-17 / Codex
- Decision: Call ffprobe only for supported video suffixes.
  Rationale: Images are duration-independent, unsupported suffixes should be reported as unsupported, and probing unsupported files would add noise and risk.
  Date/Author: 2026-05-17 / Codex
- Decision: Treat images as `image_ok` without duration probing.
  Rationale: Existing Remotion behavior displays images for the scene duration, and no image metadata dependency is currently established.
  Date/Author: 2026-05-17 / Codex
- Decision: Unreadable video metadata should be a scene-level result.
  Rationale: A single bad local file should not prevent the user from seeing readiness for all other scenes.
  Date/Author: 2026-05-17 / Codex
- Decision: Missing ffprobe executable should raise a clear `SyncCutError`.
  Rationale: If the metadata tool itself is unavailable, video duration/readiness cannot be meaningfully inspected. The error should name ffprobe and point toward installing FFmpeg tools or configuring the executable path.
  Date/Author: 2026-05-17 / Codex
- Decision: Continue to prohibit props mutation, media transformation, ffmpeg, and rendering.
  Rationale: The audit did not uncover any need for mutation or transformation to produce the report. Phase 33 remains reporting/readiness only.
  Date/Author: 2026-05-17 / Codex
- Decision: Final CLI shape is `synccut inspect-visual-duration PROPS_JSON --assets-dir assets/visuals --format markdown|json --out ...`.
  Rationale: `PROPS_JSON` supplies scene durations and visual metadata, `assets/visuals` is the existing local media convention, Markdown serves human review, and JSON supports later automated readiness workflows. Defaults are `generated/visual_duration_report.md` for Markdown and `generated/visual_duration_report.json` for JSON. Options are `--overwrite`, `--ffprobe-bin ffprobe`, `--ffprobe-timeout 15`, `--max-loops-before-warning 3`, `--min-duration-ratio 0.4`, `--aspect-min 1.55`, and `--aspect-max 1.90`. There is no `--dry-run` because the command is read-only except report output.
  Date/Author: 2026-05-17 / Codex
- Decision: Use lazy ffprobe failure.
  Rationale: The local environment currently lacks ffprobe. Missing ffprobe should not prevent image-only, missing, unsupported, or duplicate reporting. The command raises a clear `SyncCutError` naming `ffprobe` and `--ffprobe-bin` only when a supported video file must be probed and the executable is unavailable.
  Date/Author: 2026-05-17 / Codex
- Decision: Target discovery is direct-child, same-stem local source inspection for `AI_VIDEO` and `B_ROLL` scenes only.
  Rationale: This matches the existing visual manifest and visual preparation policy. Supported video suffixes are `.mp4`, `.webm`, and `.mov`; supported image suffixes are `.png`, `.jpg`, `.jpeg`, and `.webp`. The command does not recurse, create `assets_dir`, read unsupported files, or probe anything except a single supported video candidate.
  Date/Author: 2026-05-17 / Codex
- Decision: Use one primary readiness status plus a warnings list.
  Rationale: Primary statuses are `missing`, `unsupported`, `duplicate_supported`, `unreadable`, `image_ok`, `video_ok`, `video_short_loops`, `video_very_short_repetitive`, and `video_long_trimmed`. Warning codes are `loops`, `repetitive_loop`, `trimmed`, `aspect_ratio_warning`, and `unreadable_metadata`, allowing aspect warnings to coexist with duration status.
  Date/Author: 2026-05-17 / Codex
- Decision: Duration thresholds are configurable with a fixed equality tolerance.
  Rationale: Use a fixed `0.25` second tolerance for near-equal video duration. Short video assets loop; assets with loops greater than `--max-loops-before-warning` or duration ratio below `--min-duration-ratio` are `video_very_short_repetitive`. Long videos are `video_long_trimmed`. Aspect ratio warnings are added when width/height falls outside `[--aspect-min, --aspect-max]`.
  Date/Author: 2026-05-17 / Codex
- Decision: JSON and Markdown reports have deterministic contracts.
  Rationale: JSON uses schema version `0.1`, metadata, summary counts, supported thresholds, and scene rows with duration/probe/readiness fields. Markdown includes title, source/assets summary, threshold summary, counts, and a scene table. JSON formatting is `indent=2`, `ensure_ascii=False`, with a trailing newline.
  Date/Author: 2026-05-17 / Codex
- Decision: Report output uses no-overwrite idempotence.
  Rationale: If the report path is missing, write it. If existing content is identical, reuse it. If content differs, fail with a `SyncCutError` mentioning `--overwrite`. With `--overwrite`, replace only the requested report file and never mutate media or props.
  Date/Author: 2026-05-17 / Codex
- Decision: Milestone 3 implementation files are `synccut/visual_duration.py`, `synccut/cli.py`, `tests/test_visual_duration.py`, `tests/test_cli.py`, and this ExecPlan.
  Rationale: A new module keeps probe/report logic testable, CLI stays thin, and tests can mock ffprobe/subprocess without depending on local ffprobe or real media.
  Date/Author: 2026-05-17 / Codex
- Decision: Update README with a concise `inspect-visual-duration` note.
  Rationale: The command is ready for user-facing local use, but the README should not duplicate the full report schema. The note covers purpose, ffprobe dependency, non-mutating behavior, and ignored report output.
  Date/Author: 2026-05-17 / Codex
- Decision: Do not update `.gitignore`.
  Rationale: Existing `generated/` and `assets/visuals/` entries already cover duration reports and local media. No new unignored local output path was introduced.
  Date/Author: 2026-05-17 / Codex
- Decision: Document local ffprobe availability as a runtime requirement for video reports.
  Rationale: Local validation confirmed the command and tests are ready, but real video report generation on this machine is blocked until ffprobe is installed or `--ffprobe-bin` points to an available executable.
  Date/Author: 2026-05-17 / Codex

## Outcomes & Retrospective

This plan has been created but not implemented. No source code, tests, README, `.gitignore`, generated reports, media files, props files, Remotion files, downloads, ffprobe scans, ffmpeg work, media transformations, renders, commits, tags, or pushes were performed while authoring the plan.

The intended outcome is a safe local readiness report. At completion, users can inspect local visual assets before render and decide which files need replacement or review because of duration, looping, trimming, aspect ratio, missing/duplicate files, unsupported suffixes, or unreadable metadata.

Milestone 1 audit is complete. Remotion already loops video assets with `<Video muted loop>` and renders images statically with `<Img>`, while scene duration is controlled by parent Remotion sequencing from props. Existing `inspect-visual-assets`, `visual-manifest`, and `preflight` commands report prepared status and local source-file availability, but none report asset duration, loop counts, trim behavior, resolution, aspect ratio, codec, or unreadable metadata. Props provide the needed scene duration fields. Local asset discovery should reuse the existing target type and suffix policy. `ffprobe` is not installed in this environment, so no sample media was probed; Milestone 3 tests must mock probing and cover missing-ffprobe behavior. Next step: Milestone 2 duration/readiness design.

Milestone 2 design is complete. The implementation contract is a read-only `inspect-visual-duration` command that reads props, inspects local source files by direct child stem, probes only supported video files with ffprobe, treats images as duration-independent, and writes deterministic Markdown or JSON reports. The design deliberately supports environments without ffprobe by using mocked tests and lazy runtime failure only when a video probe is required. Report output uses no-overwrite idempotence and does not mutate media or `remotion/props.json`. Next step: Milestone 3 implement the command with mocked tests.

Milestone 3 implementation is complete. The new `inspect-visual-duration` command builds deterministic Markdown/JSON reports from Remotion props and local `assets/visuals` source files, uses ffprobe only for supported video metadata, keeps images duration-independent, records missing/unsupported/duplicate/unreadable/image/video readiness statuses, adds loop/trim/repetitive/aspect warnings, and applies no-overwrite report idempotence. Tests cover target filtering, scene order, file discovery statuses, image no-probe behavior, video duration outcomes, aspect warnings, unreadable metadata including zero duration, lazy missing-ffprobe errors, JSON/Markdown formatting, write conflicts/overwrite, and CLI success/error paths. Verification: `.venv/bin/python -m pytest` passed with `311 passed`. Next step: Milestone 4 local validation.

Milestone 4 local validation is complete. Unit coverage passed with `311 passed`, sample `build-timeline` and `export-remotion` succeeded, and Remotion typecheck passed. The real report command could not produce Markdown or JSON reports locally because ffprobe is still missing and current local video assets require probing; both attempts failed clearly with `Error: ffprobe: ffprobe executable not found; install FFmpeg tools or pass --ffprobe-bin`. This is an environment limitation rather than an implementation failure because the mocked tests cover ffprobe behavior and the runtime error is explicit. Generated report paths were cleaned, `remotion/props.json` was restored after temporary validation regeneration, and no media/download/render artifacts were produced. Next step: Milestone 5 docs/cleanup/final review.

Phase 33 is complete. `inspect-visual-duration` now reports local visual readiness from Remotion props and `assets/visuals` without mutating props, preparing assets, transforming media, or rendering. It distinguishes missing, unsupported, duplicate, unreadable, image, short-looping video, very-short/repetitive video, long-trimmed video, and aspect-ratio warning cases. Markdown and JSON reports are deterministic and use no-overwrite idempotence. Tests mock probe behavior and do not require local ffprobe or real media metadata. Final validation passed with `311 passed` and Remotion typecheck passing. Real video report generation is ready, but local end-to-end report generation was blocked by the missing `ffprobe` executable; the runtime error is clear and README now documents the requirement. Final commit candidates are `README.md`, `synccut/visual_duration.py`, `synccut/cli.py`, `tests/test_visual_duration.py`, `tests/test_cli.py`, and `docs/plans/visual-duration-readiness-handling.md`. Recommended commit message: `Add visual duration readiness reporting`. Next step: ask the user before Phase 34 Remotion visual quality polish.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python Typer CLI in `synccut/`. The Remotion renderer lives in `remotion/`.

The current visual pipeline has these relevant commands:

    .venv/bin/synccut visual-manifest remotion/props.json --assets-dir assets/visuals --out generated/visual_manifest.json --format json
    .venv/bin/synccut download-broll generated/visual_manifest.json --provider pexels --assets-dir assets/visuals --limit 1 --dry-run
    .venv/bin/synccut prepare-visual-assets remotion/props.json --assets-dir assets/visuals --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

`visual-manifest` is read-only and reports local source-file availability. `download-broll` can create missing local source media when run for real. `prepare-visual-assets` copies local source files into `remotion/public/visuals/` and mutates `remotion/props.json`. `inspect-visual-assets` and `preflight` inspect props readiness, but they do not measure local video duration or resolution.

Phase 33 adds a new read-only layer before render and before Phase 34 visual quality polish. It should inspect local source files under `assets/visuals/` and compare them against the scene durations in `remotion/props.json`.

Important files:

    synccut/visual_manifest.py
    synccut/visual_assets.py
    synccut/preflight.py
    synccut/cli.py
    tests/test_visual_manifest.py
    tests/test_visual_assets.py
    tests/test_preflight.py
    tests/test_cli.py
    remotion/src/components/VisualAssetScene.tsx
    .gitignore

Likely new implementation files:

    synccut/visual_duration.py
    tests/test_visual_duration.py

Generated validation reports should live under ignored `generated/`:

    generated/visual_duration_report.md
    generated/visual_duration_report.json

## Plan of Work

### Milestone 1: current visual duration/readiness audit

Audit without editing source. Read the Remotion visual component to confirm that videos loop and images remain static for the scene duration. Read the visual asset and preflight helpers to confirm what the existing commands can and cannot catch. Read current props and manifest-related code enough to confirm scene duration fields such as `duration_sec` and `duration_frames`.

Check local `ffprobe` availability:

    command -v ffprobe
    ffprobe -version

This milestone should not scan every asset. If a small sample is useful, sample one or two named files only and record exactly which files were probed and why. Do not modify media, props, source, tests, README, or `.gitignore`.

Acceptance for Milestone 1: the plan records current Remotion behavior, current readiness gaps, available scene duration fields, supported extensions, `ffprobe` availability/version, and any sampled metadata evidence.

### Milestone 2: duration/readiness design

Finalize the command and report contract before coding. The final command shapes are:

    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.md
    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.json --format json

The command options are:

- positional input: `PROPS_JSON`, normally `remotion/props.json`
- `--assets-dir`, default `assets/visuals`
- `--out`, default `generated/visual_duration_report.md` for Markdown and `generated/visual_duration_report.json` for JSON
- `--format markdown|json`, default `markdown`
- `--overwrite`, because report output should block when the requested report exists and differs
- `--ffprobe-bin`, default `ffprobe`
- `--ffprobe-timeout`, default `15`
- `--max-loops-before-warning`, default `3`
- `--min-duration-ratio`, default `0.4`
- `--aspect-min`, default `1.55`
- `--aspect-max`, default `1.90`

No `--dry-run` is required because the command is read-only except for the report output. If `--out` is omitted, the command writes the format-specific default report path.

Target scene and asset discovery:

- include only `AI_VIDEO` and `B_ROLL` scenes
- preserve props scene order
- inspect direct child files under `assets_dir`
- candidates have `Path.stem == scene_id`
- supported suffixes come from `SUPPORTED_VISUAL_EXTENSIONS`
- video suffixes are `.mp4`, `.webm`, and `.mov`
- image suffixes are `.png`, `.jpg`, `.jpeg`, and `.webp`
- do not recurse
- do not create `assets_dir`
- do not read or probe unsupported files
- before probing, report `missing`, `unsupported`, `duplicate_supported`, `image_ok`, or one of the video statuses

ffprobe behavior:

- call ffprobe only for one supported video file
- do not call ffprobe for image, missing, unsupported, or duplicate scenes
- use `subprocess.run` with `shell=False`, `timeout`, `capture_output=True`, and `text=True`
- command form: `ffprobe -v error -print_format json -show_streams -show_format <asset_path>`
- parse JSON output
- prefer `format.duration` for `asset_duration_sec`
- fall back to first video stream `duration`
- read first video stream `width`, `height`, and `codec_name`
- if the executable is missing while probing a video, raise a clear `SyncCutError` naming `ffprobe` and `--ffprobe-bin`
- if ffprobe exits nonzero, times out, returns invalid JSON, has no video stream, has missing duration, or reports empty/zero/negative duration, mark that scene `unreadable` with `unreadable_metadata` and continue
- never invoke `ffmpeg`

Primary statuses:

- `missing`: no matching local source file exists
- `unsupported`: only unsupported same-stem files exist
- `duplicate_supported`: more than one supported same-stem file exists
- `unreadable`: ffprobe failed or returned invalid metadata for a video
- `image_ok`: supported image asset found; duration-independent
- `video_ok`: video duration is close enough
- `video_short_loops`: video duration is shorter than scene duration and will loop
- `video_very_short_repetitive`: video loops more than the configured threshold or is below the configured duration ratio
- `video_long_trimmed`: video duration is longer than scene duration and Remotion scene duration will trim playback

Warning codes:

- `loops`
- `repetitive_loop`
- `trimmed`
- `aspect_ratio_warning`
- `unreadable_metadata`

Readiness rules:

- supported images are `image_ok`; no ffprobe call is made and `asset_duration_sec` is null
- missing or invalid scene duration becomes `unreadable` with a deterministic note such as `missing_scene_duration`
- use a fixed `0.25` second equality tolerance
- if `abs(asset_duration_sec - scene_duration_sec) <= 0.25`, the primary status is `video_ok`
- if `asset_duration_sec < scene_duration_sec - 0.25`, compute `loops_needed = scene_duration_sec / asset_duration_sec`
- if `loops_needed > max_loops_before_warning` or `asset_duration_sec / scene_duration_sec < min_duration_ratio`, status is `video_very_short_repetitive` with `loops` and `repetitive_loop`
- otherwise shorter videos are `video_short_loops` with `loops`
- if `asset_duration_sec > scene_duration_sec + 0.25`, status is `video_long_trimmed` with `trimmed`
- if `width` and `height` are positive and `width / height` is outside `[aspect_min, aspect_max]`, add `aspect_ratio_warning`
- aspect warnings do not replace the primary duration status
- notes are deterministic and human-readable

JSON output should include:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut inspect-visual-duration",
        "source_props": "remotion/props.json",
        "assets_dir": "assets/visuals",
        "format": "json",
        "ffprobe_bin": "ffprobe",
        "ffprobe_timeout_sec": 15,
        "thresholds": {
          "max_loops_before_warning": 3,
          "min_duration_ratio": 0.4,
          "aspect_min": 1.55,
          "aspect_max": 1.9
        }
      },
      "summary": {
        "target_scenes": 17,
        "images": 0,
        "videos": 17,
        "missing": 0,
        "unsupported": 0,
        "duplicate_supported": 0,
        "unreadable": 0,
        "image_ok": 0,
        "video_ok": 0,
        "video_short_loops": 0,
        "video_very_short_repetitive": 0,
        "video_long_trimmed": 0,
        "aspect_ratio_warning": 0
      },
      "scenes": [
        {
          "scene_id": "scene_001",
          "section_key": "01_HOOK",
          "section": "Hook",
          "visual_type": "AI_VIDEO",
          "scene_duration_sec": 9.137,
          "scene_duration_frames": 274,
          "asset_path": "assets/visuals/scene_001.mp4",
          "asset_kind": "video",
          "status": "video_short_loops",
          "warnings": ["loops"],
          "asset_duration_sec": 3.2,
          "loops_needed": 2.86,
          "width": 1920,
          "height": 1080,
          "aspect_ratio": 1.7778,
          "codec": "h264",
          "notes": "Video is shorter than scene duration and will loop."
        }
      ]
    }

JSON formatting is `indent=2`, `ensure_ascii=False`, with a trailing newline. The summary counts are `target_scenes`, `images`, `videos`, `missing`, `unsupported`, `duplicate_supported`, `unreadable`, `image_ok`, `video_ok`, `video_short_loops`, `video_very_short_repetitive`, `video_long_trimmed`, and `aspect_ratio_warning`. Each scene row includes `scene_id`, `section_key`, `section`, `visual_type`, `scene_duration_sec`, `scene_duration_frames`, `asset_path`, `asset_kind`, `status`, `warnings`, `asset_duration_sec`, `loops_needed`, `width`, `height`, `aspect_ratio`, `codec`, and `notes`.

Markdown output should include a title, source/assets summary, threshold summary, counts, and a scene table with these columns:

- `scene_id`
- `section_key`
- `visual_type`
- `scene_sec`
- `asset`
- `kind`
- `asset_sec`
- `loops`
- `dimensions`
- `status`
- `warnings`
- `notes`

Output write policy:

- if the output path is missing, write it
- if existing content is identical, reuse it
- if existing content differs and `--overwrite` is false, raise `SyncCutError` mentioning `--overwrite`
- if `--overwrite` is true, replace only the requested report file
- never mutate media or props

Tests should use mocked subprocess or an injected probe runner. Unit tests must not require real `ffprobe` or real media files. Milestone 3 tests should cover target filtering, scene order, missing, unsupported, duplicate-supported, image without probe, near-equal video, short loops, very-short repetitive loops, long trimmed video, aspect warning, unreadable ffprobe results, lazy missing-ffprobe error only for video probing, JSON determinism, Markdown summary/table output, identical report reuse, differing output conflict, overwrite, CLI Markdown success, CLI JSON success, CLI conflict, and CLI missing-ffprobe messaging.

Implementation files for Milestone 3 are:

    synccut/visual_duration.py
    synccut/cli.py
    tests/test_visual_duration.py
    tests/test_cli.py
    docs/plans/visual-duration-readiness-handling.md

### Milestone 3: implement visual duration readiness command

Add a new module `synccut/visual_duration.py`. Keep the logic pure and testable where possible. Reuse constants from `synccut.visual_assets` for target visual types and supported suffixes. Reuse or mirror the direct-child same-stem source-file inspection behavior from `visual_manifest.py` so the new command agrees with existing visual manifest status.

Use `subprocess.run` with `shell=False`, a timeout, and `ffprobe` JSON output for video files only. A safe ffprobe invocation should look like:

    ffprobe -v error -print_format json -show_streams -show_format assets/visuals/scene_001.mp4

From the JSON, read video duration from `format.duration` when present, otherwise from the first video stream duration. Read width, height, and codec from the first video stream. Treat invalid JSON, nonzero exit, timeout, missing video stream, or missing duration as `unreadable` for that scene rather than crashing the entire report, unless `ffprobe` itself is missing. If the executable is missing, raise a clear `SyncCutError` that names `ffprobe` and suggests installing FFmpeg tools or passing `--ffprobe-bin`.

Do not probe image dimensions unless Milestone 2 finds an existing dependency or simple safe standard-library path. In the default plan, classify supported images as `image_ok` with `asset_duration_sec: null`.

Wire a new Typer command in `synccut/cli.py`:

    synccut inspect-visual-duration PROPS_JSON --assets-dir assets/visuals --out generated/visual_duration_report.md --format markdown

Add tests:

- target filtering includes only `AI_VIDEO` and `B_ROLL`
- missing local file becomes `missing`
- unsupported-only local file becomes `unsupported`
- duplicate supported local files become `duplicate_supported`
- image file becomes `image_ok` without ffprobe call
- video equal/near scene duration becomes `video_ok`
- video shorter than scene becomes `video_short_loops`
- video very short becomes `video_very_short_repetitive`
- video longer than scene becomes `video_long_trimmed`
- far aspect ratio adds `aspect_ratio_warning`
- unreadable ffprobe result becomes `unreadable`
- missing ffprobe executable raises clear `SyncCutError`
- JSON output is deterministic and parseable
- Markdown output includes summary and scene table
- identical report output reuses existing file
- differing report output blocks and mentions `--overwrite`
- overwrite replaces requested report
- CLI success output for Markdown and JSON
- CLI conflict output mentions `--overwrite`

Run:

    .venv/bin/python -m pytest

Acceptance for Milestone 3: tests pass, no real media is required by tests, no props/media are mutated, and no render is run.

### Milestone 4: local validation

Run validation against the sample workspace. If sample props need refreshing, use:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json

Generate reports:

    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.md
    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.json --format json

Inspect:

    sed -n '1,220p' generated/visual_duration_report.md
    sed -n '1,220p' generated/visual_duration_report.json

Confirm:

- target scene count
- image/video counts
- missing, unsupported, duplicate, unreadable counts
- short-loop, very-short, long-trimmed, and aspect warnings
- report clearly identifies scenes that need manual replacement before render
- no media file changed
- `remotion/props.json` did not change except if regenerated for validation and later restored

Run:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..

Do not render.

Acceptance for Milestone 4: the sample report is useful for review and the validation commands pass. If `ffprobe` is unavailable in the local environment, record that exact limitation and ensure tests still pass with mocked probing.

### Milestone 5: docs, cleanup, final review

Decide whether README needs a concise note. If updated, keep it brief:

- `inspect-visual-duration` reports local visual duration/resolution readiness
- it uses `ffprobe` for video metadata inspection only
- it does not modify media, mutate props, prepare assets, or render
- reports are written under ignored `generated/`

Do not edit `.gitignore` unless a new unignored generated path is introduced. `generated/` should already cover report outputs.

Clean validation reports:

    rm -f generated/visual_duration_report.md generated/visual_duration_report.json
    rmdir generated 2>/dev/null || true

If `remotion/props.json` changed only due to validation regeneration, restore it:

    git restore remotion/props.json

Run final validation:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

Expected commit candidates after implementation:

    synccut/visual_duration.py
    synccut/cli.py
    tests/test_visual_duration.py
    tests/test_cli.py
    docs/plans/visual-duration-readiness-handling.md
    README.md only if updated

Not expected:

    generated/visual_duration_report.md
    generated/visual_duration_report.json
    remotion/props.json
    assets/visuals/*
    remotion/public/*
    remotion/out/*
    downloaded media
    transformed media
    API key files
    caches
    .venv/
    remotion/node_modules/

Recommended commit message:

    Add visual duration readiness reporting

After Phase 33, ask the user before starting Phase 34 Remotion visual quality polish.

## Concrete Steps

Milestone 1 audit commands:

    sed -n '1,260p' remotion/src/components/VisualAssetScene.tsx
    sed -n '1,320p' synccut/visual_manifest.py
    sed -n '1,260p' synccut/visual_assets.py
    sed -n '1,260p' synccut/preflight.py
    sed -n '1,360p' synccut/cli.py
    command -v ffprobe
    ffprobe -version
    git status --short --ignored

Milestone 4 validation commands:

    .venv/bin/python -m pytest
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.md
    .venv/bin/synccut inspect-visual-duration remotion/props.json --assets-dir assets/visuals --out generated/visual_duration_report.json --format json
    sed -n '1,220p' generated/visual_duration_report.md
    sed -n '1,220p' generated/visual_duration_report.json
    cd remotion && npm run typecheck && cd ..

Milestone 5 final validation commands:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

## Validation and Acceptance

The feature is accepted when:

- `synccut inspect-visual-duration` exists.
- It reads `remotion/props.json` and local files under `assets/visuals/`.
- It inspects only `AI_VIDEO` and `B_ROLL` scenes.
- It uses `ffprobe` only for video metadata inspection.
- It reports missing, unsupported, duplicate, unreadable, image, short-looping video, very-short/repetitive video, long-trimmed video, and aspect-ratio warning cases.
- It writes deterministic Markdown and JSON reports.
- It does not modify media.
- It does not mutate `remotion/props.json`.
- It does not run `prepare-visual-assets`.
- It does not use `ffmpeg`.
- It does not render.
- Unit tests mock ffprobe/subprocess and do not require real media or real ffprobe.
- `.venv/bin/python -m pytest` passes.
- `cd remotion && npm run typecheck && cd ..` passes.
- Generated reports are cleaned or ignored before final review.

## Idempotence and Recovery

The command should be safe to run repeatedly. It reads props and local media metadata and writes only the requested report file. If the report path does not exist, create it. If it exists with identical content, reuse it. If it exists with different content, block unless `--overwrite` is set. With `--overwrite`, replace only the requested report file.

ffprobe failures for individual video files should produce `unreadable` scene results rather than aborting the whole report. Missing ffprobe executable should fail clearly only when a supported video actually needs probing; image-only, missing, unsupported, and duplicate-only reports should not require ffprobe. If validation regenerates `remotion/props.json`, restore it before final review unless the user explicitly approves a sample props refresh.

## Artifacts and Notes

Generated report outputs:

    generated/visual_duration_report.md
    generated/visual_duration_report.json

These are local validation artifacts and should not be committed.

This phase is allowed to inspect metadata with `ffprobe`, but it is not allowed to call `ffmpeg`, transcode, trim, crop, normalize, generate, download, copy, prepare, or render media. A report may say a video will loop or be trimmed by the Remotion scene duration; it must not perform the loop or trim itself.

## Interfaces and Dependencies

Use Python standard library `subprocess.run` for ffprobe. Do not use `shell=True`. Use a timeout for each probe, for example 15 seconds. Use ffprobe JSON output:

    ffprobe -v error -print_format json -show_streams -show_format <path>

In `synccut/visual_duration.py`, define dataclasses similar to:

    @dataclass(frozen=True)
    class VisualDurationProbe:
        duration_sec: float | None
        width: int | None
        height: int | None
        codec: str | None

    @dataclass(frozen=True)
    class VisualDurationSceneResult:
        scene_id: str
        section_key: str | None
        visual_type: str
        scene_duration_sec: float | None
        asset_path: Path | None
        asset_kind: str | None
        status: str
        warnings: list[str]
        asset_duration_sec: float | None
        loops_needed: float | None
        width: int | None
        height: int | None
        aspect_ratio: float | None
        codec: str | None
        notes: str

    @dataclass(frozen=True)
    class VisualDurationReport:
        props_path: Path
        assets_dir: Path
        output_format: str
        scenes: list[VisualDurationSceneResult]
        summary: dict[str, int]

Public functions should include:

    build_visual_duration_report(...)
    write_visual_duration_report_file(...)
    format_visual_duration_report(...)

The CLI should import only the write/report function and keep command code thin. Tests should inject a fake probe function or monkeypatch subprocess so they never require real ffprobe or real media.

## Change Note

Revision 2026-05-17: Initial Phase 33 ExecPlan created. It records the user's approval for ffprobe metadata inspection, defines a read-only visual duration/readiness workflow, keeps media transformations and rendering out of scope, and lays out milestones for audit, design, implementation, local validation, and final review.
