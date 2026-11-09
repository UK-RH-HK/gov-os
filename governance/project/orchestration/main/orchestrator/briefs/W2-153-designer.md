# W2-153 — the independent test designer's brief (DAEO-8s85)

You are the independent test designer for **W2-153** (`.tickets/DAEO-8s85.md`): the role template delivered at
launch (W2-128 TPL-4). Profile STANDARD. Read first, in full: the ticket (five KPI lines, two failure lines and **its
body's "Interface"**: the role → template map, where the flag goes, the skills lists, who writes the copies). Then
`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §B ("Delivery") and §D TPL-4, and
`packages/ACT-CLAUDE-COPIES-1.md` (the copies ACT this ticket lands with).

## What the cases must show
- **S1:** for each worker role and for a lead, the argv `gov launch` builds carries
  `--append-system-prompt-file <root>/.claude/templates/<stem>.md`, with the map's stem, after the caller's
  arguments. With the file missing, the launch is refused with `LAUNCH_NO_TEMPLATE` naming the path, and no session
  starts. Test through the launcher's public entry (`gov.launch.launcher.launch` or the CLI) with a stub CLI binary
  and a fixture repository. Never start a real session.
- **S2:** the dispatcher's lead launch form
  (`governance/project/orchestration/tools/dispatch/launch_now.sh`) builds a command with the same flag and
  `role-lead.md`, and refuses when the file is missing. Run it with a stub `claude` early on PATH, or with its own
  test hook if it has one. Read the script on integrate first.
- **S3:** in a fixture repository, a `.rulesync/subagents/<role>.md` that is the role file's front matter, a
  `skills:` list and the role template's body is reported consistent by `gov.adapters.portability`. One that keeps
  the old body, or lacks the `skills:` list, is a finding. Extend the existing portability test fixtures
  (`tests/unit/adapters/`) by one case.
- **S4:** a `.claude/templates/` copy changed or missing is a portability finding. The writer
  `python3 -m gov.adapters.portability --write-templates <dir>` writes the eight files byte for byte.
- **S5:** the ACT's record is the CTO's evidence, not a test here. Say so in the README.
- **F1:** S1's and S2's refusal cases. **F2:** the built argv is otherwise byte-equal to today's (compare with
  integrate's launcher on the same fixture, run as a subprocess from a `git worktree` of `w2/integrate` or a copy at a
  pinned commit).
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`, made from `w2/integrate`
  today. You write only `tests/acceptance/W2-153/`: the cases, the support files, and a README with the map
  `| KPI line | Test (node id) | On integrate | Why |`.
- You may read anything on `w2/integrate` (DEC-963). Never read this ticket's implementation: never open
  `/home/usain/gov-os-worktrees/W2-153` or `w2/W2-153`. Keep every search inside your worktree (DEC-1093 (2)).
- No GPU, model, network or installs. No real Claude session: stub binaries only. Never open `~/gov-os-eval/`,
  `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- Run only your cases:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/W2-153 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`,
  with an empty `HOME` and `PYTHONUSERBASE=/home/usain/.local` if pytest is not found. Then run
  `python3 -m gov.cli.main accept W2-153 --root /home/usain/gov-os-worktrees/W2-153-tests`. If that crashes in the
  sandbox, say so.
- DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search again once (DEC-1092 (1)).
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W2-153/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1052" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Size: about 20 to 30 cases.
- **Return** (your final message, in full):
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - the case list (node id, KPI line, red or green on integrate, why);
  - the commit, `gov accept`'s counts and `TESTS-READY <hash12>`;
  - interface gaps, as `discoveries`.
