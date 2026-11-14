Also, for this batch (the failing cases below are of these kinds):
- In `<rev>:<path>` the path starts at the top of the tree `<rev>` names. Only a commit (or the index: an empty
  `<rev>`, `:<n>:`) places it at the repository's top; a `<rev>` that names a tree other than a commit's top (a
  subtree's id) cannot be placed: for a session with a refused part it is a ruled refusal, in git diff, git show and
  git cat-file alike.
- An object named by its id alone that git prints as a file's text (`git cat-file blob <id>`, `git cat-file -p <id>`
  of a blob) is a ruled refusal for a session with a refused part, as `git show <blob id>` already is; `-t`, `-s`,
  `-e` and a commit object stay allowed.
- git's own `--output=<file>` and `--output <file>` (git diff, show, log) write that file: the parser gives it as a
  write target (resolved against the command's cwd, also after `git -C` and `cd`), so the write rules judge it; the
  file word of `--output <file>` is no revision word for the read judge.
