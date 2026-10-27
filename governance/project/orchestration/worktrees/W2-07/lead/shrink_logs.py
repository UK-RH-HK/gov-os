"""Row W2-L423's rule: replace run 4's full collection listings and the parallel JUnit XML with summaries (counts, the
failures with their first message line), every 40-hex id cut to 12 digits. Usage: shrink_logs.py <log folder>."""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

log = Path(sys.argv[1])
HEX = re.compile(r"\b([0-9a-f]{12})[0-9a-f]{28}\b")


def cut(text):
    return HEX.sub(r"\1", text)


for name in ("final-collect.txt", "v4-collect.txt"):
    path = log / name
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if line.startswith("ERROR")] + lines[-1:]
    path.write_text(cut("\n".join(["(summary of the full listing, row W2-L423's rule)"] + kept)) + "\n",
                    encoding="utf-8")

xml = log / "parallel4.xml"
root = ET.parse(xml).getroot()
out = ["(summary of the JUnit XML of p4.sh, row W2-L423's rule)"]
for suite in root.iter("testsuite"):
    out.append("testsuite " + " ".join(f"{k}={suite.get(k)}" for k in ("tests", "failures", "errors", "skipped", "time")))
for tc in root.iter("testcase"):
    f = tc.find("failure") if tc.find("failure") is not None else tc.find("error")
    if f is not None:
        out.append(f"FAILED {tc.get('classname')}::{tc.get('name')} | {(f.get('message') or '').splitlines()[0][:200]}")
(log / "parallel4.summary.txt").write_text(cut("\n".join(out)) + "\n", encoding="utf-8")
xml.write_text("<!-- replaced by parallel4.summary.txt under row W2-L423's rule -->\n", encoding="utf-8")
