"""Which of the 39 queued Bash calls the guard's install rule (rule 4) matches. Run with the pinned gov's interpreter:
    $(head -1 ~/.local/bin/gov | cut -c3-) -E install_check.py <approval-queue.jsonl>
Read only; the commands are only parsed, never run."""
import json
import sys

from gov.guard.install import has_install, has_sudo

for line in open(sys.argv[1]):
    r = json.loads(line)
    if r["at"] < "2026-11-10 17:00" or r["tool"] != "Bash":
        continue
    print(r["at"], "install" if has_install(r["what"]) else "no-install", "sudo" if has_sudo(r["what"]) else "",
          "|", r["what"][:90].replace("\n", " "))
