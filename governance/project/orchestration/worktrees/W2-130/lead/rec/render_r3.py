"""Render docs/research/W2-130-link-cleanup.md and LINK-RECONCILIATION.md from rec/build.json (the lead, run 3)."""
import json
import sys
from pathlib import Path

import yaml

W = Path("/home/usain/gov-os-worktrees/W2-130")
sys.path.insert(0, str(W / "tests/acceptance/W2-130"))
import w2_130_support as s  # noqa: E402

L = W / ".gov-runtime/scratch/lead"
B = json.loads((L / "rec/build.json").read_text())
D = B["data"]
c = D["commits"]


def y(name):
    body = yaml.safe_dump(D[name], sort_keys=False, allow_unicode=True, width=100000, default_flow_style=False)
    return f"```yaml w2-130:{name}\n{body}```\n"


def diff(name):
    body = (L / f"rec/{name}.diff").read_text()
    if not body.endswith("\n"):
        body += "\n"
    return f"```diff w2-130:{name}\n{body}```\n"


def py(name, text):
    return f"```python w2-130:{name}\n{text.rstrip()}\n```\n"


before, after = D["counts-before"]["by_code"], D["counts-after"]["by_code"]
codes = sorted(set(before) | set(after))
count_rows = "\n".join(f"| {k} | {before.get(k, 0)} | {after.get(k, 0)} |" for k in codes)
linked = D["dec-1123-linked"]
n_linked = sum(len(v) for v in linked.values())
forms = {}
for es in linked.values():
    for e in es:
        forms[e["form"]] = forms.get(e["form"], 0) + 1
judged = D["judged-wrong"]
jw_rows = "\n".join(f"| {j['changed']}<-{j['changer']} | {'yes' if j['in_gov_links'] else 'no'} | {j['finding']} |"
                    for j in judged)
lbc = B["left_by_code"]
closed = D["closed-missing"]
drift_out = D["drift-run"]["output"]
short = lambda h: h[:12]  # noqa: E731
added2 = s.sources_added(c["cleanup"][5])
n_added2, n_tk2 = sum(len(v) for v in added2.values()), len(added2)
lessons_rows = "\n".join(f"| {k} | {', '.join(v['sources'])} |" for k, v in D["lessons"].items())

text = f"""# W2-130: the link clean-up, its record (DEC-1073 (5)(a))

Ticket DAEO-q8cl (W2-130), profile STANDARD. Written by the ticket lead (orchestrator), 2026-11-14, at the end of
run 3. This record holds what the ticket's eight success lines and four failure lines ask to be kept: the commits,
the marks and their independent check, the tickets' `sources:`, the trailer residuals, the status reconciliation,
the lessons, the counts before and after, and what is left for D-5, D-6 and D-9. The fenced blocks named
`w2-130:<name>` are read by `tests/acceptance/W2-130/`; the prose is for a reader.

The register holds the owner's decisions. A mark changes no decision's meaning: every register change here is a
status line kept whole with marks appended (DEC-866), or a status the owner decided (DEC-1098 (3)). No commit was
rewritten.

## 1. When it started, and on whose word (F4)

- The clean-up's first commit is `{short(c['first_commit'])}` (e12f8a30c), whose parent `{short(c['starting_head'])}`
  is the starting head.
- W2-129's landing (DAEO-q7lk, merge `{short(c['w2_129_landing'])}`) and the adoption of W2-92's stated links
  (DAEO-n0wb, merge `{short(c['w2_92_adoption'])}`) are both ancestors of e12f8a30c.
- The owner allowed the start in **DEC-1097 (9)**.
- The owner's ruling on the status list is **DEC-1098 (3)**, committed in `{short(c['status_decision_commit'])}`. That
  commit is an ancestor of every clean-up commit that changes a status (c4420040f, and the R-12 follow-up), and not
  of e12f8a30c.

## 2. The commits

| commit | what | lists |
|---|---|---|
| `{short(c['cleanup'][0])}` | batches a1, a2 (the marks: the 87 first, then the rest), a0 (the archive's line 34, one decision per line), b1 (50 open and in-progress tickets' `sources:`) | marks, sources |
| `{short(c['cleanup'][1])}` | after the owner's sitting (DEC-1098 (3)): the decided status words, the a3 marks, this ticket's KPI 4 line and its `sources:` DEC-1098 and DEC-1088 | marks, status |
| `{short(c['cleanup'][2])}` | follow-up (2): DECISIONS-IN-FORCE's R-12 line reworded (P-W2-130-3 (a)) | status, r12 |
| `{short(c['cleanup'][3])}` | follow-up (3): each lesson's `sources:` key (DEC-1073 (5)(c)) | lessons |
| `{short(c['cleanup'][4])}` | follow-up (4): the two marks the auditor passed, DEC-1115<-DEC-1122 and DEC-026<-DEC-086 | marks |
| `{short(c['cleanup'][5])}` | follow-up (1): the open and in-progress tickets' `sources:` from `gov links --propose-sources`, less DEC-1123 (2)'s forms (P-W2-130-4 (a)) | sources |

The follow-ups are numbered as the plan numbered them; (1) was made last, after the CTO's answer to P-W2-130-4. Each
changes one kind of file and nothing else. This record and LINK-RECONCILIATION.md are committed after them and are
not clean-up commits.

{y('commits')}
## 3. The marks (S1, S2)

**The 87 first.** The census's script (`docs/research/D4B-link-census.py` at 3d1c459e, run on 24f06026) finds 215
decisions current though stated changed; 87 of them have no hint of a changer in their own entry. e12f8a30c marks
them from `gov links --propose-marks` (patches a1 and a2 as the drafts' builder printed them for the commit, after
the auditor's drops and rewrites: section 4). Every register hunk of e12f8a30c is a status-line append.

{y('ids-87')}
**The census's 215 and the changers it states.**

{y('census')}
**The 13 pairs stated only in ARCHIVE-SUPERSEDED §A** (W2-92's drift script, `--from-head`, on the starting head's
register and archive; `drafts/w2-130/work-drift-head.json`). Three are marked (DEC-454<-DEC-868, DEC-454<-DEC-899,
DEC-455<-DEC-899); the other ten were judged wrong (below). Patch a0 rewrote the archive's collective line so that
each decision names only the changers its own entry supports (the auditor's F4 and the sitting's H2).

{y('archive-13')}
**Left unmarked because an independent auditor judged the pair wrong.** `gov links --all` reports exactly 8
UNMARKED_CHANGE at the last clean-up commit, the 8 pairs below with `in_gov_links: true`. The other 11 are census
pairs no status line names; `gov links` no longer reports them because patch a0 removed the archive's cross
product. This run's auditor (aud-marks-1, 2026-11-13, at 09542040f) judged all 19 wrong, each against both entries;
the earlier auditor's finding is named where it judged the same pair.

| pair | reported by gov links | finding |
|---|---|---|
{jw_rows}

{y('judged-wrong')}
**The two follow-up marks.** DEC-1115<-DEC-1122 and DEC-026<-DEC-086 were the two UNMARKED_CHANGE left besides the
8 after c4420040f. `gov links --propose-marks` proposed `**Changed by:** DEC-1122 (4)` and `**Changed by:** DEC-086`
(patch-marks-3, at bce798c3a's parent). The auditor judged both right and corrected their parts (F1: "(4)" is
DEC-1115's item, so the mark names DEC-1122 (2) with item (4) in words; F2: DEC-086 settles DEC-026 "for Wave 1").
bce798c3a commits them in the corrected texts, after the check (2026-11-13T22:46:14Z, at 09542040f, an ancestor).

**The drift count (S2).** `docs/research/W2-92-proto-drift.py`'s definitions, applied to the entries' own text
(no store): {drift_out['count']} pairs at the last clean-up commit, every one of them a pair the auditor judged wrong,
so the count after setting them aside is 0. None of the sitting's group C, D or E ids is current, so none is counted.

{py('drift', (L / 'rec/drift.py').read_text())}
{y('drift-run')}
## 4. The independent check of the marks (S3, F3)

Each marks commit was checked by an independent auditor before it was made, at a head that is its ancestor:

- **e12f8a30c** (a1, a2): the auditor's review part 1 (`reviews/w2-130-marks.md`), at 2f9c80b1f, verdict written
  2026-11-08T01:35:59Z; the commit is 2026-11-08T01:39:21Z. Every free-text mark (19: 8 committed, 11 dropped as
  wrong) was read by hand against both entries; every labelled mark (132) was checked by script against the
  changer's own label. 12 marks were dropped (F1 to F4) and four parts rewritten (F4, F5) before the commit.
- **c4420040f** (f1's ruled marks, f5): the review's part 2, at ce7f10eb8a2a, verdict written 2026-11-09T00:41:51Z;
  the commit is 2026-11-09T00:42:54Z. f5's 17 marks were each checked against the changer's text (one dropped,
  F14: DEC-853<-DEC-884); the 13 group B ruling marks were checked against the rulings; DEC-786<-DEC-942 and
  DEC-927<-DEC-1057 as appends.
- **bce798c3a** (the two follow-up marks): this run's auditor (aud-marks-1), at 09542040f, 2026-11-13T22:46:14Z;
  the commit is 2026-11-13T23:29:46Z.

In `audits`, `free_text` is every mark `gov links` (this tree's tool) flags as derived from free text on the
commit's register with its marks taken off, and every free-text mark the auditor dropped. `labelled` is 20 marks
drawn by the stated seed from the labelled marks the auditor judged (the draw is stated in `draw`), or every
labelled mark where the commit adds 20 or fewer. `also_judged` holds the auditor's other rulings that the draw did
not reach. A wrong mark's fate is `dropped`; a right mark whose part the auditor rewrote is `committed` with the
committed text.

{y('audits')}
**The comparison** of each marks commit's diff with the check: 0 committed free-text marks unchecked, 0 committed
marks judged wrong.

{y('comparison')}
**The patches** e12f8a30c applied, as the drafts' builder printed them for the commit (`drafts/w2-130/`): a0
changes the archive only; a1 (99 marks on 81 entries) and a2 (40 on 35) are the register's marks after the
auditor's drops and rewrites (the builder took them as inputs; the patches it printed before the audit, 100 and 51
marks, were not kept); b1 is the 50 tickets' `sources:`. Their marks equal e12f8a30c's marks exactly.

{diff('patch-a0')}
{diff('patch-a1')}
{diff('patch-a2')}
{diff('patch-b1')}
**patch-marks-3:** `gov links --propose-marks --all` at bce798c3a's parent (8f8d707f0). Two of its hunks were
applied, in the auditor's corrected texts; the 8 judged-wrong pairs were not.

{diff('patch-marks-3')}
## 5. The tickets' `sources:` (S4)

- **e12f8a30c (b1):** 394 ids added to 50 open and in-progress tickets, from `gov links --propose-sources`; no
  closed ticket touched (DEC-1098 (3), H1 (b)).
- **Follow-up (1), {short(c['cleanup'][5])}:** `gov links --propose-sources --all` at its parent (11c4d7a5a),
  the open and in-progress tickets' sections (patch-sources-2), less the {n_linked} ids DEC-1123 (2)'s forms already
  link (P-W2-130-4 (a)): {forms.get('list_rows', 0)} backlog rows in their ticket's `list_rows`, {forms.get('wbs', 0)}
  WBS ids whose ticket's id is in `sources:`, {forms.get('dec-798', 0)} DEC-798 through its live DEC-1033. It adds
  {n_added2} ids to {n_tk2} tickets and changes only `sources:` lines. (W3-P09 on DAEO-ecac, a plan row in that
  ticket's `list_rows`, is one of the forms; a first version of the commit added it and was amended before the
  commit left this branch.)
- **W2-H046** on DAEO-6w5n is the one backlog row not in its ticket's `list_rows`. It is added to `sources:` as
  `--propose-sources` gives it: putting it in `list_rows` would change a field other than `sources:` (F1).
- **After:** `gov links --all` reports UNLINKED_ID on an open or in-progress ticket only for the {n_linked} ids
  below, each linked by one of DEC-1123 (2)'s forms. A D-6 row asks `gov links` to read `list_rows` and a WBS id's
  ticket id as linked, so these stop being reported.

{y('dec-1123-linked')}
{diff('patch-sources-2')}
**Closed tickets** are not edited (DEC-1088 (6), H1 (b)). Their missing ids, per ticket, from `gov links --all`'s
UNLINKED_ID at the last clean-up commit ({len(closed)} tickets):

{y('closed-missing')}
**Ids that name no record**, per ticket, for D-9: none. Every UNKNOWN_ID on a ticket at the last clean-up commit is
an `acceptance_tests.path` that does not exist yet ({lbc['D-9'].get('UNKNOWN_ID', 0)}, listed by path under `left`, D-9).

{y('no-record')}
## 6. Commit trailers (S5)

History is not rewritten: the starting head 232efc47d is an ancestor of HEAD. Every `Task:` and `Implements:` value
in the history at 232efc47d that names no record is listed once below (`Task: decision-record` is valid under
DEC-861 and not listed), with its commits, its ticket and what it should have named, as DEC-927 listed its 39. The
recount script gives the same set. The `Implements:` values `engineer` and `independent-test-designer` are in commits
the path map's `accepted_history` accepted (read at c5e9d962^); their `should_have_named` is the ids it named.

{y('trailer-residuals')}
{py('recount', B['recount'])}
## 7. The status reconciliation (S6, F2)

- **The list:** `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in 2f9c80b1f, an ancestor
  of the starting head): the 110 decisions ARCHIVE-SUPERSEDED §B called spent while the register listed them
  current, the 40 PROPOSED entries, and the STATUS_CONFLICT findings (116 at 232efc47d), each with the CTO's
  proposal and its reason.
- **The ruling:** DEC-1098 (3), committed in 9546edd61: groups A to G accepted as proposed; H1 (b); H2 as
  recommended.
- **Applied:** c4420040f writes each decided status (the new word first, the old status text kept); the archive and
  DECISIONS-IN-FORCE agree; the R-12 follow-up (8d245901b) rewords the one line that read as listing the done
  DEC-896 in force.
- **After:** STATUS_CONFLICT 0.
- LINK-RECONCILIATION.md (`governance/project/orchestration/packages/LIFT-1/`) carries the sitting's 150 rows with
  their proposals, reasons and rulings.

## 8. Lessons (S7)

Each lesson's `sources:` names the decision or owner record its own **Source:** line names (8f8d707f0).

| lesson | sources |
|---|---|
{lessons_rows}

{y('lessons')}
## 9. Counts before and after (S8)

`gov links --all --json` (this tree's tool, run on a clone of each commit), by code:

| code | before (232efc47d) | after (the last clean-up commit) |
|---|---|---|
{count_rows}

The UNLINKED_ID left are on closed tickets ({D['counts-after']['unlinked_by_status'].get('closed', 0)}, listed above)
and the {n_linked} DEC-1123 (2) form ids on open and in-progress tickets. CLOSED_TICKET_EDITED and
TICKET_CHANGE_UNMARKED rose from commits after the starting head made by other tickets, not by the clean-up.

{y('counts-before')}
{y('counts-after')}
## 10. What is left, by path and role (D-5, D-6, D-9)

- **D-5 (kernel texts, `template/` and `docs/contract/`):** nothing ({sum(lbc['D-5'].values())} findings).
- **D-6 (code and tests, `src/` and `tests/`):** {sum(lbc['D-6'].values())} findings ({', '.join(f'{k} {v}' for k, v in sorted(lbc['D-6'].items()))}),
  the test designer's. Also for D-6: `gov links` should read a backlog row in `list_rows`, and a WBS id whose
  ticket id is in `sources:`, as linked (DEC-1123 (2)); and the loader's reading of a verbless `Changed by:` and of
  the archive's group lines (the judged-wrong pairs), so that the 8 stop being reported without an allow-list.
- **D-9 (tickets, `.tickets/`):** {sum(lbc['D-9'].values())} findings ({', '.join(f'{k} {v}' for k, v in sorted(lbc['D-9'].items()))}).

{y('left')}"""

(W / s.RECORD).write_text(text, encoding="utf-8")

# ---------------------------------------------------------------- LINK-RECONCILIATION.md
rows = s.sitting_rows(s.show(s.SITTING_COMMIT, s.SITTING))
assert len(rows) == 150
RULING = {g: "accepted as proposed (DEC-1098 (3))" for g in "ABCDEF"}
lines = [f"| {r['id']} | {r['group']} | {r['proposal']} | {r['reason']} | {RULING[r['group']]} |" for r in rows]
rec = f"""# LINK-RECONCILIATION: the status reconciliation the owner ruled on (W2-130, DEC-1073 (2), (5)(a))

**The list the owner ruled on:** `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in
2f9c80b1f). **The ruling:** DEC-1098 (3) (the owner, 2026-11-09, committed in 9546edd61): groups A to G accepted as
proposed; H1 (b), open and in-progress tickets only; H2 as recommended. **Applied:** c4420040f (the decided status
words, the archive, this ticket's KPI 4) and 8d245901b (DECISIONS-IN-FORCE's R-12 line). The record is
`docs/research/W2-130-link-cleanup.md`.

The 150 rows below are the sitting's groups A to F, one per decision: the 40 PROPOSED entries (A, B, C) and the 110
the archive called spent while the register listed them current (D, E, F). The proposal and the reason are the
sitting row's Proposal and Evidence columns, verbatim. Groups G (four rows the readiness review added, no status word
changed) and H (the two choices) carry no decision id; their rulings are in DEC-1098 (3) and in the sitting file.

| Decision | Group | Proposal | Reason | Ruling |
|---|---|---|---|---|
""" + "\n".join(lines) + "\n"
(W / s.RECONCILIATION).write_text(rec, encoding="utf-8")
print("written", len(text), len(rec))
