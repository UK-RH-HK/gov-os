p = "tests/unit/adopt/test_w2_88_run4.py"
s = open(p).read()
s = s.replace('monkeypatch.setenv("PATH", str(tmp_path / "nowhere"))', 'monkeypatch.setenv("PATH", "/usr/bin:/bin")  # git, and no gitleaks')
s = s.replace('''    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True).stdout
    assert status == ""''', '''    assert tree_status(root) == ""''')
s = s.replace('''    assert subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True).stdout == ""
    assert not (root / "governance/adoption").exists()''', '''    assert tree_status(root) == ""
    assert not (root / "governance/adoption").exists()''')
s = s.replace('''def head_of(root, result):''', '''def tree_status(root):
    """``git status --porcelain`` but for the store's own folder (the planted repositories have no .gitignore)."""
    lines = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
                           capture_output=True, text=True).stdout.splitlines()
    return "\\n".join(line for line in lines if ".gov-runtime/" not in line)


def head_of(root, result):''')
open(p, "w").write(s)
