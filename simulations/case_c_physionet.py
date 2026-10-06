#!/usr/bin/env python3
"""Case C: longitudinal ICU EHR (PhysioNet/CinC Challenge 2012, set A, 4000 stays, first 48 h).
Outcome: in-hospital death.  Features per variable: last value and number of measurements.
Strategies compared with 5-fold stratified CV (repeated 3x):
  S1 mean imputation (no indicators)
  S2 MICE-type single imputation (IterativeImputer)
  S3 mean imputation + missingness indicators
  S4 MI (m=5, sample_posterior) with risk averaged over imputations; per-patient between-imputation SD reported
  S5 gradient boosting with native missing-value handling (HistGradientBoosting)
Deployment-time shift: at test time, lactate is set missing for every patient (test-ordering policy change).
Metrics: AUROC, Brier score, calibration slope and intercept (logistic recalibration).
"""
import os, glob, sys, warnings
for _v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[_v]='1'
import numpy as np, pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score, brier_score_loss
import statsmodels.api as sm
from joblib import Parallel, delayed
warnings.filterwarnings("ignore")

STATIC = ["Age", "Gender", "Height", "ICUType", "Weight"]


def load(set_dir, outcomes):
    recs = []
    for f in sorted(glob.glob(os.path.join(set_dir, "*.txt"))):
        d = pd.read_csv(f)
        rid = int(d.loc[d.Parameter == "RecordID", "Value"].iloc[0])
        st = d[d.Time == "00:00"].set_index("Parameter").Value
        ts = d[~d.Parameter.isin(STATIC + ["RecordID"]) & (d.Value >= 0)]
        row = {"RecordID": rid}
        for s in ["Age", "Gender"]:
            v = st.get(s, np.nan); row[s] = np.nan if (pd.isna(v) or v < 0) else v
        row["ICUType"] = st.get("ICUType", np.nan)
        for p, g in ts.groupby("Parameter"):
            row[f"{p}_last"] = g.Value.iloc[-1]; row[f"{p}_med"] = g.Value.median(); row[f"{p}_n"] = len(g)
        recs.append(row)
    X = pd.DataFrame(recs)
    o = pd.read_csv(outcomes)[["RecordID", "In-hospital_death"]]
    X = X.merge(o, on="RecordID")
    return X


def calib(y, p):
    p = np.clip(p, 1e-6, 1-1e-6); lp = np.log(p/(1-p))
    r = sm.Logit(y, sm.add_constant(lp)).fit(disp=0)
    ri = sm.GLM(y, np.ones_like(lp), offset=lp, family=sm.families.Binomial()).fit()
    return r.params[1], ri.params[0]


def lr():
    return LogisticRegression(C=0.5, max_iter=3000)


def run_fold(k, tr, te, X, y, val_cols, n_cols, ind_cols):
    Xtr, Xte = X.iloc[tr], X.iloc[te]; ytr, yte = y[tr], y[te]
    out = []
    scen = {"as-collected": Xte.copy()}
    sh = Xte.copy(); lc = [c for c in val_cols if c.startswith("Lactate_")]
    sh[lc] = np.nan; sh["Lactate_n"] = 0
    scen["lactate unavailable at deployment"] = sh
    base = val_cols + n_cols + ["ICU_2", "ICU_3", "ICU_4"]

    def ind(D):
        return D[val_cols].isna().astype(float).add_prefix("R_")[["R_"+c for c in ind_cols]]

    _Z = Xtr[base].copy(); _Z["y"] = ytr; lo, hi = _Z.min(), _Z.max()

    m1 = make_pipeline(SimpleImputer(), StandardScaler(), lr()).fit(Xtr[base], ytr)

    m2 = make_pipeline(IterativeImputer(max_iter=5, random_state=k, min_value=lo.values[:-1], max_value=hi.values[:-1]), StandardScaler(), lr()).fit(Xtr[base], ytr)

    Atr = pd.concat([Xtr[base], ind(Xtr)], axis=1)
    m3 = make_pipeline(SimpleImputer(), StandardScaler(), lr()).fit(Atr, ytr)

    mis = []
    for j in range(5):
        imp = IterativeImputer(max_iter=5, sample_posterior=True, random_state=100*k+j,
                               min_value=lo.values, max_value=hi.values)
        Ztr = Xtr[base].copy(); Ztr["y"] = ytr
        for _try in range(5):
            arr = imp.fit_transform(Ztr)
            if np.isfinite(arr).all(): break
            imp.set_params(random_state=100*k+j+1000*(_try+1))
        Dtr = pd.DataFrame(arr, columns=Ztr.columns)

        imp_te = IterativeImputer(max_iter=5, sample_posterior=True, random_state=100*k+j+50,
                                  min_value=lo.values[:-1], max_value=hi.values[:-1]).fit(Xtr[base])
        sc = StandardScaler().fit(Dtr[base]); mdl = lr().fit(sc.transform(Dtr[base]), ytr)
        mis.append((imp_te, sc, mdl))

    m5 = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0,
                                        random_state=k).fit(Xtr[base], ytr)
    for sname, T in scen.items():
        P = {"Mean imputation": m1.predict_proba(T[base])[:, 1],
             "Single MICE": m2.predict_proba(T[base])[:, 1],
             "Mean + missingness indicators": m3.predict_proba(pd.concat([T[base], ind(T)], axis=1))[:, 1],
             "GBM, native missing handling": m5.predict_proba(T[base])[:, 1]}
        draws = np.array([mdl.predict_proba(sc.transform(imp.transform(T[base])))[:, 1] for imp, sc, mdl in mis])
        P["MI (m=5), averaged risk"] = draws.mean(0)
        mi_sd = draws.std(0, ddof=1)
        for meth, p in P.items():
            cs, ci = calib(yte, p)
            out.append(dict(fold=k, scenario=sname, method=meth, auroc=roc_auc_score(yte, p), brier=brier_score_loss(yte, p),
                            cal_slope=cs, cal_int=ci,
                            mi_sd_median=np.median(mi_sd) if meth.startswith("MI") else np.nan,
                            mi_sd_p90=np.quantile(mi_sd, .9) if meth.startswith("MI") else np.nan))
    return out


if __name__ == "__main__":
    set_dir, outc = sys.argv[1], sys.argv[2]
    if os.path.exists("physionet_features.csv"):
        D = pd.read_csv("physionet_features.csv")
    else:
        D = load(set_dir, outc); D.to_csv("physionet_features.csv", index=False)
    print("loaded", D.shape, flush=True)
    y = D["In-hospital_death"].values
    for c in [2, 3, 4]: D[f"ICU_{c}"] = (D.ICUType == c).astype(float)

    val_cols = ["Age", "Gender"] + sorted(c for c in D.columns if c.endswith("_last"))
    n_cols = sorted(c for c in D.columns if c.endswith("_n"))
    D[n_cols] = D[n_cols].fillna(0)

    miss = D[val_cols].isna().mean()
    val_cols = [c for c in val_cols if miss[c] <= 0.90]

    val_cols = [c for c in val_cols if D[c].nunique(dropna=True) > 1]
    ind_cols = [c for c in val_cols if c.endswith("_last") and miss[c] > 0.05]
    pd.DataFrame(dict(feature=miss.index, missing_frac=miss.values)).to_csv("physionet_missingness.csv", index=False)
    print("features", len(val_cols), "value,", len(n_cols), "count,", len(ind_cols), "indicators; mortality", y.mean().round(3), flush=True)
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=2026)
    os.makedirs("case_c_parts", exist_ok=True)
    def run_save(k, tr, te):
        fn = f"case_c_parts/fold_{k:02d}.csv"
        if not os.path.exists(fn):
            import warnings; warnings.filterwarnings("ignore")
            pd.DataFrame(run_fold(k, tr, te, D, y, val_cols, n_cols, ind_cols)).to_csv(fn + ".tmp", index=False)
            os.replace(fn + ".tmp", fn)
        return pd.read_csv(fn)
    res = Parallel(n_jobs=int(os.environ.get("NJ", 4)))(delayed(run_save)(k, tr, te) for k, (tr, te) in enumerate(cv.split(D, y)))
    R = pd.concat(res, ignore_index=True); R.to_csv("case_c_folds.csv", index=False)
    S = R.groupby(["scenario", "method"], sort=False).agg(
        auroc=("auroc", "mean"), auroc_sd=("auroc", "std"), brier=("brier", "mean"),
        cal_slope=("cal_slope", "mean"), cal_int=("cal_int", "mean"),
        mi_sd_median=("mi_sd_median", "mean"), mi_sd_p90=("mi_sd_p90", "mean")).reset_index()
    S.to_csv("case_c_summary.csv", index=False)
    print(S.round(3).to_string())
