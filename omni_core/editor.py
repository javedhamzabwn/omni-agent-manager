import os
import json
import difflib
import shutil
import time
from datetime import datetime, timezone
from omni_core.paths import normalize_path, OMNI_BACKUPS_DIR

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import tomllib
    HAS_TOMLLIB = True
except ImportError:
    HAS_TOMLLIB = False

def detect_file_format(filepath: str) -> str:
    """Infers file format from extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".json", ".jsonc"):
        return "json"
    elif ext in (".yml", ".yaml"):
        return "yaml"
    elif ext in (".toml",):
        return "toml"
    elif ext in (".md", ".markdown"):
        return "markdown"
    elif ext in (".py",):
        return "python"
    elif ext in (".js", ".ts"):
        return "javascript"
    return "text"

def read_file_safe(filepath: str) -> dict:
    """Reads a file with automatic UTF-8/fallback encoding detection and metadata."""
    norm = normalize_path(filepath)
    if not os.path.isfile(norm):
        return {"success": False, "error": f"File does not exist: {norm}"}
        
    mtime = os.path.getmtime(norm)
    size = os.path.getsize(norm)
    fmt = detect_file_format(norm)
    
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    content = None
    used_enc = None
    
    for enc in encodings:
        try:
            with open(norm, "r", encoding=enc) as f:
                content = f.read()
            used_enc = enc
            break
        except Exception:
            continue
            
    if content is None:
        return {"success": False, "error": "Unable to decode file with standard text encodings"}
        
    return {
        "success": True,
        "path": norm,
        "filename": os.path.basename(norm),
        "content": content,
        "format": fmt,
        "mtime": mtime,
        "size": size,
        "encoding": used_enc
    }

def validate_content(content: str, fmt: str) -> tuple[bool, str]:
    """Validates configuration syntax for JSON, YAML, and TOML."""
    if fmt == "json":
        try:
            # Strip comments if jsonc
            lines = [l for l in content.splitlines() if not l.strip().startswith("//")]
            json.loads("\n".join(lines))
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"JSON Syntax Error (line {e.lineno}, col {e.colno}): {e.msg}"
    elif fmt == "yaml" and HAS_YAML:
        try:
            yaml.safe_load(content)
            return True, "Valid YAML"
        except Exception as e:
            return False, f"YAML Syntax Error: {e}"
    elif fmt == "toml" and HAS_TOMLLIB:
        try:
            tomllib.loads(content)
            return True, "Valid TOML"
        except Exception as e:
            return False, f"TOML Syntax Error: {e}"
    return True, "Syntax OK"

def generate_diff(original: str, new: str, filename: str = "file") -> str:
    """Computes a standard unified diff string between original and modified content."""
    orig_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(
        orig_lines,
        new_lines,
        fromfile=f"a/{filename} (original)",
        tofile=f"b/{filename} (modified)"
    )
    return "".join(diff)

def create_backup(filepath: str) -> str | None:
    """Creates a timestamped copy of the target file in the backups folder."""
    norm = normalize_path(filepath)
    if not os.path.isfile(norm):
        return None
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base = os.path.basename(norm)
        bak_name = f"{ts}_{base}.bak"
        bak_path = os.path.join(OMNI_BACKUPS_DIR, bak_name)
        shutil.copy2(norm, bak_path)
        return bak_path
    except Exception:
        return None

def write_file_safe(filepath: str, new_content: str, expected_mtime: float = None, force: bool = False, validate: bool = True) -> tuple[bool, str, str | None]:
    """Safely saves content with external-change check, syntax validation, automatic backup, and atomic replacement."""
    norm = normalize_path(filepath)
    
    # 1. External modification detection
    if os.path.exists(norm) and expected_mtime is not None and not force:
        cur_mtime = os.path.getmtime(norm)
        if abs(cur_mtime - expected_mtime) > 1.0:
            return False, "File has been modified externally on disk. Use force=True to overwrite.", None
            
    # 2. Syntax validation
    fmt = detect_file_format(norm)
    if validate:
        ok, vmsg = validate_content(new_content, fmt)
        if not ok:
            return False, vmsg, None
            
    # 3. Create backup before overwriting
    bak_path = None
    if os.path.exists(norm):
        bak_path = create_backup(norm)
        
    # 4. Atomic write via temporary file
    temp_path = f"{norm}.tmp_{int(time.time()*1000)}"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        os.replace(temp_path, norm)
        return True, f"Successfully saved {os.path.basename(norm)}", bak_path
    except Exception as e:
        if os.path.exists(temp_path):
            try: os.remove(temp_path)
            except Exception: pass
        return False, f"Write error: {e}", bak_path
