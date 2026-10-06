# Trustworthy handling of missing data in clinical AI — supplementary material

Supplementary material for:

> Z. Janah, A. Abou El Kalam, W. Aabass. *Trustworthy Handling of Missing Data in Clinical AI:
> From Multiple Imputation to Uncertainty-Aware Deep Learning.* PAUL 2026 (Springer CCIS).

Code is released under the MIT licence (`LICENSE`); tables and documentation under CC BY 4.0.

## Contents

| Folder | What it contains | Paper |
|---|---|---|
| `literature/` | `search_log.md` (databases, query strings, dates, hit counts, eligibility criteria, flow counts, sources added by targeted retrieval); `pubmed_records_screened.csv` (all 2,222 retrieved records with their screening stage); `included_records.csv` (381 eligible records with topic tags); `screening_disagreements.csv` (63 records where a language-model classifier disagreed with the rule-based screen — rule decisions retained); `fetch_pubmed.py` (re-runs the five logged queries); `screen_rules.py` (reproduces every screening decision) | Sec. 2 |
| `rubric/` | `rubric_anchors.md` / `.csv` (full level 1–5 definitions for all six dimensions); `rubric_scores_evidence.csv` (score, justification and reference for each of the 48 cells in Fig. 2); `rubric_scoring_form.xlsx` (blank form for independent raters); `rubric_agreement.py` (weighted Cohen's κ, ordinal Krippendorff's α, cells to discuss, median consensus) | Sec. 8, Fig. 2, Table 1 |
| `checklist/` | `checklist_mapping.csv` (10 items mapped to TRIPOD 2015, TRIPOD+AI, PROBAST, STROBE); `checklist_mapping_sources.txt` | Sec. 10, Table 3 |
| `simulations/` | `sim_abd.py` (cases A, B, D); `case_c_physionet.py` (case C); result tables; `data/README.md` (how to obtain PhysioNet 2012) | Sec. 9, Fig. 3, Table 2 |

## Reproducing the case studies

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cd simulations
# Cases A (MCAR), B (MAR), D (MNAR): 200 replicates each, n = 2000, m = 10 imputations.
# Data for replicate r of case C uses numpy default_rng(10000*ord(C) + r);
# imputation models use random_state = r (MI: r*1000 + k for imputation k).
python sim_abd.py 200            # -> sim_raw_{A,B,D}.csv, sim_abd_raw.csv, sim_abd_summary.csv

# Case C (PhysioNet 2012 set A; see data/README.md). 5-fold stratified CV repeated 3x (random_state=2026).
NJ=8 python case_c_physionet.py data/set-a data/Outcomes-a.txt
                                 # -> physionet_features.csv, physionet_missingness.csv,
                                 #    case_c_folds.csv, case_c_summary.csv
```

`NJ` sets the number of parallel workers. Both scripts write per-case / per-fold checkpoint files and
skip work that is already done, so an interrupted run can be restarted. On a 28-core CPU the full
runs take a few minutes each; no GPU is needed.

The result files shipped here (`sim_abd_summary.csv`, `sim_abd_raw.csv`, `case_c_summary.csv`,
`case_c_folds.csv`) are the ones reported in the paper.

## Reproducing the literature screen

```bash
cd literature
python fetch_pubmed.py           # optional: re-run the search (counts drift as PubMed is updated)
python screen_rules.py pubmed_records_screened.csv   # prints stage counts; "matches stored stages: True"
```

## Scoring the rubric independently

Give each rater `rubric/rubric_anchors.md`, `rubric/rubric_scores_evidence.csv` (justification
column optional, to avoid anchoring) and a copy of `rubric_scoring_form.xlsx`. Each rater fills one
`Rater_*` sheet (integer 1–5). Then:

```bash
cd rubric
python rubric_agreement.py rubric_scoring_form.xlsx --provisional rubric_scores_evidence.csv
```

The scores in Fig. 2 of the paper are provisional ratings by the first author.
