import { useEffect, useRef } from "react";

/** Google 로그인 버튼 (Google Identity Services). VITE_GOOGLE_CLIENT_ID가 없으면 아무것도 그리지 않는다. */

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
const GSI_SRC = "https://accounts.google.com/gsi/client";

interface GsiId {
  initialize: (cfg: { client_id: string; callback: (r: { credential: string }) => void }) => void;
  renderButton: (el: HTMLElement, opts: Record<string, unknown>) => void;
}
declare global {
  interface Window {
    google?: { accounts: { id: GsiId } };
  }
}

function loadGsi(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  return new Promise((resolve, reject) => {
    let script = document.querySelector<HTMLScriptElement>(`script[src="${GSI_SRC}"]`);
    if (!script) {
      script = document.createElement("script");
      script.src = GSI_SRC;
      script.async = true;
      document.head.appendChild(script);
    }
    script.addEventListener("load", () => resolve());
    script.addEventListener("error", () => reject(new Error("Google 로그인 스크립트를 불러오지 못했습니다.")));
  });
}

interface Props {
  onCredential: (credential: string) => void;
  onError: (message: string) => void;
  lang: "ko" | "en";
}

export function GoogleLoginButton({ onCredential, onError, lang }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!CLIENT_ID) return;
    let cancelled = false;
    let observer: ResizeObserver | undefined;
    loadGsi()
      .then(() => {
        const gid = window.google?.accounts.id;
        if (cancelled || !gid || !ref.current) return;
        gid.initialize({ client_id: CLIENT_ID, callback: (r) => onCredential(r.credential) });
        const render = () => {
          if (!ref.current?.clientWidth) return;
          gid.renderButton(ref.current, { theme: "outline", size: "large", width: Math.min(400, ref.current.clientWidth), text: "continue_with", locale: lang });
        };
        observer = new ResizeObserver(render);
        observer.observe(ref.current);
        render();
      })
      .catch((e: Error) => onError(e.message));
    return () => {
      cancelled = true;
      observer?.disconnect();
    };
  }, [onCredential, onError, lang]);

  if (!CLIENT_ID) return null;
  return <div ref={ref} />;
}

export const googleLoginEnabled = Boolean(CLIENT_ID);
