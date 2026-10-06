# Literature search log

**Date of search:** 5 October 2026  
**Database:** PubMed/MEDLINE  
**Publication-date limits:** 2015/01/01 – 2026/09/30 (`datetype=pdat`)  
**Field tags:** `[tiab]`

## 1. Queries and hit counts

| ID | Query string | Hits |
|---|---|---|
| Q1_ml_imputation_clinical | `(imputation[tiab] OR "missing data"[tiab] OR "missing values"[tiab]) AND ("electronic health record*"[tiab] OR "electronic medical record*"[tiab] OR EHR[tiab] OR clinical[tiab] OR "intensive care"[tiab]) AND ("deep learning"[tiab] OR "machine learning"[tiab] OR "neural network*"[tiab] OR generative[tiab] OR transformer*[tiab] OR autoencoder*[tiab])` | 1408 |
| Q2_MI_prediction_models | `"multiple imputation"[tiab] AND ("prediction model*"[tiab] OR "prognostic model*"[tiab] OR "risk prediction"[tiab] OR "clinical prediction"[tiab])` | 339 |
| Q3_MNAR_informative | `("missing not at random"[tiab] OR MNAR[tiab] OR "informative missingness"[tiab] OR "informative presence"[tiab] OR "informatively missing"[tiab]) AND (clinical[tiab] OR health*[tiab] OR patient*[tiab] OR "electronic health record*"[tiab])` | 291 |
| Q4_missing_indicator_deployment | `("missing indicator*"[tiab] OR "missingness indicator*"[tiab] OR "missing-indicator"[tiab] OR ("missing data"[tiab] AND (deployment[tiab] OR "real-time"[tiab] OR "at prediction time"[tiab]))) AND (prediction[tiab] OR predictive[tiab] OR model*[tiab])` | 231 |
| Q5_reporting_guidance | `("missing data"[tiab] OR imputation[tiab]) AND (TRIPOD[tiab] OR PROBAST[tiab] OR STROBE[tiab] OR "reporting guideline*"[tiab] OR "reporting quality"[tiab] OR "risk of bias"[tiab]) AND (prediction[tiab] OR "machine learning"[tiab] OR "artificial intelligence"[tiab])` | 208 |

Union of PMIDs: **2225**; records with retrievable metadata: **2222**.

## 2. Eligibility criteria
**Include (all of):** I1 main subject is how missing data are handled (methodological, comparative/benchmark, simulation, systematic/scoping review, guidance); I2 clinical/health data; I3 addresses imputation, mechanisms/MNAR/sensitivity, missingness indicators/informative presence, deployment-time missingness, uncertainty, fairness, or reporting/risk of bias.

**Exclude:** E1 handling incidental (applied study, routine preprocessing); E2 non-health domain; E3 not a full article (comment, erratum, editorial, letter, no abstract); E4 omics/genomics/single-cell/image-pixel imputation.

## 3. Screening procedure
1. Title screen (rule-based): title contains `missing | imput* | missingness | incomplete data | informative presence | informatively observed`.
2. Abstract screen (rule-based, pre-specified regular expressions; implemented in `screen_rules.py`): E3 publication type/abstract length; E4 omics/imaging terms; E2 no health-setting term; E1 no methodological-evaluation term.
3. Topic tagging of eligible records by keyword rules.
4. Targeted (known-item) retrieval of original method papers and reporting guidelines, each verified by DOI in OpenAlex and PubMed (§6).
5. Selection for synthesis by relevance (priority: systematic reviews, simulation/benchmark studies on clinical data, guidance).

## 4. Flow counts

| Stage | n |
|---|---|
| Records identified (5 queries, union) | 2225 |
| Records retrieved | 2222 |
| Excluded at title screen | 1770 |
| Abstracts screened | 452 |
| Excluded E3 | 4 |
| Excluded E4 | 28 |
| Excluded E2 | 16 |
| Excluded E1 | 23 |
| **Eligible pool** | **381** |

Topic-tag counts (non-exclusive): MI=158, TREE_KNN=44, DEEP_GEN=71, SEQ_TS=115, MNAR_SENS=175, INDICATOR=27, DEPLOY=58, OUTCOME_IN_IMP=1, FAIRNESS=21, REPORTING=18, REVIEW=17


## 5. Studies from the eligible pool cited in the paper

- PMID 37105540 — Sisk R et al. (2023) Imputation and missing indicators for handling missing data in the development and deployment of clinical prediction models: A simulation study. *Stat Methods Med Res*. doi:10.1177/09622802231165001
- PMID 33164082 — Sisk R et al. (2021) Informative presence and observation in routine health data: A review of methodology for clinical risk prediction. *J Am Med Inform Assoc*. doi:10.1093/jamia/ocaa242
- PMID 34520847 — Tsvetanova A et al. (2021) Missing data was handled inconsistently in UK prediction models: a review of method used. *J Clin Epidemiol*. doi:10.1016/j.jclinepi.2021.09.008
- PMID 37316097 — Liu M et al. (2023) Handling missing values in healthcare data: A systematic review of deep learning-based imputation techniques. *Artif Intell Med*. doi:10.1016/j.artmed.2023.102587
- PMID 36823165 — Arnaud E et al. (2023) Predictive models in emergency medicine and their missing data strategies: a systematic review. *NPJ Digit Med*. doi:10.1038/s41746-023-00770-6
- PMID 39635227 — Ren W et al. (2024) Moving Beyond Medical Statistics: A Systematic Review on Missing Data Handling in Electronic Health Records. *Health Data Sci*. doi:10.34133/hds.0176
- PMID 40754039 — Awounvo S et al. (2025) Combining multiple imputation with internal model validation in clinical prediction modeling: a systematic methodological review. *J Clin Epidemiol*. doi:10.1016/j.jclinepi.2025.111916
- PMID 41512677 — Chen W et al. (2026) Real world deployment of a pancreatic cancer risk model: impact of refitting, imputation, and computational burden. *EBioMedicine*. doi:10.1016/j.ebiom.2025.106118
- PMID 34889756 — Singh J et al. (2021) On Missingness Features in Machine Learning Models for Critical Care: Observational Study. *JMIR Med Inform*. doi:10.2196/25022
- PMID 36601036 — Jeanselme V et al. (2022) Imputation Strategies Under Clinical Presence: Impact on Algorithmic Fairness. *Proc Mach Learn Res*. doi:None
- PMID 28068910 — Kontopantelis E et al. (2017) Outcome-sensitive multiple imputation: a simulation study. *BMC Med Res Methodol*. doi:10.1186/s12874-016-0281-5
- PMID 32640992 — Sperrin M et al. (2020) Multiple imputation with missing indicators as proxies for unmeasured variables: simulation study. *BMC Med Res Methodol*. doi:10.1186/s12874-020-01068-x
- PMID 35438796 — Harton J et al. (2022) Informative presence bias in analyses of electronic health records-derived data: a cautionary note. *J Am Med Inform Assoc*. doi:10.1093/jamia/ocac050
- PMID 40217663 — Sim T et al. (2025) Preserving Informative Presence: How Missing Data and Imputation Strategies Affect the Performance of an AI-Based Early Warning Score. *J Clin Med*. doi:10.3390/jcm14072213

## 6. Primary sources added by targeted retrieval

- BRITS: Bidirectional recurrent imputation for time series (2018). Advances in Neural Information Processing Systems (NeurIPS)
- Multiple Imputation and its Application (2013). doi:10.1002/9781119942283
- Recurrent Neural Networks for Multivariate Time Series with Missing Values (2018). doi:10.1038/s41598-018-24271-9
- Missing Data Handling: A Comprehensive Review, Taxonomy, and Comparative Evaluation (2025). doi:10.4236/jcc.2025.136006
- Transparent Reporting of a multivariable prediction model for Individual Prognosis Or Diagnosis (TRIPOD): The TRIPOD Statement (2015). doi:10.7326/m14-0697
- TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods (2024). doi:10.1136/bmj-2023-078378
- Sensitivity analysis for clinical trials with missing continuous outcome data using controlled multiple imputation: A practical guide (2020). doi:10.1002/sim.8569
- SAITS: Self-attention-based imputation for time series (2023). doi:10.1016/j.eswa.2023.119619
- Missing covariate data in clinical research: when and when not to use the missing-indicator method for analysis (2012). doi:10.1503/cmaj.110977
- Multiple imputation in a large-scale complex survey: a practical guide (2010). doi:10.1177/0962280208101273
- Handling missing data in clinical research (2022). doi:10.1016/j.jclinepi.2022.08.016
- Deep Learning Methods for Omics Data Imputation (2023). doi:10.3390/biology12101313
- not-MIWAE: Deep generative modelling with missing not at random data (2021). Int. Conf. Learning Representations (ICLR)
- A comparative study of imputation techniques for missing values in healthcare diagnostic datasets (2025). doi:10.1007/s41060-025-00825-9
- On the consistency of supervised learning with missing values (2019). doi:10.48550/arXiv.1902.06931
- The prevention and handling of the missing data (2013). doi:10.4097/kjae.2013.64.5.402
- What's a good imputation to predict with missing values? (2021). Advances in Neural Information Processing Systems (NeurIPS)
- A Test of Missing Completely at Random for Multivariate Data with Missing Values (1988). doi:10.1080/01621459.1988.10478722
- Statistical Analysis with Missing Data (2019). doi:10.1002/9781119482260
- MIWAE: Deep generative modelling and imputation of incomplete data sets (2019). Proc. 36th Int. Conf. Machine Learning (ICML), PMLR 97
- Using the outcome for imputation of missing predictor values was preferred (2006). doi:10.1016/j.jclinepi.2006.01.009
- PROBAST: A Tool to Assess Risk of Bias and Applicability of Prediction Model Studies: Explanation and Elaboration (2019). doi:10.7326/m18-1377
- Multiple Imputation: A Review of Practical and Theoretical Findings (2018). doi:10.1214/18-STS644
- Missing data is poorly handled and reported in prediction model studies using machine learning: a literature review (2022). doi:10.1016/j.jclinepi.2021.11.023
- The Prevention and Treatment of Missing Data in Clinical Trials (2010). doi:10.17226/12955
- The Prevention and Treatment of Missing Data in Clinical Trials (2012). doi:10.1056/nejmsr1203730
- Benchmarking missing-values approaches for predictive models on health databases (2022). doi:10.1093/gigascience/giac013
- Comparison of missing value imputation tools for machine learning models based on product development cases studies (2025). doi:10.1016/j.lwt.2025.117585
- Inference and missing data (1976). doi:10.1093/biomet/63.3.581
- Multiple Imputation for Nonresponse in Surveys (1987). doi:10.1002/9780470316696
- Multiple Imputation after 18+ Years (1996). doi:10.1080/01621459.1996.10476908
- The impact of imputation quality on machine learning classifiers for datasets with missing values (2023). doi:10.1038/s43856-023-00356-z
- Predicting In-Hospital Mortality of ICU Patients: The PhysioNet/Computing in Cardiology Challenge 2012 (2012). Computing in Cardiology
- Missing data should be handled differently for prediction than for description or causal explanation (2020). doi:10.1016/j.jclinepi.2020.03.028
- MissForest—non-parametric missing value imputation for mixed-type data (2012). doi:10.1093/bioinformatics/btr597
- Multiple imputation for missing data in epidemiological and clinical research: potential and pitfalls (2009). doi:10.1136/bmj.b2393
- Missing value estimation methods for DNA microarrays (2001). doi:10.1093/bioinformatics/17.6.520
- Fully conditional specification in multivariate imputation (2006). doi:10.1080/10629360600810434
- mice: Multivariate imputation by chained equations in {R (2011). doi:10.18637/jss.v045.i03
- Flexible Imputation of Missing Data (2018). doi:10.1201/9780429492259
- The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) Statement: guidelines for reporting observational studies* (2007). doi:10.2471/blt.07.045120
- Deep learning for multivariate time series imputation: A survey (2024). doi:10.48550/arXiv.2402.04059
- Multiple imputation using chained equations: Issues and guidance for practice (2011). doi:10.1002/sim.4067
- PROBAST: A Tool to Assess the Risk of Bias and Applicability of Prediction Model Studies (2019). doi:10.7326/m18-1376
- GAIN: Missing data imputation using generative adversarial nets (2018). Proc. 35th Int. Conf. Machine Learning (ICML), PMLR 80
- Handling missing data with graph representation learning (2020). Advances in Neural Information Processing Systems (NeurIPS)
- Review for handling missing data with special missing mechanism (2024). doi:10.48550/arXiv.2404.04905
