"""KPI 3 (DEC-911 item 4, DEC-298): only that rule and only that match. Each case below quotes something that is no
exact 40-hex match of row W2-L423's rule naming a commit of the repository scanned, and stays a finding of the check
and of the pre-index filter, in a file and in a stored value:

- a finding of another rule whose match is, or holds, a commit hash of this repository (a default rule of gitleaks,
  a project rule whose match is the bare hash, a project token rule); the same hash found by row W2-L423's rule and
  another rule; a file that holds an exempt hash and another rule's finding;
- a match of row W2-L423's rule that holds a commit hash of this repository in a prefixed form; a commit of another
  repository; a tree id and a blob id of this repository;
- a match of 39 or 41 hex digits and a shortened hash: the rule never matches these today (README), so the project
  rewrites the rule's expression (same id) to match them, and the cases show the exemption does not widen to them,
  although git resolves the 39-digit and the 12-digit prefixes to the commit.

Guards, green today: today's check and filter find each. They must stay green.
"""

from __future__ import annotations

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

PLACES = ["file", "store"]
V, P = support.VENDOR, support.PREFIX


# ---- scene 1: the kernel's rules and one project rule of a bare 40-hex value -------------------------------------

def other_cases(repo, other):
    """{case: (the text, the rule ids each rule set must find: extended, alone)}."""
    head = repo.head
    other_token = support.token_digit("another-rule-beside-the-hash")
    deploy = "the deploy token is {} for now\n"
    return {
        "default-rule-whose-secret-is-the-commit-hash":
            (f'zendesk_secret = "{head}"\n', ([support.ZENDESK_RULE], [])),
        "project-rule-whose-match-is-the-commit-hash":
            (f"{support.PROJECT_HEX_KEYWORD} {head} recorded\n",
             ([support.PROJECT_HEX_RULE], [support.PROJECT_HEX_RULE])),
        "project-token-rule-whose-match-holds-the-commit-hash":
            (f"the key is {support._joined('to', 'k_')}{head} here\n", ("project-token", "project-token")),
        "same-hash-found-by-row-w2-l423s-rule-and-another":
            (f'{V} zendesk_secret = "{head}"\n', (sorted([support.RULE_ID, support.ZENDESK_RULE]), [])),
        "exempt-hash-and-another-rules-finding-in-one-text":
            (support.vendor_line(V, head) + f"the key is {other_token} here\n",
             (sorted([support.RULE_ID, "gov-token-digit"]), ["gov-token-digit"])),
        "prefixed-form-holding-the-commit-hash":
            (deploy.format(P + head), ([support.RULE_ID], [])),
        "prefixed-16-form-holding-the-commit-hash":
            (deploy.format(f"{P}{support.hex_of('commit-16', 16)}_{head}"), ([support.RULE_ID], [])),
        "prefixed-local-form-holding-the-commit-hash":
            (deploy.format(f"{P}local_{head}"), ([support.RULE_ID], [])),
        "commit-of-another-repository-after-vendor-keyword":
            (support.vendor_line(V, other), ([support.RULE_ID], [])),
        "commit-of-another-repository-after-prefix-keyword":
            (support.vendor_line(P, other), ([support.RULE_ID], [])),
        "tree-id-of-this-repository":
            (support.vendor_line(V, repo.tree, verb="tree"), ([support.RULE_ID], [])),
        "blob-id-of-this-repository":
            (support.vendor_line(P, repo.blob, verb="blob"), ([support.RULE_ID], [])),
    }


# The case names, from a stand-in repository (no git object: only the names are read).
_NAMES_ONLY = support.Repo(None, "0" * 40, "0" * 40, "0" * 40, "0" * 40, "0" * 40)
OTHER_CASES = list(other_cases(_NAMES_ONLY, "0" * 40))


class Scene:
    def __init__(self, sandbox, name, extra_rules, cases_of):
        self.repo = support.make_repo(sandbox, name, extra_rules=extra_rules, label=name)
        self.other = support.other_repository_commit(sandbox, f"{name}-other-repository")
        self.toml = support.gitleaks_toml(extra_rules)
        self.cases = cases_of(self)
        root = self.repo.root
        self.check_rels, self.filter_rels = {}, {}
        for case, (text, _) in self.cases.items():
            self.check_rels[(case, "file")] = f".gov-runtime/scratch/{case}.log"
            self.check_rels[(case, "store")] = f".gov-runtime/stores/{case}.db"
            self.filter_rels[(case, "file")] = f"docs/{case}.md"
            self.filter_rels[(case, "store")] = f"docs/{case}.db"
            for rels in (self.check_rels, self.filter_rels):
                support.write(root / rels[(case, "file")], "a log\n" + text)
                support.sqlite_store(root / rels[(case, "store")], ["a log", text])
        self.check = support.run_check(sandbox, root)
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()))


@pytest.fixture(scope="module")
def others(module_sandbox):
    return Scene(module_sandbox, "others", support.project_hex_rule(),
                 lambda scene: other_cases(scene.repo, scene.other))


def _premise(scene, case):
    text, (want_extended, want_alone) = scene.cases[case]
    extended = support.gitleaks_finds(text, scene.toml)
    alone = support.gitleaks_finds(text, support.project_rules_alone(scene.toml))

    def meets(found, want):
        if want == "project-token":
            return len(found) == 1 and found[0] in support.PROJECT_TOKEN_RULES
        return found == want

    ok = meets(extended, want_extended) and meets(alone, want_alone)
    assert ok, support.say(f"{case}: the rule sets find {extended} and {alone}; the case wants {want_extended} and "
                           f"{want_alone}")


@pytest.mark.parametrize("case", OTHER_CASES)
def test_premise_the_text_is_a_finding_of_the_rules_the_case_names(others, case):
    _premise(others, case)


def test_premise_the_quoted_ids_are_what_the_cases_say(others):
    root, repo = others.repo.root, others.repo
    facts = {
        "the head is a commit here": support.is_object(root, repo.head, "commit"),
        "the other repository's commit is no object here": not support.is_object(root, others.other, None),
        "the tree id is a tree here": support.is_object(root, repo.tree, "tree"),
        "the tree id is no commit here": not support.is_object(root, repo.tree, "commit"),
        "the blob id is a blob here": support.is_object(root, repo.blob, "blob"),
        "the blob id is no commit here": not support.is_object(root, repo.blob, "commit"),
    }
    assert all(facts.values()), f"premises that do not hold: {[k for k, v in facts.items() if not v]}"


def test_premise_the_secret_of_the_default_rules_finding_is_the_commit_hash(others):
    text, _ = others.cases["default-rule-whose-secret-is-the-commit-hash"]
    same = support.gitleaks_secret_is(text, others.toml, support.ZENDESK_RULE, others.repo.head)
    assert same, "the default rule's finding does not have the commit hash as its secret"


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("case", OTHER_CASES)
def test_the_check_still_finds_it(others, case, place):
    rel = others.check_rels[(case, place)]
    assert others.check.ended, f"the check did not end within its declared limit\n{others.check.describe()}"
    named = others.check.names(rel)
    assert named and others.check.returncode == 1, (f"the check lets through {case} in a {place} ({rel})\n"
                                                    f"{others.check.describe()}")


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("case", OTHER_CASES)
def test_the_filter_still_leaves_it_out(others, case, place):
    rel = others.filter_rels[(case, place)]
    assert others.filter.ended, f"the filter did not end\n{others.filter.describe()}"
    passes = others.filter.passes(rel)
    assert not passes, f"the filter lets through {case} in a {place} ({rel})\n{others.filter.describe()}"


# ---- scene 2: the project rewrites row W2-L423's rule to match 39, 41 and 12 hex digits -------------------------

LENGTHS = (39, 41, 12)


def rewritten_cases(repo):
    head = repo.head
    return {
        "39-digits-a-prefix-of-the-commit-hash":
            (support.vendor_line(V, head[:39]), ([support.RULE_ID], [support.RULE_ID])),
        "41-digits-the-commit-hash-and-one-more":
            (support.vendor_line(V, head + "0"), ([support.RULE_ID], [support.RULE_ID])),
        "41-digits-one-more-and-the-commit-hash":
            (support.vendor_line(P, "0" + head), ([support.RULE_ID], [support.RULE_ID])),
        "12-digit-shortened-hash":
            (support.vendor_line(V, head[:12]), ([support.RULE_ID], [support.RULE_ID])),
    }


REWRITTEN_CASES = list(rewritten_cases(_NAMES_ONLY))


@pytest.fixture(scope="module")
def rewritten(module_sandbox):
    return Scene(module_sandbox, "rewritten", support.rewritten_vendor_rule(LENGTHS),
                 lambda scene: rewritten_cases(scene.repo))


@pytest.mark.parametrize("case", REWRITTEN_CASES)
def test_premise_row_w2_l423s_rule_as_gitleaks_ships_it_never_matches_the_text(rewritten, case):
    text, _ = rewritten.cases[case]
    toml = support.gitleaks_toml()
    found = support.gitleaks_finds(text, toml) + support.gitleaks_finds(text, support.project_rules_alone(toml))
    none = found == []
    assert none, support.say(f"{case}: the shipped rules find {found}; the README says no rule matches it")


@pytest.mark.parametrize("case", REWRITTEN_CASES)
def test_premise_the_rewritten_rule_finds_the_text(rewritten, case):
    _premise(rewritten, case)


def test_premise_git_resolves_the_39_and_the_12_digit_prefixes_to_the_commit(rewritten):
    head, root = rewritten.repo.head, rewritten.repo.root
    resolves = [support.is_object(root, head[:39], "commit"), support.is_object(root, head[:12], "commit")]
    assert all(resolves), f"git does not resolve the prefixes to the commit: {resolves}"


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("case", REWRITTEN_CASES)
def test_the_check_does_not_widen_the_exemption_to_it(rewritten, case, place):
    rel = rewritten.check_rels[(case, place)]
    assert rewritten.check.ended, f"the check did not end within its declared limit\n{rewritten.check.describe()}"
    named = rewritten.check.names(rel)
    assert named and rewritten.check.returncode == 1, (f"the check lets through {case} in a {place} ({rel})\n"
                                                       f"{rewritten.check.describe()}")


@pytest.mark.parametrize("place", PLACES)
@pytest.mark.parametrize("case", REWRITTEN_CASES)
def test_the_filter_does_not_widen_the_exemption_to_it(rewritten, case, place):
    rel = rewritten.filter_rels[(case, place)]
    assert rewritten.filter.ended, f"the filter did not end\n{rewritten.filter.describe()}"
    passes = rewritten.filter.passes(rel)
    assert not passes, f"the filter lets through {case} in a {place} ({rel})\n{rewritten.filter.describe()}"
