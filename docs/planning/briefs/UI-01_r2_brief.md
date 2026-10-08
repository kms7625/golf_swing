# UI-01 r2 — 첫 화면 새 디자인 A/B 브리프

- 작성일: 2026-10-08. 상태: **DRAFT / 이미지 승인 없음**.
- 작업 근거: [새 시안 지시문](../codex-ui01-fresh-prompt.md) 전체, [UI_STRUCTURE](../UI_STRUCTURE.md)의 작업군·UI-01 카드, [STATE](../STATE.md)의 DEC-01(revision 2, 내 영상 바로 업로드), [Nielsen 평가](../eval/NIELSEN_EVAL.md)의 UI-01 발견, [i18n KO](../../../web/src/lib/i18n.tsx).
- 형식 근거: Planning_Agents_v3.0/01_PROJECT_MD/05_VISUAL_APPROVAL.md §3·4. D05-02의 기존 시각 참고 확보는 이번 사용자의 기존 화면 비참조 지시로 적용하지 않는다.
- 기존 스크린샷·시안·웹 이미지·현재 CSS·redesign-proposal은 열지 않으며 생성 도구에 참조 이미지도 제공하지 않는다. 구조·문구만 활용한다.
- 대상: 스마트폰으로 자기 스윙을 찍어 보는 20대 골퍼. 상태: 로그인 전, 업로드 전, 키보드 초점이 주 버튼에 있는 대표 상태.
- 연결 작업군: REQ-01(시작), REQ-05(기록), REQ-08(이동), REQ-09(키보드·기기).
- 생성 방식: 기본 내장 image_gen, A/B 별도 호출, 참조 이미지 인수 없음. 목표는 각각 2048×1152, 정확한 16:9 단일 데스크톱 화면. 실제 치수·SHA-256·차이는 검토 문서에 기록한다.

## 공통 문구 계약

| 영역 | 정확한 표시 문구 | 근거 |
|---|---|---|
| 브랜드 표기 | Swing.Lab | 프로젝트 이름을 일반 텍스트로 표시, 브랜드 로고 자산 없음 |
| 상단 | 실시간 캠 / 내 기록 / 로그인 | nav_live / nav_history / auth_login |
| 테마 | 테마 | 짧은 기능 라벨; 접근 가능한 이름은 기존 theme_toggle의 ‘밝은/어두운 테마 전환’ 사용 제안 |
| 언어 | KO / EN | 요청된 공통 메뉴, KO 선택 상태 |
| 제목 | 골프 스윙을 / 계측 장비처럼 읽는다 | hero_title_1 / hero_title_2 원문 |
| 설명 | 내 영상으로 스윙의 흐름을 확인하고, / 다음 연습에서 바꿀 점을 찾아보세요. | **신규 문구 후보**, hero_lede 대안, NE-15 결과 중심 설명 |
| 주 행동 | 영상 업로드 | hero_cta_upload 원문 |
| 보조 행동 | 샘플 데이터 보기 | hero_cta_sample 원문 |
| 촬영 안내 | 전신이 보이는 한 번의 스윙 영상을 준비해 주세요. | **신규 문구 후보**, NE-20 대응 안내 |
| 그래픽 표기 | 이미지 예시 | **신규 문구 후보**, 생성 장면의 예시 성격 표시 |
| 기록 | 내 스윙 기록 | history_title 원문 |
| 기록 안내 | 로그인하면 분석 결과를 저장하고 변화를 추적할 수 있습니다. | history_login_hint 원문 |
| 기록 진입 | 내 기록 | nav_history 원문 재사용 |

i18n 파일은 수정하지 않는다. 제목은 현재 KO 원문을 유지하므로 ‘계측 장비’라는 표현은 남아 있으며, 새 설명의 이해도 개선은 사용자 검증 전 가설이다. 현재 hero_eyebrow·기술 용어 중심 hero_lede·기존 이미지 대체 텍스트는 시안에 사용하지 않는다. 테마의 짧은 표시 라벨과 새 이미지의 대체 텍스트는 구현 시 번역·접근 가능한 이름 정의가 필요하다.

## 방향 A — 플레이 코트

**한 줄 콘셉트:** 밝은 코트의 에너지와 큰 업로드 버튼으로 내 영상의 분석 시작을 빠르게 안내한다.

1. **화면 목적 / 첫 행동 / 지원 기기와 화면 비율**  
   UI-01에서 영상 업로드 → UI-02를 가장 먼저 인지한다. 16:9 데스크톱 한 장, 비회원 첫 방문. 모바일은 이번 이미지 범위 밖이며 추후 설명 → 업로드 → 샘플 → 기록 순서로 재배치한다.
2. **상단·주 영역·보조 영역·하단의 구체 배치**  
   상단 약 10% 높이에 텍스트 브랜드와 필수 메뉴. 주 영역 왼쪽 약 57%에 큰 제목, 결과 중심 설명, 업로드, 보조 샘플, 촬영 안내를 왼쪽 정렬한다. 오른쪽 약 35%에 익명 골퍼의 사진형 생성 장면 한 개. 하단 약 18%에 옅은 파랑 기록 띠, 안내와 기록 진입. 비율은 설계 목표이며 측정 결과가 아니다.
3. **정확한 제목·라벨·버튼·대표 데이터**  
   위 공통 문구 계약 전부 사용. 제목은 2줄. 사진에는 ‘이미지 예시’ 표시. 개인 기록·스코어·계측 수치 없음. 생성 장면과 이미지 속 수치·데이터가 생길 경우 모두 **예시**이며 실제 분석 결과가 아니다.
4. **컴포넌트 형태·정보 밀도·색/글자 역할**  
   흰 바탕 #FFFFFF, 코발트 #2448D8 주 버튼, 짙은 남색 #152040 글자, 옅은 파랑 #ECF1FF 기록 배경을 새로 제안한다. 굵은 현대 고딕 제목, 편안한 본문 행간. 업로드는 큰 둥근 사각형 채움 버튼, 샘플·로그인·기록은 작고 조용한 외곽선 버튼. 업로드 바깥에 흰 간격과 남색 초점선을 함께 표시한다. 코드 토큰에서 가져온 값이 아니며 PNG의 실제 픽셀색과는 차이가 있을 수 있다.
5. **참고 이미지에서 유지할 것 / 바꿀 것**  
   참고 이미지 없음. 내용·구조인 DEC-01과 필수 메뉴·기록 진입만 유지한다. B와 비교해 색(흰색·코발트), 서체(굵은 고딕), 배치(비대칭 좌우), 그래픽(사진형 장면), 버튼(둥근 사각형)이 다르다.
6. **이번 이미지에 넣지 않을 기능·자산**  
   실제 인물·특정 선수·실존 브랜드 로고·기존 프로젝트 이미지·사용자 영상·허구의 개인 점수·결제·계정 삭제·결과 화면·콜라주를 넣지 않는다.
7. **이번 기획의 현재 구조 revision**  
   새 시각 시안 r2-A / DRAFT. 공통 구조는 사용자 지시와 DEC-01 revision 2. UI_STRUCTURE 원본은 최초 revision 1 기록이므로 그 미결 표기는 DEC-01의 현재 결정으로 해석한다. STATE의 UI revision·승인·ASSET 레코드는 생성하거나 변경하지 않는다.

## 방향 B — 스윙 노트

**한 줄 콘셉트:** 차분한 골프 노트처럼 중앙의 업로드 행동과 짧은 설명에 시선을 모은다.

1. **화면 목적 / 첫 행동 / 지원 기기와 화면 비율**  
   UI-01에서 영상 업로드 → UI-02를 가장 먼저 인지한다. 16:9 데스크톱 한 장, 비회원 첫 방문. 모바일 순서는 A와 같은 기능 우선순위를 제안하며 이번에는 생성·검증하지 않는다.
2. **상단·주 영역·보조 영역·하단의 구체 배치**  
   상단 약 10% 높이에 공통 메뉴. 주 영역은 중앙 정렬 제목 → 설명 → 업로드 → 작은 샘플 → 촬영 안내의 수직 구성이다. 그 아래 낮고 넓은 잉크 드로잉 띠를 두어 골퍼·클럽 궤적·공을 장식으로 표현한다. 하단은 얇은 가로선으로 구분한 평평한 기록 영역이며 왼쪽에 제목·안내, 오른쪽에 기록 버튼. 모든 요소를 한 화면에 담고 주 버튼 주위의 여백을 확보한다.
3. **정확한 제목·라벨·버튼·대표 데이터**  
   위 공통 문구 계약 전부 사용. 제목 2줄, 드로잉 옆 ‘이미지 예시’. 그래픽은 동작의 인상을 전달하는 장식이며 측정 그래프가 아니다. 이미지 속 수치·데이터가 생길 경우 모두 **예시**이며 실제 분석 결과가 아니다.
4. **컴포넌트 형태·정보 밀도·색/글자 역할**  
   크림 #FAF5EB 배경, 가지색 #49315F 글자·주 버튼, 복숭아색 #F4D9CA와 베이지 #ECE2D1의 장식을 새로 제안한다. 제목·기록 제목은 현대 명조 느낌, 본문·메뉴는 고딕. 업로드는 큰 알약형, 보조 버튼은 작고 얇은 외곽선. 업로드에 흰 간격과 가지색 초점선을 표시한다. 넓은 여백과 낮은 정보 밀도. 색·글꼴은 설계 제안이며 실제 폰트 파일 사용·정확한 색상 구현을 주장하지 않는다.
5. **참고 이미지에서 유지할 것 / 바꿀 것**  
   참고 이미지 없음. 사용자 지시의 기능·DEC-01만 유지. A와 비교해 색(크림·가지색), 서체(명조 제목), 배치(중앙 수직), 그래픽(평면 잉크 일러스트), 버튼(알약형)이 다르다.
6. **이번 이미지에 넣지 않을 기능·자산**  
   사진·3D 인체·관절점 HUD·측정 그래프·실존 인물·브랜드 로고·선수·기존 이미지·개인 점수·결제·계정 삭제·다른 화면 콜라주 없음.
7. **이번 기획의 현재 구조 revision**  
   새 시각 시안 r2-B / DRAFT. 공통 구조는 사용자 지시와 DEC-01 revision 2이며 승인·STATE revision·ASSET 레코드를 새로 만들지 않는다.

## 동작·접근성 인계 경계

- 시안의 업로드는 사진 속 장식이 아닌 독립 버튼으로 설계한다. 구현 시 실제 `button type="button"`, 보이는 초점, Enter/Space 활성화로 UI-02 파일 선택 흐름에 연결해야 한다. **PNG는 실제 DOM 버튼이나 키보드 작동을 증명하지 않는다.** 이번 작업은 코드 수정 금지이므로 시각 표현과 동작 요구만 기록한다.
- 샘플은 보조 버튼, 상단 실시간 캠·내 기록·테마·KO/EN·로그인과 하단 기록 진입은 유지한다. 로그인 전 기록 진입 시 인증 안내가 필요하며 로그인이 업로드의 선행 조건인 것처럼 보이지 않게 한다.
- NE-01·04의 샘플 로딩·중복 실행·늦은 응답 무효화, NE-09의 빈 상태/오류 분리, NE-07 이동 복원은 구현·동작 검수 대상이다. 정적 첫 화면만으로 해결했다고 판정하지 않는다.
- 대비, 초점 가림, 읽기 순서, 보조기술 이름, 터치 영역, 축소·모바일·EN 전환은 구현 후 검증한다. 사진·일러스트는 예시 장식이며 사용자 기록이 아니다.

## 실제 이미지 생성 입력 A

```text
Use case: ui-mockup.
Create ONE high-fidelity desktop website first-screen design for a golf swing video analysis app, for Korean golfers in their 20s who record swings on smartphones. Brand text is plain "Swing.Lab", no logo. A single full-bleed rectangular screenshot, exactly 2048 x 1152 pixels, 16:9 landscape. No browser frame, no device mockup, no collage, no multiple screens. Create from scratch with NO reference images.
Direction A: "플레이 코트". Bright white canvas, vivid cobalt blue #2448D8 accents, near-black navy #152040 text, pale blue #ECF1FF supporting surfaces. Energetic, clean sports editorial design with heavy modern Korean sans-serif typography. Large generous whitespace, crisp alignment, no gradients. The main upload button is the strongest colored interaction.
Layout: top full-width navigation about 10% of canvas height, plain app name left; right navigation labels, exactly: "실시간 캠", "내 기록", sun/moon outline icon with visible label "테마", "KO / EN" with KO selected, small quiet "로그인" button. All readable with ample spacing.
Main area is asymmetrical split: left 57% contains the content and actions, right 35% contains ONE tall editorial golf photograph. Big left-aligned headline in two lines, exactly "골프 스윙을" then "계측 장비처럼 읽는다". Under it set this exact short readable Korean description in two lines: "내 영상으로 스윙의 흐름을 확인하고," then "다음 연습에서 바꿀 점을 찾아보세요."
Below the description, render a large solid cobalt rounded-rectangle primary button with an upload icon and the exact label "영상 업로드" in white. Its keyboard focus must be clearly visible: solid dark navy outer focus ring, offset by a thin WHITE gap around the entire button. This is a distinct UI button, not a pictorial control on the photo. Immediately below it, smaller and quieter outlined secondary button with exact text "샘플 데이터 보기". Under these controls, small but legible helper text "전신이 보이는 한 번의 스윙 영상을 준비해 주세요."
Right photograph: an entirely fictional anonymous young adult golfer in unbranded everyday sportswear, seen in three-quarter rear view, full body including feet and whole club visible, at a sunlit practice range. Natural candid sports photography, believable anatomy, warm sunlight, no famous person, no logos, no measurement overlays. Small label on this photo says exactly "이미지 예시". Keep photo subordinate to primary action.
Bottom about 18% of canvas is an understated pale-blue horizontal history section inside page margins, separated from hero by generous space. Left exact heading "내 스윙 기록"; below exact sentence "로그인하면 분석 결과를 저장하고 변화를 추적할 수 있습니다." On far right a quiet outlined control "내 기록" with arrow.
Render all Korean text EXACTLY, crisply and without malformed glyphs. Body text comfortably readable, generous line-height, buttons comfortable sized. No fabricated stats, no score, no chart, no extra English slogan, no extra UI features, no watermark. Only one complete desktop screen.
```

## 실제 이미지 생성 입력 B

```text
Use case: ui-mockup.
Create ONE high-fidelity desktop website first-screen design for a golf swing video analysis app, for Korean golfers in their 20s who record swings on smartphones. Brand text is plain "Swing.Lab", no logo. A single full-bleed rectangular screenshot, exactly 2048 x 1152 pixels, 16:9 landscape. No browser frame, no device mockup, no collage, no multiple screens. Create from scratch with NO reference images.
Direction B: "스윙 노트". Warm cream #FAF5EB canvas with dark aubergine #49315F text and primary action, muted peach #F4D9CA and warm beige #ECE2D1 illustration accents. Calm editorial golf journal, restrained and tactile. Elegant contemporary Korean serif (Myeongjo-style) for headline and section headings, highly readable sans-serif for body and navigation. Flat solid colors, fine rules, no gradients, no photography.
Layout is strongly CENTERED and vertically composed, wide whitespace. Top navigation about 10% of height has plain app name left; right navigation labels exactly "실시간 캠", "내 기록", sun/moon outline icon with visible label "테마", "KO / EN" with KO selected, and a quiet "로그인" button.
Main headline centered near top of hero, two lines exactly "골프 스윙을" then "계측 장비처럼 읽는다" in large dark aubergine Korean serif. Beneath it centered readable description: "내 영상으로 스윙의 흐름을 확인하고," then "다음 연습에서 바꿀 점을 찾아보세요."
Immediately below description is the central main action: a large aubergine pill-shaped button with upload icon and exact white text "영상 업로드". Clearly draw its keyboard focus as a dark aubergine outer ring separated from the filled button by a WHITE gap, all the way around. It must read as a real distinct interactive UI button. Beneath it a small quiet outlined secondary pill button "샘플 데이터 보기". Then one line of readable helper text "전신이 보이는 한 번의 스윙 영상을 준비해 주세요."
Below action block use a LOW, wide decorative hand-drawn illustration strip, balanced around the center: a single fictional anonymous young adult golfer rendered in minimal aubergine ink lines and flat peach shapes, a thin graceful club swing arc and a small ball on a tee. Full-body figure, coherent anatomy. Keep it small enough that primary button retains strongest visual emphasis. No joint dots, no statistics, no data chart, no 3D mannequin, no famous person, no branding. Near the illustration small exact label "이미지 예시". This strip is integrated into the cream page, no giant card.
Bottom history area is a flat full-width cream section divided by one delicate horizontal rule, with left serif heading "내 스윙 기록" and smaller sentence "로그인하면 분석 결과를 저장하고 변화를 추적할 수 있습니다." Right end has a quiet outlined button "내 기록" with arrow. Keep all this fully visible within the desktop viewport.
Render all Korean text EXACTLY, crisply and without malformed glyphs. Ensure all text is large enough to read, margins generous, nothing overlaps, touch targets comfortable. No fabricated scores, no invented data, no extra English slogan, no other features, no watermark. Only one complete desktop screen.
```

