"""
Skill: Auto Mapping
Maps client trial balance accounts to standard chart of accounts using TF-IDF similarity.
"""

import json
import pathlib
import re
import unicodedata

import numpy as np
import pandas as pd


def _load_file(file_path: str) -> pd.DataFrame:
    path = pathlib.Path(file_path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path)


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text))
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def _tfidf_similarity(query: str, corpus: list[str]) -> list[float]:
    """Compute cosine similarity between query and each corpus item using TF-IDF."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        all_docs = [query] + corpus
        vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3))
        tfidf = vectorizer.fit_transform(all_docs)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        return sims.tolist()
    except Exception:
        # Fallback: simple character overlap ratio
        def _overlap(a: str, b: str) -> float:
            set_a, set_b = set(a), set(b)
            if not set_a or not set_b:
                return 0.0
            return len(set_a & set_b) / len(set_a | set_b)

        return [_overlap(query, c) for c in corpus]


def run(tb_file: str, standard_coa_file: str, output_path: str) -> dict:
    try:
        tb_df = _load_file(tb_file)
        coa_df = _load_file(standard_coa_file)
    except Exception as exc:
        result = {"status": "error", "mappings": [], "message": str(exc)}
        _write(output_path, result)
        return result

    # Find account_name column (case-insensitive)
    tb_col = next((c for c in tb_df.columns if "account" in c.lower() or "科目" in c), tb_df.columns[0])
    coa_col = next((c for c in coa_df.columns if "account" in c.lower() or "科目" in c), coa_df.columns[0])

    tb_accounts = tb_df[tb_col].dropna().astype(str).tolist()
    std_accounts = coa_df[coa_col].dropna().astype(str).tolist()
    std_normalized = [_normalize(a) for a in std_accounts]

    mappings = []
    for client_acct in tb_accounts:
        query = _normalize(client_acct)
        scores = _tfidf_similarity(query, std_normalized)
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        mappings.append(
            {
                "client_account": client_acct,
                "matched_standard": std_accounts[best_idx],
                "confidence": round(best_score, 4),
            }
        )

    result = {"status": "ok", "mappings": mappings}
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
