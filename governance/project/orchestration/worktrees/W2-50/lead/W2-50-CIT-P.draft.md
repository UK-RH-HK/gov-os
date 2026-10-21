---
id: W2-50-CIT-P
type: change-impact-proposal
status: PROPOSED
date: 2026-10-16
branch: w2/W2-50
base: w2/W2-50 @ 74403441 (the acceptance tests)
ticket: DAEO-kl5e (W2-50)
author: product-spec (ticket mode, single author)
owner_question: Q-15
decisions_carried: [DEC-728, DEC-723, DEC-159]
state_class: EVIDENCE
---

# W2-50 — Change-impact proposal (CIT-P): the durable scratch root

This proposal is for the owner. The owner approves it or refuses it before any code is written (CAP-33, CAP-33.d;
queued question Q-15). It is not accepted. Nothing in it is decided until the owner answers.

The change makes `~/gov-os-runs/` one durable scratch root, in the guard and in the launcher's sandbox (DEC-728). It
changes three files and adds one, all in the ticket's `allowed_paths`. It changes no specification text, no decision,
no role file and no test. The acceptance tests exist (`tests/acceptance/W2-50/`, commit `74403441`: 139 cases, 48 red
before the change). Their README gives the readings R1 to R8; §5 puts them before the owner.

## 1. What triggers the change

| # | Trigger | Source | State before this change |
|---|---|---|---|
| T1 | Work that writes (indexing, test runs, adoption on a copy) runs on a clone under `~/gov-os-runs/<W2 id>/` | DEC-723 item 3 | Nothing lets a session write there |
| T2 | `~/gov-os-runs/` is one durable scratch root; a session of any role writes only in its own ticket's folder; nothing there is indexed; the change goes through CIT-P | DEC-728 items 1 to 5 | Not built |
| T3 | The guard refuses every write outside the repository except in the temp folder | `src/gov/guard/decide.py`; DEC-108 (the kernel scratch set) | `~/gov-os-runs` is refused like any other place outside |
| T4 | The launcher's sandbox write list holds only the session's own temp folder, and the launcher removes that folder when the session ends | DEC-159, DEC-386; `src/gov/launch/launcher.py` | A launched session's Bash cannot write in `~/gov-os-runs` |
| T5 | Clones under `/tmp` are lost on a reboot | W2-M355 (`docs/plan/WAVE_2_LIST.md`, triaged to W2-50) | Live clones stand under `/tmp` |

The change loosens the guard, so it goes through CIT-P with the owner's approval (DEC-728 item 5; CAP-33.d). The three
options below follow DEC-105's form (CAP-33.e).

## 2. The three options (DEC-105)

| Option | What it means here | Cost |
|---|---|---|
| **Apply now** | W2-50 is built in layer 2, inside its paths, against the existing tests. A fresh reviewer probes it after green; a CIT-E record follows | The ticket's estimate is 120 LOC (`est_loc`), FULL. The WBS puts its close at about day 5, with about 5 days of slack before W2-14 and W2-15a need it, and no time added to the critical path (WBS §3). W2-09, W2-21 and W2-06 each share one file with it and run after it. The points of §6 need the owner's answers first; one of them may add one file to the ticket's paths |
| **Defer** | Record the change and continue the wave without it | No code now. W2-14, W2-15a (and through it W2-15b), W2-24 and W2-27 depend on W2-50 (DEC-728 item 6), so they wait. Only W2-26 may clone under `/tmp` in the meantime (DEC-728 item 7). A clone under `/tmp` is lost on a reboot (W2-M355), and a launched session's temp folder is removed at its end (DEC-386). W2-15a is on the critical path (WBS §3): a defer longer than the slack moves the wave's end. The 48 red tests stay red |
| **Re-baseline** | Reopen DEC-723 and DEC-728 and re-plan where writing work runs | DEC-723 and DEC-728 are the owner's decisions of 2026-10-16. The 139 cases would be retired, and the WBS and the triage revised again. The one place a session may write today that survives the session is inside the repository (`.gov-runtime/scratch/`). DEC-673 says no clone and no programme file goes under `.gov-runtime/` again, and the secrets-indexing check scans everything there (`src/gov/secrets/__init__.py`) |

**The proposer's recommendation: apply now.** This is a recommendation, not a decision. The owner has already decided
what the change is (DEC-728). The tests exist. The ticket has slack before its users need it. Deferring costs the
critical path through W2-15a, and the three tickets that share a file with W2-50 would then change those files first.

## 3. Each change

Each change is described by behaviour. The engineer designs the code.

### 3(a) The guard's outside-repository rule — `src/gov/guard/decide.py`

- **Source:** DEC-728 items 1, 2 and 4; DEC-723 item 3. DEC-108 (the kernel scratch set) is unchanged.
- **Before.** A write target outside the repository is allowed only when it lies in the temp folder
  (`tempfile.gettempdir()`, DEC-108) or is `/dev/null`. Every other place outside is refused, with the reason
  "… to '<path>' denied for role '<role>'". The rule does not look at the session's ticket for a place outside.
- **After.** One more place is allowed outside the repository: the session's own folder, `~/gov-os-runs/<own folder>/`,
  and everything under it. It is allowed to the Write and Edit tools and to the Bash targets the guard judges, for each
  of the six roles (R4). The session must have a known role and a ticket (R3). The folder need not exist yet (R2).
- **Impact.** Every session that runs the guard. Inside the repository nothing changes.
- **Exactly what it loosens.** A write whose resolved target lies under the session's own folder. Writing a path under
  the own folder (for example `mkdir -p` of it) also makes the root when the root does not exist (R2).
- **Exactly what stays refused**, each with the guard's reason:
  - another ticket's folder, and a folder whose name is near the own one (R1);
  - the root itself: a file directly in it, the root path as a file, removing or moving the root (R7 adds `rmdir`, §4);
  - a path that leaves the own folder by `..`, a symbolic link or a hard link (R8, §4); a move or copy across the own
    folder's edge;
  - a session with no ticket, an empty `GOV_TICKET`, or a `GOV_TICKET` that names no ticket (R3); a session with no role
    or an unknown role (CAP-58.c);
  - every other place outside the repository but the temp folder;
  - `~/gov-os-workbench`, and `~/gov-os-worktrees` other than the session's own worktree (DEC-723, DEC-728 item 4).
  The guard's other refusals come before the path rule and are not changed: a frozen project refuses every write, the
  own folder included; held-out paths and the settings file; `dangerouslyDisableSandbox`; unknown tools (DEC-685).
- **Tests** (from the README):
  - own folder: `test_every_role_may_write_a_file_in_its_own_tickets_folder`,
    `test_every_role_may_write_through_bash_in_its_own_tickets_folder`, `test_judged_bash_forms_into_the_own_folder_are_allowed`,
    `test_a_write_deep_inside_a_clone_in_the_own_folder_is_allowed`, `test_a_clone_into_the_own_folder_is_allowed`,
    `test_the_first_write_is_allowed_when_neither_the_root_nor_the_folder_exists`;
  - another ticket's folder: `test_another_tickets_folder_is_refused_to_the_file_tools_and_bash`,
    `test_judged_bash_forms_into_another_tickets_folder_are_refused`, `test_another_tickets_folder_is_refused_to_every_role`,
    `test_a_folder_whose_name_is_near_the_own_is_another_folder`;
  - the root itself: `test_a_file_directly_in_the_root_is_refused`, `test_a_file_directly_in_the_root_is_refused_to_every_role`,
    `test_a_file_in_the_root_spelled_through_dot_is_refused`, `test_the_root_path_itself_as_a_file_is_refused`,
    `test_removing_or_moving_the_root_is_refused`;
  - `..`, links: `test_a_path_that_leaves_the_own_folder_by_dotdot_is_refused`, the five symbolic-link cases
    (`test_a_symbolic_link_in_the_own_folder_to_another_tickets_folder_is_refused`, `…_to_the_root_is_refused`,
    `…_to_a_folder_elsewhere_is_refused`, `…_to_a_file_elsewhere_is_refused`, `test_an_own_folder_that_is_itself_a_link_elsewhere_is_refused`),
    `test_a_link_in_the_repository_to_another_tickets_folder_is_refused`, the three hard-link cases (§4),
    `test_a_move_or_copy_across_the_own_folders_edge_is_refused`;
  - no ticket: `test_a_session_with_no_ticket_may_not_write_under_the_root`, `test_an_empty_gov_ticket_is_no_ticket`,
    `test_a_gov_ticket_that_names_no_ticket_is_no_ticket`, `test_a_session_with_no_role_may_not_write_in_the_folder`;
  - elsewhere: `test_a_path_outside_the_repository_the_temp_folder_and_the_own_folder_is_refused`, control
    `test_the_temp_folder_stays_open`;
  - workbench and worktrees: `test_the_workbench_stays_refused`, `test_another_worktree_stays_refused`,
    `test_the_worktrees_folder_itself_stays_refused`, control `test_the_sessions_own_worktree_stays_open_within_its_paths`.
- **How it is reversed.** Revert the rule's change in `decide.py`, with 3(b). The guard then refuses everything outside
  but the temp folder, as today. What stays behind: every folder and clone made under `~/gov-os-runs`. A revert removes
  none of them, and after it no session can write or remove them; only the owner can, by hand. Who notices: W2-14,
  W2-15a, W2-24 and W2-27 lose their clone place. W2-09 changes the same file after W2-50; a revert after W2-09's merge
  is a conflict in that file.

### 3(b) The new module that names the root and the own folder — `src/gov/guard/runs.py` (new)

- **Source:** DEC-728 items 1 and 2; DEC-723 item 3 (`<W2 id>`); the ticket's second success KPI line.
- **Before.** Nothing. Neither the guard nor the launcher knows `~/gov-os-runs`.
- **After.** One place answers two questions, for the guard and for the launcher alike, so both name the same folder:
  - the root: `~/gov-os-runs`, in the session's home;
  - the session's own folder, from `GOV_TICKET`: the ticket's `external-ref` exactly as written (case and letter suffix
    kept, `W2-99a`), or the ticket's `tk` id when it has no `external-ref` (R1). A missing, empty or unknown
    `GOV_TICKET` gives no folder (R3). The folder follows `GOV_TICKET`, not the worktree's name (R3).
- **Impact.** A new file. Used by 3(a) and 3(c).
- **Exactly what it loosens.** Nothing by itself: it names a folder; 3(a) and 3(c) open it.
- **Exactly what stays refused.** A session without a ticket has no own folder, so nothing under the root is opened
  for it. The `tk`-id folder of a ticket that has a W2 id is another folder (R1).
- **Tests:** `test_a_ticket_without_a_w2_id_writes_in_the_folder_named_by_its_tk_id`,
  `test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written`, `test_the_folder_follows_gov_ticket_not_the_worktree`
  (guard); `test_a_ticket_without_a_w2_id_gets_the_folder_named_by_its_tk_id`,
  `test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written` (launcher); and the refusals
  `test_a_folder_whose_name_is_near_the_own_is_another_folder`, `test_an_empty_gov_ticket_is_no_ticket`,
  `test_a_gov_ticket_that_names_no_ticket_is_no_ticket`.
- **How it is reversed.** Delete the file, with 3(a) and 3(c). It leaves nothing on disk. Before W2-50 closes no other
  ticket uses it; a later ticket that imports it (W2-09, W2-21) would notice.

### 3(c) The launcher's sandbox write list — `src/gov/launch/launcher.py`

- **Source:** DEC-728 item 1; the ticket's second success KPI line ("exactly that folder (not the root)"); DEC-159;
  DEC-386; DEC-161.
- **Before.** The sandbox's `allowWrite` holds one entry, the session's own temp folder (DEC-159). The launcher removes
  that folder when the session ends (DEC-386). A launched session's Bash cannot write anywhere else outside the
  repository.
- **After.**
  - `allowWrite` holds the temp folder and the session's own folder under the root. It never holds the root.
  - Before it starts the session, the launcher makes the root and the own folder when they do not exist. It leaves
    what an existing folder holds alone (R2).
  - The temp folder is still removed at the session's end. The own folder is never removed by the launcher, so a clone
    made there survives the session's end and the next session of the same ticket finds it (R6).
- **Impact.** The five launched roles (DEC-161, DEC-386). The orchestrator is not launched.
- **Note on the ticket's paths.** The ticket's body limits this file to "the sandbox write list only". Making the folder
  before the session starts (R2) is one step beyond that list. The owner's approval of R2 approves that step, or the
  owner names R2 changed.
- **Exactly what it loosens.** A launched session's Bash may write under its own folder.
- **Exactly what stays refused** by the sandbox: another ticket's folder, the root itself, `~/gov-os-workbench`, other
  worktrees, and every other place outside the repository but the session's temp folder. The launcher still refuses
  `--add-dir` and `permissions.additionalDirectories` (DEC-313): the folder enters through the sandbox's write list,
  not as an added directory.
- **Tests:** `test_the_sandbox_may_write_the_sessions_own_folder`, `test_the_sandbox_adds_exactly_the_own_folder_under_the_root`,
  `test_the_sandbox_may_not_write_another_tickets_folder_the_workbench_or_other_worktrees`,
  `test_the_sandbox_keeps_the_sessions_temp_folder`, `test_the_own_folder_exists_when_the_session_starts`,
  `test_a_launch_keeps_what_the_folder_already_holds`,
  `test_a_clone_made_in_the_own_folder_survives_the_sessions_end_and_the_next_session_finds_it`,
  `test_a_launch_of_another_ticket_leaves_the_folder_alone`, and the two naming cases of 3(b).
- **How it is reversed.** Revert the change in `launcher.py`. The sandbox then writes only the temp folder, as today.
  The folders the launcher made stay on disk, with what is in them. Who notices: W2-15a and W2-15b (research, launched)
  can no longer clone there; W2-21 changes the same file after W2-50, so a late revert is a conflict there.

### 3(d) The secrets-indexing exclusion — `template/governance/kernel/checks/secrets-indexing.yaml`

- **Source:** DEC-728 item 3; the ticket's fourth success KPI line ("this repository's secrets-indexing check never
  scans it").
- **Before.** The check's command is `python3 -m gov.secrets`, with no option. It reads every file under
  `.gov-runtime/`, following linked folders (`os.walk(…, followlinks=True)` in `src/gov/secrets/__init__.py`) and
  opening a file link's target. It never walks `~/gov-os-runs` unless a link in `.gov-runtime/` points there. When one
  does, the check scans the clone and goes red, naming the file (the README's red reason for R5).
- **After (R5).** A folder link or a file link from `.gov-runtime/` into `~/gov-os-runs` is not followed. The check
  stays green and prints nothing from there.
- **Impact.** The secrets-indexing family check (CAP-38.b), in this repository and in every project the kernel template
  reaches.
- **Exactly what it loosens.** The check no longer reads what such a link names.
- **Exactly what stays scanned.** Every file of `.gov-runtime/` itself. A linked store folder elsewhere is still
  followed: W1-15's `test_the_check_fails_on_a_canary_in_a_linked_store_folder` (B4) requires the check to follow a link
  to a folder outside the project, in the temp folder. So the exclusion must name `~/gov-os-runs`; "follow no link out
  of the repository" would turn W1-15's B4 red.
- **The indexers need no change.** `gov rebuild` does not follow a link out of the repository, and an adopted clone has
  its own store inside it. Those cases pass today and guard the change.
- **Tests:** `test_the_check_does_not_scan_the_root_through_a_link_in_the_runtime_folder` (a folder link, a file link),
  `test_the_check_is_green_with_a_secret_in_a_clone_under_the_root`, control
  `test_the_check_finds_a_secret_in_the_repositorys_own_store`; and `test_a_link_into_the_own_folder_brings_nothing_of_it_into_the_repositorys_stores`,
  `test_an_adopted_clone_in_the_own_folder_has_its_own_store_inside_it` (the stores).
- **This change cannot be made in the check's file alone.** See §6.1.
- **How it is reversed.** Revert the check's file (and whatever §6.1's answer adds). Nothing stays on disk. W2-06 changes
  the same file after W2-50, so a late revert is a conflict there.

## 4. The stricter parts

- **R7, `rmdir` of the root — stricter than today.** Today the guard does not judge `rmdir`, so `rmdir <root>` is
  allowed to every role. Test: `test_removing_or_moving_the_root_is_refused` (its `rmdir` case is the one red case of
  that test). Judging `rmdir` is a change to how the guard reads Bash forms, not to the outside-repository rule that
  the ticket's body names for `decide.py`. If `rmdir` is judged as a write target everywhere, it is stricter inside the
  repository too: `rmdir` of an empty folder outside a role's paths becomes refused. The owner's approval of R7 approves
  that, or names R7's scope (the root only).
- **R8, a hard link — not stricter than today, but stricter than opening the folder alone.** Today every place outside
  is refused, so the hard-link cases pass. Once the own folder is open, resolving a path does not show that a name in
  it is a hard link to a file elsewhere; R8 keeps such a write refused. Making a hard link from outside with `ln`,
  `cp -l` or `link` is already judged by DEC-334's rule, which treats the link's source as a write target. Tests:
  `test_a_hard_link_in_the_own_folder_to_a_file_elsewhere_is_refused`,
  `test_a_hard_link_in_the_own_folder_to_a_file_of_another_ticket_is_refused`,
  `test_making_a_hard_link_in_the_own_folder_to_a_file_outside_it_is_refused`.

## 5. The readings the owner approves with this proposal

The README's readings, as the test designer chose them. The owner's approval of this proposal approves them, or names
the ones it changes.

| Reading | What it says | Source | Recommendation | Confidence |
|---|---|---|---|---|
| R1 | The folder is the ticket's `external-ref` exactly as written (case and letter suffix kept); the `tk` id only when there is none. Near names are other folders | The KPI's "named by the ticket's W2 id (its external-ref, as for worktrees), or by its tk id when it has none"; WBS §0 rule 2 | As read | High |
| R2 | The launcher makes the root and the own folder before the session starts; the guard does not ask for the folder to exist, so an unlaunched session makes it with its first write | "The folder is created on first use"; DEC-160 (a sandbox path that does not exist yet is untested) | As read | Medium |
| R3 | A forged, unknown or empty `GOV_TICKET` is no ticket; the folder follows `GOV_TICKET`, not the worktree | "Resolved from the session's GOV_TICKET"; the guard's default deny | As read | High |
| R4 | "Any role" is all six roles, the auditor and product-spec included; the own folder is read as the scratch folder outside the repository (DEC-108's counterpart). No role or an unknown role writes nothing. The role files do not say it | DEC-728 item 2, "a session of any role" | As read | Medium |
| R5 | The secrets-indexing check does not follow a link from `.gov-runtime/` into `~/gov-os-runs` | "This repository's secrets-indexing check never scans it" | As read; the other choice is stricter on secrets (§6.1) | Medium |
| R6 | "Survives a restart": after the session ended and its temp folder was removed, the clone is still sound in the own folder, lies in no temp folder, and the next session of the ticket finds it. No reboot is made | W2-M355; DEC-159 | As read | High |
| R7 | Removing the root includes `rmdir` | "The root itself (… or removing it)" | As read; scope in §4 | High |
| R8 | A write through a hard link in the own folder to a file outside it is refused; making such a link is refused | "Reached by … a hard link"; DEC-334 | As read | Medium |

## 6. Points this proposal cannot settle inside the ticket's paths

Each is stated with its options and their costs. The proposer does not choose for the owner.

### 6.1 The secrets-indexing exclusion is not reachable from the check's file alone

The check's command is `python3 -m gov.secrets` and takes no option. The walk that follows linked folders is in
`src/gov/secrets/__init__.py`, which is not in the ticket's `allowed_paths`. W1-15's B4 test requires it to keep
following a linked store folder elsewhere (§3(d)).

| Option | Cost |
|---|---|
| (i) Add `src/gov/secrets/__init__.py` (the link rule only) to the ticket's paths | One line in the ticket, made by the orchestrator after the owner's answer. A few lines of code in the module that holds the walk. W1-15's tests must stay green; its owner is the closed W1-15 |
| (ii) Keep to the listed paths: point the check's command at an entry the new module (3(b)) provides | No change to the ticket's paths. The check's command changes in the kernel template, for every project it reaches. The scan's rule is then split over two modules |
| (iii) Keep following links (stricter on secrets); the test designer rewrites the two link cases | No code for 3(d). A link into `~/gov-os-runs` from `.gov-runtime/` turns the check red (hard-block), as DEC-673's case did. The KPI line "never scans it" is then read as "never scans it unless a link in `.gov-runtime/` names it": a reading the owner approves. A rewrite of acceptance tests, counted under DEC-106 |

### 6.2 `git clone` destinations are not judged by the guard today

The README's discoveries: the guard lets `git clone <src> <dest>` through whatever `<dest>` is. An unsandboxed session
(the orchestrator, a ticket lead) could clone into another ticket's folder, the root or `~/gov-os-workbench` with no
refusal, though DEC-723 item 3 says agents never write in the workbench. A launched session is held by its sandbox's
write list. This exists before the change; the change does not open it.

| Option | Cost |
|---|---|
| Judge clone destinations in this ticket | More code than the 120 LOC estimate; new acceptance cases by the test designer; a stricter rule for every role |
| Put it on the Wave 2 list for the guard ticket that follows (W2-09) | No cost here. The gap stays open for unsandboxed sessions until then |

### 6.3 The file tools in a launched session

The README's discoveries: the guard can allow Write and Edit in the own folder, but Claude Code's own permission check
treats a file outside the working folder on its own. DEC-313 refuses `--add-dir` and `permissions.additionalDirectories`.
So a launched session may be able to write its own folder only through Bash. The guard's half is tested; the real
session's half is not testable in this suite. This is a risk.

| Option | Cost |
|---|---|
| Accept it as a residual, and show it in W2-21's launch work | No cost now. A launched worker that needs Write or Edit there may find out late |
| A short experiment with a real launched session | A research run of its own, before or beside the engineer's work |

### 6.4 A closed ticket's folder

No source says whether a session may still write in the folder of a ticket that is closed. Every fixture ticket of the
suite is `in_progress`, so no test decides it either way.

| Option | Cost |
|---|---|
| The own folder is open only while the ticket is `in_progress`, as a ticket's `allowed_paths` are today and as the launcher requires | Stricter. A clone left in a closed ticket's folder can then be written or removed by no session, only by the owner by hand |
| The own folder is open while the ticket exists, whatever its status | A later session that carries a closed ticket's id may still write there |

### 6.5 The ticket lead's role

The guard knows seven roles: the six of R4 and `ticket-lead` (DEC-434), which may write only its checkpoint, its
scratch and merge-backs. R4 reads "any role" as the six; no case covers `ticket-lead`. R2 says an unlaunched session
"(a lead)" makes the folder with its own first write. No source says whether a ticket lead writes in its ticket's
folder.

| Option | Cost |
|---|---|
| `ticket-lead` is one of "any role" | A lead may write and clone in its ticket's folder, beyond DEC-434's list, read as its scratch outside the repository (R4). One more case for the test designer |
| `ticket-lead` is not | Stricter. A lead cannot make or use the folder; only its launched workers (made by the launcher, R2) and the orchestrator can |

### 6.6 The Contract's text

CAP-58's acceptance and CAP-58.d say that in a launched worker session a Bash write outside the repository is stopped
by the OS sandbox. The text already does not name the temp folder (DEC-159); the own folder becomes a second place it
does not name. The Contract is not in this ticket's paths.

| Option | Cost |
|---|---|
| A row on the Wave 2 list for the next Contract version | One line now; the text is brought in line later |
| Leave the text as it stands | None now; the text keeps two unnamed places |

## 7. Impact list (CAP-33)

| Kind | What | Impact |
|---|---|---|
| Specifications | Contract `contract.yaml`: CAP-58 (path guards), CAP-61 (launcher; CAP-61.d, CAP-61.f), CAP-38.b (the secrets-indexing family) | Behaviour changes under them; no text changes (§6.6) |
| Decisions | DEC-728 (implemented), DEC-723 item 3 (made possible), DEC-108 (unchanged), DEC-159 and DEC-386 (the temp folder unchanged), DEC-313 (unchanged), DEC-334 (its hard-link rule holds the new folder), DEC-160 (the sandbox's link cases stay residuals) | No decision is amended. The owner's answers to R1 to R8 and to §6 become new entries |
| Tickets sharing a file, running after | W2-09 (`decide.py`), W2-21 (`launcher.py`), W2-06 (`secrets-indexing.yaml`) | Each builds on W2-50's version of the file (WBS §3) |
| Tickets that depend on it | W2-14, W2-15a (and through it W2-15b), W2-24, W2-27 (DEC-728 item 6) | They clone into their own folder once W2-50 closes |
| Ticket on `/tmp` until then | W2-26 (DEC-728 item 7) | Unchanged; may move its clone after W2-50 closes |
| Tests | `tests/acceptance/W2-50/` (139 cases) | 48 red turn green; the 91 that pass must still pass |
| Tests read for conflicts | W1-15 B4 (`test_the_check_fails_on_a_canary_in_a_linked_store_folder`); W1-28's `test_w1_28_launch_product_spec.py` (a docstring calls the temp folder the one place outside its sandbox may write; its assertion stays true, README) | Must stay green; no rewrite needed |
| Code | `src/gov/guard/decide.py`, `src/gov/guard/runs.py` (new), `src/gov/launch/launcher.py`, `template/governance/kernel/checks/secrets-indexing.yaml`; possibly `src/gov/secrets/__init__.py` (§6.1 (i)) | As in §3 |
| Role files | `governance/kernel/roles/` | **Not touched.** No role file mentions `~/gov-os-runs`, and the role files are not in this ticket's paths (R4) |
| On disk | `~/gov-os-runs/` | Made on first use; never removed by a revert (§3) |

**Radius: R3.** The change touches the guard, which every session runs, and the launcher, which every worker session
runs; three files that three later tickets share; five tickets that wait on it. It changes no specification text, no
decision and no role file. R3 matches the ticket's FULL profile (CAP-53.a: FULL is R3 and above).

## 8. What follows approval

1. The owner answers: this proposal approved or refused, R1 to R8 approved or changed (§5), and each point of §6.
2. If an answer adds a path (§6.1 (i)) or a test case (§6.4, §6.5, R7's scope), the orchestrator changes the ticket and
   the test designer the tests, first.
3. The engineer implements inside the ticket's paths until the acceptance tests pass.
4. A fresh reviewer probes the result (FULL).
5. A CIT-E record, `docs/changes/W2-50-CIT-E.md`, records what was done: it matches this proposal or lists the
   differences (CAP-33).
