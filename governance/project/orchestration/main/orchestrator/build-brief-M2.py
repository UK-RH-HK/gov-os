"""Assemble the lead brief of the finishing run on the W1-38 round (DEC-675): headM2 + the twelve fields."""
B = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/"
wait = (
    "\n**Read this first: a headless lead's turn ends its background work.** After you start a worker or a test run in "
    "the background, wait for it in the foreground before you say anything: `until [ -s (its log or exit-code file) ]; "
    "do sleep 20; done` with the longest timeout allowed, repeated until it is there. Never end a message with "
    "\"waiting\". **Your return is one message, your last, and complete in itself.**\n\n"
    "**If a worker's log or your own call shows an authentication or access error (401, 403, \"Failed to authenticate\"): "
    "start nothing more and return at once with the first line `AUTH_REQUIRED` and the state of the branch (DEC-420).**\n"
)
text = (
    open(B + "W1-38-A5-headM2.md", encoding="utf-8").read() + wait + "\n"
    + open(B + "TWELVE-FIELDS.md", encoding="utf-8").read()
    + "\n**Last of all: your one return message carries the twelve fields above, each as a labelled line.**\n"
)
with open(B + "W1-38-A5-runM2.md", "w", encoding="utf-8") as f:
    f.write(text)
print(len(text))
