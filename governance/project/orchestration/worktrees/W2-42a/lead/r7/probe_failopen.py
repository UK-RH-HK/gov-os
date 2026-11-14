"""Lead probe (W2-42a R4/R5): candidate fail-opens of the blob-ref change. Run with PYTHONPATH at a tree's src.
Prints, per form and role, decide()'s answer. Planted repository under the given scratch folder."""
import os
import subprocess
import sys
import tempfile

scratch = sys.argv[1]
os.makedirs(scratch, exist_ok=True)
root = tempfile.mkdtemp(prefix="proj-", dir=scratch)
G = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]


def sh(*a, cwd=root):
    return subprocess.run(list(a), cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


os.makedirs(os.path.join(root, "governance", "project"))
open(os.path.join(root, "governance", "project", "path-map.yaml"), "w").write(
    "evaluation_sets:\n  w242a:\n    visible: [\"docs/visible.md\"]\n"
    "    hidden: [\"fixtures/evaluation/w242a/hidden/**\"]\n"
    "    measures:\n      roles: [research, engineer]\n")
os.makedirs(os.path.join(root, "fixtures", "evaluation", "w242a", "hidden"))
open(os.path.join(root, "fixtures", "evaluation", "w242a", "hidden", "q01.txt"), "w").write("hidden\n")
os.makedirs(os.path.join(root, "docs"))
open(os.path.join(root, "docs", "a.md"), "w").write("a\n")
open(os.path.join(root, "docs", "b.md"), "w").write("b\n")
os.makedirs(os.path.join(root, "tests", "acceptance", "X"))
open(os.path.join(root, ".env"), "w").write("K=v\n")
sh("git", "init", "-q", "-b", "main")
sh(*G, "add", "-A")
sh(*G, "commit", "-qm", "one")
sub = sh("git", "rev-parse", "HEAD:fixtures/evaluation/w242a")
hid_tree = sh("git", "rev-parse", "HEAD:fixtures/evaluation/w242a/hidden")
blob = sh("git", "rev-parse", "HEAD:fixtures/evaluation/w242a/hidden/q01.txt")
root_tree = sh("git", "rev-parse", "HEAD^{tree}")

from gov.guard.decide import decide  # noqa: E402

forms = [
    f"git diff {sub}:hidden/q01.txt HEAD:docs/a.md",
    f"git show {sub}:hidden/q01.txt",
    f"git diff {hid_tree}:q01.txt HEAD:docs/a.md",
    f"git show {hid_tree}:q01.txt",
    f"git diff {root_tree}:fixtures/evaluation/w242a/hidden/q01.txt HEAD:docs/a.md",
    f"git diff {blob} HEAD:docs/a.md",
    f"git show {blob}",
    "git diff HEAD:docs/a.md HEAD:docs/b.md --output=tests/acceptance/X/zz.txt",
    "git diff --output=tests/acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md",
    "git show --output=tests/acceptance/X/zz.txt HEAD:docs/a.md",
    "git diff --output=tests/acceptance/X/zz.txt HEAD~0 HEAD",
    "git diff HEAD:docs/a.md HEAD:docs/b.md",
    "git cat-file -p HEAD:fixtures/evaluation/w242a/hidden/q01.txt",
    f"git cat-file -p {sub}:hidden/q01.txt",
    f"git cat-file blob {blob}",
]
for role in ("research", "engineer"):
    for f in forms:
        try:
            d, why = decide("Bash", {"command": f}, root, role, None, cwd=root)
        except Exception as exc:  # the error path
            d, why = "RAISE", f"{type(exc).__name__}: {exc}"
        print(f"{role:9} {d:6} {f.replace(sub, '<SUB>').replace(hid_tree, '<HTREE>').replace(blob, '<BLOB>').replace(root_tree, '<ROOT>')}  | {why[:110]}")
