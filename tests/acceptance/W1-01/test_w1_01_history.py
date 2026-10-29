"""W1-01: what git history and the ticket records show while the bootstrap holds."""

from __future__ import annotations

import os
import re
import subprocess

import pytest

import w1_01_support as support

ACCEPTANCE_PROBE = ("Edit", "tests/acceptance/W1-02/test_guard.py")
INSTALL_PROBE = ("Bash", "pip install requests")


@pytest.mark.parametrize(
    "probe",
    [
        pytest.param(ACCEPTANCE_PROBE, id="acceptance-tests"),
        pytest.param(INSTALL_PROBE, id="installs"),
    ],
)
def test_interim_rule_stays_in_force_once_introduced(interim, repo_root, probe):
    """KPI success 1 and 3: from the state that introduces a rule to now, no state drops it."""
    tool, target = probe
    states = support.settings_states(repo_root)
    in_force = [bool(support.denying_rules(rules, tool, target, repo_root)) for _, rules in states]
    assert any(in_force), (
        f"no state of {support.SETTINGS_REL} (history or working tree) denies {tool} `{target}`"
    )
    first = in_force.index(True)
    dropped = [label for (label, _), ok in zip(states[first:], in_force[first:]) if not ok]
    assert not dropped, (
        f"{tool} `{target}` was denied from {states[first][0]} but not in: {', '.join(dropped)}"
    )


def test_only_the_test_designer_commits_to_acceptance_tests(repo_root, deny_rules, w1_05_landed):
    """KPI failure 1: no implementer commit touches tests/acceptance/** before W1-05 lands.

    DEC-253 (rewrite after implementation, "owner decision: integration merges"):
    a merge commit passes when every change it brings under tests/acceptance/
    comes from commits on the merged side carrying the test designer's role.

    DEC-906 item 2 (rewrite, W2-70): a non-merge commit without the test
    designer's role passes only when its full id is listed in the path map's
    ``acceptance_exemptions`` ({commit: <full sha>, decision: <DEC id>}, beside
    ``accepted_history``). Any other commit stays red, an owner's included: a
    ``Role: owner`` trailer alone exempts nothing until W2-44 binds trailers to
    the launch. The list's only entry is the owner's own commit
    ``c9a08678644485a7528bc875164e110881b63d93``, citing DEC-900.

    Expected red until that entry is committed: this case fails naming
    ``c9a086786444``. It is the owner's entry, not this ticket's; once it is in,
    the case is green. (A note for W1-01's README, which is not in W2-70's
    paths.)
    """
    if not w1_05_landed:
        tool, target = ACCEPTANCE_PROBE
        assert support.denying_rules(deny_rules, tool, target, repo_root), (
            f"the interim guardrail is not in force: {tool} on {target} is not denied"
        )
    offenders = support.acceptance_test_offenders(repo_root)
    assert not offenders, (
        "commits touch tests/acceptance/** without the trailer "
        f"`Role: {support.TEST_DESIGNER_ROLE}`, and are not listed by their full id in "
        f"{support.PATH_MAP_REL} `{support.EXEMPTIONS_KEY}`:\n" + "\n".join(offenders)
    )


# --------------------------------------------------------------------------
# DEC-906 item 2: the exemption list, against repositories built here
# --------------------------------------------------------------------------

_FIXTURE_TEST = "tests/acceptance/W1-99/test_fixture.py"
# Fixed author, committer and dates: two commits differ in their id only by what they hold.
_FIXTURE_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
    "GIT_AUTHOR_NAME": "The owner", "GIT_AUTHOR_EMAIL": "owner@example.invalid",
    "GIT_COMMITTER_NAME": "The owner", "GIT_COMMITTER_EMAIL": "owner@example.invalid",
    "GIT_AUTHOR_DATE": "2026-10-23T09:00:00Z", "GIT_COMMITTER_DATE": "2026-10-23T09:00:00Z",
}


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), "-c", "commit.gpgsign=false", *args], capture_output=True,
                          text=True, check=False, env=dict(os.environ, **_FIXTURE_ENV))
    assert proc.returncode == 0, f"git {' '.join(args)} failed in the fixture repository: {proc.stderr.strip()}"
    return proc.stdout.strip()


def _commit(repo, files, subject, role):
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", subject, "--trailer", "Task: decision-record", "--trailer", f"Role: {role}")
    return _git(repo, "rev-parse", "HEAD")


def _fixture_repo(directory):
    """A repository with one commit outside tests/acceptance/ (the same id in every fixture repository)."""
    directory.mkdir()
    _git(directory, "init", "-q", "-b", "main")
    _commit(directory, {"README.md": "# fixture\n"}, "base", "orchestrator")
    return directory


def _path_map(repo, body):
    """The fixture's stand-in path map, in the working tree, where the case reads this repository's."""
    path = repo / support.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("version: 1\naccepted_history: []\n" + body, encoding="utf-8")


def _listing(*shas, decision="DEC-900"):
    return f"{support.EXEMPTIONS_KEY}:\n" + "".join(f'  - commit: "{sha}"\n    decision: {decision}\n' for sha in shas)


def _named(sha, offenders):
    return any(line.split()[0] == sha[:12] for line in offenders)


def test_a_listed_owner_commit_is_not_an_offender(tmp_path):
    """DEC-906 item 2: a non-merge ``Role: owner`` commit touching tests/acceptance/, listed by its full id."""
    repo = _fixture_repo(tmp_path / "repo")
    listed = _commit(repo, {_FIXTURE_TEST: "VALUE = 1\n"}, "Owner decision: a retirement", "owner")
    _commit(repo, {_FIXTURE_TEST: "VALUE = 2\n"}, "the designer revises", support.TEST_DESIGNER_ROLE)
    assert listed in support.commits_touching("tests/acceptance", repo), "premise: the owner commit touches tests"
    _path_map(repo, _listing(listed))
    assert support.acceptance_test_offenders(repo) == [], f"{listed} is listed by its full id and is still named"


@pytest.mark.parametrize("listing", ["the-first-only", "empty-list", "no-key", "no-path-map"])
def test_an_unlisted_owner_commit_stays_an_offender(tmp_path, listing):
    """Any other owner commit stays red; a path map with no list or an empty one exempts nothing."""
    repo = _fixture_repo(tmp_path / "repo")
    first = _commit(repo, {_FIXTURE_TEST: "VALUE = 1\n"}, "Owner decision: a retirement", "owner")
    second = _commit(repo, {_FIXTURE_TEST: "VALUE = 2\n"}, "Owner decision: another retirement", "owner")
    if listing != "no-path-map":
        _path_map(repo, {"the-first-only": _listing(first), "empty-list": f"{support.EXEMPTIONS_KEY}: []\n",
                         "no-key": ""}[listing])
    offenders = support.acceptance_test_offenders(repo)
    assert _named(second, offenders), f"the unlisted owner commit {second[:12]} is not an offender: {offenders}"
    assert _named(first, offenders) is (listing != "the-first-only"), (
        f"the owner commit {first[:12]} with {listing}: {offenders}"
    )


def test_only_the_exact_listed_commit_is_exempt(tmp_path):
    """A look-alike of the listed commit (same parent, message, trailers, author and dates, other content) has
    another full id and stays red; an abbreviated id of a real offender exempts nothing."""
    subject = "Owner decision DEC-900: a retirement"
    twin = _fixture_repo(tmp_path / "twin")
    listed = _commit(twin, {_FIXTURE_TEST: "VALUE = 'as listed'\n"}, subject, "owner")
    repo = _fixture_repo(tmp_path / "repo")
    assert _git(repo, "rev-parse", "HEAD") == _git(twin, "rev-parse", f"{listed}^"), "premise: the same parent"
    look_alike = _commit(repo, {_FIXTURE_TEST: "VALUE = 'other content'\n"}, subject, "owner")
    assert look_alike != listed, "premise: the look-alike's content differs, so its id differs"
    assert _git(repo, "show", "-s", "--format=%B%an%ae%ad%cd", look_alike) == \
        _git(twin, "show", "-s", "--format=%B%an%ae%ad%cd", listed), "premise: message, trailers, author and dates match"
    _path_map(repo, _listing(listed, look_alike[:7], look_alike[:12], look_alike[:39]))
    offenders = support.acceptance_test_offenders(repo)
    assert offenders == [look_alike[:12]], (
        f"the look-alike {look_alike[:12]} of the listed {listed[:12]}, listed only by abbreviated ids, "
        f"is not the one offender: {offenders}"
    )


def test_implementer_commits_stay_inside_allowed_paths(bootstrap_text, repo_root):
    """KPI success 2 (KD-1): the diff procedure is "used" — git history is the record.

    Until W1-05 lands, a commit that names a ticket in a ``Task:`` trailer, and is
    not a test-designer commit, touches only that ticket's ``allowed_paths`` and
    the ticket's own file in ``.tickets/``.
    """
    offenders = []
    for sha, message in support.interim_commits(repo_root):
        tasks = support.trailer_values(message, "Task")
        if not tasks or support.TEST_DESIGNER_ROLE in support.trailer_values(message, "Role"):
            continue
        allowed, unknown = [], []
        for task in tasks:
            found = support.ticket_file(task, repo_root)
            if found:
                allowed.append(found[0])
                allowed.extend(found[1].get("allowed_paths", []))
            elif re.fullmatch(r"W1-\d+", task):
                unknown.append(task)
        if unknown:
            offenders.append(f"{sha[:12]}: Task {', '.join(unknown)} names no ticket")
        if not allowed:
            continue
        outside = [p for p in support.changed_paths(sha, repo_root)
                   if not support.path_in_globs(p, allowed)]
        if outside:
            offenders.append(f"{sha[:12]} (Task {', '.join(tasks)}): {', '.join(outside)}")
    assert not offenders, "commits touch paths outside their ticket's allowed_paths:\n" + "\n".join(
        offenders
    )


def _depends_on(fields, wbs_id, root):
    """Whether a ticket's ``depends_on`` names the ticket ``wbs_id``, by its W1 id or by its ticket id: a ticket
    file holds either form (DEC-620)."""
    named = support.ticket(wbs_id, root) or {}
    return bool({wbs_id, named.get("id")} & set(fields.get("depends_on", [])))


@pytest.mark.parametrize("named_as", ["W1-05", "PROJ-aaaa", None], ids=["the W1 id", "the ticket id", "not named"])
def test_a_dependency_is_read_in_either_form_of_the_id(named_as, tmp_path):
    """Two ticket files written here, W1-06's ``depends_on`` in each form and without the dependency."""
    tickets = tmp_path / ".tickets"
    tickets.mkdir()
    (tickets / "PROJ-aaaa.md").write_text("---\nid: PROJ-aaaa\nwbs_id: W1-05\nstatus: open\n---\n", encoding="utf-8")
    listed = f"depends_on:\n- {named_as}\n- W1-02\n" if named_as else "depends_on:\n- W1-02\n- PROJ-zzzz\n"
    (tickets / "PROJ-bbbb.md").write_text(f"---\nid: PROJ-bbbb\nwbs_id: W1-06\nstatus: open\n{listed}---\n",
                                          encoding="utf-8")
    assert _depends_on(support.ticket("W1-06", tmp_path), "W1-05", tmp_path) is (named_as is not None)


def test_no_install_is_recorded_before_w1_05(interim, repo_root, deny_rules):
    """KPI failure 3: installs stay denied, and W1-06 (the first install) waits for W1-05."""
    tool, target = INSTALL_PROBE
    assert support.denying_rules(deny_rules, tool, target, repo_root), (
        f"the interim install rule is not in force: {tool} `{target}` is not denied"
    )
    w1_06 = support.ticket("W1-06", repo_root)
    assert w1_06 is not None, "no ticket with wbs_id W1-06 in .tickets/"
    assert _depends_on(w1_06, "W1-05", repo_root), "W1-06 no longer depends on W1-05"
    assert w1_06.get("status") == "open", (
        f"W1-06 (tool installs) is {w1_06.get('status')} while W1-05 is not closed"
    )
    registry = repo_root / support.TOOL_REGISTRY_REL
    assert not registry.exists(), (
        f"{support.TOOL_REGISTRY_REL} records installs while W1-05 is not closed"
    )
