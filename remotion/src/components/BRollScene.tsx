import {PlaceholderScene} from "./PlaceholderScene";
import type {SyncCutScene, SyncCutSection} from "../types";

export const BRollScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <PlaceholderScene
    scene={scene}
    section={section}
    label="B-roll Placeholder"
    accentColor="#22c55e"
  />
);
