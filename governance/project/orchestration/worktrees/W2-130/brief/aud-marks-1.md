Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief: independent auditor, W2-130 (DAEO-q8cl): the check before the follow-up marks commit (KPI S3)

You are a fresh independent auditor (role independent-auditor), ticket DAEO-q8cl (W2-130), profile STANDARD, class
C2. Read-only: you write no file in any repository and make no commit. Headless: only your last message is read, and
it is the audit record the lead copies into the ticket's record word for word, so make it complete.

## Where things are
| what | path |
|---|---|
| the tree (read only) | /home/usain/gov-os-worktrees/W2-130 |
| the head you audit | `09542040f` (read files at it with `git -C /home/usain/gov-os-worktrees/W2-130 show 09542040f:<path>`) |
| the register | `docs/DECISION_REGISTER.md` (read by id: find `### DEC-n ` and read to the next `### `) |
| the archive | `governance/project/orchestration/ARCHIVE-SUPERSEDED.md` §A |
| the ticket | `.tickets/DAEO-q8cl.md` (KPI lines S1-S3 and F3 matter here) |
| the proposed patch | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/propose-marks-0954.patch (`gov links --all --propose-marks` at 09542040f) |
| the earlier audit (for context, not as your answer) | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/ref/w2-130-marks.md |
| readiness reviewer 2's links review and its digest | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/ref/readiness-2-links.md, .../ref/e-spurious-changers.md |
| scratch | your sandbox's own `$TMPDIR` only |

## How you judge (owner, the w2 prompt's section 14)

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

## The background
W2-130 marks, on a decision's own `**Status:**` line, every later decision that changes it (`**Changed by:** DEC-n
(the part)`), from `gov links --propose-marks`. A mark changes no decision's meaning; it records what the changer's own
text says. KPI S3: before each marks commit an independent auditor checks every mark derived from free text and the
labelled marks (all of them when there are 20 or fewer) against both entries; a wrong mark is dropped or corrected,
never committed. The register is the owner's: you never propose changing an entry's text other than its status marks.

At 09542040f `gov links --all` reports 10 UNMARKED_CHANGE. Two are to be committed in this run's follow-up marks
commit; eight are to stay unmarked as wrong.

## What you check
**A. The two marks to be committed (both labelled; check each in full against both entries):**
1. DEC-1115 <- DEC-1122: add ` · **Changed by:** DEC-1122 (4)` to DEC-1115's status line. gov links read it from
   DEC-1122's `**Changes:**` label. Does DEC-1122 item (4) change DEC-1115 (narrow, replace, lift or amend a part of
   it), rather than merely apply, confirm or cite it? Is "(4)" the right part, and is the mark's text right as written?
2. DEC-026 <- DEC-086: add ` · **Changed by:** DEC-086` to DEC-026's status line. gov links read it from DEC-086's
   `**Settles:**` label. Does DEC-086 change DEC-026 (settles an open part of it in a way that changes what it says),
   or only implement it? If right, should the mark name the part (for example `DEC-086 (the part)`), and which?

For each: verdict `right` or `wrong`; if right, the exact mark text to commit (the proposed one or a corrected one,
naming the part where the changer's text names it); the quotes from both entries you relied on.

**B. The eight pairs to stay unmarked, each with a verdict (right or wrong as a mark) and the quotes:**
DEC-853<-DEC-884 (item 4), DEC-1050<-DEC-1057 (8), DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017,
DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880. The earlier audit judged the first four wrong (F14, F1, F2, F3);
readiness reviewer 2 judged the last four "certainly wrong" (the changer is older than the entry, or the free text's
subject is another entry). Judge each yourself from both entries' text.

**C. The census pairs no status line names, each with a verdict and the quotes:** DEC-454<-DEC-904,
DEC-455<-DEC-904, DEC-480<-DEC-899, DEC-480<-DEC-904, DEC-490<-DEC-868, DEC-490<-DEC-899, DEC-490<-DEC-908,
DEC-492<-DEC-904, DEC-492<-DEC-908 (the earlier audit's F4: from an archive group line, since split one per line),
DEC-780<-DEC-775 (readiness reviewer 2: changer older), DEC-501<-DEC-512 (from the archive's former line "DEC-501,
DEC-502: corrected by ..."; the archive now reads "DEC-501: corrected by DEC-502" and "DEC-502: corrected by
DEC-512").

If any pair in B or C is right as a mark (the changer's text does change that entry), say so plainly as a finding:
the lead then brings it to the CTO; do not soften it.

## Return (your last message)
1. A header: `Independent auditor, <ISO 8601 date and time with zone, from `date -Is`>, at 09542040f (full hash from
   `git rev-parse 09542040f`), W2-130 follow-up marks check.`
2. A table per part (A, B, C): pair | mark text | verdict | the changer's words | the changed entry's words | fate
   (A: `commit as <text>` or `drop`; B and C: `stays unmarked` or `should be marked`).
3. Any finding, each with its two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
4. Last, a fenced block opened by ```` ```verdict ```` holding one JSON object:
   `{"head": "<full hash>", "date": "<ISO>", "marks": [{"changed": "DEC-1115", "changer": "DEC-1122", "verdict": "right|wrong", "commit_as": "<text or null>"}, {...DEC-026...}], "unmarked": [{"changed": ..., "changer": ..., "verdict": "right|wrong"} ... all of B and C], "kpis": [{"kpi": "S3 follow-up marks check", "verdict": "pass|fail", "findings": [...]}]}`.

## Searching
Read and Grep only, and git show; no `gov retrieve` or `gov context`. Search once, then once more in other words;
answer from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out
material or any hidden or memory-verdict folder. Refused twice for the same call by the guard, the sandbox or a hook:
stop and say so; never work around a refusal.
