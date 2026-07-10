import type {
  AnalyzeResponse,
  AuthResponse,
  AutoWindowResponse,
  CoachingResponse,
  JobStatus,
  Provider,
  SwingDetail,
  SwingRow,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8010";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `요청 실패 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

/** 로그인 상태면 Authorization 헤더 부착 — 토큰 저장소는 lib/auth.tsx와 동일 키. */
function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("swinglab_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
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

export async function analyzeAsync(
  file: File,
  startSec: number,
  endSec: number,
  sampleRate = 3
): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  form.append("start_sec", String(startSec));
  form.append("end_sec", String(endSec));
  form.append("sample_rate", String(sampleRate));
  const res = await fetch(`${API_BASE}/analyze-async`, { method: "POST", body: form });
  return handle<{ job_id: string }>(res);
}

export async function getJob(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  return handle<JobStatus>(res);
}

export interface LiveScoreResponse {
  score: number;
  issues: AnalyzeResponse["issues"];
  summary: AnalyzeResponse["summary"];
  phase_boundaries: Record<string, [number, number]>;
}

export async function scoreLive(
  wristY: number[],
  frames: Record<string, number>[]
): Promise<LiveScoreResponse> {
  const res = await fetch(`${API_BASE}/score-live`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wrist_y: wristY, frames }),
  });
  return handle<LiveScoreResponse>(res);
}

export async function detectPhases(wristY: number[]): Promise<Record<string, [number, number]>> {
  const res = await fetch(`${API_BASE}/detect-phases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wrist_y: wristY }),
  });
  return handle<Record<string, [number, number]>>(res);
}

export async function coaching(params: {
  summary: AnalyzeResponse["summary"];
  issues: AnalyzeResponse["issues"];
  provider: Provider;
  modelName?: string;
  swingId?: number;
}): Promise<CoachingResponse> {
  const res = await fetch(`${API_BASE}/coaching`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      summary: params.summary,
      issues: params.issues.map((i) => [i.level, i.message]),
      provider: params.provider,
      model_name: params.modelName ?? null,
      swing_id: params.swingId ?? null,
    }),
  });
  return handle<CoachingResponse>(res);
}

// ---------------------------------------------------------------- 인증

export async function authRegister(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handle<AuthResponse>(res);
}

export async function authLogin(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handle<AuthResponse>(res);
}

export async function deleteAccount(): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE}/auth/account`, { method: "DELETE", headers: authHeaders() });
  return handle<{ ok: boolean }>(res);
}

// ---------------------------------------------------------------- 스윙 기록

export async function saveSwing(videoName: string, payload: AnalyzeResponse): Promise<SwingRow> {
  const res = await fetch(`${API_BASE}/swings`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ video_name: videoName, payload }),
  });
  return handle<SwingRow>(res);
}

export async function listSwings(): Promise<{ swings: SwingRow[] }> {
  const res = await fetch(`${API_BASE}/swings`, { headers: authHeaders() });
  return handle<{ swings: SwingRow[] }>(res);
}

export async function getSwing(id: number): Promise<SwingDetail> {
  const res = await fetch(`${API_BASE}/swings/${id}`, { headers: authHeaders() });
  return handle<SwingDetail>(res);
}

export async function deleteSwing(id: number): Promise<{ ok: boolean }> {
  const res = await fetch(`${API_BASE}/swings/${id}`, { method: "DELETE", headers: authHeaders() });
  return handle<{ ok: boolean }>(res);
}
