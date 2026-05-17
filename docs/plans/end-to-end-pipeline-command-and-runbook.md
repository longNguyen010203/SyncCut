# End-to-end pipeline command and runbook

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, and validate an end-to-end pipeline command plus a user-facing runbook from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut now has individual commands for preparing narration text, generating audio and alignment, building timelines, exporting Remotion props, preparing local assets, reporting visual readiness, downloading B-roll, checking visual duration, and running preflight. A user can reach a final video today, but only by remembering and chaining many commands manually. This phase adds a safe orchestration layer and a clear runbook so a user can move from `scenes.json` to a render-ready project with fewer missed steps.

After this phase, a user should be able to run a command like:

    .venv/bin/synccut pipeline-check examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --visual-assets-dir assets/visuals

and see a step-by-step local readiness summary covering timeline build, timeline validation, Remotion props export, Remotion audio preparation, visual manifest creation, optional visual duration reporting, visual preparation, visual readiness inspection, and verified preflight. The command must not call real external APIs, download B-roll, render video, transcode media, trim media, crop media, normalize media, or implement Remotion visual polish. Rendering remains a manual Remotion command documented in the runbook.

## Progress

- [x] (2026-05-17T02:10:00+07:00) Read `.agent/PLANS.md`, README, recent audio/visual/provider plans, Remotion package scripts, relevant SyncCut modules, and current git status.
- [x] (2026-05-17T02:10:00+07:00) Created this Phase 34 ExecPlan.
- [x] (2026-05-17T14:42:52+07:00) Milestone 1: audited existing SyncCut CLI commands, Remotion npm scripts, README/runbook fragments, prior final-render plans, automation safety, and current working tree status.
- [x] (2026-05-17T14:48:44+07:00) Milestone 2: finalized the `pipeline-check` command contract, defaults, step order, visual-duration skip policy, visual-preparation mutation policy, JSON report contract, failure behavior, test plan, and README runbook structure.
- [x] (2026-05-17T14:57:25+07:00) Milestone 3: implemented `synccut pipeline-check`, added the orchestration module and focused tests, verified ffprobe-unavailable handling is non-fatal, and passed the Python test suite.
- [x] (2026-05-17T15:02:58+07:00) Milestone 4: validated `pipeline-check` on the TSMC sample, inspected generated reports, passed pytest and Remotion typecheck, cleaned generated reports, restored regenerated props, and reviewed artifact status.
- [x] (2026-05-17T15:08:57+07:00) Milestone 5: added the README runbook, kept `.gitignore` unchanged, passed final pytest and Remotion typecheck, verified artifact status, and completed Phase 34 final review.

## Surprises & Discoveries

- Observation: The README already documents most individual commands, but it does not provide one complete runbook from `scenes.json` to final video.
  Evidence: README has sections for Quick Start, Pipeline Overview, Local Visual Assets, Remotion Workflow, and Artifact Policy, but users still need to compose manual flows from separate sections.
- Observation: The core prepared-input path is safe to automate because it is local and deterministic, but it still writes generated outputs.
  Evidence: `build-timeline` reads `scenes.json`, section audio, and section alignments, then writes `timeline.json`; `validate-timeline` reads `timeline.json` and is read-only; `export-remotion` reads `timeline.json` and writes the requested props file, typically `remotion/props.json`.
- Observation: Remotion asset preparation is local but intentionally mutates props.
  Evidence: `prepare-remotion-assets` copies or reuses audio files under `remotion/public/audio/` and writes public audio paths back into the props file. `prepare-visual-assets` copies or reuses one supported local visual per target scene under `remotion/public/visuals/` and writes visual public-path/status metadata back into props.
- Observation: The optional audio-generation path is explicitly outside a default pipeline check.
  Evidence: `prepare-narration` is local and writes a generated narration package from `scenes.json`, but `generate-audio` consumes that package and, outside dry-run or injected tests, uses a provider such as ElevenLabs with `ELEVENLABS_API_KEY` to write section audio, alignment JSON, and generation metadata.
- Observation: The optional B-roll path is explicitly outside a default pipeline check.
  Evidence: `visual-manifest` is local and report-only, but `download-broll` real runs consume the JSON manifest, require provider configuration such as `PEXELS_API_KEY`, download media, write local assets, and write downloader metadata. Its dry-run mode is safe, but real provider work should remain explicit.
- Observation: Visual duration readiness is useful but ffprobe-dependent only when supported video assets are present.
  Evidence: `inspect-visual-duration` reads props and local `assets/visuals` filenames, writes a generated Markdown or JSON report, and calls ffprobe only for one supported video candidate per target scene. It does not mutate props or media, but missing ffprobe must be handled as an optional/skippable pipeline step.
- Observation: Current Remotion scripts already separate typecheck and render work.
  Evidence: `remotion/package.json` has `typecheck`, `still:local`, `render:smoke:local`, `render:segment:local`, and `render:final:local`. The Python CLI should not render by default.
- Observation: Some existing commands intentionally mutate `remotion/props.json`.
  Evidence: `prepare_remotion_assets_file` writes audio public paths back to props, and `prepare_visual_assets_file` copies local visual files into `remotion/public/visuals/` and writes visual metadata back to props.
- Observation: Some existing commands are read-only or report-only.
  Evidence: `validate-timeline`, `inspect`, `visual-manifest`, `inspect-visual-assets`, `preflight`, and `inspect-visual-duration` can be used to check state without external APIs or media generation. `visual-manifest` and `inspect-visual-duration` write generated reports, but do not mutate props or media.
- Observation: Current command side effects split cleanly into read-only checks, generated report writes, props/public preparation, provider media generation/download, and Remotion rendering.
  Evidence: `inspect-visual-assets` and `preflight` are read-only; `visual-manifest` and `inspect-visual-duration` write generated reports; `export-remotion`, `prepare-remotion-assets`, and `prepare-visual-assets` write props or public files; `generate-audio` and `download-broll` may call external providers and write media; Remotion render scripts write `remotion/out/*`.
- Observation: The current working tree is clean except for the new Phase 34 plan and ignored local artifacts.
  Evidence: `git status --short --ignored` reported `?? docs/plans/end-to-end-pipeline-command-and-runbook.md` plus ignored `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `generated/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: `ffprobe` is missing in this local environment.
  Evidence: Phase 33 recorded `ffprobe` as unavailable. A pipeline command should allow visual duration checks to be skipped or clearly reported when ffprobe is unavailable.
- Observation: `generated/`, `assets/visuals/`, `remotion/public`, `remotion/out/`, and `timeline.json` are already ignored.
  Evidence: `.gitignore` contains those paths, so generated reports and local validation artifacts should not become commit candidates.
- Observation: Prior final-render plans reinforce that rendering should remain manual.
  Evidence: `docs/plans/final-release-render-quality-review.md` and `docs/plans/post-polish-final-render-review.md` both use the existing `render:final:local` npm script for full renders, record Chrome sandbox and media-artifact risks, and treat render outputs and prepared props as generated/local validation state rather than default pipeline side effects.
- Observation: The main design tension is that users want full verified preflight, but full visual preparation intentionally rewrites props and copies local media into `remotion/public/visuals/`.
  Evidence: `prepare_visual_assets_file` is the only existing way to make local AI_VIDEO/B_ROLL visuals render from public paths. The design therefore defaults visual preparation on, but the CLI must name that side effect and provide `--no-prepare-visual-assets` for placeholder/no-visual checks.
- Observation: If visual preparation is disabled or local visual files are missing, verified preflight can still complete with warning status rather than hard failure.
  Evidence: `preflight` treats missing AI_VIDEO/B_ROLL public paths as `visual_missing` warnings and keeps `errors` and `file_errors` at zero when audio public paths and verified files are valid. The pipeline should fail only on preflight errors or file errors, not on warning-only missing optional visuals.
- Observation: Existing report writers already support deterministic generated outputs but block on differing existing files unless `overwrite=True`.
  Evidence: `write_visual_manifest_file` and `write_visual_duration_report_file` both compare planned content to the existing report and require overwrite for differing content. The pipeline design uses `overwrite_reports=True` by default so reruns are predictable.
- Observation: The pipeline implementation could use existing file-level functions without shelling out to SyncCut's own CLI.
  Evidence: `synccut/pipeline.py` calls `load_scenes`, `load_section_assets`, `build_timeline`, `validate_timeline`, `export_remotion_props_file`, `prepare_remotion_assets_file`, `write_visual_manifest_file`, `write_visual_duration_report_file`, `prepare_visual_assets_file`, `inspect_visual_asset_readiness_file`, and `inspect_preflight_file` directly.
- Observation: The Typer rich help output truncates long dual-option names in narrow help tables.
  Evidence: The first test run failed only because the help text displayed `--skip-visual-dura…` and `--prepare-visual-a…`; the test was adjusted to assert visible option stems instead of exact long strings.
- Observation: The implemented ffprobe policy is non-fatal for clear ffprobe availability errors.
  Evidence: `run_pipeline_check` catches visual-duration `SyncCutError` messages naming `ffprobe` or `--ffprobe-bin`, records the `inspect_visual_duration` step as `WARN`, and continues to visual preparation, visual inspection, preflight, and report writing.
- Observation: The pipeline report path is fixed by default under the generated directory.
  Evidence: Milestone 3 writes `generated/pipeline_check_report.json` through the `pipeline_report_out` default of `generated_dir / "pipeline_check_report.json"`.
- Observation: `ffprobe` is available in the Milestone 4 environment, unlike the earlier Phase 33 audit.
  Evidence: `command -v ffprobe` returned `/usr/bin/ffprobe`, and `ffprobe -version` reported version `4.4.2-0ubuntu0.22.04.1`.
- Observation: Sample `pipeline-check` completed without provider, download, render, or media-transform behavior.
  Evidence: `.venv/bin/synccut pipeline-check examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --visual-assets-dir assets/visuals` completed with `passed: 9`, `warnings: 1`, `skipped: 0`, `failed: 0`, and printed manual Remotion next-step commands. No ElevenLabs, Pexels, Pixabay, npm, render, ffmpeg, transcode, trim, crop, or normalize command was run by the pipeline.
- Observation: The one sample pipeline warning came from real visual duration readiness, not pipeline failure.
  Evidence: `generated/pipeline_check_report.json` recorded `inspect_visual_duration` as `WARN` with `visual_duration_warnings: 17`. The generated duration report found 17 target videos, 0 missing, 0 unsupported, 0 unreadable, 6 `video_short_loops`, 10 `video_very_short_repetitive`, 1 `video_long_trimmed`, and 0 aspect-ratio warnings.
- Observation: The generated visual manifest is useful before visual preparation because it shows source-file availability separately from props readiness.
  Evidence: `generated/visual_manifest.md` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, `local_found: 17`, `local_missing: 0`, `local_duplicate_supported: 0`, and `local_unsupported_only: 0`.
- Observation: The pipeline prepared the sample into full verified visual readiness.
  Evidence: The pipeline report recorded audio `audio_reused: 7`, visual manifest local found `17`, visual preparation `visual_reused: 17`, visual readiness `prepared: 17`, `missing: 0`, `unsupported: 0`, and verified preflight status `ok` with `errors: 0` and `file_errors: 0`.
- Observation: Generated validation reports were cleaned and props were restored after validation.
  Evidence: `rm -f generated/pipeline_check_report.json generated/visual_manifest.md generated/visual_manifest.json generated/visual_duration_report.md` removed the report outputs, `git restore remotion/props.json` restored sample props, and focused status no longer listed `remotion/props.json` or generated reports as commit candidates.
- Observation: The README now has a single end-to-end runbook while preserving detailed command-specific sections.
  Evidence: `README.md` now includes `From scenes.json to final video` with prerequisites, the recommended `pipeline-check` workflow, the manual command-by-command workflow, optional generated audio/alignment, optional B-roll download, manual Remotion typecheck/render commands, artifact notes, and troubleshooting.
- Observation: Final validation stayed within expected text/source/test changes.
  Evidence: `.venv/bin/python -m pytest` collected 320 tests and all 320 passed. `npm run typecheck` from `remotion/` passed. Focused status listed only `README.md`, `synccut/cli.py`, `tests/test_cli.py`, `docs/plans/end-to-end-pipeline-command-and-runbook.md`, `synccut/pipeline.py`, and `tests/test_pipeline.py`.

## Decision Log

- Decision: Phase 34 should start with `pipeline-check`, not render automation.
  Rationale: The user wants the workflow easier to run, but rendering has browser, Chrome sandbox, and runtime cost/failure modes that are better kept explicit. `pipeline-check` can make the project render-ready and point to manual Remotion commands.
  Date/Author: 2026-05-17 / Codex
- Decision: `pipeline-check` should not call real ElevenLabs, Pexels, or Pixabay.
  Rationale: Real provider calls require keys, may incur cost or rate-limit effects, and are already exposed through explicit commands with dry-run behavior. The pipeline command should preserve debuggability and safety.
  Date/Author: 2026-05-17 / Codex
- Decision: `pipeline-check` should not run providers, downloads, or Remotion render scripts by default.
  Rationale: Provider and render steps cross boundaries from local deterministic readiness into external services, local browser rendering, binary media writes, and potentially expensive or slow operations. They should remain explicit commands documented in the runbook.
  Date/Author: 2026-05-17 / Codex
- Decision: `pipeline-check` may call existing local deterministic functions, including export and preparation functions that intentionally mutate generated props.
  Rationale: Building render-ready Remotion props requires export plus audio public-path preparation, and full local visual preparation requires `prepare-visual-assets`. These are existing explicit local steps. The command must report when it mutates `remotion/props.json` through those known steps.
  Date/Author: 2026-05-17 / Codex
- Decision: Remotion typecheck should be optional, not default.
  Rationale: It requires Node dependencies and leaves the Python pipeline command dependent on a separate toolchain. The runbook should document `cd remotion && npm run typecheck`, and Milestone 2 can decide whether to add `--typecheck` later.
  Date/Author: 2026-05-17 / Codex
- Decision: Remotion typecheck and render should stay manual or optional in the design.
  Rationale: `npm run typecheck` is non-rendering but Node-dependent, while `still:local`, `render:smoke:local`, `render:segment:local`, and `render:final:local` are render scripts that write ignored outputs under `remotion/out/`. Keeping them out of the default Python path preserves the current tool boundary.
  Date/Author: 2026-05-17 / Codex
- Decision: Props mutation is acceptable only through explicit export and preparation steps.
  Rationale: `remotion/props.json` is tracked sample state, while export, audio preparation, and visual preparation are known commands that can intentionally rewrite it. A pipeline command must name those mutations and the runbook must explain restoring props after validation when needed.
  Date/Author: 2026-05-17 / Codex
- Decision: Phase 34 must preserve all existing individual commands.
  Rationale: The pipeline command is an orchestration convenience and runbook aid, not a replacement for the existing debuggable command-by-command workflow.
  Date/Author: 2026-05-17 / Codex
- Decision: The Phase 34 command name is `pipeline-check`; `pipeline-run` is future work only.
  Rationale: `pipeline-check` accurately describes the safe local readiness workflow. `pipeline-run` could imply provider calls, downloads, or rendering, which are intentionally excluded from this phase.
  Date/Author: 2026-05-17 / Codex
- Decision: The CLI options are `SCENES_JSON`, `--audio-dir`, `--alignment-dir`, `--visual-assets-dir assets/visuals`, `--timeline-out timeline.json`, `--props-out remotion/props.json`, `--public-dir remotion/public`, `--generated-dir generated`, `--skip-visual-duration/--no-skip-visual-duration`, `--overwrite-reports/--no-overwrite-reports`, and `--prepare-visual-assets/--no-prepare-visual-assets`.
  Rationale: These options expose the real paths users need without introducing provider, render, or cleanup behavior. Defaults match the existing sample workflow and ignored local paths.
  Date/Author: 2026-05-17 / Codex
- Decision: `skip_visual_duration` defaults to `False`, but missing or unavailable ffprobe is downgraded to a warning/skipped step and does not fail the full pipeline.
  Rationale: Phase 33 confirmed ffprobe is missing locally. Visual duration reporting is valuable when available, but a missing optional inspector should not block the core render-readiness flow; the report should say to install FFmpeg tools or rerun with a usable `--ffprobe-bin` in the standalone command if needed.
  Date/Author: 2026-05-17 / Codex
- Decision: `prepare_visual_assets` defaults to `True`.
  Rationale: A practical end-to-end readiness check should reach verified preflight with local visuals prepared when assets exist. The command must clearly report that this runs the existing local preparation behavior, copies/reuses files under `remotion/public/visuals/`, and mutates `props_out`.
  Date/Author: 2026-05-17 / Codex
- Decision: `overwrite_reports` defaults to `True`.
  Rationale: The pipeline writes deterministic generated reports under ignored `generated/`; default overwrite avoids rerun friction while limiting overwrites to known report paths. User media and render outputs are not deleted or overwritten by this flag.
  Date/Author: 2026-05-17 / Codex
- Decision: The exact pipeline step order is build timeline, validate timeline, export Remotion props, prepare Remotion audio assets, write visual manifest Markdown, write visual manifest JSON, inspect visual duration Markdown, optionally prepare visual assets, inspect visual assets, and verified preflight.
  Rationale: This follows the current manual workflow and ensures preflight sees props after the preparation steps that intentionally add public paths.
  Date/Author: 2026-05-17 / Codex
- Decision: `pipeline-check` writes `generated/pipeline_check_report.json`.
  Rationale: A deterministic report makes the orchestration auditable, testable, and useful in CI or later automation without parsing console output.
  Date/Author: 2026-05-17 / Codex
- Decision: `pipeline-check` does not run `npm run typecheck` or any render script by default, and Phase 34 will not add a `--typecheck` flag unless a later milestone explicitly revisits it.
  Rationale: Keeping the first implementation Python-only avoids a Node dependency in the orchestration command and keeps Remotion validation/rendering as clearly documented manual next steps.
  Date/Author: 2026-05-17 / Codex
- Decision: Pipeline hard failures write a partial report before returning an error.
  Rationale: A partial report with completed steps plus a final `FAIL` step makes failures easier to inspect and test while preserving fail-fast behavior.
  Date/Author: 2026-05-17 / Codex
- Decision: The CLI prints the same `format_pipeline_summary` output that tests use.
  Rationale: Keeping console formatting in `synccut/pipeline.py` avoids duplicating summary logic in the CLI and keeps `synccut/cli.py` thin.
  Date/Author: 2026-05-17 / Codex
- Decision: Add the runbook to README and do not change `.gitignore`.
  Rationale: Users need the end-to-end workflow in the primary onboarding document, while `generated/`, `assets/`, `remotion/public/`, `remotion/out/`, and `timeline.json` were already ignored, so no ignore-rule change was needed.
  Date/Author: 2026-05-17 / Codex
- Decision: Rendering remains manual after Phase 34.
  Rationale: The README now points to manual Remotion commands, and `pipeline-check` does not call npm or render video.
  Date/Author: 2026-05-17 / Codex
- Decision: Provider and download workflows remain explicit optional commands.
  Rationale: The README documents `prepare-narration`, `generate-audio`, and `download-broll` as optional workflows, and states that `pipeline-check` does not call provider APIs or download assets.
  Date/Author: 2026-05-17 / Codex
- Decision: Remotion visual quality polish is postponed.
  Rationale: The user explicitly said the former Phase 35 and Phase 36 should be done before Remotion visual polish. Phase 34 must not add captions, transitions, title cards, motion effects, or rendering changes.
  Date/Author: 2026-05-17 / Codex

## Outcomes & Retrospective

This plan has been created but not implemented. No source code, tests, README, `.gitignore`, generated reports, props files, media files, downloads, render outputs, commits, tags, or pushes were created while authoring the plan.

The intended outcome is a safer, easier workflow. At completion, users should have a `pipeline-check` command for local deterministic readiness checks and a README runbook that explains both the consolidated command and the manual command-by-command route from `scenes.json` to final Remotion render. The next step is Milestone 1: audit the existing command workflow and classify each command by side effects and automation safety.

Milestone 1 is complete. The audit classified each current command by inputs, outputs, side effects, and automation suitability. The safe default core is `build-timeline`, `validate-timeline`, `export-remotion`, `prepare-remotion-assets`, `visual-manifest` Markdown/JSON generation, `inspect-visual-assets`, and verified `preflight`. `prepare-visual-assets` is local and deterministic but mutates props and copies local media, so Milestone 2 must decide whether it is default or explicitly opt-in. `inspect-visual-duration` is report-only but should be optional or skippable because ffprobe is missing locally and should only be required when probing supported video assets.

Provider and render work are excluded from default automation. `generate-audio` can call ElevenLabs and write audio/alignment outputs; `download-broll` can call Pexels and write local media; both remain explicit optional workflows. Remotion `typecheck` is a useful manual or optional validation step, while `still:local`, `render:smoke:local`, `render:segment:local`, and `render:final:local` are render scripts that should be documented as manual next steps rather than run by Python by default.

The README has all major ingredients but not a single end-to-end runbook. Existing final-render plans show the manual final render path and reinforce that render outputs, public assets, generated reports, and local media must remain ignored or cleaned. Current working tree review shows only this Phase 34 plan as the nonignored change, plus ignored local artifacts. The next step is Milestone 2: design the exact `pipeline-check` command, defaults, report contract, mutation policy, skip behavior for ffprobe, and README runbook structure.

Milestone 2 is complete. The implementation target is a single `pipeline-check` command, not `pipeline-run`, with no provider calls, downloads, npm typecheck, or render automation. The command defaults to preparing local visual assets because that is the most useful render-readiness path, but it must explicitly report that `props_out` is mutated through `export-remotion`, `prepare-remotion-assets`, and `prepare-visual-assets`, and it must support `--no-prepare-visual-assets` for no-visual or placeholder checks.

The visual duration step defaults to attempted reporting but is non-blocking when ffprobe is missing or unavailable. If the user passes `--skip-visual-duration`, the step is recorded as skipped without trying the report. If the step is attempted and fails with a clear ffprobe availability error, the pipeline records `WARN` or `SKIP` and continues; unexpected visual-duration errors should still surface clearly. This keeps the command useful in environments like the current one where ffprobe is absent.

The pipeline report is part of the Milestone 3 implementation contract. It should be written to `generated/pipeline_check_report.json` and contain metadata paths, ordered step results, summary counts, and next-step commands for manual Remotion typecheck/render. The next step is Milestone 3: implement `synccut/pipeline.py`, wire `pipeline-check` into `synccut/cli.py`, and add focused tests without requiring real ffprobe, Node, network, provider APIs, render output, or real media metadata.

Milestone 3 is complete. `synccut/pipeline.py` now defines `PipelineStepResult`, `PipelineCheckResult`, `run_pipeline_check`, `pipeline_report_to_dict`, and `format_pipeline_summary`. The pipeline follows the Milestone 2 order, writes `generated/pipeline_check_report.json`, reports `PASS`, `WARN`, `SKIP`, and `FAIL` statuses, catches clear ffprobe availability failures as non-fatal visual-duration warnings, and writes a partial failure report before raising `SyncCutError` for hard failures.

`synccut/cli.py` now exposes `pipeline-check` with the designed path options and booleans. The command does not invoke provider, downloader, npm, render, ffmpeg, or cleanup behavior. It prints a command heading, ordered step summary, report path, and manual Remotion next-step hints.

Tests were added in `tests/test_pipeline.py` for successful orchestration, report JSON content, step ordering, skipped visual duration, missing ffprobe continuation, disabled visual preparation, preflight hard failure, and provider/downloader non-use. `tests/test_cli.py` now covers CLI execution, no-visual warning-only operation, and help exposure. `.venv/bin/python -m pytest` collected 320 tests and all 320 passed. The next step is Milestone 4: validate `pipeline-check` on the sample project without real API calls, downloads, npm from Python, or rendering.

Milestone 4 is complete. Final Python validation before the sample run passed: `.venv/bin/python -m pytest` collected 320 tests and all 320 passed. `ffprobe` is available locally at `/usr/bin/ffprobe`, version `4.4.2-0ubuntu0.22.04.1`, so the visual duration step ran instead of being skipped.

The sample `pipeline-check` run succeeded. It built `timeline.json`, validated the timeline, exported `remotion/props.json`, prepared 7 Remotion audio assets, wrote `generated/visual_manifest.md`, wrote `generated/visual_manifest.json`, wrote `generated/visual_duration_report.md`, prepared 17 visual assets, inspected visual assets, ran verified preflight, and wrote `generated/pipeline_check_report.json`. The final pipeline summary was `passed: 9`, `warnings: 1`, `skipped: 0`, and `failed: 0`. Verified preflight reported `status ok`, 33 scenes, 7 sections, 7 prepared audio assets, 17 prepared visuals, `errors: 0`, and `file_errors: 0`.

Generated report inspection matched expectations. The pipeline report captured the ordered 10-step run and manual next steps. The visual manifest reported 17 target scenes with 17 local source files found and no local missing, duplicate, or unsupported-only files. The visual duration report found 17 video assets and surfaced expected readiness warnings: 6 shorter looping videos, 10 very short repetitive looping videos, and 1 long trimmed video. No API calls, downloads, render commands, npm invocation from Python, ffmpeg usage, media transform, or Remotion visual-polish work occurred.

Remotion typecheck passed separately with `npm run typecheck` from `remotion/`. Validation cleanup removed the generated pipeline, visual manifest, and visual duration reports. `remotion/props.json` was restored after the validation regeneration; the first restore attempt was blocked by sandbox access to `.git/index.lock`, and the approved retry completed. Focused status after cleanup shows only the expected source/test/plan commit candidates for Phase 34. The next step is Milestone 5: README runbook/docs, cleanup confirmation, final validation, and artifact review.

Milestone 5 is complete. `README.md` now has a concise user-facing `From scenes.json to final video` runbook. It documents prerequisites, the recommended `pipeline-check` workflow, the manual command-by-command workflow, optional narration/audio generation, optional Pexels B-roll dry-run/download, manual Remotion typecheck/render commands, artifact policy, and troubleshooting. It explicitly states that `pipeline-check` does not call provider APIs, download B-roll, render video, or transform media.

Final validation passed. `.venv/bin/python -m pytest` collected 320 tests and all 320 passed. `npm run typecheck` from `remotion/` passed with `tsc --noEmit`. `.gitignore` was left unchanged because existing ignore rules already cover generated reports, local media, prepared public assets, render outputs, and `timeline.json`.

Final artifact review is clean. `remotion/props.json` is restored and not a commit candidate. Generated validation reports are absent or ignored only. No media, downloaded assets, render outputs, API key files, `.gitignore` changes, or generated props are commit candidates. The final expected commit candidates are `README.md`, `synccut/pipeline.py`, `synccut/cli.py`, `tests/test_pipeline.py`, `tests/test_cli.py`, and `docs/plans/end-to-end-pipeline-command-and-runbook.md`.

Phase 34 acceptance criteria are met. `synccut pipeline-check` exists, preserves individual commands, runs a local deterministic readiness pipeline through verified preflight, reports step statuses and a JSON report, does not render or download by default, does not call real providers, does not use ffmpeg or transform media, and is documented in the README runbook. Recommended commit message: `Add end-to-end pipeline check and runbook`. Next step: ask the user before starting the postponed Remotion visual quality polish phase.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python CLI implemented with Typer in `synccut/cli.py`. A Typer command is a Python function decorated with `@app.command(...)` that becomes available as `.venv/bin/synccut <command>`. The Remotion renderer is a Node/TypeScript project under `remotion/`; Remotion is not run by Python commands today.

The current prepared-input pipeline starts with `scenes.json`, section audio files such as `01_HOOK.mp3`, and section alignment JSON files such as `01_HOOK_alignment_tmp.json`. `build-timeline` creates `timeline.json`. `validate-timeline` validates it. `export-remotion` creates `remotion/props.json`. `prepare-remotion-assets` copies audio into `remotion/public/audio/` and annotates props. Optional visual workflows can create planning reports, download B-roll with Pexels when explicitly run with an API key, inspect local visual duration with ffprobe, copy local visual source files into `remotion/public/visuals/`, inspect visual readiness, and run preflight. A render then happens manually from `remotion/` using npm scripts.

Important modules:

    synccut/cli.py
    synccut/timeline_builder.py
    synccut/timeline_validator.py
    synccut/remotion_exporter.py
    synccut/remotion_assets.py
    synccut/visual_manifest.py
    synccut/broll_downloader.py
    synccut/visual_assets.py
    synccut/preflight.py
    synccut/visual_duration.py

Likely new files for this phase:

    synccut/pipeline.py
    tests/test_pipeline.py
    docs/plans/end-to-end-pipeline-command-and-runbook.md

Important generated or local artifact paths:

    timeline.json
    remotion/props.json
    remotion/public/
    remotion/out/
    generated/
    assets/visuals/

`timeline.json`, `generated/`, `assets/visuals/`, `remotion/public`, and `remotion/out/` are ignored. `remotion/props.json` is tracked as a sample file but should be restored after validation if regenerated only for local testing and not intentionally approved as a sample refresh.

## Plan of Work

### Milestone 1: current command workflow audit

Audit the existing commands and document their side effects before designing orchestration. Read `synccut/cli.py` and the implementation modules it calls. Record which commands are read-only, which write generated files, which mutate `remotion/props.json`, which copy local assets, which need API keys, which need ffprobe, which need Node, and which are safe to automate by default.

The commands to classify are `prepare-narration`, `generate-audio`, `build-timeline`, `validate-timeline`, `export-remotion`, `prepare-remotion-assets`, `visual-manifest`, `download-broll`, `inspect-visual-duration`, `prepare-visual-assets`, `inspect-visual-assets`, and `preflight`. Also classify Remotion `npm run typecheck`, `npm run still:local`, `npm run render:smoke:local`, `npm run render:segment:local`, and `npm run render:final:local`.

Read README and the final render review plans to capture current runbook fragments and release evidence. Do not edit source in this milestone.

Acceptance for Milestone 1: this plan records a command workflow audit that distinguishes read-only/report steps, generated-file steps, props-mutation steps, API-key/network steps, ffprobe-dependent steps, Node-dependent steps, and render steps.

### Milestone 2: pipeline command and runbook design

Design the command before coding. The recommended safe first command is:

    .venv/bin/synccut pipeline-check SCENES_JSON --audio-dir AUDIO_DIR --alignment-dir ALIGNMENT_DIR --visual-assets-dir assets/visuals

The command should not render, download, call provider APIs, or run Remotion typecheck by default. It should orchestrate existing Python functions directly rather than shelling out to its own CLI where practical, so errors remain testable and code stays deterministic.

Milestone 2 must decide the exact CLI shape. The expected options are:

    SCENES_JSON
    --audio-dir
    --alignment-dir
    --visual-assets-dir assets/visuals
    --timeline-out timeline.json
    --props-out remotion/props.json
    --public-dir remotion/public
    --generated-dir generated
    --skip-visual-duration
    --overwrite-reports
    --prepare-visual-assets / --no-prepare-visual-assets

The default should probably prepare local visual assets when files are present, because that is needed for full preflight, but Milestone 2 must decide this explicitly. If visual asset preparation is defaulted on, the command must make clear that `remotion/props.json` is intentionally mutated through existing local preparation steps. If visual asset preparation is defaulted off, the command must still produce useful visual manifest and preflight output.

The tentative pipeline steps are:

1. Build `timeline.json` from `scenes.json`, audio, and alignment inputs.
2. Validate `timeline.json`.
3. Export `remotion/props.json`.
4. Prepare Remotion audio assets into `remotion/public/audio/`.
5. Create `generated/visual_manifest.md`.
6. Create `generated/visual_manifest.json`.
7. Run `inspect-visual-duration` into `generated/visual_duration_report.md` when ffprobe is available or when not skipped.
8. Optionally run `prepare-visual-assets` from `assets/visuals/` into `remotion/public/visuals/`.
9. Run `inspect-visual-assets`.
10. Run `preflight --verify-files --public-dir remotion/public`.

Milestone 2 must define failure behavior. Recommended behavior is fail fast for scene loading, audio/alignment discovery, timeline build, timeline validation, props export, audio preparation, visual preparation, and preflight errors. Missing ffprobe should be either a clear warning when `--skip-visual-duration` is set or a clear failure that suggests rerunning with `--skip-visual-duration`; Milestone 2 should choose the safer default based on usability.

Milestone 2 must decide whether to write a pipeline report. A useful minimal report is `generated/pipeline_check_report.json` with step statuses, paths, counts, warnings, and next commands. If implemented, it should be deterministic and covered by tests. The command should always print a concise console summary.

Acceptance for Milestone 2: this plan records exact command options, default behavior, step order, mutation rules, report contract if any, failure behavior, test plan, and README runbook structure.

Milestone 2 design decision:

The command is:

    .venv/bin/synccut pipeline-check SCENES_JSON --audio-dir AUDIO_DIR --alignment-dir ALIGNMENT_DIR

Options and defaults:

    SCENES_JSON
    --audio-dir PATH
    --alignment-dir PATH
    --visual-assets-dir PATH          default: assets/visuals
    --timeline-out PATH               default: timeline.json
    --props-out PATH                  default: remotion/props.json
    --public-dir PATH                 default: remotion/public
    --generated-dir PATH              default: generated
    --skip-visual-duration / --no-skip-visual-duration
                                      default: --no-skip-visual-duration
    --overwrite-reports / --no-overwrite-reports
                                      default: --overwrite-reports
    --prepare-visual-assets / --no-prepare-visual-assets
                                      default: --prepare-visual-assets

No `pipeline-run` command is implemented in Phase 34. No provider options, API-key options, download options, npm typecheck option, render option, cleanup option, or ffmpeg option are added.

The exact step order is:

1. Build timeline from `SCENES_JSON`, `--audio-dir`, and `--alignment-dir` to `--timeline-out`.
2. Validate `--timeline-out`.
3. Export Remotion props from `--timeline-out` to `--props-out`.
4. Prepare Remotion audio assets into `--public-dir/audio` and mutate `--props-out`.
5. Write `--generated-dir/visual_manifest.md`.
6. Write `--generated-dir/visual_manifest.json`.
7. Inspect visual duration to `--generated-dir/visual_duration_report.md`, unless skipped or unavailable.
8. If enabled, prepare visual assets from `--visual-assets-dir` into `--public-dir/visuals` and mutate `--props-out`.
9. Inspect visual asset readiness from `--props-out`.
10. Run verified preflight for `--props-out` with `--public-dir`.

Visual duration policy: the step is attempted by default. If ffprobe is missing or unavailable when a supported video needs probing, the pipeline records a non-fatal `WARN` or `SKIP` step with a message naming ffprobe and continues. If `--skip-visual-duration` is passed, the step is `SKIP` without invoking visual duration reporting. Unexpected visual-duration failures that are not clear ffprobe availability issues should fail the pipeline so real data issues are not hidden.

Visual preparation policy: default on. When enabled, the pipeline runs existing `prepare_visual_assets_file`; this can copy/reuse/overwrite prepared public visual files according to existing semantics and rewrites `--props-out`. Missing local visuals remain non-fatal through existing behavior. Duplicate supported local files or unsupported prepared props paths remain hard errors. When disabled, the pipeline skips visual preparation, still writes visual manifests, still runs visual readiness inspection, and verified preflight may finish with warning-only missing optional visuals.

Console output contract: print one line per step with a stable status label `PASS`, `WARN`, `SKIP`, or `FAIL`, followed by a short message and important paths/counts. Finish with a compact summary:

    Pipeline check complete
    passed: <n>
    warnings: <n>
    skipped: <n>
    failed: <n>
    report: generated/pipeline_check_report.json
    Next: cd remotion && npm run typecheck
    Next: cd remotion && npm run render:smoke:local
    Next: cd remotion && npm run render:final:local

If a hard failure occurs, print completed step results and a clear `Error: ...` through the existing Typer error style, then exit non-zero.

The JSON report is required in Milestone 3 and defaults to `generated/pipeline_check_report.json`. Its shape is:

    {
      "schema_version": "0.1",
      "metadata": {
        "generated_by": "synccut pipeline-check",
        "scenes_json": "...",
        "audio_dir": "...",
        "alignment_dir": "...",
        "visual_assets_dir": "...",
        "timeline_out": "...",
        "props_out": "...",
        "public_dir": "...",
        "generated_dir": "...",
        "prepare_visual_assets": true,
        "skip_visual_duration": false,
        "overwrite_reports": true
      },
      "summary": {
        "total": 10,
        "pass": 0,
        "warn": 0,
        "skip": 0,
        "fail": 0
      },
      "steps": [
        {
          "name": "build_timeline",
          "status": "PASS",
          "message": "...",
          "paths": {"out": "timeline.json"},
          "counts": {"sections": 7, "scenes": 33},
          "warnings": []
        }
      ],
      "next_steps": [
        "cd remotion && npm run typecheck",
        "cd remotion && npm run render:smoke:local",
        "cd remotion && npm run render:final:local"
      ]
    }

Report JSON uses deterministic formatting: `indent=2`, `ensure_ascii=False`, and a trailing newline. The pipeline may overwrite `timeline_out`, `props_out`, `generated/visual_manifest.md`, `generated/visual_manifest.json`, `generated/visual_duration_report.md`, and `generated/pipeline_check_report.json`. It must not delete user media, delete render outputs, call broad cleanup commands, run npm, render, or delete files under `assets/visuals` or `remotion/out`.

Failure behavior: fail fast for timeline build, timeline validation errors, Remotion export, Remotion audio asset preparation, visual asset preparation when enabled, visual readiness inspection errors, preflight errors, and preflight file errors. Warning-only preflight status is allowed because missing optional visuals can be an intentional no-visual workflow. Continue with warning/skip for disabled visual preparation and missing/unavailable ffprobe. Do not swallow unexpected exceptions; convert expected validation problems to `SyncCutError` messages consistent with existing commands.

Milestone 3 tests:

- successful pipeline with a small fixture and local audio/alignment inputs
- exact step ordering and status labels
- `pipeline_check_report.json` metadata, steps, summary, next steps, and deterministic JSON formatting
- visual duration ffprobe unavailable becomes non-fatal warning/skip
- `--skip-visual-duration` skips duration without probe invocation
- `--no-prepare-visual-assets` skips visual preparation and allows warning-only visual preflight
- default visual preparation mutates props through existing behavior and records copied/reused/missing counts
- preflight error or file error returns a clear hard failure
- CLI command exists, prints per-step summary, final summary, report path, and next-step hints
- no provider, downloader, npm, render, ffmpeg, or broad cleanup call is made
- existing individual command tests remain unchanged

README runbook structure for Milestone 5:

- `From scenes.json to final video`
- Prerequisites
- Option A: `pipeline-check` workflow
- Option B: manual command-by-command workflow
- Optional: prepare narration and generate audio/alignment
- Optional: visual manifest and Pexels B-roll download
- Optional: visual duration report and ffprobe requirement
- Remotion typecheck and manual render commands
- Artifact policy and restoring generated props
- Troubleshooting for missing ffprobe, missing local visuals, provider API keys, Chrome sandbox, and warning-only preflight

### Milestone 3: implement `pipeline-check` command with tests

Implement the designed command in a new `synccut/pipeline.py` module and wire it into `synccut/cli.py`. Keep `synccut/cli.py` thin. The module should call existing internal functions such as `load_scenes`, `load_section_assets`, `build_timeline`, `validate_timeline`, `export_remotion_props_file`, `prepare_remotion_assets_file`, `write_visual_manifest_file`, `write_visual_duration_report_file`, `prepare_visual_assets_file`, `inspect_visual_asset_readiness_file`, and `inspect_preflight_file` as appropriate.

The implementation must not call `generate_audio` providers, `download-broll`, Pexels, Pixabay, ElevenLabs, ffmpeg, or Remotion render commands. It may use `inspect-visual-duration` logic if the design chooses to include duration reporting. It must preserve existing individual commands and not change their behavior.

Add focused tests in `tests/test_pipeline.py` and `tests/test_cli.py`. Tests should use small temporary fixtures. They should not require real media metadata, real ffprobe, Node, Remotion, external API keys, or network. If the pipeline supports visual duration checking, tests must inject or monkeypatch probe behavior so local ffprobe is not required.

Expected test coverage:

- successful no-visual or image-only pipeline check on a small fixture
- build/validate/export/audio-prep step ordering
- generated report paths under `generated/`
- props mutation only through export and preparation steps
- visual manifest creation
- optional visual duration skip or mocked success
- optional visual preparation behavior
- preflight result handling
- clear failure output when a required step fails
- CLI summary output
- no provider/download/render calls

Run:

    .venv/bin/python -m pytest

Acceptance for Milestone 3: tests pass, `pipeline-check` exists, it runs local deterministic pipeline checks, it does not render or call external APIs, and this plan records implementation evidence.

### Milestone 4: local validation on sample project

Validate the command on the sample workspace. Run:

    .venv/bin/python -m pytest

Then run:

    .venv/bin/synccut pipeline-check examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --visual-assets-dir assets/visuals

Expected behavior depends on the final design. At minimum, the command should build the timeline, validate it, export props, prepare audio assets, create visual manifests, handle visual duration reporting according to the ffprobe policy, inspect visual readiness, and run verified preflight. It must not call real APIs, download media, run Remotion render scripts, use ffmpeg, transcode media, or implement visual quality polish.

Run Remotion typecheck separately:

    cd remotion && npm run typecheck && cd ..

Do not render. If validation regenerates `remotion/props.json` and a sample props refresh is not explicitly approved, restore it:

    git restore remotion/props.json

Clean generated validation reports unless they are intentionally kept as ignored review artifacts. `timeline.json` may remain ignored/generated.

Acceptance for Milestone 4: pytest passes, `pipeline-check` produces the expected sample output or clear expected warnings, Remotion typecheck passes, generated outputs are ignored or cleaned, props are restored if needed, and this plan records the exact local behavior.

### Milestone 5: runbook/docs, cleanup, final review

Update README with a concise "From scenes.json to final video" runbook. The runbook should include the manual command-by-command workflow and the new `pipeline-check` workflow. It should explain prerequisites, prepared audio/alignment inputs, optional `prepare-narration` and `generate-audio`, optional `visual-manifest` and `download-broll`, optional `inspect-visual-duration` with ffprobe requirement, local visual preparation, preflight, Remotion typecheck, and manual render commands.

Keep the README user-facing. Do not document internal JSON schemas in detail. Do not imply that Python renders video. State that real ElevenLabs/Pexels use requires environment API keys and is not done by default in `pipeline-check`. State that Remotion render remains manual unless a future phase explicitly adds render automation.

Run final validation:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

Expected commit candidates after implementation are:

    README.md
    synccut/pipeline.py
    synccut/cli.py
    tests/test_pipeline.py
    tests/test_cli.py
    docs/plans/end-to-end-pipeline-command-and-runbook.md

Other files may appear only if the final Milestone 2 design explicitly requires them. Not expected as commit candidates are generated reports, `timeline.json`, `remotion/props.json` from local validation regeneration, `remotion/public/*`, `remotion/out/*`, local media, downloaded media, API key files, `.venv/`, `remotion/node_modules/`, or caches.

Recommended commit message:

    Add end-to-end pipeline check and runbook

After Phase 34, ask the user before starting the postponed Remotion visual quality polish phase.

## Concrete Steps

Milestone 1 audit commands:

    sed -n '1,520p' synccut/cli.py
    sed -n '1,260p' synccut/remotion_exporter.py
    sed -n '1,260p' synccut/remotion_assets.py
    sed -n '1,260p' synccut/visual_manifest.py
    sed -n '1,260p' synccut/visual_assets.py
    sed -n '1,260p' synccut/preflight.py
    sed -n '1,260p' synccut/visual_duration.py
    sed -n '1,180p' remotion/package.json
    git status --short --ignored

Milestone 3 implementation validation:

    .venv/bin/python -m pytest

Milestone 4 sample validation:

    .venv/bin/python -m pytest
    .venv/bin/synccut pipeline-check examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --visual-assets-dir assets/visuals
    cd remotion && npm run typecheck && cd ..

Milestone 5 final validation:

    .venv/bin/python -m pytest
    cd remotion && npm run typecheck && cd ..
    git status --short --ignored

## Validation and Acceptance

The phase is accepted when:

- `synccut pipeline-check` exists and is documented.
- It runs a useful local deterministic readiness pipeline from `scenes.json` through verified preflight.
- It keeps existing individual commands available and unchanged.
- It does not render by default.
- It does not download B-roll by default.
- It does not call real ElevenLabs, Pexels, or Pixabay by default.
- It does not use ffmpeg or transform media.
- It does not implement Remotion visual polish.
- It reports which steps passed, warned, skipped, or failed.
- It handles missing ffprobe according to the design chosen in Milestone 2.
- Tests cover the orchestration behavior without requiring real ffprobe, Node, network, external APIs, or real media metadata.
- `.venv/bin/python -m pytest` passes.
- `cd remotion && npm run typecheck && cd ..` passes.
- README contains a clear runbook from `scenes.json` to final video.
- Generated/local artifacts remain ignored or are cleaned.

## Idempotence and Recovery

The pipeline command should be safe to rerun. It may overwrite deterministic generated outputs such as `timeline.json`, `remotion/props.json`, `generated/visual_manifest.md`, `generated/visual_manifest.json`, and any designed pipeline report. It must not delete or overwrite user media outside existing preparation behavior. If `prepare-visual-assets` is part of the command, it should use the existing preparation semantics and report copied, reused, overwritten, and missing counts.

If validation changes `remotion/props.json` only as a local sample regeneration artifact, restore it with:

    git restore remotion/props.json

If a generated report blocks because it already exists and differs, rerun with the designed overwrite option or remove only that generated report. Do not use broad cleanup commands. Do not restore README, source, or test files unless the change is accidental.

Missing ffprobe should not corrupt output. If visual duration reporting cannot run because ffprobe is unavailable, the command should either skip it by option or fail clearly with a message that names ffprobe and the skip/configuration option. Rendering remains manual from `remotion/`.

## Artifacts and Notes

Milestone 1 command audit:

- `prepare-narration`: reads `scenes.json`; writes a narration package under the requested `--out-dir`; no API key, network, ffprobe, Node, media generation, or props mutation. It is optional upstream setup for generated audio/alignment, not part of the prepared-input default path.
- `generate-audio`: reads a narration manifest; writes audio files, alignment JSON files, and generation metadata; real ElevenLabs runs require `ELEVENLABS_API_KEY` and network. It is excluded from `pipeline-check` defaults, though the runbook should document it as an optional explicit provider workflow.
- `build-timeline`: reads `scenes.json`, `--audio-dir`, and `--alignment-dir`; writes `timeline.json` or the requested output; no API key, ffprobe, Node, or props mutation. It is safe for the default pipeline.
- `validate-timeline`: reads `timeline.json`; writes nothing; no API key, ffprobe, Node, or media side effects. It is safe for the default pipeline.
- `export-remotion`: reads `timeline.json`; writes `remotion/props.json` or the requested props path; no API key, ffprobe, Node, or media copy. It is safe as an explicit pipeline step that mutates generated props state.
- `prepare-remotion-assets`: reads and rewrites props; copies or reuses audio under `remotion/public/audio/`; no API key, ffprobe, or Node. It is safe as an explicit pipeline step and must be reported as props/public mutation.
- `visual-manifest`: reads props and optionally inspects direct local filenames under `assets/visuals`; writes generated Markdown or JSON reports; no props mutation, media copy, API key, ffprobe, or Node. It is safe for the default pipeline.
- `download-broll`: reads Phase 31 visual manifest JSON; dry-run writes nothing and needs no key; real Pexels runs require `PEXELS_API_KEY`, network, media download, local asset writes, and metadata writes. It is excluded from defaults.
- `inspect-visual-duration`: reads props and local `assets/visuals` filenames; writes generated Markdown or JSON reports; uses ffprobe only when one supported video file needs metadata; does not mutate props or media. It is useful but should be optional or skippable when ffprobe is unavailable.
- `prepare-visual-assets`: reads and rewrites props; copies or reuses one supported local visual file per target scene into `remotion/public/visuals`; no API key, network, ffprobe, or Node. It is local and deterministic but mutates props and copies local media, so Milestone 2 must decide default versus opt-in.
- `inspect-visual-assets`: reads props readiness; writes nothing; no API key, ffprobe, Node, media copy, or props mutation. It is safe for the default pipeline.
- `preflight`: reads props; with `--verify-files --public-dir` checks public files without mutation; no API key, ffprobe, Node, or media copy. It is safe for the default pipeline after public assets are prepared.

Milestone 1 Remotion script audit:

- `npm run typecheck`: runs TypeScript typecheck with Node; no render output; useful as manual or optional validation, not a Python default.
- `npm run still:local`: renders a still image to `remotion/out/preview.png`; Node/Chrome/Remotion-dependent render step; manual only.
- `npm run render:smoke:local`: renders a smoke MP4 under `remotion/out/`; Node/Chrome/Remotion-dependent render step; manual only.
- `npm run render:segment:local`: renders a segment MP4 under `remotion/out/`; Node/Chrome/Remotion-dependent render step; manual only.
- `npm run render:final:local`: renders full `remotion/out/final.mp4`; Node/Chrome/Remotion-dependent, slow, artifact-heavy, and subject to Chrome sandbox behavior; manual only.

Current working tree note after Milestone 1 audit: the only nonignored Phase 34 change is `docs/plans/end-to-end-pipeline-command-and-runbook.md`. Ignored generated/local paths are still present and must not be conflated with commit candidates.

Ignored local paths at plan creation include:

    .pytest_cache/
    .venv/
    assets/
    examples/
    generated/
    remotion/node_modules/
    remotion/out/
    remotion/public/
    synccut/__pycache__/
    tests/__pycache__/
    timeline.json

This plan intentionally postpones Remotion visual quality polish. That later work may involve visual composition, motion, titles, or rendering aesthetics, but none of those changes belong in Phase 34.

## Interfaces and Dependencies

The new orchestration module should be `synccut/pipeline.py`. It should define dataclasses or simple typed structures for step results and the final pipeline result. Suggested names are:

    PipelineStepResult
    PipelineCheckResult
    run_pipeline_check(...)

The Milestone 2 implementation target is:

    def run_pipeline_check(
        scenes_json: Path,
        *,
        audio_dir: Path,
        alignment_dir: Path,
        visual_assets_dir: Path = Path("assets/visuals"),
        timeline_out: Path = Path("timeline.json"),
        props_out: Path = Path("remotion/props.json"),
        public_dir: Path = Path("remotion/public"),
        generated_dir: Path = Path("generated"),
        skip_visual_duration: bool = False,
        overwrite_reports: bool = True,
        prepare_visual_assets: bool = True,
        pipeline_report_out: Path | None = None,
    ) -> PipelineCheckResult:
        ...

If `pipeline_report_out` is `None`, the implementation writes `generated_dir / "pipeline_check_report.json"`. Status values should be uppercase strings: `PASS`, `WARN`, `SKIP`, and `FAIL`. The final `PipelineCheckResult` should contain ordered step results, the report path, summary counts, and the manual Remotion next-step commands.

The CLI command should be added in `synccut/cli.py` as `pipeline-check`. It should catch `SyncCutError` and print `Error: ...` like existing commands. It should print a concise step summary and a final next-step hint that points to:

    cd remotion
    npm run typecheck
    npm run render:smoke:local
    npm run render:final:local

Do not add Python dependencies. Do not add Node dependencies. Do not call npm from Python unless Milestone 2 explicitly chooses an optional `--typecheck` flag and tests cover the no-Node default path.
