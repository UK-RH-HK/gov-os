# W2-141: the hook as built, staged for the operator's ACT (DEC-1093 (2), DEC-1102)

A launched worker cannot edit `.claude/` (the launcher's DEC-315 deny rules), so W2-141's hook side is staged here
as whole-file copies. The CTO prepares the ACT from the merged branch; the owner's operator copies them over the live
files at the lift's re-pin. Nothing live changes before then. W2-141's acceptance cases load these copies when they
exist, else the live hook.

| Staged copy | Goes to | Made from (sha256 of the live file) |
|---|---|---|
| `role_reads.py` | `.claude/hooks/role_reads.py` | `5407aade941734c086aefefe5372e715262aedc1805380f9427b068eb2444f07` |
| `pretooluse.py` | `.claude/hooks/pretooluse.py` | `74f8dbea4761de37628305e5d58125641ae39a409a7ed0a2babb379b1ceca5b8` |

`pretooluse.py` was rebuilt on 2026-11-10 on the live hook at `9cce7430d` (ACT-SETS-GLOBS-1; it carries rule 2b's
glob line, rule 2c and rule 2d, which the first copy, made from `bd545af8…` at `15952bbfa`, lacked). W2-141's one
change was re-applied and nothing else (DECIDED-NOT-DONE row 78).

If a live file's hash no longer matches when the ACT is prepared, the live file changed after these copies were
made: merge that change into the copy first. Never overwrite it.

## `pretooluse.py`: one word

G-14's tool list (the `role_reads` block) gains `"Glob"`, so S1's Glob half reaches `role_reads`. Nothing else
changes; `tests/unit/guard/test_w2_141_search.py` checks that this is the only difference.

```diff
-    if tool in ("Read", "NotebookRead", "Grep", "Bash"):
+    if tool in ("Read", "NotebookRead", "Grep", "Glob", "Bash"):
```

## `role_reads.py`: a search from above no longer passes for the engineer's own folder

Against the live file: 720 lines added, 14 removed (`git diff --no-index --stat .claude/hooks/role_reads.py
docs/changes/W2-141-hook/role_reads.py`).

- **The docstring** says what changes. The live text says "a search from a folder above" is let through. The new
  text keeps that, except for the engineer's own acceptance folder, and removes Glob from the "names only" list.
- **`from __future__ import annotations`** is added after the docstring. The matching block has type hints, and this
  keeps them working on every interpreter the pin may use.
- **`Bash` records searches.** `Bash.search` keeps each recursive search's start, as `x_search` reads it: grep -r/-R,
  rg, ag, ack, a find whose action reads, and `git grep`. A listing (find, `rg --files`, `ag -g`, `ack -f`,
  `git ls-files`) waits in `_listed` and becomes a search only when a reader takes its names: `| xargs <reader>`, a
  while-read loop that reads, a reader's `$(...)` word, or the `$(...)` list of a for loop whose body reads. `run`
  tracks the pipeline for this (`fed`, `into`, `_xargs_reads`, `_loop_reads`, `_for_reads`). An rg, ag or ack fed by
  a pipe, with no folder named, searches its input and is not recorded. `git grep` and `git ls-files` are recorded
  by `Bash.git`, from the folder its `-C` leaves it in, with their pathspecs.
- **`scan` and `tool_searches`.** `scan` returns the paths a call reads (as `reads_of` did; `reads_of` now calls it)
  and its searches. A Grep call searches from its path, with its globs read as rg's. A Glob call lists from its path,
  matched against its pattern.
- **`search_refusal`, called by `refusal` once no path is refused.** For each judge whose globs include
  `{ticket_tests}` (the engineer), it looks for `tests/acceptance/<WBS>/` in every tree: the judge's trees and the
  start's own tree. If the search's start holds the folder, or lies inside it, and the call takes in one of the
  folder's files (`_reaches`), the call is refused. The reason names the folder, cites
  `role_paths.engineer.reads_denied`, DEC-1052 G-14 and DEC-1093 (2), and says how to keep the folder out:
  `!tests/acceptance/<T>/**` for Grep, `--exclude-dir=<T>` for grep, `-g '!tests/acceptance/<T>/**'` for rg,
  `--ignore-dir=<T>` for ag and ack, `-name <T> -prune -o ...` for find, `-- . ':!tests/acceptance/<T>'` for git grep
  and git ls-files; Glob gets a path or pattern that cannot reach the folder. Some cases are let through, as today:
  - an empty folder, or no file in the folder that the call takes in;
  - a start the guard cannot resolve.

  Some cases are refused, so the guard fails closed:
  - a folder that cannot be walked whole;
  - a folder holding more than `MOST_GLOB` files.
- **The matching block** (between `# BEGIN W2-141 BLOCK` and `# END W2-141 BLOCK`) decides which files a call takes
  in or keeps out, following each tool's own rules:
  - rg's globs, and the Grep tool's: gitignore lines read from the session's folder; the last matching line wins.
  - grep's `--exclude-dir` (a folder's base name), `--include` and `--exclude`.
  - ag's `--ignore`.
  - ack's `--ignore-dir`.
  - find's `-prune` and its negated `-path` and `-name` tests, and `-maxdepth`.
  - Glob's pattern.
  - git grep's and git ls-files's pathspecs, read from the folder git runs in: a plain one names a path and what is
    below it, `*` crosses folders, and an exclusion (`:!`, `:^`, `:(exclude)`) keeps its files out. Before `--`, a
    git grep word that is not a path, a wildcard or magic is a revision, which leaves the search at that folder.
  - An option word with braces (`--exclude-dir={.git,<T>}`) is read as the options Bash makes of it.

  The block is byte for byte the one in `src/gov/guard/reads.py`, and a unit test compares the two. It is copied in
  so that the hook does not depend on the pinned product holding it: an import the pin lacked would refuse every read.

Unchanged:
- Other tickets' tests, and the cases revised for the ticket in other folders (`Linked`).
- Every other role: only a `{ticket_tests}` judge has an own folder.
- Names-only listings that no reader takes.
- A grep for the tests' names by pattern, from a folder that does not hold them.
- Every path the live hook already refuses: direct reads keep their reason.

## Rollback

Both live files are tracked; the hashes above are their contents at commit
`9cce7430d8f617eccabc48a7f7df7346c40a7602`, the last that changed `pretooluse.py` (`role_reads.py` last changed
before it, at `e02d55e40`). In the tree the ACT applies to:

1. **Before copying**, keep the live files outside the hook folder (a `.py` left in `.claude/hooks/` could be loaded):
   `cp .claude/hooks/role_reads.py .claude/hooks/pretooluse.py <a folder outside .claude/>/`, and check that
   `sha256sum` of the two copies gives the hashes in the table.
2. **To roll back**, copy the kept files back over `.claude/hooks/role_reads.py` and `.claude/hooks/pretooluse.py`.
   If the copies are lost, restore the tracked versions:
   `git checkout 9cce7430d8f617eccabc48a7f7df7346c40a7602 -- .claude/hooks/role_reads.py .claude/hooks/pretooluse.py`
   (this holds only while the live files matched the hashes above when the ACT was applied).
3. **Check** that `sha256sum .claude/hooks/role_reads.py .claude/hooks/pretooluse.py` gives the two hashes in the table
   again. No other file changes in the ACT, so nothing else needs restoring.

## Before the ACT

- `tests/unit/hooks/test_live_hook.py`'s `G14_PASSED` case `grep -r foo tests/` is revised in this branch to
  `grep -r --exclude-dir=W2-G14T foo tests/`, which passes with the live hook and with this copy (the designer's
  round-2 P-2).
- The CTO checks `guard4_check.py`'s cases against S1. Its engineer cases search `src/gov/guard/` (cannot reach) or
  run as the plain engineer, whose own folder depends on the session's ticket. Case `sets G5` (an engineer's Grep of the
  main tree's root) is refused after the ACT whenever that engineer's ticket has an acceptance folder with files in
  the main tree.
