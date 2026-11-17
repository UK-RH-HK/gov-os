---
name: walls-approved-line-kind
description: "an indep-walls APPROVED line is \"<sha256>  brief <kind> <path>\"; my q02 line left out the kind \"writer\" and the operator had to fix it (11-14)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-14T22:58:52.273Z
---

On 2026-11-14 the q02 commands I gave the owner's operator had an APPROVED line `<sha>  brief <path>` with no kind. The launcher needs `<sha>  brief writer <path>`. The operator corrected it, set the mode back to 400 and relaunched (run 20261114T222836Z-examin-r2 delivered, 20 of 20 hold). The cause was my command, and it is recorded in DEC-1184.

**Why:** a walls line in the wrong form stops the walled run. The owner's operator has to repair it by hand, and the run waits on that repair.

**How to apply:** before handing over any `indep-walls/APPROVED` line, copy the form from an existing line in that file's spec (`indep_launch.py` or kinds.yaml) and name the kind (writer, checker and so on). Rehearse the line against the launcher's parser in a scratch copy. Related: [[review-record-verdict-block]], [[check-before-ready-line]].
