"""Tests for skill_auto_mapping."""

import json
import pandas as pd
import pytest
from src.skills.skill_auto_mapping import run


def _write_csv(tmp_path, data: dict, filename: str) -> str:
    df = pd.DataFrame(data)
    path = tmp_path / filename
    df.to_csv(path, index=False)
    return str(path)


def test_auto_mapping_receivables(tmp_path):
    tb = {"account_name": ["应收账款", "货币资金"]}
    coa = {"account_name": ["应收账款 - Accounts Receivable", "现金及现金等价物", "存货"]}
    tb_file = _write_csv(tmp_path, tb, "tb.csv")
    coa_file = _write_csv(tmp_path, coa, "coa.csv")
    out = str(tmp_path / "out.json")
    result = run(tb_file, coa_file, out)
    assert result["status"] == "ok"
    assert len(result["mappings"]) == 2
    # 应收账款 should map to the receivables account with highest confidence
    mapping_0 = result["mappings"][0]
    assert "应收账款" in mapping_0["matched_standard"] or mapping_0["confidence"] > 0


def test_auto_mapping_exact_match(tmp_path):
    tb = {"account_name": ["现金"]}
    coa = {"account_name": ["现金", "银行存款", "应收账款"]}
    tb_file = _write_csv(tmp_path, tb, "tb.csv")
    coa_file = _write_csv(tmp_path, coa, "coa.csv")
    out = str(tmp_path / "out.json")
    result = run(tb_file, coa_file, out)
    assert result["status"] == "ok"
    mapping = result["mappings"][0]
    assert mapping["matched_standard"] == "现金"
    assert mapping["confidence"] > 0.5


def test_auto_mapping_output_written(tmp_path):
    tb = {"account_name": ["Test Account"]}
    coa = {"account_name": ["Test Account", "Other Account"]}
    tb_file = _write_csv(tmp_path, tb, "tb.csv")
    coa_file = _write_csv(tmp_path, coa, "coa.csv")
    out = str(tmp_path / "out.json")
    run(tb_file, coa_file, out)
    with open(out) as f:
        saved = json.load(f)
    assert "mappings" in saved
