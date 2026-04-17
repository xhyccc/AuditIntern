# LLM Contract Parser — API Reference

## Function Signature

```python
from skills.llm_contract_parser.scripts.skill_llm_contract_parser import run

result = run(
    text="Contract text...",
    output_path="results/contract_parse_result.json",
    api_key="sk-..."   # Optional; omit for mock mode
)
```

## OpenCode CLI — Intent Name

`run_contract_parse`

## Required Parameters

| Parameter | Type   | Description                                           |
|-----------|--------|-------------------------------------------------------|
| `text`    | string | Raw contract text (up to ~8,000 chars in LLM mode)   |

## Optional Parameters

| Parameter     | Type   | Default                       | Description                               |
|---------------|--------|-------------------------------|-------------------------------------------|
| `output_path` | string | `contract_parse_result.json`  | JSON output file path                     |
| `api_key`     | string | `null`                        | OpenAI API key; enables LLM extraction    |

## LLM Configuration

| Setting     | Value            |
|-------------|------------------|
| Model       | `gpt-4o-mini`    |
| Temperature | `0` (deterministic) |
| Max input   | 8,000 characters |

## Extracted Fields

| Field                | Type            | Description                           |
|----------------------|-----------------|---------------------------------------|
| `transaction_amount` | string          | Contract value or payment amount      |
| `effective_date`     | string          | Contract start or signing date        |
| `party_a`            | string          | First contracting party               |
| `party_b`            | string          | Second contracting party              |
| `key_terms`          | array[string]   | Notable obligations, terms, clauses   |

## Mock Parser Patterns

| Field                | Regex Pattern                                        |
|----------------------|------------------------------------------------------|
| `transaction_amount` | `(?:金额|amount)[：:\s]*([0-9,，.]+)` (case-insensitive) |
| `effective_date`     | `\d{4}[-年/]\d{1,2}[-月/]\d{1,2}`                 |
| Other fields         | `"N/A (mock)"`                                       |

## Error Handling

- LLM API failure → falls back to mock mode (no exception raised)
- JSON parse error from LLM → falls back to mock mode
- Always returns `status: "ok"`

## Dependencies

| Package  | Purpose          |
|----------|------------------|
| `openai` | LLM API calls (optional) |
