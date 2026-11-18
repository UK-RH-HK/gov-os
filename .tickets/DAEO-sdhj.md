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
