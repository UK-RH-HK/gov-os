# PLAN-10-LEADS — every ready ticket, up to the machine's capacity (the owner, 2026-11-01 ~15:25)

## Capacity now
Gate OPEN with 3 leads (W2-92, W2-13, W2-81), load 18.3 / 16.6 of 20, memory have 20.0 GB against need 13.2 GB
(floor 3 GiB + each running lead at what it uses, at least 2.1 GB, + the newcomer). Each more lead needs about 2.1 to
2.7 GB, so **about 3 more start at once now; 10 running is beyond the 23 GB machine today.** The chain waits on the
gate and starts each next lead as room opens (W2-13 returning frees one). Load near 20 also holds launches (the gate
needs min(load1, load15) below 20).

## Start now (chain `log/chain-2026-11-01-ten.txt`, in this order)
| # | Ticket | Kind | Brief | Before the chain (the CTO) |
|---|---|---|---|---|
| 1 | W2-105 `DAEO-zpdj` | resume, verification only (product-spec) | `briefs/W2-105-A5-resume-ten.md` | merge `w2/integrate` into its worktree (W1-38 may conflict with W2-106's revision: a test designer resolves, never the CTO); fill `@@HEAD@@` |
| 2 | W2-90b `DAEO-nqa2` | run 1 (test designer, LITE): KPIs 2 to 5, case by case | `briefs/W2-90b-A5-run1-ten.md` | file the split: W2-90b's ticket drops `DAEO-zpdj` from deps and KPI 1 moves to new W2-90c (after W2-105, W2-110, W2-90b); claim, worktree, fill `@@HEAD@@` |
| 3 | W2-91 `DAEO-a3u2` | run 1 (engineer, STANDARD), memory chain | `briefs/W2-91-A5-run1-ten.md` | DEC-996 (A): its record path `docs/research/W2-91-memory-measure.md` -> `docs/changes/W2-91-evidence.md` in the ticket; claim, worktree, `@@HEAD@@` (2 places) |
| 4 | W2-04 `DAEO-u4oz` | run 1 (engineer, FULL), memory chain (W2-15a waits for it) | `briefs/W2-04-A5-run1-ten.md` | claim, worktree, `@@HEAD@@` |
| 5 | W2-61h `DAEO-h2k3` | run 1, the 28-question set (memory chain: W2-15a and the 48-question measure wait for it) | `briefs/W2-61h-A5-run1-ten.md` | DEC-996 (B): its role and assignee independent-auditor -> independent-test-designer in the ticket; claim, worktree, `@@HEAD@@` (2 places). The launcher denies a test designer only `.tickets` and `.claude`, and does not bind it to its ticket's role, so `gov launch independent-test-designer` can write `fixtures/evaluation/**` today |
| 6 | W2-104 `DAEO-drhj` | run 1 (engineer, STANDARD): the skilleval harness (W2-98 to W2-103 wait for it) | `briefs/W2-104-A5-run1-ten.md` | claim, worktree, `@@HEAD@@` |

## Start when W2-11 has landed (chain `log/chain-2026-11-01-ten-b.txt`)
| # | Ticket | Kind | Brief | Before the chain |
|---|---|---|---|---|
| 7 | W2-33 `DAEO-lrre` | run 1 (product-spec), roles | `briefs/W2-33-A5-run1-ten.md` (DEC-994 and DEC-996 header on the earlier brief) | DEC-996's KPI edits (`ROLESPEC-DEC995-review.md`, W2-33: replace success line 28 and failure line 36); paths gain `.rulesync/subagents/**`, `template/.rulesync/subagents/**`, `governance/project/roster.yaml`; W2-113's role-file sentences (S2) move here and W2-113 drops its two role-file paths; claim, worktree, `@@HEAD@@` (3 places) |
| 8 | W2-120 `DAEO-i89t` | run 1 (engineer), W2-11's validator child | `briefs/W2-120-A5-run1-ten.md` | its dependency W2-11 closed by the queue; claim, worktree, `@@HEAD@@` |
| 9 | W2-60a `DAEO-cv58` | round 4 (FULL): P-W2-11-1 (`metadata.version`) and DEC-996's skills-only-listed and permission-field refusal | `briefs/W2-60a-A5-round4-ten.md` | declare round 4 (its round 3 was "the last" under DEC-951 item 4; DEC-992 and the owner's DEC-996 add this work); DEC-996's KPI edits (`ROLESPEC-DEC995-review.md`, W2-60a: replace success line 32, append to failure line 41); merge `w2/integrate` in; fill `@@HEAD@@`. **Open: W2-56's merge-back (DEC-786)**: W2-56 (in progress, no lead) shares `launcher.py`; settle the order before W2-60a merges |

With W2-92, W2-13 and W2-81 that is 12 leads queued; the gate keeps it near what the machine holds (about 6 now).

## Not now, with the reason
| Ticket | Reason |
|---|---|
| W2-115 smart close (FULL) | dependency: W2-55's close (today); **and** its KPIs 4 and 6 still find a batch's culprit by taking merges out, which DEC-988 forbids (attribution against the known baseline; culprits isolated before merge, as the queue does): revise those two lines first (a P2 within DEC-988/989), and its record path to `docs/changes/W2-115-evidence.md` (DEC-996 (A)) |
| W2-83a | role split pending: its engineer child (KPI 2's schema-map entry, `src/gov/check/schema.py`, `tests/unit/check/test_schema_playbook*`) filed first; dependency: W2-11 (landing) and W2-52 (in progress) hold the adopt skill; W2-52's clause moves here (DEC-996 item 2) |
| W2-60b | dependency: its `depends_on` lists W2-60a (in progress), and file overlap on `launcher.py` with W2-60a, W2-56, W2-82; also a missing dependency on W2-33 (sweep) |
| W2-82 | role split pending (its product-spec child, the template and `stacked_on` schema, goes first); file overlap: `launcher.py` (W2-60a), `src/gov/tasks/**` (W2-34) |
| W2-88 | dependency: W2-52 and W2-81 (in progress); role split pending (two children: product-spec for the adopt skill and its CIT-P, research for the GitHub-clone proofs) |
| W2-109 | role split pending (engineer child: the contract-forms check in `validate_w2.py`); ordering: alongside work, after the memory chain and the roles; its run 1 has no return (a lost run) |
| W2-110 | no work left: merged-ready, its three reds wait for ACT 2 (P-W2-110-4 (a)); it cannot pass the queue until then (DEC-989) |
| W2-113, W2-119 | dependency: W2-110 (and W2-52 for W2-113) |
| W2-116, W2-118 | dependency: W2-60b and W2-33 (W2-118 also W2-27: after EXAMIN's copy) |
| W2-117 | dependency: W2-115, W2-20, W2-27 (after EXAMIN's copy) |
| W2-15a, W2-32, W2-112 | dependency: W2-15a needs W2-04, W2-13 and W2-61h; W2-32 needs W2-15a; W2-112 needs W2-32 |
| W2-98 to W2-103 | dependency: W2-104 (and W2-11) |
| W2-93 | dependency: W2-81 |
| W2-94 (EXAMIN's question set) | ordering: EXAMIN's set is after the 48-question measure (DEC-957); the same DEC-996 (B) role change when it starts |
| W2-56 | in progress, no lead: its K6 work is held behind W2-60a's merge-back order (DEC-786); start it with W2-60a's order settled |
| W2-20, W2-37 | built and held (W2-20 DONE, held; W2-37's last review failed on A and B, a P1 for the owner already); not a lead start |
| W2-52 | in progress, PACKAGES: its one remaining file is a `.claude/` copy (the CTO's step with approval) and DEC-996 moves its adopt-skill clause to W2-83a |
| W2-09, W2-12, W2-17, W2-18, W2-19, W2-23, W2-31, W2-34 | ordering rule: not in DEC-979's order (memory chain, roles, alongside W2-81, W2-88, W2-96) nor DEC-983's before-EXAMIN list; DEC-946 "nothing else starts". File overlaps if started: W2-19 with W2-115 and W2-12 (`src/gov/close/**`), W2-17 with W2-23 (`src/gov/adapters/**`), W2-34 with W2-82 (`src/gov/tasks/**`), W2-09 with W2-60b (`src/gov/guard/**`) |
| W2-35, W2-36, W2-38, W2-39, W2-40 to W2-47, W2-06, W2-08, W2-10, W2-21, W2-22 | dependencies open (W2-33/W2-34; W2-37, W2-41; W2-04; W2-21; W2-10; W2-08; W2-05/W2-06; W2-09; W2-20) |
| W2-24 to W2-30, W2-14, W2-27 | EXAMIN's copy and its chain: K9's entry criteria (DEC-954 Q1) |
| W2-78, W2-83b, W2-61h's siblings, the unnumbered repairs (pr0y, s1wp, cv6c, 2d6f, sg6x, 2upp) | W2-78 parked (DEC-954); W2-83b after W2-83a's form; repairs: no plan slot (DEC-946) |

## Splits to file before their parents start (from DEC-996's approved list and the sweep)
- **W2-90c** (now; the owner's split of 2026-11-01): KPI 1 of W2-90b ("W2-90's seven named reds ... pass on the head with W2-105 and W2-106 merged"), LITE, independent-test-designer, paths: W2-90b's W1-05, W1-46 and W2-59 test files that the seven name, and `tests/acceptance/W2-90c/**`; deps W2-105, W2-110, W2-90b.
- **W2-83a-c** (before W2-83a): engineer, LITE: KPI 2 (the playbook entry in SCHEMA_MAP) and KPI 3's `gov check` half; paths `src/gov/check/schema.py`, `tests/unit/check/test_schema_playbook*`; after W2-83a's schema exists.
- The rest at each parent's claim, as listed in `packages/P1-DEC995-APPLY.md`.

## Claims and worktrees the CTO makes first (in the main tree, before chain 1)
1. W2-90b's ticket edit (deps, KPI 1 out) and W2-90c's filing; W2-91's record path; W2-61h's role. One commit per ticket.
2. Claims (`tk start`) with the DoR line for W2-90b, W2-91, W2-04, W2-61h, W2-104; worktrees `git worktree add ~/gov-os-worktrees/<W2> -b w2/<W2> w2/integrate` for each; `git merge w2/integrate` into W2-105's worktree.
3. Fill `@@HEAD@@` in each brief with the worktree's 12-digit head; then `tools/lead_chain2.sh log/chain-2026-11-01-ten.txt`.
4. Commits on `w2/integrate` while W2-11's queue run is going make it re-test: do the claims after W2-11 lands, or accept one re-test.
