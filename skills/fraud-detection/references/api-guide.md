# Fraud Detection — API Reference

## Function Signature

```python
from skills.fraud_detection.scripts.skill_fraud_detection import run

result = run(
    file_path="data/journal_entries.csv",
    output_path="results/fraud_detection_result.json"
)
```

## OpenCode CLI — Intent Name

`run_fraud_scan`

## Required Parameters

| Parameter   | Type   | Description                                       |
|-------------|--------|---------------------------------------------------|
| `file_path` | string | Path to CSV file with journal entries             |

## Optional Parameters

| Parameter     | Type   | Default                       | Description           |
|---------------|--------|-------------------------------|-----------------------|
| `output_path` | string | `fraud_detection_result.json` | JSON output file path |

## Column Detection (case-insensitive)

| Internal Name | Matched If Column Contains |
|---------------|---------------------------|
| `date_col`    | `date` or `日期`          |
| `desc_col`    | `desc`, `description`, `摘要`, `备注` |
| `amount_col`  | `amount` or `金额`        |

## Sensitive Keywords

```python
SENSITIVE_KEYWORDS = ["好处费", "冲销", "暂估", "调节", "kickback", "reverse", "adjust"]
```

## Benford's Law Critical Value

- Distribution: χ² with 8 degrees of freedom
- Significance level: p = 0.05
- Critical value: **15.507** (hardcoded)
- If `chi_square > 15.507` → `conforming: false`

## Dependencies

| Package         | Purpose                              |
|-----------------|--------------------------------------|
| `pandas`        | CSV reading and row iteration        |
| `numpy`         | Numeric operations                   |
| `scipy`         | p-value calculation (optional)       |
