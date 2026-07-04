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
