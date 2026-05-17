import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import type {CSSProperties} from "react";

export const AnimatedBackground = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const safeDuration = Math.max(1, durationInFrames);
  const progress = frame / safeDuration;
  const slowDrift = Math.sin(frame / 170);
  const counterDrift = Math.cos(frame / 220);
  const pulse = interpolate(Math.sin(frame / 95), [-1, 1], [0.82, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={styles.root}>
      <AbsoluteFill
        style={{
          ...styles.gradientSweep,
          opacity: interpolate(progress, [0, 0.5, 1], [0.55, 0.7, 0.58], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          transform: `translate3d(${slowDrift * 30}px, ${counterDrift * 18}px, 0) scale(${pulse})`,
        }}
      />
      <div
        style={{
          ...styles.lightField,
          left: `${-8 + slowDrift * 3}%`,
          top: `${8 + counterDrift * 4}%`,
          transform: `scale(${1.02 + progress * 0.04}) rotate(${progress * 8}deg)`,
        }}
      />
      <div
        style={{
          ...styles.lightField,
          ...styles.secondaryLightField,
          right: `${-10 + counterDrift * 4}%`,
          bottom: `${4 + slowDrift * 3}%`,
          transform: `scale(${1.04 + Math.sin(frame / 210) * 0.025}) rotate(${-8 + progress * 10}deg)`,
        }}
      />
      <AbsoluteFill style={styles.grid} />
      <AbsoluteFill style={styles.vignette} />
    </AbsoluteFill>
  );
};

const styles: Record<string, CSSProperties> = {
  root: {
    backgroundColor: "#070b12",
    overflow: "hidden",
  },
  gradientSweep: {
    inset: -120,
    background:
      "radial-gradient(circle at 16% 18%, rgba(56, 189, 248, 0.18), transparent 34%), radial-gradient(circle at 82% 72%, rgba(34, 197, 94, 0.14), transparent 30%), linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(2, 6, 23, 0.98))",
  },
  lightField: {
    position: "absolute",
    width: 760,
    height: 560,
    borderRadius: 8,
    background:
      "radial-gradient(ellipse at center, rgba(56, 189, 248, 0.22), rgba(56, 189, 248, 0.055) 48%, transparent 72%)",
    filter: "blur(10px)",
    opacity: 0.62,
  },
  secondaryLightField: {
    width: 680,
    height: 620,
    background:
      "radial-gradient(ellipse at center, rgba(168, 85, 247, 0.17), rgba(34, 197, 94, 0.055) 52%, transparent 74%)",
    opacity: 0.48,
  },
  grid: {
    opacity: 0.13,
    backgroundImage:
      "linear-gradient(rgba(248, 250, 252, 0.16) 1px, transparent 1px), linear-gradient(90deg, rgba(248, 250, 252, 0.16) 1px, transparent 1px)",
    backgroundSize: "72px 72px",
    maskImage:
      "radial-gradient(circle at center, rgba(0, 0, 0, 0.85), transparent 72%)",
  },
  vignette: {
    background:
      "radial-gradient(circle at center, transparent 36%, rgba(2, 6, 23, 0.34) 72%, rgba(2, 6, 23, 0.84) 100%)",
  },
};
