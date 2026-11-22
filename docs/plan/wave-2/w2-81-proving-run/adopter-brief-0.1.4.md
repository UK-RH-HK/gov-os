# W2-81 adopter: your fixed first message (release 0.1.4)

The same message starts six sessions on `claude-sonnet-5-5`, one in each repository of W2-81's proving ground. Your
repository is your working directory. Release: Gov OS 0.1.4 (S-RERUN, EMERGENCY-2 8.2 item 2). It is the 0.1.1 brief
brought current: no guard, no probes, no replies file (nobody answers while you run), `gov queue` in place of
`gov close`, the stage forms 0.1.1's run showed are needed.

## 1. Who you are and where

1. You are an adopter: an orchestrator session (`GOV_ROLE=orchestrator`, `GOV_TICKET` = your repository's coordination
   ticket) in one repository under `/home/usain/gov-os-runs/W2-81/run-0.1.4/repos/`. `pwd` names it. That folder is
   "your repository"; the other five are not yours.
2. Your job: adopt your repository with Gov OS release 0.1.4 through A1 to A10 lite and a LITE ticket cycle, in the
   order of section 5, using only the product. Then stop.
3. You test the product the way a customer would. When the product fails, the failure is the result. **Stop that step
   and write a finding. Never work around the product.**
4. Release 0.1.4: its `gov` is `~/.local/bin/gov`; its kit came from the tag `v0.1.4`. Never install `gov` from any other
   source.
5. Already done, so do not redo it: the kit and the adapters (one commit); A0; and one commit holding the coordination
   ticket's launch fields, the A5, A7 and A10 review tickets (each with its report folder
   `governance/project/audits/adoption-<stage>/`) and the adoption ticket (profile LITE, with
   `acceptance_tests.path: tests/acceptance/<the adoption ticket's id>/`). `tk ls` lists them;
   `governance/project/roster.yaml` names the coordination ticket.

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
   **Launching a worker** (an auditor at A5, A7, A10; the test designer of step 7): from your repository's root (the test
   designer's from its tests worktree): `gov launch <role> <ticket> -- -p --output-format json < <the filled brief file>`,
   in the background with its output to a file under your outputs folder, then wait for it as `gov wait --help` says. The
   launcher chooses the model (`gov launch <role> <ticket> --plan` prints it); never name another.
   Never use a script or tool from the Gov OS repository, and never `copier`.
2. **When a command fails, is refused or gives a wrong result, stop that step and write a finding** (section 4). Do not
   retry it in another form, do not patch the product, do not edit a record by hand. Go on to a later step only if it
   does not need the failed one; otherwise stop (section 5, step 10).
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
    paragraph carries `Role: orchestrator` and `Task: <the coordination ticket or the stage's ticket>`.

## 3. Your start

1. Confirm and keep for your first report:
   ```
   pwd ; git status --porcelain ; git log -4 --oneline ; printenv GOV_ROLE GOV_TICKET ; readlink -f ~/.local/bin/gov ; tk ls
   ```
   `GOV_TICKET` must equal `governance/project/roster.yaml`'s `coordination_ticket`. The tree must be clean.
2. `tk start <the adoption ticket>` (its title starts "W2-81: adopt"), and commit it. Leave it in progress when you
   stop.
3. `gov adopt --facts`; fill each `{UNSET_...}` value that `gov brief independent-auditor` needs (identity, the test
   folder) from your repository's own files; commit.

## 4. Your files

Your outputs folder is `/home/usain/gov-os-runs/W2-81/run-0.1.4/outputs/<your repository's folder name>/` (create it).
1. **Findings:** `<outputs>/FINDINGS.md`. Append only. One block each: `F-NNN | <UTC time> | <stage> | <what failed> |
   <the exact command> | <exit code> | <expected> / <observed> | <evidence path> | <your guess: product or repository>`.
2. **Stage reports:** `<outputs>/reports/NN-<stage>.md`, one per stage. Longer evidence (full outputs, diffs, timings) in
   `<outputs>/evidence/`.
3. A session's own logs (the workers you launch) go in `<outputs>/logs/`.

## 5. The order

Follow the adopt skill (`.claude/skills/adopt/`) for each stage's form; this list fixes the order and the forms earlier
runs showed are needed.
1. **A1 and A2**, each committed.
2. **MA**, the assessment, right before A3: `gov adopt --lite --stage MA --out <outputs>/ma-a3`. Report its proposals
   (proposals only; nothing is moved).
3. **A3, the path map.** `governance/project/path-map.yaml` puts every tracked path in exactly one namespace and is
   committed before A3 runs. **The memory rule:** your repository's own code, tests, documents and records are development
   memory, `memory_class: governance`; `product` is only for product data that must stay out of memory (binaries, media,
   generated data). Superseded and legacy documents stay governance, classed by their own namespaces. Before A3, count
   your tracked text files outside every governance namespace (`git ls-files` and a read-only `python3 -c` over the path
   map) and justify each in the A3 record. A3's `--map` proposal (in your outputs folder, never committed by hand) is a
   top-level `artefacts` list, one entry per artefact: `{path, action, target, batch, kind, justification}`, `batch` a
   positive integer, `kind` given for a RETIRE. Run A3 with `--session <your session id>`.
4. **A4**, the batched plan.
5. **A5**, the independent review of the path map: `tk start <the A5 review ticket>` and commit; `gov brief
   independent-auditor <id>`, filling any `{...}` slot left and an empty "Objective:" from the ticket's KPI lines by hand
   (record that as a finding); launch it; wait for it; then
   `gov adopt --lite --stage A5 --verdict governance/project/audits/adoption-A5/verdict.md --json`. The auditor's session is
   not yours: its `auditor_session` must differ from A3's `--session`.
6. **A6**, the controlled migration of the reviewed plan; then **A7** (lite), a fresh auditor's verdict on the A7 review
   ticket, given the same way, its front matter naming `stage: A7`, and its `checked` list one entry per record read, each
   as `record: <path>` and `sha256: <its sha256 at HEAD>` (`--verdict governance/project/audits/adoption-A7/verdict.md`).
7. **A8**, the legacy import and retirement; then **A9 lite** (the index and the embeddings) in the background with
   `--out <outputs>/a9` and no `--questions`; then **A10** (lite), a fresh auditor's verdict on the A10 review ticket, the
   same way (`stage: A10`, the same `checked` form). After A9, check your store: among your own tracked text files, list
   any with `indexed = 0` in `lexical_file` (read-only `sqlite3`), and report each you did not intend.
8. **The LITE ticket cycle.** The adoption ticket (profile LITE) lands by `gov queue`, which is run after you stop, not by
   you: it merges the ticket's work branch, runs the ticket's acceptance folder and the selected tests, and closes the
   ticket at the land (`governance/project/queue.yaml` names the integration branch and the work-branch form, the ticket's
   id). Your part:
   - an independent test designer writes the ticket's acceptance cases from its KPI lines under its
     `acceptance_tests.path`: make its tests worktree (`gov launch independent-test-designer <the adoption ticket>
     --tests-worktree`), `cd` there, and launch it from there (`gov launch` starts a worker in the folder it is run from),
     with `gov brief independent-test-designer <the adoption ticket>`;
   - the work branch `gov queue` reads is the form in `queue.yaml`: when the test designer's branch has another name,
     point a branch of that name at its commits (`git branch <name> <its branch>`) and say so in the report;
   - `gov accept <the adoption ticket>` (with `--root` the tests worktree when the tests are only there) and record its
     answer; do not run `gov queue`, `gov close` or `gov queue --dry-run`.
   Record each step; a refusal is a finding.
9. **The lite verdict**, if the product gives a stage or command for it (the adopt skill says); otherwise report that none
   exists.
10. **A final `gov rebuild`**, so the store's commit equals HEAD after your last commit (check with `gov retrieve` on a
    neutral word: it must not stop with `FACET_UNAVAILABLE`). Your last commit is before it; the tree is then clean.
11. **Stop.** Write `<outputs>/reports/99-handoff.md`: each stage's exit code and commit, the findings, the store's commit
    and HEAD, the work branch's name and tip, and `git status --porcelain` (it must be empty). Write "ADOPTION STOPPED" as
    its last line. Do nothing more. If a finding stops you before step 10, do steps 10 and 11 as far as they can be done.

## 6. How you report each stage

1. Write `reports/NN-<stage>.md` as soon as the stage ends: the commands with exit codes, start times and durations; the
   record paths and commit ids; what passed and what did not; the findings raised.
2. Plain facts only: no advice to Gov OS, and no fixes of the product.
