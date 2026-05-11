export type VisualType =
  | "AI_VIDEO"
  | "B_ROLL"
  | "CHART"
  | "COMPARISON_CARD"
  | "TABLE"
  | "SHARE_BREAKDOWN"
  | "TIMELINE";

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | {[key: string]: JsonValue};

export interface SyncCutMetadata {
  generated_by: string;
  source_timeline: string;
  fps: number;
  duration_sec: number;
  duration_frames: number;
  total_scenes: number;
  total_sections: number;
}

export interface SyncCutComposition {
  id: string;
  width: number;
  height: number;
  fps: number;
  duration_frames: number;
}

export interface SyncCutAudioRef {
  path: string;
  public_path?: string;
}

export interface SyncCutAlignmentRef {
  path: string;
  match_method?: "paragraph" | "sentence" | "word_span";
  matched_units?: string[];
}

export interface SyncCutSection {
  section_key: string;
  section: string;
  section_order: number;
  start_sec: number;
  end_sec: number;
  duration_sec: number;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
  audio: SyncCutAudioRef;
  alignment: Pick<SyncCutAlignmentRef, "path">;
}

export interface SyncCutVisual {
  type: VisualType;
  prompt: string | null;
  data: JsonValue;
  public_path?: string;
  asset_status?: "prepared" | "missing" | "unsupported";
  asset_source?: "local";
}

export interface SyncCutDialogue {
  text: string;
  paragraphs: string[];
}

export interface SyncCutScene {
  id: string;
  scene_order: number;
  section: string;
  section_order: number;
  section_key: string;
  start_sec: number;
  end_sec: number;
  duration_sec: number;
  local_start_sec: number;
  local_end_sec: number;
  start_frame: number;
  end_frame: number;
  duration_frames: number;
  visual_type: VisualType;
  visual: SyncCutVisual;
  dialogue: SyncCutDialogue;
  audio: SyncCutAudioRef;
  alignment: Required<SyncCutAlignmentRef>;
  warnings: string[];
}

export interface SyncCutAudioAsset {
  section_key: string;
  path: string;
  public_path?: string;
}

export interface SyncCutAssets {
  audio: SyncCutAudioAsset[];
  visuals: JsonValue[];
}

export interface SyncCutProps {
  [key: string]: unknown;
  metadata: SyncCutMetadata;
  composition: SyncCutComposition;
  sections: SyncCutSection[];
  scenes: SyncCutScene[];
  assets: SyncCutAssets;
  warnings: string[];
}
