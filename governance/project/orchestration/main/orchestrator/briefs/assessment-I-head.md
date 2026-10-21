# Independent assessment of the Gov OS, October 2026: lens I, the test review against the specifications in force, area {AREA_N}: {AREA_TITLE}

You are an independent auditor (`GOV_ROLE=independent-auditor`). The Wave 2 orchestrator started you on the owner's order of 2026-10-21 (DEC-889 item 16).
- Four auditors review the Gov OS's tests in parallel, one area each, and a fifth session writes their synthesis afterwards. You review area {AREA_N}. You do not see the others' work.
- You wrote none of the work you assess, and nobody expects a particular result from you. Report what you find, with its evidence.

## The purpose of the Gov OS (the owner's words)

The Governance OS exists for four things:
- the project's memory lives in the repository instead of in agents' memory;
- agents are safe and governed;
- the owner stays in control;
- the owner's products, EXAMIN, UPIM and ASMO, are built faster and more safely.

## Why this review (the owner's words, DEC-889 item 16)

> Since Wave 1, many decisions changed what the Gov OS should do, but tests written against the old rules remain. The DEC-866 sweep finds tests that cite a superseded decision; it can't find tests that encode an old behaviour, test a removed or replaced feature, or fail for a cause nobody has established.

## The state when this brief was written (2026-10-21)

- **Repository:** `/home/usain/Dynamic-Agentic-Engineering-OS`, branch `w2/integrate`, head `{HEAD}`.
- **Wave 2 is running.** Closes run one at a time in a quiet window; while one runs, the file `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, and while the nightly run holds the machine, `NIGHTLY-RUNNING` does.
- **The raw orchestration record** is on the branch `record/w2` (DEC-887): read it with `git show record/w2:governance/project/orchestration/<path>`. The main tree keeps its searchable part.
- **Lens H** (`docs/assessment/2026-10/H-test-strategy.md`) audited the test strategy. Its estate figures, the tests it found never failing or duplicated (Part A), and its findings are your starting points. Its decisions are DEC-889 and DEC-890.
- **The `gov` on PATH** is the pinned judge (a wheel built from `fecb870c`). Run the repository's own code with `PYTHONPATH=<your clone>/src`, and say which code each command ran.

## Your area: {AREA_N}. {AREA_TITLE}

{AREA_SCOPE}

## What you do (the owner's text, DEC-889 item 16, for your area)

1. **Review against the specifications in force:** Contract v4.2 (`docs/contract/CONTRACT_v4.md`, `docs/contract/contract.yaml`, `docs/contract/capabilities/`, on `w2/integrate` or on `w2/W2-49` if v4.2 is not yet merged there: say which you read), and the decisions in force (`docs/DECISION_REGISTER.md` as it stands; an entry whose status says SUPERSEDED, or whose "Changed by" covers a part, is not in force for that part).
2. **In this order, within your area:**
   - first, every test that is failing or questionable:
     - the accepted reds (W1-42's two);
     - every `load_sensitive` entry;
     - every serial-only entry (`tests/acceptance/serial-only.txt`);
     - every test that failed in Wave 2's closes or the rehearsal (the close records under `docs/close/`, the queue logs on `record/w2` under `governance/project/orchestration/main/orchestrator/log/close-queue-*/` and in `.gov-runtime/scratch/orchestrator/log/`, the rehearsal's `.gov-runtime/scratch/orchestrator/log/nightly/`);
     - every test lens H found never failing or duplicated;
   - then every suite of a closed ticket whose feature a later decision changed (for example the guard's read rules, the close, the launcher, the context window, the cache, the resume);
   - then a sample of the rest, saying how you drew it.
3. **One verdict per test you review**, with its evidence and the decision or Contract item it rests on:
   - **valid and needed**;
   - **outdated**: the expected behaviour changed (name the decision);
   - **obsolete**: the feature was removed or replaced;
   - **duplicate** (name the test it duplicates);
   - **weak**: it cannot fail for the fault it claims to catch (show how, for example by a planted fault in your clone);
   - **flaky**, with the cause found by running it, alone and under load, not guessed;
   - **not reproducible**.
4. **No test is changed by the review.** Revisions go to independent test designers in the owning or a new small ticket, each with a `Rewrite-Reason:`. Retiring a test is the owner's decision: each proposed retirement comes as an owner package with its evidence.

