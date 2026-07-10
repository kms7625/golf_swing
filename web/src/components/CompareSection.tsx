import { useEffect, useState } from "react";
import { getSwing, listSwings } from "../lib/api";
import { useAuth } from "../lib/auth";
import { useI18n } from "../lib/i18n";
import { PHASE_ORDER_KO, type AnalyzeResponse, type SwingRow } from "../lib/types";
import styles from "./CompareSection.module.css";

interface Props {
  result: AnalyzeResponse;
  /** 현재 화면이 저장된 스윙이라면 그 id — 비교 목록에서 자기 자신 제외 */
  currentSwingId?: number;
}

type TargetKey = "" | "pro" | `swing-${number}`;

/** 프로 샘플 + (로그인 시) 내 저장 스윙과 페이즈별 나란히 비교.
 * 비교 데이터는 전부 기존 산출물(rep_frames·summary) 재사용 — 분석 코어 무관. */
export function CompareSection({ result, currentSwingId }: Props) {
  const { t } = useI18n();
  const { isLoggedIn } = useAuth();
  const [saved, setSaved] = useState<SwingRow[]>([]);
  const [targetKey, setTargetKey] = useState<TargetKey>("");
  const [target, setTarget] = useState<AnalyzeResponse | null>(null);
  const [targetLabel, setTargetLabel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoggedIn) return;
    listSwings()
      .then((res) => setSaved(res.swings.filter((s) => s.id !== currentSwingId)))
      .catch(() => setSaved([]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isLoggedIn, currentSwingId]);

  async function select(key: TargetKey) {
    setTargetKey(key);
    setTarget(null);
    setError(null);
    if (key === "") return;
    setLoading(true);
    try {
      if (key === "pro") {
        const res = await fetch("/samples/pro.json");
        setTarget((await res.json()) as AnalyzeResponse);
        setTargetLabel(t("compare_pro"));
      } else {
        const id = Number(key.replace("swing-", ""));
        const detail = await getSwing(id);
        setTarget(detail.payload);
        setTargetLabel(detail.video_name || `#${id}`);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    } finally {
      setLoading(false);
    }
  }

  const metrics: { label: string; mine: number; theirs: number | undefined }[] = target
    ? [
        { label: t("compare_score"), mine: result.score, theirs: target.score },
        { label: t("result_metric_spine"), mine: result.summary.spine_angle_delta, theirs: target.summary?.spine_angle_delta },
        { label: t("result_metric_xfactor"), mine: result.summary.x_factor, theirs: target.summary?.x_factor },
        { label: t("result_metric_shoulder"), mine: result.summary.shoulder_rotation_max, theirs: target.summary?.shoulder_rotation_max },
      ]
    : [];

  return (
    <div className={styles.wrap}>
      <div className={styles.head}>
        <h3 className="tracked">{t("compare_title")}</h3>
        <select value={targetKey} onChange={(e) => select(e.target.value as TargetKey)}>
          <option value="">{t("compare_none")}</option>
          <option value="pro">{t("compare_pro")}</option>
          {saved.map((s) => (
            <option key={s.id} value={`swing-${s.id}`}>
              {new Date(s.created_at.endsWith("Z") || s.created_at.includes("+") ? s.created_at : s.created_at + "Z").toLocaleDateString()}{" "}
              · {s.score} · {s.video_name}
            </option>
          ))}
        </select>
      </div>
      {!isLoggedIn && <p className={styles.hint}>{t("compare_login_hint")}</p>}
      {loading && <p className={styles.hint}>{t("compare_loading")}</p>}
      {error && <p className={styles.error}>{error}</p>}

      {target && (
        <>
          <div className={styles.metricTable} role="table">
            <div className={`${styles.metricHead} ${styles.metricRow}`} role="row">
              <span>{t("compare_metric")}</span>
              <span>{t("compare_mine")}</span>
              <span className={styles.targetCol}>{targetLabel}</span>
              <span>{t("compare_diff")}</span>
            </div>
            {metrics.map((m) => {
              const diff = m.theirs !== undefined ? Math.round((m.mine - m.theirs) * 10) / 10 : null;
              return (
                <div key={m.label} className={styles.metricRow} role="row">
                  <span>{m.label}</span>
                  <span className="mono tabular">{m.mine}</span>
                  <span className={`mono tabular ${styles.targetCol}`}>{m.theirs ?? "-"}</span>
                  <span className="mono tabular">
                    {diff === null ? "-" : `${diff > 0 ? "+" : ""}${diff}`}
                  </span>
                </div>
              );
            })}
          </div>

          <div className={styles.pairGrid}>
            {PHASE_ORDER_KO.filter((ph) => result.rep_frames[ph] && target.rep_frames?.[ph]).map((ph) => (
              <PhasePair key={ph} phase={ph} mine={result.rep_frames[ph]} theirs={target.rep_frames[ph]} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function PhasePair({ phase, mine, theirs }: { phase: string; mine: string; theirs: string }) {
  const { t, phaseLabel } = useI18n();
  return (
    <div className={styles.pairCell}>
      <div className={styles.pairThumb}>
        <img src={`data:image/jpeg;base64,${mine}`} alt={`${t("compare_mine")} — ${phaseLabel(phase)}`} />
        <span className={styles.thumbTag}>{t("compare_mine")}</span>
      </div>
      <div className={styles.pairThumb}>
        <img src={`data:image/jpeg;base64,${theirs}`} alt={`${t("compare_target")} — ${phaseLabel(phase)}`} />
        <span className={`${styles.thumbTag} ${styles.thumbTagTarget}`}>{t("compare_target")}</span>
      </div>
      <div className={`${styles.pairCap} mono`}>{phaseLabel(phase).toUpperCase()}</div>
    </div>
  );
}
