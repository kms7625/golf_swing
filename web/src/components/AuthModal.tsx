import { useCallback, useState } from "react";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { GoogleLoginButton, googleLoginEnabled } from "./GoogleLoginButton";
import styles from "./AuthModal.module.css";

/** 로그인은 Google 계정으로만 — 이메일 가입은 무료 코칭 횟수용 계정 양산을 막으려고 없앴다. */

interface Props {
  onClose: () => void;
}

export function AuthModal({ onClose }: Props) {
  const { t } = useI18n();
  const { loginWithGoogle } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onGoogleCredential = useCallback(
    async (credential: string) => {
      setLoading(true);
      setError(null);
      try {
        await loginWithGoogle(credential);
        onClose();
      } catch (err) {
        setError(err instanceof Error ? err.message : t("error_generic"));
      } finally {
        setLoading(false);
      }
    },
    [loginWithGoogle, onClose, t],
  );

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <h3 className="tracked">{t("auth_title_login")}</h3>
        <p className={styles.note}>{t("auth_google_note")}</p>
        {googleLoginEnabled ? (
          <div className={styles.google} aria-busy={loading}>
            <GoogleLoginButton onCredential={onGoogleCredential} onError={setError} />
          </div>
        ) : (
          <div className={styles.error}>{t("auth_google_unavailable")}</div>
        )}
        {error && <div className={styles.error}>{error}</div>}
        <button className={styles.close} onClick={onClose} aria-label={t("auth_close")}>
          ✕
        </button>
      </div>
    </div>
  );
}
