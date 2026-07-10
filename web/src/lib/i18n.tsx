import { createContext, useContext, useState, type ReactNode } from "react";

export type Lang = "ko" | "en";

const STRINGS = {
  ko: {
    nav_analyze: "분석하기",
    nav_sample: "샘플 결과",
    nav_live: "실시간 캠",
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
    live_title: "실시간 웹캠 분석",
    live_hint: "온디바이스로 관절각을 실시간 계측합니다. 스윙이 끝나면 '촬영 종료'를 눌러 7단계 구간을 확인하세요.",
    live_loading: "카메라·모델 로딩 중...",
    live_start: "촬영 시작",
    live_stop: "촬영 종료",
    live_processing: "구간 분석 중...",
    live_too_short: "촬영 시간이 너무 짧습니다. 스윙 전체가 보이도록 다시 시도해주세요.",
    nav_history: "내 기록",
    auth_login: "로그인",
    auth_logout: "로그아웃",
    auth_title_login: "로그인",
    auth_title_register: "회원가입",
    auth_email: "이메일",
    auth_password: "비밀번호 (8자 이상)",
    auth_submit_login: "로그인",
    auth_submit_register: "가입하기",
    auth_to_register: "계정이 없나요? 가입하기",
    auth_to_login: "이미 계정이 있나요? 로그인",
    auth_close: "닫기",
    history_title: "내 스윙 기록",
    history_empty: "저장된 스윙이 아직 없습니다. 분석 결과 화면에서 '결과 저장'을 누르면 여기에 쌓입니다.",
    history_login_hint: "로그인하면 분석 결과를 저장하고 변화를 추적할 수 있습니다.",
    history_delete: "삭제",
    history_open: "보기",
    save_swing: "결과 저장",
    save_done: "저장됨 ✓",
    save_login_required: "로그인하고 저장",
    job_stage_uploaded: "업로드 완료",
    job_stage_trimming: "스윙 구간 자르기",
    job_stage_analyzing: "관절 포즈 추적·7단계 구분",
    job_stage_scoring: "점수 계산",
    job_stage_done: "완료",
    coaching_login_required: "AI 코칭은 로그인 후 무료로 이용할 수 있습니다.",
    coaching_remaining: "이번 달 남은 무료 코칭",
    privacy_notice: "업로드한 영상은 분석 직후 서버에서 즉시 삭제되며, 원본은 보관되지 않습니다.",
    privacy_link: "개인정보처리방침",
    privacy_back: "돌아가기",
    theme_toggle: "밝은/어두운 테마 전환",
    trend_title: "내 성장 그래프",
    trend_metrics: "지표별 추이 (처음 → 최근)",
    account_delete: "회원 탈퇴 (모든 기록 삭제)",
    account_delete_confirm: "정말 탈퇴할까요? 계정과 저장된 스윙이 모두 삭제되며 되돌릴 수 없습니다.",
    account_delete_yes: "탈퇴 확정",
    account_delete_cancel: "취소",
  },
  en: {
    nav_analyze: "Analyze",
    nav_sample: "Sample Result",
    nav_live: "Live Cam",
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
    live_title: "Live Webcam Analysis",
    live_hint: "Joint angles are measured on-device in real time. Press \"Stop\" when the swing ends to see the 7-phase breakdown.",
    live_loading: "Loading camera & model...",
    live_start: "Start Capture",
    live_stop: "Stop Capture",
    live_processing: "Segmenting phases...",
    live_too_short: "Capture was too short. Try again with the full swing in frame.",
    nav_history: "My Swings",
    auth_login: "Log in",
    auth_logout: "Log out",
    auth_title_login: "Log in",
    auth_title_register: "Sign up",
    auth_email: "Email",
    auth_password: "Password (8+ characters)",
    auth_submit_login: "Log in",
    auth_submit_register: "Sign up",
    auth_to_register: "No account? Sign up",
    auth_to_login: "Already have an account? Log in",
    auth_close: "Close",
    history_title: "My Swing History",
    history_empty: "No saved swings yet. Press 'Save Result' on an analysis to build your history.",
    history_login_hint: "Log in to save results and track your progress.",
    history_delete: "Delete",
    history_open: "Open",
    save_swing: "Save Result",
    save_done: "Saved ✓",
    save_login_required: "Log in to save",
    job_stage_uploaded: "Upload complete",
    job_stage_trimming: "Trimming swing window",
    job_stage_analyzing: "Tracking pose · segmenting 7 phases",
    job_stage_scoring: "Scoring",
    job_stage_done: "Done",
    coaching_login_required: "AI coaching is free after login.",
    coaching_remaining: "Free coaching left this month",
    privacy_notice: "Uploaded videos are deleted from the server right after analysis — originals are never stored.",
    privacy_link: "Privacy Policy",
    privacy_back: "Back",
    theme_toggle: "Toggle light/dark theme",
    trend_title: "My Progress",
    trend_metrics: "Metric trends (first → latest)",
    account_delete: "Delete account (erases all data)",
    account_delete_confirm: "Really delete? Your account and all saved swings will be permanently removed.",
    account_delete_yes: "Confirm deletion",
    account_delete_cancel: "Cancel",
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
