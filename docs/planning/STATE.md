# Swing.Lab — D05 상태

**현재 상태 (state_revision=23, DRAFT): P05 완료 · P06 완료 — UI-01~08 이미지 전부 승인(코발트, DEC-03). 승인 시안: UI-01 r2a(APR-06), UI-02 r3(APR-07), UI-03 r2(APR-08), UI-04 r1(APR-10), UI-05 r1(APR-12), UI-06 r1(APR-16), UI-07 r1(APR-17), UI-08 r1(APR-18). 구현 메모 8건(JSON `implementation_notes`). 다음 단계 P07~P08.**

Planning Agents v3.0 `90_SHARED_CONTRACTS.md` C02 형식. 총괄 단일 작성, `ROLE_GUIDED`; 실제 하위 에이전트 실행 없음.

## 작업 이력 (각 단계 당시 기록 — "현재·최신" 표현은 그 시점 기준. 현재 상태는 위 요약과 아래 JSON이 기준)

현재 작업에서 JSON은 state_revision 9→10 및 ASSET-07 추가만 갱신했다. 아래 두 문단은 **r2 당시 요약 기록**이며, JSON의 기존 screens·scope·pending_question·next_action도 과거 기록으로 보존한다. 현재 검토 대상은 위 r3 한 장이다.

이번 검토 대상: [UI-02 r2 시안](mockups/UI-02_r2.png) · [브리프](briefs/UI-02_r2.md) · [대조 기록](briefs/UI-02_r2_review.md) · [실제 생성 입력](briefs/UI-02_r2.imagegen.txt). 출력·영상 비율·재생 막대 등의 차이를 공개했다. 새 승인은 없으며, 아래 기존 screens·작업 필드는 과거 기록으로 보존한다. 다음 사용자 응답은 **UI-02 r2 승인 / 수정 요청**이다.

```json
{
  "project_id": "swinglab-web-ux-20261008",
  "bible_version": "3.0",
  "state_revision": 23,
  "scope_id": "D04-10_D05-07_UI-03",
  "scope_revision": 1,
  "status": "DRAFT",
  "readiness": "DRAFT",
  "current_stage": "P06",
  "request_mode": "docs/planning/ 안에서 APR-05 기록·UI-03 분석 진행 중 시안 1장 생성·대조·보고 후 중지",
  "execution_mode": "ROLE_GUIDED",
  "primary_role": "D05",
  "support_roles": [
    "D04",
    "D06"
  ],
  "reference_only_roles": [],
  "facts": [
    {
      "statement": "기존 웹 제품을 현재 사실로 조사하되 과거 승인·디자인을 승계하지 않는다.",
      "source": "docs/planning/codex-planning-agents-prompt.md §1–3"
    },
    {
      "statement": "App.tsx와 components/*.tsx 전체를 정적으로 읽었으며 7개 Stage와 별도 인증 모달을 8개 UI로 묶었다.",
      "source": "web/src/App.tsx 및 web/src/components/*.tsx; UI_STRUCTURE.md §1–3"
    },
    {
      "statement": "조사 시작 HEAD c3e51d7, 최종 확인 HEAD 4092489. 외부 작업에 따른 Hero.module.css·Hero.tsx 변경을 다시 읽었다. 그 사이 web/src·server 변경은 두 Hero 파일뿐이며 본 작업의 코드 수정·커밋은 없다.",
      "source": "읽기·git status/log/diff 결과; web/src/components/Hero.module.css 및 Hero.tsx"
    },
    {
      "statement": "기존 Club Lime은 현재 CSS의 사실일 뿐 이번 UI_STRUCTURE 또는 UI_IMAGE 승인이 아니다.",
      "source": "web/src/index.css:1; 사용자 작업 지시 §1"
    },
    {
      "statement": "D04 최초 조사에서는 모든 크기·색상 설계가 미승인이었다. 이후 UI-01 r1만 APR-02로 승인되었다. UI-02에는 그 색 역할·서체 느낌·모서리·버튼 형태를 시각 참고로 적용한다. 360px은 제안값이며 실제 기기·브라우저 동작은 미확인이다.",
      "source": "UI_STRUCTURE.md §1, §3, §6"
    },
    {
      "statement": "사용자 결정은 UI-01 구조 동의와 첫 시안 생성 요청이다. 생성될 이미지 승인으로 확대하지 않는다.",
      "source": "docs/planning/codex-planning-d05-prompt.md §1–3"
    },
    {
      "statement": "1440×900은 16:10이라 지시서의 16:9와 불일치한다. 1440×900은 배치 참고로 보존하고 16:9 1440×810을 생성 목표로 해석했다. 사용자 규격 승인 아님.",
      "source": "docs/planning/briefs/UI-01_r1.md §1"
    },
    {
      "statement": "UI-01 첫 시안 1장 실제 생성 성공. 문구 오류는 육안 대조에서 발견하지 못했으며 출력 치수·패널 비율·배치·자산 차이를 기록했다. 실제 HTML·키보드 기능은 미확인.",
      "source": "docs/planning/briefs/UI-01_r1_review.md"
    },
    {
      "statement": "UI-02 구조 동의와 이미지 생성 요청 원문은 “1번으로 진행해”. 구조 revision 2를 APR-03으로 기록하며 결과 이미지 승인은 생성하지 않는다.",
      "source": "docs/planning/codex-planning-d05-ui02-prompt.md §1–3"
    },
    {
      "statement": "UI-01 r1 PNG를 실제 열람·디코딩하고 SHA-256이 기존 APR-02의 승인 당시 해시와 일치함을 확인했다. docs/screenshots/에는 hero.jpg·result.jpg만 있고 UI-02 캡처는 없다. 현재 UI-02는 코드 근거로 재구성한다.",
      "source": "로컬 파일 조회·Pillow·SHA-256; web/src/components/UploadTrim.tsx 및 UploadTrim.module.css; web/src/lib/i18n.tsx"
    },
    {
      "statement": "UI-02 r1을 내장 image_gen 1회로 생성하고 PNG 1672×941과 원본 복사 일치·해시를 확인했다. 문구 오류는 육안 대조에서 발견하지 못했으나 목표 출력 치수·9:16 영상 비율·배치·보조 버튼 글자색·플레이어 위치 차이 5건을 기록했다. 생성 성공을 시각 요구 전체 충족이나 승인으로 간주하지 않는다.",
      "source": "docs/planning/briefs/UI-02_r1_review.md"
    },
    {
      "statement": "STATE revision 3에 남은 UI-01 pending 질문과 승인 없음 설명은 이미 존재하는 APR-02에 따라 정정했다. APR-01·APR-02 레코드·ASSET-01 파일/해시/승인은 보존하며 새 승인을 추가하지 않았다.",
      "source": "STATE의 기존 APR-02 및 ASSET-01; question_history"
    },
    {
      "statement": "작업 전후 해시 대조에서 본 작업 산출물 5개 외에 docs/planning/eval/NIELSEN_EVAL.md 및 docs/research 문서 4개의 동시 변경을 관찰했다. 변경 주체는 미확인이다. 본 작업은 해당 파일을 쓰거나 되돌리지 않았으며 화면 참고로도 사용하지 않았다. HEAD와 코드 파일 해시는 유지되었다.",
      "source": "작업 시작/종료 git ls-files 파일 목록·SHA-256 대조; 실행 도구 쓰기 대상 기록"
    },
    {
      "statement": "UI-03의 대표 상태는 서버 접수 후 analyzing/30%이다. server/main.py 단계 경계 값과 일치하며 실제 영상 분석 측정값은 아니다. 진행률은 프레임/시간 비율이 아니다.",
      "source": "server/main.py jobs.set_stage; server/jobs.py; briefs/UI-03_r1.md"
    },
    {
      "statement": "UI-03 뒤로 가기와 이탈 결과 문구는 ISSUE-02 개선 제안이다. 서버 취소 API는 확인되지 않았고 현행 App은 늦은 응답 무효화가 없어 구현 완료로 간주하지 않는다.",
      "source": "web/src/App.tsx; web/src/lib/api.ts; server/jobs.py; briefs/UI-03_r1.md §6"
    },
    {
      "statement": "기존 APR-04를 근거로 UI-02 pending·D05-08·approval_note의 낡은 설명을 정정했다. APR-01~04와 승인 PNG·해시는 보존했다.",
      "source": "STATE revision 5의 APR-04 및 ASSET-02"
    },
    {
      "statement": "UI-03 r1은 내장 image_gen 1회로 생성 후 지정 PNG로 그대로 복사했다. 실제 KO 문구 오류는 육안 대조에서 발견 못했으나 출력 규격·막대 31.6%·배치·승인 시각 언어 차이 5건을 공개했다.",
      "source": "docs/planning/briefs/UI-03_r1_review.md; TEST-07·08"
    },
    {
      "statement": "STATE revision 6 작업의 작성 파일은 STATE·UI-03 브리프·도구 입력·대조 기록·PNG 5개로 docs/planning/ 한정이다. 생성 도구 원본은 도구 기본 위치에 보유한다. 작업 중 별도 codex-ui01-fresh-prompt.md 추가를 관찰했으나 작성하거나 변경하지 않았다.",
      "source": "기준 스냅샷과 파일 해시 비교·실제 쓰기 대상; briefs/UI-03_r1_review.md §5"
    }
  ],
  "decisions": [
    {
      "id": "DEC-01",
      "revision": 2,
      "status": "DECIDED",
      "subject": "첫 화면의 주 행동",
      "options": [
        "A: 내 영상 바로 업로드",
        "B: 샘플 결과 먼저 체험"
      ],
      "recommendation": "A",
      "selected": "A: 내 영상 바로 업로드",
      "approval_id": "APR-01",
      "affected_entities": [
        "UI-01",
        "UI-02",
        "REQ-01"
      ],
      "question": "첫 화면의 중심을 ‘내 영상 바로 업로드’와 ‘샘플 결과 먼저 체험’ 중 어디에 둘까요?",
      "answer": "내 영상 바로 업로드로 진행해",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "source_reference": "docs/planning/codex-planning-d05-prompt.md §1",
      "approval_scope": "UI-01 업로드 우선 구조 동의 및 첫 시안 1장 생성 요청. UI_IMAGE·다른 화면·구현 승인 없음."
    },
    {
      "id": "DEC-02",
      "date": "2026-10-08",
      "question": "r1의 짙은 초록·라임 느낌을 어떻게 살릴까요? (다크 테마로 / 강조색만 라임으로 / 전체 다크 / UI-03만 다크)",
      "answer": "강조색만 라임으로",
      "context": "사용자가 UI-03 r2 검토 중 UI-03 r1 이미지를 보내며 '이 느낌도 좀 살렸으면좋겠어'",
      "effect": "흰 배경 유지, 강조색 코발트 → 짙은 초록+라임. UI-01 r2a·UI-02 r3(승인)·UI-03 r2의 색 변경 버전 필요. 기존 승인은 새 버전 승인 전까지 유지"
    },
    {
      "id": "DEC-03",
      "date": "2026-10-08",
      "question": "(사용자 주도) 강조색 라임 변경판(UI-01 r3·UI-02 r4·UI-03 r3) 검토 후 방향",
      "answer": "이걸로 진행 — UI-01_r2a·UI-02_r3·UI-03_r2(코발트) 이미지 3장을 첨부해 선택",
      "supersedes": "DEC-02",
      "effect": "강조색은 코발트 유지. 라임 변경판 3장 미채택"
    }
  ],
  "requirements": [
    {
      "id": "REQ-01",
      "revision": 1,
      "status": "DRAFT",
      "title": "분석 진입·파일·구간 선택",
      "screens": [
        "UI-01",
        "UI-02"
      ]
    },
    {
      "id": "REQ-02",
      "revision": 1,
      "status": "DRAFT",
      "title": "분석 진행·실패 복구",
      "screens": [
        "UI-03"
      ]
    },
    {
      "id": "REQ-03",
      "revision": 1,
      "status": "DRAFT",
      "title": "결과·비교·저장·코칭",
      "screens": [
        "UI-04"
      ]
    },
    {
      "id": "REQ-04",
      "revision": 1,
      "status": "DRAFT",
      "title": "촬영·라이브 결과·정식 분석",
      "screens": [
        "UI-05"
      ]
    },
    {
      "id": "REQ-05",
      "revision": 1,
      "status": "DRAFT",
      "title": "기록·추이·삭제",
      "screens": [
        "UI-01",
        "UI-06"
      ]
    },
    {
      "id": "REQ-06",
      "revision": 1,
      "status": "DRAFT",
      "title": "인증과 원래 작업 복귀",
      "screens": [
        "UI-07",
        "UI-04",
        "UI-05",
        "UI-06"
      ]
    },
    {
      "id": "REQ-07",
      "revision": 1,
      "status": "DRAFT",
      "title": "개인정보 안내·입력 보존",
      "screens": [
        "UI-08",
        "UI-02"
      ]
    },
    {
      "id": "REQ-08",
      "revision": 1,
      "status": "DRAFT",
      "title": "이동·뒤로·새로고침·닫기",
      "screens": [
        "UI-01",
        "UI-02",
        "UI-03",
        "UI-04",
        "UI-05",
        "UI-06",
        "UI-07",
        "UI-08"
      ]
    },
    {
      "id": "REQ-09",
      "revision": 1,
      "status": "DRAFT",
      "title": "좁은 화면·키보드·상태 인지",
      "screens": [
        "UI-01",
        "UI-02",
        "UI-03",
        "UI-04",
        "UI-05",
        "UI-06",
        "UI-07",
        "UI-08"
      ]
    }
  ],
  "screens": [
    {
      "id": "UI-01",
      "name": "첫 화면",
      "revision": 1,
      "structure_revision": 2,
      "status": "DRAFT",
      "structure_approval_id": "APR-01",
      "image_state": "APPROVED",
      "assets": [
        "ASSET-01"
      ],
      "structure_reference": "docs/planning/briefs/UI-01_r1.md",
      "image_approval_id": "APR-06",
      "image_revision": "2a"
    },
    {
      "id": "UI-02",
      "name": "업로드·구간 선택",
      "revision": 1,
      "structure_revision": 2,
      "status": "DRAFT",
      "structure_approval_id": "APR-03",
      "image_state": "APPROVED",
      "assets": [
        "ASSET-02"
      ],
      "structure_reference": "docs/planning/briefs/UI-02_r1.md",
      "image_approval_id": "APR-07",
      "image_revision": 3
    },
    {
      "id": "UI-03",
      "name": "분석 진행",
      "revision": 1,
      "structure_revision": 2,
      "status": "DRAFT",
      "structure_approval_id": "APR-05",
      "image_state": "APPROVED",
      "assets": [
        "ASSET-03"
      ],
      "structure_reference": "docs/planning/briefs/UI-03_r1.md",
      "image_approval_id": "APR-08",
      "image_revision": 2
    },
    {
      "id": "UI-04",
      "name": "결과",
      "revision": 1,
      "structure_revision": 1,
      "status": "DRAFT",
      "structure_approval_id": null,
      "image_state": "APPROVED",
      "assets": [],
      "image_approval_id": "APR-10",
      "image_revision": 1
    },
    {
      "id": "UI-05",
      "name": "실시간 캠",
      "revision": 1,
      "structure_revision": 1,
      "status": "DRAFT",
      "structure_approval_id": null,
      "image_state": "APPROVED",
      "assets": [],
      "image_approval_id": "APR-12",
      "image_revision": 1
    },
    {
      "id": "UI-06",
      "name": "내 기록",
      "revision": 1,
      "structure_revision": 1,
      "status": "DRAFT",
      "structure_approval_id": null,
      "image_state": "APPROVED",
      "assets": [],
      "image_approval_id": "APR-16",
      "image_revision": 1
    },
    {
      "id": "UI-07",
      "name": "로그인·회원가입",
      "revision": 1,
      "structure_revision": 1,
      "status": "DRAFT",
      "structure_approval_id": null,
      "image_state": "APPROVED",
      "assets": [],
      "image_approval_id": "APR-17",
      "image_revision": 1
    },
    {
      "id": "UI-08",
      "name": "개인정보처리방침",
      "revision": 1,
      "structure_revision": 1,
      "status": "DRAFT",
      "structure_approval_id": null,
      "image_state": "APPROVED",
      "assets": [],
      "image_approval_id": "APR-18",
      "image_revision": 1
    }
  ],
  "approvals": [
    {
      "id": "APR-01",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-01",
      "target_id": "UI-01",
      "target_revision": 2,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "내 영상 바로 업로드로 진행해",
      "source_reference": "docs/planning/codex-planning-d05-prompt.md §1의 사용자 결정 원문 인용",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-02",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-01",
      "target_id": "UI-01",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "승인할게",
      "source_reference": "2026-10-08 Claude Code 세션 사용자 발화. 직전 안내: 검토 대상은 UI-01_r1 한 장뿐, DIFF(패널 약 4:5·'샘플 데이터' 배지·'내 스윙 기록' 하단 띠) 공개 후 승인/수정 질문",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
      "delegated_scope_or_null": null,
      "note": "공개된 차이를 포함한 r1 이미지 그대로의 승인. 이미 구현된 9:16 패널(커밋 2fef560)과 시안의 약 4:5 패널 중 무엇을 구현 기준으로 할지는 P08에서 확인 필요"
    },
    {
      "id": "APR-03",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-02",
      "target_id": "UI-02",
      "target_revision": 2,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해",
      "source_reference": "docs/planning/codex-planning-d05-ui02-prompt.md §1의 사용자 발화 원문 인용; 직전 안내: UI-02 업로드부터 한 장씩 만들고 승인을 받아요",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-02 구조 동의와 시안 생성 요청만. 파일 선택 후 구간 선택 대표 상태 1장, ISSUE-01·03·06·11 제안 반영. UI_IMAGE·구현 승인 아님."
    },
    {
      "id": "APR-04",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-02",
      "target_id": "UI-02",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "UI-02 승인하고 5번 2번만 고쳐줘",
      "source_reference": "2026-10-08 Claude Code 세션 사용자 발화. 직전 안내: 검토 대상은 UI-02_r1 한 장, 영상 영역 9:16 대비 약 6% 좁음 공개 후 승인/수정 질문",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "ded31c7b6b7b31e5077f1622415982f83d85ef5845281ff47f1c23ebff3f7b90",
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-05",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-03",
      "target_revision": 2,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해",
      "source_reference": "docs/planning/codex-planning-d05-ui03-prompt.md §1의 사용자 발화 원문 인용; 직전 안내: 나머지 화면 시안 생성(P06 계속): UI-02 업로드부터 한 장씩 만들고 승인을 받아요",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "지시서가 해당 발화를 이번 UI-03 구조 동의와 생성 요청으로 기록하도록 명시. 후속 발화 “UI-02 승인하고 5번 2번만 고쳐줘. 시안작업은?”도 계속 진행 확인 근거. ISSUE-02·11을 반영한 분석 진행 중 대표 상태 1장만. 결과 이미지·서버 취소 기능·구현 승인으로 확대하지 않음."
    },
    {
      "id": "APR-06",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-01",
      "target_revision": "2a",
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "a로 가자",
      "source_reference": "2026-10-08 Claude Code 세션. 직전 질문: 'A / B / A에 B의 단계 그림 합치기(r3)' 중 선택. 사용자 요청 '첫화면부터 기존 화면을 참고하지말고 코덱스로 새롭게 시안 만들어봐'로 생성된 r2a·r2b 중 r2a 선택",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
      "delegated_scope_or_null": null,
      "note": "r2a 속 인물은 실사형 생성 이미지(‘이미지 예시’ 표기). 구현 시 촬영 사진 또는 권리 확인된 이미지로 교체 필요"
    },
    {
      "id": "APR-07",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-02",
      "target_revision": 3,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "응 r3 승인",
      "source_reference": "2026-10-08 Claude Code 세션. 사용자가 시안 공개 전 '승인'이라 답해 대상 확인을 요청했고, r3 이미지와 글자 오류 공개 후 '응 r3 승인'으로 확정",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
      "delegated_scope_or_null": null,
      "note": "이미지 속 파형 라벨 '잔목 감지 구간'은 생성 글자 오류 — 구현 문구는 '자동 감지 구간'. 파형·수치는 예시 데이터"
    },
    {
      "id": "APR-08",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-03",
      "target_revision": 2,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "이걸로 진행 (UI-01_r2a·UI-02_r3·UI-03_r2 이미지 첨부)",
      "source_reference": "2026-10-08 Claude Code 세션. 사용자가 세 시안 파일을 직접 첨부해 선택",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
      "delegated_scope_or_null": null,
      "note": "UI-01 r2a(APR-06)·UI-02 r3(APR-07) 기존 승인 재확인. UI-03 r2의 뒤로 가기 버튼 초점선이 불명확 — 구현 시 다른 화면과 같은 초점 표시 적용"
    },
    {
      "id": "APR-09",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-04",
      "target_id": "UI-04",
      "target_revision": 1,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해 / 이걸로 진행",
      "source_reference": "docs/planning/codex-ui04-prompt.md 근거 절: 나머지 화면 한 장씩 시안·승인 및 UI-01_r2a·UI-02_r3·UI-03_r2 코발트 3장 선택을 UI-04 구조 동의·생성 요청으로 기록하도록 명시",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-04 구조 revision 1 동의와 결과 화면 첫 뷰포트 r1 한 장 생성 요청에 한정. UI_IMAGE·구현·다른 화면 승인 아님. X-Factor 변경(P5)은 미결정."
    },
    {
      "id": "APR-10",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-04",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "승인",
      "source_reference": "2026-10-08 Claude Code 세션. UI-04_r1 이미지와 걸리는 점 3가지(X-Factor 카드 ✕ vs 진단 warning 불일치, 영어 warning/good 라벨, 저장·공유 버튼 스크롤 아래) 공개 후 '승인'",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-11",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-05",
      "target_id": "UI-05",
      "target_revision": 1,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해 / 승인(UI-04 r1)",
      "source_reference": "docs/planning/codex-ui05-prompt.md 근거 절: 나머지 화면 한 장씩 진행 발화와 UI-04 승인(APR-10) 후 진행을 UI-05 구조 동의·생성 요청으로 APR-11에 기록하도록 명시",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-05 구조 revision 1 동의 및 촬영 중 대표 상태 r1 한 장 생성 요청에 한정. 선행 UI-04 승인 발화를 UI-05 이미지 승인으로 확대하지 않는다. UI_IMAGE·구현·다른 화면 승인 없음."
    },
    {
      "id": "APR-12",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-05",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "진행해",
      "source_reference": "2026-10-08 Claude Code 세션. 직전 질문 'UI-05를 승인하시겠어요, 수정 요청하시겠어요?'(추천: 승인)에 대한 답. 검토 대상은 UI-05_r1 한 장뿐이라 승인으로 해석",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588",
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-13",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-06",
      "target_id": "UI-06",
      "target_revision": 1,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해 / 진행해",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md 근거 절: 인용된 사용자 발화를 UI-06 구조 동의·생성 요청으로 APR-13에 기록하도록 명시",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-06 구조 revision 1과 r1 대표 상태 한 장 생성 요청에 한정. 지시서가 인용한 발화이며 UI_IMAGE·구현 승인으로 확대하지 않는다. 생성된 화면의 이미지 승인은 사용자에게 별도로 받는다."
    },
    {
      "id": "APR-14",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-07",
      "target_id": "UI-07",
      "target_revision": 1,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해 / 진행해",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md 근거 절: 인용된 사용자 발화를 UI-07 구조 동의·생성 요청으로 APR-14에 기록하도록 명시",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-07 구조 revision 1과 r1 대표 상태 한 장 생성 요청에 한정. 지시서가 인용한 발화이며 UI_IMAGE·구현 승인으로 확대하지 않는다. 생성된 화면의 이미지 승인은 사용자에게 별도로 받는다."
    },
    {
      "id": "APR-15",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-08",
      "target_id": "UI-08",
      "target_revision": 1,
      "revision_kind": "structure_revision",
      "approval_kind": "UI_STRUCTURE",
      "statement": "1번으로 진행해 / 진행해",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md 근거 절: 인용된 사용자 발화를 UI-08 구조 동의·생성 요청으로 APR-15에 기록하도록 명시",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": null,
      "delegated_scope_or_null": null,
      "note": "UI-08 구조 revision 1과 r1 대표 상태 한 장 생성 요청에 한정. 지시서가 인용한 발화이며 UI_IMAGE·구현 승인으로 확대하지 않는다. 생성된 화면의 이미지 승인은 사용자에게 별도로 받는다."
    },
    {
      "id": "APR-16",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-06",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "모두 승인",
      "source_reference": "2026-10-08 Claude Code 세션. UI-06·07·08 r1 세 장을 화면별로 공개하고 '세 장을 모두 승인할까요?' 질문에 대한 답",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "cbc1b41691e3f48d1c448ddc8ad4e05370802a846184ef18eea7a08fe98e6af6",
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-17",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-07",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "모두 승인",
      "source_reference": "2026-10-08 Claude Code 세션. UI-06·07·08 r1 세 장을 화면별로 공개하고 '세 장을 모두 승인할까요?' 질문에 대한 답",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "997e9ed917aee50d2c222e64d4b5103f8294727a84f0a2786c7a66d2dffc5c28",
      "delegated_scope_or_null": null
    },
    {
      "id": "APR-18",
      "project_id": "swinglab-web-ux-20261008",
      "scope_id": "D04-10_D05-07_UI-03",
      "target_id": "UI-08",
      "target_revision": 1,
      "revision_kind": "image_revision",
      "approval_kind": "UI_IMAGE",
      "statement": "모두 승인",
      "source_reference": "2026-10-08 Claude Code 세션. UI-06·07·08 r1 세 장을 화면별로 공개하고 '세 장을 모두 승인할까요?' 질문에 대한 답",
      "date": "2026-10-08",
      "timestamp_or_null": null,
      "artifact_sha256_or_null": "400ac67ea96ea60700e3bd63138c37cac74144e9f48877b1cc5500fd939420c0",
      "delegated_scope_or_null": null
    }
  ],
  "integrations": [],
  "risks": [],
  "tests": [
    {
      "id": "TEST-01",
      "related_requirements": [
        "REQ-01",
        "REQ-02",
        "REQ-03",
        "REQ-04",
        "REQ-05",
        "REQ-06",
        "REQ-07",
        "REQ-08",
        "REQ-09"
      ],
      "kind": "문서 구조 검사",
      "scenario": "카드 필드·UI/REQ/ISSUE 참조·revision·질문·실제 파일 대조",
      "status": "PASSED",
      "environment": "로컬 파일·Python 표준 라이브러리",
      "target_revision": 1,
      "execution_evidence_or_null": "2026-10-08 로컬 Python 검사 출력 PASS: JSON 해석, UI 8개×9개 순서 필드, 카드별 5개 상태·제안값 360px, REQ 9개 양방향 연결, ISSUE 12개·상위 3개, 미결 결정 1개, revision=1/DRAFT/승인 없음, 모든 로컬 링크·산출물 존재 확인. 실제 제품 동작 시험 아님."
    },
    {
      "id": "TEST-02",
      "related_requirements": [
        "REQ-01",
        "REQ-02",
        "REQ-03",
        "REQ-04",
        "REQ-05",
        "REQ-06",
        "REQ-07",
        "REQ-08",
        "REQ-09"
      ],
      "kind": "실제 브라우저·기기·API 시험",
      "scenario": "정상/실패 흐름, 키보드, 제안값 360px, 카메라 권한, 세션 만료, 새로고침 복구",
      "status": "NOT_RUN",
      "environment": "미확인",
      "target_revision": 1,
      "execution_evidence_or_null": null
    },
    {
      "id": "TEST-03",
      "related_requirements": [
        "REQ-01",
        "REQ-09"
      ],
      "kind": "산출물 파일·상태 구조 검사",
      "scenario": "PNG 디코딩·치수·해시·원본 복사 일치·참조 파일·revision·GENERATED와 UI_STRUCTURE 승인 분리",
      "status": "PASSED",
      "environment": "로컬 Python/Pillow",
      "target_revision": 2,
      "execution_evidence_or_null": "2026-10-08 Python/Pillow 검사 PASS: PNG 디코딩·1672×941·생성 원본/복사본 SHA-256 일치, 시안 1장, STATE DRAFT/revision 2, UI-01 구조 2/시안 1 및 다른 UI revision 1 유지, UI_STRUCTURE 승인만 존재, ASSET GENERATED, 모든 산출물/로컬 링크 존재, KO 14개 키 원문 일치, HEAD 4092489·추적 파일 diff 없음·기존 .DS_Store 외 변경 경로 docs/planning/ 한정. 시각 요구 전체 충족·실제 제품 동작 검증 아님."
    },
    {
      "id": "TEST-04",
      "related_requirements": [
        "REQ-01",
        "REQ-09"
      ],
      "kind": "생성 시안의 브리프 육안 대조",
      "scenario": "UI-01 실제 KO 문구·업로드 주 행동·초점·샘플 보조·9:16 패널·배치·자산 확인",
      "status": "FAILED",
      "environment": "내장 image_gen 표시 결과 및 로컬 PNG; 같은 에이전트 육안 검토",
      "target_revision": {
        "ui_revision": 1,
        "structure_revision": 2
      },
      "execution_evidence_or_null": "docs/planning/briefs/UI-01_r1_review.md. 문구 오류는 발견하지 못했으나 캐릭터 패널 9:16 불충족·목표 출력 치수 차이 등 DIFF-01–04. 생성 성공과 요구 충족을 구분함."
    },
    {
      "id": "TEST-05",
      "related_requirements": [
        "REQ-01",
        "REQ-07",
        "REQ-09"
      ],
      "kind": "산출물 파일·상태 구조 검사",
      "scenario": "PNG 디코딩·원본 복사/해시·기존 승인 자산 보존·KO 원문·참조 경로·APR-03과 ASSET-02 GENERATED 구분·쓰기 범위/HEAD 대조",
      "status": "PASSED",
      "environment": "로컬 Python/Pillow·git 읽기 전용 조회",
      "target_revision": {
        "state_revision": 4,
        "ui_revision": 1,
        "structure_revision": 2
      },
      "execution_evidence_or_null": "2026-10-08 Python/Pillow 검사 PASS: 두 PNG 실제 디코딩·치수/bytes/SHA-256·원본 복사 일치, APR-02 승인 해시 보존, STATE revision 4/DRAFT·UI 8개·APR 3개·ASSET 2개·ID 유일성, UI-02 UI_STRUCTURE와 GENERATED 분리·승인 해시 null, 기존 KO 14개 및 도구 입력 가시 KO 11개 일치, 신규 문구 후보 4개 구별, 합성 시간 산술, 로컬 Markdown 링크 21개 및 전체 artifact 파일 존재, 시안 1장·pending 질문 1개 확인. HEAD 409248998b56b958eef33e75a156a0fba7fae7a1 및 web/server/analyzer 기준 해시 동일. 본 작업 쓰기는 STATE·UI-02 브리프/입력/리뷰/PNG 5개. 동시 변경 docs/planning/eval/NIELSEN_EVAL.md·docs/research/00_README.md·03_merged_review.md·04_swinglab_implications.md·references.bib는 별도 관찰이며 수정/되돌리기 없음. 전체 작업공간 무변경 판정이나 실제 제품 시험은 아님."
    },
    {
      "id": "TEST-06",
      "related_requirements": [
        "REQ-01",
        "REQ-07",
        "REQ-09"
      ],
      "kind": "생성 시안의 브리프·UI-01 육안 대조",
      "scenario": "파일 변경·초점 표현·감지 완료·라벨·합성 수치·CTA·개인정보 원문·9:16 영상·16:9 출력·스타일",
      "status": "FAILED",
      "environment": "내장 image_gen 표시 결과 및 복사한 로컬 PNG; 같은 에이전트 육안 대조",
      "target_revision": {
        "ui_id": "UI-02",
        "ui_revision": 1,
        "structure_revision": 2
      },
      "execution_evidence_or_null": "docs/planning/briefs/UI-02_r1_review.md. 문구 오류는 발견하지 못했으나 9:16 영상 비율 등 DIFF-01–05 기록. 생성·대조 완료와 요구 전체 충족을 구분함."
    },
    {
      "id": "TEST-07",
      "related_requirements": [
        "REQ-02",
        "REQ-08",
        "REQ-09"
      ],
      "kind": "UI-03 산출물 파일·상태 구조 검사",
      "scenario": "PNG 디코딩·치수·해시·원본 일치, KO 문구표, 기존 승인/자산 보존·UI_STRUCTURE/GENERATED 분리",
      "status": "PASSED",
      "environment": "로컬 Python/Pillow·파일 JSON 검사",
      "target_revision": 6,
      "execution_evidence_or_null": "2026-10-08 PASS: PNG 1672×941·1,268,542 bytes·원본 바이트/SHA-256 일치, KO 9개 키 브리프 원문 일치, APR-01~04·ASSET-01~02·다른 UI·기존 TEST 보존, APR-05 구조 2·UI-03/ASSET-03 GENERATED·이미지 승인 null·산출물/링크 존재. 실제 브라우저/API/접근성 검증 아님."
    },
    {
      "id": "TEST-08",
      "related_requirements": [
        "REQ-02",
        "REQ-08",
        "REQ-09"
      ],
      "kind": "UI-03 시각 요구 대조",
      "scenario": "실제 생성 PNG의 문구·배치·막대와 숫자·승인 두 시안의 시각 언어 비교",
      "status": "FAILED",
      "environment": "도구 이미지 육안 대조, Pillow 색 픽셀 범위 보조 확인",
      "target_revision": 1,
      "execution_evidence_or_null": "2026-10-08: 한글 문구 오류는 발견 못함. DIFF-01~05: 출력 치수/근사 비율, 30% 숫자와 약31.6% 막대, 카드 배치, 상단/색 역할, 완료 행/숫자 표현 차이. 상세 briefs/UI-03_r1_review.md. 생성 성공·기록 완료와 시각 요구 전체 충족을 분리."
    }
  ],
  "artifacts": [
    {
      "path": "docs/planning/UI_STRUCTURE.md",
      "kind": "D04 구조 revision 1 역사 기록; 활성 UI-01·UI-02·UI-03 구조 revision 2는 각 briefs/UI-0x_r1.md",
      "status": "DRAFT",
      "revision": 1
    },
    {
      "path": "docs/planning/STATE.md",
      "kind": "최소 활성 상태",
      "status": "DRAFT",
      "revision": 6
    },
    {
      "path": "docs/planning/briefs/UI-01_r1.md",
      "kind": "D05 생성 브리프",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/briefs/UI-01_r1.imagegen.txt",
      "kind": "실제 이미지 생성 도구 입력",
      "status": "DRAFT",
      "revision": 1
    },
    {
      "path": "docs/planning/briefs/UI-01_r1_review.md",
      "kind": "D05-06 문구·배치·자산 대조",
      "status": "DRAFT",
      "revision": 1
    },
    {
      "path": "docs/planning/mockups/UI-01_r1.png",
      "kind": "UI-01 첫 시안",
      "status": "SUPERSEDED",
      "revision": 1,
      "asset_id": "ASSET-01",
      "sha256": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
      "superseded_by": "ASSET-04 (APR-06)"
    },
    {
      "path": "docs/planning/briefs/UI-02_r1.md",
      "kind": "D05 생성 브리프",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/briefs/UI-02_r1.imagegen.txt",
      "kind": "실제 이미지 생성 도구 입력",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/briefs/UI-02_r1_review.md",
      "kind": "D05-06 문구·배치·UI-01 시각 언어 대조",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/mockups/UI-02_r1.png",
      "kind": "UI-02 파일 선택 후 구간 선택 첫 시안",
      "status": "APPROVED",
      "revision": 1,
      "asset_id": "ASSET-02",
      "sha256": "ded31c7b6b7b31e5077f1622415982f83d85ef5845281ff47f1c23ebff3f7b90"
    },
    {
      "path": "docs/planning/briefs/UI-03_r1.md",
      "kind": "D05 생성 브리프",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/briefs/UI-03_r1.imagegen.txt",
      "kind": "실제 이미지 생성 도구 입력",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/briefs/UI-03_r1_review.md",
      "kind": "D05-06 문구·배치·승인 시각 언어 대조",
      "status": "DRAFT",
      "revision": 1,
      "structure_revision": 2
    },
    {
      "path": "docs/planning/mockups/UI-03_r1.png",
      "kind": "UI-03 분석 진행 중 첫 시안",
      "status": "GENERATED",
      "revision": 1,
      "asset_id": "ASSET-03",
      "sha256": "030672914927f0b8778e48c281c8aac303283a89dfdfb8d1f203940e0c95a611"
    }
  ],
  "stage_status": [
    {
      "stage": "P05",
      "status": "COMPLETE",
      "scope": "UI-01·UI-02·UI-03 구조 동의와 각 1장 D05 진입만",
      "reason": "APR-01·03 유지, UI-03 APR-05 기록. UI-04–08 동의로 확대하지 않음."
    },
    {
      "stage": "D04-01_D04-08",
      "status": "COMPLETE",
      "reason": "기존 8개 구조 카드·흐름·검수 제안 작성 기록 유지"
    },
    {
      "stage": "D04-09_D04-10",
      "status": "COMPLETE",
      "reason": "지시서에 인용된 사용자 원문·날짜·구조 revision 2·시안 생성 요청 범위를 APR-03으로 기록.",
      "scope": "UI-02"
    },
    {
      "stage": "D04-11",
      "status": "COMPLETE",
      "reason": "UI-02_r1.md 브리프 저장 후 생성 실행.",
      "scope": "UI-02"
    },
    {
      "stage": "D04-12",
      "status": "COMPLETE",
      "reason": "UI-02 핵심 요소와 ISSUE-01·03·06·11 제안 대조. 영상 비율 등 차이 기록, 구현 완료 아님.",
      "scope": "UI-02"
    },
    {
      "stage": "P06",
      "status": "COMPLETE",
      "reason": "UI-01~08 이미지 전부 승인(코발트, DEC-03). 다음: P07 데이터·권한·연동 → P08 기술 확정·명세"
    },
    {
      "stage": "D05-01_D05-04",
      "status": "COMPLETE",
      "reason": "APR-03 구조/생성 동의·APR-02 참고 이미지 해시·브리프·대표 상태 1개 고정.",
      "scope": "UI-02"
    },
    {
      "stage": "D05-05",
      "status": "COMPLETE",
      "reason": "내장 image_gen 1회 성공, 원본 PNG를 지정 경로에 그대로 복사·디코딩·해시 확인.",
      "scope": "UI-02"
    },
    {
      "stage": "D05-06",
      "status": "COMPLETE",
      "reason": "실제 KO와 신규 후보 문구 대조·배치/비율/스타일 차이 5건 기록. 시각 요구 전체 충족 아님.",
      "scope": "UI-02"
    },
    {
      "stage": "D05-07",
      "status": "COMPLETE",
      "reason": "실제 이미지가 도구 결과로 표시되었으며 docs/planning/mockups/UI-02_r1.png 확보.",
      "scope": "UI-02"
    },
    {
      "stage": "D05-08",
      "status": "COMPLETE",
      "reason": "기존 APR-04 UI-02 이미지 승인에 따라 오래된 대기 설명 정정. 신규 승인 아님.",
      "scope": "UI-02"
    },
    {
      "stage": "D05-09_D05-12",
      "status": "NOT_STARTED",
      "reason": "사용자 반응 이후 수정·승인·구현 인계 범위. 자산 메타데이터 확보만 선행.",
      "scope": "UI-02"
    },
    {
      "stage": "D04-09_D04-11",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "명시 지시의 발화 근거로 APR-05 및 구조 revision 2, 생성 전 브리프 저장."
    },
    {
      "stage": "D05-01_D05-04",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "승인된 두 참고 PNG 실제 열람·디코딩·해시 확인, 접수 후 analyzing/30% 대표 상태 고정."
    },
    {
      "stage": "D05-05",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "내장 image_gen 1회 성공. 원본 PNG 복사·디코딩·치수·바이트·SHA-256 확인."
    },
    {
      "stage": "D04-12",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "핵심 구조·ISSUE-02/11 시각 표현 대조. 동작은 제안이며 구현 완료 아님."
    },
    {
      "stage": "D05-06",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "실제 KO·후보 문구 대조와 5건의 배치/규격/시각 언어 차이 공개. 시각 요구 전체 충족 아님."
    },
    {
      "stage": "D05-07",
      "status": "COMPLETE",
      "scope": "UI-03",
      "reason": "실제 생성 이미지가 도구 결과로 표시되었고 지정 경로에 원본과 같은 파일 확보."
    },
    {
      "stage": "D05-08",
      "status": "WAITING_USER",
      "scope": "UI-03",
      "reason": "유일한 UI-03 r1에 대한 승인/수정 요청 질문 하나. 이미지 승인 발화 없음."
    },
    {
      "stage": "D05-09_D05-12",
      "status": "NOT_STARTED",
      "scope": "UI-03",
      "reason": "수정·승인·구현 인계는 후속 범위. 자산 메타데이터 확보만 선행."
    }
  ],
  "blockers": [],
  "deferred": [
    "ISSUE-01–ISSUE-12의 구현·재현은 이번 범위 밖; UI-02 네 이슈는 구조 개선 제안만 반영",
    "브라우저·실기기·카메라·권한·접근성·서버 실제 정책 검증",
    "개인정보처리방침 시행 정보·연락처·법적 적정성 확인",
    "구현 인계와 코드 수정",
    "UI-02 빈 드롭존 상태의 다음 revision 후보",
    "UI-03 이미지 승인·접수 전/오류/모바일 등 추가 상태 시안",
    "UI-04–08 시안 생성 및 승인"
  ],
  "question_history": [
    {
      "decision_id": "DEC-01",
      "question": "첫 화면의 중심을 ‘내 영상 바로 업로드’와 ‘샘플 결과 먼저 체험’ 중 어디에 둘까요?",
      "answer": "내 영상 바로 업로드로 진행해",
      "date": "2026-10-08",
      "source_reference": "docs/planning/codex-planning-d05-prompt.md §1",
      "status": "ANSWERED"
    },
    {
      "target_id": "UI-01",
      "target_revision": 1,
      "asset_id": "ASSET-01",
      "question": "이 시안은 승인하시겠어요, 수정 요청하시겠어요?",
      "answer": "승인할게",
      "date": "2026-10-08",
      "approval_id": "APR-02",
      "source_reference": "2026-10-08 Claude Code 세션 사용자 발화. 직전 안내: 검토 대상은 UI-01_r1 한 장뿐, DIFF(패널 약 4:5·'샘플 데이터' 배지·'내 스윙 기록' 하단 띠) 공개 후 승인/수정 질문",
      "status": "ANSWERED",
      "note": "기존 APR-02를 반영하여 오래된 pending 필드 정합성만 보완; 신규 승인 아님."
    },
    {
      "target_id": "UI-02",
      "target_revision": 2,
      "revision_kind": "structure_revision",
      "preceding_guidance": "UI-02 업로드부터 한 장씩 만들고 승인을 받아요",
      "answer": "1번으로 진행해",
      "date": "2026-10-08",
      "approval_id": "APR-03",
      "source_reference": "docs/planning/codex-planning-d05-ui02-prompt.md §1",
      "status": "ANSWERED"
    },
    {
      "target_id": "UI-02",
      "target_revision": 1,
      "asset_id": "ASSET-02",
      "question": "UI-02 r1 시안을 승인하시겠어요, 수정 요청하시겠어요?",
      "answer": "UI-02 승인하고 5번 2번만 고쳐줘",
      "date": "2026-10-08",
      "approval_id": "APR-04",
      "source_reference": "2026-10-08 Claude Code 세션 사용자 발화. 직전 안내: 검토 대상은 UI-02_r1 한 장, 영상 영역 9:16 대비 약 6% 좁음 공개 후 승인/수정 질문",
      "status": "ANSWERED",
      "note": "이미 존재하는 APR-04에 따라 오래된 pending 설명만 정정. 기존 승인 레코드·파일·해시는 보존."
    },
    {
      "target_id": "UI-03",
      "target_revision": 2,
      "revision_kind": "structure_revision",
      "preceding_guidance": "나머지 화면 시안 생성(P06 계속): UI-02 업로드부터 한 장씩 만들고 승인을 받아요",
      "answer": "1번으로 진행해",
      "date": "2026-10-08",
      "approval_id": "APR-05",
      "source_reference": "docs/planning/codex-planning-d05-ui03-prompt.md §1",
      "status": "ANSWERED"
    }
  ],
  "pending_question_or_null": {
    "target_id": "UI-03",
    "target_revision": 1,
    "structure_revision": 2,
    "asset_id": "ASSET-03",
    "artifact_sha256": "030672914927f0b8778e48c281c8aac303283a89dfdfb8d1f203940e0c95a611",
    "question": "UI-03 r1 시안을 승인하시겠어요, 수정 요청하시겠어요?",
    "options": [
      "승인",
      "수정 요청"
    ],
    "answer": null,
    "approval_scope": "현재 유일한 UI-03 r1 한 장과 공개된 DIFF-01~05만. 사용자 발화 전 UI_IMAGE 승인 생성 금지."
  },
  "active_tasks": [],
  "accepted_result_ids": [
    "TASK-02_D05-01_D05-07_UI-01-r1",
    "TASK-03_D05-01_D05-07_UI-02-r1",
    "TASK-04_D05-01_D05-07_UI-03-r1"
  ],
  "conflicts": [],
  "last_saved_artifact_or_null": "docs/planning/STATE.md",
  "next_action": "UI-03 r1 시안 경로·치수·SHA-256·STATE revision 6/APR-05/ASSET-03·문구/배치/스타일 차이를 보고하고 승인/수정 요청 질문 하나로 중지. 추가 생성·코드 수정·커밋 없음.",
  "issue_summary": {
    "count": 12,
    "ids": [
      "ISSUE-01",
      "ISSUE-02",
      "ISSUE-03",
      "ISSUE-04",
      "ISSUE-05",
      "ISSUE-06",
      "ISSUE-07",
      "ISSUE-08",
      "ISSUE-09",
      "ISSUE-10",
      "ISSUE-11",
      "ISSUE-12"
    ],
    "top_three": [
      "ISSUE-01",
      "ISSUE-02",
      "ISSUE-03"
    ],
    "evidence": "UI_STRUCTURE.md §5"
  },
  "asset_records": [
    {
      "id": "ASSET-01",
      "ui_id": "UI-01",
      "ui_revision": 1,
      "structure_revision": 2,
      "role": "시안",
      "file": "docs/planning/mockups/UI-01_r1.png",
      "format": "PNG",
      "dimensions_px": {
        "width": 1672,
        "height": 941
      },
      "bytes": 1421834,
      "created_by": "Codex 이미지 생성",
      "tool": "image_gen (내장 이미지 생성 도구)",
      "generation_count": 1,
      "date": "2026-10-08",
      "status": "SUPERSEDED",
      "sha256": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
      "approval_id": "APR-02",
      "approval_sha256_or_null": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
      "source_reference": "docs/planning/codex-planning-d05-prompt.md; docs/planning/briefs/UI-01_r1.imagegen.txt",
      "reference_assets": [
        "docs/screenshots/hero.jpg",
        "web/public/images/hero-swing-916.webp"
      ],
      "usage_rights": "사용자가 이번 시안 참고용으로 지정. 기존 캐릭터·이미지의 별도 저작권/라이선스는 미확인.",
      "original_status": "생성 원본과 프로젝트 복사본 모두 보유, SHA-256 일치; 미편집",
      "original_file": "/Users/mose/.codex/generated_images/01a11a48-7bf0-7081-8c31-5e729bc3ea1d/exec-f4c4cb54-2e3d-4ff9-9481-d7a80bc98392.png",
      "text_spec": "docs/planning/briefs/UI-01_r1.md §3",
      "review": "docs/planning/briefs/UI-01_r1_review.md",
      "applies_to": [
        "UI-01"
      ],
      "known_differences": [
        "DIFF-01: 출력은 1672×941, 목표 1440×810과 다름; 근사 16:9",
        "DIFF-02: 오른쪽 패널이 9:16보다 넓음",
        "DIFF-03: 왼쪽 여백·제목 크기가 제안과 다름",
        "DIFF-04: 캐릭터 재표현·옅은 배경 광량 변화"
      ],
      "superseded_by": "ASSET-04 (APR-06)"
    },
    {
      "id": "ASSET-02",
      "ui_id": "UI-02",
      "ui_revision": 1,
      "structure_revision": 2,
      "role": "시안",
      "file": "docs/planning/mockups/UI-02_r1.png",
      "format": "PNG",
      "dimensions_px": {
        "width": 1672,
        "height": 941
      },
      "bytes": 1310073,
      "created_by": "Codex 이미지 생성",
      "tool": "image_gen (내장 이미지 생성 도구)",
      "generation_count": 1,
      "date": "2026-10-08",
      "status": "SUPERSEDED",
      "sha256": "ded31c7b6b7b31e5077f1622415982f83d85ef5845281ff47f1c23ebff3f7b90",
      "approval_id": "APR-04",
      "approval_sha256_or_null": "ded31c7b6b7b31e5077f1622415982f83d85ef5845281ff47f1c23ebff3f7b90",
      "source_reference": "docs/planning/codex-planning-d05-ui02-prompt.md; docs/planning/briefs/UI-02_r1.imagegen.txt",
      "reference_assets": [
        "docs/planning/mockups/UI-01_r1.png"
      ],
      "style_reference_approval_id": "APR-02",
      "style_reference_sha256": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
      "usage_rights": "사용자가 승인 UI-01을 이번 시각 기준으로 지정. 별도 저작권/라이선스 자료는 미확인. 영상 프레임은 익명 골퍼의 생성 예시로 실제 테스트 영상 아님.",
      "original_status": "생성 원본과 프로젝트 복사본 보유, SHA-256 일치; 미편집",
      "original_file": "/Users/mose/.codex/generated_images/01a11a6a-fe50-7a80-92b0-1fb0bc7018fc/exec-9da02ac9-82c7-46df-b65d-d98c20e70ef2.png",
      "text_spec": "docs/planning/briefs/UI-02_r1.md §3",
      "review": "docs/planning/briefs/UI-02_r1_review.md",
      "applies_to": [
        "UI-02"
      ],
      "known_differences": [
        "DIFF-01: 출력 1672×941, 목표 1536×864와 다름; 근사 16:9",
        "DIFF-02: 영상 영역 약 252×477로 9:16보다 약 6% 좁음",
        "DIFF-03: 왼쪽 카드가 상대적으로 넓고 완료 상태가 큼",
        "DIFF-04: 파일 변경 글자가 UI-01 보조 버튼의 라임과 다른 밝은 본문색",
        "DIFF-05: 플레이어 탐색 위치와 예시 표시 시간의 대응 차이"
      ],
      "superseded_by": "ASSET-07 (APR-07)"
    },
    {
      "id": "ASSET-03",
      "ui_id": "UI-03",
      "ui_revision": 1,
      "structure_revision": 2,
      "role": "시안",
      "file": "docs/planning/mockups/UI-03_r1.png",
      "format": "PNG",
      "dimensions_px": {
        "width": 1672,
        "height": 941
      },
      "bytes": 1268542,
      "created_by": "Codex 이미지 생성",
      "tool": "image_gen (내장 이미지 생성 도구)",
      "generation_count": 1,
      "date": "2026-10-08",
      "status": "SUPERSEDED",
      "sha256": "030672914927f0b8778e48c281c8aac303283a89dfdfb8d1f203940e0c95a611",
      "approval_id": null,
      "approval_sha256_or_null": null,
      "source_reference": "docs/planning/codex-planning-d05-ui03-prompt.md; docs/planning/briefs/UI-03_r1.imagegen.txt",
      "reference_assets": [
        "docs/planning/mockups/UI-01_r1.png",
        "docs/planning/mockups/UI-02_r1.png"
      ],
      "style_reference_approval_ids": [
        "APR-02",
        "APR-04"
      ],
      "style_reference_sha256": {
        "UI-01_r1.png": "19ce09af3222d41704edeb5d9441bab48c7cd9f37e55cfffacc28822665af3ea",
        "UI-02_r1.png": "ded31c7b6b7b31e5077f1622415982f83d85ef5845281ff47f1c23ebff3f7b90"
      },
      "reference_delivery": "로컬 PNG를 view_image로 열람하고 시각 언어를 텍스트 프롬프트에 반영. 새 이미지 생성이므로 참조 경로/최근 이미지 개수 도구 인수는 미사용.",
      "usage_rights": "사용자가 승인한 두 시안을 시각 언어 기준으로 지정. 별도 권리 문서·폰트 라이선스 미확인. 개인 영상·사진은 새 시안에 사용하지 않음.",
      "original_status": "생성 원본과 프로젝트 복사본 보유, 바이트·SHA-256 일치; 미편집",
      "original_file": "/Users/mose/.codex/generated_images/01a11a83-1f27-7280-9332-2f86624abe2c/exec-f3fd005f-daca-40ba-bdd2-ffce08892a2a.png",
      "text_spec": "docs/planning/briefs/UI-03_r1.md §3",
      "review": "docs/planning/briefs/UI-03_r1_review.md",
      "applies_to": [
        "UI-03"
      ],
      "known_differences": [
        "DIFF-01: 1672×941, 목표 1536×864와 다름; 근사 16:9",
        "DIFF-02: 표시값 30%이나 막대 채움 약 31.6%, 약 1.6%p 길음",
        "DIFF-03: 비례 환산 목표 대비 패널이 좁고 위에 있으며 세로 간격이 넓음",
        "DIFF-04: 공통 상단 서체·여백·캠 아이콘·로그인/테마 색과 배경·경계 색의 차이",
        "DIFF-05: 완료 단계 글자색과 진행 수치 서체 느낌의 차이"
      ],
      "superseded_by": "ASSET-08 (APR-08)"
    },
    {
      "id": "ASSET-04",
      "ui_id": "UI-01",
      "ui_revision": "2a",
      "role": "승인 시안",
      "file": "docs/planning/mockups/UI-01_r2a.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
      "approval_id": "APR-06",
      "approval_sha256_or_null": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
      "usage_rights": "실사형 인물 생성 이미지 — 구현 시 촬영 사진 또는 권리 확인 이미지로 교체 필요",
      "text_spec": "docs/planning/briefs/UI-01_r2_brief.md"
    },
    {
      "id": "ASSET-05",
      "ui_id": "UI-01",
      "ui_revision": "2b",
      "role": "대안 시안(미채택)",
      "file": "docs/planning/mockups/UI-01_r2b.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성",
      "date": "2026-10-08",
      "status": "NOT_SELECTED",
      "sha256": "ba7a7b9adf5a3469c730a3f47a5c5298c63775cca8609caa0eece62533bac59a",
      "approval_id": null,
      "text_spec": "docs/planning/briefs/UI-01_r2_brief.md"
    },
    {
      "id": "ASSET-06",
      "ui_id": "UI-02",
      "ui_revision": 2,
      "structure_revision": 2,
      "role": "시안 — 승인 UI-01 r2a 시각 언어 재생성",
      "file": "docs/planning/mockups/UI-02_r2.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "CHANGES_REQUESTED",
      "sha256": "fce2fa18f8cfc490aaa9c080fdd00c81780b5869fb2b468745cb535d43d96cd3",
      "approval_id": null,
      "approval_sha256_or_null": null,
      "style_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png"
      ],
      "style_reference_approval_ids": [
        "APR-06"
      ],
      "style_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1"
      },
      "layout_reference_assets": [
        "docs/planning/mockups/UI-02_r1.png"
      ],
      "reference_delivery": "시각 기준 r2a와 레이아웃 참고 r1을 로컬에서 열람 후 텍스트로 구분하여 전달. 새 이미지 생성으로 참조 이미지 인수 미사용.",
      "usage_rights": "사용자 지정 시안을 참고. 새로 생성한 익명 골퍼 실루엣과 이미지 예시 표기; 개인 영상·인물 사진 미사용. 별도 폰트·권리 문서는 미확인.",
      "original_status": "생성 원본·프로젝트 복사본의 바이트와 SHA-256 일치, 미편집",
      "original_file": "/Users/mose/.codex/generated_images/01a11a98-c331-7b51-84de-4a9f414c2331/exec-9c6d8938-d20c-4bcf-a855-3f68d0d7b00e.png",
      "file_size_bytes": 1235882,
      "text_spec": "docs/planning/briefs/UI-02_r2.md §3",
      "generation_prompt": "docs/planning/briefs/UI-02_r2.imagegen.txt",
      "review": "docs/planning/briefs/UI-02_r2_review.md",
      "applies_to": [
        "UI-02"
      ],
      "known_differences": [
        "DIFF-01: 1672×941, 목표 2048×1152와 다르며 엄밀한 16:9 대비 약 0.053% 차이",
        "DIFF-02: 영상 영역 약 308×522, 9:16보다 약 4.6–4.9% 넓음",
        "DIFF-03: 재생 탐색 약 19.6%, 표시 시간 1/8=12.5%보다 약 7.1%p 앞섬",
        "DIFF-04: 제안 대비 왼쪽 카드 확대·오른쪽 축소, 큰 완료 제목과 브랜드, 짙은 로그인 테두리",
        "DIFF-05: 제안색 대비 미세 RGB 변동, 정확한 단색·토큰 동일성 미충족"
      ],
      "change_request": {
        "date": "2026-10-08",
        "statement": "뭔가 좀 아쉬워",
        "selected_changes": [
          "통합 타임라인",
          "감지 근거 시각화",
          "시각 강화"
        ],
        "next": "UI-02 r3"
      },
      "superseded_by": "ASSET-07"
    },
    {
      "id": "ASSET-07",
      "ui_id": "UI-02",
      "ui_revision": 3,
      "structure_revision": 2,
      "role": "시안 — 통합 타임라인·손목 높이 파형·코발트 강조",
      "file": "docs/planning/mockups/UI-02_r3.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
      "approval_id": "APR-07",
      "approval_sha256_or_null": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
      "file_size_bytes": 1555559,
      "generation_count": 2,
      "generation_notes": "r2 편집 1회 후 세로 영상 비율 국소 교정 1회. 최종 1장만 프로젝트 산출물로 저장.",
      "source_reference": "docs/planning/codex-ui02-r3-prompt.md",
      "change_request_source_asset": "ASSET-06",
      "structure_note": "기반 구조 revision 2. 통합 타임라인 배치는 이번 r3 수정 요청에 따른 제안이며 새 구조·이미지 승인 기록은 생성하지 않음.",
      "style_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png"
      ],
      "style_reference_approval_ids": [
        "APR-06"
      ],
      "style_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1"
      },
      "edit_source_assets": [
        "docs/planning/mockups/UI-02_r2.png"
      ],
      "edit_source_sha256": {
        "UI-02_r2.png": "fce2fa18f8cfc490aaa9c080fdd00c81780b5869fb2b468745cb535d43d96cd3"
      },
      "reference_delivery": "두 로컬 PNG 실제 열람 후 1차 도구에 r2 편집 대상·r2a 시각 기준으로 전달. 2차는 1차 결과의 세로 영상 비율만 교정.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b0a-1b15-77e2-9899-3f374b1d4af6/exec-08fc7a02-ef81-4d91-9c72-e171b82ff87d.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·문구 덧그리기 없음.",
      "usage_rights": "사용자가 지정한 시안 참조. 익명 골퍼 실루엣·필름스트립·파형은 합성 예시. 실제 개인 영상 미사용. 별도 폰트·권리 문서는 미확인.",
      "text_spec": "docs/planning/briefs/UI-02_r3.md §3",
      "generation_prompt": "docs/planning/briefs/UI-02_r3.imagegen.txt",
      "review": "docs/planning/briefs/UI-02_r3_review.md",
      "applies_to": [
        "UI-02"
      ],
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 1920×1080과 다름. 엄밀한 16:9 대비 약 0.053% 차이.",
        "DIFF-02: 교정 후 영상 약 206×365로 9:16 근사(비율 약 0.33% 차이). 정확한 내부 CSS 규격은 미검증.",
        "DIFF-03: r2a와 메뉴 구조·색 역할은 유지하지만 브랜드 크기·로그인 경계 등 시각 수치 및 제안 배치와 차이.",
        "DIFF-04: 파형과 필름스트립은 합성 예시로 프레임별 손목 높이 일치를 보장하지 않음. 실제 감지 데이터 연결 필요."
      ],
      "signal_evidence": [
        "golf_swing_analyzer/analyzer/pipeline.py:auto_detect_swing_window",
        "web/src/components/Waveform.tsx",
        "server/main.py:/auto-window",
        "web/src/lib/types.ts:AutoWindowResponse"
      ],
      "implementation_limit": "자동 감지는 양손 평균 Y를 사용하지만 현행 /auto-window는 시작·끝만 반환. 원본 시간축 파형과 성공/전체반환 사유 연결은 미구현."
    },
    {
      "id": "ASSET-08",
      "ui_id": "UI-03",
      "ui_revision": 2,
      "structure_revision": 2,
      "role": "시안 — 새 코발트 시각 언어의 분석 진행 중 상태",
      "file": "docs/planning/mockups/UI-03_r2.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
      "approval_id": "APR-08",
      "approval_sha256_or_null": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
      "file_size_bytes": 1166717,
      "generation_count": 1,
      "generation_notes": "UI-03 r1의 구조·문구만 유지하는 시각 재생성 편집 1회. r3·r2a는 시각/상단 참고. 추가 교정 없음.",
      "source_reference": "docs/planning/codex-ui03-r2-prompt.md",
      "structure_approval_id": "APR-05",
      "style_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png"
      ],
      "style_reference_approval_ids": [
        "APR-06",
        "APR-07"
      ],
      "style_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138"
      },
      "edit_source_assets": [
        "docs/planning/mockups/UI-03_r1.png"
      ],
      "edit_source_sha256": {
        "UI-03_r1.png": "030672914927f0b8778e48c281c8aac303283a89dfdfb8d1f203940e0c95a611"
      },
      "reference_delivery": "3개 로컬 PNG 실제 열람 후 내장 도구에 r1(구조·문구 편집 대상), r3(시각 기준), r2a(상단 기준) 순으로 전달. r1의 색·형태는 교체하고 인물은 제외.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b16-34b4-75b3-b2d6-21ebf3e0aa93/exec-a2585d60-0d11-42a3-8f42-bb510267a8d2.png",
      "original_status": "생성 원본과 프로젝트 PNG 바이트·SHA-256 일치. 크롭·리사이즈·문구 덧그리기 없음.",
      "text_spec": "docs/planning/briefs/UI-03_r2.md §3",
      "generation_prompt": "docs/planning/briefs/UI-03_r2.imagegen.txt",
      "review": "docs/planning/briefs/UI-03_r2_review.md",
      "applies_to": [
        "UI-03"
      ],
      "representative_state": {
        "stage": "analyzing",
        "progress": 30,
        "filename": "일반.mp4",
        "data_kind": "단계 기준 합성 예시"
      },
      "known_differences": [
        "DIFF-01: 실제 1672×941로 목표 1920×1080과 다름. 엄밀한 16:9 대비 약 0.053% 차이.",
        "DIFF-02: 막대 채움 약 30.5~30.6%, 표시값 30%보다 약 0.5~0.6%p 길다.",
        "DIFF-03: 뒤로 가기 외곽선은 있으나 브리프의 흰 간격을 둔 별도 초점 외곽선은 명확히 표현되지 않음.",
        "DIFF-04: 중앙 영역은 약 1071px로 비례 목표 약 1010px보다 넓고, 진행 숫자는 비례 목표보다 작음. 현재 단계 가운뎃점 주변 시각적 간격·상단 글자 크기도 참조와 차이."
      ],
      "implementation_limit": "파일명·뒤로 가기·이탈 응답 무효화·진행률 이름 연결은 기존 개선 제안. 실제 브라우저·API·접근성 시험 및 코드 구현 없음.",
      "change_request": {
        "date": "2026-10-08",
        "statement": "이 느낌도 좀 살렸으면좋겠어 (UI-03 r1 이미지 첨부)",
        "decision": "DEC-02"
      },
      "change_request_resolved": "DEC-03로 원안 채택"
    },
    {
      "id": "ASSET-09",
      "ui_id": "UI-01",
      "ui_revision": 3,
      "structure_revision": 2,
      "role": "시안 — 흰 배경 유지·짙은 초록/라임 강조색 변경",
      "file": "docs/planning/mockups/UI-01_r3.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "NOT_SELECTED",
      "sha256": "b9d0b61bac032e0c35ccc34c89321c68a6725c93fd36b9c217be6ccd5adba7ff",
      "approval_id": null,
      "approval_sha256_or_null": null,
      "file_size_bytes": 1614429,
      "generation_count": 2,
      "generation_notes": "색/일러스트 편집 1회 + EN 대비 국소 교정 1회",
      "source_reference": "docs/planning/codex-accent-lime-prompt.md",
      "decision_id": "DEC-02",
      "edit_source_asset_id": "ASSET-04",
      "edit_source_assets": [
        "docs/planning/mockups/UI-01_r2a.png"
      ],
      "edit_source_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1"
      },
      "layout_reference_approval_id": "APR-06",
      "color_reference_assets": [
        "docs/planning/mockups/UI-03_r1.png"
      ],
      "reference_delivery": "편집 대상·UI-03 r1 색 느낌을 실제 열람 후 순서대로 전달. r1 다크 배경/배치 제외. 2차는 해당 1차 결과만 국소 교정.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b32-2dde-70a0-9bd8-d9e6f37b5968/exec-5a82f68b-e291-4f2f-ae2f-cce1c0005f3d.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/accent-lime_brief.md",
      "generation_prompt": "docs/planning/briefs/accent-lime.imagegen.txt",
      "review": "docs/planning/briefs/accent-lime_review.md",
      "applies_to": [
        "UI-01"
      ],
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 2048×1152와 다름. 엄밀한 16:9 대비 약 0.053% 차이.",
        "DIFF-02: 명시 HEX와 실제 PNG 대표색에 편차·미세 명암이 있음.",
        "DIFF-04: 큰 배치/위계는 보존, 글자 가장자리·선 굵기 등은 재생성 편차가 있음."
      ],
      "implementation_limit": "정적 시안만 생성. 실동작·브라우저·키보드·보조기술 적합성·코드 구현 미검증.",
      "usage_rights": "사용자 지정 기존 시안 참조. UI-01 일러스트와 UI-02 영상/파형은 합성 예시. 별도 외부 인물 사진 추가 없음.",
      "reason": "DEC-03"
    },
    {
      "id": "ASSET-10",
      "ui_id": "UI-02",
      "ui_revision": 4,
      "structure_revision": 2,
      "role": "시안 — 흰 배경 유지·짙은 초록/라임 강조색 변경",
      "file": "docs/planning/mockups/UI-02_r4.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "NOT_SELECTED",
      "sha256": "513faf7121d072ba37dbd6420247ffa6ee1fba20cac13bc8e49df823c8813c52",
      "approval_id": null,
      "approval_sha256_or_null": null,
      "file_size_bytes": 1551031,
      "generation_count": 2,
      "generation_notes": "색/오타 편집 1회 + 감지 라벨 자간·체크 색 국소 교정 1회",
      "source_reference": "docs/planning/codex-accent-lime-prompt.md",
      "decision_id": "DEC-02",
      "edit_source_asset_id": "ASSET-07",
      "edit_source_assets": [
        "docs/planning/mockups/UI-02_r3.png"
      ],
      "edit_source_sha256": {
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138"
      },
      "layout_reference_approval_id": "APR-07",
      "color_reference_assets": [
        "docs/planning/mockups/UI-03_r1.png"
      ],
      "reference_delivery": "편집 대상·UI-03 r1 색 느낌을 실제 열람 후 순서대로 전달. r1 다크 배경/배치 제외. 2차는 해당 1차 결과만 국소 교정.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b32-2dde-70a0-9bd8-d9e6f37b5968/exec-031a0fa5-fc7b-4be9-816e-206874a15136.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/accent-lime_brief.md",
      "generation_prompt": "docs/planning/briefs/accent-lime.imagegen.txt",
      "review": "docs/planning/briefs/accent-lime_review.md",
      "applies_to": [
        "UI-02"
      ],
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 2048×1152와 다름. 엄밀한 16:9 대비 약 0.053% 차이.",
        "DIFF-02: 명시 HEX와 실제 PNG 대표색에 편차·미세 명암이 있음.",
        "DIFF-04: 큰 배치/위계는 보존, 글자 가장자리·선 굵기 등은 재생성 편차가 있음.",
        "DIFF-05: 비조작 영상/타임라인 장식선은 연한 녹색으로 남음; 핵심 조작 경계·파형·초점선은 짙게 구별."
      ],
      "implementation_limit": "정적 시안만 생성. 실동작·브라우저·키보드·보조기술 적합성·코드 구현 미검증.",
      "usage_rights": "사용자 지정 기존 시안 참조. UI-01 일러스트와 UI-02 영상/파형은 합성 예시. 별도 외부 인물 사진 추가 없음.",
      "text_correction": {
        "from": "잔목 감지 구간",
        "to": "자동 감지 구간",
        "source": "STATE.md text_corrections"
      },
      "reason": "DEC-03"
    },
    {
      "id": "ASSET-11",
      "ui_id": "UI-03",
      "ui_revision": 3,
      "structure_revision": 2,
      "role": "시안 — 흰 배경 유지·짙은 초록/라임 강조색 변경",
      "file": "docs/planning/mockups/UI-03_r3.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "NOT_SELECTED",
      "sha256": "c9850e0fb36cc21d8324df4587e40f9ad48e5a4b3903c6ea6d893298b436b9dc",
      "approval_id": null,
      "approval_sha256_or_null": null,
      "file_size_bytes": 1477039,
      "generation_count": 2,
      "generation_notes": "색/초점선 편집 1회 + 트랙·EN 대비 국소 교정 1회",
      "source_reference": "docs/planning/codex-accent-lime-prompt.md",
      "decision_id": "DEC-02",
      "edit_source_asset_id": "ASSET-08",
      "edit_source_assets": [
        "docs/planning/mockups/UI-03_r2.png"
      ],
      "edit_source_sha256": {
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10"
      },
      "layout_reference_approval_id": null,
      "color_reference_assets": [
        "docs/planning/mockups/UI-03_r1.png"
      ],
      "reference_delivery": "편집 대상·UI-03 r1 색 느낌을 실제 열람 후 순서대로 전달. r1 다크 배경/배치 제외. 2차는 해당 1차 결과만 국소 교정.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b32-2dde-70a0-9bd8-d9e6f37b5968/exec-61b4ff9d-7495-4677-a570-d788375c407a.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/accent-lime_brief.md",
      "generation_prompt": "docs/planning/briefs/accent-lime.imagegen.txt",
      "review": "docs/planning/briefs/accent-lime_review.md",
      "applies_to": [
        "UI-03"
      ],
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 2048×1152와 다름. 엄밀한 16:9 대비 약 0.053% 차이.",
        "DIFF-02: 명시 HEX와 실제 PNG 대표색에 편차·미세 명암이 있음.",
        "DIFF-04: 큰 배치/위계는 보존, 글자 가장자리·선 굵기 등은 재생성 편차가 있음.",
        "DIFF-03: 진행 막대 채움 약 30.553%, 표시 30%보다 약 0.55%p 길음."
      ],
      "implementation_limit": "정적 시안만 생성. 실동작·브라우저·키보드·보조기술 적합성·코드 구현 미검증.",
      "usage_rights": "사용자 지정 기존 시안 참조. UI-01 일러스트와 UI-02 영상/파형은 합성 예시. 별도 외부 인물 사진 추가 없음.",
      "representative_state": {
        "stage": "analyzing",
        "progress": 30,
        "filename": "일반.mp4",
        "data_kind": "단계 기준 합성 예시"
      },
      "reason": "DEC-03"
    },
    {
      "id": "ASSET-12",
      "ui_id": "UI-04",
      "ui_revision": 1,
      "structure_revision": 1,
      "role": "시안 — 코발트 결과 화면 첫 뷰포트",
      "file": "docs/planning/mockups/UI-04_r1.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
      "approval_id": "APR-10",
      "approval_sha256_or_null": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
      "structure_approval_id": "APR-09",
      "file_size_bytes": 1619972,
      "generation_count": 2,
      "generation_notes": "신규 생성 1회 + 진단 warning/good 글자 국소 교정 1회. 최종 산출물 한 장.",
      "source_reference": "docs/planning/codex-ui04-prompt.md",
      "decision_id": "DEC-03",
      "visual_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png",
        "docs/planning/mockups/UI-03_r2.png"
      ],
      "visual_reference_approval_ids": [
        "APR-06",
        "APR-07",
        "APR-08"
      ],
      "visual_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10"
      },
      "reference_delivery": "승인 PNG 3개 실제 열람 후 텍스트로 시각 특징을 명시해 신규 생성. 2차는 첫 생성 PNG만 편집 참조로 전달.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b43-1712-7ec1-9df6-7526bd91808c/exec-9819e0ac-fb3c-4fd0-9b31-b3faa535898a.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/UI-04_r1.md",
      "generation_prompt": "docs/planning/briefs/UI-04_r1.imagegen.txt",
      "review": "docs/planning/briefs/UI-04_r1_review.md",
      "applies_to": [
        "UI-04"
      ],
      "representative_state": {
        "source": "새 분석",
        "logged_in": false,
        "saved": false,
        "filename": "일반.mp4",
        "score": 73,
        "grade": "B",
        "phases_detected": 7,
        "data_kind": "현행 기본 채점·표시 경계와 대조한 합성 예시"
      },
      "known_differences": [
        "DIFF-01: 1672×941, 목표 2048×1152와 다름. 정확한 16:9 대비 약 0.0531% 차이.",
        "DIFF-02: 척추/X-Factor 숫자는 남색, 상태 기호만 주황/빨강. warning은 목표보다 밝음. 색·대비 미검증.",
        "DIFF-03: 점수 면 약 21%와 연속 지표 띠 등 생성 배치 편차. 첫 화면에 요구 영역 모두 표시.",
        "DIFF-04: 진단 2행 어깨-골반의 연결 기호가 가운데점처럼 보여 하이픈 원문 구별 불명확."
      ],
      "implementation_limit": "정적 시안. 하단 기능·저장/공유 상태는 브리프 표만 작성. 실제 기능·브라우저·접근성·코드 구현 미검증. X-Factor P5 미적용.",
      "usage_rights": "새 합성 골퍼 실루엣과 이미지 예시 표시. 기존 승인 이미지는 시각 열람 참고, 외부 인물 사진·실제 분석 프레임 사용 없음."
    },
    {
      "id": "ASSET-13",
      "ui_id": "UI-05",
      "ui_revision": 1,
      "structure_revision": 1,
      "role": "시안 — 코발트 실시간 캠 촬영 중 대표 상태",
      "file": "docs/planning/mockups/UI-05_r1.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588",
      "approval_id": "APR-12",
      "approval_sha256_or_null": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588",
      "structure_approval_id": "APR-11",
      "file_size_bytes": 1365732,
      "generation_count": 1,
      "generation_notes": "내장 image_gen 신규 생성 1회. 최종 산출물 한 장. 코드 이미지 편집 없음.",
      "source_reference": "docs/planning/codex-ui05-prompt.md",
      "decision_id": "DEC-03",
      "visual_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png",
        "docs/planning/mockups/UI-03_r2.png",
        "docs/planning/mockups/UI-04_r1.png"
      ],
      "visual_reference_approval_ids": [
        "APR-06",
        "APR-07",
        "APR-08",
        "APR-10"
      ],
      "visual_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
        "UI-04_r1.png": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd"
      },
      "reference_delivery": "승인 PNG 4개 실제 열람 후 텍스트로 시각 특징 전달. 신규 생성 호출에 이미지 참조 인자 없음.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b5e-32ca-7d93-a26f-808a826cb92d/exec-8f514eff-b658-4760-874f-ca58d04d46ce.png",
      "original_status": "도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/UI-05_r1.md",
      "generation_prompt": "docs/planning/briefs/UI-05_r1.imagegen.txt",
      "review": "docs/planning/briefs/UI-05_r1_review.md",
      "applies_to": [
        "UI-05"
      ],
      "representative_state": {
        "phase": "capturing",
        "lang": "ko",
        "logged_in": false,
        "recording_available": true,
        "pose_visible": true,
        "preparation_checks": "사용자가 직접 확인한 준비 항목의 합성 상태",
        "data_kind": "합성 일러스트·예시 수치, 실제 카메라 분석 아님",
        "angles": {
          "spine": 32.4,
          "shoulderRotation": 18,
          "hipRotation": 9
        }
      },
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 2048×1152와 다름. 정확한 16:9 대비 약 0.0531% 차이.",
        "DIFF-02: 카메라 외곽 약 936×688(약 1.36:1), 목표 4:3보다 넓음. 오른쪽 상태 면의 시작 높이도 생성 배치 편차.",
        "DIFF-03: 높은 백스윙 자세로 생성됨. 팔·어깨 부근 점이 겹쳐 보여 실제 12개 관절/12개 연결의 1:1 재현을 확인할 수 없는 도식. 각도는 일러스트 측정값 아님."
      ],
      "implementation_limit": "정적 촬영 중 시안. 준비 체크·한글 HUD·인식/녹화 표시·원인별 복구는 제안. 실제 카메라·모델·녹화·서버·브라우저·접근성 동작 미검증.",
      "usage_rights": "새 합성 골퍼 일러스트에 이미지 예시 표시, HUD에 예시 수치 표시. 외부 인물 사진·실제 분석 프레임 사용 없음."
    },
    {
      "id": "ASSET-14",
      "ui_id": "UI-06",
      "ui_revision": 1,
      "structure_revision": 1,
      "role": "시안 — 코발트 내 기록·성장 추이·대상 명시 삭제 확인",
      "file": "docs/planning/mockups/UI-06_r1.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 940
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "cbc1b41691e3f48d1c448ddc8ad4e05370802a846184ef18eea7a08fe98e6af6",
      "approval_id": "APR-16",
      "approval_sha256_or_null": "cbc1b41691e3f48d1c448ddc8ad4e05370802a846184ef18eea7a08fe98e6af6",
      "structure_approval_id": "APR-13",
      "file_size_bytes": 1221256,
      "generation_count": 1,
      "generation_notes": "내장 image_gen 신규 생성 1회. 최종 한 장.",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md",
      "decision_id": "DEC-03",
      "visual_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png",
        "docs/planning/mockups/UI-03_r2.png",
        "docs/planning/mockups/UI-04_r1.png",
        "docs/planning/mockups/UI-05_r1.png"
      ],
      "visual_reference_approval_ids": [
        "APR-06",
        "APR-07",
        "APR-08",
        "APR-10",
        "APR-12"
      ],
      "visual_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
        "UI-04_r1.png": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
        "UI-05_r1.png": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588"
      },
      "reference_delivery": "승인 PNG 5장을 실제 열람 후 시각 특징을 텍스트로 전달. UI-07 교정에는 첫 생성 결과만 편집 참조로 전달.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b6c-aa03-7973-a692-c0463fafd704/exec-97cb1bd3-7007-4336-9aa3-bd7685e160b1.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/UI-06_r1.md",
      "generation_prompt": "docs/planning/briefs/UI-06_r1.imagegen.txt",
      "review": "docs/planning/briefs/UI-06_r1_review.md",
      "applies_to": [
        "UI-06"
      ],
      "representative_state": {
        "logged_in": true,
        "lang": "ko",
        "record_count": 4,
        "inline_delete_target": "스윙_0928.mp4",
        "data_kind": "합성 예시 데이터",
        "chronological_scores": [
          73,
          79,
          77,
          81
        ]
      },
      "known_differences": [
        "DIFF-01: 실제 1672×940, 목표 2048×1152와 다름. 정확한 16:9 대비 0.0532% 차이. 도구 원본 보존.",
        "DIFF-02: 하단 회원 탈퇴 문구가 작고 옅음. 정확한 대비·키보드 접근 미검증.",
        "DIFF-03: 그래프 텍스트·순서·방향 대조, 픽셀 좌표의 정량 정확성 미인증."
      ],
      "implementation_limit": "정적 시안과 상태별 브리프. 실제 앱·서버·키보드·보조기술·복구 동작은 미구현/미검증. 코드 수정 없음.",
      "usage_rights": "UI-07 인물은 합성 실루엣·이미지 예시 표시. UI-06은 예시 데이터 표시. 외부 인물 사진·실제 사용자 기록 사용 없음."
    },
    {
      "id": "ASSET-15",
      "ui_id": "UI-07",
      "ui_revision": 1,
      "structure_revision": 1,
      "role": "시안 — 코발트 첫 화면 위 로그인 모달·이메일 초점",
      "file": "docs/planning/mockups/UI-07_r1.png",
      "format": "PNG",
      "dimensions": {
        "width": 1671,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "997e9ed917aee50d2c222e64d4b5103f8294727a84f0a2786c7a66d2dffc5c28",
      "approval_id": "APR-17",
      "approval_sha256_or_null": "997e9ed917aee50d2c222e64d4b5103f8294727a84f0a2786c7a66d2dffc5c28",
      "structure_approval_id": "APR-14",
      "file_size_bytes": 1504531,
      "generation_count": 2,
      "generation_notes": "신규 생성 1회 + 배경 한정 교정 1회. 최종 한 장.",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md",
      "decision_id": "DEC-03",
      "visual_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png",
        "docs/planning/mockups/UI-03_r2.png",
        "docs/planning/mockups/UI-04_r1.png",
        "docs/planning/mockups/UI-05_r1.png"
      ],
      "visual_reference_approval_ids": [
        "APR-06",
        "APR-07",
        "APR-08",
        "APR-10",
        "APR-12"
      ],
      "visual_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
        "UI-04_r1.png": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
        "UI-05_r1.png": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588"
      },
      "reference_delivery": "승인 PNG 5장을 실제 열람 후 시각 특징을 텍스트로 전달. UI-07 교정에는 첫 생성 결과만 편집 참조로 전달.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b6c-aa03-7973-a692-c0463fafd704/exec-bf6de9c5-4a6b-4a63-8513-b3b0a6bb09c2.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/UI-07_r1.md",
      "generation_prompt": "docs/planning/briefs/UI-07_r1.imagegen.txt",
      "review": "docs/planning/briefs/UI-07_r1_review.md",
      "applies_to": [
        "UI-07"
      ],
      "representative_state": {
        "logged_in": false,
        "lang": "ko",
        "mode": "login",
        "background": "UI-01 첫 화면",
        "focused_field": "email",
        "inputs": "빈 값",
        "data_kind": "합성 실루엣·이미지 예시"
      },
      "known_differences": [
        "DIFF-01: 실제 1671×941, 목표 2048×1152와 다름. 정확한 16:9 대비 0.1129% 차이. 도구 원본 보존.",
        "DIFF-02: 모달 비율·배경 재구성·버튼 화살표 등 생성 배치 편차.",
        "DIFF-03: 이메일 코발트 초점 경계는 보이나 요청한 흰 간격이 완전히 분리되지는 않음. 실제 focus 동작 미검증."
      ],
      "implementation_limit": "정적 시안과 상태별 브리프. 실제 앱·서버·키보드·보조기술·복구 동작은 미구현/미검증. 코드 수정 없음.",
      "usage_rights": "UI-07 인물은 합성 실루엣·이미지 예시 표시. UI-06은 예시 데이터 표시. 외부 인물 사진·실제 사용자 기록 사용 없음."
    },
    {
      "id": "ASSET-16",
      "ui_id": "UI-08",
      "ui_revision": 1,
      "structure_revision": 1,
      "role": "시안 — 코발트 개인정보처리방침·원문 목차와 첫 뷰포트",
      "file": "docs/planning/mockups/UI-08_r1.png",
      "format": "PNG",
      "dimensions": {
        "width": 1672,
        "height": 941
      },
      "created_by": "Codex 이미지 생성 / 내장 image_gen",
      "date": "2026-10-08",
      "status": "APPROVED",
      "sha256": "400ac67ea96ea60700e3bd63138c37cac74144e9f48877b1cc5500fd939420c0",
      "approval_id": "APR-18",
      "approval_sha256_or_null": "400ac67ea96ea60700e3bd63138c37cac74144e9f48877b1cc5500fd939420c0",
      "structure_approval_id": "APR-15",
      "file_size_bytes": 1234685,
      "generation_count": 1,
      "generation_notes": "내장 image_gen 신규 생성 1회. 최종 한 장.",
      "source_reference": "docs/planning/codex-ui06-08-prompt.md",
      "decision_id": "DEC-03",
      "visual_reference_assets": [
        "docs/planning/mockups/UI-01_r2a.png",
        "docs/planning/mockups/UI-02_r3.png",
        "docs/planning/mockups/UI-03_r2.png",
        "docs/planning/mockups/UI-04_r1.png",
        "docs/planning/mockups/UI-05_r1.png"
      ],
      "visual_reference_approval_ids": [
        "APR-06",
        "APR-07",
        "APR-08",
        "APR-10",
        "APR-12"
      ],
      "visual_reference_sha256": {
        "UI-01_r2a.png": "0d05d1dd7397c94210be427c1aaa28c2e7145fc99f3b3c4212a045e56c6ab0e1",
        "UI-02_r3.png": "cb5cbc69bae10fe630b77dbffcb600ca226bc54924d2bce0b96a85382709e138",
        "UI-03_r2.png": "53f14a57a10fc4f5b855d3fea1f5197d2357fa9a661b645eb14907c638ed1f10",
        "UI-04_r1.png": "be3ca53e72aa532bc0150fad790d268ff8231989cda82e74da7e441f12f75acd",
        "UI-05_r1.png": "2c70a0ce5145aa009212213fdd81573f8f8d983cc6808e7de1092ed466f38588"
      },
      "reference_delivery": "승인 PNG 5장을 실제 열람 후 시각 특징을 텍스트로 전달. UI-07 교정에는 첫 생성 결과만 편집 참조로 전달.",
      "original_file": "/Users/mose/.codex/generated_images/01a11b6c-aa03-7973-a692-c0463fafd704/exec-66a3b74c-3af1-4fcb-8154-8f495daef905.png",
      "original_status": "최종 도구 원본과 프로젝트 PNG 바이트·SHA-256 일치. 코드 크롭·리사이즈·텍스트 합성 없음.",
      "text_spec": "docs/planning/briefs/UI-08_r1.md",
      "generation_prompt": "docs/planning/briefs/UI-08_r1.imagegen.txt",
      "review": "docs/planning/briefs/UI-08_r1_review.md",
      "applies_to": [
        "UI-08"
      ],
      "representative_state": {
        "lang": "ko",
        "public": true,
        "entry": "UI-02",
        "scroll": "top",
        "active_section": 1,
        "source": "47157d8:개인정보처리방침.md",
        "policy_version": "2026-07-10",
        "visible_sections": "1·2절 본문, 3절 제목, 1–6절 목차"
      },
      "known_differences": [
        "DIFF-01: 실제 1672×941, 목표 2048×1152와 다름. 정확한 16:9 대비 0.0531% 차이. 도구 원본 보존.",
        "DIFF-02: 현재 앱의 5항목과 달리 삭제 전 루트 원문의 6항목명·순서를 사용. 원문 내부 코드 경로·알고리즘 식별자 제외.",
        "DIFF-03: 긴 문서의 첫 뷰포트로 3절 본문·4–6절 본문은 화면 아래. 업로드 초안 보존은 브리프 전용 제안."
      ],
      "implementation_limit": "정적 시안과 상태별 브리프. 실제 앱·서버·키보드·보조기술·복구 동작은 미구현/미검증. 코드 수정 없음.",
      "usage_rights": "UI-07 인물은 합성 실루엣·이미지 예시 표시. UI-06은 예시 데이터 표시. 외부 인물 사진·실제 사용자 기록 사용 없음.",
      "policy_source_sha256": "964ed9b79ee544d926ddd8c7775db117f663ceb30644f3a14b2ab6b69dc653a2",
      "policy_source_note": "현재 루트 파일 없음. 삭제 전 Git 원문 전체를 읽어 사용. 현재 앱 5항목과의 차이 및 미결 항목은 브리프에 공개."
    }
  ],
  "approval_note": "APR-01=UI-01 구조 2, APR-02=UI-01 r1 이미지, APR-03=UI-02 구조 2, APR-04=UI-02 r1 이미지, APR-05=UI-03 구조 2 및 생성 요청. 기존 승인·파일·해시 보존. ASSET-03 GENERATED, UI-03 이미지 승인 ID/승인 당시 해시 null. 새 이미지 승인은 생성하지 않았다.",
  "source_instructions": [
    "docs/planning/codex-planning-agents-prompt.md",
    "Planning_Agents_v3.0/PROJECT_INSTRUCTIONS.txt",
    "Planning_Agents_v3.0/01_PROJECT_MD/00_ORCHESTRATOR.md",
    "Planning_Agents_v3.0/01_PROJECT_MD/90_SHARED_CONTRACTS.md",
    "Planning_Agents_v3.0/01_PROJECT_MD/04_UX_STRUCTURE.md",
    "Planning_Agents_v3.0/01_PROJECT_MD/05_VISUAL_APPROVAL.md",
    "Planning_Agents_v3.0/01_PROJECT_MD/06_WEB.md",
    "CLAUDE.md",
    "/Users/mose/.codex/skills/golf-ui-ux/SKILL.md",
    "docs/planning/codex-planning-d05-prompt.md",
    "/Users/mose/.codex/skills/.system/imagegen/SKILL.md",
    "docs/planning/codex-planning-d05-ui02-prompt.md",
    "docs/planning/codex-planning-d05-ui03-prompt.md"
  ],
  "text_corrections": [
    {
      "ui_id": "UI-02",
      "asset_id": "ASSET-07",
      "image_text": "잔목 감지 구간",
      "correct_text": "자동 감지 구간",
      "date": "2026-10-08"
    }
  ],
  "implementation_notes": [
    {
      "ui_id": "UI-04",
      "note": "지표 카드 상태(status.ts)와 진단 목록 판정(scoring) 기준 불일치 — 예: X-Factor 카드 ✕, 진단 warning. 구현 전 기준 통일 결정 필요",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-04",
      "note": "진단 등급 라벨 warning/good 영어 노출 — KO 번역(주의/양호 등) i18n 필요",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-03",
      "note": "뒤로 가기 버튼 초점선 명확화(APR-08 메모)",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-02",
      "note": "이미지 '잔목 감지 구간' → '자동 감지 구간'(text_corrections)",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-01",
      "note": "r2a 실사형 인물 이미지는 촬영 사진 또는 권리 확인 이미지로 교체",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-05",
      "note": "촬영 준비 '머리부터 발끝까지 화면 안'은 관절 인식으로 자동 확인 가능 — 수동 체크 대신 자동 표시 검토",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-04/UI-05",
      "note": "지표 명칭 일관성: UI-05는 '어깨선·골반선 기울기'(측정 실체와 일치, docs/research 03 RQ5). UI-04 '어깨 최대 회전' 등 '회전' 표현 통일 여부 결정 필요",
      "date": "2026-10-08"
    },
    {
      "ui_id": "UI-08",
      "note": "루트 개인정보처리방침.md는 705f6f2에서 삭제됨(CLAUDE.md는 여전히 PrivacyPolicy.tsx와 짝으로 기술). 시안은 삭제 전 원문 기반 — 구현 기준은 현행 web/src/components/PrivacyPolicy.tsx 문구. '시행일: 서비스 정식 오픈일'은 자리표시 문구",
      "date": "2026-10-08"
    }
  ]
}
```

[UI-03 브리프](briefs/UI-03_r1.md) · [시안](mockups/UI-03_r1.png) · [D05-06 대조](briefs/UI-03_r1_review.md) · [실제 도구 입력](briefs/UI-03_r1.imagegen.txt). UI-01·02 기존 승인·자산을 보존했다. [UI_STRUCTURE.md](UI_STRUCTURE.md)는 D04 최초 기록이며 활성 UI-01·02·03 구조 revision 2는 각 브리프를 따른다. UI-03은 생성 성공과 시각 요건 충족을 구별한다. 실제 브라우저·기기·접근성·이탈 처리 동작은 미검증이다.
