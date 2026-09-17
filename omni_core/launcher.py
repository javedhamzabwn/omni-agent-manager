import os
import subprocess
import sys
from omni_core.paths import normalize_path, find_executable, detect_terminals, detect_editors, quote_windows_arg
from omni_core.adapters import get_adapter
from omni_core.db import update_project_last_opened, get_project

def open_in_explorer(path: str) -> tuple[bool, str]:
    """Opens File Explorer focused on the specified path."""
    norm = normalize_path(path)
    if not os.path.exists(norm):
        return False, f"Path does not exist: {norm}"
    try:
        if os.path.isfile(norm):
            subprocess.Popen(["explorer.exe", f"/select,{norm}"])
        else:
            subprocess.Popen(["explorer.exe", norm])
        return True, f"Opened Explorer at {os.path.basename(norm)}"
    except Exception as e:
        return False, f"Failed to open Explorer: {e}"

def open_in_vscode(path: str) -> tuple[bool, str]:
    """Opens the directory or file in Visual Studio Code."""
    norm = normalize_path(path)
    if not os.path.exists(norm):
        return False, f"Path does not exist: {norm}"
    code_exe = find_executable("code")
    if not code_exe:
        return False, "VS Code executable ('code') not found in PATH or standard directories"
    try:
        subprocess.Popen([code_exe, norm], shell=False)
        return True, f"Opened in VS Code: {os.path.basename(norm)}"
    except Exception as e:
        return False, f"Failed to launch VS Code: {e}"

def open_in_editor(path: str, editor_choice: str = None) -> tuple[bool, str]:
    """Opens the path in preferred editor (VS Code, Cursor, Notepad++, Notepad)."""
    norm = normalize_path(path)
    if not os.path.exists(norm):
        return False, f"Path does not exist: {norm}"
    editors = detect_editors()
    
    exe = None
    if editor_choice and editor_choice in editors:
        exe = editors[editor_choice]
    elif "vscode" in editors:
        exe = editors["vscode"]
    elif "cursor" in editors:
        exe = editors["cursor"]
    elif "notepad++" in editors:
        exe = editors["notepad++"]
    else:
        exe = editors.get("notepad", "notepad.exe")
        
    try:
        subprocess.Popen([exe, norm], shell=False)
        return True, f"Opened in {os.path.basename(exe)}: {os.path.basename(norm)}"
    except Exception as e:
        return False, f"Failed to launch editor: {e}"

def open_in_terminal(path: str, terminal_choice: str = None) -> tuple[bool, str]:
    """Spawns an interactive terminal window opened to the project working directory."""
    norm = normalize_path(path)
    if not os.path.isdir(norm):
        norm = os.path.dirname(norm)
    if not os.path.isdir(norm):
        return False, f"Working directory does not exist: {norm}"
        
    terms = detect_terminals()
    term = terminal_choice or ("wt" if "wt" in terms else ("pwsh" if "pwsh" in terms else "powershell"))
    
    try:
        if term == "wt" and "wt" in terms:
            subprocess.Popen([terms["wt"], "-d", norm], shell=False)
        elif term == "pwsh" and "pwsh" in terms:
            subprocess.Popen(f'start "" "{terms["pwsh"]}" -NoExit -Command "Set-Location \'{norm}\'"', shell=True)
        elif term == "powershell":
            ps_exe = terms.get("powershell", "powershell.exe")
            subprocess.Popen(f'start "" "{ps_exe}" -NoExit -Command "Set-Location \'{norm}\'"', shell=True)
        else:
            cmd_exe = terms.get("cmd", "cmd.exe")
            subprocess.Popen(f'start "" "{cmd_exe}" /k "cd /d {norm}"', shell=True)
        return True, f"Spawned {term.upper()} terminal at {os.path.basename(norm)}"
    except Exception as e:
        return False, f"Failed to open terminal: {e}"

def launch_agent_in_project(project_path_or_id: str, agent_id: str = None, profile: dict = None, terminal_choice: str = None) -> tuple[bool, str, int | None]:
    """Safely launches an AI coding agent in the context of the project working directory."""
    # Resolve project
    proj = get_project(project_path_or_id)
    if proj:
        p_path = proj["path"]
        p_id = proj["id"]
        ag_id = agent_id or proj.get("default_agent") or "claude"
        update_project_last_opened(p_id)
    else:
        p_path = normalize_path(project_path_or_id)
        p_id = None
        ag_id = agent_id or "claude"
        
    if not os.path.isdir(p_path):
        return False, f"Project directory does not exist: {p_path}", None
        
    adapter = get_adapter(ag_id)
    cmd_list = adapter.construct_launch_cmd(p_path, profile)
    exe_name = cmd_list[0]
    
    # Check if executable exists or is accessible
    resolved_exe = find_executable(exe_name)
    if not resolved_exe and not adapter.detect_installed():
        return False, f"Agent '{ag_id}' ({adapter.name}) is not installed or executable '{exe_name}' not found in PATH", None
        
    terms = detect_terminals()
    term = terminal_choice or ("wt" if "wt" in terms else ("pwsh" if "pwsh" in terms else "powershell"))
    
    cmd_str = " ".join(quote_windows_arg(c) for c in cmd_list)
    
    try:
        proc = None
        # GUI IDE agents (Cursor, Windsurf, Antigravity IDE) launch directly
        if adapter.category == "Desktop IDE":
            proc = subprocess.Popen(cmd_list, cwd=p_path, shell=False)
            return True, f"Launched {adapter.name} on {os.path.basename(p_path)}", proc.pid
            
        # CLI agents must launch inside a visible terminal window
        if term == "wt" and "wt" in terms:
            proc = subprocess.Popen([terms["wt"], "-d", p_path, "cmd.exe", "/k", cmd_str], shell=False)
        elif term == "pwsh" and "pwsh" in terms:
            full_cmd = f'start "" "{terms["pwsh"]}" -NoExit -Command "Set-Location \'{p_path}\'; {cmd_str}"'
            proc = subprocess.Popen(full_cmd, shell=True)
        elif term == "powershell":
            ps_exe = terms.get("powershell", "powershell.exe")
            full_cmd = f'start "" "{ps_exe}" -NoExit -Command "Set-Location \'{p_path}\'; {cmd_str}"'
            proc = subprocess.Popen(full_cmd, shell=True)
        else:
            cmd_exe = terms.get("cmd", "cmd.exe")
            full_cmd = f'start "" "{cmd_exe}" /k "cd /d {p_path} && {cmd_str}"'
            proc = subprocess.Popen(full_cmd, shell=True)
            
        pid = proc.pid if proc else None
        return True, f"Launched {adapter.name} in {term.upper()} at {os.path.basename(p_path)}", pid
    except Exception as e:
        return False, f"Launch error: {e}", None
