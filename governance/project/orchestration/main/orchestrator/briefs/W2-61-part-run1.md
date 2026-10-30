You are the ticket lead for ticket `DAEO-iw1f` (`W2-61`, "The standing 20-question measure, split under Policy 2 (d)"), profile STANDARD, keystone 4, working only in the worktree `/home/usain/gov-os-worktrees/W2-61` on branch `w2/W2-61`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-iw1f.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-61 "); W2-61h's ticket file (`.tickets/DAEO-h2k3.md`) and card ("#### W2-61h"), for the hidden half's form and who writes it;
- DEC-828 (items 3 and 4), DEC-833, DEC-860, DEC-820 (d), DEC-845, DEC-873, DEC-877 and DEC-941 (item 1.2);
- lens B's report, `docs/assessment/2026-10/B-memory-retrieval.md`: §1 "What I ran, and where" and §2.1 to §2.5 (the 20 questions, Table 2 with its gold, the totals, determinism);
- the path map's `evaluation_sets` block (the last lines of `governance/project/path-map.yaml`) and `gov retrieve`'s options (`src/gov/retrieve/command.py`: `--batch-size`, `--bundle-budget`, `--continue`).

## Why you start now

- **Memory is the critical path** to EXAMIN's copy. The owner's re-plan (DEC-941 item 1.2): "W2-61's 20-question baseline on today's pinned stores: its lead starts as soon as the ticket is filed, beside everything else."
- **The last figure is lens B's,** on `fecb870c`: the governing source in the first five items for 13 of 20 questions (65 % hit@5, against CAP-10's floor of 85) and in the bundle for 17 of 20. The stacked full-evidence share (the owner's 99 % target, DEC-833) has never been measured.
- **The re-plan's date moves on your baseline** (REPLAN-W2 §3: EXAMIN's copy targeted for 2026-11-18, later if memory proves further from 85 % than lens B's 65 %).
- **Your script is the standing measure:** it is re-run after each ticket of block B's chain (W2-03, W2-55, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a), beside your baseline.

## The decisions for this run

- **Nobody in this ticket reads the hidden half (DEC-820 (d), DEC-873).** The path map's `evaluation_sets.memory-retrieval` measures the roles engineer and research, so your engineer is measured.
  - Neither you nor any worker of yours ever reads the contents of `fixtures/evaluation/memory-retrieval/hidden/**`: not in this worktree, not in the main tree, not in any other worktree. File names may be seen.
  - W2-61h's independent auditor will write those files in `/home/usain/gov-os-worktrees/W2-61h/`; it is held until the guard's (d) refusal covers every tree. Today that refusal is judged from a session's own project root only (checked by the orchestrator on 2026-10-29), so a copy in another tree is held by this rule alone.
  - Put this rule, word for word, into every worker brief.
- **One form for both halves** (W2-61h's ticket): one YAML file per question, with `question`, `gold_answer` and `sources`.
  - Each `sources` entry is one piece of needed evidence: a path, plus a heading or a line span at a stated commit. Where two places hold the same evidence, the entry is a list of alternatives, any one of which counts (lens B's gold for Q02: "DEC-782, or `semantic.py` 15–25").
  - The script also accepts these optional fields: `id`, `category`, `commit`, and `ticket` (the ticket the asker holds, as lens B's Q06, Q07, Q09 and Q14 used).
  - W2-61h writes before your script merges, so the script reads this form. Anything more you need is a package. Never ask anything of the hidden files themselves.
- **The visible half** is lens B's 20 questions. The engineer writes them under `fixtures/evaluation/memory-retrieval/visible/`, in the same form, from Table 2: each question, its command's options (`--ticket`, `--id`, `--radius`) and its "Expected (gold)" column.
  - Each source is checked at this worktree's head. Gold lines drift as files grow, so give the heading as well as the lines at that commit.
  - Lens B's report is the visible half's origin, never a gold source.
  - `fixtures/**` is not indexed (the path map's `fixtures` namespace), so the questions do not answer themselves.
- **The script (`src/gov/retrieval/measure.py`), in behaviour:**
  - **Per question and in total, it reports two things:**
    - whether a gold source is among the first five items (hit@5, counted as lens B counted it, so that 13 of 20 compares);
    - whether the stacked context holds every needed piece of evidence across batches (the full-evidence share).
  - **Both figures, always together (DEC-833 item 3):** every output line and record line that gives one gives the other, against 85 and against 99 %.
  - **Stacked, never giant (DEC-860):** each question goes through `gov retrieve` in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within a stated budget. The script measures the stacked answer, never one giant query or context.
  - **Only the governing source counts as a hit:** an item from lens B's report, from `fixtures/evaluation/**`, or from a test that only quotes the answer is not a hit (failure KPI 4).
  - **Repeatability:** the same run twice on an unchanged index, and once after a rebuild, compared per question.
  - **The retrieval it measures is named, never implied:** every output states which `gov` answered (its version, and the `gov.__file__` of the retrieving process).
  - **It prints scores, never a hidden question or answer (failure KPI 2):** for a set's hidden part it prints, logs and writes only ids, counts, ranks and pass or fail.
  - **It measures any declared set by name** (the path map's `evaluation_sets`), so the same script measures EXAMIN's set and EXP-003's split (KPI line 6). Writing those sets is other sessions' work (before W2-27; W2-15a and W2-15b), not this run's. Name KPI line 6 that way in your return.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`), in `tests/acceptance/W2-61/`:
  - every KPI line's success and failure, plus the key edge cases (STANDARD);
  - **a planted evaluation set built at test time,** in a temporary repository built from scratch, **never the real hidden half.** It has planted documents, planted gold and a planted hidden part whose answers carry a recognisable string. Checks:
    - the planted hidden answer appears in no stdout, stderr, file or record;
    - neither figure is ever given without the other;
    - a hit from the evaluation files, or from a report that only quotes the answer, is not counted;
    - batches are stacked rather than one giant query;
  - the measured role's refusal of the planted hidden part (W2-58's guard), by the routes an honest agent takes.
- **The engineer** (fresh, launched sandboxed where its suites allow, `--effort high`) works only in the allowed paths: `src/gov/retrieval/measure.py`, `tests/unit/retrieval/test_measure*`, `fixtures/evaluation/memory-retrieval/visible/**` and, in a later batch, `docs/research/W2-61-baseline.md`. Its brief carries the hidden-half rule above.
- **The baseline, today (DEC-941; KPI line 7), run in your own session.** Inside the sandbox `gov` embeds on the CPU, so a sandboxed worker's figures prove nothing about the shared GPU.
  1. **A clone by exact path, outside every tree:** `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /home/usain/gov-os-runs/W2-61/repo`, then `git -C /home/usain/gov-os-runs/W2-61/repo checkout --detach @@HEAD@@`. Nothing goes under `.gov-runtime/`, and nothing is written in the main tree.
  2. **Its stores are built by the pinned gov** (a bare `gov`, with no `PYTHONPATH`; DEC-877), in the clone: `flock /tmp/gov-os-rebuild.lock gov rebuild --json`. Never `--no-embeddings`. Run it only after the load and disk gates, and never while `CLOSE-RUNNING` or `NIGHTLY-RUNNING` exists.
  3. **This worktree's script, the visible half only, run against the clone.** The retrieval it measures is the pinned gov's: no `PYTHONPATH` and no `GOV_TICKET` reach the retrieving process (as in lens B §1, "Which code"). Show that process's `gov.__file__` inside the pin's install. Run it twice on the unchanged index; then rebuild under the lock and run it once more.
  4. **Every output goes under `/home/usain/gov-os-runs/W2-61/runs/`.** Then a fresh engineer batch writes `docs/research/W2-61-baseline.md` from those outputs. The record holds:
     - the date and the clone's commit;
     - the pinned gov's version and commit (`gov --version`; if it says "commit unknown", the pin's folder `~/.local/share/gov-os/pin-<commit>/` names it);
     - the stores' fingerprint as the rebuild records it, or the sha256 of each store file, so named;
     - both figures together, against 85 and against 99 %;
     - per question (visible half only): hit@5, in the bundle, full evidence, the repeat run and the run after the rebuild;
     - lens B's figures beside yours;
     - an empty, labelled place for the hidden half's scores. The orchestrator fills it (scores only) once W2-61h's questions exist (W2-61h's ticket).
  5. **Leave the clone and its stores in place** for the orchestrator's hidden-half scoring. Give the clone's path, its `du -sh` and its `du -s --inodes` in your return; they count in your budget.
  - **The baseline runs before your full verification,** so that it lands today. If it cannot run today, say why in your return.
- **The path map is not yours.** Its `visible` entry names lens B's report, and its comment says "W2-61 narrows `measures` to tickets". `governance/project/path-map.yaml` is owner-only (DEC-757, DEC-766). If your script needs a change there, return a package naming the exact lines.
- **Running beside you:**
  - W2-61h's independent auditor holds `fixtures/evaluation/memory-retrieval/hidden/**`: never read it (above).
  - W2-03 (`DAEO-ym8a`, merge-back) holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` and their unit tests. Your script reads the stores only through `gov retrieve`.
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls, `src/gov/util/gitenv.py`, the `lefthook.yml` files and `tests/unit/gitenv/**`. If your script runs git, leave how its git environment is built as it stands; the later merge takes the conflict.
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`. W2-60a and W2-56 hold `src/gov/launch/**`. W2-77 holds `src/gov/close/nightly.py`.
  
  Do not touch any of these. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite, no full run and no rebuild. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00. Wait for the nightly to end.
  - **Every rebuild** (your worktree's and the clone's) runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **No review (STANDARD).**

## This run's order

1. Tests first (the test designer), then **check red yourself.**
2. The engineer: the script, the visible half, its builder tests.
3. **The baseline** in your own session, on the clone.
4. A fresh engineer batch: `docs/research/W2-61-baseline.md`.
5. Rebuild and verify in full.
6. **Return** DONE or PACKAGES. DONE means the branch is ready to merge; after the merge, the orchestrator scores the hidden half beside your baseline.

**Estimate:** about 180 lines, plus the 20 visible files and the record; about a day with the baseline and the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the engineer's work into batches that fit.

---
