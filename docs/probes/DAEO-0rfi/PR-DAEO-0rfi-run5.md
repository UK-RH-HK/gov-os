---
type: probe
task: DAEO-0rfi
reviewer_session: 4a232e30-2b53-42df-b683-5b231525a33f
implementer_session: cf375c20-03b8-446b-8581-07b1bb46be39
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: ed2037fd6a5821f7c4e96e0dae4d25cc75b96c06
---

# Probe record: W2-54 (DAEO-0rfi), run 5 (DEC-874), the second and last review (DEC-413)

- **What was probed.** Head `ed2037fd6a5821f7c4e96e0dae4d25cc75b96c06` of `w2/W2-54` (CP-DAEO-0rfi-0034): run 5's
  whole change since `226ec458` — the merge-back `de42a87d` of `w2/integrate` (`a2e7b691`), the corrections of
  the four cases on W2-02's other types to KPI S4's meaning (DEC-874 item 1: W2-54's own commits bring in no
  schema file and no type of W2-02's beyond `audit-report`, before and after W2-02 merges) — the test designer's
  `49f1f81e` (session `14884e7b-5fd9-499f-9cc9-acf07e39ece4`), the engineer's `40909d21` (session
  `cf375c20-03b8-446b-8581-07b1bb46be39`, the builder test) — and the second test-design batch `92ba6f02` (session
  `4aff6f98-dca6-4884-826d-ab2b54a8788a`), which answered the first review's finding that one case did not read
  the history it named. The code is unchanged since the probe of `7661402c` (`PR-DAEO-0rfi.md`).
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session
  `4a232e30-2b53-42df-b683-5b231525a33f`, 2026-10-20), started through `gov launch` under its OS sandbox with the
  reading tools alone; commissioned and judged by the orchestrator (DEC-137). It wrote nothing in the repository:
  the lead's tripwire before and after its session shows no change in this worktree. The first review of run 5
  (session `0f50d90c-c613-4241-8e21-a5c7f594e5bb`, head `0ccafe25`) passed with four rows; its record stays a
  draft, as the head changed after it.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent
  mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines,
  `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; only "yes" with "fails open"
  or "loses work" fails the probe. The orchestrator's judgement: no finding is both; R1 to R5 are rows.

## The reviewer's record

Verdict: pass

**Head probed:** `ed2037fd6a5821f7c4e96e0dae4d25cc75b96c06` on `w2/W2-54` (run 5: merge-back `de42a87d`, corrections `49f1f81e` and `40909d21`, second batch `92ba6f02`, checkpoints `0ccafe25` and `ed2037fd`).

**Step 0:** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0rfi` failed ("Read-only file system", exit 1). (b) `git hash-object -w --stdin` gave `1ae28402…` and `git update-index --refresh` worked (exit 0). `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-0rfi`, top level `/home/usain/gov-os-worktrees/W2-54`, branch `w2/W2-54`, head `ed2037fd`.

**gov.__file__:** `/home/usain/gov-os-worktrees/W2-54/src/gov/__init__.py` (with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src`).

**gov retrieve:** used once, asking about DEC-874 and run 5. It gave no evidence (`FACET_UNAVAILABLE`; lexical and semantic both "stale"), so I read the register and the commits directly.

**Guard refusals:** read refusals (DEC-849): 0. There was one write refusal: a Bash command that wrote a script into my temp folder by heredoc was refused as a write to `/home/usain/gov-os-worktrees/W2-54/-`, a misreading of the shell text. I wrote the script into my temp folder with the Write tool instead. The harness also once declined a command that removed a temp subfolder; I re-ran it without the removal.

**Probed and found sound**

1. **Each parametrisation reads the history it names (the first review's F1 is fixed).** The readings give 43 own commits on HEAD, 38 on `4ce16df2` and `w2/W2-02`, and 0 on `2a35fd7b` and `main`. A revision that does not exist gives git's "bad revision". The last own commit to core-schema's module is `4f753c72` in both histories, with 11 added lines and none naming `close` or `adoption-verdict`. Without `--full-history`, the module walk on the real `4ce16df2` misses `4f753c72`. With the first batch's reading swapped in, or with the second batch's reading minus `--full-history`, all four module parametrisations go red on this repository through the new self-check. That self-check therefore guards against both defects.
2. **The corrections keep S4's meaning (DEC-874 item 1).** I ran the cases' own bodies (and the unit test's) against histories built from scratch, modelled on W2-54's and W2-02's real shapes, using single files from this repository. W2-54's own commit brought a W2-02 type or schema file in through nine forms:
   - a type-map entry on one line;
   - a type-map entry split over two lines;
   - the standalone types on one line;
   - the standalone types over several lines;
   - the standalone types as one split string;
   - an item assignment;
   - W2-02's whole module;
   - a schema file under the template folder, and one under the installed folder;
   - a rename into the close schema file.

   Each made the matching acceptance case fail on both `[HEAD]` and `[4ce16df2]`. The split-string form is caught by the core-schema run of W2-54's last own module, not by the line reading.

   The cases pass when only another ticket's commits bring the types in, including through a W2-54 merge. They also pass on:
   - the real shape;
   - W2-02's branch after it re-merges `w2/integrate` (which then holds run 5);
   - `w2/integrate` after W2-02's merge.

   These are the next histories DEC-874 item 3 creates.
3. **What counts as W2-54's own commits is complete and exact.** The trailer reading gives the same 43 commits as a search for the `Task: DAEO-0rfi` line. The five other text hits are other tickets' commits that only mention W2-54. Every non-merge commit on W2-54's first-parent line since its claim carries `Task: DAEO-0rfi`. The four own commits off that line are the orchestrator's records on `w2/integrate`, touching no schema file or module.
4. **No other expectation changed.** Run 5 removed only the four cases' old bodies. The support module only gained lines. There is no skip, xfail or deselection. The counts are 24 in the file and 99 in the suite (97 collected, 2 deselected). Every rewrite carries `Rewrite-Reason: DEC-874`, and each commit's `Role:` matches the paths it changed. No other test in `tests/` still judges the tree for W2-02's types.
5. **The merge-back (DEC-750, DEC-754) is sound.** `de42a87d` is a two-parent `--no-ff` merge carrying `Task: DAEO-0rfi`, not `-s ours`. Its tree equals git's own merge of its parents, which is `w2/integrate`'s tree, because W2-54's branch was already inside it. W2-54's paths are identical in both parents and the merge, and W2-54's code is identical to the probed `7661402c`. Nothing was lost.
6. **The two known reds come from the merged tree, not W2-54's change.**
   - Core-schema's only finding is W2-53's close record (type `close`), added by `a1565e56` under `Task: DAEO-7rr2` and absent before the merge. W2-02's own module and schema files judge that record clean.
   - Secrets-indexing: no line that W2-54's 43 own commits add holds a secret by the project's rules. `gov close` runs the suites in the project root, a full repository, so the cases' git readings have history there. The W1-43 report is untouched (sha256 `b14e17d6…cdac1d`).

**Classification:** 0 findings that fail the probe (yes + fails open or loses work); 5 rows (R1–R5).

**Findings (all rows)**

- **R1 — the unit test reads less than the acceptance cases (the first review's F2, confirmed and unchanged by the second batch).** What was done: own commits wrote `adoption-verdict` into the standalone types over several lines or as one split string, added `close` to the type map by an item assignment, or changed W2-02's close schema after W2-02's merge. What happened: the unit test passed each of these. What should have happened: it should fail each, as the acceptance cases do on both histories. Severity: low.
  - Ordinary work: yes, because an engineer could plausibly write the types over several lines or by assignment.
  - Consequence: other — the acceptance cases fail on every such form, so S4's gate does not fail open.
- **R2 — the unit test's reading inherits the user's git configuration, but its self-check does not.** What was done: git colour forced to "always" in the environment. What happened: the unit test's line reading of the real history saw no added lines, while its built-history self-check, run under an isolated configuration, stayed green. The acceptance cases failed closed through their own self-checks. What should have happened: the unit test's reading and its self-check should run under one configuration, or be immune to colour. Severity: low.
  - Ordinary work: no, because no colour, diff or log setting exists in this environment's git configuration, and "always" is not git's default.
  - Consequence: other — the acceptance cases fail closed under that setting.
- **R3 — a hand edit inside one of W2-54's own merges is not read (the first review's F3, unchanged).** What was done: a built own merge whose resolution added a `close` type map entry that neither parent held. What happened: all 8 cases passed. What should have happened: that line would count as W2-54's own change. Severity: low.
  - Ordinary work: no, because DEC-754 item 4 makes the orchestrator's merges plain git merges with no hand edits. A merge that takes `w2/integrate`'s side brings W2-02's change, which is rightly not counted (shown on a built history).
  - Consequence: fails open (for that construction only).
- **R4 — a later own edit of core-schema's module after W2-02's merge turns the module cases red.** This is the limit the README states under "Risk". What was done: W2-54 merges `w2/integrate` holding W2-02's types, then makes an unrelated own edit of the module. What happened: `[close-HEAD]` and `[adoption-verdict-HEAD]` failed, although W2-54 added no type; the line reading stayed green. What should have happened: the cases should judge only what W2-54's own commits add. Severity: low.
  - Ordinary work: yes, because a future W2-54 resume after W2-02's merge could touch that module.
  - Consequence: other (fails closed; it would block W2-54's close until the case is corrected).
- **R5 — the secrets-indexing hit is in a derived store, not in W2-54's change (the first review's F4, re-judged and unchanged).** What happened: `gov check` reports a secret in the code-graph store's bytes. Checked: the project's own rules find no secret in any line W2-54's 43 own commits add. What should have happened: the store holds no secret; W2-54's change is not its source. Severity: low.
  - Ordinary work: no, because the hit is in a derived store's raw bytes and in no line of W2-54's own change.
  - Consequence: other (fails closed).

**Risks, not findings (from the lead's figures; I did not run them):** the context check ran 609 s against its 600 s limit at a load near 60, and 279 s alone. The change record's measurement (128–164 s for 106 tickets) predates later rounds and the merge-back (110 tickets now). W2-54's slow cases are not on `tests/acceptance/serial-only.txt`, so a close under heavy parallel load could refuse on them (fails closed). A quiet window for the close avoids that.
