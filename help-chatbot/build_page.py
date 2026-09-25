import json
t=open('template.html').read()
ch=json.load(open('chunks.json')); ev=json.load(open('eval_set.json'))
slim=[{k:c[k] for k in ('id','url','page','title','text','src','kind')} for c in ch]
t=t.replace('__RETRIEVAL__',open('retrieval.js').read()).replace('__CHUNKS__',json.dumps(slim,ensure_ascii=False).replace('</','<\\/')).replace('__EVAL__',json.dumps(ev)).replace('__NCHUNKS__',str(len(ch))).replace('__NEVAL__',str(len(ev))).replace('__DEMO__','false').replace('__REPLAY__','null').replace('__RUNS__','[]').replace('__REPLAY_VERSION__','null')
open('cited-help-bot.html','w').write(t); print(len(t.encode())//1024,'KB')
