import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import type {CSSProperties} from "react";
import type {JsonValue, SyncCutScene, SyncCutSection} from "../types";

interface PlaceholderSceneProps {
  scene: SyncCutScene;
  section?: SyncCutSection;
  label: string;
  accentColor?: string;
}

const truncate = (value: string, maxLength: number) => {
  if (value.length <= maxLength) {
    return value;
  }

  return `${value.slice(0, maxLength - 3)}...`;
};

const summarizeJson = (value: JsonValue) => {
  if (value === null) {
    return "No visual data";
  }

  return truncate(JSON.stringify(value), 360);
};

const panelStyle: CSSProperties = {
  width: "82%",
  maxWidth: 1460,
  border: "1px solid rgba(255, 255, 255, 0.16)",
  borderRadius: 8,
  background: "rgba(16, 19, 22, 0.86)",
  boxShadow: "0 24px 80px rgba(0, 0, 0, 0.32)",
  padding: "54px 60px",
};

const eyebrowStyle: CSSProperties = {
  fontSize: 24,
  lineHeight: 1.2,
  fontWeight: 700,
  letterSpacing: 0,
  textTransform: "uppercase",
};

const titleStyle: CSSProperties = {
  margin: "18px 0 20px",
  fontSize: 72,
  lineHeight: 1,
  fontWeight: 800,
  letterSpacing: 0,
};

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 24,
  marginTop: 32,
};

const infoBoxStyle: CSSProperties = {
  border: "1px solid rgba(255, 255, 255, 0.12)",
  borderRadius: 8,
  background: "rgba(255, 255, 255, 0.045)",
  padding: "22px 24px",
  minHeight: 126,
};

const labelStyle: CSSProperties = {
  marginBottom: 10,
  color: "rgba(244, 247, 251, 0.58)",
  fontSize: 20,
  lineHeight: 1.2,
  fontWeight: 700,
  letterSpacing: 0,
};

const valueStyle: CSSProperties = {
  fontSize: 26,
  lineHeight: 1.35,
  letterSpacing: 0,
  overflowWrap: "break-word",
};

export const PlaceholderScene = ({
  scene,
  section,
  label,
  accentColor = "#38bdf8",
}: PlaceholderSceneProps) => {
  const frame = useCurrentFrame();
  const durationFrames = Math.max(1, scene.duration_frames);
  const transitionFrames = Math.max(
    1,
    Math.min(14, Math.max(5, Math.floor(durationFrames / 5))),
  );
  const panelOpacity = interpolate(frame, [0, transitionFrames], [0.72, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const panelTranslate = interpolate(frame, [0, transitionFrames], [16, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const prompt = scene.visual.prompt
    ? truncate(scene.visual.prompt, 320)
    : "No visual prompt";
  const dialogue = truncate(scene.dialogue.text, 420);
  const dataSummary = summarizeJson(scene.visual.data);
  const sectionLabel = section
    ? `${section.section_key} · ${section.section}`
    : scene.section_key;

  return (
    <AbsoluteFill
      style={{
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#111827",
        color: "#f8fafc",
        padding: 48,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          ...backgroundAccentStyle,
          borderColor: accentColor,
        }}
      />
      <div
        style={{
          ...panelStyle,
          borderTop: `10px solid ${accentColor}`,
          opacity: panelOpacity,
          transform: `translate3d(0, ${panelTranslate}px, 0)`,
        }}
      >
        <div style={{...eyebrowStyle, color: accentColor}}>{label}</div>
        <div style={titleStyle}>{scene.id}</div>
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 14,
            color: "rgba(248, 250, 252, 0.76)",
            fontSize: 25,
            lineHeight: 1.25,
            letterSpacing: 0,
          }}
        >
          <span>{scene.visual_type}</span>
          <span>{sectionLabel}</span>
          <span>
            frames {scene.start_frame}-{scene.end_frame} ({scene.duration_frames})
          </span>
          <span>
            {scene.start_sec.toFixed(3)}s-{scene.end_sec.toFixed(3)}s
          </span>
        </div>
        <div style={gridStyle}>
          <InfoBox label="Dialogue" value={dialogue} />
          <InfoBox label="Visual Prompt" value={prompt} />
          <InfoBox label="Visual Data" value={dataSummary} />
          <InfoBox label="Audio Metadata" value={scene.audio.path} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const backgroundAccentStyle: CSSProperties = {
  position: "absolute",
  inset: 64,
  borderStyle: "solid",
  borderWidth: 1,
  borderRadius: 8,
  background:
    "radial-gradient(circle at 18% 12%, rgba(56, 189, 248, 0.12), transparent 34%), radial-gradient(circle at 88% 86%, rgba(168, 85, 247, 0.1), transparent 32%)",
  boxShadow: "0 30px 110px rgba(2, 6, 23, 0.36)",
  opacity: 0.48,
  pointerEvents: "none",
};

const InfoBox = ({label, value}: {label: string; value: string}) => {
  return (
    <div style={infoBoxStyle}>
      <div style={labelStyle}>{label}</div>
      <div style={valueStyle}>{value}</div>
    </div>
  );
};
