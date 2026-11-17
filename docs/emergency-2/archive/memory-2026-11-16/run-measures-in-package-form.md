---
name: run-measures-in-package-form
description: "run a packaged/rehearsed measure exactly in the package's command form; I added `env -u GOV_ROLE -u GOV_TICKET` to W2-15a's visible run and had to stop and restart it (11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:47:38.656Z
---

On 11-16 at 05:47 I started W2-15a's visible run as `env -u GOV_ROLE -u GOV_TICKET bash visible_run.sh …`. I had copied the prefix from the owner's walled command. P-W2-15A-CLOSE §4 gives the CTO's form as a plain `bash visible_run.sh <commit> …`, and that is the form that was rehearsed. I stopped the run by its process group 8 s in, before its rebuild, and restarted it in the package's form.

**Why:** a measure's validity rests on the rehearsed form. Removing the role identity changes the product's role-based behaviour (gov's checks, telemetry). Removing it from my own session's child processes also looks like a way round the identity.

**How to apply:** copy a measure's or handed command's line from its package section, word for word, for the right actor. Never carry another actor's prefix over. Related: [[rehearse-every-handed-command]].

**And the stop itself was wrong (found 07:37):** I stopped pgid 1332856 (the Bash tool's `bash -c` wrapper), but visible_run.sh ran in its own group 1332869, so the misformed run lived on to 07:22 beside the restarted one: two measures on one clone and one GPU, which the package forbids. Figures were identical; timings are not comparable. **How to apply:** before a stop, `ps -o pid,pgid,args` and stop the TARGET's own pgid (and check with ps that it is gone); a background Bash call's wrapper group is not the script's.
