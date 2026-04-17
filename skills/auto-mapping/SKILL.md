---
name: auto-mapping
description: Maps client trial balance accounts to a standard chart of accounts using TF-IDF NLP similarity. Use when the user asks to map accounts, match trial balance items to a standard COA, auto-categorize accounts, or align client account names with standard account names from a CSV or Excel file.
---

# Auto Mapping

Reads a client trial balance file and a standard chart-of-accounts file (both CSV or Excel,
both requiring an `account_name` column) and computes TF-IDF cosine similarity to find the
best matching standard account for each client account.

## Script

`scripts/skill_auto_mapping.py` — `run(tb_file, standard_coa_file, output_path) -> dict`
