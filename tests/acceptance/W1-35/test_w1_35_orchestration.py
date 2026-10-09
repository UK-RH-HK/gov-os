"""W1-35 follow-up (DEC-537, DEC-539, DEC-541): the way a wave is run, as text of the kernel.

Covers the ticket's two last success lines:

- S14 [CAP-24.a, CAP-24.b]: the orchestration skill, the ticket lead section of the orchestrator role file and
  five brief templates hold the way a wave is run; the wording is language-neutral where tests are named; a
  skill-regression check covers the new skill.
- S15 [CAP-28.a]: a status question asked in natural language is answered from ``gov status --json``; the
  orchestration skill states the route.

The cases read delivered text and say what a reader must be able to find in it. They fix no heading and no
sentence but the three standing sentences of a brief. See the README for the reading rules and the red reasons.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

import pytest
import yaml

import w1_35_orchestration_support as support
from conftest import (
    CITATION_PATTERN,
    MAX_BODY_TOKENS,
    MAX_DESC_TOKENS,
    PERMISSION_PATTERNS,
    REPO_ROOT,
    RESERVED_COMMANDS,
    SKILL_REGRESSION_FAMILY,
    check_support,
    cli_support,
    parse_skill,
    token_count,
)

VALIDATOR = "python3 -m gov.check.skill_validator"
VALIDATOR_TIMEOUT_S = 60.0


def _skill():
    """``(frontmatter, body, full text)`` of the orchestration skill, read as the other four skills are."""
    text = support.read(support.SKILL_REL)
    front, body = parse_skill(support.path(support.SKILL_REL))
    assert front is not None, f"{support.SKILL_REL}: the frontmatter is missing or is not valid YAML"
    return front, body, text


def _run_validator(target):
    """The generic validator of W1-26 on one skill folder: ``(exit code, parsed output)``."""
    env = dict(os.environ, PYTHONPATH=str(REPO_ROOT / "src"))
    done = subprocess.run([sys.executable, "-m", "gov.check.skill_validator", str(target)], cwd=str(REPO_ROOT),
                          env=env, capture_output=True, text=True, timeout=VALIDATOR_TIMEOUT_S)
    try:
        output = json.loads(done.stdout)
    except ValueError:
        output = {"unparsed": done.stdout[-500:], "stderr": done.stderr[-500:]}
    return done.returncode, output


# ============================================================================
# S14 [CAP-24.a]: the new skill has the form and the bounds of the others
# ============================================================================

class TestOrchestrationSkillForm:
    """covers: S14, F1 (the first success line's bounds, held for the new skill)"""

    def test_the_skill_has_a_versioned_frontmatter(self):
        front, _, _ = _skill()
        for field in ("name", "version", "description"):
            assert isinstance(front.get(field), str) and front[field].strip(), (
                f"{support.SKILL_REL}: the frontmatter field '{field}' is missing, empty or not a string"
            )
        assert front["name"] == support.SKILL_NAME, (
            f"{support.SKILL_REL}: the skill is named '{front['name']}', its folder '{support.SKILL_NAME}'"
        )

    def test_the_description_is_within_60_tokens(self):
        front, _, _ = _skill()
        tokens = token_count(str(front.get("description", "")))
        assert tokens <= MAX_DESC_TOKENS, f"the description is {tokens} tokens (at most {MAX_DESC_TOKENS})"

    def test_the_body_is_within_2500_tokens(self):
        _, body, _ = _skill()
        tokens = token_count(body)
        assert tokens <= MAX_BODY_TOKENS, (
            f"the body is {tokens} tokens (at most {MAX_BODY_TOKENS}); rows that do not fit go into the brief "
            f"templates the skill names, none is dropped (DEC-539)"
        )

    def test_every_gov_command_the_skill_names_is_a_known_one(self):
        """The validator reads every code span and fenced block for ``gov <word>``."""
        _, body, _ = _skill()
        spans = re.findall(r"`([^`]+)`", body) + re.findall(r"```.*?```", body, re.DOTALL)
        named = {word for span in spans for word in re.findall(r"gov\s+(\w+)", span)}
        unknown = sorted(named - set(RESERVED_COMMANDS))
        assert not unknown, (
            f"{support.SKILL_REL} names `gov {unknown[0]}` in code, which is not a reserved command "
            f"({RESERVED_COMMANDS}); the generic validator reports it as unknown"
        )

    def test_the_skill_names_the_five_brief_templates(self):
        _, _, text = _skill()
        missing = [name for name in support.BRIEFS.values() if name not in text]
        assert not missing, f"{support.SKILL_REL} does not name the brief templates {missing}"


# ============================================================================
# S14 [CAP-24.b]: a method; it cites what it follows and grants nothing
# ============================================================================

class TestOrchestrationSkillAuthority:
    """covers: S14 (the rule of the success line citing CAP-24.b, extended to the new skill)"""

    def test_the_skill_cites_a_policy_or_a_decision(self):
        _, _, text = _skill()
        assert CITATION_PATTERN.search(text), f"{support.SKILL_REL} cites no CAP, DEC or MR id"

    def test_no_permission_is_granted_without_the_decision_it_follows(self):
        _, _, text = _skill()
        uncited = [
            f"line {number}: {line.strip()[:90]}"
            for number, line in enumerate(text.splitlines(), 1)
            if any(pattern.search(line) for pattern in PERMISSION_PATTERNS) and not CITATION_PATTERN.search(line)
        ]
        assert not uncited, (
            f"{support.SKILL_REL} has permission-like wording with no CAP, DEC or MR id on the same line:\n"
            + "\n".join(uncited[:5])
        )

    def test_every_rule_in_a_list_is_stated_with_what_it_follows(self):
        """As for the four skills: a list item (with its wrapped and indented lines) that has a word of
        authority cites an id."""
        _, body, _ = _skill()
        words = ("must", "shall", "require", "refuse", "deny", "block", "only", "never", "always")
        uncited = []
        for _section, statement in support.statements(body):
            if not re.match(r"^([-*+]|\d+[.)])\s+", statement) or len(statement) < 15:
                continue
            if any(word in statement.lower() for word in words) and not CITATION_PATTERN.search(statement):
                uncited.append(statement[:90])
        assert not uncited, (
            f"{support.SKILL_REL}: list items that state a rule as the skill's own, with no CAP, DEC or MR id:\n"
            + "\n".join(f"  {item}" for item in uncited[:5])
        )


# ============================================================================
# S14: every row of the way a wave is run is findable (DEC-539: none is dropped)
# ============================================================================

class TestRows:
    """covers: S14 (success: each row is stated; failure: a row or one of its clauses is absent)"""

    @pytest.mark.parametrize("row", sorted(support.ROWS))
    def test_every_clause_of_the_row_is_stated(self, row):
        documents = support.corpus()
        faults = support.row_faults(row, documents)
        assert not faults, (
            f"row '{row}': a reader of {sorted(documents)} cannot find\n" + "\n".join(f"  {f}" for f in faults)
        )


# ============================================================================
# S14: the Wave 2 items are rules followed by hand, not a mechanism yet (DEC-537)
# ============================================================================

class TestWave2Items:
    """covers: S14"""

    def _passages(self):
        """The sections of the skill that say a rule is followed by hand and is not enforced yet."""
        _, body, _ = _skill()
        sections = support.section_texts(body)
        return [text for text in sections.values()
                if re.search(support.BY_HAND, text, re.IGNORECASE)
                and re.search(support.NOT_ENFORCED, text, re.IGNORECASE)]

    def test_the_skill_says_which_rules_no_mechanism_enforces_yet(self):
        assert self._passages(), (
            f"{support.SKILL_REL}: no section says both that rules are followed by hand and that no mechanism "
            f"enforces them yet (DEC-537)"
        )
        _, _, text = _skill()
        assert "DEC-537" in text, f"{support.SKILL_REL} does not cite DEC-537"

    def test_the_four_wave_2_items_stand_in_that_passage(self):
        passages = self._passages()
        assert passages, f"{support.SKILL_REL}: no passage on rules followed by hand"
        missing = [what for what, ideas in support.WAVE_2_ITEMS.items()
                   if not any(support.carries(passage, ideas) for passage in passages)]
        assert not missing, (
            f"{support.SKILL_REL}: the passage on rules followed by hand does not name {missing}"
        )


# ============================================================================
# S14: the ticket lead is a section of the orchestrator role file, not a seventh role
# ============================================================================

class TestTicketLeadSection:
    """covers: S14"""

    def _section(self):
        section = support.lead_section(support.read(support.ROLE_REL))
        assert section is not None and section.strip(), (
            f"{support.ROLE_REL} has no section whose heading names the ticket lead"
        )
        return section

    def _found(self, ideas):
        return [s for _n, s in support.statements(self._section()) if support.carries(s, ideas)]

    def test_the_section_says_what_a_lead_is(self):
        assert self._found([r"orchestrator", r"\bone\b|single|its own|\bbound\b", r"ticket", r"worktree"]), (
            "the ticket lead section does not say that a lead is an orchestrator-role session bound to one "
            "ticket and one worktree"
        )

    def test_the_section_says_what_a_lead_does(self):
        assert self._found([r"worker", r"start|launch"]) or self._found([r"ticket loop|\bloop\b", r"run"]), (
            "the ticket lead section does not say that a lead runs its ticket's loop and starts its workers"
        )

    def test_the_section_says_what_a_lead_may_not_do(self):
        missing = [what for what, ideas in {
            "merge into the integration branch": [r"merg", support.NEVER],
            "edit the ticket files or the decision register":
                [r"ticket files?|tickets\b|\.tickets|decision register", support.NEVER],
            "push": [r"push", support.NEVER],
        }.items() if not self._found(ideas)]
        assert not missing, f"the ticket lead section does not say that a lead never does: {missing}"

    def test_the_section_says_what_a_lead_returns(self):
        section = self._section()
        missing = [form for form in ("DONE", "PACKAGES", "ESCALATION", "LEAD_CHECKPOINT")
                   if not re.search(rf"\b{form}\b", section)]
        assert not missing, f"the ticket lead section does not name the return forms {missing}"

    def test_the_section_cites_what_it_follows(self):
        assert CITATION_PATTERN.search(self._section()), (
            "the ticket lead section cites no CAP, DEC or MR id"
        )

    def test_the_section_adds_no_labelled_field_to_the_role(self):
        """W1-33 and W1-38 read every list item that starts with a bold label as a field of the role and
        compare the fields with the generated definition. The lead is text of the role, not a ninth field."""
        labelled = [line.strip()[:80] for line in self._section().splitlines()
                    if re.match(r"^[-*]\s+\*\*[^*]+?:?\*\*", line)]
        assert not labelled, (
            f"the ticket lead section holds list items that start with a bold label: {labelled}"
        )

    def test_the_roster_stays_at_the_same_roles(self):
        roles = sorted(p.name for p in support.path(support.ROLES_REL).glob("*.md"))
        assert roles == sorted(support.ROLE_FILES), (
            f"{support.ROLES_REL}/ holds {roles}: the lead is a section of the orchestrator role, not a role"
        )
        sources = sorted(p.name for p in support.path(support.SOURCE_SUBAGENTS_REL).glob("*.md"))
        assert sources == sorted(support.ROLE_FILES), (
            f"{support.SOURCE_SUBAGENTS_REL}/ holds {sources}: no new rulesync subagent"
        )
        self._section()   # and the section is there: the lead is stated somewhere


# ============================================================================
# S14: the five brief templates
# ============================================================================

class TestBriefTemplates:
    """covers: S14"""

    @pytest.mark.parametrize("kind", sorted(support.BRIEFS))
    def test_the_brief_has_a_placeholder_for_each_thing_it_is_filled_in_with(self, kind):
        found = support.placeholders(support.read(support.brief_rel(kind)))
        missing = [what for what, pattern in support.PLACEHOLDER_KINDS.items()
                   if not any(re.search(pattern, inner, re.IGNORECASE) for inner in found)]
        assert not missing, (
            f"{support.brief_rel(kind)} has no placeholder for {missing} (its placeholders: {found})"
        )

    @pytest.mark.parametrize("kind", sorted(support.BRIEFS))
    def test_the_brief_carries_the_standing_sentences_word_for_word(self, kind):
        text = support.collapse(support.read(support.brief_rel(kind)))
        missing = [sentence for sentence in support.STANDING_SENTENCES if sentence not in text]
        assert not missing, (
            f"{support.brief_rel(kind)} does not carry, word for word (line breaks are free):\n"
            + "\n".join(f"  {sentence}" for sentence in missing)
        )

    def test_the_test_designers_brief_states_behaviour_and_sources_only(self):
        rel = f"{support.TEMPLATES_REL}/{support.TEST_DESIGNER_BRIEF}"
        text = support.read(rel)
        assert support.statements_with(text, [r"behaviou?r", r"source", r"\b(only|never|no|nothing)\b"]), (
            f"{rel} does not say that the brief states behaviour and sources only"
        )
        assert "DEC-462" in text, f"{rel} does not cite DEC-462"

    def test_no_brief_is_named_like_a_record_template(self):
        """W1-08 validates a templates file as a record when its name holds one of these words."""
        taken = {name: [word for word in support.RECORD_TEMPLATE_WORDS if word in name.lower()]
                 for name in support.BRIEFS.values()}
        assert not any(taken.values()), f"brief names that W1-08 reads as record templates: {taken}"
        for kind in support.BRIEFS:
            front, _ = support.split_frontmatter(support.read(support.brief_rel(kind)))
            assert not (front or {}).get("type"), (
                f"{support.brief_rel(kind)} has a record frontmatter (type: {front.get('type')}); a brief is "
                f"not a record"
            )


# ============================================================================
# S14: the wording
# ============================================================================

class TestWording:
    """covers: S14 (language-neutral where tests are named, DEC-534; a project's own values, DEC-539)"""

    def _texts(self):
        """The delivered text: the skill's body, the ticket lead section, the five briefs."""
        lead = support.lead_section(support.read(support.ROLE_REL))
        assert lead is not None, f"{support.ROLE_REL} has no ticket lead section"
        texts = {support.SKILL_REL: _skill()[1], f"{support.ROLE_REL} (ticket lead section)": lead}
        for kind in sorted(support.BRIEFS):
            texts[support.brief_rel(kind)] = support.read(support.brief_rel(kind))
        return texts

    def _faults(self, patterns):
        return [f"{rel}: {fault}" for rel, text in self._texts().items()
                for fault in support.wording_faults(text, patterns)]

    def test_tests_are_named_without_a_language_or_a_runner(self):
        faults = self._faults(support.LANGUAGE_BOUND)
        assert not faults, "the delivered text names a language or a runner:\n" + "\n".join(faults[:8])
        named = [rel for rel, text in self._texts().items()
                 if re.search(r"test command|acceptance tests|ticket's tests", text, re.IGNORECASE)]
        assert support.SKILL_REL in named, (
            f"{support.SKILL_REL} names no tests in a project's own terms (the project's test command, the "
            f"ticket's acceptance tests)"
        )

    def test_this_repositorys_own_values_are_not_the_rule(self):
        faults = self._faults(support.REPOSITORY_VALUES)
        assert not faults, (
            "the delivered text carries a value of this repository's wave where a project's own value, given "
            "by a placeholder, belongs:\n" + "\n".join(faults[:8])
        )


# ============================================================================
# S15 [CAP-28.a]: the natural-language route to gov status --json (DEC-541)
# ============================================================================

class TestStatusRoute:
    """covers: S15 (on the text; a live session answering a question is W1-42's, see the README)"""

    def _sections(self):
        """The sections of the skill that state the route: a statement with the command and the question."""
        _, body, _ = _skill()
        routed = {section for section, statement in support.statements(body)
                  if re.search(support.STATUS_COMMAND, statement)
                  and re.search(support.STATUS_QUESTION, statement, re.IGNORECASE)}
        texts = support.section_texts(body)
        return [texts[section] for section in sorted(routed)]

    def test_a_status_question_is_routed_to_the_command(self):
        assert self._sections(), (
            f"{support.SKILL_REL}: no statement says that a question about where things stand, asked in plain "
            f"words, is answered by running `gov status --json`"
        )
        _, _, text = _skill()
        assert re.search(r"\b(DEC-541|CAP-28)\b", text), f"{support.SKILL_REL} cites neither DEC-541 nor CAP-28"

    def test_the_route_names_the_parts_the_answer_is_given_from(self):
        sections = self._sections()
        assert sections, f"{support.SKILL_REL} does not state the route"
        missing = [what for what, pattern in support.STATUS_PARTS.items()
                   if not any(re.search(pattern, text, re.IGNORECASE) for text in sections)]
        assert not missing, f"{support.SKILL_REL}: where the route is stated, these parts are not named: {missing}"

    def test_a_part_marked_not_read_is_said_not_to_be_read(self):
        sections = self._sections()
        assert sections, f"{support.SKILL_REL} does not state the route"
        assert any(re.search(support.NOT_READ, text, re.IGNORECASE) for text in sections), (
            f"{support.SKILL_REL}: where the route is stated, nothing says that a part marked not read is "
            f"reported as not read"
        )

    def test_the_answer_is_never_given_from_recall(self):
        sections = self._sections()
        assert sections, f"{support.SKILL_REL} does not state the route"
        assert any(support.carries(text, [support.RECALL, support.NEVER]) for text in sections), (
            f"{support.SKILL_REL}: where the route is stated, nothing says that a status question is never "
            f"answered from recall"
        )

    def test_a_skill_without_the_route_is_found(self):
        """Failure of the line: the same reading finds no route in a skill that only names the command."""
        sample = "# Method\n\nRun `gov status --json` after every merge and keep its output.\n"
        assert not [s for _n, s in support.statements(sample)
                    if re.search(support.STATUS_COMMAND, s)
                    and re.search(support.STATUS_QUESTION, s, re.IGNORECASE)]
        _skill()   # red until the skill exists: the reading is then applied to the delivered text above


# ============================================================================
# S14 [CAP-24.a]: the skill-regression check for the new skill
# ============================================================================

class TestOrchestrationCheck:
    """covers: S14 (registered the way ``skill-regression-a`` is), F1"""

    def test_the_declaration_has_the_form_of_the_existing_one(self):
        file, data = support.check_declaration()
        existing = yaml.safe_load(support.read(support.EXISTING_CHECK_REL))
        for field in ("id", "family", "tier", "severity", "command"):
            assert isinstance(data.get(field), str) and data[field].strip(), (
                f"{file.name}: the field '{field}' is missing, empty or not a string"
            )
        for field in ("family", "tier", "severity"):
            assert data[field] == existing[field], (
                f"{file.name}: {field} is '{data[field]}', the existing skill-regression check has "
                f"'{existing[field]}'"
            )
        others = {yaml.safe_load(p.read_text(encoding="utf-8")).get("id")
                  for p in support.path(support.CHECKS_REL).glob("*.yaml") if p != file}
        assert data["id"] not in others, f"{file.name}: the id '{data['id']}' is another declaration's"
        assert data["id"].startswith("skill-regression-orchestration"), (
            f"{file.name}: the id '{data['id']}' does not name the skill it covers"
        )

    def test_the_declared_command_runs_the_generic_validator_over_the_new_skill(self):
        file, data = support.check_declaration()
        command = data["command"]
        assert VALIDATOR in command, f"{file.name}: the command does not run the generic validator: {command}"
        assert support.SKILL_FOLDER_REL in command, (
            f"{file.name}: the command does not name {support.SKILL_FOLDER_REL}: {command}"
        )
        assert "||" not in command and command.strip() != "true", (
            f"{file.name}: the command can pass without measuring: {command}"
        )

    def test_the_delivered_skill_passes_the_generic_validator(self):
        support.read(support.SKILL_REL)
        code, output = _run_validator(support.path(support.SKILL_FOLDER_REL))
        assert code == 0 and output == {"findings": []}, (
            f"the generic validator does not pass {support.SKILL_FOLDER_REL}: exit {code}, {output}"
        )

    def test_the_delivered_skill_with_a_body_over_the_bound_does_not_pass(self, tmp_path):
        """F1: the same file, its body grown past 2.5k tokens in a copy outside the tree."""
        text = support.read(support.SKILL_REL)
        copy = tmp_path / support.SKILL_NAME / "SKILL.md"
        copy.parent.mkdir(parents=True)
        copy.write_text(text + "\n" + "one more line of method text\n" * 400, encoding="utf-8")
        code, output = _run_validator(copy.parent)
        codes = [finding.get("code") for finding in output.get("findings", [])]
        assert code != 0 and codes == ["SKILL_BODY_TOO_LONG"], (
            f"a body over the bound is not the one finding: exit {code}, {output}"
        )

    def test_gov_check_runs_the_check_under_the_skill_regression_family(self, check_built, sandbox, tmp_path):
        """In a temporary project built from the kernel: the check is listed under its family and is GREEN;
        with the skill taken out of that project it is RED."""
        _file, data = support.check_declaration()
        support.read(support.SKILL_REL)
        project = check_support.Project(tmp_path / "project")
        interface = cli_support.load_interface(REPO_ROOT)

        def entry():
            run = check_support.run_check(project, sandbox)
            envelope = check_support.envelope_of(run, interface)
            result = envelope.get("result") or envelope.get("error", {}).get("details", {})
            found = [e for e in check_support.checks_of(result)
                     if isinstance(e, dict) and e.get("id") == data["id"]]
            assert len(found) == 1, f"gov check reports {len(found)} entries for {data['id']}\n{run.describe()}"
            return found[0], run

        green, run = entry()
        assert green.get("family") == SKILL_REGRESSION_FAMILY and green.get("status") == check_support.GREEN, (
            f"{data['id']} is not GREEN under '{SKILL_REGRESSION_FAMILY}': {green}\n{run.describe()}"
        )
        (project.root / support.SKILL_REL).unlink()
        project.commit("the orchestration skill is gone")
        red, run = entry()
        assert red.get("status") == check_support.RED, (
            f"{data['id']} is {red.get('status')} with no orchestration skill in the project\n{run.describe()}"
        )


# ============================================================================
# S14: the template's rulesync sources stay in step with the kernel (W1-38's check)
# ============================================================================

class TestRulesyncSources:
    """covers: S14 (the adapter-portability check of W1-38 compares each kernel file with its source)"""

    def test_the_skills_rulesync_source_is_the_kernel_skill(self):
        kernel = support.split_frontmatter(support.read(support.SKILL_REL))
        source = support.split_frontmatter(support.read(support.SOURCE_SKILL_REL))
        assert source == kernel, (
            f"{support.SOURCE_SKILL_REL} is not {support.SKILL_REL}: the frontmatter as a mapping and the "
            f"body byte for byte, the blank lines after the frontmatter apart"
        )

    def test_the_orchestrator_roles_rulesync_source_carries_the_role_files_body(self):
        kernel_body = support.split_frontmatter(support.read(support.ROLE_REL))[1]
        source_body = support.split_frontmatter(support.read(support.SOURCE_ROLE_REL))[1]
        assert source_body == kernel_body, (
            f"the body of {support.SOURCE_ROLE_REL} is not the text of {support.ROLE_REL}"
        )
