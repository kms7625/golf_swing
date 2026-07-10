# 실행 방법

같은 분석 코어(`golf_swing_analyzer/analyzer/`)를 공유하는 두 개의 프론트엔드가 있습니다.

## 1. Streamlit (레퍼런스 구현, 회귀 검증 기준)

```bash
pip install -r golf_swing_analyzer/requirements.txt
streamlit run golf_swing_analyzer/app_v2.py
```

## 2. React 웹앱 + FastAPI 백엔드 (현재 개발 중인 앱)

터미널 2개가 필요합니다.

**터미널 1 — API 서버** (`analyzer/`를 직접 import, Streamlit과 동일한 분석 코어 사용)

```bash
pip install -r server/requirements.txt
cd server && uvicorn main:app --port 8010
```

**터미널 2 — 프론트엔드**

```bash
cd web && npm install && npm run dev   # http://localhost:5173
```

두 프론트엔드 모두 실행 시 사용자가 직접 Gemini/Claude/GPT API 키를 입력해야 합니다(코드에 저장되지 않음).
Gemini가 기본값이며 무료 티어가 있습니다.

### 빌드/린트 (`web/`)

```bash
npm run build     # tsc -b && vite build
npm run lint       # oxlint
npm run preview
```

## 3. Android (Capacitor 래퍼, 개발 전용)

`web/` 빌드를 그대로 감싼 네이티브 셸입니다. 별도 앱 코드는 없습니다.

```bash
cd web && npm run build:android           # .env.capacitor로 빌드 + npx cap sync android
cd android && ./gradlew.bat installDebug  # 또는 `npx cap open android`로 Android Studio에서 실행
```

- Android Studio + SDK 필요
- `JAVA_HOME`은 Android Studio 번들 JBR(예: `C:\Android\Android Studio\jbr`)을 가리켜도 됩니다 (시스템 JDK 없어도 됨)
- 에뮬레이터/기기가 로컬 FastAPI 개발 서버(`10.0.2.2:8010`)에 접근하는 **로컬 개발 전용 브릿지**이므로, 서버와 에뮬레이터가 같은 머신에서 실행돼야 합니다
- 실기기에서 쓰려면 서버를 `0.0.0.0`으로 바인딩하고 `VITE_API_BASE`를 에뮬레이터용 `10.0.2.2` 대신 개발 머신의 LAN IP로 바꿔야 합니다
- iOS는 Windows 환경에서는 Xcode가 없어 지원 범위 밖입니다

## 5. 테스트 (2026-07-10 추가)

```bash
pip install pytest httpx
python -m pytest              # 전체 (analyzer 스냅샷 포함, ~15초)
python -m pytest tests/test_api.py   # 서버 계약만 빠르게
```

- 서버 테스트는 임시 SQLite로 격리 실행 — 실 DB(.env)와 섞이지 않습니다
- `analyzer/`를 의도적으로 변경했다면 `python tests/regen_snapshot.py`로 기준값을 재생성해 함께 커밋

## 참고

- 심층 회귀 검증(3영상 전체·시각 비교)은 여전히 `golf-analysis-quality` 스킬로 수동 수행합니다
  (자동 스냅샷은 일반.mp4 1종의 최소 게이트)
- 아키텍처와 각 패키지 역할은 [`CLAUDE.md`](./CLAUDE.md)에 정리돼 있습니다

## 4. 프로덕션 배포 (Docker, 2026-07-10 추가)

`.env.example`을 `.env`로 복사해 채운 뒤:

```bash
docker compose up -d --build
# web: http://localhost:8080 / api: 127.0.0.1:8010 (로컬 바인딩)
```

- **HTTPS**: compose는 TLS를 직접 처리하지 않습니다. 앞단에 Caddy 한 줄
  (`example.com { reverse_proxy localhost:8080 }`, api 서브도메인 → `localhost:8010`)
  또는 nginx+certbot을 두세요. api 포트는 `127.0.0.1` 바인딩이라 프록시 없이는 외부 노출되지 않습니다.
- **DB**: 기본은 컨테이너 볼륨의 SQLite. Supabase(Postgres)로 전환하려면 `.env`의
  `DATABASE_URL`만 교체하고 `server/requirements.txt`에 `psycopg[binary]`를 추가하세요.
- **AI 코칭**: 사용자에게 키를 받지 않습니다 — `.env`에 서버측 키(GEMINI_API_KEY 권장)를
  설정해야 코칭이 활성화되고, 회원별 월 무료 횟수(`FREE_COACHING_PER_MONTH`)로 원가를 통제합니다.
- **한글 HUD**: 서버 이미지에 `fonts-nanum`이 포함돼 Linux에서도 한글 오버레이가 렌더링됩니다.
- **비동기 분석 큐는 단일 프로세스 전제**(인메모리) — uvicorn 워커를 늘리려면 큐를 Redis/DB로
  이전해야 합니다 (`server/jobs.py` 참조).
