---
name: cross-reference-check
description: Validates consistency across multiple financial documents using configurable rules. Use when the user asks to cross-check figures between documents, verify that totals in one file match totals in another, run cross-document reconciliation, or apply custom comparison rules across CSV or Excel files.
---

# Cross Reference Check

Loads a JSON rules file and two or more data files (CSV/Excel). For each rule, sums the
specified column in each file and flags any pair where the values differ by more than 0.01.

## Script

`scripts/skill_cross_reference_check.py` — `run(rules_file, data_files, output_path) -> dict`
