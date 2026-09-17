import os
import sys
import shutil
import subprocess

USERPROFILE = os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.expanduser("~")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", os.path.join(USERPROFILE, "AppData", "Local"))
APPDATA = os.environ.get("APPDATA", os.path.join(USERPROFILE, "AppData", "Roaming"))
PROGRAMFILES = os.environ.get("ProgramFiles", "C:\\Program Files")
PROGRAMFILES_X86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

OMNI_DATA_DIR = os.path.join(USERPROFILE, ".omni")
os.makedirs(OMNI_DATA_DIR, exist_ok=True)
OMNI_DB_PATH = os.path.join(OMNI_DATA_DIR, "omni_agent_manager.db")
OMNI_PROJECTS_JSON = os.path.join(USERPROFILE, ".omni_projects.json")
OMNI_BACKUPS_DIR = os.path.join(USERPROFILE, ".omni_backups")
os.makedirs(OMNI_BACKUPS_DIR, exist_ok=True)

def normalize_path(p: str) -> str:
    """Safely normalizes Windows paths preserving casing, resolving relative dots, and removing trailing slashes."""
    if not p:
        return ""
    try:
        expanded = os.path.expandvars(os.path.expanduser(p))
        norm = os.path.abspath(os.path.normpath(expanded))
        return norm
    except Exception:
        return p

def is_safe_subpath(child: str, parent: str) -> bool:
    """Verifies that child path is strictly located within parent directory (guards against traversal)."""
    try:
        child_norm = normalize_path(child)
        parent_norm = normalize_path(parent)
        rel = os.path.relpath(child_norm, parent_norm)
        return not rel.startswith("..") and not os.path.isabs(rel)
    except Exception:
        return False

def find_executable(name: str) -> str | None:
    """Resolves an executable from system PATH or common Windows application folders."""
    if not name:
        return None
    
    # 1. Standard PATH lookup
    found = shutil.which(name)
    if found and os.path.exists(found):
        return normalize_path(found)
    
    # 2. Add Windows extensions if missing
    if os.name == 'nt' and not any(name.lower().endswith(ext) for ext in [".exe", ".cmd", ".bat"]):
        for ext in [".exe", ".cmd", ".bat"]:
            found = shutil.which(f"{name}{ext}")
            if found and os.path.exists(found):
                return normalize_path(found)
    
    # 3. Check Windows Terminal / PowerShell / VS Code special locations
    candidates = []
    if name.lower() in ("wt", "wt.exe"):
        candidates.append(os.path.join(LOCALAPPDATA, "Microsoft", "WindowsApps", "wt.exe"))
    elif name.lower() in ("pwsh", "pwsh.exe"):
        candidates.extend([
            os.path.join(PROGRAMFILES, "PowerShell", "7", "pwsh.exe"),
            os.path.join(PROGRAMFILES, "PowerShell", "7-preview", "pwsh.exe"),
        ])
    elif name.lower() in ("code", "code.cmd", "code.exe"):
        candidates.extend([
            os.path.join(LOCALAPPDATA, "Programs", "Microsoft VS Code", "bin", "code.cmd"),
            os.path.join(LOCALAPPDATA, "Programs", "Microsoft VS Code", "Code.exe"),
            os.path.join(PROGRAMFILES, "Microsoft VS Code", "bin", "code.cmd"),
        ])
    elif name.lower() in ("cursor", "cursor.cmd", "cursor.exe"):
        candidates.extend([
            os.path.join(LOCALAPPDATA, "Programs", "cursor", "Cursor.exe"),
            os.path.join(LOCALAPPDATA, "Programs", "cursor", "resources", "app", "bin", "cursor.cmd"),
        ])
    
    for cand in candidates:
        if os.path.exists(cand):
            return normalize_path(cand)
            
    return None

def detect_terminals() -> dict[str, str]:
    """Detects available terminal engines on Windows."""
    terms = {}
    wt = find_executable("wt")
    if wt:
        terms["wt"] = wt
    pwsh = find_executable("pwsh")
    if pwsh:
        terms["pwsh"] = pwsh
    terms["powershell"] = find_executable("powershell") or "powershell.exe"
    terms["cmd"] = find_executable("cmd") or "cmd.exe"
    return terms

def detect_editors() -> dict[str, str]:
    """Detects available code editors on Windows."""
    eds = {}
    code = find_executable("code")
    if code:
        eds["vscode"] = code
    cursor = find_executable("cursor")
    if cursor:
        eds["cursor"] = cursor
    np = find_executable("notepad++")
    if np:
        eds["notepad++"] = np
    eds["notepad"] = find_executable("notepad") or "notepad.exe"
    return eds

def get_default_project_roots() -> list[str]:
    """Detects candidate project root directories on local drives."""
    roots = []
    seen = set()
    
    # 1. Current working directory & parents
    curr = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in [curr, os.path.abspath(os.path.join(curr, "..")), os.path.abspath(os.path.join(curr, "..", ".."))]:
        if os.path.isdir(p) and p not in seen:
            roots.append(p)
            seen.add(p)
            
    # 2. Standard document directories
    user_docs = os.path.join(USERPROFILE, "Documents")
    standard_candidates = [
        os.path.join(user_docs, "ai_projects"),
        os.path.join(user_docs, "Projects"),
        os.path.join(user_docs, "GitHub"),
        os.path.join(USERPROFILE, "ai_projects"),
        os.path.join(USERPROFILE, "Projects"),
        os.path.join(USERPROFILE, "source", "repos"),
        os.path.join(user_docs, "OpenCode projects"),
    ]
    for c in standard_candidates:
        if os.path.isdir(c) and c not in seen:
            roots.append(c)
            seen.add(c)
            
    # 3. Drive-level detection on Windows
    if os.name == 'nt':
        u_base = os.path.basename(USERPROFILE)
        for drive in ("D", "C", "E", "F"):
            for cand in [
                f"{drive}:\\{u_base}\\Documents\\ai_projects",
                f"{drive}:\\{u_base}\\Documents\\Projects",
                f"{drive}:\\ai_projects",
                f"{drive}:\\Projects",
            ]:
                if os.path.isdir(cand) and cand not in seen:
                    roots.append(cand)
                    seen.add(cand)
                    
    return roots

def quote_windows_arg(arg: str) -> str:
    """Safely escapes a single argument for Windows command line execution."""
    if not arg:
        return '""'
    if not any(c in arg for c in ' \t\n\v"'):
        return arg
    escaped = arg.replace('"', '\\"')
    return f'"{escaped}"'
