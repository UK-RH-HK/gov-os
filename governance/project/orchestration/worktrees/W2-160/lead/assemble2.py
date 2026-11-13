import sys
for n, role in (("eng-2", "engineer"), ("td-2", "independent-test-designer")):
    body = open(f"{n}.md").read()
    head, tail = body.split("\n## Return", 1)
    ctx = open(f"{n}.ctx.md").read()
    open(f"{n}.md", "w").write(head + f"\n## The ticket's context (from `gov context DAEO-fd0p --role {role} --budget 12000`)\n\n" + ctx + "\n\n## Return" + tail)
