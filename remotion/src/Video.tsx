import {AbsoluteFill, Sequence} from "remotion";
import {AnimatedBackground} from "./components/AnimatedBackground";
import {SceneRenderer} from "./components/SceneRenderer";
import {SceneShell} from "./components/SceneShell";
import {SectionAudio} from "./components/SectionAudio";
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
      <AnimatedBackground />
      <SectionAudio sections={sections} />
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.start_frame}
          durationInFrames={scene.duration_frames}
        >
          <SceneShell scene={scene}>
            <SceneRenderer scene={scene} sections={sections} />
          </SceneShell>
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
