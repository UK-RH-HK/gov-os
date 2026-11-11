"""survey JSON -> a markdown table: ticket, gate, commit or entry, why. Usage: python3 -I table.py <survey.json>"""
import json, re, sys
print("| ticket | gate | commit or entry | why |\n|---|---|---|---|")
for t, rows in json.load(open(sys.argv[1])).items():
    for r in rows:
        if r["gate"] == "_info" or r["gate"].startswith("probe"):
            continue
        w = r["what"]
        m = re.match(r"commit ([0-9a-f]{12}) names no task and changes (.*?): work on", w)
        if m:
            paths = m.group(2).split(", ")
            short = ", ".join(paths[:3]) + (f" (+{len(paths) - 3} more)" if len(paths) > 3 else "")
            print(f"| {t} | WORK_WITHOUT_TASK | `{m.group(1)}` | no Task: trailer; changes {short} |")
        elif r["gate"].startswith("ratchet:load_sensitive"):
            print(f"| {t} | LOAD_SENSITIVE_REFUSED | W1-19 `..::test_a_warm_query_answers_within_half_a_second_at_p95` (DEC-757) | DEC-757 is DONE, not ACCEPTED |")
        else:
            print(f"| {t} | {r['gate']} | {w[:80]} | {w[80:200]} |")
