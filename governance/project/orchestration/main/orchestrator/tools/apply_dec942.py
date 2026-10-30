"""Appends DEC-942 to the register, marks the status lines it changes (DEC-941, DEC-847, DEC-798), and brings the
prompt to v3.39: §3's parallelism and gate text, the closes-first rule, §7's daily-document lines."""
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
REG = ROOT / "docs/DECISION_REGISTER.md"
PROMPT = ROOT / "governance/project/prompts/w2-orchestrator.md"
DRAFT = ROOT / ".gov-runtime/scratch/orchestrator/drafts/DEC-942.md"

reg = REG.read_text(encoding="utf-8")
DONE = "### DEC-942 " in reg
for dec, note in () if DONE else (
    ("DEC-941", "item 1d's ceiling of 4 leads removed (DEC-942)"),
    ("DEC-847", "the hard ceiling of 10 leads removed and the gate measured on WSL as it is (DEC-942)"),
    ("DEC-798", "the fixed gate figures replaced by the measured gate (DEC-942)"),
):
    m = re.search(r"### " + dec + r" .*?\n- \*\*Status:\*\* [A-Z]+ \(", reg, re.S)
    if not m:
        sys.exit(dec + "'s status line not found")
    reg = reg[:m.end()] + note + "; " + reg[m.end():]
if not DONE:
    reg = reg.rstrip("\n") + "\n" + DRAFT.read_text(encoding="utf-8")
    REG.write_text(reg, encoding="utf-8")

p = PROMPT.read_text(encoding="utf-8")
EDITS = [
    ("v3.38: DEC-939 to DEC-941)", "v3.38: DEC-939 to DEC-941; v3.39: DEC-942)"),
    ("  - **a hard ceiling of 10 leads,** for the machine's sake.\n",
     "  - **no ceiling** (owner, DEC-942 item 1): the gate below decides, not a count.\n"),
    ("  **Up to 4 leads at once beside one verification run (standing until W2-20 carries it, DEC-941 item 1d),** always "
     "within the resource gate and the nightly window.",
     "  **No fixed number of leads (owner, standing, DEC-942, replacing DEC-941 item 1d):** launch every ready ticket "
     "that dependencies and paths allow (no overlapping running ticket, or the overlap split by file), critical path "
     "first (memory), then K3, K6 and the held merge-backs, until the gate says the machine is full "
     "(`tools/lead_chain.sh`, detached starts; `tools/gate_check.py`). If the load stays above the gate for more than "
     "15 minutes, launch nothing new until it falls; never stop a running lead for load. **Closes first (DEC-942 "
     "item 4):** while a ticket is ready to close (`CLOSE-PENDING`), launch no new lead until its close (or batch) has "
     "started; running leads continue; the queue takes the verification lock and waits for quiet at most 20 minutes, "
     "so it never starves. The locks and windows stay (item 5): one verification run at a time until its trial after "
     "W2-67, the close lock, no starts between 00:30 and 05:30."),
    ("read the gate by hand in the same command as each start: DEC-798's figures (the 1-minute load below 20 and "
     "MemAvailable at least 6710886 kB) until a lead has been measured, then the figure the measurement gives for one "
     "more lead with its suites;",
     "the gate is measured on WSL as it is at each start (owner, DEC-942 item 2; `tools/gate_check.py`, in the same "
     "command): `min(load1, load15)` below `nproc`, and MemAvailable at least a floor (6,710,886 kB until the "
     "measurements support a lower one; if the floor is what holds launches while the CPU is idle, propose a lower "
     "one with the measurements) plus each running lead's measured reservation not yet in use (`tools/lead_mem.py`, "
     "sampled each minute);"),
    ("- **The resource gate by hand (DEC-798, DEC-898), until W2-20 closes:** the 1-minute load below 20, MemAvailable "
     "at least 6710886 kB, and the shared disk",
     "- **The resource gate (DEC-942, DEC-898), until W2-20 closes:** `tools/gate_check.py` (the load below `nproc`, "
     "memory above the floor plus the running leads' measured reservations), and the shared disk"),
    ("  - **One daily document (owner, standing, DEC-941 item 4c):** the morning package carries the digest's items; "
     "there is no separate digest.",
     "  - **One daily document (owner, standing, DEC-941 item 4c):** the morning package carries the digest's items; "
     "there is no separate digest. **It reports (DEC-942 item 6):** how many leads ran at once (the peak and the "
     "average, from `log/lead-mem.jsonl`), the machine's utilisation (load against `nproc`, memory), the lead runs "
     "and their measured cost (`tools/lead_usage.py`), and whether the owner's plan's usage limits are close; ping "
     "the owner before they are."),
]
for old, new in EDITS:
    if p.count(old) != 1:
        sys.exit("prompt text not found once: " + old[:70])
    p = p.replace(old, new)
PROMPT.write_text(p, encoding="utf-8")
print("DEC-942 appended; DEC-941, DEC-847, DEC-798 marked; prompt v3.39")
