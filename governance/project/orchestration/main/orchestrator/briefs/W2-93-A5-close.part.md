This is W2-93 (DAEO-6y0x), STANDARD, class C2, run "close": W2-81's held-out half. The owner's DEC-1167 (3): its walled writer delivered on 2026-11-12 (run `20261112T185824Z-adoption-proving-ground-r1`, 60 questions in the evaluation sets' root, outside git); close it in parallel with W2-94. The ticket's Verify lines were fitted to the walled route by the CTO (S3, S5) and its paths gained `tests/acceptance/W2-93/**` and its probe folder.

**What is missing, and what you deliver** (an independent test designer, C2; you never read the hidden half's contents):
1. `fixtures/evaluation/adoption-proving-ground/validate_hidden.py`, as S5 states. It reads the hidden half under `--sets-root <root>` (S6) and checks:
   - every must-not-cite file names a file of the repository the builder builds, checked on a built copy;
   - at least one hidden variant per kind the visible generator does not produce, per repository;
   - anything it cannot read refuses (fail closed).

   It prints counts and ids only, never a question or an answer.
2. `--sets-root <root>` on `tests/acceptance/W2-81/w2_81_run.py`, with its case in `test_w2_81_runner.py` (DEC-1144 (6)). The runner finds the hidden half under the root given, never a named hidden path.
3. `tests/acceptance/W2-93/`: form-only cases on planted stand-in sets (counts, fields, sources exist). They cover each S line's Verify and both F lines: a planted unreadable file, a planted must-not-cite file absent from the built copy, and a planted kind with no variant each refuse (non-zero exit); and a read, a grep and a `git log` from a measured session's role cannot reach a planted stand-in hidden file.
4. `gov accept W2-93` on stand-ins, and the scoped run once (DEC-968). A narrow independent check of the change: a fresh read-only auditor carrying JUDGEMENT.md word for word, with the verdict block; the probe record with the schema's `implementer_session`.
5. Return DONE with the head to land.

The CTO runs `validate_hidden.py --sets-root` on the real delivery himself, records the counts, then lands and closes.

**Walls (hard):** never open, list, grep or print anything under the evaluation sets' root or any hidden folder; your cases use planted stand-ins under your sandbox's `$TMPDIR` only. Never quote a question or an answer anywhere.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits by pid only. A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). No new ticket. There is no token cap.
