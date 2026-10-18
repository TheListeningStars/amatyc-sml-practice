// Reads [[label, text], ...] on stdin; prints a JSON list of KaTeX errors.
// Math is split out exactly as the app does it (app/src/MathText.tsx). Run with cwd=app/.
import { createRequire } from "module";
const katex = createRequire(process.cwd() + "/")("katex");

function segments(src) {
  const out = [];
  let i = 0;
  while (i < src.length) {
    if (src[i] === "\\" && src[i + 1] === "$") { i += 2; continue; }
    if (src[i] !== "$") { i++; continue; }
    const d = src[i + 1] === "$" ? "$$" : "$";
    let j = i + d.length, tex = "";
    while (j < src.length && !src.startsWith(d, j)) { if (src[j] === "\\") tex += src[j++]; tex += src[j++]; }
    out.push(j >= src.length ? [null, d] : [tex, d]);
    i = j + d.length;
  }
  return out;
}

let input = "";
for await (const chunk of process.stdin) input += chunk;
const errors = [];
for (const [label, text] of JSON.parse(input)) {
  for (const [tex, d] of segments(text)) {
    if (tex === null) { errors.push(`${label}: unterminated ${d}`); continue; }
    try { katex.renderToString(tex, { throwOnError: true, displayMode: d === "$$" }); }
    catch (e) { errors.push(`${label}: KaTeX error in "${tex.slice(0, 60)}": ${e.message.split("\n")[0].slice(0, 120)}`); }
  }
}
console.log(JSON.stringify(errors));
