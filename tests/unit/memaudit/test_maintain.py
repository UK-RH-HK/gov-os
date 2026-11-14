"""W2-187 I10 (S10, F6): the weekly maintenance pass on a planted repository, a planted integration store and a stub ``gov``
(never the real ``gov rebuild``, a real search or the real sets root)."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from gov.memaudit import declare, maintain, schedule, standing
from gov.memaudit.common import UsageError
from gov.store import layout as store_layout

from .conftest import SRC, git_env, run

NOW = "2026-11-16T21:00:00Z"
WEEK = "2026-W47"
STUB = '''#!%(python)s
import json, os, sqlite3, subprocess, sys
sys.path.insert(0, %(src)r)
here = os.path.dirname(os.path.realpath(__file__))
plan = json.load(open(os.path.join(here, "plan.json")))
args = sys.argv[1:]
with open(os.path.join(here, "calls.jsonl"), "a") as f:
    f.write(json.dumps({"argv": args, "cwd": os.getcwd()}) + "\\n")
if args[:2] == ["rebuild", "--integration"]:
    mode = plan.get("rebuild", "advance")
    if "fail" in mode:
        sys.exit(1)
    if "advance" in mode:
        subprocess.run(["git", "-C", plan["link"], "checkout", "-q", "--detach", args[2]], check=True)
    if "restamp" in mode:
        from gov.store import layout
        conn = sqlite3.connect(os.path.join(plan["link"], ".gov-runtime/store.db"))
        layout.stamp(conn)
        conn.close()
    sys.exit(0)
if args[:1] == ["links"]:
    k = plan.get("links_new", 0)
    if plan.get("links_exit") == 2:
        sys.exit(2)
    print(json.dumps({"ok": True, "result": {"new": k}}))
    sys.exit(1 if k else 0)
sys.exit(2)
'''
BEFORE = ["l1", "l2", "l3", "l4", "l5", "l6"]
AFTER = ["pre1", "pre2", "l1", "X2", "X3", "l4", "l5", "l6"]  # l2 and l3 changed; l5 and l6 moved down unchanged
PATH_MAP = """\
namespaces:
  secret:
    paths: ["docs/secret/**"]
    lexical_policy: not indexed
"""


class World:
    """A repository with four commits on main, the integration store's link at the first, a stub ``gov``, the sets root
    of the ``plant`` fixture and the runs folder named by ``GOV_INDEP_RUNS_DIR``."""

    def __init__(self, plant, monkeypatch, behind=3):
        self.plant, self.tmp = plant, plant.tmp
        monkeypatch.setenv("GOV_INDEP_RUNS_DIR", str(plant.runs))
        monkeypatch.setenv("GOV_MEMAUDIT_NOW", NOW)
        monkeypatch.setenv("GOV_ROLE", "orchestrator")
        monkeypatch.delenv("GOV_MEMAUDIT_STATE", raising=False)
        self.env = git_env(plant.tmp)
        self.repo = plant.tmp / "adopted"
        run("git", "init", "-q", "-b", "main", str(self.repo), env=self.env)
        self.write("a.md", "a\n")
        self.write("b.md", "b\n")
        self.write("c.md", "c\n")
        self.write("docs/secret/x.md", "secret\n")
        self.write("docs/x.md", "".join(x + "\n" for x in BEFORE))
        self.write("governance/project/path-map.yaml", PATH_MAP)
        self.write("governance/project/retrieval.yaml", "pool:\n  meaning_uncut: true\n")
        self.first = self.commit("one")
        self.write("docs/x.md", "".join(x + "\n" for x in AFTER))
        self.commit("two")
        self.write("a.md", "a2\n")
        self.commit("three")
        self.write("b.md", "b2\n")
        self.head = self.commit("four")
        self.link = plant.tmp / "link"
        run("git", "clone", "-q", str(self.repo), str(self.link), env=self.env)
        run("git", "checkout", "-q", "--detach", self.first if behind else self.head, cwd=self.link, env=self.env)
        self.store(stamped=True, indexed=("a.md", "docs/x.md", "governance/project/path-map.yaml",
                                          "governance/project/retrieval.yaml"))
        self.bin = plant.tmp / "stubbin"
        self.bin.mkdir()
        self.gov = self.bin / "gov"
        self.gov.write_text(STUB % {"python": sys.executable, "src": SRC}, encoding="utf-8")
        self.gov.chmod(0o755)
        self.plan(link=str(self.link))
        self.state = schedule.state_dir(plant.runs, self.repo)

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, msg):
        run("git", "add", "-A", cwd=self.repo, env=self.env)
        run("git", "commit", "-q", "-m", msg, cwd=self.repo, env=self.env)
        return run("git", "rev-parse", "HEAD", cwd=self.repo, env=self.env).stdout.strip()

    def store(self, *, stamped, indexed):
        db = self.link / ".gov-runtime" / "store.db"
        db.parent.mkdir(exist_ok=True)
        db.unlink(missing_ok=True)
        conn = sqlite3.connect(db)
        conn.execute("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, path TEXT)")
        conn.executemany("INSERT INTO lexical_chunk (path) VALUES (?)", [(p,) for p in indexed])
        conn.execute(f"CREATE TABLE {store_layout.STAMP_TABLE} (version INTEGER NOT NULL)")
        conn.execute(f"INSERT INTO {store_layout.STAMP_TABLE} VALUES (?)",
                     (store_layout.LAYOUT_VERSION if stamped else store_layout.LAYOUT_VERSION - 1,))
        conn.commit()
        conn.close()

    def plan(self, **more):
        path = self.bin / "plan.json"
        doc = json.loads(path.read_text()) if path.exists() else {}
        doc.update(more)
        path.write_text(json.dumps(doc))

    def calls(self):
        log = self.bin / "calls.jsonl"
        return [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []

    def question(self, qid, lines, question):
        folder = self.plant.root / "fixtures/evaluation/memory-verdict-2/hidden"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{qid}.yaml").write_text(yaml.safe_dump(
            {"id": qid, "question": question, "gold_answer": "the gold", "category": "decision", "commit": self.first,
             "sources": [{"path": "docs/x.md", "lines": lines}]}, sort_keys=False), encoding="utf-8")

    def maintain(self, gov=None):
        said = []
        word = maintain.run(str(self.plant.root), repo=self.repo, link=str(self.link),
                            gov=str(gov or self.gov), emit=said.append)
        assert word == "ok" and len(said) == 1
        return said[0]

    def lines(self):
        path = self.state / "MAINTAIN.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []


@pytest.fixture
def world(plant, monkeypatch):
    return World(plant, monkeypatch)


def test_a_store_three_commits_behind_is_refreshed_once_and_the_head_printed(world):
    line = world.maintain()
    rebuilds = [c for c in world.calls() if c["argv"][:2] == ["rebuild", "--integration"]]
    assert len(rebuilds) == 1 and rebuilds[0]["argv"][2] == "main"
    assert line.startswith(f"MAINTAIN 1 store refreshed {world.head[:12]} 2 layout current 3 links 0 ")
    assert schedule.head_of(world.link) == world.head


def test_a_store_already_at_the_head_is_not_refreshed(plant, monkeypatch):
    world = World(plant, monkeypatch, behind=False)
    line = world.maintain()
    assert [c for c in world.calls() if c["argv"][0] == "rebuild"] == []
    assert f"1 store current {world.head[:12]} 2 layout current" in line


def test_a_failing_rebuild_keeps_the_old_store_and_names_the_failure(world):
    world.plan(rebuild="fail")
    line = world.maintain()
    assert f"1 store kept {world.first[:12]} (refresh exit 1) 2 layout current" in line
    assert schedule.head_of(world.link) == world.first
    assert len([c for c in world.calls() if c["argv"][0] == "rebuild"]) == 1  # one refresh, never a retry


def test_a_stale_layout_at_the_main_lines_head_gets_one_rebuild_by_the_same_command_else_stale_kept(plant, monkeypatch):
    world = World(plant, monkeypatch, behind=False)  # G6: the head is current, the layout is not
    world.store(stamped=False, indexed=())
    world.plan(rebuild="restamp")
    line = world.maintain()
    rebuilds = [c["argv"] for c in world.calls() if c["argv"][0] == "rebuild"]
    assert rebuilds == [["rebuild", "--integration", "main"]]
    assert f"1 store current {world.head[:12]} 2 layout rebuilt " in line
    world.store(stamped=False, indexed=())
    world.plan(rebuild="none")
    assert "2 layout stale kept " in world.maintain()
    assert len([c for c in world.calls() if c["argv"][0] == "rebuild"]) == 2  # one more, not a loop


def test_the_links_count_runs_from_the_last_passes_commit_and_a_refusal_is_none(world):
    world.plan(links_new=3)
    assert " 3 links 3 " in world.maintain()
    assert world.calls()[-1]["argv"] == ["links", "--json"]  # a first pass: from the mark, no --since
    world.plan(links_new=0, links_exit=2)
    assert " 3 links none " in world.maintain()
    assert [c["argv"] for c in world.calls() if c["argv"][0] == "links"][-1] == ["links", "--since", world.head, "--json"]


def test_the_unindexed_paths_are_counted_less_those_the_path_map_keeps_out(world):
    # tracked: a, b, c, docs/secret/x (kept out), docs/x, the path map, retrieval.yaml; the store holds chunks of four
    assert " 4 unindexed 2 " in world.maintain()


def write_rows(folder, rows):
    (folder / "reader").mkdir(parents=True)
    for i, row in enumerate(rows):
        (folder / "reader" / f"q{i:02d}.json").write_text(json.dumps(row))
    (folder / "reader" / "plan.json").write_text(json.dumps({"ids": []}))


def test_the_readers_not_found_answers_and_second_searches_are_counted_from_both_runs(world):
    root = world.plant.root
    standing.append(world.state, "STANDING.jsonl", {"event": "declared", "set": "memory-standing-20261111"})
    write_rows(root / "runs/memory-standing-20261111/2026-W46", [{"final_verdict": "not_found", "searches": [{}]}] * 9)
    write_rows(root / "runs/memory-standing-20261111/2026-W47",
               [{"final_verdict": "not_found", "searches": []}, {"final_verdict": "answer", "searches": [{}]},
                {"final_verdict": "answer", "searches": []}])
    write_rows(root / "runs/memory-audit-20261101", [{"final_verdict": "answer", "searches": [{}, {}]}] * 2
               + [{"final_verdict": "not_found", "searches": []}])
    # the latest week and the latest fresh run only: 1 + 1 not found; 1 + 2 with a second search
    assert " 5 not_found 2 second 3 " in world.maintain()


def test_one_changed_cited_block_is_listed_by_id_and_entry_a_moved_unchanged_one_is_not(world):
    root = world.plant.root
    world.question("q1", [2, 3], "zephyrquokka changed?")
    world.question("q2", [5, 6], "narwhalfjord moved?")
    line = world.maintain()
    assert line.endswith(" 6 reanchor 1")
    file = root / "runs/memory-verdict-2" / f"REANCHOR-{WEEK}.json"
    assert json.loads(file.read_text()) == {"week": WEEK, "audit_commit": world.head, "set": "memory-verdict-2",
                                            "changed": [{"id": "q1", "entry": 1}], "count": 1}
    assert stat.S_IMODE(file.stat().st_mode) == 0o600 and stat.S_IMODE(file.parent.stat().st_mode) == 0o700
    text = file.read_text() + line + (world.lines()[-1]["line"])
    for needle in ("zephyrquokka", "narwhalfjord", "the gold", "docs/x.md", "l2"):
        assert needle not in text
    assert len(list(root.glob("runs/*/REANCHOR-*.json"))) == 1


def test_a_standing_set_is_left_out_of_the_reanchor_list(world):
    root = world.plant.root
    for name in ("memory-standing-20261111",):
        folder = root / "fixtures/evaluation" / name / "hidden"
        folder.mkdir(parents=True)
        (folder / "q1.yaml").write_text(yaml.safe_dump(
            {"id": "q1", "question": "whale?", "gold_answer": "g", "category": "decision", "commit": world.first,
             "sources": [{"path": "docs/x.md", "lines": [2, 3]}]}), encoding="utf-8")
        p = {"map": root / "governance/project/path-map.yaml"}
        code, text = declare.plan_map(p, name)
        assert code is None
        declare.write_map(p, text)
    world.question("q1", [2, 3], "zephyrquokka changed?")
    assert world.maintain().endswith(" 6 reanchor 1")  # memory-verdict-2's only
    assert not (root / "runs/memory-standing-20261111").exists()


def test_the_audit_runs_whatever_the_pass_finds_and_it_never_exits_other_than_0(world, tmp_path):
    said = []
    assert maintain.run(str(world.plant.root), repo=world.repo, link=str(world.link), gov=str(tmp_path / "no-gov"),
                        emit=said.append) == "ok"
    assert "1 store kept " in said[0] and "(refresh exit 127)" in said[0] and " 3 links none " in said[0]
    # an unreadable store is named in its word, not raised
    (world.link / ".gov-runtime/store.db").write_text("not a database")
    said = []
    assert maintain.run(str(world.plant.root), repo=world.repo, link=str(world.link), gov=str(world.gov),
                        emit=said.append) == "ok" and said[0].startswith("MAINTAIN 1 store ")


def test_the_pass_changes_neither_the_retrieval_yaml_nor_the_path_map_and_writes_its_line(world):
    names = ("governance/project/retrieval.yaml", "governance/project/path-map.yaml")
    before = [hashlib.sha256((world.repo / n).read_bytes()).hexdigest() for n in names]
    world.maintain()
    assert [hashlib.sha256((world.repo / n).read_bytes()).hexdigest() for n in names] == before
    row = world.lines()[-1]
    assert row["week"] == WEEK and row["commit"] == world.head and row["store"].startswith("refreshed ")
    assert row["sha256"]["retrieval_yaml"] == {"before": before[0], "after": before[0]}
    assert row["sha256"]["path_map"] == {"before": before[1], "after": before[1]}
    assert row["line"].startswith("MAINTAIN 1 store ")
    assert standing.latest_maintain(world.state) == row["line"]


def test_the_module_writes_no_cron_table_and_applies_no_act():
    source = Path(maintain.__file__).read_text()
    assert "crontab" not in source and "walls_act" not in source and "write_map" not in source
    assert "write_whole" not in source and "retrieval.yaml" in source  # it reads the digests, it never writes the file


def test_maintain_without_a_sets_root_is_usage_exit_4(plant):
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "maintain"], capture_output=True, text=True,
                          env=plant.env(), cwd=plant.tmp)
    assert done.returncode == 4
    with pytest.raises(UsageError):
        maintain.run(str(plant.tmp / "absent"), repo=plant.tmp, link="x", gov="y", emit=print)
