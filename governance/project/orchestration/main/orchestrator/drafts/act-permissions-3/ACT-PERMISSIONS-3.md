# ACT-PERMISSIONS-3: the helpers' own temp folders without a prompt (DEC-1126 (10))

## 0. What the owner says
Class **(b)**: the owner's yes, then the operator agent (or the owner's operator by hand). The line the operator agent
reads, on its own line:

yes ACT-PERMISSIONS-3 e567660a

- **For:** one file changes, in the repository and not tracked by git: `.claude/settings.local.json` (root `repo`).
  Two rules are added to `permissions.allow` and six to `permissions.deny` (Edit and Read of key, pem and env-named
  files under the same folders). Nothing is removed. No `ask`, hook or directory changes.
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-11. Built and rehearsed in a planted repository and in
  stand-in projects. **Nothing live changes until it runs.** The live file was only read.
- **Under:** DEC-1126 (10) (the permissions asked for last night, grouped by form, with an allow-list ACT), DEC-1080 and
  DEC-1081 (P-PERMISSIONS-1), DEC-1057 (rehearsed), OPERATOR-AGENT-1 §2 and §3.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-PERMISSIONS-3/` (the CTO copies it there from
  `drafts/act-permissions-3/act/ACT-PERMISSIONS-3/`). **Manifest sha256
  `e567660a69685d102f3eb860e89d09cb738516e69b5cac6a18d8749db9cf0779`.**

## 1. The 39 requests, by form (queue rows from 2026-11-10 17:00)
All 39 were "asked (by day)": none fell in the quiet hours (the last row is 01:49). The CTO's grouping held, with these
corrections: A is 27 rows, not about 28; B's two rows have two different causes; C's seven asks were never shown to the
owner (they were headless sessions); D's two rows are one slip repeated.

| Form | Rows | Sessions | Example | Why it was asked | Recommendation |
|---|---|---|---|---|---|
| **A.** Write (23) and Read (4) in a helper's own `/tmp/gov-os-emg-<name>/` folder | 27 | `8ddb8b14` (the CTO and its in-session helpers) | Write `/tmp/gov-os-emg-checks/run_check.sh` | The user-level `Write(*)`, `Edit(*)`, `Read(*)` in `~/.claude/settings.json` reach only the working directory. The project files have no rule for `/tmp`. `acceptEdits` accepts edits only inside the working directories. Only the session's own scratchpad is exempt. Rehearsed: B0 below, the same calls refused with no rule. The form recurred on 11-07 (13), 11-09 (3) and 11-11 (27): 43 rows in all. | **Allow**, this ACT: `Edit(//tmp/gov-os-emg-*/**)` and `Read(//tmp/gov-os-emg-*/**)` in `.claude/settings.local.json`, with six deny rules for key, pem and env-named files under them |
| **B1.** Bash: a venv and `pip install --no-deps --no-index` of a local wheel, in `/tmp` | 1 | `8ddb8b14` | `cd /tmp/gov-os-emg-repin5 && python3 -m venv ... && ... pip install ...` | **The guard, not the CLI.** The guard's rule 4 (`.claude/hooks/pretooluse.py`, line 1131) answers `ask` to an install in the CTO's own session (orchestrator on W2-00) and refuses it in every other. The pinned judge (`gov.guard.install.has_install`) reads this call as an install. No allow rule can change that. | **Keep asking.** The owner's rule: no installs for non-orchestrator roles; the CTO's own asks. The re-pin is done, so the form will not recur until the next one. |
| **B2.** Bash: `cp .claude/hooks/bash_writes.py` into a rehearsal clone, then a test run with output to `/tmp` | 1 | `8ddb8b14` | `cd <repo>; export TMPDIR=...; cp .claude/hooks/bash_writes.py /tmp/gov-os-emg-repin5/stagedhook/; ... pytest ... > /tmp/...` | **The CLI's own "sensitive file" rule**: a command that copies out of `.claude/hooks/` asks whatever the allow list says. Not an install (the guard's judge says no). Reproduced in a stand-in project (rehearsal B2i): refused with or without the ACT. | **Fix at the source:** a helper copies a hook with `git show HEAD:.claude/hooks/<file> > <copy>` (or reads it with the Read tool and writes the copy with the Write tool, once A is allowed). A line in the CTO's brief for rehearsal helpers (owner: the CTO). No rule: a rule that opened `.claude/hooks/` to copies would be wider than the form. |
| **C.** Monitor until-loops over a test log in the worker's own `/tmp/gov-launch-*/` folder | 7 | `e6ecf226` (3), `244c903e` (1), `7963582a` (3): all three launched `independent-test-designer` workers, in W2-153 and W2-112 | `until grep -qE "[0-9]+ (passed|failed)" /tmp/gov-launch-e6ntqav0/claude-1000/before.txt; do sleep 15; done` | A launched worker is a headless `claude -p` session: **an ask is refused on the spot; nobody was prompted.** `7963582a`'s own log lists the three Monitor denials; `244c903e`'s lists none (not explained); `e6ecf226`'s log is empty (the first launch). The Monitor tool refuses a `grep` over a file outside the working directory (stand-in run y1: "may only search for patterns in files from the allowed working directories"); the worker's `TMPDIR` is outside its worktree. 58 Monitor rows in the queue since 11-02 (5 refused in the quiet hours). | **Keep refused; fix at the source.** Do not allow Monitor: the wired guard (`pretooluse.py` lines 995 and 1121) judges the command of a `Bash` call only, so a Monitor command would run with no check of its writes or installs. A `Read(//tmp/gov-launch-*/**)` rule would open every worker's folder to every other (they differ by a random suffix). The line is in the launch template (§9, item 1): the test designer's template has no waiting line; the engineer's and the lead's say `{CMD:wait_for}`. |
| **D.** Write to a mistaken scratchpad path, `/tmp/claude-1000/-home-usain/Dynamic-Agentic-Engineering-OS/...` (a slash where the real one has a dash) | 2 | `8ddb8b14` | `/tmp/claude-1000/-home-usain/Dynamic-Agentic-Engineering-OS/x` | The real scratchpad is `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/<session>/scratchpad` and never asks. This is another folder, so it asks: the prompt caught a typo. Four rows in all (11-06 and 11-11). | **Keep asking.** A rule for it would hide the typo. The brief line is already in LIFT-common.md (owner: the CTO). Rehearsed: still asked (B2c). |
| **E.** AskUserQuestion | 1 | `412a4e37` (the previous CTO) | the D-10 run 1 question, 17:54 | It is a question to the owner, not a permission to grant. | **Keep.** It carries a decision. |

Not asked about, and left alone: the other families of temp folder seen on earlier days (`/tmp/gov-os-lead-*`,
`/tmp/lead-*`): they are not in these 39 rows.

## 2. What changes
`.claude/settings.local.json`: two entries at the end of `permissions.allow` (42 rules become 44) and six at the end of
`permissions.deny` (4 become 10):
```
50c50,52
<       "Bash(cd ~/gov-os-worktrees/*)"
---
>       "Bash(cd ~/gov-os-worktrees/*)",
>       "Edit(//tmp/gov-os-emg-*/**)",
>       "Read(//tmp/gov-os-emg-*/**)"
56c58,64
<       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)"
---
>       "Read(//home/usain/gov-os-eval/fixtures/evaluation/memory-verdict-2/**)",
>       "Edit(//tmp/gov-os-emg-*/**/*.key)",
>       "Edit(//tmp/gov-os-emg-*/**/*.pem)",
>       "Edit(//tmp/gov-os-emg-*/**/.env*)",
>       "Read(//tmp/gov-os-emg-*/**/*.key)",
>       "Read(//tmp/gov-os-emg-*/**/*.pem)",
>       "Read(//tmp/gov-os-emg-*/**/.env*)"
```
Everything else is byte for byte as before. sha256 before `d715292711a2`, after `acb46a637d48`, mode 644.
- **The six deny rules** are the project's own deny names (`Edit(**/*.key)`, `Edit(**/*.pem)`, `Edit(**/.env*)` in
  `.claude/settings.json`) put under the allowed folders, for Edit and for Read. Those project rules are relative to the
  project and never reached `/tmp`; a deny rule wins over every allow, so the allow no longer opens these names.
  `**/` matches no folder or any number, so a key file directly in the folder is covered (rehearsed).
- `//` is Claude Code's absolute-path form (as in ACT-PERMISSIONS-2). `gov-os-emg-*` is the folder name the emergency rules
  give every helper (`TMPDIR=/tmp/gov-os-emg-<name>`, EMG-common.md), and nothing else.
- An `Edit` rule covers the Write, Edit and NotebookEdit tools (rehearsed with Write and Edit).
- **No `Write(//tmp/**)`, no `Edit(//tmp/**)`** (the owner's rule: never wider than the form). The check after the apply
  fails if any `Write(...)` rule or any rule holding `//tmp/**` is in the list.
- The guard still runs first on every call. The rules change only whether the CLI shows its prompt.

## 3. What does not change (rehearsed, §6 B2)
Still asked or refused, with the rules in place: a Write or Read of a key, pem or env-named file under a
`gov-os-emg-*` folder (now denied); a Write or Read in any other `/tmp` folder; the mistaken scratchpad
path; a Write in the sets root (stand-in); a Read of the three hidden folders (the deny rules of ACT-PERMISSIONS-2 win); a
Read through a link inside a `gov-os-emg-*` folder to the sets root (the link is followed, and the deny rule refuses);
the `.claude/hooks/` copy; the Monitor until-loop over a `gov-launch-*` folder; the install (the guard's judge). The ACT
adds no Bash rule.

## 4. The class and the route
**(b).** `governance/project/operator/class-rules.yaml`, the `settings` row: `match: {root: repo, path:
".claude/settings*.json"}`, `only_added: ["permissions.deny"]`, `else: b`; why: "allow rules, hooks blocks, any other key
alter a control (b)". The operator's own `act_class.classify` over the sealed bundle gives (b), row `settings`, no script
hits. The file is ignored by git: the operator applies and checks it and does not commit it (`operator_run.py` line 1024).
Route: the owner's yes, then the operator agent's queue (G1 to G9); G4 reads a review made under the fixed brief
(`~/gov-os-operator/install/reviewer-brief.md`), to be dropped into the bundle as `review.md`, **absent now**. By hand is
the same steps (§7).

## 5. The bundle (sha256 cut to 12)
| File | sha256 | What |
|---|---|---|
| `manifest.json` | `e567660a6968` | touched, files, two checks, rehearsal |
| `apply.sh` | see manifest | `check`, `apply`, `undo`, `verify`; cwd-based; state by sha256 alone |
| `list.txt` | see manifest | the one file, before and after sha256 |
| `before/repo/.claude/settings.local.json` | `d715292711a2` | the frozen original |
| `after/repo/.claude/settings.local.json` | `acb46a637d48` | the frozen result |
| `rehearsal.log` | see manifest | the rehearsal, `REHEARSAL PASS`, 62 checks |
| `review.md` | absent | to come: a review under the fixed brief |

Also in `drafts/act-permissions-3/`: `build.py` (builds the bundle from the live file, read only), `rehearse.py`
(writes `rehearsal.log`), `seal_check.py`, `install_check.py`, and the exploration scripts `explore.py` to `explore4.py`
with their outputs under `rehearsal/`.
- `check` (read-only): `state before|applied (sha256 ...)`, exit 0; `state other` on stderr, exit 3.
- `apply`: only from the state before; the frozen after copy is put in place atomically, mode kept. `ACT_BACKUP_BESIDE=1`
  first copies the file to `settings.local.json.bak-<UTC stamp>-ACT-PERMISSIONS-3` beside it (a hand run only).
- `undo`: the frozen original put back byte for byte, only when the file is the ACT's own after.
- The two checks (after the apply): the two rules are the last two of the allow list, the list has 44 rules, no `Write(`
  rule and nothing holding `//tmp/**`; the six deny rules are the last six of a deny list of 10; `additionalDirectories`
  (2) as before; the file parses. The first is red
  on the before file.
- **The file is frozen as it is** (`d715292711a2`, last changed 2026-11-09 20:00). Claude Code itself rewrites it when
  someone answers "don't ask again". If it has changed by the apply, `check` and `apply` refuse (exit 3, by design) and
  the bundle is rebuilt: `python3 -I -B build.py`, `rehearse.py`, `build.py --seal`.

## 6. Rehearsal (DEC-1057; `rehearsal.log`)
**Result: `REHEARSAL PASS`, 62 checks, 0 failures.**
- **A, the file** (apply.sh on a planted repository holding a copy of the live file): check (before); verify refused;
  apply with a backup; check (applied); the diff is exactly §2's (two hunks); the parsed result is the original plus the two
  allow and six deny rules, key order kept; the old deny rules kept in order; additionalDirectories, hooks and env unchanged; mode kept; both manifest checks green after
  and the first red before; apply again changes nothing; undo gives the original byte for byte, twice harmless; re-apply
  works; a later change makes undo refuse and is kept; a file that drifted by one byte makes check, apply and undo refuse
  (exit 3) and leaves no temp or backup file; a missing file and a link refused; a tampered after copy and a tampered
  before copy refused (exit 4); the dry-run shape changes exactly one file.
- **A', the operator's own code, read only:** `validate_manifest`, the path rule over `apply.sh` and the checks, and
  `act_class.classify` (class b, row `settings`) all pass on the sealed bundle (`seal_check.py`).
- **B, the behaviour:** headless Haiku sessions (`claude -p`, under the real user-level settings) in a stand-in project of
  its own (git init), with the real files' `permissions` blocks and only the paths substituted (hooks, env and directories
  left out, so nothing real is read or logged). Planted dummy files.
  - **B0, before the ACT:** a Write, a Read and an Edit in a `gov-os-emg-*` folder are all refused (headless: what
    would ask). This is the 27 prompts, reproduced.
  - **B1, after the ACT:** the same four calls pass with no denial at all, a Write into a new sub-folder too.
  - **B2, still asked or denied after the ACT:** a Write and a Read in another `/tmp` folder; the mistaken scratchpad
    path; a Write in the stand-in sets root; a Read of `memory-retrieval/hidden` and of `memory-verdict`; a Read through a
    link inside a `gov-os-emg-*` folder to the stand-in sets root; a `cp` out of `.claude/hooks/`.
  - **B2k, the key names:** under an allowed folder an ordinary file still writes, and a Write of a `.key` file, a `.pem`
    file (in a sub-folder), `.env` and `.env.local`, and a Read of a `.key`, a `.pem` and an `.env.*` file, are all denied.
  - **B3:** a Monitor until-loop over a `gov-launch-*` folder is still refused.
- **C:** the guard's pinned judge reads the 01:14:55 call as an install and the 01:16:25 call as not one. The live
  `settings.local.json` and `settings.json` are unchanged (sha256) and the approval queue did not grow (no real hook ran).
- **Earlier runs:** two exploration passes set the rule form (`Edit(...)` and `Read(...)` with a `*` inside a folder name
  work) and found B2's cause. The first full run failed two checks: the manifest's check named the real HOME (the
  operator's path rule refused it; now a count), and a key-named file written in an allowed folder passed. The second
  run (56 checks) showed that as information; at the coordinator's request the six deny rules were added, and the third
  run (62 checks) denies it.

## 7. The operator's steps
yes ACT-PERMISSIONS-3 e567660a

**By the operator agent:** after the owner's yes, the CTO writes the request line (the ACT's id and the manifest sha) in
`~/gov-os-operator/queue/`, once `review.md` is in the bundle; the agent runs G1 to G9, applies, and runs the two checks.
No commit (an ignored file).

**By hand** (about a minute):
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-PERMISSIONS-3
sha256sum $G/manifest.json                    # expect e567660a69685d102f3eb860e89d09cb738516e69b5cac6a18d8749db9cf0779
bash $G/apply.sh check                        # expect: state before (sha256 d715292711a2)   (state other: stop, tell the CTO)
ACT_BACKUP_BESIDE=1 bash $G/apply.sh apply    # expect: backup ... (sha256 d715292711a2), then state applied (sha256 acb46a637d48)
bash $G/apply.sh verify                       # silent, exit 0
bash $G/apply.sh check                        # expect: state applied (sha256 acb46a637d48)
```
The CTO's session reads the change at its next start, or at once through `/permissions`.

**Rollback:** `bash $G/apply.sh undo` (expect `state before (sha256 d715292711a2)`). If the file changed since, undo
refuses and says so; the backup beside the file is the hand copy. Either rule can also be deleted by hand from the allow
list: nothing else depends on them.

## 8. What it does not cover, and what the rehearsal found (stated so it is approved knowingly)
1. **The rule reaches launched workers too.** A session started in a git worktree of this repository reads the main
   tree's untracked `.claude/settings.local.json` (measured, `explore4.py`: a Read allowed by a rule in the main file
   passes in the worktree, and is refused with the file removed; Claude Code 2.1.322). So ACT-PERMISSIONS-2's note that
   its settings "do not reach launched workers" is wrong for this version: its hidden-folder deny rules reach them (good),
   and so does this ACT's `Read` rule. A worker's **writes** stay inside its sandbox (the temp folder and run folder
   only), so the `Edit` rule adds nothing there. A worker's Read of a `/tmp/gov-os-emg-*` folder now passes the CLI's prompt (the sandbox's own limits are separate);
   the guard still refuses the hidden half, secrets and the counterpart's work. If the owner wants the `Read` rule for
   the CTO's session alone, the only way is to drop it: there is no per-session file today.
2. **A Monitor until-loop whose only path is in a `gov-os-emg-*` folder now runs without a prompt** (rehearsal B3,
   information). Its command is still not read by the guard (see §1, C). Loops with `pgrep`, `kill` or `$(...)` still ask.
3. **Key-named files** (`*.key`, `*.pem`, `.env`, `.env.*`) under a `gov-os-emg-*` folder stay denied to Edit, Write and
   Read: the six deny rules of §2 (rehearsed, B2k). Other secret-like names are not listed (the project's own list has
   none more under Edit; `config/secrets*` is a repository path).
4. **Symlinks:** a link made inside a `gov-os-emg-*` folder to a protected folder does not open it (rehearsal B2g). Not
   tried: a link to a place no deny rule names.
5. **The reach rests on the installed CLI** (2.1.322, measured by headless sessions), not on the CLI's documents; an
   update can change it.
6. **No-ACT alternative for A:** helpers write in their session scratchpad (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/<session>/scratchpad`),
   which never asks. It would change `TMPDIR=/tmp/gov-os-emg-<name>` in EMG-common.md and the heavy-job tools that name it.
   Not recommended: it is a wider change than two rules, and the folders are the helpers' agreed place.

## 9. Not in this ACT: list items for tickets
1. **Launch template, the waiting line** (for a product-spec ticket, then an ACT for the generated copies in
   `.claude/templates/`, DEC-315; class (b), it instructs agents). Add to the end of `role-test-designer.md`
   (`template/governance/kernel/templates/`), and the same to `role-product-spec.md`, `role-reviewer.md` and
   `role-research.md`, which have no waiting line:
   > 12. Run a long command in the background with an exit-code file, and wait with {CMD:wait_for}. Never the Monitor
   > tool: no one can approve it in a launched session, and the guard does not read its command.

   `role-engineer.md` item 9 already names `{CMD:wait_for}`; add the Monitor sentence to it. The templates version moves
   by DEC-1121/1122's rule. Owner of the content: product-spec; the ACT: the CTO's helper again.
2. **LEAD-w2-common.md line 103 is out of date:** it says the guard refuses `Monitor` as an unknown tool (DEC-685). That
   is the product's full guard, which is not wired. The wired hook lets Monitor through to the permission layer. Owner:
   the CTO (a brief line), or a guard ticket if the owner wants Monitor refused outright.
3. **A brief line for rehearsal helpers (B2):** copy a hook with `git show HEAD:.claude/hooks/<file> > <copy>`, never
   `cp .claude/hooks/...`. Owner: the CTO.
4. **The launcher's check that a worker gets no added directories** (`launcher.py` line 300) reads the worktree's settings
   only. The main tree's `settings.local.json` carries two (ACT-PERMISSIONS-2), and a worktree session reads it (§8,
   item 1). Whether that matters is for the owner and an engineer ticket; not measured here.
5. Odd folders `.gov-runtime/s`, `.gov-runtime/sc`, `.gov-runtime/scr` ... exist in worktree `W2-153-d10r2-tests` (a
   path made one letter at a time by a tool). Not touched.

[DEC-1126 (10), DEC-1080, DEC-1081, DEC-1057, OPERATOR-AGENT-1 §2 and §3, ACT-PERMISSIONS-2, P-PERMISSIONS-1]
