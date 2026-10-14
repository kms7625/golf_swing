# Codex 구현 지시 — 승인 시안 UI-05~08 적용 (브랜치 `feature/ui05-08`, 기준 `release/2026-10-14` b8eace6)

## 0. 배경
- UI-01~04는 `codex-impl-ui01-04.md`로 이미 적용(코발트). 이번은 남은 4화면: UI-05 실시간 캠, UI-06 내 기록, UI-07 로그인, UI-08 개인정보처리방침
- 작업 폴더는 이 worktree(`~/PycharmProjects/golf_swing_ui`)만. **`~/PycharmProjects/golf_swing`(중간발표 시연용)과 `golf_swing_final`, 다른 worktree는 읽지도 쓰지도 않는다**
- 로그인은 이미 **Google 로그인 전용**으로 바뀌었다(`AuthModal.tsx`, `GoogleLoginButton.tsx`). UI-07 시안의 이메일·비밀번호 폼은 **만들지 않는다** — 시안의 시각 언어(배치·색·여백·제목·안내 문구 위치)만 Google 버튼 구조에 적용

## 1. 먼저 읽을 것
- 승인 시안: `docs/planning/mockups/UI-05_r1.png`(APR-12), `UI-06_r1.png`(APR-16), `UI-07_r1.png`(APR-17), `UI-08_r1.png`(APR-18)와 `docs/planning/briefs/UI-05_r1.md`~`UI-08_r1.md`, 각 `_review.md`
- `docs/planning/UI_STRUCTURE.md` 3절 UI-05~08(현재·제안), 4절 흐름
- `docs/planning/STATE.md`의 `implementation_notes`, `text_corrections`
- 이미 적용된 UI-01~04 코드와 `web/src/index.css` 토큰 — 같은 시각 언어 유지
- `docs/planning/impl/codex-impl-ui01-04.md` 2절 규칙 G1~G9 (아래 2절이 우선)

## 2. 규칙 (위반 시 실패)
| # | 규칙 |
|---|---|
| U1 | 수정 가능: `web/src/**`, `web/public/images/`(신규 이미지). `server/`, `golf_swing_analyzer/`, `tests/`, `web/public/samples/`, `web/android/` 금지 |
| U2 | 점수·판정·인증 로직 변경 금지: `status.ts`·`types.ts`·`api.ts`·`auth.tsx`·`geometry.ts`·`issueMessages.ts` 로직 그대로. 서버 API 계약 변경 금지. 표시(문구·배치·색·상태 분기 표시)와 화면 이동만 |
| U3 | npm 패키지 추가 금지, 외부 CDN 금지(Google 로그인 스크립트는 기존 그대로) |
| U4 | 색은 `index.css` 토큰만. 라이트 기본, 다크는 기존 추정 토큰 사용 |
| U5 | 새 문구는 `i18n.tsx`에 KO·EN 동시 |
| U6 | 접근성: 대비 4.5:1, 키보드 초점 표시, 상태는 색+기호, `prefers-reduced-motion` 존중. UI-07 모달: Escape 닫기·초기 초점·닫은 뒤 초점 복귀 |
| U7 | `LiveCapture` lazy-load 유지. 카메라·MediaPipe 로직(각도 계산·녹화·업로드)은 그대로, 상태 표시·배치만 |
| U8 | 개인정보처리방침의 **법적 문구 내용을 지어내지 않는다** — 기존 본문을 재배치·구조화만. 문의처·시행일이 자리표시면 자리표시 그대로 두고 보고서에 남김 |
| U9 | git 커밋하지 않는다. 보고에 커밋 묶음 제안(묶음당 200줄 이하, 추가+삭제 합) |

## 3. 화면별 구현
- **UI-05 실시간 캠:** 시안 배치(준비 상태 → 영상 → 촬영 조작 → 결과). 카메라 권한 거절/사용 불가를 일반 오류와 구별해 안내 + "다시 시도"·"영상 업로드로 분석"(UI-02) 버튼. 녹화 불가 환경이면 정식 분석 버튼이 없는 이유 표시. 360px에서 영상 → 버튼 → 인식 상태 순
- **UI-06 내 기록:** 독립 화면 제목 + "새 분석" 버튼 → 최근 기록 목록 → 추이 → 분리된 계정 관리(탈퇴). 0건과 조회 실패를 구별(실패에는 "다시 불러오기"), 1건이면 추이 비교 부족 안내. 결과(UI-04)를 기록에서 열었으면 "기록으로 돌아가기"
- **UI-07 로그인:** Google 전용 모달에 시안의 시각 언어 적용. 로그인 이유(진입 목적: 저장·코칭·기록) 보조 문구, 처리 중 문구, 실패 문구, 개인정보 안내 링크(UI-08)
- **UI-08 개인정보처리방침:** 버전·목적 → 항목 목차(앵커 이동) → 본문 → 돌아가기. **UI-02에서 열었다가 돌아와도 선택한 파일·구간이 유지**되게(언마운트 대신 오버레이/숨김 등 화면 이동 방식으로) — U2 범위 안에서

## 4. 완료 기준 (직접 실행해 결과 기록)
1. `cd web && npm run build` exit 0
2. `cd web && npm run lint` exit 0, 경고 수가 시작 시점 이하
3. `git status --short` 변경이 U1 경로 안
4. `LiveCapture` 별도 청크 유지(빌드 산출물로 확인)
5. 신규 이미지가 있으면 WebP ≤ 250KB
6. 브라우저 확인이 가능하면 360/390/1440px 가로 넘침 없음, 라이트/다크·KO/EN — 불가하면 "미확인"
7. Docker 기준 pytest 회귀 없음(서버·분석 코드는 안 건드리므로 확인용): 
   `docker run --rm --platform linux/amd64 --network none -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -e PYTHONPATH=/testdeps -v "$PWD":/work:ro -v /private/tmp/phase_testdeps:/testdeps:ro -w /work golf-server:baseline python -m pytest -p no:cacheprovider -q`

## 5. 보고 (`docs/planning/impl/REPORT_ui05-08.md`)
기준 1~7 PASS/FAIL/미확인 + 근거, 화면별 구현 요약, 시안과 다르게 한 점과 이유(특히 UI-07 Google 전용 적용), 자리표시로 남긴 항목, 커밋 묶음 제안
