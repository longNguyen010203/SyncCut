# SyncCut Testing Guide

Use pytest and small synthetic fixtures.

Do not rely on large production media files.

Run `pytest` before finishing coding tasks.

Test `scenes_loader.py`:
- valid scenes JSON
- missing metadata
- missing scenes
- empty scenes
- missing required fields
- visual type normalization
- input file not mutated

Test `alignment_loader.py`:
- valid alignment JSON
- missing file
- malformed JSON
- missing paragraphs
- missing timing fields
- section-key discovery
- ambiguous matches

Test `timeline_builder.py`:
- paragraph matching
- sentence fallback
- cumulative section offsets
- global start/end/duration
- preserving visual data
- preserving dialogue data
- missing audio
- missing alignment
- unmatched dialogue
- output JSON shape

MVP does not decode audio. Placeholder `.mp3` files are acceptable in tests.
