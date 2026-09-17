import os
import subprocess
import uuid
from datetime import datetime, timezone
from omni_core.db import get_connection, init_db

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def is_pid_alive(pid: int) -> bool:
    """Checks if a process ID is actively running on the system."""
    if not pid or pid <= 0:
        return False
    if HAS_PSUTIL:
        return psutil.pid_exists(pid)
    try:
        # On Windows, tasklist can verify PID without psutil
        out = subprocess.check_output(f'tasklist /FI "PID eq {pid}"', shell=True, text=True, stderr=subprocess.DEVNULL)
        return str(pid) in out
    except Exception:
        return False

def register_session(project_id: str, agent_id: str, pid: int, command: str, log_path: str = "") -> dict:
    """Records a new active agent/project process session."""
    init_db()
    sid = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sessions (id, project_id, agent_id, pid, status, start_time, log_path, command)
        VALUES (?, ?, ?, ?, 'running', ?, ?, ?)
        """, (sid, project_id or "", agent_id or "", pid, now, log_path or "", command or ""))
        conn.commit()
    return {
        "id": sid,
        "project_id": project_id,
        "agent_id": agent_id,
        "pid": pid,
        "status": "running",
        "start_time": now,
        "log_path": log_path,
        "command": command
    }

def list_sessions(active_only: bool = False) -> list[dict]:
    """Lists registered sessions, refreshing their live process status."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC LIMIT 50")
        rows = [dict(r) for r in cursor.fetchall()]
        
    updated = []
    with get_connection() as conn:
        cursor = conn.cursor()
        for s in rows:
            pid = s.get("pid")
            alive = is_pid_alive(pid) if pid else False
            new_status = "running" if alive else "stopped"
            if s["status"] == "running" and not alive:
                cursor.execute("UPDATE sessions SET status = 'stopped', end_time = ? WHERE id = ?",
                               (datetime.now(timezone.utc).isoformat(), s["id"]))
                s["status"] = "stopped"
            if not active_only or alive:
                updated.append(s)
        conn.commit()
    return updated

def terminate_session(session_id: str) -> tuple[bool, str]:
    """Terminates an active session's process on Windows."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return False, f"Session {session_id} not found"
        s = dict(row)
        pid = s.get("pid")
        if not pid or not is_pid_alive(pid):
            cursor.execute("UPDATE sessions SET status = 'stopped' WHERE id = ?", (session_id,))
            conn.commit()
            return True, f"Session {session_id} was already stopped"
            
        try:
            if HAS_PSUTIL:
                p = psutil.Process(pid)
                p.terminate()
            else:
                subprocess.run(f"taskkill /PID {pid} /F /T", shell=True, capture_output=True)
            cursor.execute("UPDATE sessions SET status = 'stopped', end_time = ? WHERE id = ?",
                           (datetime.now(timezone.utc).isoformat(), session_id))
            conn.commit()
            return True, f"Terminated process PID {pid} for session {session_id}"
        except Exception as e:
            return False, f"Failed to terminate PID {pid}: {e}"
