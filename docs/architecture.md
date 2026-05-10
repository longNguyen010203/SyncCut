# SyncCut Architecture

SyncCut builds `timeline.json` from `scenes.json`, audio files, and alignment JSON files.

Pipeline:

```text
scenes.json + audio/ + alignments/ -> synccut build-timeline -> timeline.json
```

Python CLI responsibilities:
- load and validate scenes
- load audio references
- load alignment JSON
- match scene dialogue to alignment timing
- create global timeline timing
- preserve visual metadata for later rendering

MVP excludes DOCX parsing, Remotion, ffmpeg, AI video generation, B-roll downloading, and final video assembly.

Preferred modules:
- `cli.py`: Typer commands only
- `models.py`: shared types
- `scenes_loader.py`: load and normalize `scenes.json`
- `alignment_loader.py`: discover and load alignment files
- `timeline_builder.py`: build `timeline.json`
- `validators.py`: validation helpers

Initial command:

```bash
synccut build-timeline scenes.json --audio-dir audio --alignment-dir alignments --out timeline.json
```
