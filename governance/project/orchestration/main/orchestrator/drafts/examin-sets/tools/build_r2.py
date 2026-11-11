#!/usr/bin/env python3
"""Builds the round-2 bundles of ACT-EXAMIN-SETS-1 and ACT-ACCEPTED-REDS-1 on the map f4029cfb4942 (DEC-1136 (1)).

  python3 -I build_r2.py copies          both bundles: before/after copies, list.txt, apply.sh (from apply_r2.sh.tpl)
  python3 -I build_r2.py draft           tmp/manifest.<act>.draft.json (the rehearsal reads each checks[] from it)
  python3 -I build_r2.py final           manifest.json of each: copies ../rehearsal.r2.log into the bundle and hashes it;
                                         refuses unless the log ends "failures: 0" and checks[] equal the draft's

examin   ACT-EXAMIN-SETS-1     drafts/examin-sets/acts-r2/ACT-EXAMIN-SETS-1/            f4029cfb4942 -> 0ec1d20da86a
reds     ACT-ACCEPTED-REDS-1   drafts/accepted-reds-1/acts-r2/ACT-ACCEPTED-REDS-1/      0ec1d20da86a -> 5654eca4c139
The entries are the r1 builders' own (tools/insert_entries.py, accepted-reds-1/tools/insert_reds.py), so they are byte
for byte the r1 entries; each check's command is the r1 manifest's, unchanged.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DX = os.path.dirname(HERE)                                   # drafts/examin-sets
DR = os.path.join(os.path.dirname(DX), "accepted-reds-1")    # drafts/accepted-reds-1
REL = "governance/project/path-map.yaml"
R1X = os.path.join(DX, "ACT-EXAMIN-SETS-1.r1", "manifest.json")
R1R = os.path.join(DR, "acts", "ACT-ACCEPTED-REDS-1.r1", "manifest.json")
MAPS = os.path.join(DX, "acts-r2", "maps")

V = {
    "examin": {
        "act": "ACT-EXAMIN-SETS-1",
        "bundle": os.path.join(DX, "acts-r2", "ACT-EXAMIN-SETS-1"),
        "before": os.path.join(MAPS, "map.live-f4029cfb.yaml"),
        "after": os.path.join(MAPS, "map.examin-after.yaml"),
        "r1": R1X,
        "change": "two entries added at the end of the `evaluation_sets:` block, `examin` and `adoption-proving-ground` "
                  "(visible and hidden globs, measures by the five roles memory-verdict-2 names)",
        "chain": "The \"before\" is the live map today (sha256 f4029cfb4942..., after ACT-W1-01-EXEMPT-3): this ACT runs BEFORE ACT-ACCEPTED-REDS-1.",
        "whyother": "another path-map ACT applied out of order?",
        "commitnote": "Class (a): the operator agent applies it with this script (the entries only tighten); this script does not commit.\n"
                      "# The sets root's own path map is NOT touched here: it is the owner's by hand (class-rules row walled-sessions); see\n"
                      "# FOR-THE-OWNER.md step 2.",
        "rebuild": ".gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py",
    },
    "reds": {
        "act": "ACT-ACCEPTED-REDS-1",
        "bundle": os.path.join(DR, "acts-r2", "ACT-ACCEPTED-REDS-1"),
        "before": os.path.join(MAPS, "map.examin-after.yaml"),
        "after": os.path.join(DR, "acts-r2", "map.reds-after.yaml"),
        "r1": R1R,
        "change": "the line `accepted_reds: []` becomes two entries (the warm real-model latency cases of W1-19 and W2-13, "
                  "decision DEC-1134, fixed_by W2-155)",
        "chain": "The \"before\" is the map as ACT-EXAMIN-SETS-1 leaves it (sha256 0ec1d20da86a...): this ACT runs AFTER that one. On any other map it refuses and touches nothing.",
        "whyother": "ACT-EXAMIN-SETS-1 not applied yet?",
        "commitnote": "The ratchet reads these entries only from a commit with `Role: owner`; this script does not commit. The owner's operator\n"
                      "# commits by hand (ACT-ACCEPTED-REDS-1.md section 5).",
        "rebuild": ".gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/tools/insert_reds.py",
    },
}


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def r1(v):
    return json.load(open(V[v]["r1"]))


def main():
    mode = sys.argv[1]
    for v, cfg in V.items():
        B = cfg["bundle"]
        draft = os.path.join(DX, "tmp", f"manifest.{v}.draft.json")
        if mode == "copies":
            for sub, src in (("before", cfg["before"]), ("after", cfg["after"])):
                dst = os.path.join(B, sub, "repo", REL)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                os.chmod(dst, 0o644)
            with open(os.path.join(B, "list.txt"), "w") as f:
                f.write(f"repo|{REL}|{sha(cfg['before'])}|{sha(cfg['after'])}\n")
            tpl = open(os.path.join(HERE, "apply_r2.sh.tpl")).read()
            for k, val in (("@ACT@", cfg["act"]), ("@CHANGE@", cfg["change"]), ("@CHAIN@", cfg["chain"]),
                           ("@WHYOTHER@", cfg["whyother"]), ("@COMMITNOTE@", cfg["commitnote"]),
                           ("@REBUILD@", cfg["rebuild"])):
                tpl = tpl.replace(k, val)
            assert "@" not in "".join(l for l in tpl.splitlines() if l.startswith("#")).replace("@@", ""), "a slot is unfilled"
            p = os.path.join(B, "apply.sh")
            with open(p, "w") as f:
                f.write(tpl)
            os.chmod(p, 0o755)
            print("copies written for", cfg["act"])
            continue
        root, path, before, after = open(os.path.join(B, "list.txt")).read().strip().split("|")
        rel = f"{root}/{path}"
        assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
        old = r1(v)
        files = {f"before/{rel}": before, f"after/{rel}": after}
        final = mode == "final"
        if final:
            log = os.path.join(DX, "rehearsal.r2.log")
            tail = open(log).read().rstrip().splitlines()[-1]
            assert tail == "failures: 0", f"the rehearsal log ends {tail!r}"
            assert json.load(open(draft))["checks"] == old["checks"], "the checks changed since the rehearsal read them"
            shutil.copyfile(log, os.path.join(B, "rehearsal.log"))
        for name in ["apply.sh", "list.txt"] + (["rehearsal.log"] if final else []):
            files[name] = sha(os.path.join(B, name))
        m = {"act": old["act"], "dec": old["dec"], "author": old["author"], "claimed_class": old["claimed_class"],
             "touched": [{"root": root, "path": path, "before": before, "after": after}],
             "files": files, "checks": old["checks"], "commands": []}
        if final:
            m["rehearsal"] = {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}
        out = os.path.join(B, "manifest.json") if final else draft
        with open(out, "w") as f:
            json.dump(m, f, indent=1)
            f.write("\n")
        print(out, "written;", len(files), "files hashed; sha256", sha(out))


main()
