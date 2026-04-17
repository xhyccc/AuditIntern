"""
FastAPI backend server for the AI Audit System.
Provides REST endpoints for project/session management and task dispatch.
"""

import json
import re
import uuid
import pathlib
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.utils.project_manager import ProjectManager, SessionManager

app = FastAPI(title="AuditIntern API", version="0.1.0")

_project_manager = ProjectManager()

# Mount the Gateway UI (plain HTML + SSE) at /ui.
_STATIC_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(_STATIC_DIR), html=True), name="ui")


# ---- Request / Response Models ----

class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""


class CreateSessionRequest(BaseModel):
    name: str = "default"


class SubmitTaskRequest(BaseModel):
    intent: str
    params: dict[str, Any] = {}


# ---- Endpoints ----

@app.post("/projects", status_code=201)
def create_project(body: CreateProjectRequest):
    project = _project_manager.create_project(body.name, body.description)
    return project


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    project = _project_manager.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/projects/{project_id}/sessions", status_code=201)
def create_session(project_id: str, body: CreateSessionRequest):
    project = _project_manager.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    sm = SessionManager(project["path"])
    session = sm.create_session(body.name)
    return session


@app.post("/sessions/{session_id}/tasks", status_code=202)
def submit_task(session_id: str, body: SubmitTaskRequest):
    # Find session across all projects
    sm = _find_session_manager(session_id)
    if sm is None:
        raise HTTPException(status_code=404, detail="Session not found")

    task_id = str(uuid.uuid4())
    instruction = {"intent": body.intent, "params": body.params}

    # Run synchronously (for simplicity - production would use a task queue)
    result = _dispatch_instruction(instruction)

    # Sanitize before storing and before returning to prevent stack trace exposure
    safe_result = _sanitize_result(result)
    sm.save_result(session_id, task_id, safe_result)
    return {"task_id": task_id, "status": "completed", "result": safe_result}


@app.get("/sessions/{session_id}/results/{task_id}")
def get_result(session_id: str, task_id: str):
    sm = _find_session_manager(session_id)
    if sm is None:
        raise HTTPException(status_code=404, detail="Session not found")
    result = sm.get_result(session_id, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return _sanitize_result(result)


@app.post("/upload/{project_id}", status_code=201)
async def upload_file(project_id: str, file: UploadFile = File(...)):
    project = _project_manager.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    uploads_dir = pathlib.Path(project["path"]) / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = re.sub(r"[^\w.\-]", "_", pathlib.Path(file.filename).name)
    dest = uploads_dir / safe_filename
    content = await file.read()
    dest.write_bytes(content)
    return {"filename": safe_filename, "path": str(dest), "size": len(content)}


# ---- Gateway: SSE streaming endpoint ----

@app.get("/gateway/intents")
def list_intents():
    """List the intents the Gateway can dispatch (mirrors MCP tools/list)."""
    from src.cli.main import INTENT_MAP
    return {"intents": sorted(INTENT_MAP.keys())}


@app.post("/gateway/run")
def gateway_run(body: SubmitTaskRequest):
    """Run an intent once and return the sanitized result (no session required)."""
    result = _dispatch_instruction({"intent": body.intent, "params": body.params})
    return _sanitize_result(result)


@app.get("/gateway/stream")
def gateway_stream(intent: str, params: str = "{}"):
    """Server-Sent Events endpoint that streams lifecycle events for a single intent.

    Query params:
        intent: intent name (see /gateway/intents)
        params: JSON-encoded params object (default "{}"); max 64 KiB.

    Emits three events: ``started``, ``result``, ``done``. All payloads are
    JSON. Errors in parsing or dispatch surface as an ``error`` event.
    """
    # Bound the input to protect against oversized payloads.
    if len(params) > 64 * 1024:
        def _too_big():
            yield _sse("error", {"message": "'params' exceeds 64 KiB limit"})
            yield _sse("done", {"status": "error"})
        return StreamingResponse(_too_big(), media_type="text/event-stream")

    try:
        parsed_params = json.loads(params)
        if not isinstance(parsed_params, dict):
            raise ValueError("params must be a JSON object")
    except (json.JSONDecodeError, ValueError):
        # Stream a generic parse error (no exception detail) so we don't leak
        # parser internals to callers.
        def _err_gen():
            yield _sse("error", {"message": "Invalid 'params': expected a JSON object"})
            yield _sse("done", {"status": "error"})

        return StreamingResponse(_err_gen(), media_type="text/event-stream")

    def _gen():
        yield _sse("started", {"intent": intent})
        result = _dispatch_instruction({"intent": intent, "params": parsed_params})
        safe_result = _sanitize_result(result)
        yield _sse("result", safe_result)
        yield _sse("done", {"status": safe_result.get("status", "ok")})

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---- Helpers ----

def _sse(event: str, data: Any) -> str:
    """Format one Server-Sent Events message."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _dispatch_instruction(instruction: dict) -> dict:
    """Dispatch instruction to the CLI and return the result."""
    from src.cli.main import dispatch
    return dispatch(instruction)


def _sanitize_result(result: dict) -> dict:
    """Remove or truncate detailed error messages before exposing to API callers."""
    if result.get("status") == "error":
        return {"status": "error", "message": "Task failed. Check server logs for details."}
    return result


def _find_session_manager(session_id: str):
    """Search all projects for the given session."""
    base = _project_manager.base_dir
    for project_dir in base.iterdir():
        if not project_dir.is_dir():
            continue
        sm = SessionManager(str(project_dir))
        if sm.session_exists(session_id):
            return sm
    return None
