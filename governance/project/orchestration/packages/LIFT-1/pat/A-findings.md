# PAT agent A: findings (DEC-1087 (10), DEC-1089 (1)), 2026-11-07

- **Worktree:** `/home/usain/gov-os-worktrees/PAT-a`, branch `test/pat-a`, head `c00d525fd` throughout (never moved).
- **Integrate:** `c00d525fd` at the start; `84c4f92d9` (DEC-1089, K7, usage pings) landed between 14:58:43 and
  14:59:59, so from search 6 on my branch was **one commit behind** integrate.
- **Store:** `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<q>" --json`; outputs in
  `/tmp/gov-os-emg-pat-a/s<k>.json`. 8 calls (7 searches and 1 continuation).

## 1. The answers

### Q1. The steps after re-pin window 4 is done, in order

From `governance/project/orchestration/START-NEXT-SESSION.md` (my tree, lines 88-132; the store's evidence 88-107,
later 88-133, sha256 equal to my lines):

> 88 `## 4. The steps after "done", in order`
> 89 `1. **End the hold:** mv log/act-in-progress.txt log/act-in-progress.ended-<HHMM>-act-repin-w4.txt (never rm). End`
> 90-92 `log/cto-standby.txt the same way. Confirm the pin, the reranker (...) and the hook (.git/hooks/reference-transaction, executable).`
> 93 `2. **Switch the pool on** (W2-32 S11; DEC-1086 A). One commit to governance/project/retrieval.yaml, adding beside`
> 104 `3. **Check the hook refreshed the store:**` (105-109: a new line in `log/integration-store.log`; the store's HEAD
>   equals integrate's; both facets, `rerank.by` service; the speed check, pin against candidate; if the hook did not
>   fire, `gov rebuild --integration w2/integrate` by hand)
> 110 `4. **The parallel-agents and memory test, before any experiment (DEC-1087 (10)).** Explain, then test:`
> 123 `5. **Then the experiments (DEC-1087 (11)):**` (124-130: E0 and E0b; E1, the pilot's cost to the owner before E2;
>   E2 to E5; the fresh 80; E3-E5's design package approved first)
> 131 `6. **Beside the experiments (CPU): W2-136** (DAEO-p3ln, gov plan, DEC-1088): tests first, the engineer, one review.`

Corroborated by `docs/DECISION_REGISTER.md` DEC-1087 (my tree 13611-13669): line 13647 `- **After the re-pin:**`,
13648 `(10) **The first test, before any experiment: parallel agents and memory.**`, 13658 `(11) **Then the
experiments,**`; and by `packages/ACT-REPIN-W4.md` 128-138 ("ends its hold ...; switches the pool on ...; runs the
parallel-agents and memory test ...; then E0 and E0b"). The owner's go for exactly these steps is DEC-1089 (1) (store
only, see Q2).

### Q2. What the owner decided about keystone 7 and about usage pings

**On integrate (and in the store from 14:59:59): DEC-1089, absent in my tree.** The store's evidence
`docs/DECISION_REGISTER.md:13703-13752` (my tree's 13703 is the register's version table `| Version | Date | Change |`):

> `### DEC-1089 — After re-pin window 4: the go for the steps after it (...); K7 done for Wave 2, its two remaining items in W2-27; usage recorded only, never pinged (standing)`
> `- (2) **K7 is done for Wave 2.** The pin ladder stays by hand until Wave 3; W2-17 (gov update) and W2-18 (the pinned install) stay in Wave 3. Two items stay in Wave 2, ...`
> `(a) the first numbered, frozen release, cut and hash-checked, for EXAMIN's copy (DEC-954 Q8c; the cut is the owner's, DEC-772);`
> `(b) exit criterion 7's paperwork for CAP-45.a (a CIT-P note moving it to Wave 3, or a named exception).`
> `- (3) **Usage, standing:** no ping and no alarm about usage at all; the owner manages the plan's limits. The CTO records only: the usage readings (tools/usage_log.sh, to log/usage.txt) and each experiment's tokens and cost (log/spend.jsonl), shown in the digests.`
> `**Changes:** DEC-942 item 6 (the usage pings end; the readings are recorded only); DEC-941 item 3 (K7's Wave 2 part)`

Home of (2): W2-27 (`DAEO-h4rh`), per `packages/K7-W2-REMAINDER.md:5-14` (absent in my tree).

**What my own tree says (behind by one commit):** the newest K7 ruling is DEC-941 item 3,
`docs/DECISION_REGISTER.md:11524-11525`:

> `3. **The deferrals of unbuilt work are accepted:** K5's W2-12, the rest of K7 after W2-16, and most of K8 go to Wave 3;`
> `- **One condition:** a release path (K7) is an entry criterion for EXAMIN's real repository, not for its copy.`

and `docs/plan/WAVE_2_REVISED_PLAN.md:311-322` (§4.7 Keystone 7: W2-16, W2-18, W2-17, the ladder). My tree has no
"usage ping" decision at all (grep of the register and the orchestration folder: none); the register's last row says
`Next free id: DEC-1089.` (13727). Searches 2-4, made before the refresh, returned only older ping decisions
(DEC-855, DEC-972, DEC-1021, DEC-1050 (9)), none about usage.

### Q3. The candidate-pool settings `governance/project/retrieval.yaml` switches on

My tree, lines 7-14 (store's evidence 1-14, same):

> 7 `# W2-32 S11, the candidate pool (DEC-1075, DEC-1086 A), switched on after re-pin window 4 (DEC-1087 (8)); the older`
> 9 `pool:`
> 10 `  meaning_uncut: true`
> 11 `  route_depth: 60`
> 12 `  rerank_depth: 40`
> 13 `  per_file_first10: 2`
> 14 `  drop_nested: true`

Meanings, `src/gov/retrieval/pool.py:6-10` (same): the meaning route's phrasings fused and not cut back; keyword and
meaning routes searched 60 deep (default 30); the first 40 fused candidates reranked once; at most 2 chunks of one file
in the first 10; an item nested inside an earlier item of the same file left out. Every bundle's `pool.settings`
echoed these five values live.

## 2. The searches

| # | time | question | ok | rerank.by | both facets | top 3 evidence | what tells the store's commit |
|---|---|---|---|---|---|---|---|
| s1 | 14:57:40 | steps after re-pin window 4 is done | true | service (cuda:0) | yes | DECISION_REGISTER.md 13611-13669 (DEC-1087); START-NEXT-SESSION.md 7-18; ACT-REPIN-W4.md 1-6 | no commit field; `pool.settings` present, so the store's `retrieval.yaml` is `c00d525fd`'s or later |
| s2 | 14:58:12 | owner decision keystone 7 | true | service | yes | DECISION_REGISTER.md 9121-9128 (DEC-836); 9107-9110 (DEC-834); .tickets/DAEO-mc6n.md 50-65 | none |
| s3 | 14:58:29 | owner decided usage pings | true | service | yes | DECISION_REGISTER.md 11388-11391 (DEC-936); 9288-9308 (DEC-855); prompts/w2-orchestrator.md 191-196 | none |
| s4 | 14:58:43 | DEC-1089 keystone 7 remainder usage pings | true | service | yes | DECISION_REGISTER.md 13721-13727 (labelled DEC-1088: the version table, last row "Next free id: DEC-1089"); WAVE_2_REVISED_PLAN.md 311-323; DECISION_REGISTER.md 11447-11456 (DEC-938) | only by content: the version table ends at 0.472, so the store was still at `c00d525fd` |
| s5 | 14:59:10 | candidate pool settings in governance/project/retrieval.yaml | true | service | yes | src/gov/retrieval/pool.py 1-102; src/gov/retrieval/retrieve.py 12-35; .tickets/DAEO-0pyc.md 40 | retrieval.yaml 1-14 carries the pool block (c00d525fd) |
| s6 | 14:59:59 | DEC-1089 keystone 7 done for Wave 2; usage recorded never pinged | true | service | yes (and closure) | DECISION_REGISTER.md 13703-13752 (DEC-1089); packages/K7-W2-REMAINDER.md 5-14; DECISIONS-IN-FORCE.md 259-262 | only by content: DEC-1089 present, so the store held `84c4f92d9` about a minute after it landed; closure's `changed_by` lists DEC-1089 on DEC-941, DEC-942 |
| s7 | 15:00:40 | continuation of s1's token | **false** | – | – | `CONTINUATION_INVALID`: "the continuation's candidate pool is not this question's: the store or the pool settings changed since the earlier call" | the refusal itself says the store changed |
| s8 | 15:00:50 | s1 repeated | true | service | yes | DECISION_REGISTER.md 13703-13752 (DEC-1089); 13638-13649 (DEC-1087); START-NEXT-SESSION.md 7-18 | DEC-1089 present (84c4f92d9) |

The continuation token's pool part has an `h` field (16 hex), but `pool.py`'s `digest` shows it is a digest of the
candidates' chunk ids, not a commit.

## 3. Every cited evidence item, checked in my tree

Checked by hashing my tree's lines `start_line..end_line`: each item's `sha256` is the sha256 of exactly those file
lines (whole lines, even where the text shown is cut at 4,000 characters), so a match proves `same`.

| item (store) | verdict in my tree |
|---|---|
| START-NEXT-SESSION.md 88-107 (s1), 88-133 (s8) | same |
| START-NEXT-SESSION.md 7-18 | same |
| DECISION_REGISTER.md 13611-13669 (DEC-1087) | same |
| DECISION_REGISTER.md 13611-13617, 13616-13627, 13638-13649 (DEC-1087 slices, s8) | same |
| ACT-REPIN-W4.md 1-6, 7-27, 128-138 | same |
| DECISION_REGISTER.md 13721-13727 (s4, version table) | same (before the refresh); after it, the store's table is longer and starts at a later line |
| WAVE_2_REVISED_PLAN.md 311-323 | same |
| DECISION_REGISTER.md 9121-9128 (DEC-836), 9107-9110 (DEC-834) | same |
| governance/project/retrieval.yaml 1-14 | same |
| src/gov/retrieval/pool.py 1-102 | same |
| docs/changes/W2-32-evidence.md 34 | same (the shown text is cut at 4,000 characters; the hash is of the whole line) |
| **DECISION_REGISTER.md 13703-13752 (DEC-1089)** | **absent in my tree**: my 13703-13752 is the version table (0.450 to 0.472) |
| **packages/K7-W2-REMAINDER.md 1-4, 5-14, 53-58** | **absent in my tree** (no such file) |
| **DECISIONS-IN-FORCE.md 259-262** | **absent in my tree** (my file ends at 256) |
| **.tickets/DAEO-h4rh.md 87-109** | **shifted**: the store's 87 is a new KPI line `[DEC-1089]`; my 87 is `sources:` (2 lines and the DEC-1089 source added on integrate) |

## 4. What I saw that matters

1. **The result names no commit.** No field gives the store's HEAD; I could tell only from content (DEC-1089
   present or not; the version table's last row). DEC-1089 (1) names this gap ("the missing commit field in search
   results"); it is still there.
2. **It could mislead a worker behind integrate.** After 84c4f92d9, the top hit for Q2 (and for the repeated Q1) is
   `docs/DECISION_REGISTER.md:13703-13752`. A worker whose branch is at `c00d525fd` opening line 13703 finds the
   version table, not DEC-1089; one who trusts the line numbers cites a wrong place; one who trusts only its own tree
   misses the decision entirely (my tree has no usage-ping decision). Files the commit did not touch were all `same`.
3. **A worker can detect it:** each item's `sha256` equals the sha256 of its file lines, so hashing one's own lines
   at the range says `same` or not, with no commit field needed. Nothing tells the worker to do so.
4. **The refresh was fast:** the store answered from 84c4f92d9 at most about 76 s after it landed (s4 at 14:58:43 had
   the old state; s6 at 14:59:59 the new). No search failed during it; I did not catch a search mid-switch.
5. **A continuation after the switch is refused cleanly** (`CONTINUATION_INVALID`, with the cause), not paged
   silently from the other half.
6. **Overlapping slices of one decision still appear with `drop_nested` on:** s8 returned DEC-1087 three times
   (13611-13617, 13616-13627, 13638-13649: two overlapping, none nested); s1 returned DEC-1037 twice (12874-12876,
   12876-12877). `drop_nested` removes only items wholly inside an earlier one (s1's `pool.nested` listed two).
7. **A stale statement inside current evidence:** `docs/changes/W2-32-evidence.md:34` (s5, rank 7) says the pool is
   "Not switched on in this repository's `retrieval.yaml`", which was true at S11's merge but is false since
   `c00d525fd`; the true file (rank 5) is in the same bundle.
8. **The version table rides on the last decision:** s4's `13721-13727` is labelled `DEC-1088` (`in_force`) but is
   the register's change table; after the refresh the table is folded into DEC-1089's span (13703-13752).
