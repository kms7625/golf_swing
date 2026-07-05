// JS port of golf_swing_analyzer/analyzer/geometry.py — kept numerically identical
// (verified against the Python reference with synthetic landmark input; see
// .claude/skills/golf-realtime/SKILL.md). Do not diverge the math without re-verifying.

export interface RawLandmark {
  x: number;
  y: number;
  z: number;
  visibility: number;
}

export interface NormalizedLandmark {
  pos: [number, number];
  z: number;
  vis: number;
}

export type NormalizedLandmarks = Record<number, NormalizedLandmark>;

export function normalizeLandmarks(
  landmarks: RawLandmark[],
  w: number,
  h: number
): { norm: NormalizedLandmarks; shoulderWidth: number } {
  const lSh: [number, number] = [landmarks[11].x * w, landmarks[11].y * h];
  const rSh: [number, number] = [landmarks[12].x * w, landmarks[12].y * h];
  const shoulderCenter: [number, number] = [(lSh[0] + rSh[0]) / 2, (lSh[1] + rSh[1]) / 2];
  const shoulderWidth = Math.hypot(lSh[0] - rSh[0], lSh[1] - rSh[1]) + 1e-8;

  const norm: NormalizedLandmarks = {};
  landmarks.forEach((lm, idx) => {
    const px: [number, number] = [lm.x * w, lm.y * h];
    norm[idx] = {
      pos: [(px[0] - shoulderCenter[0]) / shoulderWidth, (px[1] - shoulderCenter[1]) / shoulderWidth],
      z: lm.z,
      vis: lm.visibility,
    };
  });
  return { norm, shoulderWidth };
}

function angleFromThreePoints(a: [number, number], b: [number, number], c: [number, number]): number {
  const ba: [number, number] = [a[0] - b[0], a[1] - b[1]];
  const bc: [number, number] = [c[0] - b[0], c[1] - b[1]];
  const dot = ba[0] * bc[0] + ba[1] * bc[1];
  const magBa = Math.hypot(ba[0], ba[1]);
  const magBc = Math.hypot(bc[0], bc[1]);
  const cosine = dot / (magBa * magBc + 1e-8);
  const clamped = Math.min(1, Math.max(-1, cosine));
  return Math.round(((Math.acos(clamped) * 180) / Math.PI) * 10) / 10;
}

export function calcSpineAngle(norm: NormalizedLandmarks): number {
  const shC: [number, number] = [(norm[11].pos[0] + norm[12].pos[0]) / 2, (norm[11].pos[1] + norm[12].pos[1]) / 2];
  const hipC: [number, number] = [(norm[23].pos[0] + norm[24].pos[0]) / 2, (norm[23].pos[1] + norm[24].pos[1]) / 2];
  const dy = hipC[1] - shC[1];
  const dx = hipC[0] - shC[0];
  return Math.round(((Math.atan2(Math.abs(dx), Math.abs(dy) + 1e-8) * 180) / Math.PI) * 10) / 10;
}

export function calcShoulderRotation(norm: NormalizedLandmarks): number {
  const l = norm[11].pos;
  const r = norm[12].pos;
  return Math.round(((Math.atan2(Math.abs(r[1] - l[1]), Math.abs(r[0] - l[0]) + 1e-8) * 180) / Math.PI) * 10) / 10;
}

export function calcHipRotation(norm: NormalizedLandmarks): number {
  const l = norm[23].pos;
  const r = norm[24].pos;
  return Math.round(((Math.atan2(Math.abs(r[1] - l[1]), Math.abs(r[0] - l[0]) + 1e-8) * 180) / Math.PI) * 10) / 10;
}

export function calcKneeAngle(norm: NormalizedLandmarks, side: "left" | "right"): number {
  const [hipI, kneeI, ankleI] = side === "left" ? [23, 25, 27] : [24, 26, 28];
  return angleFromThreePoints(norm[hipI].pos, norm[kneeI].pos, norm[ankleI].pos);
}

export function calcElbowAngle(norm: NormalizedLandmarks, side: "left" | "right"): number {
  const [shI, elI, wrI] = side === "left" ? [11, 13, 15] : [12, 14, 16];
  return angleFromThreePoints(norm[shI].pos, norm[elI].pos, norm[wrI].pos);
}

export function visibilityOk(norm: NormalizedLandmarks, idx: number, thr = 0.5): boolean {
  return norm[idx].vis > thr;
}

/** Mirrors analyzer/pipeline.py's key_joints visibility gate before trusting a frame's angles. */
export const KEY_JOINTS = [11, 12, 23, 24, 25, 26];
