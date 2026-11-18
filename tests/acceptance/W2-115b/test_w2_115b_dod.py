"""Success line 9: DONE is the green landing itself, a Definition of Done of three lines (README, "Success 9").

The project's files are read from this worktree's own tree; the facts ``gov adopt`` writes by default are read from a
planted repository after ``gov adopt --facts``.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import yaml

import w2_115b_support as support

ROOT = support.REPO_ROOT
FACTS_REL = "governance/project/facts.yaml"
KERNEL_TEMPLATES = ROOT / "template/governance/kernel/templates"
CLAUDE_TEMPLATES = ROOT / ".claude/templates"
GENERATED = (".claude/templates", "src/gov/_shipped/template/governance/kernel/templates",
             "template/.rulesync/subagents", ".rulesync/subagents", ".claude/agents")
DROPPED = re.compile(r"DOD-[456](?!\d)|DOD-1 to DOD-6")
THREE = ["DOD-1", "DOD-2", "DOD-3"]


def assert_three_lines(data, where):
    dod = (data or {}).get("dod")
    assert isinstance(dod, list), f"{where}: no dod list"
    ids = [entry.get("id") for entry in dod]
    assert ids == THREE, f"{where}: the dod holds {ids}, not exactly {THREE}"
    lines = {entry["id"]: str(entry.get("line") or "") for entry in dod}
    assert "gov accept" in lines["DOD-1"] or "{CMD:accept}" in lines["DOD-1"], f"{where} DOD-1: {lines['DOD-1']}"
    assert "gov queue" in lines["DOD-2"], f"{where} DOD-2 does not name gov queue: {lines['DOD-2']}"
    assert re.search(r"\bclose", lines["DOD-3"], re.I), f"{where} DOD-3 does not name the close: {lines['DOD-3']}"


def test_the_project_s_facts_hold_exactly_three_dod_lines():
    data = yaml.safe_load((ROOT / FACTS_REL).read_text(encoding="utf-8"))
    assert_three_lines(data, FACTS_REL)


def test_the_facts_gov_adopt_writes_hold_exactly_three_dod_lines(tmp_path):
    project = tmp_path / "project"
    (project / ".tickets").mkdir(parents=True)
    (project / "README.md").write_text("# An adopted project\n", encoding="utf-8")
    support.git(project, "init", "-q", "-b", "main")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "adopt", "--facts", "--root", str(project), "--json"],
                          cwd=str(project), env=support.base_env(tmp_path / "env"), capture_output=True, text=True,
                          timeout=300, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gov adopt --facts: exit {done.returncode}\n{done.stdout}\n{done.stderr}"
    assert json.loads(done.stdout).get("ok") is True
    written = project / FACTS_REL
    assert written.is_file(), f"gov adopt --facts wrote no {FACTS_REL}"
    assert_three_lines(yaml.safe_load(written.read_text(encoding="utf-8")), "the facts gov adopt writes")


def test_no_kernel_template_or_generated_copy_quotes_the_dropped_lines():
    assert KERNEL_TEMPLATES.is_dir() and any(KERNEL_TEMPLATES.glob("*.md")), "no kernel templates"
    found = []
    for folder in (KERNEL_TEMPLATES, *(ROOT / rel for rel in GENERATED)):
        for path in sorted(folder.rglob("*")) if folder.is_dir() else []:
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if DROPPED.search(line):
                    found.append(f"{path.relative_to(ROOT)}:{n}: {line.strip()[:160]}")
    assert found == [], "DOD-4, DOD-5, DOD-6 or 'DOD-1 to DOD-6' still quoted:\n" + "\n".join(found)


def test_the_ticket_template_s_done_when_is_the_three_ids():
    text = (KERNEL_TEMPLATES / "ticket.md").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.startswith("done_when:")]
    assert len(lines) == 1, f"the ticket template has {len(lines)} done_when line(s)"
    value = lines[0].split(":", 1)[1].split("#", 1)[0].strip()
    assert value == "[DOD-1, DOD-2, DOD-3]", f"done_when is {value}"


def test_each_claude_templates_copy_is_its_kernel_template_with_three_lines():
    copies = sorted(CLAUDE_TEMPLATES.glob("*.md"))
    assert copies, "no .claude/templates/ copies"
    for copy in copies:
        kernel = KERNEL_TEMPLATES / copy.name
        assert kernel.is_file(), f"{copy.name}: no kernel template of that name"
        assert copy.read_bytes() == kernel.read_bytes(), f".claude/templates/{copy.name} is not its kernel template"
        assert not DROPPED.search(copy.read_text(encoding="utf-8")), f".claude/templates/{copy.name} quotes DOD-4..6"
