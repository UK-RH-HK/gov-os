from gov.adopt.safety import citations
s = ['legacy/memory/index.md', 'legacy/memory/decisions/leg-001.md']
n = ['notes/memory/2025/q1/a.md', 'notes/memory/2026/b.md']
for t, st in [('Did you search legacy/memory?', s), ('Is it still in legacy/memory/?', s), ('Should we keep notes/memory?', n),
              ('Did you search legacy/memory!', s), ('Did you search legacy/memory.', s), ('See ../memory/index.md?', s)]:
    print('R2-1', repr(t), [(f['form'], f['found']) for f in citations(t, st, [])])
print('R2-2', [(f['cites'], f['found']) for f in citations('Write documentation in docs/.', ['docs/memory/a.md', 'docs/notes/b.md'], [])])
