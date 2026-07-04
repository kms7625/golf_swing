import type { AnalyzeResponse } from "../lib/types";
import { PHASE_ORDER_KO } from "../lib/types";
import { getStatus } from "../lib/status";
import { useI18n } from "../lib/i18n";
import { translateIssueMessage } from "../lib/issueMessages";
import { Waveform } from "./Waveform";
import { CoachingPanel } from "./CoachingPanel";
import styles from "./ResultScreen.module.css";

interface Props {
  result: AnalyzeResponse;
  isSample: boolean;
  onBack: () => void;
}

function grade(score: number): string {
  if (score >= 95) return "S";
  if (score >= 85) return "A";
  if (score >= 70) return "B";
  if (score >= 55) return "C";
  return "D";
}

export function ResultScreen({ result, isSample, onBack }: Props) {
  const { t, lang, phaseLabel } = useI18n();
  const { score, issues, summary, rep_frames, wrist_y_history, phase_boundaries } = result;

  const spineStatus = getStatus(summary.spine_angle_delta, 0, 5, 5, 10);
  const xfactorStatus = getStatus(summary.x_factor, 35, 55, 20, 60);
  const phaseCount = summary.phases_detected.length;
  const phaseStatus = phaseCount >= 5 ? "ok" : "warn";

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <span className={styles.sectionTitle}>{t("result_phases_title")}</span>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {isSample && <span className={styles.sampleBadge}>{t("sample_badge")}</span>}
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
            <div className={`v ${spineStatus} tabular mono`}>{summary.spine_angle_delta}°</div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_xfactor")}</div>
            <div className={`v ${xfactorStatus} tabular mono`}>{summary.x_factor}°</div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_shoulder")}</div>
            <div className="v tabular mono">{summary.shoulder_rotation_max}°</div>
          </div>
          <div className={styles.statTile}>
            <div className="k tracked">{t("result_metric_phases")}</div>
            <div className={`v ${phaseStatus} tabular mono`}>{phaseCount} / 7</div>
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

      <CoachingPanel summary={summary} issues={issues} />
    </div>
  );
}
