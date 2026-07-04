# ⛳ AI 골프 스윙 분석기 (Streamlit 레퍼런스 구현)

MediaPipe + LLM 기반 골프 스윙 자세 분석 앱. 이 폴더는 **레퍼런스 구현**으로,
새로운 개발은 저장소 루트의 `server/`(FastAPI) + `web/`(React) 쪽에서 진행됩니다.
여기 있는 분석 코어(`analyzer/`)는 두 앱이 공유합니다 — 자세한 아키텍처는
루트의 [`CLAUDE.md`](../CLAUDE.md)를 참고하세요.

---

## 🚀 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 앱 실행
```bash
streamlit run app_v2.py
```

### 3. LLM API 키 발급
- **Gemini**(기본값, 무료 티어 있음): https://aistudio.google.com/app/apikey
- **Claude**: https://console.anthropic.com
- **GPT**: https://platform.openai.com/api-keys

발급한 키는 사이드바에 직접 입력합니다(코드나 파일에 저장되지 않음).

---

## 📋 주요 기능

| 기능 | 설명 |
|------|------|
| 🦴 관절 추출 | MediaPipe Pose로 33개 관절 포인트 추출 |
| 📐 각도 계산 | 척추각, X-Factor, 무릎 굴곡, 팔꿈치 각도를 어깨폭 정규화 좌표로 산출 |
| 🏌️ 페이즈 감지 | 어드레스 → 백스윙 → 백스윙 톱 → 다운스윙 → 임팩트 → 팔로우스루 → 피니시 (7단계) |
| ✂️ 구간 트리밍 | 슬라이더 수동 조정 + 긴 영상 자동 스윙 구간 탐지 |
| 🧠 AI 코칭 | Gemini/Claude/GPT 중 선택, 원인→결과→해결책 구조의 코칭 리포트 |
| 📊 시계열 차트 | 손목 Y 궤적(페이즈 경계 진단용), 관절 각도 변화 |
| 📚 기준 학습 | 프로/아마추어 영상을 누적 분석해 동적 판정 기준(`reference_db.json`) 구축 |
| ⬇️ 데이터 내보내기 | CSV 및 코칭 리포트(txt/json) 다운로드 |

## 📐 세미프로 기준치 (사이드바 안내용 가이드라인)

| 항목 | 권장 범위 | 설명 |
|------|--------|------|
| 척추각 변화량 | ±5° 이내 | 헤드업/스웨이 방지 |
| X-Factor (꼬임) | 35° ~ 55° | 어깨-골반 회전 차이 |
| 무릎 굴곡 | 130° ~ 155° | 지면 반력 활용 |
| 왼팔 직선성 | 150°+ | 백스윙 아크 확보 |
| 어깨 회전 | 80°+ | 백스윙 크기 |

이 수치는 사이드바에 표시되는 참고 가이드라인이며, 실제 점수 산정(`compute_score()`)은
`reference_db.json`에 축적된 데이터가 있으면 그 분포(평균±표준편차) 기반 동적 임계값을,
없으면 별도의 하드코딩 기본값을 사용합니다 — 두 수치가 항상 일치하진 않습니다.

## 🎬 권장 촬영 조건

- **앵글**: 정면(Face-on) 또는 측면(Down-the-line)
- **위치**: 골퍼가 화면 중앙에 위치
- **조명**: 밝은 환경 권장 (어두운 환경은 CLAHE 전처리로 일부 보정)
- **해상도**: 720p 이상
- **길이**: 5 ~ 30초 (30초 초과 시 스윙 구간 자동 탐지 사용 권장)

## 🛠 기술 스택

- **UI**: Streamlit
- **비전 AI**: MediaPipe Pose
- **LLM**: Gemini(`google-genai`) / Claude(`anthropic`) / GPT(`openai`)
- **영상 처리**: OpenCV (CLAHE 전처리 포함)
- **수치 계산**: NumPy 벡터 기하학 (코사인 제2법칙 기반 관절각)
- **데이터**: Pandas DataFrame

## 📁 폴더 구조

```
golf_swing_analyzer/
├── app_v2.py           # 배선 전용 (~53줄) — set_page_config → main()
├── analyzer/           # 분석 코어 (9개 모듈) — 로직 무변경, server/도 동일 코어 사용
├── ui/                 # Streamlit UI (사이드바 + 탭 5개, 모듈당 1파일)
├── video/              # 회귀 검증용 테스트 영상 3종 (일반/프로/프로2.mp4)
├── reference_db.json   # 프로/아마추어 기준 통계 누적 DB
└── requirements.txt
```

각 모듈의 역할과 알고리즘 불변식은 루트 [`CLAUDE.md`](../CLAUDE.md)에 자세히 정리돼 있습니다.
