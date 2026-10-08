# Swing.Lab 비주얼 에셋 배치 계획 · 2단계 적용 보고

2026-10-08 · **H1 + E1 + SVG 아이콘 12개 + D1·D3·D4 적용 완료. 완료 기준 1~5 PASS, 6 미확인. 커밋하지 않음.**

사용자가 추천 조합을 확정했으므로 2단계를 수행했다. H2·D2·D5는 적용하지 않았다.
기준 커밋은 `c7e8366d22b2dd8b3ffbc17d8e60f2e3143488f3`이며 작업 전 추적 파일 변경은 없었다.
기존 미추적 `.DS_Store`, `docs/codex-visual-assets-prompt.md`, `docs/visual-candidates/`, `docs/visual-plan.md`는 사용자 지시에 따라 완료 기준 3 판정에서 제외했다.

## 적용 범위와 읽은 자료

- `docs/codex-visual-assets-prompt.md`, 이전 `docs/visual-plan.md`, `docs/codex-redesign-prompt.md` R1~R10, `docs/redesign-proposal.md` 토큰 표.
- `CLAUDE.md`, 프로젝트 및 전역 `golf-ui-ux/SKILL.md`, `verify-work/SKILL.md`, 현재 토큰·컴포넌트·히어로/결과 스크린샷.
- 웹 `web/`의 이미지·SVG·마크업·CSS와 KO/EN 문자열만 수정했다. API·상태 판정·대표 프레임·샘플·화면 흐름·패키지·LiveCapture 로딩 방식은 변경하지 않았다(B1~B6).
- 원본 후보와 생성 기록은 그대로 보존했다. 이번 단계는 기존 PNG의 리사이즈·WebP 변환이며 새 AI 이미지 생성은 하지 않았다.

## 선택 및 실제 배치

| 항목 | 적용 위치와 동작 |
|---|---|
| H1 | `Hero.tsx`의 막대 인형 SVG를 `/images/hero-swing.webp`로 교체. `width="1152" height="864"`, eager 기본 로딩, `object-fit: contain`으로 전체 클럽·발 보존 |
| HTML 계측값 | `SPINE 29.4° / SHOULDER 64.2° / FRAME 0187/0266`를 기존 HTML span에 유지. 패널 하단 64px을 그림·그라데이션 영역에서 제외하고 문구 뒤에는 불투명 카드 토큰 사용 |
| E1 업로드 | 기존 `!file || !videoUrl` 분기 안에만 배치. 데스크톱 160px, 640px 이하 128px 정사각형 |
| E1 빈 기록 | 기존 로그인 이후 `!loading && rows.length === 0` 분기 안에만 배치. 데스크톱 120px, 640px 이하 104px 정사각형 |
| E1 속성 | 같은 `/images/first-swing.webp` 재사용. 두 위치 모두 `width="480" height="480" loading="lazy" alt="" aria-hidden="true"`, `pointer-events: none` |
| D1 | Hero 그림 뒤 라임 토큰 12% 방사형 그라데이션. 하단 계측 문구 영역에는 적용하지 않음 |
| D3 | 결과 총점 카드 상단 3px 브랜드 강조선. 점수·등급·상태와 무관한 비대화형 장식 |
| D4 | 업로드 이미지·안내문 간격과 패딩 조정. 기존 hover/drag 상태에서 점선 테두리와 outline 강조 |

Hero 대체 텍스트는 `hero_visual_alt` 키로 KO/EN을 함께 추가했다.

- KO: 라임과 민트 관절 표시가 있는 골퍼의 백스윙 일러스트
- EN: Illustration of a golfer in a backswing with lime and mint joint markers

장식은 클릭을 가로채지 않는다. 새 반복 애니메이션은 없으며 기존 `prefers-reduced-motion` 전역 규칙을 유지했다.
H2는 후보 보관만 유지하고 배포하지 않았다. 계측 격자 D2와 비교·코칭 밑줄 D5는 추가하지 않았다.

## SVG 아이콘 12개

모든 SVG는 `web/src/components/icons.tsx`에 직접 작성했다. `viewBox="0 0 24 24"`, 18px, `stroke="currentColor"`, 1.8px 선, 둥근 끝/모서리, `aria-hidden="true" focusable="false"`를 공통 적용한다.
기존 텍스트 라벨과 테마 토글 접근성 이름을 유지하고, 기존 `statusIcon()`의 ✓/⚠/✕도 유지했다.

| 아이콘 | 실제 사용 위치 / 의미 |
|---|---|
| UploadIcon | Hero 업로드, 결과 새 영상 분석 / 영상 가져오기 |
| PlayIcon | Hero 샘플 데이터 / 샘플 보기 |
| VideoCameraIcon | TopBar 실시간 캠 / 촬영 진입 |
| HistoryIcon | TopBar 내 기록 / 기록 열람 |
| SunIcon | 다크 상태의 테마 버튼 / 라이트 전환 |
| MoonIcon | 라이트 상태의 테마 버튼 / 다크 전환 |
| ShareIcon | 결과 공유 / 공유 동작 |
| BookmarkIcon | 결과 저장·저장 로그인 버튼 / 기록 저장 |
| CompareIcon | 비교 제목 / 비교 영역 |
| CoachingIcon | 코칭 제목 / 코칭 영역 |
| ShieldIcon | 업로드 전·트림 화면 개인정보 안내 / 안내 식별 |
| TrimIcon | 분석 구간 설정 제목 / 구간 조정 |

## 완료 기준 1~6 — 직접 실행 결과

| 번호 | 판정 | 근거 |
|---|---|---|
| 1 · build | **PASS** | `cd web && npm run build` exit 0. TypeScript 및 Vite 빌드 성공. 메인 청크 500 kB 초과 경고는 남아 있으나 빌드 실패는 아님 |
| 2 · lint | **PASS** | 작업 전·후 `cd web && npm run lint` 모두 exit 0, 경고 18개 → 18개. 새 경고 없음 |
| 3 · 허용 경로 | **PASS** | `git status --short` 및 `--untracked-files=all` 확인. 지정된 기존 미추적 파일을 제외한 17개 파일 모두 R1 안. 보호된 경로와 패키지·App.tsx의 `git diff HEAD`는 비어 있음 |
| 4 · 파일 크기 | **PASS** | `ls -la web/public/images/`: H1 72,166 bytes ≤250KB, E1 17,032 bytes ≤80KB, 합계 89,198 bytes ≤600KB. 1KB=1,000 bytes로도 충족 |
| 5 · LiveCapture | **PASS** | 빌드 출력 `LiveCapture-B_DkE0E6.js` 143.68 kB 및 별도 CSS. 메인 청크의 동적 import 확인, MediaPipe CDN 문자열은 LiveCapture 청크에만 존재 |
| 6 · 브라우저 | **미확인** | Computer Use 브라우저 목록이 비어 있고 Chrome 접근은 `Computer Use was not approved to use Google Chrome`으로 거부됨. 360·390·1440px 가로 스크롤, 앱 내 다크/라이트 배치·테마/언어 토글은 실행하지 못함 |

추가 확인: `git diff --check` 통과. PNG 원본·WebP 실파일을 직접 열어 확인했고 알파 채널은 보존되었다. 빌드된 이미지와 public 원본은 바이트 단위로 같다.
다크/라이트 카드색에 WebP를 합성한 오프라인 미리보기에서 클럽·발·영상 타일과 가장자리를 확인했다. 이는 브라우저 검증을 대체하지 않는다.
브라우저를 통한 샘플 결과 렌더링·실제 파일 선택·빈 기록 렌더링·드롭 동작은 미확인이다. 기존 조건문과 이벤트 핸들러가 바뀌지 않았다는 diff 검증만 수행했다.

### 접근성 대비 계산

현재 `index.css` 값을 읽어 sRGB 상대 휘도 공식으로 계산했다. D1은 텍스트 뒤에 놓이지 않고 계측 문구는 불투명 카드 배경을 사용한다.

| 적용 조합 | 다크 | 라이트 |
|---|---:|---:|
| nav·개인정보 아이콘/본문 `steel / graphite` | 9.12:1 | 6.27:1 |
| 업로드 안내 `steel / graphite-2` | 8.03:1 | 6.72:1 |
| 계측 문구 `teal / graphite-2` | 9.71:1 | 6.41:1 |
| 제목·업로드 hover `copper / graphite-2` | 12.52:1 | 6.80:1 |
| 업로드·저장 버튼 `graphite / copper` | 14.21:1 | 6.35:1 |
| 공유 버튼 hover `graphite / teal` | 11.02:1 | 5.98:1 |

본문 4.5:1·아이콘 3:1 기준 이상이다. 실제 브라우저 렌더링·안티앨리어싱은 미확인이다.

## 생성 이미지 및 배포 이미지 목록

| 구분 | 경로 | 픽셀 크기 | 용량 |
|---|---|---|---:|
| H1 원본, 기존 생성 | `docs/visual-candidates/H1-sculpted-swing.png` | 1448 × 1086 | 503,738 bytes |
| E1 원본, 기존 생성 | `docs/visual-candidates/E1-first-swing.png` | 1254 × 1254 | 693,136 bytes |
| H1 배포, 이번 변환 | `web/public/images/hero-swing.webp` | 1152 × 864 | 72,166 bytes |
| E1 배포, 이번 변환 | `web/public/images/first-swing.webp` | 480 × 480 | 17,032 bytes |

미선택 H2 원본 `docs/visual-candidates/H2-editorial-swing.png`(1448 × 1086, 632,214 bytes)는 보관만 한다. 배포 이미지 합계는 **89,198 bytes(87.11 KiB)**다.
이미 설치된 `/opt/homebrew/bin/cwebp` 사용, 새 패키지 설치 없음. 변환 명령:

```sh
cwebp -q 88 -m 6 -alpha_q 100 -resize 1152 864 docs/visual-candidates/H1-sculpted-swing.png -o web/public/images/hero-swing.webp
cwebp -q 88 -m 6 -alpha_q 100 -resize 480 480 docs/visual-candidates/E1-first-swing.png -o web/public/images/first-swing.webp
```

## 사용한 생성 프롬프트 원문

기존 1단계의 built-in `image_gen`, 각각 `transparent_background: true`, 참조 이미지 없음. 아래 H1·E1 프롬프트는 [원본 생성 기록](visual-candidates/prompts.md)에서 그대로 옮겼다. H2 프롬프트 및 도구 원본 경로는 해당 기록에 보존했다.

### H1

```text
Use case: stylized-concept
Asset type: H1, a transparent PNG hero illustration for the Swing.Lab golf swing analysis app, Club Lime visual direction.
Primary request: A polished sculptural 3D-style full-body anonymous adult golfer in a dynamic backswing-top pose, with thin lime and mint joint-tracking dots and connecting lines accurately placed on the visible shoulders, elbows, wrists, hips, knees and ankles. A single normal golf club is held with both hands; believable golf posture and anatomy, two arms and two legs.
Scene/backdrop: True transparent alpha background, isolated subject, no rectangular backdrop, no floor, no scenery, no checkerboard painted into the image.
Style/medium: Premium restrained matte 3D editorial sports illustration, softly faceted surfaces and crisp contours, simplified featureless face, no resemblance to any real person. Cream and muted lime shirt, dark forest-green trousers, pale shoes, a dark green club with pale edge highlights. Avoid a shiny toy or robot appearance.
Composition/framing: Landscape canvas around 4:3. Full body and full club comfortably inside the canvas, centered compact silhouette occupying about 75 percent of the frame width and height, generous clear margin around the club, hands and feet. Entire lower 12 percent remains empty for existing HTML readouts. Tracking lines remain over the body, a single restrained mint swing arc may sit behind the club; no dashboard or interface frame.
Lighting/mood: Soft studio modeling with a narrow pale rim and dark contour, clean energetic contemporary sports identity. Must remain legible when composited over both deep green #111610 / #1B2319 and off-white #F6F8EF / #FFFFFF.
Color palette: Forest green #1B2319, lime #C5F26B, mint #73DACC, warm pale #F3F7ED. Lime and mint tracking marks should have a slim dark boundary for light-background visibility.
Text: None.
Constraints: No letters, numbers, labels, angle values, watermark, logo, brand symbol, real person, extra limbs, duplicate clubs, photorealistic face, opaque background, colored background panel or broad glow. This is conceptual decorative art, not measured motion data. Generate one image only.
```

### E1

```text
Use case: stylized-concept
Asset type: E1, a small reusable transparent PNG empty-state illustration for the golf-video upload area and the empty swing-history area of Swing.Lab.
Primary request: A compact quiet still life of a single blank rounded video tile leaning slightly backward, with a simple triangular play symbol, a small golf ball on a short tee in front, and one restrained curved mint motion line ending in two small tracking dots. It should gently suggest that the first swing video is waiting to be added, without depicting a success state.
Scene/backdrop: True transparent alpha background, isolated objects, no large colored backdrop, no environment or painted checkerboard.
Style/medium: Refined minimal editorial illustration with softly modeled matte surfaces, rounded shapes and a few broad color planes, compatible with both a sculptural sports hero and a flat sports hero. Few details so the image reads clearly at 120 to 160 CSS pixels wide.
Composition/framing: Square canvas, centered compact object group occupying about 70 percent of canvas, generous transparent margin, every object fully visible. One video tile only, no collection of completed records, no charts, no celebratory badge.
Lighting/mood: Soft calm invitation, crisp dual light/dark edges that read on deep green #111610 / #1B2319 and off-white #F6F8EF / #FFFFFF; no broad outer glow.
Color palette: Forest green #1B2319, warm pale #F3F7ED, lime #C5F26B and mint #73DACC accents. Dark contour around pale elements and pale rim around dark elements.
Text: None.
Constraints: No words, letters, numbers, upload arrows, labels, logos, watermarks, real persons, trophies, checkmarks, opaque rectangular background or full UI screenshot. Not an interactive button. Generate one image only.
```

## 커밋 묶음 제안 — 실행하지 않음

텍스트는 추가+삭제 합계, 신규 파일은 전체 줄 수 기준이다. 바이너리 2개는 줄 수 대신 위 실측 용량으로 관리한다. 기존 후보 파일·지시서·`.DS_Store`는 아래 제안에서 제외한다.

| 묶음 | 파일 | 제안 메시지 | 예상 줄 수 |
|---|---|---|---:|
| 1 | `web/src/components/icons.tsx`, `web/src/index.css` | `feat(web): 공통 SVG 아이콘 12종 추가` | 69 |
| 2 | `web/src/components/Hero.tsx`, `Hero.module.css`, `web/src/lib/i18n.tsx`, `web/public/images/hero-swing.webp` | `feat(web): H1 히어로 이미지와 D1 배경 적용` | 59 + 바이너리 1개 |
| 3 | `web/src/components/UploadTrim.tsx`, `UploadTrim.module.css`, `HistoryPanel.tsx`, `HistoryPanel.module.css`, `web/public/images/first-swing.webp` | `feat(web): E1 빈 상태와 D4 업로드 강조 적용` | 41 + 바이너리 1개 |
| 4 | `web/src/components/TopBar.tsx`, `TopBar.module.css`, `ResultScreen.tsx`, `ResultScreen.module.css`, `CompareSection.tsx`, `CoachingPanel.tsx` | `feat(web): 메뉴·결과 아이콘과 D3 점수 강조 적용` | 33 |
| 5 | `docs/visual-plan.md` | `docs: 비주얼 적용 결과와 검증 근거 기록` | 150 |

각 묶음은 200줄 이하이다. Git 인덱스·커밋·푸시는 변경하지 않았다. 다음 확인은 Chrome 접근이 가능한 환경에서 완료 기준 6의 실제 화면 검증이다.
