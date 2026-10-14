# X-Factor 수평면 회전 추정 개선

2026-10-14 · `feature/xfactor` · 기준 `3bdf45d` · 미커밋

## 1. 결과와 완료 범위

MediaPipe world 좌표를 이용한 어드레스 대비 회전 추정을 기본으로 추가했다. 기존 2D 함수·비교값과 명시적 폴백을 유지한다. 앱 7개와 GolfDB 50개를 동일 Docker 포즈 스트림으로 비교했고, 실제 feature 파이프라인으로 앱 7개를 재실행해 전체 summary·점수·단계 경계·원본 프레임 키 일치를 확인했다.

Docker pytest **51 passed**. web build/lint 성공. 점수 임계값과 `compute_score()` 본문은 기준과 바이트 단위로 동일하다. `phase_detector.py`, `smoothing.py`, `video_signal.py`도 변경하지 않았다. 발표용 레포·8010·ngrok·dev에는 변경 작업을 하지 않았고 커밋도 만들지 않았다.

**남은 미검증:** Mac native 포즈는 OpenGL 초기화 실패로 비교하지 못했다. Streamlit 패키지가 없어 기동·화면 검증도 수행하지 못했다. 새 패키지는 설치하지 않았다. 따라서 요청 항목 (c)의 native Mac↔Docker 차이 감소는 아직 입증하지 못했다.

## 2. 정의와 문헌 근거

기존 `docs/research/01~04`와 `references.bib`를 먼저 확인하고 아래 원문을 다시 열었다. 접근 실패한 DOI 링크를 원문 확인으로 세지 않았다.

| 자료 | 확인 수준·적용 |
|---|---|
| [MediaPipe Pose 공식 문서](https://chuoling.github.io/mediapipe/solutions/pose.html#pose_world_landmarks) | world x/y/z는 미터, 원점은 골반 중심, visibility는 영상 landmark와 같은 의미. normalized landmark의 z와 구분한다. |
| [Smith et al., 2016, 저자 공개본](https://pure.ulster.ac.uk/ws/portalfiles/portal/11647474/Comparison_of_2d_and_3d_methods_for_analysis_of_trunk_-_IR2.pdf) | 본문 Table 1: 어깨·골반 벡터의 수평면 투영 분리각과 3D 분절 상대 회전은 다른 방법. Table 3의 톱 평균 회전은 몸통 87.10°, 골반 44.82°의 크기다. 이 평균들의 차이 42.28°는 여기서 계산한 규모 참고값이며 개인별 X-Factor의 분포·정상 범위가 아니다. |
| [Myers et al., 2008](https://pubmed.ncbi.nlm.nih.gov/17852693/) | 초록: 레크리에이션 골퍼 100명에서 톱의 분리각과 최대 분리각을 별도로 측정했다. 서로 다른 시점의 두 최대각 차이를 X-Factor로 삼는 근거가 아니다. |
| [Kwon et al., 2013](https://pubmed.ncbi.nlm.nih.gov/24245049/) | 초록: 숙련 남성 18명에서 계산법별 값 차이와 직접적인 클럽헤드 속도 상관 부재를 보고했다. 특정 지표 값의 증가를 성능 향상으로 해석하지 않는다. |

본 구현의 이름은 **world 좌표의 수평면 회전 추정**이다. 문헌의 해부학적 Cardan/Euler 분절 상대 회전을 구현한 것은 아니다. MediaPipe의 두 어깨·두 hip 점도 문헌의 acromion/ASIS/PSIS 마커 및 흉곽 좌표계와 같지 않다.

카메라가 수평이라는 가정에서 camera Y를 수직축으로, XZ를 수평면으로 둔다. world 출력은 중력 센서로 보정된 실험실 좌표계가 아니다. 고정 카메라 yaw는 기준 자세를 빼면 소거되지만 roll/pitch·카메라 이동은 별도 보정하지 않는다.

```text
v_s(t) = W_12(t) - W_11(t),  v_h(t) = W_24(t) - W_23(t)
p(t) = (v_x(t), v_z(t))
ψ(t) = atan2(-v_z(t), v_x(t))  [도, camera +Y convention]
u(t) = unwrap(ψ(t))            [신뢰할 수 있는 관측 시계열]
Δ_s(t) = u_s(t) - u_s(A),  Δ_h(t) = u_h(t) - u_h(A)
r_s(t) = q · trailing_mean_5(Δ_s(t)),  r_h(t) = q · trailing_mean_5(Δ_h(t))
XF_top = r_s(T) - r_h(T)
```

`A`는 **선택된 단일 사이클의 어드레스에서 두 segment 모두 유효한 첫 프레임**이다. 어드레스가 없으면 늦은 백스윙을 기준으로 대체하지 않는다. `T`는 변경하지 않은 검출기의 `백스윙 톱` 시작 원본 프레임이다. UI의 톱 대표 사진은 기존 중간 프레임 선택 규칙을 유지한다.

`q`는 톱의 어깨 이동 방향을 양수로 만드는 공통 부호이며, 톱 world가 없으면 유효 백스윙 어깨 이동 중앙값의 부호를 쓴다. 어깨·골반에 같은 q를 적용한다. 원래 +Y 부호도 저장한다. **X-Factor에 abs/clamp를 적용하지 않는다.** 골반이 더 돌아 음수가 되는 합성 사례는 −40°로 유지된다.

본 값은 초기 분리각을 제거한 **분리각 변화량**이다. 문헌의 절대 톱 분리각과 같으려면 어드레스에서 두 선이 정렬돼 있어야 한다. 이 차이 때문에 문헌의 수십 도라는 규모와 직접적인 정확도 비교를 할 수 없다.

5개 유효 관측의 후행 평균은 이전 순간을 포함하므로 지연·진폭 축소가 있다. 두 segment는 동일 관측 창을 사용한다. 결측에서 평균 창을 비우며, 0.2초 초과 간격에서도 비운다. `*_3d_signed`는 평균 전 unwrap 값이다. 톱~다운스윙에서 같은 순간의 최대 분리각도 별도 저장하지만 주 X-Factor·점수에는 사용하지 않는다.

## 3. 폴백과 기록 필드

두 segment를 **함께** 검증한다. world가 없거나 짧음, 비유한 좌표, 네 관절 중 visibility ≤0.5, XZ 투영 길이 <0.0001m이면 2D로 폴백한다. 기존 2D gate 탈락 후 이전 값 유지 행은 `interpolated_2d`로 표시하고 world 관측으로 세지 않는다.

추가로 accepted heading 사이의 가장 짧은 변화가 어느 segment에서든 **120° 이상**이면 `world_heading_jump`로 거부한다. 거부 관측으로 이전 accepted 방향을 갱신하지 않아 단발성 좌우 반전의 누적 회전을 막는다. 이 120°는 모호한 반회전을 거부하는 보수적인 **측정 신뢰도 기준**이며 A6 점수 임계값이나 문헌에서 검증된 임계값이 아니다. 결측 뒤 실제 큰 회전도 거부할 수 있다.

| 위치 | 필드·의미 |
|---|---|
| `frame_data` | `shoulder_rotation_2d`, `hip_rotation_2d`: 기존 5프레임 평균 결과를 그대로 보존 |
| `frame_data` | `world_rotation_headings`: 원시 어깨/골반 heading, `*_3d_signed`: unwrap 후 기준 대비 원래 부호, `*_3d`: q 적용 후 평균 |
| `frame_data` | `rotation_method`, `rotation_fallback_reason`, `rotation_reference_frame`, `rotation_sign`, `rotation_gap_sec`, `rotation_at_top` |
| `summary` | `x_factor_2d`, `x_factor_3d`, `x_factor_method`, `x_factor_frame`, `x_factor_fallback_reason`, 유효 비율·폴백 행 수 |
| `summary` | `x_factor_3d_max_separation`, `x_factor_3d_max_frame`: 톱~다운스윙 별도 참고값 |

기본 호출은 `process_video(..., rotation_method="world_3d")`; `"legacy_2d"`를 지정하면 이전 계산을 선택한다. 구형 저장 결과·라이브 2D 입력에는 이전 summary 의미를 유지한다.

정확한 T 행 또는 어드레스 기준이 유효하지 않으면 **summary의 회전 평균·최대·단계별 회전과 X-Factor 전체를 기존 방식으로** 계산한다. 유효 톱이면 평균·단계별 회전은 3D 관측만 집계하고, 어깨·골반 최대는 어드레스~톱의 3D 값만 사용한다. 피니시의 큰 회전으로 백스윙 점수를 채우지 않는다. 프레임별 활성 값은 폴백 구간에서 2D이므로 차트는 혼합될 수 있으며 web·Streamlit에서 안내한다.

## 4. 평가 설계

앱 7개는 `/datasets/golfdb_pose/apps_before.json`에 이미 기록된 자동 선택 창을 고정했다. 창·재인코딩·MediaPipe 전처리·샘플링·포즈·단계 검출은 양 버전에 공통이다. before는 변경 전 코드를 `/private/tmp/xfactor_baseline_3bdf45d`에 복사한 버전이다. before frame metrics와 world 출력은 같은 추론에서 수집했다.

GolfDB는 기존 캐시와 로컬 영상이 모두 존재하는 `slow=0`, **split 1–3**에서 방향별 ID 순 첫 25개를 고정했다. [selection.json](selection.json) 참조. split 4는 쓰지 않았다. 기존 NPZ에는 normalized landmarks만 있고 world가 없어, 같은 영상·전처리·샘플링으로 Docker에서 별도 world sidecar를 생성했다. 기존 캐시는 수정하지 않았다. 새 영상 다운로드·학습·점수 임계값 튜닝은 없다.

원자료·world NPZ는 `/Users/mose/datasets/xfactor_eval/docker/`; 57개 영상의 지표·점수는 [comparison.csv](comparison.csv), 집계는 [metrics.json](metrics.json). 정답 회전각이 없으므로 음수 비율·분포·방향 간 차이는 타당성 단서이며 정확도/MAE가 아니다. before→after에는 좌표 변경, 어드레스 기준화, 동시 시점 차이, 백스윙 최대 범위 변경이 함께 포함된다.

## 5. 앱 7개: 지표와 점수 변화

각도 단위 °. 점수는 빈 `reference_db.json`의 기존 하드코딩 기준이다.

| 영상 | 창(초) | X-Factor 전→후 | 어깨 최대 전→후 | 점수 전→후 | 후 방식·사유 |
|---|---|---:|---:|---:|---|
| 일반 | 1.467–5.067 | −4.6→26.2 | 33.9→41.0 | 45→60 (+15) | 3D 톱 |
| 프로 | 8.647–11.818 | 2.0→21.9 | 30.8→82.1 | 52→75 (+23) | 3D 톱, 일부 프레임 폴백 |
| 프로2 | 38.172–42.075 | 18.6→18.6 | 41.0→41.0 | 77→77 (0) | 2D: 어드레스 world 기준 없음 |
| pexels_8065880 | 2.833–8.583 | 37.5→5.6 | 58.8→37.1 | 72→57 (−15) | 3D 톱, 일부 프레임 폴백 |
| pexels_6541855 | 1.640–7.640 | 60.7→60.7 | 85.2→85.2 | 90→90 (0) | 2D: 정확한 톱이 기존 보간 행 |
| pexels_35546329 | 10.467–14.467 | 1.8→35.1 | 37.3→66.2 | 55→78 (+23) | 3D 톱 |
| pexels_34883764 | 6.000–9.800 | 53.5→53.5 | 81.0→81.0 | 90→90 (0) | 2D: 어드레스 world 기준 없음 |

순수 3D 주 지표는 **4/7**, summary 폴백은 **3/7**. 기본 결과의 음수는 **1/7 (14.3%)→0/7**, 4개 3D 사용 영상만 같은 집합으로 비교하면 **1/4→0/4**다. 20–80° 안의 기본 결과는 3/7→5/7이나, 이는 기존 점수 창과의 비교일 뿐 문헌 정상 판정이 아니다. 척추·무릎·팔꿈치와 단계 경계는 동일하다.

일반·프로의 감점 감소와 8065880의 −15점은 새 X-Factor가 기존 20° 하한을 통과하는지에 따른 변화다. 프로·35546329의 추가 +8점은 새 어깨 최대가 기존 60° 기준을 통과한 결과다. 점수 상승이나 하락을 실제 스윙 품질 개선/악화로 판정하지 않는다.

## 6. GolfDB 50개: 음수·촬영 방향·규모

| 방향 | n | 음수 전→후 | 중앙값 전→후 | 범위 전→후 | 3D 톱 사용 | 기존 20–80° 안 전→후 |
|---|---:|---:|---:|---|---:|---:|
| face-on | 25 | 7/25 (28%)→2/25 (8%) | 9.7→16.8 | −33.2–56.3→−10.1–39.9 | 25/25 | 10→8 |
| DTL | 25 | 5/25 (20%)→3/25 (12%) | 12.7→19.3 | −26.5–54.9→−26.5–54.9 | 12/25 | 7→12 |
| 전체 | 50 | 12/50 (24%)→5/50 (10%) | 10.9→17.05 | −33.2–56.3→−26.5–54.9 | 37/50 | 17→20 |

기본 결과에는 13개 DTL 폴백이 포함된다. **유효 3D 37개만** 보면 음수 2/37 (5.4%), 중앙값 19.3°, 20–80° 안 17/37 (45.9%)다. 음수 2개는 face-on ID 42·169이며 각각 −5.5°·−10.1°로 남겼다. DTL의 음수 3개는 기존 2D 폴백이다.

방향별 기본 결과 중앙값 차이 `|DTL−face-on|`는 **3.0→2.5°**. 그러나 **유효 3D만의** 중앙값은 face-on 16.8°, DTL 34.05°로 차이가 **17.25°**다. 방향별 유효율도 100% 대 48%로 다르다. 서로 다른 골퍼·스윙의 비대응 표본이므로 어떤 숫자도 같은 스윙의 카메라 오차가 아니다. 촬영 방향 불변성이 입증됐다고 결론 내리지 않는다.

수십 도의 결과도 있으나 주니어/클럽/숙련도 구성이 통제되지 않았고 문헌과 좌표·초기 오프셋·필터·톱 정의가 다르다. 20° 미만 결과가 상당하며, 문헌 규모에 맞추기 위한 보정·클리핑은 하지 않았다.

GolfDB 점수 평균은 **63.70→65.24**. 변화별 영상 수는 −23:2, −15:7, 0:27, +8:2, +15:8, +23:4다. 영상별 점수와 delta 50행은 comparison.csv에 있다. 점수 임계값은 동일하다.

독립 리뷰에서 ID 19의 원시 어깨 heading f100–102가 −171.08→5.07→−175.40°로 뒤집혔고, 보호 없는 unwrap에서 상대각 362.7°가 생긴 사례를 발견했다. ID 25 역시 방향 반전으로 전체 어깨 평균이 −121.5°였다. 120° ambiguity guard 적용 후 ID 25의 해당 f115는 폴백하고 평균은 −20.2°가 됐다. 이 보호가 작은 방향 오류나 모든 지속적 오추정을 해결한다는 의미는 아니다.

## 7. Mac↔Docker와 스냅샷

| 비교 | before | after | 판정 |
|---|---|---|---|
| 동일 7개 영상 native Mac 포즈↔Docker | Mac 7개 모두 추론 초기화 실패 | 같은 제약 | **측정 불가**, 차이 감소 주장 없음 |
| 동일 Docker 포즈 입력의 Mac 수치 재계산 | 이전 지표를 입력으로 보존 | 7개 summary·점수 정확히 일치, X-Factor 차이 0.0° | 계산식의 플랫폼 일치만 확인, native 포즈 비교 대체 아님 |

Mac 실패는 `Service kGpuService ... Could not create an NSOpenGLPixelFormat`이다. [실패 기록](mac_pose_failures.json), [수치 재계산 기록](mac_math_parity.json). Mac Python 3.12.4/arm64, MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4. 서버·ngrok를 우회 사용하지 않았다.

전체 일반 원본을 사용하는 Docker 스냅샷은 자동 트림 비교와 별개다. 기존 기준으로는 의도된 점수 차이 때문에 1 failed/49 passed였고, Docker에서 재생성 후 최종 51 passed였다.

| 일반 전체 영상 스냅샷 | 전 | 후 |
|---|---:|---:|
| 점수 | 45 | 60 |
| X-Factor | −23.8 | 24.5 |
| 어깨 최대 | 33.9 | 39.0 |
| 척추각 변화량 | 9.0 | 9.0 |
| 집계 프레임 | 93 | 93 |
| 검출 단계 | 7 | 7 |

전/후 파이프라인이 같은 전체 영상을 사용한다. 자동 트림의 26.2°와 전체 원본의 24.5°는 포즈 tracker·스무딩의 시작 문맥이 달라 생긴 값이며 환경 비교로 섞지 않는다.

## 8. 임계값 재설정 제안 — 적용하지 않음

X-Factor 20–80°, 어깨 60°, 척추 7/12°, 무릎 165°, 왼팔 140°와 ref_db n≥2 폴백은 유지했다. 새로운 정의에 맞는 숫자 임계값은 이번 비정답 데이터로 결정하지 않는다.

후속으로 좌표계·절대/어드레스 상대·필터·톱 이벤트를 고정한 뒤, 같은 골퍼·같은 스윙의 동시 face-on/DTL와 모션캡처를 확보할 것을 제안한다. 유효 3D·2D 폴백·서로 다른 지표 버전의 reference 통계를 분리하고, 클럽·숙련도별 개발 표본으로 기준을 추정한 뒤 별도 표본에서 검증한다. 기존 reference 누적 구조에 두 정의를 섞지 않는 버전 관리도 필요하다. 현재 50개 중앙값에 맞춰 하한을 내리는 변경은 제안하지 않는다.

## 9. 검증·환경·재현

모든 기준 포즈는 `golf-server:baseline`, linux/amd64, image `sha256:1ebff936e1e5f666cac7a3b451b5ecf57ba0b5ae6197424899122b9d267e2e06`, Python 3.11.17, MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4에서 생성했다. Docker는 네트워크 없이 실행했다. 원자료는 read-only mount, 출력은 별도 `/Users/mose/datasets/xfactor_eval`에 썼다.

- 기준선 pytest 29 passed → 새 rotation 단위 테스트 22 passed → 최종 전체 **51 passed** ([로그](pytest.log)). 기존 FastAPI lifespan 경고 2개.
- 실제 feature 파이프라인 앱 7개 모두 before와 같은 단계 경계·frame/annotated/trajectory 키, 캐시 after와 같은 summary·점수. 대표 이미지 7개씩. [기록](pipeline_verification.json).
- 프로2는 기존부터 어드레스 각도 행이 없어 지표 phase_stats는 6개, 검출 경계·이미지는 7개다. 사진을 위해 각도를 합성하지 않았다.
- 기존 2D selector와 구형 live payload의 점수 보존, yaw·좌우 부호, 음수 분리, 정상 180° 통과, pose 반전·복구, 정확한 톱 실패, 기준 자세 실패, visibility·NaN·퇴화 투영을 검증했다.
- `compute_score()`/단계 검출/기존 스무딩의 동일성은 [sources.json](sources.json)에 기록했다. 독립 읽기 전용 A1–A9 리뷰에서 위반 없음. 리뷰 발견사항인 반전 보호·어깨 설명을 수정했고 최종 테스트는 이 수정 이후 실행했다.
- `npm run build -- --configLoader runner`, `npm run lint` 성공 ([build](web_build.log), [lint](web_lint.log)). lint 경고 18개와 큰 bundle 경고는 남아 있다. 브라우저 클릭 E2E는 수행하지 않았다.
- node_modules가 발표용 레포를 가리켜 build info는 임시 tsconfig 수정으로 `/private/tmp/xfactor-*.tsbuildinfo`에 썼고 원문을 복원했다. runner loader로 발표용 node_modules에 Vite 임시 config를 쓰지 않았다. build 결과는 이 작업 폴더의 web/dist다.
- Docker에 pytest가 없어 이전 검증 때 준비된 `/private/tmp/phase_testdeps`를 read-only mount했다. 새 설치 없이 `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`·`PYTHONPATH=/testdeps`, cacheprovider 비활성화로 전체 테스트를 실행했다.

재현 명령과 산출물 경로는 [COMMANDS.md](COMMANDS.md)에 정리했다. capture는 기존 결과를 건너뛰므로 새 측정에는 별도의 output 경로를 사용한다. summarize는 같은 포즈의 after 지표만 최신 코드로 다시 계산한다. 영상·이미지는 보고서 저장소에 넣지 않았다.

## 10. 커밋 묶음 제안 — 실행하지 않음

200줄은 추가+삭제 합이다. 신규 파일도 전체 줄 수로 센다. 생성 1줄 JSON은 줄 수가 작아도 내용 검토가 필요하다. snapshot은 pipeline/scoring 선택 변경과 같은 묶음이다.

| 묶음 | 내용 | 변경 줄 수 |
|---|---|---:|
| 1 | geometry 새 함수 + rotation.py | 21+125 = 146 |
| 2 | pipeline/scoring 적용 + 일반 snapshot | 17+12+6 = 35 |
| 3 | test_xfactor.py | 145 |
| 4 | web 타입·설명·폴백 + Streamlit 설명 + 샘플 JSON 3개 | 13+16+11+6+6 = 52 |
| 5 | tools/xfactor_eval.py | 173 |
| 6 | tools/xfactor_verify.py + xfactor_math_parity.py | 49+28 = 77 |
| 7 | REPORT.md | 200줄 이하 유지 |
| 8 | COMMANDS.md + selection.json + metrics.json | 95+52+18 = 165 |
| 9 | comparison.csv + sources + pipeline/native 실패/수치 재계산 기록 + 검증 로그 3개 | 176 |

전체 묶음 적용 후 통합 검증을 유지한다. 기존 사용자 파일 `.venv`, `codex-impl-xfactor.md`, `codex_run.log`는 이 제안에서 제외하고 보존한다. 커밋·스테이징·dev 반영은 실행하지 않았다.
