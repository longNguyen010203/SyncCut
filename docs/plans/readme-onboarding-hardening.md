# README and onboarding hardening

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

This document is maintained according to `.agent/PLANS.md` in the repository root. It is self-contained: a contributor should be able to audit and harden SyncCut's README and onboarding documentation from this file without reading earlier conversation.

## Purpose / Big Picture

SyncCut v0.1.0 has been tagged and released. The code and render workflow are now proven, but a fresh-clone user still needs clear onboarding: what the project is, what the MVP can and cannot do, how to install Python and Remotion dependencies, how to run the sample pipeline, what files are generated, how local visuals work, and how to avoid common render environment traps. This phase makes the repository easier to understand and run without adding features.

After this plan is complete, a new contributor should be able to clone the repository, install dependencies, run the sample SyncCut pipeline through preflight, understand how to optionally prepare local visuals, understand the Remotion still/smoke/segment/final workflows, and know which generated artifacts must not be committed. The observable result is improved documentation plus passing validation commands.

## Progress

- [x] (2026-05-14T11:20:00+07:00) Read `AGENTS.md`, `.agent/PLANS.md`, root `README.md`, `remotion/README.md`, final render quality review, Phase 25 release checklist, Phase 24 post-polish render plan, Phase 23 timing/loop plan, `pyproject.toml`, `remotion/package.json`, `.gitignore`, and current `git status --short --ignored`.
- [x] (2026-05-14T11:20:00+07:00) Confirmed the current README already covers the MVP overview, exclusions, prerequisites, setup, quick start, input expectations, Python command summary, Remotion workflow, local visual assets, preflight/troubleshooting, artifact policy, development commands, and roadmap link.
- [x] (2026-05-14T11:20:00+07:00) Created this Phase 26 ExecPlan.
- [x] (2026-05-14T11:28:00+07:00) Milestone 1: Audited the current root README and Remotion README for onboarding strengths, gaps, contradictions, and stale release-era notes.
- [x] (2026-05-14T11:42:00+07:00) Milestone 2: Updated the root README overview, prerequisites, fresh-clone setup, no-visual quick start, and v0.1.0 release evidence summary.
- [x] (2026-05-14T11:55:00+07:00) Milestone 3: Added a root README pipeline overview, generated artifact explanations, artifact role policy, and `git status` / `git restore remotion/props.json` cleanup note.
- [x] (2026-05-14T12:08:00+07:00) Milestone 4: Clarified root README local visual asset workflow and Remotion render workflow, and made a narrow Remotion README consistency update for root README linkage and `remotion/public/visuals/*` artifacts.
- [x] (2026-05-14T12:20:00+07:00) Milestone 5: Ran final pytest, Remotion typecheck, docs diff review, artifact review, and recorded commit recommendation.

## Surprises & Discoveries

- Observation: The root README is already practical but compact.
  Evidence: It includes a project overview, MVP feature list, explicit non-goals, prerequisites, setup commands, quick-start commands, input expectations, command summary, Remotion workflow, local visual assets, preflight/troubleshooting, artifact policy, development commands, and roadmap link.
- Observation: The README quick start currently stops at smoke render and does not show the full optional visual preparation path.
  Evidence: The quick-start command block runs `prepare-remotion-assets`, `inspect-visual-assets`, verified preflight, `npm run typecheck`, and `npm run render:smoke:local`, but it does not show `prepare-visual-assets` or segment/final render commands in the main sequence.
- Observation: The artifact policy is present but could be tied more directly to the pipeline.
  Evidence: The README lists ignored artifacts, while the pipeline story is split across Quick Start, Remotion Workflow, Local Visual Assets, and Artifact Policy sections.
- Observation: The Remotion README already documents smoke, segment, and final render commands plus Chrome sandbox behavior.
  Evidence: `remotion/README.md` includes sections for still preview, smoke render, segment render, final render, Studio preview, generated artifacts, and notes about `SIGTRAP` and `setsockopt: Operation not permitted`.
- Observation: v0.1.0 release evidence is text-only and committed in planning/review docs.
  Evidence: `docs/final-render-quality-review.md` records the post-polish full render, `22584/22584` frames, `remotion/out/final.mp4`, output sizes, accepted `P22-001` and `P22-002`, and `release-ready-with-known-warnings`; `docs/plans/v0.1.0-release-checklist.md` records final validation and tag readiness.
- Observation: Current git status has only ignored generated/local paths.
  Evidence: `git status --short --ignored` showed ignored `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.
- Observation: The root README already explains the main onboarding pieces well.
  Evidence: It covers project purpose, MVP supported behavior, explicit non-goals, Python and Remotion prerequisites, virtualenv setup, `npm install`, sample commands, input expectations, Python command summaries, Remotion workflow summaries, local visual assets, preflight/troubleshooting, artifact policy, development commands, and a roadmap link.
- Observation: The root README's quick start is useful for a fast smoke path, but it does not clearly separate "fresh clone smoke validation" from "full visual asset validation."
  Evidence: The quick start prepares audio, inspects visual assets, runs verified preflight, typechecks, and smoke-renders. It does not show where `prepare-visual-assets` fits, so a new user can see missing visual warnings without a direct next command in the same path.
- Observation: The root README lacks a compact pipeline map and v0.1.0 release evidence summary.
  Evidence: The data flow is spread across Quick Start, Input Expectations, Local Visual Assets, Remotion Workflow, and Artifact Policy. The README does not yet summarize the post-polish v0.1.0 validation outcome recorded in `docs/final-render-quality-review.md` and `docs/plans/v0.1.0-release-checklist.md`.
- Observation: The local visual asset section is correct but could be more operational for a new contributor.
  Evidence: It documents `assets/visuals/<scene_id>.<ext>`, supported extensions, and `prepare-visual-assets`, but it does not show a before/after inspect flow, duplicate-file expectation, verified preflight after visual prep, or a link to `docs/tsmc-visual-asset-manifest.md`.
- Observation: The Remotion README is the right home for render-script details.
  Evidence: It documents `still:local`, `render:smoke:local`, `render:segment:local`, `render:final:local`, output paths, local Chrome flags, sandbox launch behavior, and the Studio preview network caveat.
- Observation: There is no major contradiction between root README and `remotion/README.md`, but one detail should be aligned later if the Remotion README is edited.
  Evidence: The root README artifact policy correctly covers `remotion/public/*`, while `remotion/README.md` names `remotion/public/audio/*.mp3` and does not explicitly mention `remotion/public/visuals/*`. This is a weak omission, not a blocking contradiction.
- Observation: Milestone 2 changed only root README onboarding sections.
  Evidence: The update refined the opening project description, added the v0.1.0 prepared-input-to-video framing, expanded prerequisites, added fresh-clone command context, made `source .venv/bin/activate` explicit, split the quick start into a no-visual preflight path plus Remotion typecheck, and added a concise v0.1.0 release evidence section.
- Observation: Version and dependency notes came from local metadata, not external assumptions.
  Evidence: `pyproject.toml` declares `requires-python = ">=3.11"`, and `remotion/package.json` declares Remotion 4, React 18, and TypeScript 5 dependencies.
- Observation: No direct `remotion/README.md` consistency edit was needed in Milestone 2.
  Evidence: The quickstart update points to the existing Local Visual Assets and Remotion Workflow sections without changing render-command details. The minor `remotion/public/visuals/*` generated-artifact omission can remain for Milestone 4 if still useful.
- Observation: Milestone 3 made the generated file lifecycle explicit in the root README.
  Evidence: The README now includes a `Pipeline Overview` section mapping prepared inputs to `timeline.json`, validation/inspection, `remotion/props.json`, prepared audio, optional prepared visuals, preflight, and `remotion/out/*` render outputs.
- Observation: The artifact policy now distinguishes local source media, prepared public media, render outputs, generated timelines, and generated props.
  Evidence: The README describes `assets/visuals/*`, `remotion/public/*`, `remotion/out/*`, `timeline.json`, and `remotion/props.json` by role before listing common ignored paths.
- Observation: The `remotion/props.json` policy is now less ambiguous for fresh contributors.
  Evidence: The README says `remotion/props.json` is generated sample props, should not be committed after local validation regeneration unless a sample props refresh is explicitly approved, and shows `git restore remotion/props.json` for that specific generated case.
- Observation: Milestone 4 made the local visual asset workflow operational instead of only descriptive.
  Evidence: The root README now documents `assets/visuals/<scene_id>.<supported_ext>`, supported extensions, exactly one supported file per target scene, non-bundled media policy, inspect/prepare/inspect/preflight commands, expected full TSMC visual state, and the visual asset manifest link.
- Observation: Milestone 4 expanded the Remotion workflow summary without duplicating all Remotion README detail.
  Evidence: The root README now lists the `cd remotion` command context, `typecheck`, `still:local`, `render:smoke:local`, `render:segment:local`, `render:final:local`, each output path, local Chrome flags, sandbox failure symptoms, and the guidance to rerun with browser permission rather than adding workaround code.
- Observation: A narrow `remotion/README.md` consistency update was justified.
  Evidence: The Remotion README now points readers back to the root README for the full pipeline and includes `remotion/public/visuals/*` in generated artifacts, aligning it with the root README artifact policy.
- Observation: Final validation passed after documentation changes.
  Evidence: `.venv/bin/python -m pytest` collected 212 tests and passed all 212. `cd remotion && npm run typecheck` completed `tsc --noEmit` successfully.
- Observation: Artifact review found docs-only commit candidates and expected ignored local/generated paths.
  Evidence: `git status --short --ignored` showed `M README.md`, `M remotion/README.md`, and `?? docs/plans/readme-onboarding-hardening.md` as non-ignored changes. Ignored paths included `.pytest_cache/`, `.venv/`, `assets/`, `examples/`, `remotion/node_modules/`, `remotion/out/`, `remotion/public/`, Python `__pycache__/` directories, and `timeline.json`.
- Observation: README and Remotion README are now consistent for onboarding scope.
  Evidence: The root README owns the full pipeline, visual asset workflow, preflight, artifact policy, release evidence, and troubleshooting summary. `remotion/README.md` now points to the root README for the full pipeline and keeps Remotion-specific commands and outputs.

## Decision Log

- Decision: Treat Phase 26 as documentation-only onboarding hardening.
  Rationale: v0.1.0 has already shipped; this phase should make the existing release easier to understand and run, without changing command behavior, source code, schemas, render scripts, media, or release artifacts.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep root README as the main onboarding entry point and use `remotion/README.md` for Remotion-specific depth.
  Rationale: The root README is already the user's first landing page and should tell the full story at a practical level. The Remotion README can continue to hold detailed render workflow notes so the root README does not become unwieldy.
  Date/Author: 2026-05-14 / Codex
- Decision: Do not start Phase 27, Phase 28, Phase 29, or any major feature work in this plan.
  Rationale: The user explicitly set the roadmap order as Phase 26 README/onboarding hardening, Phase 27 developer workflow and CI, and Phase 28 CLI UX polish, and said not to start Phase 29 or major upgrades without asking.
  Date/Author: 2026-05-14 / Codex
- Decision: Milestone 2 should edit the root README first, starting with the fresh-clone setup and quick start.
  Rationale: The highest-impact onboarding gap is not missing command coverage, but command sequencing. A new reader should quickly understand the difference between fast smoke validation, clean props without visuals, and the optional full local visual asset path.
  Date/Author: 2026-05-14 / Codex
- Decision: Keep detailed render command behavior in `remotion/README.md` and summarize it from the root README.
  Rationale: The Remotion README already has the detail needed for still, smoke, segment, final render, Chrome flags, output paths, and sandbox behavior. The root README should provide the contributor-level path and link deeper rather than duplicate every render note.
  Date/Author: 2026-05-14 / Codex
- Decision: Do not edit `remotion/README.md` unless Milestone 4 needs a narrow consistency fix.
  Rationale: The only audit mismatch found is the generated artifact wording around `remotion/public/visuals/*`; this can be fixed later if root README changes make the omission confusing.
  Date/Author: 2026-05-14 / Codex

## Outcomes & Retrospective

This plan has been created after reviewing the current onboarding and release documentation. No README edits, source edits, schema changes, command behavior changes, render scripts, media operations, render commands, commits, tags, or pushes were performed while creating the plan.

The expected outcome is a clearer root README with no change to project behavior. The README should explain the v0.1.0 MVP, fresh-clone setup, sample commands, end-to-end data flow, local visual assets, Remotion render options, troubleshooting, and artifact policy well enough that a new contributor can run the sample pipeline and avoid committing generated artifacts.

Milestone 1 audit result: the existing README is a solid base and should be refined rather than rewritten wholesale. The recommended README structure for the next milestones is:

1. Overview and v0.1.0 status.
2. Supported MVP scope and explicit non-goals.
3. Prerequisites and fresh-clone setup.
4. Quick start sample pipeline, with a clear fast smoke path and optional full visual path.
5. Pipeline map from inputs to timeline, props, public assets, and render output.
6. Local visual asset workflow and manifest link.
7. Remotion workflow summary with a link to `remotion/README.md`.
8. Preflight, troubleshooting, and Chrome sandbox notes.
9. Artifact policy and `remotion/props.json` guidance.
10. Development/testing and roadmap links.

Next step: Milestone 2 should update the root README quick start and setup path first. It should keep `remotion/README.md` as the detailed render reference unless a narrow consistency fix is needed later.

Milestone 2 result: the README now starts with a clearer description of SyncCut as a Python CLI plus Remotion renderer and names the v0.1.0 MVP as a prepared-input-to-video pipeline. Prerequisites now cite Python `>=3.11` from `pyproject.toml`, note the Remotion 4/React 18/TypeScript 5 project context from `remotion/package.json`, and clarify that local AI video and B-roll files are optional. Setup now reads as a fresh-clone path and explicitly says commands are run from the repository root unless `cd remotion` is shown.

The quick start now prioritizes a no-visual validation path: build timeline, validate, export Remotion props, prepare audio, and run verified preflight. It explains that missing optional AI_VIDEO/B_ROLL visuals can produce warning-only preflight output, while `errors` and `file_errors` should remain `0`. The README also adds a concise v0.1.0 release evidence section with the post-polish final render result, accepted P22-001/P22-002 fixes, `release-ready-with-known-warnings` decision, and links to the detailed evidence docs.

Remaining docs work: Milestone 3 should add a compact pipeline map and tighten artifact-policy placement, especially `timeline.json`, `remotion/props.json`, `remotion/public`, and render output lifecycle. Milestone 4 should make the visual asset workflow more operational and decide whether to align the generated-artifact wording in `remotion/README.md`. Milestone 5 should run pytest, Remotion typecheck, and artifact review.

Milestone 3 result: the README now has a concise pipeline map from `scenes.json` plus audio plus alignments through timeline generation, Remotion props export, audio and optional visual asset preparation, preflight, and Remotion render output. The artifact policy now explains each generated/local path by role instead of only listing ignored paths, and includes a practical "dirty status" note for restoring `remotion/props.json` when it changed only because of validation regeneration.

Remaining docs work: Milestone 4 should focus on making the local visual asset workflow and render workflow more operational, including inspect/prepare/preflight sequencing, the TSMC manifest link, and whether `remotion/README.md` needs the narrow `remotion/public/visuals/*` artifact wording alignment. Milestone 5 should run pytest, Remotion typecheck, and artifact review.

Milestone 4 result: the root README now explains the optional AI_VIDEO/B_ROLL local visual workflow enough for a contributor to validate the full visual sample: place one supported file per scene under `assets/visuals/`, inspect visual readiness, run `prepare-visual-assets`, inspect again, and run verified preflight. It also documents the expected full TSMC prepared counts and points to `docs/tsmc-visual-asset-manifest.md`.

The Remotion workflow summary now names the output path for still, smoke, segment, and final renders and includes the Chrome sandbox failure symptoms and permission guidance. `remotion/README.md` was changed only to add a root README pointer and include prepared visuals in its generated artifact list.

Remaining work: Milestone 5 should run `.venv/bin/python -m pytest`, `cd remotion && npm run typecheck && cd ..`, review `git status --short --ignored`, confirm commit candidates are docs only, and record the final commit recommendation.

Milestone 5 result: Phase 26 validation passed. Python tests passed with 212 tests, Remotion typecheck passed, and artifact review confirmed the only non-ignored commit candidates are documentation files: `README.md`, `remotion/README.md`, and `docs/plans/readme-onboarding-hardening.md`. Ignored generated/local artifacts remain ignored, including `timeline.json`, `remotion/public/`, `remotion/out/`, `assets/`, `.venv/`, `remotion/node_modules/`, `.pytest_cache/`, and `__pycache__/` directories.

Acceptance criteria status: met. The root README now gives a new contributor a clearer path to understand SyncCut v0.1.0, set up a fresh clone, run the no-visual sample validation path, understand the pipeline and generated artifacts, prepare optional local visuals, understand Remotion render options, and avoid committing local/generated media. The Remotion README remains consistent and focused on Remotion-specific workflows.

Commit recommendation: commit the docs-only changes with message `Improve README onboarding for v0.1.0`.

Next step: Phase 27 Developer workflow and CI can start after the user requests it. Do not start Phase 27, Phase 28, Phase 29, or any major feature work from this plan without a new user request.

## Context and Orientation

The repository root is `/home/longnguyen/Desktop/AI/Codex/SyncCut`. SyncCut is a Python CLI plus a Remotion project. The Python package metadata is in `pyproject.toml`: project name `synccut`, version `0.1.0`, Python requirement `>=3.11`, dependency `typer>=0.12`, development extra `pytest>=8`, and console script `synccut = "synccut.cli:app"`. A fresh developer usually creates `.venv`, installs with `.venv/bin/python -m pip install -e '.[dev]'`, then uses `.venv/bin/synccut`.

The Remotion project lives in `remotion/`. Its `package.json` defines scripts for `studio`, `typecheck`, `still`, `still:local`, `render:smoke:local`, `render:segment:local`, and `render:final:local`. The local render scripts use `/usr/bin/google-chrome` and `--chrome-mode=chrome-for-testing`. In sandboxed environments, Chrome launch may fail with `SIGTRAP` or `setsockopt: Operation not permitted`; that is an environment permission issue, not necessarily a Remotion app bug.

The sample pipeline starts with prepared inputs. `examples/scenes.json` describes scenes, dialogue, section keys, and visual metadata. `examples/audio/` contains section narration files named by section key. `examples/alignments/` contains alignment JSON files named by section key, with paragraph, sentence, and word timing. The CLI builds `timeline.json`, validates it, exports `remotion/props.json`, prepares public audio under `remotion/public/audio`, optionally prepares local AI_VIDEO/B_ROLL visuals under `remotion/public/visuals`, runs preflight, and then Remotion can render from `remotion/props.json`.

Local visual assets are optional files under `assets/visuals/<scene_id>.<ext>`. Supported extensions are `.mp4`, `.webm`, `.mov`, `.png`, `.jpg`, `.jpeg`, and `.webp`. Missing AI_VIDEO/B_ROLL local files render placeholders and are warnings, not errors. Prepared visual public paths must be valid; verified preflight treats missing prepared public files as errors. The full TSMC validation used 17 local AI_VIDEO/B_ROLL assets, but those media files are ignored and not bundled in git.

Generated and local-only artifacts must not be committed. `.gitignore` ignores `examples`, `assets/visuals/`, `.venv`, `remotion/node_modules`, `remotion/public`, `remotion/out/`, `timeline.json`, `__pycache__/`, and `.pytest_cache/`. `remotion/props.json` is a tracked sample input, but if it changes only because of local validation regeneration, it should usually be restored rather than committed unless the user explicitly approves a sample props refresh.

## Plan of Work

Milestone 1 is a documentation audit only. Read `README.md` and `remotion/README.md` closely. Record what the root README already explains well and identify specific onboarding gaps. Gaps to check include prerequisites, setup, fresh clone commands, sample pipeline commands, pipeline overview, generated artifact policy, Remotion render workflow, visual asset workflow, troubleshooting, and release evidence. Do not edit the README during this milestone unless a broken link blocks further planning.

Milestone 2 updates the root README quickstart and setup path. Improve or add concise sections that explain what SyncCut is, what v0.1.0 supports, prerequisites for Python, Node, npm, and local Chrome, fresh-clone setup, Python virtual environment installation, Remotion `npm install`, and the sample pipeline commands. The sample path should be runnable from a fresh clone with the repository's existing example inputs. Keep wording practical and avoid turning the README into a full changelog.

Milestone 3 clarifies the pipeline and artifact policy. The README should make the data flow explicit: `scenes.json` plus audio plus alignments produce `timeline.json`; `timeline.json` exports to `remotion/props.json`; asset preparation writes under `remotion/public`; Remotion renders from props and public assets. Document generated and ignored artifacts in the same story, including why validation-regenerated `remotion/props.json` is usually not committed and why local visual media stays ignored.

Milestone 4 clarifies visual assets and Remotion render workflow. The README should document optional AI_VIDEO/B_ROLL local visual assets, expected names under `assets/visuals/<scene_id>.<ext>`, supported extensions, `prepare-visual-assets`, `inspect-visual-assets`, `preflight --verify-files`, and the still/smoke/segment/final Remotion commands. It should point to `remotion/README.md` for detailed render notes and include the Chrome sandbox note. If `remotion/README.md` contradicts the root README, update the smallest necessary text there; otherwise leave it unchanged.

Milestone 5 validates and reviews. Run `.venv/bin/python -m pytest`, then `cd remotion && npm run typecheck && cd ..`. Do not render. Run `git status --short --ignored` and confirm commit candidates are docs only. Record validation results, artifact status, remaining risks, and a commit recommendation. A likely commit message is `Harden README onboarding for v0.1.0`.

## Concrete Steps

For Milestone 1, run read-only inspection from the repository root:

    sed -n '1,260p' README.md
    sed -n '1,260p' remotion/README.md
    git status --short --ignored

Record findings in this plan. The README already has many good pieces; the audit should focus on specific improvements rather than rewriting for its own sake.

For Milestone 2, edit `README.md` only. Keep the root README as the main entry point. Prefer a structure that includes a short project overview, what v0.1.0 does, what it does not do, prerequisites, setup, quick start, input expectations, command summary, Remotion workflow, visual assets, preflight/troubleshooting, artifact policy, development, and roadmap. If the current structure remains good, refine the existing sections instead of replacing the file wholesale.

The fresh-clone setup should include:

    python3 -m venv .venv
    .venv/bin/python -m pip install -e '.[dev]'
    cd remotion
    npm install
    cd ..

The sample pipeline should include the existing commands:

    .venv/bin/synccut build-timeline examples/scenes.json --audio-dir examples/audio --alignment-dir examples/alignments --out timeline.json
    .venv/bin/synccut validate-timeline timeline.json
    .venv/bin/synccut inspect timeline.json
    .venv/bin/synccut export-remotion timeline.json --out remotion/props.json
    .venv/bin/synccut prepare-remotion-assets remotion/props.json --out-dir remotion/public
    .venv/bin/synccut inspect-visual-assets remotion/props.json
    .venv/bin/synccut preflight remotion/props.json --verify-files --public-dir remotion/public
    cd remotion
    npm run typecheck
    npm run render:smoke:local

For Milestone 3, keep editing `README.md`. Add or refine the pipeline overview and artifact policy. Explain that clean sample validation can have missing visual warnings because local AI_VIDEO/B_ROLL files are optional. Explain that prepared visual assets are local validation state and that `remotion/props.json` can be rewritten by export and preparation commands. Tell the reader to restore or avoid committing `remotion/props.json` unless intentionally refreshing sample props.

For Milestone 4, edit `README.md` and only edit `remotion/README.md` if necessary for consistency. Include the local visual asset naming convention and supported extensions. Include commands for preparing visuals and verified preflight. Include Remotion commands:

    cd remotion
    npm run typecheck
    npm run still:local
    npm run render:smoke:local
    npm run render:segment:local
    npm run render:final:local

State that render outputs are ignored. State that Chrome launch may require sandbox permission. State that Python does not invoke Remotion.

For Milestone 5, run validation from the repository root:

    .venv/bin/python -m pytest
    cd remotion
    npm run typecheck
    cd ..
    git status --short --ignored

Do not run still, smoke, segment, or final render in this phase unless the user explicitly asks. Update this plan with validation output and commit recommendation.

## Validation and Acceptance

This phase is accepted when the root README gives a new contributor enough context to set up the Python environment, install Remotion dependencies, run the v0.1.0 sample pipeline through verified preflight, understand optional visual assets, run the local Remotion workflows, and avoid committing generated artifacts.

The Remotion README must remain consistent with the root README. It does not need to duplicate every root README detail, but it should not contradict the root instructions about render commands, Chrome sandbox behavior, generated outputs, or Python not invoking Remotion.

Validation must pass with `.venv/bin/python -m pytest` from the repository root and `npm run typecheck` from `remotion/`. Since this is a docs-only phase, no test count change is expected. Commit candidates should be documentation only, normally `README.md`, possibly `remotion/README.md` if consistency requires it, and `docs/plans/readme-onboarding-hardening.md`.

## Idempotence and Recovery

Documentation edits are safe to revise. If the README becomes too long, move detail back into existing deeper docs such as `remotion/README.md` and link to them instead of duplicating everything. If a validation command fails, record the exact failure and stop; do not change source code in this phase unless the user explicitly approves a follow-up fix.

Do not run render commands in this phase. Render commands can take a long time and produce ignored media under `remotion/out/`; Phase 26 only hardens documentation. Do not run `prepare-visual-assets` unless a later milestone explicitly changes scope, because this plan does not need prepared local visual state.

If `remotion/props.json` is modified accidentally by validation or experimentation, restore it only if the change is generated and not explicitly approved as a sample props refresh. Do not restore source or docs files without explicit user approval.

## Artifacts and Notes

Relevant current facts:

    pyproject.toml:
    - project name: synccut
    - version: 0.1.0
    - requires-python: >=3.11
    - dependency: typer>=0.12
    - dev extra: pytest>=8
    - console script: synccut = synccut.cli:app

    remotion/package.json:
    - typecheck
    - still:local
    - render:smoke:local
    - render:segment:local
    - render:final:local
    - local render scripts use /usr/bin/google-chrome and chrome-for-testing mode

    v0.1.0 release evidence:
    - Phase 23 fixed timing gap smoothing and explicit video loop behavior.
    - Phase 24 validated post-polish final render: 22584/22584 frames, remotion/out/final.mp4, 587M by ls, 615.1 MB by Remotion.
    - Human re-review accepted P22-001 and P22-002.
    - Phase 25 recorded release checklist and tag readiness.

Generated/local paths to keep out of commits:

- `timeline.json`
- `remotion/public/*`
- `remotion/out/*`
- `assets/visuals/*`
- `.venv/`
- `remotion/node_modules/`
- `.pytest_cache/`
- Python `__pycache__/`
- `remotion/props.json` when changed only by validation regeneration

## Interfaces and Dependencies

The only intended implementation interfaces in this phase are Markdown files: `README.md`, possibly `remotion/README.md`, and this plan file. Do not edit `synccut/`, `remotion/src/`, schemas, tests, npm scripts, Python packaging, or generated props.

Use the existing Python CLI commands exactly as documented by `.venv/bin/synccut --help`. Use existing Remotion npm scripts exactly as defined in `remotion/package.json`. Do not add new commands, wrappers, scripts, dependencies, CI files, or GUI/web app behavior; those belong to later phases only after explicit user request.

## Change Note

2026-05-14 / Codex: Created this ExecPlan for Phase 26 README and onboarding hardening. The plan records current README strengths, likely onboarding gaps, documentation-only milestones, validation commands, artifact policy, and explicit exclusions. No README implementation, source change, render, commit, tag, or push was performed.
2026-05-14 / Codex: Completed Milestone 1 README audit. Recorded root README strengths, weak onboarding areas, the one minor Remotion README artifact-policy omission, Milestone 2 edit priority, and recommended README structure. No README, source, media, render, commit, tag, or push action was performed.
2026-05-14 / Codex: Completed Milestone 2 README quickstart update. Root README now clarifies v0.1.0 scope, prerequisites, fresh-clone setup, no-visual sample preflight path, expected warning-only visual state, Remotion typecheck handoff, and release evidence links. No Remotion README, source, schema, render script, media, render, commit, tag, or push action was performed.
2026-05-14 / Codex: Completed Milestone 3 pipeline and artifact policy documentation. Root README now includes a pipeline overview, generated artifact role explanations, `remotion/props.json` commit guidance, and a targeted dirty-status cleanup note. No Remotion README, source, schema, command, render script, media, render, commit, tag, or push action was performed.
2026-05-14 / Codex: Completed Milestone 4 visual asset and Remotion render workflow documentation. Root README now documents one-file-per-scene visual naming, inspect/prepare/preflight commands, full TSMC visual expected state, render command outputs, and Chrome sandbox guidance. Remotion README received only a root README pointer and `remotion/public/visuals/*` generated artifact alignment. No source, schema, command, render script, media, render, commit, tag, or push action was performed.
2026-05-14 / Codex: Completed Milestone 5 final validation and artifact review. Pytest passed with 212 tests, Remotion typecheck passed, and status review found docs-only commit candidates with generated/local artifacts ignored. Recommended commit message: `Improve README onboarding for v0.1.0`. No source, schema, command, render script, media, render, commit, tag, push, or later-phase work was performed.
