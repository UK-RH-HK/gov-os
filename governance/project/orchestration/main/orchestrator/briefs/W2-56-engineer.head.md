# W2-56 — the engineer's brief: `gov launch` usable for every worker, on the guard alone (DAEO-wnnz)

You are the engineer for **W2-56** (`.tickets/DAEO-wnnz.md`: read it in full, with "The first half's points settled"
and "The guard-alone outcome (DEC-1112 (1))"). The owner decided W2-56 builds on the path-map guard alone, with today's
launcher sandbox for workers unchanged (not generated from the path map). The acceptance cases are written (both
halves, by the independent test designer); the interface they assume is below, handed to you from the start (the spec,
not the tests). Build to it, keeping every KPI line. Where the interface and a KPI line disagree, the KPI line wins: say
so in your return.

**Your job:**
1. **The product** in your paths (`src/gov/launch/launcher.py` at its call sites and argument checks;
   `src/gov/launch/sandbox.py` and `src/gov/launch/environ.py` as new modules of your own; `src/gov/codeintel/__init__.py`
   for the daemon's folder only; `tests/conftest.py` for S1's two lines only, D-1): S1 (one daemon folder per test
   session, cleaned; the tool off PATH but in W1-16 and W1-20; a launched session's daemon folder under its own temp
   folder), S4 (no placeholder reaches a commit), S5 (the cleaned environment), S6 (the refused arguments), S7 (the
   short start lock), S8/S9 (the reranker's one socket, nothing else), S11 (a sandboxed unranked search counted), S12
   (signals to the group), S14 (the template's one allow rule in `template/governance/kernel/settings.json`, now in your
   paths, DEC-1083; the hooks stay), S15 (temp folders removed), F2 (every refusal today still refuses).
2. **Your unit tests** in `tests/unit/launch/**` and `tests/unit/codeintel/**` (`tests/unit/codeintel/test_codeintel.py`
   asserts today's `/tmp/gov-cbm-<uid>`: change it to the new place).
3. **The CIT-E** `docs/changes/W2-56-CIT-E.md`: how each allowed-path form is held (S3), the script-write gap (S2), the
   accepted-arguments list weighed against the refusal list (S6, lens E R6), S7's way, S11's way; S10's section is the
   CTO's (leave a heading).

## Where you work
- `/home/usain/gov-os-worktrees/W2-56`, branch `w2/W2-56` (from `w2/integrate`; the acceptance cases are merged in
  before you start). Your paths are the ticket's `allowed_paths`; a file you need outside them is a package in your
  return, not an edit.
- **You never read `tests/acceptance/`** (W2-56's, and W1-27's revised for this ticket; G-14, DEC-820 (c)): only
  `gov accept`'s results.
- **The exclusion line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=acceptance`; every
  Grep or Glob call that could reach it carries `!tests/acceptance/**`; find carries `-path '*/acceptance' -prune`;
  never open the test designer's worktree (base name `W2-56-tests`). If a search shows you a line of a case anyway,
  stop reading it and say so.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  your unit tests (`tests/unit/launch tests/unit/codeintel`); then
  `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56` (counts per line; the real-sandbox
  cases skip here, the CTO runs them outside); then `accept W1-27` (its W2-67 cases); then `tests/unit/guard
  tests/unit/retrieval tests/unit/resources`, every red named with its cause. Never the full suite.
- **Commit as you go**, each part as it passes.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/`, `~/.cache/gov-os/` or any service; no GPU job; no installs.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-56` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112, DEC-799" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), what changed per KPI line, `gov accept`'s counts per
line for W2-56 and W1-27, the unit and regression counts with every red named, packages for files outside your paths,
and any place where the interface and a KPI line disagree.

---

# The interface the acceptance cases assume (the designer's README, as written)

