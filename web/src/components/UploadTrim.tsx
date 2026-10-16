import { useEffect, useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { autoWindow } from "../lib/api";
import { useI18n } from "../lib/i18n";
import { ShieldIcon } from "./icons";
import { RecordingGuide } from "./RecordingGuide";
import { TrimTimeline } from "./TrimTimeline";
import styles from "./UploadTrim.module.css";

interface Props {
  onAnalyze: (file: File, startSec: number, endSec: number) => void;
  onPrivacyClick: () => void;
}
type WindowRange = { start_sec: number; end_sec: number };

export function UploadTrim({ onAnalyze, onPrivacyClick }: Props) {
  const { t } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(0);
  const [current, setCurrent] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [detectFailed, setDetectFailed] = useState(false);
  const [videoFailed, setVideoFailed] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const requestRef = useRef(0);
  const durationRef = useRef(0);
  const detectedRef = useRef<WindowRange | null>(null);

  useEffect(() => () => { requestRef.current += 1; }, []);
  useEffect(() => () => { if (videoUrl) URL.revokeObjectURL(videoUrl); }, [videoUrl]);

  function applyRange(win: WindowRange | null, length: number) {
    const to = win ? Math.min(length, Math.max(0, win.end_sec)) : length;
    const from = win ? Math.max(0, Math.min(win.start_sec, to - 0.5)) : 0;
    setStart(from);
    setEnd(to);
  }

  async function handleFile(f: File) {
    const request = ++requestRef.current;
    videoRef.current?.pause();
    setFile(f);
    setVideoUrl(URL.createObjectURL(f));
    setDuration(0);
    durationRef.current = 0;
    detectedRef.current = null;
    setStart(0);
    setEnd(0);
    setCurrent(0);
    setPlaying(false);
    setVideoFailed(false);
    setDetecting(true);
    setDetectFailed(false);
    try {
      const win = await autoWindow(f);
      if (request !== requestRef.current) return;
      if (!Number.isFinite(win.start_sec) || !Number.isFinite(win.end_sec) || win.end_sec <= win.start_sec) {
        throw new Error("Invalid detection range");
      }
      detectedRef.current = win;
      if (durationRef.current > 0) applyRange(win, durationRef.current);
    } catch {
      if (request !== requestRef.current) return;
      detectedRef.current = null;
      applyRange(null, durationRef.current);
      setDetectFailed(true);
    } finally {
      if (request === requestRef.current) setDetecting(false);
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) void handleFile(f);
  }
  function onSelect(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) void handleFile(f);
    e.target.value = "";
  }
  function seekTo(sec: number) {
    if (videoRef.current) {
      videoRef.current.currentTime = sec;
      setCurrent(sec);
    }
  }
  const privacy = (
    <p className={styles.privacy}>
      <ShieldIcon />{t("privacy_notice")}{" "}
      <button className={styles.privacyLink} onClick={onPrivacyClick}>{t("privacy_link")}</button>
    </p>
  );
  const disabled = detecting || videoFailed || duration === 0 || end - start < 1 - 1e-6;
  return (
    <main className={styles.wrap}>
      <input ref={inputRef} type="file" hidden accept="video/mp4,video/quicktime,video/x-msvideo" onChange={onSelect} />
      <h1>{t("trim_title")}</h1>
      {!file || !videoUrl ? (
        <>
          <RecordingGuide />
          <div className={`${styles.dropzone} ${dragOver ? styles.dragOver : ""}`}
            role="button" tabIndex={0} aria-label={t("upload_dropzone")}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inputRef.current?.click(); }
            }}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)} onDrop={onDrop}>
            <img className={styles.emptyImage} src="/images/first-swing.webp" width="480" height="480" loading="lazy" alt="" />
            <p>{t("upload_dropzone")}</p>
          </div>
          {privacy}
        </>
      ) : (
        <>
          <div className={styles.fileRow}>
            <p>{file.name}</p>
            <button className={styles.changeFile} onClick={() => inputRef.current?.click()}>{t("trim_change_file")}</button>
          </div>
          <div className={styles.trimGrid}>
            <div className={styles.videoPanel}>
              <video key={videoUrl} ref={videoRef} src={videoUrl} playsInline preload="auto"
                aria-label={file.name}
                onLoadedMetadata={(e) => {
                  const d = e.currentTarget.duration;
                  if (!Number.isFinite(d) || d <= 0) { setVideoFailed(true); return; }
                  durationRef.current = d;
                  setDuration(d);
                  applyRange(detectedRef.current, d);
                }}
                onTimeUpdate={(e) => setCurrent(e.currentTarget.currentTime)}
                onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
                onEnded={() => setPlaying(false)} onError={() => setVideoFailed(true)} />
            </div>
            <div className={styles.controls}>
              <section className={styles.summary}>
                <p className={styles.status} role="status">
                  <span aria-hidden="true">{detecting ? "◌" : detectFailed ? "⚠" : "✓"} </span>
                  {t(detecting ? "upload_detecting" : detectFailed ? "trim_detect_failed" : "trim_detect_done")}
                </p>
                <div className={styles.duration}>
                  <span>{t("trim_duration")}</span>
                  <strong className="tabular">{(end - start).toFixed(1)}<small>s</small></strong>
                </div>
              </section>
              {!detecting && !detectFailed && start === 0 && end === duration && (
                <p className={styles.hint}>{t("trim_whole_selected")}</p>
              )}
              <button className={styles.cta} disabled={disabled} aria-describedby="trim-reason"
                onClick={() => onAnalyze(file, start, end)}>{t("trim_cta")}</button>
              <p id="trim-reason" className={styles.reason} role="status">
                {disabled && t(videoFailed ? "trim_video_failed" : detecting ? "trim_detect_wait" : duration === 0 ? "trim_video_loading" : "trim_minimum")}
              </p>
              {privacy}
            </div>
          </div>
          {duration > 0 && !videoFailed && (
            <TrimTimeline key={videoUrl} url={videoUrl} duration={duration} start={start} end={end}
              current={current} playing={playing} onSeek={seekTo}
              onStart={(v) => { setStart(v); seekTo(v); }} onEnd={(v) => { setEnd(v); seekTo(v); }}
              onTogglePlay={() => {
                const video = videoRef.current;
                if (!video) return;
                if (video.paused) void video.play().catch(() => setVideoFailed(true));
                else video.pause();
              }} />
          )}
        </>
      )}
    </main>
  );
}
