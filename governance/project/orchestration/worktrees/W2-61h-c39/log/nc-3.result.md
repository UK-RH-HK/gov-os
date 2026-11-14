The revision passes, with no blocking findings. (e), (f) and (g) each give the required outcome in both the visible planted case and the hidden-form S4 case on a throwaway root, and (a) to (d) are unchanged.

- task: DAEO-h2k3 (W2-61h), narrow independent check of the N2 (b) and N1 test revision (DEC-1180 (1), (4); DEC-1154)
- status: done, judgement pass
- work_completed: probed head dbe1236733f9d63ccccf8fc5435fbdba41617603, the designer's commit 70aa3a6b7ba3 merged at dbe123673, in `tests/acceptance/W2-61h/` only
- files_changed: none (read-only; throwaway files only under the sandbox's `$TMPDIR`)
- evidence: the probe record body below
- tests: visible folder 22 passed, 7 skipped, 9 deselected. The exclusion `-m "not local_only" -k "not real and not green_here and not time_limit"` left out the 9 deselected real-model, green-here and time-limit cases. Hidden-form S4 was run only on a planted root.
- discoveries: none blocking; one non-blocking row (R1)
- risks: none in scope
- lessons: `heavy_slot.sh` sends its "waiting" line to stderr, so piping the run through `tail` hid that it was waiting for a slot. My first run was stopped at its 20-minute background limit with no output; I re-ran it with output going straight to a file.
- proposed_decisions: none
- unresolved: none
- recommended_next_action: the lead commits the body below as `docs/probes/DAEO-h2k3/PR-DAEO-h2k3-n2.md`; then the owner's operator's walled re-run.

**Step 0, the sandbox check:**
- (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-h2k3` failed with "Read-only file system", and no file was created.
- (b) `git hash-object -w --stdin` worked (1ae28402a1…) and `git update-index --refresh` worked (exit 0).
- **The `ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.
- **At the end:** `git status --porcelain` is empty and HEAD is still dbe1236733f9d63ccccf8fc5435fbdba41617603.

---

reviewer_session: unknown

**What I probed and found sound**

- **Identity:** `git rev-parse HEAD` gives dbe1236733f9d63ccccf8fc5435fbdba41617603. The designer's commit touches only the four named files under `tests/acceptance/W2-61h/`.
- **The visible run** (the brief's command, through `heavy_slot.sh`, after waiting for a slot): 22 passed, 7 skipped, 9 deselected.
  - The 7 skipped are the hidden-form cases, because `GOV_EVAL_SETS_ROOT` was unset.
  - `test_s4_f3_judges_each_source_at_its_own_commit_on_planted_data` passes in that run.
  - No `GoldBlockChanged` warning appears at HEAD, so none of q21-q24's entries are listed.
- **Visible planted case, outcomes:**
  - red: p03 and p05, named by file name and entry number only
  - listed: p02, p06, p07, p08 (e) and p10 (g), with p10 listed once
  - not listed: p01 (a), p04 (d) and p09 (f)
  - No planted text, path or heading appears in any message.
- **Against the previous support file:** I took `w2_61h_support.py` from 494d5c933 and the new case file, copied under `$TMPDIR`.
  - The planted case is red: 1 failed, 7 passed.
  - The listed entries come out as p02, p06, p07, p10, p10: p08 is missing and p10 is listed twice.
  - So the new (e) and (g) proofs would have been red under the old rule, as the designer says.
- **Hidden-form S4 on a throwaway root:** seven planted files in `$TMPDIR/setsroot/fixtures/evaluation/memory-retrieval/hidden/`, citing a real older commit of `CLAUDE.md` and one file absent at that commit, with a copy of the path map.
  - (c) is red, named `h03.yaml source entry 1` with fixed words only.
  - The list holds 3 entries: h02 (b), h05 (e) and h07 (g), each once.
  - h01 (a), h04 (d) and h06 (f) are not listed.
  - Under `-W error` the same 3-entry list is printed to standard output instead of raising.
  - With h03 removed, the case passes and still shows the 3-entry warning.
  - Under the old support the same plant leaves h05 off the list, so (e) would not have been listed.
- **The hidden-form module still skips:** all 7 cases skip without `GOV_EVAL_SETS_ROOT`. They also skip with my planted root set under `GOV_ROLE=engineer` and under `GOV_ROLE=research`, which are the path map's `measures.roles`.
- **Is the "text differs" rule fair?** Each case was run through `_text_of`:
  - Treated as the same: trailing whitespace on a line; a section moved to the end of the file and losing its trailing blank line.
  - Treated as different: a changed word, a blank line inserted inside, a change of indentation, the next heading removed so the section grows, a subheading added, and an earlier duplicate heading (which `span_of` follows first).
  - A non-`#` heading is compared over its stated width: a move is not listed, a change inside the width is listed, a change beyond it is not.
  - The rule ignores only changes that neither a reader nor the measure can see. It hides no change of content an honest editor makes.
  - `span_of` uses the same heading pattern and section end as `measure.py`'s `_span`.
- **Did any earlier assertion weaken?** No. The red-source assertion is the same. The list assertion only gains p08 and p10. The not-listed check gains p09. The leak check is unchanged. The other changes to `judge_sources` swap `changed.append` for a call that adds each entry only once.
- **Function names and the full run:**
  - Every test function keeps its name in both case files.
  - The planted case is still one non-parametrised function, so `tests/optin-lifted-breadth.txt`'s first-row rule does not drop it. It ran in the full run above.
- **Trailers:**
  - The designer's commit ends in one block: `Co-Authored-By`, `Rewrite-Reason: DEC-1180 (1)`, `Task: DAEO-h2k3`, `Role: independent-test-designer`, `Implements`.
  - The merge ends in one block: `Task: DAEO-h2k3`, `Role: orchestrator`, `Implements`, `Co-Authored-By`.
- **No leaks:** the messages, the warning and the README name file names and entry numbers only. The README's planted proofs name throwaway file names, never real hidden content.
- **Untouched:** I never opened the real sets root or any hidden, retired-hidden or memory-verdict folder. `GOV_EVAL_SETS_ROOT` was only ever set to my own planted roots.

**Findings**

- **R1 (out of scope, a recorded row):** the hidden-form (g) plant does not by itself prove N1. Its two changed alternatives are a changed block and a rewritten section. The old rule would not have listed the section, so the old code also lists that entry once. N1 is proven only by the visible p10, whose three alternatives include two line-cited changes that the old code lists twice. Both modules call the same `judge_sources`, so the hidden case is covered.
  - What would reverse it: a hidden-form plant with two line-cited changed alternatives that the old support lists twice.
  - `Ordinary work: no, because it is a gap in how the proof is planted, not in the check; the shared support function is what the case runs.`
  - `Consequence: other`

Judgement: pass

```verdict
{"kpis": [{"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]}
```