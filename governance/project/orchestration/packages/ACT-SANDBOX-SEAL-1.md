# ACT-SANDBOX-SEAL-1: the sandbox experiment's held-out halves sealed by a path-map entry (DEC-1099 (1) Q6)

- **For:** the owner. **Applied inside ACT-INDEP-WALLS-1** (DEC-1101 (2)-(3): one ACT for the path map, the guard and
  the folders' settings), not by a separate operator step. This package is a component of that ACT: its patch, its
  hashes, its guard cases and its rehearsal.
- **By:** a research agent for the CTO, 2026-11-09. Built and rehearsed in a clone; **nothing live is changed.**
- **Sources:** SANDBOX-GUARD-EXP-1 §1, §2 (b), §4, §7 Q6; DEC-1099 (1); DEC-1101 (2)-(3); DEC-1082 (3), DEC-1097 (2)
  (the sets root and its line rule); DEC-820 (d); ACT-GUARD-SETS-1 (applied, `15952bbf`); the live hook
  `.claude/hooks/pretooluse.py` (`bd545af83198`) and the path map (`a9d8b97267c4`).

## 1. What it seals, where, and why there
- **What:** the experiment's held-out halves: the real replay's held-out half, the second planted writer's cases, the
  labels of both, and the one held-out run's results. The tuner must never see them (package §4).
- **Where:** `<sets root>/fixtures/evaluation/sandbox-guard-exp-1/hidden/` (the sets root is `~/gov-os-eval`). The
  tuning halves stay open in `~/gov-os-runs/SANDBOX-GUARD-EXP-1/tuning/`.
- **Why there:**
  - it is outside every tree: no worktree, no run clone, no branch can carry it, and git never sees it;
  - it is the one root outside the repository the live hook already guards (rules 2 and 2b): a path-map entry seals
    it with **no hook change**, the line rule included (a line naming the root with `sandbox-guard-exp-1/hidden` is
    refused);
  - the sessions outside the guard (the writers and labellers, DEC-1101 (2)) already write there, as ACT-MSET-3/4's
    writers did;
  - the harness reads and writes it only from its own code, with `--sets-root <root>` alone on its line, as the
    measure and the fresh-80 scripts do (DEC-1097 (2)).

## 2. The change: one file, two blocks (`drafts/sandbox-seal/path-map.patch`)
1. **`evaluation_sets`** gains `sandbox-guard-exp-1`: `visible: []`, `hidden:
   ["fixtures/evaluation/sandbox-guard-exp-1/hidden/**"]`, measuring `engineer, research, product-spec,
   independent-test-designer, independent-auditor`. Each of those roles, the tuner (an engineer) included, is refused
   the glob under the sets root and in every tree (the hook's `_hidden` from the main tree's map).
2. **`sets_root_hidden.hidden`** gains the same glob, so the six refused roles (the **orchestrator** too: the CTO and
   every lead) are refused it as well. The CTO briefs the tuner, and wrote earlier guard code, so it never sees them.

**Not changed:** the hook, `role_reads.py`, `bash_writes.py`, the settings, the sets root's own map. The measure is
unaffected: `_measured` is False for the orchestrator, True for the measured roles (checked).

| File (`.gov-runtime/scratch/orchestrator/drafts/sandbox-seal/`) | sha256 |
|---|---|
| `path-map.patch` (the map `a9d8b97267c4` → `ef9952e9ea4f`) | `906544ac4afb3543414e44d01b5a06e356ca0a9b9476b912134c0146965a2df6` |
| `apply.sh` (`check`, `apply`, `undo`, with a backup and sha256s; stops unless the hook is still `bd545af83198`) | see `SHA256SUMS` after the CTO's review |
| `seal_check.py` (the seal's guard cases) | as above |
| `rehearse.sh`, `replay_seal.py` (the rehearsal and its replay) | as above |

For ACT-INDEP-WALLS-1's author: apply `path-map.patch` to the map as that ACT's map step. `apply.sh check` shows the
state, and its `apply` and `undo` are a tested route for this part alone. If the walls ACT also patches the map, rebase
this patch onto that ACT's map and re-run `seal_check.py` (R1 and R2) and the rehearsal's replay.

## 3. Requirements this seal places on ACT-INDEP-WALLS-1 (the CTO's decision, 2026-11-09)
1. **The tuning session is denied `~/.claude/projects/**`** (the raw transcripts) **and the sealed folder** by its
   settings, the guard and its wall. Without this, the tuner could rebuild the real held-out half from the transcripts:
   the split's secret salt hides which sessions are held out, not what they did.
2. **The second writer and the labellers write into the sealed folder** from their walled folders, outside the guard.
   They return counts and sha256 digests only.
3. **No session the guard judges is given an exception** to read the sealed folder. The held-out run reads it through
   the harness's own code (`--sets-root` only).
4. **The seal is applied before the second writer writes and before the extractor writes the held-out half.**

## 4. The guard cases (`seal_check.py`, 179 cases over the roles)
- **Refused** to every measured role, the CTO, a lead, the CTO's subagents and the tuner (an engineer on W2-56):
  - a Read, `cat`, `head`, `ls`, `wc`, `grep -rn`, inline code, Grep and Glob of the sealed folder (names that do not
    exist, and planted files);
  - writes into it: Write, `echo >`, `cp`, and `mkdir` with a write (the auditor already by rule 5);
  - the same glob in this tree and in a worktree;
  - the line rule: the root named together with the sealed folder, in the `~`, `$HOME` and absolute spellings.
- **Allowed:**
  - the harness's own lines (`--sets-root <root>` alone, a bare set name, variables only before the root), to the CTO
    and a lead;
  - the sessions no rule names (no `GOV_ROLE`, `ticket-lead`);
  - a sibling file of the sealed folder, a names-only listing of its parent, and the tuning folder.
- `SEAL_EXPECT=before` checks the gap on the map before the patch: every case the seal adds is then an allow
  (127 cases).

## 5. The rehearsal (`REHEARSAL` in `rehearsal.log`; the first run in `rehearsal-first-run.log`)
The clone is a `--no-hardlinks` clone of `w2/integrate`, with a planted sets root (18 dummy files, the sealed folder's
three kinds included) and a worktree. The real sets root was never opened: only its own stat line was taken. The first
run, 01:14–01:22 GMT, gave:

| Step | Result |
|---|---|
| Gap (before the patch, HOME planted) | seal cases **179 run, 0 failed** (127 deny-after cases allowed before); guard4 sets cases 527, PASS |
| Suites before / after | `test_guard_fix_4` 467 passed; `test_g14` 151 passed, 1 skipped; W2-58 sets, launcher, live hook, reads 105 passed: the same |
| `apply.sh check`, `apply` | every hash as built; applied |
| R2 (HOME planted, the block as applied) | guard4 sets **527, PASS**; seal **179, 0 failed, PASS** |
| R1 (the registered hook line, root planted) | guard4 **501, PASS** (96 `~` cases run in R2); seal **165, PASS** (14 in R2) |
| Replay (48 hours to the start, the map before and after) | 5,402 unique calls: 5,365 allow→allow, 37 deny→deny, **0 changed** |
| Measure check | `_measured`: orchestrator False, engineer True, research True, ticket-lead False |
| `apply.sh undo` | the map byte for byte as before |
| Live files and the real root's entry | **unchanged** |

The first run's one failure was in the rehearsal's own check (the schema validator could not resolve the schema's
relative `$ref`), not in the map: `load_config` and `check_sets` passed. The step now validates as W2-58's
`schema_validator` does.

**The clean run, 01:23–01:31 GMT (`rehearsal.log`): 0 failures.**
- Gap: 179 run, 0 failed; guard4 527, PASS.
- Schema: patched map 0 errors, `load_config` and `check_sets` ok.
- R2: guard4 527, PASS; seal 179, PASS. R1: guard4 501, PASS; seal 165, PASS.
- Suites: 467, 151 + 1 skipped, 105 before and after.
- Replay: 5,571 unique calls (5,532 allow→allow, 39 deny→deny), **0 changed**.
- `_measured`: as in the first run. `undo`: byte for byte. Live files: **unchanged**.

## 6. Costs and limits
- **Cost:** none at run time (no hook change); about 1 s per rehearsal case.
- **The line rule's quoted-name check** gains no new word (`'hidden'` was already a key, through memory-retrieval).
- **Limits** are the ones ACT-GUARD-SETS-1 states: a root spelled in pieces, a positional parameter, and a write the
  guard cannot resolve. Requirement 1's wall closes the transcripts route, which the guard alone does not.

**Basis:** question 2 (the held-out halves sealed by walls, not by trust, DEC-1101 (2)).
