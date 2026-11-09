"""W2-128 round 1: the nine templates (TPL-1 S1-S5, F1; F7; the reviewer's reversal line; search again once).

The interface is the ticket's "Interface and rounds" section; budgets are R3-TEMPLATES §C's (README).
"""

from __future__ import annotations

import re

import pytest
import yaml

import w2_128_support as s

ROLE_TEMPLATES = [stem for stem in s.NINE]


# --- S1: the nine files and their front matter ---------------------------------------------------------------------

def test_s1_the_nine_templates_exist():
    missing = [f"{stem}.md ({label})" for stem, label in s.NINE.items() if not s.template_path(stem).is_file()]
    assert not missing, f"template/governance/kernel/templates/ lacks {missing}"


@pytest.mark.parametrize("stem", ROLE_TEMPLATES)
def test_s1_front_matter_holds_name_version_and_role(stem):
    front, _ = s.split(s.template(stem))
    assert isinstance(front, dict), f"{stem}.md opens with no YAML front matter"
    assert front.get("name") == stem, f"{stem}.md: name is {front.get('name')!r}, not the file's stem"
    version = front.get("version")
    assert isinstance(version, str) and s.SEMVER.match(version), f"{stem}.md: version {version!r} is not semver"
    role = front.get("role")
    assert (isinstance(role, str) and role.strip()) or (
        isinstance(role, list) and role and all(isinstance(r, str) and r.strip() for r in role)), \
        f"{stem}.md: role {role!r} is missing or empty"


# --- S2: the prose budget ------------------------------------------------------------------------------------------

@pytest.mark.parametrize("stem", ROLE_TEMPLATES)
def test_s2_prose_is_within_r3_budget(stem):
    size = len(s.prose(s.body(stem)))
    assert size <= s.BUDGET[stem], f"{stem}.md: prose {size} characters, over R3 §C's {s.BUDGET[stem]}"


def test_s2_facts_budgets_name_each_template_within_r3():
    budgets = s.facts().get("budgets")
    assert isinstance(budgets, dict), "facts.yaml has no budgets mapping"
    wrong = {stem: budgets.get(stem) for stem in s.NINE
             if not isinstance(budgets.get(stem), int) or not 0 < budgets[stem] <= s.BUDGET[stem]}
    assert not wrong, f"facts.yaml budgets missing or over R3 §C for {wrong}"


# --- S3: three superseded rules not restated -----------------------------------------------------------------------

def _sentences(unit: str) -> list[str]:
    return [part for part in re.split(r"(?<=[.;!?])\s+", unit) if part.strip()]


def test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests():
    reading = re.compile(r"\b(read|reads|open|opens|cat|view|inspect|study|look at)\b", re.I)
    offending = [sentence for unit in s.units(s.template("role-engineer")) for sentence in _sentences(unit)
                 if re.search(r"tests/acceptance|acceptance tests?", sentence, re.I)
                 and reading.search(sentence) and not s.NEGATION.search(sentence)]
    assert not offending, f"role-engineer.md tells the engineer to read the acceptance tests (DEC-957/959): {offending}"


def test_s3_test_designer_template_permits_reading_code_on_w2_integrate():
    permits = [sentence for unit in s.units(s.template("role-test-designer")) for sentence in _sentences(unit)
               if "w2/integrate" in sentence and re.search(r"\bread|git show", sentence, re.I)
               and re.search(r"\bcode\b|git show|src/", sentence, re.I) and not s.NEGATION.search(sentence)]
    assert permits, "role-test-designer.md has no sentence permitting reading code on w2/integrate (DEC-963)"


def test_s3_reviewer_template_carries_the_dec_1010_verdict_block():
    text = s.template("role-reviewer")
    blocks = re.findall(r"```verdict\s*\n(.*?)\n\s*```", text, re.S)
    assert blocks, "role-reviewer.md has no fenced ```verdict block (DEC-1010, the form verdict.py reads)"
    block = blocks[-1]
    for needle in ('"kpis"', '"kpi"', '"verdict"', '"findings"', '"scope"', '"ordinary_work"', '"consequence"',
                   "pass", "fail", "fails open", "loses work"):
        assert needle in block, f"role-reviewer.md's verdict block lacks {needle}"


# --- S4: the old briefs and roles/engineer.md line 5 ---------------------------------------------------------------

@pytest.mark.parametrize("old", sorted(s.OLD_BRIEFS))
def test_s4_old_brief_is_removed_or_a_one_line_pointer(old):
    path = s.TEMPLATES / old
    if not path.exists():
        return
    _, rest = s.split(path.read_text(encoding="utf-8"))
    lines = [line for line in rest.split("\n") if line.strip()]
    assert len(lines) == 1, f"{old} is neither removed nor a one-line pointer ({len(lines)} non-blank body lines)"
    assert s.OLD_BRIEFS[old] in lines[0], f"{old}'s line does not point to {s.OLD_BRIEFS[old]}: {lines[0]!r}"


def test_s4_engineer_role_line_5_says_to_fulfil_the_spec_and_its_kpis():
    lines = s.read(s.ROLES / "engineer.md").split("\n")
    assert len(lines) >= 5 and "to fulfil the spec and its KPIs" in lines[4], \
        f"roles/engineer.md line 5 is {lines[4] if len(lines) >= 5 else None!r}"


# --- S5: every placeholder is a key the generator knows ------------------------------------------------------------

def _keys() -> set[str]:
    data = yaml.safe_load(s.read(s.KEYS))
    assert isinstance(data, dict) and isinstance(data.get("keys"), list), "keys.yaml has no top-level keys: list"
    bad = [key for key in data["keys"] if not isinstance(key, str) or not s.KEY_NAME.match(key)]
    assert not bad, f"keys.yaml holds names outside [A-Z][A-Z0-9_]*: {bad}"
    return set(data["keys"])


def _all_template_texts() -> dict[str, str]:
    texts = {f"{stem}.md": s.template(stem) for stem in s.NINE}
    texts.update({f"{stem}.md": s.read(s.template_path(stem)) for stem in s.RECORDS
                  if s.template_path(stem).is_file()})
    return texts


def test_s5_every_key_placeholder_is_in_keys_yaml():
    known = _keys()
    unknown = {name: sorted(s.keys_of(text) - known) for name, text in _all_template_texts().items()
               if s.keys_of(text) - known}
    assert not unknown, f"placeholders no key in keys.yaml names: {unknown}"


def test_s5_keys_yaml_lists_the_appendix_keys():
    missing = sorted(set(s.APPENDIX_KEYS) - _keys())
    assert not missing, f"keys.yaml lacks the Appendix's keys {missing}"


# --- F1: a CMD, STEP, gov command or script a template names and facts.yaml does not -------------------------------

def test_f1_every_cmd_and_step_placeholder_is_a_facts_key():
    data = s.facts()
    commands, steps = s.commands(data), data.get("steps")
    assert isinstance(steps, dict), "facts.yaml has no steps mapping"
    wrong = {}
    for name, text in _all_template_texts().items():
        bad = sorted(f"CMD:{c}" for c in s.cmds_of(text) if c not in commands) + \
              sorted(f"STEP:{t}" for t in s.steps_of(text) if t not in steps)
        if bad:
            wrong[name] = bad
    assert not wrong, f"templates name commands or steps facts.yaml does not hold: {wrong}"


def test_f1_every_gov_command_and_script_a_template_names_is_in_facts():
    runs = " ".join(str(entry.get("run", "")) for entry in s.commands().values() if isinstance(entry, dict))
    known_gov = set(re.findall(r"\bgov(?:\.cli\.main)? ([a-z][a-z-]*)", runs))
    known_scripts = set(re.findall(r"([A-Za-z0-9_.-]+\.sh)\b", runs))
    wrong = {}
    for name, text in _all_template_texts().items():
        spans = " ".join(s.code_spans(text))
        bad = sorted({f"gov {sub}" for sub in re.findall(r"\bgov ([a-z][a-z-]*)", spans)} - {f"gov {g}" for g in known_gov})
        bad += sorted(set(re.findall(r"([A-Za-z0-9_.-]+\.sh)\b", text)) - known_scripts)
        if bad:
            wrong[name] = bad
    assert not wrong, f"templates name commands facts.yaml's commands do not hold: {wrong}"


# --- F7: every bracketed decision id is ACCEPTED -------------------------------------------------------------------

def test_f7_every_bracketed_decision_id_in_a_template_is_accepted():
    statuses = s.register_statuses()
    wrong = {}
    for name, text in _all_template_texts().items():
        cited = {dec for inside in s.BRACKET.findall(text) for dec in s.DEC_ID.findall(inside)}
        bad = sorted(f"{dec} ({statuses.get(dec, 'not in the register')})" for dec in cited
                     if statuses.get(dec) != "ACCEPTED")
        if bad:
            wrong[name] = bad
    assert not wrong, f"templates cite decisions that are not ACCEPTED as rules: {wrong}"


# --- S18: the reviewer states what would reverse each finding ------------------------------------------------------

def test_s18_reviewer_template_asks_per_finding_for_the_evidence_that_would_reverse_it():
    hits = s.units_with("role-reviewer", "finding", "evidence", "revers")
    assert hits, "role-reviewer.md asks for no evidence that would reverse a finding (DEC-1014)"


# --- S20: search again once ----------------------------------------------------------------------------------------

PHRASES = ("search again once", "own, different words", "not found", "two searches")


def test_s20_t0_carries_search_again_once_right_after_ask_memory_first():
    text = s.body("brief")
    lines = text.split("\n")
    at = [n for n, line in enumerate(lines) if "ask memory first" in line.lower()]
    assert at, "brief.md has no 'Ask memory first' line"
    section = [n for n, line in enumerate(lines[:at[0]]) if line.startswith("## ")]
    assert section and "command" in lines[section[-1]].lower(), "the 'Ask memory first' line is not in Commands"
    following = next((line for line in lines[at[0] + 1:] if line.strip()), "")
    missing = [phrase for phrase in PHRASES if phrase not in s.fold(following)]
    assert not missing, f"the line after 'Ask memory first' lacks {missing}: {following!r}"


def test_s20_t8_names_search_again_once_on_its_start_line():
    text = s.body("role-cto")
    missing = [phrase for phrase in PHRASES if phrase not in s.fold(text)]
    assert not missing, f"role-cto.md lacks {missing}"
    start = [unit for unit in s.units(text) if re.match(r"^[\s*>+\d.)-]*\**start\b", unit, re.I)]
    assert start and any("search again once" in s.fold(unit) for unit in start), \
        f"role-cto.md's Start line does not name search again once: {start}"
