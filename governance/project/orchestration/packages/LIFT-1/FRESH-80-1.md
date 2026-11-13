# FRESH-80-1: the fresh 80, what to expect, every fix for an honest verdict, how it runs, and the K9 bar (DEC-1092 (4), DEC-1095 (3))

For the owner. Drafted 2026-11-07 by a product-spec agent for the CTO (session `ad44f5fe`), from the records named in §6. **Nothing here runs before the owner decides.** The figures below are counts from the 138 (tuning and diagnostic sets). No question, label or answer from a hidden or spent set is quoted, and the fresh 80 (`memory-verdict-2`) was not opened.

## 0. In short
- **The configuration to judge,** chosen from the 138: window 4's pin with the pool on, today's bundle (6,000 tokens), and "search again once". It was the best of every condition tried (E2, E3, E3-SA, E5); the glossary did not help (E2G). E4 is still running (its section below).
- **What to expect:** retrieval lower than on the 138 and end to end close to the hidden and spent sets. hit@5 is likely about 68 % (58 to 77). Right end to end with search again once is likely about 89 % (80 to 94).
- **The bar:** hit@5 at 85 % will almost certainly be missed. Right end to end at 85 %, with wrong claims at most 5 %, will likely pass, but not surely: about 7 chances in 10 with both limits.
- **Recommended:** judge K9 on right end to end, with wrong claims capped, and report hit@5 beside it. The reason has to be what the bar measures, not that it passes (§4).
- **Before the run:** 20 fixes and checks (§2), most of them minutes of work. Three matter most: whether the nonexistent id still exists nowhere, how anchors resolve at the measured commit, and a declared rule for a fault mid-run.
- **Cost of the judged run:** about $15 (brake $30), and about 45 minutes of live runs. The retrieval measure uses no model tokens.

## 1. What to expect on the fresh 80

### 1.1 The 138, per set (E0, E3, E2; counts only)
| figure | visible 40 | hidden 39 | spent 59 | **the 138** |
|---|---|---|---|---|
| hit@5 (E0) | 34 (85.0 %) | 32 (82.1 %) | 40 (67.8 %) | **106 (76.8 %)** |
| gold in the first bundle (E0) | 37 (92.5 %) | 36 (92.3 %) | 50 (84.7 %) | **123 (89.1 %)** |
| right end to end, one call, today's bundle (E3) | 37 (92.5 %) | 32 (82.1 %) | 45 (76.3 %) | **114 (82.6 %)** |
| right end to end, search again once (E2, A2) | 40 (100 %) | 35 (89.7 %) | 53 (89.8 %) | **128 (92.8 %)** |
| wrong claims at A2 (E2) | 0 | 3 | 0 | 3 (2.2 %) |

- E2's own one-search figure (A1) was 115. The difference of 1 from E3's 114 is the reader's run-to-run spread.
- With the citation set aside, the answer was correct for 135 of the 138 (97.8 %) at A2.
- **Of the 10 not right at A2:** 3 are wrong claims (all hidden). The other 7 are correct answers whose citation missed the gold's lines (6 spent, 1 hidden).

### 1.2 Why the spent 59 are the best guide
- **The same writer and checker** wrote the spent 60 and the fresh 80 (DEC-1076 (1)), blind, by the same rubric.
- **The spent set was used once, on 11-05,** and has been diagnostic since. No configuration was adopted on it: the grid's leaders wait for E4. Its hit@5 was 40 of 59 on 11-05, and it is still 40 of 59 at window 4 (DEC-1074 (1), E0).
- **The visible 40 are the tuning set,** and the hidden half was tuned too (the owner's reading in DEC-1074 (1)). Their higher figures are not a guide to a fresh set.
- **A useful sign:** at A2 the hidden and spent sets agree almost exactly (89.7 % and 89.8 %), although they differ by 14 points at hit@5. An agent that reads the whole bundle and searches once more absorbs most of the ranking gap. End to end is the most consistent figure across sets, which is DEC-1071 (3)'s test of a sound structure.

### 1.3 What pushes the 80 lower, and what pushes it higher
- **Lower:**
  - the writer varied its phrasing by role and never echoed a source's wording (DEC-1076 (2)), so vocabulary misses are likelier;
  - none of the 80's gold sources is a gold source of any earlier set (DEC-1078 (1)), so they sit in parts of the repository no tuning ever looked at;
  - two more days of records compete in the store (E0 lost 2 against S11's check for this reason).
- **Higher:**
  - the cross-check added the whole places that also state an answer (DEC-1078 (2)), so a bundle has more ways to hold the gold;
  - source families count official copies (DEC-1078 (4)).

### 1.4 The expectation
The judged figures count 79 of the 80: the one nonexistent-id question is counted apart (DEC-1078 (1)). On 79 questions, chance alone moves a figure by about 7 points either way (a 95 % interval).

| figure | expected on the fresh 80 | likely range | basis |
|---|---|---|---|
| hit@5 | about 68 % | 58 to 77 % | the spent 59 |
| gold in the first bundle | about 85 % | 76 to 91 % | the spent 59 |
| right end to end, one call | about 76 % | 66 to 85 % | the spent 59 |
| **right end to end, search again once (A2)** | **about 89 %** | **80 to 94 %** | the hidden and spent 98 (88 of 98) |
| wrong claims at A2 | 1 to 4 of 79 | 0 to 6 | the hidden and spent 98 (3 of 98) |

- **Not a promise.** The 80 may be harder than the spent set for the reasons in §1.3. A figure near the bottom of each range would not mean anything broke.
- **If E4's M3 is adopted,** the retrieval rows move up by whatever E4 shows end to end; the grid gave M3 +11 hit@5 on the 138, with about half expected on fresh questions (SEVEN-ANSWERS §1).

## 2. Every gap or fix needed for an honest verdict
Each item: what is wrong or missing, what to do, and its cost. "Pre-flight" means a counts-only script that opens the 80 in its own code and prints ids and counts, with no search and no model call. It does not use the set, because no figure of memory is seen.

**The set and its labels**
1. **The set unchanged since DEC-1078.** No digest of the 80 was recorded on 11-05 (only "80 files, both folders mode 700, 179 sources resolved").
   - *Do:* the pre-flight counts the files (80 expected), records one combined sha256 of the 80 in the declaration, and counts the files changed since DEC-1078's close (0 expected). The result record repeats the digest.
   - *Cost:* minutes.
2. **The labels at their own commit, re-anchored at the measured commit.** The measure re-anchors in memory and never writes the sets root (W2-134, DEC-1084). Reading its code (`gov/retrieval/measure.py`, the pin's copy) shows three cases it does not report:
   - a heading found **more than once** at the measured commit: the measure takes the first match, silently;
   - a heading **not found**, with lines stated and **no commit** named: the stated lines are used unchecked, silently;
   - a source whose file is gone, with no lines or commit: a fault that ends the run. This happens at load, before any search, so nothing is spent.

   Only "unresolved" is counted (a block found nowhere or more than once at its commit), and it is scored as not found.
   - *Do:* the pre-flight loads the 80 at the measured commit with the measure's own loader and counts the sources by how they anchor: heading found once; heading found more than once; heading missing and re-anchored by its commit; heading missing with lines unchecked; unresolved. DEC-1078 found all 179 heading-anchored on 11-05, so every count but the first should be 0.
   - *If any source is not "found once":* the writer and checker sessions fix only those entries at the measured commit, in one round, as the q12 sync was done for E0. They are named to them by question id and entry number, before any search. If an entry cannot be fixed, it stays as the measure scores it (not found), and the count is reported. A question is never dropped from the denominator once figures exist.
   - *Cost:* a small script, about 1 hour with its review. The owner's operator only if a fix is needed.
3. **Gold answers gone stale.** The 80 were written against 11-05's repository. Re-anchoring finds where a passage stands now, not whether the fact is still true. A plan line, a ticket's status or an amended decision may have changed by the measured commit, and a reader right about the repository would then be graded wrong. This error fails closed: it lowers the figure.
   - *Do (recommended):* the checker session re-reads the 80's gold answers against the measured commit and flags any fact that changed; the writer updates those, in one round. Only counts come back to the CTO.
   - *Cost:* about 1 to 2 hours of the owner's operator and the two sessions.
4. **The visible q12 sync does not apply.** The CTO synced the sets root's visible q12 once, for E0 (E0-DECLARATION). The 80 have their own labels, and nobody in the CTO's system edits them.
5. **Source families.** The sets root's path map declares no `evaluation_families` (read: only `evaluation_sets`), so the measure takes the measured clone's. At `c00d525f` that block holds contract, kernel and agents (checked with `git show`).
   - *Do:* the run's first line must read `families: contract (4 members), kernel (3 members), agents (2 members)`; anything else stops the run before its first search.
   - The 80 were written before the family rule. A family hit counts only where the item's text holds the gold span's text, and on the 138 the families moved no count.
6. **The nonexistent-id question.** There is 1 in the 80 (DEC-1078 (1)). It is counted apart, so the judged figures are on 79.
   - **A real risk:** the set was written on 11-05. DEC-1079 to DEC-1096 and W2-137 to W2-142 were created after it. If the writer's nonexistent id falls in a range that now exists, the gold "not found" is wrong at the measured commit.
     - *Do:* the pre-flight checks that the question's id-shaped tokens still exist nowhere in the clone (whole-token search) and prints only yes or no.
     - *If one now exists:* the question is dropped from every figure and the drop is reported. This is decided now, before any figure.
   - **The measure does not apply DEC-1071 (5) itself.** The pass is "the product stops with `UNRESOLVED_IDS` naming the id".
     - *Do:* the figures tool reads that from the kept output (the bundle's `stopping_reason` and `gaps`).
     - The product returns that stop as a bundle with no evidence, not as an error (`gov/retrieve/command.py`), so it should not end the measure. h24 and m60 went through E0 without a fault.
   - The figures tool finds the question by its category, and never prints which id it is.

**Who reads the 80, and grading**

7. **The readers and graders read the 80.** The owner approved this for the 138 (DEC-1086 C, DEC-1092 (3)). The 80 needs the same word (§5, Q5).
   - The reader run's folder holds the 80's questions, gold answers and answers. The 138's folders are under `~/gov-os-runs/D4B/`.
   - *Do:* put the 80's under the sets root (`~/gov-os-eval/runs/fresh-80/`), beside the kept outputs. Before the run, the CTO checks that the guard refuses a measured role a read there (ACT-GUARD-SETS-1).
   - *Cost:* minutes.
8. **Grader agreement.** As on the 138: `claude-opus-5-5`'s grade counts, and `claude-sonnet-5-5`'s agreement is reported (138 of 140 in E2, 690 of 700 in E3).
   - *Add,* as data only: the judged figure under the stricter of the two grades, per question.
   - No re-grading after the run.
   - In today's scripts a grader call that returns no grade turns an answer into a wrong claim (fails closed). It is counted and reported.
9. **A known understatement.** On the 138, 7 of the 10 misses at A2 were correct answers citing a place the label does not list. The judged figure stays strict (answer and citation). "Answer correct, citation aside" is reported beside it, and the rule does not change.

**Where and how it is measured**

10. **The commit.** Recommended: window 4, `c00d525f`, E0's clone, run **before the lift's re-pin**.
    - **Why:**
      - every figure that chose the configuration was measured there (E0 to E5), so the verdict judges that choice and not a moving target;
      - window 4 carries what DEC-1083 (2) names (W2-92, W2-32's S11, W2-131) with the 0.6B, the reranker in use;
      - it is the nearest commit to the set's writing, so fewer gold answers have gone stale (item 3);
      - W2-137 (the request cap) moved nothing beyond bfloat16 noise (G1-PROFILE), and W2-138 adds a field to results, not a rank.
    - **The other way:** the lift's re-pin. The live reranker service and `~/.local/bin/gov` change at the re-pin, so the 138 must be measured again there first: E0 (35 minutes, no tokens) and E2's A2 (about $22, 15 minutes). Then the 80. It waits for the lift, and two more days of drift reach the gold.
    - **If M3 is adopted after E4:** the 80 must wait for a pin that carries M3 (DEC-1083 (2): "the reranker chosen at the decision point"), est. 1 to 1.5 days of build (SEVEN-ANSWERS §1). The 138 is measured on that pin first, as above.
11. **The exact command.** The measure as E0 ran it (`drafts/d4b/e0_run.sh`), with `memory-verdict-2 --part hidden` in place of the 138's two runs:
    - the pin's python, the measure's default budgets (batch 10, bundle 6,000, stack 24,000), `GOV_ROLE=orchestrator`, the `GOV_KEEP` wrapper, E0's clone;
    - **a control first:** the visible 40 through the same command (a tuning set, so no harm). It must equal E0's 34 within 2, or the run stops. This proves that the pin, the clone, the store and the live servers are as they were in E0.
    - *Cost:* about 10 minutes of GPU, no tokens.
12. **The clone and store unchanged.** E0's clone was used since E0 by E0b's harness (the pool off inside the harness only), E5's live run and E2's and E3-SA's searches.
    - *Do:* check a clean tree (`git status`), HEAD at `c00d525f`, and the pool's lines in `retrieval.yaml`. The control (item 11) checks the rest.
13. **Nothing beside the live parts.** While the 80 is measured and the reader's later searches run, there is:
    - no store rebuild;
    - no commit on `w2/integrate` (its hook rebuilds the integration store, E3-SA's slip);
    - no GPU window (E4's scoring, G1's bursts).
    - *Cost:* about 45 minutes with commits held.

**One shot**

14. **The measure must not run twice.** Nothing in the measure stops a second run.
    - *Do:* the fresh-80 runner refuses to start if `~/gov-os-eval/runs/fresh-80/USED` exists, and writes it before its first search.
    - Each attempt gets its own kept folder. The wrapper resets its counter but leaves old files, so a restart into the same folder would mix outputs.
15. **A fault mid-run.** The rule is declared before the run (§3.5).
16. **The reader run must resume, never re-run.** `e2_run.py` has no resume.
    - *Do:* the fresh-80 copy skips every question that already has a row file. A finished question is never run again.
17. **A silent search failure.** `e2_run.py`'s `search()` returns an empty bundle on any failure, so a failed second search looks like "no gold".
    - *Do:* count the failures, and name them in the result if there are any.
18. **The citation check.** The matcher counts any cited range that overlaps the gold; it does not check that the range came from a bundle the reader received.
    - *Do:* count the citations outside every item the reader was given (0 expected) and report the count. The risk is small, since a reader cannot guess unseen lines.

**The tools and the hidden-half rule**

19. **The scripts are written for the 138.**
    - `e2_run.py` hard-codes the 138's sets, `APART = {h24, m60}` and E0's folders;
    - `e0_figures.py` reads two files and three sets.
    - *Do:* a fresh-80 copy of each, with a dry mode (load, count, no reader), the resume (item 16), the counts of items 17 and 18, the nonexistent-id question by category (item 6), and the run folder under the sets root (item 7). One review (READY), then the files pinned by hash, as E0b's harness was.
    - *Cost:* about 2 to 3 hours of agent work on the CPU.
20. **The hidden-half rule for the CTO.**
    - The tools open the 80 in their own code. Standard output carries ids and counts only, and the measure's own hidden-part lines are already ids, ranks and pass or fail.
    - The CTO never opens the run folder's rows, the kept outputs, or the measure's JSON beyond its counts.
    - The pairing of category and id is never printed.

**The brake.** The judged reader run is projected at $15 (§3.3), so its brake is $30 (DEC-1091 (2)). A data condition has its own projection and brake. The measure uses no model tokens.

## 3. How the fresh 80 runs

### 3.1 The conditions
**Judged (one only):** the configuration the owner chooses before the run. Recommended:
- window 4's pin, `pin-bcea09060ebc`, with the pool on, on E0's clone at `c00d525f`;
- today's bundle, 6,000 tokens, as the measure's first call returns it;
- E2's reader (`claude-opus-5-5`, effort high, no tools, no transcript, with the "may be incomplete" line);
- search again once: **A2**, the A3 run cut at two attempts, computed exactly as in E2, so the 80's figure compares with the 138's 128;
- graded by `claude-opus-5-5` (counts), checked by `claude-sonnet-5-5` (agreement);
- the citation by the measure's matcher (source families on);
- the figure: right end to end on the 79; wrong claims beside it.

**For data only, declared as such:**
- **E0's retrieval figures:** hit@5, hit@10, hit@20, MRR, in the bundle and full evidence, from the measure itself. No extra cost.
- **One call on today's bundle:** A1 of the same run. It is the same prompt as E3's one-call condition, so no separate run is needed. No extra cost.
- **A3:** from the same run. No extra cost.
- **Whichever E4 condition the owner does not choose:**
  - *if M3 is adopted,* the 0.6B's configuration is the data condition, at no extra cost, because the product runs it;
  - *if M3 is not adopted,* measuring M3 on the 80 needs a scoring window of its own over the 80's candidates, plus a reader run. Not recommended: the 80 could not adopt it anyway (§3.4).

**Not run on the 80 (recommended):**
- E3's top 5, 10, 20 and 40 unranked, each beaten on the 138 (Holm p at most 0.0023);
- E5's 12,000 tokens, which needs a second live retrieval of the 80 and bought nothing on the 138;
- E2G's glossary, which lowered the figure by 6.

If the owner wants every condition for data, the cost is in §3.3.

### 3.2 The order
1. **E4 finishes** and its section is filled in. The owner decides M3, the configuration, the commit and the bar (§5).
2. **The tools** (item 19) and the pre-flight script, one review. About 3 hours on the CPU.
3. **The checker's staleness pass** (item 3), if approved. About 1 to 2 hours of the owner's operator.
4. **The pre-flight,** counts only: items 1, 2, 5, 6 and 12. Any anchoring fix goes through the writer and checker.
5. **The declaration committed** (`FRESH-80-DECLARATION.md`). It holds everything §3.4 lists, the 80's digest and the pre-flight's counts.
6. **The hold begins** (item 13).
7. **The control** on the visible 40. About 10 minutes.
8. **The measure on the 80.** About 20 minutes (E0 took 19 for its 80), one GPU job with the backstop armed, no tokens. This gives the retrieval figures (data) and the first bundles.
9. **The judged reader run** on those first bundles, with later searches live on the same clone. About 10 minutes at four calls at once (E2 took 15 for 140). This gives A2 (judged), plus A1 and A3 (data).
10. **The hold ends.** Any data condition the owner chose runs now, so that its faults cannot touch the judged figure.
11. **The result record:** the verdict against the bar, then the data table, to the owner.

**Elapsed:** about half a day with the fixes; the live part is about 45 minutes.

### 3.3 Cost (from the 138's measured costs)
| part | basis | projection | brake |
|---|---|---|---|
| the control and the measure | E0: no model tokens | $0 | |
| **the judged reader run (A1, A2, A3 in one run)** | E2: $0.157 a question; more second searches likely on a fresher set | **about $13 to $15** | **$30** |
| optional: E3's other four bundles, one call | E3: $61.93 for 140 | about $35 | $70 |
| optional: E5's 12,000 tokens | E5: $29.50 for 140, plus a second live retrieval (20 minutes) | about $17 | $34 |
| optional: an E4 cell not adopted, one call | E3's bundle cost of $0.111 a question, plus a scoring window (GPU, est. 30 to 60 minutes) | about $9 | $18 |

**Recommended total:** about $15.

### 3.4 The rule: only the condition chosen beforehand is judged
1. **The declaration comes first.** It is committed before any search with the 80, and names in full:
   - the judged condition (pin, clone and commit, store, flags, bundle, reader and its prompt, attempts and the A2 cut, graders, rubric, citation rule);
   - the denominator (79, with the nonexistent-id question apart), the bar, and how it rounds (§4.3);
   - each data condition, labelled "data only, not judged";
   - the fault rule (§3.5).
2. **The verdict line is computed from the judged condition only,** against the declared bar. Nothing else enters it.
3. **Data figures go in a separate table** headed "data only, not judged".
4. **No figure on the 80 chooses anything.** If a data condition beats the judged one, it is recorded as a finding. It can be adopted only after a new fresh set, never on the 80 and never to pass K9.
5. **Nothing changes after the run:** not the rubric, the graders, the matcher, the labels, the denominator or the bar.
6. **Nothing is run again,** except as §3.5 allows.

### 3.5 A fault, declared before the run
- **Before the first search** (the pre-flight, a load fault, the control failing): the set has not been used. Fix the fault, then run.
- **During the measure** (a non-zero exit, the backstop tripping, a failed retrieval, the machine stopping):
  - the run stops, and its partial kept outputs and figures are kept and reported, never as the verdict;
  - one restart from the start follows at once, on the same commit, store and command, into a new kept folder, **whatever the partial figures show**. The restart's figures count;
  - a second fault stops everything and goes to the owner.
  - **Why a restart is fair:** the configuration is fixed and the CTO sees no question, so a restart cannot tune anything. The risk is choosing the better of two runs, and taking the restart whatever it shows, decided now, removes it.
- **During the reader run:**
  - it resumes: only the questions with no row file run;
  - a reader or grader call that returned nothing (an error) is run once more, since there was no answer to choose from;
  - the brake stops new questions; the stop and its cause are reported, and the owner decides.
- **After the run:** no re-run. Re-scoring the kept outputs (`--kept`, no new search) is allowed only to correct a named fault in the scoring. Both figures are shown, and the owner decides which stands.

## 4. The K9 bar

### 4.1 The options
| option | the bar on the 79 | what it measures | likely result |
|---|---|---|---|
| **A.** hit@5 ≥ 85 % (DEC-1083 (2), the bar today) | 68 of 79 in the top 5 | whether the ranking puts a gold piece in the first five items | **almost surely missed.** About 68 % is expected. Even at the 138's 76.8 %, the chance of 68 of 79 is about 3 in 100 |
| **B.** right end to end ≥ 85 % and wrong claims ≤ 5 % (E3-E5-DESIGN §5) | 68 of 79 right and at most 3 wrong claims; target 95 % (76 of 79) | whether an agent, using memory as practised, answers correctly and cites the right source, without confident wrong answers | **likely passed.** At the hidden and spent sets' 89.8 %, about 9 in 10 for 68 of 79; with the wrong-claim ceiling too, about 7 in 10. At a true 85 %, about 1 in 2. The 95 % target: about 3 in 100 |
| **C.** both A and B | both lines | both | in practice the same as A: missed |

Each option reports every figure in §3.1 beside the line it judges.

### 4.2 What each means, honestly
- **A measures ranking, not use.**
  - Agents receive about 19 items and read them all (DEC-1085's reason).
  - E3 showed that handing an agent only the top 5 makes it answer worse: 84 right against 114, and with more wrong claims (10 against 3).
  - Still, hit@5 is the plain, model-free figure, and the one the Contract's CAP-10 uses (on its dev query set). A miss under A brings S9's options to the owner, as DEC-1083 (2) says.
- **B measures memory as agents use it, but it depends on things beyond memory:**
  - the reader model (`claude-opus-5-5` at effort high), so the figure should name it;
  - the graders;
  - the labels' list of places: 7 of the 138's 10 misses were correct answers citing a place the label lacks.
  - The wrong-claim ceiling is there because a confident wrong answer does more harm than "not found".
  - On the 138, B is also the more consistent figure across sets (§1.2).
- **When B came, plainly:**
  - the owner recorded the reason to judge what agents answer on 11-06, before any reader figure existed (DEC-1085: "what matters is whether an agent, reading its bundle, answers right and cites the right source");
  - the bar itself was proposed on 11-07 in E3-E5-DESIGN §5, **after** E0's 76.8 % hit@5 and **after** E2's 92.8 % on the 138 were known, though before E3 to E5 ran;
  - its 85 % and 95 % are CAP-10's floor and DEC-957's target, not figures fitted to E2.
  - So moving K9 from A to B must rest on what the bar measures (memory as agents use it), not on B being likelier to pass. If the owner holds that K9 is about retrieval as such, A is the honest bar, and a miss is the honest result.
- **The Contract:** as I read it, CAP-10's acceptance is a hit@5 on the dev query set, and K9's bar on the fresh 80 is a separate decision (DEC-1083). Choosing B does not edit CAP-10. If the owner reads CAP-10 as covering the fresh 80, a CIT-P note under DEC-105 would be needed. That reading is for the owner.

### 4.3 How the figures round on 79
- **85 %** needs at least 68 right (86.1 %); 67 is 84.8 % and misses.
- **95 %** needs at least 76 (96.2 %).
- **Wrong claims at most 5 %** allows at most 3 (3.8 %); 4 is 5.1 % and misses.
- **The bar is on the observed figure,** as DEC-1083 has it. The 95 % interval is reported beside it: for example, 70 of 79 is 88.6 %, with an interval of 79.7 to 93.9 %.
- **The nonexistent-id question** is reported apart (DEC-1071 (5)), as right or not, and is not in the bar.

**Recommendation: B,** with A's figures reported beside it every time. 95 % stays the target. The owner decides before the 80 runs.

## § E4's result (filled by the CTO from `E4-RESULT.md`)
- **What E4 measured:** today's bundle as M3 (zerank with gte) and as M1 (the 0.6B with gte) build it, through the harness at window 4's commit, one reader call each, against E3's bundle from the 0.6B.
- **The result:**
  - M3: 111 right end to end (3 gains, 6 losses, p 0.51);
  - M1: 113 (3 gains, 4 losses, p 1.0);
  - the 0.6B's bundle: 114.
  - **Neither beats it.** M3's higher hit@5 (117 against 106) moves gold up inside a bundle that already holds it (123 in every cell), and the reader reads the whole bundle.
- **G1's two profile readings** (19:05 and about 20:30, `G1-PROFILE.md`): the shared reranker's GPU is busy most of a 20-search burst (median 75 to 86 %). Two models (M3) would roughly double the scoring per search; 20 agents at once might wait about 26 to 30 s per search (an estimate, not measured).
- **The CTO's recommendation on M3's adoption (DEC-1087 (12)):** **keep the 0.6B** (M3-ADOPTION-1 §5, branch (c)), under the rule fixed before E4's figures.
- **What that changes in this package:** nothing. **§3 stands as written:** the 80 runs on window 4's pin with the 0.6B.

## 5. For the owner
1. **The configuration judged on the 80?**
   - (a) **recommended:** window 4's pin with the pool on, today's bundle at 6,000 tokens, search again once (A2);
   - (b) the same with M3, if E4 supports its adoption; the 80 then waits for M3's pin;
   - (c) one call, without search again.
2. **The commit?**
   - (a) **recommended:** window 4, `c00d525f`, E0's clone, before the lift's re-pin;
   - (b) the lift's re-pin, after E0 and E2's A2 are measured again on the 138 there (about $22 and 1 hour more, and the run waits for the lift).
3. **Which conditions run on the 80 for data?**
   - (a) **recommended:** only what comes free (the retrieval figures, A1, A3, and the 0.6B if M3 is judged);
   - (b) (a) plus E3's four other bundles, about $35 more;
   - (c) every experiment, about $60 to $70 more, including a second live retrieval for E5.
4. **The K9 bar?**
   - (a) hit@5 ≥ 85 %, as today;
   - (b) **recommended:** right end to end ≥ 85 % with wrong claims ≤ 5 %, target 95 %, with hit@5 reported beside it;
   - (c) both.
5. **May the readers and graders read the 80,** as for the 138 (DEC-1086 C, DEC-1092 (3)), with their run folder under the sets root? Recommended: yes. Without it, only option 4 (a) can be measured.
6. **The checker's staleness pass on the 80's gold answers at the measured commit** (item 3)? Recommended: yes, about 1 to 2 hours of your operator.
7. **The fixes and the fault rule as written** (§2 items 1 to 20, §3.5)? Recommended: yes.

**Confidence:**
- high that hit@5 misses 85 % on the 80;
- medium (about 7 in 10) that option 4 (b) passes;
- high that the fixes in §2 are needed for a clean single use;
- medium on the cost figures, since E2's per-question cost will rise with more second searches.

## 6. Basis (DEC-1052's five tests)
1. **Memory:** the verdict judges one configuration, chosen beforehand from the 138, on a set never used to choose, by what agents actually answer, with retrieval reported beside it.
2. **Fail open or lose work:**
   - without these fixes the verdict could fail open: a nonexistent id that now exists, a silent anchor, a better-of-two restart, a data condition put in the judged one's place;
   - or the single use could be lost: a fault mid-run with no rule.
3. **Only where the risk is:** the checks are pre-flight counts and one control on a tuning set; nothing is added to the product, and the 80 is used once.
4. **Delivery, not records:** one declaration and one result record; no new approvals beyond the decisions DEC-1092 (4) already asks of the owner.
5. **Proven before the product:** nothing here enters the product. "Search again once" is already a standing practice (DEC-1092 (1), DEC-1094 (2)), and the scripts stay in scratch.

**Sources read:** E0-DECLARATION, E0-RESULT, E0B-RESULT, E1-DECLARATION (with its amendment), E1-PILOT-RESULT, E2-RESULT, E3-E5-DESIGN (with "As run"), E3-RESULT, E3-SA-RESULT, E5-RESULT, E2G-DECLARATION, E2G-RESULT, G1-PROFILE, PAT-1-RESULT, SEVEN-ANSWERS §1 and §7, D4B-SCORE-ONCE (the grid, version 6, the family re-score); DEC-1052, DEC-1070, DEC-1071, DEC-1074 to DEC-1078, DEC-1083 to DEC-1096; both path maps' `evaluation_sets`; the pin's `gov/retrieval/measure.py` and `gov/retrieve/command.py`; `drafts/d4b/` `e0_run.sh`, `e0_figures.py`, `e2_run.py`, `e3_run.py`, `e4_run.py`; CAP-10 in `docs/contract/CONTRACT_v4.md`.
