# W2-111 r5: the live hook's diff for ACT-GUARD-FIX-7 (DEC-1187, S10; S9's live part)

`live-hook.diff` is a diff of `.claude/hooks/` against the bytes applied by ACT-GUARD-FIX-6:
`pretooluse.py` `9b4228ea095a`, `bash_writes.py` `f03f9ac3e431` and `role_reads.py` `5407aade9417`. The ticket
never writes `.claude/`; the CTO builds the ACT from this file. After the diff (r5, with rv-3's F1 fixed and
P-W2-111-YAML-REST's two role_reads reads): `pretooluse.py` `101bee39d5c9`, `role_reads.py` `02a782e31145` and
`bash_writes.py` unchanged (`f03f9ac3e431`). The r5 copy before F1 was `665614961cd0`; only the YAML loader changed
since. The F1 copy's `role_reads.py` was `543cf1b26701`; P-W2-111-YAML-REST changed only `role_reads.py` (its
`pretooluse.py` part of the diff is byte-identical).

Apply it to a clean copy, from the folder that holds `.claude/`: `git apply live-hook.diff` (or `patch -p1 <
live-hook.diff`). The engineer checked it on fresh copies of the live repository's three applied files (`9b4228ea095a`,
`f03f9ac3e431`, `5407aade9417`). `git apply --check -v` exited 0 ("Checking patch .claude/hooks/pretooluse.py...",
"Checking patch .claude/hooks/role_reads.py..."). `git apply` applied cleanly, and the result was byte-identical to
the measured copy (`101bee39d5c9`). Checked again for P-W2-111-YAML-REST on fresh copies of the live repository's
applied files: `git apply --check -v` exited 0 (the same two lines), and the applied result hashes `101bee39d5c9`,
`02a782e31145` and `f03f9ac3e431`.

**Follow-ups for the ACT (outside this ticket's paths):**
- `tests/unit/guard/test_w2_141_search.py::test_the_staged_pretooluse_adds_only_glob_to_g14s_tools` checks that
  `docs/changes/W2-141-hook/pretooluse.py` equals the live `pretooluse.py` with one line replaced. Regenerate the staged
  copy from the patched file the same way, as was done for ACT-GUARD-FIX-6.
- `role_reads.py` changes, so its `_method()` key (the module's own sha256) changes. The link cache it keys under
  `LINK_CACHE` is filled again once, on the first refusal that reads it. This affects speed only.
- The W2-111 live-hook acceptance cases (`test_w2_111_live_hook_diff_p95.py`, `test_w2_111_live_hook_slow_hook.py`
  and the live-hook part of `test_w2_111_yaml_parity.py`; 32 cases) check the before copy against ACT-GUARD-FIX-6's
  hashes. They fail by design once ACT-GUARD-FIX-7 is applied, and are to be retired or re-pointed then.

## What changes, and why no decision can change

Line ranges are before → after: pretooluse.py 9b4228ea095a → 101bee39d5c9, role_reads.py 5407aade9417 →
02a782e31145. r5's F1 fix added 24 lines in the YAML loader, so every pretooluse.py range after line 316 moved down
by 24 from the 665614961cd0 copy. P-W2-111-YAML-REST added 19 lines to role_reads.py before its `_realpaths`, so
its ranges from there on moved down by 19 from the 543cf1b26701 copy.

| function | lines before → after | what | why the decision is the same | hook-local until 0.1.1 |
|---|---|---|---|---|
| `libyaml_reads_as_python`, `load_yaml_unique`, `use_fast_yaml` (new) | — → 316-325, 328-371, 374-383 | Parses the YAML the guard reads: the held-out list, the evaluation sets and the hook's three path-map blocks. libyaml's `CSafeLoader` parses a text only when `libyaml_reads_as_python` passes it: a str with no tab, no `?` and no BOM after its first character. Every other text goes to the pinned product's own loader (the pure-Python SafeLoader). The pinned names `gov.util.parts.load_yaml_unique` and `gov.guard.heldout.load_yaml_unique` are pointed at it for this hook run. Each text is parsed once per run. | Every answer is the pure SafeLoader's: the same data, or the same refusal (exception type and text). libyaml reads three kinds of text that the pure parser refuses (rv-3 F1): a tab as a separator, a `?` inside a flow item, and a BOM at the start of a later line. Those texts never reach libyaml. Any `?` at all goes to the pure parser, because whether a `?` lies inside a flow cannot be told without scanning. For the other texts libyaml uses SafeLoader's own constructor and resolver, and the product's duplicate-key check word for word. On any error of that parse (a YAML error, a key written twice, no libyaml) the product's own loader runs on the same text. So every refusal and its text are the pure loader's, whichever parser read the text first. A stream is read first and handed to the product's loader as a stream of the same name and text, so the error's mark names the file as the pure loader names it. Each caller gets a deep copy. Nothing is kept on disk or across calls (one hook process judges one call). Checked equal (r5, F1) on 100 distinct texts, each as a text and as an open file: every `*.yaml` under `governance/` and `template/` (126 files, this tree and the live repository), every top-level block of both path maps as the hook slices it, and the planted fixtures (the unit tests' samples, broken texts and the ten divergent texts). Same data, and the same 17 refusals with the same text. A fuzz of 40,000 mutated texts (20,000 inserting tabs, `?`, `? `, BOMs and colons; 20,000 over a wider alphabet: line breaks, flow and block indicators, quotes, anchors, tags, NUL and control characters, NEL, LS, `￾`) gave **0 differences** from the pure loader, in the product and in this copy, as texts and, for every fourth text, as named streams. Raw libyaml without the rule differed on 1,382 of them, and every one held a tab, a `?` or a BOM after the start. | yes: 0.1.1's `parts.load_yaml_unique` does the same (the r5 F1 commit) |
| `_tree_roots` | 395-419 → 470-493 | Builds the runs clones' `.git` list with `runs_gits` instead of 4 globs, and resolves real paths with `realpaths`. | It gives the same list in the same order (see the two rows below). | no |
| `runs_gits`, `_glob_folders` (new) | — → 522-552 | Exactly `[g for p in ("*/.git", …, "*/*/*/*/.git") for g in glob.glob(join(RUNS, p))]`, with each folder listed once. Before, the first level was listed 4 times, the second 3 and the third 2: about 640 listings on every call. | It follows glob's own rules: dirs only for a `*` with parts after it (`is_dir()` follows links), hidden names left out, `os.path.lexists` for the literal `.git`, the listing order kept, and a folder that cannot be listed gives what was listed. Checked equal to glob on the live `~/gov-os-runs` (55 found), the corpus plant, and a planted edge folder (folder links, a broken `.git` link, a hidden folder, a file named `.git`, a folder that can be entered but not listed, a link loop, too deep). | no |
| `realpaths` (new) | — → 496-516 | `os.path.realpath` of each tree, with shared folders resolved once. | It is r4's `gov.guard.reads._realpaths`, word for word. Checked equal to `os.path.realpath` on 633 paths: live and planted trees, run clones, links, a broken link, a loop, `..`, `.`, `//`, relative, empty. | could be imported from 0.1.1 |
| `session_applies` | 638-651 → 771-788 | Reads the main tree's ticket only when the main tree is another tree. | When root and main are the same folder it is the same file: the same names, or the same refusal raised by the first read. | no |
| `classes` → `tree_part`, `tree_parts` (new) | 764-1233 → 901-1425 (new 1376-1421, 1431-1434) | Makes each tree's hidden part (the judge's `_Part`, and `Narrow`) when a path at, in or above the tree is judged. This is S8's rule, as r4's `gov.guard.reads._TreePart`. | Every answer is the part's own. A path not below the root is in no part of the tree (`rel()` is None, `match(None)` is False). A path not at, in or above the root is at or above none of its literal folders (each at or below the root). `below()` keeps the part's own first test. `held`, `files` and `match` make the part. `getattr(part, "wbs", None)` stays None without making it (no `__getattr__`). The globs are the evaluation sets' and the block's, already checked as text paths (`_paths_ok`), so making a part cannot raise: making it later turns no refusal into an allow. | `TreePart` of `_Part` could be 0.1.1's `_TreePart`; `TreeNarrow` stays (Narrow is the hook's) |
| `main` | 1386-1545 → 1658-1819 | Calls `use_fast_yaml()`, builds `TreePart`/`TreeNarrow` instead of `_Part`/`Narrow` per tree, and uses the hook's own `has_install`. | As the rows above. | — |
| `_path_folders`, `has_install` (new) | — → 1559-1622 | The install check with PATH's real folders read only when a download names a target, once per PATH value (S7, r4's `install.py` 143-211). | It is r4's `has_install`, line for line, over the pinned module's own helpers (`_segments`, `_split`, `_head`, `_PKG`, `_SH`, `_uv_install`, `_download_target`: identical in 0.1.0 and 0.1.1). It gives the same answer for every command (r4's review). When the pinned gov has `_path_folders` (0.1.1 on), the product's own is called. | yes |
| role_reads `_realpaths` (new), `Judge.trees` | — → 458-480; 443-453 → 487-497 | `trees()` resolves its ~140 trees with shared folders resolved once. | The same code as `realpaths` above (checked equal on the same 633 paths). | no |
| role_reads `load_yaml` (new), `section` | — → 95-109; 95-119 → 112-136 | P-W2-111-YAML-REST (a): the path map's `role_paths:` block is parsed by `load_yaml`: libyaml's `CSafeLoader` only for a text with no tab, no `?` and no BOM after its first character (`libyaml_reads_as_python`'s rule, word for word); any other text, and any text whose libyaml parse raises (no libyaml too), by the pure-Python SafeLoader. Before, `CSafeLoader` read every block. | For every block libyaml is given, its answer is the pure loader's (the equality and fuzz below), so a well-formed block gives the same section. A block the pure loader refuses (a tab as a separator, a `?` in a flow item) now raises `role_paths cannot be read`, the refusal the block's YAML error always gave: a fail-open closed (libyaml read it and the hook decided from it). | yes: 0.1.1's `gov.util.parts.load_yaml` and `gov.util.role_paths.section` |
| role_reads `ticket_front` | 149-174 → 166-193 | P-W2-111-YAML-REST (a) and -FRONT (a): the session ticket's front matter is parsed by `load_yaml`; front matter the pure loader refuses raises `ValueError("the session's ticket file cannot be read: its front matter is not YAML (fail closed, P-W2-111-YAML-REST-FRONT (a))")`. Before, `CSafeLoader` read it, and a front that could not be parsed gave `{}`. | Well-formed front matter gives the same dict. No front matter (`""`), a comment only, no ticket: `{}` as before. Only front matter the pure loader refuses changes: from `{}` (or libyaml's reading) to a refusal. An empty front handed a test designer the engineer's code (no `{ticket_impl}` paths): a fail-open closed. The top-level handler refuses with `could not decide: …` (exit 2). The text names no path (DEC-820). | yes: 0.1.1's `gov.util.role_paths.ticket_front` raises `RolePathsError` |
| role_reads `judges` | 843-864 → 888-912 | Reads `ticket_front` for every role whose globs name the ticket (`{ticket_…}`), not only for `{ticket_impl}`; the front is kept for `{ticket_impl}` only, as before. | For well-formed front matter the value read is dropped for a `{ticket_tests}`-only role, so `front`, `allowed`, `names`, `wbs` and the links are what they were. Without it, a malformed front would reach `_links_unless_coordination`, whose catch-all turns a ticket that cannot be read into "no links" (the own folder only): the engineer's linked tests in other tickets' folders would open. Now it refuses first. It also closes, for the engineer and the designer, the pinned 0.1.0 `parts._front` that still reads the front with libyaml until 0.1.1. Cost: one read and libyaml parse of the ticket's front per role-checked call (see the measure). | yes: 0.1.1's `gov.util.role_paths.judges` |

Fails closed, as before: any error in the new code (an import, a YAML error, a key written twice, a part that cannot
be walked) raises inside `main()`, and the top-level handler refuses with the same `could not decide: …` text.
No cache is written to disk. The per-run memos are dicts inside the one hook process.

## Proof that no decision changed (F4)

**r5, P-W2-111-YAML-REST (the copy `101bee39d5c9` / `02a782e31145`, and the product at `1e455d6d57ce`):** the
product's `role_paths.section`, `role_paths.ticket_front` and `parts._front` read through `gov.util.parts.load_yaml`,
and the live hook's `role_reads.section` and `role_reads.ticket_front` through its copy (rows above).

- **The rule, equality:** every ticket front matter of the live repository and this tree (258 distinct texts, 250 of
  them handed to libyaml; the other 8 hold a `?`, a tab or a later BOM) and every `role_paths:` block of both path maps
  and the planted ones (6 texts): **0 differences** from the pure SafeLoader, product and hook copy alike (same data,
  or the same refusal with the same text).
- **The rule, fuzz:** 24,000 mutated texts (block and front-matter seeds; 12,000 inserting tabs, `?`, `? `, BOMs,
  colons and line breaks, 12,000 over a wider alphabet: flow and block indicators, quotes, anchors, aliases, tags,
  merge keys, NUL and control characters, NEL, LS, `￾`, CR). 8,394 were handed to libyaml. **0 differences** from the
  pure loader, product and hook copy. Raw libyaml without the rule differed on 15,645 (its data or its refusal's text).
- **The product corpus:** the committed 1,190 kept calls plus every `decide` call recorded while `tests/unit/guard/`,
  the role_paths unit suites and the acceptance suites of W2-13, W2-141, W2-148, W2-150, W1-46, W2-59, W1-02, W1-05,
  W2-57 and W2-42a ran: 3,782 distinct calls, replayed on `test_w2_111_plant`'s repository for 4 roles (15,128 answers
  of `decide`, `policy_refusal` and `has_install`) under the base (`803a1af1d2c8`) and the head (`1e455d6d57ce`):
  **0 differences** (7,108 refused, 2,156 by the read rules, 40 installs, on both).
- **The role filter:** `role_paths.caller` for each of the live repository's 250 tickets × engineer and test designer
  (the live map's block, the live tickets, the links stubbed): 500 answers, **identical** on base and head (466
  filters, 34 none, 0 refused).
- **The live-hook corpus:** the same 3,782 calls through the applied copy and the patched copy (`101bee39d5c9`,
  `02a782e31145`) as processes, in the settings.json form (the pinned interpreter, `-E`: configuration A), paired per
  call, for the engineer and the test designer. The plant's path map was given the live repository's `role_paths`,
  `sets_root_hidden`, `session_hidden` and `write_refused` blocks, plus a held-out list. Of 7,564 decisions there are
  **0 differences** in exit code, decision, reason and stderr: 5,966 allowed, 1,590 denied and 8 refused by exit 2 on
  both copies (1,636 s).
- **The fail-opens closed (malformed input only):** each planted text libyaml reads and the pure loader refuses: in
  the product, `section` refuses as the pure loader does; `ticket_front` and so `caller` refuse (designer and
  engineer); `parts._front` gives the line reader's answer as with libyaml absent (a quoted `wbs_id` refuses with the
  ticket fault). Through the hook as processes, on the corpus plant: the five planted fronts (a tab inside, after an
  entry and after the key, a `?` in a flow item, a BOM after a line break) and four planted `role_paths:` blocks (a
  tab inside and after an entry, after the key, a `?` in a flow item), each on three calls (Read of an ordinary file,
  Read of code, `ls`) for the engineer and the test designer: 54 pairs, every one **allowed by the applied copy and
  refused by the patched copy** (exit 2, `could not decide: the session's ticket file cannot be read: its front matter
  is not YAML …` or `could not decide: governance/project/path-map.yaml: role_paths cannot be read`). These are the only
  decisions that change: fail-opens closed. `tests/unit/guard/test_w2_111_yaml_rest.py` keeps one case of each.

**r5, rv-3's F1 (the copy `101bee39d5c9` and the product's `parts.load_yaml_unique`):**

- **The YAML loader:** the equality check and the 40,000-text fuzz are in the `load_yaml_unique` row above, with 0
  differences. Through the hook as a process, with an engineer's Read of an ordinary file: each of the ten divergent
  held-out.yaml texts of `tests/unit/guard/test_w2_111_load.py` is decided the same by the applied copy (the pinned
  pure loader) and by `101bee39d5c9`. Eight are refused with `could not decide: governance/project/held-out.yaml
  cannot be read`, and the BOM inside a later line's key and the key written twice give the same answers on both. The
  copy before the fix (`665614961cd0`) allowed 8 of those 10.
- **The product corpus**, rebuilt: the committed 1,190 kept calls plus every `decide` call recorded while
  `tests/unit/guard/` and the acceptance suites of W2-42a, W1-02, W1-05, W2-84, W2-141 and W2-57 ran. That makes
  3,781 distinct calls (r5's earlier 4,204-call record went with its engineer's sandbox). The calls were replayed on
  `test_w2_111_plant`'s repository for 4 roles, giving 15,124 answers of `decide`, `policy_refusal` and `has_install`
  under three `src` trees: the base (`87c7fe8f3`, integrate, the pure loader), the head before the fix (`4466208f2`)
  and the fix. There are **0 differences** between any two of them (7,108 refused on each). The 1,190 kept calls also
  equal the committed pre-W2-111 answers.
- **The live-hook corpus**, the same 3,781 calls through the applied copy and `101bee39d5c9` as processes. It used the
  settings.json form (the pinned interpreter, `-E`: configuration A), paired per call, for the engineer and the test
  designer. The plant's path map was given the live repository's `role_paths`, `sets_root_hidden`, `session_hidden` and
  `write_refused` blocks, plus a held-out list. Of 7,562 decisions there are **0 differences** in exit code, decision,
  reason and stderr: 5,964 allowed, 1,590 denied and 8 refused by exit 2 on both copies.

**Before r5's F1:**

- **The decision corpus through both copies as processes**, in the settings.json command form (pinned interpreter,
  `-E`: configuration A). The planted repository is `test_w2_111_plant`'s: 155 trees, one nested, one through a link,
  a locked and a gone one, a run clone. Its main-tree path map gets the hook's own blocks (`sets_root_hidden` with
  wildcard globs, `session_hidden`, `write_refused`, `role_paths`) and a held-out list. The calls: 4,204 corpus calls
  (r4's kept 1,190; the calls of `tests/unit/guard/` and of W2-42a's, W1-02's, W1-05's, W2-84's and W2-141's
  acceptance suites, recorded this run) plus 87 hook-only calls at the planted blocks. That is 4,291 calls × 4 roles
  (engineer, test designer, auditor, none) = 17,164 decisions. On the final copy
  (665614961cd0, 543cf1b26701) there are **0 differences** in exit code, decision, reason and stderr: 13,218
  allowed, 3,946 refused and 16 fail-closed on both copies, in 1,050 s. Every rule shows among the refusals (2 hidden,
  2 held-out, 2b write and line, 2c, 2d, 1, 5, rm, 3 secret, 4 sudo and install, g14, R4/R5). An earlier copy had
  also given 0 differences. Product side: `decide`, `policy_refusal` and `has_install` on the 4,204 calls × 4 roles
  before and after `5532c6f80462`: 0 differences.
- **The live hook's unit suite** (`tests/unit/hooks/test_live_hook.py`, pointed at each copy, pinned interpreter):
  62 passed and 1 failed, the same on both copies. The one failure,
  `test_a_removed_worktree_falls_back_to_the_hook_s_own_tree`, comes from the copy's location: the scratch copy is
  in no git tree, and that case uses the hook's own tree.

## Measured (S10, S9): measure.py's method, paired, the live repository

**r5, after P-W2-111-YAML-REST (the copy `101bee39d5c9` / `02a782e31145`), a quick check of 5 cases:** the same
method: before (the live repository's applied hooks, copied) and after (a clean copy with this diff applied)
alternating per sample in the same run, each call with its own reference, the live repository, the recorded 46-entry
session PATH, quiet (load 3.5-2.5). Every case is within 100 ms with the same decision, in the first round; the live
repository's `git status --short` was the same before and after.

| case | before judged | after judged | drop | ref median b/a | CPU p95 b/a | wall p95 b/a | decision | load |
|---|---|---|---|---|---|---|---|---|
| W1-05 Read-engineer | 77.8 | 58.7 | 19.1 | 15.0/14.9 | 92.7/73.5 | 91.3/72.7 | allow → allow | 3.5-3.3 |
| W1-05 Write-engineer | 79.6 | 63.9 | 15.7 | 15.2/15.2 | 94.8/79.2 | 88.2/73.7 | allow → allow | 3.1-2.9 |
| W2-57 test-designer Read ordinary | 84.5 | 71.3 | 13.2 | 15.6/15.6 | 100.1/86.9 | 100.1/86.7 | allow → allow | 2.9-2.9 |
| Bash ls (engineer) | 86.9 | 65.5 | 21.5 | 15.0/15.1 | 101.9/80.5 | 152.3/78.6 | allow → allow | 2.9-2.6 |
| Bash pipeline (engineer) | 93.0 | 68.6 | 24.3 | 15.2/15.4 | 108.1/84.0 | 158.0/78.4 | allow → allow | 2.6-2.5 |

The engineer's role-checked calls now also read and parse the session ticket's front matter (`judges`, row above):
the live ticket's front holds no tab, `?` or BOM, so libyaml parses it. Against the F1 copy's run (a different run,
one round each): Read-engineer 58.7 (61.1), Write-engineer 63.9 (65.5), Bash ls 65.5 (71.6), Bash pipeline 68.6
(67.5), and the test designer's Read 71.3 (63.4). The designer's path read and parsed the front before this change
too (`{ticket_impl}`); its only change is the parser choice, libyaml for this front as before. Its 7.9 ms rise is
not explained by the code; its paired before figure rose too (84.5 against 78.1).

**r5, after F1 (the copy `101bee39d5c9`), a quick check of 5 cases:** measure.py's method, before (the live
repository's applied hooks) and after (a clean copy with this diff applied) alternating per sample in the same run,
each call with its own reference. The live repository was used, with the recorded 46-entry session PATH. Every case is
within 100 ms with the same decision, in the first round. The live repository's `git status --short` was the same
before and after.

| case | before judged | after judged | drop | ref median b/a | CPU p95 b/a | wall p95 b/a | decision | load |
|---|---|---|---|---|---|---|---|---|
| W1-05 Read-engineer | 83.5 | 61.1 | 22.3 | 15.1/15.1 | 98.6/76.3 | 96.2/74.6 | allow → allow | 3.7-3.3 |
| W1-05 Write-engineer | 78.6 | 65.5 | 13.1 | 15.5/15.7 | 94.1/81.2 | 92.0/79.3 | allow → allow | 3.3-3.1 |
| W2-57 test-designer Read ordinary | 78.1 | 63.4 | 14.6 | 15.5/15.4 | 93.6/78.8 | 91.5/77.1 | allow → allow | 3.1-2.8 |
| Bash ls (engineer) | 94.2 | 71.6 | 22.7 | 15.8/15.7 | 110.1/87.3 | 170.8/87.2 | allow → allow | 2.8-2.6 |
| Bash pipeline (engineer) | 90.8 | 67.5 | 23.3 | 15.5/15.8 | 106.3/83.3 | 158.9/83.2 | allow → allow | 2.6-2.6 |

The live files parse through libyaml as before: neither `governance/project/held-out.yaml` nor `path-map.yaml` holds
a tab, a `?` or a BOM.

**Before r5's F1 (the copy `665614961cd0`):**

The method is `~/gov-os-runs/W2-111/gf6-measure/measure.py`'s, copied: the reference hook, the settings command
through `sh -c`, RUSAGE_CHILDREN deltas, 3 warm-up calls, rounds of 40, judged = nearest-rank p95(CPU) −
median(reference CPU), best of 3 rounds. The before and after copies alternate per sample in the same run. The
repository, its config and the targets are the live repository's (38 worktrees, 55 run clones). PATH is the real
session PATH recorded by the lead, 46 entries (27 under `/mnt/c`). The engineer's sandbox inherited only 5 entries,
so the recorded one was used and not shortened. The live repository's `git status --short` was the same before and
after (empty).

**Configuration A, quiet** (load 1.5-7.8; the last case had a load burst, to 7.8, and its rounds spread): the
pinned 0.1.0 gov as is, which is what ACT-GUARD-FIX-7 alone gives.

| case | before judged | after judged | drop | ref median b/a | CPU p95 b/a | wall p95 b/a | load |
|---|---|---|---|---|---|---|---|
| W1-05 Edit-engineer | 72.9 | 57.9 | 15.0 | 14.7/14.7 | 87.7/72.6 | 87.3/72.4 | 5.2-6.0 |
| W1-05 Glob-engineer | 78.9 | 63.3 | 15.6 | 15.4/15.3 | 94.4/78.6 | 94.3/78.5 | 5.0-6.6 |
| W1-05 Glob-no-role | 52.0 | 47.9 | 4.1 | 14.7/14.8 | 66.7/62.7 | 67.0/63.2 | 5.2-6.5 |
| W1-05 Grep-engineer | 77.6 | 58.0 | 19.7 | 15.0/15.0 | 92.6/72.9 | 92.0/72.5 | 4.0-5.2 |
| W1-05 Grep-no-role | 52.6 | 48.7 | 4.0 | 15.0/15.0 | 67.6/63.7 | 67.6/63.6 | 3.5-4.0 |
| W1-05 NotebookEdit-engineer | 73.5 | 57.1 | 16.5 | 15.1/15.1 | 88.6/72.1 | 88.4/71.8 | 3.1-3.5 |
| W1-05 Read-engineer | 74.6 | 57.8 | 16.8 | 14.8/15.0 | 89.3/72.8 | 90.2/72.9 | 2.8-3.1 |
| W1-05 Read-no-role | 53.9 | 48.8 | 5.1 | 15.0/14.8 | 68.9/63.6 | 69.0/63.7 | 2.5-2.8 |
| W1-05 Write-engineer | 72.2 | 55.6 | 16.6 | 14.8/15.0 | 87.1/70.6 | 87.0/71.4 | 2.3-2.5 |
| W1-02 no-role Write (scratch) | 56.4 | 50.3 | 6.1 | 14.9/15.0 | 71.3/65.3 | 71.9/65.8 | 2.3-2.7 |
| W1-02 engineer Write src (allow) | 72.0 | 56.2 | 15.8 | 14.9/14.8 | 86.9/71.1 | 86.8/71.0 | 2.4-3.0 |
| W1-02 engineer Write acceptance (deny r1) | 73.2 | 57.0 | 16.3 | 14.7/14.8 | 88.0/71.7 | 87.7/71.5 | 2.6-3.0 |
| W1-02 test-designer Write acceptance | 70.5 | 54.0 | 16.6 | 14.6/14.5 | 85.1/68.5 | 85.6/69.2 | 2.0-2.6 |
| W1-02 auditor Write src (deny r5) | 70.5 | 55.4 | 15.1 | 14.6/14.5 | 85.1/69.9 | 84.7/69.7 | 1.7-2.0 |
| W2-57 test-designer Read ordinary | 72.0 | 58.4 | 13.6 | 14.7/14.8 | 86.7/73.2 | 86.5/73.9 | 1.7-1.8 |
| Bash ls (engineer) | 81.2 | 59.6 | 21.6 | 14.8/14.9 | 96.0/74.5 | 144.1/74.1 | 1.6-1.8 |
| Bash pipeline (engineer) | 82.6 | 60.2 | 22.4 | 14.8/14.8 | 97.4/75.0 | 146.9/75.5 | 1.5-1.8 |
| Bash write to scratch (engineer) | 82.9 | 61.4 | 21.5 | 14.8/14.8 | 97.7/76.2 | 145.6/76.3 | 1.5-1.9 |
| Bash git status (CTO) | 78.2 | 58.5 | 19.7 | 14.9/14.9 | 93.1/73.5 | 144.5/73.1 | 1.6-1.9 |
| Bash grep\|wc (test-designer) | 118.6 | 81.4 | 37.2 | 15.3/15.3 | 133.9/96.7 | 184.6/96.2 | 1.9-7.8 |

An earlier run of configuration A at load 3.5-20 (not quiet, kept for the record) gave after 47.8-78.6, drop
3.4-26.1:

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

Quiet, in configuration A, every one of the 20 cases is within 100 ms (after 47.9-81.4 ms; before 52.0-118.6). On
wall time, the PATH-once check brings Bash from about 145 to about 75 ms. **S9's 30 ms is not reached: the drop on
the 15 mapped cases is 4.0-19.7 ms quiet** (13.6-19.7 for the role-checked ones, 4.0-6.1 for the no-role ones).

What remains is not the hook's own code. Of an after call's ~72 ms of process CPU (quiet, engineer Read), about 15 ms
is the interpreter (the reference), about 27 ms is the pinned gov's import chain (`gov.guard.reads` 11.9 ms with
`decide`, `runs`/pathlib, `bash_writes`, `protected`), 6.8 ms is `import yaml` (the pure-Python package loads even
for CSafeLoader), and 6-9 ms is compiling the 84 KB `pretooluse.py` (a script run as `python file` is never cached).
The git children take 4.5 ms (`worktree list`, `remote get-url`, `rev-parse`). The no-role calls drop only 3-5 ms
because they build no hidden parts: their cost is mostly those imports. See the engineer's return,
`proposed_decisions`/`unresolved`, for the options.

**Configuration B** (load 2.2-9.6): the after copy with the gov of the W2-111 tree's `src`, which is what it gives
after 0.1.1. It is the pinned interpreter run without `-E`, with `PYTHONPATH=<tree>/src`, paired against the same
before copy in A. Every case is within 100 ms (after 45.5-73.0); the drop is 8.2-25.4 ms, also short of 30.

| case | before judged | after judged | drop | ref median b/a | CPU p95 b/a | wall p95 b/a | load |
|---|---|---|---|---|---|---|---|
| W1-05 Edit-engineer | 80.8 | 58.4 | 22.4 | 15.8/15.8 | 96.6/74.2 | 97.0/73.9 | 7.9-9.6 |
| W1-05 Glob-engineer | 77.1 | 57.9 | 19.3 | 15.8/15.8 | 92.9/73.7 | 93.3/73.3 | 6.4-7.9 |
| W1-05 Glob-no-role | 54.9 | 46.7 | 8.3 | 15.6/15.6 | 70.5/62.2 | 70.9/62.1 | 5.4-6.4 |
| W1-05 Grep-engineer | 78.8 | 58.8 | 20.1 | 15.5/15.5 | 94.4/74.3 | 94.0/74.0 | 4.4-5.4 |
| W1-05 Grep-no-role | 56.5 | 47.9 | 8.6 | 15.4/15.4 | 71.9/63.2 | 71.9/63.3 | 3.8-4.2 |
| W1-05 NotebookEdit-engineer | 76.9 | 55.0 | 21.8 | 15.4/15.3 | 92.3/70.3 | 92.3/70.4 | 3.2-3.8 |
| W1-05 Read-engineer | 78.1 | 56.3 | 21.8 | 15.3/15.1 | 93.4/71.4 | 93.1/71.2 | 2.8-3.2 |
| W1-05 Read-no-role | 57.0 | 47.5 | 9.6 | 15.3/15.2 | 72.3/62.7 | 72.2/62.6 | 2.5-2.8 |
| W1-05 Write-engineer | 76.4 | 55.5 | 20.9 | 15.3/15.4 | 91.7/70.9 | 91.8/70.9 | 2.3-2.5 |
| W1-02 no-role Write (scratch) | 53.7 | 45.5 | 8.2 | 15.1/15.3 | 68.8/60.7 | 69.5/60.6 | 2.2-2.3 |
| W1-02 engineer Write src (allow) | 73.4 | 54.6 | 18.8 | 14.8/14.9 | 88.3/69.6 | 88.3/68.9 | 2.2-3.2 |
| W1-02 engineer Write acceptance (deny r1) | 82.2 | 65.3 | 17.0 | 15.3/16.3 | 97.5/81.5 | 97.8/82.1 | 3.2-4.7 |
| W1-02 test-designer Write acceptance | 72.6 | 54.4 | 18.2 | 14.9/15.0 | 87.5/69.5 | 87.2/69.2 | 4.1-5.3 |
| W1-02 auditor Write src (deny r5) | 85.9 | 63.2 | 22.7 | 15.9/15.8 | 101.8/79.0 | 101.5/78.7 | 5.1-5.8 |
| W2-57 test-designer Read ordinary | 84.1 | 62.8 | 21.2 | 16.3/15.2 | 100.3/78.1 | 99.8/77.9 | 5.8-6.6 |
| Bash ls (engineer) | 97.3 | 71.9 | 25.4 | 15.8/16.0 | 113.1/87.9 | 176.1/88.7 | 6.6-8.0 |
| Bash pipeline (engineer) | 94.3 | 73.0 | 21.3 | 15.2/15.1 | 109.5/88.1 | 165.0/87.8 | 6.3-8.0 |
| Bash write to scratch (engineer) | 88.4 | 66.5 | 21.9 | 15.0/15.5 | 103.4/82.0 | 156.9/81.9 | 5.4-6.3 |
| Bash git status (CTO) | 86.9 | 64.0 | 22.8 | 15.2/15.4 | 102.1/79.5 | 157.6/79.5 | 5.3-5.9 |
| Bash grep\|wc (test-designer) | 86.8 | 64.5 | 22.3 | 15.2/15.2 | 102.0/79.7 | 157.1/80.4 | 4.5-5.4 |
