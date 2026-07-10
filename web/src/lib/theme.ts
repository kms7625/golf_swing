/** 라이트/다크 테마 전환 — 야외(직사광선) 가독성 대응.
 * 다크가 기본(기존 "모션 랩" 시안 유지), 선택은 localStorage에 저장.
 * 토큰 오버라이드는 index.css의 :root[data-theme="light"] 블록. */

export type Theme = "dark" | "light";

const KEY = "swinglab_theme";

export function getTheme(): Theme {
  return localStorage.getItem(KEY) === "light" ? "light" : "dark";
}

export function applyTheme(theme: Theme): void {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem(KEY, theme);
}

export function toggleTheme(): Theme {
  const next: Theme = getTheme() === "dark" ? "light" : "dark";
  applyTheme(next);
  return next;
}

export function initTheme(): void {
  document.documentElement.dataset.theme = getTheme();
}
