# Case study: finding help-content gaps in complaint data and building a chatbot that respects them

**Role:** product manager, doing the analysis and the build · **Timeline:** September 2026 · **Data:** public only

## TL;DR

Most self-service chatbot projects start from the help content a company already has. I started from what customers complain about. I grouped 30,763 CFPB complaints about Bank of America into 24 customer problems and checked each one against the bank's public help pages. Only 11% of complaints were about a problem the help content fully answers. I then built a RAG chatbot over that help content and tested it on questions drawn from the gaps. It made the right call on answering vs. handing off for 39 of 40 questions, and it never confidently answered a question it should have handed off.

---

## 1. The problem

Help centers are usually written from the company's point of view: how to use a feature, where to find a setting. Customers arrive with problems: my deposit is on hold, my dispute was denied, the bank closed my account. When the help center doesn't answer the real problem, customers call, and some escalate to a regulator.

The question I wanted to answer: **which problems do customers escalate that the help content doesn't answer, and what should a self-service chatbot cover first?**

## 2. Discovery: complaints vs. help content

**Data.** The CFPB's public Consumer Complaint Database has every complaint against Bank of America, N.A. from Sept 1, 2024 to Sept 23, 2026, in four product areas: checking/savings, credit card, debt collection, and money transfer. That's 30,763 complaints. I chose a peer bank, not my own employer, so the work could be shared publicly.

**A constraint I didn't plan for.** On Aug 14, 2026, the CFPB stopped publishing complaint narratives, and the older narratives are no longer in the public API either. My plan had been to cluster the customers' own words. I switched to the CFPB's structured product → issue → sub-issue fields. I mapped the 140 combinations into 24 customer problems and wrote each one as the question a customer would ask.

**Help content.** I scraped the Q&As and articles from 41 public help pages covering deposits, debit, credit cards, Zelle, online banking, security, disputes, and credit-card assistance, about 390 items in all. For each problem, I pulled the closest matches (TF-IDF plus a keyword sweep), read them, and rated coverage:
- **covered:** the help content answers the question
- **partial:** it explains how to start, but not what the complaints are about (timelines, denials, recourse)
- **missing:** nothing addresses it

**What I found**
- **11%** of complaints concern a fully covered problem, **65%** a partly covered one, and **21%** one with no help content.
- **Six problems have no help content at all:** the bank closing an account, getting money back from a closed account, collections (threats and disputed debts), being unable to open an account, and stopping recurring withdrawals.
- **The most common gap is "what happens next".** The help content explains how to file a dispute or report fraud, then stops. Complaints are about denied claims, reversed credits, and timelines. More than half of dispute and fraud complaints ended with the bank giving money back, which suggests customers escalate because they can't see where their claim stands, not because they were wrong.
- **A content-quality bug.** The overdraft FAQ's visible answer uses a **$10** fee in its example, but the hidden structured data (JSON-LD, which search engines and AI answer engines read) still says **$35**. That's a real risk for any retrieval-based bot.

![Chatbot priorities](images/gap-finder-chatbot-priorities.png)

## 3. Prioritization: what the chatbot should cover first

I ranked problems by **unanswered complaints**: complaints × 1 when coverage is missing, × 0.5 when it's partial. I also weighed growth, the relief rate, and **how much a bot can actually help**. Collections is a large gap, but complaints about it are falling (-30% vs. the prior six months), the bank is rarely found at fault (3 to 6% relief), and the topic is legally sensitive. So I recommended writing that help content first and having the bot route those questions to a person.

Top five: dispute and fraud-claim status, deposit holds, bank-initiated closures, Zelle scams, and stopping recurring withdrawals. Each one has a defined handoff rule, such as "never guess the reason for an account closure; route to a specialist."

## 4. The build: a chatbot that cites and hands off

**Design goal:** answer only from the bank's public help content, show the sources, and when the content doesn't cover something, say so rather than guess.

**Pipeline**
1. **Rewrite.** A fast Claude call turns the customer's words into three help-center-style search queries and flags off-topic questions.
2. **Retrieve.** BM25 keyword search runs over 548 passages for the original question plus each rewrite. The results are merged with reciprocal-rank fusion and the top 8 are kept.
3. **Answer.** Claude answers only from those 8 passages, cites every claim, and labels the answer ANSWERED, PARTIAL (with a "Not covered:" line) or HANDOFF.
4. **Verify.** A deterministic fact check confirms that every phone number, dollar amount, day count and time in the answer appears in the passages it cites. On a handoff, the page adds verified contact options rather than letting the model pick a phone number.
5. **Show the work.** A trace panel shows the queries, the passages, which passages were cited, and the fact-check result.

**Corpus hygiene mattered more than I expected.** I rebuilt the corpus from the visible page text and used structured data only when a question didn't appear visibly (this fixed the $35 issue). I also stripped state pickers, navigation and legal boilerplate, merged duplicate answers, and split long answers into passages of about 900 characters.

![Retrieval trace](images/chatbot-answer-with-trace.png)

## 5. Evaluation

I wrote a 40-question test set from the gap analysis: questions the help content covers, partly covers, and doesn't cover, plus everyday lookups and two off-topic questions. Each question has an expected outcome and the help topic it should retrieve. See [EVAL_REPORT.md](EVAL_REPORT.md) for details.

| | v1 (run 1) | v1 (run 2) | v2.1 |
|---|---|---|---|
| Right call: answer vs. hand off | 37/40 | 38/40 | **39/40** |
| Exact outcome (answered / partial / handoff) | 35/40 | 34/40 | 34/40 |
| Confident answers where a handoff was expected | 0 | 0 | 0 |
| Answers citing the expected topic | 25/26 | 26/26 | 24/26 |
| Answers with a figure missing from their cited passages | 1 | 0 | 4 |

**What I learned from the eval**
- **Some "failures" were my labels.** Four expected outcomes were wrong. For example, the overdraft fee never appears as a stated fee, only inside an example, so "partly covered" is the right answer. I fixed the labels, documented why, and re-scored every run against the current labels so the runs stay comparable.
- **"Exact outcome" is noisy.** Two runs of the same version differed by one question, and the line between "answered" and "partial" is fuzzy. **"Right call" (answer vs. hand off) is the metric that matters for customers**, so I made it the headline number.
- **Fixing one behavior broke another.** Version 2 cut unnecessary hedging, but in handoff answers the model started writing the general phone number from memory, uncited. The fact check caught all four cases. In v2.2 I took phone numbers out of the model's hands: handoffs now show a fixed, source-linked list of contacts. The lesson: **for high-stakes details, don't rely on a prompt when a deterministic control will do.**

## 6. What I'd do next

- **Measure embeddings against keyword search** on the same 40 questions. Keyword search alone, on the raw question, already finds the right topic in the top 8 for 25 of 27 answerable questions, so I'd only switch if embeddings do measurably better.
- **Fill the content gaps first.** The bot can only answer as well as its sources. Pages on bank-initiated closures, collections and identity theft would move the most complaints.
- **Use first-party data.** The CFPB data is a biased sample of escalated complaints. At a bank, I'd run the same method on chat transcripts and call reasons.
- **Track in production:** containment rate, handoff rate by intent, the "was this helpful" rate on PARTIAL answers, and repeat contacts within 7 days.

## Limits

CFPB complaints skew toward escalated, unresolved problems. The relief rates come from the bank's own response codes. The coverage ratings are my judgment, with evidence linked for each one. The response timelines I cite in the recommendations are federal maximums, not bank policy. The chatbot covers only the public pages captured on Sept 24, 2026.
