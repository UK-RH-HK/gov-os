"""F1: a kit file that names the guard, the sandbox or a permission prompt as in force fails the adapter check by name
(``KIT_TEXT_GUARD_IN_FORCE``, naming the file and the line, a non-zero exit); a line that says they are retired is no
finding, and the shipped head and skill give none (DEC-1217 (6); EMERGENCY-2 2.2)."""

from __future__ import annotations

import json

import pytest

import w2_208_support as support

# id -> the lines appended to the shipped head (after one blank line), and the offsets among them a finding may name
IN_FORCE = {
    "under-the-guard": (["Six roles operate under the guard:"], {0}),
    "guard-section": (["## Guard", "", "The guard enforces allowed paths, tool restrictions and permission classes."],
                      {0, 2}),
    "inside-the-sandbox": (["Every agent session runs inside the sandbox."], {0}),
    "permission-prompt": (["When a command reaches outside the repository, a permission prompt appears."], {0}),
}
RETIRED = ["No guard, no sandbox, no permission prompts.", "The guard is retired; the sandbox is retired too."]

CALL = ("import json\nfrom pathlib import Path\nfrom gov.adapters.portability import kit_text_findings\n"
        "print(json.dumps(kit_text_findings(Path.cwd())))\n")


def kit_text_findings(project, sandbox):
    done = support.python(project, sandbox, CALL)
    assert done.returncode == 0, f"gov.adapters.portability.kit_text_findings(root) could not be called\n" \
                                 f"{done.describe()}"
    found = json.loads(done.stdout)
    assert isinstance(found, list), f"kit_text_findings returned {found!r}, not a list of findings"
    return found


def _rel(project, name):
    name = str(name or "")
    return name[len(str(project)) + 1:] if name.startswith(str(project) + "/") else name.removeprefix("./")


def _ours(project, findings, rel):
    return [item for item in findings if isinstance(item, dict) and item.get("code") == support.KIT_TEXT
            and _rel(project, item.get("file")) == rel]


def _append(project, rel, lines):
    """Append ``lines`` after one blank line; the 1-based line number of the first of them."""
    path = project / rel
    text = path.read_text(encoding="utf-8").rstrip("\n") + "\n"
    first = text.count("\n") + 2
    path.write_text(text + "\n" + "".join(f"{line}\n" for line in lines), encoding="utf-8")
    return first


@pytest.mark.parametrize("case", sorted(IN_FORCE))
def test_f1_a_head_naming_the_guard_sandbox_or_prompt_in_force_is_a_finding_by_name(tmp_path, sandbox, case):
    lines, offsets = IN_FORCE[case]
    project = support.template_project(tmp_path / "product")
    first = _append(project, support.HEAD_REL, lines)
    expected = {first + offset for offset in offsets}
    ours = _ours(project, kit_text_findings(project, sandbox), support.HEAD_REL)
    assert ours and {item.get("line") for item in ours} <= expected, (
        f"kit_text_findings gives no {support.KIT_TEXT} for {support.HEAD_REL} at line(s) {sorted(expected)}: {ours}")
    checked, findings = support.portability(project, sandbox)
    assert checked.returncode != 0, f"the adapter check exits 0 although the head names the guard\n{checked.describe()}"
    ours = _ours(project, findings or [], support.HEAD_REL)
    assert ours and {item.get("line") for item in ours} <= expected, (
        f"the adapter check prints no {support.KIT_TEXT} naming {support.HEAD_REL} and line(s) {sorted(expected)}\n"
        f"{checked.describe()}")


def test_f1_the_kernel_copy_of_the_skill_is_in_the_checked_files(tmp_path, sandbox):
    project = support.template_project(tmp_path / "product")
    line = _append(project, support.SKILL_KERNEL_REL, ["Every agent session runs inside the sandbox."])
    ours = _ours(project, kit_text_findings(project, sandbox), support.SKILL_KERNEL_REL)
    assert [item.get("line") for item in ours] == [line], (
        f"no {support.KIT_TEXT} names {support.SKILL_KERNEL_REL} at line {line}: {ours}")


def test_f1_a_line_saying_they_are_retired_is_no_finding(tmp_path, sandbox):
    project = support.template_project(tmp_path / "product")
    _append(project, support.HEAD_REL, RETIRED)
    found = [item for item in kit_text_findings(project, sandbox) if item.get("code") == support.KIT_TEXT]
    assert not found, f"lines that say the guard, the sandbox and the prompts are retired are findings: {found}"


def test_f1_the_shipped_head_and_skill_give_no_finding(tmp_path, sandbox):
    project = support.template_project(tmp_path / "product", registry=True)
    found = [item for item in kit_text_findings(project, sandbox) if item.get("code") == support.KIT_TEXT]
    assert not found, f"the shipped kit text gives {support.KIT_TEXT} findings: {found}"
    checked, findings = support.portability(project, sandbox)
    assert findings is not None, f"the adapter check printed no findings document\n{checked.describe()}"
    assert not [item for item in findings if item.get("code") == support.KIT_TEXT], (
        f"the adapter check gives {support.KIT_TEXT} for the shipped kit\n{checked.describe()}")
