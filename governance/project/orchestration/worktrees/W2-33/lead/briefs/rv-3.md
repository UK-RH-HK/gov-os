# Brief rv-3: narrow independent check for DAEO-lrre (W2-33): two revised W1-33 cases, read-only

You are a fresh, read-only reviewer (role independent-auditor). **You write nothing**: no file, no commit. Your last
message is your report.

W2-33 passed review round 1 and a narrow check (docs/probes/DAEO-lrre/PR-DAEO-lrre.md). Under DEC-1156 (7) the CTO
then put two older W1-33 cases in the ticket's paths, and an independent test designer revised exactly those two in
commit `4452d6b8c`, merged into w2/W2-33 at `54ba5bcd2`. After it, `9ace61e8c` writes only the owner's approval line
into the CIT-P (records; not in your scope). In /home/usain/gov-os-worktrees/W2-33, expect HEAD = `9ace61e8c`; if it
is not, say so.

Check only `git diff 707d23b82 4452d6b8c` (the two files `tests/acceptance/W1-33/test_w1_33_kernel_role_files.py` and
`tests/acceptance/W1-33/test_w1_33_agent_definitions.py`):
1. **Case 1, `test_the_research_role_file_body_is_unchanged`** (was `..._is_unchanged`, DEC-163). Does it keep the
   case's point: the kernel holds one research role file, and its body is the one W1-46 placed (commit `c70bbb69d`),
   apart from the owner's every-role-file lines (the ticket's Interface line heads: Version, Launch default, Launch by
   criticality, Skills, Model tier, Work order, One writer per worktree)? Recompute the pinned constant
   `_W1_46_RESEARCH_BODY_SHA256` yourself from `git show c70bbb69d:template/governance/kernel/roles/research.md` with
   the case's own filter; does it match? Would a change to research.md's own body (any non-Interface line added,
   removed or changed) turn the case red? Would it stay green if an Interface line were dropped or altered (the four
   asserted values: Launch default `model claude-sonnet-5-5, effort high`, Model tier `see Launch default`, the Work
   order and One writer sentences word for word as the ticket's Interface gives them)? Is the filter so wide that it
   hides a body change (e.g. a body line that happens to start with one of the heads)?
2. **Case 2, the agents roster** (`test_there_is_one_definition_per_role_and_the_research_one`). Does it want exactly
   nine definitions under `.claude/agents/` (the five of `support.ROLES`, `research`, `ticket-lead`, `qa-engineer`,
   `senior-engineer`), no `independent-reviewer`, each defined once? Does its docstring say it is red until the copies
   ACT generates the three agents? Is that red the only one it brings?
3. Does each revised case carry a `Rewrite-Reason:` naming DEC-1156 (3), (7) and saying what changed and why? Did the
   commit change anything else in the two files (beyond `import hashlib` and a local constant or two)? Are the commit's
   trailers `Task: DAEO-lrre`, `Role: independent-test-designer`, `Implements:` ids from the ticket's sources?
4. The designer reports it printed the Interface-head lines of HEAD's research.md by an oversight while computing the
   pin, and wrote the assertions from the ticket alone. Is any assertion fitted to HEAD's file rather than to the
   ticket's Interface (the ticket: /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-lrre.md, `## Interface`)?

Decisions by id only in docs/DECISION_REGISTER.md: DEC-163, DEC-1156, DEC-1120, DEC-957.

Run tests only read-only, through the gate, with the sandbox's own TMPDIR:
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33/src python3 -m pytest tests/acceptance/W1-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
Expected: case 1 green; case 2 red (six agents found); the five `test_the_definition_agrees_with_its_kernel_role_file`
cases red before and after (the copies ACT's, already named). A heavy-slot refusal is a wait. To try a mutation of
research.md, copy the file and the case's logic into your sandbox's TMPDIR; never change the tree.

Threat model (DEC-801, DEC-808): honest mistakes in ordinary work. A finding fails the check only when it is in scope,
reachable in ordinary work, and makes a case pass when it should fail (or fail when it should pass). Anything else is a
recorded row.

## Return (your last message)
The twelve fields, each a labelled line ("none" where nothing). Then the findings (N1..Nn: behaviour, path:line,
severity, in scope or a row, blocking or not), the answers to 1-4, then exactly:
```verdict
verdict: PASS or FAIL
probed_commit: <the full 40-character hash>
findings: <n>
```
and `guard_refusals:`.
