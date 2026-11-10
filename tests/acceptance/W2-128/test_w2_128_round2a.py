"""W2-128 round 2a (S11, TPL-6 S3 and S4's kernel half; the review's F6 and F7): the two kernel skills, the
orchestrator role file, T-6's JUDGEMENT lines, the checkpoint example, the template's rulesync skill copies and the
two skills' versions (README, "Round 2a").

The baseline is integrate's text before round 2a, read with ``git show <BASELINE>:<path>`` at test time. It is
pinned to the commit integrate stood at when these cases were written, not to the moving ``w2/integrate``: after
the merge, ``w2/integrate`` holds the change itself, and "one minor above integrate" would turn red on the close.

Revised for round 2b (DEC-866, DEC-1112 (3)): the F6 role case also reads the template's rulesync copy (review F1);
the read-rule and K-4 cases are strengthened (review F3); the versions compare with ``BASELINE_VERSIONS`` (1.2.0
expected); the guards also allow round 2b's F2 and F4 lines. Round 2b's new cases are in ``test_w2_128_round2b.py``.
"""

from __future__ import annotations

import re
import subprocess
import sys

import pytest

import w2_128_support as s
from test_w2_128_links import _judge, FILLED_TICKET

BASELINE = "61231e61839e2300b37889ea7d4a44c62984ee4f"  # w2/integrate when round 2a's cases were written
# Round 2b (DEC-866 revision): the versions compare with integrate as merged into the tests branch for round 2b's
# cases, which holds round 2a (both skills 1.1.0); round 2b raises each one more minor, to 1.2.0.
BASELINE_VERSIONS = "a2576c6f66aea0645f2a5c2cc8c7633357fc4aaa"  # w2/integrate when round 2b's cases were written

SKILLS = s.REPO / "template/governance/kernel/skills"
RULESYNC_SKILLS = s.REPO / "template/.rulesync/skills"
TEST_DESIGN = "template/governance/kernel/skills/test-design/SKILL.md"
ORCHESTRATION = "template/governance/kernel/skills/orchestration/SKILL.md"
ORCHESTRATOR_ROLE = s.ROLES / "orchestrator.md"
RULESYNC_ORCHESTRATOR_ROLE = s.REPO / "template/.rulesync/subagents/orchestrator.md"  # round 2b, review F1

NEG = re.compile(r"\b(no|never|not|nor|none|nothing|forbid\w*|refus\w*|denied|without)\b|n't\b", re.I)
PERMIT = re.compile(r"\b(open|may|allowed|permitted|readable|free|no longer|lifted)\b", re.I)
HELD_OUT_BAR = re.compile(r"\b(never|not|no|refus\w*|forbid\w*|denied|but for|except|only)\b", re.I)
GENERAL_CODE_BAR = re.compile(r"src/|source code|\bimplementation\b|production director", re.I)
TEMPLATE_REF = re.compile(r"governance/kernel/templates|\brole-(?:engineer|test-designer|reviewer|product-spec|lead|"
                          r"research|cto)\.md\b")


# --- helpers ---------------------------------------------------------------------------------------------------------

def baseline(rel: str, commit: str = BASELINE) -> str:
    done = subprocess.run(["git", "-C", str(s.REPO), "show", f"{commit}:{rel}"], capture_output=True, text=True)
    assert done.returncode == 0, f"premise: git show {commit[:12]}:{rel} failed: {done.stderr.strip()}"
    return done.stdout


def now(rel: str) -> str:
    return s.read(s.REPO / rel)


def sections(text: str) -> list[tuple[str, str]]:
    """(heading, text) of each ``## `` section of a body; the part before the first one is heading ''."""
    found, heading, held = [], "", []
    for line in text.split("\n"):
        if line.startswith("## "):
            found.append((heading, "\n".join(held)))
            heading, held = line[3:].strip(), []
        else:
            held.append(line)
    found.append((heading, "\n".join(held)))
    return found


def section(text: str, word: str) -> str:
    hits = [part for heading, part in sections(s.split(text)[1]) if word.lower() in heading.lower()]
    assert len(hits) == 1, f"premise: no single section whose heading holds {word!r}"
    return hits[0]


def folded_units(text: str) -> list[str]:
    return [s.fold(unit) for unit in s.units(text) if unit.strip()]


def sentences(text: str) -> list[str]:
    found = []
    for unit in s.units(text):
        found.extend(part for part in re.split(r"(?<=[.;:!?])\s+|\s+—\s+", unit) if part.strip())
    return found


def clauses(text: str) -> list[str]:
    """Round 2b: sentences cut again at each comma, so a bar joined to a permitted or a ticket-bound clause by a
    comma (", and none …", "…, it does not read source code") is judged on its own."""
    return [part for line in sentences(text) for part in re.split(r",\s+", line) if part.strip()]


def retired_in(unit: str) -> list[str]:
    """The retired brief texts a unit names without naming the template that replaces each."""
    return [old for old, new in s.OLD_BRIEFS.items() if old in unit and new not in unit]


def version_parts(text: str) -> tuple[int, int, int]:
    front, _ = s.split(text)
    assert isinstance(front, dict), "the skill has no front matter"
    version = str(front.get("version", ""))
    assert s.SEMVER.match(version), f"version {version!r} is not semver"
    return tuple(int(part) for part in version.split("."))


# --- TPL-6 S3: the test-design skill's read rule (DEC-963; the review's F7) ------------------------------------------

def test_s11_test_design_read_rule_permits_integrate_and_forbids_only_this_tickets_implementation():
    rule = section(now(TEST_DESIGN), "read")
    assert "w2/integrate" in rule, "the test-design skill's read rule does not name w2/integrate (DEC-963)"
    assert "DEC-963" in rule, "the test-design skill's read rule does not cite DEC-963"
    bars = [line for line in sentences(rule)
            if NEG.search(line) and "implementation" in line.lower() and "ticket" in line.lower()]
    assert bars, "the read rule does not forbid this ticket's implementation (DEC-963)"
    # Round 2b (review F3): the permission is a sentence of its own kind, not only a name somewhere in the rule
    permits = [line for line in sentences(rule)
               if PERMIT.search(line) and not NEG.search(line) and re.search(r"\bread", line, re.I)
               and ("w2/integrate" in line or "integrated code" in line.lower())]
    assert permits, "no sentence of the read rule permits reading w2/integrate or the integrated code (DEC-963)"
    outright = [line for line in clauses(s.split(now(TEST_DESIGN))[1])
                if GENERAL_CODE_BAR.search(line) and NEG.search(line) and "ticket" not in line.lower()]
    assert not outright, f"the test-design skill still bars source code or implementation outright: {outright}"


# --- TPL-6 S3: the orchestration skill's "Briefs" ----------------------------------------------------------------------

def test_s11_orchestration_briefs_points_to_the_kernel_templates():
    briefs = section(now(ORCHESTRATION), "briefs")
    assert TEMPLATE_REF.search(briefs), \
        "the orchestration skill's Briefs does not point to template/governance/kernel/templates/ or a role template"
    folded = s.fold(briefs)
    assert "word for word" not in folded, "Briefs still says the standing sentences are carried word for word"
    named = [old for unit in s.units(briefs) for old in retired_in(unit)]
    assert not named, f"Briefs still starts sessions from the retired texts {named}"


def test_s11_orchestration_skill_no_longer_says_a_brief_states_each_step_in_full():
    folded = s.fold(s.split(now(ORCHESTRATION))[1])
    assert "each step in full" not in folded, "the orchestration skill still says a brief states each step in full"
    assert "standing sentences word for word" not in folded, \
        "the orchestration skill still says briefs carry the standing sentences word for word"


# --- TPL-6 S3: K-4's two lines (DEC-508 and DEC-525's settings half, as DEC-820 changed them) -------------------------

def test_s11_k4_no_bar_on_globbing_the_governance_folder():
    found = [line for line in sentences(s.split(now(ORCHESTRATION))[1])
             if re.search(r"\b(glob|listing|search)\b", line, re.I) and "governance" in line.lower()
             and NEG.search(line) and not PERMIT.search(line)]
    assert not found, f"the orchestration skill still forbids a glob or listing over the governance folder: {found}"


def test_s11_k4_no_bar_on_reading_the_settings_file():
    found = [line for line in sentences(s.split(now(ORCHESTRATION))[1])
             if "settings" in line.lower() and re.search(r"\bread\b", line, re.I)
             and NEG.search(line) and not PERMIT.search(line)]
    assert not found, f"the orchestration skill still forbids reading the settings file: {found}"


def test_s11_k4_guard_still_bars_the_held_out_contents():
    body = s.split(now(ORCHESTRATION))[1]
    bars = [line for line in sentences(body) if "held-out" in line.lower() and HELD_OUT_BAR.search(line)]
    assert bars, "the orchestration skill no longer forbids reading the held-out material's contents"


DEC_820_REFUSALS = {  # DEC-820's four read refusals, (a) to (d), as a line may name each
    "secrets": re.compile(r"\bsecrets?\b", re.I),
    "the held-out contents": re.compile(r"held-out", re.I),
    "the counterpart's work on the same ticket": re.compile(r"counterpart|same ticket", re.I),
    "the hidden half": re.compile(r"hidden half", re.I),
}


def test_s11_k4_lines_are_restated_citing_dec_820():
    protected = section(now(ORCHESTRATION), "protected")
    assert "DEC-820" in protected, "the restated K-4 lines do not cite DEC-820"
    # Round 2b (review F3): one line citing DEC-820 names all four refusals, not only the citation
    citing = [unit for unit in s.units(protected) if "DEC-820" in unit]
    best = min(([name for name, pattern in DEC_820_REFUSALS.items() if not pattern.search(unit)] for unit in citing),
               key=len)
    assert not best, f"no K-4 line citing DEC-820 names all four of its refusals; missing {best}"


# --- Review F6: the orchestration skill and the orchestrator role file ----------------------------------------------

def test_review_f6_orchestration_skill_names_no_retired_brief_text_as_content():
    named = [(old, unit[:90]) for unit in s.units(s.split(now(ORCHESTRATION))[1]) for old in retired_in(unit)]
    assert not named, f"the orchestration skill still sends sessions to the retired texts: {named}"


@pytest.mark.parametrize("path", [ORCHESTRATOR_ROLE, RULESYNC_ORCHESTRATOR_ROLE], ids=["kernel", "rulesync"])
def test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content(path):
    # Round 2b (review F1): the template's rulesync copy of the role takes the same line as the kernel role
    rel = path.relative_to(s.REPO)
    assert path.is_file(), f"premise: {rel} is missing"
    text = s.read(path)
    named = [(old, unit[:90]) for unit in s.units(text) for old in retired_in(unit)]
    assert not named, f"{rel} still starts a lead or worker from the retired texts: {named}"
    # W2-153 S3 (DEC-866): the rulesync copy's body may be role-lead.md's own body (front matter stripped, the blank
    # lines after it dropped, as portability's _split does), which names no template because it is the template.
    is_lead_body = path == RULESYNC_ORCHESTRATOR_ROLE and \
        s.split(text)[1].lstrip("\n") == s.split(s.template("role-lead"))[1].lstrip("\n")
    assert TEMPLATE_REF.search(text) or "gov brief" in text or is_lead_body, \
        f"{rel} names no kernel template (role-lead.md or the templates folder) for a lead's brief, " \
        f"nor is its body role-lead.md's body"


# --- TPL-6 S4's kernel half: JUDGEMENT's rules only in T-6 ----------------------------------------------------------

def test_s11_judgement_rules_are_in_t6_and_in_no_other_kernel_template():
    marks = ("Ordinary work:", "Consequence:")
    reviewer = s.template("role-reviewer")
    assert all(mark in reviewer for mark in marks), "role-reviewer.md (T-6) lacks JUDGEMENT's two lines"
    others = sorted(path.name for path in s.TEMPLATES.glob("*.md") if path.name != "role-reviewer.md"
                    and any(mark in path.read_text(encoding="utf-8") for mark in marks))
    assert not others, f"JUDGEMENT's rules are copied into other kernel templates: {others}"


# --- The checkpoint example: a placeholder, not DAEO-0000 -------------------------------------------------------------

def test_s11_checkpoint_example_holds_no_daeo_0000():
    assert "DAEO-0000" not in s.template("checkpoint"), "checkpoint.md's example still names DAEO-0000"


def test_s11_checkpoint_planted_from_its_example_gives_gov_links_no_unknown_id(tmp_path):
    text = s.template("checkpoint")
    # Filled as the generator fills it: {ID} is the ticket's id, any other placeholder a plain word. No other
    # substitution, so an example id that names no ticket shows as UNKNOWN_ID.
    filled = text.replace("{ID}", FILLED_TICKET)
    filled = re.sub(r"(?<!\$)\{[A-Z][A-Z0-9_]*(?::[^{}]*)?\}", "filled", filled)
    rel = "docs/checkpoints/CP-0000.md"
    answer, code, stderr = _judge(tmp_path, rel, filled)
    assert isinstance(answer, dict) and answer.get("ok"), f"gov links could not judge the planted tree (exit {code}): {stderr}"
    unknown = [f"{f.get('ids')} line {f.get('line')}" for f in answer["result"]["findings"]
               if f.get("path") == rel and f.get("code") == "UNKNOWN_ID"]
    assert not unknown, f"gov links gives UNKNOWN_ID on a record planted from checkpoint.md: {unknown}"


# --- The template's rulesync skill copies -----------------------------------------------------------------------------

@pytest.mark.parametrize("skill", ["discovery", "retrieval", "orchestration", "test-design"])
def test_s11_rulesync_skill_copy_is_byte_equal_to_the_kernel_skill(skill):
    kernel = SKILLS / skill / "SKILL.md"
    copy = RULESYNC_SKILLS / skill / "SKILL.md"
    assert kernel.is_file() and copy.is_file(), f"premise: {skill}'s kernel skill or its rulesync copy is missing"
    assert copy.read_bytes() == kernel.read_bytes(), \
        f"template/.rulesync/skills/{skill}/SKILL.md differs from the kernel skill"


# --- Versions and the skills validator --------------------------------------------------------------------------------

@pytest.mark.parametrize("rel", [ORCHESTRATION, TEST_DESIGN], ids=["orchestration", "test-design"])
def test_s11_skill_version_is_one_minor_above_integrates(rel):
    # Round 2b: one minor above integrate as round 2b's cases found it (1.1.0, round 2a's), so 1.2.0
    major, minor, _ = version_parts(baseline(rel, BASELINE_VERSIONS))
    assert version_parts(now(rel)) == (major, minor + 1, 0), \
        f"{rel}'s version is not {major}.{minor + 1}.0 (one minor above integrate's {major}.{minor}.x)"


def test_s11_skills_validator_passes_on_both_skills(tmp_path):
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", "--both-layouts",
                           str(SKILLS.relative_to(s.REPO) / "orchestration"),
                           str(SKILLS.relative_to(s.REPO) / "test-design")],
                          cwd=s.REPO, capture_output=True, text=True, env=s.sealed_env(tmp_path), timeout=60)
    assert done.returncode == 0, f"the skills validator fails: {done.stdout.strip()[-400:]} {done.stderr.strip()[-200:]}"


# --- Guards: nothing else in the two skills changes ------------------------------------------------------------------

def _front_without_version(text: str) -> dict:
    front, _ = s.split(text)
    assert isinstance(front, dict), "the skill has no front matter"
    return {key: value for key, value in front.items() if key != "version"}


def test_s11_guard_test_design_skill_changes_only_its_read_rule():
    old, new = baseline(TEST_DESIGN), now(TEST_DESIGN)
    assert _front_without_version(new) == _front_without_version(old), \
        "the test-design skill's front matter changed beyond its version"
    old_parts, new_parts = sections(s.split(old)[1]), sections(s.split(new)[1])
    assert [h for h, _ in new_parts] == [h for h, _ in old_parts], "the test-design skill's sections changed"
    # Round 2b (F4): the read rule may change; elsewhere a unit may differ only by CAP-38.b re-cited as CAP-38.c
    def recited(units: list[str]) -> list[str]:
        return [re.sub(r"cap-38\.c\b", "cap-38.b", unit, flags=re.I) for unit in units]

    changed = [h or "(before the first section)" for (h, a), (_, b) in zip(old_parts, new_parts)
               if "read" not in h.lower() and recited(folded_units(a)) != recited(folded_units(b))]
    assert not changed, f"the test-design skill changed outside its read rule: {changed}"


def test_s11_guard_orchestration_skill_changes_only_the_named_parts():
    old, new = baseline(ORCHESTRATION), now(ORCHESTRATION)
    assert _front_without_version(new) == _front_without_version(old), \
        "the orchestration skill's front matter changed beyond its version"
    old_parts, new_parts = sections(s.split(old)[1]), sections(s.split(new)[1])
    assert [h for h, _ in new_parts] == [h for h, _ in old_parts], "the orchestration skill's sections changed"
    wrong = []
    for (heading, a), (_, b) in zip(old_parts, new_parts):
        name = heading or "(before the first section)"
        if "briefs" in heading.lower():
            continue  # the Briefs part may change whole
        old_units, new_units = s.units(a), folded_units(b)
        free = [unit for unit in old_units if _orchestration_line_may_change(heading, unit)]
        kept = [s.fold(unit) for unit in old_units if unit not in free]
        # every other line of the section stays, in order; a freed line may be restated (one for one) or dropped
        at = 0
        for unit in new_units:
            if at < len(kept) and unit == kept[at]:
                at += 1
        if at < len(kept):
            wrong.append(f"{name}: {kept[at][:80]!r} changed or gone")
        elif len(new_units) - len(kept) > len(free):
            wrong.append(f"{name}: {len(new_units) - len(kept)} new lines where {len(free)} may change")
    assert not wrong, f"the orchestration skill changed beyond its named parts: {wrong}"


def _orchestration_line_may_change(heading: str, unit: str) -> bool:
    """The baseline's lines the rounds name: round 2a's K-4 lines (DEC-508, DEC-525) and the review's F6 lines (a
    retired brief text); round 2b's F2 lines, restated or dropped: the per-round ``gov checkpoint`` (DEC-511), the
    one-writer line (DEC-254) and the other session's folders (DEC-386)."""
    if any(old in unit for old in s.OLD_BRIEFS):
        return True
    if "protected" in heading.lower() and re.search(r"DEC-(508|525|386)\b", unit):
        return True
    if re.search(r"DEC-(511|254)\b", unit):
        return True
    return False
