# 03 · 취합 리뷰 — 골프 스윙 역학·단계 인식 (Claude + Codex)

취합 2026-10-08 · 취합자 Claude · 입력 `01_claude_findings.md`(Claude, 33편) + `02_codex_findings.md`(Codex, 26편, Claude 파일 미열람 확인)

## 0. 읽는 법
- 출처 ID: **K-nn** = Claude 조사 ID(`01`의 C-nn), **X-nn** = Codex 조사 ID(`02`의 C-nn). 같은 논문이면 둘 다 적는다
- 발견 표시: `양쪽 발견` / `Claude만` / `Codex만`
- 확인 수준은 두 조사 중 **더 깊은 쪽**(본문 > 초록 > 서지만)
- 검증: DOI 42개 전부 doi.org 등록 확인(실패 0), Codex DOI 20개는 Crossref 제목 일치 1.00, DOI 없는 6편은 URL 열림 확인. 수치 표본 검사 1건(X26 Smith 2016 −16.72 ± 6.20°, 15명, 핸디캡 1–29) 원문 PDF와 일치
- **검증 실패: 0건.** 단 `서지만 확인` 출처는 수치 근거로 쓰지 않는다

## 1. 출처 전체 목록 (중복 제거 47편)
| 출처 | 연도 | 발견 | 확인 수준 | RQ |
|---|---|---|---|---|
| Tinmark 외, Sports Biomech 9(4) — K01/X01 | 2010 | 양쪽 | 초록 | 1 |
| Meister 외, J Appl Biomech 27(3) — K06/X03 | 2011 | 양쪽 | 초록 | 1,2,3 |
| Myers 외, J Sports Sci 26(2) — K10/X11 | 2008 | 양쪽 | 초록 | 2,3 |
| Kwon 외, Sports Biomech 12(3) — K18/X12 | 2013 | 양쪽 | 초록 | 3,5 |
| Chu 외, J Sports Sci 28(11) — K16/X13 | 2010 | 양쪽 | 초록 | 3 |
| Han 외, Sports Biomech 18(2) (지면 상호작용) — K14/X14 | 2019 | 양쪽 | 초록 | 3 |
| Nesbit & Serrano, JSSM 4 — K12/X16 | 2005 | 양쪽 | 본문 | 3 |
| Kim & Park, Sensors 20 — K25/X18 | 2020 | 양쪽 | 본문 | 4 |
| Kim & Park, Sci Rep 14 — K26/X19 | 2024 | 양쪽 | 본문 | 4 |
| McNally 외, GolfDB, CVPRW — K24/X22 | 2019 | 양쪽 | 본문 | 4,6 |
| Lee 외, GolfPose, ICPR — K34/X23 | 2024 | 양쪽 | 본문(X) | 5,6 |
| Smith 외, J Appl Biomech 32(1) — K29/X26 | 2016 | 양쪽 | 본문(X) | 3,5 |
| Han 외, Sports Biomech 18(6) (분리 스타일과 연쇄) — X02 | 2019 | Codex만 | 초록 | 1,2 |
| Zheng 외, Int J Sports Med 29(6) — X04 | 2008 | Codex만 | 초록 | 1 |
| Sim 외, J Mot Behav 49(6) (골반-흉곽 협응) — X05 | 2017 | Codex만 | 초록 | 1,2 |
| Marsan 외, Acta Bioeng Biomech 21(2) — X06 | 2019 | Codex만 | 본문 | 1 |
| Beak 외, BioMed Eng OnLine 12 — X07 | 2013 | Codex만 | 본문 | 2 |
| Gryc 외, Sports 11(3) — X08 | 2023 | Codex만 | 본문 | 2,3,4 |
| Okuda 외, JSSM 9(1) — X09 | 2010 | Codex만 | 본문 | 2,3 |
| Parker 외, BMC Sports Sci Med Rehabil 9 — X10 | 2017 | Codex만 | 본문 | 1,2,3 |
| Nesbit, JSSM 4 (3D 운동학·운동역학) — X15 | 2005 | Codex만 | 초록 | 3 |
| Kim 외, Sensors 23 (IMU 회전 검증) — X17 | 2023 | Codex만 | 본문 | 4,5 |
| Yamamoto 외, Front Sports Act Living 5 (단안 영상) — X20 | 2023 | Codex만 | 본문 | 4,5 |
| Menychtas 외, Front Rehabil Sci 4 (보행, MediaPipe) — X21 | 2023 | Codex만 | 본문 | 5 |
| Jung 외, CaddieSet, CVPRW — X24 | 2025 | Codex만 | 본문 | 4,6 |
| Kim 외, Sci Rep 11 (14 이벤트·TP/TC) — X25 | 2021 | Codex만 | 본문 | 2,4 |
| Horan & Kavanagh, Sports Biomech 11(2) — K02 | 2012 | Claude만 | 초록 | 1 |
| Vena 외, Sports Eng — K03 | 2011 | Claude만 | 서지만 | 1 |
| Bourgain 외, Sports 10(6) (체계적 고찰) — K04 | 2022 | Claude만 | 초록 | 1,4 |
| Liu 외, PLOS One 20(9) — K05 | 2025 | Claude만 | 초록 | 1,3 |
| Sim 외, J Sports Sci 35(20) (전환 구간 정량화) — K07 | 2017 | Claude만 | 초록 | 2,4 |
| Cole & Grimshaw, Sports Med 46(3) — K08 | 2016 | Claude만 | 초록 | 2,3 |
| Lynn 외, Int J Golf Sci — K09 | 2013 | Claude만 | 서지만 | 2 |
| Hume 외, Sports Med 35(5) — K11 | 2005 | Claude만 | 초록 | 3 |
| McNally 외, Int J Sports Med 35(9) — K13 | 2014 | Claude만 | 초록 | 3 |
| Ball & Best, J Sports Sci 25(7) — K15 | 2007 | Claude만 | 초록 | 2,3 |
| Joyce, Hum Mov Sci 55 — K17 | 2017 | Claude만 | 초록 | 3 |
| Rachnavy 외, Front Sports Act Living 8 — K19 | 2026 | Claude만 | 초록 | 3 |
| Izumoto 외, IJPAS 20(1) — K20 | 2019 | Claude만 | 서지만 | 3 |
| Sinclair 외, IJPAS 14(1) — K21 | 2014 | Claude만 | 서지만 | 3 |
| Lead/Trail Legs GRF (Adv Res Foot Ankle) — K22 | 2018 | Claude만 | 서지만 | 3 |
| Stančin & Tomažič, Sensors 13 — K27 | 2013 | Claude만 | 초록 | 4 |
| Selham 외, PeerJ CS 12 (GolfDB 17관절) — K28 | 2026 | Claude만 | 초록 | 4,6 |
| Ingwersen 외, NLDL (단안 3D 골프) — K30 | 2023 | Claude만 | 초록 | 5 |
| Stamm & Heimann-Steinert, JMIR mHealth 8 — K31 | 2020 | Claude만 | 본문 | 5 |
| Nakano 외, Front Sports Act Living 2 (OpenPose) — K32 | 2020 | Claude만 | 초록 | 5 |
| Dill 외, Curr Dir Biomed Eng (MediaPipe) — K33 | 2023 | Claude만 | 초록 | 5 |

집계: **양쪽 12 / Codex만 14 / Claude만 21 = 47편**. 본문 확인 17, 초록 확인 25, 서지만 5 (GolfPose는 Claude 서지만 → Codex 본문으로 상향).
겹침이 12/47(26%)로 낮다 — 두 조사가 서로 다른 출처를 많이 찾았다는 뜻이며, 한쪽 조사만으로는 범위가 크게 빠졌을 것이다.

## 2. RQ별 종합

### RQ1 · 운동학적 연쇄
- **합의:** 숙련자는 골반→흉곽(몸통)→팔(손)→클럽 순으로 최대 각속도가 근위에서 원위로 이어진다(K01/X01, 양쪽; K02; X10 Table 3 골반 458.3 / 흉곽 712.5 / 리드팔 1050.5 °/s).
- **주의(Codex만):** 피크 "순서"는 각속도를 어떤 성분으로 계산하느냐에 따라 같은 사람에서도 5–7가지로 바뀌고, 인접 피크 간격 대부분이 0.015 s 미만(X06 본문 pp.118–119). 숙련자 사이에서도 다운스윙 피크 순서가 일관되지 않았다(X02).
- **함의:** 30 fps 스마트폰 영상(프레임 간격 약 0.033 s)으로는 인접 피크 순서를 판별하기 어렵다 — **"연쇄 순서 채점"은 근거가 약하다**.

### RQ2 · 골반 움직임 개시·전환
- **정의 후보(문헌):**
  1. 골반 회전 방향 반전 = 다운스윙 개시(K06/X03 양쪽 — "다운스윙은 골반 회전 반전으로 시작, 이어서 상체 반전")
  2. **골반 전환(TP)과 클럽 전환(TC)을 별도 이벤트로 분리**(X25 — 14 이벤트 체계, 하체 개시가 클럽 반전보다 앞설 수 있음)
  3. 분절의 각속도 최저점을 전환으로 정의(X10 Table 1)
  4. 두 분절 각도 관계(벡터 코딩)로 전환 구간을 정량화(K07; 협응 분석 X05)
  5. 골반의 타깃 방향 측면 이동(K08), 체중 이동은 다운스윙 초기에 앞으로(K15; X09)
- **상충:** X07은 "톱" 자체를 골반 반전으로 정의 → 이 연구로는 "골반이 클럽보다 몇 ms 먼저"를 말할 수 없다(Codex 지적). 문헌에서 **모든 골퍼에게 쓸 수 있는 선행시간 임계값은 확보되지 않음**(양쪽 공통 미확인).
- **함의:** Swing.Lab에 "골반 개시" 이벤트를 추가할 근거는 충분(1·2). 단 손목 기반 톱과는 **다른 이벤트**로 저장하고, 시간차를 정상/비정상으로 채점하지 않는다.

### RQ3 · 역학·에너지·X-Factor
- **합의:** 일·동력은 주로 허리·고관절에서 생성되어 위로 전달(K12/X16 본문 — 몸 전체 일의 68.7–72.2%), 하지 일·지면 상호작용도 속도와 관련(K13 R=0.63; K19 35.5%→75.4%; K14/X14).
- **상충 — X-Factor와 속도의 관계:**
  | 결과 | 출처 |
  |---|---|
  | 양(+)의 중간 상관 r ≥ 0.50 (볼 속도) | K10/X11 Myers 2008 |
  | 최대 X-factor와 CSI 상관 중앙값 0.900 | K06/X03 Meister 2011 |
  | **계산 방법마다 값이 유의하게 다르고**, 클럽헤드 속도와 **직접 관련 없음** | K18/X12 Kwon 2013 |
  | 남자 주니어에서 **r = −0.847**(음), 여자는 무관 | X08 Gryc 2023 |
  | 하부 몸통 X-factor stretch가 속도 분산과 관련 | K17 Joyce 2017 |
- **함의:** X-Factor를 점수의 핵심 감점 요인으로 쓰는 현재 방식은 근거가 엇갈린다. **정의(어느 평면·어느 시점)를 고정하지 않은 X-Factor 수치는 서로 비교할 수 없다**(K04, X10).

### RQ4 · 단계 정의와 자동 이벤트 검출
- **벤치마크:** GolfDB 1,400 영상·8 이벤트, SwingNet 평균 76.1%, 6/8 이벤트 91.8%(K24/X22 양쪽). CaddieSet 이벤트 모델 78.0%(X24 Supplement A).
- **선행 사례(Codex만):** 단안 영상에서 **손목 높이 최대/최소로 톱·임팩트·피니시를 찾는 방법이 이미 연구에 쓰임**(X20) — 현재 Swing.Lab 방식과 같은 계열. 단 이 연구는 이벤트 정확도를 보고하지 않는다.
- **IMU:** 시계열 학습 모델이 휴리스틱보다 정확(K25/X18 5–92 ms), 손목 속도 제약(어드레스·톱·피니시 ≈ 0)(K26/X19).
- **함의:** 지금 방식(손목 휴리스틱)은 문헌상 존재하는 방법이지만 **정확도 근거가 없다** → GolfDB로 측정이 우선.

### RQ5 · 단안 2D 포즈와 회전 추정
- **핵심 합의(양쪽):** 2D 투영 X-Factor는 3D와 톱에서 −16.72 ± 6.20° 차이(K29/X26, 본문) — 주원인은 몸통·골반의 굴곡·측굴에 의한 투영 오차.
- **Codex의 추가 지적:** 그 논문의 2D는 "수평면 투영"이며, Swing.Lab의 "카메라 화면상 관절선 기울기"와도 다른 측정량이다 → 16.72°를 빼는 보정은 근거가 없다.
- **단안 3D 모델:** 그럴듯해 보여도 골프 분석에 그대로 쓸 수 없음(K30). MediaPipe 정확도는 카메라 시야각·동작에 크게 의존(K33), 다리 교차 시 좌우 혼동(X21).
- **양쪽 공통 미확인:** 골프에서 **MediaPipe의 골반·흉곽 축 회전각과 개시 시점을 모션캡처와 직접 비교한 연구는 찾지 못함**.
- **함의:** 회전각을 "각도 값"으로 보고하는 것 자체를 재검토. 대신 **시간 이벤트(언제 바뀌었나)** 와 **방향(어느 쪽으로)** 처럼 투영 오차에 덜 민감한 신호를 우선.

### RQ6 · 데이터셋
| 데이터셋 | 내용 | 용도 | 권리 |
|---|---|---|---|
| GolfDB (K24/X22) | 1,400 영상, 8 이벤트 라벨, 촬영 방향 | **단계 검출 인식률** | 공식 저장소 README 확인(X22) — 원본 영상 권리는 별도 확인 필요 |
| GolfDB + 17관절 주석 (K28) | 프레임별 관절 | 관절 정확도 | 공개 여부 미확인 |
| GolfSwing/GolfPose (K34/X23) | 골퍼 17 + 클럽 5 키포인트 2D/3D | 포즈 정확도 | 본문 확인(X23), 라이선스 개별 확인 |
| CaddieSet (X24) | 924샷, 포즈 특징 + 볼 결과 | 결과 예측 | 저장소 **MIT 라이선스**(취합 시 원문 확인) — 데이터 자체 조건은 별도 확인 |

## 3. 두 조사의 차이에서 배운 점
- Claude는 **역학·지면반력·포즈 정확도 일반** 쪽을, Codex는 **이벤트 정의·전환의 조작적 정의·단안 골프 영상 선행 사례** 쪽을 더 찾았다
- Codex가 Claude보다 본문 확인 비율이 높았다(16/26 vs 2/33) — Europe PMC 전문 API를 사용
- Claude 조사에서 DOI→PubMed 잘못 매칭 1건을 발견해 제목 대조로 막았다(`01` 참조)
