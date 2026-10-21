"""Redact what the secrets-indexing check found in the orchestrator's own scratch files (DEC-601 follow-on).

Runs gitleaks on each named file, replaces every found string by a marker, prints counts only.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS"
FILES = sys.argv[1:]
for rel in FILES:
    path = os.path.join(ROOT, rel)
    total = 0
    for _ in range(5):  # a replaced string can uncover no new one, but run until clean
        with tempfile.TemporaryDirectory() as tmp:
            report = os.path.join(tmp, "r.json")
            subprocess.run(["gitleaks", "detect", "--no-git", "--no-banner", "-c", os.path.join(ROOT, ".gitleaks.toml"),
                            "-s", path, "-r", report, "-f", "json"], capture_output=True)
            found = json.load(open(report)) if os.path.exists(report) else []
        if not found:
            break
        text = open(path, encoding="utf-8").read()
        for each in found:
            secret = each.get("Secret") or ""
            if secret and secret in text:
                total += text.count(secret)
                text = text.replace(secret, "[REDACTED-" + each.get("RuleID", "rule") + "]")
        open(path, "w", encoding="utf-8").write(text)
    print(rel, "replaced", total, "rules", sorted({e.get("RuleID") for e in found}) if found else "clean")
