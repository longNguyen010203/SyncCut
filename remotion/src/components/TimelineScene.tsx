import type {CSSProperties} from "react";
import {DataSceneFrame} from "./DataSceneFrame";
import {PlaceholderScene} from "./PlaceholderScene";
import {parseTimelineData, truncateText} from "./visualData";
import type {SyncCutScene, SyncCutSection} from "../types";

export const TimelineScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => {
  const data = parseTimelineData(scene.visual.data);

  if (data === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label="Timeline Data Missing"
        accentColor="#60a5fa"
      />
    );
  }

  return (
    <DataSceneFrame
      scene={scene}
      section={section}
      title={data.title ?? "Timeline"}
      kicker="Timeline"
      accentColor="#60a5fa"
    >
      <div style={timelineShellStyle}>
        {data.events.map((event, index) => (
          <div key={`${event.date}-${event.label}-${index}`} style={eventCardStyle}>
            <div style={eventMarkerStyle}>{index + 1}</div>
            <div style={eventDateStyle}>{event.date || "Event"}</div>
            <div style={eventLabelStyle}>{truncateText(event.label || event.date, 145)}</div>
          </div>
        ))}
      </div>
    </DataSceneFrame>
  );
};

const timelineShellStyle: CSSProperties = {
  height: "100%",
  display: "grid",
  gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
  gap: 24,
  alignContent: "center",
  position: "relative",
};

const eventCardStyle: CSSProperties = {
  minWidth: 0,
  minHeight: 180,
  border: "1px solid rgba(248, 250, 252, 0.14)",
  borderRadius: 8,
  backgroundColor: "rgba(96, 165, 250, 0.1)",
  padding: "26px 28px",
  display: "grid",
  gridTemplateRows: "auto auto minmax(0, 1fr)",
  gap: 12,
};

const eventMarkerStyle: CSSProperties = {
  width: 44,
  height: 44,
  borderRadius: 22,
  backgroundColor: "#60a5fa",
  color: "#0f172a",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: 22,
  lineHeight: 1,
  fontWeight: 900,
  letterSpacing: 0,
};

const eventDateStyle: CSSProperties = {
  color: "#bfdbfe",
  fontSize: 30,
  lineHeight: 1.05,
  fontWeight: 900,
  letterSpacing: 0,
};

const eventLabelStyle: CSSProperties = {
  color: "#f8fafc",
  fontSize: 24,
  lineHeight: 1.18,
  fontWeight: 650,
  letterSpacing: 0,
  overflowWrap: "break-word",
};
