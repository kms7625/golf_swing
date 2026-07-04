import { useState } from "react";
import { coaching } from "../lib/api";
import { useI18n } from "../lib/i18n";
import { MODEL_OPTIONS, type Issue, type Provider, type Summary } from "../lib/types";
import styles from "./CoachingPanel.module.css";

interface Props {
  summary: Summary;
  issues: Issue[];
}

export function CoachingPanel({ summary, issues }: Props) {
  const { t } = useI18n();
  const [provider, setProvider] = useState<Provider>("Gemini");
  const [modelName, setModelName] = useState(MODEL_OPTIONS.Gemini[0]);
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handleProviderChange(p: Provider) {
    setProvider(p);
    setModelName(MODEL_OPTIONS[p][0]);
  }

  async function handleGenerate() {
    if (!apiKey) {
      setError(t("coaching_need_key"));
      return;
    }
    setLoading(true);
    setError(null);
    setFeedback(null);
    try {
      const res = await coaching({ summary, issues, provider, apiKey, modelName });
      setFeedback(res.feedback);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.wrap}>
      <h3>{t("coaching_title")}</h3>
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
        <div className={styles.field}>
          <label>{t("coaching_key")}</label>
          <input
            type="password"
            placeholder={t("coaching_key_placeholder")}
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </div>
        <button className={styles.generateBtn} onClick={handleGenerate} disabled={loading}>
          {t("coaching_generate")}
        </button>
      </div>

      {loading && <div className={styles.status}>{t("coaching_generating")}</div>}
      {error && <div className={styles.error}>{error}</div>}
      {feedback && <div className={styles.report}>{feedback}</div>}
    </div>
  );
}
