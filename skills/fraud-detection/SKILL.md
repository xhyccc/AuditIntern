---
name: fraud-detection
description: Analyzes journal entries for fraud indicators using rule-based checks and Benford's Law. Use when the user asks to scan for fraud, detect suspicious transactions, check for weekend entries, flag round-number amounts, identify sensitive keywords in journal descriptions, or test Benford's Law conformance on financial data.
---

# Fraud Detection

Reads a CSV of journal entries (columns: date, description, amount) and flags:
- Entries posted on weekends
- Descriptions containing sensitive keywords (e.g. "kickback", "reverse")
- Round-number or 999-ending amounts

Also runs a Benford's Law chi-square test on the amount column.

## Script

`scripts/skill_fraud_detection.py` — `run(file_path, output_path) -> dict`
