import { useId, useState } from "react";
import type { AnalyzeResponse } from "../lib/types";
import { PHASE_ORDER_KO } from "../lib/types";
import { getStatus, statusIcon } from "../lib/status";
import { useAuth } from "../lib/auth";
import { useI18n, type StringKey } from "../lib/i18n";
import { translateIssueMessage } from "../lib/issueMessages";
import { saveSwing } from "../lib/api";
import { buildShareCard, shareOrDownload } from "../lib/shareCard";
import { Waveform } from "./Waveform";
import { CompareSection } from "./CompareSection";
import { CoachingPanel } from "./CoachingPanel";
import { SwingReplay, type ReplaySource } from "./SwingReplay";
import { BookmarkIcon, ShareIcon, UploadIcon } from "./icons";
import styles from "./ResultScreen.module.css";

interface Props {
  result: AnalyzeResponse;
  isSample: boolean;
  onBack: () => void;
  onHistoryBack?: () => void;
  /** 분석에 사용한 파일명 — 저장 시 기록 */
  videoName?: string;
  /** 히스토리에서 열었을 때의 스윙 id (이미 저장된 결과) */
  swingId?: number;
  /** 저장된 스윙에 붙어 있던 코칭 리포트 */
  initialFeedback?: string;
  /** 새 분석 직후에만 존재 — 원본 영상 objectURL+구간 (저장/샘플 결과에는 없음) */
  replay?: ReplaySource;
  onLoginClick: (purpose?: "save" | "coaching") => void;
}

export function grade(score: number): string {
  if (score >= 95) return "S";
  if (score >= 85) return "A";
  if (score >= 70) return "B";
  if (score >= 55) return "C";
  return "D";
}

function MetricHelp({ metric, help }: { metric: StringKey; help: StringKey }) {
  const { t } = useI18n();
  const id = useId();
  const [open, setOpen] = useState(false);
  return (
    <span onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <button type="button" className={styles.help} title={t(help)}
        aria-label={`${t(metric)}: ${t(help)}`} aria-describedby={open ? id : undefined}
        onFocus={() => setOpen(true)} onBlur={() => setOpen(false)}
        onClick={() => setOpen(true)} onKeyDown={(e) => { if (e.key === "Escape") setOpen(false); }}>?</button>
      {open && <span id={id} className={styles.tooltip} role="tooltip">{t(help)}</span>}
    </span>
  );
}

export function ResultScreen({
  result,
  isSample,
  onBack,
  onHistoryBack,
  videoName,
  swingId,
  initialFeedback,
  replay,
  onLoginClick,
}: Props) {
  const { t, lang, phaseLabel } = useI18n();
  const { isLoggedIn } = useAuth();
  const [savedId, setSavedId] = useState<number | null>(swingId ?? null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [shareState, setShareState] = useState<"idle" | "making" | "shared" | "downloaded">("idle");
  const { score, issues, summary, rep_frames, wrist_y_history, phase_boundaries } = result;

  async function handleSave() {
    setSaveError(null);
    try {
      const row = await saveSwing(videoName ?? "", result);
      setSavedId(row.id);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  async function handleShare() {
    setShareState("making");
    try {
      const blob = await buildShareCard(result, {
        scoreLabel: t("result_score_label"),
        gradeLabel: t("grade"),
        spine: t("result_metric_spine"),
        xfactor: t("result_metric_xfactor"),
        shoulder: t("result_metric_shoulder"),
      });
      const action = await shareOrDownload(blob, `swinglab-${result.score}.png`);
      setShareState(action);
      setTimeout(() => setShareState("idle"), 2500);
    } catch {
      setShareState("idle");
    }
  }

  const spineStatus = getStatus(summary.spine_angle_delta, 0, 5, 5, 10);
  const xfactorStatus = getStatus(summary.x_factor, 35, 55, 20, 60);
  const phaseCount = summary.phases_detected.length;
  const phaseStatus = phaseCount >= 5 ? "ok" : "warn";

  return (
    <div className={styles.wrap}>
      <header className={styles.header}>
        {onHistoryBack && <button className={styles.backLink} onClick={onHistoryBack}>← {t("history_back")}</button>}
        <h1 className={styles.sectionTitle}>{t("result_phases_title")}</h1>
        <div className={styles.source}>
          {videoName && <span className={styles.filename}>{videoName}</span>}
          <span className={styles.sampleBadge}>
            {isSample ? t("sample_badge") : savedId !== null ? t("result_saved") : t("result_fresh")}
          </span>
        </div>
      </header>

      <div className={styles.resultGrid}>
        <div className={styles.scorePanel}>
          <div className={`${styles.label} tracked`}>{t("result_score_label")}</div>
          <div className={`${styles.num} tabular`}>{score}</div>
          <div className={`${styles.grade} tracked`}>
            {t("grade")} {grade(score)}
          </div>
        </div>
        <div className={styles.statStrip}>
          <div className={styles.statTile}>
            <div className={styles.k}>
              {t("result_metric_spine")}
              <MetricHelp metric="result_metric_spine" help="result_spine_help" />
            </div>
            <p className={styles.description}>{t("result_spine_desc")}</p>
            <div className={`${styles.v} ${styles[spineStatus]} tabular mono`}>
              {summary.spine_angle_delta}° {statusIcon(spineStatus)}
            </div>
          </div>
          <div className={styles.statTile}>
            <div className={styles.k}>
              {t("result_metric_xfactor")}
              <MetricHelp metric="result_metric_xfactor" help="result_xfactor_help" />
            </div>
            <p className={styles.description}>{t(summary.x_factor_method === "world_3d_top" ? "result_xfactor_3d_desc" : "result_xfactor_desc")}</p>
            <div className={`${styles.v} ${styles[xfactorStatus]} tabular mono`}>
              {summary.x_factor}° {statusIcon(xfactorStatus)}
            </div>
            {summary.x_factor_method && summary.x_factor_fallback_reason !== "requested_legacy" && <p className={styles.description}>
              {t(summary.x_factor_method === "world_3d_top" ? "result_rotation_3d" : "result_rotation_fallback")}
            </p>}
            {summary.x_factor_fallback_reason !== "requested_legacy" &&
              (summary.rotation_world_valid_ratio ?? 0) > 0 && (summary.rotation_fallback_frames ?? 0) > 0 &&
              <p className={styles.description}>{t("result_rotation_partial")}</p>}
          </div>
          <div className={styles.statTile}>
            <div className={styles.k}>
              {t("result_metric_shoulder")}
              <MetricHelp metric="result_metric_shoulder" help={summary.x_factor_method === "world_3d_top" ? "result_shoulder_3d_help" : "result_shoulder_help"} />
            </div>
            <p className={styles.description}>{t(summary.x_factor_method === "world_3d_top" ? "result_shoulder_3d_desc" : "result_shoulder_desc")}</p>
            <div className={`${styles.v} tabular mono`}>{summary.shoulder_rotation_max}°</div>
          </div>
          <div className={styles.statTile}>
            <div className={styles.k}>
              {t("result_metric_phases")}
              <MetricHelp metric="result_metric_phases" help="result_phases_help" />
            </div>
            <p className={styles.description}>{t("result_phases_desc")}</p>
            <div className={`${styles.v} ${styles[phaseStatus]} tabular mono`}>
              {phaseCount} / 7 {statusIcon(phaseStatus)}
            </div>
          </div>
        </div>
      </div>

      <h2 className={styles.subheading}>{t("result_issues_title")}</h2>
      <div className={styles.issues}>
        {issues.map((issue, i) => (
          <div key={i} className={`${styles.issue} ${styles[issue.level]}`}>
            <div className={styles.tag}>
              <span aria-hidden="true">{statusIcon(issue.level === "good" ? "ok" : issue.level === "warning" ? "warn" : "crit")}</span>
              {t(`issue_${issue.level}`)}
            </div>
            <div className={styles.txt}>{translateIssueMessage(lang, issue.message)}</div>
          </div>
        ))}
      </div>

      <h2 className={styles.subheading}>{t("result_scenes_title")}</h2>
      <div className={styles.phaseRow}>
        {PHASE_ORDER_KO.map((ph) => (
          <div key={ph} className={styles.phaseCell}>
            <div className={styles.phaseThumb}>
              {rep_frames[ph] ? (
                <img src={`data:image/jpeg;base64,${rep_frames[ph]}`} alt={phaseLabel(ph)} />
              ) : (
                <p>{t(summary.phases_detected.includes(ph) ? "result_scene_missing" : "result_phase_missing")}</p>
              )}
            </div>
            <div className={styles.cap}>{phaseLabel(ph)}</div>
          </div>
        ))}
      </div>

      <div className={styles.chartWrap}>
        <h3 className="tracked">{t("result_chart_title")}</h3>
        <div className={styles.chartPanel}>
          <Waveform wristY={wrist_y_history} phaseBoundaries={phase_boundaries}
            wristTimesSec={result.wrist_times_sec} phaseBoundariesSec={result.phase_boundaries_sec} />
        </div>
      </div>

      {replay && (
        <SwingReplay
          source={replay}
          phaseBoundaries={phase_boundaries}
          phaseBoundariesSec={result.phase_boundaries_sec}
          fps={result.fps}
          effSample={result.eff_sample}
        />
      )}

      <CompareSection result={result} currentSwingId={savedId ?? undefined} />

      <CoachingPanel
        summary={summary}
        issues={issues}
        swingId={savedId ?? undefined}
        initialFeedback={initialFeedback}
        onLoginClick={() => onLoginClick("coaching")}
      />
      {saveError && <div className={styles.saveError} role="alert">{saveError}</div>}
      <div className={styles.actions}>
        <button className={styles.shareBtn} onClick={handleShare} disabled={shareState === "making"}>
          <ShareIcon />
          {shareState === "making"
            ? t("share_making")
            : shareState === "shared"
              ? t("share_shared")
              : shareState === "downloaded"
                ? t("share_downloaded")
                : t("share")}
        </button>
        {!isSample &&
          (savedId !== null ? (
            <span className={styles.savedBadge}>{t("save_done")}</span>
          ) : isLoggedIn ? (
            <button className={styles.saveBtn} onClick={handleSave}>
              <BookmarkIcon />
              {t("save_swing")}
            </button>
          ) : (
            <button className={styles.saveBtn} onClick={() => onLoginClick("save")}>
              <BookmarkIcon />
              {t("save_login_required")}
            </button>
          ))}
        <button className={styles.backLink} onClick={onBack}>
          <UploadIcon />
          {t("result_back")}
        </button>
      </div>
    </div>
  );
}
