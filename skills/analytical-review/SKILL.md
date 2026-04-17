---
name: analytical-review
description: Performs analytical procedures comparing current vs prior period financial balances and flags significant variances. Use when the user asks to compare financial periods, perform analytical review, identify accounts with large changes, flag variances above a threshold, or analyze year-over-year or period-over-period movements in a trial balance.
---

# Analytical Review

Merges current-period and prior-period CSV/Excel files on the account column, computes
percentage and absolute changes, and flags accounts exceeding configurable thresholds
(default: 15% or ¥500,000).

## Script

`scripts/skill_analytical_review.py` — `run(current_file, prior_file, output_path, threshold_pct, threshold_amount) -> dict`
