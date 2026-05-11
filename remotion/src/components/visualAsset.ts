export type VisualAssetKind = "image" | "video";

export interface PreparedVisualAsset {
  kind: VisualAssetKind;
  publicPath: string;
}

const IMAGE_EXTENSIONS = new Set([".png", ".jpg", ".jpeg", ".webp"]);
const VIDEO_EXTENSIONS = new Set([".mp4", ".webm", ".mov"]);

export const getPreparedVisualAsset = (
  value: unknown,
): PreparedVisualAsset | null => {
  if (typeof value !== "string") {
    return null;
  }

  const publicPath = value.trim();
  if (!publicPath || !publicPath.startsWith("visuals/") || publicPath.includes("..")) {
    return null;
  }

  const extension = extensionOf(publicPath);
  if (extension === null) {
    return null;
  }

  if (IMAGE_EXTENSIONS.has(extension)) {
    return {kind: "image", publicPath};
  }

  if (VIDEO_EXTENSIONS.has(extension)) {
    return {kind: "video", publicPath};
  }

  return null;
};

const extensionOf = (publicPath: string): string | null => {
  const filename = publicPath.split("/").pop();
  if (!filename) {
    return null;
  }

  const dotIndex = filename.lastIndexOf(".");
  if (dotIndex <= 0 || dotIndex === filename.length - 1) {
    return null;
  }

  return filename.slice(dotIndex).toLowerCase();
};
