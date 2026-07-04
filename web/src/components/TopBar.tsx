import { useI18n } from "../lib/i18n";
import styles from "./TopBar.module.css";

interface Props {
  onBrandClick: () => void;
}

export function TopBar({ onBrandClick }: Props) {
  const { t, lang, setLang } = useI18n();

  return (
    <div className={styles.bar}>
      <button className={styles.brand} onClick={onBrandClick}>
        SWING<span className={`mono ${styles.accent}`}>.LAB</span>
      </button>
      <div className={styles.right}>
        <nav className={styles.nav}>
          <a>{t("nav_analyze")}</a>
          <a>{t("nav_sample")}</a>
        </nav>
        <div className={styles.langToggle}>
          <button className={lang === "ko" ? styles.active : ""} onClick={() => setLang("ko")}>
            KO
          </button>
          <button className={lang === "en" ? styles.active : ""} onClick={() => setLang("en")}>
            EN
          </button>
        </div>
      </div>
    </div>
  );
}
