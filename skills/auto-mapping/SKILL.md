---
name: auto-mapping
description: Maps client trial balance accounts to a standard chart of accounts using TF-IDF NLP similarity. Use when the user asks to map accounts, match trial balance items to a standard COA, auto-categorize client accounts, align account names across two files, or reconcile a client chart of accounts to a standard classification in CSV or Excel format.
---

# Auto Mapping

## Overview

The **auto-mapping** skill automates the tedious process of matching client account names to a standard chart of accounts (COA). It reads two files — a client trial balance and a standard COA — normalizes all account names (Unicode NFKC, lowercase, whitespace collapse), then computes **TF-IDF character n-gram cosine similarity** between each client account and every standard account. The best-matching standard account and its confidence score are returned for each client account.

This saves hours of manual cross-referencing when onboarding a new client or consolidating accounts across entities.

**Algorithm**: scikit-learn `TfidfVectorizer` with `char_wb` analyzer and 2–3 character n-grams. Falls back to Jaccard character-set overlap if scikit-learn is unavailable.

---

## OpenCode CLI Invocation

### Via stdin

```bash
echo '{
  "intent": "run_auto_mapping",
  "params": {
    "tb_file": "data/client_trial_balance.csv",
    "standard_coa_file": "data/standard_coa.csv",
    "output_path": "results/auto_mapping_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

`mapping_instruction.json`:
```json
{
  "intent": "run_auto_mapping",
  "params": {
    "tb_file": "data/client_trial_balance.xlsx",
    "standard_coa_file": "data/standard_coa.xlsx",
    "output_path": "results/auto_mapping_result.json"
  }
}
```

```bash
python -m src.cli.main --instruction mapping_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "run_auto_mapping",
    "params": {
      "tb_file": "uploads/client_tb.csv",
      "standard_coa_file": "uploads/standard_coa.csv"
    }
  }'
```

---

## Parameters

| Parameter           | Type   | Required | Default                       | Description                                        |
|---------------------|--------|----------|-------------------------------|----------------------------------------------------|
| `tb_file`           | string | ✅ Yes   | —                             | Path to client trial balance (CSV or Excel)        |
| `standard_coa_file` | string | ✅ Yes   | —                             | Path to standard COA file (CSV or Excel)           |
| `output_path`       | string | No       | `auto_mapping_result.json`    | Path to write the JSON result report               |

---

## Input File Format

Both files must contain an account name column. The skill auto-detects columns containing `account` (case-insensitive) or `科目`.

**Client trial balance** (`tb_file`):
```
account_name,debit,credit
应收账款,500000,0
货币资金,200000,0
预付账款,80000,0
```

**Standard COA** (`standard_coa_file`):
```
account_name,account_code,category
Accounts Receivable,1122,Current Assets
Cash and Cash Equivalents,1001,Current Assets
Prepaid Expenses,1221,Current Assets
```

---

## Output Schema

```json
{
  "status": "ok",
  "mappings": [
    {
      "client_account": "应收账款",
      "matched_standard": "Accounts Receivable",
      "confidence": 0.8731
    },
    {
      "client_account": "货币资金",
      "matched_standard": "Cash and Cash Equivalents",
      "confidence": 0.6204
    }
  ]
}
```

| Field                | Description                                                        |
|----------------------|--------------------------------------------------------------------|
| `status`             | `"ok"` on success, `"error"` on file load failure                 |
| `mappings`           | One entry per client account                                       |
| `client_account`     | Original account name from the client trial balance                |
| `matched_standard`   | Best-matching account from the standard COA                        |
| `confidence`         | Cosine similarity score [0.0 – 1.0]; higher = more confident      |

---

## Interpreting Confidence Scores

| Score Range | Interpretation                            | Recommended Action         |
|-------------|-------------------------------------------|----------------------------|
| ≥ 0.90      | Strong match — likely correct             | Accept automatically       |
| 0.60 – 0.89 | Moderate match — review recommended       | Manual confirmation        |
| < 0.60      | Weak match — may need reclassification    | Manual mapping required    |

---

## Notes & Edge Cases

- **Language**: works on Chinese and English account names; n-gram character model handles mixed-language inputs well.
- **Column detection**: if no column name contains `account` or `科目`, the first column is used.
- **Empty cells**: rows with null account names are skipped.
- **Many-to-one**: multiple client accounts may map to the same standard account; this is expected.

---

## Script

`scripts/skill_auto_mapping.py` — `run(tb_file: str, standard_coa_file: str, output_path: str) -> dict`
