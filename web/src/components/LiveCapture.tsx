import { useEffect, useRef, useState } from "react";
import { FilesetResolver, PoseLandmarker } from "@mediapipe/tasks-vision";
import {
  KEY_JOINTS,
  calcElbowAngle,
  calcHipRotation,
  calcKneeAngle,
  calcShoulderRotation,
  calcSpineAngle,
  normalizeLandmarks,
  visibilityOk,
  type RawLandmark,
} from "../lib/geometry";
import { detectPhases } from "../lib/api";
import { useI18n } from "../lib/i18n";
import { Waveform } from "./Waveform";
import styles from "./LiveCapture.module.css";

type Phase = "loading" | "ready" | "capturing" | "processing" | "done" | "error";

interface LiveAngles {
  spine: number;
  shoulderRotation: number;
  hipRotation: number;
  leftKnee: number;
  rightKnee: number;
  leftElbow: number;
  rightElbow: number;
}

// Standard BlazePose topology subset used for the skeleton overlay — same
// landmark indices as analyzer/geometry.py (11/12 shoulders, 23/24 hips, ...).
const SKELETON_CONNECTIONS: [number, number][] = [
  [11, 12],
  [11, 13],
  [13, 15],
  [12, 14],
  [14, 16],
  [11, 23],
  [12, 24],
  [23, 24],
  [23, 25],
  [25, 27],
  [24, 26],
  [26, 28],
];

const MIN_FRAMES = 20;

export function LiveCapture({ onBack }: { onBack: () => void }) {
  const { t } = useI18n();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const landmarkerRef = useRef<PoseLandmarker | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const wristYRef = useRef<number[]>([]);

  const [phase, setPhase] = useState<Phase>("loading");
  const [angles, setAngles] = useState<LiveAngles | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [phaseBoundaries, setPhaseBoundaries] = useState<Record<string, [number, number]> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function setup() {
      try {
        const vision = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.35/wasm"
        );
        const landmarker = await PoseLandmarker.createFromOptions(vision, {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
            delegate: "GPU",
          },
          runningMode: "VIDEO",
          numPoses: 1,
        });
        if (cancelled) {
          landmarker.close();
          return;
        }
        landmarkerRef.current = landmarker;

        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (cancelled) {
          stream.getTracks().forEach((tr) => tr.stop());
          return;
        }
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        setPhase("ready");
      } catch (e) {
        setErrorMsg(e instanceof Error ? e.message : t("error_generic"));
        setPhase("error");
      }
    }

    setup();
    return () => {
      cancelled = true;
      stopEverything();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function stopEverything() {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    streamRef.current?.getTracks().forEach((tr) => tr.stop());
    streamRef.current = null;
    landmarkerRef.current?.close();
    landmarkerRef.current = null;
  }

  function startCapture() {
    wristYRef.current = [];
    setPhase("capturing");
    const loop = () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const landmarker = landmarkerRef.current;
      if (video && canvas && landmarker && video.readyState >= 2) {
        const w = video.videoWidth;
        const h = video.videoHeight;
        const result = landmarker.detectForVideo(video, performance.now());
        const ctx = canvas.getContext("2d");
        if (ctx) {
          canvas.width = w;
          canvas.height = h;
          ctx.clearRect(0, 0, w, h);
          const raw = result.landmarks[0] as RawLandmark[] | undefined;
          if (raw) {
            drawSkeleton(ctx, raw, w, h);
            const { norm } = normalizeLandmarks(raw, w, h);
            if (KEY_JOINTS.every((idx) => visibilityOk(norm, idx))) {
              setAngles({
                spine: calcSpineAngle(norm),
                shoulderRotation: calcShoulderRotation(norm),
                hipRotation: calcHipRotation(norm),
                leftKnee: calcKneeAngle(norm, "left"),
                rightKnee: calcKneeAngle(norm, "right"),
                leftElbow: calcElbowAngle(norm, "left"),
                rightElbow: calcElbowAngle(norm, "right"),
              });
              const lwY = raw[15].y * h;
              const rwY = raw[16].y * h;
              wristYRef.current.push((lwY + rwY) / 2);
            }
          }
        }
      }
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
  }

  async function stopCapture() {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    if (wristYRef.current.length < MIN_FRAMES) {
      setErrorMsg(t("live_too_short"));
      setPhase("ready");
      return;
    }
    setPhase("processing");
    try {
      const boundaries = await detectPhases(wristYRef.current);
      setPhaseBoundaries(boundaries);
      setPhase("done");
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : t("error_generic"));
      setPhase("error");
    }
    streamRef.current?.getTracks().forEach((tr) => tr.stop());
  }

  return (
    <div className={styles.wrap}>
      <h2 className="tracked">{t("live_title")}</h2>
      <p className={styles.hint}>{t("live_hint")}</p>

      {phase !== "done" && (
        <div className={styles.panel}>
          <div className={`${styles.bracket} ${styles.tl}`} />
          <div className={`${styles.bracket} ${styles.tr}`} />
          <div className={`${styles.bracket} ${styles.bl}`} />
          <div className={`${styles.bracket} ${styles.br}`} />
          <video ref={videoRef} className={styles.video} muted playsInline />
          <canvas ref={canvasRef} className={styles.canvas} />
          {angles && (
            <div className={`${styles.readout} mono`}>
              <span>SPINE {angles.spine.toFixed(1)}°</span>
              <span>SHOULDER {angles.shoulderRotation.toFixed(1)}°</span>
              <span>HIP {angles.hipRotation.toFixed(1)}°</span>
            </div>
          )}
          {phase === "loading" && <div className={styles.overlayMsg}>{t("live_loading")}</div>}
        </div>
      )}

      {errorMsg && <div className={styles.error}>{errorMsg}</div>}

      <div className={styles.controls}>
        {phase === "ready" && (
          <button className={styles.cta} onClick={startCapture}>
            {t("live_start")}
          </button>
        )}
        {phase === "capturing" && (
          <button className={styles.cta} onClick={stopCapture}>
            {t("live_stop")}
          </button>
        )}
        {phase === "processing" && <div className={styles.overlayMsg}>{t("live_processing")}</div>}
        <button className={styles.ghost} onClick={onBack}>
          {t("result_back")}
        </button>
      </div>

      {phase === "done" && phaseBoundaries && (
        <div className={styles.result}>
          <h3 className="tracked">{t("result_chart_title")}</h3>
          <Waveform wristY={wristYRef.current} phaseBoundaries={phaseBoundaries} />
        </div>
      )}
    </div>
  );
}

function drawSkeleton(ctx: CanvasRenderingContext2D, landmarks: RawLandmark[], w: number, h: number) {
  // Scaled to native camera resolution (canvas draws in video-pixel space, not
  // displayed CSS pixels) so lines stay visible regardless of webcam resolution.
  const lineWidth = Math.max(3, w * 0.006);
  const pointRadius = Math.max(4, w * 0.009);
  ctx.strokeStyle = "#dd8b57";
  ctx.lineWidth = lineWidth;
  ctx.lineCap = "round";
  for (const [a, b] of SKELETON_CONNECTIONS) {
    const pa = landmarks[a];
    const pb = landmarks[b];
    if (!pa || !pb) continue;
    ctx.beginPath();
    ctx.moveTo(pa.x * w, pa.y * h);
    ctx.lineTo(pb.x * w, pb.y * h);
    ctx.stroke();
  }
  ctx.fillStyle = "#5fb8b0";
  for (const idx of [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]) {
    const p = landmarks[idx];
    if (!p) continue;
    ctx.beginPath();
    ctx.arc(p.x * w, p.y * h, pointRadius, 0, Math.PI * 2);
    ctx.fill();
  }
}
