# app_v2.py UI 구조화 — 실행 프롬프트

> Sonnet으로 실행 권장 (구조가 확정된 기계적 이동 작업). 실행 전 Shift+Tab으로 auto-accept edits 모드를 켤 것.

---

`golf_swing_analyzer/app_v2.py`(885줄, UI 전용)를 `ui/` 패키지로 분리한다. **로직 변경 절대 금지 — 코드 이동과 import 배선만.** 아래 단계를 순서대로, 각 단계 완료 시 즉시 git commit & push(한국어 메시지, 항목별 개별 커밋)하고, 중간에 나에게 확인 질문 없이 끝까지 진행한다. 잘못되면 git으로 되돌리면 되니 멈추지 마라.

## 0단계: 미커밋 상태 선정리 (분리 시작 전 필수)

현재 워킹트리에 1단계(analyzer/ 코어 분리) 결과물이 커밋되지 않은 채 쌓여 있다. UI 분리를 시작하기 전에 아래를 **의미 단위로 나눠서** 커밋+푸시:

1. `golf_swing_analyzer/analyzer/` 신규 + `app_v2.py` 축소분 → "분석 코어를 analyzer/ 패키지로 분리 (로직 무변경, 테스트 영상 3종 회귀 통과)"
2. `.claude/` (스킬 8종) + `CLAUDE.md` + `골프코칭_스킬세트_생성_프롬프트.md` + 이 파일 → "golf-* 스킬세트 및 프로젝트 문서 추가"
3. `golf_swing_analyzer/video/` (mp4 3종+img.png), `reference_db.json`, `Intelligent_Golf_Swing_AI.pptx`, `golf_swing_analyzer/skills/`(kis 참고용) → "테스트 영상·참고 자산 추가" — **주의: mp4/pptx가 용량이 크니 커밋 전 `git check-ignore`로 .gitignore 상태 확인하고, 100MB 넘는 파일은 없는지 확인 (최대 23MB라 문제없을 것)**
4. `.idea/` 변경분은 판단해서 커밋하거나 .gitignore 처리

## 1단계: ui/ 패키지 생성 및 분리

`golf_swing_analyzer/ui/` 패키지를 만들고 app_v2.py 코드를 아래 매핑대로 이동 (현재 줄번호 기준 — 실행 시점에 실제 파일 다시 확인할 것):

| 새 모듈 | 이동 대상 (현 app_v2.py) |
|---|---|
| `ui/styles.py` | CSS markdown 블록(L.22-108)을 문자열 상수 + `inject_css()` 함수로, `render_hero()`(L.118-124) |
| `ui/components.py` | `render_metric_card()`(L.127), `get_status()`(L.137) |
| `ui/sidebar.py` | `render_sidebar()`(L.143-204) |
| `ui/tab_analysis.py` | Tab1 블록 전체(L.225-510)를 `render(sample_rate, ref_db)` 함수로 — 내부 `get_frame_at()` 중첩 함수 포함 |
| `ui/tab_phases.py` | Tab2 블록(L.511-624)을 `render()` 함수로 |
| `ui/tab_data.py` | Tab3 블록(L.625-668)을 `render()` 함수로 |
| `ui/tab_coaching.py` | Tab4 블록(L.669-756)을 `render(provider, model_name, api_key, ref_db)` 함수로 |
| `ui/tab_learning.py` | Tab5 블록(L.757-880)을 `render(sample_rate, ref_db)` 함수로 |

`app_v2.py`에는 남길 것: import + `st.set_page_config()` + `inject_css()` 호출 + `main()`(사이드바 호출, ref_db 세션 로드, `st.tabs()` 생성, 각 탭 render 호출 배선).

### 이동 시 절대 규칙
- **`st.set_page_config()`는 반드시 첫 Streamlit 호출** — app_v2.py에 남기고, ui/ 모듈은 최상위에서 `st.*`를 호출하면 안 된다(함수 정의만). CSS 주입도 함수로 감싸서 set_page_config 이후에 호출
- Tab1의 대표 프레임 선택 로직(임팩트=첫 프레임, 다운스윙 85%, 나머지 중간 — 현 L.469-480)은 golf-code-change A8 불변식 — **문자 그대로** 이동, 절대 "개선" 금지
- 세션 상태 키 이름(`phase_det`, `eff_sample`, `trim_path` 등, 현 L.395-405) 변경 금지
- 각 탭의 조기 반환 가드(`"summary" not in st.session_state` 등, 현 L.512/626/670) 그대로 유지
- 탭 내부의 `import pandas as pd` 인라인 import는 그대로 둬도 됨 (동작 동일)
- analyzer/ 패키지는 한 글자도 건드리지 않는다

커밋: "Streamlit UI를 ui/ 패키지로 분리 (탭별 모듈화, 로직 무변경)"

## 2단계: 검증

분석 코어(analyzer/)는 무변경이므로 영상 3종 재검증은 불필요. 대신:

1. `python -c "import ast; ..."` 수준이 아니라 실제 기동: `streamlit run golf_swing_analyzer/app_v2.py` — 에러 없이 뜨는지
2. `golf_swing_analyzer/video/일반.mp4` 하나만 업로드→분석 실행이 끝까지 돌아가는지 확인 가능하면 확인 (브라우저 자동화 가능하면 시도, 안 되면 기동 확인까지만 하고 결과에 명시)
3. 이동 후 app_v2.py에 잔존 참조(옮긴 함수를 여전히 직접 부르는 곳) 없는지 grep 확인

문제 발견 시 해당 커밋만 revert하고 원인을 보고서에 남긴다.

## 3단계: 스킬·문서 줄번호 동기화 (이동으로 무효화된 참조 갱신)

1단계에서 코어 분리 때 스킬 줄번호가 전부 낡았던 전례가 있다. 이번에도 app_v2.py 줄번호를 인용하는 스킬을 전부 갱신:

- `.claude/skills/golf-ui-ux/SKILL.md` — A2(세션 키 L.395-405, trim_path L.246), A3(대표 프레임 L.465-486), A4(임계값 4곳 중 app_v2.py 3곳), A5(가드 L.512/626/670) → 새 ui/ 모듈 경로·줄번호로
- `.claude/skills/golf-code-change/SKILL.md` — A7의 UI 참조(L.454-486), A8(L.469-480) → `ui/tab_analysis.py` 기준으로
- `.claude/skills/golf-coach-llm/SKILL.md` — A3 사이드바(L.154-158) → `ui/sidebar.py`, A4 에러 분기(L.697-701) → `ui/tab_coaching.py`
- `.claude/skills/golf-analysis-quality/SKILL.md` — 판정절차 1의 차트(L.556)·경고(L.441-443) → 새 위치
- `CLAUDE.md` — "단일 파일" 전제의 아키텍처 설명이 완전히 낡았음. analyzer/ + ui/ 구조 기준으로 섹션맵을 다시 쓰되, 알고리즘 설명(7단계 감지 원리, 불변식)은 그대로 유지

커밋: "모듈 분리 반영 — 스킬 줄번호·CLAUDE.md 구조 갱신"

## 4단계: 완료 보고

```
[커밋 목록] 해시 + 메시지 나열
[구조 변경 요약] before/after 줄 수
[검증 결과] 기동 확인 / 영상 분석 확인 여부
[스킬 동기화] 갱신한 파일 목록
[발견된 이슈] 있으면 (없으면 "없음")
```
