---
name: kis-ops-infra
description: KIS 자동매매의 Windows 인프라 계층(작업 스케줄러·PowerShell 스크립트·프로세스 기동/종료·premarket_check)을 점검·수정할 때 사용한다. "스케줄러가 안 돌았어", "trader가 자동 시작 안 됐어", "17:00에 안 꺼졌어", "start_trader.ps1 고쳐줘", "08:50 알림이 안 왔어", "PC 늦게 켰는데 어떻게 해" 같은 말이 나오면 트리거한다. Python 전략·매매 코드(.py의 신호/주문 로직)는 다루지 않는다 — 그건 kis-code-change.
---

# KIS 운영 인프라 — Windows 스케줄러·PowerShell 계층

## 관할 범위

| 자산 | 역할 | 등록 |
|---|---|---|
| `start_trader.ps1` | trader.py+대시보드 시작, WMI CommandLine 기반 중복 실행 방지 | 작업 스케줄러 08:00 |
| `premarket_check.py` | 장전 점검 텔레그램 (프로세스·오류 tail 50줄 확인) | 작업 스케줄러 08:50 |
| `stop_trader.ps1` | trader.py·streamlit 종료, WMI CommandLine 기반 | 작업 스케줄러 17:00 |
| `run_morning_check.ps1` | claude CLI 헤드리스 아침점검(morning_check_prompt.md) → send_morning_report.py 텔레그램 발송. 조회 도구만 허용(Edit/Write 차단) | 작업 스케줄러 평일 09:07 (StockMorningCheck, StartWhenAvailable) |

이 스킬은 **인프라 계층만** 다룬다. 전략·신호·주문 로직 수정은 kis-code-change(A1~A14),
운용 상태 진단은 kis-daily-monitor로 넘긴다. 경계 사례: "trader가 안 떠 있어"의 원인이
스케줄러/스크립트면 이 스킬, Python import 오류면 kis-code-change.

## 확립된 원칙 (위반 금지)

1. **프로세스 식별은 WMI CommandLine 필터만 사용** — `Get-WmiObject Win32_Process -Filter
   "Name='python.exe'"` + `CommandLine -like '*trader.py*'` 패턴.
   `taskkill /FI "WINDOWTITLE eq ..."`은 Start-Process로 뜬 파이썬 창 제목("Python")과
   불일치해 **매일 조용히 실패한 전례** 있음 (stop_trader.ps1 헤더 주석 참조).
2. **python.exe 절대경로 고정** — `C:\Users\trian\AppData\Local\Programs\Python\Python312\`
   (start_trader.ps1). PATH 의존 금지 — 스케줄러 환경은 사용자 셸과 PATH가 다름.
3. **중복 실행 방지 로직 보존** — start_trader.ps1은 이미 실행 중이면 스킵.
   수동 실행 중 스케줄러가 추가 실행해도 충돌 없어야 함.
4. 스크립트 수정 후에도 **커밋 & push** (한국어 메시지) — .ps1도 git 추적 대상.
5. **파일 기록은 `-Encoding utf8` 명시** — PS5.1의 `*>`/`>` 리다이렉션과 Out-File
   기본값은 UTF-16 LE라, 파이썬이 UTF-8로 읽는 파일에 쓰면 깨짐. 네이티브 출력은
   변수로 캡처 후 `Out-File -Encoding utf8`로 기록 (실측: run_morning_check.ps1
   텔레그램 미발송 원인, 2026-07-03 — 파이썬 측도 utf-8-sig/utf-16 폴백 이중 방어).

## 알려진 운영 시나리오

### PC를 08:00 이후에 켠 경우
스케줄러 작업이 "놓친 일정 실행" 옵션 없이 등록됐다면 그날 자동 시작이 건너뜀.
- 확인: trader.log에 당일 "자동매매 시작" 배너 유무
- 조치: `powershell -ExecutionPolicy Bypass -File start_trader.ps1` 수동 실행
  (08:30 이전이면 아침 재검증도 자동 수행됨. 08:30 이후면 _run_morning_recheck가
  다음 사이클에서 당일 미실행 감지 후 실행되므로 별도 조치 불필요)
- 근본 대책 제안 시: 작업 스케줄러 속성에서 "가능한 한 빨리 놓친 일정 시작" 활성화
  — 단 스케줄러 설정 변경은 사용자 승인 후

### 08:50 텔레그램이 안 온 경우 (원인 3분법)
1. **스케줄러 미실행** — 작업 스케줄러 이력에서 08:50 작업 확인
2. **premarket_check.py 실패** — 수동 실행해 오류 재현
   (`$env:PYTHONIOENCODING="utf-8"; python premarket_check.py`)
3. **notifier 발송 실패** — 텔레그램 토큰/네트워크. notifier는 미설정 시 print 대체이므로
   스케줄러 이력이 성공인데 미수신이면 이쪽
- premarket_check.py는 `wmic` 명령 사용 중 — **wmic는 Windows 최신 빌드에서 제거 추세**,
  실패 시 PowerShell CIM 대체 필요 (알려진 잠재 리스크)

### 17:00에 안 꺼진 경우
- trader.log 마지막 줄 시각으로 판정: 16:59:5x면 정상, 17:00 이후 로그가 이어지면 실패
- 실패 시 stop_trader.ps1 수동 실행으로 종료되는지 먼저 확인 (스크립트 문제 vs 스케줄러 문제 분리)

## 점검 커맨드

```powershell
# 프로세스 확인 (스크립트와 동일 기준)
Get-WmiObject Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*trader.py*' } | Select ProcessId, CommandLine
# 스케줄러 작업 상태
Get-ScheduledTask | Where-Object { $_.TaskName -like '*Stock*' -or $_.TaskName -like '*trader*' } | Get-ScheduledTaskInfo
```

## 출력 형식

```
[증상] 1줄
[원인 계층] 스케줄러 / 스크립트 / notifier / Python 코드(→kis-code-change 이관)
[근거] 로그·이력·재현 결과
[조치] 즉시 조치 / 사용자 승인 필요 항목 구분
```
