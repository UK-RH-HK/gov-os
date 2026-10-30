"""ACT 1: the sweep's reds re-run serially, on the base and with ACT 1, so only the reds ACT 1 causes are named.
Ids that do not name a test file (collection errors) are listed apart. Writes /tmp/gov-os-act1/confirmed.json."""
import collections
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

clone = "/tmp/gov-os-act1/repo"
d = json.load(open("/tmp/gov-os-act1/result.json"))
ids = [x for x in d["caused_by_act1"] if os.path.isfile(os.path.join(clone, x.split("::")[0]))]
bad = [x for x in d["caused_by_act1"] if x not in ids]
env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
env.update(PYTHONPATH=clone + "/src", TMPDIR="/tmp/gov-os-act1/tmp",
           PATH="/home/usain/.nvm/versions/node/v22.23.3/bin:" + env.get("PATH", ""))


def red(xml):
    subprocess.run([sys.executable, "-m", "pytest", *ids, "-q", "-p", "no:cacheprovider", "--no-header",
                    "-o", "tmp_path_retention_policy=failed", f"--junitxml={xml}"], cwd=clone, env=env,
                   capture_output=True, text=True)
    out, ran = [], 0
    for case in ET.parse(xml).iter("testcase"):
        ran += 1
        if case.find("failure") is not None or case.find("error") is not None:
            f = case.get("file") or (case.get("classname", "").replace(".", "/") + ".py")
            out.append(f"{f}::{case.get('name')}")
    return ran, out


ran_a, red_a = red("/tmp/gov-os-act1/confirm-act1.xml")
subprocess.run(["git", "-C", clone, "checkout", "-q", "HEAD^", "--", ".claude", ".rulesync"], check=True)
try:
    ran_b, red_b = red("/tmp/gov-os-act1/confirm-base.xml")
finally:
    subprocess.run(["git", "-C", clone, "checkout", "-q", "HEAD", "--", ".claude", ".rulesync"], check=True)
caused = sorted(set(red_a) - set(red_b))


def folder(node):
    return "/".join(node.split("::")[0].split("/")[:3])


json.dump({"collection_errors": bad, "red_with_act1": red_a, "red_on_base": red_b, "caused": caused},
          open("/tmp/gov-os-act1/confirmed.json", "w"), indent=1)
print("ids", len(ids), "| collection-error ids", len(bad), bad)
print("with ACT 1: ran", ran_a, "red", len(red_a), "| base: ran", ran_b, "red", len(red_b))
print("caused by ACT 1:", len(caused), dict(collections.Counter(folder(x) for x in caused)))
print("files:", sorted({x.split("::")[0] for x in caused}))
