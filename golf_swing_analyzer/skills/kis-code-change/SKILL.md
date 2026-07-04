---
name: kis-code-change
description: KIS 자동매매 코드를 수정·리팩토링·버그 수정할 때 반드시 사전 체크리스트를 실행한다. "고쳐줘", "수정해줘", "리팩토링해줘", "개선해줘", "버그 있어", "최적화해줘", "함수 바꿔줘", "이 코드 이상해" 같은 말이 나오면 코드를 건드리기 전에 이 스킬의 체크리스트를 먼저 통과시킨다. 하나라도 위반하면 수정안을 제시하지 않고 위반 사항을 먼저 보고한다. PowerShell 스크립트·작업 스케줄러는 kis-ops-infra 관할.
---

# KIS 코드 수정 — 시니어 리뷰어 체크리스트

## 왜 이 체크리스트가 필요한가

실시간 매매(`backtest=False`)와 백테스팅(`backtest=True`) 두 경로가 공존한다.
잘못 건드리면:
- 백테스트에서만 통과하고 실거래에서 신호가 달라진다
- `.env` 우선순위를 모르고 `config.py`만 고쳐서 변경이 무효가 된다
- `trades.db` 컬럼명 오류로 조회가 깨진다
- `positions` 테이블(로컬캐시)과 실제 KIS 잔고를 혼동해 수량이 맞지 않는다
- 신호 소스 우선순위를 잘못 이해해 pump/override/dart/news 차단 순서가 바뀐다
- 사전스캔 순서가 뒤바뀌어 빈 watchlist로 뉴스·공시를 스캔한다
- O(n×k) 함수가 그리드서치 경로에 섞여 속도가 수십 배 저하된다
- dart_filter.py에서 `open(os.devnull)` 쓰면 병렬 스레드에서 I/O 오류 발생

---

## A. 변경 전 필수 확인

### A1. backtest 분기 확인
- [ ] 이 변경이 `backtest=True` / 실시간 분기 중 어디에 영향을 주는가?
- [ ] 실시간 분기라면 pump_detector·override·news·dart 스킵 여부 재확인
  - 근거: strategy.py L.129-133 (`if backtest: return Signal("BUY"...)`)
  - 백테스팅·그리드서치에서 `backtest=True` 전달 필수 — 현재 신호가 과거 데이터에 적용되면 룩어헤드 바이어스

### A2. .env 우선순위
- [ ] `.env`에 동일 키가 있는가? `config.py`만 고치면 `.env` 값이 덮어씀
  - 근거: config.py L.6 (`load_dotenv()`) — `.env`가 모든 `os.getenv()` 기본값을 오버라이드
  - 파라미터(SL/TP/RSI 등) 변경 시 반드시 `.env`도 함께 확인

### A3. 모의/실전 API 혼용
- [ ] 모의(`V` prefix, `KIS_APP_KEY`) / 실전(`T` prefix, `KIS_REAL_APP_KEY`) 혼용 없는가?
  - 근거: kis_api.py L.280-285 (place_order TR-ID 분기)
  - 시세·차트는 항상 실전 서버(_real), 주문·잔고는 모의/실전 서버(_trade)
- [ ] KIS API 관련 수정(TR-ID·엔드포인트·파라미터) 시 **공식 명세(`API문서\` xlsx) 대조 필수**
  — 각 카테고리 파일의 "API 목록" 시트에 TR-ID·URL·모의투자 지원 여부가 있음 (pandas/openpyxl로 파싱)
  - 알려진 불일치: 주문 order-cash의 현행 TR-ID(0801U/0802U)는 개편 전 구버전 (명세: 매도 0011U/매수 0012U).
    하위 호환으로 체결 중 — 교체는 실전전환_체크리스트.md ⑦ 절차로, 임의 교체 금지
  - "모의투자 미지원" 표기는 조회성 API에는 무의미 (이 시스템은 조회를 실전 서버 _real 경로로 호출)
- [ ] kis_api.py 수정 시 **토큰 클라이언트 공유 분기 보존** — 앱키·시크릿·서버가 동일하면
  `_trade = _real` 공유 (kis_api.py L.127-140, 커밋 44268d5). 이 분기를 제거하면 실전 전환 시
  같은 키로 토큰을 각자 발급해 상호 무효화됨. `get_token()`의 "발급 전 캐시 파일 재확인"도
  프로세스 간(trader/dashboard) 이중 발급 방지용 — 제거 금지

### A4. trades.db 컬럼명
- [ ] `action` 컬럼 사용 (BUY/SELL) — `side` 컬럼은 존재하지 않음
  - 근거: database.py L.23 (`action TEXT NOT NULL`)
  - 승률·실측 쿼리: `WHERE action='SELL'` — 잘못 쓰면 조회 결과 0건

### A5. positions 테이블 = 로컬 캐시
- [ ] `positions` 테이블은 로컬 캐시이며 KIS API `get_balance()`와 별도 관리
  - 근거: database.py L.31-37, trader.py L.158 (`positions = db.get_all_positions()`)
  - KIS 잔고와 positions 캐시는 별개 — 주문 성공 시 `db.open_position()` / `db.close_position()` 호출 필수
  - `get_balance()["positions"]`와 `db.get_all_positions()`를 혼동하면 이중 매수/누락 발생 가능

### A6. 신호 소스 우선순위
- [ ] **신규 매수 경로**: pump_detector(0순위) → override(1순위) → dart+news(2순위) 순서를 지켜야 함
  - 근거: strategy.py L.135-197 (골든크로스 분기 내 순서)
  - pump_detector: 실패 시 항상 False(정상) 반환 — pump_detector.py L.96-99
  - override -1: 즉시 차단 / override ≥0: 뉴스·공시 스킵 후 BUY — strategy.py L.141-152
  - dart 부정: OBSERVE_MODE 없이 즉시 차단 / news 부정: OBSERVE_MODE=True면 로그만
- [ ] **보유 종목 청산 경로는 get_signal이 아니라 trader.py `_check_exit()`가 관장** (2026-07-01 분리)
  - 순서: strategy.check_exit(SL/TP/트레일링, 가격 기반 최우선) → get_pump_risk(즉시 청산) →
    get_signal(데드크로스/오버라이드/뉴스·공시 청산) — trader.py L.251-264
  - get_signal의 non-golden 구간에는 pump 체크가 **없음** — 비보유 종목 스캔 시
    "보유 중 청산" 오해 로그 방지 목적. get_signal에 pump를 다시 넣으면 안 됨

### A7. 사전스캔 실행 순서 (변경 금지)
- [ ] `_run_morning_recheck()` 내 순서: `_refresh_watchlist()` → `scan_all_signals()` → `revalidate_morning()`
  - 근거: trader.py L.316-331 — 순서 변경 시 빈 watchlist로 뉴스·공시 스캔
  - `_run_premarket_scan()` 내에서도 scan_all_signals 전에 _refresh_watchlist 선행 필수 — trader.py L.307-310

### A8. dart_filter.py 병렬 환경
- [ ] `dart_filter.py`에서 stdout 억제는 `redirect_stdout(io.StringIO())` 사용 필수
  - 근거: dart_filter.py L.91-92, L.143-144
  - `open(os.devnull)` 쓰면 signal_cache.py 5-thread 병렬 환경에서 `I/O operation on closed file` 오류

### A9. 캐시 파일 무효화 조건
- [ ] 아래 캐시 파일에 영향을 주는 변경인가?
  - `watchlist_cache.json` — 24h TTL, watchlist.py L.14
  - `name_cache.json` — 24h TTL, watchlist.py L.15
  - `premarket_cache.json` — 1단계 결과, premarket.py L.24
  - `premarket_morning.json` — 2단계 결과, premarket.py L.25
  - `news_dart_cache.json` — 매일 16:00 갱신, signal_cache.py L.23
  - 캐시 포맷(키 이름, 구조) 변경 시 반드시 기존 파일 삭제 후 재생성 확인

### A10. INITIAL_CAPITAL 이중 역할
- [ ] `INITIAL_CAPITAL`(config.py L.35)은 **실제 계좌 잔고가 아님** — 두 가지 용도로만 사용
  1. 일일손실한도 계산: `INITIAL_CAPITAL × DAILY_LOSS_LIMIT` — trader.py L.119
  2. 수량계산 cash cap: `min(api_cash, INITIAL_CAPITAL)` — trader.py L.157
  - 실제 계좌 잔고는 `api.get_balance()["cash"]`로 조회

### A11. 그리드서치 경로 성능
- [ ] 신규/수정 함수가 backtester.py `precompute_signals()`나 model_trainer.py `_grid_search()`에서 호출되는가?
  - pump_detector 조건4 전례: 30일 이력 루프(pump_detector.py L.75-92)가 "종목×시점" 반복 호출 시
    누적 비용이 크므로 `backtest=True` 경로에서는 pump 호출 자체가 스킵됨 (strategy.py L.129 분기)
  - `precompute_signals()` 내에서 `get_signal(backtest=True)` 사용 — backtester.py L.382
  - 그리드서치 경로에서 네트워크 I/O 발생하면 FDR 호출 수 급증

### A12. MAX_POSITIONS / MAX_STOCKS 실전전환
- [ ] `MAX_POSITIONS`(config.py L.75, 현재=5) / `MAX_STOCKS`(watchlist.py L.22, 현재=200)가 관련된 변경인가?
  - 모의투자 데이터 축적용으로 확대된 값 — 실전 전환 시 반드시 MAX_POSITIONS=3, MAX_STOCKS=100으로 원복
  - 실전 전환 작업이면 `실전전환_체크리스트.md` 전체 절차를 따를 것

### A13. 기존 보유 포지션은 새 로직의 보호를 받지 않음
- [ ] 사이징·리스크 관련 코드(calc_quantity, cash cap, 손실한도 등) 수정 시,
  **수정 이전에 매수된 보유 포지션**이 새 로직 기준으로 과대/부적합하지 않은지 확인
  - 전례: 2026-06-30 cash cap(trader.py L.157) 도입 전 모의계좌 5억 기준으로 사이징된
    073240 포지션(운용자금의 96%)이 07-02 손절되며 -906,327원 — 단일 청산이
    일일손실한도(-3%) 전체를 소진
  - 리스크 로직 수정 완료 보고에는 "기존 포지션 잔존 리스크" 항목을 포함할 것

### A14. 관찰 계층·walk-forward 판정 규칙 보존
- [ ] **market_scanner.py는 관찰 전용** — 그 출력(market_scan_cache.json)을 매수/매도/사이징
  판단에 연결하는 변경은 kis-strategy-review 합격 판정 없이 금지 (news_filter OBSERVE 전례).
  관찰용 조회 API를 장중 60초 루프에 부착하는 것도 금지 — 실전 앱키 유량을 현재가·차트와 경합
- [ ] model_trainer.py의 walk-forward 판정 상수(VAL_MONTHS=3, TRAIN_MIN_TRADES=30,
  VAL_MIN_TRADES=10, IMPROVE_MARGIN=0.10)는 `그리드서치확장_설계.md` §4가 근거 —
  임의 변경 금지, 변경 시 설계 문서 개정 + kis-strategy-review 판정 선행
- [ ] `_grid_search()`의 `ticker_dfs` 원본 보관 구조 보존 — 제거하면 바깥 루프마다
  FDR 재호출(20×9=180회) 폭증 (설계 §3 구현 요건)

---

## B. 변경 후 필수 검증

- [ ] `evaluate.py` 기준(기댓값>0, 손익비≥1.5, MDD≥-5%, 거래≥30건) 재평가 결과 제시 (해당 시)
- [ ] 백테스트 추정치 vs 실측치를 표로 구분 (섞어서 "개선됨" 단정 금지)
- [ ] 파라미터(SL/TP/RSI 등) 영향 시 CLAUDE.md "파라미터 변경 이력" 표 업데이트 제안
- [ ] 리팩토링 있었다면 `python model_trainer.py --verify` — 신호 자체가 바뀌지 않았는지 확인

---

## 위반 시 처리

체크리스트 항목 중 하나라도 위반이면 **코드 수정안을 제시하지 않는다.**
위반 항목을 먼저 보고하고 사용자가 방향을 결정하도록 한다.

---

## 출력 형식

```
[변경 요약] 1줄
[영향 범위] backtest / 실시간 / 둘 다
[체크리스트 위반] 없음 / 항목 나열 (A1~A14 기준)
[코드 diff 또는 패치]
[평가 결과] 기댓값/손익비/MDD/거래수 — PASS/FAIL (해당 시)
[다음 액션] 1. 2. 3.
```
