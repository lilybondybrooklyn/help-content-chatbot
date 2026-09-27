"""Builds chunks_proposed.json from proposed/proposed_content.json.

Only the `a` text is indexed. `open_questions` stay out of the corpus on purpose: the bot must not
answer from facts nobody has confirmed. Chunk ids start with "p" so they never collide with the
public corpus, and src="proposed" lets the page badge them.
"""
import json
doc = json.load(open("proposed/proposed_content.json"))
chunks = []
for art in doc["articles"]:
    for it in art["items"]:
        chunks.append(dict(
            id=f"p{len(chunks)+1:02d}",
            url=f"proposed://{art['slug']}",
            page=f"PROPOSED DRAFT (not published by Bank of America): {art['title']}",
            title=it["q"], text=it["a"], src="proposed", kind="faq",
            themes=art["themes"], basis=it["basis"]))
json.dump(chunks, open("chunks_proposed.json", "w"), indent=1, ensure_ascii=False)
oq = sum(len(a["open_questions"]) for a in doc["articles"])
print(len(chunks), "proposed chunks from", len(doc["articles"]), "articles;", oq, "open policy questions kept out of the index")
