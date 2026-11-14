import json, glob, yaml, re, collections, subprocess
env = json.load(open(".gov-runtime/scratch/lead/links-all-r3.json"))
fs = env["result"].get("findings") or (env["result"].get("new", []) + env["result"].get("standing", []))
tk = {}
for p in glob.glob(".tickets/*.md"):
    fm = yaml.safe_load(open(p).read().split("---", 2)[1])
    tk[p] = fm
wbs = {str(fm.get("wbs_id")): fm.get("id") for fm in tk.values() if fm.get("wbs_id")}
# files 66303c373 touched
touched = set(subprocess.run(["git", "show", "--name-only", "--format=", "66303c373"], capture_output=True, text=True).stdout.split())
cls = collections.Counter(); rows = collections.defaultdict(list)
for f in fs:
    if f["code"] != "UNLINKED_ID": continue
    fm = tk.get(f["path"]) or {}
    if fm.get("status") not in ("open", "in_progress"): continue
    i = f["ids"][0]
    lr = [str(x.get("id") if isinstance(x, dict) else x) for x in (fm.get("list_rows") or [])]
    src = [str(s) for s in (fm.get("sources") or [])]
    if i.startswith("DEC-"):
        k = "DEC id"
        if i == "DEC-798": k = "DEC-798 (re-pointed to DEC-1033 by DEC-1123 (2))"
    elif i in wbs:
        k = "WBS id" + (" (its ticket id in sources)" if wbs[i] in src else " (its ticket id NOT in sources)")
    elif re.match(r"W2-[HML]\d+", i):
        k = "backlog row" + (" (in list_rows)" if any(i in x for x in lr) else " (not in list_rows)")
    else:
        k = "other"
    k += " | ticket touched by 66303c373" if f["path"] in touched else " | ticket not touched by 66303c373"
    cls[k] += 1; rows[k].append(f"{fm.get('id')}:{i}")
for k, v in sorted(cls.items()):
    print(v, k); print("    ", " ".join(rows[k][:40]))
