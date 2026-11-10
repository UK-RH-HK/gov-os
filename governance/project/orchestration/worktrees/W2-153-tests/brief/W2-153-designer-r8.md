Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-153 — S3 amended (the role file's fields) and W1-38's project builder, the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer working under **W2-153** (`.tickets/DAEO-8s85.md`). Read its body's
**"S3 amended"** in full: it is the CTO's decision and states the new interface. In short:
- each composed `.rulesync/subagents/<role>.md`, and the template's copy, is the rulesync front matter (with
  `claudecode.skills`), then the role template's body, then one blank line, then the kernel role file's body
  (`template/governance/kernel/roles/<role>.md`, verbatim);
- `gov.adapters.portability` exposes `compose(root, role) -> str`, the expected source text;
- W1-38's project builder copies the kernel's `templates/` into a generated project.

Why: after ACT-CLAUDE-COPIES-2 the agents lost the role file's labelled fields, and W1-33 (MR-5) and W1-38 require
them. Separately, generated projects had no `templates/`, so portability fell back to the role files: 20 cases red in
W2-05, W1-38 and W2-57.

## The changes (DEC-866: `Rewrite-Reason:` on each)
1. **W2-153's S3 cases** (`tests/acceptance/W2-153/test_w2_153_sources.py`): the expected body is the template's
   body, a blank line, then the role file's body (front matter stripped by portability's `_split` rule). Add:
   - one case that `gov.adapters.portability.compose(root, role)` exists and returns exactly what the source must
     hold, on a fixture repository;
   - one case that the composed source's labelled fields equal the role file's (W1-33's `fields()` rule: you may
     import or reproduce it), and that the template contributes none.
2. **W1-38's builder** (`tests/acceptance/W1-38/w1_38_support.py::build_project_from_template`): also copy
   `template/governance/kernel/templates/` into the project's `governance/kernel/templates/`, file by file as the
   others are copied. Update its docstring. Check whether W2-05's and W2-57's project builders (their support files and
   conftest) build a kernel without `templates/` for the portability check. If so, revise them the same way and list
   them.
3. Change no other assertion.

## Expected outcome
- On your tree (integrate's code, old composition): S3's new cases are red for the right reason, since `compose` is
  absent and the bodies lack the role file.
- The builder change alone should turn W2-05's 8, W1-38's 11 and W2-57's 1 portability cases from red toward green,
  less any that need the new composition.
- Report each folder's counts before and after: W2-153, W1-38, W2-05, W2-57.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`, integrate merged (`bbe222c59`).
  Write only `tests/acceptance/{W2-153,W1-38,W2-05,W2-57}/`.
- Never read W2-153's new implementation. The engineer works after you, on `w2/W2-153`, so never open that tree.
  Integrate's code you may read (DEC-963).
- Run each folder in its own pytest call, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not
  found):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153-tests/src python3 -m pytest tests/acceptance/<id> -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" --tb=no`.
  rulesync is at `/home/usain/.local/bin/rulesync` (set `RULESYNC_BIN` if a case needs it).
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict`
  or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search again
  once (DEC-1092 (1)).
- **Commit** on `w2/W2-153-tests`, only those folders, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-153 S3 amended (the role file's fields in the composed agent; portability.compose) and generated projects carry templates/ (the CTO, DEC-1112 (3); DEC-866)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the cases changed and added, each folder's counts before and after, the commit and `TESTS-READY <hash12>`.
