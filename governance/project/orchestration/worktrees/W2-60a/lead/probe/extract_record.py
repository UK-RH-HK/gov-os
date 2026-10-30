"""Write the probe record block of a reviewer's return to a draft file. Usage: extract_record.py <log> <out>"""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
decoder, found, position = json.JSONDecoder(), None, 0
while True:
    start = text.find("{", position)
    if start < 0:
        break
    try:
        value, end = decoder.raw_decode(text, start)
    except ValueError:
        position = start + 1
        continue
    if isinstance(value, dict) and "result" in value:
        found = value
    position = end
result = found["result"]
fence = "`" * 3
begin = result.index(fence + "\n---\ntype: probe") + len(fence) + 1
finish = result.index("\n" + fence, begin)
with open(sys.argv[2], "w", encoding="utf-8") as out:
    out.write(result[begin:finish] + "\n")
print("wrote", sys.argv[2], finish - begin, "chars")
