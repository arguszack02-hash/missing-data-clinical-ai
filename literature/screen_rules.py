#!/usr/bin/env python3
"""Deterministic two-stage screen applied to the PubMed records (search of 5 Oct 2026).

Input : pubmed_records_screened.csv (columns pmid,title,abstract,pubtypes,...; the `stage`
        column is recomputed and compared with the stored value).
Output: stage counts, topic-tag counts, and a check that the stored stages are reproduced.

Stage 1 (title): title mentions missing data / imputation.
Stage 2 (title+abstract), exclusions applied in order:
  E3 non-research item (comment, erratum, editorial, letter, retraction) or abstract < 200 chars
  E4 omics / imaging / single-cell context
  E2 no clinical or health-data context
  E1 missing data handled only incidentally (no methodological, comparative or guidance focus)
Usage: python screen_rules.py pubmed_records_screened.csv
"""
import sys, re
import pandas as pd

def screen(d):
    d = d.copy()
    d["title"] = d.title.fillna(""); d["abstract"] = d.abstract.fillna(""); d["pubtypes"] = d.pubtypes.fillna("")
    title_pass = d.title.str.contains(r"missing|imput|missingness|incomplete data|informative presence|informatively observed", case=False, regex=True)
    txt = d.title + " " + d.abstract
    E3 = d.pubtypes.str.contains("Comment|Erratum|Editorial|Letter|Retraction|Published Erratum", regex=True) | (d.abstract.str.len() < 200)
    E4 = txt.str.contains(r"\b(?:omics|genom|transcriptom|proteom|metabolom|single-cell|scRNA|gene expression|methylation|microbiom|pixel|MRI image|histopatholog|dropout imputation)", case=False, regex=True)
    health = txt.str.contains(r"clinic|patient|health|hospital|medic|EHR|electronic|intensive care|ICU|cohort|registry|trial|disease|epidemiol", case=False, regex=True)
    method = txt.str.contains(r"compar|simulat|benchmark|evaluat|review|guidance|tutorial|framework|we propose|novel|we develop|sensitivity analysis|recommend|reporting|performance of", case=False, regex=True)
    st = pd.Series("S1_excluded_title", index=d.index)
    m2 = title_pass
    st[m2 & E3] = "S2_ex_E3"
    st[m2 & ~E3 & E4] = "S2_ex_E4"
    st[m2 & ~E3 & ~E4 & ~health] = "S2_ex_E2"
    st[m2 & ~E3 & ~E4 & health & ~method] = "S2_ex_E1"
    st[m2 & ~E3 & ~E4 & health & method] = "included"
    return st

TAGS = {"MI": r"multiple imputation|MICE|chained equation|fully conditional|Rubin",
        "TREE_KNN": r"missForest|random forest imput|k-nearest|KNN",
        "DEEP_GEN": r"GAIN|generative adversarial|autoencoder|VAE|MIWAE|diffusion model",
        "SEQ_TS": r"time series|time-series|longitudinal|recurrent|LSTM|GRU|BRITS|SAITS|transformer|irregular",
        "MNAR_SENS": r"not at random|MNAR|sensitivity analys|delta|pattern-mixture|selection model|informative",
        "INDICATOR": r"missing indicator|missingness indicator|indicator method|informative presence",
        "DEPLOY": r"deploy|prediction time|real-time|implementation|at the time of prediction|external validation",
        "OUTCOME_IN_IMP": r"outcome in the imputation|include the outcome|outcome variable in the imputation",
        "FAIRNESS": r"fairness|disparit|bias across|subgroup|equity",
        "REPORTING": r"TRIPOD|PROBAST|STROBE|reporting|risk of bias",
        "REVIEW": r"systematic review|scoping review|narrative review|review of"}

if __name__ == "__main__":
    d = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "pubmed_records_screened.csv")
    st = screen(d)
    print("records:", len(d)); print(st.value_counts().to_string())
    if "stage" in d: print("matches stored stages:", bool((st.values == d.stage.values).all()))
    inc = d[st == "included"]; txt = inc.title.fillna("") + " " + inc.abstract.fillna("")
    print({k: int(txt.str.contains(p, case=False, regex=True).sum()) for k, p in TAGS.items()})
