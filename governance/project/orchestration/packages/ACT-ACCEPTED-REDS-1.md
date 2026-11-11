# ACT-ACCEPTED-REDS-1: the two warm real-model latency reds listed in `accepted_reds` until W2-155 closes (DEC-1134 (1))

## 0. What the owner says
Class **(O)**: the owner's own `Role: owner` commit, made by the owner's operator **by hand**. The operator agent cannot
do it (section 2). The line, on its own line:

yes ACT-ACCEPTED-REDS-1 49e11172

- **Review:** round 1 **READY**, class (O) (2026-11-11 16:29 UTC, `reviews/ACT-ACCEPTED-REDS-1-review-r1.md`; F1-F3 rows: run §5 only after ACT-EXAMIN-SETS-1 is applied and not while the operator agent holds a freeze (F2); a re-pin changes §5's last line (F3); both fail closed).
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-11. Built and rehearsed in a fresh clone of `w2/integrate`
  at `b9e878009b8c`, with `HOME` planted. **Nothing live changes until it runs.** The live map was only read and hashed.
- **Bundle:** `.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts/ACT-ACCEPTED-REDS-1/`. **Manifest sha256
  `49e1117248e1cccfd134151a34a18af870b49ea57cb1870863776aed006a4778`.**
- **Sources:** DEC-1134 (1); DEC-1125 (1); DEC-757 (the ratchet); DEC-762; DEC-1052 (Q-10 and O-6); DEC-862; DEC-895;
  `governance/project/prompts/w2-orchestrator.md` (section "Exception until W2-12 lands");
  `src/gov/close/ratchet.py`; `governance/project/operator/class-rules.yaml` (row `path-map`).
- **Run it AFTER ACT-EXAMIN-SETS-1** (section 3). Before the owner's operator runs it, `apply.sh check` must print
  `state before (sha256 b1ffdb0b7b3e)`.

## 1. What changes (one line becomes two entries)
In `governance/project/path-map.yaml`, the line `accepted_reds: []` (line 416) becomes:

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
| live today | `fb52ab2dc7568d24234b755abc7fd6ad7b21743ca3d01b572ef7e9dc40fc2d95` | |
| ACT-EXAMIN-SETS-1 (READY, manifest `97d45565...`) | `fb52ab2d...` | `b1ffdb0b7b3e2fb25f7a5ef8e7417a0710197cc4dbd2efac73a08a3ad6a61878` |
| **ACT-ACCEPTED-REDS-1 (this)** | `b1ffdb0b7b3e...` | `72916f1da4aef9c9bdb52849056280f1e8271e45169e83aa341ddff97ebc6632` |

- **In order (EXAMIN, then this):** the drafted hunk applies to EXAMIN's after map at its own line numbers (413, offset 0); the
  rehearsal's `git diff` from the EXAMIN-applied map is that hunk byte for byte (E9), and `patch` gives the same bytes as the
  builder (`72916f1d...`). The two ACTs' changes are in different blocks (EXAMIN at the end of `evaluation_sets`, this one at
  `accepted_reds`), so neither rewrites the other's lines.
- **Reversed (this first):** `apply.sh` sees a map that is neither its before nor its after (`fb52ab2d...`): `check`, `apply`,
  `undo` and `verify` all exit 3, the map is byte for byte as it was, the clone's `git status` is empty and no temp file is
  left (rehearsal B1 to B7). This one cannot go first by accident, so EXAMIN-SETS-1's own `fb52ab2d` before is never changed under it.
- **If the owner declines EXAMIN-SETS-1:** this bundle then refuses for good (its before never appears). A version built on the
  live map is needed: the before copy is `fb52ab2d...` and the after is `ec411be7c81337fd829627080391eb3cf9444fb36e3f89f3bd5abdab325eadd7`
  (`drafts/accepted-reds-1/path-map.after.yaml`; the builder `tools/insert_reds.py` gives the same bytes from the live map,
  checked). It is **not built or rehearsed**: it is a rebuild of `list.txt`, the two copies and the manifest, and a rehearsal
  with section C left out, about ten minutes. Recommendation: build it only if the owner declines or EXAMIN-SETS-1 waits past
  this one; the owner's answer on EXAMIN-SETS-1 comes first.
- **Undo order:** undo this one first, then EXAMIN-SETS-1 (each undo refuses unless the map is as its ACT left it).

## 4. Files, and what the checks are
| File (`acts/ACT-ACCEPTED-REDS-1/`) | sha256 (12) |
|---|---|
| `manifest.json` | `49e1117248e1` |
| `apply.sh` | in `manifest.json` (`files`) |
| `list.txt` | in `manifest.json` |
| `before/repo/governance/project/path-map.yaml` (EXAMIN's after) | `b1ffdb0b7b3e` |
| `after/repo/governance/project/path-map.yaml` | `72916f1da4ae` |
| `rehearsal.log` | `490bf4517f69` |

`apply.sh check|apply|undo|verify`, run from the repository root. `check` is read-only and prints `state before|applied
(sha256 ...)` (exit 0, 0; exit 3 for any other map). `apply` runs only from `before`: it puts the frozen after copy in
place through a temp file that `mktemp` makes in the map's folder, then moves it (mode kept); it makes **no backup file**
(the undo is the frozen before copy, byte for byte). `undo` runs only when the map is as this ACT left it. It does not
commit; section 5 does.

The two checks in `manifest.json` (each run in the rehearsal exactly as written with `bash -c` from the clone, exit logged):
1. `PYTHONPATH=src python3 -m gov.check.pathmap`: exit 0.
2. A YAML probe: `accepted_reds` is exactly the two tests, each with decision DEC-1134, `fixed_by` W2-155 and a reason, and
   `evaluation_sets` holds `examin` (so it also proves EXAMIN-SETS-1 is under it). Exit 0; exit 1 on the before map (F3).

## 5. The message for the owner's operator (by hand; about three minutes)
yes ACT-ACCEPTED-REDS-1 49e11172

> **ACT-ACCEPTED-REDS-1 (DEC-1134): `accepted_reds` lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes.** Class (O): a `Role: owner` commit, by hand. Run it only after ACT-EXAMIN-SETS-1 is applied; `check` says so.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/acts/ACT-ACCEPTED-REDS-1
> sha256sum $G/manifest.json      # expect 49e1117248e1cccfd134151a34a18af870b49ea57cb1870863776aed006a4778
> git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
> bash $G/apply.sh check          # expect: state before (sha256 b1ffdb0b7b3e)  (state other: stop, tell the CTO; it means EXAMIN-SETS-1 is not applied yet, or the map moved)
> bash $G/apply.sh apply          # expect: state applied (sha256 72916f1da4ae)
> bash $G/apply.sh verify         # silent, exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git diff --numstat -- governance/project/path-map.yaml  # expect: 9  1  governance/project/path-map.yaml
> git commit -m "ACT-ACCEPTED-REDS-1: accepted_reds lists the two warm real-model latency cases (W1-19, W2-13) until W2-155 closes (DEC-1134)" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1134, DEC-1125" --trailer "Role: owner" -- governance/project/path-map.yaml
> /home/usain/.local/share/gov-os/pin-797495bdfc70/bin/python -I -c 'from gov.close import ratchet; c,f=ratchet.counted_entries(".","accepted_reds"); print(len(c),len(f))'   # expect: 2 0
> ```
> Tell the CTO the commit hash (12 digits) and the last line. Do not run the two latency tests; the nightly does.
> To undo before the commit: `bash $G/apply.sh undo`. After the commit, the undo is a new owner commit that removes the two entries (`apply.sh undo`, then the same `git commit` with its own subject).

## 6. The rehearsal (`rehearsal.log`, ends `failures: 0`; 63 checks)
As the operator will run it: a `--no-hardlinks` clone of `w2/integrate` at `b9e878009b8c` under
`drafts/accepted-reds-1/tmp/clone`, `HOME` planted (`tmp/home`, with a copy of the git identity file only), only the root
substituted. ACT-EXAMIN-SETS-1 is applied first in the clone by its own `apply.sh` and committed there.

| Step | Result |
|---|---|
| 0, A. preconditions | the clone's map is EXAMIN's before (`fb52ab2d`); this ACT's before is EXAMIN's after (`b1ffdb0b`); the main tree's map hashed read only |
| B. **reversed order** (this ACT first) | check, apply, undo, verify all exit 3; map unchanged; `git status` empty; no temp file |
| C. EXAMIN-SETS-1 first (plain apply, committed in the clone) | map is `b1ffdb0b`, this ACT's before |
| D. this ACT's states before the apply | check says before; verify exit 3; undo says nothing to undo |
| E. the **plain apply** (review F2: no backup variable) | map is the frozen after byte for byte; mode 644 kept; `git status` lists only the map; no stray file; apply again changes nothing; the clone's diff equals the drafted hunk byte for byte; the pinned judge, before the owner's commit, counts neither entry (each "no commit of the history adds it") |
| F. **each manifest check as written** with `bash -c` (review F1) | check 1 exit 0; check 2 exit 0 (and exit 1 on the before map); both print no count (manifest `count` null) |
| G. validate (DEC-895) | `validate_entry.py` on the patch, the pin's interpreter: PASS for both, "pending the owner's commit"; placeholder scan 0 hits |
| H. the by-hand commit, exactly as in section 5, `Role: owner` | trailers `Task`, `Implements`, `Role: owner`; the pinned judge's `counted_entries` returns **both tests as accepted, 0 findings**; the message's own one-line reader prints `2 0`; `apply_accepted_reds` with both red: ok, each reported `failed` (covered); one passes: finding `ACCEPTED_RED_PASSES`; another red: `RED_NOT_ACCEPTED`; the same commit as `Role: operator`: both entries refused |
| I. undo from the committed state | map is the frozen before byte for byte; second undo says nothing to undo; no temp file |
| J. refusals | a changed map and a link: check, apply, undo refuse (exit 3); a link planted at the old fixed temp name `<map>.act-tmp` is not followed (target untouched, review F4); a tampered frozen copy: exit 4, map untouched; map folder not writable: exit 5, map untouched, no temp file |
| K. live files | the main tree's map is unchanged (`fb52ab2dc756`) |

**Differences from the real run.** (1) The clone is not the main tree: its hooks (reference-transaction, landing check, trailer
gate) are git's defaults, so the by-hand commit under the main tree's hooks is **not rehearsed** (the same form of commit passed
for the DEC-1123 exemption entries and ACT-PATHMAP-NS-2). (2) `HOME` is planted; the pinned interpreter and the bundle are the
real ones. (3) The tests were **not run** (no real-model run; the ratchet reader was shown their ids only). (4) Whether a close
accepts the red in a real nightly is shown on `apply_accepted_reds`, not by running `gov close`. (5) The clone commits
ACT-EXAMIN-SETS-1 with a stand-in `Role: operator` subject; the real EXAMIN run commits its own. (6) `G` is the drafts path here; if the
CTO moves the bundle, change that one line.
