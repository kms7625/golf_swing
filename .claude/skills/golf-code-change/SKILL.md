---
name: golf-code-change
description: 골프 스윙 분석 코어(golf_swing_analyzer/analyzer/ 패키지 — 기준DB, 좌표 정규화, 각도 계산, 이동평균 필터, 7단계 스윙 감지, 영상 파이프라인, 요약/스코어링, LLM 프롬프트 데이터)를 수정·리팩토링·버그 수정할 때 반드시 사전 체크리스트를 실행한다. "스윙 감지가 이상해", "임팩트 인식이 안 맞아", "각도 계산이 이상한데", "고쳐줘", "이 로직 수정해줘", "버그 있어", "최적화해줘" 같은 말이 나오면 코드를 건드리기 전에 이 스킬의 체크리스트를 먼저 통과시킨다. 하나라도 위반하면 수정안을 제시하지 않고 위반 사항을 먼저 보고한다. Streamlit/웹/앱 UI 코드(app_v2.py)는 golf-ui-ux 관할, LLM 프롬프트 문구·페르소나는 golf-coach-llm 관할, 모듈 분리·플랫폼 구조 변경은 golf-platform 관할.
---

# 골프 분석 코어 수정 — 시니어 리뷰어 체크리스트

## 왜 이 체크리스트가 필요한가

`golf_swing_analyzer/analyzer/` 패키지(2026-07-04 golf-platform 1단계로 `app_v2.py`
Section 0~8에서 분리됨)는 실제 버그를 겪으며 얻은 불변식의 집합이다. CLAUDE.md에도
일부 기록돼 있지만, 다음 함정들은 코드 주석에만 있고 문서화가 안 돼 있었다:

- 임팩트 감지를 "어드레스 높이 복귀" 방식으로 바꾸면 프로 영상(임팩트 wy < 어드레스 wy인 카메라 각도)에서 오탐한다 — `argmax(wy)` 방식으로 이미 교체된 이력이 있음 (phase_detector.py L.106-112 주석)
- 손목 Y는 정규화 좌표가 아니라 **원시 픽셀 좌표**를 써야 한다 — 정규화 좌표는 y부호 역전 문제가 있어 상승/하강 판정이 깨진다 (pipeline.py L.278-280 주석)
- `_smooth()`에 `np.convolve(mode='same')`을 쓰면 경계에서 0-패딩으로 값이 왜곡된다 — edge-aware 루프로 이미 교체됨 (phase_detector.py L.32-45)
- 척추각 변화량은 전체 구간이 아니라 **어드레스~임팩트 구간만** 측정해야 한다 — 전체 구간으로 재보면 피니시 자세까지 포함돼 프로 영상에서 과도하게 높게 나온다 (scoring.py L.42-49)
- `compute_score()`의 동적 임계값은 `ref_db`에 해당 지표 샘플이 **2개 이상**일 때만 적용되고, 그 전에는 하드코딩 기본값으로 폴백한다 (scoring.py L.79-85) — 현재 `reference_db.json`은 비어 있어 사실상 전부 기본값 경로다
- `annotated_frames`와 `frame_data`는 1:1 인덱스로 같은 `if results.pose_landmarks:` 블록에서 append된다 — 둘 중 하나만 건드리면 인덱스가 어긋난다 (pipeline.py L.253-351)
- CLAUDE.md의 섹션 줄번호는 `app_v2.py`가 아직 단일 파일이던 시절 기준이라 이제는 아예 무효다 (분석 코어가 `analyzer/` 패키지로 이동, `app_v2.py`는 1986줄→885줄로 축소) — **줄번호 근거는 항상 실제 파일을 읽어 확인**, CLAUDE.md나 다른 golf-* 스킬에 적힌 옛 줄번호를 그대로 믿지 말 것
- **2026-07-05부터 `server/main.py`(FastAPI)도 `analyzer/`를 직접 import한다** — Streamlit(`ui/`)뿐 아니라 웹(`server/`+`web/`)도 같은 코어를 공유하므로, 이 체크리스트는 이제 두 프론트엔드 모두에 적용된다. 코어를 변경하면 golf-analysis-quality 회귀 검증에 더해 `web/public/samples/*.json` 재생성도 필요 (golf-ui-ux B5)

---

## A. 변경 전 필수 확인

### A1. local_to_hist 인덱스 매핑 보존
- [ ] `SwingPhaseDetector.update()`가 `local_idx`(포즈 감지된 프레임만 증가)를 받아 `local_to_hist` 딕셔너리에 매핑하는 구조를 건드리는가?
  - 근거: analyzer/phase_detector.py L.20-22 (`self.local_to_hist[frame_idx] = len(self.wrist_y_history)`)
  - `get_phase_for_frame()`도 이 매핑을 통해 조회 — 근접 키 폴백 로직 포함 (phase_detector.py L.149-163)
  - 비가시 프레임으로 인한 보간 항목(`frame_data`)과 `wrist_y_history`(포즈 감지 프레임만) 사이 인덱스 불일치를 막는 유일한 장치 — 제거·단순화 금지
  - **함정**: `update()`의 첫 파라미터명은 코드상 `frame_idx`(phase_detector.py L.20)이지만, 실제 호출부(pipeline.py L.287-288)는 원본 영상 프레임 번호가 아니라 `local_idx`를 넘긴다. 파라미터 이름만 보고 "원본 프레임 인덱스를 넘겨야 한다"고 오해해 `frame_idx`(원본 카운터)를 넘기도록 고치면 `local_to_hist` 매핑이 조용히 깨진다 — 반드시 호출부 인자를 확인할 것

### A2. 임팩트 감지 = argmax(wy) 방식 보존
- [ ] `impact_idx` 계산 방식(백스윙 톱 이후 wy 최댓값)을 다른 방식으로 바꾸려 하는가?
  - 근거: analyzer/phase_detector.py L.100-114
  - 어드레스 높이 복귀 방식·속도 피크 방식 둘 다 시도했다가 폐기된 이력 — 각각 프로 영상 오탐, 0.1초 오차 문제 발생
  - 변경하려면 최소 테스트 영상 3종(golf_swing_analyzer/video/일반.mp4·프로.mp4·프로2.mp4)에서 회귀 검증 후에만 — golf-analysis-quality로 위임

### A3. 원시 픽셀 좌표 vs 정규화 좌표 구분
- [ ] 손목 Y/X를 다루는 코드에서 `norm[...]["pos"]`(정규화 공간)와 `lms_raw[...].y * h`(원시 픽셀)를 혼동하지 않는가?
  - 근거: analyzer/pipeline.py L.275-284
  - 스윙 페이즈 감지·궤적 드로잉은 원시 픽셀 좌표 사용, 관절각 계산(척추각·회전각·무릎·팔꿈치)은 어깨폭 정규화 좌표 사용 — 서로 대체 불가

### A4. edge-aware 스무딩 보존
- [ ] `SwingPhaseDetector._smooth()` 또는 `MovingAverageFilter`의 평균 계산 방식을 `np.convolve(mode='same')` 류로 바꾸려 하는가?
  - 근거: analyzer/phase_detector.py L.32-45 (경계에서 `lo`/`hi`를 클램핑하는 수동 루프)
  - `mode='same'`은 배열 경계에서 0-패딩을 섞어 첫/마지막 값을 왜곡시킴 — 스윙 초반(어드레스) 판정에 직접 영향

### A5. 척추각 변화량 측정 구간
- [ ] `spine_angle_delta` 계산 범위를 변경하려 하는가?
  - 근거: analyzer/scoring.py L.42-49 (`swing_phases = ["어드레스","백스윙","백스윙 톱","다운스윙","임팩트"]`로 필터링 후 max-min)
  - 팔로우스루·피니시까지 포함한 전체 구간 계산으로 되돌리면 프로 영상에서 값이 부풀려짐 (원래 이 문제 때문에 필터링 추가됨)

### A6. compute_score의 ref_db 폴백 조건
- [ ] `_thresh()` 헬퍼나 개별 판정 임계값(척추각/X-Factor/무릎/팔꿈치/어깨회전)을 수정하려 하는가?
  - 근거: analyzer/scoring.py L.79-85, 92-162
  - `ref_db` 해당 지표 샘플 n≥2일 때만 동적 임계값(mean+1σ/2σ) 사용, 그 외엔 하드코딩 기본값(척추각 7/12°, X-Factor 20~80°, 무릎 165°, 팔꿈치 140°, 어깨 60°)으로 폴백
  - 기본값을 바꾸면 `reference_db.json`이 비어 있는 현재 상태에서 즉시 전체 판정 기준이 바뀜 — 영향 범위 큼

### A7. frame_data ↔ annotated_frames 1:1 대응
- [ ] `process_video()`의 `if results.pose_landmarks:` 블록 내부에서 `frame_data.append()`와 `annotated_frames.append()` 중 하나만 조건부로 바꾸려 하는가?
  - 근거: analyzer/pipeline.py L.253-351 (두 리스트가 같은 블록에서 함께 append됨, `preview_indices`는 사실상 전체 인덱스)
  - 인덱스가 어긋나면 UI의 "7단계 대표 프레임" 표시(ui/tab_analysis.py L.238-269 부근, 2026-07-04 UI 분리로 app_v2.py에서 이동)가 엉뚱한 프레임을 보여줌

### A8. 임팩트/다운스윙 대표 프레임 선택 로직 (UI/서버 코드 안에 있지만 분석 불변식)
- [ ] 임팩트=첫 프레임, 다운스윙=85% 지점, 나머지=중간 프레임 선택 규칙을 건드리는가?
  - 근거: ui/tab_analysis.py L.262(임팩트=첫 프레임), L.264(다운스윙=85%), L.266(나머지=중간) — 물리적으로 UI 코드 안에 있지만 CLAUDE.md가 "Representative Frame Selection" 알고리즘으로 문서화한 로직 — analyzer/ 패키지로 옮기지 않고 UI 쪽에 의도적으로 남아있음
  - **2026-07-05 web/ 추가로 복제 지점이 3곳으로 늘어남**: `ui/tab_analysis.py`(Streamlit), `server/serialization.py`의 `extract_representative_frames()`(웹 API), CLAUDE.md 문서. 규칙을 바꾸려면 **세 곳 모두** 동시 수정 — 하나만 고치면 Streamlit과 웹의 대표 프레임이 서로 달라진다
  - 임팩트는 순간적 접촉이라 중간 프레임을 쓰면 이미 지나간 순간을 보여줌

### A9. Adaptive 샘플링 임계값
- [ ] `process_video()`의 프레임 샘플링 규칙(≤180 매 프레임, ≤540 최대 2프레임 간격, 이후 200프레임 상한)을 변경하려 하는가?
  - 근거: analyzer/pipeline.py L.206-217
  - 주석: "다운스윙(0.3~0.5초)이 최소 10프레임 이상 확보되어야 임팩트 감지 가능" — 상한을 너무 낮추면 다운스윙 프레임 수 부족으로 impact_idx 정밀도 하락

---

## B. 변경 후 필수 검증

- [ ] 테스트 영상 3종(golf_swing_analyzer/video/일반.mp4·프로.mp4·프로2.mp4)으로 7단계 페이즈 감지 결과 회귀 확인 — golf-analysis-quality로 위임
- [ ] `reference_db.json`(golf_swing_analyzer/reference_db.json — analyzer/ 이동 후에도 경로 불변)이 비어있는 현재 상태를 가정한 하드코딩 폴백 경로가 정상 동작하는지 확인
- [ ] `frame_data`/`annotated_frames`/`trajectory_pts` 세 리스트의 길이·인덱스 정합성 확인
- [ ] `analyzer/` 패키지를 건드렸다면 `streamlit run app_v2.py`로 앱이 정상 기동하는지 확인 (import 경로 오류는 기동 시점에만 드러남)

---

## 위반 시 처리

체크리스트 항목 중 하나라도 위반이면 **코드 수정안을 제시하지 않는다.**
위반 항목을 먼저 보고하고 사용자가 방향을 결정하도록 한다.

---

## 커밋 전 격리 교차 검증 (선택, 분석 코어 수정 시 권장)

분석 코어(`analyzer/` 패키지)나 그 복제 지점(A8의 ui/tab_analysis.py·
server/serialization.py, geometry.ts 포팅)을 건드린 수정은 커밋 전에
`golf-a9-reviewer` 서브에이전트(`.claude/agents/`)에 diff를 넘겨 교차
검증할 수 있다. 구현을 진행한 컨텍스트는 자기 변경을 합격으로 합리화하는
편향이 있으므로, 격리된 새 컨텍스트의 읽기 전용 리뷰어가 A1~A9를
독립적으로 재판정한다. 리뷰어가 "위반"을 보고하면 이 스킬의 "위반 시
처리" 규칙을 따른다.

---

## 출력 형식

```
[변경 요약] 1줄
[영향 범위] analyzer/어떤 모듈 또는 app_v2.py UI
[체크리스트 위반] 없음 / 항목 나열 (A1~A9 기준)
[코드 diff 또는 패치]
[회귀 검증 필요 여부] 필요 시 golf-analysis-quality로 위임
[다음 액션] 1. 2. 3.
```
