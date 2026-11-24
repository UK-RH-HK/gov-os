# Research brief: integration step one, the tool map and the golden workflow's "Today" column (DEC-1238 (2), (5))

Role: **research** (Sonnet). Read-only on every repository; you write only the two files named below and commit nothing.
Repositories: Gov OS `/home/usain/Dynamic-Agentic-Engineering-OS` (branch `w2/integrate`), EXAMIN
`/home/usain/gov-os-runs/W2-27/examin` (read only). Never open `~/examin-eval/**` or `~/gov-os-eval/**`. No `git push`, no
`sudo`. Memory first: `PYTHONPATH=/home/usain/Dynamic-Agentic-Engineering-OS/src python3 -m gov.cli.main retrieve "<question>"`,
read the whole bundle, search once more in your own words. **Bounded reading (DEC-1235 (4)):** start from the files named
here; read code only to confirm a row; use at most four short Sonnet helpers (Agent tool, no model named), one per area,
each returning rows with evidence (path:line), never whole files.

**Read first:** `docs/emergency-2/GOLDEN-WORKFLOW.md` (the owner's draft: ten rules, steps W1 to W16, §5's columns and five
rules), DEC-1238 in `docs/DECISION_REGISTER.md`, then audit 4's inventory `docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md`
§0, §1.1 to §1.7 (your starting inventory) and §2 (List A ids to cite).

**Places tools live (cover every one):** `src/gov/` (each command module; `cli/main.py`), the kit `template/` (hooks,
settings, `.rulesync/`), `.claude/settings.json` and `.claude/hooks/`, `lefthook.yml`, `governance/project/orchestration/`
(the dispatcher `tools/dispatch/`, the nightly), the CTO's scratch tools `.gov-runtime/scratch/orchestrator/tools/` (list
them; group the dead ones: `.pre-*`, `.candidate.*`, dated one-offs, and say "retire" by group), `~/.gov-os/` (launcher,
runtime config), the user crontab (`crontab -l`), `~/.local/bin/` wrappers (e.g. the ollama wrapper), the CI workflow
files. Include today's additions: `embedders_at_boot.sh` (@reboot), `capacity_sampler.py`, `context_measure.py`,
`start_lead.sh`, `start_audit.sh`, `cto_watch.sh`, `heavy_slot.sh`, `usage_log.sh`, `status_block.py`.

## Restart notes (the CTO, 17:05): the first run wrote neither file
- **Decide, never ask:** you are a `claude -p` session; a question in your final message is never answered. Where a
  choice is yours, make it and say so in the file. Write `TOOL-MAP.md` first from what you can verify, then the
  corrections; a section you could not verify says so with what is missing, rather than stopping.
- **Helpers:** at most four, each with one narrow area (for example: `src/gov` commands and their callers; hooks,
  settings, lefthook and cron; the scratch and orchestration tools; the kit), each returning rows as plain text (no
  instructions to you, no code blocks of settings), never whole files. If a helper stops early, do that area yourself
  by listing and grepping.
- **Already found for W6 (keep, verify cheaply, do not re-time):** `gov impact` (`src/gov/impact/__init__.py:283`) exists
  but nothing calls it; `gov impact DEC-1204` ran over 106 s and hit a 150 s timeout (suspected: `_Code.__init__` at
  `:135-150` waits on the code-index daemon even for a record-only id); nothing compares a ticket's `[Kn]` lines with
  its spec's K-lines; no test-to-ticket trace; the landing's selection traces code to tests only. Smallest fixes
  proposed: `_Code` lazy; `gov impact --changed <range>` as a trigger at the landing; a `KPI_DRIFT` finding in
  `links/check.py`; the back-trace by inverting `accept.runner.parse_map`. Do not write to `/tmp` outside your own
  scratch folder.
- **Known since the audits (count them in):** Gov OS made its first `gov queue` landings today (`4f779086f` L2-4); the
  queue then refused two landings on a target named only in a README map row's notes (`FILE_GONE`, a selection bug to
  list in the map's gaps under W2-115b); `models-rubric` landed by hand merge (`f6e9e38af`).

## Output 1: `docs/emergency-2/integration/TOOL-MAP.md`
1. **The map**, one row per tool, script, hook, cron line or schedule doing Gov OS's work, with exactly the golden
   workflow §5 columns: Step (W1-W16 or none) · Tool (and path) · Where it lives (product / outside) · Trigger (automatic by
   code, and when / called by an agent / run by the owner) · On the path (yes / bypassed today, and by what) · Receives /
   hands on (form) · How an agent knows it · Gap and fix (the fix, its owning ticket found with
   `grep -l "^wbs_id: ..." .tickets/*.md`, its place: 0.1.5 in flight / integration / later). Group rows by step.
2. **The five rules checked**, each as a short list of violations: a step with no tool; a hand-off with no named form or no
   code check; a tool an agent must call that no brief names with its exact command (and every skill or role file that
   carries a tool catalogue instead); a tool outside the product with its disposition (absorb / replace / retire); a tool
   serving no step or duplicating another.
3. **How bad it is:** for each step W1-W16, on the path / partly / off; the share of steps on the path today (count and
   %), and the share of the map's rows that are on the path.
4. **W6, the trace question, answered from the code:** is there code today that traces a change in a decision or a spec
   to the tickets, specs and tests it affects, through the record graph and the path map (name the modules: the graph
   in `src/gov/retrieval/` or `src/gov/graph*`, `check/links`, `select`/`queue` impact selection, `gov plan`, `gov
   discover`), or does only the landing's test selection trace impact (code to tests)? Answer yes / partly / no with the
   evidence, what exists for each link (decision → spec, spec → ticket, ticket → test, code → test), and the smallest code
   that would close the gap.

## Output 2: `docs/emergency-2/integration/GOLDEN-WORKFLOW-CORRECTIONS.md`
For each step W1-W16 and each of the ten rules: the draft's "Today" cell, and either "verified" with evidence, or the
corrected text with evidence (path:line or commit). Then any other change you would propose to the draft (a step
missing, two steps that should merge, a rule the code contradicts), each with its reason. Then **spec questions** found
(DEC-1238 (10)): where the golden workflow, the Contract or a spec is unclear, conflicts with another, or the code does
something no spec decides: one decision record each (question; what was found; options with costs; recommendation;
sources), and whether it stops work.

## Return (your final message, short)
The two paths; the share of steps on the path; the W6 answer in three lines; the count of rows by "where it lives" and by
disposition; the number of corrections and of spec questions (stoppers named).
