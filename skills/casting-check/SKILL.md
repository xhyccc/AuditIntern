---
name: casting-check
description: Validates row and column totals in financial spreadsheets (casting check). Use when the user asks to verify spreadsheet totals, check for arithmetic errors in a financial table, validate casting, or confirm that column sums match declared totals in a CSV or Excel file.
---

# Casting Check

Validates that numeric column totals in a financial spreadsheet match declared "Total" rows.
Supports CSV and Excel files. Flags any column where the computed sum differs from the declared total by more than 0.01.

## Script

`scripts/skill_casting_check.py` — `run(file_path, output_path) -> dict`
