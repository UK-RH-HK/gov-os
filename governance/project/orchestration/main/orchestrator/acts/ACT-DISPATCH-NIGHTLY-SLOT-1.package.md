# ACT-DISPATCH-NIGHTLY-SLOT-1: the dispatcher counts the nightly's own suite run as in a slot (incident 2026-11-13-0456)

- **For:** the owner (one yes line), then **the CTO** applies it (class (b): `dispatcher.py` is a `watchers` control path,
  `act_class.py` gives b) after one independent review (verdict block in `review.md`).
- **By:** an ACT-preparation helper of the CTO, 2026-11-13 from about 11:15 UTC. **Nothing live was changed or started:** no
  commit, no stage, no write to the dispatcher's code or state, nothing in the main tree's tracked files, nothing in
  `~/gov-os-runs`, no real heavy-slot file opened. Built and rehearsed on a fresh clone of `w2/integrate` and planted folders
  under `/tmp/claude-1000/` (section 4). **Not yet independently reviewed** (section 8).
- **Under:** **DEC-1163 (9)** (the owner, 2026-11-13: "Yes to two ACTs: ... the dispatcher's outside-slot check reading the
  nightly's slot locks as in-slot (each built, reviewed and brought with its yes line)"); **DEC-984** (the nightly takes
  every heavy slot itself, by flock on descriptors); **DEC-1159 (1)** (the nightly beside the leads, so the false finding
  fires every night); **DEC-1038 (4)** (no heavy step outside a slot). The manifest's `dec`: "DEC-1163 (9), DEC-984,
  DEC-1159 (1), DEC-1038 (4)".
- **Drafts:** `.gov-runtime/scratch/orchestrator/drafts/act-dispatch-nightly-slot-1/` (`dispatcher.py` the after,
  `dispatcher.py.before`, `dispatcher.diff`, `checks.json`, `check_bed.py`, `probe_live.py`, `planted/nightly/nightly.sh`,
  `rehearse.sh`, `build_manifest.py`, `followup-tests.diff`). **The bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-DISPATCH-NIGHTLY-SLOT-1/`.

## 0. The short version, the yes line, and who applies it

1. **The cause (incident 2026-11-13-0456):** `nightly.sh` holds the three heavy slots itself (`exec {sfd}>/tmp/gov-os-heavy-slot-<n>.lock;
   flock -w N $sfd`, DEC-984) and runs its suites through `heavy_slot.sh --held`, which `exec`s pytest. So no ancestor of the
   suite's pytest names a slot lock or `heavy_slot.sh`, and the dispatcher's `in_slot` (dispatcher.py:727) calls it a heavy step
   outside a slot. Admission then refuses every lead start while the nightly runs ("never while a heavy step runs outside a slot",
   dispatcher.py:1253) and an outside-slot incident opens each night.
2. **The change (one file, 47 lines added, 1 rewritten):** `governance/project/orchestration/tools/dispatch/dispatcher.py`.
   `in_slot`, when no ancestor names a slot, returns `nightly_in_slot(by_pid, f)`, which is true **only when all three hold**:
   - the process works in a clone under the nightly's run folder (`NIGHTLY_RUNS`, nightly.sh's `RUNS`,
     `/home/<user>/gov-os-runs/W2-00/nightly/<stamp>`; `DISPATCH_NIGHTLY_RUNS` for the tests);
   - the orchestrator's `NIGHTLY-RUNNING` is under 360 minutes old (`NIGHTLY_FRESH_S`, nightly.sh's own rule for a live marker);
   - an ancestor is `.../nightly/nightly.sh` **holding a heavy-slot lock on its own descriptor** (`holds_slot_lock`): one of its
     fds (`/proc/<pid>/fd`) links to a slot file (`SLOT_GLOB`) and that fd's `/proc/<pid>/fdinfo` carries an exclusive `FLOCK`
     line. The lock table cannot be used: it names the `flock` program that took the lock, which is gone, and in this pid
     namespace it hides the line altogether (measured: section 1).
   A nightly that holds no slot, a stale or missing marker, a run outside the clone, or a heavy step under no nightly.sh stays
   outside, as before. Nothing else changes: `in_slot` is read only by `heavy_outside_slots`, which feeds the outside-slot
   finding, its incident and admission. The new functions only read `/proc` and stat the marker (check 2 refuses `subprocess`,
   `kill`, `fcntl`, `write`, `unlink`, `mkdir`, `rmtree`, `open(` in them).
3. **The follow-up (after the apply):** `followup-tests.diff`, nine cases appended to `tests/unit/orchestration/test_dispatcher.py`
   (one file, class (O) for an ACT, so not in `touched`; the CTO's route). Two of them are red on the before, so they land
   after the apply. Note: the file's parametrised case runs all its rows only with `--optin=lifted,breadth` (tests/conftest.py's
   `rep:` rule keeps the first row otherwise).

**The owner's line: `yes ACT-DISPATCH-NIGHTLY-SLOT-1 9ff4f275`** (the first 8 digits of the manifest's sha256, section 7).

**Who applies it:** class (b): **the CTO**, by hand, after one independent review and the owner's yes:
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
G=.gov-runtime/scratch/orchestrator/acts/ACT-DISPATCH-NIGHTLY-SLOT-1
bash $G/apply.sh check     # exit 0: "state before (sha256 dd5e57e2d94b)"
bash $G/apply.sh apply     # exit 0: "state applied (sha256 cda0af7196c8)"
bash $G/apply.sh verify    # exit 0
git add governance/project/orchestration/tools/dispatch/dispatcher.py
git commit -m "ACT-DISPATCH-NIGHTLY-SLOT-1: the dispatcher counts the nightly's own suite run, under the slots nightly.sh holds, as in a slot (incident 2026-11-13-0456)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1163" --trailer "Role: orchestrator" -- governance/project/orchestration/tools/dispatch/dispatcher.py
```
The next dispatcher pass (cron each minute) reads the new file; the apply replaces it by `mv`, so a pass already running keeps
the code it loaded. Then the follow-up tests by the CTO's route (`git apply $G/followup-tests.diff`).

## 1. What was found (file and line)

- `governance/project/orchestration/nightly/nightly.sh:168-191`: the slots taken on the script's own fds; `:201-203` the suites
  run through `bash heavy_slot.sh --held <slots>`; `heavy_slot.sh:136` `exec`s the command, so pytest's parent is nightly.sh
  itself (it `cd`s into the clone at `:113`; its clone is `$RUNS/$STAMP`, `RUNS=/home/<user>/gov-os-runs/W2-00/nightly`, `:30`).
- `dispatcher.py:727-737` `in_slot`: an ancestor's argv naming `gov-os-heavy-slot`, `heavy_slot.sh`, `rebuild_slot.sh` or
  `verify_lock.sh`; `:768-775` `heavy_outside_slots`; `:244` the pass; `:1253` admission; `:2931` the outside-slot target.
- Measured (2026-11-13, this kernel): a lock taken by `flock <fd>` on a shell's fd is **absent from `/proc/locks`** (the taker
  has exited; this pid namespace hides it), and `/proc/<shell>/fdinfo/<fd>` shows it as
  `lock:	1: FLOCK  ADVISORY  WRITE 0 <dev>:<ino> 0 EOF`. Hence `holds_slot_lock` reads fd and fdinfo, not the lock table.
- The incident record (`log/incidents/2026-11-13-0456-outside-slot.md`): pytest pid 1924933, cwd
  `~/gov-os-runs/W2-00/nightly/20261113-0404`, 20 minutes; lead W2-88 running; the CTO's Fix line asked for exactly this.

## 2. The change (after minus before)

`drafts/act-dispatch-nightly-slot-1/dispatcher.diff`: two constants after `PROC` (`NIGHTLY_RUNS`, `NIGHTLY_FRESH_S`); `in_slot`'s
docstring and last line (`return nightly_in_slot(by_pid, f)` in place of `return False`); `holds_slot_lock(pid)` and
`nightly_in_slot(by_pid, f)` after it. No other line of the file changes.

## 3. The checks (manifest; none names a live HOME or repository path)

1. the file parses (`ast.parse`);
2. the shape: each new function once and called once, `in_slot` ends in the new return, `NIGHTLY_FRESH_S = 360 * 60`,
   `NIGHTLY_RUNS` read from `DISPATCH_NIGHTLY_RUNS` with a default matching `/home/[A-Za-z0-9_.-]+/gov-os-runs/W2-00/nightly`
   (a pattern), `heavy_outside_slots`' test line unchanged, the order of the functions, and no write or kill in the new code;
3. a behaviour bed (`check_bed.py`, inlined): the module loaded in a temp folder with planted `/proc` fd and fdinfo entries,
   slot files, marker and run folder: the nightly's run is in a slot; each of eight conditions taken away (no marker, a marker
   361 minutes old, no lock line, a non-slot file, a run outside the run folder, the run folder itself, a script that is not
   nightly.sh, no nightly parent) leaves it outside; a heavy step elsewhere is still named beside it; a step under
   `heavy_slot.sh` is still in a slot.
On the before, checks 2 and 3 exit 1 (rehearsal B2); on the after, all exit 0 (B9).

## 4. The rehearsal (`rehearsal.log`, last line `failures: 0`)

`rehearse.sh <bed> <repository>`, bed under `/tmp/claude-1000/`, every pytest through `heavy_slot.sh` with `TMPDIR` in the bed:
A. the bundle's hashes; B. a fresh clone of `w2/integrate`: check, the checks before, apply, mode kept, verify, apply again,
only the dispatcher changed, the checks after; C. **a planted nightly, live**: a stand-in `.../nightly/nightly.sh` with
nightly.sh's exact slot form (`exec {sfd}>`, `flock -w`, the suite run with the fds closed) on planted slot files (it refuses
`/tmp`'s real ones; C2 checks no planted process opened one), a planted marker and run folder, the suite a sleeper whose argv
reads `python3 ... -m pytest tests`; the real `/proc` read by the frozen before and after copies: before **outside** (the
incident reproduced), after **in a slot**; marker absent, marker 361 minutes old, no lock held, the run outside its folder, a
heavy step in a clone folder with no nightly.sh above it: each **outside**; D. the follow-up tests: before 2 red / 7 green, after
9 green, the whole `test_dispatcher.py` green after; E. undo byte for byte, and apply/undo/verify refuse a changed file and a
link; F. the main tree's dispatcher and tracked status unchanged.

**Result: 38 ok, 0 failed; `failures: 0`** (rehearsal.log sha256 `7152116ffd2d25e2e3344f5ae269d2b5b2f06b6a58cef5f715b8e901ff3bfcba`). D: before 2 failed / 7 passed; after 9 passed; the whole `test_dispatcher.py` after: 196 passed, 3 skipped, 16 deselected (the opt-in rows), 113 s.

The operator's read-only tools on the bundle: `check_act` pass, `validate_manifest` pass, `path_rule` pass; `act_class.py` gives **b** (row `watchers`, no script hits). No check names a live HOME or repository path.

## 5. Risks

- **A wider exemption than meant:** only a process whose cwd is inside a nightly clone, under a live marker, below a nightly.sh
  that holds a slot lock. A lead or a close never runs there; a CTO session diagnosing a red clone runs under no nightly.sh.
- **A day run** (`nightly.sh` without `night`) also writes the marker and holds the slots, so it is covered the same way: it is
  the same run in the same slots.
- **A nightly holding fewer than three slots** still counts its run as in a slot once it holds one (its run is budgeted for the
  slots held, `heavy_slot.sh --held`); a nightly that holds none stays outside.
- **Cost:** a `/proc` fd listing only for a heavy process older than 5 minutes inside the run folder; nothing for the rest.
- **The test seam:** `DISPATCH_NIGHTLY_RUNS`, like every `DISPATCH_*` variable, is for the tests only.

## 6. Undo

`bash $G/apply.sh undo` puts the frozen before back byte for byte, only when the file is as this ACT left it (rehearsal E1-E5);
then a commit of the revert with the same trailers. The follow-up tests' two in-slot cases go red after an undo, so they are
reverted with it.

## 7. Hashes

| file | sha256 |
|---|---|
| `before/repo/governance/project/orchestration/tools/dispatch/dispatcher.py` | `dd5e57e2d94b33c108fe90e0e2b9748e70fb84d4285f74da30e44201bd329a54` |
| `after/repo/governance/project/orchestration/tools/dispatch/dispatcher.py` | `cda0af7196c807ea96168c2d1f2b990528c2be8bde402cc181aba615409b468c` |
| `apply.sh` | `762bbeaf508c97ce2e0a3615a1bcdcb77b9714496a4f9957692de4b52224f00c` |
| `list.txt` | `cd2d47f7ec0049c99f38258b1149f3d6e1e896cfa845a9ef403e2595133e2c34` |
| `rehearsal.log` | `7152116ffd2d25e2e3344f5ae269d2b5b2f06b6a58cef5f715b8e901ff3bfcba` |
| `followup-tests.diff` | `111d4aaf8524b904ef9de6594c989de8ced760964c9597e67ae2705814cc6885` |
| `manifest.json` | `9ff4f275775243ceac5faa3b4a7ea7e8ef34cf787e411b341fda42ee860c7252` |

## 8. Before the yes

- One independent review (verdict block in `review.md`); the reviewer's brief is the operator's `reviewer-brief.md`.
- The CTO's route for `followup-tests.diff` (tests/ is not an ACT's path).
