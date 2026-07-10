import { useI18n } from "../lib/i18n";
import type { JobStage } from "../lib/types";
import styles from "./AnalyzeProgress.module.css";

interface Props {
  stage: JobStage;
  progress: number;
}

const STAGE_ORDER: JobStage[] = ["uploaded", "trimming", "analyzing", "scoring", "done"];

export function AnalyzeProgress({ stage, progress }: Props) {
  const { t } = useI18n();
  const current = STAGE_ORDER.indexOf(stage);

  return (
    <div className={styles.wrap}>
      <h2>{t("analyzing_title")}</h2>
      <div
        className={styles.barTrack}
        role="progressbar"
        aria-valuenow={progress}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div className={styles.barFill} style={{ width: `${progress}%` }} />
      </div>
      <div className={`${styles.pct} mono tabular`}>{progress}%</div>
      <ul className={styles.steps}>
        {STAGE_ORDER.map((s, i) => (
          <li
            key={s}
            className={i < current ? styles.doneStep : i === current ? styles.activeStep : styles.pendingStep}
          >
            <span className={styles.mark}>{i < current ? "✔" : i === current ? "▶" : "·"}</span>
            {t(`job_stage_${s}`)}
          </li>
        ))}
      </ul>
    </div>
  );
}
