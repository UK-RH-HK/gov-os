"""W2-201 R1 (DEC-1225): the role files, their copies and the rubric's files carry the new table.

The per-role, per-class table is S1's (``test_w2_201_s1_role_files.py``, revised: ``w2_201_support.TABLE``: Opus, high for
``orchestrator`` and ``senior-engineer``; Sonnet, high and no ``Launch by criticality`` line for the seven others).
These cases are the rest of R1: the scan for the two models, the auditor's ``Model tier`` line, the version bumps, the
copies equal to the kernel files, ``criticality.yaml``'s comments, audit 4's Table 3 and the portability check.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest
import yaml

import w2_201_support as k

REPO = k.REPO_ROOT
FOLDERS = (k.ROLES_REL,) + k.COPY_FOLDERS
ROLE_NAMES = sorted(k.TABLE)
AUDIT_4 = REPO / "docs/emergency-2/audits/04-tickets-and-rubric.md"
# the four role files whose Launch lines change (the other five carry the same lines as before), and their versions
# after the change: one minor above the base's (engineer 1.1.0, independent-test-designer 1.1.0, independent-auditor
# 1.1.0, qa-engineer 1.0.0)
BUMPED = {"engineer": "1.2.0", "independent-test-designer": "1.2.0", "independent-auditor": "1.2.0",
          "qa-engineer": "1.1.0"}
MODEL_IDS = ("claude-opus-5-5", "claude-haiku-5-5")


def _lines(location, role):
    return (REPO / location / f"{role}.md").read_text(encoding="utf-8").splitlines()


def _line(location, role, head):
    found = [line for line in _lines(location, role) if line.startswith(head)]
    assert len(found) <= 1, f"{location}/{role}.md holds {head} {len(found)} times"
    return found[0] if found else None


@pytest.mark.parametrize("role", ROLE_NAMES)
@pytest.mark.parametrize("location", FOLDERS)
def test_r1_the_opus_and_haiku_model_ids_are_left_only_in_the_two_opus_roles_default_line(location, role):
    """The scan of the kernel role files and the three copy folders: ``claude-opus-5-5`` and ``claude-haiku-5-5`` appear
    only on the ``Launch default`` line of ``orchestrator`` and ``senior-engineer`` (and nowhere in the other seven, a
    table line or a body line included)."""
    found = [(n, line) for n, line in enumerate(_lines(location, role), 1)
             if any(model in line for model in MODEL_IDS)]
    if role in k.OPUS_ROLES:
        want = _line(location, role, "- **Launch default:**")
        assert want is not None and [line for _, line in found] == [want], (
            f"{location}/{role}.md names Opus or Haiku on {found}, not only on its Launch default line")
        assert "claude-opus-5-5" in want and "claude-haiku-5-5" not in want
    else:
        assert found == [], f"{location}/{role}.md names Opus or Haiku (R1 leaves neither): {found}"


def test_r1_criticality_yaml_names_opus_only_in_its_opus_key_and_never_haiku():
    text = (REPO / k.CRITICALITY_REL).read_text(encoding="utf-8")
    hits = [line for line in text.splitlines() if any(model in line for model in MODEL_IDS)]
    assert len(hits) == 1 and re.match(r"^opus:\s*claude-opus-5-5\b", hits[0]), (
        f"{k.CRITICALITY_REL} names Opus or Haiku on {hits}, not only in its `opus` key")
    data = yaml.safe_load(text)
    assert data.get("opus") == "claude-opus-5-5", "the key `opus` stays, for the file's form"


def test_r1_criticality_yaml_s_comments_say_a_class_no_longer_picks_a_model():
    """The file's comments name DEC-1225 and say a class no longer picks a model; its key `opus` is what an
    exceptions entry may cover."""
    comments = " ".join(re.findall(r"#\s*(.*)", (REPO / k.CRITICALITY_REL).read_text(encoding="utf-8"))).lower()
    assert "dec-1225" in comments, f"{k.CRITICALITY_REL}'s comments do not name DEC-1225"
    sentences = [s for s in re.split(r"[.;]", comments) if "class" in s and "model" in s]
    assert any(re.search(r"no longer|not|never|no ", s) for s in sentences), (
        f"{k.CRITICALITY_REL}'s comments do not say a class no longer picks a model: {comments[:600]!r}")
    assert "exception" in comments, f"{k.CRITICALITY_REL}'s comments do not tie `opus` to an exceptions entry"


@pytest.mark.parametrize("location", FOLDERS)
def test_r1_the_auditor_s_model_tier_line_says_an_opus_audit_is_only_the_exceptions_file_s_entry(location):
    line = _line(location, "independent-auditor", "- **Model tier:**")
    assert line is not None, f"{location}/independent-auditor.md has no Model tier line"
    low = line.lower()
    missing = [w for w in ("opus", "dec-1225", "exception", "comprehensive", "owner") if w not in low]
    assert not missing, f"the auditor's Model tier line does not say {missing}: {line!r}"
    assert line != "- **Model tier:** see Launch default"


@pytest.mark.parametrize("role", sorted(BUMPED))
@pytest.mark.parametrize("location", FOLDERS)
def test_r1_each_changed_role_file_goes_up_by_one_minor(location, role):
    line = _line(location, role, "- **Version:**")
    assert line == f"- **Version:** {BUMPED[role]}", f"{location}/{role}.md has {line!r}, not version {BUMPED[role]}"


@pytest.mark.parametrize("role", ROLE_NAMES)
@pytest.mark.parametrize("location", k.COPY_FOLDERS)
def test_r1_a_copy_carries_the_kernel_file_s_launch_lines(location, role):
    """A copy that differs from the kernel file in a Launch line, the version or the Model tier line fails."""
    heads = ("- **Version:**", "- **Launch default:**", "- **Launch by criticality:**", "- **Model tier:**")
    got = [_line(location, role, head) for head in heads]
    want = [_line(k.ROLES_REL, role, head) for head in heads]
    assert got == want, f"{location}/{role}.md differs from the kernel file in its Launch lines:\n{got}\n{want}"


def test_r1_audit_4_table_3_carries_the_table_with_a_note_naming_dec_1225():
    text = AUDIT_4.read_text(encoding="utf-8")
    start = text.index("**Model and effort per role.**")
    end = text.index("**Measured against", start)
    section = text[start:end]
    assert "DEC-1225" in section, "Table 3's model and effort section carries no note naming DEC-1225"
    rows = [row for row in section.splitlines() if row.startswith("|") and not row.startswith("|---")][1:]
    others = [row for row in rows if not row.lower().startswith("| cto")]
    assert rows and any(row.lower().startswith("| cto") and "Opus" in row for row in rows), "no CTO row on Opus"
    leftover = [row for row in others if re.search(r"Opus|Haiku", row)]
    assert not leftover, f"Table 3 still gives Opus or Haiku to a role that is not the CTO or senior engineer: {leftover}"


ROLE_PATHS = (".claude/agents/", ".rulesync/subagents/", "template/.rulesync/subagents/",
              "template/governance/kernel/roles/")


def test_r1_the_portability_check_has_no_finding_on_a_role_file_or_a_copy():
    """``python3 -m gov.adapters.portability`` in this repository (the kernel, the rulesync sources and the generated
    adapters agree): no finding names a role file, a role source or a generated agent. A guard on the base; it turns red
    when a kernel role file changes and a copy is not regenerated.

    Reading: R1 says "the portability check is green on the tree". On the base the check reports one finding that is no
    role file's, ``GENERATED_DIFFERS`` for ``.claude/settings.json`` (the root's settings file holds the helper hook and
    the deny rules that rulesync does not generate from ``.rulesync/``); it is not R1's and is left alone, so this case
    judges the findings that name a role file or its copy."""
    env = {**os.environ, "PYTHONPATH": str(REPO / "src")}
    done = subprocess.run([sys.executable, "-m", "gov.adapters.portability"], cwd=str(REPO), capture_output=True,
                          text=True, timeout=240, env=env)
    report = json.loads(done.stdout) if done.stdout.strip().startswith("{") else None
    assert isinstance(report, dict) and isinstance(report.get("findings"), list), (
        f"the portability check gave no report: exit {done.returncode}\n{done.stdout[-800:]}\n{done.stderr[-800:]}")
    about = [f for f in report["findings"] if str(f.get("file", "")).startswith(ROLE_PATHS)]
    assert about == [], f"the portability check has findings on role files or copies: {about}"
