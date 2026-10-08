# Codex 작업 지시 — Planning Agents v3.0 · D04-10 기록 + D05 첫 시안 (UI-01)

## 0. 먼저 읽을 것
- `docs/planning/codex-planning-agents-prompt.md` 0절의 지침 파일들(특히 `04_UX_STRUCTURE.md` 6·7절, `05_VISUAL_APPROVAL.md` 전체, `90_SHARED_CONTRACTS.md`의 승인·자산 기록 형식)
- `docs/planning/UI_STRUCTURE.md`, `docs/planning/STATE.md`
- `web/src/lib/i18n.tsx`(UI-01 실제 문구), `web/src/components/Hero.tsx`·`TopBar.tsx`, `docs/screenshots/hero.jpg`(현재 화면), `web/public/images/hero-swing-916.webp`(현재 캐릭터 자산)

## 1. 사용자 결정 (2026-10-08, 원문: "내 영상 바로 업로드로 진행해")
- D04-09 질문 "첫 화면의 중심을 '내 영상 바로 업로드'와 '샘플 결과 먼저 체험' 중 어디에 둘까요?"에 대한 답 → **내 영상 바로 업로드**(샘플은 보조 버튼)
- 이 답은 **구조 동의 + 다음 단계(시안 생성) 진행 요청**이다. 시안 승인이 아니다.

## 2. 할 일
1. `STATE.md` 갱신: `DEC-01` 기록(질문·답 원문·날짜), UI-01 구조 revision 확정, `state_revision` +1. 상태는 DRAFT 유지
2. D05 3절 순서대로 **UI-01 첫 화면 시안 1장만** 생성(다른 화면·콜라주 금지)
   - 생성 브리프는 D05 4절 형식으로 `docs/planning/briefs/UI-01_r1.md`에 먼저 작성: 화면 목적 / 첫 행동(내 영상 업로드) / 데스크톱 16:9(1440×900 기준) / 상단·주 영역·보조 영역 배치 / **i18n.tsx의 실제 KO 문구 그대로** / 유지할 것(Club Lime 색 역할, 9:16 캐릭터 패널, HTML 계측 문구) / 바꿀 것(ISSUE-03 반영: 업로드는 이름 있는 실제 버튼, 키보드 초점이 보이게; 샘플은 보조 버튼)
   - 이미지 생성 도구로 생성 → `docs/planning/mockups/UI-01_r1.png`
3. D05-06: 생성 결과와 브리프를 대조해 **문구 오류·배치 차이** 목록 작성(생성 이미지 속 글자가 틀리면 문구표로 교정 사항만 기록)
4. `STATE.md`에 `ASSET-01` 기록: UI ID·revision·역할(시안)·파일·형식·치수·작성 주체(Codex 이미지 생성)·SHA-256·상태 **GENERATED**(APPROVED 아님)
5. 사용자에게 할 말: 시안 경로 + "승인 / 수정 요청" 중 무엇인지 묻는 질문 하나

## 3. 규칙
- 쓰기 가능: `docs/planning/` 아래만. `web/`·`server/` 등 코드 수정 금지, git 커밋 금지
- 승인을 만들지 않는다(사용자 발화 없이는 APPROVED 금지)
- 생성 도구 실패 시 "실패"로 보고, 다른 파일로 대체 금지
- 확인 못 한 것은 "미확인"

## 4. 보고
STATE 변경 요약(DEC-01·ASSET-01·revision), 브리프 경로, 시안 경로·치수·SHA-256, 문구/배치 차이 목록, 사용자 질문 하나
