"""Support code for the W2-94 fix flow's acceptance cases (S6-S12, F4-F6; DEC-1180 (2), DEC-1178 (5)).

The program under test is ``governance/project/orchestration/tools/indep_launch.py`` run as a process, through the
fake-session seam W2-149's unit tests built (``World``: a planted sets root, HOME, repository with the walls' template
and an APPROVED list, and a stub ``claude`` driven by a JSON config). ``FixWorld`` adds to it:

* the approved variant (``fixtures/EXAMIN-writer-q02-fix.md``, byte for byte) committed at its approved path and
  listed in the planted APPROVED list;
* a planted ``examin`` set: q01-q06 in ``hidden/``, q07 and q08 in ``hidden/visible/``, a ``hidden/dropped/`` file,
  ``hidden/DRAW.txt``, ``XCHECK-r1.md``, ``visible/`` and ``.release-visible.record``, every file with its own made-up
  content marker (``zqxw94-...``);
* planted round-1 and other runs under ``<runs>/indep/writer/<rid>/counts.json`` with their archives
  ``<walls>/writer/<rid>.tar`` holding ``<rid>/input/selection.json``: two delivered round-1 runs of the set (different
  samples), a later rejected one, a later delivered round 2, a later delivered round 1 of another set and a folder
  whose name is not a run id.

Nothing under ``~/gov-os-eval``, ``~/gov-os-runs`` or any real ``hidden`` folder is opened; every word is made up and
carries the prefix ``zqxw94``. No real ``claude`` session: the stub only.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UNIT = ROOT / "tests" / "unit" / "orchestration"
sys.path.insert(0, str(UNIT))

from test_w2_149_indep_launch import (  # noqa: E402  (the fake-session seam; its tests are not imported)
    SCRIPT, WALLS, World, indep_launch, schema, tree_hash, writer_out)

import test_w2_149_indep_launch as _seam  # noqa: E402

if os.environ.get("W2_94_FIX_SCRIPT"):  # another copy of the script in place of the tree's (a planted-break run)
    _seam.SCRIPT = Path(os.environ["W2_94_FIX_SCRIPT"])
    SCRIPT = _seam.SCRIPT

WORD = "zqxw94"
SETN = "examin"
VARIANT_REL = "governance/project/indep-briefs/examin-sets/EXAMIN-writer-q02-fix.md"
VARIANT_SHA = "0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "EXAMIN-writer-q02-fix.md"
FIX_CODES = ("SOURCE_IS_SCAFFOLD", "SOURCE_PATH_ABSENT", "SOURCE_NOT_TEXT", "SPAN_OUT_OF_FILE", "HEADING_NOT_FOUND",
             "ANSWER_NOT_IN_SPANS", "NONEXISTENT_NAME_FOUND", "NONEXISTENT_NO_NAME")
CODE = "ANSWER_NOT_IN_SPANS"

# the planted runs: run id -> (status, round, set, sample)
LATEST = "20261105T100000Z-examin-r1"
OLDER = "20261101T100000Z-examin-r1"
REJECTED = "20261107T100000Z-examin-r1"
ROUND2 = "20261108T100000Z-examin-r2"
OTHER_SET = "20261109T100000Z-other-r1"
NOT_A_RUN = "zz-examin-r1"


def _sample(tag):
    return [f"docs/{WORD}-{tag}-{n}.md" for n in ("c", "a", "b")]  # deliberately not sorted


SAMPLE_OF = {OLDER: _sample("old"), LATEST: _sample("latest"), REJECTED: _sample("rejected"),
             ROUND2: _sample("round2"), OTHER_SET: _sample("otherset"), NOT_A_RUN: _sample("notarun")}
RUNS = {OLDER: ("delivered", 1, SETN), LATEST: ("delivered", 1, SETN), REJECTED: ("rejected", 1, SETN),
        ROUND2: ("delivered", 2, SETN), OTHER_SET: ("delivered", 1, "other"), NOT_A_RUN: ("delivered", 1, SETN)}

# what the stub session writes for a good fix run
NEW_Q02 = (f"id: q02\nquestion: {WORD}-q02-new-question\ngold_answer: {WORD}-q02-new-answer\n"
           f"marker: {WORD}-q02-new-mark\n")
NEW_MARKERS = (f"{WORD}-q02-new-question", f"{WORD}-q02-new-answer", f"{WORD}-q02-new-mark")
SESSION_TEXT = f"{WORD}-session-text"
OLD_Q02_MARK = f"{WORD}-q02-old-mark"
DROP = object()  # a result key to leave out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def snap(top):
    """Every entry below *top* as {relative path: ("f", sha256) | ("d",) | ("l", target)}; nothing followed."""
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


def result_json(action="corrected", **changes):
    r = {"questions": 1, "action": action, "by_kind": {"location": 1}, "by_area": {"code": 1}}
    r.update(changes)
    return json.dumps({k: v for k, v in r.items() if v is not DROP})


def good_out(action="corrected", **changes):
    return {"out/q02.yaml": NEW_Q02, "out/result.json": result_json(action, **changes)}


def selection_bytes(sample):
    return (json.dumps({"commit": "0" * 40, "last_audit": None, "seed_sha256": "0" * 64, "changed": [],
                        "sample": sample}, indent=1) + "\n").encode()


def make_tar(path, rid, members):
    """An archive in the form pack() makes: the wall folder ``rid`` and its members; each member is
    (name below rid, bytes) or (name below rid, ("link", target))."""
    with tarfile.open(path, "w") as t:
        folders = {rid}
        for name, _ in members:
            parts = name.split("/")[:-1]
            for i in range(len(parts)):
                folders.add(rid + "/" + "/".join(parts[:i + 1]))
        for f in sorted(folders):
            ti = tarfile.TarInfo(f)
            ti.type, ti.mode = tarfile.DIRTYPE, 0o755
            t.addfile(ti)
        for name, data in members:
            ti = tarfile.TarInfo(f"{rid}/{name}")
            if isinstance(data, tuple):
                ti.type, ti.linkname, ti.mode = tarfile.SYMTYPE, data[1], 0o777
                t.addfile(ti)
            else:
                ti.size, ti.mode = len(data), 0o444
                t.addfile(ti, io.BytesIO(data))


class FixWorld(World):
    def __init__(self, tmp, listed=True):
        super().__init__(tmp)
        self.tmp = Path(tmp)
        self.put(VARIANT_REL, FIXTURE.read_bytes())
        self.commit = self.commit_all("the approved variant")
        self.approve(self.commit)
        if listed:
            with open(self.sets / WALLS / "APPROVED", "a") as f:
                f.write(f"{VARIANT_SHA}  brief writer {VARIANT_REL}\n")
        self.markers = {}
        self.plant_examin()
        for rid in RUNS:
            self.plant_run(rid)

    # -- the planted set -----------------------------------------------------------------------------------------
    @property
    def setdir(self):
        return self.sets / "fixtures" / "evaluation" / SETN

    def _plant(self, rel, text=None, qid=None, tag=None):
        p = self.setdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        slug = rel.replace("/", "-").replace(".", "-").replace("_", "-").strip("-")
        mark = f"{WORD}-{slug}-mark"
        if rel == "hidden/q02.yaml":
            mark = OLD_Q02_MARK
        if text is None:
            text = f"id: {qid}\nquestion: {mark}-question\ngold_answer: {mark}-answer\nmarker: {mark}\n"
        else:
            text = f"{text}\n{mark}\n"
        p.write_text(text)
        self.markers[rel] = mark
        return p

    def plant_examin(self):
        for i in range(1, 7):
            self._plant(f"hidden/q{i:02d}.yaml", qid=f"q{i:02d}")
        for i in (7, 8):
            self._plant(f"hidden/visible/q{i:02d}.yaml", qid=f"q{i:02d}")
        self._plant("hidden/dropped/q09.yaml", qid="q09")
        self._plant("hidden/DRAW.txt", "1 code-location SEED+1=2 even visible=q07 hidden=q01")
        self._plant("XCHECK-r1.md", "# Cross-check notes")
        for i in (7, 8):
            self._plant(f"visible/q{i:02d}.yaml", qid=f"q{i:02d}")
        self._plant(".release-visible.record", "q07.yaml 00\nq08.yaml 00")

    @property
    def other_markers(self):
        return [m for rel, m in self.markers.items() if rel != "hidden/q02.yaml"]

    @property
    def all_markers(self):
        sample_words = [s for sample in SAMPLE_OF.values() for s in sample]
        return list(self.markers.values()) + list(NEW_MARKERS) + [SESSION_TEXT] + sample_words

    # -- the planted runs ----------------------------------------------------------------------------------------
    def counts_path(self, rid):
        return self.runs / "writer" / rid / "counts.json"

    def tar_path(self, rid):
        return self.sets / WALLS / "writer" / f"{rid}.tar"

    def plant_run(self, rid, status=None, members=None, archive=True, record=True):
        st, rnd, set_name = RUNS[rid]
        if record:
            self.counts_path(rid).parent.mkdir(parents=True, exist_ok=True)
            self.counts_path(rid).write_text(json.dumps({"kind": "writer", "run": rid, "set": set_name, "round": rnd,
                                                          "status": status or st, "code": 0}) + "\n")
        if archive:
            self.tar_path(rid).parent.mkdir(parents=True, exist_ok=True)
            if members is None:
                members = [("input/selection.json", selection_bytes(SAMPLE_OF[rid])), ("brief.md", b"brief\n")]
            make_tar(self.tar_path(rid), rid, members)

    # -- the runs ------------------------------------------------------------------------------------------------
    def fix_argv(self, *, fix="q02", reason=CODE, kind="writer", rnd=2, set_name=SETN, seed=None, dry=False,
                 brief=VARIANT_REL, brief_sha=VARIANT_SHA, audit=None):
        a = ["--sets-root", str(self.sets), "--kind", kind, "--brief", brief, "--brief-sha256", brief_sha,
             "--commit", self.commit, "--set", set_name]
        if rnd is not None:
            a += ["--round", str(rnd)]
        if audit:
            a += ["--audit", audit]
        if fix is not None:
            a += ["--fix", fix]
        if reason is not None:
            a += ["--reason", reason]
        if seed is not None:
            a += ["--seed", str(seed)]
        if dry:
            a.append("--dry")
        return a

    def fix(self, extra=None, **kw):
        return self.run(*self.fix_argv(**kw), extra=extra)

    def dry_fix(self, **kw):
        return self.fix(seed=17, dry=True, **kw)

    def session(self, out, hook_lines=None, **cfg):
        self.stub(dict({"session": "write", "out": out, "marker": SESSION_TEXT}, **cfg))
        if hook_lines is None:
            return None
        body = "if point == 'after_session':\n" + "".join(f"    {ln}\n" for ln in hook_lines)
        return {"GOV_INDEP_TEST_HOOK": self.hook(body)}

    def state(self):
        """Everything a run could build or change: the sets root, the runs folder and the trees folder."""
        return {"sets": snap(self.sets), "runs": snap(self.home / "gov-os-runs"),
                "trees": snap(self.home / "gov-os-wall-trees")}

    def set_files(self):
        """The sets root less the walls' folder (the runs' own archives live there)."""
        return {k: v for k, v in snap(self.sets).items() if k.split(os.sep)[0] != WALLS}

    def tar_names(self, run):
        with tarfile.open(self.tar_path(run)) as t:
            return t.getnames()

    def tar_bytes(self, run, name):
        with tarfile.open(self.tar_path(run)) as t:
            return t.extractfile(f"{run}/{name}").read()

    def leaks(self, rc_counts_p):
        """The planted markers found in stdout, stderr, counts.json and launch.log of a run."""
        counts, p = rc_counts_p
        texts = [p.stdout, p.stderr]
        run = counts.get("run") if counts else None
        if run:
            folder = self.runs / "writer" / run
            for name in ("counts.json", "launch.log"):
                if (folder / name).exists():
                    texts.append((folder / name).read_text())
        blob = "\n".join(texts)
        return [m for m in self.all_markers if m in blob]

    def wall_listing(self, wall):
        files, dirs, links = [], [], []
        for folder, ds, names in os.walk(wall):
            for n in ds + names:
                p = os.path.join(folder, n)
                rel = os.path.relpath(p, wall)
                mode = os.lstat(p).st_mode
                (links if stat.S_ISLNK(mode) else dirs if stat.S_ISDIR(mode) else files).append(rel)
        return sorted(files), sorted(dirs), sorted(links)
