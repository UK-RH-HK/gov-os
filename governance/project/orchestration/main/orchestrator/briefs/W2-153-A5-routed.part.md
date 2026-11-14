This is a short run of W2-153 (DAEO-8s85), STANDARD, class C2: its last open line, routed from W2-33 (DEC-1156 (3)). S1 to S5 are met and merged. Everything the routed line waits on is on w2/integrate now:
- W2-33 is closed: its kernel role files carry `Launch default`, `Launch by criticality` and `Skills` lines.
- The copies ACTs are applied: COPIES-6 36d1a151b, COPIES-8 bb9dfca7a.

**The order:**
1. Merge `w2/integrate` into the branch (one command, `--no-ff`, `Task: DAEO-8s85`, `Role: orchestrator`).
2. A fresh independent test designer (C2) writes the routed line's cases in W2-153's acceptance folder:
   - each generated role copy (`.claude/agents/*.md` and `.rulesync/subagents/*.md`) holds the three lines byte-equal to its kernel role file;
   - a planted hand edit in one copy, in a stand-in, is named as drifted by the generation check.

   Map them in the README.
3. `gov accept W2-153`, and the scoped run once (DEC-968). A narrow independent check of the new cases: a fresh read-only auditor carrying JUDGEMENT.md word for word, with the verdict block. Add it to the probe record (schema's `implementer_session`; validated against probe.schema.json).
4. Return DONE with the head to land.

If a copy does not hold the lines byte-equal, name the file and the line: a copies ACT is the CTO's.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits by pid only. A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). Never open the evaluation sets' root or any hidden folder. No new ticket. There is no token cap.
