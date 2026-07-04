import { useRef, useState, type ChangeEvent, type DragEvent } from "react";
import { autoWindow } from "../lib/api";
import { useI18n } from "../lib/i18n";
import styles from "./UploadTrim.module.css";

interface Props {
  onAnalyze: (file: File, startSec: number, endSec: number) => void;
}

export function UploadTrim({ onAnalyze }: Props) {
  const { t } = useI18n();
  const [file, setFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [start, setStart] = useState(0);
  const [end, setEnd] = useState(0);
  const [detecting, setDetecting] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  async function handleFile(f: File) {
    setFile(f);
    setVideoUrl(URL.createObjectURL(f));
    setDetecting(true);
    try {
      const win = await autoWindow(f);
      setStart(win.start_sec);
      setEnd(win.end_sec);
    } catch {
      // 자동 감지 실패 시 전체 구간을 기본값으로 — 사용자가 수동 조정
    } finally {
      setDetecting(false);
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f) handleFile(f);
  }

  function onSelect(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  }

  function seekTo(sec: number) {
    if (videoRef.current) videoRef.current.currentTime = sec;
  }

  if (!file || !videoUrl) {
    return (
      <div className={styles.wrap}>
        <div
          className={`${styles.dropzone} ${dragOver ? styles.dragOver : ""}`}
          onClick={() => document.getElementById("file-input")?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
        >
          {t("upload_dropzone")}
          <input id="file-input" type="file" accept="video/mp4,video/quicktime,video/x-msvideo" onChange={onSelect} />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.trimGrid}>
        <div className={styles.videoPanel}>
          <video
            ref={videoRef}
            src={videoUrl}
            controls
            onLoadedMetadata={(e) => {
              const d = e.currentTarget.duration;
              setDuration(d);
              if (end === 0) setEnd(d);
            }}
          />
        </div>
        <div className={styles.controls}>
          <h3 className="tracked">{t("trim_title")}</h3>
          <p className={styles.hint}>{detecting ? t("upload_detecting") : t("trim_hint")}</p>

          <div className={styles.sliderRow}>
            <div className="label">
              <span>{t("trim_start")}</span>
              <span className={`val mono tabular`}>{start.toFixed(1)}s</span>
            </div>
            <input
              type="range"
              min={0}
              max={duration || 1}
              step={0.1}
              value={start}
              onChange={(e) => {
                const v = Math.min(Number(e.target.value), end - 0.5);
                setStart(v);
                seekTo(v);
              }}
            />
          </div>

          <div className={styles.sliderRow}>
            <div className="label">
              <span>{t("trim_end")}</span>
              <span className="val mono tabular">{end.toFixed(1)}s</span>
            </div>
            <input
              type="range"
              min={0}
              max={duration || 1}
              step={0.1}
              value={end}
              onChange={(e) => {
                const v = Math.max(Number(e.target.value), start + 0.5);
                setEnd(v);
                seekTo(v);
              }}
            />
          </div>

          <div className={styles.duration}>
            <span>{t("trim_duration")}</span>
            <span className="val mono tabular">{(end - start).toFixed(1)}s</span>
          </div>

          <button
            className={styles.cta}
            disabled={detecting || end - start < 1}
            onClick={() => onAnalyze(file, start, end)}
          >
            {t("trim_cta")}
          </button>
        </div>
      </div>
    </div>
  );
}
