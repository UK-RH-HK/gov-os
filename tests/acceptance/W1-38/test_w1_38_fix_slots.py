"""W1-38 (DAEO-3ef2) fix F11: no unfilled template slot in a generated agent file.

Generation fills or drops every slot (``{CMD:retrieve}``, ``{ID}``, ``{STEP:x}``), and the portability check
refuses a generated file that holds one."""

from __future__ import annotations

import json
import re

import pytest

import w1_38_support as support

REPO = support.REPO_ROOT
SLOT = re.compile(r"(?<!\$)\{(?:(?:CMD|STEP):[A-Za-z_]+|[A-Z][A-Z0-9_]*)\}")


def slots(path):
    return sorted(set(SLOT.findall(path.read_text(encoding="utf-8"))))


@pytest.mark.needs_rulesync
def test_generation_into_a_planted_tree_leaves_no_slot_in_any_agent_file(tmp_path, rulesync_bin):
    project = tmp_path / "p"
    project.mkdir()
    support.build_project_from_template(project)
    done = support.run_rulesync_generate(project)
    assert done.returncode == 0, done.stderr
    agents = sorted((project / ".claude/agents").glob("*.md"))
    assert agents
    held = {a.name: slots(a) for a in agents if slots(a)}
    assert not held, f"unfilled slots in generated agent files: {held}"


@pytest.mark.needs_rulesync
def test_the_portability_check_refuses_a_generated_file_holding_a_slot_and_names_it(tmp_path, rulesync_bin):
    project = tmp_path / "p"
    project.mkdir()
    support.build_project_from_template(project)
    support.regenerate(project)
    target = project / ".claude/agents/engineer.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nRead {CMD:retrieve} first.\n", encoding="utf-8")
    done = support.run_portability_check(project)
    assert done.returncode != 0
    named = [f for f in support.printed_findings(done)
             if re.search(r"SLOT|PLACEHOLDER", f.get("code", ""), re.I) and f.get("file") == ".claude/agents/engineer.md"]
    assert named, f"no finding names the slot and the file: {done.stdout[:600]}"
    assert "{CMD:retrieve}" in json.dumps(named)


def test_the_checked_in_agent_files_and_the_kits_copies_hold_no_slot():
    files = [p for pattern in (".claude/agents/*.md", ".rulesync/subagents/*.md", "template/.rulesync/subagents/*.md",
                               "template/.claude/agents/*.md", "src/gov/_shipped/template/.rulesync/subagents/*.md",
                               "src/gov/_shipped/template/.claude/agents/*.md")
             for p in REPO.glob(pattern)]
    assert files
    held = {str(p.relative_to(REPO)): slots(p) for p in files if slots(p)}
    assert not held, f"unfilled slots: {held}"
