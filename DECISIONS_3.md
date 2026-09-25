# Decision log

Each entry records the decision, the options I considered, and why I chose the one I did.

### 1. Analyze a peer bank, not my employer
**Options:** my employer's help content · a peer bank · both side by side.
**Chose:** a peer bank (Bank of America).
**Why:** the method is identical, and the result can be published without raising questions about using an employer's content or implying internal knowledge.

### 2. Keep the scope to self-service product areas
**Options:** all CFPB products · checking/savings, credit card, debt collection and money transfer.
**Chose:** those four.
**Why:** they map to self-service and help-center use cases. Mortgages and student loans add volume but little relevance to a help chatbot.

### 3. Group by CFPB categories when the narratives disappeared
**Context:** the CFPB stopped publishing complaint narratives on Aug 14, 2026.
**Options:** abandon the project · cluster a small older sample · map the structured categories.
**Chose:** map 140 product/issue/sub-issue combinations to 24 problems written as customer questions.
**Tradeoff:** the problems are coarser and there are no customer quotes. In exchange, the method is fully reproducible and covers every complaint.

### 4. Rate coverage by hand, with evidence
**Options:** a similarity threshold · an LLM judge · manual review of retrieved candidates.
**Chose:** manual review of TF-IDF and keyword matches, with the evidence URL and gap note recorded for every rating.
**Why:** 24 judgments is a manageable number, and a reviewer can challenge any rating by following its evidence.

### 5. Prioritize by unanswered complaints, then adjust for bot suitability
**Formula:** complaints × (1 if missing, 0.5 if partial), then weighed against growth, relief rate and legal sensitivity.
**Example:** collections is a large gap, but it's shrinking, rarely resolved in the customer's favor, and legally sensitive. So the recommendation is to write that help content first and have the bot route to a person.

### 6. Keyword search (BM25) plus LLM query rewriting, not embeddings (for now)
**Context:** the chat page runs as a self-contained web page, which can't download an embedding model.
**Why this is acceptable:** with about 550 FAQ passages, keyword search alone finds the right topic for 25 of 27 answerable test questions. Query rewriting covers vocabulary mismatches such as "a charge I didn't make" vs. "unauthorized transaction".
**Next:** measure embeddings on the same eval before switching.

### 7. Index the visible text, not structured data
**Finding:** the overdraft FAQ's JSON-LD still shows a $35 fee in its example, while the visible page shows $10.
**Chose:** visible text first, structured data only for questions that don't appear visibly, and a check comparing numbers between the two versions.

### 8. Three answer states instead of two
**Chose:** ANSWERED / PARTIAL / HANDOFF, with a required "Not covered:" line on PARTIAL answers.
**Why:** most real gaps are partial. The content covers how to start but not what happens next, and a partial answer with an honest gap is more useful than a flat refusal.

### 9. A deterministic control for high-stakes details
**Problem:** tightening the prompt in v2 led the model to write the general phone number from memory in handoff answers.
**Chose:** after every answer, a fact check that confirms each phone number, dollar amount, day count and time appears in the cited passages. On handoffs, the model writes no numbers, and the page shows a fixed, source-linked contact list instead.
**Principle:** use prompts for tone and judgment, and code for facts that must be exact.

### 10. "Right call" as the headline metric
**Why:** exact status matching swings by 1 to 2 questions between identical runs, because answered vs. partial is subjective. Whether the bot tries to answer or sends the customer elsewhere is the decision that matters, and the one that can do harm if it's wrong.

### 11. Show the work in the UI
**Chose:** a trace panel with the search queries, the retrieved passages, which ones were cited, and the fact-check result.
**Why:** it lets anyone audit a single answer, which matters more for a bank chatbot than a polished answer.
