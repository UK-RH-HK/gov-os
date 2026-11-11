#!/usr/bin/env python3
"""ACT-P95-1's tool (DEC-1133 (3), DEC-1138 (4)): the p95 of the sampled working sizes, in place of `gov resources
--remeasure`'s maximum, and the two peak figures from the same day.

`gov resources --remeasure` writes `working_size_bytes` as the LARGEST session sample taken outside a verification run
(src/gov/resources/measure.py, figures()). The owner wants the p95. DEC-1138 (4) adds: the ACT also rewrites both peak
figures from the sample day's measurements, rather than leaving them. This tool never writes the live gate file. It
freezes an operator bundle (the form of acts/ACT-NIGHTLY-RESTART-1) whose "after" gate.json differs from the "before" in
at most three keys, `working_size_bytes`, `verification_peak_bytes` and `rebuild_peak_bytes` (each peak only when the
day holds enough measurements of it), and can recompute that after file from the evidence the bundle holds.

What each figure means here (decided from what `gov resources --sample` records: a session item per live session, with
`verification` = whether a process held the verification lock; a slot-holder item per heavy job, with `kind` test|rebuild;
the product's gate uses only `working_size_bytes`, so the peaks are read by gate_check.py and the owner, not by the gate):
  working_size_bytes       the p95 of the session samples taken outside verification (a lead's ordinary working size);
  verification_peak_bytes  the LARGEST sample of a verification run: a `kind` = test slot holder's process tree (the
                           run itself, in its slot, DEC-1038 (4)), or a session sample taken while the verification lock
                           was held. A peak is a maximum by meaning. (The product's --remeasure writes the largest of all
                           session samples instead: a lead's whole tree at any moment, not a run's peak; the figures
                           text shows that figure beside this one.)
  rebuild_peak_bytes       the LARGEST sample of a `kind` = rebuild slot holder (the same rule as the product's).
A peak figure with fewer than --min-peak-samples samples behind it (default 3: a run seen once or twice is only a lower
bound) is LEFT as it is, with a note in the figures text; it is never invented or carried over from the other peak.

  figures [--samples PATH] [--since ISO]      read-only: the sample set's p50, p95 and max, per role, and what each
                                              route would write
  build   --out DIR [--samples PATH] [--gate PATH] [--date YYYY-MM-DD] [--since ISO]
          [--min-samples N] [--min-hours H] [--min-peak-samples N]
                                              freeze the bundle (before, after, evidence, apply.sh, list.txt)
  manifest DIR --rehearsal LOG                 copy the rehearsal log in and write manifest.json (files, checks)
  verify  DIR                                  recompute the after file from the bundle's evidence; exit 0 only when it
                                               is byte for byte the frozen one (and the manifest's checks are the tool's)

Population (the product's own, measure.figures): the `samples` of each line, an item whose `tree_memory_bytes` is an
integer (not a bool), not a slot holder (no `kind` key), taken while `verification` is False. Percentile: nearest rank,
the ceil(0.95 * n)-th smallest sample (an observed size, an integer, integer arithmetic only). It refuses (writes
nothing) with fewer than --min-samples such samples (default 40) or a span under --min-hours (default 6), so a short or
thin day can never write a "p95" that is the maximum in all but name.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ACT = "ACT-P95-1"
DEC = "DEC-1133, DEC-1105, DEC-1138"
KEY = "working_size_bytes"
VERIF, REBUILD = "verification_peak_bytes", "rebuild_peak_bytes"
PEAK_KEYS = (VERIF, REBUILD)
ROOT, REL = "home", ".gov-os/machine/gate.json"
PCT = 95
MIN_SAMPLES = 40
MIN_HOURS = 6.0
MIN_PEAK_SAMPLES = 3
HERE = Path(__file__).resolve().parent


class Refused(Exception):
    pass


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def when(text) -> datetime.datetime:
    try:
        stamp = datetime.datetime.fromisoformat(str(text))
    except ValueError:
        raise Refused(f"not an ISO time: {text!r}") from None
    if stamp.tzinfo is None:
        raise Refused(f"a time with no zone: {text!r} (the samples' times carry +00:00)")
    return stamp


# --- the samples ------------------------------------------------------------------------------------------------------

def read_lines(data: bytes, since: str | None = None) -> list[dict]:
    """The sample lines (one JSON object per line), from `since` on when given. A line that is not JSON, not an
    object, or has no usable time is refused: nothing is skipped silently."""
    cut = when(since) if since else None
    lines = []
    for number, raw in enumerate(data.decode("utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            line = json.loads(raw)
        except ValueError as error:
            raise Refused(f"samples line {number} is not JSON: {error}") from None
        if not isinstance(line, dict):
            raise Refused(f"samples line {number} is not a JSON object")
        stamp = when(line.get("time"))
        if cut is None or stamp >= cut:
            lines.append(line)
    return lines


def populations(lines: list[dict]) -> tuple[list[int], list[int], dict[str, list[int]]]:
    """(every session sample, those outside verification, those outside verification by role): the product's filter."""
    every, outside, by_role = [], [], {}
    for line in lines:
        for item in line.get("samples", []):
            size = item.get("tree_memory_bytes") if isinstance(item, dict) else None
            if isinstance(size, bool) or not isinstance(size, int):
                continue
            if "kind" in item:  # a slot holder: no session
                continue
            every.append(size)
            if item.get("verification") is False:
                outside.append(size)
                by_role.setdefault(str(item.get("role") or "?"), []).append(size)
    return every, outside, by_role


def peak_populations(lines: list[dict]) -> tuple[list[int], list[int]]:
    """(the samples of a verification run, the samples of a rebuild), each a size in bytes.
    A verification run: a `kind` = test slot holder's tree, or a session sample taken while the lock was held.
    A rebuild: a `kind` = rebuild slot holder's tree (the product's own rule). Bools and strings are out."""
    verification, rebuild = [], []
    for line in lines:
        for item in line.get("samples", []):
            size = item.get("tree_memory_bytes") if isinstance(item, dict) else None
            if isinstance(size, bool) or not isinstance(size, int):
                continue
            if "kind" in item:
                if item["kind"] == "test":
                    verification.append(size)
                elif item["kind"] == "rebuild":
                    rebuild.append(size)
            elif item.get("verification") is True:
                verification.append(size)
    return verification, rebuild


def nearest_rank(values: list[int], pct: int = PCT) -> int:
    """The ceil(pct * n / 100)-th smallest value: always an observed one, integer arithmetic only."""
    ordered = sorted(values)
    k = -(-pct * len(ordered) // 100)
    return ordered[k - 1]


def span_hours(lines: list[dict]) -> float:
    if not lines:
        return 0.0
    stamps = [when(line["time"]) for line in lines]
    return (max(stamps) - min(stamps)).total_seconds() / 3600


def measure(lines: list[dict], min_samples: int, min_hours: float, min_peak_samples: int = MIN_PEAK_SAMPLES) -> dict:
    _, outside, _ = populations(lines)
    if not outside:
        raise Refused("no session sample outside verification: nothing to measure")
    if len(outside) < min_samples:
        raise Refused(f"{len(outside)} session samples outside verification, fewer than the {min_samples} needed for a p95")
    hours = span_hours(lines)
    if hours < min_hours:
        raise Refused(f"the samples span {hours:.1f} h, under the {min_hours:g} h of a working day")
    times = sorted(line["time"] for line in lines)
    out = {"n": len(outside), "p95": nearest_rank(outside), "max": max(outside), "first": times[0], "last": times[-1],
           "hours": hours, "peaks": {}, "left": {}}
    verification, rebuild = peak_populations(lines)
    for key, values, what in ((VERIF, verification, "verification-run"), (REBUILD, rebuild, "rebuild")):
        if len(values) >= min_peak_samples:
            out["peaks"][key] = {"value": max(values), "n": len(values), "what": what}
        else:
            out["left"][key] = (f"{key} is LEFT as it is: the day holds {len(values)} {what} sample(s), fewer than the "
                                f"{min_peak_samples} needed for a peak (a run seen that few times is only a lower bound)")
    return out


def mb(value) -> str:
    return "none" if value is None else f"{value / 1e6:,.0f} MB"


def figures_text(lines: list[dict], min_peak_samples: int = MIN_PEAK_SAMPLES) -> str:
    every, outside, by_role = populations(lines)
    out = [f"{len(lines)} sample lines, {len(every)} session samples, {len(outside)} outside verification, "
           f"span {span_hours(lines):.1f} h"]
    for role, values in sorted(by_role.items()):
        out.append(f"  {role:<14} n={len(values):<6} p50 {mb(nearest_rank(values, 50)):>10}  "
                   f"p95 {mb(nearest_rank(values)):>10}  max {mb(max(values)):>10}")
    if outside:
        p95, top = nearest_rank(outside), max(outside)
        out.append(f"working_size_bytes: `gov resources --remeasure` would write the MAXIMUM {top} ({mb(top)}); "
                   f"ACT-P95-1 writes the p95 {p95} ({mb(p95)}), {100 * (top - p95) / top:.0f} % lower")
    else:
        out.append("working_size_bytes: no session sample outside verification; nothing would be written")
    verification, rebuild = peak_populations(lines)
    every_max = max(every) if every else None
    rebuild_max = max(rebuild) if rebuild else None
    for key, values, what, product in ((VERIF, verification, "verification-run", every_max),
                                       (REBUILD, rebuild, "rebuild", rebuild_max)):
        if len(values) >= min_peak_samples:
            out.append(f"{key}: ACT-P95-1 writes the largest of {len(values)} {what} sample(s): {max(values)} "
                       f"({mb(max(values))}); `gov resources --remeasure` would write {product} ({mb(product)})"
                       + (" (the same rule)" if key == REBUILD else " (the largest of all session samples)"))
        else:
            out.append(f"{key}: LEFT as it is: {len(values)} {what} sample(s), fewer than the {min_peak_samples} needed "
                       f"(`gov resources --remeasure` would write {product} ({mb(product)}))")
    return "\n".join(out) + "\n"


# --- the gate file ---------------------------------------------------------------------------------------------------

def dumps(data: dict) -> bytes:
    """The product's own writer (resources/config.py write()): json.dump(indent=2) and a newline."""
    return (json.dumps(data, indent=2) + "\n").encode("utf-8")


def parse_gate(before: bytes) -> dict:
    try:
        data = json.loads(before.decode("utf-8"))
    except ValueError as error:
        raise Refused(f"the gate file is not JSON: {error}") from None
    if not isinstance(data, dict):
        raise Refused("the gate file is not a JSON object")
    if dumps(data) != before:
        raise Refused("the gate file is not in the product's own form (indent 2, one newline): the after file would change more than one key")
    entry = data.get(KEY)
    if not isinstance(entry, dict) or isinstance(entry.get("value"), bool) or not isinstance(entry.get("value"), int):
        raise Refused(f"the gate file's {KEY} is missing or malformed")
    return data


def source_text(figures: dict, samples_sha: str, pct: int = PCT) -> str:
    return (f"{ACT}, {DEC.split(',')[0]} (3): the p{pct} (nearest rank) of {figures['n']} session samples outside "
            f"verification, {figures['first']} to {figures['last']} (samples.jsonl sha256 {samples_sha[:12]}); "
            f"gov resources --remeasure would have written the maximum")


def peak_source_text(key: str, peak: dict, figures: dict, samples_sha: str) -> str:
    return (f"{ACT}, {DEC.split(',')[2].strip()} (4): the largest of {peak['n']} {peak['what']} sample(s) (a peak is a "
            f"maximum), {figures['first']} to {figures['last']} (samples.jsonl sha256 {samples_sha[:12]})")


def changed_keys(before: bytes, after: bytes) -> dict:
    """{key: entry} of the keys whose entry differs between the two gate files."""
    b, a = json.loads(before.decode("utf-8")), json.loads(after.decode("utf-8"))
    return {k: a[k] for k in a if b.get(k) != a[k]}


def make_after(before: bytes, samples: bytes, params: dict) -> tuple[bytes, dict]:
    data = parse_gate(before)
    lines = read_lines(samples, params.get("since"))
    figures = measure(lines, params["min_samples"], params["min_hours"], params.get("min_peak_samples", MIN_PEAK_SAMPLES))
    datetime.date.fromisoformat(params["date"])
    after = dict(data)
    after[KEY] = {"value": figures["p95"], "date": params["date"],
                  "source": source_text(figures, sha(samples))}
    for key, peak in figures["peaks"].items():
        after[key] = {"value": peak["value"], "date": params["date"],
                      "source": peak_source_text(key, peak, figures, sha(samples))}
    return dumps(after), figures


# --- the bundle ------------------------------------------------------------------------------------------------------

def checks_for(before: bytes, after: bytes) -> list[dict]:
    """The manifest's checks: each run `bash -c` from the repository root with HOME planted. They name no live path.
    The keys that differ between the before and the after (the working size, and each peak the day measured) are
    checked one by one; the rest of the file must hash as the before's."""
    data = json.loads(after.decode("utf-8"))
    changed = changed_keys(before, after)
    figs = {k: [e["value"], e["date"]] for k, e in changed.items()}
    rest = hashlib.sha256(json.dumps({k: v for k, v in data.items() if k not in changed}, sort_keys=True).encode()).hexdigest()
    exact = (f'import hashlib,json,os,sys; '
             f'd=json.load(open(os.environ["HOME"]+"/{REL}")); F={json.dumps(figs)}; '
             f'r=json.dumps({{k:v for k,v in d.items() if k not in F}},sort_keys=True); '
             f'sys.exit(0 if all(k in d and d[k]["value"]==v[0] and d[k]["date"]==v[1] and d[k]["source"].startswith("{ACT}") '
             f'for k,v in F.items()) '
             f'and hashlib.sha256(r.encode()).hexdigest()=="{rest}" '
             f'and list(d)=={json.dumps(list(data))} else 1)')
    loads = (f'import sys; sys.path.insert(0,"src"); from gov.resources import config; c=config.load(); F={json.dumps(figs)}; '
             f'sys.exit(0 if not c["faults"] and all(c["values"][k]==v[0] and k not in c["due"] for k,v in F.items()) else 1)')
    return [
        {"cmd": f'python3 -I -m json.tool "$HOME/{REL}" > /dev/null', "exit": 0, "count": None},
        {"cmd": f"python3 -I -c '{exact}'", "exit": 0, "count": None},
        {"cmd": f"python3 -B -c '{loads}'", "exit": 0, "count": None},
    ]


def write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def build(out: Path, samples_path: Path, gate_path: Path, params: dict) -> dict:
    if out.exists() and any(out.iterdir()):
        raise Refused(f"{out} exists and is not empty")
    before, samples = gate_path.read_bytes(), samples_path.read_bytes()
    after, figures = make_after(before, samples, params)
    lines = read_lines(samples, params.get("since"))
    write(out / "before" / ROOT / REL, before)
    write(out / "after" / ROOT / REL, after)
    write(out / "evidence" / "samples.jsonl", samples)
    write(out / "evidence" / "params.json", (json.dumps(params, indent=1, sort_keys=True) + "\n").encode())
    write(out / "evidence" / "figures.txt", figures_text(lines, params.get("min_peak_samples", MIN_PEAK_SAMPLES)).encode())
    write(out / "apply.sh", (HERE / "apply.sh").read_bytes())
    write(out / "list.txt", f"{ROOT}|{REL}|{sha(before)}|{sha(after)}\n".encode())
    return {"before": sha(before), "after": sha(after), "changed": list(changed_keys(before, after)), **figures}


def listed(bundle: Path) -> tuple[str, str, str, str]:
    root, path, before, after = (bundle / "list.txt").read_text().strip().split("|")
    return root, path, before, after


def manifest(bundle: Path, rehearsal: Path) -> str:
    root, path, before, after = listed(bundle)
    shutil.copyfile(rehearsal, bundle / "rehearsal.log")
    names = [f"before/{root}/{path}", f"after/{root}/{path}", "evidence/samples.jsonl", "evidence/params.json",
             "evidence/figures.txt", "apply.sh", "list.txt", "rehearsal.log"]
    files = {n: sha((bundle / n).read_bytes()) for n in names}
    if files[names[0]] != before or files[names[1]] != after:
        raise Refused("before/ or after/ does not hash as list.txt says")
    m = {"act": ACT, "dec": DEC, "author": "cto", "claimed_class": "b",
         "touched": [{"root": root, "path": path, "before": before, "after": after}],
         "files": files, "checks": checks_for((bundle / names[0]).read_bytes(), (bundle / names[1]).read_bytes()), "commands": [],
         "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}}
    text = json.dumps(m, indent=1) + "\n"
    (bundle / "manifest.json").write_text(text)
    return sha(text.encode())


def verify(bundle: Path) -> list[str]:
    """Why the bundle does not reproduce, as a list of reasons (empty: it does)."""
    why = []
    root, path, before_h, after_h = listed(bundle)
    before = (bundle / "before" / root / path).read_bytes()
    after = (bundle / "after" / root / path).read_bytes()
    if sha(before) != before_h or sha(after) != after_h:
        why.append("before/ or after/ does not hash as list.txt says")
    params = json.loads((bundle / "evidence" / "params.json").read_text())
    samples = (bundle / "evidence" / "samples.jsonl").read_bytes()
    try:
        again, _ = make_after(before, samples, params)
    except Refused as error:
        return why + [f"recomputing refuses: {error}"]
    if again != after:
        why.append("the after file is not what the evidence gives (p95, nearest rank; the peaks as largest)")
    mfile = bundle / "manifest.json"
    if mfile.exists():
        m = json.loads(mfile.read_text())
        if m.get("checks") != checks_for(before, after):
            why.append("the manifest's checks are not the tool's for this after file")
        for name, h in m.get("files", {}).items():
            if sha((bundle / name).read_bytes()) != h:
                why.append(f"{name} does not hash as the manifest says")
    return why


# --- the command line ------------------------------------------------------------------------------------------------

def default_samples() -> Path:
    return Path(os.environ.get("HOME", "~")) / ".gov-os" / "machine" / "samples.jsonl"


def main(argv: list[str]) -> int:
    top = argparse.ArgumentParser(prog="p95_remeasure.py", description=__doc__.splitlines()[0])
    sub = top.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("figures")
    f.add_argument("--samples", type=Path)
    f.add_argument("--since")
    f.add_argument("--min-peak-samples", type=int, default=MIN_PEAK_SAMPLES)
    b = sub.add_parser("build")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--samples", type=Path)
    b.add_argument("--gate", type=Path)
    b.add_argument("--date", default=datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    b.add_argument("--since")
    b.add_argument("--min-samples", type=int, default=MIN_SAMPLES)
    b.add_argument("--min-hours", type=float, default=MIN_HOURS)
    b.add_argument("--min-peak-samples", type=int, default=MIN_PEAK_SAMPLES)
    m = sub.add_parser("manifest")
    m.add_argument("bundle", type=Path)
    m.add_argument("--rehearsal", type=Path, required=True)
    v = sub.add_parser("verify")
    v.add_argument("bundle", type=Path)
    args = top.parse_args(argv)
    try:
        if args.cmd == "figures":
            path = args.samples or default_samples()
            sys.stdout.write(figures_text(read_lines(path.read_bytes(), args.since), args.min_peak_samples))
        elif args.cmd == "build":
            home = Path(os.environ.get("HOME", "~"))
            gate = args.gate or home / REL
            params = {"since": args.since, "date": args.date, "min_samples": args.min_samples,
                      "min_hours": args.min_hours, "min_peak_samples": args.min_peak_samples, "pct": PCT,
                      "method": "nearest rank; peaks = largest"}
            got = build(args.out, args.samples or default_samples(), gate, params)
            print(f"built {args.out}: {KEY} p{PCT} {got['p95']} (max {got['max']}), n {got['n']}, "
                  f"span {got['hours']:.1f} h; before {got['before'][:8]} after {got['after'][:8]}")
            for key, peak in got["peaks"].items():
                print(f"  {key}: {peak['value']} (largest of {peak['n']} {peak['what']} sample(s))")
            for note in got["left"].values():
                print(f"  NOTE {note}")
        elif args.cmd == "manifest":
            print(f"manifest sha256 {manifest(args.bundle, args.rehearsal)}")
        else:
            why = verify(args.bundle)
            for line in why:
                print("FAIL", line)
            if not why:
                print("verify: the after file is reproduced from the evidence")
            return 1 if why else 0
    except (Refused, OSError, ValueError, KeyError) as error:
        print(f"refused: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
