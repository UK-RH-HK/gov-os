# The decisions the §9 audits need from you (one message, A-9)

Each line: the question, the options, my recommendation in **bold**. Answer with the codes, e.g. "R1 a, R2 c, ...";
"all recommended" is enough. Where I am already building on a recommendation tonight, it says so ("building on");
say otherwise and I change course. Each audit's full table is in `docs/emergency-2/audits/`.

## Release and landing
- **L1** `gov queue` for the release (audit 1): (a) port the Gov OS merge queue whole, ~1,400 lines; **(b) a thin queue on the product's pieces, ~300-500 lines** (building on); (c) no queue, `gov close` lands one ticket at a time.
- **L2** DONE by code (audit 1): (a) build `gov done` from DOD-1 to 6; **(b) DONE is the green landing itself, DOD-4 and DOD-6 go** (building on); (c) leave DONE as text.
- **L3** Release authenticity (audit 7 D-4): **(a) pinned and hash-verified, no signing until friction**; (b) an SSH-signed tag `gov doctor` checks; (c) as (b), named v1.0.0.
- **L4** The proving run's model (audit 9 #5): (a) Opus throughout; **(b) Sonnet for trial runs, Opus once at acceptance**; (c) Sonnet throughout.

## Memory
- **M1** `gov context` as code (audit 2): (a) keep it, no instruction calls it; **(b) retire the command, its check and adopt's facts entry; keep the library only for `gov close` with its ceiling lifted; `--in-force` moves to `gov decisions`** (~1 day); (c) retire the module too.

## The run-time tool
- **T1** The dead-man until the tool's first slice lands (audit 3): (a) leave it stopped; (b) restart the Haiku sentinel; **(c) the stall check runs from the dispatcher's cron pass, to the CTO's inbox only** (building on).
- **T2** Pushes to your phone (audit 3): (a) none, a stall shows in the digest; **(b) only for a CTO stall (60 min by day, 2 h at night)** (building on); (c) also machine incidents.
- **T3** No GPU on an adopter's machine (audit 3): **(a) for the release, memory says unavailable there; CPU-where-no-GPU a Wave 3 row** (building on); (b) allow the CPU there now (changes DEC-1065); (c) a Wave 3 row only.

## Tickets and the rubric
- **K1** The measured rubric (audit 4, table 3; 82 % of last month's tickets would have routed differently): **(a) approve it with its model and effort table**; (b) plus a size gate (a fix over 150 product lines becomes a ticket); (c) keep the provisional rubric for now.
- **K2** Your approval per feature ticket (DEC-974): (a) per ticket; (b) per batch; **(c) none for §6.1's build list; you approve only new features outside it**.

## The repository and the register
- **G1** How retired history leaves the tree (audit 5): (a) stays, kept out of the index; **(b) `git rm` the retired code, tests, ACT bundles and prompts, reachable from the pushed tag `pre-emergency-2`; closed-ticket records stay, unindexed**; (c) an archive branch.
- **G2** `origin/record/w2` (367 commits): **(a) keep it, stop syncing, remove its worktree**; (b) delete it on origin (a push, yours); (c) keep syncing.
- **G3** `~/gov-os-archive` (32 GB) and `~/gov-os-workbench` (11 GB): **(a) leave them (disk 43 % used)**; (b) audit later; (c) delete what you name.
- **G4** The register by group (audit 8: 1,206 decisions, 153 kept, 185 superseded, 34 retired, 834 history, in 33 groups): **(a) approve all 33 groups as listed; I settle the 48 doubtful rows inside them**; (b) read the 9 kept groups first (~30-45 min); (c) group by group with changes.
- **G5** The re-baseline (audit 7 D-1): **(a) I write Charter v6 and Contract v5 from audit 7's tables in one change; you approve by group**; (b) Contract only; (c) after the release.
- **G6** When a fresh audit runs (audit 7 D-2): **(a) at the release acceptance and adoption stages A5, AS, A7, A10; otherwise only for a red, a failed land or a feature not working**; (b) also at each STANDARD/FULL spec closure; (c) only at the release.
- **G7** Installs (audit 7 D-3): **(a) free in repositories, worktrees and venvs; user-level installs free and recorded in the tool registry; sudo yours**; (b) you approve each by message; (c) the CTO approves and records.

## EXAMIN
- **E1** The Wave 0 dispositions (report 21: keep 577, relocate 829, archive 2,030; 13 data places): **(a) group by group, lowest risk first, each one reversible commit, so the refactor starts**; (b) all at once; (c) after the release.
- **E2** "Tests kept green" for EXAMIN: **(a) no new red by test id against the last run, plus green characterization tests, now; and (b) before the merge back: you install Tesseract and Poppler (sudo, one minute)**; (c) the whole suite green before any move.
- **E3** The amended Wave 0 brief (DEC-1210 (5)): **(a) EMERGENCY-2 §7 plus a one-page addendum from me to the EXAMIN CTO; no new sha**; (b) a full amended brief for your yes; (c) after the release.

## Usage
- **U1** The CTO's context (audit 9 #1): **(a) keep the full window for now; revisit once memory-first is in every brief**; (b) compact near 300k; (c) a fresh CTO each morning.
- **U2** The helper default model in `~/.claude/settings.json` (forces Opus on unnamed spawns; your file): **(a) set it to Sonnet; I name Opus where it matters**; (b) remove the line; (c) keep.
- **U3** Your operator session on Sonnet: **(a) yes**; (b) keep Opus.
- **U4** Leads on Sonnet for LITE/STANDARD: (a) keep Opus; **(b) a trial on two tickets judged by an Opus reviewer**; (c) Sonnet for all.

## Added by the morning CTO (2026-11-18)
Already decided in DEC-1212: U1-U4 and L4 (Sonnet for the proving run, acceptance included). L1, L2, T1-T3 are built on
your working assumptions: confirm or change.
- **Q-UPD** `gov update` meeting your own edit to a shipped file: **(b) a three-way merge keeping your file, the release's copy written aside on a conflict** (built).
- **Q-CLOSE** The close's base excuses a red from an untrailered first commit: **(a) accept it, the red still recorded; refusing such a close a Wave 3 row**.
- **Q-CAP44** W2-192's CIT-P Part B (CAP-44.m: the adoption stage AS spec audit, W2, as Contract 4.4) was never approved, so the validator's `cit-p-lines-applied` is red (W2-49, five cases), and while it is red no nightly is green, so Gov OS's own landing cannot move onto `gov queue` (no green base): **(a) approve Part B now ("W2-192 CIT-P (B) approved"); I apply Contract 4.4 as the proposal gives it, and G5 re-baselines on top**; (b) fold it into G5, a known red until then; (c) withdraw Part B.
