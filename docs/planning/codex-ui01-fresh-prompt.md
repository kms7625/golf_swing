# Codex 작업 지시 — UI-01 첫 화면 **새 디자인 시안** (기존 화면 비참조)

## 사용자 요청 (2026-10-08 원문)
"첫화면부터 기존 화면을 참고하지말고 코덱스로 새롭게 시안 만들어봐."

## 0. 읽어도 되는 것 / 읽으면 안 되는 것
- **읽을 것(내용·구조만):** `docs/planning/UI_STRUCTURE.md`의 UI-01 구조 카드·작업군, `docs/planning/STATE.md`의 DEC-01(첫 화면 중심 = "내 영상 바로 업로드", 샘플은 보조), `docs/planning/eval/NIELSEN_EVAL.md`의 UI-01 발견(특히 NE-15 기술 용어 중심 설명), `web/src/lib/i18n.tsx`의 UI-01 관련 문구, 지침 `05_VISUAL_APPROVAL.md` 3·4절(경로는 `docs/planning/codex-planning-agents-prompt.md` 0절)
- **열지 말 것(시각 참고 금지):** `docs/screenshots/*`, `docs/planning/eval/screens/*`, `docs/planning/mockups/*`(UI-01_r1, UI-02_r1, UI-03_r1), `web/public/images/*`, `docs/visual-candidates/*`, `web/src/index.css`·`*.module.css`(현재 색·서체 토큰), `docs/redesign-proposal.md`
- 이미지 생성 도구에 기존 이미지를 참조 입력으로 넣지 않는다

## 1. 만들 것
**UI-01 첫 화면 시안 2개 — 서로 다른 디자인 방향**, 각각 데스크톱 16:9 한 장(콜라주 금지)
- 공통 구조(DEC-01): 주 행동 "영상 업로드"가 가장 눈에 띄고 키보드 초점이 보이는 실제 버튼, 보조 행동 "샘플 데이터 보기", 상단 메뉴(실시간 캠·내 기록·테마·KO/EN·로그인), 내 스윙 기록 진입
- 대상: 스마트폰으로 자기 스윙을 찍어 보는 20대 골퍼
- 문구: i18n 실제 KO 문구를 기본으로 쓰되, NE-15에 따라 **설명문은 이용자가 얻는 결과 중심의 신규 문구 후보**를 써도 된다(브리프에 "신규 문구 후보"로 표기, i18n 수정은 하지 않음)
- 방향 A/B는 색·서체·레이아웃·그래픽 요소(사진/일러스트/데이터 시각화 등) 중 최소 3가지가 서로 다르게. 각 방향의 이름·한 줄 콘셉트·차별점을 브리프에 적는다
- 실존 인물·브랜드 로고·특정 선수 금지. 이미지 속 수치·데이터는 예시임을 브리프에 표기

## 2. 산출물 (`docs/planning/` 아래만)
- `briefs/UI-01_r2_brief.md` — 지침 05 4절 형식, A/B 각각
- `mockups/UI-01_r2a.png`, `mockups/UI-01_r2b.png`
- `briefs/UI-01_r2_review.md` — D05-06 대조(문구 오류·구조 누락·접근성 우려), 두 방향 비교 표 + 추천 1개와 이유 2문장
- 각 PNG의 치수·SHA-256

## 3. 규칙
- **`STATE.md` 수정 금지**(다른 작업이 수정 중 — 상태 기록은 사용자 측이 한다). `web/`·코드 수정·커밋 금지
- 승인 생성 금지. 생성 실패 시 실패로 보고
- 마지막 보고: 파일 경로·치수·SHA-256, 방향 A/B 요약, 추천, 사용자 질문 하나(A/B 중 선택 또는 수정 요청)
