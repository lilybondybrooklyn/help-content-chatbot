const R=require('./retrieval.js'); const chunks=require('./chunks.json'); const E=require('./eval_set.json');
const ix=R.buildIndex(chunks); let hit=0,n=0; const rows=[];
for(const e of E){ if(e.expect==='handoff'&&e.theme!=='lookup') {}
  const res=R.search(ix,[e.q],8); const re=new RegExp(e.gold,'i');
  const h=res.findIndex(r=>re.test(r.chunk.title+' '+r.chunk.url));
  if(e.expect!=='handoff'){n++; if(h>=0)hit++;}
  rows.push(`${e.id} ${e.expect.padEnd(7)} hit@8=${h>=0?h+1:'-'} best=${(res[0]?.best||0).toFixed(1)} | ${e.q.slice(0,60)} -> ${res.slice(0,3).map(r=>r.chunk.title.slice(0,45)).join(' || ')}`);
}
console.log(rows.join('\n')); console.log(`\nretrieval hit@8 on answerable (answer+partial): ${hit}/${n}`);
