import {AbsoluteFill, Img, Video, staticFile, useCurrentFrame} from "remotion";
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
  const frame = useCurrentFrame();
  const asset = getPreparedVisualAsset(scene.visual.public_path);
  const phase = scene.scene_order * 0.41;
  const mediaScale = 1.014 + Math.sin(frame / 150 + phase) * 0.008;
  const translateX = Math.sin(frame / 180 + phase) * 7;
  const translateY = Math.cos(frame / 210 + phase) * 5;

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
      <AbsoluteFill
        style={{
          ...styles.mediaLayer,
          transform: `translate3d(${translateX}px, ${translateY}px, 0) scale(${mediaScale})`,
        }}
      >
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
      <div style={{...styles.edgeGlow, borderColor: accentColor}} />
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
    transformOrigin: "50% 50%",
  },
  media: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  edgeGlow: {
    position: "absolute",
    inset: 34,
    borderStyle: "solid",
    borderWidth: 1,
    borderRadius: 8,
    boxShadow:
      "0 28px 110px rgba(2, 6, 23, 0.48), inset 0 0 80px rgba(248, 250, 252, 0.045)",
    opacity: 0.5,
    pointerEvents: "none",
  },
  tint: {
    position: "absolute",
    inset: 0,
    borderStyle: "solid",
    borderWidth: 12,
    background:
      "linear-gradient(180deg, rgba(2, 6, 23, 0.64) 0%, rgba(2, 6, 23, 0.1) 42%, rgba(2, 6, 23, 0.78) 100%)",
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
