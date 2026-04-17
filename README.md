# AuditIntern

AI-assisted audit system with LLM, OCR, and rule-based engines.

## Features

- **Casting Check** – Validate row/column totals in financial spreadsheets
- **Fraud Detection** – Benford's Law + rule-based journal entry analysis
- **Auto Mapping** – NLP-based mapping of client accounts to standard COA
- **Cross Reference Check** – Validate consistency across multiple financial documents
- **OCR Extraction** – Extract text from images and PDFs
- **LLM Contract Parser** – Extract structured fields from contracts using GPT
- **RAG Legal Search** – TF-IDF retrieval over legal knowledge bases
- **Analytical Review** – Period-over-period variance analysis
- **Work Paper Generator** – Fill Excel/Word templates with audit data

## Quick Start

```bash
pip install -r requirements.txt
```

### CLI Usage

```bash
# From stdin
echo '{"intent": "run_casting_check", "params": {"file_path": "data.csv", "output_path": "result.json"}}' \
  | python -m src.cli.main

# From instruction file
python -m src.cli.main --instruction instruction.json
```

### API Server

```bash
uvicorn src.api.server:app --reload
```

API docs at http://localhost:8000/docs

## Testing

```bash
pytest tests/ -v
```

## Skills Reference

See [SKILLS.md](SKILLS.md) for full documentation of all available skills.

## Project Structure

```
src/
├── cli/          # CLI orchestrator
├── skills/       # Individual skill scripts
├── api/          # FastAPI backend
└── utils/        # Project/session management
tests/            # Pytest test suite
```
