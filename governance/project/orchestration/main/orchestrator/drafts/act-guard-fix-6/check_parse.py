import ast
for f in (".claude/hooks/bash_writes.py", ".claude/hooks/pretooluse.py"):
    ast.parse(open(f).read())
