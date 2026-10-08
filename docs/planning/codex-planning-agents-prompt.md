# Codex 작업 지시 — Planning Agents v3.0 절차로 Swing.Lab 웹 화면 설계 (1단계: D04 화면 구조)

## 0. 지침 원문 (먼저 읽을 것, 읽지 못한 것을 읽었다고 쓰지 말 것)
경로: `/Users/mose/Library/Mobile Documents/com~apple~CloudDocs/Desktop/obsidian/mose/08_study/AI인력양성프로그램/Planning_Agents_v3.0/`
- `PROJECT_INSTRUCTIONS.txt`, `01_PROJECT_MD/00_ORCHESTRATOR.md`, `90_SHARED_CONTRACTS.md` — 총괄·공통 계약(ID 체계 `UI-`·`REQ-`·`DEC-`·`ASSET-`, revision, 상태 DRAFT 등)
- `01_PROJECT_MD/04_UX_STRUCTURE.md` — **이번 단계의 주 담당 D04**(3절 "화면별 구조 카드" 형식을 그대로 쓴다)
- `01_PROJECT_MD/05_VISUAL_APPROVAL.md` — 다음 단계(D05) 입력 형식 확인용
- `01_PROJECT_MD/06_WEB.md` — 웹 담당 D06 보조

## 1. 대상
이 레포의 웹(`web/`) — Swing.Lab 골프 스윙 분석기. 지침은 "신규 개발" 원칙이지만, 이번은 **사용자가 기존 제품에 지침 절차를 적용하라고 명시**했다. 기존 화면·코드는 "현재 상태(사실)"로 기록하고, 지침 절차로 구조를 다시 점검한다. 기존 디자인(Club Lime)을 승인된 시안으로 승계하지 않는다(지침 05 5절: 이전 승인 자동 승계 금지).

## 2. 이번 단계 범위 — D04-01 ~ D04-09만
1. `web/src/App.tsx`와 `web/src/components/*.tsx`를 읽어 **현재 실제 화면·흐름·상태**를 사실대로 정리(코드 근거 파일명 표기)
2. D04 3절 구조 카드로 UI 목록 작성: 최소 UI-01 첫 화면, UI-02 업로드·구간 선택, UI-03 분석 진행, UI-04 결과, UI-05 실시간 캠, UI-06 내 기록, UI-07 로그인, UI-08 개인정보처리방침. 각 카드에 빈·로딩·오류·성공·권한 없음 상태와 좁은 화면(360px) 재배치 포함
3. 화면 흐름(진입·이동·뒤로·완료)을 표 또는 mermaid로. 막다른 경로가 있으면 표시
4. 지침 기준으로 본 **현재 구현의 구조상 빈틈**(예: 상태 화면 누락, 막다른 경로, 키보드 초점) — 코드 근거와 함께. 고칠 방법은 제안만
5. D04-09: 사용자에게 **구조 선택 질문 딱 하나** (예: "첫 화면에서 바로 업로드를 시작하게 할까요, 샘플 결과를 먼저 보여줄까요?" 같은 제품 목적에 영향을 주는 선택). 추천과 이유 1~2문장

## 3. 규칙
- 산출물은 `docs/planning/` 안에만: `UI_STRUCTURE.md`(구조 카드·흐름·빈틈·질문), `STATE.md`(지침 90 형식의 최소 상태: project_id, state_revision=1, 상태 DRAFT, UI 목록과 각 revision, 미결 질문)
- `web/`·`server/`·기타 코드 수정 금지. 이미지 생성 금지(구조 동의 전 시안 생성은 지침 위반). git 커밋 금지
- 숫자(px·색)는 승인 전이므로 "제안값"이라고 표기
- 확인 못 한 것은 "미확인"

## 4. 보고
- 읽은 지침 파일 목록, 만든 파일, UI 개수, 발견한 빈틈 개수와 상위 3개, 사용자에게 할 질문 하나(추천 포함)
