#!/usr/bin/env python3
"""The commit freeze in the commit path (ACT-OPERATOR-1; DEC-1106 (3), DEC-1028 (6), W2-148's F5).

    python3 -I freeze_gate.py <freeze file>     (stdin: the reference-transaction hook's lines `<old> <new> <ref>`)

Run by the main repository's reference-transaction hook in the `prepared` state, and only while the operator agent's
commit freeze exists (`<operator root>/install/act-in-progress.txt`, written by operator_run.py before `apply.sh
apply` and removed by the run that wrote it). It reads the freeze's ACT and manifest sha, the ACT's frozen manifest
(`<operator root>/acts/<ACT>-<sha12>/manifest.json`) and the update of the live branch (the branch the main tree has
checked out). That update is refused when the change it lands touches
  - a repository path the ACT changes (the manifest's `repo` touched paths), or
  - a control path the operator's after-check reads, where a commit landing now would lock the operator (F15, F26):
    `.claude/**`, `.rulesync/**`, the path map, the dead-man's and the sentinel's files,
unless every commit it adds carries the operator's own trailers (`Act: <the freeze's ACT>` and `Act-sha: <its sha>`).
Every other update goes on (DEC-1028 (6): "every other commit goes on"); other refs are never judged.
Fail closed while the freeze exists: a freeze or a manifest it cannot read makes every path frozen; a range it cannot
list, a rewind or a creation of the live branch is refused. A deletion lands no file and goes on (pack-refs and gc delete
the loose copy of a ref they pack; git reports an old value of zeros when the caller gave none, so the ref's present
value is taken). Exit 0 lets the transaction through, exit 1 aborts it
(git shows the refusal printed on stderr). Standard library only; never writes anything.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
ZERO = re.compile(r"^0+$")
ACT_RE = re.compile(r"^ACT-[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
CONTROL_PREFIXES = (".claude/", ".rulesync/")
CONTROL_FILES = ("governance/project/path-map.yaml", "governance/project/orchestration/tools/deadman.py",
                 "governance/project/orchestration/tools/sentinel-brief.md")
# the hook's own git variables would turn a call on another tree; object paths (a quarantine) are kept
DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR")


def git(args, common=None, plain=False):
    env = dict(os.environ) if plain else {k: v for k, v in os.environ.items() if k not in DROP}
    cmd = ["git"] + (["--git-dir", common] if common else []) + list(args)
    r = subprocess.run(cmd, capture_output=True, env=env, stdin=subprocess.DEVNULL, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} failed ({r.stderr.decode('utf-8', 'replace').strip()[:160]})")
    return r.stdout.decode("utf-8", "surrogateescape")


def read_freeze(path):
    """(act, sha, text) from the freeze's first line; (None, None, text) when it is not of that form."""
    try:
        if os.path.islink(path):
            return None, None, "(a link)"
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read(4096)
    except OSError as exc:
        return None, None, f"(unreadable: {exc.__class__.__name__})"
    toks = text.split()
    if len(toks) >= 2 and ACT_RE.match(toks[0]) and SHA_RE.match(toks[1]):
        return toks[0], toks[1], text.strip().splitlines()[0][:160] if text.strip() else ""
    return None, None, text.strip()[:160]


def frozen_paths(root, act, sha):
    """The ACT's repo paths from its frozen manifest, or None (every path frozen) when it cannot be read."""
    if not act:
        return None
    m = os.path.join(root, "acts", f"{act}-{sha[:12]}", "manifest.json")
    try:
        with open(m, encoding="utf-8") as f:
            data = json.load(f)
        return {t["path"] for t in data["touched"] if t.get("root") == "repo" and isinstance(t.get("path"), str)}
    except (OSError, ValueError, KeyError, TypeError):
        return None


LIVE_FALLBACK = "refs/heads/w2/integrate"


def live_branch(common):
    """The branch the main tree has checked out; on a detached HEAD the live branch by name, so a detached main tree
    never makes every ref update a refusal (review F4)."""
    try:
        return git(["symbolic-ref", "-q", "HEAD"], common=common).strip() or LIVE_FALLBACK
    except RuntimeError:
        return LIVE_FALLBACK


def is_control(p):
    return p.startswith(CONTROL_PREFIXES) or p in CONTROL_FILES


def judge(freeze, lines):
    """Returns (ok, message)."""
    act, sha, ftext = read_freeze(freeze)
    root = os.path.dirname(os.path.dirname(os.path.abspath(freeze)))
    common = os.path.abspath(git(["rev-parse", "--path-format=absolute", "--git-common-dir"], plain=True).strip())
    live = live_branch(common)
    paths = frozen_paths(root, act, sha)
    for ln in lines:
        parts = ln.split()
        if len(parts) != 3 or parts[2] != live:
            continue
        old, new, ref = parts
        head = (f"the commit freeze (DEC-1106 (3)): the operator agent is applying {act or 'an ACT'} "
                f"({ftext or freeze}); ")
        if ZERO.match(old):
            # git reports old as zeros when the caller gave none (pack-refs, gc, update-ref without an old value):
            # the ref's present value is the old one (review F3)
            try:
                cur = git(["rev-parse", "-q", "--verify", ref], common=common).strip()
            except RuntimeError:
                cur = ""
            old = cur or old
        if old == new or ZERO.match(new):
            continue                       # nothing moves, or a deletion (pack-refs prunes the loose copy so): no file lands
        if ZERO.match(old):
            return False, head + f"{ref} is created while it holds; refused"
        rng = git(["rev-list", "--first-parent", f"{old}..{new}"], common=common).split()
        changed = [p for p in git(["-c", "core.quotePath=false", "diff", "--no-renames", "--name-only", old, new],
                                  common=common).splitlines() if p]
        hit = sorted(p for p in changed if is_control(p) or paths is None or p in paths)
        if not hit:
            continue
        if not rng:
            return False, head + f"this update moves {ref} back over {', '.join(hit[:5])}; refused"
        foreign = []
        for c in rng:
            out = git(["log", "-1", "--format=%(trailers:key=Act,valueonly,separator=%x1f)%x00"
                                    "%(trailers:key=Act-sha,valueonly,separator=%x1f)", c], common=common)
            a_s, _, s_s = out.strip("\n").partition("\x00")
            acts = {v.strip() for v in a_s.split("\x1f") if v.strip()}
            shas = {v.strip() for v in s_s.split("\x1f") if v.strip()}
            if not (act and act in acts and sha in shas):
                foreign.append(c[:12])
        if foreign:
            what = "the paths the ACT changes" if paths is not None else "any path (its manifest cannot be read)"
            return False, (head + f"commit(s) {', '.join(foreign[:5])} on {ref} touch {', '.join(hit[:8])}"
                           + (" …" if len(hit) > 8 else "")
                           + f": {what} and the operator's control paths are frozen until the freeze file is gone; "
                           "refused. Every other path goes on; commit this again after the ACT (a stale freeze is "
                           "the owner's to remove).")
    return True, ""


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: freeze_gate.py <freeze file>  (stdin: the hook's lines)\n")
        return 1
    freeze = argv[1]
    if not os.path.lexists(freeze):
        return 0
    lines = sys.stdin.read().splitlines()
    try:
        ok, msg = judge(freeze, lines)
    except Exception as exc:  # fail closed while the freeze exists, but only for the live branch's update
        try:
            common = os.path.abspath(git(["rev-parse", "--path-format=absolute", "--git-common-dir"],
                                         plain=True).strip())
            live = live_branch(common)
        except Exception:
            live = None
        if live is not None and not any(len(ln.split()) == 3 and ln.split()[2] == live for ln in lines):
            return 0
        sys.stderr.write(f"the commit freeze (DEC-1106 (3)): the gate could not judge this update "
                         f"({exc.__class__.__name__}: {exc}) while {freeze} exists; refused\n")
        return 1
    if not ok:
        sys.stderr.write(msg + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
