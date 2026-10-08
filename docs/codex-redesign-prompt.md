# Codex 작업 지시 — Swing.Lab 웹 리디자인 (20대 타깃)

## 0. 먼저 읽을 것 (읽기 전에 코드 수정 금지)
1. `CLAUDE.md` — 특히 "`web/` package" 섹션
2. `.claude/skills/golf-ui-ux/SKILL.md` — "B. `web/` React 프론트엔드" 절(B1~B6)
3. `web/src/index.css` — 현재 디자인 토큰(다크 기본 + `:root[data-theme="light"]` 라이트 오버라이드)
4. `docs/screenshots/hero.jpg`, `docs/screenshots/result.jpg` — 현재 화면

## 1. 목적과 배경
- 앱: 골프 스윙 영상을 올리면 자세를 분석해 점수·7단계 구간·대표 프레임·AI 코칭을 보여주는 웹앱(React 19 + Vite + TS, `web/`). 같은 빌드를 Capacitor로 감싼 Android 앱도 있다.
- 현재 디자인은 "모션 랩"(그래파이트 배경 + 코퍼/틸 액센트 + 모노스페이스 계측기 느낌). 기능은 완성됐고, **외형만** 20대 사용자가 쓰고 싶고 공유하고 싶어지는 방향으로 바꾼다.
- 기능·데이터·API는 이번 작업 범위가 아니다.

## 2. 진행 방식 — 2단계, 1단계 끝에서 반드시 멈춘다

### 1단계: 시안 2개 제안 (코드 커밋 없음)
아래를 담은 `docs/redesign-proposal.md` 하나만 작성하고 **멈춰서 사용자 선택을 기다린다.**
- 시안 A·B 각각:
  - 한 줄 콘셉트와 참고한 실제 서비스 성향(예: 스포츠·피트니스·공유형 앱)
  - 토큰 표: `index.css`의 기존 토큰 이름(`--graphite`, `--graphite-2`, `--graphite-3`, `--steel`, `--copper`, `--teal`, `--alert`, `--ok`, `--text`, `--font-display`, `--font-mono`)별 다크/라이트 값. 새 토큰이 필요하면 추가 목록을 따로 적는다
  - 본문 텍스트 대비율(다크·라이트 각각, 계산값 명시)
  - 히어로·결과 화면이 어떻게 달라지는지 3~5줄
  - 폰트: 이름, 라이선스(OFL 등), 로딩 방식
- 두 시안 비교 표 1개 + 추천 1개와 이유 2문장 이내

### 2단계: 선택된 시안 구현 (사용자가 시안을 고른 뒤에만)
- 컴포넌트 단위로 나눠 커밋하고, **커밋당 변경 200줄 이하**(초과가 불가피하면 커밋 전에 사용자에게 묻는다)
- 권장 순서: ① `index.css` 토큰·폰트 → ② `TopBar`·`Hero` → ③ `UploadTrim`·`AnalyzeProgress` → ④ `ResultScreen`·`Waveform`·`SwingReplay` → ⑤ `CoachingPanel`·`CompareSection`·`HistoryPanel`·`AuthModal`·`PrivacyPolicy` → ⑥ `LiveCapture` → ⑦ `lib/shareCard.ts`(공유 카드 색·서체만)

## 3. 반드시 지킬 것 (위반 시 실패)
| # | 규칙 | 근거 |
|---|---|---|
| R1 | 수정 가능 경로는 `web/src/**/*.css`, `web/src/components/*.tsx`의 마크업·className, `web/src/lib/shareCard.ts`의 색·폰트, `web/src/lib/i18n.tsx`(문자열 추가), `web/public/fonts/`(신규), `web/index.html`의 `<head>`, 그리고 산출물인 `docs/redesign-proposal.md`·`docs/screenshots/*.jpg`뿐이다. `server/`, `golf_swing_analyzer/`, `tests/`, `web/public/samples/`, `web/android/`는 건드리지 않는다 | 분석 코어 보존 원칙 |
| R2 | `web/src/lib/types.ts`의 `PHASE_COLORS`, `PHASE_KEY_MAP`, `MODEL_OPTIONS`와 `status.ts`, `api.ts`, `geometry.ts`, `issueMessages.ts`의 로직은 변경 금지 | B1·B4, `analyzer/drawing.py`와 색 동기화 |
| R3 | **npm 패키지 추가 금지**(애니메이션·UI 라이브러리 포함). 필요하면 이름과 이유만 제안서에 적는다. 웹폰트는 OFL 등 재배포 가능한 woff2 파일을 `web/public/fonts/`에 두고 `@font-face`로만 로드(외부 CDN 금지), 라이선스 파일도 같이 둔다 | 의존성 추가 금지 규칙 |
| R4 | 색은 `var(--*)` 토큰으로만. 컴포넌트 CSS에 테마 색 하드코딩 금지. 다크·라이트 두 테마 모두 갱신 | CLAUDE.md `web/` 규칙 |
| R5 | 새 UI 문자열은 `i18n.tsx`의 `STRINGS`에 **KO·EN 둘 다** 추가하고 `t()`로 참조. 페이즈명은 `phaseLabel()` | B3 |
| R6 | 상태(good/warn/crit)는 색만으로 구분하지 않는다 — 기존 `statusIcon()`(✓/⚠/✕) 유지 | 접근성 |
| R7 | 본문 텍스트 대비 4.5:1 이상, 큰 글씨·아이콘 3:1 이상(두 테마 모두) | WCAG AA |
| R8 | 애니메이션은 CSS만 쓰고, `@media (prefers-reduced-motion: reduce)`에서 꺼진다 | 접근성 |
| R9 | `LiveCapture`는 lazy-load 유지(메인 번들에 mediapipe 청크가 섞이면 실패) | CLAUDE.md |
| R10 | 기능·화면 흐름·컴포넌트 구성 추가/삭제 금지. 레이아웃·간격·서체·색·모서리·그림자·마이크로 인터랙션만 바꾼다 | 범위 고정 |

## 4. 완료 기준 (모두 만족해야 완료)
1. `cd web && npm run build` exit 0
2. `cd web && npm run lint` exit 0
3. `git diff --stat e973fb6..HEAD`(리디자인 시작 직전 커밋)에 R1 허용 경로 외 파일이 없다
4. `npm run build` 결과에서 `LiveCapture`가 별도 청크로 남아 있다(빌드 로그의 청크 목록으로 확인)
5. 화면 폭 390px(모바일)과 1440px(데스크톱)에서 가로 스크롤이 없다 — 히어로, 업로드, 결과, 기록 화면
6. 다크/라이트 토글, KO/EN 토글을 모두 눌러도 원문 키 노출이나 색 깨짐이 없다
7. "샘플 데이터 보기"로 결과 화면(점수·메트릭·진단 목록·손목Y 파형·7단계 프레임·비교·코칭 패널)이 렌더링된다 — 서버 없이 확인 가능. **다시보기(`SwingReplay`)는 실제 업로드 때만 표시되는 게 정상 동작**이므로 샘플 기준에서 제외하고, 확인했다면 실제 업로드로 따로 보고한다(못 했으면 "미확인")
8. `docs/screenshots/hero.jpg`, `docs/screenshots/result.jpg`를 새 디자인으로 다시 찍어 교체(README가 참조함)

## 5. 마지막 보고 형식
- 완료 기준 1~8 각각 PASS/FAIL과 근거(명령 출력 요약 또는 스크린샷 경로)
- 커밋 목록(해시·메시지·변경 줄 수)
- R3에 따라 제안만 하고 추가하지 않은 패키지/폰트가 있으면 목록
- 확인하지 못한 항목은 "미확인"으로 표기 — 확인하지 않은 것을 통과로 쓰지 않는다

## 참고 — 알려진 사항
- 백그라운드 탭(`document.visibilityState === "hidden"`)에서는 Chrome이 `<video>` 로딩을 미뤄 업로드 미리보기·다시보기가 로딩 상태로 멈출 수 있다. 화면을 앞으로 띄운 상태에서 확인하고, 이 현상을 디자인 버그로 고치려 하지 않는다.
