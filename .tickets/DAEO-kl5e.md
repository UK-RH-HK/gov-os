---
id: DAEO-kl5e
status: open
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
- tests/unit/guard/test_runs*
- tests/unit/launch/test_runs*
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
  failure:
  - 'Each refused, with the guard''s reason: another ticket''s folder under ~/gov-os-runs'
  - 'Each refused, with the guard''s reason: the root itself (a file directly in it, or removing it)'
  - 'Each refused, with the guard''s reason: a path outside it reached by .., a symbolic link or a hard link'
  - 'Each refused, with the guard''s reason: a session with no ticket'
  - 'Each refused, with the guard''s reason: any path outside the repository other than the temp folder and the session''s own folder.'
  - 'Each refused, with the guard''s reason: ~/gov-os-workbench and ~/gov-os-worktrees (other than the session''s own worktree) stay refused as before.'
profile: FULL
sources:
- DEC-728
- DEC-723
- DEC-159
- CAP-33
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
  - `src/gov/guard/decide.py` (the outside-repository rule only);
  - `src/gov/launch/launcher.py` (the sandbox write list only);
  - `template/governance/kernel/checks/secrets-indexing.yaml` (the exclusion only);
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
