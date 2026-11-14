# SANDBOX-1 (b), B1 and R4: the exact edits that make every worker brief say it (DRAFT, nothing applied)

Prepared 2026-11-13 by a product-spec helper for the Wave 2 CTO. Read at `w2/integrate` `79159cd44c5b` (the files below are unchanged since
`95a55bfcac9b`; checked with `git diff`). **Nothing in the repository was changed**; this folder is the only thing written. Owner's decision:
DEC-1167 (7) (ACCEPTED, 2026-11-13) and its source, `.gov-runtime/scratch/orchestrator/drafts/sandbox-package-20261113.md` §4, §6.1 (R4), §6.2.

**The rule every edit states, in one sentence.** A worker started by `gov launch` writes only its own session folder, `$TMPDIR` (the launcher's
`/tmp/gov-launch-*`): its brief never names `/tmp/gov-os-lead-<W2>` or `.gov-runtime/scratch/<role>/`; and it runs no `gov retrieve` (DEC-1064 (2)):
its lead runs it, as the worker's role, and puts the bundle in the brief or answers between rounds (R4).

## 0. The edits at a glance

| Id | File | Class | What |
|---|---|---|---|
| F1-F4 | `governance/project/facts.yaml` | project | the empty `HOME` moves to `$TMPDIR`; the two pytest forms gain `heavy_slot.sh` and `PYTHONUSERBASE`; a comment on `retrieve` |
| L1-L4 | `governance/project/briefs/LEAD-w2-common.md` | project | DEC-836's line read for sandboxed workers; the temp-folder line; one new bullet (the workers' temp folder and search); the status line |
| A1-A2 | `governance/project/briefs/AUDITOR-common.md` | project (found beyond the task) | a launched auditor's search and temp folder |
| K1-K6 | `template/governance/kernel/templates/brief.md` | **kernel, core (CIT-P)** | the lines are verbatim in `CIT-P-draft.md` §2 |
| K7-K11 | `.../role-test-designer.md`, `.../role-research.md` | **kernel, extension (CIT-P), optional** | `CIT-P-draft.md` §2b; **not recommended** (section 4) |
| O1 | `governance/project/prompts/w2-orchestrator.md` | optional, the CTO's prompt | DEC-836's line at :167 |
| R | the register | text for the CTO to record | the one-line reading of DEC-836 (2) with DEC-1064 (2) (section 6) |

How to apply (when the owner says so): F, L, A and O1 are `Edit` calls with the old text below as `old_string` (each occurs exactly once at the base,
checked by script). The kernel lines only after the owner approves the CIT-P and `kernel-approved.txt` has the new sha256 line (CIT-P §3). The
sha256 of each file before and after is in section 5. The copies ACT is section 7.

**Search done** (grep over the named folders, then the rest of `governance/project/`): `/tmp/gov-os-lead`, `TMPDIR`, `gov retrieve`, `scratch/`,
`retrieve`, `sandbox`, `/tmp` in `governance/project/facts.yaml`, `governance/project/briefs/`, `template/governance/kernel/templates/`,
`.gov-runtime/scratch/orchestrator/briefs/`; beyond the folders named: `governance/project/prompts/`, `template/governance/kernel/skills/`,
`tests/acceptance/*/README.md`, `src/gov/brief/`. Section 8 lists the lines found that need no edit and why.

## 1. `governance/project/facts.yaml`

`facts.yaml` is filled into every `gov brief` worker brief (`{CMD:...}` and `{EMPTY_HOME}`). It had one path that names a worker's scratch
(`empty_home`, in the worktree's `.gov-runtime/scratch/`) and two pytest forms (`pytest_folder`, `unit_tests`) that carry neither the slot wrapper
nor `PYTHONUSERBASE` nor any temp folder. `TMPDIR` is deliberately **not** set in them: a launched worker's `$TMPDIR` is already the launcher's own,
`env` passes it on, and a form that sets it is how `/tmp/gov-os-lead-*` got into briefs.


### F1: `governance/project/facts.yaml`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  empty_home: '{WRITE_TREE}/.gov-runtime/scratch/empty-home'
```

**New text:**

```text
  # A launched worker's sandbox writes only its own $TMPDIR (the launcher's /tmp/gov-launch-*): its forms name `$TMPDIR`,
  # never /tmp/gov-os-lead-<W2> or .gov-runtime/scratch/<role>/ (DEC-1167 (7), SANDBOX-1 (b) B1). The shell expands it.
  empty_home: '$TMPDIR/empty-home'
```

**Reason:** The only temp or scratch path a worker template is filled with. It names the worktree's `.gov-runtime/scratch/`, where a launched worker's Write tool is refused (34 stated minutes, 9 returns); it moves to the session's `$TMPDIR`.


### F2: `governance/project/facts.yaml`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  pytest_folder:
    run: 'env HOME={EMPTY_HOME} PYTHONPATH={WRITE_TREE}/src python3 -m pytest {FOLDER} -q 
```

**New text:**

```text
  pytest_folder:
    run: 'bash {TOOLS}/heavy_slot.sh env HOME={EMPTY_HOME} PYTHONUSERBASE=/home/usain/.local PYTHONPATH={WRITE_TREE}/src python3 -m pytest {FOLDER} -q 
```

**Reason:** The pytest line every worker brief copies. It gains the standing slot wrapper (every pytest through `heavy_slot.sh`; the CTO's per-part boilerplate carries it today) and `PYTHONUSERBASE` (W2-11's brief gap: with an empty `HOME` the whole-folder form found no pytest). `TMPDIR` is not set: the worker's own `$TMPDIR` is inherited through `env`, so the form never names `/tmp/gov-os-lead-*`. The rest of the line (marker form, `-p no:cacheprovider`, retention) is unchanged.


### F3: `governance/project/facts.yaml`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  unit_tests:
    run: 'env HOME={EMPTY_HOME} PYTHONPATH={WRITE_TREE}/src python3 -m pytest {UNIT_TEST_PATH} -q 
```

**New text:**

```text
  unit_tests:
    run: 'bash {TOOLS}/heavy_slot.sh env HOME={EMPTY_HOME} PYTHONUSERBASE=/home/usain/.local PYTHONPATH={WRITE_TREE}/src python3 -m pytest {UNIT_TEST_PATH} -q 
```

**Reason:** The same two additions for a worker's own unit tests (a product-spec, engineer or designer session runs it).


### F4: `governance/project/facts.yaml`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  retrieve:
    run: 'gov retrieve --root {STORE_TREE} "{QUESTION}"'
```

**New text:**

```text
  retrieve:
    # A session in the launch sandbox does not run this: its lead does, as the worker's role (DEC-1064 (2), DEC-1167 (7), R4).
    run: 'gov retrieve --root {STORE_TREE} "{QUESTION}"'
```

**Reason:** Comment only. The row stays (the lead, the CTO and an unsandboxed worker run it), but a maintainer sees that a sandboxed worker must not. The command table of a worker brief still lists the row; the brief's own line says 'outside the sandbox' (E-brief-4).


**The check forms are unchanged** (`check: python3 -m pytest --version`, `gov retrieve --help`): only `run` changes. `facts.schema.json` accepts
all four edits (`gov.check.schema` and the W2-152 facts cases on the edited tree: `gov.check.schema` was not run to the end (it waited for a heavy slot for over 10 minutes); the W2-128 and W2-152 facts cases, which validate `facts.yaml` against `facts.schema.json`, pass on the edited tree). A real `gov brief engineer DAEO-5y8d` on the edited
tree fills with no placeholder left (the engineer brief of W2-182; diff of the two renderings: lines 12, 36, 39, 41-42, 48-49 only).

## 2. `governance/project/briefs/LEAD-w2-common.md`

The common lead brief is built into every lead's brief (`build_lead_brief.py`). Its four worker lines: L1 (line 30, DEC-836's `gov retrieve`), L2
(line 47, the temp folder: the source of the 130-minute class), L3 (new, after line 99), L4 (line 199, the status line). Lines kept as they are because
a test pins them: line 31 (P-R1: `P-R1`, `gov retrieve`, `drop unread`) and line 35 (`no store`, `rebuild`, `STORE_MISSING`), both in
`tests/acceptance/W2-11/test_w2_11_brief_gaps.py`. The new bullet uses only the keys the builder fills (`{W2}`, `{ID}`).


### L1: `governance/project/briefs/LEAD-w2-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
**DEC-836, memory used:** every worker brief you write tells its agent to use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 -m gov.cli.main retrieve "<question>" --json`) for what it needs to know before reading files at random; your return says, per worker, whether its brief said so and whether its log shows it used it.
```

**New text:**

```text
**DEC-836, memory used (read with DEC-1064 (2) and DEC-1167 (7)):** every worker brief you write tells its agent to use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 -m gov.cli.main retrieve "<question>" --json`) for what it needs to know before reading files at random. **A worker started by `gov launch` runs none:** in the sandbox its search comes back unranked or hangs, so its brief says to use your bundle, then Read and Grep, and you run the search for it (the bullet after "Your return names which workers ran sandboxed"). An unsandboxed worker runs `gov retrieve` itself. Your return says, per worker, whether its brief said so and whether its log shows it used it (a sandboxed worker: whether its brief carried your bundle).
```

**Reason:** Line 30 tells every worker brief to use `gov retrieve`, the DEC-836 (2) wording that conflicts with DEC-1064 (2) for a sandboxed worker. Only its first sentence changes; the search-again-once, batch and code-graph sentences stay.


### L2: `governance/project/briefs/LEAD-w2-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  - **Your temp folder:** set `TMPDIR=/tmp/gov-os-lead-{W2}` for every suite run and worker. Where `gov launch`'s sandbox sets its own temp folder, keep that one and count it.
```

**New text:**

```text
  - **Your temp folder:** set `TMPDIR=/tmp/gov-os-lead-{W2}` for your own suite runs. A worker started by `gov launch` keeps the sandbox's own `$TMPDIR` (the launcher's `/tmp/gov-launch-*`, the one folder outside its tree it can write): never set `TMPDIR` for it, never name `/tmp/gov-os-lead-{W2}` or `.gov-runtime/scratch/<role>/` to it (its sandbox refuses both), and count its folder in your budget (DEC-159, DEC-1167 (7)). A worker in the old launch form (no sandbox) may use `/tmp/gov-os-lead-{W2}`.
```

**Reason:** The source of the 130-minute class: 'for every suite run and worker' makes leads write `/tmp/gov-os-lead-<W2>` into worker briefs, a folder the worker's sandbox cannot write (41 returns, 29 tickets). The last sentence of the old line ('keep that one and count it') is kept in substance.


### L3: `governance/project/briefs/LEAD-w2-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  - **Your return names which workers ran sandboxed and which did not, and why.**
```

**New text:**

```text
  - **Your return names which workers ran sandboxed and which did not, and why.**
  - **What every launched worker's brief says about its temp folder and its search (owner, DEC-1167 (7): SANDBOX-1 (b), B1 and R4).** In the sandbox a worker writes only its own `$TMPDIR` (the launcher's `/tmp/gov-launch-*`) outside its tree, and its own `gov retrieve` comes back unranked or hangs (DEC-1064 (2)). Put this in every worker brief you write by hand; `gov brief` carries it from `brief.md`.
    - **Temp folder:** scripts, scratch files and pytest use `$TMPDIR` (the worker's command table gives the pytest form, with `heavy_slot.sh`). The brief never names a `/tmp/gov-os-lead-*` path or a `.gov-runtime/scratch/<role>/` path to a launched worker, a test designer's README run line included: its Write tool is refused there. A script goes in with Bash (`cat > "$TMPDIR/<name>.py" <<'EOF' ... EOF`), not the Write tool, which is refused for a path outside the worktree: the stated route, as DEC-1144 (7) gives reviewers.
    - **Search:** you run `gov retrieve` for the worker, unsandboxed and ranked, as the worker's role: for each question its brief rests on, `PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 -m gov.cli.main retrieve "<question>" --role <worker role> --ticket {ID} --json`, and once more in your own words for one that did not answer (DEC-1092 (1)). Put the bundle (path, lines, text) in the brief's "What the lead knows" note, cut to what the question needs; one too long for the brief's prose budget goes in a file you write in the worker's tree, named in the note. The brief tells the worker: use the bundle, then Read and Grep; when they do not answer, say "not found" and list the question under `unresolved`. Between rounds you answer each such question the same way (a resumed worker's brief gets the new bundle). A test designer's bundle goes through P-R1 before it goes in the brief.
```

**Reason:** The common lead brief's worker lines (B1 and R4). One new bullet, placed where the launch form and the sandbox are described. `--role` makes `gov retrieve` filter the bundle by the worker's `role_paths` (DEC-1065 (2), live in `src/gov/retrieve/command.py`), so the lead's own unfiltered view never reaches a designer or an engineer.


### L4: `governance/project/briefs/LEAD-w2-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
- **Every status:** the guard read refusals met (DEC-849), and per worker whether its brief told it to use `gov retrieve` and whether it did (DEC-836).
```

**New text:**

```text
- **Every status:** the guard read refusals met (DEC-849), and per worker whether its brief told it to use `gov retrieve` and whether it did (DEC-836); for a worker in the sandbox, whether its brief carried your bundle (DEC-1167 (7)).
```

**Reason:** DEC-836 (3)'s usage count for a sandboxed worker is now the bundle, not the worker's own search.


## 3. `governance/project/briefs/AUDITOR-common.md` (beyond the task's three files)

A launched `independent-auditor` is sandboxed (DEC-158, DEC-161), and this file goes "word for word" into its brief (its own line 3). It told the
auditor to run `gov retrieve` and to set `TMPDIR` to a folder of its own; both are the two frictions.


### A1: `governance/project/briefs/AUDITOR-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
- Use `gov retrieve` for what you need to know, and say in your report which questions it answered. When a bundle does not answer, or your finding may rest on an incomplete answer, search once more in your own, different words before you rely on it; two searches in all (DEC-1092 (1)).
```

**New text:**

```text
- Search through your brief: the bundle your lead put in it is the lead's `gov retrieve`, ranked (yours would come back unranked or hang in the sandbox, DEC-1064 (2), DEC-1167 (7)); then the Read and Grep tools. Say in your report which questions the bundle answered. When it does not answer, or your finding may rest on an incomplete answer, search once more in your own, different words before you rely on it; two searches in all (DEC-1092 (1)); a question that stays open goes under `unresolved` for your lead.
```

**Reason:** The auditor brief, written word for word into every launched auditor's brief, tells a sandboxed worker to run `gov retrieve` itself. Found by the grep over `governance/project/briefs/`; the task named only the common lead brief.


### A2: `governance/project/briefs/AUDITOR-common.md`

**Old text** (occurs once; the Edit tool's `old_string`):

```text
  - Set `TMPDIR` to a folder inside it, and keep pytest's own retention (three base folders), never a per-run `--basetemp`.
```

**New text:**

```text
  - Keep your sandbox's own `$TMPDIR` (the launcher's `/tmp/gov-launch-*`, the one folder outside your tree you can write; never set it elsewhere, never name a `/tmp/gov-os-lead-*` path), and keep pytest's own retention (three base folders), never a per-run `--basetemp`.
```

**Reason:** 'Set TMPDIR to a folder inside it' sends a launched auditor to a folder its sandbox cannot write.


## 4. The kernel templates (CIT-P): core and extension

The grep found the two frictions in **one** kernel template, `brief.md` (lines 17, 31, 33, 40, 41): K1-K6, the **core**. Two role files also mention a
search or a scratch, K7-K11, the **extension**: `role-test-designer.md:12` and `role-research.md:12, :14`. They already say "inside the sandbox: the Read and
Grep tools"; they do not tell a worker to run `gov retrieve` in the sandbox, and "your scratch" names no path. The extension only adds "the lead's
bundle" and `$TMPDIR` to them. **Recommendation: the core only.** Why: the extension is a system-prompt change for two roles with a measured cost
the core does not have: nine new reds in the suites run: W2-175 S5 pins the role templates' version at 1.0.1 and S7 pins their head sha256 in `docs/changes/W2-175-CIT-P.md` (4 cases, `role-research` and `role-test-designer`), and W2-153's role-source cases compare the composed `.rulesync` copies (5 cases); each needs a test designer's revision (DEC-1156 (7)) or the copies ACT, and the ticket must name `template/.rulesync/subagents/*`

The lines, verbatim before and after, and the sha256 of each file before and after, are in `CIT-P-draft.md` §2, §2b and §3. The role files that say
"ask memory (T-0)" (`role-engineer.md:11`, `role-product-spec.md:11`) or name no search (`role-reviewer.md`) need no edit: T-0 is `brief.md`.

## 5. sha256 and size, before and after

Applied together (all edits, extension included); a core-only application gives the same `brief.md`, and the two role files keep their "before".

| File | Before | After | Lines | Prose chars (budget) |
|---|---|---|---|---|
| `governance/project/facts.yaml` | `0f96904c561457f7f4b7dbf9595ef70feb35797d6e067caa78942693176e70d5` | `23bf50b9d4424ba799568f973c466fd2af3e2e0738bc04290ac93e7363b1617c` | 192 -> 195 | 9538 -> 10003 (none) |
| `governance/project/briefs/LEAD-w2-common.md` | `15983e08dbe523694b653d0a77bca04c1338c2235583875a4660cbd1854e6c8c` | `b22a7cb4130ab2e6503a15d5992144f447107d6089977e95ebaae8dda6fae638` | 200 -> 203 | 55706 -> 58366 (none) |
| `governance/project/briefs/AUDITOR-common.md` | `bb1663fd3047a5941980ba18bf9665232fe90e2f710f21db866b66ed431d52d9` | `57710c3070d654f3bda8940514af24a1e950f2d45a15302ad0be4f6807efc2c8` | 43 -> 43 | 6487 -> 6863 (none) |
| `template/governance/kernel/templates/brief.md` | `004ce0fc8f09dcc89a8ecda0b0a0ef813737323719aac3e469a1eac6ee4cfe6d` | `578ae9e10d7b7ea9027d1ef8ceec8c36a13fee0806a2165bb7d2f0047abaa645` | 62 -> 62 | 3072 -> 3525 (4000, the filled brief) |
| `template/governance/kernel/templates/role-test-designer.md` | `c1f449fbe338fc32ebc583e7e6ce57afb690bf4339cd7bf41b30a0f52fb8b990` | `d09373dc2453811676e4d01583ca15e3b8e92631c9dbd3c7abece3e247c874a9` | 31 -> 31 | 2595 -> 2653 (3500) |
| `template/governance/kernel/templates/role-research.md` | `fc41bfc1cf3bd5576080739b16cac992bb9ae912a6519b74b560b6d3af0c5799` | `5cfafa857bc1fd7e2bfe5071111eb113e2152c5fed172ecbe3e2e5dc85ad2aae` | 25 -> 25 | 1928 -> 2025 (3500) |
| `governance/project/prompts/w2-orchestrator.md` | `31498b79694d12dce45ffd9d95d6fb3c5f96e6dd79dc9fcf490a93b2c3370c07` | `2f87a79a3bae8154539ae4f7dacf4483f3738c42dba9d7a96cb5a7b53399104f` | 379 -> 379 | 86636 -> 86843 (none) |

The "after" shas are of the files produced by applying the old and new texts above to a copy of `79159cd44c5b`; they hold only if the texts are
applied exactly. For the three kernel files the "before" equals the working tree and `.claude/templates/*` (checked: byte-equal today).

**Prose budget (R3 section C).** `brief.md` is a template whose measure is on the *filled* brief (`gov brief`'s SIZE line, budget 4000: a warning, not
a refusal). The template's own body goes 3072 -> 3525 characters. A real filled brief (W2-182's engineer brief)
went 4221 -> 4738, so it was **already over 4,000 before** the change; the growth is 517 characters, of which about 200 are
the slot wrapper and `PYTHONUSERBASE` in the filled pytest line (F2). If the owner wants the brief smaller, K5 is the longest addition and can lose its last
clause without losing the rule. L3's bundle also counts in a brief's measure; L3 allows a file for a long one.

## 6. DEC-836 (2) and DEC-1064 (2): the one-line reading for the register

The conflict: DEC-836 (2) "every lead and worker brief tells its agent to use `gov retrieve`" (ACCEPTED 2026-10-19) and DEC-1064 (2) "sandboxed workers run
no `gov retrieve` (grep and the Read tool instead) ... until W2-127 makes the shared servers reachable from the sandbox" (ACCEPTED 2026-11-03, in force).
399 sandboxed searches ran anyway (11-09 to 11-13). The one line, for the register as a note on DEC-836 and on DEC-1064 (the CTO records it, with
`Role: orchestrator`; DEC-861):

> **Reading (DEC-1167 (7), standing):** DEC-836 (2)'s `gov retrieve` is, for a worker in the `gov launch` sandbox, its lead's `gov retrieve` (run as the
> worker's role; the lead puts the bundle in the brief or answers between rounds), with Read and Grep beside it (DEC-1064 (2) as written); the lead, the CTO
> and an unsandboxed worker run it themselves, and DEC-836 (3) counts, for a sandboxed worker, whether its brief carried the lead's bundle.

It covers, without an edit, the skills that say "through `gov retrieve` first (DEC-836)" (`templates/skill.md:73`, `spec-writing`, `qa-review`, `discovery`,
`retrieval`, `orchestration/briefs-and-returns.md`): a session reads them with this note. They are not drafted (a kernel skill change is its own CIT-P) and
are listed in section 8.

## 7. The copies ACT to follow (not drafted here; `.claude/**` is the CTO's, DEC-315)

After the owner approves the CIT-P and the kernel bytes land, the generated copies are rewritten by the copies ACT (`build_claude_copies_act.py`, as
for W2-98 and W2-175). Until it runs, `TEMPLATE_COPY_DIFFERS` (`src/gov/adapters/portability.py:222`) names each stale byte copy and the W2-153
portability case that compares them goes red by design (core: one finding, `.claude/templates/brief.md`; with the extension, three, adding `role-research.md` and `role-test-designer.md`; the composed copies also differ for the extension).

| Copy | Of | Kind | Tier |
|---|---|---|---|
| `.claude/templates/brief.md` | `template/governance/kernel/templates/brief.md` | byte copy | core |
| `.claude/templates/role-test-designer.md` | `.../role-test-designer.md` | byte copy | extension |
| `.claude/templates/role-research.md` | `.../role-research.md` | byte copy | extension |
| `.claude/agents/independent-test-designer.md`, `.rulesync/subagents/independent-test-designer.md`, `template/.rulesync/subagents/independent-test-designer.md` | `role-test-designer.md` | composed (the role body is the system prompt) | extension |
| `.claude/agents/research.md`, `.rulesync/subagents/research.md`, `template/.rulesync/subagents/research.md` | `role-research.md` | composed | extension |

`brief.md` has no composed copy: the **core is one copy**. `template/.rulesync/subagents/*` is a ticket path that the copies ACT's builder says it never
touches (W2-175's return, brief gap 4): the ticket of an extension names those folders in its `allowed_paths`, or the copies stay stale. The shas after are
in `CIT-P-draft.md` §3 (byte copies) and are taken when the ACT runs (composed copies).

## 8. Found on the way, and lines left alone

| Where | What | Action |
|---|---|---|
| `governance/project/briefs/AUDITOR-common.md:8, :13` | the same two frictions in the auditor's brief | **drafted** (A1, A2) |
| `governance/project/prompts/w2-orchestrator.md:167` | DEC-836 (2) in the CTO's prompt | drafted as optional (O1); `:120` ("the session sets `TMPDIR` to a folder of its own"), `:344-347` (a lead's `/tmp/gov-os-lead-<W2>` and its clean-up) are the lead's own and stay |
| `tests/acceptance/<W2>/README.md` run lines (`TMPDIR=/tmp/gov-os-lead-W2-xx ...`: W2-11, W2-65, W2-69, W2-92, W2-98, W2-107) | a designer's README names the lead's folder; an engineer who copies it hits the read-only `/tmp` | not drafted (committed acceptance files, a designer's); covered by L3's "a test designer's README run line included" |
| `template/governance/kernel/skills/{spec-writing,qa-review,discovery,retrieval}/SKILL.md`, `orchestration/briefs-and-returns.md:17`, `templates/skill.md:73` | "`gov retrieve` first (DEC-836)" | not drafted: the section 6 reading covers them; rewording a skill is a separate CIT-P |
| `template/governance/kernel/templates/role-lead.md:21, :24` | the lead's own `{CMD:retrieve}` and `gov context`, "outside the sandbox" | no edit: a lead is unsandboxed (DEC-1128 (4)); its R4 duty is in `LEAD-w2-common.md` (L3), where the CTO's lead briefs are built |
| `template/governance/kernel/templates/{role-engineer,role-product-spec,role-reviewer}.md` | "ask memory (T-0)" | no edit: resolves through `brief.md` |
| `governance/project/bootstrap.md` (:167, :987, :2062, :2177 ...) | the history of the shared `$TMPDIR` and of the Write refusals | history, not a brief |
| `.gov-runtime/scratch/orchestrator/briefs/*` (about 200 hand-written briefs) | many name `/tmp/gov-os-lead-<W2>` or `scratch/<role>/` | a lead's brief is written fresh each run from the common brief and the part. The latest (W2-182 run 4, 11-13) already carries the CTO's `$TMPDIR` line in its part, but its filled `brief.md` part still says `your scratch`, `retrieve` and a script under `.gov-runtime/scratch/` (K2, K3, K5 fix those) |
| `.gov-runtime/scratch/orchestrator/tools/launch_worker.sh:138` | the launcher script copies the brief into `<tree>/.gov-runtime/scratch/brief/` | a copy by the launcher, not a write by the worker: unaffected |

## 9. Open points (the simplest reading taken, named)

1. **How a sandboxed worker writes a script.** The Write tool is refused for `.gov-runtime/scratch/<role>/` (W2-175, W2-11, W2-176, W2-179, W2-86) and also for
   `$TMPDIR` (rows in W2-124, W2-154, W2-172: "Write tool into TMPDIR, refused once ... it then used Bash printf"). The owner named `$TMPDIR` but not the tool. I
   took DEC-1144 (7)'s stated route (Bash, `cat > "$TMPDIR/x" <<'EOF'`, "not a workaround") for every launched worker, not only reviewers: otherwise each worker's first
   script costs a refusal, and W2-154's lead counted the Bash fallback as a work-round under DEC-1142 (9). K5 and L3 carry the sentence. **If the owner reads
   DEC-1144 (7) as reviewers only, K5 and L3 lose that sentence and K6 its exception.**
2. **`$TMPDIR` against line 41's "never a shell variable as a write target"** (`brief.md`): K6 adds the one exception. The live guard lets a write it cannot
   resolve through by design (DEC-953 item 2), so it does not refuse the form; the line is advice.
3. **`heavy_slot.sh` inside the sandbox is not verified.** F2 and F3 put it in every worker's pytest line because the CTO's own per-part text already does and the
   standing rule is "every pytest through `heavy_slot.sh`". The slot locks are `/tmp/gov-os-heavy-slot-N.lock` (outside a worker's write list) and the wait log is
   under the main tree. `flock` opens an existing lock file read-only and the log write is guarded (`2>/dev/null`), so it should work, but I cannot run a sandbox.
   One line in the first sandboxed worker's run (`bash heavy_slot.sh true`), or B3's probe, settles it. **If it fails, strike `bash {TOOLS}/heavy_slot.sh ` from F2
   and F3**; the other parts stand.
4. **`$TMPDIR/empty-home` does not exist at first.** `env HOME=` a missing folder is harmless for pytest, and a tool that wants `~/.cache` creates it under the
   writable `$TMPDIR`. A `mkdir` in the line would make it a compound command.
5. **`keys.yaml:29` (kernel) still says the designer's `EMPTY_HOME` is "filled with" `{WRITE_TREE}`.** After F1 it is not; a comment, not changed here.
6. **R4's bundle must be role-filtered.** The lead's own `gov retrieve` (role orchestrator, reads open) would show an engineer its own acceptance tests and a
   designer the ticket's code. L3 passes `--role <worker role> --ticket {ID}` (the filter is live, `src/gov/retrieve/command.py`) and keeps P-R1 for designers.
   `LEAD-w2-common.md:30` gives the retrieve without `--root`, while `facts.yaml`'s `retrieve` has `--root {STORE_TREE}` (the integration store, which a designer
   must use, DEC-963). I kept the lead brief's form and did not reconcile the two.
7. **A worker's brief size.** A bundle in the note counts in the 4,000-character measure (a warning). L3 allows a file for a long one.
8. **The W2-175 record and tests pin the role templates** (section 4): why the extension is optional. A core-only change touches none of them.
9. DEC-1167 (7) also says "the correction of CLAUDE.md's guard sentence comes by its route": not in this draft.

## 10. Checks run (all on copies of `79159cd44c5b` in the session's scratchpad; the repository was not touched)

Every run through `heavy_slot.sh`, `HOME` empty, `PYTHONUSERBASE=/home/usain/.local`, `TMPDIR` in the session's scratchpad. Three copies of `79159cd44c5b`
made with `git clone` (so history-based cases work): **base** (unchanged), **core** (every edit but K7-K11) and **full** (every edit).

| Run | Result |
|---|---|
| `tests/unit/brief`, `tests/unit/launch/test_w2_153_template.py`, `tests/acceptance/W2-128`, `W2-152`, `W2-175`, `W2-153`, `W2-11/test_w2_11_brief_gaps.py` on **base** | 5 failed, 362 passed, 1 skipped. The 5 reds are at the base already: `W2-128 test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]` and `[role-lead]`, `W2-152 test_s10_gov_accept_w2_128_still_passes`, `W2-175 test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head[role-cto]` and `[role-lead]` |
| the same on **core** | 5 failed, 362 passed, 1 skipped: **the same five, no new red** |
| the same on **full** | 14 failed, 353 passed, 1 skipped: the five plus **nine new reds**, all from K7-K11: W2-175 `test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s` and `test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head` for `role-research` and `role-test-designer` (4), W2-153 `test_s3_each_role_source_is_its_front_matter_..._body` for `independent-test-designer` and `research` in `.rulesync` and `template/.rulesync` (4) and `test_s3_guard_the_check_finds_no_role_source_drift_in_this_repository` (1) |
| `tests/unit/adapters`, `tests/unit/check/test_w2_158_structural.py`, `tests/acceptance/W1-26/test_w1_26_green_base.py` on base and on **core** | 131 passed (58 deselected by the markers) on each; no new red |
| `gov.adapters.portability._template_findings` (the check behind `TEMPLATE_COPY_DIFFERS`) | base 0 findings; core 1 (`.claude/templates/brief.md`); full 3 (adding `role-research.md`, `role-test-designer.md`) |
| `gov brief engineer DAEO-5y8d` (W2-182's engineer brief) on base, core, full | exit 0 each, no placeholder left; SIZE 4,221 / 4,738 / 4,738 of 4,000 (base already over); the core's rendering differs from base's in 14 diff lines (rows 12, 36, 39, 41-42, 48-49 of the brief) |
| `gov brief independent-test-designer` and `research` on full | exit 0, SIZE 4,766 and 4,738 |
| schema | `gov.check.schema` was not run to the end (it waited for a heavy slot for over 10 minutes); the W2-128 and W2-152 facts cases, which validate `facts.yaml` against `facts.schema.json`, pass on the edited tree |

**Not run:** the full suite (DEC-968: the nightly's); a live sandboxed launch (`heavy_slot.sh` inside the sandbox, README section 9 point 3; the lead's `gov retrieve --role` bundle in a real
brief); W1-46's and W2-56's launcher cases (no launcher code changes).
