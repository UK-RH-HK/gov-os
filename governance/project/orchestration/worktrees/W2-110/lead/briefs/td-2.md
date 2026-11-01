# Brief: independent test designer, W2-110 (DAEO-3r1j), run 2: the older install cases' revision (DEC-980)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-3r1j` (`W2-110`), profile FULL. You work only in the
tests worktree `/home/usain/gov-os-worktrees/W2-110-tests` on branch `w2/W2-110-tests` (DEC-963), made from the
ticket's head `0aa2854bb6ba`. You never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-110`).
You revise earlier tickets' acceptance tests that still enforce a superseded decision, under the CTO's decision
DEC-980 (P-W2-110-1 (a)). You are a headless session: nobody answers questions while you work, and only your final
message is read.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-3r1j','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-3r1j`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-110-tests` and
`w2/W2-110-tests`). If anything differs, stop and say so. `cd` to the tests worktree for every command.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src` set per
  command (never in a session's `--settings` env). Show it once with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`
  (a read; that store holds `w2/integrate` as of its last refresh). Never this ticket's worktree's store. For what
  changed since, read `w2/integrate` itself with `git show w2/integrate:<path>`. Never one giant query or context
  (DEC-860): a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked
  within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`,
  `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/install.py`, `tests/unit/guard/test_w2_110*`,
  `tests/unit/install/test_install.py`), and name in your return any such result you were served.
- **Policy 2 (DEC-820), reads open, writes closed.** You read freely: the whole repository, git history, other
  worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out
  qualification material (its file names may be seen); never read or name the qualification oracle; (c) **the
  counterpart's work on this ticket: you never read this ticket's implementation** — the four paths named under P-R1,
  in this worktree, in `/home/usain/gov-os-worktrees/W2-110`, on any branch (the version of the two code files on
  `w2/integrate`, which predates this ticket, you may read); this ticket's own acceptance tests
  (`tests/acceptance/W2-110/`, its README and support) are tests, and you may read them; (d) the hidden half of any
  evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that
  start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form,
  search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Put anything longer in a script file in your
  session's scratchpad (the Write tool refuses `.gov-runtime/scratch/td/`) and run that file. A refused form is not
  retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another (a suite that may outlive ten minutes is split into
  parts); return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this
  repository). A test that needs a repository builds a temporary one. Never write in `~/gov-os-workbench`; dev-tier
  tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists:
  conclude nothing from it.
- Install nothing (a tool you need is returned as a P1 package). No sudo. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never
  the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 8 GB and 400,000 files and folders, outside the tracked tree, as your share of the
  ticket's 20 GB / 1,000,000. Your temp folder is the one the sandbox sets (keep it). Keep pytest's own retention;
  never a per-run `--basetemp`; run pytest with `-o tmp_path_retention_policy=failed`. Remove every temp tree you made
  as soon as it is no longer needed. Measure your scratch (`du -s --inodes`, `du -sh`) at the end and give the
  figures in `evidence`. If you pass the budget, stop the heavy work, clean what you can, and return.
- Every suite is run to its end, never with `-x`. Never run the full test suite.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md` (read-only): its KPI lines and the DEC-980 paragraph.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-980 (item 1, your mandate), DEC-971 (item 4), DEC-957 (the install
  rule: only the CTO's own session asks the owner), DEC-083 (DEC-040 amended; the old rule "any orchestrator is
  asked"), DEC-117, DEC-163, DEC-491, DEC-866.
- **The rule as it now is (the public interface, from the ticket's KPIs):** in a project, the kernel guard asks the
  owner about an install only for the CTO: a session whose `GOV_ROLE` is `orchestrator`, acting as the orchestrator
  (the main thread, or an orchestrator subagent in that session), whose `GOV_TICKET` names the same ticket as the
  top-level key `coordination_ticket` of the project's `governance/project/roster.yaml`. The key's value, and
  `GOV_TICKET`, name a ticket of the project's `.tickets/` folder by its id (file name without `.md`) or its WBS id
  (`wbs_id` in its front matter). Every other session's install is refused, with words telling it to raise a P1
  escalation to the CTO. With no roster, no key, an empty or non-text value, a file that cannot be read or parsed, or
  a key naming no ticket of the project, every session's install is refused (fail closed), the CTO's included.
  Unchanged: sudo, the freeze, the research exception, the owner's prompt, its record and before-snapshot.
- `tests/acceptance/W2-110/` (its README and support) shows the same rule tested in a generated project.

## The cases to revise (DEC-980 item 1; the earlier test designer's list, verify each yourself)

They still assert DEC-083's "any orchestrator is asked" with no coordination-ticket key in their fixtures, and now
fail with "installs are refused in every session: the project's coordination ticket is not set
(governance/project/roster.yaml does not exist)":

- `tests/acceptance/W1-04/conftest.py::install_rule` (a fixture: `pip install requests` by the orchestrator on
  DAEO-zz91 is `ask`; it gates about 340 W1-04 cases); `W1-04/test_w1_04_install_rule.py`
  (`test_an_install_by_the_orchestrator_is_asked_about`, `test_the_ask_is_one_the_harness_shows_to_the_owner`,
  `test_inside_a_subagent_the_acting_role_decides`: its cases `orchestrator-subagent-in-orchestrator-session`,
  `-in-engineer-session`, `-in-designer-session`); `W1-04/test_w1_04_auto_mode.py`
  (`test_an_install_by_the_orchestrator_is_asked_about_in_every_permission_mode`,
  `test_an_orchestrator_subagent_is_asked_about_in_auto_mode_too`); `W1-04/test_w1_04_only_escalates.py::test_a_frozen_repository_stays_closed_to_an_install_that_writes`;
  `W1-04/test_w1_04_probe_findings.py` (the cases through `_assert_an_install`, and
  `test_while_frozen_an_install_is_denied_to_every_role_the_orchestrator_included`).
- `W1-47/test_w1_47_uv_installs.py` (`test_the_orchestrator_is_asked`, `…_in_every_permission_mode`,
  `…_for_the_forms_of_dec_216_in_every_permission_mode`, `test_the_uv_installs_of_w1_04_are_still_asked`);
  `W1-47/test_w1_47_kernel_template.py::test_the_template_s_guard_asks_before_an_install`.
- `W1-50/test_w1_50_freeze_guard_reading.py::test_the_install_rule_reads_the_flag_as_the_guard_does`.
- `W1-03/test_w1_03_calls_known_to_be_over.py`, case `install-ask-the-owner-declined-then-an-engineer-subagent`.
- `W1-05/test_w1_05_live_hooks.py::test_an_install_by_the_orchestrator_asks_the_owner_through_the_kernel_s_wiring`.
- `W1-46/test_w1_46_install_spellings.py::test_the_orchestrator_is_asked_about_uv_run_w_with_its_value_joined`.
- **Not yours:** `tests/unit/install/test_install.py` (an engineer revises it in parallel); this repository's own
  five-rule hook's suites (W1-33 and the like), which are not affected; `tests/acceptance/W2-110/`.

## The revision (DEC-980 item 1, exactly; nothing else lowered)

- **Rewrite-Reason: DEC-957, DEC-971 item 4** (DEC-866: the old decision DEC-083/DEC-117, the new DEC-957 and DEC-971
  item 4).
- **Each fixture project gets a roster** (`governance/project/roster.yaml` with a top-level `coordination_ticket`)
  whose value names its orchestrator's ticket (DAEO-zz91 and the like), and, where the project's `.tickets/` lacks
  that ticket, the ticket file, so the key names a ticket of the project. With it, the orchestrator's asks are kept as
  they are: the same answer, the same prompt, the same record and snapshot assertions.
- **The cases of an orchestrator subagent in a worker's session** (an engineer's, a designer's session, and the like)
  **flip to refused** (`deny`); where the case read the old ask's words, it now reads the refusal's P1-escalation
  words as `tests/acceptance/W2-110/` reads them. Nothing else flips.
- **Nothing else lowered:** no assertion removed or weakened, no case dropped or skipped, no deny turned into an ask,
  no new tolerance. A case already asserting a refusal keeps it. Prefer one shared fixture change per suite
  (its conftest or support) over per-case edits.
- **Cases you cannot bring back by a roster** (for example, a harness that runs the template's hook under the owner's
  pinned, installed `gov` rather than this worktree's `src/`, which answers "the installed gov has no CTO install
  rule"): give them the roster all the same, do not change the interpreter they run under and do not lower them; name
  each in your return with its failure line and why (it waits for the re-pin, ACT 2). A case that a roster would need
  a decision beyond DEC-980 to revise is a package, not a guess.
- Update each touched suite's README where it states the old rule, in one or two lines citing DEC-980.

## Run (each to its end, in the foreground, split if needed)

`TMPDIR` is the sandbox's own. For each touched suite folder (W1-04, W1-47, W1-50, W1-03, W1-05, W1-46):
`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/<suite> -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
before (the counts as they are) and after your revision. Report both counts per suite and every case still red after,
with its failure line. Also `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance --collect-only -q -p no:cacheprovider`
once at the end: no collection error. (`W1-46/test_w1_46_install_spellings.py::test_a_research_install_inside_the_experiment_folder_is_let_through[npm-install]`
also fails on `w2/integrate`; it is not yours: leave it and name it.)

## Commit

Commit only the files under `tests/acceptance/` that you revised, with the trailers in the final block:

    git commit -m "W2-110: the older install cases' revision: a coordination-ticket roster in each fixture (DEC-980)" --trailer "Task: DAEO-3r1j" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-980, DEC-971, DEC-957" --trailer "Rewrite-Reason: DEC-957, DEC-971 item 4" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Put in them: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits); each file
changed, with what changed (fixture, cases flipped to refused, by id); per suite, the counts before and after; each
case still red, with why; whether you used `gov retrieve` and how often; P-R1 results served; read refusals met; your
scratch figures; any package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
