"""
Skill: Cross Reference Check
Validates consistency across multiple financial documents using configurable rules.
"""

import json
import math
import pathlib

import pandas as pd


def _load_file(file_path: str) -> pd.DataFrame:
    path = pathlib.Path(file_path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def _get_total(df: pd.DataFrame, field: str) -> float:
    col = next((c for c in df.columns if c.strip().lower() == field.strip().lower()), None)
    if col is None:
        raise KeyError(f"Column '{field}' not found. Available: {list(df.columns)}")
    numeric = pd.to_numeric(df[col], errors="coerce").dropna()
    return float(numeric.sum())


def run(rules_file: str, data_files: dict, output_path: str) -> dict:
    try:
        with open(rules_file, "r", encoding="utf-8") as fh:
            rules = json.load(fh)
    except Exception as exc:
        result = {"status": "error", "discrepancies": [], "summary": str(exc)}
        _write(output_path, result)
        return result

    loaded: dict[str, pd.DataFrame] = {}
    for key, path in data_files.items():
        try:
            loaded[key] = _load_file(path)
        except Exception as exc:
            result = {"status": "error", "discrepancies": [], "summary": f"Failed to load '{key}': {exc}"}
            _write(output_path, result)
            return result

    discrepancies = []
    for rule in rules:
        name = rule.get("name", "unnamed")
        try:
            val_a = _get_total(loaded[rule["file_a"]], rule["field_a"])
            val_b = _get_total(loaded[rule["file_b"]], rule["field_b"])
            diff = val_a - val_b
            if not math.isclose(diff, 0, abs_tol=0.01):
                discrepancies.append(
                    {
                        "rule": name,
                        "value_a": round(val_a, 4),
                        "value_b": round(val_b, 4),
                        "diff": round(diff, 4),
                    }
                )
        except Exception as exc:
            discrepancies.append({"rule": name, "error": str(exc)})

    summary = (
        "No discrepancies found."
        if not discrepancies
        else f"Found {len(discrepancies)} discrepancy(ies)."
    )
    result = {"status": "ok", "discrepancies": discrepancies, "summary": summary}
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
