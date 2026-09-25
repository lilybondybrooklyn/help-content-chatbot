"""Builds the Gap Finder report: help-gap-finder.html (Claude artifact version) and ../docs/gap-finder.html (standalone page for GitHub Pages)."""
import json, os, sys
sys.path.insert(0, os.path.join('..', 'help-chatbot'))
from wrap import wrap
t = open('template.html').read()
page = t.replace('__DATA__', json.dumps(json.load(open('gapdata.json'))))
open('help-gap-finder.html', 'w').write(page)
os.makedirs(os.path.join('..', 'docs'), exist_ok=True)
open(os.path.join('..', 'docs', 'gap-finder.html'), 'w').write(wrap(page, '<div class="wrap">'))
print('wrote help-gap-finder.html and ../docs/gap-finder.html')
