# MODEL-TIERS-1: models and effort by role, and memory search (for the owner)

Written for the owner by a read-only research helper for the CTO, 2026-11-10 (DEC-1118 (4)). Nothing changes until the
owner decides. Scripts are in this folder. M = measured (source named); E = estimated (basis named). Prices, $ and pt
are USAGE-1's (§8: Sonnet 5.5 costs half of Opus 5.5 on every token kind; 1 pt ≈ $27.5). The period is USAGE-1's
(11-08 09:00 to 11-10 11:36 UTC, $1,276 in transcripts).

## 1 Headline
- **99.7 % Opus is by design, not by accident.** DEC-839 (1) puts every role on `claude-opus-5-5`. Both launch tools
  default to it. The CTO's helpers get Opus from `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5` in ~/.claude/settings.json,
  because no agent file and none of the 41 Agent calls name another model (M).
- **The tier map has never been written.** Five role files say "Model tier: standard" and the orchestrator's says
  "none"; nothing defines "standard" or reads it. The Contract's tiers (CAP-35.a-c) are Wave 3. W2-33, which writes
  each role's default model and effort, is open. W2-60a, which applies them at launch, is in progress (M).
- **DEC-1118 C (Sonnet for ACT-preparation helpers) is not applied yet.** None of the 3 Agent calls since USAGE-1 passes
  a model, and all 1,267 helper calls since then are Opus at high (M). C needs no file change and no ACT: the CTO adds
  `model: "sonnet"` and `effort: "high"` to the Agent call. **Saving: $53, 1.9 pt** (E: half of $106, M).
- **Memory search in place of reads saves little:** ≈ $11-26 (0.4-0.9 pt) (E), plus ≈ $21 (0.8 pt) from capping long Bash
  outputs (E). Both overlap with A. A search bundle (6,000 tokens) is as large as a 22k-character file, and one search
  answers 91 % of questions where a full read answers all of them.

## 2 The map as decided
| id | rule (quoted or close) | status |
|---|---|---|
| DEC-066 | role files carry "purpose, allowed-path pattern, tools, **model tier**, authority level and handoff format" | field present; value "standard" never defined |
| DEC-460 | "Main sessions run on Opus 5.5, pinned explicitly … `--model claude-opus-5-5`" (its subagent-on-4.6 part replaced by DEC-839 (3)) | in force |
| DEC-839 (1) | "**Model:** `claude-opus-5-5` for every role." | in force |
| DEC-839 (2) | effort on every launch: orchestrator high (max for owner packages); lead, engineer, research, product-spec high; test designer high (xhigh for FULL, trial); reviewer high (max for FULL probes); auditor and synthesiser max; live harness tests low, or Haiku | in force (changed by DEC-957) |
| DEC-839 (3) | "Subagents on the parent's model … sets `CLAUDE_CODE_SUBAGENT_MODEL` to `claude-opus-5-5`" | in force (user settings, M) |
| DEC-839 (5) | values carried in prompt v3 "until W2-60 and W2-21 apply them from the role defaults" | prompt line 142 (M) |
| DEC-957 | "Effort: the CTO and the Senior Engineers at high; the highest effort only for reviewers and auditors, when needed." | in force |
| DEC-1118 (1) C | "Sonnet for the helpers that prepare ACTs, reviews staying on Opus" (rule 11) | **decided, not applied** (§3) |
| DEC-1118 (2) E, F | "Sonnet test designers and reviewers at effort high only as trials, after the lift" | decided, waits for the lift |
| W2-33 (open) | "Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a's launcher" | not built |
| W2-60a (in progress) | role's default model and effort "applied on the launch line (--model, --effort) and recorded"; "A model given after -- that is not the role's is refused" | not merged; waits for W2-33's line |
| W2-60b (open) | one record per session: model, effort, window, tokens, cost | not built (spend.jsonl does part, DEC-1118 (3)) |
| W2-21 (closed) | "A launch is refused if it has no model" | in gov launch |
| W2-153 (in progress) | composed agents gain the role file's fields, model tier included (S3 amended) | "standard" passes through unchanged |
| W2-104 (in progress) | skilleval sessions use "the model and effort from the role defaults" | depends on W2-33 |
| CAP-35.a-c [W3] | tiers T0-T3, effort declared and enforced, role defaults | Wave 3; lens F's starting map (T3 Opus ≥ high, T2 Opus medium or Sonnet, T1 Haiku) was never decided |

## 3 In effect, and where
| place | what it does today (M) | reads a role's model or effort? |
|---|---|---|
| `tools/launch_worker.sh` | `--model ${LAUNCH_MODEL:-claude-opus-5-5} --effort <arg>` (low…max, required); then `gov launch <role> <ticket> -- …` | no; the caller picks the effort, and `LAUNCH_MODEL` can override the model per launch |
| `gov launch` (src/gov/launch) | passes everything after `--` unchanged (command.py `PASSTHROUGH`); sets no `CLAUDE_CODE_SUBAGENT_MODEL` | no (no model or effort term in launcher.py) |
| dispatcher (`dispatch/`) | dispatcher.py starts no session; `launch_now.sh` starts a lead with Opus, high and subagents on Opus; the dead-man push uses Haiku | no |
| resource gate (launch/gate.py, resources/) | slots, memory and CPU; the spend brake (spend.py) works on projections | no; it does not look at the model |
| operator agent | opcommon.py defaults: `claude-sonnet-5-5` (canary and push `claude-haiku-5-5`); passes no `--effort` | its own settings, not the roles' |
| CTO's Agent helpers | the CLI takes the model from: the call's `model` alias, then the agent's `model:`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the parent (docs). No agent file has `model:` (0 of 6), no call passes one (0 of 41) → Opus. Effort: the session's own, while on the parent's model | no; nothing names a model below the env default |
| role files (kernel, .claude/agents) | "Model tier: standard" (5), "none" (orchestrator) | nothing reads it |

## 4 Why 99.7 % Opus at high or max
| cause | evidence (M unless marked) | share |
|---|---|---|
| The decision itself: Opus for every role | DEC-839 (1); prompt line 142; launch_worker.sh line 37; launch_now.sh | all Opus spend |
| Helpers inherit Opus | settings.json `env.CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5`; 45 helper meta files say `pickedEffortModel: claude-opus-5-5`; Agent calls pass no `model` (38 before the cutoff, 3 after) | helpers 36.5 % of $ |
| No tier map to route by | "standard" undefined (lens F, W2-L005); W2-33 open; CAP-35 is Wave 3 | — |
| Effort floor is high | no role below high in DEC-839 (2) except live tests; launch callers pass high or max | high 84.0 %, max 12.0 %, xhigh 1.6 %, medium 2.3 %, low 0.1 % of $ |
| Reviews at max | DEC-839 (2), DEC-957 "when needed"; worker calls at max $153.6 (12 %) | 12 % |
| Helpers copy the CTO's effort | CTO 630 of 630 calls at high; helpers 5,110 of 5,110 at high | 45 % of $ |
| User default effort is xhigh | settings.json `effortLevel: xhigh` (since 11-03). The CTO's VS Code session ran at high, so the session set its own effort (E). Any session started without `--effort` gets xhigh | latent |
| The only non-Opus runs are the small jobs | sentinel and dead-man (Haiku), operator (Sonnet), live tests (Haiku): $3.5 in all (USAGE-1 §2) | 0.3 % |
By kind (M, `agg_sessions.py`): workers Opus-high $485, helpers Opus-high $466, workers Opus-max $154, CTO Opus-high $110.

## 5 What applying it takes, saving and risk per role
Saving = half the role's spend this period if it moved to Sonnet at the same effort (E, USAGE-1 §8). A full week at this
pace is about twice the figures. The pt figures assume the meter weighs Sonnet by its list price (E; the weights are not published).
| role | spend (M) | Sonnet saving (E) | quality risk | where the change goes · ACT? | DEC-1118 |
|---|---|---|---|---|---|
| ACT-preparation helper | $106 (USAGE-1 §6) | **$53, 1.9 pt** | low to medium: a missed guard edge case. The Opus review and the rehearsal stay as gates. A Sonnet reviewer found 2 real regressions in ACT-GUARD-FIX-3 | the Agent call: `model: "sonnet"`, `effort: "high"`. Sonnet does not inherit the session's effort, so it must be named (CLI 2.1.318 ≥ 2.1.292) · **no ACT** | **C: decided** |
| test designer | $241 (M, workers.py) | $121, 4.4 pt | high: weak tests are how defects slip through | trial: `LAUNCH_MODEL=claude-sonnet-5-5` on launch_worker.sh (scratch, class O, not a control) · no ACT. Lasting: W2-33 role line, kernel (b) | **E: trial after the lift** |
| reviewer / auditor | $224 workers + $23 helpers | $124 if Sonnet (not proposed); **max→high ≈ $26, 0.9 pt** | highest: they are the last gate | effort argument high instead of max · no ACT | **F: trial after the lift**; model stays Opus |
| engineer | $217 | $109, 3.9 pt | medium to high: the acceptance tests and the Opus review catch failures, but repair rounds can eat the saving | as test designer | not decided |
| ticket lead (orchestrator helpers) | $127 | $63, 2.3 pt | high: it verifies, judges and escalates | Agent call or launch_now.sh (scratch) · no ACT | not decided |
| product-spec | $10 | $5, 0.2 pt | medium: it writes the files that instruct agents | as lead | not decided |
| research | $40 | $20, 0.7 pt | medium: its verdicts feed owner decisions | Agent call · no ACT | not decided |
| general helpers (not ACT) | $152 | depends on the task | as the task's role | Agent call | — |
| the CTO | $110 | $55, 2.0 pt | highest: every delegated decision | VS Code session model · no ACT | not proposed |
Control paths (class-rules.yaml, M): ~/.claude/settings.json and .claude/settings*.json → `settings`, (b) control.
.claude/agents/**, .claude/skills/** and template/governance/kernel/** → (b) control, CAP-33. src/gov/launch → catch-all
(O): a normal ticket, not an ACT. .gov-runtime/** → (O), not a control. An Agent-call parameter touches no file.

## 6 Memory search instead of reads
| measure (M, `scan_tools.py`, `context_cost.py`) | workers (191) | helpers (44) | CTO |
|---|---|---|---|
| sessions using `gov retrieve` | 5 | 3 | 1 |
| `gov retrieve` calls / Read calls | 10 / 3,143 | 7 / 306 | 1 / 22 |
| whole-file Reads (no offset or limit) | 1,803 (57 %), 16.2 M chars, median 5.5k | 199 (65 %), 3.3 M chars, median 15.2k | 13 |
| Bash results | 5,275, 6.9 M chars, median 197 | 4,567, 8.5 M chars, median 608 | 462, 0.4 M |
| repeat reads of the same file (path hash) | 491 ($11.9) | 42 ($2.0) | 1 |
| context cost of all tool results (E: written once, then re-read on every later call; 3.7 chars per token) | $150 (whole Reads $77, partial $32, Bash $26, Grep $14) | $100 (Bash $72, whole Reads $22) | $9.5 |
| whole Reads > 22k chars of files the session never edits | 92 | 45 | 0 |
| saving if each became one 6,000-token bundle (E) | $5.8 | $4.9 | — |
| same with a 2,000-token bundle (E; a size the fresh 80 did not test) | $13.9 | $11.6 | — |
| saving if Bash outputs > 10k chars were cut to 4k (E; head/tail, quiet flags) | $7.8 (189 outputs) | $12.9 (158) | $0.1 |
- **Total:** tool results are ≈ 20 % of transcript spend ($259 of $1,276, E). Searching instead of reading would save ≈
  $11-26 (0.4-0.9 pt). Capping Bash outputs would save ≈ $21 (0.8 pt). Both overlap with A (fresh sessions at 200k),
  which shortens every re-read (E).
- **Risk:** one search answers 91.1 %, and searching again once answers 98.7 % (M, FRESH-80-RESULT.md). A full read misses
  nothing in the file. Smaller bundles answered worse (top 5: 56 of 79, with 5 wrong claims). Engineers must Read a file
  before they Edit it, and reviewers must see the whole diff. Searching saves only on files much larger than the bundle.
- **Where it fits:** orientation questions that span many documents ("which decision says X"), for helpers, leads and the
  CTO. It does not fit an engineer's, reviewer's or auditor's reading of the files they judge.

## 7 Options and a recommendation
| # | option | saving this period (E) | change · ACT? | risk | recommend |
|---|---|---|---|---|---|
| 1 | **Apply C as decided:** every ACT-preparation helper starts with Agent `model: "sonnet"`, `effort: "high"`; spend.jsonl shows the model | $53, 1.9 pt | the CTO's practice (rule 11) · none | a missed edge case; Opus review and rehearsal remain | **yes, now** |
| 2 | **E and F trials after the lift** (2 tickets each; the Opus reviewer judges the tests; F at high, not max) | up to $121 + $26 if adopted | `LAUNCH_MODEL` and the effort argument · none for the trial | as USAGE-1 §6 | **yes, after the lift (as decided)** |
| 3 | **Write the map down:** W2-33's default line per role (Opus and its effort for every role, Sonnet only where a trial passed), applied by W2-60a; add a trial exception to W2-60a's "model not the role's is refused" | 0 directly; makes 1-2 enforced and recorded | CIT-P; kernel role files (b) · **ACT** | without the exception, W2-60a blocks per-launch trials | **yes, after the lift** |
| 4 | Sonnet for more roles now (engineer, lead, research, product-spec) | ≈ $197, 7 pt | none mechanically | untested; repairs and lead mistakes cost the saving back | no; one role at a time, by trial, after E |
| 5 | Make Sonnet the default subagent model (`CLAUDE_CODE_SUBAGENT_MODEL`) | up to $233 | ~/.claude/settings.json (b) · **ACT** | moves review and auditor helpers off Opus, against C | no |
| 6 | Brief guidance: `gov retrieve` for orientation questions; cut long Bash outputs to their head and tail | ≈ $11-26 + $21, 1-1.7 pt (overlaps A) | brief text in scratch (O) · none; in a skill, ACT (b) | a missed fact (one search 91 %) | yes, as guidance for helpers and leads only |
**Recommendation: 1 now; 2 and 3 after the lift; 6 as guidance; not 4 or 5.** The CTO, reviewers, auditors, test
designers and engineers stay on Opus until a trial gives evidence (DEC-1118's basis).

## 8 Method and gaps
- **Read:** the register (DEC-066, 460, 839, 957, 1118), DECISIONS-IN-FORCE, tickets W2-11, 21, 33, 60a, 60b, 104, 149,
  153 and W1-33, 46. Also the role files, launch_worker.sh, src/gov/launch, dispatch/, the resources gate,
  opcommon.py/operator_launch.py, class-rules.yaml, ~/.claude/settings.json (model and effort keys only), USAGE-1 §1, 2,
  5, 6, 8, FRESH-80-RESULT.md, lens F §CAP-35.
- **Scripts (`python3 -I` here):** `agg_sessions.py` (spend by kind, model, effort; agent types); `helpers_by_type.py`;
  `scan_tools.py` and `context_cost.py` (tool metadata; `REPL=<chars>` sets the bundle size); `agent_calls_since.py`.
  They reuse USAGE-1's calls.jsonl and sessions.json, and open only the transcripts listed there.
- **What was read in transcripts:** tool names; whether Read had offset or limit keys; the Agent call's subagent_type,
  model and effort; a yes/no for `gov retrieve` in a Bash command; result lengths; path hashes; model, effort and
  timestamps. No message text was printed or kept.
- **Source:** model and effort precedence, code.claude.com/docs/en/sub-agents (fetched 2026-11-10; not tested on 2.1.318).
- **Gaps:** quality per model is not measured here (one Sonnet review instance only). The meter's weight for Sonnet is
  unknown. Characters per token (3.7) and bundle sizes are assumed (E). Why the CTO session runs at high when the user
  default is xhigh is not verified (E). Only Agent calls and models were checked after the cutoff. The 2.3 % of worker
  spend at medium was not traced.
