import os
import subprocess
from abc import ABC, abstractmethod
from omni_core.paths import normalize_path, find_executable, USERPROFILE, APPDATA, LOCALAPPDATA

# Standard capability state flags
CAP_SUPPORTED = "SUPPORTED"
CAP_READ_ONLY = "READ_ONLY"
CAP_EDITABLE = "EDITABLE"
CAP_UNSUPPORTED = "UNSUPPORTED"
CAP_UNKNOWN = "UNKNOWN"
CAP_MANUAL_SETUP = "MANUAL_SETUP"

class BaseAgentAdapter(ABC):
    """Abstract base class for native AI coding agent adapters."""
    id: str = "generic"
    name: str = "Generic Agent"
    category: str = "CLI"
    docs_url: str = ""

    def __init__(self, agent_cfg: dict = None):
        self.agent_cfg = agent_cfg or {}

    def get_executable(self) -> str | None:
        cli_name = self.agent_cfg.get("cli_name", self.id)
        return find_cli_executable_cached(cli_name)

    def detect_installed(self) -> bool:
        if self.get_executable():
            return True
        for p in self.get_global_config_paths():
            if os.path.exists(p):
                return True
        return False

    def get_version(self) -> str:
        exe = self.get_executable()
        if not exe:
            return "Not Installed"
        try:
            out = subprocess.check_output(
                [exe, "--version"],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=3.0
            ).strip()
            return out.splitlines()[0] if out else "Installed"
        except Exception:
            return "Installed (version query unsupported)"

    @abstractmethod
    def get_global_config_paths(self) -> list[str]:
        pass

    @abstractmethod
    def discover_project_instructions(self, project_path: str) -> list[dict]:
        pass

    @abstractmethod
    def discover_project_configs(self, project_path: str) -> list[dict]:
        pass

    def discover_skills(self, project_path: str = None) -> list[dict]:
        skills = []
        # Global skills
        g_skills_dir = self.agent_cfg.get("skills_dir")
        if g_skills_dir and os.path.isdir(g_skills_dir):
            for item in os.listdir(g_skills_dir):
                sp = os.path.join(g_skills_dir, item)
                if os.path.isdir(sp):
                    skills.append({"id": item, "scope": "global", "path": sp, "agent": self.id})
        # Project skills
        if project_path:
            p_norm = normalize_path(project_path)
            for sub in [".claude/skills", ".gemini/skills", "skills", ".skills"]:
                cand = os.path.join(p_norm, sub)
                if os.path.isdir(cand):
                    for item in os.listdir(cand):
                        sp = os.path.join(cand, item)
                        if os.path.isdir(sp):
                            skills.append({"id": item, "scope": "project", "path": sp, "agent": self.id})
        return skills

    def discover_mcp(self, project_path: str = None) -> list[dict]:
        mcps = []
        # Global MCP
        g_mcp = self.agent_cfg.get("mcp_file")
        if g_mcp and os.path.isfile(g_mcp):
            mcps.append({"scope": "global", "path": g_mcp, "agent": self.id})
        # Project MCP
        if project_path:
            p_norm = normalize_path(project_path)
            for mname in ["mcp.json", ".mcp.json", ".claude/mcp.json", ".cursor/mcp.json"]:
                mp = os.path.join(p_norm, mname)
                if os.path.isfile(mp):
                    mcps.append({"scope": "project", "path": mp, "agent": self.id})
        return mcps

    def construct_launch_cmd(self, project_path: str, profile: dict = None) -> list[str]:
        exe = self.get_executable() or self.id
        cmd = [exe]
        if profile and profile.get("extra_args"):
            extra = profile["extra_args"]
            if isinstance(extra, list):
                cmd.extend(extra)
            elif isinstance(extra, str):
                cmd.extend(extra.split())
        return cmd

    def get_capabilities(self) -> dict[str, str]:
        return {
            "project_instructions": CAP_SUPPORTED,
            "project_skills": CAP_SUPPORTED,
            "project_mcp": CAP_SUPPORTED,
            "model_routing": CAP_SUPPORTED,
            "subagents": CAP_SUPPORTED,
            "hooks": CAP_SUPPORTED,
            "launch_directory": CAP_SUPPORTED
        }

_EXE_CACHE: dict[str, str | None] = {}
def find_cli_executable_cached(name: str) -> str | None:
    if name not in _EXE_CACHE:
        _EXE_CACHE[name] = find_executable(name)
    return _EXE_CACHE[name]

# ----------------- Concrete Agent Adapters -----------------

class ClaudeCodeAdapter(BaseAgentAdapter):
    id = "claude"
    name = "Claude Code CLI"
    category = "Terminal CLI"
    docs_url = "https://docs.anthropic.com/en/docs/agents-and-tools/claude-code"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".claude"),
            os.path.join(USERPROFILE, ".claude.json"),
            os.path.join(USERPROFILE, ".claude", "settings.json"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        instructions = []
        for f in ["CLAUDE.md", "CLAUDE.local.md"]:
            p = os.path.join(norm, f)
            if os.path.isfile(p):
                instructions.append({"name": f, "path": p, "agent": self.id, "active": True})
        return instructions

    def discover_project_configs(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        configs = []
        claude_dir = os.path.join(norm, ".claude")
        if os.path.isdir(claude_dir):
            configs.append({"name": ".claude", "path": claude_dir, "type": "directory"})
        for mf in ["mcp.json", ".mcp.json"]:
            p = os.path.join(norm, mf)
            if os.path.isfile(p):
                configs.append({"name": mf, "path": p, "type": "mcp"})
        return configs

class CodexAdapter(BaseAgentAdapter):
    id = "codex"
    name = "OpenAI Codex CLI"
    category = "Terminal CLI"
    docs_url = "https://github.com/openai/codex"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".codex"),
            os.path.join(USERPROFILE, ".codex", "config.json"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, "AGENTS.md")
        if os.path.isfile(p):
            res.append({"name": "AGENTS.md", "path": p, "agent": self.id, "active": True})
        return res

    def discover_project_configs(self, project_path: str) -> list[dict]:
        return []

class GeminiAdapter(BaseAgentAdapter):
    id = "antigravity"
    name = "Google Antigravity / Gemini CLI"
    category = "Autonomous IDE & CLI"
    docs_url = "https://gemini.google.com"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".gemini"),
            os.path.join(USERPROFILE, ".gemini", "antigravity"),
            os.path.join(USERPROFILE, ".gemini", "config", "mcp_config.json"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, "GEMINI.md")
        if os.path.isfile(p):
            res.append({"name": "GEMINI.md", "path": p, "agent": self.id, "active": True})
        return res

    def discover_project_configs(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        g_dir = os.path.join(norm, ".gemini")
        if os.path.isdir(g_dir):
            res.append({"name": ".gemini", "path": g_dir, "type": "directory"})
        return res

class OpenCodeAdapter(BaseAgentAdapter):
    id = "opencode"
    name = "OpenCode AI"
    category = "Interpreter CLI"
    docs_url = "https://github.com/opencode"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".config", "opencode"),
            os.path.join(USERPROFILE, ".config", "opencode", "opencode.json"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        for f in ["AGENTS.md", "README.md"]:
            p = os.path.join(norm, f)
            if os.path.isfile(p):
                res.append({"name": f, "path": p, "agent": self.id, "active": True})
        return res

    def discover_project_configs(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, "opencode.json")
        if os.path.isfile(p):
            res.append({"name": "opencode.json", "path": p, "type": "config"})
        return res

class AiderAdapter(BaseAgentAdapter):
    id = "aider"
    name = "Aider AI Pair Programmer"
    category = "Terminal CLI"
    docs_url = "https://aider.chat"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".aider.conf.yml"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        for f in ["CONVENTIONS.md", ".cursorrules"]:
            p = os.path.join(norm, f)
            if os.path.isfile(p):
                res.append({"name": f, "path": p, "agent": self.id, "active": True})
        return res

    def discover_project_configs(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, ".aider.conf.yml")
        if os.path.isfile(p):
            res.append({"name": ".aider.conf.yml", "path": p, "type": "config"})
        return res

class CursorAdapter(BaseAgentAdapter):
    id = "cursor"
    name = "Cursor AI IDE"
    category = "Desktop IDE"
    docs_url = "https://cursor.com"

    def get_global_config_paths(self) -> list[str]:
        return [
            os.path.join(USERPROFILE, ".cursor"),
            os.path.join(APPDATA, "Cursor", "User", "settings.json"),
        ]

    def discover_project_instructions(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, ".cursorrules")
        if os.path.isfile(p):
            res.append({"name": ".cursorrules", "path": p, "agent": self.id, "active": True})
        return res

    def discover_project_configs(self, project_path: str) -> list[dict]:
        norm = normalize_path(project_path)
        res = []
        p = os.path.join(norm, ".cursor")
        if os.path.isdir(p):
            res.append({"name": ".cursor", "path": p, "type": "directory"})
        return res

    def construct_launch_cmd(self, project_path: str, profile: dict = None) -> list[str]:
        exe = self.get_executable() or "cursor"
        return [exe, normalize_path(project_path)]

class GenericAdapter(BaseAgentAdapter):
    def get_global_config_paths(self) -> list[str]:
        return []
    def discover_project_instructions(self, project_path: str) -> list[dict]:
        return []
    def discover_project_configs(self, project_path: str) -> list[dict]:
        return []

# Factory and Registry
_ADAPTERS: dict[str, type[BaseAgentAdapter]] = {
    "claude": ClaudeCodeAdapter,
    "codex": CodexAdapter,
    "antigravity": GeminiAdapter,
    "opencode": OpenCodeAdapter,
    "aider": AiderAdapter,
    "cursor": CursorAdapter,
}

def get_adapter(agent_id: str, agent_cfg: dict = None) -> BaseAgentAdapter:
    """Instantiates the specialized adapter for agent_id or GenericAdapter."""
    cls = _ADAPTERS.get(agent_id, GenericAdapter)
    adapter = cls(agent_cfg=agent_cfg)
    adapter.id = agent_id
    if agent_cfg and agent_cfg.get("name"):
        adapter.name = agent_cfg["name"]
    return adapter

def get_all_adapters(fleet_agents: dict = None) -> dict[str, BaseAgentAdapter]:
    """Returns instantiated adapters for all known or discovered agents."""
    res = {}
    fleet = fleet_agents or {}
    for aid in list(_ADAPTERS.keys()) + list(fleet.keys()):
        if aid not in res:
            res[aid] = get_adapter(aid, fleet.get(aid))
    return res
