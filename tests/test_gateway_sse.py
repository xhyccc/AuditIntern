"""Tests for the Gateway SSE endpoint and static UI mount."""

import json
import urllib.parse

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.api.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_list_intents(client):
    r = client.get("/gateway/intents")
    assert r.status_code == 200
    intents = r.json()["intents"]
    assert "run_casting_check" in intents
    assert intents == sorted(intents)


def test_ui_is_served(client):
    r = client.get("/ui/")
    assert r.status_code == 200
    assert "AuditIntern Gateway" in r.text
    assert "EventSource" in r.text


def _parse_sse(text: str):
    """Parse a finished SSE stream into a list of (event, data) tuples."""
    events = []
    event = None
    data_lines = []
    for line in text.splitlines():
        if line.startswith("event: "):
            event = line[len("event: "):]
        elif line.startswith("data: "):
            data_lines.append(line[len("data: "):])
        elif line == "" and event is not None:
            events.append((event, json.loads("\n".join(data_lines))))
            event = None
            data_lines = []
    return events


def test_gateway_stream_happy_path(client, tmp_path):
    df = pd.DataFrame({"科目": ["A", "合计"], "Amount": [10.0, 10.0]})
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)
    out_path = tmp_path / "out.json"

    params = urllib.parse.quote(json.dumps({
        "file_path": str(csv_path),
        "output_path": str(out_path),
    }))
    r = client.get(f"/gateway/stream?intent=run_casting_check&params={params}")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    events = _parse_sse(r.text)
    names = [e[0] for e in events]
    assert names == ["started", "result", "done"]
    assert events[1][1]["status"] == "ok"
    assert events[2][1]["status"] == "ok"


def test_gateway_stream_invalid_params_json(client):
    r = client.get("/gateway/stream?intent=run_casting_check&params=not-json")
    assert r.status_code == 200
    events = _parse_sse(r.text)
    names = [e[0] for e in events]
    assert names == ["error", "done"]
    assert events[1][1]["status"] == "error"


def test_gateway_stream_params_must_be_object(client):
    r = client.get("/gateway/stream?intent=run_casting_check&params=[1,2,3]")
    events = _parse_sse(r.text)
    assert events[0][0] == "error"


def test_gateway_run_unknown_intent(client):
    r = client.post("/gateway/run", json={"intent": "nope", "params": {}})
    assert r.status_code == 200
    body = r.json()
    # Errors are sanitized: the generic message is returned rather than internals.
    assert body["status"] == "error"
