"""From the branch check's JUnit XML, write the failing output of the cases that pass on the ticket's base but fail
on the branch and are not old-rule expectations (an orchestrator asked with no coordination-ticket key): node id and
failure message, plus three full failure texts. Usage: classb.py <branch xml> <base xml> <out>"""
import sys
import xml.etree.ElementTree as ET

OLD_RULE = ("test_w1_47_uv_installs", "test_the_template_s_guard_asks_before_an_install",
            "test_w1_50_freeze_guard_reading", "test_the_orchestrator_is_asked_about_uv_run_w",
            "test_w1_03_calls_known_to_be_over")


def failing(path):
    out = {}
    for case in ET.parse(path).iter("testcase"):
        bad = case.find("failure")
        if bad is None:
            bad = case.find("error")
        if bad is None:
            continue
        parts = case.get("classname", "").split(".")
        node = "/".join(parts[:-1]) + "/" + parts[-1] + ".py::" + case.get("name")
        out[node] = bad
    return out


branch, base = failing(sys.argv[1]), failing(sys.argv[2])
rows, full = [], []
for node, bad in branch.items():
    if node in base or any(o in node for o in OLD_RULE):
        continue
    rows.append(f"- {node}\n    {(bad.get('message') or '').splitlines()[0][:300]}")
    if len(full) < 3:
        full.append(f"### {node}\n\n```\n{(bad.text or '')[-2500:]}\n```\n")
with open(sys.argv[3], "w") as f:
    f.write(f"{len(rows)} cases\n\n" + "\n".join(rows) + "\n\n## Three full failure texts\n\n" + "\n".join(full))
print(len(rows), "cases")
