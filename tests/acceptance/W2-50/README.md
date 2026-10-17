# W2-50 — The durable scratch root: acceptance tests

Written by the independent test designer (MR-3, DEC-069) from the KPI lines of ticket `DAEO-kl5e` (W2-50), the card
in `docs/plan/WAVE_2_WBS.md` §2, the list row W2-M355, and DEC-728, DEC-723, DEC-159, DEC-160, DEC-161, DEC-221 and
DEC-732. Profile FULL. Written before the implementation; no earlier ticket's test was revised.

**208 cases in 7 files**: the first 139 cases in 5 files, written before the change proposal (red run on `w2/W2-50`
at `689bd17e` plus that suite: **48 failed, 91 passed**), 15 cases in `test_w2_50_owner_answers.py` for the owner's
answers to it (DEC-743; see the section below), written before the implementation (red run at `a5ef3c69` plus that
file: **55 failed, 99 passed**), and 54 cases in `test_w2_50_review_findings.py` for the review's findings, **tests
added after implementation, from the review (DEC-136)** (red run of the whole suite at `d0c6be04` plus that file:
**34 failed, 174 passed**, about 1.5 minutes; see the section below).

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
