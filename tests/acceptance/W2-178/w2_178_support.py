"""W2-178 acceptance tests' support: a planted set with a ``hidden/dropped/`` subtree, the script as it stood before the
change, and wall snapshots, all on W2-149's planted world.

Nothing here imports the script under test: it runs as a program from W2-149's planted repository, with W2-149's planted
HOME, sets root and stub ``claude`` (imported from ``tests/acceptance/W2-149``, never copied; W2-173's auditor
delivery helper comes from ``tests/acceptance/W2-173``). Every launch goes through ``World.check_planted``, which fails
on any location outside pytest's temporary folder, so no case can reach the real sets root, a hidden half or the
held-out material.

The base script (``BASE``, the ticket's claim commit and the merge-base with ``w2/integrate``) is taken out of git into
a temporary folder next to its ``indep-schemas`` folder and run the same way as the head's, on the same planted world,
so the two builds differ only in the script.
"""

from __future__ import annotations

import io
import os
import shutil
import stat
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _p in (HERE.parent / "W2-149", HERE.parent / "W2-173"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import w2_149_support as support  # noqa: E402
import w2_173_support as s173  # noqa: E402,F401  (re-exported for the cases)

TICKET_ID = "DAEO-7oxm"
W2 = "W2-178"
BASE = "03393ee51"                      # the script before this change; also the ticket's claim commit
BASE_FALLBACK = BASE
SCRIPT_REL = "governance/project/orchestration/tools/indep_launch.py"
SCHEMAS_REL = "governance/project/orchestration/tools/indep-schemas"
SET = "memory-verdict-3"                # W2-149's planted set: hidden/q01.yaml, q02.yaml, sub/q03.yaml
SEED = 4242
RUN_MARK = b"<RUN>"
SNAPS: dict = {}                        # (the world's folder, run id) -> the wall as build read it

# -- the planted set ------------------------------------------------------------------------------------------------

# every file under hidden/dropped/, to any depth (paths relative to hidden/)
DROPPED = {
    "dropped/q07.yaml": b"id: q07\nquestion: a dropped question, one folder down\n",
    "dropped/x/q08.yaml": b"id: q08\nquestion: a dropped question, two folders down\n",
    "dropped/x/y/q11.yaml": b"id: q11\nquestion: a dropped question, three folders down\n",
}
# names that only look like the dropped folder: not under hidden/dropped/, so they stay
LOOKALIKES = {
    "dropped.yaml": b"id: q12\nquestion: a file named dropped at the top\n",
    "dropped-items/q10.yaml": b"id: q10\nquestion: a folder whose name starts with dropped\n",
    "droppedq/q13.yaml": b"id: q13\nquestion: another folder whose name starts with dropped\n",
}
# a folder named dropped below another folder is not hidden/dropped/ (the lead's reading of the ticket's wording)
NESTED = {"sub/dropped/q09.yaml": b"id: q09\nquestion: a dropped folder one level below hidden/sub/\n"}
# a kept file whose bytes are not text, to make byte identity bite
RAW = {"sub/raw.bin": b"\x00\xff\r\n\x80id: q14\r\n\x00"}


def hidden_dir(world) -> Path:
    return world.sr / "fixtures" / "evaluation" / SET / "hidden"


def plant(world, *groups, xcheck=False):
    """Add the named groups of files to the planted set's hidden folder (and round 1's notes for a writer's round 2)."""
    for group in groups:
        for rel, data in group.items():
            support.write_file(hidden_dir(world), rel, data)
    if xcheck:
        support.write_file(world.sr, f"fixtures/evaluation/{SET}/XCHECK-r1.md", "# the checker's notes (planted)\n")


def source_files(world) -> dict:
    """Every file under the set's hidden folder: path relative to hidden/ -> bytes."""
    top = hidden_dir(world)
    out = {}
    for dp, _dn, fn in os.walk(top):
        for n in fn:
            p = Path(dp) / n
            out[os.path.relpath(p, top)] = p.read_bytes()
    return out


def under_dropped(rel: str) -> bool:
    parts = rel.split("/")
    return parts[0] == "dropped" and len(parts) > 1


def sets_snapshot(world) -> dict:
    """The set's folder and the whole fixtures tree: every file's path -> bytes (the sets root's source material)."""
    top = world.sr / "fixtures"
    out = {}
    for dp, _dn, fn in os.walk(top):
        for n in fn:
            p = Path(dp) / n
            out[os.path.relpath(p, top)] = p.read_bytes()
    return out


# -- the script as it stood before the change -----------------------------------------------------------------------

def extract_base_script(dst: Path) -> Path:
    """The launch script at ``BASE`` and its ``indep-schemas`` folder, out of git, under ``dst``; the script's path."""
    raw = support.git(support.TREE, "archive", "--format=tar", BASE, "--", SCRIPT_REL, SCHEMAS_REL, raw=True)
    dst.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(raw)) as t:
        t.extractall(dst, filter="data")
    script = dst / SCRIPT_REL
    assert script.is_file() and (dst / SCHEMAS_REL).is_dir(), f"{BASE} holds no launch script or no schemas"
    return script


def launch_with(world, script: Path, *args, timeout=180) -> support.Run:
    """World.launch for any copy of the script (the base's): the planted repository as the working folder, the planted
    environment, no stdin."""
    world.check_planted()
    p = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=str(world.repo_path), env=world.base_env(),
                       capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return support.Run(p.returncode, p.stdout, p.stderr)


def build(world, script, kind, round_=None, seed=SEED, set_=SET):
    """A dry build of one wall by the given script (None: the head's, through World.launch); the counts line."""
    support.next_second()                # a new second, so the run id is new
    args = world.args(kind, set_=set_, round_=round_, seed=seed, dry=True)
    run = world.launch(*args) if script is None else launch_with(world, script, *args)
    assert run.code == 0, run.why()
    assert run.line and run.line["status"] == "dry", run.line
    line = run.line
    # The wall is read now and then removed with its tree: the settings of a later wall deny every other wall of the
    # kind that is still in the walls folder (an earlier build's), so a wall built second would differ for that alone.
    SNAPS[(str(world.tmp), line["run"])] = read_wall(world, line)
    for folder in (world.wall(line), world.tree(line)):
        support.make_writable(folder)
        shutil.rmtree(folder)
    return line


# -- the wall's snapshot ---------------------------------------------------------------------------------------------

def snapshot(world, line) -> dict:
    """The wall ``build`` read for this counts line (see ``read_wall``)."""
    return SNAPS[(str(world.tmp), line["run"])]


def read_wall(world, line) -> dict:
    """Every entry of the wall: relative path -> ('dir', mode) or (mode, bytes); the run id inside a file is
    replaced by ``RUN_MARK`` (it is in the tree's and the wall's own paths the files name). That id is the only field
    that differs between two builds by one script with one seed, in one world, one after the other with no other wall
    of the kind left: seed.txt, the selection, the settings, the brief and the manifest are otherwise equal byte for
    byte (the sanity case shows it)."""
    wall = world.wall(line)
    rid = line["run"].encode()
    out = {}
    for dp, dn, fn in os.walk(wall):
        for n in dn:
            p = Path(dp) / n
            out[os.path.relpath(p, wall)] = ("dir", stat.S_IMODE(os.lstat(p).st_mode))
        for n in fn:
            p = Path(dp) / n
            out[os.path.relpath(p, wall)] = (stat.S_IMODE(os.lstat(p).st_mode), p.read_bytes().replace(rid, RUN_MARK))
    # WALL.json's settings_sha256 is the hash of a settings file that names the run id: it follows the run id. It is
    # checked against the wall's own settings file, then replaced by the hash of the settings with the id replaced.
    mode, manifest = out["WALL.json"]
    settings = out[".claude/settings.json"][1]
    raw_settings = (wall / ".claude" / "settings.json").read_bytes()
    old = support.sha256(raw_settings).encode()
    assert old in manifest, "WALL.json's settings_sha256 is not the hash of the wall's settings file"
    out["WALL.json"] = (mode, manifest.replace(old, support.sha256(settings).encode()))
    return out


def differences(a: dict, b: dict) -> dict:
    """Paths whose entry is not the same in both (or is in one only)."""
    out = {}
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            out[k] = "only in the first" if k not in b else "only in the second" if k not in a else "differs"
    return out


def input_set(snap: dict) -> dict:
    """The wall's ``input/set/`` entries: path relative to it -> entry (the folder itself is not in the dict)."""
    head = "input/set/"
    return {k[len(head):]: v for k, v in snap.items() if k.startswith(head)}


def without_dropped(snap: dict) -> dict:
    """The snapshot with every entry under ``input/set/dropped`` taken out (the folder itself too)."""
    return {k: v for k, v in snap.items() if k != "input/set/dropped" and not k.startswith("input/set/dropped/")}
