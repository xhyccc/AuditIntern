"""
Project and Session management for the audit system.
Provides sandbox isolation per project and context persistence per session.
"""

import json
import pathlib
import uuid
from datetime import datetime, timezone


class ProjectManager:
    """Manages audit projects as file-system directories."""

    def __init__(self, base_dir: str = "audit_data/projects"):
        self.base_dir = pathlib.Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, description: str = "") -> dict:
        project_id = str(uuid.uuid4())
        project_dir = self.base_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "project_id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "path": str(project_dir),
        }
        (project_dir / "project.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return meta

    def get_project(self, project_id: str) -> dict | None:
        project_dir = self.base_dir / project_id
        meta_file = project_dir / "project.json"
        if not meta_file.exists():
            return None
        return json.loads(meta_file.read_text(encoding="utf-8"))

    def safe_path(self, project_id: str, relative_path: str) -> pathlib.Path:
        """Resolve a path within the project sandbox, preventing directory traversal."""
        project_dir = (self.base_dir / project_id).resolve()
        target = (project_dir / relative_path).resolve()
        if not target.is_relative_to(project_dir):
            raise PermissionError(f"Path '{relative_path}' is outside project sandbox.")
        return target


class SessionManager:
    """Manages sessions within a project directory."""

    def __init__(self, project_path: str):
        self.sessions_dir = pathlib.Path(project_path) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, name: str = "default") -> dict:
        session_id = str(uuid.uuid4())
        session_dir = self.sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        meta = {
            "session_id": session_id,
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        (session_dir / "session.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return meta

    def session_exists(self, session_id: str) -> bool:
        return (self.sessions_dir / session_id / "session.json").exists()

    def get_session(self, session_id: str) -> dict | None:
        meta_file = self.sessions_dir / session_id / "session.json"
        if not meta_file.exists():
            return None
        return json.loads(meta_file.read_text(encoding="utf-8"))

    def save_context(self, session_id: str, context: dict) -> None:
        session_dir = self.sessions_dir / session_id
        (session_dir / "context.json").write_text(
            json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load_context(self, session_id: str) -> dict:
        ctx_file = self.sessions_dir / session_id / "context.json"
        if not ctx_file.exists():
            return {}
        return json.loads(ctx_file.read_text(encoding="utf-8"))

    def save_result(self, session_id: str, task_id: str, result: dict) -> None:
        results_dir = self.sessions_dir / session_id / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / f"{task_id}.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_result(self, session_id: str, task_id: str) -> dict | None:
        result_file = self.sessions_dir / session_id / "results" / f"{task_id}.json"
        if not result_file.exists():
            return None
        return json.loads(result_file.read_text(encoding="utf-8"))
