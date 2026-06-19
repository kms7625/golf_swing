# ⛳ AI 골프 스윙 분석기

MediaPipe + Gemini AI 기반 골프 스윙 자세 분석 웹 앱

---

## 🚀 실행 방법

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 앱 실행
```bash
streamlit run app.py
```

### 3. Gemini API 키 발급 (무료)
1. https://aistudio.google.com/app/apikey 접속
2. Google 계정으로 로그인
3. "Create API key" 클릭
4. 생성된 키를 앱 사이드바에 입력

---

## 📋 주요 기능

| 기능 | 설명 |
|------|------|
| 🦴 관절 추출 | MediaPipe Pose로 33개 관절 포인트 실시간 추출 |
| 📐 각도 계산 | 척추각, X-Factor, 무릎 굴곡, 팔꿈치 각도 자동 산출 |
| 🏌️ 페이즈 감지 | 어드레스 → 백스윙 → 탑 → 다운스윙 → 임팩트 → 피니시 |
| 🧠 AI 피드백 | Gemini 1.5 Flash 기반 전문 코칭 피드백 생성 |
| 📊 시계열 차트 | 스윙 전 구간 관절 각도 변화 시각화 |
| ⬇️ 데이터 내보내기 | CSV 및 텍스트 피드백 다운로드 |

---

## 📐 분석 기준치 (세미프로 기준)

| 항목 | 이상값 | 설명 |
|------|--------|------|
| 척추각 변화량 | ≤ 5° | 헤드업/스웨이 방지 |
| X-Factor (꼬임) | 35° ~ 55° | 어깨-골반 회전 차이 |
| 무릎 굴곡 | 130° ~ 155° | 지면 반력 활용 |
| 왼팔 직선성 | ≥ 150° | 백스윙 아크 확보 |

---

## 🎬 권장 촬영 조건

- **앵글**: 정면(Face-on) 또는 측면(Down-the-line)
- **위치**: 골퍼가 화면 중앙에 위치
- **조명**: 밝은 환경 권장
- **해상도**: 720p 이상
- **길이**: 5 ~ 30초 분량

---

## 🛠 기술 스택

- **프론트엔드**: Streamlit
- **비전 AI**: MediaPipe Pose (BlazePose, model_complexity=2)
- **LLM**: Google Gemini 1.5 Flash
- **영상 처리**: OpenCV (CLAHE 전처리 포함)
- **수치 계산**: NumPy 벡터 기하학 (arccos 기반 각도)
- **데이터**: Pandas DataFrame

---

## 📁 파일 구조

```
golf_swing_analyzer/
├── app.py           # 메인 Streamlit 앱
├── requirements.txt # 패키지 의존성
└── README.md        # 이 파일
```
