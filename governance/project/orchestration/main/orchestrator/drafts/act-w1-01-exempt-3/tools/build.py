#!/usr/bin/env python3
"""Builds a bundle of ACT-W1-01-EXEMPT-3 (the operator's form, as acts/ACT-EXAMIN-SETS-1 has it).

  python3 -I build.py first --copies     before/after copies, list.txt, apply.sh (from apply.sh.tpl)
  python3 -I build.py first --draft      tmp/manifest.<v>.draft.json (the rehearsal reads its checks[] from it)
  python3 -I build.py first --final      manifest.json: copies rehearsal.first.log into the bundle and hashes it; refuses
                                                 unless the log ends "failures: 0" and checks[] equal the draft's

first   ACT-W1-01-EXEMPT-3       on the live map (fb52ab2d...), before ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 (DEC-1136 (1))
"""
import hashlib
import json
import os
import shutil
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORCH = os.path.dirname(os.path.dirname(os.path.dirname(D)))
REL = "governance/project/path-map.yaml"
COMMITS = ["c9a08678644485a7528bc875164e110881b63d93", "0568d91baf566b4d8f3ccb448e51af41cbb46d03",
           "cade65dfe0454bb1b34c6a44bd475a9d67c5e45e", "04460404ea8a07bfb3f3f0019d3384e30c7f9466",
           "8c512d7e7921bfd7b5c3dd50a79bb1fc145f869a", "ab169d051b82072f0db4350b2066eabf6919ffa0",
           "15952bbfa576dcfabb7d36d95912a848077e5c3c", "6fbe73b1adde40571f00d490b4b478cf86b70a52"]
V = {
    "first": {
        "act": "ACT-W1-01-EXEMPT-3",
        "before": os.path.join(D, "tmp", "clone-live-map.yaml"),  # the live map as cloned (fb52ab2d...)
        "after": os.path.join(D, "maps", "map.first.yaml"),
        "chain": "The \"before\" is the live map today (sha256 fb52ab2dc756...): this ACT runs BEFORE ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1.",
        "whyother": "another path-map ACT applied first?",
        "extra": False,
    },
}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def probe(v):
    c = COMMITS
    s = ("import yaml,sys; d=yaml.safe_load(open(\"governance/project/path-map.yaml\")); e=d[\"acceptance_exemptions\"]; "
         f"c={json.dumps(c)}; "
         "ok=[x[\"commit\"] for x in e]==c and all(x[\"decision\"].startswith(\"DEC-\") for x in e) "
         "and e[-1][\"decision\"]==\"DEC-1136\"")
    if V[v]["extra"]:
        s += " and \"examin\" in d[\"evaluation_sets\"] and len(d[\"accepted_reds\"])==2"
    s += "; sys.exit(0 if ok else 1)"
    return "python3 -I -c '" + s + "'"


def checks(v):
    return [{"cmd": "PYTHONPATH=src python3 -m gov.check.pathmap", "exit": 0, "count": None},
            {"cmd": probe(v), "exit": 0, "count": None}]


def main():
    v, mode = sys.argv[1], sys.argv[2]
    cfg = V[v]
    B = os.path.join(D, "acts", cfg["act"])
    draft = os.path.join(D, "tmp", f"manifest.{v}.draft.json")
    if mode == "--copies":
        for sub, src in (("before", cfg["before"]), ("after", cfg["after"])):
            dst = os.path.join(B, sub, "repo", REL)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            os.chmod(dst, 0o644)
        with open(os.path.join(B, "list.txt"), "w") as f:
            f.write(f"repo|{REL}|{sha(cfg['before'])}|{sha(cfg['after'])}\n")
        tpl = open(os.path.join(D, "tools", "apply.sh.tpl")).read()
        for k, val in (("@ACT@", cfg["act"]), ("@CHAIN@", cfg["chain"]), ("@WHYOTHER@", cfg["whyother"])):
            tpl = tpl.replace(k, val)
        assert "@ACT@" not in tpl and "@CHAIN@" not in tpl and "@WHYOTHER@" not in tpl
        p = os.path.join(B, "apply.sh")
        with open(p, "w") as f:
            f.write(tpl)
        os.chmod(p, 0o755)
        print("copies written for", cfg["act"])
        return
    root, path, before, after = open(os.path.join(B, "list.txt")).read().strip().split("|")
    rel = f"{root}/{path}"
    assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
    files = {f"before/{rel}": before, f"after/{rel}": after}
    final = mode == "--final"
    if final:
        log = os.path.join(D, f"rehearsal.{v}.log")
        tail = open(log).read().rstrip().splitlines()[-1]
        assert tail == "failures: 0", f"the rehearsal log ends {tail!r}"
        assert json.load(open(draft))["checks"] == checks(v), "the checks changed since the rehearsal read them"
        shutil.copyfile(log, os.path.join(B, "rehearsal.log"))
    for name in ["apply.sh", "list.txt"] + (["rehearsal.log"] if final else []):
        files[name] = sha(os.path.join(B, name))
    m = {
        "act": cfg["act"],
        "dec": "DEC-1136, DEC-1131, DEC-906, DEC-253",
        "author": "cto",
        "claimed_class": "O",
        "touched": [{"root": root, "path": path, "before": before, "after": after}],
        "files": files,
        "checks": checks(v),
        "commands": [],
    }
    if final:
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}
    out = os.path.join(B, "manifest.json") if final else draft
    with open(out, "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print(out, "written;", len(files), "files hashed; sha256", sha(out))


main()
