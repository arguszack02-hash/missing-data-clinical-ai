#!/usr/bin/env python3
"""Inter-rater agreement for the trustworthiness rubric.

Usage:  python rubric_agreement.py rubric_scoring_form.xlsx [--provisional rubric_scores_evidence.csv]

Reads every sheet named Rater_* (rows 4.., columns B..G = six dimensions, integer 1-5),
then reports:
  * quadratic-weighted Cohen's kappa for each rater pair (overall and per dimension)
  * Krippendorff's alpha (ordinal) across all raters
  * exact and within-one-level agreement
  * cells with a spread >= 2 levels (to resolve by discussion)
  * median consensus matrix, written to rubric_consensus.csv
Requires: pandas, numpy, openpyxl, scikit-learn.
"""
import sys, itertools, argparse
import numpy as np, pandas as pd
from sklearn.metrics import cohen_kappa_score

DIMS = ["Uncertainty quantification","Interpretability / transparency","MNAR robustness",
        "Bias / fairness safeguards","Computational efficiency","Regulatory auditability"]

def read_raters(path):
    xl = pd.ExcelFile(path); out = {}
    for sh in xl.sheet_names:
        if not sh.startswith("Rater_"): continue
        df = pd.read_excel(path, sheet_name=sh, header=2).iloc[:, :7]
        df.columns = ["family"] + DIMS
        df = df.dropna(subset=["family"]).set_index("family")
        if df[DIMS].isna().all().all(): continue            # empty sheet -> rater did not participate
        if df[DIMS].isna().any().any():
            raise ValueError(f"{sh}: incomplete scores")
        v = df[DIMS].astype(int)
        if not v.isin([1,2,3,4,5]).all().all(): raise ValueError(f"{sh}: values outside 1-5")
        out[sh] = v
    if len(out) < 2: raise SystemExit("Need at least two completed rater sheets.")
    return out

def kripp_alpha_ordinal(data):
    """data: raters x units array (np.nan for missing). Ordinal metric (Krippendorff 2004)."""
    data = np.asarray(data, float); vals = np.unique(data[~np.isnan(data)])
    idx = {v:i for i,v in enumerate(vals)}; k = len(vals)
    o = np.zeros((k,k))
    for u in data.T:
        u = u[~np.isnan(u)]; m = len(u)
        if m < 2: continue
        for a, b in itertools.permutations(range(m), 2):
            o[idx[u[a]], idx[u[b]]] += 1/(m-1)
    n_c = o.sum(1); n = n_c.sum()
    d = np.zeros((k,k))
    for c in range(k):
        for kk in range(k):
            lo, hi = min(c,kk), max(c,kk)
            d[c,kk] = (n_c[lo:hi+1].sum() - (n_c[lo]+n_c[hi])/2)**2
    Do = (o*d).sum()/n
    De = (np.outer(n_c,n_c)*d).sum()/(n*(n-1))
    return 1 - Do/De if De > 0 else float("nan")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("xlsx"); ap.add_argument("--provisional")
    a = ap.parse_args(); R = read_raters(a.xlsx); names = list(R)
    flat = {r: R[r].values.ravel() for r in names}
    print(f"Raters: {names}; units = {len(flat[names[0]])} cells")
    rows = []
    for r1, r2 in itertools.combinations(names, 2):
        rec = {"pair": f"{r1}-{r2}",
               "kappa_w_overall": cohen_kappa_score(flat[r1], flat[r2], weights="quadratic", labels=[1,2,3,4,5]),
               "exact_%": 100*np.mean(flat[r1]==flat[r2]),
               "within1_%": 100*np.mean(abs(flat[r1]-flat[r2])<=1)}
        for d in DIMS:
            rec[f"kappa_w[{d}]"] = cohen_kappa_score(R[r1][d], R[r2][d], weights="quadratic", labels=[1,2,3,4,5])
        rows.append(rec)
    res = pd.DataFrame(rows); print(res.round(3).T.to_string())
    alpha = kripp_alpha_ordinal(np.vstack([flat[r] for r in names]))
    print(f"\nKrippendorff alpha (ordinal), {len(names)} raters: {alpha:.3f}")
    stack = np.stack([R[r].values for r in names])
    spread = stack.max(0) - stack.min(0)
    fam = R[names[0]].index
    flag = [(fam[i], DIMS[j], stack[:, i, j].tolist()) for i, j in zip(*np.where(spread >= 2))]
    print(f"\nCells with spread >= 2 levels (discuss): {len(flag)}")
    for f in flag: print("  ", f)
    cons = pd.DataFrame(np.median(stack, 0), index=fam, columns=DIMS)
    cons.to_csv("rubric_consensus.csv"); res.to_csv("rubric_agreement_pairs.csv", index=False)
    if a.provisional:
        p = pd.read_csv(a.provisional).pivot(index="family", columns="dimension", values="score").loc[fam, DIMS]
        print("\nQuadratic-weighted kappa, median consensus vs provisional evidence-anchored scores:",
              round(cohen_kappa_score(np.rint(cons.values.ravel()).astype(int), p.values.ravel(), weights="quadratic", labels=[1,2,3,4,5]), 3))
    print("\nWrote rubric_consensus.csv, rubric_agreement_pairs.csv")

if __name__ == "__main__":
    main()
