/** golf_swing_analyzer/ui/components.py get_status()와 동일한 로직 — UI 표시용 상태 판정. */
export function getStatus(
  val: number,
  goodLo: number,
  goodHi: number,
  warnLo?: number,
  warnHi?: number
): "ok" | "warn" | "crit" {
  if (val >= goodLo && val <= goodHi) return "ok";
  if (warnLo !== undefined && warnHi !== undefined && val >= warnLo && val <= warnHi) return "warn";
  return "crit";
}

/** 색각이상 대응 — 상태를 색에만 의존하지 않도록 값 옆에 병기하는 기호. */
export function statusIcon(status: "ok" | "warn" | "crit"): string {
  return status === "ok" ? "✓" : status === "warn" ? "⚠" : "✕";
}
