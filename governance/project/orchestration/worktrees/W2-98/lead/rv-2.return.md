task: DAEO-wi46 (W2-98), review round 2 (the last), independent probe of head c530a0a1a2365cff3ea136182a8c604ab6c8e1b6
status: done. Verdict FAIL: three findings are in scope, an honest agent can hit them in ordinary work, and all three fail open.
work_completed: I ran Step 0 and read the ticket, the round 1 record, behaviours B1–B6, check_spec.py (all of it), spec-form.md, SKILL.md, imports.yaml, the template's section list and the suite's support module and README. I re-ran every round 1 reproduction of F1, F2 and F4. I probed about 230 fresh inputs in memory against the KPI parser, the code-name detector, the Test data table, section handling and the imports reader. I ran the validator, the `diff -r` of both copies, the adapter check and the suite (once).
files_changed: none intended. One accidental write, which the guard stopped me undoing: see discoveries.
evidence: I imported check_spec.py with importlib and called `check_spec()` with a stand-in path object (the same function `main` calls), and `check_imports()` with a stand-in folder. Each finding below has its reproduction.
tests: 5 failed, 261 passed in 10.57s. Two reds are the expected `.claude` ones. The other three fail only because of my stray `__pycache__` (their messages name only that `.pyc`): both `test_the_rulesync_copy_matches_the_kernel_source` cases and `test_the_adapter_check_finds_no_source_drift_in_the_real_skill`. I could not re-run after removing it, because the removal was refused.
discoveries: (1) My first in-memory probe (`python3 -c` importing check_spec.py via importlib) wrote `template/governance/kernel/skills/spec-writing/__pycache__/check_spec.cpython-312.pyc` at 00:10:05 UTC. The worktree is writable for this session (the sandbox allows writes to the worktree, "."), contrary to the brief. Step 0 (a) tests only the parent folder. The guard reads only command text, so this side effect went through. The guard then refused my `rm` of that file (DEC-953 item 2). I did not try another way. The file is gitignored, so `git status --porcelain` is empty, but the `.pyc` breaks `diff -r`, adds an adapter `SOURCE_MISSING` and turns three suite cases red. (2) The suite runs check_spec.py as a subprocess, so it writes no cache of its own; the `.pyc` is mine alone.
risks: A spec can print PASS with a KPI whose failure line is a placeholder (F1). It can also pass with a KPI whose id line has no bullet and no failure line (F2), or with a data source whose owner is `TBC`, `N/A.` or `nobody` (F3). If the copies ACT runs before the `.pyc` is removed, it may copy it.
lessons: Probe with `python3 -B` (or `PYTHONDONTWRITEBYTECODE=1`); the brief should say so. B1 and B4 closed the exact forms round 1 listed, but not the same class next to them: placeholders in KPI text, and an id line that is not a list item.
proposed_decisions: none of mine; the options for the owner are under recommended_next_action.
unresolved: The Write tool was refused once (a permission prompt for `$TMPDIR/aud2/probe.py`); I did not retry it. The `rm` of my `.pyc` was refused by the guard; I did not retry it. The lead must delete `template/governance/kernel/skills/spec-writing/__pycache__/`, then re-run the suite and the adapter check.
recommended_next_action: This was the last round, so it goes to the owner once, with options. (a) One fix batch for F1–F3, then a narrow independent check (recommended; each fix is small and keeps I2/I3's words). (b) Merge now and land F1–F3 as Wave 3 rows. (c) Re-word I2 so that placeholder text and off-form id lines are the reviewer's to catch, not the check's. In every case, first delete the `__pycache__` above and re-run the suite.

```verdict
verdict: FAIL
head: c530a0a1a
findings: 9 (failing: F1, F2, F3)
```

Classification: 3 findings block (in scope, ordinary work, fail open: F1, F2, F3). 6 are recorded rows: F4 is out of scope; F5, F7 and F9 need a deliberate construction or a rare form (ordinary work no); F6 and F8 are other. Recommendation: option (a) above.

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": [{"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S2", "verdict": "fail", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F4", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S3", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S4", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "S5", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "F2", "verdict": "fail", "findings": [{"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": [{"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]},
 {"kpi": "F5", "verdict": "pass", "findings": []}
]}
```

S6 passes on what this branch can deliver: both `.rulesync` copies match the kernel source byte for byte apart from my `__pycache__`. The `.claude` copy waits for the copies ACT (DEC-315, DEC-1112 (3)).

## Round 1 reproductions, re-run at c530a0a1a
- **F1: all six are now refused**, with a `REFUSED KPIs: list item "…" is not a KPI line…` line and exit 1:
  - `- K2 : …`
  - `2. K2: …`
  - `- K2a: …`
  - `- K3 (new): …`
  - `- **K2** — …`
  
  The column-0 wrap `- K1: A member sees the page after` / `send_welcome() runs.` now gives `REFUSED KPIs: K1 names code (name( call "send_welcome(")`.
- **F2: all are refused.**
  - An empty privacy cell gives `repos has no privacy`; an empty secrets cell gives `repos has no secrets`.
  - Owner `TBD`, empty or `none` gives `repos has no owner`.
  - Licence `unknown` gives `repos has no licence`.
  - The rest of round 1's placeholders (`—`, `-`, `n/a`) are in B4's list; the code holds that list and the suite tests it.
- **F4: both fail-open parts are refused.**
  - GPL-3.0 and MIT records for the same part, in either order, give `REFUSED import tdd: licence GPL-3.0 is not in the allowed list`.
  - A record only under `other:`, before or after `imports: []`, gives `REFUSED import tdd: no licence record`.

## Findings

**F1: A KPI whose failure line holds only a placeholder passes** (check_spec.py:99; DEC-959 item 8, DEC-1156 (5))
- **What happens:** `- K1: The member sees the page.` followed by `  Fails if: TBD` gives `PASS`, exit 0.
  - The same happens with `Fails if:` followed by `-`, `—`, `n/a`, `?`, `TODO`, `none`, `(none)`, `**TBD**` or `to be written`.
  - `- K1: TBD` with a real failure line passes, and so does `- K1:` with nothing after it.
  - B4 treats a placeholder as empty in the owner, source and licence cells, but nothing applies that rule to KPI text.
- **Should happen:** a `Fails if:` text that holds only a placeholder (B4's list, ignoring emphasis, spaces and trailing punctuation) is refused as `REFUSED KPIs: K<n> has no Fails if: line`. A behaviour that is empty or only a placeholder is refused, naming the KPI.
- Ordinary work: yes, because writing `Fails if: TBD` while drafting is as ordinary as writing `TBD` for an owner, which round 1 and the lead accepted as fail open.
- Consequence: fails open. A KPI with no real failure line is passed (F1's failure line; S3's first Done-when item).
- **What would reverse it:** an owner or lead ruling that I2 binds only the presence of a `Fails if:` label, so a placeholder there is the reviewer's to catch.

**F2: A KPI id line with no bullet is taken into the previous KPI and passes with no failure line** (check_spec.py:90-95; DEC-1156 (5))
- **What happens:** after a clean K1 with its `Fails if:` line, each of these lines gives `PASS`, exit 0:
  - `K2: The member sees the page.`, directly below or after a blank line
  - `**K2:** The member sees the page.`
  - `  K2: The member sees the page.`
  - `K2. The member sees the page.`
  
  B1 refuses only list items, so the line is counted as more of K1's failure text, and K2's missing failure line is never noticed. Code in such a line is still refused, but under the wrong name: `K2: send_welcome() runs.` gives `REFUSED KPIs: K1 names code in its Fails if: line`.
- **Should happen:** a line under `## KPIs` that is not a list item but starts with a KPI id (`K<n>`, bold or not, followed by `:` or `.`) is refused, quoting the line, like an off-form list item.
- Ordinary work: yes. Leaving the dash off one line is the same kind of slip as the stray space or numbered item that round 1 counted as ordinary.
- Consequence: fails open. A KPI with no failure line is passed.
- **What would reverse it:** a ruling that only list items can be KPIs, and an unbulleted id line is the writer's alone. Or a case showing these inputs are refused at the head.

**F3: Owner placeholders just outside B4's list pass** (check_spec.py:35, :41; DEC-959 item 8)
- **What happens:** each of these owner cells, in an otherwise clean row, gives `PASS`, exit 0: `TBC`, `Tbd.`, `N/A.`, `NA`, `nobody`, `to be decided`, `TBD` inside backticks, `...` and `<owner>`. The licence cells `unlicensed` and `none found` also pass.
- **Should happen:** placeholder matching also ignores trailing punctuation and code spans. It adds `TBC`, `NA`, `nobody`, `to be decided` / `to be confirmed`, and a lone `<…>` slot, all refused as `<source> has no owner`.
- Ordinary work: yes, because `TBC` is common British usage (the project writes "licence"), and a stray full stop is an ordinary slip.
- Consequence: fails open. A source with no real owner is passed (S2's and F2's verify lines name the owner).
- **What would reverse it:** a ruling that B4's list is closed and its near variants are recorded rows. The code matches B4 exactly.

**F4 (row): placeholders in the privacy and secrets cells pass** (check_spec.py:145-147)
- **What happens:** `-` or `TBD` for privacy, and `unknown` for secrets, each pass. B3 decided that any stated text is valid.
- **Should happen:** the lead decides whether the placeholder rule extends to these two cells.
- Scope: out, because S2's and F2's verify lines name source, owner, licence or recipe, and hidden half, not privacy or secrets.
- Ordinary work: yes.
- Consequence: fails open.
- **What would reverse it:** S2's verify line being read as covering privacy and secrets.

**F5 (row): The imports check misses a few marker and record forms** (check_spec.py:36, :207-215)
- **What happens:**
  - `<!-- Imported: tdd -->` with a capital I is not read as a marker, so a GPL-3.0 record passes.
  - A record `licence: GPL-3.0` followed by a nested `notes:` block holding `licence: MIT` passes, because the later key wins.
  - A part named `<tdd>` is skipped as if it were the form's placeholder.
  - The flow style `- {part: …}`, the `license:` spelling, quoted keys and a dash on its own line all fail closed.
- **Should happen:** the marker keyword matches without regard to case, and nested keys are not read as record keys.
- Ordinary work: no, because the marker is a fixed token copied from the form, and nested licence keys or angle-bracket part names need a deliberate construction. Wave 3 row.
- Consequence: fails open.

**F6 (other): Ordinary forms that are refused (fails closed)**
- **What happens:**
  - `**Fails if**:` (bold without the colon) is refused, and so is `Fails if:` on the same line as the behaviour.
  - Sub-bullets under a KPI or under its `Fails if:` are refused. This is by B1's design, and spec-form says so.
  - `1. K1:` is refused.
  - `## KPIs ##`, `## 5. KPIs` and `## KPI` count as missing.
  - Bold header words make a column count as missing, and so does `licence/recipe`.
  - These prose words are taken as code: `member(s)`, `page(s)`, `example.com`, email addresses, `Node.js`, `ASP.NET`, `README.md`, `x86_64` and `COVID_19`. The first five are round 1's F3 row, carried over.
- **Should happen:** these forms are either accepted, or refused with a reason that says what to reword.
- Ordinary work: yes. Consequence: other, because the writer only has to reword.

**F7 (row): Some code forms are not caught**
- **What happens:**
  - `send\_welcome`, an escaped underscore that renders as `send_welcome`, is not taken as code.
  - CamelCase, `Account::create`, `account->create` and `--dry-run` are not caught either; these sit outside I3's definition.
- **Should happen:** a Markdown-escaped underscore is read as an underscore.
- Ordinary work: no, because escaping is rare in an agent's Markdown. Consequence: fails open.

**F8 (row, carried over from round 1):** the front matter still has no `output:` key (round 1's F5). A measuring source with hidden half `no` still passes (round 1's F6). Ordinary work: yes. Consequence: other.

**F9 (row): A heading inside a code fence counts as a part**
- **What happens:** `## Accepted by` inside a fence, with no real section, gives `PASS`.
- Ordinary work: no, because it needs the heading planted inside a fence. Consequence: fails open.

## Probed and found sound
- **Output and exits:** PASS is never printed beside a REFUSED or P1 line.
  - `secured: no` (any case) gives a P1 line, the P1 package content and exit 2. With another refusal the exit is 1, and the P1 line is still printed.
  - Two unsecurable sources give two P1 lines.
  - A second `## Test data` section with `secured: no` still gives a P1 line, and a second `## KPIs` section is still judged.
  - An unclear `secured` value (`**no**`, `no.`, `not yet`, `yes (pending licence)`) is refused, never skipped.
- **KPI form:**
  - `+`, numbered, `k2`, a full-width colon and `- **K1.**` lines are refused, quoted.
  - A KPI with no or an empty `Fails if:` line is refused, and so is a `Fails if:` that comes before its KPI.
  - A `Fails if:` label with emphasis, in lower case, as a bullet, or with its text on the next line is accepted.
  - Code in the failure text, or in its continuation lines, is refused.
  - A prose line before the first KPI is allowed, and a table of targets after K1 is allowed.
  - `### ` sub-groups of KPIs are judged, and so are lines inside a code fence, a blockquote or an HTML comment.
- **Code-name detector:** it refuses code spans, calls, paths with an extension, dotted names (including `.go`, `.rs`, `.tsx`, `.vue`) and snake or upper-snake names.
  - None of about 70 plain-prose forms is refused: abbreviations such as `e.g.`, `i.e.`, `etc.`, `a.m.`, `et al.`, `Fig. 2`, `p. 12`, `Ltd.`; numbers and versions such as `1.5`, `99.9%`, `v1.2.3`, `9.30`; words such as `UTF-8`, `TCP/IP`, `HTTP/2`; `_quickly_` and other emphasis; and text in parentheses after a space.
- **Test data:** missing columns, a header with no rows, prose with no table and a short row are each refused. A `License or Recipe` header, reordered columns and an extra column are accepted.
- **Imports:**
  - No record file, `imports: []`, a forbidden licence, or a part with an allowed and an unallowed record is each refused, naming the part.
  - These are read correctly: lower case `mit`, quoted values, comments, CRLF line endings, tab indentation, a list with no indentation, a `---` document start, keys in any order, marker spacing and a marker split over lines.
- **Honest code:** check_spec.py has no special case for the planted test text; I read it whole.
- **SKILL.md:**
  - The front matter has name, version and a third-person description.
  - The sections are in the template's order, with Sources last.
  - Steps are a checklist naming the nine parts, the check and imports. Done when has five yes/no items.
  - It has the twelve fields and the P3/P2/P1/Emergency escalation.
  - The body is 98 lines, and spec-form.md sits one level down and links to no further file.

## Suite
`5 failed, 261 passed in 10.57s` (through heavy_slot, without `--basetemp`). Red:
- `test_the_rulesync_copy_matches_the_kernel_source[.rulesync/skills]`: my `.pyc` only.
- `test_the_rulesync_copy_matches_the_kernel_source[template/.rulesync/skills]`: my `.pyc` only.
- `test_the_claude_copy_matches_the_kernel_source`: expected (the `.claude` copy is absent).
- `test_the_adapter_check_finds_no_source_drift_in_the_real_skill`: my `.pyc` only (`SOURCE_MISSING` for it).
- `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`: expected.

## Step 0
- (a) `OSError: [Errno 30] Read-only file system: '/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46'`, exit 1, so it failed as required. The worktree itself, however, is writable (see discoveries).
- (b) HEAD is `c530a0a1a2365cff3ea136182a8c604ab6c8e1b6`; GOV_ROLE is `independent-auditor`; GOV_TICKET is `DAEO-wi46`.
- `gov.__file__` is `/home/usain/gov-os-worktrees/W2-98/src/gov/__init__.py`.
- At the end, `git status --porcelain` is empty. `--ignored` shows `!! template/governance/kernel/skills/spec-writing/__pycache__/`, which is mine; the lead must delete it.

## Validator and adapter
- `gov.check.skill_validator …/spec-writing/SKILL.md` printed `{"findings": []}`, exit 0.
- `diff -r` of the kernel folder against `.rulesync/skills/spec-writing`, and against `template/.rulesync/skills/spec-writing`: each printed only `Only in template/governance/kernel/skills/spec-writing: __pycache__` (mine), exit 1. Otherwise the copies are identical.
- `gov.adapters.portability` exited 1. It printed four `GENERATED_DIFFERS`, for `.claude/skills/spec-writing/{SKILL.md, check_spec.py, imports.yaml, spec-form.md}`, as expected. It also printed one `SOURCE_MISSING` for `__pycache__/check_spec.cpython-312.pyc`, which is mine. It reported `compared: rulesync_version true, kernel_files 41, generated_files 55`; 41 is 40 plus my `.pyc`.
