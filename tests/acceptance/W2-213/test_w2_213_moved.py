"""SL-14: ``gov layout check <plan> --moved`` on the hand-restructured copy."""

from __future__ import annotations

import pytest
import yaml

import w2_213_support as support


def _moved_check(work, root, plan=None):
    if plan is None:
        run, _ = support.check_lines(work, root, support.clean_lines(), "--moved")
        return run
    return support.run_check(work, root, plan, "--moved")


def test_sl14_the_correctly_moved_repository_is_clean_and_unchanged_by_the_check(moved_repo, work):
    before = support.snapshot(moved_repo)
    support.assert_clean(_moved_check(work, moved_repo))
    support.assert_unchanged(before, support.snapshot(moved_repo))


def test_sl14_the_plan_committed_at_its_usual_place_is_no_unplanned_item(moved_repo, work, tmp_path):
    root = support.copy_repository(moved_repo, tmp_path / "meadow")
    plan, _ = support.write_plan(root / support.PLAN_USUAL, support.clean_lines())
    document = support.load_yaml(root / support.MAP_REL)
    document["namespaces"]["record"]["paths"].append(support.PLAN_USUAL)
    support.add_commit(root, {support.MAP_REL: yaml.safe_dump(document, sort_keys=False),
                              support.PLAN_USUAL: plan.read_bytes()})
    support.assert_clean(_moved_check(work, root, root / support.PLAN_USUAL))


def test_sl14_before_the_moves_the_same_plan_is_not_clean_after_the_moves(clean_repo, work):
    result = support.result_of(_moved_check(work, clean_repo), 1)
    support.one_finding(result, "LAYOUT_MOVE", names=("notes/handbook.md",))


# --- the repository's files: one planted after-move fault each -------------------------------------------------------

class Tree:
    """A copy of the moved repository whose path map follows each tracked change."""

    def __init__(self, root):
        self.root = root
        self.map = support.load_yaml(root / support.MAP_REL)

    def _namespace(self, path):
        found = [n for n, s in self.map["namespaces"].items() if path in s["paths"]]
        assert len(found) == 1, f"fixture: {path} in {found}"
        return found[0]

    def place(self, path, name):
        self.map["namespaces"][name]["paths"].append(path)

    def drop(self, path):
        name = self._namespace(path)
        self.map["namespaces"][name]["paths"].remove(path)
        if not self.map["namespaces"][name]["paths"]:
            del self.map["namespaces"][name]
        return name

    def move(self, old, new):
        name = self._namespace(old)
        self.place(new, name)
        self.drop(old)
        (self.root / new).parent.mkdir(parents=True, exist_ok=True)
        support.git(self.root, "mv", old, new)

    def add(self, path, text, name):
        support.write(self.root, path, text)
        support.git(self.root, "add", "-f", path)
        self.place(path, name)

    def remove(self, path):
        self.drop(path)
        support.git(self.root, "rm", "-q", path)

    def edit(self, path, old, new):
        text = (self.root / path).read_text(encoding="utf-8")
        assert old in text, f"fixture: {path} does not hold {old!r}"
        support.write(self.root, path, text.replace(old, new))
        support.git(self.root, "add", path)

    def commit(self):
        support.write(self.root, support.MAP_REL, yaml.safe_dump(self.map, sort_keys=False))
        support.git(self.root, "add", support.MAP_REL)
        support.commit(self.root, "planted: an after-move fault")


def _rename(tree, old, new):
    (tree.root / new).parent.mkdir(parents=True, exist_ok=True)
    (tree.root / old).rename(tree.root / new)


# fault -> (the change, the paths one of which the finding names)
MOVE_FAULTS = {
    "a-moving-file-unmoved": (
        lambda t: t.move("archive/superseded/plans/roadmap-2024.md", "plans/roadmap-2024.md"),
        ("plans/roadmap-2024.md",)),
    "a-moving-folder-unmoved": (
        lambda t: [t.move(f"archive/legacy/legacy-queue/{n}", f"legacy-queue/{n}")
                   for n in ("worker.py", "README.md")],
        ("legacy-queue",)),
    "the-old-path-still-there": (
        lambda t: t.add("notes/handbook.md", "# Handbook\n", "docs"), ("notes/handbook.md",)),
    "a-held-file-moved": (
        lambda t: t.move("experiments/cache-study.md", "docs/research/cache-study/cache-study.md"),
        ("experiments/cache-study.md",)),
    "a-held-folder-moved": (
        lambda t: [t.move(f"seedpack/{n}", f"data/seedpack/{n}") for n in ("regions.csv", "units.csv")],
        ("seedpack",)),
    "a-tool-fixed-file-moved": (lambda t: t.move("CLAUDE.md", "docs/CLAUDE.md"), ("CLAUDE.md",)),
    "a-test-moved": (lambda t: t.move("tests/test_core.py", "tests/unit/test_core.py"), ("tests/test_core.py",)),
    "an-ask-item-moved": (lambda t: t.move("misc/oddity.txt", "docs/oddity.txt"), ("misc/oddity.txt",)),
    "a-never-moving-file-gone": (lambda t: t.remove("web/GUIDE.md"), ("web/GUIDE.md",)),
    "a-link-not-rewritten": (
        lambda t: t.edit("docs/guide/setup.md", "(../handbook.md)", "(../../notes/handbook.md)"),
        ("notes/handbook.md",)),
    "a-front-matter-path-not-rewritten": (
        lambda t: t.edit("docs/guide/setup.md", "related: docs/specs/checkout-spec.md",
                         "related: design/checkout-spec.md"),
        ("design/checkout-spec.md",)),
    "a-text-mention-not-rewritten": (
        lambda t: t.edit("docs/guide/setup.md", "archive/superseded/plans/roadmap-2024.md",
                         "plans/roadmap-2024.md"),
        ("plans/roadmap-2024.md",)),
    "an-unplanned-tracked-file": (lambda t: t.add("docs/extra.md", "# Extra\n", "docs"), ("docs/extra.md",)),
    "an-unplanned-untracked-file": (lambda t: support.write(t.root, "docs/stray.md", "# Stray\n"),
                                    ("docs/stray.md",)),
    "an-untracked-item-unmoved": (lambda t: _rename(t, "docs/todo.md", "todo.md"), ("todo.md",)),
}


@pytest.mark.parametrize("fault", sorted(MOVE_FAULTS))
def test_sl14_a_planted_move_fault_is_a_move_finding_naming_the_path(moved_repo, work, tmp_path, fault):
    change, paths = MOVE_FAULTS[fault]
    tree = Tree(support.copy_repository(moved_repo, tmp_path / "meadow"))
    change(tree)
    tree.commit()
    result = support.result_of(_moved_check(work, tree.root), 1)
    found = support.findings(result, "LAYOUT_MOVE")
    assert any(path in support.text_of(f) for f in found for path in paths), (
        f"no LAYOUT_MOVE naming {paths}: {result['findings'][:30]}")


# --- the repository's own path map: one planted fault each -----------------------------------------------------------

def _policy(name, **values):
    def change(spaces):
        for key, value in values.items():
            if value is None:
                spaces[name].pop(key, None)
            else:
                spaces[name][key] = value
        return list(spaces[name]["paths"])
    return change


def _no_namespace(spaces):
    spaces["docs"]["paths"].remove("docs/guide/ops.md")
    return ["docs/guide/ops.md"]


def _two_namespaces(spaces):
    spaces["record"]["paths"].append("docs/guide/ops.md")
    return ["docs/guide/ops.md"]


def _in_another_class(spaces):
    spaces["docs"]["paths"].remove("docs/guide/ops.md")
    spaces["record"]["paths"].append("docs/guide/ops.md")
    return ["docs/guide/ops.md"]


MAP_FAULTS = {
    "an-archive-namespace-indexed-and-embedded": _policy(
        "archive-superseded", lexical_policy="indexed", embedding_policy="embedded"),
    "an-archive-namespace-keyword-indexed": _policy("archive-legacy", lexical_policy=None),
    "an-archive-namespace-without-its-stale-class": _policy("archive-historical", stale_class=None),
    "an-archive-namespace-with-another-stale-class": _policy("archive-historical", stale_class="legacy"),
    "a-stale-class-outside-the-archive": _policy("docs", stale_class="legacy"),
    "docs-not-embedded": _policy("docs", embedding_policy="not embedded"),
    "records-embedded": _policy("record", embedding_policy="embedded"),
    "data-indexed": _policy("data", lexical_policy=None),
    "an-evaluation-set-indexed": _policy("evaluation", lexical_policy=None),
    "a-study-over-the-ceiling-embedded": _policy("import-bigbook", embedding_policy="embedded"),
    "an-import-in-use-embedded": _policy("import-jsonlib", embedding_policy="embedded"),
    "a-tracked-path-in-no-namespace": _no_namespace,
    "a-tracked-path-in-two-namespaces": _two_namespaces,
    "a-tracked-path-in-another-classs-namespace": _in_another_class,
}


@pytest.mark.parametrize("fault", sorted(MAP_FAULTS))
def test_sl14_a_planted_path_map_fault_is_a_map_finding_naming_the_path(moved_repo, work, tmp_path, fault):
    root = support.copy_repository(moved_repo, tmp_path / "meadow")
    document = support.load_yaml(root / support.MAP_REL)
    paths = MAP_FAULTS[fault](document["namespaces"])
    support.add_commit(root, {support.MAP_REL: yaml.safe_dump(document, sort_keys=False)})
    result = support.result_of(_moved_check(work, root), 1)
    found = support.findings(result, "LAYOUT_MAP")
    assert any(path in support.text_of(f) for f in found for path in paths), (
        f"no LAYOUT_MAP naming one of {paths[:5]}: {result['findings'][:30]}")
    allowed = set(paths)
    others = [f for f in found if f.get("path") not in allowed and not any(p in support.text_of(f) for p in allowed)]
    assert not others, f"paths the map places rightly are reported: {others[:10]}"
