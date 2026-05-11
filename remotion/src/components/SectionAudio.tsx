import {Audio, Sequence, staticFile} from "remotion";
import type {SyncCutSection} from "../types";

type SectionAudioProps = {
  sections: SyncCutSection[];
};

export const SectionAudio = ({sections}: SectionAudioProps) => {
  return (
    <>
      {sections.map((section) => {
        const publicPath = section.audio.public_path;

        if (!publicPath) {
          return null;
        }

        return (
          <Sequence
            key={section.section_key}
            from={section.start_frame}
            durationInFrames={section.duration_frames}
            layout="none"
          >
            <Audio src={staticFile(publicPath)} />
          </Sequence>
        );
      })}
    </>
  );
};
