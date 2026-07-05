# ⛳ Swing.Lab — AI 골프 스윙 분석기

MediaPipe 포즈 추정과 LLM 코칭을 결합해, 골프 스윙 영상 한 편을 7단계로 자동 분할하고
관절 각도·궤적 데이터를 원인→결과→해결책 구조의 코칭 리포트로 바꿔주는 프로젝트입니다.

같은 분석 코어를 공유하는 두 개의 프론트엔드가 있습니다.

| | 역할 | 실행 방법 |
|---|---|---|
| **`golf_swing_analyzer/`** (Streamlit) | 레퍼런스 구현 — 회귀 검증 기준 | `pip install -r golf_swing_analyzer/requirements.txt`<br>`streamlit run golf_swing_analyzer/app_v2.py` |
| **`server/` + `web/`** (FastAPI + React) | 현재 개발 중인 앱 — "모션 랩" 디자인, 한/영 지원 | `pip install -r server/requirements.txt && cd server && uvicorn main:app --port 8010`<br>`cd web && npm install && npm run dev` |

두 앱 모두 Gemini/Claude/GPT API 키를 실행 시점에 사용자가 직접 입력합니다(코드에 저장되지 않음).
Gemini는 무료 티어가 있어 기본값으로 설정돼 있습니다.

더 자세한 실행 방법(Android 포함)은 [`RUNNING.md`](./RUNNING.md) 참고.

## 핵심 기능

- **7단계 스윙 자동 세그먼테이션** — 어드레스 → 백스윙 → 백스윙 톱 → 다운스윙 → 임팩트 → 팔로우스루 → 피니시
- **어깨폭 정규화 좌표계** 기반 관절각 계산 — 카메라 거리·해상도 무관
- **원인→결과→해결책 구조의 AI 코칭 리포트** — 단순 수치 나열이 아닌 설명 가능한 피드백
- **자동/수동 스윙 구간 트리밍** — 긴 영상에서도 스윙 구간만 정확히 추출
- 웹 버전: 손목 Y 궤적 파형 차트, 한/영 토글, 서버·API 키 없이 볼 수 있는 샘플 결과

## 프로젝트 구조와 개발 가이드

아키텍처, 알고리즘 불변식, 각 패키지의 역할은 [`CLAUDE.md`](./CLAUDE.md)에 정리돼 있습니다.
이 저장소를 수정할 때는 `.claude/skills/golf-*` 스킬셋(코드 변경 체크리스트, UI 작업 규칙,
플랫폼 구조 결정 절차 등)을 먼저 확인하는 것을 권장합니다.

## 기술 스택

- **분석 코어**: MediaPipe Pose, OpenCV(CLAHE 전처리), NumPy
- **레퍼런스 프론트엔드**: Streamlit
- **웹 프론트엔드**: React + Vite + TypeScript, Recharts
- **API 서버**: FastAPI
- **LLM 코칭**: Gemini / Claude / GPT (사용자 API 키)
