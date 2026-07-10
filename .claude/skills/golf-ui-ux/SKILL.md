---
name: golf-ui-ux
description: 골프 스윙 분석 앱의 화면(Streamlit `ui/` 패키지, React `web/` 프론트엔드)을 작업할 때 사용한다. "UI 바꿔줘", "화면 이상해", "디자인 손봐줘", "탭 구조 바꿔줘", "이 화면 보기 불편해", "사이드바 수정해줘", "웹 화면 고쳐줘", "번역 이상해" 같은 말이 나오면 트리거한다. 분석 수치 로직(정규화·각도·페이즈 감지)은 golf-code-change 관할, 플랫폼/프레임워크 선택 자체(Streamlit 유지 여부, React/모바일 프레임워크 결정)는 golf-platform 관할 — 이 스킬은 그 결정이 내려진 뒤의 UI 구현·수정만 다룬다.
---

# 골프 앱 UI/UX 작업 규칙

## 현재 상태와 한계

현재 UI는 Streamlit + `golf_swing_analyzer/ui/` 패키지(2026-07-04 golf-platform
1단계로 분석 코어가 `analyzer/`로, 이어서 UI가 `ui/` 패키지로 분리됨 —
`app_v2.py`는 배선만 남아 53줄) — 사용자가 이 UI에 불만족해 개편을 요청한 상태다.
"코어 보존 + 껍데기 교체" 방향(CLAUDE.md 및 프로젝트 메모리 `golf-coaching-revamp-plan`
참조)에 따라 이 UI는 최종적으로 새 프론트엔드로 교체될 예정이지만, 교체 전까지는
이 스킬이 현재 `ui/` 패키지의 정합성을 관장한다. `ui/` 구조: styles.py(CSS+hero),
components.py(카드/상태 헬퍼), sidebar.py, tab_analysis/phases/data/coaching/learning.py
(탭별 1:1 대응). 줄번호는 모듈 분리로 전부 바뀌었으니 항상 실제 파일을 확인할 것.

플랫폼 결정(Streamlit 폐기 시점, 신규 프레임워크 선택)이 내려지지 않은 상태에서
대규모 UI 재작성을 먼저 시작하지 않는다 — 되돌리기 어려운 구조 결정은 golf-platform 선행.

---

## A. 현재 Streamlit UI 작업 시 확인 사항

### A1. 한글 렌더링 제약 (analyzer/ 코어로 이동됨 — 수정은 golf-code-change 관할)
- [ ] `cv2.putText()`로 한글을 직접 그리려 하는가? — **불가능**, PIL 경로를 써야 한다
  - 근거: analyzer/drawing.py L.40-58 (`_get_hud_font`), L.61-95 (PIL 렌더링 + ASCII 폴백) — 2026-07-04 모듈 분리로 app_v2.py에서 이동됨
  - 폰트는 `C:/Windows/Fonts/malgun.ttf` 우선, 모듈 전역 `_hud_font`로 캐싱 — 프레임마다 재로드 금지
  - 이 로직 자체는 분석 파이프라인(annotated_frames 생성)의 일부라 실제 코드 수정은 golf-code-change 관할 — 이 스킬은 새 프론트엔드에서 한글 오버레이를 어떻게 재현할지 결정할 때만 참고

### A2. 세션 상태 키 정합성
- [ ] 새 UI 요소가 기존 세션 상태 키와 충돌하거나 누락시키는가?
  - 근거: CLAUDE.md "Streamlit 세션 상태 키" 목록 — `tmp_original`, `trim_path`, `frame_data`,
    `annotated_frames`, `trajectory_pts`, `fps`, `phase_detector`(코드상 실제 키는 `phase_det`, ui/tab_analysis.py L.183-191 `session_state.update` 블록),
    `effective_sample`(코드상 실제 키는 `eff_sample`), `summary`, `score`, `issues`, `uploaded_name`
  - **주의**: CLAUDE.md 문서의 키 이름과 실제 코드의 키 이름이 일부 다르다(`phase_detector`→`phase_det`,
    `effective_sample`→`eff_sample`) — 새 코드 작성 시 반드시 실제 코드(ui/tab_analysis.py L.183-191)를 확인할 것
- [ ] 새 파일 업로드 시 `trim_path` 초기화를 빠뜨리지 않는가?
  - 근거: ui/tab_analysis.py L.34 — 파일명이 바뀌면 `st.session_state.pop("trim_path", None)` 필수, 안 하면 이전 파일의 트리밍 구간이 새 파일에 잘못 적용됨

### A3. 대표 프레임 선택 로직은 UI 코드 안에 있지만 분석 불변식
- [ ] Tab1의 7단계 대표 프레임 렌더링(ui/tab_analysis.py L.238-269 부근)을 UI 개선 명목으로 건드리는가?
  - 임팩트=첫 프레임, 다운스윙=85%지점, 나머지=중간 프레임 규칙(L.262 임팩트, L.264 다운스윙, L.266 나머지)은 golf-code-change A8 관할 —
    UI 레이아웃(카드 배치, 스타일)은 이 스킬이 다루되, 프레임 **선택 로직**은 손대기 전 golf-code-change 확인

### A4. 임계값 기준이 코드 안에서 네 곳으로 흩어져 서로 다름
- [ ] 임계값 관련 UI(사이드바 안내, 메트릭 카드 색상, 수치 요약 표) 중 하나만 고치려 하는가?
  - 같은 X-Factor에 대해 코드 안에 **서로 다른 기준 네 곳**이 존재한다 — 하나만 고치면 나머지 세 곳과 계속 어긋난다:
    1. 사이드바 "세미프로 기준치" 안내 텍스트 — X-Factor 35~55° (ui/sidebar.py L.41)
    2. Tab1 메트릭 카드 good/warn 판정 — `get_status(x_factor, 35, 55, 20, 60)` (ui/tab_analysis.py L.222)
    3. Tab4 수치 요약 표의 ✅/⚠️ 판정 — `35 <= x_factor <= 55` (ui/tab_coaching.py L.87)
    4. `compute_score()`의 실제 점수 산정 임계값 — 기본값 20~80° (analyzer/scoring.py L.110, ref_db 있으면 동적)
  - 결과적으로 같은 스윙이 메트릭 카드·요약 표에서는 경고(⚠️)로 보이는데 실제 점수는 감점 없이 통과할 수 있음
  - 척추각·무릎·팔꿈치·어깨회전도 동일한 다중 소스 패턴이 있는지 함께 확인할 것 (analyzer/scoring.py L.65-162 vs 사이드바/카드/표)
  - UI 쪽 표시만 고치면 판정 로직과 계속 어긋난다 — 네 곳을 하나의 기준(가급적 `compute_score()`가 쓰는 실제 임계값)으로 통일할지, 각 표시 위치의 역할을 다르게 유지할지 사용자에게 확인

### A5. 탭 간 의존성
- [ ] Tab2~5는 모두 `"summary" not in st.session_state` 또는 `"frame_data" not in st.session_state`일 때 안내 메시지로 조기 반환한다 (ui/tab_phases.py L.5, ui/tab_data.py L.7, ui/tab_coaching.py L.10) — 새 탭 추가 시 동일 가드 패턴 유지

---

## B. `web/` React 프론트엔드 작업 시 확인 사항 (golf-platform 3단계, 2026-07-05 구축)

구조: `src/index.css`(그래파이트+코퍼+틸 디자인 토큰, 단일 다크 테마 — golf-platform
2단계에서 확정한 "모션 랩" 시안), `src/lib/`(api.ts, types.ts, i18n.tsx, status.ts),
`src/components/`(TopBar, Hero, UploadTrim, ResultScreen, Waveform, CoachingPanel,
LiveCapture — 5단계 라이브 웹캠, 캔버스 오버레이는 `object-fit: cover` 미러링 필수,
CLAUDE.md "Live webcam analysis" 참조).
백엔드는 `server/`(FastAPI, `analyzer/` 직접 import) — 엔드포인트: `/analyze`,
`/auto-window`, `/detect-phases`(라이브 종료 시에도 사용), `/coaching`.
4단계 산출물 `web/android/`(Capacitor 래퍼, dev 전용 네트워크 배선)도 같은
`web/` 빌드를 감싼다 — 배선 수정 시 CLAUDE.md `web/android/` 섹션 선행 확인.

### B1. 서버 응답 포맷 불변 원칙
- [ ] API 응답 필드명이나 페이즈명("어드레스" 등 한국어)을 프론트 편의로 바꾸려 하는가?
  - 서버 응답은 항상 한국어 원본 그대로 — 표시 번역은 오직 `src/lib/i18n.tsx`의
    `PHASE_KEY_MAP_INTERNAL`/`phaseLabel()` 경유. 서버·프론트 양쪽을 동시에 바꾸면
    `server/serialization.py`와 `web/src/lib/types.ts`의 `PHASE_KEY_MAP`이 어긋난다

### B2. 대표 프레임 선택 로직 — 3중 복제 지점
- [ ] 임팩트=첫 프레임/다운스윙=85%/나머지=중간 규칙(golf-code-change A8)을 손대려 하는가?
  - 이 로직은 이제 **세 곳**에 복제돼 있다: `ui/tab_analysis.py`(Streamlit), `server/serialization.py`
    `extract_representative_frames()`(웹 API가 실제로 쓰는 곳), CLAUDE.md 문서. 하나만 고치면
    Streamlit과 웹의 대표 프레임이 달라진다 — 세 곳 모두 golf-code-change 경유로 동시 수정

### B3. i18n 문자열 하드코딩 금지
- [ ] 새 UI 문자열을 컴포넌트에 직접 쓰려 하는가(`<p>분석 중...</p>` 같은 하드코딩)?
  - 반드시 `src/lib/i18n.tsx`의 `STRINGS` 딕셔너리에 키를 추가하고 `useI18n().t()`로 참조 —
    한쪽 언어만 추가하고 다른 언어를 빠뜨리면 토글 시 원문 노출됨
  - 페이즈명은 `t()`가 아니라 `phaseLabel(koPhaseName)`으로 — 서버가 주는 한국어 원본을 입력받아 변환

### B4. 임계값 로직은 `status.ts`로 단일화
- [ ] 메트릭 색상 판정(good/warn/crit)을 컴포넌트 안에 직접 if문으로 새로 쓰려 하는가?
  - `src/lib/status.ts`의 `getStatus()`가 `ui/components.py`의 `get_status()`와 동일 로직으로
    이식돼 있음 — 재구현하지 말고 재사용. Streamlit A4에서 지적한 "네 곳 불일치" 문제를
    웹에서 또 만들지 않도록 주의 (현재 웹은 스코어 패널 1곳만 이 로직을 씀 — 늘어나면 위험)

### B5. 샘플 프리로드 동기화
- [ ] `analyzer/` 코어나 `server/` 응답 포맷을 바꿨는가?
  - `web/public/samples/*.json`은 변경 전 API 응답의 스냅샷이다 — 포맷이 바뀌면 프론트가
    깨지거나 낡은 필드를 표시한다. 코어/서버 변경 후에는 서버를 띄우고 샘플을 재생성할 것
    (스크립트 전례: 세 영상에 `/auto-window` → `/analyze` 순으로 호출해 저장)

### B6. Tab5/CSV 등 의도적 미구현 범위
- [ ] Streamlit Tab5(기준 학습 DB 축적), Tab3 CSV 다운로드를 웹에도 만들려 하는가?
  - golf-platform 3단계에서 의도적으로 범위 제외 — 필요해지면 먼저 golf-platform에 재확인

---

## 출력 형식

```
[작업 대상] Streamlit ui/ / 웹 web+server
[체크리스트 확인] A1~A5 또는 B1~B6 항목 중 해당 사항
[발견된 불일치] 있으면 명시 (예: 사이드바 안내치 vs 실제 판정 기준, 3중 복제 로직 불일치)
[변경 내용]
[다음 액션]
```
