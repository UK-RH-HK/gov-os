
## 275. The owner's answers of 2026-10-21 to lens H, and the orchestrator's delegated split of W2-66 (register v0.275, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-887 — Lens H's packages: P-H-2 (a), P-H-9 (a) refining DEC-883, the nightly now, the record-reading set after record commits, the leads' verification in the close's form, W2-67, the capability inside the tickets
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-881, DEC-883, DEC-884, DEC-880, DEC-852 item 3, DEC-866, DEC-861 · **Basis:** lens H's report, `docs/assessment/2026-10/H-test-strategy.md` (PARTIAL: trials cut by the close lock), its 19 findings and 9 packages.
- **Decision:**
  1. **P-H-2 (a).** W2-66 takes all of the following in before its test designer starts:
     - shared test helpers followed (such as `w1_07_support`, imported by 14 suites);
     - the 263 serial tests;
     - a defined base for "the change": the last fully green commit, so that record-only commits between closes are inside a scoped close;
     - named paths for "the retrieval core";
     - the target's scope stated;
     - the record saying what was left out;
     - a selection form that does not break W1-35's collection (the full run's form, `pytest tests --ignore=…`).
     The measured map is a follow-up.
  2. **P-H-9 (a): DEC-883 refined.**
     - **Item 3:** a declared set of record-reading tests (starting from gate (f)'s four files: W1-06's approvals, W1-08's path map, W1-27's path compliance and W1-07's envelope, with W2-54's green-here cases, W1-33's definitions and W1-49's window) runs on every head, reused or not. The nightly reports a red outside the set as a selection miss.
     - **Item 4:** two fingerprints. The code fingerprint governs the code index; changed record files refresh their lexical and semantic text chunks; a lexical index whose record files differ is never fresh.
     - **Item 5:** W1-16's daemon tests and W1-09's race tests are tried in parallel (W2-57); latency tests stay alone; live and real-model tests move to the nightly.
     - **Item 2 b:** failing tests re-run alone before any bisect or attribution; a red that passes alone is a flaky candidate, not bisected; the batch's run keeps JUnit XML.
     - DEC-883's items 2 b, 3, 4 and 5 are marked "Changed by DEC-887" (DEC-866).
  3. **W2-66's size:** if it is safer for review, the orchestrator splits it into two FULL tickets in sequence (selection and evidence first, then batching, reuse and the fingerprints). The owner delegates this call. Either way there is one combined re-pin after both, as DEC-884 says.
  4. **P-H-3:** yes. The nightly full run starts now, as an orchestrator script, in a quiet window; its result goes into the next daily digest, and a red is a P1 package. W2-66's version replaces it later.
  5. **P-H-1:** yes, as proposed: the record-reading set runs after record commits too, widened.
  6. **P-H-4:** yes. Leads keep their full scope, but verify in the close's form (one parallel run, then the serial tests); the lead brief is updated.
  7. **P-H-5:** yes, W2-67 (test hygiene) right after W2-66.
  8. **P-H-6:** yes (the capability is built inside the existing tickets). **P-H-7:** yes, riding in W2-65. **P-H-8:** delegated to the orchestrator.
  9. **Lens H's unfinished trials** run after the queue and are reported before W2-66's test designer starts: the 9 planted faults (among them those in the three widest-reaching modules) and the 65 mutation items.
  10. **A package, not a decision yet:** how to keep Policy 1 while the raw orchestration record (73 % of the tree) leaves the checked-out tree (P-REC-1).
- **Changes:** DEC-883 items 2 b, 3, 4 and 5 (refined); DEC-880 item 2 (b) (the leads' verification keeps its scope, in the close's form); DEC-852 item 3 (the nightly from now, as a script, not from W2-66's merge).
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §3 and §15 (v3.10);
  - `LEAD-w2-common.md` (P-H-4);
  - RESUME HERE;
  - the cards and ticket files of W2-66, W2-68 (new), W2-67 (new), W2-65 (P-H-7) and W2-57 (P-H-9 item 5);
  - the list's rows.
- Next free id: DEC-888.

### DEC-888 — W2-66 split in two FULL tickets in sequence; P-H-8's corrections (delegated)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-21; listed in the digest; the owner overturns it at will) · **Under:** DEC-887 items 3 and 8, DEC-884, DEC-866, DEC-802 · **Basis:** W2-66 would carry DEC-880 item 2, DEC-883 and DEC-887 at about 550 to 700 lines (lens H's estimate), in the judge's own code, under one FULL review. The owner delegated the split (DEC-887 item 3).
- **Decision:**
  1. **The split, for review's sake.** Each ticket's review then fits its own question, and the first ships the evidence the second relies on.
     - **W2-66** (`DAEO-c1uz`): selection and evidence. It covers:
       - the path-to-suite selection with test-side imports, against the last fully green commit, in the full run's form;
       - the shared core and anything unplaced widening to everything;
       - the serial tests' scoping;
       - the declared set of record-reading tests on every head;
       - the record's evidence block (scope, commit, tree, what ran, what was skipped or left out, and why), with the schema line in W2-64;
       - `--full`;
       - the nightly command that replaces the orchestrator's script;
       - the 15-minute target, measured.
       About 350 to 400 lines.
     - **W2-68** (new, FULL): batching, reuse and the fingerprints. It covers:
       - DEC-883 items 1 and 2 (the batch, the red batch with failing tests re-run alone first, then bisect);
       - item 3 (same-code reuse, the record-reading set always run);
       - item 4 (two fingerprints, the record chunks refreshed incrementally);
       - its trial on a dev tier or fixture (DEC-884 item 4).
       About 300 lines. It starts when W2-66 has merged.
     - One combined re-pin after both: W2-58, W2-59, W2-65, W2-66 and W2-68.
  2. **P-H-8, applied:**
     - the stale cache texts in W2-19's KPI, W2-38's KPI, W2-07's paths and row W2-L207's triage reason;
     - DEC-880's re-baseline note names CAP-39.c (dependency-aware selection) beside CAP-53.b;
     - W2-57 gets its ticket file;
     - each `load_sensitive` entry whose fix is a Wave 3 row gets a target date;
     - the 22 serial-only entries not on `load_sensitive` are listed for W2-57;
     - the ratchet's field rule (every entry names its fix) gets one acceptance case per list in W2-19's KPIs (DEC-802).
- Next free id: DEC-889.

| Version | Date | Change |
|---|---|---|
| 0.275 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-887 (lens H's packages: P-H-2 (a), P-H-9 (a) refining DEC-883, nightly now, the record-reading set after record commits, the leads' verification in the close's form, W2-67, P-H-6, P-H-7 in W2-65, P-H-8 delegated, the unfinished trials after the queue, P-REC-1 a package). Delegated: DEC-888 (W2-66 split into W2-66, selection and evidence, and W2-68, batching, reuse and fingerprints; P-H-8's corrections). Next free id: DEC-889. |
