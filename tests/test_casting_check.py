"""Tests for skill_casting_check."""

import json
import pandas as pd
import pytest
from src.skills.skill_casting_check import run


def _write_csv(tmp_path, data: dict, filename="test.csv") -> str:
    df = pd.DataFrame(data)
    path = tmp_path / filename
    df.to_csv(path, index=False)
    return str(path)


def test_casting_check_correct_sums(tmp_path):
    data = {
        "科目": ["销售收入", "其他收入", "合计"],
        "Q1": [100.0, 200.0, 300.0],
        "Q2": [150.0, 250.0, 400.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["status"] == "ok"
    assert result["discrepancies"] == []


def test_casting_check_wrong_column_sum(tmp_path):
    data = {
        "科目": ["销售收入", "其他收入", "合计"],
        "Q1": [100.0, 200.0, 999.0],  # Declared 999, actual 300
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    assert result["status"] == "ok"
    assert len(result["discrepancies"]) == 1
    disc = result["discrepancies"][0]
    assert disc["column"] == "Q1"
    assert abs(disc["diff"]) > 0.01


def test_casting_check_no_total_row(tmp_path):
    data = {
        "科目": ["销售收入", "其他收入"],
        "Q1": [100.0, 200.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "out.json")
    result = run(file_path, out)
    # No total row: nothing to validate against, should return no discrepancies
    assert result["status"] == "ok"
    assert result["discrepancies"] == []


def test_casting_check_output_written(tmp_path):
    data = {
        "科目": ["A", "合计"],
        "Amount": [500.0, 500.0],
    }
    file_path = _write_csv(tmp_path, data)
    out = str(tmp_path / "result.json")
    run(file_path, out)
    with open(out) as f:
        saved = json.load(f)
    assert "status" in saved
    assert "discrepancies" in saved
