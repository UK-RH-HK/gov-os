
## 277. The owner's answers of 2026-10-21 to lens H, with amendments, and the delegated split of W2-66 (register v0.277, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-889 — Lens H's packages decided, with the owner's amendments: the selection and the record-reading set refined; worksteal, per-test limits and JUnit XML; the glue; the tool trials; a review point before W2-66, W2-67 and W2-68; two re-pins planned; lens I
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat, after reading lens H's full report, the register draft and W2-66's ticket; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-881, DEC-883, DEC-884, DEC-880, DEC-852 item 3, DEC-887, DEC-888, DEC-866, DEC-861 · **Basis:** lens H's report, `docs/assessment/2026-10/H-test-strategy.md` (PARTIAL: trials cut by the close lock), its 19 findings and 9 packages.
- **Decision:**
  1. **P-H-2 (a).** W2-66 takes all of the following in:
     - shared test helpers followed (such as `w1_07_support`, imported by 14 suites);
     - the 263 serial tests;
     - a defined base for "the change": the last fully green commit, so that record-only commits between closes are inside a scoped close;
     - named paths for "the retrieval core";
     - the target's scope stated;
     - the record saying what was left out;
     - a selection form that does not break W1-35's collection (the full run's form, `pytest tests --ignore=…`).
     The measured map is a follow-up.
  2. **P-H-9 (a): DEC-883 refined.**
     - **Item 3:** a declared set of record-reading tests runs on every head, reused or not. It starts from gate (f)'s four files (W1-06's approvals, W1-08's path map, W1-27's path compliance, W1-07's envelope), with W2-54's green-here cases, W1-33's definitions and W1-49's window. The nightly reports a red outside the set as a selection miss.
     - **Item 4:** two fingerprints. The code fingerprint governs the code index; changed record files refresh their lexical and semantic text chunks; a lexical index whose record files differ is never fresh.
     - **Item 5:** W1-16's daemon tests and W1-09's race tests are tried in parallel (W2-57); latency tests stay alone; live and real-model tests move to the nightly.
     - **Item 2 b:** failing tests re-run alone before any bisect or attribution. A red that passes alone is a flaky candidate, not bisected. The batch's run keeps JUnit XML.
     - DEC-883's items 2 b, 3, 4 and 5 are marked "Changed by DEC-889" (DEC-866).
  3. **W2-66's size:** split into two FULL tickets in sequence (DEC-890, the orchestrator's call under the owner's delegation; the owner accepted it, 2026-10-21).
  4. **P-H-3:** yes. The nightly full run runs now, as an orchestrator script, in a quiet window. Its result goes into the next daily digest, and a red is a P1 package. W2-66's version replaces it later.
  5. **P-H-1:** yes, as proposed. The record-reading set runs after record commits too, widened.
  6. **P-H-4:** yes. Leads keep their full scope, but verify in the close's form (one parallel run, then the serial tests); the lead brief is updated.
  7. **P-H-5:** yes, W2-67 (test hygiene) after W2-66. It is adjusted now that the record is off the tree: the per-test copies and the nested reruns remain.
  8. **P-H-6:** yes (the capability is built inside the existing tickets). **P-H-7:** yes, riding in W2-65. **P-H-8:** delegated to the orchestrator.
  9. **Lens H's unfinished trials** (the 9 planted faults, among them those in the three widest-reaching modules, and the 65 mutation items) run on a clone, in quiet windows, never during a close.
  10. **P-REC-1: decided (a) and done** (DEC-887). The raw record is on `record/w2`, verified byte for byte, and left the tree in one commit (`dbd3cc53`).
  11. **The owner's additions, from lens H's findings:**
      - a. **Finding 13:** `--dist worksteal` in the nightly script and the leads' verification now, and as a W2-66 KPI for the close's parallel run, confirmed by trial b (item 13).
      - b. **Finding 16:** per-test time limits. They apply in the nightly and the leads' verification now, and in the close through W2-66. The mechanism is pytest-timeout or the close's own per-test limit, chosen from trial a (item 13).
      - c. **Finding 10:** the test-design skill gains test kinds, run-time cost, whole-tree copies and live-repository tests, as a W2-11 KPI.
      - d. **Finding 12:** W2-48's recorded lesson is corrected, in DEC-880, W2-66's Why and the list, to the measured causes:
        - folder listings: 7,076 tests;
        - undeclared reads: 3,750;
        - dot-files: 125;
        - child processes the cache cannot follow: only about 500.
      - e. **Finding 4:** the 15-minute target's scope is stated, with what reaches it: W2-66, W2-68, W2-57's serial rework and worksteal.
  12. **Glue, as lens H rates them.**
      - **Now:**
        - JUnit XML on every run (the close, the nightly, the leads);
        - `git bisect run` for nightly failures;
        - coverage.py with lens H's shim as the measured map in the nightly;
        - pytest-rerunfailures and pytest-randomly in the nightly only, as signals, never to pass a gate.
      - **Later, as rows:**
        - cosmic-ray for diff-scoped mutation testing on FULL core tickets; diff-cover; pytest-split for CI;
        - for UPIM and ASMO: cargo-nextest, Vitest or Jest, and Nx or Turborepo, through W2-19.
      - **Pants is not adopted now:** it is a whole build system, static, and blind to the tests' `gov` command-line calls. A row revisits it for UPIM and ASMO.
  13. **The tool trials** run on a clone, in quiet windows, never during a close. The owner installed the candidates, as an owner act, in `/tmp/gov-os-tooltrial`: a venv with `--system-site-packages`, recorded as an owner trial install, not in the tool registry.
      - **The installs:**
        - pytest-timeout 2.4.0 (sha256 `c42667e5cdadb151aeb5b26d114aff6bdf5a907f176a007a30b940d3d865b5c2`);
        - pytest-rerunfailures 16.7 (sha256 `edf1886209c2b7dafe35b5bf1708d6ec40ccf6c6b357f0f02807efcec0204c99`);
        - pytest-randomly 5.0.0 (sha256 `8a0d4703115c0c25b38b6e129fc16b1947b9643ff26a41bc1d185d7e5a7689c1`);
        - grimp 3.17 (sha256 `ecf26d99a35ab7b5966af56118bb9344d1fd1b972d3c45dd5012effc7a68c844`).
      - **The trials, with lens H's remaining ones:**
        - a. pytest-timeout: does a per-test limit fire inside a test whose code runs in a child `gov` process (a hang planted in a child-only path)? And its cost on a full run.
        - b. `--dist worksteal`: a full parallel run with and without it, measured (the tail and the total).
        - c. grimp: its selection against the declared map on lens H's planted faults (recall and test time).
        - d. pytest-rerunfailures and pytest-randomly: one dry run each in the nightly's form, as signals only.
      - `/tmp/gov-os-tooltrial` is removed when done, and its removal shown.
  14. **The review point (standing for this decision).** When lens H's remaining trials, the tool trials and lens I's test review (item 16) have reported, the orchestrator stops before any W2-66, W2-67 or W2-68 work and drafts, taking every result in (for example, widening the shared core if the declared map misses faults in the widest-reaching modules):
      - **W2-66's ticket file and card:** selection and evidence only. That is P-H-2's items, P-H-9's record-reading set, the evidence block with JUnit XML, worksteal and the time limits, the corrected Why, and the record-only list updated now that the raw record is off the tree.
      - **W2-68's:** batching, reuse, the two fingerprints, the red-batch handling, the trial.
      - **W2-67's:** the per-test copies and the nested reruns.
      - **W2-57's ticket file:** P-H-9 item 5.
      - **The re-pin plan of item 15.**
      Then it pings the owner (ACT) with the Windows paths of the four drafts, the trials' results and the test review's report, and waits for the owner's final decisions.
  15. **The re-pin, for the owner's review with the cards:** instead of one combined re-pin after W2-68 (DEC-884), plan two.
      - The first comes after W2-66 merges and passes its ladder trial. It carries W2-58, W2-59, W2-65 and W2-66, so that scoped closes start earlier.
      - The second comes after W2-68, for batching.
  16. **Lens I, an independent test review against the specifications in force.** The DEC-866 sweep finds tests that cite a superseded decision. It cannot find tests that encode an old behaviour, test a removed or replaced feature, or fail for a cause nobody has established.
      - a. **The auditors:** fresh independent auditors (Opus 5.5, highest effort, the same rules as the other lenses: reads open, they change no file, each writes only its report under `docs/assessment/2026-10/`). They are split by area so they run in parallel:
        - (1) the guard, the launcher and the sandbox;
        - (2) `gov close`, the checks and the ratchet;
        - (3) retrieval, context, checkpoints and resume;
        - (4) records, the plan, tickets and the remaining suites.
        They run in quiet windows, never during a close, under the resource gate.
      - b. **What each reviews**, against Contract v4.2 and the decisions in force (superseded entries marked):
        - first, every test that is failing or questionable: the accepted reds (W1-42's two), every `load_sensitive` entry, every serial-only entry, every test that failed in Wave 2's closes or the rehearsal, and every test lens H found never failing or duplicated;
        - then every suite of a closed ticket whose feature a later decision changed (the guard's read rules, the close, the launcher, the context window, the cache, the resume);
        - then a sample of the rest.
      - c. **One verdict per test reviewed**, with its evidence and the decision or Contract item it rests on:
        - valid and needed;
        - outdated: the expected behaviour changed (name the decision);
        - obsolete: the feature was removed or replaced;
        - duplicate;
        - weak: it cannot fail for the fault it claims to catch;
        - flaky, with the cause found by running it, alone and under load, not guessed;
        - not reproducible.
      - d. **No test is changed by the review.** Revisions go to independent test designers in the owning or a new small ticket, each with a `Rewrite-Reason:`. Retiring a test is the owner's decision: each proposed retirement comes as an owner package with its evidence.
      - e. **A short synthesis across the areas:** counts per verdict, the close time it would save, what it changes for W2-66's map and W2-57's serial list, and owner packages in the six-part format.
  17. **Rows:**
      - (a) lens H's owner-approved trial installs were refused by the guard, which does not read briefs; owner-approved installs into a named `/tmp` environment must actually work next time;
      - (b) Pants, as in item 12.
  18. **Meanwhile** the close queue (W2-02 included, now that DEC-886 is committed, `cf8219a8`), the nightly run, W2-65 stacked on W2-59, and the held resumes run as the machine allows.
- **Changes:**
  - DEC-883 items 2 b, 3, 4 and 5 (refined);
  - DEC-880 item 2 (the lesson's measured causes) and item 2 (b) (the leads' verification keeps its scope, in the close's form);
  - DEC-852 item 3 (the nightly from now, as a script);
  - DEC-884 item 2 (one combined re-pin) and item 1 (W2-66 first): two re-pins planned for the owner's review, and W2-66, W2-67 and W2-68 wait for the review point.
- **Where it goes (DEC-851):**
  - this register, with DEC-880's, DEC-883's, DEC-884's and DEC-852's status lines marked;
  - the prompt §3 and §15 (v3.11);
  - `LEAD-w2-common.md` (the close's form, worksteal, JUnit XML; the per-test limit after trial a);
  - RESUME HERE;
  - the cards and ticket files of W2-11 (finding 10), W2-65 (P-H-7) and W2-19 (P-H-8's ratchet field-rule case);
  - the WBS's W2-48 card, the plan §4.2 and the ticket `DAEO-xxgp` (the lesson);
  - the list's rows.
  W2-66's, W2-67's, W2-68's and W2-57's cards come as drafts at the review point (item 14).
- Next free id: DEC-890.

### DEC-890 — W2-66 split in two FULL tickets in sequence; P-H-8's corrections (delegated; the split accepted by the owner)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-21; the owner accepted the split in the chat, 2026-10-21) · **Under:** DEC-889 items 3 and 8, DEC-884, DEC-866, DEC-802 · **Basis:** W2-66 would carry DEC-880 item 2, DEC-883 and DEC-889 at about 550 to 700 lines (lens H's estimate), in the judge's own code, under one FULL review.
- **Decision:**
  1. **The split, for review's sake.** Each ticket's review fits its own question, and the first ships the evidence the second relies on.
     - **W2-66** (`DAEO-c1uz`): selection and evidence. It covers:
       - the path-to-suite selection with test-side imports, against the last fully green commit, in the full run's form;
       - the shared core and anything unplaced widening to everything;
       - the serial tests' scoping;
       - the declared set of record-reading tests on every head;
       - the record's evidence block (scope, commit, tree, what ran, what was skipped or left out, and why, with JUnit XML), with the schema line in W2-64;
       - `--full`, worksteal and the per-test limit;
       - the nightly command that replaces the orchestrator's script;
       - the 15-minute target, measured.
       About 350 to 400 lines.
     - **W2-68** (new, FULL): batching, reuse and the fingerprints. It covers:
       - DEC-883 items 1 and 2 (the batch; the red batch, with failing tests re-run alone first, then bisect);
       - item 3 (same-code reuse, the record-reading set always run);
       - item 4 (two fingerprints, the record chunks refreshed incrementally);
       - its trial on a dev tier or fixture (DEC-884 item 4).
       About 300 lines. It starts when W2-66 has merged.
     - The re-pins follow DEC-889 item 15, once the owner has reviewed the plan.
  2. **P-H-8, applied:**
     - the stale cache texts in W2-19's KPI, W2-38's KPI, W2-07's paths and row W2-L207's triage reason;
     - DEC-880's re-baseline note names CAP-39.c (dependency-aware selection) beside CAP-53.b;
     - the ratchet's field rule (every entry names its fix) gets one acceptance case per list in W2-19's KPIs (DEC-802);
     - each fix row of a `load_sensitive` entry that points to Wave 3 gets a target date in the list (the entries themselves stay the owner's, DEC-862);
     - the 22 serial-only entries not on `load_sensitive`, and W2-57's ticket file, come in W2-57's draft at the review point.
- Next free id: DEC-891.

| Version | Date | Change |
|---|---|---|
| 0.277 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-889 (lens H's packages decided with the owner's amendments; P-REC-1 done; worksteal, per-test limits, JUnit XML; the glue now and later; the owner's tool trials; the review point before W2-66, W2-67 and W2-68; two re-pins planned; lens I, the test review). Delegated, the split accepted by the owner: DEC-890 (W2-66 and W2-68; P-H-8's corrections). Next free id: DEC-891. |
