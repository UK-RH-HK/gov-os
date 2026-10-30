"""Print the first N evidence items (rank, path, lines) of a gov retrieve JSON bundle read from a file."""
import json
import sys

doc = json.load(open(sys.argv[1], encoding="utf-8"))
bundle = doc.get("result", doc)
for rank, item in enumerate(bundle["evidence"][: int(sys.argv[2])], 1):
    print(rank, item["path"], item["start_line"], item["end_line"], item.get("batch"))
print("continuation", bool(bundle.get("continuation")), "stopping", bundle.get("stopping_reason"))
