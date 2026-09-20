#!/usr/bin/env python3
"""P2-AR-0045 — Repo A (greenfield) shape and the explicit-N/A rule.

Contract v3:1029 puts the V2 hidden path-map oracle on the brownfield repository. A greenfield oracle
therefore carries no path map, and its score report must record path-map accuracy as an explicit,
reasoned N/A -- never a silent omission and never an invented ratio.
"""
import copy, json, os, subprocess

GOV = "target/release/gov"
S = "release/capability-baseline/verify-1/oracle-format/samples"
TMP = f"{S}/probe"
os.makedirs(TMP, exist_ok=True)
G = f"{S}/valid/oracle-greenfield.json"
dig = json.loads(subprocess.run([GOV, "--json", "oracle", "validate", G], capture_output=True, text=True).stdout)["result"]["canonical_sha256"]

base = json.load(open(f"{S}/valid/score-report.json"))


def rep(**over):
    d = copy.deepcopy(base)
    d["report_id"] = "P2AR0045-SAMPLE-REPORT-G"
    d["binding"]["oracle_id"] = "P2AR0045-SAMPLE-ORACLE-G"
    d["binding"]["repository"]["id"] = "sample-repo-a"
    d["binding"]["oracle_sha256"] = dig
    d["metrics"].update(over)
    return d


def check(name, doc):
    p = os.path.join(TMP, name + ".json")
    json.dump(doc, open(p, "w"), indent=1)
    env = json.loads(subprocess.run([GOV, "--json", "oracle", "validate", p, "--oracle", G],
                                    capture_output=True, text=True).stdout)
    if env.get("ok"):
        return "ACCEPTED", ""
    e = env["error"]
    vs = (e.get("details") or {}).get("violations") or []
    return e["code"], (f'{vs[0].get("at","")} :: {vs[0].get("problem","")[:90]}' if vs else e["message"][:90])


for label, name, doc in [
    ("greenfield report, path-map accuracy explicit N/A",
     "gf-01-path-map-explicit-na", rep(path_map_accuracy={"applicable": False, "reason": "the oracle is greenfield: it carries no path-map oracle"})),
    ("greenfield report, path-map accuracy as a ratio",
     "gf-02-path-map-invented-ratio", rep(path_map_accuracy={"numerator": 3, "denominator": 3, "value": 1.0})),
    ("greenfield report, path-map accuracy omitted",
     "gf-03-path-map-omitted", (lambda d: (d["metrics"].pop("path_map_accuracy"), d)[1])(rep())),
    ("greenfield report, N/A with no reason",
     "gf-04-na-without-reason", rep(path_map_accuracy={"applicable": False})),
]:
    code, det = check(name, doc)
    print(f"{label:52s} {code:32s} {det}")
