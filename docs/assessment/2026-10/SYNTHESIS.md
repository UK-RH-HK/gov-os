# Independent assessment of the Gov OS, October 2026 — Lens S: synthesis

**Date.** 2026-10-19.

**Assessor.** An independent-auditor session (`GOV_ROLE=independent-auditor`), the sixth session of the assessment. The Wave 2 orchestrator started it on the owner's order of 2026-10-19. I wrote none of the work assessed and none of the five lens reports.

**Head assessed.** `w2/integrate` at `fecb870c`. Its working copy holds the owner's staged batch, DEC-813 to DEC-817, uncommitted. Contract v4.2 exists only on the held branch `w2/W2-49`. Wave 2 was paused throughout.

**Readers.** The owner and an outside adviser.
- Section 1 is the diagnosis, on one page.
- Sections 2 to 6 are the roadmap and four work plans.
- Section 7 holds the owner decisions, each a stand-alone package.
- Appendix A lists where the five reports disagree. Appendix B carries every finding of the five reports with its two judgement lines.

## About this synthesis: sources, citations, words and limits

**Sources: these only.**
- The five lens reports of 2026-10-19, in `.gov-runtime/scratch/assessment/2026-10/`:
  - **A**, purpose and roadmap (`A-purpose-roadmap.md`);
  - **B**, memory and retrieval, measured (`B-memory-retrieval.md`);
  - **C**, decisions into the specifications and the skills (`C-decisions-to-spec.md`);
  - **D**, tool staging, and building versus using (`D-tool-staging.md`);
  - **E**, roles, skills and context supply (`E-roles-context.md`).
- The Charter v5 (`docs/charter/CHARTER_v5.md`).
- Contract v4.2, read with `git show` from `w2/W2-49`.
- ADR-0001, the threat model (`docs/adr/ADR-0001-threat-model.md`).

**Citations.**
- "[A F1]" is report A's finding F1. Report C numbers its findings F-1 to F-10 and its recommendations R-1 to R-8; D and E number theirs F1 and R1. A and B number their recommendations 1, 2, 3 …, cited as "A rec. 1" and "B rec. 1".
- "[D §2.2]" is a section of a report. "[B, What works]" is a named part of a report.
- "[Charter:31]" and "[ADR-0001:52–57]" are line numbers. "[CAP-44.h]" is an item of Contract v4.2.
- Line references such as "register:8296" or "WBS:951" are the reports' own citations. I did not re-check them.
- "My proposal" marks a step that is mine and not in any report.

**How findings are judged.** The threat model is ADR-0001's. The Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work. It does not guard against a deliberate adversary with the owner's privileges [ADR-0001:41–51]. Every finding carries two lines (DEC-808):
- "Ordinary work: yes|no, because …" answers "Can an honest agent hit this in ordinary work?";
- "Consequence: fails open|loses work|other" answers "Does it fail open or lose work?".

Only a finding with "yes" to both justifies a round. Even then, an accepted fix rides along in a ticket that runs anyway, with no extra round (DEC-801, DEC-802). A risk that comes with a feature becomes an entry criterion of the ticket that switches the feature on (DEC-803). **This synthesis proposes no round.**

**Words used.**

| Word | Meaning |
|---|---|
| Gov OS | The governance tool set this repository builds. It has four parts: the `gov` command-line program (Python, under `src/gov/`), the Claude Code hooks, the git hooks (installed by lefthook), and the kernel [D §1]. |
| Kernel | The part every adopting repository receives: role files, skills, brief templates and hooks, under `template/governance/kernel/` [C F-1; E F2]. |
| Charter, Contract, MR, CAP | Charter v5 says what the Gov OS is for. Contract v4 turns it into capabilities, CAP-01 to CAP-62, each with lettered items (for example CAP-44.h) and one acceptance check each. MR-1 to MR-6 are the Charter's master rules. |
| Lite | A reduced Wave 2 form of a Contract item; the full form comes later [CAP-43.b; CAP-44.h]. |
| Hard boundary | ADR-0001's last line of defence, outside any agent: git history, the lefthook pre-push gate (G3), CI on every push (G4–G5) as an advisory result, and "only the owner merges, and only on green" [ADR-0001:52–57]. |
| Wave, track, ticket | Wave 2 is the current block of work, begun on 2026-10-16. It has three tracks: A (adoption readiness), B (the EXAMIN pilot) and C (the rest). A ticket has a plan id (W2-nn) and a tracker id (DAEO-xxxx) [D §1]. |
| Orchestrator, lead, worker | The orchestrator is the main session that runs the Wave. A ticket lead runs one ticket in its own worktree and starts its workers: an engineer, an independent test designer and reviewers [D §1]. |
| Register, WBS, LIST, TRIAGE, row | The register records every owner decision (DEC-nnn). The WBS is the Wave 2 plan. The LIST holds known problems, called rows: W2-H… high, W2-M… medium, W2-L… low. The TRIAGE assigns each row to a ticket [D §1]. |
| Package, round | A package (P-W2-n) is a decision put to the owner. A round is one more review-and-repair cycle on a ticket [A F2]. |
| AR-1 to AR-10, F-M… | AR items are the owner's adoption-readiness items. F-M… are findings of the Wave 1 exit audit (W1-43). DEC-718 settles both [D §1]. |
| Guard | The hook that allows or refuses each tool call, by role and path, before the call runs [D §1]. |
| Containment | The check after each shell command that records changes outside a ticket's allowed paths. It records; it does not block [D §2.1]. |
| Sandbox | The operating-system sandbox that `gov launch` puts around a launched worker's shell commands [D §2.1]. |
| `gov launch` | Starts a worker session with its role's settings, inside the sandbox [D §2.1; E §2.3]. |
| `gov close` | Decides whether a ticket may close. It runs the acceptance tests, the full regression (about 13,500 tests, one to one and a half hours) and the governance checks (`gov check`), and it checks the probe and the commit trailers. Exit 0 is a "clean close" [D §1, F3]. |
| `tk close` | The plain ticket tool's close. It runs no checks, and is allowed only by a named owner decision [D §1]. |
| Ratchet | Two owner-kept lists. `accepted_reds` holds known failing tests that do not refuse a close. `load_sensitive` holds tests that are re-run alone inside the close when they fail, and count only if they then pass. Since 2026-10-18 both lists only shrink (DEC-766) [D F4]. |
| Probe | An independent adversarial review of a ticket's final code, recorded under `docs/probes/` [D §1]. |
| load1, resource gate, quiet window | load1 is the machine's one-minute load average. The resource gate allows a heavy run only when load1 is below 20 and enough memory is free. A quiet window is a period with no other lead running; every close needs one (DEC-780) [D §1]. |
| Editable install, release, pin | An editable install runs a source folder as it is at that moment. The `gov` on PATH is an editable install of this repository (DEC-605). A release is a fixed, hash-verified version (W2-16 builds `gov release`). To pin is to install a release so that it cannot change under its users (W2-18) [D §1, F1]. |
| Main tree, worktree | The main tree is the repository's main checkout, on `w2/integrate`. A worktree is a separate checkout of one ticket's branch [D §1]. |
| Dev tiers, fixtures | Synthetic projects, ORION ("a-dev") and ARGUS ("b-dev"), and test fixtures, used to try the Gov OS outside this repository [D §1]. |
| Context packet | What `gov context` gives a session for a ticket. Its mandatory items are the Contract items and decisions the ticket cites; its supplementary items come from retrieval. Its ceiling is 6,000 tokens (DEC-004) [B F1; C §2.5]. |
| Retrieval | `gov retrieve`: search over the repository by a lexical index (exact words), semantic vectors (meaning), the fusion of both, and a reranker. A code graph answers callers and callees [B]. |
| hit@5 | The share of test questions that have a right answer among the first five results [D §2.1]. |
| Checkpoint | A saved note of a session's state and next step. Deliberate checkpoints go in `docs/checkpoints/`. Automatic ones are written by the stop and pre-compaction hooks [B F5; E F11]. |
| Compaction | The harness's summary of a long session. After it, the session-start hook injects context again [E F9]. |
| Brief; A1 to A5 | A brief is the written instruction a session starts from. A1 to A5 are the w2 prompt's outlines for the test designer, the engineer, the reviewer, the product-spec worker and the lead [C F-2; E §2.2]. |
| Twelve-field return | The worker return contract of CAP-37.d: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action [CAP-37.d]. |
| CIT-P, CIT-E | A change proposal and its evidence record. Any change to the kernel, the policy or the skills needs both, with independent review and owner approval (CAP-33) [D §1]. |
| DEC-105's three options | A proposal that contradicts a closed specification comes with three costed options: apply now, defer, or re-baseline [D §1]. |
| Scratch | `.gov-runtime/scratch/`, a working folder that git ignores [C F-1]. |
| EXAMIN's copy, EXAMIN's real repository | The owner's copy of the EXAMIN product, used for the trial adoption (W2-27, verdict by W2-28), and the product's real repository (verdict by W2-30) [Charter:32–36]. |

**Limits.**
1. **Second-hand evidence.** I read only the sources above. Every fact about code, the register, the plan and the logs comes through the reports' own citations, which I did not re-check.
2. **Nothing re-measured.** Where the reports disagree, I say so, with the evidence each rests on, and I do not settle it (Appendix A).
3. **Estimates are mine.** The time estimates in section 2 are my judgement. I state their basis and my confidence.
4. **What I ran.** I used only the Read and Grep tools, `cat`, `git show` and `grep`, with two exceptions. One early command also used `ls` on the assessment folder and a `sed` line filter on a `grep` of report C's headings; another shortened a `git show | grep` with `head`. Both were read-only. I recorded no refused call.
5. **Not read.** The held-out material; the harness settings files; the workbench; EXAMIN's real repository; the user-level configuration folder; and the staged decisions DEC-813 to DEC-817 themselves, which I cite only through the reports.
6. **A loaded machine.** The five reports were written on one day, on a shared and loaded machine (load1 between 22 and 30) [A, header; D §1]. Their measurements are of that day.

## 1. The diagnosis, in one page

**In one sentence.** The Gov OS is built fast, and its safety design holds: nearly every fault the five lenses found fails closed. But it is judged, guarded and briefed by its own unfinished code, and its working rules live outside git. So almost nothing of Wave 2 counts as delivered yet, and no product is governed [D F1; C F-1; A F1, F3].

**Against the owner's four purposes.**

| Purpose | State on 2026-10-19 | Evidence |
|---|---|---|
| The project's memory lives in the repository | **As a record, yes; as working memory, no.** Every decision is in the register, and specification decisions reach code and tests (24 of 26 sampled). But Wave 2's working rules live mostly in uncommitted scratch, a launched session loads none of its role's rules, the context packet carries ids instead of text, and a resume loses the recorded next step. | C §2.0, F-1; E F2; B F1, F5 |
| Agents are safe and governed | **Mostly, through guardrails that fail closed.** The guard is the one tool that is a gate by its record. ADR-0001's hard boundary is off for the Wave: the git hooks are removed, and CI cannot pass. Leads run unsandboxed, with the orchestrator's rights. | D §2.1, F6; E F1 |
| The owner stays in control | **Yes, but the owner is the queue.** 99 decisions in four days; owner-only remedies for routine cases; the owner's own prompt lags the owner's decisions. | A F2; D F4; C F-2 |
| Products are built faster and more safely | **Not yet.** No product is governed. EXAMIN's copy has moved behind more work; UPIM and ASMO are in no plan; Release 1 has no date. | A F3 |

**Five findings of this synthesis.** Each joins evidence from two or more lenses.

**S-1. The Gov OS governs itself with its own working copy, and its one gate has never passed here.** The `gov` on PATH is an editable install of the main tree. Each session's hooks run that session's own tree, and `gov close` judges a ticket with the code it merged [D F1, §2.2]. None of 33 logged closes on this repository passed. Wave 2 has closed 1 ticket of 55, by owner exception. One Wave 1 timing test holds the 13 tickets in the close order, and the tickets that would end this loop wait behind it [D F3–F5; A F1].
- Ordinary work: yes, because every session, hook, check and close on this repository runs whatever code is on disk in its tree at that moment [D F1].
- Consequence: other. It fails closed; the cost is the queue, and the owner decisions the queue needs [D F1, F3].

**S-2. Wave 2's working memory is outside the repository.** Of Wave 2's 99 decisions, 52 reach agents only through scratch briefs and 22 through no channel at all. None is in the kernel that EXAMIN, UPIM and ASMO will receive [C §2.5, F-1]. Sessions get their role's rules only through briefs written by hand and kept outside git [E F2]. No decision text reaches the packet [B F1; E F8], and a resume loses the next step [B F5; E F11].
- Ordinary work: yes, because every session starts this way, and a fresh clone or an adopting repository starts from the committed prompt and the kernel, which lack these rules [C F-1; E F2].
- Consequence: other. Later gates catch a missed rule, and nothing fails open [C F-1]. But the record of what each agent was told is not in git [E F2].

**S-3. Three checks pass what is not there.** The plan validator passes exit criterion 7 on items no closed ticket delivered [A F4]. `gov doctor` passes the hooks when no git hook is installed [D F7]. The filter meant to keep superseded register decisions out lets them through [B F4].
- Ordinary work: yes, because each runs in routine work: the exit check, the health check, and every decision question [A F4; D F7; B F4].
- Consequence: fails open, because each gives a pass for something absent. Each fix rides in a ticket that runs anyway (W2-51; W2-08 or W2-22; W2-32 or W2-03), so no extra round is needed (DEC-802).

**S-4. Owner attention, not code, sets the pace, and the work is drifting into the machinery.** Six of the seven tickets added since the plan was approved repair or enable the machinery. Code comes in at about twice its estimate, with about eight test lines per code line. The size review that DEC-064 asked for was never held, and the size is now about three times DEC-064's estimate [A F2, F6]. Routine remedies are the owner's alone [D F4].
- Ordinary work: yes, because the rounds and the new tickets came out of ordinary reviews of ordinary tickets [A F2].
- Consequence: other. The cost is time, owner attention and size; nothing fails open [A F2].

**S-5. The product payoff has no schedule.** The plan put the copy's verdict near day 13. Three later owner decisions put the copy behind W2-24, which has 27 dependencies. The WBS card states these conditions, but W2-27's ticket file does not yet list W2-24 or W2-56 among its dependencies. UPIM, ASMO and Release 1 have no dates [A F3, F9].
- Ordinary work: no, because this is a roadmap matter set by owner decisions [A F3].
- Consequence: other. It is a row and an owner decision (P-S8), not a round.

**What works.**
- The guard is live on every call and fails closed on its own errors [D §2.1].
- The close fails closed, and its refusals have shrunk from 14–57 findings a run to one [D §2.2].
- Retrieval repeats exactly on an unchanged index, and answers decision questions by id or by paraphrase [B, What works].
- The scratch channel carries the owner's corrections faithfully: 44 of 45 lead briefs carry DEC-731 and DEC-732 [C §2.0].
- Of the 62 findings in the five reports, none loses work and 52 are "other". Ten fail open. Nine of those ten arise in ordinary work, and each of the nine rides in a ticket that runs anyway, is an owner check, or is an accepted risk (Appendix B; section 7).

**What to do first.**
1. Give this repository a pinned judge, and free the close queue (P-S1, P-S2).
2. Commit the working rules in one owner commit (P-S3).
3. Make the retrieval and memory proofs an entry criterion of EXAMIN's copy (P-S7).
4. Restore a referee outside the machine, and set the products' timeline (P-S9, P-S8).

## 2. A roadmap in phases

The five phases are the steps a version of the Gov OS climbs before it governs a product: build, test, integrate, use on EXAMIN's copy, and adopt EXAMIN's real repository. They follow the ladder that D proposes [D §2.3]. A ticket moves through the phases on its own, so for the Wave as a whole the phases overlap. The gates between them apply to the version that goes to EXAMIN.

**Before the phases: the queue must move.**
- This takes two owner decisions (P-S1, P-S2) and one owner commit (P-S3).
- The pinned judge costs about a day of owner and orchestrator time, plus one CIT-P [D R1].
- Package P-W2-47, which would free the queue, is already written and is on hold [A F1; D F4].
- My estimate: 1 to 3 working days.

**How the estimates are made.** They are in working days, the plan's own unit. They rest on three things.
- *The plan.* About 20.5 working days of critical path, which leaves out owner waits; 21 to 27 working days in all; the copy's verdict near day 13, Track A's near day 14, and the real repository's in days 18 to 23 [A F3; D §2.3, F5].
- *What happened.*
  - At day 4, 1 ticket of 55 has closed, by exception [A F1].
  - Two of the first three critical-path tickets were built within 3.5 days. The plan gave all three about 6.8 days [A, plan against time].
  - Code comes in at about twice its estimate [A F2].
- *The cost of a close.* One close takes one to one and a half hours of a quiet machine. The plan counted about 50 hours of serial close time, which the test cache (W2-48) was to take off the critical path [D F3, F5].

The ranges are my judgement, at low to medium confidence. They assume that P-S1 and P-S2 are decided this week, and that W2-48 starts soon after W2-53 closes [D R3].

| Phase | Exit evidence, in short | Estimate (working days) | Confidence |
|---|---|---|---|
| 1. Build | Each ticket's independent acceptance tests green on its own code; a probe record; a twelve-field return | 8–12 for Track A's remaining tickets, after the queue moves | low–medium |
| 2. Test | W2-24's pinned fixture adoption closes a ticket with `gov close` at exit 0; section 6's proofs met on this repository | 2–4 after Track A's other tickets close | low |
| 3. Integrate | Every Track A ticket closed by a clean `gov close` of the pinned release; a first release cut and pinned; hooks back on; W2-25's audit verdict | runs alongside phase 1; ends 1–2 after W2-24 | low–medium |
| 4. Use on EXAMIN's copy | W2-28's verdict under CAP-44.h, lite | 3–6 after W2-25's verdict | low |
| 5. Adopt EXAMIN's real repository | The owner's go; W2-30's verdict; the rollback shown | 5–10 after the copy's verdict | low |

### Phase 1. Build

- **Covers.**
  - The 41 tickets not yet started [A F1]. About 19 of them are in Track A: W2-04, W2-06 to W2-15b, W2-17, W2-19, W2-21, W2-24, W2-48, W2-56 and W2-57 [A F7; D R1(b)].
  - The fixes that ride along in those tickets (section 7, and Appendix B).
- **Entry.**
  - The ticket's dependencies are closed. W2-27's list misses two of the owner's conditions [A F9].
  - The independent test designer has written the acceptance tests first (MR-3).
- **Exit evidence, for each ticket.**
  - The acceptance tests are green on the ticket's own code. Each command sets `PYTHONPATH` to the worktree, and the lead shows `gov.__file__` (DEC-732) [D F8].
  - A probe record.
  - A twelve-field return (CAP-37.d) [E F2].
  - Every review finding carries the two lines (DEC-808).
- **Estimate.** 8 to 12 working days for Track A's remaining tickets, with three in flight (the cap of DEC-776) [A F8]. The basis is given above.
- **Main risk.** Review rounds: W2-50 has review records for seven runs, and W2-01 had four rounds [A F2]. DEC-801 to DEC-809 now limit them.

### Phase 2. Test

- **Covers.**
  - Each built version is proven on fixtures and the dev tiers *with that version installed*, not through the editable copy [D §2.3, F1].
  - The retrieval and memory proofs of section 6, on this repository [B].
  - W2-24's run. It cuts a release, installs it pinned into a fresh copy of the TypeScript fixture, adopts the fixture, and closes one ticket there with `gov close` [D §2.3].
- **Entry.** W2-24 waits for every other Track A ticket and, in the staged batch, for W2-57 [D §2.3, F5].
- **Exit evidence.**
  - W2-24's close at exit 0 in the fixture, with `gov doctor` and `gov check` green there.
  - No import of this repository's `src/`. That import is W2-24's own failure line [D §2.3].
  - Section 6's measures are met.
- **Estimate.** 2 to 4 working days after Track A's other tickets close. This is my judgement: W2-24's own estimate is not in my sources.

### Phase 3. Integrate

- **Covers.**
  - Every Track A ticket is merged and closed by a clean `gov close` of the pinned release in force (P-S1) [D R1].
  - W2-49 and W2-16 close, and the owner cuts the first release with `gov release` (DEC-772) [D §2.1].
  - W2-18's pinned install, widened to cover this repository [D F1].
  - The git hooks come back (W2-08). `gov doctor`'s hooks check reads what git will actually run [D F6, F7].
  - CI measures the tests [D R6].
  - The plan validator counts only what closed tickets delivered [A F4].
  - The Track A audit, W2-25 [Charter:33].
- **Entry.** The queue moves (P-S1, P-S2).
- **Exit evidence.**
  - Exit criterion 1 is met for every Track A ticket, with no `tk close` [A F1].
  - The validator gives an honest result [A F4].
  - W2-25's audit verdict.
  - `gov doctor` is green on this repository, with a hooks check that looks at git's hooks (exit criterion 3) [D F7].
- **Estimate.** It runs alongside phase 1 and ends 1 to 2 working days after W2-24, with W2-25's audit. Once the cache is in place, closes stop setting the pace. Without it, about 50 hours of serial close time remain [D F5].

### Phase 4. Use on EXAMIN's copy

- **Covers.** W2-26 (the EXAMIN profile, the research leg of EXP-003), W2-27 (the adoption of the copy) and W2-28 (the independent verdict) [Charter:33–34; D §2.1].
- **Entry.**
  - Track A has passed and been audited (W2-25) [Charter:32–34].
  - A pinned, hash-verified release exists [Charter:34].
  - W2-49 has merged, so the copy is judged against Contract 4.2 [C R-4].
  - Research can be launched (P-S6) [E F6].
  - The proofs of section 6. B asks for them "before any adoption" [B].
  - W2-24, W2-56 and W2-57 have closed, as DEC-794, DEC-799 and DEC-813 require. The WBS card states these conditions; they must also be written into W2-27's ticket file, as dependencies [A F3, F9].
  - By DEC-803, the risks that come with running agents in another repository:
    - the kernel's lead rules are brought up to Wave 2 (W2-11) [C F-9];
    - leads are sandboxed under their own role (W2-21), if W2-27 does not list it already [E F1].
- **Exit evidence.** W2-28's verdict is ADOPTED_HEALTHY, or ADOPTED_WITH_ACCEPTED_EXCEPTIONS, against CAP-44.h's lite conditions. These include:
  - `gov doctor` MATCH with the pinned release, and `gov doctor` green;
  - `gov check` with no RED family;
  - one ticket closed by `gov close` at exit 0, with the repository's own test command [CAP-44.h].
- **Estimate.** 3 to 6 working days after W2-25's verdict.
  - The plan put the copy's verdict a day before Track A's (day 13 against day 14) [D §2.3].
  - Three later owner decisions put W2-27 after W2-24 [A F3].
  - The Charter's wording puts the pilot after Track A's audit (P-S8 raises this).

### Phase 5. Adopt EXAMIN's real repository

- **Covers.** The owner's go, the adoption, and W2-30's independent verdict. The freeze and the rollback stay in the owner's hands [Charter:34–35].
- **Entry.**
  - W2-28's verdict.
  - The owner's go before the real repository is written [Charter:34–35], recorded as an owner git fact [ADR-0001:60–62].
  - The hard boundary works: the hooks are on and CI measures [ADR-0001:52–57; D F6].
  - Leads are sandboxed under their own role (W2-21) [E F1].
  - A rollback path: move the pin back [D §2.3].
- **Exit evidence.**
  - W2-30's verdict under CAP-44.h, on the real repository.
  - The owner's go and the pinned release's hash, both in git.
  - The rollback, shown once on the copy before the real repository is written (my proposal).
- **Estimate.** 5 to 10 working days after the copy's verdict, by the plan's own spacing: the copy near day 13, the real repository in days 18 to 23 [A F3].

### Totals, and the other products

**Totals.** Counted from the day the queue moves:
- Track A's verdict comes in about 12 to 21 working days;
- the copy's verdict in about 15 to 27;
- the real repository's in about 20 to 37.

From today, day 4, the plan's own figures leave about 9 working days for the copy and 14 to 19 for the real repository [A F3]. Most of the gap comes from the close queue, and from the work that later decisions put before the copy [A F1, F3; D F5].

**UPIM, ASMO and Release 1.** My sources give no basis for an estimate.
- Every product other than EXAMIN waits for Release 1 [Charter:36].
- Release 1 needs Wave 3 (38 items, no tickets yet) and qualification (CAP-49; title shortened) [A F3].
- DEC-567 makes W2-19's language-agnostic test commands a must-have before the Gov OS is adopted in any non-Python repository [A F3].

P-S8 asks the owner to size Wave 3 at Track A's verdict, and to set a range for Release 1 then.

## 3. The tool staging table

**Stages** (D's definitions) [D §2.1]:
- **Gate:** its refusal stops work (a tool call, a commit, a merge or a close), and its record here shows that it also lets correct work through.
- **Aid:** it is used, and its output informs people and agents. It stops work only through another tool, or not at all.
- **Being built:** it is not yet dependable for its intended use here: unbuilt, uninstalled, or never once passed on this repository.

The table follows D's thirteen tools [D §2.1]. I add `gov doctor`, the plan validator, `gov impact` and the editable install, and I bring in what B, C and E measured.

| Tool | Stage today | Used today as | Evidence | Next stage needs (owner ticket) |
|---|---|---|---|---|
| The editable install (the `gov` on PATH) | The way every tool is delivered | Whatever the main tree holds is what runs, for every bare `gov`, the git hooks, the checks and the dev tiers | DEC-605, after 13 closes failed with "gov: not found" [D §2.2]; there is no `framework.lock` [D F1] | A pinned, non-editable release (P-S1) [D R1] |
| `gov close` | **Being built**, yet used as *the* gate | Every Wave 2 ticket must close through it (exit criterion 1) | 33 logged runs here, none passed; the only clean close ran on the a-dev clone [D F3]; W2-01 was closed by `tk close` [A F1]; one close takes 1 to 1.5 hours [D §2.2]; refusals shrink, from 14–57 findings a run to 1 [D §2.2] | One clean close of a real ticket by a judge that is not the code under judgement (P-S1); the test cache (W2-48) [D F5]; W2-57 (P-S2) |
| The ratchet (`accepted_reds`, `load_sensitive`) | **Being built**, already in force in every close | It decides which reds refuse a close | Merged with W2-53, not closed; it holds 2 accepted reds and 27 load-sensitive entries; owner-only additions (DEC-766) [D §2.1, F4; A F1] | W2-53's close; a remedy for cases that fail only under load (P-S2) [D R2] |
| The guard | **Gate**, with the longest record here | Live on every tool call; fails closed on its own errors | W1-02's four probe records pass [D §2.1]; a broken save of a guard file locks the session that made it, with no reason shown [D F2]; it refused 58 correct SubagentHandback calls [D §2.1; A F7]; each session's guard is its own tree's code [D F1] | A pinned copy (P-S1); reasons on standard error (W2-10) [D R4]; W2-09; W2-42 |
| Containment | **Aid**, by design | It reports out-of-scope changes, and leaves them in place | It misattributes changes in a shared tree [D §2.1]; it rests on self-declared trailers [D §2.1]; it does not see a lead's writes into other trees [E F1]; script writes stay in place [E F4] | W2-44 (trailers bound to the launch identity) [D §2.1] |
| The Claude Code session hooks (start, pre-compaction, stop, subagent stop) | **Aid** | They inject context and write checkpoints | Session start runs only on compaction, clear and resume, and sends leads and the orchestrator to the Wave 1 prompt [E F9]; in a worktree, the stop hook runs the main tree's code [D §2.2]; automatic checkpoints hide the deliberate next step [B F5; E F11] | W2-10 (row W2-M373) [E R8]; DEC-805 in W2-05's resume [E F9] |
| The git hooks (commit checks; pre-push gate G3) | **Being built**: off since 2026-10-15 | Nothing; a test asserts that they are off | Removed after a hook's check wrote foreign commits onto a ticket branch (DEC-710 to DEC-712) [D §2.2, F6] | W2-05, W2-06, W2-08; F-A is an entry criterion of W2-08 (DEC-804) [D F6] |
| CI (G4–G5) | **Being built**: it cannot pass | Nothing during the Wave: nothing is pushed | The tests step is "unmeasured" without pytest on the runner, and the evidence step needs a pre-push note [D F6]; row W2-H002 names three tools for the owner to approve [A §2.1] | Owner approval (P-S9) [D R6] |
| `gov doctor` | **Aid**, relied on as a gate | W2-22, exit criterion 3 and W2-24 count its green | Its hooks check passes with no git hook installed, and it cannot tell an editable or foreign `gov` [D F7] | W2-08's measures; W2-18's or W2-22's measure widened to this repository [D R5] |
| The sandbox | **Aid**, for launched workers only | It holds a worker's shell commands to its own tree | Leads, the orchestrator, hooks and file tools run outside it [D §2.1; ADR-0001:49–51]; scripts write anywhere in their tree [E F4]; the Write tool is refused in the worker's own scratch [E F3]; parallel starts can trip over a git lock [E F17] | W2-56, W2-21, W2-40 [D §2.1; E R3] |
| `gov launch` | **Aid**, becoming the gate for how workers start (DEC-799) | It starts every worker whose suites do not need the code graph | It refuses leads and the orchestrator by design [E F6]; research cannot be launched [E F6]; it loads no role text [E F2]; it passes on the parent's whole environment [E F13]; it does not refuse every flag that drops the guard [E F19]; a worktree's own launcher code builds the sandbox [D §2.2] | W2-21, W2-56 [E R1, R2, R3, R6] |
| `gov check` | **Gate** inside `gov close`; **aid** on its own | 18 declared checks; a red hard-block check refuses a close | Its help text still says running the checks is "not built yet" [D §2.1, F9] | W2-45 (runner semantics); the help text corrected [D R5] |
| Retrieval (`gov retrieve`, the code graph) | **Aid** | It feeds `gov context`; a stale store refuses a close | Any edit to a tracked file switches the index off [B F2]; the code-graph query exceeds its 100,000-row cap [B F3]; register chunks carry the wrong id [B F4]; tests fill the semantic index and the kernel template is not in it [B F6]; the hit@5 figures disagree (Appendix A) | The proofs of section 6; W2-06, W2-13, W2-15a/b, W2-32 [D §2.1; B] |
| Context (`gov context`, the packet) | **Aid**, still being built | Every session-start brief and every close builds it | 42 to 168 times its ceiling, ids and hashes only, reported `ok: true` [B F1]; W2-54's packet holds 950,383 tokens in E's reading and 1,009,095 in B's (Appendix A.3) [E F8; B F1]; it is built from the tree's own copy of the register [E F12] | W2-03, then W2-04 [D §2.1; E R7; B rec. 1] |
| Checkpoints (`gov checkpoint`, automatic checkpoints) | **Aid** | A stale checkpoint refuses a close | Automatic checkpoints hold no state, and all sessions on a ticket share one series [E F11]; numbering has no lock and saves are not atomic [D §2.1]; the orchestrator's own checkpoint is kept by hand, uncommitted [C F-1] | W2-42 (atomic saves); W2-10; B rec. 5 |
| `gov adopt` | **Aid** here; **being built** for product repositories | Stage records for an adoption | `gov adopt --lite` ran on this repository; a-dev reached stage A8, b-dev A2 [D §2.1] | W2-24, W2-23, W2-27 [D §2.1] |
| Releases (`gov release`, `gov update`, the pinned install) | **Being built**: no release has ever been cut | Nothing | `gov release` exists only on `w2/W2-16`, held since 2026-10-17; W2-17 and W2-18 are not started [D §2.1] | P-S1's bootstrap pin; W2-49 and W2-16 closed; the owner cuts the first release (DEC-772); W2-18 [D R1] |
| The plan validator (`validate_w2.py`) | **Aid**, relied on for exit criterion 7 | It prints PASS for "contract-items-delivered" | It counts a ticket's `closes` field whatever the ticket's state, and counts READMEs as acceptance citations [A F4] | W2-51's resume [A F4] |
| `gov impact` (W2-37) | **Being built**, held | Nothing yet | It reads the code graph, which cannot answer [B F3] | "Callers of `rrf` and `indexable` on this repository" as an entry criterion of W2-37's close (DEC-803) [B F3] |

**In short** [D §2.1]:
- One tool is a gate by its record: the guard.
- Three are gates by rule, all inside `gov close`: the close itself, the ratchet and `gov check`. The close and the ratchet have not passed here yet.
- The commit and push gates are off.
- Everything else is an aid, or is still being built.
- The Wave moves at the pace of the gate with the weakest record: `gov close`.

**The staging rule I propose.** It joins D R1, R4 and R5 with S-3. A tool becomes a gate only when four things hold:
1. The copy that judges is a pinned release, not the tree under work [D R1].
2. It has passed correct work on this repository at least once: D's definition of a gate [D §2.1].
3. Its refusals say why, once: AR-6 item 4, "say why, refuse once, then record" [D F2, R4].
4. Its green means that the thing it checks is present [A F4; D F7; B F4].

A tool that meets only some of these is used as an aid, and its result goes to the owner as information, not as a verdict.

**The ladder for each version** [D §2.3]:
1. Build, with tests and review.
2. Prove the version on fixtures and the dev tiers, with that version installed.
3. The owner cuts release N+1 (DEC-772).
4. Install N+1, pinned, on another repository first, and close real tickets there (W2-24's run, repeated for each version).
5. The owner moves this repository's pin from N to N+1, on that evidence.

To roll back, move the pin back.

## 4. The pipeline from the decisions to the Contract, the specifications, the skills and the briefs

### 4.1 What the pipeline should do

Report C sorts decisions into five classes, each with its own landing place [C §2.2]:

| Class | What it is | Where it should land |
|---|---|---|
| B, behaviour correction | Changes how agents act, usually after a mistake or a near miss | A kernel skill, role file or brief template when it holds for every repository; the project prompt or the project briefs when it holds for this repository only |
| S, specification | Fixes what the product does, or how a component behaves | The Contract when it changes a capability, a provider or a wave; otherwise an ADR, a specification, an interface or a schema; in every case, code and tests |
| P, process | Runs this project's work | The plan, the ticket, the residuals record or the run's own records |
| O, owner policy | A standing rule of authority, safety or priority | The Charter, the Contract, an ADR, the role files or the prompt, and the kernel where it binds agents |
| X, superseded | Replaced or settled by a later entry | Its own register entry, marked as such |

### 4.2 What it does today

C drew a systematic sample of 63 of the register's 813 entries [C §2.1].
- **Landing.** 55 reached the place they should, 4 reached it in part, 3 did not, and 1 is not yet due [C §2.0].
- **Specification decisions reach code and tests reliably,** 24 of 26 in the sample. But the Contract stopped:
  - its text took its last decision on 2026-10-04 (DEC-255) [C §2.0];
  - later Contract-level changes went to the machine form only, so three provider lists now differ between the two forms, and the records' "(DEC-614)" names no authority [C F-3];
  - or they went to Contract 4.2, held on a ticket branch, so tickets built to 4.2 sit on a 4.1 integration branch [C F-4].
- **Wave 1's behaviour corrections reached the kernel,** most of them in one promotion (DEC-537, 2026-10-09). The kernel's roles, brief templates and orchestration skill have not changed since. No Wave 2 entry is cited anywhere in the kernel [C §2.0, §2.5].
- **Wave 2's 99 decisions reach agents by four channels** [C §2.5]:
  - 16 through the committed prompt or the project briefs;
  - 9 more through WBS §0 only;
  - 52 only through the orchestrator's scratch briefs;
  - 22 through none of these.
- **The scratch channel works but grows.**
  - 44 of 45 Wave 2 lead briefs carry DEC-731 and DEC-732 [C §2.0].
  - The briefs re-inline the growing rule set: W2-54's lead brief grew from 24,532 bytes in run 1 to 51,275 bytes in run 4c [C §2.6, F-1].
- **Rules that land nowhere an agent reads are not followed.** DEC-140 was followed in 8 of 69 commits, and DEC-062 has no landing at all [C F-6].
- **The register does not show what later entries did to earlier ones.** 134 of its 138 recorded relations are not shown on the earlier entry. 40 entries still read PROPOSED, although all were settled later [C F-5].
- **The committed texts lag the decisions.**
  - The committed prompt contradicts DEC-731, and lacks DEC-732 and DEC-733 [C F-2].
  - The judgement rules exist in two texts, each called "word for word" [C F-8].
  - The kernel still states Wave 1's launch, return and lead-write rules [C F-9].
  - API-0002 names a command source that does not exist [C F-10].
- **Sessions do not load the result.**
  - The role files are Wave 1 texts. The rules sessions are actually given sit in 449 git-ignored briefs [E F2].
  - `CLAUDE.md` names four places that do not exist [E F10].
  - A worker's tree holds the register as it was when its branch was made [E F12].
  - Each skill exists in four copies, and the copy sessions load has no version [E F15].
  - The tool describes itself as less built than it is [D F9; B F13].
- **The planned remedies are fixed lists that already lag.** W2-11's list lacks DEC-802, DEC-803 and DEC-809, and W2-55 has no landing tag [C F-7].

### 4.3 The pipeline proposed

Six stages. Each stage rests on a report's recommendation, except where I mark a proposal of my own.

| Stage | What happens | Who | Rests on |
|---|---|---|---|
| 1. Decide and tag | Each owner decision states its scope (kernel-wide, or this repository only) and a "lands in" tag: skill, role, template, prompt, Contract, specification, plan, or none | The owner, in the entry; W2-55 adds the tag | C R-3 |
| 2. Mark | A later entry that supersedes, settles, corrects, reverses or withdraws an earlier one is shown on the earlier entry at once. Amends and refines follow with W2-55's backfill | The owner's batch; W2-55 | C R-5 |
| 3. Land | This repository's rules go to the committed prompt or a committed common brief, never to scratch only. Kernel-wide rules go to the kernel's role files, skills and templates. Specification decisions go to the Contract (one authoritative form, with the other generated or checked against it) and to code and tests | The owner's edits; W2-11; W2-49's resume | C R-1, R-2, R-4 |
| 3a. Land by release | One CIT-P with each release carries the kernel-wide rules decided since the last release, so that moving the pin also moves the rules | The owner, at each release | My proposal, joining C R-3 with D §2.3 |
| 4. Check | The decisions validator checks that each standing, kernel-wide entry is cited where its tag says. A check compares the Contract's two forms. The plan validator counts only what closed tickets delivered | W2-55; W2-49 or a row; W2-51 | C R-3, R-4; A F4 |
| 5. Load | Each session gets its role text at launch, from the repository, hashed into the launch record. Decisions come as entries from the current register, and the packet names the register commit it used. `CLAUDE.md` is regenerated with the real paths. Each skill has one versioned source | W2-21; W2-03 and W2-04; W2-11 | E R2, R7, R9, R11 |
| 6. Record | Each close records the role text, the brief, the skill versions and the register commit the worker had, so that "what was this worker told?" is answered from git | W2-21's launch record; `gov close` | E R2, R11 |

### 4.4 Who makes each change

| Change | Kind | Where | Rests on |
|---|---|---|---|
| The prompt brought in line with DEC-731 and DEC-799 (the launch form), DEC-732, DEC-733, DEC-738 item 2 and DEC-673; line 1 names the decisions it carries | Owner edit, now | w2 prompt §4 and A5 | C R-1 |
| One canonical judgement text, `JUDGEMENT.md`; A3 carries DEC-801's list of deliberate constructions; WBS §0 rule 18 points to it | Owner edit, in the same commit | prompt; WBS §0 | C R-8 |
| A committed Wave 2 common lead brief, made from the non-ticket parts of `A5-early-template.md`; the stale `LEAD-common.md` deleted; the orchestrator's standing rules moved out of its scratch checkpoint | The owner, or the orchestrator under a recorded decision | `governance/project/briefs/`; the prompt or WBS §0 | C R-2 |
| ADR-0001's status settled | Owner | ADR-0001 | E R2; A F8 |
| `CLAUDE.md` regenerated: the real paths, and seven kinds of session, the lead included | Owner edit now, or in W2-11 | the rulesync source | E R9 |
| W2-11's KPI rewritten as a rule; DEC-801 (with its list), DEC-802, DEC-803 and DEC-809 added; the prompt half listed as an owner edit for W2-11's close record | Before W2-11 starts | W2-11's card | C R-3 |
| The kernel's role files and five brief templates brought up to Wave 2: the twelve fields, the judgement rules, ADR-0001; a kernel auditor brief template | Rides in W2-11 | the kernel | E R2; C R-6 |
| W2-55's "lands in" tag, and the decisions validator's check of it | Rides in W2-55 | W2-55 | C R-3 |
| The Contract's provider lists reconciled; the authoritative form recorded by decision; a check of the two forms; W2-49's merge made an entry criterion of W2-28 and W2-30 | Rides in W2-49's resume; a row if W2-49's paths do not cover the check | W2-49 | C R-4 |
| The register's header corrected; the 14 status-changing relations marked | The owner's next batch | the register | C R-5 |
| DEC-062 and DEC-140 applied or withdrawn | Owner | the register; the orchestration skill | C R-6 |
| The role text loaded at launch and hashed | Rides in W2-21 | the launcher | E R2 |
| The packet built from the current register, naming its commit | Rides in W2-03 and W2-04 | the context code | E R7 |
| One versioned source for each skill; `gov close` records the version loaded | A row for W2-11 or Wave 3 | the kernel; the rulesync output | E R11 |
| The help text and the path map's systems block corrected; each release carries its list of built commands | A row; W2-16 | the CLI; the path map | D R5; B F13 |
| API-0002's command source | A Wave 3 row | `docs/interfaces/` | C R-7 |
| The plan's records repaired: ticket files for W2-55 to W2-57, CAP-44.f in W2-52's `closes`, the LIST's counts, the untriaged rows, the in-flight cap, the ADR statuses and the Charter's front matter | One orchestrator pass | the plan | A F8 |

## 5. The context manifest for each role

A context manifest lists what a session of a role loads at its start, what it may read and write, and what it must not see.

Today the manifest does not depend on the role. Every session loads the same base, and everything specific to its role reaches it through a brief written by hand for each run [E §2, F2]. E measured this by launching one real session per role, except research, which could not be launched [E §2.3].

Below, for each role: what it loads now, the target, and the gap. The targets come from E's recommendations, with B's and C's where they apply.

### 5.1 The base every session loads

**Today** [E §2.1.1]:
- the CLI's own instructions and tool definitions;
- `CLAUDE.md`: 1,986 bytes, naming four places that do not exist [E F10];
- the names of 54 skills, 9 of them the kernel's, and 16 agent types, 6 of them the Gov OS roles. These listings take about 25,000 to 30,000 characters that the project did not write [E F7];
- four cloud connectors, two of them not authorised [E F7];
- a model-side memory folder in the user's home, outside the repository. One folder serves every session of the repository [E F7];
- its brief.

**Not loaded:** the role file, a kernel skill's text, any Contract item, the threat model, any decision [E F2].

**After a compaction**, the session-start hook adds the ticket's decision ids, the ticket list and the ticket's newest checkpoint. For the orchestrator and for leads, it names the *Wave 1* prompt [E F9, F11].

**Target** (E R2, R6, R8, R9; B rec. 5):
- the role's own text, from the repository, at launch, with its hash in the launch record [E R2];
- a corrected `CLAUDE.md` [E R9];
- a cleaned environment; no connectors; no user-level agents or skills; no model-side memory. Each of these is subject to the owner's answers in P-S5 [E R6];
- on resume: the session's own newest deliberate checkpoint with its next step, and the current Wave's prompt [E R8; B rec. 5].

### 5.2 What each role loads

| Role | Role text and brief (target) | Decisions and Contract (target) | Judgement rules | Skills | On resume (target) | Gap today |
|---|---|---|---|---|---|---|
| Engineer | Role text at launch; brief from the committed template (outline A2) plus a run part, hashed | The texts of the items and decisions its ticket cites, by span, within 6,000 tokens, from the current register [B rec. 1; E R7] | Only to answer review findings, which carry the two lines [E §2.2] | change, checkpoint, retrieval, versioned [E §2.2] | Its own next step [E F11] | Rules reach it only through the brief [E F2]; ids, or the whole register [B F1; E F8]; an old register [E F12]; no next step [B F5; E F11] |
| Independent test designer | Role text; outline A1 stating the one read rule the owner chooses (P-S5) | The Contract items behind its KPIs | No | test-design, with its citation corrected to CAP-38.c [E F5] | As the engineer | Three texts give three rules on reading code; it can read the implementation [E F5] |
| Independent auditor, audit form | Role text, with the judgement rules; the committed `AUDITOR-common.md` and `JUDGEMENT.md` (in git since `fecb870c`, for W2-25, W2-28, W2-30 and W2-47) [E §2.2]; a kernel auditor brief template [C R-6] | The audited records; the Contract items and decisions they cite | Yes, for every finding | audit | Its own next step | Read-only only for the Write tool [E F4]; its scratch refused [E F3] |
| Reviewer (auditor role, reviewer form) | As the auditor; outline A3, carrying DEC-801's list of deliberate constructions [C F-8] | The reviewed change and its ticket | Yes | audit | Its own next step | Its brief is written by the lead [E F2]; the Write tool is refused even in its scratch [E F3] |
| Product-spec | Role text; outline A4; the CIT-P/CIT-E steps (CAP-33) | The current register, since it re-baselines the Contract [E §2.2] | No | change, with the skill-version rule | As the engineer | Its tree's register is 77 decision numbers behind [E F12] |
| Research | Role text; its question and KPIs | Its experiment's record | No | none in the kernel [E §2.2] | As the engineer | It cannot be launched [E F6] |
| Ticket lead | Its own role (ticket-lead: DEC-434, DEC-437); A5 of the w2 prompt; a committed common lead brief and its run brief, hashed [C R-2; E R2] | The decisions its ticket cites; §14 | Yes | orchestration | Wave 2's A5, its notes, and its loop count, kept from its workers (DEC-096) [E F5, F9] | It runs as the orchestrator, unsandboxed [E F1]; it is sent to Wave 1's A5 after a compaction [E F9]; its workers can read its notes [E F5]; briefs of about 50 KB that grow with each run [C F-1] |
| Orchestrator | The w2 prompt; its RESUME HERE section injected; the WBS rules and table split so that the start reading is a few thousand tokens [E R8] | The register | §14 | orchestration, planning | The Wave 2 prompt, and its own RESUME HERE | A start reading list of about 400 KB [E F16]; the Wave 1 prompt after a compaction [E F9]; its working memory in an uncommitted scratch checkpoint [C F-1]; its ticket's automatic checkpoints shared with the five assessment sessions [E F11] |

### 5.3 What each role may read and write

| Role | Reads (target) | Writes (target) | Must not | Today, from E's launches |
|---|---|---|---|---|
| Engineer | Its tree, and the records it cites | Its allowed paths, its scratch, its temporary folder | Other trees; the lead's notes; the orchestrator's state | Reads everything except the held-out paths [E F5]; scripts write anywhere in its tree, and it can commit [E F4]; its scratch is refused to the Write tool [E F3] |
| Independent test designer | The specification and KPIs, and the public interfaces if the owner so decides (P-S5) | Its acceptance folder (DEC-769) | The ticket's implementation (MR-3, CAP-38.c) | It reads `src/` [E F5]; scripts write into `docs/`, and `gov checkpoint` writes outside its paths [E F4] |
| Independent auditor | The audited tree and its records | Its audit folder only | Commits, as the owner decides (P-S5) | Scripts write anywhere in its tree, and it commits [E F4] |
| Reviewer | The reviewed tree | Nothing in the repository (CAP-38.f), plus a scratch to work in | Commits | The Write tool is refused even in its scratch [E F3]; scripts write, and it commits [E F4] |
| Product-spec | Its tree and the current register | Its paths, for example `docs/contract/capabilities/` | — | As the engineer [E F3, F4] |
| Research | Its experiment folder; the hosts it needs | Its experiment folder; a clone of the project it studies, in W2-50's run folder [E F6] | The rest of the tree | It cannot be launched [E F6] |
| Ticket lead | Its ticket, its WBS row, the decisions it cites, its worktree | Its scratch and briefs; merges; the probe record under `docs/probes/<ticket>/` (DEC-733) | `.tickets/`, the register and `bootstrap.md` (DEC-236); other trees | It writes `.tickets/` and other trees, and the writes into other trees go unrecorded [E F1] |
| Orchestrator | Wide, by design (DEC-156) | Wide, by design | — | As designed; the leads inherit it [E F1] |

### 5.4 Budgets

- **The packet.** Ceiling 6,000 tokens (DEC-004) [C §2.5; B F1]. Today it is 42 to 168 times the ceiling, and carries no text [B F1].
- **The session-start injection.** It must fit the hook's size cap [CAP-37.g].
- **The orchestrator's start reading.** About 400 KB today. Its target is a few thousand tokens, by injecting the RESUME HERE section and splitting `bootstrap.md` and the WBS [E F16, R8].
- **The lead briefs.** About 50 KB each today, because each run re-inlines the rule set [C F-1]. With a committed common brief (P-S3), a run brief needs only the ticket's own part.

## 6. The retrieval and memory work that must be proven before any adoption

**Why this comes before adoption.** The Charter makes the repository the authoritative memory. Agents reach that memory through retrieval and the context packet [Charter:19–22].
- B measured retrieval on this repository with twenty real questions [B].
- In B's words, retrieval works today "only for a freshly rebuilt index and a question asked in the right words" [B, What works].
- B asks that its findings F1 to F6, and the check in F7, be fixed before any adoption [B, What works].
- A, D and E add the supply side: the packet, the register copy, and resume [A F7; D §2.1; E F8, F11, F12].

**What already works** [B, What works]:
- exact repeatability on an unchanged index: 20 of 20 answers byte-identical, and the ten packets' hashes identical;
- decision lookups by id or by paraphrase;
- honest facets in `gov retrieve`;
- bundles within their budget at radius 0 and 1;
- a small rebuild's lexical step in under a second;
- the orchestrator's RESUME HERE section survives a compaction.

**What must be proven.** The measures and pass lines below are the reports' where they give one. Where they give none, the owner sets them (P-S7). "Phase 4" means an entry criterion of W2-27, the adoption of EXAMIN's copy (DEC-803).

| # | What must be proven | Measure and pass line | Today | Owner ticket | Gates |
|---|---|---|---|---|---|
| 1 | The packet carries decision text within its ceiling, or refuses | B's ten packets measured again: each within 6,000 tokens, each mandatory decision's own entry text present, and `ok: false` when over the ceiling [B rec. 1; E R7] | 42 to 168 times the ceiling, ids and hashes only, `ok: true` [B F1]; W2-54's packet, 950,383 tokens [E F8]; 814,821 tokens at Wave 1's exit [B F1; D §2.1] | W2-03, then W2-04 (AR-1), with W2-04's KPIs widened [B rec. 1] | Phase 4 |
| 2 | The packet comes from the current register | The packet names the register commit it used, and that commit is `w2/integrate`'s [E R7] | Worker trees hold registers 40 to 83 entries behind [E F12] | W2-03, W2-04 | Phase 4 |
| 3 | Retrieval stays on while agents edit | After an edit to one tracked file, unchanged files are still served and the changed file is listed as a gap; a stale index is named in `dropped` and in the brief [B rec. 1, rec. 2] | Any edit switches the whole index off, and `gov context` hides the loss [B F2] | W2-06, its KPIs widened to uncommitted edits [B F2] | Phase 4 |
| 4 | Superseded decisions are marked and kept out | Each register chunk carries its own entry's id, and the must-not-cite filter keys on it. B's question Q05 is the test [B rec. 4] | Every register chunk carries the id DEC-812, and DEC-049, which is superseded, is served at rank 4 (fails open) [B F4] | W2-32, or W2-03 widened [B F4] | Phase 4 |
| 5 | A resume keeps the next step | CAP-37's acceptance: a fresh session with only the session-start output resumes the ticket at the recorded next step. Shown for a worker, a lead and the orchestrator, with automatic checkpoints kept per session [B rec. 5; E R8, F11] | After one compaction, the deliberate next step is shadowed by "Resume after compaction"; one checkpoint series is shared by every session on a ticket [B F5; E F11] | W2-10 (row W2-M373), and the checkpoint code | Phase 4 |
| 6 | The kernel template is searchable, and tests do not crowd out the governing files | The template is embedded; tests get their own facet or a lower weight; a question about a role, hook or skill returns the governing file [B rec. 6] | Tests hold 78 % of the vectors, and the template holds none [B F6] | Row W2-L253, raised; the owner names a ticket | Phase 4 |
| 7 | No held-out or export-denied file is indexed | The owner, or the orchestrator, checks each held-out path in the lexical index and in the code index's file copies; `gov.secrets.indexable` excludes held-out and export-denied paths [B rec. 7] | Unknown: B could not check (it fails open if such a file is indexed) [B F7] | The check now; the code change in a ticket the owner names | Now, and phase 4 |
| 8 | The code graph answers callers, callees and impact | "Callers of `rrf` and `indexable` on this repository" are answered, and the tool's own error text is passed through [B rec. 3] | The query exceeds the tool's 100,000-row cap (117,373 edges), and the cause is dropped [B F3] | An owner whose paths include `src/gov/codeintel/**`; an entry criterion of W2-37's close (DEC-803) | Phase 4, as B asks; and W2-37's close |
| 9 | A standing measure of quality | B's 20 questions, with their gold answers, run at each release: the governing source in the first five and in the bundle; repeatability on an unchanged index and after a rebuild [B rec. 12] | First five, 13 of 20; in the bundle, 17 of 20; identical runs, 20 of 20 unchanged and 11 of 20 after a rebuild [B] | The owner sets the pass lines (P-S7) | Each release |
| 10 | hit@5 against the Contract | The owner decides CAP-10's line: keep the Contract's 85, or re-baseline to the 80 that W1-21's and W2-54's tests use [A F7; D §2.1; B] | 83.33 [A F7]; 81.67 [D §2.1]; 65 % on B's set [B]; see Appendix A | W2-15a and W2-15b (EXP-003); W2-32 | W2-15a's and W2-15b's measures, with the line set first (P-S7) |
| 11 | The lexical route and the reranker earn their place | W2-13 built; the reranker shown to help on the standing set; with `--ticket`, the ticket's own front matter comes first [B rec. 8] | The lexical route matches a whole question as one exact string [B F8]; with the reranker, the mean reciprocal rank (the average over questions of one divided by the rank of the first right answer) falls from 0.45 to 0.40 [B F9] | W2-13, W2-32 | Measured in phase 4; phase 5, under P-S7's (b) |
| 12 | Reads survive a rebuild | A named, retryable error during a rebuild; the session-start hook says when the brief is missing [B rec. 9] | A wrong error code, or a traceback [B F10] | A row | Phase 5, under P-S7's (b) |
| 13 | Rebuilds are reproducible | Content-based chunk ids, or the CPU embedder for the index; the rebuild digest covers the indexes [B rec. 10] | Only 14 of 32 vectors are bit-identical after a rebuild; whole files are re-embedded [B F12] | W2-04's reproducibility KPI | Phase 5, under P-S7's (b) |
| 14 | The working memory stays in the repository | A lead's scratch records are copied before its worktree is removed; the orchestrator's standing rules are committed; governed sessions keep no model-side memory, if the owner so decides [E R2; C R-2; E F7] | A lead's records go with its worktree unless someone copies them (not checked) [E F2]; the orchestrator's working memory is uncommitted [C F-1] | The owner (P-S3, P-S5) | Phase 4 |

**On EXAMIN's copy** (my proposal). All the measures above were taken on this repository. EXAMIN's copy is a different codebase, and the index mix will differ there (here tests hold 78 % of the vectors [B F6]). So W2-27 should repeat rows 1, 3, 4, 5 and 9 on the copy, with a question set for EXAMIN. The owner, or a session independent of the adopting team, writes that set.

**Gate or aid.** Retrieval and context are aids, not gates [D §2.1]. Most of the risk is wrong or missing context, not an opened gate [B F1, F2]. Rows 4 and 7 are the exceptions, because they can fail open [B F4, F7].

## 7. The owner decisions needed

Each package stands alone, in six parts:
1. the context;
2. what happened;
3. why it matters;
4. the options;
5. the recommendation;
6. what it blocks, and what waiting costs.

In part 5, the classification of the findings comes first, on one line (DEC-809). **No package proposes a review round.** Each change rides in a ticket that runs anyway (DEC-802), is an owner edit, or is a row.

The packages are ordered by what they unblock:

| Package | Question | Recommendation, in short |
|---|---|---|
| P-S1 | Which version of the Gov OS governs this repository? | A pinned release, made by hand now |
| P-S2 | How does the close queue move again? | Decide P-W2-47; take load out of the close through W2-57; start the cache early |
| P-S3 | Where do Wave 2's working rules live? | In git, in one owner commit, now |
| P-S4 | How do decisions reach the kernel and the Contract? | By tag and check, not by fixed list |
| P-S5 | What does each role load, read and write? | The role is loaded at launch; writes follow the role; launches inherit less |
| P-S6 | How is research launched? | One experiments folder per research ticket |
| P-S7 | What must memory prove before EXAMIN? | Section 6, as an entry criterion of W2-27 |
| P-S8 | When do the products come, and how big is the Gov OS allowed to be? | Write the owner's conditions into the plan; review the size; defer the eight roles by decision |
| P-S9 | Who referees outside the machine? | Approve the CI tools; make doctor see the hooks |

### P-S1. Govern this repository by a pinned release, not by its own working tree

**1. Context.**
- The `gov` command on PATH is an editable install of this repository's main tree. The owner made it on 2026-10-10 (DEC-605), after 13 closes had failed with "gov: not found" [D §2.2].
- Each session's hooks also run code from that session's own tree [D §2.2]. So the Gov OS that governs this repository is whatever its working copy holds at that moment.
- The plan says so in terms: W2-01 "is itself closed with `gov close` once merged, because `gov` runs from this repository's `src/`" (WBS §0 rule 1) [D F1].
- The pinned install, W2-18, is planned for product repositories only [D F1].
- The Charter's "bootstrap, then dogfood" (DEC-084) does not say which version does the judging [D F1].

**2. What happened.**
- None of the 33 logged `gov close` runs on this repository passed. The one clean close ever ran on the a-dev clone [D F3].
- A ticket that changes the close is judged by its own change, after the merge (DEC-757 item 4) [D F4].
- W2-01's close refused with six findings, none of them W2-01's work, and the owner closed it with `tk close` [D §2.2; A F1].
- A broken save of a guard file locks the session that made it, the repair included, and shows no reason. This happened in Wave 1, and again in W2-50's worktree [D F2].
- In a worktree, a bare `gov` runs the main tree's code while the guard runs the worktree's. A rule written into every brief by hand keeps verification honest (DEC-732) [D F8].
- No release has ever been cut. W2-16's `gov release` has been held since 2026-10-17, and this repository has no `framework.lock` [D §2.1].

**3. Why it matters.**
- *Safe and governed.* A judge that changes with the work it judges cannot give a stable verdict. A guard ticket's half-finished guard could also be more permissive than the last good one, though D found no instance [D F1].
- *The owner in control.* The self-judging loop has brought the owner exceptions and ratchet entries to decide [D F4].
- *Products.* EXAMIN must run "a pinned, hash-verified release" [Charter:34], and nothing has been pinned anywhere yet [D §2.1].
- *Memory.* A pinned version also names what ran, which the loaded skill copies cannot do today [E F15; D R5].

**4. Options.** Three, by DEC-105, because the change contradicts WBS §0 rule 1 and the wording of exit criterion 1 [D R1].

- **(a) Apply now. This is D's recommendation** [D R1(a), §2.3].
  - *What is done:*
    1. The owner builds a "bootstrap pin": a wheel from a commit that holds W2-53's ratchet (`fecb870c` qualifies). Its sha256 is recorded in the tool registry, and it is installed non-editable, in its own environment, on PATH in place of the editable install.
    2. The hook command lines call that environment.
    3. DEC-732's per-command `PYTHONPATH` stays, and now chooses only the code under test.
    4. Exit criterion 1 reads "a clean `gov close` by the pinned release in force".
    5. W2-16 closes under the bootstrap pin, and the owner cuts the first release (DEC-772).
    6. Each later version climbs the ladder of section 3.
  - *Consequence:* it removes the moving judge, the guard's self-lock for this repository, and the cause of the two-versions rule [D §2.3].
  - *Cost:* about a day of owner and orchestrator time, plus one CIT-P [D R1].
  - *Risk:*
    - a ticket that changes a format the judge reads needs a release that accepts the new format first;
    - the change to the hook lines may turn W1-38's hook-source tests red. This is unmeasured, so the test designer checks it first (MR-3) [D R1].
  - *What it changes:*
    - DEC-605 and WBS §0 rule 1 are replaced, and exit criterion 1 is reworded;
    - W2-18 is widened to this repository: its KPI and its paths;
    - the hook source and the settings generated from it change, an owner change under CAP-33;
    - the briefs keep DEC-732, with its stated reason corrected [D R1, F8];
    - no Contract item changes, since CAP-43.b already allows a pinned, unsigned Wave 2 release.
- **(b) Defer to W2-18, widened to this repository** [D R1(b)].
  - *Consequence:* the current method stays until W2-16, W2-18 and W2-24 close.
  - *Cost:* sixteen tickets that change the close, the guard, the hooks, the checks or the launcher go on being judged or guarded by their own unfinished code [D R1(b)].
  - *Risk:* the loop of D F3 to F5 continues for the rest of Track A.
  - *What it changes:* W2-18's card only.
- **(c) Re-baseline: move exit criterion 1's proof off this repository** [D R1(c)].
  - *What is done:* this repository's tickets close on tests, independent review and the owner's merge; the clean `gov close` is proven on the fixture and on EXAMIN's copy, with a pinned release.
  - *Consequence:* the queue clears fastest.
  - *Cost:* the lowest now.
  - *Risk:* this repository's dogfooding signal is lost, and the guard's self-lock remains [D R1(c)].
  - *What it changes:* exit criterion 1 and AR-8.

**5. Recommendation.**

Classification (DEC-809): D F1 yes/other · D F2 yes/other (fails closed) · D F4 yes/other · D F5 yes/other · D F8 yes/fails open (a worktree's own verification only; owned by W2-21). No round.

Option (a), in two steps:
1. This week, the bootstrap pin on PATH. Every close, every check and every bare `gov` then runs a fixed version.
2. The hook command lines, once the test designer has checked W1-38's tests.

The split is mine; D's steps are the same. Confidence: medium-high for step 1, and medium for step 2, whose effect on the tests is unmeasured.

**6. What it blocks, and what waiting costs.**
- *Undecided, it holds:* the self-judging half of the close queue, the guard's self-lock and the two-versions rule [D R1].
- *Waiting costs:* the loop of D F3 to F5 for sixteen tickets [D R1(b)]. And EXAMIN's first pinned release reaches the copy without ever having governed this repository.

### P-S2. Free the close queue, and stop one timing test from holding every close

**1. Context.**
- Every Wave 2 ticket must close through a clean `gov close` (exit criterion 1) [A F1].
- A close runs about 13,500 tests in one to one and a half hours, and needs a quiet window (DEC-780) [D F3].
- Since 2026-10-18 the ratchet's two lists only shrink, and any addition comes to the owner first, as a package (DEC-766) [D F4].
- Package P-W2-47 proposes one such addition. It is on hold [A F1; D F4].

**2. What happened.**
- W2-53's re-close at 12:01 on 2026-10-19: 13,454 tests passed and 3 failed [A F1; D F4]. Two of the three are the accepted reds. The third is W1-30's time-limit case, which passes alone: three of three passes, 17.8 s, with a 2 s reaping margin. D ran it again: 17.36 s.
- A re-close without a change would be a forbidden retry of the ratchet [A F1; D F4].
- Thirteen tickets wait in DEC-806's close order [A F1].
- Load here is normally 22 to 30, and a sibling case and 23 W1-46 cases already sit in `load_sensitive` for the same reason [A F1; D F4].
- The plan costed closes at about 7 hours over layers 1 and 2. One re-close spent about 59 minutes in its tests alone [A F1; D §2.2].
- The test cache, W2-48, was to take most of about 50 hours of serial close time off the path. It has not started, and it waits behind W2-21 [D F5].

**3. Why it matters.**
- Nothing in Wave 2 counts as delivered until it closes [A F1].
- Single test cases use up the owner's attention (S-4) [A F2].
- The products wait behind the queue [A F3].

**4. Options.**
- **(a) Decide P-W2-47 as proposed** [D R2; A F1].
  - *What is done:* the owner adds the W1-30 case to `load_sensitive` by its exact id, with its fix row, and widens W2-57 to settle the cause: the test's timing, or the close leaving a process alive under load.
  - *Consequence:* W2-53 can close again. The case still counts only if it passes in an isolated re-run inside the same close (DEC-757 item 3) [D F4].
  - *Cost:* one owner commit.
  - *Risk:* if the close really leaves a process alive under load, the entry hides that until W2-57 settles it. The quiet window keeps the in-close re-run honest (DEC-780) [D R2].
  - *What it changes:* the path map's list, and W2-57's card.
- **(b) Take load out of the close** [A rec. 1].
  - *What is done:* the resource gate is applied to the close itself, or the timing-sensitive cases run as their own isolated suite.
  - *Consequence:* no single timing case holds the queue again.
  - *Cost:* a change to `gov close`, judged by the pinned close under P-S1.
  - *Risk:* the isolated suite must still be a real check.
  - *What it changes:* W2-57's scope, and the close's specification.
- **(c) A standing rule** [D R2].
  - *What is done:* a test that fails only in the parallel regression, and passes alone three times in a quiet window, may be added provisionally by the orchestrator, by its exact id and with its fix row. The owner ratifies or removes it in the next batch.
  - *Consequence:* the owner leaves this routine path.
  - *Cost:* it reverses DEC-766's "package first" for this one class.
  - *Risk:* drift, a list that grows by habit [D R2].
  - *What it changes:* DEC-766.
- **(d) Wait.**
  - *Consequence:* thirteen tickets stay held, and exit criterion 1 cannot be met.

Whichever option is taken, change the close order too [D R3; A rec. 1]:
- after W2-53 and W2-54, close W2-51, W2-49 and W2-16 ahead of W2-02, W2-03 and W2-20;
- start W2-48 as soon as W2-53 closes.

**5. Recommendation.**

Classification (DEC-809): A F1 yes/other (fails closed) · D F3 yes/other · D F4 yes/other. No round.

- **(a) now.** High confidence that this is safe, since the case must still pass inside the close [D F4].
- **(b) as W2-57's widened scope.** Medium confidence.
- **Not (c), for now.** DEC-766 is a day old, and (b) removes the cause. Revisit it if a second case holds the queue. Medium confidence.
- **The close order and an early W2-48, as D R3 proposes.** Medium-high confidence.
- **Report the close success rate in the countdown** [A rec. 1].

**6. What it blocks, and what waiting costs.**
- *It blocks:* W2-53's re-close and every close behind it, thirteen tickets [A F1]; exit criterion 1; and W2-48.
- *Waiting costs:* each day of waiting is a day lost from a critical path that already leaves owner waits out of its count [D F5].

### P-S3. Commit Wave 2's working rules

**1. Context.**
- The owner's rules for Wave 2's agents are decided in the register. They reach agents through three channels: the committed w2 prompt, WBS §0, and, for most of them, the orchestrator's scratch briefs, which git ignores [C F-1].
- The judgement rules were committed on 2026-10-19, for four audit tickets only [E F2].
- `CLAUDE.md` is the only governance text that every session loads [E F10].
- ADR-0001, against which every finding is judged, still reads PROPOSED [A F8; E F2].

**2. What happened.**
- Of the 15 standing entries that W2-11's KPI names, 2 are in the prompt, 3 are in WBS §0 only, and 10 are in neither [C F-1].
- The orchestrator's working memory sits in an uncommitted scratch checkpoint, for example DEC-780 [C F-1].
- The committed prompt [C F-2]:
  - contradicts DEC-731;
  - lacks DEC-732 and DEC-733;
  - still reads "(v1, as approved: DEC-720 to DEC-729)" on line 1.
- The judgement rules exist in two texts, each called "word for word" [C F-8].
- The kernel still states Wave 1's launch, return and lead-write rules [C F-9].
- Sessions are given 449 git-ignored briefs, the largest 51 KB [E F2].
- `CLAUDE.md` names four places that do not exist, and leaves out the lead [E F10].

**3. Why it matters.**
- *Purpose 1.* The working memory sits in scratch. A cleaned folder or a removed worktree loses it [C F-1; E F2].
- *Safe and governed.* An orchestrator started from a fresh clone follows A5 as written, and A5 contradicts DEC-731 [C F-2].
- *Products.* The kernel that EXAMIN will receive lacks Wave 2's rules [C F-1, F-9].

**4. Options.**
- **(a) Apply now, in one owner commit** [C R-1, R-2, R-8; E R2, R9].
  - *What is done:*
    - the prompt's §4 and A5 follow DEC-731 and DEC-799, and add DEC-732, DEC-733, DEC-738 item 2 and DEC-673; line 1 names the decisions the prompt carries;
    - `JUDGEMENT.md` becomes the one canonical judgement text, and A3 carries DEC-801's list of deliberate constructions;
    - a committed Wave 2 common lead brief replaces the scratch template's common parts, and the stale `LEAD-common.md` goes;
    - the orchestrator's standing rules move into the prompt or WBS §0;
    - `CLAUDE.md` is regenerated with the real paths and seven kinds of session;
    - ADR-0001 is accepted.
  - *Consequence:* an orchestrator or lead started from git follows the owner's current rules.
  - *Cost:* one owner edit. Most of the text exists already, in the scratch template [C R-1]. The `CLAUDE.md` fix is a change to its rulesync source [E R9].
  - *Risk:* low. The briefs already carry these rules (44 of 45) [C §2.0].
  - *What it changes:* the prompt, the project briefs, WBS §0, `CLAUDE.md`'s source and ADR-0001's status. No kernel text changes; that is P-S4 and W2-11.
- **(b) Defer to W2-11.**
  - *Consequence:* the rules stay in scratch until W2-11. W2-11 waits behind W2-10 and W2-09, and its fixed list already lags [C F-7].
  - *Cost:* nothing now.
  - *Risk:* a cleaned scratch folder or a fresh clone loses the rules.
- **(c) Re-baseline: accept scratch as Wave 2's channel, and copy the briefs into git at each close** [E R2].
  - *Consequence:* a record exists, but the committed prompt still contradicts the decisions.
  - *Cost:* low.
  - *Risk:* the prompt stays wrong.

**5. Recommendation.**

Classification (DEC-809): C F-1 yes/other · C F-2 yes/other · C F-8 yes/other · C F-9 yes/other (an entry criterion, by DEC-803) · E F2 yes/other · E F10 yes/other. No round.

- **(a)**, high confidence.
- **From now on, commit the briefs actually given with each close, or hash them into the launch record** [E R2]. Medium-high confidence.

**6. What it blocks, and what waiting costs.**
- *It blocks:* nothing directly. It protects the rules from loss.
- *Waiting costs:* each new decision lands in scratch only, as 52 of 99 already have [C §2.5]. And each run's brief re-inlines more: W2-54's grew from 24.5 KB to 51 KB [C §2.6].

### P-S4. Make decisions land by rule, and keep the Contract and the register true

**1. Context.**
- C followed a sample of 63 decisions to where they landed. 55 reached the place they should [C §2.0].
- Wave 1's behaviour corrections reached the kernel through one promotion (DEC-537, 2026-10-09). Since then, the kernel's roles, templates and orchestration skill have not changed [C §2.0].
- The Contract's text has taken no decision since 2026-10-04 [C §2.0].
- Two remedies are planned: W2-11, a fixed list of standing rules for the kernel, and W2-55, a backfill of the register [C F-7].

**2. What happened.**
- The Contract's two forms disagree on three provider lists. The records call one form the authority "(DEC-614)", but DEC-614 names none, and the tools read the YAML [C F-3].
- Contract 4.2 is held on a ticket branch, so W2-02 is built to 4.2's lite form on a 4.1 branch [C F-4].
- 134 of 138 relations between entries are not shown on the earlier entry. 40 entries read PROPOSED, and the register's header is stale [C F-5].
- Rules with no landing are not followed:
  - DEC-140 was followed in 8 of 69 commits;
  - DEC-062 has no landing, and `gh` is used in five install commands [C F-6].
- W2-11's list already lacks three standing rules, and the half of its KPI that concerns the prompt is outside its allowed paths [C F-7].
- Each skill exists in four copies, and the copy sessions load carries no version [E F15].

**3. Why it matters.**
- *Purpose 1.* An agent that finds an entry may apply a rule a later entry replaced [C F-5].
- *The owner in control.* Two of the owner's rules are not followed [C F-6].
- *Products.* EXAMIN receives what this pipeline puts into the kernel, and today that is Wave 1's text [C F-1, F-9].

**4. Options.**
- **(a) Apply, in the tickets that run anyway** [C R-3, R-4, R-5, R-6; E R11].
  - *What is done:*
    - Before W2-11 starts, its KPI becomes a rule a check can enforce: every kernel-wide standing entry is stated, with its id, in the kernel file it binds, and every entry scoped to this repository is in the prompt or the project briefs. DEC-801 (with its list of deliberate constructions), DEC-802, DEC-803 and DEC-809 are added. The prompt half is an owner edit that W2-11's close record lists.
    - W2-55 adds a "lands in" tag, which the decisions validator checks.
    - W2-49's resume adds the missing providers, records by decision which form is the authority, and adds a check that compares the forms, or generates the readable form from the YAML.
    - W2-49's merge becomes an entry criterion of W2-28 and W2-30.
    - The owner's next batch marks the 14 relations that change what stands, and corrects the register's header.
    - The owner applies or withdraws DEC-062 and DEC-140.
    - Each skill gets one versioned source: a row for W2-11 or for Wave 3.
    - From the first release on, one CIT-P per release carries the kernel-wide rules decided since the last release (my proposal).
  - *Consequence:* the gap between a decision and the kernel becomes something a check can find.
  - *Cost:* the work rides in W2-11, W2-49 and W2-55 (DEC-802), plus two owner edits.
  - *Risk:* W2-11 waits behind W2-10 and W2-09, and W2-55 behind W2-03 [C F-7].
  - *What it changes:* the KPIs of W2-11 and W2-55; possibly W2-49's paths, or else a row [C R-4]; the register; the orchestration skill, if DEC-140 is applied.
- **(b) Defer to Wave 3's kernel pass.**
  - *Consequence:* EXAMIN receives a Wave 1 kernel.
  - *Cost:* nothing now.
  - *Risk:* in an adopted repository, a lead that follows the kernel's brief meets the refused probe gate that led to DEC-733 [C F-9].
- **(c) Re-baseline: the project prompt and briefs, not the kernel, carry the standing rules until Release 1.**
  - *Consequence:* honest about today's practice.
  - *Risk:* every adopting repository starts without Wave 2's rules [C F-1].

**5. Recommendation.**

Classification (DEC-809): C F-3 to F-7 yes/other · E F15 yes/other. No round.

- **(a)**, medium-high confidence.
- **The CIT-P with each release** (my proposal): medium confidence.

**6. What it blocks, and what waiting costs.**
- *It blocks:* W2-28 and W2-30 should not start before W2-49 merges [C R-4], and W2-11 should not start with its old KPI [C R-3].
- *Waiting costs:* every new standing rule widens the gap, until someone extends the list by hand [C F-7].

### P-S5. Decide what each role loads, reads and writes

**1. Context.**
- The Charter makes each role "a subagent definition generated by rulesync from kernel role files" [E F2].
- `gov launch` starts a worker with its role's settings, inside the sandbox [D §2.1].
- E launched one real session per role, and recorded what each loaded, read and wrote [E §2.3].

**2. What happened.**
- No session loaded its role text [E F2].
- The Write tool is refused in a worker's own scratch, because the CLI reads the launcher's deny patterns the wrong way round [E F3].
- Scripts write anywhere in the tree, and every role can commit, the auditor included [E F4].
- Reads are open everywhere except the held-out paths. Three texts give the test designer three different rules, and a lead's loop count is visible to its workers [E F5].
- Every session carries context the Gov OS does not govern, including a model-side memory outside the repository [E F7].
- The launcher passes on the parent session's whole environment [E F13].
- The model a subagent runs on is not the one recorded, and no launch has to name a model [E F14].
- The launcher does not refuse every CLI flag that drops the guard [E F19].

**3. Why it matters.**
- *Independence.* Independent test authorship (MR-3, CAP-38.c), the read-only audit (MR-4) and "the reviewer writes nothing to the repository" (CAP-38.f) rest on brief text alone [E F4, F5].
- *Purpose 1.* The Charter says the memory "never lives in an agent session or a vendor account" [Charter:20–22]. A model-side memory folder outside the repository works against that, and against MR-5 [E F7].
- *The owner in control.* The record of which model did the work can be wrong [E F14].

**4. Options.** Six questions for the owner. Under each, the options are E's unless marked.
- **Q1. Load the role at launch?**
  - (a) Yes: `gov launch` appends the role file's text (`--append-system-prompt`) or starts the role's generated agent (`--agent`), and W2-21's launch record holds the text's hash and version [E R2].
  - (b) No: keep briefs alone.
- **Q2. What may the test designer read?** [E R4; E F5]
  - (a) The specification and the KPIs only, with a read deny on `src/` (the skill's rule).
  - (b) The specification, the KPIs and the public interfaces of the code it must call, but no private part of an implementation (the template's rule).
  - (c) The existing code it must work with (A1's rule).
  - *Cost:* the three texts become one; option (a) adds one read rule to the launcher.
  - *Risk:* (a) may starve tests of what they must call in existing code; (c) weakens independence.
- **Q3. Writes** [E R3].
  - Fixed in W2-56 whatever the owner decides: the `.gov-runtime` patterns, and a write list that follows the acting role, not the ticket's field, proven by a live launch.
  - Two choices for the owner: may an auditor or a reviewer commit (MR-4)? And does `docs/checkpoints/<ticket>/` belong to every role?
- **Q4. Workers' reads.** Deny reads of the main repository's `.gov-runtime/`, of other worktrees, and of the lead's notes [E R4].
- **Q5. What a launch inherits** [E R6].
  - A cleaned environment.
  - No connectors (the switch is `--strict-mcp-config`, untested on claude.ai connectors).
  - Whether user-level agents and skills belong in governed sessions.
  - Whether governed sessions keep a model-side memory.
  - The remaining flags that drop the guard or add context are refused.
- **Q6. The model** [E R10].
  - A launch must name its model (W2-21's KPI), and the launch record holds the models actually used.
  - Does DEC-460's subagent model still stand?

**5. Recommendation.**

Classification (DEC-809): E F1 yes/fails open (owned by W2-21; a row under DEC-779) · E F4 yes/fails open (detected; owned by W2-56) · E F2, F3, F5, F7, F13, F14 yes/other · E F19 no/fails open (untested): a Wave 3 row, or one line in W2-56. No round.

- **Q1: (a).** High confidence.
- **Q2: (b), the template's rule.** Enforce it by order: no test-design session on a tree that already holds the ticket's implementation, shown in W2-21's launch record. Correct the skill's citation to CAP-38.c. This is my choice among E's options; E leaves it to the owner. Medium confidence.
- **Q3:**
  - reviewers and auditors commit nothing, and the orchestrator commits an auditor's report, as it does for this assessment;
  - `docs/checkpoints/<ticket>/` belongs to every role, one subfolder per session, which also mends E F11.
  - Medium confidence.
- **Q4: yes.** Medium-high confidence.
- **Q5:**
  - launched workers get a cleaned environment, no connectors, no user-level agents or skills, and no model-side memory (MR-5): medium-high confidence;
  - the flags are refused in W2-56: medium confidence.
- **Q6: require and record the model, and restate the subagent model.** High confidence.

**6. What it blocks, and what waiting costs.**
- *It blocks:* W2-21 and W2-56 have not started, and should carry these KPIs from their start (DEC-802) [E R1, R3]. W2-26's research worker also needs P-S6.
- *Waiting costs:* every launch until then runs with these gaps, and the leads' fail-open stays a row until W2-21 lands [E F1].

### P-S6. Make research launchable before W2-26 resumes

**1. Context.**
- DEC-799 requires every worker whose suites do not need the code graph to start through `gov launch` [E F6].
- The launcher accepts a research ticket only when its allowed paths are exactly one folder `experiments/<name>/**` (DEC-242, DEC-273) [E F6].
- W2-26 is EXAMIN's research leg (EXP-003), and it is on the path to the copy [E F6; D §2.1].

**2. What happened.**
- E's research launch was refused: "the research ticket's allowed_paths names a folder that is not under the experiments root" [E F6].
- None of the four Wave 2 research tickets passes the rule [E F6]:
  - W2-26 names `docs/research/EXP-003/examin/**`;
  - W2-40, W2-15a and W2-15b each name two folders.
- W2-26's earlier workers ran unsandboxed, with `GOV_ROLE=research` [E F6].
- W2-26 works on a clone in `/tmp` until W2-50 lands. How a project names another experiments root (DP-18) is undecided [E F6].

**3. Why it matters.**
- *Products.* The EXAMIN research leg stops, or becomes a LAUNCH_BLOCKED stop for the owner [E F6].
- *Safe and governed.* Without a fix, research stays unsandboxed [E R5].

**4. Options.** Three, by DEC-105 [E R5].
- **(a) Apply now.**
  - *What is done:* re-scope the four tickets to one folder each, `experiments/EXP-00n/**`, and move the evidence record there.
  - *Cost:* four ticket edits, and no code change.
  - *Risk* (my caution): check that no specification names `docs/research/` as the record's place.
- **(b) Re-baseline.**
  - *What is done:* decide DP-18, so that a project can name `docs/research/` as its experiments root.
  - *Cost:* a launcher change with its tests, in W2-56's or W2-21's paths.
- **(c) Defer.**
  - *What is done:* start W2-26's next worker in the old form, with DEC-789's tripwire, and record it.
  - *Cost:* nothing now.
  - *Risk:* research stays unsandboxed.

In every option, W2-26 needs a place it can write for its EXAMIN clone: W2-50's run folder [E R5].

**5. Recommendation.**

Classification (DEC-809): E F6 yes/other (fails closed). No round.

(a), with W2-50's run folder for the clone. Medium-high confidence.

**6. What it blocks, and what waiting costs.**
- *It blocks:* W2-26's next worker, and so W2-27 [E F6; D §2.1].
- *Waiting costs:* the EXAMIN leg stops, or runs unsandboxed [E F6].

### P-S7. Make the retrieval and memory proofs an entry criterion of EXAMIN's copy

**1. Context.**
- The Charter's purpose is that the project's memory lives in the repository, and reaches agents through retrieval and the context packet [Charter:19–22].
- The Contract's retrieval line is CAP-10, a hit@5 of 85 by A's reading [A F7]. W1-21's and W2-54's tests use 80 [D §2.1; B].
- B measured retrieval with twenty real questions [B].

**2. What happened.**
- The packet is 42 to 168 times its ceiling, carries no text, and reports success [B F1; E F8].
- Any edit switches the whole index off, and `gov context` hides the loss [B F2].
- The code graph cannot answer callers or callees [B F3].
- Superseded register decisions pass the filter meant to stop them [B F4].
- A resume drops the recorded next step [B F5; E F11].
- Tests fill the semantic index, and the kernel template is not in it [B F6].
- Whether any held-out file is indexed is unknown [B F7].
- Workers read an old copy of the register [E F12].
- At Wave 1's exit, CAP-15.d, CAP-17.c and CAP-10 were found weakened [A F7].
- The reports give three different hit@5 figures (Appendix A).

**3. Why it matters.** Adopting EXAMIN with these defects would carry this repository's memory problems into a product [B]. Two of them can fail open: B F4, and B F7 if a held-out file is indexed.

**4. Options.**
- **(a) An entry criterion of W2-27 (the copy), by DEC-803.** It covers section 6's rows 1 to 8 and row 14, with the pass lines set now.
  - *Cost:* the fixes ride in W2-03, W2-04, W2-06, W2-10 and W2-32 (DEC-802), and W2-04's and W2-06's KPIs widen. The code-graph fix, the held-out exclusion and the index mix (row 6) each need a ticket the owner names.
  - *Risk:* the copy waits if those tickets slip.
- **(b) An entry criterion of W2-30 (the real repository) only,** with the copy used to measure the defects.
  - *Cost:* less delay.
  - *Risk:* the copy runs with the defects, though only on a copy.
- **(c) Re-baseline CAP-10, CAP-15.d and CAP-37's acceptance for Wave 2 (DEC-105), and adopt as things are.**
  - *Cost:* the lowest.
  - *Risk:* the products get today's memory.

Whichever is chosen:
- The owner, or the orchestrator, checks now whether any held-out path is in the lexical index or in the code index's file copies [B rec. 7].
- The owner decides CAP-10's line before W2-15a and W2-15b measure it: keep 85, or re-baseline to 80 by DEC-105.
- B's 20 questions, with their gold answers, become the standing measure, run at each release, with pass lines the owner sets. Today's figures are 13 of 20 in the first five and 17 of 20 in the bundle [B rec. 12].

**5. Recommendation.**

Classification (DEC-809): B F1, F2, F3, F5, F6 yes/other · B F4 yes/fails open (owned by W2-32 or W2-03) · B F7 yes/fails open, unknown (an owner check now) · E F8, F11, F12 yes/other. No round.

- **(a) for B F1 to F6, and for the check in F7, as B asks** [B, What works].
- **(b) for B F8 to F15:** W2-13, W2-32 and rows.
- **The held-out check now.**
- **CAP-10's line decided before it is measured again.**

Medium-high confidence.

**6. What it blocks, and what waiting costs.**
- *It blocks:* W2-27, under (a).
- *Waiting costs:*
  - every Wave 2 packet stays unusable, so leads paste decisions into briefs by hand [E F8];
  - the code-graph fix has no owner, so `gov impact` (W2-37) cannot work [B F3].

### P-S8. Set the products' timeline, the scope and the size

**1. Context.**
- The owner's fourth purpose is that the products are built faster and more safely.
- The Charter allows one EXAMIN pilot in Wave 2, after Track A passes and is audited. Every other product waits for Release 1 [Charter:31–36].
- DEC-064 asked for a size review at each wave: "glue ≈ 4.5k LOC across three waves" [A F6].
- The Charter lists eleven Wave 2 roles [E F18].

**2. What happened.**
- **The copy has moved behind more work** [A F3]:
  - DEC-794, DEC-799 and the staged DEC-813 put W2-27 behind W2-24, W2-56 and W2-57;
  - W2-24 has 27 dependencies and sits in layer 6 of 11;
  - W2-30 sits in days 18 to 23.
- **W2-27's ticket file lists neither W2-24 nor W2-56 among its dependencies,** though the WBS card states both conditions [A F9].
- **The plan's order and the Charter's wording seem to differ** (my reading):
  - the plan's schedule puts the copy's verdict, near day 13, before Track A's, near day 14 [D §2.3];
  - the Charter allows the pilot only after Track A passes and is audited (W2-25), and it names the copy's verdict (W2-28) as part of the pilot [Charter:32–34].
- **UPIM, ASMO and Release 1 have no plan** [A F3]:
  - UPIM and ASMO appear only in DEC-567;
  - Release 1 needs Wave 3 (38 items, no tickets) and qualification (CAP-49; title shortened).
- **The size** [A F6, F2]:
  - the Gov OS is about three times DEC-064's estimate;
  - 58 tickets now, against 52 at the plan's approval; six of the seven added repair or enable the machinery.
- **Eight of the Charter's eleven Wave 2 roles are unplanned,** and DEC-066's project roster is absent [A F5; E F18].

**3. Why it matters.**
- The product payoff is deferred, with no date [A F3].
- The owner has had no decision point on size [A F6].
- Part of the Charter's Wave 2 scope goes unbuilt, with no decision recorded [A F5].

**4. Options.**
- **(i) The EXAMIN path.**
  - (a) Write the owner's conditions (W2-24, W2-56, W2-57) into W2-27's ticket file as dependencies, make W2-25 an explicit entry criterion, and update WBS §3's dates [A rec. 4, rec. 8; A F9].
  - (b) Let the copy go ahead of W2-24, as its ticket file reads now, by re-baselining DEC-794. This is faster. It goes against the owner's decisions, and, on my reading, against the Charter.
- **(ii) The size review.**
  - (a) Now, on A's figures, with a re-baseline by DEC-105 if needed [A rec. 2].
  - (b) At Track A's verdict, together with sizing Wave 3.
- **(iii) Admitting new tickets.** Admit one only when it serves an exit criterion or a Contract item, and keep applying DEC-801 [A rec. 3].
- **(iv) The eight roles**, by DEC-105 [A rec. 6; E R12]:
  - apply now, as new Wave 2 tickets;
  - defer them to Wave 3, by a recorded decision;
  - re-baseline the Charter's §6, or DEC-066's roster.
- **(v) The other products.**
  - Tie UPIM and ASMO to W2-19 and to Release 1.
  - Size Wave 3, and set a range for Release 1, at Track A's verdict [A rec. 4].

**5. Recommendation.**

Classification (DEC-809): A F3 no/other (a row automatically) · A F5 no/other · E F18 no/other · A F6 yes/other · A F9 yes/fails open (a records fix before W2-27 can start). No round.

| Question | Recommendation | Confidence |
|---|---|---|
| (i) The EXAMIN path | (a) | High |
| (ii) The size review | (a), in a light form: record the measured size against DEC-064 now, and decide on a re-baseline with Wave 3's sizing | Medium |
| (iii) New tickets | The admission rule | Medium-high |
| (iv) The eight roles | Defer them to Wave 3 by a recorded decision; create the roster, or amend DEC-066, then | Medium |
| (v) The other products | Tie UPIM and ASMO to W2-19 and Release 1; size Wave 3 at Track A's verdict | Medium |

**6. What it blocks, and what waiting costs.**
- *It blocks:* a safe start of W2-27, since its dependency list is incomplete [A F9]; and any product plan.
- *Waiting costs:*
  - the products stay undated;
  - W2-27 could start before the owner's own conditions are met [A F9].

### P-S9. Restore a referee outside the agent's machine

**1. Context.**
- ADR-0001's hard boundary has four parts: git history; the pre-push gate (G3); CI on every push, as an advisory result; and the owner's merge, only on green [ADR-0001:52–57].
- The guard and containment are guardrails, not the boundary [ADR-0001:47–51].

**2. What happened.**
- **The git hooks are off** [D F6]:
  - they were removed on 2026-10-15, after a hook's check wrote foreign commits onto a ticket branch;
  - a test asserts that they are off;
  - F-A is an entry criterion of W2-08, which puts them back (DEC-804).
- **CI cannot pass** [D F6]:
  - its tests step stays "unmeasured" until the owner approves pytest for the runner;
  - its evidence step needs a pre-push note, which cannot be written while the hooks are off;
  - nothing is pushed during Wave 2.
- **Row W2-H002 names three tools for the owner to approve** [A §2.1].
- **`gov doctor` cannot see this** [D F7]:
  - it passes the hooks with no git hook installed;
  - it cannot tell an editable or foreign `gov`.

**3. Why it matters.**
- Every commit goes in now without the commit-time checks (G1 and G2) or the staged-secrets scan [D F6].
- Wave 2 would end with a CI that cannot be green, so "only on green" cannot be met [D F6].
- Exit criterion 3, W2-22 and W2-24 count on doctor's green [D F7].

**4. Options.**
- **(a) Now** [D R5, R6]:
  - The owner approves the CI tools under ADR-0001's install rule: pytest, per `ci.yml`, or the three tools of row W2-H002.
  - The plan states that CI's evidence step stays red until the hooks return.
  - Doctor's hooks check reads what git will actually run, as one of W2-08's measures.
  - Doctor's `gov` check fails on an editable or foreign install here too (W2-18 or W2-22).
  - Optionally, `w2/integrate` is pushed to the private remote at each merge, so that CI measures during the Wave. This is my proposal, and it changes the standing rule that nothing is pushed.
  - *Cost:* one owner approval and a recorded install; the doctor changes ride in W2-08 and W2-22 (DEC-802).
  - *Risk:* CI's tests step may be red at first. That is unmeasured.
- **(b) Wait for W2-08,** and bring the hooks and CI back together.
  - *Cost:* nothing now.
  - *Risk:* the boundary stays off for the rest of Track A.
- **(c) Re-baseline the boundary for Wave 2:** record that, until W2-08, the boundary is the owner's merge alone.
  - *Consequence:* honest about the state of things.
  - *Risk:* nothing is measured outside the machine.

**5. Recommendation.**

Classification (DEC-809): D F6 yes/fails open (accepted for the hooks by DEC-712; owned by W2-05 and W2-08) · D F7 yes/fails open (owned by W2-08 and W2-22). No round.

- **(a), without the push:** medium-high confidence.
- **The push:** medium confidence. It changes a standing rule whose reason my sources do not give.

**6. What it blocks, and what waiting costs.**
- *It blocks:* an honest green for exit criterion 3 and W2-22 [D F7], and the end-of-Wave merge "only on green" [D F6].
- *Waiting costs:* commits go in without commit-time checks, which is the risk DEC-712 accepted [D F6].

### Fixes that need no owner decision

Each rides in a ticket that runs anyway (DEC-802), or is a row.

| Finding | Fix | Where |
|---|---|---|
| A F4: the validator passes undelivered items | Count only closed tickets and acceptance tests; add CAP-44.f to W2-52's `closes`; run it again on Contract 4.2 | W2-51's resume [A rec. 5] |
| A F7: twelve Wave 1 items were found weakened | Show them, and CAP-10's open re-baseline, in the countdown | The orchestrator [A rec. 7] |
| A F8, A F9: the plan's records are out of step, and W2-27's dependencies miss two conditions | One records pass, which also adds W2-24's check and W2-56 to W2-27's dependencies | The orchestrator [A rec. 8] |
| B F8 to F15 | The lexical route, the reranker, reads during a rebuild, bundle size, drift, the path map, silent exclusions, leftover folders | W2-13, W2-32, rows [B rec. 8 to 11] |
| C F-10: API-0002 names a missing file | Name a file that exists, or generate the interface from the CLI | A Wave 3 row [C R-7] |
| D F2: the guard's self-lock | W2-10's measure covers the guard's own failures, with the reason on standard error; W2-H031's fallback comes before W2-42 | W2-10 [D R4] |
| D F9, B F13: the tool's description of itself | Correct the help text and the path map's systems block | A row [D R5; B rec. 11] |
| E F9: hooks say too little, or the wrong thing | The current Wave's prompt; the subagent's stop reason where it can see it | W2-10 [E R8] |
| E F13, E F17 | A cleaned environment; one retry on a missing git lock file | W2-56 [E R6, R12] |

## Appendix A. Where the reports disagree

The brief asks me to say where the five reports disagree, and which evidence each rests on, and not to settle a disagreement by reading further. I have settled none of them. Where an earlier section uses one report's figure, it names that report.

### A.1 How many times W2-53's close was refused

- **Report A: twice.**
  - A STORE_STALE refusal (`log/close-DAEO-7rr2-2.json`), then a CHECK_FAILED at 12:01 on 2026-10-19 (`log/close-DAEO-7rr2-3.json`) [A F1].
  - A set aside a third log, `log/close-DAEO-7rr2.json`, because it is not valid JSON [A §1].
- **Report D: three.**
  - A first close refused "on three hard-block checks … plus a stale checkpoint" (register:8414), then the re-close refused on one W1-30 test [D §2.2].
  - D counts "W2-53's three" among Wave 2's five logged close runs [D §2.2, "What it has cost"]. They are part of the 33 logged runs on this repository, none of which passed [D F3].
- **What they share.** No run passed, and the last refusal was on one W1-30 timing test that passes when run alone [A F1; D F4].
- **Not settled:** whether the log A set aside records the first refusal that D counts.

### A.2 The retrieval quality figure, and its pass line

*hit@5* is the share of test questions that have a right answer among the first five results [D §2.1].

- **Report A:** 83.33, against the Contract's 85, "and the contract is not re-baselined". This is CAP-10 as W1-43's exit audit found it [A F7].
- **Report D:** 81.67, measured by W1-21 at `5f038b47`, against a pass line of 80. W2-54 did not measure it again, because no GPU is reachable [D §2.1].
- **Report B:** a different measure, on its own twenty real questions.
  - The governing source was in the first five results for 13 of 20 (65 percent), and in the bundle for 17 of 20 [B §2.2; B rec. 12].
  - B notes that W2-54's tests set the pass line at 80 percent, on a different set of questions [B §2.4].
- **Not settled:**
  - which measured figure is current, A's or D's;
  - which line applies, 85 or 80.

  P-S7 asks the owner to decide the line before W2-15a and W2-15b measure it.

### A.3 How large the context packet is, and how serious

- **Report B, F1: high.**
  - B's reason: "CAP-15 is the core of 'memory in the repository' for a worker."
  - In B's runs CTX-A and CTX-B, W2-54's packet counts 1,009,095 tokens, 168 times its 6,000 ceiling.
  - 9 of 10 tickets give 252,220 to 1,009,095 tokens, with `ok: true` and exit 0 [B F1, §2.7].
- **Report E, F8: medium,** "Known and planned."
  - The packet file in W2-54's worktree, built on the register at commit `7d689987`, uses 950,383 tokens of 6,000 [E F8].
- **What they share.** The packet cannot be used as built.
- **Not settled:** why the sizes differ. One likely cause, which I have not checked, is that the two were built from different copies of the register; a worker's tree holds an older copy [E F12].

### A.4 How serious the lost next step on resume is

- **Report B, F5: medium-high.**
  - In B's run RS, one compaction replaced the deliberate next action with "Resume after compaction", both in `gov checkpoint --resume` and in the session-start text, because the newer automatic checkpoint wins.
  - "The recorded next step is hidden, not deleted" [B F5, §2.8].
- **Report E, F11: low.**
  - Automatic checkpoints hold no state, and every session on a ticket shares one series.
  - E's consequence: "no state is lost (none was recorded)" [E F11].
- **What they share.** A resume can leave a session without its next step.
- **Not settled.** B looked at a session that had recorded a next step; E looked at what the automatic checkpoints themselves hold.

### A.5 How much the eight unplanned Charter roles weigh

- **Report A, F5: medium.** "For product work these roles are what makes a 'software company' more than one engineer role" [A F5].
- **Report E, F18: low,** "A row for the plan". Its reason is that "no Wave 2 ticket today needs a role that is missing" [E F18].
- **What they share.**
  - Both find the same eight roles unplanned.
  - Both answer "no" to the ordinary-work question, so the finding is a row whichever severity holds (DEC-801).
  - E adds that DEC-066's project roster is absent.

### A.6 Whether EXAMIN's copy (W2-27) waits for the Track A gate run (W2-24)

- **Report D: no.**
  - "EXAMIN's copy (W2-27) does not wait for it (WBS:130)".
  - By the plan's schedule, the copy's verdict comes at about day 13, and Track A's, which includes W2-24, at about day 14 [D §2.3].
  - D does list W2-56 as a condition (DEC-799 item 4) [D §2.1].
- **Report A: yes.**
  - DEC-794: W2-27 "does not start unless W2-24's repeat of the quality-control check gives sections (a) and (d) green". The staged DEC-813 puts W2-24 after W2-57 [A F3].
  - The WBS card states these conditions, but W2-27's ticket file lists neither W2-24 nor W2-56 [A F9].
- **Not settled.** D reads the dependency line; A reads the decisions and the card. P-S8 asks the owner to write the conditions into the ticket.

### A.7 What the owner must approve for CI

- **Report A:** row W2-H002 says the CI job is red, "unmeasured", until the owner approves three tools [A §2.1].
- **Report D:** pytest for the CI runner, which `ci.yml` (lines 20–23) names as the owner's decision [D F6, R6].
- **Not settled:** whether these are one approval or two. P-S9 names both.

### A.8 How many Wave 2 tickets there are

- **Report A:**
  - By its count of the WBS ticket table: 52 at the plan's approval and 58 now, plus W2-57's staged card [A F2].
  - It quotes the checkpoint's "1/55 closed" [A F1].
  - It shows that the WBS's own counts disagree [A F8]:
    - its ids note says W2-00 to W2-50;
    - its totals say 51 plus W2-00;
    - its §4 says 53 plus W2-00;
    - its table lists 57 plus W2-00;
    - `.tickets/` holds 55 plus W2-00.
- **Report D:** 55 tickets in three tracks (WBS lines 88–90), with "one ticket of 55 closed" [D §1, §2.2].
- **Not settled.** The orchestrator's records pass for A F8 would settle it (section 7, "Fixes that need no owner decision").

### A.9 How many lead briefs there are

- **Report C:** 45 Wave 2 lead briefs, the files named `W2-*-A5-*.md`. 44 of the 45 carry DEC-731 and DEC-732 [C §1, F-1].
- **Report E:** 449 briefs, 334 of them lead briefs, the largest 51,275 bytes, all in the orchestrator's git-ignored folder [E F2].
- **What they share.** The briefs sit outside git.
- **Not settled.** C states the file pattern it counted; E does not state one.

## Appendix B. All 62 findings, with their two lines

This appendix lists every finding of the five reports, in each report's own order.
- **Ordinary work:** the report's own line, word for word.
- **Consequence:** the report's class. Where the report gives a reason, I have shortened it.
- **Severity:** the report's own judgement.
- **Finding:** the report's title, shortened.

The judgement rules are set out under "How findings are judged", at the start of this synthesis.

**The count.**
- Ordinary work: 58 answer "yes". Four answer "no": A F3, A F5, E F18 and E F19. Those four are rows automatically.
- Consequence: ten fail open (A F4, A F9, B F4, B F7, D F6, D F7, D F8, E F1, E F4, E F19). None loses work.
- Nine are both "yes" and "fails open", the only kind that can justify a round. This synthesis proposes no separate round for any of them. Each rides in a ticket that runs anyway, is an owner check, or is an accepted risk (DEC-802; sections 1 and 7).

### B.1 Report A: purpose and roadmap

| No. | Finding | Severity | Ordinary work | Consequence |
|---|---|---|---|---|
| A F1 | No ticket has yet closed through a clean `gov close`, and the close holds up all delivery | High | yes, because an ordinary close runs the full regression on a shared, loaded machine, and that is enough to fail a timing-sensitive test, as W2-53's close shows. | Other: it fails closed, but no Wave 2 work counts as delivered until closes pass |
| A F2 | Wave 2's effort has gone mostly into the Gov OS's own machinery | High, for the roadmap | yes, because the rounds and the new tickets came out of ordinary reviews of ordinary tickets, not out of anything deliberate. | Other: time, owner attention and size; nothing fails open |
| A F3 | The products wait: only EXAMIN has a pilot, and UPIM and ASMO have no date | High, against the purpose | no, because this is a roadmap matter set by owner decisions, not a fault that an agent hits in its work. | Other: the product payoff is deferred |
| A F4 | The plan validator checks less than exit criterion 7 asks, and can pass undelivered items | Medium | yes, because the validator is the routine check for exit criterion 7. A README that mentions an item is ordinary, and so is a ticket that names an item in `closes` and has not closed. | Fails open: a PASS for an exit criterion that is not met |
| A F5 | Eight Wave 2 roles in the Charter have no Contract item, ticket or row | Medium | no, because this is a gap between the Charter and the plan, not something an agent hits in its work. | Other: part of the Charter's Wave 2 scope is unbuilt, with no decision recorded |
| A F6 | DEC-064's size review was never held, and the code is about three times the estimate | Medium | yes, because the review was simply left out of the ordinary writing of the Wave 1 exit and the Wave 2 plan. | Other: the owner has had no decision point on size |
| A F7 | Twelve Wave 1 items count as delivered but were found weakened | Medium | yes, because agents rely on these items in ordinary work: the context packet, the approval facts, the guard's tool list. | Other: weakened, not missing; the guard item fails closed |
| A F8 | The plan's records are out of step with the decisions and with each other | Low | yes, because each gap comes from an ordinary edit: a decision recorded without its ticket file, a count not carried over, a row not triaged. | Other: the validator's failures are closed; the rest mislead a reader |
| A F9 | W2-27's recorded dependencies miss two of the owner's conditions | Low | yes, because starting the next ticket whose dependencies are closed is the orchestrator's ordinary routine. | Fails open: the dependency check would pass W2-27 before the sandbox and retrieval checks are green |

### B.2 Report B: memory and retrieval

Report B gives the consequence class only.

| No. | Finding | Severity | Ordinary work | Consequence |
|---|---|---|---|---|
| B F1 | The context packet is 42 to 168 times its ceiling, carries no text of its inputs, and reports success | High | yes, because every `gov context` on a ticket that cites a decision gives this packet, and so does every session-start brief. | Other |
| B F2 | Any change to a tracked file switches the whole index off, and `gov context` hides the loss | High | yes, because every edit to a tracked file, in any working tree, switches retrieval off until the next full rebuild, and the main tree is in that state now. | Other |
| B F3 | Questions about code callers, callees and impact cannot be answered here: the query exceeds the tool's 100k-row cap, and the cause is hidden | High | yes, because every `gov retrieve --id <symbol>` and `gov closure <symbol>` on this repository hits it, with no special construction. | Other |
| B F4 | Every register chunk carries the id DEC-812, so the superseded filter does nothing for register decisions | Medium-high | yes, because 60 of the 400 evidence items in the 20 questions are register chunks; any decision question gets them. | Fails open |
| B F5 | After any stop or compaction, the resume brief drops the recorded next step | Medium-high | yes, because every session with `GOV_TICKET` set writes an automatic checkpoint at the end of every turn. | Other |
| B F6 | Tests fill the semantic index, and the kernel template is not in it at all | Medium-high | yes, because any question about a role, hook, skill or check meets it. | Other |
| B F7 | Restricted and agent-settings files are in the index, and nothing in the indexers excludes held-out material | Unknown until checked; high if a held-out file is indexed | yes, because a plain question can rank text from any indexed file, and no construction is needed. | Fails open |
| B F8 | The lexical route matches a whole question as one exact string, unranked | Medium | yes, because every question in plain words gets nothing from this route. | Other |
| B F9 | The reranker is not shown to help here, and it pushes a ticket's own front matter down | Low-medium | yes, because every bundle is reranked. | Other |
| B F10 | During a rebuild, reads fail with a wrong error code or a traceback | Low-medium | yes, because DEC-719 asks for a full rebuild before each close and each planning or audit step, and any agent reading meanwhile hits it. | Other |
| B F11 | Bundles at the wider search settings (radius 2 and 3) exceed their token budget, by decision, and repeat lines | Low | yes, because any `--radius 2` or `3` question returns such a bundle. | Other |
| B F12 | A rebuild re-embeds whole files, and the embedding is not bit-for-bit repeatable, so answers drift | Low | yes, because every rebuild after an edit re-embeds. | Other |
| B F13 | The path map contradicts its own adoption rule, and its systems block is out of date | Low | yes, because any agent or adopter reading the map gets these answers. | Other |
| B F14 | A file with any secret-scanner hit is left out whole, and nothing says so | Low | yes, because questions about the secret filter or those tests cannot reach their sources. | Other |
| B F15 | Code-index daemon folders pile up, and a rebuild pushes the shared machine past its gate | Low | yes, because every rebuild raises the load, and every new repository root that uses the code index leaves a folder. | Other |

### B.3 Report C: from decisions to the specifications

Report C classifies all ten of its findings as "yes" and "other" [C §4].

| No. | Finding | Severity | Ordinary work | Consequence |
|---|---|---|---|---|
| C F-1 | Wave 2's standing rules for agents live outside the kernel, and most of them outside git | Medium; high against the purpose that the memory lives in the repository | yes, because an orchestrator started from a fresh clone, a cleaned scratch folder, or any repository that adopts the kernel (EXAMIN, UPIM, ASMO) starts from the committed prompt and the kernel, which lack these rules; that is plain use, not a construction. | Other: later gates catch each missed rule; nothing fails open, and no work is lost |
| C F-2 | The committed prompt contradicts DEC-731 and lacks DEC-732 and DEC-733 | Medium | yes, because the orchestrator reads the prompt at every start (w2-orchestrator.md:12) and writes lead briefs from A5; an orchestrator without the scratch template follows A5 as written. | Other: each missing rule fails in a way a later step catches |
| C F-3 | The Contract's two forms disagree on three provider lists | Low | yes, because the owner, an adviser or a product-spec worker told to read "Contract v4.x" (A4, w2-orchestrator.md:204) reads the readable form and sees provider lists the machine form no longer has. | Other: the drift is in provider lists only, not in scope, waves or acceptance text |
| C F-4 | Contract-level decisions since 2026-10-04 have not reached the Contract on the integration branch | Low; medium for W2-28 and W2-30 if they start before W2-49 merges | yes, because every ticket starts from w2/integrate (w2-orchestrator.md:33), so until W2-49 merges a ticket that cites a 4.2 item reads 4.1 in its own worktree. | Other: work follows the ticket text; a reviewer may judge the lite form out of scope, or the reverse |
| C F-5 | The register does not show on an entry what later entries did to it | Medium | yes, because an agent that finds an entry by gov retrieve or grep reads its status line, and nothing there says a later entry changed it. | Other: an agent may apply a replaced rule; the guard and the gates are unaffected |
| C F-6 | Rules with no landing that an agent reads are not followed | Low | yes, because each case happened in ordinary work: the residual commits, the Wave 1 exit audit's brief, an auditor's run. | Other: wrong trailers, a missed reading and a throwaway clone; none failed open or lost work |
| C F-7 | The planned remedies are fixed lists that already lag the register, and part of them needs an owner edit | Medium | yes, because every new standing rule the owner makes in ordinary work widens the gap until someone extends the list by hand. | Other |
| C F-8 | The judgement rules exist in two texts, each called "word for word" | Low | yes, because a brief writer told to copy the rules "word for word" must choose between two texts. | Other: the texts agree in substance, but A3's short form lacks the list of constructed cases |
| C F-9 | The kernel still states Wave 1's launch, return and lead-write rules | Low | yes, because a repository that adopts the kernel gets the kernel's text, not this repository's prompt. | Other: a risk only once the kernel runs agents in another repository, so an entry criterion of that ticket (DEC-803) |
| C F-10 | API-0002 points to a command source that does not exist | Low | yes, because an agent or an adviser who checks the command interface opens the file it names. | Other |

### B.4 Report D: tool staging

| No. | Finding | Severity | Ordinary work | Consequence |
|---|---|---|---|---|
| D F1 | This repository is governed by its own working copy; no pinned version exists, and the plan prescribes none for it | High | yes, because every session, hook, check and close on this repository runs whatever code is on disk in its tree at that moment. | Other: it failed closed in every case D found; it could fail open for one session, but D found no instance |
| D F2 | A broken save of a guard file locks the session that made it, the repair included, and no reason is shown | Medium | yes, because every engineer on a guard ticket edits these files in their own worktree, and it has happened at least twice. | Other: it fails closed; the session stalls until someone repairs it from outside |
| D F3 | `gov close` has never passed on this repository, and Wave 2's exit depends on it | High | yes, because every ticket must pass it, and each Wave 2 refusal I traced was caused by something outside the ticket. The evidence: register:8289 and 8414; `log/close-DAEO-7rr2-2.json` (`STORE_STALE`); `CHECKPOINT.md`, State. | Other: it fails closed; the cost is the queue, and the owner decisions it needs |
| D F4 | The close judges its own change after the merge, and the only remedy for a failure under load is an entry only the owner may add | High | yes, because parallel leads, reviewers and auditors load this machine in normal work, and the close runs the full regression. | Other: it fails closed; one Wave 1 timing test holds thirteen tickets |
| D F5 | The tickets that would end the loop wait behind it | High | yes, because this is the plan's own order, followed as written. | Other: delay |
| D F6 | The commit and push gates are off and CI cannot pass, so ADR-0001's hard boundary is not working during Wave 2 | Medium | yes, because every commit made now goes in without the commit-time checks (G1 and G2) and the staged-secrets scan, and Wave 2 will end with a CI that cannot be green. | Fails open: the commit and push checks do not run; accepted for the hooks (DEC-712), and the guard and containment still run on every call |
| D F7 | `gov doctor` reports the hooks as passing when no git hook is installed, and cannot tell an editable or foreign `gov` | Medium | yes, because adoption, W2-22, W2-24 and the exit all rely on doctor as the health check, and it is run as a matter of course. | Fails open: a health check that passes a gate that is not there |
| D F8 | Two versions of the Gov OS run in one worktree session, and a hand rule keeps them apart | Medium | yes, because a bare `gov` or a `pytest` without the per-command `PYTHONPATH` is the default form in a worktree, and W2-01's lead met it (register:7805). | Fails open, for a worktree's own verification only; the close after the merge tests the right code, and fails closed |
| D F9 | The tool's description of itself lags what is built | Low | yes, because agents read the help text and the path map to learn what exists. | Other: misleading, with no gate affected |

### B.5 Report E: roles and context

| No. | Finding | Severity | Ordinary work | Consequence |
|---|---|---|---|---|
| E F1 | Ticket leads run as the orchestrator, outside the sandbox: they can write what DEC-236 forbids them, and their script writes into other trees go unrecorded | High | yes, because every lead runs this way today, and a lead's routine is writing notes, briefs and scripts; one wrong path, such as a ticket field or a file in the main checkout, is not refused. | Fails open: writes that DEC-236 forbids a lead are allowed, and writes outside its tree are not recorded |
| E F2 | A launched session loads none of its role's rules; they reach it only through a brief written by hand for each run, and the briefs are kept outside git | High, against the first purpose | yes, because every session starts this way, and whatever a worker knows of its role is what its lead remembered to write that day. | Other: nothing opens, but the rules drift from brief to brief, and the record of what each worker was told lives outside the repository |
| E F3 | A launched worker's Write tool is refused in its own scratch folder, because the CLI reads the launcher's deny patterns the wrong way round | Medium | yes, because a worker that keeps a note, a measurement script or a draft in its scratch hits it on the first try. | Other: it fails closed; it costs a round trip, and pushes the worker to write through a script, which the guard cannot read |
| E F4 | Roles meant to write little or nothing can write anywhere in their tree through a script, and can commit; containment reports the write and leaves it | Medium | yes, because any helper script, test run or `gov checkpoint` that a worker runs writes where it writes; launches 4 and 5 did so while following ordinary steps. | Fails open (detected): the write lands and stays, and a commit can carry it |
| E F5 | Every role reads everything except the held-out paths, and three texts disagree on what the test designer may read | Medium | yes, because a test designer that follows A1 reads the code, and any worker that greps its tree for its ticket id reaches the lead's notes. | Other: no write opens, but the independence that MR-3 and CAP-38.c ask for rests on brief text alone |
| E F6 | No Wave 2 research ticket can be launched as DEC-799 requires | Medium | yes, because W2-26's next worker, started as DEC-799 says, is refused at once. | Other: it fails closed; EXAMIN's research leg (EXP-003) stops |
| E F7 | Every session carries context the Gov OS does not govern: 45 skills and 10 agent types it did not write, four cloud connectors, and a model-side memory outside the repository | Medium | yes, because every session, of every role, starts with this context. | Other: the tools fail closed, but part of every session's steering comes from texts the project did not write, and every role has a memory store outside the repository |
| E F8 | The context packet gives a worker its decisions by id, and each id turns into the whole register | Medium | yes, because every ticket's packet is built this way. | Other: the packet cannot be used as built, so leads paste decisions into briefs by hand |
| E F9 | The hooks tell sessions too little, or the wrong thing | Medium | yes, because the orchestrator compacts and continues (DEC-250), long-running leads compact, and every worker's subagent stops. | Other: the instructions are stale after a compaction, and a subagent has to search for its stop reason |
| E F10 | `CLAUDE.md`, the only governance text every session loads, names four places that do not exist and leaves out the ticket lead | Medium | yes, because a session that follows it to find its role file or the Contract looks in the wrong place first. | Other: a wasted search, or the session concludes that the Contract is absent |
| E F11 | Automatic checkpoints hold no state, and every session on a ticket shares one series | Low | yes, because a lead, its workers and its reviewer share one ticket id, and every stop and every compaction writes a checkpoint. | Other: no state is lost, since none was recorded; a worker's compaction leaves it no next step |
| E F12 | A worker's own tree holds the register as it was when its branch was made | Low | yes, because a worker checking a decision its brief cites opens `docs/DECISION_REGISTER.md` in its own tree. | Other: a decision it cites can be missing, or superseded |
| E F13 | `gov launch` hands the worker the parent session's whole environment | Low | yes, because every launch from a lead passes the lead's environment on. | Other: a worker's behaviour depends on its parent's settings, and the parent's session id reaches it |
| E F14 | The model a subagent runs on is not the one the register records, and no launch has to name its model | Low | yes, because every subagent runs this way, and so does every launch whose arguments omit the model. | Other: the record of which model did the work can be wrong |
| E F15 | The skill text a session loads carries no version, and each skill exists in four copies | Low | yes, because every session that loads a skill loads this copy. | Other: a close record cannot say which skill text the worker followed |
| E F16 | The orchestrator's start-of-session reading list is larger than its working context | Low | yes, because the orchestrator follows this list at every start and resume. | Other: the reading displaces working context and brings compactions sooner |
| E F17 | Sandboxed sessions started in parallel can trip over a git lock | Low | yes, because leads run workers in parallel worktrees that share the main `.git`. | Other: a command fails once, for no reason of its own |
| E F18 | Most of the Charter's Wave 2 roles are not planned, and the project roster DEC-066 describes is absent | Low | no, because no Wave 2 ticket today needs a role that is missing; the gap is in the plan. | Other |
| E F19 | The launcher refuses some command-line flags that remove the guard, but not all of them | Low | no, because the briefs name the arguments a lead passes, and `LEAD-common.md` (line 21) tells a lead not to fall back when a launch is refused, so a lead would have to improvise against its brief. `--restricted` is the likeliest improvisation, because its name sounds safer. | Fails open (untested): the session would run without the guard, though the sandbox and the launcher's deny rules would still apply |
