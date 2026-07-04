---
name: golf-coach-llm
description: 골프 스윙 AI 코칭 리포트(LLM 프롬프트 구조, 페르소나, 원인→결과→해결책 형식, Gemini/Claude/GPT 공급자별 차이)를 다룰 때 사용한다. "코칭 리포트 이상해", "AI 피드백 프롬프트 손보고 싶어", "코칭 문구 바꿔줘", "LLM 응답이 이상해", "다른 모델로 바꿔줘" 같은 말이 나오면 트리거한다. 앱이 최종 사용자에게 보여줄 build_prompt()/get_llm_feedback() 관련 요청 전용 — 개발자가 다음 세션·다음 작업에서 쓸 실행 프롬프트를 요청하는 경우("이거 프롬프트로 만들어줘")는 golf-prompt-engineer 관할, 헷갈리면 "코칭 리포트/AI 피드백"이라는 단어가 있는지로 구분한다. 점수 산정 로직(compute_score)이나 임계값 자체는 golf-code-change 관할 — 이 스킬은 그 결과를 사람 언어로 설명하는 프롬프트·출력 형식만 다룬다.
---

# 골프 AI 코칭 리포트 — 프롬프트 품질

## 핵심 원칙: Explainable AI (PPTX 슬라이드 3)

이 프로젝트의 차별점은 "단순 수치 나열이 아닌 원인→결과를 설명하는 AI 코치"다.
예시(슬라이드 3): "임팩트 시 척추각이 5도 들리는 현상은 백스윙 시 오른쪽 골반의
회전이 부족하여 발생한 결과입니다." — 수치 하나를 독립적으로 던지지 않고
**원인(다른 지표) → 결과(관찰된 현상) → 해결(구체적 교정법)** 구조로 연결한다.

`build_prompt()`의 출력 형식(analyzer/coach_llm.py L.93-101, 2026-07-04 모듈 분리로 app_v2.py에서 이동됨)이 이 원칙을 강제한다:
```
### ⚠️ 핵심 교정 포인트 (원인 → 결과 → 해결책)
**[1번 포인트]**: (원인) ~ 때문에, (결과) ~ 현상이 발생합니다. (해결) ~을 실천하세요.
```
이 형식을 느슨하게 바꾸면(예: 단순 나열형으로 변경) 프로젝트의 핵심 차별점이 사라진다 — 신중히 판단.

---

## A. 프롬프트 수정 시 확인 사항

### A1. 구조화 데이터 전달 방식
- [ ] `build_prompt()`가 JSON 블록(총 프레임/척추각/회전분석/관절평균/7단계 페이즈별 데이터, analyzer/coach_llm.py L.61-83)으로
  구조화된 데이터를 먼저 제시한 뒤 코칭 형식을 요청하는 흐름을 유지하는가?
  - 근거: analyzer/coach_llm.py L.9-105 — LLM이 "느낌"이 아니라 실측 수치 기반으로 답하게 하는 장치

### A2. 기준 DB 비교 블록은 조건부
- [ ] `ref_block`(analyzer/coach_llm.py L.17-53)은 `ref_db`에 "프로" 라벨 데이터가 있을 때만 생성된다 — 없으면 빈 문자열
  - 현재 `reference_db.json`이 비어있어 이 블록은 실질적으로 항상 비어 있음 — "프로 기준과 비교했다"는 표현을 리포트에 유도하려면 먼저 DB 축적이 선행돼야 함 (golf-analysis-quality의 테스트 영상 학습 활용 가능)

### A3. 공급자별 기본 모델
- [ ] Gemini/Claude/GPT 전환 시 기본 모델명이 최신인지 확인
  - 근거: analyzer/coach_llm.py L.115 (`model_name or "gemini-2.0-flash"`), L.124 (`"claude-3-5-sonnet-20241022"`), L.134 (`"gpt-4o"`)
  - 사이드바 모델 선택지(ui/sidebar.py L.15-19, 2026-07-04 UI 분리로 app_v2.py에서 이동)도 동일 목록과 동기화돼 있는지 확인 — 하드코딩된 모델명이 두 곳(analyzer/coach_llm.py 기본값, ui/sidebar.py selectbox)에 중복돼 있어 한쪽만 갱신하면 불일치 발생
  - Claude 모델을 다룰 때는 claude-api 참조 스킬로 최신 모델 ID를 재확인할 것 — 이 프로젝트 코드의 하드코딩 값을 그대로 믿지 않는다

### A4. 에러 메시지 매핑
- [ ] `get_llm_feedback()` 호출 실패 시 UI의 에러 분기(ui/tab_coaching.py L.37-42: API_KEY/quota/connect 키워드 매칭)가 새 공급자 도입 시에도 커버되는가
  - 문자열 키워드 매칭 방식이라 공급자별 실제 예외 메시지 포맷이 다르면 "알 수 없는 오류"로 뭉뚱그려질 수 있음

### A5. 페르소나 일관성
- [ ] "20년 경력 투어 프로 출신 코치" 페르소나(analyzer/coach_llm.py L.57)를 변경하려는가 — 톤/전문성 수준이 바뀌면 위 Explainable 원칙과 별개로 사용자 신뢰도에 영향, 변경 시 사용자 확인

---

## B. 새 공급자 추가 시

- `get_llm_feedback()`의 `elif provider == "..."` 분기(analyzer/coach_llm.py L.108-140) 패턴을 따른다 — lazy import 유지(Claude/GPT SDK는 선택됐을 때만 import — Gemini(`google.genai`)는 예외적으로 모듈 상단에서 항상 import됨, CLAUDE.md "LLM Integration" 서술과 다르니 새 공급자 추가 시 이 불일치를 그대로 답습할지 확인)
- 사이드바 `model_options` 딕셔너리(ui/sidebar.py L.15-19)에 모델 목록 추가 필수 — 빠뜨리면 UI 선택지와 실제 지원 공급자가 불일치

---

## 출력 형식

```
[대상] 프롬프트 구조 / 공급자 전환 / 페르소나 / 에러 처리
[Explainable 원칙 영향] 원인→결과→해결책 형식 유지 여부
[변경 내용]
[동기화 확인] 사이드바 모델 목록 vs 기본값 일치 여부 (해당 시)
[다음 액션]
```

## 경계

- 점수 산정 로직(`compute_score`, 임계값) 자체 → golf-code-change
- 리포트 표시 UI(카드 스타일, 다운로드 버튼) → golf-ui-ux
