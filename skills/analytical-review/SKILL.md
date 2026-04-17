---
name: analytical-review
description: Compares current vs prior period financial balances and flags significant variances. Use when the user asks to perform analytical review, compare financial periods, identify accounts with large changes, flag variances above a percentage or amount threshold, analyze year-over-year movements, or produce a variance analysis narrative from two trial balance CSV or Excel files.
---

# Analytical Review

## Overview

The **analytical review** skill performs one of the most common substantive audit procedures: comparing current-period account balances against prior-period figures and flagging accounts with unexpectedly large changes. It merges two financial files on the account column, computes both the **absolute change** and **percentage change** for every account, and flags any account that exceeds either a percentage threshold or an absolute amount threshold.

The output includes a structured list of flagged accounts and an auto-generated narrative summary suitable for inclusion in an audit work paper.

**Default thresholds**: flag accounts with ≥ 15% change OR ≥ ¥500,000 absolute change. Both thresholds are configurable.

---

## OpenCode CLI Invocation

### Basic usage (default thresholds)

```bash
echo '{
  "intent": "run_analytical_review",
  "params": {
    "current_file": "data/trial_balance_2024.csv",
    "prior_file": "data/trial_balance_2023.csv",
    "output_path": "results/analytical_review_result.json"
  }
}' | python -m src.cli.main
```

### Custom thresholds

```bash
echo '{
  "intent": "run_analytical_review",
  "params": {
    "current_file": "data/tb_2024.xlsx",
    "prior_file": "data/tb_2023.xlsx",
    "output_path": "results/analytical_review_result.json",
    "threshold_pct": 10.0,
    "threshold_amount": 200000
  }
}' | python -m src.cli.main
```

### Via instruction file

`ar_instruction.json`:
```json
{
  "intent": "run_analytical_review",
  "params": {
    "current_file": "data/trial_balance_2024.csv",
    "prior_file": "data/trial_balance_2023.csv",
    "output_path": "results/analytical_review_result.json",
    "threshold_pct": 15.0,
    "threshold_amount": 500000
  }
}
```

```bash
python -m src.cli.main --instruction ar_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d @ar_instruction.json
```

---

## Parameters

| Parameter          | Type   | Required | Default                              | Description                                          |
|--------------------|--------|----------|--------------------------------------|------------------------------------------------------|
| `current_file`     | string | ✅ Yes   | —                                    | Current period CSV or Excel (must have account + amount columns) |
| `prior_file`       | string | ✅ Yes   | —                                    | Prior period CSV or Excel (same column requirement)  |
| `output_path`      | string | No       | `analytical_review_result.json`      | Path to write the JSON result report                 |
| `threshold_pct`    | float  | No       | `15.0`                               | Percentage change threshold for flagging             |
| `threshold_amount` | float  | No       | `500000`                             | Absolute change threshold (in local currency)        |

---

## Input File Format

Both files must contain:
- An **account column**: auto-detected by matching `account` (case-insensitive) or `科目` in the column name. Falls back to the first column.
- An **amount column**: auto-detected by matching `amount` (case-insensitive) or `金额`. Falls back to the second column.

Example CSV:
```
account,amount
Cash and Equivalents,1500000
Accounts Receivable,3200000
Inventory,850000
Fixed Assets,12000000
```

---

## Output Schema

```json
{
  "status": "ok",
  "flagged_accounts": [
    {
      "account": "Accounts Receivable",
      "current": 3200000.0,
      "prior": 1800000.0,
      "change_pct": 77.78,
      "change_amount": 1400000.0
    },
    {
      "account": "Inventory",
      "current": 850000.0,
      "prior": 1200000.0,
      "change_pct": -29.17,
      "change_amount": -350000.0
    }
  ],
  "narrative": "Analytical review identified 2 account(s) with significant variances (threshold: 15.0% or ¥500,000)."
}
```

| Field              | Description                                                              |
|--------------------|--------------------------------------------------------------------------|
| `status`           | `"ok"` on success, `"error"` on file load failure                       |
| `flagged_accounts` | Accounts exceeding either threshold                                      |
| `account`          | Account name                                                             |
| `current`          | Current period balance (rounded to 2 decimal places)                    |
| `prior`            | Prior period balance                                                     |
| `change_pct`       | Percentage change [(current−prior) / |prior|] × 100                    |
| `change_amount`    | Absolute change (current − prior)                                        |
| `narrative`        | Auto-generated work paper narrative                                      |

---

## Flagging Logic

An account is flagged if **either** condition is met:
```
|change_pct| ≥ threshold_pct   OR   |change_amount| ≥ threshold_amount
```

For accounts with zero prior balance: `change_pct` is 100% if current ≠ 0, else 0%.

Accounts not present in one period appear with a balance of 0 for that period (outer join).

---

## Notes & Edge Cases

- **New accounts**: accounts in current but not prior period appear with `prior = 0` and `change_pct = 100%`.
- **Closed accounts**: accounts in prior but not current period appear with `current = 0` and a 100% decrease.
- **Currency**: all amounts are assumed to be in the same currency. No conversion is applied.
- **Negative amounts**: credit-balance accounts with negative values are handled correctly (liabilities, revenue).

---

## Script

`scripts/skill_analytical_review.py` — `run(current_file, prior_file, output_path, threshold_pct, threshold_amount) -> dict`
