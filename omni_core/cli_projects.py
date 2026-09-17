import sys
import os
import json

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8")
    except Exception: pass

from omni_core.db import get_projects, get_project, upsert_project, delete_project, toggle_project_favorite, get_scan_roots, add_scan_root
from omni_core.projects import run_project_discovery_scan, inspect_project_metadata
from omni_core.launcher import open_in_terminal, open_in_vscode, open_in_explorer, open_in_editor, launch_agent_in_project
from omni_core.adapters import get_all_adapters, get_adapter
from omni_core.paths import normalize_path

def handle_project_cli(args: list[str]) -> int:
    """Handles all 'omni-agent project ...' subcommands."""
    if not args or args[0] in ("-h", "--help", "help"):
        print("""OmniAgent Manager - Project Commands:
  omni-agent project list [--json] [--fav] [--tag TAG] [--search QUERY]
  omni-agent project add <PATH> [--name NAME] [--agent AGENT] [--desc DESC]
  omni-agent project remove <ID_OR_PATH>
  omni-agent project scan [--roots PATH...] [--depth N]
  omni-agent project open <ID_OR_NAME> [--terminal|--editor|--explorer]
  omni-agent project launch <ID_OR_NAME> [--agent AGENT]
  omni-agent project info <ID_OR_NAME>
  omni-agent project fav <ID_OR_NAME>
""")
        return 0
        
    sub = args[0].lower()
    
    # 1. LIST
    if sub == "list":
        is_json = "--json" in args
        fav_only = "--fav" in args
        search = None
        tag = None
        if "--search" in args:
            idx = args.index("--search")
            if len(args) > idx + 1: search = args[idx + 1]
        if "--tag" in args:
            idx = args.index("--tag")
            if len(args) > idx + 1: tag = args[idx + 1]
            
        projects = get_projects(search=search, tag=tag, favorites_only=fav_only, sort_by="last_opened")
        if is_json:
            print(json.dumps(projects, indent=2, ensure_ascii=False))
            return 0
            
        print(f"\nRegistered Workspaces & Projects ({len(projects)} total):")
        print("=" * 80)
        if not projects:
            print("  (No projects registered yet. Run 'omni-agent project scan' or 'omni-agent project add <path>')")
        for p in projects:
            fav = "★" if p.get("favorite") else "☆"
            ag = p.get("default_agent") or "default"
            ptype = p.get("project_type", "generic")
            print(f"  {fav} [{p['id'][:8]}] {p['name']:<25} | {ag:<12} | {ptype:<12} | {p['path']}")
        print("=" * 80)
        return 0
        
    # 2. ADD
    elif sub == "add":
        if len(args) < 2:
            print("Usage: omni-agent project add <PATH> [--name NAME] [--agent AGENT] [--desc DESC]")
            return 1
        path = args[1]
        norm = normalize_path(path)
        if not os.path.isdir(norm):
            print(f"[ERROR] Directory does not exist: {norm}")
            return 1
            
        name = os.path.basename(norm)
        agent = ""
        desc = ""
        if "--name" in args:
            idx = args.index("--name")
            if len(args) > idx + 1: name = args[idx + 1]
        if "--agent" in args:
            idx = args.index("--agent")
            if len(args) > idx + 1: agent = args[idx + 1]
        if "--desc" in args:
            idx = args.index("--desc")
            if len(args) > idx + 1: desc = args[idx + 1]
            
        meta = inspect_project_metadata(norm)
        p = upsert_project({
            "name": name,
            "path": norm,
            "description": desc,
            "git_root": meta.get("git_root", ""),
            "project_type": meta.get("project_type", "generic"),
            "default_agent": agent or meta.get("default_agent", ""),
            "associated_agents": meta.get("associated_agents", []),
            "scan_status": "ready"
        })
        print(f"[OK] Registered project '{p['name']}' (ID: {p['id']}) at {p['path']}")
        return 0
        
    # 3. REMOVE
    elif sub in ("remove", "rm", "delete"):
        if len(args) < 2:
            print("Usage: omni-agent project remove <ID_OR_PATH>")
            return 1
        target = args[1]
        ok = delete_project(target)
        if ok:
            print(f"[OK] Project '{target}' removed from registry (files preserved on disk).")
            return 0
        else:
            print(f"[ERROR] Project '{target}' not found in registry.")
            return 1
            
    # 4. SCAN
    elif sub == "scan":
        roots = []
        depth = 3
        if "--roots" in args:
            idx = args.index("--roots")
            for item in args[idx + 1:]:
                if item.startswith("-"): break
                roots.append(normalize_path(item))
        if "--depth" in args:
            idx = args.index("--depth")
            if len(args) > idx + 1:
                try: depth = int(args[idx + 1])
                except ValueError: pass
                
        print(f"Scanning for coding projects (depth={depth})...")
        found = run_project_discovery_scan(roots=roots if roots else None, max_depth=depth, auto_register=True)
        print(f"\n[OK] Scan complete. Discovered and registered {len(found)} project(s):")
        for p in found:
            print(f"  • {p['name']:<25} ({p.get('project_type', 'generic')}) -> {p['path']}")
        return 0
        
    # 5. OPEN
    elif sub == "open":
        if len(args) < 2:
            print("Usage: omni-agent project open <ID_OR_NAME> [--terminal|--editor|--explorer]")
            return 1
        target = args[1]
        p = get_project(target)
        if not p:
            # Check by name
            candidates = [proj for proj in get_projects() if proj['name'].lower() == target.lower()]
            p = candidates[0] if candidates else None
        if not p:
            print(f"[ERROR] Project '{target}' not found in registry.")
            return 1
            
        path = p["path"]
        if "--terminal" in args or "-t" in args:
            ok, msg = open_in_terminal(path)
        elif "--editor" in args or "-e" in args:
            ok, msg = open_in_editor(path)
        elif "--explorer" in args or "-x" in args:
            ok, msg = open_in_explorer(path)
        else:
            ok, msg = open_in_vscode(path)
            if not ok:
                ok, msg = open_in_explorer(path)
                
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return 0 if ok else 1
        
    # 6. LAUNCH
    elif sub == "launch":
        if len(args) < 2:
            print("Usage: omni-agent project launch <ID_OR_NAME> [--agent AGENT]")
            return 1
        target = args[1]
        agent = None
        if "--agent" in args:
            idx = args.index("--agent")
            if len(args) > idx + 1: agent = args[idx + 1]
            
        p = get_project(target)
        if not p:
            candidates = [proj for proj in get_projects() if proj['name'].lower() == target.lower()]
            p = candidates[0] if candidates else None
            
        target_path = p["path"] if p else normalize_path(target)
        target_agent = agent or (p.get("default_agent") if p else "claude")
        
        ok, msg, pid = launch_agent_in_project(target_path, agent_id=target_agent)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return 0 if ok else 1
        
    # 7. INFO
    elif sub == "info":
        if len(args) < 2:
            print("Usage: omni-agent project info <ID_OR_NAME>")
            return 1
        target = args[1]
        p = get_project(target)
        if not p:
            candidates = [proj for proj in get_projects() if proj['name'].lower() == target.lower()]
            p = candidates[0] if candidates else None
        if not p:
            print(f"[ERROR] Project '{target}' not found.")
            return 1
            
        meta = inspect_project_metadata(p["path"])
        print(f"\nProject Details: {p['name']}")
        print("=" * 60)
        print(f"ID:          {p['id']}")
        print(f"Path:        {p['path']}")
        print(f"Type:        {p.get('project_type')}")
        print(f"Git Root:    {meta.get('git_root') or 'Not a git repo'}")
        print(f"Default Ag:  {p.get('default_agent')}")
        print(f"Favorite:    {'Yes' if p.get('favorite') else 'No'}")
        print(f"Last Opened: {p.get('last_opened') or 'Never'}")
        print("\nInstructions Found:")
        for inst in meta.get("instructions", []):
            print(f"  • {inst['name']} ({inst['status']}) -> {inst['path']}")
        print("\nAgent Config Folders:")
        for ac in meta.get("agent_configs", []):
            print(f"  • {ac['folder']} ({ac['agent']}) -> {ac['path']}")
        return 0
        
    # 8. FAVORITE
    elif sub in ("fav", "favorite"):
        if len(args) < 2:
            print("Usage: omni-agent project fav <ID_OR_NAME>")
            return 1
        target = args[1]
        p = get_project(target)
        if not p:
            candidates = [proj for proj in get_projects() if proj['name'].lower() == target.lower()]
            p = candidates[0] if candidates else None
        if not p:
            print(f"[ERROR] Project '{target}' not found.")
            return 1
        fav = toggle_project_favorite(p["id"])
        print(f"[OK] Project '{p['name']}' favorite set to: {'★ Favorited' if fav else '☆ Unfavorited'}")
        return 0
        
    else:
        print(f"Unknown project subcommand: {sub}. Run 'omni-agent project --help'")
        return 1

def handle_agent_cli(args: list[str]) -> int:
    """Handles all 'omni-agent agent ...' subcommands."""
    if not args or args[0] in ("-h", "--help", "help"):
        print("""OmniAgent Manager - Agent Commands:
  omni-agent agent list [--json]
  omni-agent agent detect
  omni-agent agent doctor <AGENT_ID>
""")
        return 0
        
    sub = args[0].lower()
    adapters = get_all_adapters()
    
    if sub == "list":
        is_json = "--json" in args
        res = []
        for aid, ad in adapters.items():
            inst = ad.detect_installed()
            ver = ad.get_version() if inst else "Not Installed"
            res.append({
                "id": aid,
                "name": ad.name,
                "category": ad.category,
                "installed": inst,
                "version": ver
            })
        if is_json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print(f"\nInstalled & Configured AI Coding Agents ({len(res)} total):")
            print("=" * 80)
            for r in res:
                st = "✔ INSTALLED" if r["installed"] else "✗ Available"
                print(f"  [{st:<11}] {r['id']:<14} | {r['name']:<28} | {r['version']}")
            print("=" * 80)
        return 0
        
    elif sub == "detect":
        print("\nScanning system for installed coding agent runtimes & executables...")
        found = 0
        for aid, ad in adapters.items():
            inst = ad.detect_installed()
            if inst:
                found += 1
                exe = ad.get_executable() or "Config-only"
                print(f"  ✔ Detected: {ad.name:<28} ({aid}) -> Executable: {exe}")
        print(f"\n[OK] Scan completed. {found} agent(s) active on this workstation.")
        return 0
        
    elif sub == "doctor":
        if len(args) < 2:
            print("Usage: omni-agent agent doctor <AGENT_ID>")
            return 1
        aid = args[1].lower()
        ad = get_adapter(aid)
        inst = ad.detect_installed()
        exe = ad.get_executable()
        ver = ad.get_version() if inst else "N/A"
        caps = ad.get_capabilities()
        print(f"\nAgent Health Doctor: {ad.name} ({ad.id})")
        print("=" * 60)
        print(f"Status:       {'✔ INSTALLED' if inst else '✗ NOT INSTALLED'}")
        print(f"Executable:   {exe or 'Not found in PATH'}")
        print(f"Version:      {ver}")
        print(f"Documentation: {ad.docs_url or 'N/A'}")
        print("\nCapabilities:")
        for cap, val in caps.items():
            print(f"  • {cap:<25} : {val}")
        return 0
        
    else:
        print(f"Unknown agent subcommand: {sub}. Run 'omni-agent agent --help'")
        return 1
