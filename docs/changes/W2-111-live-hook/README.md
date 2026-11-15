# W2-111 r5: the live hook's diff for ACT-GUARD-FIX-7 (DEC-1187, S10; S9's live part)

`live-hook.diff` is a diff of `.claude/hooks/` against the bytes applied by ACT-GUARD-FIX-6:
`pretooluse.py` `9b4228ea095a`, `bash_writes.py` `f03f9ac3e431` and `role_reads.py` `5407aade9417`. The ticket
never writes `.claude/`; the CTO builds the ACT from this file. After the diff: `pretooluse.py` `665614961cd0`,
`role_reads.py` `543cf1b26701` and `bash_writes.py` unchanged (`f03f9ac3e431`).

Apply it to a clean copy, from the folder that holds `.claude/`: `git apply live-hook.diff` (or `patch -p1 <
live-hook.diff`). The engineer checked both on fresh copies of the three applied files: `git apply --check -v`
checked both files, `git apply` applied cleanly, and the result was byte-identical to the measured copy.

**Follow-ups for the ACT (outside this ticket's paths):**
- `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools` checks that
  `docs/changes/W2-141-hook/pretooluse.py` equals the live `pretooluse.py` with one line replaced. Regenerate the staged
  copy from the patched file the same way, as was done for ACT-GUARD-FIX-6.
- `role_reads.py` changes, so its `_method()` key (the module's own sha256) changes. The link cache it keys under
  `LINK_CACHE` is filled again once, on the first refusal that reads it. This affects speed only.

## What changes, and why no decision can change

Line ranges are before → after: pretooluse.py 9b4228ea095a → 665614961cd0, role_reads.py 5407aade9417 →
543cf1b26701.

| function | lines before → after | what | why the decision is the same | hook-local until 0.1.1 |
|---|---|---|---|---|
| `load_yaml_unique`, `use_fast_yaml` (new) | — → 316-347, 350-359 | Parses the YAML the guard reads with libyaml's `CSafeLoader`: the held-out list, the evaluation sets and the hook's three path-map blocks. The pinned names `gov.util.parts.load_yaml_unique` and `gov.guard.heldout.load_yaml_unique` are pointed at it for this hook run. Each text is parsed once per run. | It uses SafeLoader's own constructor and resolver, and the product's duplicate-key check word for word. On any error (a YAML error, a key written twice, no libyaml) the product's own loader runs on the same text, so every refusal and its text are the product's. A stream is read first. Each caller gets a deep copy. Nothing is kept on disk or across calls (one hook process judges one call). Checked equal on 88 distinct texts: every `*.yaml` under `governance/` and `template/` (this tree and the live repository), the tests' fixtures, the planted fixtures, and the four path-map blocks of both maps as the hook slices them. Same data, and the same 8 refusals with the same text. | yes: 0.1.1's `parts.load_yaml_unique` does the same (5532c6f80462) |
| `_tree_roots` | 395-419 → 446-469 | Builds the runs clones' `.git` list with `runs_gits` instead of 4 globs, and resolves real paths with `realpaths`. | It gives the same list in the same order (see the two rows below). | no |
| `runs_gits`, `_glob_folders` (new) | — → 498-528 | Exactly `[g for p in ("*/.git", …, "*/*/*/*/.git") for g in glob.glob(join(RUNS, p))]`, with each folder listed once. Before, the first level was listed 4 times, the second 3 and the third 2: about 640 listings on every call. | It follows glob's own rules: dirs only for a `*` with parts after it (`is_dir()` follows links), hidden names left out, `os.path.lexists` for the literal `.git`, the listing order kept, and a folder that cannot be listed gives what was listed. Checked equal to glob on the live `~/gov-os-runs` (55 found), the corpus plant, and a planted edge folder (folder links, a broken `.git` link, a hidden folder, a file named `.git`, a folder that can be entered but not listed, a link loop, too deep). | no |
| `realpaths` (new) | — → 472-492 | `os.path.realpath` of each tree, with shared folders resolved once. | It is r4's `gov.guard.reads._realpaths`, word for word. Checked equal to `os.path.realpath` on 633 paths: live and planted trees, run clones, links, a broken link, a loop, `..`, `.`, `//`, relative, empty. | could be imported from 0.1.1 |
| `session_applies` | 638-651 → 747-764 | Reads the main tree's ticket only when the main tree is another tree. | When root and main are the same folder it is the same file: the same names, or the same refusal raised by the first read. | no |
| `classes` → `tree_part`, `tree_parts` (new) | 764-1233 → 877-1401 (new 1352-1397, 1407-1410) | Makes each tree's hidden part (the judge's `_Part`, and `Narrow`) when a path at, in or above the tree is judged. This is S8's rule, as r4's `gov.guard.reads._TreePart`. | Every answer is the part's own. A path not below the root is in no part of the tree (`rel()` is None, `match(None)` is False). A path not at, in or above the root is at or above none of its literal folders (each at or below the root). `below()` keeps the part's own first test. `held`, `files` and `match` make the part. `getattr(part, "wbs", None)` stays None without making it (no `__getattr__`). The globs are the evaluation sets' and the block's, already checked as text paths (`_paths_ok`), so making a part cannot raise: making it later turns no refusal into an allow. | `TreePart` of `_Part` could be 0.1.1's `_TreePart`; `TreeNarrow` stays (Narrow is the hook's) |
| `main` | 1386-1545 → 1634-1795 | Calls `use_fast_yaml()`, builds `TreePart`/`TreeNarrow` instead of `_Part`/`Narrow` per tree, and uses the hook's own `has_install`. | As the rows above. | — |
| `_path_folders`, `has_install` (new) | — → 1535-1598 | The install check with PATH's real folders read only when a download names a target, once per PATH value (S7, r4's `install.py` 143-211). | It is r4's `has_install`, line for line, over the pinned module's own helpers (`_segments`, `_split`, `_head`, `_PKG`, `_SH`, `_uv_install`, `_download_target`: identical in 0.1.0 and 0.1.1). It gives the same answer for every command (r4's review). When the pinned gov has `_path_folders` (0.1.1 on), the product's own is called. | yes |
| role_reads `_realpaths` (new), `Judge.trees` | — → 439-461; 443-453 → 468-478 | `trees()` resolves its ~140 trees with shared folders resolved once. | The same code as `realpaths` above (checked equal on the same 633 paths). | no |

Fails closed, as before: any error in the new code (an import, a YAML error, a key written twice, a part that cannot
be walked) raises inside `main()`, and the top-level handler refuses with the same `could not decide: …` text.
No cache is written to disk. The per-run memos are dicts inside the one hook process.

## Proof that no decision changed (F4)

- **The decision corpus through both copies as processes**, in the settings.json command form (pinned interpreter,
  `-E`: configuration A). The planted repository is `test_w2_111_plant`'s: 155 trees, one nested, one through a link,
  a locked and a gone one, a run clone. Its main-tree path map gets the hook's own blocks (`sets_root_hidden` with
  wildcard globs, `session_hidden`, `write_refused`, `role_paths`) and a held-out list. The calls: 4,204 corpus calls
  (r4's kept 1,190; the calls of `tests/unit/guard/` and of W2-42a's, W1-02's, W1-05's, W2-84's and W2-141's
  acceptance suites, recorded this run) plus 87 hook-only calls at the planted blocks. That is 4,291 calls × 4 roles
  (engineer, test designer, auditor, none) = 17,164 decisions. Final copy: see `hfinalA` in the engineer's return.
  Earlier copy: 0 differences in exit code, decision, reason and stderr; 3,946 refused and 16 fail-closed on both.
- **The live hook's unit suite** (`tests/unit/hooks/test_live_hook.py`, pointed at each copy, pinned interpreter):
  62 passed and 1 failed, the same on both copies. The one failure,
  `test_a_removed_worktree_falls_back_to_the_hook_s_own_tree`, comes from the copy's location: the scratch copy is
  in no git tree, and that case uses the hook's own tree.

## Measured (S10, S9): measure.py's method, paired, the live repository

The method is `~/gov-os-runs/W2-111/gf6-measure/measure.py`'s, copied: the reference hook, the settings command
through `sh -c`, RUSAGE_CHILDREN deltas, 3 warm-up calls, rounds of 40, judged = nearest-rank p95(CPU) −
median(reference CPU), best of 3 rounds. The before and after copies alternate per sample in the same run. The
repository, its config and the targets are the live repository's (38 worktrees, 55 run clones). PATH is the real
session PATH recorded by the lead, 46 entries (27 under `/mnt/c`). The engineer's sandbox inherited only 5 entries,
so the recorded one was used and not shortened. The live repository's `git status --short` was the same before and
after (empty).

**Configuration A**: the pinned 0.1.0 gov as is, which is what ACT-GUARD-FIX-7 alone gives. The load column is the
1-minute load at each round. It was not quiet for most cases (over 10 from the 4th case on), so these figures are
**not quiet figures**.

| case | before judged | after judged | drop | ref median b/a | CPU p95 b/a | wall p95 b/a | load |
|---|---|---|---|---|---|---|---|
| W1-05 Edit-engineer | 80.9 | 70.6 | 10.3 | 15.9/15.6 | 96.8/86.2 | 96.3/85.7 | 3.5-8.3 |
| W1-05 Glob-engineer | 84.0 | 64.7 | 19.3 | 15.5/15.3 | 99.6/80.1 | 98.9/79.5 | 7.8-8.9 |
| W1-05 Glob-no-role | 64.5 | 59.7 | 4.8 | 16.6/16.6 | 81.0/76.3 | 79.5/75.1 | 7.8-10.6 |
| W1-05 Grep-engineer | 93.3 | 78.6 | 14.7 | 16.4/16.8 | 109.7/95.4 | 108.8/93.6 | 10.6-15.0 |
| W1-05 Grep-no-role | 67.1 | 62.6 | 4.6 | 16.9/16.7 | 84.0/79.3 | 83.6/78.2 | 15.0-17.2 |
| W1-05 NotebookEdit-engineer | 89.0 | 74.0 | 15.0 | 17.0/17.0 | 106.1/91.0 | 105.3/90.3 | 16.9-20.3 |
| W1-05 Read-engineer | 90.4 | 73.2 | 17.2 | 16.7/16.8 | 107.1/90.0 | 106.5/86.2 | 19.1-20.3 |
| W1-05 Read-no-role | 64.9 | 61.6 | 3.4 | 16.8/16.8 | 81.7/78.4 | 81.1/78.2 | 17.6-19.2 |
| W1-05 Write-engineer | 80.5 | 66.3 | 14.2 | 15.7/16.5 | 96.1/82.8 | 93.2/82.2 | 15.2-17.6 |
| W1-02 no-role Write (scratch) | 52.8 | 47.8 | 5.1 | 15.0/14.8 | 67.8/62.6 | 67.5/61.2 | 11.7-14.0 |
| W1-02 engineer Write src (allow) | 85.9 | 67.8 | 18.1 | 15.8/16.1 | 101.7/84.0 | 101.0/83.4 | 10.7-11.7 |
| W1-02 engineer Write acceptance (deny r1) | 86.9 | 69.7 | 17.3 | 16.0/16.3 | 102.9/85.9 | 102.3/85.1 | 10.7-11.7 |
| W1-02 test-designer Write acceptance | 87.1 | 69.7 | 17.4 | 16.4/16.3 | 103.5/86.0 | 102.7/83.7 | 11.5-12.1 |
| W1-02 auditor Write src (deny r5) | 88.4 | 69.5 | 18.9 | 16.6/16.4 | 105.0/86.0 | 104.4/84.2 | 11.5-13.1 |
| W2-57 test-designer Read ordinary | 94.1 | 67.9 | 26.1 | 16.7/16.4 | 110.7/84.4 | 109.2/83.9 | 12.8-14.4 |
| Bash ls (engineer) | 98.2 | 76.2 | 21.9 | 16.5/16.3 | 114.6/92.6 | 175.2/92.0 | 13.9-14.8 |
| Bash pipeline (engineer) | 96.8 | 72.8 | 24.0 | 17.0/16.5 | 113.8/89.3 | 181.4/88.7 | 13.5-14.1 |
| Bash write to scratch (engineer) | 97.4 | 73.6 | 23.8 | 16.3/16.2 | 113.8/89.8 | 174.3/88.5 | 11.7-13.5 |
| Bash git status (CTO) | 88.8 | 74.1 | 14.8 | 15.8/16.0 | 104.6/90.1 | 171.9/87.0 | 10.6-11.7 |
| Bash grep\|wc (test-designer) | 99.2 | 76.5 | 22.7 | 16.3/16.2 | 115.5/92.7 | 178.6/89.2 | 10.3-11.3 |

In configuration A every case is within 100 ms, after 47.8-78.6 ms. On wall time, the PATH-once check brings Bash
from about 175 to about 90 ms. **S9's 30 ms is not reached: the drop is 3.4-26.1 ms on the 15 mapped cases.** The
quiet trial of 4 cases at load 0.9-1.9 gave the same picture: before 72-87, after 57-68, drop 14-22.

What remains is not the hook's own code. Of an after call's ~72 ms of process CPU (quiet, engineer Read), about 15 ms
is the interpreter (the reference), about 27 ms is the pinned gov's import chain (`gov.guard.reads` 11.9 ms with
`decide`, `runs`/pathlib, `bash_writes`, `protected`), 6.8 ms is `import yaml` (the pure-Python package loads even
for CSafeLoader), and 6-9 ms is compiling the 84 KB `pretooluse.py` (a script run as `python file` is never cached).
The git children take 4.5 ms (`worktree list`, `remote get-url`, `rev-parse`). The no-role calls drop only 3-5 ms
because they build no hidden parts: their cost is mostly those imports. See the engineer's return,
`proposed_decisions`/`unresolved`, for the options.

**Configuration B**: the after copy with the gov of the W2-111 tree's `src`, which is what it gives after 0.1.1. It is
the pinned interpreter run without `-E`, with `PYTHONPATH=<tree>/src`, paired against the same before copy in A. See
the engineer's return.
