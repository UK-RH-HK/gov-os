"""DEC-950: files W2-84 (tk create, the draft written in place), adds its card to the plan, makes W2-61h depend on it,
amends W2-20's ticket for its run 3, and parks W3-P11. Writes log/tickets-2026-10-29c.json. Safe to re-run only for
the parts not yet done (each checks)."""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
D = ROOT / ".gov-runtime/scratch/orchestrator/drafts"
MAP = ROOT / ".gov-runtime/scratch/orchestrator/log/tickets-2026-10-29c.json"

if MAP.exists():
    tid = json.loads(MAP.read_text())["W2-84"]
else:
    text = (D / "tickets/W2-84.md").read_text(encoding="utf-8")
    title = re.search(r"^title: '(.*)'$", text, re.M).group(1).replace("''", "'")
    tid = subprocess.run(["tk", "create", title, "-p", "1", "--external-ref", "W2-84"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip().split()[-1]
    path = ROOT / ".tickets" / (tid + ".md")
    created = re.search(r"^created: (\S+)$", path.read_text(encoding="utf-8"), re.M).group(1)
    path.write_text(text.replace("ID-PLACEHOLDER", tid).replace("CREATED-PLACEHOLDER", created), encoding="utf-8")
    MAP.write_text(json.dumps({"W2-84": tid}) + "\n", encoding="utf-8")
print("W2-84", tid)


def edit(p, pairs):
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if new in t:
            continue
        if t.count(old) != 1:
            sys.exit(p.name + ": not found once: " + old[:70])
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8")


wbs = ROOT / "docs/plan/WAVE_2_WBS.md"
card = (D / "tickets/card-84.md").read_text(encoding="utf-8").strip()
head_end = card.index("\n")
card = card[:head_end] + "\n- **Ticket file:** `" + tid + "`." + card[head_end:]
edit(wbs, [("## 3. Order, layers and critical path", "### DEC-950: the hidden-set refusal in every tree\n\n" + card +
            "\n\n## 3. Order, layers and critical path")])
edit(ROOT / ".tickets/DAEO-h2k3.md", [("depends_on: []", "depends_on: [" + tid + "]")])
r30l = ROOT / ".tickets/DAEO-r30l.md"
adds = [
    "'The gate opens on load only while min(1-minute load, 15-minute load) < nproc: a short peak does not shut it; both at or above nproc does [DEC-942 item 2, DEC-942 item 3, DEC-950 item 2]'",
    "'The gate opens on memory only while MemAvailable plus the running sessions'' live memory (each one''s whole process tree, read at the check) is at least the floor + one verification run''s peak (reserved once) + a working size for each running session and for the new one; a session inside another live session''s process tree is counted in that one and charged no working size of its own [DEC-947, DEC-942 item 2, DEC-950 item 2]'",
    "'No fixed number: no ceiling on leads or sessions, weighted or not; only the load, memory, disk, inode and (for a start that declares one) GPU conditions shut the gate [DEC-942 item 1, DEC-950 item 2]'",
    "'All values in one configuration file (floor, verification peak, working size, disk and inode floors, verification lock, GPU margin), each with its date and source; a value missing or malformed shuts the gate, naming it; the reading names a measured figure older than seven days as due for re-measure [DEC-947 item 3, DEC-950 item 2]'",
    "'The re-measure: gov resources records samples of each live session''s process-tree memory, noting whether a verification run holds the configured lock, and from them writes the verification peak (largest sample) and the working size (largest outside verification) with the date into the configuration file, showing old and new side by side [DEC-947 items 2 and 3, DEC-950 item 2]'",
    "'GPU, minimal: a start that declares a GPU need opens only when a GPU''s free memory, read with nvidia-smi, is at least the need plus 10%; no nvidia-smi or no GPU shuts such a start, named; a start with no declared need never reads the GPU [DEC-950 item 2, DEC-941 item 6]'",
]
fails = ["'Any fixed ceiling on leads or sessions.'",
         "'A value the gate uses not taken from the configuration file, or a reading that cannot be taken treated as met.'",
         "'A worker''s memory charged twice (in its lead''s tree and as its own session).'"]
t = r30l.read_text(encoding="utf-8")
if "DEC-950 item 2" not in t:
    t = t.replace("(100 GiB and 10,000,000 by default, set in the project configuration)",
                  "(100 GiB and 10,000,000, set in the gate's one configuration file)", 1)
    t = t.replace("  failure:\n", "".join("  - " + a + "\n" for a in adds) + "  failure:\n", 1)
    t = t.replace("profile: STANDARD\n", "".join("  - " + f + "\n" for f in fails) + "profile: STANDARD\n", 1)
    t = t.replace("- DEC-898\nest_loc: 140\n", "- DEC-898\n- DEC-941\n- DEC-942\n- DEC-947\n- DEC-950\nest_loc: 320\n", 1)
    old = re.search(r"^- \*\*The values \(DEC-742, 2026-10-17\):\*\*.*$", t, re.M)
    if not old:
        sys.exit("W2-20: the values line not found")
    t = t.replace(old.group(0), "- **The values (DEC-942 item 2 and DEC-947, replacing DEC-742's; DEC-950 item 2):** floor 3 GiB; "
                  "one verification peak reserved once; a working size per running session and the new one, re-measured "
                  "weekly; min(1-, 15-minute load) below `nproc`; disk and inode floors (DEC-898); no session ceiling; a "
                  "GPU check only for a declared need (+10%); all in one configuration file.")
    t = t.replace("DEC-742's load value stands (P-C).", "DEC-742's load value stands (P-C). P-B's \"at most 8\" superseded by DEC-942 item 1.", 1)
    if t.count("DEC-950 item 2") < 6 or "est_loc: 320" not in t:
        sys.exit("W2-20: an edit did not apply")
    r30l.write_text(t, encoding="utf-8")
    print("W2-20 amended")
park = ROOT / "docs/plan/WAVE_3_PARKING.md"
p = park.read_text(encoding="utf-8")
if "W3-P11" not in p:
    row = ("| W3-P11 | The same tree-rooting gap for a ticket's own acceptance tests and changed files (Policy 2 (a), (c)): "
           "`parts()` refuses them only in the session's own tree, so a copy in the main tree or another worktree is "
           "readable; low risk, since a ticket's tests reach the main tree only after it is built (found while drafting "
           "W2-84) | the W2-84 drafting helper | 2026-10-29 |")
    p = p.replace("\n\nNot parked:", "\n" + row + "\n\nNot parked:", 1)
    park.write_text(p, encoding="utf-8")
    print("W3-P11 parked")
