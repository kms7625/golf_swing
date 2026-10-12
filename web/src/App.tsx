import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { TopBar } from "./components/TopBar";
import { Hero } from "./components/Hero";
import { UploadTrim } from "./components/UploadTrim";
import { ResultScreen } from "./components/ResultScreen";
import { AuthModal } from "./components/AuthModal";
import { HistoryPanel } from "./components/HistoryPanel";
import { AnalyzeProgress } from "./components/AnalyzeProgress";
import { PrivacyPolicy } from "./components/PrivacyPolicy";
import { analyzeAsync, getJob } from "./lib/api";
import { useI18n } from "./lib/i18n";
import type { AnalyzeResponse, JobStage } from "./lib/types";
import type { ReplaySource } from "./components/SwingReplay";
import styles from "./App.module.css";

// mediapipe(tasks-vision) 청크가 무거워 라이브 화면만 지연 로딩 — 초기 번들 축소
const LiveCapture = lazy(() =>
  import("./components/LiveCapture").then((m) => ({ default: m.LiveCapture }))
);

type Stage = "landing" | "trim" | "analyzing" | "result" | "live" | "history" | "privacy" | "analysis-error";

const POLL_MS = 1500;

function App() {
  const { t } = useI18n();
  const [stage, setStage] = useState<Stage>("landing");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isSample, setIsSample] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAuth, setShowAuth] = useState(false);
  const [jobStage, setJobStage] = useState<JobStage>("uploaded");
  const [jobProgress, setJobProgress] = useState(5);
  const [videoName, setVideoName] = useState("");
  const [openedSwingId, setOpenedSwingId] = useState<number | undefined>(undefined);
  const [openedFeedback, setOpenedFeedback] = useState<string | undefined>(undefined);
  const [replay, setReplay] = useState<ReplaySource | undefined>(undefined);
  const pollRef = useRef<number | null>(null);
  const requestRef = useRef(0);
  const activeJobRef = useRef<string | null>(null);

  useEffect(() => () => {
    requestRef.current += 1;
    activeJobRef.current = null;
    if (pollRef.current !== null) window.clearTimeout(pollRef.current);
  }, []);

  function clearReplay() {
    setReplay((prev) => {
      if (prev) URL.revokeObjectURL(prev.url);
      return undefined;
    });
  }

  function stopPolling() {
    requestRef.current += 1;
    activeJobRef.current = null;
    if (pollRef.current !== null) {
      window.clearTimeout(pollRef.current);
      pollRef.current = null;
    }
  }

  function goLanding() {
    stopPolling();
    clearReplay();
    setStage("landing");
    setResult(null);
    setError(null);
    setOpenedSwingId(undefined);
    setOpenedFeedback(undefined);
  }

  function navigate(next: Stage) {
    stopPolling();
    clearReplay();
    setError(null);
    setStage(next);
  }

  async function handleAnalyze(file: File, startSec?: number, endSec?: number) {
    stopPolling();
    const request = requestRef.current;
    setStage("analyzing");
    setResult(null);
    setError(null);
    setJobStage("uploaded");
    setJobProgress(0);
    setVideoName(file.name);
    clearReplay();
    setReplay({ url: URL.createObjectURL(file), startSec: startSec ?? 0, endSec });
    try {
      const { job_id } = await analyzeAsync(file, startSec, endSec);
      if (request !== requestRef.current) return;
      activeJobRef.current = job_id;
      setJobProgress(5);
      const isCurrent = () => request === requestRef.current && activeJobRef.current === job_id;
      async function poll() {
        if (!isCurrent()) return;
        try {
          const job = await getJob(job_id);
          // A navigation or newer job invalidates both successful and failed responses.
          if (!isCurrent()) return;
          setJobStage(job.stage);
          setJobProgress(job.progress);
          if (job.status === "done" && job.result) {
            stopPolling();
            setResult(job.result);
            setIsSample(false);
            setOpenedSwingId(undefined);
            setOpenedFeedback(undefined);
            setStage("result");
          } else if (job.status === "error") {
            stopPolling();
            clearReplay();
            setError(job.error ?? t("error_generic"));
            setStage("analysis-error");
          } else {
            // Schedule only after completion: slow requests never overlap.
            pollRef.current = window.setTimeout(poll, POLL_MS);
          }
        } catch (e) {
          if (!isCurrent()) return;
          stopPolling();
          clearReplay();
          setError(e instanceof Error ? e.message : t("error_generic"));
          setStage("analysis-error");
        }
      }
      pollRef.current = window.setTimeout(poll, POLL_MS);
    } catch (e) {
      if (request !== requestRef.current) return;
      stopPolling();
      clearReplay();
      setError(e instanceof Error ? e.message : t("error_generic"));
      setStage("analysis-error");
    }
  }

  async function handleViewSample() {
    stopPolling();
    const request = requestRef.current;
    try {
      const res = await fetch("/samples/il-ban.json");
      const data: AnalyzeResponse = await res.json();
      if (request !== requestRef.current) return;
      clearReplay();
      setVideoName("일반.mp4");
      setResult(data);
      setIsSample(true);
      setOpenedSwingId(undefined);
      setOpenedFeedback(undefined);
      setStage("result");
    } catch (e) {
      if (request !== requestRef.current) return;
      setError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  function handleOpenSaved(payload: AnalyzeResponse, swingId: number, feedback: string, filename: string) {
    stopPolling();
    clearReplay();
    setVideoName(filename);
    setResult(payload);
    setIsSample(false);
    setOpenedSwingId(swingId);
    setOpenedFeedback(feedback || undefined);
    setStage("result");
  }

  return (
    <>
      <TopBar
        onBrandClick={goLanding}
        onLiveClick={() => navigate("live")}
        onHistoryClick={() => navigate("history")}
        onLoginClick={() => setShowAuth(true)}
      />

      {error && (
        <div className={styles.errorBanner}>
          <div role="alert">{error === "스윙 동작을 찾지 못했어요. 구간을 다시 선택해 주세요." ? t("swing_not_found") : error}</div>
          {stage === "analysis-error" && <button onClick={() => { setError(null); setStage("trim"); }}>{t("reselect_swing")}</button>}
        </div>
      )}

      {stage === "landing" && (
        <Hero onUpload={() => navigate("trim")} onViewSample={handleViewSample} onHistory={() => navigate("history")} />
      )}

      {["trim", "analyzing", "analysis-error"].includes(stage) && (
        <div hidden={stage !== "trim"}>
          <UploadTrim onAnalyze={handleAnalyze} onPrivacyClick={() => setStage("privacy")} />
        </div>
      )}

      {stage === "analyzing" && <AnalyzeProgress stage={jobStage} progress={jobProgress} filename={videoName} onBack={() => navigate("trim")} />}

      {stage === "result" && result && (
        <ResultScreen
          result={result}
          isSample={isSample}
          onBack={goLanding}
          videoName={videoName}
          swingId={openedSwingId}
          initialFeedback={openedFeedback}
          replay={replay}
          onLoginClick={() => setShowAuth(true)}
        />
      )}

      {stage === "live" && (
        <Suspense fallback={<div className={styles.analyzing}><div className={styles.spinner} /></div>}>
          <LiveCapture
            onBack={goLanding}
            onLoginClick={() => setShowAuth(true)}
            onAnalyzeVideo={(file) => handleAnalyze(file)}
          />
        </Suspense>
      )}

      {stage === "history" && (
        <HistoryPanel onOpen={handleOpenSaved} onLoginClick={() => setShowAuth(true)} />
      )}

      {stage === "privacy" && <PrivacyPolicy onBack={() => setStage("trim")} />}

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}

export default App;
