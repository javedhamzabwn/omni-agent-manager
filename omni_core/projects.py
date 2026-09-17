import os
import subprocess
from datetime import datetime, timezone
from omni_core.paths import normalize_path
from omni_core.db import upsert_project, get_scan_roots, add_scan_root

EXCLUDED_DIR_NAMES = {
    "node_modules", ".git", "__pycache__", "venv", ".venv", "env",
    ".idea", ".vscode", "dist", "build", "target", ".cache", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "site-packages", "obj", "bin"
}

INSTRUCTION_FILES = [
    "CLAUDE.md", "CLAUDE.local.md", "AGENTS.md", "GEMINI.md",
    ".cursorrules", "CONVENTIONS.md", "README.md", "CONTRIBUTING.md"
]

def find_git_root(path: str) -> str | None:
    """Finds the root of the Git repository containing path without spawning slow processes if possible."""
    curr = normalize_path(path)
    if not os.path.exists(curr):
        return None
    if os.path.isfile(curr):
        curr = os.path.dirname(curr)
        
    while curr:
        if os.path.isdir(os.path.join(curr, ".git")):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
        
    # Fallback to git command if .git is a worktree file
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path if os.path.isdir(path) else os.path.dirname(path),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2.0
        ).strip()
        if out and os.path.isdir(out):
            return normalize_path(out)
    except Exception:
        pass
    return None

def detect_project_type(path: str) -> str:
    """Detects the primary tech stack/type of a project directory."""
    types = []
    if os.path.exists(os.path.join(path, "pyproject.toml")) or \
       os.path.exists(os.path.join(path, "setup.py")) or \
       os.path.exists(os.path.join(path, "requirements.txt")):
        types.append("python")
        
    if os.path.exists(os.path.join(path, "package.json")):
        types.append("node")
        
    if os.path.exists(os.path.join(path, "Cargo.toml")):
        types.append("rust")
        
    if os.path.exists(os.path.join(path, "go.mod")):
        types.append("go")
        
    if os.path.exists(os.path.join(path, "CMakeLists.txt")) or \
       os.path.exists(os.path.join(path, "Makefile")):
        types.append("c/c++")
        
    if len(types) > 1:
        return f"mixed ({'+'.join(types)})"
    elif len(types) == 1:
        return types[0]
    return "generic"

def inspect_project_metadata(path: str) -> dict:
    """Deeply inspects a project folder for Git info, instruction files, agent configs, and MCPs."""
    norm = normalize_path(path)
    if not os.path.isdir(norm):
        return {"valid": False, "error": "Directory does not exist"}
        
    git_root = find_git_root(norm)
    ptype = detect_project_type(norm)
    
    # Check instructions
    instructions = []
    for ifile in INSTRUCTION_FILES:
        ipath = os.path.join(norm, ifile)
        if os.path.isfile(ipath):
            instructions.append({
                "name": ifile,
                "path": ipath,
                "size": os.path.getsize(ipath),
                "status": "ACTIVE_RECOGNIZED" if ifile in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", ".cursorrules") else "EXISTS"
            })
            
    # Check agent configuration folders
    agent_configs = []
    agent_dirs = [
        (".claude", "Claude Code"),
        (".gemini", "Google Antigravity / Gemini"),
        (".opencode", "OpenCode Interpreter"),
        (".cursor", "Cursor AI IDE"),
        (".vscode", "VS Code")
    ]
    for dname, aname in agent_dirs:
        dpath = os.path.join(norm, dname)
        if os.path.isdir(dpath):
            agent_configs.append({
                "folder": dname,
                "agent": aname,
                "path": dpath,
                "status": "ACTIVE_RECOGNIZED"
            })
            
    # Check project-level MCP files
    mcps = []
    mcp_candidates = [
        os.path.join(norm, "mcp.json"),
        os.path.join(norm, ".mcp.json"),
        os.path.join(norm, ".claude", "mcp.json"),
        os.path.join(norm, ".gemini", "mcp_config.json"),
        os.path.join(norm, ".cursor", "mcp.json"),
    ]
    for m in mcp_candidates:
        if os.path.isfile(m):
            mcps.append({
                "path": m,
                "name": os.path.basename(m),
                "status": "ACTIVE_RECOGNIZED"
            })
            
    # Detect default agent candidate
    def_agent = ""
    assoc_agents = []
    if os.path.exists(os.path.join(norm, "CLAUDE.md")) or os.path.isdir(os.path.join(norm, ".claude")):
        assoc_agents.append("claude")
        def_agent = "claude"
    if os.path.exists(os.path.join(norm, "GEMINI.md")) or os.path.isdir(os.path.join(norm, ".gemini")):
        assoc_agents.append("antigravity")
        if not def_agent: def_agent = "antigravity"
    if os.path.exists(os.path.join(norm, ".opencode")) or os.path.exists(os.path.join(norm, "opencode.json")):
        assoc_agents.append("opencode")
        if not def_agent: def_agent = "opencode"
    if os.path.exists(os.path.join(norm, ".cursorrules")) or os.path.isdir(os.path.join(norm, ".cursor")):
        assoc_agents.append("cursor")
        if not def_agent: def_agent = "cursor"
    if os.path.exists(os.path.join(norm, ".aider.conf.yml")):
        assoc_agents.append("aider")
        if not def_agent: def_agent = "aider"
    if os.path.exists(os.path.join(norm, "AGENTS.md")):
        assoc_agents.append("codex")
        if not def_agent: def_agent = "codex"
        
    return {
        "valid": True,
        "path": norm,
        "name": os.path.basename(norm),
        "git_root": git_root or "",
        "project_type": ptype,
        "instructions": instructions,
        "agent_configs": agent_configs,
        "mcps": mcps,
        "default_agent": def_agent or "claude",
        "associated_agents": list(set(assoc_agents))
    }

def scan_directory_for_projects(root_path: str, max_depth: int = 3, progress_callback=None, cancel_check=None) -> list[dict]:
    """Scans a root folder up to max_depth for coding projects, skipping heavy build/cache dirs."""
    root = normalize_path(root_path)
    if not os.path.isdir(root):
        return []
        
    discovered = []
    
    def is_project_dir(p: str) -> bool:
        indicators = [
            ".git", "package.json", "pyproject.toml", "setup.py", "Cargo.toml",
            "go.mod", "CLAUDE.md", "AGENTS.md", "GEMINI.md", "CMakeLists.txt",
            ".claude", ".cursor", ".opencode"
        ]
        return any(os.path.exists(os.path.join(p, ind)) for ind in indicators)
        
    # Check if root itself is a project
    if is_project_dir(root):
        meta = inspect_project_metadata(root)
        discovered.append(meta)
        if progress_callback:
            progress_callback(meta)
            
    # Recursively scan subdirectories
    for current_dir, dirs, files in os.walk(root):
        if cancel_check and cancel_check():
            break
            
        # Calculate current depth relative to root
        rel = os.path.relpath(current_dir, root)
        depth = 0 if rel == "." else len(rel.split(os.sep))
        
        # Prune excluded directories in-place so os.walk skips them
        dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIR_NAMES and not d.startswith(".")]
        
        if depth >= max_depth:
            dirs.clear()
            continue
            
        # Check subdirectories
        for d in list(dirs):
            sub_path = os.path.join(current_dir, d)
            if is_project_dir(sub_path):
                meta = inspect_project_metadata(sub_path)
                discovered.append(meta)
                if progress_callback:
                    progress_callback(meta)
                # Once a directory is identified as a project, don't descend into sub-projects unless desired
                dirs.remove(d)
                
    return discovered

def run_project_discovery_scan(roots: list[str] = None, max_depth: int = 3, auto_register: bool = True, progress_callback=None, cancel_check=None) -> list[dict]:
    """Runs a complete project discovery scan across registered or detected scan roots and optionally registers them."""
    if not roots:
        registered = get_scan_roots()
        roots = [r["path"] for r in registered if r.get("enabled", 1)]
    if not roots:
        from omni_core.paths import get_default_project_roots
        roots = get_default_project_roots()
        for r in roots:
            add_scan_root(r)
            
    all_discovered = []
    seen_paths = set()
    
    for r in roots:
        if cancel_check and cancel_check():
            break
        if not os.path.isdir(r):
            continue
        found = scan_directory_for_projects(r, max_depth=max_depth, progress_callback=progress_callback, cancel_check=cancel_check)
        for p in found:
            norm = p["path"]
            if norm not in seen_paths:
                seen_paths.add(norm)
                all_discovered.append(p)
                if auto_register:
                    upsert_project({
                        "name": p["name"],
                        "path": norm,
                        "git_root": p.get("git_root", ""),
                        "project_type": p.get("project_type", "generic"),
                        "default_agent": p.get("default_agent", ""),
                        "associated_agents": p.get("associated_agents", []),
                        "scan_status": "ready"
                    })
    return all_discovered
