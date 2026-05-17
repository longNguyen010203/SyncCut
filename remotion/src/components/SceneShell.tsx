import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import type {CSSProperties, ReactNode} from "react";
import type {SyncCutScene} from "../types";
import {SectionLabel} from "./SectionLabel";

export const SceneShell = ({
  scene,
  children,
}: {
  scene: SyncCutScene;
  children: ReactNode;
}) => {
  const frame = useCurrentFrame();
  const durationFrames = Math.max(1, scene.duration_frames);
  const transitionFrames = Math.max(
    1,
    Math.min(12, Math.max(4, Math.floor(durationFrames / 4))),
  );
  const exitStart = Math.max(transitionFrames + 1, durationFrames - transitionFrames);

  const opacity =
    durationFrames <= transitionFrames * 2
      ? interpolate(frame, [0, durationFrames], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : interpolate(
          frame,
          [0, transitionFrames, exitStart, durationFrames],
          [0, 1, 1, 0],
          {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          },
        );
  const scale = interpolate(frame, [0, transitionFrames], [0.985, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame, [0, transitionFrames], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={styles.root}>
      <AbsoluteFill
        style={{
          ...styles.sceneLayer,
          opacity,
          transform: `translate3d(0, ${translateY}px, 0) scale(${scale})`,
        }}
      >
        {children}
      </AbsoluteFill>
      <div style={styles.softOverlay} />
      <SectionLabel scene={scene} />
    </AbsoluteFill>
  );
};

const styles: Record<string, CSSProperties> = {
  root: {
    overflow: "hidden",
  },
  sceneLayer: {
    transformOrigin: "50% 52%",
  },
  softOverlay: {
    position: "absolute",
    inset: 0,
    pointerEvents: "none",
    background:
      "linear-gradient(135deg, rgba(255, 255, 255, 0.035), transparent 32%, rgba(2, 6, 23, 0.12) 100%)",
    zIndex: 10,
  },
};
