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
  onUpload,
  onRetry,
}: {
  onBack: () => void;
  onUpload: () => void;
  onRetry: () => void;
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
  const [setupStage, setSetupStage] = useState<"model" | "camera">("model");
  const [failureKind, setFailureKind] = useState<"denied" | "camera" | "model" | null>(null);
  const [poseVisible, setPoseVisible] = useState(false);
  const [recording, setRecording] = useState(false);
  const [stopping, setStopping] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [liveResult, setLiveResult] = useState<LiveScoreResponse | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function setup() {
      let cameraRequested = false;
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

        cameraRequested = true;
        setSetupStage("camera");
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
        if (cancelled) return;
        const name = e instanceof Error ? e.name : "";
        setFailureKind(cameraRequested ? (["NotAllowedError", "SecurityError"].includes(name) ? "denied" : "camera") : "model");
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
    setErrorMsg(null);
    setPoseVisible(false);
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
    setRecording(recorderRef.current?.state === "recording");
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
            const visible = KEY_JOINTS.every((idx) => visibilityOk(norm, idx));
            setPoseVisible(visible);
            if (visible) {
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
          } else {
            setPoseVisible(false);
          }
        }
      }
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
  }

  async function stopCapture() {
    setStopping(true);
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
    setRecording(false);
    if (wristYRef.current.length < MIN_FRAMES) {
      setErrorMsg(t("live_too_short"));
      setPhase("ready");
      setStopping(false);
      return;
    }
    setPhase("processing");
    try {
      const res = await scoreLive(wristYRef.current, framesRef.current);
      setLiveResult(res);
      setPhase("done");
    } catch {
      setErrorMsg(t("live_score_failed"));
      setPhase("error");
    }
    streamRef.current?.getTracks().forEach((tr) => tr.stop());
    setStopping(false);
  }

  return (
    <main className={styles.wrap}>
      <h1>{t("live_title")}</h1>
      <p className={styles.hint}>{t("live_intro")}</p>
      <div className={`${styles.captureGrid} ${phase === "done" ? styles.completed : ""}`}>
        <section className={styles.statePanel} aria-live="polite">
          <h2>{phase === "loading" ? t(setupStage === "model" ? "live_model_loading" : "live_camera_wait") :
            phase === "ready" ? `✓ ${t("live_ready")}` : phase === "capturing" ? `● ${t("live_capturing")}` :
            phase === "processing" ? `◷ ${t("live_processing")}` : phase === "done" ? `✓ ${t("live_done")}` : `⚠ ${t("error_generic")}`}</h2>
          {phase === "capturing" && <><p>{recording ? `● ${t("live_recording")}` : `⚠ ${t("live_recording_unavailable")}`}</p><p>{t("live_finish_hint")}</p></>}
          {phase === "ready" && !RECORD_MIME && <p>⚠ {t("live_recording_unavailable")}</p>}
          {phase === "error" && <p role="alert">{t(failureKind === "denied" ? "live_camera_denied" : failureKind === "camera" ? "live_camera_unavailable" : failureKind === "model" ? "live_model_failed" : "live_score_failed")}</p>}
        </section>

        {phase !== "done" && <>
          <div className={styles.panel}>
            <video ref={videoRef} className={styles.video} muted playsInline aria-label={t("live_preview")} />
            <canvas ref={canvasRef} className={styles.canvas} aria-hidden="true" />
            {phase === "loading" && <div className={styles.overlayMsg}>{t(setupStage === "model" ? "live_model_loading" : "live_camera_wait")}</div>}
          </div>
          <div className={styles.recognition} role="status">
            {phase === "capturing" ? (poseVisible ? `✓ ${t("live_pose_visible")}` : `⚠ ${t("live_pose_missing")}`) : t("live_pose_wait")}
          </div>
          <div className={styles.readout}>
            <h2>{t("live_angles")}</h2>
            <div className={styles.angleGrid}>
              {[[t("live_angle_spine"), angles?.spine], [t("live_angle_shoulder"), angles?.shoulderRotation], [t("live_angle_hip"), angles?.hipRotation]].map(([label, value]) => (
                <div key={label}><span>{label}</span><strong className="tabular">{phase === "capturing" && poseVisible && typeof value === "number" ? `${value.toFixed(1)}°` : "—"}</strong></div>
              ))}
            </div>
          </div>
          <fieldset className={styles.prepare}>
            <legend>{t("live_prepare")}</legend>
            <p>{t("live_prepare_manual")}</p>
            {["live_check_body", "live_check_space", "live_check_swing"].map((key) => (
              <label key={key}><input type="checkbox" />{t(key as "live_check_body" | "live_check_space" | "live_check_swing")}</label>
            ))}
          </fieldset>
        </>}

        <div className={styles.controls}>
          {phase === "ready" && <button className={styles.cta} onClick={startCapture}>{t("live_start")}</button>}
          {phase === "capturing" && <button className={styles.cta} onClick={stopCapture} disabled={stopping}>■ {t(stopping ? "live_stopping" : "live_stop")}</button>}
          {(phase === "error" || phase === "done") && <button className={styles.cta} onClick={onRetry}>{t(phase === "done" ? "live_recapture" : "retry")}</button>}
          <button className={styles.ghost} onClick={onUpload}>{t("live_upload_alternative")}</button>
          <button className={styles.ghost} onClick={onBack}>← {t("home")}</button>
        </div>
        <div className={styles.transfer}>
          {errorMsg && phase !== "error" && <p className={styles.error} role="alert">⚠ {errorMsg}</p>}
          <p>{t("live_transfer_stats")}</p><p>{t("live_transfer_video")}</p><p>{t("live_leave_hint")}</p>
        </div>
      </div>

      {phase === "done" && liveResult && (
        <div className={styles.result}>
          <div className={styles.scoreRow}>
            <div className={styles.scoreBox}>
              <div className={`${styles.label} tracked`}>{t("result_score_label")}</div>
              <div className={`${styles.scoreNum} tabular`}>{liveResult.score}</div>
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
                <span className={styles.issueTag}>{statusIcon(issue.level === "good" ? "ok" : issue.level === "warning" ? "warn" : "crit")} {t(`issue_${issue.level}`)}</span>
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
          {!recordedBlob && <p className={styles.hint}>⚠ {t("live_no_recording")}</p>}

          <h3 className="tracked">{t("result_chart_title")}</h3>
          <Waveform wristY={wristYRef.current} phaseBoundaries={liveResult.phase_boundaries} />

          <CoachingPanel
            summary={liveResult.summary}
            issues={liveResult.issues}
            onLoginClick={onLoginClick}
          />
        </div>
      )}
    </main>
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
  ctx.strokeStyle = getComputedStyle(ctx.canvas).getPropertyValue("--copper").trim();
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
  ctx.fillStyle = getComputedStyle(ctx.canvas).getPropertyValue("--feature-text").trim();
  for (const idx of [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]) {
    const p = landmarks[idx];
    if (!p) continue;
    ctx.beginPath();
    ctx.arc(p.x * w, p.y * h, pointRadius, 0, Math.PI * 2);
    ctx.fill();
  }
}
