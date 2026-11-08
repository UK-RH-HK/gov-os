"""W2-130: the owner's one-sitting list (DEC-1097 (9), DEC-1074 (7) O2), generated from sitting_data.json.

    python3 sitting.py <sitting_data.json> <build-summary.json> <out.md>

The CTO's proposal per id is the table PROPOSALS below (read the entries; the reasons are in each row's evidence);
everything else (titles, archive words, who cites what) comes from sitting_data.py's read of HEAD.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DATA = json.loads(Path(sys.argv[1]).read_text())
BUILD = json.loads(Path(sys.argv[2]).read_text())
OUT = Path(sys.argv[3])
ARCH = "ARCHIVE §B (`2e5c9cd9`)"
D083 = "DEC-083 (`f88aac89`, register line 744)"

# ---------------------------------------------------------------- the PROPOSED entries (DEC-083 settled them)
P_AS_WRITTEN = ["DEC-001", "DEC-003", "DEC-004", "DEC-005", "DEC-006", "DEC-010", "DEC-011", "DEC-012", "DEC-014",
                "DEC-015", "DEC-022", "DEC-023", "DEC-025", "DEC-026", "DEC-027", "DEC-041", "DEC-044", "DEC-046",
                "DEC-050"]
P_NOTE = {"DEC-001": "DEC-083: 'assemble first stands'; DEC-064 turned its revisit trigger into a per-wave review",
          "DEC-004": "as settled by DEC-086", "DEC-005": "its readiness part as settled by DEC-085",
          "DEC-015": "native LSP; Serena not adopted", "DEC-026": "as settled by DEC-086"}
P_REALISED = {"DEC-007": "DEC-075", "DEC-016": "DEC-074 (R1)", "DEC-017": "DEC-074 (R1)", "DEC-024": "DEC-074 (Q5)",
              "DEC-031": "DEC-080", "DEC-032": "DEC-080", "DEC-033": "DEC-080", "DEC-034": "DEC-080",
              "DEC-035": "DEC-080 (numbers stay placeholders)", "DEC-036": "DEC-080", "DEC-037": "DEC-080",
              "DEC-040": "DEC-083 (installs: owner approval per tool); DEC-095 states it", "DEC-042": "DEC-083 (MR-3 for every task)"}
P_SUPERSEDED = {"DEC-002": ("DEC-058, DEC-064", D083), "DEC-043": ("DEC-064", D083), "DEC-045": ("DEC-058", D083),
                "DEC-047": ("DEC-058", D083),
                "DEC-013": ("DEC-074", "DEC-074 (`8e5bbe14`, line 490): 'tasks T3 wedow/ticket … Supersedes DEC-013 (`br`)'")}
P_OTHER = {"DEC-062": ("WITHDRAWN by DEC-842", "high", "DEC-842 (`a5789de1`): withdrawn, it landed nowhere"),
           "DEC-018": ("DEFERRED to Wave 3 (model routing)", "high", D083 + ": 'Deferred: DEC-018'"),
           "DEC-019": ("DEFERRED to Wave 3 (research corpus)", "medium",
                       "not in DEC-083; contract.yaml names 'Docling (pinned)' as a provider of a W3 capability")}

# ---------------------------------------------------------------- the spent ones that are not plain one-offs
KEEP = {  # id: (proposal, confidence, why)
    "DEC-729": ("In force until W2-00 closes; off the spent list", "medium",
                "its item 3: commits of no other ticket carry W2-00's id, and W2-00 closes last; W2-00 (DAEO-sdxk) is open"),
    "DEC-786": ("In force (item 1, stacked starts); mark Changed by DEC-847, DEC-942; off the spent list", "medium",
                "§A: only its cap was replaced (DEC-847, then DEC-942); DEC-942 does not restate stacking; W2-55, W2-56, W2-60a cite it"),
    "DEC-924": ("In force (item 2: reports in commits of their own); off the spent list", "medium-high",
                "its status line says 'item 2 standing'; nothing lifts it"),
    "DEC-927": ("In force (item 2, re-adopted by DEC-1074 (7)); mark Changed by DEC-1057 (item 2); off the spent list",
                "medium", "DEC-1057 lifted item 2; LINK-INTEGRITY §5, adopted by DEC-1074 (7), cites it again; W2-128, W2-129, W2-130 rest on it"),
    "DEC-928": ("In force (items 1 and 3); off the spent list", "medium-high",
                "its status line says 'item 3 standing'; item 1 (CAP ids are valid Implements: targets) is how the trailer check reads"),
    "DEC-912": ("Stays ACCEPTED (product record); reword the archive line", "high",
                "the archive line itself says 'DEC-912 and DEC-918 stay product record'"),
    "DEC-918": ("Stays ACCEPTED (product record); reword the archive line", "high",
                "the archive line itself says 'DEC-912 and DEC-918 stay product record'"),
}
DONE_NOTE = {
    "DEC-063": ("medium", "its range line 'DEC-038 to DEC-063 … Spent'; its settings clean-up is done"),
    "DEC-895": ("medium", "its rules (owner entries, probe staleness) are in DEC-953's lifted list"),
    "DEC-904": ("medium", "§A: item 3's cap ended by DEC-905; the lock it kept is DEC-905's"),
    "DEC-940": ("high", "answered by DEC-941"),
    "DEC-842": ("high", "both withdrawals made; DEC-062 and DEC-140 carry their marks"),
}


def short(title: str, words: int = 12) -> str:
    head = re.split(r"[;:]\s", title)[0].strip().replace("|", "/")
    cut = head.split()
    return " ".join(cut[:words]) + ("…" if len(cut) > words else "")


def reason(archive_line: str | None) -> str:
    if not archive_line:
        return ""
    text = (archive_line.split(":", 1)[1] if ":" in archive_line else archive_line).strip().replace("|", "/")
    return text if len(text) <= 90 else text[:90].rsplit(" ", 1)[0] + " …"


rows = {r["id"]: r for r in DATA["rows"]}
groups: dict[str, list[str]] = {k: [] for k in "ABCDEFGH"}


def row(i, drifts, proposal, conf, evidence):
    return f"| {i} | {short(rows[i]['title'])} | {drifts} | **{proposal}** | {conf} | {evidence} |"


HEAD = "| Id | Title | What drifts | Proposal | Conf. | Evidence |\n|---|---|---|---|---|---|"
for i in P_AS_WRITTEN:
    note = P_NOTE.get(i, "accepted as written")
    groups["A"].append(row(i, "register still PROPOSED", "ACCEPTED (by DEC-083)", "high", f"{D083}: {note}"))
for i, by in P_REALISED.items():
    groups["B"].append(row(i, "register still PROPOSED", f"ACCEPTED as realised; mark Changed by {by}", "high",
                           f"{D083}: 'accepted as realised by later decisions'"))
for i, (by, ev) in P_SUPERSEDED.items():
    groups["C"].append(row(i, "register still PROPOSED", f"SUPERSEDED by {by}", "high", ev))
for i, (prop, conf, ev) in P_OTHER.items():
    groups["C"].append(row(i, "register still PROPOSED", prop, conf, ev))

spent = [r for r in DATA["rows"] if r["group"] == "spent"]
for r in spent:
    i = r["id"]
    drift = f"ACCEPTED; archive: '{reason(r['archive_B'])}'"
    ch = sorted({c["source"] for c in r["changers"]}, key=lambda x: int(x[4:]))
    tail = (f"; changed by {', '.join(ch)} (marks after the sitting)" if ch else "")
    if i in KEEP:
        prop, conf, why = KEEP[i]
        groups["F"].append(row(i, drift, prop, conf, why + tail))
        continue
    conf, why = DONE_NOTE.get(i, ("high", "a one-off act, finished"))
    if r["open_tickets"]:
        groups["E"].append(row(i, drift, "DONE", "medium-high" if conf == "high" else conf,
                               f"{why}; open {', '.join(t.split(' ')[0] for t in r['open_tickets'][:4])} cite it as "
                               "origin (DONE keeps the link valid)" + tail))
    else:
        where = "ARCHIVE §C (`2e5c9cd9`)" if i == "DEC-063" else ARCH
        groups["D"].append(row(i, drift, "DONE", conf, f"{where}; {why}" + tail))

n = {k: len(v) for k, v in groups.items()}
spent_done = n["D"] + n["E"]
dropped = BUILD["dropped_certainly_wrong"]
md = f"""# W2-130: the owner's one sitting — decision statuses to rule on

**For:** the owner, one sitting (DEC-1074 (7) O2 (A); DEC-1097 (9)). **By:** the CTO's helper, 2026-11-08, a draft.
Nothing here is applied. The register, the two hand lists and the tickets stay as they are until you rule.
**Read at:** `w2/integrate` `{BUILD['head'][:9]}`.

## How to read this

- **Your job:** say "accept group X" for each group you agree with, and name any row you want changed.
- **About 30 minutes** if you accept by group; the rows are there to spot one you disagree with.
- **The list:** the 110 decisions the archive calls *spent* while the register still lists them as current
  (DEC-1073 (2)), plus the 40 entries still marked PROPOSED. DEC-1074 (7)'s "150 ids" are these same two lists
  (110 + 40). The "about 110" of DEC-1073 (5)(a) is the first part of it. Then a few rows the readiness review added.
- **"Spent" today:** 109 ids come from the archive's §B; one more, DEC-063, from §C's range line "DEC-038 to
  DEC-063 … Spent". `gov links` counts 110 findings because DEC-937 sits on two §B lines.
- **What each answer does, once you rule** (the CTO applies it in one commit, then `gov links` checks):
  - **DONE:** the entry's status word ACCEPTED becomes DONE; nothing else in the entry changes. A DONE decision is a
    finished one-off, not a working rule.
  - **In force:** the register stays as it is; the archive drops the word "spent" for it.
  - **ACCEPTED / SUPERSEDED / WITHDRAWN / DEFERRED:** the PROPOSED status word is replaced by that word, naming the
    decision that settled it.
  - **Marks:** "Changed by" notes are added to the status line, in the same commit series as W2-130's marks.
- **Confidence:** high = an entry says it in words; medium = the CTO's reading of several entries.

## Summary

| Group | What | Ids | Proposal |
|---|---|---|---|
| A | PROPOSED entries DEC-083 ratified as written | {n['A']} | ACCEPTED |
| B | PROPOSED entries DEC-083 accepted as later decisions realised them | {n['B']} | ACCEPTED, with a Changed-by mark |
| C | PROPOSED entries superseded, withdrawn or deferred | {n['C']} | SUPERSEDED 5, WITHDRAWN 1, DEFERRED 2 |
| D | Spent one-offs nothing still rests on | {n['D']} | DONE |
| E | Spent one-offs an open ticket names as its origin | {n['E']} | DONE |
| F | "Spent" but still carrying a standing rule, or product record | {n['F']} | stay in force; the archive line changes |
| G | Rows the readiness review added (no status word changes) | 4 | see each |
| H | Two choices only you can make | 2 | see each |

**Totals:** {n['A'] + n['B'] + n['C'] + n['D'] + n['E'] + n['F']} decision ids: DONE {spent_done}, stay in force
{n['F']}, ACCEPTED {n['A'] + n['B']}, SUPERSEDED 5, WITHDRAWN 1, DEFERRED 2.

## A. PROPOSED, ratified as written by DEC-083 — accept as a group?

DEC-083 (owner, 30 Sep) ratified these by name; their own status lines were never updated.

{HEAD}
""" + "\n".join(groups["A"]) + f"""

## B. PROPOSED, accepted as realised by later decisions — accept as a group?

{HEAD}
""" + "\n".join(groups["B"]) + f"""

## C. PROPOSED, superseded, withdrawn or deferred — accept as a group?

DEC-013 is the one DEC-083 does not name: DEC-074's tool bake-off chose `tk` (wedow/ticket) and says it supersedes
DEC-013. DEC-019 is the one guess in this group (medium).

{HEAD}
""" + "\n".join(groups["C"]) + f"""

## D. Spent one-offs: rounds, packages, closes, re-pins — accept as a group?

Each was a single act (a round, a merge order, a refused close and its repair, a re-pin) that is finished. Where
later decisions changed them, those "Changed by" marks are added after the sitting (W2-130's last tranche).

{HEAD}
""" + "\n".join(groups["D"]) + f"""

## E. Spent one-offs that an open ticket names as its origin — accept as a group?

Same as D, but an open ticket lists the decision in its `sources:` or a KPI bracket, as where it came from. DONE
keeps that link valid: `gov links` only objects to PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED ids in rule places.

{HEAD}
""" + "\n".join(groups["E"]) + f"""

## F. "Spent" but still in force, or product record — accept as a group?

These seven should not be on the spent list. Five carry a standing rule; two are product record, which the archive's own line says.

{HEAD}
""" + "\n".join(groups["F"]) + f"""

## G. Rows the readiness review added (reviewer 2, `reviews/readiness-2-links.md`)

| Row | What drifts | Proposal | Conf. | Evidence |
|---|---|---|---|---|
| MR-1 to MR-6 | the generated `docs/contract/master-rules/MR-n.md` say PROPOSED; `contract.yaml` says ACCEPTED; a search marks every master rule "not in force" | **Regenerate the six files from `contract.yaml`** (product-spec, before the release; no ruling on the rules themselves) | high | `gov links` STATUS_CONFLICT ×6; reviewer 2 F1; DEC-1074 (8)'s MR row |
| CONDITIONAL and DONE read as in force | DEC-020 (RAGFlow, CONDITIONAL) and DEC-056, DEC-071, DEC-077, DEC-078, DEC-079 (DONE) show "in force" in a search | **Confirm: DONE = not in force; CONDITIONAL = not in force until its trigger fires.** Then a code row for W2-92's status mark (D-6). No register change | high | reviewer 2 F5; W2-55's own rule: a done entry "is not in force" |
| Wrong "changed by" links | the loader reads a "Changed by:" note with no verb, or a clause with no subject, as naming changers: 11 links have a changer older than the decision it "changes" (e.g. DEC-880 <- DEC-843) | **Approve: no mark is committed on them** ({len(dropped)} would have been: {', '.join(d['entry'] + ' <- ' + d['changer'] for d in dropped)}); **the loader's fix is a D-6 row** (one changer per clause, by its leading id). The register's text is not edited | high | reviewer 2 F2; the list with a fix per link: `drafts/w2-130/e-spurious-changers.md` |
| ADR-0002 (PROPOSED file) | the architecture ADR is still PROPOSED | **Not in this sitting:** DEC-1097 (8) already brings its refresh to you before the lift | high | DEC-1093 (3), DEC-1097 (8) |

## H. Two choices only you can make

**H1. Closed tickets' `sources:`.** W2-130's patch adds 875 missing decision ids to 154 tickets. 104 of the tickets
are closed (481 ids). Since DEC-1088 (6), editing a closed ticket is itself a finding, "a decision id does not excuse
the edit", so that half would add 104 permanent CLOSED_TICKET_EDITED findings.
- (a) Allow this one links-only commit on closed tickets, named in the record. 0 UNLINKED_ID afterwards, 104 standing S16 findings.
- **(b) Recommended (medium):** link the 50 open and in-progress tickets only (394 ids). List the closed tickets'
  ids in W2-130's record. Change W2-130's KPI 4 to say "open and in-progress tickets". 1,097 UNLINKED_ID stay as
  history on closed tickets. Retrieval already reaches those ids through the commits.

**H2. The marks the auditor finds wrong.** The 180 marks go through an independent auditor first (KPI 3). 30
carry a mechanical warning (`drafts/w2-130/marks-audit.md`), for example the archive line that gives five decisions
four changers at once (DEC-454 to DEC-492).
- **Recommended:** a wrong mark is dropped. Where the archive's §A wording caused it, the line is rewritten one
  decision per line, with only the changer that decision's own entry names. W2-130's allowed paths include the archive.
- No allow-list, as LINK-INTEGRITY §9 says. Any finding left over is named in the record.

## What happens after you rule

1. The CTO applies your statuses in one commit: the register's status words, the archive and DECISIONS-IN-FORCE
   made to agree.
2. `gov links --propose-marks` is regenerated, because a decided status changes who counts as a changer:
   PROPOSED entries count once they are ACCEPTED.
3. The marks go to the auditor, then into commits: no-hint first ({BUILD['a1']['entries']} entries), then the rest.
4. Then the `sources:` commit, as you choose in H1.
5. Expected afterwards (measured on a scratch copy): STATUS_CONFLICT 116 → 0; UNMARKED_CHANGE 185 → 5 (the
   wrong links, until the loader row); UNLINKED_ID 1,877 → 1,097 with H1 (b), or → 0 with H1 (a).
"""
OUT.write_text(md)
print(n, "spent", len(spent))
