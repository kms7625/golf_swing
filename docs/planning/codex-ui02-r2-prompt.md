# Codex 작업 지시 — UI-02 r2 (승인된 UI-01 r2a 시각 언어로 재생성)

## 근거
- 2026-10-08 사용자 "a로 가자" → UI-01 r2a 승인(APR-06), UI-01 r1 SUPERSEDED. `STATE.md` state_revision 7
- UI-02 구조 동의 APR-03, 이전 시각 언어 시안 r1 승인 APR-04 — **구조·문구·개선 사항은 유지, 시각 언어만 r2a로 교체**

## 0. 읽을 것
- 시각 기준: `docs/planning/mockups/UI-01_r2a.png`, `docs/planning/briefs/UI-01_r2_brief.md`의 방향 A(플레이 코트)
- 구조·문구 기준: `docs/planning/briefs/UI-02_r1.md`, `UI_STRUCTURE.md` UI-02 카드, `web/src/lib/i18n.tsx`(trim_detect_failed 포함 최신 문구)
- 절차: `docs/planning/codex-planning-d05-ui02-prompt.md` 2·3절
- **UI-02_r1.png는 레이아웃 참고만 가능**, 색·서체·카드 형태는 따르지 않는다

## 1. 할 일
1. 브리프 `briefs/UI-02_r2.md` — r1 대비 바뀌는 것(시각 언어)·유지되는 것(파일 변경 버튼·감지 상태·슬라이더 라벨·9:16 영상 미리보기·개인정보 안내) 표
2. 이미지 생성 → `mockups/UI-02_r2.png` (데스크톱 16:9 1장, 파일 선택 후 구간 선택 상태)
   - 영상 미리보기 속 인물은 **실사형 대신** r2a와 어울리는 처리(실루엣·흐린 처리 등)로 두거나 "이미지 예시" 표기
3. 대조 기록 `briefs/UI-02_r2_review.md`
4. `STATE.md`의 `asset_records`에 `ASSET-06`(UI-02, revision 2, GENERATED, SHA-256), state_revision +1. **기존 승인·자산 기록은 수정하지 않는다**
5. 보고 끝 질문 하나: 승인 / 수정 요청

## 2. 규칙
`docs/planning/` 밖 쓰기 금지, 코드 수정·커밋 금지, 승인 생성 금지
