# Codex 독립 조사 — 골프 스윙 역학·단계 인식

조사일: 2026-10-08 (Asia/Seoul)

`golf-biomech-research-prompt.md` 전체를 읽고 **5절 B만 수행**했다. `01_claude_findings.md`는 읽지 않았다. 이 파일만 작성했으며 코드 수정, 구현, git 커밋, 두 조사 결과의 취합은 수행하지 않았다.

## 범위·확인 방법·집계

- **웹 검색 사용 가능**: 웹 검색과 URL 열기를 사용했다. 검색 결과 요약만으로 항목을 채택하지 않았다.
- 출판사, 학술지, 대학·저자 공식 저장소, PubMed, Europe PMC에서 실제 열린 논문 본문 또는 초록을 확인했다. PMC·출판사 웹페이지의 CAPTCHA/403/429 오류는 공개 원문을 제공하는 **Europe PMC 공식 `fullTextXML` API** 또는 저자 공개본으로 보완했다. API도 실패하면 초록만 확인으로 남겼다.
- **본문 확인**은 해당 논문의 방법·결과 및 인용한 표/절을 읽었다는 뜻이다. 초록만 확인한 항목에는 본문에 있을 법한 수치를 보충하지 않았다. HTML/XML은 절·표 번호, PDF는 해당 공개본의 쪽·표 번호를 사용한다.
- DOI는 열린 공식 서지에서 확인한 식별자다. 링크는 **실제 열어 내용을 확인한 공식 URL**을 제공한다. DOI 리다이렉트를 전수 재검증하는 지시서 6절의 취합 작업은 수행하지 않았다.
- 학술 출처 **26편**: **본문 확인 16편 / 초록만 확인 10편**. 같은 논문의 출판사·저자본·API·공식 코드 저장소는 한 편으로 집계했다. 데이터 접근·라이선스 확인에 쓴 공식 저장소는 별도 학술 출처로 세지 않았다.
- 여러 RQ에 해당하는 논문은 해당 RQ마다 표시하되 전체 편수에서는 한 번만 센다. 아래 숫자는 독립 실험·독립 참가자 집단의 수가 아니다.

| RQ | 출처 수 | ID |
|---|---:|---|
| RQ1 운동학적 연쇄 | 7 | C01, C02, C03, C04, C05, C06, C10 |
| RQ2 골반 개시·전환 | 8 | C02, C03, C05, C07, C08, C09, C10, C25 |
| RQ3 역학·에너지·GRF·X-Factor | 12 | C03, C08, C09, C10, C11, C12, C13, C14, C15, C16, C25, C26 |
| RQ4 단계·이벤트 검출 | 8 | C08, C17, C18, C19, C20, C22, C24, C25 |
| RQ5 단안 포즈·회전 측정 | 7 | C12, C17, C20, C21, C23, C24, C26 |
| RQ6 데이터셋·벤치마크 | 3 | C22, C23, C24 |

적용 가능성은 **현재 입력인 스마트폰 단안 영상과 MediaPipe 관절로 해당 연구의 측정·분석을 재현할 수 있는지**에 대한 조사자의 판단이다. 논문에서 검증된 성능과 이 판단을 구분한다. `부분`은 추가 검출기·학습·교정·검증이 필요하거나 일부 영상 특징만 재현 가능하다는 뜻이다. 모션캡처 연구의 촬영 방향은 단일 정면/후방 영상에 해당하지 않으면 그렇게 명시했다.

## 출처별 기록

### C01 — 숙련자 운동학적 연쇄

- **RQ:** RQ1
- **서지:** Tinmark F, Hellström J, Halvorsen K, Thorstensson A. (2010). *Elite golfers' kinematic sequence in full-swing and partial-swing shots*. Sports Biomechanics, 9(4), 236–244.
- **DOI·확인 URL:** DOI `10.1080/14763141.2010.535842`; [PubMed 초록](https://pubmed.ncbi.nlm.nih.gov/21309298/).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 45명: 남자 투어 프로 11명, 남자 엘리트 아마추어 21명, 여자 엘리트 아마추어 13명. 웨지 부분샷 및 5번 아이언·드라이버 풀스윙. Polhemus Liberty 전자기 추적 240 Hz로 골반·상체·손의 3D 각속도 벡터 크기 측정. 단일 카메라 방향 해당 없음. 위치: 초록.
- **핵심 결과:** 각 샷 조건·성별·숙련 집단에서 근위→원위 피크 발생 및 최대 각속도 증가를 보고했다. 그러나 **분절별 피크 값·피크 간 ms는 초록에 없어 미확인**. 측정된 손을 클럽으로 바꿔 인용하지 않는다. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 시간적 순서라는 평가 틀은 참고 가능하지만, 화면상 관절선 기울기를 이 연구의 3D 각속도로 사용할 수 없다. 초보자를 포함한 보편적 정상 순서로 일반화하기도 어렵다.

### C02 — 숙련자 내부에서도 다른 다운스윙 피크 순서

- **RQ:** RQ1, RQ2
- **서지:** Han KH, Como C, Kim J, Hung CJ, Hasan M, Kwon YH. (2019). *Effects of pelvis-shoulders torsional separation style on kinematic sequence in golf driving*. Sports Biomechanics, 18(6), 663–685.
- **DOI·확인 URL:** DOI `10.1080/14763141.2019.1629617`; [PubMed 초록](https://pubmed.ncbi.nlm.nih.gov/31543063/).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 남자 숙련자 74명, 핸디캡 ≤3, 분리·stretch 특성에 따른 5집단. 광학 모션캡처 후 기능적 스윙 평면에서 hip-line·thorax·shoulder-line·upper-lever·club·wrist의 각도/각속도 분석. 정면/후방 단안 실험 아님. 위치: 초록.
- **핵심 결과:** 백스윙·전환 순서는 대체로 완전/부분 근위→원위였으나 다운스윙 피크 순서는 집단 간 일관되지 않았고 신체 분절의 피크 시점이 유의하게 분리되지 않았다. **전환 순서와 피크 순서를 별도 정의**했다. 개별 시간차와 p값은 미확인. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 골반의 방향 전환 이벤트와 각속도 최대 이벤트를 구분할 근거. 모든 숙련자에게 하나의 피크 순서를 정답으로 부여할 근거는 되지 않는다.

### C03 — 골반 회전 반전과 초기 다운스윙의 최대 X-Factor

- **RQ:** RQ1, RQ2, RQ3
- **서지:** Meister DW, Ladd AL, Butler EE, Zhao B, Rogers AP, Ray CJ, Rose J. (2011). *Rotational biomechanics of the elite golf swing: benchmarks for amateurs*. Journal of Applied Biomechanics, 27(3), 242–251.
- **DOI·확인 URL:** DOI `10.1123/jab.27.3.242`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A21844613+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 남자 프로 10명·아마추어 5명, 3D 운동학·운동역학. 상체/골반 회전, X-/O-/S-factor 및 정규화 free moment와 임팩트 클럽헤드 속도(CSI)를 비교. 세부 장비·카메라 배치는 미확인. 위치: 초록.
- **핵심 결과:** 골반 회전 반전 후 상체 회전 반전으로 다운스윙이 시작됐다. 최대 X-Factor는 초기 다운스윙에 나타나며 모든 스윙에서 최대 free moment보다 먼저였다. CSI와 최대 X-Factor의 상관계수 중앙값 **0.900**. 클럽 톱 대비 골반 선행 ms는 미확인. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 골반 전환을 손목 톱과 별도로 관찰할 근거. 단안 영상만으로 free moment를 측정할 수 없고, 작은 표본의 상관을 인과관계나 개별 사용자 기준값으로 해석할 수 없다.

### C04 — 숙련도별 상지·클럽 각속도

- **RQ:** RQ1
- **서지:** Zheng N, Barrentine SW, Fleisig GS, Andrews JR. (2008). *Kinematic analysis of swing in pro and amateur golfers*. International Journal of Sports Medicine, 29(6), 487–493.
- **DOI·확인 URL:** DOI `10.1055/s-2007-989229`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A18004680+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 프로·낮은/중간/높은 핸디캡 남자 각 18명. 광전자 시스템 240 frames/s. 다운스윙 각속도 및 시점 분석. 단일 정면/후방 영상 실험 아님. 위치: 초록.
- **핵심 결과:** 프로 집단의 클럽 **샤프트** 각속도 **2413 ± 442°/s**, 오른 팔꿈치 신전 **854 ± 150°/s**, 오른 손목 **1183 ± 299°/s**, 왼 손목 **1085 ± 338°/s**가 각 비교집단 중 가장 컸다. 초록에는 분절 피크 간 시간차가 없다. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 숙련도와 각속도 차이를 다룰 근거지만, 이 값들은 모두 골반→흉곽 축 회전 속도나 클럽헤드 선속도가 아니다. MediaPipe 관절 위치의 단순 차분으로 그대로 재현할 수 없다.

### C05 — 골반·흉곽 협응을 벡터 코딩으로 비교

- **RQ:** RQ1, RQ2
- **서지:** Sim T, Yoo H, Choi A, Lee KY, Choi MT, Lee S, Mun JH. (2017). *Analysis of Pelvis-Thorax Coordination Patterns of Professional and Amateur Golfers during Golf Swing*. Journal of Motor Behavior, 49(6), 668–674.
- **DOI·확인 URL:** DOI `10.1080/00222895.2016.1271297`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A28287933+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 프로 15명·아마추어 15명. 골반–흉곽 운동의 vector coding으로 coupling angle γ 계산. 획득 장비·카메라 방향·프레임률은 초록에서 미확인.
- **핵심 결과:** 백스윙 회전 협응 집단 차이는 **p=0.333**. 다운스윙 회전 γ는 프로 **232.0°**, 아마추어 **229.5°**였고 굴곡/신전·측굴·회전의 협응 차이를 보고했다. 이는 **협응각**으로 X-Factor나 골반 회전각 자체가 아니다. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 두 분절의 시계열 관계를 평가하는 개념은 사용할 수 있다. 다만 화면상 기울기에 계산한 γ가 논문의 회전 협응과 같은 측정량인지는 별도 검증이 필요하다.

### C06 — 피크 순서는 각속도 성분 선택에 민감

- **RQ:** RQ1
- **서지:** Marsan T, Thoreux P, Bourgain M, Rouillon O, Rouch P, Sauret C. (2019). *Biomechanical analysis of the golf swing: methodological effect of angular velocity component on the identification of the kinematic sequence*. Acta of Bioengineering and Biomechanics, 21(2), 115–120.
- **DOI·확인 URL:** DOI 미확인; [학술지 공식 원문 PDF](https://actabio.pwr.edu.pl/fcp/YGBUKOQtTKlQhbx08SlkTUARAUWRuHQwFDBoIVURNWHlTFVZpCFghUHcKVigEQUw/302/public/publikacje/v21-2-2019/33.pdf).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 오른손잡이 남자 13명, 핸디캡 20 수준부터 프로. Vicon 12카메라·200 Hz, 84마커·OpenSim. 각속도 크기/지역 종축/다양한 평면 투영 등 7방법 비교. 위치: pp.116–118, Methods.
- **핵심 결과:** 각속도 벡터 크기의 최대값: 골반 **480 ± 82°/s**, 흉곽 **605 ± 87°/s**, 리드팔 **1310 ± 236°/s**. 같은 사람에게 방법별 **5–7개 순서**가 나왔다. 골반·흉곽·팔·전완·손 중 첫 피크–마지막 피크의 평균 간격은 방법별 **0.13 ± 0.03 ~ 0.19 ± 0.04 s**, 인접 피크 간격 대부분 **0.015 s 미만**. 위치: pp.118–119, Results·Table 2. 클럽까지 포함한 시간차로 읽으면 안 된다.
- **Swing.Lab 적용:** **부분**. 피크 순서를 판단하기 전에 각속도 정의와 시간해상도를 고정해야 함을 보여준다. 수치 자체는 단안 2D 기울기로 재현 불가.

### C07 — 골반·상체의 병진운동과 전환 정의

- **RQ:** RQ2
- **서지:** Beak SH, Choi A, Choi SW, Oh SE, Mun JH, Yang H, Sim T, Song HR. (2013). *Upper torso and pelvis linear velocity during the downswing of elite golfers*. Biomedical Engineering Online, 12, 13.
- **DOI·확인 URL:** DOI `10.1186/1475-925X-12-13`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC3599250/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** KPGA 남자 프로 14명, Vicon 6카메라·120 Hz. 골반/흉곽 마커와 인체모델로 분절 질량중심의 병진 속도·교차상관 측정. 위치: Methods.
- **핵심 결과:** 다운스윙 길이 **0.31 ± 0.04 s**(Table 1). 분절 질량중심 선속력 피크 시점은 골반 **47 ± 23%**, 상체 **59 ± 26%**(Table 2; 다운스윙 정규화 시간). 이 연구는 백스윙 톱을 **골반이 타깃 방향 회전으로 바뀌는 시점**으로 정의한다(Methods–Procedures). 따라서 이 자료로 골반이 클럽 톱보다 몇 ms 먼저 움직였다고 추론할 수 없다.
- **Swing.Lab 적용:** **부분**. 정면 골반 중심의 화면상 이동은 관찰 가능하지만, 관절 중점은 연구의 분절 질량중심과 동일하지 않다. 병진운동의 피크와 회전 개시를 분리해야 한다.

### C08 — 주니어의 골반·흉곽 협응과 클럽 기반 이벤트

- **RQ:** RQ2, RQ3, RQ4
- **서지:** Gryc T, Zahalka F, Brožka M, Marenčáková J, Miřátský P, Baca A, Stöckl M. (2023). *Do the Pelvic and Thorax Movements Differ between the Sexes and Influence Golf Club Velocity in Junior Golfers?* Sports, 11(3), 60.
- **DOI·확인 URL:** DOI `10.3390/sports11030060`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10057497/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 주니어 엘리트 14명(남 6·여 8), CODA 3D·200 Hz, 드라이버. 수평면 골반/흉곽 회전 및 continuous relative phase(CRP). 위치: §§2.1–2.4.
- **핵심 결과:** 스윙 시작은 클럽이 타깃 반대로 **0.2 m/s**에 도달할 때, 톱은 클럽 방향 전환 중 속도 0, 임팩트는 클럽 마커의 국소 가속도 피크로 정의(§2.4). 남자에서 X-Factor–클럽 속도 **r=−0.847, p<0.05**, 여자에서는 유의 관계 없음(§3.2, Table 2). 골반이 흉곽을 선행하는 CRP를 보고했으나 이를 클럽 톱 대비 개시 ms로 바꿀 수 없다.
- **Swing.Lab 적용:** **부분**. 이벤트 정의와 작은 성별 집단에서의 상반된 상관을 참고. 클럽 추적이 필요하며 이 X-Factor 관계를 성인 사용자 정상 기준으로 삼을 수 없다.

### C09 — 숙련도별 회전·하중 이동

- **RQ:** RQ2, RQ3
- **서지:** Okuda I, Gribble P, Armstrong C. (2010). *Trunk Rotation and Weight Transfer Patterns between Skilled and Low Skilled Golfers*. Journal of Sports Science and Medicine, 9(1), 127–133.
- **DOI·확인 URL:** DOI 미확인; [학술지 공식 원문 PDF](https://www.jssm.org/volume09/iss1/cap/jssm-09-127.pdf).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 숙련자 13명(핸디캡 **0.8 ± 2.6**)·낮은 숙련자 17명(**30.8 ± 5.5**). 드라이버, 8카메라 3D·240 Hz와 force plate. 위치: p.128, Methods·Table 1.
- **핵심 결과:** 연구가 정의한 downswing 이벤트에서 골반 수평각은 숙련자 **10.1 ± 7.9°**, 낮은 숙련자 **20.7 ± 13.7°**, **p<0.05**(p.130, Table 2). 숙련자는 다운스윙에서 골반 회전과 리드발 하중 이동이 더 이른 패턴을 보였다. 개별 회전 개시 지연시간을 직접 검출한 연구는 아니다. 해당 downswing 이벤트는 리드 손목의 특정 위치로 정의된다(p.130).
- **Swing.Lab 적용:** **부분**. 몸통·골반 및 단계별 이동 패턴은 참고 가능하나 영상상의 중심 이동을 발별 지면반력 또는 체중 분배로 바꿔 보고할 수 없다.

### C10 — 전환·X-Factor stretch의 조작적 정의

- **RQ:** RQ1, RQ2, RQ3
- **서지:** Parker J, Lagerhem C, Hellström J, Olsson MC. (2017). *Effects of nine weeks isokinetic training on power, golf kinematics, and driver performance in pre-elite golfers*. BMC Sports Science, Medicine and Rehabilitation, 9, 21.
- **DOI·확인 URL:** DOI `10.1186/s13102-017-0086-9`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5725976/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** pre-elite 20명(남 13·여 7), 9주 훈련 비교. Polhemus/AMM 4센서·240 Hz, TrackMan, 드라이버. 단안 카메라 실험 아님. 위치: Methods.
- **핵심 결과:** Table 1에서 transition을 분절의 **“lowest angular velocity” 시점**으로 기재하고 X-Factor는 골반 transition 때, stretch는 다운스윙 중 추가 최대 증가로 정의한다. 이를 자동으로 회전각 미분의 부호 전환과 동치라고 해석하지 않았다. 훈련 전 남자 골반/흉곽/리드팔 속도는 각각 **458.3 ± 64.1 / 712.5 ± 74.1 / 1050.5 ± 117.6°/s**(Table 3). 이것만으로 피크 순서·시간차는 알 수 없다.
- **Swing.Lab 적용:** **부분**. 전환·stretch 정의를 명시해야 한다는 근거. 서로 다른 정의로 계산한 X-Factor 수치를 하나의 기준 범위에 섞으면 안 된다.

### C11 — torso–pelvis 분리와 볼 속도

- **RQ:** RQ3
- **서지:** Myers J, Lephart S, Tsai YS, Sell T, Smoliga J, Jolly J. (2008). *The role of upper torso and pelvis rotation in driving performance during the golf swing*. Journal of Sports Sciences, 26(2), 181–188.
- **DOI·확인 URL:** DOI `10.1080/02640410701373543`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A17852693+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 레크리에이션 골퍼 100명, 개인 드라이버, 상체/골반 회전 및 속도 분석·launch monitor. 초록에는 자세 획득 장비와 카메라 배치 미기재.
- **핵심 결과:** 톱의 분리각, 최대 분리각, 상체·분리각 속도 등의 증가가 볼 속도와 **r≥0.50, p<0.001** 수준의 관계를 보였다. 리드팔 수평 및 임팩트 직전 **40 ms** 구간의 속도도 분석했다. **종속변수는 볼 속도**이며 클럽헤드 속도와 구분한다. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 구간별 분리 운동을 볼 이유는 있으나, 화면 기울기 차의 크기를 늘리면 비거리가 증가한다는 인과 근거가 아니다. 단안 축 회전 정확도는 검증하지 않았다.

### C12 — X-Factor 계산법에 따라 달라지는 값·성능 관계

- **RQ:** RQ3, RQ5
- **서지:** Kwon YH, Han KH, Como C, Lee S, Singhal K. (2013). *Validity of the X-factor computation methods and relationship between the X-factor parameters and clubhead velocity in skilled golfers*. Sports Biomechanics, 12(3), 231–246.
- **DOI·확인 URL:** DOI `10.1080/14763141.2013.771896`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A24245049+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 숙련 남자 18명, 핸디캡 **−0.6 ± 2.1**, 드라이버 각 5회, 광학 모션캡처 **250 Hz**. 기존 평면투영·기능적 스윙 평면·Cardan 상대회전 비교. 위치: 초록.
- **핵심 결과:** 계산법별 X-Factor 관련 값이 유의하게 달랐다(**p<0.001**). 기존 방식은 untwisting에서 더 큰 값을 냈다. X-Factor 변수와 최대 클럽헤드 속도 사이 직접 상관은 확인되지 않았다. 위치: 초록. 여기서 평면투영은 3D 데이터에 적용한 계산법으로 스마트폰 영상 실험이 아니다.
- **Swing.Lab 적용:** **부분**. 2D 회전 대안의 타당성을 판단할 방법론 근거. 단안 관절선 기울기 차를 3D X-Factor라 부르는 것을 뒷받침하지 않는다. 효과가 없다는 결론도 모든 숙련도에 일반화하지 않는다.

### C13 — 다변량 운동학·지면반력과 드라이빙

- **RQ:** RQ3
- **서지:** Chu Y, Sell TC, Lephart SM. (2010). *The relationship between biomechanical variables and driving performance during the golf swing*. Journal of Sports Sciences, 28(11), 1251–1259.
- **DOI·확인 URL:** DOI `10.1080/02640414.2010.507249`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A20845215+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 골퍼 308명의 스윙 운동학·GRF, 4개 이벤트별 회귀모델. 숙련도 분포, 장비·카메라 배치 세부는 초록에서 미확인.
- **핵심 결과:** 모델이 볼 속도 분산의 **44–74%**를 설명. X-Factor, 팔·손목 release 지연, 몸통 전경/측경, 하중 이동이 볼 속도와 관련됐다. 위치: 초록. 이 설명력은 X-Factor 단독의 설명력이 아니다.
- **Swing.Lab 적용:** **부분**. 손목 하나 외의 다분절 정보를 고려할 근거. 영상에서 관찰되는 전경·측경도 촬영 방향의 영향을 받으며, GRF와 볼 속도는 현재 관절 입력만으로 직접 측정할 수 없다.

### C14 — 발별 힘·모멘트와 클럽헤드 속도

- **RQ:** RQ3
- **서지:** Han KH, Como C, Kim J, Lee S, Kim J, Kim DK, Kwon YH. (2019). *Effects of the golfer-ground interaction on clubhead speed in skilled male golfers*. Sports Biomechanics, 18(2), 115–134. 동명 이니셜 Kim J 두 명은 각각 Jemin Kim·Jaewoong Kim이다.
- **DOI·확인 URL:** DOI `10.1080/14763141.2019.1586983`; [Europe PMC 공식 초록](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID%3A31042142+AND+SRC%3AMED&format=json&resultType=core&pageSize=1).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 숙련 남자 63명, 핸디캡 ≤3. 드라이버·5번 아이언·피칭웨지, 광학 모션캡처와 force plate 2대. 단안 정면/후방 실험 아님. 위치: 초록.
- **핵심 결과:** 리드발의 GRF moment와 트레일발의 pivoting moment 등이 클럽헤드 속도와 유의하게 관련(**p<0.05**). 리드팔이 지면과 평행해지는 시점을 최대 angular effort 시점으로 해석했다. 실제 상관계수와 피크 힘·모멘트 수치는 미확인. 위치: 초록.
- **Swing.Lab 적용:** **부분**. 리드팔 수평이라는 중간 이벤트는 관찰할 수 있다. 그러나 화면상의 골반 이동 또는 발 위치만으로 이 연구의 GRF·모멘트를 정량 재현하는 것은 **불가**하다.

### C15 — 전신·유연 클럽 모델의 운동역학

- **RQ:** RQ3
- **서지:** Nesbit SM. (2005). *A Three Dimensional Kinematic and Kinetic Study of the Golf Swing*. Journal of Sports Science and Medicine, 4(4), 499–519.
- **DOI·확인 URL:** DOI 미확인; [학술지 공식 초록](https://www.jssm.org/abstresearchajssm-04-499.xml.xml).
- **확인 수준:** 초록만 확인
- **설계·대상·측정:** 다양한 숙련도의 남자 84명·여자 1명. 다중 카메라 모션캡처를 입력으로 전신 인체모델과 유연 클럽 모델 구동. 단안 실험 아님. 위치: 초록.
- **핵심 결과:** 클럽 궤적, 상호작용 힘·토크, 일·파워, 샤프트 변형을 산출했다. 개인차가 크며 손 경로와 일을 하는 능력이 숙련도와 밀접하고 손목이 속도·페이스 방향에 중요하다고 보고했다. 효과크기·힘·토크·에너지 수치는 **초록에서 미확인**. 위치: 초록.
- **Swing.Lab 적용:** **불가**(같은 운동역학량의 정량 재현). 2D 관절만으로 3D 힘·토크·유연 클럽·분절 관성에 필요한 정보를 충족하지 못한다. 포즈의 피크 순서만으로 에너지 전달량을 측정했다는 주장을 뒷받침하지 않는다.

### C16 — 관절의 일과 클럽에 전달된 에너지

- **RQ:** RQ3
- **서지:** Nesbit SM, Serrano M. (2005). *Work and Power Analysis of the Golf Swing*. Journal of Sports Science and Medicine, 4(4), 520–533.
- **DOI·확인 URL:** DOI 미확인; [학술지 공식 원문 PDF](https://www.jssm.org/volume04/iss4/cap/jssm-04-520.pdf).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 아마추어 4명의 각자 선택한 대표 스윙 한 개씩. 6카메라·200 Hz, 전신 다분절·클럽 유연체 모델. 남자 scratch/5/13 핸디캡 및 여자 18 핸디캡. 위치: pp.521–525, Methods·Table 2.
- **핵심 결과:** 척추·고관절의 일은 각 대상 총 신체 일의 **71.8%, 72.2%, 70.0%, 68.7%**(p.527). 클럽 총 일은 **355, 289, 288, 235 N·m**, swing efficiency는 **24.5%, 20.2%, 26.1%, 26.8%**(p.526, Table 3). 효율은 클럽의 일/신체의 총 일이라는 모델 정의이며 일반적인 스윙 점수가 아니다.
- **Swing.Lab 적용:** **불가**(현재 입력으로 일·파워·전달 효율 정량 재현). 골반·흉곽 감속만 보고 전달 에너지를 산출할 수 없다. 소수의 대표 스윙에 기반하므로 인구 정상 범위로 사용하지 않는다. C15와 연구 맥락이 밀접하므로 독립 대규모 검증으로 합산하지 않는다.

### C17 — 골반·흉곽 회전의 기준 측정: IMU 검증

- **RQ:** RQ4, RQ5 (RQ5에는 영상 측정의 직접 검증이 아닌 기준측정 비교 자료)
- **서지:** Kim SE, Burket Koltsov JC, Richards AW, Zhou J, Schadl K, Ladd AL, Rose J. (2023). *Validation of Inertial Measurement Units for Analyzing Golf Swing Rotational Biomechanics*. Sensors, 23(20), 8433.
- **DOI·확인 URL:** DOI `10.3390/s23208433`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10611231/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 36명(프로/아마추어 및 남/녀 각 18), 7번 아이언. T1·L4의 IMU 2개·100 Hz와 10카메라 모션캡처 비교. 108스윙 중 이상치 5개 제외, 103개 분석. 위치: §§2.1–2.4, 3.2.
- **핵심 결과:** X-Factor ICC **0.94**, 골반 회전 ICC **0.99**(Table 2). 골반 회전 평균차 **0.76°**, 일치한계 **−9.57~11.10°**; X-Factor 평균차 **−1.39°**, 일치한계 **−21.35~18.56°**(Table 3). 작은 평균차를 모든 프레임의 작은 오차로 해석하면 안 된다. 톱은 클럽 수직 방향 반전, 임팩트는 볼 속도 증가 직전으로 정의(§2.4).
- **Swing.Lab 적용:** **부분**. 이벤트 정답과 회전 측정의 검증 방법을 참고할 수 있다. **IMU의 검증 결과이지 MediaPipe 정확도가 아니다.** 현재 영상만으로 동일한 측정량을 보장할 수 없다.

### C18 — 단일 IMU의 기계학습 단계 분할

- **RQ:** RQ4
- **서지:** Kim M, Park S. (2020). *Golf Swing Segmentation from a Single IMU Using Machine Learning*. Sensors, 20(16), 4466.
- **DOI·확인 URL:** DOI `10.3390/s20164466`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7472298/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 남자 20명(프로 9·아마추어 11; 아마추어 핸디캡 **15.3 ± 4.3**). 드라이버/7번 아이언 각 10회. 머리·손목·허리 각각의 IMU 200 Hz, 14카메라 모션캡처 기준. BLSTM/CNN, 참가자별 leave-one-out 검증. 위치: §2·초록.
- **핵심 결과:** ADD/BST/IMP/FIN으로 전·백스윙·다운스윙·팔로스루·후 구간 분할. 클럽 위치·속도로 정답 정의(§2.1). 평균 경계 검출오차 **5–92 ms**는 센서 위치·방법·이벤트별 범위(초록). 손목의 가속도+각속도 사용 시 다운스윙 길이 오차: BLSTM **2.9 ± 1.9%**, CNN **2.7 ± 1.8%**(Table 3). 이는 이벤트별 정답률과 다른 지표다.
- **Swing.Lab 적용:** **부분**. 시계열 분류와 피험자 분리 검증은 참고 가능하다. 영상 손목 좌표는 IMU 가속도·각속도와 다른 입력이므로 수치 성능을 이전할 수 없다.

### C19 — 손목 IMU의 이벤트 검출과 궤적 오차는 별개

- **RQ:** RQ4
- **서지:** Kim M, Park S. (2024). *Enhancing accuracy and convenience of golf swing tracking with a wrist-worn single inertial sensor*. Scientific Reports, 14(1), 9201.
- **DOI·확인 URL:** DOI `10.1038/s41598-024-59949-w`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11035581/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 오른손잡이 남자 20명(프로 9·아마추어 11), 드라이버·7번 아이언. 손목 IMU와 광학 모션캡처, BLSTM 단계 검출·CNN 방향 추정·속도/궤적 제약을 통한 drift 보정. 참가자별 leave-one-out. 위치: Methods 이하 실험·학습 절.
- **핵심 결과:** 평균 단계 경계 오차 **38 ± 19 ms**. ADD/FIN **61–69 ms**, BST/IMP **9–15 ms**(Results and discussion–Segmentation of sensor data). 전 스윙 궤적 추적 성능은 약 **17 cm**(초록). 시간 경계 검출 정확도와 공간 궤적 정확도는 동일하지 않다.
- **Swing.Lab 적용:** **부분**. 이벤트별 시간오차를 나눠 보고하는 근거. 단안 골반 회전 개시 검증은 아니다. C18과 같은 참가자 수·구성을 보고하므로 두 논문을 독립된 40명 표본으로 합산하지 않는다. 실제 데이터 공유 범위는 미확인.

### C20 — 단안 골프 영상·손목 높이 기반 이벤트의 선행 사례

- **RQ:** RQ4, RQ5
- **서지:** Yamamoto K, Hasegawa Y, Suzuki T, Suzuki H, Tanabe H, Fujii K. (2023). *Extracting proficiency differences and individual characteristics in golfers' swing using single-video markerless motion analysis*. Frontiers in Sports and Active Living, 5, 1272038.
- **DOI·확인 URL:** DOI `10.3389/fspor.2023.1272038`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10684732/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 다양한 숙련도의 대학 골퍼 27명(여 9·남 18), 7번 아이언 20회. 공에서 타깃선 뒤쪽 **3.5 m**, 몸의 시상면을 보는 후방(DTL에 해당) 영상 **240 Hz**, HRNet 17관절·DeepLabCut 클럽 검출. 위치: §§2.1–2.3.
- **핵심 결과:** 오른 손목 높이의 최대/최소로 톱·임팩트·피니시를 찾는다. 어드레스는 상승 검출 전 **30프레임(0.125 s)**(§2.3.3). 전경각의 스윙 내 변동과 평균 타수의 상관은 **r=0.595, p<0.01**(§3.1.1). 이것은 이벤트 검출 정확도가 아니다. 인용한 방법·결과에서 모션캡처 대비 골반 축 회전 오차는 보고되지 않는다.
- **Swing.Lab 적용:** **부분**. 현재 손목 높이 방식과 유사한 선행법이 존재한다. 그러나 연구에 사용됐다는 사실만으로 손목 최저점이 실제 접촉 프레임이라는 정확도 보장은 없다.

### C21 — MediaPipe·OpenPose와 Vicon 비교: 골프 외 간접 근거

- **RQ:** RQ5
- **서지:** Menychtas D, Petrou N, Kansizoglou I, Giannakou E, Grekidis A, Gasteratos A, Gourgoulis V, Douda E, Smilios I, Michalopoulou M, Sirakoulis GC, Aggelousis N. (2023). *Gait analysis comparison between manual marking, 2D pose estimation algorithms, and 3D marker-based system*. Frontiers in Rehabilitation Sciences, 4, 1238134.
- **DOI·확인 URL:** DOI `10.3389/fresc.2023.1238134`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10511642/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 건강한 고령자 **17명, 69 ± 5세**, 트레드밀 보행. Vicon 10카메라와 동기화한 시상면 RGB 영상 각 **100 Hz**, OpenPose·MediaPipe·Kinovea의 엉덩/무릎/발목 각도 비교. 위치: §§2.1–2.3.
- **핵심 결과:** MediaPipe는 가려진 다리가 교차하는 구간에서 좌우 관절 혼동·skeleton flicker를 보였고 무릎 지지기 등에 큰 변동이 있었다. OpenPose도 관절별 정확도 차이가 있었다. 위치: §§3.2–3.3, Figs.5–8. 골프 축 회전 오차의 수치로 쓸 값은 **미확인**.
- **Swing.Lab 적용:** **부분**. 좌우 바뀜·가림을 검증 항목으로 삼을 근거. 보행 각도 결과를 고속 골프·골반 회전·현행 MediaPipe 모델 성능으로 직접 일반화할 수 없다.

### C22 — GolfDB·SwingNet: 이벤트 정답과 벤치마크

- **RQ:** RQ4, RQ6
- **서지:** McNally W, Vats K, Pinto T, Dulhanty C, McPhee J, Wong A. (2019). *GolfDB: A Video Database for Golf Swing Sequencing*. IEEE/CVF CVPR Workshops (CVSports). 출판본 쪽 미확인; 확인한 저자 공개본은 10쪽.
- **DOI·확인 URL:** 출판 DOI 미확인; [저자 공개 논문 PDF](https://arxiv.org/pdf/1903.06528), [공식 저장소 설명](https://raw.githubusercontent.com/wmcnally/golfdb/master/README.md).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 영상 **1,400개**, 선수 **248명**, 정면/DTL/기타·일반속도/슬로모션. 영상 CNN+BiLSTM으로 이벤트 검출. 위치: §§4.1–4.2.
- **핵심 결과:** 이벤트는 어드레스(움직임 직전), toe-up(백스윙 샤프트 수평), mid-backswing(팔 수평), 톱(클럽 방향 반전), mid-downswing(팔 수평), 임팩트(클럽–볼 접촉), mid-follow-through(샤프트 수평), 피니시(최종 자세 해제 직전)이다(§3, p.3). **PCE**는 허용 프레임 오차 안의 검출 비율. 허용치 `δ=max(round(n/f),1)`, `n=어드레스~임팩트 프레임 수`, `f=샘플링 주파수`; 동일 원본 YouTube 영상은 같은 split에 배치하고 4 split 평균으로 평가(§4.3, pp.4–5). Table 2(p.8)의 전체 PCE **76.1%**, 임팩트 **98.4%**.
- **공개·라이선스:** 공식 README는 **코드에 CC BY-NC 4.0**을 명시한다. 이를 원본 YouTube 영상의 권리·상업 이용 허가로 확대하지 않는다. 데이터/영상의 별도 포괄적 이용 허가는 미확인. 배포 모델은 증강 없는 split 1 **71.5%**로 논문 수치와 다르다(README Introduction).
- **Swing.Lab 적용:** **가능**(영상 이벤트 평가), 모델 적용은 **부분**. MediaPipe 골반 축 회전·골반 전환 정답 데이터는 아니다.

### C23 — GolfSwing 데이터셋·GolfPose의 2D→3D 복원

- **RQ:** RQ5, RQ6
- **서지:** Lee MH, Zhang YC, Wu KR, Tseng YC. (2025). *GolfPose: From Regular Posture to Golf Swing Posture*. Pattern Recognition, ICPR 2024, LNCS 15321, 387–402. 출판사 서지연도 2025, 온라인 공개 2024-12-04.
- **DOI·확인 URL:** DOI `10.1007/978-3-031-78305-0_25`; [출판사 서지](https://link.springer.com/chapter/10.1007/978-3-031-78305-0_25), [저자 공식 원문 PDF](https://minghanlee.github.io/papers/ICPR_2024_GolfPose.pdf), [공식 README](https://raw.githubusercontent.com/MingHanLee/GolfPose/main/README.md), [데이터 EULA](https://raw.githubusercontent.com/MingHanLee/GolfPose/main/LICENSE).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 학생 6명, 7번 아이언, 정제 스윙 **20개·17,738프레임**. Vicon 9대와 정면/측면 RGB 2대 동기화; 인체 17점·클럽 5점 정답. 참가자 4명 학습/2명 시험. 위치: §3.1, Fig.2, 공개본 pp.4–6.
- **핵심 결과:** MixSTE 인체 MPJPE **109.4→35.6 mm**, 클럽을 함께 학습하면 인체 **32.3 mm**(§4.2, Table 1, p.9). **평가 입력은 추정 포즈가 아닌 2D 정답 좌표**다. 단안 영상 전체 파이프라인·MediaPipe·골반 축 회전각의 오차로 인용할 수 없다. 지표는 2D mAP@OKS와 3D MPJPE(§4.1).
- **공개·라이선스:** README상 이메일 다운로드 승인 필요. 현행 맞춤 EULA는 내부 연구·평가·모델 학습 및 파생 모델 상용화를 허용한다. 원시 데이터 재배포·재판매·재식별·승인 오인 표시는 금지하고 출처 표기를 요구한다(§§1–3). 실제 다운로드는 하지 않았다.
- **Swing.Lab 적용:** **부분**. 골프 특화 3D 복원·포즈 평가의 직접 근거. 33점→논문 관절 정의 매핑과 실제 추정 2D 입력 검증이 필요하다.

### C24 — CaddieSet: 포즈 특징과 볼 결과를 짝지은 데이터

- **RQ:** RQ4, RQ5, RQ6
- **서지:** Jung S, Hong S, Jeong J, Jeong S, Choi J, Kim H, Lee W. (2025). *CaddieSet: A Golf Swing Dataset with Human Joint Features and Ball Information*. IEEE/CVF CVPR Workshops (CVSports), 5988–5996. 서지 쪽은 공식 저장소 인용정보; 읽은 arXiv 공개본에는 보충자료 포함.
- **DOI·확인 URL:** 출판 DOI 미확인; [저자 공개 논문 PDF](https://arxiv.org/pdf/2508.20491), [공식 저장소](https://github.com/damilab/CaddieSet), [라이선스 원문](https://raw.githubusercontent.com/damilab/CaddieSet/main/LICENSE).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 논문은 8명의 정면 **924샷**, launch monitor의 볼 정보와 SwingNet 이벤트·HRNet 17관절 특징을 결합(§3.1–3.3, pp.3–4). 모션캡처 정답이 아닌 모델 추정 특징이다.
- **핵심 결과·지표:** 학습/시험 **739/185샷**; 방향각·스핀축 분류는 Acc/AUC, 볼 속도 회귀는 MSE(§4, p.5). NAM의 볼 속도 MSE **9.72**(Table 2, p.6). 이는 자세·회전각 정확도가 아니다. 별도 이벤트 모델 정확도 **78.0%**는 Supplement A(p.10)의 결과다.
- **공개·라이선스:** 현재 공식 README는 **1,757샷=정면 924+DTL 833**이라고 기재한다. 논문의 924샷 실험과 합치지 않는다. 저장소 LICENSE는 **MIT**이며 대상 표현은 software/associated documentation이다. 원본 영상 전체 제공 여부·별도 영상 권리 범위는 미확인.
- **Swing.Lab 적용:** **부분**. 결과 예측 벤치마크로 활용 가능하다. `HIP-ROTATION`·`WEIGHT-SHIFT`라는 특징명만으로 실제 축 회전·GRF의 검증된 정답이라고 취급할 수 없다.

### C25 — 골반 전환과 클럽 전환을 분리한 14이벤트

- **RQ:** RQ2, RQ3, RQ4
- **서지:** Kim SE, Lee J, Lee SY, Lee HD, Shim JK, Lee SC. (2021). *Small changes in ball position at address cause a chain effect in golf swing*. Scientific Reports, 11(1), 2694.
- **DOI·확인 URL:** DOI `10.1038/s41598-020-79091-7`; [Europe PMC 공식 원문 XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7846748/fullTextXML).
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 남자 프로 20명, 5번 아이언. 공 위치를 기준 및 좌우 **2.14/4.27 cm**로 바꾸어 각 5회. Vicon 8카메라 **250 Hz**, force plate 2대 **2000 Hz**. 위치: Methods–Participants/Instrumentation/Procedures.
- **핵심 결과:** 어드레스–임팩트 **14이벤트**에 **TP(골반 회전 방향 반전)**와 **TC(클럽헤드 좌우 방향 반전)**를 따로 포함했다. 하체 다운스윙 개시가 클럽 방향 반전보다 앞설 수 있어 TP를 추가했다. 중간 이벤트는 샤프트의 YZ평면 각도로 정의(Methods–Data analysis, Fig.2). 공 위치에 따른 하중·자세 차이가 백스윙에서 줄고 다운스윙에 재출현(초록). TP–TC 간 평균 ms는 확인한 내용에서 미확인.
- **Swing.Lab 적용:** **부분**. 골반 전환을 손목/클럽 톱과 구분할 직접적인 조작적 근거. 단안 2D에서는 골반의 실제 축 회전 방향을 검증해야 하며, 샤프트 기반 중간 이벤트에는 클럽 추적이 필요하다.

### C26 — 2D 평면투영과 3D 몸통·골반 회전 비교

- **RQ:** RQ3, RQ5
- **서지:** Smith AC, Roberts JR, Wallace ES, Kong PW, Forrester SE. (2016). *Comparison of Two- and Three-Dimensional Methods for Analysis of Trunk Kinematic Variables in the Golf Swing*. Journal of Applied Biomechanics, 32(1), 23–31.
- **DOI·확인 URL:** DOI `10.1123/jab.2015-0032`; [Ulster 대학 공식 저자 공개본 PDF](https://pure.ulster.ac.uk/ws/portalfiles/portal/11647474/Comparison_of_2d_and_3d_methods_for_analysis_of_trunk_-_IR2.pdf). 저장소 표지의 축약 저자 목록 대신 논문 내부 저자열을 사용했다.
- **확인 수준:** 본문 확인
- **설계·대상·측정:** 오른손잡이 15명, 핸디캡 1–29, 드라이버. Vicon 13카메라·250 Hz 자료를 실험실 평면에 투영한 2D 각도와 3D 분절각 비교. **스마트폰 단안 포즈추정 실험은 아니다.** 위치: Methods, PDF p.3.
- **핵심 결과:** 톱의 X-Factor `2D−3D` 차이는 **−16.72 ± 6.20°**(연구 부호 convention; Results, PDF p.7). 굴곡·측굴과 회전이 투영 차이에 관여했다. 단안 기울기의 오차가 항상 이 값이라는 뜻은 아니다. 회전·X-Factor의 2D 정의는 **수평면 투영**이며 카메라 화면상의 관절선 기울기와 구분된다(Table 1, PDF p.5).
- **Swing.Lab 적용:** **부분**. 영상 평면 기울기에서 해부학적 축 회전을 추론할 때의 구조적 한계를 설명하는 근거. 일률적으로 16.72°를 빼는 보정식이나 화면 기울기 차를 X-Factor로 치환하는 근거가 아니다.

## 조사 범위 안에서 남은 미확인 사항

- **RQ1:** 단일 정상 순서·정상 ms 간격은 확정하지 않았다. C06의 피크 간격은 골반부터 손까지의 특정 성분·필터·측정 조건에 한정된다. C01의 손, C04의 샤프트, C06의 손/전완을 같은 클럽 변수로 합치지 않았다.
- **RQ2:** 골반 회전 반전, 골반 병진 개시, 클럽 톱, 손목 높이 톱은 다른 이벤트다. C25는 TP/TC 분리 근거를 제공하지만 모든 골퍼에게 적용할 선행시간 임계값은 확보하지 못했다. C07처럼 톱 자체를 골반 반전으로 정의하는 연구는 클럽 톱 대비 선행 검증에 그대로 사용할 수 없다.
- **RQ3:** X-Factor와 성능의 관계는 표본·정의·종속변수에 따라 다르다. 볼 속도와 클럽헤드 속도를 구분했다. 관절 일·파워의 모델 결과는 확보했으나, 단안 관절만으로 분절 간 **각운동량 전달량**을 직접 검증한 수치는 미확인이다.
- **RQ4:** 프레임 이벤트(PCE), 경계 시간오차(ms), 구간 길이오차(%)를 섞지 않았다. 골반 전환은 GolfDB의 독립 라벨이 아니다. 손목 최저점 방식에는 선행 연구 C20이 있지만 실제 임팩트 접촉 프레임 대비 정확도는 별도 확인이 필요하다.
- **RQ5:** 골프에서 **MediaPipe 자체의 골반·흉곽 축 회전각 및 개시 시점**을 모션캡처와 직접 비교한 충분한 검증 근거는 이번 조사에서 확보하지 못했다. C21은 골프 외 연구, C17은 IMU 연구다. 어깨폭/골반폭 투영비만으로 절대 축 회전각을 구하는 방법과 MediaPipe 추정 깊이의 해당 용도 정확도는 미확인이다. 동일 골퍼·동일 동작에 대한 정면 대 DTL의 회전각 오차 차이도 확정하지 않았다. C23의 2D 정답 입력 MPJPE를 일반 스마트폰 영상의 최종 오차로 보고하지 않았다.
- **RQ6:** GolfDB는 이벤트, GolfSwing은 포즈, CaddieSet은 포즈 특징–볼 결과라는 서로 다른 평가 대상을 제공한다. 공개 원문이 있다고 데이터가 무조건 자유 이용인 것은 아니다. 코드·데이터·원본 영상의 권리 범위를 나눠 기록했으며 데이터 다운로드·이메일 요청은 수행하지 않았다.

## 접근·독립성·완료 점검

- 검색 경로: RQ별 영문 키워드 검색 → 논문/공식 초록 열기 → 관련 참고문헌 추적 → 공식 원문/API·저자본 확인. 모든 결과를 수집한 체계적 문헌고찰이나 메타분석으로 주장하지 않는다.
- 접근 제약: 일부 PMC 웹페이지는 CAPTCHA, MDPI는 403/429, CVF 일부 URL은 403, IEEE 일부 페이지는 로봇 확인 화면을 반환했다. 공개 원문 API/저자본으로 내용을 실제 확인한 경우에만 본문으로 집계했다. 원문이 없는 항목은 초록 범위로 제한했다. 유료 접근을 우회하지 않았다.
- 본문 확인 ID: **C06, C07, C08, C09, C10, C16, C17, C18, C19, C20, C21, C22, C23, C24, C25, C26**.
- 초록만 확인 ID: **C01, C02, C03, C04, C05, C11, C12, C13, C14, C15**.
- **26편 / RQ별 최소 3편 충족 / 본문 16편 / 초록 10편 / 웹 검색 사용 가능.** `01_claude_findings.md` 미열람. 산출물은 이 파일 한 개이며 분석 코드·테스트·git 커밋을 변경하지 않았다.
