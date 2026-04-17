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

### Gateway UI (plain HTML + SSE)

Once the API server is running, open <http://localhost:8000/ui/> for the
built-in Gateway frontend: pick an intent, edit the `params` JSON, and watch
`started` / `result` / `done` events stream in via SSE. The same intents are
also served to the `opencode` LLM driver through the MCP server below, so the
full data path is:

```
opencode → MCP (src/mcp_server) → src/skills/*
browser  → Gateway SSE (/gateway/stream) → src/skills/*
```

### MCP Server (for opencode)

Expose every skill as an MCP tool over stdio:

```bash
python -m src.mcp_server.server
```

Point your `opencode` config at that command to let the LLM call skills
directly. Tool names match `INTENT_MAP` in `src/cli/main.py`; each tool takes
a single `params` object forwarded verbatim to the skill.

## Testing

```bash
pytest tests/ -v
```

## Installing the opencode Binary

The Gateway orchestrator uses the [opencode](https://opencode.ai) CLI as the
LLM "brain" that calls our skills through an MCP server. To install it in CI
or any runtime environment, run:

```bash
# latest
bash scripts/install-opencode.sh

# pin a specific version
OPENCODE_VERSION=0.3.0 bash scripts/install-opencode.sh
```

The script is idempotent (skips the download if `opencode` is already on
`PATH`), installs to `~/.opencode/bin` by default, and — when running under
GitHub Actions — appends that directory to `$GITHUB_PATH` so later steps can
invoke `opencode` directly. The provided `.github/workflows/ci.yml` caches
`~/.opencode` across runs.

## Skills Reference

See [SKILLS.md](SKILLS.md) for full documentation of all available skills.

## Project Structure

```
src/
├── cli/          # CLI orchestrator
├── skills/       # Skill loader (scripts live in top-level skills/)
├── mcp_server/   # MCP server exposing skills to opencode over stdio
├── api/          # FastAPI backend + Gateway SSE endpoint
└── utils/        # Project/session management
static/           # Gateway frontend (plain HTML + SSE, served at /ui)
tests/            # Pytest test suite
```
