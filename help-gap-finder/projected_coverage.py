"""Projected coverage IF the proposed pages were published.

Re-rates only the themes the proposed pages target, using the same rubric as coverage.py
(covered / partial / missing), and recomputes the headline numbers from gapdata.json.
This is a projection from my own re-rating, not a measured outcome. The measured part is the eval.
"""
import json

V3_RATING = {  # theme: (new rating, why)
    "cc_dispute_stuck": ("covered", "Adds the federal timeline and what happens after a denial. Appeal process is still an open policy question."),
    "card_fraud":       ("covered", "Adds the debit/checking claim timeline, provisional credit and what happens after a denial."),
    "deposit_hold":     ("partial", "Explains reversals after funds were available. Missing deposits and cashing a check are still not covered."),
    "bank_closed":      ("partial", "Gives next steps. The reason is individual, so the bot still hands off on 'why'."),
    "closed_funds":     ("missing", "Unchanged on purpose: how the remaining balance is returned is a blocking open policy question."),
    "zelle_scam":       ("partial", "Explains unauthorized vs. authorized and how to report. Which scams qualify is still unknown."),
    "recurring_withdrawal": ("partial", "Adds the federal stop-payment right. The bank's own channel and fee are open questions."),
}
W = {"missing": 1.0, "partial": 0.5, "covered": 0.0, "n/a": 0.0}

g = json.load(open("gapdata.json"))
themes, total = g["themes"], g["meta"]["total"]

def summarize(rating_of):
    by = {"covered": 0, "partial": 0, "missing": 0, "n/a": 0}
    unanswered = 0.0
    for t in themes:
        r = rating_of(t)
        by[r] += t["n"]
        unanswered += t["n"] * W[r]
    return by, unanswered

before_by, before_un = summarize(lambda t: t["coverage"])
after_by, after_un = summarize(lambda t: V3_RATING.get(t["id"], (t["coverage"],))[0])

pct = lambda x: f"{100 * x / total:.0f}%"
print(f"{'':32}{'public only':>14}{'+ proposed':>14}")
for k in ("covered", "partial", "missing"):
    print(f"{'Complaints ' + k:32}{pct(before_by[k]):>14}{pct(after_by[k]):>14}")
print(f"{'Unanswered complaints (weighted)':32}{before_un:>14,.0f}{after_un:>14,.0f}   ({(after_un - before_un) / before_un:+.0%})")
print("\nRe-rated themes:")
for t in themes:
    if t["id"] in V3_RATING:
        r, why = V3_RATING[t["id"]]
        print(f"  {t['label'][:44]:44} {t['n']:>6,}  {t['coverage']:>8} -> {r:8} {why}")
json.dump(dict(before=before_by, after=after_by, unanswered_before=before_un, unanswered_after=after_un,
               total=total, rerated={k: v[0] for k, v in V3_RATING.items()}),
          open("projected_coverage.json", "w"), indent=1)
