import { useEffect, useRef, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { deleteAccount, deleteSwing, getSwing, listSwings } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import type { AnalyzeResponse, SwingRow } from "../lib/types";
import styles from "./HistoryPanel.module.css";

interface Props {
  onOpen: (result: AnalyzeResponse, swingId: number, feedback: string, filename: string, returnFocus?: HTMLElement) => void;
  onLoginClick: () => void;
  onNewAnalysis: () => void;
}

function fmtDate(iso: string): string {
  const d = new Date(iso.endsWith("Z") || iso.includes("+") ? iso : iso + "Z");
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(
    d.getMinutes()
  ).padStart(2, "0")}`;
}

/** 점수 추이 — 단일 시리즈 라인 (제목이 시리즈명을 대신하므로 범례 없음, 표 역할은 아래 기록 목록) */
function TrendChart({ rows }: { rows: SwingRow[] }) {
  const data = [...rows].reverse().map((r) => ({ label: fmtDate(r.created_at).split(" ")[0], score: r.score }));
  return (
    <div className={styles.trendChart}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: 12 }}>
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: "var(--steel)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis width={32} domain={[0, 100]} ticks={[0, 50, 100]} tick={{ fontSize: 12, fill: "var(--steel)" }} axisLine={false} tickLine={false} />
          <Tooltip
            isAnimationActive={false}
            contentStyle={{
              background: "var(--graphite-2)",
              border: "1px solid var(--graphite-3)",
              color: "var(--text)",
              fontSize: 12,
            }}
            labelStyle={{ color: "var(--steel)" }}
            formatter={(value) => [String(value), ""]}
          />
          <Line
            type="monotone"
            dataKey="score"
            stroke="var(--teal)"
            strokeWidth={2}
            dot={{ r: 3.5, fill: "var(--teal)", strokeWidth: 0 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

/** 변화량만 표시하며 개선/악화 판정을 추가하지 않는다. */
function MetricTrends({ rows }: { rows: SwingRow[] }) {
  const { t } = useI18n();
  const first = rows[rows.length - 1];
  const last = rows[0];
  const items: { label: string; from: number; to: number }[] = [
    { label: t("result_metric_spine"), from: first.spine_angle_delta, to: last.spine_angle_delta },
    { label: t("result_metric_xfactor"), from: first.x_factor, to: last.x_factor },
    { label: t("result_metric_shoulder"), from: first.shoulder_rotation_max, to: last.shoulder_rotation_max },
  ];
  return (
    <div className={styles.metricTrends}>
      <div className={styles.metricTrendsTitle}>{t("trend_metrics")}</div>
      {items.map((m) => {
        const diff = m.to - m.from;
        const flat = Math.abs(diff) < 0.05;
        return (
          <div key={m.label} className={styles.metricRow}>
            <span className={styles.metricLabel}>{m.label}</span>
            <span className={`mono tabular ${styles.metricVals}`}>
              {m.from}° → {m.to}°{" "}
              <span className={styles.change}>
                {flat ? "—" : `${diff > 0 ? "+" : "−"}${Math.abs(diff).toFixed(1)}°`}
              </span>
            </span>
          </div>
        );
      })}
      <p className={styles.hint}>{t("trend_neutral_hint")}</p>
    </div>
  );
}

export function HistoryPanel({ onOpen, onLoginClick, onNewAnalysis }: Props) {
  const { t } = useI18n();
  const { isLoggedIn, email, logout } = useAuth();
  const [rows, setRows] = useState<SwingRow[]>([]);
  const [loading, setLoading] = useState(isLoggedIn);
  const [loadFailed, setLoadFailed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [busy, setBusy] = useState<number | "account" | null>(null);
  const requestRef = useRef(0);

  async function refresh() {
    const request = ++requestRef.current;
    setLoading(true);
    setLoadFailed(false);
    try {
      const res = await listSwings();
      if (request === requestRef.current) setRows(res.swings);
    } catch {
      if (request === requestRef.current) setLoadFailed(true);
    } finally {
      if (request === requestRef.current) setLoading(false);
    }
  }

  useEffect(() => {
    setRows([]);
    setError(null);
    setDeleteId(null);
    setConfirmingDelete(false);
    if (isLoggedIn) refresh();
    return () => { requestRef.current += 1; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoggedIn, email]);

  async function open(row: SwingRow) {
    const trigger = document.activeElement as HTMLElement;
    const request = requestRef.current;
    setBusy(row.id);
    setError(null);
    try {
      const detail = await getSwing(row.id);
      if (request !== requestRef.current) return;
      onOpen(detail.payload, detail.id, detail.feedback, row.video_name, trigger);
    } catch {
      setError(t("history_open_failed"));
    } finally { setBusy(null); }
  }

  function cancelDelete() {
    const id = deleteId;
    setDeleteId(null);
    requestAnimationFrame(() => document.getElementById(`delete-${id}`)?.focus());
  }

  async function remove(row: SwingRow) {
    setBusy(row.id);
    setError(null);
    try {
      await deleteSwing(row.id);
      setRows((rs) => rs.filter((r) => r.id !== row.id));
      setDeleteId(null);
    } catch { setError(t("history_delete_failed")); }
    finally { setBusy(null); }
  }

  async function removeAccount() {
    setBusy("account");
    setError(null);
    try {
      await deleteAccount();
      setConfirmingDelete(false);
      setRows([]);
      logout();
    } catch { setError(t("account_delete_failed")); }
    finally { setBusy(null); }
  }

  const trend = rows.length >= 2 ? Math.round((rows[0].score - rows[rows.length - 1].score) * 10) / 10 : null;

  return (
    <main className={styles.wrap}>
      <header className={styles.header}>
        <div><h1>{t("history_title")}</h1><p className={styles.hint}>{email ?? t("history_login_hint")}</p></div>
        <button className={styles.cta} onClick={onNewAnalysis}>{t("result_back")}</button>
      </header>
      {!isLoggedIn ? (
        <section className={styles.card}><p className={styles.hint}>{t("history_login_hint")}</p><button className={styles.cta} onClick={onLoginClick}>{t("auth_login")}</button></section>
      ) : (
        <>
          {error && <div className={styles.error} role="alert"><p>⚠ {error}</p><button className={styles.secondary} onClick={refresh} disabled={loading || busy !== null}>{t("history_reload")}</button></div>}
          <div className={styles.layout}>
            <section className={styles.card} aria-labelledby="history-recent" aria-busy={loading}>
              <h2 id="history-recent">{t("history_recent")} · {rows.length}</h2>
              {loading && <p className={styles.hint} role="status">◷ {t("history_loading")}</p>}
              {loadFailed && <div className={styles.loadError} role="alert"><p>⚠ {t("history_load_failed")}</p><button className={styles.secondary} onClick={refresh} disabled={loading}>{t("history_reload")}</button></div>}
              {!loading && !loadFailed && rows.length === 0 && <div className={styles.empty}><p className={styles.hint}>{t("history_empty")}</p><button className={styles.secondary} onClick={onNewAnalysis}>{t("history_first_analysis")}</button></div>}
              <div className={styles.list}>
                {rows.map((row) => (
                  <div key={row.id}>
                    <div className={styles.row}>
                      <span className={`${styles.score} tabular`}>{row.score}<span className="srOnly"> {t("compare_score")}</span></span>
                      <span className={styles.meta}><time className={styles.date}>{fmtDate(row.created_at)}</time><span className={styles.name}>{row.video_name}</span></span>
                      <div className={styles.rowActions}>
                        <button className={styles.secondary} onClick={() => open(row)} disabled={busy !== null} aria-label={`${t("history_open")}: ${row.video_name}`}>{busy === row.id && deleteId !== row.id ? t("history_loading") : t("history_open")}</button>
                        <button id={`delete-${row.id}`} className={styles.del} onClick={() => setDeleteId(row.id)} disabled={busy !== null} aria-label={`${t("history_delete")}: ${row.video_name}`}>{t("history_delete")}</button>
                      </div>
                    </div>
                    {deleteId === row.id && <div className={styles.confirmBox} onKeyDown={(e) => { if (e.key === "Escape" && busy === null) cancelDelete(); }}>
                      <h3>{t("history_delete_question")}</h3><strong>{row.video_name}</strong><p>{fmtDate(row.created_at)} · {row.score}</p><p>{t("history_delete_scope")}</p>
                      <div className={styles.confirmBtns}><button className={styles.secondary} onClick={cancelDelete} disabled={busy !== null} autoFocus>{t("account_delete_cancel")}</button><button className={styles.confirmYes} onClick={() => remove(row)} disabled={busy !== null}>{busy === row.id ? t("history_deleting") : t("history_delete_record")}</button></div>
                    </div>}
                  </div>
                ))}
              </div>
            </section>
            <section className={styles.card} aria-labelledby="history-trend">
              <div className={styles.head}><h2 id="history-trend">{t("trend_title")}</h2>{trend !== null && <span className={`${styles.trend} tabular`}>{t("trend_since_first")} {trend > 0 ? "+" : ""}{trend}</span>}</div>
              {rows.length >= 2 ? <><TrendChart rows={rows} /><MetricTrends rows={rows} /></> : <p className={styles.hint}>{t("trend_need_more")}</p>}
            </section>
          </div>
          <section className={styles.accountZone} aria-labelledby="account-title">
            <h2 id="account-title">{t("account_management")}</h2>
            {confirmingDelete ? <div className={styles.confirmBox}>
              <p>⚠ {t("account_delete_confirm")}</p>
              <div className={styles.confirmBtns}><button className={styles.secondary} onClick={() => setConfirmingDelete(false)} disabled={busy !== null} autoFocus>{t("account_delete_cancel")}</button><button className={styles.confirmYes} onClick={removeAccount} disabled={busy !== null}>{busy === "account" ? t("history_deleting") : t("account_delete_yes")}</button></div>
            </div> : <button className={styles.accountDelete} onClick={() => setConfirmingDelete(true)}>{t("account_delete")}</button>}
          </section>
        </>
      )}
    </main>
  );
}
