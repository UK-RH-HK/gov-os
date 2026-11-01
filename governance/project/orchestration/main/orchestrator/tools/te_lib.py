"""Small exact editors for ticket files (front matter kept as written) and a commit helper (DEC-954 ticket edits).
Every edit asserts what it expects to find, so a ticket that drifted from the draft stops the run."""
import pathlib
import re
import subprocess
import time

import yaml

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ORCH = ROOT / ".gov-runtime/scratch/orchestrator"
CO = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def q(s):
    return "'" + s.replace("'", "''") + "'"


class T:
    def __init__(self, tid):
        self.tid = tid
        self.path = ROOT / ".tickets" / (tid + ".md")
        text = self.path.read_text(encoding="utf-8")
        assert text.startswith("---\n"), tid
        end = text.index("\n---\n", 4)
        self.fm = text[4:end].split("\n")
        self.body = text[end + 5:]

    # -- front matter ---------------------------------------------------------------------------------------------
    def _key(self, key):
        idx = [i for i, l in enumerate(self.fm) if l.startswith(key + ":")]
        assert len(idx) == 1, (self.tid, key, idx)
        return idx[0]

    def get(self, key):
        return self.fm[self._key(key)][len(key) + 1:].strip()

    def set(self, key, value, was=None):
        i = self._key(key)
        if was is not None:
            assert self.fm[i] == f"{key}: {was}", (self.tid, self.fm[i], was)
        self.fm[i] = f"{key}: {value}"

    def _block(self, key):
        """Index range of a block list's '- ' items under a top-level key (empty if inline)."""
        i = self._key(key)
        j = i + 1
        while j < len(self.fm) and self.fm[j].startswith("- "):
            j += 1
        return i, j

    def list_items(self, key):
        i, j = self._block(key)
        rest = self.fm[i][len(key) + 1:].strip()
        if rest:
            assert rest.startswith("[") and rest.endswith("]"), (self.tid, key, rest)
            return [x.strip() for x in rest[1:-1].split(",") if x.strip()]
        return [l[2:] for l in self.fm[i + 1:j]]

    def set_list(self, key, items, inline=None):
        i, j = self._block(key)
        rest = self.fm[i][len(key) + 1:].strip()
        if inline is None:
            inline = bool(rest)
        if inline:
            self.fm[i:j] = [f"{key}: [{', '.join(items)}]"]
        else:
            self.fm[i:j] = [f"{key}:"] + [f"- {x}" for x in items]

    def add(self, key, *items):
        cur = self.list_items(key)
        self.set_list(key, cur + [x for x in items if x not in cur])

    def drop(self, key, *items):
        cur = self.list_items(key)
        for x in items:
            assert x in cur, (self.tid, key, x)
        self.set_list(key, [x for x in cur if x not in items])

    def add_tags(self, *tags):
        self.add("tags", *tags)

    def deps(self, items):
        """Set deps (inline) and depends_on (its own form) to the same list."""
        self.set_list("deps", items, inline=True)
        self.set_list("depends_on", items)

    # kpis.success items: '  - ' lines plus their continuation lines ('    ' indented)
    def _success(self):
        s = self.fm.index("  success:")
        f = next(i for i in range(s + 1, len(self.fm)) if not self.fm[i].startswith("  - ") and not self.fm[i].startswith("    "))
        items, cur = [], None
        for i in range(s + 1, f):
            if self.fm[i].startswith("  - "):
                cur = [i, i + 1]
                items.append(cur)
            else:
                cur[1] = i + 1
        return s, f, items

    def kpi_append(self, text):
        s, f, items = self._success()
        self.fm.insert(f, "  - " + q(text))

    def kpi_replace(self, n, text, startswith):
        s, f, items = self._success()
        a, b = items[n]
        assert startswith in self.fm[a], (self.tid, n, self.fm[a][:80])
        self.fm[a:b] = ["  - " + q(text)]

    def kpi_append_to(self, n, suffix, startswith):
        """Append a sentence to the n-th success KPI (re-quoted as one line)."""
        s, f, items = self._success()
        a, b = items[n]
        assert startswith in self.fm[a], (self.tid, n, self.fm[a][:80])
        cur = yaml.safe_load("x:\n" + "\n".join(self.fm[a:b]))["x"][0]
        self.fm[a:b] = ["  - " + q(cur.rstrip() + suffix)]

    def kpi_set_all(self, texts):
        s, f, items = self._success()
        self.fm[s + 1:f] = ["  - " + q(t) for t in texts]

    def failure_set(self, texts):
        i = self.fm.index("  failure: []")
        self.fm[i:i + 1] = ["  failure:"] + ["  - " + q(t) for t in texts]

    # -- body -------------------------------------------------------------------------------------------------------
    def body_line(self, line):
        if line in self.body:
            return
        m = re.search(r"^# .*$", self.body, re.M)
        assert m, self.tid
        self.body = self.body[:m.end()] + "\n\n" + line + self.body[m.end():]

    # -- write, check, commit -------------------------------------------------------------------------------------------
    def text(self):
        return "---\n" + "\n".join(self.fm) + "\n---\n" + self.body

    def save(self):
        t = self.text()
        yaml.safe_load("\n".join(self.fm))
        self.path.write_text(t, encoding="utf-8")
        r = subprocess.run(["python3", str(ORCH / "tools/placeholder_scan.py"), str(self.path)], capture_output=True, text=True)
        assert "0 hit(s)" in r.stdout, (self.tid, r.stdout, r.stderr)


def commit(subject, paths, trailers):
    args = ["git", "-C", str(ROOT), "commit", "-q", "-m", subject]
    for t in trailers + [CO]:
        args += ["--trailer", t]
    args += ["--"] + [str(p) for p in paths]
    for _ in range(30):
        a = subprocess.run(["git", "-C", str(ROOT), "add", "--"] + [str(p) for p in paths], capture_output=True, text=True)
        if "index.lock" in a.stderr:
            time.sleep(10)
            continue
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode == 0:
            return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short=8", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()
        if "index.lock" in r.stderr:
            time.sleep(10)
            continue
        if "nothing to commit" in (r.stdout + r.stderr) or "no changes added" in (r.stdout + r.stderr):
            return None
        raise SystemExit(f"commit failed: {subject}: {r.stdout} {r.stderr}")
    raise SystemExit("index.lock held too long")
