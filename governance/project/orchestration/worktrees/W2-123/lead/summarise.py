"""Summarise measure.py's JSON lines: summarise.py <sweep.jsonl>..."""
import json
import sys

print("| parallel | cap | runner -np | determinism (256, n in flight) | alone c/s | alone stage s | alone cores | "
      "alone GPU % | three total c/s | three per-rebuild c/s | three stage s | three cores | three GPU % | load |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for path in sys.argv[1:]:
    for line in open(path):
        r = json.loads(line)
        if r["kind"] == "sample":
            corpus = r["corpus_chunks"]
            continue
        if r["kind"] == "full":
            s = r["stage"]
            print(f"full stage: parallel {r['parallel']} {r['cap']}: {s['chunks']} chunks in {s['wall_s']} s "
                  f"({s['chunks_per_s']} c/s), cores {s['cores_busy']}, gpu {s['gpu']}, load {s['load1']:.1f}, "
                  f"differ vs stored {s['per_rebuild'][0]['differ']}")
            continue
        a, t, d = r["alone"], r["three"], r["determinism"]
        settings = r["started"]["settings"]
        cap = f"{r['cap']} ({settings.get('cpus')}, nice {settings.get('nice')})"
        np_ = r["started"]["runners"][0]["np"] if r["started"]["runners"] else "?"
        per = "/".join(str(p["chunks_per_s"]) for p in t["per_rebuild"])
        print(f"| {r['parallel']} | {cap} | {np_} | {d['verdict']} ({d['differing']} differ) | {a['chunks_per_s']} | "
              f"{r['stage_s_alone']} | {a['cores_busy']} | {(a['gpu'] or {}).get('util_mean')} | {t['chunks_per_s']} | "
              f"{per} | {r['stage_s_three']} | {t['cores_busy']} | {(t['gpu'] or {}).get('util_mean')} | "
              f"{t['load1']:.1f} |")
