"""KPI 1 (DEC-911 item 4): a match of row W2-L423's rule that is exactly 40 hex digits naming a commit object of the
repository being scanned is no finding, for the secrets-indexing check and the pre-index filter, in a file and in a
stored value, after either of the rule's keywords.

Red today: the check names each file and store, and the filter leaves each path out (README, KPI 1).
"""

from __future__ import annotations

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

KEYWORD_CASES = {"vendor-keyword": support.VENDOR, "prefix-keyword": support.PREFIX}


def _several(repo):
    """A review log that quotes every commit of the repository, after both keywords, one a line."""
    return "".join(support.vendor_line(keyword, sha, verb=verb)
                   for keyword in support.KEYWORDS
                   for verb, sha in (("first commit", repo.first), ("merged head", repo.head),
                                     ("side branch at", repo.side)))


class Scene:
    """One project whose runtime folder and indexable folder hold commit hashes of its own repository only."""

    def __init__(self, sandbox):
        self.sandbox = sandbox
        self.repo = support.make_repo(sandbox, "exempt-project")
        root, head = self.repo.root, self.repo.head
        self.check_rels, self.filter_rels = {}, {}
        for name, keyword in KEYWORD_CASES.items():
            line = support.vendor_line(keyword, head)
            self.check_rels[("file", name)] = f".gov-runtime/scratch/review-{name}/review.log"
            support.write(root / self.check_rels[("file", name)], "a lead's review log\n" + line)
            self.check_rels[("store", name)] = f".gov-runtime/stores/review-{name}.db"
            support.sqlite_store(root / self.check_rels[("store", name)], ["a lead's review log", line])
            self.filter_rels[("file", name)] = f"docs/review-{name}.md"
            support.write(root / self.filter_rels[("file", name)], "# A review\n\n" + line)
            self.filter_rels[("store", name)] = f"docs/review-{name}.db"
            support.sqlite_store(root / self.filter_rels[("store", name)], ["a review", line])
        self.check_rels[("file", "every-commit")] = ".gov-runtime/scratch/every-commit/review.log"
        support.write(root / self.check_rels[("file", "every-commit")], _several(self.repo))
        self.filter_rels[("file", "every-commit")] = "docs/every-commit.md"
        support.write(root / self.filter_rels[("file", "every-commit")], _several(self.repo))
        self.check = support.run_check(sandbox, root)
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()))


@pytest.fixture(scope="module")
def scene(module_sandbox):
    return Scene(module_sandbox)


PLACES = [("file", "vendor-keyword"), ("file", "prefix-keyword"), ("store", "vendor-keyword"),
          ("store", "prefix-keyword"), ("file", "every-commit")]
IDS = [f"{form}-{name}" for form, name in PLACES]


# ---- premises ----------------------------------------------------------------------------------------------------

def test_premise_every_quoted_id_names_a_commit_of_the_project(scene):
    commits = [support.is_object(scene.repo.root, sha, "commit") for sha in scene.repo.commits]
    assert all(commits), f"a quoted id names no commit of the project: {commits}"


@pytest.mark.parametrize("name", list(KEYWORD_CASES))
def test_premise_the_line_is_a_finding_of_row_w2_l423s_rule_and_of_no_other(scene, name):
    line = support.vendor_line(KEYWORD_CASES[name], scene.repo.head)
    toml = support.gitleaks_toml()
    extended = support.gitleaks_finds(line, toml)
    alone = support.gitleaks_finds(line, support.project_rules_alone(toml))
    ok = extended == [support.RULE_ID] and alone == []
    assert ok, support.say(f"{name}: the rule sets find {extended} and {alone}, not row W2-L423's rule alone")


def test_premise_the_every_commit_log_is_a_finding_of_row_w2_l423s_rule_only(scene):
    toml = support.gitleaks_toml()
    extended = support.gitleaks_finds(_several(scene.repo), toml)
    alone = support.gitleaks_finds(_several(scene.repo), support.project_rules_alone(toml))
    ok = extended == [support.RULE_ID] and alone == []
    assert ok, support.say(f"the every-commit log: the rule sets find {extended} and {alone}")


# ---- the check -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES, ids=IDS)
def test_a_commit_hash_of_this_repository_beside_the_keyword_is_no_finding_of_the_check(scene, place):
    rel = scene.check_rels[place]
    assert scene.check.ended, f"the check did not end within its declared limit\n{scene.check.describe()}"
    named = scene.check.names(rel)
    assert not named, (f"the check reports {rel} (a commit hash of this repository after the rule's keyword, "
                       f"{place[0]}) as a finding\n{scene.check.describe()}")


def test_the_check_is_clean_on_a_runtime_folder_that_holds_only_commit_hashes_of_this_repository(scene):
    assert scene.check.returncode == 0, ("the check is not clean on a runtime folder whose only matches are commit "
                                         f"hashes of this repository\n{scene.check.describe()}")


# ---- the filter ----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES, ids=IDS)
def test_a_commit_hash_of_this_repository_beside_the_keyword_passes_the_filter(scene, place):
    rel = scene.filter_rels[place]
    passes = scene.filter.passes(rel)
    assert passes, (f"the filter leaves out {rel} (a commit hash of this repository after the rule's keyword, "
                    f"{place[0]})\n{scene.filter.describe()}")


# ---- beside real findings: the exemption is per match, the other files are still found -----------------------------

class Mixed:
    """A project with a commit hash after the keyword in one file and one store, and a real token of the vendor in
    another file and store: the check names the token's only, the filter passes the hash's only."""

    def __init__(self, sandbox):
        self.repo = support.make_repo(sandbox, "mixed-project", label="mixed")
        root = self.repo.root
        exempt = support.vendor_line(support.VENDOR, self.repo.head)
        token = f"the deploy token is {support.PREFIX}{support.hex_of('mixed-token')} for now\n"
        self.exempt = {"file": ".gov-runtime/scratch/exempt.log", "store": ".gov-runtime/stores/exempt.db"}
        self.token = {"file": ".gov-runtime/scratch/token.log", "store": ".gov-runtime/stores/token.db"}
        self.exempt_docs = {"file": "docs/exempt.md", "store": "docs/exempt.db"}
        self.token_docs = {"file": "docs/token.md", "store": "docs/token.db"}
        for rels, text in ((self.exempt, exempt), (self.token, token), (self.exempt_docs, exempt),
                           (self.token_docs, token)):
            support.write(root / rels["file"], text)
            support.sqlite_store(root / rels["store"], [text])
        self.check = support.run_check(sandbox, root)
        self.filter = support.run_filter(sandbox, root, sorted([*self.exempt_docs.values(),
                                                                *self.token_docs.values()]))


@pytest.fixture(scope="module")
def mixed(module_sandbox):
    return Mixed(module_sandbox)


@pytest.mark.parametrize("form", ["file", "store"])
def test_beside_a_real_token_the_check_names_the_token_and_not_the_commit_hash(mixed, form):
    assert mixed.check.ended, f"the check did not end\n{mixed.check.describe()}"
    token_named = mixed.check.names(mixed.token[form])
    exempt_named = mixed.check.names(mixed.exempt[form])
    assert token_named, f"the check does not name the token's {form}\n{mixed.check.describe()}"
    assert not exempt_named, (f"the check names the {form} that holds only a commit hash of this repository, beside "
                              f"a real finding elsewhere\n{mixed.check.describe()}")


@pytest.mark.parametrize("form", ["file", "store"])
def test_beside_a_real_token_the_filter_passes_the_commit_hash_and_not_the_token(mixed, form):
    token_passes = mixed.filter.passes(mixed.token_docs[form])
    exempt_passes = mixed.filter.passes(mixed.exempt_docs[form])
    assert not token_passes, f"the filter passes the token's {form}\n{mixed.filter.describe()}"
    assert exempt_passes, (f"the filter leaves out the {form} that holds only a commit hash of this repository\n"
                           f"{mixed.filter.describe()}")


# ---- a project that is a linked worktree: the commits of its repository, any branch --------------------------------

class Worktree:
    """A project that is a linked worktree of a repository built from scratch (as every ticket's worktree is): its
    runtime folder and indexable folder quote a commit of another branch and the repository's first commit."""

    def __init__(self, sandbox):
        self.repo = support.make_repo(sandbox, "worktree-main", label="worktree")
        self.root = sandbox.base / "worktree-project"
        support.git(self.repo.root, "worktree", "add", "-q", "-b", "ticket", str(self.root), "main")
        text = (support.vendor_line(support.VENDOR, self.repo.side)
                + support.vendor_line(support.PREFIX, self.repo.first))
        self.check_rels = {"file": ".gov-runtime/scratch/lead.log", "store": ".gov-runtime/stores/lead.db"}
        self.filter_rels = {"file": "docs/lead.md", "store": "docs/lead.db"}
        for rels in (self.check_rels, self.filter_rels):
            support.write(self.root / rels["file"], text)
            support.sqlite_store(self.root / rels["store"], [text])
        self.check = support.run_check(sandbox, self.root)
        self.filter = support.run_filter(sandbox, self.root, sorted(self.filter_rels.values()))


@pytest.fixture(scope="module")
def worktree(module_sandbox):
    return Worktree(module_sandbox)


def test_premise_the_worktree_quotes_commits_its_repository_holds(worktree):
    commits = [support.is_object(worktree.root, sha, "commit") for sha in (worktree.repo.side, worktree.repo.first)]
    assert all(commits), f"a quoted id is no commit of the worktree's repository: {commits}"


@pytest.mark.parametrize("form", ["file", "store"])
def test_in_a_linked_worktree_a_commit_of_its_repository_is_no_finding_of_the_check(worktree, form):
    assert worktree.check.ended, f"the check did not end\n{worktree.check.describe()}"
    named = worktree.check.names(worktree.check_rels[form])
    assert not named, (f"in a linked worktree the check reports the {form} that quotes commits of its repository\n"
                       f"{worktree.check.describe()}")


@pytest.mark.parametrize("form", ["file", "store"])
def test_in_a_linked_worktree_a_commit_of_its_repository_passes_the_filter(worktree, form):
    passes = worktree.filter.passes(worktree.filter_rels[form])
    assert passes, (f"in a linked worktree the filter leaves out the {form} that quotes commits of its repository\n"
                    f"{worktree.filter.describe()}")
