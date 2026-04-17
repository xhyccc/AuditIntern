---
name: casting-check
description: Validates row and column totals in financial spreadsheets. Use when the user asks to verify spreadsheet totals, check arithmetic in a financial table, validate casting, confirm column sums match declared totals, audit a balance sheet for addition errors, or check if subtotals foot correctly in a CSV or Excel file.
---

# Casting Check

## Overview

The **casting check** is a fundamental audit procedure that verifies whether declared row and column totals in a financial spreadsheet are arithmetically correct. It reads a CSV or Excel file, identifies "total" rows (by keywords such as `合计`, `Total`, `小计`, `Subtotal`), computes the sum of each numeric column from the data rows, and compares it against the declared total. Any column where the computed sum differs from the declared total by more than **¥0.01** is reported as a discrepancy.

This skill is fully automated — it requires no configuration beyond the input file path.

---

## OpenCode CLI Invocation

### Via stdin (recommended)

```bash
echo '{
  "intent": "run_casting_check",
  "params": {
    "file_path": "data/balance_sheet.csv",
    "output_path": "results/casting_check_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

```bash
python -m src.cli.main --instruction casting_instruction.json
```

`casting_instruction.json`:
```json
{
  "intent": "run_casting_check",
  "params": {
    "file_path": "data/balance_sheet.xlsx",
    "output_path": "results/casting_check_result.json"
  }
}
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "run_casting_check",
    "params": {
      "file_path": "uploads/balance_sheet.csv",
      "output_path": "results/casting_result.json"
    }
  }'
```

---

## Parameters

| Parameter     | Type   | Required | Default                        | Description                                  |
|---------------|--------|----------|--------------------------------|----------------------------------------------|
| `file_path`   | string | ✅ Yes   | —                              | Path to CSV or Excel (`.xlsx`/`.xls`) file   |
| `output_path` | string | No       | `casting_check_result.json`    | Path to write the JSON result report         |

---

## Input File Format

The input file must have:
- A **first column** whose values may include total-row keywords: `合计`, `Total`, `TOTAL`, `total`, `小计`, `subtotal`, `Subtotal`
- One or more **numeric columns** representing financial amounts

Example CSV:

```
account,Q1,Q2,Q3
Revenue,100000,120000,130000
COGS,60000,70000,80000
合计,160000,190000,210000
```

---

## Output Schema

```json
{
  "status": "ok" | "error",
  "discrepancies": [
    {
      "type": "column_sum",
      "column": "Q1",
      "expected": 160000.0,
      "actual": 160000.0,
      "diff": 0.0
    }
  ],
  "summary": "No discrepancies found."
}
```

| Field           | Description                                                  |
|-----------------|--------------------------------------------------------------|
| `status`        | `"ok"` on success, `"error"` on file load failure           |
| `discrepancies` | List of columns where computed sum ≠ declared total          |
| `summary`       | Human-readable summary of findings                           |

---

## Notes & Edge Cases

- **Tolerance**: differences ≤ 0.01 are ignored (rounding tolerance).
- **Multiple total rows**: only the first declared total value per column is used.
- **No total row**: if no total-row keyword is found, no discrepancy check is performed and an empty list is returned.
- **Mixed data**: non-numeric cells in numeric columns are treated as 0.
- **Supported file types**: `.csv`, `.xlsx`, `.xls`. Other formats return `status: error`.

---

## Script

`scripts/skill_casting_check.py` — `run(file_path: str, output_path: str) -> dict`
