import { useEffect, useRef, useState } from "react";
import { useI18n } from "../lib/i18n";
import { PHASE_COLORS, PHASE_ORDER_KO } from "../lib/types";
import styles from "./SwingReplay.module.css";

export interface ReplaySource {
  /** 분석에 사용한 원본 파일의 objectURL (새 분석 흐름에서만 존재 — 원본은 서버 미보관) */
  url: string;
  startSec: number;
  endSec: number;
}

interface Props {
  source: ReplaySource;
  phaseBoundaries: Record<string, [number, number]>;
  fps: number;
  effSample: number;
}

const SPEEDS = [0.25, 0.5, 1];

/** 페이즈 경계(hist idx)를 분석 구간 내 시간으로 — frame_data의 time 관례(local_idx*eff_sample/fps)와 동일한 근사 */
function idxToSec(idx: number, fps: number, effSample: number): number {
  return (idx * effSample) / Math.max(fps, 1);
}

export function SwingReplay({ source, phaseBoundaries, fps, effSample }: Props) {
  const { t, phaseLabel } = useI18n();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [pos, setPos] = useState(0); // 분석 구간 내 상대 초

  const span = Math.max(source.endSec - source.startSec, 0.1);

  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    const onTime = () => {
      // 분석 구간 밖으로 나가면 구간 시작으로 루프 — 스윙 반복 리뷰 용도
      if (v.currentTime >= source.endSec) {
        v.currentTime = source.startSec;
      }
      setPos(Math.max(v.currentTime - source.startSec, 0));
    };
    const onMeta = () => {
      v.currentTime = source.startSec;
    };
    v.addEventListener("timeupdate", onTime);
    v.addEventListener("loadedmetadata", onMeta);
    return () => {
      v.removeEventListener("timeupdate", onTime);
      v.removeEventListener("loadedmetadata", onMeta);
    };
  }, [source]);

  function togglePlay() {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) {
      // playbackRate는 setRate()가 video 요소에 직접 유지 — 여기서 재할당하면
      // 속도 클릭 직후 같은 틱의 재생 클릭이 stale state로 되돌리는 레이스가 생긴다
      v.play();
      setPlaying(true);
    } else {
      v.pause();
      setPlaying(false);
    }
  }

  function seekRel(relSec: number) {
    const v = videoRef.current;
    if (!v) return;
    v.currentTime = source.startSec + Math.min(Math.max(relSec, 0), span);
    setPos(relSec);
  }

  function setRate(r: number) {
    setSpeed(r);
    if (videoRef.current) videoRef.current.playbackRate = r;
  }

  const phases = PHASE_ORDER_KO.filter((ph) => phaseBoundaries[ph]);

  return (
    <div className={styles.wrap}>
      <h3 className="tracked">{t("replay_title")}</h3>
      <p className={styles.hint}>{t("replay_hint")}</p>

      <div className={styles.videoBox}>
        <video ref={videoRef} src={source.url} playsInline muted onClick={togglePlay} />
      </div>

      <div className={styles.timeline}>
        {phases.map((ph) => {
          const [lo, hi] = phaseBoundaries[ph];
          const left = (idxToSec(lo, fps, effSample) / span) * 100;
          const width = ((idxToSec(hi, fps, effSample) - idxToSec(lo, fps, effSample)) / span) * 100;
          return (
            <div
              key={ph}
              className={styles.segment}
              style={{
                left: `${Math.min(left, 100)}%`,
                width: `${Math.max(Math.min(width, 100 - left), 0.5)}%`,
                background: PHASE_COLORS[ph],
              }}
              title={phaseLabel(ph)}
            />
          );
        })}
        <div className={styles.cursor} style={{ left: `${Math.min((pos / span) * 100, 100)}%` }} />
        <input
          type="range"
          className={styles.scrub}
          min={0}
          max={span}
          step={0.01}
          value={Math.min(pos, span)}
          onChange={(e) => seekRel(Number(e.target.value))}
          aria-label={t("replay_title")}
        />
      </div>

      <div className={styles.controls}>
        <button className={styles.playBtn} onClick={togglePlay}>
          {playing ? `⏸ ${t("replay_pause")}` : `▶ ${t("replay_play")}`}
        </button>
        <div className={styles.speeds}>
          <span className={`${styles.speedLabel} tracked`}>{t("replay_speed")}</span>
          {SPEEDS.map((r) => (
            <button
              key={r}
              className={`${styles.speedBtn} ${speed === r ? styles.speedActive : ""} mono`}
              onClick={() => setRate(r)}
            >
              {r}x
            </button>
          ))}
        </div>
      </div>

      <div className={styles.chips}>
        {phases.map((ph) => (
          <button
            key={ph}
            className={styles.chip}
            style={{ borderColor: PHASE_COLORS[ph] }}
            onClick={() => seekRel(idxToSec(phaseBoundaries[ph][0], fps, effSample))}
          >
            <span className={styles.chipDot} style={{ background: PHASE_COLORS[ph] }} />
            {phaseLabel(ph)}
          </button>
        ))}
      </div>
    </div>
  );
}
