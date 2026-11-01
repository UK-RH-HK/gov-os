"""Where the heredoc scan of a corpus row ends in an open quote (prints the quote state at each line end)."""
import json, os, sys
c = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus.json")))
cmd = c[int(sys.argv[1])]["input"]["command"]
quote, i, line = "", 0, 0
while i < len(cmd):
    ch = cmd[i]
    if ch == "\n":
        print(line, "state", repr(quote))
        line += 1
    if quote == "'":
        quote = "" if ch == "'" else quote
    elif ch == "\\":
        i += 1
    elif quote == '"':
        quote = "" if ch == '"' else quote
    elif ch in "'\"":
        quote = ch
    i += 1
print("end state", repr(quote))
