import { useRef, useState } from "react";
import { TopBar } from "./components/TopBar";
import { Hero } from "./components/Hero";
import { UploadTrim } from "./components/UploadTrim";
import { ResultScreen } from "./components/ResultScreen";
import { LiveCapture } from "./components/LiveCapture";
import { AuthModal } from "./components/AuthModal";
import { HistoryPanel } from "./components/HistoryPanel";
import { AnalyzeProgress } from "./components/AnalyzeProgress";
import { PrivacyPolicy } from "./components/PrivacyPolicy";
import { analyzeAsync, getJob } from "./lib/api";
import { useI18n } from "./lib/i18n";
import type { AnalyzeResponse, JobStage } from "./lib/types";
import styles from "./App.module.css";

type Stage = "landing" | "trim" | "analyzing" | "result" | "live" | "history" | "privacy";

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
  const pollRef = useRef<number | null>(null);

  function stopPolling() {
    if (pollRef.current !== null) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }

  function goLanding() {
    stopPolling();
    setStage("landing");
    setResult(null);
    setError(null);
    setOpenedSwingId(undefined);
    setOpenedFeedback(undefined);
  }

  async function handleAnalyze(file: File, startSec: number, endSec: number) {
    setStage("analyzing");
    setError(null);
    setJobStage("uploaded");
    setJobProgress(5);
    setVideoName(file.name);
    try {
      const { job_id } = await analyzeAsync(file, startSec, endSec);
      pollRef.current = window.setInterval(async () => {
        try {
          const job = await getJob(job_id);
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
            setError(job.error ?? t("error_generic"));
            setStage("trim");
          }
        } catch (e) {
          stopPolling();
          setError(e instanceof Error ? e.message : t("error_generic"));
          setStage("trim");
        }
      }, POLL_MS);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
      setStage("trim");
    }
  }

  async function handleViewSample() {
    try {
      const res = await fetch("/samples/il-ban.json");
      const data: AnalyzeResponse = await res.json();
      setResult(data);
      setIsSample(true);
      setOpenedSwingId(undefined);
      setOpenedFeedback(undefined);
      setStage("result");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  function handleOpenSaved(payload: AnalyzeResponse, swingId: number, feedback: string) {
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
        onLiveClick={() => setStage("live")}
        onHistoryClick={() => setStage("history")}
        onLoginClick={() => setShowAuth(true)}
      />

      {error && (
        <div className={styles.errorBanner}>
          <div>{error}</div>
        </div>
      )}

      {stage === "landing" && (
        <>
          <Hero onUpload={() => setStage("trim")} onViewSample={handleViewSample} />
          <HistoryPanel onOpen={handleOpenSaved} onLoginClick={() => setShowAuth(true)} />
        </>
      )}

      {stage === "trim" && <UploadTrim onAnalyze={handleAnalyze} onPrivacyClick={() => setStage("privacy")} />}

      {stage === "analyzing" && <AnalyzeProgress stage={jobStage} progress={jobProgress} />}

      {stage === "result" && result && (
        <ResultScreen
          result={result}
          isSample={isSample}
          onBack={goLanding}
          videoName={videoName}
          swingId={openedSwingId}
          initialFeedback={openedFeedback}
          onLoginClick={() => setShowAuth(true)}
        />
      )}

      {stage === "live" && <LiveCapture onBack={goLanding} onLoginClick={() => setShowAuth(true)} />}

      {stage === "history" && (
        <HistoryPanel onOpen={handleOpenSaved} onLoginClick={() => setShowAuth(true)} />
      )}

      {stage === "privacy" && <PrivacyPolicy onBack={() => setStage("trim")} />}

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  );
}

export default App;
