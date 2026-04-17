---
name: wp-generator
description: Generates audit work papers by filling tagged placeholders in Excel or Word templates. Use when the user asks to generate a work paper, fill in an audit template, populate a Word or Excel document with audit data, produce a formatted report from a template, create an audit memo, or output a completed work paper from a JSON data file and a template.
---

# Work Paper Generator

## Overview

The **work paper generator** skill automates the production of standardized audit documentation. It reads a JSON file containing key-value data and fills `{{placeholder}}` tags in an Excel (`.xlsx`) or Word (`.docx`) template, producing a completed work paper file.

This enables audit teams to:
- Maintain a single canonical template per work paper type
- Populate dozens of fields automatically from structured audit data
- Generate consistent, professionally formatted documents without manual copy-paste
- Combine with other skills: run `analytical-review` → feed output into `wp-generator`

---

## OpenCode CLI Invocation

### Excel template

```bash
echo '{
  "intent": "run_wp_generate",
  "params": {
    "template_path": "assets/wp-generator/audit_memo_template.xlsx",
    "data_file": "data/audit_data.json",
    "output_path": "results/completed_audit_memo.xlsx"
  }
}' | python -m src.cli.main
```

### Word template

```bash
echo '{
  "intent": "run_wp_generate",
  "params": {
    "template_path": "assets/wp-generator/engagement_letter_template.docx",
    "data_file": "data/engagement_data.json",
    "output_path": "results/engagement_letter_2024.docx"
  }
}' | python -m src.cli.main
```

### Via instruction file

`wp_instruction.json`:
```json
{
  "intent": "run_wp_generate",
  "params": {
    "template_path": "assets/wp-generator/analytical_review_wp.docx",
    "data_file": "data/analytical_review_data.json",
    "output_path": "results/AR_WP_2024.docx"
  }
}
```

```bash
python -m src.cli.main --instruction wp_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d @wp_instruction.json
```

---

## Parameters

| Parameter       | Type   | Required | Default          | Description                                          |
|-----------------|--------|----------|------------------|------------------------------------------------------|
| `template_path` | string | ✅ Yes   | —                | Path to Excel (`.xlsx`) or Word (`.docx`) template   |
| `data_file`     | string | ✅ Yes   | —                | Path to JSON file with key-value substitution data   |
| `output_path`   | string | No       | `wp_output`      | Path for the generated work paper (no extension added) |

---

## Template Format

Templates use `{{key}}` placeholders that are replaced with values from the data JSON.

**Excel template** (any cell):
```
Audit Period:    {{audit_period}}
Client Name:     {{client_name}}
Prepared By:     {{preparer_name}}
Total Revenue:   {{total_revenue}}
```

**Word template** (any paragraph or table cell):
```
AUDIT MEMORANDUM

Client: {{client_name}}
Period: {{audit_period}}
Engagement Partner: {{partner_name}}

Finding: {{finding_description}}
Risk Level: {{risk_level}}
```

---

## Data File Format

The data file is a flat JSON object:

```json
{
  "client_name": "ABC Manufacturing Co., Ltd.",
  "audit_period": "Year ended December 31, 2024",
  "preparer_name": "Li Ming",
  "partner_name": "Wang Fang",
  "total_revenue": "¥125,000,000",
  "finding_description": "Revenue recognition policy was consistently applied.",
  "risk_level": "Low"
}
```

All values are converted to strings before substitution.

---

## Output Schema

The skill writes a **result JSON** alongside the generated document:

```json
{
  "status": "ok",
  "output_file": "results/completed_audit_memo.xlsx",
  "fields_filled": [
    "client_name",
    "audit_period",
    "preparer_name",
    "total_revenue"
  ]
}
```

| Field          | Description                                                           |
|----------------|-----------------------------------------------------------------------|
| `status`       | `"ok"` on success, `"error"` on template load or fill failure        |
| `output_file`  | Path to the generated work paper                                      |
| `fields_filled`| List of placeholder keys that were successfully substituted           |

> Note: a `<output_path>.result.json` sidecar file is always written in addition to the work paper itself.

---

## Notes & Edge Cases

- **Unfilled placeholders**: if a key exists in the template but not in the data JSON, that placeholder is left as-is in the output (e.g. `{{missing_key}}`).
- **Extra data keys**: keys in the JSON that have no matching placeholder in the template are silently ignored.
- **Word run splitting**: Word sometimes splits placeholder text across multiple runs. If a placeholder is not being replaced, try typing and deleting it fresh in the template to force a single run.
- **Excel formulas**: formula cells are not processed — only string-value cells are scanned for placeholders.
- **Supported formats**: `.xlsx`/`.xls` (openpyxl) and `.docx` (python-docx). `.doc` and `.odt` are not supported.

---

## Script

`scripts/skill_wp_generator.py` — `run(template_path: str, data_file: str, output_path: str) -> dict`
