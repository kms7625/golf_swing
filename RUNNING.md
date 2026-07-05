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

## 참고

- 자동화된 테스트 스위트(Python/TS)는 없습니다 — 회귀 검증은 `golf-analysis-quality` 스킬과
  `golf_swing_analyzer/video/`의 테스트 영상 3종(일반.mp4/프로.mp4/프로2.mp4)으로 수동 비교합니다
- 아키텍처와 각 패키지 역할은 [`CLAUDE.md`](./CLAUDE.md)에 정리돼 있습니다
