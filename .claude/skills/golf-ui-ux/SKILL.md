---
name: golf-ui-ux
description: 골프 스윙 분석 앱의 화면(현재 Streamlit UI, 향후 신규 웹/앱 프론트엔드)을 작업할 때 사용한다. "UI 바꿔줘", "화면 이상해", "디자인 손봐줘", "탭 구조 바꿔줘", "이 화면 보기 불편해", "사이드바 수정해줘" 같은 말이 나오면 트리거한다. 분석 수치 로직(정규화·각도·페이즈 감지)은 golf-code-change 관할, 플랫폼/프레임워크 선택 자체(Streamlit 유지 여부, React/모바일 프레임워크 결정)는 golf-platform 관할 — 이 스킬은 그 결정이 내려진 뒤의 UI 구현·수정만 다룬다.
---

# 골프 앱 UI/UX 작업 규칙

## 현재 상태와 한계

현재 UI는 Streamlit 단일 파일(`app_v2.py`, 2026-07-04 golf-platform 1단계로 분석
코어가 `analyzer/` 패키지로 분리된 뒤 1986줄→885줄로 축소됨) — 사용자가 이 UI에
불만족해 개편을 요청한 상태다. "코어 보존 + 껍데기 교체" 방향(CLAUDE.md 및 프로젝트
메모리 `golf-coaching-revamp-plan` 참조)에 따라 이 UI는 최종적으로 새 프론트엔드로
교체될 예정이지만, 교체 전까지는 이 스킬이 현재 Streamlit UI의 정합성을 관장한다.
줄번호는 모듈 분리로 전부 바뀌었으니 항상 실제 파일을 확인할 것.

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
    `annotated_frames`, `trajectory_pts`, `fps`, `phase_detector`(코드상 실제 키는 `phase_det`, app_v2.py L.403),
    `effective_sample`(코드상 실제 키는 `eff_sample`, app_v2.py L.404), `summary`, `score`, `issues`, `uploaded_name`
  - **주의**: CLAUDE.md 문서의 키 이름과 실제 코드의 키 이름이 일부 다르다(`phase_detector`→`phase_det`,
    `effective_sample`→`eff_sample`) — 새 코드 작성 시 반드시 실제 코드(app_v2.py L.395-405)를 확인할 것
- [ ] 새 파일 업로드 시 `trim_path` 초기화를 빠뜨리지 않는가?
  - 근거: app_v2.py L.246 — 파일명이 바뀌면 `st.session_state.pop("trim_path", None)` 필수, 안 하면 이전 파일의 트리밍 구간이 새 파일에 잘못 적용됨

### A3. 대표 프레임 선택 로직은 UI 코드 안에 있지만 분석 불변식
- [ ] Tab1의 7단계 대표 프레임 렌더링(app_v2.py L.465-486)을 UI 개선 명목으로 건드리는가?
  - 임팩트=첫 프레임, 다운스윙=85%지점, 나머지=중간 프레임 규칙은 golf-code-change A8 관할 —
    UI 레이아웃(카드 배치, 스타일)은 이 스킬이 다루되, 프레임 **선택 로직**은 손대기 전 golf-code-change 확인

### A4. 임계값 기준이 코드 안에서 네 곳으로 흩어져 서로 다름
- [ ] 임계값 관련 UI(사이드바 안내, 메트릭 카드 색상, 수치 요약 표) 중 하나만 고치려 하는가?
  - 같은 X-Factor에 대해 코드 안에 **서로 다른 기준 네 곳**이 존재한다 — 하나만 고치면 나머지 세 곳과 계속 어긋난다:
    1. 사이드바 "세미프로 기준치" 안내 텍스트 — X-Factor 35~55° (app_v2.py L.180-186)
    2. Tab1 메트릭 카드 good/warn 판정 — `get_status(x_factor, 35, 55, 20, 60)` (app_v2.py L.434)
    3. Tab4 수치 요약 표의 ✅/⚠️ 판정 — `35 <= x_factor <= 55` (app_v2.py L.747)
    4. `compute_score()`의 실제 점수 산정 임계값 — 기본값 20~80° (analyzer/scoring.py L.110, ref_db 있으면 동적)
  - 결과적으로 같은 스윙이 메트릭 카드·요약 표에서는 경고(⚠️)로 보이는데 실제 점수는 감점 없이 통과할 수 있음
  - 척추각·무릎·팔꿈치·어깨회전도 동일한 다중 소스 패턴이 있는지 함께 확인할 것 (analyzer/scoring.py L.65-162 vs 사이드바/카드/표)
  - UI 쪽 표시만 고치면 판정 로직과 계속 어긋난다 — 네 곳을 하나의 기준(가급적 `compute_score()`가 쓰는 실제 임계값)으로 통일할지, 각 표시 위치의 역할을 다르게 유지할지 사용자에게 확인

### A5. 탭 간 의존성
- [ ] Tab2~5는 모두 `"summary" not in st.session_state` 또는 `"frame_data" not in st.session_state`일 때 안내 메시지로 조기 반환한다 (app_v2.py L.512, 626, 670) — 새 탭 추가 시 동일 가드 패턴 유지

---

## B. 새 프론트엔드(웹/앱) 설계 시 확인 사항

golf-platform에서 프레임워크가 확정된 뒤 적용:

- [ ] 온디바이스 30fps 목표(PPTX 비전)를 만족하려면 무거운 서버 왕복을 최소화하는 구조인가
- [ ] 기존 Streamlit UX의 검증된 사용자 동선(업로드 → 구간 트리밍 미리보기 → 분석 → 7단계 결과 → AI 코칭)을 신규 UI에서도 유지하는가, 의도적으로 바꾸는가 명확히 구분
- [ ] 한글 HUD, 페이즈별 색상 코드(`PHASE_COLORS`, analyzer/drawing.py L.6-15) 등 기존에 확정된 시각 언어를 재사용할지 새로 디자인할지 결정하고 명시

---

## 출력 형식

```
[작업 대상] Streamlit / 신규 프론트엔드
[체크리스트 확인] A1~A5 또는 B 항목 중 해당 사항
[발견된 불일치] 있으면 명시 (예: 사이드바 안내치 vs 실제 판정 기준)
[변경 내용]
[다음 액션]
```
