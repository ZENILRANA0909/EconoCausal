# EconoCausal AI

**Dynamic Pricing via Double Machine Learning** — an internship/portfolio project aligned with the Infotact Advanced Data Science & ML Engineering project brief.

> Current status: foundation implementation. Synthetic data, schema validation, initial FastAPI endpoints, an illustrative budget allocator, drift checks, and a first React dashboard are present. The actual EconML `LinearDML` + DoWhy estimation/refutation pipeline is **not yet implemented**; the UI and API disclose that status. Optimization currently uses an illustrative heuristic scenario engine, not validated causal estimates.

## Architecture
- `backend/`: FastAPI, reproducible synthetic data, schema/quality validation, optimization, drift monitoring, tests.
- `frontend/`: React + TypeScript + Vite dashboard using live API data.
- `data/generated/`: generated CSV files.
- `docs/`: methodology and implementation notes.

## Requirements
- Python 3.11 recommended by the specification (the current build container was inspected with Python 3.13.5).
- Node.js 20+ and npm.

## Run locally

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Open API docs at `http://localhost:8000/docs`.

Generate a dataset independently:
```bash
python -m app.data.generator --n 10000 --seed 42 --out ../data/generated
```

### Frontend
In another terminal:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`. Configure `VITE_API_BASE_URL` if the API is hosted elsewhere; default is `http://localhost:8000/api/v1`.

### Tests
```bash
cd backend
python -m pytest -q
```

## Current endpoints
- `GET /api/v1/health`
- `GET /api/v1/dataset/summary`
- `POST /api/v1/dataset/generate`
- `POST /api/v1/dataset/upload`
- `GET /api/v1/causal/graph`
- `GET /api/v1/customers?limit=50&offset=0`
- `GET /api/v1/customers/{customer_id}`
- `POST /api/v1/optimization/run`
- `POST /api/v1/drift/evaluate` (CSV upload)
- `GET /api/v1/drift/status`
- `GET /api/v1/metrics`

## Data and causal limitations
The generator creates treatment assignment that depends on observed customer features and keeps evaluation-only synthetic ground truth in a separate file. Ground truth must never be used as a model input. Observational causal inference requires assumptions such as conditional exchangeability, positivity, and consistency; diagnostics do not prove these assumptions. All current generated data and heuristic scenario results are simulated and must not be used to make real marketing or financial decisions.

## Roadmap
1. Complete EconML `LinearDML`, DoWhy identification and compatible refutation methods.
2. Add propensity-score balance diagnostics, confidence intervals, and out-of-sample uplift/Qini evaluation.
3. Replace the illustrative scenario engine with properly estimated counterfactual outcomes and a validated profit formulation.
4. Complete API integration tests and production hardening.
5. Finish dashboard pages, persistence, deployment configs, and model/report documentation.
