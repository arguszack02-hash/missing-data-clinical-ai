#!/usr/bin/env python3
"""Re-run the PubMed search logged in search_log.md (executed 2026-10-05).

PubMed is updated continuously, so a re-run returns slightly different counts; the record set
used in the paper is pubmed_records_screened.csv.
Usage: python fetch_pubmed.py [--email you@example.org]   -> pubmed_records_rerun.csv
"""
import sys, time, argparse, xml.etree.ElementTree as ET
import requests, pandas as pd

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
MINDATE, MAXDATE = "2015/01/01", "2026/09/30"
QUERIES = {
    'Q1_ml_imputation_clinical': '(imputation[tiab] OR "missing data"[tiab] OR "missing values"[tiab]) AND ("electronic health record*"[tiab] OR "electronic medical record*"[tiab] OR EHR[tiab] OR clinical[tiab] OR "intensive care"[tiab]) AND ("deep learning"[tiab] OR "machine learning"[tiab] OR "neural network*"[tiab] OR generative[tiab] OR transformer*[tiab] OR autoencoder*[tiab])',  # 1408 hits on 2026-10-05
    'Q2_MI_prediction_models': '"multiple imputation"[tiab] AND ("prediction model*"[tiab] OR "prognostic model*"[tiab] OR "risk prediction"[tiab] OR "clinical prediction"[tiab])',  # 339 hits on 2026-10-05
    'Q3_MNAR_informative': '("missing not at random"[tiab] OR MNAR[tiab] OR "informative missingness"[tiab] OR "informative presence"[tiab] OR "informatively missing"[tiab]) AND (clinical[tiab] OR health*[tiab] OR patient*[tiab] OR "electronic health record*"[tiab])',  # 291 hits on 2026-10-05
    'Q4_missing_indicator_deployment': '("missing indicator*"[tiab] OR "missingness indicator*"[tiab] OR "missing-indicator"[tiab] OR ("missing data"[tiab] AND (deployment[tiab] OR "real-time"[tiab] OR "at prediction time"[tiab]))) AND (prediction[tiab] OR predictive[tiab] OR model*[tiab])',  # 231 hits on 2026-10-05
    'Q5_reporting_guidance': '("missing data"[tiab] OR imputation[tiab]) AND (TRIPOD[tiab] OR PROBAST[tiab] OR STROBE[tiab] OR "reporting guideline*"[tiab] OR "reporting quality"[tiab] OR "risk of bias"[tiab]) AND (prediction[tiab] OR "machine learning"[tiab] OR "artificial intelligence"[tiab])',  # 208 hits on 2026-10-05
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--email", default=None); a = ap.parse_args()
    base = dict(db="pubmed", tool="missing-data-review")
    if a.email: base["email"] = a.email
    ids = {}
    for k, q in QUERIES.items():
        r = requests.get(E + "esearch.fcgi", params={**base, "term": q, "datetype": "pdat", "mindate": MINDATE,
                         "maxdate": MAXDATE, "retmax": 10000, "retmode": "json"}, timeout=60).json()
        ids[k] = set(r["esearchresult"]["idlist"]); print(k, len(ids[k])); time.sleep(0.4)
    allids = sorted(set().union(*ids.values())); print("union", len(allids))
    recs = []
    for i in range(0, len(allids), 200):
        x = requests.post(E + "efetch.fcgi", data={**base, "id": ",".join(allids[i:i+200]), "retmode": "xml"}, timeout=120).text
        for art in ET.fromstring(x).findall(".//PubmedArticle"):
            pmid = art.findtext(".//PMID")
            t = "".join(art.find(".//ArticleTitle").itertext()) if art.find(".//ArticleTitle") is not None else ""
            ab = " ".join("".join(e.itertext()) for e in art.findall(".//AbstractText"))
            yr = art.findtext(".//PubDate/Year") or (art.findtext(".//PubDate/MedlineDate") or "")[:4]
            j = art.findtext(".//Journal/ISOAbbreviation") or art.findtext(".//Journal/Title")
            doi = next((aid.text for aid in art.findall(".//ArticleId") if aid.get("IdType") == "doi"), None)
            pt = [p.text for p in art.findall(".//PublicationType")]
            au = [(x.findtext("LastName") or "") + " " + (x.findtext("Initials") or "") for x in art.findall(".//Author")]
            recs.append(dict(pmid=pmid, title=t, abstract=ab, year=yr, journal=j, doi=doi, pubtypes=";".join(pt), authors="; ".join(au)))
        time.sleep(0.4)
    df = pd.DataFrame(recs)
    df["queries"] = df.pmid.map(lambda p: ";".join(k for k, v in ids.items() if p in v))
    df.to_csv("pubmed_records_rerun.csv", index=False); print("retrieved", len(df))

if __name__ == "__main__":
    main()
