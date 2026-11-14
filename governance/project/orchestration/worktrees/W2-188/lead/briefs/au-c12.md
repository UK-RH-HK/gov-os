# W2-188 (DAEO-zlog): narrow independent check of the F2 guard revisions and the owner-approval line (brief au-c12, from the ticket lead)

You are a fresh, read-only independent auditor for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C3, a kernel
skill change by the CIT-P route (CAP-33). This is **a narrow independent check of one change only** (DEC-1156 (7)),
not a review round: review round 1 passed on `b75472d48` (`docs/probes/DAEO-zlog/PR-DAEO-zlog.md`) and the S5 narrow
check passed on `c1c8685b8` (`docs/probes/DAEO-zlog/PR-DAEO-zlog-s5.md`). Use your skill `audit`. You wrote none of
this work. You write nothing in the tree: you return your record as text and the lead commits it as
`docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md`.

## The change you check
The owner approved the adopt skill's bytes (sha256 `6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489`,
DEC-1181 (1), "yes W2-188 adopt skill 6a884cf1"). The CTO's answer **P-C12-1 (a)** (DEC-1156 (7), within the ticket's
purpose): the copies ACT **ACT-CLAUDE-COPIES-12** writes the generated `.claude/skills/adopt/SKILL.md` from the approved
kernel skill; that copy's after-bytes have sha256 `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc`,
and it lands as the owner's operator's commit with `Role: owner`. Ticket F2 ("the ticket writes
`.claude/skills/adopt/SKILL.md` or any test under `tests/acceptance/`") is about the ticket's own writers; its verify
line says "the copies ACT regenerates the `.claude` copy after the owner's approval". So two F2 guard cases were revised:

- the `.claude` copy case passes when the copy equals the base's **or** its sha256 is exactly the ACT's after-bytes;
  any other bytes stay red;
- the commit case excuses a commit whose trailers carry `Role: owner` **and** whose subject names
  `ACT-CLAUDE-COPIES-` (for `.claude/` paths only); any other commit touching `.claude/` or `tests/` outside the test
  designer stays red.

| what | commit | session |
|---|---|---|
| merge of `w2/integrate` (bf04ed69c) before the revisions, the lead, no conflict | 84ca16727 | the lead |
| the two F2 cases revised and the README map updated, independent test designer td-3 (`Rewrite-Reason: P-C12-1 (a), DEC-1156 (7)`) | 1734f74221fdfa5e48bdb666fca88f3f127dd356 (merged 7604a3b0b) | 5281ba07-b3fa-4204-8148-813e59ea90d3 |
| the CIT-P's `owner_approval:` line brought to the ticket's I6 form (`'<sha256 after> approved by the owner, <date>, <reference>'`), the owner's words kept, and §6's stale "This record holds none yet." sentence, the lead | 7130a29c0a3c713a67f521f35af8b4d7db1e3399 | the lead (orchestrator) |

Why the third commit: the CTO wrote the `owner_approval:` line at 0db33e558 as `'"yes W2-188 adopt skill 6a884cf1"
(the owner, chat, 2026-11-14 ~15:40; DEC-1181 (1)): the skill''s bytes at sha256 6a884cf1…9489'`. The S5 case
`test_s5_the_owner_approval_line_names_the_after_sha256` asks for the after sha256 and the word `approved`, the form
the ticket's I6 states; the line lacked `approved`, so the lead re-worded it to I6's form.

| what | value |
|---|---|
| tree | /home/usain/gov-os-worktrees/W2-188 (branch w2/W2-188) |
| probed commit | 7130a29c0a3c713a67f521f35af8b4d7db1e3399 |
| the change | `git diff 5ada20fef 7130a29c0 -- tests/acceptance/W2-188/ docs/changes/W2-188-CIT-P.md template/governance/kernel/skills/adopt/SKILL.md .rulesync/skills/adopt/SKILL.md template/.rulesync/skills/adopt/SKILL.md docs/research/W2-88-memory-practice.md .claude/` (5ada20fef is the S5 check's head; 0db33e558 is the CTO's owner_approval line; 84ca16727 merges `w2/integrate`, whose own changes outside this ticket's paths are not yours to judge) |
| the ticket (F2, S5, I6, and its last paragraph) | /home/usain/gov-os-worktrees/W2-188/.tickets/DAEO-zlog.md |
| the decisions | `docs/DECISION_REGISTER.md`, grep by id only (1.6 MB): `### DEC-1156` item (7), `### DEC-1181` item (1), `### DEC-136`, `### DEC-105` |

## What you judge (this change only)
1. **The two revisions:** does each revised case in `tests/acceptance/W2-188/test_w2_188_copies.py` check exactly the
   described behaviour above, as described behaviour (DEC-136)? Did the test designer touch any other case (the diff of
   `tests/acceptance/W2-188/` from 5ada20fef)? Is the README map row and the F2 note true to the renamed cases?
2. **Nothing refused before becomes allowed:** list every situation the old two cases made red, and show each is still
   red, save exactly the ACT's own change. In particular: the product-spec worker or the lead writing `.claude/`; any
   `Task: DAEO-zlog` commit outside the test designer touching `tests/`, including a `Role: owner` ACT commit touching
   `tests/`; a `Role: owner` commit whose subject does not name `ACT-CLAUDE-COPIES-`; another role's commit whose
   subject names it; a `.claude` copy with any bytes other than the base's or `65d6abd9…dbc`. Read how roles and
   subject are parsed (a trailer value like `owner, product-spec`, a missing Role, a subject holding the mark mid-text)
   and say whether an honest agent could hit a hole in ordinary work.
3. **The constant:** is `65d6abd9…dbc` truly the generated copy of the approved skill? The lead reproduced it by
   applying the base's `.rulesync` → `.claude` transform (seen at 5336a6fca: the description folded at the same
   width, `version:` dropped, the blank line after the front matter dropped) to the HEAD `.rulesync` copy; the script is
   `/home/usain/gov-os-worktrees/W2-188/.gov-runtime/scratch/lead/act-bytes.py` (read it; you may run it, it only reads
   git). Check it independently if you can (for example with the project's adapter generator,
   `grep -rn "generate\|rulesync" src/gov/adapters/ | head`, run so that it writes only into your `$TMPDIR`).
4. **The record line:** is the new `owner_approval:` line faithful to the owner's approval as DEC-1181 (1) records it
   (hash, date, reference, the owner's words), in I6's form, valid YAML? Is the §6 sentence true? Did anything else in
   the record change since 5ada20fef (the front matter's other keys, hashes, counts, §6's `verdict: PASS` as the last
   verdict)?
5. **Unchanged bytes:** the skill's three copies are byte-equal at sha256 `6a884cf1…9489` and the practice record is
   byte-unchanged from 5ada20fef; no commit since 5ada20fef touches `.claude/`.
6. **Trailers:** each commit carries `Task: DAEO-zlog`, a `Role:` of its session, `Implements:` naming only ids in the
   ticket's `sources:`, the test commit `Rewrite-Reason: P-C12-1 (a), DEC-1156 (7)`; trailers in one final paragraph.
7. **The folder:** run `tests/acceptance/W2-188` once. Expected: every case passes (54).

You may run read-only commands (`git`, `grep`, `sha256sum`, `python3` scripts that only read, written in the sandbox's own
`$TMPDIR`). A planted run goes in a throwaway clone under `$TMPDIR` (`git clone --no-hardlinks
/home/usain/gov-os-worktrees/W2-188 "$TMPDIR/plant"`), never in the tree. A pytest run goes through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with
`PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<the tree or clone>/src`, `-p no:cacheprovider
-o tmp_path_retention_policy=failed`, `HOME` an empty folder in `$TMPDIR` (a resource gate's refusal is a wait). Never
open the evaluation sets' root (`~/gov-os-eval`), any hidden or memory-verdict folder, or secrets. Refused twice for the
same action: stop and say so; never work around it.

## Judgement rules (JUDGEMENT.md, word for word)
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



## Return (your last message; only it is read)
The sandbox check first, then the twelve fields as labelled lines (task, status, work_completed, files_changed,
evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), then **the probe
record's full text** for `docs/probes/DAEO-zlog/PR-DAEO-zlog-c12.md`: front matter with `type: probe`,
`task: DAEO-zlog`, `ticket: W2-188`, `round: 'narrow check (DEC-1156 (7)), not a review round'`,
`reviewer_role: independent-auditor`, `reviewer_session` (yours, in full),
`implementer_session` (one string naming the test designer td-3 5281ba07-b3fa-4204-8148-813e59ea90d3 (1734f7422, merged
7604a3b0b) and the lead's record commit 7130a29c0), `reviewer_wrote_nothing: true`,
`probed_commit: 7130a29c0a3c713a67f521f35af8b4d7db1e3399`, `judgement: pass|fail`, `decisions: [...]`,
`commissioned_by: orchestrator`, `judged_by: orchestrator`; quote (single or double quotes) any front-matter value
holding `: `. Then your checks with their evidence, each finding with its two lines, and at the end the fenced
`verdict` block (one entry per KPI line this change touches: F2, S5, and F1 for the unchanged skill), and one line
`verdict: PASS` or `verdict: FAIL`.
