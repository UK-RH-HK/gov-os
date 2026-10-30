from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead")
PAD = Path("/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-60a/8cb9a1a6-e619-4676-9fae-2da8ec131c99/scratchpad")
b2 = (LEAD / "briefs/b2-test-designer.md").read_text(encoding="utf-8")
head = b2[:b2.index("## What you read")]
head = head.replace("You write the ticket's acceptance tests from its KPI lines and its sources, **before the implementation exists**, and you show them red.",
                    "You extend the ticket's acceptance tests with review 1's findings, as described behaviours, and you show them red.")
head = head.replace("scratch/test-designer-b2/", "scratch/test-designer-b5/")
out = LEAD / "briefs/b5-test-designer-round2.md"
out.write_text(head + (PAD / "b5-tail.md").read_text(encoding="utf-8"), encoding="utf-8")
print(out, len(out.read_text().splitlines()))
