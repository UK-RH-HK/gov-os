---
type: probe
task: DAEO-qvff
round: 4
reviewer_session: d876120b-ee32-4c87-9cb3-9486a29d618c
implementer_session: "fa09841f-4475-4da2-b503-2625e317462f"
test_designer_session: cec26ffd-55cb-4165-bf92-9e576aeb61ab
test_designer_path_case_session: f88f227d-a7d3-4f51-b9b9-861e7a21472e
reviewer_wrote_nothing: true
reviewer_model: claude-opus-5-5
reviewer_effort: high
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 3137efe994335cae371ef779c78978f770f0a5f7
base_commit: d54654eab143ec306c6093a4e38216ac13318b38
decisions_applied: [DEC-1184, DEC-979, DEC-906, DEC-968, DEC-958, DEC-1157, DEC-1010, DEC-808]
---

# Probe record: W2-111 (DAEO-qvff), round 4: the reopen's guard costs (DEC-1184 (3)), the review of d54654eab..3137efe99

## The lead's judgement

- **What was checked.** The reopen's change, base d54654eab, probed commit 3137efe99:
  - the engineer's `src/gov/guard/install.py`, `src/gov/guard/reads.py` and `tests/unit/guard/test_w2_111_*`
    (7b5d62ed136a, 3d8311cf345f, 689e9706b2d3);
  - the test designer's `tests/acceptance/W2-111/**` (15c380fdc64a, merged at a90cd4bfe);
  - the CTO's path case, `tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py` (badfc8ee289a: one xfail mark made
    non-strict, DEC-1156 (7)).
  The merge of w2/integrate (2d55215d8) brings only others' records and was not under review. success-1 to success-4 and
  failure-1 to failure-3 were judged in the earlier round on the 15 revised cases (DEC-892). The reviewer found those
  files unchanged.
- **The reviewer.** A fresh independent auditor (claude-opus-5-5, effort high, read-only: Bash, Read, Grep and Glob).
  Round 1 of at most two (DEC-1010). The brief carried JUDGEMENT.md word for word and ended with the verdict block.
- **The verdict block, as returned:** all six lines pass. No finding is in scope, reachable in ordinary work, and fails
  open or loses work. READY by the block's rule.
- **Fails open, the review's first question.** The reviewer compared base and probed decisions directly. **0** decisions
  differed in each of these:
  - 796 calls × 4 roles;
  - 678 git-pathspec calls;
  - 70 run-clone decisions;
  - a fuzz of 14,000 paths of `_realpaths` against `os.path.realpath`;
  - a fuzz of 4,680 `has_install` calls across PATH forms.
  The engineer's own corpus (3,452 calls × 4 roles) also showed 0 differences.
- **Triage of each finding** (the lead, by DEC-1010's rule):

  | finding | line | what it is | outcome |
  |---|---|---|---|
  | F1 | success-5 | Its verify clause "before the change they fail" is not shown on the product hook by the CPU measure. | A package to the owner (P-W2-111-RED-BEFORE). Not a defect of the change. |
  | F2 | success-8 | Revision-colon-path reads (`git show HEAD:<path>`) still build every tree's part. Decisions are unchanged. | A Wave 3 row; it could ride the live-hook ACT's copy. |
  | F3 | success-7 | The PATH cache could go stale in a long-lived process. The product hook is one process per call. | A Wave 3 row. |
  | F4 | failure-4 | The engineer's corpus misses mutants M2 and M4. The unit tree cases catch both. | A Wave 3 row: add pathspec-above-hidden calls and a linked listing entry to the corpus. |
  | F5 | out of scope | Allows of hidden reads through loops and substitutions. They are the same at the base. | A Wave 3 hardening row. |

- **The lead's loaded runs.** The figures are p95 of the hook's own CPU time, less the reference hook's median, in ms. All
  runs used the CTO session's PATH: 46 entries, 27 of them under /mnt/c. The full figures are in the lead's return.
  - **Before the change, at load 20-24:** Bash plain and pipe were red, at 104-118 in all three rounds.
  - **Before the change, at load 3 and at 52:** all pass, with plain at 99.9 at load 52.
  - **After the change, at load 20-23:** all pass, at 59-94. The 151-tree Bash case passed on its second round (106.5, then
    93.8).
  - **After the change, at load 37-49:** all pass, at 52-93.
  - **The planted 150 ms hook:** it fails every new case at every load, at 180-304.

## The reviewer's return, verbatim

> **Sandbox check (Step 0):** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-qvff` failed with `Read-only file system` and no file was created. (b) `git hash-object -w --stdin` worked (it gave `1ae28402a`) and `git update-index --refresh` worked. HEAD is `3137efe994335cae371ef779c78978f770f0a5f7`. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-qvff`.
>
> **`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing. The sandbox's process namespace only shows my own processes.
>
> - **task:** DAEO-qvff (W2-111), independent review round 1 (brief rv-1), probed commit 3137efe99, base d54654eab.
> - **status:** done. Nothing blocks: no finding is in scope, reachable in ordinary work, and fails open or loses work. All six lines pass.
> - **work_completed:**
>   - Read the ticket and the whole diff.
>   - Compared base and probed decisions directly on planted repositories, using scratch copies under `$TMPDIR/rv1`.
>   - Fuzzed `_realpaths` and `has_install` against the base behaviour.
>   - Ran mutants to see whether the engineer's decision corpus would catch a fail-open.
>   - Ran the new timing and planted-hook cases on full copies of the base and the probed commit.
> - **files_changed:** none in the repository. `git status --porcelain` is empty. All scratch work is under `/tmp/gov-launch-zb5hdfhc/claude-1000/rv1/`.
> - **evidence:**
>   - **Planted repository:** I used the engineer's `plant()` layout: 155 trees, one nested, one through a link, one locked, one gone, a runs clone and a hidden part.
>   - **My own differential set:** 796 calls × 4 roles, through `policy_refusal` and `decide`. It covers a Read, Write or Edit of a hidden part in the first, last, nested, linked, locked, gone, own and clone trees. It covers searches from folders above the trees: `grep -r`, `find -exec cat`, `cat <parent>/*/…`, `for` loops, the Grep and Glob tools, `rg` and `tar`. It also covers paths through a symlink, `..`, `//` and `/./`, a `cd` the guard can follow, and `cd $X`, `$(…)`, `cd -` and `pushd` that it cannot. Base and probed differ on **0** calls; 1520 refusals are the same.
>   - **Git pathspecs:** 678 calls of `log -p`, `show`, `diff` and `format-patch` with pathspecs at, above or inside the hidden folder, from six trees, with and without `-C`. **0** differ.
>   - **Run clone:** a session in a run clone with the marker that `_clone_trees` reads gave 70 decisions, **0** differ, 56 of them refusals.
>   - **Engineer's corpus:** it passes on the base source (so its expected answers really are the base's) and on the probed source.
>   - **`_realpaths` vs `os.path.realpath`:** 14,000 paths over 400 random link layouts (links in a shared parent, relative, dangling and looping links, `..`, relative entries, trailing `/`, a leading `//`). **0** differ. Its cache lives only inside one call, so a path that changes between calls is resolved again.
>   - **`has_install` base vs probed, in one process:** 4,680 calls covering `-o`, `-o<t>`, `--output`, `--output=`, `-O`, `--output-document=`, `-P`, `--directory-prefix=`, `~`, relative targets and `$HOME`. PATH was empty, unset, relative, duplicated, held empty entries, linked, or changed between calls in shuffled order. **0** differ, and 806 of the answers were installs.
>   - **Timing (my runs are informational, not a load verdict).** Figures are the hook's CPU time less the reference hook's; my sandbox's PATH has 5 entries.
>
>     | Case | Base (load 39–51) | Probed (load 30–42) |
>     |---|---|---|
>     | Bash plain | 87.9 | 121.3, 110.0, 99.2 (passed on round 3) |
>     | Bash pipe | 95.9 | 56.5 |
>     | Bash redirect | 94.0 | 61.4 |
>     | 150-tree Read | **101.5, 104.2, 102.1 (red)** | 51.5 |
>     | 150-tree Write | passed | 33.1 |
>     | 150-tree Bash | **112.6, 112.3, 144.8 (red)** | 59.5 |
>     | Planted 150 ms hook, all six cases | 253–304 | 198.6–280.2 |
>
>     The planted 150 ms hook fails each of the six cases in both runs.
> - **tests:**
>   - Probed full copy, `tests/acceptance/W2-111` plus `tests/unit/guard/test_w2_111_install.py` and `test_w2_111_trees.py`: 78 passed. The corpus test ran separately and passed.
>   - Base copy, the timing and planted-hook files only: 2 failed (150-tree Read and Bash), 10 passed.
>   - On mutant M2: `tests/unit/guard` plus `tests/acceptance/W2-84` plus the W2-111 hidden-part file, with `-m "not local_only" -k "not real and not green_here and not time_limit"`. The `-k` exclusion left out the real-model, green_here and time_limit cases; those are for the CTO's runs outside the sandbox.
> - **discoveries:**
>   1. **`_TreePart` is a pure lazy delegate.** It makes the same decisions as `_Part`, and its errors arise at the same time: `_Part`'s constructor doesn't walk the filesystem, and `files` was already lazy at the base.
>   2. **The rule suites alone do not cover a pathspec above the hidden folder.** Mutant M2 makes `under()` always return false, which turns 354 refusals of `git log -p -- eval` into allows. The 950 rule-suite and W2-84 cases still pass on M2. The engineer's lazy-vs-eager unit case does catch it.
>   3. **The engineer's corpus catches mutants M1, M3 and M5 but misses M2 and M4.** The unit tree cases catch M2 and M4. In the corpus layout, git stores the "linked" tree t900 as its real path, so the listing's link handling is never exercised there.
>   4. **Pre-existing allows, identical at the base and not from this change:** `for f in <trees>/*; do cat $f/eval/bench/hidden/q1.txt; done`, `cat $(ls -d <trees>/t15*)/<hidden>`, and `cd <tree> && cd - && cat <hidden>`.
> - **risks:**
>   - Bash `[plain]` sits near the bound under load (99–121 ms on probed at load ~40). It may change verdict at the nightly's load of ~50. The lead's loaded runs decide this.
>   - The PATH cache keeps one value per process. If a PATH folder's link is retargeted while PATH stays the same, the answer is stale. I reproduced this in one long-lived process. The product hook (`template/governance/kernel/hooks/pretooluse.py`) runs as a fresh process per call, so the product cannot hit it.
> - **lessons:** a differential corpus should be checked against mutants before it is trusted to catch a fail-open. Here a fixture whose path git resolves on its own left the listing's link handling unexercised.
> - **proposed_decisions:** success-5's "before the change they fail" should go to the owner as a package. Options: drop that clause; re-baseline it to the many-tree cost (failing at the base is shown at load); or defer it to the live-hook ACT's rehearsal, where the wall time and the 9p wait on /mnt/c are measured.
> - **unresolved:** the success-5 package above. The loaded runs (quiet, ~20, ≥50) are the lead's.
> - **recommended_next_action:** the close computes READY from the verdict block. The lead runs the loaded timing, sends success-5's verify clause to the owner as a package, and logs rows F2–F5 for the Wave 3 hardening list.
>
> **Refusals during the review:**
> - The live hook refused one of my Bash analysis commands as a secret read. The command text named the planted file `a.key.txt`. I did not respell it; I dropped that filter and ran a different check.
> - Two `Monitor` wait attempts were refused: one because of a variable in the command, one because the grep path was outside the working directory. I stopped using Monitor and waited with Bash instead.
>
> ## Findings
>
> **F1, success-5: "before the change they fail" does not hold for the Bash cases.**
> - At the base, in my run, Bash plain, pipe and redirect gave 87.9, 95.9 and 94.0 ms at load 39–45: they pass.
> - The test designer's README records the same at the base: plain 175.8 → 67.0 ms across runs, pipe and redirect green.
> - This agrees with the lead's figures (56–64 ms at load 3 with the 46-entry PATH).
> - The 103–167 ms behind the clause was wall time. It included the live hook's own code and the 9p wait on /mnt/c, which the CPU measure leaves out.
> - On the probed commit the cases pass at the bound (plain only on round 3 at load ~40), and the planted 150 ms hook fails each of them.
> - So this is a verify clause the facts contradict, not a defect of the change. The line's statement (a Bash call decided within 100 ms of the hook's own work) holds.
> - Ordinary work: yes, because every run of these cases on the base passes and so cannot show the change's effect.
> - Consequence: other (a test-validity gap; no decision changes).
> - Scope: in. It goes to the owner as a package; it does not block.
> - What would reverse it: a base run with the product hook where the three Bash cases fail by the CPU measure at a quiet load.
>
> **F2, success-8: some calls still build every tree's part.**
> - At probed `src/gov/guard/reads.py:1826,1847,1979`, a revision-colon-path read checks `h.match(rel)` against every hidden part. `git show HEAD:README.md` builds all 158 trees' parts, where the call's only target lies in one tree.
> - Plain Read, Bash, `git log -p -- src` and `git grep` build one tree's part.
> - The decisions are unchanged; only the "judged only against its targets' trees" property is weaker for this form.
> - Ordinary work: yes, because `git show <rev>:<path>` is a common call.
> - Consequence: other (speed only).
> - Scope: in. A row.
> - What would reverse it: a count showing that this call builds only one tree's part.
>
> **F3, success-7: the PATH cache only lives as long as the hook process.**
> - At `install.py:146-162`, the cache is per process, keyed by the PATH value. The product hook is a fresh process for each call, so "once per session" holds within one call. The real saving comes from resolving PATH only for an absolute download target; a call with no download reads no PATH at all.
> - In a long-lived process, retargeting a PATH folder's link while PATH stays the same gives a stale answer. I saw base False and probed True, and the reverse direction is possible.
> - Ordinary work: no, because nothing in the product holds the cache across calls.
> - Consequence: other.
> - Scope: in. A row.
> - What would reverse it: a long-lived product process that calls `has_install`.
>
> **F4, failure-4: the engineer's corpus would not catch a broken `under()` or a broken `_realpaths`.**
> - Mutant M2 (`under()` always false) and mutant M4 (`_realpaths` returns paths unresolved) both pass the corpus.
> - `test_w2_111_trees.py` (the lazy-vs-eager case and the listing-resolution case) catches both.
> - The rule suites miss M2: they have no case for `git log -p -- <folder above the hidden part>`.
> - Ordinary work: no, because this is a test-strength gap, not a behaviour.
> - Consequence: other.
> - Scope: in. A row: add pathspec-above-hidden calls and a listing entry that is really a link to the corpus.
> - What would reverse it: the corpus failing on M2 or M4.
>
> **F5 (out of scope): pre-existing allows of hidden reads.**
> - `for f in <trees>/*; do cat $f/<hidden>; done`, `cat $(ls -d …)/<hidden>` and `cd <tree> && cd - && cat <hidden>` are allowed at the base and at the probed commit alike.
> - Ordinary work: no, because an honest agent does not aim loops at a hidden folder.
> - Consequence: fails open.
> - Scope: out (the five rules' own decisions; the change doesn't touch them). A Wave 3 row.
>
> ## Verdicts per line
> - **success-5: pass.** The Bash calls pass at the bound on the probed commit and the planted hook fails them. "Before the change they fail" is a verify clause the facts contradict (F1), so it goes to the owner as a package, not as a fail.
> - **success-6: pass.** With 151 trees, probed Read, Write and Bash gave 51.5, 33.1 and 59.5 ms, against base Read 101.5 and Bash 112.6 ms (red) at load. The 150-tree check is asserted in the case.
> - **success-7: pass.** The PATH-count unit cases pass, the install fuzz shows 0 differences, and a changed PATH is read again. F3 is a row.
> - **success-8: pass.** No decision changes across the corpus, my 1,544 calls × 4 roles, the clone and the fuzzes, and the per-tree judge runs only for target trees except for colon-path reads (F2). The 15 earlier case files are unchanged, and no skip, xfail or flaky mark was added in W2-111's folder. The W2-42a change is the single non-strict mark the ticket allows, committed with `Role: independent-test-designer`.
> - **failure-4: pass.** No decision differs anywhere I probed. F4 (corpus strength) is a row.
> - **failure-5: pass.** The planted 150 ms CPU hook (a busy loop on `process_time`, not a sleep) gives 198–304 ms on all six new cases in both runs; none passes.
>
> ```verdict
> {"kpis": [{"kpi": "success-5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "success-8", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "failure-5", "verdict": "pass", "findings": []}]}
> ```
## The verdict block (the reviewer's, copied unchanged)

```verdict
{"kpis": [{"kpi": "success-5", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "success-6", "verdict": "pass", "findings": []}, {"kpi": "success-7", "verdict": "pass", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "success-8", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "out", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "failure-4", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "failure-5", "verdict": "pass", "findings": []}]}
```
