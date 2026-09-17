import sys
import os

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8")
    except Exception: pass

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
import json
import shutil
import re
import subprocess
import socket
import urllib.request
import urllib.error
import difflib
import time

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


try:
    import tomllib
except ImportError:
    tomllib = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from textual.app import App, ComposeResult
    from textual import events
    from textual.containers import Container, Horizontal, Vertical, VerticalScroll, Grid
    from textual.widgets import (
        Header, Footer, Button, Static, Label, Input, DataTable,
        SelectionList, TabbedContent, TabPane, Switch, Rule, Select, OptionList
    )
    from textual.screen import ModalScreen
    from textual.reactive import reactive
    from textual.binding import Binding
    from textual.theme import Theme
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False

# Enable ANSI escape sequences on Windows
os.system('')

try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

# Cross-platform environment resolution
USERPROFILE = os.environ.get("USERPROFILE") or os.environ.get("HOME") or os.path.expanduser("~")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", os.path.join(USERPROFILE, "AppData", "Local"))
APPDATA = os.environ.get("APPDATA", os.path.join(USERPROFILE, "AppData", "Roaming"))

def resolve_projects_dir():
    curr = os.path.dirname(os.path.abspath(__file__))
    for p in [curr, os.path.abspath(os.path.join(curr, "..")), os.path.abspath(os.path.join(curr, "..", ".."))]:
        if os.path.basename(p).lower() == "ai_projects":
            return p
        sub = os.path.join(p, "ai_projects")
        if os.path.isdir(sub):
            return sub
    for candidate in [
        os.path.join(USERPROFILE, "Documents", "ai_projects"),
        os.path.join(USERPROFILE, "ai_projects"),
    ]:
        if os.path.exists(candidate):
            return candidate
    if os.name == 'nt':
        u_base = os.path.basename(USERPROFILE)
        for drive in ("D", "C", "E", "F"):
            for candidate in [
                f"{drive}:\\{u_base}\\Documents\\ai_projects",
                f"{drive}:\\Documents\\ai_projects",
                f"{drive}:\\ai_projects",
            ]:
                if os.path.exists(candidate):
                    return candidate
    return os.path.join(USERPROFILE, "Documents", "ai_projects")

def resolve_opencode_workspace():
    for candidate in [
        os.path.join(USERPROFILE, "Documents", "OpenCode projects"),
        os.path.join(USERPROFILE, "OpenCode projects"),
    ]:
        if os.path.exists(candidate):
            return candidate
    if os.name == 'nt':
        u_base = os.path.basename(USERPROFILE)
        for drive in ("D", "C", "E", "F"):
            for candidate in [
                f"{drive}:\\{u_base}\\Documents\\OpenCode projects",
                f"{drive}:\\Documents\\OpenCode projects",
                f"{drive}:\\OpenCode projects",
            ]:
                if os.path.exists(candidate):
                    return candidate
    return os.path.join(USERPROFILE, "Documents", "OpenCode projects")

AI_PROJECTS = resolve_projects_dir()
OPENCODE_WORKSPACE = resolve_opencode_workspace()

# ================= INTEGRATED 20-CATEGORY ECOSYSTEM CATALOG =================
DATA = {
    "1": {
        "title": "Claude Code CLI",
        "desc": "Skills (52), Subagents (29), Slash Commands (5), .claude.json",
        "items": [
            ("Main Working Directory (.claude)", os.path.join(USERPROFILE, ".claude"), "Core configuration & state"),
            ("Active Skills Folder (52 Skills)", os.path.join(USERPROFILE, ".claude", "skills"), "52 Deployed active skills"),
            ("Custom Subagents Folder (29 Agents)", os.path.join(USERPROFILE, ".claude", "agents"), "29 Markdown agent personas"),
            ("Custom Slash Commands (5 Commands)", os.path.join(USERPROFILE, ".claude", "commands"), "opencontext-* custom slash commands"),
            ("Master MCP Config (.claude.json)", os.path.join(USERPROFILE, ".claude.json"), "codegraph, context-mode servers"),
            ("Local MCP Config (mcp.json)", os.path.join(USERPROFILE, ".claude", "mcp.json"), "Local directory MCP configuration"),
            ("Plugins Runtime Directory", os.path.join(USERPROFILE, ".claude", "plugins"), "Installed plugins & cache"),
            ("Official Marketplace Cache", os.path.join(USERPROFILE, ".claude", "plugins", "marketplaces", "claude-plugins-official"), "53 Official & external plugins"),
            ("Claude Registry & Backups Hub", os.path.join(USERPROFILE, ".claude-registry"), "Multi-agent registry and backups")
        ]
    },
    "2": {
        "title": "Claude Desktop (GUI & 3P)",
        "desc": "Standard & Cowork 3P MCPs, Tool Toggles, Logs, VM Sessions",
        "items": [
            ("Standard Claude Desktop Directory", os.path.join(LOCALAPPDATA, "Claude"), "Standard desktop application data"),
            ("Standard Claude Desktop MCP Config", os.path.join(LOCALAPPDATA, "Claude", "claude_desktop_config.json"), "Standard desktop MCP configuration"),
            ("Standard Claude Desktop Logs", os.path.join(LOCALAPPDATA, "Claude", "Logs"), "Application activity and diagnostic logs"),
            ("3P Cowork Claude Desktop Directory", os.path.join(LOCALAPPDATA, "Claude-3p"), "Third-Party Cowork build runtime"),
            ("3P Cowork MCP Config JSON", os.path.join(LOCALAPPDATA, "Claude-3p", "claude_desktop_config.json"), "Cowork MCP tools & server configuration"),
            ("3P MCP User Tool Toggles JSON", os.path.join(LOCALAPPDATA, "Claude-3p", "mcp-user-tool-toggles.json"), "Active/inactive toggle state for MCP tools"),
            ("3P Claude Code Sessions Storage", os.path.join(LOCALAPPDATA, "Claude-3p", "claude-code-sessions"), "Stored interactive cowork sessions"),
            ("3P Claude Code VM Environment", os.path.join(LOCALAPPDATA, "Claude-3p", "claude-code-vm"), "Cowork virtual machine state directory")
        ]
    },
    "3": {
        "title": "Google Antigravity (IDE & CLI)",
        "desc": "IDE User Dir, CLI Library: 2,024 Skills, Global Config, Schemas",
        "items": [
            ("Antigravity IDE User Dir", os.path.join(USERPROFILE, ".antigravity-ide"), "Antigravity IDE workspace & state"),
            ("Antigravity CLI Working Dir", os.path.join(USERPROFILE, ".gemini", "antigravity-cli"), "Binary: agy.exe"),
            ("CLI Shared Skills Library (2,024 Skills)", os.path.join(USERPROFILE, ".gemini", "antigravity-cli", "skills"), "2,024 Skills / 2,136 SKILL.md"),
            ("Antigravity Built-in Skills (5 Skills)", os.path.join(USERPROFILE, ".gemini", "antigravity", "builtin", "skills"), "Core built-in agent skills"),
            ("CLI MCP Config (mcp_config.json)", os.path.join(USERPROFILE, ".gemini", "antigravity-cli", "mcp_config.json"), "codegraph, context-mode servers"),
            ("CLI Plugins Folder", os.path.join(USERPROFILE, ".gemini", "antigravity-cli", "plugins"), "clawbrowser, superpowers plugins"),
            ("Global Production Skills (60 Skills)", os.path.join(USERPROFILE, ".gemini", "config", "skills"), "Global production skills library"),
            ("Global MCP Config (4 Servers)", os.path.join(USERPROFILE, ".gemini", "config", "mcp_config.json"), "chrome-devtools, cloudrun, codegraph, context-mode"),
            ("Global Plugins Folder", os.path.join(USERPROFILE, ".gemini", "config", "plugins"), "chrome-devtools-plugin, superpowers"),
            ("MCP Schemas Folder (5 Schemas)", os.path.join(USERPROFILE, ".gemini", "antigravity", "mcp"), "Registered tool definitions"),
            ("Conversation Brain Logs & Artifacts", os.path.join(USERPROFILE, ".gemini", "antigravity", "brain"), "Agent transcripts & generated artifacts")
        ]
    },
    "4": {
        "title": "Cursor IDE",
        "desc": "skills-cursor (3), 5 .mdc Rules, 4 Subagents, mcp.json",
        "items": [
            ("Cursor Main Working Directory", os.path.join(USERPROFILE, ".cursor"), "Cursor user settings & configs"),
            ("Cursor Skills (3 Skills)", os.path.join(USERPROFILE, ".cursor", "skills-cursor"), "code-simplifier, commit-push-pr, techdebt"),
            ("Cursor Rules (5 .mdc Files)", os.path.join(USERPROFILE, ".cursor", "rules"), "build-discipline, code-index, context-tools, principles, response-style"),
            ("Cursor Custom Subagents (4 Agents)", os.path.join(USERPROFILE, ".cursor", "agents"), "code-reviewer, doc-generator, test-writer, verifier"),
            ("Cursor MCP Config (mcp.json)", os.path.join(USERPROFILE, ".cursor", "mcp.json"), "clawbrowser, codegraph, context-mode"),
            ("Cursor Plugins Directory", os.path.join(USERPROFILE, ".cursor", "plugins"), "Cursor extension plugins"),
            ("Cursor Roaming User Directory", os.path.join(APPDATA, "Cursor", "User"), "VS Code-compatible user settings")
        ]
    },
    "5": {
        "title": "OpenAI Codex CLI",
        "desc": "Active Skills (52), Plugins, config.toml, CCR TOML",
        "items": [
            ("Codex Main Working Directory", os.path.join(USERPROFILE, ".codex"), "Codex CLI agent environment"),
            ("Codex Active Skills (52 Skills)", os.path.join(USERPROFILE, ".codex", "skills"), "52 Deployed active skills"),
            ("Codex Plugins (4 Plugins)", os.path.join(USERPROFILE, ".codex", "plugins"), "clawbrowser with dedicated .mcp.json"),
            ("ClawBrowser Dedicated MCP Config", os.path.join(USERPROFILE, ".codex", "plugins", "clawbrowser", ".mcp.json"), "ClawBrowser MCP configuration"),
            ("Codex Core Config TOML", os.path.join(USERPROFILE, ".codex", "config.toml"), "Primary engine configuration"),
            ("Claude Code Router TOML", os.path.join(USERPROFILE, ".codex", "claude-code-router.config.toml"), "CCR model routing configuration"),
            ("Codex Global State JSON", os.path.join(USERPROFILE, ".codex", ".codex-global-state.json"), "Codex runtime state file")
        ]
    },
    "6": {
        "title": "Codex Desktop & OpenAI App",
        "desc": "Codex Desktop GUI, Web App, Local & Roaming Cache, OpenAI App",
        "items": [
            ("Codex Desktop Roaming Storage", os.path.join(APPDATA, "Codex"), "Codex desktop user application state"),
            ("Codex Desktop Web App & Runtime", os.path.join(APPDATA, "Codex", "web", "Codex"), "Codex browser app, captive runtime, cache"),
            ("Codex Desktop Local Storage", os.path.join(LOCALAPPDATA, "Codex"), "Local execution binaries, extension cache"),
            ("Codex Desktop Local Logs", os.path.join(LOCALAPPDATA, "Codex", "Logs"), "Diagnostic and execution logs"),
            ("OpenAI Windows Desktop App", os.path.join(LOCALAPPDATA, "OpenAI"), "Official ChatGPT / OpenAI desktop client"),
            ("OpenAI Codex Runtime & Bin", os.path.join(LOCALAPPDATA, "OpenAI", "Codex"), "Codex embedded binary runtime"),
            ("OpenAI Native Messaging Host", os.path.join(LOCALAPPDATA, "OpenAI", "extension"), "Chrome native host & extension connectors")
        ]
    },
    "7": {
        "title": "Nous Hermes Agent",
        "desc": "Primary & Local Skills (329+), Plugins (17), Source Repo",
        "items": [
            ("Hermes Primary Working Directory", os.path.join(USERPROFILE, ".hermes"), "Primary user environment"),
            ("Hermes Primary Skills (109 Skills)", os.path.join(USERPROFILE, ".hermes", "skills"), "109 Skills / 442 SKILL.md"),
            ("Hermes Primary Plugins (4 Plugins)", os.path.join(USERPROFILE, ".hermes", "plugins"), "clawbrowser, shardx, backups"),
            ("Hermes AppData Local Directory", os.path.join(LOCALAPPDATA, "hermes"), "Extended runtime storage"),
            ("Hermes AppData Skills (220 Skills)", os.path.join(LOCALAPPDATA, "hermes", "skills"), "220 Skills / 565 SKILL.md"),
            ("Hermes AppData Plugins (13 Plugins)", os.path.join(LOCALAPPDATA, "hermes", "plugins"), "superpowers, humanizer, shardx, etc."),
            ("Hermes MCP Schema Cache JSON", os.path.join(LOCALAPPDATA, "hermes", "cache", "mcp_schema_cache.json"), "Cached MCP schema catalog"),
            ("Local Framework Source Repo", os.path.join(AI_PROJECTS, "tools-frameworks", "hermes agent"), "Full engine source & tools"),
            ("Bundled MCP Server Archives", os.path.join(AI_PROJECTS, "tools-frameworks", "hermes agent", "mcps"), "Web Search & Chrome MCP archives")
        ]
    },
    "8": {
        "title": "VS Code & Cline",
        "desc": "Code User Config, Extensions, Cline Storage, MCPs",
        "items": [
            ("VS Code User Configuration Dir", os.path.join(APPDATA, "Code", "User"), "Global settings & shortcuts"),
            ("VS Code Installed Extensions", os.path.join(USERPROFILE, ".vscode", "extensions"), "Cline, Copilot, DeepSeek, Claude Code"),
            ("VS Code Native MCP (mcp.json)", os.path.join(APPDATA, "Code", "User", "mcp.json"), "playwright server"),
            ("Cline Extension Global Storage", os.path.join(APPDATA, "Code", "User", "globalStorage", "saoudrizwan.claude-dev"), "Cline tasks, sessions, cache"),
            ("Cline Extension MCP Config", os.path.join(APPDATA, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json"), "Cline GUI MCP configuration"),
            ("Cline CLI Working Directory", os.path.join(USERPROFILE, ".cline"), "Script: cline.ps1"),
            ("Cline CLI MCP Config (mcp_settings.json)", os.path.join(USERPROFILE, ".cline", "mcp_settings.json"), "Cline CLI MCP server config"),
            ("Cline CLI Runtime Data Dir", os.path.join(USERPROFILE, ".cline", "data"), "Tasks, sessions, sqlite DBs")
        ]
    },
    "9": {
        "title": "GitHub Copilot (CLI & IDE)",
        "desc": "Skills (40), Config, Logs, Multi-Router Extensions",
        "items": [
            ("Copilot CLI Working Directory", os.path.join(USERPROFILE, ".copilot"), "GitHub Copilot CLI state & cache"),
            ("Copilot Active Skills (40 Skills)", os.path.join(USERPROFILE, ".copilot", "skills"), "40 Cross-agent synced skills"),
            ("Copilot Configuration File (config.json)", os.path.join(USERPROFILE, ".copilot", "config.json"), "Copilot CLI configuration"),
            ("Copilot CLI Logs Directory", os.path.join(USERPROFILE, ".copilot", "logs"), "Execution & interaction logs"),
            ("VS Code Extensions Directory", os.path.join(USERPROFILE, ".vscode", "extensions"), "Includes DeepSeek Copilot & 9Router extensions"),
            ("Obsidian Copilot Directory", os.path.join(USERPROFILE, ".obsidian-copilot"), "Obsidian vault Copilot integration")
        ]
    },
    "10": {
        "title": "OpenCode AI Desktop & Ecosystem",
        "desc": "Desktop App, Studio Server, C: Configs & DB, Workspace Skills",
        "items": [
            ("OpenCode Desktop App Install Dir", os.path.join(LOCALAPPDATA, "Programs", "@opencode-aidesktop"), "OpenCode desktop application directory & OpenCode.exe"),
            ("OpenCode Desktop Binary (OpenCode.exe)", os.path.join(LOCALAPPDATA, "Programs", "@opencode-aidesktop", "OpenCode.exe"), "Main desktop application executable"),
            ("OpenCode Desktop Resources & Asar", os.path.join(LOCALAPPDATA, "Programs", "@opencode-aidesktop", "resources"), "app.asar (144MB), app-update.yml"),
            ("OpenCode Desktop Roaming Storage", os.path.join(APPDATA, "ai.opencode.desktop"), "Workspaces, SQLite drafts, UI settings"),
            ("OpenCode Desktop Settings File", os.path.join(APPDATA, "ai.opencode.desktop", "opencode.settings"), "Desktop client window & onboarding settings"),
            ("OpenCode Desktop Logs Directory", os.path.join(APPDATA, "ai.opencode.desktop", "logs"), "Desktop app main, renderer & crash logs"),
            ("OpenCode Desktop Auto-Updater", os.path.join(LOCALAPPDATA, "@opencode-aidesktop-updater"), "Desktop app update runtime"),
            ("OpenCode Global Config Dir (C:)", os.path.join(USERPROFILE, ".config", "opencode"), "Global config & Antigravity auth plugin"),
            ("OpenCode Global Config JSON", os.path.join(USERPROFILE, ".config", "opencode", "opencode.json"), "Global providers & model configuration"),
            ("OpenCode Global MCP & Config (opencode.jsonc)", os.path.join(USERPROFILE, ".config", "opencode", "opencode.jsonc"), "Active MCP servers (browsermcp, reddit, firecrawl, playwright) & providers"),
            ("OpenCode Global Skills Directory", os.path.join(USERPROFILE, ".config", "opencode", "skills"), "Global skills repository (~/.config/opencode/skills)"),
            ("OpenCode Global SQLite DB & State", os.path.join(USERPROFILE, ".local", "share", "opencode"), "opencode.db (154MB), auth, logs"),
            ("OpenCode Global Cache & Models", os.path.join(USERPROFILE, ".cache", "opencode"), "models.json (4.6MB) & binary cache"),
            ("OpenCode Studio Web Manager Server", os.path.join(APPDATA, "npm", "node_modules", "opencode-studio-server"), "Web/Studio GUI dashboard server"),
            ("OpenCode AI Autonomous CLI", os.path.join(APPDATA, "npm", "node_modules", "opencode-ai"), "Modular autonomous CLI agent (opencode)"),
            ("Official SST OpenCode VS Code Ext", os.path.join(USERPROFILE, ".vscode", "extensions", "sst-dev.opencode-0.0.13"), "Official SST OpenCode extension"),
            ("VS Code OpenCode Copilot Chat", os.path.join(USERPROFILE, ".vscode", "extensions", "ltmoerdani.opencode-copilot-chat-0.7.5"), "OpenCode extension for VS Code"),
            ("OpenCode Primary User Workspace", OPENCODE_WORKSPACE, "OpenCode user project workspace"),
            ("OpenCode Workspace Skills (40 Skills)", os.path.join(OPENCODE_WORKSPACE, ".opencode", "skills"), "40 Active deployed workspace skills"),
            ("Skills.sh Manager (Built-in)", os.path.join(OPENCODE_WORKSPACE, ".opencode", "skills", "skills-sh-manager"), "Built-in skills.sh manager skill"),
            ("OpenCode Workspace Config JSON", os.path.join(OPENCODE_WORKSPACE, "opencode.json"), "Project gateway config (27 models)")
        ]
    },
    "11": {
        "title": "OpenManus Bot & Operator",
        "desc": "Desktop App (openmausbot), Daemon Workspaces, Operator MCP",
        "items": [
            ("OpenManus Desktop GUI Storage", os.path.join(APPDATA, "openmausbot"), "Electron desktop client state & cache"),
            ("OpenManus Desktop Auto-Updater", os.path.join(LOCALAPPDATA, "openmausbot-updater"), "Desktop client updater runtime"),
            ("OpenManus Daemon Home (.openmausbot)", os.path.join(USERPROFILE, ".openmausbot"), "Bots, tools, vm-home, workspaces"),
            ("OpenManus Bot Profiles Config", os.path.join(USERPROFILE, ".openmausbot", "bots.json"), "Registered agent bots configuration"),
            ("OpenManus Active Workspaces", os.path.join(USERPROFILE, ".openmausbot", "workspaces"), "Multi-agent runtime workspaces"),
            ("Manus Computer Operator Root", os.path.join(USERPROFILE, ".manus"), "Manus operator environment"),
            ("Manus Computer Operator Runtime", os.path.join(USERPROFILE, ".manus", "manus-computer-operator"), "Operator logs and execution state"),
            ("Manus Operator MCP Config", os.path.join(USERPROFILE, ".config", "manus-computer-operator", "mcp_servers.json"), "Registered MCP server configs")
        ]
    },
    "12": {
        "title": "Local Models & Knowledge Engines",
        "desc": "Ollama Models (.ollama), OpenWhispr Voice, OpenTabs",
        "items": [
            ("Ollama Local CLI Data & Models", os.path.join(USERPROFILE, ".ollama"), "Model weights, cache, keys, config.json"),
            ("Ollama GGUF / Model Weights Dir", os.path.join(USERPROFILE, ".ollama", "models"), "Downloaded local LLM model weights"),
            ("Ollama Desktop App Roaming Dir", os.path.join(APPDATA, "ollama app.exe"), "Ollama Windows desktop GUI state"),
            ("OpenWhispr CLI Bridge Config", os.path.join(USERPROFILE, ".openwhispr"), "Voice-to-text bridge configuration"),
            ("OpenWhispr Desktop App Roaming", os.path.join(APPDATA, "open-whispr"), "Voice integration client data"),
            ("OpenTabs Browser Integration", os.path.join(USERPROFILE, ".opentabs"), "Browser extension connector & state"),
            ("OpenContext Local Database Hub", os.path.join(USERPROFILE, ".opencontext"), "opencontext.db & agent context cache")
        ]
    },
    "13": {
        "title": "Pi Coding Agent",
        "desc": "40 Skills, mcp.json, Backups",
        "items": [
            ("Pi Agent Working Directory", os.path.join(USERPROFILE, ".pi", "agent"), "Pi coding agent runtime"),
            ("Pi Agent Skills (40 Skills)", os.path.join(USERPROFILE, ".pi", "agent", "skills"), "Wiki & history ingest suite"),
            ("Pi Agent MCP Config (mcp.json)", os.path.join(USERPROFILE, ".pi", "agent", "mcp.json"), "codegraph, context-mode servers"),
            ("Pi Agent Backups Directory", os.path.join(USERPROFILE, ".pi", "backups"), "Backup archives")
        ]
    },
    "14": {
        "title": "Claude Code Router (CCR)",
        "desc": "Gateways, Model Catalogs, Routing TOMLs, Scoped Packages",
        "items": [
            ("CCR Main Roaming Runtime", os.path.join(APPDATA, "claude-code-router"), "Claude Code Router runtime state"),
            ("CCR Scoped Package Runtime", os.path.join(APPDATA, "@claude-code-router"), "Scoped package files & updater"),
            ("CCR Model Catalog JSON", os.path.join(USERPROFILE, ".codex", "ccr-model-catalog.json"), "Multi-model routing configuration"),
            ("CCR Switch Model Catalog JSON", os.path.join(USERPROFILE, ".codex", "cc-switch-model-catalog.json"), "Model switching catalog"),
            ("CCR Router Config TOML", os.path.join(USERPROFILE, ".codex", "claude-code-router.config.toml"), "Router configuration TOML")
        ]
    },
    "15": {
        "title": "Browser Automation Agents",
        "desc": "Browser-Use, Camofox Stealth Browser, ShardX, OpenContext",
        "items": [
            ("Camofox Stealth Browser Engine", os.path.join(AI_PROJECTS, "tools-frameworks", "camofox-browser"), "Anti-detect stealth browser framework"),
            ("OpenContext Unified Memory Engine", os.path.join(AI_PROJECTS, "tools-frameworks", "OpenContext"), "Unified memory & knowledge context engine"),
            ("Shard MCP Server & Multi-Profile", os.path.join(AI_PROJECTS, "extensions", "mcps", "shard mcp"), "Deployed Shard MCP with 3 skills & tools"),
            ("ShardX PowerShell Agent Toolkit", os.path.join(AI_PROJECTS, "github projects", "agents", "ShardX-PowerShell-Agent-Toolkit"), "PowerShell automation agent toolkit"),
            ("ClawBrowser Gemini Extension", os.path.join(USERPROFILE, ".gemini", "extensions", "clawbrowser"), "ClawBrowser integration for Gemini"),
            ("Camofox Browser MCP Package", os.path.join(APPDATA, "npm", "node_modules", "@askjo", "camofox-browser-mcp"), "Global npm Camofox MCP server")
        ]
    },
    "16": {
        "title": "Utility Agents (Kiro, Kilo, MCPorter)",
        "desc": "Kiro: 40, Kilo: 6, MCPorter Switcher",
        "items": [
            ("Kiro Agent Skills (40 Skills)", os.path.join(USERPROFILE, ".kiro", "skills"), "Rule enforcer agent skills"),
            ("Kilo Agent Skills (6 Skills)", os.path.join(USERPROFILE, ".kilo", "skills"), "Fast task execution skills"),
            ("MCPorter Config (mcporter.json)", os.path.join(USERPROFILE, ".mcporter", "mcporter.json"), "Global MCP switcher config: exa")
        ]
    },
    "17": {
        "title": "Master Skills Warehouses (D: Drive)",
        "desc": "10 Curated Repositories (1,350+ Upstream Skills)",
        "items": [
            ("claude-skills (973 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "claude-skills"), "40 Categories / 973 SKILL.md / 3,222 MDs"),
            ("hermes-skills (309 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "hermes-skills"), "58 Categories / 309 SKILL.md / 549 MDs"),
            ("marketingagentskills (33 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "marketingagentskills"), "2 Categories / 33 SKILL.md / 142 MDs"),
            ("linkedin-skills (28 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "linkedin-skills"), "11 Categories / 28 SKILL.md / 134 MDs"),
            ("andrej-karpathy-skills", os.path.join(AI_PROJECTS, "github projects", "skills", "andrej-karpathy-skills"), "3 Categories / 1 Skill / 6 MDs"),
            ("ELI5 Simplification Skills", os.path.join(AI_PROJECTS, "github projects", "skills", "ELI5"), "4 Categories / 2 Skills / 5 MDs"),
            ("health-skill Informatics", os.path.join(AI_PROJECTS, "github projects", "skills", "health-skill"), "12 Categories / 1 Skill / 54 MDs"),
            ("last30days-skill Scraper", os.path.join(AI_PROJECTS, "github projects", "skills", "last30days-skill"), "14 Categories / 1 Skill / 72 MDs"),
            ("claude-skills-llm-council", os.path.join(AI_PROJECTS, "github projects", "skills", "claude-skills-llm-council"), "Multi-LLM deliberation & consensus"),
            ("prompt-master Engineering", os.path.join(AI_PROJECTS, "github projects", "skills", "prompt-master"), "1 Category / 1 Skill / 4 MDs"),
            ("Master Skills Hub Directory", os.path.join(AI_PROJECTS, "github projects", "skills"), "Upstream skills root folder")
        ]
    },
    "18": {
        "title": "Master Agents & Personas (D: Drive)",
        "desc": "agency-agents (325 Roles), ShardX Toolkit",
        "items": [
            ("agency-agents (325 Personas)", os.path.join(AI_PROJECTS, "github projects", "agents", "agency-agents"), "23 Role Categories / 325 Agent Files"),
            ("ShardX PowerShell Agent Toolkit", os.path.join(AI_PROJECTS, "github projects", "agents", "ShardX-PowerShell-Agent-Toolkit"), "PowerShell execution & toolkit"),
            ("Master Agents Root Directory", os.path.join(AI_PROJECTS, "github projects", "agents"), "Agents root repository folder")
        ]
    },
    "19": {
        "title": "Master MCPs, Extensions & Frameworks (D: Drive)",
        "desc": "markdownify-mcp, shard mcp, camofox, OpenContext, artemis",
        "items": [
            ("markdownify-mcp Source Repo", os.path.join(AI_PROJECTS, "github projects", "mcp-servers", "markdownify-mcp"), "6 Subdirs / 8,003 Files (MCP Source)"),
            ("shard mcp Directory", os.path.join(AI_PROJECTS, "extensions", "mcps", "shard mcp"), "3 Skills / 175 MDs / 3,571 Files"),
            ("Project Extensions Plugins", os.path.join(AI_PROJECTS, "extensions", "plugins"), "Hermes-ShardX, i-have-adhd, last30days"),
            ("hermes agent Framework Engine", os.path.join(AI_PROJECTS, "tools-frameworks", "hermes agent"), "Full engine source & tools"),
            ("camofox-browser Stealth Engine", os.path.join(AI_PROJECTS, "tools-frameworks", "camofox-browser"), "Browser automation engine"),
            ("OpenContext Unified Memory", os.path.join(AI_PROJECTS, "tools-frameworks", "OpenContext"), "Unified context & retrieval engine"),
            ("artemis Autonomous Platform", os.path.join(AI_PROJECTS, "tools-frameworks", "artemis"), "Artemis multi-agent platform"),
            ("Claude Control Centers & Gateways", os.path.join(AI_PROJECTS, "github projects", "claude"), "11 Control center repositories")
        ]
    },
    "20": {
        "title": "Master ai_projects Root Hub",
        "desc": AI_PROJECTS,
        "items": [
            ("Master ai_projects Hub Root", AI_PROJECTS, "Root storage directory for all AI projects"),
            ("Extensions Directory", os.path.join(AI_PROJECTS, "extensions"), "mcps and plugins storage"),
            ("GitHub Projects Root", os.path.join(AI_PROJECTS, "github projects"), "Git clones & reference projects"),
            ("Notes Vaults Root", os.path.join(AI_PROJECTS, "notes-vaults"), "Obsidian & wiki vaults"),
            ("Tools & Frameworks Root", os.path.join(AI_PROJECTS, "tools-frameworks"), "Local agent engines & runtimes")
        ]
    }
}

# ================= TUI RENDER ENGINE =================

FOLDER_DATA = DATA


# ANSI Colors & Controls
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_DIM = "\033[90m"
CLR_REVERSE = "\033[7m"
CLR_GREEN = "\033[1;32m"
CLR_YELLOW = "\033[1;33m"
CLR_RED = "\033[1;31m"
CLR_CYAN = "\033[1;36m"
CLR_WHITE = "\033[1;37m"
CLR_MAGENTA = "\033[1;35m"
CLR_HIDE_CURSOR = "\033[?25l"
CLR_SHOW_CURSOR = "\033[?25h"

def init_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_frame(lines):
    buf = "\033[H"
    for line in lines:
        buf += line + "\033[K\n"
    buf += "\033[J"
    sys.stdout.write(buf)
    sys.stdout.flush()

def read_key():
    if not HAS_MSVCRT:
        return input().strip()
    ch = msvcrt.getch()
    if ch in (b'\x00', b'\xe0'):
        ch2 = msvcrt.getch()
        if ch2 == b'H': return 'UP'
        elif ch2 == b'P': return 'DOWN'
        elif ch2 == b'K': return 'LEFT'
        elif ch2 == b'M': return 'RIGHT'
        elif ch2 == b'I': return 'PGUP'
        elif ch2 == b'Q': return 'PGDN'
        elif ch2 == b'G': return 'HOME'
        elif ch2 == b'O': return 'END'
        elif ch2 == b'S': return 'DEL'
        return 'SPECIAL'
    elif ch == b' ': return 'SPACE'
    elif ch in (b'\r', b'\n'): return 'ENTER'
    elif ch == b'\x1b': return 'ESC'
    elif ch == b'\x08': return 'BACKSPACE'
    elif ch == b'\t': return 'TAB'
    else:
        try:
            return ch.decode('utf-8', errors='ignore')
        except:
            return ''

def find_cli_executable(name):
    cmd = 'where.exe' if os.name == 'nt' else 'which'
    try:
        out = os.popen(f'{cmd} {name} 2>nul').read().strip()
        if out:
            return out.splitlines()[0]
    except Exception:
        pass
    return None

# ================= DYNAMIC AGENT AUTO-DISCOVERY ENGINE =================

def discover_installed_agents():
    """
    Dynamically scans the system for installed AI coding agents (CLIs, Desktop apps, and configuration roots).
    Works on any system by verifying CLI presence in PATH and directory trees.
    """
    detected = {}

    # 1. Google Antigravity
    agy_cli = find_cli_executable('agy')
    agy_ide = os.path.exists(os.path.join(LOCALAPPDATA, "Programs", "antigravity")) or os.path.exists(os.path.join(USERPROFILE, ".antigravity-ide"))
    agy_cfg = os.path.join(USERPROFILE, ".gemini", "config", "mcp_config.json")
    if agy_cli or agy_ide or os.path.exists(agy_cfg):
        detected["antigravity"] = {
            "id": "antigravity",
            "name": "Google Antigravity (IDE & CLI)",
            "cli": agy_cli or "Installed (Desktop/Service)",
            "skills_dir": os.path.join(USERPROFILE, ".gemini", "config", "skills"),
            "skills_available": os.path.join(USERPROFILE, ".gemini", "config", "skills-available"),
            "mcp_file": agy_cfg,
            "mcp_format": "standard_json",
            "plugins_dir": os.path.join(USERPROFILE, ".gemini", "config", "plugins"),
            "alt_skills": [os.path.join(USERPROFILE, ".gemini", "antigravity", "skills")],
            "alt_mcps": [os.path.join(USERPROFILE, ".gemini", "antigravity", "mcp_config.json")]
        }

    # 2. Claude (Code CLI & Desktop)
    claude_cli = find_cli_executable('claude')
    claude_d1 = os.path.join(LOCALAPPDATA, "Claude", "claude_desktop_config.json")
    claude_d2 = os.path.join(LOCALAPPDATA, "Claude-3p", "claude_desktop_config.json")
    claude_root = os.path.join(USERPROFILE, ".claude")
    if claude_cli or os.path.exists(claude_d1) or os.path.exists(claude_root) or os.path.exists(os.path.join(USERPROFILE, ".claude.json")):
        detected["claude"] = {
            "id": "claude",
            "name": "Claude (Code CLI & Desktop)",
            "cli": claude_cli or "Installed (Desktop App)",
            "skills_dir": os.path.join(USERPROFILE, ".claude", "skills"),
            "skills_available": os.path.join(USERPROFILE, ".claude", "skills-available"),
            "mcp_file": os.path.join(USERPROFILE, ".claude.json"),
            "mcp_format": "standard_json",
            "plugins_dir": os.path.join(USERPROFILE, ".claude", "plugins"),
            "alt_mcps": [p for p in [os.path.join(USERPROFILE, ".claude", "mcp.json"), claude_d1, claude_d2] if os.path.exists(p)]
        }

    # 3. Cursor IDE
    cursor_cli = find_cli_executable('cursor')
    cursor_dir = os.path.join(USERPROFILE, ".cursor")
    if cursor_cli or os.path.exists(cursor_dir) or os.path.exists(os.path.join(APPDATA, "Cursor")):
        detected["cursor"] = {
            "id": "cursor",
            "name": "Cursor IDE",
            "cli": cursor_cli or "Installed (Editor)",
            "skills_dir": os.path.join(USERPROFILE, ".cursor", "skills-cursor"),
            "skills_available": os.path.join(USERPROFILE, ".cursor", "skills-available"),
            "mcp_file": os.path.join(USERPROFILE, ".cursor", "mcp.json"),
            "mcp_format": "standard_json",
            "plugins_dir": os.path.join(USERPROFILE, ".cursor", "plugins")
        }

    # 4. OpenCode (Desktop App & CLI)
    opencode_desktop_dir = os.path.join(LOCALAPPDATA, "Programs", "@opencode-aidesktop")
    opencode_exe = os.path.join(opencode_desktop_dir, "OpenCode.exe")
    opencode_cli = find_cli_executable('opencode')
    opencode_cfg_dir = os.path.join(USERPROFILE, ".config", "opencode")
    opencode_json = os.path.join(opencode_cfg_dir, "opencode.json")
    opencode_jsonc = os.path.join(opencode_cfg_dir, "opencode.jsonc")
    opencode_global_skills = os.path.join(opencode_cfg_dir, "skills")
    opencode_ws_skills = os.path.join(OPENCODE_WORKSPACE, ".opencode", "skills")
    opencode_ws_avail = os.path.join(OPENCODE_WORKSPACE, ".opencode", "skills-available")
    opencode_ws_json = os.path.join(OPENCODE_WORKSPACE, "opencode.json")

    # Determine primary MCP config (prefer file containing active 'mcp' block)
    active_mcp_candidate = None
    for cand in [opencode_jsonc, opencode_json, opencode_ws_json]:
        if os.path.exists(cand):
            try:
                with open(cand, "r", encoding="utf-8") as f:
                    _cdata = json.load(f)
                    if "mcp" in _cdata or "mcpServers" in _cdata:
                        active_mcp_candidate = cand
                        break
            except Exception:
                pass
    if not active_mcp_candidate:
        active_mcp_candidate = opencode_jsonc if os.path.exists(opencode_jsonc) else (opencode_json if os.path.exists(opencode_json) else opencode_ws_json)

    if opencode_cli or os.path.exists(opencode_desktop_dir) or os.path.exists(opencode_cfg_dir) or os.path.exists(opencode_ws_skills):
        detected["opencode"] = {
            "id": "opencode",
            "name": "OpenCode AI (Desktop & CLI)",
            "cli": opencode_exe if os.path.exists(opencode_exe) else (opencode_cli or "Installed"),
            "desktop_dir": opencode_desktop_dir,
            "skills_dir": opencode_ws_skills if os.path.exists(opencode_ws_skills) else opencode_global_skills,
            "skills_available": opencode_ws_avail,
            "alt_skills": [p for p in [opencode_global_skills, opencode_ws_skills] if os.path.exists(p)],
            "mcp_file": active_mcp_candidate,
            "mcp_format": "opencode_json",
            "plugins_dir": os.path.join(opencode_cfg_dir, "node_modules"),
            "config_file": opencode_jsonc if os.path.exists(opencode_jsonc) else opencode_json,
            "alt_mcps": [p for p in [opencode_jsonc, opencode_json, opencode_ws_json] if os.path.exists(p) and p != active_mcp_candidate]
        }

    # 5. Nous Hermes Agent
    hermes_cli = find_cli_executable('hermes')
    hermes_local = os.path.join(LOCALAPPDATA, "hermes")
    hermes_root = os.path.join(USERPROFILE, ".hermes")
    if hermes_cli or os.path.exists(hermes_local) or os.path.exists(hermes_root):
        detected["hermes"] = {
            "id": "hermes",
            "name": "Nous Hermes Agent",
            "cli": hermes_cli or "Installed (Local Runtimes)",
            "skills_dir": os.path.join(hermes_local, "skills"),
            "skills_available": os.path.join(hermes_local, "skills-available"),
            "alt_skills": [os.path.join(hermes_root, "skills")],
            "mcp_file": os.path.join(hermes_local, "config.yaml"),
            "mcp_format": "hermes_yaml",
            "plugins_dir": os.path.join(hermes_local, "plugins")
        }

    # 6. OpenAI Codex Agent
    codex_root = os.path.join(USERPROFILE, ".codex")
    if os.path.exists(codex_root):
        detected["codex"] = {
            "id": "codex",
            "name": "OpenAI Codex Agent",
            "cli": "Installed (.codex)",
            "skills_dir": os.path.join(codex_root, "skills"),
            "skills_available": os.path.join(codex_root, "skills-available"),
            "mcp_file": os.path.join(codex_root, "plugins", "clawbrowser", ".mcp.json"),
            "mcp_format": "standard_json",
            "plugins_dir": os.path.join(codex_root, "plugins")
        }

    # 7. VS Code & Cline
    code_cli = find_cli_executable('code')
    cline_mcp = os.path.join(APPDATA, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json")
    vscode_mcp = os.path.join(APPDATA, "Code", "User", "mcp.json")
    cline_dir = os.path.join(USERPROFILE, ".cline")
    if code_cli or os.path.exists(cline_mcp) or os.path.exists(cline_dir):
        detected["cline"] = {
            "id": "cline",
            "name": "VS Code & Cline",
            "cli": code_cli or "Installed (VS Code Extension)",
            "skills_dir": os.path.join(USERPROFILE, ".cline", "skills"),
            "skills_available": os.path.join(USERPROFILE, ".cline", "skills-available"),
            "mcp_file": cline_mcp if os.path.exists(cline_mcp) else vscode_mcp,
            "mcp_format": "cline_json",
            "plugins_dir": None,
            "alt_mcps": [p for p in [os.path.join(cline_dir, "mcp_settings.json"), vscode_mcp] if os.path.exists(p)]
        }

    # 8. Pi Coding Agent
    pi_dir = os.path.join(USERPROFILE, ".pi", "agent")
    if os.path.exists(pi_dir):
        detected["pi"] = {
            "id": "pi",
            "name": "Pi Coding Agent",
            "cli": "Installed (.pi)",
            "skills_dir": os.path.join(pi_dir, "skills"),
            "skills_available": os.path.join(pi_dir, "skills-available"),
            "mcp_file": os.path.join(pi_dir, "mcp.json"),
            "mcp_format": "standard_json",
            "plugins_dir": None
        }

    # 9. GitHub Copilot CLI
    copilot_dir = os.path.join(USERPROFILE, ".copilot")
    if os.path.exists(copilot_dir):
        detected["copilot"] = {
            "id": "copilot",
            "name": "GitHub Copilot CLI",
            "cli": "Installed (.copilot)",
            "skills_dir": os.path.join(copilot_dir, "skills"),
            "skills_available": os.path.join(copilot_dir, "skills-available"),
            "mcp_file": None,
            "plugins_dir": None
        }

    # 10. Kiro Agent
    kiro_dir = os.path.join(USERPROFILE, ".kiro")
    if os.path.exists(kiro_dir):
        detected["kiro"] = {
            "id": "kiro",
            "name": "Kiro Agent",
            "cli": "Installed (.kiro)",
            "skills_dir": os.path.join(kiro_dir, "skills"),
            "skills_available": os.path.join(kiro_dir, "skills-available"),
            "mcp_file": None,
            "plugins_dir": None
        }

    # 11. Kilo Agent
    kilo_dir = os.path.join(USERPROFILE, ".kilo")
    if os.path.exists(kilo_dir):
        detected["kilo"] = {
            "id": "kilo",
            "name": "Kilo Agent",
            "cli": "Installed (.kilo)",
            "skills_dir": os.path.join(kilo_dir, "skills"),
            "skills_available": os.path.join(kilo_dir, "skills-available"),
            "mcp_file": None,
            "plugins_dir": None
        }

    return detected

# ================= MASTER SKILLS WAREHOUSES =================

WAREHOUSES = [
    ("claude-skills (973 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "claude-skills")),
    ("hermes-skills (309 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "hermes-skills")),
    ("marketingagentskills (33 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "marketingagentskills")),
    ("linkedin-skills (28 Skills)", os.path.join(AI_PROJECTS, "github projects", "skills", "linkedin-skills")),
    ("agency-agents (325 Roles)", os.path.join(AI_PROJECTS, "github projects", "agents", "agency-agents")),
    ("andrej-karpathy-skills", os.path.join(AI_PROJECTS, "github projects", "skills", "andrej-karpathy-skills")),
    ("ELI5 Simplification", os.path.join(AI_PROJECTS, "github projects", "skills", "ELI5")),
    ("health-skill Informatics", os.path.join(AI_PROJECTS, "github projects", "skills", "health-skill")),
    ("last30days-skill Scraper", os.path.join(AI_PROJECTS, "github projects", "skills", "last30days-skill")),
    ("prompt-master Engineering", os.path.join(AI_PROJECTS, "github projects", "skills", "prompt-master")),
    ("claude-skills-llm-council", os.path.join(AI_PROJECTS, "github projects", "skills", "claude-skills-llm-council"))
]

# ================= SYSTEM INSPECTION HELPERS =================

def get_dir_items(path):
    if not path or not os.path.exists(path):
        return []
    try:
        return sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
    except Exception:
        return []

def get_agent_skills(agent_cfg):
    active = get_dir_items(agent_cfg.get("skills_dir"))
    available = get_dir_items(agent_cfg.get("skills_available"))
    return active, available

def get_agent_plugins(agent_cfg):
    p_dir = agent_cfg.get("plugins_dir")
    if p_dir and os.path.exists(p_dir):
        return get_dir_items(p_dir)
    # Special check for OpenCode plugins array in JSON
    if agent_cfg.get("mcp_format") == "opencode_json":
        cfg_file = agent_cfg.get("config_file")
        if cfg_file and os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("plugin", [])
            except:
                pass
    return []

def read_mcp_config(agent_cfg):
    mcp_file = agent_cfg.get("mcp_file")
    mcp_format = agent_cfg.get("mcp_format", "standard_json")
    if not mcp_file or not os.path.exists(mcp_file):
        return {}, {}

    active = {}
    disabled = {}

    try:
        if mcp_format in ("standard_json", "cline_json"):
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            for k, v in servers.items():
                is_dis = v.get("disabled", False) or not v.get("enabled", True)
                if is_dis: disabled[k] = v
                else: active[k] = v
        elif mcp_format == "opencode_json":
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # OpenCode can store in "mcp" or "mcpServers"
            servers = data.get("mcp", {}) or data.get("mcpServers", {})
            for k, v in servers.items():
                is_dis = not v.get("enabled", True) if isinstance(v, dict) else False
                if is_dis: disabled[k] = v
                else: active[k] = v
        elif mcp_format == "hermes_yaml":
            if yaml:
                with open(mcp_file, "r", encoding="utf-8") as f:
                    ydata = yaml.safe_load(f) or {}
                servers = ydata.get("mcp_servers", {})
                for k, v in servers.items():
                    if isinstance(v, dict):
                        is_dis = not v.get("enabled", True)
                        if is_dis: disabled[k] = v
                        else: active[k] = v
            else:
                with open(mcp_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                in_mcp = False
                for line in lines:
                    stripped = line.strip()
                    if line.startswith("mcp_servers:"):
                        in_mcp = True
                        continue
                    if in_mcp and line and not line.startswith(" ") and not line.startswith("\t") and not stripped.startswith("#"):
                        break
                    if in_mcp:
                        m = re.match(r"^  ([a-zA-Z0-9_\-\.]+):", line)
                        if m:
                            sname = m.group(1)
                            if sname not in ("command", "args", "env", "enabled", "url", "auth", "connect_timeout", "transport", "tools"):
                                active[sname] = {"raw": True}
    except Exception:
        pass

    return active, disabled

def save_mcp_servers(agent_cfg, active_set):
    mcp_file = agent_cfg.get("mcp_file")
    mcp_format = agent_cfg.get("mcp_format", "standard_json")
    if not mcp_file or not os.path.exists(mcp_file):
        return

    if mcp_format in ("standard_json", "cline_json"):
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            servers = data.get("mcpServers", {})
            for k, v in servers.items():
                if k in active_set:
                    v["disabled"] = False
                    v["enabled"] = True
                else:
                    v["disabled"] = True
                    v["enabled"] = False
            with open(mcp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            for alt_f in agent_cfg.get("alt_mcps", []):
                if os.path.exists(alt_f):
                    try:
                        with open(alt_f, "r", encoding="utf-8") as f:
                            alt_data = json.load(f)
                        for k, v in alt_data.get("mcpServers", {}).items():
                            if k in active_set:
                                v["disabled"] = False
                                v["enabled"] = True
                            else:
                                v["disabled"] = True
                                v["enabled"] = False
                        with open(alt_f, "w", encoding="utf-8") as f:
                            json.dump(alt_data, f, indent=2)
                    except Exception:
                        pass
        except Exception:
            pass
    elif mcp_format == "opencode_json":
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            target_key = "mcp" if "mcp" in data else "mcpServers"
            if target_key in data:
                for k, v in data[target_key].items():
                    if isinstance(v, dict):
                        v["enabled"] = (k in active_set)
            with open(mcp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

# ================= UNIVERSAL AI AGENT MODEL & PROVIDER ENGINE =================

def backup_config_file(filepath):
    """Creates a timestamped or .bak copy of any config file before modification."""
    if not filepath or not os.path.exists(filepath):
        return
    try:
        shutil.copy2(filepath, filepath + ".bak")
    except Exception:
        pass

def test_ping_endpoint(url, timeout=2.5):
    """Fast probe to check if an AI endpoint or local server (Ollama, LM Studio, vLLM, OpenRouter) is alive."""
    if not url:
        return False, "Empty URL"
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    
    probe_targets = [url.rstrip('/') + '/models', url]
    for target in probe_targets:
        try:
            req = urllib.request.Request(target, headers={'User-Agent': 'UniversalAgentCustomizer/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return True, f"Online (HTTP {resp.status})"
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404, 405):
                return True, f"Online (HTTP {e.code} - Auth/Endpoint Verified)"
            return False, f"HTTP Error {e.code}"
        except Exception:
            continue
    return False, "Offline / Unreachable (Timeout)"

PROVIDER_PRESETS = {
    "ollama": {
        "id": "ollama",
        "name": "Ollama (Local)",
        "baseURL": "http://localhost:11434/v1",
        "default_models": ["llama3.3", "qwen2.5-coder:32b", "deepseek-r1:14b", "mistral:7b", "codellama:34b"],
        "requires_key": False
    },
    "lmstudio": {
        "id": "lmstudio",
        "name": "LM Studio / LocalAI / vLLM",
        "baseURL": "http://localhost:1234/v1",
        "default_models": ["local-model", "qwen2.5-coder", "deepseek-coder"],
        "requires_key": False
    },
    "openrouter": {
        "id": "openrouter",
        "name": "OpenRouter Cloud",
        "baseURL": "https://openrouter.ai/api/v1",
        "default_models": [
            "deepseek/deepseek-r1",
            "deepseek/deepseek-chat",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "qwen/qwen-2.5-coder-32b-instruct"
        ],
        "requires_key": True
    },
    "deepseek": {
        "id": "deepseek",
        "name": "DeepSeek API",
        "baseURL": "https://api.deepseek.com/v1",
        "default_models": ["deepseek-chat", "deepseek-reasoner"],
        "requires_key": True
    },
    "groq": {
        "id": "groq",
        "name": "Groq Cloud Fast Inference",
        "baseURL": "https://api.groq.com/openai/v1",
        "default_models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "deepseek-r1-distill-llama-70b"],
        "requires_key": True
    },
    "anthropic": {
        "id": "anthropic",
        "name": "Anthropic Claude Official",
        "baseURL": "https://api.anthropic.com",
        "default_models": ["claude-3-7-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-latest"],
        "requires_key": True
    },
    "openai": {
        "id": "openai",
        "name": "OpenAI Official API",
        "baseURL": "https://api.openai.com/v1",
        "default_models": ["gpt-4o", "gpt-4o-mini", "o1", "o3-mini"],
        "requires_key": True
    },
    "custom": {
        "id": "custom",
        "name": "Custom OpenAI-Compatible Endpoint",
        "baseURL": "http://localhost:8000/v1",
        "default_models": ["custom-model"],
        "requires_key": False
    }
}

def get_agent_models_and_providers(agent_cfg):
    """
    Returns unified model and provider metadata for any agent.
    Format:
    {
       "config_file": str,
       "active_model": str,
       "active_provider": str,
       "base_url": str,
       "has_key": bool,
       "providers": { prov_id: { "name": ..., "baseURL": ..., "models": [...] } },
       "models": [ { "id": ..., "name": ..., "provider": ..., "is_active": bool, "is_enabled": bool } ]
    }
    """
    aid = agent_cfg.get("id")
    result = {
        "config_file": None,
        "active_model": "default",
        "active_provider": "default",
        "base_url": "default",
        "has_key": False,
        "providers": {},
        "models": []
    }

    # 1. OpenCode
    if aid == "opencode":
        cf = agent_cfg.get("config_file") or os.path.join(USERPROFILE, ".config", "opencode", "opencode.json")
        result["config_file"] = cf
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                active = data.get("model", "auto")
                result["active_model"] = active
                provs = data.get("provider", {})
                for pid, pdata in provs.items():
                    b_url = pdata.get("options", {}).get("baseURL", "")
                    p_key = bool(pdata.get("options", {}).get("apiKey"))
                    p_models = pdata.get("models", {})
                    bl = pdata.get("blacklist", [])
                    wl = pdata.get("whitelist", [])
                    result["providers"][pid] = {
                        "name": pdata.get("name", pid),
                        "baseURL": b_url,
                        "has_key": p_key,
                        "models": list(p_models.keys())
                    }
                    if active and (active.startswith(pid + "/") or active in p_models):
                        result["active_provider"] = pid
                        result["base_url"] = b_url
                        result["has_key"] = p_key

                    for mid, mval in p_models.items():
                        mname = mval.get("name", mid) if isinstance(mval, dict) else mid
                        full_id = f"{pid}/{mid}"
                        is_act = (active == full_id or active == mid)
                        is_en = (mid not in bl) and (not wl or mid in wl)
                        result["models"].append({
                            "id": mid,
                            "full_id": full_id,
                            "name": mname,
                            "provider": pid,
                            "is_active": is_act,
                            "is_enabled": is_en
                        })
            except Exception:
                pass

    # 2. Claude Code
    elif aid == "claude":
        cf = os.path.join(USERPROFILE, ".claude", "settings.json")
        result["config_file"] = cf
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                env = data.get("env", {})
                active = env.get("ANTHROPIC_MODEL", "default")
                b_url = env.get("ANTHROPIC_BASE_URL") or env.get("ANTHROPIC_API_BASE_URL", "https://api.anthropic.com")
                has_k = bool(env.get("ANTHROPIC_AUTH_TOKEN") or env.get("ANTHROPIC_API_KEY"))
                result["active_model"] = active
                result["active_provider"] = "Anthropic / Gateway"
                result["base_url"] = b_url
                result["has_key"] = has_k

                known_claude_models = [
                    ("ANTHROPIC_MODEL", env.get("ANTHROPIC_MODEL", "default"), "Active/Default Model"),
                    ("ANTHROPIC_DEFAULT_SONNET_MODEL", env.get("ANTHROPIC_DEFAULT_SONNET_MODEL", "claude-3-5-sonnet"), "Sonnet Tier"),
                    ("ANTHROPIC_DEFAULT_OPUS_MODEL", env.get("ANTHROPIC_DEFAULT_OPUS_MODEL", "claude-3-opus"), "Opus Tier"),
                    ("ANTHROPIC_DEFAULT_HAIKU_MODEL", env.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "claude-3-5-haiku"), "Haiku Tier"),
                    ("ANTHROPIC_SMALL_FAST_MODEL", env.get("ANTHROPIC_SMALL_FAST_MODEL", "claude-3-5-haiku"), "Small Fast Model")
                ]
                for key_name, m_val, label in known_claude_models:
                    result["models"].append({
                        "id": m_val,
                        "full_id": m_val,
                        "name": f"{m_val} ({label})",
                        "provider": "claude_env",
                        "is_active": (m_val == active and key_name == "ANTHROPIC_MODEL"),
                        "is_enabled": True
                    })
            except Exception:
                pass

    # 3. Google Antigravity
    elif aid == "antigravity":
        cf = os.path.join(USERPROFILE, ".gemini", "antigravity-cli", "settings.json")
        result["config_file"] = cf
        active = "gemini-3.8-flash-high"
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    active = d.get("model", active)
            except Exception:
                pass
        result["active_model"] = active
        result["active_provider"] = "Google DeepMind Vertex / Antigravity"
        result["base_url"] = "Native Vertex AI"
        result["has_key"] = True

        agy_models = [
            ("gemini-3.8-flash-high", "Gemini 3.8 Flash (High Effort)"),
            ("gemini-3.8-flash-medium", "Gemini 3.8 Flash (Medium Effort)"),
            ("gemini-3.8-flash-low", "Gemini 3.8 Flash (Low Effort)"),
            ("gemini-3.7-flash-high", "Gemini 3.7 Flash (High Effort)"),
            ("gemini-3.1-pro-high", "Gemini 3.1 Pro (High Reasoning)"),
            ("claude-sonnet-4-6", "Claude Sonnet 4.6 (Thinking Mode)"),
            ("claude-opus-4-6-thinking", "Claude Opus 4.6 (Extended Thinking)"),
            ("gpt-oss-120b-medium", "GPT-OSS 120B (Medium Effort)")
        ]
        for mid, mname in agy_models:
            result["models"].append({
                "id": mid,
                "full_id": mid,
                "name": mname,
                "provider": "antigravity",
                "is_active": (mid == active),
                "is_enabled": True
            })

    # 4. OpenAI Codex Agent
    elif aid == "codex":
        cf = os.path.join(USERPROFILE, ".codex", "config.toml")
        result["config_file"] = cf
        if os.path.exists(cf):
            try:
                active_m = "default"
                active_p = "default"
                with open(cf, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line.startswith("model =") or line.startswith("model="):
                        active_m = line.split("=", 1)[1].strip().strip('"\'')
                    elif line.startswith("model_provider =") or line.startswith("model_provider="):
                        active_p = line.split("=", 1)[1].strip().strip('"\'')
                result["active_model"] = active_m
                result["active_provider"] = active_p
                result["base_url"] = "Configured in config.toml"
                result["has_key"] = True

                result["models"].append({
                    "id": active_m,
                    "full_id": active_m,
                    "name": f"{active_m} (Active Codex Model)",
                    "provider": active_p,
                    "is_active": True,
                    "is_enabled": True
                })
            except Exception:
                pass

    # 5. Nous Hermes Agent
    elif aid == "hermes":
        cf = os.path.join(LOCALAPPDATA, "hermes", "config.yaml")
        if not os.path.exists(cf):
            cf = os.path.join(USERPROFILE, ".hermes", "config.yaml")
        result["config_file"] = cf
        if os.path.exists(cf) and yaml is not None:
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    ydata = yaml.safe_load(f)
                msec = ydata.get("model", {})
                result["active_model"] = msec.get("default", "auto")
                result["active_provider"] = msec.get("provider", "default")
                result["base_url"] = msec.get("base_url", "Native")
                result["has_key"] = bool(msec.get("key_env") or ydata.get("SHARDX_API"))

                provs = ydata.get("providers", {})
                for pid, pdata in provs.items():
                    p_base = pdata.get("base_url", "")
                    p_models = pdata.get("models", {})
                    result["providers"][pid] = {
                        "name": pdata.get("name", pid),
                        "baseURL": p_base,
                        "has_key": True,
                        "models": list(p_models.keys()) if isinstance(p_models, dict) else []
                    }
                    if isinstance(p_models, dict):
                        for mid in p_models.keys():
                            result["models"].append({
                                "id": mid,
                                "full_id": mid,
                                "name": mid,
                                "provider": pid,
                                "is_active": (mid == result["active_model"]),
                                "is_enabled": True
                            })
                # Add aliases
                aliases = msec.get("aliases", {})
                for al_name, al_val in aliases.items():
                    al_m = al_val.get("model", al_name) if isinstance(al_val, dict) else str(al_val)
                    result["models"].append({
                        "id": al_name,
                        "full_id": al_m,
                        "name": f"{al_name} -> {al_m}",
                        "provider": "alias",
                        "is_active": (al_name == result["active_model"] or al_m == result["active_model"]),
                        "is_enabled": True
                    })
            except Exception:
                pass

    # 6. Cursor IDE
    elif aid == "cursor":
        cf = os.path.join(APPDATA, "Cursor", "User", "settings.json")
        result["config_file"] = cf
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    d = json.load(f)
                result["base_url"] = d.get("cursor.general.openAiBaseUrl", "https://api.openai.com/v1")
                result["active_provider"] = "Custom OpenAI / Cursor"
                result["active_model"] = d.get("cursor.model", "auto")
                result["has_key"] = bool(d.get("cursor.apiKey") or os.environ.get("OPENAI_API_KEY"))
                for m in d.get("cursor.models", ["claude-3-5-sonnet", "gpt-4o", "cursor-fast"]):
                    result["models"].append({
                        "id": m,
                        "full_id": m,
                        "name": m,
                        "provider": "cursor",
                        "is_active": (m == result["active_model"]),
                        "is_enabled": True
                    })
            except Exception:
                pass

    # 7. VS Code & Cline
    elif aid == "cline":
        cf = os.path.join(APPDATA, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json")
        result["config_file"] = cf
        result["active_provider"] = "OpenRouter / Anthropic / Ollama"
        result["active_model"] = "auto"
        result["base_url"] = "http://localhost:11434/v1"
        result["has_key"] = True
        result["models"].append({
            "id": "claude-3-5-sonnet",
            "full_id": "claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet (Default)",
            "provider": "cline",
            "is_active": True,
            "is_enabled": True
        })

    # Default fallback for others
    else:
        result["config_file"] = "Standard Config"
        result["active_model"] = "default"
        result["active_provider"] = agent_cfg.get("name", "AI Agent")
        result["base_url"] = "Native"

    return result

def set_agent_active_model(agent_cfg, model_id, provider_id=None):
    """Sets active default model for given agent in its native config file."""
    aid = agent_cfg.get("id")

    # 1. OpenCode
    if aid == "opencode":
        cf = agent_cfg.get("config_file") or os.path.join(USERPROFILE, ".config", "opencode", "opencode.json")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["model"] = model_id
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True

    # 2. Claude Code
    elif aid == "claude":
        cf = os.path.join(USERPROFILE, ".claude", "settings.json")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = json.load(f)
            env = data.setdefault("env", {})
            env["ANTHROPIC_MODEL"] = model_id
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True

    # 3. Google Antigravity
    elif aid == "antigravity":
        cf = os.path.join(USERPROFILE, ".gemini", "antigravity-cli", "settings.json")
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        backup_config_file(cf)
        data = {}
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data["model"] = model_id
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True

    # 4. OpenAI Codex
    elif aid == "codex":
        cf = os.path.join(USERPROFILE, ".codex", "config.toml")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            found = False
            for line in lines:
                if line.strip().startswith("model =") or line.strip().startswith("model="):
                    new_lines.append(f'model = "{model_id}"\n')
                    found = True
                else:
                    new_lines.append(line)
            if not found:
                new_lines.insert(0, f'model = "{model_id}"\n')
            with open(cf, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True

    # 5. Nous Hermes
    elif aid == "hermes":
        cf = os.path.join(LOCALAPPDATA, "hermes", "config.yaml")
        if not os.path.exists(cf):
            cf = os.path.join(USERPROFILE, ".hermes", "config.yaml")
        if os.path.exists(cf) and yaml is not None:
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            data.setdefault("model", {})["default"] = model_id
            if provider_id:
                data["model"]["provider"] = provider_id
            with open(cf, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)
            return True

    # 6. Cursor IDE
    elif aid == "cursor":
        cf = os.path.join(APPDATA, "Cursor", "User", "settings.json")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["cursor.model"] = model_id
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True

    return False

def toggle_agent_model(agent_cfg, model_id, provider_id=None, enable=None):
    """Toggles model on/off (e.g. in OpenCode blacklist, or tier overrides)."""
    aid = agent_cfg.get("id")
    if aid == "opencode":
        cf = agent_cfg.get("config_file") or os.path.join(USERPROFILE, ".config", "opencode", "opencode.json")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = json.load(f)
            prov = data.get("provider", {}).get(provider_id, {})
            bl = prov.setdefault("blacklist", [])
            if enable is None:
                enable = (model_id in bl)
            if enable and model_id in bl:
                bl.remove(model_id)
            elif not enable and model_id not in bl:
                bl.append(model_id)
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
    return False

def add_agent_provider(agent_cfg, prov_id, name, base_url, api_key=None, models_list=None):
    """Adds or updates a custom AI provider (Ollama, OpenRouter, DeepSeek, Custom) in agent config."""
    aid = agent_cfg.get("id")

    # 1. OpenCode
    if aid == "opencode":
        cf = agent_cfg.get("config_file") or os.path.join(USERPROFILE, ".config", "opencode", "opencode.json")
        backup_config_file(cf)
        data = {"provider": {}}
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        p = data.setdefault("provider", {}).setdefault(prov_id, {})
        p["name"] = name
        p["npm"] = "@ai-sdk/openai-compatible"
        opts = p.setdefault("options", {})
        opts["baseURL"] = base_url
        if api_key:
            opts["apiKey"] = api_key
        opts["setCacheKey"] = True

        m_dict = p.setdefault("models", {})
        if models_list:
            for m in models_list:
                if m not in m_dict:
                    m_dict[m] = {"name": m}
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True

    # 2. Claude Code
    elif aid == "claude":
        cf = os.path.join(USERPROFILE, ".claude", "settings.json")
        backup_config_file(cf)
        data = {"env": {}}
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        env = data.setdefault("env", {})
        env["ANTHROPIC_BASE_URL"] = base_url
        env["ANTHROPIC_API_BASE_URL"] = base_url
        env["CLAUDE_AGENT_API_BASE_URL"] = base_url
        if api_key:
            env["ANTHROPIC_AUTH_TOKEN"] = api_key
            env["ANTHROPIC_API_KEY"] = api_key
        if models_list and len(models_list) > 0:
            first_m = models_list[0]
            env["ANTHROPIC_MODEL"] = first_m
            env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = first_m
            env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = first_m
            env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = first_m
            env["ANTHROPIC_SMALL_FAST_MODEL"] = first_m
        with open(cf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True

    # 3. OpenAI Codex
    elif aid == "codex":
        cf = os.path.join(USERPROFILE, ".codex", "config.toml")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                txt = f.read()
            block_header = f"[model_providers.{prov_id}]"
            lines = txt.splitlines()
            new_lines = []
            in_block = False
            found = False
            for line in lines:
                if line.strip() == block_header:
                    in_block = True
                    found = True
                    new_lines.append(line)
                    new_lines.append(f'name = "{prov_id}"')
                    new_lines.append('wire_api = "responses"')
                    new_lines.append('requires_openai_auth = true')
                    new_lines.append(f'base_url = "{base_url}"')
                    continue
                if in_block:
                    if line.strip().startswith("["):
                        in_block = False
                        new_lines.append(line)
                    continue
                new_lines.append(line)
            if not found:
                new_lines.append("")
                new_lines.append(block_header)
                new_lines.append(f'name = "{prov_id}"')
                new_lines.append('wire_api = "responses"')
                new_lines.append('requires_openai_auth = true')
                new_lines.append(f'base_url = "{base_url}"')
            with open(cf, "w", encoding="utf-8") as f:
                f.write("\n".join(new_lines) + "\n")
            return True

    # 4. Nous Hermes
    elif aid == "hermes":
        cf = os.path.join(LOCALAPPDATA, "hermes", "config.yaml")
        if not os.path.exists(cf):
            cf = os.path.join(USERPROFILE, ".hermes", "config.yaml")
        if os.path.exists(cf) and yaml is not None:
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            p = data.setdefault("providers", {}).setdefault(prov_id, {})
            p["name"] = name
            p["base_url"] = base_url
            if models_list and len(models_list) > 0:
                p["model"] = models_list[0]
                m_map = p.setdefault("models", {})
                for m in models_list:
                    m_map[m] = {}
            with open(cf, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False)
            return True

    # 5. Cursor IDE
    elif aid == "cursor":
        cf = os.path.join(APPDATA, "Cursor", "User", "settings.json")
        if os.path.exists(cf):
            backup_config_file(cf)
            with open(cf, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["cursor.general.openAiBaseUrl"] = base_url
            if api_key:
                data["cursor.apiKey"] = api_key
            if models_list:
                existing_m = data.get("cursor.models", [])
                for m in models_list:
                    if m not in existing_m:
                        existing_m.append(m)
                data["cursor.models"] = existing_m
            with open(cf, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True

    return False

def universal_deploy_provider(all_agents, prov_key, custom_base=None, custom_key=None, custom_model=None):
    """
    1-Click deploy a provider setup across ALL compatible installed AI agents!
    (OpenCode, Claude, Codex, Hermes, Cursor, Cline).
    """
    preset = PROVIDER_PRESETS.get(prov_key, PROVIDER_PRESETS["custom"])
    prov_id = preset["id"]
    name = preset["name"]
    base_url = custom_base or preset["baseURL"]
    models_list = [custom_model] if custom_model else preset["default_models"]

    deployed = []
    failed = []

    for a in all_agents.values():
        try:
            ok = add_agent_provider(a, prov_id, name, base_url, api_key=custom_key, models_list=models_list)
            if ok:
                if custom_model:
                    set_agent_active_model(a, custom_model, provider_id=prov_id)
                deployed.append(a["name"])
            else:
                failed.append(a["name"])
        except Exception:
            failed.append(a["name"])

    return deployed, failed

# ================= INTERACTIVE MODEL SCREENS =================

def universal_models_hub(all_agents):
    """Global AI Models & Providers Overview and 1-Click Universal Deploy Hub"""
    init_screen()
    print(CLR_HIDE_CURSOR, end="", flush=True)

    cursor = 0
    agent_items = list(all_agents.values())

    try:
        while True:
            # Gather fresh statuses
            statuses = []
            for a in agent_items:
                st = get_agent_models_and_providers(a)
                statuses.append((a, st))

            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}         UNIVERSAL AI AGENT MODELS & PROVIDERS CONTROL HUB                      {CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_DIM}Real-time view of active models, providers, and endpoints across all installed agents{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}{'Agent':<24} {'Active Model':<30} {'Active Provider / URL':<24}{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")

            for i, (a, st) in enumerate(statuses):
                is_cur = (i == cursor)
                ind = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "
                act_m = st["active_model"]
                if len(act_m) > 28: act_m = act_m[:25] + "..."
                prov_label = st["active_provider"]
                if len(prov_label) > 22: prov_label = prov_label[:19] + "..."

                if is_cur:
                    lines.append(f"{ind}{CLR_BOLD}{CLR_REVERSE} [{i+1:>2}] {a['name']:<20} {CLR_RESET} {CLR_GREEN}{act_m:<28}{CLR_RESET} {CLR_YELLOW}{prov_label:<22}{CLR_RESET}")
                else:
                    lines.append(f"{ind}{CLR_WHITE} [{i+1:>2}] {a['name']:<20}{CLR_RESET} {CLR_CYAN}{act_m:<28}{CLR_RESET} {CLR_DIM}{prov_label:<22}{CLR_RESET}")

            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Global Operations:{CLR_RESET}")
            idx_u = len(agent_items)
            idx_t = len(agent_items) + 1
            idx_x = len(agent_items) + 2

            ind_u = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_u) else "  "
            ind_t = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_t) else "  "
            ind_x = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_x) else "  "

            lines.append(f"{ind_u}[U] Universal Deploy Provider (1-Click Push Ollama/OpenRouter/Custom to ALL Agents)")
            lines.append(f"{ind_t}[T] Test / Ping Endpoint Connectivity (Check if local LLM or API is online)")
            lines.append(f"{ind_x}[0] Return to Main Menu")
            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Navigation:{CLR_RESET} [↑/↓] Move Cursor  [Enter] Manage Agent Models  [U/T/0] Actions  [Esc/q] Back")
            lines.append("================================================================================")

            render_frame(lines)

            key = read_key()
            total_rows = len(agent_items) + 3

            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < total_rows - 1: cursor += 1
            elif key == 'ENTER':
                if cursor < len(agent_items):
                    manage_agent_models(agent_items[cursor], all_agents)
                    init_screen()
                elif cursor == idx_u:
                    run_universal_deploy_wizard(all_agents)
                    init_screen()
                elif cursor == idx_t:
                    run_endpoint_test_tool()
                    init_screen()
                elif cursor == idx_x:
                    break
            elif key.isdigit():
                val = int(key)
                if 1 <= val <= len(agent_items):
                    manage_agent_models(agent_items[val-1], all_agents)
                    init_screen()
                elif val == 0:
                    break
            elif key.upper() == 'U':
                run_universal_deploy_wizard(all_agents)
                init_screen()
            elif key.upper() == 'T':
                run_endpoint_test_tool()
                init_screen()
            elif key in ('ESC', 'q'):
                break
    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)

def run_universal_deploy_wizard(all_agents):
    """Wizard to deploy an AI provider across all installed agents simultaneously."""
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}       UNIVERSAL 1-CLICK PROVIDER DEPLOYMENT WIZARD                             {CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("Deploy a local LLM or cloud API endpoint to ALL detected agents in one shot.\n")

    preset_keys = list(PROVIDER_PRESETS.keys())
    for idx, pk in enumerate(preset_keys, 1):
        p = PROVIDER_PRESETS[pk]
        print(f"  {CLR_WHITE}[{idx}] {p['name']:<32}{CLR_RESET} {CLR_DIM}({p['baseURL']}){CLR_RESET}")
    print(f"  {CLR_DIM}[0] Cancel{CLR_RESET}\n")

    choice = input(f"{CLR_YELLOW}Select Provider Template [1-{len(preset_keys)}, 0]: {CLR_RESET}").strip()
    if not choice or choice == "0":
        return
    try:
        p_idx = int(choice) - 1
        selected_key = preset_keys[p_idx]
    except Exception:
        return

    preset = PROVIDER_PRESETS[selected_key]
    print(f"\n{CLR_GREEN}Selected: {preset['name']}{CLR_RESET}")
    base_url = input(f"Endpoint Base URL [{preset['baseURL']}]: ").strip() or preset["baseURL"]
    
    api_key = ""
    if preset["requires_key"] or selected_key == "custom":
        api_key = input("API Key / Token (leave blank for local/env): ").strip()

    def_model = preset["default_models"][0] if preset["default_models"] else "custom-model"
    model_name = input(f"Default Active Model [{def_model}]: ").strip() or def_model

    print(f"\n{CLR_YELLOW}Testing endpoint connectivity...{CLR_RESET}")
    is_live, msg = test_ping_endpoint(base_url)
    status_clr = CLR_GREEN if is_live else CLR_RED
    print(f"Endpoint Status: {status_clr}{msg}{CLR_RESET}\n")

    confirm = input(f"{CLR_BOLD}Push this configuration to ALL installed agents? [y/N]: {CLR_RESET}").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        input("Press [Enter] to return...")
        return

    print(f"\n{CLR_CYAN}Deploying across ecosystem...{CLR_RESET}")
    deployed, failed = universal_deploy_provider(all_agents, selected_key, custom_base=base_url, custom_key=api_key, custom_model=model_name)

    print(f"\n{CLR_GREEN}[SUCCESS] Successfully configured in ({len(deployed)}) agents:{CLR_RESET}")
    for d in deployed:
        print(f"  ✓ {d}")
    if failed:
        print(f"\n{CLR_YELLOW}[NOTE] Skipped or not applicable ({len(failed)}):{CLR_RESET}")
        for f in failed:
            print(f"  - {f}")

    print()
    input("Press [Enter] to continue...")

def run_endpoint_test_tool():
    """Interactive tool to test connectivity to any model server or API."""
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}       AI ENDPOINT & MODEL SERVER CONNECTIVITY TESTER                           {CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("Verify if local inference servers or cloud gateways are reachable.\n")

    quick_targets = [
        ("Ollama Local", "http://localhost:11434/v1"),
        ("LM Studio / LocalAI", "http://localhost:1234/v1"),
        ("Custom Port 31415", "http://127.0.0.1:31415"),
        ("OpenRouter Cloud", "https://openrouter.ai/api/v1"),
        ("DeepSeek API", "https://api.deepseek.com/v1"),
        ("Groq Cloud", "https://api.groq.com/openai/v1"),
        ("OpenAI API", "https://api.openai.com/v1"),
        ("Anthropic API", "https://api.anthropic.com")
    ]

    print("Quick Presets:")
    for i, (name, u) in enumerate(quick_targets, 1):
        print(f"  [{i}] {name:<22} ({u})")
    print("  [C] Custom URL")
    print("  [0] Back\n")

    ch = input(f"{CLR_YELLOW}Choose endpoint to test [1-8, C, 0]: {CLR_RESET}").strip()
    if not ch or ch == "0":
        return

    if ch.isdigit() and 1 <= int(ch) <= len(quick_targets):
        url = quick_targets[int(ch) - 1][1]
        name = quick_targets[int(ch) - 1][0]
    else:
        url = input("Enter full URL (e.g. http://localhost:8000/v1): ").strip()
        name = "Custom Endpoint"

    if not url:
        return

    print(f"\nTesting {CLR_WHITE}{name}{CLR_RESET} at {CLR_CYAN}{url}{CLR_RESET}...")
    is_live, msg = test_ping_endpoint(url)
    clr = CLR_GREEN if is_live else CLR_RED
    print(f"\nResult: {clr}{msg}{CLR_RESET}\n")
    input("Press [Enter] to continue...")

def manage_agent_models(agent_cfg, all_agents):
    """
    Dedicated interactive model dashboard for a specific agent:
    - View active model, provider, base URL, API key status
    - Switch active model with [Enter]
    - Toggle model enabled/disabled with [Space]
    - Add custom provider/model with [a]
    - Edit provider base URL / key with [e]
    - Delete model/provider with [d]
    - Test connection with [t]
    - Sync provider to other agents with [s]
    """
    cursor = 0
    init_screen()
    print(CLR_HIDE_CURSOR, end="", flush=True)

    try:
        while True:
            info = get_agent_models_and_providers(agent_cfg)
            models = info["models"]
            act_m = info["active_model"]
            prov = info["active_provider"]
            base = info["base_url"]
            has_k = "Configured" if info["has_key"] else "None / Optional"

            total_models = len(models)
            cursor = 0 if total_models == 0 else max(0, min(cursor, total_models - 1))

            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}  AI MODEL & PROVIDER MANAGER: {agent_cfg['name'].upper()}{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_WHITE}  Config File:    {CLR_RESET}{CLR_DIM}{info['config_file'] or 'Native'}{CLR_RESET}")
            lines.append(f"{CLR_WHITE}  Active Model:   {CLR_RESET}{CLR_GREEN}{CLR_BOLD}{act_m}{CLR_RESET}")
            lines.append(f"{CLR_WHITE}  Active Provider:{CLR_RESET} {CLR_CYAN}{prov}{CLR_RESET}  |  {CLR_WHITE}Base URL:{CLR_RESET} {CLR_YELLOW}{base}{CLR_RESET}  |  {CLR_WHITE}Key:{CLR_RESET} {has_k}")
            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}{'Status':<14} {'Model ID':<36} {'Provider':<24}{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")

            if total_models == 0:
                lines.append(f"  {CLR_DIM}No explicit models listed. Press [a] to add a custom provider or model.{CLR_RESET}")
            else:
                window_size = 12
                if cursor < window_size // 2: start_idx = 0
                elif cursor > total_models - (window_size // 2): start_idx = max(0, total_models - window_size)
                else: start_idx = max(0, cursor - window_size // 2)
                end_idx = min(total_models, start_idx + window_size)

                for i in range(start_idx, end_idx):
                    m = models[i]
                    is_cur = (i == cursor)
                    ind = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "

                    if m.get("is_active"):
                        badge = f"{CLR_GREEN}● ACTIVE{CLR_RESET}"
                    elif m.get("is_enabled", True):
                        badge = f"{CLR_CYAN}[✓] ON  {CLR_RESET}"
                    else:
                        badge = f"{CLR_RED}[ ] OFF {CLR_RESET}"

                    m_id_disp = m["id"]
                    if len(m_id_disp) > 34: m_id_disp = m_id_disp[:31] + "..."
                    m_prov = m.get("provider", "local")

                    if is_cur:
                        lines.append(f"{ind}{badge} {CLR_BOLD}{CLR_REVERSE} {m_id_disp:<34} {CLR_RESET} {CLR_YELLOW}{m_prov:<20}{CLR_RESET}")
                    else:
                        lines.append(f"{ind}{badge} {CLR_WHITE}{m_id_disp:<34}{CLR_RESET} {CLR_DIM}{m_prov:<20}{CLR_RESET}")

            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Actions:{CLR_RESET} [Enter] Set Active  [Space] Toggle ON/OFF  [a] Add Provider/Model")
            lines.append(f"         [e] Edit Provider    [d] Delete Model       [t] Test Ping  [s] Sync to Agents  [Esc/q] Back")
            lines.append("================================================================================")

            render_frame(lines)

            key = read_key()
            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < total_models - 1: cursor += 1
            elif key == 'ENTER' and total_models > 0:
                selected_model = models[cursor]
                set_agent_active_model(agent_cfg, selected_model.get("full_id") or selected_model["id"], provider_id=selected_model.get("provider"))
            elif key == 'SPACE' and total_models > 0:
                selected_model = models[cursor]
                toggle_agent_model(agent_cfg, selected_model["id"], provider_id=selected_model.get("provider"))
            elif key.lower() == 'a':
                add_provider_interactive(agent_cfg)
                init_screen()
            elif key.lower() == 'e':
                edit_provider_interactive(agent_cfg, info)
                init_screen()
            elif key in ('d', 'DEL') and total_models > 0:
                selected_model = models[cursor]
                delete_model_interactive(agent_cfg, selected_model)
                init_screen()
            elif key.lower() == 't':
                init_screen()
                print(f"{CLR_BOLD}Testing connection to: {CLR_CYAN}{base}{CLR_RESET}...")
                ok, msg = test_ping_endpoint(base)
                clr = CLR_GREEN if ok else CLR_RED
                print(f"\nStatus: {clr}{msg}{CLR_RESET}\n")
                input("Press [Enter] to continue...")
                init_screen()
            elif key.lower() == 's':
                sync_provider_to_other_agents(agent_cfg, info, all_agents)
                init_screen()
            elif key in ('ESC', 'q'):
                break
    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)

def add_provider_interactive(agent_cfg):
    """Interactive wizard to add a new AI provider or models to the selected agent."""
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}  ADD AI PROVIDER / MODEL TO {agent_cfg['name'].upper()}{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("Choose from ready-to-use provider presets or configure a custom endpoint:\n")

    preset_keys = list(PROVIDER_PRESETS.keys())
    for idx, pk in enumerate(preset_keys, 1):
        p = PROVIDER_PRESETS[pk]
        print(f"  [{idx}] {p['name']:<32} {CLR_DIM}({p['baseURL']}){CLR_RESET}")
    print("  [0] Cancel\n")

    ch = input(f"{CLR_YELLOW}Select Provider Template [1-{len(preset_keys)}, 0]: {CLR_RESET}").strip()
    if not ch or ch == "0":
        return
    try:
        p_idx = int(ch) - 1
        pk = preset_keys[p_idx]
    except Exception:
        return

    p = PROVIDER_PRESETS[pk]
    prov_id = p["id"]
    prov_name = p["name"]
    base_url = input(f"Endpoint Base URL [{p['baseURL']}]: ").strip() or p["baseURL"]
    
    api_key = ""
    if p["requires_key"] or pk == "custom":
        api_key = input("API Key / Token (optional for local): ").strip()

    models_input = input(f"Models to add (comma-separated, default: {','.join(p['default_models'][:3])}): ").strip()
    if models_input:
        models_list = [m.strip() for m in models_input.split(",") if m.strip()]
    else:
        models_list = p["default_models"]

    print(f"\n{CLR_YELLOW}Verifying endpoint...{CLR_RESET}")
    is_live, msg = test_ping_endpoint(base_url)
    clr = CLR_GREEN if is_live else CLR_RED
    print(f"Endpoint status: {clr}{msg}{CLR_RESET}\n")

    ok = add_agent_provider(agent_cfg, prov_id, prov_name, base_url, api_key=api_key, models_list=models_list)
    if ok:
        set_active = input(f"Set {models_list[0]} as active model now? [Y/n]: ").strip().lower()
        if set_active != 'n':
            set_agent_active_model(agent_cfg, models_list[0], provider_id=prov_id)
        print(f"\n{CLR_GREEN}[SUCCESS] Provider '{prov_name}' added to {agent_cfg['name']}!{CLR_RESET}")
    else:
        print(f"\n{CLR_RED}[ERROR] Failed to write configuration for {agent_cfg['name']}. Check file permissions.{CLR_RESET}")
    print()
    input("Press [Enter] to continue...")

def edit_provider_interactive(agent_cfg, info):
    """Allows editing current active provider base URL or API key."""
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}  EDIT AI PROVIDER OPTIONS: {agent_cfg['name'].upper()}{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}\n")
    print(f"Current Base URL: {CLR_YELLOW}{info['base_url']}{CLR_RESET}")
    new_url = input("New Base URL (leave blank to keep current): ").strip()

    new_key = input("New API Key / Token (leave blank to keep current): ").strip()

    target_url = new_url if new_url else info["base_url"]
    prov_id = info.get("active_provider") or "custom"
    
    ok = add_agent_provider(agent_cfg, prov_id, prov_id, target_url, api_key=new_key if new_key else None)
    if ok:
        print(f"\n{CLR_GREEN}[SUCCESS] Provider settings updated!{CLR_RESET}")
    else:
        print(f"\n{CLR_RED}[ERROR] Could not update settings.{CLR_RESET}")
    input("Press [Enter] to continue...")

def delete_model_interactive(agent_cfg, model_item):
    """Removes a model or provider entry."""
    init_screen()
    m_id = model_item["id"]
    p_id = model_item.get("provider")
    confirm = input(f"{CLR_RED}Remove model '{m_id}' from {agent_cfg['name']}? [y/N]: {CLR_RESET}").strip().lower()
    if confirm == 'y':
        # OpenCode model deletion
        aid = agent_cfg.get("id")
        if aid == "opencode":
            cf = agent_cfg.get("config_file") or os.path.join(USERPROFILE, ".config", "opencode", "opencode.json")
            if os.path.exists(cf):
                backup_config_file(cf)
                with open(cf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                p = data.get("provider", {}).get(p_id, {})
                if "models" in p and m_id in p["models"]:
                    del p["models"][m_id]
                with open(cf, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print(f"{CLR_GREEN}Model removed.{CLR_RESET}")
        else:
            print(f"{CLR_YELLOW}Deletion not required for native enum model.{CLR_RESET}")
    input("Press [Enter] to continue...")

def sync_provider_to_other_agents(agent_cfg, info, all_agents):
    """Pushes current agent's active provider config to other installed agents."""
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}  SYNC PROVIDER ACROSS AGENTS                                                   {CLR_RESET}")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"Syncing Provider: {CLR_YELLOW}{info['active_provider']}{CLR_RESET}")
    print(f"Base URL:         {CLR_YELLOW}{info['base_url']}{CLR_RESET}")
    print(f"Active Model:     {CLR_GREEN}{info['active_model']}{CLR_RESET}\n")

    confirm = input("Deploy this configuration to all other compatible agents? [y/N]: ").strip().lower()
    if confirm == 'y':
        deployed, failed = universal_deploy_provider(all_agents, "custom", custom_base=info["base_url"], custom_model=info["active_model"])
        print(f"\n{CLR_GREEN}[SUCCESS] Deployed to ({len(deployed)}) agents!{CLR_RESET}")
    input("Press [Enter] to continue...")

# ================= INTERACTIVE CHECKLIST ENGINE =================

def run_checklist(title, all_items, selected_set, details=None, agent_name="", allow_delete=True):
    items = sorted(list(all_items))
    selected = set(selected_set)
    cursor = 0
    filter_text = ""
    status_msg = ""

    init_screen()
    print(CLR_HIDE_CURSOR, end="", flush=True)
    try:
        while True:
            if filter_text:
                filtered = [it for it in items if filter_text.lower() in it.lower()]
            else:
                filtered = items

            total_filtered = len(filtered)
            cursor = 0 if total_filtered == 0 else max(0, min(cursor, total_filtered - 1))

            window_size = 15
            if cursor < window_size // 2: start_idx = 0
            elif cursor > total_filtered - (window_size // 2): start_idx = max(0, total_filtered - window_size)
            else: start_idx = max(0, cursor - window_size // 2)
            end_idx = min(total_filtered, start_idx + window_size)

            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}  {title.upper()}{CLR_RESET}")
            if agent_name:
                lines.append(f"{CLR_DIM}  Target Agent: {agent_name}{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_WHITE}Selected: {len(selected)} / {len(items)} active  |  Showing: {total_filtered} items  |  Pos: {cursor + 1}/{max(1, total_filtered)}{CLR_RESET}")
            if filter_text:
                lines.append(f"{CLR_YELLOW}Filter: '{filter_text}' (Press 'c' to clear filter){CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")

            if total_filtered == 0:
                lines.append(f"  {CLR_DIM}(No items match '{filter_text}'){CLR_RESET}")
            else:
                for idx in range(start_idx, end_idx):
                    it = filtered[idx]
                    is_sel = it in selected
                    is_cur = (idx == cursor)

                    box = f"{CLR_GREEN}[x]{CLR_RESET}" if is_sel else f"{CLR_DIM}[ ]{CLR_RESET}"
                    indicator = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "

                    det = ""
                    if details and it in details:
                        det = f" {CLR_DIM}({details[it]}){CLR_RESET}"

                    if is_cur:
                        lines.append(f"{indicator}{box} {CLR_BOLD}{CLR_REVERSE} {it:<36} {CLR_RESET}{det}")
                    else:
                        color = CLR_WHITE if is_sel else CLR_DIM
                        lines.append(f"{indicator}{box} {color}{it:<36}{CLR_RESET}{det}")

            lines.append("--------------------------------------------------------------------------------")
            if status_msg:
                lines.append(f"{CLR_YELLOW}{status_msg}{CLR_RESET}")
                status_msg = ""
            del_hint = "  [Del] Remove" if allow_delete else ""
            lines.append(f"{CLR_BOLD}Controls:{CLR_RESET} [↑/↓] Navigate  [Space] Toggle  [Enter] Save & Apply{del_hint}")
            lines.append(f"          [/] Search  [a] All  [d] None  [i] Invert  [Esc/q] Cancel")
            lines.append("--------------------------------------------------------------------------------")

            render_frame(lines)

            key = read_key()
            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < total_filtered - 1: cursor += 1
            elif key == 'PGUP': cursor = max(0, cursor - 10)
            elif key == 'PGDN': cursor = min(total_filtered - 1, cursor + 10)
            elif key == 'HOME': cursor = 0
            elif key == 'END': cursor = max(0, total_filtered - 1)
            elif key == 'SPACE':
                if 0 <= cursor < total_filtered:
                    cur_it = filtered[cursor]
                    if cur_it in selected: selected.remove(cur_it)
                    else: selected.add(cur_it)
            elif key == 'ENTER':
                return selected
            elif key in ('ESC', 'q'):
                if selected != set(selected_set):
                    init_screen()
                    ans = input("\nYou have unsaved changes! Save now? [y/n/c]: ").strip().lower()
                    if ans == 'y': return selected
                    elif ans == 'n': return None
                    else:
                        init_screen()
                        continue
                return None
            elif key == '/':
                init_screen()
                f_in = input(f"\n{CLR_CYAN}Search & Filter:{CLR_RESET} ").strip()
                filter_text = f_in
                cursor = 0
                init_screen()
            elif key == 'c' and filter_text:
                filter_text = ""
                cursor = 0
            elif key == 'a':
                for it in filtered: selected.add(it)
                status_msg = f"Selected all {len(filtered)} visible items."
            elif key == 'd':
                for it in filtered: selected.discard(it)
                status_msg = f"Deselected all {len(filtered)} visible items."
            elif key == 'i':
                for it in filtered:
                    if it in selected: selected.remove(it)
                    else: selected.add(it)
                status_msg = f"Inverted selection for {len(filtered)} items."
            elif key == 'DEL' and allow_delete and 0 <= cursor < total_filtered:
                it_del = filtered[cursor]
                init_screen()
                print(f"\n{CLR_RED}Remove Item: {it_del}?{CLR_RESET}")
                print("  [1] Stash / Disable (move to available - safe)")
                print("  [2] Permanently Delete from disk")
                print("  [0] Cancel")
                c_del = input("Choice: ").strip()
                if c_del == "1":
                    selected.discard(it_del)
                    status_msg = f"Stashed '{it_del}'."
                elif c_del == "2":
                    items.remove(it_del)
                    selected.discard(it_del)
                    status_msg = f"Removed '{it_del}'."
                init_screen()

    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)

# ================= ADVANCED SKILLS & MCP ADDERS =================

def add_skills_interactive(agent_cfg=None, all_agents=None):
    """
    Rich interactive menu to add skills via:
    1. Master Warehouses (D: drive repos)
    2. Local Directory Path
    3. Git / GitHub clone
    4. NPX / CLI command
    5. Scaffold New Skill Template
    """
    init_screen()
    target_name = agent_cfg["name"] if agent_cfg else "ALL INSTALLED AGENTS"
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"                      ADD NEW SKILLS TO: {target_name.upper()}                  ")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("Select Method to Add Skills:")
    print("  [1] Browse & Import from Master Warehouses (1,350+ Skills on D: drive)")
    print("  [2] Import Skill from Local Folder / Directory Path")
    print("  [3] Install Skill from Git / GitHub Repository URL")
    print("  [4] Install Skill via CLI Command (e.g. npx skills add)")
    print("  [5] Scaffold New Custom Skill Template (Interactive Generator)")
    print("  [0] Cancel / Back")
    print("--------------------------------------------------------------------------------")
    choice = input("Enter option [1-5/0]: ").strip()

    dest_dirs = []
    if agent_cfg and agent_cfg.get("skills_dir"):
        dest_dirs.append(agent_cfg["skills_dir"])
    elif all_agents:
        for a in all_agents.values():
            if a.get("skills_dir"):
                dest_dirs.append(a["skills_dir"])

    if choice == "1":
        browse_warehouse_import(target_agent_cfg=agent_cfg)
    elif choice == "2":
        path_in = input("\nEnter full path to skill directory: ").strip().strip('"')
        if os.path.exists(path_in):
            sname = os.path.basename(path_in)
            for d in dest_dirs:
                os.makedirs(d, exist_ok=True)
                dst = os.path.join(d, sname)
                if os.path.exists(dst): shutil.rmtree(dst)
                shutil.copytree(path_in, dst)
            print(f"\n{CLR_GREEN}[SUCCESS] Installed skill '{sname}' to {len(dest_dirs)} agent(s)!{CLR_RESET}")
        else:
            print(f"\n{CLR_RED}Path does not exist:{CLR_RESET} {path_in}")
        input("Press [Enter] to continue...")
    elif choice == "3":
        git_url = input("\nEnter Git / GitHub URL (e.g. https://github.com/user/repo): ").strip()
        if git_url:
            sname = input("Enter skill folder name: ").strip() or git_url.split("/")[-1].replace(".git", "")
            for d in dest_dirs:
                os.makedirs(d, exist_ok=True)
                dst = os.path.join(d, sname)
                if os.path.exists(dst): shutil.rmtree(dst)
                print(f"Cloning into {dst}...")
                subprocess.run(["git", "clone", "--depth", "1", git_url, dst])
            print(f"\n{CLR_GREEN}[SUCCESS] Cloned skill '{sname}'!{CLR_RESET}")
        input("Press [Enter] to continue...")
    elif choice == "4":
        cmd_run = input("\nEnter installation command: ").strip()
        if cmd_run:
            subprocess.run(cmd_run, shell=True)
        input("Press [Enter] to continue...")
    elif choice == "5":
        sname = input("\nEnter new skill name (e.g. 'my-api-tool'): ").strip().lower().replace(" ", "-")
        desc = input("Enter short description (When to use): ").strip()
        if sname:
            template = f"""---
name: {sname}
description: {desc or 'Custom agent procedure and workflow.'}
---

# {sname.replace('-', ' ').title()}

## Overview
Describe what this skill accomplishes.

## Instructions
1. Step 1
2. Step 2
"""
            for d in dest_dirs:
                s_folder = os.path.join(d, sname)
                os.makedirs(s_folder, exist_ok=True)
                with open(os.path.join(s_folder, "SKILL.md"), "w", encoding="utf-8") as f:
                    f.write(template)
            print(f"\n{CLR_GREEN}[SUCCESS] Created custom skill '{sname}'!{CLR_RESET}")
            input("Press [Enter] to continue...")

def add_mcp_interactive(agent_cfg=None, all_agents=None):
    """
    Rich interactive menu to add MCP servers via:
    1. Raw JSON code block / snippet
    2. Interactive step-by-step Wizard
    3. Clone MCP server from another installed agent
    4. Broadcast / Add to ALL agents
    """
    init_screen()
    target_name = agent_cfg["name"] if agent_cfg else "ALL INSTALLED AGENTS"
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print(f"                      ADD MCP SERVER TO: {target_name.upper()}                  ")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("Select Method:")
    print("  [1] Paste Raw JSON MCP Configuration Snippet")
    print("  [2] Interactive Step-by-Step MCP Wizard (Stdio / SSE)")
    print("  [3] Clone MCP Server from another Agent (Antigravity, Claude, Cursor, Hermes)")
    print("  [0] Cancel / Back")
    print("--------------------------------------------------------------------------------")
    choice = input("Enter option [1-3/0]: ").strip()

    target_configs = []
    if agent_cfg and agent_cfg.get("mcp_file"):
        target_configs.append(agent_cfg)
    elif all_agents:
        for a in all_agents.values():
            if a.get("mcp_file"): target_configs.append(a)

    if choice == "1":
        init_screen()
        print(f"\n{CLR_CYAN}Paste your JSON MCP snippet below (End with an empty line or 'DONE'):{CLR_RESET}")
        print(CLR_DIM + 'Example: {"my-server": {"command": "npx", "args": ["-y", "my-package"]}}' + CLR_RESET)
        json_lines = []
        while True:
            try:
                line = input()
                if line.strip() == "DONE" or (not line and json_lines and json_lines[-1] == ""):
                    break
                json_lines.append(line)
            except EOFError:
                break
        raw_text = "\n".join(json_lines).strip()
        try:
            parsed = json.loads(raw_text)
            if "mcpServers" in parsed: parsed = parsed["mcpServers"]
            # Add to target configs
            for ag in target_configs:
                mf = ag.get("mcp_file")
                if mf and os.path.exists(mf) and ag.get("mcp_format") in ("standard_json", "cline_json"):
                    with open(mf, "r", encoding="utf-8") as f: data = json.load(f)
                    if "mcpServers" not in data: data["mcpServers"] = {}
                    data["mcpServers"].update(parsed)
                    with open(mf, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
            print(f"\n{CLR_GREEN}[SUCCESS] Injected MCP servers into {len(target_configs)} agent(s)!{CLR_RESET}")
        except Exception as e:
            print(f"\n{CLR_RED}JSON Parse Error:{CLR_RESET} {e}")
        input("Press [Enter] to continue...")

    elif choice == "2":
        init_screen()
        name = input("\nEnter MCP Server Name (e.g. 'sqlite-mcp'): ").strip()
        if not name: return
        print("\nTransport Mechanism:")
        print("  [1] Stdio (Local binary / npx / uvx / python)")
        print("  [2] SSE / Remote HTTP (URL)")
        ttype = input("Select [1/2]: ").strip()
        new_entry = {}
        if ttype == "2":
            url = input("Enter Server SSE URL: ").strip()
            if not url: return
            new_entry = {"serverUrl": url}
        else:
            cmd = input("Enter Command (e.g. 'npx', 'python', 'uvx'): ").strip()
            if not cmd: return
            args_str = input("Enter Arguments (space separated, or empty): ").strip()
            args = args_str.split() if args_str else []
            new_entry = {"command": cmd, "args": args}

        for ag in target_configs:
            mf = ag.get("mcp_file")
            if mf and os.path.exists(mf) and ag.get("mcp_format") in ("standard_json", "cline_json"):
                with open(mf, "r", encoding="utf-8") as f: data = json.load(f)
                if "mcpServers" not in data: data["mcpServers"] = {}
                data["mcpServers"][name] = new_entry
                with open(mf, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
        print(f"\n{CLR_GREEN}[SUCCESS] Registered MCP '{name}' in {len(target_configs)} agent(s)!{CLR_RESET}")
        input("Press [Enter] to continue...")

    elif choice == "3" and all_agents:
        init_screen()
        print(f"{CLR_CYAN}Select Source Agent to Clone MCP From:{CLR_RESET}")
        src_agents = [a for a in all_agents.values() if a.get("mcp_file") and os.path.exists(a["mcp_file"])]
        for idx, sa in enumerate(src_agents, 1):
            print(f"  [{idx}] {sa['name']}")
        c_src = input("Choice: ").strip()
        if c_src.isdigit() and 1 <= int(c_src) <= len(src_agents):
            src_ag = src_agents[int(c_src)-1]
            act_m, dis_m = read_mcp_config(src_ag)
            all_m = list(act_m.keys()) + list(dis_m.keys())
            if not all_m:
                print("No MCP servers found in source agent.")
                input("Press [Enter] to continue...")
                return
            chosen_mcp = run_checklist(f"Select MCPs to Clone from: {src_ag['name']}", all_m, set(), agent_name=target_name, allow_delete=False)
            if chosen_mcp:
                # Merge into target
                for mname in chosen_mcp:
                    mcfg = act_m.get(mname) or dis_m.get(mname)
                    if mcfg and not mcfg.get("raw"):
                        for ag in target_configs:
                            mf = ag.get("mcp_file")
                            if mf and os.path.exists(mf) and ag.get("mcp_format") in ("standard_json", "cline_json"):
                                with open(mf, "r", encoding="utf-8") as f: data = json.load(f)
                                if "mcpServers" not in data: data["mcpServers"] = {}
                                data["mcpServers"][mname] = mcfg
                                with open(mf, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)
                print(f"\n{CLR_GREEN}[SUCCESS] Cloned {len(chosen_mcp)} MCP server(s)!{CLR_RESET}")
                input("Press [Enter] to continue...")

# ================= WAREHOUSE BROWSER & IMPORTER =================

def browse_warehouse_import(target_agent_cfg=None):
    init_screen()
    cursor = 0
    print(CLR_HIDE_CURSOR, end="", flush=True)

    try:
        while True:
            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}                   MASTER SKILLS & AGENTS WAREHOUSE BROWSER                     {CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_DIM}Import upstream skills into your agents with a single keystroke{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")

            for i, (w_name, w_path) in enumerate(WAREHOUSES):
                is_cur = (i == cursor)
                indicator = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "
                exists = os.path.exists(w_path)
                status_tag = f"{CLR_GREEN}[AVAILABLE]{CLR_RESET}" if exists else f"{CLR_RED}[MISSING]{CLR_RESET}"
                if is_cur:
                    lines.append(f"{indicator}{CLR_BOLD}{CLR_REVERSE} [{i+1}] {w_name:<36} {CLR_RESET} {status_tag}")
                else:
                    lines.append(f"{indicator}{CLR_WHITE} [{i+1}] {w_name:<36}{CLR_RESET} {status_tag}")

            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Actions:{CLR_RESET} [↑/↓] Navigate  [Enter] Browse Skills  [Esc/q] Back")
            lines.append("================================================================================")

            render_frame(lines)

            key = read_key()
            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < len(WAREHOUSES) - 1: cursor += 1
            elif key == 'ENTER':
                w_name, w_path = WAREHOUSES[cursor]
                if not os.path.exists(w_path):
                    init_screen()
                    print(f"\n{CLR_RED}Warehouse directory not found:{CLR_RESET} {w_path}")
                    input("Press [Enter] to continue...")
                    init_screen()
                    continue

                skills_found = {}
                for root, dirs, files in os.walk(w_path):
                    if "SKILL.md" in files:
                        sname = os.path.basename(root)
                        skills_found[sname] = root

                if not skills_found:
                    for root, dirs, files in os.walk(w_path):
                        for f in files:
                            if f.endswith(".md") and not f.startswith("README"):
                                sname = f[:-3]
                                skills_found[sname] = os.path.join(root, f)

                if not skills_found:
                    init_screen()
                    print(f"\n{CLR_YELLOW}No skills found in {w_name}.{CLR_RESET}")
                    input("Press [Enter] to continue...")
                    init_screen()
                    continue

                chosen_skills = run_checklist(f"Import from: {w_name}", list(skills_found.keys()), set(), agent_name=target_agent_cfg['name'] if target_agent_cfg else "ALL AGENTS", allow_delete=False)
                if chosen_skills:
                    init_screen()
                    target_dirs = []
                    if target_agent_cfg and target_agent_cfg.get("skills_dir"):
                        target_dirs.append(target_agent_cfg["skills_dir"])
                    else:
                        all_ag = discover_installed_agents()
                        for ag in all_ag.values():
                            if ag.get("skills_dir"): target_dirs.append(ag["skills_dir"])

                    for sname in chosen_skills:
                        src = skills_found[sname]
                        for t_dir in target_dirs:
                            os.makedirs(t_dir, exist_ok=True)
                            dst = os.path.join(t_dir, sname)
                            try:
                                if os.path.isdir(src):
                                    if os.path.exists(dst): shutil.rmtree(dst)
                                    shutil.copytree(src, dst)
                                else:
                                    os.makedirs(dst, exist_ok=True)
                                    shutil.copy2(src, os.path.join(dst, "SKILL.md"))
                            except Exception:
                                pass

                    print(f"\n{CLR_GREEN}[SUCCESS] Imported {len(chosen_skills)} skills to {len(target_dirs)} destination(s)!{CLR_RESET}")
                    input("Press [Enter] to continue...")
                    init_screen()
            elif key in ('ESC', 'q'):
                break
    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)

# ================= GLOBAL SKILLS HUB =================

def global_skills_hub(all_agents):
    """
    Manages global skills across ALL installed agents:
    - View shared deployment matrix
    - Broadcast install any skill to all agents
    - 1-Click universal toggle
    """
    init_screen()
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    print("                      GLOBAL SKILLS HUB (ALL AGENTS)                            ")
    print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
    
    # Collect all skills across all agents
    skills_map = {}
    for a_id, a in all_agents.items():
        s_dir = a.get("skills_dir")
        if s_dir and os.path.exists(s_dir):
            for s in os.listdir(s_dir):
                if os.path.isdir(os.path.join(s_dir, s)):
                    if s not in skills_map: skills_map[s] = []
                    skills_map[s].append(a["name"])

    print(f"Total Unique Skills Deployed: {len(skills_map)}")
    print(f"Target Agents: {len(all_agents)} installed on this system")
    print("--------------------------------------------------------------------------------")
    print("Options:")
    print("  [1] View Shared Skills Deployment Matrix")
    print("  [2] Deploy / Sync Skill to ALL Agents")
    print("  [3] Universal Skill Toggle (Enable/Disable across all agents)")
    print("  [4] Add New Skill to ALL Agents (Warehouse / Git / Path / Scaffold)")
    print("  [0] Back to Main Menu")
    print("--------------------------------------------------------------------------------")
    choice = input("Select [1-4/0]: ").strip()

    if choice == "1":
        init_screen()
        print(f"\n{'Skill Name':<35} {'Installed In Agents'}")
        print("-" * 78)
        for s, ag_list in sorted(skills_map.items()):
            print(f"{s:<35} {', '.join(ag_list[:3])}{'...' if len(ag_list)>3 else ''}")
        input("\nPress [Enter] to return...")
    elif choice == "2":
        all_skill_names = sorted(list(skills_map.keys()))
        sel = run_checklist("Deploy / Sync to ALL Agents", all_skill_names, set(), allow_delete=False)
        if sel:
            for sname in sel:
                # Find source folder
                src = None
                for a in all_agents.values():
                    sd = a.get("skills_dir")
                    if sd and os.path.exists(os.path.join(sd, sname)):
                        src = os.path.join(sd, sname)
                        break
                if src:
                    for a in all_agents.values():
                        td = a.get("skills_dir")
                        if td:
                            os.makedirs(td, exist_ok=True)
                            dst = os.path.join(td, sname)
                            if not os.path.exists(dst):
                                shutil.copytree(src, dst)
            print(f"\n{CLR_GREEN}[SUCCESS] Deployed {len(sel)} skills across all agents!{CLR_RESET}")
            input("Press [Enter] to continue...")
    elif choice == "3":
        all_skill_names = sorted(list(skills_map.keys()))
        sel = run_checklist("Universal Toggle (Checked = ACTIVE in all agents)", all_skill_names, set(all_skill_names), allow_delete=False)
        if sel is not None:
            for sname in all_skill_names:
                make_active = (sname in sel)
                for a in all_agents.values():
                    sd = a.get("skills_dir")
                    sav = a.get("skills_available")
                    if sd and sav:
                        act_p = os.path.join(sd, sname)
                        stash_p = os.path.join(sav, sname)
                        if make_active and os.path.exists(stash_p):
                            shutil.move(stash_p, act_p)
                        elif not make_active and os.path.exists(act_p):
                            shutil.move(act_p, stash_p)
            print(f"\n{CLR_GREEN}[SUCCESS] Universal skills toggled!{CLR_RESET}")
            input("Press [Enter] to continue...")
    elif choice == "4":
        add_skills_interactive(agent_cfg=None, all_agents=all_agents)

# ================= INDIVIDUAL AGENT HUB =================

def manage_single_agent(agent_cfg, all_agents):
    cursor = 0
    menu = [
        ("Manage Skills", "Interactive checklist: Arrow keys + Space + Enter"),
        ("Manage MCP Servers", "Interactive checklist of tool providers & servers"),
        ("Manage AI Models & Providers", "Switch active model, add custom API/endpoints, toggle models"),
        ("Add New Skills", "Add via Warehouses, Local Path, GitHub URL, or Scaffold"),
        ("Add New MCP Server", "Add via Raw JSON, Interactive Wizard, or Clone from Agent"),
        ("Manage Plugins", "Interactive checklist of installed plugins"),
        ("Reveal in Windows Explorer", "Open agent directory in File Explorer"),
        ("Back to Master Hub", "Return to main agent selector")
    ]

    init_screen()
    print(CLR_HIDE_CURSOR, end="", flush=True)

    try:
        while True:
            act_s, av_s = get_agent_skills(agent_cfg)
            act_m, dis_m = read_mcp_config(agent_cfg)
            plugs = get_agent_plugins(agent_cfg)
            m_info = get_agent_models_and_providers(agent_cfg)

            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}  MANAGE AGENT: {agent_cfg['name'].upper()}{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_DIM}  Status: {agent_cfg.get('cli', 'Installed')}{CLR_RESET}")
            lines.append(f"{CLR_WHITE}  Active Model: {CLR_GREEN}{m_info['active_model']}{CLR_RESET}  |  {CLR_WHITE}Provider:{CLR_RESET} {CLR_CYAN}{m_info['active_provider']}{CLR_RESET}")
            lines.append(f"{CLR_WHITE}  Skills: {len(act_s)} active ({len(av_s)} stashed)  |  MCPs: {len(act_m)} active ({len(dis_m)} disabled)  |  Plugins: {len(plugs)}{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")

            for i, (title, desc) in enumerate(menu):
                is_cur = (i == cursor)
                num = (i + 1) if i < len(menu) - 1 else 0
                indicator = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "
                if is_cur:
                    lines.append(f"{indicator}{CLR_BOLD}{CLR_REVERSE} [{num}] {title:<28} {CLR_RESET}  {CLR_YELLOW}{desc}{CLR_RESET}")
                else:
                    lines.append(f"{indicator}{CLR_WHITE} [{num}] {title:<28}{CLR_RESET}  {CLR_DIM}{desc}{CLR_RESET}")

            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Navigation:{CLR_RESET} [↑/↓] Move Cursor  [Enter] Select Option  [1-7/0/M] Jump  [Esc/q] Back")
            lines.append("================================================================================")

            render_frame(lines)

            key = read_key()
            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < len(menu) - 1: cursor += 1
            elif key == 'ENTER':
                if cursor == 0:
                    s_dir = agent_cfg.get("skills_dir")
                    av_dir = agent_cfg.get("skills_available")
                    if not s_dir:
                        init_screen()
                        print(f"\n{CLR_YELLOW}No local skills folder for {agent_cfg['name']}.{CLR_RESET}")
                        input("Press [Enter] to continue...")
                        init_screen()
                        continue
                    os.makedirs(s_dir, exist_ok=True)
                    os.makedirs(av_dir, exist_ok=True)
                    all_s = sorted(list(set(get_dir_items(s_dir)).union(set(get_dir_items(av_dir)))))
                    new_sel = run_checklist("Skills Checklist Manager", all_s, set(get_dir_items(s_dir)), agent_name=agent_cfg["name"])
                    if new_sel is not None:
                        for s in all_s:
                            ap = os.path.join(s_dir, s)
                            sp = os.path.join(av_dir, s)
                            if s in new_sel and os.path.exists(sp): shutil.move(sp, ap)
                            elif s not in new_sel and os.path.exists(ap): shutil.move(ap, sp)
                    init_screen()
                elif cursor == 1:
                    mf = agent_cfg.get("mcp_file")
                    if not mf or not os.path.exists(mf):
                        init_screen()
                        print(f"\n{CLR_YELLOW}No MCP configuration file for {agent_cfg['name']}.{CLR_RESET}")
                        input("Press [Enter] to continue...")
                        init_screen()
                        continue
                    act_m, dis_m = read_mcp_config(agent_cfg)
                    all_m = sorted(list(set(act_m.keys()).union(set(dis_m.keys()))))
                    new_sel = run_checklist("MCP Servers Checklist Manager", all_m, set(act_m.keys()), agent_name=agent_cfg["name"])
                    if new_sel is not None:
                        save_mcp_servers(agent_cfg, new_sel)
                    init_screen()
                elif cursor == 2:
                    manage_agent_models(agent_cfg, all_agents)
                    init_screen()
                elif cursor == 3:
                    add_skills_interactive(agent_cfg=agent_cfg, all_agents=all_agents)
                    init_screen()
                elif cursor == 4:
                    add_mcp_interactive(agent_cfg=agent_cfg, all_agents=all_agents)
                    init_screen()
                elif cursor == 5:
                    # Plugins checklist
                    p_dir = agent_cfg.get("plugins_dir")
                    if p_dir and os.path.exists(p_dir):
                        plugs = get_agent_plugins(agent_cfg)
                        run_checklist("Plugins Checklist", plugs, set(plugs), agent_name=agent_cfg["name"], allow_delete=False)
                    else:
                        init_screen()
                        print(f"\n{CLR_YELLOW}No plugins directory found for {agent_cfg['name']}.{CLR_RESET}")
                        input("Press [Enter] to continue...")
                    init_screen()
                elif cursor == 6:
                    p = agent_cfg.get("skills_dir") or agent_cfg.get("mcp_file") or USERPROFILE
                    if os.path.exists(p): os.startfile(os.path.dirname(p) if os.path.isfile(p) else p)
                elif cursor == 7:
                    break
            elif key == '1': cursor = 0
            elif key == '2': cursor = 1
            elif key == '3': cursor = 2
            elif key == '4': cursor = 3
            elif key == '5': cursor = 4
            elif key == '6': cursor = 5
            elif key == '7': cursor = 6
            elif key.upper() == 'M':
                manage_agent_models(agent_cfg, all_agents)
                init_screen()
            elif key == '0' or key in ('ESC', 'q'):
                break
    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)

# ================= MASTER AGENT SELECTOR HUB =================


def open_agent_folder_cli():
    keys = list(FOLDER_DATA.keys())
    cursor_idx = 0
    while True:
        init_screen()
        print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
        print(f"{CLR_BOLD}{CLR_CYAN}                   AI AGENT ECOSYSTEM CONTROL CENTER - FOLDERS                  {CLR_RESET}")
        print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
        print(f"{CLR_WHITE}{CLR_BOLD}Select an AI Agent or Category to explore its Skills, MCPs, and Configs:{CLR_RESET}")
        print("--------------------------------------------------------------------------------")
        for idx, key in enumerate(keys):
            cat = FOLDER_DATA[key]
            is_active = (idx == cursor_idx)
            cursor = f"{CLR_CYAN}>{CLR_RESET}" if is_active else " "
            num_tag = f"[{key:>2}]"
            if key == "17":
                print(f"{CLR_DIM}--- MASTER PUBLISH WAREHOUSES (D: DRIVE) -------------------------------------{CLR_RESET}")
            if is_active:
                print(f" {cursor} {CLR_REVERSE} {num_tag} {cat['title']:<32}{CLR_RESET} {CLR_YELLOW}{cat['desc']}{CLR_RESET}")
            else:
                print(f" {cursor} {CLR_BOLD}{num_tag}{CLR_RESET} {cat['title']:<32} {CLR_DIM}{cat['desc']}{CLR_RESET}")

        is_exit = (cursor_idx == len(keys))
        exit_cur = f"{CLR_CYAN}>{CLR_RESET}" if is_exit else " "
        if is_exit:
            print(f" {exit_cur} {CLR_REVERSE} [ 0] Return to Main Menu                 {CLR_RESET}")
        else:
            print(f" {exit_cur} {CLR_BOLD} [ 0]{CLR_RESET} Return to Main Menu")
        print("--------------------------------------------------------------------------------")
        print(f"{CLR_DIM}Navigation: [↑/↓] Move  [Enter] Open Category  [1-20/0] Jump  [Esc/q] Back{CLR_RESET}")

        k = read_key()
        if k in ('UP', 'k'):
            cursor_idx = (cursor_idx - 1) % (len(keys) + 1)
        elif k in ('DOWN', 'j'):
            cursor_idx = (cursor_idx + 1) % (len(keys) + 1)
        elif k in ('ESC', 'q') or (k == 'ENTER' and cursor_idx == len(keys)) or k == '0':
            break
        elif k == 'ENTER':
            run_folder_category_cli(keys[cursor_idx])
        elif k.isdigit():
            val = k
            if val in FOLDER_DATA:
                cursor_idx = keys.index(val)
                run_folder_category_cli(val)

def run_folder_category_cli(cat_key):
    cat = FOLDER_DATA.get(cat_key)
    if not cat: return
    items = cat.get("items", [])
    cursor_idx = 0
    while True:
        init_screen()
        print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
        print(f"{CLR_BOLD}{CLR_CYAN}  {cat['title'].upper()} - FOLDERS & CONFIGURATIONS {CLR_RESET}")
        print(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
        for idx, item in enumerate(items):
            name, path, desc = item
            exists = os.path.exists(path)
            st = f"{CLR_GREEN}EXISTS{CLR_RESET}" if exists else f"{CLR_RED}MISSING{CLR_RESET}"
            is_active = (idx == cursor_idx)
            indicator = f"{CLR_CYAN}> {CLR_RESET}" if is_active else "  "
            if is_active:
                print(f"{indicator}{CLR_REVERSE} [{idx+1:>2}] {name:<36} [{st}]{CLR_RESET}")
                print(f"     {CLR_YELLOW}Path: {path}{CLR_RESET}")
                print(f"     {CLR_DIM}Desc: {desc}{CLR_RESET}")
            else:
                print(f"{indicator}{CLR_WHITE} [{idx+1:>2}] {name:<36} [{st}]{CLR_RESET}")
        print("--------------------------------------------------------------------------------")
        print(f"{CLR_DIM}[E] Explorer  [V] Editor  [C] Copy Path  [T] Terminal  [↑/↓] Move  [Esc/q] Back{CLR_RESET}")

        k = read_key()
        if k in ('UP', 'k'):
            cursor_idx = (cursor_idx - 1) % len(items)
        elif k in ('DOWN', 'j'):
            cursor_idx = (cursor_idx + 1) % len(items)
        elif k in ('ESC', 'q'):
            break
        elif k in ('ENTER', 'e', 'E'):
            desktop_open_explorer(items[cursor_idx][1])
        elif k in ('v', 'V'):
            desktop_open_editor(items[cursor_idx][1])
        elif k in ('c', 'C'):
            desktop_copy_clipboard(items[cursor_idx][1])
        elif k in ('t', 'T'):
            desktop_open_terminal(items[cursor_idx][1])

def master_hub():
    cursor = 0
    init_screen()
    print(CLR_HIDE_CURSOR, end="", flush=True)

    try:
        while True:
            # Dynamically discover all agents installed on this machine
            agents = discover_installed_agents()
            agent_list = list(agents.values())

            # Compute system totals
            tot_s = sum(len(get_agent_skills(a)[0]) for a in agent_list)
            tot_m = sum(len(read_mcp_config(a)[0]) for a in agent_list)
            tot_p = sum(len(get_agent_plugins(a)) for a in agent_list)

            lines = []
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}                   OMNIAGENT MANAGER - UNIVERSAL AI AGENT CONTROL HUB                        {CLR_RESET}")
            lines.append(f"{CLR_BOLD}{CLR_CYAN}================================================================================{CLR_RESET}")
            
            bar = "█" * 16 + "░" * 4
            lines.append(f"Auto-Discovery: {CLR_GREEN}[{bar}]{CLR_RESET} {CLR_BOLD}{len(agents)} AGENTS DETECTED ON SYSTEM{CLR_RESET}")
            lines.append(f"{CLR_DIM}Ecosystem Totals: {tot_s} Active Skills | {tot_m} Active MCPs | {tot_p} Plugins{CLR_RESET}")
            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_WHITE}Detected AI Coding Agents & Platforms:{CLR_RESET}")

            for i, a in enumerate(agent_list):
                is_cur = (i == cursor)
                indicator = f"{CLR_CYAN}> {CLR_RESET}" if is_cur else "  "
                act_s, av_s = get_agent_skills(a)
                act_m, dis_m = read_mcp_config(a)
                plugs = get_agent_plugins(a)
                m_info = get_agent_models_and_providers(a)

                tag = f"Model: {m_info['active_model'][:18]:<18} | Skills: {len(act_s):<3} | MCPs: {len(act_m):<2}"
                if is_cur:
                    lines.append(f"{indicator}{CLR_BOLD}{CLR_REVERSE} [{i+1:>2}] {a['name']:<27} {CLR_RESET}  {CLR_YELLOW}{tag}{CLR_RESET}")
                else:
                    lines.append(f"{indicator}{CLR_WHITE} [{i+1:>2}] {a['name']:<27}{CLR_RESET}  {CLR_DIM}{tag}{CLR_RESET}")

            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Global & Ecosystem Operations:{CLR_RESET}")
            
            idx_m = len(agent_list)
            idx_g = len(agent_list) + 1
            idx_w = len(agent_list) + 2
            idx_f = len(agent_list) + 3
            idx_x = len(agent_list) + 4

            ind_m = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_m) else "  "
            ind_g = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_g) else "  "
            ind_w = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_w) else "  "
            ind_f = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_f) else "  "
            ind_x = f"{CLR_CYAN}> {CLR_RESET}" if (cursor == idx_x) else "  "

            lines.append(f"{ind_m}[M] Universal Models & Providers Hub (Cross-Agent Models & 1-Click Deploy)")
            lines.append(f"{ind_g}[G] Global Skills Hub (Sync & Manage Skills Across ALL Agents)")
            lines.append(f"{ind_w}[W] Master Skills Warehouse Browser (1,350+ Upstream Skills)")
            lines.append(f"{ind_f}[F] 📂 Open Agent Folders & Files (20 Categories, 150+ Locations)")
            lines.append(f"{ind_x}[0] Exit")
            lines.append("--------------------------------------------------------------------------------")
            lines.append(f"{CLR_BOLD}Navigation:{CLR_RESET} [↑/↓] Move Cursor  [Enter] Select  [1-{len(agent_list)}/M/G/W/F/0] Jump  [Esc/q] Quit")
            lines.append("================================================================================")

            render_frame(lines)

            key = read_key()
            total_menu_rows = len(agent_list) + 5

            if key in ('UP', 'k'):
                if cursor > 0: cursor -= 1
            elif key in ('DOWN', 'j'):
                if cursor < total_menu_rows - 1: cursor += 1
            elif key == 'ENTER':
                if cursor < len(agent_list):
                    manage_single_agent(agent_list[cursor], agents)
                    init_screen()
                elif cursor == idx_m:
                    universal_models_hub(agents)
                    init_screen()
                elif cursor == idx_g:
                    global_skills_hub(agents)
                    init_screen()
                elif cursor == idx_w:
                    browse_warehouse_import()
                    init_screen()
                elif cursor == idx_f:
                    open_agent_folder_cli()
                    init_screen()
                elif cursor == idx_x:
                    break
            elif key.isdigit():
                val = int(key)
                if 1 <= val <= len(agent_list):
                    manage_single_agent(agent_list[val-1], agents)
                    init_screen()
                elif val == 0:
                    break
            elif key.upper() == 'M':
                universal_models_hub(agents)
                init_screen()
            elif key.upper() == 'G':
                global_skills_hub(agents)
                init_screen()
            elif key.upper() == 'W':
                browse_warehouse_import()
                init_screen()
            elif key.upper() == 'F':
                open_agent_folder_cli()
                init_screen()
            elif key in ('ESC', 'q'):
                break
    finally:
        print(CLR_SHOW_CURSOR, end="", flush=True)
        init_screen()
        print("Done. Universal Agent Customizer closed.")


# ================= ADVANCED MCP WORKSPACES, HEALTH, REGISTRY & PROFILE ENGINES =================

MCP_PRESETS = [
    {
        "id": "fullstack",
        "name": "🌐 Full-Stack Web",
        "desc": "Filesystem, GitHub, Brave Search, Puppeteer browser automation",
        "match": ["filesystem", "github", "brave", "puppeteer", "fetch"],
    },
    {
        "id": "datascience",
        "name": "📊 Data Science & SQL",
        "desc": "PostgreSQL, SQLite, Filesystem, Memory knowledge graph",
        "match": ["postgres", "sqlite", "filesystem", "memory", "database"],
    },
    {
        "id": "devops",
        "name": "🚀 DevOps & Cloud",
        "desc": "Docker, Kubernetes, AWS, GitHub, Filesystem",
        "match": ["docker", "kubernetes", "aws", "github", "filesystem"],
    },
    {
        "id": "security",
        "name": "🛡️ Security & Audit",
        "desc": "Semgrep, Sentry, GitHub, Filesystem auditing tools",
        "match": ["security", "semgrep", "sentry", "github", "filesystem"],
    },
    {
        "id": "minimal",
        "name": "🪶 Minimal / Lean",
        "desc": "Filesystem only - preserves maximum LLM context window",
        "match": ["filesystem"],
    },
    {
        "id": "all_active",
        "name": "✨ All Active",
        "desc": "Enable all configured MCP servers across agent",
        "match": ["*"],
    },
]

REGISTRY_MCPS = [
    {
        "id": "github",
        "name": "GitHub MCP",
        "category": "Developer Tools",
        "desc": "Inspect repos, pull requests, issues, commits, branches, and search code",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env_vars": ["GITHUB_PERSONAL_ACCESS_TOKEN"],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/github"
    },
    {
        "id": "postgres",
        "name": "PostgreSQL Database",
        "category": "Databases",
        "desc": "Inspect schemas, execute read-only queries, and analyze Postgres databases",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
        "env_vars": ["DATABASE_URL"],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/postgres"
    },
    {
        "id": "sqlite",
        "name": "SQLite Database",
        "category": "Databases",
        "desc": "Query, inspect tables, and interact with local SQLite databases",
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "${DB_PATH}"],
        "env_vars": ["DB_PATH"],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite"
    },
    {
        "id": "brave-search",
        "name": "Brave Web Search",
        "category": "Web & Search",
        "desc": "Web search and local search capabilities using the Brave Search API",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env_vars": ["BRAVE_API_KEY"],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
    },
    {
        "id": "filesystem",
        "name": "Secure Filesystem",
        "category": "Core System",
        "desc": "Direct file read/write access with directory allowlist security",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "${ALLOWED_DIR}"],
        "env_vars": ["ALLOWED_DIR"],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem"
    },
    {
        "id": "docker",
        "name": "Docker Container Manager",
        "category": "DevOps",
        "desc": "Manage containers, images, volumes, and inspect Docker daemon",
        "command": "uvx",
        "args": ["mcp-server-docker"],
        "env_vars": [],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/docker"
    },
    {
        "id": "memory",
        "name": "Knowledge Graph Memory",
        "category": "Memory & State",
        "desc": "Persistent knowledge graph memory system for entities and relations",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "env_vars": [],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/memory"
    },
    {
        "id": "puppeteer",
        "name": "Puppeteer Web Automation",
        "category": "Browser Automation",
        "desc": "Browser automation, web scraping, and JavaScript rendering via Puppeteer",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env_vars": [],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer"
    },
    {
        "id": "fetch",
        "name": "Web Fetch & Scraper",
        "category": "Web & Search",
        "desc": "Fetch web pages and convert HTML to markdown for LLM consumption",
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "env_vars": [],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/fetch"
    },
    {
        "id": "sequential-thinking",
        "name": "Sequential Thinking Reasoning",
        "category": "Reasoning & Agentic",
        "desc": "Dynamic step-by-step reasoning and problem-solving tool for complex tasks",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env_vars": [],
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking"
    },
    {
        "id": "context-mode",
        "name": "Context Mode Sandbox",
        "category": "Sandbox & Optimization",
        "desc": "Executes analysis inside sandbox and keeps raw bytes out of LLM context",
        "command": "npx",
        "args": ["-y", "@context-mode/mcp"],
        "env_vars": [],
        "docs": "https://github.com/context-mode"
    }
]

def apply_mcp_preset(agent_cfg, preset_id, all_agents=None, broadcast=False):
    preset = next((p for p in MCP_PRESETS if p["id"] == preset_id), None)
    if not preset:
        return False, "Preset not found"

    targets = list(all_agents.values()) if (broadcast and all_agents) else [agent_cfg]
    modified = []

    for ag in targets:
        mcp_file = ag.get("mcp_file")
        if not mcp_file or not os.path.exists(mcp_file):
            continue
        act_m, dis_m = read_mcp_config(ag)
        all_names = sorted(list(set(act_m.keys()).union(set(dis_m.keys()))))
        if not all_names:
            continue

        active_set = set()
        if "*" in preset["match"]:
            active_set = set(all_names)
        else:
            for name in all_names:
                for pattern in preset["match"]:
                    if pattern.lower() in name.lower():
                        active_set.add(name)
                        break

        # Save backup first
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            shutil.copy2(mcp_file, f"{mcp_file}.{ts}.bak")
        except Exception:
            pass

        save_mcp_servers(ag, active_set)
        modified.append(ag["name"])

    scope_str = f"broadcasted across {len(modified)} agents" if broadcast else f"applied to {agent_cfg['name']}"
    return True, f"Preset '{preset['name']}' {scope_str} ({len(modified)} updated)"

def probe_mcp_server_health(server_name, server_def, timeout=2.0):
    start = time.time()
    url = server_def.get("url") or server_def.get("endpoint")
    if url:
        try:
            if HAS_HTTPX:
                resp = httpx.get(url, timeout=timeout)
                ms = int((time.time() - start) * 1000)
                if resp.status_code < 400:
                    return True, ms, f"HTTP {resp.status_code} OK"
                return False, ms, f"HTTP {resp.status_code}"
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "OmniAgent-Health/4.0"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    ms = int((time.time() - start) * 1000)
                    return True, ms, f"HTTP {resp.status} OK"
        except Exception as e:
            return False, 0, f"Connect Error: {type(e).__name__}"

    cmd = server_def.get("command")
    args = list(server_def.get("args", []))
    if isinstance(cmd, (list, tuple)):
        if not cmd:
            return False, 0, "Empty command list"
        args = list(cmd[1:]) + args
        cmd = cmd[0]

    if not cmd or not isinstance(cmd, str):
        return False, 0, "No command configured"

    bin_path = shutil.which(cmd)
    if not bin_path:
        return False, 0, f"Binary '{cmd}' not found in PATH"

    try:
        proc = subprocess.Popen(
            [bin_path] + list(args),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        ping_payload = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"omni-probe","version":"1.0"}}}\n'
        try:
            stdout, _ = proc.communicate(input=ping_payload, timeout=timeout)
            ms = int((time.time() - start) * 1000)
            if "jsonrpc" in stdout:
                return True, ms, "JSON-RPC Handshake OK"
            elif proc.returncode == 0:
                return True, ms, "Exited Cleanly (0)"
            else:
                return False, ms, f"Exit Code {proc.returncode}"
        except subprocess.TimeoutExpired:
            proc.kill()
            ms = int((time.time() - start) * 1000)
            return True, ms, "Active (Listening on Stdio)"
    except Exception as e:
        return False, 0, str(e)

def list_agent_backups(agent_cfg):
    backups = []
    dirs_to_check = set()
    mcp_file = agent_cfg.get("mcp_file")
    if mcp_file:
        dirs_to_check.add(os.path.dirname(mcp_file))
    skills_dir = agent_cfg.get("skills_dir")
    if skills_dir:
        dirs_to_check.add(skills_dir)
        dirs_to_check.add(os.path.dirname(skills_dir))

    for d in dirs_to_check:
        if not os.path.exists(d): continue
        try:
            for entry in os.scandir(d):
                if entry.is_file() and entry.name.endswith(".bak"):
                    st = entry.stat()
                    mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
                    backups.append({
                        "path": entry.path,
                        "name": entry.name,
                        "dir": d,
                        "mtime": mtime_str,
                        "raw_mtime": st.st_mtime,
                        "size_bytes": st.st_size,
                        "target_name": entry.name.split(".")[0]
                    })
        except Exception:
            pass

    backups.sort(key=lambda x: x["raw_mtime"], reverse=True)
    return backups

def restore_backup_file(backup_path, target_path=None):
    if not os.path.exists(backup_path):
        return False, "Backup file not found"
    
    if not target_path:
        d = os.path.dirname(backup_path)
        base = os.path.basename(backup_path)
        parts = base.split(".")
        if len(parts) >= 3 and parts[-1] == "bak":
            target_name = ".".join(parts[:-2])
            target_path = os.path.join(d, target_name)
        else:
            target_path = backup_path[:-4]

    try:
        if os.path.exists(target_path):
            safety = f"{target_path}.pre_restore_{int(time.time())}.bak"
            shutil.copy2(target_path, safety)
        shutil.copy2(backup_path, target_path)
        return True, f"Successfully restored to {os.path.basename(target_path)}"
    except Exception as e:
        return False, f"Restore failed: {e}"

def calculate_agent_tools_token_metrics(agent_cfg):
    act_m, _ = read_mcp_config(agent_cfg)
    raw_str = json.dumps(act_m)
    base_tokens = max(10, int(len(raw_str) / 3.85)) if act_m else 0
    
    ag_id = agent_cfg.get("id")
    trimmed_count = 0
    if ag_id:
        for s_name in act_m:
            trimmed_count += len(get_trimmed_subtools(ag_id, s_name))
    saved_tokens = trimmed_count * 200
    est_tokens = max(0, base_tokens - saved_tokens)

    max_context = 128000
    headroom = max(0, max_context - est_tokens)
    pct = min(100.0, (est_tokens / max_context) * 100)
    
    cost_claude = est_tokens * 0.000003
    cost_deepseek = est_tokens * 0.00000055
    cost_gpt4o = est_tokens * 0.0000025

    total_blocks = 14
    filled = min(total_blocks, max(0, int((pct / 100.0) * total_blocks)))
    bar = "█" * filled + "░" * (total_blocks - filled)

    return {
        "tokens": est_tokens,
        "base_tokens": base_tokens,
        "servers_count": len(act_m),
        "headroom": headroom,
        "pct_used": pct,
        "bar": bar,
        "cost_claude": cost_claude,
        "cost_deepseek": cost_deepseek,
        "cost_gpt4o": cost_gpt4o,
        "trimmed_count": trimmed_count,
        "saved_tokens": saved_tokens
    }

def export_omni_profile(agents, out_path="omni-profile.json"):
    if not os.path.isabs(out_path):
        cwd = os.getcwd()
        try:
            test_file = os.path.join(cwd, ".test_perm.tmp")
            with open(test_file, "w") as tf: tf.write("ok")
            os.remove(test_file)
            out_path = os.path.join(cwd, out_path)
        except Exception:
            out_path = os.path.join(USERPROFILE, out_path)

    bundle = {
        "version": "4.1.0",
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "agents": {}
    }
    for k, ag in agents.items():
        m_info = get_agent_models_and_providers(ag)
        act_s, _ = get_agent_skills(ag)
        act_m, _ = read_mcp_config(ag)
        bundle["agents"][k] = {
            "name": ag["name"],
            "active_model": m_info["active_model"],
            "active_provider": m_info["active_provider"],
            "base_url": m_info["base_url"],
            "active_skills": act_s,
            "active_mcps": list(act_m.keys())
        }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
    return True, f"Profile exported to {os.path.abspath(out_path)}"

def import_omni_profile(agents, in_path="omni-profile.json"):
    if not os.path.isabs(in_path) and not os.path.exists(in_path):
        cand = os.path.join(USERPROFILE, in_path)
        if os.path.exists(cand):
            in_path = cand

    if not os.path.exists(in_path):
        return False, f"Profile file not found: {in_path}"
    with open(in_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    imported_agents = bundle.get("agents", {})
    count = 0
    for k, data in imported_agents.items():
        ag = agents.get(k)
        if not ag: continue
        if data.get("active_model"):
            set_agent_active_model(ag, data["active_model"], provider_id=data.get("active_provider"))
        if "active_mcps" in data:
            save_mcp_servers(ag, set(data["active_mcps"]))
        count += 1

    return True, f"Imported configuration settings for {count} agents"

def install_registry_mcp(mcp_def, env_values, target_agents):
    mcp_id = mcp_def["id"]
    args = []
    for a in mcp_def.get("args", []):
        arg_val = a
        for ev, val in env_values.items():
            arg_val = arg_val.replace(f"${{{ev}}}", val)
        args.append(arg_val)

    env_dict = {}
    for ev in mcp_def.get("env_vars", []):
        if ev in env_values and env_values[ev]:
            env_dict[ev] = env_values[ev]

    installed_count = 0
    for ag in target_agents:
        mcp_file = ag.get("mcp_file")
        if not mcp_file:
            continue
        try:
            os.makedirs(os.path.dirname(mcp_file), exist_ok=True)
            data = {}
            if os.path.exists(mcp_file):
                # Save backup
                ts = time.strftime("%Y%m%d_%H%M%S")
                shutil.copy2(mcp_file, f"{mcp_file}.{ts}.bak")
                with open(mcp_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if "mcpServers" not in data:
                data["mcpServers"] = {}

            entry = {
                "command": mcp_def["command"],
                "args": args,
                "disabled": False,
                "enabled": True
            }
            if env_dict:
                entry["env"] = env_dict

            data["mcpServers"][mcp_id] = entry

            with open(mcp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            installed_count += 1
        except Exception:
            pass

    return installed_count > 0, f"Installed {mcp_def['name']} to {installed_count} agents"

def install_online_skill(source_type, source_val, target_agent, skill_name=None):
    dest_dir = target_agent.get("skills_dir")
    if not dest_dir:
        return False, "Target agent has no skills directory configured"

    os.makedirs(dest_dir, exist_ok=True)

    if source_type == "git":
        repo_name = skill_name or source_val.rstrip("/").split("/")[-1].replace(".git", "")
        target_folder = os.path.join(dest_dir, repo_name)
        if os.path.exists(target_folder):
            return False, f"Skill folder '{repo_name}' already exists"
        try:
            res = subprocess.run(["git", "clone", "--depth", "1", source_val, target_folder], capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                return True, f"Successfully cloned skill '{repo_name}'"
            return False, f"Git clone failed: {res.stderr[:200]}"
        except Exception as e:
            return False, f"Git error: {e}"

    elif source_type == "url":
        s_name = skill_name or "custom_downloaded_skill"
        target_folder = os.path.join(dest_dir, s_name)
        os.makedirs(target_folder, exist_ok=True)
        target_file = os.path.join(target_folder, "SKILL.md")
        try:
            if HAS_HTTPX:
                resp = httpx.get(source_val, timeout=15)
                content = resp.text
            else:
                with urllib.request.urlopen(source_val, timeout=15) as resp:
                    content = resp.read().decode("utf-8")
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
            return True, f"Downloaded skill to '{s_name}/SKILL.md'"
        except Exception as e:
            return False, f"Download failed: {e}"

    elif source_type == "npx":
        pkg = source_val.strip()
        try:
            res = subprocess.run(["npx", "-y", pkg], capture_output=True, text=True, timeout=45)
            if res.returncode == 0:
                return True, f"Executed npx command for '{pkg}'"
            return False, f"npx execution failed: {res.stderr[:200]}"
        except Exception as e:
            return False, f"npx error: {e}"

    return False, f"Unknown source type: {source_type}"


# ================= TEXTUAL DESKTOP-GRADE TUI APPLICATION =================

THEME_FILE = os.path.join(AI_PROJECTS, ".agent_customizer_theme")
THEME_FILE_USER = os.path.join(USERPROFILE, ".gemini", ".agent_customizer_theme")

def save_user_theme(theme_name: str):
    for p in (THEME_FILE, THEME_FILE_USER):
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(theme_name.strip())
        except Exception:
            pass

def load_user_theme() -> str:
    for p in (THEME_FILE, THEME_FILE_USER):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val: return val
            except Exception:
                pass
    return "github-dark"

def desktop_open_explorer(path):
    if open_in_explorer_fn:
        return open_in_explorer_fn(path)
    if not os.path.exists(path):
        return False, f"Path not found: {path}"
    try:
        if os.path.isdir(path):
            os.startfile(path)
        else:
            subprocess.run(f'explorer.exe /select,"{path}"', shell=True)
        return True, "Opened in Windows Explorer!"
    except Exception as e:
        return False, str(e)

def desktop_open_editor(path):
    if open_in_editor_fn:
        return open_in_editor_fn(path)
    if not os.path.exists(path):
        return False, f"Path not found: {path}"
    try:
        os.startfile(path)
        return True, "Opened in default editor!"
    except Exception:
        try:
            subprocess.run(f'notepad.exe "{path}"', shell=True)
            return True, "Opened in Notepad!"
        except Exception as e:
            return False, str(e)

def desktop_copy_clipboard(text):
    if copy_to_clipboard_fn:
        return copy_to_clipboard_fn(text)
    try:
        subprocess.run('clip', input=text.strip().encode('utf-8'), shell=True, check=True)
        return True, "Copied to clipboard!"
    except Exception as e:
        return False, str(e)

def desktop_open_terminal(path):
    if open_terminal_fn:
        return open_terminal_fn(path)
    dir_p = path if os.path.isdir(path) else os.path.dirname(path)
    if not os.path.exists(dir_p):
        return False, f"Directory not found: {dir_p}"
    try:
        subprocess.run(f'start cmd.exe /k "cd /d {dir_p}"', shell=True)
        return True, "Terminal opened!"
    except Exception as e:
        return False, str(e)

# ================= v4.1 ADVANCED FLEET & MCP ENGINE =================

TRIMMED_TOOLS_FILE = os.path.join(USERPROFILE, ".omni_trimmed_tools.json")

def get_trimmed_subtools(agent_id, server_name):
    """Retrieve set of tool names disabled/trimmed for a specific MCP server and agent."""
    if not os.path.exists(TRIMMED_TOOLS_FILE):
        return set()
    try:
        with open(TRIMMED_TOOLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        key = f"{agent_id}::{server_name}"
        return set(data.get(key, []))
    except Exception:
        return set()

def toggle_trimmed_subtool(agent_id, server_name, tool_name, agent_cfg=None):
    """Toggle a sub-tool disabled state, saving to .omni_trimmed_tools.json and agent config."""
    data = {}
    if os.path.exists(TRIMMED_TOOLS_FILE):
        try:
            with open(TRIMMED_TOOLS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    key = f"{agent_id}::{server_name}"
    curr = set(data.get(key, []))
    if tool_name in curr:
        curr.remove(tool_name)
        new_st = "ENABLED"
    else:
        curr.add(tool_name)
        new_st = "TRIMMED (DISABLED)"
    data[key] = list(curr)
    try:
        with open(TRIMMED_TOOLS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Also persist in agent MCP config file if writable
        if agent_cfg and agent_cfg.get("mcp_file") and os.path.exists(agent_cfg["mcp_file"]):
            try:
                with open(agent_cfg["mcp_file"], "r", encoding="utf-8") as f:
                    cfg_data = json.load(f)
                servers_dict = cfg_data.get("mcpServers") or cfg_data.get("mcp")
                if isinstance(servers_dict, dict) and server_name in servers_dict:
                    s_obj = servers_dict[server_name]
                    if isinstance(s_obj, dict):
                        if curr:
                            s_obj["disabled_tools"] = list(curr)
                        else:
                            s_obj.pop("disabled_tools", None)
                        with open(agent_cfg["mcp_file"], "w", encoding="utf-8") as f:
                            json.dump(cfg_data, f, indent=2)
            except Exception:
                pass

        return True, f"Tool '{tool_name}' in '{server_name}' is now {new_st}"
    except Exception as e:
        return False, str(e)

def query_mcp_tools(server_name, server_def, timeout=4.0):
    """Query live MCP server tools schema via JSON-RPC protocol without LLM tokens."""
    cmd = server_def.get("command")
    args = list(server_def.get("args", []))
    if isinstance(cmd, (list, tuple)):
        if not cmd: return False, "Empty command list"
        args = list(cmd[1:]) + args
        cmd = cmd[0]
    if not cmd or not isinstance(cmd, str):
        return False, "No valid command configured"
    bin_path = shutil.which(cmd)
    if not bin_path:
        return False, f"Binary '{cmd}' not found in PATH"

    child_env = os.environ.copy()
    if server_def.get("env") and isinstance(server_def["env"], dict):
        child_env.update(server_def["env"])

    try:
        proc = subprocess.Popen(
            [bin_path] + list(args),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=child_env,
            text=True
        )
        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "omni-inspector", "version": "1.0"}
            }
        }) + "\n"
        proc.stdin.write(init_req)
        proc.stdin.flush()

        init_notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        proc.stdin.write(init_notif)
        proc.stdin.flush()

        tools_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}) + "\n"
        proc.stdin.write(tools_req)
        proc.stdin.flush()

        start = time.time()
        tools_result = None
        while time.time() - start < timeout:
            line = proc.stdout.readline()
            if not line: break
            try:
                msg = json.loads(line)
                if msg.get("id") == 2:
                    tools_result = msg.get("result", {}).get("tools", [])
                    break
            except Exception:
                pass
        proc.kill()
        if tools_result is not None:
            return True, tools_result
        return False, "No tools returned (timeout or unsupported)"
    except Exception as e:
        return False, str(e)

def execute_mcp_tool(server_name, server_def, tool_name, arguments=None, timeout=6.0):
    """Directly test and execute an MCP tool live via JSON-RPC protocol without LLM token cost."""
    if arguments is None:
        arguments = {}
    cmd = server_def.get("command")
    args = list(server_def.get("args", []))
    if isinstance(cmd, (list, tuple)):
        if not cmd: return False, "Empty command list"
        args = list(cmd[1:]) + args
        cmd = cmd[0]
    if not cmd or not isinstance(cmd, str):
        return False, "No valid command configured"
    bin_path = shutil.which(cmd)
    if not bin_path:
        return False, f"Binary '{cmd}' not found in PATH"

    child_env = os.environ.copy()
    if server_def.get("env") and isinstance(server_def["env"], dict):
        child_env.update(server_def["env"])

    try:
        proc = subprocess.Popen(
            [bin_path] + list(args),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=child_env,
            text=True
        )
        init_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "omni-tool-runner", "version": "1.0"}
            }
        }) + "\n"
        proc.stdin.write(init_req)
        proc.stdin.flush()

        init_notif = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        proc.stdin.write(init_notif)
        proc.stdin.flush()

        call_req = json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments}
        }) + "\n"
        proc.stdin.write(call_req)
        proc.stdin.flush()

        start = time.time()
        call_result = None
        while time.time() - start < timeout:
            line = proc.stdout.readline()
            if not line: break
            try:
                msg = json.loads(line)
                if msg.get("id") == 3:
                    if "error" in msg:
                        call_result = (False, json.dumps(msg["error"], indent=2))
                    else:
                        call_result = (True, json.dumps(msg.get("result", {}), indent=2))
                    break
            except Exception:
                pass
        proc.kill()
        if call_result is not None:
            return call_result
        return False, "Tool call timed out or returned no response"
    except Exception as e:
        return False, str(e)

def scan_fleet_processes():
    """Scan local AI inference engine ports and active agent processes via psutil."""
    def check_port(port, host="127.0.0.1"):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.25)
                return s.connect_ex((host, port)) == 0
        except Exception:
            return False

    engines = [
        {"name": "Ollama Inference Engine", "port": 11434, "online": check_port(11434)},
        {"name": "LM Studio Local Server", "port": 1234, "online": check_port(1234)},
        {"name": "vLLM / LocalAI Server", "port": 8000, "online": check_port(8000)},
        {"name": "LocalAI Secondary", "port": 5000, "online": check_port(5000)},
    ]

    agent_keywords = ["claude", "antigravity", "agy", "opencode", "cursor", "codex", "hermes", "code", "gemini", "copilot"]
    procs = []
    if HAS_PSUTIL:
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                pname = p.info['name'].lower()
                for kw in agent_keywords:
                    if kw in pname:
                        mem_mb = int(p.info['memory_info'].rss / (1024 * 1024))
                        procs.append({
                            "pid": p.info['pid'],
                            "name": p.info['name'],
                            "agent_kw": kw,
                            "cpu": p.info.get('cpu_percent', 0.0),
                            "mem_mb": mem_mb
                        })
                        break
            except Exception:
                pass
    return {"engines": engines, "processes": procs}

def extract_agent_config_flags(agent_cfg):
    """Recursively scan agent JSON configs to discover all toggleable boolean feature flags."""
    flags = []
    files_to_check = []
    mcp_file = agent_cfg.get("mcp_file")
    if mcp_file and os.path.exists(mcp_file):
        files_to_check.append(mcp_file)

    ag_id = agent_cfg.get("id", "")
    candidates = [
        os.path.join(USERPROFILE, f".{ag_id}.json"),
        os.path.join(USERPROFILE, f".{ag_id}", "config.json"),
        os.path.join(USERPROFILE, ".config", ag_id, f"{ag_id}.json"),
        os.path.join(USERPROFILE, ".gemini", "antigravity", "config.json"),
        os.path.join(USERPROFILE, ".gemini", "config.json"),
        os.path.join(USERPROFILE, ".cursor", "settings.json"),
        os.path.join(USERPROFILE, "AppData", "Roaming", "Cursor", "User", "settings.json"),
        os.path.join(USERPROFILE, "AppData", "Roaming", "Code", "User", "settings.json"),
    ]
    for c in candidates:
        if c and os.path.exists(c) and c not in files_to_check:
            files_to_check.append(c)

    def walk_dict(data, prefix=""):
        items = []
        if isinstance(data, dict):
            for k, v in data.items():
                full_k = f"{prefix}.{k}" if prefix else k
                if isinstance(v, bool):
                    section = prefix.split(".")[0] if prefix else "root"
                    items.append((full_k, v, section))
                elif isinstance(v, dict) and k not in ("mcpServers", "mcp", "providers", "models", "history", "conversations"):
                    items.extend(walk_dict(v, full_k))
        return items

    for fpath in files_to_check:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            extracted = walk_dict(d)
            for k, v, sec in extracted:
                flags.append({
                    "file": fpath,
                    "filename": os.path.basename(fpath),
                    "key": k,
                    "value": v,
                    "section": sec
                })
        except Exception:
            pass
    return flags

def set_agent_config_flag(file_path, dot_path, new_value):
    """Atomically toggle a boolean feature flag in a JSON file with automatic timestamped .bak backup."""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    try:
        ts = time.strftime("%Y%m%d_%H%M%S")
        bak_file = f"{file_path}.{ts}.bak"
        shutil.copy2(file_path, bak_file)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        keys = dot_path.split(".")
        curr = data
        for k in keys[:-1]:
            if k not in curr or not isinstance(curr[k], dict):
                curr[k] = {}
            curr = curr[k]
        curr[keys[-1]] = bool(new_value)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        st_str = "ENABLED" if new_value else "DISABLED"
        return True, f"Saved {keys[-1]} = {st_str} (Backup: {os.path.basename(bak_file)})"
    except Exception as e:
        return False, str(e)


if HAS_TEXTUAL:
    THEME_GITHUB_DARK = Theme(
        name="github-dark",
        primary="#58a6ff",
        secondary="#1f6feb",
        warning="#d29922",
        error="#f85149",
        success="#2ea043",
        accent="#f0883e",
        foreground="#c9d1d9",
        background="#0d1117",
        surface="#161b22",
        panel="#21262d",
        dark=True,
    )

    THEME_OLED_BLACK = Theme(
        name="oled-black",
        primary="#ffffff",
        secondary="#cccccc",
        warning="#ffff00",
        error="#ff3333",
        success="#00ff66",
        accent="#ffffff",
        foreground="#ffffff",
        background="#000000",
        surface="#0f0f0f",
        panel="#1c1c1c",
        dark=True,
    )

    THEME_HACKER_GREEN = Theme(
        name="hacker-green",
        primary="#00ff66",
        secondary="#00cc55",
        warning="#ccff00",
        error="#ff3333",
        success="#00ff66",
        accent="#33ff77",
        foreground="#b8ffc9",
        background="#050d06",
        surface="#0a1a0d",
        panel="#112916",
        dark=True,
    )

    CUSTOM_APP_THEMES = [THEME_GITHUB_DARK, THEME_OLED_BLACK, THEME_HACKER_GREEN]

    class DesktopPingModal(ModalScreen):
        CSS = """
        DesktopPingModal {
            align: center middle;
        }
        #ping-box {
            width: 58;
            height: auto;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #ping-url {
            color: $warning;
            margin-bottom: 1;
        }
        #ping-result {
            margin-top: 1;
            margin-bottom: 1;
            text-style: bold;
        }
        .btn-bar {
            margin-top: 1;
            height: 3;
        }
        """
        def __init__(self, url):
            super().__init__()
            self.url = url

        def compose(self) -> ComposeResult:
            with Vertical(id="ping-box"):
                yield Label("[b cyan]⚡ AI ENDPOINT CONNECTIVITY TEST[/b cyan]")
                yield Label(f"Target: {self.url}", id="ping-url")
                yield Label("Pinging server...", id="ping-result")
                with Horizontal(classes="btn-bar"):
                    yield Button("Close Window", id="btn-close", variant="primary")

        def on_mount(self):
            ok, msg = test_ping_endpoint(self.url)
            lbl = self.query_one("#ping-result", Label)
            if ok:
                lbl.update(f"[b green]ONLINE:[/b green] {msg}")
            else:
                lbl.update(f"[b red]OFFLINE:[/b red] {msg}")

        def on_button_pressed(self, event: Button.Pressed):
            self.dismiss()

    class DesktopAddProviderModal(ModalScreen):
        CSS = """
        DesktopAddProviderModal {
            align: center middle;
        }
        #prov-box {
            width: 70;
            height: auto;
            max-height: 90%;
            background: $surface;
            border: round $success;
            padding: 1 2;
        }
        .field-label {
            color: $primary;
            margin-top: 1;
        }
        .btn-bar {
            margin-top: 1;
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """
        def __init__(self, agent_cfg):
            super().__init__()
            self.agent_cfg = agent_cfg

        def compose(self) -> ComposeResult:
            with Vertical(id="prov-box"):
                yield Label(f"[b green]ADD AI PROVIDER TO: {self.agent_cfg['name'].upper()}[/b green]")
                yield Label("Preset / Provider ID (ollama, openrouter, deepseek, groq, custom):", classes="field-label")
                yield Input(placeholder="e.g. ollama", id="in-pid", value="ollama")
                yield Label("Endpoint Base URL:", classes="field-label")
                yield Input(placeholder="http://localhost:11434/v1", id="in-url", value="http://localhost:11434/v1")
                yield Label("API Key / Token (leave blank for local):", classes="field-label")
                yield Input(placeholder="sk-...", id="in-key", password=True)
                yield Label("Default Model Name:", classes="field-label")
                yield Input(placeholder="llama3.3", id="in-model", value="llama3.3")
                with Horizontal(classes="btn-bar"):
                    yield Button("Save & Activate", id="btn-save", variant="success")
                    yield Button("Test Ping", id="btn-test", variant="primary")
                    yield Button("Cancel", id="btn-cancel", variant="default")

        def on_button_pressed(self, event: Button.Pressed):
            bid = event.button.id
            if bid == "btn-cancel":
                self.dismiss(False)
            elif bid == "btn-test":
                url = self.query_one("#in-url", Input).value.strip() or "http://localhost:11434/v1"
                self.app.push_screen(DesktopPingModal(url))
            elif bid == "btn-save":
                pid = self.query_one("#in-pid", Input).value.strip() or "custom"
                url = self.query_one("#in-url", Input).value.strip() or "http://localhost:11434/v1"
                key = self.query_one("#in-key", Input).value.strip()
                mod = self.query_one("#in-model", Input).value.strip() or "custom-model"
                add_agent_provider(self.agent_cfg, pid, pid.title(), url, api_key=key, models_list=[mod])
                set_agent_active_model(self.agent_cfg, mod, provider_id=pid)
                self.dismiss(True)

    class DesktopUniversalDeployModal(ModalScreen):
        CSS = """
        DesktopUniversalDeployModal {
            align: center middle;
        }
        #deploy-box {
            width: 74;
            height: auto;
            max-height: 90%;
            background: $surface;
            border: round $warning;
            padding: 1 2;
        }
        .field-label {
            color: $warning;
            margin-top: 1;
        }
        .btn-bar {
            margin-top: 1;
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """
        def __init__(self, all_agents):
            super().__init__()
            self.all_agents = all_agents

        def compose(self) -> ComposeResult:
            with Vertical(id="deploy-box"):
                yield Label("[b yellow]🌐 UNIVERSAL 1-CLICK PROVIDER DEPLOYMENT[/b yellow]")
                yield Label("Push this provider configuration to ALL detected agents simultaneously.", classes="field-label")
                yield Label("Preset Template (ollama, lmstudio, openrouter, deepseek, groq, openai, custom):", classes="field-label")
                yield Input(placeholder="openrouter", id="in-preset", value="openrouter")
                yield Label("Endpoint Base URL:", classes="field-label")
                yield Input(placeholder="https://openrouter.ai/api/v1", id="in-url", value="https://openrouter.ai/api/v1")
                yield Label("API Key / Token:", classes="field-label")
                yield Input(placeholder="sk-or-...", id="in-key", password=True)
                yield Label("Default Model Name:", classes="field-label")
                yield Input(placeholder="deepseek/deepseek-r1", id="in-model", value="deepseek/deepseek-r1")
                with Horizontal(classes="btn-bar"):
                    yield Button("Deploy to ALL Agents", id="btn-deploy", variant="success")
                    yield Button("Test Ping", id="btn-test", variant="primary")
                    yield Button("Cancel", id="btn-cancel", variant="default")

        def on_button_pressed(self, event: Button.Pressed):
            bid = event.button.id
            if bid == "btn-cancel":
                self.dismiss(False)
            elif bid == "btn-test":
                url = self.query_one("#in-url", Input).value.strip()
                self.app.push_screen(DesktopPingModal(url))
            elif bid == "btn-deploy":
                pk = self.query_one("#in-preset", Input).value.strip() or "custom"
                url = self.query_one("#in-url", Input).value.strip()
                key = self.query_one("#in-key", Input).value.strip()
                mod = self.query_one("#in-model", Input).value.strip()
                dep, fail = universal_deploy_provider(self.all_agents, pk, custom_base=url, custom_key=key, custom_model=mod)
                self.dismiss(len(dep))

    class DesktopThemeModal(ModalScreen):
        CSS = """
        DesktopThemeModal {
            align: center middle;
        }
        #theme-box {
            width: 68;
            height: auto;
            max-height: 85%;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #theme-list {
            height: 12;
            margin-top: 1;
            margin-bottom: 1;
            border: round $panel;
            background: $panel 20%;
        }
        .btn-bar {
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """

        THEMES = [
            ("github-dark", "🐙 GitHub Dark (Deep #0d1117 Black & GitHub Blue)"),
            ("oled-black", "🕶️ OLED Pure Black & White (Monochrome High Contrast)"),
            ("hacker-green", "⚡ Hacker Green (Matrix Cyber Phosphor #00ff66)"),
            ("tokyo-night", "🌃 Tokyo Night (Modern Vibrant Dark Slate)"),
            ("catppuccin-mocha", "🌸 Catppuccin Mocha (Soothing Pastel Charcoal)"),
            ("nord", "❄️ Nord Frost (Clean Arctic Dark Slate)"),
            ("dracula", "🧛 Dracula Dark (Vibrant Purple & Pink Accents)"),
            ("gruvbox", "📦 Gruvbox Dark (Warm Retro Studio Palette)"),
            ("monokai", "🎨 Monokai Classic (High Visibility Accent Palette)"),
        ]

        def compose(self) -> ComposeResult:
            with Vertical(id="theme-box"):
                yield Label("[b cyan]🎨 DESKTOP PALETTE & THEME ENGINE[/b cyan]")
                yield Label("[dim]Select aesthetic style (applies instantly & saves to disk):[/dim]")
                yield OptionList(*[t[1] for t in self.THEMES], id="theme-list")
                with Horizontal(classes="btn-bar"):
                    yield Button("Apply Theme", id="btn-apply", variant="success")
                    yield Button("Cancel", id="btn-cancel", variant="default")

        def on_mount(self):
            curr = getattr(self.app, "theme", "github-dark")
            opt_list = self.query_one("#theme-list", OptionList)
            for idx, (tid, _) in enumerate(self.THEMES):
                if tid == curr:
                    opt_list.highlighted = idx
                    break

        def on_option_list_option_selected(self, event: OptionList.OptionSelected):
            sel_idx = event.option_index
            if 0 <= sel_idx < len(self.THEMES):
                theme_id = self.THEMES[sel_idx][0]
                self.app.theme = theme_id
                save_user_theme(theme_id)
                self.dismiss(theme_id)

        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "btn-cancel":
                self.dismiss(None)
            elif event.button.id == "btn-apply":
                opt_list = self.query_one("#theme-list", OptionList)
                if opt_list.highlighted is not None:
                    theme_id = self.THEMES[opt_list.highlighted][0]
                    self.app.theme = theme_id
                    save_user_theme(theme_id)
                    self.dismiss(theme_id)
                else:
                    self.dismiss(None)


    class DesktopCommandPaletteModal(ModalScreen):
        CSS = """
        DesktopCommandPaletteModal {
            align: center top;
            padding-top: 3;
        }
        #palette-box {
            width: 78;
            height: auto;
            max-height: 80%;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #palette-input {
            margin-bottom: 1;
            border: round $primary;
            background: $surface;
        }
        #palette-list {
            height: 14;
            border: round $panel;
            background: $panel 20%;
        }
        #palette-hint {
            margin-top: 1;
            color: $text-muted;
            text-align: center;
        }
        """

        COMMANDS = [
            ("tab:models", "📑 Go to Tab: 🤖 AI Models & Providers", "tab"),
            ("tab:skills", "📑 Go to Tab: ⚡ Skills Management Hub", "tab"),
            ("tab:mcps", "📑 Go to Tab: 🔌 MCP Tool Servers", "tab"),
            ("tab:presets", "📑 Go to Tab: 🍱 MCP Presets & Workspaces", "tab"),
            ("tab:explorer", "📑 Go to Tab: 📂 20-Category Agent Explorer", "tab"),
            ("tab:global", "📑 Go to Tab: 🌐 Universal Fleet Matrix", "tab"),
            ("preset:fullstack", "🍱 Apply Preset: 🌐 Full-Stack Web (Git, Brave, Puppeteer)", "preset"),
            ("preset:datascience", "🍱 Apply Preset: 📊 Data Science & SQL (Postgres, SQLite, Memory)", "preset"),
            ("preset:devops", "🍱 Apply Preset: 🚀 DevOps & Cloud (Docker, Kubernetes, AWS)", "preset"),
            ("preset:security", "🍱 Apply Preset: 🛡️ Security & Audit (Semgrep, Sentry, Git)", "preset"),
            ("preset:minimal", "🍱 Apply Preset: 🪶 Minimal / Lean (Filesystem only)", "preset"),
            ("preset:all_active", "🍱 Apply Preset: ✨ All Active (Enable All Configured)", "preset"),
            ("preset:broadcast", "⚡ 1-Click Broadcast Active Preset to ALL 11 Agents", "preset_broadcast"),
            ("tool:health", "⚡ Run Live Health Checks on Active MCP Servers", "health"),
            ("tool:registry", "📦 Open 1-Click MCP Registry Auto-Installer", "registry"),
            ("tool:skill_install", "🌐 Install Online Skill (GitHub clone / URL)", "skill_install"),
            ("tool:restore", "↺ 1-Click Restore .bak Configuration Backup", "restore"),
            ("tool:export", "💾 Export Fleet Bundle to omni-profile.json", "export"),
            ("tool:import", "📥 Import Fleet Bundle from omni-profile.json", "import"),
            ("tool:theme", "🎨 Open Desktop Palette & Themes [T]", "theme"),
            ("tool:ping", "⚡ Ping Test Active Model API Endpoint [P]", "ping"),
            ("tool:refresh", "🔄 Refresh All Runtimes and Disk Data [R]", "refresh"),
            ("ag:antigravity", "🟢 Switch to Agent: Google Antigravity", "agent"),
            ("ag:claude", "🟣 Switch to Agent: Claude Code CLI & Desktop", "agent"),
            ("ag:cursor", "⚪ Switch to Agent: Cursor IDE", "agent"),
            ("ag:opencode", "🔵 Switch to Agent: OpenCode AI Desktop & CLI", "agent"),
            ("ag:hermes", "🟡 Switch to Agent: Nous Hermes Agent", "agent"),
            ("ag:codex", "🟠 Switch to Agent: OpenAI Codex Agent", "agent"),
            ("ag:cline", "🟢 Switch to Agent: VS Code & Cline", "agent"),
            ("ag:pi", "⚪ Switch to Agent: Pi Coding Agent", "agent"),
            ("ag:copilot", "⚪ Switch to Agent: GitHub Copilot CLI", "agent"),
            ("ag:kiro", "⚪ Switch to Agent: Kiro Agent", "agent"),
            ("ag:kilo", "⚪ Switch to Agent: Kilo Agent", "agent"),
        ]

        def compose(self) -> ComposeResult:
            with Vertical(id="palette-box"):
                yield Label("[b cyan]⚡ FUZZY COMMAND PALETTE[/b cyan]  [dim](LazyGit / VS Code pattern)[/dim]")
                yield Input(placeholder="🔍 Type to search commands, tabs, presets, tools, or agents...", id="palette-input")
                yield OptionList(id="palette-list")
                yield Label("[dim]↑/↓ Navigate  •  Enter Execute  •  Esc Close[/dim]", id="palette-hint")

        def on_mount(self):
            self.filter_commands("")
            self.query_one("#palette-input", Input).focus()

        def on_input_changed(self, event: Input.Changed):
            self.filter_commands(event.value.strip().lower())

        def filter_commands(self, q: str):
            opt_list = self.query_one("#palette-list", OptionList)
            opt_list.clear_options()
            self.current_filtered = []
            for cid, label, ctype in self.COMMANDS:
                if not q or q in label.lower() or q in cid.lower():
                    opt_list.add_option(label)
                    self.current_filtered.append((cid, label, ctype))

        def on_option_list_option_selected(self, event: OptionList.OptionSelected):
            idx = event.option_index
            if 0 <= idx < len(self.current_filtered):
                cmd_item = self.current_filtered[idx]
                self.dismiss(cmd_item)

    class DesktopRegistryModal(ModalScreen):
        CSS = """
        DesktopRegistryModal {
            align: center middle;
        }
        #reg-box {
            width: 88;
            height: auto;
            max-height: 85%;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #reg-table {
            height: 11;
            margin-top: 1;
            margin-bottom: 1;
            border: round $panel;
            background: $surface;
        }
        #reg-env-input {
            margin-bottom: 1;
            border: round $primary;
            background: $surface;
        }
        .btn-bar {
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """

        def __init__(self, target_agent, all_agents):
            super().__init__()
            self.target_agent = target_agent
            self.all_agents = all_agents

        def compose(self) -> ComposeResult:
            with Vertical(id="reg-box"):
                yield Label("[b cyan]📦 1-CLICK MCP REGISTRY AUTO-INSTALLER[/b cyan]")
                yield Label(f"[dim]Install verified MCP servers to [b]{self.target_agent['name']}[/b] or fleet-wide:[/dim]")
                yield DataTable(id="reg-table")
                yield Input(placeholder="🔑 Env Var / Param (e.g. GITHUB_TOKEN or BRAVE_API_KEY if needed)...", id="reg-env-input")
                with Horizontal(classes="btn-bar"):
                    yield Button("Install to Active Agent", id="btn-reg-active", variant="success")
                    yield Button("⚡ Install to ALL 11 Agents", id="btn-reg-all", variant="primary")
                    yield Button("Cancel", id="btn-reg-cancel", variant="default")

        def on_mount(self):
            table = self.query_one("#reg-table", DataTable)
            table.clear(columns=True)
            table.add_columns("Category", "Server Name", "Package / Command", "Description")
            table.cursor_type = "row"
            for idx, item in enumerate(REGISTRY_MCPS):
                table.add_row(item["category"], item["name"], f"{item['command']} {' '.join(item['args'][:2])}", item["desc"][:42], key=f"r-{idx}")

        def on_button_pressed(self, event: Button.Pressed):
            bid = event.button.id
            if bid == "btn-reg-cancel":
                self.dismiss(None)
                return

            table = self.query_one("#reg-table", DataTable)
            if table.cursor_row is None or not (0 <= table.cursor_row < len(REGISTRY_MCPS)):
                self.dismiss(None)
                return

            mcp_def = REGISTRY_MCPS[table.cursor_row]
            env_val = self.query_one("#reg-env-input", Input).value.strip()
            env_map = {}
            if mcp_def.get("env_vars") and env_val:
                for ev in mcp_def["env_vars"]:
                    env_map[ev] = env_val

            targets = list(self.all_agents.values()) if bid == "btn-reg-all" else [self.target_agent]
            ok, msg = install_registry_mcp(mcp_def, env_map, targets)
            self.dismiss((ok, msg))

    class DesktopRestoreModal(ModalScreen):
        CSS = """
        DesktopRestoreModal {
            align: center middle;
        }
        #res-box {
            width: 82;
            height: auto;
            max-height: 85%;
            background: $surface;
            border: round $error;
            padding: 1 2;
        }
        #res-table {
            height: 11;
            margin-top: 1;
            margin-bottom: 1;
            border: round $panel;
            background: $surface;
        }
        .btn-bar {
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """

        def __init__(self, target_agent):
            super().__init__()
            self.target_agent = target_agent
            self.backups = list_agent_backups(target_agent)

        def compose(self) -> ComposeResult:
            with Vertical(id="res-box"):
                yield Label(f"[b red]↺ CONFIG BACKUP ROLLBACK MANAGER[/b red] - [b]{self.target_agent['name']}[/b]")
                yield Label("[dim]Select a historical timestamped snapshot to restore immediately:[/dim]")
                yield DataTable(id="res-table")
                with Horizontal(classes="btn-bar"):
                    yield Button("↺ Restore Selected Backup", id="btn-do-restore", variant="error")
                    yield Button("Cancel", id="btn-res-cancel", variant="default")

        def on_mount(self):
            table = self.query_one("#res-table", DataTable)
            table.clear(columns=True)
            table.add_columns("Backup File", "Timestamp", "Size", "Directory")
            table.cursor_type = "row"
            for idx, b in enumerate(self.backups):
                sz_str = f"{b['size_bytes']} B" if b['size_bytes'] < 1024 else f"{b['size_bytes']//1024} KB"
                table.add_row(b["name"][:30], b["mtime"], sz_str, b["dir"][-28:], key=f"b-{idx}")

        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "btn-res-cancel":
                self.dismiss(None)
                return
            elif event.button.id == "btn-do-restore":
                table = self.query_one("#res-table", DataTable)
                if table.cursor_row is not None and 0 <= table.cursor_row < len(self.backups):
                    b = self.backups[table.cursor_row]
                    ok, msg = restore_backup_file(b["path"])
                    self.dismiss((ok, msg))
                else:
                    self.dismiss(None)

    class DesktopSkillInstallModal(ModalScreen):
        CSS = """
        DesktopSkillInstallModal {
            align: center middle;
        }
        #skill-box {
            width: 74;
            height: auto;
            max-height: 85%;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #skill-url-input {
            margin-top: 1;
            margin-bottom: 1;
            border: round $primary;
            background: $surface;
        }
        .btn-bar {
            height: 3;
        }
        .btn-bar Button {
            margin-right: 1;
        }
        """

        def __init__(self, target_agent):
            super().__init__()
            self.target_agent = target_agent

        def compose(self) -> ComposeResult:
            with Vertical(id="skill-box"):
                yield Label(f"[b green]🌐 ONLINE SKILL & PLUGIN AUTO-INSTALLER[/b green]")
                yield Label(f"[dim]Install skill into [b]{self.target_agent['name']}[/b]:[/dim]")
                yield Input(placeholder="🔗 GitHub URL (e.g. https://github.com/org/skill) or raw SKILL.md URL...", id="skill-url-input")
                with Horizontal(classes="btn-bar"):
                    yield Button("Git Clone Skill", id="btn-skill-git", variant="success")
                    yield Button("Download SKILL.md", id="btn-skill-url", variant="primary")
                    yield Button("Cancel", id="btn-skill-cancel", variant="default")

        def on_button_pressed(self, event: Button.Pressed):
            bid = event.button.id
            if bid == "btn-skill-cancel":
                self.dismiss(None)
                return
            val = self.query_one("#skill-url-input", Input).value.strip()
            if not val:
                self.dismiss((False, "Empty URL provided"))
                return

            stype = "git" if bid == "btn-skill-git" else "url"
            ok, msg = install_online_skill(stype, val, self.target_agent)
            self.dismiss((ok, msg))

    class DesktopToolInspectorModal(ModalScreen):
        CSS = """
        DesktopToolInspectorModal {
            align: center middle;
        }
        #inspector-box {
            width: 100;
            height: 38;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #inspector-header {
            text-style: bold;
            color: $accent;
            margin-bottom: 0;
        }
        #inspector-subhead {
            margin-bottom: 1;
        }
        #table-tools {
            height: 14;
            margin-bottom: 1;
        }
        #tool-runner-box {
            height: 13;
            border: solid $panel;
            padding: 0 1;
            margin-bottom: 1;
        }
        #lbl-tool-output {
            height: 5;
            background: $background;
            padding: 0 1;
            overflow-y: auto;
        }
        .btn-bar {
            height: 3;
            margin-top: 1;
        }
        """
        def __init__(self, agent_cfg, server_name, server_def):
            super().__init__()
            self.agent_cfg = agent_cfg
            self.server_name = server_name
            self.server_def = server_def
            self.tools = []
            self.trimmed_set = get_trimmed_subtools(self.agent_cfg.get("id", "agent"), self.server_name)

        def compose(self) -> ComposeResult:
            with Vertical(id="inspector-box"):
                yield Label(f"[b cyan]🔍 MCP TOOL RUNNER & SCHEMA INSPECTOR[/b cyan] — [bold green]{self.server_name}[/bold green]", id="inspector-header")
                cmd_txt = f"{self.server_def.get('command')} {' '.join(self.server_def.get('args', []))[:60]}"
                yield Label(f"[dim]Command:[/dim] {cmd_txt}", id="inspector-subhead")
                yield DataTable(id="table-tools")
                with Vertical(id="tool-runner-box"):
                    yield Label("[b yellow]⚡ Direct Tool Call Tester (Zero LLM Tokens)[/b yellow]")
                    with Horizontal():
                        yield Input(placeholder='JSON arguments, e.g. {"query": "test"} or empty {}', id="input-tool-args")
                        yield Button("▶ Run Tool Call", id="btn-run-tool", variant="success")
                    yield Static("[dim]Output will appear here after execution...[/dim]", id="lbl-tool-output")
                with Horizontal(classes="btn-bar"):
                    yield Button("⇄ Toggle Trim Tool [Space]", id="btn-toggle-trim", variant="warning")
                    yield Button("🔄 Re-query Tools", id="btn-requery-tools", variant="default")
                    yield Button("Close [Esc]", id="btn-close-inspector", variant="error")

        def on_mount(self):
            t_table = self.query_one("#table-tools", DataTable)
            t_table.add_columns("Status", "Tool Name", "Parameters", "Description")
            t_table.cursor_type = "row"
            self.load_tools()

        def load_tools(self):
            t_table = self.query_one("#table-tools", DataTable)
            t_table.clear()
            self.trimmed_set = get_trimmed_subtools(self.agent_cfg.get("id", "agent"), self.server_name)
            ok, res = query_mcp_tools(self.server_name, self.server_def, timeout=4.0)
            if ok and isinstance(res, list):
                self.tools = res
                for idx, t in enumerate(self.tools):
                    t_name = t.get("name", "unknown")
                    is_trimmed = (t_name in self.trimmed_set)
                    st = "[dim red]○ TRIMMED[/dim red]" if is_trimmed else "[bold green]● ENABLED[/bold green]"
                    params = t.get("inputSchema", {}).get("properties", {})
                    param_desc = f"{len(params)} fields ({', '.join(list(params.keys())[:3])})" if params else "None"
                    desc = (t.get("description") or "No description").replace("\n", " ")[:45]
                    t_table.add_row(st, t_name, param_desc, desc, key=f"t-{idx}")
            else:
                self.tools = []
                err = str(res)
                t_table.add_row("[dim]Error[/dim]", "Query Failed", "0", err[:50])

        def action_toggle_trim_selected(self):
            t_table = self.query_one("#table-tools", DataTable)
            if t_table.cursor_row is not None and 0 <= t_table.cursor_row < len(self.tools):
                t_item = self.tools[t_table.cursor_row]
                t_name = t_item.get("name")
                if t_name:
                    ok, msg = toggle_trimmed_subtool(self.agent_cfg.get("id", "agent"), self.server_name, t_name, agent_cfg=self.agent_cfg)
                    self.load_tools()
                    self.notify(msg, title="Sub-Tool Context Trimmer", severity="information" if ok else "error")

        def action_run_selected_tool(self):
            t_table = self.query_one("#table-tools", DataTable)
            if t_table.cursor_row is not None and 0 <= t_table.cursor_row < len(self.tools):
                t_item = self.tools[t_table.cursor_row]
                t_name = t_item.get("name")
                raw_args = self.query_one("#input-tool-args", Input).value.strip()
                args_dict = {}
                if raw_args:
                    try:
                        args_dict = json.loads(raw_args)
                    except Exception as je:
                        self.notify(f"Invalid JSON arguments: {je}", title="JSON Error", severity="error")
                        return
                self.query_one("#lbl-tool-output", Static).update(f"[yellow]Executing {t_name} with params: {args_dict}...[/yellow]")
                ok, res = execute_mcp_tool(self.server_name, self.server_def, t_name, arguments=args_dict, timeout=6.0)
                if ok:
                    out_text = f"[bold green]✔ SUCCESS (Zero LLM Tokens):[/bold green]\n{res[:800]}"
                else:
                    out_text = f"[bold red]✖ ERROR:[/bold red]\n{res[:800]}"
                self.query_one("#lbl-tool-output", Static).update(out_text)

        def on_key(self, event):
            if event.key == "space":
                event.prevent_default()
                self.action_toggle_trim_selected()
            elif event.key == "escape":
                event.prevent_default()
                self.dismiss(None)

        def on_data_table_row_selected(self, event: DataTable.RowSelected):
            self.action_toggle_trim_selected()

        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "btn-toggle-trim":
                self.action_toggle_trim_selected()
            elif event.button.id == "btn-run-tool":
                self.action_run_selected_tool()
            elif event.button.id == "btn-requery-tools":
                self.load_tools()
            elif event.button.id == "btn-close-inspector":
                self.dismiss(None)

    class DesktopProcessRadarModal(ModalScreen):
        CSS = """
        DesktopProcessRadarModal {
            align: center middle;
        }
        #radar-box {
            width: 96;
            height: 36;
            background: $surface;
            border: round $primary;
            padding: 1 2;
        }
        #radar-header {
            text-style: bold;
            color: $accent;
            margin-bottom: 1;
        }
        #table-engines {
            height: 8;
            margin-bottom: 1;
        }
        #table-procs {
            height: 14;
            margin-bottom: 1;
        }
        .btn-bar {
            height: 3;
            margin-top: 1;
        }
        """
        def compose(self) -> ComposeResult:
            with Vertical(id="radar-box"):
                yield Label("[b cyan]📡 FLEET PROCESS & LOCAL ENGINE RADAR[/b cyan]", id="radar-header")
                yield Label("[b yellow]Local AI Inference Engines (Listening Ports):[/b yellow]")
                yield DataTable(id="table-engines")
                yield Label("[b green]Active Coding Agent Processes (psutil Live Monitor):[/b green]")
                yield DataTable(id="table-procs")
                with Horizontal(classes="btn-bar"):
                    yield Button("🔄 Rescan Fleet Now", id="btn-rescan-radar", variant="primary")
                    yield Button("Close [Esc]", id="btn-close-radar", variant="error")

        def on_mount(self):
            e_table = self.query_one("#table-engines", DataTable)
            e_table.add_columns("Engine Name", "Port", "Status", "Readiness")
            e_table.cursor_type = "row"

            p_table = self.query_one("#table-procs", DataTable)
            p_table.add_columns("PID", "Agent Affinity", "Process Name", "CPU %", "RAM (RSS)")
            p_table.cursor_type = "row"

            self.load_radar()

        def load_radar(self):
            res = scan_fleet_processes()
            e_table = self.query_one("#table-engines", DataTable)
            e_table.clear()
            for idx, eng in enumerate(res["engines"]):
                st = "[bold green]● ONLINE[/bold green]" if eng["online"] else "[dim red]○ OFFLINE[/dim red]"
                lat = "[green]Ready for local inference[/green]" if eng["online"] else "[dim]No listener detected[/dim]"
                e_table.add_row(eng["name"], str(eng["port"]), st, lat, key=f"e-{idx}")

            p_table = self.query_one("#table-procs", DataTable)
            p_table.clear()
            procs = res["processes"]
            if procs:
                for idx, p in enumerate(procs):
                    aff = f"[bold cyan]{p['agent_kw'].upper()}[/bold cyan]"
                    cpu_s = f"{p['cpu']:.1f}%"
                    ram_s = f"{p['mem_mb']:,} MB"
                    p_table.add_row(str(p["pid"]), aff, p["name"], cpu_s, ram_s, key=f"p-{idx}")
            else:
                p_table.add_row("—", "None", "No active agent processes detected in memory", "0.0%", "0 MB")

        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "btn-rescan-radar":
                self.load_radar()
                self.notify("Fleet radar rescanned successfully!", title="Radar Updated")
            elif event.button.id == "btn-close-radar":
                self.dismiss(None)

        def on_key(self, event):
            if event.key == "escape":
                event.prevent_default()
                self.dismiss(None)

    class AgentCustomizerDesktopApp(App):
        TITLE = "OmniAgent Manager"
        SUB_TITLE = "Universal AI Coding Agent Control Hub v4.0"
        CSS = """
        Screen {
            background: $background;
            color: $foreground;
        }
        #app-layout {
            height: 1fr;
        }
        #sidebar {
            width: 33;
            background: $surface;
            border-right: heavy $panel;
            padding: 0 1;
        }
        #sidebar-header {
            text-align: center;
            color: $primary;
            text-style: bold;
            margin-top: 1;
            margin-bottom: 1;
            border-bottom: solid $panel;
            padding-bottom: 1;
        }
        .agent-item {
            width: 100%;
            margin-bottom: 1;
            background: transparent;
            color: $foreground;
            border: none;
            text-align: left;
            padding: 0 1;
        }
        .agent-item:hover {
            background: $primary 20%;
            color: $primary;
        }
        .agent-item-active {
            background: $primary 25%;
            color: $primary;
            border-left: thick $primary;
            text-style: bold;
        }
        #sidebar-footer {
            margin-top: 1;
            border-top: solid $panel;
            padding-top: 1;
        }
        #sidebar-footer Button {
            width: 100%;
            margin-bottom: 1;
            border: none;
        }
        #workspace {
            width: 1fr;
            padding: 0 1;
            background: $background;
        }
        #lbl-token-gauge {
            background: $surface;
            border: round $primary 40%;
            padding: 0 1;
            margin-bottom: 1;
            height: 3;
            content-align: center middle;
        }
        .desktop-card {
            background: $surface;
            border: round $primary 40%;
            padding: 1 2;
            margin-bottom: 1;
        }
        .action-bar {
            height: 3;
            margin-bottom: 1;
        }
        .action-bar Button {
            margin-right: 1;
            border: none;
        }
        #skills-filter {
            margin-bottom: 1;
            border: round $primary;
            background: $surface;
        }
        #sel-explorer-cat {
            width: 42;
            margin-right: 1;
            background: $surface;
            border: round $primary;
        }
        DataTable {
            height: 1fr;
            border: round $panel;
            background: $surface;
        }
        DataTable > .datatable--cursor {
            background: $primary 30%;
            color: $foreground;
            text-style: bold;
        }
        Button {
            border: none;
            min-width: 12;
            height: 3;
            padding: 0 1;
        }
        """

        BINDINGS = [
            Binding("ctrl+p", "open_command_palette", "Palette [Ctrl+P]", show=True),
            Binding("f1", "open_command_palette", "Palette", show=False),
            Binding("w", "open_presets_tab", "Workspaces [W]", show=True),
            Binding("m", "open_models_tab", "Models", show=True),
            Binding("s", "open_skills_tab", "Skills", show=True),
            Binding("c", "open_mcps_tab", "MCPs", show=True),
            Binding("i", "open_tool_inspector", "Inspect Tools [I]", show=True),
            Binding("o", "open_fleet_radar", "Radar [O]", show=True),
            Binding("g", "open_features_tab", "Config Flags [G]", show=True),
            Binding("f", "open_explorer_tab", "Folders", show=True),
            Binding("t", "open_theme_modal", "Themes [T]", show=True),
            Binding("p", "ping_active", "Ping Test", show=True),
            Binding("r", "refresh_data", "Refresh", show=True),
            Binding("ctrl+r", "open_restore_modal", "Restore .bak", show=False),
            Binding("q", "quit", "Quit", show=True),
        ]

        def __init__(self):
            super().__init__()
            self.agents = discover_installed_agents()
            self.agent_keys = list(self.agents.keys())
            self.selected_key = self.agent_keys[0] if self.agent_keys else "antigravity"
            self.cached_skills = []
            self.active_explorer_cat = "1"
            self.mcp_health_cache = {}
            self.cached_features = []

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with Horizontal(id="app-layout"):
                with Vertical(id="sidebar"):
                    yield Label("AI CODING AGENTS", id="sidebar-header")
                    with VerticalScroll(id="agent-scroll"):
                        for k in self.agent_keys:
                            ag = self.agents[k]
                            cls = "agent-item agent-item-active" if k == self.selected_key else "agent-item"
                            yield Button(f"● {ag['name'][:18]}", id=f"ag-{k}", classes=cls)
                    with Vertical(id="sidebar-footer"):
                        yield Button("⚡ Command Palette [Ctrl+P]", id="btn-side-palette", variant="success")
                        yield Button("📡 Fleet Process Radar [O]", id="btn-side-radar", variant="primary")
                        yield Button("⚙️ Config Feature Flags [G]", id="btn-side-features", variant="default")
                        yield Button("🎨 Switch Theme [T]", id="btn-side-theme", variant="default")
                        yield Button("📂 Explore Agent Folders", id="btn-side-folders", variant="primary")
                        yield Button("🌐 1-Click Deploy Provider", id="btn-side-deploy", variant="warning")
                        yield Button("💾 Export omni-profile.json", id="btn-side-export", variant="default")
                        yield Button("📥 Import omni-profile.json", id="btn-side-import", variant="default")
                        yield Button("🔄 Refresh All Runtimes", id="btn-side-refresh", variant="default")

                with Vertical(id="workspace"):
                    yield Label("[dim]Calculating tool context overhead...[/dim]", id="lbl-token-gauge")
                    with TabbedContent(id="tabs-main"):
                        with TabPane("🤖 AI Models & Providers", id="pane-models"):
                            with Vertical(classes="desktop-card", id="card-models"):
                                yield Label("[b green]ACTIVE MODEL:[/b green] Loading...", id="lbl-active-model")
                                yield Label("[b cyan]PROVIDER:[/b cyan] Loading...", id="lbl-active-prov")
                                yield Label("[b yellow]ENDPOINT:[/b yellow] Loading...", id="lbl-active-url")
                            with Horizontal(classes="action-bar"):
                                yield Button("+ Add Provider", id="btn-add-provider", variant="success")
                                yield Button("⚡ Ping Test", id="btn-ping-test", variant="primary")
                                yield Button("Set Active Model", id="btn-set-active", variant="default")
                                yield Button("Toggle ON/OFF", id="btn-toggle-model", variant="default")
                            yield DataTable(id="table-models")

                        with TabPane("⚡ Skills Management", id="pane-skills"):
                            yield Input(placeholder="🔍 Type to filter skills in real time...", id="skills-filter")
                            with Horizontal(classes="action-bar"):
                                yield Button("⇄ Toggle Selected [Space]", id="btn-skill-toggle", variant="primary")
                                yield Button("✔ Activate All", id="btn-skill-all", variant="success")
                                yield Button("✖ Stash All", id="btn-skill-none", variant="error")
                                yield Button("🌐 Install Online Skill", id="btn-online-skill", variant="warning")
                                yield Button("📦 Warehouses", id="btn-warehouses", variant="default")
                            yield DataTable(id="table-skills")

                        with TabPane("🔌 MCP Tool Servers", id="pane-mcps"):
                            with Horizontal(classes="action-bar"):
                                yield Button("⇄ Toggle Selected [Space]", id="btn-toggle-mcp", variant="primary")
                                yield Button("🔍 Inspect & Trim Tools [I]", id="btn-inspect-tools", variant="warning")
                                yield Button("⚡ Run Health Checks", id="btn-health-check", variant="default")
                                yield Button("📦 1-Click Registry", id="btn-open-registry", variant="success")
                                yield Button("↺ Restore .bak", id="btn-restore-bak", variant="error")
                                yield Button("+ Add MCP Server", id="btn-add-mcp", variant="default")
                            yield DataTable(id="table-mcps")

                        with TabPane("⚙️ Config Feature Flags", id="pane-features"):
                            with Vertical(classes="desktop-card"):
                                yield Label("[b cyan]⚙️ Universal Agent Config JSON Feature Switchboard[/b cyan]")
                                yield Label("[dim]Discover, search, and toggle all boolean settings across config files. Changes automatically generate timestamped .bak backups.[/dim]")
                            yield Input(placeholder="🔍 Type to filter settings and feature flags in real time...", id="features-filter")
                            with Horizontal(classes="action-bar"):
                                yield Button("⇄ Toggle Selected [Space]", id="btn-toggle-feature", variant="primary")
                                yield Button("↺ Restore .bak", id="btn-restore-feature-bak", variant="error")
                                yield Button("🔄 Reload Flags", id="btn-reload-features", variant="default")
                            yield DataTable(id="table-features")

                        with TabPane("🍱 MCP Presets & Workspaces", id="pane-presets"):
                            with Vertical(classes="desktop-card"):
                                yield Label("[b cyan]🍱 Task-Based MCP Workspaces & Fleet Synchronization[/b cyan]")
                                yield Label("[dim]Switch active tool profiles across the selected agent or broadcast across all 11 agents simultaneously[/dim]")
                            with Horizontal(classes="action-bar"):
                                yield Button("Apply to Active Agent", id="btn-apply-preset", variant="primary")
                                yield Button("⚡ 1-Click Broadcast All 11 Agents", id="btn-broadcast-preset", variant="success")
                            yield DataTable(id="table-presets")

                        with TabPane("📂 Agent Explorer", id="pane-explorer"):
                            with Horizontal(classes="action-bar"):
                                yield Select(options=[], id="sel-explorer-cat", prompt="Choose Category...")
                                yield Button("📁 Explorer", id="btn-exp-explorer", variant="success")
                                yield Button("📝 Editor", id="btn-exp-editor", variant="primary")
                                yield Button("📋 Copy Path", id="btn-exp-copy", variant="default")
                                yield Button("💻 Terminal", id="btn-exp-terminal", variant="warning")
                            yield DataTable(id="table-explorer")

                        with TabPane("🌐 Universal Matrix", id="pane-global"):
                            with Vertical(classes="desktop-card"):
                                yield Label("[b cyan]Universal Multi-Agent Deployment Hub[/b cyan]")
                                yield Label("[dim]View and sync models, providers, and skills across all installed coding agents[/dim]")
                            with Horizontal(classes="action-bar"):
                                yield Button("1-Click Broadcast Provider to ALL", id="btn-broadcast-prov", variant="success")
                            yield DataTable(id="table-global")
            yield Footer()

        def on_mount(self):
            # Register modern custom themes
            for th in CUSTOM_APP_THEMES:
                try:
                    self.register_theme(th)
                except Exception:
                    pass
            # Load user saved theme
            user_theme = load_user_theme()
            if user_theme in self.available_themes:
                self.theme = user_theme

            self.load_active_agent_data()
            self.load_global_matrix()
            self.init_explorer_categories()

        def on_resize(self, event: events.Resize) -> None:
            try:
                sidebar = self.query_one("#sidebar")
                if event.size.width < 95:
                    sidebar.styles.width = 10
                    for k in self.agent_keys:
                        btn = self.query_one(f"#ag-{k}", Button)
                        btn.label = f"● {k[:3].upper()}"
                else:
                    sidebar.styles.width = 33
                    for k in self.agent_keys:
                        btn = self.query_one(f"#ag-{k}", Button)
                        name = self.agents[k]["name"][:18]
                        btn.label = f"● {name}"
            except Exception:
                pass

        def load_active_agent_data(self):
            ag = self.agents.get(self.selected_key)
            if not ag: return

            # 0. Live Token & Cost Context Overhead Gauge
            try:
                tm = calculate_agent_tools_token_metrics(ag)
                trim_txt = f"  [b magenta]Trimmed:[/b magenta] {tm.get('trimmed_count', 0)} tools (-{tm.get('saved_tokens', 0):,} tok)" if tm.get('trimmed_count', 0) > 0 else ""
                self.query_one("#lbl-token-gauge", Label).update(
                    f"[b green]Tools Context Overhead:[/b green] {tm['tokens']:,} tokens ({tm['pct_used']:.1f}% of 128k)  "
                    f"[{tm['bar']}]  [b cyan]Headroom:[/b cyan] {tm['headroom']:,} tokens free{trim_txt}  "
                    f"[b yellow]Est. Cost:[/b yellow] ~${tm['cost_claude']:.4f}/req (Claude 3.5) | ~${tm['cost_deepseek']:.5f}/req (DeepSeek)"
                )
            except Exception:
                pass

            # 1. Update Models Tab
            m_info = get_agent_models_and_providers(ag)
            self.query_one("#lbl-active-model", Label).update(f"[b green]ACTIVE MODEL:[/b green]  [b]{m_info['active_model']}[/b]")
            self.query_one("#lbl-active-prov", Label).update(f"[b cyan]PROVIDER:[/b cyan]      {m_info['active_provider']}")
            key_st = "[green]Configured[/green]" if m_info["has_key"] else "[dim]None / Local[/dim]"
            self.query_one("#lbl-active-url", Label).update(f"[b yellow]ENDPOINT:[/b yellow]      {m_info['base_url']}  |  [b]Key:[/b] {key_st}")

            saved_m_row = None
            try:
                m_table = self.query_one("#table-models", DataTable)
                saved_m_row = m_table.cursor_row
            except Exception:
                pass

            m_table = self.query_one("#table-models", DataTable)
            m_table.clear(columns=True)
            m_table.add_columns("Status", "Model Identifier", "Provider Type", "Context / Tier")
            m_table.cursor_type = "row"

            for idx, m in enumerate(m_info["models"]):
                if m.get("is_active"):
                    badge = "[bold #a6e3a1]  ● ACTIVE [ON]   [/bold #a6e3a1]"
                elif m.get("is_enabled", True):
                    badge = "[bold #89b4fa]  [✓] ENABLED     [/bold #89b4fa]"
                else:
                    badge = "[dim #6c7086]  [ ] DISABLED    [/dim #6c7086]"
                m_table.add_row(badge, m["id"], m.get("provider", "native"), m.get("name", ""), key=f"m-{idx}")

            if saved_m_row is not None and m_table.row_count > 0:
                m_table.move_cursor(row=min(saved_m_row, m_table.row_count - 1), scroll=False)

            # 2. Update Skills Tab (Large Modern Badges & Cursor Preservation)
            act_s, av_s = get_agent_skills(ag)
            all_s = sorted(list(set(act_s).union(set(av_s))))
            self.cached_skills = all_s
            self.populate_skills_table()

            # 3. Update MCPs Tab (Cursor Preservation & Inline Toggle Action)
            saved_mcp_row = None
            try:
                mcp_table = self.query_one("#table-mcps", DataTable)
                saved_mcp_row = mcp_table.cursor_row
            except Exception:
                pass

            act_m, dis_m = read_mcp_config(ag)
            mcp_table = self.query_one("#table-mcps", DataTable)
            mcp_table.clear(columns=True)
            mcp_table.add_columns("Status", "Server Name", "Health / Latency", "Command / Protocol", "Quick Action")
            mcp_table.cursor_type = "row"
            sorted_mcps = sorted(list(set(act_m.keys()).union(set(dis_m.keys()))))
            for idx, m in enumerate(sorted_mcps):
                health_info = self.mcp_health_cache.get(m)
                if health_info:
                    h_ok, h_ms, h_msg = health_info
                    h_badge = f"[bold #a6e3a1]● LIVE ({h_ms}ms)[/bold #a6e3a1]" if h_ok else f"[bold #fab387]⚠ {h_msg[:12]}[/bold #fab387]"
                else:
                    h_badge = "[dim]— Unchecked[/dim]"

                if m in act_m:
                    st = "[bold #a6e3a1]  ● ACTIVE [ON]   [/bold #a6e3a1]"
                    act_text = "[bold #89b4fa] [ ⇄ Click / Space ] [/bold #89b4fa]"
                else:
                    st = "[dim #6c7086]  ○ DISABLED [OFF] [/dim #6c7086]"
                    act_text = "[bold #a6e3a1] [ ⇄ Click / Space ] [/bold #a6e3a1]"
                mcp_table.add_row(st, m, h_badge, "Stdio / SSE", act_text, key=f"mcp-{idx}")

            # Populate MCP Presets Table
            try:
                p_table = self.query_one("#table-presets", DataTable)
                p_table.clear(columns=True)
                p_table.add_columns("Preset Name", "Target Tools / Matchers", "Description", "Quick Action")
                p_table.cursor_type = "row"
                for p_idx, pr in enumerate(MCP_PRESETS):
                    p_table.add_row(
                        f"[b]{pr['name']}[/b]",
                        ", ".join(pr["match"]),
                        pr["desc"],
                        "[bold #a6e3a1] [ Apply / Space ] [/bold #a6e3a1]",
                        key=f"preset-{p_idx}"
                    )
            except Exception:
                pass

            if saved_mcp_row is not None and mcp_table.row_count > 0:
                mcp_table.move_cursor(row=min(saved_mcp_row, mcp_table.row_count - 1), scroll=False)
            
            # 4. Populate Config Feature Flags
            self.populate_features_table()

        def populate_features_table(self):
            ag = self.agents.get(self.selected_key)
            if not ag: return

            saved_f_row = None
            try:
                f_table = self.query_one("#table-features", DataTable)
                saved_f_row = f_table.cursor_row
            except Exception:
                return

            f_table.clear(columns=True)
            f_table.add_columns("Status", "Setting Path (Key)", "Config File", "Section", "Quick Action")
            f_table.cursor_type = "row"

            flags = extract_agent_config_flags(ag)
            self.cached_features = flags

            q = ""
            try:
                q = self.query_one("#features-filter", Input).value.strip().lower()
            except Exception:
                pass

            filtered = [f for f in flags if (q in f["key"].lower() or q in f["section"].lower() or q in f["filename"].lower())] if q else flags

            for idx, fl in enumerate(filtered):
                if fl["value"]:
                    st = "[bold #a6e3a1]  ● ENABLED [ON]   [/bold #a6e3a1]"
                    act = "[bold #89b4fa] [ ⇄ Click / Space ] [/bold #89b4fa]"
                else:
                    st = "[dim #6c7086]  ○ DISABLED [OFF] [/dim #6c7086]"
                    act = "[bold #a6e3a1] [ ⇄ Click / Space ] [/bold #a6e3a1]"
                f_table.add_row(st, fl["key"], fl["filename"], fl["section"], act, key=f"feat-{idx}")

            if saved_f_row is not None and f_table.row_count > 0:
                f_table.move_cursor(row=min(saved_f_row, f_table.row_count - 1), scroll=False)

        def action_toggle_config_feature(self):
            f_table = self.query_one("#table-features", DataTable)
            if f_table.cursor_row is not None and f_table.row_count > 0:
                saved_row = f_table.cursor_row
                q = ""
                try:
                    q = self.query_one("#features-filter", Input).value.strip().lower()
                except Exception:
                    pass
                filtered = [f for f in self.cached_features if (q in f["key"].lower() or q in f["section"].lower() or q in f["filename"].lower())] if q else self.cached_features
                if 0 <= saved_row < len(filtered):
                    item = filtered[saved_row]
                    new_val = not item["value"]
                    ok, msg = set_agent_config_flag(item["file"], item["key"], new_val)
                    self.populate_features_table()
                    if f_table.row_count > 0:
                        f_table.move_cursor(row=min(saved_row, f_table.row_count - 1), scroll=False)
                    self.notify(msg, title="Feature Flag Updated" if ok else "Update Failed", severity="information" if ok else "error")

        def action_open_tool_inspector(self):
            ag = self.agents.get(self.selected_key)
            if not ag: return
            act_m, dis_m = read_mcp_config(ag)
            sorted_mcps = sorted(list(set(act_m.keys()).union(set(dis_m.keys()))))
            if not sorted_mcps:
                self.notify("No MCP servers configured for active agent", title="Tool Inspector", severity="warning")
                return
            mcp_table = self.query_one("#table-mcps", DataTable)
            cur_idx = mcp_table.cursor_row if (mcp_table.cursor_row is not None and 0 <= mcp_table.cursor_row < len(sorted_mcps)) else 0
            s_name = sorted_mcps[cur_idx]
            s_def = act_m.get(s_name) or dis_m.get(s_name)
            if not s_def:
                self.notify(f"Could not find configuration for {s_name}", title="Error", severity="error")
                return
            def on_inspector_done(res):
                self.load_active_agent_data()
            self.push_screen(DesktopToolInspectorModal(ag, s_name, s_def), on_inspector_done)

        def action_open_fleet_radar(self):
            self.push_screen(DesktopProcessRadarModal())

        def action_open_features_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-features"

        def populate_skills_table(self):
            ag = self.agents.get(self.selected_key)
            if not ag: return
            act_s, _ = get_agent_skills(ag)

            saved_s_row = None
            try:
                s_table = self.query_one("#table-skills", DataTable)
                saved_s_row = s_table.cursor_row
            except Exception:
                pass

            s_table = self.query_one("#table-skills", DataTable)
            s_table.clear(columns=True)
            s_table.add_columns("Status", "Skill Name", "Location / Mode", "Quick Action")
            s_table.cursor_type = "row"

            q = ""
            try:
                q = self.query_one("#skills-filter", Input).value.strip().lower()
            except Exception:
                pass

            filtered_s = [s for s in self.cached_skills if q in s.lower()] if q else self.cached_skills

            for idx, s in enumerate(filtered_s):
                is_active = (s in act_s)
                if is_active:
                    st = "[bold #a6e3a1]  ● ACTIVE [ON]   [/bold #a6e3a1]"
                    loc = "[green]skills/ (deployed)[/green]"
                    act_col = "[bold #89b4fa] [ ⇄ Click / Space ] [/bold #89b4fa]"
                else:
                    st = "[dim #6c7086]  ○ STASHED [OFF]  [/dim #6c7086]"
                    loc = "[dim]skills-available/[/dim]"
                    act_col = "[bold #a6e3a1] [ ⇄ Click / Space ] [/bold #a6e3a1]"
                s_table.add_row(st, s, loc, act_col, key=f"s-{idx}")

            if saved_s_row is not None and s_table.row_count > 0:
                s_table.move_cursor(row=min(saved_s_row, s_table.row_count - 1), scroll=False)

        def init_explorer_categories(self):
            if not FOLDER_DATA: return
            sel = self.query_one("#sel-explorer-cat", Select)
            cat_options = []
            for k in sorted(FOLDER_DATA.keys(), key=lambda x: int(x) if x.isdigit() else 99):
                v = FOLDER_DATA[k]
                title = v.get("title", f"Category {k}")
                items_len = len(v.get("items", []))
                cat_options.append((f"{k}. {title} ({items_len})", k))
            sel.set_options(cat_options)

            # Auto-map active agent to category
            agent_map = {
                "claude": "1", "claudecode": "1", "antigravity": "3", "cursor": "4",
                "codex": "5", "hermes": "7", "cline": "8", "copilot": "9",
                "opencode": "10", "pi": "13", "kiro": "16", "kilo": "16"
            }
            target_cat = agent_map.get(self.selected_key, "3")
            sel.value = target_cat
            self.load_explorer_category(target_cat)

        def load_explorer_category(self, cat_id: str):
            self.active_explorer_cat = str(cat_id)
            exp_table = self.query_one("#table-explorer", DataTable)
            exp_table.clear(columns=True)
            exp_table.add_columns("Status", "Type", "Target Name", "Path", "Description")
            exp_table.cursor_type = "row"

            cat_info = FOLDER_DATA.get(str(cat_id))
            if not cat_info: return

            for idx, item in enumerate(cat_info.get("items", [])):
                name, path, desc = item
                exists = os.path.exists(path)
                is_dir = os.path.isdir(path) if exists else ("." not in os.path.basename(path))
                st = "[bold #a6e3a1]  ● EXISTS  [/bold #a6e3a1]" if exists else "[dim #f38ba8]  ○ NOT FOUND[/dim #f38ba8]"
                t_str = "[cyan]Folder[/cyan]" if is_dir else "[yellow]File[/yellow]"
                exp_table.add_row(st, t_str, name, path, desc, key=f"exp-{idx}")

        def load_global_matrix(self):
            g_table = self.query_one("#table-global", DataTable)
            g_table.clear(columns=True)
            g_table.add_columns("Agent Name", "Active Model", "Provider", "Skills", "MCPs")
            g_table.cursor_type = "row"
            for idx, (k, ag) in enumerate(self.agents.items()):
                m_info = get_agent_models_and_providers(ag)
                act_s, _ = get_agent_skills(ag)
                act_m, _ = read_mcp_config(ag)
                g_table.add_row(
                    ag["name"],
                    m_info["active_model"][:22],
                    m_info["active_provider"][:18],
                    str(len(act_s)),
                    str(len(act_m)),
                    key=f"g-{idx}"
                )

        def on_key(self, event):
            # Universal Spacebar Toggle on focused DataTable
            if event.key == "space":
                focused = self.focused
                if isinstance(focused, DataTable):
                    if focused.id == "table-mcps":
                        event.prevent_default()
                        self.action_toggle_mcp()
                    elif focused.id == "table-skills":
                        event.prevent_default()
                        self.action_toggle_skill()
                    elif focused.id == "table-features":
                        event.prevent_default()
                        self.action_toggle_config_feature()

        def on_button_pressed(self, event: Button.Pressed):
            bid = event.button.id
            if not bid: return

            # Switch active agent in sidebar
            if bid.startswith("ag-"):
                k = bid.replace("ag-", "")
                self.selected_key = k
                for ak in self.agent_keys:
                    btn = self.query_one(f"#ag-{ak}", Button)
                    if ak == k:
                        btn.add_class("agent-item-active")
                    else:
                        btn.remove_class("agent-item-active")
                self.load_active_agent_data()
                
                # Update explorer tab category to match agent
                agent_map = {
                    "claude": "1", "claudecode": "1", "antigravity": "3", "cursor": "4",
                    "codex": "5", "hermes": "7", "cline": "8", "copilot": "9",
                    "opencode": "10", "pi": "13", "kiro": "16", "kilo": "16"
                }
                if k in agent_map:
                    try:
                        self.query_one("#sel-explorer-cat", Select).value = agent_map[k]
                        self.load_explorer_category(agent_map[k])
                    except Exception:
                        pass
                self.notify(f"Switched to {self.agents[k]['name']}", title="Agent Activated")

            elif bid in ("btn-side-theme", "btn-theme-picker"):
                self.action_open_theme_modal()

            elif bid == "btn-side-folders":
                self.action_open_explorer_tab()

            elif bid == "btn-ping-test":
                ag = self.agents.get(self.selected_key)
                m_info = get_agent_models_and_providers(ag)
                self.push_screen(DesktopPingModal(m_info["base_url"]))

            elif bid == "btn-add-provider":
                ag = self.agents.get(self.selected_key)
                self.push_screen(DesktopAddProviderModal(ag), callback=self.on_provider_saved)

            elif bid in ("btn-side-deploy", "btn-broadcast-prov"):
                self.push_screen(DesktopUniversalDeployModal(self.agents), callback=self.on_universal_deployed)

            elif bid == "btn-side-refresh":
                self.action_refresh_data()

            elif bid == "btn-set-active":
                self.action_set_active_model()

            elif bid == "btn-toggle-model":
                self.action_toggle_model()

            elif bid == "btn-toggle-mcp":
                self.action_toggle_mcp()

            elif bid == "btn-inspect-tools":
                self.action_open_tool_inspector()

            elif bid == "btn-side-radar":
                self.action_open_fleet_radar()

            elif bid == "btn-side-features":
                self.action_open_features_tab()

            elif bid == "btn-toggle-feature":
                self.action_toggle_config_feature()

            elif bid == "btn-reload-features":
                self.populate_features_table()
                self.notify("Reloaded config feature flags", title="Config Flags")

            elif bid == "btn-restore-feature-bak":
                self.action_open_restore_modal()

            elif bid == "btn-side-palette":
                self.action_open_command_palette()

            elif bid == "btn-side-export":
                self.action_export_profile()

            elif bid == "btn-side-import":
                self.action_import_profile()

            elif bid == "btn-health-check":
                self.action_run_health_checks()

            elif bid == "btn-open-registry":
                self.action_open_registry_modal()

            elif bid == "btn-restore-bak":
                self.action_open_restore_modal()

            elif bid == "btn-online-skill":
                self.action_open_skill_install_modal()

            elif bid == "btn-apply-preset":
                self.action_apply_preset()

            elif bid == "btn-broadcast-preset":
                self.action_broadcast_preset()

            elif bid == "btn-skill-toggle":
                self.action_toggle_skill()

            elif bid == "btn-skill-all":
                self.action_activate_all_skills()

            elif bid == "btn-skill-none":
                self.action_stash_all_skills()

            elif bid == "btn-warehouses":
                self.notify("Open Classic Mode (M -> [W]) for 1,350+ Warehouse Browser", title="Warehouses Hub")

            elif bid == "btn-exp-explorer":
                self.perform_explorer_action("explorer")

            elif bid == "btn-exp-editor":
                self.perform_explorer_action("editor")

            elif bid == "btn-exp-copy":
                self.perform_explorer_action("copy")

            elif bid == "btn-exp-terminal":
                self.perform_explorer_action("terminal")

        def on_select_changed(self, event: Select.Changed):
            if event.select.id == "sel-explorer-cat" and event.value != Select.BLANK:
                self.load_explorer_category(str(event.value))

        def on_input_changed(self, event: Input.Changed):
            if event.input.id == "skills-filter":
                self.populate_skills_table()
            elif event.input.id == "features-filter":
                self.populate_features_table()

        def on_data_table_row_selected(self, event: DataTable.RowSelected):
            tid = event.data_table.id
            if tid == "table-models":
                coord = event.data_table.cursor_coordinate
                ag = self.agents.get(self.selected_key)
                m_info = get_agent_models_and_providers(ag)
                if 0 <= coord.row < len(m_info["models"]):
                    model_item = m_info["models"][coord.row]
                    model_id = model_item.get("full_id") or model_item["id"]
                    set_agent_active_model(ag, model_id, provider_id=model_item.get("provider"))
                    self.load_active_agent_data()
                    self.load_global_matrix()
                    self.notify(f"Active model switched to: {model_id}", title="Model Changed")
            elif tid == "table-presets":
                self.action_apply_preset()
            elif tid == "table-mcps":
                self.action_toggle_mcp()
            elif tid == "table-skills":
                self.action_toggle_skill()
            elif tid == "table-features":
                self.action_toggle_config_feature()
            elif tid == "table-explorer":
                self.perform_explorer_action("explorer")

        def action_toggle_mcp(self):
            mcp_table = self.query_one("#table-mcps", DataTable)
            if mcp_table.cursor_row is not None and mcp_table.row_count > 0:
                saved_row = mcp_table.cursor_row
                ag = self.agents.get(self.selected_key)
                act_m, dis_m = read_mcp_config(ag)
                sorted_mcps = sorted(list(set(act_m.keys()).union(set(dis_m.keys()))))
                if 0 <= saved_row < len(sorted_mcps):
                    server_name = sorted_mcps[saved_row]
                    active_set = set(act_m.keys())
                    if server_name in active_set:
                        active_set.remove(server_name)
                        new_st = "DISABLED"
                    else:
                        active_set.add(server_name)
                        new_st = "ACTIVE"
                    save_mcp_servers(ag, active_set)
                    self.load_active_agent_data()
                    if mcp_table.row_count > 0:
                        mcp_table.move_cursor(row=min(saved_row, mcp_table.row_count - 1), scroll=False)
                    self.notify(f"MCP server '{server_name}' toggled to {new_st}", title="MCP Server Updated")

        def action_toggle_skill(self):
            s_table = self.query_one("#table-skills", DataTable)
            if s_table.cursor_row is not None and s_table.row_count > 0:
                saved_row = s_table.cursor_row
                ag = self.agents.get(self.selected_key)
                sd = ag.get("skills_dir")
                sav = ag.get("skills_available")
                if not sd or not sav: return

                os.makedirs(sd, exist_ok=True)
                os.makedirs(sav, exist_ok=True)

                q = ""
                try:
                    q = self.query_one("#skills-filter", Input).value.strip().lower()
                except Exception:
                    pass
                filtered = [s for s in self.cached_skills if q in s.lower()] if q else self.cached_skills

                if 0 <= saved_row < len(filtered):
                    skill_name = filtered[saved_row]
                    act_p = os.path.join(sd, skill_name)
                    sav_p = os.path.join(sav, skill_name)

                    if os.path.exists(act_p):
                        shutil.move(act_p, sav_p)
                        st_msg = "STASHED [OFF]"
                    elif os.path.exists(sav_p):
                        shutil.move(sav_p, act_p)
                        st_msg = "ACTIVATED [ON]"
                    else:
                        return

                    self.populate_skills_table()
                    if s_table.row_count > 0:
                        s_table.move_cursor(row=min(saved_row, s_table.row_count - 1), scroll=False)
                    self.notify(f"Skill '{skill_name}' is now {st_msg}", title="Skill Updated")

        def action_activate_all_skills(self):
            ag = self.agents.get(self.selected_key)
            sd = ag.get("skills_dir")
            sav = ag.get("skills_available")
            if not sd or not sav or not os.path.exists(sav): return
            for item in os.listdir(sav):
                src = os.path.join(sav, item)
                dst = os.path.join(sd, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            self.populate_skills_table()
            self.notify("All available skills activated!", title="Skills")

        def action_stash_all_skills(self):
            ag = self.agents.get(self.selected_key)
            sd = ag.get("skills_dir")
            sav = ag.get("skills_available")
            if not sd or not sav or not os.path.exists(sd): return
            for item in os.listdir(sd):
                src = os.path.join(sd, item)
                dst = os.path.join(sav, item)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            self.populate_skills_table()
            self.notify("All skills stashed to available pool!", title="Skills")

        def perform_explorer_action(self, action_type: str):
            exp_table = self.query_one("#table-explorer", DataTable)
            if exp_table.cursor_row is None or exp_table.row_count == 0:
                self.notify("Please select an item in the table first", title="Warning", severity="warning")
                return

            cat_info = FOLDER_DATA.get(str(self.active_explorer_cat))
            if not cat_info: return
            items = cat_info.get("items", [])
            row_idx = exp_table.cursor_row
            if not (0 <= row_idx < len(items)): return

            name, path, _ = items[row_idx]

            if action_type == "explorer":
                ok, msg = desktop_open_explorer(path)
                self.notify(msg, title=f"Explorer: {name}", severity="information" if ok else "error")
            elif action_type == "editor":
                ok, msg = desktop_open_editor(path)
                self.notify(msg, title=f"Editor: {name}", severity="information" if ok else "error")
            elif action_type == "copy":
                ok, msg = desktop_copy_clipboard(path)
                self.notify(f"Copied: {path}", title="Clipboard", severity="information" if ok else "error")
            elif action_type == "terminal":
                ok, msg = desktop_open_terminal(path)
                self.notify(msg, title=f"Terminal: {name}", severity="information" if ok else "error")

        def on_provider_saved(self, saved):
            if saved:
                self.load_active_agent_data()
                self.load_global_matrix()
                self.notify("AI Provider saved and model activated!", title="Success", severity="information")

        def on_universal_deployed(self, count):
            if count:
                self.load_active_agent_data()
                self.load_global_matrix()
                self.notify(f"Universal provider deployed to {count} agents!", title="Deployment Complete", severity="information")

        def action_set_active_model(self):
            m_table = self.query_one("#table-models", DataTable)
            if m_table.cursor_row is not None and m_table.row_count > 0:
                ag = self.agents.get(self.selected_key)
                m_info = get_agent_models_and_providers(ag)
                if 0 <= m_table.cursor_row < len(m_info["models"]):
                    model_item = m_info["models"][m_table.cursor_row]
                    model_id = model_item.get("full_id") or model_item["id"]
                    set_agent_active_model(ag, model_id, provider_id=model_item.get("provider"))
                    self.load_active_agent_data()
                    self.load_global_matrix()
                    self.notify(f"Active model switched to: {model_id}", title="Model Changed")

        def action_toggle_model(self):
            m_table = self.query_one("#table-models", DataTable)
            if m_table.cursor_row is not None and m_table.row_count > 0:
                ag = self.agents.get(self.selected_key)
                m_info = get_agent_models_and_providers(ag)
                if 0 <= m_table.cursor_row < len(m_info["models"]):
                    model_item = m_info["models"][m_table.cursor_row]
                    model_id = model_item["id"]
                    toggle_agent_model(ag, model_id, provider_id=model_item.get("provider"))
                    self.load_active_agent_data()
                    self.notify(f"Toggled model: {model_id}", title="State Changed")

        def action_refresh_data(self):
            self.agents = discover_installed_agents()
            self.load_active_agent_data()
            self.load_global_matrix()
            self.init_explorer_categories()
            self.notify("Refreshed all agents and configurations", title="Reloaded")

        def action_open_theme_modal(self):
            self.push_screen(DesktopThemeModal())

        def action_open_models_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-models"

        def action_open_skills_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-skills"

        def action_open_mcps_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-mcps"

        def action_open_explorer_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-explorer"

        def action_ping_active(self):
            ag = self.agents.get(self.selected_key)
            m_info = get_agent_models_and_providers(ag)
            self.push_screen(DesktopPingModal(m_info["base_url"]))


        def action_open_command_palette(self):
            def handle_palette(cmd_item):
                if not cmd_item: return
                cid, label, ctype = cmd_item
                if ctype == "tab":
                    tab_id = f"pane-{cid.split(':')[1]}"
                    try: self.query_one("#tabs-main", TabbedContent).active = tab_id
                    except Exception: pass
                elif ctype == "agent":
                    ag_id = cid.split(":")[1]
                    self.selected_key = ag_id
                    self.update_sidebar_active_class()
                    self.load_active_agent_data()
                    self.notify(f"Switched active agent to: {self.agents[ag_id]['name']}", title="Agent Switched")
                elif ctype == "preset":
                    preset_id = cid.split(":")[1]
                    ag = self.agents.get(self.selected_key)
                    ok, msg = apply_mcp_preset(ag, preset_id, all_agents=self.agents, broadcast=False)
                    self.load_active_agent_data()
                    self.notify(msg, title="Preset Applied", severity="information" if ok else "error")
                elif ctype == "preset_broadcast":
                    p_table = self.query_one("#table-presets", DataTable)
                    cur_idx = p_table.cursor_row if (p_table.cursor_row is not None and 0 <= p_table.cursor_row < len(MCP_PRESETS)) else 0
                    preset_id = MCP_PRESETS[cur_idx]["id"]
                    ag = self.agents.get(self.selected_key)
                    ok, msg = apply_mcp_preset(ag, preset_id, all_agents=self.agents, broadcast=True)
                    self.load_active_agent_data()
                    self.notify(msg, title="Fleet Broadcast Complete", severity="information" if ok else "error")
                elif ctype == "radar":
                    self.action_open_fleet_radar()
                elif ctype == "inspector":
                    self.action_open_tool_inspector()
                elif ctype == "features":
                    self.action_open_features_tab()
                elif ctype == "health":
                    self.action_run_health_checks()
                elif ctype == "registry":
                    self.action_open_registry_modal()
                elif ctype == "skill_install":
                    self.action_open_skill_install_modal()
                elif ctype == "restore":
                    self.action_open_restore_modal()
                elif ctype == "export":
                    self.action_export_profile()
                elif ctype == "import":
                    self.action_import_profile()
                elif ctype == "theme":
                    self.action_open_theme_modal()
                elif ctype == "ping":
                    self.action_ping_active()
                elif ctype == "refresh":
                    self.action_refresh_data()

            self.push_screen(DesktopCommandPaletteModal(), handle_palette)

        def action_open_presets_tab(self):
            self.query_one("#tabs-main", TabbedContent).active = "pane-presets"

        def action_run_health_checks(self):
            ag = self.agents.get(self.selected_key)
            if not ag: return
            act_m, dis_m = read_mcp_config(ag)
            all_servers = {**act_m, **dis_m}
            if not all_servers:
                self.notify("No MCP servers configured for this agent", title="Health Check", severity="warning")
                return

            self.notify("Probing active MCP server heartbeats...", title="Health Check", severity="information")
            checked_count = 0
            for s_name, s_def in all_servers.items():
                if s_name in act_m:
                    ok, ms, detail = probe_mcp_server_health(s_name, s_def, timeout=2.0)
                    self.mcp_health_cache[s_name] = (ok, ms, detail)
                    checked_count += 1

            self.load_active_agent_data()
            self.notify(f"Probed {checked_count} active servers successfully!", title="Health Check Complete")

        def action_open_registry_modal(self):
            ag = self.agents.get(self.selected_key)
            def on_reg_done(res):
                if res:
                    ok, msg = res
                    self.load_active_agent_data()
                    self.notify(msg, title="Registry Install", severity="information" if ok else "error")
            self.push_screen(DesktopRegistryModal(ag, self.agents), on_reg_done)

        def action_open_restore_modal(self):
            ag = self.agents.get(self.selected_key)
            def on_res_done(res):
                if res:
                    ok, msg = res
                    self.load_active_agent_data()
                    self.notify(msg, title="Rollback", severity="information" if ok else "error")
            self.push_screen(DesktopRestoreModal(ag), on_res_done)

        def action_open_skill_install_modal(self):
            ag = self.agents.get(self.selected_key)
            def on_skill_done(res):
                if res:
                    ok, msg = res
                    self.load_active_agent_data()
                    self.notify(msg, title="Skill Installer", severity="information" if ok else "error")
            self.push_screen(DesktopSkillInstallModal(ag), on_skill_done)

        def action_export_profile(self):
            ok, msg = export_omni_profile(self.agents, "omni-profile.json")
            self.notify(msg, title="Export Complete" if ok else "Export Failed", severity="information" if ok else "error")

        def action_import_profile(self):
            ok, msg = import_omni_profile(self.agents, "omni-profile.json")
            self.load_active_agent_data()
            self.load_global_matrix()
            self.notify(msg, title="Import Complete" if ok else "Import Failed", severity="information" if ok else "error")

        def action_apply_preset(self):
            p_table = self.query_one("#table-presets", DataTable)
            if p_table.cursor_row is not None and 0 <= p_table.cursor_row < len(MCP_PRESETS):
                preset = MCP_PRESETS[p_table.cursor_row]
                ag = self.agents.get(self.selected_key)
                ok, msg = apply_mcp_preset(ag, preset["id"], all_agents=self.agents, broadcast=False)
                self.load_active_agent_data()
                self.notify(msg, title="Preset Applied", severity="information" if ok else "error")

        def action_broadcast_preset(self):
            p_table = self.query_one("#table-presets", DataTable)
            if p_table.cursor_row is not None and 0 <= p_table.cursor_row < len(MCP_PRESETS):
                preset = MCP_PRESETS[p_table.cursor_row]
                ag = self.agents.get(self.selected_key)
                ok, msg = apply_mcp_preset(ag, preset["id"], all_agents=self.agents, broadcast=True)
                self.load_active_agent_data()
                self.notify(msg, title="Fleet Broadcast Complete", severity="information" if ok else "error")

# ================= APPLICATION ENTRYPOINT =================

def main():
    """Main CLI / GUI entrypoint for OmniAgent Manager (pip console_script & direct execution)."""
    if "-h" in sys.argv or "--help" in sys.argv:
        print("""OmniAgent Manager v4.1.0 - Universal AI Agent Control Hub
Usage:
  omni-agent [OPTIONS]
  omni-agent-manager [OPTIONS]
  python omni_agent_manager.py [OPTIONS]

Options:
  --help, -h            Show this help message and exit
  --version, -v         Show version information and exit
  --classic, --cli      Launch in classic minimal ANSI terminal menu mode
  --folders, --explorer Launch standalone interactive agent folder explorer
  --radar               Display live local inference engine status & agent process monitor
  --features [AGENT_ID] Scan and list all discovered toggleable JSON config feature flags
  --tools [SERVER_NAME] Query tools/list schema for an MCP server on active agent
  --export [PATH]       Export all agents configuration into omni-profile.json
  --import [PATH]       Import and sync configuration from omni-profile.json
  --presets             Display available MCP Workspaces & Presets catalog
  --health              Run probe heartbeats on all discovered active MCP servers
  --theme THEME         Launch with specified UI theme (github_dark, matrix_green, etc.)
  --no-admin            Skip Administrator privilege check (for restricted environments)
""")
        return
    elif "--export" in sys.argv:
        ag = discover_installed_agents()
        out = "omni-profile.json"
        if len(sys.argv) > sys.argv.index("--export") + 1:
            out = sys.argv[sys.argv.index("--export") + 1]
        ok, msg = export_omni_profile(ag, out)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return
    elif "--import" in sys.argv:
        ag = discover_installed_agents()
        inp = "omni-profile.json"
        if len(sys.argv) > sys.argv.index("--import") + 1:
            inp = sys.argv[sys.argv.index("--import") + 1]
        ok, msg = import_omni_profile(ag, inp)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")
        return
    elif "--presets" in sys.argv:
        print("OmniAgent Manager - Available MCP Workspaces & Presets:")
        for pr in MCP_PRESETS:
            print(f"  • {pr['name']:<25} : {pr['desc']}")
        return
    elif "--radar" in sys.argv:
        res = scan_fleet_processes()
        print("OmniAgent Fleet & Local Engine Radar:")
        print("\n[Local AI Inference Engines]")
        for eng in res["engines"]:
            st = "ONLINE" if eng["online"] else "OFFLINE"
            print(f"  • {eng['name']:<28} (Port {eng['port']}): [{st}]")
        print("\n[Active Agent Processes (psutil)]")
        if res["processes"]:
            for p in res["processes"]:
                print(f"  • PID {p['pid']:<6} | {p['agent_kw'].upper():<12} | {p['name']:<20} | CPU: {p['cpu']:.1f}% | RAM: {p['mem_mb']} MB")
        else:
            print("  • No active agent processes currently in memory.")
        return
    elif "--features" in sys.argv:
        ag = discover_installed_agents()
        target_k = "claude"
        if len(sys.argv) > sys.argv.index("--features") + 1 and not sys.argv[sys.argv.index("--features") + 1].startswith("-"):
            target_k = sys.argv[sys.argv.index("--features") + 1]
        target_ag = ag.get(target_k) or next(iter(ag.values()), None)
        if not target_ag:
            print(f"Agent '{target_k}' not found.")
            return
        flags = extract_agent_config_flags(target_ag)
        print(f"Config Feature Flags for {target_ag['name']} ({len(flags)} discovered):")
        for fl in flags:
            st = "ENABLED [ON]" if fl["value"] else "DISABLED [OFF]"
            print(f"  • {fl['key']:<45} : [{st}] ({fl['filename']})")
        return
    elif "--tools" in sys.argv:
        ag = discover_installed_agents()
        target_s = None
        if len(sys.argv) > sys.argv.index("--tools") + 1 and not sys.argv[sys.argv.index("--tools") + 1].startswith("-"):
            target_s = sys.argv[sys.argv.index("--tools") + 1]
        found_def = None
        for a_k, a_v in ag.items():
            act_m, _ = read_mcp_config(a_v)
            if target_s and target_s in act_m:
                found_def = act_m[target_s]
                break
            elif not target_s and act_m:
                target_s = next(iter(act_m.keys()))
                found_def = act_m[target_s]
                break
        if not found_def:
            print(f"MCP server '{target_s}' not found.")
            return
        print(f"Querying tools/list for MCP server '{target_s}'...")
        ok, res = query_mcp_tools(target_s, found_def)
        if ok:
            print(f"Discovered {len(res)} tools:")
            for t in res:
                params = list(t.get("inputSchema", {}).get("properties", {}).keys())
                print(f"  • {t.get('name'):<25} : {t.get('description', '')[:50]} (params: {params})")
        else:
            print(f"Failed to query tools: {res}")
        return
    elif "--health" in sys.argv:
        ag = discover_installed_agents()
        print("Running MCP Server Heartbeat Checks across detected fleet...")
        for k, v in ag.items():
            act_m, _ = read_mcp_config(v)
            if act_m:
                print(f"\nAgent: {v['name']} ({len(act_m)} active servers):")
                for s_name, s_def in act_m.items():
                    ok, ms, msg = probe_mcp_server_health(s_name, s_def)
                    st = f"[LIVE {ms}ms]" if ok else f"[FAIL: {msg}]"
                    print(f"  - {s_name:<20} : {st}")
        return
    elif "-v" in sys.argv or "--version" in sys.argv:
        print("OmniAgent Manager version 4.1.0")
        return
    elif "--classic" in sys.argv or "--cli" in sys.argv or not HAS_TEXTUAL:
        master_hub()
    elif "--folders" in sys.argv or "--explorer" in sys.argv:
        open_agent_folder_cli()
    else:
        try:
            app = AgentCustomizerDesktopApp()
            app.run()
        except Exception as e:
            # Fallback seamlessly to ANSI CLI on any exception
            print(f"Starting Classic CLI mode (Desktop TUI fallback: {e})")
            master_hub()

if __name__ == "__main__":
    main()


