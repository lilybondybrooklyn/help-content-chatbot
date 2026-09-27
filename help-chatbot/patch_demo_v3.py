"""Makes the static GitHub Pages demo replay BOTH saved v2.2 runs (public pages, and public + proposed),
following the corpus switch. Only DEMO code paths change; the live artifact page behaves as before."""
p = 'template.html'
t = open(p).read()
if 'function demoLoad' in t:
    raise SystemExit('already patched')

def sub(old, new):
    global t
    assert t.count(old) == 1, old[:70]
    t = t.replace(old, new)

sub("const REPLAY = __REPLAY__;      // {question: saved result} from one complete eval run",
    "const REPLAY = __REPLAY__;      // {question: saved result} from one run, or {public:{...}, v3:{...}} for one run per corpus")
sub("const rep = DEMO ? REPLAY[question] : null;",
    "const rep = DEMO ? (((REPLAY && (REPLAY.public || REPLAY.v3)) ? (REPLAY[CORPUS] || {}) : REPLAY)[question] || null) : null;")
sub("This public demo can replay answers only for the 40 test questions",
    "This public demo can replay answers only for the ${EVAL.length} test questions")
sub("Object.keys(results).forEach(k=>delete results[k]); renderEval(); loadHistory(); }); }",
    "Object.keys(results).forEach(k=>delete results[k]); if (DEMO) demoLoad(); renderEval(); loadHistory(); }); }")

start = t.index("if (DEMO) {\n  const run = SAVED_RUNS")
end = t.index("renderEval(); loadHistory();\n</script>")
t = t[:start] + r"""function demoLoad(){ // static demo: show the saved run for the selected help content
  const run = SAVED_RUNS.find(r=>r.promptVersion===REPLAY_VERSION && (r.corpus||'public')===CORPUS)
    || SAVED_RUNS.find(r=>r.promptVersion===REPLAY_VERSION) || SAVED_RUNS[0];
  Object.keys(results).forEach(k=>delete results[k]);
  if (run) for (const x of run.results){ const {id,expect,q,...rest}=x; results[id]=rest; }
  const where = HAS_PROPOSED ? ` on ${CORPUS_LABEL[run?.corpus||'public'].toLowerCase()}` : '';
  $('#evalnote').textContent = `Showing the saved ${run?.promptVersion||''} run${where} (${run?.tier||'quick'} model). In this static demo the eval can't run; in the Claude artifact version, the Run eval button re-runs all ${EVAL.length} questions live.`;
}
if (DEMO) {
  if (HAS_PROPOSED && REPLAY && REPLAY.v3) { CORPUS = 'v3'; IX = IXS.v3; $('#corpus').value = 'v3'; computeBase(); }
  demoLoad();
  $('#run').hidden = true; $('#tier').hidden = true; document.querySelector('label[for="tier"]').hidden = true;
  $('#unavail').hidden = false;
  $('#unavail').innerHTML = `Public demo: answers are replayed from saved ${esc(REPLAY_VERSION||'')} eval runs for the ${EVAL.length} test questions${HAS_PROPOSED ? ', one run for each help-content setting above' : ''}. Search and the trace run live in your browser. Pick a question:` +
    `<select id="demoq" style="display:block;margin-top:8px;width:100%;font:inherit;padding:8px;border-radius:8px;border:1px solid var(--rule);background:var(--surface);color:var(--ink)"><option value="">Choose one of the ${EVAL.length} test questions…</option>${EVAL.map(e=>`<option>${esc(e.q)}</option>`).join('')}</select>`;
  $('#demoq').addEventListener('change',e=>{ if(e.target.value && !busy){ $('#q').value=e.target.value; e.target.value=''; ask(); }});
}
""" + t[end:]
open(p, 'w').write(t)
print('patched demo code in', p)
