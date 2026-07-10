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
import { scoreLive, type LiveScoreResponse } from "../lib/api";
import { useI18n } from "../lib/i18n";
import { getStatus, statusIcon } from "../lib/status";
import { translateIssueMessage } from "../lib/issueMessages";
import { Waveform } from "./Waveform";
import { CoachingPanel } from "./CoachingPanel";
import { grade } from "./ResultScreen";
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

const RECORD_MIME = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"].find(
  (m) => typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported(m)
);

export function LiveCapture({
  onBack,
  onLoginClick,
  onAnalyzeVideo,
}: {
  onBack: () => void;
  onLoginClick: () => void;
  /** 녹화본을 업로드 분석 파이프라인(정식 결과·저장·비교)으로 넘긴다 */
  onAnalyzeVideo: (file: File) => void;
}) {
  const { t, lang } = useI18n();
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const landmarkerRef = useRef<PoseLandmarker | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const wristYRef = useRef<number[]>([]);
  // wristYRef와 1:1 — 같은 가시성 게이트를 통과한 프레임의 각도만 쌓인다 (/score-live 요구 형식)
  const framesRef = useRef<Record<string, number>[]>([]);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);

  const [phase, setPhase] = useState<Phase>("loading");
  const [angles, setAngles] = useState<LiveAngles | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [liveResult, setLiveResult] = useState<LiveScoreResponse | null>(null);

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
    framesRef.current = [];
    setRecordedBlob(null);
    // 화면과 동일한 스트림을 녹화 — 종료 후 "정식 분석"으로 업로드 파이프라인 재사용
    if (RECORD_MIME && streamRef.current) {
      try {
        chunksRef.current = [];
        const rec = new MediaRecorder(streamRef.current, { mimeType: RECORD_MIME });
        rec.ondataavailable = (e) => {
          if (e.data.size > 0) chunksRef.current.push(e.data);
        };
        rec.start(1000);
        recorderRef.current = rec;
      } catch {
        recorderRef.current = null; // 녹화 불가 환경 — 라이브 점수만 제공
      }
    }
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
              const frame = {
                spine_angle: calcSpineAngle(norm),
                shoulder_rotation: calcShoulderRotation(norm),
                hip_rotation: calcHipRotation(norm),
                left_knee: calcKneeAngle(norm, "left"),
                right_knee: calcKneeAngle(norm, "right"),
                left_elbow: calcElbowAngle(norm, "left"),
                right_elbow: calcElbowAngle(norm, "right"),
              };
              setAngles({
                spine: frame.spine_angle,
                shoulderRotation: frame.shoulder_rotation,
                hipRotation: frame.hip_rotation,
                leftKnee: frame.left_knee,
                rightKnee: frame.right_knee,
                leftElbow: frame.left_elbow,
                rightElbow: frame.right_elbow,
              });
              const lwY = raw[15].y * h;
              const rwY = raw[16].y * h;
              wristYRef.current.push((lwY + rwY) / 2);
              framesRef.current.push(frame);
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
    // 트랙 정지 전에 레코더부터 마감해야 마지막 청크가 유실되지 않는다
    const rec = recorderRef.current;
    recorderRef.current = null;
    if (rec && rec.state !== "inactive") {
      await new Promise<void>((resolve) => {
        rec.onstop = () => resolve();
        rec.stop();
      });
      if (chunksRef.current.length > 0) {
        setRecordedBlob(new Blob(chunksRef.current, { type: RECORD_MIME }));
      }
    }
    if (wristYRef.current.length < MIN_FRAMES) {
      setErrorMsg(t("live_too_short"));
      setPhase("ready");
      return;
    }
    setPhase("processing");
    try {
      const res = await scoreLive(wristYRef.current, framesRef.current);
      setLiveResult(res);
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

      {phase === "done" && liveResult && (
        <div className={styles.result}>
          <div className={styles.scoreRow}>
            <div className={styles.scoreBox}>
              <div className="label tracked">{t("result_score_label")}</div>
              <div className={`${styles.scoreNum} mono tabular`}>{liveResult.score}</div>
              <div className={styles.scoreGrade}>
                {t("grade")} {grade(liveResult.score)}
              </div>
            </div>
            <div className={styles.liveStats}>
              <LiveStat
                label={t("result_metric_spine")}
                value={`${liveResult.summary.spine_angle_delta}°`}
                status={getStatus(liveResult.summary.spine_angle_delta, 0, 5, 5, 10)}
              />
              <LiveStat
                label={t("result_metric_xfactor")}
                value={`${liveResult.summary.x_factor}°`}
                status={getStatus(liveResult.summary.x_factor, 35, 55, 20, 60)}
              />
              <LiveStat
                label={t("result_metric_shoulder")}
                value={`${liveResult.summary.shoulder_rotation_max}°`}
              />
              <LiveStat
                label={t("result_metric_phases")}
                value={`${liveResult.summary.phases_detected.length} / 7`}
              />
            </div>
          </div>

          <div className={styles.issueList}>
            {liveResult.issues.map((issue, i) => (
              <div key={i} className={`${styles.issueRow} ${styles[issue.level]}`}>
                <span className={`${styles.issueTag} tracked`}>{issue.level}</span>
                <span>{translateIssueMessage(lang, issue.message)}</span>
              </div>
            ))}
          </div>

          {recordedBlob && (
            <button
              className={styles.fullAnalysisBtn}
              onClick={() =>
                onAnalyzeVideo(
                  new File([recordedBlob], `live-${Date.now()}.webm`, { type: recordedBlob.type })
                )
              }
            >
              {t("live_full_analysis")}
            </button>
          )}

          <h3 className="tracked">{t("result_chart_title")}</h3>
          <Waveform wristY={wristYRef.current} phaseBoundaries={liveResult.phase_boundaries} />

          <CoachingPanel
            summary={liveResult.summary}
            issues={liveResult.issues}
            onLoginClick={onLoginClick}
          />
        </div>
      )}
    </div>
  );
}

function LiveStat({ label, value, status }: { label: string; value: string; status?: "ok" | "warn" | "crit" }) {
  return (
    <div className={styles.liveStat}>
      <div className={`${styles.liveStatK} tracked`}>{label}</div>
      <div className={`${styles.liveStatV} ${status ? styles[status] : ""} mono tabular`}>
        {value}
        {status ? ` ${statusIcon(status)}` : ""}
      </div>
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
