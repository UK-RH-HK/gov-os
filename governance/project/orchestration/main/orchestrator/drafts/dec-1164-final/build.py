#!/usr/bin/env python3
"""Builds the DEC-1164 final patches from the draft (drafts/dec-1164-dif-supersede.md) and the owner's six corrections
of 2026-11-13. Reads the repository, writes only into this folder (patched copies go to a temp folder given by --tmp).

    python3 build.py --tmp <empty folder>

Every replacement asserts that its old text occurs exactly once; a gone target stops the build and is named.
"""
import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
OUT = Path(__file__).resolve().parent
DRAFT = ROOT / ".gov-runtime/scratch/orchestrator/drafts/dec-1164-dif-supersede.md"
REG = "docs/DECISION_REGISTER.md"
DIF = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
ARC = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"
PROMPT = "governance/project/prompts/w2-orchestrator.md"

problems = []


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        problems.append(f"{label}: old text occurs {n} times: {old[:90]!r}")
        return text
    return text.replace(old, new, 1)


def udiff(rel, a, b, context=3):
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), f"a/{rel}", f"b/{rel}", n=context))


def read(rel):
    return (ROOT / rel).read_text()


draft = DRAFT.read_text()


def section(start, end):
    i = draft.index(start)
    j = draft.index(end, i)
    return draft[i:j]


# --------------------------------------------------------------------------------------------- entry
S1 = section("### DEC-1164 —", "**The version table row**")
entry_lines = S1.rstrip("\n").split("\n")
entry = "\n".join(entry_lines)

# heading
entry = once(entry, "the prompt's lifted and spent holds removed (standing for (4), (5), (9)-(19))",
             "the prompt's lifted and spent holds removed; the owner's asleep clause restored (standing for (4), (5), (9)-(19), (23))", "E heading")

# status line, whole
i = entry.index("- **Status:**")
j = entry.index("\n", i)
old_status = entry[i:j]
new_status = old_status
new_status = once(new_status,
                  "PROPOSED (the CTO, 2026-11-13, for the owner's acceptance; on acceptance it reads: ACCEPTED (owner, 2026-11-13, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`); (4), (5), (9)-(19) standing)",
                  "ACCEPTED (owner, 2026-11-13, in the chat ~16:00; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-13)`); (4), (5), (9)-(19), (23) standing",
                  "E status")
new_status = once(new_status, "DEC-1052 (the basis) ·", "DEC-1052 (the basis), DEC-1156 (8) (for (23)) ·", "E under")
new_status = once(new_status, "DEC-1104 (2), DEC-1157 (2) ·", "DEC-1104 (2), DEC-1157 (1) ((23): the asleep clause), DEC-1157 (2) ·", "E changes")
new_status = once(new_status, "DEC-1087 (1)-(11), DEC-1097 (1)(g), (9),",
                  "DEC-1087 (1)-(11), DEC-1093 (1)'s close form for W2-139 and W2-140, DEC-1097 (1)(g), (9),", "E spent")
entry = entry.replace(old_status, new_status, 1)

# (1): correction 1
entry = once(entry,
             "**Also kept:** DEC-1093 (1)'s close form for W2-139 and W2-140 (both still open, so not spent); DEC-1159 (1)'s \"nightly.sh takes the heavy slots and the rebuild lock itself\" (decided after the sweep, which proposed dropping that lock: not done here).",
             "**Also kept:** DEC-1159 (1)'s \"nightly.sh takes the heavy slots and the rebuild lock itself\" (decided after the sweep, which proposed dropping that lock: not done here). **Not kept (spent):** W2-139 and W2-140 were closed on 2026-11-13 by DEC-953's practice, so DEC-1093 (1)'s close form for them is spent.",
             "E (1)")
# (3): correction 2
entry = once(entry,
             "sandboxed searches are unranked, named and counted (DEC-1114 (3)), and the cache's write by its ACT (DEC-1163 (9)). Its other half,",
             "sandboxed searches are unranked, named and counted (DEC-1114 (3)); the cache-write ACT of DEC-1163 (9) was withdrawn by DEC-1167 (7) (it changed only the error text); sandboxed searches name the true cause since the reranker log fix (79159cd44). Its other half,",
             "E (3)")
# (7): the spent close form
entry = once(entry,
             "all done; its (13), the three layers in Wave 2, stays); DEC-1097 (1)(g)'s",
             "all done; its (13), the three layers in Wave 2, stays); DEC-1093 (1)'s close form for W2-139 and W2-140 (both closed on 2026-11-13, see (1)); DEC-1097 (1)(g)'s",
             "E (7)")
# (11): the asleep clause where a yes is still to be asked
entry = once(entry,
             "or a (b) ACT a lead waits on whose owner's yes is recorded (DEC-1157 (1)).\"**",
             "or a (b) ACT a lead waits on whose owner's yes is recorded (DEC-1157 (1)).\"** Where a lead waits on the owner's yes itself, the push is DEC-1157 (1)'s, subject to (23).",
             "E (11)")
# (17): correction 6
entry = once(entry,
             "then the CTO pushes the owner (DEC-1157 (1)) and runs it, the owner approving through Remote Control.\"",
             "then the CTO pushes the owner (DEC-1157 (1)) and runs it, the owner approving through Remote Control, unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package.\"",
             "E (17)")
# (21)
entry = once(entry,
             "word for word as listed in this entry's package (`drafts/dec-1164-dif-supersede.md` §4).",
             "word for word as in `.gov-runtime/scratch/orchestrator/drafts/dec-1164-final/prompt.patch` (the draft's §4 with the owner's corrections of 2026-11-13: DEC-946's \"Nothing else starts\" paragraph deleted with its priorities; the pre-close gate paragraph reduced to one line, lifted on this repository with the close windows (DEC-953); and (23)'s asleep clause added in the two places where the prompt says a decision that stops or delays a lead goes or pings at once, at any hour).",
             "E (21)")
# (22)
entry = once(entry,
             "the DEC-866 marks in this entry's commit (§2 of the package), with three missed marks corrected:",
             "the DEC-866 marks in this entry's commit (`drafts/dec-1164-final/marks.patch`: 31 entries, DEC-1093's for (1) and (7) and DEC-1157's for (4) and (23) among them), with three missed marks corrected:",
             "E (22) marks")
entry = once(entry, "(its twenty \"(the 09:00 sweep: …)\" markers replaced)", "(its \"(the 09:00 sweep: …)\" markers replaced)", "E (22) twenty")
entry = once(entry, "START-NEXT-SESSION's next free id and sweep line;", "START-NEXT-SESSION's next free id (DEC-1171) and sweep line;", "E (22) next id")
# (23) and the basis
item23 = ("  - (23) **The owner's asleep clause (standing):** a decision that stops or delays a lead goes to the owner at once, at any hour, "
          "unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package. Changes DEC-1157 (1)'s wording accordingly.")
entry = once(entry, "\n- **Basis:**", "\n" + item23 + "\n- **Basis:**", "E (23)")
i = entry.index("- **Basis:**")
entry = entry[:i] + (
    "- **Basis:** the CTO's sweep (DEC-1157 (16)) and DEC-1163 (9) (\"The CTO brings the DIF sweep's supersede entry\"); questions 2 and 4 of DEC-1052's basis "
    "(nothing here lets ordinary work fail open or lose work; each removed hold cost lead-hours or would freeze work). The owner's acceptance, in the chat of "
    "2026-11-13 (~16:00), verbatim: \"yes DEC-1164, with your five corrections and one more: wherever the prompt says a decision that stops a lead pings me "
    "\"at once, at any hour\", add \"unless I have said I am asleep (DEC-1156 (8)); then it waits for the morning package\".\"")

VERSION_ROW = ("| 0.551 | 2026-11-13 | Owner (recorded by the orchestrator, DEC-861): DEC-1164 (the DIF sweep decided: DEC-946's priorities and the operator's "
               "night sleep superseded; thirteen rules amended; the spent sequencing archived; the prompt's lifted holds removed; the owner's asleep clause "
               "for a decision that stops or delays a lead, (23); DEC-866 marks on 31 entries). Next free id: DEC-1171. |")

(OUT / "entry.md").write_text(
    entry + "\n\n---\n\nVersion-table row (append after the register's last row; the CTO's 0.550 for DEC-1170 comes before it):\n\n" + VERSION_ROW + "\n")

# --------------------------------------------------------------------------------------------- marks
MARKS = [  # (entry id, text appended to the end of its status line)
    (1052, ', DEC-1164 (2) (the plan bullet and "Tonight" spent; D-11 its own line)'),
    (1055, " · **Changed by:** DEC-1164 (2) (its order and (8)-(10) spent: D-4 to D-10 done)"),
    (1064, " · **Changed by:** DEC-1164 (3) (item (2)'s hold until W2-127 met; no private embedder stays as DEC-1065)"),
    (1141, " · **Superseded by:** DEC-1164 (4) (item (6): the operator runs every hour, ACT-OPERATOR-HOURS-3)"),
    (1142, " · **Superseded by:** DEC-1164 (4) (item (5): HOURS-1 and -2's hours, retired by ACT-OPERATOR-HOURS-3)"),
    (1104, ", DEC-1164 (4) (the operator's hours: every hour, ACT-OPERATOR-HOURS-3)"),
    (1157, " · **Changed by:** DEC-1164 (4) (item (2)'s interim operator sleep, spent once ACT-OPERATOR-HOURS-3 is applied), DEC-1164 (23) (item (1): a decision that stops or delays a lead goes at once, at any hour, unless the owner has said they are asleep, DEC-1156 (8); then it waits for the morning package)"),
    (1018, ", DEC-1164 (5) (item 1's no commit and no file: from 03:55, not 03:15)"),
    (946, " · **Superseded by:** DEC-1164 (6) (items 1-6, 8, 9; item 7 kept; item 10 done)"),
    (1086, ", DEC-1164 (7) (D spent: window 4 done, DEC-1089)"),
    (1087, " · **Changed by:** DEC-1164 (7) ((1)-(11) spent; (13) stays)"),
    (1093, " · **Changed by:** DEC-1164 (1), (7) (item (1)'s close form for W2-139 and W2-140 spent: both closed on 2026-11-13 by DEC-953's practice)"),
    (1097, " · **Changed by:** DEC-1164 (7) ((1)(g)'s and (9)'s holds for the 80 spent)"),
    (1098, " · **Changed by:** DEC-1164 (7) ((6) spent at the lift)"),
    (1115, "; item (4) spent at the lift, DEC-1164 (7)"),
    (1122, " · **Changed by:** DEC-1126 (2) ((2): usage (A) ended at the lift; marked by DEC-1164 (22)), DEC-1164 (7) ((3) spent: D-10 done)"),
    (1039, ', DEC-1164 (8) (item 1b\'s "even if that limits leads to two or three" deleted)'),
    (1038, ", DEC-1164 (9) (item 4's last sentence: slots from the machine, re-sized from the wait log)"),
    (979, ", DEC-1164 (9) (D1's slots re-sized from the wait log; a starved slot released by the CTO)"),
    (1057, " · **Changed by:** DEC-1164 (10) (item (5): scoped tests permanently, no full run per settings ACT)"),
    (925, ", DEC-1164 (10) (item 2's full run after D-10)"),
    (1058, " · **Changed by:** DEC-1164 (11) ((b)'s quiet hours: a (b) ACT a lead waits on, the yes recorded)"),
    (1053, " · **Changed by:** DEC-1164 (12) (item (6): the CTO disposes of the branches now)"),
    (1067, ", DEC-1164 (13) (GPU safety: a measure and a rebuild never use the GPU at the same time)"),
    (1028, ", DEC-1164 (14) (item 6: G9 holds only an ACT whose paths overlap)"),
    (902, " · **Changed by:** DEC-1164 (15) (item 1: the sweep at any time)"),
    (991, ", DEC-1164 (17) (item 3: a call a lead waits on runs at any hour after a push, unless the owner has said they are asleep, DEC-1164 (23))"),
    (1088, ", DEC-1164 (18) (item (6): a defect inside a closed ticket's own scope reopened by the CTO)"),
    (989, "; DEC-1164 (19) (item 2: a critical-path ticket lands first)"),
    (847, " · **Changed by:** DEC-1149 (3) (the usage-limit bullet: usage never holds a lead; marked by DEC-1164 (22))"),
    (949, ", DEC-1157 (1) (items 1-2: a decision that stops or delays a lead goes at any hour, unless the owner has said they are asleep, DEC-1164 (23); marked by DEC-1164 (22))"),
]
MARKS_EXTRA = [  # optional, outside the draft's list
    (1156, ", DEC-1164 (23) (item (8) restored: the owner's asleep clause for a decision that stops a lead)"),
]

reg_old = read(REG)


def apply_marks(text, marks, label):
    lines = text.split("\n")
    for n, add in marks:
        heads = [k for k, l in enumerate(lines) if l.startswith(f"### DEC-{n} ")]
        if len(heads) != 1:
            problems.append(f"{label}: DEC-{n} heading found {len(heads)} times")
            continue
        k = heads[0] + 1
        if not lines[k].startswith("- **Status:**"):
            problems.append(f"{label}: DEC-{n} has no status line right after its heading")
            continue
        if add in lines[k]:
            problems.append(f"{label}: DEC-{n} already carries this mark")
            continue
        lines[k] = lines[k] + add
    return "\n".join(lines)


reg_marked = apply_marks(reg_old, MARKS, "marks")
(OUT / "marks.patch").write_text(udiff(REG, reg_old, reg_marked))

# the DEC-1165 note and DEC-1156's mark: optional, own patch
reg_extra = apply_marks(reg_old, MARKS_EXTRA, "marks-extra")
reg_extra = once(reg_extra, " · DEC-1164 is held: drafted, PROPOSED, waiting for the owner's reading", " · DEC-1164 was held until the owner accepted it (2026-11-13, ~16:00)", "marks-extra 1165")
(OUT / "marks-extra.patch").write_text(udiff(REG, reg_old, reg_extra))

# --------------------------------------------------------------------------------------------- DIF
S3a = section("### 3a. Replacements", "### 3b. Additions")
fences = re.findall(r"```(dif-old|dif-new)\n(.*?)\n```", S3a, flags=re.S)
pairs, standalone, k = [], [], 0
while k < len(fences):
    t, s = fences[k]
    if t == "dif-old":
        assert fences[k + 1][0] == "dif-new"
        pairs.append((s, fences[k + 1][1]))
        k += 2
    else:
        standalone.append(s)
        k += 1
assert len(standalone) == 2, len(standalone)  # B9's added bullet; DEC-1087's replacement
b9_new, dec1087_new = standalone

dif_old = read(DIF)
dif = dif_old


def pair_new_override(old, new):
    if old.startswith("and to DEC-1159 on 2026-11-13"):
        new = once(new, "register v0.545", "register v0.551", "DIF header")
    if old.startswith("quiet hours, DEC-1144 (7)). The quiet-hours ban"):
        new = once(new, "pushes the owner and runs it at any hour\n  (DEC-1164 (17), DEC-1157 (1)).",
                   "pushes the owner and runs it at any hour,\n  unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package (DEC-1164 (17), (23)).", "DIF B17")
    if old.startswith("  Basis: 2. The spent W2-139/W2-140 sequencing"):
        new = "  Basis: 2. (W2-139 and W2-140 closed on 2026-11-13 by DEC-953's practice: their close form is spent, DEC-1164 (1).)"
    return new


for old, new in pairs:
    dif = once(dif, old, pair_new_override(old, new), "DIF pair " + old[:40].strip())

# DEC-1093's bullet: the one-batch close form is spent (correction 1)
dif = once(dif, "  tests) merge and close in one batch, one green run, outside an experiment window; DEC-841's nine to P1-11, else",
           "  tests), closed on 2026-11-13 by DEC-953's practice (the one-batch close form spent, DEC-1164 (1)); DEC-841's nine to P1-11, else",
           "DIF 1093 body")

# the DEC-1086 bullet: delete; the DEC-1087 bullet: replace
lines = dif.split("\n")


def bullet_span(lines, start_text):
    s = [i for i, l in enumerate(lines) if l.startswith(start_text)]
    if len(s) != 1:
        problems.append(f"DIF bullet {start_text[:30]!r} found {len(s)} times")
        return None
    e = s[0] + 1
    while e < len(lines) and not lines[e].startswith("- ") and not lines[e].startswith("## "):
        e += 1
    while lines[e - 1].strip() == "":
        e -= 1
    return s[0], e


span = bullet_span(lines, "- DEC-1086 (2026-11-06; its C's cap changed by DEC-1091 (1): no cap)")
if span:
    assert "recommended to supersede" in "\n".join(lines[span[0]:span[1]])
    del lines[span[0]:span[1]]
span = bullet_span(lines, "- DEC-1087 (2026-11-06): before re-pin window 4")
if span:
    block = "\n".join(lines[span[0]:span[1]])
    assert "recommended to supersede" in block and "After the re-pin" in block
    lines[span[0]:span[1]] = dec1087_new.split("\n")
dif = "\n".join(lines)

# B9's bullet, after the DEC-1045 bullet
dif = once(dif, "- DEC-1045: no gitleaks scan here (`secrets.yaml` `scan: off`); a weekly full scan only on the owner's approval.\n",
           "- DEC-1045: no gitleaks scan here (`secrets.yaml` `scan: off`); a weekly full scan only on the owner's approval.\n" + b9_new + "\n", "DIF B9 insert")

# Lifted: the DEC-1164 bullet (3b), with DEC-1093's close form among the spent; DEC-1156 (8)'s clause restored
S3b = section("### 3b. Additions", "### 3c. Beside the DIF")
lifted_new, end_new = re.findall(r"```dif-new\n(.*?)\n```", S3b, flags=re.S)
lifted_new = once(lifted_new, "DEC-1087 (1)-(11); DEC-1097 (1)(g)", "DEC-1087 (1)-(11); DEC-1093 (1)'s close form for W2-139 and W2-140 (closed 2026-11-13); DEC-1097 (1)(g)", "DIF lifted 1093")
dif = once(dif, "- DEC-1159 (2026-11-13): DEC-1132 (4)'s \"with nothing else running\" for leads (the nightly runs beside them).\n",
           "- DEC-1159 (2026-11-13): DEC-1132 (4)'s \"with nothing else running\" for leads (the nightly runs beside them).\n" + lifted_new + "\n", "DIF lifted insert")

# the DEC-1164 line, after the DEC-1159 bullet (before DEC-1168's, which the CTO's later lines follow)
end_new = once(end_new, "(2026-11-13, (4), (5), (9)-(19) standing)", "(2026-11-13, (4), (5), (9)-(19), (23) standing)", "DIF end header")
end_new = once(end_new, "tickets land first; the runs sweep back by ACT; spent sequencing archived; the prompt's lifted holds removed. Basis:\n  the owner's acceptance of the sweep.",
               "tickets land first; the runs sweep back by ACT; spent sequencing archived (DEC-1093 (1)'s close form for W2-139 and W2-140 among it);\n  the prompt's lifted holds removed; **a decision that stops or delays a lead goes to the owner at once, at any hour, unless the\n  owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package** ((23)). Basis: the owner's acceptance of\n  the sweep, 2026-11-13.", "DIF end body")
dif = once(dif, "  requests above its limit outside a GPU window.** Basis: the owner's answers (no question named).\n- DEC-1168",
           "  requests above its limit outside a GPU window.** Basis: the owner's answers (no question named).\n" + end_new + "\n- DEC-1168", "DIF end insert")

# (23) in the lines that state the night push rule
dif = once(dif, "delays a lead comes to the owner at once, at any hour, as a full package (DEC-1157 (1)).**",
           "delays a lead comes to the owner at once, at any hour, as a full package (DEC-1157 (1)), unless the owner has said they are\n  asleep (DEC-1156 (8)); then it waits for the morning package (DEC-1164 (23)).**", "DIF 36")
dif = once(dif, "except a decision that stops or delays a lead (DEC-1157 (1)); an emergency pings",
           "except a decision that stops or delays a lead (DEC-1157 (1)), unless the owner has said they are asleep (DEC-1156 (8)); then it waits for\n  the morning package (DEC-1164 (23)); an emergency pings", "DIF 38")
dif = once(dif, "**DEC-1156 (8)** (night pushes \"until the owner says they are asleep\": now at any hour, DEC-1157 (1));",
           "**DEC-1156 (8)** (night pushes \"until the owner says they are asleep\": at any hour, DEC-1157 (1); the asleep clause restored, DEC-1164 (23));", "DIF 161")
dif = once(dif, "- DEC-1156 (2026-11-12, (7) standing; (8) superseded by DEC-1157 (1)):", "- DEC-1156 (2026-11-12, (7) standing; (8) superseded by DEC-1157 (1), restored by DEC-1164 (23)):", "DIF 679")
dif = once(dif, "  at once, at any hour, as a full package; (2) no night hold", "  at once, at any hour, as a full package (unless the owner has said they are asleep, DEC-1164 (23)); (2) no night hold", "DIF 688")

# the archive
arc_old = read(ARC)
S3c = section("### 3c. Beside the DIF", "**`START-NEXT-SESSION.md`:**")
arc_sec = re.findall(r"```dif-new\n(.*?)\n```", S3c, flags=re.S)[0]
arc_sec = once(arc_sec, "- DEC-1097 (1)(g), (9):", "- DEC-1093 (1)'s one-batch close form for W2-139 and W2-140: spent, both closed on 2026-11-13 by DEC-953's practice (DEC-1164 (1), (7)).\n- DEC-1097 (1)(g), (9):", "ARC 1093")
arc_new = arc_old.rstrip("\n") + "\n\n" + arc_sec + "\n"
(OUT / "dif.patch").write_text(udiff(DIF, dif_old, dif) + udiff(ARC, arc_old, arc_new))

# --------------------------------------------------------------------------------------------- prompt
head = subprocess.run(["git", "-C", str(ROOT), "show", f"e93d846a8:{PROMPT}"], capture_output=True, text=True, check=True).stdout
p_work = read(PROMPT)
if head != p_work:
    problems.append("the prompt in the tree is not the file of e93d846a8")
S4 = section("## 4. The owner's prompt edit", "## 5. Not settled here")
f4 = re.findall(r"```(prompt-old|prompt-new)\n(.*?)\n```", S4, flags=re.S)
ppairs, k = [], 0
while k < len(f4):
    assert f4[k][0] == "prompt-old"
    if k + 1 < len(f4) and f4[k + 1][0] == "prompt-new":
        ppairs.append((f4[k][1], f4[k + 1][1]))
        k += 2
    else:
        ppairs.append((f4[k][1], None))
        k += 1
assert len(ppairs) == 30 and sum(1 for p in ppairs if p[1] is None) == 3

prompt = head
for n, (old, new) in enumerate(ppairs):
    if prompt.count(old) != 1:
        problems.append(f"prompt pair {n}: old text occurs {prompt.count(old)} times: {old[:80]!r}")
        continue
    if new is None:
        idx = prompt.index(old)
        if (idx == 0 or prompt[idx - 1] == "\n") and prompt[idx + len(old):idx + len(old) + 1] == "\n":
            prompt = prompt[:idx] + prompt[idx + len(old) + 1:]
        else:
            prompt = prompt.replace(old, "", 1)
    else:
        prompt = prompt.replace(old, new, 1)

# correction 4: DEC-946's "Nothing else starts" paragraph, deleted with the priorities
m = re.search(r"^  \*\*Nothing else starts\.\*\* .*\n", prompt, flags=re.M)
if not m or len(re.findall(r"^  \*\*Nothing else starts\.\*\* ", prompt, flags=re.M)) != 1:
    problems.append("prompt: the 'Nothing else starts' paragraph not found once")
else:
    prompt = prompt[:m.start()] + prompt[m.end():]

# correction 5: the pre-close gate paragraph reduced to one line
m = re.search(r"^- \*\*The pre-close gate \(owner, standing, DEC-868\), until W2-07 builds it into `gov close`:\*\*.*\n", prompt, flags=re.M)
if not m:
    problems.append("prompt: the pre-close gate paragraph not found")
else:
    prompt = prompt[:m.start()] + ('- **The pre-close gate (DEC-868):** lifted on this repository with the close windows (DEC-953; DECISIONS-IN-FORCE, "Lifted"); '
                                   'built into `gov close` in the product (W2-07).\n') + prompt[m.end():]

# correction 6: the owner's asleep clause where the prompt says a decision that stops or delays a lead goes or pings at once
prompt = once(prompt,
              "Every decision that stops or delays a lead goes at once, at any hour (DEC-1157 (1)); any other blocking P1",
              "Every decision that stops or delays a lead goes at once, at any hour (DEC-1157 (1)), unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package; any other blocking P1",
              "prompt asleep 1")
prompt = once(prompt,
              "nothing pings but a decision that stops or delays a lead (DEC-1157 (1)) and an emergency.",
              "nothing pings but an emergency and a decision that stops or delays a lead (DEC-1157 (1)), unless the owner has said they are asleep (DEC-1156 (8)); then it waits for the morning package.",
              "prompt asleep 2")
prompt = once(prompt, "v3.73: DEC-1158 (4), DEC-1164 (21): the lifted and spent holds removed)", "v3.73: DEC-1158 (4), DEC-1164 (21), (23): the lifted and spent holds removed; the owner's asleep clause)", "prompt version")

(OUT / "prompt.patch").write_text(udiff(PROMPT, head, prompt, 3))
(OUT / "prompt-U1-phone.diff").write_text(udiff(PROMPT, head, prompt, 1))

# --------------------------------------------------------------------------------------------- patched copies for the placeholder scan
ap = argparse.ArgumentParser()
ap.add_argument("--tmp", required=True)
args = ap.parse_args()
tmp = Path(args.tmp)
for rel, text in ((REG, None), (DIF, dif), (ARC, arc_new), (PROMPT, prompt)):
    p = tmp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if rel == REG:
        r = reg_marked
        r = once(r, "### DEC-1165 —", entry + "\n\n### DEC-1165 —", "temp register insert")
        r = r.rstrip("\n") + "\n" + VERSION_ROW + "\n"
        text = r
    p.write_text(text)
(tmp / "register-before.md").write_text(reg_old)

if problems:
    print("PROBLEMS:")
    for x in problems:
        print("  -", x)
    sys.exit(1)
print("build ok")
