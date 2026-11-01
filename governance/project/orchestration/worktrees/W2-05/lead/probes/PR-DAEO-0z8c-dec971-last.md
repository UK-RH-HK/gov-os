---
type: probe
task: DAEO-0z8c
reviewer_session: 738f9982-d4c4-4439-ba4f-257d1615171f
implementer_session: 6ca9d4cf-0ae6-4ec0-8fc2-f1edb3b9d937
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: e122beca7ef7-FULL-ID-AT-COMMIT
---

# Probe of W2-05 (DAEO-0z8c), the DEC-971/DEC-980 round, second and last review, at e122beca7ef7

**Probed:** head e122beca7ef7 on `w2/W2-05`, the round the resume under DEC-971 and DEC-980 declared, from b28866ba3b22:
- the lead's merge of `w2/integrate` (f7f4fb5e1c88) as d1533bf30a10, which resolved a conflict in `src/gov/check/pathmap.py`, a file the DEC-970 round's review judged (DEC-895);
- test designer aedc72140fcb, merged as 4e225e7c63da: fourteen cases for DEC-971 item 3 in the hooks-source suite; W2-72's four fail-closed merge-tree cases moved onto routes containment still takes (DEC-980 item 2, `Rewrite-Reason: DEC-802 (P-B1-2)`);
- engineer 1d9c0dca01b2: the hooks comparison's exception for the two events ACT 1 lifted (DEC-971 item 3);
- the checkpoint records 110125ddda0b (the first review's head) and e122beca7ef7;
- the fix after the first review, engineer a5b728d2f8a7: the lexical index's four git calls run pinned (R6-2; the lead's scoped run found this ticket's planted `gov close` case red on W2-108's freshness calls, W2-M161).

The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-05/src/gov/__init__.py`.

**Who:** a fresh, read-only QA engineer (role `independent-auditor`), started through `gov launch`, sandboxed, `--effort max`; its only repository writes were the sandbox check's git object and index refresh. This is the round's second and last review (DEC-413, DEC-916). The first review (session d83ac155, `--effort high`, at 110125ddda0b) judged pass, with rows R6-1 and R6-2; its record stays a draft under the lead's scratch.

**Method:** it read the ticket, DEC-971 item 3, DEC-980 items 2 and 3, DEC-805, DEC-802, DEC-895 and DEC-953 item 2, the DEC-970 round's record, the round's diffs and the fix's builder tests, and ran nine probes in its temporary folder against this worktree's `src/`, on throwaway repositories built from scratch from single named files; no suite was re-run (DEC-959 item 1):
- P1: in-process, with the real secrets filter and the person's trace2 event, perf and normal targets in `~/.gitconfig`, then in the XDG file: refresh, freshness (W2-108's key), search without refresh, an edit, refresh, freshness; every git start recorded with its caller and pinning.
- P2: `gov rebuild --no-embeddings`, `gov check` and `gov retrieve` as separate processes, with a logging git first on `PATH`, in both placements.
- P3, P3b: the key, listing, blob ids, digest and freshness, pinned against unpinned: an ordinary configuration; the repository's own `.gitattributes`, `.git/info/attributes` and `.git/config`; the person's id-changing settings.
- P4: global `core.autocrlf = true`: a store built by the pre-fix code, then judged and refreshed by the fix, and the reverse.
- P5: another owner simulated (git's test switch), with `safe.directory` only in the person's file.
- P6: a main tree and a linked worktree, nine cases with inherited `GIT_INDEX_FILE`, `GIT_DIR`, `GIT_WORK_TREE`.
- P7: sweep row 62's commit lookup, called directly.
- P8: an index written by the person's git as version 4 with skipHash, or split.
- P9: a stand-in system file named by `GIT_CONFIG_SYSTEM`.

`gov close` itself was not run by the reviewer (a close-able fixture copies repository folders); it reaches these calls only through `run_checks`, which `gov check` exercised. The lead's scoped run covers the close's planted case.

## Findings

Classification (DEC-809): R6-1 no/fails open (row, unchanged); R6-2 yes/other (fixed); R7-1 yes/other; R7-2 no/other; R7-3 no/other. None fails the probe.

**R6-1 (first review; row): a lifted hook event given a value that is not a list in the repository's source is no finding**
- What was done: the repository's hooks source gave `postToolUse` an object instead of a list, while the template has it.
- What happened: the comparison skips a value that is not a list, so the event counts as absent, the exception applies and there is no finding; before this round the same state was `HOOKS_EVENT_DIFFERS`.
- What should have happened: the comparison flags it until the exception ends with W2-08.
- Ordinary work: no, because restoring the events with W2-08 copies the template's list entries, and an object where rulesync expects a list is a construction no honest edit makes.
- Consequence: fails open (the drift report only, and only while the exception lasts).

**R6-2 (first review; fixed): the lexical index's git calls read the person's configuration**
- What was done (at 110125ddda0b): a person's global `trace2.eventTarget`; `gov close`, `gov check`, `gov retrieve` on a throwaway project.
- What happened then: the lexical index's calls, W2-108's merged freshness calls among them, wrote the person's trace target; this ticket's planted `gov close` case was red on it.
- Now (e122beca7ef7): P1, every lexical start pinned (2 to 4 per step) in both placements, no target written; P2, `gov check` (5 git starts) and `gov retrieve` (5) all pinned, no trace; P9, the stand-in system file's targets never written pinned, while the unpinned control wrote 3 events each.
- Ordinary work: yes, because a person's trace setting is read by every unpinned git.
- Consequence: other (fixed).

**R7-1: a person's global `core.autocrlf`, global attributes file or global clean filter makes the whole index stale once (row; low)**
- What was done: a person with `core.autocrlf = true` in `~/.gitconfig` checked out a throwaway project (9 tracked files written with CRLF); a store built by the pre-fix code, then judged and refreshed by the fix, then judged by the older code again; in P3 the same for a global `core.attributesFile` and a global clean filter named by the repository's attributes (a stand-in for Git LFS's).
- What happened: the fix saw 9 of 9 files stale; until a refresh the lexical facet answered FACET_UNAVAILABLE and the index-freshness check would be red; after the refresh the same paths, flags, chunk texts and answers, nothing dropped; the older code then saw the fixed code's store as stale; chunk ids carry the blob id, so the next rebuild re-embeds every changed chunk.
- What should have happened: as it did (pinning is right), but sweep row 24 and the fix's message say "such a file … stale once": for such a person it is every text file the setting covers, and while two code versions share one store each sees the other's as stale.
- Ordinary work: yes, because `git lfs install` writes a global clean filter, and some people keep a global `core.autocrlf = true`.
- Consequence: other (fails closed once until `gov rebuild`; one re-index and re-embed; nothing lost).

**R7-2: sweep row 62's deferral lapsed with this merge; its commit lookup still reads the person's configuration (row; low)**
- What was done: the secrets filter's commit lookup (sweep row 62) called with the project's own commit id, under a pinned caller, with trace targets in `~/.gitconfig` and then in the XDG file; end to end, a tracked probe record holding a full commit id through refresh and `gov check`.
- What happened: the lookup's two git processes (`config --list`, `cat-file --batch-check`) ran unpinned (they drop every inherited git variable, the caller's pinning ones included) and wrote all three of the person's targets in each placement; the answer was right. End to end, the full id alone reached no lookup (row W2-L423's rule needs one of its keywords beside it). W2-107 merged here and has closed, yet row 62 still reads "after W2-107 merges".
- What should have happened: the row resolved now that its holder has closed: the lookup pinned with the person's partial-clone settings read as data, or the row marked open with its reason.
- Ordinary work: no, because the lookup is reached only when a scanned text holds that rule's keyword next to a full commit id.
- Consequence: other (trace events only; the lookup fails closed on any error).

**R7-3: R3-2's class now covers the lexical index (row; low)**
- What was done: a repository simulated as another owner's, marked safe only by `safe.directory = *` in the person's `~/.gitconfig`; a store built before the fix.
- What happened: pinned git refused ("detected dubious ownership"); freshness, search and refresh raised INDEX_GIT_FAILED and the index-freshness check exited 1 ("cannot be decided"); the path-map check reported TRACKED_PATHS_UNLISTED; the store was unchanged; the pre-fix code had answered "fresh".
- What should have happened: as it did (fails closed), or the person's `safe.directory` read as data.
- Ordinary work: no, because it needs a repository owned by another OS user, with `safe.directory` in the person's configuration (simulation only).
- Consequence: other (fails closed; nothing written or lost).

Notes (known, not this round's): N-7, `gov rebuild` writes a person's trace targets through the code index's three git calls (sweep rows 16 and 17; W2-56 holds the file); `gov close` does not rebuild. N-8, sweep row 63 waits on W2-87, which closed before this round.

Rows of the earlier reviews, unchanged by this round: R4-2 to R4-5, N-1, R5-1 to R5-4.

## Found sound

- The fix: see R6-2.
- Answers (P3, P3b): an ordinary configuration (sixteen common settings, among them `autocrlf=input`, `quotePath=false`, an alias shadowing `ls-files`, an excludes file covering tracked paths, `feature.manyFiles`; non-ASCII and tab file names) gives an identical key, listing, ids, digest and freshness pinned and unpinned; the unpinned control wrote 9 events per target.
- The repository's own configuration (P3): its `eol=crlf`, filter driver, `ident`, `info/attributes` and `core.autocrlf` still shape the pinned ids, which equal git's own in that repository.
- Index forms (P8): an index in version 4 with skipHash, or split, is read identically.
- Inherited variables (P6): `--git-path index` right in both trees; an inherited index of the root's own git directory kept, and its staged file listed and hashed; another tree's index, `GIT_DIR` and `GIT_WORK_TREE` cleared; the decoy unchanged; no trace written.
- The merge (DEC-895), both reviews: it differs from git's own merge only in the conflict hunk of `pathmap.py`, which is the integration branch's code plus this ticket's pinned environment on its one git call; `lexical.py` is the integration branch's plus the environment (now pinned); files only one side changed are identical to that side's; nothing dropped. The path-map check under every inherited `GIT_*` variable and the person's configuration gives the baseline's findings; an unlistable repository is never green.
- W2-107's and W2-108's merged code starts no git of its own (the cache starts only `gitleaks version`; the semantic index and the rebuild's counts start no process).
- H (DEC-971 item 3): exactly the two named events, skipped only when the template alone has them; every other one-sided event still a finding in either direction; a lifted event only in the repository's source still a finding; once back in both, compared as any other; output form unchanged; an adopted project unaffected; nothing else reads a hooks source.
- W2-72 (DEC-980 item 2): nothing lowered or removed, a control added; the exit-128 route reaches the failing `merge-tree --write-tree` alone; the seam goes red on a regression; it reaches no other test and nothing of the person's environment.

**Judgement: pass.** No finding is "yes" with "fails open" or "loses work"; R6-1, R7-1, R7-2 and R7-3 go to the Wave 3 hardening pass (DEC-801), or ride along in W2-05's next resume (DEC-802).
