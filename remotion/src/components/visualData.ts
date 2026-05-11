import type {JsonValue} from "../types";

export interface ComparisonData {
  headline: string | null;
  left: {
    label: string;
    value: string;
  };
  right: {
    label: string;
    value: string;
  };
  footer: string | null;
}

export interface TableData {
  title: string | null;
  columns: string[];
  rows: string[][];
}

export interface ChartPoint {
  x: string;
  y: number;
}

export interface ChartSeries {
  name: string | null;
  points: ChartPoint[];
}

export interface ChartData {
  title: string | null;
  chartType: string | null;
  xLabel: string | null;
  yLabel: string | null;
  series: ChartSeries[];
  annotations: string[];
}

export interface TimelineData {
  title: string | null;
  events: Array<{
    date: string;
    label: string;
  }>;
}

export interface ShareBreakdownData {
  title: string | null;
  unit: string | null;
  items: Array<{
    label: string;
    value: number;
  }>;
}

export const isRecord = (
  value: JsonValue | undefined
): value is Record<string, JsonValue> => {
  return value !== null && typeof value === "object" && !Array.isArray(value);
};

export const asString = (value: JsonValue | undefined): string | null => {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }

  return null;
};

export const asNumber = (value: JsonValue | undefined): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }

  if (typeof value === "string") {
    const trimmed = value.trim();
    if (trimmed.length === 0) {
      return null;
    }

    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : null;
  }

  return null;
};

export const asArray = (value: JsonValue | undefined): JsonValue[] => {
  return Array.isArray(value) ? value : [];
};

export const getString = (
  object: Record<string, JsonValue>,
  key: string
): string | null => {
  return asString(object[key]);
};

export const getNumber = (
  object: Record<string, JsonValue>,
  key: string
): number | null => {
  return asNumber(object[key]);
};

export const getRecord = (
  object: Record<string, JsonValue>,
  key: string
): Record<string, JsonValue> | null => {
  const value = object[key];
  return isRecord(value) ? value : null;
};

export const getArray = (
  object: Record<string, JsonValue>,
  key: string
): JsonValue[] => {
  return asArray(object[key]);
};

export const stringifyCell = (value: JsonValue | undefined): string => {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "string") {
    return value.trim();
  }

  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }

  try {
    return JSON.stringify(value);
  } catch {
    return "";
  }
};

export const truncateText = (value: string, maxLength: number): string => {
  if (maxLength <= 0) {
    return "";
  }

  if (value.length <= maxLength) {
    return value;
  }

  if (maxLength <= 3) {
    return value.slice(0, maxLength);
  }

  return `${value.slice(0, maxLength - 3)}...`;
};

export const parseComparisonData = (
  data: JsonValue
): ComparisonData | null => {
  if (!isRecord(data)) {
    return null;
  }

  const left = parseComparisonSide(getRecord(data, "left"));
  const right = parseComparisonSide(getRecord(data, "right"));

  if (left === null || right === null) {
    return null;
  }

  return {
    headline: getString(data, "headline"),
    left,
    right,
    footer: getString(data, "footer"),
  };
};

export const parseTableData = (data: JsonValue): TableData | null => {
  if (!isRecord(data)) {
    return null;
  }

  const columns = getArray(data, "columns")
    .map(stringifyCell)
    .filter((column) => column.length > 0);
  const rows = getArray(data, "rows")
    .map((row) => {
      const cells = Array.isArray(row) ? row : [row];
      return cells.map(stringifyCell);
    })
    .filter((row) => row.some((cell) => cell.length > 0));

  if (columns.length === 0 || rows.length === 0) {
    return null;
  }

  return {
    title: getString(data, "title"),
    columns,
    rows,
  };
};

export const parseChartData = (data: JsonValue): ChartData | null => {
  if (!isRecord(data)) {
    return null;
  }

  const series = getArray(data, "series")
    .map(parseChartSeries)
    .filter((item): item is ChartSeries => item !== null);

  if (series.length === 0) {
    return null;
  }

  return {
    title: getString(data, "title"),
    chartType: getString(data, "chart_type"),
    xLabel: getString(data, "x_label"),
    yLabel: getString(data, "y_label"),
    series,
    annotations: parseAnnotations(getArray(data, "annotations")),
  };
};

export const parseTimelineData = (data: JsonValue): TimelineData | null => {
  if (!isRecord(data)) {
    return null;
  }

  const events = getArray(data, "events")
    .map((event) => {
      if (!isRecord(event)) {
        return null;
      }

      const date = getString(event, "date") ?? "";
      const label = getString(event, "label") ?? "";

      if (date.length === 0 && label.length === 0) {
        return null;
      }

      return {date, label};
    })
    .filter((event): event is {date: string; label: string} => event !== null);

  if (events.length === 0) {
    return null;
  }

  return {
    title: getString(data, "title"),
    events,
  };
};

export const parseShareBreakdownData = (
  data: JsonValue
): ShareBreakdownData | null => {
  if (!isRecord(data)) {
    return null;
  }

  const items = getArray(data, "items")
    .map((item) => {
      if (!isRecord(item)) {
        return null;
      }

      const label = getString(item, "label");
      const value = getNumber(item, "value");

      if (label === null || value === null) {
        return null;
      }

      return {label, value};
    })
    .filter((item): item is {label: string; value: number} => item !== null);

  if (items.length === 0) {
    return null;
  }

  return {
    title: getString(data, "title"),
    unit: getString(data, "unit"),
    items,
  };
};

const parseComparisonSide = (
  value: Record<string, JsonValue> | null
): ComparisonData["left"] | null => {
  if (value === null) {
    return null;
  }

  const label = getString(value, "label") ?? "";
  const sideValue = getString(value, "value") ?? "";

  if (label.length === 0 && sideValue.length === 0) {
    return null;
  }

  return {
    label,
    value: sideValue,
  };
};

const parseChartSeries = (value: JsonValue): ChartSeries | null => {
  if (!isRecord(value)) {
    return null;
  }

  const points = getArray(value, "points")
    .map((point, index) => {
      if (!isRecord(point)) {
        return null;
      }

      const y = getNumber(point, "y");
      if (y === null) {
        return null;
      }

      return {
        x: getString(point, "x") ?? String(index + 1),
        y,
      };
    })
    .filter((point): point is ChartPoint => point !== null);

  if (points.length === 0) {
    return null;
  }

  return {
    name: getString(value, "name"),
    points,
  };
};

const parseAnnotations = (annotations: JsonValue[]): string[] => {
  return annotations
    .map((annotation) => {
      if (isRecord(annotation)) {
        return getString(annotation, "label") ?? getString(annotation, "x") ?? "";
      }

      return stringifyCell(annotation);
    })
    .filter((annotation) => annotation.length > 0);
};
