"""W1-02 — the allow-list: a role may write only inside its active ticket's ``allowed_paths``.

KPI success 1: "Edit/Write/Bash writes are allowed only inside the active ticket
allowed_paths plus the kernel scratch set, per role [CAP-39.a, CAP-58.a]".
KPI success 3, second clause: "the guard reads ticket frontmatter directly".
KPI failure 1: "Any write outside allowed_paths is allowed".

The session declares its role and ticket through ``GOV_ROLE`` and ``GOV_TICKET``
(owner answer to KD-1). File tools are tested here; Bash is in
``test_w1_02_bash_writes.py`` and the scratch set in ``test_w1_02_scratch.py``.

Path patterns are read as the W1-01 commit check reads them (DEC-097): anchored
at the repository root, ``**`` crosses directories, ``*`` stays in one name.
"""

from __future__ import annotations

import pytest

import w1_02_support as support

ENGINEER = support.ENGINEER
ORCHESTRATOR = support.ORCHESTRATOR
PRODUCT_SPEC = support.PRODUCT_SPEC
TICKET = support.TICKET_ID
ORCHESTRATOR_TICKET = support.ORCHESTRATOR_TICKET_ID
PRODUCT_SPEC_TICKET = support.PRODUCT_SPEC_TICKET_ID
DOCS_TICKET = support.DOCS_TICKET_ID

FILE_TOOLS = ["Edit", "Write"]

# The engineer on DAEO-zz90: src/gov/guard/**, tests/unit/guard/**,
# template/governance/kernel/hooks/pretooluse*, pyproject.toml.
INSIDE = {
    "existing-source": "src/gov/guard/decide.py",
    "new-file": "src/gov/guard/new_module.py",
    "new-file-in-new-directories": "src/gov/guard/sub/deep/module.py",
    "unit-test": "tests/unit/guard/test_decide.py",
    "name-prefix-pattern": "template/governance/kernel/hooks/pretooluse.py",
    "name-prefix-pattern-longer-name": "template/governance/kernel/hooks/pretooluse_guard.sh",
    "single-file-pattern": "pyproject.toml",
}

OUTSIDE = {
    "sibling-directory-with-the-same-prefix": "src/gov/guardian/other.py",
    "file-named-like-the-directory": "src/gov/guard.py",
    "parent-package": "src/gov/__init__.py",
    "other-source": "src/app/main.py",
    "other-unit-tests": "tests/unit/other/test_other.py",
    "name-prefix-pattern-sibling": "template/governance/kernel/hooks/posttooluse.py",
    "name-prefix-pattern-in-a-subdirectory": "template/governance/kernel/hooks/sub/pretooluse.py",
    "single-file-name-in-another-directory": "docs/pyproject.toml",
    "docs": "docs/notes.md",
    "root-file": "README.md",
    "own-ticket-file": f".tickets/{TICKET}.md",
    "other-ticket-file": f".tickets/{DOCS_TICKET}.md",
    "session-settings": ".claude/settings.json",
    "gitignore": ".gitignore",
    "git-directory": ".git/config",
    "freeze-flag": support.FREEZE_FLAG_REL,
    "findings-file": support.FINDINGS_REL,
    "path-no-ticket-names": "brand/new/file.txt",
    "dot-dot-to-other-source": "src/gov/guard/../../app/main.py",
    "dot-dot-to-the-root": "src/gov/guard/../../../README.md",
    "symlink-out-of-the-allowed-directory": "src/gov/guard/docs_link/notes.md",
}

OTHER_ROLES = {
    "orchestrator-settings": (ORCHESTRATOR, ORCHESTRATOR_TICKET, ".claude/settings.json", True),
    "orchestrator-bootstrap": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "governance/project/bootstrap.md", True),
    # DEC-156 (W1-45): the orchestrator may write anywhere except tests/acceptance/**.
    # Rewrite: owner correction, DEC-156. Previously False (denied outside ticket paths).
    "orchestrator-neighbour-file": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "governance/project/roster.yaml", True),
    "orchestrator-source": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "src/gov/guard/decide.py", True),
    "orchestrator-root-file": (ORCHESTRATOR, ORCHESTRATOR_TICKET, "README.md", True),
    "product-spec-role-file": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "template/governance/kernel/roles/engineer.md", True),
    "product-spec-spec": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "docs/spec/feature.md", True),
    "product-spec-new-spec": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "docs/spec/new/readiness.md", True),
    "product-spec-other-docs": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "docs/notes.md", False),
    "product-spec-source": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "src/gov/guard/decide.py", False),
    "product-spec-hook": (PRODUCT_SPEC, PRODUCT_SPEC_TICKET, "template/governance/kernel/hooks/pretooluse.py", False),
}

# A role that works on another role's ticket gets none of that ticket's paths.
MISMATCHED = {
    "engineer-on-orchestrator-ticket": (ENGINEER, ORCHESTRATOR_TICKET, ".claude/settings.json"),
    "engineer-on-product-spec-ticket": (ENGINEER, PRODUCT_SPEC_TICKET, "docs/spec/feature.md"),
    # DEC-156 (W1-45): the orchestrator cases are removed; the orchestrator may write
    # regardless of the active ticket.  Rewrite: owner correction, DEC-156.
    "product-spec-on-engineer-ticket": (PRODUCT_SPEC, TICKET, "src/gov/guard/decide.py"),
    "product-spec-on-orchestrator-ticket": (PRODUCT_SPEC, ORCHESTRATOR_TICKET, ".claude/settings.json"),
}

NO_TICKET = {
    "not-set": None,
    "empty": "",
    "no-such-ticket": "DAEO-none",
    "no-such-w1-id": "W1-99",
    "path-to-a-file-that-is-no-ticket": "../docs/notes",
}


@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(INSIDE), ids=sorted(INSIDE))
def test_engineer_can_write_inside_the_ticket_paths(project, write, tool_name, target):
    relpath = INSIDE[target]
    result = write(project, relpath, ENGINEER, TICKET, tool_name)
    support.assert_allowed(result, f"{tool_name} on {relpath} by the engineer on {TICKET}")


@pytest.mark.parametrize("tool_name", FILE_TOOLS)
@pytest.mark.parametrize("target", sorted(OUTSIDE), ids=sorted(OUTSIDE))
def test_engineer_cannot_write_outside_the_ticket_paths(project, write, tool_name, target):
    relpath = OUTSIDE[target]
    result = write(project, relpath, ENGINEER, TICKET, tool_name)
    support.assert_denied(result, f"{tool_name} on {relpath} by the engineer on {TICKET}")


@pytest.mark.parametrize("where", ["home", "next-to-the-project", "system-directory"])
def test_engineer_cannot_write_outside_the_repository(project, write, sandbox, where):
    target = {
        "home": sandbox.home / ".bashrc",
        "next-to-the-project": sandbox.elsewhere / "file.txt",
        "system-directory": "/etc/w1-02-acceptance-probe",
    }[where]
    for tool_name in FILE_TOOLS:
        result = write(project, target, ENGINEER, TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on {target} by the engineer on {TICKET}")


def test_engineer_cannot_rewrite_the_installed_guard(project, write):
    relpath = support.installed_hook_rel()
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, ENGINEER, TICKET, tool_name)
        support.assert_denied(result, f"{tool_name} on the guard hook {relpath} by the engineer")


def test_engineer_notebook_edits_follow_the_same_list(project, write):
    inside = write(project, "src/gov/guard/analysis.ipynb", ENGINEER, TICKET, "NotebookEdit")
    outside = write(project, "docs/analysis.ipynb", ENGINEER, TICKET, "NotebookEdit")
    support.assert_allowed(inside, "NotebookEdit inside the ticket paths")
    support.assert_denied(outside, "NotebookEdit outside the ticket paths")


@pytest.mark.parametrize("case", sorted(OTHER_ROLES), ids=sorted(OTHER_ROLES))
def test_each_ticket_role_gets_its_own_ticket_paths_only(project, write, case):
    role, ticket, relpath, allowed = OTHER_ROLES[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, role, ticket, tool_name)
        what = f"{tool_name} on {relpath} by {role} on {ticket}"
        if allowed:
            support.assert_allowed(result, what)
        else:
            support.assert_denied(result, what)


def test_the_list_follows_the_active_ticket(project, write):
    """Same role, two tickets: each call gets the paths of the ticket it names, and no other."""
    expectations = [
        (TICKET, "src/gov/guard/decide.py", True),
        (TICKET, "docs/notes.md", False),
        (DOCS_TICKET, "docs/notes.md", True),
        (DOCS_TICKET, "src/gov/guard/decide.py", False),
    ]
    for ticket, relpath, allowed in expectations:
        result = write(project, relpath, ENGINEER, ticket)
        what = f"Write on {relpath} by the engineer on {ticket}"
        if allowed:
            support.assert_allowed(result, what)
        else:
            support.assert_denied(result, what)


@pytest.mark.parametrize("case", sorted(MISMATCHED), ids=sorted(MISMATCHED))
def test_a_ticket_of_another_role_gives_no_paths(project, write, case):
    role, ticket, relpath = MISMATCHED[case]
    for tool_name in FILE_TOOLS:
        result = write(project, relpath, role, ticket, tool_name)
        support.assert_denied(result, f"{tool_name} on {relpath} by {role} on {ticket}, a ticket of another role")


@pytest.mark.parametrize("case", sorted(NO_TICKET), ids=sorted(NO_TICKET))
def test_a_known_role_without_a_ticket_gets_no_ticket_paths(project, write, case):
    ticket = NO_TICKET[case]
    for relpath in ("src/gov/guard/decide.py", "docs/notes.md", "README.md"):
        result = write(project, relpath, ENGINEER, ticket)
        support.assert_denied(result, f"Write on {relpath} by the engineer with GOV_TICKET={ticket!r}")


def test_role_and_ticket_are_read_on_every_call(project, write):
    """An earlier call leaves nothing behind that widens a later one."""
    relpath = "src/gov/guard/decide.py"
    support.assert_allowed(write(project, relpath, ENGINEER, TICKET), "the engineer's write")
    support.assert_denied(write(project, relpath), "the same write with no role and no ticket, one call later,")
    support.assert_denied(write(project, relpath, None, TICKET), "the same write with a ticket and no role")
    support.assert_denied(write(project, relpath, ENGINEER, None), "the same write with a role and no ticket")
    support.assert_allowed(write(project, relpath, ENGINEER, TICKET), "the engineer's write, declared again,")


def test_allowed_paths_come_straight_from_the_ticket_file(project, write):
    """A change to the ticket's frontmatter changes the next decision; no derived store is involved."""
    ticket_file = project / ".tickets" / f"{TICKET}.md"
    assert not (project / ".gov-runtime").exists(), "the fixture project must start without a runtime directory"

    support.assert_allowed(write(project, "src/gov/guard/decide.py", ENGINEER, TICKET), "the write inside the list")
    support.assert_denied(write(project, "docs/notes.md", ENGINEER, TICKET), "the write outside the list")

    ticket_file.write_text(
        support.ticket_text(allowed_paths=("src/gov/guard/**", "docs/**")), encoding="utf-8"
    )
    support.assert_allowed(
        write(project, "docs/notes.md", ENGINEER, TICKET),
        "the write to docs/, after docs/** was added to the ticket file,",
    )

    ticket_file.write_text(support.ticket_text(allowed_paths=("docs/**",)), encoding="utf-8")
    support.assert_denied(
        write(project, "src/gov/guard/decide.py", ENGINEER, TICKET),
        "the write to src/gov/guard/, after the pattern was removed from the ticket file,",
    )


def test_guard_reads_this_repository_s_own_ticket(hook, tmp_path, write):
    """The real W1-02 ticket file, as ``tk`` wrote it, set in progress."""
    ticket_id, text = support.real_ticket_text("W1-02")
    project = support.make_project(tmp_path / "project", {f"{ticket_id}.md": text})
    inside = (
        "src/gov/guard/decide.py",
        "tests/unit/guard/test_decide.py",
        "template/governance/kernel/hooks/pretooluse.py",
    )
    outside = (
        "tests/acceptance/W1-02/test_added.py",
        "template/governance/kernel/hooks/posttooluse.py",
        "src/gov/cli/main.py",
        "README.md",
    )
    for relpath in inside:
        support.assert_allowed(write(project, relpath, ENGINEER, ticket_id), f"Write on {relpath} under {ticket_id}")
    for relpath in outside:
        support.assert_denied(write(project, relpath, ENGINEER, ticket_id), f"Write on {relpath} under {ticket_id}")
