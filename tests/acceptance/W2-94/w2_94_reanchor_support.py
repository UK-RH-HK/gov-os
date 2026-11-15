"""Support code for the W2-94 ``--reanchor`` flow's acceptance cases (S14, S15, their failure line; DEC-1186 (4)).

The program under test is ``governance/project/orchestration/tools/indep_launch.py``, run as a process through W2-149's
fake-session seam (``World``: a planted sets root, HOME and repository with the walls' template and an APPROVED list, a
stub ``claude``), or in-process through ``indep_launch.main(argv)`` for the rename-failure cases. ``ReanchorWorld`` adds:

* the planted template's ``kinds.yaml`` declaring ``input_reanchor`` under the writer kind (or not, or malformed),
  committed and approved (the repository's own ``kinds.yaml`` is not touched);
* a planted ``examin`` set whose hidden half mixes the case of its file names: ``hidden/Q01.yaml``, ``hidden/q02.yaml``,
  ``hidden/q03.yaml`` (never requested), ``hidden/<UID>.yaml`` (a question whose id is itself a unique string),
  ``hidden/visible/q04.yaml``, ``hidden/dropped/q05.yaml``, ``hidden/DRAW.txt``, ``XCHECK-r1.md`` and ``visible/q04.yaml``;
  every text value carries the made-up word ``zqxw94``;
* the weekly request ``<sets root>/runs/examin/REANCHOR-<week>.json`` in the form ``gov.memaudit maintain`` writes.

Nothing under ``~/gov-os-eval``, ``~/gov-os-runs``, ``~/gov-os-wall-trees`` or any real ``hidden`` folder is opened. No
real ``claude``: the stub only.
"""

from __future__ import annotations

import copy
import errno
import hashlib
import json
import os
import stat
import sys
import tarfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
UNIT = ROOT / "tests" / "unit" / "orchestration"
sys.path.insert(0, str(UNIT))

from test_w2_149_indep_launch import (  # noqa: E402  (the fake-session seam; its tests are not imported)
    SCRIPT, WALLS, World, indep_launch, schema)

WORD = "zqxw94"
SETN = "examin"
WEEK = "2026-W46"
UID = "zqxw94uid7k"  # a question id that is itself a unique planted string (its file name too)
CODE = "ANSWER_NOT_IN_SPANS"
DECLARED = "[questions, reanchor]"
REAL_REPLACE = os.replace
DROP = object()  # a key to leave out

# the default request: two rows for q01 (served by Q01.yaml), one for Q02 (served by q02.yaml), one for the unique id,
# one for an id the set does not hold
ROWS = [{"id": "q01", "entry": 2}, {"id": "q01", "entry": 1}, {"id": "Q02", "entry": 2}, {"id": UID, "entry": 1},
        {"id": "q77", "entry": 1}]
STAGED_STEMS = ["Q01", "q02", UID]
EXPECTED_CHANGED = [{"id": "Q01", "entry": 1}, {"id": "Q01", "entry": 2}, {"id": "q02", "entry": 2},
                    {"id": UID, "entry": 1}]
COUNTS_KEYS = ("week", "entries", "ids", "absent", "corrected", "replaced")

# the strings a good delivery writes into the hidden files (hidden content once delivered)
NEW_MARKERS = (f"{WORD}-Q01-heading-a-new", f"src/{WORD}-Q01-path-b1-new.py", f"{WORD}-Q01-heading-b2-new",
               f"{WORD}-q02-heading-b1-new")
SESSION_TEXT = f"{WORD}-session-text"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def m(qid, what):
    return f"{WORD}-{qid}-{what}"


def question(qid, commit, shape):
    """A planted question mapping. ``shape`` lists its sources: "map" (one mapping) or "alts" (two alternatives)."""
    sources = []
    for n, kind in enumerate(shape, start=1):
        if kind == "map":
            sources.append({"path": f"docs/{m(qid, f'path-{n}')}.md", "heading": f"## {m(qid, f'heading-{n}')}",
                            "lines": [3 * n, 3 * n + 6], "note": m(qid, f"note-{n}")})
        else:
            sources.append([{"path": f"src/{m(qid, f'path-{n}1')}.py", "heading": f"# {m(qid, f'heading-{n}1')}",
                             "lines": [1, 4], "role": m(qid, f"role-{n}1")},
                            {"path": f"src/{m(qid, f'path-{n}2')}.py", "lines": [5, 8],
                             "role": m(qid, f"role-{n}2")}])
    return {"id": qid, "question": m(qid, "question-text"), "gold_answer": m(qid, "gold-answer"),
            "category": "location", "commit": commit, "keyword": m(qid, "keyword"), "sources": sources}


def dump(d):
    return yaml.safe_dump(d, sort_keys=False, allow_unicode=True, default_flow_style=False)


SHAPES = {"Q01": ["map", "alts", "map"], "q02": ["map", "alts", "map"], "q03": ["map"], UID: ["map"],
          "q04": ["map"], "q05": ["map"]}


def result_json(**changes):
    r = {"questions": 3, "corrected": 2, "replaced": 1, "by_kind": {"location": 2, "fact": 1},
         "by_area": {"code": 2, "docs": 1}}
    r.update(changes)
    return json.dumps({k: v for k, v in r.items() if v is not DROP})


def snap(top):
    """Every entry below *top*: {relative path: ("f", sha256) | ("d",) | ("l", target)}; nothing followed."""
    out = {}
    top = str(top)
    if not os.path.lexists(top):
        return out
    for folder, dirs, names in os.walk(top):
        rel = os.path.relpath(folder, top)
        for n in dirs + names:
            p = os.path.join(folder, n)
            r = os.path.normpath(os.path.join(rel, n))
            mode = os.lstat(p).st_mode
            if stat.S_ISLNK(mode):
                out[r] = ("l", os.readlink(p))
            elif stat.S_ISDIR(mode):
                out[r] = ("d",)
            else:
                with open(p, "rb") as f:
                    out[r] = ("f", sha(f.read()))
    return out


def set_kinds(text, declare):
    """The template's kinds.yaml with ``input_reanchor: <declare>`` added under the writer kind (after its round-2
    input line, which only the writer has)."""
    i = text.index("    input_round2:")
    j = text.index("\n", i) + 1
    return text[:j] + f"    input_reanchor: {declare}\n" + text[j:]


class ReanchorWorld(World):
    def __init__(self, tmp, declare=DECLARED, rows=None):
        tmp = Path(tmp)
        tmp.mkdir(parents=True, exist_ok=True)
        super().__init__(tmp)
        self.tmp = tmp
        self.procs = []
        if declare is not None:
            rel = f"governance/project/{WALLS}/kinds.yaml"
            text = self.blob(self.commit, rel).decode()
            self.put(rel, set_kinds(text, declare))
            self.commit = self.commit_all("the writer declares input_reanchor")
            self.approve(self.commit)
        self.markers = []
        self.plant_set()
        self.write_request(self.request(rows))

    # -- the planted set -------------------------------------------------------------------------------------------
    @property
    def setdir(self):
        return self.sets / "fixtures" / "evaluation" / SETN

    @property
    def hidden(self):
        return self.setdir / "hidden"

    def _put(self, rel, text):
        p = self.setdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def plant_question(self, rel, qid):
        d = question(qid, self.commit, SHAPES.get(qid, ["map"]))
        self._put(rel, dump(d))
        self._collect(d)
        return d

    def _collect(self, node):
        if isinstance(node, dict):
            for v in node.values():
                self._collect(v)
        elif isinstance(node, list):
            for v in node:
                self._collect(v)
        elif isinstance(node, str) and WORD in node:
            self.markers.append(node)

    def plant_set(self):
        for stem in ("Q01", "q02", "q03", UID):
            self.plant_question(f"hidden/{stem}.yaml", stem)
        self.plant_question("hidden/visible/q04.yaml", "q04")
        self.plant_question("hidden/dropped/q05.yaml", "q05")
        for rel in ("hidden/DRAW.txt", "XCHECK-r1.md", "visible/q04.yaml"):
            mark = f"{WORD}-{rel.replace('/', '-').replace('.', '-')}-mark"
            self._put(rel, f"{mark}\n")
            self.markers.append(mark)
        self.markers.append(UID)

    def staged(self, stem):
        return yaml.safe_load((self.hidden / f"{stem}.yaml").read_text())

    @property
    def all_markers(self):
        return sorted(set(self.markers) | set(NEW_MARKERS) | {SESSION_TEXT})

    @property
    def other_markers(self):
        """The planted strings of the set's files that are never staged."""
        out = []
        for rel in ("hidden/q03.yaml", "hidden/visible/q04.yaml", "hidden/dropped/q05.yaml", "hidden/DRAW.txt",
                    "XCHECK-r1.md", "visible/q04.yaml"):
            text = (self.setdir / rel).read_text()
            out += [s for s in self.markers if s in text]
        return sorted(set(out))

    # -- the request -----------------------------------------------------------------------------------------------
    def request(self, rows=None, **changes):
        rows = copy.deepcopy(ROWS if rows is None else rows)
        r = {"week": WEEK, "audit_commit": self.commit, "set": SETN, "changed": rows, "count": len(rows)}
        r.update(changes)
        return {k: v for k, v in r.items() if v is not DROP}

    @property
    def request_path(self):
        return self.sets / "runs" / SETN / f"REANCHOR-{WEEK}.json"

    def write_request(self, obj):
        p = self.request_path
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.is_symlink() or p.is_file():
            p.unlink()
        data = obj if isinstance(obj, bytes) else (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()
        p.write_bytes(data)
        os.chmod(p, 0o600)

    # -- the runs --------------------------------------------------------------------------------------------------
    def ra_argv(self, *, week=WEEK, kind="writer", rnd=2, set_name=SETN, seed=None, dry=False, commit=None,
                more=()):
        commit = commit or self.commit
        rel = f"governance/project/indep-briefs/{kind}.md"
        a = ["--sets-root", str(self.sets), "--kind", kind, "--brief", rel,
             "--brief-sha256", sha(self.blob(commit, rel)), "--commit", commit, "--set", set_name]
        if rnd is not None:
            a += ["--round", str(rnd)]
        if kind == "auditor":
            a += ["--audit", "e0"]
        if week is not None:
            a += ["--reanchor", week]
        if seed is not None:
            a += ["--seed", str(seed)]
        if dry:
            a.append("--dry")
        return a + list(more)

    def run(self, *args, extra=None):
        rc, counts, p = super().run(*args, extra=extra)
        self.procs.append((p.stdout, p.stderr))
        return rc, counts or {}, p

    def ra(self, extra=None, **kw):
        return self.run(*self.ra_argv(**kw), extra=extra)

    def dry(self, **kw):
        return self.ra(seed=17, dry=True, **kw)

    def session(self, out, hook_lines=None):
        self.stub({"session": "write", "out": out, "marker": SESSION_TEXT})
        if hook_lines is None:
            return None
        body = "if point == 'after_session':\n" + "".join(f"    {ln}\n" for ln in hook_lines)
        return {"GOV_INDEP_TEST_HOOK": self.hook(body)}

    def inproc(self, monkeypatch, capsys, argv, fail_at=None):
        """``indep_launch.main(argv)`` in this process, HOME and PATH planted, the module's ``os.replace`` wrapped:
        the calls whose target lies in the set's hidden folder (or below it) are counted, and the ``fail_at``-th of
        them raises. Returns (rc, counts, the counted targets)."""
        monkeypatch.chdir(self.repo)
        for k in list(os.environ):
            if k.startswith("GOV_"):
                monkeypatch.delenv(k)
        monkeypatch.setenv("HOME", str(self.home))
        monkeypatch.setenv("PATH", f"{self.bin}:{os.environ['PATH']}")
        hidden = os.path.realpath(self.hidden)
        calls = []

        def replace(src, dst, *a, **kw):
            d = os.path.realpath(os.path.dirname(os.path.abspath(os.fspath(dst))))
            if d == hidden or d.startswith(hidden + os.sep):
                calls.append(os.fspath(dst))
                if fail_at is not None and len(calls) == fail_at:
                    raise OSError(errno.EIO, "planted rename failure")
            return REAL_REPLACE(src, dst, *a, **kw)

        monkeypatch.setattr(indep_launch.os, "replace", replace)
        capsys.readouterr()
        try:
            rc = indep_launch.main(list(argv))
        except SystemExit as e:  # the unchanged script's parser may exit
            rc = e.code
        finally:
            monkeypatch.setattr(indep_launch.os, "replace", REAL_REPLACE)
        out = capsys.readouterr()
        self.procs.append((out.out, out.err))
        lines = [x for x in out.out.splitlines() if x.strip()]
        try:
            counts = json.loads(lines[-1]) if lines else {}
        except ValueError:
            counts = {}
        return rc, counts, calls

    # -- what a run builds or changes ------------------------------------------------------------------------------
    def state(self):
        return {"sets": snap(self.sets), "runs": snap(self.home / "gov-os-runs"),
                "trees": snap(self.home / "gov-os-wall-trees")}

    def set_files(self):
        """The sets root less the walls' folder (the runs' archives live there)."""
        return {k: v for k, v in snap(self.sets).items() if k.split(os.sep)[0] != WALLS}

    def tar_path(self, run):
        return self.sets / WALLS / "writer" / f"{run}.tar"

    def tar_members(self, run):
        with tarfile.open(self.tar_path(run)) as t:
            return {n.name: (t.extractfile(n).read() if n.isfile() else None) for n in t.getmembers()}

    def wall_listing(self, wall):
        files, dirs, links = [], [], []
        for folder, ds, names in os.walk(wall):
            for n in ds + names:
                p = os.path.join(folder, n)
                rel = os.path.relpath(p, wall)
                mode = os.lstat(p).st_mode
                (links if stat.S_ISLNK(mode) else dirs if stat.S_ISDIR(mode) else files).append(rel)
        return sorted(files), sorted(dirs), sorted(links)

    # -- F1: the planted strings outside the sets root --------------------------------------------------------------
    def leaks(self):
        """Every (place, marker) where a planted string shows outside the sets root: the runs' stdout and stderr (the
        counts line among them), and every file name and file under the planted HOME (its runs and trees folders)
        and the planted repository."""
        hits = set()
        markers = self.all_markers
        for i, (out, err) in enumerate(self.procs):
            for name, text in (("stdout", out), ("stderr", err)):
                hits |= {(f"run {i} {name}", mk) for mk in markers if mk in (text or "")}
        for top in (self.home, self.repo):
            for folder, dirs, names in os.walk(top):
                for n in dirs + names:
                    p = os.path.join(folder, n)
                    hits |= {(p, mk) for mk in markers if mk in n}
                    if n in names and not os.path.islink(p):
                        try:
                            data = open(p, "rb").read()
                        except OSError:
                            continue
                        hits |= {(p, mk) for mk in markers if mk.encode() in data}
        return sorted(hits)


# -- the delivered files ---------------------------------------------------------------------------------------------
def good_delivered(w):
    """{stem: mapping}: Q01 and q02 re-anchored (only the named entries' cited keys changed), the unique-id question
    marked with a replace_reason and its named entry given a commit."""
    q1, q2, qu = w.staged("Q01"), w.staged("q02"), w.staged(UID)
    # Q01, entry 1 (a mapping): lines and heading changed, a commit added
    q1["sources"][0].update(lines=[4, 11], heading=f"## {NEW_MARKERS[0]}", commit=w.commit)
    # Q01, entry 2 (alternatives): the first's path changed; the second's lines removed and a heading added
    q1["sources"][1][0]["path"] = NEW_MARKERS[1]
    del q1["sources"][1][1]["lines"]
    q1["sources"][1][1]["heading"] = f"# {NEW_MARKERS[2]}"
    # q02, entry 2 (alternatives): the first re-anchored, the second left as it is
    q2["sources"][1][0].update(lines=[2, 6], heading=f"# {NEW_MARKERS[3]}", commit=w.commit)
    # the unique-id question: marked for replacement, its named entry given a commit
    qu["sources"][0]["commit"] = w.commit
    qu["replace_reason"] = "changed"
    return {"Q01": q1, "q02": q2, UID: qu}


def out_files(w, delivered=None, result=None, drop=(), add=None):
    delivered = delivered if delivered is not None else good_delivered(w)
    out = {f"out/{stem}.yaml": (d if isinstance(d, str) else dump(d)) for stem, d in delivered.items()
           if stem not in drop}
    if result is not DROP:
        out["out/result.json"] = result if result is not None else result_json()
    out.update(add or {})
    return out
