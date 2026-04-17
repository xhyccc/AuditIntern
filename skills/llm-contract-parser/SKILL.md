---
name: llm-contract-parser
description: Extracts structured fields from contract text using an LLM (OpenAI) or a built-in mock parser. Use when the user asks to parse a contract, extract key terms from an agreement, identify transaction amounts or effective dates in a legal document, or analyze contract text for party names and obligations.
---

# LLM Contract Parser

Accepts raw contract text and optionally an OpenAI API key. Calls GPT-4o-mini to extract
`transaction_amount`, `effective_date`, `party_a`, `party_b`, and `key_terms`. Falls back
to a regex-based mock parser when no API key is provided.

## Script

`scripts/skill_llm_contract_parser.py` — `run(text, output_path, api_key=None) -> dict`
