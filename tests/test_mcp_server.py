"""Tests for the stdio MCP server (src.mcp_server.server)."""

import json
import pathlib
import subprocess
import sys

import pandas as pd

from src.mcp_server.server import handle_request, list_tools

_REPO_ROOT = pathlib.Path(__file__).parent.parent


def test_list_tools_covers_all_intents():
    from src.cli.main import INTENT_MAP

    tools = list_tools()
    names = {t["name"] for t in tools}
    assert names == set(INTENT_MAP.keys())
    for tool in tools:
        assert tool["inputSchema"]["type"] == "object"
        assert "params" in tool["inputSchema"]["properties"]


def test_handle_initialize():
    resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "auditintern-mcp"
    assert "protocolVersion" in resp["result"]


def test_handle_unknown_tool():
    resp = handle_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "nope", "arguments": {"params": {}}},
    })
    assert "error" in resp
    assert "Unknown tool" in resp["error"]["message"]


def test_handle_notification_returns_none():
    # No 'id' => notification => no response.
    assert handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_tool_call_round_trip_via_stdio(tmp_path):
    """Drive the server as a real subprocess: initialize → tools/call → parse result."""
    df = pd.DataFrame({"科目": ["A", "合计"], "Amount": [42.0, 42.0]})
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)
    out_path = tmp_path / "out.json"

    frames = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "run_casting_check",
                "arguments": {"params": {"file_path": str(csv_path), "output_path": str(out_path)}},
            },
        },
    ]
    stdin = "\n".join(json.dumps(f) for f in frames) + "\n"

    proc = subprocess.run(
        [sys.executable, "-m", "src.mcp_server.server"],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        timeout=20,
    )
    assert proc.returncode == 0, proc.stderr

    responses = [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]
    assert len(responses) == 3

    init_resp, list_resp, call_resp = responses
    assert init_resp["result"]["serverInfo"]["name"] == "auditintern-mcp"
    assert any(t["name"] == "run_casting_check" for t in list_resp["result"]["tools"])

    call_result = call_resp["result"]
    assert call_result["isError"] is False
    payload = json.loads(call_result["content"][0]["text"])
    assert payload["status"] == "ok"
