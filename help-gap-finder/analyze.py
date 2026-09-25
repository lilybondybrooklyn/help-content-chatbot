import json, pandas as pd, numpy as np
from themes import THEMES, assign
d = pd.read_csv('data/cfpb_boa_complaints.csv')
d['theme'] = [assign(a,b,c) for a,b,c in zip(d['Product'], d['Issue'], d['Sub-issue'])]
d['date'] = pd.to_datetime(d['Date received']).dt.tz_localize(None)
d['relief'] = d['Company response to consumer'].str.contains('relief')
closed = ~d['Company response to consumer'].isin(['In progress'])
end = d['date'].max()
recent = d['date'] > end - pd.Timedelta(days=182)
prior = (d['date'] <= end - pd.Timedelta(days=182)) & (d['date'] > end - pd.Timedelta(days=364))
rows=[]
for tid,label,q,sq,_ in THEMES:
    t = d[d.theme==tid]
    rows.append(dict(id=tid,label=label,n=len(t),share=len(t)/len(d),
        relief=(t.relief & closed).sum()/max(1,(closed & (d.theme==tid)).sum()),
        recent=int((recent&(d.theme==tid)).sum()), prior=int((prior&(d.theme==tid)).sum())))
s = pd.DataFrame(rows).sort_values('n',ascending=False)
s['trend']=(s.recent/s.prior.replace(0,np.nan)-1)
pd.set_option('display.width',200)
print(s.to_string(float_format=lambda x:f'{x:.2f}'))
print('overall relief', (d.relief&closed).sum()/closed.sum(), 'recent window', end - pd.Timedelta(days=182), end)
d.to_pickle('complaints.pkl'); s.to_pickle('themes.pkl')
