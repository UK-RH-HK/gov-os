# CTO handover (session 5349501f → the fresh CTO on Opus, 2026-11-22 about 13:35, after the machine restart)

Read `docs/emergency-2/EMERGENCY-2.md` first, then this page, then **DEC-1219 to DEC-1230** in `docs/DECISION_REGISTER.md`
(the register in force holds the kept decisions and everything from DEC-1211 on; an older id is in
`docs/archive/DECISION_REGISTER-2026-11-19.md`). Then write your session id to
`.gov-runtime/scratch/orchestrator/log/cto-session.txt`, read your inbox (`PYTHONPATH=src python3 -m gov.cli.main msg read cto`)
and carry on from §3. **The owner is awake and answering in the chat.**

## 0. Standing orders (the owner)
- **Models (DEC-1225), in force:** Opus only for each app's CTO and a senior engineer; every other agent Sonnet, C3
  included (leads, engineers, test designers, helpers, writers, the measure's reader and grader, reviewers, auditors,
  proving runs); no Fable; one exception, a comprehensive audit the owner asks for runs Opus. The helper rule is live
  (`governance/project/model-exceptions.yaml`, `e49c093fd`): an Opus engineer is refused, Fable is refused, an Opus
  `independent-auditor` is let through for the owner's audits. The rest (launcher, role files, memaudit, EXAMIN) is the
  lead `models-rubric`'s (§1). **Tell the owner the moment it is live** (the lead's landing). It is a trial: every
  Sonnet role measured as the C3 trial does, against `docs/emergency-2/C3-TRIAL.md`'s baseline.
- **Pace:** full pace, the release path first. **Pushes:** at 95 % and 99 % of the plan (it reset 2026-11-22 09:00);
  a decision that stops work pushes at any hour; every report ends with the status block
  (`python3 .gov-runtime/scratch/orchestrator/tools/status_block.py --mark`; keep `waiting_on_owner` in
  `log/report-state.json` true). Wake less and batch: report for a landing, a red, a decision or a push.
- **Context and usage (DEC-1229):** measure, per long session (you, the EXAMIN CTO), context size and growth, what fills
  it, each wake's cost; find the cheapest wake pattern (how often, timed to the prompt cache's life, which events wake);
  how much investigation goes to short Sonnet helpers. Report the figures daily from today beside the plan's reading,
  and bring the owner a proposal. This session reached about a million cached tokens a wake: keep your own small, send
  wide reading to Sonnet helpers, read lead returns by section.
- **The machine:** load inside the gate (20); test runs through `.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`
  with `-n auto`; the full suite with the weekly tier peaked at 22 on 2026-11-20 (W2-88's real redis-copy secret scans
  beside the leads' runs): give the next one a narrower CPU set or run it when the leads are idle.
- **tmux:** target a session exactly (`-t "=name"`); never a prefix.

## 1. Running at the handover (all started 2026-11-22 13:2x)
| What | Returns to | Note |
|---|---|---|
| Lead `models-rubric` (Sonnet), brief `docs/emergency-2/briefs/LEAD-models-rubric.md` | `log/leads/models-rubric.json`, a wake | DEC-1225 in the launcher, role files and copies, the hook's audit limiter, memaudit's reader and grader, the list for EXAMIN |
| Audits 1, 2, 3 (Opus, read-only), briefs `docs/emergency-2/briefs/AUDIT-*.md` | `log/leads/audit-*.json`, wakes; tables in `docs/emergency-2/audits/E2-AUDIT-{1,2,3}-*.md` | DEC-1230; each a table with its gaps and fixes |
| The EXAMIN CTO (Opus), tmux `examin-cto-1122-1329`, Remote Control | the owner's app; `REQUESTS.md` in its copy | from `FRESH-START-2026-11-22.md`: holds its fresh 80 until 0.1.5 |
| `usage_log.sh` (restarted 13:29) | `log/usage.txt` | restart if dead: `EVERY=3600 SPEND_CHECK=0 setsid nohup bash usage_log.sh` in the tools folder |
| The dispatcher's cron line (every minute) | — | intact after the restart |

**Tools** (`.gov-runtime/scratch/orchestrator/tools/`, recreated today; the scratchpad was cleared): `start_lead.sh <name>
<brief>` (Sonnet lead), `start_audit.sh <name> <brief>` (Opus, owner-asked audits only), `full_suite.sh <tag>` (store
rebuild then the full suite with the weekly tier, detached), `cto_watch.sh <seen file>` (run as a tracked background
command; a seen file of your own; `NSAMP=10`).

## 2. The base and the branches (nothing was lost in the restart: every lead had returned)
- `w2/integrate` head: see `git log -1` (13:3x, the audit briefs). Release 0.1.4 is live (tag `v0.1.4`, pin
  `pin-961db6546490`). The full suite on `49e7fa070` (the scan fix and the W2-17 fixes) was **green**: 18,245 passed,
  0 failed (`docs/close/nightly/NR-20261120T154700Z-49e7fa070d78.json`, untracked: commit it with the next chore).
- **Done on branches, not merged** (each green on its branch; check test authorship before any merge:
  `git log --no-merges --format='%h [%(trailers:key=Role,valueonly,separator=)]' w2/integrate..<branch> -- tests/acceptance`,
  and read its output before merging; a `[]` means a blank line hid the trailers):
  - `e2/release-patch`: **W2-209 slice (a)** (ticket `DAEO-a2h5`, in progress): patch rule, gates, `gov release --patch`,
    general re-pin, rollback, burned, pushes, the nightly's weekly option; `gov accept W2-209` 128/128; rehearsal 26/26
    (`docs/plan/wave-2/w2-209-rehearsal/`); authority file committed **off**. Real G3 still needs one run on W2-81's kept
    outputs (`~/gov-os-runs/W2-81/run-0.1.4/`; check `report.json`'s `repositories.<name>.queue.ticket` key, else the
    one-line fix in `src/gov/release/proving.py` `_queue_ticket`). C3 trial ticket 1.
  - `e2/l2-4-queue`: **L2-4**, the fix under W2-115b (the selection no longer refuses documents only the green range
    holds: `unplaced_base`) and `DAEO-gr7t`'s record fix. **Land it through `gov queue` as the real proving landing**
    (command in its return, `log/leads/l2-4-queue.json`; about 40 min); then retire the scratch landing tools in one
    chore (list: `governance/project/orchestration/packages/L2-4-PROVING.md` on the branch).
  - `e2/w2-81-fixes`: W2-52's verdict record (`VERDICT_NOT_A_RECORD`), W2-88's `FABRIC_INCOMPLETE` names, W2-81's runner
    (`HOME`, AS, owner-exceptions input, ranked bundles, T10 the launches' `GOV_MSG_ADDRESS`), the re-run's adopter brief.
  - `e2/w2-81-proving-run`: the 0.1.4 run's record (NOT_READY): merge it as a record.

## 3. Next, in order
1. **Land `models-rubric`** when it returns, then tell the owner the rule is live in code. EXAMIN's changes the kit does
   not carry: send the EXAMIN CTO the lead's list.
2. **Release 0.1.5 = (a) (DEC-1226), the owner's last manual cut.** Land, in this order, each checked on the merged tree:
   `models-rubric`; `e2/release-patch` (W2-209); `e2/l2-4-queue` **through `gov queue`**; `e2/w2-81-fixes`;
   `e2/w2-81-proving-run`. Then three fixes 0.1.5 should carry for EXAMIN and the re-run, each a lead (Sonnet, failing
   test first): **D5** the strict forbidden-citation rule in `gov memaudit`'s grading (a fix under W2-204), so EXAMIN's
   95 % is graded as the proving run's; **D6** `gov doctor`'s patch-only CLI/extension drift reported with exit 0 (a
   fix under W2-22); **D7** real adopted repositories land: choose the simpler of `gov adopt` writing `Role:`/`Task:`
   trailers on its stage commits or the landing accepting adopt's own commits by a marker, and **tell the owner which**.
   Then the version commit and `docs/emergency-2/release-0.1.5/` (STEPS.md and repin.sh as 0.1.4's), the full suite on
   that head, and **push the owner** with C. After his cut: turn the authority file on (a decision-record commit, his
   standing approval DEC-1223/DEC-1226), tell him, and the EXAMIN CTO updates and runs its fresh 80.
3. **D1** (the lite verdict stage, CAP-44.h) and **D3** (the route keeping stale and legacy documents out of default
   memory, designed with the imports feature) are **new feature tickets**. Ask the owner in one line whether D1 rides
   0.1.5 (then 0.1.5 waits for it) or the next release (a bigger one: his cut). D3 goes with the imports feature (after
   EXAMIN's fresh 80, IM-1 (b)). Then W2-81's re-run on the release that carries them (D8), exceptions named in one
   decision (D9: D2, D3's content-reading A2, D4).
4. **Decision 4 (DEC-1228), starts now:** a Sonnet research lead approves nothing itself: you approve and record REA's
   install under the install rule (`governance/project/tool-registry.yaml`: version pinned, size, why, given only to
   the study's sessions as an MCP tool); the study of Startup Launchpad in its own folder outside the products (for
   example `~/gov-os-runs/study-startup-launchpad/`): REA on its website and browser code; its scanning engines studied
   from their output on a **synthetic test repository with planted issues, never our own code**; reconstructed code is
   study with its origin (the app, its version, the date, REA); nothing of it in a product without an absorb
   assessment stating whether we hold a commercial licence. The records move into the imports register when that
   feature lands.
5. **Decision 5 (DEC-1229):** the measurement and the daily figures (§0).
6. **The audits (DEC-1230)** when they return: read each table by section, bring the owner the gaps with the fixes,
   batched.
7. **Then the rest:** W2-207 (the cut-over, by day; then W2-209 slice (b), the automatic update; by hand until then);
   L2's B1 with TI-1 and TI-3 (the strict close and the secrets tests retire; one real-gitleaks case weekly); G1-2;
   Gov OS's first fresh 80 (its control settled first).
8. **Fixes owed:** `gov accept W2-16` gives `ACCEPT_NO_MAP` (its README maps no KPI line); `context_watch.py` registered
   twice after `gov update` (EXAMIN's report 28); `gov --version` prints `commit unknown`; the weekly tier's CPU set;
   the 30-odd stale worktrees under `~/gov-os-worktrees/` (G3's size audit); EXAMIN's smaller requests in its
   `REQUESTS.md`.

## 4. Waiting on the owner (keep `waiting_on_owner` equal to this)
- The push for 0.1.5 when its base is green (his last manual cut).
- D7's choice, to be told (not asked). D1's placement (one line, §3.3).

## 5. What this session got wrong, so you do not repeat it
- Messages to a running `claude -p` lead are never read: change a lead's scope in its brief or at the landing.
- Trailers count only in a commit message's last paragraph: a blank line before `Co-Authored-By` hides `Role:`; read the
  authorship check's output before merging, not after.
- A file list built by grep included the bare `tests` folder and started a whole-suite run in one slot: build test
  lists by folder and drop `tests` itself.
- It blamed inbox wakes on a test leak; they came from the proving run's own launches. Attribute a message by its
  `data.repository` and sender before acting.
- A YAML edit in a single-quoted KPI line needs a doubled apostrophe; a ticket's `sources` need quoted strings where
  YAML would read a number.
- It read EXAMIN's "X12" from a file name and recorded the wrong decision; ask or read the item itself.
- `gov queue` counts the change from the last green record; documents committed after it are now listed as
  `unplaced_base` (L2-4's fix), not refused.
