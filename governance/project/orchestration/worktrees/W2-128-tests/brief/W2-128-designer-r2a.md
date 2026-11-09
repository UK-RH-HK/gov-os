Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 2a — the independent test designer's brief (DAEO-t8mp)

You are a fresh independent test designer for **W2-128** (`.tickets/DAEO-t8mp.md`). Round 1 (the templates) is merged.
Round 2a is text: read the ticket's body, **"Round 2a"**, in full, then its TPL-6 KPI line (S11) and the review
`governance/project/orchestration/reviews/w2-128-r1.md` (findings F6 and F7). Sources: DEC-963 (the test designer
reads the integrated code on `w2/integrate`), DEC-820 (reads are open but for secrets, the held-out material's
contents, the counterpart's work and the hidden half), DEC-508 and DEC-525 (changed by DEC-820), DEC-1050, DEC-1052.

## What the cases must show (append to `tests/acceptance/W2-128/`; map them to `S11` in the README)
- **TPL-6 S3:**
  - `template/governance/kernel/skills/test-design/SKILL.md`'s read rule permits reading the integrated code on
    `w2/integrate` and forbids this ticket's implementation (DEC-963); it no longer forbids `src/` outright;
  - `skills/orchestration/SKILL.md`'s "Briefs" part points to the kernel templates (`template/governance/kernel/templates/`
    or the role templates by name) and no longer says briefs state each step in full or carry the standing sentences
    word for word;
  - K-4's two lines: the skill no longer forbids a glob or listing over the governance folder (DEC-508 as DEC-820
    changed it), nor reading the settings file (DEC-525's settings half), while it still forbids reading the held-out
    material's contents.
- **Review F6:** `template/governance/kernel/roles/orchestrator.md` no longer sends briefs to the retired
  `brief-*.md` texts as their content (today's line 39).
- **TPL-6 S4's kernel half:** JUDGEMENT's rules (the `Ordinary work:` and `Consequence:` lines) appear in T-6
  (`role-reviewer.md`) and in no other kernel template.
- **The checkpoint example:** `templates/checkpoint.md` holds no `DAEO-0000`, and `gov links` on a record planted from
  it gives no `UNKNOWN_ID` (extend round 1's planted-record case if that is simpler).
- **The template's rulesync skill copies:** each `template/.rulesync/skills/<s>/SKILL.md` is byte-equal to
  `template/governance/kernel/skills/<s>/SKILL.md` for discovery, retrieval, orchestration and test-design.
- **Versions:** the orchestration and test-design skills' `version` is one minor above integrate's (read integrate's
  with `git show w2/integrate:<path>` at test time), and the skills validator passes on both
  (`python3 -m gov.check.skill_validator --both-layouts <skill folder>`).
- **Guards:** nothing else in the two skills changes beyond the named parts and the version (compare section by section
  with integrate's text; allow changes only in the read-restriction section, the briefs part and the two K-4 lines).
- Say for each case whether it is red on integrate for the right reason, or a green guard. Round 1's 92 cases stay as
  they are.

## Where you work
- Your worktree `/home/usain/gov-os-worktrees/W2-128-tests`, branch `w2/W2-128-tests`, with integrate merged by the CTO
  (it holds the ticket's round 2a text). You write only `tests/acceptance/W2-128/`.
- **Never read this ticket's implementation:** never open `/home/usain/gov-os-worktrees/W2-128` or `w2/W2-128`; keep
  every search inside your worktree (DEC-1093 (2)). You may read integrate's text and code (DEC-963).
- Run only W2-128's cases: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tests/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`
  with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not found), then
  `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128-tests` (if it crashes in the
  sandbox, say so).
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU,
  model, network or installs. DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search again once
  (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128-tests`, only `tests/acceptance/W2-128/`, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-963, DEC-1050, DEC-1052" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Size: about 10 to 15 cases.

## Return
Your final message, in full: the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the new
cases (node id, red or green on integrate, why), the run's counts, `gov accept`'s counts, `TESTS-READY <hash12>`.
