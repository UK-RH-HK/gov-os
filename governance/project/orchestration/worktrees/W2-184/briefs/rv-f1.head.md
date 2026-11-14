# Brief: independent auditor, W2-184 (DAEO-6f0s): the narrow independent check of the changes decided after review round 2 (DEC-1154, DEC-1177 (1))

You are a fresh, read-only independent auditor (Opus, effort high). This is **not** a third review round: the FULL
ticket's two rounds are done (DEC-1010); round 2 failed on F1 and the owner decided it (DEC-1177: P-W2-184-1 (a),
with (c) as the stop-gap). DEC-1154: a change decided after a ticket's review gets a narrow independent check of that
change only, and the ticket lands on it. Check **only** the two decided changes below, at the head named, against the
decision, the interface's amended sections (at the end, word for word) and the judgement rules (below, word for word).
Write no file of any repository; run probes only in your session's own `$TMPDIR` (copies, fixtures). Re-run no whole
suite. Use your audit skill.

## What to check
- Tree (read-only): /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. **Head to check: HEADPROBE.**
- **Change 1, the owner's DEC-1177 (1) (round 2's F1):** the probe records are also read under each worktree root
  that the ticket's launch records name (interface 5.1a, with the lead's two settled points P-td5-1 and P-td5-2). The
  engineer's commits 94b48c130 and 42d0867d3 (`git show` each; `src/gov/launch/launcher.py`,
  `tests/unit/launch/test_w2_184_launch.py`, `docs/changes/W2-184-CIT-E.md`); the independent test designer's cases
  `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py` and the rewritten S4 case in
  `tests/acceptance/W2-184/test_w2_184_s4_reviews.py` (a4ad2e380, merged at 7d275b97f).
- **Change 2, the CTO's P-W2-184-2 (a):** `gov launch` carries `--reason`, `--trial` and `--owner-named` before `--`
  (interface 7.2a). ENGCOMMITS; the test designer's cases `tests/acceptance/W2-184/test_w2_184_cli_options.py`
  (3e3d275a0, merged at 0a4ce21fd).
- Round 2's record: `docs/probes/DAEO-6f0s/PR-DAEO-6f0s.md` (its F1, the probe p2 and the real-tree evidence);
  DEC-1177, DEC-1154, DEC-1010, DEC-1120 (3) in /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md
  (read each by id); the ticket /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (its last two
  paragraphs).
- Evidence the lead has: the full verification run at 42d0867d3 GREEN (7,992 tests, 0 failed), and at HEADPROBE
  VERIFYLINE; `gov accept W2-184` ACCEPTCOUNT.

## What to probe (at least)
- **Change 1:** does a test designer launched from the ticket's tests worktree now get the promotion the ticket
  earned (round 2's p2, re-run on this head: a fixture repository with two git worktrees, the fail-open record on the
  ticket branch only)? A deleted or non-folder root named by a record: skipped, nothing refused for it? No probe
  record anywhere: as before? Does any path that refused before now let a launch through (a probe record that is not
  YAML or whose verdict block is not JSON, under another root; a launch record that is not JSON)? Counted once per
  root-relative path (no false "two failed reviews")? Another ticket's records do not widen the search? The review
  count (6.1) unchanged by the shared read (resumes, `--resume` of a record, other tickets, other roles)? The cost of
  the new read on every launch in a project with `criticality.yaml` (P-td5-1: one unreadable record stops every
  launch): judge it by the rules.
- **Change 2:** each option through the CLI gives the keyword case's result; forms checked; an option after `--`
  stays a CLI argument; the usage line; `--plan` and lead launches unchanged.
- Do the new cases fail when the code does not do what they claim (a mutant or two in a `git archive` copy is enough)?
- Anything outside the two changes is out of scope: do not re-open rounds 1 and 2's settled findings or rows.
- Do not open, list or read anything under the evaluation sets' fixtures or any hidden folder.

# Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

JUDGEMENTTEXT

# Your record (your last message; the lead commits it as docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md)
Return, as your last message, the record's body in Markdown (the lead adds the front matter):
1. A title line `# Narrow check of DAEO-6f0s (W2-184) after review round 2: judgement pass|fail`, then the head you
   checked (full hash), your session's role, model and effort, and what you ran (commands, fixtures in `$TMPDIR`).
2. `## Findings`: each finding with an id (F1, F2, ...), the change (1 or 2) and KPI line, what you saw (file:line,
   the probe and its output), and its lines: `Ordinary work: yes|no, because …`, `Consequence: fails open|loses
   work|other`, `Scope: in|out`.
3. `## Per KPI line`: S1, S2, S3, S4, S5, F1: pass or fail as far as the two changes bear on it, one paragraph each.
4. The fenced verdict block, exactly in this form (JSON), one entry per KPI line:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
5. A last line: `judgement: pass` or `judgement: fail` (fail only when a finding is in scope, ordinary work yes, and
   fails open or loses work).
Then, after the record, the twelve fields, each a labelled line: task: / status: / work_completed: / files_changed: /
evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

