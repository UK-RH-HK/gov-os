"""Assemble the lead brief of run 3 on W1-42: head3 + the twelve fields + the common part + the steps."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
parts = ["W1-42-A5-head3.md", "TWELVE-FIELDS.md", "LEAD-common.md", "LEAD-steps.md"]
text = "\n".join(open(B + name, encoding="utf-8").read() for name in parts)
text += "\n**Last of all: your one return message carries the twelve fields of \"The twelve-field return\" above, each as a labelled line.**\n"
with open(B + "W1-42-A5-run3.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
