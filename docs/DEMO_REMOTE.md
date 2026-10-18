# 발표 시연 — 현재 dev의 Google 로그인·외부 접속

기준: `golf_swing` dev `e5a81a5` (2026-10-17). 이 Mac의 서버·웹을 ngrok HTTPS 주소 하나로 연결한다.
학교 PC·휴대폰은 브라우저로 접속한다. 로그인은 Google 전용이며 이메일·비밀번호 가입/로그인은 제거됐다.
별도 `golf_swing_final` 실행법인 [RUN_FINAL.md](RUN_FINAL.md)는 병합 전 환경 설명이므로 이 절차와 구분한다.

## 1. 환경 파일과 Google 콘솔

기존 환경 파일에서 아래 키를 설정한다. 값은 문서·로그에 출력하거나 커밋하지 않는다.

| 파일 | 필요한 키 |
|---|---|
| 레포 루트 `.env` | `GOOGLE_CLIENT_ID`, `JWT_SECRET`, `ANTHROPIC_API_KEY` |
| `web/.env.local` | `VITE_GOOGLE_CLIENT_ID` — 서버와 같은 Google OAuth 클라이언트 ID |

Google 콘솔에서 해당 OAuth 클라이언트의 **승인된 JavaScript 원본**에 다음 두 주소를 등록해야 한다.

- `http://localhost:4173`
- `https://tweet-isolated-civil.ngrok-free.dev`

등록 여부와 참여자 계정의 로그인 가능 여부는 **미확인**이다. OAuth 앱이 테스트 모드라면 참여자 접근 설정도 확인한다.
`VITE_GOOGLE_CLIENT_ID`는 빌드 시 반영되므로 설정을 바꾸면 웹을 다시 빌드한다.

## 2. Mac에서 실행 — 터미널 3개

먼저 포트 사용 여부를 조회한다. 출력이 없을 때만 새 프로세스를 실행한다.

```bash
lsof -nP -iTCP:8010 -iTCP:4173 -sTCP:LISTEN
```

이미 사용 중이면 기존 서버·웹·ngrok을 유지한다. 중복 실행하거나 PID를 찾아 강제 종료하지 않는다.
실행 중인 시연 웹의 `dist`를 덮어쓰는 재빌드도 피한다. 아래는 사용자가 시연 환경을 시작할 때의 명령이다.

```bash
# 1) 분석 서버 — 셸의 무효 Gemini 키를 이 프로세스에서 제외
cd ~/PycharmProjects/golf_swing/server && env -u GEMINI_API_KEY ../.venv/bin/uvicorn main:app --port 8010

# 2) 웹 — 같은 접속 주소의 /api로 요청, preview가 서버 8010으로 중계
cd ~/PycharmProjects/golf_swing/web && VITE_API_BASE=/api npm run build && npm run preview -- --port 4173 --strictPort

# 3) 외부 주소 + 잠자기 방지 — 기존 ngrok이 없을 때만 실행
caffeinate -dis ngrok http 4173
```

`env -u GEMINI_API_KEY`는 셸 설정을 삭제하지 않는다. 서버는 레포 `.env`를 읽으므로 그 파일에 무효 키를 다시 넣지 않는다.
현재 키 구성에서는 Claude 코칭을 사용한다. `VITE_API_BASE=/api`는 외부 기기가 자기 `localhost`로 API를 호출하는 일을 방지한다.
`--strictPort`는 4173이 사용 중이면 다른 포트로 자동 이동하지 않고 종료하게 한다.

ngrok 화면의 `Forwarding`이 `https://tweet-isolated-civil.ngrok-free.dev`인지 확인한다.
이 주소는 기존 시연 주소이며, 이번 세션에서 실제 터널 연결은 **미확인**이다. 다른 주소가 나오면 공유 전에 Google 원본 등록도 확인한다.

에이전트가 별도 서버를 띄워 검증해야 한다면 8020·5199 등 빈 포트를 사용한다.
단, 현재 `web/vite.config.ts`의 preview 중계 대상은 8010으로 고정되어 있어 포트 숫자만 바꿔 같은 절차를 실행하면 안 된다.

## 3. 접속 확인

아래 명령의 응답은 **기대값**이며, 실제 실행 결과와 구분한다.

```bash
curl --fail --silent --show-error http://127.0.0.1:8010/health
curl --fail --silent --show-error http://localhost:4173/api/health
```

두 요청의 기대 응답은 `{"status":"ok"}`다. 이는 서버·중계 확인이며 Google 로그인 성공을 증명하지 않는다.

학교 PC·휴대폰에서 확인할 순서:

1. 고정 HTTPS 주소 접속 → ngrok 안내가 나오면 **Visit Site** 클릭.
2. Google 버튼으로 로그인 → 앱에 로그인 상태가 표시되는지 확인.
3. 영상 업로드 → 구간 선택 → 분석 결과 → AI 코칭 → 저장·기록 조회.
4. 실시간 캠을 사용한다면 카메라 권한 허용 후 촬영·종료 확인. HTTPS 외에도 기기·브라우저 권한 확인이 필요하다.

| 확인 항목 (2026-10-17) | 상태·근거 |
|---|---|
| Google 전용 인증·시계 오차 허용 | 코드 확인: `server/main.py`, `server/auth.py` |
| 환경변수 키 존재 | `.env`와 `web/.env.local`의 위 키 이름만 확인; 값의 유효성·일치 여부는 미확인 |
| `/api` 중계·ngrok 호스트 허용 | 설정 확인: `web/vite.config.ts` |
| 8010·4173 사용 여부 | `lsof`에서 두 포트 LISTEN 확인; 실행 중인 코드·빌드 버전은 미확인 |
| Google 원본 등록·외부 로그인 성공 | 미확인 |
| 외부 업로드부터 코칭·저장까지 / 실시간 캠 | 미확인 |

## 4. Google 로그인 401과 시계 오차 수정

- 증상: Google 인증 후 `POST /auth/google`이 401, 앱에 `Google 로그인 확인에 실패했습니다.` 표시.
- 기존 기록의 원인: Mac 시계가 Google보다 약 2초 늦어 ID 토큰 발급 시각(`iat`)이 미래로 판정됨. 이번 세션에서 시계 오차를 다시 측정하지는 않았다.
- 수정: `e5a81a5`의 `server/auth.py`에서 `GOOGLE_CLOCK_SKEW_SEC = 60`을 정의하고 Google ID 토큰 검증에 `leeway=60` 적용.
- 회귀 테스트: `tests/test_api.py::test_google_credential_tolerates_small_clock_skew`는 발급 시각 +5초 허용, +600초 거부를 검사한다.
- 401이 계속되면 시스템 시각 동기화, 서버 실행 코드에 수정 반영 여부, 서버·웹 클라이언트 ID 일치 여부를 확인한다. 모든 401의 원인이 시계 오차인 것은 아니다.
- 토큰·환경변수 값은 공유하지 않는다. Google 콘솔 원본 등록 오류와 API의 401도 구분해 기록한다.

## 5. 시연 운영

- Mac 전원을 연결하고 뚜껑을 열어 둔다. `caffeinate`가 실행되는 동안 잠자기를 방지한다.
- 접속이 안 되면 학교 PC·Mac 양쪽 네트워크를 확인한다. 필요한 경우 휴대폰 핫스팟에서 재확인한다.
- 외부 시연이 어려우면 Mac 화면 직접 연결 또는 샘플 결과·준비한 시연 영상으로 대체한다.
- 시연이 끝나면 **진행자가 자신이 실행한 ngrok 터미널**에서 `Ctrl+C`로 종료한다.

평소 개발은 웹 `npm run dev`(5173)와 서버 8010을 사용한다. 현재 `/api` 중계 설정은 `vite preview`에만 적용된다.
