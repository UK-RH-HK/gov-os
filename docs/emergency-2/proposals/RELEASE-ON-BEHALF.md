`docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` · the product-spec session of the Gov OS CTO, 2026-11-19 · **approved by the owner, DEC-1223** (RB-1 a, RB-2 a, RB-3 b, RB-4 b, RB-5 a, RB-6 a, RB-7 keep both); built as one feature ticket in two slices and two fixes under W2-17; the authority file goes on after a rehearsal on a scratch clone

Decisions cited: DEC-1220, DEC-772, DEC-722, DEC-861, DEC-1204, DEC-1211, DEC-1214, DEC-1217, DEC-1219, DEC-1222, DEC-409. Sources: DEC-1220 (3), EMERGENCY-2 2.4, 2.5, 2.6, 2.8, 3, 3.5, 4.6, 6.3, 8.2, 8.3, 8.4, Contract v5 CAP-02, CAP-43, CAP-45, T2-ESCALATION-RUBRIC 2 and 3, docs/emergency-2/release-0.1.2 and release-0.1.3, src/gov/release, src/gov/update, src/gov/install, src/gov/doctor, src/gov/dispatch, src/gov/resources, src/gov/queue, src/gov/close/nightly.py, tests/acceptance/W2-81, .tickets/DAEO-rt4s.md.

# Releasing on the owner's behalf

`docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` · 2026-11-19 · written by the spec-writing method · for the owner's decision; after release 0.1.4

**In five lines.** (1) A patch release is one that carries only fixes and chores; code decides that from the commits between two release tags. (2) The CTO may cut a patch release only when five gates pass by code, in order: the owner's standing yes is on file, the patch rule holds, the full suite (weekly tier included) is green on the exact release commit, the proving run is READY on the candidate, and the tree is in a state a release can be cut from. (3) The re-pin switches the machine's `gov` by one rename and puts the old one back by itself if a check fails. (4) Adopted repositories update by themselves at a quiet point, never with a conflict, with a check after and a one-command rollback. (5) You get one push per release; bigger releases, and every push to GitHub, stay yours. **This changes EMERGENCY-2 2.5 and 8.3 and narrows DEC-772, so it needs your decision recorded first (RB-1).**

## Problem

Every release so far (0.1.0 to 0.1.3) waited for the owner's hand: he types a code in a plain terminal, commits the record, tags it, runs a re-pin script, tells the CTO, and the CTO has each adopted repository run `gov update` by hand. Fixes pile up in the meantime: the head of `w2/integrate` is 300 commits past `v0.1.3`. A release by code needs seven things the code lacks today, read on the repository:

- **`gov release` refuses everyone but the owner in person** (`src/gov/release/command.py`: no Claude ancestor, no `GOV_ROLE`, a terminal, a typed code; DEC-772, after a reviewer showed a spoofed role could write a release). It neither commits nor tags; the docs say agents never tag.
- **The re-pin is a bash script per release with the version written into it** (`docs/emergency-2/release-0.1.3/repin.sh`). It commits as `Role: owner`. It does roll back by itself on a failed check, but the checks are four, not the hooks every session runs.
- **No gate ties a suite run to a release commit.** The nightly record (`docs/close/nightly/NR-*.json`) holds `head`, `tree`, `scope` and `verdict`, but the weekly tier (`tests/optin-weekly.txt`, DEC-1220 (1)) is outside its default run, and a record is untracked.
- **The proving run (W2-81) reads an adoption's outputs.** Its full form needs launched adopter sessions. Nothing runs it on a candidate by code.
- **`gov update` has no rollback after it commits** (it rolls back only a failed step). On a merge conflict it does not stop: `classify` in `src/gov/update/core.py` keeps the project's file, writes the release's copy aside under `governance/updates/<B>/release/` and goes on.
- **`gov doctor` reports no pending update, and session start does not run it** (CAP-45.b is a W2 line with no code).
- **Nothing says when a repository is quiet.** Pieces exist: the live-session registry (`~/.gov-os/machine/sessions`), the pause flag, the resource gate, the dirty-tree refusal. The landing takes no lock, and no file lists the adopted repositories.

## Users and scenarios

- **The owner** wants fixes in use within a day, without typing codes, and wants to know what happened and how to undo it. He keeps the say over features, the Contract and GitHub.
- **The CTO** cuts a patch release on a day with fixes landed and a green base. It never decides a bigger one.
- **An adopted repository's CTO** (EXAMIN today) wants its release to change only when nothing of its own is running.

Stories:
1. Seven fixes land over two days. The CTO runs the checks, the gates pass and the release is cut and pinned. The owner reads one push with the rollback line.
2. A ticket closes (a feature) between two releases. The patch check says bigger and names the ticket. The CTO brings the owner a package, as today.
3. The full suite has one red on the release commit. No record, no tag, no pin. The CTO fixes and starts again.
4. The post-pin check fails at night. The old `gov` is back within seconds; the owner is pushed once; the release is marked burned and the CTO cuts the next patch.
5. EXAMIN has a session open. The update waits. Two hours later nothing runs; the update applies, the check passes, a line goes into the morning brief.
6. EXAMIN's own edit conflicts with a fixed kit file. The update stops before it writes anything; its CTO and the owner are told once.

## Goals

- A patch release is decided by a rule code can check, never by judgement.
- No release is cut, tagged or pinned unless every gate passed on the exact commit released.
- A failed re-pin or a failed update puts the previous state back by itself, and says so.
- Adopted repositories reach a patch release with no one asked, only at a quiet point, and never with a half-applied merge.
- The owner is told of every release, in one push with what changed and the way back; the rollback is one command.
- Bigger releases, and everything that leaves the machine, stay the owner's.

## Non-goals

- No push to GitHub, by any path, and no change to the two denies (EMERGENCY-2 2.4).
- No signing (DEC-1214 L3, CAP-02.c).
- No release of a bigger change by the CTO, and no loosening of the plain `gov release` for the owner's own releases.
- No change to `gov update`'s three-way merge, its overlay rule or its hash checks.
- No new `gov` command: everything below is a flag or a step of `gov release`, `gov update`, `gov doctor` and the run-time tool's pass (the command table is being cut from 37 to 34, DEC-1217).
- No Contract, Charter or EMERGENCY-2 text changed by this design; the owner's yes (RB-1) lets the CTO and a product-spec session make those changes after.

## What a patch release is

Let N be the newest release tag whose record is in `docs/releases/`, and C the release's version commit (the commit that sets the version, as `1d4e6a875` did for 0.1.3). The release is a **patch release** when all five rules hold, each read by code from N to C. Anything else is a **bigger release**, and goes to the owner.

| Rule | Reads | Fails when |
|---|---|---|
| P1 version | `pyproject.toml` at C | it is not N's version with only the last number raised, or has a pre-release part |
| P2 owner's text | `git diff --name-only N C -- docs/contract docs/charter docs/emergency-2/EMERGENCY-2.md` | any path changed |
| P3 no feature | `.tickets/*.md` at N and at C; the non-merge commits N..C that touch `src/gov` or `template` | a ticket is closed at C and was not at N; or such a commit carries neither `Fix:` (with a `Task:` ticket closed at N) nor `Class: Q` nor `Class: C` |
| P4 no new command | the command names the CLI knows at N and at C | the sets differ |
| P5 no new record kind | the files under `template/governance/kernel/schemas` | one added or removed |

P2's third path and P5 are mine; you may drop them (RB-7). `Class:` alone cannot tell a feature from a fix: `F` is on 263 commits since `v0.1.2`, ticket merges and test-only commits alike. So P3 reads the ticket status and the `Fix:` trailer (which `gov queue` already uses for fixes, W2-201 X6), and uses `Class: Q` and `C` only for the CTO's direct work.

**What it says today.** Run on `v0.1.3` to the head: P2 fails (320 paths under `docs/contract`, the Charter), P3 fails (15 tickets closed; 47 ticket commits touch code, none carries `Fix:`), P5 fails (`memory-audit.schema.json` added), P4 passes. So 0.1.4 is a bigger release in content, and stays yours. From then on a bigger release is a minor number (0.2.0); only fixes and chores move the last number.

The result is written as `docs/releases/<X>/kind.json` (each rule, pass or fail, the offending ticket, commit or path). `gov release <X> --patch --check` prints it and writes nothing.

## The gates and the cut

The gates run in this order and stop at the first red. The CTO session runs them; nothing in them is its judgement.

| Gate | What code reads | Red means |
|---|---|---|
| G0 authority | `governance/project/release-authority.yaml`: `patch_releases: on`, the decision id, `bake_hours`; its last commit carries the decision-record trailer `Decided-by: owner` | refused; nothing read further |
| G1 the rule | P1 to P5 above | refused, with the rule named; the CTO takes it to the owner as a bigger release |
| G2 the suite | a nightly record with `scope: full`, the weekly tier included (the runner gains `--optin weekly`, and the record names it), `verdict: green`, `head` equal to C in full, `tree` equal to C's tree | no record, an older commit's record (even C's parent), a record without the weekly tier, or any red: refused |
| G3 the proving run | the update rehearsal below, READY, on the candidate | not READY: refused |
| G4 the state | tree clean; C an ancestor of `w2/integrate`; no `gov pause` freeze; no tag `v<X>` and no record `<X>` yet; the previous release's record readable | refused |

**G2 on the exact commit.** The suite takes about two hours (103 minutes on three workers before the weekly tier moved out; the tier was 49 % of that run's time, DEC-1220). So it runs on a detached worktree of C, through the heavy slot, while landings go on. C stays in the history; whatever lands after is in the next release. The CTO copies the record into the release folder; the untracked original is removed so the build sees a clean tree.

**G3, the proving run for a patch (the update rehearsal, RB-2).** The six synthetic repositories of W2-81, adopted at N and kept from the last bigger release's full proving run, each in a throwaway clone: `gov update --check` shows no conflict; `gov update` to C's release applies; `gov doctor` exits as it did before; the W2-81 judge, in its `read` mode, over the kept outputs and the clone, is still READY; `gov close` of one ticket in each clone exits 0. It starts no adopter session and costs no model time. The full run with adopter sessions (Sonnet, DEC-1221) stays the release acceptance of a bigger release (EMERGENCY-2 8.2).

**The cut** (`gov release <X> --patch`, only after G0 to G4, run by the CTO, `GOV_ROLE=orchestrator`; every other role is refused, as `--lock-from` refuses them today):
1. Build the record at C exactly as `gov release` builds it: manifest, file hashes, the wheel's sha256, notes, `manifest.sha256`. Add `kind.json` and `gates.json` (the suite record's name and head, the proving run's report, the rule's result). The record's hash covers the manifest only, so these two do not change it.
2. Commit the record on a side branch whose parent is C (as the re-pin script already requires), with `Role: orchestrator`, `Decided-by: owner (standing, DEC-<n>)`, `Task: release`. Tag it `v<X>`, annotated, unsigned, locally.
3. Merge that commit into `w2/integrate` with an ordinary merge. It adds new files only, so it cannot conflict, and landings need not stop while the gates ran.

The plain `gov release <X>` is unchanged: the owner in person, a plain terminal, the typed code (DEC-772, DEC-409). It is the only way to cut a bigger release.

## What the CTO may run, and where a release lives

| The CTO session may run | The CTO session never runs |
|---|---|
| the version commit (a chore); `gov release <X> --patch --check`; the gate runs through the heavy slot; `gov release <X> --patch`; the re-pin step; `gov update --auto` by hand until the pass has it | `git push`, `sudo`; plain `gov release` for a bigger release; any edit of the authority file other than by the decision-record commit; moving or deleting a release tag; changing a release record after the cut (DEC-722 already refuses it) |

Where the artifacts are, and what leaves the machine:

| Artifact | Place | Leaves the machine |
|---|---|---|
| record, `kind.json`, `gates.json`, `NOTE.md` | `docs/releases/<X>/` on `w2/integrate` | no |
| tag `v<X>` | the local Gov OS repository | no |
| wheel; pin environment | `~/.local/share/gov-os/wheels/<C>/`; `~/.local/share/gov-os/pin-<C>` | no |
| the machine's `gov` | the link `~/.local/bin/gov`; the registry entry in `governance/project/tool-registry.yaml` | no |
| rollback script | `~/.local/share/gov-os/rollback.sh` | no |
| an adopted repository's pin | `<git common dir>/gov/envs/<X>`, `<git common dir>/gov/bin/gov`, `governance/updates/<X>.json` | no |
| the hourly bundles (`gov backup`) | `~/.gov-os/backups/` | no: they carry the tag, locally |

Nothing is fetched or sent. The wheel is built and installed offline; Copier renders from the local source path in `.copier-answers.yml`. The one thing that leaves the machine is the push text, through the CTO's own session (its push tool) or the run-time tool's `--push` command.

## Re-pin and its rollback

The re-pin is `docs/emergency-2/release-0.1.3/repin.sh` made general: the version is read from the tag, not written in. Steps, each stopping before the switch on failure (nothing changed for sessions): the tag is annotated and its parent is C; only the record's files differ between C and the tag; the manifest matches its hash and names the version and commit; the wheel built twice from C equals the record's sha256; the new environment `pin-<C>` is made beside the live one and its `gov --version` says the release.

Then the switch (one rename of `~/.local/bin/gov`) and the **post-pin check**, through the new link: `gov --help`; `gov launch --help`; a search of the memory store with both its facets; **the five hook programs of this repository's settings, run with an empty event, each exiting 0** (every session runs them; today's script does not); `gov doctor` here shows no part unhealthy that was healthy in a reading taken just before the switch.

- **Pass:** the registry entry is committed (`Role: orchestrator`, `Decided-by: owner (standing)`), `repin.json` says `ok`, `rollback.sh` is written, the push goes out.
- **Fail:** the link goes back to the old pin by one rename, `repin.json` says `rolled_back` and why, the release is **burned** (its tag and record stay; an immutable release is never deleted), the owner is pushed, the CTO fixes and cuts the next patch. Adopted repositories never update to a burned release.

**The rollback line the owner pastes** is `bash ~/.local/share/gov-os/rollback.sh`. It is plain shell, not `gov`, because the new `gov` is the thing in doubt. It holds exactly the line of 0.1.3's re-pin (`ln -sfn <old pin>/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r`) and adds the release to `~/.local/share/gov-os/burned`, which the update pass reads. It restores what every session sees. It leaves the new pin folder, the tag and the registry commit (the CTO reverts that commit in its next work).

## Adopted repositories: the quiet point and the update

**Which repositories.** The ones listed in `~/.gov-os/update/repositories`, one path a line, written by the CTO when a repository is adopted (EXAMIN's copy is the first). Each names its source through its own `.copier-answers.yml`.

**The target.** The newest release in the source that has a verified record, `kind.json` saying patch, `repin.json` saying `ok`, no mark in `burned`, and an age of at least `bake_hours` (default 4: the machine's own pin runs it first). If a bigger release lies between the held one and the target, nothing is automatic; the owner decides that one.

**Quiet point.** All of these, read twice: once to decide, and again under the repository's lock just before the first write.

| Quiet means | Read from |
|---|---|
| no session of the repository | the live-session registry (any entry whose repository or worktree is this one); and, for an interactive session the registry does not hold, no `claude` process whose working folder is inside it (from `/proc`, as the resource gate reads) |
| no landing, no half-done git operation | a lock file in `<git common dir>/gov/` that `gov queue` and the update both take (to build); no merge, rebase or cherry-pick in progress; the tree clean (`gov update` already refuses a dirty tree) |
| not paused | the `gov pause` freeze flag |
| the machine has room | the resource gate open, which includes load below the processor count |
| no earlier failure for this release | no `rolled-back` or `held` record for this repository and release, unless its head moved since |

**Who runs it.** A step of the run-time tool's pass, every 15 minutes (W2-207's one cron line; RT-7 keeps one watcher), calling `gov update --auto`. Until W2-207's cut-over, the CTO runs `gov update --auto` by hand (RB-5). It is one repository at a time.

**The update** (`gov update <B> --auto`), in order:
1. A fresh `gov backup` of the repository (a verified bundle outside the tree).
2. `gov update <B> --check`. If it lists any file under `conflicts`, **stop**: nothing is written, no pin placed; a `held` record is written; the repository's CTO gets one message (`gov msg send`) naming the files, and the owner one push per repository and release. (Today `gov update` would go on; `--auto` adds the refusal `UPDATE_REFUSED` with reason `conflicts`, before any write.)
3. The update as today: the three-way merge, the pin placed beside the old one, the lock and answers, the adapters, one commit, the record `governance/updates/<B>.json`, the store refreshed. A failed step already rolls back.
4. **The check after:** `gov doctor` shows no part unhealthy that was healthy before; `gov check` shows no RED family that was not RED before; the repository's own tests selected for the files the update changed, by the landing's selection (skipped, and said so, where the repository names none).
5. A failed check runs the rollback below by itself, writes `rolled-back`, tells the repository's CTO and pushes the owner.
6. A pass writes the result line for the morning brief and a message to the repository's CTO.

**The rollback of an update** is one command, run from the repository root with the **previous** release's `gov`, the one not in doubt:

`<git common dir>/gov/envs/<A>/bin/gov update --rollback`

(`<A>` is the release the repository held; the update's push and its brief line print the whole path.) It reverts the update commit with `git revert` (a new commit; history stays; if later commits make the revert conflict it stops and says so, changing nothing), puts the pin's link and `pin.json` back to A (the record gains a `pin_before` field for it), runs `gov rebuild`, and writes `governance/updates/<B>.rolled-back.json`. It restores every tracked file of the update, the lock, the answers, the settings lines, the adapters, the memory store and the pin. It leaves B's environment folder for diagnosis. The hold lifts when a newer release appears.

**`gov doctor` and session start (CAP-45.b).** A part `updates` reads the source's tags and reports: the held release, the newest, the kind, how many fixes it carries, and what happens next ("at the next quiet point" or "bigger: the owner decides, `gov update <version>`"). Session start prints one line when an update is pending. Severity is the release's kind; the manifest has no link to lesson records, so the "highest lesson severity" of CAP-45.b has nothing to read (a discovery, below).

## The pushes

A push is the text of the stall push today: one detached command, at most 190 characters (the dispatcher cuts it there). The long form is `docs/releases/<X>/NOTE.md` and the morning brief.

| When | Text (a worked example, with its length) |
|---|---|
| a release is pinned | `Gov OS 0.1.5 released (patch, 7 fixes). Suite green on 1b2c3d4e, proving run READY, pin live. Roll back: bash ~/.local/share/gov-os/rollback.sh` (143) |
| a re-pin fails | `Gov OS 0.1.5 NOT pinned: post-pin check failed (hooks). Rolled back, old gov live, nothing for you to do. Release burned; CTO cuts 0.1.6.` (137) |
| an update is held or rolled back | `EXAMIN update to 0.1.5 held: 2 files conflict. Repo unchanged. Its CTO has the list; nothing for you unless you want to decide it.` (130) |

`NOTE.md` holds: the version; each fix in plain words (from the `Fix:` lines and the chore subjects, one line each); the gate evidence (the suite record, its head, the weekly tier, the proving run's report, the rule's result); the rollback line; and which repositories update next and when. An update that succeeds is not a push: it stops nothing, so it is a line in the morning brief (T2 rubric, §3), with its rollback command (RB-4).

## Placement and size

After 0.1.4 and EXAMIN's fresh 80, and after W2-207's cut-over (the pass needs it). By DEC-1219 (6) a new ticket is for a new feature only:

- **One new feature ticket, FULL** (it touches kernel, release and update code): the patch rule and the gates in `gov release --patch`, the general re-pin with its hook check and rollback script, the nightly's weekly-tier option, the pushes and `NOTE.md`, and the update pass with its quiet point. About 900 lines of code and the tests, built in two slices by one lead: (a) patch release, (b) automatic update. **It extends W2-16 (release) and W2-17 (update) and replaces neither**: both are closed, and a new KPI line on a closed feature is a new ticket (EMERGENCY-2 4.6).
- **Two fixes under W2-17, no ticket:** CAP-45.b's `gov doctor` part and session-start line, and the update's `--rollback`. CAP-45.a already lists "rollback" and CAP-45.b is a W2 line with no code, so both are gaps in a closed feature. Failing test first, then the code, recorded in W2-17's record with `Fix:` trailers. They can go out sooner than the rest, even in 0.1.5, because they change nothing about who releases.
- W2-18 (the pinned install) is not changed.
- The first patch release is rehearsed on a scratch clone of this repository and a scratch `$HOME` before the authority file is turned on.

## KPIs

- K1: When the commits between the last release and the candidate change the Contract, the Charter or EMERGENCY-2, close a feature ticket, add a command or add or remove a kit schema, the patch release is refused and the answer names each rule that failed and what failed it; when none of that happened, the answer says patch.
  Fails if: a patch release is cut with any such change in range, a refusal names no rule, or a candidate with fixes and chores only is called bigger.
- K2: No release record, tag or new pin exists after any gate was red or missing: the standing yes, the rule, the full suite with its weekly tier, the proving run and the state check.
  Fails if: a record, a tag or a pin appears when a planted gate is red, missing or stale.
- K3: The suite's evidence is for the exact commit released: a record of the commit's parent, of another branch, or without the weekly tier is refused.
  Fails if: a release is cut on a suite record whose commit or tree is not the release commit's.
- K4: When the check after the switch fails, the machine's previous gov is live again within one minute, the release is marked burned, and the owner receives one push saying so; no adopted repository updates to it.
  Fails if: the machine's gov still names the new pin after a failed check, no push is sent, or an adopted repository later updates to the burned release.
- K5: The CTO never cuts a bigger release or a patch release without the owner's recorded standing yes: the plain release command still refuses everyone but the owner in person with his typed code, and the patch path refuses when the authority file is off, absent or not committed by a decision record.
  Fails if: any tag of a bigger release appears without the owner's typed code, or a patch release is cut with the authority file missing or off.
- K6: Within five minutes of a release being pinned, the owner receives one push of at most 190 characters that names the version, the number of fixes, the suite and proving-run evidence and the rollback line; the release folder holds the long note; and the pasted rollback line, run in a plain terminal, puts the previous gov back.
  Fails if: no push arrives, the push lacks the version, the evidence or the rollback line, it is longer than 190 characters, or the pasted line does not restore the previous gov.
- K7: An automatic update starts only at a quiet point, read twice: no live session of the repository, no landing or half-done git operation, no freeze, the machine's gate open, a release at least the bake time old, a verified pin and no earlier failure for it.
  Fails if: any tracked file or the pin of a repository changes while a session of it is live, a landing is running, the repository is paused, or the release is younger than the bake time.
- K8: A merge conflict stops the update before anything is written: the repository's files, its lock, its pin and its history are byte for byte as before, its CTO gets one message naming the files, and the owner one push per repository and release.
  Fails if: any file, the pin or the lock differs after a conflicting update, a release's copy is left aside in the repository, or the notices repeat on each pass.
- K9: After an automatic update the diagnosis and scoped test run decide: a part newly unhealthy rolls the update back by itself and tells the repository's CTO and the owner; and the one rollback command, run with the previous gov, brings back every tracked file, the lock, the settings lines, the adapters, the memory store and the pin as they were.
  Fails if: a newly red check leaves the update in place, or after the rollback any of those differs from the state recorded before the update.
- K10: At session start and in the doctor's report, every repository says which release it holds, which is the newest, whether the update is pending and of what kind, and for a bigger release says the owner decides.
  Fails if: a session in a repository with a pending release is told nothing, a bigger release is shown as automatic, or a burned release is offered.

## How each KPI is verified

The K lines above are each KPI's line and its failure; this table adds the observation. All run in temporary folders with a temporary `$HOME`; none cuts a real release.

| Code | In short | Verify |
|---|---|---|
| K1 | the patch rule | a built repository with two tags and one planted change each (a contract path, a ticket closing, a new command module, a schema added, a commit with neither `Fix:` nor a quick class, then none): `gov release <X> --patch --check` names exactly the planted rule, and passes the clean one |
| K2 | red gate never cuts | for each gate, one planted red, missing or stale input: `--patch` exits non-zero and the folder, tags and pin links are unchanged (compared before and after) |
| K3 | exact commit | suite records for C, for C's parent, for C with the weekly tier missing, and a green one with a different tree: only the first passes |
| K4 | re-pin rollback | a planted pin whose hook fails: the link names the old pin within 60 seconds, `repin.json` says `rolled_back`, one push is recorded by a stand-in push command, and `gov update --auto` refuses that release |
| K5 | the owner's hand | the plain `gov release` from an orchestrator session is refused as today; `--patch` with the authority file off, absent, or last committed without the decision trailer is refused; on a bigger range it is refused with K1's answer |
| K6 | the push | the stand-in push command receives one text of 190 characters or fewer carrying version, count, evidence and rollback line; `NOTE.md` exists; running `rollback.sh` in a temporary `$HOME` restores the previous link |
| K7 | quiet point | each of the five planted conditions in turn (a registry entry, an unregistered process in the folder, a held lock, a freeze flag, a young release) leaves the repository byte for byte unchanged; with none, it updates |
| K8 | conflict | a clone with an edit to a kit file that the release also changes: `gov update --auto` exits with `UPDATE_REFUSED`, the tree, lock, pin and history compare equal before and after, one inbox message and one stand-in push exist after three passes |
| K9 | check after, rollback | a release whose update breaks one doctor part in the clone: the update ends rolled back, no later pass tries it; the rollback command run by hand after a good update restores every tracked file, lock, settings, adapter output, store and pin link (a byte comparison of a before-snapshot) |
| K10 | pending update | `gov doctor` and the session-start output in a clone one patch behind, one bigger behind, and one with a burned release: each prints the right line |

## Test data

| source | kind | owner | licence or recipe | privacy | secrets | hidden half | secured |
|---|---|---|---|---|---|---|---|
| synthetic release histories: a repository with two release tags and, between them, one planted change per patch rule, plus a clean range | synthetic | independent test designer | built at test time from a fixed seed, one commit at a time, with the trailers and ticket files each case needs | none | none | n/a | yes |
| the six W2-81 synthetic repositories, adopted at the previous release | synthetic | independent test designer (W2-81's builders) | the W2-81 builders with the seed recorded in the run's report; adopted by the stages that need no session | none | the secret-history repository's planted value is drawn in memory and never written, as W2-81 does | n/a | yes |
| an adopted clone with an edit that conflicts with a kit file the next release changes | synthetic | independent test designer | the first of the six repositories, one tracked kit file edited, built at test time | none | none | n/a | yes |
| suite and gate records: green, red, stale head, wrong tree, no weekly tier, authority file on, off and unsigned | synthetic | independent test designer | JSON and YAML written at test time from the record forms in `docs/close/nightly` and the authority file's own form | none | none | n/a | yes |
| a temporary `$HOME` with a pin folder, a link, a planted failing hook and a stand-in push command | synthetic | independent test designer | built at test time in a temporary folder; no real pin, link or push is touched | none | none | n/a | yes |

## Out of scope

- The release 0.1.4 itself: the owner's hand, as decided (DEC-1217; R-1).
- Wave 3 items: signing releases (CAP-02.c), lesson severity in release notes, a minor or major release by code.
- The Contract's new text for this feature (a covers item under CAP-43 and the wave note that says the owner cuts and re-pins) and the changes to EMERGENCY-2 2.5 and 8.3, `docs/releases/README.md`, DEC-772's wording and the orchestrator's role text: after the owner's yes (RB-1), by the CTO (EMERGENCY-2 3.5) and, for the Contract, as the owner's own decision.
- The imports feature (IM-1) and the run-time tool's cut-over (W2-207): separate work; this design waits for the second.
- A repository's own CI or release process: not Gov OS's.

## Open questions

Answer by code, for example "RB-1 a, RB-2 a, RB-3 b, RB-4 b, RB-5 a, RB-6 a, RB-7 keep".

- Question RB-1: May the CTO cut patch releases by code, which changes EMERGENCY-2 2.5 and 8.3 and narrows DEC-772 for patch releases only?
  - Options: (a) yes, standing, with the authority file as the off-switch and one rehearsal on a scratch clone first (cost: your hand leaves the patch path; the rule and gates are the only check); (b) a trial: for the first three patch releases the CTO does everything but you type the code (cost: three more waits, and evidence the rule is right); (c) no (cost: today's wait for every fix)
  - Recommendation: (a). The rule fails safe: a doubtful change counts as bigger and comes to you, and the off-switch is one line. The rehearsal gives the evidence (b) would. Confidence: medium; the main risk is the rule missing a feature committed as a chore, which a ticket flip would still catch.
- Question RB-2: Which proving run gates a patch release?
  - Options: (a) the update rehearsal on the six kept repositories, by code, no model time (cost: it tests that the update and adoption still work, not new adoption behaviour); (b) the full run with launched adopter sessions on Sonnet (cost: hours and model spend for every fix)
  - Recommendation: (a) for patch releases, (b) kept for bigger ones (EMERGENCY-2 8.2). A patch adds no feature, so what it can break is the update and the kit. Confidence: medium; `--mode read` needs a first full run's kept outputs, which the 0.1.4 acceptance gives.
- Question RB-3: How long after a release is pinned do adopted repositories wait before they update?
  - Options: (a) none (cost: no evidence from the machine's own use); (b) 4 hours (cost: a short delay); (c) 24 hours (cost: a fix reaches EXAMIN a day late)
  - Recommendation: (b), set as `bake_hours` in the authority file. The machine's own pin runs the release first; four hours covers a working session's worth of hooks. Confidence: medium.
- Question RB-4: What does an automatic update of an adopted repository send you?
  - Options: (a) a push for every update (cost: more pushes than releases once there are several repositories); (b) a push only when an update is held or rolled back, and a line with its rollback command in the morning brief when it succeeds (cost: a success is read the next morning); (c) one batched push when every listed repository has updated or 24 hours have passed (cost: a late failure notice)
  - Recommendation: (b). A success stops nothing, which your rubric sends to the morning brief (DEC-1217 (5)); a failure leaves the repository on the old release and is the case that needs you. Confidence: high.
- Question RB-5: What runs the automatic update?
  - Options: (a) a step of the run-time tool's pass after W2-207's cut-over, by hand until then (cost: waits for W2-207); (b) its own cron line (cost: a second watcher, against RT-7); (c) each repository's CTO runs it when it chooses (cost: it is not automatic)
  - Recommendation: (a). One watcher is what you approved (RT-7), and the pass already reads the registry, the gate and the freeze flag. Confidence: high.
- Question RB-6: How is the work ticketed?
  - Options: (a) one new feature ticket in two slices, and CAP-45.b's doctor part and the update's rollback as two fixes under W2-17 (cost: one ticket to run); (b) everything in one new ticket (cost: a fix to a closed feature hidden in a feature); (c) reopen W2-16 and W2-17 (cost: against your rule that a new KPI line on a closed feature is a new ticket)
  - Recommendation: (a). Confidence: medium; whether CAP-45.b is a fix or a new line is the CTO's reading of the Contract.
- Question RB-7: Keep my two additions to the patch rule: P2's third path (EMERGENCY-2 itself) and P5 (no kit schema added or removed)?
  - Options: keep both (cost: a release that adds a schema waits for you); drop P5 (cost: a new record kind can ship without you); drop both (cost: the strategy text could change in a patch)
  - Recommendation: keep both. They are cheap, they fail safe, and a new record kind changes what every adopted repository holds. Confidence: medium.

## Accepted by

The owner, by his decision on RB-1 to RB-7, recorded by the orchestrator (DEC-861). Then, for each KPI, the independent test designer's acceptance tests written from K1 to K10, red on the base; the engineer's `gov accept` green; one rehearsal of a patch release and an update on a scratch clone and scratch home, whose record the CTO reads before the authority file is turned on; and the first real patch release, whose push and note the owner reads.

## For the owner

You asked for releases on your behalf for patches only, with the way back in your pocket. The design gives it this way. A patch release is one the code proves carries only fixes and chores: no Contract, Charter or EMERGENCY-2 change, no feature ticket closed, no new command, no new kit schema. The CTO may cut one only when your standing yes is on file, the full suite (weekly tier too) is green on that very commit, the proving run passes on it, and the tree is in order; then it cuts, pins the machine's `gov` and checks it, and puts the old one back by itself if the check fails. You get one short push per release with the fixes, the evidence and a rollback line that is plain shell, so it works even if the new `gov` does not. Adopted repositories update only when nothing of theirs is running, never with a conflict, with a check after and one command back. Nothing goes to GitHub and nothing is signed; a bigger release, such as 0.1.4 would be today, is still your hand and your typed code. This changes the text of EMERGENCY-2 2.5 and 8.3, so it starts with your yes on RB-1; my recommendation on all seven is in the table above, and the one I am least sure of is RB-2 (what proves a patch). Nothing is built, no ticket is opened, and the file is not committed.
