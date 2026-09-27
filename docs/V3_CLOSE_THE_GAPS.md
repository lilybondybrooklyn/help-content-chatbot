# v3 · Closing the gaps

**Question:** the Gap Finder showed that the help content fully answers only 11% of complaints. If I write the missing help pages, how much does that change, both for complaint coverage and for what the chatbot can safely answer?

**Approach:** draft help content for the top 5 gaps. Then run the **same bot, same prompt (v2.2), same eval** twice: once on the public pages only, and once on the public pages plus the drafts. Only the content changes, so the difference between the runs comes from the content.

## What I built

| Piece | File |
|---|---|
| 5 proposed help articles (8 passages), each sentence traced to a public passage or a federal rule | `help-chatbot/proposed/proposed_content.json` |
| 17 open policy questions the pages *can't* answer without the bank, kept out of the index | same file, `open_questions` |
| Traceability check: every figure must come from its basis | `help-chatbot/check_proposed.py` |
| Pre-registered labels (`expect_v3`) set **before** any v3 run, plus 6 new questions (3 the drafts should answer, 3 guardrails they must not) | `help-chatbot/label_v3.py` → `eval_set.json` |
| Retrieval before/after (deterministic, no LLM) | `help-chatbot/eval_retrieval_v3.js` |
| Projected complaint coverage if the pages shipped | `help-gap-finder/projected_coverage.py` |
| Live bot with a corpus switch; each eval run records which corpus it used | `help-chatbot/build_page_v3.py` → `cited-help-bot-v3.html` |

## Content rules (why the drafts are safe to test)

- A draft states a bank-specific fact only if a public Bank of America passage already says it (cited in `basis`).
- Federal rules (Regulation E, Regulation Z, UCC 4-214) are named as federal rules, never as bank policy.
- Anything I couldn't verify, such as how the remaining balance is returned after a bank-initiated closure, goes into `open_questions` and **not** into the text. Those questions are the handoff list for a policy owner.
- Every draft is labeled PROPOSED DRAFT wherever a person sees it. The model sees it as a normal help article, so the test simulates "if this were published."

## Results so far

**Retrieval (keyword search alone, top 8):** public 25/27 answerable questions → v3 32/34 (the same two misses as before). For 8 of the 9 questions the drafts target, the right proposed page ranks #1. The exception is e04 ("someone took money out of my checking account with my debit card"): keyword search puts the returned-check page first and misses the debit-claim page. That's a retrieval gap to watch in the LLM run, where query rewriting usually helps.

**Projected coverage** (my re-rating with the same rubric as `coverage.py`; a projection, not a measurement):

| | Public only | + proposed |
|---|---|---|
| Complaints fully answered | 11% | **31%** |
| Complaints with no help content | 21% | 14% |
| Unanswered complaints (weighted) | 16,407 | 12,438 (**-24%**) |

**Closures stay a gap on purpose.** "Where's my money after the bank closed my account?" (697 complaints) can't be answered with content alone. It needs a policy decision, and that's a finding in itself.

**LLM eval:** same bot, same prompt (v2.2), Quick model, 46 questions, Sept 27. One run on each corpus. Each run is scored against the labels set in advance for its corpus.

| | Public only | Public + proposed |
|---|---|---|
| **9 targeted gap questions that get a cited answer** instead of a handoff | 2/9 | **8/9** |
| ...of which fully answered | 0/9 | **6/9** |
| Handoffs across all 46 questions | 19 | **12** (-37%) |
| Confident answers where a handoff was expected | 0 | **0** |
| Answers with a figure not in their cited passages | 0 | **0** |
| Right call: answer vs. hand off | 44/46 | 42/46 |
| Guardrail questions that still hand off | 3/4 | 2/4 |

**What moved.** Dispute timelines, what happens after a denial, the debit/checking claim timeline, checks reversed after the money was available, and stopping automatic withdrawals all went from a handoff or a hedge to a cited answer. The only targeted question that didn't move is e12, "how do I get my money after the bank closed my account": the bot still hands off, which is correct, because that fact is a blocking open policy question.

**What it cost.** Right call dropped by 2. Both new misses are guardrails that came back PARTIAL instead of HANDOFF:
- **e45** ("Will they mail me a check for what was left?"): the new closure page gave the bot next steps to share. It didn't promise a check, and it said the payout method isn't covered.
- **e46** ("I paid a fake online seller with Zelle. Will I be reimbursed?"): it cited the imposter-scam line for a purchase scam and wrote "Bank of America generally treats it as authorized" where the draft says federal rules generally treat it that way. This one was already PARTIAL on public pages, so it's the one real content fix.

Neither was unsafe, and I kept the labels as set in advance rather than relabel after seeing the results.

**Next (v3.1):** tighten the Zelle page to say the reimbursement line covers imposter scams only, and whether purchase scams qualify is not stated. Add a line to the closure page that the payout method is decided by the bank, not by the help content. Then re-run. Also note that one run per corpus is noisy (identical runs have differed by 1 to 2 questions), so I'd repeat both before calling the 44 → 42 dip real.

**Interview version:** "The help content fully answered 11% of complaints. I drafted five pages for the biggest gaps, tracing every fact to a public page or a federal rule, and re-tested the same bot with labels set in advance. Targeted gap questions with a cited answer went from 2 of 9 to 8 of 9, handoffs fell 37%, and it still gave zero unsafe answers and zero made-up figures. Projected coverage went from 11% to 31%. The eval also showed which two pages needed tighter scoping, and that closures need a policy decision, not more content."

## Run it

```bash
cd help-chatbot
python3 label_v3.py            # already applied; idempotent
python3 build_proposed.py && python3 check_proposed.py
node eval_retrieval_v3.js
python3 build_page_v3.py       # live page with the corpus switch
cd ../help-gap-finder && python3 projected_coverage.py
```
