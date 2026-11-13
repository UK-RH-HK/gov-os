"""The owner's edit of rule 11 of governance/project/prompts/w2-orchestrator.md (DEC-1141 (3), DEC-1142 (10)).
Run from the repository root: python3 -I <this file> check | apply. 'check' exits 0 only when the old text is there once.
'apply' replaces lines 38-40's rule 11 (A) and deletes line 43's "through D-10 engineers on C2/C1 tickets stay on Opus, high; ",
writing by a temporary file and a rename; it refuses (exit 3) and writes nothing if either old text is not found exactly once."""
import os
import sys
import tempfile

P = "governance/project/prompts/w2-orchestrator.md"
OLD_A = ("11. **Context and models (DEC-1118):** (A) a helper or lead hands over through its record and a fresh one continues\n"
         "    once its context passes about 200k tokens; the CTO checkpoints and clears at the same limit; (B) the CTO\n")
NEW_A = ("11. **Context and models (DEC-1118, DEC-1141):** (A) there is no token cap for any session (the CTO, leads, workers\n"
         "    and helpers): each uses its model's full window and compacts; before compaction the hook writes the checkpoint\n"
         "    and handover, and the summary opens with the read-first line; the CTO starts a fresh session each morning after\n"
         "    the digest and its handover (DEC-1140 (4)); (B) the CTO\n")
OLD_B = "through D-10 engineers on C2/C1 tickets stay on Opus, high; "


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    text = open(P, encoding="utf-8").read()
    if text.count(OLD_A) != 1 or text.count(OLD_B) != 1:
        print(f"rule11: REFUSED: the old text is not there exactly once (A {text.count(OLD_A)}, B {text.count(OLD_B)})")
        sys.exit(3)
    if mode == "check":
        print("rule11: ready (both old texts found once)")
        return
    new = text.replace(OLD_A, NEW_A, 1).replace(OLD_B, "", 1)
    mode_bits = os.stat(P).st_mode
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(P), prefix=".rule11-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(new)
    os.chmod(tmp, mode_bits)
    os.replace(tmp, P)
    print("rule11: applied (rule 11 (A) replaced; line 43's D-10 Opus phrase deleted)")


main()
