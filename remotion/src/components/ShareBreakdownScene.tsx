import type {CSSProperties} from "react";
import {DataSceneFrame} from "./DataSceneFrame";
import {PlaceholderScene} from "./PlaceholderScene";
import {parseShareBreakdownData, truncateText} from "./visualData";
import type {SyncCutScene, SyncCutSection} from "../types";

export const ShareBreakdownScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => {
  const data = parseShareBreakdownData(scene.visual.data);

  if (data === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label="Share Breakdown Data Missing"
        accentColor="#f43f5e"
      />
    );
  }

  const max = Math.max(...data.items.map((item) => item.value), 1);
  const total = data.items.reduce((sum, item) => sum + item.value, 0);

  return (
    <DataSceneFrame
      scene={scene}
      section={section}
      title={data.title ?? "Share Breakdown"}
      kicker="Share Breakdown"
      accentColor="#f43f5e"
    >
      <div style={shareShellStyle}>
        <div style={summaryStyle}>
          <span>unit: {data.unit ?? "value"}</span>
          <span>items: {data.items.length}</span>
          <span>raw total: {formatValue(total, data.unit)}</span>
        </div>
        <div style={shareListStyle}>
          {data.items.map((item, index) => (
            <div key={`${item.label}-${index}`} style={shareRowStyle}>
              <div style={shareLabelStyle}>{truncateText(item.label, 72)}</div>
              <div style={shareTrackStyle}>
                <div
                  style={{
                    ...shareFillStyle,
                    width: `${Math.max(2, (item.value / max) * 100)}%`,
                  }}
                />
              </div>
              <div style={shareValueStyle}>{formatValue(item.value, data.unit)}</div>
            </div>
          ))}
        </div>
      </div>
    </DataSceneFrame>
  );
};

const formatValue = (value: number, unit: string | null) => {
  const rendered = Number.isInteger(value) ? String(value) : value.toFixed(2);
  return unit ? `${rendered}${unit}` : rendered;
};

const shareShellStyle: CSSProperties = {
  height: "100%",
  display: "grid",
  gridTemplateRows: "auto minmax(0, 1fr)",
  gap: 22,
};

const summaryStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 16,
  color: "rgba(248, 250, 252, 0.66)",
  fontSize: 22,
  lineHeight: 1.2,
  letterSpacing: 0,
};

const shareListStyle: CSSProperties = {
  minHeight: 0,
  border: "1px solid rgba(248, 250, 252, 0.14)",
  borderRadius: 8,
  backgroundColor: "rgba(248, 250, 252, 0.04)",
  padding: 28,
  display: "grid",
  gap: 18,
  alignContent: "center",
};

const shareRowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "430px minmax(0, 1fr) 110px",
  gap: 24,
  alignItems: "center",
};

const shareLabelStyle: CSSProperties = {
  color: "#fecdd3",
  fontSize: 25,
  lineHeight: 1.15,
  fontWeight: 800,
  letterSpacing: 0,
  overflowWrap: "break-word",
};

const shareTrackStyle: CSSProperties = {
  height: 30,
  borderRadius: 6,
  backgroundColor: "rgba(248, 250, 252, 0.1)",
  overflow: "hidden",
};

const shareFillStyle: CSSProperties = {
  height: "100%",
  borderRadius: 6,
  backgroundColor: "#f43f5e",
};

const shareValueStyle: CSSProperties = {
  color: "#f8fafc",
  fontSize: 24,
  lineHeight: 1,
  fontWeight: 900,
  textAlign: "right",
  letterSpacing: 0,
};
