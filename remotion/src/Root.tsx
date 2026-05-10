import {Composition} from "remotion";
import {defaultProps} from "./props";
import type {SyncCutProps} from "./types";
import {Video} from "./Video";

export const RemotionRoot = () => {
  return (
    <Composition<any, SyncCutProps>
      id={defaultProps.composition.id}
      component={Video}
      durationInFrames={defaultProps.composition.duration_frames}
      fps={defaultProps.composition.fps}
      width={defaultProps.composition.width}
      height={defaultProps.composition.height}
      defaultProps={defaultProps}
    />
  );
};
