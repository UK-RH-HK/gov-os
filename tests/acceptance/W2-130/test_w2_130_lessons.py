"""S7: each lesson names the decision or failure it came from in a ``sources:`` key."""

from __future__ import annotations

import re

import yaml

import w2_130_support as s

LESSONS = sorted((s.ROOT / "docs" / "lessons").glob("*.md"))


def _front(text: str) -> dict:
    return yaml.safe_load(text.split("\n---\n", 1)[0].removeprefix("---\n")) or {}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def test_s7_every_lesson_at_head_has_a_front_matter_sources_key_naming_at_least_one_id(head_tree):
    files = sorted((head_tree / "docs" / "lessons").glob("*.md"))
    assert files, "docs/lessons holds no lesson"
    bad = []
    for path in files:
        sources = _front(path.read_text(encoding="utf-8")).get("sources")
        if not (isinstance(sources, list) and sources and all(isinstance(i, str) and i.strip() for i in sources)):
            bad.append(path.name)
    assert not bad, f"lessons with no sources: naming an id: {bad}"


def test_s7_gov_links_reports_no_unknown_id_with_a_lesson_s_path(head_findings):
    bad = [(f["ids"], f["path"]) for f in head_findings if f["code"] == "UNKNOWN_ID" and f["path"].startswith("docs/lessons/")]
    assert not bad, f"{bad}"


def test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from(record, head_tree):
    data = record.data("lessons")
    files = {p.stem: p.read_text(encoding="utf-8") for p in sorted((head_tree / "docs" / "lessons").glob("*.md"))}
    assert isinstance(data, dict) and set(data) == set(files), f"lessons: {sorted(set(data) ^ set(files))}"
    bad = []
    for name, text in files.items():
        entry, sources = data[name], _front(text).get("sources")
        if not isinstance(entry, dict) or entry.get("agree") is not True:
            bad.append((name, "agree is not true"))
            continue
        if sorted(map(str, entry.get("sources") or [])) != sorted(map(str, sources or [])):
            bad.append((name, "the record's sources differ from the lesson's front matter"))
        said = str(entry.get("came_from", "")).strip()
        if not said or _norm(said) not in _norm(text):
            bad.append((name, "came_from is empty or not the lesson's own words"))
        source_line = [line for line in text.splitlines() if line.startswith("**Source:**")]
        named = set(re.findall(r"\bDEC-\d+\b", " ".join(source_line)))
        if not named <= set(map(str, sources or [])):
            bad.append((name, f"the lesson's **Source:** line names {sorted(named - set(sources or []))} (decisions) its sources: lack"))
    assert not bad, f"{bad}"


def test_s7_the_lessons_commit_changes_only_lessons_each_by_the_one_added_sources_line(record):
    commit = record.commit_list("lessons")[0]
    changed = s.changed_files(commit)
    assert changed and all(p.startswith("docs/lessons/") and p.endswith(".md") and f == "M" for p, f in changed.items()), (
        f"the lessons commit changes {sorted(changed)}")
    before, bad = s.parent(commit), []
    for path in changed:
        old, new = s.show(before, path).split("\n"), s.show(commit, path).split("\n")
        closing = old.index("---", 1)
        wanted = old[:closing] + [new[closing]] + old[closing:]
        if len(new) != len(old) + 1 or new != wanted or not new[closing].startswith("sources: ["):
            bad.append(path)
    assert not bad, f"not the old file plus one `sources: [...]` line before the closing ---: {bad}"
    assert sorted(changed) == sorted(f"docs/lessons/{p.name}" for p in LESSONS), "a lesson was left without the key"
