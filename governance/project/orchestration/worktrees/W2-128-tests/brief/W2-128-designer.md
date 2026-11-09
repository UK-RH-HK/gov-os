Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 1 — the independent test designer's brief (DAEO-t8mp)

You are the independent test designer for **W2-128** (`.tickets/DAEO-t8mp.md`): the templates, one per role, the
ticket and the brief envelope, filled from the ticket and one facts file (R3-TEMPLATES TPL-1 to TPL-8; DEC-1050,
DEC-1052, DEC-1083, DEC-1088 (3), DEC-1094 (4), DEC-1073 (5)(c)). Profile STANDARD. Read first, in full: the ticket
(its KPI lines **and its body's "Interface and rounds" section**, which fixes the file names, the placeholder syntax,
the key list, the facts file's shape, the prose measure and the schema fields: build on it, do not guess past it);
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B, §C, §D and the Appendix (T-0 to T-8);
`LINK-INTEGRITY.md` §5; `D5-ROWS.md` (rows 1-17).

## This round: the text half only
Write cases for these KPI lines (positions in the ticket; the README's KPI cell uses the position, `S<n>` for the
n-th success line, `F<n>` for the n-th failure line, because the ticket's lines begin with TPL labels):
- **S1-S5** (TPL-1 S1-S5): the nine files and their `name`/`version`/`role` front matter; prose within R3 §C's budget
  (the ticket's prose measure); the three DEC-957/959/963/1010 string facts; the `brief-*.md` pointers and
  `roles/engineer.md` line 5; every placeholder a key in `templates/keys.yaml` or a `CMD:`/`STEP:` key of `facts.yaml`.
- **S6** (TPL-2) for S1, S2 and S4 only: `facts.yaml` validates against `facts.schema.json`; every `commands` entry
  has a `check:` and each check runs and exits 0 in a temporary copy or temporary repository (no model, no network, no
  GPU, no `gov retrieve` other than `--help`, each under a few seconds: assert those limits too); `dod` at most six
  items, quoted by id in T-1 and T-7. **S3 (a switch flipped in a filled brief) is round 2**: say so in the README.
- **S8** (TPL-3 S5): `facts.yaml` names `lead_verify`, `launch_worker`, `wait_for` and the templates name each in one line.
- **S10** (TPL-5) for S1 and S2 only: the ticket schema accepts `non_goals`, the `{line, verify}` KPI form beside the
  string form, `reads`/`needs`/`waits_on`, and **every existing ticket in `.tickets/` stays valid** (`gov check` schema
  or the schema validator on them); T-1 is the ticket template. The ready check (S3) is round 2.
- **S14** link lines: a string test per template for LINK-INTEGRITY §5's lines for that role (and the record
  templates); the planted-record `gov links` case if `gov links` can run on a temporary tree in the sandbox (try it;
  if not, mark that half untestable here and say why).
- **S15** the facts' `links` command (`gov links --since {BASE}`) with its check; T-7's return quotes its first line.
- **S16** the lesson, failure and research schemas allow optional `sources` (and research `decisions`); every existing
  record of those types stays valid.
- **S17** for its round-1 part only: `docs/changes/W2-128-CIT-P.md` exists and names its evidence (R2, R3) and CAP-33;
  the review, the owner's approval and the promotion are later (say so).
- **S18** T-6 asks the reviewer, per finding, for the evidence that would reverse it.
- **S19** the dependency fields' template part (T-1 sets `reads:`, `needs:`, `waits_on:` beside `allowed_paths:`, with
  their meanings); the refusals (`READS_MISSING`, `NEEDS_MISSING`, `WAITS_ON_MISSING`) are round 2.
- **S20** search again once: the four strings in T-0's Commands block right after the "Ask memory first" line, and
  T-8's Start line naming it.
- **S21** D5-ROWS rows 1-9 in the named templates, one string test per row (test the substance, e.g. `Task:` of the
  revised ticket, `':!tests/acceptance'` or `--stat`, `--role`, the ticket's own id, no merge in the sandbox, the
  pytest marker form, the full node id, `gov accept` outside the sandbox until W2-56, the interface before the pair).
- **F1** a `{CMD:…}`, path key or command form in a template that is not in `facts.yaml`; **F7** a bracketed decision id
  in a template that is not ACCEPTED in `docs/DECISION_REGISTER.md` (read the register at test time).
- **Round 2, not now (list them in the README as "round 2: not mapped"):** S7, S9, S11, S12, S13, F2-F6 and the
  round-2 halves above.

Prefer facts that must hold whatever words the writer chooses (presence of a key, a front-matter field, a size, a
schema result, a required phrase that the ticket or R3 quotes). Do not pin prose the KPI lines do not quote. Say for
each case whether it is red on integrate for the right reason, or a green guard (e.g. existing tickets valid today).

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-128-tests`, branch `w2/W2-128-tests`, made from `w2/integrate` at
  `75a29ff6` today.
- You write only `tests/acceptance/W2-128/`: the cases, a `conftest.py` and a support module if needed, and a
  `README.md` whose map the runner reads: header `| KPI line | Test (node id) | On integrate | Why |`, one id such as
  `S1` in each KPI cell, each test in backticks with its full node id (as `tests/acceptance/W2-142/README.md`).
- **Your record:** write your return (the twelve fields) also to
  `/home/usain/gov-os-worktrees/W2-128-tests/.gov-runtime/scratch/lead/W2-128-designer-return.md`.
- You may read anything on `w2/integrate` (DEC-963): today's `template/governance/kernel/templates/`, the schemas,
  `roles/engineer.md`, `src/gov/check/schema.py`, `src/gov/links/`, `tests/acceptance/W2-142/` for the form.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** never open `/home/usain/gov-os-worktrees/W2-128` or
  the branch `w2/W2-128` if either appears, nor the product-spec worker's files on this ticket.
- **The exclusion line (DEC-1093 (2)):** keep every Grep, Glob and recursive Bash search inside your own worktree, never
  from `/home/usain/gov-os-worktrees/` or `/home/usain/`; if a search shows you a line of the implementation anyway,
  stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox) does not
  answer, search once more in your own, different words; then answer from both with path and lines, or say "not
  found". Two searches in all.
- No GPU, no model, no network, no installs. **The hidden-half rule:** never open anything under `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- Run only your own cases: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tests/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider`
  with an empty `HOME`, never the whole suite; then
  `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-128-tests`, only `tests/acceptance/W2-128/`, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1050, DEC-1052, DEC-1073, DEC-1088, DEC-1092" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- No merge inside the sandbox. Before you end, make sure every test run you started has finished.
- Size: about 30 to 45 cases; keep each file focused (one per area: templates, facts, schemas, links, rows).

## Return
Your whole return is your session's final message: the twelve labelled fields of `EMG-common.md` (sandbox check and
`ps` check first), the case list (node id, KPI line, red or green on integrate, and why), the commit, `gov accept`'s
counts, the `TESTS-READY <hash12>` line, and anything untestable or ambiguous in the ticket's interface as
`discoveries`.
