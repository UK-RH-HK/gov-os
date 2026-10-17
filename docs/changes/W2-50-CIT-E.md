---
id: W2-50-CIT-E
type: change-execution-record
status: APPLIED
date: 2026-10-17
branch: w2/W2-50
base: w2/W2-50 @ a5ef3c69 (the approved CIT-P)
proposal: W2-50-CIT-P
ticket: DAEO-kl5e (W2-50)
author: engineer (ticket mode, single author)
decisions_recorded: []
decisions_carried: [DEC-728, DEC-743, DEC-723, DEC-108, DEC-159, DEC-386, DEC-313, DEC-334, DEC-434, DEC-732, DEC-738]
state_class: EVIDENCE
---

# W2-50 — Change-execution record (CIT-E): the durable scratch root

This records what the W2-50 change did, file by file, against the proposal `docs/changes/W2-50-CIT-P.md`. It says
where the code matches the proposal and the owner's answers, and lists each difference with its reason (CAP-33). It
changes no code and no test.

## 1. What was applied

The owner approved the proposal on 2026-10-17 (DEC-743): apply now, within DEC-728, with readings R1 to R8 as written,
R7 scoped to the root, R2's launcher step, §6.1 (i), the own folder open only while the ticket is `in_progress`
(§6.4), and `ticket-lead` not among "any role" (§6.5). The points §6.2, §6.3 and §6.6 went to list rows (§5 below).

| Commit | Role | What |
|---|---|---|
| `a5ef3c69` | engineer | The approved CIT-P, word for word, with the owner's answers (DEC-738 item 1) |
| `887c288c` | independent-test-designer | 15 acceptance cases for the owner's answers (`tests/acceptance/W2-50/test_w2_50_owner_answers.py`) and the README's new section; no case of the first suite changed |
| `91200c82` | engineer | The implementation: the guard, the new module, the launcher, the secrets check, and builder tests |

Every commit carries `Task: DAEO-kl5e` and `Implements: DEC-728`. The files changed by `91200c82` are all in the
ticket's `allowed_paths`, as DEC-743 left them: `src/gov/guard/runs.py` (new), `src/gov/guard/decide.py`,
`src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`, `tests/unit/guard/test_runs.py` (new),
`tests/unit/launch/test_runs.py` (new). No specification text, decision, role file, settings file or acceptance test
was changed by the implementation.

## 2. What was done, file by file

### 3(b) The new module — `src/gov/guard/runs.py`

**Done.** One module names the root and the session's own folder, for the guard, the launcher and the secrets check
alike:

- the root is `gov-os-runs` in the session's home, the home taken by its real path; it need not exist. A home that
  cannot be resolved to an absolute path gives no root;
- the own folder is the ticket's `external-ref` as written, or its `id` (the `tk` id) when it has none (R1). It is
  resolved from the ticket that `GOV_TICKET` names, through the guard's existing ticket loader (R3: a missing, empty or
  unknown ticket gives no folder; the worktree's name plays no part);
- the folder is given only to the six roles of R4 (orchestrator, product-spec, independent-test-designer, engineer,
  independent-auditor, research). It is not given to `ticket-lead` (§6.5) or to an unknown role;
- the folder is given only while the ticket is `in_progress` (§6.4);
- a second question, used by the guard: whether a resolved path lies in the own folder (the folder itself included),
  and is not a second name of a file elsewhere. An existing file with more than one hard link is not held (R8).

**Matches** 3(b), R1, R3, R4 and the answers to §6.4 and §6.5.

**Differences** (each stricter than the proposal; no test asked for them, the unit tests hold them):

1. **A root that is a symbolic link gives no folder.** The proposal does not say. Reason: a root linked elsewhere would
   make every own folder lie elsewhere while its name still reads `~/gov-os-runs/<id>`; refusing is the guard's
   default deny. Unit case `test_a_root_that_is_a_link_gives_no_folder`.
2. **A folder name that is not one folder gives no folder:** an empty name, `.`, `..`, or a name holding `/` or a NUL.
   The proposal does not say. Reason: a ticket's `external-ref` is free text; such a name would name the root, a
   folder above it or a nested folder.
3. **The guard's ticket loader also finds a ticket by its `wbs_id`.** So a `GOV_TICKET` that is the W2 id names the
   same ticket, and the same folder, as the `tk` id. This is the guard's behaviour before this change, not new; R3 is
   kept, since the folder still follows the ticket `GOV_TICKET` names.
4. **The ticket's role need not be the session's role.** Any of the six roles on an `in_progress` ticket gets that
   ticket's folder (the fixture's test designer and auditor on an engineer's ticket). This is R4 as written ("any
   role"); it is stated here because a ticket's `allowed_paths` hold only for the ticket's own role.

### 3(a) The guard's outside-repository rule — `src/gov/guard/decide.py`

**Done.**

- The path rule gains one place outside the repository: a resolved write target the module above holds in the own
  folder is allowed. The rule is checked after the temp-folder rule (DEC-108, unchanged) and before the
  inside-repository rule, which is unchanged. It applies to Write, Edit and every Bash target the guard judges, for
  the acting role (the session's role, or the subagent's type).
- Every target is resolved by its real path first, as before. So `..`, a symbolic link in or to the own folder, an own
  folder that is itself a link elsewhere, and a repository link into another ticket's folder all resolve outside the
  own folder and are refused (R8's link half). A hard link already in the own folder is refused by the module's
  link-count rule (R8). Making a hard link from outside (`ln`, `cp -l`, `link`) stays refused by DEC-334's rule, which
  judges the link's source. A move or copy across the folder's edge is refused because its outside name is a judged
  target.
- The folder need not exist (R2): a target that does not exist yet is held when it lies in the folder, so `mkdir -p`
  of it makes the root too.
- **R7, scoped to the root (DEC-743 1).** `rmdir` is now read among the Bash forms; its arguments are resolved, and
  only a target equal to the root is judged (and refused, as the root is never held). Every other `rmdir`, inside the
  repository or under the root, stays unjudged as before.
- The refusal reason is the guard's existing one, "… to '<path>' denied for role '<role>'", naming the resolved
  target. The guard's other refusals still come first and are unchanged (frozen, held-out, settings file, escape
  hatch, unknown tools, unknown roles).

**Matches** 3(a), §4 (R7 scoped to the root as answered; R8), and the answers to §6.4 and §6.5 (through the module).

**Differences:**

5. **An unresolvable `rmdir` argument is not refused.** Elsewhere the guard refuses a write target it cannot resolve
   (an unknown variable, a brace). For `rmdir`, only a target equal to the root is kept, so an argument the guard
   cannot resolve is dropped and the command is allowed, as every `rmdir` was before this change. Reason: the owner's
   scope (judge `rmdir` of the root only; nothing everywhere) and the answer case
   `test_rmdir_of_an_empty_folder_in_the_repository_outside_the_paths_stays_as_today`. It leaves open that `rmdir` of
   a variable that holds the root is not refused (§5).
6. **The refusal reason names no `gov-os-runs` rule.** A refusal under the root reads as any refusal outside does; the
   README accepts it because it names the target. Not a difference in behaviour, stated for the reader of a refusal.

### 3(c) The launcher's sandbox write list — `src/gov/launch/launcher.py`

**Done.**

- After the built settings pass their strictness check and before the session starts, the launcher asks the module
  for the own folder and makes it, with the root when the root does not exist (R2, DEC-743 1). An existing folder and
  what it holds are left alone; no other folder under the root is made.
- The sandbox's `allowWrite` holds the session's temp folder (DEC-159) and the own folder, and never the root.
- The temp folder is still removed at the session's end (DEC-386). The own folder is never removed by the launcher
  (R6).
- `--add-dir` and `permissions.additionalDirectories` are still refused (DEC-313): the folder enters only through the
  sandbox's write list.

**Matches** 3(c), R2 (with the owner's approval of the step beyond "the sandbox write list only"), R6, and the KPI
line "exactly that folder (not the root)".

**Differences:**

7. **When the own folder cannot be named or made, the session starts without it.** The proposal does not say. If the
   module gives no folder, if making it fails, or if what stands at its path is a link or not a folder, the launcher
   adds nothing to the write list and starts the session with the temp folder only. It does not refuse the launch and
   prints nothing. Reason: the guard's default (no folder is opened that cannot be shown to be the own one), and no
   case asks for a refusal; a launch the session does not need the folder for is not stopped. Unit case
   `test_an_own_folder_that_is_a_link_is_not_opened`. It leaves open whether such a launch should be refused or
   announced (§5).
8. **The folder is made before the temp folder and before the signal handlers are set.** A launch stopped by a signal
   before the session starts still leaves the made folder on disk. This matches R2 ("before it starts the session")
   and the reversal note of 3(c) (folders the launcher made stay on disk).

### 3(d) The secrets-indexing exclusion — `src/gov/secrets/__init__.py`, not `secrets-indexing.yaml`

**Done.** In the walk over `.gov-runtime/`, which still follows linked folders, a folder or a file is not followed
when its real path lies in the root and not in the repository's own `.gov-runtime/`. The check then stays green and
prints nothing from the root (R5). A linked folder elsewhere, outside the root, is still followed (W1-15's B4). The
root is matched as a folder, so a near name such as `~/gov-os-runs-old` is elsewhere and still followed.

**Matches** R5, DEC-743 3 (§6.1 (i), the link rule only), and the answer cases: a link to the own folder, to a file
in it, to the root itself; a linked folder elsewhere still followed; a near name of the root still followed.

**Differences:**

9. **`template/governance/kernel/checks/secrets-indexing.yaml` did not change.** The CIT-P's §3(d) titles the change
   with that file and §7 lists it among the code. The check's command stays `python3 -m gov.secrets`, with no option;
   the whole rule is in the module that holds the walk, which §6.1 (i) added to the ticket's paths. Reason: §6.1 says
   the exclusion cannot be reached from the check's file, and the owner chose (i), so nothing was left for the file to
   say. Consequence: W2-06, which §7 names as building on W2-50's version of that file, finds it as it was. 3(d)'s
   reversal is a revert of the module's change alone.
10. **A clone under the root runs its own check over its own store.** When the check runs in a repository that itself
    lies under the root (an adopted clone in an own folder), the files of that repository's own `.gov-runtime/` are
    scanned, because a path in the scanned repository's runtime folder is followed before the root rule is applied.
    A link from the clone's runtime folder to elsewhere under the root is not followed; a link outside the root is.
    The proposal does not say; reason: the KPI line "a product clone that is adopted there has its own store, inside
    the clone" — that store is the clone's to check, and an exclusion of the whole root would leave the clone's check
    always green. **No test holds this:** the suite runs the check only from the fixture project, and no builder test
    covers the secrets module (its tests are not in the ticket's paths). It is open (§5).
11. **The secrets module now imports the guard's new module** to name the root, so the two cannot name different
    roots. A new dependency of `gov.secrets` on `gov.guard`; the module it imports holds no state.

### The builder tests — `tests/unit/guard/test_runs.py`, `tests/unit/launch/test_runs.py` (new)

Eight test functions: the folder's name (`external-ref` or `tk` id), no folder without a known role and an
`in_progress` ticket, a root that is a link, the guard opening the own folder only, a hard link in the own folder,
`rmdir` judged for the root only; the launcher making and adding the folder, and not opening a folder that is a link.
They are the engineer's tests; the acceptance suite is the test designer's.

### What did not change

- The role files (`governance/kernel/roles/`): no role file names `~/gov-os-runs` (R4).
- DEC-108's scratch set, DEC-159's temp folder and its removal (DEC-386), DEC-313's refusals, DEC-334's hard-link
  rule, DEC-434's `ticket-lead` list.
- `gov rebuild` and the indexers: they do not follow a link out of the repository, as the CIT-P said; the store cases
  passed before the change and pass after it.
- The Contract's text (CAP-58, CAP-61, CAP-38.b): behaviour changes under it, no text changes (§6.6, row W2-L342).

## 3. Verification

As the lead ran it at `91200c82`, each command with `PYTHONPATH` set to this worktree's `src/` (DEC-732):

| Run | Result |
|---|---|
| `gov rebuild --json`, one full rebuild | ok; lexical, semantic and codeintel recreated |
| `tests/acceptance/W2-50` | **154 passed** (55 red before the change, README) |
| Builder tests `tests/unit` | **2113 passed, 1 skipped** |
| Acceptance suites W1-01 to W1-50 | green, except W1-42's two known reds (RETR-X-02, "no named parent expansion"; the governance share per programme), named exceptions at Wave 1's close (DEC-713, DEC-714), not this ticket's |
| W1-46 and W1-50 | run with `-m "not local_only"` |

**Not run, and why:**

- **38 live-launch cases:** 36 of `tests/acceptance/W1-46/test_w1_46_live_sessions.py`, and two of W1-50
  (`test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`,
  `test_a_flag_put_over_the_placeholder_during_a_command_stays`). They launch real sessions through `gov launch` with
  the real HOME, and from this change on a launch makes the real `~/gov-os-runs/<fixture W2 id>/`. Nobody creates the
  real root in this run.
- **`docs/plan/tools/validate_s1.py`:** not run (DEC-738 item 2).

This record's own check: its frontmatter was validated against
`template/governance/kernel/schemas/change-execution-record.schema.json` (with `common.schema.json`).

The list row **W2-M355** ("Live clones under /tmp lost on reboot") is taken in by this change: the own folder lies in
no temp folder and survives the session's end (R6,
`test_a_clone_made_in_the_own_folder_survives_the_sessions_end_and_the_next_session_finds_it`).

## 4. Size against the estimate

`git show --shortstat 91200c82`: 6 files, 265 insertions, 7 deletions.

| Part | Added | Removed |
|---|---|---|
| `src/gov/guard/runs.py` (new) | 54 | 0 |
| `src/gov/guard/decide.py` | 17 | 2 |
| `src/gov/launch/launcher.py` | 13 | 1 |
| `src/gov/secrets/__init__.py` | 16 | 4 |
| **Code** | **100** | **7** |
| `tests/unit/guard/test_runs.py` (new) | 92 | 0 |
| `tests/unit/launch/test_runs.py` (new) | 73 | 0 |
| **Builder tests** | **165** | **0** |

The code is within the estimate of 120 LOC (`est_loc`): 100 lines added, 93 net. With the builder tests the change is
265 lines.

## 5. What stays open

| Item | Where it goes |
|---|---|
| The guard does not judge `git clone` destinations (CIT-P §6.2) | Row **W2-H055**, ticket W2-09 (DEC-743 4) |
| Whether a launched session's Write and Edit reach the own folder past Claude Code's own permission check (CIT-P §6.3) | Row **W2-M359**, ticket W2-21 (DEC-743 5) |
| CAP-58's text names neither the temp folder nor the own folder (CIT-P §6.6) | Row **W2-L342**, Wave 3 (DEC-743 8) |
| The 38 live `local_only` launch cases of W1-46 and W1-50 have not run against this change; the real `~/gov-os-runs/` does not exist | Run when the owner lets the real root be made; the first live launch of a ticket makes `~/gov-os-runs/<its id>/` |
| `rmdir` under the root but not of it (another ticket's empty folder; `rmdir -p` that removes an otherwise empty root), README discoveries | W2-09, with the guard's Bash forms; the owner's root-only scope was kept |
| Difference 5: an unresolvable `rmdir` argument is allowed, so `rmdir` of a variable that holds the root is not refused | W2-09, with the item above |
| Difference 7: a launch whose own folder cannot be named or made starts without it, silently | W2-21 (it edits `launcher.py` next), or an owner answer: refuse, announce, or keep |
| Difference 10: the secrets check run inside a clone under the root scans the clone's own store; no test holds it | The test designer of a later ticket that adopts a clone under the root (W2-14, W2-15a), or W2-06 |
| W2-06 builds on `secrets-indexing.yaml` unchanged (difference 9) | W2-06; nothing to merge from W2-50 in that file |
