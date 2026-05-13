import {AbsoluteFill, Img, Video, staticFile} from "remotion";
import type {CSSProperties} from "react";
import type {SyncCutScene, SyncCutSection} from "../types";
import {PlaceholderScene} from "./PlaceholderScene";
import {getPreparedVisualAsset} from "./visualAsset";

export const VisualAssetScene = ({
  scene,
  section,
  assetLabel,
  placeholderLabel,
  accentColor,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
  assetLabel: string;
  placeholderLabel: string;
  accentColor: string;
}) => {
  const asset = getPreparedVisualAsset(scene.visual.public_path);

  if (asset === null) {
    return (
      <PlaceholderScene
        scene={scene}
        section={section}
        label={placeholderLabel}
        accentColor={accentColor}
      />
    );
  }

  return (
    <AbsoluteFill style={styles.frame}>
      <AbsoluteFill style={styles.mediaLayer}>
        {asset.kind === "image" ? (
          <Img src={staticFile(asset.publicPath)} style={styles.media} />
        ) : (
          <Video
            src={staticFile(asset.publicPath)}
            muted
            loop
            style={styles.media}
          />
        )}
      </AbsoluteFill>
      <div style={{...styles.tint, borderColor: accentColor}} />
      <div style={styles.header}>
        <div style={{...styles.kicker, color: accentColor}}>{assetLabel}</div>
        <div style={styles.title}>{scene.id}</div>
      </div>
      <div style={{...styles.metadata, borderColor: accentColor}}>
        <span>{scene.visual_type}</span>
        <span>{section?.section_key ?? scene.section_key}</span>
        <span>{asset.publicPath}</span>
      </div>
    </AbsoluteFill>
  );
};

const styles: Record<string, CSSProperties> = {
  frame: {
    backgroundColor: "#0b1020",
    color: "#f8fafc",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    overflow: "hidden",
  },
  mediaLayer: {
    backgroundColor: "#020617",
  },
  media: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  tint: {
    position: "absolute",
    inset: 0,
    borderStyle: "solid",
    borderWidth: 12,
    background:
      "linear-gradient(180deg, rgba(2, 6, 23, 0.72) 0%, rgba(2, 6, 23, 0.12) 42%, rgba(2, 6, 23, 0.78) 100%)",
    pointerEvents: "none",
  },
  header: {
    position: "absolute",
    top: 56,
    left: 72,
    right: 72,
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  kicker: {
    fontSize: 34,
    fontWeight: 800,
    lineHeight: 1,
    textTransform: "uppercase",
  },
  title: {
    fontSize: 76,
    fontWeight: 900,
    lineHeight: 1,
    textShadow: "0 8px 28px rgba(0, 0, 0, 0.6)",
  },
  metadata: {
    position: "absolute",
    left: 72,
    right: 72,
    bottom: 52,
    display: "grid",
    gridTemplateColumns: "220px 260px minmax(0, 1fr)",
    gap: 22,
    alignItems: "center",
    borderLeftStyle: "solid",
    borderLeftWidth: 8,
    backgroundColor: "rgba(2, 6, 23, 0.78)",
    padding: "20px 26px",
    fontSize: 28,
    fontWeight: 700,
    lineHeight: 1.15,
    overflow: "hidden",
  },
};
