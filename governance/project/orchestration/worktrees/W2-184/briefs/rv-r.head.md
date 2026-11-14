# Brief: independent auditor, W2-184 (DAEO-6f0s): the narrow independent check of R1-R3 (DEC-1180 (4), DEC-1154)

You are a fresh, read-only independent auditor (Opus, effort high). This is **not** a review round: the FULL ticket's
two rounds are done (DEC-1010), and the narrow check after round 2 passed with three findings F1-F3
(`docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`; read it). The CTO reopened the ticket under the owner's standing rule
DEC-1180 (4) ("a defect spotted is fixed in the same flow") to fix F1-F3 as KPI lines R1-R3. DEC-1154: a change made
after a ticket's review gets a narrow independent check of that change only, and the ticket lands on it. Check **only**
this change (since the merged base BASEPROBE), at the head named, against R1-R3, the interface's section 10 (at the
end, word for word), the rule **"nothing refused before becomes allowed"**, and the judgement rules (below, word for
word). Write no file of any repository; run probes only in your session's own `$TMPDIR` (`git archive` copies,
fixtures). Re-run no whole suite. Use your audit skill.

## What to check
- Tree (read-only): /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. **Head to check: HEADPROBE.** The change:
  `git diff BASEPROBE HEADPROBE` (BASEPROBE is the merge of w2/integrate before R1-R3).
- **The test designer's cases** (19324ca4b, merged at bf7b93bcf): `tests/unit/launch/test_w2_184_r_fixes.py` (new,
  `test_r1_*`, `test_r2_*`, `test_r3_*`) and two cases of `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py`
  revised to R3 (`Rewrite-Reason: DEC-1180 (4), rv-f1 F3`).
- **The engineer's change:** ENGCOMMITS.
- The ticket /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (KPI lines R1, R2, R3 and its last
  paragraph); DEC-1180, DEC-1154, DEC-1010, DEC-1120 (3) in
  /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md (read each by id).
- Evidence the lead has: VERIFYLINE; `gov accept W2-184` ACCEPTCOUNT; the unit file `test_w2_184_r_fixes.py`
  UNITCOUNT (`gov accept` collects only `tests/acceptance/W2-184/`, so R1 and R2's cases are run directly, as the KPI
  lines' Verify says).

## What to probe (at least)
- **R1:** a lead launch (`orchestrator`, `lead`) with each of `--reason`, `--trial`, `--owner-named`, alone and
  together, empty values too: exit 2, the message, nothing started, no record, the gate not consulted, no
  plan-override line. The same words after `--` for a lead: as before. A lead launch without them, and worker launches
  with them: unchanged. The direct `launcher.launch` call with a lead role and an option: refused.
- **R2:** `record.write`: kill or fail at each step (create, write, fsync, link, temp removal): never an empty or
  partial `<session_id>.json`; a leftover temp file is never read as a record nor refuses a launch nor blocks a later
  write; no overwrite of an existing final name; two writers: one whole record, the other refused as "already there".
  Any reader of the record folder (`record.read` for `--resume`, `_launch_records`, anything else that lists it) that
  could take the temp file as a record? A file system where hard links fail (if the code falls back to something):
  is that fallback still non-overwriting?
- **R3:** differing copies of one probe-record path under several roots: a fail-open finding in any copy promotes;
  one path is one review (no false "two failed reviews" from two copies); identical copies once; a copy that refuses
  (YAML, verdict block) still refuses; the record named is the root-relative path.
- **Nothing refused before becomes allowed:** compare BASEPROBE and HEADPROBE for every refusal the change touches.
- Do the new cases fail when the code does not do what they claim (a mutant or two in a `git archive` copy is enough)?
- Anything outside R1-R3 is out of scope: do not re-open rounds 1 and 2, or the earlier narrow check's settled points.
- Do not open, list or read anything under the evaluation sets' fixtures or any hidden folder.

# Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

JUDGEMENTTEXT

# Your record (your last message; the lead commits it as docs/probes/DAEO-6f0s/PR-DAEO-6f0s-r.md)
Return, as your last message, the record's body in Markdown (the lead adds the front matter):
1. A title line `# Narrow check of DAEO-6f0s (W2-184) R1-R3: judgement pass|fail`, then the head you checked (full
   hash), your session's role, model and effort, and what you ran (commands, fixtures in `$TMPDIR`).
2. `## Findings`: each finding with an id (F1, F2, ...), the KPI line (R1, R2, R3), what you saw (file:line, the probe
   and its output), and its lines: `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
   `Scope: in|out`.
3. `## Per KPI line`: R1, R2, R3: pass or fail, one paragraph each.
4. The fenced verdict block, exactly in this form (JSON), one entry per KPI line:
```verdict
{"kpis": [{"kpi": "R1", "verdict": "pass", "findings": []}, {"kpi": "R3", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
5. A last line: `judgement: pass` or `judgement: fail` (fail only when a finding is in scope, ordinary work yes, and
   fails open or loses work).
Then, after the record, the twelve fields, each a labelled line: task: / status: / work_completed: / files_changed: /
evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments and section 10, R1-R3)

