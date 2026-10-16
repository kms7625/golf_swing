import { useI18n } from "../lib/i18n";
import styles from "./RecordingGuide.module.css";

const ITEMS = [
  ["guide_1_head", "guide_1"],
  ["guide_2_head", "guide_2"],
  ["guide_3_head", "guide_3"],
  ["guide_4_head", "guide_4"],
  ["guide_5_head", "guide_5"],
  ["guide_6_head", "guide_6"],
] as const;

export function RecordingGuide() {
  const { t } = useI18n();
  return (
    <section className={styles.guide} aria-labelledby="recording-guide-title">
      <h2 id="recording-guide-title">{t("guide_title")}</h2>
      <ol>
        {ITEMS.map(([head, body], i) => (
          <li key={head}>
            <span className={styles.num} aria-hidden="true">{i + 1}</span>
            <div><strong>{t(head)}</strong><p>{t(body)}</p></div>
          </li>
        ))}
      </ol>
    </section>
  );
}
