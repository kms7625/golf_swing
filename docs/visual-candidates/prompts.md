# 생성 프롬프트 원문

초기 H1·H2·E1: 2026-10-08 · built-in `image_gen` · 각 요청 `transparent_background: true` · 입력 참조 이미지 없음.
초기 3종은 별도 요청 3회로 생성했으며 CLI/API 폴백, 재생성, 배경 제거·색상 보정·리사이즈를 하지 않았다. 원본 PNG를 그대로 복사했다. 후속 H1v의 참조·변환 기록은 아래 별도 절에 있다.

## H1

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

## H2

```text
Use case: stylized-concept
Asset type: H2, an alternate transparent PNG hero illustration for the Swing.Lab golf swing analysis app, Club Lime visual direction.
Primary request: One anonymous full-body adult golfer in an athletic mid-downswing pose, both hands gripping one golf club pointing diagonally down toward a small ball, with readable lime and mint joint-tracking dots and slender connecting lines aligned to the shoulders, elbows, wrists, hips, knees and ankles. Believable coherent anatomy, two arms and two legs, simplified featureless profile.
Scene/backdrop: True transparent alpha background, no background fill, no landscape, no rectangular card or ground plane, no painted checkerboard.
Style/medium: Sophisticated flat editorial sports illustration with large cut-paper-like color planes, clean curved shapes and restrained subtle grain inside solid shapes only. This should be visibly different from a 3D render. A pale warm shirt and dark forest-green trousers, bold quiet shapes with lime accents and mint joint overlays. Not a stick figure.
Composition/framing: Landscape canvas around 4:3, centered full-body figure and complete club with generous safe margins. Body, club and tiny ball form one compact balanced composition, occupying about 75 percent of width and height. Lower 12 percent remains clear for HTML readouts. One thin graphic swing arc reinforces movement without surrounding the figure in rings.
Lighting/mood: Calm precise editorial poster aesthetic, energetic pose, strong silhouette, no cast shadow beyond subject. Dark contour plus pale edge details make the figure visible on both deep green #111610 / #1B2319 and off-white #F6F8EF / #FFFFFF.
Color palette: Forest green #1B2319, lime #C5F26B, mint #73DACC, warm pale #F3F7ED. Lime and mint tracking marks have a subtle dark edge so they remain visible against light backgrounds.
Text: None.
Constraints: No words, letters, numbers, labels, measurement values, brand logos, watermark, recognizable person, detailed face, extra limbs or clubs, opaque background, broad glow. Conceptual decorative art, not measured motion data. Generate one image only.
```

## E1

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

## 원본 출처

| ID | 생성 도구 원본 파일 | 프로젝트 사본 |
|---|---|---|
| H1 | `/Users/mose/.codex/generated_images/01a11a0c-826e-7991-a5e9-68df87100dbf/exec-30de0aa8-e628-4339-8d35-60738ebcd1ae.png` | `H1-sculpted-swing.png` |
| H2 | `/Users/mose/.codex/generated_images/01a11a0c-826e-7991-a5e9-68df87100dbf/exec-c99566dc-6a43-4e47-bdd1-6d7f68eb3308.png` | `H2-editorial-swing.png` |
| E1 | `/Users/mose/.codex/generated_images/01a11a0c-826e-7991-a5e9-68df87100dbf/exec-5f345ba0-aa86-4e44-a5d7-542de7f4255f.png` | `E1-first-swing.png` |

## H1v — Hero 9:16 세로 구도

2026-10-08 · built-in `image_gen` 1회 · `transparent_background: true`.
참조 입력: `docs/visual-candidates/H1-sculpted-swing.png` (`referenced_image_paths`). CLI/API 폴백 없음.

```text
Use case: stylized-concept
Asset type: H1v, a transparent PNG hero illustration for the Swing.Lab golf swing analysis app, Club Lime visual direction.
Input image: H1-sculpted-swing.png is the reference for the exact anonymous character, wardrobe, sculptural rendering style, lime/mint joint-tracking overlay, and golf backswing pose.
Primary request: Generate a new portrait 9:16 composition of this same full-body anonymous adult golfer. Preserve the featureless face, dark forest-green cap and trousers, cream shirt with muted lime side panels, pale golf shoes, matte sculptural 3D surfaces, and thin lime/mint joint dots and connecting lines with dark edges.
Composition/framing: Strict 9:16 vertical canvas, ideally 1080 x 1920. Make the golfer large: the top of the cap through the soles of the shoes must span at least 80 percent of the full image height, ideally 84 percent. Keep the complete head, hands, both feet and single club inside the image with small safe margins. Recompose the backswing and camera perspective to foreshorten the club into the narrow portrait canvas instead of shrinking the body to fit a wide horizontal club. Keep believable golf anatomy, two arms, two legs, and both hands gripping one club. Center the body with minimal surrounding empty space. No large blank lower area; the app provides separate HTML readouts.
Scene/backdrop: True transparent alpha background, isolated golfer and restrained mint swing arc only. No opaque backdrop, ground, scenery, shadow rectangle, or checkerboard drawn into the pixels.
Lighting and palette: Match the reference's soft studio modeling, pale rim and dark contours. Forest green #1B2319, lime #C5F26B, mint #73DACC and warm pale #F3F7ED. Clear silhouette over both dark green and off-white app backgrounds.
Constraints: Same anonymous character and premium matte 3D editorial style as the reference. No identifiable real person, realistic facial features, text, letters, numbers, labels, measurement values, logo, watermark, brand, interface panel, extra limbs or duplicate clubs. Joint overlay stays on the body. Generate one image only.
```

생성 도구 원본: `/Users/mose/.codex/generated_images/01a11a35-323c-7453-8330-fdc315f90041/exec-8210d4df-a72f-4371-aca2-a1187c56796b.png` (941 × 1672, RGBA). 도구 원본은 그대로 보존했다.
프로젝트 PNG: `H1v-sculpted-swing-916.png` (936 × 1664, 정확한 9:16). 오른쪽 5px·하단 8px의 완전히 투명한 여백만 기존 `cwebp`·`dwebp`의 무손실 변환으로 잘랐다. 남은 영역의 RGBA 픽셀은 생성 원본과 완전히 같다. `sips`는 지정한 좌상단 원점 대신 중앙을 잘라 최종 파일에 사용하지 않았다.
앱 WebP: `web/public/images/hero-swing-916.webp` (936 × 1664). 기존 `cwebp`로 변환했고 알파 채널을 보존했다. 새 패키지 설치 없음.

```sh
cwebp -lossless -exact -crop 0 0 936 1664 /Users/mose/.codex/generated_images/01a11a35-323c-7453-8330-fdc315f90041/exec-8210d4df-a72f-4371-aca2-a1187c56796b.png -o /private/tmp/hero-916-lossless.webp
dwebp /private/tmp/hero-916-lossless.webp -o docs/visual-candidates/H1v-sculpted-swing-916.png
cwebp -q 88 -m 6 -alpha_q 100 docs/visual-candidates/H1v-sculpted-swing-916.png -o web/public/images/hero-swing-916.webp
```
