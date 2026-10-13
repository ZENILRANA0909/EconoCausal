# EconoCausal methodology (initial foundation)

## Treatment and outcome
The planned primary contrast is a discount of at least 10% versus no discount. The primary causal outcome is purchase (binary). Contribution margin and expected discount expenditure are separate business quantities for the optimizer.

## Synthetic data generating process
Treatment assignment depends on observed age, income, previous purchases, and website visits, creating observable confounding with overlap. Customer response varies by observed characteristics and includes heterogeneous/negative effects. The generated `true_cate` and true propensity fields are written to a separate evaluation-only artifact and are not columns in the modeling dataset.

## Identification assumptions to evaluate
- Conditional exchangeability given observed pre-treatment covariates.
- Positivity/common support.
- Consistency and well-defined treatment.
- No unmeasured confounding (assumption, not established by a graph or refutation test).

## Implementation status
Data generation, schema validation, initial API, drift tests, and a constrained assignment primitive are implemented. The EconML/DoWhy estimator and causal refutation workflow remain pending. The currently exposed optimization route is explicitly illustrative and must not be described as a validated causal recommendation.
