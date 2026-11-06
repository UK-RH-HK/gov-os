# The sets-root guard (DEC-1082 (3)): the rehearsal of 2026-11-06

`rehearse.sh` ran every step in order, in one run, from a fresh `env -i` shell, 12:03:36–12:08:03 GMT, and ended with 0 failures. Its output is
in `rehearsal.log` beside this file. Nothing live was changed.

## The files
| File | sha256 (first 12) | What |
|---|---|---|
| `pretooluse.candidate.py` | `42749e673c50` | the live hook (`e406653ef6c9`) with spec B applied (B.1–B.4), nothing else |
| `pretooluse.diff` | `892acd89715b` | its unified diff against the live hook, 158 lines |
| `path-map.patch` | `d8351eb83bab` | spec A's block after line 544; the map goes `cc8139a1c8f4` → `da095dce9171` |
| `guard4_check.candidate.py` | `12af75e62a82` | the live check, plus spec C's script changes and its 194 sets cases in `SETS` |
| `apply.sh` | `39c61ed11919` | `check`, `apply` and `undo` of the two files |
| `rehearse.sh`, `replay_sets.py` | — | the rehearsal and its replay |

- **The 70 existing cases are unchanged.** `CASES` stays the 70, compared equal with the live check's. The new cases
  are kept in a list of their own, because `test_guard_fix_3.py` executes the check up to `ok = True` and takes `CASES`.
- **`apply.sh` finds its tree from where it sits.** It acts only on the tree holding it, so the clone's copy cannot
  touch the main tree. `check` and `apply` stop unless both files hash as built. `undo` restores the files from the
  backups, then checks them byte for byte.

## Every name the spec's code uses
These exist in the hook and the pin (`pin-8284fb408bd4`) at the lines the spec gives: `reads._hidden` (470),
`reads._Part` (151), `held()` (203), `inside()` (182), `listing()` (1365–1385), `RUNTIME_REFUSAL` (101), the
`[["cat", "--"]]` stand-in (1327, 1332), `_related` (283), `_paths_ok` (405) and `reads._expand_token` (imported,
31). `heldout.load_yaml_unique` is at line 29. In the hook, `tree_roots`, `WRITE_TOOLS`, `bash_writes_of`, `HOME`
and `main_tree` (182–194) are where the spec says, and so are lines 363–375, 382 and 544/545.

One line has moved: `loader.py`'s `validate` is now at 241, and `_validate_path_map` at 291–309. The spec's claim
still holds: there is no check for an unknown key. The patched map passes `load_config`, `check_sets` and
`role_reads.section`.

## The results
| Step | Result |
|---|---|
| Clone | `--no-hardlinks` clone at `aa999aa607ce` (w2/integrate; the two files are unchanged since `8b85bbb90`), 66 branches, 0 root mentions left |
| Planted root | `~/gov-os-runs/SETS-rehearsal/home/gov-os-eval`: 10 dummy files, no `.git`. Its map is a stub that copies the repository's `evaluation_sets` |
| Suites before (the hook as it is) | `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped |
| `apply.sh check`, `apply` | both hashes as built; applied; backups and `SHA256SUMS` written |
| **R2** (HOME substituted, the block as applied, `GUARD4_ONLY=sets`) | **194 run, 0 failed, PASS** |
| **R1** (the registered line, the block's root planted) | **250 run (70 + 180), 0 failed, PASS**. The 14 cases that name `~` or `$HOME` are skipped here; they run in R2 |
| R1, L cases only (what the live tree runs after the ACT) | 203 run (70 + 133), 0 failed, PASS |
| Override switched off | exactly 6 fail: M6, M7, and X1 and X2 for the engineer and the orchestrator. That is the spec's "deny without it" |
| Suites after (the candidate, with the block) | `test_guard_fix_4.py` 467 passed; `test_g14.py` 151 passed, 1 skipped (the same as before) |
| Replay | 3,612 unique calls: 3,582 allow→allow, 5 deny→deny, **25 allow→deny**, 0 deny→allow (below) |
| Measure check | `_measured` per set, `GOV_ROLE=orchestrator`: all False; `GOV_ROLE=engineer`: all True (the control) |
| Writer session | `claude -p --model haiku` in `writer/`, with the clone and the planted root added, Read only: exit 0. 1 Read, no error, it returned the planted line; 0 hook events (no guard runs there) |
| `apply.sh undo` | from the applied state: both files back to `e406653ef6c9` and `cc8139a1c8f4`, `cmp` equal to the backups, `git diff` clean |
| Live files | the hook `e406653ef6c9` and the map `cc8139a1c8f4`, before and after; the real root's entry unchanged: **unchanged** |

## Where a case's answer is not the spec's
- **W8, the independent reviewer:** deny, not allow. Rule 5 already refuses every reviewer write outside its records,
  its scratch and `/tmp`; this change plays no part. The case expects deny and checks for rule 5's reason. W8 for no
  `GOV_ROLE` and for ticket-lead is allow, as the spec says.
- **`test_g14.py`:** 151 passed and 1 skipped, not the spec's 146. ACT-G14b added cases (see its log). The count is the
  same before and after the change.
- **The 14 cases that name `~` or `$HOME`** (B2, B3, G3, M1, M2, M6, M7, X5) run only when the block's root is
  `~/gov-os-eval` as the current HOME expands it: in R2 here, and on the live tree after the ACT. In R1 they would name
  the real root, so they are skipped.

## The replay
**What it judged.**
- The source: the tool calls of the last 48 hours, from the transcripts of the main tree's and the worktrees'
  sessions. Only their inputs were read, never a tool result.
- The rewrite: every spelling of `~/gov-os-eval` became the planted root, and the main tree became the clone.
- The comparison: each call was judged by the hook as it is and by the candidate, with the clone as the project.
- The counts: 3,724 calls, 84 duplicates, 3,612 judged, 154 of them naming the sets root. 28 were skipped: they name
  the real root in a form the rewrite cannot place.

**The 25 that the change refuses.** Each names the sets root's hidden folders, or a folder above them. No call that
does not name the sets root changed.

| Cause | Calls | What they are |
|---|---|---|
| The shell's own words name a hidden path | 21 | the CTO's own work on the hidden sets, by its sessions and subagents (auditor 12, test designer 1): reads and listings for the cross-check and for checking hidden domains, `repin_gold.py` and `leak_check.py` on hidden folders, and `ls` or `stat` of hidden folders (names only). These are refusals the rule means to make. |
| Only words inside a heredoc body | 4 | `python3 - <<'EOF'` scripts that write the ACT-MSET-2 and ACT-MSET-3 packages, whose text names the hidden paths. With the bodies blanked, all 4 are allowed. One is refused as a run-time listing: the judge takes backticks in the body as command substitution. The bodies were not read, so whether a body opens a hidden file was not checked. Most likely these are **false refusals**. |

The 24 hidden refusals give `HIDDEN_REFUSAL`, and the 1 run-time refusal gives `RUNTIME_REFUSAL`.

## Limits
- **The real `~/gov-os-eval`:** only its root's own entry was taken (inode, size, mtime and ctime), before and after.
  Nothing under it was opened or listed, so its contents are not hashed.
- **The planted map:** a stub. The real sets root's map was not read, so the measure check assumes it lists
  `measures.roles` as the repository's map does.
- **The replay's roles** are inferred from each session's first message, as in G-14's `replay.py`, and every call ran
  with `GOV_TICKET=DAEO-sdxk`. Because both hooks judged the same events, every difference comes from the change.
- **The writer check** shows only that a session outside the repository runs no guard: the user settings hold no
  hook, and `--add-dir` does not bring in the clone's hook. It does not check the guard inside such a session.
