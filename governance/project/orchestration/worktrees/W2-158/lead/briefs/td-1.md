# Brief td-1: independent test designer for DAEO-8a3f (W2-158), profile STANDARD, class C2

You are the independent test designer (MR-3) for ticket DAEO-8a3f (W2-158: `gov check --structural`, one cheap,
bounded pass over the declared check families and the new links on a head, a notice and never a refusal). You write
the acceptance tests from the ticket's KPI lines (S1-S5, F1-F4, each with its Verify) and the Interface below (the
ticket's Interface line and the lead's readings L1-L10), before the engineer's code exists. You write to the
Interface; you never change it. A gap or a clash in it comes back as a package (status PACKAGES: question, options with
cost, recommendation, confidence, what it blocks), not as your own invention; a small reading the Interface does not
settle goes into the test's docstring and `unresolved`. You never read the engineer's work on this ticket (branch
w2/W2-158 after this brief; `src/gov/check/structural.py`, any change to `src/gov/check/command.py` beyond your base,
`tests/unit/check/test_w2_158*`, `docs/changes/W2-158-evidence.md`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-158-tests |
| branch | w2/W2-158-tests |
| your allowed paths | tests/acceptance/W2-158/** |
| the ticket (read it first, whole) | /home/usain/gov-os-worktrees/W2-158-tests/.tickets/DAEO-8a3f.md |
| `gov check` at your base (the integrated code, DEC-963) | src/gov/check/command.py, src/gov/cli/checks.py, src/gov/cli/main.py (the command module convention, its docstring) |
| `gov links` (what the links line calls; its output form in its docstring) | src/gov/links/command.py, src/gov/links/check.py |
| how other suites drive `gov` in a child process over a planted git tree (reuse ideas; your files live under tests/acceptance/W2-158/) | tests/acceptance/W2-157/ (its support module and F4 case), tests/acceptance/conftest.py |
| the CTO's reference tool (the same pass, read only; not code to test; where it differs from the Interface, the Interface wins) | /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/structural_pass.py |
| the package the ticket reads | governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md (row D9) |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1052, DEC-1073, DEC-1119, DEC-1109 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The Interface (the ticket's Interface line, plus the lead's readings L1-L10 of what it leaves open)

The ticket's own line: `gov check --structural [<base>] [--timeout <s>]`; the output lines as S2; exit codes as S3.
The declarations are where the ticket says: `template/governance/kernel/checks/<id>.yaml`, else
`governance/kernel/checks/<id>.yaml`. The lead fixed the points below (read from the ticket, the CTO's reference tool
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/structural_pass.py` and the code at
your base) so the test designer and the engineer write to one interface. Both conform to it and change none of it; a
clash with a KPI line comes back as a package (status PACKAGES), not as an invention. Where this reading and the
reference tool differ, this reading wins (the ticket's F3 forbids the reference's built-in commands).

- **L1 The command.** `gov check --structural [<base>] [--timeout <s>] [--root <tree>]`, in `src/gov/check/command.py`
  (the module `gov check` dispatches to; it wins over `src/gov/cli/commands/check.py`). The tree is `--root`, else the
  working directory (every `gov` command's rule). `<base>` is one optional positional argument, any git revision.
  `--timeout` is a number of seconds above 0 (float allowed, e.g. `--timeout 2` or `0.5`), default 50; it is the bound
  of each check and of links alike (a declaration's own `timeout-seconds` is not used by this pass). Usage errors are
  argparse's (exit 2): `--timeout 0`, `--timeout -1` and `--timeout abc`; `--structural` with `--list`; a `<base>`
  given without `--structural`. `gov check --list` and plain `gov check` behave exactly as before.
- **L2 The output.** Plain lines on standard output, in this order, whatever `--json` says: the eight families
  `schema`, `graph`, `claims`, `mutation`, `authority`, `pathmap`, `audit`, `skills`; then `portability`; then
  `links`; then one last line starting `structural pass at <the first 12 characters of HEAD's sha>`. Each family line
  is exactly one of: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)`,
  `<family>: NOTICE <what it found, its first lines>`. A NOTICE's text is on that one line (findings joined with
  ` | `, each shortened; at most three shown, then `(+k more)`). The last line names the families with a NOTICE and
  says it is a notice, not a refusal, or that all ran families are ok; and the time taken. Nothing else on stdout.
- **L3 Which declaration is which family.** By the declaration's `id`: schema `core-schema`, graph `core-graph`,
  claims `core-claims`, mutation `core-mutation`, authority `core-authority`, pathmap `core-pathmap`, audit
  `audit-reproducibility`, portability `adapter-portability`; skills: every declaration whose `family` field is
  exactly `skill regression` (today skill-regression-a, -b1 and -orchestration), each run, the family ok only if all
  are ok. A declaration is looked up in `template/governance/kernel/checks/` first, else `governance/kernel/checks/`,
  read per file (a YAML file that cannot be read, or has no string `command`, makes only its own family a NOTICE
  naming the file; never an exit other than 0). A family with no declaration in the tree reads
  `<family>: skipped (no declaration)` and nothing is run for it. There is no built-in command: only the tree's own
  declared `command` strings are ever run (F3).
- **L4 How a declared command runs.** `shlex.split(command)`; a first word `python3` is replaced by the interpreter
  running `gov` (`sys.executable`); any other first word is looked up on `PATH` as it is. Working directory: the tree;
  environment: the caller's, less every `GIT_*` variable, with `PYTHONPATH=<tree>/src` and `PYTHONDONTWRITEBYTECODE=1`;
  stdin from /dev/null; stdout and stderr captured; each in its own session and process group
  (`start_new_session=True`). All families' commands are started at once (one process each, a thread or a plain Popen
  per command), and each is waited for up to the bound; at the bound its whole process group is killed (SIGKILL), so a
  grandchild it started dies with it. The pass never waits past the bound for any one command.
- **L5 How a result is read.** Exit 0: ok. Exit 2 with stdout a JSON object holding `"not_applicable": true`:
  `ok (not applicable: <its "reason">)`. Killed at the bound: `NOTICE not measured: <id> did not end within <s> s`
  (the family line starts `<family>: NOTICE` and holds `not measured`; never ok, and never a non-zero exit). Any other
  exit: NOTICE with what it found: the `message` of each item of a JSON list or of a JSON object's `findings` list on
  stdout, else `<id> exit <code>: <the first line of stdout, else of stderr>`. A command that cannot be started (no
  such program): NOTICE `<id> could not run: <why>`.
- **L6 Portability (needs a `<base>`).** With a `<base>`: it runs (as L3-L5) when `git diff --name-only <base>..HEAD`
  lists a path under `template/governance/kernel/roles/`, `template/governance/kernel/skills/`,
  `template/governance/kernel/hooks/` or `.rulesync/`, or when `<base>` does not resolve to a commit; otherwise
  `portability: skipped (no such change)`. It starts with the eight others. Without a `<base>`:
  `portability: skipped (no base given)`.
- **L7 Links (needs a `<base>`).** With a `<base>` and a folder `<tree>/src/gov/links/`: after the others have ended,
  the tree's own `python3 -m gov.cli.main links --since <base>` runs as L4 (the tree's `src` on `PYTHONPATH`), within
  the bound. Its first stdout line is `gov links: N new since <rev>, M standing...`; exit 0 or 1 is a reading. N = 0:
  `links: ok (0 new since <base>, M standing)`; N > 0: `links: NOTICE N new: <the next stdout lines, the first
  findings>`. Killed at the bound: `links: NOTICE not measured: ...`; any other exit or a first line of another form:
  `links: NOTICE gov links could not run (exit <code>): <its last line>`. No such folder:
  `links: skipped (no gov links in this tree)`. Without a `<base>`: `links: skipped (no base given)`. It writes only
  what `gov links` itself writes (its mark, `.gov-runtime/links/mark`).
- **L8 Exit codes.** 0 whenever the pass ran, whatever any check or links found or however they ended. 2 only when it
  could not run at all: the tree is no folder, it is not the top of a git work tree (`git rev-parse --show-toplevel`
  is not the tree itself), it has no HEAD commit, or a usage error (L1); the reason on standard error as
  `gov check: structural pass could not run: <why>`, nothing on stdout but what was already printed. The module
  declares `CHILD_EXIT_CODE = True` and `run` returns the int 0 or 2 under `--structural` (the command line's
  convention in `src/gov/cli/main.py`: `gov` then ends with that code and prints no envelope); `run` returns its
  dict, as today, otherwise. `EXIT_CODES` keeps its `{3: "checks failed"}` for the plain `gov check`.
- **L9 Nothing else.** The pass itself writes no file: no log, no cache, no `__pycache__` in the tree
  (`PYTHONDONTWRITEBYTECODE=1` for the children), and its git reads take no optional lock
  (`git --no-optional-locks ...` or `GIT_OPTIONAL_LOCKS=0`), so the index is not rewritten. The only writes are those
  of the declared commands themselves and of links' mark. No commit, close, landing or launch code calls it to decide
  anything; `src/gov/close/`, `src/gov/launch/` and `src/gov/queue/` (where they exist) do not import or call it.
- **L10 Where the code lives.** `src/gov/check/structural.py` holds the pass (a function such as
  `run_structural(tree, base, timeout, out) -> int`); `src/gov/check/command.py` gains only the arguments and the
  dispatch. No other product file changes.

## Rules
- One test (or more) per KPI line S1-S5 and F1-F4, each doing what its Verify says, read with the Interface items it
  names. Name each after its id (`test_s1_...`, `test_f3_...`).
- Plant everything under pytest's `tmp_path`: a git tree (`git init`, a commit; GIT_CONFIG_GLOBAL=/dev/null,
  GIT_CONFIG_NOSYSTEM=1, a planted HOME) holding `template/governance/kernel/checks/<id>.yaml` declarations (the five
  fields id, family, tier, severity, command) whose commands are small stand-in scripts in the planted tree (e.g.
  `python3 checks/marker.py schema ok`), each recording that it ran (its pid, start and end times) in a file of its
  own and then passing, finding a problem (non-zero exit and a JSON findings list or a first line), answering not
  applicable (exit 2 and `{"not_applicable": true, "reason": "..."}`) or sleeping past the bound. Never this
  repository's tickets, checks or declarations as the subject (the ticket's acceptance_tests line); S5's timing case
  alone runs on this tree (below).
- Reach the code as its callers do: `python3 -m gov.cli.main check --structural [<base>] [--timeout <s>] --root
  <planted tree>` in a child process, with THIS tree's `src/` first on `PYTHONPATH` (fail the run if `gov` would import
  from elsewhere), judged by exit code and stdout lines (standard error for the could-not-run reason). Never import
  `gov.check.structural` at collection, so the suite runs red by failing, not by erroring at import. Use a small
  `--timeout` (1-3 s) in planted cases so each takes seconds; bound every wait (a timeout on the child), never a bare
  sleep. Allow for a loaded machine: assert "within bound + a few seconds", never tight timings.
- S1: eight families each declared with a marker: eight marker records, one line per family, in L2's order; the
  markers overlap in time (each sleeps e.g. 1 s; the whole run well under eight times that), each its own pid; a
  stand-in that sleeps far past the bound (and one that starts a grandchild that sleeps) is killed at the bound: the
  run ends within bound + slack and the (grand)child pid is gone afterwards; `--timeout` changes the bound.
- S2: passing, finding, not-applicable and timing-out planted checks, each family's line as L2/L5 states; the timed-out
  family's line starts `<family>: NOTICE` and contains `not measured`; a family with no declaration reads
  `skipped (no declaration)`; the last line starts `structural pass at <head12>` (the planted HEAD's first 12).
- S3/F1: a failing planted check gives exit 0 and a NOTICE line; `--root` a folder that is no git work tree, and a
  path that does not exist, each give exit 2 (reason on stderr); `--timeout 0` and `--timeout abc` exit 2; a static
  search of `src/gov/close`, `src/gov/launch` and `src/gov/queue` (each where it exists) finds no import or call of
  `structural` / `gov.check.structural` / `--structural`.
- S4: planted history: a `<base>` commit, then a commit touching `template/governance/kernel/skills/x/SKILL.md` (the
  portability marker runs), and one touching only another path (`portability: skipped (no such change)`); a `<base>`
  that does not resolve (the marker runs); no `<base>`: `portability: skipped (no base given)` and
  `links: skipped (no base given)`. Links: a planted tree with a stand-in `src/gov/__init__.py`,
  `src/gov/cli/__init__.py`, `src/gov/cli/main.py` and `src/gov/links/__init__.py` (the tree's own `gov links`,
  answering `gov links: 0 new since <base>, 4 standing` exit 0, or `gov links: 2 new since <base>, 4 standing` plus two
  finding lines exit 1, and writing `.gov-runtime/links/mark`): `links: ok (0 new since <base>, 4 standing)` and a line
  starting `links: NOTICE 2 new` holding the first finding line; it ran after the eight families had ended (its start
  after their markers' ends); without `src/gov/links/`: `links: skipped (no gov links in this tree)`.
- S5: a filesystem spy over a planted tree: snapshot every file (path, size, mtime_ns) under the planted tree's work
  files (you may leave `.git/` out) and the planted HOME before and after a run with a base and links; only the
  markers' own records and `.gov-runtime/links/mark` are new or changed. The timing case on this tree: `gov check
  --structural HEAD~1` with `--root` this repository's tree (ROOT, the tree the suite sits in), default bound, ends
  within 60 s and exits 0; name this test with `real` (e.g. `test_s5_real_pass_on_this_tree_is_bounded`) so the
  whole-folder filter leaves it out and `gov accept` runs it.
- F2: S1's sleeper and S2's timed-out check: the line is a NOTICE holding "not measured", never ok; exit 0.
- F3: a planted tree whose `core-schema` declaration holds a marker command: the marker runs, and no command of a
  built-in list does (plant `src/gov/__init__.py`, `src/gov/check/__init__.py` and `src/gov/check/schema.py`, graph.py
  and so on in the planted tree, each recording if run, i.e. what the reference tool's built-in
  `python3 -m gov.check.<module>` would start, and assert none ran); a planted tree with no declaration for a family reads it as
  `skipped (no declaration)`; a declaration in `governance/kernel/checks/` alone is used when the template layout has
  none, and the template layout's wins when both hold one.
- F4: `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only paths matched by the ticket's
  `allowed_paths`, `tests/acceptance/W2-158/` or `docs/probes/DAEO-8a3f/`. It judges only this ticket's own branch:
  when the current branch (`git rev-parse --abbrev-ref HEAD`) is neither `w2/W2-158` nor `w2/W2-158-tests`, it skips,
  naming why (DECIDED-NOT-DONE row 171: otherwise the next ticket in the area and the merge queue's batches go red on
  it). Say so in its docstring.
- Tests are red now (no `--structural` yet). Run them and say which are red and why; anything green now is a fault in
  the test unless it guards "nothing else happens", the static search, or a refusal argparse already gives.
- No test named with `real`, `green_here` or `time_limit` unless it must be skipped by that filter. The whole folder in
  well under two minutes.
- Every pytest run goes through the heavy-job slot, with TMPDIR outside the repository and outside ~/gov-os-runs:
  `env HOME=/home/usain/gov-os-worktrees/W2-158-tests/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-158-td
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-158-tests/src
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest
  tests/acceptance/W2-158 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"` (make /tmp/w2-158-td and the empty home first; put the line in a
  script file under your scratch and run it with `bash <file>`).
- Add `tests/acceptance/W2-158/README.md`: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-158-tests/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-8a3f" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1052, DEC-1073, DEC-1119, DEC-1109, DAEO-q7lk, DAEO-neam" -- tests/acceptance/W2-158`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context packet (`gov context DAEO-8a3f --role independent-test-designer --budget 12000`)
{
  "ticket": "DAEO-8a3f",
  "ticket_text": "---\nid: DAEO-8a3f\nstatus: in_progress\ndeps: []\nlinks: [DAEO-neam, DAEO-q7lk]\ncreated: 2026-11-11T01:20:17Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-158\ntags: [wave-2, implementation, standard, after-the-lift, check]\nwbs_id: W2-158\ntitle: 'gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/check/structural.py\n- src/gov/check/command.py  # the one option, --structural\n- tests/unit/check/test_w2_158*\n- docs/changes/W2-158-evidence.md\nreads:\n- src/gov/check/**\n- src/gov/cli/checks.py\n- src/gov/links/**\n- governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md\nneeds:\n- src/gov/check/command.py\nwaits_on:\n- ref: DAEO-q7lk\n  reason: 'the links line of S4 calls `gov links --since <base>` (W2-129); this ticket skips that line while `gov links` is absent'\nkpis:\n  success:\n  - 'S1 `gov check --structural` runs, each in a process of its own, all at once and each within a time bound (default 50 seconds, `--timeout` to change it), the tree''s declared checks of these families: schema, graph, claims, mutation, authority, pathmap, audit and skills; each command is the tree''s own declaration (template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml). Verify: a planted tree with a declaration per family: eight processes started, one line per family; a stand-in command that sleeps past the bound is killed at the bound [DEC-1052, INVESTIGATION-1 T-2]'\n  - 'S2 It prints one line per family: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)` or `<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`; a family that timed out is a NOTICE reading \"not measured\", never ok and never red. Verify: planted checks that pass, find a problem, are not applicable and time out: each reads as stated [DEC-1052, INVESTIGATION-1 T-2]'\n  - 'S3 It exits 0 whatever the checks find, and 2 only when it could not run at all (no such folder, not a git work tree, bad arguments); no commit, close, landing or launch refuses or waits on its result (a landing may call it after the fact and log its lines, as the CTO''s `land.py` does). Verify: a planted failing check gives exit 0 and a NOTICE; a folder that is no work tree gives exit 2; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal [DEC-1052, DEC-1073]'\n  - 'S4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree''s own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links'' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]'\n  - 'S5 It is bounded and cheap: the whole pass on this repository''s main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks'' own outputs and links'' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]'\n  failure:\n  - 'A refusal, a non-zero exit or a blocked commit, close, landing or launch because of what it found. Verify: S3''s planted failing check: exit 0 and a NOTICE line; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal'\n  - 'A family that timed out reading ok or red. Verify: S1''s stand-in command that sleeps past the bound and S2''s timed-out planted check: the family''s line reads NOTICE \"not measured\"; a line reading ok, or a red result, is this failure'\n  - 'A check run that is not the tree''s own declaration. Verify: a planted tree whose declaration for one family holds a marker command: the marker runs and no command from a built-in list does; a planted tree with no declaration for a family reads that family as skipped'\n  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'\nprofile: STANDARD\nsources:\n- DEC-1052\n- DEC-1073\n- DEC-1119\n- DEC-1109\n- DAEO-q7lk  # W2-129\n- DAEO-neam  # W2-45\nest_loc: 200\nacceptance_tests:\n  path: tests/acceptance/W2-158/\n  author: 'independent-test-designer (MR-3), from these KPI lines; planted trees with declared checks and planted histories, never this repository''s tickets'\ntrack: C\nlist_rows: []\n---\n# W2-158 gov check --structural\n\nFiled by the product-spec helper of the night audit (DAEO-sdxk's anti-drift audit (d), 2026-11-11) on EMERGENCY-TOOLS-1 row D9; **after the lift**, not before EXAMIN's copy (\u00a71 D9 \"no\").\n\n- **Problem.** The CTO's `structural_pass.py` (`.gov-runtime/scratch/orchestrator/tools/structural_pass.py`, R1-21, DEC-1052) gives a cheap notice-only pass over the check families after every record commit and every landing. Its own docstring says \"later replaced by T-2's `--families`\", but no ticket holds T-2's scoped check: W2-45 (runner semantics) lists no scoped or notice-only run, and `gov check` has only `--list`. An adopted product has the 17 families and no cheap way to run them after a commit.\n- **Approach.** A module that reads the declarations the runner already reads, starts each in its own process with a bound, and prints the notice lines. It reuses the declarations; it adds no check. Alternatives: `gov check --changed <base>` with input globs per check (INVESTIGATION-1 T-2's full design, left to W2-45 or a later ticket); a wrapper script in the template (rejected: scratch tools are the problem this audit names).\n- **Interface.** `gov check --structural [<base>] [--timeout <s>]`; the output lines as S2; exit codes as S3.\n- **Non-goals.** No new check, no scoping by input globs, no gate; W2-45's runner semantics are untouched.\n- **Rabbit holes.** Making a notice a refusal (never, DEC-1052); running the checks in sequence (one process each, all at once, is the measured speed).\n\n[DEC-1052, DEC-1073, DEC-1119 (5)]\n",
  "authority": [
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "reason": "declared in sources",
      "tokens": 3919
    },
    {
      "id": "DAEO-neam",
      "sha256": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "authority": "task",
      "lifecycle": "open",
      "constraint": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "reason": "declared in sources",
      "tokens": 812
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1052",
      "sha256": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "adfcc8f9fe4a5f99cf528155317cd036a40191733165299df39b2e229982491b",
      "reason": "declared in sources",
      "tokens": 1859
    },
    {
      "id": "DEC-1073",
      "sha256": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c35a4272874e4ccfb5fe307885c0fb94f9880677de63ca13352d31c0ec1d6852",
      "reason": "declared in sources",
      "tokens": 1047
    },
    {
      "id": "DEC-1119",
      "sha256": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1dfff067b5f5479ac70a03c5d6a27ebd78e1bb0a66258b29b384f953854e74f7",
      "reason": "declared in sources",
      "tokens": 723
    },
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DAEO-q7lk",
      "sha256": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "authority": "task",
      "lifecycle": "in_progress",
      "constraint": "eb060f56f9d6d6c6bd056410e9418af1f5a8d838e93608169ecdbadfa246ff13",
      "reason": "declared in sources",
      "tokens": 3919
    },
    {
      "id": "DAEO-neam",
      "sha256": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "authority": "task",
      "lifecycle": "open",
      "constraint": "16b1548bb946dd5f476690e128718e9d7879592dba0d4855a1dd5c5287a412f2",
      "reason": "declared in sources",
      "tokens": 812
    }
  ],
  "supplementary": [
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md",
      "text": "  - 'S4 The helper watch reads names, timestamps and error codes only, never a message''s text; it matches no process by name; it writes only the inbox, its own state file and its own log; only transcripts whose last entry is inside a window (default 24 hours) are looked at. Verify: a filesystem-spy and a text-canary test: a planted message text never appears in an item or the log; a search of the module for a process-name match finds none [DEC-1112 (3), DEC-1073 (4), DEC-495]'\n  failure:\n  - 'A wait that outlives its bound, or that waits for a job whose process is gone. Verify: S1''s never-written exit file at `<max-s>` 1 returns exit 124 within the bound, and S2''s killed stand-in job returns exit 125 within one poll period with a same-name process still running'\n  - 'A process matched by name, or a message''s text copied into an item or a log. Verify: S4''s text-canary test (the planted message text found 0 times in items and log) and its search of the module for a process-name match (none found)'\n",
      "tokens": 254
    },
    {
      "id": "DAEO-o5x1",
      "path": ".tickets/DAEO-o5x1.md",
      "text": "  - 'S9 Dependency fields (DEC-1088 (3)): a ticket created on or after facts.yaml ready.new_since without reads:, needs: or waits_on: is refused by name (READS_MISSING, NEEDS_MISSING, WAITS_ON_MISSING; an empty list is a declared none); each waits_on id or record path must exist (WAITS_ON_UNKNOWN <ref>); a ticket created before the date is not refused for them. Verify: the ready check on planted tickets either side of the date [DEC-1088, DEC-1052]'\n  - 'S10 facts.yaml gains ready.new_since (an ISO date, the day this ticket lands) and the schema declares it; W2-128''s acceptance cases still pass. Verify: the schema test and gov accept W2-128 [DEC-1050]'\n  failure:\n  - 'Two runs of gov brief on the same inputs differ (TPL-3 F1).'\n  - 'The ready check refuses a ticket for an advisory item, or lets a ticket missing a required field through as READY (TPL-5 F1, as DEC-1083 amends it).'\n  - 'gov brief writes any file, or reads anything beyond the ticket file, facts.yaml, the kernel templates and the --part/--repair files (a filesystem-spy test).'\nprofile: STANDARD\nsources:\n- DEC-1050\n- DEC-1052\n- DEC-1083\n- DEC-1088\n- DEC-1112\n- DEC-1109\nest_loc: 380\nacceptance_tests:\n",
      "tokens": 295
    },
    {
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md",
      "text": "  - 'S4 Only the named groups are touched: nothing is matched by name, a name that is not a process group id above 1 refuses to start (exit 2), and a group already ended is skipped and named. A trip writes one inbox item naming the reason, the groups paused and how to resume (`kill -CONT -- -<pgid>`) or stop them, then the watch ends; when every named group has ended on its own, the watch logs it and ends. Verify: a stand-in with an unrelated process of the same name left running after a trip; a refused argument \"abc\"; a job that ends first [DEC-1067 (GPU safety), DEC-1068 (4), DEC-1073]'\n  - 'S5 It changes nothing else: it only reads the GPU, the servers'' answers and their logs, and writes its own log and the one inbox item. Verify: a filesystem-spy test over a run with no trip: only its log is written [DEC-1068 (4)]'\n  failure:\n  - 'A process outside the named groups paused or signalled. Verify: S4''s planted unrelated process of the same name, left running after a trip: its state is still running and it received no signal; any stop of it is this failure'\n",
      "tokens": 269
    },
    {
      "id": "1bb7395b046294dd36c9248b",
      "path": "governance/project/orchestration/START-NEXT-SESSION.md",
      "text": "  412a4e37 started it, its pid and log are in CHECKPOINT's RESUME HERE. Run: `governance/project/orchestration/nightly/nightly.sh`\n  (day mode, a fresh clone of the head, ~5 h), then the `lifted` suite once, report-only (D4-LIST \u00a72). **No commits on\n  w2/integrate during it.** Then: **triage the reds by group for the owner** (re-run each alone; P1-NIGHTLY-2026-11-02\n  as the old map); fixes by role under RUBRIC-2; a second run.\n- **Done today (11-10 afternoon):** ACT-W2-149-INSTALL-1 `baac0b2c2` (by hand); ACT-DEADMAN-WAKE-1 `905b82a3b`,\n  ACT-CLAUDE-COPIES-3 `a4e703580` (agent); the portability family 204/0; W1-08 merged `34b7815f9`; the ticket template\n  1.0.1 approved (DEC-1121, DEC-1122) and merged; DEC-1119's rubric found then replaced by RUBRIC-2; EMERGENCY-TOOLS-1.\n- **In flight at handover:** ACT-PATHMAP-NS-2 by the owner's operator (fixes `core-pathmap`: the install left\n  `governance/project/indep-briefs/**` without a namespace); ACT-EFFORT-HIGH-2 queued for the agent at 17:33 (the owner's yes just before).\n  Check both landed (`git log`, `~/gov-os-operator/log/operator.jsonl`); landing check after each.\n",
      "tokens": 283
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md",
      "text": "---\nid: DAEO-6lid\nstatus: in_progress\ndeps: []\nlinks: [DAEO-cb2b, DAEO-fd0p]\ncreated: 2026-11-11T01:20:18Z\ntype: task\npriority: 3\nassignee: engineer\nexternal-ref: W2-159\ntags: [wave-2, implementation, standard, after-the-lift, orchestration, hooks]\nwbs_id: W2-159\ntitle: 'The orchestrator''s two Stop checks in the product: a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains, each a reminder blocking at most once a turn (EMERGENCY-TOOLS-1 A8, A9; DEC-1027 E, DEC-1110 (1))'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on: []\nallowed_paths:\n- src/gov/session_watch/**\n- src/gov/check/commands.py  # the one line that records `session-watch` (the precedent: W2-20's `resources`)\n- src/gov/cli/main.py  # P-W2-159-1 (a): a hyphenated command maps to its underscore folder (about 4 lines; the CTO, 2026-11-12 08:22)\n- tests/unit/session_watch/**\n- docs/changes/W2-159-evidence.md\nreads:\n- src/gov/dispatch/**\n- src/gov/plan/**\n- governance/project/orchestration/tools/stop_waiter_check.py\n- governance/project/orchestration/tools/stop_idle_check.py\nneeds:\n- src/gov/check/commands.py\nwaits_on:\n- ref: DAEO-cb2b\n",
      "tokens": 294
    }
  ],
  "supplementary_query": "gov check --structural: one cheap, bounded pass over the declared check families and the new links on a head, a notice and never a refusal (EMERGENCY-TOOLS-1 D9; DEC-1052 R1-21, INVESTIGATION-1 T-2)\nS1 `gov check --structural` runs, each in a process of its own, all at once and each within a time bound (default 50 seconds, `--timeout` to change it), the tree's declared checks of these families: schema, graph, claims, mutation, authority, pathmap, audit and skills; each command is the tree's own declaration (template/governance/kernel/checks/<id>.yaml, else governance/kernel/checks/<id>.yaml). Verify: a planted tree with a declaration per family: eight processes started, one line per family; a stand-in command that sleeps past the bound is killed at the bound [DEC-1052, INVESTIGATION-1 T-2]\nS2 It prints one line per family: `<family>: ok`, `<family>: ok (not applicable: <reason>)`, `<family>: skipped (<reason>)` or `<family>: NOTICE <what it found, its first lines>`, then one last line `structural pass at <head12> ...`; a family that timed out is a NOTICE reading \"not measured\", never ok and never red. Verify: planted checks that pass, find a problem, are not applicable and time out: each reads as stated [DEC-1052, INVESTIGATION-1 T-2]\nS3 It exits 0 whatever the checks find, and 2 only when it could not run at all (no such folder, not a git work tree, bad arguments); no commit, close, landing or launch refuses or waits on its result (a landing may call it after the fact and log its lines, as the CTO's `land.py` does). Verify: a planted failing check gives exit 0 and a NOTICE; a folder that is no work tree gives exit 2; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal [DEC-1052, DEC-1073]\nS4 With a `<base>`: the portability family runs only when `<base>..HEAD` touches template/governance/kernel/{roles,skills,hooks}/** or .rulesync/**, or when `<base>` does not resolve (otherwise it reads \"skipped (no such change)\"), and the tree's own `gov links --since <base>` runs after the others, as `links: ok (0 new since <base>, M standing)` or `links: NOTICE N new: <the first finding lines>`; it writes only links' own mark. Without a `<base>` both are left out, named. Verify: planted history with and without a kernel change; a planted tree with and without `src/gov/links/` [DEC-1052, DEC-1073]\nS5 It is bounded and cheap: the whole pass on this repository's main tree ends within the time bound plus 10 seconds, and it reads and writes nothing else (a filesystem-spy test over a planted tree: only the declared checks' own outputs and links' mark). Verify: the measured time on this repository, recorded in docs/changes/W2-158-evidence.md [DEC-1052]\nA refusal, a non-zero exit or a blocked commit, close, landing or launch because of what it found. Verify: S3's planted failing check: exit 0 and a NOTICE line; a search of src/gov/close, src/gov/launch and src/gov/queue finds no call of it whose result decides a refusal\nA family that timed out reading ok or red. Verify: S1's stand-in command that sleeps past the bound and S2's timed-out planted check: the family's line reads NOTICE \"not measured\"; a line reading ok, or a red result, is this failure\nA check run that is not the tree's own declaration. Verify: a planted tree whose declaration for one family holds a marker command: the marker runs and no command from a built-in list does; a planted tree with no declaration for a family reads that family as skipped\nAny change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists only paths matched by the ticket's allowed_paths",
  "further_batch": [
    {
      "id": "DAEO-fd0p",
      "path": ".tickets/DAEO-fd0p.md"
    },
    {
      "id": "DAEO-ozyt",
      "path": ".tickets/DAEO-ozyt.md"
    },
    {
      "id": "DAEO-ylsh",
      "path": ".tickets/DAEO-ylsh.md"
    },
    {
      "id": "DAEO-6lid",
      "path": ".tickets/DAEO-6lid.md"
    },
    {
      "id": "5ee67db475a7425d3597b0a2",
      "path": "governance/project/orchestration/START-NEXT-SESSION.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-o5x1",
          "path": ".tickets/DAEO-o5x1.md"
        },
        {
          "id": "DAEO-ozyt",
          "path": ".tickets/DAEO-ozyt.md"
        },
        {
          "id": "1bb7395b046294dd36c9248b",
          "path": "governance/project/orchestration/START-NEXT-SESSION.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "DAEO-fd0p",
          "path": ".tickets/DAEO-fd0p.md"
        },
        {
          "id": "DAEO-ozyt",
          "path": ".tickets/DAEO-ozyt.md"
        },
        {
          "id": "DAEO-ylsh",
          "path": ".tickets/DAEO-ylsh.md"
        },
        {
          "id": "DAEO-6lid",
          "path": ".tickets/DAEO-6lid.md"
        },
        {
          "id": "5ee67db475a7425d3597b0a2",
          "path": "governance/project/orchestration/START-NEXT-SESSION.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "5ee67db475a7425d3597b0a2",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-6lid",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-fd0p",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ozyt",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-ylsh",
      "reason": "budget exceeded"
    },
    {
      "id": "role_filter",
      "reason": "withheld from independent-test-designer (ticket DAEO-8a3f): 0 paths, 0 chunks; none matched (DEC-1065 (2))"
    }
  ],
  "tokens": 11858,
  "budget": {
    "limit": 12000,
    "used": 11858
  },
  "left_out": {
    "count": 8,
    "superseded": [
      "DEC-038",
      "DEC-045",
      "DEC-047",
      "DEC-048",
      "DEC-049",
      "DEC-636",
      "DEC-875",
      "DEC-876"
    ],
    "done": []
  },
  "hash": "2b983f0d3cb304c04ce6793f2d90aede9456064da6b35e31af71582378f5c6ca"
}
