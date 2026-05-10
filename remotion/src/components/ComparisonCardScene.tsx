import {PlaceholderScene} from "./PlaceholderScene";
import type {SyncCutScene, SyncCutSection} from "../types";

export const ComparisonCardScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <PlaceholderScene
    scene={scene}
    section={section}
    label="Comparison Card Placeholder"
    accentColor="#a78bfa"
  />
);
