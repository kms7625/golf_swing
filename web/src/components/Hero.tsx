import { useI18n } from "../lib/i18n";
import { PlayIcon, UploadIcon } from "./icons";
import styles from "./Hero.module.css";

interface Props {
  onUpload: () => void;
  onViewSample: () => void;
  onHistory: () => void;
}

export function Hero({ onUpload, onViewSample, onHistory }: Props) {
  const { t } = useI18n();
  return (
    <main className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.copy}>
          <h1>{t("hero_title_1")}<br />{t("hero_title_2")}</h1>
          <p className={styles.lede}>{t("hero_intro")}</p>
          <div className={styles.ctaRow}>
            <button className={`${styles.btn} ${styles.btnPrimary}`} onClick={onUpload}>
              <UploadIcon />{t("hero_cta_upload")}
            </button>
            <button className={`${styles.btn} ${styles.btnGhost}`} onClick={onViewSample}>
              <PlayIcon />{t("hero_cta_sample")}
            </button>
          </div>
          <p className={styles.hint}>{t("hero_recording_hint")}</p>
        </div>
        <figure className={styles.panel}>
          <img src="/images/hero-photo.webp" width="732" height="675" alt={t("hero_cobalt_alt")} />
          <figcaption>{t("image_example")}</figcaption>
        </figure>
      </div>
      <div className={styles.wrap}>
      <section className={styles.history}>
        <div><h2>{t("history_title")}</h2><p>{t("history_login_hint")}</p></div>
        <button className={`${styles.btn} ${styles.btnGhost}`} onClick={onHistory}>
          {t("nav_history")} <span aria-hidden="true">→</span>
        </button>
      </section>
      </div>
    </main>
  );
}
