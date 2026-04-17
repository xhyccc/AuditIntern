"""Tests for skill_fraud_detection."""

import json
import pandas as pd
import pytest
from src.skills.skill_fraud_detection import run


def _write_csv(tmp_path, data: dict, filename="je.csv") -> str:
    df = pd.DataFrame(data)
    path = tmp_path / filename
    df.to_csv(path, index=False)
    return str(path)


def test_fraud_benford_natural_data(tmp_path):
    # Natural Benford-conforming data: powers of 2
    import math
    amounts = [2**i for i in range(30)]
    data = {
        "date": ["2024-01-15"] * 30,
        "description": ["Normal entry"] * 30,
        "amount": amounts,
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["status"] == "ok"
    assert "benford_result" in result


def test_fraud_sensitive_keyword(tmp_path):
    data = {
        "date": ["2024-01-15"],
        "description": ["支付好处费给供应商"],
        "amount": [50000.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["red_flag_count"] >= 1
    reasons = result["risk_flags"][0]["reasons"]
    assert any("好处费" in r for r in reasons)


def test_fraud_round_number(tmp_path):
    data = {
        "date": ["2024-01-10"],
        "description": ["费用报销"],
        "amount": [100000.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["red_flag_count"] >= 1
    reasons = result["risk_flags"][0]["reasons"]
    assert any("Round number" in r for r in reasons)


def test_fraud_weekend_detection(tmp_path):
    # 2024-01-06 is a Saturday
    data = {
        "date": ["2024-01-06"],
        "description": ["周末记账"],
        "amount": [12345.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["red_flag_count"] >= 1
    reasons = result["risk_flags"][0]["reasons"]
    assert any("weekend" in r.lower() for r in reasons)


def test_fraud_output_written(tmp_path):
    data = {
        "date": ["2024-03-01"],
        "description": ["Normal"],
        "amount": [1234.5],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    run(file_path, out)
    with open(out) as f:
        saved = json.load(f)
    assert "risk_flags" in saved
    assert "benford_result" in saved
