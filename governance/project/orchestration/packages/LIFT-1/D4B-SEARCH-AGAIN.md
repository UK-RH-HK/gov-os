# D4B-SEARCH-AGAIN: an agent searches again in its own words, then settles (DEC-1085 (4)); declared before any run

**Status:** declared, not run. It runs after the memory build's decided items (DEC-1085 (1)). One point needs the
owner's word first (§6).

## 1. What is tested
When an agent's first search does not answer the question, it searches again in different words. If that fails, it
settles as "not found". The cap is two attempts or three.
- **A1, one search:** the agent answers from the first bundle or settles. This is the baseline, today's practice.
- **A2:** up to two searches.
- **A3:** up to three searches.

**One run gives all three.** The reader is given the same instructions at every attempt, and is never told how many
attempts remain. The harness stops it at the cap, and a request for one more search at the cap counts as "not found".
So A1 and A2 are A3's run cut after its first and second attempts. That is exact, not an estimate.

## 2. The set and the retrieval
- **The 138** (tuning: the visible 40, the hidden 39, the spent 59). The nonexistent-id questions are included and
  counted apart, by the measure's code, in ids and counts only.
- **The retrieval is B0,** the base every cell was judged on (v456, the question given to the rerank, L3, the 0.6B).
  - The first search's bundle comes from g-B0's kept outputs, so no GPU is needed.
  - Later searches run live through the harness copy, the reranker cache seeded with the kept scores. Only new texts
    go to the live 0.6B. That is one GPU job, in a quiet window.
- **A bundle is the first call's,** as an agent receives it (18 or 19 items, the top 10 always). The same rule holds
  at every attempt.

## 3. The reader (an agent of the kind Gov OS launches)
- **The model:** `claude-opus-5-5` at effort `high`, the launcher's default (`tools/launch_worker.sh`).
- **How it runs:** `claude -p --safe-mode --tools "" --no-session-persistence --output-format json --json-schema`,
  with a short system prompt of the run's own. It has no tools and no repository, and it keeps no transcript.
- **What it is given:** the question, then the bundles so far (each item's path, lines and text). It answers only from
  them.
- **What it returns:**
  `{"verdict": "answer" | "search_again" | "not_found", "answer", "citations": [{path, start_line, end_line}], "search"}`.
  - `search` is new search words; it is used only with `search_again`.
  - The instruction is the practice under test: "If the bundles do not answer the question, give different search
    words. If you judge the answer is not in the repository (an id that exists nowhere, say), answer not_found. Never
    answer beyond the bundles."
- **The words are the reader's own.** The harness never rephrases.

## 4. The grader (independent of the reader)
- **The citation is checked by code:** it is right when it overlaps a gold source's lines, by the measure's own
  matching (the corrected labels; source families once W2-134 lands).
- **The answer is checked by a grader session:** `claude-opus-5-5` at effort `high`, run the same way as the reader
  (no tools, no transcript). It is a separate session, which never sees the reader's reasoning.
  - It is given the question, the gold answer and the reader's answer.
  - It returns `correct`, `wrong` or `not_found`. `correct` means the answer states the gold's facts and contradicts
    none.
  - For a nonexistent-id question, `correct` means "not found" or "that id does not exist".
- **The agreement check:** a second grader (`claude-sonnet-5-5`) grades every final answer. Disagreements are counted
  and reported. The first grader's verdict counts.
- **Right end to end** means the answer is correct and the citation is right.

## 5. What is reported, per condition (A1, A2, A3), per set and on the 138
- **Right end to end;** the answer correct; the citation right.
- **Wrong claims:** answered, but not correct. They are counted on the nonexistent-id questions apart.
- **Not found** (settled).
- **Misses recovered:**
  - at the retrieval level: the 15 questions whose first bundle lacks the gold (B0: 123 of 138 in the bundle) and
    whose later bundle holds it;
  - at the answer level: answers wrong or not found at A1 that are right at A2 or A3.
- **Cost:** the reader's and the grader's tokens (input and output) per question, the number of searches, and the
  wall time per question (median and p90).
- **McNemar,** exact, on "right end to end": A1 against A2, and A2 against A3.
- **The hidden-half rule:** the harness prints counts per set and question ids only. The questions, the answers and
  the grades stay in the run folder, and the CTO never opens them.

## 6. The point for the owner, before any run
**The reader and the grader read the hidden and spent questions and their gold.** No measured role does. The sessions
have no tools, run from a run folder under `~/gov-os-runs/D4B/search-again/`, and keep no transcript
(`--no-session-persistence`). Their outputs stay in that folder, and the CTO sees counts only.
- **(a) Run on all 138 this way (recommended).** The misses are mostly in the hidden and spent sets: of the 15,
  2 are visible, 4 hidden and 9 spent.
- **(b) The visible 40 only.** There would be too few misses to show anything.

## 7. Cost and time (est., before the pilot)
- **The pilot first:** 5 visible questions, to check the schema and measure tokens, time and cost from each call's own
  JSON (`total_cost_usd`). The full run follows only if the pilot is within the figures below, or the owner says so.
- **Reader:** about 200 attempts. Input is about 7k tokens at attempt 1, 14k at attempt 2 and 21k at attempt 3: about
  1.6M tokens in, and 0.3 to 0.5M out at high effort.
- **Graders:** about 170 final answers, each graded twice: about 0.7M tokens in.
- **Time:** about 45 s a reader call. With 4 calls at once, the run takes about 1 hour, plus the live searches
  (about 1.2 s each).
- **A budget cap** on every call (`--max-budget-usd`). The run stops if the pilot's cost per question, times 138, goes
  past the cap the owner sets.

## 8. What follows
If search-again recovers misses without raising wrong claims, a practice package follows (DEC-1085 (5)). The
end-to-end package (DEC-1085 (6)) reuses this reader, grader and harness, and adds the bundle conditions.
