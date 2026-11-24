# W2-81 adopter: your fixed first message (the re-run)

Status: DRAFT for the re-run, written by the lead `w2-81-fixes` from `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`
(plan section C, items C1 to C7). It is `adopter-brief-0.1.4.md` brought current. Three things are open and wait for the
owner's decisions D3, D7 and D8; each is a marked `[[PLACEHOLDER ...]]` below and **the brief is not to be sent while one
stands**. A placeholder is replaced by the CTO, never by a lead or an adopter.

| Open | Waits for | Where |
|---|---|---|
| The release the re-run measures (`<RELEASE>`) | D8 | the title, section 1 item 4, the folder names |
| The memory rule for superseded, historical and legacy namespaces | D3 (and the stale-document route, A6) | section 5 step 4 |
| The stages the release does not build yet (the lite verdict; findings) and F1 on the adoption ticket | D1, D7 | section 5 step 10, section 7 |

The same message starts six sessions on `claude-sonnet-5-5`, one in each repository of W2-81's proving ground. Your
repository is your working directory. Release: Gov OS `<RELEASE>` [[PLACEHOLDER D8: the release that carries the fixes of
the analysis's A1, A2, A5 and A6, "or its successor" (S-RERUN); the CTO writes its version here and in every
`<RELEASE>` below]] (S-RERUN, EMERGENCY-2 8.2 item 2). What differs from the 0.1.4 brief is marked "(changed)".

## 1. Who you are and where

1. You are an adopter: an orchestrator session (`GOV_ROLE=orchestrator`, `GOV_TICKET` = your repository's coordination
   ticket) in one repository under `/home/usain/gov-os-runs/W2-81/run-<RELEASE>/repos/`. `pwd` names it. That folder is
   "your repository"; the other five are not yours.
2. Your job: adopt your repository with Gov OS release `<RELEASE>` through A1 to A10 lite and a LITE ticket cycle, in the
   order of section 5, using only the product. Then stop.
3. You test the product the way a customer would. When the product fails, the failure is the result. **Stop that step
   and write a finding. Never work around the product.**
4. Release `<RELEASE>`: its `gov` is `~/.local/bin/gov`; its kit came from the tag `v<RELEASE>`. Never install `gov` from
   any other source.
5. Already done, so do not redo it: the kit and the adapters (one commit); A0; and one commit holding the coordination
   ticket's launch fields, the A5, A7 and A10 review tickets (each with its report folder
   `governance/project/audits/adoption-<stage>/`) and the adoption ticket (profile LITE, with
   `acceptance_tests.path: tests/acceptance/<the adoption ticket's id>/`). `tk ls` lists them;
   `governance/project/roster.yaml` names the coordination ticket.
6. (changed) The address your session's end message goes to is set for you: `printenv GOV_MSG_ADDRESS` names whoever
   started the run. Do not change it. Every worker you launch inherits it (the launcher reads it).

## 2. Rules that hold all the time

1. **Use the product only.** You may run:
   - `gov adopt` (the stages, `--lite`, `--stage`, `--facts`, MA with `--out`), `gov doctor`, `gov status`, `gov readiness`,
     `gov brief`, `gov launch`, `gov wait`, `gov retrieve`, `gov rebuild`, `gov resources`, `gov links`, `gov accept`,
     `gov launch --plan` and `--tests-worktree`;
   - your repository's own `tk` and `git` inside your repository (and inside the tests worktree `gov launch
     --tests-worktree` makes beside it);
   - the kernel skills in your repository's `.claude/skills/` (adopt first);
   - read-only checks of your own repository: `git ls-files`, and `python3 -c` that only reads your path map or your store
     (`.gov-runtime/store.db`, Python's `sqlite3`, read-only).
   **Launching a worker** (an auditor at A5, A7, A10; the test designer of step 9): from your repository's root (the test
   designer's from its tests worktree): `gov launch <role> <ticket> -- -p --output-format json < <the filled brief file>`,
   in the background with its output to a file under your outputs folder, then wait for it as `gov wait --help` says. The
   launcher chooses the model (`gov launch <role> <ticket> --plan` prints it); never name another.
   Never use a script or tool from the Gov OS repository, and never `copier`.
2. **When a command fails, is refused or gives a wrong result, stop that step and write a finding** (section 4). Do not
   retry it in another form, do not patch the product, do not edit a record by hand. Go on to a later step only if it
   does not need the failed one; otherwise stop (section 5, step 11).
3. **Never read** anything outside your repository except your own outputs folder (section 4) and the product's own
   command outputs. Not the other five repositories, not the run folder's other files, not the Gov OS repository, not any
   other folder of the machine.
4. **Write only inside your repository** and your outputs folder (section 4). Stage MA and stage A9 write outside the
   project through `--out` (section 5).
5. **Never edit** `.claude/settings.json`, the hooks under `governance/kernel/hooks/` and `.claude/hooks/`, or anything
   under `.tickets/` (tickets change only through `tk start` and the stages).
6. **The repository's own files stay as built.** A file of the repository changes only by an action the path map gives it
   (A3), reviewed at A5 and carried out by A6 or A8; never move, rename, rewrite or delete one by hand. Never write the
   value of anything that looks like a credential in any file or message: name it by its place and rule id.
7. **No push, no tag, no `sudo`, no install.**
8. Run long jobs (A9, rebuilds) one at a time, in the background, after `gov resources --check` exits 0.
9. **No question set:** do not write, ask or measure one. The proving ground's questions are asked after you stop, by the
   run's reader.
10. Commit messages: write the message to a file with the Write tool and `git commit -F <file>`; every commit's final
    paragraph carries `Role: orchestrator` and `Task: <the coordination ticket or the stage's ticket>`, all trailers in
    that one paragraph with no blank line inside it. (The commits the product makes for a stage carry a subject only, by
    design: do not amend or rewrite them.)

## 3. Your start

1. Confirm and keep for your first report:
   ```
   pwd ; git status --porcelain ; git log -4 --oneline ; printenv GOV_ROLE GOV_TICKET GOV_MSG_ADDRESS ; readlink -f ~/.local/bin/gov ; tk ls
   ```
   `GOV_TICKET` must equal `governance/project/roster.yaml`'s `coordination_ticket`. The tree must be clean.
2. `tk start <the adoption ticket>` (its title starts "W2-81: adopt"), and commit it. Leave it in progress when you
   stop.
3. (changed) `gov adopt --facts`; then fill `governance/project/facts.yaml` and commit it, before anything asks for a
   brief. Three values the 0.1.4 run left open and every brief needs:
   - `commands.where`: `run: 'pwd && git branch --show-current'`, `check: 'pwd'`;
   - `paths.tests_tree`: the real folder `gov launch independent-test-designer <ticket> --tests-worktree` will make, which
     is `../<your repository's folder name>-tests` (the default `'../{W2}-tests'` leaves `{W2}` open and the test
     designer's brief names a folder that does not exist);
   - `commands.accept`: `run: 'gov accept {ID} --root ../<your repository's folder name>-tests'`, `check: 'gov accept
     --help'` (the default's `{WRITE_TREE}` otherwise carries the same open `{W2}`);
   - and each other `{UNSET_...}` value that `gov brief independent-auditor` names, from your repository's own files.
   Then `gov brief independent-auditor <the A5 review ticket>` once, to see that no `where` or tests-tree slot is left
   open; a slot still open is a finding (`gov brief` builds its briefs by construction).

## 4. Your files

Your outputs folder is `/home/usain/gov-os-runs/W2-81/run-<RELEASE>/outputs/<your repository's folder name>/` (create it).
1. **Findings:** `<outputs>/FINDINGS.md`. Append only. One block each: `F-NNN | <UTC time> | <stage> | <what failed> |
   <the exact command> | <exit code> | <expected> / <observed> | <evidence path> | <your guess: product or repository>`.
2. **Stage reports:** `<outputs>/reports/NN-<stage>.md`, one per stage. Longer evidence (full outputs, diffs, timings) in
   `<outputs>/evidence/`.
3. A session's own logs (the workers you launch) go in `<outputs>/logs/`.

## 5. The order (changed)

Follow the adopt skill (`.claude/skills/adopt/`) for each stage's form; this list fixes the order and the forms earlier
runs showed are needed. **The order is A1, the path map, A2, AS, MA, A3.** Run each stage once, with the form below; a
stage's second run leaves a second commit and is a finding, not a retry.

1. **A1**, committed (the product commits it).
2. **The path map**, before A2 (the 0.1.4 run wrote it after A2 in three repositories: A2 then classed 125 to 128 paths
   `namespace: null`, six controls were flagged and two large files missed on that alone).
   `governance/project/path-map.yaml` puts **every tracked path in exactly one namespace** and is committed before A2
   runs.
   - Check it yourself with a read-only `python3 -c` over `git ls-files` and the path map's globs: each tracked path
     matches **one** namespace's `paths`, not none and not two (the product's classifier takes the first match and says
     nothing of a second, so an overlap passes silently and fails later).
   - The adoption's own records are the usual overlap: `governance/adoption/**` and
     `governance/project/audits/adoption-*/**` belong to one namespace (the `adoption` namespace, not embedded), so the
     namespace that holds `governance/project/**` must not also match `governance/project/audits/**` (name its
     sub-folders, or its files, instead of the whole tree).
   - Each namespace states `embedding_policy` as exactly `embedded` or `not embedded`, and at least one is `embedded`.
   Record the check and its result (paths counted, none unmatched, none matched twice) in the report.
3. **A2** (`gov adopt --lite --stage A2 --session <your session id> --role orchestrator --json`). Its record then classes
   every path; if any path has `namespace: null`, that is a finding about the path map (go back and fix the map before AS,
   committing it) and not something to leave for A3.
4. **The memory rule, before A3:** your repository's own code, tests, documents and records are development memory,
   `memory_class: governance`; `product` is only for product data that must stay out of memory: binaries, media, and data
   files that are generated or bulk (a text file is `product` only if you can say what generated it or why it is bulk
   data; a hand-written table, a checklist or a note is a document, `governance`). Count your tracked text files outside
   every governance namespace (`git ls-files` and a read-only `python3 -c` over the path map) and justify each in the A3
   record.
   [[PLACEHOLDER D3 (waits for the owner's decision on the stale-document route, and for it to be built): the sentence
   for superseded, historical and legacy namespaces: whether the adopter gives them `lexical_policy: not indexed` and
   `embedding_policy: not embedded` as the explicit treatment under test, or leaves them as the 0.1.4 run did (namespaces
   of their own, `not embedded`, still found by the keyword route). Not written by the lead; the CTO fills it in.]]
5. **AS**, the spec audit, between A2 and A3 (A3 refuses `ADOPT_STAGE_MISSING "run AS first"` without it):
   `gov adopt --lite --stage AS --session <your session id> --role orchestrator --json`. Report what it found (specs,
   modules, gaps). A result of 0 specs and 0 modules for a repository that visibly tracks specs is a finding.
6. **MA**, the assessment, right before A3: `gov adopt --lite --stage MA --out <outputs>/ma-a3`. Report its proposals
   (proposals only; nothing is moved). A3 is run after it with `--assessment <outputs>/ma-a3` (nothing may be committed
   between MA and A3: a commit moves HEAD and A3 refuses an assessment of another commit).
7. **A3, the path map as the release takes it**, run **once**, `--session <your session id>`. Its `--map` proposal (in
   your outputs folder, never committed by hand) is a top-level `artefacts` list, one entry per artefact you act on, in the
   form the release takes:
   - **KEEP** takes no `target` and no `batch` (the product refuses a KEEP with either, whole);
   - **RETIRE** takes no `target`, and a `kind` that is one of `rule-file`, `memory-store`, `chat-database` (the three
     kinds A8 retires; a legacy document of any other kind has no RETIRE route: KEEP it and say so in the report);
   - **MOVE, RENAME** take a `target` and a positive integer `batch`; SPLIT takes a non-empty `targets`; a file in a
     native package layout needs `justification.materially_better` and `justification.migration_risk`;
   - a path the proposal does not name is KEPT; an empty `artefacts: []` is accepted and committed as all-KEEP, so do not
     run A3 with one to "probe the form".
   Then **A4**, the batched plan.
8. **A5**, the independent review of the path map: `tk start <the A5 review ticket>` and commit; `gov brief
   independent-auditor <id>`, filling any `{...}` slot left and an empty "Objective:" from the ticket's KPI lines by hand
   (record that as a finding); launch it; wait for it; then
   `gov adopt --lite --stage A5 --verdict governance/project/audits/adoption-A5/verdict.md --json`. The auditor's session is
   not yours: its `auditor_session` must differ from A3's `--session`.
   **The verdict's front matter (changed):** the keys the adopt skill gives (`stage`, `verdict`, `path_map_hash` for A5,
   `auditor_session`, `checked` as `record: <path>` and `sha256: <its sha256 at HEAD>` entries for A7 and A10). The
   verdict is also read by the store: if it states an `id` it must also state `type` and `status` (non-empty strings, for
   example `type: evidence`, `status: RECORDED`); a verdict with an `id` and no `status` is accepted by an older release's
   gate and then listed as an invalid record by `gov rebuild`. The release `<RELEASE>` refuses it at the gate; say in the
   auditor's brief to follow this form, and run `gov rebuild` once after A5 to see that no record is listed invalid.
9. **A6**, the controlled migration of the reviewed plan; then **A7** (lite), a fresh auditor's verdict on the A7 review
   ticket, given the same way, its front matter naming `stage: A7`, and its `checked` list one entry per record read, each
   as `record: <path>` and `sha256: <its sha256 at HEAD>` (`--verdict governance/project/audits/adoption-A7/verdict.md`);
   **A8**, the legacy import and retirement; then **A9 lite** (the index and the embeddings) in the background with
   `--out <outputs>/a9` and no `--questions`; then **A10** (lite), a fresh auditor's verdict on the A10 review ticket, the
   same way (`stage: A10`, the same `checked` form). After A9, check your store: among your own tracked text files, list
   any with `indexed = 0` in `lexical_file` (read-only `sqlite3`), and report each you did not intend. A9's refusal
   `FABRIC_INCOMPLETE` names the files; copy them into the finding.
   **The LITE ticket cycle**, in the same step list's place: the adoption ticket (profile LITE) lands by `gov queue`,
   which is run after you stop, not by you: it merges the ticket's work branch, runs the ticket's acceptance folder and the
   selected tests, and closes the ticket at the land (`governance/project/queue.yaml` names the integration branch and the
   work-branch form, the ticket's id). Your part:
   - an independent test designer writes the ticket's acceptance cases from its KPI lines under its
     `acceptance_tests.path`: make its tests worktree (`gov launch independent-test-designer <the adoption ticket>
     --tests-worktree`), `cd` there, and launch it from there (`gov launch` starts a worker in the folder it is run from),
     with `gov brief independent-test-designer <the adoption ticket>` (it needs the `where` and `tests_tree` of section 3);
   - the work branch `gov queue` reads is the form in `queue.yaml`: when the test designer's branch has another name,
     point a branch of that name at its commits (`git branch <name> <its branch>`) and say so in the report;
   - `gov accept <the adoption ticket>` (with `--root` the tests worktree when the tests are only there) and record its
     answer; do not run `gov queue`, `gov close` or `gov queue --dry-run`.
   Record each step; a refusal is a finding.
10. **The lite verdict**, if the product gives a stage or command for it (the adopt skill says); otherwise report that none
    exists. [[PLACEHOLDER D1 (the verdict stage): if the owner has it built before the re-run, the CTO writes its command
    and form here; until then this step stays as written, and the stage is a named exception or a reason of the run, not
    the adopter's finding.]]
11. **A final `gov rebuild`**, so the store's commit equals HEAD after your last commit (check with `gov retrieve` on a
    neutral word: it must not stop with `FACET_UNAVAILABLE`). Your last commit is before it; the tree is then clean.
    `gov rebuild --json` lists no invalid record; one listed is a finding.
12. **Stop.** Write `<outputs>/reports/99-handoff.md`: each stage's exit code and commit, the findings, the store's commit
    and HEAD, the work branch's name and tip, and `git status --porcelain` (it must be empty). Write "ADOPTION STOPPED" as
    its last line. Do nothing more. If a finding stops you before step 11, do steps 11 and 12 as far as they can be done.

## 6. How you report each stage

1. Write `reports/NN-<stage>.md` as soon as the stage ends: the commands with exit codes, start times and durations; the
   record paths and commit ids; what passed and what did not; the findings raised.
2. Plain facts only: no advice to Gov OS, and no fixes of the product.

## 7. What the operator does (not yours; kept here so the run is one document)

These are the steps of whoever starts and ends the run, written down because the 0.1.4 run's operator steps each failed
for a reason of the environment, not of the product. The adopters do none of them.

1. **Start (changed).** The driver (`tools/drive-rerun.sh` beside this brief) starts each adopter with a scrubbed
   environment plus exactly: `PATH` with `~/.nvm/versions/node/v22.23.3/bin` after `~/.local/bin` (so `ccusage` 20.0.26,
   registered in `governance/project/tool-registry.yaml`, resolves for `gov telemetry` and the read step), the operator's
   real `HOME` (so the adopter's and the landing's pytest resolve), `GOV_ROLE`, `GOV_TICKET`, and **`GOV_MSG_ADDRESS` set
   to the address of whoever starts the run** (the driver refuses to start without it). Every session an adopter then
   launches inherits it, so no end message goes to an inbox that is not the starter's. On 2026-11-20 the run's end
   messages went to the live CTO's inbox, 29 of them, because the environment was scrubbed and the launcher's default is
   `cto`.
2. **After the adopters stop:** `gov queue <the adoption ticket>` per repository, `gov doctor` and `gov telemetry` with the
   operator's real `HOME` and the `PATH` of item 1 (the runner's `--pinned-gov` landing now runs with the operator's
   `HOME`, W2-81 fix T1; do not run it by hand with a scrubbed one: pytest then lives outside the scrubbed `HOME` and the
   landing is a crash with 0 tests, not a result).
3. **The landing and the adoption ticket's F1 line.** [[PLACEHOLDER D7 (F1 on the adoption ticket; the analysis's R2b): the
   set-up's F1 line (`tools/setup_0.1.4.py:125`, "every commit touching governance/adoption/ carries Role: orchestrator")
   fails the landing in all six repositories because the product's own stage commits are subject-only. The CTO writes the
   line the re-run's set-up uses (the owner's option (a): a stage record changes only by `gov adopt`'s own commit, subject
   `gov adopt --lite <stage>`, or (b)). Not written by the lead.]]
4. **The measure:** the runner's `--exceptions <file>` takes the owner's one-by-one list of named reason ids with the
   decision id (D9); the lead does not write it.
