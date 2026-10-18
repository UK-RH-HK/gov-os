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
decisions_carried: [DEC-728, DEC-743, DEC-751, DEC-723, DEC-108, DEC-159, DEC-386, DEC-313, DEC-334, DEC-434, DEC-732, DEC-738, DEC-136, DEC-135, DEC-752, DEC-758, DEC-764, DEC-765]
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
| `72263054` | independent-test-designer | 54 acceptance cases for the review's findings (`tests/acceptance/W2-50/test_w2_50_review_findings.py`), tests added after implementation (DEC-136); 34 red at that commit |
| `86aa805c` | engineer | The repair round (§6): a project inside the own folder, plain folder names, one folder per ticket |
| `e58081be` | independent-test-designer | 25 acceptance cases for the last review's findings (`tests/acceptance/W2-50/test_w2_50_last_review.py`, DEC-751), 15 red; 80 earlier cases made the folder by a launch (DEC-491) |
| `df5f1e50` | engineer | The repair round after the last review (§7): the own folder's repository marker, links inside the scanned project |
| `ef7c1835` | independent-test-designer | 72 acceptance cases for the extra review's findings F1 and F2 (`tests/acceptance/W2-50/test_w2_50_extra_review.py`, DEC-758), 38 red |
| `83b0f2f4` | engineer | The last round (§9): a copy into a folder judged file by file, no own folder for a project under the root |

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
   folder above it or a nested folder. *Superseded in the repair round (§6, change 2): only a plain folder name gives
   a folder.*
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
| Difference 10: the secrets check run inside a clone under the root scans the clone's own store; no test holds it | Closed in §7 (DEC-751 2): held by the last review's tests |
| W2-06 builds on `secrets-indexing.yaml` unchanged (difference 9) | W2-06; nothing to merge from W2-50 in that file |
| Difference 13: a ticket file in `.tickets/` that cannot be read closes every own folder of the project | Kept as the guard's default deny; an owner answer if it is found too strict |

## 6. The repair round (after the review)

The review of `91200c82` found three behaviours the suite did not hold. The test designer added them as
`tests/acceptance/W2-50/test_w2_50_review_findings.py` at `72263054`, tests added after implementation (DEC-136):
54 cases, 34 red against `91200c82` (the README's section "The review's findings"). The findings the new tests hold:

1. **A project inside the own folder keeps every in-project rule.** A clone at `~/gov-os-runs/W2-90/clone` with
   its own `.tickets/` is a project like any other: its acceptance tests, its `.gov-runtime/` outside `scratch/`, its
   `.tickets/`, its `.claude/settings.json`, its guard hook and every path outside the ticket's `allowed_paths` stay
   refused; the own folder outside such a project gives that session nothing (DEC-108's counterpart), and `gov
   launch` there adds no entry that holds the project. Before the repair, the own-folder allowance covered the
   whole clone (16 + 1 + 1 red).
2. **Only a plain folder name names a folder:** a letter or digit first, then only letters, digits, `.`, `_` and
   `-`. Before the repair, `*`, `W2-9?`, `W2 90`, `-W2-90`, `.hidden` and the like each gave a folder, and the
   launcher put a glob entry such as `//…/gov-os-runs/*` in the sandbox's write list (10 + 6 red).
3. **One folder belongs to one ticket.** A name that two or more tickets of the project give, whatever the other
   ticket's status, gives no session of either ticket that folder, also when one ticket's `external-ref` equals the
   `tk` id another ticket's folder is named by (3 + 1 + 2 + 2 red).

### What the repair changed, file by file

- **`src/gov/guard/runs.py`** — `own_folder` gives no folder (`None`) in three more cases, each checked after the
  existing ones:
  - the name is not a plain folder name (`PLAIN_NAME`, `[A-Za-z0-9][A-Za-z0-9._-]*`, matched whole). This replaces
    the earlier test for `""`, `.`, `..`, `/` and NUL, which it covers;
  - the own folder and the project's real root overlap: the folder is the project's root, holds it or lies in it;
  - the name is not given by exactly one ticket of the project's `.tickets/` (`_named_once`: each ticket's name is
    its `external-ref` as written, else its `id`, as for the session's own ticket). A ticket file that cannot be read
    gives no folder, since it may give the name too.
  
  The interface is unchanged: `root()`, `own_folder(project_root, ticket_id, role) -> str | None` and
  `holds(own, real) -> bool`. The launcher and the secrets check need no change: the launcher makes and adds only
  what `own_folder` gives, so each finding's launcher half follows from the guard's.
- **`src/gov/guard/decide.py`** — `own_folder` is now asked only when a write target lies outside the project's real
  root (new helper `_at_or_under`). This is exact, not a shortcut: an own folder never overlaps the project, so it can
  never hold a target inside it. It keeps the ticket scan of `_named_once` off the guard's path for every write in
  the project, for the latency cases of W1-02 and W1-05.
- **`tests/unit/guard/test_runs.py`**, **`tests/unit/launch/test_runs.py`** — builder tests, regression evidence
  only: names that are not plain (8) and a plain name with `.` and `_`; a name two tickets give (the same
  `external-ref`, and an `external-ref` equal to a `tk` id), refused to both; a project in the own folder that keeps
  its in-project rules and is refused beside itself; the launcher neither making nor adding a shared folder.
- **Not changed:** `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`,
  `template/governance/kernel/checks/secrets-indexing.yaml`, every acceptance test.

### New differences from the CIT-P

12. **A folder overlaps the project in either direction.** The tests ask that a project inside the own folder gets
    no folder. The repair also gives none when the own folder would lie inside the project (a HOME inside a
    repository). Reason: there, too, the own-folder allowance would pass over the in-project rules. It costs nothing
    on the tested paths.
13. **An unreadable ticket file closes the folder.** A `.md` file in `.tickets/` that cannot be read (or a folder of
    that name) gives no own folder to any session of the project, since it cannot be shown not to give the same name.
    The guard's default deny; no test asks for it (§5).

None of the three findings is in the CIT-P's text; they are the review's readings of R1 ("named by the ticket's W2
id") and of DEC-108's counterpart, passed on as described behaviour (DEC-136). Each makes the guard stricter: no case
that refused before the repair is allowed after it.

### Verification of the repair round

At `86aa805c`, each run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` (DEC-732), in the foreground:

| Run | Result |
|---|---|
| `tests/acceptance/W2-50` | **208 passed** (34 failed, 174 passed at `72263054`) |
| W1-02 (incl. `test_decision_p95_is_under_100_ms`) | 3653 passed |
| W1-03 | 363 passed, 1 skipped (the interpreter finds `gov` without `PYTHONPATH`) |
| W1-04 | 336 passed |
| W1-05 (incl. `test_a_call_waits_under_100_ms_p95_for_the_hook`) | 99 passed |
| W1-15 | 124 passed |
| W1-28 | 151 passed |
| W1-32 | 81 passed |
| W1-38 | 201 passed |
| W1-46, `-m "not local_only"` | 457 passed, 36 deselected |
| W1-48 | 172 passed |
| W1-50, `-m "not local_only"` | 683 passed, 2 deselected |
| Builder tests `tests/unit` | **2126 passed, 1 skipped** |

The `local_only` live-launch cases were not run, as in §3: they would make the real `~/gov-os-runs`, which does not
exist.

### Size of the repair

`git show --shortstat 86aa805c`: 4 files, 87 insertions, 5 deletions.

| Part | Added | Removed |
|---|---|---|
| `src/gov/guard/runs.py` | 41 | 4 |
| `src/gov/guard/decide.py` | 8 | 1 |
| **Code** | **49** | **5** |
| `tests/unit/guard/test_runs.py` | 30 | 0 |
| `tests/unit/launch/test_runs.py` | 8 | 0 |
| **Builder tests** | **38** | **0** |

With the first round's 100 code lines, the change's code is 149 lines added and 12 removed, 137 net, above the
estimate of 120 LOC (`est_loc`) by 17 lines.

## 7. The repair round after the last review (DEC-751)

The last review of the repaired change found two behaviours the suite did not hold. The orchestrator decided them on
2026-10-17 (DEC-751, delegated, stricter only; staged for the owner's commit, not yet in this worktree's register):
P-A (a) and P-B (a), fixes after the review that DEC-413 allows. The test designer added them as
`tests/acceptance/W2-50/test_w2_50_last_review.py` at `e58081be`, tests added after implementation (DEC-136), and
rewrote 80 earlier cases to make the own folder by a launch (DEC-491). The suite at `e58081be`: 15 failed, 218
passed. The findings the new tests hold (the README's section "The last review's findings"):

1. **A folder belongs to the one repository whose launch made it.** `gov launch` records in the folder it makes the
   repository's git common directory, so every worktree of one repository is the same repository and a clone is
   another. Another repository's session whose `in_progress` ticket gives the same name gets nothing there (a project
   built apart, a clone inside the first project's own folder, a clone outside the root: 3 red), and its launch
   neither adds the folder nor changes it (3 red). A folder made by hand (2 red) and a folder that does not exist yet
   (2 red) give no session anything; a launch neither adds nor records a folder that was there before any launch
   (2 red).
2. **A project's own secrets check follows a link that stays inside the project, also under the root.** A clone at
   `~/gov-os-runs/W2-90/clone` whose `.gov-runtime/` links to a folder or file of the same clone holding a secret goes
   red, as the same layout outside the root does (3 red). A link from it to a place under the root but outside the
   clone is still not followed (DEC-743 3).

### What the repair changed, file by file

- **`src/gov/guard/runs.py`** — the marker, and the rule on it:
  - `MARKER = ".gov-os-repository"`: a regular file in the own folder holding the real path of the git common
    directory of the repository whose launch made the folder, and a newline.
  - `common_dir(project_root)`: that real path, read from the project's `.git` without running git — `.git` a
    folder gives itself; `.git` a file gives its `gitdir:` line, then that folder's `commondir` when there is one.
    Anything else, or a folder that is not there, gives `None`.
  - `_marked(own, project_root)`: true only when `own` is a folder (not a link) and its marker, opened without
    following a link, is a regular file whose bytes are exactly the project's common directory and a newline. A
    marker missing, unreadable, not a regular file or naming another repository, or a common directory that cannot be
    found, gives false.
  - `folder(...)` is the former `own_folder` body: the path a ticket's own folder has, whether or not it is there.
    `own_folder(...)` is now `folder(...)` when `_marked`, else `None`: every case that refused before still refuses.
  - `make(own, project_root)`: makes the root when needed, then the own folder with `mkdir` (never one that is
    there), then the marker with `O_CREAT | O_EXCL | O_NOFOLLOW` (never a rewrite). Nothing is made when the common
    directory is unknown; an error leaves at most a folder without a marker, which gives nothing.
  - `holds(own, real)` no longer holds the marker itself, so the guard refuses Write, Edit and judged Bash on it.
- **`src/gov/launch/launcher.py`** — the launch makes and marks the folder only when nothing is at its path
  (`runs.make`), then opens what `runs.own_folder` gives. A folder there without this repository's marker (made by
  hand, there before any launch, or marked by another repository), a link, or a file, is left as it is and not added
  to the sandbox's write list. This replaces the `makedirs(..., exist_ok=True)` and the link and folder checks, which
  `_marked` now makes.
- **`src/gov/secrets/__init__.py`** (the link rule only) — `followed` also follows a path whose real path stays inside
  the project being scanned (`os.path.realpath(root)`), even under the root. A link from it to a place under the root
  but outside the project, and from a project outside the root into a clone under it, is still not followed.
- **`src/gov/guard/decide.py`** — not changed: it asks `runs.own_folder` as before, so the marker rule reaches the
  guard through it. The marker is read only when a write target lies outside the project (§6), a few system calls.
- **`tests/unit/guard/test_runs.py`**, **`tests/unit/launch/test_runs.py`** — builder tests, regression evidence
  only: the fixture projects get a `.git` folder; the cases that open the folder make it with `runs.make`; new cases
  for a folder missing, made by hand (and not marked by `make`), marked by this repository, refused to another
  repository and its marker refused to its own session; a worktree's `.git` file giving its repository's common
  directory; a later launch keeping the folder; a folder already there, empty or not, neither marked nor added.
- **Not changed:** `template/governance/kernel/checks/secrets-indexing.yaml`, every acceptance test.

### New differences from the CIT-P

14. **A session writes in its own folder only after a launch of its ticket has made it.** R2's guard half ("the
    folder need not exist", so an unlaunched session's first write made it, §2 3(a)) is gone: a folder that does not
    exist yet, or that no launch of this repository made, gives nothing. The orchestrator, which is not launched, can
    write in a ticket's folder only once that ticket has been launched. DEC-751 1; tested.
15. **The marker is refused to its own session in the guard, not in the sandbox.** The guard refuses Write, Edit and
    every judged Bash form on the marker (*corrected in §9: until DEC-758 a copy, install or move into the own folder
    that landed on the marker was not refused, row W2-L349; since the last round it is*); the sandbox's write list
    still holds the whole folder, so a command whose target the guard cannot see could change it. A session that does so closes or hands over its own folder only,
    never opens another's. No source asks for it; it costs one comparison.

**Difference 10 is closed.** A clone under the root now has its own check over its own store and over links that stay
inside it, held by `last::test_a_projects_own_check_follows_a_link_that_stays_inside_the_project` and the three
controls beside it (§5's row for difference 10 is done).

### Verification of the repair round after the last review

At `df5f1e50`'s tree, each run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` (DEC-732), in the
foreground, never with `-x`:

| Run | Result |
|---|---|
| `tests/acceptance/W2-50` | **233 passed** (15 failed, 218 passed at `e58081be`) |
| W1-02 (incl. `test_decision_p95_is_under_100_ms`) | 3653 passed |
| W1-03 | 363 passed, 1 skipped (the interpreter finds `gov` without `PYTHONPATH`) |
| W1-04 | 336 passed |
| W1-05 (incl. `test_a_call_waits_under_100_ms_p95_for_the_hook`) | 99 passed |
| W1-15 (B4 included) | 124 passed |
| W1-16 | 167 passed |
| W1-27, `test_w1_27_rebuild_r4.py` (the only file that calls `stores_with_secrets`) | 5 passed |
| W1-28 | 151 passed |
| W1-30 | 512 passed |
| W1-32 | 81 passed |
| W1-38 | 201 passed |
| W1-46, `-m "not local_only"` | 457 passed, 36 deselected |
| W1-48 | 172 passed |
| W1-50, `-m "not local_only"` | 683 passed, 2 deselected |
| Builder tests `tests/unit` | **2130 passed, 1 skipped** |

The machine was under load from other sessions (load average about 12); the two latency cases passed as part of
their suites.

The `local_only` live-launch cases were not run, as in §3; the real `~/gov-os-runs` still does not exist.

### Size of the repair after the last review

`git show --shortstat df5f1e50`: 5 files, 139 insertions, 24 deletions.

| Part | Added | Removed |
|---|---|---|
| `src/gov/guard/runs.py` | 71 | 5 |
| `src/gov/launch/launcher.py` | 8 | 11 |
| `src/gov/secrets/__init__.py` | 4 | 3 |
| **Code** | **83** | **19** |
| `tests/unit/guard/test_runs.py` | 40 | 4 |
| `tests/unit/launch/test_runs.py` | 16 | 1 |
| **Builder tests** | **56** | **5** |

The code is 64 lines net, within the brief's estimate of 50 to 70 lines; 83 lines added, above it, about a third of
them docstrings. With the earlier rounds the change's code is 232 lines added and 31 removed, 201 net, above the
estimate of 120 LOC (`est_loc`) by 81 lines.

## 8. The two failed reviews (history, DEC-752)

Two independent reviews of this change failed before the repairs of §6 and §7. Each was a fresh read-only reviewer
(role `independent-auditor`, the reading tools only), commissioned and judged by the orchestrator. Their probe records
are kept here as history, not under `docs/probes/` (DEC-752 item 2, the owner, 2026-10-17; staged for the owner's
commit, not yet in this worktree's register).

### Review 1

- **Probed commit:** `b7981b0faf3cad33b596cdd330cd1a339fad5d8c` (implementation `91200c82`, CIT-E `b7981b0f`).
- **Reviewer session:** `9ffac555-e15e-4654-ba56-e68b45435bb3`.
- **Judgement:** fail.

| # | Finding (the record's words, summarised) | What was done with it |
|---|---|---|
| 1 | A project lying inside the session's own folder lost every in-project rule (acceptance tests, freeze flag, records, `.tickets/`, settings file, guard hook, `allowed_paths`); high, reproduced, fail-open | Repaired: tests `72263054`, repair `86aa805c`, CIT-E `0bbada97` (§6 finding 1) |
| 2 | Glob characters in `external-ref` put `//…/gov-os-runs/*` or `/**` into the sandbox write list; medium | Repaired in the same commits (§6 finding 2) |
| 3 | Two tickets naming the same folder shared it; medium-low, can lose work | Repaired in the same commits (§6 finding 3) |
| 4 | A `ticket-lead` session's subagent of another role type reaches the folder (the guard's acting-role model); low, owner question | Residual: the guard's model of the acting role, as inside the repository; not fail-open under DEC-743 item 7, as the second review was briefed |
| 5 | The own folder's path can be written as a file; low | Residual: a later launch then started without an own folder (difference 7, to W2-21; DEC-751 W-2 (b) makes the silent start a warning row for W2-21). Since `df5f1e50` a file in the folder's place also gives no folder (§7) |
| 6 | `rmdir` of the root with an unresolvable argument; low | Residual: difference 5, to W2-09 (§5) |
| 7 | Bash forms the guard never judged (`find -delete`, `env rm`, `git clean`, `rsync --delete`, `dd of=`, `truncate`, an interpreter's `-c`); pre-existing | Residual, pre-existing: the guard's Bash forms, W2-09 |
| 8 | Two cases stricter than needed: a link in the own folder resolved through for `rm`; a secrets-check loop on a link to a HOME that holds the project, which fails closed and existed before | Residual, not fail-open |

### Review 2, the second and last under DEC-413

- **Probed commit:** `f9277098f60c747df9c52efb134dd684cd064f0c` (implementation `91200c82`, repair `86aa805c`, CIT-E
  `0bbada97`, lead checkpoint `f9277098`).
- **Reviewer session:** `1e0c179d-c135-4a63-a5a3-e65980db433f`.
- **Judgement:** fail.

| # | Finding (the record's words, summarised) | What was done with it |
|---|---|---|
| 1 | Another project's ticket of the same name gets this repository's ticket folder: a second Gov OS project on the same home with an `in_progress` ticket whose `external-ref` names the folder may write in it and remove it, and its launch adds the folder to the sandbox write list; medium-high, reproduced through the guard and `gov launch` | Decided by DEC-751 item 1 (P-A (a)); repaired: tests `e58081be`, repair `df5f1e50`, CIT-E `8a3c27e9` (§7 finding 1, the marker) |
| 2 | A clone's own secrets check fails open for a linked store inside the clone: with the project under the root, a `.gov-runtime/` link to a folder of the same project holding a secret is not followed (green), while the same layout outside the root goes red; medium, reproduced | Decided by DEC-751 item 2 (P-B (a)); repaired in the same commits (§7 finding 2) |
| 3 | A FIFO among the ticket files hangs `gov launch` and makes the guard refuse every write outside the project (the temp folder included) until its deadline; low | Residual row (DEC-751 item 5): fails closed, availability only |

Neither fail record is committed: both stay uncommitted drafts by DEC-752 item 2, and a further independent review of
the repaired change follows this record; its pass record, if it passes, is the only probe record committed under
`docs/probes/DAEO-kl5e/`.

## 9. The last round, after the extra review (DEC-758)

An extra independent review of the repaired change found two more behaviours missing. The owner decided them on
2026-10-17 (DEC-758 item 1; staged for the owner's commit, not yet in this worktree's register) and allowed this
round as the last. The test designer added them as `tests/acceptance/W2-50/test_w2_50_extra_review.py` at
`ef7c1835`, tests added after implementation (DEC-136): 72 cases. The suite at `ef7c1835`: 38 failed, 267 passed, every
failure in the new file (the README's section "The extra review's findings"). The findings the new tests hold:

- **F1. A copy or install into a folder is judged as each file it writes.** `cp X d/`, `cp X d`, `install X d/`,
  `cp -r s/. d/`, `cp a b d/` and the `-t` / `--target-directory` forms write `d/<name>`, and the call is refused,
  with the guard's reason, when any such file is refused as a direct write: an entry already at that name that is a
  symbolic link out of the allowed place, a hard link to a file elsewhere, or a link to a folder outside. Before the
  repair the guard judged only the folder `d` (11 + 4 red in the own folder). This closes:
  - **row W2-H056**, the older hole, for every ticket inside the repository: a copy into a folder of the role's paths
    that lands on a link to the acceptance test (4 red);
  - **row W2-L349**: a file named like the own folder's marker copied, installed or moved into the own folder (5
    red), refused as the direct write onto the marker is.
- **F2. A project whose real root is inside `~/gov-os-runs` gets no own folder.** Its sessions get nothing in any
  folder under the root outside the project, whatever ticket they name (7 red), and its `gov launch` adds no folder
  under the root to the sandbox's write list, makes none and writes nothing there (7 red).

A FIFO in the marker's place is row W2-L350, not this round's work.

### What the repair changed, file by file

- **`src/gov/guard/runs.py`** (F2) — `folder(...)`, and so `own_folder(...)`, gives `None` when the project's real
  root (`os.path.realpath`) is the root or lies under it. The project's path is resolved, so a project reached
  through a link outside the root is caught too. The interface is unchanged.
- **`src/gov/launch/launcher.py`** — not changed. The launcher makes and adds only what `runs.folder` and
  `runs.own_folder` give, so F2's launcher half follows from the module: no folder is made or marked, and the write
  list holds the temp folder only.
- **`src/gov/guard/decide.py`** (F1), in the Bash target reading:
  - `_paths(raw)`: the expansion half of `_resolve` (variables, `~`, globs, `/dev/null`, the working folder), giving
    the absolute paths as written and not resolved. `_resolve` now calls it; what it gives is unchanged.
  - `_into(dest, sources, itself=..., merge=...)`: a copy, install or move of the sources into the folder `dest`. When
    `dest` is a folder that exists (a `-t` folder whether or not it exists), each source gives `<dest>/<name of the
    source as written>`; a source written `s/.`, `s/..` or `/` gives each entry of `s` in `dest`. A destination whose
    kind cannot be told (an error other than "not there") and a source that cannot be resolved are refused.
  - `_land(src, dst)`: judges `dst` by its real path, as a direct write is judged, so a link out, a link to another
    ticket's folder, the marker and a hard link (R8, in the own folder) are refused as they are for Write. When `src`
    is a folder and `dst` a folder that exists, each entry of `src` in `dst` is judged too, and so on down.
  - `_copies(args, operands, dirs)`: for `cp`, `install` and `mv`, each `-t` folder, and the last operand (every
    operand but the first after an option written after an operand, as before). `-T` / `--no-target-directory`
    (`merge`): a source folder's entries land in the destination itself.
  - Every target judged before is still judged: the new targets are added to them, so no call that was refused before
    is allowed now. `_MOST_LANDED = 10000`: a copy judged as more paths than that is refused.
- **`tests/unit/guard/test_runs.py`**, **`tests/unit/launch/test_runs.py`** — builder tests, regression evidence
  only: eight copy forms (`cp X d/`, `cp X d`, `install`, `cp -r s/. d/`, several sources, `mv`, `cp -rT`, `cp -t`)
  × a link out, a hard link, the marker, each refused, and the same into a clean folder allowed; a folder below a
  folder already there; the path limit; a project under the root with no folder, keeping its own writes; a launch
  from a project under the root that makes and adds nothing.
- **Not changed:** `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`,
  `template/governance/kernel/checks/secrets-indexing.yaml`, every acceptance test.

### The interface as changed

- **A copy, install or move into a folder** is judged as the folder (as before) and as each file it writes in it,
  `<folder>/<name>`, by that file's real path and under the same link and hard-link rule as a Write on it, and below
  where a folder of the same name is already there. The refusal is the guard's own: "Bash write to '<path>' denied for
  role '<role>'", naming the file's resolved path.
- **A project whose real root lies in `~/gov-os-runs`** has no own folder: in the guard every path under the root
  outside the project is refused to its sessions; in the launcher nothing is made, marked or added there. Its
  in-project rules are unchanged.

### New differences from the CIT-P

16. **`mv` into a folder is judged the same way.** DEC-758 names copies and installs; the marker case of the tests
    moves a file, and a move into a folder writes `<folder>/<name>` as a copy does. Stricter only.
17. **The walk goes down only where the destination already has a folder.** Files a recursive copy makes inside a
    folder that is not there yet are judged by that folder's own path, which is judged; nothing below it exists that
    could lead out. A ticket pattern that holds a folder but not the files in it (`src/app/*`) is therefore judged at
    the copy's first new level only, as before this round. Reason: the cost of a walk of the whole source; no test
    asks more.
18. **Doubt refuses.** A destination whose kind cannot be told, a source that cannot be resolved (an unknown
    variable, a glob with no match), a `-t` source written as a folder's contents, and a copy of more than 10 000
    paths are refused. The first three were allowed before when the destination alone was allowed; DEC-758 and the
    brief ask that doubt refuse.
19. **`-T` is read wherever a `T` stands in a cluster of short options.** A suffix such as `-S.T` is read as `-T`
    too; the call is then judged both ways, never fewer.

**Difference 15's text is corrected** (§7): it said every judged Bash form on the marker was refused, which did not
hold for a copy, install or move into the own folder (W2-L349). It holds as written since this round.

### Verification of the last round

At `83b0f2f4`'s tree, each run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` (DEC-732), in the
foreground, never with `-x`; `gov.__file__` is `/home/usain/gov-os-worktrees/W2-50/src/gov/__init__.py`:

| Run | Result |
|---|---|
| `tests/acceptance/W2-50` | **305 passed** (38 failed, 267 passed at `ef7c1835`) |
| W1-02 (incl. `test_decision_p95_is_under_100_ms`) | 3653 passed |
| W1-03 | 363 passed, 1 skipped (the interpreter finds `gov` without `PYTHONPATH`) |
| W1-04 | 336 passed |
| W1-05 (incl. `test_a_call_waits_under_100_ms_p95_for_the_hook`) | 99 passed |
| W1-15 | 124 passed |
| W1-16 | 167 passed |
| W1-28 | 151 passed |
| W1-30 | 512 passed |
| W1-32 | 81 passed |
| W1-38 | 201 passed |
| W1-46, `-m "not local_only"` | 457 passed, 36 deselected |
| W1-48 | 172 passed |
| W1-50, `-m "not local_only"` | 683 passed, 2 deselected |
| Builder tests `tests/unit` | **2159 passed, 1 skipped** |

The latency cases passed as part of their suites, with the machine under load from other sessions. The
`local_only` live-launch cases were not run, as in §3; the real `~/gov-os-runs` still does not exist.

### Size of the last round

`git show --shortstat 83b0f2f4`: 4 files, 211 insertions, 19 deletions.

| Part | Added | Removed |
|---|---|---|
| `src/gov/guard/decide.py` | 103 | 18 |
| `src/gov/guard/runs.py` | 6 | 1 |
| **Code** | **109** | **19** |
| `tests/unit/guard/test_runs.py` | 73 | 0 |
| `tests/unit/launch/test_runs.py` | 29 | 0 |
| **Builder tests** | **102** | **0** |

The code is 90 lines net, about a third of them docstrings and comments. With the earlier rounds the change's code
is 341 lines added and 50 removed, 291 net, above the estimate of 120 LOC (`est_loc`) by 171 lines.

## 10. One more short round, after the review of the last round (DEC-764, DEC-765)

The review of the last round found two behaviours missing. The owner decided them on 2026-10-18 (DEC-764 and DEC-765;
staged for the owner's commit, not yet in this worktree's register): **A** (DEC-764), the guard refuses `cp --parents`,
and every copy, install or move option that makes the landed path other than `<folder>/<name>`, as doubt, the way it
refuses `ln -t`; **B** (DEC-765), the guard reads option values as values and honours `--`, and judges each call as the
files it writes. The test designer added them as `tests/acceptance/W2-50/test_w2_50_short_round.py` at `41aa00c0`,
tests added after implementation (DEC-136): 53 cases. The suite at `41aa00c0`: 24 failed, 334 passed, every failure in
the new file: A 13; B 9 (`cp -S.t`, `cp -bS.t`, `cp -S -t F`, `cp --suffix -t F`, `install -S.t`, `install -oroot`,
`install -m+t`, `install -gstaff`, `cp -- -t`); the control `install -m 0644 -o root X f` 2 (the README's section "The
review of the last round"). `ln -f` / `ln -sf` onto the own folder's marker (row W2-L354) and a FIFO in the marker's
place (row W2-L350) are not this round's work.

### The correction of §9

This section corrects §9; §9 is left as written.

- **What §9 claimed.** F1: "a copy, install or move into a folder is judged as the folder (as before) and as each file
  it writes in it, `<folder>/<name>`", and with it that row **W2-H056** was closed "for every ticket inside the
  repository".
- **What did not hold at `8a310cb2`** (the tree §9 describes), each shown red by the new file at `41aa00c0`:
  - **`cp --parents`** (and `--parent`, `--par`) writes `<folder>/<source as written>`, not `<folder>/<name>`. The
    guard judged `<folder>/<name>`, so `cp --parents ../../tests/acceptance/W2-90/test_a.py -t <project>/src/app`,
    which lands on the acceptance test, and `cp --parents sub/test_a.py src/app/m/` through a link at a middle level
    were allowed, as were the same forms into the own folder that land in another ticket's folder (13 red).
  - **The option reader** (`_cp_operands`) read any cluster of short options holding a `t` as `-t`, with the rest of
    the word or the next word as its folder; it read an option's separate value as an operand; and it read nothing
    after `--` as an operand. So `cp -S.t X <acceptance test>`, `cp -bS.t …`, `cp -S -t F …`, `cp --suffix -t F …`,
    `install -S.t …`, `install -oroot …`, `install -m+t …` and `cp -- -t <acceptance test>` were allowed,
    `install -gstaff …` was refused for a wrong path (`…/aff/X`), and `install -m 0644 -o root X f` onto an allowed
    file was refused for `<project>/root` (11 red).
  - So W2-H056 was **not** closed at `8a310cb2`: a copy into a folder of the role's paths could still land on the
    acceptance test.
- **§9's difference 19** ("`-T` is read wherever a `T` stands in a cluster of short options; a suffix such as `-S.T`
  is read as `-T` too") no longer holds: since this round a value is a value, so `-S.T` is the suffix `.T` and the
  call is judged as the one it is. `-T` and `--no-target-directory` are read where the tool reads them.
- **W2-H056 now.** For `cp`, `install` and `mv`, read as GNU coreutils 9.4 reads them, a copy, install or move into a
  folder is judged as each file it writes, and a form whose landed path the guard does not read is refused. The
  grounds: the 13 A cases, the B premise and 20 B cases, and the 19 controls of `test_w2_50_short_round.py`, with F1's cases of
  `test_w2_50_extra_review.py`, all green at this round's tree. This record reads W2-H056 as closed within that
  scope; the forms under "What stays open" below are outside it.

### What holds after this round

- **How `cp`, `install` and `mv` are read** (`_copy_args`, DEC-765), as GNU coreutils 9.4 reads them:
  - the short letters that take no value (`cp` `abdfHilLnPprRsTuvxZ`, `mv` `bfinTuvZ`, `install` `bcCdDpsTvZ`) and those
    that take one (`-S`, `-t`, and for `install` `-g`, `-m`, `-o`), the value joined to the letter (`-S.t`, `-oroot`,
    `-m+t`, `-bS.t`) or the next word (`-S -t`, `-o root`); `-Z` takes no value, so `cp -Zt <folder> X` is a copy into
    `<folder>` and stays judged (held by the fail-closed control);
  - the long names, and every abbreviation the tool accepts (a unique prefix, or prefixes that name one option, as
    `--pa` names `--parents` and `--path`); a long name that takes a value takes it after `=` or as the next word
    (`--suffix .t`, `--mode=+t`), one with an optional value only after `=` (`--backup`, `--preserve`, `--context`
    for `cp` and `install`);
  - nothing after `--` is an option (`cp -- -t f` copies the file `-t` onto `f`); a lone `-` is an operand.
  - The tables were checked against the tools on this machine by a script in my temporary folder (each long name is
    known to the tool, takes a value exactly when the table says, and every name in `--help` is in the table): **not a
    committed test**. The acceptance and builder tests hold the forms they name.
- **What is judged.** As before: the operands of `mv`, each `-t` folder, the destination (the last operand), and each
  file a copy, install or move writes in a folder (§9). With an option written after an operand every word after
  the first operand is judged as a possible destination, separate values included (as the earlier reader did, so a
  call read with `POSIXLY_CORRECT` set is judged no less than before; not tested). `install -d` and `cp -l` are read
  from the options as read, so a value (`-S.d`, `-S.l`) or `--debug` no longer reads as either (not tested).
- **Refused as doubt**, with the guard's reason naming `/<guard-unresolvable>`, the target an `ln -t` refusal names
  (DEC-764): `cp --parents`, whatever its source and whether its folder is given as the last operand, `-t` or
  `--target-directory`, in the spellings `--parents`, `--parent`, `--par` (A cases), `--pa` and the old alias
  `--path`, which coreutils 9.4 still accepts (builder tests); the other prefixes (`--pare`, `--paren`) are read
  the same way, not tested one by one; an option the tool does not know (`cp -q`, `install --no-such`); an ambiguous abbreviation
  (`--p`); a value given to an option that takes none (`--parents=x`); an option missing its value at the end
  (`mv X d -S`). Held by the A cases and the builder test
  `test_a_copy_whose_landed_path_is_not_read_is_refused` (10 forms).
- **Backups** (DEC-765, "the files it writes"): with `-b`, `--backup`, `-S` or `--suffix`, the backup
  `<file><suffix>` is judged beside each file the call replaces that is not a folder, and beside the destination
  folder of `mv -T` (which `mv -b -T` renames); a suffix that is empty or holds a slash is read as `~`, as the tools
  do. Held by the builder test `test_a_backup_is_judged_beside_the_file_it_replaces`: `mv -b -T <dir> <own folder>`
  (the backup would land directly in the root) and `cp -S<c> X <own folder>/<marker minus c>` (the backup would
  replace the marker) are refused; the same calls without a backup, and backups into allowed places, are allowed.
  The README's discovery that no case asks this is answered by these builder tests, not by an acceptance test.
- **Allowed as before:** ordinary copies, installs and moves into a folder the session may write; `cp -t` and
  `install -m 644` into an allowed folder; a value with no `t`, a `--`, and the B forms onto an allowed file (the
  controls). `install -m 0644 -o root X f` onto an allowed file is allowed now (red before).

### What stays open

- **Rows W2-L354** (`ln -f` / `ln -sf` onto the own folder's marker) and **W2-L350** (a FIFO in the marker's place):
  not this round's work (DEC-765).
- **`POSIXLY_CORRECT`.** With it set in the session the tools read every word after the first operand as an operand.
  Every such word that does not start with `-` is judged as a possible destination (above), but a word that starts
  with `-` after the first operand (a `-t` there) is not judged as a source landing in that destination
  (`<folder>/-t`). The landed folder itself is judged. Not tested.
- **Numbered backups and `SIMPLE_BACKUP_SUFFIX`.** `--backup=numbered` writes `<file>.~N~` and the environment's
  suffix replaces `~`: the guard judges `<file>~` (or the given suffix) in the same folder instead, so the folder's
  rules hold but a ticket pattern that admits one name and not the other is not read. Not tested.
- **`src/gov/guard/protected.py`** (outside this ticket's paths) still reads the second names of `mv` and `cp -l`
  with the earlier `_cp_operands`, which this round leaves unchanged for it: for `mv -- -t f` it finds no source.
  That reader serves the settings and held-out rules (DEC-548, DEC-553), not the write targets judged here. Not
  tested; returned to the lead.
- **Other tools that write into a folder** (`git clone`, `rsync`, `tar -C`, `unzip -d`) are not read as copies (the
  README's earlier discovery for `git clone`). Not this round's work.
- **Another coreutils version** may read options otherwise. An option this table does not know is refused as doubt,
  so a newer option (9.5's `mv --exchange`) fails closed; a letter that changes from no value to a value would not.

### What the repair changed, file by file

- **`src/gov/guard/decide.py`**:
  - `_COPY_SPEC` and `_COPY_LONG`: the short letters (with and without a value) and the long names (with what each
    takes) of `cp`, `mv` and `install`, as coreutils 9.4 reads them.
  - `_copy_args(name, args)`: the reader. It gives the operands, the options read (each key with its values) and,
    when an option follows an operand, the words after the first operand; `None` when an option cannot be read.
  - The `cp` / `install` and `mv` branches of the Bash target reading are one branch on `_copy_args`. `--parents`
    (key `parents`, for `--path` too) and `None` add `/<guard-unresolvable>`. The rest is as before, read from the
    options as read; the backups are added after.
  - `_copies(operands, dirs, dests, merge)`: takes the destinations and `-T` from the branch, which reads them,
    instead of reading the raw words again.
  - `_cp_operands` and `_option_after_operand` are unchanged: `protected.py` imports the first, `ln` uses the second.
- **`tests/unit/guard/test_runs.py`** — builder tests, regression evidence only (temporary HOME): the doubt forms
  (10); values and `--` (14: refused onto the acceptance test, allowed onto an allowed file); the backups (one case).
- **Not changed:** `src/gov/guard/runs.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`,
  `template/governance/kernel/checks/secrets-indexing.yaml`, every acceptance test.

### Verification of this round

At `83756def`'s tree, each run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` (DEC-732), never with `-x`;
`gov.__file__` is `/home/usain/gov-os-worktrees/W2-50/src/gov/__init__.py`. Two suites took longer than one
foreground call may run (W1-05, whose switch-over case runs other suites for about ten minutes, and W1-30): they were
run in the background to their end and their logs read; the first W1-05 run was stopped by a time limit before its
end and was run again whole.

| Run | Result |
|---|---|
| `tests/acceptance/W2-50` | **358 passed** (24 failed, 334 passed at `41aa00c0`) |
| W1-02 (incl. `test_decision_p95_is_under_100_ms`) | 3653 passed |
| W1-03 | 363 passed, 1 skipped (the interpreter finds `gov` without `PYTHONPATH`) |
| W1-04 | 336 passed |
| W1-05 (incl. `test_a_call_waits_under_100_ms_p95_for_the_hook`) | 99 passed |
| W1-15 | 124 passed |
| W1-16 | 167 passed |
| W1-28 | 151 passed |
| W1-30 | 512 passed |
| W1-32 | 81 passed |
| W1-38 | 201 passed |
| W1-46, `-m "not local_only"` | 457 passed, 36 deselected |
| W1-47 (it holds `cp`, `mv` and `install` forms) | 983 passed |
| W1-48 | 172 passed |
| W1-50, `-m "not local_only"` | 683 passed, 2 deselected |
| Builder tests `tests/unit` | **2184 passed, 1 skipped** (2159 before, and this round's 25) |

The `local_only` live-launch cases were not run, as in §3; the real `~/gov-os-runs` still does not exist.

### Commits and size of this round

- `83756def` — the repair: `src/gov/guard/decide.py`, `tests/unit/guard/test_runs.py`.
- The commit that adds this section — `docs/changes/W2-50-CIT-E.md` only.

`git show --shortstat 83756def`: 2 files, 225 insertions, 52 deletions.

| Part | Added | Removed |
|---|---|---|
| `src/gov/guard/decide.py` | 170 | 52 |
| **Code** | **170** | **52** |
| `tests/unit/guard/test_runs.py` | 55 | 0 |
| **Builder tests** | **55** | **0** |

The code is 118 lines net, about a third of them docstrings, comments and the option tables. With the earlier rounds
the change's code is 511 lines added and 102 removed, 409 net, above the estimate of 120 LOC (`est_loc`) by 289 lines.
