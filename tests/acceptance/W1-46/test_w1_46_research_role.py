"""W1-46 -- the minimal research role: its role file and its roster entry.

KPI success 5 [CAP-22.d]: "A minimal research role is in the Wave 1 roster: a
role file with purpose, allowed-path pattern, tools, model tier, authority level
and handoff format, plus its roster entry; a research or experiment session runs
as GOV_ROLE=research; the guard knows the role and holds its writes to its
ticket's allowed_paths (its experiment folder); its network grant comes from the
launcher's profile, the research allowlist of DEC-158, not from the guard
(DEC-163)".

KPI success 8 [CAP-58.d], the file-tool half: "a file-tool write outside it is
refused by the permission rules and the guard".

The guard is asked through the PreToolUse commands the committed settings
register, run through the shell as the harness runs them. No call is made.

Rewrite-Reason: EMERGENCY-2 6.1 (the guard / the sandbox retired), DAEO-gr7t. The cases that asked the kernel's guard
for the research role's writes, scratch and network are deleted with the guard; the role file and the roster entry
stay.
"""

from __future__ import annotations

import re

import pytest
import yaml

import w1_46_support as support

RESEARCH = support.RESEARCH
FOLDER = support.EXPERIMENT_REL

# The six parts the KPI names, as a role file would word them.
ROLE_FILE_PARTS = {
    "purpose": r"purpose",
    "allowed-path pattern": r"allowed[\s_-]*paths?",
    "tools": r"tools",
    "model tier": r"model[\s_-]*tier",
    "authority level": r"authority",
    "handoff format": r"hand[\s_-]?off",
}


# --------------------------------------------------------------------------
# The role file and the roster entry (committed files of this repository)
# --------------------------------------------------------------------------

def _role_files():
    files = [path for path in sorted(support.REPO_ROOT.glob(support.KERNEL_ROLE_GLOB)) if path.is_file()]
    agent = support.REPO_ROOT / support.AGENT_REL
    return files + ([agent] if agent.is_file() else [])


def test_the_research_role_has_a_role_file():
    assert _role_files(), f"there is no research role file ({support.KERNEL_ROLE_GLOB} or {support.AGENT_REL})"


def test_the_role_file_states_the_six_parts_the_kpi_names():
    files = _role_files()
    assert files, "there is no research role file"
    missing = {}
    for path in files:
        text = path.read_text(encoding="utf-8")
        missing[path.relative_to(support.REPO_ROOT).as_posix()] = [part for part, pattern in ROLE_FILE_PARTS.items()
                              if not re.search(pattern, text, re.IGNORECASE)]
    assert any(not parts for parts in missing.values()), f"no research role file states all six parts: {missing}"


def test_the_research_role_is_a_session_role_definition_like_the_others():
    """``.claude/agents/research.md`` with the frontmatter of the five existing definitions (W1-05)."""
    path = support.REPO_ROOT / support.AGENT_REL
    assert path.is_file(), f"{support.AGENT_REL} does not exist"
    meta = support.live_support.frontmatter(path.read_text(encoding="utf-8"))
    assert meta and meta.get("name") == RESEARCH, f"{support.AGENT_REL} does not declare name: research ({meta})"
    assert str(meta.get("description", "")).strip(), f"{support.AGENT_REL} has no description"


def _names_research(value):
    if isinstance(value, dict):
        return any(key == RESEARCH or _names_research(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_names_research(item) for item in value)
    return value == RESEARCH


def test_the_roster_has_an_entry_for_the_research_role():
    path = support.REPO_ROOT / support.ROSTER_REL
    assert path.is_file(), f"{support.ROSTER_REL} does not exist"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, (dict, list)) and _names_research(data), (
        f"{support.ROSTER_REL} has no entry whose key or value is the role name `research`"
    )
