"""Run 2 (DEC-911 item 4, KPI 4; the orchestrator's decision P1-MORNING-2026-10-29 item 4): a repository counts as a
partial clone when the configuration git would use for it has ``extensions.partialClone`` set, any remote with
``promisor`` true (in git's spellings of a boolean) or any remote with a ``partialclonefilter``; one whose
configuration cannot be read counts as one too (fail closed). In such a repository a commit of its own history after
the rule's keyword stays a finding, and no request reaches the remote.

Each project is a full clone, over ``file://``, of a bare source built from scratch, with one setting added:

- ``promisor-only``: ``[Remote "origin"] Promisor = yes`` in the repository's own file (a mixed-case section and key,
  and ``yes`` for true); no filter, no extension;
- ``filter-only``: a ``partialclonefilter`` on the remote, and nothing else;
- ``extension-only``: ``extensions.partialClone = origin`` (format version 1), and nothing else;
- ``global-promisor``: ``promisor = true`` for the remote in the user's global file (a temporary ``HOME`` holding a
  ``.gitconfig``, ``XDG_CONFIG_HOME`` an empty folder, ``GIT_CONFIG_GLOBAL`` unset), not in the repository's file;
- ``included-promisor``: ``promisor = 1`` in a file the repository's own file includes (``include.path``);
- ``unreadable-config``: the repository's ``.git/config`` made unreadable (mode 000) for the runs;
- ``malformed-config``: a malformed line at the end of the repository's ``.git/config``.

git 2.43 lazy-fetches a missing object in each of the first five (measured; each scene's control shows it). Each
quotes its own head commit after each keyword (a log under ``.gov-runtime/`` for the check, a page under ``docs/``
for the filter) and, after the vendor keyword, a random 40-hex id that names nothing: code that asks git about it
sends it to the remote. Every request the remote serves is counted (``remote.origin.uploadpack``, a logging program).

Red on run 1's code in the first five: it exempts the own commit and its lookup of the random id reaches the remote.
The last two are guards, green today: git cannot read such a configuration, so run 1's verification fails and fails
closed (README, run 2).
"""

from __future__ import annotations

import functools
import os
import re

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

KEYWORD_CASES = {"vendor-keyword": support.VENDOR, "prefix-keyword": support.PREFIX}
PROMISOR_SCENES = ["promisor-only", "filter-only", "extension-only", "global-promisor", "included-promisor"]
UNREADABLE_SCENES = ["unreadable-config", "malformed-config"]
RANDOM_CHECK_REL = ".gov-runtime/scratch/random.log"
RANDOM_FILTER_REL = "docs/random.md"


def _append(path, text):
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


class Case:
    def __init__(self, sandbox, name):
        self.name = name
        self.clone = support.make_clone(sandbox, name, label=name)
        root = self.clone.root
        self.random = support.hex_of(f"run-2-{name}-random")
        self.check_rels, self.filter_rels = {}, {}
        for keyword_name, keyword in KEYWORD_CASES.items():
            line = support.vendor_line(keyword, self.clone.head)
            self.check_rels[keyword_name] = f".gov-runtime/scratch/own-commit-{keyword_name}.log"
            support.write(root / self.check_rels[keyword_name], "a lead's review log\n" + line)
            self.filter_rels[keyword_name] = f"docs/own-commit-{keyword_name}.md"
            support.write(root / self.filter_rels[keyword_name], "# A review\n\n" + line)
        random_line = support.vendor_line(support.VENDOR, self.random)
        support.write(root / RANDOM_CHECK_REL, "a lead's review log\n" + random_line)
        support.write(root / RANDOM_FILTER_REL, "# A review\n\n" + random_line)

        config = root / ".git/config"
        self.env = support.base_environment(sandbox)
        if name == "promisor-only":
            _append(config, '[Remote "origin"]\n\tPromisor = yes\n')
        elif name == "filter-only":
            _append(config, '[remote "origin"]\n\tpartialclonefilter = blob:none\n')
        elif name == "extension-only":
            support.git(root, "config", "core.repositoryformatversion", "1")
            _append(config, "[extensions]\n\tpartialClone = origin\n")
        elif name == "global-promisor":
            home = sandbox.base / f"{name}-home"
            support.write(home / ".gitconfig", '[remote "origin"]\n\tpromisor = true\n')
            empty = sandbox.base / f"{name}-xdg-config"
            empty.mkdir()
            self.env = {key: value for key, value in self.env.items() if key != "GIT_CONFIG_GLOBAL"}
            self.env.update(HOME=str(home), XDG_CONFIG_HOME=str(empty))
        elif name == "included-promisor":
            included = sandbox.elsewhere / f"{name}.gitconfig"
            support.write(included, '[remote "origin"]\n\tpromisor = 1\n')
            _append(config, f"[include]\n\tpath = {included}\n")
        elif name == "malformed-config":
            _append(config, "\n[broken\n")
        self.own_file = config.read_text(encoding="utf-8").lower()
        self.plain_config = support.config_list(root, support.base_environment(sandbox))
        if name == "unreadable-config":
            config.chmod(0)
        try:
            self.config_code, self.config = support.config_list(root, self.env)
            self.head_readable = support.lookup_by_the_test(root, self.clone.head, self.env) == 0
            before = self.clone.request_count()
            self.check = support.run_check(sandbox, root, env=self.env)
            after_check = self.clone.request_count()
            self.filter = support.run_filter(sandbox, root, sorted([*self.filter_rels.values(), RANDOM_FILTER_REL]),
                                             env=self.env)
            after_filter = self.clone.request_count()
        finally:
            if name == "unreadable-config":
                config.chmod(0o644)
        self.check_requests, self.filter_requests = after_check - before, after_filter - after_check
        # the control: the test's own plain lookup of another id that names nothing, in the same environment
        self.control_code = support.lookup_by_the_test(root, support.hex_of(f"run-2-{name}-control"), self.env)
        self.control_requests = self.clone.request_count() - after_filter


class Cases:
    """Each scene's project, built and judged the first time a case asks for it."""

    def __init__(self, sandbox):
        self.sandbox = sandbox

    @functools.cache
    def __getitem__(self, name):
        return Case(self.sandbox, name)


@pytest.fixture(scope="module")
def cases(module_sandbox):
    return Cases(module_sandbox)


PROMISOR_PLACES = [(scene, keyword) for scene in PROMISOR_SCENES for keyword in KEYWORD_CASES]
PROMISOR_IDS = [f"{scene}-{keyword}" for scene, keyword in PROMISOR_PLACES]
UNREADABLE_PLACES = [(scene, keyword) for scene in UNREADABLE_SCENES for keyword in KEYWORD_CASES]
UNREADABLE_IDS = [f"{scene}-{keyword}" for scene, keyword in UNREADABLE_PLACES]


# ---- premises ----------------------------------------------------------------------------------------------------

def _has(lines, key):
    return any(line.startswith(key + "=") for line in lines)


@pytest.mark.parametrize("name", PROMISOR_SCENES)
def test_premise_the_scene_is_configured_as_said(cases, name):
    case = cases[name]
    lines = case.config
    keys = {key: _has(lines, key) for key in ("remote.origin.promisor", "remote.origin.partialclonefilter",
                                              "extensions.partialclone")}
    expected = {
        "promisor-only": {"remote.origin.promisor": True, "remote.origin.partialclonefilter": False,
                          "extensions.partialclone": False},
        "filter-only": {"remote.origin.promisor": False, "remote.origin.partialclonefilter": True,
                        "extensions.partialclone": False},
        "extension-only": {"remote.origin.promisor": False, "remote.origin.partialclonefilter": False,
                           "extensions.partialclone": True},
        "global-promisor": {"remote.origin.promisor": True, "remote.origin.partialclonefilter": False,
                            "extensions.partialclone": False},
        "included-promisor": {"remote.origin.promisor": True, "remote.origin.partialclonefilter": False,
                              "extensions.partialclone": False},
    }[name]
    outside = name in ("global-promisor", "included-promisor")
    own_key = re.search(r"^\s*promisor\s*(=|$)", case.own_file, flags=re.MULTILINE) is not None
    own_file_ok = not own_key if outside else True
    spelling_ok = {"promisor-only": "remote.origin.promisor=yes" in lines,
                   "global-promisor": "remote.origin.promisor=true" in lines,
                   "included-promisor": "remote.origin.promisor=1" in lines}.get(name, True)
    ok = case.config_code == 0 and keys == expected and own_file_ok and spelling_ok and case.head_readable
    assert ok, (f"{name}: config read exit {case.config_code}; keys {keys}; the repository's own file free of the "
                f"setting: {own_file_ok}; the spelling as said: {spelling_ok}; the head readable: {case.head_readable}")


def test_premise_the_global_setting_is_read_only_through_the_users_file(cases):
    case = cases["global-promisor"]
    code, lines = case.plain_config
    assert code == 0 and not _has(lines, "remote.origin.promisor"), (
        "without the temporary HOME's .gitconfig the repository still has a promisor remote")


@pytest.mark.parametrize("name", PROMISOR_SCENES)
def test_premise_the_counter_sees_a_lazy_fetch_in_the_scene(cases, name):
    case = cases[name]
    assert case.control_requests >= 1, (f"{name}: the test's own lookup of a missing id reached the remote "
                                        f"{case.control_requests} times (exit code {case.control_code})")


@pytest.mark.parametrize("name", UNREADABLE_SCENES)
def test_premise_git_cannot_read_the_configuration(cases, name):
    case = cases[name]
    not_root = os.geteuid() != 0
    ok = not_root and case.config_code != 0 and not case.head_readable
    assert ok, (f"{name}: not root: {not_root}; config read exit {case.config_code}; git still reads the head commit: "
                f"{case.head_readable}")


def test_premise_the_own_commit_lines_are_findings_of_row_w2_l423s_rule(cases):
    toml = support.gitleaks_toml()
    wrong = []
    for name in PROMISOR_SCENES + UNREADABLE_SCENES:
        case = cases[name]
        for keyword_name, keyword in KEYWORD_CASES.items():
            if support.gitleaks_finds(support.vendor_line(keyword, case.clone.head), toml) != [support.RULE_ID]:
                wrong.append(f"{name}/{keyword_name}")
        if support.gitleaks_finds(support.vendor_line(support.VENDOR, case.random), toml) != [support.RULE_ID]:
            wrong.append(f"{name}/random")
    assert not wrong, support.say(f"lines that are not a finding of row W2-L423's rule alone: {wrong}")


# ---- a promisor remote, wherever it is configured: no exemption, nothing sent ------------------------------------

@pytest.mark.parametrize("place", PROMISOR_PLACES, ids=PROMISOR_IDS)
def test_with_a_promisor_remote_its_own_commit_stays_a_finding_of_the_check(cases, place):
    name, keyword_name = place
    case = cases[name]
    rel = case.check_rels[keyword_name]
    assert case.check.ended, f"{name}: the check did not end within its declared limit\n{case.check.describe()}"
    found = support.finds(case.check, rel)
    assert found, (f"{name}: the check passes {rel} (a commit of the repository's own history after the rule's "
                   f"keyword, with a promisor remote) as clean\n{case.check.describe()}")


@pytest.mark.parametrize("place", PROMISOR_PLACES, ids=PROMISOR_IDS)
def test_with_a_promisor_remote_its_own_commit_is_left_out_by_the_filter(cases, place):
    name, keyword_name = place
    case = cases[name]
    rel = case.filter_rels[keyword_name]
    assert case.filter.ended, f"{name}: the filter did not end\n{case.filter.describe()}"
    passes = case.filter.passes(rel)
    assert not passes, (f"{name}: the filter lets {rel} (a commit of the repository's own history, with a promisor "
                        f"remote) through\n{case.filter.describe()}")


@pytest.mark.parametrize("name", PROMISOR_SCENES)
def test_with_a_promisor_remote_the_check_sends_nothing_to_the_remote(cases, name):
    case = cases[name]
    assert case.check.ended, f"{name}: the check did not end\n{case.check.describe()}"
    assert case.check_requests == 0, f"{name}: the check's run reached the remote {case.check_requests} times"


@pytest.mark.parametrize("name", PROMISOR_SCENES)
def test_with_a_promisor_remote_the_filter_sends_nothing_to_the_remote(cases, name):
    case = cases[name]
    assert case.filter.ended, f"{name}: the filter did not end\n{case.filter.describe()}"
    assert case.filter_requests == 0, f"{name}: the filter's run reached the remote {case.filter_requests} times"


# ---- a configuration that cannot be read: fails closed -------------------------------------------------------------

@pytest.mark.parametrize("place", UNREADABLE_PLACES, ids=UNREADABLE_IDS)
def test_with_a_configuration_that_cannot_be_read_its_own_commit_stays_a_finding_of_the_check(cases, place):
    name, keyword_name = place
    case = cases[name]
    rel = case.check_rels[keyword_name]
    assert case.check.ended, f"{name}: the check did not end within its declared limit\n{case.check.describe()}"
    closed = support.check_fails_closed(case.check, rel, [*case.check_rels.values(), RANDOM_CHECK_REL])
    assert closed, (f"{name}: the check passes {rel} (a commit of the repository's own history, its configuration "
                    f"unreadable) as clean\n{case.check.describe()}")


@pytest.mark.parametrize("place", UNREADABLE_PLACES, ids=UNREADABLE_IDS)
def test_with_a_configuration_that_cannot_be_read_its_own_commit_is_left_out_by_the_filter(cases, place):
    name, keyword_name = place
    case = cases[name]
    rel = case.filter_rels[keyword_name]
    assert case.filter.ended, f"{name}: the filter did not end\n{case.filter.describe()}"
    passes = case.filter.passes(rel)
    assert not passes, (f"{name}: the filter lets {rel} (its configuration unreadable) through\n"
                        f"{case.filter.describe()}")
