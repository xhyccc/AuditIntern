---
name: rag-legal-search
description: Retrieves relevant legal or regulatory passages from a local knowledge base using TF-IDF similarity search. Use when the user asks to search legal documents, look up regulations, find relevant clauses in a knowledge base, query audit standards, or retrieve passages from a text or markdown document collection.
---

# RAG Legal Search

Loads documents from a directory (`.txt` / `.md`) or a single file and indexes them with
TF-IDF. Returns the top matching passages and citation metadata for a natural-language query.

## Script

`scripts/skill_rag_legal_search.py` — `run(query, knowledge_base_path, output_path) -> dict`
