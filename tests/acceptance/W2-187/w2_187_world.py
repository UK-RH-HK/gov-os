"""W2-187's planted world: W2-172's world (its repository, store link, sets root, runs folder, launch stub, gate, crontab,
interpreter shim and file-access spy) with a standing set of 80 added, a planted ``gov`` that also answers ``rebuild`` and
``links`` and puts ``result.store.commit`` on each search answer, and the planting of the audit's state per repository.

Everything is under pytest's ``tmp_path``. The tool is only ever run as ``python3 -m gov.memaudit ...`` and the cron wrapper
in child processes with this tree's ``src/`` first on ``PYTHONPATH`` (``W172_SRC`` may name another tree's ``src/``, used to
show the suite sound; unset otherwise). The new modules (``gov.memaudit.standing`` and ``maintain``) are never imported.

The standing set ``memory-standing-20261101``: ``hidden/q01..q80.yaml`` in the sets root; ``q80`` is the nonexistent-id
question (scored apart, counted in n); ``q01..q79`` each cite a heading of ``docs/std/s<NN>.md`` (the five planted misses'
files are named for a unique word). Its entry in the sets root's path map is planted, as the set's owner's own record of
it (the Interface does not say who writes it before the pre-flight loads it; see README).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ACCEPT = HERE.parent
sys.path.insert(0, str(ACCEPT / "W2-172"))

import w2_172_git as G172  # noqa: E402
import w2_172_world as W172  # noqa: E402
from w2_172_world import S171, W171, iso, parse_iso  # noqa: E402

TREE, SRC, WRAPPER = W172.TREE, W172.SRC, W172.WRAPPER
NOW = W172.NOW                                   # 2026-11-10T12:00:00Z, a Tuesday, ISO week 2026-W46
MONDAY = "2026-11-16T12:00:00Z"                  # the next Monday (ISO 2026-W47)
STD = "memory-standing-20261101"
N_SET = 80
APART = "q80"
ASK_ID = "DEC-9998"
CATS = [c for c in W171.CATEGORIES if c != "nonexistent-id"]
MISS_IDS = ("q03", "q19", "q25", "q28", "q33")  # the five planted misses of the scenario ``five``
QWORDS = ("zephyrnook", "tumbleweft", "ostrichlumen", "pewterscone", "marlinfathom")
GWORDS = ("brindlecask", "fennelwrask", "gantrywhist", "osierplume", "cobaltreef")
PWORDS = ("harrowmuster", "juniperdrake", "kestrelvault", "lanternspur", "mulberrygate")
AWORDS = ("nettlefjord", "oxbowsparrow", "puddlegrate", "quillmantle", "russetwharf")
CWORDS = ("rookerywhin", "saffronbolt", "thistlevane", "umberlatch", "vellumknack")
PLANTED = {qid: {"q": QWORDS[i], "g": GWORDS[i], "p": PWORDS[i], "a": AWORDS[i], "c": CWORDS[i]}
           for i, qid in enumerate(MISS_IDS)}
UNIQUE = [w for words in (QWORDS, GWORDS, PWORDS, AWORDS, CWORDS) for w in words]
WRITER_SHA, CHECKER_SHA = hashlib.sha256(b"the writer brief").hexdigest(), hashlib.sha256(b"the checker brief").hexdigest()


def week_of(now: str) -> str:
    year, week, _ = date.fromisoformat(now[:10]).isocalendar()
    return f"{year}-W{week:02d}"


def std_path(k: int) -> str:
    qid = f"q{k:02d}"
    return f"docs/std/{PLANTED[qid]['p']}.md" if qid in PLANTED else f"docs/std/s{k:02d}.md"


def std_question(k: int, commit: str) -> dict:
    qid = f"q{k:02d}"
    if k == N_SET:
        return {"id": qid, "question": f"What does decision {ASK_ID} decide?",
                "gold_answer": "None: the register's next free id is below it.",
                "sources": [{"path": "docs/DECISION_REGISTER.md", "heading": "Next free id: DEC-200", "lines": [3, 3]}],
                "commit": commit, "category": "nonexistent-id", "drawn": "none"}
    path, planted = std_path(k), PLANTED.get(qid)
    question = (f"Which {planted['q']} rule applies to standing item {k}?" if planted
                else f"Where is the rule of standing item {k} stated?")
    gold = f"The {planted['g']} rule applies." if planted else f"It is stated in the standing file of item {k}."
    return {"id": qid, "question": question, "gold_answer": gold,
            "sources": [{"path": path, "heading": W171.heading_of(path), "lines": [3, 8]}], "commit": commit,
            "category": CATS[(k - 1) % len(CATS)], "drawn": "sample"}


def write_std_set(hidden: Path, commit: str, count: int = N_SET) -> None:
    hidden.mkdir(parents=True, exist_ok=True)
    for k in range(1, count + 1):
        (hidden / f"q{k:02d}.yaml").write_text(yaml.safe_dump(std_question(k, commit), sort_keys=False), encoding="utf-8")


def entry_text(name: str) -> str:
    roles = ", ".join(W171.ROLES)
    return f"  {name}:\n    visible: []\n    hidden: [\"fixtures/evaluation/{name}/hidden/**\"]\n    measures:\n      roles: [{roles}]\n"


def add_map_entry(sets: Path, name: str) -> None:
    path = sets / "governance" / "project" / "path-map.yaml"
    text = path.read_text(encoding="utf-8")
    mark = "  # the last comment inside the block\n"
    assert mark in text
    path.write_text(text.replace(mark, entry_text(name) + mark, 1), encoding="utf-8")


# -- the template -------------------------------------------------------------------------------------------------------
def install_x(source: Path, dest: Path, token: str, value: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(f"#!{sys.executable} -S\n" + source.read_text(encoding="utf-8").replace(token, value), encoding="utf-8")
    dest.chmod(0o755)


def build_template(base: Path) -> None:
    original = W171.repo_files

    def with_standing_files():
        files = original()
        for k in range(1, N_SET):
            files[std_path(k)] = W171.file_text(std_path(k))
        return files

    W171.repo_files = with_standing_files
    try:
        W172.build_template(base)
    finally:
        W171.repo_files = original
    meta = json.loads((base / "world.json").read_text())
    write_std_set(base / "sets" / "fixtures" / "evaluation" / STD / "hidden", meta["audit_commit"])
    add_map_entry(base / "sets", STD)
    fake = str(W171.HERE / "fake_gov.py")
    for pin in (W171.PIN, W171.OTHER_PIN, "plain"):
        install_x(HERE / "fake_gov_x.py", base / "pins" / pin / "gov", "@FAKE@", fake)
    install_x(HERE / "py_shim187.py", base / "bin" / "py_shim187", "@REAL@", sys.executable)
    spy = base / "spy" / "sitecustomize.py"  # W2-172's file-access spy, then W2-187's function spy (one sitecustomize)
    spy.write_text(spy.read_text(encoding="utf-8") + "\n\n" + (HERE / "fn_spy.py").read_text(encoding="utf-8"),
                   encoding="utf-8")


# -- the scenario of the standing set -----------------------------------------------------------------------------------
class StdScenario:
    """Ranks, verdicts and costs for the 80 questions, and the oracle (written from the Interface and W2-171's pinned
    ``outcome``, independently of the tool). ``live`` names the questions whose anchors resolve (the rest are dropped)."""

    def __init__(self, behaviour=None, ranks=None, routes=None, later_fail=(), disagree=(), live=None):
        self.behaviour = {f"q{i:02d}": "A1" for i in range(1, N_SET)}
        self.behaviour[APART] = "NF"
        self.behaviour.update(behaviour or {})
        self.ranks = {f"q{i:02d}": S171.CYCLE[(i - 1) % 13] for i in range(1, N_SET)}
        self.ranks[APART] = None
        self.ranks.update(ranks or {})
        self.routes = dict(routes or {})
        self.later_fail, self.disagree = set(later_fail), set(disagree)
        self.live = set(live) if live is not None else set(self.behaviour)

    def row(self, qid: str) -> dict:
        verdict, attempts, answered_at, grade, cite = S171.BEHAVIOURS[self.behaviour[qid]]
        check = None if grade is None else (grade if qid not in self.disagree else ("wrong" if grade == "correct" else "correct"))
        return {"id": qid, "final_verdict": verdict, "attempts": attempts, "answered_at": answered_at, "grade": grade,
                "check": check, "citation_right": cite, "apart": qid == APART}

    def ids(self) -> list[str]:
        return sorted(self.live)

    def outcomes(self, cut: int) -> dict:
        return {q: S171.outcome(self.row(q), cut) for q in self.ids()}

    # -- the plans of the planted programs
    def answer(self, qid: str) -> str:
        return f"The {PLANTED[qid]['a']} answer for {qid}." if qid in PLANTED else f"Answer for {qid}."

    def claude_spec(self, qid: str, gold: list) -> dict:
        cite = [{"path": gold[0], "start_line": gold[1], "end_line": min(gold[2], gold[1] + 3)}]
        other = [{"path": f"docs/plan/{PLANTED[qid]['c']}.md" if qid in PLANTED else "docs/plan/p90.md", "start_line": 3,
                  "end_line": 6}]
        beh = self.behaviour[qid]
        sa = {"verdict": "search_again", "answer": "", "citations": [], "search": S171.search_words(qid)}
        ans = {"verdict": "answer", "answer": self.answer(qid), "citations": other if beh == "A1_cite" else cite, "search": ""}
        nf = {"verdict": "not_found", "answer": "", "citations": [], "search": ""}
        reader = {"A1": [ans], "A2": [sa, ans], "A3": [sa, sa, ans], "A1_wrong": [ans], "A1_cite": [ans], "A1_gradenf": [ans],
                  "NF": [nf], "CAP": [sa, sa, sa], "EMPTY2": ["empty", "empty"]}[beh]
        r = self.row(qid)
        spec = {"id": qid, "reader": reader}
        if r["grade"] is not None:
            spec["grader"], spec["check"] = [r["grade"]], [r["check"]]
        return spec

    def install(self, world: "SW", *, other_commit: dict | None = None) -> None:
        docs = world.std_docs()
        gov, claude = {W171.PROBE: {"calls": [["d"] * 10]}}, {}
        for k in range(1, W171.CONTROL_N + 1):
            gov[W171.control_text(k)] = {"gold": [[f"docs/ctl/c{k:02d}.md", 1, 3]], "calls": S171.calls_for(1 if k <= 34 else None)}
        for qid, doc in docs.items():
            src = doc["sources"][0]
            gold = [src["path"], *(src.get("lines") or [1, 3])]
            if qid == APART:
                gov[doc["question"]] = {"fault": "unresolved"}
            else:
                gov[doc["question"]] = {"gold": [gold], "calls": S171.calls_for(self.ranks[qid], self.routes.get(
                    qid, ("lexical", "semantic")))}
            if qid in self.live:
                claude[doc["question"]] = self.claude_spec(qid, gold)
            gov[S171.search_words(qid)] = {"gold": [gold], "calls": S171.calls_for(1)}
            if qid in self.later_fail and qid in self.live:
                gov[S171.search_words(qid)]["fault"] = "rerank"
        world.write_plans(gov, claude, cost={"reader": 0.10, "grader": 0.02, "check": 0.01})
        world.write_x_plan(store_commit=world.link_head(), other_commit=dict(other_commit or {}))


class StdExpected:
    """What the tool must print and write for ``sc`` (n = the live questions)."""

    def __init__(self, sc: StdScenario, n_set: int = N_SET):
        self.sc, self.n_set = sc, n_set
        self.ids = sc.ids()
        self.n = len(self.ids)
        self.main = [q for q in self.ids if q != APART]
        o2 = sc.outcomes(2)
        self.right, self.wrong = sum(x["right"] for x in o2.values()), sum(x["wrong"] for x in o2.values())
        self.nf = sum(x["nf"] for x in o2.values())
        self.pct = 100 * self.right / self.n
        self.a1 = sum(x["right"] for x in sc.outcomes(1).values())
        self.gains, self.losses, self.p = S171.mcnemar([x["right"] for x in sc.outcomes(1).values()],
                                                      [x["right"] for x in o2.values()])
        self.hit5 = sum(1 for q in self.main if (sc.ranks[q] or 99) <= 5)
        self.in_bundle = sum(1 for q in self.main if (sc.ranks[q] or 99) <= 10)
        self.by_outcome = {"wrong": 0, "incomplete": 0, "not_found": 0}
        self.by_rank = {"rank_1_5": 0, "rank_6_20": 0, "not_in_20": 0}
        for q in self.ids:
            if o2[q]["right"]:
                continue
            row = sc.row(q)
            kind = "not_found" if o2[q]["nf"] or row["grade"] == "not_found" else (
                "incomplete" if o2[q]["correct"] and not o2[q]["right"] else "wrong")
            self.by_outcome[kind] += 1
            r = sc.ranks[q]
            self.by_rank["rank_1_5" if r and r <= 5 else "rank_6_20" if r and r <= 20 else "not_in_20"] += 1
        self.misses = sum(self.by_outcome.values())
        self.need = -(-95 * self.n // 100)
        self.passes = self.right >= self.need and self.wrong <= 5 * self.n // 100


def scenario(name: str) -> StdScenario:
    five = dict(behaviour={"q03": "A1_wrong", "q19": "A1_cite", "q25": "NF", "q28": "A1_gradenf", "q33": "CAP"},
                ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14, "q33": 25},
                routes={"q19": ["lexical"], "q28": ["semantic"], "q33": ["graph"]})
    a2 = {"q10": "A2", "q20": "A2", "q30": "A2"}
    if name == "pass":      # 80 right: three needed a second search, the second search of q10 comes from another store
        return StdScenario(behaviour=a2, later_fail=())
    if name == "pass76":    # four misses: right = need_right (76), passes
        beh = {k: v for k, v in five["behaviour"].items() if k != "q33"}
        return StdScenario(behaviour=beh, ranks=five["ranks"], routes=five["routes"])
    if name == "five":      # five misses with the unique words: right 75 = need_right - 1, a miss
        return StdScenario(**five)
    raise KeyError(name)


def live_without(broken: list[str]) -> set:
    return {f"q{i:02d}" for i in range(1, N_SET + 1)} - set(broken)


def register_fresh_scenarios() -> None:
    """Fresh 40-question scenarios whose right-end-to-end per cent is 90.0, 92.5 and 97.5 (clean: 100.0)."""
    base = dict(ranks={"q03": 3, "q19": 8, "q25": None, "q28": 14}, routes={"q19": ["lexical"], "q28": ["semantic"]})
    miss = {"q03": "A1_wrong", "q19": "A1_cite", "q25": "NF", "q28": "A1_gradenf"}
    for name, ids in (("w187_miss4", ["q03", "q19", "q25", "q28"]), ("w187_miss3", ["q03", "q19", "q25"]),
                      ("w187_miss1", ["q03"])):
        S171.SCENARIOS.setdefault(name, S171.Scenario(name, behaviour={k: miss[k] for k in ids}, **base))


register_fresh_scenarios()
FRESH_PCT = {"w187_miss4": 90.0, "w187_miss3": 92.5, "w187_miss1": 97.5, "clean": 100.0}


# -- the world ------------------------------------------------------------------------------------------------------------
def tree_state(*roots: Path) -> dict:
    """Every file under the roots (its bytes' sha256 and mode) and every folder (its mode): equal means byte-identical."""
    found = {}
    for root in roots:
        root = Path(root)
        if not root.exists():
            continue
        for folder, dirs, names in os.walk(root):
            for name in names:
                path = Path(folder) / name
                found[str(path)] = ("link", os.readlink(path)) if path.is_symlink() else (
                    W171.sha_file(path), path.stat().st_mode)
            for d in dirs:
                found[str(Path(folder) / d) + "/"] = ("dir", (Path(folder) / d).stat().st_mode)
    return found


def hits(text: str, words) -> list[str]:
    return [w for w in words if w in text]


class SW(W172.World):
    """One test's copy of the template, with the standing set and its state."""

    def __init__(self, base: Path, now: str = NOW):
        super().__init__(base, now)
        if not (self.state / "x_plan.json").exists():
            self.write_x_plan(store_commit=self.audit_commit)

    def set_now(self, now: str | None) -> None:
        super().set_now(now)
        self.week = week_of(now) if now else None
        self.std_set_dir = self.sets / "fixtures" / "evaluation" / STD
        self.std_hidden = self.std_set_dir / "hidden"
        self.std_runs = self.sets / "runs" / STD
        if self.week:
            self.std_week = self.std_runs / self.week
            self.std_state = self.mem / "standing" / STD / self.week

    # -- plans and the link
    def write_x_plan(self, **kw) -> None:
        self.state.mkdir(exist_ok=True)
        path = self.state / "x_plan.json"
        doc = json.loads(path.read_text()) if path.exists() else {}
        doc.update(kw)
        path.write_text(json.dumps(doc), encoding="utf-8")

    def link_head(self) -> str:
        return W171.git(self.link, "rev-parse", "HEAD", home=self.home).strip()

    def repo_commit(self, date_: str, files: dict | None = None, message: str = "c") -> str:
        for rel, text in (files or {}).items():
            W171._write(self.repo, rel, text)
        self.repo_git("add", "-A", date=date_)
        self.repo_git("commit", "-q", "--allow-empty", "-m", message, date=date_)
        return self.repo_git("rev-parse", "HEAD", date=date_).strip()

    def relink(self, commit: str) -> None:
        self.make_link(commit, head=commit)
        self.write_x_plan(store_commit=commit)

    def plant_repo_store(self, head: str) -> Path:
        """The repository's own ``.gov-runtime/store.db`` (the template's store, its fingerprints head set to ``head``),
        kept out of git by ``.git/info/exclude`` as a real repository keeps ``.gov-runtime/`` out (review round 1's F-A)."""
        folder = self.repo / ".gov-runtime"
        folder.mkdir(exist_ok=True)
        shutil.copy(self.store, folder / "store.db")
        con = sqlite3.connect(folder / "store.db")
        con.execute("UPDATE fingerprints SET head = ?", (head,))
        con.commit()
        con.close()
        exclude = self.repo / ".git" / "info" / "exclude"
        exclude.parent.mkdir(parents=True, exist_ok=True)
        text = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
        if ".gov-runtime/" not in text.splitlines():
            exclude.write_text(text + ".gov-runtime/\n", encoding="utf-8")
        return folder / "store.db"

    def search_roots(self, *steps: str) -> list[tuple[str | None, str]]:
        """``(step, root)`` of each logged search, ``steps`` keeping only those steps' (all when none are given)."""
        return [(c.get("step"), c.get("root")) for c in self.searches() if not steps or c.get("step") in steps]

    # -- the standing set
    def std_docs(self) -> dict:
        return {p.stem: yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(self.std_hidden.glob("*.yaml"))}

    def std_digest(self) -> str:
        return W171.set_digest(self.std_hidden)

    def break_anchors(self, ids) -> None:
        """Questions whose cited file is gone at the audit commit (their anchors cannot resolve)."""
        for qid in ids:
            path = self.std_hidden / f"{qid}.yaml"
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
            doc["sources"] = [{"path": f"docs/std/gone-{qid}.md", "heading": "## Section gone", "lines": [3, 8]}]
            path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    def standing_record(self, name: str = STD, **over) -> dict:
        line = {"event": "declared", "set": name, "set_digest": W171.set_digest(self.sets / "fixtures" / "evaluation" / name / "hidden"),
                "n": N_SET, "n_apart": 1, "writer_brief_sha256": WRITER_SHA, "checker_brief_sha256": CHECKER_SHA,
                "written_commit": self.base_commit, "wave0": False, "at": "2026-11-02T10:00:00Z"}
        line.update(over)
        return line

    def plant_standing(self, *lines: dict) -> None:
        """STANDING.jsonl: the live standing set's record (or the lines given)."""
        self.mem.mkdir(parents=True, exist_ok=True)
        rows = lines or (self.standing_record(),)
        (self.mem / "STANDING.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")

    def standing_lines(self) -> list[dict]:
        return self.jsonl_file(self.mem / "STANDING.jsonl")

    def digests_now(self) -> dict:
        def sha(rel):
            path = self.repo / rel
            return W171.sha_file(path) if path.exists() else None
        return {"retrieval_yaml_sha256": sha("governance/project/retrieval.yaml"),
                "path_map_sha256": sha("governance/project/path-map.yaml")}

    def std_line(self, week: str, pct: float, *, word: str = "pass", n: int = N_SET, **over) -> dict:
        right = round(pct * n / 100)
        line = {"kind": "standing", "set": STD, "week": week, "audit": STD, "commit": self.audit_commit,
                "at": "2026-11-02T21:00:00Z", "mode": "weekly", "churn": 0.01, "retrieval_28d": False,
                "passes": word == "pass", "pool_regression": False, "measured": True, "used": True, "n": n,
                "right": right, "wrong": 0, "not_found": n - right, "dropped": 0, "pct": pct, "word": word,
                "gov_pin": W171.PIN, **self.digests_now(),
                # F15's stamp: a figure without it is never compared, so a planted line carries it
                "release": "0.1.5", "reader_model": "claude-sonnet-5-5", "grader_models": ["claude-sonnet-5-5"],
                "forbidden_rule": "strict", "questions_with_forbidden": 0}
        line.update(over)
        return line

    def plant_briefs(self, name: str = STD, *, runs: Path | None = None, status: str = "delivered", kinds=("writer", "checker"),
                     set_name: str | None = None) -> None:
        """The delivered writer and checker counts, under ``<runs>/indep/<kind>/<run>/counts.json``."""
        root = runs or self.runs_env
        for kind in kinds:
            folder = root / "indep" / kind / f"20261101T000000Z-{kind}-r1"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "counts.json").write_text(json.dumps(
                {"kind": kind, "run": folder.name, "set": set_name or name, "round": 1, "commit": self.base_commit,
                 "brief_sha256": WRITER_SHA if kind == "writer" else CHECKER_SHA, "status": status, "code": 0}),
                encoding="utf-8")

    # -- running
    def std_flags(self, *, gate=None, extra=()) -> list[str]:
        args = ["--sets-root", str(self.sets), "--repo", str(self.repo), "--store-link", str(self.link),
                "--gov", str(self.gov), "--claude", str(self.claude)]
        if gate:
            args += ["--gate-cmd", str(gate)]
        return [*args, *extra]

    def standing_run(self, *, gate=None, extra=(), **kw) -> W171.Run:
        return self.drive("standing", "run", *self.std_flags(gate=gate, extra=extra), **kw)

    def declare_flags(self, name: str = STD, *, runs: Path | None = None, extra=()) -> list[str]:
        return ["--sets-root", str(self.sets), "--set", name, "--repo", str(self.repo),
                "--runs-dir", str(runs or self.runs_env), *extra]

    def standing_declare(self, name: str = STD, *, runs: Path | None = None, extra=(), **kw) -> W171.Run:
        return self.drive("standing", "declare", *self.declare_flags(name, runs=runs, extra=extra), **kw)

    def standing_live(self, **kw) -> W171.Run:
        return self.drive("standing", "live", "--sets-root", str(self.sets), "--repo", str(self.repo), **kw)

    def maintain(self, *, extra=(), **kw) -> W171.Run:
        return self.drive("maintain", "--sets-root", str(self.sets), "--repo", str(self.repo), "--store-link",
                          str(self.link), "--gov", str(self.gov), *extra, **kw)

    def status_repair(self, *extra, **kw) -> W171.Run:
        return self.drive("status", "--sets-root", str(self.sets), "--repo", str(self.repo), "--repair", *extra, **kw)

    def due_fresh(self, **kw) -> W171.Run:
        return self.drive("due", *self.common_flags(), "--store-link", str(self.link), "--fresh", **kw)

    # -- reading
    def std_json(self, name: str, folder: Path | None = None):
        return json.loads(((folder or self.std_week) / name).read_text(encoding="utf-8"))

    def std_digest_lines(self) -> list[str]:
        return (self.std_state / "DIGEST.txt").read_text(encoding="utf-8").splitlines()

    def std_ledger(self) -> list[dict]:
        return self.jsonl_file(self.std_week / "ledger.jsonl")

    def gov_x_calls(self) -> list[dict]:
        return self.jsonl("gov_x_calls.jsonl")

    def searches(self) -> list[dict]:
        return [c for c in self.gov_x_calls() if c["argv"][:1] == ["retrieve"]]

    def history_kind(self, kind: str) -> list[dict]:
        return [x for x in self.history() if x.get("kind") == kind]

    def scan_targets(self, *roots: Path) -> list[Path]:
        return [p for root in roots for p in sorted(Path(root).rglob("*")) if p.is_file()]


def digest_line(lines, word: str) -> str | None:
    return next((x for x in lines if x == word or x.startswith(word + " ")), None)


def parse_maintain(line: str) -> dict:
    import re
    m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                     r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                     r"6 reanchor (?P<reanchor>\d+)", line)
    assert m, f"not the MAINTAIN line of I10: {line!r}"
    return m.groupdict()
