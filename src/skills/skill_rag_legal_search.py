"""
Skill: RAG Legal Search
Retrieves relevant legal/regulatory passages from a knowledge base using TF-IDF similarity.
"""

import json
import os
import pathlib


def _load_documents(knowledge_base_path: str) -> list[dict]:
    kb_path = pathlib.Path(knowledge_base_path)
    docs = []
    if kb_path.is_file():
        text = kb_path.read_text(encoding="utf-8", errors="ignore")
        # Split by paragraph
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for i, para in enumerate(paragraphs):
            docs.append({"source": kb_path.name, "chunk_id": i, "text": para})
    elif kb_path.is_dir():
        for f in kb_path.iterdir():
            if f.suffix.lower() in {".txt", ".md"}:
                text = f.read_text(encoding="utf-8", errors="ignore")
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                for i, para in enumerate(paragraphs):
                    docs.append({"source": f.name, "chunk_id": i, "text": para})
    return docs


def _tfidf_search(query: str, docs: list[dict], top_k: int = 3) -> list[dict]:
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        corpus = [d["text"] for d in docs]
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(corpus + [query])
        scores = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {**docs[i], "score": round(float(scores[i]), 4)}
            for i in top_indices
            if scores[i] > 0
        ]
    except Exception:
        return []


def run(query: str, knowledge_base_path: str, output_path: str) -> dict:
    docs = _load_documents(knowledge_base_path)
    if not docs:
        result = {
            "status": "ok",
            "answer": "No documents found in knowledge base.",
            "citations": [],
        }
        _write(output_path, result)
        return result

    hits = _tfidf_search(query, docs)
    answer = hits[0]["text"] if hits else "No relevant passage found."
    citations = [
        {"source": h["source"], "score": h["score"], "excerpt": h["text"][:200]}
        for h in hits
    ]

    result = {"status": "ok", "answer": answer, "citations": citations}
    _write(output_path, result)
    return result


def _write(output_path: str, data: dict) -> None:
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
