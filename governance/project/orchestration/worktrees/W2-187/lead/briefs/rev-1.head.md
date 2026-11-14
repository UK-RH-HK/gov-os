# Brief rev-1: independent auditor (reviewer) for DAEO-0cd2 (W2-187), review round 1, profile FULL, class C2

You are a fresh, read-only independent auditor. You review ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden
set, judged every week at 95 %, counts only; the monthly fresh set as the check against fitting; the weekly maintenance
pass; the audit's state per repository; the schedule's code; the weekly secret scan and push) at the head below. You
wrote none of it and you write nothing in the repository: your findings and the verdict block are your return; your
lead writes the probe record from it. This is review round 1 of at most two (DEC-1010).

## What to probe
| what | path / value |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-187 |
| branch, head | w2/W2-187 at 5b82d1d53868625c43a5b8b2bb58492bad3f8038 |
| base (the claim) | 5336a6fca |
| the change | `git diff 5336a6fca..5b82d1d53 -- src/gov/memaudit src/gov/adopt/memory_sets.py governance/project/orchestration/tools/memaudit_cron.sh tests/unit/memaudit tests/unit/adopt tests/acceptance/W2-170 tests/acceptance/W2-171 tests/acceptance/W2-172 tests/acceptance/W2-187 docs/changes/W2-187-evidence.md docs/probes/DAEO-0cd2` (the two `w2/integrate` merges, 530635305 and f4fdc7fa1, bring other tickets' files: out of scope) |
| the ticket (KPI lines S1-S12, F1-F7, the Approach, the method, rabbit holes, the Interface I1-I12, the gaps and routings, the amendments, and I13 at the end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the packages and the CTO's answers | docs/probes/DAEO-0cd2/PACKAGE-W2-187-P1.md, PACKAGE-W2-187-S12.md |
| the engineer's evidence | docs/changes/W2-187-evidence.md |
| the acceptance suite's map | tests/acceptance/W2-187/README.md |
| the threat model | docs/adr/ADR-0001-threat-model.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1182, DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072, DEC-1156, DEC-1157, DEC-1010 |

**Readings settled by the CTO or the lead (judge against these):**
- **The I13 note** (the CTO, DEC-1157 (3), on I13 against W2-172 S9's unchanged files):
  - A no-declaration `push` prints `PUSH none: no declaration`, exits 0 and writes nothing. That line reaches the
    wrapper's own stdout.
  - A declared push writes its own `cron.log` line (the six keys, step `push`) and the DIGEST last line.
  - The wrapper calls `push` after any started audit step, on the live path and on today's path. Its exit stays the
    last audit step's.
- **S1, I3:** a used set's own run's `misses.jsonl` and `miss-classes.json` are skipped. A Wave 0 set lacking its
  record, or at another commit, is then `STANDING_SPENT 0`.
- **S2:** the week ledger reads `preflight, declaration, used, search`. The fresh path's pre-flight writes its own
  ledger line too.
- **S8:** a plain `status --repair` after `--residual` prints `REPAIR none` (I8's two forms).
- **The O8 (a) split of S10 and S11 was not taken.** The designer's estimate was under the trigger, and S10 and S11
  were built by then. The ticket's own source is about 1.5k insertions against est 700; size is not a finding.

**The lead's results** (do not re-run whole suites; small probes are yours):
- `gov accept W2-187` passes: 205 passed, 0 failed, every line `success-1` to `success-12` and `failure-1` to
  `failure-7` pass.
- `tests/acceptance/W2-170` 184 passed; `W2-171` 140 passed; `W2-172` 162 passed; `W2-173` 91 passed; `W2-88` 215
  passed; `tests/unit/memaudit` 354 passed.
- The scoped `lead_verify` runs in parallel.
- No QA engineer ran: the launcher has no `qa-engineer` role, so this review also carries the KPI trace. For each KPI
  line, say which tests and which code meet it, and whether a test could pass for the wrong reason.

**Look hard at:**
- counts only (S4, F1, F7): no id, question, gold, answer, citation, path or secret leaves a run folder or reaches a
  line, log, digest, ACT text or `REANCHOR` file;
- the one judged path (S3, F4): no second copy of the reader path; `prompts.py` unchanged;
- the week rule and use-once (S2, F2, F5), and fresh-path behaviour unchanged without `--week` and with no live set;
- F3: no command compares configurations;
- `maintain` never a gate and never changing a setting (S10, F6);
- the scan-then-push order and fail-closed scan (S12, F7);
- the keyed state (S9);
- writes outside `allowed_paths`.

## Held-out rules (DEC-820)
Never open the real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`, any `indep/` under it), any hidden
half or memory-verdict folder, the real crontab. Never a real model call, a real search, a real push to a real remote, or
a real gitleaks over a real repository. Probes plant everything in your sandbox's `$TMPDIR`. Any pytest goes through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
with a Bash timeout of 3600000 ms; a heavy-slot refusal is a wait. Search with the Read, Grep and Glob tools; if the first
search does not answer, search once more in different words (DEC-1065). No `gov retrieve`, no `gov context`.

The ticket's context packet (`gov context DAEO-0cd2 --role independent-auditor`, built by your lead from the integration
store) follows; the ticket file above is authoritative where they differ.

----

