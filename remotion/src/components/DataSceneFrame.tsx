import {AbsoluteFill, interpolate, useCurrentFrame} from "remotion";
import type {CSSProperties, ReactNode} from "react";
import type {SyncCutScene, SyncCutSection} from "../types";

interface DataSceneFrameProps {
  scene: SyncCutScene;
  section?: SyncCutSection;
  title: string;
  kicker: string;
  accentColor: string;
  children: ReactNode;
}

const frameStyle: CSSProperties = {
  backgroundColor: "#101316",
  color: "#f8fafc",
  fontFamily:
    "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
  padding: 56,
  overflow: "hidden",
};

const shellStyle: CSSProperties = {
  position: "relative",
  width: "100%",
  height: "100%",
  display: "grid",
  gridTemplateRows: "auto minmax(0, 1fr) auto",
  gap: 28,
  border: "1px solid rgba(248, 250, 252, 0.12)",
  borderRadius: 8,
  backgroundColor: "rgba(2, 6, 23, 0.36)",
  boxShadow: "0 30px 120px rgba(2, 6, 23, 0.36)",
  padding: 34,
  overflow: "hidden",
};

const headerStyle: CSSProperties = {
  display: "flex",
  alignItems: "flex-end",
  justifyContent: "space-between",
  gap: 32,
  borderBottom: "1px solid rgba(248, 250, 252, 0.14)",
  paddingBottom: 24,
};

const kickerStyle: CSSProperties = {
  marginBottom: 12,
  fontSize: 24,
  lineHeight: 1.1,
  fontWeight: 800,
  letterSpacing: 0,
  textTransform: "uppercase",
};

const titleStyle: CSSProperties = {
  margin: 0,
  maxWidth: 1320,
  fontSize: 64,
  lineHeight: 1.04,
  fontWeight: 800,
  letterSpacing: 0,
};

const sectionStyle: CSSProperties = {
  maxWidth: 360,
  color: "rgba(248, 250, 252, 0.66)",
  fontSize: 22,
  lineHeight: 1.25,
  textAlign: "right",
  letterSpacing: 0,
};

const contentStyle: CSSProperties = {
  minHeight: 0,
};

const footerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: 24,
  borderTop: "1px solid rgba(248, 250, 252, 0.12)",
  paddingTop: 18,
  color: "rgba(248, 250, 252, 0.6)",
  fontSize: 20,
  lineHeight: 1.2,
  letterSpacing: 0,
};

export const DataSceneFrame = ({
  scene,
  section,
  title,
  kicker,
  accentColor,
  children,
}: DataSceneFrameProps) => {
  const frame = useCurrentFrame();
  const durationFrames = Math.max(1, scene.duration_frames);
  const transitionFrames = Math.max(
    1,
    Math.min(14, Math.max(5, Math.floor(durationFrames / 5))),
  );
  const shellOpacity = interpolate(frame, [0, transitionFrames], [0.78, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shellTranslate = interpolate(frame, [0, transitionFrames], [14, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const sectionLabel = section
    ? `${section.section_key} / ${section.section}`
    : scene.section_key;

  return (
    <AbsoluteFill style={frameStyle}>
      <div style={backgroundAccentStyle} />
      <div
        style={{
          ...shellStyle,
          opacity: shellOpacity,
          transform: `translate3d(0, ${shellTranslate}px, 0)`,
        }}
      >
        <header style={headerStyle}>
          <div>
            <div style={{...kickerStyle, color: accentColor}}>{kicker}</div>
            <h1 style={titleStyle}>{title}</h1>
          </div>
          <div style={sectionStyle}>{sectionLabel}</div>
        </header>
        <main style={contentStyle}>{children}</main>
        <footer style={footerStyle}>
          <span>{scene.id}</span>
          <span>{scene.visual_type}</span>
          <span>
            frames {scene.start_frame}-{scene.end_frame} ({scene.duration_frames})
          </span>
        </footer>
      </div>
    </AbsoluteFill>
  );
};

const backgroundAccentStyle: CSSProperties = {
  position: "absolute",
  inset: 34,
  borderRadius: 8,
  background:
    "radial-gradient(circle at 18% 16%, rgba(56, 189, 248, 0.11), transparent 36%), radial-gradient(circle at 84% 82%, rgba(168, 85, 247, 0.1), transparent 34%)",
  pointerEvents: "none",
};
