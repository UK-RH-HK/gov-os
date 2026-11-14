# W2-153 — narrow independent check of the routed line's new cases, the independent auditor's brief (DAEO-8s85)

You are a fresh, read-only independent auditor working under **W2-153** (`.tickets/DAEO-8s85.md`, read-only at
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-8s85.md`). This is a **narrow** check (DEC-1154 form):
only the new cases for the ticket's sixth success line, routed from W2-33 (DEC-1156 (3)). S1 to S5 and both failure
lines were reviewed and merged earlier; they are out of scope.

**The line (success 6, `S6`):** the generated role copies carry each kernel role file's `Launch default`,
`Launch by criticality` and `Skills` lines unchanged, and a hand edit to a generated role copy is named as drifted by
the generation check. Verify: after the copies ACT, each generated role copy holds those lines byte-equal to its
kernel role file; a planted hand edit in one copy is named as drifted [DEC-315, DEC-957, DEC-1156 (3)].
W2-33's ticket (`.tickets/DAEO-lrre.md`, its F1 and the "Clauses judged elsewhere" paragraph) states where the
clause came from: F1's "one edited by hand in the generated folder (the generation check names it as drifted)".

## Head to probe
`0ffe7196e1e2cfc64f9e5da8fef0a438c2e6a80d` on `w2/W2-153`, in `/home/usain/gov-os-worktrees/W2-153` (read it; write
nothing there). Since the branch's last integrate merge (`9afc9e44d`) its only changes are
`tests/acceptance/W2-153/test_w2_153_routed.py` (new) and `tests/acceptance/W2-153/README.md` (the "Routed line"
section, mapped to `S6`). The code under check is integrate's `src/gov/adapters/portability.py` (the generation
check) and the committed copies (`.claude/agents/*.md`, `.rulesync/subagents/*.md`,
`template/.rulesync/subagents/*.md`) against `template/governance/kernel/roles/*.md`.

## What the lead saw (verify, do not take on trust)
- `gov accept W2-153` on this head: pass; `success-6` 71 passed, 0 failed, 18 skipped (the 18: six role files carry no
  `Launch by criticality` line, times three folders); nothing unmapped.
- The test designer reported planted breaks: a `Launch default` line changed in `template/.rulesync/subagents/engineer.md`
  failed exactly that case; the check's generated-file comparison disabled failed the three `generated-agent` drift
  cases; its source comparison disabled failed the three `composed-source` drift cases.
- The designer's discovery: the check compares `.rulesync/subagents/` with `compose()` and `.claude/agents/` with
  rulesync's output, but does not compare `template/.rulesync/subagents/`; a hand edit there is not named. Triage it
  against the line's scope (in or out, ordinary work, consequence) in your verdict.

## Questions
1. Do the cases verify both clauses of S6 as written (byte-equal lines in every generated role copy; a planted hand
   edit in a generated copy named as drifted by the generation check)? Any silent narrowing (a skip, a filter, a
   parametrize that drops a role or folder)?
2. Can each case fail? Plant your own break where you can, only in copies under your own `$TMPDIR` (e.g. `git
   worktree`-free: `git archive 0ffe7196e1e2 | tar -x -C <your $TMPDIR>/tree`), never in the repository's files.
3. Is the README's map right for `gov accept` (`src/gov/accept/runner.py`, `parse_map`)?

## Rules
- Read-only: you have Bash, Read, Grep, Glob only. `git status --short` in `/home/usain/gov-os-worktrees/W2-153` must be
  empty before and after. Write only under your sandbox's `$TMPDIR`.
- Pytest, if you run it, in this form with a copy's own `src` or the tree's:
  `env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <tree>/tests/acceptance/W2-153/test_w2_153_routed.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short`
  in the foreground (the slot may queue; wait in the same call, Bash timeout 600000 ms). Never run anything in the
  background or end your session while a command runs. If pytest writes `.pytest_cache` or `__pycache__` into the
  tree, use `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`.
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. One simple command per Bash call. Refused twice for the same call:
  stop and say so; never work around a refusal.

## Return (your final message, in full)
The twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks
first), then a judgement line (`judgement: pass` or `judgement: fail`), your findings (each: id, what you did, what
happened, scope in/out, ordinary work yes/no, consequence), and the fenced `verdict` block JUDGEMENT.md below
defines, with one entry for `success-6`, exactly in that form:

```verdict
{"kpis": [{"kpi": "success-6", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

## JUDGEMENT.md (word for word, `governance/project/briefs/JUDGEMENT.md` at this head)

