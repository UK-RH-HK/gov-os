---
id: DAEO-kl5e
status: in_progress
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: engineer
external-ref: W2-50
tags: [wave-2, implementation, full]
wbs_id: W2-50
title: 'The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher''s sandbox (CIT-P)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/guard/runs.py
- src/gov/guard/decide.py
- src/gov/launch/launcher.py
- template/governance/kernel/checks/secrets-indexing.yaml
- src/gov/secrets/__init__.py
- tests/unit/guard/test_runs*
- tests/unit/launch/test_runs*
- src/gov/guard/protected.py
- tests/unit/guard/test_protected*
- tests/unit/secrets/**
- docs/changes/W2-50-CIT-P.md
- docs/changes/W2-50-CIT-E.md
kpis:
  success:
  - One durable root. ~/gov-os-runs/ is the one durable scratch root outside the repository, known to the guard and to the launcher's sandbox [DEC-728, W2-M355].
  - 'Its own folder only. A session of any role writes only under ~/gov-os-runs/<its own ticket>/. That folder is named by the ticket''s W2 id (its external-ref, as for worktrees), or by its tk id when
    it has none, and resolved from the session''s GOV_TICKET: The guard allows Write, Edit and judged Bash targets there; The launcher adds exactly that folder (not the root) to the sandbox write list;
    The folder is created on first use.'
  - Survival. A clone made there survives the session's end and a restart.
  - 'Never indexed. Nothing under ~/gov-os-runs is indexed by this repository''s stores, and this repository''s secrets-indexing check never scans it: A product clone that is adopted there has its own store,
    inside the clone; that store is the clone''s, not this repository''s; A planted secret in a clone there reaches no index of this repository.'
  - 'The secrets scan finishes. This repository''s secrets-indexing scan finishes on stores of today''s size (a 250 MB store.db, a 210 MB code graph): its time limit grows with the content''s size, or a large
    store is scanned in bounded chunks each within the limit, and its pool is bounded so that large files are not starved [DEC-853].'
  - 'A clean scan reused by its hash. A store whose hash has not changed since its last clean scan is not scanned again; its clean result is reused, keyed on the store''s hash [DEC-853].'
  failure:
  - 'Each refused, with the guard''s reason: another ticket''s folder under ~/gov-os-runs'
  - 'Each refused, with the guard''s reason: the root itself (a file directly in it, or removing it)'
  - 'Each refused, with the guard''s reason: a path outside it reached by .., a symbolic link or a hard link'
  - 'Each refused, with the guard''s reason: a session with no ticket'
  - 'Each refused, with the guard''s reason: any path outside the repository other than the temp folder and the session''s own folder.'
  - 'Each refused, with the guard''s reason: ~/gov-os-workbench and ~/gov-os-worktrees (other than the session''s own worktree) stay refused as before.'
  - 'The secrets scan stays whole and closed: every file is still scanned with every rule set; a scan that cannot finish still fails closed; a store changed by one byte is scanned again in full; a finding
    is never reused [DEC-853].'
profile: FULL
sources:
- DEC-728
- DEC-723
- DEC-159
- CAP-33
- DEC-738
- DEC-743
- DEC-853
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-50/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-728
- W2-M355
list_rows:
- W2-M355
---
# W2-50 The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-50), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Why:** the plan moves writing work to `~/gov-os-runs/<W2 id>/` (DEC-723), but nothing lets a session write there.
  - The guard allows writes outside the repository only in the temp folder (`src/gov/guard/decide.py`).
  - The launcher's sandbox write list holds only the session's own temp folder (DEC-159, `src/gov/launch/launcher.py`).
  - Clones under `/tmp` are lost on a reboot (W2-M355).
- **Route:** the change loosens the guard, so it goes through CIT-P with the owner's approval (CAP-33), like W2-09. DEC-728 is the owner decision behind it. The lead returns the CIT-P as a package before the engineer starts (queued Q-15). The test designer goes first, and a probe follows green.
- **Allowed paths:**
  - `src/gov/guard/runs.py` (new);
  - `src/gov/guard/decide.py` (the outside-repository rule, and `rmdir` of the root, R7);
  - `src/gov/launch/launcher.py` (the sandbox write list, and making the own folder before the session starts, R2);
  - `template/governance/kernel/checks/secrets-indexing.yaml` (the exclusion only);
  - `src/gov/secrets/__init__.py` (the link rule only: a link from `.gov-runtime/` into `~/gov-os-runs` is not followed; DEC-743 §6.1 (i));
  - `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`;
  - `docs/changes/W2-50-CIT-P.md`, `docs/changes/W2-50-CIT-E.md`.
- **KPIs, success:**
  - **One durable root.** `~/gov-os-runs/` is the one durable scratch root outside the repository, known to the guard and to the launcher's sandbox [DEC-728, W2-M355].
  - **Its own folder only.** A session of any role writes only under `~/gov-os-runs/<its own ticket>/`. That folder is named by the ticket's W2 id (its `external-ref`, as for worktrees), or by its `tk` id when it has none, and resolved from the session's `GOV_TICKET`.
    - The guard allows Write, Edit and judged Bash targets there.
    - The launcher adds exactly that folder (not the root) to the sandbox write list.
    - The folder is created on first use.
  - **Survival.** A clone made there survives the session's end and a restart.
  - **Never indexed.** Nothing under `~/gov-os-runs` is indexed by this repository's stores, and this repository's secrets-indexing check never scans it.
    - A product clone that is adopted there has its own store, inside the clone; that store is the clone's, not this repository's.
    - A planted secret in a clone there reaches no index of this repository.
- **KPIs, failure** (each refused, with the guard's reason):
  - another ticket's folder under `~/gov-os-runs`;
  - the root itself (a file directly in it, or removing it);
  - a path outside it reached by `..`, a symbolic link or a hard link;
  - a session with no ticket;
  - any path outside the repository other than the temp folder and the session's own folder.
  - `~/gov-os-workbench` and `~/gov-os-worktrees` (other than the session's own worktree) stay refused as before.
- **CIT-P approved (DEC-743, 2026-10-17)** within DEC-728: R1 to R8 as written (R7 scoped to the root only), §6.1 (i), the own folder open only while the ticket is `in_progress`, `ticket-lead` not among "any role". The engineer commits the CIT-P word for word before any code, and the CIT-E after (DEC-738 item 1). A session writes only under its own ticket's folder; nothing there is indexed or scanned; the workbench and other worktrees stay refused.
- **Widened for run 7 (owner, 2026-10-18, P-I):** `src/gov/guard/protected.py` uses the option reader this ticket built for `cp` and `install` for `mv` and `cp -l` too, so the guard reads every copy-like command one way, for writes and for reads; the paths gain `src/gov/guard/protected.py` and `tests/unit/guard/test_protected*`.
- **Widened for run 8 (owner, 2026-10-19, DEC-853, P-W2-49 (a)):** the secrets scan's time limit and pool are fixed in this resume, in `src/gov/secrets/__init__.py` (the scan only, keeping this ticket's link rule in `stores_with_secrets`): the time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit), and the pool is bounded so that large files are not starved. A store whose hash has not changed since its last clean scan is not re-scanned; its clean result is reused, keyed on the store's hash. Every file is still scanned with every rule set; a scan that cannot finish still fails closed; a changed store is always scanned in full; a finding is never reused. The paths gain `tests/unit/secrets/**`.
