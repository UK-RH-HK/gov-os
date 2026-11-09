"""W2-152: the filled brief (S1, S4, S6, S7, F1). Each case builds its own repository (README)."""

from __future__ import annotations

import re

import pytest

import w2_152_support as s


# --- S1: the filled T-0 per worker role --------------------------------------------------------------------------

@pytest.mark.parametrize("role", sorted(s.WORKER_ROLES))
def test_s1_golden_brief_per_worker_role(repo, role):
    """The planted T-0 filled for each worker role equals its committed golden file (README, "Golden files")."""
    out = s.ok(repo.run(role, s.TICKET_ID))
    assert s.normal(out) == s.golden(f"brief-{role}.txt"), \
        f"gov brief {role} differs from fixtures/golden/brief-{role}.txt:\n{out}"


def test_s1_kernel_templates_fill_for_every_worker_role(real_repo):
    """This tree's T-0 and facts fill for every worker role on a READY ticket; the write tree is the tests tree for
    a test designer and the tree for every other role."""
    facts = real_repo.facts()
    tree = facts["paths"]["tree"].replace("{W2}", s.TICKET_W2)
    tests_tree = facts["paths"]["tests_tree"].replace("{W2}", s.TICKET_W2)
    for role in sorted(s.WORKER_ROLES):
        out = s.ok(real_repo.run(role, s.TICKET_ID))
        assert s.TICKET_ID in out and s.TICKET_W2 in out and s.TITLE in out, \
            f"gov brief {role} on the real T-0 lacks the ticket's id, W2 id or title:\n{out}"
        write_tree = tests_tree if role == "independent-test-designer" else tree
        row = f"| your tree (write here only) | {write_tree} |"
        assert row in out, f"gov brief {role}: the 'your tree' row is not {row!r}:\n{out}"


def test_s1_a_w2_id_resolves_to_the_same_brief_as_the_tk_id(repo):
    by_id = s.ok(repo.run("engineer", s.TICKET_ID))
    by_w2 = s.ok(repo.run("engineer", s.TICKET_W2))
    assert by_w2 == by_id, "gov brief by the W2 id differs from gov brief by the tk id"


def test_s1_templates_under_governance_kernel_are_the_fallback(tmp_path):
    """With no template/ folder, the templates at governance/kernel/templates/ are used (ticket, "Inputs")."""
    repo = s.Repo(tmp_path / "repo", templates="planted", templates_rel=s.FALLBACK_TEMPLATES_REL)
    assert not (repo.root / "template").exists()
    out = s.ok(repo.run("engineer", s.TICKET_ID))
    assert s.normal(out) == s.golden("brief-engineer.txt"), f"the fallback templates gave another brief:\n{out}"


# --- S4: --part, --repair, and no role template text --------------------------------------------------------------

def test_s4_part_fills_lead_note(repo):
    part = repo.file("parts/part.md", "PART-NOTE: the parser lives in src/widget/parse.py.\n")
    out = s.ok(repo.run("engineer", s.TICKET_ID, "--part", str(part)))
    assert "PART-NOTE: the parser lives in src/widget/parse.py." in out, f"--part's text is not in the brief:\n{out}"
    assert "Lead note: none" not in out, f"{{LEAD_NOTE}} is still 'none' with --part:\n{out}"
    assert "Repair: none" in out, f"{{REPAIR}} is not 'none' without --repair:\n{out}"


def test_s4_repair_fills_repair(repo):
    repair = repo.file("parts/repair.txt", "REPAIR-OUTPUT: AssertionError: widget printed nothing\n")
    out = s.ok(repo.run("engineer", s.TICKET_ID, "--repair", str(repair)))
    assert "REPAIR-OUTPUT: AssertionError: widget printed nothing" in out, \
        f"--repair's text is not in the brief:\n{out}"
    assert "Repair: none" not in out, f"{{REPAIR}} is still 'none' with --repair:\n{out}"
    assert "Lead note: none" in out, f"{{LEAD_NOTE}} is not 'none' without --part:\n{out}"


def test_s4_no_text_of_the_kernel_role_template_is_in_a_worker_brief(real_repo):
    """For each worker role, no distinctive text of role-<x>.md (a fragment of 25 characters or more found neither
    in T-0 nor in facts.yaml) is in its brief: the role template goes as the system prompt (W2-153)."""
    for role, stem in sorted(s.WORKER_ROLES.items()):
        out = s.ok(real_repo.run(role, s.TICKET_ID))
        pieces = s.role_fragments(stem)
        assert pieces, f"{stem}.md has no distinctive text to look for"
        leaked = [piece for piece in pieces if piece in out]
        assert not leaked, f"gov brief {role} carries text of {stem}.md: {leaked[:5]}"


# --- S6: the lead's run kinds -------------------------------------------------------------------------------------

@pytest.mark.parametrize("kind", s.RUN_KINDS)
def test_s6_golden_lead_block_per_run_kind(repo, kind):
    """gov brief lead --run <kind> carries the kind's block of the planted role-lead.md as its golden file (filled),
    no other kind's block, and no other line of role-lead.md (S4's exception)."""
    out = s.ok(repo.run("lead", s.TICKET_ID, "--run", kind))
    block = s.golden(f"lead-{kind}.txt")
    assert s.contains_block(out, block), f"the {kind} block is not in the lead brief as fixtures/golden:\n{out}"
    for other in s.RUN_KINDS:
        if other == kind:
            continue
        assert not re.search(rf"(?m)^\*\*{other}\*\*:", out), f"the {other} block is in the --run {kind} brief"
        assert f"PLANTED-RUN-{other.upper()}" not in out, f"a line of the {other} block is in the --run {kind} brief"
    assert "PLANTED-ROLE-LEAD" not in out, f"a line of role-lead.md outside the run section is in the brief:\n{out}"
    assert "{RUN_KIND}" not in out, "{RUN_KIND} is left unfilled"


def test_s6_kernel_role_lead_each_run_kind_carries_only_its_block(real_repo):
    """On this tree's role-lead.md: for each kind, the text of its block is in the brief, the distinctive text of the
    other four blocks is not, and no line of role-lead.md outside the run section is."""
    lead_text = (s.TEMPLATES / "role-lead.md").read_text(encoding="utf-8")
    blocks = s.lead_blocks(lead_text)
    assert sorted(blocks) == sorted(s.RUN_KINDS), f"role-lead.md's run blocks are {sorted(blocks)}"
    shared = (s.TEMPLATES / "brief.md").read_text(encoding="utf-8") + s.FACTS.read_text(encoding="utf-8")
    section_lines = {line.strip() for lines in blocks.values() for line in lines}
    section_lines |= {line.strip() for line in lead_text.split("\n") if line.startswith("## Your run:")
                      or line.strip().startswith("{STEP:")}
    outside = s.role_fragments("role-lead", exclude_lines=section_lines)
    for kind in s.RUN_KINDS:
        out = s.ok(real_repo.run("lead", s.TICKET_ID, "--run", kind))
        own = [piece for line in blocks[kind] for piece in s.fragments(line, 12)]
        missing = [piece for piece in own if piece not in out]
        assert not missing, f"--run {kind}: text of its block is missing: {missing[:5]}"
        own_text = "\n".join(blocks[kind])
        for other in s.RUN_KINDS:
            if other == kind:
                continue
            foreign = [piece for line in blocks[other] for piece in s.fragments(line, 15)
                       if piece not in shared and piece not in own_text]
            leaked = [piece for piece in foreign if piece in out]
            assert not leaked, f"--run {kind} carries text of the {other} block: {leaked[:5]}"
        leaked = [piece for piece in outside if piece in out]
        assert not leaked, f"--run {kind} carries role-lead.md text outside the run section: {leaked[:5]}"


# --- S7: a steps switch -------------------------------------------------------------------------------------------

def test_s7_a_switch_turned_off_removes_its_one_line_planted(repo):
    on = s.ok(repo.run("engineer", s.TICKET_ID))
    facts = repo.facts()
    facts["steps"]["alpha"]["on"] = False
    repo.write_facts(facts)
    off = s.ok(repo.run("engineer", s.TICKET_ID))
    on_lines, off_lines = on.split("\n"), off.split("\n")
    alpha = "Alpha step: run printenv GOV_ROLE GOV_TICKET [DEC-1]."
    assert alpha in on_lines, f"the alpha step's line is not in the brief with the switch on:\n{on}"
    expected = [line for line in on_lines if line != alpha]
    assert off_lines == expected, f"turning alpha off changed more than its one line:\n--- on ---\n{on}\n--- off ---\n{off}"


def test_s7_a_switch_turned_off_removes_its_one_line_kernel(real_repo):
    """On this tree's T-0: guard_refusal_lines off drops the one line holding it and changes nothing else."""
    on = s.ok(real_repo.run("engineer", s.TICKET_ID))
    facts = real_repo.facts()
    facts["steps"]["guard_refusal_lines"]["on"] = False
    real_repo.write_facts(facts)
    off = s.ok(real_repo.run("engineer", s.TICKET_ID))
    on_lines, off_lines = on.split("\n"), off.split("\n")
    assert len(on_lines) == len(off_lines) + 1, \
        f"turning one switch off did not remove exactly one line ({len(on_lines)} -> {len(off_lines)})"
    removed = [i for i in range(len(on_lines)) if on_lines[:i] + on_lines[i + 1:] == off_lines]
    assert removed, "the brief with the switch off is not the brief with one line removed"
    assert "<the command's form, one line>" in on_lines[removed[0]], \
        f"the removed line is not the guard_refusal_lines step's: {on_lines[removed[0]]!r}"


# --- F1: two runs on the same inputs ------------------------------------------------------------------------------

def test_f1_two_runs_are_byte_identical(real_repo, tmp_path):
    """Same inputs, run from another working folder, time zone and locale: stdout is byte-identical."""
    other = tmp_path / "elsewhere"
    other.mkdir()
    for args in (("engineer", s.TICKET_ID), ("lead", s.TICKET_ID, "--run", "build")):
        first = real_repo.run(*args, env={"TZ": "UTC", "LC_ALL": "C"})
        second = real_repo.run(*args, cwd=other, env={"TZ": "Asia/Tokyo", "LC_ALL": "C.UTF-8"})
        s.ok(first)
        s.ok(second)
        assert first.stdout.encode() == second.stdout.encode(), f"two runs of gov brief {' '.join(args)} differ"


def test_f1_json_brief_is_the_same_text_as_plain_stdout(repo):
    plain = s.ok(repo.run("independent-auditor", s.TICKET_ID))
    done = repo.run("independent-auditor", s.TICKET_ID, json_out=True)
    assert done.returncode == 0, s.describe(done)
    data = s.envelope(done)
    assert data["ok"] is True, data
    brief = data["result"].get("brief")
    assert isinstance(brief, str) and s.normal(brief) == s.normal(plain), \
        "result.brief under --json is not the plain run's stdout"
