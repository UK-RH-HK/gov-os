"""W2-61, KPI success 1 -- lens B's 20 questions are the visible development half.

"Lens B's 20 questions and their gold answers (docs/assessment/2026-10/B-memory-retrieval.md section 2) are the
visible development half [DEC-828 item 4, DEC-820 (d)]".

The files: ``fixtures/evaluation/memory-retrieval/visible/*.yaml`` in this worktree, one per question, in the
question form (required ``question``, ``gold_answer``, ``sources``; optional ``id``, ``ticket``, ``ids``,
``radius``). Each ``question`` is exactly the query text of Table 2's Command column, with its ``--ticket``,
``--id`` and ``--radius`` as ``ticket``, ``ids`` and ``radius`` (Table 2 is parsed from lens B's report here).
Every source exists at this worktree's HEAD, every heading it gives is a line of that file there, and no source
names lens B's report or ``fixtures/evaluation/**`` (failure KPI 4).

Red now: the folder does not exist.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_61_support as s  # noqa: E402


def _files():
    files = sorted(s.REAL_VISIBLE.glob("*.yaml")) if s.REAL_VISIBLE.is_dir() else []
    assert files, f"{s.REAL_VISIBLE.relative_to(s.REPO_ROOT)} holds no question file"
    return files


def _load(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{path.name} is not a YAML map"
    return data


def _entries(data):
    """Every source map of a question: an entry, or each alternative of a list entry."""
    sources = data.get("sources")
    assert isinstance(sources, list) and sources, "sources is not a non-empty list"
    found = []
    for entry in sources:
        alternatives = entry if isinstance(entry, list) else [entry]
        assert alternatives, "an empty list of alternatives"
        for alternative in alternatives:
            assert isinstance(alternative, dict) and isinstance(alternative.get("path"), str), (
                f"a source is not a map with a path: {alternative!r}")
            found.append(alternative)
    return found


def _at_head(rel):
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "show", f"HEAD:{rel}"], capture_output=True,
                          timeout=s.TIMEOUT_S)
    return done.stdout.decode("utf-8", "replace") if done.returncode == 0 else None


def _heading_found(text, heading):
    """The measure's rule: a line of the file whose text, trailing whitespace removed, equals the heading."""
    return any(line.rstrip() == heading for line in text.splitlines())


def test_the_visible_half_holds_lens_b_s_twenty_questions_one_file_each():
    files = _files()
    assert len(files) == 20, f"the visible half holds {len(files)} question files, not lens B's 20"
    ids = [(_load(path).get("id") or path.stem) for path in files]
    assert len(set(ids)) == 20, f"the question ids are not distinct: {ids}"


@pytest.mark.parametrize("key", ["question", "gold_answer", "sources"])
def test_every_visible_question_has_the_required_fields(key):
    faults = []
    for path in _files():
        data = _load(path)
        value = data.get(key)
        if key == "sources":
            if not isinstance(value, list) or not value:
                faults.append(path.name)
        elif not isinstance(value, str) or not value.strip():
            faults.append(path.name)
    assert not faults, f"these question files have no {key}: {faults}"


def test_each_question_is_table_2_s_command_with_its_options():
    table = s.lens_b_commands()
    assert len(table) == 20, f"Table 2 of lens B's report parsed to {len(table)} commands, not 20"
    assert table["Q01"]["question"] == "DEC-782"
    assert table["Q12"]["question"] == "CONTINUATION_INVALID"
    assert table["Q09"]["question"] == "How large may the context packet be?"
    expected = sorted((e["question"], e["ticket"], tuple(e["ids"]), e["radius"]) for e in table.values())
    got = []
    for path in _files():
        data = _load(path)
        ids = data.get("ids") or []
        assert isinstance(ids, list), f"{path.name}: ids is not a list"
        got.append((data.get("question"), data.get("ticket"), tuple(str(i) for i in ids),
                    int(data.get("radius") or 0)))
    missing = sorted(set(expected) - set(got))
    extra = sorted(set(got) - set(expected))
    assert sorted(got) == expected, (
        f"the visible questions are not Table 2's commands; missing: {missing}; not in Table 2: {extra}")


def test_every_source_exists_at_head_and_every_heading_is_found_there():
    faults = []
    for path in _files():
        for source in _entries(_load(path)):
            text = _at_head(source["path"])
            if text is None:
                faults.append(f"{path.name}: {source['path']} is not a file at HEAD")
                continue
            heading = source.get("heading")
            if heading is not None and not _heading_found(text, str(heading)):
                faults.append(f"{path.name}: heading {heading!r} is not a line of {source['path']}")
            lines = source.get("lines")
            if lines is not None:
                ok = (isinstance(lines, list) and len(lines) == 2 and all(isinstance(n, int) for n in lines)
                      and 1 <= lines[0] <= lines[1] <= len(text.splitlines()))
                if not ok:
                    faults.append(f"{path.name}: lines {lines!r} are not a span of {source['path']}")
    assert not faults, "\n".join(faults)


def test_no_source_names_the_report_the_set_declares_or_the_evaluation_files():
    sets = yaml.safe_load(s.REAL_PATH_MAP.read_text(encoding="utf-8"))["evaluation_sets"]
    declared = [*sets[s.REAL_SET].get("visible", [])]
    assert s.LENS_B_REL in declared
    faults = []
    for path in _files():
        for source in _entries(_load(path)):
            rel = source["path"].removeprefix("./")
            if rel in declared or rel.startswith("fixtures/evaluation/"):
                faults.append(f"{path.name}: {rel}")
    assert not faults, f"a source names the set's own report or the evaluation files (failure KPI 4): {faults}"


def test_the_measure_takes_the_real_visible_half_by_its_set_s_name(tmp_path):
    """End to end on this worktree: ``memory-retrieval`` declared by this worktree's path map, its 20 visible files
    read in the measure's own form, every source resolved in this worktree; the answers are the planted gov's
    (empty bundles), so the figures are 0 of 20 and the run ends with 0. Only ``--part visible``: the real hidden
    folder is never named to the measure."""
    files = _files()
    world = s.make_world(tmp_path)
    for path in files:
        world.answer(_load(path).get("question"), [[]])
    run = world.measure(s.REAL_SET, "--root", s.REPO_ROOT, "--part", "visible", "--json", root=False,
                        cwd=world.base, role="orchestrator")
    document = run.json()
    assert document.get("set") == s.REAL_SET and document.get("part") == "visible"
    ids = [str(_load(path).get("id") or path.stem) for path in files]
    assert [q.get("id") for q in s.questions(document)] == ids, "the measure did not take the 20 files in order"
    total = document.get("total") or {}
    assert total.get("questions") == 20, f"total: {total}"
    assert (total.get("hit_at_5") or {}).get("of") == 20 and (total.get("full_evidence") or {}).get("of") == 20
    assert {call["cwd"] for call in world.calls()} == {str(s.REPO_ROOT)}
