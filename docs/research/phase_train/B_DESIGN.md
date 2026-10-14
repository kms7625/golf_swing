# B안: 관절 시계열 이벤트 모델 — 설계만, 설치·학습 없음

2026-10-13. A안 이후 별도 실험 후보다. 아래 속도·성능 기대는 실측 결과가 아니다.

## 입력·라벨

- 입력은 같은 MediaPipe 33관절 x/y/z, visibility. 어깨·골반 중심으로 평행 이동하고 몸통
  길이로 크기를 정규화한다. z는 metric depth가 아니므로 별도 정규화 및 ablation 대상으로 둔다.
- 프레임마다 좌표 99 + 속도 99 + visibility 33 + 관측 mask 33 + 실제 dt 1 = 265차원.
  속도는 원본 시간으로 나눈 차분. 결측을 0으로 채우더라도 mask를 함께 주고, 컷/긴 결측은
  별개 시퀀스로 분리한다. 통계 정규화의 평균/표준편차도 학습 split에서만 추정한다.
- 원 events[1:9]−events[0]을 8이벤트 프레임 라벨로 사용. 나머지는 no-event로 하여 9클래스.
  A안과의 주 비교는 동일 4이벤트 PCE, 보조로 8이벤트 PCE를 별도 표기한다.
- 1프레임 희소 라벨의 불균형은 학습 split 빈도로 가중한 교차엔트로피로 처리한다.
  ±1프레임 soft target이나 시간 jitter는 사전 ablation으로만 비교하며 평가 GT는 수정하지 않는다.
- pose 입력에는 클럽·공이 없다. 특히 Top과 Impact의 실제 정의를 관절만으로 완전히
  복구할 수 있다는 전제는 두지 않는다. Finish에는 자세를 풀기 전후의 문맥이 필요하다.

## 두 개의 작은 후보

| 후보 | 구조 | 산술 규모 | 활용 |
|---|---|---|---|
| 1D CNN | 265→64 pointwise, 64채널 kernel3 dilated Conv1d 5층(d=1,2,4,8,16), 64→9 head | 약 79,369 파라미터, FP32 약 0.30 MiB, 600프레임 약 47.4M MAC | 비인과 양방향 문맥 63프레임, 약 2.1초(30fps). 병렬 계산 쉬움 |
| GRU | 265→64 projection, 1층 양방향 GRU(hidden64), 128→9 head | 약 68,105 파라미터, FP32 약 0.26 MiB, gate별 순차 연산 | 긴 자세 유지/이완 문맥. 전체 클립 완료 뒤 추론하며 실시간 지연과 별개 |

규모는 weight/bias 개수의 계산이며 구현·벤치마크가 아니다. 근거 API:
[Conv1d 2.8](https://docs.pytorch.org/docs/2.8/generated/torch.nn.Conv1d.html),
[GRU 2.8](https://docs.pytorch.org/docs/2.8/generated/torch.nn.GRU.html).
후처리는 시간 순서 제약을 둔 최대 로그확률 경로로 8이벤트를 고른다. 스윙 미존재를 무조건
8이벤트로 만드는 일을 피하려고 no-event 대비 점수와 관측 coverage를 개발 데이터에서 검증한다.
Impact의 기존 argmax를 바꾸는 통합은 A2 의도적 변경이므로 별도 비교/승인이 필요한 미래 작업이다.

## 분리와 A안 비교

원 YouTube 영상 단위 GolfDB split을 유지한다. split1–3 3-fold에서 architecture/학습률/
early stopping을 정한다. 같은 프레임을 랜덤하게 train/validation에 섞지 않는다.
seed 3개, 방향별 PCE와 거부율, median absolute error, ≤5프레임, 앱 7개 거부/창/점수 변화를 기록한다.
7개 앱 영상은 이미 회귀 제약에 사용됐으므로 외부 검증 세트라고 부르지 않는다.

이번 A안에서 split4를 평가한 후에는 그 숫자를 보고 B안을 설계·튜닝하면서 다시 같은 split4를
완전히 독립된 최종 성능으로 주장할 수 없다. 사전 고정한 B 계획으로 참고 비교는 가능하지만,
최종 채택 근거에는 새로운 선수/원본 영상의 미노출 평가셋이 필요하다.

학습 기반 시간 문맥이 규칙의 고정 임계값보다 도움이 될 가능성은 있다. GolfDB 논문의
MobileNetV2+BiLSTM은 RGB 입력으로 8이벤트를 추정한다. 그 76.1%를 관절 모델의 예상 PCE나
이번 4이벤트 지표로 옮겨 적지 않는다. 낮은 해상도 포즈 오차·클럽 미관측·작은 개발 표본 때문에
관절 모델이 A안보다 좋아진다는 수치 예측은 현재 근거가 없다.
[GolfDB 원문 §5–6](https://arxiv.org/html/1903.06528).

## 의존성·배포 비용

| 제안 | 버전·라이선스 | 이유/영향 |
|---|---|---|
| PyTorch CPU | `torch==2.8.0+cpu`, BSD-3-Clause 계열 LICENSE 및 포함 third-party notices | Conv1d/GRU 학습·추론. Python3.11, Linux amd64 대상. torchvision/torchaudio는 필요 없음 |
| 기존 NumPy | 현재 1.26.4 유지 후보 | cache→tensor 입력, 메트릭. 현재 실행에는 새 패키지 없음 |
| torch 전이 의존성 | filelock/typing-extensions/sympy/networkx/jinja2/fsspec 등 | 별도 환경에서 버전·각 라이선스 lock 검증 필요; 현재 설치하지 않음 |

[공식 CPU 설치 경로·2.8.0](https://pytorch.org/get-started/previous-versions/),
[해당 버전 LICENSE](https://github.com/pytorch/pytorch/blob/v2.8.0/LICENSE).
PyPI의 일반 Linux cp311 x86_64 wheel은 **888,063,640 bytes(약 846.9 MiB)**이며 CUDA
패키지를 전이 의존한다([PyPI 메타데이터](https://pypi.org/pypi/torch/2.8.0/json)). 이것은 CPU
wheel 크기나 Docker 증가량이 아니다. CPU wheel HEAD 요청은 403으로 크기를 확인하지 못했다.
CPU 전용 설치의 이미지 증가는 **약 0.5–1.5 GiB를 예산 추정치**로만 두고, 별도 이미지에서
설치 전후 `docker image inspect`와 압축 레이어 크기를 실제 측정해야 한다. 모델 파일은 1 MiB 미만 예상.

현재 같은 Docker의 8개 ARM 호스트 CPU 위 amd64 에뮬레이션에서는 속도 예측 오차가 크다.
600프레임 CNN 약 95M FLOP를 유효 1–10 GFLOP/s로 처리한다고 가정하면 산술 10–95ms,
tensor 생성/메모리/실행 overhead를 포함한 **50–500ms/클립**을 초기 예산으로 제안한다.
GRU는 순차 연산 때문에 같은 FLOP여도 다를 수 있어 별도 측정한다. 두 값 모두 포즈 추론을
제외한 가설이며, 전체 서비스 속도는 현재 MediaPipe·영상 디코딩 비용에 크게 좌우된다.
warm/cold 30회 p50/p95와 peak RSS를 같은 Docker에서 측정하기 전 성능 보장으로 쓰지 않는다.

GolfDB 영상·캐시·학습 결과의 사용 범위는 이번과 같은 비상업 연구·평가로 제한한다.
상용 데이터/모델 도입은 데이터, 코드, 가중치 권리를 각각 별도로 검토하는 후속 과제다.
