"""gov accept W2-157 as the CLI runs it, but each private folder's report.xml is copied out before its removal, and
each failed case is printed with its message."""
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if "--tree" in sys.argv: sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-157/src")
keep = Path("/tmp/w2-157-lead/accept-keep")
keep.mkdir(parents=True, exist_ok=True)
real_rmtree = shutil.rmtree
count = [0]


def rmtree(path, *args, **kwargs):
    report = Path(path) / "report.xml"
    if report.exists():
        count[0] += 1
        shutil.copy(report, keep / f"report-{count[0]}.xml")
    return real_rmtree(path, *args, **kwargs)


shutil.rmtree = rmtree
from gov.cli.main import main  # noqa: E402
import gov.accept.runner as runner  # noqa: E402

real_remove = runner._remove


def keep_remove(path, *args, **kwargs):
    report = Path(path) / "report.xml"
    if report.exists():
        count[0] += 1
        shutil.copy(report, keep / f"report-{count[0]}.xml")
    return real_remove(path, *args, **kwargs)


runner._remove = keep_remove
print("runner", runner.__file__)

code = main(["accept", "W2-157", "--root", "/home/usain/gov-os-worktrees/W2-157"])
print("exit", code, "reports", count[0])
for file in sorted(keep.glob("report-*.xml")):
    for case in ET.parse(file).iter("testcase"):
        for child in case:
            if child.tag in ("failure", "error"):
                print("FAILED", file.name, case.get("classname"), case.get("name"))
                print((child.text or child.get("message") or "")[-3000:])
