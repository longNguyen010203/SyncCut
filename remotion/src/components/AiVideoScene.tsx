import {PlaceholderScene} from "./PlaceholderScene";
import type {SyncCutScene, SyncCutSection} from "../types";

export const AiVideoScene = ({
  scene,
  section,
}: {
  scene: SyncCutScene;
  section?: SyncCutSection;
}) => (
  <PlaceholderScene
    scene={scene}
    section={section}
    label="AI Video Placeholder"
    accentColor="#38bdf8"
  />
);
