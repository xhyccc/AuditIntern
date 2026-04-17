---
name: llm-contract-parser
description: Extracts structured fields from contract text using an LLM or a built-in mock parser. Use when the user asks to parse a contract, extract key terms from an agreement, identify transaction amounts or effective dates in a legal document, pull party names from a contract, analyze contract obligations, or structure unstructured contract text into JSON fields.
---

# LLM Contract Parser

## Overview

The **LLM contract parser** skill extracts a standardized set of fields from raw contract text. It supports two modes:

1. **LLM mode** (when an OpenAI API key is provided): sends the contract text to `gpt-4o-mini` with a structured extraction prompt and parses the JSON response. This provides high-quality extraction across any contract language and format.
2. **Mock mode** (when no API key is provided): applies regex patterns to extract dates and amounts. Useful for testing, offline environments, or low-priority documents where approximate extraction is acceptable.

Extracted fields are standardized regardless of mode, making downstream processing consistent.

---

## OpenCode CLI Invocation

### LLM mode (with OpenAI API key)

```bash
echo '{
  "intent": "run_contract_parse",
  "params": {
    "text": "This agreement is entered into on 2024-03-01 between Party A (ABC Corp) and Party B (XYZ Ltd). The transaction amount is ¥2,500,000. Key terms include: 90-day payment schedule, penalty clauses for late delivery.",
    "output_path": "results/contract_parse_result.json",
    "api_key": "sk-..."
  }
}' | python -m src.cli.main
```

### Mock mode (no API key)

```bash
echo '{
  "intent": "run_contract_parse",
  "params": {
    "text": "Contract dated 2024-03-01. Amount: 2,500,000. Between ABC Corp and XYZ Ltd.",
    "output_path": "results/contract_parse_result.json"
  }
}' | python -m src.cli.main
```

### With text from OCR (pipeline)

```bash
# Extract text from scanned contract, then parse fields
OCR_TEXT=$(python -m src.cli.main --instruction ocr_instruction.json | python -c "import json,sys; print(json.load(sys.stdin)['text'])")

echo "{
  \"intent\": \"run_contract_parse\",
  \"params\": {
    \"text\": $(echo "$OCR_TEXT" | python -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    \"output_path\": \"results/contract_fields.json\"
  }
}" | python -m src.cli.main
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "run_contract_parse",
    "params": {
      "text": "Contract text here...",
      "output_path": "results/contract_parse_result.json",
      "api_key": "sk-..."
    }
  }'
```

---

## Parameters

| Parameter     | Type   | Required | Default                          | Description                                              |
|---------------|--------|----------|----------------------------------|----------------------------------------------------------|
| `text`        | string | ✅ Yes   | —                                | Raw contract text to parse (up to ~8,000 chars for LLM) |
| `output_path` | string | No       | `contract_parse_result.json`     | Path to write the JSON result report                     |
| `api_key`     | string | No       | `null` (uses mock mode)          | OpenAI API key; enables LLM extraction                   |

---

## Output Schema

```json
{
  "status": "ok",
  "fields": {
    "transaction_amount": "¥2,500,000",
    "effective_date": "2024-03-01",
    "party_a": "ABC Corp",
    "party_b": "XYZ Ltd",
    "key_terms": [
      "90-day payment schedule",
      "penalty clauses for late delivery"
    ]
  },
  "source": "llm"
}
```

| Field                | Description                                                              |
|----------------------|--------------------------------------------------------------------------|
| `status`             | Always `"ok"` (falls back to mock on LLM failure)                       |
| `fields`             | Extracted contract fields                                                |
| `transaction_amount` | Contract value or transaction amount                                     |
| `effective_date`     | Contract effective or signing date                                       |
| `party_a`            | First party name                                                         |
| `party_b`            | Second party name                                                        |
| `key_terms`          | List of notable contract terms, obligations, or clauses                 |
| `source`             | `"llm"` when OpenAI was used, `"mock"` otherwise                        |

---

## LLM System Prompt

The skill uses this system prompt:
> *"You are a legal contract analysis assistant. Extract the following fields from the contract text provided and return a JSON object: transaction_amount, effective_date, party_a, party_b, key_terms (array of strings). Return ONLY valid JSON."*

---

## Notes & Edge Cases

- **Text length**: LLM mode truncates input to 8,000 characters. For longer contracts, pre-chunk the text.
- **LLM fallback**: if the OpenAI call fails (network error, quota exceeded, malformed JSON), the skill automatically falls back to mock mode without raising an error.
- **Code fences**: the skill strips ` ```json ` / ` ``` ` fences from LLM responses before parsing.
- **Mock accuracy**: the regex mock extracts the first matching date pattern (`YYYY-MM-DD`, `YYYY年MM月DD日`, etc.) and the first `amount:` or `金额:` match. All other fields default to `"N/A (mock)"`.

---

## Script

`scripts/skill_llm_contract_parser.py` — `run(text: str, output_path: str, api_key: str = None) -> dict`
