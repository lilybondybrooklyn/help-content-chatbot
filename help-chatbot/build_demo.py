"""Builds the static demo (for GitHub Pages): replays saved eval runs instead of calling Claude.

v3: includes the proposed pages and replays one saved v2.2 run per help-content setting, so visitors
can switch between "public pages only" and "public + proposed pages" and see the before/after."""
import json, glob, sys, os
from wrap import wrap
REPLAY_VERSION = 'v2.2'
t = open('template.html').read()
pub = json.load(open('chunks.json'))
prop = json.load(open('chunks_proposed.json')) if os.path.exists('chunks_proposed.json') else []
ev = json.load(open('eval_set.json'))
runs = [json.load(open(f)) for f in sorted(glob.glob('eval_runs/*.json'))]
runs = [r.get('data', r) for r in runs]
runs = [r for r in runs if r.get('status', 'done') == 'done' and len(r['results']) >= 40]  # full runs only (40-question runs predate v3)
for r in runs: r.setdefault('promptVersion', 'v1'); r.setdefault('corpus', 'public')
runs.sort(key=lambda r: r['startedAt'], reverse=True)
qmap = {e['id']: e['q'] for e in ev}
pick = lambda x: {k: x[k] for k in ('status', 'answer', 'queries', 'offtopic') if k in x}
replay = {}
for corpus in ('public', 'v3'):
    run = next((r for r in runs if r['promptVersion'] == REPLAY_VERSION and r['corpus'] == corpus), None)
    if run: replay[corpus] = {qmap[x['id']]: pick(x) for x in run['results'] if x['id'] in qmap}
assert 'public' in replay, 'no saved public run for ' + REPLAY_VERSION
if not prop: replay = replay['public']
keys = ('id', 'url', 'page', 'title', 'text', 'src', 'kind')
slim = [{k: c[k] for k in keys} for c in pub + prop]
slimruns = [{k: r[k] for k in ('startedAt', 'promptVersion', 'corpus', 'tier', 'results', 'status') if k in r} for r in runs]
J = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
t = (t.replace('__RETRIEVAL__', open('retrieval.js').read()).replace('__CHUNKS__', J(slim)).replace('__EVAL__', J(ev))
     .replace('__NCHUNKS__', str(len(pub))).replace('__NEVAL__', str(len(ev))).replace('__DEMO__', 'true')
     .replace('__REPLAY__', J(replay)).replace('__RUNS__', J(slimruns)).replace('__REPLAY_VERSION__', J(REPLAY_VERSION)))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join('..', 'docs', 'chatbot-demo.html')
t = wrap(t, '<div class="wrap">')
open(out, 'w').write(t); print(out, len(t.encode()) // 1024, 'KB', 'runs', len(runs), 'replay corpora', list(replay) if prop else ['public'])
