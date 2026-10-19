You are a fresh independent test designer (MR-3). Ticket: DAEO-7rr2 (W2-53, "The probe gate measures every later merge against git's own merge of its parents"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-53` on branch `w2/W2-53`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-7rr2`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-53` and `w2/W2-53`). If anything differs, stop and say so.
- **DEC-732, the code under test (word for word from the lead's brief):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your tests, run from this worktree, must exercise this worktree's code; your README says how.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Commit your tests before you run any long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (you should need none).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it). A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree (your tests run `gov close` only inside temporary repositories they build). Never run `gov rebuild --no-embeddings`.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error, stop and return.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-7rr2.md` (read-only): its KPI lines, its `allowed_paths` (`src/gov/close/**`, `tests/unit/close/**`) and its sources.
- `docs/plan/WAVE_2_WBS.md` §0 (rules for every ticket) and the W2-01 and W2-53 cards in §2.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-750, DEC-754, DEC-704, DEC-498, DEC-734 (accepted history: its form and its check against the register), DEC-736 (the ratchet of known reds W2-19 builds), DEC-372 (latency cases), DEC-436 (the merge form), DEC-490, DEC-500, DEC-505, DEC-581, DEC-739, DEC-221, DEC-462, DEC-491. DEC-757 is not in this worktree's register yet; it is given below and is in force.
- W2-01's probe records under `docs/probes/DAEO-g0ip/`, above all `PR-DAEO-g0ip-round-4.md` (findings 1 to 3 and package P-5, the cases this ticket takes over, with the layouts that showed them) and `PR-DAEO-g0ip-split.md`.
- W2-01's acceptance suite `tests/acceptance/W2-01/` and its README: its 88 cases must stay green, and its support module shows how a temporary project is built and how `gov close` is run in it on this worktree's `src/`. You may import or reuse it as W2-01's suite reuses W1-30's (by path, without changing it).
- The public interfaces the ticket works with: `gov close <ticket> --json` (its envelope, `docs/interfaces/API-0002.yaml`), the project's path map `governance/project/path-map.yaml` **of the temporary project** (keys `trailers_base`, `decision_register`, `accepted_history` as W2-01 fixed them), probe records under `docs/probes/<ticket>/` (their frontmatter as W2-01's suite writes them), the decision register's entry form, and commit trailers in the final block. You read no private part of an implementation to learn what a test should expect.

## DEC-757 (owner, 2026-10-17; in force, staged for the owner's commit; item 2 as it concerns this ticket)

W2-53's scope is widened by the owner's P-W2-19 (a), est. 40 -> 160:

1. **The probe gate measures every later merge against git's own merge of its parents** (DEC-754: W2-01's round-4 findings 1 to 3 and P-5 (c)).
2. **An owner-accepted known-red list, as a ratchet.** The path map (`governance/project/path-map.yaml`) key **`accepted_reds`**: a list of entries with **`test`** (the exact test id), **`decision`** (the owner's ACCEPTED decision naming that test id), **`reason`** and **`fixed_by`** (the ticket that fixes it). An entry counts only when the commit that added it carries `Role: owner`. A listed red does not refuse a close; any red not on the list does. A listed test that passes refuses the close, naming the entry, until the entry leaves the list. The list never grows without an owner decision. **Its core (reading, checking and applying the list to a run's results) is one public function: W2-19 reuses it for declared test commands and EXAMIN (DEC-736).**
3. **A ticket-file edit made from the integration side is not the ticket's own change:** a commit carrying `Role: orchestrator` or `Role: owner`, naming the ticket in `Task:` and changing only its ticket file. A change on the ticket's own side after the probe still refuses.
4. **A named load-sensitive quarantine.** The path map key **`load_sensitive`**: entries with `test`, `decision` and `reason`, under the same owner-commit rule. A listed test that fails in the close counts only if it passes in an isolated re-run (alone, in its own process) inside the same close, and the close reports it by name with both results, never silently. A test not on the list is never re-run. An entry may name a test function, covering its parameters.

- **The key names `accepted_reds` and `load_sensitive` and the entry fields (`test`, `decision`, `reason`, `fixed_by`; `test`, `decision`, `reason`) are fixed by DEC-757** and must not change: the owner commits the first entries in the main tree's path map. You settle the other details in your README, as DEC-734 item 3 allowed for accepted history (for example the exact form of a test id, how a decision "names" a test id, which commit "added" an entry, what the close reports). A contested form is a package.
- **The owner's first entries, which your forms must accept as written** (they are not in this worktree; tests build their own path maps in temporary repositories): `accepted_reds` will hold W1-42's `test_retrieval_query_ran_with_bundles_expansions_notes_and_stopping_reason[RETR-X-02]` (fixed by W2-13) and `test_governance_share_is_measured_and_at_most_15_percent_on_each_programme` (fixed by W2-14), both in `tests/acceptance/W1-42/test_w1_42_exit_report.py`; `load_sensitive` will hold three p95 latency cases, each named by its test function: `test_a_call_waits_under_100_ms_p95_for_the_hook` (W1-05), `test_decision_p95_is_under_100_ms` (W1-02) and `test_a_warm_query_answers_within_half_a_second_at_p95` (W1-19). Expect the owner's register entry to name such a test the way this paragraph does: the test's own name (with its parameter where it has one) and its file. State in your README the test-id form you fix, so the owner's entries can be written to it.

## The behaviour to test (the ticket's KPI lines, in full)

Success:
1. After a FULL ticket's probed commit, every later merge that holds it refuses, naming the merge, whatever task it names (or none), when a probed path (the ticket's allowed paths, its acceptance folder, its ticket file) at the merge is not what git's own merge of its parents gives, a removal or a return to a version from before the ticket included; on the integration branch, inward on the ticket's branch, and for an octopus merge [DEC-750, DEC-754].
2. A later merge that takes another ticket's whole version of a probed file is measured the same way, against git's own merge of its parents (P-5 (c)) [DEC-754].
3. A reopened FULL ticket whose earlier round was merged back before its final probe closes when the probed code at the closed head is the final probed code [DEC-754].
4. A merge whose probed paths are what git's own merge of its parents gives, and another ticket's merge holding the probed commit on neither side, pass as before; W2-01's acceptance cases stay green [W2-H047, W2-M202].
5. The accepted-red ratchet (DEC-757 item 2.1). A red whose exact test id the path map's `accepted_reds` lists, with an ACCEPTED owner decision naming it, a reason and the ticket that fixes it, does not refuse the close; the close names it with its decision and fixing ticket. An entry counts only when the commit that added it carries `Role: owner`. Its core is one function W2-19 reuses for declared test commands (DEC-736) [DEC-757].
6. Integration-side ticket edits (DEC-757 item 2.2). A change to the ticket's file after its probed commit, made by a commit carrying `Role: orchestrator` or `Role: owner`, naming the ticket in `Task:` and changing only that file, is not a change to the probed code [DEC-757].
7. The load-sensitive quarantine (DEC-757 item 2.3). A test the path map's `load_sensitive` lists that fails in the close is re-run alone, in its own process, inside the same close; it counts as passed only if that re-run passes, and the close reports it by name with both results [DEC-757, DEC-372].
8. W2-53 closes through `gov close` with its own merged mechanism, its only reds the listed ones [DEC-757]. (This line is shown by the orchestrator's real close after the merge, not by a test in a temporary repository; say so in your README.)

Failure:
1. An acceptance test added on the ticket's branch before the probe and removed or changed by a later merge refuses the close.
2. A merge whose own merge git cannot compute, or cannot read, is judged against the probed code and never passes by default.
3. A red not on `accepted_reds` refuses the close. A listed red that passes refuses the close, naming the entry to remove. An entry added by a commit without `Role: owner`, or whose decision is not an ACCEPTED owner entry naming that test id, is refused, naming the entry; the list never grows without an owner decision [DEC-757].
4. A ticket-file change on the ticket's own side after the probe, or an integration-side commit that changes more than the ticket's file, still refuses [DEC-757].
5. A load-sensitive test that fails its isolated re-run refuses; a test not on `load_sensitive` is never re-run; no re-run is silent [DEC-757].

Cases the lead expects your FULL suite to hold (behaviour, in addition to each line's plain success and failure):
- Round 4's layouts: a later merge holding the probed commit that brings another ticket's branch made before the merge-back, naming that ticket's `Task:` (and one naming no task), and deletes a probed file, sets it back to its text from before the ticket, or removes or changes an acceptance test of the ticket; on the integration branch, inward on the ticket's branch, and as an octopus merge. Each refuses, naming the merge.
- P-5: a later merge that takes another ticket's whole version of a probed file refuses where git's own merge of the parents gives something else, and passes where it gives the same.
- A merge whose parents conflict on a probed path, and a merge git cannot read, are judged against the probed code: never a pass by default.
- Finding 3: a reopened ticket whose first round was merged back before its final probe closes when the closed head's probed code is the final probed code; and it still refuses when the probed code at the closed head differs from the final probed code.
- The accepted-red list: an exact id passes; a near id, another parameter of the same test, or the bare function name for a parameterised red does not cover it; an entry added by a commit whose `Role:` is not `owner` (and a `Role: owner` line that is not in the commit's final trailer block) does not count; an entry whose decision is missing from the register, not ACCEPTED, delegated rather than the owner's, or does not name that test id does not count; an entry whose test now passes refuses, naming the entry; the close names each listed red with its decision and fixing ticket. Settle and test what happens to an entry whose test the close did not run.
- The load-sensitive list: a listed test that fails in the close's run and passes alone counts, and the close reports it by name with both results; a listed test that fails alone too refuses; a test not on the list that fails is not re-run (and refuses unless `accepted_reds` covers it); an entry naming a function covers its parameters; an entry added without `Role: owner` does not count.
- Integration-side ticket edits: an orchestrator's or owner's commit naming the ticket and changing only its ticket file after the probe passes; the same change on the ticket's own side (an implementer's role) refuses; an orchestrator's commit that changes the ticket file and anything else refuses; one that names another task or none does not count as integration-side. Settle in your README what "the ticket's own side" means, from DEC-757 item 3's text, and check that the merges carrying such an edit in (inward, and the merge-back) are judged consistently.
- W2-01's acceptance cases stay green: run `tests/acceptance/W2-01` too and say which of its cases this ticket's KPIs touch. If a KPI line of this ticket requires revising an earlier ticket's acceptance test (W2-01's or any other), name it and return it as a package; do not edit it.

## What you write

- Only inside `tests/acceptance/W2-53/`. No earlier ticket's tests are touched. No throwaway implementation is left in the tree.
- FULL: thorough, every KPI line's success and failure, no combinatorial expansion beyond what a KPI demands (DEC-221).
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need a repository build a temporary one from scratch (pytest's `tmp_path`). Tests that need a test to fail only under load use a deterministic stand-in (for example a test that fails in the close's ordinary run and passes when run alone), never real machine load or timing.
- The KPI makes the ratchet's core one public function that W2-19 reuses. Whether you also test it directly, and so fix its public name, module and contract in your README for W2-19, is yours to settle; if you do, fix it in your README as the interface the implementation must provide.
- A README that maps each KPI line to its tests and gives the expected red reason of each, states the forms you settle (above), and says how the tests run this worktree's `src/` (DEC-732).
- Red first: run `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-53/src python3 -m pytest tests/acceptance/W2-53 -q -p no:cacheprovider -rs` to its end (never `-x`); the tests fail for the reason the README states. Tests of behaviour that already holds (KPI 4's pass cases) may pass now; say which. Also run `tests/acceptance/W2-01` the same way and report its counts.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-53 (DAEO-7rr2): acceptance tests, red" --trailer "Task: DAEO-7rr2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-754" --trailer "Implements: DEC-757" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In the fields, give: your commit's hash; the test count; the KPI lines with their tests; the red reason as you saw it, per test file; the forms you settled (test-id form, decision naming, adding commit, the reports' wording, the ratchet's public interface if you fixed one, the meaning of "the ticket's own side"); the `gov.__file__` line; W2-01's counts; every earlier test you would need revised, as a package.
