# Casting Check — API Reference

## Function Signature

```python
from skills.casting_check.scripts.skill_casting_check import run

result = run(
    file_path="data/balance_sheet.csv",
    output_path="results/casting_check_result.json"
)
```

## Python Direct Call

```python
import sys
sys.path.insert(0, ".")
from skills.casting_check.scripts import skill_casting_check

result = skill_casting_check.run(
    file_path="data/balance_sheet.csv",
    output_path="results/casting_check_result.json"
)
print(result["summary"])
```

## OpenCode CLI — Intent Name

`run_casting_check`

## Required Parameters

| Parameter   | Type   | Description                               |
|-------------|--------|-------------------------------------------|
| `file_path` | string | Path to CSV or Excel financial statement  |

## Optional Parameters

| Parameter     | Type   | Default                      | Description             |
|---------------|--------|------------------------------|-------------------------|
| `output_path` | string | `casting_check_result.json`  | JSON output file path   |

## Total Row Detection

The first column is scanned for any of these values (exact match):

```python
TOTAL_KEYWORDS = {"合计", "Total", "TOTAL", "total", "小计", "subtotal", "Subtotal"}
```

Rows matching these keywords are treated as declared totals and excluded from the sum computation.

## Error Response

```json
{
  "status": "error",
  "discrepancies": [],
  "summary": "<exception message>"
}
```

Errors occur when the file cannot be read (wrong path, unsupported format, permission denied).

## Dependencies

| Package  | Purpose                         |
|----------|---------------------------------|
| `pandas` | CSV/Excel reading and DataFrame |
| `numpy`  | Numeric operations              |
