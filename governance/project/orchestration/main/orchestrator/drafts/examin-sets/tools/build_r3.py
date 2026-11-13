#!/usr/bin/env python3
"""Builds the round-3 bundles of the path-map chain on the live map 30233a092a4b (after ACT-OPERATOR-HOURS-2's second commit,
6b8634d2c, which added one acceptance_exemptions entry). A rebuild with byte-identical entries, as round 2 was (DEC-1136 (1)).

  python3 -I build_r3.py copies          the three bundles: before/after copies, list.txt, apply.sh
  python3 -I build_r3.py draft           <TMP>/manifest.<v>.draft.json (the rehearsal reads each checks[] from it)
  python3 -I build_r3.py final           manifest.json of each: copies ../rehearsal.r3.log into the bundle and hashes it;
                                         refuses unless the log ends "failures: 0" and checks[] equal the draft's

The maps come from the builders of rounds 1 and 2, unchanged (tools/insert_entries.py, accepted-reds-1/tools/insert_reds.py,
pathmap-exp-1/insert_exp.py: the third is round 2's exact-text replacement written down; it reproduces round 2's after copy
byte for byte). apply.sh of the first two comes from tools/apply_r3.sh.tpl (round 2's template, "round 2" and "build_r2.py"
named "round 3" and "build_r3.py"); apply.sh of ACT-PATHMAP-EXP-1 is its round-2 file with the before hash named in a comment
and its rebuild hint (now naming insert_exp.py) changed: no line of logic differs. Each check's command, `dec`, `author` and
`claimed_class` are read from the round-2 manifests (acts/<ACT>.r2-<sha8>/manifest.json), unchanged.

examin   ACT-EXAMIN-SETS-1     drafts/examin-sets/acts-r3/ACT-EXAMIN-SETS-1/         live 30233a092a4b -> EXAMIN after
reds     ACT-ACCEPTED-REDS-1   drafts/accepted-reds-1/acts-r3/ACT-ACCEPTED-REDS-1/   EXAMIN after -> REDS after
exp      ACT-PATHMAP-EXP-1     drafts/pathmap-exp-1/acts-r3/ACT-PATHMAP-EXP-1/       REDS after -> EXP after
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DX = os.path.dirname(HERE)                                   # drafts/examin-sets
DRAFTS = os.path.dirname(DX)
DR = os.path.join(DRAFTS, "accepted-reds-1")
DE = os.path.join(DRAFTS, "pathmap-exp-1")
ACTS = os.path.join(os.path.dirname(DRAFTS), "acts")
REL = "governance/project/path-map.yaml"
MAPS = os.path.join(DX, "acts-r3", "maps")
TMP = "/home/usain/gov-os-runs/W2-00/pathmap-chain-r3/tmp"
LOG = os.path.join(DX, "rehearsal.r3.log")

M_LIVE = os.path.join(MAPS, "map.live-30233a09.yaml")
M_EX = os.path.join(MAPS, "map.examin-after.yaml")
M_RD = os.path.join(DR, "acts-r3", "map.reds-after.yaml")
M_EP = os.path.join(DE, "acts-r3", "map.exp-after.yaml")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


H = {k: sha(p)[:12] for k, p in (("live", M_LIVE), ("ex", M_EX), ("rd", M_RD), ("ep", M_EP))}

V = {
    "examin": {
        "act": "ACT-EXAMIN-SETS-1",
        "bundle": os.path.join(DX, "acts-r3", "ACT-EXAMIN-SETS-1"),
        "before": M_LIVE, "after": M_EX,
        "r2": os.path.join(ACTS, "ACT-EXAMIN-SETS-1.r2-e8020292", "manifest.json"),
        "change": "two entries added at the end of the `evaluation_sets:` block, `examin` and `adoption-proving-ground` "
                  "(visible and hidden globs, measures by the five roles memory-verdict-2 names)",
        "chain": f"The \"before\" is the live map today (sha256 {H['live']}..., after ACT-OPERATOR-HOURS-2): this ACT runs BEFORE ACT-ACCEPTED-REDS-1.",
        "whyother": "another path-map ACT applied out of order?",
        "commitnote": "Class (a): the operator agent applies it with this script (the entries only tighten); this script does not commit.\n"
                      "# The sets root's own path map is NOT touched here: it is the owner's by hand (class-rules row walled-sessions); see\n"
                      "# FOR-THE-OWNER.md step 2.",
        "rebuild": ".gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py",
    },
    "reds": {
        "act": "ACT-ACCEPTED-REDS-1",
        "bundle": os.path.join(DR, "acts-r3", "ACT-ACCEPTED-REDS-1"),
        "before": M_EX, "after": M_RD,
        "r2": os.path.join(ACTS, "ACT-ACCEPTED-REDS-1.r2-b8df21d8", "manifest.json"),
        "change": "the line `accepted_reds: []` becomes two entries (the warm real-model latency cases of W1-19 and W2-13, "
                  "decision DEC-1134, fixed_by W2-155)",
        "chain": f"The \"before\" is the map as ACT-EXAMIN-SETS-1 leaves it (sha256 {H['ex']}...): this ACT runs AFTER that one. On any other map it refuses and touches nothing.",
        "whyother": "ACT-EXAMIN-SETS-1 not applied yet?",
        "commitnote": "The ratchet reads these entries only from a commit with `Role: owner`; this script does not commit. The owner's operator\n"
                      "# commits by hand (ACT-ACCEPTED-REDS-1.md section 5).",
        "rebuild": ".gov-runtime/scratch/orchestrator/drafts/accepted-reds-1/tools/insert_reds.py",
    },
    "exp": {
        "act": "ACT-PATHMAP-EXP-1",
        "bundle": os.path.join(DE, "acts-r3", "ACT-PATHMAP-EXP-1"),
        "before": M_RD, "after": M_EP,
        "r2": os.path.join(ACTS, "ACT-PATHMAP-EXP-1.r2-9a945c99", "manifest.json"),
    },
}


def r2(v):
    return json.load(open(V[v]["r2"]))


def exp_apply():
    """ACT-PATHMAP-EXP-1's round-2 apply.sh with the before hash and the rebuild hint changed (comments only)."""
    src = open(os.path.join(ACTS, "ACT-PATHMAP-EXP-1.r2-9a945c99", "apply.sh")).read()
    old_before = r2("exp")["touched"][0]["before"][:12]
    assert src.count(old_before) == 1, "the r2 before hash is not named once in apply.sh"
    src = src.replace(old_before, H["rd"])
    hint = ("# the one line to the namespace doc-records with a tool in the style of\n"
            "#   .gov-runtime/scratch/orchestrator/drafts/examin-sets/tools/insert_entries.py\n"
            "# (one exact-text replacement, refused unless it matches exactly once) and freeze a new bundle; this one is not edited.\n")
    new = ("# the one line to the namespace doc-records with\n"
           "#   .gov-runtime/scratch/orchestrator/drafts/pathmap-exp-1/insert_exp.py\n"
           "# (one exact-text replacement, refused unless it matches exactly once; the build_r3.py beside insert_entries.py freezes\n"
           "# the bundle) and freeze a new bundle; this one is not edited.\n")
    assert src.count(hint) == 1, "the r2 rebuild hint is not as expected"
    return src.replace(hint, new)


def main():
    mode = sys.argv[1]
    for v, cfg in V.items():
        B = cfg["bundle"]
        draft = os.path.join(TMP, f"manifest.{v}.draft.json")
        if mode == "copies":
            for sub, src in (("before", cfg["before"]), ("after", cfg["after"])):
                dst = os.path.join(B, sub, "repo", REL)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                os.chmod(dst, 0o644)
            with open(os.path.join(B, "list.txt"), "w") as f:
                f.write(f"repo|{REL}|{sha(cfg['before'])}|{sha(cfg['after'])}\n")
            if v == "exp":
                text = exp_apply()
            else:
                text = open(os.path.join(HERE, "apply_r3.sh.tpl")).read()
                for k, val in (("@ACT@", cfg["act"]), ("@CHANGE@", cfg["change"]), ("@CHAIN@", cfg["chain"]),
                               ("@WHYOTHER@", cfg["whyother"]), ("@COMMITNOTE@", cfg["commitnote"]),
                               ("@REBUILD@", cfg["rebuild"])):
                    text = text.replace(k, val)
                assert "@" not in "".join(l for l in text.splitlines() if l.startswith("#")).replace("@@", ""), "a slot is unfilled"
            p = os.path.join(B, "apply.sh")
            with open(p, "w") as f:
                f.write(text)
            os.chmod(p, 0o755)
            print("copies written for", cfg["act"])
            continue
        root, path, before, after = open(os.path.join(B, "list.txt")).read().strip().split("|")
        rel = f"{root}/{path}"
        assert sha(os.path.join(B, "before", rel)) == before and sha(os.path.join(B, "after", rel)) == after
        old = r2(v)
        files = {f"before/{rel}": before, f"after/{rel}": after}
        final = mode == "final"
        if final:
            tail = open(LOG).read().rstrip().splitlines()[-1]
            assert tail == "failures: 0", f"the rehearsal log ends {tail!r}"
            assert json.load(open(draft))["checks"] == old["checks"], "the checks changed since the rehearsal read them"
            shutil.copyfile(LOG, os.path.join(B, "rehearsal.log"))
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
