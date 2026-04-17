# Auto Mapping — API Reference

## Function Signature

```python
from skills.auto_mapping.scripts.skill_auto_mapping import run

result = run(
    tb_file="data/client_trial_balance.csv",
    standard_coa_file="data/standard_coa.csv",
    output_path="results/auto_mapping_result.json"
)
```

## OpenCode CLI — Intent Name

`run_auto_mapping`

## Required Parameters

| Parameter           | Type   | Description                                 |
|---------------------|--------|---------------------------------------------|
| `tb_file`           | string | Path to client trial balance (CSV or Excel) |
| `standard_coa_file` | string | Path to standard COA file (CSV or Excel)    |

## Optional Parameters

| Parameter     | Type   | Default                    | Description           |
|---------------|--------|----------------------------|-----------------------|
| `output_path` | string | `auto_mapping_result.json` | JSON output file path |

## Column Detection

Account name columns are detected by (in order):
1. Column name containing `account` (case-insensitive)
2. Column name containing `科目`
3. First column (fallback)

## Similarity Algorithm

| Setting       | Value                    |
|---------------|--------------------------|
| Vectorizer    | `TfidfVectorizer`        |
| Analyzer      | `char_wb`                |
| N-gram range  | (2, 3) — bigrams/trigrams |
| Similarity    | Cosine similarity        |
| Fallback      | Jaccard character overlap |

## Normalization

Before comparison, all account names are:
1. Unicode NFKC normalized
2. Lowercased
3. Whitespace collapsed to single space
4. Leading/trailing whitespace stripped

## Dependencies

| Package      | Purpose                        |
|--------------|--------------------------------|
| `pandas`     | File reading                   |
| `numpy`      | argmax for best match          |
| `scikit-learn` | TF-IDF vectorization, cosine similarity |
