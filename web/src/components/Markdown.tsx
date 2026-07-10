import type { ReactNode } from "react";

/** 코칭 리포트용 초경량 마크다운 렌더러 — coach_llm.py build_prompt()가 요구하는
 * 형식(### 소제목, **굵게**, - 목록)만 다룬다. React 노드로 조립하므로 XSS 표면 없음.
 * 범용 마크다운이 필요해지면 라이브러리로 교체할 것. */

function inline(text: string, keyBase: string): ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? <strong key={`${keyBase}-${i}`}>{p.slice(2, -2)}</strong> : p
  );
}

export function Markdown({ text }: { text: string }) {
  const lines = text.split(/\r?\n/);
  const out: ReactNode[] = [];
  let listBuf: ReactNode[] = [];

  function flushList(key: string) {
    if (listBuf.length) {
      out.push(<ul key={key}>{listBuf}</ul>);
      listBuf = [];
    }
  }

  lines.forEach((line, i) => {
    const t = line.trim();
    if (/^#{1,6}\s/.test(t)) {
      flushList(`ul-${i}`);
      out.push(<h4 key={i}>{inline(t.replace(/^#{1,6}\s*/, ""), `h-${i}`)}</h4>);
    } else if (/^[-*]\s+/.test(t)) {
      listBuf.push(<li key={i}>{inline(t.replace(/^[-*]\s+/, ""), `li-${i}`)}</li>);
    } else if (t === "") {
      flushList(`ul-${i}`);
    } else {
      flushList(`ul-${i}`);
      out.push(<p key={i}>{inline(t, `p-${i}`)}</p>);
    }
  });
  flushList("ul-end");
  return <div>{out}</div>;
}
