"""Assemble the narrow check's auditor brief a7: head, JUDGEMENT.md word for word, tail, the context packet."""
import re, subprocess, sys
B = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/"
J = "/home/usain/gov-os-worktrees/W2-42a/governance/project/briefs/JUDGEMENT.md"
head = subprocess.run(["git", "-C", "/home/usain/gov-os-worktrees/W2-42a", "rev-parse", "HEAD"],
                      capture_output=True, text=True, check=True).stdout.strip()
scoped = sys.argv[1]
claims = """eng-6's stated claims and risks: (a) a variable `read` binds from a here-string,
  used as a command's name (also behind `env`, `command`, `time`, `stdbuf`, `setsid`, …) or as an argument of a program
  that runs its words (`xargs`, `sudo`, `doas`, `parallel`, `watch`, `find -exec`), gives the unresolvable target; as an
  argument of a command that runs nothing it stays free; (b) `mapfile`/`readarray -C` (separate, joined `-tC`, glued
  `-C'cmd'`) judges a literal callback as that command, a variable, substitution or unknown callback (a function such as
  `cb`) gives the unresolvable target, with or without a here-string; it says it does not cover `read f < file; $f`
  (no here-string) nor a variable read inside a substitution and used outside it, and that `xargs echo $f` is now
  refused (a false positive it accepts).
- The lead's probe of the head (pointers, not findings): every T form td-9 pinned is refused; still allowed at the head
  and refused at 209ec8464, each writing T in real bash with a literal text: `mapfile -t L <<< 'touch T'; "${L[@]}"`,
  `readarray -t L <<< 'touch T'; ${L[0]}`, `read -r a <<< 'touch T'; b=$a; $b`,
  `f=$(read -r x <<< 'touch T'; echo $x); $f`, `read -r a <<< 'touch T'; echo "$a" | sh`; their siblings without a
  here-string are allowed at both commits (`echo 'touch T' | sh`, `a="$v"; $a`, `read -r a < x.py; $a`,
  `mapfile -t L < x.py; "${L[@]}"`). Loop bodies `ssh h` and `docker exec -i c sh` over a here-string are allowed at the
  head (eng-5's stated risk). Judge each by the two questions."""
h = open(B + "r6/a7-head.md").read().replace("HEAD_FULL", head).replace("SCOPED_LINE", scoped)
h = h.replace("ENG6_CLAIMS", claims).replace("ENG6_COMMIT", "9196ce961")
tail = open(B + "briefs/a3-tail.md").read()
tail = tail.replace("Then the fenced verdict block, one entry per line S1-S11, F1, F2:",
                    "Then the fenced verdict block, one entry per line RO, NRA, DEC409:")
tail = tail.replace('{"kpi": "S1"', '{"kpi": "RO"')
tail = tail.replace("(gov context DAEO-03ub --role independent-auditor)",
                    "(gov context DAEO-03ub --role independent-auditor --budget 12000)")
parts = [h, open(J).read(), "\n", tail, "\n```json\n", open(B + "r6/ctx-independent-auditor.md").read(), "\n```\n"]
text = "".join(parts)
open(B + "r6/a7.md", "w").write(text)
print(head, text.count("\n"), "lines; slots:", re.findall(r"\b(HEAD_FULL|SCOPED_LINE|ENG6_\w+)\b", text),
      re.findall(r"\{[A-Z_]+\}", text), "verdict ids ok:", "RO, NRA, DEC409" in text, "JUDGEMENT in:", open(J).read() in text)
