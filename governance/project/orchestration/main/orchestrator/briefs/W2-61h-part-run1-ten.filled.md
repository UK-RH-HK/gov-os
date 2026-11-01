You are the ticket lead for ticket `DAEO-h2k3` (`W2-61h`, "W2-61's enlarged set: 28 new memory questions with their gold sources, 24 hidden and 4 visible, by an independent session"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-61h` on branch `w2/W2-61h`. It is on memory's critical chain: W2-15a and the 48-question measure wait for it (DEC-979 item 4, DEC-957).

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve; allowed paths, KPIs, profile and the acceptance path are set; no open dependency (W2-84, which refuses the hidden half from every worktree, is closed).

## Who writes the set (DEC-996 (B))
The owner decided that evaluation sets are authored by the independent test designer (its writes gain `fixtures/evaluation/**`); the CTO changes this ticket's role from independent-auditor to independent-test-designer at claim. **Your only worker is one fresh independent test designer** (`gov launch independent-test-designer DAEO-h2k3`, sandboxed, effort high). If the launch is refused, return LAUNCH_BLOCKED with the exact text; never another form.

## Independence and the hidden half (DEC-820 (d), DEC-828 item 3, DEC-845 item 2)
- **You never read the questions or answers,** and no session that builds or tunes retrieval reads them. Your brief to the designer gives the KPIs, the spread and the form only (W2-61's visible half's form: `fixtures/evaluation/memory-retrieval/visible/q01.yaml` to `q20.yaml` show it; the designer may read those 20 and must not copy or paraphrase them).
- **The designer writes all 28 first,** then a recorded seeded draw, stratified by category, sends 4 to `visible/q21.yaml` to `q24.yaml` and 24 to `hidden/`; the seed and the draw's record (counts per category only, no text) go in its return.
- **Nothing quoted anywhere:** no question or answer in a commit message, a return, a log, a ticket note or your checkpoint. Your return gives counts only (per category, per half) and the commits.
- **The five-rule guard refuses reads of the hidden half from every worktree** (W2-84). A designer's own check of its hidden files that the guard refuses is taken, not worked round: the designer validates each file's form before it writes it (in memory), and a validation it cannot do after writing is named in its return.
- **Every gold source exists at `@@HEAD@@`** and holds its answer, cited by path and heading or line (the designer checks each source, not the hidden file).

## Verification
There is no code. The designer runs W2-61's measure's form check on the 4 visible files only (`--part visible`), never `--part hidden`; you run `select_tests.py`'s scoped set once in the close's form (DEC-968, DEC-983), which should select the evaluation set's own checks only. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head. **No review (STANDARD).** One role (DEC-995): nothing outside the ticket's paths.

**Estimate:** 28 questions with gold sources; about 3 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-61h`.

---
