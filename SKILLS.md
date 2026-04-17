# Audit Intern Skills Reference

This document describes all available skills in the AI Audit System.

---

## skill_casting_check

**Description:** Validates row and column totals in financial spreadsheets (casting check).

**Input:**
- `file_path` (str): Path to CSV or Excel file containing financial data
- `output_path` (str): Path to write the JSON result report

**Output JSON:**
```json
{
  "status": "ok" | "error",
  "discrepancies": [
    {"type": "column_sum", "column": "...", "expected": 0.0, "actual": 0.0, "diff": 0.0}
  ],
  "summary": "Found N discrepancies in casting check."
}
```

---

## skill_fraud_detection

**Description:** Analyzes journal entries for fraud indicators using rule-based checks and Benford's Law.

**Input:**
- `file_path` (str): Path to CSV file containing journal entries (must have columns: date, description, amount)
- `output_path` (str): Path to write the JSON result report

**Output JSON:**
```json
{
  "status": "ok",
  "risk_flags": [{"row": 0, "reason": "..."}],
  "benford_result": {"chi_square": 0.0, "p_value": 0.0, "conforming": true},
  "red_flag_count": 0
}
```

---

## skill_auto_mapping

**Description:** Maps client trial balance accounts to standard chart of accounts using NLP similarity.

**Input:**
- `tb_file` (str): Path to CSV/Excel with client trial balance (must have 'account_name' column)
- `standard_coa_file` (str): Path to CSV/Excel with standard chart of accounts (must have 'account_name' column)
- `output_path` (str): Path to write the JSON result report

**Output JSON:**
```json
{
  "status": "ok",
  "mappings": [
    {"client_account": "...", "matched_standard": "...", "confidence": 0.95}
  ]
}
```

---

## skill_cross_reference_check

**Description:** Validates consistency across multiple financial documents using configurable rules.

**Input:**
- `rules_file` (str): Path to JSON rules file
- `data_files` (dict): Mapping of file keys to file paths, e.g. `{"file_a": "path/to/a.csv"}`
- `output_path` (str): Path to write the JSON result report

**Rules JSON format:**
```json
[
  {
    "name": "Rule name",
    "file_a": "file_a",
    "field_a": "column_in_a",
    "file_b": "file_b",
    "field_b": "column_in_b"
  }
]
```

**Output JSON:**
```json
{
  "status": "ok",
  "discrepancies": [
    {"rule": "...", "value_a": 0.0, "value_b": 0.0, "diff": 0.0}
  ],
  "summary": "..."
}
```

---

## skill_ocr_extraction

**Description:** Extracts text and structured fields from images or PDF files.

**Input:**
- `file_path` (str): Path to image (PNG/JPG/TIFF) or PDF file
- `output_path` (str): Path to write the JSON result report

**Output JSON:**
```json
{
  "status": "ok",
  "text": "extracted text...",
  "confidence": 0.9,
  "page_count": 1
}
```

---

## skill_llm_contract_parser

**Description:** Extracts structured fields from contract text using an LLM (OpenAI or mock).

**Input:**
- `text` (str): Contract text to parse
- `output_path` (str): Path to write the JSON result report
- `api_key` (str, optional): OpenAI API key; if absent, returns mock data

**Output JSON:**
```json
{
  "status": "ok",
  "fields": {
    "transaction_amount": "...",
    "effective_date": "...",
    "party_a": "...",
    "party_b": "...",
    "key_terms": ["..."]
  },
  "source": "llm" | "mock"
}
```

---

## skill_rag_legal_search

**Description:** Retrieves relevant legal/regulatory passages from a knowledge base using TF-IDF similarity.

**Input:**
- `query` (str): Search query
- `knowledge_base_path` (str): Path to directory or text file containing documents
- `output_path` (str): Path to write the JSON result report

**Output JSON:**
```json
{
  "status": "ok",
  "answer": "Most relevant passage...",
  "citations": [{"source": "doc.txt", "score": 0.85, "excerpt": "..."}]
}
```

---

## skill_analytical_review

**Description:** Performs analytical procedures comparing current vs prior period financial balances.

**Input:**
- `current_file` (str): Path to current period CSV/Excel (must have 'account' and 'amount' columns)
- `prior_file` (str): Path to prior period CSV/Excel (must have 'account' and 'amount' columns)
- `output_path` (str): Path to write the JSON result report
- `threshold_pct` (float): Percentage change threshold for flagging (default: 15.0)
- `threshold_amount` (float): Absolute amount threshold for flagging (default: 500000)

**Output JSON:**
```json
{
  "status": "ok",
  "flagged_accounts": [
    {"account": "...", "current": 0.0, "prior": 0.0, "change_pct": 0.0, "change_amount": 0.0}
  ],
  "narrative": "..."
}
```

---

## skill_wp_generator

**Description:** Generates audit work papers by filling tagged placeholders in Excel or Word templates.

**Input:**
- `template_path` (str): Path to Excel (.xlsx) or Word (.docx) template file
- `data_file` (str): Path to JSON file with key-value data to fill into template
- `output_path` (str): Path to save the generated work paper

**Output JSON:**
```json
{
  "status": "ok",
  "output_file": "...",
  "fields_filled": ["..."]
}
```
