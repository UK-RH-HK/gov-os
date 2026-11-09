Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-152-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-152 revision 2 — the independent test designer's brief (DAEO-o5x1)

You are a fresh independent test designer for **W2-152** (`.tickets/DAEO-o5x1.md`: read it, with its "Interface" and
"Clarified" sections). Your predecessor's 56 cases (TESTS-READY `b08ede6890c6`) all pass on the engineer's branch.
The review (round 1) found four gaps the cases did not catch. The CTO adds them as cases now, before the engineer's
fix. Specify them as behaviours from the ticket's lines; nothing here comes from the implementation.

## The cases to add (in `tests/acceptance/W2-152/`, mapped to the KPI line named)
- **S5, every role's template:** the "until <ticket>" refusal (`UNTIL_CLOSED <ticket>`) applies to the role's own
  template too, not only T-0, the lead's run block and `--part`.
  - A fixture where `role-engineer.md` holds "… until W2-901" and W2-901 is closed: refused for
    `gov brief engineer …`.
  - The same for `role-lead.md` with `--run build`, with the line outside the selected run block (in the template's
    common part).
  - A guard: an open W2-901 is not refused.
  - Reason: W2-153 delivers the whole role template as the system prompt, so a stale line there reaches the session
    (R2-12, DEC-1050).
- **S9, the dependency check never off silently:**
  - facts.yaml with no `ready` key: `gov brief` refuses, naming the missing key (any code that names
    `ready.new_since`).
  - A malformed `new_since` (`"soon"`): refused the same way.
  - Also: the schema requires `ready` (a schema case).
- **S8, a ticket with no readable KPI lines is not READY:** `kpis` missing, `kpis` as a list, or an empty `success`
  list are each refused (any code; the detail names `kpis`).
- **S8, unreadable front matter:** an unclosed or invalid YAML block is refused as `TICKET_UNREADABLE` (not as
  `ALLOWED_PATHS_EMPTY`).
- Each new case is red on today's branch head for the right reason. You cannot read the branch, so state the
  expected outcome from the review's description: these four behaviours are absent.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-152-tests`, branch `w2/W2-152-tests`. Write only
  `tests/acceptance/W2-152/`. Update the README's map.
- **Never read the implementation:** never open `/home/usain/gov-os-worktrees/W2-152`, the branch `w2/W2-152` or
  `src/gov/brief/`. Keep every search inside your worktree. Your cases go red on your own tree, where `gov brief` does
  not exist; say which ones are red for the new reason only on the engineer's tree.
- Use planted ids in the `W2-9xx` range, as your predecessor did. Their `gov links` notices are expected; W2-129 S17
  covers them.
- Run only your cases, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not found):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-152-tests/src python3 -m pytest tests/acceptance/W2-152 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`.
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict`
  or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search again
  once (DEC-1092 (1)).
- **Commit** on `w2/W2-152-tests`, only `tests/acceptance/W2-152/`, with
  `--trailer "Task: DAEO-o5x1" --trailer "Implements: DEC-1050, DEC-1083, DEC-1088" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: about 8 to 10 cases.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the new cases, the commit and `TESTS-READY <hash12>`.
