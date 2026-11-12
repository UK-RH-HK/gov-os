# Brief: independent test designer, W2-110 (DAEO-3r1j), run 3: W2-105's fixture gains a roster (P-W2-110-5 (a))

You are a fresh independent test designer (MR-3). Ticket: `DAEO-3r1j` (`W2-110`), profile FULL, class C3. You work only
in the tests worktree `/home/usain/gov-os-worktrees/W2-110-tests` on branch `w2/W2-110-tests` (DEC-963), made from the
ticket's head `7313e9891aaf`. You never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-110`).
You make one small revision of an earlier ticket's acceptance tests (W2-105's), decided by the CTO as P-W2-110-5 (a)
under DEC-980 and DEC-971 item 4. You are a headless session: nobody answers questions while you work, and only your
final message is read.

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
  (a read). Never this ticket's worktree's store. For what changed since, `git show w2/integrate:<path>`. Never one
  giant query (DEC-860): batches (`--batch-size`, then `--continue <token>`). A code question uses the code-graph
  tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted (DEC-859).
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/install.py`, `tests/unit/guard/test_w2_110*`,
  `tests/unit/install/test_install.py`), and name in your return any such result you were served.
- **Policy 2 (DEC-820), reads open, writes closed.** You read freely: the repository, git history, other worktrees.
  Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file
  names may be seen); never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you
  never read this ticket's implementation** (the four paths under P-R1, in any worktree or branch; their versions on
  `w2/integrate` that predate this ticket you may read); this ticket's acceptance tests (`tests/acceptance/W2-110/`,
  its README and support) are tests, and you may read them; (d) the hidden half of any evaluation set, by whoever is
  measured by it.
- **Read refusals (DEC-849):** the guard still refuses some reads (searches starting at the repository root,
  `governance/project/` or `.claude/`). Take the refusal, never another form, search named folders, count them.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Anything longer goes in a script file in your
  session's scratchpad, then run it. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commit exists.
- No `git checkout` of another commit, no reset, no clean, no amend, no rebase, no push, no merge.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Never
  write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only.
- `.gov-runtime/freeze` shows as a placeholder device file inside a launched session: conclude nothing from it.
- Install nothing (a tool you need is a P1 package in your return). No sudo. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`. No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, commit hashes as 12 digits, never the
  full 40, and never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Scratch budget (DEC-898):** 4 GB and 200,000 files and folders, outside the tracked tree, your share of the ticket's
  20 GB / 1,000,000. Keep the sandbox's temp folder; pytest's own retention, never `--basetemp`; pytest with
  `-o tmp_path_retention_policy=failed`. Remove temp trees you made. Measure (`du -s --inodes`, `du -sh` of your temp
  folder) at the end, figures in `evidence`. Past the budget: stop, clean, return.
- Every suite is run to its end, never with `-x`. Never run the full test suite.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md` (read-only): its KPIs, the DEC-980 paragraph and the last paragraph
  ("Delegated (the CTO, DEC-1112 (3) ... P-W2-110-5 (a)"), your mandate.
- `docs/DECISION_REGISTER.md`: DEC-980, DEC-971 (item 4), DEC-957, DEC-966 (item 1), DEC-491, DEC-866.
- **The rule as it now is (from the ticket's KPIs):** in a generated project, the kernel guard asks the owner about an
  install only for the CTO: a session whose `GOV_ROLE` is `orchestrator`, acting as the orchestrator, whose
  `GOV_TICKET` names the same ticket as the top-level key `coordination_ticket` of the project's
  `governance/project/roster.yaml` (by ticket id, the file name in `.tickets/` without `.md`, or by `wbs_id`). Every
  other session's install is refused (raise a P1). With no roster, no key, or a key naming no ticket of the project,
  every session is refused (fail closed), the CTO included. `tests/acceptance/W2-110/README.md` shows the roster's
  form (its configuration table, `key-by-id`).
- W2-105's suite: `tests/acceptance/W2-105/` (README, `conftest.py`, `w2_105_support.py`,
  `test_w2_105_install_block.py`). Its support already names `COORDINATION_TICKET = "DAEO-zz91"` and gives the
  orchestrator that ticket, but the generated project it builds has no roster.

## The cases (verify yourself)

On this head, two cases are red, both failing with "the guard's own answer: ['deny']":
`tests/acceptance/W2-105/test_w2_105_install_block.py::test_an_install_by_the_orchestrator_on_its_coordination_ticket_is_asked_by_the_guard`
`[npm install -g ccusage]` and `[pip install requests]`. They pass on `w2/integrate` (which lacks W2-110's rule).

## The revision (P-W2-110-5 (a), exactly; nothing else lowered)

- **Rewrite-Reason: DEC-971 item 4, DEC-980** (DEC-866: the old rule "any orchestrator is asked", DEC-083; the new,
  DEC-957 and DEC-971 item 4).
- **W2-105's fixture project gets a roster:** `governance/project/roster.yaml` with a top-level
  `coordination_ticket: DAEO-zz91`, and, if the project's `.tickets/` lacks DAEO-zz91's file, that ticket's file, so the
  key names a ticket of the project. One change in the shared fixture (support or conftest), not per-case edits.
- **Nothing else lowered:** no assertion removed or weakened, no case dropped, skipped or marked, no deny turned into an
  ask, no new tolerance. The other roles' cases (engineer, test designer, and any lead or worker session) stay
  refused. If the roster changes any other case's result, stop and name it: that is a package, not a fix.
- If W2-105's README states the fixture or the old rule, add one or two lines citing DEC-980 and P-W2-110-5 (a).
- Write only under `tests/acceptance/W2-105/`.

## Run (each to its end, in the foreground)

`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/W2-105 -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
before (the counts as they are) and after your revision; report both, and every case red after, with its failure line.
Then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110-tests/src python3 -m pytest tests/acceptance/W2-105 --collect-only -q -p no:cacheprovider`: no collection error.

## Commit

Commit only the files under `tests/acceptance/W2-105/` that you revised, trailers in the final block:

    git commit -m "W2-110: W2-105's fixture gains a coordination-ticket roster (P-W2-110-5 (a), DEC-980)" --trailer "Task: DAEO-3r1j" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-980, DEC-971, DEC-957" --trailer "Rewrite-Reason: DEC-971 item 4, DEC-980" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Put in them: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits); each file
changed and what changed; the counts before and after; each case still red, with why; whether you used `gov retrieve`
and how often; P-R1 results served; read refusals met; your scratch figures; any package (question, why now, options,
impact, reversibility, cost, recommendation, confidence).

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
