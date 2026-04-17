"""
Minimal MCP (Model Context Protocol) server for AuditIntern.

Speaks MCP over stdio using line-delimited JSON-RPC 2.0.
Exposes every intent registered in ``src.cli.main.INTENT_MAP`` as an MCP tool,
so that opencode (or any other MCP client) can call them with:

    opencode → MCP (this process) → src/skills/*

We implement the protocol by hand to avoid pulling in an extra runtime
dependency. Only the subset needed for tool discovery and invocation is
handled: ``initialize``, ``tools/list``, ``tools/call`` (plus ``ping`` and a
generic ``notifications/*`` no-op).

Run with:

    python -m src.mcp_server.server
"""

from __future__ import annotations

import json
import sys
import traceback
from typing import Any

from src.cli.main import INTENT_MAP, dispatch

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "auditintern-mcp"
SERVER_VERSION = "0.1.0"


# --- Tool schema ---------------------------------------------------------
#
# Each intent becomes a tool whose input schema documents the parameters the
# underlying skill expects. We keep the schema conservative (JSON Schema
# "object" with a permissive "params" bag) so changes to the skills don't
# require regenerating the schema -- the skill itself raises a clear error
# for missing keys and ``dispatch`` turns that into an MCP error.

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "run_casting_check": "Validate row/column totals in a financial spreadsheet (CSV/XLSX).",
    "run_fraud_scan": "Run Benford's Law + rule-based fraud detection on journal entries.",
    "run_auto_mapping": "Map client trial-balance accounts to a standard chart of accounts.",
    "run_cross_reference": "Check consistency of values across multiple financial documents.",
    "run_ocr": "Extract text from an image or PDF using OCR.",
    "run_contract_parse": "Use an LLM to extract structured fields from contract text.",
    "run_rag_search": "TF-IDF retrieval over a legal knowledge base.",
    "run_analytical_review": "Period-over-period variance analysis with thresholds.",
    "run_wp_generate": "Fill Excel/Word working-paper templates with audit data.",
}


def _tool_schema(intent: str) -> dict[str, Any]:
    return {
        "name": intent,
        "description": _TOOL_DESCRIPTIONS.get(intent, f"AuditIntern skill: {intent}"),
        "inputSchema": {
            "type": "object",
            "properties": {
                "params": {
                    "type": "object",
                    "description": (
                        "Parameters forwarded to the skill. See SKILLS.md for the "
                        "exact keys each skill expects."
                    ),
                    "additionalProperties": True,
                }
            },
            "required": ["params"],
            "additionalProperties": False,
        },
    }


def list_tools() -> list[dict[str, Any]]:
    return [_tool_schema(intent) for intent in INTENT_MAP]


# --- JSON-RPC helpers ----------------------------------------------------

def _response(msg_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    """Dispatch a single JSON-RPC message.

    Returns the response dict, or ``None`` for notifications (no response).
    """
    method = message.get("method")
    msg_id = message.get("id")
    params = message.get("params") or {}

    # Notifications carry no id and expect no response.
    is_notification = "id" not in message

    if method == "initialize":
        return _response(
            msg_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        )

    if method == "ping":
        return _response(msg_id, {})

    if method == "tools/list":
        return _response(msg_id, {"tools": list_tools()})

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if name not in INTENT_MAP:
            return _error(msg_id, -32602, f"Unknown tool: {name!r}")

        tool_params = arguments.get("params", {})
        if not isinstance(tool_params, dict):
            return _error(msg_id, -32602, "'params' must be an object")

        try:
            result = dispatch({"intent": name, "params": tool_params})
        except Exception:  # noqa: BLE001 -- defensive; dispatch already catches, but stay safe
            traceback.print_exc(file=sys.stderr)
            return _error(msg_id, -32603, "Internal server error. See server logs.")

        is_error = result.get("status") == "error"
        return _response(
            msg_id,
            {
                "content": [
                    {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                ],
                "isError": is_error,
            },
        )

    # Accept and silently ignore standard notification methods.
    if is_notification:
        return None

    return _error(msg_id, -32601, f"Method not found: {method}")


# --- stdio loop ----------------------------------------------------------

def serve_stdio(stdin=None, stdout=None) -> None:
    """Run the MCP server on line-delimited JSON over stdio."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout

    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            # Can't map a broken frame to an id; log and continue.
            print(f"[mcp] failed to parse frame: {line!r}", file=sys.stderr)
            continue

        response = handle_request(message)
        if response is None:
            continue
        stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        stdout.flush()


def main() -> None:
    serve_stdio()


if __name__ == "__main__":
    main()
