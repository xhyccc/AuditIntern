"""
FastAPI backend server for the AI Audit System.
Provides REST endpoints for project/session management and task dispatch.
"""

import json
import uuid
import pathlib
import subprocess
import sys
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from src.utils.project_manager import ProjectManager, SessionManager

app = FastAPI(title="AuditIntern API", version="0.1.0")

_project_manager = ProjectManager()


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

    sm.save_result(session_id, task_id, result)
    return {"task_id": task_id, "status": "completed", "result": result}


@app.get("/sessions/{session_id}/results/{task_id}")
def get_result(session_id: str, task_id: str):
    sm = _find_session_manager(session_id)
    if sm is None:
        raise HTTPException(status_code=404, detail="Session not found")
    result = sm.get_result(session_id, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@app.post("/upload/{project_id}", status_code=201)
async def upload_file(project_id: str, file: UploadFile = File(...)):
    project = _project_manager.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    uploads_dir = pathlib.Path(project["path"]) / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    dest = uploads_dir / file.filename
    content = await file.read()
    dest.write_bytes(content)
    return {"filename": file.filename, "path": str(dest), "size": len(content)}


# ---- Helpers ----

def _dispatch_instruction(instruction: dict) -> dict:
    """Dispatch instruction to the CLI and return the result."""
    from src.cli.main import dispatch
    return dispatch(instruction)


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
