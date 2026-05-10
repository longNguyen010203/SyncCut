# SyncCut Agent Instructions

## Project Overview
SyncCut is a Python CLI tool that builds structured video production timelines from:
- pre-generated `scenes.json`
- narration audio files
- alignment JSON files with paragraph, sentence, and word-level timestamps

Current MVP command:
`synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json`

The MVP output is `timeline.json`.

## MVP Scope
Do:
- read and validate `scenes.json`
- load matching audio files
- load matching alignment JSON files
- match scenes to alignment timing
- generate `timeline.json`

Do not do in MVP:
- DOCX parsing
- Remotion rendering
- ffmpeg processing
- AI video generation
- B-roll downloading
- final MP4 assembly
- GUI/web app

## Required References
Before implementation, read:
- `docs/architecture.md`
- `docs/schemas.md`
- `docs/matching.md`
- `docs/testing.md`

For future Remotion/ffmpeg work, read:
- `docs/future-phases.md`

## Development Stack
Use Python 3.11+, Typer, pytest, JSON, and pathlib.
Use Pydantic only if schema validation becomes clearly useful.

## Project Structure
Prefer:
- `synccut/cli.py`
- `synccut/models.py`
- `synccut/scenes_loader.py`
- `synccut/alignment_loader.py`
- `synccut/timeline_builder.py`
- `synccut/validators.py`
- `tests/test_scenes_loader.py`
- `tests/test_alignment_loader.py`
- `tests/test_timeline_builder.py`
- `docs/architecture.md`
- `docs/schemas.md`
- `docs/matching.md`
- `docs/testing.md`
- `docs/future-phases.md`

## Core Rules
- Treat `scenes.json` as input.
- Do not mutate input files.
- Keep CLI code thin.
- Keep timeline logic testable.
- Prefer pure functions.
- Use `pathlib.Path`.
- Use clear CLI errors.
- Keep changes small and focused.
- Do not rewrite unrelated files.
- Do not add future-phase logic unless requested.
- Do not commit changes unless explicitly asked.

## Visual Types
Supported normalized values: `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, `TIMELINE`.
Normalize input `B-ROLL` to `B_ROLL`.
Use normalized values internally and in generated output.

## Timeline Rules
Alignment timestamps are section-local.
Build global timing by accumulating section durations.
`scene_start = section_offset + local_start`
`scene_end = section_offset + local_end`
`duration = scene_end - scene_start`
Use alignment duration as the MVP source of truth.
Do not use ffmpeg/ffprobe in MVP unless explicitly requested.

## Matching Rules
Match by:
1. `section_key`
2. dialogue paragraphs
3. sentence fallback
4. word span fallback only if needed

Do not silently invent timing.
Default behavior is strict: fail clearly if matching is impossible.

## Testing
Use pytest with small synthetic fixtures.
Before finishing any coding task, run `pytest`.
If tests fail, fix them and run pytest again.

## External Docs
When implementing external libraries, frameworks, CLIs, or APIs, check Context7 when relevant.
Use Context7 for Typer, pytest, Pydantic, ffmpeg, Remotion, Python packaging, GitHub Actions, and external SDKs.
Do not use Context7 for internal SyncCut logic.

## Git Rules
Allowed read-only commands: `git status`, `git diff`, `git log --oneline`.
Do not run unless explicitly asked: `git add`, `git commit`, `git push`, `git reset`, `git clean`, `git checkout`, `git merge`, `git rebase`.

## Workflow
For non-trivial tasks:
1. Read relevant files.
2. Restate the goal.
3. Propose a short plan.
4. Wait for approval if risky or architectural.
5. Implement only the approved scope.
6. Run tests.
7. Summarize changed files and verification results.

For read-only tasks, do not edit files.

## Definition of Done
A task is done only when:
- requested behavior is implemented
- tests are added or updated
- `pytest` passes
- changed files are summarized
- no unrelated files were modified
- no commit was created unless requested

## Reporting Style
Be concise.
Preferred summary: `Done. Changed: ... Verified: pytest passed. Notes: ...`

## Execution Plans

For large or risky tasks, create an ExecPlan in `docs/plans/`.

Follow the repository root `.agent/PLANS.md` exactly when writing or updating ExecPlans.

Use ExecPlans for:
- `build-timeline` MVP
- Remotion export
- ffmpeg assembly
- asset management
- major schema changes

Do not create an ExecPlan for tiny edits or simple bug fixes unless requested.