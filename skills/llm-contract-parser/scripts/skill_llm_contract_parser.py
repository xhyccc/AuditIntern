"""
Skill: LLM Contract Parser
Extracts structured fields from contracts using LLM (OpenAI) or mock.
"""

import json
import pathlib
import re


_MOCK_RESULT = {
    "transaction_amount": "N/A (mock)",
    "effective_date": "N/A (mock)",
    "party_a": "N/A (mock)",
    "party_b": "N/A (mock)",
    "key_terms": ["N/A (mock)"],
}

_SYSTEM_PROMPT = (
    "You are a legal contract analysis assistant. "
    "Extract the following fields from the contract text provided and return a JSON object: "
    "transaction_amount, effective_date, party_a, party_b, key_terms (array of strings). "
    "Return ONLY valid JSON."
)


def run(text: str, output_path: str, api_key: str = None) -> dict:
    if api_key:
        fields = _call_openai(text, api_key)
        source = "llm"
    else:
        fields = _mock_parse(text)
        source = "mock"

    result = {"status": "ok", "fields": fields, "source": source}
    _write(output_path, result)
    return result


def _call_openai(text: str, api_key: str) -> dict:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text[:8000]},
            ],
            temperature=0,
        )
        raw = response.choices[0].message.content
        # Strip code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
        return json.loads(raw)
    except Exception:
        return _mock_parse(text)


def _mock_parse(text: str) -> dict:
    """Simple regex-based mock parser."""
    result = dict(_MOCK_RESULT)

    amount_match = re.search(r"(?:金额|amount)[：:\s]*([0-9,，.]+)", text, re.IGNORECASE)
    if amount_match:
        result["transaction_amount"] = amount_match.group(1)

    date_match = re.search(r"\d{4}[-年/]\d{1,2}[-月/]\d{1,2}", text)
    if date_match:
        result["effective_date"] = date_match.group(0)

    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
