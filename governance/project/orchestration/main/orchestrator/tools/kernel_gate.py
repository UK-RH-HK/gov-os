"""The kernel gate (owner, 2026-11-12, "item 5 (a)"; CAP-33; DECIDED-NOT-DONE row 173): a kernel path needs the
owner's approval before any merge.

    python3 kernel_gate.py --repo <repo> --branch <ref> [--base <ref, default w2/integrate>] [--list <path>]

Every file under template/governance/kernel/ that differs between merge-base(base, branch) and branch (a rename is a
delete and an add) must be in the approval list (default: kernel-approved.txt beside this script):
  - an added or modified file: a line with the sha256 of its bytes at <branch> AND its path;
  - a deleted file: a line `DELETED <path> ...`.
One line per kernel file: `ok <path> <sha256-12> <DEC>` or `REFUSED <path> <sha256-64>: no owner approval for these
bytes` (a deletion: `ok <path> DELETED <DEC>` / `REFUSED <path> DELETED: no owner approval for this deletion`);
`kernel_gate: no kernel path changed` when none.
Exit: 0 every file passes (or none changed); 1 any refused; 2 the list is missing, unreadable or malformed, the repo
or a ref does not resolve, or git fails. Fails closed: an error is never exit 0.

List format, one entry per line: `<sha256 64 hex | DELETED> <repo-relative path> <DEC id> <free note>`; `#` comments
and blank lines ignored. Standard library only.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

KERNEL = "template/governance/kernel/"
DEFAULT_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kernel-approved.txt")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
DEC = re.compile(r"^DEC-\d+$")


class GateError(Exception):
    """Anything that must end in exit 2."""


def git(repo, *args):
    """A read-only git command; its stdout as bytes, or GateError."""
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    except OSError as e:
        raise GateError(f"git could not run: {e}")
    if r.returncode:
        raise GateError(f"git {' '.join(args[:2])} failed: {r.stderr.decode(errors='replace').strip()[:300]}")
    return r.stdout


def load_list(path):
    """{(kind, path): DEC} where kind is a sha256 or 'DELETED'; GateError on a missing, unreadable or malformed list."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise GateError(f"approval list {path} missing or unreadable: {e}")
    entries = {}
    for n, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 3)
        if len(parts) < 3:
            raise GateError(f"{path} line {n}: malformed (need <sha256|DELETED> <path> <DEC id> <note>): {s[:120]}")
        kind, rel, dec = parts[0], parts[1], parts[2]
        if kind != "DELETED" and not HEX64.match(kind):
            raise GateError(f"{path} line {n}: malformed: field 1 is neither a 64-hex sha256 nor DELETED: {kind[:80]}")
        if rel.startswith("/") or ".." in rel.split("/"):
            raise GateError(f"{path} line {n}: malformed: the path is not repo-relative: {rel[:120]}")
        if not DEC.match(dec):
            raise GateError(f"{path} line {n}: malformed: field 3 is not a DEC id: {dec[:80]}")
        entries.setdefault((kind, rel), dec)
    return entries


def resolve(repo, ref):
    if ref.startswith("-"):
        raise GateError(f"ref {ref!r} does not resolve")
    try:
        return git(repo, "rev-parse", "--verify", "-q", "--end-of-options", ref + "^{commit}").decode().strip()
    except GateError:
        raise GateError(f"ref {ref!r} does not resolve in {repo}")


def changes(repo, mb, head):
    """[(status, path)] with status A, M or D; a rename or copy is split by --no-renames; T counts as M."""
    out = git(repo, "diff", "--no-renames", "--name-status", "-z", mb, head, "--", KERNEL).decode("utf-8", "surrogateescape")
    fields = out.split("\0")
    if fields and fields[-1] == "":
        fields.pop()
    if len(fields) % 2:
        raise GateError("git diff --name-status output could not be read")
    res = []
    for st, path in zip(fields[0::2], fields[1::2]):
        st = st[:1]
        if st in ("A", "M", "T"):
            res.append(("A" if st == "A" else "M", path))
        elif st == "D":
            res.append(("D", path))
        else:
            raise GateError(f"unexpected git diff status {st!r} for {path}")
    return sorted(res, key=lambda x: x[1])


def run(repo, branch, base, list_path):
    """(exit code, output lines); raises GateError."""
    entries = load_list(list_path)
    if not os.path.isdir(repo):
        raise GateError(f"repo {repo} does not exist")
    git(repo, "rev-parse", "--git-dir")
    head = resolve(repo, branch)
    base_c = resolve(repo, base)
    mb = git(repo, "merge-base", base_c, head).decode().strip()
    if not re.match(r"^[0-9a-f]{40}([0-9a-f]{24})?$", mb):
        raise GateError(f"no merge-base for {base} and {branch}")
    files = changes(repo, mb, head)
    if not files:
        return 0, ["kernel_gate: no kernel path changed"]
    lines, refused = [], 0
    for st, path in files:
        if st == "D":
            dec = entries.get(("DELETED", path))
            if dec:
                lines.append(f"ok {path} DELETED {dec}")
            else:
                refused += 1
                lines.append(f"REFUSED {path} DELETED: no owner approval for this deletion")
            continue
        data = git(repo, "cat-file", "blob", f"{head}:{path}")  # the bytes at <branch> (no textconv, no filters)
        sha = hashlib.sha256(data).hexdigest()
        dec = entries.get((sha, path))
        if dec:
            lines.append(f"ok {path} {sha[:12]} {dec}")
        else:
            refused += 1
            lines.append(f"REFUSED {path} {sha}: no owner approval for these bytes")
    return (1 if refused else 0), lines


def main(argv=None):
    ap = argparse.ArgumentParser(description="The kernel gate: a kernel path needs the owner's approval to merge.")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", required=True)
    ap.add_argument("--base", default="w2/integrate")
    ap.add_argument("--list", default=DEFAULT_LIST)
    try:
        a = ap.parse_args(argv)
    except SystemExit:  # bad arguments (or --help): never 0
        return 2
    try:
        rc, lines = run(a.repo, a.branch, a.base, a.list)
    except GateError as e:
        print(f"kernel_gate: error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # fail closed on anything unforeseen
        print(f"kernel_gate: error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
