"""Asks the guard's read policy (the tree's src) whether a measured engineer session in one tree is refused a read of
the memory-retrieval set's hidden part in its own tree, in the main tree and in another worktree. Paths only; no
file is read (the paths need not exist). Prints one line per case: the path's tree and REFUSED or ALLOWED."""
from gov.guard.reads import policy_refusal

MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
REL = "fixtures/evaluation/memory-retrieval/hidden/q01.yaml"
cases = [
    ("own tree (session root = main tree)", MAIN, MAIN + "/" + REL),
    ("main tree, session in a worktree", "/home/usain/gov-os-worktrees/W2-03", MAIN + "/" + REL),
    ("another worktree", MAIN, "/home/usain/gov-os-worktrees/W2-61h/" + REL),
    ("a run clone", MAIN, "/home/usain/gov-os-runs/W2-61/clone/" + REL),
]
for name, root, path in cases:
    why = policy_refusal("Read", {"file_path": path}, root, root, "engineer", None)
    print(("REFUSED" if why else "ALLOWED") + "  " + name)
