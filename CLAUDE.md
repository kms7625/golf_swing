# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This repo has a project-specific skillset in `.claude/skills/golf-*` (golf-code-change, golf-ui-ux,
golf-realtime, golf-platform, golf-coach-llm, golf-analysis-quality, golf-session-retro,
golf-prompt-engineer) that encodes the invariants, checklists, and cross-file duplication traps
referenced throughout this document — check there before non-trivial changes to `analyzer/`, `ui/`,
or `web/`+`server/`. `golf_swing_analyzer/skills/kis-*` is an unrelated reference skillset copied in
from another project — ignore it when working on this codebase.

## Running the App

Two frontends share the same analysis core (`golf_swing_analyzer/analyzer/`):

**Streamlit (reference implementation)** — the original app, kept as the regression baseline:
```bash
pip install -r golf_swing_analyzer/requirements.txt
streamlit run golf_swing_analyzer/app_v2.py
```

**React web app + FastAPI backend (the app being actively developed)**:
```bash
# terminal 1 — API server (imports analyzer/ directly, same core as Streamlit)
pip install -r server/requirements.txt
cd server && uvicorn main:app --port 8010

# terminal 2 — frontend
cd web && npm install && npm run dev   # http://localhost:5173
```

Both frontends require a Gemini/Claude/GPT API key entered by the user at runtime (not stored anywhere). Gemini is the default and has a free tier.

**Build/lint (`web/`)**: `npm run build` (`tsc -b && vite build`), `npm run lint` (oxlint), `npm run preview`.

**Android (Capacitor wrapper around the same `web/` build, dev-only, added 2026-07-05)**:
```bash
cd web && npm run build:android           # builds with .env.capacitor + npx cap sync android
cd android && ./gradlew.bat installDebug  # or `npx cap open android` for Android Studio
```
Requires Android Studio + SDK. `JAVA_HOME` can point at Android Studio's bundled JBR (e.g.
`C:\Android\Android Studio\jbr`) if no system JDK is installed. See the `web/android/` section
below for the dev-only network wiring this depends on (mixed-content/cleartext/CORS).

`golf_swing_analyzer/requirements.txt` used to pin the old `google-generativeai` package while
`analyzer/coach_llm.py` imports the newer `from google import genai` (`google-genai` package) — fixed
2026-07-05. If a fresh install of the Streamlit app fails on the Gemini import, check this file matches
`server/requirements.txt`'s `google-genai` entry.
There is no automated test suite (Python or TS) in this repo — regression checking is manual, via the
golf-analysis-quality skill and the 3 videos in `golf_swing_analyzer/video/` (일반.mp4/프로.mp4/프로2.mp4),
comparing `analyzer/` output before/after a change.

## Architecture

**Updated 2026-07-04/05**: the app was originally a single ~1986-line file. It went through
three splits, in order:
1. `golf_swing_analyzer/app_v2.py` Section 0~8 (analysis core) → `golf_swing_analyzer/analyzer/` package
2. Remaining UI (Section 9~10, 885 lines) → `golf_swing_analyzer/ui/` package (Streamlit only), `app_v2.py` reduced to ~53 lines of wiring
3. New `server/` (FastAPI) + `web/` (React+Vite+TS) added — a second frontend that calls the *same* `analyzer/` package, per the "코어 보존 + 껍데기 교체" plan (see `.claude/skills/golf-platform/SKILL.md`)
4. `web/android/` (Capacitor) added 2026-07-05 — wraps the same `web/` build for Android, no new frontend code, just a native shell + dev-only network wiring (see below)

Algorithm logic was moved verbatim at every step (no behavior change) — see the golf-code-change
skill (`.claude/skills/golf-code-change/SKILL.md`) for the invariants each split had to preserve.
The Streamlit app (`golf_swing_analyzer/`) is kept indefinitely as the reference implementation /
regression baseline — new work happens in `server/` + `web/`.

### `server/` package — FastAPI backend for the web frontend

| File | Role |
|---|---|
| `main.py` | 4 endpoints: `POST /analyze`, `POST /auto-window`, `POST /detect-phases` (pre-built for future real-time use), `POST /coaching` |
| `serialization.py` | numpy→JSON conversion, representative-frame extraction (byte-identical duplicate of `ui/tab_analysis.py`'s logic — see golf-code-change A8), base64 JPEG encoding |

The server imports `analyzer/` directly (adds `golf_swing_analyzer/` to `sys.path`) — no core logic
lives in `server/`. It never returns `annotated_frames` in full (only 7 representative frames as
base64) to keep API payloads small.

### `web/` package — React + Vite + TypeScript frontend ("모션 랩" design)

| Path | Role |
|---|---|
| `src/index.css` | Design tokens (graphite/copper/teal palette) — single dark theme, deliberate |
| `src/lib/api.ts` | Fetch wrappers for the 4 server endpoints |
| `src/lib/types.ts` | API response types, `PHASE_KEY_MAP`, `PHASE_COLORS` (mirrors `analyzer/drawing.py`) |
| `src/lib/i18n.tsx` | KO/EN string dictionary + phase-name translation table — server responses stay Korean, only display is translated |
| `src/lib/status.ts` | Port of `ui/components.py`'s `get_status()` — same thresholds |
| `src/lib/issueMessages.ts` | Regex-based KO→EN translation for `compute_score()`'s diagnostic messages (12 fixed templates) — server messages stay Korean (same principle as phase names), untranslatable text falls back to the Korean original rather than breaking |
| `src/components/` | `TopBar`, `Hero`, `UploadTrim` (upload + auto/manual trim), `ResultScreen`, `Waveform` (recharts), `CoachingPanel` |
| `public/samples/*.json` | Pre-computed `/analyze` responses for the 3 test videos — lets visitors view a full result screen with no server call and no API key |

`web/` intentionally does not replicate Streamlit Tab 5 (reference-DB batch learning) or Tab 3's
CSV export — those stay Streamlit-only. See `.claude/skills/golf-platform/SKILL.md` stage 3 for
the full scope decision.

### `web/android/` — Capacitor Android wrapper (dev-only, added 2026-07-05)

Wraps the same `web/` build for Android via Capacitor — no separate app code, just a native
shell plus dev-only network wiring so an emulator/device can reach the FastAPI dev server:

| File | Role |
|---|---|
| `capacitor.config.ts` | Sets `server.androidScheme: 'http'` — **not** Capacitor's default (`'https'`). Required because the default `https://localhost` origin triggers browser mixed-content blocking against the plain-`http://10.0.2.2:8010` dev API. This is a document-level (browser) policy, separate from and stricter than Android's cleartext-traffic setting below — setting the network security config alone does *not* fix it |
| `.env.capacitor` | `VITE_API_BASE=http://10.0.2.2:8010`, used only by `npm run build:android` (`vite build --mode capacitor`), not the regular web build. `10.0.2.2` is the Android emulator's alias for the host machine's loopback interface |
| `android/app/src/main/res/xml/network_security_config.xml` | Permits cleartext (non-HTTPS) traffic to `10.0.2.2`/`localhost` — Android 9+ (API 28+) blocks cleartext by default at the OS/socket level. Wired in via `android:networkSecurityConfig` in `AndroidManifest.xml` |

`server/main.py`'s CORS `allow_origins` includes `http://localhost` (the Capacitor WebView's
origin once `androidScheme` is `http`) alongside the Vite dev origins — a stale/unrestarted
`uvicorn` process silently keeps serving the old CORS list, which looks identical to a
mixed-content failure from the client (both manifest as a generic `Failed to fetch`).

This whole setup is a **local-dev bridge**: it only works when the FastAPI server and the
Android emulator run on the same machine. A physical device needs the server bound to `0.0.0.0`
and `VITE_API_BASE` pointed at the dev machine's LAN IP instead of `10.0.2.2`. iOS is out of
scope on Windows (no Xcode). See `.claude/skills/golf-platform/SKILL.md` stage 4.

### `analyzer/` package — analysis core (preserved, do not rewrite)

| Module | Role |
|---|---|
| `mp_setup.py` | MediaPipe init (`mp_pose`, `mp_drawing`) |
| `reference_db.py` | Pro/amateur reference DB (load/save/update, mean±std stats) |
| `geometry.py` | Landmark normalization, joint angle calculation |
| `smoothing.py` | `MovingAverageFilter` — per-key deque-based smoothing |
| `phase_detector.py` | `SwingPhaseDetector` — 7-phase segmentation algorithm |
| `drawing.py` | Trajectory overlay + Korean HUD rendering |
| `pipeline.py` | `process_video()` and video utilities (trim, thumbnails, auto swing-window detection) |
| `scoring.py` | `compute_summary()` / `compute_score()` — metrics aggregation |
| `coach_llm.py` | `build_prompt()` + `get_llm_feedback()` — LLM coaching report |

### `ui/` package — Streamlit UI (candidate for replacement per the "코어 보존 + 껍데기 교체" plan)

| Module | Role |
|---|---|
| `styles.py` | CSS injection (`inject_css()`) + `render_hero()` |
| `components.py` | `render_metric_card()`, `get_status()` |
| `sidebar.py` | `render_sidebar()` — LLM provider/model, API key, sample rate |
| `tab_analysis.py` | Tab 1 — upload, trim, analyze, results, representative frames |
| `tab_phases.py` | Tab 2 — 7-phase breakdown, wrist-Y diagnostic chart |
| `tab_data.py` | Tab 3 — raw time-series charts, CSV export |
| `tab_coaching.py` | Tab 4 — AI coaching report generation/display |
| `tab_learning.py` | Tab 5 — batch video upload into the reference DB |

### 7-Phase Swing Detection (`SwingPhaseDetector`)

This is the most complex part of the codebase. It runs **post-hoc** after all frames are processed, operating on the full `wrist_y_history` time series.

**Signal**: average pixel Y of both wrists (`lms[15].y * h + lms[16].y * h) / 2`). In image coordinates, **Y increases downward**, so:
- Backswing (wrists rise physically) → Y **decreases**
- Downswing (wrists descend) → Y **increases**
- Impact = **argmax(wy)** after backswing top = wrist at its lowest physical point

**Detection order** (all computed in `detect_all_phases()`):
1. `addr_end` — first frame where smoothed wy drops 10% of y_range from initial = backswing starts
2. `top_idx` — velocity zero-crossing (negative→positive in `wy_v`) after `addr_end` = backswing top
3. `impact_idx` — `argmax(wy[top_idx+1 : top_idx + 70%])` = downswing wrist peak = actual impact
4. `follow_idx` — `argmin(wy_s)` after impact = follow-through apex

**Critical**: the address-height-threshold approach (checking `wy >= y_addr`) was intentionally abandoned because pro swing videos can have impact wy < address wy (camera angle differences). `argmax` is robust to this.

**Smoothing**: `_smooth()` uses an edge-aware loop (NOT `np.convolve(mode='same')` which causes zero-padding artifacts at boundaries that corrupt the first few values).

**Index mapping**: `local_to_hist` dict maps `local_idx` (frame counter, increments only when pose is detected) → `hist_idx` (index into `wrist_y_history`). This prevents off-by-one errors when non-visible frames cause interpolation entries in `frame_data` without corresponding `wrist_y_history` entries.

### Video Processing Pipeline (`process_video`)

1. Adaptive frame sampling: ≤180 total frames → every frame; ≤540 → max 2-frame skip; longer → cap at 200 analysis frames
2. CLAHE preprocessing per frame (contrast enhancement for pose detection)
3. Per-frame: MediaPipe pose → `normalize_landmarks()` → angle calculations → `phase_detector.update()`
4. After loop: `phase_detector.detect_all_phases()` fills `frame_phases` array
5. Back-fill: each `frame_data` entry gets its phase via `get_phase_for_frame(local_idx)`
6. Returns `(frame_data, annotated_frames, trajectory_pts, fps, phase_detector, effective_sample)`

`annotated_frames` and `frame_data` are 1:1 indexed (both append in the same `if results.pose_landmarks:` block, in `analyzer/pipeline.py`).

### Korean HUD Rendering (`analyzer/drawing.py`)

`cv2.putText()` cannot render Korean. The HUD uses PIL (`Pillow`) with Malgun Gothic font (`C:/Windows/Fonts/malgun.ttf`). Font is cached in a module-level `_hud_font` global. Falls back to ASCII if font file not found.

### Representative Frame Selection (`ui/tab_analysis.py`)

For displaying the 7-phase grid in the UI, each phase picks one frame from `annotated_frames`.
This selection logic lives in the UI layer (not `analyzer/`) but is treated as an analysis
invariant — see golf-code-change A8:
- **임팩트 (impact)**: uses the **first** frame of the phase (index 0 of matching entries) — impact is instantaneous
- **다운스윙 (downswing)**: uses the frame at the 85% point (skips the initial plateau, shows the actual drop)
- All other phases: uses the **middle** frame

### LLM Integration (`analyzer/coach_llm.py`)

`get_llm_feedback()` supports Gemini (`google.genai`), Claude (`anthropic`), GPT (`openai`).
**Note**: Claude and GPT SDKs are imported lazily (only when selected), but Gemini's
`google.genai` is imported eagerly at module top — this is an inconsistency in the current
code, not a design choice; don't assume all three behave the same way when reasoning about
import cost or startup errors. The prompt (`build_prompt()`) sends structured JSON of
per-phase statistics and AI-flagged issues.

## Key Data Structures

**`frame_data`**: list of dicts per processed frame:
```python
{
    "frame": int,        # original video frame index
    "local_idx": int,    # sequential counter (pose-detected frames only)
    "time": float,       # local_idx * effective_sample / fps
    "phase": str,        # filled post-hoc
    "spine_angle": float,
    "shoulder_rotation": float,
    "hip_rotation": float,
    "left_knee": float, "right_knee": float,
    "left_elbow": float, "right_elbow": float,
}
```

**Streamlit session state keys** (set in `ui/tab_analysis.py`): `tmp_original`, `trim_path`, `frame_data`, `annotated_frames`, `trajectory_pts`, `fps`, `phase_det`, `eff_sample`, `summary`, `score`, `issues`, `uploaded_name`, `ref_db`, `ai_feedback`

## Landmark Normalization

All joint angles use **shoulder-width normalized coordinates** (`analyzer/geometry.py`):
- Origin = shoulder center
- Scale = shoulder width = 1.0 unit
- This makes angles camera-distance and resolution independent

Wrist Y for phase detection uses **raw pixel coordinates** (not normalized) to preserve the actual up/down signal magnitude needed for threshold comparisons.
