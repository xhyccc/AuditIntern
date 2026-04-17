# Analytical Review — API Reference

## Function Signature

```python
from skills.analytical_review.scripts.skill_analytical_review import run

result = run(
    current_file="data/trial_balance_2024.csv",
    prior_file="data/trial_balance_2023.csv",
    output_path="results/analytical_review_result.json",
    threshold_pct=15.0,
    threshold_amount=500000
)
```

## OpenCode CLI — Intent Name

`run_analytical_review`

## Required Parameters

| Parameter      | Type   | Description                                           |
|----------------|--------|-------------------------------------------------------|
| `current_file` | string | Path to current period CSV or Excel trial balance    |
| `prior_file`   | string | Path to prior period CSV or Excel trial balance      |

## Optional Parameters

| Parameter          | Type   | Default                          | Description                                |
|--------------------|--------|----------------------------------|--------------------------------------------|
| `output_path`      | string | `analytical_review_result.json`  | JSON output file path                      |
| `threshold_pct`    | float  | `15.0`                           | Percentage change threshold (%)            |
| `threshold_amount` | float  | `500000`                         | Absolute change threshold (currency units) |

## Column Detection

| Column Type | Detection Logic                                                      |
|-------------|----------------------------------------------------------------------|
| Account     | First column containing `account` or `科目` (case-insensitive), else column 0 |
| Amount      | First column containing `amount` or `金额` (case-insensitive), else column 1 |

## Merge Behavior

Files are outer-joined on the account column. Missing accounts in either period appear with balance = 0.

## Change Percentage Formula

```
change_pct = (current - prior) / |prior| * 100   (when prior ≠ 0)
change_pct = 100.0                                 (when prior = 0 and current ≠ 0)
change_pct = 0.0                                   (when both = 0)
```

## Flagging Condition

An account is flagged if:
```
|change_pct| ≥ threshold_pct  OR  |change_amount| ≥ threshold_amount
```

## Dependencies

| Package  | Purpose                    |
|----------|----------------------------|
| `pandas` | File reading, merge, pivot |
| `numpy`  | Numeric operations         |
