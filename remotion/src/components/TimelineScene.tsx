import {PlaceholderScene} from "./PlaceholderScene";
import type {SyncCutScene, SyncCutSection} from "../types";

export const TimelineScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <PlaceholderScene
    scene={scene}
    section={section}
    label="Timeline Placeholder"
    accentColor="#60a5fa"
  />
);
