import {interpolate, useCurrentFrame} from "remotion";
import type {CSSProperties} from "react";
import type {SyncCutScene} from "../types";

export const SectionLabel = ({scene}: {scene: SyncCutScene}) => {
  const frame = useCurrentFrame();
  const durationFrames = Math.max(1, scene.duration_frames);
  const transitionFrames = Math.max(
    1,
    Math.min(12, Math.max(4, Math.floor(durationFrames / 4))),
  );
  const primary = scene.section_key || scene.section || scene.visual_type || scene.id;
  const secondary = scene.section && scene.section !== primary ? scene.section : null;
  const opacity = interpolate(frame, [0, transitionFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const translateY = interpolate(frame, [0, transitionFrames], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        ...styles.wrapper,
        opacity: opacity * 0.92,
        transform: `translate3d(0, ${translateY}px, 0)`,
      }}
    >
      <div style={styles.primaryRow}>
        <span>{primary}</span>
        <span style={styles.dot} />
        <span>{scene.visual_type || scene.id}</span>
      </div>
      <div style={styles.secondaryRow}>
        {secondary ? <span>{secondary}</span> : null}
        <span>scene {scene.scene_order || scene.id}</span>
      </div>
    </div>
  );
};

const styles: Record<string, CSSProperties> = {
  wrapper: {
    position: "absolute",
    right: 42,
    top: 34,
    zIndex: 12,
    maxWidth: 620,
    border: "1px solid rgba(248, 250, 252, 0.14)",
    borderRadius: 8,
    backgroundColor: "rgba(2, 6, 23, 0.58)",
    boxShadow: "0 18px 50px rgba(2, 6, 23, 0.24)",
    padding: "14px 18px",
    pointerEvents: "none",
    backdropFilter: "blur(10px)",
  },
  primaryRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    color: "#f8fafc",
    fontSize: 21,
    lineHeight: 1.1,
    fontWeight: 800,
    letterSpacing: 0,
    textTransform: "uppercase",
  },
  secondaryRow: {
    marginTop: 7,
    display: "flex",
    flexWrap: "wrap",
    gap: 12,
    color: "rgba(248, 250, 252, 0.62)",
    fontSize: 16,
    lineHeight: 1.15,
    fontWeight: 650,
    letterSpacing: 0,
  },
  dot: {
    width: 5,
    height: 5,
    borderRadius: 5,
    backgroundColor: "rgba(248, 250, 252, 0.5)",
  },
};
