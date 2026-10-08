import { useI18n } from "../lib/i18n";
import { PlayIcon, UploadIcon } from "./icons";
import styles from "./Hero.module.css";

interface Props {
  onUpload: () => void;
  onViewSample: () => void;
}

export function Hero({ onUpload, onViewSample }: Props) {
  const { t } = useI18n();

  return (
    <div className={styles.hero}>
      <div>
        <p className={`${styles.eyebrow} tracked`}>{t("hero_eyebrow")}</p>
        <h1>
          {t("hero_title_1")}
          <br />
          {t("hero_title_2")}
        </h1>
        <p className={styles.lede}>{t("hero_lede")}</p>
        <div className={styles.ctaRow}>
          <button className={`${styles.btn} ${styles.btnPrimary}`} onClick={onUpload}>
            <UploadIcon />
            {t("hero_cta_upload")}
          </button>
          <button className={`${styles.btn} ${styles.btnGhost}`} onClick={onViewSample}>
            <PlayIcon />
            {t("hero_cta_sample")}
          </button>
        </div>
      </div>
      <div className={styles.panel}>
        <div className={`${styles.bracket} ${styles.tl}`} />
        <div className={`${styles.bracket} ${styles.tr}`} />
        <div className={`${styles.bracket} ${styles.bl}`} />
        <div className={`${styles.bracket} ${styles.br}`} />
        <div className={styles.visual}>
          <img src="/images/hero-swing.webp" width="1152" height="864" alt={t("hero_visual_alt")} />
        </div>
        <div className={`${styles.readout} mono`}>
          <span>SPINE 29.4°</span>
          <span>SHOULDER 64.2°</span>
          <span>FRAME 0187/0266</span>
        </div>
      </div>
    </div>
  );
}
