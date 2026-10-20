"""DEC-614: one capability record per CAP id of docs/contract/contract.yaml (62 capabilities, 211 covers items).

Each record is a small file under docs/contract/capabilities/, generated from the contract file and nothing else:
the contract file stays the authority, the record gives the id something to resolve to (state class DERIVED).
Run again, it writes the same bytes.
"""
import os
import yaml

ROOT = "/home/usain/Dynamic-Agentic-Engineering-OS/"
OUT = ROOT + "docs/contract/capabilities/"
contract = yaml.safe_load(open(ROOT + "docs/contract/contract.yaml", encoding="utf-8"))
STATUS = contract["status"]


def front(fields):
    return "---\n" + yaml.safe_dump(fields, sort_keys=False, allow_unicode=True, width=1000) + "---\n"


os.makedirs(OUT, exist_ok=True)
written = 0
for cap in contract["capabilities"]:
    covers = cap.get("covers") or []
    body = (f"# {cap['id']}: {cap['title']}\n\n"
            f"Generated from `docs/contract/contract.yaml` (Contract v4, version {contract['version']}), which is the "
            f"authority; this record exists so that the id resolves (DEC-614).\n\n"
            f"- **Outcome:** {cap['outcome']}\n- **Acceptance:** {cap['acceptance']}\n- **Wave:** {cap['wave']}\n"
            f"- **Disposition:** {cap['disposition']['class']}\n")
    if covers:
        body += "- **Covers:** " + ", ".join(c["id"] for c in covers) + "\n"
    fields = {"id": cap["id"], "type": "capability", "status": STATUS, "state_class": "DERIVED",
              "title": cap["title"], "depends_on": ["CONTRACT-v4"]}
    with open(OUT + cap["id"] + ".md", "w", encoding="utf-8") as f:
        f.write(front(fields) + "\n" + body)
    written += 1
    for item in covers:
        body = (f"# {item['id']}: {item['item']}\n\n"
                f"A covers item of {cap['id']} ({cap['title']}). Generated from `docs/contract/contract.yaml` "
                f"(Contract v4, version {contract['version']}), which is the authority (DEC-614).\n\n"
                f"- **Item:** {item['item']}\n- **Wave:** {item.get('wave', cap['wave'])}\n")
        fields = {"id": item["id"], "type": "capability", "status": STATUS, "state_class": "DERIVED",
                  "title": item["item"], "depends_on": [cap["id"]]}
        with open(OUT + item["id"] + ".md", "w", encoding="utf-8") as f:
            f.write(front(fields) + "\n" + body)
        written += 1
print("written", written)
