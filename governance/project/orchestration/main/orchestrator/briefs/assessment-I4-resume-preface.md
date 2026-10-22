# Lens I, area 4 — a fresh session that finishes the report (resume, 2026-10-22)

You are a fresh independent auditor for lens I's area 4. The full brief follows this preface and binds you in every point; this preface only says where your predecessor stopped.

**Where your predecessor stopped.** The first session for this area ended its turn while its own background runs were still pending: in this launch form (`claude -p`), ending a turn ends the session, so those runs were never read and the report was never written. Its work is in your own folder, `/tmp/gov-os-assessment-I4/`:
- `drafts/` holds the report's parts:
  - `00-terms.md`, `01-header.md`, `02-method.md`, `02-tables.md` (the verdict table), `02-verdicts.md`, `02-21.md`;
  - `03-counts.md`, `03-findings.md`, `04-changes.md`, `05-packages.md`;
  - `REPORT-draft.md`, an older assembly.
- `logs/`, `runs/`, `notes/` and `plans/` hold its evidence.
- Its last status: every phase-1 case green alone, three times each:
  - W1-07 `[doctor]` and `[hard-block]`, on the head and on the 10,286-file tree;
  - the help case;
  - the three W1-38 probe cases;
  - W1-09's two race cases.
  - W1-33's research case passed 3 of 3 once the sandbox HOME linked the real tools read-only. Five area suites look tools up under HOME; the header says so.
- The parallel runs, three times each, had not reported:
  - W1-07 on the head;
  - W1-07 on the 10,286-file tree;
  - W1-09;
  - W1-38 with the probe sampler.
  The planted faults were next.

**What you do:**
1. Read the drafts and the notes. Do not redo work they record with evidence.
2. Run the outstanding parallel runs and the planted faults **in the foreground**: each Bash call at most 10 minutes (`timeout` 600000), split into pieces if needed.
   - **Never end your turn while a run of yours is pending:** you would not be woken, and the session would end.
   - If a run would take longer than your remaining budget, record it as a limit instead.
3. Before every run, honour the close lock exactly as the brief says: while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md`'s sibling file `CLOSE-RUNNING` exists, run nothing heavy and wait.
4. Assemble the report at the path the brief names, in its structure. Read it once more from the file, then return as the brief says.
5. At the end, list your folder's size. The orchestrator removes `/tmp/gov-os-assessment-I4/`; you do not.

---

