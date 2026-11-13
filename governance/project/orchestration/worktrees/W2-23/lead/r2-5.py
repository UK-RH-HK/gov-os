from gov.adopt.safety import citations
s = ['legacy/memory/index.md', 'legacy/memory/decisions/leg-001.md']
n = ['notes/memory/2025/q1/a.md', 'notes/memory/2026/b.md']
cases = [
    ('Did you search legacy/memory?', s, True), ('Is it still in legacy/memory/?', s, True),
    ('Should we keep notes/memory?', n, True), ('Is it in notes/memory/?', n, True),
    ('Really legacy/memory?!', s, True), ('(legacy/memory?)', s, True), ('legacy/memory??', s, True),
    ('"legacy/memory?"', s, True), ('legacy/memory?.', s, True),
    ('Did you search legacy/memory!', s, True), ('Did you search legacy/memory.', s, True),
    ('Is it legacy/memory/*.md?', s, True), ('legacy/memory/decisions/leg-00?.md', s, True),
    ('legacy/memory/decisions/leg-00?', s, True), ('See ../memory/index.md?', s, True),
    ('legacy/memory?x', s, False), ('legacy/memory/?.md', s, False), ('legacy/memory.db?', s, False),
    ('legacy/memory2?', s, False), ('Is it in notes/?', n, False), ('Is it legacy/memoryx/*.md?', s, False),
]
bad = 0
for t, st, want in cases:
    got = [(f['form'], f['found']) for f in citations(t, st, [])]
    ok = bool(got) == want
    bad += not ok
    print('ok ' if ok else 'BAD', repr(t), got)
print('bad', bad)
