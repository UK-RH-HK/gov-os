"""W1-38, the round of DEC-664: the template's deny rule on the acceptance-test folder is taken out.

The template's permission source (``template/.rulesync/permissions.jsonc``) held, among its edit rules, a
deny rule on ``tests/acceptance/**`` beside the one on ``.tickets/**``. rulesync turns each into a deny rule
of the generated settings of every project made from the template, for every session whatever its role: the
independent test designer's included. DEC-664: the line is taken out of the template's source. MR-3 is held
by the launcher and the guard (DEC-069, DEC-315), not by a deny rule that also stops the test designer.

What the cases hold:

1. the template's source holds no edit rule on the folder, and the settings generated from it no rule on it;
2. every other rule the source gives is still there and still generated: the removal takes one rule;
3. in a stand-in project made from the template the folder is open to the independent test designer and to
   nobody else: the guard, asked through the PreToolUse commands the generated settings register, and the
   settings ``gov launch`` builds for a session there.

Every case that needs a project builds the suite's stand-in project under pytest's ``tmp_path`` (the
template's sources, the kernel, the tool registry, the real ``rulesync generate``, found as the suite finds
it: ``support.RULESYNC_BIN``, skipped when it is not installed). No tool call is ever made: the guard is
asked, and ``gov launch`` starts a stand-in program that records what a session would be started with
(W1-46's stand-in). Nothing of this repository but the template's files and the named tool registry is read.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import w1_38_hooks_support as hooks
import w1_38_support as support

_W1_46 = str(Path(__file__).resolve().parent.parent / "W1-46")
if _W1_46 not in sys.path:
    sys.path.insert(0, _W1_46)

import w1_46_support as launch_support  # noqa: E402  (the stand-in CLI, what a rule covers, a rule's parts)

needs_rulesync = pytest.mark.needs_rulesync
check_support, live_support, w47 = hooks.check_support, hooks.live_support, launch_support.w47

SOURCE_REL = "template/.rulesync/permissions.jsonc"
GENERATED_REL = support.SETTINGS_REL
FOLDER = "tests/acceptance"

# The folder itself, a file that exists in the stand-in project, a new one, one directly under, a nested one.
EXISTING_TEST = hooks.ACCEPTANCE_FILE
NEW_TEST = f"{FOLDER}/W1-90/test_added.py"
FOLDER_PATHS = (FOLDER, EXISTING_TEST, NEW_TEST, f"{FOLDER}/conftest.py", f"{FOLDER}/W1-91/data/deep/case.json")

# The tools whose rules bind a file write (an ``Edit`` rule binds every file tool; the others by name).
WRITE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
RULE_LISTS = ("deny", "ask", "allow")

# What the template's source gives beside the rule DEC-664 takes out, and what rulesync makes of each.
OTHER_SOURCE_RULES = {
    ("edit", ".tickets/**", "deny"),
    ("bash", "npm install*", "deny"),
    ("bash", "pip install*", "deny"),
    ("bash", "sudo *", "deny"),
}
OTHER_GENERATED_RULES = {
    "deny": ["Bash(npm install*)", "Bash(pip install*)", "Bash(sudo *)", "Edit(.tickets/**)"],
}

ENGINEER = hooks.ENGINEER
ORCHESTRATOR = check_support.ORCHESTRATOR
PRODUCT_SPEC = check_support.PRODUCT_SPEC
TEST_DESIGNER = check_support.TEST_DESIGNER
AUDITOR = check_support.AUDITOR
RESEARCH = launch_support.RESEARCH
EXPERIMENT_REL = "experiments/spikes/exp-901"

# The ticket each role's session is on. The test designer works on the engineer's ticket (its paths are
# ``src/app/**`` and ``tests/unit/**``: the ticket names no acceptance test). Every other role has a ticket
# of its own role.
TICKET_OF = {
    ENGINEER: hooks.TICKET_ID,
    TEST_DESIGNER: hooks.TICKET_ID,
    PRODUCT_SPEC: check_support.PRODUCT_SPEC_TICKET_ID,
    RESEARCH: "DAEO-zz97",
    AUDITOR: check_support.AUDITOR_TICKET_ID,
    ORCHESTRATOR: check_support.ORCHESTRATOR_TICKET_ID,
}
OWN_TICKET_PATHS = {
    PRODUCT_SPEC: ("docs/spec/**",),
    RESEARCH: (f"{EXPERIMENT_REL}/**",),
    AUDITOR: ("docs/audit/**",),
    ORCHESTRATOR: ("docs/**",),
}
NOT_THE_TEST_DESIGNER = (ENGINEER, PRODUCT_SPEC, RESEARCH, AUDITOR, ORCHESTRATOR)
# ``gov launch`` starts worker sessions; the orchestrator's is not one (W1-46 holds that refusal). A research
# session is not launched here: the launcher reads a research allowlist the suite's stand-in project does not
# carry, and none is written for the test. W1-46 holds the research session's built rules (README).
LAUNCHED_NOT_THE_TEST_DESIGNER = (ENGINEER, PRODUCT_SPEC, AUDITOR)


# ---------------------------------------------------------------------------
# What a rule covers
# ---------------------------------------------------------------------------

def _covered(specs, project, home):
    """The paths of ``FOLDER_PATHS`` a rule among ``specs`` covers (the rule's own path or a folder above it)."""
    return [rel for rel in FOLDER_PATHS if launch_support.covers(list(specs), rel, Path(project), Path(home))]


def _source_rules():
    """``(category, pattern, value)`` for every rule of the template's permission source."""
    source = hooks.load_source(support.REPO_ROOT / SOURCE_REL, SOURCE_REL)
    block = source.get("permission")
    assert isinstance(block, dict), f"{SOURCE_REL} holds no `permission` map"
    rules = set()
    for category, patterns in block.items():
        assert isinstance(patterns, dict), f"{SOURCE_REL}: `permission.{category}` is not a map of patterns"
        for pattern, value in patterns.items():
            rules.add((category, pattern, value))
    return rules


def _on_the_folder(rule, tmp_path):
    """Whether a rule of the source is an edit rule that covers a path of the folder, whatever its value."""
    category, pattern, _value = rule
    return category == "edit" and bool(_covered([pattern], tmp_path / "anywhere", tmp_path / "home"))


def _write_rules_on_the_folder(settings, project, home):
    """``list name: rule`` for every permission rule of a write tool, in any list, that covers a path of the folder."""
    found = []
    for kind in RULE_LISTS:
        for rule in w47.permission_rules(settings, kind):
            tool, spec = w47.split_rule(rule)
            if tool in WRITE_TOOLS and (spec is None or _covered([spec.strip()], project, home)):
                found.append(f"{kind}: {rule}")
    return found


def _edit_rules(settings):
    return launch_support.deny_rules(settings, "Edit")


# ---------------------------------------------------------------------------
# The stand-in project, its tickets, a session's home
# ---------------------------------------------------------------------------

@pytest.fixture()
def product(generated_project):
    """The generated project with a product's files, the engineer's ticket in progress, a ticket for each
    other role, and the research ticket's experiment folder."""
    project = hooks.add_product_work(generated_project)
    files = {f"{EXPERIMENT_REL}/README.md": "# Experiment 901\n"}
    for number, (role, paths) in enumerate(sorted(OWN_TICKET_PATHS.items()), start=1):
        files[f".tickets/{TICKET_OF[role]}.md"] = check_support.ticket_text(
            ticket_id=TICKET_OF[role], wbs_id=f"W1-9{number}", role=role, allowed_paths=paths)
    for rel, text in files.items():
        path = project / rel
        assert not path.exists(), f"{rel} is already in the stand-in project"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    check_support.commit_all(project, "a ticket for each other role")
    repo = support.REPO_ROOT.resolve()
    assert not project.resolve().is_relative_to(repo), "the stand-in project lies inside this repository"
    return project


@pytest.fixture()
def session_sandbox(tmp_path):
    """A stand-in home with the ``gov`` package installed, and a temporary folder, outside the project."""
    return hooks.make_session_sandbox(tmp_path / "session")


# ---------------------------------------------------------------------------
# The guard, asked through the commands the generated settings register
# ---------------------------------------------------------------------------

def _write_input(tool, path):
    if tool == "Write":
        return {"file_path": str(path), "content": "VALUE = 2\n"}
    if tool == "Edit":
        return {"file_path": str(path), "old_string": "VALUE = 1", "new_string": "VALUE = 2"}
    return {"command": f"echo changed >> {path}", "description": "W1-38 acceptance call"}


def _calls(project, rels=(EXISTING_TEST, NEW_TEST)):
    """``(what, tool, tool input)``: a Write and an Edit on each path by its whole name, and a Bash redirect
    into the new file by its name relative to the project."""
    calls = [(f"{tool} on {rel}", tool, _write_input(tool, Path(project) / rel))
             for rel in rels for tool in ("Write", "Edit")]
    calls.append((f"Bash `echo changed >> {rels[-1]}`", "Bash", _write_input("Bash", rels[-1])))
    return calls


_NUMBERS = iter(range(1, 1_000_000))


def _ask(project, sandbox, tool, tool_input, role):
    """The answers of the PreToolUse commands the generated settings register for ``tool``, run through the
    shell as registered in the project's root, as a session of ``role`` on its ticket. No call is made."""
    settings = support.load_settings(project)
    commands = live_support.hook_commands(settings, "PreToolUse", tool)
    assert commands, f"{GENERATED_REL}, generated from the template's sources, registers no PreToolUse command for {tool}"
    stdin = live_support.hook_input(project, sandbox, "PreToolUse", tool, tool_input,
                                    tool_use_id=f"toolu_w1_38_folder_{next(_NUMBERS):04d}")
    return [hooks.run_registered(command, stdin, project, sandbox, project, role, TICKET_OF[role])
            for command in commands]


def _decisions(results):
    return [check_support._guard_decision(result.returncode, result.stdout) for result in results]


def _describe(results):
    return "; ".join(result.describe() for result in results)


# ---------------------------------------------------------------------------
# ``gov launch`` in the stand-in project
# ---------------------------------------------------------------------------

@pytest.fixture()
def launched(product, sandbox):
    """``launched(role)``: ``gov launch <role> <its ticket>`` run in the stand-in project with this worktree's
    code and a stand-in home whose CLI is W1-46's recording stand-in. No session is started."""
    cli = launch_support.install_stand_in_cli(sandbox)

    def _launch(role):
        before = len(launch_support.calls(cli))
        run = support.cli_support.run_gov_with_code(support.REPO_ROOT, product, sandbox, "launch", role,
                                                    TICKET_OF[role])
        result = launch_support.Launch(run, tuple(launch_support.calls(cli)[before:]))
        assert run.returncode == 0, (
            f"gov launch {role} {TICKET_OF[role]} was refused in the stand-in project made from the template\n"
            f"{result.describe()}"
        )
        return result

    return _launch


# ===================================================================
# 1. The rule is gone: from the template's source and from what rulesync generates
# ===================================================================

class TestTheRuleIsGone:
    """DEC-664: the test-folder line is taken out of the template's permission source."""

    def test_the_templates_source_holds_no_edit_rule_on_the_acceptance_test_folder(self, tmp_path):
        """Whatever its value: a rule that asks would stop an unattended test designer as well."""
        found = sorted(rule for rule in _source_rules() if _on_the_folder(rule, tmp_path))
        assert not found, (
            f"{SOURCE_REL} holds an edit rule on the acceptance-test folder: {found}. rulesync turns it into a "
            f"rule of every session of a project made from the template, the independent test designer's "
            f"included (DEC-664: the line is taken out; MR-3 is held by the launcher and the guard)"
        )

    @needs_rulesync
    def test_the_generated_settings_hold_no_deny_rule_on_the_acceptance_test_folder(self, generated_project, tmp_path):
        settings = support.load_settings(generated_project)
        covered = _covered(_edit_rules(settings), generated_project, tmp_path / "home")
        assert not covered, (
            f"{GENERATED_REL}, generated from the template's sources, holds an Edit deny rule that covers "
            f"{covered}: {_edit_rules(settings)}. No test designer can write acceptance tests in a project made "
            f"from the template (DEC-664)"
        )

    @needs_rulesync
    def test_the_generated_settings_hold_no_rule_of_a_write_tool_on_the_folder_in_any_list(
        self, generated_project, tmp_path,
    ):
        """Not as a deny rule under another tool's name, and not moved to the ask or the allow list."""
        found = _write_rules_on_the_folder(support.load_settings(generated_project), generated_project,
                                           tmp_path / "home")
        assert not found, (
            f"{GENERATED_REL}, generated from the template's sources, holds a permission rule of a write tool on "
            f"the acceptance-test folder: {found} (DEC-664: who may write there is the guard's and the "
            f"launcher's decision, not a rule of the project's settings)"
        )


# ===================================================================
# 2. The removal takes one rule and no other
# ===================================================================

class TestEveryOtherRuleStays:
    """Green before implementation; it must stay green."""

    def test_the_templates_source_gives_the_four_other_rules_and_nothing_else(self, tmp_path):
        others = {rule for rule in _source_rules() if not _on_the_folder(rule, tmp_path)}
        assert others == OTHER_SOURCE_RULES, (
            f"beside the test-folder rule, {SOURCE_REL} must give the ticket-folder edit rule and the install "
            f"and sudo rules, and no other; missing: {sorted(OTHER_SOURCE_RULES - others)}, "
            f"not expected: {sorted(others - OTHER_SOURCE_RULES)}"
        )

    @needs_rulesync
    def test_the_four_other_deny_rules_are_still_generated_and_nothing_else(self, generated_project, tmp_path):
        settings = support.load_settings(generated_project)
        permissions = settings.get("permissions")
        assert isinstance(permissions, dict), f"{GENERATED_REL} holds no `permissions` map"
        on_the_folder = {entry.split(": ", 1)[1] for entry in
                         _write_rules_on_the_folder(settings, generated_project, tmp_path / "home")}
        others = {kind: sorted(rule for rule in rules if rule not in on_the_folder)
                  for kind, rules in permissions.items()}
        others = {kind: rules for kind, rules in others.items() if rules}
        assert others == OTHER_GENERATED_RULES, (
            f"beside a rule on the acceptance-test folder, {GENERATED_REL} generated from the template's sources "
            f"must hold the ticket-folder Edit rule and the install and sudo rules as deny rules, each once, and "
            f"no other permission rule; it holds {others}"
        )

    @needs_rulesync
    def test_the_generated_settings_still_close_the_ticket_folder(self, generated_project, tmp_path):
        """By what the rule covers, not by its spelling: a ticket file that exists and a new one."""
        specs = _edit_rules(support.load_settings(generated_project))
        open_ = [rel for rel in (".tickets/DAEO-zz90.md", ".tickets/new/DAEO-zz99.md")
                 if not launch_support.covers(specs, rel, generated_project, tmp_path / "home")]
        assert not open_, f"no Edit deny rule of {GENERATED_REL} covers {open_}; rules: {specs}"


# ===================================================================
# 3. The guard's decision in a project made from the template
# ===================================================================

class TestTheGuardInAProjectMadeFromTheTemplate:
    """MR-3, DEC-069, DEC-664: taking the line out opens the folder to nobody but the independent test
    designer. Green before implementation (the guard decides so already); it must stay green."""

    @needs_rulesync
    def test_the_test_designer_on_its_ticket_is_allowed_a_write_under_the_folder(self, product, session_sandbox):
        for what, tool, tool_input in _calls(product):
            results = _ask(product, session_sandbox, tool, tool_input, TEST_DESIGNER)
            assert set(_decisions(results)) == {"allow"}, (
                f"{what} by the independent test designer on {TICKET_OF[TEST_DESIGNER]}, in a project made from "
                f"the template: the guard did not allow it (MR-3: the acceptance tests are the test designer's "
                f"to write): {_describe(results)}"
            )

    @needs_rulesync
    def test_the_test_designer_is_still_refused_outside_the_folder(self, product, session_sandbox):
        """The allowance above is the guard's decision for this role, not a guard that lets everything through:
        the ticket's own paths, a file beside the folder, the ticket file."""
        rels = (hooks.IN_SCOPE_FILE, "tests/unit/test_main.py", f".tickets/{TICKET_OF[TEST_DESIGNER]}.md")
        for rel in rels:
            for tool in ("Write", "Edit"):
                results = _ask(product, session_sandbox, tool, _write_input(tool, product / rel), TEST_DESIGNER)
                assert any(hooks.refused_by_the_program(result) for result in results), (
                    f"{tool} on {rel} by the independent test designer: the guard's program did not answer with "
                    f"its refusal: {_describe(results)}"
                )

    @needs_rulesync
    @pytest.mark.parametrize("role", NOT_THE_TEST_DESIGNER)
    def test_every_other_role_is_refused_a_write_under_the_folder(self, product, session_sandbox, role):
        """The refusal is the guard's own: its program ended with 0 and wrote the refusal. An exit 2 would stop
        the call too, but it is also what an interpreter gives that did not find the program."""
        before = check_support.read(product, EXISTING_TEST)
        for what, tool, tool_input in _calls(product):
            results = _ask(product, session_sandbox, tool, tool_input, role)
            assert any(hooks.refused_by_the_program(result) for result in results), (
                f"{what} by {role} on its ticket {TICKET_OF[role]}, in a project made from the template: the "
                f"guard's program did not answer with its refusal. With the template's deny rule taken out "
                f"(DEC-664) nothing else stops this write: {_describe(results)}"
            )
        assert check_support.read(product, EXISTING_TEST) == before and not (product / NEW_TEST).exists()

    @needs_rulesync
    def test_the_engineer_is_let_through_inside_its_ticket(self, product, session_sandbox):
        """The refusals above are decisions about the folder, not a guard that refuses every write there is."""
        for tool in ("Write", "Edit"):
            results = _ask(product, session_sandbox, tool, _write_input(tool, product / hooks.IN_SCOPE_FILE),
                           ENGINEER)
            assert set(_decisions(results)) == {"allow"}, (
                f"{tool} on {hooks.IN_SCOPE_FILE} by the engineer, inside its ticket's paths: {_describe(results)}"
            )


# ===================================================================
# 3. The launcher's rules for a session in a project made from the template
# ===================================================================

class TestALaunchedSessionInAProjectMadeFromTheTemplate:
    """DEC-315: the settings the launcher builds carry Edit deny rules for the acceptance tests for every role
    but the independent test designer. A launched session is bound by those settings and by the project's own
    generated settings together: a deny rule of either one stops the write."""

    @needs_rulesync
    @pytest.mark.parametrize("role", LAUNCHED_NOT_THE_TEST_DESIGNER)
    def test_the_launchers_settings_close_the_folder_for_every_other_role(self, launched, product, sandbox, role):
        """Green before implementation; it must stay green. The launcher's settings alone are looked at: with
        the template's rule gone they are the only deny rule left for these sessions."""
        result = launched(role)
        specs = _edit_rules(result.settings())
        open_ = [rel for rel in FOLDER_PATHS if not launch_support.covers(specs, rel, product, sandbox.home)]
        assert not open_, (
            f"no Edit deny rule of the settings gov launch builds for {role}, in a project made from the "
            f"template, covers {open_}; rules: {specs}"
        )

    @needs_rulesync
    def test_the_launchers_settings_leave_the_folder_to_the_test_designer(self, launched, product, sandbox):
        """Green before implementation; it must stay green."""
        result = launched(TEST_DESIGNER)
        specs = _edit_rules(result.settings())
        assert not _covered(specs, product, sandbox.home), (
            f"an Edit deny rule of the settings gov launch builds for the independent test designer covers "
            f"{_covered(specs, product, sandbox.home)}; rules: {specs}"
        )
        closed = [rel for rel in (".tickets/DAEO-zz90.md", ".claude/settings.json")
                  if launch_support.covers(specs, rel, product, sandbox.home)]
        assert len(closed) == 2, f"the test designer's built settings no longer close the tickets and .claude: {specs}"

    @needs_rulesync
    def test_no_settings_of_a_launched_test_designer_close_the_folder(self, launched, product, sandbox):
        """The decided state: the session ``gov launch independent-test-designer <ticket>`` starts in a project
        made from the template can write its acceptance tests. Red before implementation: the project's own
        generated settings carry the template's deny rule."""
        result = launched(TEST_DESIGNER)
        built = _covered(_edit_rules(result.settings()), product, sandbox.home)
        own = _write_rules_on_the_folder(support.load_settings(product), product, sandbox.home)
        assert not built and not own, (
            f"a launched independent test designer, in a project made from the template, is stopped from writing "
            f"under the acceptance-test folder: the launcher's settings cover {built or 'nothing there'}; the "
            f"project's {GENERATED_REL} holds {own or 'no rule there'} (DEC-664)"
        )
