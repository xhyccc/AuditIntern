"""
Skill: Casting Check
Validates row/column totals in financial spreadsheets.
"""

import json
import math
import pathlib

import numpy as np
import pandas as pd

TOTAL_KEYWORDS = {"合计", "Total", "TOTAL", "total", "小计", "subtotal", "Subtotal"}


def _load_file(file_path: str) -> pd.DataFrame:
    path = pathlib.Path(file_path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, dtype=str)
    return pd.read_csv(path, dtype=str)


def _to_numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def run(file_path: str, output_path: str) -> dict:
    try:
        df = _load_file(file_path)
    except Exception as exc:
        result = {"status": "error", "discrepancies": [], "summary": str(exc)}
        _write(output_path, result)
        return result

    discrepancies = []

    # Identify total rows by checking first column value
    first_col = df.columns[0]
    total_mask = df[first_col].isin(TOTAL_KEYWORDS)
    data_df = df[~total_mask].copy()
    total_df = df[total_mask].copy()

    numeric_cols = [
        c for c in df.columns if _to_numeric_series(df[c]).notna().any()
    ]

    for col in numeric_cols:
        data_vals = _to_numeric_series(data_df[col]).fillna(0)
        computed_sum = data_vals.sum()

        if not total_df.empty:
            total_vals = _to_numeric_series(total_df[col])
            declared_total = total_vals.dropna()
            if declared_total.empty:
                continue
            declared = declared_total.iloc[0]
            diff = computed_sum - declared
            if not math.isclose(diff, 0, abs_tol=0.01):
                discrepancies.append(
                    {
                        "type": "column_sum",
                        "column": col,
                        "expected": round(declared, 4),
                        "actual": round(computed_sum, 4),
                        "diff": round(diff, 4),
                    }
                )

    status = "ok"
    summary = (
        f"No discrepancies found."
        if not discrepancies
        else f"Found {len(discrepancies)} discrepancy(ies) in casting check."
    )
    result = {"status": status, "discrepancies": discrepancies, "summary": summary}
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
