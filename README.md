# 🌐 OmniAgent Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Package: pip installable](https://img.shields.io/badge/Package-pip%20install%20.-orange.svg)](pyproject.toml)
[![Console Script: omni--agent](https://img.shields.io/badge/CLI-omni--agent-blueviolet.svg)](pyproject.toml)
[![TUI Engine: Textual 8.2+](https://img.shields.io/badge/TUI-Textual%208.2%2B-magenta.svg)](https://textual.textualize.io)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com)

**OmniAgent Manager** is a universal operational control hub, configuration orchestrator, and diagnostics cockpit for modern AI coding agents, model providers, custom agent skills, and Model Context Protocol (MCP) servers.

Instead of hunting through dozens of fragmented directories, cryptic JSON/TOML configuration files, and incompatible schema definitions across disparate AI assistants, OmniAgent Manager aggregates your entire AI development fleet into a unified, high-performance control plane.

---

## 📑 Table of Contents

- [The Problem OmniAgent Manager Solves](#-the-problem-omniagent-manager-solves)
- [Core Architectural Pillars & Technical Benefits](#-core-architectural-pillars--technical-benefits)
- [Feature Deep-Dive](#-feature-deep-dive)
  - [1. Universal AI Models & Providers Dashboard](#1-universal-ai-models--providers-dashboard)
  - [2. Intelligent Skills Lifecycle Hub](#2-intelligent-skills-lifecycle-hub)
  - [3. Granular MCP Tool Server Management](#3-granular-mcp-tool-server-management)
  - [4. Deep Agent Filesystem Explorer (20 Categories, 150+ Paths)](#4-deep-agent-filesystem-explorer-20-categories-150-paths)
  - [5. Automated Safety, AST Validation & Atomic Backups](#5-automated-safety-ast-validation--atomic-backups)
  - [6. High-Visibility TUI & Classic Headless Fallback](#6-high-visibility-tui--classic-headless-fallback)
- [Supported AI Agents & Runtimes](#-supported-ai-agents--runtimes)
- [Installation & Setup](#-installation--setup)
  - [Method 1: Global Pip Installation (Recommended)](#method-1-global-pip-installation-recommended)
  - [Method 2: Standalone Windows Batch Launcher (Auto-Elevating)](#method-2-standalone-windows-batch-launcher-auto-elevating)
  - [Method 3: Direct Git Clone & Run](#method-3-direct-git-clone--run)
- [CLI Reference & Command Flags](#-cli-reference--command-flags)
- [Keyboard Navigation & Shortcuts](#-keyboard-navigation--shortcuts)
- [Configuration Protocols & Safe Writing](#-configuration-protocols--safe-writing)
- [Directory Layout](#-directory-layout)
- [Contributing & Development](#-contributing--development)
- [License](#-license)

---

## 💡 The Problem OmniAgent Manager Solves

Developers today rarely use only one AI coding assistant. A typical high-performance engineering workflow often combines:
- **Claude Code CLI** for rapid terminal scaffolding and deep git integration.
- **Google Antigravity** for complex autonomous multi-agent pipelines and workflows.
- **OpenCode AI & Codex** for local and open-source models.
- **Cursor IDE, Windsurf, & VS Code / Cline** for in-editor copilot completions and file editing.
- **Nous Hermes, Aider, and custom LLM runtimes** for local privacy-first offline coding.

### The Pain Points:
1. **Configuration Fragmentation**: Every tool enforces a different configuration schema (`claude.json`, `opencode.json`, `mcp.json`, `config.toml`, `settings.json`) in arbitrary directories (`~/.claude`, `%USERPROFILE%\.gemini\antigravity`, `%APPDATA%\Cursor`, `%USERPROFILE%\.opencode`).
2. **Model Swapping Overhead**: Switching between DeepSeek-R1, Claude 3.5 Sonnet, GPT-4o, and local Ollama/vLLM endpoints requires editing multiple distinct config files, copy-pasting API keys, and risking typos.
3. **Skill & Tool Isolation**: A skill authored for Claude or Antigravity remains trapped in that tool's private stash rather than shared universally across all agent runtimes.
4. **Fragile MCP Integration**: Disabling a malfunctioning MCP server often requires manual JSON editing; a single missing comma breaks the agent's initialization entirely.
5. **No Unified Latency/Health Benchmarking**: Developers cannot easily verify whether a remote provider API or local LLM engine is responsive without manually sending curl requests.

OmniAgent Manager eliminates these friction points by providing **one single source of truth** with automated synchronization, schema validation, and atomic backups.

---

## 🏛️ Core Architectural Pillars & Technical Benefits

| Technical Benefit | Real-World Impact | How OmniAgent Manager Delivers It |
|---|---|---|
| **Zero-Friction Model Swapping** | Instant pivot between reasoning, coding, and fast frontier models | Normalizes model definitions across 11 agents; switches active model in one keystroke |
| **Universal 1-Click Broadcast** | Instant fleet-wide credential & endpoint synchronization | Pushes API key, endpoint base URL, and model identifier to all detected agents simultaneously |
| **Prevent Config Corruption** | Zero risk of broken JSON/TOML crashing your AI agents | Generates timestamped `.bak` files before any write; verifies AST/JSON integrity |
| **Cross-Platform Portability** | Works identically across developer machines without path errors | Pure dynamic path resolution (`USERPROFILE`, `HOME`, relative project discovery); zero hardcoded paths |
| **Universal Tool Access** | Reuse high-value agent skills and MCPs across the entire fleet | Scans and bridges skill stashes across Claude, Antigravity, OpenCode, and Cursor |
| **Live Endpoint Diagnostics** | Immediate diagnosis of API timeouts or authentication errors | Built-in HTTP/REST socket probe verifies model provider latency in real time |
| **Multi-Modal Execution** | Operates equally well on desktop workstations and remote headless servers | Full-featured Rich/Textual TUI with auto-fallback to ANSI CLI for SSH sessions |
| **Global Shell Integration** | Run anywhere on the system via pip binary | Registered `omni-agent` console script available directly in Windows PATH / Linux shell |

---

## ⚡ Feature Deep-Dive

### 1. Universal AI Models & Providers Dashboard
- **Comprehensive Agent Detection**: Automatically scans your system for active installations and config files of 11+ AI coding agents.
- **Provider Aggregator**: Manage cloud providers (OpenRouter, DeepSeek, Anthropic, OpenAI, Groq, Mistral) and local inference servers (Ollama, LM Studio, vLLM, LocalAI).
- **Fleet-Wide Broadcast**: Update endpoint URLs and credentials in one place; OmniAgent Manager translates the configuration to every agent's native format.
- **Model Toggling & Active Selection**: Maintain active and standby models. Toggle availability per agent without deleting underlying configuration definitions.
- **Latency Ping Utility**: Built-in endpoint health check computes round-trip latency to guarantee your provider is operational before launching agent workflows.

### 2. Intelligent Skills Lifecycle Hub
- **Unified Skill Discovery**: Recursively indexes installed skills from global directories, agent-specific repositories, and project-local directories.
- **Active vs. Stashed State Management**: Safely disable skills without deleting them by moving them into an isolated `.stashed_skills` vault.
- **Cursor-Anchored Interaction**: Toggle individual skills using `Space` or `Enter` without the table jumping to the first line.
- **Real-Time Substring Filtering**: Instantly find specific capabilities across hundreds of installed skills.
- **Batch Deployment**: One-click actions to stash all skills or activate all skills across selected agent directories.

### 3. Granular MCP Tool Server Management
- **Universal Schema Parser**: Normalizes MCP configurations across Claude Desktop, Claude Code, Google Antigravity, Cursor, and OpenCode.
- **Per-Server Enable/Disable**: Toggle individual MCP servers on and off with immediate reflection in the target configuration file.
- **Parameter & Env Inspector**: View environment variables, command binaries, and runtime arguments for each MCP tool server.
- **Safe Dynamic Re-serialization**: Automatically re-indents and formats modified JSON files using standard UTF-8 encodings.

### 4. Deep Agent Filesystem Explorer (20 Categories, 150+ Paths)
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
- 📂 **Open in Explorer**: Launches native Windows Explorer / Finder / file manager directly at the path.
- 📝 **Open in Editor**: Launches your configured editor (VS Code, Cursor, or Notepad) focused on the file.
- 📋 **Copy Path**: Copies clean, absolute path directly to your OS clipboard.
- 💻 **Terminal Here**: Spawns an interactive shell pre-navigated to the target directory.

### 5. Automated Safety, AST Validation & Atomic Backups
- **Automatic `.bak` Snapshots**: Every write operation creates a timestamped backup before touching target files.
- **Atomic File Swapping**: Configuration files are written to a temporary sibling file and renamed atomically to prevent partial writes during unexpected shutdowns.
- **Syntax Pre-Validation**: Validates JSON and TOML structures before saving to prevent corrupting active agent configurations.
- **Non-Destructive Restoration**: If an external configuration is malformed, OmniAgent Manager preserves the original data and issues a clear diagnostic warning.

### 6. High-Visibility TUI & Classic Headless Fallback
- **Modern Desktop TUI**: Built with Textual and Rich, featuring dual-pane layouts, responsive data tables, modal dialogs, and status bars.
- **Dynamic Theming Engine**: Switch instantly between 9 palettes (`GitHub Dark`, `OLED Black & White`, `Hacker Green`, `Tokyo Night`, `Catppuccin Mocha`, `Nord Frost`, `Dracula`, `Gruvbox`, `Monokai`).
- **Classic ANSI CLI Fallback**: When run over minimal SSH connections or environments without full TUI capability, automatically provides an interactive ANSI menu interface.

---

## 🤖 Supported AI Agents & Runtimes

| Agent / Runtime | Detected Config Formats | Models | Skills | MCPs | Explorer Support |
|---|:---:|:---:|:---:|:---:|:---:|
| **Google Antigravity** | JSON / YAML / MD | ✅ | ✅ | ✅ | ✅ |
| **Claude Code CLI** | JSON / Markdown | ✅ | ✅ | ✅ | ✅ |
| **OpenCode AI** | JSON / TS | ✅ | ✅ | ✅ | ✅ |
| **Cursor IDE** | JSON / MDC / Rules | ✅ | ✅ | ✅ | ✅ |
| **VS Code & Cline** | JSON / Settings | ✅ | ✅ | ✅ | ✅ |
| **GitHub Copilot CLI** | YAML / JSON | ✅ | ✅ | ✅ | ✅ |
| **OpenAI Codex CLI** | TOML / JSON | ✅ | ✅ | ✅ | ✅ |
| **Nous Hermes** | JSON / YAML | ✅ | ✅ | ✅ | ✅ |
| **Pi Coding Agent** | JSON / Markdown | ✅ | ✅ | ✅ | ✅ |
| **Claude Desktop** | JSON (`claude_desktop_config.json`) | — | — | ✅ | ✅ |
| **Local LLM Runtimes** | Ollama / LM Studio / vLLM | ✅ | — | — | ✅ |

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
OmniAgent Manager v3.5.0 - Universal AI Agent Control Hub

Usage:
  omni-agent [OPTIONS]
  omni-agent-manager [OPTIONS]
  python omni_agent_manager.py [OPTIONS]
  omni_agent_manager.bat [OPTIONS]

Options:
  -h, --help            Display help reference and exit
  -v, --version         Display version details and exit
  --classic, --cli      Run in minimal ANSI terminal menu mode (ideal for SSH)
  --folders, --explorer Launch directly into 20-Category Folder Explorer
  --theme THEME         Launch with specified UI theme (e.g. github_dark, matrix_green)
  --no-admin            Skip Windows UAC elevation check
```

---

## 🕹️ Keyboard Navigation & Shortcuts

| Key | Context | Action |
|:---:|:---|:---|
| `Space` | Skills / MCPs / Models | **Toggle selected item** in-place (no cursor jumping) |
| `Enter` | Any Table | **Select / Apply** active model or execute primary action |
| `↑` / `↓` | Data Tables | Navigate through rows smoothly |
| `T` | Global | Open **Theme & Palette Selector** modal |
| `M` | Global | Switch to **AI Models & Providers** tab |
| `S` | Global | Switch to **Skills Lifecycle** tab |
| `C` | Global | Switch to **MCP Tool Servers** tab |
| `F` | Global | Switch to **20-Category Agent Explorer** tab |
| `P` | Models Tab | Run **Real-Time Ping Test** on active provider endpoint |
| `R` | Global | **Refresh** all agent runtimes, skills, and configs from disk |
| `Q` | Global | **Quit** application cleanly |

---

## 🛡️ Configuration Protocols & Safe Writing

1. **Backup Protocol**: Prior to altering any configuration file (`.json`, `.toml`, `.yaml`), a sibling backup file is created:
   ```
   config.json -> config.json.20260917_102000.bak
   ```
2. **Schema Sanitization**: JSON files are parsed and checked for syntax correctness. Formatting is standardized with 2-space indentation and UTF-8 encoding.
3. **Skill Stashing Protocol**: When a skill is disabled, its folder is cleanly transferred into `.stashed_skills/` within the same directory tree. Restoring the skill re-integrates it into the active search path instantly.

---

## 📂 Directory Layout

```
omni-agent-manager/
├── omni_agent_manager.py     # Complete standalone core engine (TUI, CLI, Models, Skills, MCPs, Catalog)
├── omni_agent_manager.bat    # Windows launcher with robust UAC elevation handling
├── pyproject.toml            # PEP 517/621 packaging (registers omni-agent & omni-agent-manager)
├── setup.py                  # Backward-compatible setuptools build script
├── requirements.txt          # Production dependencies (Textual, Rich)
├── LICENSE                   # MIT Open Source License
├── .gitignore                # Clean development gitignore
└── README.md                 # Technical architecture and user guide
```

---

## 🤝 Contributing & Development

Contributions are welcome! Please follow these development standards:
1. **Zero Unnecessary Dependencies**: Keep external runtime requirements strictly limited to `textual` and `rich`.
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
