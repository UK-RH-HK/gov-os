"""W1-34 — Decision-package template: one test per KPI line (profile LITE, DEC-221).

The template is the customer interface (MR-6). Each test reads what the template
publishes: the ``decision-package*`` and ``decision-record*`` files of the kernel
templates folder. See the README for the readings and the red reasons.
"""

from __future__ import annotations

import re

import w1_34_support as support


def test_the_template_has_the_ten_fields_and_a_rank(form):
    """Success 1 [CAP-34.b]: the ten fields, plus rank P1-P3."""
    headings = form.headings()
    missing = [name for name, pattern in support.TEN_FIELDS
               if not any(re.search(pattern, heading, re.IGNORECASE) for heading in headings)]
    assert not missing, f"{form.name}: no heading for {missing} (headings: {headings})"
    assert "rank" in form.frontmatter, f"{form.name}: the frontmatter has no `rank`"
    assert form.frontmatter["rank"] in support.RANKS, (
        f"{form.name}: rank is {form.frontmatter['rank']!r}, not one of {list(support.RANKS)}")
    unnamed = [rank for rank in support.RANKS if not support.has_word(form.text, rank)]
    assert not unnamed, f"{form.name}: the ranks {unnamed} are not named"


def test_batching_allows_at_most_five_open_packages_and_p1_may_bypass(package_text):
    """Success 2 [CAP-34.c]: at most five open packages at a time; a P1 package may bypass the cap (DEC-093)."""
    cap = support.paragraphs_with(package_text, r"\b(at most|no more than|maximum of|up to)\s+(five|5)\b")
    assert cap, "the template states no cap of five packages at a time"
    assert any(support.has_word(block, "open") for block in cap), (
        "the template's cap of five does not say it counts open packages")
    bypass = [block for block in support.paragraphs_with(package_text, r"\bP1\b")
              if re.search(r"\bbypass", block, re.IGNORECASE)]
    assert bypass, "the template does not say that a P1 package may bypass the cap"


def test_an_answer_maps_to_a_decision_record_with_accepted_and_who(form, record_text):
    """Success 3: an answer maps to a decision record appended with ACCEPTED (owner, date)."""
    answer = form.section(r"\banswer\b")
    assert answer is not None, f"{form.name}: no Answer section"
    assert support.DECISION_ID.search(answer), (
        f"{form.name}: the Answer section names no decision record (an ADR-… or DEC-… id) for the answer")
    for where, text in ((f"{form.name}, Answer section", answer), ("the decision-record template", record_text)):
        forms = support.ACCEPTED_FORM.findall(text)
        assert forms, f"{where}: no `ACCEPTED (who, date)` form"
        assert all(inside.split(",")[0].strip() for inside in forms), (
            f"{where}: an `ACCEPTED (…)` form names nobody: {forms}")


def test_the_gate_record_carries_a_state_and_its_cit(form, package_text):
    """Success 4 [CAP-34.d]: a state (open, answered, declined, revoked, stale) and the CIT it belongs to."""
    # DEC-308: the template keeps the key and the status the READY rule of W1-09 reads.
    assert form.frontmatter.get("status") == "PROPOSED", (
        f"{form.name}: status is {form.frontmatter.get('status')!r}; a new package is open, which is PROPOSED")
    assert isinstance(form.frontmatter.get("constrains"), list), (
        f"{form.name}: the frontmatter has no `constrains` list for the tickets that wait on the package")
    unnamed = [state for state in support.GATE_STATES if not support.has_word(package_text, state)]
    assert not unnamed, f"the template does not name the gate states {unnamed}"
    gates = support.gate_frontmatters()
    with_cit = [name for name, frontmatter in gates.items()
                if any("cit" in support.key_tokens(key) for key in frontmatter)]
    assert with_cit, (f"no gate record's frontmatter has a key for the CIT it belongs to "
                      f"(keys: { {name: sorted(frontmatter) for name, frontmatter in gates.items()} })")


def test_the_routing_rule_classes_a_contradiction(package_text):
    """Success 5 [CAP-34.a]: agent-resolvable (settled by precedence and recorded) or human-resolvable (a package)."""
    agent = support.paragraphs_with(package_text, r"\bagent[- ]resolvable\b")
    human = support.paragraphs_with(package_text, r"\bhuman[- ]resolvable\b")
    assert agent, "the template has no routing rule: it never says agent-resolvable"
    assert human, "the template has no routing rule: it never says human-resolvable"
    assert any(support.has_word(block, "contradiction") or support.has_word(block, "contradictions")
               for block in agent + human), "the routing rule does not say it classes a contradiction"
    assert any(support.has_word(block, "precedence") and re.search(r"\brecord", block, re.IGNORECASE)
               for block in agent), "agent-resolvable is not said to be settled by precedence and recorded"
    assert any(support.has_word(block, "package") for block in human), (
        "human-resolvable is not said to be raised as a package")


def test_a_package_cannot_be_rendered_without_a_recommendation_or_confidence(form):
    """Failure 1: a package can be rendered without a recommendation or confidence."""
    for name in ("recommendation", "confidence"):
        section = form.section(rf"\b{name}\b")
        assert section is not None, f"{form.name}: no {name} section"
        assert section, f"{form.name}: the {name} section is blank, so a package renders without one"
        assert support.OBLIGATION.search(section), (
            f"{form.name}: the {name} section does not say that it is required")
    confidence = form.section(r"\bconfidence\b")
    unnamed = [level for level in support.CONFIDENCE_LEVELS if not support.has_word(confidence, level)]
    assert not unnamed, f"{form.name}: the confidence section does not name the levels {unnamed}"


def test_an_answer_cannot_be_recorded_without_a_date(form, record_text):
    """Failure 2: an answer can be recorded without a date."""
    answer = form.section(r"\banswer\b")
    assert answer is not None, f"{form.name}: no Answer section"
    for where, text in ((f"{form.name}, Answer section", answer), ("the decision-record template", record_text)):
        forms = support.ACCEPTED_FORM.findall(text)
        assert forms, f"{where}: no `ACCEPTED (who, date)` form, so nothing asks for the date of an answer"
        undated = [inside for inside in forms if not support.DATE_SLOT.search(inside)]
        assert not undated, f"{where}: an `ACCEPTED (…)` form has no date (YYYY-MM-DD): {undated}"
    assert any(support.has_word(block, "date") and support.OBLIGATION.search(block)
               for block in support.paragraphs(answer)), (
        f"{form.name}: the Answer section does not say that the date is required")
