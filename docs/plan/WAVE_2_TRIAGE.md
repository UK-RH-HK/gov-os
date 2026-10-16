---
id: WAVE-2-TRIAGE
type: plan
status: ACCEPTED
state_class: AUTHORITATIVE
depends_on: [WAVE-2-LIST, WAVE-2-WBS]
decisions: [DEC-105, DEC-136, DEC-718, DEC-722, DEC-725, DEC-726, DEC-728, DEC-729]
---

# Wave 2 triage of the open list rows (proposed)

**Status: ACCEPTED, with `docs/plan/WAVE_2_WBS.md` (owner, 2026-10-16; DEC-729).** Every one of the 791 open rows of `docs/plan/WAVE_2_LIST.md` §3 is placed here: **in Wave 2** (with the ticket that takes it), **Wave 3**, or **backlog**, each with a one-line reason. Nothing is silently dropped. The 42 rows already closed (§4 of the list) are not repeated.

**How to read it.** "Named in W2-xx's KPIs" means the ticket card cites the row. "Fits W2-xx's paths and KPIs" means the row lies inside that ticket's allowed paths and subject, and its builder takes it in the same round; the test designer may cite it. A row's state is re-checked against the code when its ticket picks it up (DEC-718); a row found already fixed is closed with the commit that fixed it. The owner may move any row (queued package Q-12). Revised after the owner's review of 2026-10-16 (DEC-720 to DEC-727): W2-M102 and W2-L233 come into W2-13; W2-I017 comes in, lite, through W2-49; EXP-003's rows split between W2-15a, W2-32 and W2-15b; the caching rows move to W2-48. Revision 3 (DEC-728): W2-M355, live clones under /tmp lost on reboot, moves from W2-14 to W2-50, the durable scratch root.

## Counts

| Severity | Wave 2 | Wave 3 | backlog | Total |
|---|---|---|---|---|
| high | 48 | 6 | 0 | 54 |
| medium | 309 | 32 | 15 | 356 |
| low | 170 | 40 | 131 | 341 |
| info | 11 | 7 | 23 | 41 |
| **all** | **538** | **85** | **169** | **792** |

The counts include W2-H054, added by the owner after the plan's approval (DEC-732); the 791 rows named elsewhere are the rows at approval.

**Rows per Wave 2 ticket:** W2-01 14 · W2-02 23 · W2-03 9 · W2-04 13 · W2-05 8 · W2-06 19 · W2-07 26 · W2-08 6 · W2-09 5 · W2-10 8 · W2-11 9 · W2-12 18 · W2-13 8 · W2-14 8 · W2-15a 6 · W2-15b 5 · W2-16 6 · W2-17 1 · W2-18 14 · W2-19 17 · W2-20 3 · W2-21 36 · W2-22 18 · W2-23 37 · W2-24 1 · W2-26 1 · W2-32 11 · W2-33 6 · W2-34 25 · W2-35 1 · W2-36 1 · W2-37 5 · W2-38 4 · W2-39 8 · W2-40 19 · W2-41 23 · W2-42 29 · W2-43 33 · W2-44 19 · W2-45 26 · W2-46 3 · W2-47 2 · W2-48 2 · W2-49 1 · W2-50 1.

**Wave 3 groups.** Held-out and oracle hardening (before qualification, CAP-49); risks resting on the unsandboxed orchestrator session or the install rule's spellings (Wave 3, or a non-goal under CAP-25.c); pause and freeze hardening; `gov status` accuracy; rows whose own source says Wave 3. **Backlog groups.** Test-quality debt (taken up when a ticket touches the suite, DEC-136); low edge cases no exit criterion depends on; observations; by-design items.

## Rows on the Wave 1 WBS's Wave 2 outline but not on the list

| Item | Title | Disposition | Reason |
|---|---|---|---|
| S0b2 G-13 | Framing-tolerant MCP client | W2-32 | The code-index client is a retrieval component. |
| S0b2 G-16 | Id mapping between the graphs | W2-37 | gov impact joins the record and code graphs by id. |
| S0b2 G-23 | Incremental re-index hook | W2-06 | Same as CAP-17.b (Wave 1 WBS §6). |
| S0b2 G-24 | Deletable-class join | W2-37 | gov impact's radius needs the deletable-class join. |

## Every open row

| Row | Item | Severity | Disposition | Reason |
|---|---|---|---|---|
| W2-H001 | No ticket lead runs under the ticket-lead role; leads keep orchestrator rights | high | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-H002 | CI job red 'unmeasured' until the owner approves pytest, openspec, rulesync | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-H003 | Opaque Bash write outside repository unseen by guard and containment check | high | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-H004 | Opaque Bash read of the qualification oracle without naming its path | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-H005 | Opaque Bash writes into .gov-runtime/ unseen in orchestrator session | high | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-H006 | _get_allowed_paths gives wide orchestrator scope when role argument omitted | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H007 | Missing held-out.yaml silently disables the held-out rule | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H008 | Project can delete or rewrite template secret rules, including the canary | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-H009 | In-place checkpoint save during PreCompact window can be lost | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H010 | New .gov-runtime/ names created after launch not denied | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H011 | Shared git directory writable from a launched worktree session | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H012 | Launcher does not check user ~/.claude/settings.json | high | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-H013 | Unseen link paths: existing hard links, replaced acceptance-test symlink, cp -s | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H014 | Removed text, including later secrets, persists in SQLite free pages | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-H015 | Direct openspec archive and hand-set spec status bypass readiness | high | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-H016 | Worker bulk-copied tree including held-out.yaml into scratchpad | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-H017 | DEC-385 fixture exclusion covers one exact path only | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-H018 | Decision checker too slow at scale for every gov check | high | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-H019 | Containment rests on self-declared commit trailers | high | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-H020 | gov check red on this repository: the baseline of 13 hard-block reds | high | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-H021 | Declared check commands name template/ paths absent in installed projects | high | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-H022 | Task-less commit adding test configuration outside the ticket folder refuses nothing | high | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-H023 | Close commit range follows date order, not ancestry | high | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-H024 | Any owner decision after an escalation lifts it | high | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-H025 | Escalation state and counter in caller-writable files | high | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-H026 | Regression run that collects or passes nothing counts as passed | high | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-H027 | Evidence record can be hand-written (cheap Wave 2 addition: compare with declarations) | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-H028 | CI gitleaks scans only the checkout's two commits | high | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-H029 | Project can silence the framework-lock comparison; lock unsigned until Wave 3 | high | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-H030 | Pathless git commands read protected files via tree or history | high | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-H031 | Incomplete save of a guard file stops every session of the worktree | high | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-H032 | Without an installed gov, the pre-call hook blocks every call | high | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-H033 | External references list read from the working tree; a ticket can self-unblock | high | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-H034 | Unreadable mandatory record presented as read (empty hash, 0 tokens) | high | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-H035 | Dependency proof misses citations, so a store can be released wrongly | high | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-H036 | Adoption rollback deletes every untracked non-ignored file | high | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-H037 | Authority check reads 'decision checker could not run' as green | high | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-H038 | gov close counts adoption-gap refusals toward escalation | high | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-H039 | Pre-commit tier runs slow index-freshness and recovery-rebuild checks | high | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-H040 | Pre-commit tier holds only fast checks; index checks move to pre-push or CI | high | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-H041 | Commit-time re-index (CAP-17.b), built first | high | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-H042 | Declared, language-agnostic test commands for gov close and the regression | high | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-H043 | Impact-based test selection; full suite nightly or in CI | high | W2-38 | Named in W2-38's KPIs (profile from impact, impact-selected tests). |
| W2-H044 | Test result caching | high | W2-48 | Named in W2-48's KPIs (test-result cache at close). |
| W2-H045 | gov close judges a ticket by its class, not always by acceptance tests | high | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-H046 | Start ticket leads through the launcher, not a raw claude launch under Auto mode | high | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-H047 | Probe gate refuses after integration branch is merged into ticket branch and back | high | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-H048 | core-authority reads 'decision checker could not run' as green | high | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-H049 | human_gate gaps: decision set active without owner approval trailer | high | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-H050 | Plain rulesync generate overwrites a programme's own CLAUDE.md and AGENTS.md | high | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-H051 | Delivered tasks.md template is refused by the bridge | high | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-H052 | Harness hook time limit not measured; a hook past its limit lets the call through | high | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-H053 | Governance share not measured per programme (ORION); ARGUS's half is in AR-9 | high | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-H054 | A ticket worktree's tests and gov commands import the editable install's main-tree src/, not the worktree's own code | high | W2-21 | Added by the owner (DEC-732): the launcher builds every lead and worker session in a worktree; until it lands, the rule is kept by hand in every brief. |
| W2-M001 | No test against real Ollama; embedding model registry row missing | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M002 | Canary near spellings missed; canary count unconfirmed | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M003 | gitleaks on CI is an owner install | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M004 | Tickets naming .tickets/ or .claude/ allowed by guard, denied in launch | medium | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-M005 | Whether WebSearch/WebFetch count as NETWORK_* is unsettled | medium | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-M006 | Whole-tree fixtures copy settings.json with held-out deny line | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M007 | 1461 held-out-named file copies under /tmp/pytest-of-usain | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M008 | Ticket source texts absent from the readable tree, so no tests derive from them | medium | backlog | Source texts were archived by the owner after S1-A; tests derive from the Contract and the tickets. |
| W2-M009 | Unsettled: whether record-type containment findings stay records | medium | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-M010 | Owner's manual check of freeze, pause and lift at W1-42 | medium | W2-46 | Fits W2-46's paths and KPIs (Wave 2 exit run); its builder takes it. |
| W2-M011 | Lexical index stale after every commit; no second rebuild | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M012 | adapter-portability red: .claude/, CLAUDE.md, AGENTS.md hand-kept | medium | W2-05 | Fits W2-05's paths and KPIs (git environment sweep); its builder takes it. |
| W2-M013 | No lefthook installed; owner installs at W1 exit once the baseline is empty | medium | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-M014 | CI runner is a simulation; the real runner is unseen until the owner's first push | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M015 | Commit naming another ticket that changes this ticket's paths escapes the probe gate | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M016 | Harmless tools (Monitor, Artifact, mcp__ read-only) refused in guarded sessions | medium | W2-09 | Named in W2-09's KPIs (guard tool list). |
| W2-M017 | CAP-10's contract line is 85; DEC-414's pass line is 80; measured 83.33; the contract is not re-baselined | medium | W2-15b | Named in W2-15b's KPIs (EXP-003 final measurement). |
| W2-M018 | gov ci job unmeasured here while openspec is not on the runner (CI_NOT_MEASURED) | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M019 | Guard tokeniser drops quotes and expands literal $NAME in write targets | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M020 | Change by an unseen actor during a Bash call is attributed to that call | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M021 | Frozen repo restores acceptance tests changed by opaque Bash regardless of author | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M022 | Background command writes are attributed to whichever call is active | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M023 | Prefix commands hide sudo or installs from the install rule | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M024 | Download piped to a shell inside a subshell is not seen | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M025 | Unlisted package managers (yarn add, pnpm add, make install) not seen | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M026 | Evasive install spellings (alias, variable, bash -c, eval, base64) not seen | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M027 | Option before -m or before uv subcommand hides install | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M028 | Install writing inside the repository not stopped by sandbox write wall | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M029 | Launcher deny list fixed at launch; .git/ and glob names excluded | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M030 | Fetch and install commands lose prompt in orchestrator session after ask-rule withdrawal | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M031 | Guard does not judge ln; links under .gov-runtime/ unseen | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M032 | Held-out relative path after cd or inside --option=value not resolved | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M033 | Holder exception follows symbolic links | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M034 | uv run -w<pkg> unseen; --with of inner program misread; env uv add unseen | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M035 | Here-string sh <<< treated as a non-writing command | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M036 | Here-document interpreter writes judged inconsistently by guard | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M037 | Integration merges produce containment findings | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M038 | Worker commits in a worktree attributed to the waiting lead | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M039 | Dangling edges from WBS ids and non-record trailer values | medium | W2-03 | Fits W2-03's paths and KPIs (decisions as records); its builder takes it. |
| W2-M040 | Graph reads HEAD while index reads working tree | medium | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-M041 | Canary rule over-blocks upper-case identifiers | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M042 | Path-map patterns match narrowly and silently | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M043 | Secrets-indexing check blind to compressed, UTF-32 and filename secrets | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M044 | Pre-index filter TOCTOU, hard links and split secrets | medium | Wave 3 | Pre-index filter TOCTOU and split secrets need a redesign of the filter; W2-43 holds the floor meanwhile. |
| W2-M045 | .gov-runtime/scratch/ counted as a store makes the check red here | medium | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-M046 | gitleaks trusted by name, version unverified | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M047 | Half-written resume block after kill or double write failure | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M048 | Checkpoint file kinds: symlink written through, FIFO hangs hooks | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M049 | Hooks ignore stdin; broken precompact.py makes SessionStart silent | medium | W2-10 | Named in W2-10's KPIs (guardrails explain themselves). |
| W2-M050 | READY rule reads a stale store with no freshness mark | medium | W2-34 | Fits W2-34's paths and KPIs (gov readiness --generate); its builder takes it. |
| W2-M051 | Decision packages that fail to load block nothing | medium | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-M052 | Specification gate edges | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M053 | in_progress ticket without lock can be claimed; Closed capitalised accepted | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-M054 | Acceptance folder naming another ticket's folder or empty still counts | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-M055 | Only deps read, not depends_on; SUPERSEDED without edge is good input | medium | W2-03 | Fits W2-03's paths and KPIs (decisions as records); its builder takes it. |
| W2-M056 | CIT-E rule for taxonomy changes stated only | medium | W2-37 | Fits W2-37's paths and KPIs (gov impact); its builder takes it. |
| W2-M057 | evidence and gap_ticket fields carry no id pattern or existence check | medium | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-M058 | Nothing enforces the decision-package template | medium | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-M059 | Effect of declined, revoked or stale packages on waiting tickets | medium | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-M060 | Nothing calls gov checkpoint yet | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-M061 | Checkpoint numbering has no lock and writes are not atomic | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M062 | Watchdog misses input drift and uncommitted checkpoints | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-M063 | Checkpoint family check passes when no ticket has a checkpoint | medium | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |
| W2-M064 | Held-out path travels in launcher argv | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M065 | Research session starts in repo root; research-created dirs barely seen | medium | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-M066 | Guard alone misses many install spellings for worker roles | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M067 | ln behind a wrapper not judged | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M068 | Options after operands misread for touch -d, tee, rsync, dd | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M069 | Stray module can take over gov status or check | medium | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-M070 | Index-freshness check red here and never green on an empty index | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M071 | Lexical search raises instead of returning unavailable | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M072 | Lexical query misses mid-token matches; case, stems and ranking unhandled | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M073 | No version pin in store; untracked config changes not re-judged | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M074 | Readiness content not judged; zero-width-space N/A reason passes | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M075 | readiness.close accepts any audit-class ticket; reclosed spec gets none | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M076 | readiness.close partial failures leave orphan tickets or unclosed records | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M077 | Spec id unchecked into audit ticket allowed_paths | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M078 | Readiness YAML duplicate keys last-wins; loose row identity | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M079 | --ticket without specification key returns SPECIFICATION_NOT_FOUND | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M080 | Nothing calls gov.tasks.bridge.derive; not exported | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M081 | Bridge re-run edges | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M082 | Bridge does not check role against roster or dependency state | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M083 | Bridge partial failures, concurrent duplicates and id prefix | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M084 | .claude/agents definitions placed by owner, not generated | medium | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-M085 | Orchestrator and product-spec permission denials have no mechanism | medium | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-M086 | SECRET_READ and SYSTEM_INSTALL not enforced by guard | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M087 | Freeze flag appears as a character device inside the sandbox | medium | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-M088 | Failed re-index leaves no index; non-UTF-8 name blocks indexing | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M089 | Graph cached per process; memory at DEC-078 envelope untested | medium | W2-15b | Named in W2-15b's KPIs (EXP-003 final measurement). |
| W2-M090 | Token rule still over- and under-flags after the DEC-325 repair | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M091 | gitleaks built-in rules sheltered by its global allowlist | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M092 | Filter costs two gitleaks runs per file | medium | backlog | Performance only; one extra gitleaks run per file; revisit if W2-06's fast tier exceeds 60 s. |
| W2-M093 | W1-16 suite heavy and flaky | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M094 | Launched worker cannot run the W1-16 suite | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M095 | Launcher temp folder stays on kill, SIGTERM, SIGHUP or failed removal | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M096 | Worker scratchpad deleted at session end | medium | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-M097 | Live-session, model and local_only cases cannot run in a launched worker's sandbox | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M098 | Stopping reason for a non-record start id depends on the machine | medium | W2-13 | Fits W2-13's paths and KPIs (RETR-X-02 and ranked lexical route); its builder takes it. |
| W2-M099 | Closure does not check that HEAD is among the store's commits | medium | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-M100 | W1-17 residuals (search can raise; whole-token matching) unsettled, moved on | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M101 | Guard lets through amends, here-documents, sed -i and script edits | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M102 | Ranked lexical route for exact identifiers (backlog, later wave) | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M103 | fusion.search caps at 30 hits regardless of limit | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M104 | Reranker that dies after loading makes score raise | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M105 | Merge helper git reached by lazy fetch and GIT_TRACE | medium | W2-05 | Named in W2-05's KPIs (git environment sweep). |
| W2-M106 | Decision status and id comparisons are exact and case-sensitive | medium | W2-03 | Named in W2-03's KPIs (decisions as records). |
| W2-M107 | Backdating: author date not compared with committer date | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M108 | Signature as the stricter owner-approval fact not built | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M109 | Decision checker raises false alarms on legitimate merges | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M110 | Tickets waiting on a dead package matched by file stem only | medium | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-M111 | Gates read only the exact key 'approval' | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M112 | Uncommitted acceptance-test edit not restored when the merge is flagged | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-M113 | Git configuration not pinned in containment's and W1-03's git calls | medium | W2-05 | Named in W2-05's KPIs (git environment sweep). |
| W2-M114 | Two ticket files with the same wbs_id: first wins silently | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-M115 | Late commit on a closed ticket passes via reopen and re-close | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M116 | Links or gitlinks at exactly tests/acceptance or .tickets not matched | medium | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-M117 | Lift-form rule bypassed by obfuscated command forms | medium | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-M118 | Odd objects at the freeze flag path break pause or read as unfrozen | medium | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-M119 | Killed pause leaves a freeze.<random> file; flag not synced | medium | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-M120 | gov pause --root with a missing path creates it and reports paused | medium | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-M121 | Long TMPDIR fails the sandbox start but the session exits 0 | medium | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-M122 | Guard record unbounded; writers follow links and block on pipes | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M123 | A session's guard is its own tree's code | medium | W2-18 | Fits W2-18's paths and KPIs (pinned install); its builder takes it. |
| W2-M124 | No zero-result canary for the code index | medium | W2-22 | Fits W2-22's paths and KPIs (gov doctor green); its builder takes it. |
| W2-M125 | Canaries not run after a reindex | medium | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-M126 | Supplementary query is the first long word of the ticket title | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M127 | fresh-agent-reconstruction red because gov is not on the check shell's PATH | medium | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-M128 | Schema check validates field presence only | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M129 | Check command that exits 0 is green whatever it prints | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M130 | Absent tool gives yellow, and yellow refuses nothing | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M131 | Check commands run through a shell unvalidated, with write access | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M132 | Policy coverage by substring; skill-version accepts any ACTIVE decision | medium | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |
| W2-M133 | Provenance inputs_hash does not hash the inputs | medium | W2-04 | Fits W2-04's paths and KPIs (gov context bounded); its builder takes it. |
| W2-M134 | validate_notes has no caller; gov context does not use synthesis | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M135 | Freeze mirror location follows the process's home directory | medium | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-M136 | No checkpoint on context-utilisation threshold (KPI line 3) | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-M137 | Open decisions and loop counts preserved for the orchestrator only | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-M138 | Audit validator does not check milestone value or pack_sha256 target | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M139 | Claude Code extension newer than CLI reported as drift; doctor exits 3 | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M140 | Several tools pass doctor by version only, not by hash | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M141 | core-graph red: depends_on names W1 ids, not record ids | medium | W2-03 | Fits W2-03's paths and KPIs (decisions as records); its builder takes it. |
| W2-M142 | retrieval-regression and context-reproducibility unmeasured here | medium | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-M143 | secrets-indexing exceeds the runner's 60-second limit on this tree | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M144 | Five policy keys have no associated check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M145 | Decision-citations check accepts any frontmatter id or register heading as a record | medium | W2-03 | Named in W2-03's KPIs (decisions as records). |
| W2-M146 | Decision-citations check says clean without reporting its measurement scope | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M147 | product-traceability-trailers red with 735 findings | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M148 | Escalation owner decision read from decision files only, not a register | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M149 | Check-runner error ends close uncounted without a repair ticket | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M150 | Governance-changing defined by fixed path prefixes | medium | W2-37 | Named in W2-37's KPIs (gov impact). |
| W2-M151 | Check runner's 60-second limit is fixed and untested | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M152 | Launch record per session (Wave 2 item) | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M153 | gov close runs the project's tests, about an hour per ticket | medium | W2-48 | Named in W2-48's KPIs (test-result cache at close). |
| W2-M154 | Adapter check says 'matches' without comparing some paths (Wave 2 list) | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M155 | No CI step for the adapter comparison; live loading of generated adapters unverified | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M156 | Probe record 'by the orchestrator' rests on a self-written Role trailer | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M157 | Close record lists no skills in a project with an installed kernel | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M158 | Interrupted ticket-tool close leaves a record and checkpoint that block the next close | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M159 | Refused close's test run dirties the tree where compiled files are not ignored | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M160 | Ignored files are in the test tree but not in the commit | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M161 | Only close's own git is cut off from the caller's environment and refs | medium | W2-05 | Named in W2-05's KPIs (git environment sweep). |
| W2-M162 | Acceptance run with one passing test counts as measured whatever was skipped | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M163 | Governance checks run only when the range touches a governance prefix | medium | W2-38 | Named in W2-38's KPIs (profile from impact, impact-selected tests). |
| W2-M164 | Tree and HEAD checked once at the start of close | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M165 | Task-less merge commit bringing ticket work over-refuses | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M166 | Governance share not yet in the close record | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M167 | Hooks bypassable by design (no lefthook on PATH, --no-verify, LEFTHOOK=0) | medium | backlog | By design: hooks are a convenience tier; CI and gov close are the gates (DEC-489). |
| W2-M168 | Evidence notes ref with several clones (Wave 2 list) | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M169 | skill-version check reads a missing parent commit as green; only the last pushed commit compared (Wave 2 list) | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M170 | Yellow passes the CI job; a missing path map yields no policy result | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M171 | gitleaks install trusts the pushed registry; binary version not compared | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M172 | Strict pre-commit gitleaks scan against canary fixtures, for the exit package | medium | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-M173 | Guard refuses mkdir of an allowed file's folder; Write refuses lefthook.yml | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M174 | Lock comparison ignores __pycache__, non-kernel paths, file modes, empty folders | medium | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-M175 | Lock task needs a python3 on PATH that imports gov; gov lock subcommand pending | medium | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-M176 | Path-map fix not delivered to existing projects; no check that shipped files are classed | medium | W2-17 | Named in W2-17's KPIs (gov update). |
| W2-M177 | Regression summary's last line was the plan validator's, not a suite verdict | medium | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-M178 | Estimate reads instruction files as they are now, not as they were in-session | medium | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-M179 | Session role used by the estimate is the caller's unverified word | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M180 | Governance count can be low without any sign | medium | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-M181 | Launched workers refused Write and rm under .gov-runtime/scratch/ | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M182 | Governance share in status always 'not measured' | medium | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-M183 | Status shows no audit tickets, check gates or gate records | medium | Wave 3 | gov status accuracy; not on the adoption or exit path; Wave 3. |
| W2-M184 | Absent .tickets/ or openspec/changes/ reads as an empty list | medium | Wave 3 | gov status accuracy; not on the adoption or exit path; Wave 3. |
| W2-M185 | Status trusts a store holding HEAD's commit; stale rows read clean | medium | Wave 3 | gov status accuracy; not on the adoption or exit path; Wave 3. |
| W2-M186 | Uncommitted decision packages silently absent from status | medium | Wave 3 | gov status accuracy; not on the adoption or exit path; Wave 3. |
| W2-M187 | Launcher signals only the session process, not its process group | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M188 | Resource gate, model-less launch, AUTH_REQUIRED, leads via launcher followed by hand | medium | W2-20 | Named in W2-20's KPIs (machine-wide resource gate). |
| W2-M189 | Serial-only entry naming an existing file with no case refuses nothing | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M190 | Folder entry declares nothing; byte-order mark silently drops the first entry | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M191 | rebuild --no-embeddings leaves stale vectors in the store | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M192 | Guard cannot see a script file or piped interpreter that opens protected files | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M193 | cd followed whether or not it takes effect | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M194 | Root-search shapes not built: find name tests, git grep, xargs, -c shells | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M195 | Over-refusals: here-doc lines, commit messages, find without name test | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M196 | Over-limit brace word shortened by the shell reads a held-out folder | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M197 | Denied write of the held-out file reveals its place in the reason | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M198 | Refusal at the guard deadline records no finding | medium | W2-10 | Named in W2-10's KPIs (guardrails explain themselves). |
| W2-M199 | Named pipe in hook bookkeeping folder refuses every call after 20 s | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M200 | Bookkeeping program over its 10 s ends in allow with a finding | medium | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-M201 | gov doctor check that the hook limit exceeds the guard deadline | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M202 | Integration merge into ticket branch after probe, merged back, refuses | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M203 | Task: trailer with unusual spacing escapes probe gate and work-without-task check | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M204 | Hand-resolved merge that drops probed code passes the gate | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M205 | Probe gate weak checks: ancestor-only, task-less commits, designer commits elsewhere | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M206 | gov check red in installed-layout-only projects until checks can be measured | medium | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-M207 | Misspelt 'Constrains:' key and lower-case status words give READY | medium | W2-34 | Fits W2-34's paths and KPIs (gov readiness --generate); its builder takes it. |
| W2-M208 | Close stated-result check satisfied by a printed line; stand-in check root and src only | medium | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-M209 | Reopened FULL ticket with an earlier probe record always refuses at probe gate | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M210 | Commit hook waits for the whole secrets scan (137-369 s); result caching | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M211 | Hard-block key covered by any declaring check, whatever its severity or tier | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M212 | Success form with findings or 'unmeasured' inside its result is green | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M213 | fresh-agent-reconstruction green with no checkpoint or an unfindable one | medium | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-M214 | core-pathmap reads namespaces as a list where path maps hold a map | medium | W2-23 | Fits W2-23's paths and KPIs (adoption safety); its builder takes it. |
| W2-M215 | RETIRED and REJECTED records satisfy a mandatory source | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M216 | Move to a target no namespace holds is executed, then blocks A8 | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M217 | Project whose .gitignore omits .gov-runtime/ refuses at A8 after A6's rebuild | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M218 | Project without .gitleaks.toml refuses A3 with a move | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M219 | Failed A6 batch leaves earlier batches committed with no A6 record | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M220 | Interrupted adoption batch leaves a staged state with no resume | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M221 | Flat-layout packages move without success line 7's grounds | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M222 | Adoption verdict independence rests on self-declared trailers | medium | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-M223 | Importers computed only for indexed files; A6 does not recheck at HEAD | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M224 | Rebuild failure after the record commit refuses though the moves stand | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M225 | A8 misses legacy rule files not in the path map or fixed list | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M226 | A3 with a move needs a writable /tmp/gov-cbm-<uid> | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M227 | human_gate held by one rule; active decision without owner approval not caught | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M228 | Context check edge cases: duplicate ids, non-.md names, README in ticket folder | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M229 | rulesync writes no env block; auto-compact entry lost on other machines | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M230 | HELD_OUT_STEP_FAILED merges two causes and hides other drift | medium | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-M231 | Check and hand-run generator use different project roots | medium | W2-05 | Fits W2-05's paths and KPIs (git environment sweep); its builder takes it. |
| W2-M232 | rulesync over existing settings keeps unsourced content and reorders | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M233 | Unlaunched worker session can spawn a test-designer subagent that writes acceptance tests | medium | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-M234 | Skill text can run inline shell without reaching the guard | medium | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-M235 | Launcher wiring check accepts a matcher covering only three write tools | medium | W2-09 | Fits W2-09's paths and KPIs (guard tool list); its builder takes it. |
| W2-M236 | New or renamed harness tools refused until listed | medium | W2-09 | Named in W2-09's KPIs (guard tool list). |
| W2-M237 | A3 checks what namespaces state, not what retrieval embeds | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M238 | gov close's trailer gate ignores trailers_base | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M239 | Context differs between computations with a live semantic index | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M240 | Staged gates: close runs own plus impacted tests; full suite at milestones | medium | W2-38 | Named in W2-38's KPIs (profile from impact, impact-selected tests). |
| W2-M241 | Full project test suite runs on CI machines, not the owner's machine | medium | W2-38 | Named in W2-38's KPIs (profile from impact, impact-selected tests). |
| W2-M242 | Automatic flaky-test quarantine, shown in gov status | medium | Wave 3 | Its source places it in Wave 3. |
| W2-M243 | Secrets-indexing scan checks only changed files | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M244 | Resource gate as a command | medium | W2-20 | Named in W2-20's KPIs (machine-wide resource gate). |
| W2-M245 | Launcher refuses a launch without a model | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M246 | AUTH_REQUIRED as a mechanism | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M247 | A launch record per session (id, role, ticket, model) and a Session: trailer | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M248 | Session logs read not measured after every CLI update until a new specimen | medium | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-M249 | gov close counts adoption-gap refusals toward escalation, against DEC-492 | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M250 | gov close's trailer gate honours the project's trailers base | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M251 | gov close judges the ticket-creating commit; clone path maps lack a trailers base | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M252 | Every repeated refusal opens a new repair ticket | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M253 | Tests run in a clean checkout of the commit | medium | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-M254 | Task: trailer with unusual spacing escapes the probe gate and work-without-task check | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M255 | Hand-resolved merge that drops probed code passes the probe gate | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M256 | Probe gate ignores another ticket's later commit inside this ticket's paths | medium | W2-41 | Named in W2-41's KPIs (close and escalation integrity). |
| W2-M257 | human_gate gap: a gate never written as a decision package | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M258 | How the system knows a register entry is the owner's (owner-signed decisions) | medium | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-M259 | A hard-block policy key is covered by any declaring check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M260 | Type with absent schema file not reported unmeasured | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M261 | rulesync writes no env block; adopted projects elsewhere lack auto-compact window | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M262 | Close's test-runner cases and secrets scan fail under concurrent machine load | medium | W2-20 | Named in W2-20's KPIs (machine-wide resource gate). |
| W2-M263 | product-traceability-trailers red 'nothing is judged' right after adoption | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M264 | gov doctor reports version drift without failing on it | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M265 | Runner reports an absent tool of a hard-block check as red? | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M266 | Moving the citations base takes earlier commits out of judgement unreported | medium | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-M267 | Any Markdown file with decision id in frontmatter counts as its record | medium | W2-03 | Named in W2-03's KPIs (decisions as records). |
| W2-M268 | Project states on purpose that it declares no G3 check | medium | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-M269 | Fetch and merge evidence notes before writing, for multiple clones | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M270 | Skill-version check: missing parent commit green; only last pushed commit compared | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M271 | Hosted CI installs the approved tools by checksum | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M272 | Local-only checks reported as local-only by gov ci job | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M273 | Full git history in CI for checks that read it | medium | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-M274 | core-claims and gov readiness disagree on which rows need gap tickets | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M275 | gov rebuild and gov check unusable inside a launched session | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M276 | checker.close writes audit ticket citing DEC-088 and MR-4 | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M277 | Adoption auditor could not reproduce the A3 proposal_sha256 | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M278 | Containment check reports sandbox placeholders as worker changes | medium | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-M279 | Kernel hook programs look in project's src after the installed package | medium | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-M280 | Stop program ends silent with no checkpoint where gov not importable | medium | W2-10 | Named in W2-10's KPIs (guardrails explain themselves). |
| W2-M281 | Adapter-portability does not read the template's hooks source | medium | W2-05 | Fits W2-05's paths and KPIs (git environment sweep); its builder takes it. |
| W2-M282 | Commit hook waits for the whole secrets scan in large stores | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M283 | gov readiness --generate automates gap-ticket creation | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M284 | gov discover, the entry point to discovery | medium | W2-36 | Named in W2-36's KPIs (gov discover). |
| W2-M285 | gov impact answers plain-language impact questions | medium | W2-37 | Named in W2-37's KPIs (gov impact). |
| W2-M286 | No measured governance share for tickets closed with the ticket tool | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M287 | gov doctor reads pytest-xdist as not found (found_version null) while 3.8.0 is installed | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M288 | The doctor judges citations inside adoption records and evidence snapshots (path_compliance a named exception) | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M289 | After a --no-embeddings rebuild the doctor reports a semantic canary miss, not 'semantic index not built' | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M290 | gov doctor exits non-zero on this repository | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M291 | The main session records its writes under the closed ticket DAEO-6cc2; leads run as role orchestrator (DEC-434 unbuilt) | medium | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-M292 | The lexical facet matches a question as one phrase; a plain-word question gets nothing | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M293 | A ticket-tool close changes a ticket file and leaves the store stale (index freshness, recovery/rebuild red) | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M294 | The context-reproducibility result depends on the store it runs on (green on a stale store, red after a rebuild) | medium | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-M295 | git runs no hook on a merge commit: lefthook installs pre-commit and pre-push only | medium | W2-06 | Named in W2-06's KPIs (fast pre-commit tier and re-index). |
| W2-M296 | A question about an id that exists nowhere returns 20 unrelated semantic items and stops with BUDGET_EXHAUSTED_WITH_GAPS at 404 of 6,000 tokens | medium | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-M297 | Vendored SKILL.md sizes sit exactly on their ceilings | medium | backlog | At the ceiling, not over it; a later vendored update re-measures. |
| W2-M298 | Namespace policy fields free text; permitted_roles meaning unconfirmed | medium | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-M299 | Failure, research, decision-package and checkpoint schemas lack type fields | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M300 | New top-level folder fails the namespace coverage check until added | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M301 | Charter, contract and plan load invalid; templates load as records | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M302 | Readiness record lacks profile and capability-type fields | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M303 | OpenSpec does not force readiness before tasks | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M304 | Schema does not hold the five decision-package status values | medium | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-M305 | Nothing writes specification frontmatter; bare gov readiness INVALID | medium | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-M306 | Undecided which tickets each lesson constrains | medium | Wave 3 | Which tickets each lesson constrains is an owner rule for the upstream lesson loop (Wave 3, W2-I018). |
| W2-M307 | Installed projects must ignore .gov-runtime/ and compiled files | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M308 | Doctor hard-codes six registry entries; registry lacks location fields | medium | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-M309 | Record store names three docs invalid for lacking a type key | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M310 | core-schema red: legacy records without state_class | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M311 | Shipped path map invalid against the kernel's path-map schema | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M312 | Adapter generation not run at copy; project-owned .rulesync paths undefined | medium | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-M313 | Project values in skill and briefs are unfilled, unchecked placeholders | medium | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-M314 | Template settings register three hook programs; four more are unregistered | medium | W2-10 | Fits W2-10's paths and KPIs (guardrails explain themselves); its builder takes it. |
| W2-M315 | Each declaring check catches only one kind of violation of its policy | medium | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |
| W2-M316 | Kernel has no record type for an audit report | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M317 | Kernel record type for audit and adoption verdict reports | medium | W2-02 | Named in W2-02's KPIs (record types). |
| W2-M318 | Brief's PYTHONPATH=<clone>/src falls through to installed gov when no src/ | medium | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-M319 | Template path map ships only paths | medium | W2-23 | Fits W2-23's paths and KPIs (adoption safety); its builder takes it. |
| W2-M320 | Rule for a closed specification changed in place | medium | W2-37 | Fits W2-37's paths and KPIs (gov impact); its builder takes it. |
| W2-M321 | Wave 2 role roster | medium | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-M322 | UX role owns UX readiness with approved wireframes and visual tests | medium | W2-35 | Named in W2-35's KPIs (UX readiness row). |
| W2-M323 | W1-01 history test fails on first integration merge | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M324 | Release flock advisory; double-hold fix unproven | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M325 | Latency and p95 cases fail under machine load and pass alone | medium | backlog | Load-sensitive timing cases; W2-20's machine-wide gate lowers the load; otherwise test debt (DEC-136). |
| W2-M326 | Missing-code-index case passes inside a sandbox for the wrong reason | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M327 | W1-16 not-indexed case fails when any session writes a snapshot | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M328 | Shared W1-07 support file makes merge-backs flagged repeatedly | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M329 | W1-46 live-session cases error when run beside other suites | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M330 | Cross-process ordering of the supplementary block untested | medium | W2-04 | Fits W2-04's paths and KPIs (gov context bounded); its builder takes it. |
| W2-M331 | W1-35 and W1-36 suites cannot be collected in one pytest run | medium | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-M332 | p95 latency and time-limit cases fail under machine load | medium | backlog | Load-sensitive timing cases; W2-20's machine-wide gate lowers the load; otherwise test debt (DEC-136). |
| W2-M333 | W1-43's acceptance tests (tests/acceptance/W1-43/) do not exist; the audit-to-repair loop is untested | medium | W2-47 | Named in W2-47's KPIs (Wave 2 exit audit). |
| W2-M334 | File-tool Read/Edit/Write run outside the sandbox | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M335 | Hooks and MCP servers run outside the sandbox | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M336 | EXP-002: untested sandbox cases | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M337 | EXP-002: subagents inside a sandboxed worker session | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M338 | Auto-compaction near 300k tokens never observed live | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M339 | Option prefixes, case variants and =true skip flag pass the launcher | medium | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-M340 | 60% code-intelligence line measured on designer's own questions | medium | W2-15a | Named in W2-15a's KPIs (EXP-003 baseline). |
| W2-M341 | Semantic retrieval hit@5 85 baseline not reached | medium | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-M342 | Retrieval passes with thin margins (MWA-03) | medium | W2-15a | Named in W2-15a's KPIs (EXP-003 baseline). |
| W2-M343 | Skill KPI clauses measurable only by live sessions; unmeasured until W1-42/W1-43 | medium | W2-46 | Fits W2-46's paths and KPIs (Wave 2 exit run); its builder takes it. |
| W2-M344 | Automatic compaction and PreCompact hook output unmeasured | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M345 | Sandbox's added system-prompt tokens not measured | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M346 | Skill, briefs and status route are text only, not shown in a session | medium | W2-11 | Fits W2-11's paths and KPIs (briefs and orchestration skill); its builder takes it. |
| W2-M347 | Other hook programs keep no deadline; harness behaviour at their limit unobserved | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M348 | After a CLI update every log is 'not measured' until a new specimen | medium | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-M349 | instructions and sandbox_instructions lines count nothing | medium | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-M350 | EXP-002: Wave 2 sandbox experiment on untested cases | medium | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-M351 | Scale probes on ~/EXAMIN APP and ~/workspace before Wave 2 | medium | W2-15b | Named in W2-15b's KPIs (EXP-003 final measurement). |
| W2-M352 | Two branches revising one acceptance-test line cannot be merged | medium | backlog | Process: one owner of each acceptance-test file per wave; no tool change needed in Wave 2. |
| W2-M353 | gov close merged before any independent probe of its final code | medium | W2-01 | Fits W2-01's paths and KPIs (gov close and traceability); its builder takes it. |
| W2-M354 | Repair ticket ade-ke2y in a-dev open and incomplete, turning checks red | medium | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-M355 | Live clones under /tmp lost on reboot | medium | W2-50 | Named in W2-50's KPIs (durable scratch root). |
| W2-M356 | Mechanise rules the compliance report shows as instruction-only | medium | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L001 | Held-out path itself is visible to agents | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L002 | No LICENSE in vendored superpowers copy | low | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-L003 | Decision-package choices sources do not fix | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L004 | Permission classes mapped as families | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L005 | No model tier decision; no model frontmatter | low | Wave 3 | Its source places it in Wave 3. |
| W2-L006 | Old gov-launch temp folders in /tmp to clear | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L007 | Read beyond DEC-370 returned a G-17 row | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L008 | Leftover /tmp folders from W1-16 | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L009 | Windows-side claude on WSL PATH left in place | low | W2-22 | Fits W2-22's paths and KPIs (gov doctor green); its builder takes it. |
| W2-L010 | Body edits that keep an approved decision ACTIVE are not flagged | low | W2-12 | Named in W2-12's KPIs (owner approval facts and gov approve). |
| W2-L011 | No hook timeout key in the settings file | low | W2-22 | Fits W2-22's paths and KPIs (gov doctor green); its builder takes it. |
| W2-L012 | Empty mirror means frozen; failing lift refuses | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L013 | Tests wrote six entries into the real gov-os state folder | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L014 | Vendored superpowers skills have no version and are not validated | low | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-L015 | Whether the old cli/ tree is live or archived | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L016 | 'Nothing else shipped in the overlay' is the brief's reading of DEC-493 | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L017 | retrieval-regression red because the dev tiers variable is unset | low | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-L018 | ORION's merge 736669f in the a-dev clone was the lead's, after a red CI | low | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-L019 | HEAD move without before-snapshot checked only against last seen HEAD | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L020 | Snapshot cleanup after one hour undercuts larger pending-snapshot timeout | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L021 | Unusable hook input naming an actor clears that actor's leftover snapshot | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L022 | Acceptance test restore stages pre-call HEAD content into the index | low | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-L023 | Install rule false asks on here-documents and 'install' arguments | low | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-L024 | Orchestrator session keeps the shared temp directory | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L025 | Hidden directories look empty to workers with no error | low | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-L026 | Held-out substring match also denies look-alike siblings | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L027 | Duplicate key in held-out.yaml keeps last value | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L028 | Any truthy dangerouslyDisableSandbox value is denied | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L029 | Ollama serve that never becomes healthy is left running | low | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-L030 | Guard stricter than needed on cp/ln forms | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L031 | Store digest omits frontmatter keys and body; no content_hash | low | W2-03 | Fits W2-03's paths and KPIs (decisions as records); its builder takes it. |
| W2-L032 | Merge commits list no changed paths; renames untested | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L033 | Secret filter edges fail closed or noisily with tracebacks | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L034 | Checkpoint warning after every compaction; same-second and future-time gaps | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L035 | Pending owner decisions not known to the resume hook | low | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-L036 | Resume block parsing edges: trailing text, headings, fences | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L037 | Resume size caps in code points; block unbounded; GOV_TICKET verbatim | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L038 | Hook process edges: orphaned tk, no fsync, exit 120 | low | W2-10 | Fits W2-10's paths and KPIs (guardrails explain themselves); its builder takes it. |
| W2-L039 | Claim holder compared on stripped text; empty lock released by empty holder | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L040 | tasks.create trusts the script's last line and skips the sha256 check | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L041 | Raw exceptions instead of GovError in claims and create | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L042 | Minor lock edges: dangling-link lock, duplicate status, filename keying | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L043 | Orchestrator-only gov checkpoint not enforced by the command | low | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-L044 | --resume brief without --json is indented JSON | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L045 | Launcher builder test uses unbuilt commands as stand-ins | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L046 | gov launch exit code overlaps API-0002 codes | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L047 | Stray command module hard-exit makes gov --help exit 0 | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L048 | Store without graph tables gives raw SQLite error | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L049 | Coarse parents and line numbering in the lexical index | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L050 | lexical.py imports non-exported gov.secrets.CONFIG_REL | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L051 | Carried cli/govbridge code untouched and not ported | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L052 | MR-4 fresh auditor rule rests on orchestrator session rules | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L053 | Readiness taxonomy constants held in code | low | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-L054 | Bridge uses private guard names; globs reaching acceptance not refused | low | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-L055 | Auditor launched on another role's ticket gets no write path | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L056 | Tracked file named by .gitignore silently missing from graph | low | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-L057 | dead_code lists entry points and tests; rename symbol-only | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L058 | Codebase-memory daemon dir under shared /tmp never cleaned | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L059 | Namespace-dependent cases skip without namespaces | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L060 | Suite __pycache__ holds planted secret strings | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L061 | Temp folder removal by name; nonexistent launcher TMPDIR not run | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L062 | Owner-installed tools awaiting tool-registry entries | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L063 | Launch by WBS id sets GOV_TICKET to the WBS id; a repeated key takes the last value | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L064 | Closure 'uncommitted' ends in a traceback when git fails | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L065 | Vectors built before the 512-character cut not detected as stale | low | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-L066 | Reranker worker writes a progress bar and prompt line to stderr | low | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-L067 | Modules import private helpers of other modules | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L068 | Code under test leaves ollama serve running | low | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-L069 | Decision with an empty id is followed as 'None' or '' | low | W2-03 | Named in W2-03's KPIs (decisions as records). |
| W2-L070 | Frontmatter-like heads not read as frontmatter pass silently | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L071 | Deeply nested YAML raises bare RecursionError | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L072 | Dead package without id fails no ticket | low | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-L073 | Clean combination of two orchestrator edits of a ticket file flagged | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L074 | Identical both-sides test change with several merge bases fails closed | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L075 | Whole-move findings that name no path | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L076 | read_merge has no bound for a whole move | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L077 | DEC-182 message-body fallback not used by containment | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L078 | Unseen characters inside a role word read as Role: owner | low | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-L079 | Leftovers under tests/acceptance need the owner to delete | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L080 | Forged snapshot can conjure a freeze | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L081 | Refusal text says 'stays frozen' without asking the guard's reader | low | W2-10 | Named in W2-10's KPIs (guardrails explain themselves). |
| W2-L082 | Rollback reverting a flag-touching commit leaves a dirty tree | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L083 | batch_size of zero or less gives a zero-progress continuation | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L084 | batch_size None and 10 give different continuation tokens | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L085 | MWA-05: CAP-08.a owner and links filters not built (backlog, later wave) | low | Wave 3 | Its source places it in Wave 3. |
| W2-L086 | Canary declarations read from a module-level path | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L087 | Commits without a Role: trailer and with wrong co-author models | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L088 | Missing record file gives default content or hash silently | low | W2-04 | Fits W2-04's paths and KPIs (gov context bounded); its builder takes it. |
| W2-L089 | Four Contract-fixed lists are constants in the check code | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L090 | wbs_to_id in claims.py built and never used | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L091 | Synthesis notes in one file; a second synthesis replaces the first | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L092 | Moved repository gets a new freeze mirror key | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L093 | Launched worker's guard reads only the in-repository flag | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L094 | Hook process writes are not decided by the guard | low | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-L095 | stop.py and subagentstop.py duplicated from template hooks | low | W2-10 | Fits W2-10's paths and KPIs (guardrails explain themselves); its builder takes it. |
| W2-L096 | Not-applicable opt-in read only from a file named after the check id | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L097 | Skill validator checks gov commands against the reserved list, not installed ones | low | W2-11 | Fits W2-11's paths and KPIs (briefs and orchestration skill); its builder takes it. |
| W2-L098 | Two checks of one family over different folders make family status ambiguous | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L099 | judge_commits judges each commit by its own trailers only | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L100 | Scratch checkpoint without head_commit counts zero commits | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L101 | Doctor hashes 1.75 GB of models on every run | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L102 | Rebuild takes about 157 s on a 955-file project | low | W2-15a | Fits W2-15a's paths and KPIs (EXP-003 baseline); its builder takes it. |
| W2-L103 | Rebuild exits 0 when optional indexes are not recreated | low | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-L104 | Recovery check unmeasured on a project never loaded | low | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |
| W2-L105 | Launches leave temporary gov-launch folders in /tmp | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L106 | Yellow families at baseline | low | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-L107 | --disposition finding records no class or context on the repair ticket | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L108 | Close command inserts fields into the ticket tool's frontmatter itself | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L109 | One edit gives many adapter findings | low | W2-05 | Fits W2-05's paths and KPIs (git environment sweep); its builder takes it. |
| W2-L110 | Ticket argument that is a path writes a counter outside the iterations folder | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L111 | Earlier-round probe record refuses beside a passing one | low | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-L112 | Committed conftest.py inside the ticket's own folder runs | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L113 | deviations always 'not measured'; watchdog given no utilisation | low | W2-39 | Fits W2-39's paths and KPIs (model-switch continuity and checkpoints); its builder takes it. |
| W2-L114 | Status read-back after a ticket tool on PATH checks only the status field | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L115 | traceability.py:101 keeps an except Exception | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L116 | Close time limit covers each test run, not the whole close | low | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-L117 | gov ci declares class 'read' though push writes a note (Wave 2 list) | low | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-L118 | Tier selection calls check-runner internals; gov check has no tier option (Wave 2 list) | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L119 | 'Unmeasured' only for pytest, openspec, rulesync | low | W2-19 | Named in W2-19's KPIs (language-agnostic test commands). |
| W2-L120 | Invalid manifest key raises a traceback | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L121 | Doctor on a fresh project mostly unmeasured; reads the real CLI regardless of HOME | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L122 | Lock writer blocks on a FIFO under the kernel | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L123 | Sub-agent instruction files and MCP left out of the estimate | low | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-L124 | Counter takes the larger reading for hook text and compound gov commands | low | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-L125 | Rewrite ordering uses topological log order; agent.harness is a literal | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L126 | Any unloadable Markdown record listed under decision_packages | low | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-L127 | Status imports private functions; a missing mirror folder reads as not frozen | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L128 | Status passes doctor states without reasons and exits 0 when parts unread | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L129 | src/gov/cli/commands/status.py is dead code | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L130 | SIGQUIT/SIGUSR1/SIGKILL or a nohup-ignored signal leaves the session running | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L131 | Launcher exit-code edge cases (130 race, negative code, non-OSError) | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L132 | launch() from a non-main thread raises before starting | low | W2-21 | Named in W2-21's KPIs (stable launch). |
| W2-L133 | Refusal printed to an unwritable stderr ends with a traceback's code | low | W2-10 | Named in W2-10's KPIs (guardrails explain themselves). |
| W2-L134 | First checkpoint record numbered 0002 with no 0001 | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L135 | Containment hook attributes designer's files to the lead's waiting call | low | W2-44 | Named in W2-44's KPIs (trailers bound to launch identity). |
| W2-L136 | Non-UTF-8 byte in serial-only list ends close in a traceback | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L137 | Serial-only entries in undocumented forms double-count or double-run cases | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L138 | test_runs says parallel/workers auto when no worker started | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L139 | close_workers and close_timeout accept odd YAML values and no bounds | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L140 | Unusable parallel plugin counted against the ticket, not 'could not measure' | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L141 | Close inside a parallel worker passes the worker variable to its runs | low | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-L142 | Path map in a small project brings the lexical index into gov rebuild | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L143 | Run-time names (substitution, variables, xargs, find -exec) not held for reads | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L144 | Copies or second names made earlier or via symlinks are not recognised | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L145 | Programs that read the settings file by themselves (claude, rulesync) unseen | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L146 | git -C another checkout with a relative path; cd into a run-time folder | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L147 | Copy reached by glob or search starting above its folder | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L148 | Second names by unknown programs or unparsed options not detected | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L149 | User-level settings file not at the hook's $HOME unprotected | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L150 | Wildcard-only words in non-reader commands; other spellings of 'everything' | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L151 | Shell spellings the token expansion gives up on are allowed | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L152 | bash -c with operator glued to name, eval, here-string into shell allowed | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L153 | Search-tool globs with escapes, braces or comma lists allowed | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L154 | In-place edit that prints (sed -i 'w /dev/stdout') allowed for a writing role | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L155 | Hook-listing helper reveals deny paths for unusual rule shapes or spellings | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L156 | Reading-tool call with list or number path field answered allow | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L157 | Root search built at run time escapes the root-search rule | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L158 | rg may wait on non-terminal stdin; slow matcher shapes; NUL in pattern allowed | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L159 | Held-out check word separation, later-line paths and edit content gaps | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L160 | Hook starts git by name; freeze look-up has no limit of its own | low | W2-05 | Named in W2-05's KPIs (git environment sweep). |
| W2-L161 | Forked decision process escapes or orphans; needs os.fork; SIGCHLD-ignored hook refuses all | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L162 | Duplicate allowed_paths: guard uses the union, close uses the last block | low | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-L163 | Containment shapes: clean ticket-file combination stays a finding; trailerless/owner commits | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L164 | Store/READY edge cases: unclosed front matter, empty reasons, missing edges | low | W2-34 | Fits W2-34's paths and KPIs (gov readiness --generate); its builder takes it. |
| W2-L165 | Close misc: repair-ticket cut by count, findings_cut unset, narrow error catch | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L166 | One gitleaks run can pass the module's own 60 s limit | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L167 | Stated check limit above about 2,147,483 s ends gov check in a traceback | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L168 | YAML spellings of the limit accepted; duplicate or misspelt keys silent | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L169 | gov check --list entries carry a sixth key when the limit is stated | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L170 | File deleted mid-walk or a dangling link makes secrets-indexing red | low | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-L171 | Killed check leaves children; scan unbounded; defaults unpinned; template hooks unchecked | low | W2-45 | Fits W2-45's paths and KPIs (check runner semantics); its builder takes it. |
| W2-L172 | Session-start and pre-compaction hooks import a product package named gov from src | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L173 | Relative PYTHONPATH=src in the session environment brings back src-first resolution | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L174 | CLAUDE_PROJECT_DIR unset or empty makes all seven hook commands exit 2 | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L175 | Trailers check in a worktree without a built store reads ids as unresolved | low | W2-01 | Fits W2-01's paths and KPIs (gov close and traceability); its builder takes it. |
| W2-L176 | Record relabelled as a new type leaves type-selecting checks | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L177 | Type with no schema file not reported unmeasured; id grammars unapplied | low | W2-02 | Named in W2-02's KPIs (record types). |
| W2-L178 | ci/command.py still passes family names the policy rule ignores | low | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-L179 | Dead entries in gitleaks config, doctor's historical paths and a closed ticket | low | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-L180 | Any supplementary lookup failure becomes 'index unavailable' | low | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-L181 | Cursor rule with unquoted globs refuses A8; partial retire refuses too | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L182 | 'Active records' wording vs proof reading every standing record; chat-db proof status-blind | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L183 | Ticket file change between the context's two reads falls back to every id | low | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-L184 | Unnamed artefacts default to KEEP; unbatched entries go into a last batch | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L185 | Batch check ignores file modes; A8 checks the staged tree, not the commit | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L186 | rulesync import verified loosely; frontmatter and headings-only sections lost | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L187 | governance/adoption/** outside inventory; stale decision packages kept | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L188 | Reading the record graph writes .gov-runtime/store.db into the project | low | W2-23 | Fits W2-23's paths and KPIs (adoption safety); its builder takes it. |
| W2-L189 | Adopt tool uses private functions codeintel._graph and doctor's _match_pattern | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L190 | External references: dangling symlink, summary cut, unknown keys accepted | low | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-L191 | Gate rule reads the last commit; uncommitted package changes unseen | low | W2-12 | Fits W2-12's paths and KPIs (owner approval facts and gov approve); its builder takes it. |
| W2-L192 | Project holding both kernel layouts refused until core-authority copies agree | low | W2-23 | Fits W2-23's paths and KPIs (adoption safety); its builder takes it. |
| W2-L193 | Held-out file without permissions and hooks sources can never be green | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L194 | Settings finding does not mention the held-out step | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L195 | RULESYNC_FAILED echoes 500 characters of rulesync error text | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L196 | Multi-version sessions give version 'not measured' with no reason | low | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-L197 | agent.version can be null; the close record carries no version | low | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-L198 | Version pattern accepts non-ASCII digits | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L199 | Log line whose type is a list gives a traceback | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L200 | Unseen attachment type with no version refused with misleading reason | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L201 | Unreadable Bash writes restored after the fact, not prevented | low | Wave 3 | Rests on the unsandboxed orchestrator session or the install rule's spellings; Wave 3 or a non-goal under CAP-25.c. |
| W2-L202 | Guard does not judge WebFetch URLs against the protected-file read rule | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L203 | Agent worktree isolation creates worktrees; SendMessage reaches other sessions | low | W2-09 | Named in W2-09's KPIs (guard tool list). |
| W2-L204 | Extra unjudged path field of Edit or MultiEdit ignored | low | W2-42 | Fits W2-42's paths and KPIs (guard holes); its builder takes it. |
| W2-L205 | A3 does not pin the path map's hash | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L206 | Doctor's 'no namespace embedded' words only under the semantic canary's answer | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L207 | Merge queue with batch testing and automatic culprit split | low | Wave 3 | Merge queue with batch testing is a scale feature; the close bottleneck is met in Wave 2 by W2-38. |
| W2-L208 | Each session's own Claude Code version in the telemetry record | low | W2-07 | Fits W2-07's paths and KPIs (close by ticket class, repair tickets, share); its builder takes it. |
| W2-L209 | gov close leaves its repair ticket untracked, and without role in b-dev | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L210 | gov close residuals: overwritten close record, undeclared escalation folder, unresolved Implements ids | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L211 | allowed_paths written twice: guard reads the union, close reads the last block | low | W2-41 | Fits W2-41's paths and KPIs (close and escalation integrity); its builder takes it. |
| W2-L212 | Lift clean combinations of ticket files in merge commits | low | W2-44 | Fits W2-44's paths and KPIs (trailers bound to launch identity); its builder takes it. |
| W2-L213 | Guard refuses shell words whose brace expansion exceeds a fixed alternative count | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L214 | Lesser guard probe findings from W1-02's last round | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L215 | gov doctor checks hook time limit exceeds guard's own deadline | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L216 | Guard refuses creating the folder of an allowed file | low | W2-42 | Named in W2-42's KPIs (guard holes). |
| W2-L217 | Schema check residuals: new types, depends_on shape, id grammars, success form | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L218 | Dead argument the CI command passes to the policy rule | low | W2-43 | Fits W2-43's paths and KPIs (CI and secret floor); its builder takes it. |
| W2-L219 | Context and gate-check residuals: ticket names, duplicate ids, both layouts, messages | low | W2-04 | Named in W2-04's KPIs (gov context bounded). |
| W2-L220 | Adapter check held-out step residuals | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L221 | A register heading alone suffices as a decision entry | low | W2-03 | Named in W2-03's KPIs (decisions as records). |
| W2-L222 | Hash or signature on the pre-push evidence note | low | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-L223 | Public tier argument of the check runner; tier of tier-less built-in checks | low | W2-45 | Named in W2-45's KPIs (check runner semantics). |
| W2-L224 | gov ci declares its class as read | low | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-L225 | actions/checkout bump off Node 20 in workflow and template | low | W2-43 | Named in W2-43's KPIs (CI and secret floor). |
| W2-L226 | Show open gate records in gov status | low | Wave 3 | gov status accuracy; not on the adoption or exit path; Wave 3. |
| W2-L227 | Copying template/ directly writes no framework.lock | low | W2-16 | Named in W2-16's KPIs (hash-pinned releases). |
| W2-L228 | gov --help says check is 'not built yet' | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L229 | gov.guard.heldout --help has no help and executes | low | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-L230 | Session-start and pre-compaction hooks still import a product's own gov package | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L231 | Hook residuals: relative PYTHONPATH=src, unset CLAUDE_PROJECT_DIR, unverified variable passing | low | W2-18 | Named in W2-18's KPIs (pinned install). |
| W2-L232 | Secrets-scan time-limit and parallel-scan residuals | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L233 | Ranked lexical route for exact identifiers | low | W2-13 | Named in W2-13's KPIs (RETR-X-02 and ranked lexical route). |
| W2-L234 | CAP-08.a owner and links filters | low | Wave 3 | Its source places it in Wave 3. |
| W2-L235 | Trailer findings outside DEC-717 (20 register commits and two closes without Role:, wrong co-author, wrong Task:) | low | W2-01 | Named in W2-01's KPIs (gov close and traceability). |
| W2-L236 | Repair tickets DAEO-52q7 and DAEO-ldvk moved out of .tickets/ into the orchestrator's scratch log | low | W2-07 | Named in W2-07's KPIs (close by ticket class, repair tickets, share). |
| W2-L237 | gov --help says running the checks is not built | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L238 | A launched session sees eleven dot-files at its project root as untracked files | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L239 | ADR-0002 and W1-18 ticket text say gov stops Ollama; it does not | low | W2-32 | Named in W2-32's KPIs (retrieval components and bounded improvements). |
| W2-L240 | Ticket schema requires only kpis, role, allowed_paths | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L241 | Record status is any non-empty string; ticket type unpinned | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L242 | Id grammars undecided except lesson_id; link fields have no grammar | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L243 | Committed ADRs lack state_class | low | W2-02 | Named in W2-02's KPIs (record types). |
| W2-L244 | Four unnamed edge keys need checking against Framework 11.2 | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L245 | blocked can return an empty reason list; cannot-be-read code needs decision | low | W2-34 | Fits W2-34's paths and KPIs (gov readiness --generate); its builder takes it. |
| W2-L246 | feature-readiness vs readiness naming mismatch with G-07/G-08 | low | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-L247 | validate --strict ignores proposal, design, tasks and readiness | low | W2-34 | Named in W2-34's KPIs (gov readiness --generate). |
| W2-L248 | Package rules live in an HTML comment authors delete | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L249 | Launcher refuses any --setting-sources and guard only in settings.local | low | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-L250 | Roster header comment stale | low | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-L251 | Product-spec role file and agent definition say launcher cannot start it | low | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-L252 | Product-spec role file and agent definition say the launcher does not start it | low | W2-33 | Named in W2-33's KPIs (Wave 2 roles and handoffs). |
| W2-L253 | template/** not embedded because of the path-map value | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L254 | L-0074 written from register entries, not an original lesson text | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L255 | gov --help shows ci, launch, telemetry beyond the twelve reserved names | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L256 | Loose citations in the orchestration skill | low | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L257 | Launcher command in a code span in brief-lead.md and the role file | low | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L258 | Five brief templates have no record frontmatter or schema | low | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L259 | Repository orchestrator prompt still duplicates the rules in the skill | low | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L260 | Kernel path-map schema lacks close_workers and close_timeout | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L261 | Ticket schema's second form admits any id grammar for depends_on | low | W2-02 | Fits W2-02's paths and KPIs (record types); its builder takes it. |
| W2-L262 | Documents still point to cli/ as present | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L263 | carried-code namespace keeps the cli/** pattern and retention text | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L264 | Adoption auditor findings: dead cli/ references, skipped unit case, uninventoried stage records | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L265 | gov adopt --lite needs --stage and a clean tree | low | W2-23 | Named in W2-23's KPIs (adoption safety). |
| W2-L266 | ARGUS audit's major finding: retention input contract (created_at, now, aware datetimes) | low | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-L267 | Form of a project audit report against the kernel audit validator | low | W2-02 | Named in W2-02's KPIs (record types). |
| W2-L268 | The W1-43 brief did not state DEC-430 | low | W2-11 | Named in W2-11's KPIs (briefs and orchestration skill). |
| W2-L269 | Unasserted Ollama engineer choices and test designer readings | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L270 | Vendored file modes not asserted | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L271 | Open maps accepting extra keys are untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L272 | Untested W1-08 schema points | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L273 | DEC-182 boundary date and timezone untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L274 | STORE_MISSING, STORE_GIT_FAILED and CAP-08.a owner/links filters untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L275 | Unknown schema in config.yaml untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L276 | DEC-321 watchdog defaults unasserted by acceptance; thresholds unchecked | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L277 | No acceptance test that a new module alone adds a command | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L278 | TASKS_NOT_FOUND and TICKET_FAILED untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L279 | Untested wrapper refusals | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L280 | W1-16 README fifth-batch section stale | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L281 | Pause behaviours that are built but held by no test | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L282 | Callees in the closure wrapper are thinly tested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L283 | Closure cases missing for homonym symbols, methods and referenced_by on gaps | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L284 | W1-07 closure cases exercise only STORE_MISSING | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L285 | Offline reranker loading checked only where the snapshot is absent | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L286 | Overlapping ids tested only for identical digit strings | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L287 | Stale docstrings and READMEs in acceptance suites | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L288 | local_only mark not registered for the W1-50 folder | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L289 | MWA-04: W1-03's 'and at gov close' is untested | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L290 | MWA-06: W1-10 load-time line runs only where the dev tiers are configured | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L291 | MWA-08: W1-01's deny in every session settings file shown by presence only | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L292 | 'Lesson restates policy as authority' checked by fields, not prose | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L293 | Case rewrite mislabelled 'owner correction' | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L294 | Loose kernel-listing case; no case for an unreadable answers file without a lock | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L295 | W1-46 shared live research session gives setup errors in parallel runs | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L296 | W1-36 helper accepts any PYTHONPATH containing the src path as a substring | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L297 | W1-27 run_python_snippet and one 30 s wait keep the old bound | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L298 | W1-07 30 s read-command wait exceeded under ten workers | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L299 | Prefixes, keywords and redirects not held by any case | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L300 | No cases for NUL in edit path, one-character home, other variables | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L301 | W1-30 skipped-only-case test failed under load (inner close time limits) | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L302 | Stale READMEs and docstrings, never-red case, blind spot, worker slips | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L303 | No case holds that the harness passes CLAUDE_PROJECT_DIR as env, not text | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L304 | W1-38 helper returns none for subagentstop.py; repo hooks source unpinned to template | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L305 | W1-46 live network case fails intermittently in the serial run | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L306 | Unit case test_lexical.py skips for good now that its origin is gone | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L307 | Stale W1-26 README count; a killed background script leaves its pytest child | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L308 | W1-26 policy-key case still expects human_gate among owed keys | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L309 | No case for empty held-out list or unreadable file | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L310 | W1-33 research-definition case skips where rulesync is absent | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L311 | W1-49 session case skips outside a session and cannot tell export from user entry | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L312 | W1-28 copying-helper list omits W1-33's copy_adapter_source | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L313 | Containment count of an allowed MultiEdit held by a unit case only | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L314 | W1-49 live-session case asks a small model to repeat four facts | low | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-L315 | CAP-56's transcript acceptance (bundle, no intermediate batch) is tested on the skill text only | low | W2-47 | Named in W2-47's KPIs (Wave 2 exit audit). |
| W2-L316 | EXP-002: excludedCommands behaviour | low | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-L317 | 2.8 s scale KPI held as 10 s; G-20 not read | low | W2-15b | Named in W2-15b's KPIs (EXP-003 final measurement). |
| W2-L318 | Loopback UI port lingers; any call creates config; cost unmeasured | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L319 | Closure depth numbers per radius are placeholders | low | W2-37 | Named in W2-37's KPIs (gov impact). |
| W2-L320 | Vectors use a brute-force cosine scan, unmeasured beyond the dev tiers | low | W2-15b | Named in W2-15b's KPIs (EXP-003 final measurement). |
| W2-L321 | Rerank process RAM margin is about 0.2 GB | low | W2-15a | Named in W2-15a's KPIs (EXP-003 baseline). |
| W2-L322 | Two dev queries lack gold paths; deletable class stuck at 40 | low | W2-15a | Named in W2-15a's KPIs (EXP-003 baseline). |
| W2-L323 | Pause from a sandboxed session with a mounted flag path fails (inferred) | low | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-L324 | Share denominator slightly low, so the share reads slightly high | low | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-L325 | Seven log forms 'not measured' until a fourth specimen shows them | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L326 | Four passed-over types are known by type and length only | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L327 | Decide whether instructions/sandbox_instructions log lines replace the static estimate | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L328 | Deadline for post-call hook programs, after an experiment on harness behaviour | low | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-L329 | Spike a lighter reranker to replace Qwen3-Reranker-0.6B | low | W2-15a | Named in W2-15a's KPIs (EXP-003 baseline). |
| W2-L330 | Live store writer rule to revisit when gov rebuild is wired | low | W2-06 | Fits W2-06's paths and KPIs (fast pre-commit tier and re-index); its builder takes it. |
| W2-L331 | Test designer left throwaway reference implementation outside repo | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L332 | W1-50 KPI wording not amended for DEC-410 DP-24 and DP-26 | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L333 | MWA-07: four changes outside a ticket's paths | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L334 | Old automatic checkpoint records left untracked under docs/checkpoints | low | backlog | Low edge case; no Wave 2 exit criterion depends on it; taken up when its module is touched. |
| W2-L335 | core-decision-citations yellow with 10 findings from unmerged decisions | low | W2-08 | Named in W2-08's KPIs (hooks back on). |
| W2-L336 | pytest-xdist checksum mismatch in tool registry | low | W2-22 | Named in W2-22's KPIs (gov doctor green). |
| W2-L337 | Lesser findings of the ORION and ARGUS exit audits | low | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-L338 | Outward actions (pushes, hook installs and uninstalls) recorded only after the fact | low | Wave 3 | Recording outward actions before they happen needs the Wave 3 claims and session work. |
| W2-L339 | 19 amends of merge commits on w1/integrate (2026-10-07 to 2026-10-14); standing rule: never amend | low | backlog | Held by the standing rule (DEC-718 item 8; plan rule 2): no commit on an integration branch is amended. |
| W2-L340 | COMPLIANCE.md stale since 2026-10-07, with wrong base counts | low | W2-46 | Fits W2-46's paths and KPIs (Wave 2 exit run); its builder takes it. |
| W2-L341 | ORION's programme test test_exact_agreement fails before and after ORION-im02 | low | W2-14 | Named in W2-14's KPIs (ARGUS cycle and share). |
| W2-I001 | Sandbox cost and whether its tokens count toward the governance share | info | W2-40 | Named in W2-40's KPIs (EXP-002 and harness limits). |
| W2-I002 | Path-map capability values for this repository are the implementer's | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I003 | fixtures/** is the only product namespace | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I004 | stores_with_secrets second scan stricter than DEC-347 | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I005 | Lesson severities and lifecycles chosen by the worker | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I006 | Whether acceptance tests should be embedded (adapters, repository, tests took 'not embedded' by the lead's reading) | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I007 | Held-out rule exceeds 100 ms budget at about ten thousand paths | info | Wave 3 | Held-out and oracle hardening; Wave 3, before qualification runs (CAP-49). |
| W2-I008 | CAP-24 version for vendored skills read from vendored.yaml | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I009 | Store load replaces only its own five tables | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I010 | Root gitleaks allowlist reconstructed by the lead | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I011 | Experiments root fixed as experiments/ | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I012 | Sandbox placeholder dotfiles and docs/source show as untracked in worktrees | info | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-I013 | Unexplained single failure of the collect-only unit case | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I014 | gov adopt without --lite is NOT_IMPLEMENTED | info | W2-23 | Fits W2-23's paths and KPIs (adoption safety); its builder takes it. |
| W2-I015 | Reason order for an unknown tool meeting older rules | info | W2-09 | Named in W2-09's KPIs (guard tool list). |
| W2-I016 | A3's embedding check answers before its --map check | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I017 | Independent adoption gates A7, A10, A11 and the final verdict (Wave 3) | info | W2-49 | A7, A10 and the verdict come into Wave 2, lite, by Contract v4.2 (DEC-722); A11 stays in Wave 3. |
| W2-I018 | Upstream lesson loop, lite form (Wave 3) | info | Wave 3 | Its source places it in Wave 3. |
| W2-I019 | Full claims and concurrency, the claims role and gov claim (CAP-23.b, Wave 3) | info | Wave 3 | Its source places it in Wave 3. |
| W2-I020 | G-22 text exists only in archived sources | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I021 | Kernel templates/openspec/ folder holds nothing | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I022 | Unpinned pause error codes and flag mode | info | Wave 3 | Pause and freeze hardening; no Wave 2 exit criterion depends on it; Wave 3. |
| W2-I023 | Lessons are HISTORICAL records, not authority | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I024 | Full research lifecycle CAP-32 (Wave 3) | info | Wave 3 | Its source places it in Wave 3. |
| W2-I025 | Wave 3 role roster | info | Wave 3 | Its source places it in Wave 3. |
| W2-I026 | W1-20 suite takes about four and a half minutes | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I027 | One case holds both hit@5 KPI lines | info | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-I028 | Six of 18 cases are pins and the round 4 README is outdated | info | backlog | Test-quality debt; taken up when a ticket touches that suite (DEC-136). |
| W2-I029 | A single-file adapter-source copy helper counts as exercised | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I030 | Before-snapshot adds about 28 ms to every Bash PreToolUse | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I031 | Untracked placeholder files at worktree root during sessions | info | W2-21 | Fits W2-21's paths and KPIs (stable launch); its builder takes it. |
| W2-I032 | Approval rule judged nothing on this repository | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I033 | Not probed: other parallel plugin versions, huge worker counts, nested close | info | W2-19 | Fits W2-19's paths and KPIs (language-agnostic test commands); its builder takes it. |
| W2-I034 | Harness identity rests on log form and ccusage only | info | backlog | Observation; recorded, nothing to build in Wave 2. |
| W2-I035 | Not probed: real session log, real 2.1.296 log, gov close end to end | info | W2-24 | Fits W2-24's paths and KPIs (Track A gate run); its builder takes it. |
| W2-I036 | Not probed: launcher rules binding subagents and sandbox; research launch | info | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-I037 | Not probed: real MultiEdit, real subagent start, real skill inline shell | info | W2-40 | Fits W2-40's paths and KPIs (EXP-002 and harness limits); its builder takes it. |
| W2-I038 | Local gpt-oss T1 model, deferred to Wave 3 model routing | info | Wave 3 | Its source places it in Wave 3. |
| W2-I039 | Wave 1 tickets built by unsandboxed workers | info | backlog | Observation; W2-21's launch records and EXP-002 (W2-40) bear on it; nothing to build. |
| W2-I040 | Systematic size overruns against ticket estimates | info | backlog | Observation; the plan's estimates carry a 30 % contingency for it (§4). |
| W2-I041 | The harness refuses edits of a clone's local exclude file and git init inside its git folder; the bare remote stands under target/ | info | W2-26 | Named in W2-26's KPIs (EXAMIN profile). |
