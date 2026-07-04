# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r golf_swing_analyzer/requirements.txt
streamlit run golf_swing_analyzer/app_v2.py
```

The app requires a Gemini/Claude/GPT API key entered in the sidebar at runtime (not stored in code). Gemini is the default and has a free tier.

## Architecture

**Updated 2026-07-04**: the app was originally a single ~1986-line file. It has since been split
into two packages under `golf_swing_analyzer/`, with `app_v2.py` reduced to a ~53-line wiring
script (`st.set_page_config()` → `inject_css()` → `main()`, which calls the sidebar and tab
renderers below). Algorithm logic was moved verbatim (no behavior change) — see the golf-code-change
skill (`.claude/skills/golf-code-change/SKILL.md`) for the invariants this split had to preserve.

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
