"""Summaries for the return: the governance checks that are not green, and a JUnit file's counts and failures."""
import json
import sys
import xml.etree.ElementTree as ET

kind, path = sys.argv[1], sys.argv[2]
if kind == "check":
    data = json.load(open(path))
    print("ok:", data.get("ok"))
    result = data.get("result", data)
    checks = result.get("checks") if isinstance(result, dict) else result
    if isinstance(checks, dict):
        checks = [dict(value, id=key) if isinstance(value, dict) else {"id": key, "status": value}
                  for key, value in checks.items()]
    for check in checks or []:
        status = str(check.get("status") or check.get("verdict") or check.get("result"))
        if status.lower() not in ("green", "pass", "passed", "ok", "true"):
            print(" ", check.get("id") or check.get("name"), status,
                  str(check.get("reason") or check.get("message") or check.get("detail") or "")[:240])
    if not checks:
        print(json.dumps(result)[:1500])
else:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = {key: sum(int(s.get(key, 0)) for s in suites) for key in ("tests", "failures", "errors", "skipped")}
    print(totals, "time", round(sum(float(s.get("time", 0)) for s in suites), 1))
    for case in root.iter("testcase"):
        for child in case:
            if child.tag in ("failure", "error"):
                print(" ", child.tag.upper(), f"{case.get('classname')}::{case.get('name')}",
                      "|", (child.get("message") or "")[:200].replace("\n", " "))
