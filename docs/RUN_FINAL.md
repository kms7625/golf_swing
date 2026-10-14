# 완성본 실행 방법 (release/2026-10-14)

중간발표 시연용(`~/PycharmProjects/golf_swing`, dev `3bdf45d`, 8010·4173·ngrok)과 **별개로** 이 Mac에서만 띄우는 완성본.
포함: Google 로그인 전용 · 단계 분할 회귀 수정 · X-Factor 3D.

| | 중간발표 시연용 | 완성본 |
|---|---|---|
| 폴더 | `~/PycharmProjects/golf_swing` | `~/PycharmProjects/golf_swing_final` |
| 서버 | 8010 | 8011 |
| 웹 | 4173 (+ ngrok 고정 주소) | 5173 (이 Mac 브라우저에서만) |
| 로그인 | 이메일 | Google |
| `.env` | 레포 루트 `.env` | 레포 루트 `.env` + `web/.env.local` (각자 따로) |

발표 중에는 완성본을 꺼둔다(분석이 CPU를 많이 써서 시연이 느려질 수 있음).

## 1. 처음 한 번 — 환경 파일

`~/PycharmProjects/golf_swing_final/.env` (커밋 금지, `.gitignore` 대상)

```
GOOGLE_CLIENT_ID=<Google OAuth 클라이언트 ID>
JWT_SECRET=<openssl rand -hex 32 결과>
ANTHROPIC_API_KEY=<Claude API 키>
```

`~/PycharmProjects/golf_swing_final/web/.env.local`

```
VITE_GOOGLE_CLIENT_ID=<위와 같은 클라이언트 ID>
```

Google 콘솔의 "승인된 JavaScript 원본"에 `http://localhost:5173`이 있어야 한다.

## 2. 실행 — 터미널 2개

포트가 비어 있는지 먼저 확인 (아무것도 안 나와야 함):

```bash
lsof -ti tcp:8011; lsof -ti tcp:5173
```

터미널 1 — 서버

```bash
cd ~/PycharmProjects/golf_swing_final/server && env -u GEMINI_API_KEY ../../golf_swing/.venv/bin/uvicorn main:app --port 8011
```

`env -u GEMINI_API_KEY`: 셸에 설정된 Gemini 키가 무효(2026-10-14 확인)라 AI 코칭 공급자 목록에서 빼기 위함. 유효한 키로 바꾸면 이 부분을 지운다.

터미널 2 — 웹 (빌드 후 미리보기)

```bash
cd ~/PycharmProjects/golf_swing_final/web && VITE_API_BASE=http://localhost:8011 npm run build && npx vite preview --port 5173 --strictPort
```

브라우저에서 `http://localhost:5173` 접속 → 로그인은 Google 버튼만 있음.

## 3. 확인

```bash
curl -s http://127.0.0.1:8011/health          # {"status":"ok"}
curl -s -o /dev/null -w "%{http_code}\n" -X POST http://127.0.0.1:8011/auth/register   # 404 (이메일 가입 제거)
```

## 4. 끄기

각 터미널에서 `Ctrl+C`. 백그라운드로 띄웠다면:

```bash
kill $(lsof -ti tcp:8011) $(lsof -ti tcp:5173)
```

## 참고

- 가상환경은 발표용 폴더의 `.venv`를 함께 쓴다(같은 의존성, 새 의존성 없음).
- 완성본 DB는 `server/golf.db`(이 폴더 전용)라 발표용 계정·기록과 섞이지 않는다.
- 외부 공개(ngrok)는 완성본에 연결하지 않았다. 필요하면 별도 ngrok 주소와 Google 원본 등록이 필요하다.
