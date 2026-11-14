"""ACT-CLAUDE-RULES-1: the "## Guard" paragraph of .rulesync/rules/governance.md, made true for this repository (DEC-1167 (7)).
    python3 -I patch_source.py <before file> <after file>
Replaces the paragraph's writes sentences and keeps the reads sentence and the last one. The five rules are those of
.claude/hooks/pretooluse.py's own header ("It keeps exactly five rules, and the catastrophic deletes (DEC-953 item 2,
DEC-954, DEC-1050 (8))"): 1 acceptance tests, 2 the hidden half and the held-out material, 5 reviewers' writes, 3 secrets,
4 installs (and sudo). Round b2 folds in the independent review's F1 to F3 (acts/ACT-CLAUDE-RULES-1.review-b-round-1.md):
F1 rule 2d (no writes into the operator's folder but queue/, or the guard's call log) and rule 4's sudo refusal; F2 rule
2b's write refusal and rule 2c's walls for named sessions; F3 the five rules cited to DEC-953 item 2 and DEC-954. Also, from
the hook and bash_writes.py: the write rules judge only the writes the guard resolves (ACT-GUARD-FIX-4), and the role
separation (G-14) is a read rule. Round b1's text is in patch_source.round-b1.py."""
import sys

OLD = ("The guard enforces allowed paths, tool restrictions and permission classes at runtime. It refuses writes outside a "
       "ticket's scope, denies installs for non-orchestrator roles, and blocks access to held-out paths. Reads are open; "
       "only secrets, the held-out material's contents, the counterpart's work on the same ticket and the hidden half of "
       "an evaluation set are refused, and writes stay inside the ticket's paths (DEC-820). The guard decides; role files "
       "state.\n")
NEW = ("Here the live hook (`.claude/hooks/pretooluse.py`) keeps five rules (DEC-953 item 2, and DEC-954 for the fifth): "
       "only the independent test designer writes acceptance tests; the held-out material is not read, nor the hidden "
       "half of an evaluation set by the sessions it measures, and the sets root's hidden folders are neither read nor written by the roles the path "
       "map refuses them; independent reviewers "
       "and auditors write only their own outcomes; secrets and keys are not read; and an install asks the owner in the "
       "CTO's own session and is refused in every other, while sudo is refused to every session. It also refuses the "
       "catastrophic deletes; refuses every session's writes into the operator agent's folder (but its queue/) and into "
       "the guard's call log; refuses named sessions reads and writes of the folders the path map walls off for them (the "
       "engineer on W2-56: the raw transcripts); and applies the path map's role separation to reads. Its write rules judge "
       "a Bash line by the writes the guard resolves from it (`.claude/hooks/bash_writes.py`): a write whose target it "
       "cannot work out is let through, and for the acceptance-test and reviewer rules the backstops are the landing's "
       "check of acceptance-test commits and the reviewed tree's git status. It has no rule that keeps a worker's writes inside its ticket's paths: a launched worker's "
       "writes outside its worktree are walled by the OS sandbox of `gov launch` (SANDBOX-1, DEC-1128 (4)), not by the "
       "hook. In an adopted product the kernel guard enforces allowed paths, tool restrictions and permission classes at "
       "runtime. Reads are open; only secrets, the held-out material's contents, the counterpart's work on the same "
       "ticket and the hidden half of an evaluation set are refused (DEC-820). The guard decides; role files state.\n")
t = open(sys.argv[1], encoding="utf-8").read()
assert t.count(OLD) == 1, "the Guard paragraph is not as expected"
open(sys.argv[2], "w", encoding="utf-8").write(t.replace(OLD, NEW))
