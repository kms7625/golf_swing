# docs/research — 골프 스윙 역학·단계 인식 문헌 조사

조사·취합 2026-10-08 · 지시서 `golf-biomech-research-prompt.md`

| 파일 | 내용 |
|---|---|
| `golf-biomech-research-prompt.md` | 조사 지시서(RQ1~6, 출처 기준, 이중 조사 절차) |
| `01_claude_findings.md` | Claude 독립 조사 — 33편(본문 2, 초록 25, 서지만 6) |
| `02_codex_findings.md` | Codex(gpt-6-astra) 독립 조사 — 26편(본문 16, 초록 10). `01` 미열람을 실행 로그로 확인 |
| `03_merged_review.md` | 취합 — 중복 제거 **47편**(양쪽 12 / Codex만 14 / Claude만 21), RQ별 합의·상충 |
| `04_swinglab_implications.md` | 근거 → 코드 적용 제안 P1~P8(**제안만, 구현 안 함**) |
| `references.bib` | BibTeX 47개(DOI 42개는 doi.org 공식 BibTeX, DOI 없는 5개는 수기·출처 표기) |

## 조사 범위·기준
- RQ1 운동학적 연쇄 · RQ2 골반 개시·전환 · RQ3 역학·에너지·X-Factor · RQ4 단계·이벤트 검출 · RQ5 단안 2D 포즈·회전 · RQ6 데이터셋
- 학술 출처만, DOI 또는 공식 URL을 실제로 열어 확인한 것만 채택. 수치는 초록·본문 위치와 함께 인용

## 검증 (취합 단계, Claude 직접 실행)
| 검사 | 결과 |
|---|---|
| DOI 42개 doi.org 등록 조회 | 42/42 성공, 실패 0 |
| Codex DOI 20개 Crossref 제목 대조 | 20/20 일치 |
| DOI 없는 출처 URL 열림(Codex 6편) | 8/8 URL 200 |
| 수치 표본 대조 | Smith 2016 X-Factor 2D–3D −16.72 ± 6.20°, 15명, 핸디캡 1–29 — 원문 PDF와 일치 |
| 04의 제안이 검증된 출처를 인용 | P1~P8 모두 인용(서지만 확인 출처는 근거에서 제외) |
| 검증 실패로 제외 | 0편 (Claude 조사 단계에서 서지 미확인 1편은 이미 제외) |

## 한계
- 체계적 문헌고찰·메타분석이 아니다(두 에이전트의 키워드 검색 + 참고문헌 추적)
- ResearchGate·CVF·MDPI·PMC 일부 페이지 403/CAPTCHA → 공개 API·저자본으로 대체, 유료 원문 우회 없음
- **골프에서 MediaPipe의 골반·흉곽 축 회전각을 모션캡처와 직접 비교한 연구는 두 조사 모두 찾지 못함** — 회전 지표 개선은 자체 검증이 필요
- 서지만 확인 5편(Vena 2011, Lynn 2013, Izumoto 2019, Sinclair 2014, Lead/Trail Legs 2018)은 수치 인용 금지
- 데이터셋(GolfDB·CaddieSet 등)의 원본 영상 이용 권리는 다운로드 전 개별 확인 필요
