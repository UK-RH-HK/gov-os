"""SL-13: the same inputs give the same bytes and hash, a changed input another hash, and the output states what the
owner is shown."""

from __future__ import annotations

import random
import re
import shutil
from collections import Counter

import pytest

import w2_213_support as support


def _shuffled():
    lines = support.clean_lines()
    random.Random(213).shuffle(lines)
    assert lines != support.clean_lines()
    return lines


@pytest.fixture(scope="module")
def runs(clean_repo, tmp_path_factory):
    """The clean plan twice and shuffled, in both forms."""
    work = tmp_path_factory.mktemp("w2-213-determinism")
    plan, _ = support.write_plan(work / "ordered.jsonl", support.clean_lines())
    other, _ = support.write_plan(work / "shuffled.jsonl", _shuffled())
    return {(name, form): support.run_check(work, clean_repo, path, json_form=form == "json")
            for name, path in (("first", plan), ("second", plan), ("shuffled", other))
            for form in ("json", "text")}


def _counts():
    """Items per class, folder lines expanded: each file, ignored root, submodule and declared line is one."""
    files = support.tracked_files()
    items = [*files, "external/widgets", *support.UNTRACKED, *support.IGNORED_ROOTS, "../solar-sketch"]
    counts = Counter()
    for item_line in support.clean_lines():
        counts[item_line["class"]] += len(support.covered(item_line, items))
    assert sum(counts.values()) == len(items), "fixture: the clean plan does not cover each item once"
    return dict(counts)


@pytest.mark.parametrize("form", ["json", "text"])
def test_sl13_the_same_plan_twice_and_in_another_order_gives_the_same_bytes(runs, form):
    first = runs[("first", form)]
    assert first.returncode == 0, first.describe()
    for name in ("second", "shuffled"):
        other = runs[(name, form)]
        assert (other.returncode, other.stdout) == (0, first.stdout), (
            f"{name} differs\n{first.describe()}\n{other.describe()}")


def test_sl13_the_output_holds_no_absolute_path_and_the_hash_is_recorded(runs, clean_repo):
    run = runs[("first", "json")]
    result = support.assert_clean(run)
    assert re.fullmatch(r"[0-9a-f]{64}", str(result["hash"])), f"no plan hash\n{run.describe()}"
    for form in ("json", "text"):
        assert str(clean_repo) not in runs[("first", form)].stdout, "the output holds the repository's absolute path"
    assert result["hash"] in runs[("first", "text")].stdout, "the text form does not state the plan's hash"


def test_sl13_the_result_states_version_commit_counts_and_asks(runs, clean_repo):
    result = support.assert_clean(runs[("first", "json")])
    assert result["standard"] == support.load_yaml(support.STANDARD)["version"], result["standard"]
    assert result["commit"] == support.head(clean_repo), result["commit"]
    assert result["counts"] == _counts(), f"counts {result['counts']}, planted {_counts()}"
    assert result["asks"] == [{"path": "misc/oddity.txt", "question": support.QUESTION, "recommended": "docs"}], (
        result["asks"])
    assert result["stoppers"] == []


def test_sl13_the_text_states_version_commit_counts_asks_rewrites_and_held_items(runs, clean_repo):
    run = runs[("first", "text")]
    assert run.returncode == 0, run.describe()
    text = run.stdout
    version = support.load_yaml(support.STANDARD)["version"]
    assert re.search(rf"(?i)(standard|version)\D{{0,30}}\b{version}\b", text), f"no version\n{run.describe()}"
    assert support.head(clean_repo) in text, f"no commit\n{run.describe()}"
    rows = text.splitlines()
    summary = "\n".join(r for r in rows if not re.match(r"gov layout check: (REWRITE|HELD|KEPT|ASK) ", r))
    missing = {cls: n for cls, n in _counts().items()
               if not re.search(rf"(?<![\w-]){cls}(?![\w-])\W{{0,4}}{n}(?!\d)|(?<![\w.]){n}\W{{1,4}}{cls}(?![\w-])",
                                summary)}
    assert not missing, f"items per class not stated: {missing}\n{run.describe()}"
    assert any(r.startswith("gov layout check: ASK line -: misc/oddity.txt: ") and support.QUESTION in r
               for r in rows), f"the ask line and its question\n{run.describe()}"
    for rel in support.HELD_ITEMS:
        assert any(r.startswith("gov layout check: HELD ") and rel in r for r in rows), f"held {rel}\n{text}"
    assert sum(r.startswith("gov layout check: REWRITE ") for r in rows) >= 4, f"rewrites\n{run.describe()}"


def test_sl13_every_stopper_is_stated(dirty_repo, work):
    plan, _ = support.write_plan(work / "plan.jsonl", support.dirty_lines())
    first = support.run_check(work, dirty_repo, plan, json_form=False)
    assert first.returncode == 1, first.describe()
    rows = first.stdout.splitlines()
    for rel in (*support.TRACKED_STOPPERS, "eval/hidden/more.txt"):
        assert any(r.startswith("gov layout check: LAYOUT_STOPPER ") and f": {rel}: " in r for r in rows), (
            f"the stopper {rel} is not stated\n{first.describe()}")


def _hash(work, root, lines, **kwargs):
    run, _ = support.check_lines(work, root, lines, **kwargs)
    return support.assert_clean(run)["hash"]


def test_sl13_a_changed_line_changes_the_hash(clean_repo, runs, work):
    before = support.assert_clean(runs[("first", "json")])["hash"]
    lines = support.clean_lines()
    support.by_path(lines, "docs/guide/ops.md")["reason"] = "another reading of the operations page"
    assert _hash(work, clean_repo, lines) != before, "one changed reason keeps the hash"
    lines = support.clean_lines()
    support.by_path(lines, "experiments/cache-study.md")["destination"] = "docs/research/caching/cache-study.md"
    assert _hash(work, clean_repo, lines) != before, "one changed destination keeps the hash"


def test_sl13_another_commit_changes_the_hash(own_repo, work):
    before = _hash(work, own_repo, support.clean_lines())
    support.commit(own_repo, "planted: an empty commit")
    assert _hash(work, own_repo, support.clean_lines()) != before, "another commit keeps the hash"


def test_sl13_another_version_of_the_standard_changes_the_hash(clean_repo, work, tmp_path):
    version = support.load_yaml(support.STANDARD)["version"] if support.STANDARD.is_file() else None
    assert version is not None, f"the kit holds no standard file: {support.STANDARD_REL}"
    site = tmp_path / "site"
    shutil.copytree(support.SRC / "gov", site / "gov", ignore=shutil.ignore_patterns("__pycache__"))
    shipped = site / "gov/_shipped" / support.STANDARD_REL
    assert shipped.is_file(), f"the package ships no standard: {shipped}"
    same = _hash(work, clean_repo, support.clean_lines(), src=site)
    assert same == _hash(work, clean_repo, support.clean_lines()), "the same inputs give another hash"
    text = shipped.read_text(encoding="utf-8")
    shipped.write_text(text.replace(f"version: {version}", f"version: {version + 1}", 1), encoding="utf-8")
    assert _hash(work, clean_repo, support.clean_lines(), src=site) != same, "another version keeps the hash"
