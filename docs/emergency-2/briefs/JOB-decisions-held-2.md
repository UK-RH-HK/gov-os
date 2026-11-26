# Research job: decisions-held-2, the one Sonnet pass classing the 162 older decisions in force (DEC-1252 DE-2 (a))

You are a research session (Sonnet, high effort, the role table), started by the Gov OS CTO on 2026-11-26. Read-only except your one
output file. **Memory first:** `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"`, read the whole result
(write it to a file and read it whole if long; never `head`, `tail` or a pipe), then search once more in your own words. Never open a
hidden question-set root (`/home/usain/examin-eval`, `/home/usain/gov-os-eval`) and never glob `/home/usain/*`. Decide, never ask:
a claim you cannot verify by reading a line is a "not verified" row, never a question.

Work in a worktree: `git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree add -b e2/decisions-held-2
/home/usain/gov-os-worktrees/E2-decisions-held-2 w2/integrate`; write only the output file there and commit it with
`Role: research`, `Task: chore`, `Class: C`, one trailer paragraph. Never commit to `w2/integrate`, never push.

The job form, from `docs/emergency-2/integration/PRACTICE-FIRST-PLAN.md` §2.3 (read the whole file once for context):

### 2.3 The one research pass (job form, plan 2-2's fields)

| Field | Content |
|---|---|
| Role, model | research, Sonnet, effort high; read-only except its output; about $6.60 (card DE-2) |
| Question | For each of the 162 older decisions in force: which class holds it (HELD's key), what does it affect, and may it leave agents' reading? |
| Decision it feeds | DEC-1252 DE-2 (a), applying DE-0 and DE-1: the CTO's one commit on the register |
| Scope | The 153 decisions in force up to DEC-1208 and the 9 of DEC-1239 to DEC-1247. Counted today with `gov decisions in-force`: 198 in force = 153 + 30 (DEC-1209 to DEC-1238, classed by HELD) + 9 + 6 (DEC-1248 to DEC-1253, outside scope, C10). Not in scope: superseded or done entries, EXAMIN's register, any edit to the register |
| Evidence pack | `docs/DECISION_REGISTER.md` by id; `DECISIONS-HELD.md` (the key and its rows as the worked form); `../audits/E2-AUDIT-4-DETERMINISM.md` §1.7, §4.2 (the 11 "enforced for their producers": DEC-030, 032 to 037, 091, 815, 409, 772; read each again); proposals §4; the code at the run's commit; `gov retrieve --root <integration store>` first, whole bundles |
| Yardstick | One row per decision: id; HELD class (P, P*, O, A, T, X, N, H; weakest live item); `path:line` or check id for P, P*, O, A, T; proposed `Enforced-by:` (`code`, `checked-after`, `judgement`); proposed `Affects:` (paths, specs, W1 to W16, or `none`); spent yes or no with the superseding id; leaves the digest only if H, or P with a resolving check. A claim with no line read is "not verified" |
| Output path | `docs/emergency-2/integration/DECISIONS-HELD-2.md` |
| Stop rule | All 162 rows written and counted (162, no id twice); questions become "not verified" rows, never an open question to the CTO |


## Return
Branch and head; the counts by class (P, P*, O, A, T, X, N, H) and by proposed `Enforced-by:`; how many are spent and how many may leave
the digest; the "not verified" count; your retrieves (count, queries, records used). Under 300 words.

## Your memory bundle (decisions, history and plans; uncut)
store: 5eb29e7ff560 (/home/usain/gov-os-worktrees/W2-00-store-a)
{
  "store": {
    "commit": "5eb29e7ff560a27a00d5e91d36d3f3648f0e8c0a",
    "head": "5eb29e7ff560a27a00d5e91d36d3f3648f0e8c0a",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-a"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "3fd7e64bf336df3a795a37d8",
      "sha256": "69cd972526bfc2b21616fc610b4b8c8a5e168e40f9bcd0414d9f23be47047ee7",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 191,
      "end_line": 210,
      "text": "## Counts by class\n\nCounted by a script over the class column of the three tables above (a split class such as \"P (partial)\" or \"O / N mix\" counts as its first class; `P\\*` is its own row). One row is one decision item, so a count is of items, not of lines of code.\n\n| Class | Gov OS, EMERGENCY-2 (15) | Gov OS, DEC-1209 to DEC-1238 | Gov OS total | EXAMIN (DEC-001 to DEC-005) |\n|---|---|---|---|---|\n| P code on the path | 1 | 8 | 9 | 2 |\n| P\\* on the path, outside the product | 0 | 4 | 4 | 0 |\n| O code off the path | 1 | 9 | 10 | 0 |\n| A checked after (auto) | 1 | 1 | 2 | 0 |\n| T checked after (typed) | 3 | 6 | 9 | 2 |\n| X text only | 7 | 21 | 28 | 6 |\n| N not built | 0 | 33 | 33 | 3 |\n| H history | 2 | 30 | 32 | 4 |\n| **rows** | 15 | 112 | 127 | 17 |\n\n**Reading the counts.** Of the Gov OS decisions that still ask for something (not H), the largest group is **text only** (X) and **not built** (N): most decisions are held by a sentence in a document or are not built. Code that holds a decision **on the path** is a short list: the two denies and `gov update`'s refusal to restore them, the helper-model hook (fork, Fable, other models; the exceptions file), `gov adopt`'s stage chain, and the removal of `gov context`. The next group is built and **off the path** (O): the queue and launch refusals, the patch release gates, the planned-wave check. The scratch scripts that hold a decision (P\\*) are exactly the tools the tool map (step one) must absorb or retire.\n\n---\n\n",
      "chunk_id": "3fd7e64bf336df3a795a37d8",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "01cc18b378a8d9296393a50f",
      "sha256": "87fdb243ef9cff3ef8b3956a1f5942c7e312a7c0da8e6374049c7e076d50f6ed",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 203,
      "end_line": 216,
      "text": "**How many are in force today: 190** (`gov decisions in-force`, register `docs/DECISION_REGISTER.md`). By HELD's classes (it reads DEC-1209 to DEC-1238, at `1085f9b95` on 22 November; some rows have moved since):\n\n| Group | Decisions | Held by code on the path | Spent (history) | Partial (typed, or code outside the product) | Text only or not built |\n|---|---|---|---|---|---|\n| DEC-1209 to DEC-1238, classed by HELD | 30 | 1 (DEC-1213) | 6 (1209, 1215, 1226, 1230, 1231, 1237) | 3 (1210, 1216, 1221) | 20 |\n| DEC-1239 to DEC-1245, newer than HELD | 7 | not classed | not classed | not classed | not classed |\n| Before DEC-1209, never classed by HELD | 153 | not classed | not classed | not classed | not classed |\n| **All in force** | **190** | | | | |\n\nA decision's class is the weakest of its items (HELD's rule), and HELD classes items, so I grouped them by decision with a script over HELD's tables. Audit 4 \u00a71.7 classed 11 of the 153 older ones as enforced for their producers: DEC-030, 032 to 037, 091, 815, 409, 772.\n\n**How many would leave agents' reading:**\n\n- **At least 7 now** (3.7 % of 190): 1 held by code on the path and 6 spent.\n",
      "chunk_id": "01cc18b378a8d9296393a50f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1238",
      "sha256": "9f7ae49669d1ebb3e7a31a2aeb83af095ede81bf8fad4501229cb3e3a7407583",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2135,
      "end_line": 2135,
      "text": "  - (6) **Step two, the decisions and the rubrics:** every decision since DEC-1209, and EXAMIN's from DEC-001, marked as held by code or by text only (from audits 1 and 4); in particular the ticket rubric, the model and effort rubric by criticality, and the escalation rubric (rule 8: the level set by code from the record, a decision below its level refused, the judgement kept in a fixed form); what makes each enforced on the path, and when.\n",
      "chunk_id": "8821b139d85b815b25ec61ea",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1,
      "entry": "DEC-1238",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1244",
        "DEC-1240",
        "DEC-1239"
      ],
      "in_force": true
    },
    {
      "id": "446fa0347c0a61e7eb95c50f",
      "sha256": "3eee1f94d7a52b9d9387a30f6006dcf977e29336024672e19730b87524ae8fbb",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 199,
      "end_line": 204,
      "text": "2. **Every new decision names what it affects:** an `Affects:` line with paths, specs or workflow steps (W1 to W16), or `none`. The impact trace (W6) reads it, so a change to a decision shows the paths and steps it touches. Today the graph has `Under`, `Changes` and `Supersedes` links only (`store/loader.py:410-470`).\n3. **A decision that code holds is marked so and leaves agents' reading.** The marker is the `Enforced-by:` line A-23 already adds for a new standing rule (plan 5-1; DEC-1238 (1b)): `Enforced-by: code <check id or path:line>`. The in-force digest (`decisions/command.py:79-86`) hides an entry whose marker resolves to an existing check, as it already hides `superseded` and `done` entries (`decisions/register.py` `leave_out`). The other classes (checked after, judgement, text) stay in the digest.\n4. **Spent decisions** (status DONE, which the digest already hides) are marked by the CTO as one chore commit.\n\n**How many are in force today: 190** (`gov decisions in-force`, register `docs/DECISION_REGISTER.md`). By HELD's classes (it reads DEC-1209 to DEC-1238, at `1085f9b95` on 22 November; some rows have moved since):\n\n",
      "chunk_id": "446fa0347c0a61e7eb95c50f",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "746ca268e9788523b5a1ab10",
      "sha256": "743e5b501a08f31b09c477a19e4e0ab907d0733a9df52980bff788639d4884d1",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 15,
      "end_line": 31,
      "text": "## Key\n\n| Code | Class | Meaning |\n|---|---|---|\n| **P** | code on the path | code refuses or does it before the act, on the path today's Gov OS sessions take (path:line) |\n| **P\\*** | code on the path, outside the product | the same, but the code is a scratch script or the CTO's own tool (`.gov-runtime/scratch/\u2026`, `start_lead.sh`); no adopted repository gets it |\n| **O** | code off the path | built inside `gov queue`, `gov launch`, `gov brief`, `gov release --patch` and not used by Gov OS's own sessions today |\n| **A** | checked after (auto) | a hook, cron line or after-step finds it by itself |\n| **T** | checked after (typed) | code finds it only when someone types the command |\n| **X** | text only | a sentence in a document, role file, skill, script comment or memory note; no code reads it |\n| **N** | not built | decided, with no code and no complete text carrier yet |\n| **H** | history | spent or superseded; nothing to hold |\n\nWhere an item has several parts, the row takes the **weakest** part and the notes name the strongest. \"Fix\" names the audit 4 List A id (`A-n`) or the brief line that would hold it by code. The mark \"(H\\*)\" means history once an act happens (0.1.5's cut).\n\n---\n\n",
      "chunk_id": "746ca268e9788523b5a1ab10",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "55d0aff42764ddd71aee56e3",
      "sha256": "15996a5c27c23c55d8e43dd27b4f92d73e874d08944eb659ee71cb7bffb0ed89",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 808,
      "end_line": 837,
      "text": "      \"Reuse <code>Enforced-by:</code>; an entry whose <code>code</code> marker resolves to a check, and every spent one, leaves the digest\",\n      \"No new name; the text-only decisions stay.\",\n      1\n     ],\n     [\n      \"b\",\n      \"A separate <code>Held-by:</code> line\",\n      \"Two names for one thing, two checks.\"\n     ],\n     [\n      \"c\",\n      \"Option a, and a <code>reference</code> class so the 15 architecture choices leave too\",\n      \"A fourth class to keep; about 8 % more relief.\"\n     ]\n    ],\n    \"reason\": \"One field, already approved, that the enforcement check will read anyway.\",\n    \"sources\": \"DEC-1238 (1b); E2-AUDIT-4 A-23; decisions/command.py:79-86; DECISIONS-HELD.md.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"DE-2\",\n    \"from\": \"Proposal 4\",\n    \"title\": \"Who classes the other 162 decisions?\",\n    \"found\": [\n     \"HELD read DEC-1209 to DEC-1238 only. 153 older and 9 newer (DEC-1239 to DEC-1247) are not classed.\",\n     \"Audit 4 \u00a71.7 calls 11 of the older ones enforced for their producers: DEC-030, 032 to 037, 091, 815, 409, 772.\",\n     \"The digest is about 6,800 tokens of titles that every CTO reads at each start.\"\n    ],\n    \"opts\": [\n     [\n",
      "chunk_id": "55d0aff42764ddd71aee56e3",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "886c2488e6e7babf7319007a",
      "sha256": "797f0f81d1b8d7bbaae72e0a0e2a8a8b455e536ff8729467c1babfa80f6f8954",
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "start_line": 14,
      "end_line": 39,
      "text": "## Output: `docs/emergency-2/integration/DECISIONS-HELD.md`\n1. **One row per decision** (Gov OS DEC-1209 to DEC-1238, item by item where items differ; EXAMIN DEC-001 on): id and item;\n   what it requires in one line; held by: **code on the path** (path:line) / **code off the path** (inside `gov queue`,\n   `gov launch`, `gov brief`, not used by Gov OS today) / **checked after** (auto or typed) / **text only** (where the text\n   lives) / **not built** / **history** (spent, nothing to hold); in flight (branch or brief: `e2/models-rubric`,\n   `LEAD-fixes-015a.md`, `e2/d1-verdict`, `e2/w2-207-runtime`); the List A id or the fix that would hold it by code.\n   Counts by class at the end.\n2. **The three rubrics**, each in its own section:\n   - **The ticket rubric** (feature / fix / chore, golden rule 6; DEC-1219 (5)-(6), EMERGENCY-2 \u00a74): where it is in code\n     today (`gov launch --fix/--chore`, the queue's fix landing, `NEW_TICKET_NOT_FEATURE`, the patch rule's P1/P3), what\n     still rests on text, and what makes it enforced on the path (e.g. the queue writes the fix record, `--direct` for\n     chores, `ticket.schema.json` requires `class`), with size and when (0.1.5 in flight / integration).\n   - **The model and effort rubric by criticality** (golden rule 7; DEC-1225, DEC-1236 (2)-(3); `governance/project/criticality.yaml`,\n     `.claude/hooks/agent_model.py`, `src/gov/launch/`, the role files): what holds it today, what `e2/models-rubric` and\n     `fixes-015a` F13 and F14 add, what is left (e.g. the CTO's own start script, effort for every role in one table, a\n     change to a model or effort refused unless it names the owner's decision).\n   - **The escalation rubric** (golden rule 8; `docs/emergency-2/T2-ESCALATION-RUBRIC.md`; the decisions-by-page feature,\n     `docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md`): today, is the level of a decision computed by code from its\n     record anywhere, is a decision below its level refused anywhere, is the judgement kept in a fixed form; then the\n     design that makes it enforced on the path: the record's fields that set the level (touches a spec / KPI / Contract /\n     standing decision; reversible; inside a worktree; paid or secret), the code that computes P1/P2/P3/emergency, where\n     the refusal sits (the decision-record commit's basis check; the queue for a ticket that changes a spec), and how it\n     joins the decisions page; size; when.\n3. **Spec questions** found (DEC-1238 (10)): one decision record each (question; what was found; options with costs;\n   recommendation; sources), and whether it stops work.\n\n",
      "chunk_id": "886c2488e6e7babf7319007a",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "9a6a4e8af2dd7ebd425bf5be",
      "sha256": "c5eb30caf4442269f69823d5fb7f9169152dcdc489a61c70b996c99537b199e6",
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "start_line": 788,
      "end_line": 813,
      "text": "      \"The impact trace stays blind to a decision's paths and steps.\"\n     ]\n    ],\n    \"reason\": \"The rubric is in your words, and the line gives W6 the input it lacks.\",\n    \"sources\": \"DEC-1245 (4); store/loader.py:410-470; PRACTICE-FIRST-PROPOSALS.md \u00a74.\",\n    \"stops\": \"Does not stop work.\"\n   },\n   {\n    \"id\": \"DE-1\",\n    \"from\": \"Proposal 4\",\n    \"title\": \"How is a decision that code holds marked, and does it leave agents' reading?\",\n    \"found\": [\n     \"A-23, which you approved (DEC-1238 (1b)), already adds an <code>Enforced-by:</code> line to a new standing rule.\",\n     \"The in-force digest hides only superseded and done entries.\",\n     \"Of the 30 decisions that HELD classed (DEC-1209 to DEC-1238): 1 held by code on the path, 6 spent, 3 partial, 20 text only or not built. At least 7 of 192 would leave, at most about 18.\",\n     \"About 15 more, DEC-001 to DEC-025, are architecture choices rather than rules.\"\n    ],\n    \"opts\": [\n     [\n      \"a\",\n      \"Reuse <code>Enforced-by:</code>; an entry whose <code>code</code> marker resolves to a check, and every spent one, leaves the digest\",\n      \"No new name; the text-only decisions stay.\",\n      1\n     ],\n     [\n      \"b\",\n",
      "chunk_id": "9a6a4e8af2dd7ebd425bf5be",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "28f39df11c600a02f8052e55",
      "sha256": "3dcb5d3602ac268cce2635dd35b0e355f16dcb27e3cf68eefba188e4c91380b3",
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "start_line": 320,
      "end_line": 329,
      "text": "**Decisions in force** (DEC-1209 to DEC-1231 and older standing ones the digest lists; architecture choices are omitted as not rules)\n\n| rule | for | class | in flight | evidence |\n|---|---|---|---|---|\n| DEC-1209 no new tickets, leads or rounds | stop the cycle | judgement; lifted in practice by A-10; still whole in the digest | \u2014 | register 1851 |\n| DEC-1212 (1), 1218 (2), 1229: CTO full window, fresh daily; wake cost measured | CTO cost | judgement; measuring is a scratch script | N-18 | `usage_log.sh` |\n| DEC-1212 (2), 1225: helpers Sonnet; another model refused | rubric | enforced | models-rubric | `agent_model.py:159-198` |\n| DEC-1225 (1)(5): launched roles and leads Sonnet; role files say so | rubric | enforced (off path); judgement for leads and the CTO; role files still say C3 Opus | models-rubric | `roles/engineer.md:10` |\n| DEC-1225 (2): only an owner-asked wide audit on Opus | cost | judgement: the standing auditor exception lets any auditor through | models-rubric R3 | `model-exceptions.yaml:12-13` |\n| DEC-1212 (4): no fork; no waiter or idle hooks | usage | enforced (fork); judgement (rest) | \u2014 | `agent_model.py:159-167` |\n",
      "chunk_id": "28f39df11c600a02f8052e55",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "DEC-1233",
      "sha256": "68e425ca4f3f4937a33793f586d1abbbd42d40d3ea246f7f884b5f3ec83e1e8b",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2085,
      "end_line": 2087,
      "text": "  - (3) **First in 0.1.6, ahead of the rest:** N-06 (leads launched from a filled brief, an unfilled slot refused), N-03 (the acceptance folder must be red on the base, or the landing refuses it), N-25 (the skills sweep, with memory first in every skill and template): \"These are what make the flow deterministic.\"\n  - (4) **W-2:** \"wire or retire each piece of uncalled code by its value; keep no dead code.\"\n  - (5) **Audit 4, determinism across the whole of Gov OS,** on Opus as a wide audit the owner asks for (DEC-1225 (2)), in parallel with the rest of the work: every command, step of the flow, role, skill, template, hook and rule classed as enforced by code, checked by code after the fact, or left to an agent's judgement; then what can become deterministic (the code, its size, its place, ordered by what it protects) and what must stay with agents (for each agent type: what it receives, what it must produce and in what form, and how code checks it). Brief `docs/emergency-2/briefs/AUDIT-4-determinism.md`.\n",
      "chunk_id": "6a373f31ca3732061f30d94a",
      "routes": [
        "lexical"
      ],
      "batch": 1,
      "entry": "DEC-1233",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1239"
      ],
      "in_force": true
    },
    {
      "id": "84b5dbbe9e97e8c8d40a5807",
      "sha256": "cdc5d48ac1dbddda1c6a31c6ff9a083bea1afc78a595f1885f39958a3c618225",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 214,
      "end_line": 222,
      "text": "**How many would leave agents' reading:**\n\n- **At least 7 now** (3.7 % of 190): 1 held by code on the path and 6 spent.\n- **At most about 18** from what is classed today (9.5 %): the 7 and the 11 older ones audit 4 calls enforced; those 11 are enforced \"for producers\", so each needs a look before it leaves.\n- **The 153 older ones decide the rest.** A pass over them, in HELD's key, is the real answer (card DE-2). Audit 4 notes the digest keeps DEC-1088, 1209, 1215, 933, 953 and 1182 without their changes, and I count about 15 architecture choices (DEC-001 to DEC-025) that are choices, not rules; the owner may let those leave too (card DE-1, option c).\n- Most decisions will stay: 20 of the 30 classed are text only or not built. A decision held by an instruction cannot leave; agents must read it.\n\n**What code holds and what stays practice.** Code: the `Enforced-by:` and `Affects:` lines required on a new decision by the basis check (`gov decisions basis`, extended with plan 5-1 and 5-4); the digest's hiding. Practice: deciding what is a decision, writing the lines, the one-time classing of the old ones.\n\n",
      "chunk_id": "84b5dbbe9e97e8c8d40a5807",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "DEC-1252",
      "sha256": "b3f94e430bfdc3e5d4cff58f7a309fe8087f37ab0b0842aa816496b38d336ada",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2303,
      "end_line": 2308,
      "text": "### DEC-1252 \u2014 The practice-first decisions (B-2026-11-24-practice, 31 cards): every recommendation, by the owner's D-06 (b)\n- **Status:** ACCEPTED (owner, 2026-11-25T21:55:15Z, card D-06 (b) of B-2026-11-25-cto: \"every recommendation on the practice-first page, all 31 cards, including gov findings collect and the one pass classing the 162 older decisions\"; recorded by the orchestrator with `Role: orchestrator`, `Decided-by: owner (page B-2026-11-25-cto, D-06)`; standing) \u00b7 **Under:** DEC-1245 (4), DEC-1251\n- **Decision** (each card's findings, options and costs are on `docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html`; the proposals are `docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md`): **TL-0 (a)**; **TL-1 (a)**; **TL-2 (a)**; **TL-3 (a)**; **TL-4 (a)**; **TL-5 (a)**; **TL-6 (a)**; **TL-7 (a)**; **TL-8 (a)**; **TL-9 (a)**; **TL-10 (a)**; **TL-11 (a)**; **FR-0 (a)**; **FR-1 (a)**; **FR-2 (b)**; **FR-3 (a)**; **OW-0 (a)**; **OW-1 (a)**; **OW-2 (a)**; **OW-3 (a)**; **DE-0 (a)**; **DE-1 (a)**; **DE-2 (a)**; **RG-0 (a)**; **RG-1 (a)**; **RG-2 (a)**; **DS-0 (a)**; **DS-1 (a)**; **DS-2 (a)**; **DS-3 (a)**; **DS-4 (a)**. In short: the tool status list as drafted, with its rules and where it ships; the findings log in each repository with `gov findings collect` and `gov findings sync` (a new feature, approved), a stopper pushed at once; every record carries its release, closed work never re-checked, a rule marked `Applies: at once` by the CTO; the decision rubric with `Affects:` and `Enforced-by:`, and one Sonnet research pass classing the 162 older decisions in HELD's key; the rubrics register (`docs/RUBRICS.md` and its kit copy, binding rows only); data declared in the spec's test-data table with `serves` and `path`, `real` rows naming an owner decision, an unlicensed import red for test data, old specs a notice.\n- **Basis:** the owner's answer of 2026-11-25 (D-06 (b)).\n- **Governing sources:** docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html; docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md; DEC-1245; DEC-1251.\n\n",
      "chunk_id": "1b3bfd607b71dc1f3a4fe894",
      "routes": [
        "semantic"
      ],
      "batch": 2,
      "entry": "DEC-1252",
      "status": "ACCEPTED",
      "changed_by": [],
      "in_force": true
    },
    {
      "id": "DEC-1233",
      "sha256": "b7cbc3e78b1bd40fa1fa689d90a7d7ea8cd9cc5597bc7f91cd37758e7325f7af",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2087,
      "end_line": 2088,
      "text": "  - (5) **Audit 4, determinism across the whole of Gov OS,** on Opus as a wide audit the owner asks for (DEC-1225 (2)), in parallel with the rest of the work: every command, step of the flow, role, skill, template, hook and rule classed as enforced by code, checked by code after the fact, or left to an agent's judgement; then what can become deterministic (the code, its size, its place, ordered by what it protects) and what must stay with agents (for each agent type: what it receives, what it must produce and in what form, and how code checks it). Brief `docs/emergency-2/briefs/AUDIT-4-determinism.md`.\n  - (6) **The rule from now on:** \"whatever can be deterministic becomes code; what cannot is specified so.\" It becomes part of the Contract and the Charter, so Gov OS is assessed by it: the Charter states the rule; every Contract item carries whether it is built, how it is enforced today (code, checked after the fact, or an agent's judgement), if not built why not and when, and what it should be (code, or an agent's job with its specification); audit 4's result fills these in, and the release acceptance checks them.\n",
      "chunk_id": "d55578f72efb6cd55fe5c0cc",
      "routes": [
        "lexical"
      ],
      "batch": 2,
      "entry": "DEC-1233",
      "status": "ACCEPTED",
      "changed_by": [
        "DEC-1239"
      ],
      "in_force": true
    },
    {
      "id": "140f140cd6b118b5931574cb",
      "sha256": "50ffb199d5f54978ac12d27dd0be2ff5699ff2b6814563519405f1f3dff0d279",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 323,
      "end_line": 329,
      "text": "4. **How it joins the decisions page:** `gov decisions page` takes only P1 and the P2 the CTO brings (`blocks` is not `nothing`); `rubric` is the computed line; a stopper (`blocks` set) forces the immediate page and the push; `gov decisions answer <sheet>` writes each answer as a register entry with `Decided-by: owner (page <batch>)`, so the level check at the commit passes by the same rule the sheet's entry satisfies (`ACCEPTED (owner, \u2026)`, DEC-862 (c)). `gov decisions basis --week` lists owner entries by channel (`page` or `chat`) and counts open packages not on a page, as the spec says.\n5. **The fixed form of the judgement** is the package itself: `question` (300), `found` (900), `options` 2-6 with `cost` and `consequence`, `recommendation {option, reason, confidence}`, `sources` each existing. The lead's or the CTO's own P3 and P2 choices are the same record with `status: ACCEPTED` and their `Decided-by`, listed in the digest (DEC-220), so the check at the commit is one rule for all three levels.\n\n**Size and when:**\n\n| Piece | Size | When |\n|---|---|---|\n",
      "chunk_id": "140f140cd6b118b5931574cb",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "3d354a002b387fcc7ab38967",
      "sha256": "bae251dce92cff9aed0615f4b51ae660e1c866bad47c8e8d6278e085c0704959",
      "path": "docs/emergency-2/briefs/LEAD-practice-first-plan.md",
      "start_line": 244,
      "end_line": 246,
      "text": "      \"text\": \"**What code holds and what stays practice.** Code: the `Enforced-by:` and `Affects:` lines required on a new decision by the basis check (`gov decisions basis`, extended with plan 5-1 and 5-4); the digest's hiding. Practice: deciding what is a decision, writing the lines, the one-time classing of the old ones.\\n\\n**Where it lives in the kit.** The rubric: the `decision-record.md` template (`template/governance/kernel/templates/`) and a section of `docs/RUBRICS.md` (proposal 5). The two lines: the template and the basis check.\\n\\n**Rides.** Plan 5-1 (the enforcement field, F-1) and 5-4 (the record's stated facts, F-2): `Affects:` and `Enforced-by:` are two more lines on the record those items already change. The digest change is a fix under W2-200 (`decisions/command.py:79`). Practice from today: the CTO writes both lines in every new decision.\\n\\n**Options and costs.** Cards DE-0 to DE-2 on the page.\\n\\n- **Approval:** (a) approve the rubric and `Affects:` (recommended); (b) with changes; (c) the rubric only, no `Affects:` line: cost, the impact trace stays blind to a decision's paths and steps.\\n\",\n      \"chunk_id\": \"729567ee0400859bbb8716ab\",\n      \"routes\": [\n",
      "chunk_id": "3d354a002b387fcc7ab38967",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "82455157dc4bbc96ba72f787",
      "sha256": "f147070e7aa52c144d062bf8f0691d409c95e002eb1b322a4e82c28b64919a0d",
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "start_line": 311,
      "end_line": 322,
      "text": "| \u00a75.4 memory by construction | agents use memory | enforced (off path) for the brief; judgement for starts | N-13 | A2 \u00a75 |\n| \u00a75.5 `gov context` off | no ceiling | enforced (the command is gone) | \u2014 | `cli/main.py` |\n| \u00a75.8 no CPU fallback | memory quality | enforced | \u2014 | `semantic.py:541-572` |\n| A-1 keep the nightly, brake, slots, dead-man | machine safety | **contradicted**: nightly commented, brake never scheduled, no dead-man line | w2-207 | crontab |\n| RT-1 to RT-8 | run-time tool | RT-2, RT-4, RT-6 checked after (auto) or by construction; RT-1 typed; RT-3, RT-7 not built; RT-5 hooks only; RT-8 off path | w2-207; models-rubric | A2 CAP-64 |\n| \u00a710.1 basis line checked at the commit; weekly review | no regrowth | checked after (typed) | N-11 | `decisions/basis.py` |\n| \u00a710.2 weekly measures | regrowth watch | checked after (typed), partly no code | W-3 | A2 CAP-40.c |\n| \u00a710.3 transcripts kept 365 days | scan evidence | enforced (a setting), unchecked | N-16 | `~/.claude/settings.json` |\n\n**Decisions in force** (DEC-1209 to DEC-1231 and older standing ones the digest lists; architecture choices are omitted as not rules)\n\n| rule | for | class | in flight | evidence |\n",
      "chunk_id": "82455157dc4bbc96ba72f787",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "729567ee0400859bbb8716ab",
      "sha256": "86f0584ffa64a673b156c7aa0de3f061bf0ae155e16dd2ba24475f51707bdf79",
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "start_line": 221,
      "end_line": 229,
      "text": "**What code holds and what stays practice.** Code: the `Enforced-by:` and `Affects:` lines required on a new decision by the basis check (`gov decisions basis`, extended with plan 5-1 and 5-4); the digest's hiding. Practice: deciding what is a decision, writing the lines, the one-time classing of the old ones.\n\n**Where it lives in the kit.** The rubric: the `decision-record.md` template (`template/governance/kernel/templates/`) and a section of `docs/RUBRICS.md` (proposal 5). The two lines: the template and the basis check.\n\n**Rides.** Plan 5-1 (the enforcement field, F-1) and 5-4 (the record's stated facts, F-2): `Affects:` and `Enforced-by:` are two more lines on the record those items already change. The digest change is a fix under W2-200 (`decisions/command.py:79`). Practice from today: the CTO writes both lines in every new decision.\n\n**Options and costs.** Cards DE-0 to DE-2 on the page.\n\n- **Approval:** (a) approve the rubric and `Affects:` (recommended); (b) with changes; (c) the rubric only, no `Affects:` line: cost, the impact trace stays blind to a decision's paths and steps.\n",
      "chunk_id": "729567ee0400859bbb8716ab",
      "routes": [
        "semantic"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 11,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "3fd7e64bf336df3a795a37d8",
      "parent_id": "66fec517f98459bc143753d9",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 191,
      "end_line": 210
    },
    {
      "chunk_id": "746ca268e9788523b5a1ab10",
      "parent_id": "1839820a810adac5769791f2",
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "start_line": 15,
      "end_line": 31
    },
    {
      "chunk_id": "886c2488e6e7babf7319007a",
      "parent_id": "6c519a5b5dcbff4883aeee85",
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "start_line": 14,
      "end_line": 39
    },
    {
      "chunk_id": "1b3bfd607b71dc1f3a4fe894",
      "parent_id": "2ed23f677083c2697d6db005",
      "path": "docs/DECISION_REGISTER.md",
      "start_line": 2303,
      "end_line": 2308
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "8e876d172c874e3571c08abc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "78360b66057ef0453e780ee2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "213942ff4330a20dc536dae7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "00b011dd6f60e73237b3f542",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/research/W2-92-proto-drift.py",
      "chunk_id": "9e507fb8dc0f00913edfd486",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "39de402f9125d9b9bc714885",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/precompact.py",
      "chunk_id": "ab29e80f51800e754b8ac27a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/precompact.py",
      "chunk_id": "e1400d672f8aafe7974f6ac7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/pool.py",
      "chunk_id": "43506d8f1f1bdc219a0f357f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/pool.py",
      "chunk_id": "96b60f54c19e306eb4b41cd8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "3ba1ca3e5fe70b164139b7e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/pool.py",
      "chunk_id": "b7436bf28a630e05d9f0fb4c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/tools/validate_s1.py",
      "chunk_id": "64409dfa064bfb75928c0748",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/events.py",
      "chunk_id": "85f9884db56d20be54b9d5d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/derive.py",
      "chunk_id": "25abb7d4aa5a0e65f0ad5775",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "058b05e624e85a7de1778acc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "6883808397844da21e8ade25",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "110ae2db216f6e1240705fbf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "cab06b4a4d51779a761f9901",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "cd6dd572a5f6edbaa4444edf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "ba616d8a3261f7ce1fcbee74",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "00379cf3405a0c74308f6ad7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/dispatcher.py",
      "chunk_id": "b846330b7f505840da24620c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "5be0465c7336a0519f08dc09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "99dcff6d1a2eded4c47445d5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "c1c5e57b68373411e6b126c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "d580a9e55abfe745138156c7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "d6b92d9829cc473c4a591d9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "4d1b02765694cad2de25ff68",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "bea4eddfd0441633670cfd02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "03efff181458151ad4f338e8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-new-register.py",
      "chunk_id": "6b7d9e50d731ab33408bfe84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "c1a51de1e82fbdd6264c007c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "chunk_id": "76e0e8adb7fdcc66260438df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "4c65408b759c2954a0655293",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "699a59a20eceda55fac2a79b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "547daaa9acdf99898d887edc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "b2ce3f952c91f62c41c082c0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "e796bf4cda2e181f66664789",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "9da5dde5071c715a698419ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "84984b4c1c25755ea9470b2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "54ecce6039751abd5143e497",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4ab56cb82ae415b0536ba6e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "d8ee876de586b1594a080227",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "90cef8b16816617c25d32d46",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/hooks/precompact.py",
      "chunk_id": "656d9596084b12c47012fcb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "f1b8ae203ea15a68afdca418",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "b0d2db133a27cf930a155b21",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/golden-workflow-decisions.html",
      "chunk_id": "49f87a88d722bb66ca328d01",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "961731a66b86304ffa7c656d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "6ca1b7349689a2dca842a2ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "e2d295a285038f84c17036ac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2ee0ef097deb52488e914a86",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "69c0e89113a851735ff73cc8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "b48f3fd978d135789f20f2e9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/store/loader.py",
      "chunk_id": "7b7a3001f5f4741b6d71172f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/integration-plan-decisions-2026-11-24.html",
      "chunk_id": "782f2060f0ffd414520ae695",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/ARCHIVE-SUPERSEDED.md",
      "chunk_id": "01141729926a4d53bfd1bed8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/tools/validate_s1.py",
      "chunk_id": "6e104b6471d053a43e35d8aa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/gov-os-decisions.html",
      "chunk_id": "9c90eb1e221c065e7f57c07e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "2dfc45f420fdddffa3af4ad5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "bc50d915692f7fb4daca7530",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "9a9660e8d079ccc05016c03d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/cli/errors.py",
      "chunk_id": "2fab0638d1a25bdfddbe8b36",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
      "chunk_id": "503371e8317a6a0913c87362",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/dispatch/dispatcher.py",
      "chunk_id": "c488f061656d5963b249a2d8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "96b4523e8ff1c16b31cb4c07",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "b00369517d2ad3169c9ea0a7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/vector_cache.py",
      "chunk_id": "d2b257b5f6fc4f0edbca1a2e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-141-hook/role_reads.py",
      "chunk_id": "cb51b08ff0e763c504d87a95",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/ledger.py",
      "chunk_id": "5ec5b12016e29f3ea41d909a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "5dba36b8dc5e4fe3ec6180ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/store/loader.py",
      "chunk_id": "e12e9ae12a0484f686c6ad33",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "de1a0da443cdc92857e82c28",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "587889641d57b2cbfde59ddc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/claude.py",
      "chunk_id": "4ab0c6802cffeeefcf43dc8f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "84a464cc13d67c10d0f5374b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-practice-first-plan.md",
      "chunk_id": "df604a9507f2617e880d702b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "22bb9b69c767fdd24cdccf9a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "a7870fb6393208a6c463fc17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "4fc24aeb1907ddd7788f8868",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/vector_cache.py",
      "chunk_id": "756b926b293797a4ea77f119",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "chunk_id": "d582fc8cf0b415cc94b0bd91",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/vector_cache.py",
      "chunk_id": "46d3b97a6096e104ee6b12ff",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "fb465d8fdaa5126f22f7ad4d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/lexical.py",
      "chunk_id": "02c336d8285ab1e0090e0b8d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "fea366715a68a978d6f3b8bd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "29e3957a3474f57aac75f412",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/vector_cache.py",
      "chunk_id": "4e87d470313fcb60c01ee6d7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "285d256f8530524fbb7612c5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-COMBINED.md",
      "chunk_id": "06925bad7bfc015bb65f93e4",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/tools/validate_s1.py",
      "chunk_id": "71fa60decb7dacac87b0c4ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/links/test_links.py",
      "chunk_id": "f20b964ed5c69baf39fef2cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "e6c137833f6489ec568b1e82",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/PRACTICE-FIRST-PROPOSALS.md",
      "chunk_id": "79a5a8ce90609fffb13e174c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/derive.py",
      "chunk_id": "f7a856d3875e2fbb4a930ca9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "73e98867b4626f2b459f4b97",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "984da576e2f5c161fab0a942",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "da04372fa61c836c501704c3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-PAGE-2026-11-22.html",
      "chunk_id": "7f5e31daf41c801ca37f54cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/launch/role.py",
      "chunk_id": "cb49fceb30982d40531070a5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PLAN-DECISIONS-2026-11-24.html",
      "chunk_id": "f3775b12bc48f2fe554110c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-doubtful-settled.md",
      "chunk_id": "8fbed94c8298ecaa3733966d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/store/loader.py",
      "chunk_id": "9d3739974bc916cf1f88f4ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/COMPETITIVE-ANALYSIS.md",
      "chunk_id": "d114a2d698e1d3e9afa11b20",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/DECISION_REGISTER.md",
      "chunk_id": "d8bc0e49b111e4662835411b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/codeintel/__init__.py",
      "chunk_id": "a7803ce0a6ea941337dc5e89",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-25.html",
      "chunk_id": "53c5f9787eb4e7aae460ea2c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4250c59a485bd8117c3c1f32",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/vector_cache.py",
      "chunk_id": "09f16f859e8dca802acc2954",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md",
      "chunk_id": "7fd3b4bc7c2b94aa822b720b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/GOV-OS-DECISIONS-2026-11-26.html",
      "chunk_id": "8a65bbb8f4845ab593516b02",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/AUDIT-NIGHT-1/a-decisions.md",
      "chunk_id": "09a47c5c9538744d8347e1ef",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/PRACTICE-FIRST-DECISIONS-2026-11-24.html",
      "chunk_id": "cbc05399e9a7c7650b381446",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-q7lk.md",
      "chunk_id": "29c5a93f0fb37faf79f8e309",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "5a558cbde4ec578549527579",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "eafdc78b20476aebb857aef1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "cfe7f7b8811acf669a762ec6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "0e04146049de4abcf496f163",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "4e77d573f95968936b705358",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-doubtful-settled.md",
      "chunk_id": "2b7e33de3e782d7851a3346d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "66bad4d2915626f6e2765e94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-r4xc.md",
      "chunk_id": "47215003af94eb4fffe04a72",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/gov-os-decisions.html",
      "chunk_id": "d902294f15ff3279c577479d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "a1669ab3617a2a7a09c544c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md",
      "chunk_id": "debaa3680663c7af3d4fb9df",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "6fb634c3851a3c8294612e27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "4d2bbb1cae6fb41a3609606a",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/RESTART-CLASSES.md",
      "chunk_id": "6c75b612f7516d6f3b966e4e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/tools/indep_launch.py",
      "chunk_id": "cff15f25740f7451037f2058",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "52226f0d7659b3641ac34231",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4550e628018f8cc36762907e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "9aacf6bea8b7c6f943297033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "29c2beafd1dbf1ae05ed589b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "1a067776913effa2dbd91015",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "99b27db9fe1df534863faae8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "4b9ec159fb8a9faeac928fbd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "47f2a7ae68b12348deba162d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "18ac3b27ef086ccebbba0663",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "95f6afbd4d42b13143d72980",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "f638f756c49a82c851222393",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "75ca27447a384be2c06f50a9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/W2-130-SITTING.md",
      "chunk_id": "b91098af8925cc06a43136a1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVESTIGATION-1-parts/C.md",
      "chunk_id": "a71d467b84b305e01cb44a52",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "075ca21e91bffbdcab545d04",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/plan/render.py",
      "chunk_id": "412e39f2ee41ae79b1b4f547",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "b866b1c7a01c212d7d9dd8a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/launch/test_w2_184_launch.py",
      "chunk_id": "a91ac1f43a8504a539d07c31",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "c0f0cf43c46875c2c1a20389",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
      "chunk_id": "b21729473b7d9c05931509f3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/INVENTORY-TESTS-CODE-1.md",
      "chunk_id": "7e9997d105253068b5e58dea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/AUDIT-1-decisions.md",
      "chunk_id": "7b68d373a0a238e6e8f7e11b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "97b3adb3e5683d5a76ab15e2",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/retro-P4-ceremony.md",
      "chunk_id": "8688a37c48da862c72c6b3bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/H-test-strategy.md",
      "chunk_id": "30cdc64fc3f3e843ee08e007",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-202/conftest.py",
      "chunk_id": "f53013a71a57bca80d548149",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5907
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL0RFQ0lTSU9OX1JFR0lTVEVSLm1kIiwyMDg1LDIwODcsIjZhMzczZjMxY2EzNzMyMDYxZjMwZDk0YSJdLFsiZG9jcy9ERUNJU0lPTl9SRUdJU1RFUi5tZCIsMjA4NywyMDg4LCJkNTU1NzhmNzJlZmI2Y2Q1NWZlNWMwY2MiXSxbImRvY3MvREVDSVNJT05fUkVHSVNURVIubWQiLDIxMzUsMjEzNSwiODgyMWIxMzlkODViODE1YjI1ZWM2MWVhIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2F1ZGl0cy9FMi1BVURJVC00LURFVEVSTUlOSVNNLm1kIiwzMTEsMzIyLCI4MjQ1NTE1N2RjNGJiYzk2YmE3MmY3ODciXSxbImRvY3MvZW1lcmdlbmN5LTIvYXVkaXRzL0UyLUFVRElULTQtREVURVJNSU5JU00ubWQiLDMyMCwzMjksIjI4ZjM5ZGYxMWM2MDBhMDJmODA1MmU1NSJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9icmllZnMvTEVBRC1wcmFjdGljZS1maXJzdC1wbGFuLm1kIiwyNDQsMjQ2LCIzZDM1NGEwMDJiMzg3ZmNjN2FiMzg5NjciXSxbImRvY3MvZW1lcmdlbmN5LTIvYnJpZWZzL1JFU0VBUkNILXN0ZXAyLWRlY2lzaW9ucy1ydWJyaWNzLm1kIiwzMSwzOSwiOTBmOTAwYjBmODViYzAwMzQ0N2M1YTgxIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0RFQ0lTSU9OUy1IRUxELm1kIiwyNSwzMSwiNTE0NDcwNzdlNzBjNWZiZjVmM2I2NTMyIl0sWyJkb2NzL2VtZXJnZW5jeS0yL2ludGVncmF0aW9uL0RFQ0lTSU9OUy1IRUxELm1kIiwyMDIsMjEwLCIyMDU5NDExNjgzMDdlNmE0MDZiNzk4NTAiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vREVDSVNJT05TLUhFTEQubWQiLDMyMywzMjksIjE0MGYxNDBjZDZiMTE4YjU5MzE1NzRjYiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9pbnRlZ3JhdGlvbi9QUkFDVElDRS1GSVJTVC1ERUNJU0lPTlMtMjAyNi0xMS0yNC5odG1sIiw3ODgsODEzLCI5YTZhNGU4YWYyZGQ3ZWJkNDI1YmY1YmUiXSxbImRvY3MvZW1lcmdlbmN5LTIvaW50ZWdyYXRpb24vUFJBQ1RJQ0UtRklSU1QtREVDSVNJT05TLTIwMjYtMTEtMjQuaHRtbCIsODA4LDgzNywiNTVkMGFmZjQyNzY0ZGRkNzFhZWU1NmUzIl0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDE5OSwyMDQsIjQ0NmZhMDM0N2MwYTYxZTdlYjk1YzUwZiJdLFsiZG9jcy9lbWVyZ2VuY3ktMi9wcm9wb3NhbHMvUFJBQ1RJQ0UtRklSU1QtUFJPUE9TQUxTLm1kIiwyMDMsMjE2LCIwMWNjMThiMzc4YThkOTI5NjM5M2E1MGYiXSxbImRvY3MvZW1lcmdlbmN5LTIvcHJvcG9zYWxzL1BSQUNUSUNFLUZJUlNULVBST1BPU0FMUy5tZCIsMjE0LDIyMiwiODRiNWRiYmU5ZTk3ZThjOGQ0MGE1ODA3Il0sWyJkb2NzL2VtZXJnZW5jeS0yL3Byb3Bvc2Fscy9QUkFDVElDRS1GSVJTVC1QUk9QT1NBTFMubWQiLDIyMSwyMjksIjcyOTU2N2VlMDQwMDg1OWJiYjg3MTZhYiJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYSIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiY2IxZjQ5MDM1YTI0OWYyZSIsIm8iOlsxLDYsOSwyLDAsMywzMCw1LDE4LDIwLDQsNywyNiwxMSwzNSwxMCwxNiwyOCw4LDMyLDIzLDM4LDI3LDM0LDM3LDEzLDI1LDI0LDEyLDM2LDE3LDE5LDE0LDIyLDMzLDIxLDI5LDMxLDM5LDE1XX0sInEiOiJERUNJU0lPTlMtSEVMRCBrZXkgY2xhc3NlcyBQIFAqIE8gQSBUIFggTiBILCBkZWNpc2lvbnMgaW4gZm9yY2UsIGVuZm9yY2VkIGJ5IGNvZGUgY2hlY2tlZCBhZnRlciBqdWRnZW1lbnQsIHNwZW50IGRlY2lzaW9ucywgdGhlIGRpZ2VzdCIsInIiOjAsInMiOiI1ZWIyOWU3ZmY1NjBhMjdhMDBkNWU5MWQzNmQzZjM2NDhmMGU4YzBhIiwidCI6bnVsbCwieCI6WyIxODM5ODIwYTgxMGFkYWM1NzY5NzkxZjIiLCIyZWQyM2Y2NzcwODNjMjY5N2Q2ZGIwMDUiLCI2NmZlYzUxN2Y5ODQ1OWJjMTQzNzUzZDkiLCI2YzUxOWE1YjVkY2JmZjQ4ODNhZWVlODUiXX0=",
  "routing": {
    "code": [],
    "named": [],
    "phrasings": [
      "DECISIONS-HELD key classes P P* O A T X N H, decisions in force, enforced by code checked after judgement, spent decisions, the digest",
      "DECISIONS-HELD key classes P P O T X N H decisions force enforced code checked judgement spent decisions digest"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "205941168307e6a406b79850",
        "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
        "start_line": 202,
        "end_line": 210
      },
      {
        "chunk_id": "51447077e70c5fbf5f3b6532",
        "path": "docs/emergency-2/integration/DECISIONS-HELD.md",
        "start_line": 25,
        "end_line": 31
      },
      {
        "chunk_id": "90f900b0f85bc003447c5a81",
        "path": "docs/emergency-2/briefs/RESEARCH-step2-decisions-rubrics.md",
        "start_line": 31,
        "end_line": 39
      }
    ]
  }
}
