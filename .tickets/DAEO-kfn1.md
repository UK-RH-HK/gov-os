---
id: DAEO-kfn1
wbs_id: W2-189
external-ref: W2-189
title: "The store fresh after an adoption's last commit, or gov retrieve serving the last good store naming its commit"
type: task
class: implementation
role: engineer
profile: FULL
status: in_progress
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-16T05:39:29Z
deps: [DAEO-2bdu]
links: []
tags: [wave-2, adoption, memory, retrieval]
allowed_paths:
- src/gov/retrieval/retrieve.py
- src/gov/retrieval/lexical.py
- src/gov/retrieval/semantic.py
- src/gov/retrieve/command.py
- src/gov/adopt/stages.py
- src/gov/adopt/command.py
- tests/unit/retrieval/test_w2_189*
- tests/unit/adopt/test_w2_189*
- docs/probes/DAEO-kfn1/**
reads:
- src/gov/retrieval/**
- src/gov/retrieve/**
- src/gov/adopt/**
- src/gov/rebuild/**
- governance/project/orchestration/packages/P-W2-81-VERDICT-1.md
- template/governance/kernel/skills/retrieval/SKILL.md
needs:
- src/gov/retrieval/retrieve.py
- src/gov/adopt/stages.py
waits_on:
- ref: DAEO-2bdu
  reason: W2-88 holds the adoption's memory stages (A9) and S11, the store practice this ticket completes; closed
- ref: DAEO-rmhj
  reason: W2-138's store_of (the store's commit in every result) is merged on w2/integrate; this ticket extends it, so the lead merges integrate first
est_loc: 160
kpis:
  success:
  - line: "S1 In a repository adopted with `gov adopt --lite` whose HEAD has moved past the commit its store was built at (the adoption's own closing commits: stage records, verdicts, tickets), `gov retrieve` answers a query whose source file is unchanged since that commit with that file in its evidence, instead of stopping `FACET_UNAVAILABLE` with no evidence [DEC-1197 (2)(i), W2-88 S11]"
    verify: "tests/unit/retrieval/test_w2_189_moved_head.py: a fixture git repository with its store built at commit X, then one commit that adds only a file under governance/adoption/; `gov retrieve` (and gov.retrieval.retrieve) for a phrase planted in an unchanged file returns that file in its evidence and does not stop FACET_UNAVAILABLE"
  - line: "S2 Every answer names the store it was answered from and how far it lags: the result's store entry carries the commit the store was built at (W2-138 S1), the HEAD it was asked at, and the tracked paths that changed between the two (`stale`, empty when they are equal); `gov retrieve`'s output shows the commit and the count of stale paths [DEC-1197 (2)(i), DEC-1090 (3)]"
    verify: "tests/unit/retrieval/test_w2_189_store_named.py: the S1 fixture gives store commit X, head HEAD and stale exactly the added record; a fixture whose store is built at HEAD gives stale empty and commit equal to head; the CLI's JSON output carries the same three values"
  - line: "S3 The same holds after an ordinary commit later in the adopted repository's life, with no refresh hook installed (EXAMIN's case: A9 records the refresh hook as the operator's, so no adopted repository rebuilds its store after each commit today): the answer comes from the last good store, named as in S2 [DEC-1197 (2)(i)]"
    verify: "tests/unit/retrieval/test_w2_189_moved_head.py: a fixture with two later commits that change one source file and add one; queries on unchanged files answer from the store with both paths in stale"
  failure:
  - line: "F1 Text from a file changed since the store's commit served as current: evidence from a path in `stale` is never returned (it is left out and named), so an answer never quotes a file's old content as if it stood [DEC-1197 (2)(i), DEC-342]"
    verify: "tests/unit/retrieval/test_w2_189_stale_left_out.py: a phrase planted in a file at X and removed from it in a later commit is not returned from that file; the file is named in stale; a phrase planted only after X is not invented"
  - line: "F2 A store that is missing, empty, unreadable, or built with other index-time methods than rebuild.yaml's (DEC-1068) answered from as if usable: those still stop `FACET_UNAVAILABLE` with their reason, as today [DEC-342, DEC-1068]"
    verify: "tests/unit/retrieval/test_w2_189_unusable.py: one case each (no store, an empty store, a corrupt store file, a changed embed recipe) keeps FACET_UNAVAILABLE and its reason"
  - line: "F3 An answer from a store whose commit is not HEAD that does not name both commits, or a change to what any role may read: the stale path list is computed from tracked paths only and a search still applies the path map's walls and hidden sets as before [DEC-820, DEC-1197 (2)(i)]"
    verify: "tests/unit/retrieval/test_w2_189_store_named.py: the moved-head result always carries commit, head and stale; the existing retrieval wall cases (tests/unit/retrieval, tests/acceptance/W2-138) pass unchanged"
non_goals:
- "no refresh hook installed by this ticket: installing the after-commit refresh is the operator's under ACT-WALLS (memory-audit), as EXAMIN's A9 records"
- no change to gov rebuild, the stores' format or the double-buffered store halves
- no change to the retrieval skill's text (a kernel path); a skill line, if wanted, comes back as a package
- no change to the guard, the path map or the hidden sets
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1197, DEC-1189, DEC-1090, DEC-342, DEC-1068, DEC-820, DEC-974, DAEO-2bdu, DAEO-rmhj, DAEO-l78m, DAEO-h4rh]
acceptance_tests: {path: tests/acceptance/W2-189/}
---
# W2-189 The store fresh after an adoption's last commit, or gov retrieve serving the last good store naming its commit

Filed 2026-11-16 by the CTO on the owner's word (DEC-1197 (2)(i), P-W2-81-VERDICT-1 (b)).

**Problem.** W2-81's full run on release 0.1.0 (P-W2-81-VERDICT-1 §1): in five of six adopted repositories `gov retrieve`
returned no evidence, because each store's commit was not HEAD. The adopters committed after A9's rebuild (the A10
record, verdicts, tickets); `gov retrieve` reads with `refresh=False`, so any tracked change since the build makes the
lexical facet stale (`src/gov/retrieval/lexical.py` `search`, `freshness`), the search stops `FACET_UNAVAILABLE`
(`retrieve.py` near line 727), and the runner scored a miss. python-app-clean, whose store commit equalled HEAD, scored
90. EXAMIN's copy has the same gap: its A9 records the after-commit refresh hook as the operator's (memory-audit,
ACT-WALLS), so no adopted repository refreshes its store after each commit today. W2-88 S11's practice is that "a
failed build leaves the last good store in service" and "every bundle names the commit its store was built at".

**Approach.** DEC-1197 (2)(i) names two routes: the store fresh after the adoption's last commit, or `gov retrieve`
serving the last good store naming its commit. Only the second meets S3 (a commit later in the repository's life with no
hook installed), so the KPI lines are written for it: answer from the last good store, leave out evidence from paths
changed since its commit, and name the commit, HEAD and the stale paths. A final rebuild at the adoption's end may be
added as well, but it is not enough alone. (The CTO's reading of the decision's "or"; listed for the owner's reading.)

**Interface.** `store_of(root)` (W2-138 S1) gains `head` (HEAD now) and `stale` (tracked paths changed between the
store's commit and HEAD, sorted); every result's `store` entry carries the three. The lexical and semantic facets, read
without refresh, answer from the store and leave out chunks of stale paths, rather than reporting the store unavailable
because tracked files moved. Missing, empty, unreadable and recipe-changed stores keep `FACET_UNAVAILABLE`.

**Rabbit holes.** Do not rebuild inside `gov retrieve`. Do not serve a stale path's old text. Do not compute `stale`
from anything but git's tracked files (no hidden-set path may appear in it).
