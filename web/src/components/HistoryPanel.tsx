import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { deleteAccount, deleteSwing, getSwing, listSwings } from "../lib/api";
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
          <YAxis hide domain={[0, 100]} />
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

/** 지표별 처음→최근 변화 — 지표마다 개선 방향이 달라 색은 방향 의미에 맞게 */
function MetricTrends({ rows }: { rows: SwingRow[] }) {
  const { t } = useI18n();
  const first = rows[rows.length - 1];
  const last = rows[0];
  const items: { label: string; from: number; to: number; betterWhenLower: boolean }[] = [
    { label: t("result_metric_spine"), from: first.spine_angle_delta, to: last.spine_angle_delta, betterWhenLower: true },
    { label: t("result_metric_xfactor"), from: first.x_factor, to: last.x_factor, betterWhenLower: false },
    { label: t("result_metric_shoulder"), from: first.shoulder_rotation_max, to: last.shoulder_rotation_max, betterWhenLower: false },
  ];
  return (
    <div className={styles.metricTrends}>
      <div className={styles.metricTrendsTitle}>{t("trend_metrics")}</div>
      {items.map((m) => {
        const diff = m.to - m.from;
        const improved = m.betterWhenLower ? diff < 0 : diff > 0;
        const flat = Math.abs(diff) < 0.05;
        return (
          <div key={m.label} className={styles.metricRow}>
            <span className={styles.metricLabel}>{m.label}</span>
            <span className={`mono tabular ${styles.metricVals}`}>
              {m.from}° → {m.to}°{" "}
              <span className={flat ? styles.flat : improved ? styles.improved : styles.worsened}>
                {flat ? "—" : diff > 0 ? "▲" : "▼"}
              </span>
            </span>
          </div>
        );
      })}
    </div>
  );
}

export function HistoryPanel({ onOpen, onLoginClick }: Props) {
  const { t } = useI18n();
  const { isLoggedIn, logout } = useAuth();
  const [rows, setRows] = useState<SwingRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

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

  async function removeAccount() {
    try {
      await deleteAccount();
      setConfirmingDelete(false);
      setRows([]);
      logout();
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
      {rows.length >= 2 && (
        <>
          <div className={styles.head}>
            <h3 className="tracked">{t("trend_title")}</h3>
            {trend !== null && (
              <span className={`${styles.trend} mono tabular`}>
                {trend >= 0 ? "▲" : "▼"} {Math.abs(trend)}
              </span>
            )}
          </div>
          <TrendChart rows={rows} />
          <MetricTrends rows={rows} />
        </>
      )}

      <div className={styles.head}>
        <h3 className="tracked">{t("history_title")}</h3>
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

      <div className={styles.accountZone}>
        {confirmingDelete ? (
          <div className={styles.confirmBox}>
            <p>{t("account_delete_confirm")}</p>
            <div className={styles.confirmBtns}>
              <button className={styles.confirmYes} onClick={removeAccount}>
                {t("account_delete_yes")}
              </button>
              <button className={styles.confirmNo} onClick={() => setConfirmingDelete(false)}>
                {t("account_delete_cancel")}
              </button>
            </div>
          </div>
        ) : (
          <button className={styles.accountDelete} onClick={() => setConfirmingDelete(true)}>
            {t("account_delete")}
          </button>
        )}
      </div>
    </div>
  );
}
