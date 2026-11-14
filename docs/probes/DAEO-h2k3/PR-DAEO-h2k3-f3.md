---
type: probe
task: DAEO-h2k3
kind: "narrow independent check (DEC-1154) of the S4/F3 revision under DEC-1178 (1): each gold source judged at its own commit; a moved block no fault; a changed block listed by file and entry; not a round, DEC-1010"
reviewer_session: "4312c571-0b45-4a28-a4f6-8bad354a8f06 (independent-auditor, claude-opus-5-5, high, C2)"
implementer_session: "498ecb44-f333-4a3e-a0ac-b8c161e6061a (td-4, independent-test-designer, claude-sonnet-5-5, high, C2; commit 3bc8fe6d15b6f5d1845209608038f2f0db12d5cf)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: dda647a49eaa51782442b7c4203bf70de487809d
date: 2026-11-14
decisions_applied: [DEC-1178, DEC-1154, DEC-1084, DEC-828]
---

# Narrow check of W2-61h's S4/F3 revision (DEC-1178 (1))

The lead's triage: N1, N2 and N3 are rows (none is in scope with ordinary work yes and fails open or loses work); no
round. N1 (an entry listed twice when two alternatives both changed) and N3 (no planted anchor-miss red for q21-q24)
are rows for the next test-design pass on this set; N2 (a heading-cited section rewritten under a heading still found
is not listed) is the owner's reading of "lines changed", named in the lead's return.

The reviewer's return, word for word:

**Sandbox check (Step 0):** (a) passed: writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-h2k3` was refused (`OSError: Read-only file system`), so no file was created. (b) passed: `git hash-object -w --stdin` exited 0 (object `1ae28402a`) and `git update-index --refresh` exited 0. **`ps` check:** no ollama or llama-server process is running.

task: DAEO-h2k3, the narrow independent check of the S4/F3 revision (DEC-1178 (1), DEC-1154)
status: done, judgement pass
work_completed: probed head `dda647a49` (confirmed with `rev-parse`) against DEC-1178 (1), the ticket's S4 and F3 lines and its "Reopened 2026-11-14" paragraph; ran the visible side; planted a throwaway hidden sets root and ran the hidden S4 case against it
files_changed: none (`git status --porcelain` is empty; throwaway files only under `$TMPDIR/probe`)
evidence: commands and counts are in the record below
tests: visible folder 22 passed, 7 skipped, 9 deselected; the hidden S4 case on planted roots in four variants; the hidden-module skip checks
discoveries: N1 to N3, all rows
risks: none blocking
lessons: none
proposed_decisions: none
unresolved: N2 is the owner's reading if they want heading-cited sections on the list
recommended_next_action: the owner's operator's walled re-run (expected 7 passed, with h03 on the list)

---

reviewer_session: 4312c571-0b45-4a28-a4f6-8bad354a8f06 (read from the sandbox's task path)

**What I probed and found sound**
- **Scope:** `git diff e0381969c dda647a49` touches only the four files in `tests/acceptance/W2-61h/`. The merge's parents are `e0381969c` and `3bc8fe6d1`.
- **Trailers:** `git interpret-trailers --parse` finds one final block on each commit:
  - the designer's commit has `Rewrite-Reason: DEC-1178 (1)`, `Task: DAEO-h2k3` and `Role: independent-test-designer`;
  - the merge has `Task: DAEO-h2k3` and `Role: orchestrator`.
- **Visible run (the brief's command, through heavy_slot):** 22 passed, 7 skipped (the hidden cases), 9 deselected (the `breadth` rows). This matches the README. The exclusion left out the `local_only`, `real`, `green_here` and `time_limit` cases.
- **The planted case runs in the full run.** With `-rA`, `test_s4_f3_judges_each_source_at_its_own_commit_on_planted_data` shows PASSED. It is a single function with no parameters, so the "first row only" rule in `optin-lifted-breadth.txt` does not drop it.
- **Function names are kept.** A diff of the `def test_` names shows the hidden module unchanged and the visible module with one name added (the planted case), none renamed or lost. Only one other case's code changed: the F3 anchor case now reads each source at its own commit (`span_text_own`), which is the intended change. The two helpers removed (`source_faults` and `span_text`) are used nowhere else; grep finds only unrelated helpers of the same name in W1-38 and W2-135.
- **Hidden S4 case on a throwaway root** (`$TMPDIR/probe/root`, run with `env -u GOV_ROLE -u GOV_TICKET`). The planted sources cite real non-evaluation files: `measure.py` at `289b9314a`, the W2-61h README at `e0381969c`, the support file, and `src/gov/hooks/precompact.py` with a per-source commit at `fa9d71614^`.
  - **Moved block** (h01, lines 28–30, which moved to 51–53): passes, not listed.
  - **Changed block** (h02, lines 4–6): passes, listed as `h02.yaml entry 1`.
  - **File deleted at HEAD with a per-source commit** (h06): passes, listed.
  - **Alternatives, one moved and one changed** (h07): passes, listed.
  - **Answer missing at its own commit:** h03 (a heading that exists only at HEAD) and h05 (a path that is a file only at HEAD) are red, named `h03.yaml: source entry 1: …` and `h05.yaml: source entry 1: …`.
  - **Control** (h04): passes, not listed.
  - **Counts:** with h03 and h05 present, 1 failed; with them removed, 1 passed with the warning; under `-W error`, 1 passed with the list printed instead (shown by `-rA`); with h02, h06 and h07 also removed, 1 passed with no warning.
- **The list appears in the walled command's own output as the README says.** It is one `GoldBlockChanged` line under "warnings summary", for a passing and a failing run alike, naming file names and entry numbers only.
- **Skips:** without `GOV_EVAL_SETS_ROOT`, 7 skipped. With `GOV_ROLE=engineer` or `GOV_ROLE=research` (the path map's `measures.roles` is exactly those two), 7 skipped each.
- **Own commit, probed directly:** `span_text_own` reads the source's own commit (its text differs from HEAD's), falls back to HEAD when no commit is named, and honours a per-alternative `commit`.
- **Hand re-anchors still resolve.** `repin_gold.py --write` sets the re-pinned source's `commit` to the root's HEAD, so those sources resolve at their own commit under the new rule.
- **No leaks found.** Every message, the warning and the README name file names and entry numbers only. The planted test asserts that no `zqxw` text, no `docs/` and no `.md` appears in any message. The README's `h0x`/`h1x`/`h2x` mentions are file names. I read no hidden content and never opened `~/gov-os-eval`.

**Findings**

- **N1 (scope: in): an entry can appear twice in the list.** When two alternatives of the same entry both changed at HEAD, the list shows that entry twice (`[1, 1]` → "hNN.yaml entry 1; hNN.yaml entry 1"). It should appear once.
  Ordinary work: yes, because alternatives are part of the question form and one edit to a cited file can change both.
  Consequence: other (the repeat is cosmetic; the list still holds file names and entry numbers only and nothing fails).
  Reversed by: a reading that the list is per alternative rather than per entry.

- **N2 (scope: in): a rewritten heading-cited section is not listed.** A source cited by heading, whose heading is still found at HEAD but whose section text changed, is not put on the list. DEC-1178 (1) says "a block whose lines changed is listed". The designer narrowed the list to what the measure would count as not found, and documented this in the README's "changed rule" row.
  Ordinary work: yes, because cited sections are edited in ordinary work.
  Consequence: other (the maintenance list can miss a rewritten section; the S4 check neither fails open nor loses work, and the operator's cross-check judges whether the section still answers).
  Reversed by: the owner reading "lines changed" as "what the measure cannot re-anchor".

- **N3 (scope: in): the anchor check has no planted red case.** For q21–q24, the "anchor missing from its span at its own commit → red" path has no red case on planted data. The planted reds are both resolution faults (a path or a heading missing at the own commit). My direct probe confirmed that the anchor reader reads the source's own commit.
  Ordinary work: no, because a correct q21–q24 run passes today and this is only a gap in proof.
  Consequence: other.
  Reversed by: a planted anchor-miss case added by the test designer.

**Judgement: pass**

```verdict
{"kpis": [{"kpi": "S4", "verdict": "pass", "findings": [{"id": "N1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "N2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "F3", "verdict": "pass", "findings": [{"id": "N3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
