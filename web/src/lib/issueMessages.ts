import type { Lang } from "./i18n";

/**
 * analyzer/scoring.py compute_score()가 생성하는 한국어 진단 문구를 영문으로 번역.
 *
 * 서버 응답(analyzer/ 코어)은 절대 건드리지 않는다는 원칙 때문에, LLM이 아닌
 * 정규식 패턴 매칭으로 처리한다 — compute_score()의 메시지 템플릿은 5개 지표 ×
 * 2~3개 분기(critical/warning/good)로 개수가 고정돼 있어 정규식으로 안전하게
 * 매핑 가능하다 (자유 형식 텍스트라면 이 방식은 성립하지 않음).
 *
 * **주의**: analyzer/scoring.py의 메시지 문구가 바뀌면(golf-code-change A6 대상)
 * 이 파일의 패턴도 함께 갱신해야 한다 — 매칭 실패 시 한국어 원문을 그대로 보여주는
 * 안전한 폴백이 있으므로 화면이 깨지진 않지만, 번역이 누락된다.
 */
const PATTERNS: Array<{ re: RegExp; en: (m: RegExpMatchArray) => string }> = [
  {
    re: /^척추각 변화량 ([\-\d.]+)° — 헤드업·스웨이 위험\. 임팩트까지 척추각을 고정하세요\.$/,
    en: (m) => `Spine angle change ${m[1]}° — head-up/sway risk. Keep your spine angle fixed through impact.`,
  },
  {
    re: /^척추각 변화량 ([\-\d.]+)° — 약간의 상체 흔들림\. (\d+)° 이내 유지를 목표로 하세요\.$/,
    en: (m) => `Spine angle change ${m[1]}° — slight upper-body sway. Aim to keep it within ${m[2]}°.`,
  },
  {
    re: /^척추각 안정 \(([\-\d.]+)°\) — 견고한 회전축 유지 ✓$/,
    en: (m) => `Spine angle stable (${m[1]}°) — solid rotation axis maintained ✓`,
  },
  {
    re: /^X-Factor ([\-\d.]+)° — 어깨-골반 꼬임 부족\. 백스윙 시 어깨를 더 회전하세요\.$/,
    en: (m) => `X-Factor ${m[1]}° — insufficient shoulder-hip separation. Rotate your shoulders more on the backswing.`,
  },
  {
    re: /^X-Factor ([\-\d.]+)° — 과도한 꼬임\. (\d+)° 이하로 제한하세요\.$/,
    en: (m) => `X-Factor ${m[1]}° — excessive separation. Limit it to ${m[2]}° or below.`,
  },
  {
    re: /^X-Factor ([\-\d.]+)° — 적절한 몸통 꼬임 ✓$/,
    en: (m) => `X-Factor ${m[1]}° — good torso separation ✓`,
  },
  {
    re: /^어드레스 무릎 굴곡 부족 \(좌 ([\-\d.]+)° \/ 우 ([\-\d.]+)°\) — 지면 반력 활용이 제한됩니다\.$/,
    en: (m) => `Insufficient knee flex at address (L ${m[1]}° / R ${m[2]}°) — limits ground-force use.`,
  },
  {
    re: /^어드레스 무릎 굴곡 적절 \(좌 ([\-\d.]+)° \/ 우 ([\-\d.]+)°\) ✓$/,
    en: (m) => `Good knee flex at address (L ${m[1]}° / R ${m[2]}°) ✓`,
  },
  {
    re: /^백스윙 톱 왼팔 굽힘 \(([\-\d.]+)°\) — 백스윙 아크 손실\. 왼팔을 펴는 연습이 필요합니다\.$/,
    en: (m) => `Left arm bent at the top of backswing (${m[1]}°) — losing swing arc. Practice keeping it straight.`,
  },
  {
    re: /^백스윙 톱 왼팔 직선성 양호 \(([\-\d.]+)°\) ✓$/,
    en: (m) => `Good left-arm extension at the top of backswing (${m[1]}°) ✓`,
  },
  {
    re: /^어깨 최대 회전 ([\-\d.]+)° — 백스윙 부족으로 비거리 손실 가능성\.$/,
    en: (m) => `Max shoulder rotation ${m[1]}° — possible distance loss from an incomplete backswing.`,
  },
  {
    re: /^어깨 회전 충분 \(([\-\d.]+)°\) ✓$/,
    en: (m) => `Sufficient shoulder rotation (${m[1]}°) ✓`,
  },
];

export function translateIssueMessage(lang: Lang, koMessage: string): string {
  if (lang === "ko") return koMessage;
  for (const { re, en } of PATTERNS) {
    const match = koMessage.match(re);
    if (match) return en(match);
  }
  return koMessage; // 매칭 실패 시 한국어 원문 폴백 — 화면이 깨지지 않음
}
