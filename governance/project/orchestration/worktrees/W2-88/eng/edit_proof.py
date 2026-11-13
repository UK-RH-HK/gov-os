p = "/home/usain/gov-os-runs/W2-88/proof_a.py"
s = open(p).read()
s = s.replace('''    (root / "governance/project/retrieval.yaml").write_text(
        (WORK / "governance/project/retrieval.yaml").read_text(encoding="utf-8"), encoding="utf-8")  # as Gov OS ships it
    commit(root, "path map and retrieval.yaml for the proof")''', '''    commit(root, "path map for the proof")  # no retrieval.yaml by hand: A9's copy step installs Gov OS's (B-1.3)''')
s = s.replace('''    result["digests"] = record["digests"]''', '''    result["installed"] = {"count": len(record["installed"]), "retrieval_yaml": any(
        item["path"] == "governance/project/retrieval.yaml" for item in record["installed"]), "kept": record["kept"]}
    result["digests"] = record["digests"]''')
open(p, "w").write(s)
