import {AiVideoScene} from "./AiVideoScene";
import {BRollScene} from "./BRollScene";
import {ChartScene} from "./ChartScene";
import {ComparisonCardScene} from "./ComparisonCardScene";
import {PlaceholderScene} from "./PlaceholderScene";
import {ShareBreakdownScene} from "./ShareBreakdownScene";
import {TableScene} from "./TableScene";
import {TimelineScene} from "./TimelineScene";
import type {SyncCutScene, SyncCutSection} from "../types";

interface SceneRendererProps {
  scene: SyncCutScene;
  sections: SyncCutSection[];
}

export const SceneRenderer = ({scene, sections}: SceneRendererProps) => {
  const section = sections.find((item) => item.section_key === scene.section_key);
  const visualType: string = scene.visual_type;

  switch (visualType) {
    case "AI_VIDEO":
      return <AiVideoScene scene={scene} section={section} />;
    case "B_ROLL":
      return <BRollScene scene={scene} section={section} />;
    case "CHART":
      return <ChartScene scene={scene} section={section} />;
    case "COMPARISON_CARD":
      return <ComparisonCardScene scene={scene} section={section} />;
    case "TABLE":
      return <TableScene scene={scene} section={section} />;
    case "SHARE_BREAKDOWN":
      return <ShareBreakdownScene scene={scene} section={section} />;
    case "TIMELINE":
      return <TimelineScene scene={scene} section={section} />;
    default:
      return (
        <PlaceholderScene
          scene={scene}
          section={section}
          label="Unknown Visual Placeholder"
          accentColor="#f97316"
        />
      );
  }
};
