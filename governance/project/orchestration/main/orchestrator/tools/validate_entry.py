"""Validate a prepared ratchet or accepted-history entry with the pinned judge's own readers, against the register text
as it will stand, before the entry reaches the owner's commit (owner, standing, DEC-895 item 1).

Run with the pin's interpreter, so the judge's own code reads it:
    <the current pin's interpreter, the first line of ~/.local/bin/gov> -E validate_entry.py <patch of the path map> [<register file>]

It applies nothing. It reads the entries the patch adds to `load_sensitive`, `accepted_reds` or `accepted_history`,
and judges each:
  - a ratchet entry by `gov.close.ratchet._refused_because`, against the register file (default: the working copy);
    the one refusal expected before the owner's commit, "no commit of the history ... adds it", is reported as
    "pending the owner's commit", and so is a commit-role refusal; any other refusal fails;
  - an accepted-history entry by `gov.close.history._refused_because` (the decision and the commit it names).
The placeholder scan runs on the patch too (DEC-893). Prints one verdict per entry; exits 1 if any fails.
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml
from gov.close import history, ratchet

ROOT = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
patch = Path(sys.argv[1])
register_file = (Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else ROOT / "docs/DECISION_REGISTER.md")
PENDING = ("no commit of the history", "without Role: owner")

added, section = [], None
for line in patch.read_text().splitlines():
    if line.startswith("@@"):
        continue
    body = line[1:] if line[:1] in "+ -" else line
    m = re.match(r"^(load_sensitive|accepted_reds|accepted_history):", body)
    if m:
        section = m.group(1)
    if line.startswith("+") and not line.startswith("+++"):
        added.append((section, body))
# Rebuild each added entry from its "- test:"/"- commit:" line and the indented lines after it.
entries, cur = [], None
for section, body in added:
    if re.match(r"^\s*- (test|commit):", body):
        cur = {"_key": section, "_text": body.replace("- ", "  ", 1) + "\n"}
        entries.append(cur)
    elif cur is not None:
        cur["_text"] += body + "\n"
register = history.register_entries(ROOT, str(register_file.relative_to(ROOT)))
failed = 0
for e in entries:
    data = yaml.safe_load(e["_text"])
    key = e["_key"] or ("accepted_history" if "commit" in data else "load_sensitive")
    if key == "accepted_history":
        commit = history.commit_of(ROOT, str(data.get("commit")))
        why = history._refused_because(commit, data.get("decision"), register)
    else:
        why = ratchet._refused_because(ROOT, key, data, register, [], lambda sha, entry: False, "HEAD")
    label = data.get("test") or data.get("commit")
    if why is None or any(p in why for p in PENDING):
        print(f"PASS ({key}): {label}" + (" (pending the owner's commit)" if why else ""))
    else:
        failed += 1
        print(f"FAIL ({key}): {label}: {why}")
# Only the lines the patch adds are scanned: a line it removes leaves the tree, so its text adds no placeholder
# (2026-10-28: an old entry's "00:2x" on a removed line failed ACT-W2-57-LS-1).
import tempfile
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as added_text:
    added_text.write("\n".join(line[1:] for line in patch.read_text().splitlines()
                               if line.startswith("+") and not line.startswith("+++")) + "\n")
scan = subprocess.run([sys.executable, "-E", str(Path(__file__).with_name("placeholder_scan.py")), added_text.name],
                      capture_output=True, text=True)
Path(added_text.name).unlink()
print(scan.stdout.strip().splitlines()[-1] if scan.stdout.strip() else "placeholder scan: no output")
failed += scan.returncode != 0
print(f"entries judged: {len(entries)}; failed: {failed}")
sys.exit(1 if failed or not entries else 0)
