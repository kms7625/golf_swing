# Codex 작업 지시 — Planning Agents v3.0 · D05 시안 (UI-03 분석 진행)

## 0. 먼저 읽을 것
- `docs/planning/codex-planning-d05-ui02-prompt.md`(직전 지시 — 3절 규칙 동일)
- `docs/planning/STATE.md`(state_revision 5, APR-01~04), `UI_STRUCTURE.md`의 UI-03 구조 카드와 ISSUE-02·11, `eval/NIELSEN_EVAL.md`의 UI-03 관련 발견
- **승인된 시안 2장이 시각 언어 기준**: `mockups/UI-01_r1.png`(APR-02), `mockups/UI-02_r1.png`(APR-04)
- 실제 코드·문구: `web/src/components/AnalyzeProgress.tsx`, `.module.css`, `web/src/lib/i18n.tsx`

## 1. 사용자 발화 근거
- 2026-10-08 "1번으로 진행해" — 직전 안내 "나머지 화면 시안 생성(P06 계속): UI-02 업로드부터 **한 장씩** 만들고 승인을 받아요"에 대한 답. UI-03 **구조 동의 + 생성 요청**으로 기록(`APR-05`, UI_STRUCTURE, 원문 그대로, 근거 설명 포함)
- 2026-10-08 "UI-02 승인하고 5번 2번만 고쳐줘. 시안작업은?" — 시안 작업 계속 확인

## 2. 할 일 (UI-02 지시서 2절과 동일 절차)
1. `STATE.md`: APR-05 기록, state_revision +1
2. 브리프 `briefs/UI-03_r1.md` — 대표 상태: **분석 진행 중**(단계 표시·진행률). 반영할 구조 개선: ISSUE-02(진행 중 이동 시 결과 처리 — 시안에서는 "취소/뒤로" 행동과 그 결과 문구를 보이게), ISSUE-11(진행 막대 이름·상태 알림). 문구는 i18n 실제 KO, 신규 문구는 후보로 표기
3. 이미지 생성 → `mockups/UI-03_r1.png` (데스크톱 16:9 1장)
4. 대조 기록 `briefs/UI-03_r1_review.md`, `ASSET-03` GENERATED + SHA-256
5. 보고 끝 질문 하나: 승인 / 수정 요청

## 3. 규칙
`docs/planning/` 밖 쓰기 금지(**`web/`은 다른 작업이 수정 중**), 코드 수정·커밋 금지, 승인 생성 금지
