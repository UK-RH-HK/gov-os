# PAT B: findings (DEC-1087 (10), DEC-1089 (1)), 2026-11-07

Agent B, research role, task DAEO-sdxk. Worktree `/home/usain/gov-os-worktrees/PAT-b`, branch `test/pat-b`, based on
`bcea09060ebc` (W2-112's sources). While I worked, `w2/integrate` moved from `c00d525fd420` (the pool switched on) to
`84c4f92d9d05` (DEC-1089). My branch is three commits behind the first and four behind the second.

## 1. The searches

All searches used `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<q>" --json`. The outputs are in
`/tmp/gov-os-emg-pat-b/s<k>.json`.

| # | time | question | ok | rerank.by | both facets | top 3 evidence | store commit (my own check; the result has no field) |
|---|---|---|---|---|---|---|---|
| s1 | 14:57:40 | steps after re-pin window 4 is done | true | service | yes | DECISION_REGISTER.md 13611-13669 (DEC-1087); START-NEXT-SESSION.md 7-18; ACT-REPIN-W4.md 1-6 | link -> `W2-00-store-a` = `c00d525fd420` |
| s2 | 14:58:15 | owner decision keystone 7 and usage pings | true | service | yes | DECISION_REGISTER.md 11388-11391 (DEC-936); 9889-9907 (DEC-888); WAVE_2_REVISED_PLAN.md 311-323 | a (`c00d525fd420`) |
| s3 | 14:58:49 | keystone 7 remainder of Wave 2 owner decided | true | service | yes | DECISION_REGISTER.md 7673-7681 (DEC-720); 7755-7768 (DEC-729); WAVE_2_REVISED_PLAN.md 311-323 | a |
| s4 | 14:59:00 | candidate pool settings in governance/project/retrieval.yaml | true | service | yes | src/gov/retrieval/pool.py 1-102; src/gov/retrieval/retrieve.py 12-35; .tickets/DAEO-0pyc.md 40-40 (also retrieval.yaml 1-14, 5th) | a |
| s5 | 14:59:36 | START-NEXT-SESSION steps after done: check the hook ..., then the parallel-agents test, then E0 | true | service | yes | START-NEXT-SESSION.md 88-133; ACT-REPIN-W4.md 128-138; DECISION_REGISTER.md 13648-13661 (DEC-1087) | a |
| s6 | 14:59:50 | usage pings | true | service | yes | DECISION_REGISTER.md 12186-12198 (DEC-972); P-PING-1.md 5-9; INVESTIGATION-1-COMBINED.md 137-137 | a (integrate already at `84c4f92d9d05` by 15:00:03; `W2-00-store-b` checked out at it, link still on a) |
| s7 | ~15:00:05 | DEC-1089 keystone 7 and usage pings | true | service | yes, plus a third facet `closure` (followed 12 records; `changed_by` shows DEC-1089) | DECISION_REGISTER.md 13703-13752 (DEC-1089); K7-W2-REMAINDER.md 1-4; K7-W2-REMAINDER.md 5-14 | answered from b (`84c4f92d9d05`): DEC-1089 is in the evidence; link -> b right after |
| s8 | 15:00:44 | s1's question with `--continue <s1's token>` (token minted on a) | **false** | - | - | `CONTINUATION_INVALID`: "the continuation's candidate pool is not this question's: the store or the pool settings changed since the earlier call" | b |

**What in a result names the commit:** nothing. The envelope has `ok`, `command`, `result`, `session`. `result` has
`stopping_reason`, `evidence`, `batches`, `merge`, `rerank`, `expansions`, `repeats`, `gaps`, `facets`, `budget`,
`continuation`, `routing` and `pool`. None of them holds a commit, a build time or a store half. Two clues are only
indirect:
- `result.pool.settings` echoes the store's `retrieval.yaml` (pool on), so the store is at `c00d525fd` or later.
- The evidence itself: s7 shows DEC-1089, so the store holds `84c4f92d9` or later.

I learnt the actual commit only outside gov: `readlink -f` on the link, then `git -C <half> rev-parse HEAD`.

## 2. The answers (cited as the lines stand in my worktree)

### Q1. The steps after re-pin window 4 is done, in order

The store gives the full list in six steps; my tree has only the outline in DEC-1087.
`governance/project/orchestration/START-NEXT-SESSION.md` §4 in the store (88-133, from s5; at `c00d525fd`) lists six
steps:
1. End the hold.
2. Switch the pool on.
3. Check the hook refreshed the store, with the speed check.
4. Run the parallel-agents and memory test, with W2-112's live measure.
5. Then the experiments: E0/E0b, E1 and the pilot's cost, then E2 to E5, the owner's decisions and the fresh 80.
6. Beside the experiments: W2-136.

The store quotes it as:
> `## 4. The steps after "done", in order` / `1. **End the hold:** ...` / `2. **Switch the pool on** (W2-32 S11; DEC-1086 A)` / `3. **Check the hook refreshed the store:**` / `4. **The parallel-agents and memory test, before any experiment (DEC-1087 (10)).**` / `5. **Then the experiments (DEC-1087 (11)):**` / `6. **Beside the experiments (CPU): W2-136**`

None of this is in my tree. My START-NEXT-SESSION.md is the older (2026-11-06, 812bc5ce) version. Line 88 is in §3c,
and line 98 is `## 4. Live and running now`. `packages/ACT-REPIN-W4.md` (whose "After it", 128-138, gives the short
form: end the hold, the pool on, the parallel-agents test, then E0 and E0b) does not exist in my tree.

The outline that **is** in my tree, `docs/DECISION_REGISTER.md` DEC-1087:
- 13647: `  - **After the re-pin:**`
- 13648: `    - (10) **The first test, before any experiment: parallel agents and memory.** Explained, then tested:`
- 13656-13657: `Tested with two agents in two worktrees searching while a merge refreshes the store. Any gap is reported before the experiments start.`
- 13658: `    - (11) **Then the experiments,** in the CTO's order with its improvements: E0 and E0b, E1, the owner's cap, E2, E3,`
- 13661: `    - (12) **M3's adoption** is decided only after all the experiments, ...`

DEC-1089 (1) (store only, 13703-13752) then gave the go for §4: "end the hold; switch the pool on; check the store and
its speed against the old pin; then the parallel-agents and memory test ... **The test's result goes to the owner before E0.**"

### Q2. What the owner decided about keystone 7 and usage pings

The answer is DEC-1089, landed on integrate at `84c4f92d9` at about 15:00, while I worked. It is **absent in my tree**:
my register ends at DEC-1088 (13670). In the store, `docs/DECISION_REGISTER.md` 13703-13752 says:
- (2) "**K7 is done for Wave 2.** The pin ladder stays by hand until Wave 3; W2-17 (`gov update`) and W2-18 (the pinned
  install) stay in Wave 3. Two items stay in Wave 2 ...". They are:
  - (a) "the first numbered, frozen release, cut and hash-checked, for EXAMIN's copy (DEC-954 Q8c; the cut is the
    owner's, DEC-772)";
  - (b) "exit criterion 7's paperwork for CAP-45.a (a CIT-P note moving it to Wave 3, or a named exception)".

  Both go in W2-27 (`DAEO-h4rh`). The package is `governance/project/orchestration/packages/K7-W2-REMAINDER.md`,
  which is also absent in my tree.
- (3) "**Usage, standing:** no ping and no alarm about usage at all; the owner manages the plan's limits. The CTO records
  only: the usage readings (`tools/usage_log.sh`, to `log/usage.txt`) and each experiment's tokens and cost
  (`log/spend.jsonl`), shown in the digests." It changes DEC-942 item 6 ("the usage pings end; the readings are
  recorded only").

Before the store refreshed (s2, s3 and s6, all on `c00d525fd`), no search found this decision. s2 and s6 returned older
ping rules (DEC-855, DEC-936, DEC-972, DEC-1021, DEC-1050 (9)). s2 and s3 returned keystone 7 only as the plan's §4.7
"releases and the pin ladder" (WAVE_2_REVISED_PLAN.md 311-323). An agent that stopped there would have answered "no
decision" or given an old rule.

### Q3. The candidate-pool settings `governance/project/retrieval.yaml` switches on

There are five, from the store (`c00d525fd` and later), `governance/project/retrieval.yaml` 7-14 (s4, item 5):
```
# W2-32 S11, the candidate pool (DEC-1075, DEC-1086 A), switched on after re-pin window 4 (DEC-1087 (8)); the older
# pins refuse this key.
pool:
  meaning_uncut: true
  route_depth: 60
  rerank_depth: 40
  per_file_first10: 2
  drop_nested: true
```
In **my tree**, `retrieval.yaml` has only lines 1-6 (`routing:` with `code_first: 2`, `named_first: 2`,
`phrasings: true`) and no `pool:` key. In my tree the pool is off. What each setting means is in my tree,
`src/gov/retrieval/pool.py` 5-10. I quote it because it agrees with the store:
- 6: `meaning_uncut: true     # the meaning route's phrasings fused and not cut back to its depth`
- 7: `route_depth: 60         # the keyword and meaning routes' depth (lexical.TOP_K, semantic.TOP_K: 30)`
- 8: `rerank_depth: 40        # the first 40 fused candidates reranked once; the pages cut from that one order`
- 9: `per_file_first10: 2     # at most 2 chunks of one file in the first 10 of the final order, the rest after`
- 10: `drop_nested: true       # an item whose lines lie inside an earlier item's of the same file left out`

Every search's `result.pool.settings` showed the same five values, so the store has them on.

## 3. Each cited evidence item, checked in my worktree

| evidence (store) | in my tree |
|---|---|
| START-NEXT-SESSION.md 88-133 (§4 steps after done; s5) and 88-107 (s1) | **absent in my tree**: my 88-133 are §3c's tail, §4 "Live and running now" and §5 "Next, in order (DEC-1079)". The same line numbers hold other content |
| START-NEXT-SESSION.md 7-18 ("## 0. First: has the owner's operator run re-pin window 4?"; s1) | **absent in my tree**: my line 7 is `## 1. The emergency: in force`. Different content at the same lines |
| ACT-REPIN-W4.md 1-6, 7-27, 49-65, 128-138 | **absent in my tree** (the file does not exist; added in `71b1f9b77`) |
| DECISION_REGISTER.md 13611-13669 (DEC-1087; s1), 13648-13661 (s5) | **same** (the register only grew past 13669 after my base) |
| DECISION_REGISTER.md 13703-13752 (DEC-1089; s7) | **absent in my tree** (my register ends with DEC-1088 at 13670) |
| K7-W2-REMAINDER.md 1-4, 5-14 | **absent in my tree** (the file does not exist) |
| retrieval.yaml 1-14 (s4) | **lines 1-6 same; 7-14 absent in my tree** |
| src/gov/retrieval/pool.py 1-102 (s4) | **same** (unchanged between `bcea09060` and `84c4f92d9`) |

## 4. What I saw that matters for the test

1. **There is no commit in a result.** A worker behind integrate cannot tell from gov's output which commit answered.
   It has to run `readlink` and `git rev-parse` on the store itself. DEC-1089 (1) names this gap; it is still open.
2. **Line numbers mislead a worker whose branch is behind.** START-NEXT-SESSION.md 7-18 and 88-133 exist in my tree
   but hold different text. A worker that opened "line 88" in its own tree would read §3c or §4 "Live and running
   now", not the steps after done. A worker that searched and did not open its own file would act on text its branch
   does not have, such as the pool on in `retrieval.yaml` or DEC-1089.
3. **The refresh during work went cleanly for plain searches.** s6 ran on half a while half b was being prepared, and s7
   ran on half b. Neither failed, and each answered from one whole half. The hook fired on the CTO's commit; I did
   nothing to cause it. Half b was at the new head by 15:00:03, and the link flipped by about 15:00:10.
4. **A continuation after the switch is refused.** s8 returned `ok: false`, `CONTINUATION_INVALID`, with a clear
   message. It did not page the other half silently, so W2-116's R2-F3 now fails closed. The message does not say which
   store or commit the token came from.
5. **Overlapping slices of one decision still come back.** `drop_nested` is on, yet s5 returned four overlapping DEC-1087
   slices: 13648-13661, 13611-13617, 13616-13627 and 13638-13649. s1 returned DEC-1037 twice (12874-12876 and
   12876-12877, overlapping at 12876). `drop_nested` drops only slices wholly inside an earlier item. In s1, the
   `pool.nested` list shows 13611-13617 and 13616-13627 dropped under the expanded 13611-13669, but slices that only
   overlap stay. DEC-1089 (1) asks this question.
6. **A `closure` facet appeared only once.** It came in s7, the question that named DEC-1089, and was absent elsewhere.
   It is reported beside lexical and semantic. "Both facets available" stays true, but the set of facets differs
   between searches.
