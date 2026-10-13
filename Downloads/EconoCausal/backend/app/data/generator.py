"""Reproducible synthetic customer/campaign data for EconoCausal."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd


def generate_customers(n: int = 10_000, seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    if n < 200:
        raise ValueError("n must be at least 200 to provide meaningful treatment/control samples")
    rng = np.random.default_rng(seed)
    age = rng.integers(18, 76, n)
    income = np.clip(rng.lognormal(np.log(48_000), .45, n), 12_000, 250_000).round(2)
    previous = np.clip(rng.poisson(4, n), 0, 30)
    visits = np.clip(rng.poisson(7, n), 0, 60)
    segment = np.select([previous >= 7, income >= 75_000], ["loyal", "premium"], default="standard")
    aov = np.clip(rng.normal(1_800 + income * .004, 450, n), 250, 12_000).round(2)
    # Treatment assignment depends on observed pre-treatment characteristics (confounding),
    # while clipping probabilities keeps overlap between treatment arms.
    logit = -0.35 + 0.018 * (age - 40) - 0.000006 * (income - 48_000) + .10 * previous + .035 * visits
    propensity = np.clip(1 / (1 + np.exp(-logit)), .12, .88)
    treated = rng.binomial(1, propensity, n)
    # Heterogeneous response; negative effects are possible for a subset of customers.
    cate = .045 + .009 * np.minimum(previous, 10) + .0012 * np.minimum(visits, 20) - .0000012 * income
    cate -= .11 * ((previous <= 1) & (visits <= 3))  # sleeping-dog/lost-cause behavior
    cate = np.clip(cate, -.12, .22)
    baseline_logit = -1.45 + .12 * previous + .055 * visits + .000009 * (income - 45_000) - .012 * abs(age - 38)
    p0 = np.clip(1 / (1 + np.exp(-baseline_logit)), .02, .95)
    # Convert additive uplift to a probability under treatment; clip to valid probability range.
    p1 = np.clip(p0 + cate, .01, .98)
    purchase_prob = np.where(treated == 1, p1, p0)
    purchase = rng.binomial(1, purchase_prob)
    discount = np.where(treated == 1, 10.0, 0.0)
    order_value = np.where(purchase == 1, aov * (1 - discount / 100) * rng.uniform(.85, 1.15, n), 0).round(2)
    # Approximate contribution margin after COGS; discount cost is accounted for separately in optimization.
    contribution = np.where(purchase == 1, (aov * .42) - (aov * discount / 100), 0).round(2)
    dates = pd.to_datetime("2026-01-01") + pd.to_timedelta(rng.integers(0, 270, n), unit="D")
    frame = pd.DataFrame({
        "customer_id": [f"C{i:06d}" for i in range(1, n + 1)], "age": age, "income": income,
        "previous_purchases": previous, "website_visits": visits, "customer_segment": segment,
        "historical_aov": aov, "campaign_id": rng.integers(1, 9, n).astype(str),
        "discount_received": discount, "purchase": purchase, "order_value": order_value,
        "contribution_margin": contribution, "campaign_date": dates.strftime("%Y-%m-%d")
    })
    eval_only = pd.DataFrame({"customer_id": frame.customer_id, "propensity_true": propensity.round(6),
                              "true_cate": cate.round(6), "purchase_probability_no_discount": p0.round(6),
                              "purchase_probability_discount": p1.round(6)})
    return frame, eval_only


def save_dataset(out_dir: str | Path, n: int = 10_000, seed: int = 42) -> tuple[Path, Path]:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    data, truth = generate_customers(n, seed)
    data_path, truth_path = out / "customers.csv", out / "synthetic_eval_truth.csv"
    data.to_csv(data_path, index=False); truth.to_csv(truth_path, index=False)
    return data_path, truth_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate reproducible EconoCausal synthetic data")
    parser.add_argument("--n", type=int, default=10_000); parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="data/generated")
    args = parser.parse_args(); paths = save_dataset(args.out, args.n, args.seed)
    print(f"Generated dataset: {paths[0]}\nEvaluation-only truth: {paths[1]}")
