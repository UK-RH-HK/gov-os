"""Assemble the brief of run J2: its top part, then the full brief of the round."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
text = open(B + "W1-30-A5-J2-top.md", encoding="utf-8").read() + open(B + "W1-30-A5-runJ.md", encoding="utf-8").read()
with open(B + "W1-30-A5-runJ2.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
