export type IssueLevel = "good" | "warning" | "critical";

export interface Issue {
  level: IssueLevel;
  message: string;
}

export interface PhaseStat {
  spine_angle: number | null;
  shoulder_rot: number | null;
  hip_rot: number | null;
  left_elbow: number | null;
  right_elbow: number | null;
  left_knee: number | null;
  right_knee: number | null;
  count: number;
}

export interface Summary {
  total_frames: number;
  spine_angle_avg: number;
  spine_angle_delta: number;
  spine_angle_min: number;
  spine_angle_max: number;
  shoulder_rotation_avg: number;
  shoulder_rotation_max: number;
  hip_rotation_avg: number;
  hip_rotation_max: number;
  x_factor: number;
  left_knee_avg: number;
  right_knee_avg: number;
  left_elbow_avg: number;
  right_elbow_avg: number;
  phases_detected: string[];
  phase_stats: Record<string, PhaseStat>;
}

export interface FrameDatum {
  frame: number;
  local_idx: number;
  time: number;
  phase: string;
  spine_angle: number;
  shoulder_rotation: number;
  hip_rotation: number;
  left_knee: number;
  right_knee: number;
  left_elbow: number;
  right_elbow: number;
}

export interface AnalyzeResponse {
  score: number;
  issues: Issue[];
  summary: Summary;
  frame_data: FrameDatum[];
  fps: number;
  eff_sample: number;
  wrist_y_history: number[];
  phase_boundaries: Record<string, [number, number]>;
  rep_frames: Record<string, string>;
}

export interface AutoWindowResponse {
  start_sec: number;
  end_sec: number;
}

export interface CoachingResponse {
  feedback: string;
}

export type Provider = "Gemini" | "Claude" | "GPT";

export const MODEL_OPTIONS: Record<Provider, string[]> = {
  Gemini: ["gemini-2.0-flash", "gemini-1.5-pro"],
  Claude: ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
  GPT: ["gpt-4o", "gpt-4o-mini"],
};

/** 서버가 보내는 한국어 페이즈명 → i18n 코드 키. 서버 응답 포맷은 불변 — 표시만 번역. */
export const PHASE_KEY_MAP: Record<string, string> = {
  "어드레스": "address",
  "백스윙": "backswing",
  "백스윙 톱": "top",
  "다운스윙": "downswing",
  "임팩트": "impact",
  "팔로우스루": "follow_through",
  "피니시": "finish",
};

export const PHASE_ORDER_KO = ["어드레스", "백스윙", "백스윙 톱", "다운스윙", "임팩트", "팔로우스루", "피니시"];

/** analyzer/drawing.py PHASE_COLORS와 대응하는 웹 표시용 색 — 파형 배경 음영 전용, 로직 무관 */
export const PHASE_COLORS: Record<string, string> = {
  "어드레스": "#96c896",
  "백스윙": "#64b4ff",
  "백스윙 톱": "#ffdc32",
  "다운스윙": "#ff8c32",
  "임팩트": "#ff3c3c",
  "팔로우스루": "#b464ff",
  "피니시": "#50dcb4",
};
