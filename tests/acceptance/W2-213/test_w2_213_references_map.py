"""SL-11 and SL-12: the references of every item the plan moves, and the namespaces the standard and plan imply."""

from __future__ import annotations

import pytest

import w2_213_support as support

HANDBOOK = ("notes/handbook.md", "docs/handbook.md")
CHECKOUT = ("design/checkout-spec.md", "docs/specs/checkout-spec.md")
ROADMAP = ("plans/roadmap-2024.md", "archive/superseded/plans/roadmap-2024.md")

# (the file holding the mention, the path mentioned, where it goes)
REWRITES = {
    ("docs/guide/setup.md", *HANDBOOK),                                     # a Markdown link
    ("docs/guide/setup.md", *CHECKOUT),                                     # a front-matter path
    ("docs/guide/setup.md", *ROADMAP),                                      # a path in a document's text
    ("notes/handbook.md", "docs/guide/setup.md", "docs/guide/setup.md"),    # a moving document's relative link
}
KEPT = {
    (support.MAP_REL, *ROADMAP),                                            # the path map
    ("docs/close/PLT-1.md", *HANDBOOK),                                     # a tool-written record
    ("governance/kernel/skills/retrieval.md", *CHECKOUT),                   # the kit
    ("vendor/jsonlib/README.md", *HANDBOOK),                                # an import's own file
    ("views/index.generated.md", *CHECKOUT),                                # a generated file
}
# (the held item, the code or configuration file naming it)
HELD = {
    ("experiments/cache-study.md", "src/meadow/core.py"),                   # code
    ("reports/audit-2025-03-02.md", "src/meadow/core.py"),                  # also named by a link and front matter
    ("reports/audit-2025-03-02.md", ".github/workflows/ci.yml"),            # configuration
    ("fixtures/sample-orders.csv", "tests/test_core.py"),                   # a test
    ("seedpack", ".github/workflows/ci.yml"),                               # a file of a moving folder
}


def _triples(result, key):
    entries = result[key]
    assert all(isinstance(e, dict) and e.get("path") and e.get("target") and "new" in e for e in entries), (
        f"`{key}` entries are not path/target/new: {entries}")
    return {(e["path"], e["target"], e["new"]) for e in entries if e["target"] not in support.HELD_ITEMS}


def test_sl11_the_references_leave_the_clean_plan_clean(clean_run):
    result = support.assert_clean(clean_run[0])
    assert result["rewrites"] and result["held"] and result["kept"], "no reference is reported"


def test_sl11_document_mentions_links_front_matter_and_relative_links_are_rewrites(clean_run):
    result = support.assert_clean(clean_run[0])
    got = _triples(result, "rewrites")
    assert got == REWRITES, f"missing {sorted(REWRITES - got)}\nextra {sorted(got - REWRITES)}"


def test_sl11_code_tests_and_configuration_mentions_hold_their_item(clean_run):
    result = support.assert_clean(clean_run[0])
    got = {(e.get("path"), e.get("by")) for e in result["held"]}
    assert got == HELD, f"missing {sorted(HELD - got)}\nextra {sorted(got - HELD, key=str)}"


def test_sl11_a_held_item_is_not_shown_as_moving(clean_run):
    result = support.assert_clean(clean_run[0])
    moving = [e for e in result["rewrites"]
              if e.get("target") in support.HELD_ITEMS or e.get("path") in support.HELD_ITEMS
              or str(e.get("target")).startswith("seedpack/")]
    assert not moving, f"rewrites that show a held item moving: {moving}"


def test_sl11_path_map_kit_import_generated_and_record_mentions_are_kept(clean_run):
    result = support.assert_clean(clean_run[0])
    got = _triples(result, "kept")
    assert got == KEPT, f"missing {sorted(KEPT - got)}\nextra {sorted(got - KEPT)}"


def test_sl11_the_text_form_prints_each_rewrite_hold_and_kept_mention(clean_repo, work):
    plan, _ = support.write_plan(work / "plan.jsonl", support.clean_lines())
    run = support.run_check(work, clean_repo, plan, json_form=False)
    assert run.returncode == 0, run.describe()
    rows = run.stdout.splitlines()
    for code, entries in (("REWRITE", REWRITES), ("KEPT", KEPT),
                          ("HELD", {(item, by) for item, by in HELD})):
        for entry in sorted(entries):
            found = [row for row in rows if row.startswith(f"gov layout check: {code} line -: ")
                     and all(name in row for name in entry[:2])]
            assert found, f"no {code} line naming {entry[:2]}\n{run.describe()}"


def test_sl11_a_mention_of_an_item_that_does_not_move_is_no_reference(own_repo, work):
    support.add_commit(own_repo, {"docs/guide/more.md": "# More\n\nSee data/prices.csv and [ops](ops.md).\n"})
    lines = support.clean_lines() + [support.line("docs/guide/more.md", "docs")]
    run, _ = support.check_lines(work, own_repo, lines)
    result = support.assert_clean(run)
    named = [e for key in ("rewrites", "kept", "held") for e in result[key]
             if "docs/guide/more.md" in (e.get("path"), e.get("by"))]
    assert not named, f"mentions of items that stay are reported: {named}"


# --- SL-12: the map compiles -----------------------------------------------------------------------------------------

def _namespaces(result):
    spaces = result["namespaces"]
    for space in spaces:
        assert {"name", "paths", "lexical_policy", "embedding_policy", "stale_class"} <= set(space), (
            f"a namespace lacks a key: {space}")
    names = [space["name"] for space in spaces]
    assert len(names) == len(set(names)), f"two namespaces share a name: {names}"
    return {space["name"]: space for space in spaces}


def _holding(spaces, path):
    return [name for name, space in spaces.items() if any(support.matches(path, p) for p in space["paths"])]


def _destinations(repo):
    """``{destination file: plan line}`` for every tracked and untracked file of the clean plan (ask apart)."""
    items = support.items_of(repo)
    found = {}
    for item_line in support.clean_lines():
        if item_line["kind"] in ("declared", "ignored-root") or item_line["class"] == "ask":
            continue
        for item in support.covered(item_line, items):
            found[item_line["destination"] + item[len(item_line["path"]):]] = item_line
    return found


def test_sl12_every_destination_lies_in_exactly_one_namespace_with_its_class_policies(clean_repo, clean_run):
    spaces = _namespaces(support.assert_clean(clean_run[0]))
    wrong = []
    for path, item_line in sorted(_destinations(clean_repo).items()):
        holding = _holding(spaces, path)
        if item_line["kind"] == "submodule" and not holding:
            holding = _holding(spaces, path + "/any")  # a namespace may name a submodule as its folder
        if len(holding) != 1:
            wrong.append((path, f"in {holding}"))
            continue
        space = spaces[holding[0]]
        cls = item_line["class"]
        if cls == "import-study":
            continue
        name = (f"archive-{item_line['stale_class']}" if cls == "archive"
                else f"import-{item_line['import']}" if cls in support.IMPORT_CLASSES else cls)
        policy = support.POLICIES[support.MEMORY[cls]]
        got = (space["lexical_policy"], space["embedding_policy"])
        if holding[0] != name or got != policy:
            wrong.append((path, f"in {holding[0]} {got}, expected {name} {policy}"))
    assert not wrong, f"destinations placed wrongly: {wrong}"


def test_sl12_the_three_archive_namespaces_carry_their_stale_class_and_no_other_does(clean_run):
    spaces = _namespaces(support.assert_clean(clean_run[0]))
    for stale in ("superseded", "historical", "legacy"):
        space = spaces.get(f"archive-{stale}")
        assert space, f"no namespace archive-{stale}: {sorted(spaces)}"
        assert (space["stale_class"], space["lexical_policy"], space["embedding_policy"]) == (
            stale, "not indexed", "not embedded"), f"archive-{stale}: {space}"
    stray = [n for n, s in spaces.items() if s["stale_class"] is not None and not n.startswith("archive-")]
    assert not stray, f"namespaces outside the archive with a stale class: {stray}"


def _imports(result):
    found = {entry.get("name"): entry for entry in result["imports"]}
    for entry in found.values():
        assert {"name", "class", "chunks", "namespace", "embedding_policy"} <= set(entry), f"import entry: {entry}"
    return found


def test_sl12_each_import_is_named_with_its_namespace_and_each_study_with_its_chunks(clean_run):
    result = support.assert_clean(clean_run[0])
    spaces, imports = _namespaces(result), _imports(result)
    assert {"jsonlib", "ratelimit", "notebook", "bigbook", "widgets"} <= set(imports), sorted(imports)
    assert imports["notebook"]["chunks"] == 3 and imports["bigbook"]["chunks"] == 2001, (
        f"chunk counts: {imports['notebook']}, {imports['bigbook']}")
    assert imports["notebook"]["embedding_policy"] == "embedded", imports["notebook"]
    assert imports["bigbook"]["embedding_policy"] == "not embedded", imports["bigbook"]
    assert imports["notebook"]["namespace"] != imports["bigbook"]["namespace"], "one namespace for both studies"
    for name, entry in imports.items():
        space = spaces.get(entry["namespace"])
        assert space, f"{name}: the namespace {entry['namespace']!r} is not listed"
        assert space["embedding_policy"] == entry["embedding_policy"], f"{name}: {entry} but {space}"
        assert space["lexical_policy"] == "indexed", f"{name}: {space}"
    for name, file in (("notebook", "imports/notebook/p1.md"), ("bigbook", "imports/bigbook/volume.md")):
        assert _holding(spaces, file) == [imports[name]["namespace"]], f"{file}: {_holding(spaces, file)}"


def test_sl12_the_clean_plans_destinations_overlap_nowhere(clean_run):
    result = support.assert_clean(clean_run[0])
    assert not support.findings(result, "LAYOUT_MAP")


def _study_repository(own_repo, sizes):
    """The clean repository with its two studies replaced by studies of ``sizes`` chunks; the plan."""
    support.git(own_repo, "rm", "-q", "-r", "study")
    files = {f"study/s{n}/text.md": support.sections(size, f"study{n}") for n, size in enumerate(sizes)}
    support.add_commit(own_repo, files, "planted: other studies")
    lines = support.without(support.clean_lines(), "study/notebook", "study/bigbook")
    lines += [support.line(f"study/s{n}", "import-study", f"imports/s{n}", "folder", imp=f"s{n}", sign="content")
              for n in range(len(sizes))]
    return lines


CEILINGS = {
    "an-import-at-the-ceiling": ((2000,), "all"),
    "an-import-one-over": ((2001,), "none"),
    "the-repository-at-its-ceiling": ((2000, 2000, 1000), "all"),
    "the-repository-one-over": ((2000, 2000, 1001), "some-not"),
    "three-studies-over-the-repository-ceiling": ((1800, 1800, 1800), "some-not"),
}


@pytest.mark.parametrize("case", sorted(CEILINGS))
def test_sl12_the_study_ceiling_of_an_import_and_of_the_repository(own_repo, work, case):
    sizes, expected = CEILINGS[case]
    run, _ = support.check_lines(work, own_repo, _study_repository(own_repo, sizes))
    result = support.assert_clean(run)
    imports = _imports(result)
    studies = [imports.get(f"s{n}") for n in range(len(sizes))]
    assert all(studies), f"a study import is not listed: {sorted(imports)}"
    assert [s["chunks"] for s in studies] == list(sizes), f"chunk counts: {studies}"
    embedded = [s for s in studies if s["embedding_policy"] == "embedded"]
    assert sum(s["chunks"] for s in embedded) <= 5000, f"over 5,000 study chunks under meaning search: {studies}"
    if expected == "all":
        assert len(embedded) == len(studies), f"a study within the ceiling is not under meaning search: {studies}"
    elif expected == "none":
        assert not embedded, f"a study over 2,000 chunks is under meaning search: {studies}"
    else:
        assert embedded != studies, f"nothing is moved to keyword search over the repository ceiling: {studies}"


OVERLAPS = {
    "a-docs-folder-onto-the-spec-place": ("manual/specs", "docs/specs"),
    "a-docs-folder-onto-the-record-place": ("manual/records", "docs/records"),
    "a-docs-folder-onto-the-research-place": ("manual/research", "docs/research"),
}


@pytest.mark.parametrize("case", sorted(OVERLAPS))
def test_sl12_a_folder_line_holding_another_classs_destination_is_a_finding(own_repo, work, case):
    folder, destination = OVERLAPS[case]
    support.add_commit(own_repo, {f"{folder}/howto.md": "# How to\n"})
    lines = support.clean_lines() + [support.line(folder, "docs", destination, "folder")]
    run, _ = support.check_lines(work, own_repo, lines)
    result = support.result_of(run, 1)
    found = support.findings(result, "LAYOUT_MAP")
    assert any(folder in support.text_of(f) or destination in support.text_of(f) for f in found), (
        f"no LAYOUT_MAP for {folder} -> {destination}: {result['findings'][:20]}")
