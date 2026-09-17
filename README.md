# 🌐 OmniAgent Manager

[![Version: 4.1.0](https://img.shields.io/badge/Version-4.1.0-blueviolet.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Package: pip installable](https://img.shields.io/badge/Package-pip%20install%20.-orange.svg)](pyproject.toml)
[![Console Script: omni--agent](https://img.shields.io/badge/CLI-omni--agent-blueviolet.svg)](pyproject.toml)
[![TUI Engine: Textual 8.2+](https://img.shields.io/badge/TUI-Textual%208.2%2B-magenta.svg)](https://textual.textualize.io)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

**OmniAgent Manager** is an enterprise-grade operational control hub, configuration orchestrator, and diagnostics cockpit for modern AI coding agents, model providers, custom agent skills, and Model Context Protocol (MCP) tool servers.

Instead of hunting through dozens of fragmented directories, cryptic JSON/TOML configuration files, and incompatible schema definitions across disparate AI assistants, OmniAgent Manager aggregates your entire AI development fleet into a unified, high-performance control plane.

---

## 📑 Table of Contents

- [The Problem OmniAgent Manager Solves](#-the-problem-omniagent-manager-solves)
- [Core Architectural Pillars & Technical Benefits](#-core-architectural-pillars--technical-benefits)
- [Feature Deep-Dive](#-feature-deep-dive)
  - [1. Universal AI Models & Providers Dashboard](#1-universal-ai-models--providers-dashboard)
  - [2. MCP Presets & Workspaces (1-Click Fleet Synchronization)](#2-mcp-presets--workspaces-1-click-fleet-synchronization)
  - [3. Live MCP Health Checks & Heartbeats](#3-live-mcp-health-checks--heartbeats)
  - [4. 1-Click MCP Registry Auto-Installer](#4-1-click-mcp-registry-auto-installer)
  - [5. Fuzzy Command Palette (Ctrl+P / F1)](#5-fuzzy-command-palette-ctrlp--f1)
  - [6. 1-Click "Restore .bak" Rollback Manager](#6-1-click-restore-bak-rollback-manager)
  - [7. Responsive Sidebar Auto-Collapse (Icon Rail)](#7-responsive-sidebar-auto-collapse-icon-rail)
  - [8. Portable Bundle Export & Import (omni-profile.json)](#8-portable-bundle-export--import-omni-profilejson)
  - [9. Live Token & Cost Gauges (abtop Pattern)](#9-live-token--cost-gauges-abtop-pattern)
  - [10. Online Skill & Plugin Auto-Installer](#10-online-skill--plugin-auto-installer)
  - [11. Deep Agent Filesystem Explorer (20 Categories, 150+ Paths)](#11-deep-agent-filesystem-explorer-20-categories-150-paths)
  - [12. Automated Safety, AST Validation & Atomic Backups](#12-automated-safety-ast-validation--atomic-backups)
  - [13. MCP Tool Runner & Schema Inspector (Zero LLM Tokens)](#13-mcp-tool-runner--schema-inspector-zero-llm-tokens)
  - [14. Sub-Tool Context Trimmer](#14-sub-tool-context-trimmer)
  - [15. Fleet Process & Local Engine Radar (psutil Live Monitor)](#15-fleet-process--local-engine-radar-psutil-live-monitor)
  - [16. Universal Agent Config JSON Feature Switchboard](#16-universal-agent-config-json-feature-switchboard)
- [Supported AI Agents & Runtimes](#-supported-ai-agents--runtimes)
- [Installation & Setup](#-installation--setup)
  - [Method 1: Global Pip Installation (Recommended)](#method-1-global-pip-installation-recommended)
  - [Method 2: Standalone Windows Batch Launcher (Auto-Elevating)](#method-2-standalone-windows-batch-launcher-auto-elevating)
  - [Method 3: Direct Git Clone & Run](#method-3-direct-git-clone--run)
- [CLI Reference & Command Flags](#-cli-reference--command-flags)
- [Keyboard Navigation & Shortcuts](#-keyboard-navigation--shortcuts)
- [Directory Layout](#-directory-layout)
- [Contributing & Development](#-contributing--development)
- [License](#-license)

---

## 💡 The Problem OmniAgent Manager Solves

Developers today rarely use only one AI coding assistant. A typical high-performance engineering workflow combines:
- **Claude Code CLI** for rapid terminal scaffolding and deep git integration.
- **Google Antigravity** for complex autonomous multi-agent pipelines and workflows.
- **OpenCode AI & Codex** for local and open-source models.
- **Cursor IDE, Windsurf, & VS Code / Cline** for in-editor copilot completions and file editing.
- **Nous Hermes, Aider, and custom LLM runtimes** for local privacy-first offline coding.

### The Pain Points:
1. **Configuration Fragmentation**: Every tool enforces a different configuration schema (`claude.json`, `opencode.json`, `mcp.json`, `config.toml`, `settings.json`) in arbitrary directories (`~/.claude`, `%USERPROFILE%\.gemini\antigravity`, `%APPDATA%\Cursor`, `%USERPROFILE%\.opencode`).
2. **Context Window Exhaustion**: Running 15 MCP servers simultaneously injects 15,000–35,000 tokens of schema into system prompts on *every single request*, dramatically slowing down reasoning and ballooning API costs.
3. **Model Swapping Overhead**: Switching between DeepSeek-R1, Claude 3.5 Sonnet, GPT-4o, and local Ollama/vLLM endpoints requires editing multiple distinct config files, copy-pasting API keys, and risking typos.
4. **Skill & Tool Isolation**: A skill authored for Claude or Antigravity remains trapped in that tool's private stash rather than shared universally across all agent runtimes.
5. **Silent Tool Failures**: Malfunctioning MCP servers hang silently or crash agents without clear health diagnostics or heartbeat verification.

OmniAgent Manager eliminates these friction points by providing **one single source of truth** with automated synchronization, schema validation, and atomic backups.

---

## 🏛️ Core Architectural Pillars & Technical Benefits

| Technical Benefit | Real-World Impact | How OmniAgent Manager Delivers It |
|---|---|---|
| **MCP Workspaces & Presets** | Save up to 85% of LLM context window by loading only needed tools per task | Switch task profiles (Full-Stack Web, Data Science, DevOps, Minimal) with 1-click fleet broadcast |
| **Live Health Heartbeats** | Stop debugging silent tool failures and hanging child processes | Sub-second stdio JSON-RPC initialize handshake & async HTTP latency probing |
| **1-Click Registry Auto-Installer** | Install verified MCPs in seconds without JSON syntax errors | Curated catalog of top verified servers with automated env injection |
| **Fuzzy Command Palette** | Navigate agents, tools, tabs, and presets in under 2 seconds | LazyGit/VS Code pattern (`Ctrl+P` / `F1`) with instant search-as-you-type |
| **1-Click Rollback Manager** | Never lose a working configuration to a syntax error | Visual `.bak` snapshot selector restores files with safety snapshots |
| **Portable Fleet Profiles** | Share complete setups across machines or team members | Single-file export/import (`omni-profile.json`) with cross-platform normalization |
| **Live Token & Cost Gauges** | Always know tool overhead and remaining context headroom | Real-time schema token estimator and per-request cost breakdown (`abtop` pattern) |
| **Responsive Sidebar Rail** | Maximizes table width on smaller laptop displays | Auto-collapses into a 10-column icon rail when terminal width < 95 columns |
| **MCP Tool Runner & Inspector** | Inspect tool schemas & test live tool calls without consuming LLM tokens | Interactive TUI runner sends JSON-RPC requests directly to MCP child processes |
| **Sub-Tool Context Trimmer** | Disable heavy sub-tools within an MCP server to reduce prompt bloat | Selectively trim tools with `[Space]` and instantly reclaim context headroom |
| **Fleet & Engine Radar** | Real-time observability over local models and agent processes | Live `psutil` process tracker + socket listener checks for Ollama, LM Studio, vLLM |
| **Config Feature Switchboard** | Toggle hidden feature flags across all agent JSON configurations | Recursive boolean flag scanner with 1-click toggling and automated `.bak` backups |

---

## ⚡ Feature Deep-Dive

### 1. Universal AI Models & Providers Dashboard
- **Fleet-Wide Discovery**: Detects active installations and config files of 11+ AI coding agents.
- **Provider Aggregator**: Connect local engines (Ollama on `11434`, LM Studio on `1234`, vLLM on `8000`) and cloud endpoints (OpenRouter, DeepSeek, Anthropic, OpenAI, Groq).
- **Universal 1-Click Broadcast**: Deploy API keys, custom base URLs, and active model IDs across all detected agents simultaneously.
- **Real-Time Endpoint Ping**: Probe round-trip latency to remote model APIs before launching workflows.

### 2. MCP Presets & Workspaces (1-Click Fleet Synchronization)
- **Task-Based Tool Grouping**: Stop loading all MCPs at once. Use curated workspaces:
  - `🌐 Full-Stack Web`: `filesystem`, `github`, `brave-search`, `puppeteer`, `fetch`
  - `📊 Data Science & SQL`: `postgres`, `sqlite`, `filesystem`, `memory`
  - `🚀 DevOps & Cloud`: `docker`, `kubernetes`, `aws`, `github`, `filesystem`
  - `🛡️ Security & Audit`: `semgrep`, `sentry`, `github`, `filesystem`
  - `🪶 Minimal / Lean`: `filesystem` only (maximum context window preservation)
  - `✨ All Active`: Enable all configured servers
- **1-Click Fleet Broadcast**: Apply a preset to the active agent, or click **"⚡ 1-Click Broadcast All 11 Agents"** to atomically update the entire fleet in milliseconds.
- **Manual Management Preserved**: Individual per-MCP toggling remains completely intact in the MCPs tab.

### 3. Live MCP Health Checks & Heartbeats
- **Sub-Second Probing**:
  - **Stdio Processes**: Spawns test subprocess, transmits standard MCP JSON-RPC initialize payload, and measures round-trip latency.
  - **HTTP / SSE Endpoints**: Sends async GET/HEAD requests to verify endpoint connectivity.
- **High-Contrast Indicators**:
  - `● LIVE (28ms)` (Bright Green)
  - `○ DISABLED [OFF]` (Muted Grey)
  - `⚠ STOPPED / FAILED` (Amber / Red)
- **CLI Mode**: Run `omni-agent --health` to probe all servers from your terminal without opening the GUI.

### 4. 1-Click MCP Registry Auto-Installer
- **Verified Catalog**:
  - `GitHub MCP` (`@modelcontextprotocol/server-github`)
  - `PostgreSQL MCP` (`@modelcontextprotocol/server-postgres`)
  - `SQLite MCP` (`@modelcontextprotocol/server-sqlite`)
  - `Brave Web Search` (`@modelcontextprotocol/server-brave-search`)
  - `Secure Filesystem` (`@modelcontextprotocol/server-filesystem`)
  - `Docker Manager` (`mcp-server-docker`)
  - `Knowledge Graph Memory` (`@modelcontextprotocol/server-memory`)
  - `Puppeteer Automation` (`@modelcontextprotocol/server-puppeteer`)
  - `Web Fetch & Scraper` (`mcp-server-fetch`)
  - `Sequential Thinking` (`@modelcontextprotocol/server-sequential-thinking`)
  - `Context Mode Sandbox` (`@context-mode/mcp`)
- **Automated Parameter Injection**: Prompts for required API keys/connection strings and injects sanitized configuration into target agent files.

### 5. Fuzzy Command Palette (Ctrl+P / F1)
- **Quick-Access Modal**: Press `Ctrl+P` or `F1` from anywhere in the app to open the floating command palette.
- **Fuzzy Search Scope**: Switch agents, jump between tabs, apply presets, run health checks, trigger backups, export profiles, and change themes in seconds.

### 6. 1-Click "Restore .bak" Rollback Manager
- **Visual Snapshot History**: Press `Ctrl+R` or click `↺ Restore .bak` to view all timestamped configuration backups.
- **Instant Rollback**: Select any historical backup and restore it with one click. OmniAgent Manager automatically creates a `.pre_restore.bak` safety copy before restoring.

### 7. Responsive Sidebar Auto-Collapse (Icon Rail)
- **Intelligent Layout**: On displays or terminals with `< 95` columns, the sidebar automatically collapses to an 10-column icon rail (`● AGY`, `● CLD`, `● OPC`, `● CUR`, etc.).
- **Automatic Expansion**: When resized back to `>= 95` columns, full agent titles and badges return automatically.

### 8. Portable Bundle Export & Import (omni-profile.json)
- **Fleet Snapshot**: Export your active models, endpoints, enabled skills, and active MCP servers into a single portable `omni-profile.json` file.
- **Cross-Machine Sync**: Import `omni-profile.json` on a new workstation to configure all 11 local AI agents automatically.
- **CLI Commands**:
  ```bash
  omni-agent --export [path]
  omni-agent --import [path]
  ```

### 9. Live Token & Cost Gauges (abtop Pattern)
- **Context Overhead Tracking**: Live banner computes approximate JSON schema token footprint across active MCP tools (~3.85 characters/token).
- **Headroom Bar**: High-contrast visual bar displaying remaining context window capacity:
  ```
  Tools Context Overhead: 8,420 tokens (6.6% of 128k) [██░░░░░░░░░░░░] Headroom: 119.5k free  Est. Cost: ~$0.025/req (Claude)
  ```

### 10. Online Skill & Plugin Auto-Installer
- **Multi-Source Support**:
  - **Git Clone**: Clone skill repositories directly into the agent's active skills folder.
  - **Direct URL**: Download raw `SKILL.md` documents directly from GitHub or web links.
  - **NPX Package**: Run official npx package installers with one click.

### 11. Deep Agent Filesystem Explorer (20 Categories, 150+ Paths)
Consolidates the complete filesystem catalog of modern AI coding infrastructure:
1. **Claude Code CLI**: Global config (`.claude.json`), project instructions, custom skills, subagents.
2. **Claude Desktop & Cowork 3P**: Desktop app config, MCP servers, sessions, VM environments.
3. **Google Antigravity**: User configuration, builtin skills, global skills, rules, MCP schemas.
4. **Cursor IDE**: System settings, workspace rules, `skills-cursor`, `mcp.json`.
5. **OpenAI Codex CLI**: TOML configurations, CCR routers, local cache, plugins.
6. **Codex Desktop & OpenAI App**: Local runtimes, web cache, extension store.
7. **Nous Hermes Agent**: System prompt configurations, memory stores, primary skills.
8. **VS Code & Cline**: Global storage, extension configs, Cline CLI directories.
9. **GitHub Copilot**: CLI configuration, telemetry, router extensions, logs.
10. **OpenCode AI Desktop & CLI**: App config (`opencode.json`), active agents, custom MCPs.
11. **OpenManus Bot & Operator**: Agent runner, execution logs, workflow definitions.
12. **Local Models & Knowledge Engines**: Ollama models, LM Studio cache, HuggingFace weights.
13. **Pi Coding Agent**: Session storage, agent definitions, tools.
14. **Claude Code Router (CCR)**: Routing policies, load balancing configs.
15. **Browser Automation Agents**: ClawBrowser, Camoufox, AdsPower profile directories.
16. **Utility Agents & Bridges**: Kiro, Kilo, MCPorter tool translation caches.
17. **Master Skills Warehouses**: Centralized upstream repositories and skill stores.
18. **Master Personas & Subagents**: Custom role definitions, instructions, and prompt libraries.
19. **Master MCPs & Frameworks**: Source code repositories for custom MCP servers.
20. **Master Projects Root Hub**: Active developer workspace repositories.

**Instant Actions on Any Target:**
- 📁 **Open in Explorer**: Launches native file manager directly at the target path.
- 📝 **Open in Editor**: Launches your configured editor (VS Code, Cursor, or Notepad) focused on the file.
- 📋 **Copy Path**: Copies clean, absolute path directly to your OS clipboard.
- 💻 **Terminal Here**: Spawns an interactive shell pre-navigated to the target directory.

### 12. Automated Safety, AST Validation & Atomic Backups
- **Automatic `.bak` Snapshots**: Every write operation creates a timestamped backup before touching target files.
- **Atomic File Swapping**: Configuration files are written to a temporary sibling file and renamed atomically to prevent partial writes.
- **Syntax Pre-Validation**: Validates JSON and TOML structures before saving to prevent corrupting active agent configurations.

### 13. MCP Tool Runner & Schema Inspector (Zero LLM Tokens)
- **Direct Child Process Probing**: Connects directly to the configured MCP server process over standard JSON-RPC protocol (`initialize` → `notifications/initialized` → `tools/list`).
- **Interactive Tool Runner**: Test and execute any tool live inside the TUI without wasting prompt tokens or calling LLM APIs.
  - Pass JSON arguments directly (e.g. `{"query": "search query"}`).
  - View raw structured output and verify parameters before deploying into autonomous agent workflows.
- **Shortcut**: Press `I` on the MCP Tool Servers tab or click `🔍 Inspect & Trim Tools`.

### 14. Sub-Tool Context Trimmer
- **Surgical Context Reduction**: Large MCP servers often bundle 10–25 individual tools, injecting thousands of unwanted schema tokens into every LLM request.
- **Per-Tool Disabling**: With one keypress (`Space`), disable individual tools within an MCP server (persisted in `.omni_trimmed_tools.json` and agent configuration).
- **Instant Headroom Feedback**: The live context gauge immediately recalculates, displaying the exact tokens saved and cost reduction.

### 15. Fleet Process & Local Engine Radar (psutil Live Monitor)
- **Local AI Inference Engine Radar**: Probes listening ports in real time:
  - `Ollama Inference Engine` (Port `11434`)
  - `LM Studio Local Server` (Port `1234`)
  - `vLLM / LocalAI Engine` (Port `8000`)
  - `LocalAI Secondary` (Port `5000`)
- **Active Agent Process Tracking**: Uses `psutil` to detect running instances of Claude, Antigravity, OpenCode, Cursor, Codex, and Hermes in system memory. Displays real-time PID, CPU %, and memory RSS footprint.
- **Shortcut**: Press `O` or click `📡 Fleet Process Radar [O]`.
- **CLI Mode**: Run `omni-agent --radar` for a fast terminal snapshot.

### 16. Universal Agent Config JSON Feature Switchboard
- **Dynamic Configuration Discovery**: Recursively scans all configuration files associated with the active agent (`.claude.json`, `antigravity/config.json`, `cursor/settings.json`, `opencode.json`, etc.).
- **Live Boolean Flag Switchboard**: Extracts hundreds of hidden boolean settings and experimental feature flags into a clean, searchable table.
- **1-Click Atomic Toggling**: Press `Space` to toggle any setting on/off. OmniAgent Manager automatically creates a timestamped `.bak` safety backup and rewrites the JSON file atomically.
- **Shortcut**: Switch to tab `⚙️ Config Feature Flags` or press `G`.
- **CLI Mode**: Run `omni-agent --features [AGENT_ID]` to inspect flags from the terminal.

---

## 🤖 Supported AI Agents & Runtimes

| Agent / Runtime | Detected Config Formats | Models | Skills | MCPs | Presets | Explorer Support |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Google Antigravity** | JSON / YAML / MD | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Claude Code CLI** | JSON / Markdown | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenCode AI** | JSON / TS | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cursor IDE** | JSON / MDC / Rules | ✅ | ✅ | ✅ | ✅ | ✅ |
| **VS Code & Cline** | JSON / Settings | ✅ | ✅ | ✅ | ✅ | ✅ |
| **GitHub Copilot CLI** | YAML / JSON | ✅ | ✅ | ✅ | ✅ | ✅ |
| **OpenAI Codex CLI** | TOML / JSON | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Nous Hermes** | JSON / YAML | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Pi Coding Agent** | JSON / Markdown | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Claude Desktop** | JSON (`claude_desktop_config.json`) | — | — | ✅ | ✅ | ✅ |
| **Local LLM Runtimes** | Ollama / LM Studio / vLLM | ✅ | — | — | — | ✅ |

---

## 🚀 Installation & Setup

### Method 1: Global Pip Installation (Recommended)
Installing via `pip` creates global console commands (`omni-agent` and `omni-agent-manager`) accessible from any terminal or directory.

```bash
# Clone the repository
git clone https://github.com/your-username/omni-agent-manager.git
cd omni-agent-manager

# Install in editable mode for current user
pip install -e .
```

Once installed, simply launch from any terminal:
```bash
# Launch default Desktop TUI
omni-agent

# Launch classic ANSI CLI mode
omni-agent --classic

# Launch standalone 20-category folder catalog
omni-agent --folders

# Export complete fleet configuration
omni-agent --export

# Probe live health heartbeats across all MCP servers
omni-agent --health
```

---

### Method 2: Standalone Windows Batch Launcher (Auto-Elevating)
OmniAgent Manager includes an intelligent Windows launcher script (`omni_agent_manager.bat`) that:
- Detects if administrator permissions are required to modify system-level agent configs.
- Seamlessly requests Windows UAC elevation without directory path errors.
- Guarantees execution in the correct script directory (avoiding `System32` working directory issues).

```cmd
:: Simply double-click omni_agent_manager.bat in File Explorer, or run:
omni_agent_manager.bat
```

To bypass administrator prompt (for restricted or CI environments):
```cmd
omni_agent_manager.bat --no-admin
```

---

### Method 3: Direct Git Clone & Run
```bash
git clone https://github.com/your-username/omni-agent-manager.git
cd omni-agent-manager

pip install -r requirements.txt

python omni_agent_manager.py
```

---

## ⌨️ CLI Reference & Command Flags

```
OmniAgent Manager v4.1.0 - Universal AI Agent Control Hub

Usage:
  omni-agent [OPTIONS]
  omni-agent-manager [OPTIONS]
  python omni_agent_manager.py [OPTIONS]
  omni_agent_manager.bat [OPTIONS]

Options:
  -h, --help            Display help reference and exit
  -v, --version         Display version details and exit
  --radar               Display live local inference engine status & agent process monitor
  --features [AGENT_ID] Scan and list all discovered toggleable JSON config feature flags
  --tools [SERVER_NAME] Query tools/list schema for an MCP server on active agent
  --presets             Display available MCP Workspaces & Presets catalog
  --health              Run probe heartbeats on all discovered active MCP servers
  --export [PATH]       Export all agents configuration into omni-profile.json
  --import [PATH]       Import and sync configuration from omni-profile.json
  --classic, --cli      Run in minimal ANSI terminal menu mode (ideal for SSH)
  --folders, --explorer Launch directly into 20-Category Folder Explorer
  --theme THEME         Launch with specified UI theme (e.g. github_dark, matrix_green)
  --no-admin            Skip Windows UAC elevation check
```

---

## 🕹️ Keyboard Navigation & Shortcuts

| Key | Context | Action |
|:---:|:---|:---|
| `Ctrl+P` / `F1` | Global | Open **Fuzzy Command Palette** modal |
| `Ctrl+B` | Global | **Toggle Sidebar** (Collapse to 100% full workspace width) |
| `W` | Global | Switch to **MCP Presets & Workspaces** tab |
| `M` | Global | Switch to **AI Models & Providers** tab |
| `S` | Global | Switch to **Skills Lifecycle** tab |
| `C` | Global | Switch to **MCP Tool Servers** tab |
| `I` | MCPs Tab | Open **MCP Tool Runner & Schema Inspector** modal |
| `O` | Global | Open **Fleet Process & Local Engine Radar** modal |
| `G` | Global | Switch to **Config Feature Flags Switchboard** tab |
| `F` | Global | Switch to **20-Category Agent Explorer** tab |
| `T` | Global | Open **Theme & Palette Selector** modal |
| `P` | Models Tab | Run **Real-Time Ping Test** on active provider endpoint |
| `Ctrl+R` | Global | Open **1-Click .bak Backup Rollback Manager** |
| `Space` | Tables | **Toggle selected item** in-place (no cursor jumping) |
| `Enter` | Tables | **Select / Apply** active item or execute primary action |
| `↑` / `↓` | Tables | Navigate through rows smoothly |
| `R` | Global | **Refresh** all agent runtimes, skills, and configs from disk |
| `Q` | Global | **Quit** application cleanly |

---

## 📂 Directory Layout

```
omni-agent-manager/
├── omni_agent_manager.py     # Complete standalone core engine (TUI, CLI, Models, Presets, Health, Registry)
├── omni_agent_manager.bat    # Windows launcher with robust UAC elevation handling
├── pyproject.toml            # PEP 517/621 packaging (registers omni-agent & omni-agent-manager v4.0.0)
├── setup.py                  # Backward-compatible setuptools build script
├── requirements.txt          # Production dependencies (Textual, Rich)
├── LICENSE                   # MIT Open Source License
├── .gitignore                # Clean development gitignore
└── README.md                 # Technical architecture and user guide
```

---

## 🤝 Contributing & Development

Contributions are welcome! Please follow these development standards:
1. **Zero Unnecessary Dependencies**: Keep external runtime requirements strictly limited to `textual` and `rich` (with optional `httpx` and `psutil`).
2. **Dynamic Pathing**: Never hardcode user profiles or absolute drive letters. Always use dynamic platform resolvers (`USERPROFILE`, `HOME`, `resolve_projects_dir()`).
3. **Atomic Modification**: Every write to user configuration files must include backup handling and AST validation.

```bash
# Clone and create editable installation for local development
git clone https://github.com/your-username/omni-agent-manager.git
cd omni-agent-manager
pip install -e .
```

---

## 📜 License

Distributed under the [MIT License](LICENSE).  
Authored and maintained by **Javed Hamza**.
