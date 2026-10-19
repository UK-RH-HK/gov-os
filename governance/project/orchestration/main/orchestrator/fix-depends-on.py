"""DEC-614: rewrite depends_on in the ticket files from work-breakdown ids (W1-05) to record ids (DAEO-...).

Only the lines of the depends_on block change; every other byte of a ticket file stays. A W1 id with no ticket stops the
script before anything is written.
"""
import glob
import re
import sys
import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
files = sorted(glob.glob(ROOT + ".tickets/*.md"))
fronts = {}
for path in files:
    text = open(path, encoding="utf-8").read()
    fronts[path] = (text, yaml.safe_load(text.split("\n---\n")[0].split("---\n", 1)[1]))
idof = {front["wbs_id"]: front["id"] for _, front in fronts.values() if front.get("wbs_id")}
plan, unknown = {}, []
for path, (text, front) in fronts.items():
    lines = text.split("\n")
    end = lines.index("---", 1)
    out, inside, changed = [], False, 0
    for number, line in enumerate(lines):
        if number < end and line.startswith("depends_on:"):
            inside = True
            inline = re.fullmatch(r"depends_on: \[(.*)\]", line)
            if inline and inline.group(1).strip():
                ids = [x.strip() for x in inline.group(1).split(",")]
                unknown += [x for x in ids if x.startswith("W1-") and x not in idof]
                line = "depends_on: [" + ", ".join(idof.get(x, x) for x in ids) + "]"
                changed += 1
        elif number < end and inside and re.fullmatch(r"- (W1-[0-9]+)", line):
            wbs = line[2:]
            if wbs not in idof:
                unknown.append(wbs)
            else:
                line = "- " + idof[wbs]
                changed += 1
        elif number < end and inside and not line.startswith("- "):
            inside = False
        out.append(line)
    if changed:
        plan[path] = "\n".join(out)
if unknown:
    sys.exit(f"no ticket for {sorted(set(unknown))}: nothing written")
for path, text in plan.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
print("ticket files rewritten:", len(plan), "of", len(files))
