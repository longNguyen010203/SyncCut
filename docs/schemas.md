# SyncCut Schemas

## scenes.json

`scenes.json` is input and must not contain audio timing.

Recommended scene:

```json
{
  "scene_id": "scene_001",
  "scene_order": 1,
  "section": "HOOK",
  "section_order": 1,
  "section_key": "01_HOOK",
  "dialogue": {
    "text": "Every iPhone in your pocket.",
    "paragraphs": ["Every iPhone in your pocket."]
  },
  "visual": {
    "type": "AI_VIDEO",
    "prompt": "Extreme close-up of a silicon wafer...",
    "data": null
  }
}
```

Metadata should include `schema_version` and numeric `total_scenes`.

Visual types: `AI_VIDEO`, `B_ROLL`, `CHART`, `COMPARISON_CARD`, `TABLE`, `SHARE_BREAKDOWN`, `TIMELINE`.

Normalize `B-ROLL` to `B_ROLL`.

## Alignment JSON

Useful fields:

```json
{
  "total_duration_sec": 18.39,
  "paragraphs": [
    {
      "paragraph": "Every iPhone in your pocket.",
      "paragraph_index": 0,
      "start": 0.0,
      "end": 1.556,
      "duration": 1.556,
      "sentences": []
    }
  ],
  "words": [{"word": "Every", "start": 0.0, "end": 0.302}]
}
```

## timeline.json

MVP output should include metadata, timeline array, audio references, alignment references, timing, dialogue match metadata, visual data, and warnings.

Scene timing should use global seconds.
