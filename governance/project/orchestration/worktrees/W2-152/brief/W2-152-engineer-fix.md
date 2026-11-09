Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-152 fix round — the engineer's brief (DAEO-o5x1)

You are a fresh engineer for **W2-152** (`.tickets/DAEO-o5x1.md`: read it, with its "Interface" and "Clarified"
sections). `gov brief` is built on `w2/W2-152` (`16d052d2f`). Review round 1 was NOT READY:
`/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/w2-152-r1.md`. Read its
findings F1, F3, F4, F5 and F6. The designer's revision 2 (TESTS-READY `50902d8a422f`, merged by the CTO as
`645fcfd4`) added 11 cases. 10 of them are red on your branch, for exactly these gaps.

## The fixes (only these)
1. **F1 (S5, the blocking one):** the "until <ticket>" check (`UNTIL_CLOSED`) also scans the role's own template,
   for every role, as a whole file, not only the lead's selected block. W2-153 delivers the whole role template as
   the system prompt.
2. **F3 (S9):** a facts.yaml with no `ready` key, or a `new_since` that is not a date, is refused, naming
   `ready.new_since`. The schema lists `ready` as required.
3. **F4 (S8):** `kpis` missing, not a mapping, or with an empty `success` list is refused, the detail naming `kpis`.
4. **F6 (S8):** an unclosed or invalid front-matter block is refused as `TICKET_UNREADABLE`.
5. **F5 (cheap, rides along under DEC-802):** a ticket, facts, `--part` or `--repair` file that is not UTF-8, or
   facts.yaml that is not valid YAML, is a named `GovError` refusal, never a traceback.

Nothing else. F7, F8, F9, F10 and F11 are rows the CTO keeps. Add one unit case per fix in `tests/unit/brief/`.

## Where you work and the rules
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-152`, branch `w2/W2-152`. Your paths: the ticket's
  `allowed_paths`.
- **You never read `tests/acceptance/W2-152/`** (DEC-820 (c)). Run the cases only through
  `python3 -m gov.cli.main accept W2-152 --root /home/usain/gov-os-worktrees/W2-152`, or, if that crashes in the
  sandbox, `python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -rf` with
  `PYTHONUSERBASE=/home/usain/.local`. Read only the result lines. Exclude the folder from every search.
- Also run W2-128's cases (`gov accept W2-128 --root …`), your unit tests and `python3 -m gov.check.schema`. No
  whole-suite run. Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152/src`.
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No
  GPU, model, network, installs or `gov retrieve`. DEC-1080: one simple command per Bash call. Search again once
  (DEC-1092 (1)) if a search does not answer.
- Do not merge. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-152`, only your paths, with
  `--trailer "Task: DAEO-o5x1" --trailer "Implements: DEC-1050, DEC-1083, DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.

## Return
Your final message, in full:
- the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
- per fix, what changed (file and line);
- `gov accept W2-152`'s and `gov accept W2-128`'s counts, the unit tests' counts and the schema check's output.
