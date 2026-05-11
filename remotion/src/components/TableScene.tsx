import type {CSSProperties} from "react";
import {DataSceneFrame} from "./DataSceneFrame";
import {PlaceholderScene} from "./PlaceholderScene";
import {parseTableData, truncateText} from "./visualData";
import type {SyncCutScene, SyncCutSection} from "../types";

const MAX_VISIBLE_ROWS = 6;

export const TableScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => {
  const data = parseTableData(scene.visual.data);

  if (data === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label="Table Data Missing"
        accentColor="#14b8a6"
      />
    );
  }

  const visibleRows = data.rows.slice(0, MAX_VISIBLE_ROWS);
  const hiddenRows = Math.max(0, data.rows.length - visibleRows.length);
  const gridTemplateColumns = `repeat(${data.columns.length}, minmax(0, 1fr))`;

  return (
    <DataSceneFrame
      scene={scene}
      section={section}
      title={data.title ?? "Table"}
      kicker="Table"
      accentColor="#14b8a6"
    >
      <div style={tableShellStyle}>
        <div style={{...rowStyle, ...headerRowStyle, gridTemplateColumns}}>
          {data.columns.map((column, index) => (
            <div key={`${column}-${index}`} style={headerCellStyle}>
              {truncateText(column, 64)}
            </div>
          ))}
        </div>
        <div style={bodyStyle}>
          {visibleRows.map((row, rowIndex) => (
            <div
              key={`row-${rowIndex}`}
              style={{
                ...rowStyle,
                gridTemplateColumns,
                backgroundColor:
                  rowIndex % 2 === 0
                    ? "rgba(248, 250, 252, 0.045)"
                    : "rgba(248, 250, 252, 0.025)",
              }}
            >
              {data.columns.map((_, columnIndex) => (
                <div key={`cell-${rowIndex}-${columnIndex}`} style={bodyCellStyle}>
                  {truncateText(row[columnIndex] ?? "", 150)}
                </div>
              ))}
            </div>
          ))}
        </div>
        {hiddenRows > 0 ? (
          <div style={moreRowsStyle}>+{hiddenRows} more rows</div>
        ) : null}
      </div>
    </DataSceneFrame>
  );
};

const tableShellStyle: CSSProperties = {
  height: "100%",
  minHeight: 0,
  border: "1px solid rgba(248, 250, 252, 0.14)",
  borderRadius: 8,
  overflow: "hidden",
  backgroundColor: "rgba(248, 250, 252, 0.04)",
  display: "grid",
  gridTemplateRows: "auto minmax(0, 1fr) auto",
};

const rowStyle: CSSProperties = {
  display: "grid",
  minWidth: 0,
};

const headerRowStyle: CSSProperties = {
  backgroundColor: "rgba(20, 184, 166, 0.18)",
  borderBottom: "1px solid rgba(248, 250, 252, 0.16)",
};

const headerCellStyle: CSSProperties = {
  minWidth: 0,
  padding: "24px 26px",
  color: "#99f6e4",
  fontSize: 28,
  lineHeight: 1.15,
  fontWeight: 800,
  letterSpacing: 0,
  overflowWrap: "break-word",
};

const bodyStyle: CSSProperties = {
  minHeight: 0,
  display: "grid",
  alignContent: "stretch",
};

const bodyCellStyle: CSSProperties = {
  minWidth: 0,
  padding: "22px 26px",
  borderRight: "1px solid rgba(248, 250, 252, 0.1)",
  color: "#f8fafc",
  fontSize: 25,
  lineHeight: 1.25,
  fontWeight: 600,
  letterSpacing: 0,
  overflowWrap: "break-word",
};

const moreRowsStyle: CSSProperties = {
  borderTop: "1px solid rgba(248, 250, 252, 0.12)",
  padding: "16px 24px",
  color: "rgba(248, 250, 252, 0.68)",
  fontSize: 22,
  lineHeight: 1.2,
  textAlign: "right",
  letterSpacing: 0,
};
