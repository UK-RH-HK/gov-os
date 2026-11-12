# ACT-ACCEPTED-REDS-1: the two warm real-model latency reds listed in `accepted_reds` until W2-155 closes (DEC-1134 (1))

**Round 2: a rebuild with byte-identical entries on the new map (DEC-1136 (1)); the r1 review's findings carried.**
ACT-W1-01-EXEMPT-3 was applied by the owner's operator (`7b5c3cb94fd9`), so the live map is `f4029cfb4942`, and ACT-EXAMIN-SETS-1 is
rebuilt on it (round 2: `f4029cfb` to `0ec1d20d`). This ACT is rebuilt on EXAMIN's new after: **`0ec1d20da86a` to `5654eca4c139`**. The r1 bundle
(reviewed READY, manifest `49e11172...`, before `b1ffdb0b`, after `72916f1d`) refuses on any of these maps and is kept untouched in
`drafts/accepted-reds-1/acts/ACT-ACCEPTED-REDS-1/` (the reviewed copy) and as `ACT-ACCEPTED-REDS-1.r1/` beside it. The entries are the same two (`tools/insert_reds.py`, `tools/entries.yaml`; the added
lines equal `entries.yaml` and r1's changed lines byte for byte: rehearsal E13, E14); the hunk's line numbers moved by 2 (`@@ -415` for `-413`).
**Neither this ACT nor ACT-EXAMIN-SETS-1 touches `tests/acceptance/`** (each changes only `governance/project/path-map.yaml`), so DEC-1136 (2) (an
ACT whose commit changes `tests/acceptance/` carries its own `acceptance_exemptions` entry by a second owner commit) adds nothing here.
**The r1 review's findings, carried:** F1 no literal live repository path in `apply.sh`'s comments (the rebuild hint is a repository-relative path);
F2 section 5 says what to do if the freeze refuses the commit; F3 section 5's last line reads the pin from `~/.local/bin/gov`, not a fixed
path. And the lessons of ACT-EXAMIN-SETS-1's review and ACT-W1-01-EXEMPT-3's: every manifest check as written with `bash -c`, the plain apply, `mktemp`,
no head, pid, date or count line in the hashed log (two runs are byte for byte equal), the pin's python with `-E` for `validate_entry.py`.

## 0. What the owner says
Class **(O)**: the owner's own `Role: owner` commit, made by the owner's operator **by hand**. The operator agent cannot
do it (section 2). The line, on its own line:

yes ACT-ACCEPTED-REDS-1 b8df21d8

- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-11 (round 2 the same day). Built and rehearsed in a fresh clone of `w2/integrate`
  with `HOME` planted. **Nothing live changes until it runs.** The live map was only read and hashed.
- **Bundle (round 2):** `.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts-r2/ACT-ACCEPTED-REDS-1/`. **Manifest sha256
  `b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7`.**
- **Sources:** DEC-1134 (1); DEC-1125 (1); DEC-757 (the ratchet); DEC-762; DEC-1052 (Q-10 and O-6); DEC-862; DEC-895;
  `governance/project/prompts/w2-orchestrator.md` (section "Exception until W2-12 lands");
  `src/gov/close/ratchet.py`; `governance/project/operator/class-rules.yaml` (row `path-map`).
- **Run it AFTER ACT-EXAMIN-SETS-1** (round 2, manifest `e80202922e72...`, sha8 `e8020292`; section 3). Before the owner's operator runs it,
  `apply.sh check` must print `state before (sha256 0ec1d20da86a)`.

## 1. What changes (one line becomes two entries)
In `governance/project/path-map.yaml`, the line `accepted_reds: []` (line 418 of the map ACT-EXAMIN-SETS-1 leaves) becomes:

```
accepted_reds:
  - test: "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"
    decision: DEC-1134
    reason: "the warm real-model query latency, p95 0.54-0.59 s against the 0.5 s budget: the named red of DEC-1125 (1)"
    fixed_by: W2-155
  - test: "tests/acceptance/W2-13/test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget"
    decision: DEC-1134
    reason: "the warm real-model query latency, p95 0.54-0.59 s against the 0.5 s budget: the named red of DEC-1125 (1)"
    fixed_by: W2-155
```

Nothing else in the map changes (9 lines added, 1 removed). Both test functions exist in the tree; DEC-1134 is an ACCEPTED
entry of the register whose text names both test ids (file and function), so each entry meets the ratchet's tests R-2.

## 2. Why, the class, and why not the operator agent
**Why (DEC-1134 (1)):** the nightly's two warm-latency tests fail at p95 0.54-0.59 s against the 0.5 s budget, the red
DEC-1125 (1) named. The owner decided (2026-11-11, in the chat) to list them by test id, with decision DEC-1134 and
`fixed_by` W2-155 (`DAEO-ar89`), so a known, named red does not stop every night's report. A listed test that passes must
leave the list (the close refuses until its entry is removed).

**Class (O).** `governance/project/operator/class-rules.yaml` (identical to `~/gov-os-operator/install/class-rules.yaml`: `diff`
is empty), row **`path-map`**, with `list.ratchet: [acceptance_exemptions, accepted_reds, load_sensitive, accepted_history]`
and `ratchet_class: O`; its `why`: "... a ratchet list or accepted history (acceptance_exemptions, accepted_reds,
load_sensitive, accepted_history) is read only from the owner's commits (O) (W1-01-EXEMPT-1, W2-57-LS-1,
P-TRACE-IMPL-1)". The operator's own `act_class.py` on the bundle (read only) gives
`{"class": "O", ... "row": "path-map", "why": "a change to accepted_reds, read only from the owner's commits"}`, `hits: []`.
The manifest claims `O`, so the three votes agree.

**The operator agent cannot make this commit.** Four places, all read in the code:
1. `operator_run.py` `g6`: `if self.cls == "O": raise oc.Refused("G6", "class (O): yours, not the operator's ...")`. No yes
   line, from anyone, changes that; the yes is read only for class (b).
2. Every commit it makes carries `Role: operator` (`git_commit`: `Role: operator`, `Act:`, `Act-sha:`, `Class:`, `Review:`);
   there is no path in the code that writes `Role: owner`.
3. OPERATOR-AGENT-1: "Never `Role: owner`. Records that the close reads only from your commits stay yours" (section 1, the
   commit trailers), and section 5 (what stays yours) lists "`Role: owner` records (ratchets, exemptions, accepted history for
   code, until W2-12)" as the owner's.
4. Even if it did commit: `ratchet._refused_because` accepts an entry only when every commit that added it carries `Role: owner`
   in its final trailer block. The rehearsal (H7) shows it: the same entries in a `Role: operator` commit are both refused,
   "added it without Role: owner", and cover nothing.

So the owner's operator commits it by hand (section 5), as the prompt's "Exception until W2-12 lands" says ("prepare each
ready to commit, with the exact operator commands, and ping ACT"); ACT-PATHMAP-NS-2 went by hand in the same form. The CTO never
makes this commit.

**Note on the route's date.** The operator agent's path-map replay refuses until about 21:17 UTC on 11-12 (DECIDED-NOT-DONE
row 124); the CTO queues no path-map ACT before then. The by-hand route is not affected by that row. ACT-EXAMIN-SETS-1 (class
(a)) is the agent's to apply after 21:17 UTC 11-12, or the owner's operator's by hand earlier; either way it comes first.

## 3. Order with ACT-EXAMIN-SETS-1 (both decide by the sha256 of the map)
| | map before | map after |
|---|---|---|
| live today (after ACT-W1-01-EXEMPT-3, `7b5c3cb94fd9`) | `f4029cfb49428708a7c7f9ca754bcd50a1c610ccc22966d09c4c581f1abbd971` | |
| ACT-EXAMIN-SETS-1 round 2 (manifest `e80202922e72...`) | `f4029cfb4942...` | `0ec1d20da86a4bdb0f38affe6bd76e86185af3152478ea6422e764442df8645d` |
| **ACT-ACCEPTED-REDS-1 round 2 (this)** | `0ec1d20da86a...` | `5654eca4c139be0e2f8457593a685fcd9d747657e952215e3c46bcac45998211` |

- **In order (EXAMIN, then this):** the hunk applies to EXAMIN's after map at its own line numbers (415, offset 0); the rehearsal's `git diff` from the
  EXAMIN-applied map equals the diff of the bundle's before and after copies, hunk for hunk (E12), and the added lines are `entries.yaml` byte for
  byte (E13). The two ACTs' changes are in different blocks (EXAMIN at the end of `evaluation_sets`, this one at `accepted_reds`), so neither rewrites the
  other's lines.
- **Reversed (this first):** `apply.sh` sees a map that is neither its before nor its after (`f4029cfb...`): `check`, `apply`, `undo` and `verify` all exit 3, the map is
  byte for byte as it was, the clone's `git status` is empty and no temp file is left (rehearsal B1 to B7). The r1 bundles of both ACTs refuse the same way (B8).
- **If the owner declines ACT-EXAMIN-SETS-1:** this bundle then refuses for good (its before never appears). A version built on the live map is needed:
  before `f4029cfb...`, after `f69afbe63e7d...` (`tools/insert_reds.py` on the live map; checked, **not built or rehearsed**: a rebuild of `list.txt`, the
  two copies and the manifest and a rehearsal without EXAMIN's steps, about ten minutes). Build it only if the owner declines or EXAMIN waits past this one.
- **Undo order:** undo this one first, then EXAMIN-SETS-1 (each undo refuses unless the map is as its ACT left it; rehearsal I).

## 4. Files, and what the checks are
| File (`acts-r2/ACT-ACCEPTED-REDS-1/`) | sha256 (12) |
|---|---|
| `manifest.json` | `b8df21d89160` |
| `apply.sh` | in `manifest.json` (`files`) |
| `list.txt` | in `manifest.json` |
| `before/repo/governance/project/path-map.yaml` (EXAMIN round 2's after) | `0ec1d20da86a` |
| `after/repo/governance/project/path-map.yaml` | `5654eca4c139` |
| `rehearsal.log` (the chain's, `drafts/examin-sets/rehearsal.r2.log`) | `69e57ee8b53e` |

`apply.sh check|apply|undo|verify`, run from the repository root. `check` is read-only and prints `state before|applied
(sha256 ...)` (exit 0, 0; exit 3 for any other map). `apply` runs only from `before`: it puts the frozen after copy in
place through a temp file that `mktemp` makes in the map's folder, then moves it (mode kept); it makes **no backup file**
(the undo is the frozen before copy, byte for byte). `undo` runs only when the map is as this ACT left it. It does not
commit; section 5 does.

The two checks in `manifest.json` (each run in the rehearsal exactly as written with `bash -c` from the clone, exit logged (section F)):
1. `PYTHONPATH=src python3 -m gov.check.pathmap`: exit 0.
2. A YAML probe: `accepted_reds` is exactly the two tests, each with decision DEC-1134, `fixed_by` W2-155 and a reason, and
   `evaluation_sets` holds `examin` (so it also proves EXAMIN-SETS-1 is under it). Exit 0; exit 1 on the before map (section F).

## 5. The message for the owner's operator (by hand; about three minutes)
yes ACT-ACCEPTED-REDS-1 b8df21d8

> **ACT-ACCEPTED-REDS-1 (DEC-1134): `accepted_reds` lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes.** Class (O): a `Role: owner` commit, by hand. Run it only after ACT-EXAMIN-SETS-1 (round 2) is applied; `check` says so.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts-r2/ACT-ACCEPTED-REDS-1
> sha256sum $G/manifest.json      # expect b8df21d891600ff4701ff264ff94f32257c4c9150ae4eb4a3254af2662248ea7
> git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
> bash $G/apply.sh check          # expect: state before (sha256 0ec1d20da86a)  (state other: stop, tell the CTO; it means EXAMIN-SETS-1 is not applied yet, or the map moved)
> bash $G/apply.sh apply          # expect: state applied (sha256 5654eca4c139)
> bash $G/apply.sh verify         # silent, exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git diff --numstat -- governance/project/path-map.yaml  # expect: 9  1  governance/project/path-map.yaml
> git commit -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml
> "$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c 'from gov.close import ratchet; c,f=ratchet.counted_entries(".","accepted_reds"); print(len(c),len(f))'   # expect: 2 0
> ```
> If `git commit` is refused by the freeze (the operator agent is applying another ACT), wait for its run to end and run the commit line again (or `bash $G/apply.sh undo`).
> Tell the CTO the commit hash (12 digits) and the last line. Do not run the two latency tests; the nightly does.
> To undo before the commit: `bash $G/apply.sh undo`. After the commit, the undo is a new owner commit that removes the two entries (`apply.sh undo`, then the same `git commit` with its own subject).

## 6. The rehearsal (round 2: `rehearsal.log` is the chain's, `drafts/examin-sets/rehearsal.r2.log`, ends `failures: 0`; 124 checks)
As the operators will run them: one `--no-hardlinks` clone of `w2/integrate` (`tools/rehearse_r2.sh` in `drafts/examin-sets/`), `HOME` planted (a copy of the git
identity file, and links to `~/.local/bin` and `~/.local/share` so the pin is read as section 5 reads it), only the root substituted. ACT-EXAMIN-SETS-1 is applied
first by its own `apply.sh` (the plain apply) and committed in the clone as the agent would; this ACT then goes by section 5's commit line (`Role: owner`).
The log holds no head, pid, date or count line of the live tree; two runs gave byte for byte equal logs.

| Step | Result |
|---|---|
| 0, A. preconditions | the clone's and the main tree's map are `f4029cfb4942`; this ACT's before is EXAMIN's after (`0ec1d20d`); the chain hashes are `0ec1d20d` and `5654eca4`; the clone is clean |
| B. **reversed order** (this ACT first) | check, apply, undo, verify all exit 3; map unchanged; `git status` empty; no temp file; the r1 bundles refuse too |
| C, D. EXAMIN first | its plain apply and commit (see its package, sections C and D); the clone's map is this ACT's before |
| E. this ACT: states, then the **plain apply** | check says before; verify exit 3; undo says nothing to undo; the apply puts the frozen after in place byte for byte; mode 644 kept; `git status` lists only the map; no stray file; apply again changes nothing; the clone's hunk equals the bundle's before-to-after hunk; the added lines are `entries.yaml` byte for byte; the pin's judge, before the owner's commit, counts neither entry (each "no commit of the history adds it") |
| F. **each manifest check as written** with `bash -c` | check 1 exit 0; check 2 exit 0 (and exit 1 on the before map); both print no count (manifest `count` null) |
| G. validate (DEC-895) | `validate_entry.py` on this round's patch (`accepted-reds.r2.diff`, the clone's diff), the pin's python with `-E`: PASS for both, "pending the owner's commit"; placeholder scan 0 hits |
| H. the by-hand commit, as section 5's commit line, `Role: owner` | trailers `Task`, `Implements`, `Role: owner`; the pin's `counted_entries` returns **both tests as accepted, 0 findings**; section 5's own one-line reader (the pin read from `~/.local/bin/gov`) prints `2 0`; `apply_accepted_reds` with both red: ok, each reported `failed` (covered); one passes: finding `ACCEPTED_RED_PASSES`; another red: `RED_NOT_ACCEPTED`; the same commit as `Role: operator`: both entries refused |
| I. undo, reverse order | REDS undo, then EXAMIN undo: the live map byte for byte; EXAMIN's undo with this ACT on top refuses |
| J. refusals | a changed map and a link: check, apply, undo refuse (exit 3); a link planted at the old fixed temp name is not followed; a tampered frozen copy: exit 4; map folder not writable: exit 5, map untouched, no temp file |
| K. live files | the main tree's map is unchanged (`f4029cfb4942`) |

**Section 5 as written, on top of the chain** (`drafts/examin-sets/tools/run_section5_r2.sh`): one fresh clone; EXAMIN by its `apply.sh` and committed as the
agent would; then this file's section 5 code block cut out and run as written (only the `cd` line points at the clone); its output is `section5.r2.out` beside
this file (script exit 0: the sha256 line is the manifest's `b8df21d8...`, check `state before (sha256 0ec1d20da86a)`, apply `state applied (sha256 5654eca4c139)`, verify silent, pathmap `0`, numstat `9 1`, a commit with `Task`, `Implements`, `Role: owner`, the reader line `2 0`, the clone clean).

**Differences from the real run.** (1) The clone is not the main tree: its hooks (reference-transaction, landing check, trailer gate) are git's defaults, so the
by-hand commit under the main tree's hooks is **not rehearsed** (the same form of commit passed for the DEC-1123 exemption entries, ACT-PATHMAP-NS-2 and
ACT-W1-01-EXEMPT-3; the freeze line in section 5 covers the one known refusal). (2) `HOME` is planted; the pin's interpreter and the bundle are the real ones. (3) The tests
were **not run** (no real-model run; the ratchet reader was shown their ids only). (4) Whether a close accepts the red in a real nightly is shown on
`apply_accepted_reds`, not by running `gov close`. (5) The clone commits ACT-EXAMIN-SETS-1 with a stand-in `Role: operator` subject; the real EXAMIN run
commits its own. (6) `G` is the drafts path here; if the CTO moves the bundle, change that one line.
