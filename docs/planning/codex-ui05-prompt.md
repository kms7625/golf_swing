# Codex 작업 지시 — UI-05 실시간 캠 r1 (코발트 시각 언어)

## 근거 (STATE.md state_revision 18)
- 승인된 시각 언어(DEC-03): UI-01 r2a, UI-02 r3, UI-03 r2, UI-04 r1(APR-10)
- 사용자 발화 "1번으로 진행해"(나머지 화면 한 장씩) + UI-04 "승인" 후 진행 → UI-05 **구조 동의 + 생성 요청**으로 `APR-11`(UI_STRUCTURE) 기록

## 0. 읽을 것
- 시각: `mockups/UI-01_r2a.png`~`UI-04_r1.png`(승인본), `briefs/UI-04_r1.md`
- 구조: `UI_STRUCTURE.md` UI-05 카드, ISSUE-10, `eval/NIELSEN_EVAL.md` UI-05 발견(NE-15 '온디바이스'·영문 각도 HUD, NE-20 촬영 전 준비 안내)
- 실제 기능·문구: `web/src/components/LiveCapture.tsx`, `web/src/lib/i18n.tsx`, CLAUDE.md "Live webcam analysis" 절

## 1. 할 일
1. `STATE.md`: APR-11 기록, state_revision +1
2. 브리프 `briefs/UI-05_r1.md` — 대표 상태: **촬영 중**(카메라 화면 위 관절 스켈레톤 오버레이, 실시간 지표 HUD, 녹화/종료 버튼). 반영: NE-15(쉬운 말·한글 지표 이름), NE-20(전신이 프레임에 들어오는지 등 촬영 준비 체크 표시), ISSUE-10(권한 거절·모델 실패 시 복구 경로는 브리프에 상태별 표로)
3. 이미지 생성 → `mockups/UI-05_r1.png` (데스크톱 16:9 1장). 카메라 속 인물은 실루엣/일러스트 + "이미지 예시"
4. 대조 기록 `briefs/UI-05_r1_review.md`, `asset_records`에 `ASSET-13` GENERATED + SHA-256, state_revision +1, 기존 기록 수정 금지
5. 보고 끝 질문 하나: 승인 / 수정 요청

## 2. 규칙
`docs/planning/` 밖 쓰기 금지, 코드 수정·커밋 금지, 이미지 승인 생성 금지
