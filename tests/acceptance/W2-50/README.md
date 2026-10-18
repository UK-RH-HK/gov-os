# W2-50 — The durable scratch root: acceptance tests

Written by the independent test designer (MR-3, DEC-069) from the KPI lines of ticket `DAEO-kl5e` (W2-50), the card
in `docs/plan/WAVE_2_WBS.md` §2, the list row W2-M355, and DEC-728, DEC-723, DEC-159, DEC-160, DEC-161, DEC-221 and
DEC-732. Profile FULL. Written before the implementation; no earlier ticket's test was revised.

**358 cases in 10 files**: the first 139 cases in 5 files, written before the change proposal (red run on `w2/W2-50`
at `689bd17e` plus that suite: **48 failed, 91 passed**), 15 cases in `test_w2_50_owner_answers.py` for the owner's
answers to it (DEC-743; see the section below), written before the implementation (red run at `a5ef3c69` plus that
file: **55 failed, 99 passed**), 54 cases in `test_w2_50_review_findings.py` for the review's findings, **tests
added after implementation, from the review (DEC-136)** (red run of the whole suite at `d0c6be04` plus that file:
**34 failed, 174 passed**, about 1.5 minutes; see the section below), and 25 cases in `test_w2_50_last_review.py`
for the last review's findings, **tests added after implementation, from the last review (DEC-136, DEC-751)**, with
80 earlier cases rewritten to make the own folder by a launch (red run of the whole suite at `21ac28b7` plus these
changes: **15 failed, 218 passed, 0 skipped**, about 3 minutes; see its section), and 72 cases in
`test_w2_50_extra_review.py` for the extra review's findings, **tests added after implementation, from the extra
review (DEC-136, DEC-758)**, no earlier case rewritten (red run of the whole suite at `19a4e9fd` plus that file and
this README: **38 failed, 267 passed, 0 skipped**, about 5.5 minutes; see its section), and 53 cases in
`test_w2_50_short_round.py` for the review of the last round, **tests added after implementation, from the review of
the last round (DEC-136, DEC-764, DEC-765)**, no earlier case rewritten (red run of the whole suite at `8a310cb2` plus
that file and this README: **24 failed, 334 passed, 0 skipped**, about 4.5 minutes; see the last section).

## Run

```sh
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src \
  python3 -m pytest tests/acceptance/W2-50 -q -p no:cacheprovider -rs
```

Standard library, `pytest` and PyYAML. No network, nothing installed, no real `claude` session. `git` is needed;
`gitleaks` on `PATH` is needed by the six cases of `test_w2_50_never_indexed.py` (they skip without it; the red
run used gitleaks 8.30.1 at `~/.local/bin`).

## How the suite is built

- **The code under test is this worktree's `src/` (DEC-732).** Every child process gets `PYTHONPATH`: the runner's
  own value when it has one (the run line above sets it per command), else this worktree's `src`.
  `test_w2_50_code_under_test.py` runs a child and checks that its `gov.__file__` lies in this worktree's `src/`.
- **Public interfaces only.** The guard is the kernel's PreToolUse hook (`template/governance/kernel/hooks/
  pretooluse.py`), run as the harness runs it, with the call on stdin, as W1-03's suite runs it. `gov launch`,
  `gov rebuild` and the secrets-indexing check are run as commands. No private module is imported.
- **A temporary home, and a temp folder disjoint from it.** Each test has its own folder (pytest's `tmp_path`) with
  three sibling folders:
  - `home/` is the `HOME` of every process under test. `~/gov-os-runs` is `home/gov-os-runs`, the fixture project is
    the ticket worktree `home/gov-os-worktrees/W2-90`, and the workbench is `home/gov-os-workbench`;
  - `systmp/` is the `TMPDIR` of every process under test, so `tempfile.gettempdir()` in the guard is `systmp/`;
  - `elsewhere/` lies outside the project, `home/` and the temp folder.

  The guard allows writes in the temp folder. Because `home/` is a sibling of `systmp/`, never inside it (the
  sandbox fixture asserts it), nothing under `home/` is allowed for that reason, and a refusal or an allowance under
  `home/gov-os-runs` is the new rule's. The real `~/gov-os-runs`, `~/gov-os-worktrees` and `~/gov-os-workbench` are
  never named to a process, created, listed or written. A session-wide fixture fails the run if the real
  `~/gov-os-runs` appears (it reads only whether the path exists, from the password database's home).
- **The fixture project is built from scratch** (DEC-673): seven tickets, a few files, a `.claude/settings.json`
  written by the test that registers the guard for every tool, and one commit. Only single named files are copied
  into it: the guard hook, `template/governance/kernel/launch/research-allowlist.yaml` (a research launch reads it),
  and, for the index cases, `template/.gitleaks.toml` and a path map made from
  `template/governance/project/path-map.yaml` with an indexed `docs` namespace.
- **The fixture tickets.**

  | tk id | role | W2 id (external-ref) | own folder |
  |---|---|---|---|
  | DAEO-zz90 | engineer (also the test designer's and the ticket lead's) | W2-90 | `~/gov-os-runs/W2-90` |
  | DAEO-zz91 | engineer, "another ticket" | W2-91 | `~/gov-os-runs/W2-91` |
  | DAEO-zz92 | product-spec | W2-92 | `~/gov-os-runs/W2-92` |
  | DAEO-zz94 | independent-auditor | W2-94 | `~/gov-os-runs/W2-94` |
  | DAEO-zz97 | research | W2-97 | `~/gov-os-runs/W2-97` |
  | DAEO-zz98 | engineer | none | `~/gov-os-runs/DAEO-zz98` |
  | DAEO-zz99 | engineer | W2-99a | `~/gov-os-runs/W2-99a` |

- **`gov launch`** runs with a stand-in CLI at `<HOME>/.local/bin/claude`, W1-46's way: it starts no session,
  records the settings the session would get, and does what a plan file asks of a session (look at folders, list
  them, clone, write a file). The sandbox's write list is `sandbox.filesystem.allowWrite` of those settings, as W1-28
  and W1-46 read it; an entry may be `//abs`, `/abs` or `~/rel`, with or without `/**`.
- **"With the guard's reason".** A refusal is a `deny` whose reason is not empty and names the target (as given,
  normalised or resolved) or says why (`gov-os-runs`, `gov-os-workbench`, `gov-os-worktrees`, `ticket`, `outside`,
  `role`). The guard's wording is not prescribed.

## KPI lines, tests and red reasons

Files: `own` = `test_w2_50_guard_own_folder.py`, `ref` = `test_w2_50_guard_refusals.py`, `launch` =
`test_w2_50_launcher.py`, `index` = `test_w2_50_never_indexed.py`.

### Success

| KPI line | Tests | Red reason today |
|---|---|---|
| **1. One durable root**, known to the guard and to the launcher's sandbox | the guard's half: every `own` case below; `ref::test_a_path_outside_the_repository_the_temp_folder_and_the_own_folder_is_refused` with `a-folder-of-the-roots-name-outside-home`, `a-sibling-of-the-root-with-a-longer-name`, `...-with-an-extension` (only `~/gov-os-runs` is the root). The sandbox's half: every `launch` case below | own: the guard denies "Write to '…/home/gov-os-runs/W2-90/…' denied for role 'engineer'"; launch: `allowWrite` holds only the session's temp folder. The three `ref` cases pass today (everything outside is refused) |
| **2. Its own folder only** — the guard allows Write, Edit and judged Bash targets there, for any role | `own::test_every_role_may_write_a_file_in_its_own_tickets_folder` (6 roles × Write, Edit), `own::test_every_role_may_write_through_bash_in_its_own_tickets_folder` (6 roles), `own::test_judged_bash_forms_into_the_own_folder_are_allowed` (redirect, append, tee, touch, mkdir -p, cp into, mv within, rm within), `own::test_a_write_deep_inside_a_clone_in_the_own_folder_is_allowed`, `own::test_a_clone_into_the_own_folder_is_allowed` | denied by the guard, reason "… denied for role '<role>'". `test_a_clone_into_the_own_folder_is_allowed` passes today: the guard does not judge a `git clone` destination (see Discoveries) |
| 2 — named by the W2 id, or the tk id when there is none, resolved from `GOV_TICKET` | `own::test_a_ticket_without_a_w2_id_writes_in_the_folder_named_by_its_tk_id`, `own::test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written`, `own::test_the_folder_follows_gov_ticket_not_the_worktree`; `launch::test_a_ticket_without_a_w2_id_gets_the_folder_named_by_its_tk_id`, `launch::test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written`; and as refusals `ref::test_a_folder_whose_name_is_near_the_own_is_another_folder` (6 names) | own: denied by the guard; launch: not in `allowWrite`. The `ref` names pass today |
| 2 — the launcher adds exactly that folder (not the root) to the sandbox write list | `launch::test_the_sandbox_may_write_the_sessions_own_folder` (5 launched roles), `launch::test_the_sandbox_adds_exactly_the_own_folder_under_the_root` (5 roles), `launch::test_the_sandbox_may_not_write_another_tickets_folder_the_workbench_or_other_worktrees`, `launch::test_the_sandbox_keeps_the_sessions_temp_folder` | "may not write its own folder …: allowWrite is ['//…/systmp/gov-launch-…']" and "the sandbox's entries under the root are [], not exactly the own folder". The last two pass today (nothing is added yet; DEC-159's folder is there) |
| 2 — the folder is created on first use | `own::test_the_first_write_is_allowed_when_neither_the_root_nor_the_folder_exists`, `launch::test_the_own_folder_exists_when_the_session_starts`, `launch::test_a_launch_keeps_what_the_folder_already_holds` | own: denied by the guard; launch: "the session started without its own folder". The last passes today (nothing touches the folder) |
| **3. Survival** — a clone made there survives the session's end and a restart | `launch::test_a_clone_made_in_the_own_folder_survives_the_sessions_end_and_the_next_session_finds_it`, `launch::test_a_launch_of_another_ticket_leaves_the_folder_alone` | the first: "a sandboxed session could not make the clone …: allowWrite is [temp folder only]" (the stand-in is not sandboxed, so the case first asks that a sandboxed session could make the clone). The second passes today |
| **4. Never indexed** — nothing under `~/gov-os-runs` is indexed by this repository's stores; a planted secret there reaches no index of this repository | `index::test_a_link_into_the_own_folder_brings_nothing_of_it_into_the_repositorys_stores` (a control word of the repository must reach the store) | passes today: `gov rebuild` does not follow a link out of the repository. It stays as the guard on the change |
| 4 — an adopted product clone there has its own store inside the clone, not this repository's | `index::test_an_adopted_clone_in_the_own_folder_has_its_own_store_inside_it` | passes today. The repository's stores are compared without their `logs/` folders: the code index's daemon may write its log after the rebuild returned |
| 4 — this repository's secrets-indexing check never scans it | `index::test_the_check_is_green_with_a_secret_in_a_clone_under_the_root`, `index::test_the_check_does_not_scan_the_root_through_a_link_in_the_runtime_folder` (a folder link, a file link from `.gov-runtime/scratch/`), with the control `index::test_the_check_finds_a_secret_in_the_repositorys_own_store` | the link cases: "the repository's check scanned ~/gov-os-runs through a-folder-link / a-file-link" — today the check follows a link in `.gov-runtime/` and reports "secret found in derived store: .gov-runtime/scratch/runs/clone/.gov-runtime/store.txt" (reading R5). The other two pass today |

### Failure (each refused, with the guard's reason)

| KPI line | Tests | Today |
|---|---|---|
| another ticket's folder | `ref::test_another_tickets_folder_is_refused_to_the_file_tools_and_bash`, `ref::test_judged_bash_forms_into_another_tickets_folder_are_refused` (touch, mkdir -p, cp into, mv into, rm in, tee), `ref::test_another_tickets_folder_is_refused_to_every_role` (6 roles), `ref::test_a_folder_whose_name_is_near_the_own_is_another_folder` (a ticket that does not exist, a case change `w2-90`, `W2-900`, `W2-90a`, `W2-90.old`, the tk-id folder of a ticket that has a W2 id) | pass (the guard refuses everything outside the repository but the temp folder) |
| the root itself (a file directly in it, or removing it) | `ref::test_a_file_directly_in_the_root_is_refused`, `ref::test_a_file_directly_in_the_root_is_refused_to_every_role`, `ref::test_a_file_in_the_root_spelled_through_dot_is_refused` (`root/./f`, `root/W2-90/./../f`), `ref::test_the_root_path_itself_as_a_file_is_refused`, `ref::test_removing_or_moving_the_root_is_refused` (`rm -rf root`, `root/`, `root/.`, `root/W2-90/..`, `rmdir root`, `mv root …`) | pass, **except `rmdir`**: red, "Bash `rmdir …/home/gov-os-runs` was not refused: decision=allow" — the guard does not judge `rmdir` today |
| a path outside it reached by `..`, a symbolic link or a hard link | `ref::test_a_path_that_leaves_the_own_folder_by_dotdot_is_refused` (5 paths × Write, Edit, Bash), the symbolic-link cases (to another ticket's folder, to the root, to a folder and to a file elsewhere, the own folder itself a link, a repository link into another ticket's folder), the hard-link cases (an existing hard link in the own folder to a file elsewhere or of another ticket, × Write, Edit, Bash; making one with `ln`, `cp -l`, `link` from elsewhere or another ticket), `ref::test_a_move_or_copy_across_the_own_folders_edge_is_refused` (7 moves and copies in and out) | pass |
| a session with no ticket | `ref::test_a_session_with_no_ticket_may_not_write_under_the_root` (6 roles, three targets), `ref::test_an_empty_gov_ticket_is_no_ticket`, `ref::test_a_gov_ticket_that_names_no_ticket_is_no_ticket` (2), `ref::test_a_session_with_no_role_may_not_write_in_the_folder` | pass |
| any path outside the repository other than the temp folder and the session's own folder | `ref::test_a_path_outside_the_repository_the_temp_folder_and_the_own_folder_is_refused` (elsewhere, HOME, a dotfile of HOME, two siblings of the root, a folder of the root's name outside HOME), control `ref::test_the_temp_folder_stays_open` | pass |
| `~/gov-os-workbench` and `~/gov-os-worktrees` (other than the own worktree) stay refused | `ref::test_the_workbench_stays_refused`, `ref::test_another_worktree_stays_refused`, `ref::test_the_worktrees_folder_itself_stays_refused`, control `ref::test_the_sessions_own_worktree_stays_open_within_its_paths` | pass |

The refusals that pass today are expected to: the guard refuses every write outside the repository but the temp
folder, so they hold now. They are here so that the change that opens the own folder opens nothing else; each must
still pass once the own-folder cases are green.

### Also

`test_w2_50_code_under_test.py::test_a_child_process_imports_this_worktrees_gov` (DEC-732): passes when run as above.

## The owner's answers (DEC-743, 2026-10-17)

The owner approved the change proposal (`docs/changes/W2-50-CIT-P.md`, its closing section) with answers that fix
behaviour the first suite left open. They are tested in `answers` = `test_w2_50_owner_answers.py`, as described
behaviour (DEC-136), written before the implementation. No file of the first suite was changed. For each answer the
first suite's cases that already hold part of it are named; only what was missing was added (DEC-221).

| Answer | KPI line it holds | Already held by | New cases | Red reason today |
|---|---|---|---|---|
| **1. R7 is scoped to the root**: `rmdir` of `~/gov-os-runs` is refused, in each spelling of the root | failure: the root itself (… or removing it) | `ref::test_removing_or_moving_the_root_is_refused[rmdir]` (plain) | `answers::test_rmdir_of_the_root_is_refused_in_each_spelling` (`root/`, `root/.`, `root/W2-90/..`) | "Bash `rmdir …/home/gov-os-runs/` was not refused: decision=allow" (likewise `/.` and `/W2-90/..`): the guard does not judge `rmdir` |
| 1 — `rmdir` is not judged everywhere: inside the repository, outside the role's paths, it stays as today | failure: the root itself; DEC-743 1 (scope) | none | `answers::test_rmdir_of_an_empty_folder_in_the_repository_outside_the_paths_stays_as_today` | passes today: measured at `a5ef3c69`, the guard **allows** `rmdir` of an empty `docs/empty` for the engineer (paths `src/app/**`); the case holds that decision, so judging `rmdir` everywhere turns it red |
| 1 — `rmdir` of the own folder's empty sub-folder stays allowed once the folder is open | success 2 (Bash targets there) | none | `answers::test_rmdir_of_an_empty_folder_inside_the_own_folder_stays_allowed` | passes today (`rmdir` is not judged); must stay green once the rule judges the root |
| **2. R2's step**: the launcher makes the root and the own folder before the session starts, leaves what is there alone, makes no other folder under the root | success 2 (created on first use) | `launch::test_the_own_folder_exists_when_the_session_starts` (own made, W2-91 not), `launch::test_a_launch_keeps_what_the_folder_already_holds`, `launch::test_a_launch_of_another_ticket_leaves_the_folder_alone` | `answers::test_the_first_launch_makes_the_root_with_the_own_folder_and_nothing_else` (the session finds the root holding exactly `[W2-90]`), `answers::test_a_launch_into_an_existing_root_makes_only_the_own_folder_and_leaves_the_rest_alone` (a root with `W2-77/` and `W2-91/clone/`: it then holds those and `W2-90`, the rest unchanged) | "the root … held None, not exactly the own folder ['W2-90']" and "the root held ['W2-77', 'W2-91'], not ['W2-77', 'W2-90', 'W2-91']": the launcher makes no folder today |
| **3. The link rule (§6.1 (i))**: the check does not follow a link from `.gov-runtime/` into `~/gov-os-runs` | success 4 (the check never scans it) | `index::test_the_check_does_not_scan_the_root_through_a_link_in_the_runtime_folder` (a folder link to the own folder, a file link to a file in it) | `answers::test_the_check_does_not_scan_the_root_through_a_link_to_the_root_itself` (a folder link to the root, not to a folder under it) | "the repository's check scanned ~/gov-os-runs through a link to the root itself": the check reports "secret found in derived store: .gov-runtime/scratch/runs-root/W2-90/clone/.gov-runtime/store.txt" |
| 3 — a linked folder elsewhere is still followed (W1-15's B4 stays green) | success 4; DEC-743 3 | W1-15's own suite only | `answers::test_the_check_still_follows_a_linked_folder_elsewhere` (a link to `elsewhere/shared-store` with a secret; the root exists too) | passes today (the check follows every link); the check must still go red after the change, so "follow no link out of the project" fails this case |
| 3 — a near name of the root (`~/gov-os-runs-old`) is elsewhere | success 4; R1's near-name reading for the root | none | `answers::test_the_check_follows_a_link_to_a_folder_whose_name_only_starts_with_the_roots` | passes today; turns red if the exclusion matches the root's name as a prefix |
| **4. §6.4**: the own folder is open only while the ticket is `in_progress` | success 2 (resolved from `GOV_TICKET`); failure: a session with no ticket | none (every fixture ticket is `in_progress`) | `answers::test_the_folder_of_a_ticket_that_is_not_in_progress_is_closed` (`open`, `closed`: Write, Edit, Bash redirect, `mkdir -p`), with the control `answers::test_the_same_ticket_in_progress_opens_its_folder` | the refusals pass today (everything outside is refused); the control is red: "Write on …/gov-os-runs/W2-95/notes.txt by the engineer on DAEO-zz95 (in_progress) was not allowed: … denied for role 'engineer'" |
| **5. §6.5**: `ticket-lead` is not among "any role" | success 2 ("any role", R4); failure: any path outside | none (R4's six roles only) | `answers::test_a_ticket_lead_may_not_write_in_its_tickets_folder` (Write, Edit, Bash redirect, `mkdir -p`), with the control `answers::test_a_ticket_lead_keeps_its_scratch_in_the_repository` | both pass today: the guard knows `ticket-lead` (its scratch is allowed) and refuses the folder like any place outside, "Write to '…/gov-os-runs/W2-90/notes.txt' denied for role 'ticket-lead'". The refusal must still hold once the folder opens for the six roles |

**The fixture ticket of answer 4.** `DAEO-zz95` (engineer, W2 id `W2-95`, folder `~/gov-os-runs/W2-95`), written into
the fixture project by the case from the suite's own ticket text with only its `status` line changed, and committed.
The control writes it `in_progress` the same way, so a refusal for `open` or `closed` is the status's, not a fault of
the ticket file.

**Red run (whole suite, at `a5ef3c69` plus the new file): 55 failed, 99 passed.** The new file: 7 red (the three
`rmdir` spellings, the two launcher cases, the link to the root itself, the `in_progress` control) and 8 green (the
two `rmdir` controls, the two followed links, the two refusals of answer 4 and the two cases of answer 5).

### Discoveries of this round (no test)

- **`rmdir` under the root but not of it.** With R7 scoped to the root, `rmdir ~/gov-os-runs/W2-91` (another ticket's
  empty folder) stays unjudged, as today, though the failure line refuses "another ticket's folder". And
  `rmdir -p ~/gov-os-runs/W2-90/sub` removes the root too when it is otherwise empty. Neither is a spelling of the
  root, so neither is tested; the owner's scope is kept. Both are W2-09's to judge with the guard's Bash forms.

## The review's findings: tests added after implementation, from the review (DEC-136)

The review of the implemented ticket found three behaviours the suite missed. The lead passed them on as described
behaviour; they are tested in `review` = `test_w2_50_review_findings.py`, through the guard's hook and `gov launch`
with the stand-in CLI, as the rest of the suite. No existing test file, support module or conftest was changed; the
new file builds what it needs from the support module's public pieces. One sandbox form is new: `_InsideTheOwnFolder`,
the suite's `Sandbox` with the fixture project at `~/gov-os-runs/W2-90/clone` of the temporary HOME (the same folders,
only the project's location differs). Tickets are written as the suite writes them, `external-ref: <name>` with the
value as written (no quoting), the form the review's examples have.

| Behaviour | New cases | Red reason today | Green today, and why |
|---|---|---|---|
| **1. A project inside the session's own folder keeps every in-project rule** (Write, Edit and a judged Bash redirect, with the guard's reason) | `review::test_a_project_inside_the_own_folder_keeps_its_refusals` × 8 places × 2 locations: an acceptance test by the engineer, and by the orchestrator; `.gov-runtime/freeze`; `.gov-runtime/findings.jsonl`; `.tickets/DAEO-zz90.md`; `.claude/settings.json`; the guard hook; `docs/notes.md` (outside `src/app/**`) | `inside-the-own-folder`: "Write on …/gov-os-runs/W2-90/clone/<place> by <role> on DAEO-zz90 … was not refused: decision=allow": the own-folder allowance covers the whole clone | the 8 `a-worktree` cases: the control that each rule holds in another project (reason "Write to '…' denied for role '…'") |
| 1 — what the rules allow stays allowed there | `review::test_a_project_inside_the_own_folder_keeps_what_its_rules_allow` × 3 × 2: `src/app/main.py`, `.gov-runtime/scratch/notes.md`, an acceptance test by the test designer | none | all 6: the controls of the refusals; they must stay green |
| 1 — the own folder outside such a project gives that session nothing (DEC-108's counterpart) | `review::test_the_own_folder_outside_a_project_inside_it_gives_that_session_nothing` (a file beside the clone, a file in a sibling clone, `mkdir -p` of a sibling) | "Write on …/gov-os-runs/W2-90/notes.txt (beside the project …) was not refused: decision=allow" | — |
| 1 — `gov launch` there puts no entry holding the project's root in the write list; the temp folder stays | `review::test_a_launch_in_a_project_inside_the_own_folder_does_not_add_the_project` | "the sandbox of a session in the project …/W2-90/clone may write the project itself through ['//…/gov-os-runs/W2-90']" | — |
| **2. Only a plain folder name names a folder**: the guard refuses a write in the folder a name that is not plain would give (Write, Edit, Bash redirect, `mkdir -p`), and for a glob name in a folder the glob matches | `review::test_a_name_that_is_not_a_plain_folder_name_gives_no_own_folder` × 11: `*`, `**`, `W2-9?`, `W2-[9]3`, `W2'90`, `W2 90`, `W2-90#a`, `~W2-90`, `-W2-90`, `.hidden`, `..` | "Write on …/gov-os-runs/<name>/notes.txt by the engineer on DAEO-zz80 (external-ref '<name>') was not refused: decision=allow" (10 names) | `dot-dot`: `~/gov-os-runs/..` is HOME, which the guard refuses already; it stays as the guard on the change |
| 2 — control: a plain name with `.` and `_` names its folder | `review::test_a_plain_folder_name_with_dot_and_underscore_names_the_folder` (`W2-90_b.1`, the same ticket form) | none | passes today; shows the refusals above are the name's, not the ticket form's |
| 2 — the launcher neither makes the folder nor adds an entry at, under or above the root, and the write list holds no pattern; the temp folder stays | `review::test_the_launcher_neither_makes_nor_adds_a_folder_for_a_name_that_is_not_plain` × 7: `*`, `**`, `W2-[9]3`, `W2'90`, `W2 90`, `-W2-90`, `..` | "the sandbox of a session on DAEO-zz80 (external-ref '*') may write at or under the root through ['//…/gov-os-runs/*']" (likewise `/**`, `/W2-[9]3`, …; 6 names) | `dot-dot`: the launcher adds nothing for it today; it stays as the guard on the change |
| 2 — control: the launcher adds exactly the folder of a plain name and makes it | `review::test_the_launcher_adds_the_folder_of_a_plain_name_with_dot_and_underscore` | none | passes today |
| **3. One folder belongs to one ticket**: two tickets with the external-ref `W2-90`; MAIN's session refused there whatever the other's status | `review::test_a_folder_two_tickets_name_is_refused_to_the_session_of_either` × `in_progress`, `open`, `closed` | "Write on …/gov-os-runs/W2-90/notes.txt by the engineer on DAEO-zz90 (DAEO-zz81 names it too, <status>) was not refused: decision=allow" | — |
| 3 — the other ticket's session gets it neither | `review::test_the_other_ticket_naming_the_folder_gets_it_neither` (DAEO-zz81, `in_progress`) | "… by the engineer on DAEO-zz81 … was not refused: decision=allow" | — |
| 3 — an external-ref equal to the tk id another ticket's folder is named by: refused to both sessions | `review::test_an_external_ref_equal_to_another_tickets_tk_id_folder_is_refused_to_both` × 2 (DAEO-zz98, which has no external-ref; DAEO-zz82, external-ref `DAEO-zz98`) | "Write on …/gov-os-runs/DAEO-zz98/notes.txt by the engineer on <tk> … was not refused: decision=allow" | — |
| 3 — control: a ticket whose name no other shares keeps its folder, in the same project | `review::test_a_ticket_whose_name_no_other_shares_keeps_its_folder` (W2-91) | none | passes today |
| 3 — the launcher neither makes nor adds a shared folder; the temp folder stays | `review::test_the_launcher_neither_makes_nor_adds_a_folder_two_tickets_name` × 2 (the same external-ref of a closed ticket; an external-ref equal to the tk id) | "the sandbox of a session on DAEO-zz90 may write the shared folder …/gov-os-runs/W2-90 through ['//…/gov-os-runs/W2-90']" (likewise DAEO-zz98) | — |
| 3 — control: the launcher gives the unshared ticket exactly its folder, made | `review::test_the_launcher_keeps_the_folder_of_a_ticket_whose_name_no_other_shares` (W2-91, beside a shared W2-90) | none | passes today |

**The fixture tickets of this file**, written into the fixture project by the case from the suite's ticket text (an
engineer ticket on `src/app/**`, no `wbs_id`), with the `external-ref` line added and, where named, the status
changed, and committed with the rest of the project:

| tk id | external-ref | used by |
|---|---|---|
| DAEO-zz80 | the case's name (behaviour 2) | the name cases |
| DAEO-zz81 | `W2-90` (MAIN's), `in_progress`, `open` or `closed` | behaviour 3, the same external-ref |
| DAEO-zz82 | `DAEO-zz98` (the tk id NO_W2_ID's folder is named by) | behaviour 3, a name equal to a tk id |

**Red run (whole suite, at `d0c6be04` plus the new file): 34 failed, 174 passed, 0 skipped.** The new file: 34 red,
20 green (the 8 worktree refusals and the 6 allowances of behaviour 1, the two `..` cases, and the four controls of
behaviours 2 and 3). Every earlier case still passes (154).

### Discoveries of this round (no test)

- **A quoted `external-ref` is read two ways.** With `external-ref: "W2-90_b.1"` (YAML quotes), measured at
  `d0c6be04`: the guard allows `~/gov-os-runs/"W2-90_b.1"/…` and refuses `~/gov-os-runs/W2-90_b.1/…`, and the
  launcher adds and makes `~/gov-os-runs/"W2-90_b.1"`. Both keep the quotes, so the two agree, and under behaviour 2
  such a name (it holds a quote) gives no folder. A YAML reader would give the plain `W2-90_b.1`. No source says
  which reading a ticket's front matter has; `tk` writes the value unquoted. Not tested: the cases write values
  unquoted, as `tk` does.
- **A name holding `/`** (`external-ref: W2-91/sub`) is refused by the guard and given nothing by the launcher
  today; behaviour 2 holds it too (a `/` is not allowed in a plain name). Not tested beyond `..`.

## The last review's findings: tests added after implementation, from the last review (DEC-136, DEC-751)

The second and last review found two behaviours the suite missed. The orchestrator decided them (DEC-751,
2026-10-17, delegated, stricter only): P-A (a), the launcher writes a record in the own folder naming the
repository's git common directory, and the guard and the launcher refuse a folder whose record is missing or names
another repository; P-B (a), the secrets walk follows a link whose target stays inside the repository being scanned,
even under the root (W1-15's B4 stays green). They are tested in `last` = `test_w2_50_last_review.py`, through the
guard's hook, `gov launch` with the stand-in CLI and the secrets-indexing check, as the rest of the suite.

**How the record is made.** Only the public way: `gov launch` with the stand-in CLI in the project whose folder it is
(`support.open_own_folder`, or the new file's fixture `first`). No case writes, names or reads the record, or assumes
its file name or form (DEC-462). Where a case asks that a launch "changes nothing" in a folder, it compares the
folder's entries by name, kind, size and modification time, reading no file. "Another repository" is a project whose
git common directory differs: one built apart from scratch, or a `git clone` of the fixture project made inside the
test's own folder. "The same repository" is the fixture project or a `git worktree add` of it, inside the test's own
folder.

| Behaviour | New cases | Red reason today (`21ac28b7`) | Green today, and why |
|---|---|---|---|
| **1. A folder belongs to the one repository whose launch made it** — control: the launching repository's session keeps its folder (Write, Edit, Bash redirect, `mkdir -p`, `rm -rf` of a sub-folder) | `last::test_the_launching_repositorys_session_keeps_its_folder` | none | passes: the control; it must stay green |
| 1 — control: a later launch in the same repository keeps the folder, the test's own file in it, and exactly its entry under the root; the guard still allows | `last::test_a_later_launch_in_the_same_repository_keeps_the_folder_its_content_and_its_entry` | none | passes: the control |
| 1 — control: a second worktree of the same repository (its ticket `in_progress`) gets the same folder, in the guard and in its launch's write list | `last::test_a_second_worktree_of_the_same_repository_gets_the_same_folder` | none | passes: the control; a record that named the worktree instead of the common directory turns it red |
| 1 — another repository's session, its `in_progress` ticket of the same name, gets nothing there: Write, Edit, a Bash redirect, `mkdir -p` and `rm -rf` of the folder refused with the guard's reason; the first project's session keeps the folder (control in the same case) | `last::test_another_repositorys_session_gets_nothing_in_a_folder_the_first_made` × 3 forms: (a) `a-project-built-apart-outside-the-root` (`~/projects/second`, ticket W2-91), (b) `a-clone-inside-the-first-projects-own-folder` (`~/gov-os-runs/W2-90/clone`, ticket W2-91), (c) `a-clone-of-the-first-project-outside-the-root` (`~/clones/third`, ticket W2-90) | "Write on …/gov-os-runs/<W2-91 or W2-90>/work/README.md by the engineer on <tk> of another repository <project> (<form>) was not refused: decision=allow" (3) | — |
| 1 — `gov launch` in that other repository adds no entry at, under or above the root, changes nothing the folder holds (the record included), and keeps the temp folder | `last::test_a_launch_in_another_repository_neither_adds_nor_changes_the_folder` × the same 3 forms | "the sandbox of a session on <tk> in another repository <project> (<form>) may write at or under the root through ['//…/gov-os-runs/<W2-91 or W2-90>']" (3) | — |
| 1 — a folder made by hand gives no session anything (Write, Edit, Bash redirect, `mkdir -p`, `rm -rf` refused with the guard's reason) | `last::test_a_folder_made_by_hand_gives_no_session_anything` × `before-any-launch`, `beside-a-launched-folder` (OTHER's W2-91 launched, W2-90 by hand) | "Write on …/gov-os-runs/W2-90/work/README.md (a folder made by hand, <layout>) was not refused: decision=allow" (2) | — |
| 1 — a folder that does not exist yet gives no session anything (Write, Edit, Bash redirect, `mkdir -p`) | `last::test_a_folder_that_does_not_exist_yet_gives_no_session_anything` × the same 2 layouts | "Write on …/gov-os-runs/W2-90/notes.txt (the own folder does not exist yet, <layout>) was not refused: decision=allow" (2): R2's guard half, now replaced | — |
| 1 — a launch neither adds nor records a folder that was there before any launch: no entry at or under the root, the folder's entries unchanged (an empty folder stays empty), the temp folder kept, and the guard still refuses a Write there | `last::test_a_launch_neither_adds_nor_records_a_folder_that_exists_without_a_record` × `empty`, `holding-a-file` | "the launch added a folder that no launch made (<content>) through ['//…/gov-os-runs/W2-90']" (2) | — |
| **2. A project's own secrets check follows a link that stays inside the project, also under the root** — a link in its `.gov-runtime/` to a folder or file of the same project outside `.gov-runtime/` holding a planted secret: red. Premise in each case: with no link, the check is green (it scans only `.gov-runtime/`) | `last::test_a_projects_own_check_follows_a_link_that_stays_inside_the_project` × 2 locations (`outside-the-root`: the fixture worktree; `a-clone-under-the-root`: its `git clone` at `~/gov-os-runs/W2-90/clone`) × 3 links (`.gov-runtime/packets` → `shared-store/`; `.gov-runtime/scratch/kept` → `kept-store/`; the file link `.gov-runtime/store.txt` → `kept/store.txt`) | `a-clone-under-the-root` (3): "the check of the project …/gov-os-runs/W2-90/clone (a-clone-under-the-root) did not follow <link> …, a place of the same project that holds a secret: it is green" (CIT-E difference 10) | `outside-the-root` (3): the same layout outside the root is red today (the check follows a link elsewhere, W1-15's B4); they must stay green |
| 2 — control: from the clone's `.gov-runtime/`, a link to a place under the root but outside the clone is still not followed (DEC-743 3): green, the secret not printed | `last::test_a_link_under_the_root_but_outside_the_project_is_still_not_followed` × `a-sibling-in-the-same-own-folder` (`W2-90/sibling-store`), `another-tickets-folder` (`W2-91/store`), `the-root-itself` (secret in `W2-77/store`) | none | passes (3): the control; "follow every link from a project under the root" turns it red |
| 2 — control: this repository's check (the worktree outside the root) does not follow a link into a folder of a clone under the root | `last::test_this_repositorys_check_does_not_follow_a_link_into_a_clone_under_the_root` | none | passes: the target lies inside *a* project, but not the scanned one; "follow a link into any repository" turns it red. The other forms are held by `index::test_the_check_does_not_scan_the_root_through_a_link_in_the_runtime_folder` and `answers::test_the_check_does_not_scan_the_root_through_a_link_to_the_root_itself` |

**Red run (whole suite, at `21ac28b7` plus these changes): 15 failed, 218 passed, 0 skipped.** The new file: 15 red,
10 green (the 3 controls of behaviour 1, the 3 outside-the-root links and the 4 controls of behaviour 2). Every
earlier case still passes (208), the 80 rewritten among them. W1-15's suite, run to its end: **124 passed**.

### Earlier cases rewritten (DEC-491; `Rewrite-Reason:` names DEC-751)

Behaviour 1 makes a folder that no launch made give no session anything, so each earlier case that made the own
folder by hand (or not at all) and expects a write there allowed now makes it by `gov launch` of the fixture project
first. The expectation of every case is unchanged. Refusal cases whose setup built the own folder by hand are made by
a launch too, so that each refusal stays the rule's, not that of a folder no launch made (before DEC-751 a folder made
by hand was open, so those refusals were judged against an open folder; this keeps them so).

| File | Change | Cases |
|---|---|---|
| `w2_50_support.py` | new public helper `open_own_folder(sandbox, ticket, role, folder)`: `gov launch` of the ticket with the stand-in CLI, asserting the folder made; a docstring paragraph | — |
| `own` | `test_every_role_may_write_a_file_in_its_own_tickets_folder` (12), `test_every_role_may_write_through_bash_in_its_own_tickets_folder` (6), `test_judged_bash_forms_into_the_own_folder_are_allowed` (8, through `_prepare_own`), `test_a_write_deep_inside_a_clone_in_the_own_folder_is_allowed`, `test_a_ticket_without_a_w2_id_writes_in_the_folder_named_by_its_tk_id`, `test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written`, `test_the_folder_follows_gov_ticket_not_the_worktree` (OTHER launched in the W2-90 worktree): the folder made by a launch of the ticket | 30 |
| `own` | `test_the_first_write_is_allowed_when_neither_the_root_nor_the_folder_exists`: neither exists before the first launch; the launch makes them (R2's step), then the first write in it is allowed. The guard half of R2 ("an unlaunched session makes it with its first write") is replaced by DEC-751; the refusal of a folder that does not exist yet is in `last` | 1 |
| `ref` | `_populate` makes MAIN's and OTHER's folders by a launch (setup only): the cases that call it — another ticket's folder (7), a file in the root (1), removing the root (6), `..` (5), the symbolic links (5), the hard links (8), the moves (7) | 39 |
| `answers` | `_populate` by a launch: the `rmdir` spellings of the root (3) and `rmdir` inside the own folder (1); `test_the_same_ticket_in_progress_opens_its_folder` (launch of DAEO-zz95); `test_the_folder_of_a_ticket_that_is_not_in_progress_is_closed` (launched while `in_progress`, then its status changed and committed; 2); `test_a_ticket_lead_may_not_write_in_its_tickets_folder` (MAIN launched first) | 8 |
| `review` | `test_a_plain_folder_name_with_dot_and_underscore_names_the_folder` (DAEO-zz80 launched), `test_a_ticket_whose_name_no_other_shares_keeps_its_folder` (OTHER launched) | 2 |

**Not changed, and why.** `own::test_a_clone_into_the_own_folder_is_allowed` passes either way (the guard does not
judge a clone's destination). `launch::test_a_launch_keeps_what_the_folder_already_holds` makes the folder by hand and
asks that the session find exactly `['earlier']` and the file kept: DEC-751 keeps that (a launch writes no record
into a folder that exists without one). `launch::test_a_launch_of_another_ticket_leaves_the_folder_alone` and the two
launch cases of `answers` hold nothing a record changes (the record lies inside the made folder). The other refusal
cases (`review`'s names that are not plain, shared names, the folder beside a project inside it; `ref`'s cases that
build no folder) keep their folders as they were: no launch can make those folders, or none is needed. No earlier
ticket's test was changed.

### Discoveries of this round (no test)

- **An unlaunched session no longer makes the own folder.** R2's guard half (DEC-743's approved reading) let an
  unlaunched session (the orchestrator) make the folder with its first write. Under DEC-751 the orchestrator writes
  there only after a launch of the ticket made the folder. Tested as described (a folder that does not exist yet gives
  nothing); the orchestrator's own way in is the lead's to confirm with the owner.
- **The record lies in a folder its session may write.** The ticket's own session may remove or change what the
  launcher wrote there, and so close its own folder; it cannot open another repository's (it writes nowhere else). No
  source says the record is protected from its own session; not tested.

## The extra review's findings: tests added after implementation, from the extra review (DEC-136, DEC-758)

An extra independent review found two behaviours the suite missed. The owner decided them (DEC-758 item 1,
2026-10-17; staged for the owner's commit, not yet in this worktree's register): **F1**, every copy or install into a
folder is judged as each file it writes, `<folder>/<name>`, under the same link and hard-link rule as a direct write
(rows W2-H056 and W2-L349); **F2**, a project whose real root is inside `~/gov-os-runs` gets no own folder. They are
tested in `extra` = `test_w2_50_extra_review.py`, through the guard's hook with the call on stdin and `gov launch`
with the stand-in CLI, as the rest of the suite. A FIFO in the marker's place is row W2-L350, not this round's: no
test. No earlier test file, support module or conftest was changed; no earlier ticket's test conflicts.

**How the cases are built.** The sources of the copies are files of the test's own in `elsewhere/` (`payload.py`,
`first.py`, `s/payload.py`); the destination folder `d` already holds, at the source's name `payload.py`, the entry
of the case. Each refusal case first asks the guard for a direct Write on that same file (`d/payload.py`, or
`d/s/payload.py` for a linked folder, or the marker by its name) and expects it refused: that is the premise that the
direct write is refused today, so the copy's refusal is the same rule's. No allowed command is ever run: the guard is
only asked. **The marker's name** is not taken from code: right after `gov launch` made the own folder, the case lists
that folder and takes its one entry (a premise asserts there is exactly one, a regular file). Its content is never
read or written (DEC-462). **A project under the root** (F2) is made inside MAIN's own folder `~/gov-os-runs/W2-90`,
after the first project (the fixture worktree, outside the root) launched MAIN and OTHER, which made and marked
`W2-90` and `W2-91`; each such project also holds a forged `in_progress` ticket `DAEO-zz77` (external-ref `W2-77`,
a folder that does not exist).

| Behaviour | New cases | Red reason today (`19a4e9fd`) | Green today, and why |
|---|---|---|---|
| **F1. A copy or install into a folder of the own folder that lands on an entry leading out is refused**, with the guard's reason | `extra::test_a_copy_into_an_own_folder_folder_that_lands_on_an_entry_leading_out_is_refused` × 13: `d/payload.py` a symbolic link to the project's acceptance test `tests/acceptance/W2-90/test_kpi.py` × the 7 forms `cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, `cp first.py X d/` (only the second lands on the link), `cp -t d X`, `cp --target-directory=d X`; a symbolic link to `W2-91/theirs.py` × `cp X d/`, `install X d/`, `cp a b d/`; a hard link to the project's `docs/notes.md` × `cp X d`, `install X d/`, `cp -r s/. d/` | "Bash `cp …/elsewhere/payload.py …/gov-os-runs/W2-90/d/` (…; d holds payload.py, <entry>) was not refused: decision=allow" (11): the guard judges the folder `d`, which lies in the own folder | the two `-t` forms (2): the guard refuses them today; they must stay refused |
| F1 — a folder copy onto a link to a folder outside | `extra::test_a_folder_copy_onto_a_link_to_a_folder_outside_is_refused` × 2 targets (`W2-91`, the project's `tests/acceptance/W2-90/`) × `cp -r s d/`, `cp -r s d` | "Bash `cp -r …/elsewhere/s …/W2-90/d/` (…/d/s links to …) was not refused: decision=allow" (4) | — |
| F1 — control: the same forms into a folder of the own folder that holds no such entry are allowed | `extra::test_an_ordinary_copy_into_an_own_folder_folder_is_allowed` × 6 (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, `cp a b d/`, `cp -r s d/`) | none | pass (6): the controls; a fix that refuses every copy into a folder turns them red |
| F1 — control: a copy over an ordinary file of the same name in the own folder is allowed | `extra::test_a_copy_over_an_ordinary_file_of_the_same_name_in_the_own_folder_is_allowed` × `cp X d/`, `install X d/` | none | pass (2): the controls; a fix that refuses any existing entry turns them red |
| **F1 — inside the repository, for every ticket (W2-H056)**: a copy or install into a folder of the role's paths that lands on a symbolic link to the acceptance test is refused, as the direct write is | `extra::test_a_copy_into_a_repository_folder_that_lands_on_a_link_to_the_acceptance_test_is_refused` × 2 sessions (the engineer on DAEO-zz90 in `src/app/drop/`; product-spec on DAEO-zz92 in `docs/spec/drop/`) × `cp X d/`, `install X d/` | "Bash `cp …/elsewhere/payload.py …/W2-90/src/app/drop/` by engineer on DAEO-zz90 (…/drop/payload.py links to …/tests/acceptance/W2-90/test_kpi.py) was not refused: decision=allow" (4) | — |
| F1 — control: the same into an allowed folder of the repository with no such entry | `extra::test_an_ordinary_copy_into_an_allowed_repository_folder_is_allowed` × the same 2 sessions × `cp X d/`, `install X d/`, `cp -r s/. d/` | none | pass (6): the controls |
| **F1 — the own folder's marker (W2-L349)**: premise, the marker named directly is refused (Write; `cp` and `mv` onto it by its name; CIT-E difference 15) | `extra::test_the_marker_named_directly_is_refused` | none | passes: the premise of the next row; it must stay green |
| F1 — a file named like the marker, copied, installed or moved into the own folder, is refused | `extra::test_a_copy_install_or_move_of_a_file_named_like_the_marker_into_the_own_folder_is_refused` × `cp f W2-90/`, `cp f W2-90`, `install f W2-90/`, `cp -r staging/. W2-90/`, `mv f W2-90/` (the file in `W2-90/staging/`) | "Bash `cp …/W2-90/staging/<marker> …/W2-90/` (lands on the marker …/W2-90/<marker>) was not refused: decision=allow" (5). The `mv` form is allowed today though `mv` onto the marker named directly is refused, so it is a red case, as the brief asks | — |
| F1 — control: an ordinary file copied, installed or moved into the own folder is allowed | `extra::test_an_ordinary_file_copied_or_moved_into_the_own_folder_is_allowed` × `cp f W2-90/`, `install f W2-90/`, `mv f W2-90/` | none | pass (3): the controls |
| **F2. A project whose real root lies under the root gets nothing in any folder under the root outside itself**: Write, Edit, a Bash redirect and `rm -rf` refused with the guard's reason, whatever ticket it names | `extra::test_a_project_under_the_root_gets_nothing_in_a_folder_under_the_root` × 4 forms × 4 folders. Forms: (a) a project written at `W2-90/forged` whose `.git` is a file naming the first project's `.git`; (b) a `git worktree add` of the first project at `W2-90/wt`; (c) a `git clone` of it at `W2-90/clone`; (d) a worktree at `W2-90/wt-linked` reached through the link `~/projects/via-link`. Folders: `W2-91`, made by the first project (session on DAEO-zz91; control in the same case: the first project's session on DAEO-zz91 keeps it); `W2-90`, the own ticket's folder that holds the project, marked (session on DAEO-zz90, target `W2-90/work/README.md` outside the project); `W2-77` made by hand, not marked (session on DAEO-zz77); `W2-77` after `gov launch` of DAEO-zz77 from the project | `W2-91` in (a), (b), (d) (3): "Write on …/gov-os-runs/W2-91/work/README.md by the engineer on DAEO-zz91 of the project … under the root (…) was not refused: decision=allow" — the project names the first project's common directory, which marked `W2-91`. `W2-77` after the launch, all 4 forms (4): the same, for `W2-77`: today's launch from the project makes and marks `W2-77` (with the first project's common directory, or the clone's). After the fix the launch makes nothing, so this case's refusal is then also the folder's absence; the guard's own half is held by the `W2-91` cases | `W2-91` in (c) (1): the clone is another repository (DEC-751). `W2-90` (4): the own folder outside a project inside it gives nothing (the first review's finding 1). `W2-77` by hand (4): a folder no launch made gives nothing (DEC-751). All must stay green |
| F2 — control: writes the project under the root makes inside its own tree are judged as before | `extra::test_a_project_under_the_root_keeps_its_in_project_writes` × the 4 forms (Write and Edit on `src/app/main.py` by the engineer on DAEO-zz90). Held already, for a project built at `W2-90/clone`, by `review::test_a_project_inside_the_own_folder_keeps_its_refusals[inside-the-own-folder-*]` and `review::test_a_project_inside_the_own_folder_keeps_what_its_rules_allow[inside-the-own-folder-*]` | none | pass (4): the controls; a fix that refuses the whole project turns them red |
| F2 — `gov launch` from such a project adds no entry at, under or above the root, makes nothing and changes nothing under the root outside the project (by name, kind, size and modification time, no file read), and keeps the temp folder | `extra::test_a_launch_from_a_project_under_the_root_adds_makes_and_writes_nothing_there` × 4 forms × 2 tickets (DAEO-zz91, whose `W2-91` the first project made; DAEO-zz77, whose `W2-77` is not there yet). Control in the same case for DAEO-zz91: a later launch of DAEO-zz91 in the first project keeps `W2-91` in its write list | DAEO-zz91 in (a), (b), (d) (3): "the sandbox of a session on DAEO-zz91 in the project … under the root (…) may write at or under the root through ['//…/gov-os-runs/W2-91']"; DAEO-zz77 in all 4 forms (4): "… through ['//…/gov-os-runs/W2-77']" (the launch makes and marks it) | DAEO-zz91 in (c) (1): the clone is another repository (DEC-751); it must stay green |
| F2 — control: the first project, outside the root, keeps its own folder | in the cases above (the first project's Write in `W2-91`, its later launch of DAEO-zz91), and `last::test_the_launching_repositorys_session_keeps_its_folder`, `last::test_a_later_launch_in_the_same_repository_keeps_the_folder_its_content_and_its_entry`, `last::test_a_second_worktree_of_the_same_repository_gets_the_same_folder` (a worktree outside the root) | none | pass |

**Red run (whole suite, at `19a4e9fd` plus the new file and this README): 38 failed, 267 passed, 0 skipped**, about
5.5 minutes. Every earlier case still passes (233). The new file: 38 red, 34 green. Red: F1 own folder 11 + linked folder 4 + repository 4 + marker 5; F2 guard 7 + launch 7. Green:
the two `-t` forms, 8 own-folder controls, 6 repository controls, the marker premise, 3 marker controls, 9 F2 guard
cases already refused, 4 in-project controls and 1 clone launch.

### Discoveries of this round (no test)

- **The marker's name is only public through a listing.** No document a test may read names it outside the CIT-E's
  record of the code; the cases take it from the one entry the launch leaves in the folder it makes. A launch that one
  day leaves a second entry there fails the marker cases' premise, not their behaviour.
- **`cp` and `install` forms the brief does not name** (`cp -a`, `cp -R`, `install -t d`, `install -D`) fall under
  the same rule in F1's words ("every copy or install into a folder"), but only the named forms are tested (DEC-221).

## The review of the last round: tests added after implementation, from the review of the last round (DEC-136, DEC-764, DEC-765)

The review of the last round found two behaviours the suite missed. The owner decided them (DEC-764 and DEC-765,
2026-10-18; staged for the owner's commit, not yet in this worktree's register): **A** (DEC-764), the guard refuses
`cp --parents`, and every copy, install or move option that makes the landed path other than `<folder>/<name>`, as
doubt, the way it refuses `ln -t`; **B** (DEC-765), the guard reads option values as values and honours `--`, and
judges each call as the files it writes. They are tested in `round` = `test_w2_50_short_round.py`, through the guard's
hook with the call on stdin, as the rest of the suite. `ln -f` onto the marker (row W2-L354) and a FIFO in the
marker's place (row W2-L350) are other rows: no test. No earlier test file, support module or conftest was changed;
no earlier ticket's test conflicts (W1-03's `install -m 644 README.md docs/installed.md` and W1-46's options after the
destination, `install … -m 644`, `cp … --suffix bak`, already read a value as a value).

**How the cases are built.** One fixture, `places`: MAIN's and OTHER's folders made by a launch; the project's
acceptance test `tests/acceptance/W2-90/test_a.py` ("the acceptance test", in "the acceptance folder"); empty folders
`~/gov-os-runs/W2-90/d/` and `src/app/d/` that hold no link; the links `~/gov-os-runs/W2-90/lnk` → OTHER's folder and
`src/app/m/sub` → the acceptance folder, for the middle-level cases; sources of the test's own in `elsewhere/` and
in `src/app/staging/` (`X`, `F`, and a file named `-t`) and `~/gov-os-runs/W2-90/staging/`, so that a move's source
lies where the session may write and its removal is not what is refused. A call is asked from a working folder (the
payload's `cwd` and the guard's own): the project, `elsewhere/`, `elsewhere/cwd/` or `src/app/staging/`, as the
relative spelling of the case needs. No allowed command is run: the guard is only asked. The engineer on DAEO-zz90
(paths `src/app/**`) makes every call.

**What each tool writes** was found by running each form in a temporary folder of the designer's own (GNU coreutils
9.4, `cp --help`, `install --help`, `mv --help`), never in the project or the root:

- `cp --parents <source> <folder>` (and `-t <folder>`, `--target-directory=<folder>`, with `-r` or `-a`) writes
  `<folder>/<source as written>`: from `a/b/src`, `cp --parents ../src/X d/` wrote `d/../src/X`, outside `d`.
  `cp` accepts `--parent`, `--paren`, `--par` and `--pa` as `--parents`; `--p` is refused as ambiguous
  (`--parents`, `--preserve`); `--parents=x` is refused.
- `-S <suffix>` / `--suffix` makes a backup for `cp`, `install` and `mv` without `-b`: `cp -S.t X f`, `cp -bS.t X f`,
  `cp -S .t X f`, `cp --suffix=.t X f`, `cp --suffix .t X f`, `install -S.t X f` and `mv -S.t X f` each write `f` and
  `f.t` (the old `f`); `cp -S -t F f` and `cp --suffix -t F f` write `f` (from `F`) and `f-t`. A suffix holding `/`
  is not used (`cp -b -S /../evil X f` wrote `f~`).
- `install -oroot X f`, `install -o root X f`, `install -gstaff X f` write `f` and then fail to change its owner or
  group (not root here); `install -m+t X f` and `install --mode=+t X f` write `f` with mode `+t`.
- `cp -- -t f` and `mv -- -t f` write `f` from the file named `-t`; `cp -t d -- X` and `cp -- X d/` write `d/X`;
  `cp X -- f` writes `f`.
- `-Z` takes no value for `cp`, `install` and `mv` here (`--help`: "set SELinux security context … to default
  type"); `cp -Zt d X`, `install -Zt d X` and `mv -Zt d X` each write `d/X`.
- **`install` and `mv`: no option makes the landed path other than `<folder>/<name>` or the named destination.**
  `install -D X d/new/f` writes the named destination `d/new/f` (making its folders), `install -D -t d/n X` writes
  `d/n/X`; `install -d` makes folders only; `--strip-trailing-slashes` (`mv`, `cp`) changes how a source is read, not
  where it lands; backups land at `<destination><suffix>` (B). So A has no `install` or `mv` case.

**What A's comparison with `ln -t` is.** Today `ln -t <folder> X` is refused with "Bash write to
'/<guard-unresolvable>' denied for role 'engineer'". Each A case asks the guard for `ln -t <the case's folder>
<elsewhere>/X` from the same working folder first (a premise: it must be refused), takes the first quoted path of
that refusal's reason (today `/<guard-unresolvable>`), and asks that the `--parents` call's refusal name the same.
That is as far as the public result lets the two be compared: the same target named, so the same "cannot read" path,
not a refusal of the place the copy lands in. The wording around it is not prescribed. If an `ln -t` refusal one day
names no quoted path, only the refusal itself is asked.

**"With the guard's reason" in B.** The reason must name a file the call writes (as given, normalised or resolved):
the destination, the backup `<destination><suffix>`, or for a copy into a folder `<folder>/X` or the folder. The
suite's usual reason words (`role`, `ticket`, `outside`) are not accepted here: every refusal names its role, and a
refusal for a wrong path must not pass.

| Behaviour | New cases | Red reason today (`8a310cb2`) | Green today, and why |
|---|---|---|---|
| **A. `cp --parents` is refused as a form the guard cannot read**, into the own folder and into a folder of the repository the session may write, whatever its source | `round::test_a_copy_with_parents_is_refused_as_a_form_the_guard_cannot_read` × 13. Own folder: `cp --parents ../W2-91/work.txt ~/gov-os-runs/W2-90/` from `elsewhere/cwd` (lands in OTHER's folder, the review's example); `cp --parents lnk/work.txt ~/gov-os-runs/W2-90/` (through the link `W2-90/lnk` at a middle level); harmless sources that land inside `W2-90/d`: `cp --parents X d`, `… X d/`, `… -t d X`, `… --target-directory=d X`, `cp -r --parents s d/`, `cp --parent X d`. Repository: `cp --parents ../../tests/acceptance/W2-90/test_a.py -t <project>/src/app` from the project (lands on the acceptance test; the review's example, its source a file of the test's own in HOME), `cp --parents sub/test_a.py src/app/m/` (through the link `src/app/m/sub`), and harmless: `cp --parents X src/app/d`, `cp -a --parents s src/app/d/`, `cp --par X src/app/d` | "Bash `cp --parents …` from … (<case>; cp --parents writes <folder>/<source as written>) was not refused: decision=allow" (13): the guard judges the folder (and `<folder>/<name>`), which is allowed | — |
| **B. An option's value is read as a value, and nothing after `--` as an option**: each call judged as the files it writes and refused, naming one of them, when one is refused as a direct write. Premise: the acceptance test named directly (Write, a redirect, a plain `cp`) is refused | `round::test_the_acceptance_test_named_directly_is_refused` | none | passes: the premise; it must stay green |
| B — the value of `-S` / `--suffix` | `round::test_an_option_value_or_a_double_dash_is_judged_as_the_files_the_call_writes` × `cp -S.t X <acceptance test>`, `cp -bS.t …`, `cp -S .t …`, `cp --suffix=.t …`, `cp --suffix .t …`, `cp -S -t F …`, `cp --suffix -t F …`, `install -S.t …`, `mv -S.t …` (X and F in `src/app/staging/`) | "… was not refused: decision=allow" for `cp -S.t`, `cp -bS.t`, `cp -S -t F`, `cp --suffix -t F`, `install -S.t` (5): the `t` of the value, or the value `-t`, is read as `-t` with `X` (or `F`) as the target folder, so the guard judges `src/app/staging/X/test_a.py`, which is allowed, and the acceptance test is read as a source | `cp -S .t`, `cp --suffix=.t`, `cp --suffix .t`, `mv -S.t` (4): judged and refused naming the acceptance test today; they must stay so |
| B — the values of `install -o`, `-m`, `-g` (`--mode`) | the same test × `install -oroot X <acceptance test>`, `install -o root …`, `install -m+t …`, `install --mode=+t …`, `install -gstaff …` | `-oroot`, `-m+t` (2): "was not refused: decision=allow" (read as `-t` with `X` as the target folder). `-gstaff` (1): refused, but "the refusal's reason names neither the target nor why …: \"Bash write to '…/W2-90/aff/X' denied …\"" (the rest of `-gstaff` after its `t`, `aff`, read as a `-t` folder) | `-o root`, `--mode=+t` (2): refused naming the acceptance test today |
| B — `--` | the same test × `cp -- -t <acceptance test>` and `mv -- -t <acceptance test>` from `src/app/staging/` (which holds a file named `-t`), `cp -t <acceptance folder> -- X`, `cp -- X <acceptance folder>/`, `cp X -- <acceptance test>` | `cp -- -t` (1): "was not refused: decision=allow": `-t` after `--` is read as `-t`, with the acceptance test as the target folder and no source, so nothing is judged | `mv -- -t`, `cp -t … -- X`, `cp -- X …/`, `cp X -- …` (4): refused naming the file they write today; they must stay so |
| B — `-Z` takes no value: `cp -Zt <acceptance folder> X` stays judged and refused (fail-closed control) | the same test × `cp -Zt <acceptance folder> X` | none | passes: refused naming `<acceptance folder>/X` today; a reading of `-Z` as taking a value (`t`) must not let it through |
| **Controls: a value with no `t`, a `--`, and the B forms, onto an allowed file, are allowed** (`src/app/existing.py`, and `~/gov-os-runs/W2-90/d2/f.txt`) | `round::test_an_option_value_or_a_double_dash_onto_an_allowed_file_is_allowed` × 5 forms × 2 places: `cp -S.bak X f`, `install -m 0644 -o root X f`, `cp -- X f`, and the B forms `cp -S.t X f`, `install -oroot X f` (X in `src/app/staging/`) | `install -m 0644 -o root` (2): "was not allowed: decision=deny … reason=\"Bash write to '…/W2-90/root' denied …\"": the separate value `root` of `-o`, after `-m 0644`, is read as an operand (B; the brief lists it as a control, it is red today) | `cp -S.bak`, `cp --` (4): allowed today. `cp -S.t`, `install -oroot` (4): allowed today only because the misread `-t` folder `src/app/staging/X` lies in the session's paths; after the fix they must be allowed as the files they write |
| Controls: ordinary forms into an allowed folder holding no link, allowed | `round::test_an_ordinary_copy_or_move_into_an_allowed_folder_is_allowed` × `mv W2-90/staging/X W2-90/d/`, `mv src/app/staging/X src/app/d/`, `cp X src/app/d` (no slash). The other ordinary forms are held already: `extra::test_an_ordinary_copy_into_an_own_folder_folder_is_allowed` (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`, `cp a b d/`, `cp -r s d/` in the own folder), `extra::test_an_ordinary_copy_into_an_allowed_repository_folder_is_allowed` (`cp X d/`, `install X d/`, `cp -r s/. d/` in `src/app/drop/` and `docs/spec/drop/`), `extra::test_an_ordinary_file_copied_or_moved_into_the_own_folder_is_allowed` (`cp`, `install`, `mv` into the own folder itself) | none | pass (3): the controls; a fix that refuses every copy into a folder, or every move, turns them red |
| Controls: `cp -t <folder> X` and `install -m 644 X <folder>/` stay judged as before | `round::test_the_t_and_m_forms_stay_judged_as_before` × the 2 forms × `~/gov-os-runs/W2-90/d` (allowed), `src/app/d` (allowed), the acceptance folder (refused, naming it or `<folder>/X`) | none | pass (6): the controls; a fix that reads `-m 644` or `-t` otherwise turns them red |

**Red run (whole suite, at `8a310cb2` plus the new file and this README): 24 failed, 334 passed, 0 skipped**, about 4.5 minutes. Every earlier case still
passes (305). The new file: 24 red, 29 green. Red: A 13; B 9 (`cp -S.t`, `cp -bS.t`, `cp -S -t F`,
`cp --suffix -t F`, `install -S.t`, `install -oroot`, `install -m+t`, `install -gstaff`, `cp -- -t`); controls 2
(`install -m 0644 -o root`, both places). Green: the B premise, 11 B forms refused today with the guard's reason
(`cp -S .t`, `cp --suffix=.t`, `cp --suffix .t`, `mv -S.t`, `install -o root`, `install --mode=+t`, `mv -- -t`,
`cp -t … -- X`, `cp -- X …/`, `cp X -- …`, `cp -Zt`), 8 controls onto an allowed file, 3 ordinary forms and 6 `-t`
and `-m` forms.

### Discoveries of this round (no test)

- **A backup is a second file written.** With `-S` or `--suffix` (and `-b`, `--backup`) `cp`, `install` and `mv`
  rename the file they replace to `<destination><suffix>` in the same folder. B's refusals accept a reason that names
  that backup; no case asks that the backup path alone be judged, for an allowed destination that exists and whose
  backup name is a protected entry of the same folder (for example a suffix that turns a file of the own folder
  into the marker's name: the rename would replace the marker). No source names it; it is the lead's to raise if
  wanted (it may be W2-L354's neighbour).
- **`install -m 0644 -o root X f` is refused today** for `<project>/root`: a separate value after another option's
  value is read as an operand. The brief lists it as a control; it is red today, and B's "values are values" makes it
  green.
- **The misreading also lets some B forms pass for the wrong reason.** `cp -S.t X <allowed file>` and
  `install -oroot X <allowed file>` are allowed today only because the misread `-t` folder (the source's own path)
  lies in the session's paths; with a source in `elsewhere/` the same calls are refused today, naming
  `elsewhere/X/<name>`.

## Readings chosen where a KPI line admits more than one

Each is the lead's to put before the owner with the change proposal.

- **R1 — the folder's name.** The ticket's `external-ref` exactly as written, case kept and a letter suffix kept
  (`W2-99a`), as worktrees are named (`~/gov-os-worktrees/<W2 id>`, WBS §0 rule 2; W2-15a/W2-15b in the plan); the
  `tk` id only when the ticket has no `external-ref`. The tk-id folder of a ticket that has a W2 id, a case change and
  a longer id that starts with the own id are other folders. Source: the KPI's "named by the ticket's W2 id (its
  external-ref, as for worktrees), or by its tk id when it has none". Confidence high.
- **R2 — who creates the folder on first use.** The launcher creates the root and the own folder before it starts
  the session, when they do not exist, and leaves an existing folder's contents alone; the guard does not ask for the
  folder to exist, so an unlaunched session (a lead) makes it with its own first Write or `mkdir -p`. Source: "the
  folder is created on first use"; DEC-160 lists a sandbox path that does not exist yet as untested, and the sandbox
  can only bind a folder that exists. Confidence medium.
- **R3 — a forged, unknown or empty `GOV_TICKET` is no ticket**, and the folder follows `GOV_TICKET`, not the
  worktree's name. Source: "resolved from the session's GOV_TICKET"; the guard's default deny. Confidence high.
- **R4 — "any role" is all six roles**, the independent auditor and product-spec included, though the auditor's role
  file says it writes only its report path or `.gov-runtime/scratch/**`: the own folder is read as the scratch
  folder outside the repository (DEC-108's counterpart), which every role may write. A session with no role or an
  unknown role writes nothing. The sandbox cases cover the five launched roles (DEC-161, DEC-386); the orchestrator
  is not launched. The role files are not in this ticket's allowed paths, so they will not say it. Source: DEC-728
  item 2, "a session of any role". Confidence medium.
- **R5 — the secrets-indexing check does not follow a link from `.gov-runtime/` into `~/gov-os-runs`** (a folder
  link or a file link): it stays green and prints no secret. Today it follows the link and fails. Source: "this
  repository's secrets-indexing check never scans it". The other choice (follow, or flag the link) is stricter on
  secrets and would make these two cases wrong. Confidence medium.
- **R6 — "survives a restart"** is read as: after the session ended and its temp folder was removed, the clone is
  still a sound repository in the own folder, lies in no temp folder, and the next session of the same ticket finds
  it. No reboot is made. Source: W2-M355 (clones under /tmp are lost on a reboot), DEC-159. Confidence high.
- **R7 — removing the root includes `rmdir`.** Today the guard lets `rmdir <root>` through. Source: "the root itself
  (… or removing it)". Confidence high.
- **R8 — a hard link.** A write through a name in the own folder that is a hard link to a file outside it is refused,
  and making such a link (`ln`, `cp -l`, `link`) is refused. Source: "a path outside it reached by … a hard link";
  DEC-334's form for hard links in the repository. Confidence medium.

## Discoveries (no test)

- **The guard does not judge a `git clone` destination.** `git clone <src> ~/gov-os-workbench/clone` (or into another
  ticket's folder) is allowed by the guard today. In a launched session the sandbox's write list stops it; in an
  unsandboxed session (the orchestrator, a ticket lead) nothing does, though DEC-723 says agents never write in the
  workbench. The workbench test leaves the clone form out, since "as before" the guard never judged it.
- **File tools outside the project in a launched session.** The guard can allow Write and Edit in the own folder, but
  Claude Code's own permission check treats a file outside the working directory separately, and DEC-313 refuses
  `--add-dir` and `permissions.additionalDirectories`. A launched session may therefore be able to write there only
  through Bash. Not testable without a real session.
- **No earlier test contradicts these KPI lines.** No acceptance test names `gov-os-runs`. W1-28's
  `test_w1_28_launch_product_spec.py` says in a docstring that the temp folder is "the one place outside the project
  its sandbox may write"; its assertion only asks that the temp folder be in the list, which stays true.
