"""Scan the files changed since rebuild-4 with gitleaks (redacted); print only rule id, file and line, never a value."""
import json
import os
import subprocess
import sys

TREE = "/home/usain/gov-os-worktrees/W2-96"
REF = TREE + "/.gov-runtime/scratch/lead/log/rebuild-4.exit"
REPORT = "/tmp/gov-os-lead-W2-96/leak-report.json"
SKIP = (".git/", ".gov-runtime/store", ".gov-runtime/rebuild/", ".gov-runtime/codeintel", ".gov-runtime/lexical",
        ".gov-runtime/semantic", ".gov-runtime/query-vector-cache", "__pycache__/")
ref_time = os.path.getmtime(REF)
files = []
for root, dirs, names in os.walk(TREE):
    rel_root = os.path.relpath(root, TREE)
    if rel_root.startswith(".git") and (rel_root == ".git" or rel_root.startswith(".git/")):
        dirs[:] = []
        continue
    for name in names:
        path = os.path.join(root, name)
        rel = os.path.relpath(path, TREE)
        if any(s in rel + ("/" if os.path.isdir(path) else "") for s in SKIP):
            continue
        try:
            if os.path.isfile(path) and not os.path.islink(path) and os.path.getmtime(path) > ref_time:
                files.append(path)
        except OSError:
            pass
print("files scanned:", len(files))
config = [c for c in (TREE + "/.gitleaks.toml",) if os.path.exists(c)]
hits = 0
for path in files:
    argv = ["gitleaks", "dir", path, "--redact", "--no-banner", "--exit-code", "0", "--report-format", "json",
            "--report-path", REPORT, "--log-level", "error"]
    if config:
        argv += ["--config", config[0]]
    subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        found = json.load(open(REPORT, encoding="utf-8"))
    except (OSError, ValueError):
        found = []
    for f in found or []:
        hits += 1
        print(f.get("RuleID"), os.path.relpath(path, TREE), "line", f.get("StartLine"))
print("hits:", hits, "config:", config)
if os.path.exists(REPORT):
    os.remove(REPORT)
