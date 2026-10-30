from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead")
PAD = Path("/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-60a/8cb9a1a6-e619-4676-9fae-2da8ec131c99/scratchpad")
b3 = (LEAD / "briefs/b3-engineer.md").read_text(encoding="utf-8")
opening = ("You are a fresh engineer. Ticket: DAEO-cv58 (W2-60a, \"The role, its skills and its model and effort loaded at "
           "launch; the launch record\"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-60a` "
           "on branch `w2/W2-60a`. **This is the ticket's round 2:** you make the acceptance cases that fail at the head "
           "pass, from the failing output at the end of this brief, and update the design note.\n\n")
standing = b3[b3.index("## Step 0"):b3.index("## What you read")]
commit_and_return = b3[b3.index("## Commit"):]
failing = (PAD / "failing2.txt").read_text(encoding="utf-8")
text = (opening + standing + (PAD / "b6-middle.md").read_text(encoding="utf-8") + commit_and_return.rstrip()
        + "\n\n## The failing output (the lead's red run at head 8379a8c66f79, one file at a time; all you are given)\n\n"
        + failing)
out = LEAD / "briefs/b6-engineer-round2.md"
out.write_text(text, encoding="utf-8")
print(out, len(text.splitlines()))
