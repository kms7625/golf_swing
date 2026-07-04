import { useI18n } from "../lib/i18n";
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
            {t("hero_cta_upload")}
          </button>
          <button className={`${styles.btn} ${styles.btnGhost}`} onClick={onViewSample}>
            {t("hero_cta_sample")}
          </button>
        </div>
      </div>
      <div className={styles.panel}>
        <div className={`${styles.bracket} ${styles.tl}`} />
        <div className={`${styles.bracket} ${styles.tr}`} />
        <div className={`${styles.bracket} ${styles.bl}`} />
        <div className={`${styles.bracket} ${styles.br}`} />
        <svg viewBox="0 0 120 160" className={styles.skeleton}>
          <g fill="none" stroke="#dd8b57" strokeWidth="2" strokeLinecap="round">
            <circle cx="60" cy="20" r="9" stroke="#5fb8b0" />
            <path d="M60 29 L60 75" />
            <path d="M60 40 L30 55 L20 90" />
            <path d="M60 40 L92 30 L100 8" />
            <path d="M60 75 L40 120 L34 155" />
            <path d="M60 75 L82 120 L90 155" />
          </g>
          <g fill="#5fb8b0">
            <circle cx="60" cy="40" r="2.4" />
            <circle cx="30" cy="55" r="2.4" />
            <circle cx="20" cy="90" r="2.4" />
            <circle cx="92" cy="30" r="2.4" />
            <circle cx="100" cy="8" r="2.4" />
            <circle cx="60" cy="75" r="2.4" />
            <circle cx="40" cy="120" r="2.4" />
            <circle cx="34" cy="155" r="2.4" />
            <circle cx="82" cy="120" r="2.4" />
            <circle cx="90" cy="155" r="2.4" />
          </g>
        </svg>
        <div className={`${styles.readout} mono`}>
          <span>SPINE 29.4°</span>
          <span>SHOULDER 64.2°</span>
          <span>FRAME 0187/0266</span>
        </div>
      </div>
    </div>
  );
}
