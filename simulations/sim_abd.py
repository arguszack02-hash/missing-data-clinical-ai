#!/usr/bin/env python3
"""Simulation case studies A (low MCAR), B (moderate MAR), D (suspected MNAR).
Ground truth is known by construction.

Cohort (n = 2000 per replicate):
  age ~ N(65,12); sex ~ Bern(0.5)
  sbp   = 130 + 0.3(age-65) + N(0,18)
  cr    = log creatinine = 0.01(age-65) + N(0,0.35)
  lac   = log lactate    = 0.4 - 0.008(sbp-130) + N(0,0.45)
  y ~ Bern(expit(b0 + b_age z(age) + b_sex sex + b_sbp z(sbp) + b_cr z(cr) + b_lac z(lac)))
  acu (auxiliary triage acuity, NOT an analysis covariate) = 0.8 z(lac) + 0.9 y + N(0,1)
z() uses fixed population constants, so target coefficients are fixed.
Analysis model: logistic regression of y on z(age), sex, z(sbp), z(cr), z(lac).
Primary estimand: beta_lac (true 0.60).  Secondary (case D): population mean of z(lac) (true 0).
"""
import os; os.environ['PYTHONWARNINGS']='ignore'
for _v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[_v]='1'
import numpy as np, pandas as pd, warnings, sys
from scipy.special import expit
from scipy import stats
import statsmodels.api as sm
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer, SimpleImputer, KNNImputer
from sklearn.ensemble import RandomForestRegressor
from joblib import Parallel, delayed
warnings.filterwarnings("ignore")

TRUE = dict(b0=-1.8, age=0.45, sex=0.20, sbp=-0.30, cr=0.40, lac=0.60)
MU = dict(age=65, sbp=130, cr=0.0, lac=0.4)
SD = dict(age=12, sbp=np.sqrt(18**2 + (0.3*12)**2), cr=np.sqrt(0.35**2+(0.01*12)**2),
          lac=np.sqrt(0.45**2 + (0.008**2)*(18**2+(0.3*12)**2)))
COLS = ["age", "sex", "sbp", "cr", "lac"]
N = 2000; M_IMP = 10
DELTAS = [-0.25, -0.5, -0.75, -1.0]


def gen(rng, n=N):
    age = rng.normal(65, 12, n); sex = rng.binomial(1, .5, n)
    sbp = 130 + .3*(age-65) + rng.normal(0, 18, n)
    cr = .01*(age-65) + rng.normal(0, .35, n)
    lac = .4 - .008*(sbp-130) + rng.normal(0, .45, n)
    z = lambda v, k: (v-MU[k])/SD[k]
    eta = TRUE["b0"] + TRUE["age"]*z(age, "age") + TRUE["sex"]*sex + TRUE["sbp"]*z(sbp, "sbp")\
        + TRUE["cr"]*z(cr, "cr") + TRUE["lac"]*z(lac, "lac")
    y = rng.binomial(1, expit(eta))
    acu = 0.8*z(lac, "lac") + 0.9*y + rng.normal(0, 1, n)
    X = pd.DataFrame(dict(age=z(age, "age"), sex=sex, sbp=z(sbp, "sbp"), cr=z(cr, "cr"), lac=z(lac, "lac")))
    return X, y, acu


def ampute(case, X, y, acu, rng):
    Xm = X.copy(); n = len(X)
    if case == "A":
        for c in ["sbp", "cr", "lac"]:
            Xm.loc[rng.random(n) < .05, c] = np.nan
    elif case == "B":
        Xm.loc[rng.random(n) < expit(-0.2 - 1.3*acu + 0.3*X.age), "lac"] = np.nan
        Xm.loc[rng.random(n) < expit(-1.2 + 0.6*X.age - 0.5*acu), "cr"] = np.nan
    elif case == "D":
        Xm.loc[rng.random(n) < expit(-0.4 - 1.4*X.lac), "lac"] = np.nan
        Xm.loc[rng.random(n) < expit(-1.2 + 0.6*X.age), "cr"] = np.nan
    return Xm


def fit_logit(X, y, cols=COLS, term="lac"):
    r = sm.Logit(y, sm.add_constant(X[cols], has_constant="add")).fit(disp=0, method="newton", maxiter=100)
    return r.params[term], r.bse[term]


def rubin(ests, ses):
    ests, ses = np.asarray(ests), np.asarray(ses); m = len(ests)
    qb = ests.mean(); ub = (ses**2).mean(); b = ests.var(ddof=1)
    t = ub + (1+1/m)*b
    r = (1+1/m)*b/ub
    df = (m-1)*(1+1/r)**2 if b > 0 else 1e6
    return qb, np.sqrt(t), df


def mi(Xm, y, acu, use_y=True, use_aux=True, m=M_IMP, seed=0, delta=0.0):
    """MICE-type MI: IterativeImputer(BayesianRidge, sample_posterior=True), m datasets, Rubin's rules.
    delta: shift (z units) added to imputed lactate (delta-adjusted MNAR sensitivity analysis)."""
    Z = Xm.copy()
    if use_aux: Z["acu"] = acu
    if use_y: Z["y"] = y
    miss = Xm.lac.isna().values
    out, means = [], []
    for k in range(m):
        imp = IterativeImputer(sample_posterior=True, max_iter=5, random_state=seed*1000+k)
        D = pd.DataFrame(imp.fit_transform(Z), columns=Z.columns)
        if delta: D.loc[miss, "lac"] += delta
        out.append(fit_logit(D, y)); means.append((D.lac.mean(), D.lac.std(ddof=1)/np.sqrt(len(D))))
    q, se, df = rubin(*zip(*out)); mq, mse, mdf = rubin(*zip(*means))
    return dict(est=q, se=se, df=df, mean=mq, mean_se=mse, mean_df=mdf)


def single(Xm, y, acu, kind, seed):
    """Single imputation. KNN and MissForest receive the same imputation inputs as MI
    (covariates + auxiliary + outcome) so that differences reflect uncertainty handling."""
    Z = Xm.copy(); Z["acu"] = acu; Z["y"] = y
    if kind == "mean":
        D = pd.DataFrame(SimpleImputer().fit_transform(Xm), columns=COLS)
    elif kind == "knn":
        Zs = (Z - Z.mean())/Z.std()
        D = pd.DataFrame(KNNImputer(n_neighbors=5).fit_transform(Zs), columns=Z.columns)*Z.std() + Z.mean()
    else:
        imp = IterativeImputer(estimator=RandomForestRegressor(n_estimators=25, min_samples_leaf=3, max_features=0.6, n_jobs=1, random_state=seed),
                               max_iter=4, random_state=seed)
        D = pd.DataFrame(imp.fit_transform(Z), columns=Z.columns)
    e, s = fit_logit(D, y)
    return dict(est=e, se=s, df=1e6, mean=D.lac.mean(), mean_se=D.lac.std(ddof=1)/np.sqrt(len(D)), mean_df=1e6)


def indicator(Xm, y):
    D = Xm.copy(); D["R_lac"] = D.lac.isna().astype(float); D["lac"] = D.lac.fillna(0.0)
    D[["sbp", "cr"]] = D[["sbp", "cr"]].fillna(D[["sbp", "cr"]].mean())
    e, s = fit_logit(D, y, cols=COLS+["R_lac"])
    return dict(est=e, se=s, df=1e6, mean=np.nan, mean_se=np.nan, mean_df=1e6)


def cca(Xm, y):
    ok = Xm.notna().all(1).values
    e, s = fit_logit(Xm[ok].reset_index(drop=True), y[ok])
    l = Xm.lac.dropna()
    return dict(est=e, se=s, df=1e6, mean=l.mean(), mean_se=l.std(ddof=1)/np.sqrt(len(l)), mean_df=1e6, cc_frac=ok.mean())


def one_rep(case, r):
    rng = np.random.default_rng(10_000*ord(case) + r)
    X, y, acu = gen(rng); Xm = ampute(case, X, y, acu, rng)
    jobs = [("Complete-case", lambda: cca(Xm, y)),
            ("Mean imputation", lambda: single(Xm, y, acu, "mean", r)),
            ("KNN (k=5)", lambda: single(Xm, y, acu, "knn", r)),
            ("MissForest (single)", lambda: single(Xm, y, acu, "rf", r)),
            ("MI without outcome", lambda: mi(Xm, y, acu, use_y=False, seed=r)),
            ("MI with outcome", lambda: mi(Xm, y, acu, use_y=True, seed=r))]
    if case in ("B", "D"):
        jobs.append(("MI without auxiliary", lambda: mi(Xm, y, acu, use_aux=False, seed=r)))
    if case == "D":
        jobs.append(("Missingness indicator", lambda: indicator(Xm, y)))
        for d in DELTAS:
            jobs.append((f"MI delta={d}", lambda d=d: mi(Xm, y, acu, seed=r, delta=d)))
    rows, cc = [], None
    mr = Xm.isna().mean()
    for lab, f in jobs:
        v = f()
        if lab == "Complete-case": cc = v["cc_frac"]
        rows.append(dict(case=case, rep=r, method=lab, **{k: v[k] for k in ["est", "se", "df", "mean", "mean_se", "mean_df"]},
                         cc_frac=cc, miss_lac=mr["lac"], miss_cr=mr["cr"], miss_sbp=mr["sbp"], prev=y.mean()))
    return rows


def one_rep_q(case, r):
    import warnings; warnings.filterwarnings("ignore")
    return one_rep(case, r)


def summarise(df):
    def agg(g):
        q = stats.t.ppf(.975, g.df); lo, hi = g.est-q*g.se, g.est+q*g.se
        qm = stats.t.ppf(.975, g.mean_df)
        covm = ((g["mean"]-qm*g.mean_se <= 0) & (0 <= g["mean"]+qm*g.mean_se)).mean() if g["mean"].notna().any() else np.nan
        return pd.Series(dict(bias=g.est.mean()-TRUE["lac"], rel_bias_pct=100*(g.est.mean()-TRUE["lac"])/TRUE["lac"],
                              emp_se=g.est.std(ddof=1), mod_se=g.se.mean(),
                              coverage=((lo <= TRUE["lac"]) & (TRUE["lac"] <= hi)).mean(), ci_width=(hi-lo).mean(),
                              rmse=np.sqrt(((g.est-TRUE["lac"])**2).mean()),
                              mean_lac_bias=g["mean"].mean(), mean_lac_cov=covm, reps=len(g)))
    return df.groupby(["case", "method"], sort=False).apply(agg).reset_index()


if __name__ == "__main__":
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rows = []
    NJ = int(os.environ.get("NJ", 6))
    for case in ["A", "B", "D"]:
        fn = f"sim_raw_{case}.csv"
        if os.path.exists(fn):
            rows += pd.read_csv(fn).to_dict("records"); continue
        out = Parallel(n_jobs=NJ)(delayed(one_rep_q)(case, r) for r in range(R))
        part = [x for o in out for x in o]; pd.DataFrame(part).to_csv(fn, index=False); rows += part
        print(case, "done", flush=True)
    df = pd.DataFrame(rows); df.to_csv("sim_abd_raw.csv", index=False)
    s = summarise(df); s.to_csv("sim_abd_summary.csv", index=False)
    print(df.groupby("case")[["miss_lac", "miss_cr", "miss_sbp", "cc_frac", "prev"]].mean().round(3).to_string())
    print(s.round(3).to_string())
