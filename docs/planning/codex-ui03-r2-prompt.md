# Codex 작업 지시 — UI-03 r2 (신규 시각 언어로 재생성)

## 근거 (STATE.md state_revision 11)
- 승인된 시각 언어: UI-01 r2a(APR-06), UI-02 r3(APR-07)
- UI-03 구조 동의 APR-05. r1(ASSET-03)은 이전 시각 언어, 승인 보류
- 유지할 구조(r1에서 사용자에게 좋은 평가로 안내된 것): 처리 단계 목록(업로드→구간 자르기→관절 추적·7단계 구분→점수 계산→완료)과 현재 단계 강조, 이름 있는 진행 막대·수치, **"뒤로 가기" + 결과 안내 문구**(ISSUE-02)

## 0. 읽을 것
`mockups/UI-01_r2a.png`, `mockups/UI-02_r3.png`, `briefs/UI-02_r3.md`(시각 언어), `briefs/UI-03_r1.md`·`mockups/UI-03_r1.png`(구조·문구만, 색·형태는 따르지 않음), `web/src/components/AnalyzeProgress.tsx`, `web/src/lib/i18n.tsx`

## 1. 할 일
1. 브리프 `briefs/UI-03_r2.md`(r1 대비 유지·변경 표). UI-02 r3처럼 과감한 코발트 강조와 굵은 숫자(진행률) 사용
2. 이미지 생성 → `mockups/UI-03_r2.png` (데스크톱 16:9 1장, 분석 진행 중 상태)
3. 대조 기록 `briefs/UI-03_r2_review.md`
4. `STATE.md` `asset_records`에 `ASSET-08` GENERATED + SHA-256, state_revision +1, 기존 기록 수정 금지
5. 보고 끝 질문 하나: 승인 / 수정 요청

## 2. 규칙
`docs/planning/` 밖 쓰기 금지, 코드 수정·커밋 금지, 승인 생성 금지. 실사형 인물 금지
