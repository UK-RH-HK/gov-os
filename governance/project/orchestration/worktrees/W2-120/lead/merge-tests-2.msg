W2-120 (DAEO-i89t): merge the gov check case's envelope fix (run 3, td-2) into the ticket branch

The I3 gov check case looked for its entry under `result`, which is {} on a refusal (the entries sit under
error.details.checks, exit 3), and expected status "red" where gov check spells "RED". Test-design batch c63335672f81.

Task: DAEO-i89t
Role: orchestrator
Implements: DEC-995, DEC-996, DEC-992, CAP-24.b, DEC-718, DEC-1083
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
