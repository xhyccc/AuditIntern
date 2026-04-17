"""
Skill: Fraud Detection
Analyzes journal entries for fraud indicators using rule-based checks and Benford's Law.
"""

import json
import math
import pathlib

import numpy as np
import pandas as pd

SENSITIVE_KEYWORDS = ["好处费", "冲销", "暂估", "调节", "kickback", "reverse", "adjust"]
BENFORD_EXPECTED = {
    d: math.log10(1 + 1 / d) for d in range(1, 10)
}


def _first_digit(value: float) -> int | None:
    abs_val = abs(value)
    if abs_val == 0:
        return None
    s = f"{abs_val:.10f}".replace(".", "").lstrip("0")
    return int(s[0]) if s else None


def _benford_test(amounts: pd.Series) -> dict:
    digits = [_first_digit(v) for v in amounts if v != 0]
    digits = [d for d in digits if d is not None]
    if len(digits) < 10:
        return {"chi_square": None, "p_value": None, "conforming": None, "note": "Insufficient data"}

    counts = {d: 0 for d in range(1, 10)}
    for d in digits:
        if d in counts:
            counts[d] += 1
    n = len(digits)
    chi_sq = sum(
        (counts[d] - n * BENFORD_EXPECTED[d]) ** 2 / (n * BENFORD_EXPECTED[d])
        for d in range(1, 10)
    )
    # chi-square distribution with 8 dof; critical value at p=0.05 is 15.507
    conforming = chi_sq < 15.507
    # approximate p-value using scipy if available, else None
    try:
        from scipy.stats import chi2
        p_value = float(1 - chi2.cdf(chi_sq, df=8))
    except ImportError:
        p_value = None

    return {
        "chi_square": round(chi_sq, 4),
        "p_value": round(p_value, 4) if p_value is not None else None,
        "conforming": conforming,
    }


def run(file_path: str, output_path: str) -> dict:
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as exc:
        result = {"status": "error", "risk_flags": [], "benford_result": {}, "red_flag_count": 0, "message": str(exc)}
        _write(output_path, result)
        return result

    risk_flags = []

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]

    date_col = next((c for c in df.columns if "date" in c or "日期" in c), None)
    desc_col = next((c for c in df.columns if "desc" in c or "摘要" in c or "description" in c or "备注" in c), None)
    amount_col = next((c for c in df.columns if "amount" in c or "金额" in c), None)

    amounts = pd.Series(dtype=float)
    if amount_col:
        amounts = pd.to_numeric(df[amount_col], errors="coerce").dropna()

    for idx, row in df.iterrows():
        reasons = []

        # Weekend check
        if date_col:
            try:
                dt = pd.to_datetime(row[date_col])
                if dt.weekday() >= 5:
                    reasons.append(f"Entry on weekend ({dt.strftime('%A')})")
            except Exception:
                pass

        # Sensitive keyword check
        if desc_col:
            desc = str(row.get(desc_col, ""))
            for kw in SENSITIVE_KEYWORDS:
                if kw in desc:
                    reasons.append(f"Sensitive keyword detected: '{kw}'")

        # Round number / ends in 999
        if amount_col:
            try:
                amt = float(row[amount_col])
                if amt != 0 and amt % 1000 == 0:
                    reasons.append(f"Round number amount: {amt}")
                elif str(int(abs(amt))).endswith("999"):
                    reasons.append(f"Amount ending in 999: {amt}")
            except (ValueError, TypeError):
                pass

        if reasons:
            risk_flags.append({"row": int(idx), "reasons": reasons})

    benford_result = _benford_test(amounts) if len(amounts) >= 1 else {"note": "No amount data"}

    result = {
        "status": "ok",
        "risk_flags": risk_flags,
        "benford_result": benford_result,
        "red_flag_count": len(risk_flags),
    }
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
