"""Simple reference-vs-current feature drift checks."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency


def _psi(reference, current, bins=10):
    ref = np.asarray(reference, dtype=float); cur = np.asarray(current, dtype=float)
    ref = ref[np.isfinite(ref)]; cur = cur[np.isfinite(cur)]
    if len(ref) == 0 or len(cur) == 0: return None
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3: return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    rp = np.histogram(ref, bins=edges)[0] / len(ref); cp = np.histogram(cur, bins=edges)[0] / len(cur)
    rp = np.clip(rp, 1e-6, None); cp = np.clip(cp, 1e-6, None)
    return float(np.sum((cp - rp) * np.log(cp / rp)))


def evaluate_drift(reference: pd.DataFrame, current: pd.DataFrame, numeric=None, categorical=None, psi_threshold=.2, p_threshold=.05) -> dict:
    if reference.empty or current.empty:
        return {"available": False, "status": "no_evaluation", "message": "Reference and current datasets are both required", "features": []}
    numeric = numeric or [c for c in reference.select_dtypes(include=np.number).columns if c in current.columns]
    categorical = categorical or [c for c in reference.select_dtypes(exclude=np.number).columns if c in current.columns]
    results=[]
    for col in numeric:
        if col not in reference or col not in current: continue
        a=pd.to_numeric(reference[col], errors="coerce").dropna(); b=pd.to_numeric(current[col], errors="coerce").dropna()
        if a.empty or b.empty: continue
        ks=ks_2samp(a, b)
        psi=_psi(a, b)
        results.append({"feature": col, "type":"numeric", "psi":psi, "ks_statistic":float(ks.statistic), "p_value":float(ks.pvalue),
                        "drift": bool((psi is not None and psi >= psi_threshold) or ks.pvalue < p_threshold), "reference_n":len(a), "current_n":len(b)})
    for col in categorical:
        if col not in reference or col not in current: continue
        a=reference[col].fillna("<MISSING>").astype(str); b=current[col].fillna("<MISSING>").astype(str)
        levels=sorted(set(a)|set(b))
        if len(levels)<2: p=1.0
        else:
            table=np.array([[int((a==x).sum()), int((b==x).sum())] for x in levels]).T
            try: p=float(chi2_contingency(table)[1])
            except ValueError: p=1.0
        results.append({"feature":col,"type":"categorical","p_value":p,"drift":bool(p < p_threshold),"reference_n":len(a),"current_n":len(b)})
    return {"available": True, "status": "warning" if any(x["drift"] for x in results) else "stable",
            "reference_rows":len(reference), "current_rows":len(current), "features":results,
            "thresholds":{"psi":psi_threshold,"p_value":p_threshold}, "note":"Statistical drift is not necessarily practically meaningful."}
