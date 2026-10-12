/** 라이트/다크 테마 전환 — 야외(직사광선) 가독성 대응.
 * 승인된 라이트 테마가 기본, 선택은 localStorage에 저장.
 * 다크 토큰은 미승인 추정이며 index.css에 정의. */

export type Theme = "dark" | "light";

const KEY = "swinglab_theme";

export function getTheme(): Theme {
  return localStorage.getItem(KEY) === "dark" ? "dark" : "light";
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
