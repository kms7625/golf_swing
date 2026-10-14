import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { GoogleLoginButton, googleLoginEnabled } from "./GoogleLoginButton";
import styles from "./AuthModal.module.css";

export type AuthPurpose = "general" | "save" | "coaching" | "history";

interface Props {
  onClose: () => void;
  onPrivacyClick: () => void;
  purpose: AuthPurpose;
  suspended: boolean;
}

export function AuthModal({ onClose, onPrivacyClick, purpose, suspended }: Props) {
  const { t, lang } = useI18n();
  const { loginWithGoogle } = useAuth();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLElement | null>(document.activeElement as HTMLElement);
  const backdropPressRef = useRef(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    const dialog = dialogRef.current;
    const trigger = triggerRef.current;
    return () => {
      dialog?.close();
      trigger?.focus({ preventScroll: true });
    };
  }, []);

  useLayoutEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (suspended) dialog.close();
    else if (!dialog.open) dialog.showModal();
  }, [suspended]);

  const onGoogleError = useCallback(() => setError(true), []);
  const onGoogleCredential = useCallback(
    async (credential: string) => {
      setLoading(true);
      setError(false);
      try {
        await loginWithGoogle(credential);
        onClose();
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    },
    [loginWithGoogle, onClose],
  );

  return (
    <dialog ref={dialogRef} className={styles.modal} aria-modal="true" aria-labelledby="auth-title" aria-describedby="auth-purpose"
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      onPointerDown={(e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        backdropPressRef.current = e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom;
      }}
      onClick={(e) => { if (e.target === e.currentTarget && backdropPressRef.current) onClose(); }}>
      <button className={styles.close} onClick={onClose} autoFocus>
        <span aria-hidden="true">✕</span> {t("auth_close")}
      </button>
      <h1 id="auth-title">{t("auth_title_login")}</h1>
      <p id="auth-purpose" className={styles.purpose}>{t(`auth_purpose_${purpose}`)}</p>
      <p className={styles.note}>{t("auth_google_note")}</p>
      {googleLoginEnabled ? (
        <div className={styles.google} aria-busy={loading} inert={loading}>
          <GoogleLoginButton lang={lang} onCredential={onGoogleCredential} onError={onGoogleError} />
        </div>
      ) : (
        <p className={styles.error} role="status">⚠ {t("auth_google_unavailable")}</p>
      )}
      {loading && <p className={styles.processing} role="status">◷ {t("auth_processing")}</p>}
      {error && <p className={styles.error} role="alert">⚠ {t("auth_failed")}</p>}
      <div className={styles.privacy}>
        <p>{t("auth_privacy_hint")}</p>
        <button onClick={onPrivacyClick}>{t("privacy_link")} →</button>
      </div>
    </dialog>
  );
}
