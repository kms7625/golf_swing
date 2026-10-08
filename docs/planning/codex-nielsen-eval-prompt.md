# Codex 작업 지시 — Nielsen 10 사용성 원칙 휴리스틱 평가 (Planning Agents D14 형식)

## 0. 먼저 읽을 것
- 원칙 원문: Nielsen Norman Group 공식 글 "10 Usability Heuristics for User Interface Design"과 심각도 척도 글 "Severity Ratings for Usability Problems"를 **웹에서 직접 열어** 확인하고 URL·확인일을 적는다. 열지 못하면 "원문 미확인"으로 적고 기억으로 정의를 쓰지 않는다
- Planning Agents 지침 `01_PROJECT_MD/14_QA_SIMULATION.md`(경로는 `docs/planning/codex-planning-agents-prompt.md` 0절), `90_SHARED_CONTRACTS.md`의 TEST·ISSUE 형식
- `docs/planning/UI_STRUCTURE.md`(UI-01~08, ISSUE-01~12) — **이미 찾은 빈틈과 중복 판정**
- 평가 대상
  1. 현재 앱: `docs/planning/eval/screens/*.jpg`(2026-10-08 실제 화면 캡처: 첫 화면 다크/라이트·1440/390/360px, 업로드, 결과, 구간 선택, 다시보기) + 코드 `web/src/App.tsx`, `web/src/components/*.tsx`, `web/src/lib/i18n.tsx`
  2. 승인된 시안: `docs/planning/mockups/UI-01_r1.png`(APR-02)
  3. (있으면) `docs/planning/mockups/UI-02_r1.png` — 생성 중일 수 있음. 없으면 평가 제외하고 그렇게 적는다

## 1. 산출물 — `docs/planning/eval/NIELSEN_EVAL.md` 한 파일
1. 원칙 출처(URL·확인일)와 심각도 척도(0~4) 정의
2. 원칙 10개 × 화면별 표: `원칙 / UI ID / 발견 / 근거(스크린샷 파일명 또는 코드 파일:줄) / 심각도 0~4 / 기존 ISSUE와의 관계(신규·ISSUE-nn과 동일·보강) / 개선 제안`
3. 현재 앱 vs 승인 시안(UI-01 r1) 비교: 시안이 해결한 문제 / 시안에도 남은 문제 / 시안이 새로 만든 문제
4. 상위 5개(심각도·사용 빈도 기준) + 중간발표(2026-10-15) 전에 고칠 가치가 있는 것 표시
5. 지침 형식 TEST 후보(`TEST-` 정상/실패·경계 시나리오) — STATE.md에는 쓰지 말고 이 파일 안에 "제안"으로만

## 2. 규칙
- **쓰기 허용: `docs/planning/eval/NIELSEN_EVAL.md` 한 파일.** `STATE.md`는 다른 작업이 수정 중이므로 절대 수정 금지. 코드 수정·커밋 금지
- 심각도는 근거 없이 매기지 않는다. 스크린샷이나 코드로 확인 안 된 것은 "미확인"
- 실제 사용자 테스트가 아님을 문서 첫 줄에 명시(전문가 휴리스틱 평가 1인)

## 3. 보고
원칙 출처 확인 여부, 발견 수(신규/기존 중복), 심각도 분포, 상위 5개
