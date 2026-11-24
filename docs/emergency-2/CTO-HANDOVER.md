# CTO handover (session 015dc3de → the fresh CTO after the WSL restart, 2026-11-24 about 16:30)

Read first, in this order: `docs/emergency-2/GOLDEN-WORKFLOW.md` (the spine, DEC-1244 WF), `docs/emergency-2/EMERGENCY-2.md`
(with §13, the dated changes since v3), this page, then DEC-1231 to DEC-1246 in `docs/DECISION_REGISTER.md`. The owner is
awake and answers in the chat; he restarts WSL after this handover (`autoMemoryReclaim=dropCache`, DEC-1233 (8)).

## 0. Standing orders
- **The owner's priority order (DEC-1232 (1)), as changed by DEC-1245 (practice first):** every repository works by the
  golden workflow as written practice; products use only the tools proven in real use (a tool status list per release:
  green / amber / not yet); no product waits for Gov OS. Gov OS: the integration plan, Wave 2's close, lifting its
  emergency, then Wave 3 on its own tools.
- **Emergency mode for Gov OS itself (DEC-1239):** its own fixes land by the plain path: a hand merge, the change's own
  tests and **the impact-selected suites** (`gov queue <ticket>=<branch> --onto w2/integrate --select` lists them;
  DEC-1244 X-1), recorded. The full suite only for a release (on demand) and weekly. A red the selection missed is a
  selection bug (findings log).
- **Roles in tests:** only the independent test designer changes anything under `tests/acceptance/` (DEC-1243 (2));
  check trailers before every merge (`git log --no-merges --format='%h [%(trailers:key=Role,valueonly,separator=)]'
  w2/integrate..<branch> -- tests/acceptance`); a blank line before `Co-Authored-By` hides `Role:`.
- **Models and effort (DEC-1225, DEC-1236, DEC-1242 R-4):** Opus only for each product's CTO and a senior engineer;
  every lead Sonnet at medium (`tools/start_lead.sh`), research Sonnet high (`EFFORT=high`), test designers and engineers
  Sonnet high; an owner-asked wide audit Opus (`tools/start_audit.sh`); no Fable; **no change to any role's model or
  effort without the owner**.
- **Decisions:** spec questions come to the owner as decision records batched on a decisions page in his template (the
  latest form: `docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html`); a stopper pushes at once. Record his
  answers card by card in the register; commit his page as their record.
- **Pushes and watching:** push the owner for anything ready for his review and at each phase end with the three
  measures (DEC-1244 GO). Run `tools/cto_watch.sh <seen file>` as a tracked background command and **restart it after
  every event, heartbeat included** (the lapse of 22–24 November idled 0.1.5 for 30 hours, I-13). The cron
  `tools/stall_check.sh` (every 15 min, DEC-1243 (4)) types into the CTO's tmux session after 3 hours with nothing moving
  (it reads the session name from `log/cto-tmux.txt`).
- **Test runs:** through `tools/heavy_slot.sh` with `-n auto`; `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH`;
  `PYTHONPATH=<tree>/src:<tree>/src/gov/close/pytest_plugin`; `GOV_TESTS_OPTIN=weekly` for weekly folders; the full
  suite by `tools/full_suite.sh <tag>` (store rebuild + nightly, detached; the watcher sees its end).
- **tmux:** always an exact target, `-t "=name:0.0"` for send-keys.

## 1. State at the handover
- **Release 0.1.5 is cut and pinned** (the owner, 2026-11-24): tag `v0.1.5` on the record commit `8b892a2d4`, C =
  `ba09214f2`, pin `pin-ba09214f2024` live (`pin-961db6546490` kept), both stores rebuilt, registry entry `8346b9a30`;
  green base `NR-20261124T135851Z-0bd2945b04fe.json` (19,074 passed, 0 failed, weekly tier). It carries DEC-1225's model
  rule in code, W2-209 slice (a), the strict memory grading with the stamped figure, no claude.ai connectors, pause stops
  every starter, no hit@5 floor, the doctor/update/queue fixes, D5, D6, D7, W2-81's fixes, Contract 5.1, and every red fix
  of the week (findings I-1 to I-16, `docs/emergency-2/integration/FINDINGS.md`).
- **The authority file is ON** (`a48c6e3ed`): the CTO cuts every release whose content the owner approved, by code, once
  the release acceptance passes, with the re-pin's self-rollback and a push each time (DEC-1223, DEC-1226, DEC-1235).
- **The shared reranker** was stopped after the re-pin (it differed from the new pin's); it starts from the new pin on the
  next search.
- **Nothing is running** but: the dispatcher's minute cron, the hourly backup cron, `@reboot embedders_at_boot.sh`, the
  stall check cron. After the restart, start again: `usage_log.sh` (`cd tools && EVERY=3600 SPEND_CHECK=0 setsid nohup
  bash usage_log.sh &`) and, if the capacity data is still wanted, `capacity_sampler.py` (`EVERY=60 setsid nohup python3
  tools/capacity_sampler.py --hours 36 &`; its samples so far are in `log/capacity-samples.jsonl`).
- **Held branches:** `e2/d1-verdict` (W2-210, the lite verdict stage, green; lands in 0.1.6); `e2/w2-207-runtime` and
  `e2/w2-207-pre-retire` (W2-207, green; the cut-over runbook is on the branch at `docs/emergency-2/W2-207-CUTOVER-RUNBOOK.md`).

## 2. The plans
- **The golden workflow v2** is the spine (`docs/emergency-2/GOLDEN-WORKFLOW.md`, DEC-1244 WF); CLAUDE.md and AGENTS.md
  point to it beside the golden rule.
- **The integration plan** (`docs/emergency-2/integration/INTEGRATION-PLAN.md`, approved DEC-1244 with X-1 to X-5 and
  Q-1 to Q-14; 75 items in seven phases; the exit: the scratch repository through the whole workflow and EXAMIN's planning
  on the integrated workflow, DEC-1239 (4); a push at each phase end with the three measures).
- **The next release, 0.1.6** (the CTO's cut of approved content; target about 2026-11-28; DEC-1245 (2), DEC-1246 (3)):
  Phase 0 (memory first in every repository: the refresh retried and checked, the embedder at boot in the product, the
  weekly measure scheduled, the git hook installed by the product, the "all rights reserved" file 0-4) + W2-207 as **one
  machine-wide gate** over every repository's sessions, leads, test slots and GPU work (MA-1 to MA-5; work waits for a
  slot) + models and effort by role, criticality setting review depth, and the escalation rubric's first slice (levels
  computed from the record, a decision below its level refused) through the kit + usage and context per repository, per
  role, per session, daily, beside the plan's reading + D1 (the verdict stage). In the plan these items run beside Phase 1
  in three streams after Phase 0; Phase 1's first items (making the impact selection trustworthy) stay first.

## 3. NEXT ACTIONS, in order
1. Write your session id and tmux name (the start prompt says where); start the watcher; start `usage_log.sh`. Re-run the post-landing check the restart cut off (it follows the owner's registry commit): `bash .gov-runtime/scratch/orchestrator/tools/landing_select.sh 8b892a2d4 8346b9a30`.
2. **Start the EXAMIN CTO fresh from its handover** (its copy: `/home/usain/gov-os-runs/W2-27/examin`, its latest
   `FRESH-START-*.md`): a tmux session `examin-cto-<MMDD-HHMM>`, `cd` there, `env -u CLAUDECODE claude --remote-control
   'EXAMIN CTO' --model claude-opus-5-5 --effort high --permission-mode bypassPermissions "<a prompt to read its
   FRESH-START file and carry on>"`. Its order: `gov update` to 0.1.5, its fresh 80; then its Contract, the golden
   workflow as its practice, its planning, each for the owner's yes; then execution on the green tools (DEC-1245 (3)).
3. **Start the ASMO OS CTO fresh from its brief** (`docs/emergency-2/briefs/ASMO-CTO-START.md`): a tmux session
   `asmo-cto-<MMDD-HHMM>` in `/home/usain/ASMO-OS-V1`, the same command line with `'ASMO OS CTO'` and the brief as the
   prompt (DEC-1246 (1), (2)). Tell the owner both are running; report their usage after a few days.
4. **The practice-first decisions page:** read `docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html`
   whole (31 cards; proposals in `docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md`), check it against the
   proposals, publish it privately with the Artifact tool (icon `checklist`), push the owner the link (DEC-1245 (4)).
5. **Phase 0 and the 0.1.6 streams:** brief leads (Sonnet, medium) from `docs/emergency-2/briefs/LEAD-COMMON.md` for:
   Phase 0 (items 0-1 to 0-4); the W2-207 cut-over by its runbook and its extension to one machine-wide gate; the
   models/effort/criticality/escalation slice; usage per repository; land each by the plain path with its impact-selected
   suites; then the release full suite, the version commit, `gov release 0.1.6 --patch`-or-full as the content requires
   (a release with new features is cut by the CTO only because the owner approved that content, DEC-1235), a push.
6. Then the integration plan's Phase 1 (its first items: the trustworthy selection), and the rest in order.

## 4. Waiting on the owner
- Answers on the practice-first decisions page (after it is published).
- Nothing else blocks work.

## 5. Lessons of this session (do not repeat)
- A broad branch tested only on its own folders hid 95 reds (I-14): run the impact-selected suites; the release and
  weekly full runs catch the rest.
- Briefs must never ask an engineer to touch acceptance tests (I-12); a helper may write a false role trailer (I-15):
  read the authorship check before merging.
- `gov adapters generate` appended a duplicate governance block to CLAUDE.md and AGENTS.md and re-added legacy denies
  (I-16): edit the heads by hand until that is fixed; check `.claude/settings.json` after any generation.
- A `claude -p` lead that ends on a question is never answered (I-10): every brief says "decide, never ask".
