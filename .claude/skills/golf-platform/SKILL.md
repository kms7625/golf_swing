---
name: golf-platform
description: 골프 스윙 분석 프로젝트의 되돌리기 어려운 구조 결정(단일 파일→모듈 분리, 웹/모바일 프레임워크 선택, 분석 코어와 프론트엔드 사이 연결 방식)을 오케스트레이션한다. "웹이랑 앱 어떻게 나눠?", "구조 바꿔도 될까", "모듈로 쪼개자", "프론트엔드 뭘로 만들지", "이 구조로 가도 돼?" 같은 말이 나오면 트리거한다. 이 스킬은 직접 코드를 리팩토링·구현하지 않고, "코어 보존 + 껍데기 교체" 원칙(CLAUDE.md/프로젝트 메모리 확정 사항)을 지키며 결정을 게이트하고 개별 실행은 golf-code-change·golf-ui-ux·golf-realtime에 위임하는 관제탑 역할만 한다.
---

# 골프 프로젝트 플랫폼 구조 — 관제탑

## 이 스킬의 역할과 한계

멀티플랫폼(웹+앱) 전환과 실시간 지원은 단일 파일(원래 `app_v2.py` 1986줄) 구조로는
불가능한 목표다. 이 전환은 여러 스킬에 걸친 작업이며, 한번 커밋되면 되돌리기
어려운 구조 결정(모듈 경계, API 계약, 프레임워크 선택)을 포함한다. 이 스킬은
직접 판단하거나 코드를 고치지 않는다 — **확정된 방향**(아래)을 전제로 각 결정을
단계별로 게이트하고, 실행은 다른 스킬에 위임하는 것이 유일한 책임이다.

**현재 위치: 1단계 완료 (2026-07-04)** — 원래 `app_v2.py`(1986줄)를 두 차례에 걸쳐 분리:
① Section 0~8(분석 코어)을 `golf_swing_analyzer/analyzer/` 패키지(mp_setup.py, reference_db.py,
geometry.py, smoothing.py, phase_detector.py, drawing.py, pipeline.py, scoring.py, coach_llm.py)로,
② 남은 UI(Section 9~10, 885줄)를 다시 `golf_swing_analyzer/ui/` 패키지(styles.py, components.py,
sidebar.py, tab_analysis/phases/data/coaching/learning.py)로 분리. `app_v2.py`는 배선만 남아 53줄.
테스트 영상 3종(일반/프로/프로2.mp4) 전체 회귀 검증 통과, UI 분리는 Streamlit AppTest로
5개 탭 무예외 렌더링 확인. **다른 golf-* 스킬의 줄번호 인용은 두 분리 모두 반영해 갱신됨 —
아직 참조가 `app_v2.py`의 옛 줄번호(900 이상)를 가리키고 있다면 낡은 것이다.**

## 확정된 방향 — "코어 보존 + 껍데기 교체" (2026-07-04 결정)

1. **분석 코어(Section 0~8)는 보존** — 관절각 수학, 7단계 감지, 스무딩/보간, 점수 계산은
   재작성 금지. 로직 변경 없이 모듈(`analyzer/` 패키지 등)로 분리만 한다
2. **Streamlit 껍데기(Section 9)는 교체** — 실시간 카메라·모바일 앱은 Streamlit으로
   구조적으로 불가능. 새 프론트엔드(웹 → 앱 순)를 신규 구축
3. **기존 Streamlit 앱은 검증 기준(reference implementation)으로 유지** — 테스트 영상
   3종 + reference_db.json으로 새 구현의 회귀 검증에 사용
4. 현재 단계 감지는 post-hoc 구조 — 실시간 전환 설계는 golf-realtime 관할

이 방향에 반하는 결정(예: 코어 로직까지 처음부터 재작성)을 제안받으면, 이 방향이
언제·왜 확정됐는지 상기시키고 재검토 사유를 먼저 확인한다.

## 절대 규칙

1. **선행 결정 없이 실행을 시작하지 않는다** — 예: 프론트엔드 프레임워크 미확정 상태로 UI 컴포넌트부터 작성 금지
2. **단계당 1승인** — 아래 단계 완료 시 결과를 보고하고 사용자의 명시적 "다음 진행"을 기다린다. 여러 단계를 한 턴에 묶어 실행하지 않는다
3. **코어 로직 변경이 필요한 리팩토링(모듈 분리 포함)은 golf-code-change 체크리스트를 통과해야 한다** — "구조만 바꾸는 것"이어도 예외 없음

## 단계

### 0단계: 현황 판정 (읽기 전용 — 언제든 실행 가능)
- 현재 `app_v2.py`(UI) + `analyzer/`(코어) 구조 재확인
- 테스트 영상 3종(golf_swing_analyzer/video/) + reference_db.json 존재 확인 (회귀 검증 준비 상태)

### 1단계: 코어 모듈 분리 (로직 무변경) — ✅ 완료 (2026-07-04)
- `app_v2.py` Section 0~8을 `golf_swing_analyzer/analyzer/` 패키지로 분리 완료 — 함수 시그니처와 알고리즘 그대로, import 경로만 변경
- golf-code-change 체크리스트 A1~A9 통과 확인 완료 (인덱스 매핑, argmax 방식, 원시좌표 구분 등 그대로 보존)
- golf-analysis-quality로 테스트 영상 3종(일반/프로2/프로.mp4) 전체 회귀 검증 통과 (frame_data/annotated_frames/trajectory_pts 인덱스 정합 유지, 7단계 전부 감지)
- Streamlit 앱이 새 import 구조로 정상 기동 확인 완료
- **추가로 완료(같은 날)**: 남은 UI(Section 9~10, 885줄)를 `golf_swing_analyzer/ui/` 패키지로 재분리 — CSS/사이드바/5개 탭을 모듈당 파일로, `app_v2.py`는 배선만 남아 53줄. Streamlit AppTest로 5개 탭 무예외 렌더링 확인. 이동으로 무효화된 golf-ui-ux·golf-code-change·golf-coach-llm·golf-analysis-quality의 줄번호 참조 전부 갱신

### 2단계: 프론트엔드 아키텍처 결정 — ✅ 결정 완료 (2026-07-05)

**전제 확인(사용자 답변)**: 배포 형태 = 취업/데모 포트폴리오, JS 경험 = 거의 없음(Python 주력).

**확정 아키텍처 — 하이브리드(3안)**:
1. **웹 프레임워크**: React + Vite + TypeScript SPA — SEO/SSR 불필요한 도구형 앱, Next.js 과잉. 정적 배포(Vercel/GitHub Pages 무료)
2. **코어 연결**: `server/`(FastAPI, 얇게)가 `analyzer/`를 직접 import — 코어 무포팅·무재검증. 배포는 무료/저가 티어(Render, Fly.io, HF Spaces Docker 등)
3. **실시간**: 온디바이스 MediaPipe Tasks JS(라이브 스켈레톤·관절각) + **스윙 종료 후 손목 Y 시계열(float 배열)만 서버 전송해 검증된 Python `detect_all_phases()` 실행** (golf-realtime 방향 A). JS 포팅 범위는 `geometry.py` 하나로 제한(순수 수학 ~70줄, 테스트 영상 3종으로 Python 대조 검증)
4. **모바일(4단계)**: Capacitor로 웹앱 래핑 — 네이티브 재작성 없음
5. **리포 구조**: `server/` + `web/` 신설, `golf_swing_analyzer/`(Streamlit)는 reference implementation으로 유지

**설계 유의점(3단계에서 반영)**:
- annotated_frames 전량 API 반환 금지 — 대표 프레임 7장 + frame_data JSON만 반환, 차트는 프론트 렌더
- 실시간 경로엔 CLAHE 없음 — 저조도 정확도 별도 확인 항목
- LLM 키는 현행(사용자 직접 입력, 클라이언트 보관) 유지 + 포트폴리오 방문자용으로 샘플 분석 결과 프리로드(키·서버 없이도 데모 가능하게)

**기각한 대안**: 1안 서버 중심(실시간이 PPTX 온디바이스 비전과 충돌 — 포트폴리오 핵심 가치 훼손), 2안 완전 온디바이스(코어 전체 JS 재구현·재검증 + CLAHE 부재 리스크가 1인·JS 무경험 조건에 과대)

### 3단계: 신규 웹 프론트엔드 구축 — 범위 확정 (2026-07-05, 사용자 합의)

**포함**:
- `server/` FastAPI 3개 엔드포인트: `POST /analyze`(영상→분석 결과), `POST /detect-phases`(손목Y 시계열→7단계 경계, 5단계 실시간 대비 선구현), `POST /coaching`(LLM 리포트 프록시)
- API 응답: 대표 프레임 7장 + frame_data JSON + score/issues — annotated_frames 전량 반환 금지
- `web/` 핵심 플로우: 업로드 → 트리밍(자동 감지 초기값 + **수동 슬라이더**, HTML5 video currentTime 바인딩으로 서버 왕복 없는 미리보기) → 분석 → 결과(점수·메트릭·7단계 그리드·차트) → AI 코칭(사용자 키 입력)
- **한/영 토글(i18n)**: 문자열 딕셔너리 방식. 서버 응답의 한국어 페이즈명("어드레스" 등)은 코드 키(address/backswing/...)로 매핑하는 테이블을 프론트에 두고 표시만 번역 — 서버 응답 포맷은 불변(코어 무변경 원칙)
- **완전 새 디자인**: 기존 다크그린 테마에 앵커링하지 않음. 디자인 시안 2개 제시 → 사용자 선택 게이트 필수. 단 7페이즈 색상은 서버가 그리는 대표 프레임 오버레이(analyzer/drawing.py PHASE_COLORS)와 일치해야 함 — 기본은 기존 7색 계승, 새 팔레트로 가려면 drawing.py 색값 동기 변경을 golf-code-change 경유로(색값만, 로직 무변경)
- 샘플 프리로드: 테스트 영상 3종 분석 결과를 정적 JSON 번들 — 방문자가 키·서버 없이 결과 열람
- 동일성 검증 게이트: 3종 영상을 새 API로 돌려 Streamlit reference와 frame_data/score 대조 (golf-analysis-quality)

**제외**: Tab5 기준 학습(Streamlit reference에 유지), Tab3 CSV/원시 테이블(후순위)
**완료 기준**: ① 로컬 전체 플로우 동작 ② 3종 동일성 검증 통과 ③ 샘플 프리로드 동작. **배포는 별도 게이트**(무료 티어 콜드스타트/타임아웃 확인 필요)
- 기존 Streamlit 앱은 삭제하지 않고 reference implementation으로 유지

### 4단계: 모바일 앱 확장
- 웹 프론트엔드 안정화 후 착수 (2단계 결정에 따라 네이티브 vs 웹뷰 래핑 vs 크로스플랫폼 선택)
- 실시간 카메라 기능은 이 단계에서 golf-realtime 설계를 반영

### 5단계: 실시간 기능 통합
- golf-realtime에서 설계한 방향(A: 배치 후처리 / B: 슬라이딩 윈도우)을 웹/앱에 통합
- 신규 알고리즘(방향 B 선택 시)은 golf-code-change + golf-analysis-quality 순서로 검증 후 병합

## 출력 형식

```
[현재 단계] 0~5 중 위치
[이번 턴 수행] 수행 내용 + 위임한 스킬
[코어 보존 확인] 로직 무변경 여부 (해당 시)
[회귀 검증 결과] golf-analysis-quality 결과 요약 (해당 시)
[다음 단계 진행 조건] 사용자 승인 대기 항목 명시
```
