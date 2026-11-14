# Brief: independent auditor, W2-184 (DAEO-6f0s): the narrow independent check of R1-R3 (DEC-1180 (4), DEC-1154)

You are a fresh, read-only independent auditor (Opus, effort high). This is **not** a review round: the FULL ticket's
two rounds are done (DEC-1010), and the narrow check after round 2 passed with three findings F1-F3
(`docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`; read it). The CTO reopened the ticket under the owner's standing rule
DEC-1180 (4) ("a defect spotted is fixed in the same flow") to fix F1-F3 as KPI lines R1-R3. DEC-1154: a change made
after a ticket's review gets a narrow independent check of that change only, and the ticket lands on it. Check **only**
this change (since the merged base bbe1510f899b4599222a1cfc6939bf13b5350222), at the head named, against R1-R3, the interface's section 10 (at the
end, word for word), the rule **"nothing refused before becomes allowed"**, and the judgement rules (below, word for
word). Write no file of any repository; run probes only in your session's own `$TMPDIR` (`git archive` copies,
fixtures). Re-run no whole suite. Use your audit skill.

## What to check
- Tree (read-only): /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. **Head to check: 90e657a3583bf4e8edfd40e69a0591e981097dfa.** The change:
  `git diff bbe1510f899b4599222a1cfc6939bf13b5350222 90e657a3583bf4e8edfd40e69a0591e981097dfa` (bbe1510f899b4599222a1cfc6939bf13b5350222 is the merge of w2/integrate before R1-R3).
- **The test designer's cases** (19324ca4b, merged at bf7b93bcf): `tests/unit/launch/test_w2_184_r_fixes.py` (new,
  `test_r1_*`, `test_r2_*`, `test_r3_*`) and two cases of `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py`
  revised to R3 (`Rewrite-Reason: DEC-1180 (4), rv-f1 F3`).
- **The engineer's change:** f2f76a154 (`src/gov/launch/command.py`, `src/gov/launch/launcher.py`, `src/gov/launch/record.py`, `docs/changes/W2-184-CIT-E.md` section 9, `tests/unit/launch/test_w2_184_r_engineer.py`) and 90e657a35 (two earlier builder unit cases of P-td5-2 in `tests/unit/launch/test_w2_184_launch.py` revised to 10.3); `git show` each.
- The ticket /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (KPI lines R1, R2, R3 and its last
  paragraph); DEC-1180, DEC-1154, DEC-1010, DEC-1120 (3) in
  /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md (read each by id).
- Evidence the lead has: the full verification at 90e657a35 GREEN (8,118 tests, 0 failed, 29 skipped); `gov accept W2-184` 507/507, outcome pass, at 90e657a35; the unit file `test_w2_184_r_fixes.py`
  with `test_w2_184_r_engineer.py` and `test_w2_184_launch.py`: 218 passed at 90e657a35 (`gov accept` collects only `tests/acceptance/W2-184/`, so R1 and R2's cases are run directly, as the KPI
  lines' Verify says).

## What to probe (at least)
- **R1:** a lead launch (`orchestrator`, `lead`) with each of `--reason`, `--trial`, `--owner-named`, alone and
  together, empty values too: exit 2, the message, nothing started, no record, the gate not consulted, no
  plan-override line. The same words after `--` for a lead: as before. A lead launch without them, and worker launches
  with them: unchanged. The direct `launcher.launch` call with a lead role and an option: refused.
- **R2:** `record.write`: kill or fail at each step (create, write, fsync, link, temp removal): never an empty or
  partial `<session_id>.json`; a leftover temp file is never read as a record nor refuses a launch nor blocks a later
  write; no overwrite of an existing final name; two writers: one whole record, the other refused as "already there".
  Any reader of the record folder (`record.read` for `--resume`, `_launch_records`, anything else that lists it) that
  could take the temp file as a record? A file system where hard links fail (if the code falls back to something):
  is that fallback still non-overwriting?
- **R3:** differing copies of one probe-record path under several roots: a fail-open finding in any copy promotes;
  one path is one review (no false "two failed reviews" from two copies); identical copies once; a copy that refuses
  (YAML, verdict block) still refuses; the record named is the root-relative path.
- **Nothing refused before becomes allowed:** compare bbe1510f899b4599222a1cfc6939bf13b5350222 and 90e657a3583bf4e8edfd40e69a0591e981097dfa for every refusal the change touches.
- Do the new cases fail when the code does not do what they claim (a mutant or two in a `git archive` copy is enough)?
- Anything outside R1-R3 is out of scope: do not re-open rounds 1 and 2, or the earlier narrow check's settled points.
- Do not open, list or read anything under the evaluation sets' fixtures or any hidden folder.

# Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.
- **How reviews converge (owner, standing, DEC-1010 item 1; in force for the CTO, every lead, reviewer and QA engineer):**
  - **A moderator, not a circle of reviewers:** the QA engineer (or the Senior Engineer; until the three layers start, the CTO) triages every finding against the ticket's own scope and KPIs. A finding outside the scope, or one that needs an unusual construction, becomes a Wave 3 row, never a round.
  - **A finding blocks only if it is in scope, reachable in ordinary work, and fails open or loses work.** Everything else lands as a recorded row.
  - **At most two review rounds.** If something still blocks after that, it goes to the owner once, with options; no more routine exceptions.
  - **READY is computed by code, not declared by an agent:** each reviewer returns a structured verdict per KPI line, a fenced `verdict` block in the probe record: `{"kpis": [{"kpi": "<line id>", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}`; the close (and the merge queue's pre-check) computes READY from it: no finding that is in scope, ordinary work yes and fails open or loses work. A lead never writes a verdict over a reviewer's.

# Your record (your last message; the lead commits it as docs/probes/DAEO-6f0s/PR-DAEO-6f0s-r.md)
Return, as your last message, the record's body in Markdown (the lead adds the front matter):
1. A title line `# Narrow check of DAEO-6f0s (W2-184) R1-R3: judgement pass|fail`, then the head you checked (full
   hash), your session's role, model and effort, and what you ran (commands, fixtures in `$TMPDIR`).
2. `## Findings`: each finding with an id (F1, F2, ...), the KPI line (R1, R2, R3), what you saw (file:line, the probe
   and its output), and its lines: `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
   `Scope: in|out`.
3. `## Per KPI line`: R1, R2, R3: pass or fail, one paragraph each.
4. The fenced verdict block, exactly in this form (JSON), one entry per KPI line:
```verdict
{"kpis": [{"kpi": "R1", "verdict": "pass", "findings": []}, {"kpi": "R3", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
5. A last line: `judgement: pass` or `judgement: fail` (fail only when a finding is in scope, ordinary work yes, and
   fails open or loses work).
Then, after the record, the twelve fields, each a labelled line: task: / status: / work_completed: / files_changed: /
evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments and section 10, R1-R3)

# W2-184 (DAEO-6f0s): the interface (DEC-1052), one text for the test designer, the engineer and the reviewer

The CTO adopted W2-60a run 4d's proposal at claim (DEC-1157, commit b624fa3c1). This text states it whole, with the
points run 4d left open settled by the ticket lead (each marked **[settled]**). The KPI lines S1-S5 and F1 are the
ticket's (`.tickets/DAEO-6f0s.md`). Governing: DEC-1120 (RUBRIC-2), DEC-1119, DEC-1167 (2), DEC-1126 (3), DEC-839,
DEC-1010, DEC-1014 item 1.

Nothing here changes W2-60a's reviewed core (the role text, the skills, the record's base fields, no compaction, the
refused arguments) or `gov launch --plan`, which keeps printing the role file's `Launch default` line alone
(DEC-1167 (2)). A lead launch (`orchestrator`, `lead`) reads no role file and is untouched. **Every existing suite
stays green:** a fixture project with no `criticality.yaml` launches exactly as before, whatever its role files and
records (rule 1.4 below, as amended on 2026-11-14).

## 1. `governance/project/criticality.yaml` and `gov.launch.criticality`

1.1 The file (YAML, read with `gov.guard.heldout.load_yaml_unique`, so a key written twice is malformed):
```yaml
version: 1
default: C2                 # the class when no rule matches
opus: claude-opus-5-5       # [settled] the Opus model a promotion and a FULL ticket's probe use
rules:
  - class: C3
    paths: [".claude/hooks/*", "src/gov/guard/*", ...]   # globs
  - class: C2
    profile: FULL
```
Form: a map with exactly the keys `version` (the integer 1), `default` (one of C0, C1, C2, C3), `opus` (a model id
matching `claude-opus(-[a-z0-9]+)+`) and `rules` (a list, may be empty). Each rule is a map with `class` (C0..C3) and
exactly one of `paths` (a non-empty list of non-empty strings) or `profile` (one of FULL, STANDARD, LITE); no other
key. Anything else is malformed.

1.2 `ticket_criticality(root, ticket) -> str` in `src/gov/launch/criticality.py`: `root` a Path, `ticket` the ticket's
front-matter map as `gov.guard.decide._load_ticket(str(root), id)` returns it. The ticket's criticality is the highest
class (C3 > C2 > C1 > C0) among the rules that match; `default` when none matches. A `profile` rule matches when the
ticket's `profile` equals it. A `paths` rule matches when any of its globs matches any of the ticket's `allowed_paths`.
**[settled]** Matching: each allowed path first loses a trailing inline comment (`\s+#.*$`; the ticket loader keeps
it, e.g. `docs/probes/DAEO-6f0s/**  # the probe record`); a glob and an allowed path match when either, read as an
`fnmatch.fnmatchcase` pattern (`*` crosses `/`), matches the other as a string (so a broad allowed path such as `src/**`
matches the rule glob `src/gov/guard/*`). The ticket's `class` key is never read (it is the ticket's kind).
Also: `opus_model(root) -> str` (the file's `opus`). Both read the file each call (no cache).

1.3 An unreadable or malformed file (and a missing one where `--trial` needs it, or where `ticket_criticality` or
`opus_model` is called directly) raises `GovError("LAUNCH_REFUSED", ...)` naming
`governance/project/criticality.yaml`.

1.4 **[settled; amended by the lead on 2026-11-14 before review, replacing the earlier 1.4]** RUBRIC-2's choices run
on the project's `criticality.yaml`.
- **File present:** it is read on every worker launch; unreadable or malformed refuses, naming it (1.3); sections
  2.3, 4.3, 5 and 6 apply as written.
- **File absent:** the launch is as before W2-184 (DEC-1167 (2): an adopted repository with no file, such as EXAMIN's
  copy, launches on each role's `Launch default` line). The role's `Launch default` line serves every role and class
  (a `Launch by criticality` line is still read, and a malformed one still refuses, but it is not applied); no
  promotion (section 5); no review count, no probe and no same-setting refusal (section 6); `criticality`,
  `promotion` and `review_round` are null; `model_source` and `effort_source` are `role default` or `after --`.
  Still applied with no file: a model after `--` other than the resolved (default) one is refused naming both (4.1);
  the floor and max/`--reason` (3.1, 3.2, 3.2a), judged on the default line's effort; the forms of `--reason`,
  `--trial` and `--owner-named` (section 9); `effort_reason` and `owner_named` recorded. `--trial` with no file is
  refused, naming the file (a trial needs the ticket's criticality).
- Why the amendment: under the earlier 1.4, a project with the kernel role files (whose engineer and test designer
  files carry a `Launch by criticality` line) and no `criticality.yaml` refused every engineer and test designer
  launch: 76 cases of W1-28's, W1-32's, W1-46's and W1-50's suites, and any adopted repository, against
  DEC-1167 (2). It also keeps W2-60a's two-auditor fixture launching.

1.5 The project's own file: `rules` written from DEC-1120 (1): C3 the guard (`src/gov/guard/*`, `.claude/hooks/*`),
permissions, the path map (`governance/project/path-map.yaml`), hidden sets, the operator agent
(`governance/project/operator/*`), the kernel (`template/governance/kernel/*`, `governance/kernel/*`) and the Contract
(`docs/contract/*`); C2 product code (`src/*`), launch, gate and plan, test maps (`governance/project/test-map.yaml`),
schemas; C1 records and docs (`docs/*`, `governance/project/orchestration/*`); plus `{class: C2, profile: FULL}`;
`default: C2`. This ticket (DAEO-6f0s: FULL, `src/gov/launch/*`) resolves to C2.
**[amended by the lead on 2026-11-14 after review round 1, F1 and F8]** The C3 rule also holds, at the least:
hidden sets `fixtures/evaluation/*/hidden/*` (the path map's hidden halves, `governance/project/path-map.yaml`; F1),
and for permissions `.claude/settings.json`, `.claude/settings.local.json`, `governance/project/secrets.yaml` and
`governance/project/indep-walls/*` (F8), beside `governance/project/held-out.yaml`. So a ticket whose
`allowed_paths` name `fixtures/evaluation/<set>/hidden/**` resolves to C3, also with a `docs/probes/<id>/**` path
beside it (highest class wins).

## 2. The role file's lines (`src/gov/launch/role.py`)

2.1 `- **Launch default:** model <model>, effort <effort>` stays as W2-60a reads it (required, once).

2.2 `- **Launch by criticality:** <entry>; <entry>; <entry>; <entry>` (optional, at most once), the four entries for
C3, C2, C1, C0 in that order, each once, separated by `; `. An entry is either
`C<n> model <model>, effort <effort>` or the FULL form
`C<n> model <model>, effort <effort> on FULL, model <model>, effort <effort> otherwise`
(as `template/governance/kernel/roles/qa-engineer.md` writes its C2). `<model>` and `<effort>` as the default line's
(efforts: low, medium, high, xhigh, max). A line of another form (a class missing, twice or out of order, a bad model
or effort, a second such line) refuses the launch with LAUNCH_REFUSED naming the role file and the line's form.

2.3 Choosing the table line: a role file with a `Launch by criticality` line takes the entry of the ticket's
criticality (the FULL form: its first pair when the ticket's `profile` is FULL, else its second) and the source is
`by criticality`; a role file with none takes its `Launch default` line for every class and the source is
`role default`. This pair is **the table's model and effort**.

## 3. Effort: the floor, max and `--reason`

3.1 **[settled]** The floor: when the table's effort is high, xhigh or max, an effort after `--` of low or medium is
refused with LAUNCH_REFUSED naming the given effort and the floor "high" (DEC-1120 (3)). When the table's effort is low
or medium (C0, or a fixture's default) there is no floor.

3.2 Max: an effort of max that is the launch's own choice (after `--`, or a trial's) is refused unless `--reason
"<text>"` (non-empty after stripping) is given. A max that the table itself names (the role file's line) or that a
FULL ticket's probe sets (section 6) needs no reason. **[settled]**: so existing fixtures whose role default is max
still launch.

3.2a **[settled, amended by the lead on 2026-11-14 before review]** A max given after `--` that equals the effort
already resolved for this launch (the table's max, or the probe's max on a FULL ticket's round 2 or later) is not the
launch's own choice: it needs no `--reason`. Only a max after `--` that differs from the resolved effort, or a trial's
max, needs `--reason`. When the given max equals the probe's, `effort_source` is `probe`; when it equals the table's,
`after --` (section 8's precedence). Why: `launch_worker.sh` and every scripted launch pass `--effort` after `--`;
without this, a FULL ticket's probe could not be launched through `gov launch` while `--reason` is not yet a
`gov launch` option (7.2).

3.3 `--reason` is recorded as `effort_reason` (else null), whatever the effort.

## 4. The model: the tier, after `--`, `--trial`

4.1 The session's model is the table's, unless a promotion (section 5), a probe (section 6) or a trial (4.3) sets it.
A model after `--` that is not the session's resolved model is refused with LAUNCH_REFUSED naming both models (the given
and the resolved), unless a trial admits it. A model after `--` equal to the resolved one is accepted.

4.2 `tier` is the family word of the session's model: the second hyphen-separated part of its id (`claude-opus-5-5`
gives `opus`; `claude-haiku-4-5-20251001` gives `haiku`).

4.3 `--trial <id>`: `<id>` matches `[A-Za-z0-9][A-Za-z0-9._-]*` (else refused); the launcher reads
`governance/project/trials/<id>.yaml` under the launch root (`load_yaml_unique`), a map holding exactly:
```yaml
role: engineer               # the launch's role
criticality: C2              # the ticket's criticality (section 1)
model: claude-haiku-5-5      # the trial's model
effort: high                 # the trial's effort
tickets: [DAEO-aaaa, DAEO-6f0s]   # two or more distinct ticket ids, this launch's ticket among them
reviewer:
  model: claude-opus-5-5     # an Opus model (claude-opus-...): the trial's judge
```
The trial admits the launch only when every field is present and well formed and `role`, `criticality` and `tickets`
fit this launch; else LAUNCH_REFUSED naming the trial file and the field that does not fit (missing file, unreadable,
malformed: refused, naming it). Admitted: the session's model and effort are the trial's; a model or effort after `--`
that differs from the trial's is refused naming both; `model_source` and `effort_source` are `trial` and `trial` holds
the id. **[settled]** A trial's effort below the floor is accepted (the trial is the recorded exception to the table);
a trial's max needs `--reason` (3.2). A trial on a ticket where a promotion applies is refused (5.3).

4.4 The subagent model (`CLAUDE_CODE_SUBAGENT_MODEL` in the settings' env, and the record's `subagent_model`) is the
session's final model, whatever set it.

## 5. Promotion from the probe records

5.1 The ticket's probe records are the `.md` files under `docs/probes/<ticket id>/` of the launch root, at any depth,
in sorted path order. A file's front matter (between its first two `---` lines) that is not YAML refuses the launch
naming the file; a file with no front matter or whose front matter is not a map with `type: probe` is skipped.

5.1a **[amended after review round 2, the owner's P-W2-184-1 (a), DEC-1010]** The probe records are also read under
each worktree root that the ticket's launch records name: every file in the shared record folder
(`gov.launch.record.folder(root)`) with `record: gov-launch` and a `ticket` that is one of the ticket's names (the id
the launch was given, its `id`, its `wbs_id`), any role, gives its `root`. A named root that no longer exists (or is
not a folder) is skipped. A record file there that cannot be read as JSON refuses the launch naming it (as 6.1). The
records found are one set by their root-relative path (`docs/probes/<name>/...`): a path present under two roots
counts once, the launch root's copy first, then the other roots in sorted order; 5.2's "sorted path order" and its
`record` path are over that set (the path stays root-relative). With no probe record under any root, the launch is as
before. Nothing that refuses today stops refusing. **[settled, td-5]** (P-td5-1) In a project with a
`criticality.yaml` every launch reads the record folder for the roots, so a record file there that is not JSON refuses
it even when no probe record exists anywhere (fail closed: a skipped record could hide a promotion); with no
`criticality.yaml` nothing is read (1.4). (P-td5-2) For a path under two roots the launch root's copy counts, else the
first other root in path-sorted order.

5.2 A promotion applies when (a) a record holds a fail-open finding: a fenced ```` ```verdict ```` block (JUDGEMENT.md's
form, JSON: `{"kpis": [{"kpi": ..., "verdict": ..., "findings": [{"id": ..., "consequence": "fails open|loses
work|other", ...}]}]}`) with any finding whose `consequence` is `fails open` (a verdict block that is not JSON of that
shape refuses, naming the file); or (b) two or more records have `judgement` fail or failed. **[settled]** (a) is
checked first. The reason is the text `a fail-open finding` or `two failed reviews`; the record is the root-relative
path of the first record holding a fail-open finding, or of the second failed record, in sorted path order.

5.3 A promotion sets the session's model to `criticality.yaml`'s `opus` at the table's effort (or the probe's,
section 6), for every worker role launched on that ticket. Recorded: `model_source: "promotion"` and
`promotion: {"reason": <text>, "record": <path>}` (else `promotion: null`). A model after `--` other than the Opus model
is refused naming both; `--trial` is refused ("a lower model is refused", DEC-1120 (3)).

## 6. A FULL ticket's two reviews (S4; run 4d's S10)

6.1 For a launch of `independent-auditor` on a ticket whose `profile` is FULL, the launcher counts the launch records
in the shared record folder (`gov.launch.record.folder(root)`, the main checkout's `.gov-runtime/launches/`) with
`record: gov-launch`, this `ticket`, `role: independent-auditor` and `resumes: null`, leaving out the record of the
session being resumed, if any. A record file there that cannot be read as JSON refuses the launch naming it.
`review_round` is that count plus one, recorded (null for every other launch).

6.2 Round 1 takes the table's model and effort (the auditor's role file: Opus, high). Round 2 and later is the probe:
the model is `criticality.yaml`'s `opus` and the effort max; `effort_source: "probe"`, and `model_source: "probe"` if
the probe changed the model (**[settled]**: `probe` is a sixth source value beside the KPI's five). No `--reason` is
needed for the probe's max. An effort after `--` on round 2+ is accepted if not below the floor; a max on any review
that is not the probe needs `--reason` (3.2).

6.3 The same setting twice: a launch whose final (model, effort) equals the (model, effort) of a record counted in 6.1
is refused with LAUNCH_REFUSED naming that record's session id and the setting, unless `--owner-named <DEC-id>`
(`DEC-\d+`, else refused) is given; it is recorded as `owner_named` (else null). So a third review (round 3: Opus max
again) is refused without the owner's decision (DEC-1010).
**[amended by the lead on 2026-11-14 after review round 1, F2]** Also, whatever its setting: a launch whose
`review_round` is 3 or more is refused with LAUNCH_REFUSED naming the round and DEC-1010 (at most two review rounds)
unless `--owner-named <DEC-id>` is given (so a round 2 run on another effort, e.g. `--effort xhigh`, does not open a
third round). The same-setting rule stays as written for round 2.

6.4 Not FULL: no count, no probe, no same-setting refusal; `review_round` null.

## 7. The launcher's options (`launcher.launch`)

7.1 `launcher.launch(root, role, ticket_id, cli_args, gate_override=None, gpu_need_mib=None, *, reason=None,
trial=None, owner_named=None)`: the three new keyword arguments carry `--reason`, `--trial` and `--owner-named`.
All checks of sections 1-6 run before the resource gate and before any record, temp folder or session is made, as
W2-60a's refusals do.

7.2 **[settled] The CLI options.** `gov launch <role> <ticket> [--reason <text>] [--trial <id>] [--owner-named
<DEC-id>] [-- ...]` are wired in `src/gov/launch/command.py`, which is **not in this ticket's `allowed_paths`**. It is
not edited here: the lead returns it as a package (three `add_argument` lines and the keywords passed through). Until
then the acceptance cases that need these options call `gov.launch.launcher.launch(...)` with the keyword arguments,
in a child Python process with the same environment `gov launch` gets; every other case may drive `gov launch` as
W2-60a's cases do.

7.2a **[amended, the CTO's P-W2-184-2 (a), 2026-11-14]** `src/gov/launch/command.py` is now in the ticket's paths, and
the options are wired: `gov launch <role> <ticket> [--plan] [--gate-override DEC-NNN] [--gpu-need-mib N] [--reason
<text>] [--trial <id>] [--owner-named <DEC-id>] [-- <CLI arguments>]`, each before `--`, passed to `launcher.launch`
as the keywords `reason`, `trial`, `owner_named` (absent: `None`). Through the CLI they behave exactly as the keyword
cases (the same refusals with exit 1 and no record or session; the same records), and the usage line names them. An
option written after `--` stays a CLI argument (W2-60a's checks of the passthrough judge it, unchanged). `--plan` is
unchanged (it does not read the three options), and so is a lead launch (7.1: a lead takes none of them).

## 8. The launch record (`src/gov/launch/record.py`, W2-60a's record plus these keys, each always present)

| key | value |
|---|---|
| `tier` | the family word of `model` (4.2) |
| `criticality` | C0..C3, or null only under 1.4's absent-file case |
| `model_source` | `role default`, `by criticality`, `after --`, `trial`, `promotion`, `probe` |
| `effort_source` | `role default`, `by criticality`, `after --`, `trial`, `probe` |
| `trial` | the trial id, else null |
| `promotion` | `{"reason": ..., "record": ...}`, else null |
| `effort_reason` | the `--reason` text, else null |
| `owner_named` | the `--owner-named` id, else null |
| `review_round` | 1, 2, ... for an auditor launch on a FULL ticket, else null |

`model_source` precedence when several apply: promotion, trial, probe, after -- (the given model equals the resolved
one), then the table's source. `effort_source`: trial, after -- (but `probe` when the given effort is the probe's max,
3.2a), probe, then the table's source. `model`, `effort`
and `subagent_model` are the final values, and the launch line carries `--model` and `--effort` with them (W2-60a's
rule stands: a value given after `--` is not repeated before it).

## 9. Refusals: LAUNCH_REFUSED (exit 1), with no record left, no session started, naming the cause

A malformed `Launch by criticality` line (two such lines, a class missing, ...); an unreadable or malformed
`criticality.yaml` (1.4); `--trial` with no `criticality.yaml`; a model
after `--` that is not the resolved one (both named); an effort after `--` below the floor; a max that is the launch's
own choice with no `--reason`; a bad, missing or non-fitting trial; a model below Opus or a trial when a promotion
applies; a FULL ticket's auditor launch repeating a recorded setting with no `--owner-named`; a malformed
`--owner-named`, `--trial` id or empty `--reason`; an unreadable probe record or launch record.

## 10. R1-R3 (reopened 2026-11-14 by the CTO, DEC-1180 (4); the narrow check's F1-F3, `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`) [stated by the ticket lead before the pair starts, DEC-1052]

These amend 7.2a, 8 and 5.1a. Nothing refused before becomes allowed. Every other rule of sections 1-9 stands.

10.1 **R1: a lead takes none of the three options (amends 7.2a's last sentence).** `gov launch <lead role> <ticket>`
(a lead role is `orchestrator` or `lead`, `gov.launch.launcher.LEAD_ROLES`) given any of `--reason`, `--trial` or
`--owner-named` before `--` (each alone, or several; an empty value counts as given) is refused by the CLI with **exit
2**, before the launcher is called: nothing starts, no launch record is written, the resource gate is not consulted
and no plan-override line is logged. The message goes to stderr, names each option given, and says that a lead launch
takes none of `--reason`, `--trial` and `--owner-named` (the words "a lead" and the option names appear in it). A lead
launch without them is unchanged. A worker launch with them is unchanged (7.2a). The same three written after `--`
are CLI arguments, not these options: a lead launch with them after `--` is judged by the existing passthrough checks,
as before. `--plan` is unchanged. Also, `gov.launch.launcher.launch(...)` called directly with a lead role and any of
`reason`, `trial`, `owner_named` not `None` refuses with LAUNCH_REFUSED (exit 1) before anything starts (a second
fence; the CLI case is the KPI's).

10.2 **R2: the launch record is written atomically (amends 8; `gov.launch.record.write(records, record)`).** The
record's bytes are written, flushed and fsynced to a temporary file in the same folder whose name begins with `.` and
ends with `.tmp` (form: `.<session_id>.<unique part>.tmp`), so that no reader of `*.json` takes it as a record; then
it is hard-linked to the final name `<session_id>.json`, which fails if a file of that name exists (no overwrite);
then the temporary file is removed. So at no moment is there a final-name file that is empty or partial: a launch
killed at any point leaves either no `<session_id>.json` or a whole one (a leftover `.tmp` file at most). If the final
name exists, `write` refuses as today (LAUNCH_REFUSED, "a launch record of the session <id> is already there") and
removes its temporary file. Any `OSError` (the create, the write, the fsync, the link other than "exists") refuses as
today ("the launch record cannot be written in <folder>") and leaves no final-name file and no temporary file. Readers:
a file in the record folder that does not match `*.json` (a leftover temporary file included) is not a record and is
never read or refused on. A final-name `*.json` record that is not JSON still refuses a launch that reads the folder,
naming the file (5.1a, 6.1, P-td5-1 unchanged). Two writers of the same session id: exactly one final record (the
winner's whole bytes); the other is refused as already there.

10.3 **R3: every root's copy is read (revises 5.1a's P-td5-2).** The probe records are still found under the launch
root and every root the ticket's launch records name (5.1a). For one root-relative path (`docs/probes/<name>/...`)
found under several roots: copies with identical bytes are one copy; copies with different bytes are each read. Each
copy that refuses (front matter not YAML, a verdict block not of the form) refuses the launch, naming the file as
today. The path is still **one review** for 5.2: (a) it holds a fail-open finding if **any** of its copies does; (b)
it counts as one failed record if **any** of its copies has `judgement` fail or failed (never more than one per path,
so two differing copies of one failed record are not two failed reviews). The promotion's `record` is the
root-relative path as in 5.2, in sorted path order over the set of paths. So a stale launch-root copy without the
fail-open finding and a newer copy under the ticket worktree with it: promoted, `promotion.reason` `a fail-open
finding`, `promotion.record` the root-relative path. With one copy, or identical copies, the result is as before.
