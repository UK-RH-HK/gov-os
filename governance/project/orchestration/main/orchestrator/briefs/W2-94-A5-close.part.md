This is W2-94 (DAEO-g87r), STANDARD, class C2, run "close": EXAMIN's question set. The owner's DEC-1167 (3): its walled writer delivered on 2026-11-12 (run `20261112T185806Z-examin-r1`, 20 questions; the visible half released and confirmed, DEC-1152); close it in parallel with W2-93. The CTO fitted the ticket's S3 and S4 Verify lines to the walled route. Its paths gained `tests/acceptance/W2-94/**`, `fixtures/evaluation/examin/check_gold.py` and its probe folder. W2-61's close record now names KPI 6 as moved here.

**What is missing, and what you deliver** (an independent test designer, C2; you never read the hidden half's contents):
1. `fixtures/evaluation/examin/check_gold.py` (S4). Under `--sets-root <root>` and `--copy <the launch clone's path>`, it checks for each question that its gold source exists at the copy's recorded commit (`COPY-HEAD.txt`) and holds the answer. It prints only counts and ids ("n of n hold"), and reports a failing question by id. It refuses when it cannot read (fail closed).
2. `tests/acceptance/W2-94/`: form-only cases on planted stand-in sets and a planted stand-in copy. They cover:
   - S1: between 10 and 20 questions, each with its fields, and a set outside 10 to 20 refused;
   - S4 and F3: a planted source that is absent or does not hold its answer is reported by id;
   - F1: a read, a grep and a `git log` from a measured session's role cannot reach a planted stand-in hidden file;
   - S5: a grep of W2-61's close record finds KPI 6 named as moved to W2-94.
3. `gov accept W2-94` on stand-ins, and the scoped run once (DEC-968). A narrow independent check of the change: a fresh read-only auditor carrying JUDGEMENT.md word for word, with the verdict block; the probe record with the schema's `implementer_session`.
4. Return DONE with the head to land.

The CTO then:
- runs `check_gold.py --sets-root --copy` on the real delivery and records the counts;
- has the owner's operator record S2's `git status` of the workbench copy and EXAMIN's real repository;
- lands, and closes.

**Walls (hard):** never open, list, grep or print anything under the evaluation sets' root or any hidden folder, the workbench, the owner's EXAMIN copy or EXAMIN's real repository. Your cases use planted stand-ins under your sandbox's `$TMPDIR` only. Never quote a question or an answer anywhere.

Workers launched by `gov launch` write only their sandbox's own `$TMPDIR`. Every pytest through bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh with a TMPDIR outside the repository and outside ~/gov-os-runs (a launched worker: its sandbox's `$TMPDIR`), PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider -o tmp_path_retention_policy=failed. Waits by pid only. A resource gate's refusal is a wait (DEC-1146). A session refused twice for the same action stops and says so, and never works around a refusal by another tool or form (DEC-1142 (9)). No new ticket. There is no token cap.
