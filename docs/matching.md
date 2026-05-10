# SyncCut Matching Rules

Use `section_key` when present.

Example:
- section key: `01_HOOK`
- audio: `audio/01_HOOK.mp3`
- alignment: `alignments/01_HOOK_alignment_tmp.json`

If `section_key` is missing, infer it from `section_order` and `section`.

Audio matching:
- prefer `audio/<section_key>.mp3`
- fallback to `audio/<section_key>*.mp3`
- error on ambiguous matches

Alignment matching:
- use `alignments/<section_key>_alignment*.json`
- error if missing in MVP

Dialogue matching order:
1. `dialogue.paragraphs`
2. alignment paragraphs
3. sentence fallback
4. word span fallback only if needed

Text normalization:
- trim whitespace
- collapse repeated spaces
- lowercase for comparison
- optionally normalize curly quotes
- optionally ignore `⟶`

Timing:
- local start = first matched unit start
- local end = last matched unit end
- global start = section offset + local start
- global end = section offset + local end

Do not silently invent timing.
