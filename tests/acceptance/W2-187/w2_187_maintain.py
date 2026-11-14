"""Helpers of S10 only (the maintenance pass): they move to W2-187b with it, whole.

Planted here: commits on the main line (a store some commits behind), a rebuild plan for the planted ``gov``, a store layout
stamp, the store's lexical chunks (all tracked paths but a few), reader rows of earlier runs, and a set whose cited blocks
changed or moved between the question's commit and the audit commit.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path

import yaml

import w2_187_world as W
from w2_187_world import W171

KEPT_OUT = ("docs/research/evalsrc/", "fixtures/evaluation/", "fixtures/memory-quality/")  # the planted path map's two namespaces
AUDIT_SET = "memory-audit-20261103"
RQ, RG, RP = ("falconreach", "gimletwhorl"), ("heronwick", "inkwellmoor"), ("hollowtarn", "ivorycleft")
WORDS = [*RQ, *RG, *RP]


def behind(world, count: int) -> str:
    """``count`` more commits on the main line after the link's: the store is that many (plus the template's) behind."""
    head = None
    for k in range(count):
        head = world.repo_commit(f"2026-11-10T0{k + 1}:00:00+00:00", {f"docs/std/behind-{k}.md": f"behind {k}\n"}, f"c{k}")
    return head


def plan_rebuild(world, **spec) -> None:
    world.write_x_plan(rebuild={"link": str(world.link), **spec})


def rebuild_calls(world) -> list[dict]:
    return [c for c in world.gov_x_calls() if c["argv"][:1] == ["rebuild"]]


def links_calls(world) -> list[dict]:
    return [c for c in world.gov_x_calls() if c["argv"][:1] == ["links"]]


def maintain_line(run) -> str:
    lines = [x for x in run.lines if x.startswith("MAINTAIN ")]
    assert len(lines) == 1, run
    return lines[0]


def tracked(world) -> list[str]:
    out = subprocess.run(["git", "-C", str(world.link), "ls-tree", "-r", "--name-only", "-z", "HEAD"], capture_output=True,
                         check=True).stdout.decode()
    return sorted(p for p in out.split("\0") if p)


def candidates(world) -> list[str]:
    """The tracked paths of the link's work tree that the path map does not keep out of the lexical index."""
    return [p for p in tracked(world) if not p.startswith(KEPT_OUT)]


def plant_chunks(world, skip=()) -> None:
    con = sqlite3.connect(world.link / ".gov-runtime" / "store.db")
    con.execute("DROP TABLE IF EXISTS lexical_chunk")
    con.execute("CREATE TABLE lexical_chunk (id TEXT, chunk_id TEXT, path TEXT, start_line INTEGER, end_line INTEGER, parent_id TEXT)")
    for k, path in enumerate(p for p in candidates(world) if p not in set(skip)):
        con.execute("INSERT INTO lexical_chunk VALUES (?, ?, ?, 1, 3, ?)", (f"c{k}", f"k{k}", path, f"p{k}"))
    con.commit()
    con.close()


def stamp_layout(world, version: int) -> None:
    con = sqlite3.connect(world.link / ".gov-runtime" / "store.db")
    con.execute("CREATE TABLE IF NOT EXISTS store_layout (version INTEGER NOT NULL)")
    con.execute("DELETE FROM store_layout")
    con.execute("INSERT INTO store_layout VALUES (?)", (version,))
    con.commit()
    con.close()


def reader_row(qid: str, *, verdict: str = "answer", searches: int = 0) -> dict:
    return {"id": qid, "final_verdict": verdict,
            "searches": [{"attempt": k + 1, "ok": True, "why": None, "rerank_by": "service"} for k in range(searches)]}


def plant_rows(folder: Path, rows: list[dict]) -> None:
    (folder / "reader").mkdir(parents=True)
    for row in rows:
        (folder / "reader" / f"{row['id']}.json").write_text(json.dumps(row), encoding="utf-8")


def plant_reader_runs(world) -> tuple[int, int]:
    """Standing weeks W44 (older: 5 not found) and W45 (2 not found, 3 second searches) and the latest fresh run (1 not
    found, 2 second searches): the pass counts the latest of each, ``(3, 5)``."""
    runs = world.sets / "runs"
    plant_rows(runs / W.STD / "2026-W44", [reader_row(f"q0{k}", verdict="not_found") for k in range(1, 6)])
    plant_rows(runs / W.STD / "2026-W45", [reader_row("q01", verdict="not_found"), reader_row("q02", verdict="not_found"),
                                           *[reader_row(f"q0{k}", searches=1) for k in (3, 4, 5)]])
    plant_rows(runs / "memory-audit-20261110", [reader_row("q01", verdict="not_found"), reader_row("q02", searches=1),
                                                reader_row("q03", searches=2), reader_row("q04")])
    return 3, 5


def block(first: int, last: int, words: str) -> str:
    return "".join(f"{words} line {k}\n" for k in range(first, last + 1))


def plant_reanchor_set(world) -> tuple[str, str]:
    """A set of two questions, each citing lines 3-8 of a file at commit ``d1``: ``q01``'s block moves unchanged in ``d2``
    (three lines inserted above it), ``q02``'s block is rewritten. The link is at ``d2``. Returns ``(d1, d2)``."""
    files = {f"docs/std/{RP[0]}.md": "# moved\n\n" + block(1, 6, "stays") + "tail\n",
             f"docs/std/{RP[1]}.md": "# changed\n\n" + block(1, 6, "was") + "tail\n"}
    d1 = world.repo_commit("2026-11-10T01:00:00+00:00", files, "anchors v1")
    files = {f"docs/std/{RP[0]}.md": "# moved\n\nnew a\nnew b\nnew c\n" + block(1, 6, "stays") + "tail\n",
             f"docs/std/{RP[1]}.md": "# changed\n\n" + block(1, 6, "became") + "tail\n"}
    d2 = world.repo_commit("2026-11-10T02:00:00+00:00", files, "anchors v2")
    world.relink(d2)
    hidden = world.sets / "fixtures" / "evaluation" / AUDIT_SET / "hidden"
    hidden.mkdir(parents=True)
    for k in (0, 1):
        doc = {"id": f"q0{k + 1}", "question": f"Which {RQ[k]} line is cited?", "gold_answer": f"The {RG[k]} line.",
               "sources": [{"path": f"docs/std/{RP[k]}.md", "lines": [3, 8]}], "commit": d1, "category": "plan", "drawn": "sample"}
        (hidden / f"q0{k + 1}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    W.add_map_entry(world.sets, AUDIT_SET)
    return d1, d2


SEC = {k: (f"vellumdrift{k}", f"thistlewane{k}", f"marrowpike{k}") for k in range(1, 9)}   # (question, answer, file) words
SECTION_WORDS = [w for words in SEC.values() for w in words] + ["Sectone", "Subtwo", "Aftern"]


def section_doc(file_word: str, *, intro=("intro",), sect="body one", sub="sub body", after="after body", tail=()) -> str:
    """A document with a ``##`` section that holds a ``###`` sub-section, then a following ``##`` section (a heading-cited
    source's section runs from its ``## Sectone`` line to the line before ``## Aftern``, the sub-section inside it)."""
    lines = [f"# {file_word}", *intro, "## Sectone", sect, "### Subtwo", sub, "## Aftern", after, *tail]
    return "\n".join(lines) + "\n"


def plant_section_set(world) -> tuple[str, str, list[tuple[str, int]]]:
    """DEC-1180 (1) N2 (b): a set of heading-cited questions, each file at ``d1`` (the questions' commit) and at ``d2`` (the
    link's head). What happens to the cited section between them (each heading is still found at ``d2``):
    q01 body line rewritten: listed; q02 three lines inserted above the section, section unchanged: not listed (it moved);
    q03 nothing changed: not listed; q04 a line of the ``###`` sub-section inside it rewritten: listed; q05 a line of the
    following ``##`` section rewritten, the cited section unchanged: not listed; q06 one entry of two alternatives, a section
    that both moved (three lines inserted above) and changed, and a line-cited block rewritten, then a control entry: listed
    once, entry 1; q07 the last section of its file (to the end of the file) with a line appended: listed; q08 a control
    entry, then a changed section: entry 2. Returns ``(d1, d2, expected)`` with ``expected`` the (id, entry) pairs, sorted."""
    docs = {f"q0{k}": f"docs/std/{SEC[k][2]}.md" for k in range(1, 9)}
    lined = "docs/std/{}-lines.md".format(SEC[6][2])
    v1 = {docs[q]: section_doc(SEC[int(q[1:])][2]) for q in docs}
    v1[docs["q07"]] = f"# {SEC[7][2]}\nintro\n## Sectone\nbody one\n"
    v1[lined] = "# lines\n\n" + block(1, 6, "was") + "tail\n"
    d1 = world.repo_commit("2026-11-10T01:00:00+00:00", v1, "sections v1")
    v2 = {docs["q01"]: section_doc(SEC[1][2], sect="body one REWRITTEN"),
          docs["q02"]: section_doc(SEC[2][2], intro=("intro", "new a", "new b", "new c")),
          docs["q04"]: section_doc(SEC[4][2], sub="sub body REWRITTEN"),
          docs["q05"]: section_doc(SEC[5][2], after="after body REWRITTEN"),
          docs["q06"]: section_doc(SEC[6][2], intro=("intro", "new a", "new b", "new c"), sect="body one REWRITTEN"),
          docs["q07"]: f"# {SEC[7][2]}\nintro\n## Sectone\nbody one\nbody two appended\n",
          docs["q08"]: section_doc(SEC[8][2], sect="body one REWRITTEN"),
          lined: "# lines\n\n" + block(1, 6, "became") + "tail\n"}
    d2 = world.repo_commit("2026-11-10T02:00:00+00:00", v2, "sections v2")
    world.relink(d2)
    hidden = world.sets / "fixtures" / "evaluation" / AUDIT_SET / "hidden"
    hidden.mkdir(parents=True)
    head = {"heading": "## Sectone"}
    control = {"path": docs["q03"], **head}
    sources = {"q01": [{"path": docs["q01"], **head}], "q02": [{"path": docs["q02"], **head}], "q03": [control],
               "q04": [{"path": docs["q04"], **head}], "q05": [{"path": docs["q05"], **head}],
               "q06": [[{"path": docs["q06"], **head}, {"path": lined, "lines": [3, 8]}], control],
               "q07": [{"path": docs["q07"], **head}], "q08": [control, {"path": docs["q08"], **head}]}
    for q, entries in sources.items():
        k = int(q[1:])
        doc = {"id": q, "question": f"Which {SEC[k][0]} section is cited?", "gold_answer": f"The {SEC[k][1]} section.",
               "sources": entries, "commit": d1, "category": "plan", "drawn": "sample"}
        (hidden / f"{q}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    W.add_map_entry(world.sets, AUDIT_SET)
    return d1, d2, [("q01", 1), ("q04", 1), ("q06", 1), ("q07", 1), ("q08", 2)]


def maintain_lines(world) -> list[dict]:
    return world.jsonl_file(world.mem / "MAINTAIN.jsonl")


def digests(world) -> dict:
    sha = W171.sha_file
    return {"retrieval.yaml": sha(world.repo / "governance/project/retrieval.yaml"),
            "path-map": sha(world.repo / "governance/project/path-map.yaml"),
            "sets-map": sha(world.sets / "governance/project/path-map.yaml")}


def repo_status(world) -> str:
    return subprocess.run(["git", "-C", str(world.repo), "status", "--porcelain", "--untracked-files=all"], capture_output=True,
                          text=True, env=W171.git_env(world.home), check=True).stdout


def real(path) -> str:
    return os.path.realpath(path)
