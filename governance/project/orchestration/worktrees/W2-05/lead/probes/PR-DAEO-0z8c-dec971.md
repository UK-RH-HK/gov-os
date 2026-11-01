---
type: probe
task: DAEO-0z8c
reviewer_session: d83ac155-01e9-4a7b-afba-b9ab231fdb90
implementer_session: 611e8297-a9ff-4da9-9049-06f2c3b70026
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 110125ddda0b-FULL-ID-AT-COMMIT
---

# Probe of W2-05 (DAEO-0z8c), the DEC-971/DEC-980 round, at 110125ddda0b

**Probed:** head 110125ddda0b on `w2/W2-05`, the round the resume under DEC-971 and DEC-980 declared, from b28866ba3b22: the lead's merge of `w2/integrate` (d1533bf30a10, f7f4fb5e's W2-95 path-map check, W2-107 secrets cache and W2-108 lexical freshness), which resolved a conflict in `src/gov/check/pathmap.py`, a file the last review judged (DEC-895); test designer aedc72140fcb (fourteen cases for DEC-971 item 3 in the hooks-source suite; W2-72's four fail-closed merge-tree cases moved onto routes containment still takes, DEC-980 item 2, `Rewrite-Reason: DEC-802 (P-B1-2)`), merged as 4e225e7c63da; engineer 1d9c0dca01b2 (the hooks comparison's exception for the two events ACT 1 lifted); the lead's checkpoint record 110125ddda0b. The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-05/src/gov/__init__.py`.

**Who:** a fresh, read-only QA engineer (role `independent-auditor`), started through `gov launch`, sandboxed, `--effort high` (the short re-review the resume's brief asked for, DEC-895); its only repository writes were the sandbox check's git object and index refresh. This is the round's first review (at most two, DEC-916).

**Method:** it read the ticket, DEC-971 item 3, DEC-980, the round's diffs and the cases, and ran probe scripts in its temporary folder against this worktree's `src/`; no suite was re-run (DEC-959 item 1):
- P1, the merge resolution: the merge of b28866ba3b22 and f7f4fb5e recomputed with merge-tree; it differs from d1533bf30a10 in `src/gov/check/pathmap.py` alone, in the conflict hunk only: all of W2-95's code kept, plus this ticket's pinned git environment on its one git call. `src/gov/retrieval/lexical.py` merged clean; W2-108's new calls go through `_git` with this ticket's environment.
- P2, the path-map check under inherited state: an inherited `GIT_DIR` naming another repository, `GIT_WORK_TREE`, both, a foreign or missing `GIT_INDEX_FILE`, `GIT_CONFIG_COUNT` or `GIT_CONFIG_PARAMETERS` setting quotePath, a global `~/.gitconfig` with quotePath, an alias, `trace2.eventTarget` or `core.worktree`, `GIT_TRACE`: findings identical to the baseline every time, no trace written; non-UTF-8, quoted, spaced and accented paths listed byte-exact; a non-repository, a corrupt index and a dangling `.git` file give `TRACKED_PATHS_UNLISTED`, never green.
- P3, the lexical index's freshness key and listing in a main tree and a linked worktree under an inherited `GIT_DIR`, `GIT_WORK_TREE`, a foreign index, and a hook's own `GIT_DIR` and index: the root's own listing every time; `--git-path index` correct in both trees.
- P4, H's exception, twelve cases on the comparison: the two lifted events in the template alone give no finding; any other one-sided event in either direction still a finding beside them; a lifted event in the repository's source alone still a finding; once back in both sources compared as any other; a case variant not excepted; an adopted kernel unaffected; the finding's form unchanged; nothing else in the product compares the two hooks sources.
- P5, W2-72's revised cases: nothing lowered or removed (diff against 4e225e7c63da's first parent), a control added; the exit-128 route reaches the failing `merge-tree --write-tree` alone (the one non-zero call of eleven, with the finding); the seam goes red on a regression (a `PATH` git, no fail-closed, no `sitecustomize`); the seam reaches no other test and nothing of the person's environment.

## Findings

Classification (DEC-809): R6-1 no/fails open; R6-2 yes/other. Neither fails the probe.

**R6-1: a lifted event given a value that is not a list in the repository's source is no finding (row; low)**
- What was done: the repository's hooks source gave `postToolUse` an object instead of a list, while the template has it.
- What happened: the comparison skips a value that is not a list, so the event counts as absent, the exception applies and there is no finding; before this round the same state was `HOOKS_EVENT_DIFFERS`.
- What should have happened: the comparison flags it until the exception ends with W2-08.
- Ordinary work: no, because restoring the events with W2-08 copies the template's list entries, and an object where rulesync expects a list is a construction no honest edit makes.
- Consequence: fails open (the drift report only, and only while the exception lasts).

**R6-2: the lexical index's git calls are unpinned, so a person's global trace setting writes events (row; low)**
- What was done: a person's global `~/.gitconfig` set `trace2.eventTarget`.
- What happened: the lexical index's git calls, W2-108's merged freshness calls among them, run under the unpinned git environment and wrote 20 trace events to that target; the path-map check's pinned call wrote none. Answers and listings unchanged.
- What should have happened: probably pinned like the other read-only calls, unless `hash-object`'s filters are why it was left unpinned.
- Ordinary work: yes, because a person may keep tracing configured globally.
- Consequence: other (a trace written to the person's own target; nothing fails open, no work lost).

Rows of the earlier reviews, unchanged by this round: R4-2 to R4-5, N-1, R5-1 to R5-4.

## Found sound

- The merge kept everything of both sides; the one conflict resolved with W2-95's code and this ticket's environment.
- The path-map check and the lexical index ignore every inherited `GIT_*` variable and the person's configuration for what they list and judge; an unlistable repository is never green.
- DEC-971 item 3 holds exactly: two events, named in the comparison, one direction only, ending by itself when they return.
- W2-72's four cases keep every expectation and reach the failing merge-tree on routes containment still takes.
- The commits carry `Task`, `Role`, `Implements` and, for the test revision, both `Rewrite-Reason` lines; the engineer's paths are inside the ticket's `allowed_paths`.

**Judgement: pass.** No finding is "yes" with "fails open" or "loses work"; R6-1 and R6-2 go to the Wave 3 hardening pass (DEC-801).
