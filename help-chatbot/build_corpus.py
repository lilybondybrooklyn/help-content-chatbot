import json, re, hashlib
raw = json.load(open('data/boa_help_corpus_v2.json'))
BASE = 'https://www.bankofamerica.com'
def short_title(t):
    t = re.sub(r'\s*[|\-–]\s*Bank of America.*$', '', t).strip()
    return t or 'Bank of America help'
def split(text, n=900):
    sents = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    out, cur = [], ''
    for s in sents:
        if len(cur) + len(s) > n and cur:
            out.append(cur.strip()); cur = ''
        cur += s + ' '
    if cur.strip(): out.append(cur.strip())
    return out
BOILER = [r'Select Your State\s*Please tell us where you bank.*?location\.', r'Select Your State.*?Wyoming(?:\s*Go and get state information)?', r'Please select your device.*?Enter y\w*', r'^Skip to main content', r'Select Your StatePlease tell us where you bank.*?Go and get state information', r'Information for:ZIP code.*?Enter your zip code', r'Please enter the zip code.*?location\.', r'Change to accessible version']
chunks, seen = [], set()
def add(url, page, q, a, src, kind):
    key = re.sub(r'\W', '', a.lower())[:400]
    if key in seen: return
    seen.add(key)
    parts = split(a) if len(a) > 1200 else [a]
    for i, p in enumerate(parts):
        chunks.append(dict(id=f'c{len(chunks)+1:03d}', url=url, page=page,
            title=q + (f' (part {i+1})' if len(parts) > 1 else ''), text=p, src=src, kind=kind))
for path, v in raw.items():
    url, page = BASE + path, short_title(v['title'])
    for it in v['items']:
        a = re.sub(r'\s+', ' ', it['a']).strip()
        if len(a) < 20: continue
        add(url, page, it['q'].strip(), a, it['src'], 'faq')
    body = v.get('body') or ''
    for pat in BOILER: body = re.sub(pat, ' ', body, flags=re.S)
    body = re.sub(r'\s+', ' ', body).strip()
    if len(body) > 200:
        for i, p in enumerate(split(body, 1000)):
            add(url, page, f'{page} (section {i+1})', p, 'visible', 'article')
DROP=re.compile(r'cybersecurity team|deeply committed to protecting our company|should be regarded as general information|Trading in securities|investment banking activities|Get the app Please enter a valid phone', re.I)
chunks=[c for c in chunks if not DROP.search(c['text'])]
for i,c in enumerate(chunks): c['id']=f'c{i+1:03d}'
json.dump(chunks, open('chunks.json', 'w'), indent=1)
idx = '\n'.join(f"{c['id']}|{c['page'][:40]}|{c['title'][:110]}" for c in chunks)
print(len(chunks), 'chunks;', sum(len(c['text']) for c in chunks), 'chars; index', len(idx.encode()), 'bytes')
print('structured-only:', sum(c['src']=='structured' for c in chunks), 'articles:', sum(c['kind']=='article' for c in chunks))
print([c['text'][:200] for c in chunks if 'overdraft fee?' in c['title'] and 'thought' in c['title']])
print(len(raw), 'pages')
