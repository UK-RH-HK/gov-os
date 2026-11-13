# Brief td-1: independent test designer for DAEO-lrre (W2-33), profile STANDARD, class C2

You are the independent test designer (MR-3) for ticket DAEO-lrre (W2-33: the three layers' role files and the
machine-readable defaults per role). You write the acceptance tests from the ticket's KPI lines (S1 to S9, F1, F2)
and its `## Interface` section, before the product-spec worker writes the role files. You write to the ticket; you
never change it. A gap or a clash in it comes back as a package (status PACKAGES: question, options with cost,
recommendation, confidence, what it blocks), not as your own invention; a small reading the ticket does not settle
goes into the test's docstring, the README and `unresolved`. You never read the product-spec worker's work on this
ticket (branch w2/W2-33 after this brief's base `7d8c2d524`; there is none yet).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33-tests |
| branch | w2/W2-33-tests (base `7d8c2d524`) |
| your allowed paths | tests/acceptance/W2-33/** |
| the ticket (read it first, whole; its `## Interface` section is the contract for line forms) | /home/usain/gov-os-worktrees/W2-33-tests/.tickets/DAEO-lrre.md |
| the role files today (six; none has a Version, Launch default or Skills line yet) | template/governance/kernel/roles/{engineer,independent-auditor,independent-test-designer,orchestrator,product-spec,research}.md |
| the orchestrator's second copy (S9, F1) | template/.rulesync/subagents/orchestrator.md (front matter, then a body; today it still says "The guard asks on every install command" near line 112) |
| the approved roles spec (DEC-957) | governance/project/orchestration/packages/ROLES-SPEC-1.md: §3.0 (every role), §3.1 CTO, §3.2 Senior Engineer, §3.3 ticket lead, §3.8 the reviewer (now the QA engineer, DEC-959 item 3), §3.9 auditor, §5.1-5.2 the line form |
| RUBRIC-2's values as applied (S7) | governance/project/orchestration/packages/RUBRIC-2-APPLY.md lines 95-125; DEC-1120, DEC-1119 in the register |
| W2-60a's reader of the lines (the form your parser must agree with) | `git show w2/W2-60a:src/gov/launch/role.py` lines 35-60: `VERSION_LINE`, `DEFAULT_LINE`, `SKILLS_LINE`, `_one_line` (a line is found by its head after `lstrip`, then `fullmatch`ed against the whole raw line, so it must start at column 0 and carry nothing after the value) |
| the install key (S9) | `coordination_ticket` (src/gov/guard/install.py:257, `COORDINATION_KEY`; read from `governance/project/roster.yaml`); W2-113's ticket .tickets/DAEO-g29a.md lines 28-34 for the rule's wording (DEC-971 item 4) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-954, DEC-957, DEC-959, DEC-963, DEC-983, DEC-982, DEC-847, DEC-1010, DEC-1119, DEC-1120, DEC-236, DEC-839, DEC-971, DEC-1156 (3) and (4), DEC-1155 |
| the ticket's context packet (`gov context DAEO-lrre --role independent-test-designer --budget 20000`, built by your lead; the default 6000-token ceiling refused it) | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/ctx-td.json |
| earlier role-file suites, for form only (do not edit them) | tests/acceptance/W1-33/ (test_w1_33_kernel_role_files.py, w1_33_support.py), tests/acceptance/W2-62/ (a CIT-P suite) |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The target set of role files
After the work, `template/governance/kernel/roles/` holds nine role files: the six above plus `ticket-lead.md`,
`qa-engineer.md` and `senior-engineer.md`; `independent-reviewer.md` does not exist. "Every role file" means every
`*.md` in that folder (state how you treat a README if one appears). Require the nine to be present; check each rule
on every file found, so a tenth file is checked too.

## What to test (one test or more per line; name each after its id: `test_s1_...` … `test_f2_...`)
Build one checker (a function over a roles folder that returns the list of failures, each naming the file and the
rule) and use it both on the real folder and on planted copies in `tmp_path` (F2). Every failure message names the
file and the missing or malformed line, since the writer sees only the failing output.

- **Line forms, word for word from the Interface** (each once and whole, at column 0, in every role file; parse with
  regexes equal in effect to W2-60a's):
  `- **Version:** x.y.z` · `- **Launch default:** model <id>, effort <e>` · `- **Skills:** a, b` ·
  `- **Model tier:** see Launch default` · and only where RUBRIC-2 varies, `- **Launch by criticality:** C3 model <id>,
  effort <e>; C2 …; C1 …; C0 …`. "Opus" = `claude-opus-5-5`, "Sonnet" = `claude-sonnet-5-5`.
- **S1:** `ticket-lead.md` exists and names its reads, its writes and its handover (the ticket gives no line heads for
  these: accept the heads the role files use today, `Allowed paths` / `Handoff format`, or `Reads` / `Writes` /
  `Handover`, as you judge from ROLES-SPEC-1 §3.3, and state the reading); `orchestrator.md` has 0 lines matching the
  heading `## The ticket lead`.
- **S2:** every role file has the Version, Launch default (model and effort) and Skills lines; each skill named exists
  under `template/governance/kernel/skills/<name>/` (your reading; say so if you keep it); orchestrator.md and
  senior-engineer.md give effort high; a planted file missing any one of the three keys fails, naming file and key.
  Not here: "the launcher's plan prints the file's model and effort" is judged in W2-60a (Interface).
- **S3:** `qa-engineer.md` exists, `independent-reviewer.md` does not; the file states read access to the spec, the
  KPIs, the tests and the code, that it changes none of them, and that it writes only its findings report; it carries
  the line head `- **Per stream:**` stating core tickets (the guard, the close, memory's retrieval, anything that could
  fail open) one by one before they merge and the others in batches of up to about five;
  `independent-auditor.md` still names the milestone audits. Not here: the guard's refusal of a planted QA write
  elsewhere (W2-60b).
- **S4:** the work-order line, the same sentence, word for word in every file:
  `- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both.`
  A planted file without it fails. `independent-test-designer.md` and `engineer.md` each state, in their allowed
  paths, that reads of the other's work (the counterpart's work on the same ticket) are denied.
- **S5:** the one-writer line, word for word in every file:
  `- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead.`
  A planted file without it fails. Not here: the launcher's refusal of two writers in one worktree (W2-60b).
- **S6:** `qa-engineer.md` carries the line heads `- **Moderator:**` (triages every finding against the ticket's own
  scope and KPIs), `- **Wave 3 row:**` (a finding out of scope, or needing an unusual construction, is a Wave 3 row,
  never a round), `- **Verdict:**` (the structured verdict per KPI), `- **Rounds:**` (at most two review rounds per
  ticket), each with the KPI's wording (build matchers from the KPI's own words, case-insensitive and
  whitespace-normalised; strict on content). Not here: the planted review brief, which the reviewer runs as a probe.
- **S7:** a test per role file (parametrise over the nine) that reads both lines and compares the values to this
  table; a missing or malformed line fails:
  | role file | Launch default | Launch by criticality |
  |---|---|---|
  | orchestrator, ticket-lead, senior-engineer | claude-opus-5-5, high | absent |
  | engineer | claude-sonnet-5-5, high | C3 claude-opus-5-5 high; C2, C1 claude-sonnet-5-5 high; C0 present and well formed |
  | independent-test-designer | claude-sonnet-5-5, high | C3 claude-opus-5-5 high; C2, C1 claude-sonnet-5-5 high; C0 present and well formed |
  | qa-engineer | (the ticket does not state it: require well formed, state your reading; the lead's suggestion is claude-sonnet-5-5, high, the C1 value) | C3 claude-opus-5-5 high; C2 exactly `C2 model claude-opus-5-5, effort high on FULL, model claude-sonnet-5-5, effort high otherwise`; C1 claude-sonnet-5-5 high; C0 present and well formed |
  | independent-auditor | claude-opus-5-5, high | absent |
  | product-spec, research | claude-sonnet-5-5, high | absent |
  C0: S7 gives no C0 value (RUBRIC-2-APPLY.md:23 says "Haiku or deterministic"); the lead's reading is: require the
  C0 entry present with a model id and an effort, do not assert its value; record it in `unresolved`. "Absent" follows
  the Interface's "only where RUBRIC-2 varies". Every file keeps `- **Model tier:** see Launch default`. No role file
  states the through-D-10 rule for engineers (the CTO's practice): a negative check on "D-10" is your call.
  Not here: the generated agents carrying the same lines (W2-153).
- **S8:** `senior-engineer.md` holds its reads and writes, its skills line, `Launch default: model claude-opus-5-5,
  effort high`, its brief contents and its handover (ROLES-SPEC-1 §3.2; same head tolerance as S1, stated);
  `orchestrator.md` is the CTO's file (it names the CTO / master orchestrator; the file name and role id
  `orchestrator` are kept).
- **S9 and F1:** in each of `template/governance/kernel/roles/orchestrator.md` and
  `template/.rulesync/subagents/orchestrator.md`: the CTO-only install rule is stated (only the orchestrator on the
  project's coordination ticket is asked for an install; every other session is refused), the key
  `coordination_ticket` and `GOV_TICKET` are named; no sentence says the guard asks on every install (F1: 0 lines
  matching that old wording; build the pattern so "The guard asks on every install command" and close variants match).
- **F2:** planted copies of the real folder in `tmp_path`, each with one departure (a line form broken, the work-order
  or one-writer sentence altered, a defaults block removed, a value off the S7 table): each fails the checker, the
  failure naming the planted file; none passes. Not here: "one edited by hand in the generated folder" is W2-153's
  generation check (Interface).
- Fields of ROLES-SPEC-1 §5.2 that the Interface does not name (Launch, Ticket, Network, Guard class, Writes, Tools,
  Brief template, Return): not required here (the Interface is the owner-approved form; DEC-1156 (3)); say so in the
  README.
- Non-goals (no test): the CIT-P record `docs/changes/W2-33-CIT-P.md` (the lead writes it for the owner), the
  handoff schema and template (moved to Wave 3), `.claude/agents/**` and the other `.rulesync` copies (W2-153 and the
  copies ACT), the launcher, the guard.

## Rules
- Tests read files only; no network, no model, never the store. Locate the repository from `Path(__file__)`
  (parents[3]). If you run any child process, give it this tree's `src/` first on `PYTHONPATH`.
- Any path case compares paths with `Path.is_relative_to`, never a text search of a temporary path; a case of the form
  "the branch changes only the ticket's allowed_paths" judges only branch w2/W2-33 and skips elsewhere, naming the
  branch found (DEC-1155).
- Tests are red now (the three files do not exist; no file has the lines). Run them and say which are red and why;
  anything green now is a fault in the test unless it guards something that already holds (say which: e.g.
  `independent-reviewer.md` absent, the auditor's milestone audits).
- Older suites your target state will turn red (for example tests/acceptance/W1-35/test_w1_35_orchestration.py:205
  `TestTicketLeadSection`, and any W1-33 roster case counting six roles): do not edit them (not your paths); list each
  with file:line in `discoveries`.
- No test named with `real`, `green_here` or `time_limit`. Keep the folder to seconds.
- **Every pytest through the heavy-slot gate**, TMPDIR outside the repository and outside ~/gov-os-runs (the folders
  exist; recreate with `mkdir -p` if not):
  `TMPDIR=/tmp/gov-w2-33-td bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33-tests/src python3 -m pytest tests/acceptance/W2-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A heavy-slot or resource refusal is a wait: run again when it opens.
- Add `tests/acceptance/W2-33/README.md`: how the tests reach the files, each KPI's cases, the clauses judged
  elsewhere, your readings.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-lrre" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-954, DEC-957, DEC-959, DEC-963, DEC-983, DEC-982, DEC-847, DEC-1010, DEC-1119, DEC-1120, DEC-236, DEC-839" -- tests/acceptance/W2-33`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers), `readings:` (each reading you chose where the ticket is silent: the reads/writes/handover heads,
the skills existence check, QA's Launch default, C0, a README in the folder, the D-10 check) and `guard_refusals:`
(none, or each: time | form | the hook's reason | true or false-positive).
