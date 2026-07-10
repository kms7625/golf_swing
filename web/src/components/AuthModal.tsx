import { useState, type FormEvent } from "react";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import styles from "./AuthModal.module.css";

interface Props {
  onClose: () => void;
}

export function AuthModal({ onClose }: Props) {
  const { t } = useI18n();
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("error_generic"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <h3 className="tracked">{mode === "login" ? t("auth_title_login") : t("auth_title_register")}</h3>
        <form onSubmit={onSubmit}>
          <label>
            {t("auth_email")}
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label>
            {t("auth_password")}
            <input
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </label>
          {error && <div className={styles.error}>{error}</div>}
          <button className={styles.submit} type="submit" disabled={loading}>
            {mode === "login" ? t("auth_submit_login") : t("auth_submit_register")}
          </button>
        </form>
        <button
          className={styles.switchMode}
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
        >
          {mode === "login" ? t("auth_to_register") : t("auth_to_login")}
        </button>
        <button className={styles.close} onClick={onClose} aria-label={t("auth_close")}>
          ✕
        </button>
      </div>
    </div>
  );
}
