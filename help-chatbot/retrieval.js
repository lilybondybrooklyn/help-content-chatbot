// Keyword retrieval (BM25) with reciprocal-rank fusion across several query phrasings.
// Same code runs in the published page and in the offline eval (node).
(function (root) {
  const STOP = new Set(("a an and are as at be but by can could did do does for from had has have how i if in into is it its " +
    "me my of on or our so that the their them then there these they this to was we were what when where which who why " +
    "will with would you your yours i'm im i've ive it's dont don't bank america bofa").split(" "));
  const SYN = { // light normalisation of customer words to help-content words
    atm: "atm", debit: "debit", cheque: "check", checks: "check", fee: "fee", fees: "fee", charged: "charge",
    login: "log", signin: "log", password: "password", pw: "password", zelle: "zelle", wire: "wire",
    reimburse: "reimburs", reimbursement: "reimburs", refund: "refund", scammed: "scam", scammer: "scam",
    frozen: "freez", freeze: "freez", locked: "lock", unlock: "lock", cancel: "cancel", canceled: "cancel", cancelled: "cancel",
  };
  function stem(w) {
    if (SYN[w]) return SYN[w];
    if (w.length > 5 && w.endsWith("ing")) return w.slice(0, -3);
    if (w.length > 4 && w.endsWith("ed")) return w.slice(0, -2);
    if (w.length > 4 && w.endsWith("ies")) return w.slice(0, -3) + "y";
    if (w.length > 3 && w.endsWith("es") && !w.endsWith("ses")) return w.slice(0, -2);
    if (w.length > 3 && w.endsWith("s") && !w.endsWith("ss")) return w.slice(0, -1);
    return w;
  }
  function tokens(s) {
    return (s.toLowerCase().replace(/[’']/g, "").match(/[a-z0-9$]+/g) || [])
      .filter(w => !STOP.has(w) && w.length > 1).map(stem);
  }
  function buildIndex(chunks) {
    const docs = chunks.map(c => {
      const tf = new Map();
      const t = tokens(c.title), b = tokens(c.text);
      for (const w of t) tf.set(w, (tf.get(w) || 0) + 2);   // title words count double
      for (const w of b) tf.set(w, (tf.get(w) || 0) + 1);
      return { tf, len: t.length * 2 + b.length };
    });
    const df = new Map();
    for (const d of docs) for (const w of d.tf.keys()) df.set(w, (df.get(w) || 0) + 1);
    const avg = docs.reduce((s, d) => s + d.len, 0) / docs.length;
    return { chunks, docs, df, avg, N: docs.length };
  }
  function bm25(ix, query, k = 20) {
    const q = [...new Set(tokens(query))], k1 = 1.2, b = 0.75;
    const scores = ix.docs.map((d, i) => {
      let s = 0;
      for (const w of q) {
        const f = d.tf.get(w); if (!f) continue;
        const n = ix.df.get(w), idf = Math.log(1 + (ix.N - n + 0.5) / (n + 0.5));
        s += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * d.len / ix.avg));
      }
      return [i, s];
    }).filter(x => x[1] > 0).sort((a, b) => b[1] - a[1]).slice(0, k);
    return scores;
  }
  // Fuse several phrasings; returns [{chunk, score, best}] where best = top raw BM25 score seen.
  function search(ix, queries, k = 8) {
    const fused = new Map();
    for (const q of queries) {
      bm25(ix, q, 20).forEach(([i, s], rank) => {
        const cur = fused.get(i) || { rrf: 0, best: 0 };
        cur.rrf += 1 / (60 + rank); cur.best = Math.max(cur.best, s);
        fused.set(i, cur);
      });
    }
    return [...fused.entries()].sort((a, b) => b[1].rrf - a[1].rrf).slice(0, k)
      .map(([i, v]) => ({ chunk: ix.chunks[i], score: v.rrf, best: v.best }));
  }
  const api = { tokens, buildIndex, bm25, search };
  if (typeof module !== "undefined") module.exports = api; else root.Retrieval = api;
})(typeof window !== "undefined" ? window : globalThis);
