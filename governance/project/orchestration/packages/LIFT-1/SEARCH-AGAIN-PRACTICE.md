# SEARCH-AGAIN-PRACTICE: "search again once" as a standing practice for agents (DEC-1092 (1), under DEC-1085 (5))

For the owner. Drafted 2026-11-07 by a product-spec agent for the CTO (session `ad44f5fe`). Nothing here is applied:
each change below is a patch to apply once the owner approves.

## 1. What is decided, and what this package asks
- **Decided (DEC-1092 (1)):** E2 is accepted. "Search again once" becomes a standing practice for agents. It comes to the
  owner as a package: skills, the role templates through W2-128, and hooks if needed (DEC-1085 (5)). Nothing goes into
  the skills or the roles before the owner approves.
- **The evidence** (`packages/LIFT-1/E2-RESULT.md`, on the 138 tuning questions):
  - right end to end: **83.3 % with one search, 92.8 % with up to two**; 13 gains, 0 losses, exact McNemar p = 0.0002;
  - **a third search adds nothing** (0 and 0, p = 1.0);
  - the answer correct, citation aside: 121 at one search, 135 (97.8 %) at two;
  - wrong claims: 2 at one search, 3 at two, all on the hidden set (counts only); none on the visible or spent sets;
  - "not found": 15 at one search (mostly requests to search again, cut at the cap), 0 at two.
- **Where the practice came from:**
  - `D4B-SEARCH-AGAIN.md` §3 declared the reader's instruction: "If the bundles do not answer the question, give
    different search words. If you judge the answer is not in the repository (an id that exists nowhere, say), answer
    not_found. Never answer beyond the bundles."
  - The pilot (`E1-PILOT-RESULT.md`) found Q14: the reader answered a partial list while saying itself "this list may
    not be complete", and did not search again.
  - So the owner added one line before E2 (DEC-1091 (3), `E1-DECLARATION.md`'s amendment): "If you can tell your
    answer may be incomplete, search again for what is missing." Q14 was right in E2.
- **This package asks the owner for six things (§8):** the practice's text; the order it lands in; the skills' home;
  one W2-128 KPI line; no hook now; and how adoption is counted.

## 2. The practice (the paragraph agents follow)
> **Search again once.** When your `gov retrieve` bundle answers the question, answer from it. When it does not, or
> you can tell your answer may be incomplete, search once more in your own, different words: use the ids, names and
> paths the first bundle showed you, or the term the repository uses. Then answer from both bundles and the files you
> read, citing each fact's path and lines, or say "not found" and what is missing. Two searches in all, by default.
> Never answer beyond what the bundles and the files you read show.

**What counts as "does not answer":**
- no item states the fact asked for; the items are only about the same area;
- an item names the thing but not the part asked (the decision but not its item, the function but not the behaviour,
  the ticket but not its status);
- the question asks for all of something ("every ticket that…", "each place where…"), and the bundle shows some but
  cannot show that it holds all (Q14's kind);
- your own draft needs "probably", "it seems" or "this may not be complete";
- the stopping reason is `UNRESOLVED_IDS` for an id you were asked about. Search once more (the id may be written
  another way); if the second search finds nothing, say "not found": the id may not exist. (E2's two nonexistent-id
  questions were right at every condition.)

**What does not count:**
- the bundle answers, but its lines differ from your tree: that is step 5's line-hash check (read your own file);
- a continuation token: `--continue` is the same search (step 6), not the second one;
- `FACET_UNAVAILABLE`: a fault, not a miss. Report it;
- wanting more confirmation of an answer the bundle already states with its source.

**The cap:** two searches in all. A third only when the brief asks for it (E2: a third search changed no outcome).

## 3. Where it lives (a patch per file; nothing applied)
The practice lands in two layers, in this order (DEC-1052's fifth test: a practice enters the product only after it
has proven itself in use):
- **Now, the project layer** (the CTO's lane, no ACT): the CTO's agents' common brief, and the lead's and the
  auditor's common briefs, which reach every worker brief written today. Items 3.4 to 3.6.
- **Then, the kernel layer** (CAP-33: evidence, an independent review, the owner's approval, a versioned promotion):
  the two kernel skills (3.1, 3.2) and the templates W2-128 writes (3.3).
  - **The generated `.claude/` copies follow at an owner ACT.** The templates' approval and their `.claude/` copies
    are an ACT (`START-NEXT-SESSION.md` §6: "the templates' approval and their `.claude/` copies (an ACT)").
  - `.claude/skills/retrieval/SKILL.md` today still lacks W2-138's step-5 line; its copy is regenerated at the lift's
    re-pin ACT. Step 7 below can ride that same regeneration (§8 question 3).

**No kernel role file changes.** No file under `template/governance/kernel/roles/` tells an agent how to use
`gov retrieve` (the only "search" hits there are the WebSearch tool). W2-128's TPL-4 generates the role bodies from
its templates, so the practice reaches the roles through T-0 (3.3).

### 3.1 `template/governance/kernel/skills/retrieval/SKILL.md`: a new step 7 (W2-138's step-5 line kept)
**Current text (line 24, step 6, unchanged; the new step goes after it, before "## Key constraints"):**
```
6. **Handle continuation.** If the bundle carries a continuation token and the stopping reason is not `CLOSURE_COMPLETE` or `SATURATED`, pass the token back with `--continue` to gather more evidence within the spend budget.
```
**New text (inserted as line 25, after a blank line):**
```

7. **Search again once (DEC-1092 (1)).** If the bundle does not answer the question, or you can tell your answer may be incomplete, run `gov retrieve` once more in your own, different words (the ids, names and paths the first bundle showed, or the repository's own term). Then answer from both bundles and the files you read, citing path and lines, or say "not found" and what is missing. The bundle does not answer when no item states the fact asked (only its neighbourhood), when an item names the thing but not the part asked, when the question asks for all of something and the bundle cannot show it holds all, or when your draft needs "probably" or "may be incomplete". A continuation (step 6) is the same search, not the second; `FACET_UNAVAILABLE` is a fault to report, not a miss. Two searches in all by default; a third only when your brief asks. Never answer beyond what the bundles and the files you read show.
```
**The front matter, line 4:** `version: "1.0.0"` becomes `version: "1.1.0"` (one bump covering W2-138's line and
step 7, at the versioned promotion).

**Checks that still hold:**
- W2-138's text test reads step 5 as the text from `5.` to `6.`. Steps 5 and 6 are untouched, so it still passes.
- The skills check (`gov.check.skill_validator`): `retrieve` is a known command, and the body stays far under 2,500
  tokens (2,854 characters today, about 3,800 after).

### 3.2 `template/governance/kernel/skills/discovery/SKILL.md`: before a question is routed to the owner
A decision package is routed when "the retrieval bundle and existing specifications do not answer" (line 43). One
search is too little to say that.

**Current text (line 55):**
```
Before formulating a decision package, the practitioner gathers context through `gov retrieve` (CAP-34.c). The retrieval bundle surfaces related specifications, decisions and evidence so that packages present questions the existing record does not already answer.
```
**New text:**
```
Before formulating a decision package, the practitioner gathers context through `gov retrieve` (CAP-34.c). The retrieval bundle surfaces related specifications, decisions and evidence so that packages present questions the existing record does not already answer. When the first bundle does not answer, the practitioner searches once more in its own words before treating the question as unanswered (the retrieval skill, step 7; DEC-1092 (1)).
```
**Unchanged:** line 35 (experiments) and `skills/checkpoint/SKILL.md` line 42. Both only say where knowledge comes
from, not how to search.

### 3.3 The templates, through W2-128 (`.tickets/DAEO-t8mp.md`, open, not started)
- **What W2-128 owns:** T-0 to T-8 in `template/governance/kernel/templates/` (TPL-1 S1), written "as in
  R3-TEMPLATES.md's Appendix". D-5 in `P1-PLAN.md` places them; none exists yet (the folder still holds the old
  `brief-*.md` files).
- **Where the line goes:**
  - **T-0** (`brief.md`), the envelope every launched session receives on stdin, the leads' briefs included (TPL-3
    S1). It is the one place every worker and lead reads, so the line goes there once. The role templates T-2 to T-7
    only point to `{CMD:retrieve}`. Of them, only T-2 (research) lists the `retrieval` skill.
  - **T-8**, the CTO's operating card, which does not receive T-0.
- **T-0, current text (R3-TEMPLATES.md Appendix, line 286):**
  ```
  Ask memory first: {CMD:retrieve} "<which decision governs X | where is Y implemented>"; grep the register only by id.
  ```
  **New text (one line added after it):**
  ```
  Ask memory first: {CMD:retrieve} "<which decision governs X | where is Y implemented>"; grep the register only by id.
  Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read.
  ```
  This adds about 230 characters. T-0's prose in the Appendix is 2,295 characters, against a budget of 4,000 (R3 §C).
- **T-8, current text (Appendix, line 511):**
  ```
  Start: read RESUME HERE and the decisions-in-force list; the rest on demand ({CMD:retrieve}).
  ```
  **New text:**
  ```
  Start: read RESUME HERE and the decisions-in-force list; the rest on demand ({CMD:retrieve}; search again once in other words when a bundle does not answer, the retrieval skill's step 7).
  ```
- **R3-TEMPLATES.md itself is not edited.** It is a dated research record. W2-128's KPI line below carries the change.
- **The ready check is unchanged.** The practice is how an agent works, not a field of a ticket or a brief. The ticket
  template (T-1) gets no line.
- **Proposed W2-128 KPI line, marked for the owner** (DEC-1088 (6): an open ticket may change, each change marked with
  the decision that made it):
  ```
  - 'Search again once (DEC-1092 (1)): T-0''s Commands block carries, right after its "Ask memory first" line, "Search again once: if the bundle does not answer, or your answer may be incomplete, ask once more in your own, different words; then answer from both bundles with path and lines, or say "not found". Two searches in all; never answer beyond what you read."; T-8''s Start line names it. TPL-7''s M3 reports this line''s use but sets it no target (it applies only on a miss). Verify: a string test on T-0 and T-8 for "search again once", "own, different words", "not found" and "two searches" [DEC-1092, DEC-1085 (5)] [added, DEC-1092]'
  ```

### 3.4 `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`: the "Knowledge" bullet (the CTO's file, untracked)
**Current text (lines 40 to 44):**
```
- **Knowledge:** use `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` for what you need to
  know about the codebase and the decisions (DEC-836, DEC-1087 (3)). A worktree has no store of its own (a plain
  `gov retrieve` there answers `STORE_MISSING`). The integration store holds integrate's head, so its line numbers are
  integrate's: read the file in your own worktree before relying on a line. Ask code questions by small, targeted
  searches, never one giant query (DEC-859, DEC-860).
```
**New text:**
```
- **Knowledge:** use `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` for what you need to
  know about the codebase and the decisions (DEC-836, DEC-1087 (3)). A worktree has no store of its own (a plain
  `gov retrieve` there answers `STORE_MISSING`). The integration store holds integrate's head, so its line numbers are
  integrate's: read the file in your own worktree before relying on a line. Ask code questions by small, targeted
  searches, never one giant query (DEC-859, DEC-860). **Search again once (DEC-1092 (1)):** if the bundle does not
  answer, or you can tell your answer may be incomplete, search once more in your own, different words; then answer
  from both bundles and the files you read, with path and lines, or say "not found". Two searches in all.
```

### 3.5 `governance/project/briefs/LEAD-w2-common.md`: what every worker brief says (line 30)
Leads write every worker brief from this bullet today, until TPL-6 S2 replaces the file with T-7 and the facts.

**Current text (the first sentence of line 30, unique in the file):**
```
- **DEC-836, memory used:** every worker brief you write tells its agent to use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 -m gov.cli.main retrieve "<question>" --json`) for what it needs to know before reading files at random; your return says, per worker, whether its brief said so and whether its log shows it used it.
```
**New text:**
```
- **DEC-836, memory used:** every worker brief you write tells its agent to use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 -m gov.cli.main retrieve "<question>" --json`) for what it needs to know before reading files at random; your return says, per worker, whether its brief said so and whether its log shows it used it. **DEC-1092 (1), search again once:** the same line tells it that when a bundle does not answer, or it can tell its answer may be incomplete, it searches once more in its own, different words, then answers from both bundles with path and lines, or says "not found"; two searches in all.
```
The rest of line 30 (DEC-860, DEC-859) is unchanged.

### 3.6 `governance/project/briefs/AUDITOR-common.md`: the reviewer's retrieval line (line 8)
**Current text (the first sentence of line 8):**
```
- Use `gov retrieve` for what you need to know, and say in your report which questions it answered.
```
**New text:**
```
- Use `gov retrieve` for what you need to know, and say in your report which questions it answered. When a bundle does not answer, or your finding may rest on an incomplete answer, search once more in your own, different words before you rely on it; two searches in all (DEC-1092 (1)).
```
The rest of line 8 is unchanged.

**Unchanged in the project layer:** `governance/project/prompts/w2-orchestrator.md` lines 127 and 391 only require that
briefs name `gov retrieve`. The briefs above now carry the practice with it.

## 4. Hooks: none recommended
- **What a hook could do:**
  - a SessionStart hook could add the practice's paragraph to every session;
  - a PostToolUse hook on `gov retrieve` could remind the agent after each search.
- **Why not, by DEC-1052's five tests:**
  - **Test 3 (only where the risk is):** both hooks fire on every session or every search. The practice applies only on
    a miss: 19 extra searches in 140 questions in E2.
  - **Test 4 (more delivered, not more text):** a hook adds the same text where the skill and T-0 already carry it.
  - **Can it tell a miss?** No hook can tell whether a bundle answered the question. Only the agent reading the bundle
    can, which is where E2 put the judgement.
  - **Test 2:** without a hook, nothing fails open. The cost of a missed second search is a weaker answer, and the
    practice and the "may be incomplete" line already cover it.
- **When to look again:** if the adoption count (§5 (b)) shows that, of the returns that say "not found" or "may be
  incomplete", fewer than half searched twice first, the CTO brings a hook package with those counts. The threshold is
  proposed, not measured.

## 5. Measure: how adoption is judged after it lands
- **(a) The effect, end to end.** E3 runs search-again on its best two conditions on the 138 (DEC-1092 (2)). The fresh
  80's configuration, chosen from the 138 before the 80 runs, includes the practice, and is judged once (DEC-1092 (4)).
  No extra run and no extra cost.
- **(b) Adoption in use.** A read-only count over the launched sessions' transcripts, two weeks after the project
  lines land, then weekly in the digest. It is never a gate (DEC-1052: measures only report). It counts:
  - of the sessions that ran `gov retrieve`, how many ran a second search with different words;
  - of the returns that say "not found" or "may be incomplete", how many searched twice first.

  It is a small script in the CTO's tools (about 40 lines, about an hour, est.). Once W2-128 lands, TPL-7's M3 reports
  the same line from a `match:` pattern in `facts.yaml`, with no target, because the line applies only on a miss.
- **Not a measure of this practice:** W2-61's memory measure (and W2-61h's enlarged set) scores the retrieval, hit@5
  and the bundle, not what an agent does with it.

## 6. Cost
- **E2's measured cost:** $21.95 for 140 questions, **$0.157 a question all in** (the reader and two graders). There
  were 159 reader calls and 19 live searches: one extra search on about 14 % of questions, at most.
- **In agent work, the practice costs one more `gov retrieve` on a miss:**
  - one live search (about 1.2 s, D4B §7, est.) and one more bundle in context (about 7k tokens, D4B §7, est.);
  - in the pilot, a question needing a second search cost about $0.30, against about $0.16 when one search answered;
  - so about $0.02 a question on average at E2's rate (est.).
- **The shared reranker** gets the extra searches too: about 14 more requests per 100 questions. This is small beside
  W2-137's 64-text cap.
- **Writing it:**
  - the project layer: a few minutes of the CTO's time;
  - the two skills as a LITE ticket: about 2 to 3 hours of agent time (product-spec, a text test by an independent
    test designer like W2-138's, one review, est.);
  - the W2-128 line: inside W2-128's estimate;
  - the owner: this reading, plus the `.claude/` copy inside an ACT already planned.

## 7. Risks
- **E2 measured a reader with no tools.** Real agents also read and grep files, so the gain in use may be smaller. The
  fresh 80 judges the harness form once; §5 (b) counts the use.
- **Wrong claims went from 2 to 3,** all hidden and counted only. "Never answer beyond what you read" stays in every
  copy of the practice.
- **The evidence is on the tuning sets** (visible, hidden, spent). The fresh 80 gives the verdict once, after the
  decisions (E2-RESULT).

## 8. For the owner
1. **The practice (§2):** approve the paragraph, the "does not answer" list and the cap of two searches as written?
   *Recommended: yes* (high confidence: 13 gains, 0 losses, p = 0.0002; a third search adds nothing).
2. **The order:** the project layer (3.4 to 3.6) now, by the CTO; the kernel layer (3.1 to 3.3) after it has been in
   use, through CAP-33. *Recommended: yes* (DEC-1052's fifth test).
3. **The two skills' home (3.1, 3.2):**
   - (a) a new LITE ticket (product-spec, tests first, one review; the next free id, W2-139 today), landing at the
     lift's re-pin ACT, where `.claude/skills/retrieval/` is regenerated for W2-138 anyway;
   - (b) folded into W2-128's CIT-P, adding the two skill paths to its `allowed_paths` (marked DEC-1092). W2-128 is
     not started and is about 4 to 5 days of work.

   *Recommended: (a)* (medium confidence). It reaches the kernel sooner with the same single ACT; (b) saves one review
   but waits on W2-128.
4. **W2-128's KPI line (3.3):** add it, marked DEC-1092? *Recommended: yes.* It changes no other line of W2-128, and
   the ready check is unchanged.
5. **Hooks (§4):** none now; a hook package only if §5 (b)'s count calls for one. *Recommended: yes.*
6. **The adoption count (§5 (b)):** a read-only script in the CTO's tools, in the digest, never a gate.
   *Recommended: yes.*

**Basis:**
- question 1: memory judged by what agents answer, end to end;
- question 3: it runs only on a miss, never on every search;
- question 4: more right answers, about 2 cents a question, and no new record, approval or ping;
- question 5: proven on the 138, and in use in the project's briefs before it enters the kernel.
