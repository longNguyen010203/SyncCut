# SyncCut Future Phases

Do not implement these until explicitly requested.

## Validation

Potential commands:
- `synccut validate-scenes scenes.json`
- `synccut validate-timeline timeline.json`

## Remotion Export

Potential command:

```bash
synccut export-remotion timeline.json --out remotion/props.json
```

Remotion should render:
- `COMPARISON_CARD`
- `CHART`
- `TABLE`
- `TIMELINE`
- `SHARE_BREAKDOWN`

## Remotion Rendering

Potential command:

```bash
synccut render-visuals timeline.json
```

SyncCut may call Remotion, but components live in the Remotion project.

## Asset Management

For `AI_VIDEO` and `B_ROLL`, SyncCut should manage prompts and asset paths.

Do not generate videos or download B-roll unless requested.

## ffmpeg Assembly

Potential command:

```bash
synccut assemble timeline.json --audio-dir audio --out final.mp4
```

Only add ffmpeg after timeline generation is stable.
