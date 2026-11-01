# Brief: engineer, DAEO-jsg1 (W2-86), batch 1 — the path map's namespace block

You are a fresh engineer. Ticket: `DAEO-jsg1` (`W2-86`), profile STANDARD. You work in the worktree `/home/usain/gov-os-worktrees/W2-86` on branch `w2/W2-86` only. You build to the specification and its KPIs, never to the tests.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-jsg1','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (the twelve fields), naming what happened. Never delete anything outside this worktree.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-jsg1`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-86` and `w2/W2-86`), and `git rev-parse --short=12 HEAD` (expect `eb198a6ff517`, the merge of the acceptance tests onto the base `9dc5288161c4`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another; return only after your commit exists.
- **The code under test (DEC-732), word for word:** **In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820).** You read freely: the whole repository, git history, other worktrees. Refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-86/` (here, in `/home/usain/gov-os-worktrees/W2-86-tests`, or anywhere), by any tool; you may run those tests and see their names, results and failure messages, never their source;** **(d) the hidden half of any evaluation set (`fixtures/evaluation/**/hidden/**`), in any tree, never read or run.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; never list, glob or search it.
- **DEC-849, read refusals:** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (literal paths only); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; anything longer goes in a script file you write with the Write tool under `/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/eng/`, and you run that file. A refused form is not retried in another disguise (DEC-409).
- **Your scratch:** the test designer of this ticket found writes under `.gov-runtime/scratch/<name>/` refused in its sandbox. If `.gov-runtime/scratch/eng/` is refused for you too, take that refusal and use instead the sandbox's own temporary folder (print it once with `printenv TMPDIR`, then write there by its literal path with the Write tool). Say in your return which one you used.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. No copy of the repository (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it or a folder of it); a stand-in copies single named files, never `governance/project/`. No clone or copy of a programme under `.gov-runtime/` (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- Never touch `tests/acceptance/**`, or `.gov-runtime/**` outside `.gov-runtime/scratch/`. Install nothing (an install is a P1 package in your return). Never run `gov rebuild --no-embeddings`; you need no rebuild at all. Never run `gov close`, `gov adopt` or `gov pause`.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** your share is 2 GB and 100,000 files and folders outside the tracked tree. Set `TMPDIR=/tmp/gov-os-lead-W2-86` for every test run unless the sandbox has set its own temp folder (then keep that one). Keep pytest's own retention (no `--basetemp`). Clean up what you make as you go; measure your scratch (`du -sh`, `du -s --inodes` of `.gov-runtime/scratch/eng/`) at the end and give it in `evidence`.
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return `AUTH_REQUIRED`.
- **The acceptance tests arrive while you work (DEC-963):** the test designer works in parallel in its own worktree; your lead merges its tests here between your batches. If `/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/lead/TESTS-READY` exists when you have committed, run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m pytest tests/acceptance/W2-86 -q -p no:cacheprovider -rA` once, reading results only, and quote them. If it does not exist, say so and do not wait.

## What you read

- The ticket file `.tickets/DAEO-jsg1.md` (read-only): its KPI lines (success and failure) and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-86").
- In `docs/DECISION_REGISTER.md`: DEC-952 item 1, DEC-388 (DP-8 above all: it names this value and this fix), DEC-381, DEC-694.
- Lens B's F6: `docs/assessment/2026-10/B-memory-retrieval.md` (the finding near line 520, the policy value near line 633).
- `src/gov/retrieval/semantic.py`: `EMBEDDED` (line 44) and `_wanted` (lines 206 to 220): a file is embedded only when it is in at least one namespace and every namespace it is in says exactly `embedded`. The pattern language is `gov.secrets._matches` (`*` stays inside one folder, `**` crosses folders). Read them; never change them.
- `governance/project/path-map.yaml`: its header (lines 1 to 3) and its `namespaces:` block (lines 6 to 133), above all `kernel-template` (lines 84 to 93).
- The vendored parts: the `superpowers` entry of `governance/project/tool-registry.yaml`, `template/governance/kernel/skills/superpowers/vendored.yaml`, and the tracked files under `template/` (`git ls-files template`).

## The specification (DEC-952, DEC-388)

Today `kernel-template` (`template/**`) says `embedded, except vendored code`; the indexer reads any value but the two as not embedded (fail closed, DEC-388), so nothing under `template/` has a vector. DEC-388 named the fix: the vendored paths get their own namespace, so the rest of `template/**` can say `embedded`. **Nothing in the code changes.**

Edit **only the `namespaces:` block** of `governance/project/path-map.yaml` (DEC-952 lets this ticket edit it; nothing else in the file changes, the `retrieval_authority` block, the capabilities, the ratchet lists `accepted_reds` and `load_sensitive` and every other line included):

- **`kernel-template`** changes only its `paths` and its `embedding_policy`, which becomes exactly `embedded`. It covers every tracked file under `template/` except the sets below. Among them: the role files (`template/governance/kernel/roles/*.md`), the hooks (`template/governance/kernel/hooks/*.py`), the kernel skills (`template/governance/kernel/skills/<name>/SKILL.md`) and `template/governance/kernel/skills/superpowers/vendored.yaml` (the kernel's own record), and the template's top-level files, `.github/`, `openspec/`, `governance/project/`, the kernel's checks, schemas, templates, canaries, launch and settings.
- **New namespace(s) beside it, `embedding_policy: not embedded` written exactly:**
  - **vendored code:** `template/governance/kernel/vendor/**`; the kernel's copies of the vendored skills, `template/governance/kernel/skills/superpowers/<skill>/**` (every file in a folder below `superpowers/`, never `vendored.yaml`); the vendored tk, `template/governance/kernel/bin/**`;
  - **the generated adapter copies:** `template/.rulesync/**` (the root's `.rulesync/**` and `.claude/**` are already not embedded, and the copies would put each kernel skill in the index twice). A namespace of its own, separate from the vendored one.
  - Every new namespace carries every field `kernel-template` has (`paths`, `memory_class`, `sensitivity`, `permitted_roles`, `retention`, `export_policy`, `embedding_policy`, `provenance`, `deletion_rebuild`), with values true to what it holds, and a short comment naming DEC-952 and DEC-388.
- **Exactly one namespace for every tracked path under `template/`** (the header's rule). So `kernel-template`'s patterns are narrowed (`**` crosses folders, `*` stays inside one), never left overlapping the new ones. Prefer patterns that a new kernel file in an existing kernel folder still falls under; a path that falls in no namespace is not embedded (fail closed) and is caught by the path-map check.
- **Fail closed:** no vendored file or generated copy embedded; no path under `template/` in no namespace or in two; no value but the two; no change to the indexer's code; no file outside `template/` gains or loses its embedding.

## How you check it (your own checks; never the acceptance tests' source)

- Write a small script under `/home/usain/gov-os-worktrees/W2-86/.gov-runtime/scratch/eng/` that, over `git ls-files`, counts for each tracked path the namespaces it matches (with `gov.secrets._matches`) under the new map and under `git show 9dc5288161c4:governance/project/path-map.yaml`, and reports: paths under `template/` in zero or two namespaces; the embedded verdict of every path under `template/` by group (roles, hooks, kernel skills, `vendored.yaml`, vendored set, `.rulesync`); and every path outside `template/` whose verdict differs from the base's (must be none). Quote its summary.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.check.pathmap` (W2-95 owns that check: run it, never edit it) and `gov.check.schema`: green; quote them. Also `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m gov.cli.main doctor --json` (or without `--json` if it takes none): it must not report "no namespace is embedded".
- `git diff 9dc5288161c4 -- governance/project/path-map.yaml`: every changed line lies inside the `namespaces:` block. Quote the diff's stat.
- Optionally a builder test as a new file `tests/unit/retrieval/test_w2_86_<name>.py` (regression evidence only; no other file in `tests/unit/retrieval/`), run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-86/src python3 -m pytest <file> -q -p no:cacheprovider`.

You write only: `governance/project/path-map.yaml` (its `namespaces:` block), new `tests/unit/retrieval/test_w2_86*`, and your scratch under `.gov-runtime/scratch/eng/`. In proportion (DEC-135): about 25 lines of path map; nothing beyond the KPIs.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`. One commit, trailers in the final block:

    git commit -m "W2-86 (DAEO-jsg1): the kernel template is embedded as the path map means it; vendored code and the generated copies in namespaces of their own" --trailer "Task: DAEO-jsg1" --trailer "Implements: DEC-952, DEC-388" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`, quoted.

## Return

Your commit's hash (12 digits); the namespaces you added and the patterns of each; your script's summary (counts per group, zero/two-namespace paths, verdict changes outside `template/`); the checks' output; the diff stat; the acceptance results if TESTS-READY existed; whether you used `gov retrieve` and for what; the read refusals you met (DEC-849); any package.

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

Your return gives the twelve fields first, each as a labelled line, with any payload after them. Refused twice for the same call: stop and say so.
