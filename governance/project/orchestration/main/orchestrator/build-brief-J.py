"""Assemble the lead brief of the fix round: head (with the policy piece) + the common part + the steps."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/"
head = open(B + "briefs/W1-30-A5-J-head.md", encoding="utf-8").read()
assert head.count("@@POLICY@@") == 1
head = head.replace("@@POLICY@@", open(B + "policy-piece.md", encoding="utf-8").read().strip())
text = head + "\n" + open(B + "briefs/LEAD-common.md", encoding="utf-8").read() + "\n" + open(B + "briefs/LEAD-steps.md", encoding="utf-8").read()
with open(B + "briefs/W1-30-A5-runJ.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
