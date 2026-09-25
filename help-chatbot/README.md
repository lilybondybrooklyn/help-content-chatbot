# Cited Help Bot

A RAG chatbot over Bank of America's public help pages. It answers only from retrieved passages, cites every claim, fact-checks figures against its sources, and hands off when the help content doesn't cover a question. This is an unofficial demo and isn't affiliated with Bank of America.

For results and the story behind it, see [`../docs/CASE_STUDY.md`](../docs/CASE_STUDY.md) and [`../docs/EVAL_REPORT.md`](../docs/EVAL_REPORT.md).

## How a question is answered
1. **Rewrite:** a quick Claude call turns the question into 3 search queries and flags off-topic questions.
2. **Retrieve:** BM25 (`retrieval.js`) runs over the question and each rewrite. The results are merged with reciprocal-rank fusion and the top 8 passages are kept.
3. **Answer:** Claude answers only from those passages. It returns `STATUS: ANSWERED | PARTIAL | HANDOFF`, cites passages as `[n]`, and adds a "Not covered:" line to partial answers.
4. **Verify:** every phone number, $ amount, day count and time in the answer must appear in its cited passages. Handoffs get a fixed, source-linked contact list instead of model-written numbers.
5. **Trace:** the page shows the queries, the passages, which were cited, and the fact-check result.

## Files
| File | Purpose |
|---|---|
| `data/boa_help_corpus_v2.json` | Raw scrape of 40 public help pages (Sept 24, 2026). Each Q&A records whether its text came from the visible page or only from structured data |
| `build_corpus.py` → `chunks.json` | Cleans and chunks the scrape into 548 passages: visible text first, boilerplate stripped, duplicates merged |
| `retrieval.js` | BM25 + stemming + synonym map + reciprocal-rank fusion. The same code runs in the browser and in node |
| `eval_set.json` | 40 test questions with expected outcome, gold topic, and notes on any relabeling |
| `eval_retrieval.js` | Keyword-only retrieval baseline (`node eval_retrieval.js`) |
| `grounding.py` | Offline fact check of saved eval runs |
| `eval_runs/` | Saved eval runs exported from the page (v1 ×2, v2 partial, v2.1) |
| `template.html` + `build_page.py` → `cited-help-bot.html` | The live chat page (runs as a Claude artifact), with Chat, Eval and How it works tabs |
| `build_demo.py` → `../docs/chatbot-demo.html` | Static demo for GitHub Pages. It replays the saved v2.1 eval answers; search, trace and fact check run live |
| `wrap.py` | Wraps a page as a full standalone HTML document |

## Running
```bash
python3 build_corpus.py
node eval_retrieval.js
python3 build_page.py
python3 build_demo.py
python3 grounding.py
```
The page calls Claude through the Claude artifacts runtime (`sample` capability) and saves eval runs to the artifact's database (`db` capability). As a plain local file, only search and trace work; the static demo replays saved answers instead.
