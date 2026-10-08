# 01 · Claude 조사 결과 — 골프 스윙 역학·단계 인식

조사 2026-10-08 · 조사자 Claude (Opus) · 지시서 `golf-biomech-research-prompt.md` 5절 A

## 조사 방법과 한계
- 검색: WebSearch(일반) + **Crossref API**(서지 확인) + **PubMed E-utilities**(초록 원문) + 출판사/학회 페이지 WebFetch
- 확인 수준: `본문 확인`(전문 열람) / `초록 확인`(PubMed·Crossref·학회 페이지 초록 원문) / `서지만 확인`(Crossref 메타데이터는 있으나 초록을 열지 못함 — **수치 인용 금지**)
- 검증 사고 1건: DOI로 PubMed를 조회했을 때 `10.7557/18.6793`이 무관한 의학 논문으로 잘못 매칭됨 → 학회 원문 페이지로 재확인. 이후 모든 초록은 제목 일치를 대조함
- 접근 실패: ResearchGate·CVF 페이지 403, 일부 PDF 텍스트 추출 불가 → 해당 항목은 PubMed/Crossref/arXiv로 대체 확인
- 수치는 아래 각 항목의 "위치"에 적은 초록·본문 문장에 있는 값만 옮겼다

## 출처 수 요약
| RQ | 출처 ID |
|---|---|
| RQ1 운동학적 연쇄 | C01, C02, C03, C04, C05, C23 |
| RQ2 골반 개시·전환 | C06, C07, C08, C09, C10 |
| RQ3 역학·에너지 | C08, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C22 |
| RQ4 단계·이벤트 검출 | C24, C25, C26, C27, C28, C04 |
| RQ5 단안 2D 포즈·회전 추정 | C29, C18, C30, C31, C32, C33, C34 |
| RQ6 데이터셋 | C24, C28, C34 |
중복 없는 출처 **33개** (초록·본문 확인 27 / 서지만 확인 6, C23은 확인 실패로 제외)

---

## RQ1 · 운동학적 연쇄

**C01** / RQ1,RQ3 / Tinmark F, Hellström J, Halvorsen K, Thorstensson A (2010). Elite golfers' kinematic sequence in full-swing and partial-swing shots. *Sports Biomechanics* 9(4):236–244 / doi:10.1080/14763141.2010.535842 / 초록 확인
- 설계·대상: 45명(남 프로 11, 남 엘리트 아마 21, 여 엘리트 아마 13), 웨지 40/55/70 m 부분 스윙 + 5번 아이언·드라이버 풀스윙
- 측정: 전자기 추적(Polhemus Liberty) 240 Hz, 골반·상체·손의 합성 각속도 크기
- 결과(초록): 모든 조건·성별·숙련도에서 근위→원위 시간 순서와 최대 각속도의 순차 증가가 유의
- 적용: **부분** — 순서(골반→몸통→손)는 2D 관절 좌표의 각도 시계열로 근사 가능하나, 각속도 "크기"는 3D 기준이라 2D 값과 직접 비교 불가

**C02** / RQ1 / Horan SA, Kavanagh JJ (2012). The control of upper body segment speed and velocity during the golf swing. *Sports Biomechanics* 11(2):165–174 / doi:10.1080/14763141.2011.638390 / 초록 확인
- 대상: 남 프로 14명, 광학 모션캡처 3D
- 결과(초록): 다운스윙 중 상체에서 흉곽이 최고 속도; 흉곽–골반 결합 강함(평균 R² = 0.92), 머리–흉곽은 변동 큼(평균 R² = 0.76)
- 적용: **부분** — 흉곽·골반 결합이 강하다는 점은 "골반 개시 후 흉곽이 따라온다"는 시간 지연 검출의 근거. 머리 움직임은 독립 신호로 다뤄야 함

**C03** / RQ1 / Vena A, Budney D, Forest T, Carey JP (2011). Three-dimensional kinematic analysis of the golf swing using instantaneous screw axis theory, Part 2: golf swing kinematic sequence. *Sports Engineering* / doi:10.1007/s12283-010-0059-7 / **서지만 확인**
- 적용: 판단 보류(수치 인용 금지)

**C04** / RQ1,RQ4 / Bourgain M, Rouch P, Rouillon O, Thoreux P, Sauret C (2022). Golf Swing Biomechanics: A Systematic Review and Methodological Recommendations for Kinematics. *Sports (Basel)* 10(6):91 / doi:10.3390/sports10060091 / 초록 확인
- 설계: 체계적 문헌고찰 92편 — X-factor, crunch factor, 스윙 평면·클럽헤드 궤적, 운동학적 연쇄, 관절 각운동학
- 결과(초록): **방법론 합의 부족으로 결과 일반화가 어렵고 상충 결과가 존재**; 3D 접근이 일반적이나 ISB(국제생체역학회) 권고는 드물게 적용
- 적용: **해당(방법론)** — Swing.Lab의 각도 정의를 문헌의 어느 정의와 맞출지 명시해야 한다는 근거

**C05** / RQ1,RQ3 / Liu H, Li Z, Zhou H, Zhao Z, Liu B, Wang Z (2025). Biomechanical characteristics of swing techniques using different clubs in college male golfers. *PLOS One* 20(9):e0331051 / doi:10.1371/journal.pone.0331051 / 초록 확인
- 대상·측정: 저핸디캡 대학생 남 10명, 드라이버·5i·7i 각 10회, 250 Hz 적외선 모션캡처 + 1000 Hz 3D 지면반력판
- 결과(초록): 아이언이 드라이버보다 최대값 도달이 빠르고 각속도가 작음; 클럽별 지면반력 양상이 다름
- 적용: **부분** — 클럽 종류에 따라 단계 시간 비율이 달라지므로 고정 비율(현재 `phase_detector.py`의 25%/70% 등) 휴리스틱의 한계 근거

## RQ2 · 골반 움직임 개시·전환

**C06** / RQ2,RQ3 / Meister DW, Ladd AL, Butler EE, Zhao B, Rogers AP, Ray CJ, Rose J (2011). Rotational biomechanics of the elite golf swing: benchmarks for amateurs. *Journal of Applied Biomechanics* 27(3):242–251 / doi:10.1123/jab.27.3.242 / 초록 확인
- 대상: 프로 10, 아마 5 (남), 3D 운동학·운동역학
- 결과(초록): **"다운스윙은 골반 회전의 방향 전환으로 시작되고, 이어서 상체 회전이 전환된다"**; 최대 X-factor는 모든 스윙에서 최대 free moment보다 먼저, **다운스윙 초기**에 발생; CSI(임팩트 클럽헤드 속도)와의 상관 중앙값 — free moment/kg 0.943, 임팩트 X-factor 0.943, 최대 X-factor 0.900, 최대 상체 회전 0.900
- 적용: **부분(핵심)** — "골반 회전 방향 전환 시점 = 다운스윙 개시"라는 정의를 제공. 단 2D에서 골반 축 회전의 방향 전환을 안정적으로 잡아야 함(RQ5 참조)

**C07** / RQ2,RQ4 / Sim T, Choi A, Lee S, Mun JH (2017). How to quantify the transition phase during golf swing performance: Torsional load affects low back complaints during the transition phase. *Journal of Sports Sciences* 35(20):2051–2059 / doi:10.1080/02640414.2016.1255345 / 초록 확인
- 결과(초록): 전환 구간 정량화 방법 3가지(**벡터 코딩 기법 VCT**, 리드 손 속도, X-factor stretch)를 비교하고 VCT를 제안; 이전 방법들은 정확도 한계가 있었다고 기술
- 적용: **부분(핵심)** — 전환 구간을 "손 속도" 하나로 정하는 것(현재 손목 y 기반과 유사)보다 분절 간 협응 패턴(VCT)으로 정하는 접근 근거. VCT는 두 분절 각도 시계열만 있으면 계산 가능 → 2D 근사 각도로 시도 가능

**C08** / RQ2,RQ3 / Cole MH, Grimshaw PN (2016). The Biomechanics of the Modern Golf Swing: Implications for Lower Back Injuries. *Sports Medicine* 46(3):339–351 / doi:10.1007/s40279-015-0429-1 / 초록 확인
- 결과(초록): 숙련자는 다운스윙에서 **골반을 타깃 방향으로 측면 이동(lateral slide)** 시키며 이것이 클럽헤드 속도에 기여; 측정 방법·지표 정의의 합의 부족 지적
- 적용: **가능** — 골반 측면 이동은 정면(face-on) 2D 영상에서 골반 중심 x좌표 변화로 비교적 직접 관측 가능 → 골반 "개시" 신호 후보(현재 코드에 `hip_x_history`가 이미 수집되지만 단계 판정에는 미사용)

**C09** / RQ2 / Lynn SK, Frazier BS, New KM, Wu WFW, Cheetham PJ, Noffal GJ (2013). Rotational Kinematics of the Pelvis During the Golf Swing: Skill Level Differences and Relationship to Club and Ball Impact Conditions. *International Journal of Golf Science* / doi:10.1123/ijgs.2013-0011 / **서지만 확인**

**C10** / RQ2,RQ3 / Myers J, Lephart S, Tsai YS, Sell T, Smoliga J, Jolly J (2008). The role of upper torso and pelvis rotation in driving performance during the golf swing. *Journal of Sports Sciences* 26(2):181–188 / doi:10.1080/02640410701373543 / 초록 확인
- 대상: 레크리에이션 골퍼 100명, 본인 드라이버, 론치 모니터
- 결과(초록): 볼 속도와 중간 수준 상관(r ≥ 0.50, P < 0.001) — 톱에서의 몸통-골반 분리, 최대 분리, 최대 상체 회전 속도, 리드 팔 수평 시점·임팩트 전 40 ms 상체 회전 속도, 분리 속도 등. "톱과 **다운스윙 개시 시점**에 분리를 최대화" 권고
- 적용: **부분** — "리드 팔 수평(lead arm parallel)"을 중간 이벤트로 쓰는 근거(C14도 동일 이벤트 사용)

## RQ3 · 역학·에너지·지면반력

**C11** / RQ3 / Hume PA, Keogh J, Reid D (2005). The role of biomechanics in maximising distance and accuracy of golf shots. *Sports Medicine* 35(5):429–449 / doi:10.2165/00007256-200535050-00005 / 초록 확인
- 결과(초록): 백스윙에서 지면반력이 뒷발 쪽 비중↑ → 다운스윙에서 앞발로 이동; 백스윙에서 엉덩이·몸통·상지 근육 신장, **다운스윙 초기 X-factor 최대화**, 리드 팔이 수평 아래 **약 30°일 때 손목 언코킹** → 힘의 합산 원리
- 적용: **부분** — "리드 팔 수평 아래 약 30°"는 2D에서 팔 각도로 근사 가능한 이벤트 후보

**C12** / RQ3 / Nesbit SM, Serrano M (2005). Work and Power Analysis of the Golf Swing. *Journal of Sports Science and Medicine* 4:520–533 / PMC3899668 (DOI 없음) / 본문 확인(jssm.org 전문)
- 설계: 아마 4명, 전신 3D 다분절 모델 + 유연 클럽 모델
- 결과(본문): 신체 일의 대부분이 **허리(요추·흉추)와 고관절**에서 생성 — 피험자별 71.8, 72.2, 70.0, 68.7%; 어깨·팔 24.7–28.0%, 다리 3.3–3.8%; 일은 아래→위 순차로 생성·전달; "힘과 가동범위가 동등하게 중요"
- 적용: **불가(직접)** — 관절 일률 계산은 힘 정보가 필요. 단 "고관절·몸통이 주 동력원" → 골반·몸통 지표 정확도 개선의 우선순위 근거

**C13** / RQ3 / McNally MP, Yontz N, Chaudhari AM (2014). Lower extremity work is associated with club head velocity during the golf swing in experienced golfers. *International Journal of Sports Medicine* 35(9):785–788 / doi:10.1055/s-0034-1367010 / 초록 확인
- 결과(초록): 다운스윙 하지 총 일이 클럽헤드 속도의 강한 예측 변수(R = 0.63)
- 적용: **불가(직접)** — 힘판 필요

**C14** / RQ3 / Han KH, Como C, Kim J, Lee S, Kim J, Kim DK, Kwon YH (2019). Effects of the golfer–ground interaction on clubhead speed in skilled male golfers. *Sports Biomechanics* 18(2):115–134 / doi:10.1080/14763141.2019.1586983 / 초록 확인
- 대상: 핸디캡 ≤ 3 남 63명, 드라이버·5i·PW, 모션캡처 + 힘판 2개
- 결과(초록): **리드 팔이 지면과 평행해지는 순간이 최대 각 노력 시점**이며 그 근처 리드 발 하중이 두 최대 모멘트 생성에 결정적
- 적용: **부분** — "리드 팔 수평"을 다운스윙 내 핵심 이벤트로 추가하는 근거(2D 팔 각도로 검출 가능)

**C15** / RQ3,RQ2 / Ball KA, Best RJ (2007). Different centre of pressure patterns within the golf stroke I: Cluster analysis. *Journal of Sports Sciences* 25(7):757–770 / doi:10.1080/02640410600874971 / 초록 확인
- 대상: 프로~고핸디캡 62명, 힘판 2개, 200 Hz 영상으로 **8개 스윙 이벤트** 식별
- 결과(초록): 체중 이동 스타일 2가지("Front Foot", "Reverse") — 둘 다 백스윙에 뒷발, **다운스윙 초기에 앞으로** 이동; 이후 양상이 갈림. 두 스타일 모두 숙련도 전반에 존재 → 기술 오류 아님
- 적용: **부분** — 골반/체중 이동 하나의 패턴을 "정답"으로 채점하면 안 된다는 근거(채점 로직 주의)

**C16** / RQ3 / Chu Y, Sell TC, Lephart SM (2010). The relationship between biomechanical variables and driving performance during the golf swing. *Journal of Sports Sciences* 28(11):1251–1259 / doi:10.1080/02640414.2010.507249 / 초록 확인
- 대상: 308명, 운동학 + 지면반력, 4개 이벤트에서 회귀
- 결과(초록): 모델이 볼 속도 분산의 44–74% 설명; X-Factor, 팔·손목 늦은 릴리스, 몸통 전방·측방 기울기, 체중 이동이 유의
- 적용: **부분** — 몸통 측방 기울기는 정면 2D에서 비교적 관측 가능

**C17** / RQ3 / Joyce C (2017). The most important "factor" in producing clubhead speed in golf. *Human Movement Science* 55:138–144 / doi:10.1016/j.humov.2017.08.007 / 초록 확인
- 대상: 저핸디캡 남 15명, 10카메라 250 Hz
- 결과(초록): 5번 아이언 회귀에서 클럽헤드 속도 분산이 **하부 몸통 X-factor stretch 증가**와 **몸통 측방 굴곡 감소**와 관련
- 적용: **부분**

**C18** / RQ3,RQ5 / Kwon YH, Han KH, Como C, Lee S, Singhal K (2013). Validity of the X-factor computation methods and relationship between the X-factor parameters and clubhead velocity in skilled golfers. *Sports Biomechanics* 12(3):231–246 / doi:10.1080/14763141.2013.771896 / 초록 확인
- 대상: 숙련 남 18명(핸디캡 −0.6 ± 2.1), 250 Hz 광학
- 결과(초록): **X-factor 계산 방법(평면 기반 2가지 vs 상대 방향)에 따라 값이 유의하게 다름(p < 0.001)**; 관행적 방법은 언와인딩 구간에서 값이 과대 → 의미가 의문; X-factor 지표들은 최대 클럽헤드 속도와 **직접 관련이 없었음**
- 적용: **해당(핵심)** — Swing.Lab의 X-Factor 불안정의 원인 후보(계산 방법 자체) + "X-Factor로 점수를 매기는 것"의 근거가 약하다는 신호

**C19** / RQ3 / Rachnavy P et al. (2026). Foot–ground interaction and clubhead speed: impulse-based energy transfer as the key mechanism in the golf swing. *Frontiers in Sports and Active Living* 8:1790645 / doi:10.3389/fspor.2026.1790645 / 초록 확인
- 대상: 30명(프로 15, 상급 아마 15), 드라이버·7i, 운동학 + 지면반력 + 족저압
- 결과(초록): 발-지면 상호작용 변수가 클럽헤드 속도 분산의 35.5% 설명 → 몸통 순서·충격량 기반 에너지 전달 효율 추가 시 75.4%(adj R² = 0.715); 영향은 직접이 아니라 에너지 전달 효율을 통한 간접 경로
- 적용: **불가(직접)**

**C20** / RQ3 / Izumoto Y, Kurihara T, Sato T, Maeo S, Sugiyama T, Kanehisa H, Isaka T (2019 온라인 게재, 권호는 2020). Changes in angular momentum during the golf swing and their association with club head speed. *International Journal of Performance Analysis in Sport* 20(1):42–52 / doi:10.1080/24748668.2019.1702298 / **서지만 확인**

**C21** / RQ3 / Sinclair J, Currigan G, Fewtrell DJ, Taylor PJ (2014). Biomechanical correlates of club-head velocity during the golf swing. *International Journal of Performance Analysis in Sport* 14(1):54–63 / doi:10.1080/24748668.2014.11868702 / **서지만 확인**

**C22** / RQ3 / Lead and Trail Legs Ground Reaction Forces and Timing During the Golf Swing with Different Clubs in Average Golfers (2018). *Advance Research on Foot & Ankle* / doi:10.29011/2688-6413.100009 / **서지만 확인**(저자 미확인)

**C23** / RQ1 / Cheetham PJ 등 계열 운동학적 연쇄 비교 연구 — **확인 실패(제외)**: "Comparison of kinematic sequence parameters between amateur and professional golfers"는 Crossref에서 일치 항목을 찾지 못함. 근거로 쓰지 않음

## RQ4 · 단계 정의와 자동 이벤트 검출

**C24** / RQ4,RQ6 / McNally W, Vats K, Pinto T, Dulhanty C, McPhee J, Wong A (2019). GolfDB: A Video Database for Golf Swing Sequencing. *CVPR Workshops*, pp. 2553–2562 / doi:10.1109/CVPRW.2019.00311 (저자·쪽 Crossref 확인) / arXiv:1903.06528 / 초록 확인(arXiv)
- 데이터: 영상 1,400개, 이벤트 프레임·바운딩박스·선수·성별·클럽·촬영 방향 라벨
- 결과(초록): 경량 CNN+RNN **SwingNet**이 8개 이벤트를 평균 **76.1%**, 8개 중 6개를 **91.8%** 정확도로 검출; 모바일 실시간 분석 지향
- 적용: **가능(핵심)** — 공개 기준(8 이벤트 정의·평가 지표)으로 Swing.Lab 단계 검출 인식률을 정량 비교 가능. 라이선스·이벤트 정의 세부는 본문 미확인

**C25** / RQ4 / Kim M, Park S (2020). Golf Swing Segmentation from a Single IMU Using Machine Learning. *Sensors* 20(16):4466 / doi:10.3390/s20164466 / 초록 확인
- 대상: 프로 9, 숙련 11 (남); 머리·손목·허리 IMU; BiLSTM·CNN
- 결과(초록): 5개 주요 단계 분할 평균 오차 **5–92 ms**, 휴리스틱보다 정확
- 적용: **부분** — "시계열 학습 모델 > 휴리스틱" 근거. 입력이 IMU라 직접 이식은 불가하나 관절 좌표 시계열에도 같은 구조 적용 가능

**C26** / RQ4 / Kim M, Park S (2024). Enhancing accuracy and convenience of golf swing tracking with a wrist-worn single inertial sensor. *Scientific Reports* 14:9201 / doi:10.1038/s41598-024-59949-w / 초록 확인
- 결과(초록): **어드레스·백스윙 톱·피니시에서 손목 속도 제약**으로 드리프트 절반 감소, 궤적 오차 약 17 cm
- 적용: **부분** — 톱·피니시 = 손목 속도 ≈ 0이라는 제약은 현재 손목 기반 검출과 일치(검증 근거)

**C27** / RQ4 / Stančin S, Tomažič S (2013). Early improper motion detection in golf swings using wearable motion sensors: the first approach. *Sensors* 13(6):7505–7521 / doi:10.3390/s130607505 / 초록 확인
- 결과(초록): 리드 팔 센서 + PCA로 개인 기준 스윙 대비 백스윙 초반 이상 동작 검출
- 적용: **부분** — 개인별 기준 대비 편차 검출 아이디어

**C28** / RQ4,RQ6 / Selham, Tian, Guo (2026). Spatiotemporal key point detection in golf swing sequences via hybrid CNN-TCN architecture and regression-based refinement. *PeerJ Computer Science* 12:e3664 / doi:10.7717/peerj-cs.3664 / 초록 확인(Crossref)
- 결과(초록): GolfDB에 **프레임별 17관절 수동 주석** 추가; MAE 2.8 px, PCK@0.1 = 94.5%, 14.9 ms/프레임
- 적용: **가능** — 골프 특화 키포인트 벤치마크로 MediaPipe 관절 정확도 비교 가능(데이터 공개·라이선스는 본문 미확인)

## RQ5 · 단안 2D 포즈 추정과 회전 추정

**C29** / RQ5 / Smith AC, Roberts JR, Wallace ES, Kong P, Forrester SE (2016). Comparison of Two- and Three-Dimensional Methods for Analysis of Trunk Kinematic Variables in the Golf Swing. *Journal of Applied Biomechanics* 32(1):23–31 / doi:10.1123/jab.2015-0032 / 초록 확인
- 결과(초록): 2D(실험실 평면 투영)와 3D 비교 — 곡선 모양은 비슷하나 톱에서 몸통 굴곡 차 −6.5 ± 3.6°, 임팩트에서 우측 측굴 차 8.7 ± 2.9°; **2D와 3D X-factor 차이 약 16°**, 대부분 몸통·골반의 굴곡·측굴로 인한 **투영 오차**로 설명
- 적용: **해당(핵심)** — Swing.Lab의 회전 지표가 **2D 투영 오차를 그대로 안고 있다**는 직접 근거. 현재 계산은 "실험실 평면 투영"보다도 단순한 화면상 선 기울기

**C30** / RQ5 / Ingwersen CK, Jensen JN, Hannemose MR, Dahl AB (2023). Evaluating current state of monocular 3D pose models for golf. *Proceedings of the Northern Lights Deep Learning Workshop* / doi:10.7557/18.6793 / 초록 확인(학회 페이지)
- 결과(초록): 단안 3D 포즈 모델 예측을 마커 모션캡처와 비교 — 재투영은 그럴듯하나 **"현재 모델은 고급 골프 분석에 그대로 쓸 수 없다"**
- 적용: **해당** — MediaPipe의 z(깊이)로 축 회전을 계산하는 방식도 검증 없이 쓰면 위험하다는 근거

**C31** / RQ5 / Stamm O, Heimann-Steinert A (2020). Accuracy of Monocular Two-Dimensional Pose Estimation Compared With a Reference Standard for Kinematic Multiview Analysis: Validation Study. *JMIR mHealth and uHealth* 8(12):e19608 / doi:10.2196/19608 / 본문 확인(PMC7781802)
- 결과: 2D+3D 결합 알고리즘(OpenPose Body25 기반) vs 다시점 기준 — ICC 0.951–0.997, **골반 MAE 1.40°**(가장 정확), 우측 어깨 6.48°(가장 큼)
- 적용: **부분** — 일상 동작 기준. 골프 스윙처럼 빠르고 회전이 큰 동작에는 일반화 미확인

**C32** / RQ5 / Nakano N, Sakura T, Ueda K, Omura L, Kimura A, Iino Y, Fukashiro S, Yoshioka S (2020). Evaluation of 3D Markerless Motion Capture Accuracy Using OpenPose With Multiple Video Cameras. *Frontiers in Sports and Active Living* 2:50 / doi:10.3389/fspor.2020.00050 / 초록 확인
- 결과(초록): 다중 카메라 OpenPose vs 광학 마커 — MAE 약 47%가 < 20 mm, 80%가 < 30 mm, 10%는 > 40 mm(주원인: 2D 오추적·분절 뒤바뀜)
- 적용: **부분** — 단안이 아닌 다중 카메라 결과. 프레임별 오추적 보정이 정확도에 결정적이라는 점은 공통

**C33** / RQ5 / Dill S, Rösch A, Rohr M, Güney G, De Witte L, Schwartz E (2023). Accuracy Evaluation of 3D Pose Estimation with MediaPipe Pose for Physical Exercises. *Current Directions in Biomedical Engineering* / doi:10.1515/cdbme-2023-1141 / 초록 확인(Crossref)
- 결과(초록): MediaPipe Pose 정확도가 **카메라 시야각과 동작 종류에 크게 의존**; 최적 조건에선 높지만 조건이 나빠지면 빠르게 저하
- 적용: **해당** — 촬영 방향 고정(정면/후방) 안내가 인식률에 직접 영향

**C34** / RQ5,RQ6 / Lee M-H, Zhang Y-C, Wu K-R, Tseng Y-C (2024). GolfPose: From Regular Posture to Golf Swing Posture. *ICPR 2024, LNCS*, pp. 387–402 / doi:10.1007/978-3-031-78305-0_25 / **서지만 확인**(초록 미열람. 검색 결과 요약상 골퍼 17 + 클럽 5 키포인트 2D/3D 데이터셋 — 원문 미확인이라 수치 인용 금지)

## Claude 조사의 잠정 결론 (취합 전, 근거 ID 포함)
1. 현재 회전 지표 불안정은 **계산 방법 문제일 가능성이 높다**: 2D 투영만으로 X-factor를 구하면 3D와 약 16° 차이(C29), 계산 방법마다 값이 유의하게 다름(C18), 단안 3D 모델도 그대로는 부정확(C30)
2. **골반 개시**는 문헌상 "골반 회전 방향 전환"(C06) 또는 "골반 측면 이동"(C08)으로 정의되며, 정면 2D에서는 후자(골반 중심 x 이동)가 더 직접 관측 가능
3. 단계 세분화 후보 이벤트: 리드 팔 수평(C10·C14), 리드 팔 수평 아래 약 30°(C11), 전환 구간(C07의 VCT)
4. 인식률은 GolfDB 8 이벤트 기준(C24, SwingNet 76.1%)으로 정량 비교 가능
5. 채점 주의: 체중 이동은 두 스타일이 모두 정상(C15), X-factor와 속도의 직접 관계는 방법에 따라 부정적 결과도 있음(C18)
