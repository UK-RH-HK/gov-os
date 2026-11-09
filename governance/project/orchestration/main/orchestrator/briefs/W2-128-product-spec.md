# W2-128 round 1 — the product-spec worker's brief (DAEO-t8mp)

You are a fresh product-spec worker for **W2-128** (`.tickets/DAEO-t8mp.md`): the templates. Read the ticket in full
first, **especially its body's "Interface and rounds" section** (the file names, the placeholder syntax, the key list,
the facts file's shape, the prose measure, the schema fields: these are fixed; follow them). Then
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B, §B′, §C, §D and the Appendix (T-0 to T-8 are
the starting texts), `LINK-INTEGRITY.md` §5 (the link lines per role), `D5-ROWS.md` rows 1-17, and
`SEARCH-AGAIN-PRACTICE.md` §2 (the T-0 line is quoted in the ticket's S20).

## This round: the text half only (the ticket's round 1)
- **The nine templates** in `template/governance/kernel/templates/`: `brief.md` (T-0), `ticket.md` (T-1, replacing
  today's), `role-research.md`, `role-product-spec.md`, `role-test-designer.md`, `role-engineer.md`,
  `role-reviewer.md`, `role-lead.md`, `role-cto.md`, from R3's Appendix, each with `name`, `version`, `role` front
  matter, each within R3 §C's prose budget. Carry into them: LINK-INTEGRITY §5's lines (rows 10-17), D5-ROWS 1-9 in
  the templates the ticket's S21 names, the dependency fields in T-1 (S19), search again once in T-0 and T-8 (S20,
  exact text), the reviewer's reversal line in T-6 (S18), `JUDGEMENT.md`'s content as a section of T-6 (TPL-6 S4's
  template half). A line enters only where it changes what a session does; an imperative ending with its decision id
  in brackets, **ACCEPTED ids only** (check each in `docs/DECISION_REGISTER.md`; F7); no history.
- **`templates/keys.yaml`**: the key list, every placeholder the templates use.
- **The record templates** (`checkpoint.md`, `decision-record.md`, `decision-package.md`, `failure.md`, `lesson.md`,
  `research.md`) gain their link lines (S14). **`brief-*.md`**: each becomes a one-line pointer to its replacement.
  **`roles/engineer.md` line 5:** "to fulfil the spec and its KPIs" (TPL-1 S4); nothing else in the role files.
- **`governance/project/facts.yaml`** and **`template/governance/kernel/schemas/facts.schema.json`** (TPL-2 S1, S2, S4;
  S8; S15): `paths`, `commands` (each with `run:` and a `check:` that exits 0 safely in a temporary repository: `--help`,
  a dry run or a no-op; no model, network or GPU; `retrieve`'s check is `--help`), `dod` (at most six, by id), `steps`
  (today's switches from R3 §B′, defaults per P1, each with `line:` and `match:`), `budgets` (R3 §C),
  `harness_allowed`. The three scripts are under `{TOOLS}` = `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/`.
- **The schemas** (S10's S1, S16): `ticket.schema.json` gains `non_goals`, the `{line, verify}` KPI form beside the
  string, `reads`, `needs`, `waits_on`, all optional; `lesson`, `failure`, `research` gain optional `sources`, research
  optional `decisions`. Every existing record must stay valid: run `python3 -m gov.check.schema` before you commit.
- **`docs/changes/W2-128-CIT-P.md`**: the CIT-P record's draft (S17): the change, its evidence (R2, R3, the counts R3
  cites), the kernel files touched, CAP-33's steps with the review, the owner's approval, the promotion and the
  `.claude/` copies ACT marked "to come".
- **Points the test design raised (the CTO's notes, no case text):** a template's `role` front matter is a plain
  string (`any` for T-0 and T-1), never `{ROLE}`; no `{FACT:…}` family (R3's T-7 uses one: make it a KEY or a `CMD:`);
  `waits_on` items are a string or `{ref, reason}` (never the key `on`); any `gov <subcommand>` or script a template
  names in code needs its `facts.yaml` command (F1), including `gov context` (D5 row 3) and `gov accept`; T-0 must carry
  both "Ask memory first: {CMD:retrieve}" (S20's neighbour) and D5 row 6's "no `gov retrieve` in the sandbox", without
  contradiction; T-8 carries LINK-INTEGRITY §5's `gov links --since HEAD~1` for the CTO while the facts' `links`
  command is `--since {BASE}`; cite no DONE-status register entry in brackets (F7 reads ACCEPTED only); keep each rule
  on its own line or list item ending with its id.
- **Not this round:** `gov brief`, the ready check's refusals, the launcher flag, the dispatcher, the `.claude/` copies,
  the skills (TPL-6 S3), the CTO prompt, `LEAD-w2-common.md` (round 2 or the owner's).

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-128`, branch `w2/W2-128`: `w2/integrate` with the designer's
  cases merged in by the CTO.
- **Your paths** are the ticket's `allowed_paths` (the guard refuses the rest). The generated `.claude/` copies are not
  yours (DEC-315).
- **You never read `tests/acceptance/W2-128/`** (DEC-820 (c)): run those cases only through
  `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128` and read only its results. Every
  Grep or Glob call that could reach it carries `!tests/acceptance/W2-128/**`, every recursive Bash search
  `--exclude-dir=W2-128`. If `gov accept` crashes in the sandbox (it can with an empty `HOME`, D5 row 8), run
  `python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -rf` instead and read only its result lines (the
  failing node ids and assertion messages), never the case files; the CTO runs `gov accept` outside the sandbox.
  There are 92 cases (TESTS-READY `bd7732def530`), 8 green guards today.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no network, no installs, no `gov retrieve` in the
  sandbox. No whole-suite run; `gov accept W2-128` and the schema and skills checks only, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128/src`.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own, different words;
  then answer from both with path and lines, or say "not found". Two searches in all.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-128`, only your paths, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-1050, DEC-1052, DEC-1073, DEC-1088, DEC-1092" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- An interface point the ticket leaves open: choose the simplest reading and name it in `discoveries`; never widen the
  scope.

## Return
Your whole return is your session's **final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox
and `ps` checks first), the files changed, each template's prose size against its budget, `gov accept W2-128`'s counts
(and each failing case's node id and message), the schema check's output.
