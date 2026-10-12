import { useI18n } from "../lib/i18n";
import type { JobStage } from "../lib/types";
import styles from "./AnalyzeProgress.module.css";

interface Props {
  stage: JobStage;
  progress: number;
  filename: string;
  onBack: () => void;
}
const STAGE_ORDER: JobStage[] = ["uploaded", "trimming", "analyzing", "scoring", "done"];

export function AnalyzeProgress({ stage, progress, filename, onBack }: Props) {
  const { t } = useI18n();
  const current = STAGE_ORDER.indexOf(stage);
  return (
    <main className={styles.wrap}>
      <h1>{t("analyzing_title")}</h1>
      <p className={styles.filename}>{filename}</p>
      <section className={styles.card}>
        <div className={styles.summary}>
          <h2 id="analysis-progress-label">{t("progress_label")}</h2>
          <span className={`${styles.pct} tabular`}>{progress}%</span>
        </div>
        <div className={styles.barTrack} role="progressbar" aria-labelledby="analysis-progress-label"
          aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
          <div className={styles.barFill} style={{ width: `${progress}%` }} />
        </div>
        <p>{t("progress_hint")}</p>
      </section>
      <p className="srOnly" role="status">{progress === 0 ? t("job_uploading") : t(`job_stage_${stage}`)} {progress}%</p>
      <ol className={styles.steps}>
        {STAGE_ORDER.map((s, i) => {
          const done = i < current || stage === "done" || (s === "uploaded" && progress > 0);
          const active = i === current && !done;
          return (
            <li key={s} aria-current={active ? "step" : undefined}
              className={done ? styles.doneStep : active ? styles.activeStep : styles.pendingStep}>
              <span className={styles.mark} aria-hidden="true">{done ? "✓" : active ? "▶" : "○"}</span>
              <span>{s === "uploaded" && progress === 0 ? t("job_uploading") : t(`job_stage_${s}`)}</span>
              <span className={styles.state}>{done ? t("job_stage_done") : active ? t("progress_active") : t("progress_pending")}</span>
            </li>
          );
        })}
      </ol>
      <div className={styles.footer}>
        <button onClick={onBack} aria-describedby="analysis-leave-hint"><span aria-hidden="true">← </span>{t("progress_back")}</button>
        <div id="analysis-leave-hint" className={styles.hint}>
          <p>{t("progress_leave_result")}</p>
          <p>{t("progress_leave_server")}</p>
          <p>{t("progress_leave_retry")}</p>
        </div>
      </div>
    </main>
  );
}
