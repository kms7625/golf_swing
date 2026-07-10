import { useState } from "react";
import { coaching } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { MODEL_OPTIONS, type Issue, type Provider, type Summary } from "../lib/types";
import { Markdown } from "./Markdown";
import styles from "./CoachingPanel.module.css";

interface Props {
  summary: Summary;
  issues: Issue[];
  /** 저장된 스윙에서 열었을 때 — 생성한 리포트를 해당 스윙에 저장 */
  swingId?: number;
  /** 저장된 스윙에 이미 붙어 있던 리포트 */
  initialFeedback?: string;
  onLoginClick: () => void;
}

export function CoachingPanel({ summary, issues, swingId, initialFeedback, onLoginClick }: Props) {
  const { t } = useI18n();
  const { isLoggedIn } = useAuth();
  const [provider, setProvider] = useState<Provider>("Gemini");
  const [modelName, setModelName] = useState(MODEL_OPTIONS.Gemini[0]);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(initialFeedback || null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handleProviderChange(p: Provider) {
    setProvider(p);
    setModelName(MODEL_OPTIONS[p][0]);
  }

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    setFeedback(null);
    try {
      const res = await coaching({ summary, issues, provider, modelName, swingId });
      setFeedback(res.feedback);
      setRemaining(res.remaining);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.wrap}>
      <h3>{t("coaching_title")}</h3>

      {!isLoggedIn ? (
        <div className={styles.loginGate}>
          <p>{t("coaching_login_required")}</p>
          <button className={styles.generateBtn} onClick={onLoginClick}>
            {t("auth_login")}
          </button>
        </div>
      ) : (
        <div className={styles.controls}>
          <div className={styles.field}>
            <label>{t("coaching_provider")}</label>
            <select value={provider} onChange={(e) => handleProviderChange(e.target.value as Provider)}>
              {(Object.keys(MODEL_OPTIONS) as Provider[]).map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
          <div className={styles.field}>
            <label>{t("coaching_model")}</label>
            <select value={modelName} onChange={(e) => setModelName(e.target.value)}>
              {MODEL_OPTIONS[provider].map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>
          <button className={styles.generateBtn} onClick={handleGenerate} disabled={loading}>
            {t("coaching_generate")}
          </button>
        </div>
      )}

      {remaining !== null && (
        <div className={styles.status}>
          {t("coaching_remaining")}: <span className="mono tabular">{remaining}</span>
        </div>
      )}
      {loading && <div className={styles.status}>{t("coaching_generating")}</div>}
      {error && <div className={styles.error}>{error}</div>}
      {feedback && (
        <div className={styles.report}>
          <Markdown text={feedback} />
        </div>
      )}
    </div>
  );
}
