---
name: rag-legal-search
description: Retrieves relevant legal or regulatory passages from a local knowledge base using TF-IDF similarity search. Use when the user asks to search regulations, look up audit standards, find relevant clauses in a document library, retrieve passages from legal texts, query compliance requirements, or find references to specific accounting rules in a collection of text or markdown files.
---

# RAG Legal Search

## Overview

The **RAG legal search** skill implements a lightweight retrieval-augmented generation (RAG) pattern using TF-IDF similarity — without requiring an external vector database or embedding API. It indexes a local collection of `.txt` or `.md` documents (or a single file), splits them into paragraphs, and retrieves the top-K most relevant passages for a natural-language query using cosine similarity.

This is ideal for:
- Searching internal audit manuals or policy documents
- Looking up specific clauses in accounting standards (IFRS, GAAP, CAS)
- Retrieving regulatory requirements relevant to an audit finding
- Building a precedent library from past audit reports

---

## OpenCode CLI Invocation

### Search a directory of documents

```bash
echo '{
  "intent": "run_rag_search",
  "params": {
    "query": "revenue recognition criteria under IFRS 15",
    "knowledge_base_path": "knowledge_base/accounting_standards/",
    "output_path": "results/rag_search_result.json"
  }
}' | python -m src.cli.main
```

### Search a single file

```bash
echo '{
  "intent": "run_rag_search",
  "params": {
    "query": "related party transaction disclosure requirements",
    "knowledge_base_path": "knowledge_base/ias_24.txt",
    "output_path": "results/rag_search_result.json"
  }
}' | python -m src.cli.main
```

### Via instruction file

`rag_instruction.json`:
```json
{
  "intent": "run_rag_search",
  "params": {
    "query": "impairment testing goodwill",
    "knowledge_base_path": "knowledge_base/",
    "output_path": "results/rag_search_result.json"
  }
}
```

```bash
python -m src.cli.main --instruction rag_instruction.json
```

### Via REST API

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "run_rag_search",
    "params": {
      "query": "going concern indicators",
      "knowledge_base_path": "knowledge_base/audit_standards/"
    }
  }'
```

---

## Parameters

| Parameter              | Type   | Required | Default                     | Description                                                  |
|------------------------|--------|----------|-----------------------------|--------------------------------------------------------------|
| `query`                | string | ✅ Yes   | —                           | Natural-language search query                                |
| `knowledge_base_path`  | string | ✅ Yes   | —                           | Path to directory (`.txt`/`.md` files) or a single file     |
| `output_path`          | string | No       | `rag_search_result.json`    | Path to write the JSON result report                         |

---

## Knowledge Base Format

**Directory mode**: the skill reads all `.txt` and `.md` files in the specified directory (non-recursive). Each file is split into paragraphs on double newlines (`\n\n`).

**Single file mode**: the file is split into paragraphs similarly.

Example knowledge base structure:
```
knowledge_base/
├── ifrs_15_revenue.txt
├── ias_36_impairment.txt
├── audit_manual.md
└── company_policies.md
```

---

## Output Schema

```json
{
  "status": "ok",
  "answer": "Revenue shall be recognised when (or as) the entity satisfies a performance obligation by transferring a promised good or service...",
  "citations": [
    {
      "source": "ifrs_15_revenue.txt",
      "score": 0.7341,
      "excerpt": "Revenue shall be recognised when (or as) the entity satisfies a performance obligation..."
    },
    {
      "source": "audit_manual.md",
      "score": 0.5102,
      "excerpt": "For revenue recognition testing, auditors should obtain management's analysis of..."
    }
  ]
}
```

| Field       | Description                                                               |
|-------------|---------------------------------------------------------------------------|
| `status`    | `"ok"` always (returns empty citations if no documents found)            |
| `answer`    | Text of the top-scoring passage                                           |
| `citations` | Top-3 passages by relevance, each with source filename, score, excerpt   |
| `score`     | TF-IDF cosine similarity [0.0–1.0]                                        |
| `excerpt`   | First 200 characters of the passage                                       |

---

## Building a Good Knowledge Base

| Content type               | Recommended format | Tips                                      |
|----------------------------|--------------------|-------------------------------------------|
| Accounting standards       | `.txt`             | One standard per file; separate articles with blank lines |
| Audit procedures manual    | `.md`              | Use headings; each section as a paragraph |
| Regulatory circulars       | `.txt`             | Strip headers/footers before adding       |
| Past audit findings        | `.md`              | One finding per paragraph                 |

---

## Notes & Edge Cases

- **Top-K**: returns up to 3 passages with similarity score > 0. If no passage has a positive score, `citations` is empty.
- **No scikit-learn**: if scikit-learn is unavailable, the skill returns an empty citations list (no fallback search).
- **File encoding**: files are read as UTF-8 with error tolerance (`errors="ignore"`).
- **Non-.txt/.md files**: only `.txt` and `.md` are indexed; other files in the directory are silently skipped.

---

## Script

`scripts/skill_rag_legal_search.py` — `run(query: str, knowledge_base_path: str, output_path: str) -> dict`
