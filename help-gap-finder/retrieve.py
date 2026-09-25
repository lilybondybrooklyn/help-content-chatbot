import json, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from themes import THEMES
raw=json.load(open('data/boa_help_content.json'))
items=[]
for path,v in raw.items():
    for it in v['items']:
        items.append(dict(url='https://www.bankofamerica.com'+path, page=v['title'], q=it['q'], a=it['a']))
h=pd.DataFrame(items); h['text']=h.q+' '+h.q+' '+h.a
h=h.drop_duplicates(subset=['q','a']).reset_index(drop=True)
h.to_pickle('help.pkl')
vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),sublinear_tf=True,min_df=1)
X=vec.fit_transform(h.text)
out={}
for tid,label,cq,sq,_ in THEMES:
    sims=cosine_similarity(vec.transform([sq+' '+cq]),X)[0]
    top=sims.argsort()[::-1][:7]
    out[tid]=[(int(i),round(float(sims[i]),3)) for i in top]
    print(f'\n=== {tid}: {cq}')
    for i in top: print(f'  [{i}] {sims[i]:.2f} {h.q[i][:110]} || {h.a[i][:230]}')
json.dump(out,open('retrieval.json','w'))
print(len(h))
