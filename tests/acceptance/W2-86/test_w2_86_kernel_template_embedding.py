"""W2-86 (DAEO-jsg1): the kernel template is embedded as the path map means it (DEC-952, DEC-388, DEC-381, DEC-694).

The repository is the one this file sits in; its path map and tracked files are read, nothing in it is written.
The semantic route's own selection is asked which chunks it embeds, over a chunk table planted in a temporary folder.
"""

from __future__ import annotations

import sqlite3
import subprocess
from pathlib import Path

import gov
from gov.config.loader import PROJECT_DIR, load_config
from gov.retrieval import lexical, semantic
from gov.secrets import _matches

ROOT = Path(__file__).resolve().parents[3]
BASE = "9dc5288161c4"  # the ticket's base: the path map before the change
PATH_MAP = f"{PROJECT_DIR}/path-map.yaml"
VALUES = {"embedded", "not embedded"}  # DEC-388 DP-8, DEC-694


def _tracked(inside: bool) -> list[str]:
    paths = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return [rel for rel in paths.split("\0") if rel and rel.startswith("template/") == inside]


def _namespaces(root: Path) -> dict:
    return load_config(root)["path-map.yaml"]["namespaces"]


def _selected(root: Path, paths: list[str], folder: Path) -> set[str]:
    """The paths whose chunk the route's selection embeds under ``root``'s path map, one chunk per path."""
    assert Path(gov.__file__).resolve().is_relative_to(ROOT / "src"), f"gov is not this repository's: {gov.__file__}"
    connection = sqlite3.connect(folder / "chunks.db")
    connection.executescript(lexical.SCHEMA)
    connection.executemany("INSERT INTO lexical_chunk (chunk_id, path, start_line, end_line, parent_id) "
                           "VALUES (?, ?, 1, 1, ?)", [(f"c{i}", rel, f"p{i}") for i, rel in enumerate(paths)])
    by_id = {f"c{i}": rel for i, rel in enumerate(paths)}
    chosen = {by_id[chunk_id] for chunk_id in semantic._wanted(root, connection)}
    connection.close()
    return chosen


def _vendored(rel: str) -> bool:
    superpowers = "template/governance/kernel/skills/superpowers/"
    return (rel.startswith(("template/governance/kernel/vendor/", "template/governance/kernel/bin/"))
            or (rel.startswith(superpowers) and "/" in rel[len(superpowers):]))


def test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated(tmp_path):
    tracked = _tracked(inside=True)
    namespaces = _namespaces(ROOT)
    homes = {rel: [name for name, entry in namespaces.items() if any(_matches(rel, p) for p in entry["paths"])]
             for rel in tracked}
    assert {rel: names for rel, names in homes.items() if len(names) != 1} == {}

    vendored = {rel for rel in tracked if _vendored(rel)}
    generated = {rel for rel in tracked if rel.startswith("template/.rulesync/")}
    kernel = "template/governance/kernel/"
    roles = {rel for rel in tracked if _matches(rel, kernel + "roles/*.md")}
    hooks = {rel for rel in tracked if _matches(rel, kernel + "hooks/*.py")}
    skills = {rel for rel in tracked if _matches(rel, kernel + "skills/*/SKILL.md")}
    sets = {part: {rel for rel in vendored if f"/{part}/" in rel} for part in ("vendor", "bin", "superpowers")}
    sets.update({".rulesync": generated, "roles": roles, "hooks": hooks, "skills": skills})
    assert [name for name, found in sets.items() if not found] == [], "an empty set: the case would pass vacuously"

    chosen = _selected(ROOT, tracked, tmp_path)
    assert sorted(chosen & (vendored | generated)) == [], "vendored code or a generated copy is embedded"
    missing = sorted(set(tracked) - vendored - generated - chosen)
    assert missing == [], f"{len(missing)} kernel-template files not embedded, e.g. {missing[:5]}"
    assert kernel + "skills/superpowers/vendored.yaml" in chosen


def test_every_namespace_states_one_of_the_two_values():
    assert semantic.EMBEDDED == "embedded"  # the indexer still embeds on the one exact value
    stated = {name: entry.get("embedding_policy") for name, entry in _namespaces(ROOT).items()}
    assert {name: value for name, value in stated.items() if value not in VALUES} == {}


def _newly_embedded_by_dec_957(rel: str) -> bool:
    """DEC-957's three sets, embedded later on purpose (W2-91, DEC-1013 TD-2 (a)): the tracked root files, every
    tracked file under ``governance/**`` and every tracked file under ``schemas/**``. The same definition as W2-91's
    acceptance tests (``tests/acceptance/W2-91/w2_91_support.py``, ``newly_embedded_area``)."""
    return "/" not in rel or rel.startswith(("governance/", "schemas/"))


# D-7's decided cut (DEC-1052 M-4, DEC-1055 (3), DEC-1066 (3)): these files leave the vectors on purpose, and only
# towards not embedded. Written here as the decisions word them, not read from the path map, so a path map that takes
# anything more out (a namespace silently not embedded, a folder slipped into a records namespace) stays red. The
# overlay's four record folders sit under governance/, which DEC-957's sets already leave out of this comparison.
# W2-15a's raw measure output quotes the visible questions, names gold positions and holds the hidden half's ranks:
# G4 keeps it out of both indexes, as lens B (DEC-1066 (3); the D-7 review's F5).
D7_NOT_EMBEDDED = ("tests/**", "docs/close/**", "docs/checkpoints/**", "docs/probes/**",
                   "docs/assessment/2026-10/B-memory-retrieval.md", "docs/research/EXP-003/w2-15a/raw/**",
                   "fixtures/evaluation/**",
                   "governance/project/orchestration/closes/**", "governance/project/orchestration/nightly/**",
                   "governance/project/orchestration/sessions/**", "governance/project/orchestration/reviews/**")


def test_guard_outside_template_every_verdict_as_at_the_base(tmp_path):
    base = tmp_path / "base"
    (base / PROJECT_DIR).mkdir(parents=True)
    text = subprocess.run(["git", "show", f"{BASE}:{PATH_MAP}"], cwd=ROOT, check=True, capture_output=True).stdout
    (base / PATH_MAP).write_bytes(text)
    outside = [rel for rel in _tracked(inside=False) if not _newly_embedded_by_dec_957(rel)]
    assert outside, "no tracked path outside template/ is left to compare: the case would pass vacuously"
    cut = {rel for rel in outside if any(_matches(rel, pattern) for pattern in D7_NOT_EMBEDDED)}
    assert cut, "no tracked file in D-7's cut: the exception would be vacuous"
    head_db, base_db = tmp_path / "head", tmp_path / "base-db"
    head_db.mkdir(), base_db.mkdir()
    head, before = _selected(ROOT, outside, head_db), _selected(base, outside, base_db)
    still = sorted(head & cut)
    assert still == [], f"{len(still)} files of D-7's cut still embedded, e.g. {still[:5]}"
    moved = sorted((head ^ before) - cut)
    assert moved == [], f"{len(moved)} files outside template/ and D-7's cut gained or lost their embedding, " \
                        f"e.g. {moved[:5]}"
