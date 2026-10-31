"""W2-107: a clean verdict is remembered by the bytes judged, their kind and the engine, and answered without gitleaks.

KPI success 1 (a second rebuild of an unchanged tree scans nothing again; the key is the content's sha256, the kind and
the engine's fingerprint; one cache shared by every tree); failure 6's testable part. The scan calls are counted by
the stand-in gitleaks first on PATH; ``per_text`` is what one clean text costs with no cache.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import w2_107_support as support
from gov import secrets

pytestmark = support.needs_tools

CLEAN = {
    "docs/alpha.md": "W2-107: the alpha page, ordinary text.\n",
    "docs/plans/beta.md": "W2-107: the beta plan, ordinary text.\n",
    "notes/gamma.txt": "W2-107: the gamma note, ordinary text.\n",
}


def test_files_judged_clean_once_are_not_scanned_again(project, engine, cache, per_text):
    rels = support.put(project, CLEAN)
    kept, calls = support.counted(engine, lambda: secrets.indexable(project, rels))
    assert kept == rels and calls == len(rels) * per_text, "the first call scans every file"
    kept, calls = support.counted(engine, lambda: secrets.indexable(project, rels))
    assert kept == rels, "the second call gives the same verdicts, in the same order"
    assert calls == 0, "the second call with the same bytes, engine and rules starts gitleaks for nothing"


def test_path_names_judged_clean_once_are_not_scanned_again(project, engine, cache, per_text):
    names = ["docs/alpha-name.md", "docs/plans/beta-name.md"]
    verdicts, calls = support.counted(engine, lambda: [secrets.path_holds_secret(project, name) for name in names])
    assert verdicts == [False, False] and calls == len(names) * per_text, "the first call scans every name"
    verdicts, calls = support.counted(engine, lambda: [secrets.path_holds_secret(project, name) for name in names])
    assert verdicts == [False, False]
    assert calls == 0, "names judged clean before are answered without gitleaks"


def test_a_changed_file_is_scanned_and_its_old_bytes_stay_remembered(project, engine, cache, per_text):
    rels = support.put(project, CLEAN)
    secrets.indexable(project, rels)
    old = (project / rels[1]).read_bytes()
    support.write(project / rels[1], "W2-107: the beta plan, changed.\n")
    kept, calls = support.counted(engine, lambda: secrets.indexable(project, rels))
    assert kept == rels and calls == per_text, "only the changed file's new bytes are scanned"
    support.write(project / rels[1], old)
    kept, calls = support.counted(engine, lambda: secrets.indexable(project, rels))
    assert kept == rels and calls == 0, "the verdict is kept by the bytes, not the path: the old bytes are remembered"


def test_the_verdicts_and_their_order_are_those_of_a_scan_without_a_cache(project, engine, cache, tmp_path):
    """A guard: the verdicts, order and dropping are unchanged by the cache, on its first use and on its second."""
    rels = support.put(project, CLEAN)
    secret = support.put(project, {"docs/planted.md": f"The value is {support.planted()} today.\n"})[0]
    product = support.put(project, {"exports/rows.csv": "id\n1\n"})[0]
    support.write(tmp_path / "outside.md", CLEAN["docs/alpha.md"])
    (project / "docs/outside.md").symlink_to(tmp_path / "outside.md")
    asked = [rels[2], secret, rels[0], "docs/missing.md", product, rels[0], "docs/outside.md", "/etc/hostname", rels[1]]
    names = ["docs/alpha.md", f"docs/{support.planted()}/page.md", f"notes/{support.planted()}.txt", "notes/x.txt"]
    with support.cache_off():
        expected = secrets.indexable(project, asked)
        expected_names = [secrets.path_holds_secret(project, name) for name in names]
    assert expected == [rels[2], rels[0], rels[1]] and expected_names == [False, True, True, False]
    for _ in range(2):
        assert secrets.indexable(project, asked) == expected
        assert [secrets.path_holds_secret(project, name) for name in names] == expected_names


def test_two_projects_with_the_same_rules_share_what_was_remembered(tmp_path, project, engine, cache, per_text):
    other = support.make_project(tmp_path / "other-project")
    rels = support.put(project, CLEAN)
    moved = support.put(other, {f"elsewhere/{Path(rel).name}": text for rel, text in CLEAN.items()})
    secrets.indexable(project, rels)
    secrets.path_holds_secret(project, "docs/shared-name.md")
    kept, calls = support.counted(engine, lambda: secrets.indexable(other, moved))
    assert kept == moved and calls == 0, "the same bytes under the same rules in another tree are answered from the cache"
    verdict, calls = support.counted(engine, lambda: secrets.path_holds_secret(other, "docs/shared-name.md"))
    assert verdict is False and calls == 0, "so is the same name in another tree"


def test_a_content_verdict_and_a_path_verdict_are_kept_apart(project, engine, cache, per_text):
    """The kind is part of the key: a file whose bytes are exactly what a path's names are judged as (the path and each
    of its names, a line each) does not answer for that path, and a path judged does not answer for such a file."""
    def names_text(name):
        return os.fsencode("\n".join([name, *Path(name).parts]))

    # the content first, then the path
    name, rel = "docs/kind-probe/one.md", "docs/kind-file-one.md"
    support.put(project, {rel: names_text(name)})
    secrets.indexable(project, [rel])
    assert support.counted(engine, lambda: secrets.indexable(project, [rel]))[1] == 0, "premise: the content is remembered"
    verdict, calls = support.counted(engine, lambda: secrets.path_holds_secret(project, name))
    assert verdict is False and calls == per_text, "a content verdict does not answer for a path"

    # the path first, then the content
    name, rel = "docs/kind-probe/two.md", "docs/kind-file-two.md"
    support.put(project, {rel: names_text(name)})
    secrets.path_holds_secret(project, name)
    assert support.counted(engine, lambda: secrets.path_holds_secret(project, name))[1] == 0, "premise: the name is remembered"
    kept, calls = support.counted(engine, lambda: secrets.indexable(project, [rel]))
    assert kept == [rel] and calls == per_text, "a path verdict does not answer for a content"


def test_only_the_content_verdict_is_remembered_namespace_reach_and_reading_are_decided_each_time(
        tmp_path, project, engine, cache, per_text):
    """A guard on what is not remembered: the same clean bytes in a product namespace, behind a link out of the root,
    in a file that cannot be read, or in a file gone, are dropped although the bytes were remembered clean."""
    text = CLEAN["docs/alpha.md"]
    kept = support.put(project, {"docs/alpha.md": text, "docs/unreadable.md": text, "docs/gone.md": text})
    assert secrets.indexable(project, kept) == kept
    product = support.put(project, {"exports/alpha.md": text})[0]
    support.write(tmp_path / "outside.md", text)
    (project / "docs/link-out.md").symlink_to(tmp_path / "outside.md")
    (project / "docs/gone.md").unlink()
    unreadable = project / "docs/unreadable.md"
    unreadable.chmod(0)
    try:
        if os.access(unreadable, os.R_OK):
            pytest.skip("this user reads a file of mode 000 (root): the unreadable case cannot be built")
        result, calls = support.counted(engine, lambda: secrets.indexable(
            project, [product, "docs/alpha.md", "docs/link-out.md", "docs/unreadable.md", "docs/gone.md"]))
    finally:
        unreadable.chmod(0o644)
    assert result == ["docs/alpha.md"], "only the governance file that can be read inside the root is let through"
    assert calls == 0, "and its bytes were answered from the cache"
