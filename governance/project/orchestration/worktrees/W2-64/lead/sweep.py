"""Lead's feasibility sweep (scratch, not the implementation): every record's frontmatter through check-jsonschema,
batched per schema file, docs/imported/ left out. Prints the failing records and the time."""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "src"))
from gov.check import schema as S  # noqa: E402

root = Path(sys.argv[1])
start = time.monotonic()
groups = {}
for record_dir in S.RECORD_PATHS:
    for md in sorted((root / record_dir).rglob("*.md")):
        rel = md.relative_to(root).as_posix()
        if rel.startswith("docs/imported/"):
            continue
        front = S._frontmatter(md.read_text(encoding="utf-8"))
        if front is None:
            continue
        in_audit = md.is_relative_to(root / S.AUDIT_REPORT_DIR)
        kind = front.get("type", S.AUDIT_REPORT_TYPE if in_audit else None)
        sf = S.SCHEMA_MAP.get(kind) if isinstance(kind, str) else None
        if sf:
            groups.setdefault(sf, []).append((rel, front))
tmp = Path(tempfile.mkdtemp(dir="/tmp/gov-os-lead-W2-64"))
total = 0
for sf, recs in sorted(groups.items()):
    files = []
    for i, (rel, front) in enumerate(recs):
        p = tmp / f"{sf}-{i}.json"
        p.write_text(json.dumps(front, default=str))
        files.append((str(p), rel))
    total += len(files)
    names = dict(files)
    out = subprocess.run(["check-jsonschema", "-v", "-o", "json", "--schemafile",
                          str(root / S.SCHEMA_DIR / sf)] + [f for f, _ in files],
                         capture_output=True, text=True)
    data = json.loads(out.stdout)
    for err in data["errors"]:
        print(sf, names.get(err["filename"], err["filename"]), err["path"], err["message"][:160])
    for err in data.get("parse_errors", data.get("parse-errors", [])):
        print("PARSE", sf, err)
    print(f"# {sf}: {len(files)} records, exit {out.returncode}, "
          f"{len(data.get('successes', []))} ok", file=sys.stderr)
print(f"# {total} records in {time.monotonic() - start:.2f} s", file=sys.stderr)
