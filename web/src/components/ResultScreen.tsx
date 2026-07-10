import { useState } from "react";
import type { AnalyzeResponse } from "../lib/types";
import { PHASE_ORDER_KO } from "../lib/types";
import { getStatus, statusIcon } from "../lib/status";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { translateIssueMessage } from "../lib/issueMessages";
import { saveSwing } from "../lib/api";
import { buildShareCard, shareOrDownload } from "../lib/shareCard";
import { Waveform } from "./Waveform";
import { CompareSection } from "./CompareSection";
import { CoachingPanel } from "./CoachingPanel";
import { SwingReplay, type ReplaySource } from "./SwingReplay";
import styles from "./ResultScreen.module.css";

interface Props {
  result: AnalyzeResponse;
  isSample: boolean;
  onBack: () => void;
  /** 분석에 사용한 파일명 — 저장 시 기록 */
  videoName?: string;
  /** 히스토리에서 열었을 때의 스윙 id (이미 저장된 결과) */
  swingId?: number;
  /** 저장된 스윙에 붙어 있던 코칭 리포트 */
  initialFeedback?: string;
  /** 새 분석 직후에만 존재 — 원본 영상 objectURL+구간 (저장/샘플 결과에는 없음) */
  replay?: ReplaySource;
  onLoginClick: () => void;
}

export function grade(score: number): string {
  if (score >= 95) return "S";
  if (score >= 85) return "A";
  if (score >= 70) return "B";
  if (score >= 55) return "C";
  return "D";
}

export function ResultScreen({
  result,
  isSample,
  onBack,
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
      <div className={styles.header}>
        <span className={styles.sectionTitle}>{t("result_phases_title")}</span>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          {isSample && <span className={styles.sampleBadge}>{t("sample_badge")}</span>}
          <button className={styles.shareBtn} onClick={handleShare} disabled={shareState === "making"}>
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
                {t("save_swing")}
              </button>
            ) : (
              <button className={styles.saveBtn} onClick={onLoginClick}>
                {t("save_login_required")}
              </button>
            ))}
          <button className={styles.backLink} onClick={onBack}>
            {t("result_back")}
          </button>
        </div>
      </div>

      <div className={styles.resultGrid}>
        <div className={`${styles.panel} ${styles.scorePanel}`}>
          <div className={`${styles.bracket} ${styles.tl}`} />
          <div className={`${styles.bracket} ${styles.br}`} />
          <div className="label tracked">{t("result_score_label")}</div>
          <div className="num tabular mono">{score}</div>
          <div className="grade tracked">
            {t("grade")} {grade(score)}
          </div>
        </div>
        <div className={styles.statStrip}>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_spine")}</div>
            <div className={`v ${spineStatus} tabular mono`}>
              {summary.spine_angle_delta}° {statusIcon(spineStatus)}
            </div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_xfactor")}</div>
            <div className={`v ${xfactorStatus} tabular mono`}>
              {summary.x_factor}° {statusIcon(xfactorStatus)}
            </div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_shoulder")}</div>
            <div className="v tabular mono">{summary.shoulder_rotation_max}°</div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_phases")}</div>
            <div className={`v ${phaseStatus} tabular mono`}>
              {phaseCount} / 7 {statusIcon(phaseStatus)}
            </div>
          </div>
        </div>
      </div>

      <div className={styles.issues}>
        {issues.map((issue, i) => (
          <div key={i} className={`${styles.issue} ${styles[issue.level]}`}>
            <div className="tag">{issue.level}</div>
            <div className="txt">{translateIssueMessage(lang, issue.message)}</div>
          </div>
        ))}
      </div>

      <div className={styles.chartWrap}>
        <h3 className="tracked">{t("result_chart_title")}</h3>
        <div className={styles.chartPanel}>
          <Waveform wristY={wrist_y_history} phaseBoundaries={phase_boundaries} />
        </div>
      </div>

      <div className={styles.phaseRow}>
        {PHASE_ORDER_KO.filter((ph) => rep_frames[ph]).map((ph) => (
          <div key={ph} className={styles.phaseCell}>
            <div className={styles.phaseThumb}>
              <img src={`data:image/jpeg;base64,${rep_frames[ph]}`} alt={phaseLabel(ph)} />
            </div>
            <div className="cap mono">{phaseLabel(ph).toUpperCase()}</div>
          </div>
        ))}
      </div>

      {saveError && <div className={styles.saveError}>{saveError}</div>}

      {replay && (
        <SwingReplay
          source={replay}
          phaseBoundaries={phase_boundaries}
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
        onLoginClick={onLoginClick}
      />
    </div>
  );
}
