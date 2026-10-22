# Independent assessment of the Gov OS, October 2026: lens I, the synthesis of the test review

You are an independent auditor (`GOV_ROLE=independent-auditor`). The Wave 2 orchestrator started you on the owner's order of 2026-10-21 (DEC-889 item 16).
- Four auditors have each reviewed the tests of one area against the specifications in force, independently. You are the fifth session: the synthesiser. You saw none of their work in progress.
- You wrote none of the work you assess, and nobody expects a particular result from you. Report what you find, with its evidence.

## The purpose of the Gov OS (the owner's words)

The Governance OS exists for four things:
- the project's memory lives in the repository instead of in agents' memory;
- agents are safe and governed;
- the owner stays in control;
- the owner's products, EXAMIN, UPIM and ASMO, are built faster and more safely.

## Why this review (the owner's words, DEC-889 item 16)

Since Wave 1, many decisions changed what the Gov OS should do, but tests written against the old rules remain. Lens I asks of every test: is it valid and needed, weak, duplicate, obsolete, outdated, flaky or not reproducible; what it costs a close; and what it changes in the plan.

## What your synthesis is for

The owner has set a **review point** (DEC-889 item 14). No work starts on:
- W2-66 (path-scoped regression at close, with the test map);
- W2-68 (batched closes, reuse, fingerprints);
- W2-67 (test hygiene: per-test copies, nested reruns).

They wait until lens I has reported and the owner has reviewed, in writing:
- their cards;
- W2-57's ticket file (the serial-only and load-sensitive lists);
- W2-07's card (the close by ticket class);
- the re-pin plan.

Your synthesis is what the owner reads, with the orchestrator's drafts, to decide. It must make the decisions easy to take, in the order the work needs them.

## The state when this brief was written (2026-10-22)

- **Repository:** `/home/usain/Dynamic-Agentic-Engineering-OS`, branch `w2/integrate`, at the head `git log -1` shows when you start. The four reports reviewed it at `4166d8d9` and the commits after it, read-only.
- **Contract v4.2** is on branch `w2/W2-49`: `git show w2/W2-49:docs/contract/CONTRACT_v4.md`, `git show w2/W2-49:docs/contract/contract.yaml`, and its capability files on that branch.
- **The decisions in force** are in `docs/DECISION_REGISTER.md`. Those that bear most on this review:
  - DEC-880 (W2-66's scope);
  - DEC-883 and DEC-884 (batched closes; the ladder before the re-pin);
  - DEC-889 and DEC-890 (lens H's answers and W2-66's split);
  - DEC-892 (worksteal deferred; pytest-timeout; the widest modules in the shared core);
  - DEC-896 (the test map in its own file, `governance/project/test-map.yaml`, never the path map; W2-07's KPIs; the first re-pin carries W2-58, W2-59, W2-65, W2-66 and W2-07);
  - DEC-897 (W2-69, the secrets check).
  An entry whose status line says `SUPERSEDED by DEC-n`, or carries a "Changed by" note, is not in force for that part (DEC-866).

## What you read: these sources only

- **The four reports:**
  - `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I1-guard-launcher-sandbox.md` (area 1: the guard, the launcher and the sandbox);
  - `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I2-close-checks-ratchet.md` (area 2: `gov close`, the checks and the ratchet);
  - `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I3-retrieval-context-resume.md` (area 3: retrieval, context, checkpoints and resume);
  - `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I4-records-plan-rest.md` (area 4: the records, the plan, the tickets and the rest).
  If area 4's report is missing or says PARTIAL, synthesise what is there and say what is missing.
- **Lens H's report:** `docs/assessment/2026-10/H-test-strategy.md`.
- **The owner's tool trials:** `governance/project/orchestration/packages/TOOL-TRIALS-2026-10-22.md`.
- **The decisions, the plan and the tickets:**
  - the register;
  - `docs/plan/WAVE_2_WBS.md` (the cards);
  - `docs/plan/WAVE_2_LIST.md` (the rows);
  - `.tickets/` (the ticket files);
  - `governance/project/path-map.yaml` (the ratchet lists `accepted_reds` and `load_sensitive`, and the allowed paths' context).
- **Contract v4.2** on `w2/W2-49`, and ADR-0001 (`docs/adr/ADR-0001-threat-model.md`).

Where the reports disagree, say so and say which evidence each rests on. Do not settle a disagreement by running tests.

## Rules

- **You write one file only, your synthesis (see below).** You run no command except to read (`cat`, `git show`, `grep`, `rg`, `gov retrieve`). You run no test and start no background job.
- **Never end your turn while anything of yours is pending:** in this launch form, ending a turn ends the session, and its work is lost.
- **Reads are open except Policy 2's four refusals:**
  - (a) secrets;
  - (b) the contents of the held-out material;
  - (c) another session's work on the same ticket;
  - (d) the hidden half of an evaluation set.
  Never read or name the qualification oracle. Never touch `~/gov-os-workbench`, EXAMIN's real repository or `~/.claude/`.
- **Use `gov retrieve` for what you need to know** (`PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m gov.cli.main retrieve "<question>" --json`), and say which questions it answered. Take a large question in batches, ranked and stacked, never one giant query or context (DEC-860).
  - Lens I3 found that every register item `gov retrieve` returns carries the id DEC-891. Check any decision id it gives against the register itself.
- **If a call is refused twice,** stop trying it and record it as a limit. Never look for a way round a refusal.
- **You never ask or notify the owner directly** (no question box, never `owner-ping`).

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.


Every finding in your synthesis carries the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Findings you carry over keep their two lines from the reports. Where you would classify one differently, say so and why.

## The decision format the owner requires (DEC-818)

Every owner decision you propose is a package that stands on its own, because the owner and an outside adviser may lack context. It has six parts:
1. the context, in plain words, with its history and links;
2. what happened, with the evidence;
3. why it matters to the Gov OS's purpose;
4. the options, each with its consequence, cost and risk, and what it changes in the Contract, the specifications, the skills or the briefs;
5. a recommendation, with your confidence, and the threat-model classification of its findings on one line, before the recommendation (DEC-809);
6. what it blocks, and what waiting costs.

## Your synthesis

- **Where:** write it to `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/assessment/2026-10/I-SYNTHESIS.md`. The orchestrator copies it unchanged, byte for byte, to `docs/assessment/2026-10/I-SYNTHESIS.md`.
- **Who reads it:** the owner and an outside adviser who may lack context. Write in plain words, define every internal term at its first use, and keep each section readable on a phone: short paragraphs, lists, tables where they help.
- **Sections, in this order:**
  1. **The diagnosis, in one page:** what the test estate is worth today, what it fails to catch, and what it costs a close; the few things that matter most.
  2. **The combined counts:** per verdict and per area, functions and cases, with the close time each class costs today. Say what was not reviewed, and why.
  3. **What fails open or loses work:** every finding classified "yes" on both questions, and every planted fault that no test catches and that fails open or loses work. Say for each whether it needs a round now, rides along in a ticket that will run anyway (DEC-802), or is an entry criterion of a ticket that switches a feature on (DEC-803).
  4. **What it changes, by ticket.** One block per ticket, saying what goes into its card or ticket file, from which finding:
     - W2-66 (the test map: suites, the shared core, the record-only list);
     - W2-68 (its record-reading set; reuse; fingerprints);
     - W2-67 (per-test copies; the nested reruns; worksteal);
     - W2-57 (the serial-only list, `load_sensitive`, `accepted_reds`, and a route out for each entry);
     - W2-07 (its KPIs);
     - W2-19;
     - W2-69;
     - every ticket whose allowed paths or entry criteria a report says must change before it starts (for example W2-65, W2-04, W2-21, W2-27, W2-32 and W2-37).
     Flag every place where two reports propose different changes to the same ticket.
  5. **Retirements and rewrites:** one consolidated table of every test the reports propose to retire or rewrite, deduplicated across areas, with its verdict, its evidence, the decision or Contract item it rests on, its owning ticket, and the close time saved.
  6. **The owner decisions needed, each in the six-part format, in the order the work needs them:**
     - first those that gate the review point (W2-66, W2-67, W2-68, W2-57, W2-07, the re-pin plan);
     - then those that gate other tickets' starts;
     - then the rest.
     Merge the reports' packages where they ask the same question. Keep their ids (P-I1-n, P-I2-n, R/O items of I3, I4's) so each can be traced.
  7. **Disagreements and limits:** where the reports disagree, and what none of them could review.
- **Sources:** cite the report and its finding, package or table row for every claim.
- **When you have written it,** read it once more from the file.

## Your return (after the synthesis is written)

First, twelve labelled lines in this order:
1. task
2. status (DONE, PARTIAL or BLOCKED)
3. work_completed
4. files_changed
5. evidence
6. tests
7. discoveries
8. risks
9. lessons
10. proposed_decisions
11. unresolved
12. recommended_next_action

Then the synthesis's path, its top-level headings, and the list of owner decisions in their order. Nothing else.
