---
id: WAVE-2-LIST
type: plan
status: ACCEPTED
state_class: AUTHORITATIVE
depends_on: [CHARTER-v5, CONTRACT-v4, WAVE-1-WBS]
decisions: [DEC-534, DEC-567, DEC-577, DEC-712, DEC-714, DEC-715, DEC-716, DEC-718]
---

# The Wave 2 list (consolidated)

This file is the one Wave 2 list (DEC-718; F-M8 of the W1-43 exit audit). It gathers every item from four sources:

- **`governance/project/bootstrap.md`:** its Wave 2 sections and every ticket's residuals (DEC-577);
- **the decisions** that put an item on the list or defer it to Wave 2;
- **the exit report** `docs/plan/wave-1-exit/EXIT-REPORT.md`: its adoption-readiness block and its residuals, those "not on any list yet" included;
- **the exit audit** `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`: F-M1 to F-M13 and F-m1 to F-m10.

It replaces the scattered Wave 2 sections. New items are added here, not in `bootstrap.md`.

**Columns:**

- **Sev** is the severity. **adoption-blocking** means it passes before any pilot adoption (§1, in order). **high** is a fail-open hole, lost work, or something that blocks ordinary work or adoption. **medium** is a wrong result, or a false red or green, in ordinary use. **low** is a deliberate or unusual shape, or a cosmetic gap. **info** is an observation or an open question.
- **Owner** is the role that does the work. The orchestrator coordinates every item. *owner* is the owner's own act.
- **Closes when** is the observable condition.
- **Sources** name the decision and where the item was recorded: `B:<line>` is a line of `bootstrap.md`, `R:<line>` a line of the register, `X` the exit report, `A` the exit audit.

The severity is the source's own word where it gives one, and otherwise the orchestrator's proposal. The owner's ranking of Wave 2 overrides it.

An item that closes is marked **closed** with its commit. It stays in the file.

## 1. The adoption-readiness block (DEC-718; takes in DEC-712 and DEC-714)

Every line passes, in this order, before any pilot adoption of an owner repository.

### AR-1: decisions as records; a bounded context (F-M5)

- **What:** at the audited head, `gov context DAEO-03pw` returned `ok: true` with 814,821 tokens against a budget of 6,000. Every DEC id resolves to the whole register, so all its decisions carry one sha256 (`cd983b…`). The ticket's own text was among the 20 dropped items.
- **Closes when:**
  - each decision is a record of its own with its own hash;
  - `gov context` holds its budget and never drops the ticket's own text;
  - when the mandatory inputs exceed the ceiling, it refuses instead of reporting success.
  - A context built for the same ticket then names each decision by its own hash, within the ceiling.
- **Owners:** product-spec (the decision record and its schema), engineer (`gov context`, the store).
- **Sources:** A F-M5, CAP-15.d.

### AR-2: the hook's git environment (DEC-712, FIRST item)

- **What:** in a linked worktree, the pre-commit hook wrote two foreign commits onto `w1/W1-42` (DEC-710, DEC-711). The cause: `src/gov/retrieval/retrieve_check.py` runs `git -C <temporary clone> add -A` and `commit` with the `GIT_*` variables the hook inherits.
- **Closes when:**
  - every check, test helper and command that runs git clears the inherited `GIT_*` variables;
  - the sweep of every git call in another folder is kept as a record;
  - a hooked commit in a linked worktree leaves its branch and index as the commit made them;
  - `lefthook install` and `uninstall` leave `.claude/settings.json` as committed, with adapter-portability green.
- **Owner:** engineer.
- **Sources:** DEC-710, DEC-711, DEC-712; B:2806; X.

### AR-3: an audit-report record type; accepted history stops blocking commits; the hooks back on (F-M13, F-M4)

- **What:** two problems meet at the pre-commit hook.
  - core-schema reads every frontmatter Markdown under `docs/` and knows no audit-report type, so a report in DEC-441's form is `SCHEMA_INVALID_TYPE` (G1, hard-block).
  - Product traceability is red on eight DAEO-gjjf commits that DEC-717 accepts.
  - So every commit meets a red hard-block check. The audit report could only be committed with the hooks uninstalled.
- **Closes when:**
  - the schema knows an audit-report record type, and the exit report's form validates under both checks;
  - accepted history (history findings an owner decision names) no longer fails later commits;
  - the hooks are reinstalled, and a commit of a report in DEC-441's form passes the hook;
  - the independent test designer restates or retires W1-40's `test_no_lefthook_hook_is_installed_in_this_repository` (F-M4), so that installed hooks are the expected state.
- **Owners:** product-spec (the record type), engineer (the traceability check), independent test designer (F-M4).
- **Sources:** A F-M13, F-M4; DEC-441, DEC-717; B:2643 (the kernel has no audit-report type).

### AR-4: `SubagentHandback` on the guard's list; the list checked against the CLI (F-M7)

- **What:** the guard's default deny of unknown tools (DEC-685) refuses `SubagentHandback` to every role, so no helper's return can be handed back. Nothing compares the guard's known-tool list with the installed CLI's tools.
- **Closes when:**
  - the tool is on the guard's known list, with its reason, through the CIT-P route with owner approval (CAP-33);
  - `gov doctor` compares the guard's list with the installed CLI's tool list at every CLI version change and names each difference.
- **Owner:** engineer.
- **Sources:** A F-M7; DEC-685; B:2743 (the list rechecked at each CLI version change).

### AR-5: refusals final for the call; briefs stop after two identical refusals (F-M12)

- **What:** a helper of the exit audit made 58 identical refused `SubagentHandback` calls. Those calls read 11,994,916 cached tokens.
- **Closes when:**
  - the guard's refusal text says the refusal is final for that call;
  - every brief template and the orchestration skill carry the rule "stop after two identical refusals and return";
  - optionally, a loop counter on identical refused calls backs the rule.
- **Owners:** engineer (the refusal text, the counter), product-spec (the briefs, the skill).
- **Sources:** A F-M12; DEC-096, CAP-59.a.

### AR-6: guardrails explain themselves and never loop (the owner's note on the SubagentStop refusals; beside AR-4 and AR-5)

- **What:** helpers' returns were refused by the SubagentStop hook. It was right to require the twelve-field return (DEC-442, DEC-444), but the brief had asked for "JSON lines only". The helpers saw no reason and retried.
  - This happened in the W1-43 audit and again in this session's extraction of the list.
  - *The orchestrator's reading of the code, not measured:* `src/gov/hooks/subagentstop.py` does not read `stop_hook_active`, while `stop.py` does.
  - On a block it writes its reason to standard output with exit 2, where Claude Code shows the agent only standard error.
  - An exception inside it also exits 2.
- **Closes when:**
  1. the SubagentStop and Stop hooks name the missing fields and the expected form in their refusal text, so the agent sees why;
  2. they block at most once: when Claude Code reports that the stop hook has already blocked this stop (`stop_hook_active`), the hook lets the agent stop and records a "return without the contract fields" finding instead of blocking again;
  3. the rule states where a machine-readable payload goes: after the twelve fields;
  4. the same standard, "say why, refuse once, then record", applies to the guard's refusals (AR-4, AR-5).
  - A helper briefed for JSON lines only is refused once, with the missing fields named, and then stops with a recorded finding.
- **Until it passes (the owner, 2026-10-16):**
  - every subagent brief lists the twelve fields by name and requires them first, as labelled lines, with any machine-readable payload after them;
  - it tells the helper to stop and say so if its return is refused twice;
  - a helper refused twice is stopped by its caller, and its result is taken from its transcript.
- **Owners:** engineer (the hooks, the guard's refusals, the finding), product-spec (the rule's text, the brief templates, the orchestration skill).
- **Sources:** A F-M7, F-M12; DEC-442, DEC-444, DEC-718.

### AR-7: register acceptances as owner git facts (F-M6)

- **What:** 466 entries read "ACCEPTED (owner …)" but are committed under `Role: orchestrator`. No entry is ever `ACTIVE`, so the approval gate of DEC-360 judged no Wave 1 decision.
- **Closes when:** the owner's acceptances are owner git facts, or the owner's reading of the transcribed form is stated in a decision.
  - "Owner git facts" means owner-committed, or a gate that a `Role: owner` commit passes.
  - DEC-718's own commit is the first such fact for an exit.
- **Owners:** owner, with engineer for the approval gate.
- **Sources:** A F-M6; CAP-01.b, CAP-21.a, DEC-360.

### AR-8: the first Wave 2 ticket closes through a clean `gov close` (F-M3)

- **What:** no Wave 1 ticket of this repository closed through a clean `gov close`. All seven closes after `1c33dd28` used `tk close` under owner decisions.
- **Closes when:**
  - DEC-704's fix is merged: `gov close`'s own trailer gate reads `trailers_base`;
  - the first Wave 2 ticket in this repository then closes with `gov close` at exit 0, with no disposition and no exception, and its close record is kept.
- **Owners:** orchestrator, with engineer for DEC-704's fix.
- **Sources:** A F-M3, F-m6; DEC-522, DEC-704; B:2780; X.

### AR-9: ARGUS's full cycle, the a-dev reds, RETR-X-02 (DEC-714)

- **ARGUS's full cycle** (b-dev adopted to A2 only).
  - **Closes when:** b-dev is adopted far enough that its store holds the ticket's sources. Then one `gov close` of ARGUS's implementation ticket gives exit 0, with no disposition and no exception, followed by its `gov ci` and its merge. Each is kept under the evidence folder.
  - Its governance share is measured and at most 15 %: the counter's measure after the clean close, every part measured, entered for ARGUS in `governance-share.json`.
  - b-dev's canaries run and hit.
- **a-dev's context reproducibility (ORION-gp01).**
  - **Closes when:** on a store freshly rebuilt with embeddings, `gov check` is green on context reproducibility and `gov ci checks G1 G2` no longer names it.
  - The cause is measured: the order of supplementary items that rank next to each other.
- **a-dev's claims and schema.** ade-ke2y lacks role, allowed paths and KPIs, and ORION-im02's close record has type `close`, which the schema does not know.
  - **Closes when:** `gov close` writes complete repair tickets, the schema knows the type the close writes, and `gov check` in a-dev is green on both families.
- **RETR-X-02.**
  - **Closes when:** a kept bundle of RETR-X-02 has at least one parent expansion that names its parent, or the owner rules whether a question about an id that exists nowhere has to show one.
- **Merges** of the programmes are the owner's, after green CI (F-m10).
- **Owners:** orchestrator (the runs), engineer (the product fixes), owner (the RETR-X-02 ruling and the merges).
- **Sources:** DEC-713, DEC-714; X's block; A F-m10.

### AR-10: EXP-003, `gov update`, language-agnostic test commands, accept-edits mode with its first tested lead launch

- **EXP-003:** see §2. *Owner:* research.
- **`gov update` (CAP-45.a):** check and impact, an authenticated source (signed tag), migrations, the overlay kept, adapters regenerated, affected indexes rebuilt, verify, rollback, and a ledger.
  - **Closes when:** `gov update --check` reports the version change and the migrations; `copier update` applies them with the overlay files unchanged, and `gov doctor` is green.
  - *Owner:* engineer.
- **Language-agnostic test commands (DEC-534, DEC-567):** `gov close` and the regression run the test commands the project declares, each with its own parallel option, not only pytest. These are a must-have before adoption in any non-Python repository.
  - **Closes when:** a project that declares `cargo test` or `npm test` closes a ticket with its own command.
  - *Owner:* engineer.
- **Accept-edits mode for orchestrator sessions (DEC-716), now in place,** beside DEC-715's stable launch command `gov launch lead <ticket>`.
  - **Closes when:** from a fresh orchestrator session in accept-edits mode, one lead starts with `gov launch lead` (or the owner's form), with no classifier denial and no permission given by hand. The launch is recorded.
  - *Owners:* engineer (the launch command), orchestrator (the tested launch).
- **Sources:** DEC-534, DEC-567, DEC-715, DEC-716, DEC-718; Contract CAP-45.

## 2. EXP-003: retrieval and indexing on small and big repositories (planned, not run)

*Owner:* research. It is part of AR-10. It runs in Wave 2, after AR-1's fix, which its decision-level granularity measure needs. Its plan, as the owner gave it (DEC-718):

- **Corpora:**
  - the dev tiers (`GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`);
  - `~/EXAMIN APP`, **read-only, on a copy**;
  - `~/workspace`.
- **Indexing:** time, RAM (peak RSS) and incremental update, each measured against the Contract's envelope, the scale probe of DEC-078 (Contract §2, about 80k nodes and 270k edges at about 2.2 GB peak RSS).
- **Retrieval modes, compared:**
  - lexical only;
  - semantic only;
  - fused;
  - fused plus reranker.
- **Accuracy:** a defined metric, measured on the evidence the stacked context must contain. The owner's goal is **99 %**. The metric's definition (what counts as a hit, how needed evidence is labelled) is fixed and recorded before the first run.
- **Stacking:** a question that needs about **24k tokens**, retrieved in **8k batches** and assembled complete, with **no duplicates**.
- **Granularity:** decision-level retrieval after F-M5's fix (AR-1): each decision is its own record and hash.
- **Closes when:** the experiment's record holds every measure above per corpus, with the commands, the versions and the raw answers kept. The owner has the figures for F-m2 (CAP-10's re-baseline) and for the envelope.

## 3. The rest of the list, by severity

791 open items: 53 high, 356 medium, 341 low, 41 info. Items added after the Wave 2 plan's approval: W2-H054 (DEC-732), W2-M357 (DEC-735), W2-M358 (DEC-736), W2-H055, W2-M359 and W2-L342 (DEC-743), W2-L343 (DEC-741), W2-M360 and W2-L344 to W2-L348 (DEC-757), W2-H056, W2-L349, W2-L350 and W2-M361 to W2-M363 (DEC-758), W2-H057 (DEC-759), W2-H058 and W2-L351 (DEC-761), W2-M364 and W2-L352 (DEC-762), and W2-M365, W2-M366 and W2-L353 (DEC-763), W2-L354 (DEC-765), W2-M367 (DEC-768), and W2-H059 and W2-H060 (DEC-772), and W2-H061 (DEC-781), and W2-H062, W2-M368 and W2-M369 (DEC-779, DEC-785, W2-50's last review) and W2-M370 (W2-54's run 2, DEC-782), and W2-M371 (DEC-790), W2-M372 and W2-M373 (DEC-792), and W2-M374 (DEC-798), and W2-M375 to W2-M377 (DEC-807, DEC-808), and W2-M378 and W2-M379 (DEC-810), and W2-M380 to W2-M383 and W2-L355 (DEC-812), and W2-L356 to W2-L361 (W2-54's review), and W2-M384 (DEC-823), and W2-L362 (DEC-856), and W2-L363 (DEC-863), and W2-M386 to W2-M390 and W2-L364 to W2-L371 (DEC-864), and W2-L372 (W2-63), and W2-L373 (DEC-867), and W2-M391 (DEC-870), and W2-M392 (P-W2-55), and W2-L374 (DEC-873), and W2-M393, W2-M394 and W2-L375 to W2-L381 (DEC-877), and W2-M395, W2-M396 and W2-L382 to W2-L385 (W2-54 run 5), and W2-M397 and W2-L386 to W2-L389 (DEC-879), and W2-L390 to W2-L396 (W2-02 run 5), and W2-M398 and W2-L397 to W2-L400 (DEC-880, W2-58 run 2), and W2-M399 and W2-L401 to W2-L408 (DEC-882), and W2-L409 (DEC-885), and W2-L410 (DEC-888), and W2-M400 to W2-M402 and W2-L411 to W2-L413 (DEC-889), and W2-L414 (DEC-892), and W2-M403 (DEC-894), and W2-M404 (DEC-897), and W2-M405 and W2-L415 (DEC-902), and W2-L416 (DEC-908), and W2-L417 and W2-L418 (W2-70's return), and W2-L419 (DEC-909), and W2-L420 and W2-L421 (W2-07's and W2-67's returns), and W2-L422 to W2-L425 (W2-69's return), and W2-L426 (W2-70's round 2), and W2-L427 to W2-L429 (W2-65's run 1), and W2-M406 and W2-L430 to W2-L437 (W2-66's run 3), and W2-L438 and W2-L439 (W2-65's run 2), and W2-L440 and W2-L441 (W2-65's run 3), and W2-L442 to W2-L446 (W2-67's run 3), and W2-L447 and W2-L448 (W2-67's run 4), W2-L449 (DEC-932), W2-M407 (DEC-933), so 960 were opened; W2-02's close (2026-10-21) closed 7 of them (W2-M260, W2-M304, W2-M310, W2-M316, W2-M317, W2-L243, W2-L260, now in section 4), and W2-62's close (2026-10-22) closed 2 (W2-M372, W2-M373, now in section 4), and W2-50's close (2026-10-22) closed 1 (W2-M355, now in section 4), and the queue of 2026-10-27 closed 6 (W2-H044 and W2-M153 by W2-66, W2-L437 by W2-72, W2-M404, W2-M395 and W2-L373 by W2-69, now in section 4), so 944 are open, 61 of them high, 395 medium and 445 low. Within a severity they are grouped by owner, then in the order of their sources. 49 more items closed or were superseded in the record; they are in §4.

- **How the list was made:** helpers read every line of `bootstrap.md` and the register, and gave one row per item. The orchestrator added the exit report's residuals and the audit's findings, and merged rows with the same title (2 merged).
- **What remains to check:** a row is carried as the source recorded it. Rows that name one problem from two places may remain; the source references join them. Before a ticket picks a row up, its state is re-checked against the code at that time, because a later commit may have fixed it unrecorded.
- **Where to read more:** the full text of each item is at its source line. Item ids are stable once committed; new items take the next free id of their severity.

### 3.1 high (61)

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-H001 | No ticket lead runs under the ticket-lead role; leads keep orchestrator rights | owner | The owner changes the lead start line, and leads run as ticket-lead. | B:1390 (DEC-156, DEC-437) |
| W2-H002 | CI job red 'unmeasured' until the owner approves pytest, openspec, rulesync | owner | The owner approves the tools, and the CI job is green on a push. | B:1916 (DEC-497) |
| W2-H003 | Opaque Bash write outside repository unseen by guard and containment check | engineer | An opaque Bash write outside the repository from the orchestrator session is refused or reported | B:61 (DEC-123, DEC-152, DEC-156, DEC-161) |
| W2-H004 | Opaque Bash read of the qualification oracle without naming its path | engineer | Oracle unreachable from any agent session by any read form | B:141 (DEC-162, DEC-215, DEC-218, DEC-213) |
| W2-H005 | Opaque Bash writes into .gov-runtime/ unseen in orchestrator session | engineer | Opaque writes to protected .gov-runtime/ paths are refused or detected in the orchestrator session | B:252 (DEC-176, DEC-180, DEC-181) |
| W2-H006 | _get_allowed_paths gives wide orchestrator scope when role argument omitted | engineer | Builder test shows a missing role argument yields no write scope | B:263 (DEC-179) |
| W2-H007 | Missing held-out.yaml silently disables the held-out rule | engineer | gov doctor reports a missing held-out.yaml, or the guard fails closed when it is missing in a repository that declares one | B:282 (DEC-218, DEC-223) |
| W2-H008 | Project can delete or rewrite template secret rules, including the canary | engineer | Template and canary rules are always enforced regardless of the project file | B:479 (DEC-299, DEC-287, DEC-290, DEC-298) |
| W2-H009 | In-place checkpoint save during PreCompact window can be lost | engineer | W1-29 writes atomically and no window remains | B:523 (DEC-306) |
| W2-H010 | New .gov-runtime/ names created after launch not denied | engineer | Late-created .gov-runtime/ paths are refused in launched sessions | B:677 (DEC-311) |
| W2-H011 | Shared git directory writable from a launched worktree session | engineer | Main .git refs are unwritable except through the session's own commit | B:681 |
| W2-H012 | Launcher does not check user ~/.claude/settings.json | engineer | Launcher refuses unsafe user-level settings | B:693 (DEC-313) |
| W2-H013 | Unseen link paths: existing hard links, replaced acceptance-test symlink, cp -s | engineer | Guard resolves links and refuses writes reaching acceptance tests | B:710 |
| W2-H014 | Removed text, including later secrets, persists in SQLite free pages | engineer | Store vacuumed or secure-deleted on removal | B:778 |
| W2-H015 | Direct openspec archive and hand-set spec status bypass readiness | engineer | W1-26 check and W1-35 skill gate archive/apply on readiness | B:798 (DEC-348, DEC-350) |
| W2-H016 | Worker bulk-copied tree including held-out.yaml into scratchpad | engineer | Mechanism prevents copying held-out.yaml, not only briefs | B:897 (DEC-376) |
| W2-H017 | DEC-385 fixture exclusion covers one exact path only | engineer | Exclusion by identity and the check covers all copy paths | B:991 (DEC-385) |
| W2-H018 | Decision checker too slow at scale for every gov check | engineer | The checker runs within the gov check budget on a 200-decision, 20k-commit repository. | B:1081 |
| W2-H019 | Containment rests on self-declared commit trailers | engineer | Trailers are bound to a verified session or launch identity, so forged roles are refused. | B:1123 (DEC-255, DEC-319, DEC-410) |
| W2-H020 | gov check red on this repository: the baseline of 13 hard-block reds | engineer | gov check exits 0 on this repository and the baseline list is empty. | B:1320 (DEC-438, DEC-466, DEC-467, DEC-481, DEC-482) |
| W2-H021 | Declared check commands name template/ paths absent in installed projects | engineer | Declarations resolve kernel paths in installed projects, and checks run there. | B:1482 |
| W2-H022 | Task-less commit adding test configuration outside the ticket folder refuses nothing | engineer | Close refuses task-less changes to test configuration files. | B:1856 (DEC-490, DEC-500) |
| W2-H023 | Close commit range follows date order, not ancestry | engineer | The range is computed by ancestry. | B:1858 (DEC-500) |
| W2-H024 | Any owner decision after an escalation lifts it | engineer | Lift requires a decision that names the escalated ticket. | B:1862 (DEC-500) |
| W2-H025 | Escalation state and counter in caller-writable files | engineer | Escalation state is stored where the caller cannot reset it, or a reset is detected. | B:1863 (DEC-487, DEC-500) |
| W2-H026 | Regression run that collects or passes nothing counts as passed | engineer | Zero collected or passed tests counts as unmeasured or failed. | B:1879 |
| W2-H027 | Evidence record can be hand-written (cheap Wave 2 addition: compare with declarations) | engineer | CI compares the note with the checkout's G3 declarations and refuses a mismatch. | B:1926 (DEC-489, DEC-497) |
| W2-H028 | CI gitleaks scans only the checkout's two commits | engineer | CI scans every commit of the pushed range. | B:1939 |
| W2-H029 | Project can silence the framework-lock comparison; lock unsigned until Wave 3 | engineer | A missing lock fails, and the lock is signed (CAP-02.c). | B:1967 (DEC-499) |
| W2-H030 | Pathless git commands read protected files via tree or history | engineer | Pathless history and tree reads cannot reveal protected file content | B:2276 (DEC-577) |
| W2-H031 | Incomplete save of a guard file stops every session of the worktree | engineer | The guard falls back safely or the save is atomic, so a broken edit cannot lock every session | B:2444 |
| W2-H032 | Without an installed gov, the pre-call hook blocks every call | engineer | The three hooks fall back to the project's src, or say clearly that gov is missing | B:2522 (DEC-603, DEC-609) |
| W2-H033 | External references list read from the working tree; a ticket can self-unblock | engineer | The external list is read from a commit and only decision ids are accepted | B:2337 (DEC-552) |
| W2-H034 | Unreadable mandatory record presented as read (empty hash, 0 tokens) | engineer | An unreadable mandatory record blocks the context or is marked not read | B:2340 (DEC-552) |
| W2-H035 | Dependency proof misses citations, so a store can be released wrongly | engineer | The proof finds every listed citation form and ignores status mislabels | B:2362 |
| W2-H036 | Adoption rollback deletes every untracked non-ignored file | engineer | Rollback refuses or preserves untracked files | B:2393 |
| W2-H037 | Authority check reads 'decision checker could not run' as green | engineer | 'Cannot check' is a finding | B:2652 (DEC-627) |
| W2-H038 | gov close counts adoption-gap refusals toward escalation | engineer | Baseline or adoption-gap refusals do not count toward the escalation counter | B:2731 (DEC-651, DEC-492) |
| W2-H039 | Pre-commit tier runs slow index-freshness and recovery-rebuild checks | engineer | Commits pass with no manual rebuild, both checks run at pre-push or CI, and CAP-17.b is built | B:2802 (DEC-706, DEC-709) |
| W2-H040 | Pre-commit tier holds only fast checks; index checks move to pre-push or CI | engineer | A commit made straight after staging, with no hand rebuild, passes a pre-commit hook that holds only fast checks, and index-freshness and recovery-rebuild run at G3 or in CI. | R:7461 (DEC-709) |
| W2-H041 | Commit-time re-index (CAP-17.b), built first | engineer | After any commit the lexical index matches the committed tree without a hand rebuild, and index-freshness is green. | R:7461 (DEC-709) |
| W2-H042 | Declared, language-agnostic test commands for gov close and the regression | engineer | A project declares its own test command, for example cargo test or vitest, with a parallel option, and gov close and the regression run it in a non-Python repository. | R:5826 (DEC-534, DEC-567) |
| W2-H043 | Impact-based test selection; full suite nightly or in CI | engineer | A close runs only the tests that gov impact names for the change, and the full suite runs nightly or in CI. | R:5827 (DEC-534, DEC-567) |
| W2-H045 | gov close judges a ticket by its class, not always by acceptance tests | engineer | gov close closes a spec ticket on its closed readiness record and an audit ticket on its report, with no acceptance tests and no exception. | R:7003 (DEC-658) |
| W2-H046 | Start ticket leads through the launcher, not a raw claude launch under Auto mode | engineer | An orchestrator session starts a lead through the launcher or another approved mechanism with no classifier denial and no operator step. | R:5865 (DEC-537, DEC-653) |
| W2-H047 | Probe gate refuses after integration branch is merged into ticket branch and back | engineer | A ticket branch probed, then merged with the integration branch and merged back, passes the probe gate when the probed code is unchanged. | R:6361 (DEC-592) |
| W2-H048 | core-authority reads 'decision checker could not run' as green | engineer | core-authority is red or unmeasured whenever the decision checker cannot run, and a case shows it. | R:6902 (DEC-643, DEC-648) |
| W2-H049 | human_gate gaps: decision set active without owner approval trailer | engineer | A planted decision made active without an owner approval trailer turns core-authority red. | R:6713 (DEC-627, DEC-643) |
| W2-H050 | Plain rulesync generate overwrites a programme's own CLAUDE.md and AGENTS.md | engineer | The documented generation in a templated project preserves or merges the programme's own CLAUDE.md and AGENTS.md. | R:6956 (DEC-654, DEC-661) |
| W2-H051 | Delivered tasks.md template is refused by the bridge | product-spec | Template produces a task block the bridge accepts | B:847 (DEC-355, DEC-350) |
| W2-H052 | Harness hook time limit not measured; a hook past its limit lets the call through | research | The harness behaviour at the hook limit is measured and the guard's deadline sits below it | B:2417 (DEC-110, DEC-179, DEC-580) |
| W2-H053 | Governance share not measured per programme (ORION); ARGUS's half is in AR-9 | research | A measured share of at most 15 % on each programme's run (ORION and ARGUS) in governance-share.json, from the counter after clean closes with every part measured; W1-42's share case green. | A F-M1 (DEC-086, DEC-713, DEC-714, DEC-718) |
| W2-H054 | A ticket worktree's tests and gov commands import the editable install's main-tree `src/`, not the worktree's own code | engineer | A ticket worktree's tests and gov commands run that worktree's code, never the editable install's main tree; shown by the import path of `gov` in the worktree's verification. | W2-01 lead run 1, 2026-10-16 (DEC-732) |
| W2-H055 | The guard does not judge `git clone` destinations: a session without a sandbox (orchestrator, lead) can clone into another ticket's folder, the `~/gov-os-runs` root or `~/gov-os-workbench` | engineer | A `git clone` destination is judged as a write target like any other, for every role; a clone into another ticket's folder, the root or the workbench is refused with the guard's reason. | W2-50 CIT-P §6.2, 2026-10-16 (DEC-743) |
| W2-H056 | A copy or install into a folder (`cp X d/`, `cp X d`, `install X d/`, `cp -r s/. d/`) is judged by the folder, so it writes through a symbolic or hard link already in it: an acceptance test, another ticket's file, a local clone's objects | engineer | Every copy or install into a folder is judged as each file it writes, `<folder>/<name>`, under the same link and hard-link rule as a direct write, and refused with the guard's reason. Closed by W2-50. | W2-50 extra review F1, 2026-10-17 (DEC-758) |
| W2-H057 | Guard-hardening pass (Wave 3): no systematic inventory of the command shapes that write (copy into folders, links, merges, opaque interpreters); Wave 2's reviews found three such holes (MultiEdit, the merge-back, the copy through a link) | engineer | Every command shape that writes is inventoried and judged by the guard, each with a test of its own, before qualification. | Owner, 2026-10-17 (DEC-759) |
| W2-H058 | Neither the guard nor the CLI enforces an act command's declared write paths: a role denied a direct write to a file can rewrite it through a `gov` command (found with `gov release --lock-from` and `governance/framework.lock`) | engineer | Every act command's writes are judged against the caller's role and allowed paths, by the guard or by the command, and refused with a reason; each act command has a test of it. | W2-16 last review R2-F1, 2026-10-17 (DEC-761) |
| W2-H059 | Every role check that reads `GOV_ROLE` can be spoofed: a session sets the variable for one command (found with `gov release` from an auditor's session, R3-NAMED) | engineer | A session's identity is bound to its launch, and every role check reads that binding, not a variable the caller sets (W2-44). | W2-16 run-2 review R3-NAMED, 2026-10-18 (DEC-772) |
| W2-H060 | The guard skips a leading `NAME=value` assignment, and reads an `env` prefix as the command, in front of a `gov` command, so a session runs `GOV_ROLE=orchestrator gov …` or `env -u GOV_ROLE gov …` past a role check (found with `gov release`, R3-NAMED) | engineer | The guard refuses a leading `NAME=value` assignment or an `env` prefix in front of any `gov` command, with a reason (W2-42). | W2-16 run-2 review R3-NAMED, 2026-10-18 (DEC-772) |
| W2-H061 | `openspec-validate`, a hard-block check, never measures anything here: it is yellow with "openspec is not on PATH" without node, and yellow with "nothing to validate" with it, and a yellow check does not refuse a close: a false green | owner | Either this repository gets real openspec content that the check validates, green or red, or an owner decision declares the check not applicable here and the check states that; it never stays silently yellow (W2-45). | the blocker sweep, 2026-10-18 (DEC-775, DEC-781) |
| W2-H062 | A backup left by `cp`, `mv` or `install` with `-b`, `-S` or `--backup` onto the settings file is not counted as a second name by the guard's read rule (it is for `sed -i`, DEC-553), so the original can be read at the backup's name; only a session with the orchestrator role reaches it, which today includes every lead (found by W2-50's run-7 review, R1, older than that round) | engineer | The read rule counts the backup name of `-b`, `-S` and `--backup` as a second name of a protected file and refuses it, with a reason (the Wave 3 hardening pass, DEC-801: it needs a deliberate `cp -b` onto the settings file; was W2-42, DEC-785). | W2-50's run-7 review, 2026-10-18 (DEC-779, DEC-785, DEC-801) |

### 3.2 medium (395)

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-M001 | No test against real Ollama; embedding model registry row missing | owner | Ollama installed by owner, registry row added, and a real-daemon test run | B:437 (DEC-195) |
| W2-M002 | Canary near spellings missed; canary count unconfirmed | owner | Owner confirms count; decision on near spellings | B:488 (DEC-286) |
| W2-M003 | gitleaks on CI is an owner install | owner | Owner installs gitleaks on CI | B:504 (DEC-287) |
| W2-M004 | Tickets naming .tickets/ or .claude/ allowed by guard, denied in launch | owner | Decision on how such tickets are executed | B:719 (DEC-315, DEC-312) |
| W2-M005 | Whether WebSearch/WebFetch count as NETWORK_* is unsettled | owner | Owner decision on web tools | B:882 (DEC-158) |
| W2-M006 | Whole-tree fixtures copy settings.json with held-out deny line | owner | Owner answers DP-15 and fixtures strip the line | B:995 (DEC-385) |
| W2-M007 | 1461 held-out-named file copies under /tmp/pytest-of-usain | owner | Owner confirms removal | B:997 |
| W2-M008 | Ticket source texts absent from the readable tree, so no tests derive from them | owner | Every cited source is readable by the test designer, or it is struck from the ticket's sources. | B:1031 (DEC-432) |
| W2-M009 | Unsettled: whether record-type containment findings stay records | owner | An owner decision states how each finding class is treated. | B:1127 (DEC-254, DEC-401, DEC-319) |
| W2-M010 | Owner's manual check of freeze, pause and lift at W1-42 | owner | The owner's manual check is recorded as passed. | B:1407 (DEC-428) |
| W2-M011 | Lexical index stale after every commit; no second rebuild | owner | The index refreshes on commit, or the owner decides on a rebuild at W1-41. | B:1693 (DEC-448, DEC-466) |
| W2-M012 | adapter-portability red: .claude/, CLAUDE.md, AGENTS.md hand-kept | owner | The owner applies the generated adapters, and the check is green. | B:1811 (DEC-481) |
| W2-M013 | No lefthook installed; owner installs at W1 exit once the baseline is empty | owner | The owner runs lefthook install, and the hooks run on commit and push. | B:1912 (DEC-489, DEC-497) |
| W2-M014 | CI runner is a simulation; the real runner is unseen until the owner's first push | owner | The first real push records each step's outcome. | B:1919 |
| W2-M015 | Commit naming another ticket that changes this ticket's paths escapes the probe gate | owner | The gate judges every commit after the probe that touches the ticket's paths | B:2466 (DEC-581) |
| W2-M016 | Harmless tools (Monitor, Artifact, mcp__ read-only) refused in guarded sessions | owner | The owner lists the needed tools or Monitor is judged like Bash | B:2742 (DEC-685) |
| W2-M017 | CAP-10's contract line is 85; DEC-414's pass line is 80; measured 83.33; the contract is not re-baselined | owner | The owner chooses under DEC-105 at the start of Wave 2: apply (reach 85), defer, or re-baseline CAP-10, with EXP-003's figures; 'callers/impact 100.0' is reported beside 87.5 for all classes. | A F-m2 (DEC-105, DEC-414, DEC-718) |
| W2-M018 | gov ci job unmeasured here while openspec is not on the runner (CI_NOT_MEASURED) | owner | The owner installs openspec on the runner (DEC-585's exit package), and gov ci job is measured. | X (runs 6, 7) (DEC-585) |
| W2-M019 | Guard tokeniser drops quotes and expands literal $NAME in write targets | engineer | Guard judges a quoted or escaped $NAME target as the literal path the shell writes | B:63 (DEC-128) |
| W2-M020 | Change by an unseen actor during a Bash call is attributed to that call | engineer | Containment attributes changes by commit trailers or actor, not by the active call | B:67 (DEC-134, DEC-206) |
| W2-M021 | Frozen repo restores acceptance tests changed by opaque Bash regardless of author | engineer | A restore during freeze spares changes by the permitted test designer role | B:69 (DEC-134) |
| W2-M022 | Background command writes are attributed to whichever call is active | engineer | Background command writes are attributed to the launching call or actor | B:83 (DEC-144) |
| W2-M023 | Prefix commands hide sudo or installs from the install rule | engineer | Install rule sees through listed prefix commands, or the orchestrator session is sandboxed | B:95 (DEC-135, DEC-147, DEC-152) |
| W2-M024 | Download piped to a shell inside a subshell is not seen | engineer | Subshell pipe-to-shell is classified as install | B:96 (DEC-135, DEC-147) |
| W2-M025 | Unlisted package managers (yarn add, pnpm add, make install) not seen | engineer | Install rule covers the listed managers or the orchestrator session is sandboxed | B:97 (DEC-135, CAP-25.c) |
| W2-M026 | Evasive install spellings (alias, variable, bash -c, eval, base64) not seen | engineer | Accepted as non-goal (CAP-25.c) or covered by a sandbox in every session | B:98 (DEC-135, CAP-25.c) |
| W2-M027 | Option before -m or before uv subcommand hides install | engineer | Classifier parses options before -m and uv subcommands | B:100 (DEC-135, DEC-147) |
| W2-M028 | Install writing inside the repository not stopped by sandbox write wall | engineer | In-repository installs outside the experiment folder are refused in every role | B:122 (DEC-158, DEC-163) |
| W2-M029 | Launcher deny list fixed at launch; .git/ and glob names excluded | engineer | Late-created paths and .git/ internals are covered by a sandbox rule or containment | B:126 (DEC-163) |
| W2-M030 | Fetch and install commands lose prompt in orchestrator session after ask-rule withdrawal | engineer | Fetch/install forms in the right-hand column are asked or the orchestrator session is sandboxed | B:139 (DEC-172, DEC-174) |
| W2-M031 | Guard does not judge ln; links under .gov-runtime/ unseen | engineer | Guard judges ln targets under protected paths | B:256 (DEC-180, DEC-181) |
| W2-M032 | Held-out relative path after cd or inside --option=value not resolved | engineer | Guard resolves relative held-out paths after cd and in option values | B:272 (DEC-215) |
| W2-M033 | Holder exception follows symbolic links | engineer | Holder exception refuses when the holder file is a symlink | B:275 (DEC-215, DEC-218) |
| W2-M034 | uv run -w<pkg> unseen; --with of inner program misread; env uv add unseen | engineer | Classifier handles joined options, inner-program options and prefixes | B:291 (CAP-25.c, DEC-174) |
| W2-M035 | Here-string sh <<< treated as a non-writing command | engineer | Guard treats here-strings to a shell as opaque writes | B:294 |
| W2-M036 | Here-document interpreter writes judged inconsistently by guard | engineer | Guard gives a consistent, documented verdict on here-document interpreter writes | B:515 |
| W2-M037 | Integration merges produce containment findings | engineer | W1-50 merged and integration merges write no finding | B:354 (DEC-254, DEC-235) |
| W2-M038 | Worker commits in a worktree attributed to the waiting lead | engineer | W1-50 judges each commit by its own Role/Task trailers | B:358 (DEC-254) |
| W2-M039 | Dangling edges from WBS ids and non-record trailer values | engineer | dangling() empty for this repository or the classes are explicitly excluded | B:458 (DEC-277) |
| W2-M040 | Graph reads HEAD while index reads working tree | engineer | W1-20 defines and tests a consistent view | B:463 (DEC-344) |
| W2-M041 | Canary rule over-blocks upper-case identifiers | engineer | Canary rule no longer flags ordinary identifiers | B:483 (DEC-324, DEC-325) |
| W2-M042 | Path-map patterns match narrowly and silently | engineer | W1-27 schema refuses or correctly matches these forms | B:490 (DEC-228) |
| W2-M043 | Secrets-indexing check blind to compressed, UTF-32 and filename secrets | engineer | Check decodes these forms or they are excluded by design | B:496 |
| W2-M044 | Pre-index filter TOCTOU, hard links and split secrets | engineer | Filter and indexer read the same bytes and refuse hard links | B:499 |
| W2-M045 | .gov-runtime/scratch/ counted as a store makes the check red here | engineer | W1-26 excludes or handles scratch, and the check is green here | B:502 |
| W2-M046 | gitleaks trusted by name, version unverified | engineer | gitleaks path and version verified before use | B:504 (DEC-287) |
| W2-M047 | Half-written resume block after kill or double write failure | engineer | Atomic write in W1-29 | B:533 |
| W2-M048 | Checkpoint file kinds: symlink written through, FIFO hangs hooks | engineer | Hooks refuse non-regular checkpoint files | B:537 |
| W2-M049 | Hooks ignore stdin; broken precompact.py makes SessionStart silent | engineer | Hooks read source from stdin and report failures | B:548 |
| W2-M050 | READY rule reads a stale store with no freshness mark | engineer | Store carries a freshness mark and READY refuses a stale store | B:561 |
| W2-M051 | Decision packages that fail to load block nothing | engineer | Unloadable packages block dependants | B:564 (DEC-308) |
| W2-M052 | Specification gate edges | engineer | Gate refuses each edge | B:566 (DEC-307) |
| W2-M053 | in_progress ticket without lock can be claimed; Closed capitalised accepted | engineer | Claim refuses in_progress, closed (any case) and status-less tickets | B:571 (DEC-292) |
| W2-M054 | Acceptance folder naming another ticket's folder or empty still counts | engineer | Both cases refused | B:576 (DEC-293, DEC-300) |
| W2-M055 | Only deps read, not depends_on; SUPERSEDED without edge is good input | engineer | Both keys read and superseded/rejected inputs refused | B:583 |
| W2-M056 | CIT-E rule for taxonomy changes stated only | engineer | W1-26 check fails a taxonomy change without a CIT-E record | B:597 (DEC-309) |
| W2-M057 | evidence and gap_ticket fields carry no id pattern or existence check | engineer | W1-26 check validates gap_ticket existence and state | B:615 (DEC-227) |
| W2-M058 | Nothing enforces the decision-package template | engineer | Tool or skill refuses incomplete packages and answers | B:624 |
| W2-M059 | Effect of declined, revoked or stale packages on waiting tickets | engineer | W1-11 defines and tests the effect | B:630 (DEC-308) |
| W2-M060 | Nothing calls gov checkpoint yet | engineer | Transitions, compactions and stops write checkpoints | B:645 (DEC-280) |
| W2-M061 | Checkpoint numbering has no lock and writes are not atomic | engineer | Numbering locked and writes atomic | B:652 |
| W2-M062 | Watchdog misses input drift and uncommitted checkpoints | engineer | Watchdog re-hashes inputs and handles uncommitted checkpoints | B:655 (DEC-336) |
| W2-M063 | Checkpoint family check passes when no ticket has a checkpoint | engineer | Decision recorded and check behaves accordingly | B:660 |
| W2-M064 | Held-out path travels in launcher argv | engineer | Settings passed by file not argv | B:684 (DEC-223) |
| W2-M065 | Research session starts in repo root; research-created dirs barely seen | engineer | Research session starts in its experiment folder and new dirs are fenced | B:687 (DEC-163) |
| W2-M066 | Guard alone misses many install spellings for worker roles | engineer | Guard covers the forms or the sandbox is documented as the only wall | B:704 (DEC-163) |
| W2-M067 | ln behind a wrapper not judged | engineer | Guard sees ln through wrappers | B:709 |
| W2-M068 | Options after operands misread for touch -d, tee, rsync, dd | engineer | Guard parses these programs' operands correctly | B:713 |
| W2-M069 | Stray module can take over gov status or check | engineer | Reserved commands cannot be overridden | B:735 (DEC-317) |
| W2-M070 | Index-freshness check red here and never green on an empty index | engineer | Check green here after a build, and defined for empty indexes | B:753 (DEC-342, DEC-345, DEC-322) |
| W2-M071 | Lexical search raises instead of returning unavailable | engineer | search returns the DEC-260 unavailable mapping | B:761 (DEC-260) |
| W2-M072 | Lexical query misses mid-token matches; case, stems and ranking unhandled | engineer | Decision recorded and tests cover substring/case/ranking | B:764 |
| W2-M073 | No version pin in store; untracked config changes not re-judged | engineer | Store records versions and config hashes and rebuilds on change | B:769 |
| W2-M074 | Readiness content not judged; zero-width-space N/A reason passes | engineer | Placeholder content refused | B:806 |
| W2-M075 | readiness.close accepts any audit-class ticket; reclosed spec gets none | engineer | close validates the audit ticket state and role | B:811 (DEC-349) |
| W2-M076 | readiness.close partial failures leave orphan tickets or unclosed records | engineer | close is atomic or recoverable with clean errors | B:814 (DEC-349) |
| W2-M077 | Spec id unchecked into audit ticket allowed_paths | engineer | Id validated against grammar before path construction | B:817 (DEC-349) |
| W2-M078 | Readiness YAML duplicate keys last-wins; loose row identity | engineer | Duplicates and malformed rows refused | B:822 |
| W2-M079 | --ticket without specification key returns SPECIFICATION_NOT_FOUND | engineer | Ticket without a specification is reported as not held | B:825 (DEC-307) |
| W2-M080 | Nothing calls gov.tasks.bridge.derive; not exported | engineer | derive exported and used by the W1-35 skill | B:845 |
| W2-M081 | Bridge re-run edges | engineer | Re-run reconciles edits, removals and completions | B:849 (DEC-356) |
| W2-M082 | Bridge does not check role against roster or dependency state | engineer | Role and dependency validated | B:856 |
| W2-M083 | Bridge partial failures, concurrent duplicates and id prefix | engineer | Atomic, locked derive with valid id prefix | B:858 |
| W2-M084 | .claude/agents definitions placed by owner, not generated | engineer | W1-38 generates byte-identical files | B:871 (DEC-352) |
| W2-M085 | Orchestrator and product-spec permission denials have no mechanism | engineer | Denials enforced or accepted by decision | B:875 (DEC-352) |
| W2-M086 | SECRET_READ and SYSTEM_INSTALL not enforced by guard | engineer | Guard rules for secret reads and system installs | B:885 (DEC-074) |
| W2-M087 | Freeze flag appears as a character device inside the sandbox | engineer | Freeze detection distinguishes the placeholder | B:912 |
| W2-M088 | Failed re-index leaves no index; non-UTF-8 name blocks indexing | engineer | Old index kept on failure and non-UTF-8 names handled | B:932 |
| W2-M089 | Graph cached per process; memory at DEC-078 envelope untested | engineer | Cache invalidation and an envelope memory test | B:935 (DEC-078) |
| W2-M090 | Token rule still over- and under-flags after the DEC-325 repair | engineer | Rule tuned and tested on these forms | B:941 (DEC-325, DEC-339) |
| W2-M091 | gitleaks built-in rules sheltered by its global allowlist | engineer | Built-in rules rescanned or a test shows coverage | B:944 (DEC-347) |
| W2-M092 | Filter costs two gitleaks runs per file | engineer | Batched scanning | B:948 (DEC-339) |
| W2-M093 | W1-16 suite heavy and flaky | engineer | Suite isolated and stable | B:959 |
| W2-M094 | Launched worker cannot run the W1-16 suite | engineer | Suite runnable inside a launched sandbox | B:965 |
| W2-M095 | Launcher temp folder stays on kill, SIGTERM, SIGHUP or failed removal | engineer | W1-32 handles signals and removal failure | B:983 (DEC-392) |
| W2-M096 | Worker scratchpad deleted at session end | engineer | Launcher preserves declared outputs | B:989 |
| W2-M097 | Live-session, model and local_only cases cannot run in a launched worker's sandbox | engineer | Workers can run these cases through a sandbox profile, or a recorded lead run of them is a required close step. | B:1006 |
| W2-M098 | Stopping reason for a non-record start id depends on the machine | engineer | The stopping reason is the same on every machine, and the three cases assert it exactly. | B:1018 (DEC-396) |
| W2-M099 | Closure does not check that HEAD is among the store's commits | engineer | Closure or doctor reports a store built for a commit that is not HEAD's. | B:1027 (DEC-391) |
| W2-M100 | W1-17 residuals (search can raise; whole-token matching) unsettled, moved on | engineer | The lexical index's search never raises, matches whole tokens, and has cases for both. | B:1032 |
| W2-M101 | Guard lets through amends, here-documents, sed -i and script edits | engineer | The guard refuses commit --amend and opaque or in-place write commands from workers. | B:1038 |
| W2-M102 | Ranked lexical route for exact identifiers (backlog, later wave) | engineer | A ranked lexical route contributes hits to the fusion on identifier queries. | B:1051 (DEC-414) |
| W2-M103 | fusion.search caps at 30 hits regardless of limit | engineer | fusion.search honours limit, or rejects a limit above its cap. | B:1062 |
| W2-M104 | Reranker that dies after loading makes score raise | engineer | A dead reranker yields the absent path or an envelope error, with a case. | B:1063 (DEC-374) |
| W2-M105 | Merge helper git reached by lazy fetch and GIT_TRACE | engineer | gov.guard.containment_merge sets GIT_NO_LAZY_FETCH and clears GIT_TRACE, with cases. | B:1085 |
| W2-M106 | Decision status and id comparisons are exact and case-sensitive | engineer | A non-canonical status is reported as a finding. | B:1089 |
| W2-M107 | Backdating: author date not compared with committer date | engineer | A divergent author date and committer date on an approval commit is a finding. | B:1097 |
| W2-M108 | Signature as the stricter owner-approval fact not built | engineer | Owner approval can be required as a verified signature. | B:1098 (DEC-360) |
| W2-M109 | Decision checker raises false alarms on legitimate merges | engineer | These merge shapes pass when the owner approved the content. | B:1099 |
| W2-M110 | Tickets waiting on a dead package matched by file stem only | engineer | Tickets in subfolders are matched. | B:1105 |
| W2-M111 | Gates read only the exact key 'approval' | engineer | Variant keys and file forms are reported, not ignored. | B:1107 (DEC-331) |
| W2-M112 | Uncommitted acceptance-test edit not restored when the merge is flagged | engineer | The uncommitted edit is restored as in the non-merge path. | B:1136 |
| W2-M113 | Git configuration not pinned in containment's and W1-03's git calls | engineer | All governance git calls run with pinned configuration and a cleared environment. | B:1146 |
| W2-M114 | Two ticket files with the same wbs_id: first wins silently | engineer | A duplicate wbs_id is a finding. | B:1151 |
| W2-M115 | Late commit on a closed ticket passes via reopen and re-close | engineer | Commits are judged against the close state at their ancestry point, in both directions. | B:1152 |
| W2-M116 | Links or gitlinks at exactly tests/acceptance or .tickets not matched | engineer | The bare names are matched as protected paths. | B:1154 |
| W2-M117 | Lift-form rule bypassed by obfuscated command forms | engineer | Lift is only possible through a non-shell owner path. | B:1173 (DEC-409) |
| W2-M118 | Odd objects at the freeze flag path break pause or read as unfrozen | engineer | Every such object at the flag path reads as frozen and is reported. | B:1177 |
| W2-M119 | Killed pause leaves a freeze.<random> file; flag not synced | engineer | The temp file is cleaned up, and the flag is fsynced before rename. | B:1180 |
| W2-M120 | gov pause --root with a missing path creates it and reports paused | engineer | A missing root is refused. | B:1182 |
| W2-M121 | Long TMPDIR fails the sandbox start but the session exits 0 | engineer | The launcher shortens TMPDIR or reports a non-zero exit. | B:1188 |
| W2-M122 | Guard record unbounded; writers follow links and block on pipes | engineer | Record writes are bounded, refuse links and FIFOs, and record only decided installs. | B:1190 |
| W2-M123 | A session's guard is its own tree's code | engineer | Sessions run a guard from a fixed, verified location. | B:1192 |
| W2-M124 | No zero-result canary for the code index | engineer | A code-index canary runs and is reported by gov doctor. | B:1269 (DEC-037) |
| W2-M125 | Canaries not run after a reindex | engineer | Every reindex or rebuild runs the canaries and reports them. | B:1272 |
| W2-M126 | Supplementary query is the first long word of the ticket title | engineer | The query is built from the ticket's content, with a measured hit rate. | B:1300 (DEC-437) |
| W2-M127 | fresh-agent-reconstruction red because gov is not on the check shell's PATH | engineer | The check runs gov from a resolved path and is measured. | B:1326 |
| W2-M128 | Schema check validates field presence only | engineer | The schema check validates full JSON-schema constraints. | B:1329 |
| W2-M129 | Check command that exits 0 is green whatever it prints | engineer | Check output must be a valid result to count as green. | B:1330 (DEC-285) |
| W2-M130 | Absent tool gives yellow, and yellow refuses nothing | engineer | An absent tool on a hard-block check is red, or is explicitly allowed per project. | B:1331 |
| W2-M131 | Check commands run through a shell unvalidated, with write access | engineer | Check commands are validated and run read-only. | B:1332 |
| W2-M132 | Policy coverage by substring; skill-version accepts any ACTIVE decision | engineer | Exact key matching, and a skill-version check tied to the relevant decision. | B:1334 |
| W2-M133 | Provenance inputs_hash does not hash the inputs | engineer | inputs_hash covers the files the check reads. | B:1336 |
| W2-M134 | validate_notes has no caller; gov context does not use synthesis | engineer | gov context or the exit run calls validate_notes and acts on invalid notes. | B:1365 |
| W2-M135 | Freeze mirror location follows the process's home directory | engineer | The mirror is resolved from the password database rather than HOME. | B:1382 (DEC-429) |
| W2-M136 | No checkpoint on context-utilisation threshold (KPI line 3) | engineer | A hook or watchdog writes a checkpoint on crossing the utilisation threshold. | B:1428 (DEC-445) |
| W2-M137 | Open decisions and loop counts preserved for the orchestrator only | engineer | Worker checkpoints carry open decisions and loop counts, or the KPI is re-scoped. | B:1440 (DEC-096) |
| W2-M138 | Audit validator does not check milestone value or pack_sha256 target | engineer | The validator checks milestone against the plan and the hash against the pack. | B:1478 (DEC-441) (W2-02's part closed by its close, `e52ad8a2`, 2026-10-21; the rest stays open) |
| W2-M139 | Claude Code extension newer than CLI reported as drift; doctor exits 3 | engineer | Doctor treats a newer extension above the minimum as passing, or the pin is updated. | B:1619 (DEC-210, DEC-448) |
| W2-M140 | Several tools pass doctor by version only, not by hash | engineer | Registered hashes are of artefacts present on the machine and are compared. | B:1630 (DEC-448) |
| W2-M141 | core-graph red: depends_on names W1 ids, not record ids | engineer | core-graph is green on this repository. | B:1690 (DEC-466) |
| W2-M142 | retrieval-regression and context-reproducibility unmeasured here | engineer | Both checks are measured green on this repository. | B:1695 (DEC-425, DEC-466) |
| W2-M143 | secrets-indexing exceeds the runner's 60-second limit on this tree | engineer | secrets-indexing is green in the main tree. | B:1696 (DEC-466) |
| W2-M144 | Five policy keys have no associated check | engineer | Each policy key maps to a registered check. | B:1697 (DEC-438) |
| W2-M145 | Decision-citations check accepts any frontmatter id or register heading as a record | engineer | Only decision files in the declared folders and live register entries count. | B:1740 (DEC-466, DEC-463) |
| W2-M146 | Decision-citations check says clean without reporting its measurement scope | engineer | The result reports commits judged, the base move, and branches not judged. | B:1741 (DEC-466) |
| W2-M147 | product-traceability-trailers red with 735 findings | engineer | The base setting is built, ids resolve after adoption, and the check is green. | B:1763 (DEC-476, DEC-482) |
| W2-M148 | Escalation owner decision read from decision files only, not a register | engineer | gov close reads register entries at W1-41 adoption. | B:1773 (DEC-483, DEC-487) |
| W2-M149 | Check-runner error ends close uncounted without a repair ticket | engineer | A runner error is counted and opens a repair ticket. | B:1778 (DEC-466) |
| W2-M150 | Governance-changing defined by fixed path prefixes | engineer | Governance paths are derived from the path map: `gov impact`'s in W2-37; the close command's fixed prefixes (DEC-500's residual 14) in W2-07. | B:1779 (DEC-466, DEC-500, DEC-812) |
| W2-M151 | Check runner's 60-second limit is fixed and untested | engineer | The limit is configurable and a case holds the timeout behaviour. | B:1780 (DEC-466) |
| W2-M152 | Launch record per session (Wave 2 item) | engineer | Each launch writes a record, and close checks sessions and models against it. | B:1786 (DEC-470, DEC-487) |
| W2-M154 | Adapter check says 'matches' without comparing some paths (Wave 2 list) | engineer | Every .claude/ path is classed and judged, and the rulesync artefact is hash-verified. | B:1825 (DEC-466, DEC-471) |
| W2-M155 | No CI step for the adapter comparison; live loading of generated adapters unverified | engineer | A CI step runs the comparison with real rulesync, and W1-42 records live loading. | B:1830 (DEC-497, DEC-471) |
| W2-M156 | Probe record 'by the orchestrator' rests on a self-written Role trailer | engineer | The probe record is bound to a launch record or the guard refuses forged roles. | B:1860 (DEC-500) |
| W2-M157 | Close record lists no skills in a project with an installed kernel | engineer | Close lists installed kernel skills. | B:1864 (DEC-500) |
| W2-M158 | Interrupted ticket-tool close leaves a record and checkpoint that block the next close | engineer | Close is resumable after an interruption. | B:1865 (DEC-500) |
| W2-M159 | Refused close's test run dirties the tree where compiled files are not ignored | engineer | Close runs tests without writing bytecode into the tree. | B:1869 (DEC-500) |
| W2-M160 | Ignored files are in the test tree but not in the commit | engineer | Close runs tests in a clean checkout of the commit. | B:1871 (DEC-500) |
| W2-M161 | Only close's own git is cut off from the caller's environment and refs | engineer | All subprocesses of close run with a sanitised environment and pinned git configuration. | B:1873 (DEC-500) |
| W2-M162 | Acceptance run with one passing test counts as measured whatever was skipped | engineer | Skips above a threshold refuse, or are justified per case. | B:1880 |
| W2-M163 | Governance checks run only when the range touches a governance prefix | engineer | Every close records a check result. | B:1881 |
| W2-M164 | Tree and HEAD checked once at the start of close | engineer | HEAD and tree are re-verified just before closing. | B:1882 |
| W2-M165 | Task-less merge commit bringing ticket work over-refuses | engineer | Merges whose parents were measured pass. | B:1884 |
| W2-M166 | Governance share not yet in the close record | engineer | The close record includes the governance share. | B:1894 (DEC-495) |
| W2-M167 | Hooks bypassable by design (no lefthook on PATH, --no-verify, LEFTHOOK=0) | engineer | Server-side checks cover every pushed commit. | B:1923 |
| W2-M168 | Evidence notes ref with several clones (Wave 2 list) | engineer | Concurrent pushes from two clones keep both notes. | B:1930 (DEC-497) |
| W2-M169 | skill-version check reads a missing parent commit as green; only the last pushed commit compared (Wave 2 list) | engineer | A missing parent is unmeasured, and every pushed commit is compared. | B:1931 (DEC-497) |
| W2-M170 | Yellow passes the CI job; a missing path map yields no policy result | engineer | A missing path map fails the job, and tool-absent codes are generic. | B:1935 (DEC-497) |
| W2-M171 | gitleaks install trusts the pushed registry; binary version not compared | engineer | The binary version is compared, the registry comes from a trusted base, and adoption supplies archive fields. | B:1940 |
| W2-M172 | Strict pre-commit gitleaks scan against canary fixtures, for the exit package | engineer | The strict scan runs and is recorded at the exit. | B:1942 (DEC-489) |
| W2-M173 | Guard refuses mkdir of an allowed file's folder; Write refuses lefthook.yml | engineer | The guard allows creating parent folders of allowed paths. | B:1948 (DEC-489, DEC-497) |
| W2-M174 | Lock comparison ignores __pycache__, non-kernel paths, file modes, empty folders | engineer | The comparison covers modes, folders and declared non-kernel paths. | B:1971 (DEC-488) |
| W2-M175 | Lock task needs a python3 on PATH that imports gov; gov lock subcommand pending | engineer | A gov lock subcommand is used by the Copier task. | B:1976 (DEC-499) |
| W2-M176 | Path-map fix not delivered to existing projects; no check that shipped files are classed | engineer | A check classes every template file, and the update path migrates path-map entries. | B:1993 |
| W2-M177 | Regression summary's last line was the plan validator's, not a suite verdict | engineer | The regression summary's last line is the overall suite verdict. | B:2000 |
| W2-M178 | Estimate reads instruction files as they are now, not as they were in-session | engineer | The estimate uses the instruction-file versions in force during the session, for example by commit at session start | B:2020 (DEC-507) |
| W2-M179 | Session role used by the estimate is the caller's unverified word | engineer | Launch records carry each session's role and the counter reads it from them | B:2022 (DEC-470, DEC-507) |
| W2-M180 | Governance count can be low without any sign | engineer | Each listed shape is either counted or named in the record's known gaps | B:2037 (DEC-502) |
| W2-M181 | Launched workers refused Write and rm under .gov-runtime/scratch/ | engineer | A launched worker can write its scratch files under the runtime scratch folder, or briefs name the allowed scratch location | B:2062 |
| W2-M182 | Governance share in status always 'not measured' | engineer | Ticket sessions are recorded and status shows a measured share | B:2088 (DEC-491) |
| W2-M183 | Status shows no audit tickets, check gates or gate records | engineer | gov status lists audit tickets, check gates and gate records | B:2090 (DEC-088) |
| W2-M184 | Absent .tickets/ or openspec/changes/ reads as an empty list | engineer | A missing folder is reported as not read | B:2095 |
| W2-M185 | Status trusts a store holding HEAD's commit; stale rows read clean | engineer | Status checks the store's integrity and marks a read failure instead of returning empty | B:2096 |
| W2-M186 | Uncommitted decision packages silently absent from status | engineer | Status shows or flags uncommitted packages | B:2099 |
| W2-M187 | Launcher signals only the session process, not its process group | engineer | The launcher signals the whole process group and no child survives | B:2109 (DEC-449) |
| W2-M188 | Resource gate, model-less launch, AUTH_REQUIRED, leads via launcher followed by hand | engineer | Each rule is enforced by a command or check, for example gov launch for leads (see L2819) | B:2163 (DEC-537) |
| W2-M189 | Serial-only entry naming an existing file with no case refuses nothing | engineer | An entry that selects no case is refused | B:2212 (DEC-549, DEC-555) |
| W2-M190 | Folder entry declares nothing; byte-order mark silently drops the first entry | engineer | Folder entries and BOM-prefixed lists are handled or refused | B:2224 |
| W2-M191 | rebuild --no-embeddings leaves stale vectors in the store | engineer | --no-embeddings removes or marks old vectors | B:2229 (DEC-530) |
| W2-M192 | Guard cannot see a script file or piped interpreter that opens protected files | engineer | Such reads are prevented by sandbox or OS-level read denial | B:2272 (DEC-508, DEC-525, DEC-577) |
| W2-M193 | cd followed whether or not it takes effect | engineer | cd is followed only when it takes effect in the same shell | B:2294 (DEC-577) |
| W2-M194 | Root-search shapes not built: find name tests, git grep, xargs, -c shells | engineer | Each shape is judged by the root-search rule | B:2422 (DEC-570, DEC-577) |
| W2-M195 | Over-refusals: here-doc lines, commit messages, find without name test | engineer | These safe shapes are allowed | B:2424 (DEC-577) |
| W2-M196 | Over-limit brace word shortened by the shell reads a held-out folder | engineer | The guard expands or shortens words before skipping long ones, and the shape is refused | B:2438 (DEC-574, DEC-577) |
| W2-M197 | Denied write of the held-out file reveals its place in the reason | engineer | Write refusals for the held-out file name no path | B:2439 (DEC-577) |
| W2-M198 | Refusal at the guard deadline records no finding | engineer | Each deadline refusal writes one guard finding | B:2440 (DEC-580) |
| W2-M199 | Named pipe in hook bookkeeping folder refuses every call after 20 s | engineer | The guard detects and skips a FIFO in its bookkeeping folder | B:2440 (DEC-580) |
| W2-M200 | Bookkeeping program over its 10 s ends in allow with a finding | engineer | A bookkeeping timeout denies, or is shown to be safe | B:2440 (DEC-580) |
| W2-M201 | gov doctor check that the hook limit exceeds the guard deadline | engineer | gov doctor reports when the configured hook limit is not above the guard deadline | B:2442 (DEC-580) |
| W2-M202 | Integration merge into ticket branch after probe, merged back, refuses | engineer | A merge that brings exactly the probed code plus integration content passes | B:2467 (DEC-581) |
| W2-M203 | Task: trailer with unusual spacing escapes probe gate and work-without-task check | engineer | Trailers are parsed with git's trailer parser | B:2467 |
| W2-M204 | Hand-resolved merge that drops probed code passes the gate | engineer | The gate compares the merge's ticket paths with the probed tree | B:2467 (DEC-581) |
| W2-M205 | Probe gate weak checks: ancestor-only, task-less commits, designer commits elsewhere | engineer | The gate covers each shape | B:2467 (DEC-581) |
| W2-M206 | gov check red in installed-layout-only projects until checks can be measured | engineer | gov check in a fresh installed project is green or says 'not measurable' by name | B:2468 |
| W2-M207 | Misspelt 'Constrains:' key and lower-case status words give READY | engineer | An unknown key or a non-canonical status is refused or held | B:2470 (DEC-544) |
| W2-M208 | Close stated-result check satisfied by a printed line; stand-in check root and src only | engineer | The stated result is read from a structured channel and the stand-in check covers the whole import path | B:2471 (DEC-555) |
| W2-M209 | Reopened FULL ticket with an earlier probe record always refuses at probe gate | engineer | The gate judges only the latest probe record, or each record against its own round | B:2485 (DEC-581) |
| W2-M210 | Commit hook waits for the whole secrets scan (137-369 s); result caching | engineer | Scan results are cached so a commit-time scan is fast, and the Bash-limit case is measured | B:2500 (DEC-595) |
| W2-M211 | Hard-block key covered by any declaring check, whatever its severity or tier | engineer | Coverage requires a hard-block check run by that gate | B:2559 (DEC-612) |
| W2-M212 | Success form with findings or 'unmeasured' inside its result is green | engineer | The runner reads findings and unmeasured inside the success form | B:2562 |
| W2-M213 | fresh-agent-reconstruction green with no checkpoint or an unfindable one | engineer | Missing or misnamed checkpoints make the check red or unmeasured | B:2563; R:6636 (DEC-622) |
| W2-M214 | core-pathmap reads namespaces as a list where path maps hold a map | engineer | core-pathmap reads the map form and a case shows it | B:2565 |
| W2-M215 | RETIRED and REJECTED records satisfy a mandatory source | engineer | Retired and rejected records block a mandatory source | B:2339 (DEC-552) |
| W2-M216 | Move to a target no namespace holds is executed, then blocks A8 | engineer | A3 refuses moves to unheld targets | B:2344 (DEC-522) |
| W2-M217 | Project whose .gitignore omits .gov-runtime/ refuses at A8 after A6's rebuild | engineer | Adoption adds .gov-runtime/ to .gitignore or tolerates it | B:2345 (DEC-522) |
| W2-M218 | Project without .gitleaks.toml refuses A3 with a move | engineer | A3 supplies a default or explains the need | B:2346 (DEC-522) |
| W2-M219 | Failed A6 batch leaves earlier batches committed with no A6 record | engineer | A failed batch writes an A6 record and rollback refs are unique | B:2352 |
| W2-M220 | Interrupted adoption batch leaves a staged state with no resume | engineer | Adoption resumes or cleanly rolls back an interrupted batch | B:2355 |
| W2-M221 | Flat-layout packages move without success line 7's grounds | engineer | Flat layouts are recognised as native | B:2358 |
| W2-M222 | Adoption verdict independence rests on self-declared trailers | engineer | Verdict independence is tied to a launch record | B:2373 |
| W2-M223 | Importers computed only for indexed files; A6 does not recheck at HEAD | engineer | Importers cover all files and A6 rechecks at HEAD | B:2375 |
| W2-M224 | Rebuild failure after the record commit refuses though the moves stand | engineer | Rebuild runs before the commit, or the state is reported accurately | B:2381 |
| W2-M225 | A8 misses legacy rule files not in the path map or fixed list | engineer | A8 discovers all known rule places | B:2383 |
| W2-M226 | A3 with a move needs a writable /tmp/gov-cbm-<uid> | engineer | A3 uses a session-writable location | B:2396 |
| W2-M227 | human_gate held by one rule; active decision without owner approval not caught | engineer | Both shapes are caught by a hard-block check | B:2651 (DEC-627) |
| W2-M228 | Context check edge cases: duplicate ids, non-.md names, README in ticket folder | engineer | Each shape is handled and the message is accurate | B:2654 (DEC-628) |
| W2-M229 | rulesync writes no env block; auto-compact entry lost on other machines | engineer | The product sets the auto-compact env entry on adoption | B:2656 (DEC-636) |
| W2-M230 | HELD_OUT_STEP_FAILED merges two causes and hides other drift | engineer | Distinct findings, with other files still compared | B:2666 |
| W2-M231 | Check and hand-run generator use different project roots | engineer | Both use the same root and a case sets them apart | B:2667 |
| W2-M232 | rulesync over existing settings keeps unsourced content and reorders | engineer | A gov command applies the adapter output this way | B:2669 (DEC-645) |
| W2-M233 | Unlaunched worker session can spawn a test-designer subagent that writes acceptance tests | engineer | The guard allows the designer subagent only in an orchestrator session | B:2714 (DEC-664) |
| W2-M234 | Skill text can run inline shell without reaching the guard | engineer | Inline skill shell is switched off in the template settings or judged by the guard | B:2737 (DEC-685) |
| W2-M235 | Launcher wiring check accepts a matcher covering only three write tools | engineer | The wiring check requires a catch-all matcher | B:2738 (DEC-685) |
| W2-M236 | New or renamed harness tools refused until listed | engineer | A per-CLI-version recheck procedure or check exists | B:2743 (DEC-685) |
| W2-M237 | A3 checks what namespaces state, not what retrieval embeds | engineer | A3 and none_embedded() count the files actually embedded | B:2770 (DEC-694) |
| W2-M238 | gov close's trailer gate ignores trailers_base | engineer | gov close's trailer gate honours trailers_base | B:2780 (DEC-482, DEC-690, DEC-695) |
| W2-M239 | Context differs between computations with a live semantic index | engineer | Repeated context computations are identical, and gov ci green | B:2782 (DEC-695) |
| W2-M240 | Staged gates: close runs own plus impacted tests; full suite at milestones | engineer | A close runs the ticket's tests plus the impact-selected tests, and the full suite runs nightly, at each wave exit and before any release. | R:6121 (DEC-567) |
| W2-M241 | Full project test suite runs on CI machines, not the owner's machine | engineer | Where a project allows it, the hosted CI job runs the project's full test suite and reports the result. | R:6122 (DEC-567, DEC-585) |
| W2-M242 | Automatic flaky-test quarantine, shown in gov status | engineer | A fail-then-pass-alone case is marked flaky automatically, kept out of the gate with its record and a deadline, and listed in gov status. | R:6123 (DEC-567) |
| W2-M243 | Secrets-indexing scan checks only changed files | engineer | A second secrets-indexing run on an unchanged store rescans no file and still finds a planted secret in a changed file. | R:6390 (DEC-595) |
| W2-M244 | Resource gate as a command | engineer | A gov command refuses to start a ticket when free memory or load breaks the gate, and a case shows the refusal. | R:5865 (DEC-537) |
| W2-M245 | Launcher refuses a launch without a model | engineer | gov launch with no model exits non-zero, and a case shows the refusal. | R:5865 (DEC-537) |
| W2-M246 | AUTH_REQUIRED as a mechanism | engineer | A gov command returns AUTH_REQUIRED in the envelope and stops in the case the skill names, and a test shows it. | R:5865 (DEC-537) |
| W2-M247 | A launch record per session (id, role, ticket, model) and a Session: trailer | engineer | Every launch writes a record with session id, role, ticket and model, commits carry Session:, and gov close and telemetry attribute sessions with no caller input. | R:5167 (DEC-470, DEC-491, DEC-540) |
| W2-M248 | Session logs read not measured after every CLI update until a new specimen | engineer | After a CLI update, logs of known line types are still measured without waiting for a new specimen, and unknown forms are named. | R:7045 (DEC-663) |
| W2-M249 | gov close counts adoption-gap refusals toward escalation, against DEC-492 | engineer | A refusal for adoption gaps alone leaves the escalation counter unchanged, and a case shows it. | R:6927 (DEC-651) |
| W2-M250 | gov close's trailer gate honours the project's trailers base | engineer | gov close reports no TRAILER_MISSING for commits before the project's trailers_base. | R:7417 (DEC-704, DEC-717) |
| W2-M251 | gov close judges the ticket-creating commit; clone path maps lack a trailers base | engineer | A ticket's creating commit no longer refuses its close, and adoption writes a trailers base into the clone's path map. | R:7146 (DEC-674) |
| W2-M252 | Every repeated refusal opens a new repair ticket | engineer | Repeated refusals for one cause reuse one repair ticket, and the count is not exposed to the session. | R:5325 (DEC-487) |
| W2-M253 | Tests run in a clean checkout of the commit | engineer | gov close runs its tests in a clean checkout of the commit, and an ignored local file cannot change the result. | R:5548 (DEC-503) |
| W2-M254 | Task: trailer with unusual spacing escapes the probe gate and work-without-task check | engineer | Task: trailers with any whitespace form are parsed, and a case with a tab is caught. | R:6363 (DEC-592, DEC-598) |
| W2-M255 | Hand-resolved merge that drops probed code passes the probe gate | engineer | The probe gate refuses a merge whose result differs from the probed code inside the ticket's paths. | R:6363 (DEC-592) |
| W2-M256 | Probe gate ignores another ticket's later commit inside this ticket's paths | engineer | The probe gate refuses, or flags, any later commit that changes the ticket's paths, whatever ticket it names. | R:6398 (DEC-597) |
| W2-M257 | human_gate gap: a gate never written as a decision package | engineer | A planted gate with no package turns core-authority red. | R:6713 (DEC-627, DEC-643) |
| W2-M258 | How the system knows a register entry is the owner's (owner-signed decisions) | engineer | Owner decision commits are signed, and gov close and core-authority accept only entries with a valid owner signature. | R:6266 (DEC-582, DEC-627) |
| W2-M259 | A hard-block policy key is covered by any declaring check | engineer | A policy key counts as covered only by a hard-block check of a stated tier, and a case with a warning-only declarer is red. | R:6636 (DEC-622) |
| W2-M261 | rulesync writes no env block; adopted projects elsewhere lack auto-compact window | engineer | An adopted project on a fresh machine gets the env entry through a documented, generated mechanism. | R:6789 (DEC-636, DEC-643) |
| W2-M262 | Close's test-runner cases and secrets scan fail under concurrent machine load | engineer | Those cases and the scan pass in a close run beside another active session. | R:6887 (DEC-647) |
| W2-M263 | product-traceability-trailers red 'nothing is judged' right after adoption | engineer | Just after adoption the trailers check reads unmeasured or green, not red, until a ticket closes after the base. | R:6900 (DEC-647, DEC-648) |
| W2-M264 | gov doctor reports version drift without failing on it | engineer | gov doctor with only version drift exits 0 and reports the drift. | R:7075 (DEC-659, DEC-667) |
| W2-M265 | Runner reports an absent tool of a hard-block check as red? | engineer | A decision is made, and a hard-block check with its tool absent is red (or explicitly unmeasured and blocking) in gov check and gov close. | R:5263 (DEC-480) |
| W2-M266 | Moving the citations base takes earlier commits out of judgement unreported | engineer | A base move is reported with the number of commits it takes out of judgement. | R:5300 (DEC-485) |
| W2-M267 | Any Markdown file with decision id in frontmatter counts as its record | engineer | Only a schema-valid decision record satisfies a citation. | R:5300 (DEC-485) |
| W2-M268 | Project states on purpose that it declares no G3 check | engineer | gov ci fails when no G3 check is declared and no explicit statement file exists. | R:5448 (DEC-497) |
| W2-M269 | Fetch and merge evidence notes before writing, for multiple clones | engineer | The pre-push hook fetches and merges refs/notes/gov-evidence before writing, and a two-clone case pushes from both. | R:5449 (DEC-497) |
| W2-M270 | Skill-version check: missing parent commit green; only last pushed commit compared | engineer | A missing parent reads not measured, and every commit of a push is compared. | R:5451 (DEC-497) |
| W2-M271 | Hosted CI installs the approved tools by checksum | engineer | The hosted job installs every approved tool verified by its checksum, and no step reads unmeasured for an absent tool. | R:6293 (DEC-585) |
| W2-M272 | Local-only checks reported as local-only by gov ci job | engineer | A check declared local-only is reported as local-only by gov ci job, never failed or green. | R:6293 (DEC-585) |
| W2-M273 | Full git history in CI for checks that read it | engineer | CI fetches the history the checks need, and those checks are measured on the runner. | R:6293 (DEC-585) |
| W2-M274 | core-claims and gov readiness disagree on which rows need gap tickets | engineer | Both use one rule, and a shared case agrees. | R:7037 (DEC-662) |
| W2-M275 | gov rebuild and gov check unusable inside a launched session | engineer | Both commands run to completion inside a launched worker session. | R:7037 (DEC-662) |
| W2-M276 | checker.close writes audit ticket citing DEC-088 and MR-4 | engineer | The audit ticket cites ids that resolve in the project, or kernel ids that are imported. | R:7037 (DEC-662) |
| W2-M277 | Adoption auditor could not reproduce the A3 proposal_sha256 | engineer | An auditor recomputes the recorded proposal_sha256 from the stated inputs. | R:7037 (DEC-662) |
| W2-M278 | Containment check reports sandbox placeholders as worker changes | engineer | A stand-in project reproduces it or not; if it does, the post-command check ignores sandbox placeholders. | R:7315 (DEC-693, DEC-696, DEC-697) |
| W2-M279 | Kernel hook programs look in project's src after the installed package | engineer | Hooks run in a project with gov only under src and none installed, and an installed gov still takes precedence. | R:6499 (DEC-608) |
| W2-M280 | Stop program ends silent with no checkpoint where gov not importable | engineer | Both programs print a reason when gov is not importable, and the stop program exits non-zero. | R:6517 (DEC-609) |
| W2-M281 | Adapter-portability does not read the template's hooks source | engineer | Adapter-portability goes red on a planted drift in the template hooks source, compared by hook events and matchers with paths normalised; the template's `sessionStart` matcher is added in the same change (W2-05's resume, DEC-805). | R:6436 (DEC-601, DEC-805) |
| W2-M282 | Commit hook waits for the whole secrets scan in large stores | engineer | A commit in a large-store project finishes within the agent's tool limit, measured. | R:6433 (DEC-601) |
| W2-M283 | gov readiness --generate automates gap-ticket creation | engineer | gov readiness --generate creates one linked gap ticket per required open cell. | R:824 (DEC-089) |
| W2-M284 | gov discover, the entry point to discovery | engineer | gov discover opens a discovery ticket and schedules evidence-backed research tasks. | R:1529 (DEC-166) |
| W2-M285 | gov impact answers plain-language impact questions | engineer | gov impact returns an impact assessment for a stated change. | R:1536 (DEC-167) |
| W2-M286 | No measured governance share for tickets closed with the ticket tool | engineer | A ticket closed with tk close under an owner decision still gets a measured governance total. | A F-M1; X (DEC-718) |
| W2-M287 | gov doctor reads pytest-xdist as not found (found_version null) while 3.8.0 is installed | engineer | The doctor reads the installed version, and its tools section passes here. | A F-M2; X (DEC-718) |
| W2-M288 | The doctor judges citations inside adoption records and evidence snapshots (path_compliance a named exception) | engineer | The doctor does not judge citations inside adoption records or evidence snapshots. The A5 review record, the three evidence snapshots (gov-commands.json, gov-doctor-run1.json, gov-doctor.json) and the audit report keep the old path unchanged, and path_compliance passes. | A F-M2 (DEC-718 item 4) (DEC-626, DEC-718) |
| W2-M289 | After a --no-embeddings rebuild the doctor reports a semantic canary miss, not 'semantic index not built' | engineer | After gov rebuild --no-embeddings, gov doctor names the semantic index as not built instead of a canary miss. | A F-M2 (DEC-718 item 4) (DEC-709, DEC-718) |
| W2-M290 | gov doctor exits non-zero on this repository | engineer | gov doctor exits 0 on this repository (tools, path compliance and drift each fixed or accepted). | A F-M2 (DEC-667, DEC-718) |
| W2-M291 | The main session records its writes under the closed ticket DAEO-6cc2; leads run as role orchestrator (DEC-434 unbuilt) | engineer | DEC-434's lead role is built, and the main session records under an id of its own. | A F-m7 (DEC-434, DEC-718) |
| W2-M292 | The lexical facet matches a question as one phrase; a plain-word question gets nothing | engineer | The lexical route matches the question's words, and a plain-word question returns lexical hits. | X (run 5) |
| W2-M293 | A ticket-tool close changes a ticket file and leaves the store stale (index freshness, recovery/rebuild red) | engineer | tk close or the commit-time re-index (DEC-709) leaves the store fresh, and the next gov check is green on both families. | X (run 8) (DEC-704, DEC-708, DEC-709) |
| W2-M294 | The context-reproducibility result depends on the store it runs on (green on a stale store, red after a rebuild) | engineer | The check gives the same result on a stale and a fresh store, or reports a stale store as unmeasured (with AR-9's a-dev red). | X (run 8) (DEC-714) |
| W2-M295 | git runs no hook on a merge commit: lefthook installs pre-commit and pre-push only | engineer | A merge into a ticket branch is checked by gov ci checks G1 G2 (a merge hook or a pre-push check of merges). | X (run 8) |
| W2-M296 | A question about an id that exists nowhere returns 20 unrelated semantic items and stops with BUDGET_EXHAUSTED_WITH_GAPS at 404 of 6,000 tokens | engineer | Such a question returns the stated gap without unrelated items, or the owner's RETR-X-02 ruling (AR-9) says otherwise. | X (runs 6, 7) (DEC-714) |
| W2-M297 | Vendored SKILL.md sizes sit exactly on their ceilings | product-spec | Ceilings have headroom or the vendoring update path is defined | B:378 (DEC-247) |
| W2-M298 | Namespace policy fields free text; permitted_roles meaning unconfirmed | product-spec | Closed lists defined, permitted_roles meaning confirmed, and tests cover them | B:397 (DEC-289) |
| W2-M299 | Failure, research, decision-package and checkpoint schemas lack type fields | product-spec | Type-specific required fields defined for these four record types | B:409 |
| W2-M300 | New top-level folder fails the namespace coverage check until added | product-spec | Documented procedure or default namespace for new top-level folders | B:416 |
| W2-M301 | Charter, contract and plan load invalid; templates load as records | product-spec | Core documents load valid, templates excluded, decisions resolvable, duplicates refused | B:454 (DEC-274) (W2-02's part closed by its close, `e52ad8a2`, 2026-10-21; the rest stays open) |
| W2-M302 | Readiness record lacks profile and capability-type fields | product-spec | Schema carries the fields or checker reads them from the contract YAML | B:605 |
| W2-M303 | OpenSpec does not force readiness before tasks | product-spec | Schema makes tasks/apply depend on readiness | B:609 |
| W2-M305 | Nothing writes specification frontmatter; bare gov readiness INVALID | product-spec | Template or skill writes frontmatter and bare readiness passes on a valid change | B:801 (DEC-350) |
| W2-M306 | Undecided which tickets each lesson constrains | product-spec | A decision assigns each lesson's constrained tickets. | B:1256 (DEC-435) |
| W2-M307 | Installed projects must ignore .gov-runtime/ and compiled files | product-spec | The template's ignore file covers .gov-runtime/ and compiled files, and adoption verifies it. | B:1597 |
| W2-M308 | Doctor hard-codes six registry entries; registry lacks location fields | product-spec | Registry schema fields for location and hash scope, with doctor reading only those. | B:1622 |
| W2-M309 | Record store names three docs invalid for lacking a type key | product-spec | The files carry valid frontmatter or are classed as non-records. | B:1662 (DEC-448) (W2-02's part closed by its close, `e52ad8a2`, 2026-10-21; the rest stays open) |
| W2-M311 | Shipped path map invalid against the kernel's path-map schema | product-spec | The shipped path map validates against the schema. | B:1978 (DEC-499) |
| W2-M312 | Adapter generation not run at copy; project-owned .rulesync paths undefined | product-spec | A spec names the project-owned .rulesync paths, and the copy runs generation or checks it. | B:1982 (DEC-488) |
| W2-M313 | Project values in skill and briefs are unfilled, unchecked placeholders | product-spec | Adoption or a check fills the placeholders and flags unfilled ones | B:2170 |
| W2-M314 | Template settings register three hook programs; four more are unregistered | product-spec | The template registers every hook it ships, or removes the unused ones | B:2472 |
| W2-M315 | Each declaring check catches only one kind of violation of its policy | product-spec | Each policy key has checks covering its main violation kinds | B:2558; R:6636 (DEC-612, DEC-622) |
| W2-M318 | Brief's PYTHONPATH=<clone>/src falls through to installed gov when no src/ | product-spec | Briefs and templates name the gov in use explicitly, and a clone without src/ is reported. | R:6959 (DEC-654) |
| W2-M319 | Template path map ships only paths | product-spec | The template path map carries those fields and a tests/** namespace, and validates. | R:7034 (DEC-662) |
| W2-M320 | Rule for a closed specification changed in place | product-spec | A rule exists, and a check flags an in-place edit of a closed specification. | R:7144 (DEC-674, DEC-680) |
| W2-M321 | Wave 2 role roster | product-spec | Kernel role files for each Wave 2 role are generated by rulesync and pass the adapter check. | R:454 (DEC-066, DEC-094) |
| W2-M322 | UX role owns UX readiness with approved wireframes and visual tests | product-spec | A UI feature's readiness row needs approved designs, and its acceptance tests include visual checks. | R:948 (DEC-104) |
| W2-M323 | W1-01 history test fails on first integration merge | independent-test-designer | Revised W1-01 history test green on integration merges | B:364 (DEC-253) |
| W2-M324 | Release flock advisory; double-hold fix unproven | independent-test-designer | Reproduction or a stress test shows no double hold | B:588 |
| W2-M325 | Latency and p95 cases fail under machine load and pass alone | independent-test-designer | The latency cases are isolated from load or tolerate it, and a full regression under load shows no latency failures. | B:1008 (DEC-372) |
| W2-M326 | Missing-code-index case passes inside a sandbox for the wrong reason | independent-test-designer | The case fails when the sandbox refusal is the cause, and passes only for a missing index. | B:1020 |
| W2-M327 | W1-16 not-indexed case fails when any session writes a snapshot | independent-test-designer | The case ignores snapshot writes from other sessions and passes in a full regression run beside live sessions. | B:1073 (DEC-372) |
| W2-M328 | Shared W1-07 support file makes merge-backs flagged repeatedly | independent-test-designer | The shared support files are split per ticket, or aligned merges are not flagged. | B:1131 (DEC-412, DEC-254) |
| W2-M329 | W1-46 live-session cases error when run beside other suites | independent-test-designer | A full regression passes W1-46 without a separate run. | B:1218 (DEC-372) |
| W2-M330 | Cross-process ordering of the supplementary block untested | independent-test-designer | A case holds equal hashes across processes with an index. | B:1296 |
| W2-M331 | W1-35 and W1-36 suites cannot be collected in one pytest run | independent-test-designer | `python3 -m pytest` over both folders collects and passes. | B:1522 |
| W2-M332 | p95 latency and time-limit cases fail under machine load (Wave 3; the fix of `load_sensitive`'s three p95 entries, DEC-762; **target: before W2-24 starts**, DEC-890) | independent-test-designer | Latency cases are serial-only or load-aware and pass in a full parallel regression; their `load_sensitive` entries leave the list | B:2127 (DEC-372) |
| W2-M333 | W1-43's acceptance tests (tests/acceptance/W1-43/) do not exist; the audit-to-repair loop is untested | independent-test-designer | The cases for the W1-43 part of CAP-59.a and CAP-59.b exist, and the loop has run once with them green. | A F-M10 (DEC-718 item 6) (DEC-718) |
| W2-M334 | File-tool Read/Edit/Write run outside the sandbox | research | File-tool access is bound by an OS-level rule or accepted explicitly | B:157 (DEC-152) |
| W2-M335 | Hooks and MCP servers run outside the sandbox | research | Hooks and MCP servers are confined, or the residual is accepted with a recorded decision | B:159 (DEC-152) |
| W2-M336 | EXP-002: untested sandbox cases | research | EXP-002 reports results for each case | B:160 (DEC-160) |
| W2-M337 | EXP-002: subagents inside a sandboxed worker session | research | EXP-002 shows whether subagents inherit the sandbox | B:162 (DEC-164) |
| W2-M338 | Auto-compaction near 300k tokens never observed live | research | A live auto compaction observed with the hook firing | B:531 |
| W2-M339 | Option prefixes, case variants and =true skip flag pass the launcher | research | Real CLI run shows rejection, or the launcher refuses the forms | B:695 (DEC-313) |
| W2-M340 | 60% code-intelligence line measured on designer's own questions | research | W1-42 measures on the dev query set | B:927 (DEC-377) |
| W2-M341 | Semantic retrieval hit@5 85 baseline not reached | research | Measured hit@5 is at least 85 at W1-42 or at qualification. | B:1048 (DEC-343, DEC-414) |
| W2-M342 | Retrieval passes with thin margins (MWA-03) | research | Re-measurement at W1-42 and qualification shows a margin on both lines. | B:1199 (DEC-414, DEC-425) |
| W2-M343 | Skill KPI clauses measurable only by live sessions; unmeasured until W1-42/W1-43 | research | Live-session runs at W1-42/W1-43 measure each clause. | B:1507 |
| W2-M344 | Automatic compaction and PreCompact hook output unmeasured | research | A specimen with a compaction is read and PreCompact output is counted | B:2049 (DEC-502, DEC-512) |
| W2-M345 | Sandbox's added system-prompt tokens not measured | research | A paired with-and-without-sandbox measurement record exists and the counter uses it | B:2053 (DEC-491, DEC-501) |
| W2-M346 | Skill, briefs and status route are text only, not shown in a session | research | A recorded session shows each behaviour | B:2156 (DEC-537) |
| W2-M347 | Other hook programs keep no deadline; harness behaviour at their limit unobserved | research | An experiment records the harness behaviour at hook limits and the other hooks get deadlines as needed | B:2441 (DEC-587) |
| W2-M348 | After a CLI update every log is 'not measured' until a new specimen | research | Unknown forms degrade gracefully, or the specimen refresh is routine | B:2699 (DEC-663) |
| W2-M349 | instructions and sandbox_instructions lines count nothing | research | Measured decision on counting them | B:2700 (DEC-663) |
| W2-M350 | EXP-002: Wave 2 sandbox experiment on untested cases | research | An EXP-002 evidence record gives a measured result for each listed case. | R:1460 (DEC-160, DEC-164) |
| W2-M351 | Scale probes on ~/EXAMIN APP and ~/workspace before Wave 2 | research | Probe evidence records for both repositories exist, with index time, memory and size. | R:491 (DEC-074) |
| W2-M352 | Two branches revising one acceptance-test line cannot be merged | orchestrator | A defined test-designer path resolves conflicting acceptance-test revisions. | B:1034 |
| W2-M353 | gov close merged before any independent probe of its final code | orchestrator | An independent probe of the final close code is run and recorded. | B:1851 (DEC-498) |
| W2-M354 | Repair ticket ade-ke2y in a-dev open and incomplete, turning checks red | orchestrator | ade-ke2y completed or removed, and a-dev claims and schema green | B:2781 (DEC-695) |
| W2-M356 | Mechanise rules the compliance report shows as instruction-only | orchestrator | A re-classified list exists in the exit package, and each item is either mechanised or has a ticket. | R:5115 (DEC-466) |
| W2-M357 | `gov rebuild` exits 0 with `"ok": true` when no index is built (every store `not_recreated` on an unadopted repository) | engineer | `gov rebuild` exits non-zero, or warns by name, when an index it is expected to build is not built; callers no longer need to read `stores.*.status` to know. | W2-26 lead run 2, 2026-10-16 (DEC-735) |
| W2-M358 | EXAMIN's product suite has no reproducible environment of its own (10 packages, a bundled Postgres) | orchestrator | A Docker Compose environment (or the like) runs EXAMIN's whole product suite, the `slow` Postgres tests included, from one declared command. | P-W2-8 (b), 2026-10-16 (DEC-736) |
| W2-M359 | A launched session's Write and Edit tools may not reach its own folder under `~/gov-os-runs` (Claude Code's own check of paths outside the working folder; DEC-313 refuses `--add-dir`), leaving Bash only | engineer | W2-21's launch work shows whether a launched worker's Write and Edit reach its own folder, and either they do or the launch states that only Bash writes there. | W2-50 CIT-P §6.3, 2026-10-16 (DEC-743) |
| W2-M360 | `gov close`'s accepted history trusts the register's text whoever committed it: an entry worded as the owner's, committed by an engineer, was accepted when the path map listed it | engineer | An accepted-history entry counts only when its decision entry was committed by an owner commit (`Role: owner`). | W2-01 probe of run 2, 2026-10-16 (DEC-757) |
| W2-M361 | W1-46's and W1-50's live `local_only` cases start real sessions with the real home and would create the real `~/gov-os-runs`; deselected in every run until W2-21 | engineer | The cases run against a home that is not the owner's and are selected again (W2-21). | W2-50 last review W-1, 2026-10-17 (DEC-751 item 5) |
| W2-M362 | The launcher starts a session with no own folder without saying so (W2-50 CIT-E difference 7) | engineer | The launcher prints a warning line naming the missing own folder (W2-21). | W2-50 last review W-2, 2026-10-17 (DEC-751 item 6) |
| W2-M363 | The own folder's marker is protected by the guard only; the launcher's sandbox does not deny writes to it | engineer | The launcher's sandbox lists the marker under `denyWrite` (W2-21). | W2-50 CIT-E difference 15, 2026-10-17 (DEC-756 item 2) |
| W2-M364 | W1-46's 23 live-session cases fail at setup under parallel load (the launched session runs a step without its `cd`, so its probe script is not found) and pass alone (the fix of their `load_sensitive` entries, DEC-762) | independent-test-designer | The cases are robust under load; their `load_sensitive` entries leave the list (W2-57, in Wave 2, before W2-24; DEC-813). | W2-03 run 2, 2026-10-17 (DEC-760, DEC-762, DEC-813) |
| W2-M384 | W1-30's r13 time-limit case (`test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project`) fails once in the full regression at load about 25 and passes alone, 3 of 3 in 17.8 s with a 2 s reaping margin: its timing, or the close leaving a process alive under load (the fix of its `load_sensitive` entry, DEC-823) | independent-test-designer | The cause is settled and recorded and the case holds under load; its `load_sensitive` entry leaves the list (W2-57, DEC-823). | W2-53's re-close, 2026-10-19 12:01 (P-W2-47; DEC-823) |
| W2-M365 | After the probe, an integration-side edit of the ticket file (DEC-757 item 2.2) can change `profile`, `allowed_paths`, `wbs_id` or `external-ref`, and then unprobed code closes or the acceptance folder moves | engineer | The probe gate reads those fields at the probed commit, or refuses an integration-side edit that changes them (W2-41). | W2-53 review finding 2, 2026-10-17 (DEC-763) |
| W2-M366 | A ticket-file edit after the probe whose commit names another ticket's task passes the probe gate, for an orchestrator's commit and for an engineer's | engineer | Such an edit refuses, for every role. | W2-53 lead P-3, 2026-10-17 (DEC-763) |
| W2-M367 | A refused close's envelope does not carry the ratchet's report: the accepted reds it let through and the load-sensitive re-runs are stated only in a passing close's record | engineer | A refused close states the ratchet's report beside its findings, each test by name (W2-41). | W2-53's first close, 2026-10-18 (DEC-768) |
| W2-M368 | Onto a link at a protected name, the guard allows forms that replace, remove or move the link while it judges the target: `cp` of a FIFO or socket source with `-a`, `-r`, `-R`, `-P`, `-d` or `--no-dereference`; `cp --preserve=links`, `-a` or `--preserve=all` onto a link whose target has a second hard name; `cp -a -t` with sources that are hard links of each other; `mv --strip-trailing-slashes <link>/`. It needs a link already at that name, which no session makes through the guard; W2-50's CIT-E §11 overclaims ("any other form", "a link moved away is judged") | engineer | `decide.py` counts these forms as replacing writes (refused as doubt), and the change record corrects §11 (W2-09). | W2-50's run-7 review, D1 to D4, 2026-10-18 (DEC-779, DEC-785); DEC-801: Wave 3 hardening pass, it needs a link already planted at a protected name |
| W2-M369 | `sed -i` without `--follow-symlinks`, and `rm`, onto a link at a protected name act on the link while the guard judges its target; same precondition as W2-M368 | engineer | The guard judges `sed -i` and `rm` on a link at the link's own path (W2-09). | W2-50's run-7 record engineer, 2026-10-18 (DEC-779, DEC-785); DEC-801: Wave 3 hardening pass, it needs a link already planted at a protected name |
| W2-M370 | `gov context` asks the retrieval only the first word of more than two letters in a ticket's title (`src/gov/context/__init__.py`, since `d454ee7a`), so most Wave 2 tickets ask "The" | engineer | The context's retrieval question is built from the ticket's title and KPI lines, and a test shows two tickets with different titles ask different questions (W2-04). | W2-54's run-2 return, 2026-10-18 (DEC-782) |
| W2-M371 | The probe gate refuses any committed probe record whose judgement is not pass, and has no way to accept a failed record whose findings are all owner-accepted rows (DEC-779); such a ticket closes only through a later round's passing probe (W2-M209) | engineer | The probe gate accepts a failed record whose every finding is named, with its row, in an ACCEPTED owner decision that names the record and its probed commit, and the close names that decision; any finding not so named still refuses (W2-07). | the owner's P-W2-35, 2026-10-18 (DEC-790) |
| W2-M374 | The resource gate counts only what is free now: the CPU-only query embedder (DEC-798) holds about 2.4 GB once loaded, and a start made while it is unloaded can leave too little memory when it loads | engineer | The resource gate counts the CPU embedder's 2.4 GB as standing memory, loaded or not; until then the orchestrator's gate asks 4 GiB plus 2.4 GB while it is not loaded (W2-21, which takes the gate into `gov launch lead`). | DEC-798 item 4 |
| W2-M375 | With `GIT_OBJECT_DIRECTORY` or alternates set by hand in a commit's environment, the git helper clears them, gitleaks cannot read the staged blob, logs git's error and exits 0, so `staged-secrets` passes a staged secret (W2-05's second review, F-B) | engineer | `staged-secrets` refuses, naming the variable, on inherited object, alternate or common-dir variables, and on a git error inside gitleaks (the Wave 3 hardening pass: a deliberate construction, DEC-801, DEC-807). | W2-05 run 2b, 2026-10-19 (DEC-807) |
| W2-M376 | gitleaks follows replace refs (`git replace`), so it scans the clean replacement and a secret commit lands (W2-05's D-1, from before W2-05) | engineer | The secret scan runs with replace refs ignored (`GIT_NO_REPLACE_OBJECTS=1`) (the Wave 3 hardening pass: a deliberate construction, DEC-801, DEC-807). | W2-05 run 2b, 2026-10-19 (DEC-807) |
| W2-M377 | Probe records and audit reports do not say, per finding, whether an honest agent can hit it in ordinary work and what it does, so a deliberate construction can still be taken for a round | product-spec | Every finding in a probe record and an audit report carries `ordinary_work` (yes or no, with its reason) and `consequence` (fails open, loses work or other), in the schemas and the kernel's reviewer brief and audit skill; a finding marked "no" is a row, never a round (W2-11). | DEC-808 item 4 |
| W2-M378 | The lite A10 gate reads A8's record but does not re-check A8's dependency proof or its rule imports (W2-52's reviewer, F-1) | engineer | A10 re-checks the dependency proof and the rule imports A8's record names, and fails naming the one that no longer holds (W2-28, with the machine reader of conditions). | W2-52 run 2b, 2026-10-19 (DEC-810) |
| W2-M379 | The lite A7 gate checks the records' positions, not their content, and a passing A7 or A10 record does not notice later drift (W2-52's reviewer, F-3) | engineer | A7 checks each record's content against its schema, and the adoption verdict re-reads A7 and A10's checked records by their sha256, naming a record that changed after its gate ran (W2-28). | W2-52 run 2b, 2026-10-19 (DEC-810) |
| W2-M380 | The record graph takes tickets' `sources` and `closes` fields and commit trailers as no edges, so a decision that real work cites can read R0 and deletable in `gov impact` and `gov closure` (W2-37 run 1b) | engineer | Those fields and trailers are edges of the record graph, and a decision a ticket or commit cites is never deletable (triaged at W2-03's close). | W2-37 run 1b, 2026-10-19 (DEC-812) |
| W2-M381 | The record store reads a register entry's Supersedes edge from its status line only (W2-37 run 1b) | engineer | A Supersedes or amended-by named anywhere the register's form allows is an edge (triaged at W2-03's close). | W2-37 run 1b, 2026-10-19 (DEC-812) |
| W2-M382 | `gov impact --compare` reads list items written as maps without an `id` all as the item "None", so two hand-written records can match (W2-37's second review, D) | engineer | An item without an id is refused, naming it (the Wave 3 hardening pass: a construction `gov impact` never writes, DEC-801). | W2-37 run 1b, 2026-10-19 (DEC-812) |
| W2-M383 | `gov impact --out` (a read command's write) is not policed by the guard: a plain out-of-scope path is written; `..`, `.git/` and a dangling link too (W2-37's review 1, F5) | engineer | `--out` refuses a path outside the session's allowed paths, through `..`, into `.git/` or through a link (the Wave 3 hardening pass, DEC-801). | W2-37 run 1b, 2026-10-19 (DEC-812) |
| W2-M392 | Adapter portability probes `rulesync --version` with a 10-second limit, which Node's start-up passes under a close's parallel load (`RULESYNC_FAILED`; W1-38's two generated-project cases, W2-53's close of 2026-10-20) | engineer | The probe's limit holds under the close's load, or the close runs these cases in its isolated suite (W2-57, load out of the close). | W2-53's close, 2026-10-20 (P-W2-55, DEC-871) |
| W2-M391 | `gov close`'s escalation counter counts every refused close as a non-converging iteration, so four different causes outside a ticket's code, each already fixed, escalated W2-53 (2026-10-20) | engineer | The counter counts repeated refusals of the same cause, or refusals caused by the ticket's own work; a refusal whose cause lies outside the ticket and is fixed does not count toward the escalation (W2-10). | the owner, 2026-10-20, on P-W2-53 (DEC-870) |
| W2-M393 | The committed launch form and `src/gov/launch/launcher.py` carry `PYTHONPATH` into every launched worker's environment (`{**os.environ, **settings["env"]}`), against DEC-732's "set per command, never in a session's env"; a bare `gov` in such a session runs the tree's code | engineer | The launcher drops `PYTHONPATH` from the session's environment, or states that it passes it on, with a test (W2-56). | W2-59 run 2, P-W2-59-7 (a), 2026-10-20 (DEC-877; ordinary work: yes; other: the hook lines ignore it since `e791465b`) |
| W2-M394 | `gov close`'s work-without-a-task gate (`_check_unmeasured`) reads a merge by its first-parent diff, with no exemption for a merge that is git's own merge of its parents, while the trailer gate has one (DEC-436): a merge-back with a forgotten trailer refuses every later close whose range holds it | engineer | The two gates read such a merge alike: a merge whose tree equals git's own merge of its parents changes no path of its own (Wave 3). | W2-59 run 2, P-W2-59-5 (b), 2026-10-20 (DEC-877; ordinary work: yes; other: fails closed) |
| W2-M396 | W2-54's context-check and time-limit cases run near their 600 s limit under load (609 s at a load near 60; 279 s alone) and are not on `tests/acceptance/serial-only.txt` | engineer | The cases run in the close's isolated serial suite, or their limit holds under the close's load (W2-57). | W2-54 run 5's review, risks, 2026-10-20 (ordinary work: yes; other: fails closed) |
| W2-M400 | Lens H's owner-approved trial installs into its own `/tmp` virtual environment were refused by the guard, which does not read briefs: an owner exception written in a brief cannot reach the guard | engineer | An owner-approved install into a named `/tmp` environment, for one named session, actually works: the exception is declared where the guard reads it (a decision-backed entry it checks), never by a brief alone (W2-56 or W2-10). | lens H, 2026-10-21 (DEC-889 item 17 a; ordinary work: yes; other: fails closed) |
| W2-M401 | Diff-scoped mutation testing is not run on FULL tickets that change the shared core | engineer | cosmic-ray (MIT; edits files on disk, child-safe here), driven by `cr-filter-git` over the ticket's diff, with a selector in its test command, runs on FULL core tickets and its kill rate is in the close record (Wave 3). | lens H B2, 2026-10-21 (DEC-889 item 12) |
| W2-M402 | The Gov OS has no test commands, selection or sharding for Rust (UPIM) or TypeScript (ASMO) | engineer | Through W2-19's declared commands: cargo-nextest for Rust; Vitest or Jest for TypeScript; Nx or Turborepo's affected targets for their monorepos (Wave 3, with UPIM and ASMO). | lens H B2 and C5, 2026-10-21 (DEC-889 item 12) |
| W2-M403 | A FULL ticket closed after a later ticket changed the files its review judged (W2-50 after W2-58's guard work, through W2-58's conflict-resolving merge `eb0f1454`) is refused PROBE_INVALID only at the end of a full close | engineer | The pre-close gate inside `gov close` names a stale probe before the regression runs, so a fresh probe is ordered without spending a close (W2-07). | W2-50's refused close, 2026-10-22 (DEC-894; ordinary work: yes; other: fails closed) |
| W2-M405 | The launcher left two sandboxed engineers' temp folders behind on 2026-10-20 (`/tmp/gov-launch-engineer-*`, 4.1 million inodes, 36 GiB), so W2-C002's fix at W1-28 no longer holds: a worker that ends leaves its temp tree on the shared disk, which the inode floor of DEC-898 then has to absorb | engineer | The launcher removes a sandboxed worker's temp folder when the worker ends, whatever its exit, and a test shows none left after a worker's run (W2-21). | the disk inventory of 2026-10-23 (DEC-902; ordinary work: yes; other: fails closed, the disk gate shuts) |
| W2-M406 | The nightly's cleanup prunes every worktree whose folder it cannot see, so a worktree on an unmounted or unreadable path loses its registration (W2-66's R8) | engineer | The cleanup prunes only the nightly's own clone, by its exact path, in the nightly's next change. | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; loses work) |
| W2-M407 | The nightly's window and length are an orchestrator script's (`tools/nightly.sh night`, `tools/nightly_estimate.py`), not the product's: an adopted product's `gov.close.nightly` has no window, no measured estimate, no clean-start conditions and no locks, and its green does not yet serve as a scoped close's base where the script runs it | engineer | `gov.close.nightly` applies the owner's nightly rule itself for every adopted product: the 02:00 to 05:00 window, the run booked by an estimate measured from the last full runs' per-test durations (the effective parallelism measured, not the worker count), the clean start (no close or merge in progress, the tree clean, the head stable) and its latest start, the close and verification locks during the run, closes resuming at its end, a package when the estimate no longer fits, and a green run recorded as the next day's base (after row W2-M406's fix). | The owner, 2026-10-28 (DEC-933 item 2; ordinary work: yes; other: fails open, a nightly that never runs) |
| W2-M399 | `gov doctor`'s moved-path check does not treat the orchestration record (`governance/project/orchestration/`) as history, so a committed copy that names an old path (a test's own output naming its fixture's path) fails W1-27's case in every tree | engineer | The orchestration record is among the doctor's historical paths, as `docs/source/` is (W2-45). | W2-58 run 3, 2026-10-21 (DEC-882; ordinary work: yes; other: fails closed, every close refused) |
| W2-M398 | A search that starts at a folder above a secret-named file (`.env`, `*.pem` and the like) prints the secret: the guard refuses only reads that name such a file. On 2026-10-21 no such file but two tracked fixtures (`fixtures/brownfield/project/.env`, `fixtures/brownfield/project/config/secrets.yaml`) was found in the repository or its worktrees | engineer | The guard refuses an unnarrowed search over a tree that holds a secret-named file, or the index-style filter covers searches too, without undoing DEC-857's open root searches (the Wave 3 hardening pass). | P-W2-58-3 (c), 2026-10-21 (DEC-880 item 4; ordinary work: yes where such a file exists; fails open; credentials kept out of the trees meanwhile) |
| W2-M397 | The template's own hook source, which adopted projects receive, still starts the first `python3` on `PATH`, not the pin's interpreter as W2-59's lines do here | engineer | The template's hook lines find the pinned judge as this repository's do (W2-18, the pin ladder). | W2-59 run 3's lead, 2026-10-20 (DEC-879; ordinary work: yes; other) |
| W2-M386 | When the secrets check passes the runner's time limit it is RED, but its scan and gitleaks children keep running for minutes, holding 4.7 to 6.2 GB | engineer | The runner ends the check's whole process group at its time limit (W2-45). | W2-50 run 8's probe F6, 2026-10-20 (ordinary work: yes; fails closed; DEC-864) |
| W2-M387 | A first full secrets scan takes 482.8 s against the check's declared 900 s at today's sizes, and every close rebuilds first, so the margin shrinks as the stores grow | engineer | The margin is measured at each close and the limit or the scan recalibrated before it is passed (W2-45). | W2-50 run 8's probe F7, 2026-10-20 (ordinary work: yes; fails closed; DEC-864) |
| W2-M388 | A file under `.gov-runtime/` that vanishes during the secrets scan (a guard snapshot a live session removes) fails the check with `FileNotFoundError` | engineer | A file gone during the walk is skipped and named, never a crash; a file that cannot be read for another reason still fails closed (W2-45). | W2-50 run 8's probe F8 and W2-59 run 1, 2026-10-20 (ordinary work: yes; fails closed; DEC-864) |
| W2-M389 | `precompact.py` and `sessionstart.py` put the project's `src` on their own import path, so a hook program imports the tree's code, not the pin's | engineer | The hook programs import the pinned package only (W2-10, which holds the kernel hooks). | W2-59 run 1, P-W2-59-1 (b), 2026-10-20 (ordinary work: yes; other: they fail soft; DEC-864) |
| W2-M390 | The hook programs themselves are still read from the tree: a ticket that changes a hook program and the package it imports would block every tool call until a re-pin | engineer | A hook program and the package it imports move together on the pin ladder, or the program checks the pin's version and says what to re-pin (W2-18). | W2-59 run 1's residual, 2026-10-20 (ordinary work: yes; fails closed; DEC-864) |

### 3.3 low (445)

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-L001 | Held-out path itself is visible to agents | owner | Owner reconfirms acceptance or the path is hidden from agents | B:278 (DEC-223, DEC-218) |
| W2-L002 | No LICENSE in vendored superpowers copy | owner | Licence shipped with the copy, or owner confirms the vendor folder suffices | B:382 (DEC-244) |
| W2-L003 | Decision-package choices sources do not fix | owner | Owner confirms or decides each choice | B:631 (DEC-093, DEC-220) |
| W2-L004 | Permission classes mapped as families | owner | Audit accepts or refines the mapping | B:873 (DEC-352) |
| W2-L005 | No model tier decision; no model frontmatter | owner | Owner decides tiers and role files carry model | B:878 |
| W2-L006 | Old gov-launch temp folders in /tmp to clear | owner | Operator clears them | B:907 (DEC-386) |
| W2-L007 | Read beyond DEC-370 returned a G-17 row | owner | Owner answers DP-7 | B:920 (DEC-370) |
| W2-L008 | Leftover /tmp folders from W1-16 | owner | Operator removes them | B:970 |
| W2-L009 | Windows-side claude on WSL PATH left in place | owner | Launcher always uses an absolute path, or the owner removes the copy | B:42 (DEC-205) |
| W2-L010 | Body edits that keep an approved decision ACTIVE are not flagged | owner | Body edits to ACTIVE decisions require owner approval, or the decision stays as accepted. | B:1095 (DEC-360) |
| W2-L011 | No hook timeout key in the settings file | owner | The owner sets an explicit hook timeout, or accepts the default. | B:1163 |
| W2-L012 | Empty mirror means frozen; failing lift refuses | owner | The owner confirms or overturns DEC-437 on this point. | B:1388 (DEC-437) |
| W2-L013 | Tests wrote six entries into the real gov-os state folder | owner | The entries are removed, and suites cannot reach the real folder. | B:1395 |
| W2-L014 | Vendored superpowers skills have no version and are not validated | owner | A decision is made, and either versions are added or the exclusion is recorded. | B:1550 (DEC-194) |
| W2-L015 | Whether the old cli/ tree is live or archived | owner | The W1-41 decision on archiving cli/ is recorded. | B:1677 (DEC-456) |
| W2-L016 | 'Nothing else shipped in the overlay' is the brief's reading of DEC-493 | owner | The owner confirms the reading. | B:1986 (DEC-493) |
| W2-L017 | retrieval-regression red because the dev tiers variable is unset | owner | The dev-tier variable is set in the owner's environment, or the check says 'not configured' | B:2575 |
| W2-L018 | ORION's merge 736669f in the a-dev clone was the lead's, after a red CI | owner | In AR-9, programme merges are the owner's, after green CI. | A F-m10 (DEC-714, DEC-718) |
| W2-L019 | HEAD move without before-snapshot checked only against last seen HEAD | engineer | A HEAD move with no snapshot is judged against a per-call baseline | B:68 (DEC-134) |
| W2-L020 | Snapshot cleanup after one hour undercuts larger pending-snapshot timeout | engineer | Cleanup age follows the configured timeout or the timeout is capped at 3600 | B:89 (DEC-135, DEC-137) |
| W2-L021 | Unusable hook input naming an actor clears that actor's leftover snapshot | engineer | Input is validated before the actor's snapshot is cleared | B:90 (DEC-135) |
| W2-L022 | Acceptance test restore stages pre-call HEAD content into the index | engineer | Restore leaves the index consistent with the current HEAD | B:91 (DEC-135, DEC-143) |
| W2-L023 | Install rule false asks on here-documents and 'install' arguments | engineer | These forms no longer trigger ask | B:99 (DEC-135) |
| W2-L024 | Orchestrator session keeps the shared temp directory | engineer | Orchestrator session uses a private temp directory, or this is accepted | B:167 (DEC-159) |
| W2-L025 | Hidden directories look empty to workers with no error | engineer | Workers get a visible signal for hidden paths, or briefs and tools account for it | B:184 |
| W2-L026 | Held-out substring match also denies look-alike siblings | engineer | Match is path-component exact | B:274 (DEC-215) |
| W2-L027 | Duplicate key in held-out.yaml keeps last value | engineer | Duplicate keys are refused | B:285 (DEC-218) |
| W2-L028 | Any truthy dangerouslyDisableSandbox value is denied | engineer | Behaviour documented or narrowed | B:289 |
| W2-L029 | Ollama serve that never becomes healthy is left running | engineer | Test fixes the behaviour for an unhealthy serve | B:429 (DEC-261) |
| W2-L030 | Guard stricter than needed on cp/ln forms | engineer | These harmless forms are allowed | B:387 |
| W2-L031 | Store digest omits frontmatter keys and body; no content_hash | engineer | Digest or content_hash covers body and all frontmatter | B:466 (DEC-276) |
| W2-L032 | Merge commits list no changed paths; renames untested | engineer | Merges and renames handled and tested | B:468 |
| W2-L033 | Secret filter edges fail closed or noisily with tracebacks | engineer | Clean GovError for each case | B:507 |
| W2-L034 | Checkpoint warning after every compaction; same-second and future-time gaps | engineer | W1-29 refines the staleness signal | B:527 (DEC-283, DEC-323) |
| W2-L035 | Pending owner decisions not known to the resume hook | engineer | Resume injection includes pending owner decisions | B:530 (DEC-284) |
| W2-L036 | Resume block parsing edges: trailing text, headings, fences | engineer | W1-29 parser handles or refuses these forms | B:539 |
| W2-L037 | Resume size caps in code points; block unbounded; GOV_TICKET verbatim | engineer | Sizes bounded and GOV_TICKET validated | B:544 |
| W2-L038 | Hook process edges: orphaned tk, no fsync, exit 120 | engineer | Each edge handled | B:546 |
| W2-L039 | Claim holder compared on stripped text; empty lock released by empty holder | engineer | Exact holder match and empty holders refused | B:569 |
| W2-L040 | tasks.create trusts the script's last line and skips the sha256 check | engineer | Hash verified and tk copy decided | B:573 (DEC-295) |
| W2-L041 | Raw exceptions instead of GovError in claims and create | engineer | All raise GovError and leave no stuck lock | B:578 |
| W2-L042 | Minor lock edges: dangling-link lock, duplicate status, filename keying | engineer | Each edge handled | B:585 (DEC-297) |
| W2-L043 | Orchestrator-only gov checkpoint not enforced by the command | engineer | Command refuses non-orchestrator roles | B:648 (DEC-320) |
| W2-L044 | --resume brief without --json is indented JSON | engineer | Human-readable resume brief | B:662 (DEC-317) |
| W2-L045 | Launcher builder test uses unbuilt commands as stand-ins | engineer | Test uses a dedicated fake module | B:664 |
| W2-L046 | gov launch exit code overlaps API-0002 codes | engineer | Distinct exit-code space or documented envelope rule | B:699 (DEC-332) |
| W2-L047 | Stray command module hard-exit makes gov --help exit 0 | engineer | Import failures give a non-zero exit | B:734 (DEC-317) |
| W2-L048 | Store without graph tables gives raw SQLite error | engineer | STORE_MISSING returned | B:758 |
| W2-L049 | Coarse parents and line numbering in the lexical index | engineer | Parent and line handling refined or accepted | B:772 (DEC-343) |
| W2-L050 | lexical.py imports non-exported gov.secrets.CONFIG_REL | engineer | Name exported or import changed | B:781 |
| W2-L051 | Carried cli/govbridge code untouched and not ported | engineer | Ported or retired with cli/tests | B:784 |
| W2-L052 | MR-4 fresh auditor rule rests on orchestrator session rules | engineer | Auditor independence enforced mechanically | B:818 |
| W2-L053 | Readiness taxonomy constants held in code | engineer | Checker reads the taxonomy from the contract YAML | B:830 (DEC-085) |
| W2-L054 | Bridge uses private guard names; globs reaching acceptance not refused | engineer | Public guard API used and globs checked | B:853 |
| W2-L055 | Auditor launched on another role's ticket gets no write path | engineer | Launcher refuses mismatched tickets or the guard aligns | B:887 |
| W2-L056 | Tracked file named by .gitignore silently missing from graph | engineer | Indexed or reported | B:934 |
| W2-L057 | dead_code lists entry points and tests; rename symbol-only | engineer | Entry points excluded and moves tested | B:937 |
| W2-L058 | Codebase-memory daemon dir under shared /tmp never cleaned | engineer | Cleanup defined | B:950 (DEC-338, DEC-346) |
| W2-L059 | Namespace-dependent cases skip without namespaces | engineer | CI runs them | B:957 (DEC-338) |
| W2-L060 | Suite __pycache__ holds planted secret strings | engineer | Strings not persisted in bytecode | B:961 |
| W2-L061 | Temp folder removal by name; nonexistent launcher TMPDIR not run | engineer | Removal by handle and test for a missing TMPDIR | B:986 |
| W2-L062 | Owner-installed tools awaiting tool-registry entries | engineer | Registry lists all three with versions | B:35 (DEC-141, DEC-203) |
| W2-L063 | Launch by WBS id sets GOV_TICKET to the WBS id; a repeated key takes the last value | engineer | The launcher resolves a WBS id to the ticket id, and a duplicate ticket key is refused, with tests for both. | B:1001 |
| W2-L064 | Closure 'uncommitted' ends in a traceback when git fails | engineer | A git failure returns an error envelope. | B:1025 |
| W2-L065 | Vectors built before the 512-character cut not detected as stale | engineer | The manifest records the cut, and a mismatch marks the store stale. | B:1055 |
| W2-L066 | Reranker worker writes a progress bar and prompt line to stderr | engineer | The first load writes nothing to the caller's stderr. | B:1065 |
| W2-L067 | Modules import private helpers of other modules | engineer | Shared helpers are public and named as such, with no cross-module underscore imports. | B:1070 |
| W2-L068 | Code under test leaves ollama serve running | engineer | Runs stop the ollama serve they start, or the decision accepts it. | B:1077 (DEC-261) |
| W2-L069 | Decision with an empty id is followed as 'None' or '' | engineer | An empty id is reported as a finding. | B:1090 |
| W2-L070 | Frontmatter-like heads not read as frontmatter pass silently | engineer | Any file whose head resembles frontmatter but does not parse is reported. | B:1092 (DEC-387) |
| W2-L071 | Deeply nested YAML raises bare RecursionError | engineer | Nested YAML yields a GovError. | B:1104 |
| W2-L072 | Dead package without id fails no ticket | engineer | A dead package without an id is itself a finding. | B:1106 |
| W2-L073 | Clean combination of two orchestrator edits of a ticket file flagged | engineer | A clean same-role combination raises no finding. | B:1135 |
| W2-L074 | Identical both-sides test change with several merge bases fails closed | engineer | Multi-base merges are judged per path. | B:1138 (DEC-417) |
| W2-L075 | Whole-move findings that name no path | engineer | Each such finding records its reason. | B:1140 (DEC-417) |
| W2-L076 | read_merge has no bound for a whole move | engineer | read_merge enforces a bound and normalises ids. | B:1144 |
| W2-L077 | DEC-182 message-body fallback not used by containment | engineer | The check applies the fallback, or a decision drops it. | B:1156 (DEC-182) |
| W2-L078 | Unseen characters inside a role word read as Role: owner | engineer | Trailer normalisation matches the decision text. | B:1157 |
| W2-L079 | Leftovers under tests/acceptance need the owner to delete | engineer | A governed delete path exists for the test designer. | B:1164 |
| W2-L080 | Forged snapshot can conjure a freeze | engineer | Snapshots are authenticated or the case is accepted. | B:1176 |
| W2-L081 | Refusal text says 'stays frozen' without asking the guard's reader | engineer | The message reflects the guard's actual reading. | B:1183 |
| W2-L082 | Rollback reverting a flag-touching commit leaves a dirty tree | engineer | Rollback excludes the flag path or cleans it. | B:1184 |
| W2-L083 | batch_size of zero or less gives a zero-progress continuation | engineer | A non-positive batch_size is refused. | B:1203 |
| W2-L084 | batch_size None and 10 give different continuation tokens | engineer | The tokens are canonicalised on the effective batch size. | B:1207 |
| W2-L085 | MWA-05: CAP-08.a owner and links filters not built (backlog, later wave) | engineer | Both filters are built and tested. | B:1241 (DEC-431) |
| W2-L086 | Canary declarations read from a module-level path | engineer | The declaration path is a parameter. | B:1274 |
| W2-L087 | Commits without a Role: trailer and with wrong co-author models | engineer | A commit hook refuses worker commits without Role: and a wrong model line. | B:1279 |
| W2-L088 | Missing record file gives default content or hash silently | engineer | A missing record file raises an error. | B:1298 |
| W2-L089 | Four Contract-fixed lists are constants in the check code | engineer | They are derived from the Contract file. | B:1337 (DEC-436) |
| W2-L090 | wbs_to_id in claims.py built and never used | engineer | It is removed or used. | B:1340 |
| W2-L091 | Synthesis notes in one file; a second synthesis replaces the first | engineer | Notes are kept per synthesis or per ticket. | B:1363 |
| W2-L092 | Moved repository gets a new freeze mirror key | engineer | The mirror key survives a move, or a move is detected. | B:1378 (DEC-437) |
| W2-L093 | Launched worker's guard reads only the in-repository flag | engineer | The worker guard can read the real mirror read-only. | B:1385 |
| W2-L094 | Hook process writes are not decided by the guard | engineer | Hook writes are restricted to the scratch area, and that restriction is tested. | B:1437 (DEC-444) |
| W2-L095 | stop.py and subagentstop.py duplicated from template hooks | engineer | There is a single source with a generated copy. | B:1443 |
| W2-L096 | Not-applicable opt-in read only from a file named after the check id | engineer | The opt-in is read by declaration id. | B:1476 (DEC-447) |
| W2-L097 | Skill validator checks gov commands against the reserved list, not installed ones | engineer | The validator checks against the installed gov. | B:1480 |
| W2-L098 | Two checks of one family over different folders make family status ambiguous | engineer | Family status aggregates several checks by a defined rule. | B:1555 |
| W2-L099 | judge_commits judges each commit by its own trailers only | engineer | Commits are judged against a launch record. | B:1575 (DEC-453) |
| W2-L100 | Scratch checkpoint without head_commit counts zero commits | engineer | A missing head_commit is reported as invalid. | B:1591 (DEC-444) |
| W2-L101 | Doctor hashes 1.75 GB of models on every run | engineer | Model hashes are cached by mtime and size. | B:1634 |
| W2-L102 | Rebuild takes about 157 s on a 955-file project | engineer | Rebuild time is measured and within an agreed budget. | B:1636 |
| W2-L103 | Rebuild exits 0 when optional indexes are not recreated | engineer | The exit status distinguishes partial rebuilds. | B:1639 |
| W2-L104 | Recovery check unmeasured on a project never loaded | engineer | Fresh projects have a defined recovery state. | B:1642 (DEC-425) |
| W2-L105 | Launches leave temporary gov-launch folders in /tmp | engineer | The launcher removes its temporary folders. | B:1650 |
| W2-L106 | Yellow families at baseline | engineer | Each yellow family is green or explicitly not applicable. | B:1699 (DEC-466) |
| W2-L107 | --disposition finding records no class or context on the repair ticket | engineer | The repair ticket carries class and context_hash. | B:1783 (DEC-466) |
| W2-L108 | Close command inserts fields into the ticket tool's frontmatter itself | engineer | The fields are written through the ticket tool's interface. | B:1784 (DEC-466) |
| W2-L109 | One edit gives many adapter findings | engineer | Findings are grouped by cause. | B:1823 |
| W2-L110 | Ticket argument that is a path writes a counter outside the iterations folder | engineer | Path-like ticket arguments are refused. | B:1868 (DEC-500) |
| W2-L111 | Earlier-round probe record refuses beside a passing one | engineer | Only the probe record of the closing commit is judged. | B:1869 (DEC-500) |
| W2-L112 | Committed conftest.py inside the ticket's own folder runs | engineer | The ticket-folder conftest is restricted to test-designer commits. | B:1884 |
| W2-L113 | deviations always 'not measured'; watchdog given no utilisation | engineer | Both are measured in the close record. | B:1886 |
| W2-L114 | Status read-back after a ticket tool on PATH checks only the status field | engineer | Read-back verifies all fields close wrote. | B:1886 |
| W2-L115 | traceability.py:101 keeps an except Exception | engineer | The handler is narrowed. | B:1888 |
| W2-L116 | Close time limit covers each test run, not the whole close | engineer | A whole-close time limit is enforced. | B:1893 (DEC-487) |
| W2-L117 | gov ci declares class 'read' though push writes a note (Wave 2 list) | engineer | gov ci push is declared as a write. | B:1931 (DEC-497) |
| W2-L118 | Tier selection calls check-runner internals; gov check has no tier option (Wave 2 list) | engineer | gov check exposes a tier option that gov ci uses. | B:1933 (DEC-497) |
| W2-L119 | 'Unmeasured' only for pytest, openspec, rulesync | engineer | Every missing tool reports 'unmeasured' consistently. | B:1944 |
| W2-L120 | Invalid manifest key raises a traceback | engineer | An invalid key yields ERROR. | B:1975 |
| W2-L121 | Doctor on a fresh project mostly unmeasured; reads the real CLI regardless of HOME | engineer | A fresh project after adoption reports these sections measured. | B:1984 |
| W2-L122 | Lock writer blocks on a FIFO under the kernel | engineer | The writer refuses non-regular files. | B:1990 |
| W2-L123 | Sub-agent instruction files and MCP left out of the estimate | engineer | The estimate includes sub-agent instruction files and MCP tool text, or the gap is ruled acceptable | B:2024 (DEC-512) |
| W2-L124 | Counter takes the larger reading for hook text and compound gov commands | engineer | These are counted exactly, or the overcount is bounded and documented | B:2045 |
| W2-L125 | Rewrite ordering uses topological log order; agent.harness is a literal | engineer | Order is judged by ancestry and the harness is read from the log | B:2051 |
| W2-L126 | Any unloadable Markdown record listed under decision_packages | engineer | Only likely packages appear under decision_packages | B:2100 |
| W2-L127 | Status imports private functions; a missing mirror folder reads as not frozen | engineer | Status uses public APIs and handles a missing mirror explicitly | B:2102 |
| W2-L128 | Status passes doctor states without reasons and exits 0 when parts unread | engineer | Status carries doctor's reasons, and its latency is within the KPI | B:2104 |
| W2-L129 | src/gov/cli/commands/status.py is dead code | engineer | The dead module is removed | B:2107 |
| W2-L130 | SIGQUIT/SIGUSR1/SIGKILL or a nohup-ignored signal leaves the session running | engineer | The launcher handles or documents these signals and cleans up the session | B:2111 |
| W2-L131 | Launcher exit-code edge cases (130 race, negative code, non-OSError) | engineer | The launcher always returns the session's code or a defined signal code | B:2113 |
| W2-L132 | launch() from a non-main thread raises before starting | engineer | launch() works from any thread or refuses with a clear error | B:2117 |
| W2-L133 | Refusal printed to an unwritable stderr ends with a traceback's code | engineer | The refusal exit code is kept when stderr cannot be written | B:2118 |
| W2-L134 | First checkpoint record numbered 0002 with no 0001 | engineer | The first checkpoint of a ticket is numbered 0001 | B:2122 |
| W2-L135 | Containment hook attributes designer's files to the lead's waiting call | engineer | Containment attributes each file to the session that wrote it | B:2125 (DEC-253, DEC-254, DEC-255) |
| W2-L136 | Non-UTF-8 byte in serial-only list ends close in a traceback | engineer | A non-UTF-8 list gives a named refusal | B:2214 (DEC-555) |
| W2-L137 | Serial-only entries in undocumented forms double-count or double-run cases | engineer | Entries are normalised and each case counts and runs once | B:2218 |
| W2-L138 | test_runs says parallel/workers auto when no worker started | engineer | test_runs records the actual worker count | B:2220 |
| W2-L139 | close_workers and close_timeout accept odd YAML values and no bounds | engineer | Both keys are bounded and refuse sexagesimal or octal readings | B:2222 |
| W2-L140 | Unusable parallel plugin counted against the ticket, not 'could not measure' | engineer | An unusable plugin gives 'could not measure', and the serial fallback is recorded | B:2226 |
| W2-L141 | Close inside a parallel worker passes the worker variable to its runs | engineer | A nested close clears the runner's worker variable | B:2232 |
| W2-L142 | Path map in a small project brings the lexical index into gov rebuild | engineer | The behaviour is documented or made conditional | B:2240 |
| W2-L143 | Run-time names (substitution, variables, xargs, find -exec) not held for reads | engineer | Run-time names are refused or contained for reads | B:2274 (DEC-577) |
| W2-L144 | Copies or second names made earlier or via symlinks are not recognised | engineer | Content-based or inode-based protection covers copies | B:2278 (DEC-577) |
| W2-L145 | Programs that read the settings file by themselves (claude, rulesync) unseen | engineer | Such programs are listed and judged, or the risk is accepted | B:2280 (DEC-577) |
| W2-L146 | git -C another checkout with a relative path; cd into a run-time folder | engineer | Paths are resolved against git -C targets and created folders | B:2281 (DEC-577) |
| W2-L147 | Copy reached by glob or search starting above its folder | engineer | Searches from above a copy's folder are refused or filtered | B:2282 (DEC-557, DEC-577) |
| W2-L148 | Second names by unknown programs or unparsed options not detected | engineer | Each program is read as a second name, or the risk is accepted | B:2284 (DEC-577) |
| W2-L149 | User-level settings file not at the hook's $HOME unprotected | engineer | The guard finds the user settings location independently of HOME | B:2288 (DEC-577) |
| W2-L150 | Wildcard-only words in non-reader commands; other spellings of 'everything' | engineer | Wildcard-only words are judged | B:2289 (DEC-577) |
| W2-L151 | Shell spellings the token expansion gives up on are allowed | engineer | These spellings are expanded or refused | B:2297 (DEC-577) |
| W2-L152 | bash -c with operator glued to name, eval, here-string into shell allowed | engineer | Inline scripts are tokenised and judged | B:2299 (DEC-577) |
| W2-L153 | Search-tool globs with escapes, braces or comma lists allowed | engineer | Full glob syntax is matched against protected paths | B:2301 (DEC-577) |
| W2-L154 | In-place edit that prints (sed -i 'w /dev/stdout') allowed for a writing role | engineer | Printing in-place edits of protected files are refused | B:2303 (DEC-577) |
| W2-L155 | Hook-listing helper reveals deny paths for unusual rule shapes or spellings | engineer | The helper redacts every protected path whatever its form | B:2304 (DEC-577) |
| W2-L156 | Reading-tool call with list or number path field answered allow | engineer | Malformed path fields are denied | B:2311 (DEC-577) |
| W2-L157 | Root search built at run time escapes the root-search rule | engineer | Run-time-built searches are contained | B:2421 (DEC-577) |
| W2-L158 | rg may wait on non-terminal stdin; slow matcher shapes; NUL in pattern allowed | engineer | rg with no path is not left waiting, and matcher time is bounded | B:2425 (DEC-577) |
| W2-L159 | Held-out check word separation, later-line paths and edit content gaps | engineer | Each shape is refused by the held-out check | B:2439 (DEC-577) |
| W2-L160 | Hook starts git by name; freeze look-up has no limit of its own | engineer | git is resolved by absolute path and the freeze look-up has its own limit | B:2440 (DEC-580) |
| W2-L161 | Forked decision process escapes or orphans; needs os.fork; SIGCHLD-ignored hook refuses all | engineer | The decision process tree is always reaped and findings carry session and tool | B:2440 (DEC-580) |
| W2-L162 | Duplicate allowed_paths: guard uses the union, close uses the last block | engineer | A duplicate key is refused or read the same everywhere | B:2467 |
| W2-L163 | Containment shapes: clean ticket-file combination stays a finding; trailerless/owner commits | engineer | Each shape is decided and pinned | B:2469 (DEC-572, DEC-588) |
| W2-L164 | Store/READY edge cases: unclosed front matter, empty reasons, missing edges | engineer | Each shape gives a named reason or edge | B:2470 |
| W2-L165 | Close misc: repair-ticket cut by count, findings_cut unset, narrow error catch | engineer | Each is fixed or pinned by a case | B:2471 |
| W2-L166 | One gitleaks run can pass the module's own 60 s limit | engineer | A per-run limit is set and measured on the real store | B:2496 (DEC-595) |
| W2-L167 | Stated check limit above about 2,147,483 s ends gov check in a traceback | engineer | The declaration reader enforces an upper bound | B:2497 (DEC-596) |
| W2-L168 | YAML spellings of the limit accepted; duplicate or misspelt keys silent | engineer | Non-decimal spellings, duplicates and unknown keys are refused | B:2498 (DEC-596) |
| W2-L169 | gov check --list entries carry a sixth key when the limit is stated | engineer | The --list entry shape is fixed | B:2499 |
| W2-L170 | File deleted mid-walk or a dangling link makes secrets-indexing red | engineer | Vanished files and dangling links are skipped with a note | B:2501 |
| W2-L171 | Killed check leaves children; scan unbounded; defaults unpinned; template hooks unchecked | engineer | Children are reaped, memory is bounded, defaults are pinned and the template hooks source is checked | B:2504 |
| W2-L172 | Session-start and pre-compaction hooks import a product package named gov from src | engineer | These hooks prefer the installed package | B:2523 (DEC-609) |
| W2-L173 | Relative PYTHONPATH=src in the session environment brings back src-first resolution | engineer | Hooks clear or normalise PYTHONPATH | B:2524 |
| W2-L174 | CLAUDE_PROJECT_DIR unset or empty makes all seven hook commands exit 2 | engineer | Hooks fall back or give a clear refusal | B:2525 |
| W2-L175 | Trailers check in a worktree without a built store reads ids as unresolved | engineer | The trailers check builds or locates a store in worktrees | B:2528 |
| W2-L176 | Record relabelled as a new type leaves type-selecting checks | engineer | Type changes are detected, or checks select by location as well | B:2560 |
| W2-L177 | Type with no schema file not reported unmeasured; id grammars unapplied | engineer | Missing schemas are reported unmeasured and id grammars are applied | B:2564 (W2-02's part closed by its close, `e52ad8a2`, 2026-10-21; the rest stays open) |
| W2-L178 | ci/command.py still passes family names the policy rule ignores | engineer | The parameter is removed | B:2565 |
| W2-L179 | Dead entries in gitleaks config, doctor's historical paths and a closed ticket | engineer | The dead entries are removed | B:2643 (DEC-624) |
| W2-L180 | Any supplementary lookup failure becomes 'index unavailable' | engineer | Failures are reported by kind | B:2341 (DEC-552) |
| W2-L181 | Cursor rule with unquoted globs refuses A8; partial retire refuses too | engineer | Unquoted globs are imported and partial retirement works | B:2360 |
| W2-L182 | 'Active records' wording vs proof reading every standing record; chat-db proof status-blind | engineer | Wording matches behaviour and the chat-db proof checks status | B:2366 |
| W2-L183 | Ticket file change between the context's two reads falls back to every id | engineer | The context reads the ticket once | B:2368 |
| W2-L184 | Unnamed artefacts default to KEEP; unbatched entries go into a last batch | engineer | The defaults are documented or made explicit | B:2378 |
| W2-L185 | Batch check ignores file modes; A8 checks the staged tree, not the commit | engineer | Modes are compared and A8 verifies the commit | B:2379 |
| W2-L186 | rulesync import verified loosely; frontmatter and headings-only sections lost | engineer | Import verification compares frontmatter and keeps all sections | B:2386 |
| W2-L187 | governance/adoption/** outside inventory; stale decision packages kept | engineer | Adoption tracks its own folder and clears resolved packages | B:2391 |
| W2-L188 | Reading the record graph writes .gov-runtime/store.db into the project | engineer | Graph reads do not create the store, or this is documented | B:2394 |
| W2-L189 | Adopt tool uses private functions codeintel._graph and doctor's _match_pattern | engineer | Public APIs are used | B:2395 |
| W2-L190 | External references: dangling symlink, summary cut, unknown keys accepted | engineer | Each is handled or refused | B:2398 |
| W2-L191 | Gate rule reads the last commit; uncommitted package changes unseen | engineer | The gate reads the working tree, or the gap is documented | B:2653 (DEC-329) |
| W2-L192 | Project holding both kernel layouts refused until core-authority copies agree | engineer | Layout precedence is defined | B:2655 |
| W2-L193 | Held-out file without permissions and hooks sources can never be green | engineer | The step creates settings or the check says why | B:2664 (DEC-641) |
| W2-L194 | Settings finding does not mention the held-out step | engineer | The finding names the step | B:2665 |
| W2-L195 | RULESYNC_FAILED echoes 500 characters of rulesync error text | engineer | The echoed text is redacted | B:2670 |
| W2-L196 | Multi-version sessions give version 'not measured' with no reason | engineer | The record lists the versions with a reason | B:2698 (DEC-663) |
| W2-L197 | agent.version can be null; the close record carries no version | engineer | The version is non-null or documented, and the close record carries it | B:2702 |
| W2-L198 | Version pattern accepts non-ASCII digits | engineer | ASCII-only digits | B:2703 |
| W2-L199 | Log line whose type is a list gives a traceback | engineer | A named refusal | B:2704 |
| W2-L200 | Unseen attachment type with no version refused with misleading reason | engineer | The reason names the unseen type | B:2705 |
| W2-L201 | Unreadable Bash writes restored after the fact, not prevented | engineer | Such writes are prevented, for example by the sandbox in every session | B:2716 |
| W2-L202 | Guard does not judge WebFetch URLs against the protected-file read rule | engineer | The guard refuses file URLs that resolve to protected files | B:2739 (DEC-685) |
| W2-L203 | Agent worktree isolation creates worktrees; SendMessage reaches other sessions | engineer | Side effects judged or accepted by decision | B:2740 (DEC-685) |
| W2-L204 | Extra unjudged path field of Edit or MultiEdit ignored | engineer | Unknown fields are denied | B:2741 |
| W2-L205 | A3 does not pin the path map's hash | engineer | A6 and A8 refuse a changed path map | B:2771 (DEC-694) |
| W2-L206 | Doctor's 'no namespace embedded' words only under the semantic canary's answer | engineer | Doctor states it independently of the canary | B:2772 (DEC-694) |
| W2-L207 | Merge queue with batch testing and automatic culprit split | engineer | Several finished tickets merge as one batch tested once, and a failing batch is split automatically to find the culprit (in Wave 2 by W2-68: batched closes, the red batch re-run alone then bisected; DEC-883, DEC-890). | R:6120 (DEC-567) |
| W2-L208 | Each session's own Claude Code version in the telemetry record | engineer | The record lists each session's version, and a mixed-version ticket reports both versions. | R:7044 (DEC-663) |
| W2-L209 | gov close leaves its repair ticket untracked, and without role in b-dev | engineer | A refused close's repair ticket is schema-valid with a role, and its tracking state is decided and tested. | R:7147 (DEC-674) |
| W2-L210 | gov close residuals: overwritten close record, undeclared escalation folder, unresolved Implements ids | engineer | Close records are kept per close, the escalation folder is declared, and Implements: ids are resolved or flagged at close. | R:5325 (DEC-487) |
| W2-L211 | allowed_paths written twice: guard reads the union, close reads the last block | engineer | A ticket file with a duplicated allowed_paths key is refused by the schema. | R:6363 (DEC-592) |
| W2-L212 | Lift clean combinations of ticket files in merge commits | engineer | A clean combination of a ticket file whose sides each passed is not a finding. | R:6335 (DEC-588) |
| W2-L213 | Guard refuses shell words whose brace expansion exceeds a fixed alternative count | engineer | The guard refuses any shell word whose brace expansion exceeds the fixed number of alternatives, whatever its length. | R:6343 (DEC-577, DEC-587, DEC-590) |
| W2-L214 | Lesser guard probe findings from W1-02's last round | engineer | Each of the four shapes has a case showing a bounded, explained result. | R:6323 (DEC-587) |
| W2-L215 | gov doctor checks hook time limit exceeds guard's own deadline | engineer | gov doctor reports unhealthy when any guard hook entry's limit is at or below the guard deadline. | R:6257 (DEC-580) |
| W2-L216 | Guard refuses creating the folder of an allowed file | engineer | mkdir of a parent folder of an allowed path is allowed by the guard. | R:5453 (DEC-497) |
| W2-L217 | Schema check residuals: new types, depends_on shape, id grammars, success form | engineer | The schema check applies the new id grammars and depends_on shape, and the success form with findings inside is not green. | R:6636 (DEC-622) (W2-02's part closed by its close, `e52ad8a2`, 2026-10-21; the rest stays open) |
| W2-L218 | Dead argument the CI command passes to the policy rule | engineer | The argument is removed from gov ci, or the rule uses it, and a test holds which. | R:6620 (DEC-621) |
| W2-L219 | Context and gate-check residuals: ticket names, duplicate ids, both layouts, messages | engineer | Each shape has a case, and ticket files with other extensions and duplicate ids are measured or refused by name. | R:6843 (DEC-643) |
| W2-L220 | Adapter check held-out step residuals | engineer | Distinct finding codes with a remedy text, and a consistent project-root rule between the check and the generator. | R:6856 (DEC-644) |
| W2-L221 | A register heading alone suffices as a decision entry | engineer | A register entry needs a heading and a status line to count. | R:5300 (DEC-485) |
| W2-L222 | Hash or signature on the pre-push evidence note | engineer | CI rejects an evidence note whose hash or signature does not verify. | R:5356 (DEC-489) |
| W2-L223 | Public tier argument of the check runner; tier of tier-less built-in checks | engineer | The runner has a public --tier argument, and each built-in check has a declared tier. | R:5358 (DEC-489) |
| W2-L224 | gov ci declares its class as read | engineer | gov ci's declared class matches its writes. | R:5450 (DEC-497) |
| W2-L225 | actions/checkout bump off Node 20 in workflow and template | engineer | The workflow and its template pin a commit id of a checkout version on a supported Node. | R:6293 (DEC-585) |
| W2-L226 | Show open gate records in gov status | engineer | An open gate record appears in gov status --json. | R:6053 (DEC-543, DEC-556) |
| W2-L227 | Copying template/ directly writes no framework.lock | engineer | Any install path produces framework.lock, or gov doctor names the missing step. | R:6957 (DEC-654) |
| W2-L228 | gov --help says check is 'not built yet' | engineer | gov --help describes check accurately. | R:6960 (DEC-654) |
| W2-L229 | gov.guard.heldout --help has no help and executes | engineer | --help prints usage and writes nothing. | R:7148 (DEC-674) |
| W2-L230 | Session-start and pre-compaction hooks still import a product's own gov package | engineer | With a product package named gov under src, the session-start and pre-compaction programs use the installed gov, and a case shows it. | R:6513 (DEC-609) |
| W2-L231 | Hook residuals: relative PYTHONPATH=src, unset CLAUDE_PROJECT_DIR, unverified variable passing | engineer | Each shape has a measured result recorded, and gov doctor is run on a generated project. | R:6515 (DEC-609) |
| W2-L232 | Secrets-scan time-limit and parallel-scan residuals | engineer | The declaration reader bounds the limit and refuses the odd spellings, worker count and child cleanup are set, and the default has a case. | R:6429 (DEC-601) |
| W2-L233 | Ranked lexical route for exact identifiers | engineer | Exact-identifier queries hit at rank 1 on the dev tiers. | R:4429 (DEC-414) |
| W2-L234 | CAP-08.a owner and links filters | engineer | Record queries filter by owner and by links. | R:4656 (DEC-431) |
| W2-L235 | Trailer findings outside DEC-717 (20 register commits and two closes without Role:, wrong co-author, wrong Task:) | engineer | Accepted as history; AR-8 with the trailers base honoured by gov close (DEC-704), so no new one is made. | A F-m6 (DEC-704, DEC-717, DEC-718) |
| W2-L236 | Repair tickets DAEO-52q7 and DAEO-ldvk moved out of .tickets/ into the orchestrator's scratch log | engineer | gov close writes complete repair tickets that stay tracked (DEC-674's residual). | A F-m8 (DEC-674, DEC-718) |
| W2-L237 | gov --help says running the checks is not built | engineer | gov --help describes check as built. | X (run 5) |
| W2-L238 | A launched session sees eleven dot-files at its project root as untracked files | engineer | A launched session's project shows no untracked dot-files of the launcher's. | X (runs 6, 7) |
| W2-L239 | ADR-0002 and W1-18 ticket text say gov stops Ollama; it does not | product-spec | ADR and ticket text match the start-only behaviour, or stop is implemented | B:369 (DEC-261) |
| W2-L240 | Ticket schema requires only kpis, role, allowed_paths | product-spec | Decision on required ticket fields reflected in the schema | B:403 |
| W2-L241 | Record status is any non-empty string; ticket type unpinned | product-spec | Schemas constrain status values per record type | B:405 |
| W2-L242 | Id grammars undecided except lesson_id; link fields have no grammar | product-spec | Id grammars decided and validated | B:407 (DEC-252, DEC-227) |
| W2-L244 | Four unnamed edge keys need checking against Framework 11.2 | product-spec | Product-spec check recorded against archived Framework 11.2 | B:461 (DEC-277, DEC-012) |
| W2-L245 | blocked can return an empty reason list; cannot-be-read code needs decision | product-spec | Reason code decided and returned | B:581 |
| W2-L246 | feature-readiness vs readiness naming mismatch with G-07/G-08 | product-spec | Sources and briefs use readiness.yaml | B:602 (DEC-305) |
| W2-L247 | validate --strict ignores proposal, design, tasks and readiness | product-spec | Other artefacts validated by gov readiness or a check | B:611 |
| W2-L248 | Package rules live in an HTML comment authors delete | product-spec | W1-35 skills carry the rules | B:637 |
| W2-L249 | Launcher refuses any --setting-sources and guard only in settings.local | product-spec | Behaviour documented or relaxed | B:697 (DEC-314) |
| W2-L250 | Roster header comment stale | product-spec | Comment updated with test adjusted | B:889 |
| W2-L251 | Product-spec role file and agent definition say launcher cannot start it | product-spec | Role file and agent definition updated | B:1000 (DEC-371) |
| W2-L252 | Product-spec role file and agent definition say the launcher does not start it | product-spec | The role file and agent definition describe the launcher's current behaviour for product-spec, or DP-12 is answered. | B:1000 |
| W2-L253 | template/** not embedded because of the path-map value | product-spec | The path map splits vendored paths, and template files are embedded. | B:1058 (DEC-388) |
| W2-L254 | L-0074 written from register entries, not an original lesson text | product-spec | It is checked against an original text if one is found. | B:1262 (DEC-041, DEC-046, DEC-426) |
| W2-L255 | gov --help shows ci, launch, telemetry beyond the twelve reserved names | product-spec | The reserved command list is amended or the extra commands are folded in | B:2120 (DEC-526) |
| W2-L256 | Loose citations in the orchestration skill | product-spec | Each rule cites the decision that covers it | B:2165 (DEC-537, DEC-183, DEC-371, DEC-486) |
| W2-L257 | Launcher command in a code span in brief-lead.md and the role file | product-spec | Templates and role files follow the skill rule, or the validator covers them | B:2172 |
| W2-L258 | Five brief templates have no record frontmatter or schema | product-spec | The briefs have frontmatter and a schema the schema check runs | B:2174 |
| W2-L259 | Repository orchestrator prompt still duplicates the rules in the skill | product-spec | The prompt defers to the skill and briefs | B:2175 |
| W2-L261 | Ticket schema's second form admits any id grammar for depends_on | product-spec | The schema check validates depends_on forms | B:2561 |
| W2-L262 | Documents still point to cli/ as present | product-spec | No active document presents cli/ as present | B:2643 (DEC-624) |
| W2-L263 | carried-code namespace keeps the cli/** pattern and retention text | product-spec | The namespace is updated or removed | B:2643 (DEC-624) |
| W2-L264 | Adoption auditor findings: dead cli/ references, skipped unit case, uninventoried stage records | product-spec | No active document or config names cli/, the unit case is removed or re-based, and stage records are inventoried. | R:6687 (DEC-625) |
| W2-L265 | gov adopt --lite needs --stage and a clean tree | product-spec | The adopt skill or command states, or removes, the precondition. | R:6958 (DEC-654) |
| W2-L266 | ARGUS audit's major finding: retention input contract (created_at, now, aware datetimes) | product-spec | The synthetic programme's spec states the rule, and its implementation follows it. | R:7143 (DEC-674, DEC-680) |
| W2-L267 | Form of a project audit report against the kernel audit validator | product-spec | The audit skill's template produces a report the validator accepts. | R:7145 (DEC-674, DEC-680) |
| W2-L268 | The W1-43 brief did not state DEC-430 | product-spec | The audit brief in the orchestration skill states DEC-430. | A F-m1 (DEC-430, DEC-718) |
| W2-L269 | Unasserted Ollama engineer choices and test designer readings | independent-test-designer | Decisions or tests pin these behaviours | B:431 |
| W2-L270 | Vendored file modes not asserted | independent-test-designer | Test asserts the executable bit | B:381 |
| W2-L271 | Open maps accepting extra keys are untested | independent-test-designer | Tests pin open-map behaviour or the maps are closed | B:411 |
| W2-L272 | Untested W1-08 schema points | independent-test-designer | Tests added for the three points | B:419 (DEC-251, DEC-265) |
| W2-L273 | DEC-182 boundary date and timezone untested | independent-test-designer | Test pins which date decides | B:465 (DEC-182) |
| W2-L274 | STORE_MISSING, STORE_GIT_FAILED and CAP-08.a owner/links filters untested | independent-test-designer | Acceptance cases cover them | B:469 |
| W2-L275 | Unknown schema in config.yaml untested | independent-test-designer | Test added | B:617 |
| W2-L276 | DEC-321 watchdog defaults unasserted by acceptance; thresholds unchecked | independent-test-designer | Acceptance case and range check added | B:650 (DEC-321) |
| W2-L277 | No acceptance test that a new module alone adds a command | independent-test-designer | Acceptance case added | B:736 (DEC-317) |
| W2-L278 | TASKS_NOT_FOUND and TICKET_FAILED untested | independent-test-designer | Tests added | B:862 |
| W2-L279 | Untested wrapper refusals | independent-test-designer | Acceptance tests added | B:939 |
| W2-L280 | W1-16 README fifth-batch section stale | independent-test-designer | Test designer corrects README | B:963 |
| W2-L281 | Pause behaviours that are built but held by no test | independent-test-designer | Acceptance cases hold each of the four behaviours. | B:1003 |
| W2-L282 | Callees in the closure wrapper are thinly tested | independent-test-designer | Cases hold callees against the real tool in a run that the regression includes. | B:1023 (DEC-391) |
| W2-L283 | Closure cases missing for homonym symbols, methods and referenced_by on gaps | independent-test-designer | Cases exist for each of these and for the reranker process. | B:1028 |
| W2-L284 | W1-07 closure cases exercise only STORE_MISSING | independent-test-designer | A W1-07 closure case runs against a loaded store. | B:1030 |
| W2-L285 | Offline reranker loading checked only where the snapshot is absent | independent-test-designer | A case holds offline loading with the snapshot present. | B:1066 |
| W2-L286 | Overlapping ids tested only for identical digit strings | independent-test-designer | A case covers ids that differ in prefix and padding. | B:1109 |
| W2-L287 | Stale docstrings and READMEs in acceptance suites | independent-test-designer | The docstrings and READMEs reflect the decided packages. | B:1161 |
| W2-L288 | local_only mark not registered for the W1-50 folder | independent-test-designer | The mark is registered and the warnings are gone. | B:1195 |
| W2-L289 | MWA-04: W1-03's 'and at gov close' is untested | independent-test-designer | A W1-30 acceptance case asserts that the containment check runs at close. | B:1239 |
| W2-L290 | MWA-06: W1-10 load-time line runs only where the dev tiers are configured | independent-test-designer | The case runs in any configured environment, including CI. | B:1243 |
| W2-L291 | MWA-08: W1-01's deny in every session settings file shown by presence only | independent-test-designer | A case parses each settings file's deny rule and compares it with the guard. | B:1247 |
| W2-L292 | 'Lesson restates policy as authority' checked by fields, not prose | independent-test-designer | A prose check or review covers it. | B:1264 |
| W2-L293 | Case rewrite mislabelled 'owner correction' | independent-test-designer | A test designer corrects the label. | B:1445 |
| W2-L294 | Loose kernel-listing case; no case for an unreadable answers file without a lock | independent-test-designer | The case asserts one reason, and the missing case is added. | B:1988 |
| W2-L295 | W1-46 shared live research session gives setup errors in parallel runs | independent-test-designer | W1-46 passes in a parallel full run | B:2066 |
| W2-L296 | W1-36 helper accepts any PYTHONPATH containing the src path as a substring | independent-test-designer | The helper compares PYTHONPATH elements | B:2233 |
| W2-L297 | W1-27 run_python_snippet and one 30 s wait keep the old bound | independent-test-designer | The W1-27 waits match the new bound | B:2234 |
| W2-L298 | W1-07 30 s read-command wait exceeded under ten workers | independent-test-designer | The W1-07 wait is lengthened and passes under parallel load | B:2235 (DEC-554) |
| W2-L299 | Prefixes, keywords and redirects not held by any case | independent-test-designer | Cases pin each shape either way | B:2423 (DEC-577) |
| W2-L300 | No cases for NUL in edit path, one-character home, other variables | independent-test-designer | Cases pin each input | B:2439 (DEC-577) |
| W2-L301 | W1-30 skipped-only-case test failed under load (inner close time limits) | independent-test-designer | The case passes under full parallel load | B:2452 (DEC-372) |
| W2-L302 | Stale READMEs and docstrings, never-red case, blind spot, worker slips | independent-test-designer | Texts corrected, W1-21 case shown red once, and blind spot covered | B:2475 |
| W2-L303 | No case holds that the harness passes CLAUDE_PROJECT_DIR as env, not text | independent-test-designer | A case pins the behaviour | B:2526 |
| W2-L304 | W1-38 helper returns none for subagentstop.py; repo hooks source unpinned to template | independent-test-designer | Cases cover both | B:2527 |
| W2-L305 | W1-46 live network case fails intermittently in the serial run | independent-test-designer | Network cases are isolated or retried so the close is not red on network blips | B:2534 (DEC-672) |
| W2-L306 | Unit case test_lexical.py skips for good now that its origin is gone | independent-test-designer | The case is rewritten or removed | B:2643 (DEC-624) |
| W2-L307 | Stale W1-26 README count; a killed background script leaves its pytest child | independent-test-designer | README corrected, and children are reaped | B:2401 |
| W2-L308 | W1-26 policy-key case still expects human_gate among owed keys | independent-test-designer | The case is updated | B:2657 |
| W2-L309 | No case for empty held-out list or unreadable file | independent-test-designer | Cases added | B:2668 |
| W2-L310 | W1-33 research-definition case skips where rulesync is absent | independent-test-designer | The case runs without rulesync or the skip is reported | B:2717 (DEC-665) |
| W2-L311 | W1-49 session case skips outside a session and cannot tell export from user entry | independent-test-designer | The case distinguishes the sources | B:2718 (DEC-665) |
| W2-L312 | W1-28 copying-helper list omits W1-33's copy_adapter_source | independent-test-designer | The helper is listed | B:2719 (DEC-675) |
| W2-L313 | Containment count of an allowed MultiEdit held by a unit case only | independent-test-designer | An acceptance case added | B:2745 |
| W2-L314 | W1-49 live-session case asks a small model to repeat four facts | independent-test-designer | The case passes reliably, for example 20 runs alone with no failure. | R:7176 (DEC-676) |
| W2-L315 | CAP-56's transcript acceptance (bundle, no intermediate batch) is tested on the skill text only | independent-test-designer | A test reads a main session's transcript on RETR-X-02 and finds the bundle and no intermediate batch. | A F-m3 (DEC-718) |
| W2-L316 | EXP-002: excludedCommands behaviour | research | EXP-002 tests excludedCommands, or the launcher refuses the setting | B:164 (DEC-164) |
| W2-L317 | 2.8 s scale KPI held as 10 s; G-20 not read | research | G-20 read and target set and measured | B:768 (DEC-341) |
| W2-L318 | Loopback UI port lingers; any call creates config; cost unmeasured | research | Measured and accepted | B:953 (DEC-362, DEC-389) |
| W2-L319 | Closure depth numbers per radius are placeholders | research | The depth values come from a measurement (Wave 3); for Wave 2 the owner set them: 1, 3 and 8 hops (DEC-815). | B:1016 (DEC-035, DEC-391, DEC-815) |
| W2-L320 | Vectors use a brute-force cosine scan, unmeasured beyond the dev tiers | research | Latency is measured on a larger corpus and is within its limit. | B:1060 |
| W2-L321 | Rerank process RAM margin is about 0.2 GB | research | Peak RAM is re-measured with a wider margin, or the limit is re-decided. | B:1067 |
| W2-L322 | Two dev queries lack gold paths; deletable class stuck at 40 | research | The dev tier queries all have reachable gold paths. | B:1068 (DEC-388) |
| W2-L323 | Pause from a sandboxed session with a mounted flag path fails (inferred) | research | Measured behaviour with overlapping sandboxed sessions is recorded. | B:1186 |
| W2-L324 | Share denominator slightly low, so the share reads slightly high | research | W1-42 reports the difference once, or the denominator includes the unseen calls | B:2028 (DEC-501) |
| W2-L325 | Seven log forms 'not measured' until a fourth specimen shows them | research | A specimen shows each form and the counter has a rule for it | B:2032 (DEC-512) |
| W2-L326 | Four passed-over types are known by type and length only | research | A real specimen confirms they carry no governance text | B:2701 (DEC-655) |
| W2-L327 | Decide whether instructions/sandbox_instructions log lines replace the static estimate | research | A decision states whether those lines are counted, and the counter does what it states. | R:7046 (DEC-663) |
| W2-L328 | Deadline for post-call hook programs, after an experiment on harness behaviour | research | An evidence record shows the harness behaviour at the limit, and the post-call programs carry a deadline. | R:6324 (DEC-587) |
| W2-L329 | Spike a lighter reranker to replace Qwen3-Reranker-0.6B | research | A spike evidence record compares a lighter reranker on hit@5, latency and RAM against R1. | R:491 (DEC-074) |
| W2-L330 | Live store writer rule to revisit when gov rebuild is wired | orchestrator | Rule reconfirmed at W1-27 with gov rebuild | B:449 (DEC-322) |
| W2-L331 | Test designer left throwaway reference implementation outside repo | orchestrator | Removed and briefs forbid it | B:787 |
| W2-L332 | W1-50 KPI wording not amended for DEC-410 DP-24 and DP-26 | orchestrator | The ticket's KPI lines are amended. | B:1159 (DEC-410) |
| W2-L333 | MWA-07: four changes outside a ticket's paths | orchestrator | The exit auditor accepts the explanations, or the paths are amended. | B:1245 |
| W2-L334 | Old automatic checkpoint records left untracked under docs/checkpoints | orchestrator | The trees have no untracked automatic records under docs/checkpoints. | B:1595 (DEC-444) |
| W2-L335 | core-decision-citations yellow with 10 findings from unmerged decisions | orchestrator | The orchestrator brief makes merging before citing a standing rule, and no new findings appear. | B:1769 (DEC-453, DEC-454, DEC-470, DEC-476, DEC-480) |
| W2-L336 | pytest-xdist checksum mismatch in tool registry | orchestrator | gov doctor reports pytest-xdist healthy. | R:6797 (DEC-626, DEC-638) |
| W2-L337 | Lesser findings of the ORION and ARGUS exit audits | orchestrator | Each listed finding is fixed or explicitly accepted. | R:7149 (DEC-674) |
| W2-L338 | Outward actions (pushes, hook installs and uninstalls) recorded only after the fact | orchestrator | Each outward action is recorded in the register or the bootstrap record when it is made. | A F-M9 (DEC-718 item 5) (DEC-465, DEC-718) |
| W2-L339 | 19 amends of merge commits on w1/integrate (2026-10-07 to 2026-10-14); standing rule: never amend | orchestrator | The standing rule holds: no commit on w1/integrate is amended or rewritten; a correction is a new commit. | A F-m4 (DEC-718 item 8) (DEC-412, DEC-718) |
| W2-L340 | COMPLIANCE.md stale since 2026-10-07, with wrong base counts | orchestrator | The compliance report is brought up to date at the start of Wave 2, or retired in favour of the exit audit, by the owner's choice. | A F-m5 (DEC-718) |
| W2-L341 | ORION's programme test test_exact_agreement fails before and after ORION-im02 | orchestrator | A ticket of its own in a-dev settles it (the engineer's recommendation: leave it). | X (run 5) |
| W2-L342 | CAP-58's acceptance and CAP-58.d name neither the temp folder nor a session's own folder under `~/gov-os-runs` among the places a launched worker's Bash may write outside the repository | product-spec | The next Contract version's CAP-58 text names both places. | W2-50 CIT-P §6.6, 2026-10-16 (DEC-743) |
| W2-L343 | `docs/contract/contract.yaml` says `status: PROPOSED` while `CONTRACT_v4.md` says ACCEPTED | product-spec | Both files state the same status for Contract v4.2. | W2-49 lead run 1, 2026-10-16 (DEC-741) |
| W2-L344 | `gov close`'s register reader takes an id heading at levels 2 to 6, also inside fenced code; the record store takes only `### DEC-n` outside fences | engineer | Both read entry headings by one rule. | W2-01 probe of run 2, 2026-10-16 (DEC-757) |
| W2-L345 | An inward merge naming another ticket's task that resolves a probed file to the integration side closes on the ticket branch (W2-01's README restates KPI 9 that way) | engineer | Re-checked after W2-53: such a merge refuses, measured against git's own merge of its parents. | W2-01 round 3 probe, 2026-10-16 (DEC-757) |
| W2-L346 | A task-less merge not holding the probed commit, whose own resolution writes byte-identical probed content, escapes the work-without-task rule | engineer | Such a merge is named as work without a task. | W2-01 round 3 probe, 2026-10-16 (DEC-757) |
| W2-L347 | A STANDARD ticket closed after a plain merge-back refuses with work without a task (fails closed) | engineer | A STANDARD ticket's merge-back in the merge form closes. | W2-01 round 3 probe, 2026-10-16 (DEC-757) |
| W2-L348 | The probe gate names only the newest breaking commit when several break the probed code (the close still refuses) | engineer | Every breaking commit is named. | W2-01 split probe, 2026-10-17 (DEC-757) |
| W2-L349 | The marker's refusal is bypassed when the destination is a folder (`mv`, `cp`, `install`, `ln -sf` into the own folder); the session can only hand over its own folder | engineer | Closed with W2-H056 when W2-50's round judges every folder destination as the file it writes; otherwise fixed. | W2-50 extra review F3, 2026-10-17 (DEC-758) |
| W2-L350 | A FIFO in `.tickets/` or in the marker's place makes `gov launch` hang with no end (fails closed) | engineer | `gov launch` refuses a file that is not regular there, within its deadline. | W2-50 last review finding 3 and extra review F4, 2026-10-17 (DEC-751 item 7, DEC-758) |
| W2-L351 | Which commit the owner tags for a release (the commit the manifest names, or the commit holding the release record) is not stated, and `gov release`'s verify does not check the tag against the manifest's `commit` | engineer | The release notes state which commit is tagged, and verify refuses a tag that names another commit. | W2-16 last review R2-P2, 2026-10-17 (DEC-761) |
| W2-L352 | `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it` fails under parallel load (`-n 8`) and passes alone (Wave 3; the fix of its `load_sensitive` entry, DEC-762; **target: before W2-24 starts**, DEC-890) | independent-test-designer | The case is robust under load, or runs serially; its `load_sensitive` entry leaves the list. | W2-53 review, 2026-10-17 (DEC-762) |
| W2-L353 | W1-50 makes a finding of an owner's commit that names a ticket in `Task:`, even when it changes only that ticket's file from the integration side | engineer | W1-50's ledger states the case; owner commits name `Task: decision-record`. | W2-53 lead P-1, 2026-10-17 (DEC-763) |
| W2-L354 | `ln -f` and `ln -sf` into the session's own folder under `~/gov-os-runs` replace its marker; the session can only hand over its own folder | engineer | A link whose destination is the own folder's marker is refused, for every form of `ln`. | W2-50 run-5 review finding C, 2026-10-18 (DEC-765) |
| W2-L355 | An error from the code index during `gov impact`'s walk ends in a traceback, no envelope (W2-37's review 1, F7; fails closed) | engineer | The walk's error is an envelope naming the graph `unavailable` (the Wave 3 hardening pass, DEC-801). | W2-37 run 1b, 2026-10-19 (DEC-812) |
| W2-L356 | The CPU query embedder's model revision is not compared with the revision that built the index (quality only) | engineer | A query vector from a revision other than the index's is refused, naming both revisions (the Wave 3 hardening pass). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L357 | Lowering `GOV_QUERY_VECTOR_CACHE_MAX_BYTES` below the cache's size never shrinks the file, and caching stops | engineer | A lowered bound shrinks the cache to it, oldest entries first (the Wave 3 hardening pass). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L358 | A query-vector cache file that is not a database is never recreated | engineer | A cache that cannot be opened as a database is set aside and rebuilt, named in the output (the Wave 3 hardening pass). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L359 | On AMD or Metal, `CUDA_VISIBLE_DEVICES=-1` does not hide the GPU, so the semantic facet is always unavailable (fails closed) | engineer | The CPU embedder is kept off every GPU backend; an entry criterion of the ticket that supports a non-CUDA backend (DEC-803). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L360 | A process that loses the cache's write race answers with its own vector, not the stored one | engineer | The loser of a write race re-reads and answers with the stored vector (the Wave 3 hardening pass). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L361 | W1-19's and W1-21's write checks accept any one file under `.gov-runtime`, not `query-vector-cache.db` by name | engineer | The checks name the one file a read may write (the Wave 3 hardening pass). | W2-54's review of `7661402c`, 2026-10-19 (ordinary work: no; DEC-801) |
| W2-L362 | Every rebuild runs gitleaks again on every indexable file, in both the lexical and the code-graph indexer, although most files are unchanged since the last rebuild | engineer | Each file's clean secret verdict is reused, keyed on its content hash and the rule set's hash; a changed file is scanned in full; a finding is never reused (W2-06). | P-W2-50 (b), the rebuild diagnosis of 2026-10-19 (1,258 s, most of it the per-file gate; DEC-856) |
| W2-L363 | A ticket that edits a kernel skill in `template/governance/kernel/skills/` has no paths for its rulesync copies (`.rulesync/skills/`, `template/.rulesync/skills/`) or the generated `.claude/skills/`, so the copies go stale and W1-38, W1-30 and adapter portability turn red | product-spec | The skill method and the ticket template say that a skill edit lists its copies, or the orchestrator regenerates them at the merge (W2-11). | W2-62's lead, 2026-10-20 (DEC-863) |
| W2-L364 | The secrets scan reuses a SQLite store's clean result by the store's own bytes, while a secret may stand in its `-wal` or `-journal` file | engineer | A store with a `-wal` or `-journal` beside it is never reused, or the key covers all three files (the Wave 3 hardening pass). | W2-50 run 8's probe F1, 2026-10-20 (ordinary work: no; DEC-801, DEC-864) |
| W2-L365 | Gitleaks' verdict on identical bytes depends on input timing, and the first scan's verdict decides for every later reuse | engineer | The reuse is keyed so that a verdict is never inherited from a scan whose timing differed (the Wave 3 hardening pass). | W2-50 run 8's probe F2, 2026-10-20 (ordinary work: no; DEC-864) |
| W2-L366 | A rules file that `.gitleaks.toml` extends by `path` is outside the secrets scan's reuse key | engineer | The reuse key holds every rules file the configuration reads (the Wave 3 hardening pass). | W2-50 run 8's probe F3, 2026-10-20 (ordinary work: no; DEC-864) |
| W2-L367 | A store's rows are read after its bytes are hashed, so a write between the two is scanned under the old hash | engineer | The rows are read from the same snapshot the hash was taken of (the Wave 3 hardening pass). | W2-50 run 8's probe F4, 2026-10-20 (ordinary work: no; DEC-864) |
| W2-L368 | The secrets scan's reuse label prints a store's file name | engineer | The label names the store by an id, or the name is shown to have no secret (the Wave 3 hardening pass). | W2-50 run 8's probe F5, 2026-10-20 (ordinary work: no; DEC-864) |
| W2-L369 | W2-54's sandboxed-worker test runs a real `gov launch` with the real HOME and leaves `~/gov-os-runs/W1-90/` behind on every regression | independent-test-designer | The test runs with a temporary HOME and leaves nothing behind (a test revision under its ticket's next round, or W2-24). | W2-50 run 8, 2026-10-20 (DEC-864) |
| W2-L370 | W2-50's change-execution record has no section for DEC-853's scan fix | orchestrator | The CIT-E gains the section as a record-only follow-up at W2-50's close. | W2-50 run 8, 2026-10-20 (DEC-864) |
| W2-L372 | W1-49's `test_the_project_settings_set_no_auto_compact_window_of_their_own` still cites DEC-636 in its message and docstring; its assertion is right under DEC-838 | independent-test-designer | The wording names DEC-838, with no change to the assertion, at the next touch of W1-49 (DEC-866). | W2-63 run 1, 2026-10-20 |
| W2-L374 | Policy 2's (c) and (d) are enforced by the guard only: a program a session runs deliberately to open a refused file (an opaque interpreter) is not stopped by the operating system | engineer | An OS-level layer for (c) and (d) that keeps a channel for the session to run its own tests and the scorer, for example a test broker outside the sandbox (the Wave 3 hardening pass; DEC-801, ADR-0001). | P-W2-58-1 (a), 2026-10-20 (DEC-873; ordinary work: no) |
| W2-L375 | W2-59's preToolUse hook line checks only that the interpreter it names is an executable file: a hand-made `gov` naming `/bin/true` ends with exit 0 | engineer | The line checks that the interpreter is the pin's, or that the guard actually ran (the Wave 3 hardening pass; DEC-801). | W2-59 run 2's review, F3, 2026-10-20 (DEC-877; ordinary work: no; fails open, with a deliberate construction) |
| W2-L376 | `gov --version` run from a source tree follows a `GIT_DIR` set by hand | engineer | The version is read from the package's own tree whatever the environment (the Wave 3 hardening pass). | W2-59 run 2's review, F4, 2026-10-20 (DEC-877; ordinary work: no; other) |
| W2-L377 | The pinned judge rewrites only a declared command whose first word is exactly `python3` or `gov`; another form would run unpinned (no declaration uses one today) | engineer | Every declared command form runs from the pin, or a declaration in another form is refused (the Wave 3 hardening pass). | W2-59 run 2's review, F5, 2026-10-20 (DEC-877; ordinary work: no; other) |
| W2-L378 | A project holding both kernel layouts with different canary declarations uses the template's silently | engineer | Two differing declarations are reported, or one layout is chosen by a stated rule (the Wave 3 hardening pass). | W2-59 run 2's review, F7, 2026-10-20 (DEC-877; ordinary work: no; other) |
| W2-L379 | W1-26's `test_readiness_check_all_return_value_not_ignored` and `test_readiness_check_all_exception_caught` plant `src/gov/readiness/checker.py`, which the judge no longer imports, and assert on a family name no family has, so they pass whether or not the plant runs; `test_new_command_module_discovered_by_commands_check`'s condition is always true | independent-test-designer | A test designer revises the three cases so that each fails when its behaviour breaks (`Rewrite-Reason`; the Wave 3 test-hygiene pass). | W2-59 run 2's test designer td-2, 2026-10-20 (DEC-877) |
| W2-L380 | W1-22's README (line 103) and `tests/unit/validate/test_canary.py` still describe a module-level `_TEMPLATE` install path | independent-test-designer | The text describes the install path as built (the Wave 3 test-hygiene pass). | W2-59 run 2's test designer td-2, 2026-10-20 (DEC-877) |
| W2-L382 | W2-54's unit test `test_the_other_types_of_w2_02_stay_unknown` reads less than its acceptance cases: types written over several lines, as a split string or by an item assignment pass it | independent-test-designer | The unit test reads the change as the acceptance cases do (the Wave 3 test-hygiene pass). | W2-54 run 5's review, R1, 2026-10-20 (ordinary work: yes; other: the acceptance cases fail on each form) |
| W2-L383 | W2-54's unit test reads git history under the user's git configuration while its self-check runs under an isolated one | independent-test-designer | Both run under one isolated configuration (the Wave 3 test-hygiene pass). | W2-54 run 5's review, R2, 2026-10-20 (ordinary work: no; other) |
| W2-L384 | A hand edit inside one of W2-54's own merges is not counted as W2-54's change by its S4 cases | independent-test-designer | A merge's own resolution lines are read as the ticket's change (the Wave 3 hardening pass; DEC-801). | W2-54 run 5's review, R3, 2026-10-20 (ordinary work: no, DEC-754 item 4; fails open for that construction only) |
| W2-L385 | An own edit of `src/gov/check/schema.py` by W2-54 after W2-02's merge is in its branch turns its module cases red although it adds no type | independent-test-designer | The module cases judge only what W2-54's own commits add (the README's stated limit; when W2-54 next touches the module). | W2-54 run 5's review, R4, 2026-10-20 (ordinary work: yes; other: fails closed) |
| W2-L386 | Under `-E`, `PYTHONUSERBASE` still sets the pin interpreter's user site, so a `usercustomize` there runs in a hook line; W2-59's CIT-P §3.2 and §9 say otherwise | engineer | The lines also ignore the user site (`-s`), or the CIT-P states it (the Wave 3 hardening pass; DEC-801). | W2-59 run 3's review, R2-F1, 2026-10-20 (DEC-879; ordinary work: no; other: the pin's guard still decided) |
| W2-L387 | `gov --version` run from a source tree on a machine with no git on `PATH` ends in a traceback | engineer | It prints the version with "(commit unknown)" (the Wave 3 hardening pass). | W2-59 run 3's review, R2-F3, 2026-10-20 (DEC-879; ordinary work: no; other) |
| W2-L388 | W2-59's CIT-P at its head says P-W2-59-5 to -7 are open and its review residuals proposed, lacks DEC-412 and DEC-877 in `decisions_carried`, and §1 says `70cfbcf9` corrects `e48a601d` (it corrects the old `3eadca4c`) | product-spec | Corrected by whoever next edits the CIT-P; until then the probe record `docs/probes/DAEO-kh9l/PR-DAEO-kh9l.md` states it (DEC-413: nothing follows the probed head). | W2-59 run 3's review, R2-F2, 2026-10-20 (DEC-879; ordinary work: yes; other) |
| W2-L390 | core-schema skips the top-level keywords it cannot read on a standalone record schema | engineer | The full validator reads every keyword (W2-64, check-jsonschema). | W2-02 run 5's probe, R1, 2026-10-21 (ordinary work: no; other) |
| W2-L391 | An adoption verdict passes core-schema when `common.schema.json` is missing | engineer | A missing shared schema is a named failure (the Wave 3 hardening pass). | W2-02 run 5's probe, R2, 2026-10-21 (ordinary work: no; other) |
| W2-L392 | An adoption verdict with an empty conditions list is valid | engineer | The verdict's KPIs decide whether a conditional verdict needs at least one condition (W2-52, W2-28). | W2-02 run 5's probe, R3, 2026-10-21 (other) |
| W2-L393 | The shared fields and the `close` type are checked for presence only, not for their form | engineer | The full validator checks their form (W2-64). | W2-02 run 5's probe, R4, 2026-10-21 (other) |
| W2-L394 | The record schemas' patterns accept a trailing newline | engineer | Patterns anchor at the true end of the value (the Wave 3 hardening pass). | W2-02 run 5's probe, R5, 2026-10-21 (ordinary work: no; other) |
| W2-L395 | `src/gov/context/__init__.py` keeps a second `wbs_id` grammar without DEC-730's suffix | engineer | One grammar for `wbs_id`, DEC-730's (the owner of `src/gov/context/`, W2-04). | W2-02 run 5's probe, R6, 2026-10-21 (other) |
| W2-L396 | With every mapped type now "unmeasured, not green" when unknown, a project whose installed kernel is older than its `gov` package fails closed at a close that touches governance files, until `copier update` | product-spec | The adoption and upgrade guide says so, and `gov doctor` names the kernel's age (W2-18). | W2-02 run 5's probe, R7, 2026-10-21 (ordinary work: yes; other: fails closed, KPI line 3's intent) |
| W2-L397 | An engineer can read the earlier tickets' acceptance cases that its own branch's test designer rewrote, because Policy 2 (c) covers only the ticket's own test folder | engineer | (c) covers every acceptance file the ticket's test designer changed, wherever it lies (W2-58's follow-up or the Wave 3 hardening pass). | W2-58 run 2's residuals, 2026-10-21 (ordinary work: yes; other) |
| W2-L398 | Plain `git diff` and `git show` are refused to the engineer under (c), though most of their output is the engineer's own work | engineer | The engineer's `git diff` and `git show` are allowed where they show none of the ticket's acceptance files (the Wave 3 hardening pass). | W2-58 run 2's residuals, 2026-10-21 (ordinary work: yes; other: fails closed) |
| W2-L399 | Forms W2-58's read rules do not cover: saved session transcripts, a repository without `w2/integrate`, a ticket without `wbs_id`, `uv run pytest`, `git cat-file` from a subfolder, a `tar` pipe, a `cd` to a glob, unresolvable shell variables | engineer | Each form is judged or refused with a reason (the Wave 3 hardening pass). | W2-58 run 2's residuals, 2026-10-21 (ordinary work: mostly no; other) |
| W2-L400 | The test designer's refusal (c) covers the branch's committed changes only, not an engineer's uncommitted edits in the same tree | engineer | (c) also covers the working tree's changes, or the rule "never two writing sessions in one tree" is checked (the Wave 3 hardening pass). | W2-58 run 2's residuals, 2026-10-21 (ordinary work: no, one writer per tree; other) |
| W2-L401 | A Write to `~<user>/…` that the guard allows (it expands `~<user>`) lands under a literal `~<user>` folder in the working folder, since the file tools expand only `~/` | engineer | The guard judges a `~<user>` path as the tool will write it (the Wave 3 hardening pass). | W2-58 run 3's review, finding 1, 2026-10-21 (DEC-882; ordinary work: no; fails open, narrowly) |
| W2-L402 | `coverage run --data-file=<a test file>` overwrites a test; containment restores it | engineer | The data file's target is judged as a write (the Wave 3 hardening pass). | W2-58 run 3's review, finding 2, 2026-10-21 (DEC-882; ordinary work: no; other) |
| W2-L403 | `coverage html` and `coverage annotate -d` write copies of the tests' source that the guard does not protect from the engineer | engineer | Coverage's report outputs are refused or protected for a ticket's own tests (the Wave 3 hardening pass). | W2-58 run 3's review, finding 3, 2026-10-21 (DEC-882; ordinary work: no; fails open; the route predates the round) |
| W2-L404 | Spaces around a file tool's path get past refusals (a) to (d): the tools trim them, the guard does not | engineer | The guard trims a path as the tools do (the Wave 3 hardening pass). | W2-58 run 3's review, finding 6, 2026-10-21 (DEC-882; ordinary work: no; fails open) |
| W2-L405 | A `pytest --trace` run fed debugger commands lists a test's source to the engineer | engineer | Debugger options are refused to the engineer on its own tests (the Wave 3 hardening pass). | W2-58 run 3's review, finding 7, 2026-10-21 (DEC-882; ordinary work: no; fails open) |
| W2-L406 | `coverage3 run -m pytest` and `python3 -P -m pytest` are still refused to the engineer | engineer | Allowed as the other pytest forms are, in the next guard ticket (DEC-802). | W2-58 run 3's review, finding 4, 2026-10-21 (DEC-882; ordinary work: yes; other: fails closed) |
| W2-L407 | Every coverage run leaves a containment note for `.coverage`, which is not git-ignored | engineer | `.coverage` is git-ignored, or containment knows it (the next guard ticket, DEC-802). | W2-58 run 3's review, finding 5, 2026-10-21 (DEC-882; ordinary work: yes; other) |
| W2-L408 | W2-58's live cases leave a run folder `~/gov-os-runs/W2-95` behind | independent-test-designer | The live cases remove the run folder they make (the Wave 3 test-hygiene pass). | W2-58 run 3, 2026-10-21 (DEC-882; other) |
| W2-L409 | W1-07's `test_every_command_returns_the_envelope[doctor]` was red in W2-02's close's parallel regression (2026-10-21) and green alone on the same tree at load 5; the close keeps no failure text, so the cause is not measured | engineer | The cause is measured (load, timing or the environment) and the case holds inside the full regression, or it runs in the close's isolated part with a named reason (W2-57; lens H's flaky-test findings). | W2-02's refused close, 2026-10-21 (DEC-885; ordinary work: yes; other: fails closed) |
| W2-L411 | A close records no gate on the coverage of the lines a ticket changed | engineer | diff-cover (Apache-2.0), given the child-process coverage of the nightly's measured map, reports the changed lines' coverage in the close record as a signal (Wave 3). | lens H B2, 2026-10-21 (DEC-889 item 12) |
| W2-L412 | CI runs no tests (W2-43 keeps CI's tests red by design until the hooks are back), and no sharding exists for CI | engineer | pytest-split (MIT) shards CI's run by recorded durations once CI runs tests (Wave 3, after W2-43). | lens H B2, 2026-10-21 (DEC-889 item 12) |
| W2-L413 | Pants (Apache-2.0) is not adopted: a whole build system, static, and blind to the tests' `gov` command-line calls | engineer | Revisited for UPIM and ASMO, where its affected-targets selection may fit (Wave 3). | lens H B2, 2026-10-21 (DEC-889 items 12 and 17 b) |
| W2-L410 | The guard cannot confine writes into the record worktree (`~/gov-os-worktrees/W2-00-record/`, branch `record/w2`) to the main orchestrator of W2-00: it refuses every role's tool writes there, but git and the sync script are not judged, so a lead's own opaque program could write there, stopped only by its brief | engineer | A guard rule allows writes there only to a session with role `orchestrator` and ticket W2-00, by tool and by the known commands (the Wave 3 hardening pass). | P-REC-2 (b), 2026-10-21 (DEC-888 item 2; ordinary work: no, a deliberate construction, DEC-801; other) |
| W2-L414 | W1-46's live research-allowlist cases fail when a starting host is unreachable (`static.crates.io`, W2-63's close, 2026-10-22 00:11: failed in the run and alone, passed alone between 00:12 and 00:16), and a close is spent on a network fault | engineer | The queue's pre-close check confirms the allowlisted hosts first and holds the queue while one is unreachable (DEC-892, done in the orchestrator's queue); the live cases move to the nightly's live layer (DEC-889 item 2; W2-57). | P-W2-63-C1 (3) (a), 2026-10-22 (DEC-892; ordinary work: yes; other: fails closed) |
| W2-L415 | Two W1-38 rulesync cases, `TestGenerateCheck::test_check_clean_after_generate` and `TestRegisteredFamilyCheck::test_gov_check_lists_the_check_under_the_family`, errored under load in W2-50's run 9 (`rulesync generate` timed out at 30 s) and passed alone; they are not on `load_sensitive`, so a close under load would count them red | engineer | The probe's limits meet a loaded machine (W2-57's first item, DEC-892 item 2), and the two cases pass in three closes' worth of parallel runs. | W2-50's run 9, 2026-10-22 (DEC-902; ordinary work: yes; other: fails closed) |
| W2-L416 | In W1-30's fixture, repeated closes pass without a fresh checkpoint after the close's own repair-ticket commit (a refused close now commits its repair ticket, W2-07's KPI 8), so the checkpoint gate does not see the commit it made | engineer | A close after a repair-ticket commit needs a checkpoint newer than that commit, or the gate names it (W2-24; W2-07's run 3 found it outside its paths: the watchdog's rule lives in `gov.checkpoint`). | W2-07's run 2, 2026-10-23 (DEC-908; ordinary work: yes; other: a fresh-checkpoint rule not applied after the close's own commit) |
| W2-L417 | After W2-70 (`efdc4188`), three acceptance READMEs and one docstring are stale: `tests/acceptance/W1-30/README.md` (line 1204) and `tests/acceptance/W2-58/EARLIER_CASES.md` (lines 114, 158) still name the retired switch-over case; `tests/acceptance/W1-01/README.md` lacks DEC-906's and DEC-908's exact-commit rule; the history case's docstring still says "expected red until the entry is committed" | independent-test-designer | The three files and the docstring match DEC-899, DEC-906 and DEC-908, in the next test-designer round that holds those folders (W2-67 for W1-30; a W1-01 or W2-58 revision otherwise). | W2-70's return, 2026-10-23 (ordinary work: yes; other: stale text, no behaviour) |
| W2-L418 | `tests/acceptance/W1-50/test_w1_50_move_of_very_many_merge_commits.py::test_a_move_of_very_many_merge_commits_with_24_parents_that_undoes_a_test_is_a_finding_within_the_hook_s_limit[orchestrator-trailers-dropped-near-the-newest]` timed out at its 30-second limit under load in W2-70's first verification run and passed in the second; it is not on `load_sensitive` | engineer | Its limit meets a loaded machine, or it runs alone (W2-57's serial rework). | W2-70's return, 2026-10-23 (ordinary work: yes; other: fails closed) |
| W2-L419 | The secrets check and the pre-index filter give gitleaks each BEGIN…END key block whole only up to 24 KiB, because gitleaks reads at most 25,000 bytes ahead, and the bound applies after encoding and after the form feeds: a key block over 24 KiB can be missed where a piece edge cuts it; a key export wrapped as one word over 24,000 bytes (base64 once from a block of about 18 KB, base64 twice or hex from about 12 to 14 KB; gitleaks decodes each by default) is missed at every placement, even as a standalone file, where the code before W2-69 found it standalone; a 24,576-byte block with a blank line after every line passes the whole-piece bound and is missed (W2-69's third review, findings 1 and 2) | engineer | A key block or encoded key export of any length is found, for example by a stream reader that does not cut a block. For a key export wrapped as one word over 24,000 bytes the check is narrower than the code before W2-69, so the reader is due in Wave 3 (its hardening pass) and does not slip past it (DEC-911 item 6). | DEC-909; widened by DEC-910 (R3-A), 2026-10-24 (W2-69's third review: ordinary work: no; consequence: fails open) (W2-69's part closed by its close, `07a8d624`, 2026-10-27; the rest stays open: a key export wrapped as one word over 24,000 bytes, due in Wave 3, DEC-911 item 6) |
| W2-L420 | After W2-07 (`2a9d1a11`), W1-30's `test_w1_30_context_failures.py::test_a_decision_checker_that_cannot_run_refuses_the_close` still asserts a counted refusal (DEC-455, changed by DEC-868 item 3 and DEC-908), and the module docstrings of `test_w1_30_governance_checks.py` and `test_w1_30_context_failures.py` still describe DEC-480's and DEC-455's old rules | independent-test-designer | The case and the two docstrings follow DEC-868 and DEC-908, in W2-67's round 2 (it holds W1-30). | W2-07's run 3 return, 2026-10-24 (DEC-866; ordinary work: yes; other: a superseded rule still asserted) |
| W2-L421 | W2-67's round 1 review (`docs/probes/DAEO-9nys/PR-DAEO-9nys.md`) left three findings an honest agent does not meet in ordinary work: R1 and F5 (lose work: a killed run's folder judged by pid across namespaces in rare forms) and F4 (fails open: an f-string `--basetemp=` passes the static guard) | engineer | Wave 3's hardening pass (DEC-801); F4's guard rides W2-67's round 2 if small (P-W2-67-TD4-A). | W2-67's round 1, 2026-10-24 (ordinary work: no; consequence: loses work / fails open) |
| W2-L422 | A file under `.gov-runtime/` that vanishes between the secrets check's walk and its read makes the check raise (fails closed; pre-existing in the base) | engineer | A file gone before its read is skipped and named, never judged clean (W2-45). | W2-69's third review, 2026-10-24 (ordinary work: yes; other: fails closed) |
| W2-L423 | One of gitleaks' default rules flags a full 40-hex commit hash written beside a vendor keyword, so a lead's or reviewer's log under `.gov-runtime/scratch/` that quotes full hashes can turn `gov check`'s secrets-indexing RED by chance (W2-69's run 2 met it on three of its own scratch records) | engineer | In force (DEC-911): 12-digit hashes and none of the rule's keywords under `.gov-runtime/`, a paths-only early warning in the record checks and the close queue, gate (b) failing closed as the backstop; W2-71 exempts only that rule's exact 40-hex matches naming a real commit of this repository, in the second re-pin. | W2-69's run 2, 2026-10-24 (ordinary work: yes; other: fails closed) |
| W2-L424 | Many BEGIN markers in one input cost the secrets check one extra piece each (W2-69's fourth scan form) | engineer | The cost is measured and bounded (Wave 3). | W2-69's third review, 2026-10-24 (ordinary work: no; other) |
| W2-L425 | W2-69's recorded residuals: review 1's F2 (a store locked past the 10 s wait judged by raw bytes), F4 (gitleaks skips an input as binary at a file signature at offset 128 or 257), F5 (WAL and auto_vacuum layouts, an entry criterion), F7 (a freed overflow page on an uncompacted store), F8 (neighbouring values interacting; W2-45 keeps the rest of W2-M395); review 2's F2 (a damaged FTS5 leaf read as no terms) and F3 (an fts5vocab table blocks compaction, an entry criterion); the designers' (a key block spread over several stored values; freed-space forms) | engineer | Each in W2-45 or the Wave 3 hardening pass, as its classification says (DEC-801, DEC-803). | W2-69's reviews, 2026-10-23 and 2026-10-24 (classifications in `docs/probes/DAEO-rmbe/PR-DAEO-rmbe.md`) |
| W2-L426 | `tests/acceptance/W1-01/README.md` does not describe the history rules W1-01 now enforces: the exact-commit exemption list (DEC-906, DEC-908) and the merge whose acceptance files equal git's own merge of its parents (DEC-912) | independent-test-designer | The README states each rule with its decision, by a test designer (DEC-906 item 1), in W1-01's next revision. | W2-70's round 2, 2026-10-24 (ordinary work: yes; other) |
| W2-L427 | W1-29's SubagentStop "once" (a second stop with `stop_hook_active`) is untested: its only reading would let a helper end without the twelve fields (CAP-37.d), and no source decides it | owner | A decision on the second stop, then one case (W2-65's evidence). | W2-65's run 1, 2026-10-24 (ordinary work: no; other) |
| W2-L428 | `tests/acceptance/W1-38/w1_38_hooks_support.py` reads SubagentStop's undocumented stdout record, which DEC-889 item 8 (P-H-7) replaces with the reason on standard error; the hook keeps the record only for it (DEC-866) | independent-test-designer | W1-38's support reads standard error, then the record is dropped (W1-38's next revision, DEC-906 item 1). | W2-65's run 1, 2026-10-24 (ordinary work: yes; other) |
| W2-L429 | W2-54's `test_gov_check_gives_context_reproducibility_green_here` timed out at 600 s in W2-65's parallel run and passed alone (250 s); it is not on `load_sensitive` | engineer | The case reads the close's check result instead of running `gov check` itself (P-W2-66-a), or the owner places it (W2-57). | W2-65's run 1, 2026-10-24 (ordinary work: yes; other: fails closed) |
| W2-L430 | A renamed helper imported inside a function is not followed by the scoped close's selection (R1) | engineer | The selection follows function-level imports, or widens on them (Wave 3). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open) |
| W2-L431 | `pyproject.toml` is placed by W1-07's suites alone, though W2-59 now holds it (R2) | engineer | Every suite that reads it is coupled to it (W2-68's map upkeep). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open) |
| W2-L432 | The nightly's bisect names the range's first commit when the red test is new (R3, F7) | engineer | A new test's red is reported as new, not bisected (the nightly's next change). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: yes; other) |
| W2-L433 | An unreadable `--check-result` delays a counted refusal by one run (R4) | engineer | An unreadable result is a refusal at once (W2-07). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: yes; other) |
| W2-L434 | The test map's upkeep: a folder target still resolves after its record-reading file moved away (R5); the map's literal paths are not checked at the head (R6); an inherited, guarded or aliased case is judged gone, so the close runs in full (R9, the safe side); who corrects the map when a target is retired or renamed | engineer | W2-68 takes the map's upkeep and checks every target and literal path at the head; until then a close widens (P1, DEC-912) and the orchestrator corrects the map by a record edit. | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open (R9: yes; other)) |
| W2-L435 | Fixture inputs that no coupling takes to their readers: scanner configurations (W1-40, W2-50, W2-69), the template path map (W2-50, W2-58, W2-69), the check declaration (W2-69) (R7) | engineer | Each is coupled to its readers (W2-68). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no; fails open) |
| W2-L436 | W2-54's record-reading case runs `gov check` itself (611 of a scoped close's 617 s) instead of reading the close's check result (P-W2-66-a); the check result is taken as given, which fails open once a test reads it (feature-gated, DEC-803) | engineer | The case reads `GOV_CLOSE_CHECK_RESULT` and the close passes its own result (W2-54); the ticket that adds a reader verifies the result (its entry criterion). | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: no exit criterion; other) |
| W2-L438 | A lifecycle hook program (SessionStart, Stop, PreCompact, SubagentStop) that cannot run exits with its own code, which Claude Code ignores, so SubagentStop's twelve-field check fails open for that helper (CAP-37.d); mapping it to exit 2 as the guard lines do would make Stop and SubagentStop loop | engineer | A design per event (for example exit 2 on SubagentStop only while `stop_hook_active` is false), with the owner's decision, since it touches the hooks (Wave 3 or W2-45). | W2-65's run 2, 2026-10-24 (DEC-917; ordinary work: no; fails open) |
| W2-L439 | W2-59's lexical canary can pass on its own committed declaration (`governance/kernel/canaries/lexical.yaml` holds the canary's query) once that file is indexed, even if no project content was | engineer | The canary's query is kept out of the index it measures, or the canary checks a hit outside its declaration (the canary runner's next change). | W2-65's run 2, 2026-10-24 (ordinary work: yes; other: a weak measurement) |
| W2-L440 | W2-66's `test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes` diffs `w2/integrate...HEAD`, so it is red on any ticket branch that changes a plain run's configuration or a conftest (W2-59's, W2-67's), though it states a property of W2-66's own change | independent-test-designer | The case judges W2-66's own commits (by Task trailer) or the close's own change, `Rewrite-Reason: DEC-919` (W2-68's test designer). | W2-65's run 3, 2026-10-24 (DEC-919; ordinary work: yes; other: a false red, fails closed) |
| W2-L441 | `tests/acceptance/W1-38/README.md` (lines about the hook command lines) and possibly `tests/acceptance/W2-59/README.md` still describe DEC-608's single form, which DEC-917 split in two | independent-test-designer | Each README states the two forms by line (the next test designer of each folder, DEC-906 item 1). | W2-65's run 3, 2026-10-24 (ordinary work: yes; other) |
| W2-L442 | Whether DEC-868 wants a decision checker that cannot run refused uncounted at the pre-close gate, rather than as the close's counted finding at the context step (W2-L420's case, P-W2-67-TD6-1 (a)) | engineer | The pre-close gate refuses it uncounted, if the owner reads DEC-868 so; W1-30's case follows. | W2-67's run 3, 2026-10-25 (DEC-920; ordinary work: yes; other) |
| W2-L443 | core-authority is GREEN when W1-11's decision checker cannot run (as in a shallow clone) | engineer | A checker that cannot run makes the check not measured, never GREEN (the check's owner). | W2-67's run 3, 2026-10-25 (DEC-920; ordinary work: no; fails open) |
| W2-L444 | W2-50's large-store and hang cases declare their short limit through two private names of the secrets check (`_TIMEOUT_S`, `_LARGE`) (P-W2-67-TD7-A) | engineer | The check takes a public declared limit when it is next opened (W2-45 or W2-71). | W2-67's run 3, 2026-10-25 (DEC-920; ordinary work: yes; other) |
| W2-L445 | `tests/acceptance/W1-07/test_w1_07_config_details.py`'s rebuild case still leaves a code-graph daemon folder (P-W2-67-TD8-A) | independent-test-designer | W1-07's fixture removes the folders of the projects it built (W1-07's next test designer). | W2-67's run 3, 2026-10-25 (DEC-920; ordinary work: yes; other) |
| W2-L446 | The 180 s bound on the 13 nested-run unit close functions is not yet measured under worksteal beside the whole regression (W2-67 KPI 2's second half) | engineer | The nightly measures it once worksteal is on (DEC-892 a). | W2-67's run 3, 2026-10-25 (DEC-920; ordinary work: yes; other) |
| W2-L447 | The root conftest's static `--basetemp` guard (W2-67 KPI 4) misses forms outside list and tuple literals: `cmd.append(f"--basetemp=…")`, the option appended alone, `PYTEST_ADDOPTS` in the environment, a shell string, or the option built with `+`, `.format` or `%`; the runtime refusal still stops them (widens round 1's F3) | engineer | The guard reads every string that reaches a pytest argument list or `PYTEST_ADDOPTS` (Wave 3). | W2-67's run 4 review, 2026-10-25 (ordinary work: yes; other) |
| W2-L448 | W2-67's td-7 changed `tests/acceptance/W2-50/w2_50_scan_support.py` and `README.md` and added `README-W2-67.md`; the ticket file names only `test_w2_50_secrets_scan_scale.py` there, while its card says `W2-50/**`, and the test-designer role may write all of `tests/acceptance/**`, so only review holds a ticket to its named files | orchestrator | The card's `W2-50/**` is read as the scope (its ticket file is not edited after its probe, DEC-581); the guard checks a test designer's writes against the files the ticket names (W2-45 or Wave 3). | W2-67's run 4 review, 2026-10-25 (F-B; ordinary work: yes; other) |
| W2-L449 | Run without `PYTHONPATH`, the pin's interpreter loads the pinned wheel's `gov`, not the project's `src/`: a lone `pytest tests/unit/close/test_serial.py` fails to import `gov.close.serial` (new in W2-57). Every run the close starts sets `PYTHONPATH` to `src/`, so a narrow scoped selection passes (W2-57's unit test 11 of 11, `tests/unit/close` 428 of 428, 2026-10-28) | engineer | A unit test run outside the close imports the project's own code, or says that it runs the pin's (for example the root conftest putting `src/` first). | The orchestrator, 2026-10-28 (DEC-932 item 2; ordinary work: no; other: fails closed) |
| W2-L389 | The launcher's own-ticket rule refuses a product-spec worker on a ticket whose role is engineer, so brief A4 on a code ticket can only be given to an engineer | orchestrator | Briefs name the ticket's own role for record edits on code tickets, or the launcher admits product-spec for documentation paths (W2-56 or W2-11). | W2-59 run 3's lead, 2026-10-20 (DEC-879; ordinary work: yes; other: fails closed) |
| W2-L381 | W1-22's lexical canary hits its own declaration files in the adopted layout, so it proves only that the index is searchable | independent-test-designer | The canary's expected hit lies outside its declaration files (the Wave 3 test-hygiene pass). | W2-59 run 2's test designer td-2, 2026-10-20 (DEC-877) |
| W2-L371 | An installed `gov` wheel prints `(commit unknown)` from `gov --version` | engineer | A release records its commit in the wheel, as W2-16 and W2-18 decide (W2-16, W2-18). | W2-59 run 1, P-W2-59-2 (c), 2026-10-20 (DEC-864) |

### 3.4 info (41)

| ID | Item | Owner | Closes when | Sources |
|---|---|---|---|---|
| W2-I001 | Sandbox cost and whether its tokens count toward the governance share | owner | Owner decision on counting, based on measured figures in W1-31 | B:180 (DEC-170) |
| W2-I002 | Path-map capability values for this repository are the implementer's | owner | Owner confirms the capability values | B:395 (DEC-251, DEC-265) |
| W2-I003 | fixtures/** is the only product namespace | owner | Owner confirms the product namespace scope | B:402 |
| W2-I004 | stores_with_secrets second scan stricter than DEC-347 | owner | Confirmed as intended | B:947 (DEC-347) |
| W2-I005 | Lesson severities and lifecycles chosen by the worker | owner | The owner reviews them, or the decision stands. | B:1261 (DEC-433) |
| W2-I006 | Whether acceptance tests should be embedded (adapters, repository, tests took 'not embedded' by the lead's reading) | owner | The owner rules on the embedded value of the tests namespace, and the template's path map says it. | X (runs 6, 7) (DEC-693) |
| W2-I007 | Held-out rule exceeds 100 ms budget at about ten thousand paths | engineer | Accepted, or the rule is indexed to stay in budget | B:287 (DEC-149) |
| W2-I008 | CAP-24 version for vendored skills read from vendored.yaml | engineer | gov close reads vendored versions from vendored.yaml | B:384 (DEC-262) |
| W2-I009 | Store load replaces only its own five tables | engineer | Confirmed as intended | B:471 |
| W2-I010 | Root gitleaks allowlist reconstructed by the lead | engineer | Allowlist re-verified by a gitleaks run | B:512 |
| W2-I011 | Experiments root fixed as experiments/ | engineer | Project key added when needed | B:742 (DEC-333) |
| W2-I012 | Sandbox placeholder dotfiles and docs/source show as untracked in worktrees | engineer | Sandbox placeholders no longer appear in worktree status, or are ignored by every check | B:2124 (DEC-253, DEC-255, DEC-693, DEC-697) |
| W2-I013 | Unexplained single failure of the collect-only unit case | engineer | Cause found, or no recurrence over a defined window | B:2238 |
| W2-I014 | gov adopt without --lite is NOT_IMPLEMENTED | engineer | Full gov adopt is implemented | B:2397 |
| W2-I015 | Reason order for an unknown tool meeting older rules | engineer | None needed unless revisited | B:2744 (DEC-685) |
| W2-I016 | A3's embedding check answers before its --map check | engineer | The --map check runs first | B:2773 (DEC-694) |
| W2-I017 | Independent adoption gates A7, A10, A11 and the final verdict (Wave 3) | engineer | A7, A10 and A11 run, and an adoption verdict is issued. | R:832 (DEC-090) |
| W2-I018 | Upstream lesson loop, lite form (Wave 3) | engineer | A framework lesson reaches the inbox, is triaged, and gov doctor reports pending updates. | R:1514 (DEC-165, DEC-168) |
| W2-I019 | Full claims and concurrency, the claims role and gov claim (CAP-23.b, Wave 3) | engineer | gov claim exists, and CAP-23.b's check passes. | R:2253 (DEC-235, DEC-291) |
| W2-I020 | G-22 text exists only in archived sources | product-spec | G-22 available in-tree or recorded as superseded | B:441 (DEC-260, DEC-257) |
| W2-I021 | Kernel templates/openspec/ folder holds nothing | product-spec | Folder removed or given a purpose | B:600 (DEC-304, DEC-326) |
| W2-I022 | Unpinned pause error codes and flag mode | product-spec | They are pinned in a decision or the spec. | B:1193 (DEC-412) |
| W2-I023 | Lessons are HISTORICAL records, not authority | product-spec | Ticket templates make this citation rule explicit. | B:1259 |
| W2-I024 | Full research lifecycle CAP-32 (Wave 3) | product-spec | CAP-32's acceptance check passes. | R:1501 (DEC-163) |
| W2-I025 | Wave 3 role roster | product-spec | Kernel role files for these roles exist. | R:454 (DEC-066) |
| W2-I026 | W1-20 suite takes about four and a half minutes | independent-test-designer | The suite's run time is reduced or accepted by decision. | B:1040 |
| W2-I027 | One case holds both hit@5 KPI lines | independent-test-designer | The KPI lines are deduplicated, or the case split is accepted. | B:1054 (DEC-414) |
| W2-I028 | Six of 18 cases are pins and the round 4 README is outdated | independent-test-designer | README corrected | B:2671 |
| W2-I029 | A single-file adapter-source copy helper counts as exercised | independent-test-designer | Revisited if the coverage looks too weak | B:2720 (DEC-675) |
| W2-I030 | Before-snapshot adds about 28 ms to every Bash PreToolUse | research | Measured overhead is accepted at Wave 2 or reduced | B:70 (DEC-134, DEC-149) |
| W2-I031 | Untracked placeholder files at worktree root during sessions | research | Explained and accounted for in containment/status | B:916 |
| W2-I032 | Approval rule judged nothing on this repository | research | The rule judges a real owner approval in this repository. | B:1112 |
| W2-I033 | Not probed: other parallel plugin versions, huge worker counts, nested close | research | A probe covers each shape | B:2241 |
| W2-I034 | Harness identity rests on log form and ccusage only | research | An independent identity signal is recorded | B:2706 |
| W2-I035 | Not probed: real session log, real 2.1.296 log, gov close end to end | research | A probe measures real logs through gov close | B:2707 (DEC-655) |
| W2-I036 | Not probed: launcher rules binding subagents and sandbox; research launch | research | A live probe confirms both | B:2721 |
| W2-I037 | Not probed: real MultiEdit, real subagent start, real skill inline shell | research | A live probe covers each | B:2746 (DEC-685) |
| W2-I038 | Local gpt-oss T1 model, deferred to Wave 3 model routing | research | Model routing decides the local model. | R:754 (DEC-083) |
| W2-I039 | Wave 1 tickets built by unsandboxed workers | orchestrator | Mid-wave or exit audit weighs the unsandboxed work | B:667 (DEC-183, DEC-371) |
| W2-I040 | Systematic size overruns against ticket estimates | orchestrator | Estimation method reviewed at the Wave 1 exit | B:744 (DEC-343) |
| W2-I041 | The harness refuses edits of a clone's local exclude file and git init inside its git folder; the bare remote stands under target/ | orchestrator | The exit-run brief places the bare remote outside the clone's git folder from the start. | X (run 6) (DEC-687) |

## 4. Closed or superseded in the record

These rows are kept so that a reader of the sources sees where each item went.

| ID | Item | Closed by | Sources |
|---|---|---|---|
| W2-C001 | Path-map systems snapshot needs updating as tickets land | L413/L741 (updated at W1-33 close; ongoing upkeep) | B:413 |
| W2-C002 | Per-session temp directory left behind after session ends | L980 (W1-28; remaining kill cases at L983) | B:686 (DEC-386) |
| W2-C003 | gov launch has no product-spec role | L981 (W1-28 launches product-spec sandboxed) | B:880 (DEC-371, DEC-183) |
| W2-C004 | Copying test fixtures duplicated held-out.yaml into temp projects | L991 (W1-28, narrow exclusion) | B:902 (DEC-385) |
| W2-C005 | Worker cannot delete its own scratchpad | L989 (W1-28, scratchpad gone at session end) | B:910 |
| W2-C006 | Opaque commands can remove or forge the freeze flag (MWA-01) | L1376 freeze mirror (DEC-429, DEC-437); an opaque write by the unsandboxed orchestrator session remains an accepted residual | B:1170 (DEC-429, DEC-437) |
| W2-C007 | Suite helper accepts the whole-file hash as a citation sha256 | L1278 the W1-22 validator checks the span hash only (DEC-435); the W1-21 suite helper itself is unchanged | B:1205 (DEC-435) |
| W2-C008 | MWA-02: acceptance tests added after implementation are systematic | DEC-430 (owner: this is how MR-3 is met; the exit auditor is told so) | B:1233 (DEC-136, DEC-430) |
| W2-C009 | Stop and SubagentStop hooks not registered; installer may need them | DEC-442 (registered at the Wave 1 exit run, L1497) | B:1425 (DEC-442) |
| W2-C010 | Auto-compact threshold not set | L1493 (DEC-451, already set via CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000) | B:1432 (DEC-208, DEC-451) |
| W2-C011 | Hook checkpoints written as untracked files under docs/checkpoints | L1583 (DEC-444, moved to .gov-runtime/scratch/checkpoints/) | B:1436 (DEC-444) |
| W2-C012 | Path compliance reports 180 stale paths; historical exclusion counted zero | L1704 (DEC-456, 0 moved references, 179 historical excluded; plan validator path fixed in 4eb9aacd) | B:1669 (DEC-456) |
| W2-C013 | Close measured an uncommitted tree as its HEAD | L1847 follow-up measures the commit and not the tree (ignored-file residual remains, L1871) | B:1777 (DEC-466) |
| W2-C014 | gov close does not call the governance-share counter | L2460 (W1-30 follow-up after W1-41: gov close calls the cost counter) | B:2017 (DEC-495) |
| W2-C015 | Counter accepts only Claude Code 2.1.288 logs | L2696 W1-31 round (DEC-655) accepts any version it can parse | B:2026 (DEC-655) |
| W2-C016 | Natural-language half of CAP-28.a: route status questions to gov status | L2150 (W1-35 orchestration skill states the route; still text only, see L2156) | B:2085 (DEC-526) |
| W2-C017 | Ticket listed ready when its constraining package fails to load | L2460 (READY rule holds such a ticket, DEC-544) | B:2093 (DEC-544) |
| W2-C018 | gov close cannot open its repair ticket: argument list too long | L2490 (repair ticket DAEO-fknh opened by a refused close; cut residual at L2471) | B:2138 (DEC-521) |
| W2-C019 | Adapter-portability shows two more findings until the owner applies the generated output | L2679 (adapter-portability GREEN at 76ce6416) | B:2160 (DEC-481, DEC-550) |
| W2-C020 | Declared-case run ending exit 0 with no result is accepted | L2471 (built; residual: a printed line can satisfy the stated-result check) | B:2205 (DEC-555) |
| W2-C021 | Project file named like the close plugin replaces it | L2471 (stand-in check built; covers the root and src/ only) | B:2208 (DEC-555) |
| W2-C022 | Parallel workers outlive a run cut at the time limit | L2484 (case test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it exists; inferred) | B:2210 (DEC-555) |
| W2-C023 | 200 KB command costs about 8 s in the read rule | L2413 (commands over 32,768 characters refused) | B:2312 (DEC-557) |
| W2-C024 | Project with neither protected file refuses no root search (P-27) | L2432 DEC-573 (root search refused only where a protected file lies under the start) | B:2426 (DEC-573) |
| W2-C025 | Long path-like string makes held-out check take 40 s or more (P-28) | L2432 (DEC-574: strings over the path limit not resolved, decided in a millisecond) | B:2426 (DEC-574) |
| W2-C026 | 60 s hook limit and failed-tool-call entry missing from template's rulesync hooks source | L2492 (W1-15 round; commit 7112564a at L2633) | B:2466 (DEC-580, DEC-596) |
| W2-C027 | secrets-indexing check times out at 60 s | L2513 (W1-15 round: 179 s inside a 900 s limit) | B:2473 (DEC-591, DEC-595) |
| W2-C028 | PYTHONPATH prefix in hooks source lets a product package named gov silence containment | L2520 (second run: no PYTHONPATH prefix; residual at L2523) | B:2502 (DEC-603) |
| W2-C029 | Relative hook command lines exit 2 from a subfolder | L2518 (W1-15 second run; measured on a clone at L2539) | B:2503 (DEC-603, DEC-608) |
| W2-C030 | secrets-indexing found canary strings in three scratch files | L2541 (moved; DEC-604 rule) | B:2513 (DEC-602, DEC-604) |
| W2-C031 | human_gate has no check and stays red in every project | L2649 (core-authority declares human_gate; residual at L2651) | B:2557 (DEC-613, DEC-627) |
| W2-C032 | Generated orchestration SKILL.md differs until the owner applies the output | L2679 (adapter-portability GREEN) | B:2566 (DEC-616) |
| W2-C033 | context-reproducibility takes the kernel template ticket PROJ-0000 as a project ticket | L2649 (P-43 round: measures the store's records of the ticket folder) | B:2575 (DEC-623) |
| W2-C034 | A5 record names the verdict's old path after the move | DEC-718 (adoption records keep their pinned hashes; the doctor stops judging citations inside them) | B:2645 (DEC-626) |
| W2-C035 | Hooks source alone does not clear adapter check (44 files) | L2679 (adapter-portability GREEN) | B:2658 (DEC-635, DEC-636, DEC-641) |
| W2-C036 | Guard does not know MultiEdit and allows it for every role | L2735 (W1-02 round DEC-685) | B:2715 (DEC-685) |
| W2-C037 | Product package named gov silences containment via PYTHONPATH prefix | DEC-608 removed the prefix (guard, containment, stop only; see next item) | R:6435 (DEC-601, DEC-608) |
| W2-C038 | No consolidated Wave 2 list with a severity per item | this file, committed with DEC-718 | A F-M8 (DEC-718) |
| W2-C039 | Charter, Contract and WBS carry status PROPOSED | DEC-718 item 9, the owner's commit | A F-m9 (DEC-718) |
| W2-C040 | The semantic canary misses (FACET_UNAVAILABLE) | full rebuild of 2026-10-16 (DEC-718 item 4) | A F-M2 (DEC-709, DEC-718) |
| W2-C041 | Outward actions after 2026-10-07 unrecorded | DEC-718 item 5 | A F-M9 (DEC-465, DEC-718) |
| W2-C042 | FULL tickets W1-16 and W1-21 (and three follow-ups of 2026-10-07) have no probe record | accepted as named exceptions, DEC-718 item 7 | A F-M11 (DEC-565, DEC-718) |
| W2-M260 | Type with absent schema file not reported unmeasured | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `81eac9a7` | R:6636 (DEC-622) |
| W2-M304 | Schema does not hold the five decision-package status values | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `81eac9a7` | B:627 (DEC-328) |
| W2-M310 | core-schema red: legacy records without state_class | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `81eac9a7` | B:1691 (DEC-466) |
| W2-M316 | Kernel has no record type for an audit report | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `81eac9a7` | B:2643 (DEC-624) |
| W2-M317 | Kernel record type for audit and adoption verdict reports | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `81eac9a7` | R:6670 (DEC-624, DEC-626) |
| W2-L243 | Committed ADRs lack state_class | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `6359bd00` | B:418 |
| W2-L260 | Kernel path-map schema lacks close_workers and close_timeout | W2-02, closed by `gov close` (`e52ad8a2`, 2026-10-21); the fix `1c21d0d2` | B:2237 (DEC-554) |
| W2-M372 | The session-start hook injects only the first 9,000 characters of a checkpoint's RESUME HERE section (`SECTION_MAX_CHARS`), and says so only in a closing line; a long section's later state never reaches the resumed session | W2-62, closed by `gov close` (`d7daf01b`, 2026-10-22) | the quality-control check, 2026-10-18 (DEC-792) |
| W2-M373 | The session-start hook names the Wave 1 prompt (`PROMPT_REL = governance/project/prompts/w1-orchestrator.md`) as the one to read first, in Wave 2 | W2-62, closed by `gov close` (`d7daf01b`, 2026-10-22) | the quality-control check, 2026-10-18 (DEC-792) |
| W2-M355 | Live clones under /tmp lost on reboot | W2-50, closed by `gov close` (`01488b72`, 2026-10-22) | B:2783 (DEC-698, DEC-699) |
| W2-H044 | Test result caching | W2-66, closed by `gov close` (`f8d1f60a`, 2026-10-27); its close record names each suite it ran and why | R:6119 (DEC-567) |
| W2-M153 | gov close runs the project's tests, about an hour per ticket | W2-66, closed by `gov close` (`f8d1f60a`, 2026-10-27); measured: the six scoped closes after it took 10 to 28 minutes each, against 66 and 76 for the full ones | B:1788 (DEC-484) |
| W2-L437 | The containment hook still flags a merge whose acceptance files equal git's own merge of its parents (`03f470a5`, "flagged, left in place" at W2-66's merge), though W1-01's rule passes it since DEC-912 | W2-72, closed by `gov close` (`6c439d8a`, 2026-10-27) | W2-66's reviews, 2026-10-24 (probe `docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`; ordinary work: yes; other) |
| W2-M404 | The secrets-indexing check feeds a store's content to `gitleaks stdin` as one input, and a read of gitleaks that begins inside a word makes a rule's leading word boundary match there, so a fragment of a longer identifier is taken for a token (W2-62's queue, 2026-10-22: a `gov-token-lower` hit, 62 bytes inside an 84-character identifier, clean on its whole line and red on the line cut at the match). Where the reads begin moves with every rebuild, so any rebuild can turn `gov check` and a close RED by chance | W2-69, closed by `gov close` (`07a8d624`, 2026-10-27) | W2-62's queue stopped at gate (b), 2026-10-22 (P-W2-62-G1, DEC-897; ordinary work: yes; other: fails closed) |
| W2-M395 | The secrets-indexing check scans a SQLite store's raw bytes as one text, so a record's header bytes, its row id's bytes and the next text value can spell a token-shaped string that no stored value holds (W2-54's rebuilt code-graph store, 2026-10-20: a `properties` length byte, the row id 27437's two bytes and `codeFunction…` made a `gov-token-lower` match). Row ids change with each rebuild, so any rebuild can turn the check RED by chance, and with it `gov check` and a close | W2-69, closed by `gov close` (`07a8d624`, 2026-10-27); settled by its choice (`docs/research/W2-69-secrets-scan.md` §13) | the orchestrator's diagnosis of W2-54 run 5's R5, 2026-10-20 (ordinary work: yes, any rebuild; other: fails closed) |
| W2-L373 | `tests/unit/secrets/` is a package named `secrets`, which shadows the standard library's `secrets` in a pytest worker where either is imported first ("'secrets' is not a package"; W2-53's fourth close, five errors) | W2-69, closed by `gov close` (`07a8d624`, 2026-10-27); the folder is `tests/unit/secrets_check/` | W2-53's close of 2026-10-20 (DEC-867) |
