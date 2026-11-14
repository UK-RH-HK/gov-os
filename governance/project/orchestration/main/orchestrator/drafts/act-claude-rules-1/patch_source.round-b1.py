"""ACT-CLAUDE-RULES-1: the "## Guard" paragraph of .rulesync/rules/governance.md, made true for this repository (DEC-1167 (7)).
    python3 -I patch_source.py <before file> <after file>
Replaces the paragraph's writes sentences and keeps the reads sentence and the last one. The five rules are those of
.claude/hooks/pretooluse.py's own header ("It keeps exactly five rules, and the catastrophic deletes"): 1 acceptance
tests, 2 the hidden half and the held-out material, 5 reviewers' writes, 3 secrets, 4 installs."""
import sys

OLD = ("The guard enforces allowed paths, tool restrictions and permission classes at runtime. It refuses writes outside a "
       "ticket's scope, denies installs for non-orchestrator roles, and blocks access to held-out paths. Reads are open; "
       "only secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden half of "
       "an evaluation set are refused, and writes stay inside the ticket's paths (DEC-820). The guard decides; role files "
       "state.\n")
NEW = ("Here, since DEC-953 item 2, the live hook (`.claude/hooks/pretooluse.py`) keeps five rules: only the independent "
       "test designer writes acceptance tests; the held-out material and the hidden half of an evaluation set are not "
       "read; independent reviewers and auditors write only their own outcomes; secrets and keys are not read; and an "
       "install asks the owner in the CTO's own session and is refused in every other. It also refuses the catastrophic deletes and applies the path "
       "map's role separation. It has no rule that keeps a worker's writes inside its ticket's paths: a launched worker's "
       "writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by the "
       "hook. In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at "
       "runtime. Reads are open; only secrets, the held-out material's contents, the counterpart's work on the same "
       "ticket and the hidden half of an evaluation set are refused (DEC-820). The guard decides; role files state.\n")
t = open(sys.argv[1], encoding="utf-8").read()
assert t.count(OLD) == 1, "the Guard paragraph is not as expected"
open(sys.argv[2], "w", encoding="utf-8").write(t.replace(OLD, NEW))
