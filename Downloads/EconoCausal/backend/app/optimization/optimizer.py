"""Budget-constrained allocation across customer/discount options."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.optimize import milp, Bounds, LinearConstraint


def optimize_allocations(scenarios: pd.DataFrame, budget: float, discount_levels=(0, 5, 10, 15, 20)) -> dict:
    """Maximize incremental contribution under budget.

    Required columns: customer_id, discount_pct, expected_discount_cost, incremental_profit.
    incremental_profit must already be net of discount cost to avoid double-counting it in the objective.
    """
    required = {"customer_id", "discount_pct", "expected_discount_cost", "incremental_profit"}
    if required - set(scenarios.columns): raise ValueError(f"Missing columns: {sorted(required - set(scenarios.columns))}")
    if budget < 0: raise ValueError("budget must be non-negative")
    if scenarios.empty: return {"status": "empty", "allocations": [], "budget": budget, "discount_cost": 0.0, "remaining_budget": budget, "incremental_profit": 0.0, "roi": None, "feasible": True}
    s = scenarios.copy().reset_index(drop=True)
    if not s.discount_pct.isin(discount_levels).all(): raise ValueError("Scenario contains unsupported discount level")
    if (s.expected_discount_cost < 0).any(): raise ValueError("Discount cost cannot be negative")
    # No-discount option is required for every customer.
    for cid in s.customer_id.unique():
        if not ((s.customer_id == cid) & (s.discount_pct == 0)).any(): raise ValueError(f"Customer {cid} has no 0% baseline option")
    # Keep only positive-value non-baseline offers; baseline is always eligible.
    values = s.incremental_profit.astype(float).to_numpy()
    costs = s.expected_discount_cost.astype(float).to_numpy()
    values = np.where(s.discount_pct.to_numpy() == 0, 0.0, values)
    values = np.where(costs > budget, -1e12, values)
    constraints = []
    constraints.append(LinearConstraint(costs.reshape(1, -1), -np.inf, budget))
    customer_ids = list(s.customer_id.unique())
    matrix = np.zeros((len(customer_ids), len(s)))
    for i, cid in enumerate(customer_ids): matrix[i, np.where(s.customer_id.to_numpy() == cid)[0]] = 1
    constraints.append(LinearConstraint(matrix, 0, 1))
    result = milp(c=-values, integrality=np.ones(len(s)), bounds=Bounds(np.zeros(len(s)), np.ones(len(s))), constraints=constraints,
                  options={"time_limit": 10.0})
    if result.x is None:
        # Transparent fallback: choose best positive profit/cost offers, at most one per customer.
        chosen = []; used = set(); spent = 0.0
        ranked = s.assign(_value=values, _cost=costs).sort_values("_value", ascending=False)
        for idx, row in ranked.iterrows():
            if row._value <= 0 or row.customer_id in used: continue
            if spent + row._cost <= budget:
                chosen.append(idx); used.add(row.customer_id); spent += row._cost
        chosen = set(chosen); status = "greedy_fallback"
    else:
        chosen = set(np.where(result.x > .5)[0].tolist()); status = "optimal" if result.success else "feasible_limit"
    selected = s.loc[sorted(chosen)].copy()
    # MILP may choose any 0% row; include one row per customer by construction.
    spent = float(selected.expected_discount_cost.sum()) if len(selected) else 0.0
    profit = float(selected.loc[selected.discount_pct != 0, "incremental_profit"].sum()) if len(selected) else 0.0
    feasible = spent <= budget + 1e-6 and selected.customer_id.is_unique and selected.discount_pct.isin(discount_levels).all()
    return {"status": status, "allocations": selected.to_dict(orient="records"), "budget": float(budget),
            "discount_cost": spent, "remaining_budget": max(0.0, float(budget - spent)),
            "incremental_profit": profit, "roi": (profit / spent if spent > 0 else None), "feasible": bool(feasible),
            "solver_message": str(result.message) if result.x is not None else "MILP unavailable; greedy fallback used"}
