import {AbsoluteFill} from "remotion";
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
};

const shellStyle: CSSProperties = {
  width: "100%",
  height: "100%",
  display: "grid",
  gridTemplateRows: "auto minmax(0, 1fr) auto",
  gap: 28,
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
  const sectionLabel = section
    ? `${section.section_key} / ${section.section}`
    : scene.section_key;

  return (
    <AbsoluteFill style={frameStyle}>
      <div style={shellStyle}>
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
