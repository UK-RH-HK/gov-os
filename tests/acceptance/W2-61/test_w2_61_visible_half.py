"""W2-61, KPI success 1 -- lens B's 20 questions are the visible development half.

"Lens B's 20 questions and their gold answers (docs/assessment/2026-10/B-memory-retrieval.md section 2) are the
visible development half [DEC-828 item 4, DEC-820 (d)]".

The files: ``fixtures/evaluation/memory-retrieval/visible/*.yaml`` in this worktree, one per question, in the
question form (required ``question``, ``gold_answer``, ``sources``; optional ``id``, ``ticket``, ``ids``,
``radius``). Lens B's 20 are ``q01.yaml`` to ``q20.yaml``; each of their ``question`` is exactly the query text of
Table 2's Command column, with its ``--ticket``, ``--id`` and ``--radius`` as ``ticket``, ``ids`` and ``radius``
(Table 2 is parsed from lens B's report here). Further visible files are allowed and meet the form, not Table 2
[DEC-954 (Q9a), DEC-1009].
``q03.yaml`` is the owner's rewritten Q03 (2026-11-03: DEC-1033 replaced DEC-798, the rule lens B's Q03 asked for):
Table 2's Q03 is matched by the retired original, kept unchanged in ``fixtures/evaluation/memory-retrieval/retired/
q03-lens-b.yaml`` outside the visible half, and the rewritten question repeats no Table 2 query. Its label was
checked blind after W2-32's merge (the owner's DEC-1067 (c) form, 2026-11-04): DEC-1065 (1) made the GPU the only
device, so its sources state DEC-1065's rule, and the DEC-1033 label is kept unchanged in
``retired/q03-pre-dec1067.yaml``.
``q09.yaml`` is re-labelled blind (the owner's DEC-1066 (4), 2026-11-03): its question and gold answer are lens B's,
its sources now the Contract's statements of the packet's ceiling with the ticket's KPI lines as one alternative;
Table 2's Q09 is matched by the retired original, kept unchanged in ``retired/q09-lens-b.yaml``.
``q16.yaml`` is re-labelled blind (the owner's DEC-1067 (c), 2026-11-04): lens B's label's one source was DEC-798
item 4, superseded by DEC-1033, so its question names the launch gate's memory rule in force (DEC-961 item 1, the
floor of DEC-947 item 5) and repeats no Table 2 query; Table 2's Q16 is matched by the retired original, kept
unchanged in ``retired/q16-pre-dec1067.yaml``.
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


LENS_B_NAMES = tuple(f"q{n:02d}.yaml" for n in range(1, 21))   # lens B's 20, by file name [DEC-1009]
# The owner's q03 decision of 2026-11-03: q03.yaml rewritten to DEC-1033's rule, lens B's original retired unchanged.
REWRITTEN = "q03.yaml"
RETIRED = s.REAL_VISIBLE.parent / "retired" / "q03-lens-b.yaml"
RETIRED_FROM = "8d09eb40"   # the commit that wrote lens B's Q03 into the visible half
# The DEC-1067 (c) form's check of q03 after W2-32's merge: DEC-1065 (1) replaced DEC-1033's "any device", so q03.yaml
# is re-labelled to DEC-1065's rule and the DEC-1033 label, as 68252f5c wrote it, is kept unchanged in retired/.
RETIRED_Q03_DEC1033 = s.REAL_VISIBLE.parent / "retired" / "q03-pre-dec1067.yaml"
RETIRED_Q03_DEC1033_FROM = "68252f5c"   # the commit that wrote q03's DEC-1033 label
# The owner's Q09 re-label (DEC-1066 (4)): q09.yaml's sources re-set blind, lens B's label retired unchanged; 8d09eb40
# wrote it too.
RELABELLED = "q09.yaml"
RETIRED_Q09 = s.REAL_VISIBLE.parent / "retired" / "q09-lens-b.yaml"
# The owner's DEC-1067 (c) blind label check: q16.yaml re-labelled (DEC-798, its one source, superseded by DEC-1033;
# the question re-worded to the launch gate's rule in force), lens B's label retired unchanged; 8d09eb40 wrote it too.
REWRITTEN_Q16 = "q16.yaml"
RETIRED_Q16 = s.REAL_VISIBLE.parent / "retired" / "q16-pre-dec1067.yaml"
RETIRED_ORIGINALS = {REWRITTEN: RETIRED, RELABELLED: RETIRED_Q09, REWRITTEN_Q16: RETIRED_Q16}


def _files():
    files = sorted(s.REAL_VISIBLE.glob("*.yaml")) if s.REAL_VISIBLE.is_dir() else []
    assert files, f"{s.REAL_VISIBLE.relative_to(s.REPO_ROOT)} holds no question file"
    return files


def _lens_b_files():
    """Lens B's 20 files, ``q01.yaml`` to ``q20.yaml``: every one required [DEC-954 (Q9a), DEC-1009]."""
    _files()
    missing = [name for name in LENS_B_NAMES if not (s.REAL_VISIBLE / name).is_file()]
    assert not missing, f"lens B's question files missing from the visible half: {missing}"
    return [s.REAL_VISIBLE / name for name in LENS_B_NAMES]


def _extra_files():
    """The visible files beyond lens B's 20 (DEC-954 Q9a's new visible questions)."""
    return [path for path in _files() if path.name not in LENS_B_NAMES]


def _table_2_files():
    """The files that hold Table 2's 20 commands: lens B's 20, with the retired originals in the rewritten q03's and
    the re-labelled q09's and q16's places (the owner's q03 decision of 2026-11-03; DEC-1066 (4); DEC-1067 (c))."""
    for retired in RETIRED_ORIGINALS.values():
        assert retired.is_file(), f"{retired.relative_to(s.REPO_ROOT)} (lens B's original) is not on record"
    return [RETIRED_ORIGINALS.get(path.name, path) for path in _lens_b_files()]


def _command(path):
    """A question file's command: its query with its ticket, ids and radius, as Table 2 gives them."""
    data = _load(path)
    ids = data.get("ids") or []
    assert isinstance(ids, list), f"{path.name}: ids is not a list"
    return (data.get("question"), data.get("ticket"), tuple(str(i) for i in ids), int(data.get("radius") or 0))


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
    """Lens B's 20 files, ``q01.yaml`` to ``q20.yaml``, all exist; further visible files are allowed (DEC-954 Q9a's
    48 questions put 4 new ones beside lens B's 20) and each meets the question form, which the required-fields and
    sources cases check over every visible file; every question id is distinct [DEC-954 (Q9a), DEC-1009]."""
    files = _files()
    _lens_b_files()
    ids =[(_load(path).get("id") or path.stem) for path in files]
    assert len(set(ids)) == len(ids), f"the question ids are not distinct: {ids}"


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
    """Lens B's 20 files, ``q01.yaml`` to ``q20.yaml``, are exactly Table 2's 20 commands with their options, at
    full strength, with the retired originals in the rewritten ``q03.yaml``'s and the re-labelled ``q09.yaml``'s
    places (``q09.yaml`` keeps lens B's question, which its own case checks); a visible file beyond them, and
    the rewritten ``q03.yaml``, is not required to be a Table 2 command, and none repeats a Table 2 query (failure
    KPI: no question copied from lens B's 20). Failure messages name files and Table 2 rows by id only, never a
    question's text [DEC-954 (Q9a), DEC-1009, DEC-820 (d); the owner's q03 decision of 2026-11-03]."""
    table = s.lens_b_commands()
    assert len(table) == 20, f"Table 2 of lens B's report parsed to {len(table)} commands, not 20"
    assert table["Q01"]["question"] == "DEC-782"
    assert table["Q12"]["question"] == "CONTINUATION_INVALID"
    assert table["Q09"]["question"] == "How large may the context packet be?"
    commands = {qid: (e["question"], e["ticket"], tuple(e["ids"]), e["radius"]) for qid, e in table.items()}
    expected = sorted(commands.values())
    got = {path.name: _command(path) for path in _table_2_files()}
    unmatched = sorted(qid for qid, command in commands.items() if command not in got.values())
    not_in_table = sorted(name for name, command in got.items() if command not in commands.values())
    assert sorted(got.values()) == expected, (
        f"lens B's 20 files are not Table 2's commands; Table 2 rows not matched: {unmatched}; "
        f"files not in Table 2: {not_in_table}")
    queries = {command[0] for command in commands.values()}
    copies = [path.name for path in [*_extra_files(), s.REAL_VISIBLE / REWRITTEN, s.REAL_VISIBLE / REWRITTEN_Q16]
              if _load(path).get("question") in queries]
    assert not copies, (
        f"a visible file beyond lens B's 20, or the rewritten q03 or q16, repeats a Table 2 query: {copies}")


def test_q03_is_relabelled_to_dec_1065_and_the_earlier_labels_are_kept_unchanged():
    """The owner's q03 decision of 2026-11-03, then the DEC-1067 (c) form's check after W2-32's merge (2026-11-04):
    lens B's original Q03 is kept, byte for byte as W2-61 wrote it, and the DEC-1033 label, byte for byte as
    68252f5c wrote it, both in ``retired/`` outside the visible half; the visible ``q03.yaml`` keeps the id Q03 and
    the DEC-1033 label's question, its gold answer is not that label's, and its sources state the rule in force:
    each source span (the measure's rule: a heading found governs) holds DEC-1065 at HEAD, and none is DEC-798's
    entry or DEC-1033's, whose "any device" DEC-1065 (1) replaced."""
    rel = (s.REAL_VISIBLE / REWRITTEN).relative_to(s.REPO_ROOT).as_posix()
    for retired, commit, label in ((RETIRED, RETIRED_FROM, "lens B's Q03"),
                                   (RETIRED_Q03_DEC1033, RETIRED_Q03_DEC1033_FROM, "q03's DEC-1033 label")):
        done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "show", f"{commit}:{rel}"], capture_output=True,
                              timeout=s.TIMEOUT_S)
        assert done.returncode == 0, f"{label} is not found at {commit}"
        assert retired.is_file() and retired.read_bytes() == done.stdout, (
            f"{retired.relative_to(s.REPO_ROOT)} is not {label} as {commit} wrote it")
        assert retired.parent != s.REAL_VISIBLE
    data, earlier = _load(s.REAL_VISIBLE / REWRITTEN), _load(RETIRED_Q03_DEC1033)
    assert data.get("id") == "Q03", "the rewritten q03 does not keep the id Q03"
    assert data.get("question") != _load(RETIRED).get("question"), "q03 still asks lens B's question"
    assert data.get("question") == earlier.get("question"), "q03 no longer asks the DEC-1033 label's question"
    assert data.get("gold_answer") != earlier.get("gold_answer"), "q03 still gives the DEC-1033 label's answer"
    faults = []
    for source in _entries(data):
        span = _span_at_head(source)
        if span is None:
            faults.append(f"{source['path']} is not a file at HEAD")
            continue
        heading = str(source.get("heading") or "")
        if "DEC-1065" not in "\n".join(span):
            faults.append(f"{source['path']}: its span does not hold DEC-1065")
        if heading.startswith("### DEC-798 ") or heading.startswith("### DEC-1033 "):
            faults.append(f"{source['path']}: DEC-798's or DEC-1033's entry, a replaced rule")
    assert not faults, "\n".join(faults)


def _span_at_head(source):
    """A source's lines at HEAD by the measure's rule (a heading found governs: a ``#`` heading to the next of its
    level or higher, any other as many lines as ``lines`` state; not found, ``lines``), or None when no file."""
    text = _at_head(source["path"])
    if text is None:
        return None
    lines = text.splitlines()
    heading, stated = source.get("heading"), source.get("lines")
    at = next((i for i, line in enumerate(lines) if heading is not None and line.rstrip() == str(heading).rstrip()),
              None)
    if at is not None and str(heading).startswith("#"):
        level = len(str(heading)) - len(str(heading).lstrip("#"))
        end = next((j for j in range(at + 1, len(lines)) if lines[j].startswith("#")
                    and len(lines[j]) - len(lines[j].lstrip("#")) <= level), len(lines))
        return lines[at:end]
    if at is not None:
        return lines[at:at + (stated[1] - stated[0] + 1 if stated else 1)]
    return lines[stated[0] - 1:stated[1]] if stated else lines


def test_q09_is_relabelled_to_the_contract_and_the_original_is_kept_unchanged():
    """The owner's Q09 re-label (DEC-1066 (4), 2026-11-03): lens B's Q09 is kept, byte for byte as W2-61 wrote it,
    in ``retired/`` outside the visible half; the visible ``q09.yaml`` keeps its id, question, gold answer and
    ticket; its sources are one entry of alternatives that names the Contract (``docs/contract/``) and keeps the
    ticket's KPI lines, and each alternative's span (the measure's rule) states the packet's ceiling of ~6k tokens
    at HEAD."""
    rel = (s.REAL_VISIBLE / RELABELLED).relative_to(s.REPO_ROOT).as_posix()
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "show", f"{RETIRED_FROM}:{rel}"], capture_output=True,
                          timeout=s.TIMEOUT_S)
    assert done.returncode == 0, f"lens B's Q09 is not found at {RETIRED_FROM}"
    assert RETIRED_Q09.is_file() and RETIRED_Q09.read_bytes() == done.stdout, (
        f"{RETIRED_Q09.relative_to(s.REPO_ROOT)} is not lens B's Q09 as {RETIRED_FROM} wrote it")
    assert RETIRED_Q09.parent != s.REAL_VISIBLE
    data, original = _load(s.REAL_VISIBLE / RELABELLED), _load(RETIRED_Q09)
    for key in ("id", "question", "gold_answer", "ticket"):
        assert data.get(key) == original.get(key), f"the re-labelled q09 does not keep lens B's {key}"
    sources = data.get("sources")
    assert isinstance(sources, list) and len(sources) == 1 and isinstance(sources[0], list), (
        "q09's sources are not one entry of alternatives")
    alternatives = _entries(data)
    paths = [source["path"] for source in alternatives]
    assert any(path.startswith("docs/contract/") for path in paths), "no source of q09 is the Contract"
    assert any(source in alternatives for source in _entries(original)), "q09 no longer keeps the ticket's KPI lines"
    faults = []
    for source in alternatives:
        span = _span_at_head(source)
        if span is None:
            faults.append(f"{source['path']} is not a file at HEAD")
        elif "6k tokens" not in "\n".join(span):
            faults.append(f"{source['path']} ({source.get('heading')!r}): its span does not state ~6k tokens")
    assert not faults, "\n".join(faults)


def test_q16_is_relabelled_off_dec_798_and_the_original_is_kept_unchanged():
    """The owner's DEC-1067 (c), 2026-11-04: lens B's Q16 label is kept, byte for byte as W2-61 wrote it, in
    ``retired/`` outside the visible half; the visible ``q16.yaml`` keeps the id Q16, no longer asks lens B's question,
    and no source is DEC-798's entry or its item 4 (superseded by DEC-1033): the rule's entry has DEC-961 item 1's
    span among its alternatives and another entry DEC-947 item 5's floor, each span (the measure's rule) found at
    HEAD."""
    rel = (s.REAL_VISIBLE / REWRITTEN_Q16).relative_to(s.REPO_ROOT).as_posix()
    done = subprocess.run(["git", "-C", str(s.REPO_ROOT), "show", f"{RETIRED_FROM}:{rel}"], capture_output=True,
                          timeout=s.TIMEOUT_S)
    assert done.returncode == 0, f"lens B's Q16 is not found at {RETIRED_FROM}"
    assert RETIRED_Q16.is_file() and RETIRED_Q16.read_bytes() == done.stdout, (
        f"{RETIRED_Q16.relative_to(s.REPO_ROOT)} is not lens B's Q16 as {RETIRED_FROM} wrote it")
    assert RETIRED_Q16.parent != s.REAL_VISIBLE
    data = _load(s.REAL_VISIBLE / REWRITTEN_Q16)
    assert data.get("id") == "Q16", "the re-labelled q16 does not keep the id Q16"
    assert data.get("question") != _load(RETIRED_Q16).get("question"), "q16 still asks lens B's question"
    spans, faults = [], []
    for source in _entries(data):
        span = _span_at_head(source)
        if span is None:
            faults.append(f"{source['path']} is not a file at HEAD")
            continue
        text = "\n".join(span)
        spans.append(text)
        if str(source.get("heading") or "").startswith("### DEC-798 ") or "CPU embedder's 2.4 GB" in text:
            faults.append(f"{source['path']}: DEC-798's entry or its item 4, the superseded decision")
    assert any("No memory is set aside for a full test run" in text for text in spans), (
        "no source of q16 is DEC-961 item 1, the rule in force")
    assert any("The floor goes from 6.4 GiB to 3 GiB" in text for text in spans), (
        "no source of q16 is DEC-947 item 5, the floor")
    assert not faults, "\n".join(faults)


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
    """End to end on this worktree: ``memory-retrieval`` declared by this worktree's path map, its visible files
    read in the measure's own form, every source resolved in this worktree; the answers are the planted gov's
    (empty bundles), so the figures are 0 of N and the run ends with 0. The measure's total equals the number of
    question files in the real visible folder, counted here (lens B's 20 and any further visible file), not a
    literal 20 [DEC-954 (Q9a), DEC-1009]. Only ``--part visible``: the real hidden folder is never named to the
    measure."""
    files = _files()
    world = s.make_world(tmp_path)
    for path in files:
        world.answer(_load(path).get("question"), [[]])
    run = world.measure(s.REAL_SET, "--root", s.REPO_ROOT, "--part", "visible", "--json", root=False,
                        cwd=world.base, role="orchestrator")
    document = run.json()
    assert document.get("set") == s.REAL_SET and document.get("part") == "visible"
    ids = [str(_load(path).get("id") or path.stem) for path in files]
    assert [q.get("id") for q in s.questions(document)] == ids, (
        f"the measure did not take the {len(files)} files in order")
    total = document.get("total") or {}
    assert total.get("questions") == len(files), f"total: {total}; visible question files: {len(files)}"
    assert ((total.get("hit_at_5") or {}).get("of") == len(files)
            and (total.get("full_evidence") or {}).get("of") == len(files))
    assert {call["cwd"] for call in world.calls()} == {str(s.REPO_ROOT)}
