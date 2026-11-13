**Review rv-1: W2-146 (DAEO-f6x3) passes.** I found no fail-open path in ordinary work. I recorded five minor rows, none of which blocks.

**Sandbox check (Step 0):**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-f6x3` failed with "Read-only file system", as it should.
- (b) `git hash-object -w --stdin` worked (1ae28402a109…) and `git update-index --refresh` worked (exit 0).

**Model-process check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

task: DAEO-f6x3 (W2-146), rv-1, STANDARD review, class C2

status: DONE

work_completed:
- Confirmed head 908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3 and a clean tree.
- Read the whole change since 3556fd7d1825 (schema, `lexical.py`, `command.py`), plus `lexical.search`/`_ranked`, the tokenizer, `whole_id`, `gov.launch.store` and `gov.config.path_map_schema`.
- Read all four test files and the support module.
- Probed `ids_in` and `id_forms` in TMPDIR. This included 20,000 random texts comparing the old expression with the new code, with and without a form that matches nothing: 0 differences.
- Ran the ticket's tests.
- Answered the lead's six questions:
  - **Q1, fail-open paths:** none in ordinary work.
    - `id_forms(root)` is called at `src/gov/retrieve/command.py:60`, outside the records check's try/except at :66-70. So a CONFIG_INVALID is never swallowed, and it is raised before the records read and before any `lexical.search` (:72).
    - An entry that is not a map, has an empty or non-string name or pattern, or has a pattern that does not compile raises CONFIG_INVALID naming `id_forms[i]` (`src/gov/retrieval/lexical.py:204-214`).
    - `id_forms: {}` raises CONFIG_INVALID. Only a YAML null, an empty list or a missing key gives `()` (:197-199).
    - A continuation request skips `_nowhere` (:131). That is right, since a continuation follows a request that was already retrieved.
  - **Q2, no form declared:** `forms=()` runs the old expression unchanged (`lexical.py:228-229`). The only caller that passes forms is `command.py:61,63`. `_lead_id` (:253), `_words` (:569), `_ranked` (:617) and `memaudit/preflight.py:378` call `ids_in(text)`. `gov.links` has its own `ids_in` and is untouched.
  - **Q3, whole-token and overlap rules:** they match Interface point 3 (`lexical.py:218,230-239`).
    - Overlaps are sorted by start, then longest first. Probes: `SPEC-4.2` → `['SPEC-4.2']`; `SPEC-4.2.` → `SPEC-4.2`.
    - Partial tokens are refused: `XREQ12`, `REQ123a`, `rq-7-b`, `SPEC 9-A` are not read.
    - Built-in shape candidates are not given the whole-token check, as the Interface specifies.
  - **Q4 (F2), a present id is found:** yes for all five planted forms.
    - The tokenizer is `porter unicode61 tokenchars '_'` (:68). It splits and folds the question and the indexed text the same way, so the FTS phrase finds the chunk.
    - `_ranked` (:626,633) then requires the exact substring, and `whole_id` (:76) confirms the whole token.
    - The acceptance test `test_s3_failure2_the_present_id_asked_alone_cites_the_file_that_holds_it` confirms it end to end.
  - **Q5, do the tests check each KPI line:** yes, no test passes vacuously.
    - The stop tests skip only without git or gitleaks; both are present, and 63 ran with none skipped.
    - Taking out any of these would turn tests red: passing forms in `_nowhere`, the overlap rule, the whole-token check, or the loud error. A premise test pins that the built-in shape does not read the planted ids.
  - **Q6, schema:** the diff only adds `id_forms` and `$defs/id_form`; nothing else in the schema changed. The schema tests pass under `Draft202012Validator` with `FormatChecker`: it refuses a nameless, patternless, non-compiling, empty, non-string or extra-key entry, and a non-list.
- **The lead's three known judgements:** I agree with all three. I recorded the null and extra-key cases as rows R2 and R3, and a misspelled top-level key as R1.

files_changed: none

evidence:
- `git -C /home/usain/gov-os-worktrees/W2-146 rev-parse HEAD` = 908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3; `git status --porcelain` is empty at the end.
- Probe output, run in TMPDIR (`$TMPDIR/rv/probe.py`):
  - `ids_in('see REQ12 rq-7 TC_3 SPEC-4.2 SPEC 9 and DEC-5', F)` = `['REQ12','rq-7','TC_3','SPEC-4.2','SPEC 9','DEC-5']`.
  - `id_forms` returns `()` for `id_forms:` (null), for a misspelled top-level key, and for an entry with an extra `flags:` key that it compiles without the flag.
  - It raises CONFIG_INVALID for `{}`, a missing pattern, `'('`, `''`, a pattern given as a number, and a bare string entry.
  - `re.compile('a{4294967296}')` raises OverflowError, not `re.error`.

tests:
- I ran without `heavy_slot.sh`. It keeps its lock files in `/tmp`, which is read-only in the launch sandbox, so the first run sat with no output until it was stopped at 20 minutes. The brief's `/tmp/w2-146-rv` could not be created either. Following EMG-d4b-launched ("the heavy slot only if the sandbox allows it"), I ran one process (`-p no:xdist`), with TMPDIR set to `$TMPDIR/w2-146-rv` and the empty HOME, plus `-m "not local_only" -k "not real and not green_here and not time_limit"`.
- Results:
  - `tests/acceptance/W2-146/test_w2_146_reader.py`, `test_w2_146_schema.py`, `tests/unit/retrieval/test_w2_146_id_forms.py` and `tests/unit/retrieve/test_w2_146_stop.py` together: 175 passed, 39 deselected.
  - The 39 deselected are not from the exclusion filter. The opt-in "breadth" `rep:` rule in `tests/conftest.py` keeps only the first row of each parametrised unit test. With `--optin=breadth`, the unit file gave 57 passed.
  - `tests/acceptance/W2-146/test_w2_146_stop.py`: 63 passed, 0 skipped.
- I did not re-run the lead's full suite.

discoveries:
- In a default run, the opt-in "breadth" rule drops 39 of the 57 rows in the engineer's `test_w2_146_id_forms.py`; only `--optin=breadth` runs them all. The acceptance tests cover the same ground, so nothing is lost here.
- The JSON path-map schema is not checked at run time: `src/gov/config/path_map_schema.py` is a Python schema that ignores `id_forms`. `lexical.id_forms` is therefore the only check of the forms when `gov retrieve` runs.

risks:
- R1: a misspelled top-level key such as `id_form:` is silently ignored, so the stop never fires for that repository's forms. This comes from the top level staying open by design.

lessons:
- In this launch sandbox, `heavy_slot.sh` cannot get a slot because `/tmp` is read-only. It waits silently rather than failing. Briefs for sandboxed reviewers should say to run serially without it, or give `GOV_HEAVY_DIR`.

proposed_decisions: none

unresolved: none

recommended_next_action:
- Ready to land from the review's side.
- Optional follow-up, owner or CTO choice, not this ticket: check `path-map.yaml` against the JSON schema somewhere ordinary (for example a check that `gov check` runs), so `id_form:` typos, a null `id_forms`, and extra keys are caught. That would close R1 to R3.

```verdict
verdict: PASS
probed_commit: 908a6c2527edb0c0d2a7cdc5ff44ae38ec3e4fa3
findings: 5
```
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}]}
```
Classification: 5 findings. None is in scope, reachable in ordinary work, and failing open or losing work; R1 is reachable but out of scope. All five are recorded rows; no new round is proposed.

**R1 — a misspelled top-level key declares nothing, silently** (low; out of scope)
- Where: `src/gov/retrieval/lexical.py:197-199`; `template/governance/kernel/schemas/path-map.schema.json`, whose top level stays open.
- What happens: a repository writes `id_form:` or `idforms:` with valid entries. The reader finds no `id_forms`, nothing is declared, and the schema accepts the file. A question naming a nonexistent id in that form gets unrelated evidence instead of UNRESOLVED_IDS. It should have been refused loudly.
- Ordinary work: yes, because a one-letter typo in a key name is an ordinary slip.
- Consequence: fails open.
- Scope: out. Interface point 1, accepted by the CTO, keeps the top level open and the loader untouched. Fixing it would mean an unknown-key check or running the JSON schema at load time.
- Rests on: P-W2-146-1 (a), DEC-801, DEC-808, DEC-1010.
- Would reverse it: a check that runs in ordinary work refusing unknown top-level keys in `path-map.yaml`.

**R2 — a null `id_forms` declares nothing at run time** (low; the lead's known judgement, I agree)
- Where: `src/gov/retrieval/lexical.py:198-199`.
- What happens: entries written without the list dash and without indentation (`id_forms:` then `name: x` / `pattern: …` at the top level) parse as `id_forms: null`. Nothing is declared and no runtime check catches it, because the JSON schema is not run.
- Ordinary work: no, because it needs both the dash and the indentation lost. A bare `id_forms:` means "nothing declared", which is what it says.
- Consequence: fails open.
- Rests on: DEC-801, P-W2-146-1 (a).
- Would reverse it: evidence that agents write YAML lists that way in path maps.

**R3 — extra keys in an entry are ignored at run time** (low; the lead's known judgement, I agree)
- Where: `src/gov/retrieval/lexical.py:206-214`.
- What happens: an entry with `flags: i`, meant to make the form ignore case, compiles case-sensitive with no warning. A question writing the id in another case is not read as an id, so it gets no stop.
- Ordinary work: no, because the Interface and the schema say inline flags are the way, and a question in another case is not the declared form.
- Consequence: fails open, for case variants only.
- Rests on: P-W2-146-1 (a).
- Would reverse it: a documented form syntax that suggests a separate flags key.

**R4 — a pattern with an oversized repeat crashes instead of raising CONFIG_INVALID** (low)
- Where: `src/gov/retrieval/lexical.py:211-214`.
- What happens: `re.compile` raises OverflowError for a pattern like `a{4294967296}`, and only `re.error` is caught. `gov retrieve` stops with a traceback instead of the CONFIG_INVALID envelope; nothing is retrieved or offered.
- Ordinary work: no, because a repeat count above 2^32 is not written by accident.
- Consequence: other (fails closed).
- Rests on: P-W2-146-1 (a) point 5.
- Would reverse it: a Python version where `re.compile` raises `re.error` for this pattern.

**R5 — a pattern that swallows trailing punctuation can stop on an id that exists** (low)
- Where: `src/gov/retrieval/lexical.py:233-234`; `src/gov/retrieve/command.py:72-77`.
- What happens: a repository declares a loose form such as `SPEC-[\d.]+`. A question ending "…SPEC-4.2." reads the id as `SPEC-4.2.` with the full stop. No index line holds that string as a whole token, so an existing `SPEC-4.2` is stopped with UNRESOLVED_IDS. It should have been retrieved.
- Ordinary work: no, because it depends on the repository's own pattern being loose; the planted forms and the Interface's forms are bounded.
- Consequence: other (fails closed, a false stop).
- Rests on: DEC-1071 (5), P-W2-146-1 (a) point 3.
- Would reverse it: an adopted repository's real `id_forms` with a pattern that ends in a character class including `.`.

guard_refusals: none. Two sandbox write refusals, neither from the guard hook:
- `mkdir /tmp/w2-146-rv`: Read-only file system, a true refusal, so I used TMPDIR instead.
- `heavy_slot.sh` could not get its `/tmp` lock and waited until stopped: a true sandbox limit.