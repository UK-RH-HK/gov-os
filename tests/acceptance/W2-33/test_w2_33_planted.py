"""W2-33 F2: a role built other than as the approved roles spec states, or without its machine-readable defaults,
fails the role test, naming the file; none passes.

Each case plants ONE departure in a copy of the roles folder under ``tmp_path`` and asks the checker
(``w2_33_support.role_faults``). Two bases per case:

1. a planted control folder (``build_synthetic``: nine files that satisfy the line rules and nothing else): the
   checker must pass it and then fail the plant, naming the planted file (this keeps the checker honest);
2. a copy of the folder as it stands in the repository: it must pass before the plant (the control; red until the work
   is done) and then fail the plant, naming the planted file.

Judged elsewhere: a role file edited by hand in the generated folder (W2-153's generation check, Interface).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_33_support as W  # noqa: E402


def _edit(name, old, new):
    def plant(folder):
        path = Path(folder) / f"{name}.md"
        text = path.read_text(encoding="utf-8")
        assert old in text, f"the plant cannot find {old!r} in {name}.md"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return name
    return plant


def _drop_lines(name, *heads):
    def plant(folder):
        path = Path(folder) / f"{name}.md"
        kept = [line for line in path.read_text(encoding="utf-8").splitlines()
                if not any(line.lstrip().startswith(head) for head in heads)]
        path.write_text("\n".join(kept) + "\n", encoding="utf-8")
        return name
    return plant


def _drop_file(name):
    def plant(folder):
        (Path(folder) / f"{name}.md").unlink()
        return name
    return plant


def _add_file(name):
    def plant(folder):
        (Path(folder) / f"{name}.md").write_text("# a role\n", encoding="utf-8")
        return name
    return plant


def _line(name, head):
    """The whole of the planted file's line that begins ``head``, read when the plant is made."""
    def plant(folder, change):
        path = Path(folder) / f"{name}.md"
        lines = path.read_text(encoding="utf-8").splitlines()
        index = next(i for i, line in enumerate(lines) if line.lstrip().startswith(head))
        lines[index] = change(lines[index])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return name
    return plant


def _change(name, head, change):
    def plant(folder):
        return _line(name, head)(folder, change)
    return plant


PLANTS = {
    # a line form broken (S2, S7)
    "version-not-x-y-z": (_change("engineer", W.VERSION_HEAD, lambda l: "- **Version:** 1.0"), "Version"),
    "launch-default-without-comma": (_change("research", W.DEFAULT_HEAD, lambda l: l.replace(", effort", " effort")),
                                     "Launch default"),
    "launch-default-with-a-full-stop": (_change("product-spec", W.DEFAULT_HEAD, lambda l: l + "."), "Launch default"),
    "skills-line-indented": (_change("orchestrator", W.SKILLS_HEAD, lambda l: "  " + l), "Skills"),
    "launch-default-twice": (_change("senior-engineer", W.DEFAULT_HEAD, lambda l: l + "\n" + l), "Launch default"),
    "skills-names-a-skill-that-does-not-exist": (_change("research", W.SKILLS_HEAD,
                                                         lambda l: l + ", no-such-skill-w2-33"), "no-such-skill-w2-33"),
    "model-tier-line-changed": (_change("independent-auditor", W.TIER_HEAD, lambda l: "- **Model tier:** standard"),
                                "Model tier"),
    "criticality-entries-out-of-order": (_change("engineer", W.CRITICALITY_HEAD,
                                                 lambda l: l.replace("C3 model", "C1 model", 1)), "Launch by criticality"),
    # the two sentences altered or taken out (S4, S5)
    "work-order-altered": (_edit("ticket-lead", "work in parallel from them", "work one after the other from them"),
                           "work-order"),
    "work-order-removed": (_drop_lines("qa-engineer", W.WORK_ORDER_HEAD), "work-order"),
    "one-writer-altered": (_edit("independent-test-designer", "never share a worktree", "may share a worktree"),
                           "one-writer-per-worktree"),
    "one-writer-removed": (_drop_lines("engineer", W.ONE_WRITER_HEAD), "one-writer-per-worktree"),
    # a defaults block removed (F2)
    "defaults-block-removed": (_drop_lines("research", W.VERSION_HEAD, W.DEFAULT_HEAD, W.SKILLS_HEAD,
                                           W.CRITICALITY_HEAD), "Launch default"),
    "skills-line-removed": (_drop_lines("senior-engineer", W.SKILLS_HEAD), "Skills"),
    "version-line-removed": (_drop_lines("independent-auditor", W.VERSION_HEAD), "Version"),
    # a value off S7's table
    "orchestrator-effort-medium": (_change("orchestrator", W.DEFAULT_HEAD, lambda l: l.replace("effort high", "effort medium")),
                                   "Launch default"),
    "engineer-default-opus": (_change("engineer", W.DEFAULT_HEAD, lambda l: l.replace(W.SONNET, W.OPUS)), "Launch default"),
    "product-spec-default-opus": (_change("product-spec", W.DEFAULT_HEAD, lambda l: l.replace(W.SONNET, W.OPUS)),
                                  "Launch default"),
    "test-designer-c3-sonnet": (_change("independent-test-designer", W.CRITICALITY_HEAD,
                                        lambda l: l.replace(f"C3 model {W.OPUS}", f"C3 model {W.SONNET}", 1)),
                                "Launch by criticality"),
    "qa-c2-not-the-full-form": (_change("qa-engineer", W.CRITICALITY_HEAD, lambda l: l.replace(W.QA_C2, f"C2 model {W.SONNET}, effort high")),
                                "Launch by criticality"),
    "criticality-line-removed-where-it-varies": (_drop_lines("engineer", W.CRITICALITY_HEAD), "Launch by criticality"),
    "criticality-line-where-rubric-2-does-not-vary": (
        _change("independent-auditor", W.DEFAULT_HEAD,
                lambda l: l + f"\n- **Launch by criticality:** C3 model {W.OPUS}, effort high; C2 model {W.OPUS}, "
                          f"effort high; C1 model {W.OPUS}, effort high; C0 model {W.SONNET}, effort high"),
        "Launch by criticality"),
    "c0-entry-malformed": (_change("engineer", W.CRITICALITY_HEAD, lambda l: l.rsplit("; C0", 1)[0] + "; C0 deterministic"),
                           "Launch by criticality"),
    # the roster of files
    "ticket-lead-file-missing": (_drop_file("ticket-lead"), "ticket-lead.md"),
    "qa-engineer-file-missing": (_drop_file("qa-engineer"), "qa-engineer.md"),
    "independent-reviewer-file-present": (_add_file("independent-reviewer"), "independent-reviewer.md"),
    "a-tenth-file-without-the-lines": (_add_file("tenth-role"), "tenth-role.md"),
}


def _judge(folder, plant, key, label):
    name = plant(folder)
    faults = W.role_faults(folder)
    assert faults, f"{label}: the checker passes the planted departure {key!r} in {name}.md"
    stray = [f for f in faults if not f.startswith(f"{name}.md: ")]
    assert not stray, f"{label}: a failure does not name the planted file {name}.md first: {stray}"
    assert any(key in f for f in faults), f"{label}: no failure names {key!r} for {name}.md: {faults}"


@pytest.mark.parametrize("case", sorted(PLANTS))
def test_f2_a_planted_departure_fails_the_role_test_naming_the_file(tmp_path, case):
    plant, key = PLANTS[case]
    # 1. the checker on a planted control folder: passes it, then fails the plant
    control = W.build_synthetic(tmp_path / "control")
    stray = W.role_faults(control)
    assert not stray, f"the checker's own control folder fails it (a fault of the test, not of the work): {stray}"
    _judge(control, plant, key, "checker control")
    # 2. the repository's roles folder, copied: it passes unplanted, and fails the plant
    copy = W.copy_folder(tmp_path / "copy")
    before = W.role_faults(copy)
    assert not before, (f"the roles folder as it stands has {len(before)} fault(s), so no departure planted in it "
                        f"can be told from them; the first: {before[:6]}")
    _judge(copy, plant, key, "roles folder copy")
