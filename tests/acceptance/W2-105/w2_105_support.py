"""Support code for the W2-105 acceptance tests: the template's install block removed (DEC-966 item 1).

**A generated project.** As W2-90's helper makes it (``w2_90_kernel_wiring.generate_project``): ``copier.yml`` and
``template/`` assembled file by file into a temporary template source, ``copier copy``, then ``rulesync generate`` in
the project. The project's ``.claude/settings.json`` is what a product of the template runs with. Everything is read
relative to the repository this file sits in (``REPO_ROOT``), so the tests judge that worktree's template and code.

**How a call is decided.** As the harness decides it, and as W1-05's and W1-38's harnesses read it: a rule of the
settings' ``permissions.deny`` refuses before any hook is asked; otherwise every PreToolUse command the settings
register for the tool is run through ``sh -c`` with the event's JSON on standard input and ``CLAUDE_PROJECT_DIR`` set
to the project (W1-05's ``run_commands``). The hook's environment is built from scratch (no ``PYTHONPATH``): this
worktree's ``gov`` is importable for the stand-in home through a path file in its user site folder, as an editable
install leaves one (W2-90's ``install_gov_for``). So the guard that answers is this worktree's ``src/gov`` (DEC-732).

**The base.** "Before" is the template as it stood before this ticket: ``template/.rulesync/permissions.jsonc`` at
``BASE_COMMIT``, the commit of DEC-664's round, the last to change the file on ``w2/integrate`` before W2-105.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS = REPO_ROOT / "tests" / "acceptance"
if str(_TESTS / "W2-90") not in sys.path:
    sys.path.insert(0, str(_TESTS / "W2-90"))

import w2_90_kernel_wiring as kernel_wiring  # noqa: E402  (the generated project; puts W1-05, W1-38, W1-39 on the path)
import w1_38_hooks_support as hooks  # noqa: E402  (the rulesync source reader; a refusal that is the program's own)

live_support = kernel_wiring.live_support          # W1-05: the settings' deny rules, hook input, registered commands
rulesync_support = kernel_wiring.rulesync_support  # W1-38: rulesync generate
check_support = hooks.check_support                # W1-03: a ticket file, a hook's answer read as the harness reads it

SOURCE_REL = "template/.rulesync/permissions.jsonc"   # the ticket's one path
PROJECT_SOURCE_REL = ".rulesync/permissions.jsonc"    # where Copier puts it in the project
SETTINGS_REL = kernel_wiring.SETTINGS_REL
BASE_COMMIT = "74d83913a86b"   # DEC-664's round: the template's permission source on w2/integrate before W2-105

# The two rules DEC-966 item 1 removes, as the source gives them and as rulesync generates them.
INSTALL_SOURCE_RULES = frozenset({("bash", "npm install*", "deny"), ("bash", "pip install*", "deny")})
INSTALL_GENERATED_RULES = Counter({("deny", "Bash(npm install*)"): 1, ("deny", "Bash(pip install*)"): 1})

# One install for each removed rule.
INSTALLS = ("npm install -g ccusage", "pip install requests")
RULE_LISTS = ("deny", "ask", "allow")
PERMISSION_MODES = ("default", "auto", "acceptEdits")

ORCHESTRATOR = "orchestrator"
ENGINEER = "engineer"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
PRODUCT_SPEC = "product-spec"
RESEARCH = "research"
NO_ROLE = "no-role"
OTHER_ROLES = (ENGINEER, TEST_DESIGNER, AUDITOR, PRODUCT_SPEC)
EXPERIMENT_REL = "experiments/spikes/exp-901"

# (ticket id, the ticket's role, its allowed paths). The orchestrator's is its coordination ticket. The test
# designer works on the engineer's ticket (MR-3); every other role has a ticket of its own.
COORDINATION_TICKET = "DAEO-zz91"
TICKETS = {
    "DAEO-zz90": (ENGINEER, ("src/app/**", "tests/unit/**")),
    COORDINATION_TICKET: (ORCHESTRATOR, ("docs/**",)),
    "DAEO-zz92": (PRODUCT_SPEC, ("docs/spec/**",)),
    "DAEO-zz93": (AUDITOR, ("docs/audit/**",)),
    "DAEO-zz97": (RESEARCH, (f"{EXPERIMENT_REL}/**",)),
}
TICKET_OF = {ENGINEER: "DAEO-zz90", TEST_DESIGNER: "DAEO-zz90", ORCHESTRATOR: COORDINATION_TICKET,
             PRODUCT_SPEC: "DAEO-zz92", AUDITOR: "DAEO-zz93", RESEARCH: "DAEO-zz97", NO_ROLE: None}


# --------------------------------------------------------------------------
# The project
# --------------------------------------------------------------------------

def make_project(base):
    """A project generated from the template (Copier, then rulesync generate), with a ticket in progress for each
    role, a product file and the research ticket's experiment folder, committed. Never run a hook in it."""
    project = kernel_wiring.generate_project(base)
    files = {"README.md": "# A product of the Gov OS kernel\n", "src/app/main.py": "VALUE = 1\n",
             f"{EXPERIMENT_REL}/README.md": "# Experiment 901\n"}
    for number, (ticket_id, (role, paths)) in enumerate(sorted(TICKETS.items()), start=1):
        files[f".tickets/{ticket_id}.md"] = check_support.ticket_text(
            ticket_id=ticket_id, wbs_id=f"W2-9{number}", role=role, allowed_paths=paths)
    return kernel_wiring.plant(project, files, "a ticket for each role, a product file, the experiment folder")


def make_sandbox(base):
    """A stand-in home and temporary folder, with this worktree's ``gov`` importable as an install makes it."""
    box = live_support.make_sandbox(base)
    kernel_wiring.install_gov_for(box.home)
    return box


def load_settings(project):
    return kernel_wiring.load_settings(project)


def base_source_text():
    """The template's permission source at ``BASE_COMMIT``, read from this repository's history."""
    proc = subprocess.run(["git", "-C", str(REPO_ROOT), "show", f"{BASE_COMMIT}:{SOURCE_REL}"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, (
        f"the template's permission source before this ticket ({BASE_COMMIT}:{SOURCE_REL}) cannot be read from "
        f"this repository's history: {proc.stderr.strip()}"
    )
    return proc.stdout


def generate_with_source(pristine, destination, source_text):
    """The settings rulesync generates in a copy of ``pristine`` whose ``.rulesync/permissions.jsonc`` is
    ``source_text``: what a project made from that source would be given."""
    project = kernel_wiring.copy_project(pristine, destination)
    (project / PROJECT_SOURCE_REL).write_text(source_text, encoding="utf-8")
    generated = rulesync_support.run_rulesync_generate(project)
    assert generated.returncode == 0, (
        f"rulesync generate failed in a copy of the generated project given the base source "
        f"(exit {generated.returncode}): {generated.stderr[-1500:]}"
    )
    return load_settings(project)


# --------------------------------------------------------------------------
# The rules, by name
# --------------------------------------------------------------------------

def source_rules(source, name):
    """``{(category, pattern, value)}`` for every rule of a rulesync permission source."""
    block = source.get("permission") if isinstance(source, dict) else None
    assert isinstance(block, dict), f"{name} holds no `permission` map"
    rules = set()
    for category, patterns in block.items():
        assert isinstance(patterns, dict), f"{name}: `permission.{category}` is not a map of patterns"
        for pattern, value in patterns.items():
            rules.add((category, pattern, value))
    return rules


def template_source_rules():
    return source_rules(kernel_wiring.load_jsonc(REPO_ROOT / SOURCE_REL), SOURCE_REL)


def base_source_rules():
    name = f"{BASE_COMMIT}:{SOURCE_REL}"
    return source_rules(hooks.parse_source(base_source_text(), name), name)


def permissions_of(settings):
    permissions = settings.get("permissions", {})
    assert isinstance(permissions, dict), f"{SETTINGS_REL} holds a `permissions` entry that is not a map"
    return permissions


def generated_rules(settings):
    """``Counter({(list name, rule): times})`` over every list of the settings' ``permissions`` map."""
    found = Counter()
    for kind, rules in permissions_of(settings).items():
        if isinstance(rules, list):
            found.update((kind, rule) for rule in rules)
    return found


def other_permission_entries(settings):
    """The entries of ``permissions`` that are not rule lists (a default mode, a folder list), by key."""
    return {kind: value for kind, value in permissions_of(settings).items() if not isinstance(value, list)}


def matching_rule(rules, command, project):
    """The first of ``rules`` (``Tool(spec)`` strings) that binds the Bash ``command``, read as W1-05 reads a
    settings rule, or ``None``."""
    return live_support.denied_by_settings({"permissions": {"deny": list(rules)}}, "Bash",
                                           live_support.bash_input(command), project)


def settings_rule_for(settings, kind, command, project):
    rules = permissions_of(settings).get(kind, [])
    return matching_rule(rules if isinstance(rules, list) else [], command, project)


# --------------------------------------------------------------------------
# A call, decided as the harness decides it
# --------------------------------------------------------------------------

_NUMBERS = iter(range(1, 1_000_000))


def _program_answer(result):
    """What the guard's program itself answered (exit 0 and its written decision), or how it ended."""
    if result.returncode != 0:
        return f"exit {result.returncode}"
    try:
        data = json.loads(result.stdout.strip() or "null")
    except ValueError:
        return "allow"
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    decision = specific.get("permissionDecision") if isinstance(specific, dict) else None
    return decision if decision in ("deny", "ask", "allow") else "allow"


@dataclass(frozen=True)
class Asked:
    command: str
    who: str
    deny_rule: str | None   # the settings deny rule that refuses before any hook, or None
    other_rules: dict       # {"ask": rule or None, "allow": rule or None}: a settings rule deciding too
    results: tuple          # the registered PreToolUse commands' results. Run whatever the settings say, so a
                            # message can tell what the guard would have answered; the harness runs them only
                            # when no deny rule refused first.

    @property
    def answers(self):
        return [_program_answer(result) for result in self.results]

    @property
    def reaches_the_guard(self):
        return self.deny_rule is None and bool(self.results)

    @property
    def asked_by_the_guard(self):
        """No settings rule decides; every registered command ended with 0; none refused; the guard asked."""
        return (self.reaches_the_guard and not any(self.other_rules.values())
                and all(result.returncode == 0 for result in self.results)
                and "deny" not in self.answers and "ask" in self.answers)

    @property
    def refused_by_the_guard(self):
        """No settings deny rule refused first, and the guard's program itself refused (exit 0 and its written
        refusal; an exit 2 is also what an interpreter gives that did not find the program)."""
        return self.reaches_the_guard and any(hooks.refused_by_the_program(result) for result in self.results)

    def describe(self):
        settings = f"settings deny rule {self.deny_rule}" if self.deny_rule else "no settings deny rule"
        others = {kind: rule for kind, rule in self.other_rules.items() if rule}
        if others:
            settings += f", settings rules {others}"
        reached = "the hook is asked" if self.deny_rule is None else "the harness never asks the hook"
        detail = "; ".join(result.describe() for result in self.results) or "no PreToolUse command is registered"
        return (f"`{self.command}` by {self.who}: {settings} ({reached}); the guard's own answer: "
                f"{self.answers or 'none'} [{detail}]")


def ask(project, settings, sandbox, command, who, permission_mode="default"):
    """What the generated settings and their PreToolUse commands decide about the Bash ``command`` in a session
    of ``who`` (a role on its ticket, or ``NO_ROLE``), started in the project's root."""
    role = None if who == NO_ROLE else who
    ticket = TICKET_OF[who]
    tool_input = live_support.bash_input(command)
    commands = live_support.hook_commands(settings, "PreToolUse", "Bash")
    stdin = live_support.hook_input(project, sandbox, "PreToolUse", "Bash", tool_input,
                                    permission_mode=permission_mode,
                                    tool_use_id=f"toolu_w2_105_{next(_NUMBERS):04d}")
    results = live_support.run_commands(project, commands, stdin, sandbox, role, ticket)
    who_text = who if ticket is None else f"{who} on {ticket}"
    return Asked(command, f"{who_text} ({permission_mode} mode)", settings_rule_for(settings, "deny", command, project),
                 {kind: settings_rule_for(settings, kind, command, project) for kind in ("ask", "allow")},
                 tuple(results))
