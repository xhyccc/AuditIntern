---
name: cross-reference-check
description: Validates consistency of figures across multiple financial documents using configurable rules. Use when the user asks to cross-check totals between files, reconcile figures across documents, verify that a balance sheet total matches a trial balance, compare column sums in two different spreadsheets, or run multi-document consistency checks defined in a rules file.
---

# Cross Reference Check

## Overview

The **cross-reference check** skill validates that numeric totals are consistent across two or more financial documents — for example, confirming that the total revenue in the income statement equals the revenue line in the trial balance, or that bank balances in the bank reconciliation match the general ledger.

It reads a **JSON rules file** that declaratively describes which column in which file to compare, loads the data files (CSV or Excel), sums each referenced column, and flags any pair whose values differ by more than **¥0.01**.

This skill is fully data-driven: you define the rules without changing any code, making it reusable across different audit engagements.

---

## OpenCode CLI Invocation

### Via stdin

```bash
echo '{
  "intent": "run_cross_reference",
  "params": {
    "rules_file": "data/cross_ref_rules.json",
    "data_files": {
      "income_stmt": "data/income_statement.csv",
      "trial_balance": "data/trial_balance.csv"
    },
    "output_path": "results/cross_reference_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

`cross_ref_instruction.json`:
```json
{
  "intent": "run_cross_reference",
  "params": {
    "rules_file": "data/cross_ref_rules.json",
    "data_files": {
      "income_stmt": "data/income_statement.csv",
      "trial_balance": "data/trial_balance.csv",
      "bank_rec": "data/bank_reconciliation.csv"
    },
    "output_path": "results/cross_reference_result.json"
  }
}
```

```bash
python -m src.cli.main --instruction cross_ref_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d @cross_ref_instruction.json
```

---

## Parameters

| Parameter     | Type             | Required | Default                            | Description                                            |
|---------------|------------------|----------|------------------------------------|--------------------------------------------------------|
| `rules_file`  | string           | ✅ Yes   | —                                  | Path to JSON file containing comparison rules          |
| `data_files`  | dict[str, str]   | ✅ Yes   | —                                  | Map of file keys (used in rules) to actual file paths  |
| `output_path` | string           | No       | `cross_reference_result.json`      | Path to write the JSON result report                   |

---

## Rules File Format

The rules file is a JSON array. Each rule object specifies:

| Field      | Type   | Description                                          |
|------------|--------|------------------------------------------------------|
| `name`     | string | Human-readable rule name (appears in output)         |
| `file_a`   | string | Key in `data_files` for the first file               |
| `field_a`  | string | Column name in file A to sum (case-insensitive)      |
| `file_b`   | string | Key in `data_files` for the second file              |
| `field_b`  | string | Column name in file B to sum (case-insensitive)      |

Example `cross_ref_rules.json`:
```json
[
  {
    "name": "Revenue: Income Statement vs Trial Balance",
    "file_a": "income_stmt",
    "field_a": "revenue",
    "file_b": "trial_balance",
    "field_b": "amount"
  },
  {
    "name": "Bank Balance: Bank Rec vs General Ledger",
    "file_a": "bank_rec",
    "field_a": "balance",
    "file_b": "trial_balance",
    "field_b": "cash_balance"
  }
]
```

---

## Output Schema

```json
{
  "status": "ok",
  "discrepancies": [
    {
      "rule": "Revenue: Income Statement vs Trial Balance",
      "value_a": 5000000.0,
      "value_b": 4998500.0,
      "diff": 1500.0
    }
  ],
  "summary": "Found 1 discrepancy(ies)."
}
```

| Field           | Description                                                        |
|-----------------|--------------------------------------------------------------------|
| `status`        | `"ok"` even when discrepancies found; `"error"` on file failures  |
| `discrepancies` | List of rules where totals differ by > ¥0.01                       |
| `summary`       | Plain-language count of discrepancies                              |

If a rule encounters a missing column or unloaded file key, it adds an error entry:
```json
{ "rule": "Revenue check", "error": "Column 'revenue' not found. Available: ['Amount']" }
```

---

## Notes & Edge Cases

- **Column matching**: case-insensitive and leading/trailing whitespace is stripped.
- **Sum semantics**: the skill sums all rows in the specified column (no filtering). Pre-filter your files if only certain rows should be compared.
- **Tolerance**: differences ≤ 0.01 are not flagged.
- **Multiple files**: you can reference as many files as needed; just add them to `data_files`.

---

## Script

`scripts/skill_cross_reference_check.py` — `run(rules_file: str, data_files: dict, output_path: str) -> dict`
