# D-10's red-fix list: the review of W1-46's and W1-27's README maps made readable by gov accept (W2-96, DAEO-ouet)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-accept-maps-review.md`; branch `w2/W2-96-maps-d10-tests` at `48c2cd33b`; reviewer log `/home/usain/gov-os-worktrees/W2-96-maps-d10-tests/.gov-runtime/scratch/lead/log/D10-accept-maps-review.json`.
- verdict.py: READY (no blocking finding; F1-F3 out of scope, rows).

## Review record: W2-96 (DAEO-ouet), D-10's review of `48c2cd33b`, the W1-46 and W1-27 README maps

**Sandbox check (Step 0):** passed. (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-96` failed with "Read-only file system". (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`) and `git update-index --refresh` exited 0.
**ps check:** inside the sandbox, `ps` sees only its own processes (the shell and `ps`). No ollama or llama-server process of mine.

- **task:** W2-96 (DAEO-ouet). Read-only review of `48c2cd33b`, the map fixes for W1-46's and W1-27's READMEs. Head checked: `a4fe340f1cf3`.
- **status:** DONE
- **work_completed:**
  - Read the brief, EMG-common, JUDGEMENT, the commit, both READMEs, both tickets' KPI lines and DEC-242.
  - Read the map reader (`src/gov/accept/runner.py`), the opt-in mechanism (`tests/conftest.py`) and the opt-in lists.
  - Collected both folders' default runs (collect-only).
  - Checked every map item against what the default run collects, using the reader's own matching rules.
  - Checked the trailers and that every cited decision is ACCEPTED.
- **files_changed:** none.
  - Writes outside the trees: Step 0's blob and index refresh, and a scratch folder under the sandbox's TMPDIR, now removed.
  - `git status --porcelain` is empty.
- **evidence:**
  - **Word diff of `48c2cd33b`:** only the KPI cells changed (W1-46 rows 92, 95, 97, 100, 104) and the ten headings (W1-27 lines 9–136). Every Tests cell is unchanged.
  - **Reader:**
    - `runner.py:52-61`: a cell's names are read from its start and stop at the first character that is not `/ , ; and`.
    - `:94-96`: a table needs a Test/File column.
    - `:121-131`: a row id (`[x]`) matches only in the form `file::name[x]`.
    - `:134-137` and `:435-440`: a named test that no collected case matches fails its line, and any failed case fails the outcome.
    - `:333`: the runner keeps `GOV_TESTS_OPTIN` in the child's environment.
  - **Opt-in:** `tests/conftest.py:37-53` and `:265-317`: listed cases are deselected, not skipped; a `rep:` entry keeps only the first row of a parametrised test.
  - **Lists:** `tests/optin-lifted-guard.txt:120` (lifted) and `tests/optin-lifted-breadth.txt:619` (breadth, a `rep:` entry).
  - **Collections:** W1-46 collects 134 of 493 cases (359 deselected); W1-27 collects 67 of 179 (112 deselected).
  - **Scratch:** 16K and 4 inodes before removal.
- **tests:**
  - Two collect-only runs (W1-46 and W1-27, default) through `heavy_slot.sh`, with the worktree's `src` on `PYTHONPATH`, an empty HOME, `PYTHONUSERBASE=/home/usain/.local` and my own TMPDIR. No case executed.
  - DEC-1012's `-m "not local_only" -k "not real…"` was not applied. It would remove cases `gov accept` collects (W1-46's 12 live cases, W1-27's `…real_registry…`), and collection starts nothing.
  - One reader call on W1-49's README.
  - `gov accept` was not re-run; the helper's runs stand.
- **discoveries:**
  - The reader skips both "KPI map after D-4's cut" tables (they have no Test/File column) and reads the older tables.
  - W1-46's success-10 file is cut by `lifted`, not `breadth`.
  - 44 of W1-46's 134 default cases count toward no line.
  - The reader silently drops names after the first (F1).
- **risks:** F1 is a fail-open waiting for the next map fixer. Acting on the brief's "breadth" attribution would not clear success-10.
- **lessons:** check what the reader takes from a cell, not what the cell says.
- **proposed_decisions:**
  1. **W1-27 success-8:** fix the item form to `test_w1_27_schema.py::…[row]` now; it lowers nothing. Whether `gov accept` should run with `breadth` included goes to the CTO. Confidence: medium.
  2. **W1-46 success-10:** record it as feature-gated (DEC-803). It is an entry criterion of the ticket that switches the full guard back on, not a map change. Confidence: medium-high.
  3. **F1:** a reader row: refuse a KPI cell with text the reader cannot take after the first name, or compare the map's lines with the ticket's `kpis:`. Confidence: medium.
- **unresolved:**
  - Whether D-10's declared way runs `gov accept` with the opt-in suites included.
  - `D10-REDS.md` in this tree has no row for this map fix.
  - Per-line results with `breadth` included were not measured.
- **recommended_next_action:** READY, computed from the verdict block (no in-scope finding). Merge per the queue, record F1–F3 as rows, and decide items 1 and 2 above.

**Refusals (both taken as given):**
- **Write tool:** it asked for permission to write a scratch script under the sandbox's TMPDIR, and nobody can answer that prompt in this session. No file was written instead.
- **Guard:** it refused a one-call scripted analysis (DEC-820 (c)/(d)), asking me to "name the folder the listing starts at" (DEC-953 item 2). I did not retry that call. I used collect-only runs on named folders and matched items by reading, which follows the guard's own instruction.

---

### Probe record
`task: DAEO-ouet`
`decisions: [DEC-959, DEC-1061, DEC-242, DEC-803, DEC-801, DEC-1010]`

No superseded or PROPOSED rule is in use: DEC-242, DEC-866, DEC-959, DEC-1061 and DEC-1109 are all ACCEPTED.

**Check 1, same meaning: yes.**
- Applying the stated substitutions to the old text gives the new text exactly. No item changed, so no case dropped or moved.
- **W1-46:** the rows now name the lines their old text meant:
  - S1, F1, F2, F8
  - S4, F4, F5
  - S6, F6, F7
  - S9, F9
  
  Under the old wording the reader kept only S1, S4, S6 and S9.
- **The DEC-242 row is success 1's:**
  - its own words: "refusals in the words of success 1";
  - DEC-242's text: "refuses to launch for an unknown ticket, a ticket that isn't `in_progress`, or a ticket of another role";
  - D-4's own S1 row (placed "by its words") already names `test_an_unknown_ticket_refuses_the_launch` and `test_a_ticket_that_is_not_in_progress_refuses_the_launch`.
  
  The row's item is the whole file, so success-1 now also counts the file's three launch controls. That makes it stricter, never looser.
- **W1-27:** the ten headings are eight "Success" and two "Failure"; the N and the items under each are unchanged.
- **Unchanged rows read by no one:** the DEC-271/273, DEC-313/314 and DEC-317 rows after the blank line at line 105 are skipped. This was true before and after the revision (F3).

**Check 2, the remaining fails come from D-4's cut and the item form, not from this revision.**
- **W1-27:** only success-8 fails. Its four `test_missing_required_top_level_key_names_the_key[row]` items cannot match in that form (`runner.py:124-131`). That includes `[state_class]`, which *is* collected. The other three rows are cut by the `rep:` entry at `optin-lifted-breadth.txt:619`.
- **W1-46:** only success-10 fails, on a row this revision did not touch. Its file `test_w1_46_options_after_the_destination.py` has no collected case: it is listed in `optin-lifted-guard.txt:120`, "the full guard (G-4/G-6; DEC-1061 (3a))". That is the `lifted` suite, not `breadth`. Every other item that names a test matches at least one collected case.
- **Could a fix inside the READMEs clear them without lowering a line? No, for either line.**
  - Success-8's form fix lowers nothing, but the line would still fail on the three `breadth` rows. It clears only with `breadth` included: `GOV_TESTS_OPTIN` passes through the runner (`runner.py:333`; read at `conftest.py:288`). That is predicted from the code, not run.
  - Success-10 clears only by dropping its batch-7 file, which lowers the line. Including `lifted` would run the switched-off guard's cases.

**Check 3, trailers: present and parsed by git.**
- Task: DAEO-ouet
- Implements: DEC-1109, DEC-959
- Role: independent-test-designer
- Rewrite-Reason: DEC-959 item 6, DEC-866
- Co-Authored-By: Claude Opus 5.5

Only the two READMEs changed, and the integrate merge did not touch them.

**Findings.** Classification: 0 in scope, 3 out of scope. No round is proposed.

**F1 (scope out).**
- **Behaviour:** a KPI cell such as "Success 4 [CAP-61.c], failures 4, 5" is read as success 4 alone. The other lines are dropped without a refusal, and `gov accept` reports only the lines a map names. This revision worked round it correctly.
- **Same shape elsewhere:** W1-49 rows 88, 89 and 94 (failures 1, 2 and 4 are named nowhere else the reader takes), and W2-87 row 36 (its failure 4 is also named on row 70). W1-49's map is refused today because of another row. Whoever fixes that row the way DEC-242's row was fixed leaves those three lines unchecked.
- **Should have:** the reader should refuse the cell, as it refuses a heading it cannot read.
- Ordinary work: yes, because a designer writes cells like these in normal map writing, and they exist in two other maps today.
- Consequence: fails open.
- **Would reverse it:** a reader run that refuses such a cell or returns every line in it, or a check that fails when a map names fewer lines than the ticket's `kpis:`.

**F2 (scope out).**
- **Behaviour:** the brief puts success-10's missing file in `breadth`. It is in `lifted`, so including `breadth` leaves the line failing.
- Ordinary work: yes, because the next agent would act on the brief's attribution.
- Consequence: other (a misdirected fix; the line stays failing).
- **Would reverse it:** a W1-46 collection with only `--optin=breadth` that collects that file.

**F3 (scope out).**
- **Behaviour:** 44 of W1-46's 134 default cases count toward no line. That is 34 cases in files that only the skipped rows or the batch tables name, plus 10 live cases the KPI table names only in prose. The skipped rows' stated lines (S1, S2, S8) therefore do not show them. A failure among them still fails the outcome (`runner.py:439`).
- Ordinary work: yes, because anyone reading the per-line report meets it.
- Consequence: other.
- **Would reverse it:** a per-line report that counts those cases.

**Probed and found sound:**
- **Both maps now read:** each README now gives the reader a map (`ACCEPT_MAP_UNREADABLE` is gone), and every KPI line of both tickets is named: W1-46 11 success + 9 failure, W1-27 8 + 2.
- **Fails closed:** a line fails when a file it names has no collected case.
- **No line lost evidence:** no line lost an item, and every added line has collected cases in the files it names.
- **Scope:** no implementer touched acceptance material; the commit's role is the test designer's.

```verdict
{"kpis": [{"kpi": "accept-maps-readable", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
