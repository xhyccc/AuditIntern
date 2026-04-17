# AuditIntern

AI-assisted audit system with LLM, OCR, and rule-based engines.

## Architecture at a Glance

AuditIntern is a **thin Gateway** over a shared catalog of audit skills. The same
`INTENT_MAP` in `src/cli/main.py` is re-used by every front-door (CLI, HTTP/SSE
Gateway, MCP server), so the three entry paths stay in lock-step.

```mermaid
flowchart LR
    subgraph Clients
        UI["Browser UI<br/>(static/index.html)"]
        OC["opencode<br/>(LLM driver)"]
        CLIu["Terminal<br/>(stdin / --instruction)"]
    end

    subgraph Gateway["AuditIntern Gateway"]
        API["FastAPI server<br/>src/api/server.py<br/>/gateway/stream (SSE)"]
        MCP["MCP server<br/>src/mcp_server/server.py<br/>stdio JSON-RPC 2.0"]
        CLI["CLI orchestrator<br/>src/cli/main.py<br/>INTENT_MAP + dispatch()"]
    end

    subgraph Skills["Skill Catalog (skills/&lt;name&gt;/scripts/*.py)"]
        S1[casting-check]
        S2[fraud-detection]
        S3[auto-mapping]
        S4[cross-reference-check]
        S5[ocr-extraction]
        S6[llm-contract-parser]
        S7[rag-legal-search]
        S8[analytical-review]
        S9[wp-generator]
    end

    UI  -- "HTTP + SSE" --> API
    OC  -- "MCP stdio"  --> MCP
    CLIu -- "JSON on stdin" --> CLI

    API --> CLI
    MCP --> CLI
    CLI -->|"importlib loader<br/>(src/skills/__init__.py)"| Skills
```

### Request flow — browser → Gateway → skill (SSE)

```mermaid
sequenceDiagram
    autonumber
    participant B as Browser (static/index.html)
    participant A as FastAPI (/gateway/stream)
    participant C as CLI dispatch()
    participant S as Skill module
    B->>A: GET /gateway/stream?intent=...&params=...
    A->>A: Validate size (≤64 KiB) & parse JSON
    A-->>B: event: started
    A->>C: dispatch({intent, params})
    C->>S: INTENT_MAP[intent](params)
    S-->>C: result dict
    C-->>A: result
    A->>A: _sanitize_result (hide errors)
    A-->>B: event: result
    A-->>B: event: done
```

## Features

| Skill | Intent (`INTENT_MAP`) | What it does |
|---|---|---|
| 🧮 Casting Check | `run_casting_check` | Validate row/column totals in financial spreadsheets |
| 🕵️ Fraud Detection | `run_fraud_scan` | Benford's Law + rule-based journal entry analysis |
| 🔗 Auto Mapping | `run_auto_mapping` | NLP-based mapping of client accounts to standard COA |
| 🧾 Cross Reference Check | `run_cross_reference` | Validate consistency across multiple financial documents |
| 👁️ OCR Extraction | `run_ocr` | Extract text from images and PDFs |
| 📄 LLM Contract Parser | `run_contract_parse` | Extract structured fields from contracts using GPT |
| ⚖️ RAG Legal Search | `run_rag_search` | TF-IDF retrieval over legal knowledge bases |
| 📊 Analytical Review | `run_analytical_review` | Period-over-period variance analysis |
| 📝 Work Paper Generator | `run_wp_generate` | Fill Excel/Word templates with audit data |

## Tech Stack

```mermaid
flowchart TB
    subgraph Web["Web / API"]
        F[FastAPI]
        U[Uvicorn]
        P[Pydantic]
        H["Plain HTML + SSE<br/>(no framework)"]
    end
    subgraph Data["Data / Docs"]
        PD[pandas]
        NP[numpy]
        OX[openpyxl / xlsxwriter]
        DX[python-docx]
        J2[Jinja2]
    end
    subgraph ML["ML / NLP / OCR"]
        SK[scikit-learn]
        SP[scipy]
        ST[sentence-transformers]
        FS[faiss-cpu]
        OAI[openai]
        TS[pytesseract]
        PI[Pillow]
        PP[pdfplumber]
    end
    subgraph Integration["Integration"]
        MC["MCP (JSON-RPC 2.0 over stdio)"]
        OCb["opencode CLI"]
    end
    subgraph Test["Testing"]
        PT[pytest]
        HX[httpx]
    end
```

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
AuditIntern/
├── src/
│   ├── cli/          # CLI orchestrator — defines INTENT_MAP + dispatch()
│   ├── skills/       # Dynamic loader (importlib) — re-exports skills/*/scripts
│   ├── mcp_server/   # MCP server exposing skills to opencode over stdio
│   ├── api/          # FastAPI backend + Gateway SSE endpoint (/gateway/stream)
│   └── utils/        # Project / session management
├── skills/           # Skill catalog (Anthropic-style: SKILL.md + scripts/ + assets/)
│   ├── casting-check/
│   ├── fraud-detection/
│   ├── auto-mapping/
│   ├── cross-reference-check/
│   ├── ocr-extraction/
│   ├── llm-contract-parser/
│   ├── rag-legal-search/
│   ├── analytical-review/
│   └── wp-generator/
├── static/           # Gateway frontend (plain HTML + SSE, served at /ui)
├── scripts/          # install-opencode.sh and friends
├── tests/            # Pytest test suite
├── requirements.txt
├── pyproject.toml
└── SKILLS.md         # Full per-skill input/output reference
```

### How the three front-doors stay in sync

```mermaid
flowchart LR
    subgraph SOT["Single source of truth"]
        IM["INTENT_MAP<br/>(src/cli/main.py)"]
    end
    IM --> CLI_FD["CLI front-door<br/>python -m src.cli.main"]
    IM --> API_FD["HTTP/SSE front-door<br/>/gateway/intents<br/>/gateway/run<br/>/gateway/stream"]
    IM --> MCP_FD["MCP front-door<br/>tools/list & tools/call"]
```

Adding a new skill is a 3-step change: drop a module under
`skills/<name>/scripts/skill_<name>.py`, register it in `src/skills/__init__.py`'s
`_SKILL_MAP`, and add an entry to `INTENT_MAP` (plus a description in
`src/mcp_server/server.py`'s `_TOOL_DESCRIPTIONS`). All three front-doors pick
it up automatically.
