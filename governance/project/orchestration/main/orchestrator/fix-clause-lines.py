"""DEC-624: ticket source lines 'DEC-074 <clause>' are cut to the id, once per ticket. Run again, it changes nothing."""
import re

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/"
for ticket in "DAEO-1ve2 DAEO-3ef2 DAEO-7nne DAEO-be7u DAEO-lkeb DAEO-t6hf DAEO-yvzh".split():
    path = ROOT + ticket + ".md"
    text = open(path, encoding="utf-8").read()
    head, sep, rest = text[4:].partition("\n---\n")
    lines, seen, out = head.split("\n"), "- DEC-074" in head.split("\n"), []
    for line in lines:
        if re.fullmatch(r"- DEC-074 [A-Z][0-9]+", line):
            if seen:
                continue
            line, seen = "- DEC-074", True
        out.append(line)
    new = text[:4] + "\n".join(out) + sep + rest
    if new != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        print(ticket, "changed")
