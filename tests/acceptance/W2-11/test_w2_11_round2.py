"""W2-11 round 2 (DEC-983, DEC-991, DEC-995, DEC-996): the skill template's closed front matter and Never section
(success-9's second half), the anti-drift kit (success-13), scope control (success-14), self-timed timing tests
(success-15), the approvals section (success-16's skill half) and no skill that widens its role (failure-1).

The orchestration and test-design rules are read from the skill's whole folder (SKILL.md and its reference files):
SKILL.md's body is at its cap (2,500 tokens), so a rule may stand in a reference file, which SKILL.md must name."""
from __future__ import annotations

import re

import pytest

import w2_11_support as s

ORCHESTRATION = f"{s.SKILLS}/orchestration"
TEST_DESIGN = f"{s.SKILLS}/test-design"


def _front(rel, root=s.REPO_ROOT):
    front, _ = s.split_frontmatter(s.read(rel, root))
    assert front is not None, f"{rel} has no front matter"
    return front


def _shown(folder, rule, decision, ideas):
    """The rule is stated in one statement of the folder, in a file SKILL.md reaches, and the folder cites
    ``decision``."""
    texts = s.folder_texts(folder)
    assert len(texts) > 0, f"{folder} has no Markdown file"
    cited = any(s.cites(t, decision) for t in texts.values())
    assert cited, f"{folder} does not cite {decision}"
    holders = sorted({rel for rel, _ in s.folder_stated(folder, ideas)})
    assert len(holders) > 0, f"{folder} does not state: {rule}"
    reached = any(s.reached(folder, rel) for rel in holders)
    assert reached, f"{rule}: stated only in {holders}, which SKILL.md does not name"


# success-9, round 2's half: the skill template's front matter is closed; its Never section ------------------------

def test_the_skill_templates_front_matter_is_closed():
    front = _front(s.SKILL_TEMPLATE_REL)
    missing = [key for key in s.TEMPLATE_KEYS if key not in front]
    extra = sorted(set(front) - {*s.TEMPLATE_KEYS, "metadata"})
    assert not missing, f"skill.md's front matter lacks {missing}"
    assert not extra, f"skill.md's front matter carries keys outside name, version, description, output: {extra}"
    if "metadata" in front:
        meta = front["metadata"]
        assert isinstance(meta, dict) and set(meta) == {"version"}, (
            f"skill.md's metadata holds more than the carried version: {meta!r}")
        assert str(meta["version"]) == str(front["version"]), "skill.md's metadata.version is not its version"


def test_the_skill_template_says_what_output_holds():
    text = s.read(s.SKILL_TEMPLATE_REL)
    ideas = [r"\boutput\b", r"path class|class of paths", r"\bnone\b"]
    said = any(s.carries(s.plain(u), ideas) for u in [*s.statements(text), *text.splitlines()])
    assert said, "skill.md does not say that output is the path class the skill's method writes, or none"


NEVER = {
    "the skill changes no role's reads or writes":
        [r"\bskills?\b", r"\brole", r"\breads?\b", r"\bwrites?\b", r"chang|widen|grant|add|alter|extend",
         r"\b(no|never|not|nothing)\b"],
    "work needing other writes goes back as a package for the role that holds them":
        [r"\bwrites?\b", r"\bpackage", r"\brole\b", r"\bhold", r"\bback\b|return|hand|goes|go to|passe"],
}


@pytest.mark.parametrize("rule", sorted(NEVER))
def test_the_skill_templates_never_section_states(rule):
    text = s.read(s.SKILL_TEMPLATE_REL)
    cited = s.cites(text, "DEC-995") or s.cites(text, "DEC-996")
    assert cited, "skill.md cites neither DEC-995 nor DEC-996"
    never = s.section(text, r"never\b")
    has_never = never is not None
    assert has_never, "skill.md has no Never section"
    found = bool(s.stated(never, NEVER[rule]))
    assert found, f"skill.md's Never section does not state: {rule}"


# success-13: the anti-drift kit [DEC-952 item 6, DEC-953 item 7, DEC-851] ------------------------------------------

ANTI_DRIFT = {
    "a fresh orchestrator session every morning from a handover":
        ("DEC-952", [r"\bfresh\b", r"session", r"morning|every day|each day|daily", r"hand-?over|hand over"]),
    "the handover holds the checkpoint, RESUME HERE and the decisions in force":
        ("DEC-952", [r"hand-?over|hand over", r"checkpoint", r"RESUME HERE", r"in[- ]force"]),
    "the digest is loaded at start":
        ("DEC-953", [r"digest", r"\bload", r"\bstart"]),
    "every rule is written into its five places":
        ("DEC-851", [r"\brules?\b", r"\b(five|5)\b", r"places?"]),
}


@pytest.mark.parametrize("rule", sorted(ANTI_DRIFT))
def test_the_orchestration_skill_states_the_anti_drift_kit(rule):
    _shown(ORCHESTRATION, rule, *ANTI_DRIFT[rule])


# success-14: scope control [DEC-974] --------------------------------------------------------------------------------

SCOPE = {
    "a new ticket in the WBS goes to the owner as a P1 with a recommendation before it is filed":
        [r"new ticket", r"WBS|work breakdown|the plan", r"owner", r"\bP1\b", r"recommend", r"before",
         r"\bfil(e|ed|ing)\b"],
    "a lead names a needed ticket in its return and never files one":
        [r"\bleads?\b", r"\bnames?\b|naming", r"\breturn", r"never fil|not fil|no lead files|files none|never one"],
}


@pytest.mark.parametrize("rule", sorted(SCOPE))
def test_the_orchestration_skill_states_scope_control(rule):
    _shown(ORCHESTRATION, rule, "DEC-974", SCOPE[rule])


# success-15: a timing test measures the work under test [DEC-979 item 1 D2] ---------------------------------------

TIMING = {
    "a timing test measures its process's CPU time or against a quiet reference beside it":
        [r"timing|timed|time limit|latency", r"CPU time|process'?s? (own )?time", r"reference"],
    "never the wall time of a loaded machine":
        [r"timing|timed|time limit|latency", r"wall", r"load", r"\b(never|not|no)\b"],
    "at the same bound":
        [r"timing|timed|time limit|latency", r"same (bound|limit|threshold)|lowering nothing|bound unchanged"],
}


@pytest.mark.parametrize("rule", sorted(TIMING))
def test_the_test_design_skill_states_self_timed_timing_tests(rule):
    _shown(TEST_DESIGN, rule, "DEC-979", TIMING[rule])


# success-16, the skill half: the approvals section [DEC-991, DEC-994 item 3] --------------------------------------

def test_the_orchestration_skill_has_an_approvals_section():
    texts = s.folder_texts(ORCHESTRATION)
    holders = [rel for rel, text in texts.items()
               if re.search(r"^#{1,6}\s+.*approv", text, re.M | re.I) or "approv" in rel.rsplit("/", 1)[-1].lower()]
    assert holders, "the orchestration skill's folder has no approvals section (no heading, no file)"
    assert any(s.reached(ORCHESTRATION, rel) for rel in holders), (
        f"the approvals section stands only in {holders}, which SKILL.md does not name")


APPROVALS = {
    "the orchestrator reads its own allow list at session start":
        [r"allow[- ]?list|allow, ask and deny|own allow", r"session start|start of (each|the|every|a) session|"
                                                           r"at (the )?start|starts"],
    "the allow list is the settings files' allow, ask and deny rules":
        [r"\ballow\b", r"\bask\b", r"\bdeny\b", r"setting"],
    "and the host's known safety checks: for Claude Code, any .claude/ path":
        [r"safety check|built-in check|own check", r"\.claude/", r"Claude Code|host"],
    "before each command it classifies it as allowed or as possibly needing the owner's approval":
        [r"before (each|every|running|a|any) (command|call)|each command|every command|each call", r"allowed",
         r"approv"],
    "such a call is never chained to other work":
        [r"chain", r"\b(never|not|no)\b|alone", r"approv|such a (call|command)"],
    "by day it notifies the owner first, then runs it":
        [r"\bby day\b|\bday(time)?\b|during the day", r"notif|ping|tell", r"owner", r"\bthen\b|\bfirst\b",
         r"\brun"],
    "inside the project's quiet hours it never runs it and queues it for the morning package":
        [r"quiet hours", r"never runs?|not run|does not run|no run", r"queue", r"morning"],
}


@pytest.mark.parametrize("rule", sorted(APPROVALS))
def test_the_orchestration_skill_states_the_approvals_rule(rule):
    _shown(ORCHESTRATION, rule, "DEC-991", APPROVALS[rule])


def test_the_quiet_hours_are_the_projects_not_a_fixed_clock():
    fixed = [(rel, st[:100]) for rel, st in s.folder_stated(ORCHESTRATION, [r"quiet hours", r"\b\d{1,2}:\d{2}\b"])]
    named = len(s.folder_stated(ORCHESTRATION, [r"quiet hours"])) > 0
    assert named, "the orchestration skill names no quiet hours"
    assert not fixed, f"the quiet hours are a fixed clock, not the project's: {fixed}"


SCENARIOS = {
    "day": [r"\bby day\b|\bday(time)?\b|during the day", r"notif|ping|tell", r"\brun"],
    "night": [r"quiet hours|night", r"queue"],
    "chained command": [r"chain", r"approv|alone|separate|split|own (call|command)"],
}


@pytest.mark.parametrize("kind", sorted(SCENARIOS))
def test_the_approvals_section_has_a_scenario_for(kind):
    units = [u for text in s.folder_texts(ORCHESTRATION).values() for u in s.scenario_units(text)]
    found = any(s.carries(u, SCENARIOS[kind]) for u in units)
    assert found, f"the orchestration skill has no approvals scenario for {kind}"


# failure-1: no kernel skill, copy or template widens its role [DEC-995, DEC-996] ----------------------------------

@pytest.mark.parametrize("rel", s.skill_files())
def test_no_permission_field_in_front_matter(rel):
    found = s.permission_fields(_front(rel))
    assert not found, f"{rel} carries a permission field in its front matter: {found}"


@pytest.mark.parametrize("name", [n for n in s.kernel_skill_names() if n != "adopt"])
def test_every_write_step_lies_in_the_skills_output_class(name):
    front = _front(f"{s.SKILLS}/{name}/SKILL.md")
    assert "output" in front, f"{name} declares no output class, so its write steps cannot be held to one"
    output = front["output"]
    assert s.declares_none(output) or s.output_classes(output), (
        f"{name}'s output is neither none nor a path class: {output!r}")
    stray = {rel: s.stray_writes(text, output)
             for rel, text in s.folder_texts(f"{s.SKILLS}/{name}").items()}
    stray = {rel: found for rel, found in stray.items() if found}
    assert not stray, f"{name} tells its role to write outside its output class {output!r}: {stray}"


PERMISSION_PLANTS = ["allowed-tools", "permissions", "paths", "network", "model", "effort", "metadata.allowed-tools"]


def _plant_rels():
    return (f"{s.SKILLS}/planted/SKILL.md", ".claude/skills/planted/SKILL.md", s.SKILL_TEMPLATE_REL)


@pytest.mark.parametrize("key", PERMISSION_PLANTS)
def test_a_planted_permission_field_is_found(tmp_path, key):
    rel = _plant_rels()[PERMISSION_PLANTS.index(key) % 3]     # a kernel skill, its generated copy, the template
    if key.startswith("metadata."):
        field = f"metadata:\n  version: \"1.0.0\"\n  {key.split('.', 1)[1]}: Bash(*)\n"
    else:
        field = f"{key}: Bash(*)\n"
    planted = tmp_path / rel
    planted.parent.mkdir(parents=True)
    planted.write_text(f"---\nname: planted\nversion: \"1.0.0\"\ndescription: A planted skill.\noutput: none\n"
                       f"{field}---\n\n# Planted\n", encoding="utf-8")
    if "/planted/" in rel:
        (tmp_path / s.SKILLS / "planted").mkdir(parents=True, exist_ok=True)
        (tmp_path / s.SKILLS / "planted" / "SKILL.md").touch()
    assert rel in s.skill_files(tmp_path), "the checked file list does not reach the planted file"
    assert key in s.permission_fields(_front(rel, tmp_path)), f"the check passed a front matter carrying {key}"


STRAY_PLANTS = {
    "output none, a step that commits a record": ("none", "- [ ] Commit the record to `docs/records/r1.md`."),
    "output the acceptance folder, a step that writes code":
        ("tests/acceptance/<ticket>/", "- [ ] Write the module `src/gov/check/thing.py` and run it."),
    "output the acceptance folder, a step that edits a role file":
        ("tests/acceptance/<ticket>/", "1. Edit `template/governance/kernel/roles/engineer.md` to add a path."),
}
WITHIN = ("- [ ] Write the cases in `tests/acceptance/<ticket>/test_cases.py`.\n"
          "- [ ] Run `gov accept <ticket>` and read the result.\n\n"
          "## Never\n\n- Never write `src/**` or `.claude/**`: work that needs those writes goes back as a package "
          "for the role that holds them.\n")


@pytest.mark.parametrize("kind", sorted(STRAY_PLANTS))
def test_a_planted_step_writing_outside_its_output_class_is_found(kind):
    output, step = STRAY_PLANTS[kind]
    text = f"---\nname: planted\nversion: \"1.0.0\"\ndescription: A planted skill.\noutput: {output}\n---\n\n" \
           f"# Planted\n\n## Steps\n\n{WITHIN}\n## More steps\n\n{step}\n"
    assert s.stray_writes(text, output), f"the check passed a step writing outside {output!r}: {step}"


def test_a_planted_skill_writing_inside_its_class_passes():
    text = f"---\nname: planted\noutput: tests/acceptance/<ticket>/\n---\n\n# Planted\n\n## Steps\n\n{WITHIN}"
    front, _ = s.split_frontmatter(text)
    assert not s.permission_fields(front), "the check refuses a front matter without a permission field"
    assert s.write_targets(text) == ["tests/acceptance/<ticket>/test_cases.py"], s.write_targets(text)
    assert not s.stray_writes(text, front["output"]), "the check refuses a step inside the output class"
