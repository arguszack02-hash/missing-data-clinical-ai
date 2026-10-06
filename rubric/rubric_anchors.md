# Trustworthiness rubric — anchored level definitions

Each method family is scored 1–5 on six dimensions. A score is the highest level whose definition is fully satisfied by the best-documented published member of the family (ties → lower level). Every score must cite evidence.

## Uncertainty quantification

| Level | Definition |
|---|---|
| 1 | Returns a single value; no representation of uncertainty about the missing values. |
| 2 | Uncertainty obtainable only by wrapping the method in external resampling (e.g. bootstrap, MC-dropout, ensembles); no native pooling rule. |
| 3 | Natively produces multiple stochastic draws, but no established pooling rule or evidence of near-nominal interval coverage. |
| 4 | Multiple draws with an established pooling rule (e.g. Rubin's rules); near-nominal coverage shown in published simulations under MAR. |
| 5 | Level 4 and recommended as the uncertainty-propagating approach in clinical methods or reporting guidance. |

## Interpretability / transparency

| Level | Definition |
|---|---|
| 1 | Opaque learned model; no component of the imputation rule can be inspected. |
| 2 | Partially inspectable learned structure (attention maps, explicit observation graph), but no per-variable model. |
| 3 | Non-parametric but inspectable (variable importance, donor neighbours, out-of-bag error per variable). |
| 4 | Explicit per-variable conditional models whose form and coefficients can be printed and checked, with standard diagnostics. |
| 5 | Rule stated fully in one sentence; no fitted model. |

## MNAR robustness

| Level | Definition |
|---|---|
| 1 | Biased unless data are MCAR. |
| 2 | Valid under MAR (correct model); no MNAR mechanism, sensitivity parameter, or use of missingness pattern. |
| 3 | Valid under MAR and either supports a standard MNAR sensitivity analysis OR uses the missingness mask/indicators as model input. |
| 4 | A published member explicitly models the MNAR mechanism (selection, pattern-mixture or self-masking) under stated identifying assumptions. |
| 5 | Level 4 and validated on clinical data within an established sensitivity-analysis framework. |

## Bias / fairness safeguards

| Level | Definition |
|---|---|
| 1 | Known to distort subgroup distributions (e.g. shrinkage to a global value) or to drop subgroups differentially; no audit mechanism. |
| 2 | No built-in subgroup handling; subgroup error audit possible only post hoc, without per-value uncertainty. |
| 3 | Can condition explicitly on subgroup variables/interactions and supports post-hoc subgroup error audit. |
| 4 | Level 3 and uncertainty allows subgroup-level interval reporting, with clinical evidence that subgroup-aware imputation reduces disparity. |
| 5 | Explicit fairness constraint or objective built into the imputation, validated on clinical data. |

## Computational efficiency

| Level | Definition |
|---|---|
| 1 | Deep model needing GPU, extensive tuning and large training sets for clinical-scale data. |
| 2 | Deep or graph model trainable on CPU for small/medium data; tuning required. |
| 3 | Iterative fitting repeated m times or tree ensembles; minutes on 10^4-10^5 rows on CPU. |
| 4 | One fitted model per variable; seconds on 10^4-10^5 rows on CPU. |
| 5 | Closed-form or no fitting. |

## Regulatory auditability

| Level | Definition |
|---|---|
| 1 | No reference implementation or documentation standard. |
| 2 | Reference implementation exists; reproducible with seeds and stored weights, but no standard diagnostics. |
| 3 | Seed-reproducible open-source implementation with some standard diagnostics (e.g. OOB error). |
| 4 | Established software with documented diagnostics, and covered by reporting-guideline items. |
| 5 | Level 4 and named as an accepted primary or sensitivity procedure in regulatory/trial guidance. |

## Provisional scores (first-author ratings, Fig. 2)

The justification and supporting reference for every cell are in `rubric_scores_evidence.csv`.

| Family | UQ | INT | MNAR | FAIR | COMP | AUD |
|---|---|---|---|---|---|---|
| Listwise deletion | 1 | 5 | 1 | 1 | 5 | 4 |
| Mean / regression | 1 | 4 | 1 | 1 | 5 | 3 |
| Multiple Imputation (MICE/FCS) | 5 | 4 | 4 | 3 | 3 | 5 |
| MissForest | 2 | 3 | 2 | 3 | 3 | 3 |
| GAIN (GAN) | 3 | 1 | 2 | 2 | 2 | 2 |
| VAE (MIWAE / not-MIWAE) | 3 | 1 | 4 | 2 | 2 | 2 |
| RNN / Transformer (BRITS, SAITS) | 2 | 1 | 3 | 2 | 1 | 2 |
| GNN (GRAPE) | 2 | 2 | 2 | 2 | 2 | 2 |
