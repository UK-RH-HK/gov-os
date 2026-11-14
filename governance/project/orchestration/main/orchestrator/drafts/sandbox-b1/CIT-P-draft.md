---
id: SANDBOX-1-B1-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-11-13
branch: none yet (draft in the CTO's scratch; the change lands by the CTO's route for kernel bytes)
base: 79159cd44c5b
head: none yet
ticket: none yet (no ticket is filed here; the CTO names it, DEC-974)
author: product-spec helper for the Wave 2 CTO
review: none yet (CAP-33: a reviewer who did not write it)
decisions_read: [DEC-1167, DEC-1128, DEC-1064, DEC-1065, DEC-836, DEC-1144, DEC-1092, DEC-158, DEC-159, DEC-161, DEC-963, DEC-1073, DEC-105, DEC-315]
decisions_carried: [DEC-1167, DEC-1064, DEC-1065, DEC-1144, DEC-963, DEC-1073]
owner_approval: none yet (CAP-33; to be written here before the merge)
state_class: EVIDENCE
---

# SANDBOX-1 B1: change-impact proposal (CIT-P) for the kernel template `brief.md`, with an optional extension to two role files

This change reads the worker brief template as the owner's DEC-1167 (7) decided: a worker started by `gov launch` writes only its own `$TMPDIR` and runs no
`gov retrieve`; its lead runs the search. It is a kernel change, so it goes through CIT-P (CAP-33): evidence, corroboration, independent review and the
owner's approval line before the merge. The **core** is one file, `brief.md` (six line edits). The **extension** adds the same reading to two role files
(five line edits) and is not recommended (section 4). The project files that carry the same rule (`facts.yaml`, `LEAD-w2-common.md`, `AUDITOR-common.md`)
are not kernel and are drafted in `README.md`.

## 1. What triggers the change

| # | Trigger | Source | State before |
|---|---|---|---|
| T1 | A worker brief names `/tmp/gov-os-lead-<W2>` or `.gov-runtime/scratch/<role>/`, which the worker's sandbox cannot write; scripts, pytest and scratch files fail | DEC-1167 (7) B1; `sandbox-package-20261113.md` §4: 41 returns (29 tickets), 130 stated minutes for `/tmp`; 9 returns, 34 minutes for `scratch/<role>/` | `brief.md` lines 17 and 40 name `{WRITE_TREE}/.gov-runtime/scratch/` |
| T2 | A sandboxed worker's `gov retrieve` comes back unranked or hangs 2-5 minutes; 399 sandboxed searches went unranked (11-09 to 11-13); hit@5 on the 138 falls 107 -> 95 without the reranker | DEC-1167 (7) R4; package §4 (14 returns, 34 minutes) and §5; DEC-1064 (2) | `brief.md` line 31 sends the worker to Read and Grep but never names its lead |
| T3 | DEC-836 (2) (every brief says use `gov retrieve`) and DEC-1064 (2) (sandboxed workers run none) conflict | W2-152's return (`log/W2-152-A5-resume-1112.json`) | no reading in the register (README section 6 drafts it) |
| T4 | The Write tool is refused for a path outside the worktree, `$TMPDIR` included; a worker's only way to write a script is Bash | returns of W2-124, W2-154, W2-172; DEC-1144 (7) (reviewers) | `brief.md` line 41 forbids a shell variable as a write target |

**Corroboration (CAP-33.a, .d).** The first source is the leads' own returns (168 scanned, `log/*.json`, counted by the package's script). The second is
independent of it: the owner's decision itself (DEC-1167 (7), 2026-11-13) and the workers' side in W2-175's and W2-11's returns, which name the same two
frictions in their `guard_refusals` rows ("Write tool, `.gov-runtime/scratch/check_fm.py` ... directory denied by permission settings"; "used `$TMPDIR`").

## 2. What changes: the core (lines verbatim)

Six edits in `brief.md`. Each rule line ends with its ACCEPTED decision ids in brackets (DEC-1073): DEC-1064, DEC-1065, DEC-1144 and DEC-1167 are ACCEPTED.


### K1: `template/governance/kernel/templates/brief.md`

**Before:**

```text
version: 1.0.0
```

**After:**

```text
version: 1.0.1
```

*Why:* Versioned promotion (CAP-33.d): a patch bump for a changed line.

### K2: `template/governance/kernel/templates/brief.md`

**Before:**

```text
| your scratch | {WRITE_TREE}/.gov-runtime/scratch/ |
```

**After:**

```text
| your temp folder | $TMPDIR (your session's own; the one folder outside your tree you may write) |
```

*Why:* Line 17 names the worktree's `.gov-runtime/scratch/` as the worker's scratch. A table line: outside the prose budget.

### K3: `template/governance/kernel/templates/brief.md`

**Before:**

```text
Ask memory first: outside the sandbox {CMD:retrieve} "<which decision governs X | where is Y implemented>"; inside it, the Read and Grep tools [DEC-1065]; grep the register only by id.
```

**After:**

```text
Ask memory first: outside the sandbox {CMD:retrieve} "<which decision governs X | where is Y implemented>"; inside it, the lead's bundle above, then the Read and Grep tools [DEC-1064, DEC-1065, DEC-1167]; grep the register only by id.
```

*Why:* Line 31 stays 'outside the sandbox: gov retrieve' (DEC-836 (2)) and names the bundle for a sandboxed worker (R4).

### K4: `template/governance/kernel/templates/brief.md`

**Before:**

```text
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way [DEC-1065].
```

**After:**

```text
No `gov retrieve` in the sandbox, and no `gov context`: a launched worker searches with the Read and Grep tools, and searches again once the same way; a question they leave open goes under `unresolved`, and your lead answers it between rounds with its own `gov retrieve` [DEC-1064, DEC-1065, DEC-1167].
```

*Why:* Line 33 already forbids `gov retrieve` in the sandbox (W2-128 row 6 pins it); it gains the way a worker's question reaches its lead's search. Keeps the words 'retrieve', 'sandbox' and the negation that `test_row_6_...` looks for.

### K5: `template/governance/kernel/templates/brief.md`

**Before:**

```text
- Anything longer than one line goes in a script file under {WRITE_TREE}/.gov-runtime/scratch/, run with `bash <file>` or `python3 <file>`.
```

**After:**

```text
- Anything longer than one line goes in a script file in `$TMPDIR` (your session's temp folder; never a `/tmp/gov-os-lead-*` or `.gov-runtime/scratch/<role>/` path), run with `bash <file>` or `python3 <file>`. Write it with Bash (`cat > "$TMPDIR/<name>.py" <<'EOF'`), not the Write tool, which is refused outside your tree: the stated route [DEC-1144, DEC-1167].
```

*Why:* Line 40 sends scripts to the worktree's scratch, where the Write tool is refused (W2-175, W2-11, W2-176, W2-179, W2-86). The Write tool is also refused for `$TMPDIR` (W2-124, W2-154, W2-172 rows), so the line states the Bash route up front: DEC-1144 (7) gives it to reviewers as 'the stated route, not a workaround'; here it is read for every launched worker (an open point, named in the README).

### K6: `template/governance/kernel/templates/brief.md`

**Before:**

```text
- Use literal paths, never a shell variable or `$(…)` as a write target; name the folder a listing or search starts at.
```

**After:**

```text
- Use literal paths, never a shell variable or `$(…)` as a write target (`$TMPDIR` above is the one exception); name the folder a listing or search starts at.
```

*Why:* Line 41 would contradict K5 (`$TMPDIR` is a shell variable as a write target).

## 2b. The extension (optional, not recommended): two role files

Five edits. Same rule for the ids: DEC-963, DEC-1064, DEC-1065 and DEC-1167 are ACCEPTED.


### K7: `template/governance/kernel/templates/role-test-designer.md`

**Before:**

```text
version: 1.0.1
```

**After:**

```text
version: 1.0.2
```

*Why:* Versioned promotion (CAP-33.d).

### K8: `template/governance/kernel/templates/role-test-designer.md`

**Before:**

```text
3. Ask memory only of the integration store: outside the sandbox {CMD:retrieve}; inside it, the Read and Grep tools on w2/integrate [DEC-963, DEC-1065].
```

**After:**

```text
3. Ask memory only of the integration store: outside the sandbox {CMD:retrieve}; inside it, the lead's bundle in your brief, then the Read and Grep tools on w2/integrate [DEC-963, DEC-1064, DEC-1065, DEC-1167].
```

*Why:* A designer's search is the lead's, run as `independent-test-designer` (the role filter drops the ticket's implementation), then Read and Grep on w2/integrate.

### K9: `template/governance/kernel/templates/role-research.md`

**Before:**

```text
version: 1.0.1
```

**After:**

```text
version: 1.0.2
```

*Why:* Versioned promotion (CAP-33.d).

### K10: `template/governance/kernel/templates/role-research.md`

**Before:**

```text
3. Find what the repository already knows first (outside the sandbox {CMD:retrieve}; inside it, the Read and Grep tools [DEC-1065]); then external sources (WebSearch, WebFetch), each cited by URL.
```

**After:**

```text
3. Find what the repository already knows first (outside the sandbox {CMD:retrieve}; inside it, the bundle in your brief, then the Read and Grep tools [DEC-1064, DEC-1065, DEC-1167]); then external sources (WebSearch, WebFetch), each cited by URL.
```

*Why:* The research session is sandboxed too (DEC-161); the session that started it (its lead or the CTO) supplies the bundle.

### K11: `template/governance/kernel/templates/role-research.md`

**Before:**

```text
5. Write only in {PATHS} and your scratch; install only into a venv inside your experiment folder.
```

**After:**

```text
5. Write only in {PATHS} and your `$TMPDIR` (your session's own temp folder); install only into a venv inside your experiment folder [DEC-1167].
```

*Why:* 'Your scratch' is the other place a role file names a worker's temp folder.

No other kernel file changes: no hook, no skill, no schema, no `keys.yaml`, and the guard does not change.

## 3. sha256 of every file, before and after

Core:

| File | Before (sha256) | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/templates/brief.md` | `004ce0fc8f09dcc89a8ecda0b0a0ef813737323719aac3e469a1eac6ee4cfe6d` | `578ae9e10d7b7ea9027d1ef8ceec8c36a13fee0806a2165bb7d2f0047abaa645` | 62 -> 62 |

Extension (only if chosen):

| File | Before (sha256) | After (sha256) | Lines |
|---|---|---|---|
| `template/governance/kernel/templates/role-test-designer.md` | `c1f449fbe338fc32ebc583e7e6ce57afb690bf4339cd7bf41b30a0f52fb8b990` | `d09373dc2453811676e4d01583ca15e3b8e92631c9dbd3c7abece3e247c874a9` | 31 -> 31 |
| `template/governance/kernel/templates/role-research.md` | `fc41bfc1cf3bd5576080739b16cac992bb9ae912a6519b74b560b6d3af0c5799` | `5cfafa857bc1fd7e2bfe5071111eb113e2152c5fed172ecbe3e2e5dc85ad2aae` | 25 -> 25 |

Byte copies (rewritten by the copies ACT, not by this change; each takes its kernel file's "after" sha256): `.claude/templates/brief.md` (core; before
`004ce0fc8f09dcc89a8ecda0b0a0ef813737323719aac3e469a1eac6ee4cfe6d`, after `578ae9e10d7b7ea9027d1ef8ceec8c36a13fee0806a2165bb7d2f0047abaa645`); `.claude/templates/role-test-designer.md` and `.claude/templates/role-research.md` (extension; before and after as
the two kernel rows). The composed copies (`.claude/agents/independent-test-designer.md`, `.claude/agents/research.md` and their `.rulesync/subagents/` and
`template/.rulesync/subagents/` twins, extension only) take their shas when the ACT runs.

**For `kernel_gate.py`** (the owner's approval list `kernel-approved.txt`; `<sha256> <path> <DEC> <note>`; the approving decision id is the owner's, to be filled):

```text
578ae9e10d7b7ea9027d1ef8ceec8c36a13fee0806a2165bb7d2f0047abaa645 template/governance/kernel/templates/brief.md DEC-<the approving decision> SANDBOX-1 B1 core (DEC-1167 (7))
# extension only:
d09373dc2453811676e4d01583ca15e3b8e92631c9dbd3c7abece3e247c874a9 template/governance/kernel/templates/role-test-designer.md DEC-<the approving decision> SANDBOX-1 B1 extension (DEC-1167 (7))
5cfafa857bc1fd7e2bfe5071111eb113e2152c5fed172ecbe3e2e5dc85ad2aae template/governance/kernel/templates/role-research.md DEC-<the approving decision> SANDBOX-1 B1 extension (DEC-1167 (7))
```

## 4. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now, the core only** (recommended) | Merge the six `brief.md` edits after review and the owner's approval line; the CTO's copies ACT rewrites one byte copy, `.claude/templates/brief.md`; the project files (README) apply beside it | One kernel file, six line edits; one narrow independent check of the lines; one copies ACT. Tests: no new red in the suites run (base and core both show the same 5 reds that were there before: W2-128 row 8 x2, W2-152 S10, W2-175 S7 for `role-cto` and `role-lead`); one `TEMPLATE_COPY_DIFFERS` finding until the copies ACT |
| Apply now, core and extension | The same, plus five line edits in `role-test-designer.md` and `role-research.md` at 1.0.2 | Everything above, plus eight more copies (two byte, six composed) and the revision of tests that pin the role templates: nine new reds in the suites run: W2-175 S5 pins the role templates' version at 1.0.1 and S7 pins their head sha256 in `docs/changes/W2-175-CIT-P.md` (4 cases, `role-research` and `role-test-designer`), and W2-153's role-source cases compare the composed `.rulesync` copies (5 cases); each needs a test designer's revision (DEC-1156 (7)) or the copies ACT, and the ticket must name `template/.rulesync/subagents/*` |
| Defer | Keep the template as it is; leads carry the rule in each part's text (the CTO's `$TMPDIR` line, as in W2-182 run 4) | The two frictions continue (about 20 stated minutes a day of lead and worker time, package §4). `brief.md` keeps naming `scratch/` and a retrieve line that DEC-1064 (2) forbids; every lead must remember the line |
| Re-baseline | Rewrite `brief.md` around a sandboxed and an unsandboxed form and have `gov brief` pick one by how the role is launched | A larger change to `gov brief` and its W2-128 and W2-152 suites (product code), and the owner's decision on the form first |

(DEC-105's three options are apply, defer and re-baseline; "apply" has two sizes here, and the recommendation is the smaller.)

## 5. Impact

| Area | Impact |
|---|---|
| Kernel files | core: `brief.md` 1.0.0 -> 1.0.1. Extension: `role-test-designer.md` 1.0.1 -> 1.0.2 and `role-research.md` 1.0.1 -> 1.0.2. No other kernel file, and no guard, hook or schema |
| Generated copies | core: one byte copy. Extension: eight more. Until the copies ACT, `TEMPLATE_COPY_DIFFERS` names each stale copy (core: one finding, `.claude/templates/brief.md`; with the extension, three, adding `role-research.md` and `role-test-designer.md`; the composed copies also differ for the extension) |
| Tests | core: no new red in the 7 suites run (362 passed, the same 5 reds as at the base) nor in `tests/unit/adapters` (131 passed). Extension: nine new reds (README section 10) |
| Briefs | every `gov brief` worker brief changes by the same lines; the lead's hand-written briefs follow `LEAD-w2-common.md` (README L1-L4) |
| Decisions | none changed; README section 6 gives the one-line reading of DEC-836 (2) with DEC-1064 (2) for the register |
| Open points | README section 9: points 1 (the Bash route for every worker, K5 and K6) and 3 (`heavy_slot.sh` in the sandbox, F2 and F3) are the two the owner may want to rule on |

## 6. Independent review and approval

Not yet reviewed. The reviewer (a fresh read-only session) should check: each "before" text is byte-identical to the base file; each "after" rule line ends with
ACCEPTED ids only (DEC-1073); `brief.md` still carries the pytest marker form with `HOME`, and the "no `gov retrieve` in the sandbox" line with its negation
(`tests/acceptance/W2-128/test_w2_128_rows.py::test_row_6_...`); the prose budgets in README section 5 hold; and the sha256 above equal the files at the head.

The owner's approval line (CAP-33) is written here before the merge: `owner_approval:` in the front matter.
