import { useEffect, useRef, useState } from "react";
import { useI18n } from "../lib/i18n";
import styles from "./TrimTimeline.module.css";

interface Props {
  url: string;
  duration: number;
  start: number;
  end: number;
  current: number;
  playing: boolean;
  onStart: (value: number) => void;
  onEnd: (value: number) => void;
  onSeek: (value: number) => void;
  onTogglePlay: () => void;
}

function mediaEvent(video: HTMLVideoElement, event: string, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const cleanup = () => {
      clearTimeout(timer);
      video.removeEventListener(event, ready);
      video.removeEventListener("error", failed);
      signal.removeEventListener("abort", failed);
    };
    const ready = () => { cleanup(); resolve(); };
    const failed = () => { cleanup(); reject(new Error("Video preview unavailable")); };
    const timer = setTimeout(failed, 8000);
    video.addEventListener(event, ready, { once: true });
    video.addEventListener("error", failed, { once: true });
    signal.addEventListener("abort", failed, { once: true });
    if (signal.aborted) failed();
  });
}

export function TrimTimeline({ url, duration, start, end, current, playing, onStart, onEnd, onSeek, onTogglePlay }: Props) {
  const { t } = useI18n();
  const [frames, setFrames] = useState<string[]>([]);
  const [failed, setFailed] = useState(false);
  const stripRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const controller = new AbortController();
    const video = document.createElement("video");
    video.muted = true;
    video.playsInline = true;
    video.preload = "auto";
    async function capture() {
      try {
        const loaded = mediaEvent(video, "loadeddata", controller.signal);
        video.src = url;
        await loaded;
        const canvas = document.createElement("canvas");
        canvas.width = 160;
        canvas.height = 90;
        const context = canvas.getContext("2d");
        if (!context) throw new Error("Canvas unavailable");
        const images: string[] = [];
        for (let i = 0; i < 10; i++) {
          if (controller.signal.aborted) return;
          const seeked = mediaEvent(video, "seeked", controller.signal);
          video.currentTime = duration * (i + 0.5) / 10;
          await seeked;
          const scale = Math.min(canvas.width / video.videoWidth, canvas.height / video.videoHeight);
          const width = video.videoWidth * scale, height = video.videoHeight * scale;
          context.clearRect(0, 0, canvas.width, canvas.height);
          context.drawImage(video, (160 - width) / 2, (90 - height) / 2, width, height);
          images.push(canvas.toDataURL("image/webp", 0.7));
        }
        if (!controller.signal.aborted) setFrames(images);
      } catch {
        if (!controller.signal.aborted) setFailed(true);
      }
    }
    void capture();
    return () => { controller.abort(); video.removeAttribute("src"); video.load(); };
  }, [url, duration]);

  const valueText = (value: number) => `${value.toFixed(1)} ${t("trim_seconds")}`;
  const startLimit = Math.max(0, end - 0.5);
  const endLimit = Math.min(duration, start + 0.5);
  return (
    <section className={styles.wrap} aria-label={t("trim_timeline")}>
      <div className={styles.toolbar}>
        <button onClick={onTogglePlay} aria-label={playing ? t("replay_pause") : t("replay_play")}>
          <span aria-hidden="true">{playing ? "Ⅱ" : "▶"}</span>
        </button>
        <span className="mono tabular">{current.toFixed(1)} / {duration.toFixed(1)}s</span>
        <p>{t("trim_handles_hint")}</p>
      </div>
      <div className={styles.timeline}>
        <button ref={stripRef} className={styles.filmstrip} tabIndex={-1} aria-hidden="true"
          onClick={(e) => {
            const rect = stripRef.current!.getBoundingClientRect();
            onSeek(Math.max(0, Math.min(duration, (e.clientX - rect.left) / rect.width * duration)));
          }}>
          {frames.map((src, index) => <img key={index} src={src} alt="" />)}
        </button>
        <div className={styles.outside} style={{ left: 0, width: `${start / duration * 100}%` }} />
        <div className={styles.outside} style={{ left: `${end / duration * 100}%`, right: 0 }} />
        <div className={styles.selection} style={{ left: `${start / duration * 100}%`, width: `${(end - start) / duration * 100}%` }} />
        <div className={styles.playhead} style={{ left: `${current / duration * 100}%` }} aria-hidden="true" />
        <input className={`${styles.range} ${styles.seek}`} type="range" min={0} max={duration} step={0.01}
          value={current} aria-label={t("trim_playhead")} aria-valuetext={valueText(current)}
          onChange={(e) => onSeek(Number(e.target.value))} />
        <input className={`${styles.range} ${styles.handle}`} type="range" min={0} max={duration} step={0.1}
          value={start} aria-label={t("trim_range_start")} aria-valuemax={startLimit} aria-valuetext={valueText(start)}
          onChange={(e) => onStart(Math.min(Number(e.target.value), startLimit))}
          onKeyDown={(e) => {
            if (e.key === "End") { e.preventDefault(); onStart(startLimit); }
          }} />
        <input className={`${styles.range} ${styles.handle}`} type="range" min={0} max={duration} step={0.1}
          value={end} aria-label={t("trim_range_end")} aria-valuemin={endLimit} aria-valuetext={valueText(end)}
          onChange={(e) => onEnd(Math.max(Number(e.target.value), endLimit))}
          onKeyDown={(e) => {
            if (e.key === "Home") { e.preventDefault(); onEnd(endLimit); }
            if (e.key === "End") { e.preventDefault(); onEnd(duration); }
          }} />
      </div>
      {frames.length === 0 && <p className={styles.notice} role="status">{t(failed ? "trim_thumbnails_failed" : "trim_thumbnails_loading")}</p>}
      <div className={styles.labels}>
        <span>{t("trim_start")} <b>{start.toFixed(1)}s</b></span>
        <span>{t("trim_current")} <b>{current.toFixed(1)}s</b></span>
        <span>{t("trim_end")} <b>{end.toFixed(1)}s</b></span>
      </div>
      <p className={styles.length}>{t("trim_duration")} <b className="tabular">{(end - start).toFixed(1)}s</b></p>
    </section>
  );
}
