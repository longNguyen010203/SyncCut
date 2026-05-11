import type {CSSProperties} from "react";
import {DataSceneFrame} from "./DataSceneFrame";
import {PlaceholderScene} from "./PlaceholderScene";
import {parseComparisonData, truncateText} from "./visualData";
import type {SyncCutScene, SyncCutSection} from "../types";

export const ComparisonCardScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => {
  const data = parseComparisonData(scene.visual.data);

  if (data === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label="Comparison Card Data Missing"
        accentColor="#a78bfa"
      />
    );
  }

  return (
    <DataSceneFrame
      scene={scene}
      section={section}
      title={data.headline ?? data.footer ?? "Comparison"}
      kicker="Comparison Card"
      accentColor="#a78bfa"
    >
      <div style={contentStyle}>
        <ComparisonPanel
          label={data.left.label}
          value={data.left.value}
          accentColor="#c4b5fd"
        />
        <ComparisonPanel
          label={data.right.label}
          value={data.right.value}
          accentColor="#f0abfc"
        />
      </div>
      {data.footer ? <div style={footerCaptionStyle}>{data.footer}</div> : null}
    </DataSceneFrame>
  );
};

const ComparisonPanel = ({
  label,
  value,
  accentColor,
}: {
  label: string;
  value: string;
  accentColor: string;
}) => {
  return (
    <section style={{...panelStyle, borderTop: `8px solid ${accentColor}`}}>
      <div style={{...panelLabelStyle, color: accentColor}}>
        {label || "Unlabeled"}
      </div>
      <div style={panelValueStyle}>{truncateText(value || "No value", 300)}</div>
    </section>
  );
};

const contentStyle: CSSProperties = {
  height: "100%",
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: 36,
  alignItems: "stretch",
};

const panelStyle: CSSProperties = {
  minWidth: 0,
  border: "1px solid rgba(248, 250, 252, 0.14)",
  borderRadius: 8,
  backgroundColor: "rgba(248, 250, 252, 0.055)",
  padding: "42px 44px",
  display: "flex",
  flexDirection: "column",
  justifyContent: "center",
  gap: 28,
};

const panelLabelStyle: CSSProperties = {
  fontSize: 32,
  lineHeight: 1.1,
  fontWeight: 800,
  letterSpacing: 0,
};

const panelValueStyle: CSSProperties = {
  color: "#f8fafc",
  fontSize: 44,
  lineHeight: 1.16,
  fontWeight: 700,
  letterSpacing: 0,
  overflowWrap: "break-word",
};

const footerCaptionStyle: CSSProperties = {
  marginTop: 22,
  color: "rgba(248, 250, 252, 0.68)",
  fontSize: 24,
  lineHeight: 1.25,
  textAlign: "center",
  letterSpacing: 0,
};
