# Lens F: model, effort and context policy

Independent assessment of the Gov OS, October 2026.

## 1. Header

| | |
|---|---|
| **Lens** | F: model, effort and context policy. The owner asked three things. (1) The record: every decision and setting that sets a model, an effort level, or a context or compaction threshold, with the reason given at the time and the case it was meant for. (2) The facts: the context window each model in use offers in this setup, and for each Wave 2 session type the compactions, tokens, cost and any evidence that a compaction lost something. (3) A proposal per role and task type, tied to CAP-35 and CAP-36. |
| **Date** | 2026-10-19. Written between 16:21 and about 17:05 UTC. |
| **Assessor** | An independent auditor (`GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-sdxk`). This is a headless session the Wave 2 orchestrator started with `--model claude-opus-5-5 --effort max`; I read those flags from the session's own process (F4). I changed no setting anywhere. |
| **Head assessed** | `w2/integrate` at `fecb870c`, in `/home/usain/Dynamic-Agentic-Engineering-OS`. The working tree has uncommitted additions to the register (DEC-813 to DEC-817, appended after line 8895), to the Wave 2 list and to the WBS. None of them concerns models, effort or compaction. Every line number cited here is the same at `fecb870c`. |
| **Branches read** | `w2/integrate` (head and working tree). `w2/W2-49` (Contract v4.2): its CAP-35, CAP-36 and CAP-37 files differ from the head's only in the version string (`git diff HEAD w2/W2-49`). The ticket worktrees under `/home/usain/gov-os-worktrees/W2-*`, for their result logs and automatic checkpoints only. |

### 1.1 Words used here

- **Session.** One run of Claude Code, the AI coding agent that the Gov OS governs.
  - **Interactive** sessions are the owner's.
  - **Headless** sessions are started from a command line (`claude -p`). When one ends it prints a **result log** (JSON) with its cost, tokens, models and turns.
- **Session types.**
  - The **orchestrator** runs the wave. It is the owner's interactive session.
  - A **lead** (ticket lead) runs one ticket in its own **worktree**, a separate checkout of the repository. A lead starts **workers** (engineer, test designer, product-spec, research) and **reviewers** (independent review sessions).
  - An **auditor** audits finished work as a fresh, read-only session.
  - The **synthesiser** merged the six lens reports of this assessment.
- **Models.**
  - `claude-opus-5-5` (Opus 5.5).
  - `claude-opus-4-6` (Opus 4.6, an older model).
  - `claude-haiku-4-5-20251001` (Haiku 4.5, a small model).
  - `claude-sonnet-5-5` (Sonnet 5.5).
- **Token and context window.** A token is the unit a model reads and writes, roughly three-quarters of an English word. The **context window** is the most tokens a model can hold at once.
- **Compaction.** When the conversation nears the **compaction threshold**, Claude Code replaces the conversation with a summary it writes itself, then carries on. Claude Code calls the threshold the "auto-compact window".
- **Effort.** How much the model reasons before it acts: low, medium, high, xhigh or max. Reasoning is billed as output; it is counted as "thinking tokens".
- **Subagent.** A helper conversation that a session starts inside itself, with the Agent tool.
  - **Explore** is a built-in read-only type.
  - **general-purpose** is another built-in type.
  - The project's role files define further types.
- **User-level settings.** The owner's settings for every project on this machine, under `~/.claude/`. Their **env block** sets environment variables in every session.
- **Launch form.** The command line that starts a headless session.
- **Cache read and cache write.** At every turn the whole conversation is sent again. The part already cached is billed cheaply (a cache read); new parts cost more (a cache write).
- **Checkpoint.** A saved note of a session's state and its next step.
  - **Automatic checkpoints** are written by **hooks**: scripts that Claude Code runs at events such as session start, the moment before a compaction, and each stop.
- **Project records.**
  - **Register:** the decision register, `docs/DECISION_REGISTER.md`; DEC-nnn is an entry.
  - **Contract:** `docs/contract/CONTRACT_v4.md`; CAP-nn is a capability.
  - **Wave 2 list:** `docs/plan/WAVE_2_LIST.md`; W2-Xnnn is an item.
  - **WBS:** the Wave 2 work breakdown, `docs/plan/WAVE_2_WBS.md`.
  - **w2 prompt:** `governance/project/prompts/w2-orchestrator.md`; **w1 prompt:** `governance/project/prompts/w1-orchestrator.md`.
- **The two questions.** Every finding answers the w2 prompt's two questions (§14, DEC-808): "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- **Severity.**
  - **High:** in ordinary work it can lose work or let a guarded action through.
  - **Medium:** in ordinary work it degrades cost, quality or the record.
  - **Low:** a record error, a rare case, or a feature that is not in use.

### 1.2 What I read

- **Register entries** on context, compaction, models and launches: DEC-208, 237, 248, 250, 420, 443, 445, 451, 460, 470, 634, 636, 648, 665, 671, 676, 715, 716, 784 and 801–809. Lines are cited where each is used. I also scanned every entry for the model, effort and window terms (`regscan.py`).
- **The prompts.** The w2 prompt in full (217 lines). The w1 prompt's §4 and lines 81 and 159. `governance/project/bootstrap.md`, lines 878 and 1791.
- **The Contract.** `docs/contract/CONTRACT_v4.md` lines 547–590, and the capability files CAP-35, 35.a–c, 36, 36.a, 37.e and 37.g, on the head and on `w2/W2-49`.
- **Code.**
  - `src/gov/launch/launcher.py` in full.
  - `src/gov/close/command.py` lines 465–482.
  - `src/gov/telemetry/counter.py` lines 1–45 and 195–300.
  - The hooks `template/governance/kernel/hooks/precompact.py` and `sessionstart.py`, and their registration in `.rulesync/hooks.jsonc`.
- **Role and agent files.** The six role files under `template/governance/kernel/roles/`, and the frontmatter of `.claude/agents/*.md`.
- **The test.** `tests/acceptance/W1-49/test_w1_49_live_session.py`.
- **List and WBS rows.**
  - Wave 2 list: W2-L005, W2-I038, W2-M049, W2-M137, W2-M229, W2-M261, W2-M372, W2-M373, W2-L203 and W2-L314.
  - WBS: W2-09 and W2-39.
- **Records.**
  - `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`.
  - `.gov-runtime/scratch/orchestrator/COMPLIANCE.md`, line 161.
  - The Wave 1 exit audit, `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`, lines 340–345.
- **Logs and checkpoints.** Every result log and automatic checkpoint named in §1.3.
- **The other lenses.**
  - Lens E (`docs/assessment/2026-10/E-roles-context.md`), for its context findings.
  - Lenses A to D and the synthesis, for what they say about models, compaction and CAP-35 and CAP-36.
- **The CLI.** The output of `claude --help`, and the text of the installed CLI binary, for the effort variables.

The user-level settings were read only from my own session's environment, with `printenv`, filtered to the model, effort and window variables. I did not open `~/.claude/`.

### 1.3 What I ran

**In the main repository, read-only** (working directory `/home/usain/Dynamic-Agentic-Engineering-OS`):

- `git log`, `git show`, `git diff`, `git grep` and `git ls-tree` on `w2/integrate` and `w2/W2-49`.
- `grep`, `sed -n`, `wc -c -l` and `ls` on the files in §1.2.
- `printenv`, filtered as described in §1.2.
- `/proc/<pid>/cmdline` for my own Claude process (2587313), and for the Claude processes running at about 16:45 UTC. For each I printed only the model and effort flags and the role and ticket names.

I ran no `gov` command and no `tk` command.

**My scripts**, in `/tmp/gov-os-assessment-F/scripts/`. Each runs with `python3 -I` and only reads.

- `sessions.py` parses every result log into `/tmp/gov-os-assessment-F/{main,worker,e}-sessions.json`:
  - the main repository's `.gov-runtime/scratch/orchestrator/log/` (312 records);
  - each worktree's `.gov-runtime/scratch/lead/log/` (104 records);
  - lens E's `/tmp/gov-os-assessment-E/log/` (11 records).
- `cplist.py` and `cps.py` list the automatic checkpoints, with time and trigger. They cover the main repository's `.gov-runtime/scratch/checkpoints/` and each worktree's.
- `attrib.py` matches each worktree compaction to the sessions running at that moment. For a lead it takes the start as the time its brief was written.
- `regscan.py` lists the register entries that name the model, effort and window terms.
- `statuses.py` counts the status line returned by each lead.
- `tally.py` produces Table 2's figures, with one record per session id.
- `w1models.py` gives the main model of each main-repository session over time.
- `fit.py` fits, by least squares, the CLI's cost estimate against token counts, per model.

**In my clone.** I made it with `git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS /tmp/gov-os-assessment-F/repo`, at `fecb870c`. The same command checked the resource gate first: load 0.13, MemAvailable 22,221,996 kB.

In it I ran the installed Claude Code CLI 2.1.292 (`~/.local/bin/claude`) eleven times. Every run used `-p … --output-format json --no-session-persistence`, and the outputs are in `/tmp/gov-os-assessment-F/runs/`.

- The clone's own project settings and hooks ran with these sessions. Where the hooks call `gov` or import its package, they run the main repository's `src/`, as the brief says of the `gov` on PATH. That is the same code at the same head.
- The hooks' automatic checkpoints went to the clone's `.gov-runtime/`. None reached the main repository: its newest checkpoint is still CP-DAEO-sdxk-0128, my own compaction.

| # | Command, run in the clone | Result | Cost |
|---|---|---|---|
| P1 | `claude -p "/autocompact"` | "Auto-compact window for Opus 5.5: 300k tokens (from CLAUDE_CODE_AUTO_COMPACT_WINDOW) … The auto setting picks a window tuned for your model and is strongly recommended for the best cost and performance. Overriding auto may result in high token usage, especially when resuming long sessions." | $0, no model call |
| P2 | `claude -p "/autocompact" --autocompact auto` | 300k, "from CLAUDE_CODE_AUTO_COMPACT_WINDOW" | $0 |
| P3 | `claude -p "/autocompact" --autocompact 500000` | 300k, "from CLAUDE_CODE_AUTO_COMPACT_WINDOW" | $0 |
| P4 | `claude -p "/autocompact" --settings '{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"500000"}}'` | 500k, "from CLAUDE_CODE_AUTO_COMPACT_WINDOW" | $0 |
| P5 | `claude -p "/autocompact" --model claude-opus-4-6` | "Opus 4.6: 300k tokens (from CLAUDE_CODE_AUTO_COMPACT_WINDOW) · capped to 200k by model" | $0 |
| P6 | `env -u CLAUDE_CODE_AUTO_COMPACT_WINDOW claude -p "/autocompact" --setting-sources project,local` | "Opus 5.5: 1m tokens (default for this model)" | $0 |
| P7 | as P6, with `--model claude-opus-4-6` | "Opus 4.6: 200k tokens (default for this model)" | $0 |
| P8 | `claude -p "/effort"` | only the usage line, `/effort <low\|medium\|high\|xhigh\|max\|auto\|…>` | $0 |
| P9 | `claude -p "/status"` | "/status isn't available in this environment." | $0 |
| P10 | `env -u CLAUDE_EFFORT claude -p "Run exactly one Bash command: printenv CLAUDE_EFFORT. Reply with its output only, nothing else." --allowedTools Bash --max-turns 3 --max-budget-usd 0.5` | "high". Model `claude-opus-5-5`, window 1,000,000 | $0.33 |
| P11 | as P10, without `env -u`, so the child inherits my `CLAUDE_EFFORT=max` | "high" | $0.12 |

P1 to P9 also had `--max-turns 1 --max-budget-usd 0.3`. The total cost was $0.45.

### 1.4 Limits

1. **User-level settings.** I read them only from my session's environment, with `printenv`, as the brief requires. A settings key under `~/.claude/` that is not an environment variable, such as a default model or effort, does not show there. P6 and P10 show the effect of whatever is set (an unpinned launch runs Opus 5.5 at effort high), but not where it is set.
2. **The orchestrator's cost and tokens are not measured.** It is an interactive session (its process has no `-p`), so it writes no result log. Its transcript is under `~/.claude/`, which this lens may not read.
3. **Compactions are counted from automatic checkpoints** whose trigger is "compaction". These carry a ticket but no session id. Where several sessions ran under one ticket, the count per session type is a range: the 18 compactions under DAEO-sdxk between 12:49 and 15:32 UTC, and one each in the W2-05 and W2-54 worktrees.
4. **Costs are the CLI's list-price estimates** (`costBasis` "list"), not invoices. The per-token prices in §2.2 are fitted to those estimates; they are not published prices.
5. **Lead minutes are understated.** A lead's `duration_ms` is 19–30 minutes shorter than its wall time. For example, W2-16-A5-run1's brief was written at 10:34:42 UTC and the run ended at 16:07:50, but its duration is 303 minutes. Minutes in Table 2 are the CLI's.
6. **One cause is unknown.** Why sessions switched to Opus 4.6 on 10-06 is not established (F9).
7. **Refusals.** The guard refused two different calls, once each, both because of how it parsed the shell command rather than for scope.
   - A here-document holding Python code with a `>` was read as a redirect into the repository root: "Bash write to '/home/usain/Dynamic-Agentic-Engineering-OS/250000' denied".
   - A redirect to a path built from a shell variable was refused as unresolvable: "Bash write to '/<guard-unresolvable>' denied".

   I then wrote the script with the file tool, into my scratch folder, and used literal paths. No call was refused twice.
8. **My session compacted once**, at 16:33:21 UTC, 12 minutes after launch (CP-DAEO-sdxk-0128). This report rests on files, logs and the commands above. I re-ran the counts after the compaction.
9. **Cut-off.** Logs and checkpoints are counted as they stood at 16:36 UTC on 2026-10-19. At about 16:45 UTC no lead or worker was running. The only Claude processes were this session, the orchestrator's interactive session, and one more interactive session in another of the owner's directories.

## 2. Answers

### 2.1 The record

Table 1 lists every decision and setting I found that sets a model, an effort level, or a context or compaction threshold. Decisions come in date order, followed by the settings and forms that rest on no decision.

- "Reason at the time" quotes or condenses the entry.
- "Case meant for" is the session the entry was written for.

**Table 1. Record.**

| # | Setting or decision | Value | Reason at the time | Case meant for | Where set |
|---|---|---|---|---|---|
| R1 | DEC-208 (owner, 10-03) | Stop with `CONTEXT_CHECKPOINT` at "about 300k tokens used, of a 1M window". From W1-29 this is automatic, with the auto-compact threshold "about 300k tokens if Claude Code allows it". | The orchestrator's context limit; an automatic resume through the PreCompact and SessionStart hooks | The main orchestrator, on a model with a 1M window | Register l.1924 |
| R2 | DEC-237 (owner, 10-04), amends DEC-208 | The orchestrator stops at about 300k, after a merge or a close. Each lead, "at about 300k tokens", writes `.gov-runtime/scratch/lead/CHECKPOINT.md` and returns `LEAD_CHECKPOINT`. | Extend the limit to leads, so that a fresh lead resumes from the file | The orchestrator and the ticket leads | Register l.2270. Still in the w2 prompt: A5 at l.216, and the orchestrator's handling at l.44 |
| R3 | DEC-248 (owner, 10-04), KPI (c) | The auto-compact threshold is "about 300k tokens (30 % of the window)" | Light auto-resume hooks (ticket W1-49, CAP-37.g) | The orchestrator and, in a worktree, the lead | Register l.2380 |
| R4 | DEC-250 | After W1-49 closes, context is handled by auto-compaction with the hooks | — | The orchestrator | Register l.2411 |
| R5 | DEC-443 and DEC-445 (10-07) | Verify the threshold from the official documentation. "A checkpoint when context utilisation passes the threshold" is accepted as a residual. | No hook receives the utilisation | The orchestrator | Register l.4862 and l.4878 |
| R6 | DEC-451 (owner, 10-07) | `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000`, at that time in the env block of the project settings (added by W1-49). The `CONTEXT_CHECKPOINT` fallback is dropped. | The documentation names the variable, "each a number of tokens from 100000 to 1000000, capped at the model's context window" | The orchestrator | Register l.4926 |
| R7 | DEC-460 (owner, 10-07) | `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6` is kept. Main sessions are pinned: a lead with `--model claude-opus-5-5`, a worker with `gov launch <role> <ticket> -- --model claude-opus-5-5`. "Each session's model is recorded in close records." | An answer to the compliance report, which found 91 co-author lines and about 70 worker sessions naming Opus 4.6. In-session subagents run on 4.6 "by design"; the 4.6 lines "come from subagent sessions and are not a defect". | In-session subagents; leads and launched workers | Register l.5064; the user-level env; the launch forms |
| R8 | DEC-634 and DEC-635 (10-11), package P-44 | The generated settings (rulesync) would lose the env block that holds the threshold, and the deny rules | — | Every adopted repository | Register l.6758 |
| R9 | DEC-636 (owner, 10-11) | The threshold (300000) moves to the env block of the owner's user-level settings, "beside CLAUDE_CODE_SUBAGENT_MODEL" | "so every adopted repository on this machine gets it". "rulesync writes no env block" goes on the Wave 2 list (W2-M229, W2-M261). | Every repository on this machine | Register l.6787; the user-level env |
| R10 | DEC-648 (10-11) and DEC-716 (10-16) | The user-level env holds `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` and `CLAUDE_CODE_SUBAGENT_MODEL`; the CLI is 2.1.292 | Checks that the settings are intact | — | Register l.6897 and l.7524 |
| R11 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` | None on record | None on record | The user-level env (`printenv`) |
| R12 | DEC-715 (owner, 10-16) | One stable launch command for leads and workers, for example `gov launch lead <ticket>`. It "builds the whole `claude` invocation itself (absolute paths, the identity in `--settings`, the model, background mode, the log file and the PID file)" and "records the model and the PID". Until it exists, the owner's lead form applies. | After the restart of 10-15, hand-written launches "matched neither of the owner's" forms | Leads and workers | Register l.7509; on the Wave 2 list, ranked high; not built yet. It names neither effort nor the compaction window. |
| R13 | The w2 prompt's lead form (§4) | `claude -p --model claude-opus-5-5 --output-format json --permission-mode acceptEdits --allowedTools … --settings '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":…}}'`, with no `--effort`, no `--fallback-model` and no compaction setting | DEC-460 and DEC-715 | Leads | w2 prompt l.54 |
| R14 | The w1 prompt's lead form | The same, without `--model`; "let the session compact at about 300k tokens" | — | Wave 1 leads | w1 prompt §4, l.81 and l.159 |
| R15 | Effort | No decision. Observed: the CLI's default, `high` (P10); this assessment's auditor F, `max` (its own flags); lens E's probes, `medium` (E l.344, l.353) | None on record | — | Nowhere in the record; only on whatever launch line is typed |
| R16 | Model tier in the role files | "standard; the orchestrator may name another model after `--`" for four worker roles. The orchestrator's file: "the model of the session the owner starts … No decision assigns a tier." | No decision assigns a tier (bootstrap l.878), and no `.claude/agents/*.md` file has a `model:` line | Every role | `template/governance/kernel/roles/engineer.md:15` and the other role files; W2-L005, deferred to Wave 3 |
| R17 | Contract CAP-35 (Wave 3) | Tiers T0–T3; a task's reasoning level (low, medium, high, extra-high) "declared and enforced"; role defaults, "minimum tier and default reasoning per role" | Contract v3, M1–M3 | Every role and task class | `CONTRACT_v4.md` l.547–558 |
| R18 | Contract CAP-36 (Wave 3) | Per run: "model/provider, task class, reasoning effort, cost, latency, pass/fail, repair count, reviewer findings" | "The owner can compare cost and pass/fail per model per task class from real runs." | Every run | `CONTRACT_v4.md` l.561–570 |
| R19 | Contract CAP-37.e (Wave 2, ticket W2-39) | "Model/provider switch reconstructs the same inputs" | — | Any session | `CONTRACT_v4.md` l.586; WBS l.143 |
| R20 | The W1-49 live-session test | `--model haiku` for the forced compaction | "The cheapest model", for a test that calls the network (DEC-232) | A test of the compaction hooks | `test_w1_49_live_session.py:34` and `:102`; DEC-671, DEC-676; W2-L314 |
| R21 | The session-start hook | After a compaction, clear or resume, it names `governance/project/prompts/w1-orchestrator.md` to the orchestrator and to leads. It injects at most 9,000 characters of a checkpoint section, inside a 10,000-character cap. | W1-49 (CAP-37.g) | The orchestrator, leads and any ticket session | `sessionstart.py:39–41` and `:92`; W2-M373, W2-M372 |
| R22 | W2-I038 | A local gpt-oss model as tier T1, deferred to Wave 3 | Model routing decides | — | Wave 2 list l.1049 (DEC-083) |

### 2.2 The facts

#### 2.2.1 The context window each model offers in this setup

The window and maximum output come from each result log (`modelUsage`). The threshold comes from P1, P5, P6 and P7.

| Model | Window | Max output | Compaction threshold here | Where it ran |
|---|---|---|---|---|
| `claude-opus-5-5` | 1,000,000 | 128,000 | 300,000, from the user-level variable (P1). Without the variable the CLI would use the full 1,000,000 (P6). | Every main session since DEC-460: all of Wave 2, and this assessment |
| `claude-opus-4-6` | 200,000 | not read | 200,000. The 300,000 setting is "capped to 200k by model" (P5); the model's own default is also 200k (P7). | General-purpose and role-type subagents; 75 unpinned main sessions on 10-06 and 10-07 |
| `claude-haiku-4-5-20251001` | 200,000 | 32,000 | — | The CLI's own small calls in every session ($0.001 to $0.33 per session type); the W1-49 live test |
| `claude-sonnet-5-5` | 1,000,000 | — | — | A custom `explore` agent in two Wave 1 sessions, W1-30-lead-run3 and W1-38-lead-run2 ($1.51) |

So 300k is 30% of Opus 5.5's window. On Opus 4.6, nothing triggers compaction before the window itself is nearly full.

#### 2.2.2 Which model ran when

Source: `w1models.py` over the main repository's result logs.

- **10-03 to 10-06:** main sessions on Opus 5.5, unpinned (the w1 launch form had no `--model`).
- **10-06 to 10-07:** 75 main sessions on Opus 4.6, with a 200k window, costing $508.97.
  - The period runs from W1-11-lead-run4b, on 10-06 after the restart that followed the expired login (COMPLIANCE.md l.161), to W1-27b-fix, which ended 10-07 10:11 UTC.
  - 47 of these sessions started no subagent at all.
  - 10 of them ended above 150k of their 200k window.
- **From DEC-460 (10-07):** main sessions on Opus 5.5, pinned.
- **Wave 2.** Everything ran on Opus 5.5 apart from the subagents noted below:
  - all 37 lead runs;
  - 75 worker sessions;
  - 17 reviewer sessions;
  - the auditor and synthesiser sessions.

  General-purpose subagents ran on Opus 4.6. In assessment D they cost $11.61 of its $33.33. Explore subagents ran on their parent's model (F8).

#### 2.2.3 Compactions, tokens and cost per session type

Wave 2, from 10-16 to 10-19 16:36 UTC.

- "Tokens" means all tokens billed: input, cache read, cache write and output.
- Cost is the CLI's list estimate.
- A resumed run reports its session's cost and tokens cumulatively, so each session is counted once, at its latest record (F5).

**Table 2. Facts per session type.**

| Session type | Sessions counted | Compactions | Tokens | Cost | Evidence of loss |
|---|---|---|---|---|---|
| Orchestrator | 1 interactive session, under DAEO-sdxk | 10, from 10-16 19:55 to 10-19 12:37 UTC: about one every 6.5 hours | Not measured (limit 2) | Not measured (limit 2) | None recorded. Its hand-kept RESUME HERE section survives compaction (B §2.8). After each compaction, though, the hook names the Wave 1 prompt (E F9, W2-M373). Its generated state block says "pending owner decisions: not known to the hook" (`precompact.py:88`). |
| Lead | 37 runs that ended, plus 7 killed or empty; 37 sessions; 5,806 CLI minutes | 3 certain (W2-16, W2-37, W2-50) and 2 more possible (W2-05, W2-54) | 380.3 M, of which 1.97 M output and 0.52 M thinking | $162.50; median $4.26 a run; most $9.11 | None recorded. No lead ever returned `LEAD_CHECKPOINT` (F2). Final contexts were 64k to 239k; none ended at 250k or more. |
| Worker: test designer 33, engineer 33, product-spec 8, research 1 | 75 sessions (77 runs, and 3 more empty) | 4 certain (W2-16 td-1, W2-50 td-1, W2-53 td-1 and eng-1), plus the 2 possible above | 425.1 M | $243.47: test designers $131.59, engineers $86.88, product-spec $21.45, research $3.55. Medians $2.28 to $3.61 a session. | None recorded. 4 runs ended at 250k or more, just under the threshold. Their automatic checkpoints carry no state (B F5), and workers' checkpoints carry no open decisions or loop counts (W2-M137). |
| Reviewer | 17 sessions (19 runs) | None seen | 71.1 M | $47.69; median $2.57; most $4.36 | None |
| Auditor: this assessment, lenses A to E | 5 sessions, 301 CLI minutes. Lens E also ran 8 probe sessions ($6.27, 16 minutes). | 18 under DAEO-sdxk between 12:49 and 15:32 UTC, shared with the synthesiser and possibly the orchestrator. B and E each report two of their own. | 196.9 M | $124.03; median $23.29. D cost $33.33, of which $11.61 was on Opus 4.6 subagents. | None reported. B and E resumed from the harness's summary and re-read files. The hook gave them the coordination ticket's context (E F11, B F5). |
| Synthesiser | 1 session, 85 CLI minutes | Among the 18 above | 16.1 M | $23.77 | None reported |
| Auditor F: this session, still running | 1 | 1 so far, at 16:33:21 UTC, 12 minutes after launch (CP-DAEO-sdxk-0128) | — | $0.45 for its probes; its own cost is not yet written | The hook injected the coordination ticket's ten tickets in progress and a checkpoint with no content (F6). I found nothing lost; I re-ran the counts after it. |

**Total.** Without the orchestrator and this session, Wave 2 so far comes to about $608 at list estimate.

**Compactions per session-hour:**

- auditors and the synthesiser together: 18 in 6.4 hours, about 2.8 an hour;
- workers: 4 to 6 in 30.5 hours, 0.13 to 0.20 an hour;
- leads: 3 to 5 in 96.8 hours;
- the orchestrator: 10 in about 65 hours;
- reviewers: none in 4.3 hours.

#### 2.2.4 Where the cost goes

**Fitted prices.** `fit.py` fits the CLI's own estimates. The largest error is $0.40 a session for Opus 5.5 and $0.63 for Opus 4.6. Input tokens are too few to fit.

| Model | Cache read, per million tokens | Cache write, per million tokens | Output, per million tokens |
|---|---|---|---|
| Opus 5.5 | about $0.21 | about $7.8 | about $19.6 |
| Opus 4.6 | about $0.53 | about $5.9 | about $30.8 |

**Re-reading the context is the largest single share for leads.** Cache reads are the context sent again at each turn. They were 48% of lead cost, 30–39% for workers, reviewers and auditors, and 13% for the synthesiser (`tally.py`). The size of the context, set by the threshold and by what a session reads, therefore drives cost.

**Thinking (effort) is a smaller share for most types.** As a share of output, thinking was:

- leads 26%;
- workers about 40%;
- reviewers 51%;
- auditors 56%;
- the synthesiser 78%.

At the fitted output price, that comes to about 6% of lead cost, 11–13% of workers', 17% of reviewers', 19% of auditors' and 40% of the synthesiser's.

**The price of a full turn on Opus 5.5.** A turn re-reads its whole context: up to about $0.06 at 300k, $0.10 at 500k, and $0.21 at 1M.

**The price of one compaction is small.** By my estimate from the fitted prices it is about $0.3 to $0.9. That covers one read of the conversation, a summary of some thousands of tokens, and a cache write of the new, shorter context. The cost of a compaction is in what the summary drops, not in money.

#### 2.2.5 Evidence that a compaction lost something

1. **A measured loss, in a test.** In W1-49's live-session case (DEC-671, DEC-676, W2-L314), after a forced compaction on Haiku 4.5, the session named loop count 17 instead of 23 in two of six runs.
2. **A measured loss of the recorded next step, in a probe.** In B's run RS (B §2.8, F5), one compaction replaced the deliberate next action with "Resume after compaction", both in `gov checkpoint --resume` and in the session-start text.
3. **Wrong or cut pointers after a compaction.**
   - The orchestrator and every lead are sent to the Wave 1 prompt (E F9, W2-M373).
   - Only the first 9,000 characters of a RESUME HERE section are injected (W2-M372).
4. **Mixed checkpoints.** All sessions under one ticket write into one folder, and the files carry no session id (E F11). This session's own compaction wrote CP-DAEO-sdxk-0128 next to the orchestrator's checkpoints.
5. **A rule that never fires.** No lead has returned `LEAD_CHECKPOINT` (F2).
6. **No recorded lost work.** I found no case in Wave 2 where a compaction lost work: none in the register, the Wave 2 list, the lead returns or the other lenses. Nothing measures it, though, so this is an absence of reports, not proof.

### 2.3 The proposal

The proposal does four things:

1. It keeps Opus 5.5 for every role that writes or judges. There is no pass/fail data per model yet that would justify a cheaper one; collecting that is CAP-36's job.
2. It makes effort explicit.
3. It keeps 300k where that figure was reasoned, and tries more room for read-heavy work.
4. It puts every value on the launch line, taken from role defaults kept in the repository.

**Table 3. Proposal.**

| Role or task type | Model | Effort | Compaction threshold | Subagent model | Set where | Cost against quality |
|---|---|---|---|---|---|---|
| Orchestrator (the owner's interactive session) | `claude-opus-5-5` | high; max when it drafts an owner package | 300k: the case DEC-208 was reasoned for | `claude-opus-5-5` | The owner's session start, with the values written into the RESUME HERE section | Its cost is not measured. A wrong coordination step costs a round, so keep the strongest model. Ten compactions in 65 hours is a low rate; the losses come from the hook (F6), not from the threshold. |
| Ticket lead | `claude-opus-5-5` | high: today's default, made explicit | 300k. Replace A5's 300k rule with a checkpoint at each milestone (F2). | None used; `claude-opus-5-5` if any | `gov launch lead` (DEC-715): `--model`, `--effort` and a `--settings` env, written to a launch record | Half of a lead's cost (48%) is re-reading its context. A lower threshold would cut that but add compactions to sessions that run for hours. At 300k, leads compacted only 3–5 times in 97 session-hours. |
| Test designer | `claude-opus-5-5` | high; xhigh for FULL-profile tickets, as a measured trial | 300k | — | `gov launch`, from the role default | The largest worker spend ($131.59; median $3.61). Its tests decide what "done" means, so a missed case costs more than the session does. Only 3 runs ended at 250k or more, so most of this work fits in one context. |
| Engineer | `claude-opus-5-5` | high | 300k | — | `gov launch` | Median $2.28 a session; thinking is 11% of the cost. The tests check its work, so the extra reasoning of xhigh or max buys less here. |
| Reviewer | `claude-opus-5-5` | high; max for FULL-profile probes, as a trial | 300k (never reached) | — | `gov launch` | Cheap (median $2.57) and never compacted. A review is worth the defect it finds, so this is where extra effort costs least. |
| Auditor: fresh, read-only, reads the large records | `claude-opus-5-5` | max, as this assessment ran. On one lens, measure high against max. | 500k per launch, as a measured trial | `claude-opus-5-5` | Per launch: `--settings '{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"500000"}}'` (P4 shows it takes effect) | At 300k the auditors compacted 2.8 times per session-hour (F7). 500k adds up to $0.04 a turn while the context is between 300k and 500k. In return it saves summaries that drop cited detail. At max, thinking was about 19% of their cost. |
| Synthesiser | `claude-opus-5-5` | max | 500k, as a trial | — | Per launch | Thinking was 40% of its $23.77. It reads six reports, so fewer compactions keep its cross-references intact. |
| Research | `claude-opus-5-5` | high | 300k | — | `gov launch` | One session, $3.55; no basis for a change |
| Product-spec: schemas, templates, documentation | `claude-opus-5-5` for now; a lower tier only as a CAP-35 trial | high | 300k | — | `gov launch` | CAP-35's own acceptance example puts a documentation task on T1. But there is no pass/fail data per model yet. A cheaper model without it trades a known cost for an unknown quality. |
| In-session read-only probes and exploration (subagents) | The parent's model, as Explore already does | The parent's | The model's own | — (these are the subagents) | `CLAUDE_CODE_SUBAGENT_MODEL` per launch, set to the parent's model, unless the owner states a reason for Opus 4.6 | Opus 4.6 has a fifth of the window and, by the CLI's estimate, about 2.5 times the cache-read price. Its only possible gain, a second model's view, is claimed by no decision. |
| Live-session tests of the harness (W1-49, W1-46) | Haiku 4.5 for cases that only check that a hook fired; `claude-opus-5-5` at low effort for the case that asks what the session remembers | low | The test's own | — | The test's command line | Haiku keeps the runs cheap, but it drops a loop count in two of six runs (DEC-676). Opus 5.5 at low effort costs more per run, but then the case tests the hooks rather than the model's recall. |
| Mechanical work: `gov` commands, checks, CI | No model (T0) | — | — | — | — | Free and deterministic |

**Per launch, not globally.** Yes: these values should be set per launch, for five reasons.

1. **The repository is the project's memory.** A value that governs every session belongs in the repository and on the launch record, not only in `~/.claude/`. DEC-636 put the threshold there so that adopted repositories on this machine get it. The cost is that no repository file holds it any more (DEC-636, DEC-648).
2. **A global value cannot vary by role.** The proposal needs different values, for example 500k for auditors.
3. **The documented flag loses to the global variable.** In CLI 2.1.292, while the user-level variable exists, `--autocompact` has no effect (P2, P3). Only an env value passed with `--settings` wins (P4). So "per launch" means the `--settings` env that the launcher already builds (`launcher.py:130`).
4. **Defaults change under the project.** On 10-06 the model changed for 75 sessions (F9). Today's defaults (Opus 5.5, high, 300k) are right because of how things stand today, not because anything records them.
5. **A machine default can stay as a fallback** for sessions the launcher does not start. The launcher overrides it and records what it set.

The owner's interactive orchestrator session is the exception: the owner picks its values, and the orchestrator writes them into its RESUME HERE section.

**The tie to CAP-35 and CAP-36.**

- **CAP-35.c, role defaults.** Table 3's columns become each role file's "Model tier" line, with a default effort and threshold that the launcher reads. Today that line says "standard", which nothing defines (W2-L005).
- **CAP-35.b, reasoning declared and enforced.** A ticket or brief may raise the effort, for example to xhigh for a FULL-profile ticket. The launcher refuses an effort below the role's minimum.
- **CAP-35.a, tiers.** No document on this head says which model is which tier. A starting map for the owner to decide:
  - T3: `claude-opus-5-5` at high or above;
  - T2: `claude-opus-5-5` at medium, or Sonnet 5.5;
  - T1: Haiku 4.5, or a local model (W2-I038);
  - T0: no model.
- **CAP-36.a, per-run telemetry.**
  - The result log already holds the model, cost, latency, tokens, window, thinking and turns.
  - The launcher adds the role, ticket, task class, effort and threshold, in a launch record.
  - The close adds pass/fail, the repair count and the reviewer findings.
  - Keep one record per session id (F5). Starting this in Wave 2 means Wave 3's routing starts with data.
- **CAP-37.e (W2-39).** The switch on 10-06 changed the window (from 1M to 200k) as well as the model. W2-39's case should include a window change.

## 3. Findings

### F1. The launcher sets and records no model, effort or window; the model pin depends on the caller typing it

**Evidence**

- **What the launcher builds.**
  - `build_settings` returns the env (`GOV_ROLE`, `GOV_TICKET`), the deny rules and the sandbox; there is no model (`src/gov/launch/launcher.py:130`).
  - The session gets `env = {**os.environ, **settings["env"]}` (`:310`) and `Popen([cli, "--settings", …, *cli_args])` (`:313`), so a model is set only if the caller types one after `--`.
  - `grep -i effort src/gov/launch/*.py` finds nothing.
- **The pin exists only in text.** DEC-460 (l.5064) states the pin as a sentence and two launch forms. DEC-715 (l.7509) plans a command that "builds the whole `claude` invocation itself (… the model …)" and "records the model and the PID". It is on the Wave 2 list, ranked high, and not built. It names neither effort nor the compaction window.
- **The role files give the choice to the caller.**
  - Four role files say "Model tier: standard; the orchestrator may name another model after `--`" (`template/governance/kernel/roles/engineer.md:15`, `independent-auditor.md:17`, `independent-test-designer.md:16`, `research.md:14`).
  - `product-spec.md:17`: "the session uses the model it is started with".
  - "Standard" is defined nowhere (bootstrap l.878; W2-L005).
- **What happened without a pin.** 75 main sessions ran on Opus 4.6, with a 200k window, on 10-06 and 10-07, costing $508.97 (`w1models.py`). Nobody noticed until the compliance report (DEC-459, DEC-460).
- **Today's default happens to be right.** An unpinned launch now gets Opus 5.5 (P10). The risk is that the default changes again, as it did on 10-06.
- **The close record does not take the model from the session.** It takes it from the commits' co-author lines (`src/gov/close/command.py:469–481`), which the session writes about itself. A session that commits nothing, such as a reviewer or an auditor, has no model on record.

Ordinary work: yes, because every worker launch passes the model by hand after `--`, and 75 sessions ran on another model when it was missing.
Consequence: fails open, because a launch without `--model` is accepted and runs on whatever default the CLI has that day; nothing refuses it or records it.

**Severity:** Medium. The planned launch command (DEC-715) is the place to fix it.

### F2. The lead's 300k checkpoint rule cannot fire before auto-compaction, and never has

**Evidence**

- **The rule.**
  - A5 (w2 prompt l.216): "If you pass about 300k tokens, write .gov-runtime/scratch/lead/CHECKPOINT.md in this worktree and return LEAD_CHECKPOINT."
  - l.44 tells the orchestrator how to restart a lead that returns it. The rule's source is DEC-237 (l.2270).
- **Why it cannot fire.** The session compacts as it nears 300k (P1), so a lead never "passes" 300k with its old context still in place. No hook or tool gives the lead its own token count (DEC-445, l.4878).
- **The orchestrator's version was dropped; the lead's was not.** DEC-451 (l.4926) dropped the orchestrator's equivalent, the `CONTEXT_CHECKPOINT` fallback, for this reason. A5's lead rule was left in place.
- **It never fired.**
  - `statuses.py` over the 48 Wave 2 lead logs: PACKAGES 25, DONE 10, LAUNCH_BLOCKED 2, ESCALATION 1, no status line 3, empty 7. `LEAD_CHECKPOINT`: 0.
  - Across all 152 Wave 1 lead logs the string appears in no result. The one log that contains it (W1-42-lead-run3) has it in quoted brief text.
  - Leads compacted instead: 3 times for certain, 5 at most (Table 2).
- **The hook covers part of the rule's purpose.** For `GOV_ROLE=orchestrator`, the role leads run as, the PreCompact hook writes a generated state block into the lead's `CHECKPOINT.md`. The block holds the git head, the tickets in progress, the worktrees and "pending owner decisions: not known to the hook" (`precompact.py:88`). It holds none of the lead's own state.

Ordinary work: yes, because any lead that runs long enough reaches the threshold; 3 to 5 did in Wave 2.
Consequence: other, because the deliberate checkpoint A5 asks for is never written, so a lead's own state at a compaction rests on the harness's summary alone. No lost work is recorded.

**Severity:** Medium.

### F3. The compaction threshold is a machine-wide user setting, and it silently beats the launch flag

**Evidence**

- **The setting.** `printenv` in this session shows `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000`, from the user-level env block, where DEC-636 put it (l.6787). Per DEC-636 and DEC-648 (l.6897), no project file holds it any more.
- **What the CLI says about it** (P1): "300k tokens (from CLAUDE_CODE_AUTO_COMPACT_WINDOW) … The auto setting picks a window tuned for your model and is strongly recommended for the best cost and performance. Overriding auto may result in high token usage, especially when resuming long sessions."
- **The launch flag is shadowed.**
  - `--autocompact 500000` still gives 300k from the variable (P3); so does `--autocompact auto` (P2). The CLI documents this flag as the per-session control (`claude --help`: "Auto-compact window size (auto, or 100k–1M tokens)").
  - Only a per-launch env value takes effect: `--settings '{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"500000"}}'` gives 500k (P4).
- **Without the user-level settings,** the CLI's own default for Opus 5.5 is the full 1M window (P6).
- **Its reach.** DEC-636's reason was "so every adopted repository on this machine gets it". The effect is that every Claude Code session this user runs on this machine, in any directory, compacts at 300k, and none of them can change it with the documented flag. Adopted projects on other machines lack it (W2-M229 l.486, W2-M261 l.518).

Ordinary work: yes, because every session on this machine runs under it, and a session or test that passes `--autocompact` gets 300k without any notice.
Consequence: other, because the value that governs every session lives outside the repository and silently overrides the per-launch flag. Nothing fails open and no work is lost.

**Severity:** Medium.

### F4. No decision sets effort; three levels are in use, and none is recorded

**Evidence**

- **No decision.**
  - `grep -c -- '--effort'` gives 0 in the register and 0 in the orchestrator's CHECKPOINT.md.
  - The w2 prompt's lead form (l.54) and DEC-460's worker form carry no `--effort`.
  - CAP-35.b (Wave 3) asks for reasoning levels that are "declared and enforced" (`CONTRACT_v4.md:557`).
- **The CLI's default is high.** A launch without `--effort`, with `CLAUDE_EFFORT` removed from its environment, reports its own effort as "high" (P10).
- **The parent's effort does not pass on.** A launch that inherits my `CLAUDE_EFFORT=max` also reports "high" (P11). The variable is an output that the CLI sets for its own Bash tool, not an input. This corrects one item in lens E's list of variables through which a worker's behaviour depends on its parent (E l.825–832): in CLI 2.1.292, effort does not pass on that way. The compaction window and the subagent model do, because they come from the user-level env.
- **Three levels in use.**
  - Leads and workers, launched with the §4 and DEC-460 forms: high, the default.
  - This assessment's auditor F: max. Its process (`/proc/2587313/cmdline`) carries `-p`, `--model claude-opus-5-5`, `--effort max`, `--output-format json`, `--permission-mode acceptEdits`, and a `--settings` env that holds only `GOV_ROLE` and `GOV_TICKET`. I printed only these flags.
  - Lens E's probes: medium (E l.344, l.353).
  - The interactive orchestrator: not observable.
- **The effect shows in thinking tokens.** Thinking was 26% of lead output but 56% of the auditors' (A to E) and 78% of the synthesiser's (`tally.py`). That fits A to E and the synthesiser running at a higher effort than the leads, though only F's flag is known.

Ordinary work: yes, because every launch runs at some effort, chosen by whoever types the command.
Consequence: other, because cost and depth of reasoning vary from launch to launch with no record. Nothing fails open.

**Severity:** Medium.

### F5. The cost, token and context figures CAP-36 needs are in every result log, but nothing collects them

**Evidence**

- **What a result log holds.** I printed the key list from `assessment-B.json`:
  - `total_cost_usd` (a list estimate);
  - `duration_ms` and `duration_api_ms`;
  - `num_turns`;
  - `usage`, for the run;
  - `modelUsage` per model: input, output, cache-read and cache-write tokens, `costUSD`, `contextWindow`, `maxOutputTokens` and `thinkingTokens`;
  - `subagent_stats`, `permission_denials` and `terminal_reason`.

  Table 2 needed nothing else.
- **What `gov telemetry` covers.**
  - It measures tokens and cost through ccusage, from the session logs under `~/.claude/` (`src/gov/telemetry/counter.py:1–12`).
  - It lists provider, role, retries and others as "UNDECIDED" (`counter.py:37–39`).
  - There is no "effort" anywhere in `src/gov/telemetry`, `src/gov/close` or `src/gov/launch`.
- **What CAP-36.a asks for** (`CONTRACT_v4.md:570`): model and provider, task class, reasoning effort, cost, latency, pass/fail, repair count and reviewer findings. Of these, model, cost and latency are in the result log. Effort, task class, pass/fail, repair count and reviewer findings are recorded nowhere per run.
- **A trap for whoever adds these logs up.** A resumed run (`--resume`) reports its session's cost and `modelUsage` cumulatively:

  | Session | Original run | Resumed run (reported) | The resume's own share |
  |---|---|---|---|
  | W2-54 td4 | $9.43 | $9.78 | $0.35 |
  | W2-54 eng5 | $5.48 | $6.22 | $0.74 |
  | W2-37 rev-1 | $2.11 | $3.07 | $0.96 |
  | W2-37 rev-2 | $2.40 | $3.15 | $0.75 |

  A sum over files over-counts these four sessions by $19.42. My own first tally made that mistake: I first took td4-resume's $9.78 for "2 turns in 0.9 minutes" as the cost of the resume itself.

Ordinary work: yes, because every run writes these logs, and any report of cost would read them.
Consequence: other, because the owner cannot yet compare cost and pass/fail per model and task class, which is CAP-36's outcome, although most of the data is already on disk.

**Severity:** Medium.

### F6. After a compaction, the hook gives a session its ticket's or Wave 1's context, not its own (confirmed in this session)

**Evidence**

- **My own compaction.** It came at 16:33:21 UTC and wrote CP-DAEO-sdxk-0128 (`.gov-runtime/scratch/checkpoints/DAEO-sdxk/`). Its only content is the next action "Resume after compaction". It sits in the coordination ticket's folder, beside the orchestrator's checkpoints.
- **What the session-start text gave me:**
  - the coordination ticket's decision (DEC-729);
  - the ten tickets in progress;
  - that empty checkpoint.

  None of it concerns lens F. As an independent auditor I was not pointed to a prompt. Leads are pointed to "appendix A5 of" `PROMPT_REL`, which is the Wave 1 prompt (`sessionstart.py:39`, `:92`).
- **The same happened to B and E.**
  - B: CP-0112 and CP-0119 (B §2.8, l.379).
  - E: CP-0110 and one more (E l.165, l.223).
- **Already known:**
  - W2-M373 (l.630) and W2-M372 (l.629);
  - E F9 (Medium) and E F11 (Low);
  - B F5 (medium-high).

Ordinary work: yes, because every long session compacts.
Consequence: other, because the session resumes from the harness's own summary, and the hook adds nothing about the session's own task.

**Severity:** Medium, as for E F9. This finding adds evidence from one more session; it is not a new defect.

### F7. Read-heavy sessions compact more than ten times as often per hour as workers; the 300k figure was reasoned for the orchestrator only

**Evidence**

- **The rates** (Table 2):
  - auditors and the synthesiser: 18 compactions in 6.4 session-hours, about 2.8 an hour. The 18 may include one or two of the orchestrator's; B and E each report two of their own.
  - this session: one compaction 12 minutes after launch;
  - workers: 4 to 6 in 30.5 hours, 0.13 to 0.20 an hour;
  - leads: 3 to 5 in 96.8 hours.
- **What the auditors read.** By `wc -c`:
  - `DECISION_REGISTER.md`: 1,017,989 bytes (8,932 lines);
  - `WAVE_2_LIST.md`: 179,127 bytes;
  - `bootstrap.md`: 282,855 bytes.

  At roughly four bytes a token, the register alone is about 250k tokens, close to the 300k threshold on its own.
- **How 300k was reasoned.**
  - DEC-208 (l.1924): for the orchestrator, "of a 1M window".
  - DEC-248 (l.2380): "30 % of the window".
  - DEC-237 extended it to leads. No decision considered workers, reviewers or auditors.
- **The other lenses.** E notes that reading displaces context (l.887). The synthesis proposes a start reading of a few thousand tokens for the orchestrator (SYNTHESIS l.439).

Ordinary work: yes, because every auditor, and every session that starts by reading the register, fills the window quickly.
Consequence: other, because each compaction replaces what the session read with a summary. For an auditor who cites lines, that means reading again. No lost work is recorded.

**Severity:** Low.

### F8. The subagent model is an older, 200k-window model, kept with no stated reason; Explore subagents ignore it

**Evidence**

- **The setting and its reason.** `printenv` shows `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6` in the user-level env. DEC-460 (l.5064) says only "by design. It is kept"; no reason is given.
- **Its window.** P5: "Opus 4.6: 300k tokens … capped to 200k by model". The result logs show `contextWindow` 200000 for `claude-opus-4-6`.
- **Where it is used.** In the main repository's logs, three Opus 5.5 sessions carry Opus 4.6 subagent cost, $16.26 in all (`w1models.py`):
  - W1-07-A1-run1: one independent-test-designer subagent, $1.25;
  - W1-42-lead-run1: one general-purpose subagent, $3.40;
  - assessment D: five general-purpose subagents, $11.61 of its $33.33.
- **Explore subagents run on the parent's model instead.**
  - Of the 20 sessions that used Explore, the 3 whose parent was on Opus 5.5 (W1-02-lead-run9, W1-30-lead-runG1, W1-42-lead-run4b) show no Opus 4.6 cost (`w1models.py`).
  - E's 8 probes started 6 Explore subagents and show no 4.6 cost either.
  - E F14 reported the same (E l.502–505, l.841–843).
- **Price, from the CLI's own estimates** (`fit.py`, 78 sessions for 4.6 and 317 for 5.5): cache reads cost about $0.53 per million tokens on Opus 4.6, against about $0.21 on Opus 5.5. So a 4.6 subagent costs more, not less, for each token of context it re-reads. These are fitted prices, not published ones.

Ordinary work: yes, because the w2 prompt allows in-session subagents for read-only work (l.60), and every general-purpose subagent then runs on Opus 4.6.
Consequence: other, because the reading is done by an older model with a fifth of the window, at a higher price per cached token, for a reason not on record.

**Severity:** Low.

### F9. DEC-460's stated cause is contradicted by the logs: 75 main sessions ran unpinned on Opus 4.6

**Evidence**

- **The statement.** DEC-460 (l.5064): "The 'Claude Opus 4.6' co-author lines come from subagent sessions and are not a defect."
- **The logs** (`w1models.py`):
  - 75 main sessions whose main model, by cost, is Opus 4.6;
  - from W1-11-lead-run4b (10-06) to W1-27b-fix (ended 10-07 10:11 UTC);
  - 47 of them started no subagent;
  - $508.97 in all;
  - `contextWindow` 200000.
- **Other records already count them.** COMPLIANCE.md (l.161) counts these sessions and dates the start "after the restart that followed the expired login". Bootstrap l.1791 already speaks of "a session that ran unpinned on Claude Opus 4.6".
- **The cause is not on record.** Today, an unpinned launch from inside a session whose environment names Opus 4.6 as the subagent model ran on Opus 5.5 (P11). So the cause does not reproduce with CLI 2.1.292.

Ordinary work: no, because every launch form now pins the model (DEC-460), so the wrong reason misleads no current step.
Consequence: other, because the register gives a wrong reason for a past model change, and a reader would not learn that a main session's model can change unnoticed.

**Severity:** Low.

### F10. Agent teams are switched on for every session, with no decision

**Evidence**

- **The setting.** `printenv` shows `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. DEC-648 (l.6897) and DEC-716 (l.7524) name it among the user-level variables. No entry gives a reason or a case (`regscan.py`).
- **The guard refuses its handback.** The Wave 1 exit audit's F-M7 (`docs/audit/wave-1/W1-43-wave-1-exit-audit.md` l.340–345) found that the guard refuses SubagentHandback to every role: "a fail-closed defect that blocks ordinary work wherever Claude Code's agent teams are enabled". W2-09 (DAEO-a3m2, still open; WBS l.103) is to put SubagentHandback on the guard's list.
- **Messages reach other sessions.** W2-L203 (l.848) notes that SendMessage reaches other sessions. E (l.825–832) found that the messaging socket and token pass to child sessions.
- **No logged session used it.** The subagent types seen are Explore, `explore`, general-purpose and the role types (`tally.py`, `w1models.py`).

Ordinary work: no, because no brief or role uses agent teams, and no logged session started a teammate.
Consequence: other, because an experimental feature is on for every session with no decision, and its first use would meet the guard's refusal (F-M7).

**Severity:** Low. Under DEC-803, a feature's risks are entry criteria of the ticket that switches it on. This feature is already on, so the owner would name that ticket.

### F11. The live compaction test asks the smallest model to recall facts, so its flaky case says little about the hooks

**Evidence**

- **The test.** `tests/acceptance/W1-49/test_w1_49_live_session.py:102` calls the CLI with `--model haiku`; l.34 calls it "the cheapest model"; the loop counts are `("17", "23")` (l.67).
- **The flaky result.** DEC-671 (l.7110) and DEC-676 (l.7172): after the compaction the session named loop count 17, not 23, in two of six runs. The case is named as a flaky live-model case, and W2-L314 (l.959) carries it: "asks a small model to repeat four facts".
- **What the test was for.** DEC-208 asked W1-29 for "a test that a compaction preserves the open decisions, the active ticket and the loop counts".

Ordinary work: no, because it is a test run, and the owner has accepted the case as flaky (DEC-676).
Consequence: other, because the evidence that a compaction keeps the loop counts rests on a model that dropped one in two of six runs, so a failure cannot tell the hooks from the model.

**Severity:** Low.

## 4. Recommendations

**Classification (DEC-809).** One finding answers yes to both questions: F1 (yes, fails open). F2 to F8 are yes and other. F9 to F11 are no and other. No finding calls for an extra round:

- F1 belongs to the launch-command ticket already ranked high on the Wave 2 list (DEC-715).
- The others are rows for existing items, owner decisions or Wave 3 (DEC-801, DEC-802).

1. **Make the launch command set the model, effort and compaction window, and record them.** DEC-715 already has the planned command build and record the model. Add to its acceptance criteria:
   - effort and the compaction window, taken with the model from role defaults kept in the repository;
   - a launch record, next to the result log, holding all three;
   - a refusal of any launch whose model is not the role's.

   The cost is small: the launcher already builds a `--settings` env, and P4 shows the window takes effect there. Rests on F1, F3, F4 and F9.
2. **An owner decision on effort per role,** as Table 3 proposes. Until then:
   - write `--effort high` into the w2 prompt's lead form (l.54) and into the worker form;
   - record the `--effort max` used for this assessment.

   Rests on F4.
3. **An owner decision on where the compaction threshold lives.** The proposal:
   - set it per launch, through the `--settings` env;
   - keep the user-level variable only as a fallback, or remove it;
   - record the value in the repository.

   While the variable exists, `--autocompact` has no effect. Run a measured 500k trial for auditors and the synthesiser, using recommendation 6. Rests on F3 and F7.
4. **Replace A5's "if you pass about 300k tokens"** with "write CHECKPOINT.md at each milestone: a worker's return, a merge, a package". Drop `LEAD_CHECKPOINT` from l.44 and l.216, as DEC-451 dropped the orchestrator's equivalent, unless the owner wants it kept. Rests on F2.
5. **Widen the planned hook fixes** (W2-M373, W2-M372, E F9, B F5) in two ways:
   - give automatic checkpoints a session id;
   - after a compaction, inject the session's own role and task, not the ticket's list of tickets in progress.

   Rests on F6 (and E F11).
6. **Start CAP-36.a's record now.** Collect each result log into one record per session id, holding the model, effort, window, tokens, cost, minutes, turns and subagents. Add the role, ticket and task class from the launcher, and pass/fail and the repair count from the close. Rests on F5 and F1.
7. **Ask the owner for the reason behind `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6`,** or set the subagent model per launch to the parent's model. Lens E proposes the same question (E l.1070). Rests on F8.
8. **Correct DEC-460's stated cause in a new register entry:** the Opus 4.6 sessions were unpinned main sessions, and the cause is not established. Rests on F9.
9. **An owner decision on `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.** Either give it a reason and name the ticket whose entry criteria carry its risks (DEC-803; W2-09 and W2-L203 are the candidates), or switch it off. Rests on F10.
10. **Run W1-49's recall case on `claude-opus-5-5` at low effort,** or keep Haiku and say in W2-L314 that a failure there tests the model, not the hooks. Rests on F11.
