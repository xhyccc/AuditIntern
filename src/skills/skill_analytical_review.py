"""
Skill: Analytical Review
Performs analytical procedures comparing current vs prior period financial balances.
"""

import json
import pathlib

import numpy as np
import pandas as pd


def _load_file(file_path: str) -> pd.DataFrame:
    path = pathlib.Path(file_path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def run(
    current_file: str,
    prior_file: str,
    output_path: str,
    threshold_pct: float = 15.0,
    threshold_amount: float = 500000,
) -> dict:
    try:
        cur_df = _load_file(current_file)
        pri_df = _load_file(prior_file)
    except Exception as exc:
        result = {"status": "error", "flagged_accounts": [], "narrative": str(exc)}
        _write(output_path, result)
        return result

    acct_col_cur = next((c for c in cur_df.columns if "account" in c.lower() or "科目" in c), cur_df.columns[0])
    amt_col_cur = next((c for c in cur_df.columns if "amount" in c.lower() or "金额" in c), cur_df.columns[1])
    acct_col_pri = next((c for c in pri_df.columns if "account" in c.lower() or "科目" in c), pri_df.columns[0])
    amt_col_pri = next((c for c in pri_df.columns if "amount" in c.lower() or "金额" in c), pri_df.columns[1])

    cur_df = cur_df[[acct_col_cur, amt_col_cur]].rename(columns={acct_col_cur: "account", amt_col_cur: "current"})
    pri_df = pri_df[[acct_col_pri, amt_col_pri]].rename(columns={acct_col_pri: "account", amt_col_pri: "prior"})

    cur_df["current"] = pd.to_numeric(cur_df["current"], errors="coerce")
    pri_df["prior"] = pd.to_numeric(pri_df["prior"], errors="coerce")

    merged = pd.merge(cur_df, pri_df, on="account", how="outer").fillna(0)
    merged["change_amount"] = merged["current"] - merged["prior"]
    merged["change_pct"] = merged.apply(
        lambda r: (r["change_amount"] / abs(r["prior"]) * 100) if r["prior"] != 0 else (100.0 if r["current"] != 0 else 0.0),
        axis=1,
    )

    flagged = merged[
        (merged["change_pct"].abs() >= threshold_pct) | (merged["change_amount"].abs() >= threshold_amount)
    ]

    flagged_accounts = []
    for _, row in flagged.iterrows():
        flagged_accounts.append(
            {
                "account": row["account"],
                "current": round(float(row["current"]), 2),
                "prior": round(float(row["prior"]), 2),
                "change_pct": round(float(row["change_pct"]), 2),
                "change_amount": round(float(row["change_amount"]), 2),
            }
        )

    narrative = (
        f"Analytical review identified {len(flagged_accounts)} account(s) with significant variances "
        f"(threshold: {threshold_pct}% or ¥{threshold_amount:,.0f})."
    )

    result = {"status": "ok", "flagged_accounts": flagged_accounts, "narrative": narrative}
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
