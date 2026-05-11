import type {SyncCutScene, SyncCutSection} from "../types";
import {VisualAssetScene} from "./VisualAssetScene";

export const BRollScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <VisualAssetScene
    scene={scene}
    section={section}
    assetLabel="B-roll Asset"
    placeholderLabel="B-roll Placeholder"
    accentColor="#22c55e"
  />
);
