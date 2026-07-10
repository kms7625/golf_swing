import type { AnalyzeResponse } from "./types";

/** 결과 공유 카드(1080×1350 PNG) 생성 — 캔버스 로컬 렌더링, 서버 호출 없음.
 * 색은 다크 "모션 랩" 토큰 고정값(공유 이미지는 테마와 무관하게 브랜드 룩 유지). */

const BG = "#14181d";
const PANEL = "#1c222a";
const LINE = "#262e38";
const COPPER = "#dd8b57";
const TEAL = "#5fb8b0";
const TEXT = "#dfe4e8";
const STEEL = "#8ca0ac";

export interface ShareLabels {
  scoreLabel: string; // TOTAL SCORE
  gradeLabel: string; // 등급
  spine: string;
  xfactor: string;
  shoulder: string;
}

function gradeOf(score: number): string {
  if (score >= 95) return "S";
  if (score >= 85) return "A";
  if (score >= 70) return "B";
  if (score >= 55) return "C";
  return "D";
}

function loadImage(b64: string): Promise<HTMLImageElement | null> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => resolve(null);
    img.src = `data:image/jpeg;base64,${b64}`;
  });
}

export async function buildShareCard(result: AnalyzeResponse, labels: ShareLabels): Promise<Blob> {
  const W = 1080;
  const H = 1350;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d")!;

  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, W, H);

  // 상단 브랜드 + 날짜
  ctx.fillStyle = TEXT;
  ctx.font = "700 44px Bahnschrift, 'Segoe UI', sans-serif";
  ctx.fillText("SWING", 60, 96);
  const sw = ctx.measureText("SWING").width;
  ctx.fillStyle = COPPER;
  ctx.fillText(".LAB", 60 + sw, 96);
  ctx.fillStyle = STEEL;
  ctx.font = "400 30px Consolas, monospace";
  const date = new Date().toLocaleDateString();
  ctx.fillText(date, W - 60 - ctx.measureText(date).width, 92);

  // 임팩트 장면 (4:3 cover 크롭)
  const impact = result.rep_frames["임팩트"] ?? Object.values(result.rep_frames)[0];
  const imgTop = 140;
  const imgH = 700;
  if (impact) {
    const img = await loadImage(impact);
    if (img) {
      const targetRatio = W / imgH;
      const srcRatio = img.width / img.height;
      let sx = 0, sy = 0, sw2 = img.width, sh = img.height;
      if (srcRatio > targetRatio) {
        sw2 = img.height * targetRatio;
        sx = (img.width - sw2) / 2;
      } else {
        sh = img.width / targetRatio;
        sy = (img.height - sh) / 2;
      }
      ctx.drawImage(img, sx, sy, sw2, sh, 0, imgTop, W, imgH);
    }
  }
  // 코너 브래킷 장식 (모션 랩 시그니처) — 좌상/우하 L자
  ctx.strokeStyle = COPPER;
  ctx.lineWidth = 6;
  ctx.beginPath();
  ctx.moveTo(24, imgTop + 40);
  ctx.lineTo(24, imgTop - 16);
  ctx.lineTo(80, imgTop - 16);
  ctx.moveTo(W - 24, imgTop + imgH - 40);
  ctx.lineTo(W - 24, imgTop + imgH + 16);
  ctx.lineTo(W - 80, imgTop + imgH + 16);
  ctx.stroke();

  // 점수 패널
  const py = imgTop + imgH + 40;
  ctx.fillStyle = PANEL;
  ctx.fillRect(60, py, 400, 330);
  ctx.strokeStyle = LINE;
  ctx.lineWidth = 2;
  ctx.strokeRect(60, py, 400, 330);

  ctx.fillStyle = STEEL;
  ctx.font = "700 26px Bahnschrift, 'Segoe UI', sans-serif";
  ctx.fillText(labels.scoreLabel.toUpperCase(), 100, py + 64);
  ctx.fillStyle = COPPER;
  ctx.font = "700 150px Consolas, monospace";
  ctx.fillText(String(result.score), 100, py + 220);
  ctx.fillStyle = TEXT;
  ctx.font = "700 40px Bahnschrift, 'Segoe UI', sans-serif";
  ctx.fillText(`${labels.gradeLabel} ${gradeOf(result.score)}`, 100, py + 290);

  // 지표 3종
  const metrics: [string, string][] = [
    [labels.spine, `${result.summary.spine_angle_delta}°`],
    [labels.xfactor, `${result.summary.x_factor}°`],
    [labels.shoulder, `${result.summary.shoulder_rotation_max}°`],
  ];
  metrics.forEach(([k, v], i) => {
    const my = py + i * 110;
    ctx.fillStyle = PANEL;
    ctx.fillRect(500, my, 520, 100);
    ctx.strokeStyle = LINE;
    ctx.strokeRect(500, my, 520, 100);
    ctx.fillStyle = STEEL;
    ctx.font = "700 24px Bahnschrift, 'Segoe UI', sans-serif";
    ctx.fillText(k.toUpperCase(), 530, my + 42);
    ctx.fillStyle = TEAL;
    ctx.font = "700 44px Consolas, monospace";
    ctx.fillText(v, 530, my + 88);
  });

  // 푸터
  ctx.strokeStyle = LINE;
  ctx.beginPath();
  ctx.moveTo(60, H - 90);
  ctx.lineTo(W - 60, H - 90);
  ctx.stroke();
  ctx.fillStyle = STEEL;
  ctx.font = "400 26px Consolas, monospace";
  ctx.fillText("AI GOLF SWING ANALYSIS", 60, H - 40);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("card render failed"))), "image/png");
  });
}

/** 모바일이면 공유 시트, 아니면 PNG 다운로드. 반환값: 실제 수행된 동작. */
export async function shareOrDownload(blob: Blob, filename: string): Promise<"shared" | "downloaded"> {
  const file = new File([blob], filename, { type: "image/png" });
  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file] });
      return "shared";
    } catch {
      // 사용자가 시트를 닫은 경우 등 — 다운로드로 폴백하지 않고 조용히 종료해도 되지만
      // 명시적 동작 보장을 위해 다운로드 폴백
    }
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
  return "downloaded";
}
