import {PlaceholderScene} from "./PlaceholderScene";
import type {SyncCutScene, SyncCutSection} from "../types";

export const ShareBreakdownScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <PlaceholderScene
    scene={scene}
    section={section}
    label="Share Breakdown Placeholder"
    accentColor="#f43f5e"
  />
);
