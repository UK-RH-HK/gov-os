# Lead brief: the memory measure's transcript scan voids every set (EXAMIN's F-033); a fix under W2-204 (`DAEO-ma4q`)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (worktree, the machine rule, memory first, the flow,
trailers, models, the C3 trial). Name: `memaudit-scan-fix`; worktree `/home/usain/gov-os-worktrees/E2-memaudit-scan-fix`,
branch `e2/memaudit-scan-fix` from `w2/integrate`. **Do not merge.** This blocks release acceptance item 3 (EXAMIN's
fresh 80): the CTO needs it fast, for a patch release.

**The defect** (EXAMIN's report, `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/REQUESTS.md`, section
"2026-11-20 15:1x"; read it): `gov.memaudit.scan` (`src/gov/memaudit/scan.py`) takes the set's ids from its file stems,
which `deliver` requires to be `q` plus two digits, and matches them as whole tokens in every `*.jsonl` under
`~/.claude/projects` written in the window. Such tokens are everywhere (the Gov OS CTO's session discusses W2-61's
`q09`, numbered items), so a dummy set of 40 empty files nobody read gave `MEASURE VOID`, 20 findings in 27 transcripts.
Every fresh 80 ends void after the writers, checkers and the measure have run: ordinary work, and it loses the work.

**The rule the scan serves** (EMERGENCY-2 2.7, A-12, approved by the owner): "the scan reads every transcript written
between the set's writing and the end of its measure, looking for the set's path and its question ids"; a set that was
read voids the measure. Keep "every transcript" in the window (do not narrow it to some sessions: that would change A-12).

**Kind:** a fix in W2-204's feature (the memory measure on any adopted repository), recorded in `.tickets/DAEO-ma4q.md`
(append `## Fix: the transcript scan's id match (EXAMIN's F-033)` with the lines below, each with its verify); the
ticket stays closed. Every commit: `Task: DAEO-ma4q` and `Fix: <one line>`, all trailers in ONE final paragraph.
**C3 trial:** `src/gov/memaudit/**` is C3: test designer **Opus** (`model: opus`, prompt carrying `Task: DAEO-ma4q`),
engineer **Sonnet**. Report the trial figures.

## The fix lines (the CTO's; refine the wording, keep the behaviour)
- **M1 A bare id is not evidence.** A token like `q07` alone in a transcript line is no finding. A question id counts
  only when the same line also names the set (its folder path in any form the scan already knows, or the set's tag or
  audit name). Verify: a planted transcript full of bare `q01`..`q40` tokens (as a CTO's chat) and a dummy set nobody
  read: `MEASURE CLEAN`; the same transcript with one line `.../hidden/<set>/q07.md` or `<tag> q07`: `MEASURE VOID`
  naming that line's transcript.
- **M2 A question's text read is evidence.** A transcript line holding a hidden question's own text (a normalised
  prefix long enough to be specific: say how long and why; whitespace and case normalised) is a finding, so a session
  that read the file's contents is caught even without the path. Verify: a planted transcript holding one question's
  text: `MEASURE VOID` naming the question id and transcript (never printing the text); a transcript with text from no
  question: clean.
- **M3 The path still counts as today**, and nothing printed ever holds a question's or answer's text (the scan's
  existing rule). Verify: the existing path cases stay green; the scan's output and report hold ids and transcript
  paths only.
- **M4 EXAMIN's case.** The planted reproduction of F-033 (40 empty hidden files, a window of busy transcripts with bare
  ids and numbered lists, the dummy set's path typed once by its own CTO in a session outside the measure... the path
  case stays a finding: say so) gives the result the lines above say, end to end through `gov memaudit scan`.

## Order, green, return
Spec lines in the ticket (`Role: orchestrator`) → test designer (Opus): new cases under `tests/acceptance/W2-204/`, red
on the base, mapped as the next S numbers in that folder's README → engineer (Sonnet) until `gov accept W2-204 --root
<worktree>` is green → green: `gov accept W2-204`, `tests/unit/memaudit`, `tests/unit/optin` → return: branch and head,
each M line with its tests, the summary lines, the trial figures, reds not yours.
