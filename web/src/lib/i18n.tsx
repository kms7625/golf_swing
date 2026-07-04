import { createContext, useContext, useState, type ReactNode } from "react";

export type Lang = "ko" | "en";

const STRINGS = {
  ko: {
    nav_analyze: "분석하기",
    nav_sample: "샘플 결과",
    hero_eyebrow: "Biomechanics · Motion Tracking",
    hero_title_1: "골프 스윙을",
    hero_title_2: "계측 장비처럼 읽는다",
    hero_lede:
      "어깨폭 정규화 좌표계와 7단계 자동 세그먼테이션 알고리즘으로 스윙을 프레임 단위 계측하고, 관절 궤적 데이터를 리포트로 변환합니다.",
    hero_cta_upload: "영상 업로드",
    hero_cta_sample: "샘플 데이터 보기",
    upload_dropzone: "MP4, MOV, AVI 파일을 드래그하거나 클릭해서 선택하세요",
    upload_detecting: "스윙 구간 자동 감지 중...",
    trim_title: "분석 구간 선택",
    trim_hint: "자동 감지된 구간을 슬라이더로 조정할 수 있습니다",
    trim_start: "시작",
    trim_end: "끝",
    trim_duration: "선택 길이",
    trim_cta: "이 구간으로 분석 시작",
    analyzing_title: "분석 중...",
    analyzing_hint: "관절 포인트 추출 → 페이즈 세그먼테이션 → 스코어 산정",
    result_score_label: "TOTAL SCORE",
    result_metric_spine: "척추각 변화",
    result_metric_xfactor: "X-FACTOR",
    result_metric_shoulder: "어깨 최대 회전",
    result_metric_phases: "감지 페이즈",
    result_issues_title: "항목별 진단",
    result_phases_title: "7단계 스윙 분석",
    result_chart_title: "손목 Y 궤적",
    result_back: "새 영상 분석하기",
    coaching_title: "AI 코칭 리포트",
    coaching_provider: "LLM 공급자",
    coaching_model: "모델",
    coaching_key: "API 키",
    coaching_key_placeholder: "API 키를 입력하세요",
    coaching_generate: "코칭 리포트 생성",
    coaching_generating: "AI가 분석 중... (10~30초 소요)",
    coaching_need_key: "API 키가 필요합니다.",
    sample_badge: "샘플 데이터",
    error_generic: "오류가 발생했습니다",
    grade: "등급",
  },
  en: {
    nav_analyze: "Analyze",
    nav_sample: "Sample Result",
    hero_eyebrow: "Biomechanics · Motion Tracking",
    hero_title_1: "Read a golf swing",
    hero_title_2: "like lab instrumentation",
    hero_lede:
      "Shoulder-width normalized coordinates and a 7-phase auto-segmentation algorithm measure your swing frame by frame and turn joint trajectories into a report.",
    hero_cta_upload: "Upload Video",
    hero_cta_sample: "View Sample Data",
    upload_dropzone: "Drag & drop or click to select an MP4, MOV, or AVI file",
    upload_detecting: "Detecting swing window automatically...",
    trim_title: "Select Analysis Range",
    trim_hint: "Adjust the auto-detected range with the sliders",
    trim_start: "Start",
    trim_end: "End",
    trim_duration: "Selected length",
    trim_cta: "Analyze This Range",
    analyzing_title: "Analyzing...",
    analyzing_hint: "Extracting joints → segmenting phases → scoring",
    result_score_label: "TOTAL SCORE",
    result_metric_spine: "Spine Angle Change",
    result_metric_xfactor: "X-FACTOR",
    result_metric_shoulder: "Max Shoulder Rotation",
    result_metric_phases: "Phases Detected",
    result_issues_title: "Diagnosis",
    result_phases_title: "7-Phase Swing Breakdown",
    result_chart_title: "Wrist-Y Trajectory",
    result_back: "Analyze Another Video",
    coaching_title: "AI Coaching Report",
    coaching_provider: "LLM Provider",
    coaching_model: "Model",
    coaching_key: "API Key",
    coaching_key_placeholder: "Enter your API key",
    coaching_generate: "Generate Coaching Report",
    coaching_generating: "AI is analyzing... (10-30s)",
    coaching_need_key: "An API key is required.",
    sample_badge: "Sample Data",
    error_generic: "Something went wrong",
    grade: "Grade",
  },
} as const;

export type StringKey = keyof (typeof STRINGS)["ko"];

const PHASE_LABELS: Record<Lang, Record<string, string>> = {
  ko: {
    address: "어드레스",
    backswing: "백스윙",
    top: "백스윙 톱",
    downswing: "다운스윙",
    impact: "임팩트",
    follow_through: "팔로우스루",
    finish: "피니시",
  },
  en: {
    address: "Address",
    backswing: "Backswing",
    top: "Top",
    downswing: "Downswing",
    impact: "Impact",
    follow_through: "Follow-through",
    finish: "Finish",
  },
};

interface I18nContextValue {
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: StringKey) => string;
  phaseLabel: (koPhaseName: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("ko");

  const t = (key: StringKey) => STRINGS[lang][key];
  const phaseLabel = (koPhaseName: string) => {
    const codeKey = PHASE_KEY_MAP_INTERNAL[koPhaseName] ?? koPhaseName;
    return PHASE_LABELS[lang][codeKey] ?? koPhaseName;
  };

  return <I18nContext.Provider value={{ lang, setLang, t, phaseLabel }}>{children}</I18nContext.Provider>;
}

const PHASE_KEY_MAP_INTERNAL: Record<string, string> = {
  "어드레스": "address",
  "백스윙": "backswing",
  "백스윙 톱": "top",
  "다운스윙": "downswing",
  "임팩트": "impact",
  "팔로우스루": "follow_through",
  "피니시": "finish",
};

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
