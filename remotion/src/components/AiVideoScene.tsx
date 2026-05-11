import type {SyncCutScene, SyncCutSection} from "../types";
import {VisualAssetScene} from "./VisualAssetScene";

export const AiVideoScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <VisualAssetScene
    scene={scene}
    section={section}
    assetLabel="AI Video Asset"
    placeholderLabel="AI Video Placeholder"
    accentColor="#38bdf8"
  />
);
