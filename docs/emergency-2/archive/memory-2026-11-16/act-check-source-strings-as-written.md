---
name: act-check-source-strings-as-written
description: an ACT check that greps a source file for a message must match it as written (Python splits long strings across lines); run every check on the after copy before freezing
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T07:14:22.432Z
---

2026-11-16 (ACT-GUARD-FIX-7 build): my shape check looked for "its front matter is not YAML (fail closed, P-W2-111-YAML-REST-FRONT (a))" in role_reads.py, but the source writes it as two adjacent string literals split over lines. The check failed on the after copy, so the rehearsal's apply rolled back (correctly) and I had to rebuild the bundle and re-rehearse.

**Why:** an ACT's manifest checks run at apply time; one that is wrong on the after copy makes every apply roll back, and each rebuild changes the manifest sha the owner's yes line names.

Same build: my rehearsal's suite step counted only `^FAILED` lines and passed while 65 cases ERRORed at setup (W2-111's unit fixtures `git apply` the live-hook diff, which no longer applies once the ACT is in). With `-rf` pytest's summary lists no errors; count `ERROR at setup of` (or use `-rfE`) too.

Round 2 of the same build: a rehearsal string `OPENV="env -i PATH=$PATH ..."` expanded unquoted, and this machine's PATH holds `/mnt/c/Program Files/...`, so every case run through it died at `env`. Use a function (`openv() { env -i PATH="$PATH" ... "$@"; }`), never a command held in a string.

**How to apply:** before freezing a bundle, run each check source directly against the after copy in a scratch tree (e.g. `cd <after dir> && python3 -B -I check_x.py`), and grep for fragments that sit on one source line. Related: [[rehearse-every-handed-command]], [[no-rehearsal-against-live]].
