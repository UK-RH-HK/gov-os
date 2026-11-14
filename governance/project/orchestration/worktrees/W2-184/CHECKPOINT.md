---
task: DAEO-6f0s
decisions_applied: [DEC-1167, DEC-1120, DEC-1119, DEC-1052, DEC-1010, DEC-1146, DEC-802, DEC-136, DEC-1154, DEC-1177]
---
STATE: build run; F1 fix built (eng-5: 94b48c130, 42d0867d3), lead_verify running at 42d0867d3 (pid 3436431); td-6 (CLI options, P-W2-184-2 (a)) running in W2-184-tests (pid 3463848) | HEAD: 42d0867d3 | NEXT: wait_for lead/log/verify/verify.exit and W2-184-tests lead/log/td-6.exit; merge td-6; eng-6 (command.py) on the failing output; rebuild, lead_verify, gov accept; then the narrow check (needs --owner-named DEC-1177: launch_worker.sh cannot pass it -> package to the CTO) | WAITING ON: verify, td-6
Workers: td-1..td-5, eng-1..eng-5 done (td-5 83e513a0, eng-5 06690070); rv-1 0be7734a (fail), rv-2 d4de9d3f (fail); td-6 ec344c7f running
Rounds: two review rounds done (DEC-1010); no third; the narrow check (DEC-1154, DEC-1177 (1)) is the next auditor launch = review_round 3 by the launcher's count, refused without --owner-named
Decisions taken: INTERFACE 5.1a (+P-td5-1 (a), P-td5-2); 7.2a (CLI options, P-W2-184-2 (a)); (c) held (tests branch from e99c8059c)
Open packages: (to come) P-W2-184-4: the narrow check's launch needs --owner-named through launch_worker.sh
Paths: briefs .gov-runtime/scratch/briefs/ (td-5, eng-5, td-6); logs .gov-runtime/scratch/lead/log/ and W2-184-tests/.gov-runtime/scratch/lead/log/; red-5 in .gov-runtime/scratch/log/
