"""Builds the static demo (for GitHub Pages): replays a saved eval run instead of calling Claude."""
import json, glob, sys, os
from wrap import wrap
t=open('template.html').read()
ch=json.load(open('chunks.json')); ev=json.load(open('eval_set.json'))
runs=[json.load(open(f)) for f in sorted(glob.glob('eval_runs/*.json'))]
runs=[r for r in runs if r.get('status','done')=='done' and len(r['results'])==len(ev)]
for r in runs: r.setdefault('promptVersion','v1')
runs.sort(key=lambda r:r['startedAt'], reverse=True)
replay_run = next(r for r in runs if r['promptVersion']=='v2.1')
qmap={e['id']:e['q'] for e in ev}
replay={qmap[x['id']]:{k:x[k] for k in ('status','answer','queries','offtopic') if k in x} for x in replay_run['results']}
slim=[{k:c[k] for k in ('id','url','page','title','text','src','kind')} for c in ch]
slimruns=[{k:r[k] for k in ('startedAt','promptVersion','tier','results','status') if k in r} for r in runs]
J=lambda o: json.dumps(o,ensure_ascii=False).replace('</','<\\/')
t=(t.replace('__RETRIEVAL__',open('retrieval.js').read()).replace('__CHUNKS__',J(slim)).replace('__EVAL__',J(ev))
    .replace('__NCHUNKS__',str(len(ch))).replace('__NEVAL__',str(len(ev))).replace('__DEMO__','true')
    .replace('__REPLAY__',J(replay)).replace('__RUNS__',J(slimruns)).replace('__REPLAY_VERSION__','"v2.1"'))
out=sys.argv[1] if len(sys.argv)>1 else os.path.join('..','docs','chatbot-demo.html')
t=wrap(t,'<div class="wrap">')
open(out,'w').write(t); print(out, len(t.encode())//1024,'KB', 'runs', len(runs))
