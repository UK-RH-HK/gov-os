# D-10's red-fix list: the review of gov accept's opt-in groups (S-D10a) and its map reader (S-D10b) (W2-96, DAEO-ouet)

You are a fresh, read-only independent reviewer of tests and code for two new KPI lines (STANDARD; one review).
READY is computed by `verdict.py` from your block.

## The KPI lines (in `.tickets/DAEO-ouet.md`, from the CTO's delegated decisions, DEC-1112 (3))
- **S-D10a:** `gov accept` runs the opt-in groups its own map's cases need, only for that ticket's cases. A line
  whose mapped cases an opt-in list leaves out of a default run is measured. A line whose mapped cases run zero stays
  a fail. The report names the groups.
- **S-D10b:** the map reader reads every line a cell lists, or refuses naming the cell.

## What to review (the worktree `/home/usain/gov-os-worktrees/W2-96-d10b` holds both, merged for you)
- **Tests:** `88c0772ff` (designer): `tests/acceptance/W2-96/test_w2_96_at_d10a_optin.py`,
  `test_w2_96_at_d10b_cells.py`, a premise revision and the README rows. 25 red at integrate.
- **Code:** `04b52305a` and `3ac8e892f` (engineer): `src/gov/accept/runner.py` (`needed_optins`, `line_names`,
  `Unlisted`) and `tests/unit/accept/test_w2_96_d10.py`.
- **The engineer's measurements:**
  - `gov accept W2-96`: pass, optin breadth, 109/0.
  - `gov accept W1-27`: optin breadth, 159/19. The 19 are unmapped breadth cases; S8 is still 14/0 from a bare
    `name[row]` form.
  - `gov accept W1-46`: optin breadth and lifted, 386/107. Lines now fail on `lifted` cases, the features switched
    off here (DEC-1061, report-only in D-10's window).

## Check
1. **Run the designer's cases on this code** (both opt-ins, `-n 4`, then `tests/unit/accept`), and `gov accept W2-96`
   the declared way (`PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept W2-96`).
   Report counts.
2. **No fail-open:**
   - S-D10a: a line with zero run cases still fails; another ticket's cases never run; the report names exactly the
     groups enabled; no test content leaks.
   - S-D10b: the reader never drops a listed line silently, and refuses an unreadable cell naming it; no existing
     readable form changed meaning.
3. **The scope question for the CTO (PKG-D10a-scope),** your view with evidence. Enabling a group runs the ticket's
   whole folder under it, so unmapped and `lifted` (switched-off-feature) cases now count. That makes W1-46's
   formal accept fail on DEC-1061's report-only cases. Options:
   - (a) as built;
   - (b) enable only `breadth` (the tier-2 cut), and keep `lifted` report-only, a line resting only on lifted
     cases saying so;
   - (c) run only the mapped cases of the enabled groups, by node id.
   Which keeps KPIs measured without contradicting DEC-1061?
4. **Trailers** on all three commits.

KPI ids for the verdict block: `s-d10a-optin`, `s-d10b-reader`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
