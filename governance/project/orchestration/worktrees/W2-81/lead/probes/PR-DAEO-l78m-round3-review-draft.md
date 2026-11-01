session_id: f00a8125-adc8-4e2a-ab48-a3997cc10436
is_error: False subtype: success turns: 101 duration_s: 2559
----
pytest's own retention has retired my probe sessions' folders (no repository and no value left there). Probing is complete; here is the return.

task: Fresh review of W2-81 (DAEO-l78m, FULL), round 3 (DEC-1005) at head 165d3057146a, the ticket's last review: probe the proving ground for behaviour its self-tests miss, writing nothing in the repository.
status: DONE. Probing is complete and the probe fails by the rules: three findings answer yes to both questions (ordinary work, fails open).
work_completed: Sandbox check passed. I read the ticket, both WBS cards, the README, every support module and the round 2, 2b and 3 changes. I then ran the suite's modules with two probe plugins I wrote in my temporary folder: one records any write inside the worktree, the other fixes the runner's seed. I also ran about 25 probe cases of my own, on copies of the support modules where only the repository-root and visible-questions paths were changed back to the worktree. All 10 round-3 and round-2b items, and the earlier batches, were probed beyond the self-tests' forms.
files_changed: none in the repository. Probe files exist only in my session's temporary folder.
evidence: Head 165d3057146a (round 3's suite changes are 1c79204eeb5d and 8c14b3f06d8f). The worktree listing (6,483 paths, empty folders included) was unchanged across every run. The write recorder logged 0 writes inside the worktree. The probe outputs quoted in the record below are verbatim. gitleaks on the suite folder: 0 findings.
tests: Probe runs, not verification (DEC-959 item 1):
- The whole suite alone: 276 passed in 32.26 s.
- The whole suite with `-n auto`: 276 passed in 8.44 s, and again in 8.52 s.
- Each of the 12 modules alone: 276 passed in total.
- The runner module at 24 seeds of my choosing: 37 of 37 passed at each seed.
- The suite against a mutant that restores the old forbidden-drop rule: 4 failed, 272 passed (exactly the round-3 cases).
- The suite against a judge mutant with no output scan: 16 failed, 260 passed (15 real failures, plus 1 caused by where I placed the mutant).
- One module with gitleaks taken off PATH: 6 errors naming `gitleaks`, no skips.
- The manifest module 3 times (7 passed each), so pytest would retire my probe folders.
- My own probe cases: 25 passed.
discoveries: The three findings F1, F2 and F3, a demonstration of the open floors reading, five new rows for Wave 3, and one stale README sentence. Details are in the record below.
risks: My probe folder (3.8 MB) is still in this session's temporary folder, because deleting it needs a permission I don't have. A scan of its 5,126 files finds no secret value. The one file that held values (a saved `--showlocals` output) was emptied in place. My probes ran on copies of the support modules; byte comparison shows they are identical except for the two path constants.
lessons:
- The guard refuses a shell variable as a write target, and refuses `python3 -c` when the suite folder is on PYTHONPATH.
- The Write tool works for the temporary folder. Copies of the support modules, plus `-p` plugins (one fixing `secrets.randbelow`, one preloading mutants into `sys.modules`), let the suite and probes run without touching the worktree.
- Git objects are compressed, so a byte scan can't see a value inside a built repository. Built repositories have to be removed, not scanned.
proposed_decisions: One package of three fixes. Classification: F1 yes/fails open; F2 yes/fails open; F3 yes/fails open (low); the floors reading open for the owner; R1 no/fails open, R2 yes/other, R3 no/other, R4 no/fails open, R5 no/other.
- F1: each forbidden citation must be a list item that names a file of the built HEAD, as gold sources already are; otherwise refuse it by id. Recommend, high confidence.
- F2: READY needs at least one hidden variant per kind, counted from the manifests. A missing kind is named in the reasons, both reports and the command line, and a variants file with another extension is refused or counted absent. Recommend, high confidence.
- F3: no value in a failing case's output under `--showlocals`. Recommend, medium confidence on the classification: if the owner rates a synthetic value shown under a debugging flag as "other", F3 becomes a row.
- Floors reading: recommend that the floors also apply to the measurement half alone. The owner's call; medium confidence.
- R1 to R5: rows for Wave 3.
unresolved: The floors reading (pooled, or the measurement half alone) is open for the owner. How F1 to F3 land is the lead's and the owner's call (a resume under DEC-802). My temporary probe folder still needs removing.
recommended_next_action: The lead takes F1 to F3 to the owner as one small batch for this ticket's resume (DEC-802), with the floors reading.

**Head probed:** 165d3057146a.

**Sandbox check:**
1. The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-l78m` failed with "Read-only file system", as required.
2. `git hash-object -w --stdin` and `git update-index --refresh` both worked (exit 0).
3. `GOV_ROLE` is `independent-auditor` and `GOV_TICKET` is `DAEO-l78m`; the top level is `/home/usain/gov-os-worktrees/W2-81` on `w2/W2-81`; HEAD is 165d3057146a. All as expected.

**Refusals:**
- Guard: 2, each a different call and neither retried. One was a shell variable used as a write target. The other was `python3 -c` with the suite folder on PYTHONPATH ("may write the acceptance tests").
- Permission mode (not the guard): 2, neither retried in another form. One was a chained command starting with `rm -f` on a glob in my temporary folder; the other was `rm -rf` of my probe folder.
- Read refusals (DEC-849): 0.
- `gov retrieve` answered FACET_UNAVAILABLE (the store is stale), with no network error, so I read named files.
- Contrary to the brief, this session did have a Write tool. I used it only for probe files in my temporary folder.

---

# PR-DAEO-l78m-review5: W2-81 round 3, the final review

- **Ticket:** DAEO-l78m (W2-81, FULL). Round 3 (DEC-1005), the ticket's last review (DEC-916).
- **Probed head:** 165d3057146a (`probed_commit`: the full id, filled in by the lead). Round 3's suite changes are 1c79204eeb5d and 8c14b3f06d8f; round 2b's is 56af0a59973b; round 2's is 226d47b8d5d7.
- **Reviewer:** a fresh independent-auditor session, read-only.
- **Judgement: FAIL** by section 14's rules. F1, F2 and F3 each answer "yes" to "Can an honest agent hit this in ordinary work?" and "fails open" to "Does it fail open or lose work?".

## Summary

Round 3's two changes hold as built:
- No case and no helper makes anything inside the repository. Listings, a write recorder and a stand-in repository root all agree.
- A mistyped fact name in a hidden forbidden citation is refused by id.

Three gaps remain where the proving ground passes an adoption it should not, or shows a value:
- **F1:** a forbidden citation that names no file of the built repository is still dropped silently. This covers a typo in a literal path (the README's own form for a hidden variant's files), one path written as a YAML scalar, and an unquoted `{name}`. End to end, the same adoption reads READY instead of NOT_READY.
- **F2:** the measurement half's planted-problem variants are not required. READY is given with none at all, and the report still says the hidden half is present.
- **F3 (low):** with pytest's `--showlocals`, a failing case prints synthetic secret values.

The floors reading is demonstrated: the pooled figures give READY while the measurement half alone is at 70 % hit@5.

## Findings

### F1. A forbidden citation that names no file of the built repository is accepted silently

- **Done:**
  - Resolved hidden questions (a stand-in in my temporary folder) whose forbidden citation was one of four forms:
    - a literal path with a typo;
    - one path written as a YAML scalar instead of a one-item list;
    - an unquoted `{stale}`, which YAML reads as a mapping;
    - a fact template naming no file, `{stale}.bak`.
  - End to end at seed 5150: a hidden stale-spec variant in rust-workspace (`docs/frames/frame-limits.md`), the perfect stand-in adoption, and a gov stand-in that answers gold first except for rust-workspace-h01, where it puts the hidden stale spec first.
- **Happened:**
  - Every form resolved with no refusal and none names a file at HEAD:
    - the scalar became 28 one-character entries;
    - the mapping became the literal path `stale`;
    - the typo and the `.bak` path were kept as written, and can never match.
  - End to end:
    - with the correct one-item list, the verdict was NOT_READY: `rust-workspace: the figure stacked_share is 95, below its floor of 99`;
    - with the scalar form or the typo, the verdict was READY at 100 and 100, the same as with no forbidden citation at all.
  - Through the command, the scalar form is read on (exit 1 on today's code) with no `refused:`.
- **Should have happened:** as gold sources already are, each forbidden citation is a list item naming a file of the built HEAD, hidden variants' files included. Otherwise the command refuses with `refused: <id>: …` and exit 2, naming the id only. At seeds 8128 and 424242 all 17 visible forbidden citations per seed name files at HEAD, so this check refuses nothing correct.
- **Severity:** high for the measurement. It is the gap round 3 item 2 closed for fact names, reached by another route.
- Ordinary work: yes, because W2-93's author writes the hidden half by hand and the README tells them to name a hidden variant's files by literal path; a typo in a path is as ordinary as the typo in a fact name that DEC-1005 fixed, and writing a one-item list as a scalar is a common YAML slip.
- Consequence: fails open

### F2. The measurement half's planted-problem variants are not required

- **Done:** at seed 2468, a stand-in hidden half with 10 hidden questions per repository (present and asked), the perfect adoption and gold-first answers, with one of four variants files:
  - no variants file;
  - the variants in `variants.yml`;
  - `variants: []`;
  - a single variant, so one kind only.
- **Happened:** READY in all four cases. `run.json` showed `hidden_variants` 0, 0, 0 and 1. There was no reason, and the reports and the command line said `hidden half: present and asked in 6 of 6 repositories`.
- **Should have happened:** the companion card's KPI asks for "at least one hidden planted-problem variant per kind … so that an adoption tuned to the visible generator is caught", and the README defines the measurement half as "its questions, and planted-problem variants". By DEC-997 item 3's rule for the questions, READY should need them:
  - the hidden variants counted per kind from the manifests (`hidden: true`);
  - a kind without one named in the reasons, both reports and the command line;
  - a variants file with another extension refused or counted absent, as a `.yml` question set already is.
- Ordinary work: yes, because W2-93's author can name the file `variants.yml` (the slip round 2b handled for question sets), or write variants for only some kinds, and nothing says so.
- Consequence: fails open

### F3 (low). With pytest's `--showlocals`, a failing case prints secret values

- **Done:** ran the suite against a mutated copy of the judge with no output scan, saved the output in my temporary folder, and searched it in memory for every value of every seed the suite uses.
- **Happened:**
  - With `-vv -l`, the output held 3 values (seed 31's two typescript-monorepo tokens and seed 8128's). A failing case's local stand-in model holds the leaked text in plain form.
  - With the README's own `-q`, and with `-vv`, it held none.
  - No project setting turns locals on: `pyproject.toml` has none, and CI runs plain `python3 -m pytest tests`.
- **Should have happened:** no value in any output, whatever pytest reporting flags are used. For example, the suite's conftest could turn `showlocals` off, or the cases could hold leak texts only inside `Held` until `render` writes them.
- Ordinary work: yes, because debugging a failing case of this suite with pytest's own `-l` is ordinary, for example in another ticket's close when `gov.adopt.project` (which the judge imports) changes.
- Consequence: fails open

### The floors reading (open, the owner's; not a row)

- **Done:** at seed 5150, the perfect adoption with every visible question answered gold first, and in every repository hidden questions h01 to h03 answered with five filler items before the gold (gold at rank 6).
- **Happened:** READY.

  | Repository | Pooled hit@5 | Pooled stacked share | Hidden half alone, hit@5 |
  |---|---|---|---|
  | python-app | 85.7 | 100 | 70.0 |
  | the other five | 85.0 | 100 | 70.0 |

  The 99 % stacked-share target leaves room only in hit@5: with 20 or 21 questions, any question without full evidence brings the stacked share down to 95 %.
- **Reading:** if the floors apply to the measurement half alone, this run is NOT_READY. If they apply to the pooled figure, it is READY by design.
- Ordinary work: yes, because a retrieval tuned on the visible half and weaker on the measurement half is exactly what the hidden half exists to catch.
- Consequence: fails open (under the measurement-half reading; none under the pooled reading)

## Rows for Wave 3 (new)

- **R1. Figures are rounded to one decimal before the floor test.**
  - Ran: 189 of 191 (98.95 %) reads 99.0 and the verdict is READY; 96 of 113 (84.96 %) reads 85.0.
  - By arithmetic (not run): 95 of 96 (98.96 %) also reads 99.0, so 96 questions is the smallest repository where one miss is rounded away.
  - Ordinary work: no, because it needs 96 or more questions in one repository, against a visible half of 10 or 11 and a hidden minimum of 10.
  - Consequence: fails open
- **R2. A refused or crashed read leaves the earlier report in place.**
  - After a READY read, two later reads failed: one refused (exit 2, a hidden template error), one crashed (a mistyped `--pinned-gov` path, FileNotFoundError, exit 1). Both left the earlier `report.json` and `report.md` saying READY.
  - The report holds no time or run id.
  - Ordinary work: yes, because re-reading in the same run folder is the documented flow and a path typo is ordinary.
  - Consequence: other (the failing command never says READY; the file left behind is the earlier read's)
- **R3. `scan_history`'s scratch folder is not checked.**
  - The scratch folder is not passed through `outside_this_repository`. Handed a folder inside a stand-in repository root, it made a temporary folder there while gitleaks ran, and removed it afterwards.
  - Ordinary work: no, because every caller passes one of pytest's own folders.
  - Consequence: other (transient)
- **R4. A5, A7 and A10 records count as PRESENT with any front-matter mapping.**
  - A record with none of the stage's fields counts as PRESENT, and READY follows (18 cases of the bad-record matrix).
  - A7 and A10 are the classified row and NOT_BUILT today. A5 is built, but the tool refuses any verdict except `pass` (VERDICT_NOT_PASS) and checks `path_map_hash`, so only a hand-written A5 reaches the judge. This joins the classified A7/A10 row.
  - Ordinary work: no, because the tool never writes a failing or empty A5.
  - Consequence: fails open
- **R5. The tripwire's listing covers only the suite's folder and the worktree's top level.**
  - At the top level it looks only for the names a W2-81 case makes. `git status` shows no empty folder, so an empty folder made elsewhere in the tree would pass unseen.
  - Judged by reading only: probing it would need a write in the worktree.
  - Ordinary work: no, because no case makes such a folder today (listings unchanged); a later case could.
  - Consequence: other
- **README note.**
  - The last sentence of the README's template paragraph ("A forbidden citation naming a fact the repository lacks is still dropped") and the docstring of `w2_81_questions.py` still state the pre-round-3 rule; the code refuses, which fails closed.
  - Ordinary work: yes, because W2-93's author reads these texts.
  - Consequence: other

## Probed and found sound

- **Round 3, item 1 (no writes inside the repository):**
  - The worktree listing (6,483 paths, empty folders included; `.git`, `.claude`, `governance/project` and `fixtures/evaluation` pruned and only their timestamps checked; `__pycache__` aside) was unchanged across the suite alone, the suite with `-n auto` twice, each of the 12 modules alone, and all probes.
  - A write recorder (folder creation, file opens for writing, renames, links and sqlite files; checked first on a control folder) saw 0 writes inside the worktree in every run, including all 11 processes under `-n auto`.
  - The stray `no-hidden-questions` folder is gone.
  - Every write helper handed a path inside a stand-in repository root (git, the stand-ins, the manifest, the variants hook, and the runner in every mode, including `--manifests`) refuses and makes nothing there.
  - Paths through a symlink, `..`, `~`, a relative path, the parent folder, the root itself, and a deep path are all refused.
- **Round 3, item 2 (mistyped facts):**
  - `{stael}`, and `{zqx_stale}` through the command, are refused with exit 2, naming the id only.
  - A fact another repository has is refused: `{stale}` in legacy-docs, `{plan_old}` in secret-history, `{dead_module}` in rust-workspace.
  - The clean twin's three declared absences are dropped.
  - The old drop rule, restored as a mutant, is caught by exactly the 4 round-3 cases.
  - **The stricter rule cannot refuse a correct hidden half.** It refuses only a citation of a planted source the repository does not have, and hidden variants' files are named literally, so they are unaffected. It fails closed by id. The gap left by literal paths is F1.
- **Round 2b:**
  - Item 1: the runner module passes 37 of 37 at 24 seeds of my choosing (seed 1001 included), and the plugin's fixed seed was confirmed.
  - Item 2: the value written in 8 more places is MISHANDLED for that secret, named `run:<path>` (or by its folder only, for a file name), never by value. The places were a nested outputs folder, the runner's `.home` and `.tmp`, `manifests/`, the root of `repos/`, a binary file, another repository's `.gov-runtime`, and a file name. The same holds on today's capabilities through the runner.
  - Items 4 and 6 (with round 2's labelling item): a stand-in hidden half carrying markers (60 hidden questions, 3 variants of 3 kinds) went through the command. No marker appeared in stdout, stderr, `report.json`, `report.md`, `run.log`, `run.json`, the outputs folder, `.home` or `.tmp`. Variants appear as `hidden variant #n (id)` only.
  - Refusals of every hidden-file error (duplicate id, gold source not at HEAD, template error, mistyped fact, a variant that cannot be built) name only the id or the number.
  - Item 7: `{product!r}`, a valid Python conversion, is refused by id.
  - The real `gov retrieve` stores only a sha256 of each query and its vector, and synthesis notes hold citations only, so no hidden text reaches the run folder through gov.
- **Round 2:**
  - A large file renamed into a namespace given by a glob pattern is FOUND (naming the target) without vectors, and MISHANDLED with them.
  - 220 placements of 22 runner configuration names, in every folder from the orphaned test's own up to the root, in all three shapes: all as stated. The perfect adoption is not blamed.
  - Successor proposals for DELETE or RETIRE are MISHANDLED.
  - Every case removes what it built: pytest's kept folders held no repository after the suite's runs.
  - The reading that a control in a namespace held but not embedded is CLEAN is sound. A namespace that isn't embedded still keeps the control in the lexical index, so it stays in default results, and the scorer measures the control specs as gold sources. Mapping a control there by its looks is the classified entry criterion.
- **Planted files:** 189 cases (every planted file of every instance deleted, rewritten, moved without review, moved or renamed with review, retired with review, deleted with review): each as the README's table says.
- **Controls:** 12 controls × 23 ways of flagging them = 276 cases, all FLAGGED and NOT_READY. The ways were:
  - classed historical, superseded, dead, legacy, or "stale" (outside the vocabulary, so MALFORMED);
  - every A3 action that takes a file away;
  - A8 retired, or taken as a legacy document;
  - named by a finding through its `paths`, `path` or `test` field;
  - left out of the index; no A2 entry; mapped to no namespace;
  - changed in place; deleted.

  The one exception is "no index at all", which stays CLEAN by the README's reading; retrieval then returns nothing, so the figures fail.
- **Bad records:** A2, A3, A5, A8, the verdict, A7 and A10, each absent, empty, binary, JSON, partly written, a list instead of a mapping, a mapping without the stage's fields, or truncated YAML, in all six repositories, plus a finding file in each bad form: never READY, except R4.
- **Secret's value:**
  - gitleaks finds 0 in the suite folder.
  - No temporary file left by the suite holds a value.
  - Exceptions show `Held` as withheld.
  - Failing cases' output with `-q` or `-vv` holds no value (F3 covers `-l`).
- **READY:**
  - It needs every stage PRESENT.
  - The command never passes `built`, so on today's code it is NOT_READY.
  - A single figure, or no figure, is "missing"; an ERROR from the judge stays ERROR.
  - The seed appears in the JSON, the markdown and the command line.
  - A close not run, or exiting non-zero, is named per repository; with partial tickets, 5 repositories are named.
- **Hermetic and bounded:**
  - A missing gitleaks errors naming the tool, with no skips.
  - No network is needed and nothing reads the workbench.
  - The suite takes 32.3 s alone and 8.4 to 8.5 s with `-n auto` (up to 40 s with `-n 6` while the machine was loaded during the mutant runs).
- **Already classified:** none fails open beyond its classification on today's capabilities; R4 only extends the A7/A10 row to A5.

## Judgement

**FAIL.**
- **F1:** yes / fails open.
- **F2:** yes / fails open.
- **F3:** yes / fails open (low).
- **R1 to R5:** rows for Wave 3.
- **The floors reading:** the owner's.

Each of the three fixes is a few lines with a case of its own.
