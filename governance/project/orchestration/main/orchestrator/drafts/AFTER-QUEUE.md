# What to do when queue run 4 ends (in order)

1. **If a close was refused:** handle it first.
   - DEC-886's trigger means W1-07's `doctor` case and nothing else: follow `ACT-DEC-886-load-sensitive.md`.
   - Any other red: a P1 package and a ping.
2. **Copy lens H's report,** byte for byte: `.gov-runtime/scratch/assessment/2026-10/H-test-strategy.md` → `docs/assessment/2026-10/H-test-strategy.md` (sha256 `b10437c3…f173`).
3. **Register:** append `register-274-DEC-886.md` (if not already committed at a trigger), then `register-275-DEC-887-888.md`.
   - Mark DEC-883's status line: `Changed by: DEC-887 (items 2 b, 3, 4, 5 refined) and DEC-888 (items 1 to 4 move to W2-68)`.
   - Mark DEC-880's: `(b) the leads' verification keeps its scope, in the close's form (DEC-887 item 6)`.
   - Mark DEC-852's: `item 3 starts now as an orchestrator script (DEC-887 item 4)`.
   - Mark DEC-884's: `W2-68 joins the combined re-pin (DEC-888)`.
4. **W2-66's card and ticket:**
   - Scope reduced to selection and evidence, with P-H-2's seven items, P-H-9's record-reading set on every head, and the nightly command.
   - Batching, reuse and fingerprints move out to W2-68.
   - Paths: `select.py`, `nightly.py`, `command.py` (calls, `--full`, the record block), the path map's shared-core and record-reading lists, tests, the research record.
   - The `repo.py`, `store/**`, `batch.py` and `fingerprint.py` paths move to W2-68.
   - About 400 lines.
5. **W2-68:** `tk create`, then the ticket file and card. It holds DEC-883 items 1 to 4 as refined by DEC-887 item 2, the ladder (DEC-884 item 4) and the paths above; FULL, about 300 lines; it starts after W2-66 merges.
6. **W2-67:** `tk create`, then the ticket file and card. It holds P-H-5: the copy helpers copy `git ls-files` minus the record, per-test copies become a session copy with a reset, nested reruns move to the nightly; independent-test-designer only, `Rewrite-Reason:` on each change; about 150 to 250 lines; right after W2-66.
7. **W2-65's card and ticket:** P-H-7 rides along (the SubagentStop hook prints its reason on stderr, or emits `{"decision":"block","reason":…}`, with one acceptance case); paths + `template/governance/kernel/hooks/subagentstop.py`.
8. **W2-57's card and ticket file** (new file, P-H-8): DEC-883 item 5 as refined (daemon and race cases tried in parallel, latency alone, live and model to the nightly), and the 22 serial-only entries not on `load_sensitive`.
9. **P-H-8's corrections:** W2-19's KPI text, W2-38's KPI, W2-07's paths, W2-L207's reason, DEC-880's CAP-39.c note, the target dates of Wave 3 fixes in the `load_sensitive` rows, and W2-19's KPI for the ratchet field rule.
10. **Prompt v3.10:**
    - §3: W2-66 then W2-68 (then W2-67); the combined re-pin after W2-68;
    - §15: the nightly script now (`tools/nightly.sh`), its result in the digest, a red a P1 package;
    - §15: the record-reading set in `tools/record_checks.sh` and gate (f).
11. **`LEAD-w2-common.md` (P-H-4):** the full verification in the close's form. Keep the scope (every suite, `tests/unit`, the collection, `gov check`), and run it as one parallel `pytest tests -n auto` with the serial-only cases afterwards (the close's plugin `gov_close_serial_only`), with `--junitxml`.
12. **Rows:** lens H's findings, those not already a ticket's KPI, as list rows (finding numbers in the sources).
13. **`close_queue.sh`:**
    - wait while `NIGHTLY-RUNNING` exists;
    - gate (f) gains W2-54's green-here file, W1-33's definitions and W1-49's window.
14. **Run** `tools/record_checks.sh` (with the record-reading set), commit (decision-record, owner), sync, commit working memory.
15. **Then, in the background:** lens H's rest (`bash /tmp/gov-os-assessment-H/scripts/run_rest.sh`), then the first nightly (`tools/nightly.sh`). Report lens H's rest before W2-66's test designer.
16. **Bring P-REC-1** (`drafts/P-REC-1.md`, to `governance/project/orchestration/packages/`) with the report.
17. **Free slots:** W2-65 (stacked on `w2/W2-59`); then the held resumes by keystone.
