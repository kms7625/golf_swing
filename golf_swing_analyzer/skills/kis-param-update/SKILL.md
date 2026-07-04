---
name: kis-param-update
description: KIS 자동매매 파라미터(SL/TP/RSI/거래량 등)를 실제로 변경하는 워크플로우를 실행한다. "SL 바꿔줘", "TP를 올려봐", "RSI 범위 조정해줘", "파라미터 업데이트해줘", "model_trainer 돌려줘", "그리드서치 결과 적용해줘", "손절을 -3%로 바꿔봐" 같은 말이 나오면 반드시 이 스킬을 사용한다. config.py만 고치면 안 되고 .env도 반드시 함께 확인해야 한다.
---

# KIS 파라미터 변경 워크플로우

## 왜 이 순서를 지켜야 하는가

`.env`에 같은 키가 있으면 `config.py` 값을 덮어쓴다.
코드만 바꾸고 끝내면 다음 재시작 시 `.env` 값이 복원된다.
실측 게이트 없이 파라미터를 적용하면 과최적화된 파라미터가 실거래에 들어간다.

---

## 변경 단계

### 1단계: 현재 상태 확인

```
- config.py의 현재 파라미터 값 (config.py L.39-40, L.60-64)
- .env의 동일 키 값 (두 곳 중 .env가 우선 — config.py L.6)
- 마지막 model_trainer.py 실행 날짜 (DB model_version 테이블)
- 현재 실측 SELL 거래 건수:
  SELECT COUNT(*) FROM trades WHERE action='SELL'
  (주의: action 컬럼, side 컬럼 없음 — database.py L.23)
```

### 2단계: 합격 기준 사전 검토

변경 전 새 파라미터로 백테스트를 돌려 합격 여부를 확인한다 (`kis-backtest-result` 참조):

```
기댓값 > 0, 손익비 ≥ 1.5, MDD ≥ -5%, 거래 ≥ 30건
(evaluate.py L.36-40 동일 기준)
```

미달 시 변경 중단.

### 3단계: 실측 게이트 확인

실측 SELL ≥ 30건이 아니면 `.env` 자동 적용을 하지 않는다.
(model_trainer.py L.481-521 동일 로직 — LOCK_THRESHOLD=30, L.487)
자동 적용은 추가로 walk-forward `decision == "update"`도 요구 — 검증 거부권·현상 유지
우대를 통과한 조합만 배포됨.

- **30건 미만**: 백테스트 합격이어도 **PARAMS LOCKED** — 코드/env 수정 없이 결과만 기록
- **30건 이상**: 4단계 진행

### 4단계: 두 곳 동시 수정

```python
# config.py 예시 (L.39-40)
STOP_LOSS   = float(os.getenv("STOP_LOSS",   -0.025))
TAKE_PROFIT = float(os.getenv("TAKE_PROFIT",  0.07))
```

```
# .env 예시 (반드시 동시에)
STOP_LOSS=-0.025
TAKE_PROFIT=0.07
```

두 파일을 함께 수정하지 않으면 변경이 무효.

### 5단계: 실전 전환 관련 파라미터 원복 확인

아래 값은 모의투자 데이터 축적 목적으로 확대된 값이므로
**실전 전환 시에만** 함께 원복:

| 파라미터 | 현재(모의) | 실전 전환 시 | 위치 |
|---|---|---|---|
| MAX_POSITIONS | 5 | 3 | config.py L.75 |
| MAX_STOCKS | 200 | 100 | watchlist.py L.22 |

파라미터 변경 요청이 SL/TP/RSI 관련이더라도 실전 전환이 동반되면 이 두 값도 함께 확인.
실전 전환 자체가 목적이면 이 스킬 단독으로 진행하지 말고 **`실전전환_체크리스트.md`의
전체 절차**(선행 게이트 → 앱키 교체 → 설정 변경 → 토큰 삭제 → 검증 → 롤백 경로)를 따를 것.
특히 INITIAL_CAPITAL(.env)은 일일손실한도·cash cap의 기준액이므로 실전 투입 자금과 일치 필수.

### 6단계: CLAUDE.md 파라미터 변경 이력 기록

```
| 날짜 | 검토 결과 | 조치 | 사유 |
| YYYY-MM-DD | SL=X%, TP=Y% (손익비 Z, EV +W, 거래 N건) | 적용/보류 | 사유 |
```

항목을 추가하지 않으면 다음 세션에서 변경 맥락을 잃는다.

### 7단계: 변경 후 검증

```bash
python model_trainer.py --verify   # 리팩토링이 신호 자체를 바꾸지 않았는지 확인
python evaluate.py                 # 합격 기준 재평가
```

---

## 그리드서치 탐색 범위 (model_trainer.py 상수 블록, 2026-07-03 확장)

```python
# 안쪽 루프 (신호 불변 — 이벤트 재사용)
SL_LIST    = [-0.015, -0.02, -0.025, -0.03]
TP_LIST    = [0.04, 0.05, 0.06, 0.07, 0.08, 0.10]
TRAIL_LIST = [1.5, 2.0, 2.5]
# 바깥 루프 (신호 가변 — 사전계산 재실행)
RSI_MAX_LIST   = [65, 70, 75]
VOL_RATIO_LIST = [1.0, 1.1, 1.3]
```

2계층 648조합 (약 2.4분 실측). walk-forward(9개월 학습/3개월 검증 거부권/+10% 현상 유지
우대) 통과 시에만 decision=update. `.env` 자동 갱신은 **5키**: STOP_LOSS, TAKE_PROFIT,
RSI_BUY_MAX, VOLUME_SURGE_RATIO, TRAILING_ATR_MULT(.env에 없으면 끝에 추가됨).
판정 상수 변경은 그리드서치확장_설계.md 개정 선행 (kis-code-change A14).

---

## 현재 확정 파라미터 (기준값)

| 파라미터 | 값 | 비고 |
|---|---|---|
| STOP_LOSS | -0.025 | EV 기준 최적 |
| TAKE_PROFIT | 0.07 | 실용 균형 — 백테스트 기준값: 손익비 3.09 / EV +0.3207 (2026-W26-TP7, deployed=0) |
| RSI_BUY_MIN/MAX | 25/70 | 백테스트 완화 결과 |
| VOLUME_SURGE_RATIO | 1.1 | 백테스트 완화 결과 |

TP=10%(손익비 3.42)는 2026-06-30 보류 — 실측 SELL 30건 달성 후, 실측 손익비가
현행 기준값(3.09) 대비 30% 이내 괴리인지 확인하며 TP=7% 유지·변경을 재검토.
최신 기준값은 `db.get_last_model_version()` 또는 CLAUDE.md 파라미터 변경 이력에서 확인.

---

## 출력 형식

```
[현재 상태] config.py 값 / .env 값 / 실측 SELL N건
[제안 변경] 파라미터명: 현재값 → 제안값
[백테스트 결과] 기댓값/손익비/MDD/거래수 — PASS/FAIL
[실측 게이트] SELL N건 / 30건 기준 통과 여부
[적용 여부] 적용 / PARAMS LOCKED
[수정 파일] config.py L.N / .env 키명
[실전전환 원복] MAX_POSITIONS/MAX_STOCKS 해당 시 명시
[CLAUDE.md 이력] 추가할 행
```
