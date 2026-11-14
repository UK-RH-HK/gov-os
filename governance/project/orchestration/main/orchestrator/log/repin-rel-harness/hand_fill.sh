#!/usr/bin/env bash
# The hand checks of fill_release.sh and the operator's hash list (review F6; the 18-file list; review r2 F3), each to
# its own log under log/. Scratch copies only: no bundle file, tool or test is changed; the release read is run-f7's
# scratch clone.
set -uo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
O=$R/.gov-runtime/scratch/orchestrator
B=$O/drafts/repin-rel-0.1.0
L=$O/log
SP=$(cd "$(dirname "$0")" && pwd)/hand
REL=/tmp/gov-os-rel-repin/run-f7/release
C=f2f28ed4ef40
rm -rf "$SP"; mkdir -p "$SP"
head() { echo "== $1, $(date '+%F %T')"; echo "bundle: BUNDLE.sha256 sha256 $(sha256sum < "$B/BUNDLE.sha256" | cut -c1-12); the release read: $REL (run f7's scratch clone)"; }

# 1. F6: a byte changed in a bundle file after the review -> fill_release.sh refuses, writes nothing
{
  head "F6: fill_release.sh refuses a bundle that differs from BUNDLE.sha256"
  mkdir -p "$SP/f6"; cp -p "$B"/*.sh "$B"/*.py "$B"/*.md "$B/BUNDLE.sha256" "$SP/f6/"
  printf '# an edit after the review\n' >> "$SP/f6/rel_checks.sh"
  echo "-- the copy: one line added to rel_checks.sh; BUNDLE.sha256 as reviewed"
  bash "$SP/f6/fill_release.sh" "$C" "$REL" "$SP/f6/out.sh"; echo "exit $?"
  echo "files written: $(ls "$SP/f6/out.sh" "$SP/f6/REPIN-REL-0.1.0.sha256" 2>/dev/null | wc -l) (expect 0)"
} > "$L/repin-rel-hand-f6-refusal.txt" 2>&1

# 2. the positive: 18 files, the operator's check 18 OK, the filled script = the template but the four values
{
  head "the positive: fill_release.sh writes the filled script and the 18-file list; the operator's check"
  mkdir -p "$SP/pos"
  bash "$B/fill_release.sh" "$C" "$REL" "$SP/pos/REPIN-COMMANDS-REL-0.1.0.sh"; echo "fill exit $?"
  echo "-- the operator's check (sha256sum -c):"
  sha256sum -c "$SP/pos/REPIN-REL-0.1.0.sha256"; echo "check exit $?, $(wc -l < "$SP/pos/REPIN-REL-0.1.0.sha256") lines"
  m() { sed 's/^\(C\|EPOCH\|SHA\|RECORD\)=[^ ]*/\1=__FILLED__/' "$1"; }
  if diff <(m "$SP/pos/REPIN-COMMANDS-REL-0.1.0.sh") <(m "$B/REPIN-COMMANDS-REL.template.sh") > /dev/null; then
    echo "the filled script differs from the template in the four value lines only:"; grep -E '^(C|EPOCH|SHA|RECORD)=' "$SP/pos/REPIN-COMMANDS-REL-0.1.0.sh" | cut -c1-40
  else echo "the filled script differs from the template BEYOND the four values"; fi
  echo "run f7's own values: $(grep -E '^(C|EPOCH|SHA|RECORD)=' /tmp/gov-os-rel-repin/run-f7/REPIN-COMMANDS-REL-0.1.0.sh | cut -d' ' -f1 | cut -c1-30 | tr '\n' ' ')"
} > "$L/repin-rel-hand-fill-positive.txt" 2>&1

# 3. a byte changed in one of the five new files -> the operator's check fails (the real file untouched)
{
  head "a changed byte in one of the 5 files part B also runs: the operator's check stops the line"
  mkdir -p "$SP/byte"; cp -p "$O/drafts/g14/test_g14.py" "$SP/byte/test_g14.py"; printf ' ' >> "$SP/byte/test_g14.py"
  sed "s#  $O/drafts/g14/test_g14.py\$#  $SP/byte/test_g14.py#" "$SP/pos/REPIN-REL-0.1.0.sha256" > "$SP/byte/list.sha256"
  echo "-- the list of the positive, with test_g14.py's line naming a copy with one byte added (its hash: the real file's):"
  diff "$SP/pos/REPIN-REL-0.1.0.sha256" "$SP/byte/list.sha256" | sed -E 's/^([<>] [0-9a-f]{12})[0-9a-f]+ /\1… /'
  echo "-- the operator's line: sha256sum -c <list> && bash <script>"
  sha256sum -c --quiet "$SP/byte/list.sha256" && echo "WOULD RUN THE SCRIPT"; echo "line exit $?"
  echo "the real test_g14.py unchanged: $(sha256sum < "$O/drafts/g14/test_g14.py" | cut -c1-12) = $(grep 'drafts/g14/test_g14.py$' "$SP/pos/REPIN-REL-0.1.0.sha256" | cut -c1-12)"
} > "$L/repin-rel-hand-changed-byte.txt" 2>&1

# 4. a file of the list that cannot be read -> fill_release.sh refuses, writes neither the script nor the list
{
  head "an unreadable file of the list: fill_release.sh refuses, nothing written"
  mkdir -p "$SP/unread/b" "$SP/unread/root"; cp -p "$B"/*.sh "$B"/*.py "$B"/*.md "$SP/unread/b/"
  sed -i "s#^R=$R\$#R=$SP/unread/root#" "$SP/unread/b/fill_release.sh"
  echo "-- a copy of the bundle whose hash-list root is an empty folder: $(grep -n '^R=' "$SP/unread/b/fill_release.sh" | cut -c1-12)…; its BUNDLE.sha256 rewritten for the copy"
  (cd "$SP/unread/b" && sha256sum REPIN-COMMANDS-REL.template.sh fill_release.sh rel_checks.sh rel_registry.py rehearse_rel.sh README.md NOTES.md > BUNDLE.sha256)
  bash "$SP/unread/b/fill_release.sh" "$C" "$REL" "$SP/unread/out.sh" 2>&1 | tail -2; echo "exit ${PIPESTATUS[0]}"
  echo "files written: $(ls "$SP/unread/out.sh" "$SP/unread/out.sh.tmp" "$SP/unread/REPIN-REL-0.1.0.sha256" "$SP/unread/REPIN-REL-0.1.0.sha256.tmp" 2>/dev/null | wc -l) (expect 0)"
} > "$L/repin-rel-hand-unreadable.txt" 2>&1
for f in f6-refusal fill-positive changed-byte unreadable; do echo "--- $f"; tail -3 "$L/repin-rel-hand-$f.txt" | cut -c1-200; done
