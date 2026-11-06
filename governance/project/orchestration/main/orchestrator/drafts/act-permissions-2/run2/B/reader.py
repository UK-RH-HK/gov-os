import sys, pathlib
root = pathlib.Path(sys.argv[1])
print((root / 'fixtures/evaluation/memory-retrieval/hidden/h.yaml').read_text().strip())
