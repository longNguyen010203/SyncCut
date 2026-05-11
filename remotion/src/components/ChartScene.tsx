import type {CSSProperties} from "react";
import {DataSceneFrame} from "./DataSceneFrame";
import {PlaceholderScene} from "./PlaceholderScene";
import {parseChartData, truncateText} from "./visualData";
import type {SyncCutScene, SyncCutSection} from "../types";

export const ChartScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => {
  const data = parseChartData(scene.visual.data);

  if (data === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label="Chart Data Missing"
        accentColor="#f59e0b"
      />
    );
  }

  const firstSeries = data.series[0];
  const otherSeries = data.series.slice(1).map((series) => series.name ?? "Unnamed");
  const title = data.title ?? firstSeries.name ?? "Chart";
  const isBarLike = data.chartType?.toLowerCase() === "pie";

  return (
    <DataSceneFrame
      scene={scene}
      section={section}
      title={title}
      kicker="Chart"
      accentColor="#f59e0b"
    >
      <div style={chartShellStyle}>
        <div style={chartMetaStyle}>
          <span>{data.chartType ? `type: ${data.chartType}` : "type: chart"}</span>
          {firstSeries.name ? <span>series: {firstSeries.name}</span> : null}
          {data.xLabel ? <span>x: {data.xLabel}</span> : null}
          {data.yLabel ? <span>y: {data.yLabel}</span> : null}
        </div>
        <div style={chartBodyStyle}>
          {isBarLike ? (
            <BarChart points={firstSeries.points} />
          ) : (
            <LineChart
              points={firstSeries.points}
              xLabel={data.xLabel}
              yLabel={data.yLabel}
            />
          )}
        </div>
        <div style={notesStyle}>
          {data.annotations.map((annotation, index) => (
            <span key={`annotation-${index}`}>{truncateText(annotation, 120)}</span>
          ))}
          {otherSeries.length > 0 ? (
            <span>other series: {otherSeries.map((name) => truncateText(name, 36)).join(", ")}</span>
          ) : null}
        </div>
      </div>
    </DataSceneFrame>
  );
};

const LineChart = ({
  points,
  xLabel,
  yLabel,
}: {
  points: Array<{x: string; y: number}>;
  xLabel: string | null;
  yLabel: string | null;
}) => {
  const width = 1160;
  const height = 470;
  const padding = {left: 78, right: 38, top: 32, bottom: 78};
  const values = points.map((point) => point.y);
  const min = Math.min(0, ...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const coordinates = points.map((point, index) => {
    const x =
      padding.left +
      (points.length === 1 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth);
    const y = padding.top + plotHeight - ((point.y - min) / range) * plotHeight;
    return {x, y, point};
  });
  const polyline = coordinates.map((item) => `${item.x},${item.y}`).join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} style={svgStyle}>
      <line x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + plotHeight} stroke="rgba(248,250,252,0.28)" strokeWidth={2} />
      <line x1={padding.left} y1={padding.top + plotHeight} x2={padding.left + plotWidth} y2={padding.top + plotHeight} stroke="rgba(248,250,252,0.28)" strokeWidth={2} />
      <text x={padding.left - 18} y={padding.top + 8} fill="rgba(248,250,252,0.64)" fontSize={24} textAnchor="end">
        {formatNumber(max)}
      </text>
      <text x={padding.left - 18} y={padding.top + plotHeight} fill="rgba(248,250,252,0.64)" fontSize={24} textAnchor="end">
        {formatNumber(min)}
      </text>
      <polyline points={polyline} fill="none" stroke="#fbbf24" strokeWidth={7} strokeLinejoin="round" strokeLinecap="round" />
      {coordinates.map(({x, y, point}, index) => (
        <g key={`${point.x}-${index}`}>
          <circle cx={x} cy={y} r={9} fill="#fde68a" stroke="#92400e" strokeWidth={3} />
          <text x={x} y={height - 36} fill="rgba(248,250,252,0.72)" fontSize={22} textAnchor="middle">
            {truncateText(point.x, 12)}
          </text>
          <text x={x} y={y - 18} fill="#fef3c7" fontSize={22} textAnchor="middle">
            {formatNumber(point.y)}
          </text>
        </g>
      ))}
      {xLabel ? <text x={padding.left + plotWidth / 2} y={height - 6} fill="rgba(248,250,252,0.58)" fontSize={20} textAnchor="middle">{xLabel}</text> : null}
      {yLabel ? <text x={24} y={padding.top + plotHeight / 2} fill="rgba(248,250,252,0.58)" fontSize={20} textAnchor="middle" transform={`rotate(-90 24 ${padding.top + plotHeight / 2})`}>{yLabel}</text> : null}
    </svg>
  );
};

const BarChart = ({points}: {points: Array<{x: string; y: number}>}) => {
  const max = Math.max(...points.map((point) => point.y), 1);

  return (
    <div style={barListStyle}>
      {points.map((point, index) => (
        <div key={`${point.x}-${index}`} style={barRowStyle}>
          <div style={barLabelStyle}>{truncateText(point.x, 34)}</div>
          <div style={barTrackStyle}>
            <div
              style={{
                ...barFillStyle,
                width: `${Math.max(2, (point.y / max) * 100)}%`,
              }}
            />
          </div>
          <div style={barValueStyle}>{formatNumber(point.y)}</div>
        </div>
      ))}
    </div>
  );
};

const formatNumber = (value: number) => {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
};

const chartShellStyle: CSSProperties = {
  height: "100%",
  display: "grid",
  gridTemplateRows: "auto minmax(0, 1fr) auto",
  gap: 20,
};

const chartMetaStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 14,
  color: "rgba(248, 250, 252, 0.66)",
  fontSize: 22,
  lineHeight: 1.2,
  letterSpacing: 0,
};

const chartBodyStyle: CSSProperties = {
  minHeight: 0,
  border: "1px solid rgba(248, 250, 252, 0.14)",
  borderRadius: 8,
  backgroundColor: "rgba(248, 250, 252, 0.04)",
  padding: 28,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const svgStyle: CSSProperties = {
  width: "100%",
  height: "100%",
  display: "block",
};

const notesStyle: CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: 14,
  color: "rgba(248, 250, 252, 0.64)",
  fontSize: 20,
  lineHeight: 1.2,
  letterSpacing: 0,
};

const barListStyle: CSSProperties = {
  width: "100%",
  display: "grid",
  gap: 22,
};

const barRowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "280px minmax(0, 1fr) 90px",
  gap: 22,
  alignItems: "center",
};

const barLabelStyle: CSSProperties = {
  color: "#fef3c7",
  fontSize: 28,
  lineHeight: 1.15,
  fontWeight: 800,
  letterSpacing: 0,
};

const barTrackStyle: CSSProperties = {
  height: 34,
  borderRadius: 6,
  backgroundColor: "rgba(248, 250, 252, 0.1)",
  overflow: "hidden",
};

const barFillStyle: CSSProperties = {
  height: "100%",
  borderRadius: 6,
  backgroundColor: "#f59e0b",
};

const barValueStyle: CSSProperties = {
  color: "#f8fafc",
  fontSize: 26,
  lineHeight: 1,
  fontWeight: 800,
  textAlign: "right",
  letterSpacing: 0,
};
