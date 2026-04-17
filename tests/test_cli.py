"""Tests for the CLI orchestrator."""

import json
import pathlib
import subprocess
import sys
import pandas as pd
import pytest

_REPO_ROOT = pathlib.Path(__file__).parent.parent


def _write_csv(tmp_path, data: dict, filename: str) -> str:
    df = pd.DataFrame(data)
    path = tmp_path / filename
    df.to_csv(path, index=False)
    return str(path)


def _run_cli(instruction: dict) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main"],
        input=json.dumps(instruction),
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    return json.loads(result.stdout)


def test_cli_casting_check(tmp_path):
    data = {
        "科目": ["A", "B", "合计"],
        "Amount": [100.0, 200.0, 300.0],
    }
    file_path = _write_csv(tmp_path, data, "test.csv")
    out = str(tmp_path / "out.json")
    instruction = {
        "intent": "run_casting_check",
        "params": {"file_path": file_path, "output_path": out},
    }
    result = _run_cli(instruction)
    assert result["status"] == "ok"
    assert result["discrepancies"] == []


def test_cli_invalid_intent():
    instruction = {"intent": "run_nonexistent_skill", "params": {}}
    result = _run_cli(instruction)
    assert result["status"] == "error"
    assert "Unknown intent" in result["message"]


def test_cli_missing_intent():
    result = _run_cli({})
    assert result["status"] == "error"
    assert "intent" in result["message"].lower()


def test_cli_from_instruction_file(tmp_path):
    data = {
        "科目": ["X", "合计"],
        "Val": [42.0, 42.0],
    }
    csv_path = _write_csv(tmp_path, data, "data.csv")
    out = str(tmp_path / "out.json")
    instruction = {
        "intent": "run_casting_check",
        "params": {"file_path": csv_path, "output_path": out},
    }
    instr_file = tmp_path / "instruction.json"
    instr_file.write_text(json.dumps(instruction))
    result = subprocess.run(
        [sys.executable, "-m", "src.cli.main", "--instruction", str(instr_file)],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    parsed = json.loads(result.stdout)
    assert parsed["status"] == "ok"
