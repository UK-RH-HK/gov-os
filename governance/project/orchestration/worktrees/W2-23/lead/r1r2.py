from gov.adopt.safety import citations
s1 = ['legacy/memory/decisions/leg-001.md']
for t in ['The old store is legacy/memory.', 'The old store is legacy/memory, now gone', 'See legacy/memory/.', 'See ../decisions/leg-001.md.', 'See ../decisions/leg-001.md, too']:
    print('R1', repr(t), citations(t, s1, []))
s2 = ['.claude/memory/2025/a.md', '.claude/memory/2026/b.md']
for t in ['The store moved from .claude/memory/ to here', 'The store moved from .claude/memory/2025/ to here']:
    print('R2', repr(t), citations(t, s2, []))
