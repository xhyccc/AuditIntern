# RAG Legal Search — API Reference

## Function Signature

```python
from skills.rag_legal_search.scripts.skill_rag_legal_search import run

result = run(
    query="revenue recognition criteria",
    knowledge_base_path="knowledge_base/",
    output_path="results/rag_search_result.json"
)
```

## OpenCode CLI — Intent Name

`run_rag_search`

## Required Parameters

| Parameter             | Type   | Description                                              |
|-----------------------|--------|----------------------------------------------------------|
| `query`               | string | Natural-language search query                            |
| `knowledge_base_path` | string | Path to directory (`.txt`/`.md`) or a single file       |

## Optional Parameters

| Parameter     | Type   | Default                   | Description           |
|---------------|--------|---------------------------|-----------------------|
| `output_path` | string | `rag_search_result.json`  | JSON output file path |

## Indexing Behavior

| Mode          | Trigger                                   | Behavior                                              |
|---------------|-------------------------------------------|-------------------------------------------------------|
| Directory     | Path is a directory                       | Reads all `.txt` and `.md` files (non-recursive)      |
| Single file   | Path is a file                            | Reads and splits into paragraphs                      |
| Chunking      | Both modes                                | Split on double newlines (`\n\n`), empty chunks dropped |

## Retrieval Algorithm

| Setting          | Value                                |
|------------------|--------------------------------------|
| Vectorizer       | `TfidfVectorizer` (default settings) |
| Similarity       | Cosine similarity                    |
| Top-K            | 3 passages                           |
| Score threshold  | > 0 (zero-score passages not returned) |

## Output Fields

| Field      | Type           | Description                                   |
|------------|----------------|-----------------------------------------------|
| `answer`   | string         | Full text of the top-scoring passage          |
| `citations`| array          | Up to 3 passages with metadata               |
| `source`   | string         | Filename of the source document               |
| `score`    | float          | Cosine similarity [0.0–1.0]                  |
| `excerpt`  | string         | First 200 characters of the passage          |

## Dependencies

| Package       | Purpose                             |
|---------------|-------------------------------------|
| `scikit-learn`| TF-IDF vectorization, cosine similarity |
| `numpy`       | Score sorting                       |
