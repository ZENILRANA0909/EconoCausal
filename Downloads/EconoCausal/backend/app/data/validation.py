"""Dataset schema and quality validation."""
from __future__ import annotations
import pandas as pd

REQUIRED = {"customer_id", "age", "income", "previous_purchases", "website_visits", "customer_segment",
            "historical_aov", "campaign_id", "discount_received", "purchase", "order_value",
            "contribution_margin", "campaign_date"}
NUMERIC_RANGES = {"age": (18, 120), "income": (0, 10_000_000), "previous_purchases": (0, 10000),
                  "website_visits": (0, 100000), "historical_aov": (0, 10_000_000),
                  "discount_received": (0, 100), "purchase": (0, 1), "order_value": (0, 10_000_000)}


def validate_dataset(df: pd.DataFrame) -> dict:
    missing_cols = sorted(REQUIRED - set(df.columns))
    if missing_cols:
        return {"valid": False, "errors": [f"Missing required columns: {', '.join(missing_cols)}"], "rows": len(df)}
    errors = []
    if df.empty: errors.append("Dataset is empty")
    if df.customer_id.isna().any(): errors.append("customer_id contains missing values")
    if df.customer_id.duplicated().any(): errors.append("customer_id contains duplicates")
    missing_values = {str(k): int(v) for k, v in df[list(REQUIRED)].isna().sum().items() if v}
    for col, (lo, hi) in NUMERIC_RANGES.items():
        vals = pd.to_numeric(df[col], errors="coerce")
        if vals.isna().any(): errors.append(f"{col} contains non-numeric or missing values")
        elif ((vals < lo) | (vals > hi)).any(): errors.append(f"{col} values must be between {lo} and {hi}")
    if not df["purchase"].dropna().isin([0, 1]).all(): errors.append("purchase must be binary (0 or 1)")
    if not df["discount_received"].dropna().isin([0, 5, 10, 15, 20]).all(): errors.append("discount_received must use supported levels: 0, 5, 10, 15, 20")
    return {"valid": not errors, "errors": errors, "rows": int(len(df)), "columns": int(len(df.columns)),
            "duplicate_customer_ids": int(df.customer_id.duplicated().sum()), "missing_values": missing_values,
            "treatment_count": int((df.discount_received >= 10).sum()),
            "control_count": int((df.discount_received == 0).sum()),
            "discount_levels": sorted(df.discount_received.dropna().unique().tolist())}
