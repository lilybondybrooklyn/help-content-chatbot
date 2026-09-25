import json, re, glob, sys
chunks = {c['id']: c for c in json.load(open('chunks.json'))}
PAT = re.compile(r'\b\d{3}[.\-]\d{3}[.\-]\d{4}\b|\$\d[\d,]*(?:\.\d\d)?|\b\d+\s*(?:business\s+)?days?\b|\b\d{1,2}(?::\d\d)?\s*[ap]\.?m\.?', re.I)
def norm(s): return re.sub(r'[^0-9a-z$]', '', s.lower())
for f in sorted(glob.glob('eval_runs/*.json')):
    d = json.load(open(f)); d = d.get('data', d)
    bad = 0; tot = 0; rows = []
    for r in d['results']:
        if 'answer' not in r: continue
        cited_txt = norm(' '.join(chunks[c]['text'] for c in r['cited'] if c in chunks))
        for m in PAT.finditer(r['answer']):
            tot += 1
            if norm(m.group()) not in cited_txt:
                bad += 1; rows.append(f"  {r['id']} {m.group()!r}")
    print(f, 'facts', tot, 'not in cited passages', bad); print('\n'.join(rows))
