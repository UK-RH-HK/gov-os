# ACT-W1-01-EXEMPT-3: the owner's operator's commit 6fbe73b1adde is listed in `acceptance_exemptions` (DEC-1136 (1))

## 0. What the owner says
Class **(O)**: the owner's own `Role: owner` commit, made by the owner's operator **by hand**. The operator agent cannot make it
(section 2). The line, on its own line:

yes ACT-W1-01-EXEMPT-3 6af6bdeb

- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-11. Built and rehearsed in a fresh clone of `w2/integrate`
  with `HOME` planted. **Nothing live changes until it runs.** The live map was only read and hashed.
- **Bundle:** `.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-3/acts/ACT-W1-01-EXEMPT-3/`.
  **Manifest sha256 `6af6bdeb15b018d37f8b11b451b783dbb959ea33e762c89cefaa1033f01cba5e`.**
- **Sources:** DEC-1136 (1) (the order: this ACT first, on the live map); DEC-253 and DEC-906 (item 3: the owner's own
  `Role: owner` commits are the `acceptance_exemptions` entries); DEC-757 (the ratchet lists); DEC-1123 (item 4: the same form
  for the earlier entries, ACT-W1-01-EXEMPT-2); `governance/project/operator/class-rules.yaml` (row `path-map`).
- **Before the operator runs it:** `apply.sh check` must print `state before (sha256 fb52ab2dc756)`. Any other map: stop and tell the CTO.
- **Package:** the problem, the options and the cost of waiting are in `P1-W1-01-EXEMPT-3.md` beside this file.

## 1. What changes (one entry, two lines)
In `governance/project/path-map.yaml`, one entry is added at the end of `acceptance_exemptions` (after line 409, the
ACT-GUARD-SETS-1 entry of DEC-1123):

```
  - commit: "6fbe73b1adde40571f00d490b4b478cf86b70a52"
    decision: DEC-1136  # the owner's ACT-OPERATOR-ROUNDS-1 commit changed the acceptance support file tests/acceptance/W2-148/w2_148_support.py (DEC-1136 (1)); not a test designer's commit
```

Nothing else in the map changes (2 lines added, 0 removed; `path-map.diff` beside this file). The full id is `6fbe73b1adde40571f00d490b4b478cf86b70a52`
(read from the repository, not typed: `git rev-parse 6fbe73b1a`). W1-01 matches an exemption by its whole id only.

**The only owner commit that needed an entry.** Since the last entry's own commit (`3428f659f095`, DEC-1123 item 3, 11-10 22:11) every
commit that touches `tests/acceptance/` is a test designer's (`Role: independent-test-designer`: `53affe5337fd`, `a7d476c16da2`,
`35396225e07c`, `669707a760b7`) or an integration merge of designers' commits (`9007b8cfa76e`, `d831dd35e0f4`, `ba2ecaacf7b1`, which W1-01's
merge case passes), except `6fbe73b1adde` (`Role: owner`, the operator's ACT-OPERATOR-ROUNDS-1: it changed
`tests/acceptance/W2-148/w2_148_support.py`). `0c5032bc80a1` changes only briefs and `91c8885a407d` no test file; neither needs one.
The W1-01 history case, run on `w2/integrate` in a clone, names `6fbe73b1adde` and nothing else (rehearsal A3).

**DEC-1136 (2) (standing): an ACT whose commit changes a file under `tests/acceptance/` carries its own exemption entry in the same
apply.** This ACT changes only `governance/project/path-map.yaml`, so its own commit touches nothing under `tests/acceptance/` and needs
no entry; there is no second commit.

## 2. Why, the class, and why not the operator agent
**Why:** the commit `6fbe73b1adde` (17:41 UTC) changed an acceptance support file, as `Role: owner`, not as the test designer. W1-01's
history case (`test_only_the_test_designer_commits_to_acceptance_tests`) names it an offender, and its merge case judges every merge that brings it in
(DEC-253, DEC-906 item 3): until its full id is listed, integrate and every non-fast-forward merge of it are red on W1-01. DEC-1136 (1)
is the owner's decision to list it first.

**Class (O).** `class-rules.yaml`, row `path-map`, lists `acceptance_exemptions` among the ratchet lists (`ratchet_class: O`): records
read only from the owner's commits. The operator's own `act_class.classify_manifest` on the final bundle votes `O` (stated in the
rehearsal's companion check, section 6). The manifest claims `O`.

**The operator agent cannot make this commit** (same four places as ACT-ACCEPTED-REDS-1 section 2): `operator_run.py` `g6` refuses class (O);
every commit it makes is `Role: operator`; OPERATOR-AGENT-1 section 1 never `Role: owner`; and section 5 keeps `Role: owner` records
as the owner's. **A finding for you (rehearsal F4, information only):** W1-01 reads the list by full id and decision shape only. The same entry in a
`Role: operator` commit turns the case green too, so the owner's-commit rule is DEC-906's and the class table's, not code W1-01 enforces.
The close's gate (h) reader (`gates.owner_listed`) also does not look at the commit's role. Take the by-hand route as the rule says.

## 3. Order with the two other path-map ACTs (DEC-1136 (1): this one first)
All three decide by the sha256 of `governance/project/path-map.yaml`.

| | map before | map after |
|---|---|---|
| live today | `fb52ab2dc7568d24234b755abc7fd6ad7b21743ca3d01b572ef7e9dc40fc2d95` | |
| **ACT-W1-01-EXEMPT-3 (this)** | `fb52ab2d...` | `f4029cfb494287...` (`list.txt`) |
| ACT-EXAMIN-SETS-1 (frozen, reviewed, READY) | `fb52ab2d...` | `b1ffdb0b...` |
| ACT-ACCEPTED-REDS-1 (frozen, reviewed, READY) | `b1ffdb0b...` | `72916f1d...` |

After this ACT is applied, the map is neither of their before copies: both **refuse** (`check`, `apply`, `undo`, `verify` all exit 3, state other;
nothing is touched; shown for this direction in rehearsal H4 with EXAMIN's after copy as the map, and by those bundles' own rehearsals). Nothing
is lost. They are rebuilt on the new map, with byte-identical entries, as a separate job (DEC-1136 (1)); the CTO's section.
Facts for that job (computed here, not built): `insert_entries.py` and `insert_reds.py` insert at their blocks, which this ACT does not touch,
so the entries come out byte-identical and only the hunks' line numbers move by 2 (EXAMIN's `@@ -553` instead of `-551`, REDS's `@@ -415` instead of `-413`).
The chain on the new map: this ACT `fb52ab2d` to `f4029cfb`; EXAMIN rebuilt `f4029cfb` to `0ec1d20d`; REDS rebuilt `0ec1d20d` to `5654eca4`. The final map
is the same whichever order is used (EXAMIN, REDS, then this one also gives `5654eca4`).
**Undo order:** undo this one only when the map is still as this ACT left it (the after hash); once another ACT has been applied on top, undo that one first.

## 4. Files, and what the checks are
| File (`acts/ACT-W1-01-EXEMPT-3/`) | sha256 (12) |
|---|---|
| `manifest.json` | `6af6bdeb15b0` |
| `apply.sh` | in `manifest.json` (`files`) |
| `list.txt` | in `manifest.json` |
| `before/repo/governance/project/path-map.yaml` | `fb52ab2dc756` |
| `after/repo/governance/project/path-map.yaml` | `f4029cfb4942` |
| `rehearsal.log` | `3359eb2c49d5` |

`apply.sh check|apply|undo|verify`, run from the repository root. `check` is read-only and prints `state before|applied (sha256 ...)` (exit 0;
exit 3 for any other map). `apply` runs only from `before`: it puts the frozen after copy in place through a temp file that `mktemp` makes in the map's folder,
then moves it (mode kept); **no backup file**. `undo` runs only when the map is as this ACT left it. It does not commit; section 5 does.
The two checks in `manifest.json` (each run in the rehearsal exactly as written with `bash -c` from the clone):
1. `PYTHONPATH=src python3 -m gov.check.pathmap`: exit 0.
2. A YAML probe: `acceptance_exemptions` holds exactly the eight commits in order, each with a `DEC-` decision, the last is `DEC-1136`. Exit 0; exit 1 on the before map.

## 5. The message for the owner's operator (by hand; about three minutes)
yes ACT-W1-01-EXEMPT-3 6af6bdeb

> **ACT-W1-01-EXEMPT-3 (DEC-1136 (1)): `acceptance_exemptions` lists the owner's commit `6fbe73b1adde` (ACT-OPERATOR-ROUNDS-1), so W1-01 is green again.** Class (O): a `Role: owner` commit, by hand. Run it BEFORE ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1; `check` says if the map is not the live one.
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-w1-01-exempt-3/acts/ACT-W1-01-EXEMPT-3
> sha256sum $G/manifest.json      # expect 6af6bdeb15b018d37f8b11b451b783dbb959ea33e762c89cefaa1033f01cba5e
> git status --short              # the map must not be listed (other lines are the CTO's and stay uncommitted)
> bash $G/apply.sh check          # expect: state before (sha256 fb52ab2dc756)  (state other: stop, tell the CTO)
> bash $G/apply.sh apply          # expect: state applied (sha256 f4029cfb4942)
> bash $G/apply.sh verify         # silent, exit 0
> PYTHONPATH=src python3 -m gov.check.pathmap; echo $?   # expect: 0, with no output before it
> git diff --numstat -- governance/project/path-map.yaml  # expect: 2  0  governance/project/path-map.yaml
> git commit -m "ACT-W1-01-EXEMPT-3: acceptance_exemptions lists the owner's ACT-OPERATOR-ROUNDS-1 commit 6fbe73b1adde (DEC-1136 (1))" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1136, DEC-906, DEC-253" --trailer "Role: owner" -- governance/project/path-map.yaml
> "$(head -1 ~/.local/bin/gov | cut -c3-)" -I -c 'import yaml; from pathlib import Path; from gov.close import gates; s=yaml.safe_load(open("governance/project/path-map.yaml")); print("6fbe73b1adde40571f00d490b4b478cf86b70a52" in gates.owner_listed(Path("."), s))'   # expect: True
> ```
> Optional, about one minute (W1-01's two history cases, through the heavy-job gate): `PYTHONPATH=src bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass -q -p no:cacheprovider` (expect `2 passed`).
> If `git commit` is refused by the freeze (the operator agent is applying another ACT), wait for its run to end and run the commit line again (or `bash $G/apply.sh undo`).
> Tell the CTO the commit hash (12 digits) and the last line. To undo before the commit: `bash $G/apply.sh undo`. After the commit, the undo is a new owner commit that removes the entry (`apply.sh undo`, then the same `git commit` with its own subject).

## 6. The rehearsal (`rehearsal.log`, ends `failures: 0`)
As the operator will run it: a `--no-hardlinks` clone of `w2/integrate` under `drafts/act-w1-01-exempt-3/tmp/clone`, `HOME` planted (`tmp/home`, a copy of the git identity
file only), only the root substituted. The log holds no live head, pid, date or count line, so a re-run gives the same bytes (checked: the rehearsal ran twice and the two logs are byte for byte equal).

| Step | Result |
|---|---|
| 0, A. preconditions | the clone's and the main tree's map are the frozen before (`fb52ab2d`); the clone is clean. **A3: W1-01's two cases before the apply are red**: the history case fails naming `6fbe73b1adde` and nothing else; the merge case passes |
| B. states before the apply | check says before; verify exit 3; undo says nothing to undo |
| C. the **plain apply** (review F2 of ACT-EXAMIN-SETS-1) | the map is the frozen after byte for byte; mode 644 kept; `git status` lists only the map; no stray file; apply again changes nothing; 2 lines added, 0 removed; the entry names the full id |
| D. **each manifest check as written** with `bash -c` (review F1) | check 1 exit 0; check 2 exit 0, and exit 1 on the before map |
| E. validate (DEC-895) | `validate_entry.py` with the pin's python (`-E`), on the patch, against the register as it stands (it holds DEC-1136): PASS for the entry (DEC-1136 is the owner's and names `6fbe73b1a`); placeholder scan 0 hits |
| F. the by-hand commit, as section 5 gives it, `Role: owner` | trailers `Task`, `Implements`, `Role: owner`; **W1-01's two cases are green: `2 passed`**; `gates.owner_listed` returns True. F4 (information): the same entry in a `Role: operator` commit is also green (section 2) |
| F5. **section 5's code block run as written** (`tools/run_section5.sh`: the block is cut from this file and run in a second fresh clone, planted HOME, only the root substituted) | sha256sum prints the manifest sha; check `state before (sha256 fb52ab2dc756)`; apply `state applied (sha256 f4029cfb4942)`; verify silent; pathmap `0`; numstat `2 0`; the commit carries `Task`, `Implements`, `Role: owner` and leaves the clone clean; the reader line prints `True`; the optional W1-01 line gives `2 passed` (the planted HOME hides the user-site pytest, so that one line ran with `PYTHONUSERBASE` set; with the real HOME pytest is found) |
| G. undo from the committed state | the frozen before byte for byte; second undo says nothing to undo; no temp file |
| H. refusals | a changed map, another path-map ACT's map (EXAMIN's after copy) and a link: check, apply, undo refuse (exit 3); a link at the old fixed temp name is not followed; a tampered frozen copy exit 4; map folder not writable exit 5, map untouched |
| K. live files | the main tree's map is unchanged |

**Differences from the real run.** (1) The clone is not the main tree: its hooks are git's defaults, so the by-hand commit under the main tree's hooks
(the `reference-transaction` freeze gate, the landing check, the trailer gate) is not rehearsed; the same form of commit passed for the DEC-1123 entries,
ACT-PATHMAP-NS-2 and ACT-ACCEPTED-REDS-1's rehearsal. The freeze line in section 5 covers the one known refusal. (2) `HOME` is planted; the pin's interpreter and the bundle are the real ones.
(3) Only W1-01's two cases ran (the full suite never ran). (4) `G` is the drafts path; if the CTO moves the bundle, change that one line.
