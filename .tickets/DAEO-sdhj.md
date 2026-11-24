---
id: DAEO-sdhj
status: closed
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-17
tags: [implementation, full, emergency-2]
wbs_id: W2-17
title: gov update
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/update/**
- src/gov/install/**
- src/gov/release/__init__.py
- src/gov/adapters/**
- tests/unit/update/**
- tests/acceptance/W2-17/**
kpis:
  success:
  - 'The dry run: `gov update <B> --check` shows the whole update first and changes nothing. Verify: in a planted project adopted at fixture release A (`copier copy` at `vA`, adapters generated, `governance/framework.lock` naming A, all committed) with a fixture source holding release B, whose template updates one shipped file, adds one, removes one, changes one overlay file and changes one file the project also changed: `gov update B --check` exits 0 and prints A and B, the three checks passed (manifest, shipped files, wheel), every changed file under its outcome (updated, added, removed, merged or conflict, kept), the overlay file as untouched, the pinned gov it would install, the lock it would write, and the adapters and memory store it would refresh; afterwards `git status --porcelain` is empty, every file outside `.git` is byte-identical to before and no pin exists under the git common dir (`<common>/gov/`).'
  - 'The update: `gov update <B>` moves an adopted project to release B without re-adopting [CAP-45.a, W2-M176; EMERGENCY-2 7.6]. Verify: in the same planted project, `gov update B` exits 0; every shipped file the project had not changed holds release B''s bytes (the added file present, the updated one B''s, the removed one gone); the project''s changed file that B did not change is byte-identical to before and reported kept; every file under `governance/project/` is byte-identical (sha256 equal) to before, the one B changed among them; `.copier-answers.yml` names `vB`; `governance/framework.lock` names release B with B''s manifest sha256, and `gov doctor --json` run by the pinned gov reports in `framework_lock` no drifted file other than those the update reports kept or conflict; `<common>/gov/bin/gov --version` prints B''s CLI version; a skill B changed under `.rulesync/skills/` is regenerated into `.claude/skills/`; the report says the memory store was refreshed; one new commit holds the update with the record `governance/updates/B.json`, which names A, B, B''s manifest sha256 and every changed file''s outcome; `git status --porcelain` is empty.'
  - 'A project''s change to a shipped file is kept and reported, never silently overwritten. Verify: planted: a shipped file changed by the project and by release B in different lines holds both changes after the update (a clean three-way merge) and is reported merged; a shipped file changed by both in the same line keeps the project''s bytes unchanged, release B''s copy is written to `governance/updates/B/release/<path>`, and the report names it under conflicts; no file the update wrote holds a conflict marker (`<<<<<<<`).'
  - 'A failed update rolls back to the recorded point. Verify: a planted update whose adapter generation fails (a `rulesync` first on PATH that exits 1): `gov update B` exits non-zero naming the failed step and saying it rolled back; afterwards HEAD is the commit before, every tracked and untracked file outside `.git` is byte-identical to before, the lock still names A, and `<common>/gov/` holds the pin it held before (none, or A''s link and record).'
  failure:
  - 'An update to a release that fails hash verification refuses and changes nothing. Verify: three planted target releases: `manifest.json` not matching `manifest.sha256`; one template file at the tag `vB` whose sha256 differs from the manifest; a wheel (`--wheel <file>`) whose sha256 differs from the manifest''s: for each, `gov update B` and `gov update B --check` exit non-zero naming the manifest, the file, or the wheel with the mismatch; HEAD, every file outside `.git` and `<common>/gov/` are as before; the output never says the update was applied.'
  - 'An update refuses a tree it cannot roll back to, or a project it cannot read. Verify: a planted project with an uncommitted change: `gov update B` exits non-zero naming the uncommitted path and changes nothing; a project with no `governance/framework.lock`, or one stating `release: null`: exits non-zero naming the lock; a project already at B: exits non-zero saying it is at B.'
profile: FULL
sources:
- CAP-45.a
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W2-17/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- CAP-45.a
- AR-10
list_rows:
- W2-M176
---
# W2-17 gov update

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** The rest of K7 (DEC-941 item 3); CAP-45.a moves to Wave 3 by a CIT-P note or is a named exception.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-17), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/update/**` (new), `src/gov/adapters/**` (regeneration only), `tests/unit/update/**`.
- **KPIs, success:**
  - `gov update --check` reports the installed and target versions, the migrations and their impact.
  - The update [CAP-45.a, W2-M176]:
    - verifies the target release's manifest and file hashes;
    - applies the migrations with `copier update`, keeping the overlay files unchanged;
    - regenerates the adapters and rebuilds the affected indexes;
    - runs `gov doctor` and writes a ledger entry.
  - A failed update rolls back to the recorded point.
- **KPIs, failure:**
  - An update to a release that fails hash verification refuses.
  - An overlay file changed by the update is a failure and triggers the rollback.

**D9-FATES (DEC-1083):** Wave 3 by DEC-1083 (D9-FATES, as P1-PLAN §C); the status is kept.

**Moved to Wave 3's list 2026-11-16 by the owner (DEC-1201 (3)):** W2-17 leaves Wave 2's list (status `deferred`, tag `wave-2` removed); it is not closed and not done. It is listed in `docs/plan/WAVE_3_PARKING.md` under "Moved from Wave 2 (DEC-1201)". `gov plan` no longer offers it.

**Emergency 2 (2026-11-17): built for the release** (EMERGENCY-2 §6.1 "W2-17 build for the release", §7.6: EXAMIN moves to the release by `gov update` without re-adopting; with W2-18, §6.2 A-4). The KPI lines above are rewritten for §2 and §8, approved by the CTO's brief to the ticket lead:

- **No migrations line:** no release carries migrations (a release is its manifest, its template and its wheel); a release that needs one brings a new KPI line.
- **The update's steps, in order:** check the lock (held release A) and a clean tree; verify release B in the source (`_src_path` of `.copier-answers.yml`, or `--source`) at its tag `vB`: the record's manifest against `manifest.sha256`, every template file at the tag against the manifest, the wheel against the manifest's sha256; plan each shipped file three ways (release A's render, the project's file, release B's render, both rendered by `copier copy --skip-tasks` in temporary folders); with `--check`, print the plan and stop. Otherwise record the point (HEAD and the pin), install B's gov (W2-18's `gov install`), apply the plan (never writing an existing file under `governance/project/`), write `.copier-answers.yml` from B's render and the lock with B's verified manifest, regenerate the adapters with the pinned gov, check the overlay and the lock, commit with the record `governance/updates/B.json`, then refresh the memory store with the pinned gov's `gov rebuild`. Any failure before the commit rolls back to the recorded point; a store refresh that fails after the commit leaves the update applied and exits non-zero saying `gov rebuild` is to run.
- **A project's change to a shipped file** (the owner's to settle; built as recommended): a clean three-way text merge is applied; a conflicting one keeps the project's file whole and writes the release's copy beside the record for a hand merge. Alternatives: keep the project's file whole always; or the release wins and the project's copy is saved aside.
- **No guard, no sandbox, no ACTs (§2):** `gov update` is an ordinary command of the project's owner or CTO; its lock and answers file change by its own commit (2.10).

**Closed at the land 2026-11-18 by the CTO (EMERGENCY-2 4.3 step 5):** merged into w2/integrate with gov accept green on the merged tree; no review (3.6).

## Fix: two deny lines only; gov update takes the legacy lines out; the held-out Read deny step retires (DEC-1217 (6), DEC-1219 (4))
- **The bug:** `gov update` 0.1.3 put back the deny and allow lines Emergency 2 removed (`Edit(.tickets/**)`, `Bash(gov launch:*)`, one `Read` deny per held-out path), found in EXAMIN's report 28 (2026-11-18).
- **The fix (built on branch `e2/kit-e2` under the W2-208 ticket `DAEO-kt8e`, before the owner's ruling that it is a fix here reached its lead; merged into `w2/integrate` at `fc8a52fb9` on 2026-11-19):** the kit's permission source and kernel settings hold the two deny lines (`git push`, `sudo`) and no allow line (K1, `c81e9b796`); `gov update` takes the legacy lines out of a project's settings through its journal and keeps a line the owner added by hand (K2, F2, `f8b4a677f`); the held-out `Read` deny step retires (`write_read_rules` gone; K3, F1, `62658001c`). Its tests are `tests/acceptance/W2-208/` (K1 to K3, F1, F2; designer commit `d513e8559`), read by `gov accept W2-208`.
- **The chore beside it (DEC-1217 (7)):** the golden rules head the kit's CLAUDE.md and AGENTS.md and `judging-work` 1.2.0 agrees (K4 to K6: `1589dd08a`, `fa4bf7346`, `dced49bb6`): kernel text, the CTO's (EMERGENCY-2 3.5).
- **Evidence on the merged tree:** W2-208, W2-17, W1-38, W2-195, W2-56, W2-188, W2-201 and the adapters, update, brief, launch and opt-in unit tests: 1,958 passed, 0 failed.

## Fix: pending-update report and rollback (DEC-1223 (6))
- **The gap:** CAP-45.a lists "rollback" and CAP-45.b (`gov doctor` reports a pending update) has no code; both are gaps in
  this closed feature, found in `docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` ("Adopted repositories: the quiet point
  and the update"; "Placement and size") and approved by the owner as RB-6 (a), DEC-1223 (6): two fixes under W2-17, no
  new ticket. The tests are written first, red on the base (`tests/acceptance/W2-17/`, S5 to S7, the next S numbers).
- **Not here:** `gov release --patch`, the re-pin, the update pass (`gov update --auto`) and the quiet point: the feature
  ticket, later. Nothing in `src/gov/queue/**`.
- **Allowed paths for the fixes:** `src/gov/update/**`, `src/gov/doctor/**`, `src/gov/cli/**` where a command's arguments
  need it, `template/governance/kernel/hooks/sessionstart.py` (and its copy where the repository keeps one),
  `tests/unit/update/**`, `tests/unit/doctor/**`, `tests/unit/hooks/**`, `tests/acceptance/W2-17/**`.
- **Fix lines** (each observable, each with its verify; S5 to S7 in the acceptance README):
  - **S5 / U1, `gov doctor` reports a pending update (CAP-45.b).** A part `updates` reads, from the local source only
    (`_src_path` of the repository's `.copier-answers.yml`; its tags `v<X>` and the records at them; nothing is fetched,
    no network, no copier): the release the repository holds (its lock), the newest release in the source that has a
    verified record (`gov.release.verify_at`, manifest only) and is newer than the held one, that release's kind (`patch`
    or `bigger`: the `kind` key of `docs/releases/<X>/kind.json` at the tag where the record has one; no file, or one
    that does not read, or any other value: `bigger`), how many fixes it carries (the commits of `v<held>..v<newest>` in
    the source whose message has a `Fix:` trailer; 0 where the held tag is not an ancestor) and the next step (`at the
    next quiet point` for a patch; `bigger: the owner decides, gov update <version>` otherwise; where
    `governance/updates/<newest>.rolled-back.json` exists in the repository: `held: rolled back here; waits for a newer
    release`, with `pending: false` and `rolled_back: true`). Keys: `status` is always `report` (a notice: it never makes doctor unhealthy, whatever the source says),
    `held`, `newest`, `pending` (bool), `kind`, `fixes`, `next`, and `summary` (one line; `up to date (<held>)` when
    nothing newer exists). A repository with no held release, no readable source, or no verified newer record reports
    `pending: false` with `reason` and never raises. Verify: a planted source with two releases (A, and B a patch with
    `kind.json` and two `Fix:` commits) and an adopted clone holding A: `gov doctor --json`'s `updates` part names A, B,
    `patch`, 2 and the quiet-point step; with B's record carrying no `kind.json`, kind `bigger` and the owner step naming
    `gov update B`; with the clone at B: `up to date`, `pending` false; with `_src_path` pointing nowhere: `pending`
    false with a reason, doctor's exit and `healthy` as without the part; in every case `healthy` and the other parts'
    statuses are exactly those of the same clone with the source untouched.
  - **S6 / U2, session start prints one line when an update is pending.** The kernel's SessionStart hook adds one line
    to its `additionalContext` (a critical part, never trimmed by the cap) naming the held release, the newest and the
    next step, in the form `Gov OS update pending: this repository holds <held>, <newest> is the newest (<kind>): <next
    step>.`, for any role (the step is the doctor's `next` text, except that for a bigger release the line says `the
    owner decides, gov update <newest>` without the leading `bigger: `, the kind being in the parentheses); nothing when up to date or when the update is held after a rollback; it uses the same reading
    as the doctor's part (`gov.update.pending`), and a source that cannot be read, a repository that holds no release,
    or gov not importable prints nothing and the hook exits 0 (its other parts, the checkpoint resume and `tk ready`,
    are unchanged). Verify: the hook run with an empty event (`{}`) and `CLAUDE_PROJECT_DIR` the planted clone prints a
    JSON `additionalContext` that holds the line with both releases and the step, exit 0; up to date: no output, exit 0;
    `_src_path` broken: no output, exit 0; with the source tree's `GOV_ROLE=orchestrator` environment the line is there
    beside the existing parts.
  - **S7 / U3, `gov update --rollback` restores the previous release in one command.** Run from the repository root with
    the previous release's gov (`<git common dir>/gov/envs/<A>/bin/gov update --rollback`; no version given: with one
    it refuses, reason `usage`): it finds the update to undo as the lock's held release B and the commit that added
    `governance/updates/<B>.json` (refused as `UPDATE_REFUSED` with reason `no_update` where there is none, `dirty`
    for an uncommitted change); it takes the previous pin from the record's new field `pin_before` (`{"existed": bool,
    "link": <target or null>, "record": <pin.json as it was or null>}`, written by `gov update` into the record from the
    state it records before it installs B). **A record written before the field existed** (releases 0.1.3 and 0.1.4's
    updates): A is the record's `from`; the pin goes to `<common>/gov/envs/<A>` where that folder exists (the link to
    its `bin/gov` and a `pin.json` naming A and that environment), and the rollback is refused with reason
    `no_previous_pin` before anything changes where it does not. It reverts the update commit with `git revert` (a
    new commit; one commit holds the revert and the record below; history keeps the update commit and the revert);
    where later commits make the revert conflict it stops, runs nothing else, leaves HEAD, the tree and the pin as
    before and refuses with reason `rollback_conflict` naming the conflicting paths; it puts the pin's link and
    `pin.json` back to A (or removes them where the project held no pin before); runs `gov rebuild` with the restored
    pin's gov (the running gov where there is no pin), a failed rebuild leaving the rollback committed and exit
    non-zero as `UPDATE_STORE_FAILED` saying `gov rebuild` is to run; and writes
    `governance/updates/<B>.rolled-back.json` (`from` B, `to` A, `update_commit`, `pin`: the pin restored, in the shape
    of `pin_before`) in that commit (a commit cannot name itself, so no key names the revert commit).
    It leaves B's environment folder `<common>/gov/envs/<B>`. **Which gov runs it (W2-18's dispatch):** in a repository
    pinned at B, a gov started there is handed to B's, the one in doubt; so the pin dispatch (`gov.install.dispatch`)
    hands nothing over for `update --rollback`: the gov that was started, A's by the path above, runs it. Any failure before the commit puts HEAD, the tree and the
    pin back as they were. Verify: a planted clone updated A to B (the S2 fixture), then `--rollback`: every tracked
    file but the rolled-back record equals A's tracked state (the bytes of the commit before the update: lock, answers,
    settings lines, adapters, shipped files), the pin link and `pin.json` name A, `envs/<B>` still exists, the record
    exists, `git log` holds the update commit and the revert, the status is clean, the store was rebuilt (`retrieve
    --json`'s `store.commit` is HEAD); a planted later commit that changes a file the update changed makes the same
    command refuse with `rollback_conflict` naming it and HEAD, the tree and the pin unchanged; a record with its
    `pin_before` taken out rolls back the same way through the fallback; a project with no pin before the update has
    none after.
- **Order:** this section (`Role: orchestrator`); the test designer (Opus, the C3 trial of DEC-1222 (2); `src/gov/update/**`
  is C3); the engineer (Sonnet) until `gov accept W2-17` is green. Every commit carries `Task: DAEO-sdhj` and a `Fix:`
  trailer with the line's summary. The ticket stays closed.

**Landed:** merged into `w2/integrate` at `d2c920b9a` on 2026-11-20 by hand (the CTO; `gov queue` refused the selection: the docs committed since the last green base map to no suite, see L2-4); on the merged tree W2-17, W2-208, W2-18 and the update, doctor, hooks, install and opt-in units: 519 passed.

## Fix: a kernel hook is registered once after `gov update` (F4; EXAMIN report 28; DEC-1232, DEC-1233)

Found 2026-11-22 in EXAMIN's copy: `.claude/settings.json` held the `PostToolUse` `Bash` hook for `context_watch.py` twice,
in two command strings (the older generation's and the new one's), because the update removes only entries equal to the
old generation and adds the new one beside the older. Required: `gov update` never adds a hook entry already present
(same event, same matcher, same hook program, whatever the command text), and an update of a repository that has it twice
leaves it once, the project's own hooks untouched and in order. Kind: a fix; the ticket stays closed. Failing tests first:
`tests/acceptance/W2-17/test_w2_17_fix_hook_once.py` (README id S8; 5 red, 4 guards on the base), `aa2281b7f`; code
`src/gov/update/hooks.py` and `core.py`, `1e29c1c42`; units `tests/unit/update/test_fix_hook_once.py`. `gov adapters
generate` alone (`src/gov/adapters/merge.py`) can still add a hook beside an older form; only `gov update` collapses them
(a point for the owner of that module).

## Fix: `gov update` leaves `gov doctor` red (F6; the real G3 run of 2026-11-22; DEC-1232, DEC-1233)

Found by the real G3 run of 2026-11-22 (`.gov-runtime/scratch/orchestrator/log/g3-real-20261122.json`): `gov update`
writes `governance/updates/<version>.json`, which an adopted repository's path map does not classify, so doctor's
`path_map` part failed (`unclassified: ["governance/updates/0.1.5.json"]`) in all six of W2-81's kept repositories (doctor
exit 0 before, 3 after). Required: the kit's path map classifies `governance/updates/**`, and `gov update` adds the line to
an adopted repository's map that lacks it, as a merge (the other lines and comments stay; never a conflict; once).
EXAMIN's copy (read only) already classifies it (`- governance/updates/**`, line 37 of its path map). Kind: a fix; the
ticket stays closed. Failing tests first: `tests/acceptance/W2-17/test_w2_17_fix_updates_path_map.py` (README id S9; 6 red,
1 guard on the base), `20f88cbac`; code `src/gov/update/pathmap.py`, `core.py` and `template/governance/project/path-map.yaml`,
`35ebf28d5`; units `tests/unit/update/test_fix_updates_path_map.py`. The merge is textual (comments survive), exempt from
the overlay check, and skipped when an existing pattern already classifies the path. Lead `fixes-015b` (Sonnet), branch
`e2/fixes-015b`. `gov accept W2-17` green on the first run after the engineer's commits (12 lines pass, 70 passed);
`tests/unit/update`, `tests/unit/doctor`, `tests/unit/adopt`, W1-06, W1-48: 529 passed.

## Fix: `gov update` and `gov adopt` carry `disableClaudeAiConnectors` into the adopted settings (F1; fixes-015a; DEC-1232, DEC-1233)

Found by the E2 audit 3: an adopted repository's `.claude/settings.json` did not turn the claude.ai connectors off, so a
session started by hand there loaded them (Gov OS's own settings already had the key). Required: the kit's
`template/governance/kernel/settings.json` carries `"disableClaudeAiConnectors": true`, and `gov adopt` and `gov update`
(both through `gov adapters generate`) merge it into the adopted settings, keeping every other key and any value the
project already holds. Kind: a fix; the ticket stays closed. Failing tests first:
`tests/acceptance/W2-17/test_w2_17_fix_connectors_key.py` (README "The fix F1 (a)"), `361802ceb`; code
`src/gov/adapters/merge.py` (`CONNECTORS_KEY`, added by `merge_settings` where the key is absent) and the kit settings
file, `83b73ba96`; units `tests/unit/launch/test_fixes_015a_connectors.py`. Lead `fixes-015a`, branch `e2/fixes-015a`.
