# 7단계 분할·자동 구간 감지 진단 보고서

2026-10-12 · Swing.Lab · 원인 분석만 수행 · 앱 코드 수정/패키지 설치/git 커밋 없음

**한 줄 결론 — “프레임 수 부족”은 부분 지지: 동일 GolfDB 50개에서 30→15→10fps 분석 시 Impact PCE가 88%→68%→42%, 실제 다운스윙 유효 관측 중앙값이 9→4→3개로 감소했다. 그러나 인덱스 불일치·결측 시간 압축·다중 스윙/장면 전환·정지 구간 강제 분할은 별도로 고쳐야 한다.**

같은 일반 샘플 구간(1.5–9.7초)도 매 프레임 분석하면 Impact 경계가 원본 f90(3.00초), 2프레임 간격이면 f167(5.57초)으로 달라졌다. 따라서 프레임 부족을 기각할 수 없다. 반대로 매 프레임 GolfDB에서도 Address 0%, Top 18%, Finish 4%여서 샘플 수 증대만으로 7단계 정의와 구간 선택 문제가 해결되지는 않는다.

## 1. 원인 순위

순위는 현재 증상 설명력과 수정 선행 관계 기준이다. 수치는 아래의 동일 Docker 환경 실험이며 문헌 수치와 합산하지 않았다.

| 순위 | 원인 | 증상 | 코드·실험·문헌 근거 | 확신도 |
|---|---|---|---|---|
| 1 | 한 번의 스윙이라는 전제가 깨짐: 자동 구간이 컷/다음 스윙/연습 동작을 포함하고 검출기는 다른 사이클의 극값을 연결 | S1·S3·S4 | 일반 선택 1.5–9.7초에 f162 컷 포함, Impact f167·Finish 대표 f273. 프로 f366 이후는 다음 정면 장면. 어려운 영상의 실제 샷 21.4초를 자동 2.8–10.1초가 제외. `pipeline.py:144–178`, `phase_detector.py:109–126`. L1은 단일 스윙 이벤트 문제 | 높음 |
| 2 | 시간/이미지 인덱스의 서로 다른 기준을 혼용 | S2 및 타임라인 | `rep_i` 대 `local_idx` 불일치: 녹색 셔츠 K=36, 108원본 프레임(4.5초); 빨간 셔츠 7.6초 시작 재현 K=39, 78프레임(2.6초). 전체 빨간 영상의 Impact UI 5.1초 대 실제 대응 11.3초. `serialization.py:37–47`, `pipeline.py:266–352`, `SwingReplay.tsx:23–26` | 결함 높음; S2 원래 세션의 정확한 K는 미확인 |
| 3 | fps를 낮추는 샘플링 + fps와 무관한 스무딩/탐색 규칙 | S1·S3·S4를 악화 | 50개 paired Impact 44/50→34/50→21/50. 고정된 포즈 신호만 솎아도 88→72→44%. `pipeline.py:208–216`, `phase_detector.py:62–63`. L4의 다운스윙 약 0.3초 | 높음 |
| 4 | 6관절 전부 가시성 조건 및 결측 처리: 손목 신호 삭제·이전 각도 복사 | S2·S4 | GolfDB DTL 유효율 중앙값 62.0%(30fps), 정면 100%. 어려운 원본 유효율 38.6%, 각도 복사 55.8%. 빨간 원본 연속 결측 6.2초. `pipeline.py:272–338`. L5/L6은 포즈 한계의 보조 근거 | 높음; 좌표의 실제 오차 크기는 미확인 |
| 5 | 스윙 존재/단계 순서 검증 없음, 단계 폭이 전체 길이에 비례 | S5·S4 | 실제 정지 36프레임이 7개 구간/7개 라벨로 분할. 상수 120개에도 경계 7개, Down [10,9] 역전. 동일 스윙 앞뒤 0/1/3초 정지 시 Down 라벨 6/4/1개. `phase_detector.py:57–145` | 높음 |
| 6 | 손목 Y만으로 클럽 이벤트·Finish를 정의하는 한계 | S1·S3·S4 | 30fps에서도 Top 오차 중앙값 −2프레임, Finish 절대오차 중앙값 12프레임. 좌우 손목 교환은 평균 차이 0, 경계 동일. 일반의 계단 급락은 f161→163 영상 컷. L1 이벤트 정의와 L2 손목 기반 방법 구별 필요 | 정의 차이 높음; 각 오차의 생체역학적 원인 분해는 부분 확인 |

## 2. H1–H8 판정

| 가설 | 판정 | 수치·해석 | 재검토할 실험 파일 |
|---|---|---|---|
| H1 대표 장면 인덱스가 주원인 | **부분 지지** | 실제 결함 확인. 녹색 K36, 빨간 7.6초 시작 K39. S1·S3 샘플 K0이므로 이 두 증상의 주원인이라는 주장은 기각. S2와 같은 첫 6장 준비 자세(그중 무관절 표시 5장)를 부분 재현했지만 원래 업로드 세션의 K는 미확인 | `representative_mapping.csv`, `s2_candidate_7.6.json`, `*_snapshot.json`, `s2_screenshot_matches.json` |
| H2 프레임 부족 | **부분 지지** | (a) 일반 같은 구간 step1/2/3 Impact f90/f167/f279; 7개 영상 전체 비교도 수행. (b) paired 50개 Impact PCE 88/68/42%. (c) GT Top–Impact 유효 관측 중앙값 9/4/3, 범위 0–31/0–16/0–10 | `sample_boundaries.csv`, `il-ban_snapshot_rate*.json`, `golfdb_results.json`, `golfdb_summary.csv` |
| H3 포즈 미검출·가시성 탈락 | **지지** | 원본 빨간/어려운 사례에서 포즈 자체 검출 100%여도 6관절 통과 68.2/38.6%; 이 둘을 혼동하면 원인을 놓침. 연속 결측 6.2/6.13초. 손목 가시도는 현재 gate에 들어 있지 않음 | `pose_metrics.csv`, 영상별 `*_trace.csv`, `*_signals.png` |
| H4 규칙 가정 위반 | **지지, 일부 주장 제한** | 실제 정지 클립은 7단계. 컷 포함 시 다른 스윙 연결. 단, 검증한 단일 스윙의 0/1/3초 패딩에서는 Top f81·Impact f90이 유지되어 “정지만 붙이면 항상 경계가 붕괴”는 지지하지 않음. 단계 폭은 붕괴 | `control_summary.csv`, `control_*.json`, `signal_invariants.json` |
| H5 손목 Y 신호 문제 | **부분 지지** | S1 최대 점프 ΔY=0.26667(영상 높이 비율), f161→163에서 양 손목 동시 변화, 실제 컷 f162. 순수 좌우 교환은 평균/경계 불변이라 계단 원인으로 기각. 손목 기반 Top의 조기 편향은 관찰되지만 모든 오차를 클럽 지연으로 단정 불가 | `signal_invariants.json`, `il-ban_cut_manual.png`, `golfdb_summary.csv` |
| H6 자동 구간 감지 | **지지** | 7개 모두 원본/비율 보존 비교. 세로 3개 스캔 pose율 93.8/79.7/82.6%→각 100%, 그러나 어려운 샷은 두 방식 모두 창 IoU=0. 1.2초 정지 클립은 검사 없이 전체 반환 | `auto_window_comparison.csv`, `auto_*_*.json`, `control_static_ilban.json` |
| H7 촬영 방향 의존 | **부분 지지** | 각각 25개: 30fps Impact 정면 100% 대 DTL 76%, 15fps 96% 대 40%, 10fps 56% 대 28%. 서로 다른 영상이므로 방향만의 인과 효과 아님. 후방의 손목 규칙 자체가 불가능하다는 명제도 L2와 맞지 않음 | `golfdb_selection.json`, `golfdb_summary.csv`, `pose_metrics.csv` |
| H8 오래된 프로 JSON | **기각(현재 코드와 다른 오래된 결과라는 설명)** | 일반/프로/프로2를 실제 trim→process로 재분석: frame_data·모든 경계 정확히 동일, 손목 최대 차이 0. 점수 55/67/42 동일. JSON을 다시 생성하기만 하면 같은 오류가 돌아옴 | `pro_snapshot.json` 등 `stored_comparison`, `*_snapshot_annotated.png` |

## 3. 해결책 후보

아래는 **미구현 제안**이다. 줄 수는 테스트·문서·생성 JSON을 제외한 대략적인 변경/추가 규모로, 실제 diff가 아니다. 점수 수치의 변화와 점수 기준 자체의 변경은 구별했다.

| 후보 | 고치는 원인 | 예상 효과/측정한 효과 | 예상 수정 파일 | 줄 수 추정 | 위험·재생성 | 새 의존성 |
|---|---|---|---|---|---|---|
| A. 대표 이미지에 원본 frame ID를 보존해 조회; 단기 local_idx 매핑을 양 UI에 동시 적용 | H1 | 녹색의 7장 각각 108프레임, 빨간 7.6초 시작 78프레임의 이미지 조회 오차 제거. 단계 판정 오류까지 해결하지는 않음 | `server/serialization.py`, `ui/tab_analysis.py`, 필요시 `analyzer/pipeline.py` | 20–60 | A8 양쪽 동기화. local_idx도 pose-only이므로 장기 키는 원본 frame. 점수 기준 불변; rep_frames 재생성 | 없음 |
| B. history→원본 frame/time 매핑을 응답에 명시하고 재생·파형에 적용 | 결측 시간 압축 | 빨간 전체의 Impact 표시 5.1→11.3초, Finish 시작 7.1→13.3초로 원본 매핑 복원. 이벤트가 정확하다는 의미는 아님 | `analyzer/phase_detector.py`, `pipeline.py`, `server/main.py`, `web/src/lib/types.ts`, `SwingReplay.tsx`, `Waveform.tsx` | 70–150 | API 계약과 오래된 JSON 호환 처리. 점수 기준 불변; 스냅샷 필드 재생성 | 없음 |
| C. 정지/부분 스윙/역전 경계의 명시적 분석 불가 판정; 단계별 최소 증거 요구 | H4·S5 | 정지 36프레임과 상수 120개를 거부해야 함. 이번 실험은 반례 확인이며 임계값 성능은 미측정 | `phase_detector.py`, `pipeline.py`, 결과 직렬화·결과 UI | 80–180 | 기존에 점수 나왔던 영상이 거부될 수 있음. 거부 상태 설계 필요, 기준 숫자를 바꾸지 않아도 결과 커버리지가 변함 | 없음 |
| D. 컷·여러 사이클을 분리하고 완전한 후보를 선택; 검증된 한 사이클만 다음 분석에 전달 | H4·H6 | 일반 f45–160 단일 사이클 실험에서 Top81·Impact90, 현행 스냅샷 Impact167의 오류 제거. 어려운 사례의 연습 동작/실제 샷 분리는 추가 검증 필요 | `pipeline.py:auto_detect_swing_window`, `phase_detector.py`, 구간 선택 UI | 150–350 | 스윙 후보 선택의 의미 변경, 저장 샘플 전부 재생성. 단계 기반 점수/코칭 재검증 필요 | 기본안 없음 |
| E. 자동 스캔의 종횡비 유지·실제 타임스탬프 사용 | H6 | 세로 3개 검출률 모두 100%로 개선. 일반 창 IoU 0.467→0.518; 어려운 영상은 0→0이라 단독 처방 불충분 | `pipeline.py:83–178` | 20–60 | 축소 후 인물 픽셀 수 감소 가능. 다른 영상에서의 회귀 확인, 스냅샷 재생성 | 없음 |
| F. 단일 스윙을 먼저 자르고 충분한 원본 fps로 분석; fps 기준 필터·최소 구간 폭 | H2·H4 | GolfDB 10→30fps Impact 42→88%(관찰 결과, 새 코드 보장값 아님). 고정 포즈 10fps에서 시간 폭을 근사한 필터는 44→68%, Top은 2→4%에 그침 | `pipeline.py:208–216`, `phase_detector.py:62–117` | 60–140 | CPU 비용 증가; 경계·각도 집계·점수 변동. 같은 데이터로 임계값 튜닝 후 성능 주장 금지. 스냅샷/스코어 회귀 재검증 | 없음 |
| G. 이벤트용 손목 품질과 각도용 6관절 품질을 분리, 짧은 결측만 시간 기반 보간 | H3 | 부적절한 손목 삭제를 줄일 여지. 무제한 선형 채우기 탐색은 30fps PCE 개선 0, 10fps Impact 44→50%, Top 2→0%; 그대로 채택할 근거 부족 | `pipeline.py:272–338`, `phase_detector.py` | 70–160 | 긴 가림을 가짜 동작으로 채우지 않도록 상한/거부 필수. 각도·점수 신뢰도 정책과 스냅샷 변경 | 없음 |
| H. 클럽/손목·자세 시계열 또는 영상 기반 이벤트 모델을 별도 평가 | H5·H7, 규칙의 정확도 한계 | L1/L3은 학습 기반의 가능성을 보이나 본 앱 개선량은 미확인. 먼저 같은 split/영상/허용오차로 외부 검증 | 새 이벤트 추론 모듈, `pipeline.py`, 모델 자산·응답 스키마 | 300–800+ | 모델·가중치·학습 영상 상용 권리 각각 확인. 이벤트 정의 및 점수 입력 변경. 배포/성능 비용 | PyTorch/MMPose 등 후보, 이번에 설치 안 함 |
| I. RIFE/SR 전처리 | H2·H3의 후보 보조책 | 골프 이벤트 개선 미확인. L7은 보행 시간 지표 개선, L9는 큰 움직임 아티팩트. 우선순위 낮음 | 별도 전처리 실험 모듈 | 150–400+ | 생성 손목/클럽이 잘못된 이벤트 증거가 될 수 있음. 추가 GPU 비용·가중치 권리 확인 | RIFE/PyTorch 또는 SR 모델 |

## 4. 권장 실행 순서

1. **바로 고칠 버그:** A/B로 원본 frame/time 계약을 먼저 고정하고, C의 무동작/역전 경계 거부를 넣는다. 정지 영상에서 점수·코칭을 생성하지 않는 실패 경로를 마련한다. 저장 이미지와 UI seek가 같은 원본 프레임을 가리키는지 확인한다.
2. **규칙 개선:** D/E로 한 사이클 구간과 비율을 바로잡고 F의 원본 fps 확보·시간 기반 필터를 적용한다. G는 신호 품질을 분리하되 긴 결측을 채우지 않는다. 앱 7구간과 GolfDB 이벤트 정의를 명시하고 독립 split에서 Top/Address/Finish를 평가한다. 고정 +2프레임 보정은 현재 데이터에 맞춘 임시방편이므로 바로 제품화하지 않는다.
3. **학습 기반 전환 검토:** 위 버그가 없는 입력으로 H를 규칙 기준선과 비교한다. 학습/평가 데이터의 비상업 조건을 지키며 코드·가중치·데이터 권리를 별도로 확인한다. I는 그 뒤 제한된 실패 사례에서 검증한다. 프레임 보간을 가장 먼저 도입할 근거는 없다.

①만으로 정확한 이벤트 검출기가 완성되는 것은 아니다. 어느 단계에서든 분석 단계가 바뀌면 샘플 JSON과 단계 의존 점수·코칭을 함께 재검증해야 한다.

## 5. 문헌·오픈소스 조사 (R1–R5)

확인일 2026-10-12. 아래 URL을 이번 실행에서 실제 열어 제목/본문 또는 LICENSE 내용을 확인했다. 성능 수치는 논문 본문·초록에서만 가져왔다. 저장소 README는 구현·가중치·환경의 존재 확인에만 사용했다. 논문 결과는 본 레포의 실험 결과와 직접 비교하지 않는다.

| ID / RQ | 실제 확인한 논문·공식 URL | 확인 수준·위치 | 확인 내용과 적용 한계 |
|---|---|---|---|
| L1 / R1·R2 | McNally et al., **GolfDB: A Video Database for Golf Swing Sequencing** (2019), [공식 저자 공개본](https://arxiv.org/pdf/1903.06528) | **본문 확인**, §3 p.3, §4.3 pp.4–5, Table 2 p.8 | MobileNetV2+양방향 LSTM. 8이벤트 전체 PCE 76.1%, Top 83.9%, Impact 98.4%. 클럽 방향 반전이 Top, 클럽–공 접촉이 Impact, 최종 자세를 풀기 직전이 Finish. 단일 스윙으로 자른 영상의 이벤트 검출이며 긴 원본에서 스윙을 찾는 문제와 구별한다. 앱의 7구간 중 4개 시작점 평가와 수치 직접 비교 불가. |
| L2 / R1·R3 | Yamamoto et al., **Extracting proficiency differences and individual characteristics in golfers’ swing using single-video markerless motion analysis** (2023), [DOI가 포함된 출판사 원문](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2023.1272038/full) | **본문 확인**, §§2.2, 2.3.1–2.3.3 | DTL/시상면 240 Hz 영상에 HRNet 인체 포즈와 DeepLabCut 클럽 추적을 사용. 오른 손목 수직 궤적으로 Address/Top/Impact/Finish를 찾고 6 Hz Butterworth 필터를 사용한다. Address는 손목 상승 검출보다 30프레임(0.125초) 앞. 손목 규칙 자체가 후방에서 원천적으로 불가능하다는 근거가 아니다. 이 논문의 숙련도 분석을 이벤트 PCE 검증으로 읽을 수 없다. DOI: 10.3389/fspor.2023.1272038. |
| L3 / R1 | Jung et al., **CaddieSet: A Golf Swing Dataset with Human Joint Features and Ball Information** (CVPRW 2025), [공식 저자 공개본](https://arxiv.org/pdf/2508.20491) | **본문 확인**, §3.2 p.4, Supplement A p.10 | SwingNet을 추가 학습한 뒤 이벤트별 Faster R-CNN/HRNet 포즈를 추출. 보충자료의 8이벤트 accuracy 78.0%, Address·Finish 제외 94.1%. 골프 이벤트와 포즈/볼 결과를 연결한 후속 방법이지만 일반 스마트폰 영상에 대한 외부 검증치는 아니다. 모델이 추정한 관절은 모션캡처 정답이 아니다. |
| L4 / R2 | Choi et al., **Kinematic evaluation of movement smoothness in golf: relationship between the normalized jerk cost of body joints and the clubhead** (2014), [공식 PMC 원문](https://pmc.ncbi.nlm.nih.gov/articles/PMC3941698/) | **본문 확인**, Methods, Table 1 | 다운스윙 0.307±0.04초(숙련 20명), 0.327±0.04초(비숙련 19명); Vicon 120 Hz. 이 수치는 물리적 동작 시간이며 스마트폰 이벤트 검출의 필요 fps를 직접 비교한 실험이 아니다. DOI: 10.1186/1475-925X-13-20. |
| L5 / R3 | Yuan & Ndongmo, **On the Utility of Pose Estimation Models for Golf Swing Understanding** (저널 2026, 공개 2025-12-22), [출판사 PDF](https://file.scirp.org/pdf/jdaip_2870855.pdf) | **본문 확인**, Abstract p.40, §§2–3 pp.41–44 | 골프 영상의 빠른 동작·가림·환경 변화 문제를 다룬다. 초록 mean OKS: MediaPipe 0.636, YOLO 0.604. 이는 이벤트 정확도나 본 프로젝트의 오류율이 아니다. 표본 구성/모델 설정의 재현성 한계가 있어 보조 근거로만 사용. DOI: 10.4236/jdaip.2026.141003. |
| L6 / R3 | **MediaPipe Pose** 공식 Legacy Solutions 문서, [원문](https://chuoling.github.io/mediapipe/solutions/pose.html) | **공식 문서 본문 확인**, Pose Estimation Quality / ML Pipeline / Output | 평가 대상은 Yoga·Dance·HIIT, 카메라 2–4 m 거리의 한 사람이다. 골프 DTL 검증값이 아니다. visibility는 관절의 가시성 추정값이며 실제 좌표 오차의 보증이 아니다. 검출 후 이전 포즈에서 ROI를 이어가므로 프레임 솎기는 단순 시간 양자화 외에 추적 입력도 바꾼다. |
| L7 / R4 | Dunn et al., **Application of video frame interpolation to markerless, single-camera gait analysis** (2023), [출판사 원문](https://link.springer.com/article/10.1007/s12283-023-00419-3) | **본문 확인**, §2.3, §3/Table 1 | RIFE로 보행 영상 25→100 Hz, 이후 OpenPose. 시간 지표 RMSE가 0.005–0.008초 감소. 좌우 다리 오인 수동 수정·짧은 결측 보간·필터도 함께 사용. 보행에서의 개선이며 골프 클럽/임팩트, 무보정 MediaPipe에 그대로 전이되는지는 **미확인**. DOI: 10.1007/s12283-023-00419-3. |
| L8 / R4 | Huang et al., **Real-Time Intermediate Flow Estimation for Video Frame Interpolation** (ECCV 2022), [공식 arXiv 초록](https://arxiv.org/abs/2011.06294) | **초록만 확인**; PDF 열기는 크기 제한으로 실패 | IFNet과 intermediate flow로 중간 영상을 생성한다. 골프 이벤트/인체 포즈 개선 검증은 이 초록에 없다. 생성 프레임 수 증가를 실제 관측 증가로 취급하지 않는다. |
| L9 / R4 | **EGVD: Event-Guided Video Diffusion Model for Physically Realistic Large-Motion Frame Interpolation**, [공식 저자 공개본](https://arxiv.org/pdf/2503.20268) | **본문 확인**, §4.3.2, Fig.3, PDF pp.6–8 | 비교 실험에서 RIFE의 큰 움직임 위치 오류와 비강체 인체의 변형·경계 아티팩트를 보고한다. 골프 특화 평가는 아니므로 본 앱의 손목 오차 크기를 여기서 추정하지 않는다. 영상의 시각 품질 지표와 이벤트 정확도는 다르다. |
| L10 / R4 | Hardy et al., **Can Super Resolution be used to improve Human Pose Estimation in Low Resolution Scenarios?** (2021), [공식 arXiv 초록](https://arxiv.org/abs/2107.02108) | **초록만 확인** | 작은 인물의 keypoint 성능은 SR로 개선되지만 원래 인물 픽셀 면적이 커지면 성능 저하도 관찰. 골프/MediaPipe 이벤트 개선 수치는 **미확인**. 일괄 SR 전처리를 우선 처방할 근거가 아니다. |

**R2에서 확인하지 못한 것:** 동일 골프 이벤트 검출기를 실제 촬영 30/60/120/240fps에서 통제 비교한 오류 표는 이번 조사에서 확인하지 못했다. 30→15→10fps 실험은 본 보고서의 직접 근거이고, 이를 60/120/240fps의 실측 개선량으로 외삽하지 않는다. 순수 시간 격자의 반 간격은 각각 16.67/8.33/4.17/2.08 ms이고, 0.3초 동작의 평균 관측 수는 9/18/36/72이다. 이는 `1/(2fps)`, `0.3×fps`의 **산술 계산**이며 센서·블러·포즈·알고리즘 오차를 포함한 성능 수치가 아니다.

| R5 후보 | 코드·가중치·데이터 제공 | 실제 열어 확인한 라이선스 | 상업 이용·환경·확인 수준 |
|---|---|---|---|
| [SwingNet / GolfDB](https://github.com/wmcnally/golfdb) | README에 PyTorch 코드, 사전학습 가중치 다운로드, 160×160 클립 링크 있음 | [LICENSE 경로](https://raw.githubusercontent.com/wmcnally/golfdb/master/LICENSE)는 **404**. [루트 파일 목록](https://api.github.com/repos/wmcnally/golfdb/contents)에도 LICENSE 없음. [README](https://raw.githubusercontent.com/wmcnally/golfdb/master/README.md)는 CC BY-NC 4.0 선언 | 사용자 출처 규칙대로 **라이선스 파일 없음(신규 도입은 사용 불가 취급)**. README 선언만으로 상용 허가하지 않음. 기존 로컬 GolfDB는 이번 요청에 따라 비상업 평가만 수행. 코드의 GPU 필수 여부는 미확인; 논문 Table 3에는 CPU 추론 평가 있음. 가중치·영상 권리를 코드 선언과 동일시하지 않는다. |
| [MediaPipe](https://github.com/google-ai-edge/mediapipe) | 현재 설치된 Pose 모델·코드; [공식 모델 가이드](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker) | [LICENSE](https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/LICENSE), **Apache-2.0**, 원문 확인 | 코드 상용 가능(고지 조건). 특정 배포 가중치의 별도 권리 범위는 배포 전 재확인. 현재 Docker CPU 실행 검증 완료, Mac 본 세션은 OpenGL 초기화 실패. |
| [MMPose / HRNet·RTMPose](https://github.com/open-mmlab/mmpose) | 코드와 모델 저장소·가중치 링크 제공; [설치 문서](https://raw.githubusercontent.com/open-mmlab/mmpose/main/docs/en/installation.md) | [LICENSE](https://raw.githubusercontent.com/open-mmlab/mmpose/main/LICENSE), **Apache-2.0**, 원문 확인 | 코드 상용 가능(고지 조건). PyTorch/MMCV/MMEngine 필요. CPU-only 설치 경로가 있고 GPU는 학습/속도상 유리. 골프 특화 성능·개별 체크포인트 학습자료의 상용 권리는 **미확인**. 이번에 설치하지 않음. |
| [RIFE](https://github.com/hzwer/ECCV2022-RIFE) | PyTorch 코드·[공식 README의 사전학습 모델 링크](https://raw.githubusercontent.com/hzwer/ECCV2022-RIFE/main/README.md) | [LICENSE](https://raw.githubusercontent.com/hzwer/ECCV2022-RIFE/main/LICENSE), **MIT**, 원문 확인 | 코드 상용 가능(고지 조건). CUDA GPU 활용 경로 제공. 배포 모델 링크 존재만 확인했고 별도 가중치 허가 범위는 **미확인**. 골프 이벤트 개선 실험 없음. 이번에 설치하지 않음. |
| [CaddieSet](https://github.com/damilab/CaddieSet) | [README](https://raw.githubusercontent.com/damilab/CaddieSet/main/README.md)에 특징/볼 결과 데이터. 독립된 이벤트 검출 사전학습 모델의 사용 가능성은 미확인 | [LICENSE](https://raw.githubusercontent.com/damilab/CaddieSet/main/LICENSE), **MIT**, 원문 확인 | 저장소의 software/문서 대상 MIT. 원본 골프 영상 전체의 권리까지 확대하지 않음. 표 데이터는 CPU 처리 가능; 본 평가의 프레임 정답 대체물은 아님. |
| [GolfPose](https://github.com/MingHanLee/GolfPose) | [README](https://raw.githubusercontent.com/MingHanLee/GolfPose/main/README.md)의 이메일 신청 데이터셋. 즉시 다운로드 가능한 완제품 이벤트 모델은 미확인 | [LICENSE](https://raw.githubusercontent.com/MingHanLee/GolfPose/main/LICENSE), **맞춤 Dataset EULA**, 원문 확인 §§1–3 | 내부 연구·평가·학습, 파생 모델 상용화 허용. 원자료 재배포·재판매 금지, 출처 표기 요구. 무료 오픈소스 코드 라이선스와 구별. 특정 모델 GPU 요구량 미확인. |
| [Hybrid CNN–TCN](https://github.com/nadaselham/Hybrid-CNN-TCN) | [README](https://raw.githubusercontent.com/nadaselham/Hybrid-CNN-TCN/main/README.md)에 시계열 관절 회귀 코드·학습법. 사전학습 가중치 **미확인** | [LICENSE](https://raw.githubusercontent.com/nadaselham/Hybrid-CNN-TCN/main/LICENSE), **MIT**, 원문 확인 | 코드 상용 가능(고지 조건), GolfDB 권리는 별도. GPU/실행 재현성 미확인. 논문 출판사 URL은 접근 실패하여 성능 근거에서 제외. |

확인 실패 기록: CVF GolfDB/CaddieSet PDF 직접 접근은 오류여서 arXiv 저자 공개본으로 제목·본문을 검증했다. GolfMate 출판사 HTML/PDF와 PeerJ `10.7717/peerj-cs.3664` 본문은 403/429 등으로 열리지 않아 논문 성능 근거에서 제외했다. 블로그·서비스 마케팅 페이지의 정확도·권장 fps는 채택하지 않았다.

## 6. 실행 환경·방법·해석 범위

- 코드 기준 HEAD `e3afac2c73f0b55216b51220e02c17de6a719e3d`. 샘플 JSON의 마지막 관련 변경 `e973fb6`도 확인했다. 코드와 주석이 다르면 실행 코드를 기준으로 했다.
- **모든 포즈 수치: 기존 `golf-server:baseline` Docker, linux/amd64**, Python 3.11.17, MediaPipe 0.10.21, OpenCV 4.10.0.84, NumPy 1.26.4. 이미지 ID `sha256:1ebff936e1e5f666cac7a3b451b5ecf57ba0b5ae6197424899122b9d267e2e06`. 네트워크 차단, repo read-only mount, 결과 폴더만 쓰기 mount.
- Mac `.venv` Python 3.12.4/arm64에서는 `Could not create an NSOpenGLPixelFormat`으로 MediaPipe 초기화 실패. Mac은 이미지 디코딩·집계·그래프 생성에만 사용했고 Mac 포즈 수치를 Docker와 섞지 않았다. 패키지 상세/소스 SHA는 `data/environment_*.json`.
- 진단용 `process_video` 복사본을 메모리에서 계측했다. 선택 구간·샘플 간격을 지정하고 포즈/가시도/원본 프레임을 기록한다. 영상에 그리는 작업만 건너뛰어 메모리를 절약했다. 실제 import한 원래 `trim_video`→`process_video`로 샘플 3개와 빨간 기본 자동 구간을 별도 실행하여 frame_data·손목·경계 완전 일치를 assert했다. 새 패키지는 설치하지 않았다.
- 숫자의 `f`는 **0부터 시작하는 원본 프레임 번호**. `*_snapshot.json`의 trace/대표 번호는 잘린 영상 기준이며 `source_offset_frame`을 더해야 한다. CSV `*_absolute_frame`/집계 표는 이를 반영한다. 원본을 직접 읽은 `*_s1/s2/s3.json`은 `source_frame`이 이미 원본 번호다. MP4 재인코딩은 포즈 입력을 바꾸므로 원본 interval 실험과 재인코딩 스냅샷의 경계가 꼭 같지는 않다.
- 7개 영상의 사람이 본 구간은 한 명(Codex)의 contact sheet 검토로 만든 **탐색용 참조**다. Top/Impact는 불확실성 프레임 구간으로 저장했다. 창 시작/끝은 준비·피니시 여유를 포함하며 GolfDB Address/Finish와 정의가 다르다. 정확도 benchmark로 삼지 않았다. 원본 영상을 눈으로 본 동작/컷과 정답 이벤트를 구별한다.
- GolfDB는 로컬 기존 영상만 비상업 평가에 사용했다. `slow=0`, 실제 fps가 30과 ±0.15 이내인 영상 중 ID 순 정면 25개+DTL 25개, 세 조건 모두 동일한 50개다. 무작위 대표 표본이나 독립 최종 테스트셋을 주장하지 않는다. 160×160 영상이므로 방향·인물 크기·촬영 조건을 완전히 분리할 수 없다.
- GolfDB 정답은 원본 annotations의 `events[1:9]−events[0]`. 4개 이벤트만 평가: Address는 백스윙 시작 경계, Top/Impact/Finish는 해당 구간 시작 경계. 허용오차 `max(round((Impact−Address)/30),1)`를 **원본 프레임 단위로 모든 fps에서 고정**했다. 예측이 없는 경우 오답. 학습/튜닝 없이 150번 포즈 추론, 결과 CSV/JSON만 저장했다. GolfDB 이미지·영상은 레포에 넣지 않았다.
- 30→15→10fps는 같은 원본을 1/2/3간격으로 MediaPipe에 전달한 실험이다. 셔터 속도/블러가 다른 실제 저fps 촬영이나 실제 60/120/240fps 촬영의 결과로 외삽하지 않는다. 추적과 필터도 함께 영향을 받으므로 고정 포즈 신호의 솎기 실험을 추가했다.

## 7. 코드 사전 사실 재확인 및 수정

| 사실 | 재확인 결과 |
|---|---|
| F1 | 인덱스 불일치는 맞지만 **annotated_frames는 모든 sampled 프레임이 아니라 pose가 잡힌 프레임만** 담는다. K는 첫 valid 이전의 pose 검출·6관절 gate 실패 수다. pose 자체 실패 프레임은 양쪽에서 빠진다. 끝의 floor(total/step) 때문에 마지막 preview가 하나 빠질 수도 있어 원본 ID 계약이 가장 안전하다. |
| F2 | 맞음. hip/shoulder/wrist_x history는 저장만 하고 현재 detect_all_phases 판정에는 쓰지 않는다. |
| F3 | 길이 비율 제약은 맞음. 현재 Top은 속도 부호 전환 우선+argmin fallback, Impact는 이후 구간 **raw Y argmax**다. 어드레스 높이 복귀라고 적힌 함수 docstring은 현재 구현과 다르다. |
| F4 | valid history 8개 이상이면 7개 **경계 키**를 만든다. 7개 정상/비어 있지 않은 순서의 단계라는 뜻은 아니다. 상수 입력에서 Down 역전 확인. |
| F5 | 맞음: Y k5, 기울기 k3. MediaPipe 자체 temporal smoothing도 별도로 켜져 있다. |
| F6 | 각도 metrics는 이전 값을 복사하지만 **손목 history는 복사하지 않고 삭제/압축된다**. 최초 gate 통과 전 fd는 생략, annotated는 존재. 그 뒤 실패 fd에는 값 복사. 손목 자체 visibility는 이 gate에 포함되지 않는다. |
| F7 | 조건 분기는 맞지만 “200 상한”은 엄밀하지 않음. `total//200`의 floor를 쓰므로 532프레임은 step2로 266개, 826프레임은 step4로 207개 분석된다. |
| F8 | 맞음. 8초 이하면 전체 반환. 320×180 강제 resize. 추가로 scan도 floor이므로 400개 상한이 엄밀하지 않고, 누락 후 유효 샘플 수/전체 길이로 평균 sps를 계산한다. |
| F9 | 정적 JSON 맞음. 하지만 현재 재분석과 정확히 같으므로 오래된 코드 결과라는 원인은 기각. |
| F10 | 기존 246개 보고 수치는 기존 분석 결과다. `results.json`을 확인하면 eff_sample1 240개, 2가 3개, 3이 3개여서 “246개 모두 매 프레임”이라는 설명은 부정확하다. 이번 50개 forced step 실험과 섞지 않았다. |

핵심 코드: [pipeline.py](../../../golf_swing_analyzer/analyzer/pipeline.py) L61–178, L203–354; [phase_detector.py](../../../golf_swing_analyzer/analyzer/phase_detector.py) L20–163; [serialization.py](../../../server/serialization.py) L24–48; [Streamlit 복제](../../../golf_swing_analyzer/ui/tab_analysis.py) L238–269; [SwingReplay](../../../web/src/components/SwingReplay.tsx) L23–26, L116–117, L168. 대표 이미지 선택은 단계 중간/다운 85%/임팩트 첫 라벨이며 경계 프레임과 같지 않을 수 있다.

## 8. S1·S2·S3의 장면 추적

### S1 일반 샘플: K=0, 단계가 다른 재생 사이클을 연결

원본 30fps. 자동 선택 1.5–9.7초, 시작 f45. 스냅샷의 valid/pose 모두 124/124(15fps), 보간 0. 아래 모든 행에서 `rep_i=local_idx`; 단순 local_idx 교체 전후 영상은 동일하다.

| 단계 | rep_i | local_idx | K | trim 프레임 | 원본 프레임 | 원본 초 |
|---|---|---|---|---|---|---|
| 어드레스 | 7 | 7 | 0 | 14 | 59 | 1.967 |
| 백스윙 | 16 | 16 | 0 | 32 | 77 | 2.567 |
| 백스윙 톱 | 19 | 19 | 0 | 38 | 83 | 2.767 |
| 다운스윙 | 55 | 55 | 0 | 110 | 155 | 5.167 |
| 임팩트 | 62 | 62 | 0 | 124 | 169 | 5.633 |
| 팔로우스루 | 84 | 84 | 0 | 168 | 213 | 7.100 |
| 피니시 | 114 | 114 | 0 | 228 | 273 | 9.100 |

첫 스윙 Top 참조 f82–84, Impact f89–91. f161은 피니시이고 **f162에서 재생 영상의 어드레스로 컷**된다. 기록된 샘플 f161→163의 평균 Y 점프 0.26667은 양 손목에 동시에 나타난다. 15fps 검출은 Top 경계 f79 뒤에서 가장 낮은 손목 위치를 찾다가 두 번째 재생의 f167을 Impact 경계로 선택한다. 대표는 앞 단계와 경계가 겹치는 라벨링 때문에 다음 샘플 f169가 된다. Down 대표 f155는 첫 피니시, Finish 대표 f273은 두 번째 느린 백스윙이다. 긴 평탄 구간은 피니시 유지, 급락은 컷으로 설명된다. 미검출이나 손목 값 복사로 만든 계단이 아니다.

[현행 vs local_idx 이미지](figures/il-ban_snapshot_annotated.png) · [Y/가시도/경계](figures/il-ban_snapshot_signals.png) · [컷 전후 원본 f156–174](figures/il-ban_cut_manual.png)

### S3 프로 비교: K=0, DTL→정면 전환을 가로질러 분할

자동 선택 8.3–15.4초, 원본 시작 f248. 검출 104/107, valid104, 첫 gate 손실 K0. 대표의 Back/Top f296/f302는 원본에서 손이 올라간 자세다. 스크린샷의 “어드레스처럼 보인다”는 관찰은 작은 비교 카드의 크롭도 고려해야 하며 원본에서는 같은 어드레스가 아니다. 실제 오류는 Down/Impact/Follow가 다음 정면 장면의 준비 자세를 선택하고, Finish가 그 다음 백스윙인 것이다.

| 단계 | rep_i | local_idx | K | trim 프레임 | 원본 프레임 | 원본 초 |
|---|---|---|---|---|---|---|
| 어드레스 | 10 | 10 | 0 | 22 | 270 | 9.014 |
| 백스윙 | 23 | 23 | 0 | 48 | 296 | 9.882 |
| 백스윙 톱 | 26 | 26 | 0 | 54 | 302 | 10.082 |
| 다운스윙 | 56 | 56 | 0 | 118 | 366 | 12.219 |
| 임팩트 | 61 | 61 | 0 | 128 | 376 | 12.553 |
| 팔로우스루 | 78 | 78 | 0 | 162 | 410 | 13.688 |
| 피니시 | 98 | 98 | 0 | 202 | 450 | 15.023 |

원본 Top 참조 f299–307, Impact f311–317. f350대 이후 페이드/장면 전환으로 다른 정면 스윙 준비가 나온다. 현재 대표 f366/f376/f410은 그 장면의 준비 자세, f450은 다음 백스윙이다. 저장 JSON과 새 분석의 모든 fd/경계/손목이 동일하므로 새 JSON으로 교체만 해서는 고쳐지지 않는다.

[현행 vs local_idx 이미지](figures/pro_snapshot_annotated.png) · [컷 전후](figures/pro_cut_manual.png) · [Y/가시도](figures/pro_snapshot_signals.png)

### S2 빨간 셔츠: 원본 식별, 동일 유형 부분 재현, 원래 세션의 정확한 설정은 미확인

원본은 **`pexels_35546329.mp4`**다. 스크린샷 각 내부 영상 영역을 90×160으로 맞춰 상단 HUD를 제외하고 RGB 픽셀 오차의 중앙값으로 원본 585프레임과 비교했다. 아래는 **최근접 후보**이며 리사이즈/압축/정지 자세 때문에 ±몇 프레임을 확정할 수 없다. 정확한 세션 frame_data나 trim 로그를 복구한 값은 아니다.

| 단계 | 스크린샷 최근접 원본 f | 초 | 화면 해석 |
|---|---|---|---|
| Address | 241 | 8.033 | 준비 자세·무관절 표시 |
| Backswing | 256 | 8.533 | 준비 자세·무관절 표시 |
| Top | 264 | 8.800 | 준비 자세·무관절 표시 |
| Downswing | 273 | 9.100 | 준비 자세·무관절 표시 |
| Impact | 274 | 9.133 | 준비 자세·무관절 표시 |
| Follow | 293 | 9.767 | 준비 자세·무관절 표시 |
| Finish | 396 | 13.200 | 피니시·관절 표시 |

원본의 실제 Top f360–364, Impact f375–377와 비교하면 첫 6장이 동작 이전으로 밀렸다는 점은 확인된다. 기본 Docker 자동 구간 10.6–19.5초에서는 K8(16프레임)만 발생해 6장 모두 어드레스인 원래 스크린샷은 그대로 재현되지 않았다. 시작 7.5/7.6/7.7/8.0초를 탐색했고 **7.6–19.5초에서는 첫 6장 준비 자세, 그중 5장 무관절 표시**가 재현된다. 여섯 번째는 gate를 통과하여 원래 스크린샷과 한 장 차이가 남는다. 이것은 원래 사용자가 7.6초를 선택했다는 증거가 아니다.

| 단계 | rep_i | local_idx | K | 현재 원본 f | local_idx 적용 원본 f | 현재 gate |
|---|---|---|---|---|---|---|
| 어드레스 | 11 | 50 | 39 | 250 | 328 | False |
| 백스윙 | 25 | 64 | 39 | 278 | 356 | False |
| 백스윙 톱 | 30 | 69 | 39 | 288 | 366 | False |
| 다운스윙 | 33 | 72 | 39 | 294 | 372 | False |
| 임팩트 | 34 | 73 | 39 | 296 | 374 | False |
| 팔로우스루 | 42 | 81 | 39 | 312 | 390 | True |
| 피니시 | 94 | 133 | 39 | 416 | 494 | True |

원인은 첫 valid 이전의 pose-only 이미지가 annotated에 쌓인 상태에서 fd의 짧아진 순번을 이미지 순번으로 썼기 때문이다. 첫 5장의 gate는 false이므로 skeleton을 그리지 않는다. 여섯 번째 f312는 준비 자세지만 gate가 true인 차이가 남는다. 피니시 rep_i는 충분히 뒤로 가서 실제 피니시 이미지를 만난다. local_idx 조회는 이 78프레임 조회 오차를 제거하지만, 준비 자세의 gate 누락과 event 경계 오차는 별도다.

타임라인에도 별도 압축이 있다. 빨간 **전체 원본 adaptive** 실험에서 hist51 Impact는 실제 f339=11.3초인데 UI는 51×3/30=5.1초로 이동한다. Finish hist71도 실제 f399=13.3초를 7.1초로 표시한다. 유효 손목 history에서 62개 샘플이 빠져 6.2초가 사라졌기 때문이다. 스크린샷의 “앞에 단계가 몰림”과 같은 방향의 오류이며, 원래 세션의 정확한 경계 숫자는 JSON이 없어 미확인이다.

[스크린샷 최근접 원본](figures/s2_raw_frame_matches.png) · [6장 오류 재현과 매핑 교정](figures/s2_candidate_7.6_representatives.png) · [재현 신호](figures/s2_candidate_7.6_signals.png) · [기본 자동 구간 실제 annotated 비교](figures/pexels_35546329_snapshot_annotated.png)

## 9. H2 실험 수치

### (a) 같은 구간, effective_sample 1·2·3

먼저 S1과 동일하게 실제 trim한 1.5–9.7초를 사용했다. 아래 Top/Impact는 대표 이미지가 아니라 **경계 시작**이다. 참조 범위는 Top82–84/Impact89–91. 매 프레임으로 바꾸면 이 사례의 Impact는 복구되지만, 자동 구간이 컷을 포함한다는 결함은 남는다. 세 조건에서 같은 사이클을 계속 고른다는 보장은 없다.

| step | 분석 fps | 샘플 수 | 유효 수 | Top f / 초 | Impact f / 초 | 참조 Top83–Impact90 유효 관측 |
|---|---|---|---|---|---|---|
| 1 | 30.0 | 247 | 247 | 81 / 2.700 | 90 / 3.000 | 8 |
| 2 | 15.0 | 124 | 124 | 79 / 2.633 | 167 / 5.567 | 4 |
| 3 | 10.0 | 83 | 83 | 258 / 8.600 | 279 / 9.300 | 3 |

7개 대상도 원본의 동일 구간을 step만 바꾸어 분석했다. 일반·테스트 4개는 **전체 원본**, 프로/프로2는 자동 선택 구간에 해당하는 원본 f248:462 / f3701:3942이다(끝 제외). 이 표는 재인코딩 스냅샷 실험과 구별한다. 느리게 재생되는 테스트 영상의 media time을 실제 다운스윙 시간으로 해석하지 않는다.

| 영상 | step | Top 초 | Impact 초 | 참조 Top–Impact 샘플 수 | 그중 gate 통과 |
|---|---|---|---|---|---|
| il-ban | 1 | 2.700 | 10.567 | 8 | 8 |
| il-ban | 2 | 2.667 | 10.467 | 4 | 4 |
| il-ban | 3 | 4.700 | 10.500 | 3 | 3 |
| pro | 1 | 10.116 | 12.085 | 12 | 12 |
| pro | 2 | 9.949 | 12.085 | 6 | 6 |
| pro | 3 | 9.982 | 12.085 | 4 | 4 |
| pro2 | 1 | 125.692 | 128.195 | 30 | 25 |
| pro2 | 2 | 125.692 | 128.295 | 15 | 15 |
| pro2 | 3 | 125.692 | 128.295 | 10 | 10 |
| pexels_8065880 | 1 | 8.583 | 18.542 | 26 | 15 |
| pexels_8065880 | 2 | 8.667 | 18.583 | 13 | 11 |
| pexels_8065880 | 3 | 8.000 | 18.375 | 9 | 8 |
| pexels_6541855 | 1 | 4.760 | 5.560 | 26 | 24 |
| pexels_6541855 | 2 | 6.240 | 8.240 | 13 | 13 |
| pexels_6541855 | 3 | 4.440 | 5.520 | 9 | 9 |
| pexels_35546329 | 1 | 2.000 | 10.133 | 15 | 15 |
| pexels_35546329 | 2 | 1.800 | 11.133 | 8 | 8 |
| pexels_35546329 | 3 | 2.200 | 11.300 | 5 | 5 |
| pexels_34883764 | 1 | 7.400 | 15.367 | 11 | 7 |
| pexels_34883764 | 2 | 7.400 | 14.467 | 6 | 0 |
| pexels_34883764 | 3 | 12.000 | 15.600 | 4 | 0 |

따라서 프레임 증가는 평균적으로 유리하지만 모든 사례에서 단조 개선되지 않는다. 예를 들어 노란 셔츠는 step2에서 다른 극값을 택하고 step3에서 복구된다. 전구간 규칙·포즈 추적·스무딩의 상호작용을 단순 fps 임계값으로 환원하면 안 된다.

### (b) GolfDB 50개 paired PCE

| 방향 | 분석 fps | n | Address | Top | Impact | Finish | Impact 절대오차 중앙값(원본 f) |
|---|---|---|---|---|---|---|---|
| all | 30 | 50 | 0% (0/50) | 18% (9/50) | 88% (44/50) | 4% (2/50) | 1.0 |
| all | 15 | 50 | 0% (0/50) | 0% (0/50) | 68% (34/50) | 4% (2/50) | 1.0 |
| all | 10 | 50 | 2% (1/50) | 2% (1/50) | 42% (21/50) | 0% (0/50) | 24.0 |
| face-on | 30 | 25 | 0% (0/25) | 16% (4/25) | 100% (25/25) | 8% (2/25) | 0.0 |
| face-on | 15 | 25 | 0% (0/25) | 0% (0/25) | 96% (24/25) | 8% (2/25) | 1.0 |
| face-on | 10 | 25 | 4% (1/25) | 0% (0/25) | 56% (14/25) | 0% (0/25) | 1.0 |
| down-the-line | 30 | 25 | 0% (0/25) | 20% (5/25) | 76% (19/25) | 0% (0/25) | 1.0 |
| down-the-line | 15 | 25 | 0% (0/25) | 0% (0/25) | 40% (10/25) | 0% (0/25) | 18.0 |
| down-the-line | 10 | 25 | 0% (0/25) | 4% (1/25) | 28% (7/25) | 0% (0/25) | 34.0 |

[PCE 및 실제 관측 수 그래프](figures/golfdb_fps.png) · [클립별 결과](data/golfdb_results.json) · [선정 ID/GT 원자료](data/golfdb_selection.json)

30fps의 포즈 결과를 고정하고 시계열만 솎는 보조 실험에서 Impact 88→72→44%. 포즈를 매번 새로 추론한 88→68→42%와 비슷해, 추적 품질 변화만으로 감소를 설명할 수 없다. 시간 폭을 근사한 스무딩 ablation은 같은 고정 신호의 10fps Impact를 44→68%로 올렸지만 Top은 2→4%다. 이는 새로운 알고리즘의 독립 검증 결과가 아니라 후속 개선 방향을 가르는 탐색이다. `dense_linear`는 누락 위치를 시간 격자에 선형으로 채운 가상 신호이며 **RIFE 영상 보간 실험이 아니다**.

### (c) 다운스윙에 실제로 들어간 관측 수

GolfDB GT Top부터 Impact까지 양끝 포함, 원본 프레임 기준으로 계산했다. detected Down 라벨 수와 다르다. 검출기가 잘못 긴 구간을 Down으로 지정하면 그 라벨 프레임 수가 많아도 올바른 다운스윙을 관측한 것은 아니다.

| 방향 | 분석 fps | 샘플 중앙값 | gate 유효 중앙값 | gate 유효 범위 |
|---|---|---|---|---|
| all | 30 | 9.0 | 9.0 | 0–31 |
| all | 15 | 4.0 | 4.0 | 0–16 |
| all | 10 | 3.0 | 3.0 | 0–10 |
| face-on | 30 | 9.0 | 9.0 | 7–31 |
| face-on | 15 | 4.0 | 4.0 | 3–16 |
| face-on | 10 | 3.0 | 3.0 | 2–10 |
| down-the-line | 30 | 8.0 | 8.0 | 0–10 |
| down-the-line | 15 | 4.0 | 4.0 | 0–5 |
| down-the-line | 10 | 3.0 | 3.0 | 0–4 |

30fps에서도 유효 0개인 DTL 사례가 있어 프레임 수와 가시성 문제를 분리해야 한다. 코드 주석의 “임팩트 감지에 최소 10프레임 필요”는 검증된 필수조건이 아니다: 정면 25개의 30fps Impact PCE는 100%이고 GT 구간 관측 중앙값은 9개다. 일반 단일 스윙에서는 Top81–Impact90 경계 사이 실제 10개를 관측하면서도 Down 라벨은 패딩에 따라 6→4→1개였다.

## 10. H3–H7 상세 집계

### 포즈 검출과 6관절 gate는 다르다

아래 adaptive 실험의 일반/테스트는 전체 원본, 프로/프로2는 앞서 명시한 원본 interval이다. 최대 결측 시간은 `연속 탈락 샘플 수×step/fps`의 노출 시간 근사다. 복사율 분모는 frame_data이고 pose 실패 자체는 fd에도 빠진다.

| 영상 | 샘플 수 | pose 검출 | 6관절 통과 | 초기 K | 최대 결측 초 | metrics 복사율 |
|---|---|---|---|---|---|---|
| il-ban | 266 | 100.0% | 100.0% | 0 | 0.00 | 0.0% |
| pexels_34883764 | 207 | 100.0% | 38.6% | 26 | 6.13 | 55.8% |
| pexels_35546329 | 195 | 100.0% | 68.2% | 0 | 6.20 | 31.8% |
| pexels_6541855 | 130 | 100.0% | 100.0% | 0 | 0.00 | 0.0% |
| pexels_8065880 | 184 | 100.0% | 79.3% | 36 | 4.50 | 1.4% |
| pro2 | 121 | 100.0% | 75.2% | 0 | 2.00 | 24.8% |
| pro | 107 | 97.2% | 97.2% | 0 | 0.13 | 0.0% |

각 관절의 visibility>0.5 비율은 `pose_metrics.csv`의 vis11/12/23/24/25/26 및 vis15/16 열에, 좌/우 손목 y와 가시도 원자료는 trace CSV에 있다. 손목 두 개의 위치가 틀렸는지를 판정하는 수동 landmark 정답은 만들지 않았다. 검출 성공/visibility가 높다는 이유만으로 좌표가 정확하다고 주장하지 않는다.

### 정지 및 패딩 실험

| 케이스 | 경계 키 수 | 실제 라벨 종류 | 유효 수 | Y 범위(px) | Down 라벨 수 | Top 원본 f | Impact 원본 f |
|---|---|---|---|---|---|---|---|
| control_single_pad0 | 7 | 7 | 116 | 417.95480728149414 | 6 | 81 | 90 |
| control_static_ilban | 7 | 7 | 36 | 18.40190887451172 | 20 | 34 | 55 |
| control_single_pad1 | 7 | 7 | 176 | 417.4298095703125 | 4 | 81 | 90 |
| control_static_red | 0 | 0 | 0 |  | 0 |  |  |
| control_single_pad3 | 7 | 7 | 296 | 417.56221771240234 | 1 | 81 | 90 |

실제 정지 일반 클립 f30–65는 잔동작/포즈 흔들림의 Y 범위 약 18.4px만으로 7단계를 만든다. 빨간 정지 f180–240은 gate를 전혀 통과하지 못해 0개다. “모든 정지 영상이 7단계”가 아니라 **valid8개 이상에 스윙 존재 검사 없이 적용되는 문제**다. 정확한 상수 입력 120개에서 경계는 7개지만 Down [10,9]가 역전되어 실제 라벨은 6종뿐이다.

패딩 실험은 같은 원본 f45–160 앞뒤에 각각 첫/끝 프레임을 0/1/3초 반복한 실제 영상이다. 모두 30fps로 새 추론했고 Top81·Impact90은 그대로다. 변화하는 전체 길이의 3%/2%로 Top/Impact 폭을 정하기 때문에 Down에 남은 라벨이 줄어든다. 0.3초의 실제 다운스윙 전체가 사라진 것이 아니다.

### 자동 구간: 7개 원본 대 종횡비 보존

모든 숫자는 초. 사람 참조는 탐색적 창이며 시작/끝 여유의 정의에 따라 IoU가 달라진다. 특히 pro2의 시작은 거친 수동 범위라 몇 프레임 수준 정답으로 해석하지 않는다. 어려운 영상의 실제 공 이동은 f642 부근(21.4초)이며 그 이전 연습 동작을 두 자동 방식이 각각 선택했다.

| 영상 | 사람 참조 창 | 현행 320×180 | 비율 보존 | 스캔 pose율 | 창 IoU |
|---|---|---|---|---|---|
| il-ban | 1.50–5.33 | 1.5–9.7 | 1.4–8.8 | 93.8→100.0% | 0.467→0.518 |
| pro | 8.41–11.82 | 8.3–15.4 | 8.3–15.4 | 92.2→92.2% | 0.480→0.480 |
| pro2 | 120.12–127.46 | 123.5–131.5 | 123.5–131.5 | 96.3→96.3% | 0.348→0.348 |
| pexels_8065880 | 2.50–8.75 | 2.6–9.6 | 2.6–9.6 | 100.0→100.0% | 0.866→0.866 |
| pexels_6541855 | 2.60–7.40 | 2.4–8.5 | 2.4–8.5 | 100.0→100.0% | 0.787→0.787 |
| pexels_35546329 | 10.50–14.50 | 10.6–19.5 | 10.5–19.5 | 79.7→100.0% | 0.433→0.444 |
| pexels_34883764 | 20.00–23.33 | 2.8–10.1 | 6.1–13.3 | 82.6→100.0% | 0.000→0.000 |

비율 보존은 320×180 안에 들어오게 축소한 실험(세로 영상 약 101×180)이며 픽셀 예산은 같지 않다. 따라서 기하 왜곡만의 완전 통제 실험으로 과장하지 않는다. 더 큰 비율 보존 입력/letterbox는 후속 후보이고 이번에 최적값을 찾지 않았다. 8초 이하 우회는 실제 1.2초 정지 클립에서 `(0.0,1.2)` 반환으로 확인했다. fps/진폭 개선이 스윙 존재 검사를 대신할 수 없다.

## 11. 산출물·완료 확인

- 실행 및 파일 설명: [README.md](README.md). 주요 원자료: [data/](data/), 그림: [figures/](figures/). 모든 7개 영상의 좌/우/평균 Y, 8관절 visibility, pose/gate, source/UI 경계 그림을 생성했다.
- H1–H8 판정 완료. H2(a)(b)(c) 수치 포함. S1/S3 저장 샘플은 현재 원래 함수로 완전 재현. S2는 원본/장면 최근접 번호와 동일 유형 오류를 재현했으나 **원래 업로드 세션의 정확한 trim·플랫폼·frame_data는 미확인**이다. 독립 검증 시 원래 JSON을 확보하면 후보 K와 직접 대조할 수 있다.
- 문헌 10개와 오픈소스/데이터 후보 7개의 실제 열린 URL/확인 수준을 기록했다. 접근 실패한 논문 성능은 제외했다. 60/120/240fps 골프 검출 실측 비교는 미확인으로 남겼다.
- 앱 코드 수정/새 패키지 설치/커밋 없음. 검증 기록은 [data/validation.json](data/validation.json), 최종 상태는 [data/git_status_final.txt](data/git_status_final.txt).
- 시작 시 이미 `.DS_Store`, `docs/research/phase-segmentation-diagnosis-prompt.md`, `docs/research/phase_diag/`가 untracked였다. 이 중 앞 두 경로는 G1 밖이지만 기존 사용자 파일이므로 삭제하지 않았다. 따라서 **git status 전체가 G1 경로만이라는 문구는 문자 그대로 충족하지 않으며, 이번 작업으로 추가·변경한 경로만 G1 안임**을 별도로 확인했다.
