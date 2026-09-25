import json, pandas as pd, numpy as np
from themes import THEMES
from coverage import COVERAGE, GAP_WEIGHT
d=pd.read_pickle('complaints.pkl'); s=pd.read_pickle('themes.pkl').set_index('id')
h=pd.read_pickle('help.pkl')
d['month']=d.date.dt.to_period('M').astype(str)
months=sorted(d.month.unique())[:-1]  # drop partial current month
out=[]
for tid,label,cq,sq,_ in THEMES:
    r=s.loc[tid]; cov,ev,gap=COVERAGE[tid]
    t=d[d.theme==tid]
    subs=(t['Issue'].str.cat(t['Sub-issue'].fillna(''),sep=' — ').str.rstrip(' — ')).value_counts().head(3)
    prod=t.Product.value_counts()
    out.append(dict(id=tid,label=label,question=cq,n=int(r.n),share=float(r.share),relief=float(r.relief),
        trend=None if pd.isna(r.trend) else float(r.trend),recent=int(r.recent),prior=int(r.prior),
        coverage=cov,weight=GAP_WEIGHT[cov],unanswered=int(round(r.n*GAP_WEIGHT[cov])),gap=gap,evidence=ev,
        subissues=[[k,int(v)] for k,v in subs.items()],products=[[k,int(v)] for k,v in prod.items()],
        monthly=[int(((t.month==m)).sum()) for m in months]))
out.sort(key=lambda x:(-x['unanswered'],-x['n']))
meta=dict(total=int(len(d)),start=str(d.date.min().date()),end=str(d.date.max().date()),
    help_items=int(len(h))+35, help_pages=42, months=months,
    products={k:int(v) for k,v in d.Product.value_counts().items()},
    relief_overall=float(((d.relief)&(d['Company response to consumer']!='In progress')).sum()/(d['Company response to consumer']!='In progress').sum()),
    coverage_counts={c:sum(1 for x in out if x['coverage']==c) for c in ['covered','partial','missing']},
    complaints_by_cov={c:sum(x['n'] for x in out if x['coverage']==c) for c in ['covered','partial','missing','n/a']})
json.dump(dict(meta=meta,themes=out),open('gapdata.json','w'),indent=1)
for x in out: print(f"{x['unanswered']:>6} {x['n']:>6} {x['coverage']:8} {x['relief']:.2f} {x['trend'] if x['trend'] is None else round(x['trend'],2):>6}  {x['label']}")
print(meta)
