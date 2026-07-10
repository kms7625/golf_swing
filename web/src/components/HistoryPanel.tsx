import { useEffect, useState } from "react";
import { deleteSwing, getSwing, listSwings } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import type { AnalyzeResponse, SwingRow } from "../lib/types";
import styles from "./HistoryPanel.module.css";

interface Props {
  onOpen: (result: AnalyzeResponse, swingId: number, feedback: string) => void;
  onLoginClick: () => void;
}

function fmtDate(iso: string): string {
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(
    d.getMinutes()
  ).padStart(2, "0")}`;
}

export function HistoryPanel({ onOpen, onLoginClick }: Props) {
  const { t } = useI18n();
  const { isLoggedIn } = useAuth();
  const [rows, setRows] = useState<SwingRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const res = await listSwings();
      setRows(res.swings);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (isLoggedIn) refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoggedIn]);

  async function open(row: SwingRow) {
    try {
      const detail = await getSwing(row.id);
      onOpen(detail.payload, detail.id, detail.feedback);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  async function remove(row: SwingRow) {
    try {
      await deleteSwing(row.id);
      setRows((rs) => rs.filter((r) => r.id !== row.id));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  if (!isLoggedIn) {
    return (
      <div className={styles.wrap}>
        <h3 className="tracked">{t("history_title")}</h3>
        <p className={styles.hint}>{t("history_login_hint")}</p>
        <button className={styles.cta} onClick={onLoginClick}>
          {t("auth_login")}
        </button>
      </div>
    );
  }

  const scores = rows.map((r) => r.score);
  const trend =
    scores.length >= 2 ? Math.round((scores[0] - scores[scores.length - 1]) * 10) / 10 : null;

  return (
    <div className={styles.wrap}>
      <div className={styles.head}>
        <h3 className="tracked">{t("history_title")}</h3>
        {trend !== null && (
          <span className={`${styles.trend} mono tabular`}>
            {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}
          </span>
        )}
      </div>
      {error && <div className={styles.error}>{error}</div>}
      {loading && <div className={styles.hint}>…</div>}
      {!loading && rows.length === 0 && <p className={styles.hint}>{t("history_empty")}</p>}
      <div className={styles.list}>
        {rows.map((row) => (
          <div key={row.id} className={styles.row}>
            <button className={styles.rowMain} onClick={() => open(row)} title={t("history_open")}>
              <span className={`${styles.score} mono tabular`}>{row.score}</span>
              <span className={styles.meta}>
                <span className={styles.date}>{fmtDate(row.created_at)}</span>
                <span className={styles.name}>{row.video_name}</span>
              </span>
              <span className={`${styles.mini} mono tabular`}>
                XF {row.x_factor}° · SP {row.spine_angle_delta}°
              </span>
            </button>
            <button className={styles.del} onClick={() => remove(row)} aria-label={t("history_delete")}>
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
