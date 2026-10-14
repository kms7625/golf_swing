# UI-05~08 구현 보고

2026-10-14 · `feature/ui05-08` · 기준 `release/2026-10-14` / `b8eace6c3e0b5f65b14aec44e119bdc8d82830f9`.

승인 시안 APR-12·16·17·18, 각 브리프·검토 기록, UI_STRUCTURE 3~4절, STATE의 implementation_notes·text_corrections와 기존 UI-01~04를 읽고 적용했다. `golf-ui-ux` B1~B6와 `verify-work`로 표시 범위·diff·검증 결과를 대조했다. git 커밋·스테이징은 하지 않았다.

## 완료 기준

| # | 판정 | 실행 결과·근거 |
|---|---|---|
| 1 | PASS | `cd web && npm run build` exit **0**. TypeScript와 Vite 빌드 성공. 주 청크 623.19 kB로 Vite의 500 kB 안내는 남는다. |
| 2 | PASS | `cd web && npm run lint` exit **0**. 시작 **19** → 최종 **19** 경고, 오류 0. 기존 issueMessages 14개와 Fast Refresh 5개. 새 경고 없음. |
| 3 | PASS — 지정 보고서 예외 | 구현 변경 **14개 모두 `web/src/**`**. 사용자 §5가 지정한 이 보고서만 docs에 신규 작성. 시작부터 있던 미추적 `codex-impl-ui05-08.md`는 수정하지 않았다. 아래에 문자 그대로의 범위 차이를 명시했다. |
| 4 | PASS | `dist/assets/LiveCapture-BtMoOGQ_.js` **146.27 kB** / gzip 43.94 kB, 별도 CSS **4.70 kB**. App의 `lazy(() => import(...))` 유지. |
| 5 | PASS — 비적용 | 신규 이미지 0개. `web/public/images/` 변경 없음. WebP 변환·용량 검증 대상 없음. |
| 6 | 미확인 | 360/390/1440px 가로 넘침, 라이트/다크·KO/EN, 실제 키보드·카메라·Google 로그인은 브라우저에서 실행하지 못했다. 연결된 브라우저 surface가 없고, 네이티브 Chrome 접근도 컴퓨터 사용 도구가 승인하지 않았다. |
| 7 | PASS | 지정 Docker 명령 exit **0**, **94 passed, 2 warnings in 73.13s**. 경고는 FastAPI `on_event` 사용 관련 2개. |

기준 3을 “git status의 모든 항목이 예외 없이 U1 경로 안”으로 읽으면 docs의 두 미추적 파일 때문에 그 조건 자체는 성립하지 않는다. 이번 작업의 코드 변경은 U1 안이고, 보고서 생성은 §5의 명시적 지시이며 기존 지시서는 시작 상태다. 이를 숨기거나 코드 범위를 넓히지 않았다.

회귀 검사 실행 명령:

```sh
docker run --rm --platform linux/amd64 --network none -e PYTHONDONTWRITEBYTECODE=1 -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 -e PYTHONPATH=/testdeps -v "$PWD":/work:ro -v /private/tmp/phase_testdeps:/testdeps:ro -w /work golf-server:baseline python -m pytest -p no:cacheprovider -q
```

## 화면별 구현

- **UI-05** — [LiveCapture.tsx](../../../web/src/components/LiveCapture.tsx): 영상과 상태·준비 영역의 2열 배치, 촬영 조작, 영상 밖 3개 각도 요약, 라이브 결과. 좁은 폭은 CSS상 영상 → 버튼 → 인식 상태 순. 모델 준비·권한 요청·권한 거절·카메라 사용 불가·점수 실패를 구별하고 재시도·업로드 대안을 제공한다. 녹화 상태는 실제 레코더 시작 결과로 표시하며 녹화본 없는 완료 상태에 정식 분석이 없는 이유를 설명한다. 미인식 시 이전 각도는 `—`로 표시한다.
- **UI-06** — [HistoryPanel.tsx](../../../web/src/components/HistoryPanel.tsx): 독립 제목·새 분석 → 최근 목록 → 추이 → 계정 관리. 성공 0건과 조회 실패를 분리하고 실패에 다시 불러오기를 제공한다. 1건이면 비교 자료 부족 안내. 목록과 그래프에 같은 데이터를 사용하고 0~100점 축을 표시한다. 개별 삭제는 파일·날짜·점수·삭제 범위를 보여주는 별도 확인이며 3초 재클릭 방식은 제거했다. 취소·Escape 복귀와 처리 중 표시를 추가했다.
- **UI-07** — [AuthModal.tsx](../../../web/src/components/AuthModal.tsx): 흰/남색 카드, 큰 제목, 목적 안내, Google 버튼, 처리·실패 안내, 개인정보 링크. 저장·코칭·기록 진입 목적을 전달한다. native `dialog.showModal()`로 배경 조작을 제한하고 닫기에 초기 초점, Escape 닫기, 호출 요소로 초점 복귀를 구현했다. 방침을 보는 동안 모달을 닫아 두고 복귀 시 같은 모달을 다시 표시한다.
- **UI-08** — [PrivacyPolicy.tsx](../../../web/src/components/PrivacyPolicy.tsx): 버전·읽는 목적 → 5개 앵커 목차 → 기존 본문 → 돌아가기. 제목으로 이동하면 초점도 이동한다. 본문과 기존 EN 요약은 보존했다. [App.tsx](../../../web/src/App.tsx)의 방침 표시를 별도 상태로 분리해 UI-02를 숨겨 유지하므로 선택 파일·구간이 언마운트로 초기화되지 않는다. 복귀 요소·스크롤도 기억한다.
- **화면 연결** — 기록에서 연 UI-04에 ‘기록으로 돌아가기’를 제공하고 숨긴 HistoryPanel을 유지한다. 공통 상단은 방침에서도 유지하며 실시간 캠·내 기록의 활성 메뉴를 표시한다. 저장과 코칭의 로그인 목적은 ResultScreen에서 각각 전달한다.

## 시안과의 차이·이유

1. **Google 전용**: UI-07의 이메일·비밀번호·가입 전환 폼은 만들지 않았다. 승인 시안의 제목·목적 문구 위치·여백·카드 위계를 Google 구조에 적용했고 기존 Google 공식 버튼을 유지했다. 버튼 폭과 언어만 화면에 맞게 표시하며 로그인 API·토큰 처리·성공 후 인증 동작은 바꾸지 않았다.
2. **방침 5개 항목**: 시안은 삭제된 루트 문서의 6개 항목을 사용한다. STATE 메모와 U8에 따라 현행 컴포넌트의 5개 항목·순서·법적 문구를 기준으로 삼았다. 수집 시점 등 새 법적 내용을 추가하는 표는 만들지 않고 기존 목록을 카드로 구조화했다.
3. **준비 직접 확인**: 머리·발끝·클럽 포함을 현재 KEY_JOINTS가 보증하지 않으므로 자동 전신 확인으로 바꾸지 않았다. 체크는 측정 성공 판정이나 촬영 시작 조건이 아니다.
4. **라이브 영상과 각도**: 실제 카메라를 사용하며 시안의 합성 인물·예시 수치를 넣지 않았다. 영상 시야와 좁은 폭의 순서를 위해 각도 요약은 영상 밖에 둔다. video/canvas의 동일 cover·크기·좌우 반전을 유지했다.
5. **추이 판정**: 증가·감소를 개선/악화 색으로 해석하던 표시를 제거하고 동일 텍스트 색·변화량·안내 문구로 바꿨다. 점수·지표 값·차이 계산은 그대로다.
6. **다크는 미승인 추정**: 기존 index.css의 다크 토큰을 그대로 사용했다. 라이트 기본 설정과 로컬 폰트도 유지했다. 실제 시안 픽셀 일치나 다크 승인 완료를 주장하지 않는다.

## 보존·접근성 정적 확인

- `status.ts`, `types.ts`, `api.ts`, `auth.tsx`, `geometry.ts`, `issueMessages.ts`는 HEAD와 바이트가 동일하다. server·분석 코드·tests·샘플·Android·패키지 파일 변경 없음. 다른 worktree 파일은 열람하거나 수정하지 않았다.
- LiveCapture의 카메라·모델 초기화, 감지, 각도 계산, 가시성 검사, 레코더 시작/종료, 점수 요청 **19개 주요 호출**을 TypeScript AST로 대조해 동일함을 확인했다. 가시성 결과를 표시 상태로 재사용했으며 기존 버퍼·MIN_FRAMES·MediaRecorder 설정·업로드 인자를 보존했다.
- 방침의 첫 항목부터 기존 EN 요약까지 태그·공백을 정규화한 텍스트 대조가 **동일**했다. 법적 본문은 한국어 고정이며 EN에서는 목차·조작·보조 안내만 번역한다.
- 신규 문구 **67개 키**를 KO·EN에 동시 등록했다. API 응답·단계명·샘플은 변경하지 않았다. 기준 불일치인 지표 카드 상태와 진단 판정도 그대로다.
- 새 스타일과 캔버스 색은 index.css 토큰만 참조한다. 주요 텍스트/배경 11개 조합씩 계산한 WCAG 대비 최소값: 라이트 **5.76:1**, 다크 **6.28:1**. 실제 영상 위 관절선이나 Google 공식 버튼의 대비 검증을 대신하지 않는다.
- 기존 `:focus-visible`·`prefers-reduced-motion` 규칙을 유지했다. 상태는 기호·문구를 함께 표시하고 그래프 애니메이션은 끈다. native 모달·앵커·복귀 동작은 소스 확인이며 실제 브라우저 검증은 미확인이다.
- `git diff --check` exit 0. npm 패키지·새 CDN·이미지 추가 없음. 기존 MediaPipe URL 및 Google 로그인 스크립트 로더는 유지했다.

## 남긴 자리표시·미확인

- 시행일: **‘서비스 정식 오픈일’** 그대로.
- 문의처: **‘서비스 운영자 이메일(정식 오픈 시 공지)’** 그대로.
- 본문의 비밀번호 해시 안내는 Google 전용 화면과 차이가 있지만 법적 문구 변경 금지에 따라 유지했다. 방침 책임자의 별도 검토 사항이다.
- 실제 카메라·MediaPipe·녹화 호환성, 실서비스 Google 성공/실패, 파일·구간 보존 왕복, 로그인/방침/기록의 초점 복귀는 미확인. 새로고침·탭 닫기 후 초안 복구나 라이브 정식 분석 실패 후 녹화본 복구 기능을 추가하지 않았다.
- 컴퓨터 사용 도구의 Chrome 접근 거절 문구: `Computer Use was not approved to use Google Chrome`. 상세 거절 사유는 제공되지 않았다. 우회하거나 추가 승인을 요청하지 않았다.

## 커밋 묶음 제안 — 실행하지 않음

아래는 최종 소스와 가상 중간 상태 사이의 unified patch로 계산한 **추가+삭제 합**이다. 큰 파일은 부분 스테이징을 전제로 하며 한 파일 전체를 묶지 않는다. 중간 묶음별 빌드 통과를 의미하지 않고 최종 조합만 검증했다. 지시서 미추적 파일은 이 제안에 포함하지 않는다.

| 순서 | 묶음 | 대상·분할 경계 | 추가+삭제 |
|---|---|---|---:|
| 1 | KO·EN 화면 안내 | `i18n.tsx` | 142 |
| 2 | Google 전용 모달과 초점·반응형 버튼 | `AuthModal.tsx`, `AuthModal.module.css`, `GoogleLoginButton.tsx` | 180 |
| 3 | 방침 목차·본문 재배치 | `PrivacyPolicy.tsx`, `PrivacyPolicy.module.css` | 116 |
| 4 | 복귀·화면 이동·활성 메뉴 연결 | `App.tsx`, `ResultScreen.tsx`, `TopBar.tsx`, `TopBar.module.css` | 94 |
| 5 | 라이브 상태 표시·촬영 화면 | `LiveCapture.tsx` | 128 |
| 6 | 기록 그래프·중립 증감·열기 초점 | `HistoryPanel.tsx` — 그래프·Props 및 open의 호출 초점 기억 | 26 |
| 7 | 기록 조회 상태·목록·삭제 확인 | `HistoryPanel.tsx` — 나머지 컴포넌트 상태·본문 | 200 |
| 8 | 기록 페이지·목록 스타일 | `HistoryPanel.module.css` — 파일 시작부터 ` .trendChart` 이전 | 172 |
| 9 | 기록 추이·계정 관리 스타일 | `HistoryPanel.module.css` — 해당 경계부터 파일 끝 | 134 |
| 10 | 라이브 영상·조작·준비 스타일 | `LiveCapture.module.css` — 파일 시작부터 ` .result` 이전 | 179 |
| 11 | 라이브 결과·모바일 스타일 | `LiveCapture.module.css` — 해당 경계부터 파일 끝 | 165 |
| 12 | 검증 보고 | `REPORT_ui05-08.md` 신규 | 81 |

분할 산정 근거는 `/private/tmp/ui05-08-review/group-01.patch`~`group-11.patch`와 `commit-groups.json`에 임시 보관했다. 모두 200줄 이하이며 Git 인덱스·커밋은 변경하지 않았다.
