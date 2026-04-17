---
name: fraud-detection
description: Analyzes journal entries for fraud indicators using rule-based checks and Benford's Law. Use when the user asks to detect fraud, scan for suspicious transactions, check for weekend postings, flag round-number amounts, identify sensitive keywords in journal descriptions, test Benford's Law on financial data, or assess fraud risk in a journal entry CSV file.
---

# Fraud Detection

## Overview

The **fraud detection** skill applies a multi-layer analytical approach to a CSV file of journal entries to identify transactions that warrant further investigation. It combines three complementary techniques:

1. **Rule-based red flags** — detects entries posted on weekends, descriptions containing sensitive keywords (e.g. `好处费`, `kickback`, `reverse`, `adjust`), and amounts that are suspiciously round (multiples of 1,000) or end in `999`.
2. **Benford's Law test** — applies a chi-square goodness-of-fit test to the distribution of leading digits in the `amount` column. Natural financial data typically follows Benford's distribution; significant deviation (χ² > 15.507, df=8, p<0.05) suggests possible manipulation.
3. **Structured output** — returns every flagged row with specific reasons, plus the full Benford test statistics.

---

## OpenCode CLI Invocation

### Via stdin (recommended)

```bash
echo '{
  "intent": "run_fraud_scan",
  "params": {
    "file_path": "data/journal_entries.csv",
    "output_path": "results/fraud_detection_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

`fraud_instruction.json`:
```json
{
  "intent": "run_fraud_scan",
  "params": {
    "file_path": "data/journal_entries.csv",
    "output_path": "results/fraud_detection_result.json"
  }
}
```

```bash
python -m src.cli.main --instruction fraud_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{"intent": "run_fraud_scan", "params": {"file_path": "uploads/je.csv"}}'
```

---

## Parameters

| Parameter     | Type   | Required | Default                          | Description                              |
|---------------|--------|----------|----------------------------------|------------------------------------------|
| `file_path`   | string | ✅ Yes   | —                                | Path to CSV file with journal entries    |
| `output_path` | string | No       | `fraud_detection_result.json`    | Path to write the JSON result report     |

---

## Input File Format

CSV with at least one of these columns (column names are matched case-insensitively):

| Column              | Aliases                          | Purpose                        |
|---------------------|----------------------------------|--------------------------------|
| `date`              | `日期`                           | Entry date (for weekend check) |
| `description`       | `desc`, `摘要`, `备注`          | Narrative (keyword check)      |
| `amount`            | `金额`                           | Transaction amount (Benford)   |

Example:
```
date,description,amount
2024-01-15,Operating expenses,45000
2024-01-20,好处费 payment,100000
2024-01-21,Kickback adjustment,999
```

---

## Output Schema

```json
{
  "status": "ok",
  "risk_flags": [
    {
      "row": 1,
      "reasons": [
        "Sensitive keyword detected: '好处费'",
        "Round number amount: 100000.0"
      ]
    }
  ],
  "benford_result": {
    "chi_square": 12.34,
    "p_value": 0.1361,
    "conforming": true
  },
  "red_flag_count": 1
}
```

| Field             | Description                                                            |
|-------------------|------------------------------------------------------------------------|
| `status`          | `"ok"` on success, `"error"` on file read failure                     |
| `risk_flags`      | List of flagged rows, each with zero-indexed row number and reasons    |
| `benford_result`  | Chi-square statistic, p-value, and conformance boolean                 |
| `red_flag_count`  | Total number of rows with at least one red flag                        |

---

## Detection Rules

| Rule                   | Trigger Condition                                              |
|------------------------|----------------------------------------------------------------|
| Weekend posting        | `date` column parses to Saturday or Sunday                     |
| Sensitive keyword      | `description` contains: `好处费`, `冲销`, `暂估`, `调节`, `kickback`, `reverse`, `adjust` |
| Round number           | `amount % 1000 == 0` and amount ≠ 0                           |
| 999-ending             | Integer part of `abs(amount)` ends with `999`                  |

---

## Notes & Edge Cases

- **Benford threshold**: χ² > 15.507 (p < 0.05, df = 8) is considered non-conforming.
- **Minimum data**: Benford test requires ≥ 10 non-zero amounts; smaller datasets return `"note": "Insufficient data"`.
- **scipy optional**: p-value is `null` if `scipy` is not installed; conformance is still evaluated via the hardcoded critical value.
- **Input only CSV**: unlike other skills, this skill reads only CSV (not Excel) to preserve column name casing.

---

## Script

`scripts/skill_fraud_detection.py` — `run(file_path: str, output_path: str) -> dict`
