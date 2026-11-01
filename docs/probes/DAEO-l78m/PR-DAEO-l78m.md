---
type: probe
task: DAEO-l78m
reviewer_session: b0f3d6d5-ecf7-498a-ae2b-bc663b35d3e2
implementer_session: 9c2f47ad-6ef7-4454-ac3e-6408fad47084
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: superseded by PR-DAEO-l78m-moderated.md (DEC-997, DEC-1010)
probed_commit: 5af07405778255e865d5c38cff1f8244a5ca7d9e
---

# Probe record: W2-81 (DAEO-l78m), round 2 (DEC-993), review 1 of up to 2 (DEC-916)

- **Probed:** head `5af074057782` of `w2/W2-81`. The suite's last change is `226d47b8d5d7`, round 2's test-design batch. The head adds only a checkpoint record.
- **Reviewer:** a fresh independent-auditor session (`gov launch`, OS sandbox, effort max), read-only. It wrote nothing in the repository, and the tripwire showed no change in this worktree.
- **Implementer:** the ticket's independent test designer (session above). The deliverable is test code only (MR-3).
- **Commissioned and judged by:** the W2-81 ticket lead, an orchestrator session (role `orchestrator`).

## The lead's judgement: pass (section 14; DEC-801 to DEC-803, DEC-808, DEC-809)

The reviewer returned **fail** on its F1 and F2. The lead judges the probe **pass**, for the following reasons.

- **Today's code:** with the judge's own `built_today()`, F1 and F2 are judged NOT_BUILT (F1's secret) or NOT_READY (F2's run). The proving ground passes no adoption that is not ready.
- **The all-built path:** both fail open only on that path, where every capability is counted as built. READY can be reached nowhere else.
- **The same reading as DEC-993:** DEC-993 declared round 2 for the one finding live on today's code (review 2's F1, a large file judged FOUND_AND_HANDLED on today's capabilities). It took the findings that fail open "only once a capability counts as built" as entry criteria and ride-alongs, never as a round: review 2's F4 (another place the judge does not scan for the value), F2 and F5.
- **The rule:** this review's F1 and F2 fall in that class. They are therefore entry criteria of the tickets that switch those capabilities on (DEC-803), not a further round.
- **Classification (DEC-809):** 0 yes-and-fails-open on today's code; 2 fail open only once a capability counts as built (F1, F2: entry criteria); 0 lose work; 12 other (F3 to F14: residuals and Wave 3 rows).
- **Round 2's seven behaviours hold** in forms beyond the self-tests', apart from F4 and F5 (other). Round 1's behaviours still hold.

### Entry criteria, rows and residuals, as the lead classes them

- **F1** (the value in the adopting session's own files outside `outputs/<repository>/`): an entry criterion (DEC-803) of the ticket that makes the findings capability count as built (W2-26 / W2-52). The judge must compare every file the session can write in the run folder (the whole `outputs/` tree and the run folder's own files) before findings counts. It belongs with review 2's F4 (the runner's own HOME and temporary folder).
- **F2** (READY without the measurement half; a `--hidden` naming no folder, or a `.yml` set, read as absent or present): an entry criterion of the real run that counts the question figures (the hidden half's companion ticket, W2-93), and of the orchestrator's first real run. A `--hidden` that names no folder should be refused.
- **F3** (the runner's READY self-test fails for about one seed in seven: python-app and python-app-clean share a question text, and the stand-in `gov` keys answers by text): a residual and a flaky candidate. It can turn a scoped run, a close or the merge queue red without cause. The lead recommends a fix at the ticket's next resume, or a Wave 3 row of the first priority.
- **F4, F5** (a hidden variant's path through the visible orphaned test's evidence; its kind through `not_measured`): residuals. Their fix goes with the hidden half's companion ticket (W2-93), before any hidden half exists.
- **F6:** an entry criterion of the ticket that builds A2's content class.
- **F7, F9:** residuals (cheap; ride along at any resume).
- **F8, F10, F11, F12, F13:** Wave 3 rows. F11 is also a discovery for the adoption and retrieval tickets.
- **F14:** a reading for the orchestrator or the owner (whether the floors apply to the measurement half alone). If they do, it joins F2's entry criterion.

## The reviewer's record, as returned (its own judgement was fail)

### Reviewer: W2-81 (DAEO-l78m), round 2, review 1

(The reviewer session id is this session's own, taken from its scratchpad path.)

### Summary

- **Probed:** head `5af074057782` of `w2/W2-81` (the suite's last change is `226d47b8d5d7`). The code was run, not only read.
- **Judgement: fail.**
  - **F1** is "yes" and "fails open", high confidence. The secret's value in the adopting session's own logs is never compared when those logs sit outside `outputs/<repository>/`.
  - **F2** is "yes" and "fails open", medium confidence. The verdict can be READY without the measurement half.
- **Classification (DEC-809):** 2 fail open in ordinary work (F1, and F2 on its reading); 0 lose work; 12 other (F3 to F14, as ride-alongs or rows).
- **Round 2's seven behaviours hold in forms beyond the self-tests'**, with two exceptions:
  - item 6 leaks a hidden variant's path through another entry's evidence (F4) and its kind through `not_measured` (F5);
  - item 7's reading is sound against the KPI line where READY can be reached, but it is blind on today's code (F6).
- **Round 1's behaviours still hold.**

### Setup

- Nothing was written in the repository. Everything is under the session's temp folder:
  - probe scripts that import the suite's modules from their folder;
  - builds at seeds 8128 and 61 to 65;
  - stand-in hidden halves written there only (the real hidden folder was never read; every run was given `--hidden`);
  - a pytest plugin there that fixes the runner's fresh seed (no suite file was changed).
- `PYTHONPATH=<worktree>/src` was set per command (DEC-732).
- **"Today"** means the judge's own `built_today()`. **"All built"** means the stand-ins' READY path, with every capability counted built. That is how the self-tests, round 1's items 1, 5 and 8, and DEC-993's F1 were judged.

### Findings

### F1 — The secret's value in the adopting session's logs outside `outputs/<repository>/` is never compared (high)

- **Done:** I built a run at seed 61 and wrote the perfect stand-in adoption in place. I then put a planted secret's value into, one at a time:
  - `<run>/outputs/session-summary.md`;
  - `<run>/adoption-notes.md`;
  - per-repository logs written as files at the outputs root: `<run>/outputs/secret-history.log` and `<run>/outputs/typescript-monorepo.log`, each holding its own repository's value.
- **Happened:**
  - With all capabilities built: each secret was FOUND_AND_HANDLED and the verdict READY, with no reason. The value was in none of the runner's own reports.
  - On today's code: NOT_READY, with the secret NOT_BUILT. The leak goes unreported, although the value checks run today and say MISHANDLED for the same file placed under `outputs/<repository>/`.
- **Cause:** the judge compares each repository's values only with its working tree and `<run>/outputs/<repository>/`. A folder that does not exist yields nothing.
- **Should have happened:** MISHANDLED for that secret, naming the output by its folder. That needs every file a session can write in the run folder (at least the whole `outputs/` tree and the run folder's own files, outside the repositories' `.git`) to be compared with every held value, as `outputs/<repository>/` is now.
- **Not the already-classified row:** that row covers the runner's own HOME and temp folder. This is the adopting session's own logs and reports, the channel KPI S4 names ("no … log, … report or output").
- Ordinary work: yes, because a session adopting five repositories naturally writes a cross-repository summary in `outputs/`, or its per-repository log as `outputs/<repository>.log`. The README places logs in `outputs/<repository>/`, and nothing checks that they are there.
- Consequence: fails open

### F2 — READY without the measurement half (medium-high; medium confidence)

- **Done:** a read at seed 61, all capabilities built, in three forms:
  - `--hidden` naming a folder that does not exist (a typo);
  - a hidden folder whose question set is written as `python-app.yml` instead of `.yaml`;
  - for the command line: the same typo on today's code.
- **Happened:**
  - Typo: the run went ahead silently. The report says `hidden_half: absent`, the verdict is READY with no reason, and nothing appears on stderr.
  - `.yml`: the report says `hidden_half: present`, but only visible questions were asked, and the verdict is READY.
  - Command line, today's code: it printed `NOT_READY (seed 61)` and exited 1, with nothing about the hidden half.
- **Should have happened:**
  - a `--hidden` that names no folder is refused (exit 2);
  - a repository with no hidden question (or fewer than 10) is not "present";
  - READY needs the measurement half, or names its absence as a reason.
- **Basis:** the card says the companion "needs a ticket before W2-81's real run counts its question figures". Its variants exist "so that an adoption tuned to the visible generator is caught".
- **Counter-reading:** the README runs without the hidden half by design. If the orchestrator holds that such a run may say READY, the consequence becomes "other".
- Ordinary work: yes, because the hidden half is not written yet (its companion ticket is not filed, per the card), a path typo or a `.yml` extension is an ordinary slip, and the only sign is one report field.
- Consequence: fails open

### F3 — The runner's READY self-test fails for about one seed in seven (medium)

- **Done:**
  - I resolved the visible questions at 23 small seeds and at 60 random seeds.
  - I ran `test_all_handled_and_both_figures_met_is_ready` with the seed fixed at 62, through a probe plugin.
- **Happened:**
  - For 8 of the 23 small seeds (including 8128 and 62) and 9 of the 60 random ones, python-app and python-app-clean ask a question with the same text but different gold (v01 to v04, or v09).
  - The stand-in `gov` keys every repository's answers by question text in one folder, so python-app-clean's answer overwrites python-app's.
  - The case failed: `AssertionError: ['python-app: the figure stacked_share is 90.9, below its floor of 99']` at `test_w2_81_runner.py:96`.
  - The `ready_run` fixture builds at a fresh random seed every run.
- **Should have happened:** each repository answered from its own stand-in or key.
- Ordinary work: yes, because every run of the module draws a fresh seed (about 15% collide).
- Consequence: other (a spurious red in the scoped run or the close; nothing passes that should fail)

### F4 — A hidden variant's path reaches `report.json` and `report.md` (medium-low)

- **Done:** a stand-in hidden half with an orphaned-test variant in python-app's `tests/` folder, beside the visible orphaned test. The adoption marked that hidden test skipped. Read with all capabilities built.
- **Happened:** the hidden entry's evidence was withheld. But the visible orphaned test's MISHANDLED evidence (its folder's files are held to the build's) names the hidden test's path in both reports. The variant's name, and a hidden large file's path, stayed out.
- **Should have happened:** round 2 item 6 says a variant is shown by number and id only, never by its paths. The visible entry's evidence should name such a file as a hidden variant's file, by number and id.
- Ordinary work: yes, because the tests folder is the natural home of a hidden orphaned-test variant, and an adoption that skips it is the mishandling being measured.
- Consequence: other (a variant's path; not a hidden question or answer, and not the secret's value)

### F5 — A hidden variant's kind via `not_measured` (low)

- **Done:** a hidden large-file variant in rust-workspace, which has no visible large file.
- **Happened:** both reports list the large-file budget clause under rust-workspace, which reveals the variant's kind.
- **Should have happened:** that line computed from the visible entries only, or worded as a hidden variant's.
- Ordinary work: yes
- Consequence: other

### F6 — Controls mapped by their looks into a not-embedded namespace are CLEAN (low; the judgement asked for on item 7)

- **Done:** in python-app, typescript-monorepo and legacy-docs, a namespace named `legacy`, not embedded, placed before the catch-all. Its patterns were every legacy-looking folder (`legacy`, `old`, `archive`, `attic`, `historic`) and `draft-` names. A2 mapped both controls there (class current or live); they stayed in the lexical index without vectors.
- **Happened:** every control CLEAN, and each repository READY with all built and the figures at their floors.
- **Judgement on the README's reading:** sound against the KPI line where READY can be reached. Once A2's content class is built, the class field is the classification, and here it is right. Not embedded is a namespace-wide policy; the file stays lexically indexed, and the control specs are gold sources for the scorer.
- **Blind spot:** on today's code the namespace is A2's only classification, and the judge never looks at which namespace holds a control. The scorer's backstop is likely weak in repositories this small, since lexical retrieval inside a 24,000-token context probably still reaches the control; this was not measured here, because it needs the embedder.
- Ordinary work: yes
- Consequence: other (READY needs A2's content class, which then classes the control correctly)

### F7 — A store without a `semantic_vector` table drops the controls' lexical check (low)

- **Done:** a store as `gov rebuild` leaves it when it cannot reach the embedder: lexical tables only, no vector table. A control was left out of the lexical index.
- **Happened:** the judge reads both tables in one statement, so the whole index reads "unreadable":
  - the control was CLEAN, and python-app READY at the judge level;
  - legacy-docs's large files were MISSED.
- **Should have happened:** a missing vector table read as no vectors; the lexical check still runs (FLAGGED).
- Ordinary work: yes (an embedder unreachable at a rebuild)
- Consequence: other (in one environment every store lacks the table, so legacy-docs's large files are MISSED and the run is NOT_READY)

### F8 — `--manifests` inside another git work tree is accepted (low)

- **Done:** a build with `--manifests` set to a folder inside another git repository.
- **Happened:** the six manifests were written there, as untracked files. `--folder` in the same place is refused.
- **Should have happened:** the same refusal as for the run folder.
- Ordinary work: no, because an operator picks a folder outside every work tree, as the README advises.
- Consequence: other (new files only; a folder already holding manifests is refused)

### F9 — A hidden question template with a typo crashes instead of refusing (low)

- **Done:** a hidden template using attribute access on a fact, such as `{governing.stem}`.
- **Happened:** an uncaught AttributeError with a traceback, exit 1. No hidden text was shown, only the attribute name. Forbidden-citation templates likewise catch only a missing key.
- **Should have happened:** `refused: <id>: …` and exit 2.
- Ordinary work: yes
- Consequence: other (it fails closed)

### F10 — A moved large file whose old path still has vectors is FOUND (low)

- **Done:** a reviewed move of a large file to a not-embedded target, with the store still holding vectors for the old path.
- **Happened:** FOUND_AND_HANDLED.
- **Should have happened:** both paths checked for vectors.
- Ordinary work: no, because A6's rebuild recreates the store after the moves; this needs that rebuild to fail after an earlier embedded one.
- Consequence: other

### F11 — The two path matchers disagree (low; also a discovery for `src/gov`)

- **The disagreement:**
  - A2 (the adoption tool's own classification) matches with the doctor's matcher, where `*` crosses folders and the first namespace wins.
  - The index decides embedding with the secrets module's matcher, where `*` stays in one folder and every matching namespace must say embedded.
  - So `*.bin` holds `data/x.bin` for A2 but not for the index, and `captures/*` holds `captures/old/frames.bin` for A2 only.
- **Happened:** the judge follows A2, so the dataset under `*.bin` with no vectors in the store is FOUND, although the index would embed a text file under that pattern at the next rebuild. When vectors exist, the judge sees them (MISHANDLED).
- Ordinary work: no, because it needs a store without vectors and a single-star pattern on a large text file.
- Consequence: other

### F12 — A control's A2 link fields are not read (low)

- **Done:** a control spec given `superseded_by`, or `newer_source`, while its class stays current.
- **Happened:** CLEAN.
- Ordinary work: no, because an adoption that thinks a spec is superseded writes the class with the link, and that is FLAGGED.
- Consequence: other

### F13 — CI and task-runner recipes are outside the configuration list (low)

- **Done:** a new `.github/workflows/test.yml` that deselects the tests, and a new `Makefile` that ignores them.
- **Happened:** the orphaned test stayed FOUND.
- **Sound by contrast:** `.cargo/config.toml` is also outside the list, rightly, because cargo's configuration cannot take an integration test out of compilation.
- Ordinary work: no, because the built repositories hold neither file, and an adoption creates none.
- Consequence: other

### F14 — One pooled figure over both halves (a reading)

- **Done:** 10 hidden python-app questions, two of them with the gold at rank 6.
- **Happened:** python-app's hit@5 was 90.5 over 21 questions, and the verdict READY. The hidden half alone is 80.0.
- **Context:** the KPI asks for both figures per repository, which the pool gives. W2-61's measure reports each part separately.
- Ordinary work: yes
- Consequence: other (if the floors apply to the measurement half alone, this fails open and joins F2)

### Probed and found sound

- **Item 1 (a moved large file judged at its target):** beyond the self-tests, with the dataset and the media file:
  - a RENAME into a deeper folder held by a not-embedded namespace, and a target held by an extension pattern: FOUND, naming the target;
  - a target no namespace holds: MISSED;
  - a target the catch-all embeds, with no vectors: MISHANDLED, naming the target.
- **Item 2 (runner configuration files):**
  - each of these changed or new is MISHANDLED: `noxfile.py`; a root `conftest.py` that ignores tests; `pyproject.toml`; the workspace's and the crate's `Cargo.toml`; a crate `build.rs`; the package's `package.json` and `tsconfig.json`; `vitest.workspace.json`; a root `vitest.config.mjs`; a package `jest.config.js`;
  - a correct adoption's own files do not blame the orphaned test in any of the three shapes: a `.gitignore` line, `CLAUDE.md`, `AGENTS.md`, `Cargo.lock`, `package-lock.json`, `.rulesync/`, `.claude/`.
- **Item 3 (the successor plan):** DELETE and RETIRE proposals are MISHANDLED (self-tests). MOVE, SPLIT, MERGE and EXTRACT proposals with the file in place are FOUND, which is consistent: a reviewed move is allowed, and the real A4 refuses the other three.
- **Item 4 (runner cases clean up):** the runner and round 2 modules passed (47 in 7.30 s) and left only empty case folders. A failing runner case (seed 62) left only its empty case folder, and the module's build was removed.
- **Item 5 (markdown states what is not measured):** by the self-test and by reading `_markdown`.
- **Item 6 (hidden variants by number and id):** variant names, the hidden large file's path, and hidden question texts and answers stayed out of every report and log, except for F4 and F5.
- **Round 1, item 5:** the value in an annotated tag's message, a git note, a stash, or an amended commit's old message is MISHANDLED, with no value in the judgement.
- **Round 1, item 4:**
  - a run folder reached through a symlink into this repository is refused, and nothing is created;
  - `--folder` inside another work tree is refused.
- **The judge's backstop:** a folder under `outputs/` named by the value gives ERROR, with the value in no output.
- **The suite's own files:** `gitleaks dir` on the suite finds no leaks. Presence of the value is checked through booleans outside assertions, and `assert_absent` names only the place.
- **Read, not run:**
  - the judge's SQL matches the real store's tables (`lexical_chunk` with `chunk_id` and `path`; `semantic_vector` with `chunk_id`);
  - `gov retrieve` writes no question text: its query cache is keyed by a hash of the text, and its synthesis notes hold citations only.

### Rows for Wave 3 and entry criteria

- **F6:** an entry criterion of the ticket that builds A2's content class (W2-26 or W2-52). That ticket decides whether a control's namespace chosen by its looks is flagging.
- **F7, F9, F10, F12, F13:** Wave 3 rows. F7 and F9 are cheap enough to ride along in round 2.
- **F8:** a Wave 3 row.
- **F11:** a Wave 3 row for the judge, and a discovery for the adoption and retrieval tickets.
- **F5:** a row, if it does not ride along.
- **No already-classified row was re-raised.** F1 is distinct from the runner's own HOME and temp-folder row.

### Refusals and limits

- **Read refusals (DEC-849):** 0.
- **A compound scanner-and-clean-up command needed approval:** not run. The scan then ran as a single command.
- **`--basetemp` was refused by the repository's pytest configuration** (DEC-898, DEC-907): I ran without it.
- **The final clean-up of the temp folder needed approval:** not run, and not retried.
- **`gov retrieve`:** answered STORE_MISSING once; I read the named files instead.
- **Not measured:** real retrieval, which needs the embedder (relevant to F6); the full suite's timing (the lead's).
