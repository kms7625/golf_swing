import { useState } from "react";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { getTheme, toggleTheme, type Theme } from "../lib/theme";
import { HistoryIcon, MoonIcon, SunIcon, VideoCameraIcon } from "./icons";
import styles from "./TopBar.module.css";

interface Props {
  onBrandClick: () => void;
  onLiveClick: () => void;
  onHistoryClick: () => void;
  onLoginClick: () => void;
}

export function TopBar({ onBrandClick, onLiveClick, onHistoryClick, onLoginClick }: Props) {
  const { t, lang, setLang } = useI18n();
  const { isLoggedIn, email, logout } = useAuth();
  const [theme, setTheme] = useState<Theme>(getTheme());

  return (
    <div className={styles.bar}>
      <button className={styles.brand} onClick={onBrandClick}>
        SWING<span className={`mono ${styles.accent}`}>.LAB</span>
      </button>
      <div className={styles.right}>
        <nav className={styles.nav}>
          <button onClick={onLiveClick}><VideoCameraIcon />{t("nav_live")}</button>
          <button onClick={onHistoryClick}><HistoryIcon />{t("nav_history")}</button>
        </nav>
        <button
          className={styles.iconBtn}
          onClick={() => setTheme(toggleTheme())}
          aria-label={t("theme_toggle")}
          title={t("theme_toggle")}
        >
          {theme === "dark" ? <SunIcon /> : <MoonIcon />}
        </button>
        <div className={styles.langToggle}>
          <button className={lang === "ko" ? styles.active : ""} onClick={() => setLang("ko")}>
            KO
          </button>
          <button className={lang === "en" ? styles.active : ""} onClick={() => setLang("en")}>
            EN
          </button>
        </div>
        {isLoggedIn ? (
          <button className={styles.authBtn} onClick={logout} title={email ?? undefined}>
            {t("auth_logout")}
          </button>
        ) : (
          <button className={styles.authBtn} onClick={onLoginClick}>
            {t("auth_login")}
          </button>
        )}
      </div>
    </div>
  );
}
