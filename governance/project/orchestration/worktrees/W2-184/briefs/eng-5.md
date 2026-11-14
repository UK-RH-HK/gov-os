# Brief: engineer, W2-184 (DAEO-6f0s), batch eng-5 (fix after review round 2, F1)

You are a fresh engineer for DAEO-6f0s (W2-184), launched on Opus because the ticket is promoted (DEC-1120 (3)). The
head is 7d275b97f. New acceptance cases are red; make them green within the ticket's paths. The behaviour they test
is interface **5.1a** (below, with its two settled points); the rest of the interface is unchanged and its cases are
green.

## The failing output (all you are given beyond the interface)
`gov accept W2-184 --root /home/usain/gov-os-worktrees/W2-184` exits 3: 453 passed, 19 failed (success-5: 15,
failure-1: 4). The 19 are all in `tests/acceptance/W2-184/test_w2_184_f1_tests_worktree.py`:
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-5-short.txt (the case names and the two
  assertion lines);
- /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/log/red-5.txt (the full `--tb=line -rf` output).

Context: /home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/briefs/ctx-eng-5.md (JSON: the ticket and its
sources, from `gov context`).

Never write under `tests/acceptance/` (the independent test designer's), and never open anything under
`fixtures/evaluation/` or a `hidden` folder.

## What to deliver
- The change in `src/gov/launch/launcher.py` (and only the ticket's other paths if needed).
- Unit cases in `tests/unit/launch/test_w2_184_launch.py` (or a new `tests/unit/launch/test_w2_184_*.py`).
- One paragraph in `docs/changes/W2-184-CIT-E.md`: review round 2's F1, the owner's P-W2-184-1 (a) (DEC-1010), what
  changed.

## Where you work
- Your tree: /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. Write only `src/gov/launch/launcher.py`,
  `src/gov/launch/role.py`, `src/gov/launch/record.py`, `src/gov/launch/criticality.py`, `src/gov/launch/command.py`,
  `governance/project/criticality.yaml`, `tests/unit/launch/test_w2_184_*.py`, `docs/changes/W2-184-CIT-E.md`, and
  scratch under `.gov-runtime/scratch/eng/`.

## How to run tests (every pytest through heavy_slot.sh; in the background, never with `&`)
```
env HOME=/home/usain/gov-os-worktrees/W2-184/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Before your last commit, green: `tests/unit/launch tests/acceptance/W2-184 tests/acceptance/W2-60a
tests/acceptance/W1-46`. Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once
more in other words.

## Commit (your paths only; trailers in ONE final paragraph, no blank line inside it)
```
git -C /home/usain/gov-os-worktrees/W2-184 commit -m "W2-184 (DAEO-6f0s): review round 2's F1: the probe records are also read under each root the ticket's launch records name (P-W2-184-1 (a))" --trailer "Task: DAEO-6f0s" --trailer "Role: engineer" --trailer "Implements: DEC-1120, DEC-1010" -- <your paths>
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 and round-2 amendments)

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
