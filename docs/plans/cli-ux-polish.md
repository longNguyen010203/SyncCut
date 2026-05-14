# CLI UX polish

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit, design, implement, and validate small SyncCut CLI usability improvements from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut v0.1.0 is released and has onboarding docs plus CI. The CLI already works, but a new user can still benefit from clearer command output, more scan-friendly validation and preflight summaries, and better help text that explains what to do next. This phase makes the current MVP commands easier to run and understand without adding a major feature or changing schemas.

After this plan is complete, a user should be able to run the existing commands and more quickly answer: did the command succeed, were there warnings or errors, what files were written, and what is the next safe command. The observable result is improved CLI text output and help messages, covered by focused tests, with existing command behavior preserved.

## Progress

- [x] (2026-05-14T13:42:00+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, root `README.md`, Phase 26 onboarding plan, Phase 27 developer workflow/CI plan, `pyproject.toml`, `synccut/cli.py`, `synccut/timeline_builder.py`, `synccut/timeline_validator.py`, `synccut/remotion_exporter.py`, `synccut/remotion_assets.py`, `synccut/visual_assets.py`, `synccut/preflight.py`, `tests/test_cli.py`, and current `git status --short --ignored`.
- [x] (2026-05-14T13:42:00+07:00) Confirmed the current CLI commands and output modules to audit in Milestone 1.
- [x] (2026-05-14T13:42:00+07:00) Created this Phase 28 ExecPlan.
- [x] (2026-05-14T13:58:00+07:00) Milestone 1: Audited current CLI help and representative safe no-visual sample command output without editing source.
- [x] (2026-05-14T14:15:00+07:00) Milestone 2: Chose a small, backward-compatible output polish design focused on human-readable summaries, next-step hints, optional visual clarity, and help text.
- [x] (2026-05-14T14:35:00+07:00) Milestone 3: Implemented focused CLI output/help polish and tests.
- [x] (2026-05-14T14:50:00+07:00) Milestone 4: Validated the polished CLI output on the representative no-visual sample workflow, Python tests, and Remotion typecheck.
- [x] (2026-05-14T15:05:00+07:00) Milestone 5: Completed docs decision, final validation, generated props cleanup, artifact review, and commit recommendation.

## Surprises & Discoveries

- Observation: The asset preparation modules named in the phase prompt are not present under those exact names.
  Evidence: `sed -n '1,260p' synccut/asset_preparer.py` and `sed -n '1,260p' synccut/visual_asset_preparer.py` failed with "No such file or directory". The current modules are `synccut/remotion_assets.py` for audio/public asset preparation and `synccut/visual_assets.py` for local AI_VIDEO/B_ROLL visual asset preparation and inspection.
- Observation: The CLI output is currently mostly stable key-value text.
  Evidence: `synccut/cli.py` prints labels such as `scenes:`, `sections:`, `warnings:`, `errors:`, `audio_assets:`, `visual_missing:`, and `public_dir:`. This is easy to test, but some commands do not yet provide next-step hints.
- Observation: Preflight already has structured status fields and JSON output.
  Evidence: `synccut/preflight.py` defines `PreflightSummary`, `format_preflight`, and `preflight_to_dict`, and tests assert fields such as `status`, `warnings`, `errors`, `verify_files`, `public_dir`, and `file_errors`.
- Observation: Existing CLI tests assert many output strings directly.
  Evidence: `tests/test_cli.py` checks output for `OK`, `Exported`, `Prepared Remotion assets`, `warnings:`, `visual_missing:`, `status: warning`, and preflight error text. Any output polish must update tests intentionally and avoid unnecessary churn.
- Observation: Current tracked working tree is clean before this plan is created.
  Evidence: `git status --short --ignored` showed only ignored generated/local paths: `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/`, and `timeline.json`.
- Observation: Root help lists all MVP commands clearly.
  Evidence: `.venv/bin/synccut --help` showed `build-timeline`, `validate-timeline`, `inspect`, `export-remotion`, `prepare-remotion-assets`, `prepare-visual-assets`, `inspect-visual-assets`, and `preflight` with short command descriptions.
- Observation: Command help is readable but sparse around side effects and option relationships.
  Evidence: `prepare-remotion-assets --help` says "Copy Remotion assets into the public directory and update props JSON" but does not explicitly say it prepares audio only. `preflight --help` lists `--verify-files` and `--public-dir`, but does not explain that `--public-dir` is required with `--verify-files` and invalid without it. `prepare-visual-assets --help` says "Directory containing local visual assets" but does not mention `assets/visuals/<scene_id>.<ext>` or one supported file per scene.
- Observation: `build-timeline` succeeds silently.
  Evidence: Running `.venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json` exited `0` with no output, even though it wrote `timeline.json`. This is the clearest success-message gap.
- Observation: Validation and export summaries are concise and stable.
  Evidence: `validate-timeline timeline.json` printed `OK timeline.json`, `scenes: 33`, `sections: 7`, `duration_sec: 752.79`, and `warnings: 0`. `export-remotion timeline.json --out remotion/props.json` printed `Exported remotion/props.json`, `scenes: 33`, `sections: 7`, `fps: 30`, `duration_frames: 22584`, and `warnings: 0`.
- Observation: Audio preparation summary is useful but could be clearer about the next step.
  Evidence: `prepare-remotion-assets remotion/props.json --out-dir remotion/public` printed copied/reused/overwritten counts, `audio_assets: 7`, and `public_dir: remotion/public`, but no hint to run visual inspection or verified preflight next.
- Observation: Clean no-visual visual inspection is correct but can feel alarming without context.
  Evidence: `inspect-visual-assets remotion/props.json` printed `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, followed by 17 per-scene `missing -` rows. It does not say these missing AI_VIDEO/B_ROLL assets are optional in no-visual validation.
- Observation: Verified preflight is technically clear but noisy for the common no-visual state.
  Evidence: `preflight remotion/props.json --verify-files --public-dir remotion/public` printed `status: warning`, `errors: 0`, `file_errors: 0`, and 17 repeated `warning visual_missing ... placeholder will render` lines. This is accurate, but a short summary note would help users understand the warning-only state.
- Observation: JSON/human output boundary should remain unchanged.
  Evidence: `inspect-visual-assets` and `preflight` both provide `--json` for machine-readable output; the audit found enough human-output polish opportunities without changing JSON structures.
- Observation: Milestone 1 sample commands regenerated tracked props.
  Evidence: The audit ran `export-remotion timeline.json --out remotion/props.json` and `prepare-remotion-assets remotion/props.json --out-dir remotion/public`. Per user instruction, `remotion/props.json` is not restored in Milestone 1 and should be handled in later cleanup if it appears as a commit candidate.
- Observation: The best UX improvement is additive text, not label replacement.
  Evidence: Tests assert existing labels such as `OK`, `Exported`, `warnings:`, `errors:`, and `status:`. Keeping those labels and adding concise new lines avoids unnecessary test churn and preserves familiar output for existing users.
- Observation: `build-timeline` can report useful counts without changing data structures.
  Evidence: The command already receives the built timeline before writing it, and the timeline metadata contains total sections, total scenes, and total duration.
- Observation: Optional visual clarity should be a summary note while preserving detailed per-scene rows.
  Evidence: `inspect-visual-assets` and `preflight` already identify exact missing scene ids. The confusing part is context, not the rows themselves.
- Observation: Milestone 3 changed only the planned output/help surface and focused tests.
  Evidence: Source edits were limited to `synccut/cli.py`, `synccut/visual_assets.py`, and `synccut/preflight.py`. Test edits were limited to `tests/test_cli.py`, `tests/test_visual_assets.py`, and `tests/test_preflight.py`.
- Observation: Typer help output wraps long help strings in tests.
  Evidence: The first pytest run failed because the assertion expected the exact phrase `one supported file per target scene`, while Typer wrapped the help text across columns. The test was tightened to assert the stable substring `supported file per target scene`.
- Observation: The implemented JSON behavior remains unchanged.
  Evidence: Existing JSON tests for `inspect-visual-assets --json` and `preflight --json` continued to pass without expectation changes.
- Observation: Sample command validation confirmed the new `Next:` hints in real CLI output.
  Evidence: `build-timeline` printed `Next: synccut validate-timeline timeline.json`; `validate-timeline` printed `Next: synccut export-remotion timeline.json --out remotion/props.json`; `export-remotion` printed `Next: synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public`; and `prepare-remotion-assets` printed `Next: synccut preflight remotion/props.json --verify-files --public-dir remotion/public`.
- Observation: Sample no-visual validation remains warning-only and clearer.
  Evidence: `inspect-visual-assets remotion/props.json` reported `target_scenes: 17`, `prepared: 0`, `missing: 17`, `unsupported: 0`, and included the optional placeholder note. Verified preflight reported `status: warning`, `errors: 0`, `file_errors: 0`, `visual_missing: 17`, and included the warning-only placeholder note.
- Observation: No validation bug was discovered in Milestone 4.
  Evidence: `.venv/bin/python -m pytest` passed with 214 tests, the representative sample workflow exited successfully through verified preflight, and `npm run typecheck` passed in `remotion/`.
- Observation: README remains accurate after the CLI output/help polish.
  Evidence: The root README already documents the no-visual quick start, warning-only optional visual placeholders, command help, local visual workflow, and preflight behavior. The new CLI hints and notes clarify runtime output without changing the documented workflow, so no README edit was needed.
- Observation: Final validation passed after Milestone 3 changes.
  Evidence: `.venv/bin/python -m pytest` passed with 214 tests, and `cd remotion && npm run typecheck` passed.
- Observation: Restoring generated props required elevated filesystem access in this sandbox.
  Evidence: The first `git restore remotion/props.json` failed because Git could not create `.git/index.lock` on a read-only filesystem path. Retrying the same explicit cleanup command with elevated permission succeeded.
- Observation: Artifact review found only expected non-ignored commit candidates.
  Evidence: `git status --short --ignored` showed modified `synccut/cli.py`, `synccut/preflight.py`, `synccut/visual_assets.py`, `tests/test_cli.py`, `tests/test_preflight.py`, `tests/test_visual_assets.py`, and untracked `docs/plans/cli-ux-polish.md`. Ignored generated/local paths included `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, `__pycache__/`, and `timeline.json`.

## Decision Log

- Decision: Keep Phase 28 limited to low-risk output/help polish.
  Rationale: The user explicitly requested no behavior-breaking changes, no major feature, and no schema change unless separately justified and approved. The safest valuable work is wording, summary consistency, and help text.
  Date/Author: 2026-05-14 / Codex
- Decision: Treat JSON output as a compatibility surface and avoid changing JSON keys unless explicitly approved later.
  Rationale: `preflight --json` and `inspect-visual-assets --json` are machine-readable outputs. Changing their structure would be more than small CLI UX polish.
  Date/Author: 2026-05-14 / Codex
- Decision: Prefer improving human-readable output and Typer help text over changing generated timeline, props, or schema data.
  Rationale: The goal is usability, not data model evolution. The existing data outputs are already validated and released.
  Date/Author: 2026-05-14 / Codex
- Decision: Do not start Phase 29 or major feature work from this plan.
  Rationale: The user set the roadmap order through Phase 28 and explicitly said not to start Phase 29 or any major feature upgrade without asking first.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 2 should design around human-readable success messages, next-step hints, and optional-visual warning clarity.
  Rationale: The audit found the highest-value UX gaps in silent `build-timeline`, sparse side-effect help text, no next-step hints after successful pipeline commands, and noisy missing-visual warnings. These can be improved without schema, option, or command behavior changes.
  Date/Author: 2026-05-14 / Codex
- Decision: Exclude JSON output changes from the Milestone 2 design.
  Rationale: JSON output is already available and stable for automation. Human-readable output can be improved while keeping machine-readable contracts unchanged.
  Date/Author: 2026-05-14 / Codex
- Decision: Exclude broad formatter rewrites and suppression of warning details.
  Rationale: Existing tests assert stable text, and detailed warning rows are useful for diagnosing exact missing scenes. The design should add context or summaries rather than remove information.
  Date/Author: 2026-05-14 / Codex
- Decision: Add a `build-timeline` success summary.
  Rationale: This is the only audited command that succeeds silently. The summary will print the output path, `sections`, `scenes`, `duration_sec`, `warnings`, and a next-step hint: `Next: synccut validate-timeline <out>`.
  Date/Author: 2026-05-14 / Codex
- Decision: Add short `Next:` hints only to successful human-readable pipeline commands.
  Rationale: Hints help new users move through the current MVP without adding commands or options. Planned hints are after `build-timeline`, `validate-timeline` when it exits successfully, `export-remotion`, and `prepare-remotion-assets`. They will not be emitted for JSON output.
  Date/Author: 2026-05-14 / Codex
- Decision: Add optional-visual context to human-readable visual inspection and preflight output.
  Rationale: The no-visual sample state is warning-only but can look alarming. The planned note says missing AI_VIDEO/B_ROLL visuals are optional and Remotion will render placeholders unless visual assets are prepared. Existing warning rows and JSON keys remain unchanged.
  Date/Author: 2026-05-14 / Codex
- Decision: Improve Typer help text for audio preparation, visual asset naming, and verified preflight paths.
  Rationale: The audit found help text gaps around `prepare-remotion-assets`, `prepare-visual-assets`, `--verify-files`, and `--public-dir`. These are wording-only improvements and do not change options.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 3 expected source files are `synccut/cli.py`, `synccut/visual_assets.py`, and `synccut/preflight.py`.
  Rationale: `synccut/cli.py` owns Typer help text and command success output. `synccut/visual_assets.py` owns human visual readiness formatting. `synccut/preflight.py` owns human preflight formatting.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 3 expected test files are `tests/test_cli.py`, `tests/test_visual_assets.py`, and `tests/test_preflight.py`.
  Rationale: CLI tests should cover new build output, next-step hints, and help text. Formatter tests should cover optional visual notes in visual readiness and preflight output.
  Date/Author: 2026-05-14 / Codex
- Decision: JSON output remains unchanged.
  Rationale: `inspect-visual-assets --json` and `preflight --json` are machine-readable interfaces. Phase 28 will not add JSON fields, remove JSON fields, rename JSON fields, or alter generated timeline/props structures.
  Date/Author: 2026-05-14 / Codex

## Outcomes & Retrospective

This plan was created after reviewing the current CLI, output formatters, tests, onboarding docs, CI plan, and repository status. No source code, tests, README, schemas, command behavior, render scripts, media, generated artifacts, commits, tags, pushes, or later-phase work were changed while creating the plan.

The intended outcome is a small set of CLI output and help text improvements. The work should make current commands easier to scan while keeping existing command names, options, exit codes, JSON formats, generated `timeline.json`, generated `remotion/props.json`, and Remotion behavior stable.

Milestone 1 is complete. The help audit found that all commands are present and readable, but some help text can better explain side effects and relationships: `prepare-remotion-assets` is audio preparation, `prepare-visual-assets` expects local files named by scene id, and `preflight --public-dir` is only valid with `--verify-files`.

The sample output audit found several focused polish candidates. `build-timeline` is silent on success and should report the output path and basic counts. `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` already have concise summaries, but could benefit from short next-step hints. `inspect-visual-assets` and `preflight` correctly report the no-visual state, but the common `missing: 17` and 17 `visual_missing` warnings need a short explanation that missing AI_VIDEO/B_ROLL assets are optional in no-visual validation and render as placeholders.

Candidate polish list for Milestone 2:

1. Add a `build-timeline` success summary with path, scenes, sections, duration, and `warnings: 0`.
2. Add concise `Next:` hints after successful build/export/audio-prep commands.
3. Improve help text for `prepare-remotion-assets`, `prepare-visual-assets`, `--verify-files`, and `--public-dir`.
4. Add a human-readable note to `inspect-visual-assets` and/or preflight when missing visuals are warning-only optional placeholders.
5. Preserve JSON output, exit codes, command names, option names, generated data, and detailed warning rows.

The next step is Milestone 2: choose a small final subset of those polish candidates and define exact source/test edits before implementation.

Milestone 2 is complete. The final implementation design is intentionally small and additive:

1. `build-timeline` should print a concise success summary:

       Built timeline <out>
       sections: <n>
       scenes: <n>
       duration_sec: <seconds>
       warnings: <n>
       Next: synccut validate-timeline <out>

   This uses data already present in the generated timeline and does not change the written JSON.

2. `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` should add one short `Next:` hint after successful human-readable output. The intended hints are:

       Next: synccut export-remotion <timeline> --out remotion/props.json
       Next: synccut prepare-remotion-assets <props> --out-dir remotion/public
       Next: synccut preflight <props> --verify-files --public-dir <out-dir>

   These hints are plain text only and must not appear in JSON output.

3. `inspect-visual-assets` should add a human-readable note when `missing` is greater than zero:

       Note: Missing AI_VIDEO/B_ROLL visuals are optional; Remotion will render placeholders unless visual assets are prepared.

   Existing summary labels and per-scene rows should remain.

4. `preflight` should add the same optional-visual context when the summary has missing visual warnings but `errors: 0` and `file_errors: 0`. Existing warning rows should remain, because they identify exact missing scenes.

5. Typer help text should be clarified without changing command names or options:

   - `prepare-remotion-assets` is audio/public asset preparation.
   - `prepare-visual-assets` expects local files named `assets/visuals/<scene_id>.<ext>` with one supported file per target scene.
   - `--verify-files` verifies prepared public audio/visual files.
   - `--public-dir` is the Remotion public directory used with `--verify-files`.

The planned tests are focused. `tests/test_cli.py` should assert the new build success summary, selected next-step hints, and help text snippets. `tests/test_visual_assets.py` should assert the optional visual note in human visual readiness output. `tests/test_preflight.py` should assert the optional visual note in human preflight output while preserving detailed warning lines. Existing JSON tests should continue to pass without expectation changes.

The next step is Milestone 3: implement only these chosen source/test changes.

Milestone 3 is complete. Implementation summary:

- `synccut/cli.py` now prints a success summary from `build-timeline` after writing the timeline, including output path, sections, scenes, duration, warning count, and `Next: synccut validate-timeline <out>`.
- `synccut/cli.py` now prints `Next:` hints after successful `validate-timeline`, `export-remotion`, and `prepare-remotion-assets` human output.
- `synccut/cli.py` help text now clarifies that `prepare-remotion-assets` prepares audio assets, `prepare-visual-assets` expects `assets/visuals/<scene_id>.<ext>` style local files with one supported file per target scene, and `preflight --verify-files` requires `--public-dir`.
- `synccut/visual_assets.py` now adds a human-readable optional-placeholder note when visual readiness has missing AI_VIDEO/B_ROLL assets.
- `synccut/preflight.py` now adds a human-readable warning-only optional-placeholder note when missing visuals are present and there are no errors or file errors.
- `tests/test_cli.py` now covers the new build summary, next-step hints, and help text snippets.
- `tests/test_visual_assets.py` now covers the optional visual readiness note.
- `tests/test_preflight.py` now covers the optional preflight note while preserving detailed warning lines.

Validation result: `.venv/bin/python -m pytest` passed with 214 tests. One initial test assertion was adjusted because Typer wraps help text; the product help text itself stayed as designed. No README, schema, command, option, JSON key, timeline/props structure, media, render script, tag, push, or Phase 29 work was changed. `remotion/props.json` remains regenerated from earlier audit work and is intentionally not restored in Milestone 3 per scope.

The next step is Milestone 4: run the representative sample command validation and Remotion typecheck without rendering.

Milestone 4 is complete. Validation summary:

- `.venv/bin/python -m pytest` passed with 214 tests.
- `build-timeline` regenerated `timeline.json` and printed the new success summary: 7 sections, 33 scenes, `duration_sec: 752.79`, `warnings: 0`, and the validate next-step hint.
- `validate-timeline timeline.json` passed with `warnings: 0` and printed the export next-step hint.
- `export-remotion timeline.json --out remotion/props.json` passed with `warnings: 0`, 30 fps, 22584 frames, and printed the audio preparation next-step hint.
- `prepare-remotion-assets remotion/props.json --out-dir remotion/public` passed with 7 reused audio assets and printed the verified preflight next-step hint.
- `inspect-visual-assets remotion/props.json` reported 17 target scenes, 0 prepared, 17 missing, 0 unsupported, and printed the optional visual placeholder note.
- `preflight remotion/props.json --verify-files --public-dir remotion/public` reported `status: warning`, 17 visual-missing warnings, `errors: 0`, `file_errors: 0`, and printed the warning-only optional visual placeholder note.
- `cd remotion && npm run typecheck` passed.

The output is clearer and not meaningfully noisier: the new notes add one short explanatory paragraph before the existing detailed warning rows. No source or test changes were needed during Milestone 4. `remotion/props.json` remains generated/modified from sample validation and should be restored in Milestone 5 unless the user explicitly approves refreshing sample props.

The next step is Milestone 5: decide whether docs need a small update, run final validation, clean generated props, review artifacts, and recommend a commit message.

Milestone 5 is complete. Final summary:

- Docs decision: README was reviewed and left unchanged because it already remains accurate. It explains the no-visual quick start, warning-only optional visual placeholders, command help, local visual assets, preflight, artifact policy, and development validation.
- Final validation: `.venv/bin/python -m pytest` passed with 214 tests, and `cd remotion && npm run typecheck` passed.
- Cleanup: `remotion/props.json` was restored because the sample props refresh was not approved. The first restore attempt was blocked by sandbox filesystem permissions for `.git/index.lock`; the elevated retry succeeded.
- Artifact review: generated/local paths remain ignored, including `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, and caches.
- Acceptance criteria: CLI output/help is clearer for current MVP commands, changes are small and backward-compatible, JSON output keys and structures are unchanged, schemas and command options are unchanged, tests pass, Remotion typecheck passes, and generated artifacts are not commit candidates.

Final commit candidates:

- `synccut/cli.py`
- `synccut/visual_assets.py`
- `synccut/preflight.py`
- `tests/test_cli.py`
- `tests/test_visual_assets.py`
- `tests/test_preflight.py`
- `docs/plans/cli-ux-polish.md`

Recommended commit message:

    Polish CLI output and help text

Phase 28 is complete. The next step is not to start Phase 29 automatically; ask the user before beginning Phase 29 or any major upgrade direction.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is installed locally as `.venv/bin/synccut` from `pyproject.toml`, which declares project name `synccut`, Python `>=3.11`, dependency `typer>=0.12`, development extra `pytest>=8`, and console script `synccut = "synccut.cli:app"`.

The CLI entry point is `synccut/cli.py`. It uses Typer, a Python CLI framework, to define the commands. Typer help text comes from command docstrings and `typer.Argument` or `typer.Option` help strings. The current command set is:

- `build-timeline`, which builds `timeline.json` from `scenes.json`, audio references, and alignment timestamps.
- `validate-timeline`, which validates timeline structure and timing.
- `inspect`, which prints a readable timeline overview.
- `export-remotion`, which exports Remotion props to `remotion/props.json`.
- `prepare-remotion-assets`, which copies audio into `remotion/public/audio` and annotates props.
- `prepare-visual-assets`, which copies local AI_VIDEO/B_ROLL visual files into `remotion/public/visuals` and annotates props.
- `inspect-visual-assets`, which reports whether AI_VIDEO/B_ROLL target scenes have prepared public visual paths.
- `preflight`, which reports render readiness from Remotion props and can verify public files with `--verify-files --public-dir remotion/public`.

The main implementation modules are `synccut/timeline_builder.py`, `synccut/timeline_validator.py`, `synccut/remotion_exporter.py`, `synccut/remotion_assets.py`, `synccut/visual_assets.py`, and `synccut/preflight.py`. `synccut/remotion_assets.py` is the current audio asset preparation module. `synccut/visual_assets.py` is the current visual asset preparation and inspection module. There are no files named `synccut/asset_preparer.py` or `synccut/visual_asset_preparer.py` in this working tree.

Tests live under `tests/`. `tests/test_cli.py` uses Typer's `CliRunner` to invoke commands and assert human-readable output and error behavior. `tests/test_preflight.py` and `tests/test_visual_assets.py` cover formatter and summary behavior. Because output text is directly asserted, any text polish must be accompanied by focused test updates.

Generated and local-only paths must stay out of commits. `.gitignore` ignores `examples`, `assets/visuals/`, `.venv`, `remotion/node_modules`, `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`. `remotion/props.json` may change during validation, but if it changes only because of local regeneration, it should be restored before final review unless the user explicitly approves a sample props refresh.

## Plan of Work

Milestone 1 audits the current CLI UX without changing source. Run the root help and every command help. Then run a safe representative no-visual sample workflow through preflight: build timeline, validate timeline, export Remotion props, prepare audio assets, inspect visual assets, and preflight with verified public files. Do not run `prepare-visual-assets` unless a later milestone specifically needs it, and do not render. Record unclear output, inconsistent labels, missing next-step hints, noisy sections, and confusion around missing optional visuals.

Milestone 2 turns the audit into a small implementation design. Choose only a few changes that improve scanability without changing core behavior. Acceptable changes include consistent status labels, clearer warning/error summaries, short next-step hints after successful commands, clearer explanation that missing optional visuals are warning-only, and improved Typer help text. Explicitly reject changes that add commands, new schemas, render automation, DOCX parsing, media probing, or breaking option changes.

Milestone 3 implements the chosen polish. Edit only relevant output/help modules and tests. Likely files are `synccut/cli.py`, `synccut/preflight.py`, `synccut/visual_assets.py`, and `tests/test_cli.py` or formatter tests. Keep the implementation small. Do not change generated timeline or props structure. If adding next-step hints, make them human-readable only and avoid JSON output. If improving preflight summaries, preserve `preflight_to_dict` keys unless the user separately approves a JSON contract change.

Milestone 4 validates the updated command behavior on the sample no-visual workflow. Run Python tests first, then regenerate the sample `timeline.json`, validate it, export `remotion/props.json`, prepare audio assets, inspect visual assets, and run verified preflight. Then run Remotion typecheck. Do not run `prepare-visual-assets` unless needed for the selected UX change, and do not render.

Milestone 5 decides whether docs need a small update and performs final cleanup. Update `README.md` only if the CLI output/help changes alter user-facing guidance. Run final pytest and Remotion typecheck. If `remotion/props.json` changed only because of validation regeneration, restore it with `git restore remotion/props.json`. Review `git status --short --ignored` and confirm generated/local artifacts remain ignored. Recommend a commit message.

## Concrete Steps

Run commands from the repository root unless a command explicitly changes directory.

For Milestone 1, inspect command help:

    .venv/bin/synccut --help
    .venv/bin/synccut build-timeline --help
    .venv/bin/synccut validate-timeline --help
    .venv/bin/synccut inspect --help
    .venv/bin/synccut export-remotion --help
    .venv/bin/synccut prepare-remotion-assets --help
    .venv/bin/synccut prepare-visual-assets --help
    .venv/bin/synccut inspect-visual-assets --help
    .venv/bin/synccut preflight --help

Then run representative safe sample commands:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public

Expected current sample behavior after Phase 23 is that `validate-timeline` and `export-remotion` report zero warnings. In clean no-visual state, `inspect-visual-assets` should report 17 target scenes, 0 prepared, 17 missing, and 0 unsupported. Verified preflight should be warning-only because optional visual assets are missing, with `errors: 0` and `file_errors: 0`.

For Milestone 2, update this plan with the chosen small changes before editing source. The design should say exactly which files will be edited and what tests will be updated. Examples of acceptable design choices are:

    Add a one-line next-step hint after export-remotion:
    Next: run prepare-remotion-assets remotion/props.json --out-dir remotion/public

    Add a one-line note to inspect-visual-assets when missing visuals are present:
    Missing AI_VIDEO/B_ROLL visuals are optional; preflight will warn and Remotion will render placeholders.

    Add clearer Typer help text for --verify-files and --public-dir.

Do not choose all possible polish ideas. Keep the selected set small enough to review easily.

For Milestone 3, implement the selected changes and update tests. Run:

    .venv/bin/python -m pytest

If tests fail because expected output changed, update only the focused assertions that correspond to the planned output changes. Do not broaden tests to ignore meaningful output regressions.

For Milestone 4, run:

    .venv/bin/python -m pytest
    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    cd remotion
    npm run typecheck
    cd ..

Do not run render commands.

For Milestone 5, run final validation and review:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck
    cd ..
    git status --short --ignored

If `remotion/props.json` is a commit candidate only because of sample regeneration, restore it with:

    git restore remotion/props.json

Then rerun:

    git status --short --ignored

Recommended commit message, unless the actual implementation suggests a better one:

    Polish CLI output and help text

## Validation and Acceptance

This phase is accepted when the current CLI commands are easier to understand while remaining backward-compatible. Human-readable output should make status, warning counts, error counts, generated paths, and next steps easier to scan. Existing command names, options, exit-code semantics, JSON outputs, timeline schema, Remotion props schema, and render workflows must remain stable unless the user explicitly approves a change.

Python validation must pass with:

    .venv/bin/python -m pytest

Remotion validation must pass with:

    cd remotion
    npm run typecheck
    cd ..

The sample no-visual workflow must still reach verified preflight with `errors: 0` and `file_errors: 0`, with warnings only for missing optional AI_VIDEO/B_ROLL visuals. Generated artifacts must remain ignored, and commit candidates should be limited to source, tests, and docs relevant to CLI UX.

## Idempotence and Recovery

The audit and validation commands can be run repeatedly. `build-timeline`, `export-remotion`, and asset preparation commands rewrite generated local files such as `timeline.json`, `remotion/props.json`, and `remotion/public/`. These are expected validation artifacts. Do not commit generated media, public assets, render outputs, or validation-regenerated `remotion/props.json` unless explicitly approved.

If a selected UX change proves too broad, stop and record the issue in this plan rather than continuing into feature work. If tests fail unexpectedly, inspect whether the failure is due to planned output text changes or an unintended behavior change. Revert or redesign only the unplanned behavior change; do not hide regressions by weakening tests.

Do not use ffmpeg, ffprobe, media probing, media transcoding, media generation, external downloads, Remotion rendering, new render scripts, DOCX parsing, GUI/web app work, tags, pushes, or Phase 29 feature work in this phase.

## Artifacts and Notes

Current CLI output locations:

    synccut/cli.py:
    - Typer command registration and help text.
    - Human-readable command success and error output.
    - JSON output routing for inspect-visual-assets and preflight.

    synccut/preflight.py:
    - PreflightSummary data class.
    - format_preflight human-readable output.
    - preflight_to_dict JSON output.

    synccut/visual_assets.py:
    - format_visual_asset_readiness human-readable output.
    - visual_asset_readiness_to_dict JSON output.

    tests/test_cli.py:
    - CLI invocation tests.
    - Direct assertions for output text and no-traceback behavior.

Known current output examples from code and tests include `OK <timeline>`, `Exported <props>`, `Prepared Remotion assets for <props>`, `warnings: <n>`, `errors: <n>`, `status: warning`, `file_errors: <n>`, and `warning visual_missing ... placeholder will render`.

## Interfaces and Dependencies

Use the existing Typer dependency already declared in `pyproject.toml`. Do not add new Python dependencies. Do not add new npm dependencies. Do not add new command-line parser libraries.

If editing CLI help, use existing Typer patterns in `synccut/cli.py`: command docstrings, `typer.Argument(help=...)`, and `typer.Option(help=...)`. If editing output formatters, keep outputs as plain text with stable key-value labels where possible. If adding next-step hints, keep them in human-readable output only and do not add them to JSON outputs.

Do not change public data schemas. The `timeline.json`, `remotion/props.json`, `preflight --json`, and `inspect-visual-assets --json` structures must remain unchanged unless a later explicit approval says otherwise.

## Change Note

2026-05-14 / Codex: Created this Phase 28 ExecPlan for CLI UX polish. The plan records current CLI/output modules, current tests, absent old asset module names, safe audit commands, small allowed UX changes, validation workflow, artifact policy, and explicit exclusions. No CLI implementation, source change, tests change, README change, schema change, render, media operation, commit, tag, push, or Phase 29 work was performed.
2026-05-14 / Codex: Completed Milestone 1 CLI UX audit. Ran all command help output and the safe no-visual sample workflow through verified preflight. Recorded help gaps, silent build success, next-step opportunities, optional visual warning clarity issues, JSON boundary constraints, and generated props cleanup note. No source, tests, README, schema, CLI behavior, render, media operation, commit, tag, push, or Phase 29 work was performed.
