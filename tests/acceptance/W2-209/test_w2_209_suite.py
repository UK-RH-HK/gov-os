"""S4 and F3: G2, the full suite on the exact release commit.

``gov release 0.1.2 --patch --suite <record>`` in the planted source (clean range, authority on): only a record with
``scope: full``, ``verdict: green``, ``optin`` naming ``weekly``, ``head`` equal to C in full and ``tree`` equal to C's
tree passes (the answer then names G3: no kept run given). Every other record is refused at G2 naming the check that
failed (README, "Interface": ``check``), and a record that cannot be read is ``unreadable``, never a pass.
README, "S4, F3".
"""

import pytest

import w2_209_support as support


@pytest.fixture(scope="module")
def planted(base, tmp_path_factory):
    folder = tmp_path_factory.mktemp("w2-209-suite")
    repo = support.make_case(base, folder / "repo", "clean")
    home = support.make_home(folder / "home", base.n_version_commit)
    return repo, home, folder / "records"


def _refused_at_g2(planted, record, check, what):
    repo, home, _ = planted
    before = support.snapshot(repo)
    args = ("--suite", str(record)) if record is not None else ()
    run = support.release(repo, home.path, support.X, *args)
    support.assert_gate(support.refusal(run), "G2", what, check=check)
    assert not support.difference(before, support.snapshot(repo)), f"{what}: a refused cut changed the repository"


def test_s4_a_record_for_c_full_green_with_the_weekly_tier_passes_g2(planted):
    repo, home, records = planted
    record = support.good_suite(repo, records)
    run = support.release(repo, home.path, support.X, "--suite", str(record))
    support.assert_gate(support.refusal(run), "G3", "a good record and no kept run")


def test_s4_no_suite_record_is_refused(planted):
    _refused_at_g2(planted, None, "missing", "no --suite")


def _stale(repo, records, name, **change):
    c = support.rev(repo)
    return support.suite_record(records, name, change.pop("head", c), change.pop("tree", support.tree_of(repo)),
                                **change)


@pytest.mark.parametrize("name, check", [
    ("parent", "head"), ("other_branch", "head"), ("no_optin", "optin"), ("lifted_only", "optin"),
    ("red", "verdict"), ("other_tree", "tree"), ("scoped", "scope")])
def test_s4_f3_a_record_not_for_the_exact_commit_or_without_the_weekly_tier_is_refused(planted, base, name, check):
    repo, home, records = planted
    other = support.rev(repo, "case/contract")
    change = {
        "parent": {"head": support.rev(repo, "HEAD~1"), "tree": support.tree_of(repo, "HEAD~1")},
        "other_branch": {"head": other, "tree": support.tree_of(repo, other)},
        "no_optin": {"optin": support.DROP},
        "lifted_only": {"optin": ["lifted"]},
        "red": {"verdict": "red"},
        "other_tree": {"tree": support.tree_of(repo, base.n_commit)},
        "scoped": {"scope": "scoped"},
    }[name]
    _refused_at_g2(planted, _stale(repo, records, f"NR-{name}.json", **change), check, name)


@pytest.mark.parametrize("name", ["not_json", "not_a_map", "short_head", "ref_name_head", "no_such_file"])
def test_f3_a_record_that_cannot_be_read_is_refused_as_unreadable(planted, name):
    repo, home, records = planted
    records.mkdir(parents=True, exist_ok=True)
    path = records / f"NR-{name}.json"
    if name == "not_json":
        path.write_text('{"head": "' + support.rev(repo) + '", "scope": full', encoding="utf-8")
    elif name == "not_a_map":
        path.write_text('["' + support.rev(repo) + '", "full", "green", ["weekly"]]\n', encoding="utf-8")
    elif name == "short_head":
        path = _stale(repo, records, path.name, head=support.rev(repo)[:12])
    elif name == "ref_name_head":  # a ref that names C is not C in full
        path = _stale(repo, records, path.name, head=support.INTEGRATION)
    # no_such_file: the path names nothing
    _refused_at_g2(planted, path, "unreadable", name)
