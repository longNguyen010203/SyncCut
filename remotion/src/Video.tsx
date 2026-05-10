import {AbsoluteFill, Sequence} from "remotion";
import {SceneRenderer} from "./components/SceneRenderer";
import type {SyncCutProps} from "./types";

export const Video = ({metadata, scenes, sections}: SyncCutProps) => {
  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#101316",
        color: "#f4f7fb",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
      }}
    >
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.start_frame}
          durationInFrames={scene.duration_frames}
        >
          <SceneRenderer scene={scene} sections={sections} />
        </Sequence>
      ))}
      <div
        style={{
          position: "absolute",
          left: 48,
          bottom: 34,
          fontSize: 22,
          lineHeight: 1.3,
          color: "rgba(244, 247, 251, 0.62)",
          letterSpacing: 0,
        }}
      >
        {metadata.total_scenes} scenes · {metadata.total_sections} sections ·{" "}
        {metadata.duration_frames} frames
      </div>
    </AbsoluteFill>
  );
};
