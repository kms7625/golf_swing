# Codex 작업 지시 — UI-04 결과 화면 r1 (코발트 시각 언어)

## 근거 (STATE.md state_revision 15)
- 승인된 시각 언어(DEC-03, 코발트): UI-01 r2a(APR-06), UI-02 r3(APR-07), UI-03 r2(APR-08)
- 사용자 발화: "1번으로 진행해"(나머지 화면 한 장씩 시안·승인), "이걸로 진행"(코발트 3장 선택) → UI-04 **구조 동의 + 생성 요청**으로 `APR-09`(UI_STRUCTURE) 기록

## 0. 읽을 것
- 시각: `mockups/UI-01_r2a.png`, `mockups/UI-02_r3.png`, `mockups/UI-03_r2.png`, `briefs/UI-02_r3.md`
- 구조: `UI_STRUCTURE.md` UI-04 카드, ISSUE-07·12, `eval/NIELSEN_EVAL.md`의 UI-04 발견(특히 NE-15: X-FACTOR·손목 Y 등 용어 설명 부족)
- 실제 기능·문구: `web/src/components/ResultScreen.tsx`, `Waveform.tsx`, `SwingReplay.tsx`, `CompareSection.tsx`, `CoachingPanel.tsx`, `web/src/lib/i18n.tsx`, `web/src/lib/status.ts`
- 참고(결정 아님): `docs/research/04_swinglab_implications.md` P5(X-Factor 감점 재검토)

## 1. 할 일
1. `STATE.md`: APR-09 기록, state_revision +1
2. 브리프 `briefs/UI-04_r1.md` — **첫 화면(스크롤 전)에 보이는 영역**을 대표 상태로: 총점·등급, 핵심 지표 4개(상태 기호 ✓/⚠/✕ 유지), 진단 목록, 7단계 대표 장면 줄. 스크롤 아래(손목 파형·다시보기·비교·AI 코칭·공유/저장)는 순서·역할만 표로
   - 반영: NE-15(지표 이름 옆 짧은 설명 또는 도움말 아이콘), ISSUE-07(저장/공유 버튼 상태)
   - **X-Factor 표시 방식은 바꾸지 말 것** — P5는 사용자 미결정. 브리프에 "결정 필요" 항목으로만 기록
3. 이미지 생성 → `mockups/UI-04_r1.png` (데스크톱 16:9 1장). 장면 썸네일 인물은 실루엣·"이미지 예시"
4. 대조 기록 `briefs/UI-04_r1_review.md`, `asset_records`에 `ASSET-12` GENERATED + SHA-256, state_revision +1. 기존 기록 수정 금지
5. 보고 끝 질문 하나: 승인 / 수정 요청

## 2. 규칙
`docs/planning/` 밖 쓰기 금지, 코드 수정·커밋 금지, 승인 생성 금지(APR-09 구조 동의 기록은 1절 근거로 허용)
