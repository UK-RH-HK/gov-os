#!/usr/bin/env bash
# Re-pin gov from release 0.1.3 (EMERGENCY-2.md 6.1, 7.6, 8.3: gov update for EXAMIN): the owner's act, in a plain terminal, after the
# owner made release 0.1.3 (gov release 0.1.3 at the version commit C, the record committed, the annotated tag v0.1.3 on
# the record commit). As 0.1.2's script, the version changed:
# the store is not rebuilt (0.1.3 changes no store or rebuild code, retrieval only its memory-use line; the reference-transaction hook keeps it
# fresh through the new link); the reranker is not restarted (its bytes are unchanged; checked below).
#     bash docs/emergency-2/release-0.1.3/repin.sh 2>&1 | tee -a ~/repin-rel-0.1.3.log
# Stops at the first failure before the switch (nothing changed for sessions); after the switch a failed check switches
# straight back to the old pin and prints ROLLED BACK.
set -euo pipefail
REPO=${GOV_REPIN_REPO:-/home/usain/Dynamic-Agentic-Engineering-OS}   # the rehearsal names a scratch clone
VERSION=0.1.3; TAG=v$VERSION; REL=docs/releases/$VERSION
P=$HOME/.local/share/gov-os; BIN=$HOME/.local/bin
STORE=$HOME/gov-os-worktrees/W2-00-store
X=$(mktemp -d /tmp/repin-rel-$VERSION.XXXXXX)
stop() { echo; echo "STOP: $1"; echo "Nothing was switched: $BIN/gov -> $(readlink -f "$BIN/gov"). Tell the CTO."; exit 1; }
[ -z "${CLAUDECODE:-}${GOV_ROLE:-}${GOV_TICKET:-}" ] || stop "run this in a plain terminal (CLAUDECODE, GOV_ROLE or GOV_TICKET is set)"
cd "$REPO"

echo "== 0. the live pin"
OLDPIN=$(basename "$(dirname "$(dirname "$(readlink -f "$BIN/gov")")")")
case "$OLDPIN" in pin-*) ;; *) stop "$BIN/gov does not point into a pin ($OLDPIN)";; esac
echo "live: $OLDPIN ($("$BIN/gov" --version 2>&1 | head -1))"

echo "== R. the tag $TAG, its record and C"
[ "$(git cat-file -t "refs/tags/$TAG" 2>/dev/null)" = tag ] || stop "$TAG is not an annotated tag"
TAGC=$(git rev-parse "$TAG^{commit}")
FULL=$(git rev-parse "$TAGC^"); C=${FULL:0:12}
changed=$(git diff --name-only "$FULL" "$TAGC" | sort | tr '\n' ' ')
[ "$changed" = "$REL/manifest.json $REL/manifest.sha256 " ] || stop "between C ($C) and $TAG more than the record changed: $changed"
mkdir -p "$X/rec"
git show "$TAGC:$REL/manifest.json" > "$X/rec/manifest.json"
git show "$TAGC:$REL/manifest.sha256" > "$X/rec/manifest.sha256"
(cd "$X/rec" && sha256sum -c --strict --quiet manifest.sha256) || stop "manifest.json does not match manifest.sha256"
read -r SHA CLI < <(python3 - "$X/rec/manifest.json" "$VERSION" "$FULL" <<'PY'
import json, re, sys
m = json.load(open(sys.argv[1])); w = m.get("wheel") or {}; cli = m.get("cli_version")
ok = m.get("version") == sys.argv[2] and m.get("commit") == sys.argv[3] and w.get("name") == f"gov-{cli}-py3-none-any.whl" \
    and re.fullmatch(r"[0-9a-f]{64}", str(w.get("sha256")))
print(f"{w['sha256']} {cli}" if ok else "- -")
PY
)
[ "$SHA" != - ] || stop "the manifest does not name version $VERSION, commit $FULL and a wheel with its sha256"
EPOCH=$(git show -s --format=%ct "$FULL")
WHL=gov-$CLI-py3-none-any.whl
N=$P/pin-$C; W=$P/wheels/$C/$WHL
echo "ok: $TAG on ${TAGC:0:12}, C=$C, cli $CLI, wheel sha256 ${SHA:0:16}"

echo "== A. the wheel of C, built twice, checked against the record; its own environment"
[ ! -e "$N" ] || stop "$N already exists (an earlier run): remove it first (rm -rf $N) if it is not live"
for n in 1 2; do
  mkdir -p "$X/src-$n" "$X/wheel-$n"
  git archive "$FULL" | tar -x -C "$X/src-$n"
  SOURCE_DATE_EPOCH=$EPOCH python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$X/wheel-$n" "$X/src-$n" > /dev/null
done
a=$(sha256sum "$X/wheel-1/$WHL" | cut -d' ' -f1); b=$(sha256sum "$X/wheel-2/$WHL" | cut -d' ' -f1)
[ "$a" = "$b" ] || stop "the two builds differ"
[ "$a" = "$SHA" ] || stop "the wheel's sha256 ($a) is not the record's ($SHA)"
mkdir -p "$P/wheels/$C"; cp "$X/wheel-1/$WHL" "$W"
python3 -m venv --system-site-packages "$N"
"$N/bin/python" -m pip install -q --no-deps --no-index "$W"
v=$("$N/bin/gov" --version 2>&1 | head -1)
case "$v" in *"$CLI"*) echo "ok: $N/bin/gov --version: $v";; *) stop "the new pin's gov --version says '$v', not $CLI";; esac
svc=$(pgrep -f 'rerank_service\.py' | head -1 || true)
if [ -n "$svc" ]; then
  f=$(tr '\0' '\n' < /proc/$svc/cmdline | grep 'rerank_service\.py$' | head -1)
  cmp -s "$f" "$N/lib/python3.12/site-packages/gov/retrieval/rerank_service.py" \
    && echo "ok: the shared reranker (pid $svc) has the new pin's bytes: no restart" \
    || echo "NOTE: the shared reranker (pid $svc) differs from the new pin's; it keeps running; the CTO restarts it"
fi

echo "== D. the switch (an atomic rename), then the checks through the link"
rollback() {
  ln -sfn "$P/$OLDPIN/bin/gov" "$BIN/gov.new" && mv -Tf "$BIN/gov.new" "$BIN/gov"; hash -r
  echo; echo "ROLLED BACK: $1"; echo "$BIN/gov -> $(readlink -f "$BIN/gov"). Tell the CTO."; exit 1
}
ln -sfn "$N/bin/gov" "$BIN/gov.new" && mv -Tf "$BIN/gov.new" "$BIN/gov"; hash -r
[ "$(readlink -f "$BIN/gov")" = "$(readlink -f "$N/bin/gov")" ] || rollback "the link does not name pin-$C"
"$BIN/gov" --help > /dev/null 2>&1 || rollback "gov --help through the new pin failed"
(cd "$STORE" && "$BIN/gov" retrieve "what decides a close" --json > "$X/search.json") || rollback "a search through the new pin failed"
python3 -c "import json,sys; r=json.load(open(sys.argv[1]))['result']; f=r['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) else 1)" "$X/search.json" \
  || rollback "a search through the new pin lost a facet"
"$BIN/gov" launch --help > /dev/null 2>&1 || rollback "gov launch --help through the new pin failed"
echo "ok: $BIN/gov -> $(readlink -f "$BIN/gov"); gov --help, gov launch --help and a search (both facets) work"

echo "== E. the registry entry, committed as the owner's"
python3 - "$REPO/governance/project/tool-registry.yaml" "$C" "$SHA" "$VERSION" "$CLI" "$OLDPIN" "$(sha256sum < "$N/bin/gov" | cut -d' ' -f1)" <<'PY'
import datetime, re, sys
path, c, sha, version, cli, oldpin, script = sys.argv[1:8]
text = open(path, encoding="utf-8").read()
start = text.index("  - name: gov\n")
end = text.find("\n  - name: ", start + 1); end = len(text) if end == -1 else end + 1
whl = f"gov-{cli}-py3-none-any.whl"
new = ('  - name: gov\n'
       f'    version: "{version}"\n'
       f'    sha256: "{sha}"\n'
       f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{c} && ~/.local/share/gov-os/pin-{c}/bin/python -m pip install --no-deps --no-index ~/.local/share/gov-os/wheels/{c}/{whl} && ln -s ~/.local/share/gov-os/pin-{c}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov"\n'
       f'    uninstall: "ln -s ~/.local/share/gov-os/{oldpin}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov && rm -rf ~/.local/share/gov-os/pin-{c}"\n'
       f'    date: "{datetime.date.today().isoformat()}"\n'
       f'    approved_by: "DEC-1209"\n'
       f'    note: "Re-pin from release {version} (EMERGENCY-2.md 6.1, 8.3; the owner\'s act): the wheel of the numbered release {version}, tag v{version} on the record commit whose parent is {c}; built twice from {c} with SOURCE_DATE_EPOCH, equal to the record\'s sha256; its own environment ~/.local/share/gov-os/pin-{c}; linked from ~/.local/bin/gov by an atomic rename (script sha256 {script}). Replaces the entry of {oldpin}, kept for a one-command rollback (the uninstall line)."\n')
open(path, "w", encoding="utf-8").write(text[:start] + new + text[end:])
PY
git commit -q -F - -- governance/project/tool-registry.yaml <<MSG
Re-pin from release $VERSION: gov from the release's wheel (tag $TAG, commit $C)

The wheel built twice from $C equals the release record's sha256; $OLDPIN kept for the rollback.

Role: owner
Task: emergency-2
Implements: DEC-1209
MSG
echo "committed: $(git log -1 --format='%h %s')"
echo; echo "RE-PIN DONE: pin-$C (release $VERSION) is live; $OLDPIN kept. Rollback:"
echo "  ln -sfn $P/$OLDPIN/bin/gov $BIN/gov.new && mv -Tf $BIN/gov.new $BIN/gov; hash -r"
