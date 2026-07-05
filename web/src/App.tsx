import { useState } from "react";
import { TopBar } from "./components/TopBar";
import { Hero } from "./components/Hero";
import { UploadTrim } from "./components/UploadTrim";
import { ResultScreen } from "./components/ResultScreen";
import { LiveCapture } from "./components/LiveCapture";
import { analyze } from "./lib/api";
import { useI18n } from "./lib/i18n";
import type { AnalyzeResponse } from "./lib/types";
import styles from "./App.module.css";

type Stage = "landing" | "trim" | "analyzing" | "result" | "live";

function App() {
  const { t } = useI18n();
  const [stage, setStage] = useState<Stage>("landing");
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [isSample, setIsSample] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function goLanding() {
    setStage("landing");
    setResult(null);
    setError(null);
  }

  async function handleAnalyze(file: File, startSec: number, endSec: number) {
    setStage("analyzing");
    setError(null);
    try {
      const res = await analyze(file, startSec, endSec);
      setResult(res);
      setIsSample(false);
      setStage("result");
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
      setStage("result");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("error_generic"));
    }
  }

  return (
    <>
      <TopBar onBrandClick={goLanding} onLiveClick={() => setStage("live")} />

      {error && (
        <div className={styles.errorBanner}>
          <div>{error}</div>
        </div>
      )}

      {stage === "landing" && <Hero onUpload={() => setStage("trim")} onViewSample={handleViewSample} />}

      {stage === "trim" && <UploadTrim onAnalyze={handleAnalyze} />}

      {stage === "analyzing" && (
        <div className={styles.analyzing}>
          <div className={styles.spinner} />
          <h2>{t("analyzing_title")}</h2>
          <p>{t("analyzing_hint")}</p>
        </div>
      )}

      {stage === "result" && result && <ResultScreen result={result} isSample={isSample} onBack={goLanding} />}

      {stage === "live" && <LiveCapture onBack={goLanding} />}
    </>
  );
}

export default App;
