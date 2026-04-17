# Cross Reference Check — API Reference

## Function Signature

```python
from skills.cross_reference_check.scripts.skill_cross_reference_check import run

result = run(
    rules_file="data/cross_ref_rules.json",
    data_files={"income_stmt": "data/income_statement.csv", "tb": "data/trial_balance.csv"},
    output_path="results/cross_reference_result.json"
)
```

## OpenCode CLI — Intent Name

`run_cross_reference`

## Required Parameters

| Parameter    | Type           | Description                                          |
|--------------|----------------|------------------------------------------------------|
| `rules_file` | string         | Path to JSON array of comparison rules               |
| `data_files` | dict[str, str] | Map of file keys to file paths (CSV or Excel)        |

## Optional Parameters

| Parameter     | Type   | Default                        | Description           |
|---------------|--------|--------------------------------|-----------------------|
| `output_path` | string | `cross_reference_result.json`  | JSON output file path |

## Rules JSON Schema

```json
[
  {
    "name": "string — human-readable rule name",
    "file_a": "string — key in data_files",
    "field_a": "string — column name in file_a (case-insensitive)",
    "file_b": "string — key in data_files",
    "field_b": "string — column name in file_b (case-insensitive)"
  }
]
```

## Column Matching

Column names are matched with `.strip().lower()` on both sides, so `"Revenue"`, `"revenue"`, `" Revenue "` all match `"revenue"` in the rules file.

## Sum Semantics

The skill sums ALL rows in the specified column using `pd.to_numeric(errors='coerce').dropna().sum()`. Non-numeric values are excluded from the sum.

## Dependencies

| Package  | Purpose          |
|----------|------------------|
| `pandas` | File reading     |
