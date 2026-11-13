import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1])]
by = collections.OrderedDict()
for r in rows:
    by.setdefault(r["test"], []).append(r["p95_ms"])
for test, vals in by.items():
    cpu, wall = vals[0::2], vals[1::2]
    short = test.split("::",0)[0].split("/")[-1].replace("test_","").replace(".py","") + "::" + test.split("::")[-1][-60:]
    print(f"{test.split('/')[-2]:7} {test.split('::')[-1][-70:]:70} rounds={len(cpu)} cpu_p95_ms={cpu} wall_p95_ms={wall}")
