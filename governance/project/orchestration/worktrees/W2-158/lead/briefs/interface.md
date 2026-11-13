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
