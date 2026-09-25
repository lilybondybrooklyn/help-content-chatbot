# Help Gap Finder

This project compares CFPB consumer complaints about Bank of America with the bank's public help content. It shows which customer problems the help center doesn't answer and ranks what a self-service chatbot should cover first.

## Data (`data/`)
- `cfpb_boa_complaints.csv`: CFPB export of 30,763 complaints (Sept 2024 to Sept 2026) in four products: checking/savings, credit card, debt collection, and money transfer. The CFPB stopped publishing complaint narratives on Aug 14, 2026, so there's no free text.
- `boa_help_content.json` and `boa_help_content_extra.json`: Q&As and articles scraped on Sept 24, 2026 from 41 public Bank of America help pages, taken from each page's visible text and its FAQ structured data.

## Pipeline (Python 3 + pandas + scikit-learn), run from this folder
1. `python3 analyze.py` maps each product/issue/sub-issue combination to one of the 24 customer problems in `themes.py`, then computes volume, relief rate, and 6-month trend.
2. `python3 retrieve.py` finds the closest help content for each problem (TF-IDF) to support the hand review.
3. `coverage.py` holds the hand-judged coverage rating (covered/partial/missing) for each problem, with evidence URLs and gap notes.
4. `python3 build_data.py` computes unanswered complaints (complaints × 1 for missing, × 0.5 for partial) and writes `gapdata.json`.
5. `python3 build_report.py` builds `help-gap-finder.html` and the standalone `../docs/gap-finder.html` for GitHub Pages.
