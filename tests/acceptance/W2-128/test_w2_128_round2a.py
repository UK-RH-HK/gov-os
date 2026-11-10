"""W2-128 round 2a (S11, TPL-6 S3 and S4's kernel half; the review's F6 and F7): the two kernel skills, the
orchestrator role file, T-6's JUDGEMENT lines, the checkpoint example, the template's rulesync skill copies and the
two skills' versions (README, "Round 2a").

The baseline is integrate's text before round 2a, read with ``git show <BASELINE>:<path>`` at test time. It is
pinned to the commit integrate stood at when these cases were written, not to the moving ``w2/integrate``: after
the merge, ``w2/integrate`` holds the change itself, and "one minor above integrate" would turn red on the close.
"""

from __future__ import annotations

import re
import subprocess
import sys

import pytest

import w2_128_support as s
from test_w2_128_links import _judge, FILLED_TICKET

BASELINE = "61231e61839e2300b37889ea7d4a44c62984ee4f"  # w2/integrate when round 2a's cases were written

SKILLS = s.REPO / "template/governance/kernel/skills"
RULESYNC_SKILLS = s.REPO / "template/.rulesync/skills"
TEST_DESIGN = "template/governance/kernel/skills/test-design/SKILL.md"
ORCHESTRATION = "template/governance/kernel/skills/orchestration/SKILL.md"
ORCHESTRATOR_ROLE = s.ROLES / "orchestrator.md"

NEG = re.compile(r"\b(no|never|not|nor|none|nothing|forbid\w*|refus\w*|denied|without)\b|n't\b", re.I)
PERMIT = re.compile(r"\b(open|may|allowed|permitted|readable|free|no longer|lifted)\b", re.I)
HELD_OUT_BAR = re.compile(r"\b(never|not|no|refus\w*|forbid\w*|denied|but for|except|only)\b", re.I)
TEMPLATE_REF = re.compile(r"governance/kernel/templates|\brole-(?:engineer|test-designer|reviewer|product-spec|lead|"
                          r"research|cto)\.md\b")


# --- helpers ---------------------------------------------------------------------------------------------------------

def baseline(rel: str) -> str:
    done = subprocess.run(["git", "-C", str(s.REPO), "show", f"{BASELINE}:{rel}"], capture_output=True, text=True)
    assert done.returncode == 0, f"premise: git show {BASELINE[:12]}:{rel} failed: {done.stderr.strip()}"
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
    outright = [line for line in sentences(s.split(now(TEST_DESIGN))[1])
                if "src/" in line and NEG.search(line) and "ticket" not in line.lower()]
    assert not outright, f"the test-design skill still forbids src/ outright: {outright}"


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


def test_s11_k4_lines_are_restated_citing_dec_820():
    assert "DEC-820" in section(now(ORCHESTRATION), "protected"), \
        "the restated K-4 lines do not cite DEC-820"


# --- Review F6: the orchestration skill and the orchestrator role file ----------------------------------------------

def test_review_f6_orchestration_skill_names_no_retired_brief_text_as_content():
    named = [(old, unit[:90]) for unit in s.units(s.split(now(ORCHESTRATION))[1]) for old in retired_in(unit)]
    assert not named, f"the orchestration skill still sends sessions to the retired texts: {named}"


def test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content():
    text = s.read(ORCHESTRATOR_ROLE)
    named = [(old, unit[:90]) for unit in s.units(text) for old in retired_in(unit)]
    assert not named, f"roles/orchestrator.md still starts a lead or worker from the retired texts: {named}"
    assert TEMPLATE_REF.search(text) or "gov brief" in text, \
        "roles/orchestrator.md names no kernel template (role-lead.md or the templates folder) for a lead's brief"


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
    major, minor, _ = version_parts(baseline(rel))
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
    changed = [h or "(before the first section)" for (h, a), (_, b) in zip(old_parts, new_parts)
               if "read" not in h.lower() and folded_units(a) != folded_units(b)]
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
        if "protected" in heading.lower():
            # K-4's two lines may change; every other line of the section stays, in order
            kept = [s.fold(unit) for unit in old_units if not re.search(r"DEC-(508|525)\b", unit)]
            at = 0
            for unit in new_units:
                if at < len(kept) and unit == kept[at]:
                    at += 1
            if at < len(kept):
                wrong.append(f"{name}: {kept[at][:80]!r} changed or gone")
            continue
        # elsewhere only a line naming a retired brief text may change (the review's F6), one line for one
        if len(new_units) != len(old_units):
            wrong.append(f"{name}: {len(old_units)} lines became {len(new_units)}")
            continue
        for unit_old, unit_new in zip(old_units, new_units):
            if s.fold(unit_old) != unit_new and not any(o in unit_old for o in s.OLD_BRIEFS):
                wrong.append(f"{name}: {unit_old[:80]!r} changed")
    assert not wrong, f"the orchestration skill changed beyond its named parts: {wrong}"
