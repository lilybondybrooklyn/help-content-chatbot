"""One-time patch: adds a corpus switch (public vs. public + proposed) to template.html.

The prompt (v2.2) is untouched, so a public run and a v3 run differ ONLY in the passages available.
Pages built without proposed chunks (build_demo.py) look and behave exactly as before.
"""
import re
p = 'template.html'
t = open(p).read()
if 'HAS_PROPOSED' in t:
    raise SystemExit('already patched')

def sub(old, new, count=1):
    global t
    n = t.count(old)
    assert n == count, f'expected {count} match(es), found {n}: {old[:70]!r}'
    t = t.replace(old, new)

# 1. two indexes + current corpus
sub("const IX = Retrieval.buildIndex(CHUNKS);",
"""const HAS_PROPOSED = CHUNKS.some(c=>c.src==='proposed');
const IXS = { public: Retrieval.buildIndex(CHUNKS.filter(c=>c.src!=='proposed')), v3: HAS_PROPOSED ? Retrieval.buildIndex(CHUNKS) : null };
let CORPUS = 'public', IX = IXS.public;
const expOf = (e, corpus=CORPUS) => corpus==='v3' ? (e.expect_v3||e.expect) : e.expect;
const CORPUS_LABEL = { public:'Public pages only', v3:'Public + proposed pages' };""")

# 2. the model sees a proposed passage as a plain help article (no "draft" cue), so only content differs
sub("Source: ${h.chunk.page} (${h.chunk.url})",
    "Source: ${h.chunk.src==='proposed' ? h.chunk.page.replace(/^PROPOSED DRAFT[^:]*:\\s*/,'')+' (help article)' : h.chunk.page+' ('+h.chunk.url+')'}")

# 3. badge proposed passages in the trace and in source lists (people always see what's a draft)
sub("${h.chunk.src==='structured'?'structured data':h.chunk.kind}",
    "${h.chunk.src==='proposed'?'<b style=\"color:var(--part)\">PROPOSED DRAFT</b>':h.chunk.src==='structured'?'structured data':h.chunk.kind}")
sub("""<a href="${esc(h.chunk.url)}" target="_blank" rel="noopener" style="font-size:12px">${esc(h.chunk.page)}</a>""",
    """${h.chunk.src==='proposed'?`<span style="font-size:12px;color:var(--part)">${esc(h.chunk.page)}</span>`:`<a href="${esc(h.chunk.url)}" target="_blank" rel="noopener" style="font-size:12px">${esc(h.chunk.page)}</a>`}""")
src_old = """`<a href="${esc(t.hits[n-1].chunk.url)}" target="_blank" rel="noopener"><span class="n">[${n}]</span>${esc(t.hits[n-1].chunk.title)}</a>`"""
src_new = """(t.hits[n-1].chunk.src==='proposed' ? `<span><span class="n">[${n}]</span>${esc(t.hits[n-1].chunk.title)} <b style="color:var(--part)">(proposed draft)</b></span>` : `<a href="${esc(t.hits[n-1].chunk.url)}" target="_blank" rel="noopener"><span class="n">[${n}]</span>${esc(t.hits[n-1].chunk.title)}</a>`)"""
sub(src_old, src_new, count=2)

# 4. scoring uses the label for the corpus a run used
sub("function outcome(e, r){", "function outcome(e, r, corpus=CORPUS){ const x = expOf(e, corpus);")
sub("  if (r.status === EXPECT_STATUS[e.expect]) return 'pass';\n  if (e.expect!=='handoff' && r.status!=='HANDOFF') return 'soft';\n  if (e.expect==='handoff' && r.status==='PARTIAL') return 'soft';",
    "  if (r.status === EXPECT_STATUS[x]) return 'pass';\n  if (x!=='handoff' && r.status!=='HANDOFF') return 'soft';\n  if (x==='handoff' && r.status==='PARTIAL') return 'soft';")
sub("function score(res){", "function score(res, corpus=CORPUS){ const X = id => expOf(EV[id], corpus);")
sub("const o = id => outcome(EV[id], res[id]);", "const o = id => outcome(EV[id], res[id], corpus);")
sub("const needSrc = ids.filter(id=>EV[id].expect!=='handoff'", "const needSrc = ids.filter(id=>X(id)!=='handoff'")
sub("unsafe: ids.filter(id=>EV[id].expect==='handoff' && res[id].status==='ANSWERED').length,",
    "unsafe: ids.filter(id=>X(id)==='handoff' && res[id].status==='ANSWERED').length,")
sub("((EV[id].expect==='handoff')===(res[id].status==='HANDOFF'))", "((X(id)==='handoff')===(res[id].status==='HANDOFF'))")

# 5. search-hit baseline recomputed per corpus
sub("EVAL.forEach(e => { const re = new RegExp(e.gold,'i'); e.base = Retrieval.search(IX,[e.q],8).some(h=>re.test(h.chunk.title+' '+h.chunk.url)); });",
    "function computeBase(){ EVAL.forEach(e => { const re = new RegExp(e.gold,'i'); e.base = Retrieval.search(IX,[e.q],8).some(h=>re.test(h.chunk.title+' '+h.chunk.url)); }); }\ncomputeBase();")
sub("const baseN = EVAL.filter(e=>e.expect!=='handoff')", "const baseN = EVAL.filter(e=>expOf(e)!=='handoff')")
sub("const src = r && e.expect!=='handoff'", "const src = r && expOf(e)!=='handoff'")
sub("""<td><span class="status ${EXPECT_STATUS[e.expect]}">${e.expect}</span></td>""",
    """<td><span class="status ${EXPECT_STATUS[expOf(e)]}">${expOf(e)}</span>${expOf(e)!==e.expect?`<div style="font-size:11px;color:var(--muted);margin-top:3px">was ${e.expect}</div>`:''}</td>""")
sub("<td>${e.expect==='handoff'?'':(e.base?", "<td>${expOf(e)==='handoff'?'':(e.base?")
sub("const note = e.label_note ?", "const note = (CORPUS==='v3' && e.v3_note) ? `<div style=\"font-size:12px;color:var(--muted);margin-top:3px\">v3: ${esc(e.v3_note)}</div>` : e.label_note ?")

# 6. runs record their corpus; history shows it and scores each run with its own labels
sub("status, tier, promptVersion: PROMPT_VERSION, corpusChunks: CHUNKS.length,",
    "status, tier, promptVersion: PROMPT_VERSION, corpus: CORPUS, corpusChunks: IX.N,")
sub("<th>Prompt</th><th>Model</th>", "<th>Prompt</th><th>Corpus</th><th>Model</th>")
sub("const res = Object.fromEntries((r.results||[]).map(x=>[x.id,x])); const s = score(res);",
    "const res = Object.fromEntries((r.results||[]).map(x=>[x.id,x])); const s = score(res, r.corpus||'public');")
sub("<td class=\"num\">${esc(r.promptVersion||'v1')}</td><td>${esc(r.tier||'')}</td>",
    "<td class=\"num\">${esc(r.promptVersion||'v1')}</td><td>${esc(CORPUS_LABEL[r.corpus||'public'])}</td><td>${esc(r.tier||'')}</td>")
sub("last.promptVersion===PROMPT_VERSION && last.status!=='done'",
    "last.promptVersion===PROMPT_VERSION && (last.corpus||'public')===CORPUS && last.status!=='done'")

# 7. the switch itself (hidden when there are no proposed pages)
sub("""<p class="notice">""",
    """<div class="notice" id="corpusbar" hidden style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><b>Help content:</b>
  <select id="corpus"><option value="public">Public pages only (what's live today)</option><option value="v3">Public + proposed pages (drafts for the top 5 gaps)</option></select>
  <span style="color:var(--muted)">Proposed pages are drafts I wrote for this project. They are not published by Bank of America, and they're marked PROPOSED DRAFT wherever they appear.</span></div>
<p class="notice">""")
sub("computeBase();", """computeBase();
if (HAS_PROPOSED) { $('#corpusbar').hidden = false; $('#corpus').addEventListener('change', e => {
  if (evalCtl && !evalCtl.signal.aborted && $('#run').disabled) { e.target.value = CORPUS; return; } // no switching mid-run
  CORPUS = e.target.value; IX = IXS[CORPUS]; computeBase(); Object.keys(results).forEach(k=>delete results[k]); renderEval(); loadHistory(); }); }""")
open(p, 'w').write(t)
print('patched', p)
