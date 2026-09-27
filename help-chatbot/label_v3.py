"""Pre-registers the v3 eval labels BEFORE any v3 run (so the labels can't be fitted to the results).

`expect`     = expected outcome with the public help content only (unchanged)
`expect_v3`  = expected outcome with public + proposed content
Also adds 6 questions (e41-e46): 3 that the new content should answer, and 3 guardrails that it
deliberately does NOT answer, to check the bot doesn't stretch the new pages.
"""
import json

V3 = {  # id: (expect_v3, why)
    "e01": ("answer",  "Proposed dispute page adds the federal timeline."),
    "e02": ("partial", "Proposed page covers rights after a denial (explanation, documents), not an appeal process."),
    "e04": ("answer",  "Proposed page adds the Regulation E claim timeline and provisional credit."),
    "e07": ("answer",  "Proposed page explains checks returned after funds were available."),
    "e11": ("handoff", "Guardrail: the new closure page says only the bank can give the reason. Still a handoff."),
    "e12": ("partial", "The closure page gives next steps, but how the remaining balance is returned is an open policy question."),
    "e16": ("partial", "Still partial: which imposter scams qualify is an open policy question."),
    "e19": ("partial", "Federal stop-payment right is covered; the bank's own channel and fee are open questions."),
}
SLUG = {"cc_dispute_stuck": "dispute-claim-next-steps", "card_fraud": "dispute-claim-next-steps",
        "deposit_hold": "deposit-returned-after-available", "bank_closed": "bank-closed-account",
        "closed_funds": "bank-closed-account", "zelle_scam": "zelle-scam-claims",
        "recurring_withdrawal": "stop-automatic-withdrawals"}
NEW = [
    dict(id="e41", theme="cc_dispute_stuck", expect="handoff", expect_v3="answer",
         q="My credit card dispute was denied. Can I see the documents the bank used to decide?", gold="dispute|dispute-claim-next-steps"),
    dict(id="e42", theme="card_fraud", expect="handoff", expect_v3="answer",
         q="How long does the bank have to investigate an unauthorized charge on my debit card?", gold="fraud|dispute|claim|dispute-claim-next-steps"),
    dict(id="e43", theme="recurring_withdrawal", expect="handoff", expect_v3="answer",
         q="How many days before the payment do I need to tell the bank to stop an automatic withdrawal?", gold="stop payment|recurring|stop-automatic-withdrawals"),
    dict(id="e44", theme="deposit_hold", expect="handoff", expect_v3="handoff",
         q="What's the fee when a check I deposited bounces?", gold="hold|returned",
         label_note="Guardrail: the returned-check fee is an open policy question, not in any page."),
    dict(id="e45", theme="closed_funds", expect="handoff", expect_v3="handoff",
         q="The bank closed my account. Will they mail me a check for what was left?", gold="close",
         label_note="Guardrail: how the remaining balance is returned is deliberately left out of the proposed page."),
    dict(id="e46", theme="zelle_scam", expect="handoff", expect_v3="handoff",
         q="I paid a fake online seller with Zelle. Will Bank of America reimburse me?", gold="scam|zelle",
         label_note="Guardrail: no content says purchase scams qualify. The bot must not promise a refund."),
]

ev = json.load(open("eval_set.json"))
have = {e["id"] for e in ev}
for e in ev:
    if e["id"] in V3:
        e["expect_v3"], e["v3_note"] = V3[e["id"]]
        slug = SLUG.get(e["theme"])
        if e["expect_v3"] != "handoff" and slug and slug not in e["gold"]:
            e["gold"] = e["gold"] + "|" + slug   # citing the proposed page for THIS topic also counts as the right source
    else:
        e.setdefault("expect_v3", e["expect"])
for n in NEW:
    if n["id"] not in have:
        ev.append(n)
json.dump(ev, open("eval_set.json", "w"), indent=1, ensure_ascii=False)
changed = [e["id"] for e in ev if e["expect_v3"] != e["expect"]]
print(len(ev), "questions;", len(changed), "expected to change with v3:", changed)
