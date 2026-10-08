import type { ReactNode } from "react";

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      className="uiIcon" viewBox="0 0 24 24" width="18" height="18"
      fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"
    >
      {children}
    </svg>
  );
}

export function UploadIcon() {
  return <Icon><path d="M12 16V3m-4 4 4-4 4 4M4 15v5h16v-5" /></Icon>;
}

export function PlayIcon() {
  return <Icon><path d="m8 4 12 8-12 8Z" /></Icon>;
}

export function VideoCameraIcon() {
  return <Icon><rect x="3" y="6" width="12" height="12" rx="2" /><path d="m15 10 6-3v10l-6-3" /></Icon>;
}

export function HistoryIcon() {
  return <Icon><path d="M3 4v5h5M3.5 9a9 9 0 1 1-.2 6M12 7v5l3 2" /></Icon>;
}

export function SunIcon() {
  return <Icon><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5" /></Icon>;
}

export function MoonIcon() {
  return <Icon><path d="M20.5 14a9 9 0 0 1-10.5-10.5A9 9 0 1 0 20.5 14Z" /></Icon>;
}

export function ShareIcon() {
  return <Icon><path d="M12 15V3m-4 4 4-4 4 4M6 11H4v10h16V11h-2" /></Icon>;
}

export function BookmarkIcon() {
  return <Icon><path d="M6 3h12v18l-6-4-6 4Z" /></Icon>;
}

export function CompareIcon() {
  return <Icon><path d="M9 3H3v18h6m6-18h6v18h-6M7 12h10m-7-3-3 3 3 3m4-6 3 3-3 3" /></Icon>;
}

export function CoachingIcon() {
  return <Icon><path d="M5 3h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H9l-6 4V5a2 2 0 0 1 2-2ZM7 8h10M7 12h6" /></Icon>;
}

export function ShieldIcon() {
  return <Icon><path d="m12 3 8 3v6c0 4-5 8-8 9-3-1-8-5-8-9V6Z" /></Icon>;
}

export function TrimIcon() {
  return <Icon><path d="M7 4H3v16h4M17 4h4v16h-4M7 8v8m10-8v8M7 12h10" /></Icon>;
}
