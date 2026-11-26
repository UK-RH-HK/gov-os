"""The fix under the closed ticket DAEO-ma4q (W2-204), line FR-1 (DEC-1254 E-02's note): ``gov memaudit forbidden-reach``
counts whether the forbidden sources an audit's misses cited are now outside default memory.

The command is driven only as a child process (``python3 -m gov.cli.main memaudit forbidden-reach``; one case runs
``python3 -m gov.memaudit`` beside it). Everything is planted under pytest's temporary folder: a git repository with its
path map and tracked files, and a sets root holding the judged rows ``runs/<audit>/reader/<id>.json`` in the shape the
judge writes and the question files ``fixtures/evaluation/<audit>/hidden/<id>.yaml``.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest
import yaml

import w2_204_support as K

AUDIT = "memory-audit-26112502"
HEAD = "FORBIDDEN-REACH"

# Every planted path, question, gold answer and reader answer holds one of these words, found nowhere else.
PATH_WORD, ASKED_WORD, GOLD_WORD, SAID_WORD = "zorvexal", "plimquor", "hasterfen", "wubbrint"
PLANTED = (PATH_WORD, ASKED_WORD, GOLD_WORD, SAID_WORD)


def _p(folder: str, name: str) -> str:
    return f"{folder}/{PATH_WORD}-{name}.md"


GOLD = _p("code", "gold")                 # the gold source of every question
OLD_A, OLD_B = _p("archive", "a"), _p("archive", "b")       # stale-classed, not indexed, not embedded
LIVE = _p("docs", "live")                 # a live namespace
LIVE_2 = _p("docs", "live-two")
SEALED = _p("docs/sealed", "shut")        # held by `docs` (live) first and by `sealed` (not indexed) second
TWICE = _p("docs/twice", "both")          # held by `docs` and by `mirror`, both live
FROZEN = _p("frozen", "ice")              # not indexed, no stale class
QUIET = _p("quiet", "hush")               # not embedded only
LOOSE = _p("loose", "nowhere")            # in no namespace
GONE = _p("docs", "removed")              # tracked, then removed from the repository
NEVER = _p("docs", "never-added")         # in the working tree, never tracked
COMMITTED = (GOLD, OLD_A, OLD_B, LIVE, LIVE_2, SEALED, TWICE, FROZEN, QUIET, LOOSE, GONE)

STALE = {"stale_class": "historical", "lexical_policy": "not indexed", "embedding_policy": "not embedded"}


def path_map() -> dict:
    return {"version": 1, "namespaces": {
        "code": {"paths": ["code/**"], "embedding_policy": "embedded"},
        "archive": {"paths": ["archive/**"], **STALE},
        "docs": {"paths": ["docs/**"], "embedding_policy": "embedded"},
        "sealed": {"paths": ["docs/sealed/**"], "lexical_policy": "not indexed", "embedding_policy": "not embedded"},
        "mirror": {"paths": ["docs/twice/**"], "embedding_policy": "embedded"},
        "frozen": {"paths": ["frozen/**"], "lexical_policy": "not indexed", "embedding_policy": "not embedded"},
        "quiet": {"paths": ["quiet/**"], "embedding_policy": "not embedded"},
    }}


def attempt(n: int, verdict, *paths: str) -> dict:
    """One attempt as the judge records it; a path may be cited more than once, on other lines."""
    cites = [{"path": path, "start_line": 1 + at, "end_line": 2 + at} for at, path in enumerate(paths)]
    return {"attempt": n, "model": "claude-sonnet-5-5", "cost_usd": 0.01, "retried": False, "verdict": verdict,
            "answer": f"The {SAID_WORD} answer." if verdict == "answer" else None, "citations": cites}


class Planted:
    def __init__(self, base: Path):
        self.home, self.repo, self.sets, self.work = base / "home", base / "repo", base / "sets", base / "work"
        for folder in (self.home, self.repo, self.sets, self.work):
            folder.mkdir()
        self.run_dir = self.sets / "runs" / AUDIT
        self.hidden = self.sets / "fixtures" / "evaluation" / AUDIT / "hidden"
        self.git("init", "-q")
        self.git("checkout", "-q", "-b", "main")
        for rel in COMMITTED:
            self.write(self.repo, rel, f"# Planted {PATH_WORD} page\n\nOne line.\nTwo lines.\n")
        self.write_map(path_map())
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("rm", "-q", GONE)
        self.git("commit", "-q", "-m", "a page is removed")
        self.write(self.repo, NEVER, "never added\n")
        entry = {"visible": [], "hidden": [f"fixtures/evaluation/{AUDIT}/hidden/**"],
                 "measures": {"roles": ["no-such-role-w2-204"]}}
        self.write(self.sets, "governance/project/path-map.yaml",
                   yaml.safe_dump({"version": 1, "evaluation_sets": {AUDIT: entry}}, sort_keys=False))

    def git(self, *args: str) -> str:
        return K.W171.git(self.repo, *args, home=self.home)

    @staticmethod
    def write(root: Path, rel: str, text: str) -> None:
        K.W171._write(root, rel, text)

    def write_map(self, doc: dict) -> None:
        self.write(self.repo, "governance/project/path-map.yaml", yaml.safe_dump(doc, sort_keys=False))

    def question(self, qid: str, forbidden) -> None:
        doc = {"id": qid, "question": f"What does the {ASKED_WORD} rule {qid} say?",
               "gold_answer": f"It says {GOLD_WORD} {qid}.",
               "sources": [{"path": GOLD, "heading": f"# Planted {PATH_WORD} page", "lines": [1, 4]}],
               "category": "decision"}
        if forbidden is not None:
            doc["forbidden"] = list(forbidden)
        self.write(self.hidden, f"{qid}.yaml", yaml.safe_dump(doc, sort_keys=False))

    def row(self, qid: str, attempts: list[dict], forbidden_cited: bool = True) -> None:
        final = next((a for a in reversed(attempts) if a["verdict"] in ("answer", "search_again", "not_found")), None)
        verdict = attempts[-1]["verdict"]
        verdict = {"answer": "answer", "not_found": "not_found", "search_again": "not_found"}.get(verdict, "error")
        row = {"id": qid, "kind": "audit", "apart": False, "final_verdict": verdict, "attempts": attempts,
               "answered_at": len(attempts) if verdict == "answer" else None,
               "gold_in_bundle": [True for _ in attempts], "citation_right": False,
               "forbidden_cited": forbidden_cited, "grades": {}, "searches": [], "search_failures": 0,
               "citations": len((final or {}).get("citations") or []), "citations_outside": 0,
               "citation_right_only_outside": False, "calls_retried": 0, "first_stopping_reason": "SUFFICIENT",
               "first_gaps_name_ids": None}
        self.write(self.run_dir / "reader", f"{qid}.json", json.dumps(row))
        ids = sorted(f.stem for f in (self.run_dir / "reader").glob("q*.json"))
        self.write(self.run_dir / "reader", "plan.json", json.dumps({"ids": ids, "apart": [], "projection": 0.5}))

    def miss(self, qid: str, forbidden, cites=None) -> None:
        """A judged row marked ``forbidden_cited``: one answer citing the gold source and ``cites``."""
        self.question(qid, forbidden)
        self.row(qid, [attempt(1, "answer", GOLD, *(forbidden if cites is None else cites))])

    def run(self, *extra: str, entry: str = "cli", repo: bool = True, cwd: Path | None = None,
            audit: str = AUDIT) -> subprocess.CompletedProcess:
        argv = [*K.ENTRIES[entry], "forbidden-reach", "--sets-root", str(self.sets), "--audit", audit, *extra]
        if repo:
            argv += ["--repo", str(self.repo)]
        return subprocess.run(argv, cwd=str(cwd or self.work), env=K.W171.child_env(self.home),
                              capture_output=True, text=True, timeout=60)

    def snapshot(self) -> dict:
        found = K.W171.snapshot(self.sets, self.repo, self.work)
        inside_git = str(self.repo / ".git") + "/"
        return {path: value for path, value in found.items() if not path.startswith(inside_git)}


@pytest.fixture
def planted(tmp_path) -> Planted:
    return Planted(tmp_path)


def assert_line(done: subprocess.CompletedProcess, line: str) -> None:
    assert (done.returncode, done.stdout.splitlines()) == (0, [line]), (done.returncode, done.stdout, done.stderr)
    assert done.stderr == "", done.stderr


def assert_refused(done: subprocess.CompletedProcess, code: str) -> None:
    assert (done.returncode, done.stdout.splitlines()) == (1, [code]), (done.returncode, done.stdout, done.stderr)
    assert done.stderr.splitlines() in ([], [code]), done.stderr


def three_misses(planted: Planted) -> None:
    """The K-line's case: three misses citing forbidden sources, two in the stale-classed namespace, one in a live one."""
    planted.miss("q05", [OLD_A])
    planted.miss("q07", [OLD_B])
    planted.miss("q09", [LIVE])


TWO_OUT = f"{HEAD} 3 cited, 2 outside, 1 inside; archive: 2, docs: 1"
ALL_OUT = f"{HEAD} 3 cited, 3 outside, 0 inside; archive: 2, docs: 1"


# ==== the K-line's Verify ============================================================================================
def test_fr1_two_cited_sources_are_outside_and_the_live_namespace_s_one_is_inside(planted):
    three_misses(planted)
    assert_line(planted.run(), TWO_OUT)


def test_fr1_the_live_namespace_gaining_the_class_in_the_working_tree_takes_the_third_out(planted):
    three_misses(planted)
    assert_line(planted.run(), TWO_OUT)
    changed = path_map()
    changed["namespaces"]["docs"].update(STALE)
    planted.write_map(changed)  # not committed: the working tree's file is the current policy
    assert_line(planted.run(), ALL_OUT)


def test_fr1_the_output_holds_no_path_question_answer_or_id(planted):
    three_misses(planted)
    done = planted.run()
    assert done.returncode == 0, (done.stdout, done.stderr)
    out = done.stdout + done.stderr
    assert HEAD in out
    for word in (*PLANTED, AUDIT, str(planted.sets), str(planted.repo), ".md", ".yaml", "/"):
        assert word not in out, word
    assert not re.search(r"\bq[0-9]{2}\b", out), out


def test_fr1_both_entries_print_the_same_line(planted):
    three_misses(planted)
    for entry in ("cli", "module"):
        assert_line(planted.run(entry=entry), TWO_OUT)


def test_fr1_without_repo_the_current_repository_s_top_level_is_read(planted):
    three_misses(planted)
    assert_line(planted.run(repo=False, cwd=planted.repo / "docs"), TWO_OUT)


# ==== what is outside, what is inside, and who holds it ==============================================================
def test_fr1_not_indexed_without_a_class_is_outside_and_not_embedded_alone_is_inside(planted):
    planted.miss("q05", [FROZEN])
    planted.miss("q07", [QUIET])
    assert_line(planted.run(), f"{HEAD} 2 cited, 1 outside, 1 inside; frozen: 1, quiet: 1")


def test_fr1_the_holder_is_the_namespace_that_takes_the_source_out_else_the_first_that_holds_it(planted):
    planted.miss("q05", [SEALED])
    planted.miss("q07", [TWICE])
    assert_line(planted.run(), f"{HEAD} 2 cited, 1 outside, 1 inside; docs: 1, sealed: 1")


def test_fr1_unmapped_is_inside_untracked_is_outside_and_holders_are_in_name_order(planted):
    planted.miss("q05", [LOOSE])
    planted.miss("q07", [GONE])
    planted.miss("q09", [NEVER])
    planted.miss("q11", [QUIET, OLD_A])
    assert_line(planted.run(),
                f"{HEAD} 5 cited, 3 outside, 2 inside; archive: 1, quiet: 1, unmapped: 1, untracked: 2")


# ==== which citations count ==========================================================================================
def test_fr1_only_the_final_attempt_s_citations_count(planted):
    planted.question("q05", [OLD_A, LIVE])
    planted.row("q05", [attempt(1, "search_again", OLD_A), attempt(2, "answer", GOLD, LIVE)])
    planted.question("q07", [OLD_A, OLD_B])
    planted.row("q07", [attempt(1, "answer", OLD_A), attempt(2, "not_found", OLD_B)])
    planted.question("q09", [OLD_A, LIVE_2])
    planted.row("q09", [attempt(1, "search_again", OLD_A), attempt(2, "search_again", LIVE_2)])
    assert_line(planted.run(), f"{HEAD} 3 cited, 1 outside, 2 inside; archive: 1, docs: 2")


def test_fr1_an_error_last_attempt_falls_back_to_the_last_valid_one(planted):
    planted.question("q05", [OLD_A, OLD_B, LIVE])
    planted.row("q05", [attempt(1, "search_again", OLD_A), attempt(2, "search_again", LIVE),
                        attempt(3, None, OLD_B)])
    assert_line(planted.run(), f"{HEAD} 1 cited, 0 outside, 1 inside; docs: 1")


def test_fr1_a_source_counts_once_a_row_and_again_in_another_row(planted):
    planted.miss("q05", [OLD_A], cites=[OLD_A, OLD_A])
    planted.miss("q07", [OLD_A, LIVE], cites=[OLD_A, LIVE, LIVE])
    assert_line(planted.run(), f"{HEAD} 3 cited, 2 outside, 1 inside; archive: 2, docs: 1")


def test_fr1_an_unmarked_row_and_a_gold_or_other_citation_count_nothing(planted):
    planted.miss("q05", [OLD_A], cites=[LIVE_2, OLD_A])    # gold and an unlisted page are cited beside it
    planted.question("q07", [OLD_B])
    planted.row("q07", [attempt(1, "answer", GOLD, OLD_B)], forbidden_cited=False)
    planted.question("q09", [LIVE])
    planted.row("q09", [attempt(1, "answer", GOLD)], forbidden_cited=False)
    assert_line(planted.run(), f"{HEAD} 1 cited, 1 outside, 0 inside; archive: 1")


def test_fr1_nothing_cited_prints_the_bare_line_and_exits_0(planted):
    planted.question("q05", [OLD_A])
    planted.row("q05", [attempt(1, "answer", GOLD)], forbidden_cited=False)
    planted.row("q07", [attempt(1, "not_found")], forbidden_cited=False)  # unmarked: its question file is not needed
    assert_line(planted.run(), f"{HEAD} 0 cited, 0 outside, 0 inside")


# ==== the refusals: each the only line, exit 1 =======================================================================
def test_fr1_an_audit_without_a_run_folder_is_reach_noaudit(planted):
    three_misses(planted)
    assert_refused(planted.run(audit="memory-audit-26112509"), "REACH-NOAUDIT")


@pytest.mark.parametrize("holds", ["no-reader-folder", "an-empty-reader-folder", "the-plan-and-no-row"])
def test_fr1_a_run_without_a_judged_row_is_reach_norows(planted, holds):
    planted.question("q05", [OLD_A])
    planted.run_dir.mkdir(parents=True)
    if holds != "no-reader-folder":
        (planted.run_dir / "reader").mkdir()
    if holds == "the-plan-and-no-row":
        planted.write(planted.run_dir / "reader", "plan.json",
                      json.dumps({"ids": ["q05"], "apart": [], "projection": 0.5}))
        planted.write(planted.run_dir / "reader", "gov.err", "")
    assert_refused(planted.run(), "REACH-NOROWS")


NOSET = ["the-question-file-is-missing", "the-question-file-is-unreadable", "the-question-names-no-forbidden-list",
         "the-citations-and-the-list-share-no-path"]


@pytest.mark.parametrize("fault", NOSET)
def test_fr1_a_marked_row_the_set_cannot_explain_is_reach_noset_and_no_count(planted, fault):
    planted.miss("q05", [OLD_A])  # a sound row beside it: no partial count is printed
    planted.row("q07", [attempt(1, "answer", GOLD, OLD_B)])
    if fault == "the-question-file-is-unreadable":
        planted.write(planted.hidden, "q07.yaml", f"question: [{ASKED_WORD}\n  : : {OLD_B}\n")
    elif fault == "the-question-names-no-forbidden-list":
        planted.question("q07", None)
    elif fault == "the-citations-and-the-list-share-no-path":
        planted.question("q07", [LIVE])
    assert_refused(planted.run(), "REACH-NOSET")


# ==== nothing is written =============================================================================================
@pytest.mark.parametrize("outcome", ["counted", "nothing-cited", "no-audit", "no-rows", "no-set"])
def test_fr1_nothing_is_written(planted, outcome):
    if outcome == "counted":
        three_misses(planted)
    elif outcome == "nothing-cited":
        planted.row("q05", [attempt(1, "answer", GOLD)], forbidden_cited=False)
    elif outcome == "no-rows":
        planted.run_dir.mkdir(parents=True)
    elif outcome == "no-set":
        planted.row("q05", [attempt(1, "answer", OLD_A)])
    before = planted.snapshot()
    done = planted.run()
    first = {"counted": TWO_OUT, "nothing-cited": f"{HEAD} 0 cited, 0 outside, 0 inside", "no-audit": "REACH-NOAUDIT",
             "no-rows": "REACH-NOROWS", "no-set": "REACH-NOSET"}[outcome]
    assert done.stdout.splitlines() == [first], (done.returncode, done.stdout, done.stderr)
    assert done.returncode == (0 if outcome in ("counted", "nothing-cited") else 1)
    assert planted.snapshot() == before
