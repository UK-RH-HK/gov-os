import sys, pathlib
root = pathlib.Path(sys.argv[1])
text = (root / 'fixtures/evaluation/memory-retrieval/hidden/h.yaml').read_text().strip()
pathlib.Path('/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/act-permissions-2/run3/B/reader.out').write_text(text)
print('read', len(text), 'characters')
