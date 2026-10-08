# Codex 작업 지시 — Planning Agents v3.0 · D05 시안 (UI-02 업로드·구간 선택)

## 0. 먼저 읽을 것
- `docs/planning/codex-planning-d05-prompt.md`(이전 UI-01 지시 — 0·3절 규칙 동일 적용)
- `docs/planning/STATE.md`(state_revision 3, APR-01·APR-02), `UI_STRUCTURE.md`의 UI-02 구조 카드와 ISSUE-01·03·06·11
- 승인된 UI-01 시안 `docs/planning/mockups/UI-01_r1.png`(APR-02) — **시각 언어 기준**(색 역할·서체 느낌·카드 모서리·버튼 형태)
- 실제 UI-02 코드·문구: `web/src/components/UploadTrim.tsx`, `UploadTrim.module.css`, `web/src/lib/i18n.tsx`, 현재 화면 참고 `docs/research`가 아닌 `docs/screenshots/`

## 1. 사용자 발화 (2026-10-08)
직전 안내 "UI-02 업로드부터 한 장씩 만들고 승인을 받아요"에 대한 답: **"1번으로 진행해"** → UI-02 **구조 동의 + 시안 생성 요청**(지침 04 6절). 시안 승인은 아님.

## 2. 할 일
1. `STATE.md`: UI-02 구조 동의를 `APR-03`(UI_STRUCTURE, 원문 "1번으로 진행해")으로 기록, `state_revision` +1
2. 브리프 `docs/planning/briefs/UI-02_r1.md`(지침 05 4절 형식). 대표 상태는 **파일 선택 후 구간 선택 상태** 하나(빈 드롭존 상태는 이번 생성 제외 — 브리프에 다음 revision 후보로만 기록)
   - 반영할 구조 개선(제안이며 기능 추가 아님, 기존 기능 범위 안): ISSUE-03 키보드로 접근 가능한 "파일 선택/변경" 버튼, ISSUE-01 **파일 변경** 버튼, ISSUE-06 자동 구간 감지 상태 문구(감지 중/완료/실패 시 수동 조정 안내), ISSUE-11 슬라이더 라벨
   - 문구는 `i18n.tsx`의 실제 KO 문구. 새 문구가 필요하면 브리프에 "신규 문구 후보"로 표기
   - 9:16 세로 영상 미리보기(실제 테스트 영상이 세로) + 시작/끝 슬라이더 + 선택 길이 + 주 버튼 "이 구간으로 분석 시작" + 개인정보 안내
   - 데스크톱 16:9 1 장
3. 이미지 생성 → `docs/planning/mockups/UI-02_r1.png`
4. D05-06 대조 → `docs/planning/briefs/UI-02_r1_review.md`(문구 오류·배치 차이·UI-01 시각 언어와의 불일치)
5. `STATE.md`에 `ASSET-02`(GENERATED, SHA-256) 기록
6. 보고 끝에 사용자 질문 하나: 승인 / 수정 요청

## 3. 규칙
`docs/planning/` 밖 쓰기 금지, 코드 수정·커밋 금지, 승인 생성 금지(APPROVED는 사용자 발화로만), 생성 실패 시 실패로 보고
