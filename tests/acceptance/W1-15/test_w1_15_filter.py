"""KPI success 2 and failure 1: the content filter an indexer calls before chunking [CAP-03.a, CAP-03.e].

No indexer exists yet (W1-16, W1-17 and W1-19 build them). What this ticket
delivers, and what these tests hold it to, is the filter those indexers call:
``gov.secrets.indexable(root, paths)`` returns the paths an indexer may read.
A file with a secret in its content is never among them. The suites of the
indexer tickets assert that their indexer reads nothing else.
"""

from __future__ import annotations

import pytest

import w1_15_support as support

CLEAN = "notes/clean.md"


def _with_clean(project):
    return project.write(CLEAN, support.CLEAN_PROSE)


def test_a_file_without_a_secret_is_indexable(project, sandbox):
    """Text that speaks of canaries, tokens and secrets, and holds none, stays in the corpus."""
    _with_clean(project)
    run = support.allowed(project.root, [CLEAN], sandbox)
    assert list(run.allowed) == [CLEAN], run.describe()


@pytest.mark.parametrize("form", list(support.FORMS))
def test_a_file_with_the_canary_is_not_indexable(project, sandbox, form):
    _with_clean(project)
    planted = project.write("notes/planted.md", support.in_prose(support.FORMS[form]))
    run = support.allowed(project.root, [CLEAN, planted], sandbox)
    assert planted not in run.allowed, f"the canary ({form}) is let through to the indexer\n{run.describe()}"
    assert CLEAN in run.allowed, f"the clean neighbour was dropped too\n{run.describe()}"


@pytest.mark.parametrize("kind", list(support.DEFAULT_SECRETS))
def test_a_file_with_a_secret_the_defaults_find_is_not_indexable(project, sandbox, kind):
    _with_clean(project)
    planted = project.write("notes/planted.md", f"# Notes\n\n{support.DEFAULT_SECRETS[kind]}\n")
    run = support.allowed(project.root, [CLEAN, planted], sandbox)
    assert planted not in run.allowed, f"a {kind} is let through to the indexer\n{run.describe()}"
    assert CLEAN in run.allowed, run.describe()


@pytest.mark.parametrize("rel", [
    "app/config.ts",
    "app/settings.py",
    "app/data/values.json",
    "notes/README",
    "notes/deep/er/and/deeper/page.md",
])
def test_the_secret_is_found_by_content_whatever_the_file_is(project, sandbox, rel):
    """Content-based: an ordinary name and a code file are no shelter (the code route, CAP-03.e)."""
    _with_clean(project)
    planted = project.write(rel, f"// configuration\nconst value = \"{support.TIER_FORM}\";\n")
    run = support.allowed(project.root, [planted, CLEAN], sandbox)
    assert planted not in run.allowed, f"{rel} holds the canary and is let through\n{run.describe()}"
    assert CLEAN in run.allowed, run.describe()


def test_a_secret_far_into_a_long_file_is_found(project, sandbox):
    lines = [f"line {number}: nothing of interest here" for number in range(6000)]
    lines[5321] = f"line 5321: {support.TIER_FORM}"
    planted = project.write("notes/long.md", "\n".join(lines) + "\n")
    run = support.allowed(project.root, [planted], sandbox)
    assert list(run.allowed) == [], f"a secret on line 5322 of a long file is let through\n{run.describe()}"


def test_only_the_files_with_a_secret_are_dropped_and_the_order_is_kept(project, sandbox):
    """The filter drops whole files, one by one: the rest of the corpus is untouched."""
    clean = [project.write(f"notes/page-{number}.md", f"# Page {number}\n\nOrdinary text.\n") for number in range(6)]
    first = project.write("notes/planted-a.md", support.in_prose(support.KPI_FORM))
    second = project.write("app/planted-b.py", f"KEY = '''{support.PRIVATE_KEY}'''\n")
    asked = clean[:2] + [first] + clean[2:4] + [second] + clean[4:]
    run = support.allowed(project.root, asked, sandbox)
    assert list(run.allowed) == clean, f"expected exactly the clean files, in the order asked\n{run.describe()}"


def test_a_link_to_a_file_with_a_secret_is_not_indexable(project, sandbox, tmp_path):
    """An indexer that reads the link reads the secret: the link is no way round the filter."""
    outside = tmp_path / "outside" / "planted.txt"
    outside.parent.mkdir()
    outside.write_text(support.in_prose(support.TIER_FORM), encoding="utf-8")
    _with_clean(project)
    linked = project.link("notes/linked.md", outside)
    run = support.allowed(project.root, [linked, CLEAN], sandbox)
    assert linked not in run.allowed, f"a link to a file with the canary is let through\n{run.describe()}"


def test_a_path_that_is_no_file_is_not_indexable(project, sandbox):
    """Default deny: what the filter cannot read, it does not let through."""
    _with_clean(project)
    (project.root / "notes" / "folder").mkdir()
    run = support.run_filter(project.root, ["notes/absent.md", "notes/folder", CLEAN], sandbox)
    if run.allowed is None:
        return  # the call refused the whole request: nothing was let through
    assert "notes/absent.md" not in run.allowed and "notes/folder" not in run.allowed, run.describe()


def test_without_a_scanner_nothing_with_a_secret_is_let_through(project, sandbox):
    """Default deny (CAP-03.a): when the filter cannot scan, it fails or drops the file; it never passes it."""
    _with_clean(project)
    planted = project.write("notes/planted.md", support.in_prose(support.TIER_FORM))
    second = project.write("notes/planted-key.md", support.PRIVATE_KEY + "\n")
    run = support.run_filter(project.root, [CLEAN, planted, second], sandbox, path=sandbox.empty_bin)
    if run.allowed is None:
        return  # the call failed: nothing was let through
    assert planted not in run.allowed and second not in run.allowed, \
        f"with no gitleaks on PATH the filter lets a secret through\n{run.describe()}"


def test_the_filter_leaves_no_copy_of_a_secret_behind(project, sandbox):
    """A scan report left in the project, the home or the temporary directory would itself hold the secret."""
    _with_clean(project)
    planted = [project.write("notes/planted.md", support.in_prose(support.TIER_FORM)),
               project.write("app/planted.py", f"KEY = '''{support.PRIVATE_KEY}'''\n")]
    needles = [support.TIER_FORM, support.PRIVATE_KEY.splitlines()[1]]
    before = support.listing(project.root)
    run = support.allowed(project.root, [CLEAN, *planted], sandbox)
    created = sorted(path for path in support.listing(project.root) - before
                     if not path.startswith(support.RUNTIME_REL + "/"))
    assert not created, f"the filter wrote into the project, outside .gov-runtime/: {created}\n{run.describe()}"
    holding = support.files_holding(project.root, needles)
    assert sorted(holding) == sorted(planted), \
        f"the secret now stands in other files of the project: {sorted(holding)}\n{run.describe()}"
    for place in (sandbox.home, sandbox.tmpdir, sandbox.elsewhere):
        left = support.files_holding(place, needles)
        assert not left, f"the filter left the secret in {place}: {sorted(left)}\n{run.describe()}"
    assert support.TIER_FORM not in run.stdout + run.stderr, \
        f"the filter printed the secret\n{run.describe()}"


# --------------------------------------------------------------------------
# The dev tiers: 0 of 7 dev canaries reach any store
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_the_dev_tiers_hold_the_seven_canaries(tmp_path):
    """The premise of the next test. Passes before W1-15: it reads the tiers, not the filter."""
    count = 0
    for tier, canaries in support.DEV_PLANTED.items():
        clone = support.clone_tier(tier, tmp_path / tier)
        if clone is None:
            pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
        found = {hit for hits in support.files_holding(clone, canaries).values() for hit in hits}
        missing = [canary for canary in canaries if canary not in found]
        assert not missing, f"the {tier} tier no longer holds {len(missing)} of its planted values"
        count += len(canaries)
    assert count == 7


@pytest.mark.local_only
@pytest.mark.parametrize("tier", list(support.DEV_PLANTED))
def test_no_dev_canary_is_in_a_file_an_indexer_may_read(module, sandbox, tmp_path, tier):
    """A clone of the tier, adopted with a path map that classes all of it as governance memory."""
    clone = support.clone_tier(tier, tmp_path / "tier")
    if clone is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
    tracked = [rel for rel in support.git(clone, "ls-files", "-z").split("\0") if rel]
    adopted = support.Project(clone, namespaces={"everything": (["**"], "governance")})
    canaries = support.DEV_PLANTED[tier]
    holding = support.files_holding(clone, canaries)
    assert holding, f"the {tier} tier holds none of its planted values"
    run = support.allowed(adopted.root, tracked, sandbox)
    leaked = sorted(rel for rel in run.allowed if rel in holding)
    assert not leaked, f"{len(leaked)} file(s) holding a dev canary are let through: {leaked}"
    assert "README.md" in run.allowed, "the filter dropped the tier's README.md"
    assert len(run.allowed) > len(tracked) // 2, \
        f"the filter let through {len(run.allowed)} of {len(tracked)} tracked files: the corpus is gone"
