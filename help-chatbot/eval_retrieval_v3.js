// Retrieval before/after: keyword search alone (no rewriting), public corpus vs. public + proposed.
// Scores each question against the label for that corpus. Deterministic, no LLM needed.
const R = require('./retrieval.js');
const pub = require('./chunks.json'), prop = require('./chunks_proposed.json');
const E = require('./eval_set.json');
const corpora = { public: R.buildIndex(pub), v3: R.buildIndex([...pub, ...prop]) };
const out = {};
for (const [name, ix] of Object.entries(corpora)) {
  let hit = 0, n = 0; const rows = [];
  for (const e of E) {
    const expect = name === 'v3' ? (e.expect_v3 || e.expect) : e.expect;
    if (expect === 'handoff') continue;
    const re = new RegExp(e.gold, 'i');
    const res = R.search(ix, [e.q], 8);
    const h = res.findIndex(r => re.test(r.chunk.title + ' ' + r.chunk.url));
    n++; if (h >= 0) hit++;
    rows.push({ id: e.id, rank: h >= 0 ? h + 1 : null, top: res[0]?.chunk.id });
  }
  out[name] = { hit, n, rows };
  console.log(`${name.padEnd(7)} answerable questions: ${n}   keyword search finds the topic in top 8: ${hit}/${n}`);
}
// Where did proposed pages land for the questions they target?
console.log('\nProposed pages in the top 8 (v3 corpus):');
for (const e of E) {
  if ((e.expect_v3 || e.expect) === e.expect && !['e11','e44','e45','e46'].includes(e.id)) continue;
  const res = R.search(corpora.v3, [e.q], 8);
  const p = res.map((r, i) => r.chunk.src === 'proposed' ? `${r.chunk.id}@${i + 1}` : null).filter(Boolean);
  console.log(`  ${e.id} ${e.expect.padEnd(7)}->${(e.expect_v3 || e.expect).padEnd(7)} ${p.join(' ') || 'none'}  | ${e.q.slice(0, 70)}`);
}
require('fs').writeFileSync('retrieval_v3.json', JSON.stringify(out, null, 1));
