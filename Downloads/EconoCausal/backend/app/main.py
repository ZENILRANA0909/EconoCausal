from __future__ import annotations
from pathlib import Path
import io
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from app.data.generator import generate_customers
from app.data.validation import validate_dataset
from app.optimization.optimizer import optimize_allocations
from app.monitoring.drift import evaluate_drift

app = FastAPI(title="EconoCausal AI API", version="0.1.0", description="Causal marketing analysis and budget-constrained discount optimization.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
STATE = {"dataset": None, "eval_truth": None, "reference": None, "model_ready": False}

class GenerateRequest(BaseModel):
    n: int = Field(default=10_000, ge=200, le=100_000)
    seed: int = Field(default=42, ge=0)
class OptimizeRequest(BaseModel):
    budget: float = Field(ge=0)
    discount_levels: list[int] = Field(default_factory=lambda: [0,5,10,15,20])

@app.on_event("startup")
def startup():
    data, truth = generate_customers(10_000, 42)
    STATE["dataset"] = data; STATE["eval_truth"] = truth; STATE["reference"] = data.copy()

@app.get("/api/v1/health")
def health():
    return {"status":"healthy", "service":"EconoCausal AI API", "version":"0.1.0", "dataset_loaded":STATE["dataset"] is not None, "causal_model_ready":STATE["model_ready"]}

@app.get("/api/v1/dataset/summary")
def dataset_summary():
    df=STATE["dataset"]
    if df is None: raise HTTPException(503,"No dataset loaded")
    report=validate_dataset(df)
    return {**report, "synthetic":True, "purchase_rate":float(df.purchase.mean()), "mean_income":float(df.income.mean()),
            "mean_aov":float(df.historical_aov.mean()), "segment_counts":df.customer_segment.value_counts().to_dict(),
            "treatment_rate":float((df.discount_received>=10).mean())}

@app.post("/api/v1/dataset/generate")
def dataset_generate(req: GenerateRequest):
    try: data, truth = generate_customers(req.n, req.seed)
    except ValueError as e: raise HTTPException(400,str(e))
    STATE["dataset"]=data; STATE["eval_truth"]=truth; STATE["reference"]=data.copy(); STATE["model_ready"]=False
    return {"message":"Synthetic dataset generated", "seed":req.seed, "summary":validate_dataset(data), "synthetic":True}

@app.post("/api/v1/dataset/upload")
async def dataset_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Upload a .csv file")
    raw=await file.read()
    if len(raw)>10*1024*1024: raise HTTPException(413,"CSV must be 10 MB or smaller")
    try: df=pd.read_csv(io.BytesIO(raw))
    except Exception as e: raise HTTPException(400,f"Unable to parse CSV: {e}")
    report=validate_dataset(df)
    if not report["valid"]: raise HTTPException(400,{"message":"Dataset validation failed","report":report})
    STATE["dataset"]=df; STATE["model_ready"]=False
    return {"message":"Dataset uploaded", "summary":report, "synthetic":False}

@app.get("/api/v1/causal/graph")
def causal_graph():
    return {"treatment":"discount_received >= 10%", "outcome":"purchase", "confounders":["age","income","previous_purchases","website_visits","customer_segment","historical_aov"],
            "edges":[["age","discount_received"],["income","discount_received"],["previous_purchases","discount_received"],["website_visits","discount_received"],["discount_received","purchase"],["age","purchase"],["income","purchase"],["previous_purchases","purchase"],["website_visits","purchase"]],
            "assumptions":["Conditional exchangeability given observed pre-treatment covariates","Positivity/overlap","Consistency and a well-defined treatment","No unmeasured confounding is an assumption, not a verified fact"],
            "note":"Graph description is available. EconML/DoWhy model fitting is unavailable until optional causal dependencies are installed and the estimator workflow is implemented."}

@app.get("/api/v1/customers")
def customers(limit:int=50, offset:int=0, segment:str|None=None, search:str|None=None):
    if limit<1 or limit>500 or offset<0: raise HTTPException(400,"limit must be 1-500 and offset non-negative")
    df=STATE["dataset"]
    if df is None: raise HTTPException(503,"No dataset loaded")
    if segment: df=df[df.customer_segment==segment]
    if search: df=df[df.customer_id.str.contains(search,case=False,regex=False)]
    return {"total":int(len(df)),"limit":limit,"offset":offset,"items":df.iloc[offset:offset+limit].to_dict(orient="records")}

@app.get("/api/v1/customers/{customer_id}")
def customer_detail(customer_id:str):
    df=STATE["dataset"]
    if df is None: raise HTTPException(503,"No dataset loaded")
    rows=df[df.customer_id==customer_id]
    if rows.empty: raise HTTPException(404,"Customer not found")
    return rows.iloc[0].to_dict()

@app.post("/api/v1/optimization/run")
def run_optimization(req:OptimizeRequest):
    if STATE["dataset"] is None: raise HTTPException(503,"No dataset loaded")
    df=STATE["dataset"].head(2000).copy()
    levels=sorted(set(req.discount_levels)|{0})
    if any(x not in [0,5,10,15,20] for x in levels): raise HTTPException(400,"Discount levels must be selected from 0, 5, 10, 15, 20")
    rows=[]
    # Transparent baseline scenario engine: a simple, explicitly non-causal heuristic used until DML is fitted.
    # This endpoint labels output as illustrative rather than presenting it as a causal estimate.
    for _,r in df.iterrows():
        baseline=float(r.historical_aov)*.42*float(r.purchase)
        for d in levels:
            expected_purchase=float(1/(1+__import__('math').exp(-(-1.45+.12*r.previous_purchases+.055*r.website_visits+.000009*(r.income-45000)-.012*abs(r.age-38)+(.05 if d else 0)))))
            expected_margin=expected_purchase*(float(r.historical_aov)*.42-float(r.historical_aov)*d/100)
            cost=expected_purchase*float(r.historical_aov)*d/100
            rows.append({"customer_id":r.customer_id,"discount_pct":d,"expected_discount_cost":max(0,cost),"incremental_profit":float(expected_margin-baseline-cost) if d else 0.0,
                         "expected_purchase_probability":expected_purchase})
    try: result=optimize_allocations(pd.DataFrame(rows),req.budget,levels)
    except ValueError as e: raise HTTPException(400,str(e))
    result["warning"]="Illustrative heuristic only: DML causal model has not been trained. Do not interpret this allocation as validated causal advice."
    result["customers_evaluated"]=len(df)
    return result

@app.post("/api/v1/drift/evaluate")
async def drift_evaluate(file:UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'): raise HTTPException(400,"Upload a .csv file")
    try: current=pd.read_csv(io.BytesIO(await file.read()))
    except Exception as e: raise HTTPException(400,f"Unable to parse CSV: {e}")
    ref=STATE["reference"]
    if ref is None: return {"available":False,"status":"no_evaluation","message":"Reference dataset unavailable","features":[]}
    return evaluate_drift(ref,current)

@app.get("/api/v1/drift/status")
def drift_status():
    return {"available":False,"status":"no_evaluation","message":"Upload a current CSV to evaluate drift; no drift result is fabricated."}

@app.get("/api/v1/metrics")
def metrics():
    df=STATE["dataset"]
    if df is None: raise HTTPException(503,"No dataset loaded")
    return {"synthetic":True,"customers":len(df),"purchase_rate":float(df.purchase.mean()),"treatment_rate":float((df.discount_received>=10).mean()),
            "mean_contribution_margin":float(df.contribution_margin.mean()),"causal_model_ready":False,
            "note":"Causal ATE, uplift and Qini metrics are unavailable until the EconML/DoWhy estimator is implemented and trained."}
