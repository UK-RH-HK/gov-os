"""Both figures together from W2-61 measure records (W2-87 lead), side by side per question, with each run's
gov_file and its comparison with the control. Scores only: ids, counts, ranks; never a question's text or gold.
argv: name=record ..."""
import json
import sys

runs = [arg.split("=", 1) for arg in sys.argv[1:]]
data = {name: json.load(open(path)) for name, path in runs}
for name, record in data.items():
    total = record["total"]
    in_bundle = sum(1 for q in record["questions"] if q["in_bundle"])
    print(f"{name}: gov_file {record['retriever']['gov_file']} | commit {record['commit']} | hit@5 "
          f"{total['hit_at_5']['count']}/20 ({total['hit_at_5']['percent']} %, floor 85) | full evidence "
          f"{total['full_evidence']['count']}/20 ({total['full_evidence']['percent']} %, target 99) | in bundle "
          f"{in_bundle}/20")
print("Q | " + " | ".join(f"{name}: hit5 rank bundle full(found/needed) same-as-control" for name in data))
for index in range(20):
    cells = []
    for name, record in data.items():
        q = record["questions"][index]
        same = q.get("compare", [{}])[0].get("same") if q.get("compare") else "-"
        differs = q.get("compare", [{}])[0].get("differs") if q.get("compare") else ""
        cells.append(f"{'y' if q['hit_at_5'] else 'n'} {q.get('first_gold_rank') or 'none'} "
                     f"{'y' if q['in_bundle'] else 'n'} {'y' if q['full_evidence'] else 'n'}"
                     f"({q.get('pieces_found')}/{q.get('pieces_needed')}) {same} {differs or ''}")
    print(record["questions"][index]["id"], "|", " | ".join(cells))
