"""Adoption step: records for the ids that tickets cite and no record holds (the master rules, the interface
API-0002), and the two source lines that carry a clause after the id. Generated from the contract file and the
interface file, which stay the authority. Run again, it writes the same bytes."""
import os
import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
contract = yaml.safe_load(open(ROOT + "docs/contract/contract.yaml", encoding="utf-8"))


def front(fields):
    return "---\n" + yaml.safe_dump(fields, sort_keys=False, allow_unicode=True, width=1000) + "---\n"


os.makedirs(ROOT + "docs/contract/master-rules", exist_ok=True)
for rule in contract["master_rules"]:
    fields = {"id": rule["id"], "type": "specification", "status": contract["status"], "state_class": "DERIVED",
              "title": rule["title"], "depends_on": ["CONTRACT-v4"]}
    body = (f"# {rule['id']}: {rule['title']}\n\n"
            f"A master rule of the Charter (v5, §4). Generated from `docs/contract/contract.yaml` (Contract v4, version "
            f"{contract['version']}), which is the authority; this record exists so that the id resolves.\n\n"
            f"- **Text:** {rule['text_source']}\n- **Acceptance:** {rule['acceptance']}\n")
    with open(ROOT + f"docs/contract/master-rules/{rule['id']}.md", "w", encoding="utf-8") as f:
        f.write(front(fields) + "\n" + body)
    print("written", rule["id"])

api = yaml.safe_load(open(ROOT + "docs/interfaces/API-0002.yaml", encoding="utf-8"))
fields = {"id": "API-0002", "type": "specification", "status": api["status"], "state_class": "DERIVED",
          "title": api["title"]}
body = (f"# API-0002: {api['title']}\n\nThe interface itself is `docs/interfaces/API-0002.yaml`, which is the authority; "
        "this record exists so that the id resolves.\n")
with open(ROOT + "docs/interfaces/API-0002.md", "w", encoding="utf-8") as f:
    f.write(front(fields) + "\n" + body)
print("written API-0002")

for ticket, old, new in (("DAEO-dtv3", "- DEC-074 Q9\n", "- DEC-074\n"),
                         ("DAEO-emkd", "- OWNER-DECISION-P2-0001 BC-P2-08\n", "- OWNER-DECISION-P2-0001\n")):
    path = ROOT + f".tickets/{ticket}.md"
    text = open(path, encoding="utf-8").read()
    if text.count(old) == 1:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text.replace(old, new))
        print(ticket, "source line:", old.strip(), "->", new.strip())
