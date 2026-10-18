import katex from "katex";
import { useMemo } from "react";

// Renders problem text: $inline$ and $$display$$ math via KaTeX, \$ for a literal dollar sign,
// **bold**, *italic*, and blank lines as paragraph breaks.

const escapeHtml = (s: string) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const formatText = (s: string) =>
  escapeHtml(s)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/\n\n/g, "<br/><br/>")
    .replace(/\n/g, "<br/>");

const renderMath = (tex: string, display: boolean) =>
  katex.renderToString(tex, { displayMode: display, throwOnError: false });

export function toHtml(src: string): string {
  let html = "";
  let text = "";
  let i = 0;
  while (i < src.length) {
    if (src[i] === "\\" && src[i + 1] === "$") {
      text += "$";
      i += 2;
      continue;
    }
    if (src[i] !== "$") {
      text += src[i++];
      continue;
    }
    const display = src[i + 1] === "$";
    const delim = display ? "$$" : "$";
    let j = i + delim.length;
    let tex = "";
    while (j < src.length && !src.startsWith(delim, j)) {
      if (src[j] === "\\") tex += src[j++]; // keep escapes (incl. \$) inside math
      tex += src[j++];
    }
    html += formatText(text) + renderMath(tex, display);
    text = "";
    i = j + delim.length;
  }
  return html + formatText(text);
}

export function MathText({ src, as: Tag = "span" }: { src: string; as?: "span" | "div" }) {
  const html = useMemo(() => toHtml(src), [src]);
  return <Tag className="math-text" dangerouslySetInnerHTML={{ __html: html }} />;
}
