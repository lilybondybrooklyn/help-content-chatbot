"""Builds the live v3 page (runs as a Claude artifact): public passages + proposed pages, with the corpus switch."""
import json
t = open('template.html').read()
pub = json.load(open('chunks.json')); prop = json.load(open('chunks_proposed.json')); ev = json.load(open('eval_set.json'))
keys = ('id', 'url', 'page', 'title', 'text', 'src', 'kind')
slim = [{k: c[k] for k in keys} for c in pub + prop]
J = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
t = (t.replace('__RETRIEVAL__', open('retrieval.js').read()).replace('__CHUNKS__', J(slim)).replace('__EVAL__', J(ev))
      .replace('__NCHUNKS__', str(len(pub))).replace('__NEVAL__', str(len(ev))).replace('__DEMO__', 'false')
      .replace('__REPLAY__', 'null').replace('__RUNS__', '[]').replace('__REPLAY_VERSION__', 'null'))
open('cited-help-bot-v3.html', 'w').write(t)
print('cited-help-bot-v3.html', len(t.encode()) // 1024, 'KB;', len(pub), 'public +', len(prop), 'proposed passages;', len(ev), 'eval questions')
