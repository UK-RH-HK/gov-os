---
type: probe
task: DAEO-0z8c
reviewer_session: d26b718c-3d60-43bc-9846-0594d19fbfc5
implementer_session: 8f696f48-3724-45bd-8ef2-dcc024b3ff5f
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ecbdf689f283cab6b7068cdd2b93d46f449d8058
---

# Probe of W2-05 (DAEO-0z8c) round 3 at ecbdf689f283

**Probed:** head ecbdf689f283 on `w2/W2-05`: this resume's own commits (batch 1 8b8a3baa347a; batch 2 55586fded9de, 147bed88be33, adb61a23cf83, 0ff79288c72e; the W1-02 revision a8b9cd07e1ae; the repair batch 8383bea1da69) and the ticket's whole change against `w2/integrate`. It is the review of F-A's fix that DEC-804 item 1 named, and of batches 1 and 2 and the W1-02 revision. The code under test is this worktree's `src/` (DEC-732): `gov.__file__` is `/home/usain/gov-os-worktrees/W2-05/src/gov/__init__.py`.

**Who:** a fresh, read-only QA engineer (role `independent-auditor`), started through `gov launch`, sandboxed, `--effort max`. Its only repository writes were the sandbox check's git object and index refresh. A first launch on f217353e59fa was stopped after about six minutes, before any finding, because the repair batch was to change the head; this record is the second launch's.

**Method:** it read the ticket, DEC-710, 580, 777, 783, 801, 802, 804, 805, 807, 808, 822, 951 and 959, rows W2-L160 and W2-M161, ADR-0001, the round-1 and round-2 records, each commit above and the change against `w2/integrate`. It ran ten probes in its temporary folder against this worktree's `src/`, with bytecode writing off:
- P1: F-A and P-1 through lefthook 2.1.15 with this repository's `lefthook.yml`, in five shapes (main plain, main `-a`, main `-- <path>`, linked plain, linked `-a`);
- P2: staged-secrets; P3: the freeze look-up, six ways; P4: containment with no git found;
- P5: the real hook programs with a hanging repository setting; P6: who authors the close's commits;
- P7: `_started`'s environment; P8: the bisect step's environment (run once more as a Python file after a guard refusal of its shell form; it bears only on package I's addition below);
- P9: the staged view under P-1 against round 2's environment; P10: adapter-portability's hooks comparison.

Suites were not re-run (DEC-959 item 1); the lead's verification is recorded beside this record in the lead's return.

**Verdict: pass.** Classification (DEC-809): R3-1 yes/fails open, feature-gated (DEC-803: the hooks are off until W2-08; the owner's P-1 as decided), so it goes to the owner as a package and an entry criterion of W2-08, not a round; R3-2 no/fails open (a Wave 3 row); R3-3 no/other (a row). The known packages: H yes/other, P-W2-05-DRIFT-BASE yes/other, I yes/other (fails closed). No finding against this ticket's work is "yes" with "fails open" or "loses work" outside a feature that is switched off.

## Findings

### R3-1: P-1 gives a declared check the default index, which under `commit -a` and `commit -- <path>` is not what is committed (package; medium)
- **What was done:** a declared G1 check, run by lefthook's pre-commit, asked git in the project root what is staged, in five commit shapes; in one plain hook the same question was asked with P-1's environment and with round 2's.
- **What happened:** in a plain commit (main tree and linked worktree) the check saw exactly the committed file. Under `commit -a` (both trees) and `commit -- notes.md` it saw nothing staged, and could not compute the index's tree because the commit holds the lock; the commit still carried the change. Round 2's environment saw the committed file in all three shapes.
- **What should have happened:** this is P-1 as accepted (DEC-804 item 3). But the sweep record and the helper's description say such a git "finds the root's own index by itself", which is not true of the index being committed in those two forms.
- **Today:** no kernel check reads what is staged; the staged-secrets gate keeps git's own index and refuses (P2); the hooks are off until W2-08.
- Ordinary work: yes, because `git commit -a` is ordinary, and a check that reads what is staged is an ordinary kind of check for an adopted project to declare once W2-08 installs the hooks.
- Consequence: fails open
- **Routing:** the owner's P-1 implemented exactly, and the risk is feature-gated (DEC-803): a package to the owner (DEC-105), with W2-08 as the ticket whose entry criterion it becomes.

### R3-2: the pinned freeze look-up misses a freeze in a linked worktree when git refuses the repository for its owner (row; low)
- **What was done:** `gov pause`'s mirror was written from the main tree; the person's configuration marked every repository safe (`safe.directory`); another owner was simulated with git's own test switch, added to the helper's pinned variables; an orchestrator's Write was judged in the worktree and in the main tree.
- **What happened:** git with the person's configuration answered; pinned git refused ("detected dubious ownership"). The look-up fell back to the tree's own path, missed the mirror, and allowed both Writes. Without the simulated owner both Writes were refused ("frozen: all writes denied").
- **What should have happened:** a look-up that git refuses should be refused like a missing git or a time-out, or the reader and the writer should use the same git and configuration. The fallback itself is W1's code; every containment call in such a setup also fails and leaves a finding.
- Ordinary work: no, because it needs a repository owned by another OS user, with `safe.directory` in the person's configuration (a container or a shared mount); shown by simulation only.
- Consequence: fails open

### R3-3: the Bash bookkeeping's git that hangs (answers P-W1-02-CHILD) (row; low)
- **What was done:** the project's own configuration named a file-system monitor program that never ends; the template's PreToolUse and then PostToolUse programs were run on an orchestrator's `ls`.
- **What happened:** the decision allowed the call (the look-up does not use the monitor). The before-snapshot timed out at containment's 10 s with the finding "before-snapshot failed: … timed out after 10 seconds"; the hook allowed the call at 10.2 s. The post-hook timed out the same way: exit 2, with the finding "containment: check failed: … timed out after 10 seconds". The monitor program, a child of git, was still running after each hook.
- **What should have happened:** as W1 decided (DEC-126), a snapshot failure is recorded and does not block, and it was recorded; this is not a fail-open under DEC-580. The leftover process should end with its git (containment's git in a process group of its own, ended whole at its limit).
- Ordinary work: no, because it needs the repository's own configuration to make git's status hang, which every `git status` the person runs would show at once.
- Consequence: other

## Known packages, classified

- **H** (adapter-portability over this repository after ACT 1: `postToolUse` and `postToolUseFailure` only in the template's hooks source; P10 confirms exactly those two findings). Ordinary work: yes, because adapter-portability runs over this repository in every check. Consequence: other.
- **P-W2-05-DRIFT-BASE** (the matcher-drift case plants on `postToolUseFailure`, now an event difference; a matcher change on an event both sources hold is still red, P10). Ordinary work: yes, because the case runs in every suite run. Consequence: other.
- **I** (the close's and the nightly's test runs pinned, so a test that commits without an identity of its own fails). Addition: the nightly's bisect step runs the tests unpinned while the night's runs are pinned, so such a red would pass at every bisect step (reasoned, not reproduced). Ordinary work: yes, because every close's test run is now pinned. Consequence: other (fails closed).

## Notes (no finding)

- N-1: adapter-portability compares events and matchers only (DEC-805 as its tests specify it). Ordinary work: no, because the template's hooks source changes only through an owner-approved kernel change. Consequence: other.
- N-2: the helper keeps the SSH transport and the identity, and drops the HTTPS transport's variables; unchanged since round 1. Ordinary work: no, because such settings usually sit in the person's configuration, which the push reads. Consequence: other (fails closed).
- N-3: the helper's check of whether an inherited index is git's own starts git by name; in a hook only if the session itself inherited an index. Ordinary work: no, because a session does not inherit an index in ordinary work. Consequence: other.
- N-4 (cosmetic): sweep row 63 omits `measure.py`'s interpreter probe (starts no git; a held file); W1-02's README describes "the guard keeps no deadline of its own" as the message for an allowed call, where it is the message for an unanswered call, as before; nothing became unreachable.

## Found sound

- **F-A and P-1 (P1, five shapes):** no `GIT_INDEX_FILE`, `GIT_DIR`, `GIT_WORK_TREE` or `GIT_COMMON_DIR` reached the check; the check's own repository held its one commit and file; each commit landed with exactly what was staged, the old head as parent, no other ref moved; the index matched the commit with no missing object; the other worktree's index unchanged; the settings file byte-identical after `lefthook install`.
- **Staged-secrets (P2):** `-a` in both trees and `-- <path>` refused with SECRET_STAGED; a foreign index refused, naming it; a clean scan found 0.
- **Freeze look-up (P3):** no git found: refused at 0.0 s; hang: refused at 15.02 s, no rev-parse left running; a stand-in `git` first on `PATH` never started; inherited trace or git-directory variables and a planted global trace target wrote nothing; the mirror equals `gov pause`'s in both trees.
- **Containment with no git (P4):** the snapshot and the post-check raise; `judge_commits` raises.
- **The close:** `_started` passed none of 14 planted caller `GIT_*` variables, pinned the configuration and kept every other key; the collection run goes through it (P7). The authors of the batch and repair-ticket commits are unchanged from the base in all eight shapes (P6). The bisect step got only git's own variables and `GIT_NO_LAZY_FETCH` (P8).
- **Rows 39 to 41 and the nightly:** only the environments differ from `w2/integrate`; the graft, shallow and lazy-fetch settings are kept.
- **The sweep:** 63 process starts under `src/gov`, each mapped to a row or the "starts no git" list; the held files unchanged in this resume.
- **The W1-02 revision and the repair:** test functions, parameters and labels unchanged; DEC-580's reason and the 19 to 26 s window kept on slow steps the 15 s does not cover; the look-up cases held at 14.5 to 21 s; no `PATH` stand-in remains; the order case's construction only changed.
