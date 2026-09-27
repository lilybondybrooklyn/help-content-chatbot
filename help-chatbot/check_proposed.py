"""Traceability check for the proposed pages: every figure must come from its basis.

For each proposed item, every phone number, $ amount, day count and time in the text must appear in a
public passage listed in `basis`, OR the item must cite a federal rule (listed for manual review).
Fails loudly if a figure has no source, or a basis chunk id doesn't exist.
"""
import json, re, sys
PAT = re.compile(r'\b\d{3}[.\-]\d{3}[.\-]\d{4}\b|\$\d[\d,]*(?:\.\d\d)?|\b\d+\s*(?:business\s+)?days?\b|\b\d{1,2}(?::\d\d)?\s*[ap]\.?m\.?', re.I)
norm = lambda s: re.sub(r'[^0-9a-z$]', '', s.lower())
pub = {c['id']: c for c in json.load(open('chunks.json'))}
doc = json.load(open('proposed/proposed_content.json'))
bad = 0
for art in doc['articles']:
    for it in art['items']:
        ids = [b for b in it['basis'] if re.fullmatch(r'c\d{3}', b)]
        rules = [b for b in it['basis'] if b not in ids]
        missing = [i for i in ids if i not in pub]
        src = norm(' '.join(pub[i]['text'] for i in ids if i in pub))
        figs = sorted(set(m.group().strip() for m in PAT.finditer(it['a'])))
        unsourced = [f for f in figs if norm(f) not in src]
        status = 'ok'
        if missing: status = f'MISSING BASIS {missing}'; bad += 1
        elif unsourced and not rules: status = f'UNSOURCED {unsourced}'; bad += 1
        elif unsourced: status = f'from federal rule ({"; ".join(rules)}): {", ".join(unsourced)}'
        print(f"[{art['slug']}] {it['q'][:60]}\n    {status}")
print('\nFAIL' if bad else '\nAll figures traced to a public passage or a cited federal rule.')
sys.exit(1 if bad else 0)
