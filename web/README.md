# Swing.Lab — Web Frontend

React + Vite + TypeScript로 만든 신규 웹 프론트엔드입니다. "모션 랩(Motion Lab)" 디자인
방향(그래파이트 배경 + 코퍼/틸 액센트, 모노스페이스 데이터 타이포)으로 구현했습니다.
자세한 배경은 루트의 [`CLAUDE.md`](../CLAUDE.md)와 `.claude/skills/golf-platform/SKILL.md`를
참고하세요.

## 실행 방법

이 앱은 `../server/`(FastAPI)를 통해 분석 코어(`../golf_swing_analyzer/analyzer/`)와 통신합니다.
두 개를 함께 띄워야 합니다.

```bash
# 터미널 1 — API 서버
cd ../server
pip install -r requirements.txt
uvicorn main:app --port 8010

# 터미널 2 — 프론트엔드
npm install
npm run dev   # http://localhost:5173
```

`npm run dev`만으로는 분석 기능이 동작하지 않습니다(서버 없이도 "샘플 데이터 보기"로
결과 화면은 확인 가능 — `public/samples/*.json`에 미리 계산된 응답이 번들돼 있습니다).

## 스크립트

| 명령 | 설명 |
|---|---|
| `npm run dev` | 개발 서버 (HMR) |
| `npm run build` | 타입체크(`tsc -b`) + 프로덕션 빌드 |
| `npm run lint` | oxlint |
| `npm run preview` | 빌드 결과 로컬 미리보기 |

## 구조

```
src/
├── lib/           # api.ts(서버 통신), types.ts, i18n.tsx(한/영), status.ts, issueMessages.ts
├── components/    # TopBar, Hero, UploadTrim, ResultScreen, Waveform, CoachingPanel
├── index.css      # 디자인 토큰 (그래파이트/코퍼/틸, 단일 다크 테마)
└── App.tsx        # 랜딩 → 업로드/트리밍 → 분석중 → 결과 상태 머신
public/
└── samples/       # 테스트 영상 3종의 /analyze 응답 스냅샷 (샘플 결과 보기용)
```

서버 응답 포맷(특히 한국어 페이즈명·진단 문구)은 그대로 두고 표시 단계에서만 번역하는
원칙을 따릅니다 — 자세한 내용은 `src/lib/i18n.tsx`, `src/lib/issueMessages.ts` 주석과
`.claude/skills/golf-ui-ux/SKILL.md`의 B1~B6 항목을 참고하세요.
