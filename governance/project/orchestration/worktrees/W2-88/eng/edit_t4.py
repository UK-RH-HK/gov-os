p = "tests/unit/adopt/test_w2_88_layout.py"
s = open(p).read()
s = s.replace('''        root = repo_with_record(tmp_path / str(found))
''', '''        (tmp_path / str(found)).mkdir()
        root = repo_with_record(tmp_path / str(found))
''')
open(p, "w").write(s)

p = "src/gov/adopt/fabric.py"
s = open(p).read()
s = s.replace('''        project.git(root, "--literal-pathspecs", "add", "--", *copies["written"])
    except BaseException:''', '''        project.git(root, "--literal-pathspecs", "add", "--", *copies["written"])
        for entry in project.git(root, "--literal-pathspecs", "ls-files", "-s", "-z", "--", *copies["written"]).split("\\0"):
            meta, _, rel = entry.partition("\\t")
            if rel:  # the copies are tracked files of the project from here on: judged like every other
                run.tracked[rel] = meta.split()[1]
    except BaseException:''')
s = s.replace('''what ``undo`` removes. An untracked file at a destination is never overwritten (refused, naming it)."""''', '''what ``undo`` removes. The copies join ``run.tracked`` (the stores judge them like any file). An untracked file at a
    destination is never overwritten (refused, naming it)."""''')
open(p, "w").write(s)
