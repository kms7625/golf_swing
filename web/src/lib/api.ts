import type { AnalyzeResponse, AutoWindowResponse, CoachingResponse, Provider } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8010";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `요청 실패 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function autoWindow(file: File): Promise<AutoWindowResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/auto-window`, { method: "POST", body: form });
  return handle<AutoWindowResponse>(res);
}

export async function analyze(
  file: File,
  startSec: number,
  endSec: number,
  sampleRate = 3
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("start_sec", String(startSec));
  form.append("end_sec", String(endSec));
  form.append("sample_rate", String(sampleRate));
  const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  return handle<AnalyzeResponse>(res);
}

export async function coaching(params: {
  summary: AnalyzeResponse["summary"];
  issues: AnalyzeResponse["issues"];
  provider: Provider;
  apiKey: string;
  modelName?: string;
}): Promise<CoachingResponse> {
  const res = await fetch(`${API_BASE}/coaching`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      summary: params.summary,
      issues: params.issues.map((i) => [i.level, i.message]),
      provider: params.provider,
      api_key: params.apiKey,
      model_name: params.modelName ?? null,
    }),
  });
  return handle<CoachingResponse>(res);
}
