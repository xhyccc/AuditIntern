"""Tests for skill_cross_reference_check."""

import json
import pandas as pd
import pytest
from src.skills.skill_cross_reference_check import run


def _write_csv(tmp_path, data: dict, filename: str) -> str:
    df = pd.DataFrame(data)
    path = tmp_path / filename
    df.to_csv(path, index=False)
    return str(path)


def _write_rules(tmp_path, rules: list, filename="rules.json") -> str:
    path = tmp_path / filename
    path.write_text(json.dumps(rules), encoding="utf-8")
    return str(path)


def test_cross_reference_matching_values(tmp_path):
    file_a = _write_csv(tmp_path, {"revenue": [100.0, 200.0, 300.0]}, "a.csv")
    file_b = _write_csv(tmp_path, {"total_revenue": [600.0]}, "b.csv")
    rules = [
        {
            "name": "Revenue check",
            "file_a": "a",
            "field_a": "revenue",
            "file_b": "b",
            "field_b": "total_revenue",
        }
    ]
    rules_file = _write_rules(tmp_path, rules)
    out = str(tmp_path / "out.json")
    result = run(rules_file, {"a": file_a, "b": file_b}, out)
    assert result["status"] == "ok"
    assert result["discrepancies"] == []


def test_cross_reference_mismatching_values(tmp_path):
    file_a = _write_csv(tmp_path, {"revenue": [100.0, 200.0]}, "a.csv")
    file_b = _write_csv(tmp_path, {"total_revenue": [999.0]}, "b.csv")
    rules = [
        {
            "name": "Revenue mismatch",
            "file_a": "a",
            "field_a": "revenue",
            "file_b": "b",
            "field_b": "total_revenue",
        }
    ]
    rules_file = _write_rules(tmp_path, rules)
    out = str(tmp_path / "out.json")
    result = run(rules_file, {"a": file_a, "b": file_b}, out)
    assert result["status"] == "ok"
    assert len(result["discrepancies"]) == 1
    assert result["discrepancies"][0]["rule"] == "Revenue mismatch"


def test_cross_reference_output_written(tmp_path):
    file_a = _write_csv(tmp_path, {"amount": [50.0]}, "a.csv")
    file_b = _write_csv(tmp_path, {"amount": [50.0]}, "b.csv")
    rules = [{"name": "Match", "file_a": "a", "field_a": "amount", "file_b": "b", "field_b": "amount"}]
    rules_file = _write_rules(tmp_path, rules)
    out = str(tmp_path / "out.json")
    run(rules_file, {"a": file_a, "b": file_b}, out)
    with open(out) as f:
        saved = json.load(f)
    assert "discrepancies" in saved
    assert "summary" in saved
