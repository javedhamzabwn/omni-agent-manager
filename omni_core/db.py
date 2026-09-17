import sqlite3
import json
import os
import time
import uuid
from datetime import datetime, timezone
from omni_core.paths import OMNI_DB_PATH, OMNI_PROJECTS_JSON, normalize_path

def get_connection() -> sqlite3.Connection:
    """Returns a thread-safe sqlite3 connection configured with WAL mode."""
    conn = sqlite3.connect(OMNI_DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    """Initializes the database schema if not already present."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            path TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            git_root TEXT DEFAULT '',
            project_type TEXT DEFAULT 'generic',
            default_agent TEXT DEFAULT '',
            associated_agents TEXT DEFAULT '[]',
            default_terminal TEXT DEFAULT '',
            default_editor TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            favorite INTEGER DEFAULT 0,
            last_opened TEXT DEFAULT '',
            last_scanned TEXT DEFAULT '',
            launch_profile TEXT DEFAULT '{}',
            scan_status TEXT DEFAULT 'ready',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_roots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            enabled INTEGER DEFAULT 1,
            last_scanned TEXT DEFAULT ''
        );
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            agent_id TEXT,
            pid INTEGER,
            status TEXT DEFAULT 'running',
            start_time TEXT NOT NULL,
            end_time TEXT DEFAULT '',
            log_path TEXT DEFAULT '',
            command TEXT DEFAULT ''
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_path ON projects(path);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_fav ON projects(favorite);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_last_opened ON projects(last_opened);")
        conn.commit()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _row_to_project_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    try:
        d["associated_agents"] = json.loads(d.get("associated_agents") or "[]")
    except Exception:
        d["associated_agents"] = []
    try:
        d["tags"] = json.loads(d.get("tags") or "[]")
    except Exception:
        d["tags"] = []
    try:
        d["launch_profile"] = json.loads(d.get("launch_profile") or "{}")
    except Exception:
        d["launch_profile"] = {}
    d["favorite"] = bool(d.get("favorite", 0))
    return d

def get_projects(search: str = None, tag: str = None, favorites_only: bool = False, sort_by: str = "last_opened") -> list[dict]:
    """Queries projects matching optional search query, tag, or favorite status."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM projects WHERE 1=1"
        params = []
        
        if favorites_only:
            query += " AND favorite = 1"
            
        if search and search.strip():
            s = f"%{search.strip()}%"
            query += " AND (name LIKE ? OR description LIKE ? OR path LIKE ? OR tags LIKE ?)"
            params.extend([s, s, s, s])
            
        if tag and tag.strip():
            query += " AND tags LIKE ?"
            params.append(f"%{tag.strip()}%")
            
        if sort_by == "favorite":
            query += " ORDER BY favorite DESC, last_opened DESC, name ASC"
        elif sort_by == "name":
            query += " ORDER BY name ASC"
        elif sort_by == "last_opened":
            query += " ORDER BY last_opened DESC, name ASC"
        else:
            query += " ORDER BY updated_at DESC"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_project_dict(r) for r in rows]

def get_project(project_id_or_path: str) -> dict | None:
    """Fetches a project by its unique ID or absolute path."""
    init_db()
    norm = normalize_path(project_id_or_path)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ? OR path = ?", (project_id_or_path, norm))
        row = cursor.fetchone()
        return _row_to_project_dict(row) if row else None

def upsert_project(pdata: dict) -> dict:
    """Inserts or updates a project record in the registry."""
    init_db()
    norm_path = normalize_path(pdata.get("path", ""))
    if not norm_path:
        raise ValueError("Project path cannot be empty")
        
    pid = pdata.get("id") or str(uuid.uuid5(uuid.NAMESPACE_URL, norm_path))
    name = pdata.get("name") or os.path.basename(norm_path) or "Project"
    desc = pdata.get("description", "")
    git_root = normalize_path(pdata.get("git_root", ""))
    ptype = pdata.get("project_type", "generic")
    def_ag = pdata.get("default_agent", "")
    assoc = json.dumps(pdata.get("associated_agents") or [])
    def_term = pdata.get("default_terminal", "")
    def_ed = pdata.get("default_editor", "")
    tags = json.dumps(pdata.get("tags") or [])
    fav = 1 if pdata.get("favorite") else 0
    now = _now_iso()
    last_opened = pdata.get("last_opened", "")
    last_scanned = pdata.get("last_scanned") or now
    launch_prof = json.dumps(pdata.get("launch_profile") or {})
    scan_st = pdata.get("scan_status", "ready")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO projects (
            id, name, path, description, git_root, project_type, default_agent,
            associated_agents, default_terminal, default_editor, tags, favorite,
            last_opened, last_scanned, launch_profile, scan_status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            name = excluded.name,
            description = CASE WHEN excluded.description != '' THEN excluded.description ELSE projects.description END,
            git_root = excluded.git_root,
            project_type = excluded.project_type,
            default_agent = CASE WHEN excluded.default_agent != '' THEN excluded.default_agent ELSE projects.default_agent END,
            associated_agents = excluded.associated_agents,
            default_terminal = CASE WHEN excluded.default_terminal != '' THEN excluded.default_terminal ELSE projects.default_terminal END,
            default_editor = CASE WHEN excluded.default_editor != '' THEN excluded.default_editor ELSE projects.default_editor END,
            tags = excluded.tags,
            favorite = CASE WHEN excluded.favorite != 0 THEN excluded.favorite ELSE projects.favorite END,
            last_scanned = excluded.last_scanned,
            launch_profile = excluded.launch_profile,
            scan_status = excluded.scan_status,
            updated_at = excluded.updated_at;
        """, (
            pid, name, norm_path, desc, git_root, ptype, def_ag, assoc,
            def_term, def_ed, tags, fav, last_opened, last_scanned,
            launch_prof, scan_st, now, now
        ))
        conn.commit()
        
    sync_to_json()
    return get_project(pid)

def delete_project(project_id: str) -> bool:
    """Removes a project from the registry without deleting any files on disk."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ? OR path = ?", (project_id, normalize_path(project_id)))
        affected = cursor.rowcount
        conn.commit()
    if affected > 0:
        sync_to_json()
        return True
    return False

def toggle_project_favorite(project_id: str) -> bool:
    """Toggles the favorite flag on a project."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET favorite = CASE WHEN favorite = 1 THEN 0 ELSE 1 END, updated_at = ? WHERE id = ?", (_now_iso(), project_id))
        conn.commit()
    sync_to_json()
    p = get_project(project_id)
    return p.get("favorite", False) if p else False

def update_project_last_opened(project_id: str):
    """Updates the last_opened timestamp when a user opens or launches an agent in a project."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET last_opened = ?, updated_at = ? WHERE id = ?", (_now_iso(), _now_iso(), project_id))
        conn.commit()
    sync_to_json()

def get_scan_roots() -> list[dict]:
    """Retrieves all registered project scan root directories."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scan_roots ORDER BY path ASC")
        return [dict(r) for r in cursor.fetchall()]

def add_scan_root(path: str) -> bool:
    """Adds a custom scan root to the database."""
    init_db()
    norm = normalize_path(path)
    if not os.path.isdir(norm):
        return False
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO scan_roots (path, enabled, last_scanned) VALUES (?, 1, '')", (norm,))
        conn.commit()
    return True

def remove_scan_root(path: str) -> bool:
    """Removes a scan root from the database."""
    init_db()
    norm = normalize_path(path)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scan_roots WHERE path = ?", (norm,))
        affected = cursor.rowcount
        conn.commit()
    return affected > 0

def sync_to_json(out_path: str = None) -> bool:
    """Exports the complete project registry to JSON for human readability and portability."""
    path = out_path or OMNI_PROJECTS_JSON
    try:
        projects = get_projects(sort_by="name")
        roots = get_scan_roots()
        data = {
            "version": "4.2.0",
            "exported_at": _now_iso(),
            "projects": projects,
            "scan_roots": roots
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def sync_from_json(in_path: str = None) -> int:
    """Imports projects from JSON into SQLite registry."""
    path = in_path or OMNI_PROJECTS_JSON
    if not os.path.exists(path):
        return 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for p in data.get("projects", []):
            if p.get("path") and os.path.exists(p["path"]):
                upsert_project(p)
                count += 1
        for r in data.get("scan_roots", []):
            if r.get("path") and os.path.exists(r["path"]):
                add_scan_root(r["path"])
        return count
    except Exception:
        return 0
