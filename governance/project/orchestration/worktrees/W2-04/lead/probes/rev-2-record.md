Review 2 of W2-04 (`gov context` bounded and reproducible) passes on all eight KPI lines, S1–S7 and F1. All three repairs from review 1 hold, and the later merges by W2-13, W2-150, D-4 and D-10 did not weaken S3, S4, S5 or S7. Nothing blocks. Five findings land as rows: four are behaviour that agents don't reach in ordinary work or that never fails open, and one is a test-coverage gap from D-4's cut. The ticket can close at the lift as planned, with no third round and nothing for the owner.

One thing to know about my method: the Write tool was refused twice when I tried to put a probe script in my TMPDIR, so I stopped using it. I didn't create the file another way; I ran the probes as inline `python3 -c` commands instead.

```
task: Review 2 of 2 (the last) of W2-04 (DAEO-u4oz): a fresh, read-only probe of head 4c55f14179be against S1–S7 and F1
status: DONE — every KPI line passes; no finding is in scope, reachable in ordinary work and failing open or losing work
work_completed: read the ticket, src/gov/context/{__init__,command,context_check}.py, src/gov/retrieval/supplementary.py, gov.util.role_paths.caller/Filter, the session-start hook's call, the emptied-file test, the support module, the README map, the opt-in lists and the diffs 70965cf61..4c55f14179be; built 5 throwaway projects under TMPDIR and ran 4 probe sets (≈190 gov/context calls)
files_changed: none
evidence: Step 0: (a) the write to /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-u4oz failed with "OSError: [Errno 30] Read-only file system"; (b) `echo sandbox-trial | git hash-object -w --stdin` gave blob 1ae28402a109 and `git update-index --refresh` exited 0 (an earlier variant also wrote the empty blob e69de29bb2d1; both are loose objects in .git, not tree changes); GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-u4oz. Head at start 4c55f14179be, at end 4c55f14179be; `status --porcelain` empty at end. gov.__file__ = /home/usain/gov-os-worktrees/W2-04/src/gov/__init__.py. Session id: not known. TMPDIR probe folder: 26M and 2,055 inodes at its peak, then removed (nothing left that I cannot remove; the h/ HOME was never created). Read refusals met: 0. Write-tool refusals: 2 (probe script files under TMPDIR), so I stopped using Write and did not make the file another way.
tests: none of the suites run; probes only (counts under Method)
discoveries: (1) A mandatory input that has a status of DEPRECATED or WITHDRAWN satisfies a mandatory source. The supplementary block treats those two as no longer standing (DEC-568, DEC-423); the context counts only SUPERSEDED, RETIRED and REJECTED. F1 names only RETIRED and REJECTED, so this is not a finding here. (2) D-4's cut moved F1's no-longer-stands case and S4's stale-store check into the breadth opt-in, so the default full run no longer exercises them (row R2-F5). (3) The one skip in success-4 is the live-embedder case (no embedder by design, DEC-1064); no failure-1 line hides anything: the F1 case ran inside success-2's 8.
risks: the emptied-file block tests only for an empty or whitespace-only file; a BOM-only, NUL-filled or remnant file still shows as read (rows R2-F1, R2-F2)
lessons: Api.env() in w2_04_support passes no GOV_ROLE or GOV_TICKET, so W2-04's acceptance suite never exercises W2-13's role filter; probe it by setting those variables yourself.
proposed_decisions: none
unresolved: whether the owner wants F1's RETIRED/REJECTED case and the stale-store case back in the default full run (D-4's matter, row R2-F5)
recommended_next_action: compute READY from the verdict block (pass) and close W2-04 at the lift as D9-FATES plans; file rows R2-F1 to R2-F5 for Wave 3
```

---

task: DAEO-u4oz
decisions: DEC-801, DEC-808, DEC-1010, DEC-1014, DEC-1025, DEC-1065, DEC-568, DEC-860
probed_commit: 4c55f14179be (12 digits here, row W2-L423's rule; the full id is in the committed record)

**Scope.** `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`, `tests/acceptance/W2-04/**`, the ticket file, and what the session-start hook's caller sees of S2 and S5. Out: review 1's F4, F5 and F6.

**Method.** All projects were throwaway git repositories under TMPDIR, built with `w2_04_support` (imported read-only), with HEAD empty and this tree's own `src/`.
- **Probe 1 (F1's neighbours).** One project: a charter, CAP-15, ADR-0099 (a decision file of its own) and a dependency ticket. Each of the three inputs was rewritten in the working tree, after a store built from HEAD, as:
  - empty, whitespace, NBSP only, BOM only, BOM plus a newline, 64 NUL bytes;
  - a comment only, `---` only, front matter only, and a legitimate edit (one line added).

  Each was run under `--json`, `--dry-run`, `--brief`, `--brief --dry-run` and `context(brief=True)` as the hook calls it, then the file was restored. 26 forms by kind, about 110 calls.
- **Probe 2 (F2).** The 48-page ledger, at budgets giving zero room, an exact fit after k = 3, 9, 10, 11 and 20 items, a cut, and room 5 (8 builds).
- **Probe 3 (F3).** The context check on a project where every ticket refuses, and on one with one ticket refused and one fitting.
- **Probe 4 (S3/S4).** Two clones of one commit, each with its own store. 5 role/ticket settings × semantic stand-in off and on × 2 clones = 20 builds, plus one `--role engineer` build.

**Probed and found sound.**
1. **F1 repaired.** An empty, whitespace-only or NBSP-only capability file, decision file or `deps` ticket is BLOCKED (exit 1) in all four CLI modes and through `context(brief=True)`. The error names the id and the file. A legitimately edited file is not blocked and is read with its new sha256. A dependency ticket cut down to its front matter is read correctly, because only its front matter counts (CAP-15.b). The hook gets the BLOCKED error and shows nothing as read; that it drops the error silently is F4, out.
2. **F2 repaired.**
   - Zero room: `further_batch` holds ranked items 1–10, no batch taken.
   - Exact fit after 3 or 9 items: it holds the rest of that batch.
   - Exact fit after 10 or 20 items: it holds the next 10.
   - Room 5: it holds 5.
   - Every time it starts at the first ranked item not stacked, is at most one batch long, and the same items appear in `dropped` as `budget exceeded`. Tokens never exceed the budget.
3. **F3 repaired.** All refused: `REFUSED: TK-BIG …` then `unmeasured: no packet was built …`, exit 1. Mixed: `green (1 packet(s) built twice alike, 1 refused …)` with its `REFUSED:` line, exit 0.
4. **S3 and S4 kept.** Across two clones of one commit the packet hash is identical for each role and ticket setting, with the semantic stand-in on or off. `GOV_ROLE=engineer` with or without `GOV_TICKET` gives the same hash, and `--role engineer` without `GOV_ROLE` gives it too. W2-126's two caches are semantic only; the supplementary block uses only the lexical index, so they cannot reach the packet. In `_read_record`, the code that hashes a decision is unchanged since 70965cf61. W2-13 changed only how role and ticket are passed through; D-10 made the damaged-index wording broader but added an assertion that it is not the generic message.
5. **S1, S2, S6, F1 as built.**
   - S1: the ticket's text counts as mandatory and is never shortened, and a second ceiling check after the supplementary block refuses rather than going over.
   - S2: refusal is `CONTEXT_OVER_CEILING` or BLOCKED with exit 1.
   - S6: the query is the title plus the KPI lines.
   - F1: SUPERSEDED, RETIRED and REJECTED each block with their status (code lines 276–284); the lead's breadth run passed DAEO-03pw's shape.

**Findings** (all rows)

- **R2-F1 (S5).** A mandatory file left holding only a BOM, or only NUL bytes, is shown as read in every mode and through the hook: 1 or 16 tokens, the hash of what is left, and listed as "(capability, ACCEPTED)". It should be BLOCKED or `"read": false`, like an empty file.
  - scope: in
  - Ordinary work: no, because agents' write tools and a truncating write leave an empty file, which blocks; a BOM-only file needs an editor that writes a BOM into an emptied file, and NUL fill needs a machine crash mid-write.
  - Consequence: fails open
  - Reversed by: evidence that a tool in agents' normal path (Write/Edit, gov, tk, git) leaves such a file.
- **R2-F2 (S5).** A mandatory file cut down to a remnant (only a comment, only `---`, or only its front matter) is shown as read with the remnant's hash, although it no longer holds the record. The context cannot tell this from an edit without comparing the file with what the store lists.
  - scope: in
  - Ordinary work: no, because the write tools write a file whole; a remnant of this shape needs an unusual interrupted write.
  - Consequence: other (the packet truthfully shows what it read, and the hash differs from HEAD's)
  - Reversed by: an ordinary-work path that produces such remnants.
- **R2-F3 (S4).** For one ticket and one role (engineer), building the context in a session whose `GOV_TICKET` names another ticket gives a different packet hash. That ticket's tests are also withheld, and the `role_filter` line names both tickets. It is the same across clones.
  - scope: in
  - Ordinary work: yes, because an engineer's session can build another ticket's context.
  - Consequence: other (the filter only withholds more; it never fails open)
  - Reversed by: a ruling that S4's "one ticket's context" includes the caller's session ticket.
- **R2-F4 (S3, scope out).** Seen in the code, not run: when the role filter cannot read its paths, the error is caught and reported as one `dropped` entry with an empty block. That fails closed and is correct; I note only that the packet is still `ok: true`.
  - scope: out
  - Ordinary work: yes, because the path map can be unreadable mid-edit.
  - Consequence: other
  - Reversed by: none needed.
- **R2-F5 (F1/S4, D-4's cut).** In the default full run, F1's no-longer-stands case and S4's stale-store check run only with `--optin=breadth`.
  - scope: out
  - Ordinary work: yes, because the default run leaves out breadth.
  - Consequence: other (coverage only)
  - Reversed by: the default run including them.

**Classification:** 0 yes/fails open or loses work; 3 yes/other (R2-F3, R2-F4, R2-F5); 2 rows marked no (R2-F1, R2-F2).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R2-F4", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": [{"id": "R2-F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S5", "verdict": "pass", "findings": [{"id": "R2-F1", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R2-F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "S7", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "R2-F5", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```