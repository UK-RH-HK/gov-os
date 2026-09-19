#!/usr/bin/env bash
# P2-AR-0029 — the four ingress/floor properties and the OWNER-DECISION-0006 §5 allow-list, measured structurally on
# this worktree against the base commit (the behavioural measurements are the R1 held-out suites and srr.rs /
# section6.rs; this script records the source-level invariants they rest on).
# Usage: r1-invariants.sh <base-commit>   (prints to stdout)
set -u
BASE="${1:?base}"
cd "$(dirname "${BASH_SOURCE[0]}")/../../../../.." || exit 1
src() { git ls-files runtime/src cli/src | grep '\.rs$'; }
code() { for f in $(src); do awk -v f="$f" '/#\[cfg\(test\)\]/{exit} {print f": "$0}' "$f"; done | sed 's#//.*##'; }
echo "# HEAD $(git rev-parse HEAD); base $BASE"
echo "## P1 every privileged ingress calls the one verifier; only admit constructs the typed value"
echo "srr::admit( call sites (expect 5): $(code | grep -c 'srr::admit(')"
code | grep 'srr::admit(' | cut -d: -f1 | sort | uniq -c
echo "install_kernel( call sites (expect 5): $(code | grep -E 'install_kernel\(&|install_kernel\(a,' | grep -vc 'fn install_kernel')"
echo "by_admit( call sites (expect 1 + the fn): $(code | grep -c 'by_admit(')"
echo "AuthenticatedRelease { literals outside verifier.rs (expect 0): $(code | grep 'AuthenticatedRelease {' | grep -v 'runtime/src/srr/verifier.rs' | grep -vc 'pub struct')"
echo "## P2 the floor check binds every ingress (is_backward_capable / floor code unchanged)"
for fn in is_backward_capable may_use_protected_installed_record; do
  a=$(git show "$BASE":runtime/src/srr/verifier.rs | awk "/fn $fn/,/^    }/" | sha256sum | cut -c1-16)
  b=$(awk "/fn $fn/,/^    }/" runtime/src/srr/verifier.rs | sha256sum | cut -c1-16)
  echo "verifier::$fn byte-identical to base: $([ "$a" = "$b" ] && echo yes || echo NO)"
done
a=$(git show "$BASE":runtime/src/srr/verifier.rs | sed -n '/(9) THE FLOOR CHECK/,/^    Ok(AuthenticatedRelease {/p' | sha256sum | cut -c1-16)
b=$(sed -n '/(9) THE FLOOR CHECK/,/^    Ok(AuthenticatedRelease {/p' runtime/src/srr/verifier.rs | sha256sum | cut -c1-16)
echo "admit_inner floor-check + break-glass block (step 9-10) byte-identical to base: $([ "$a" = "$b" ] && echo yes || echo NO)"
echo "effective_floor_sequence() occurrences (expect <= 4): $(code | grep -o 'effective_floor_sequence()' | wc -l)"
echo "## P3 break-glass relaxes the floor only, never authenticity"
echo "SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE present in admit_inner: $(grep -c SRR_BREAK_GLASS_REQUIRES_AUTHENTIC_RELEASE runtime/src/srr/verifier.rs)"
echo "## P4 floors monotonic, raised only from authenticated observations; no new floor writer"
echo "files changed vs base under srr/ that hold Floors/breakglass/state code: $(git diff --name-only "$BASE" -- runtime/src/srr/breakglass.rs runtime/src/srr/state.rs runtime/src/srr/metadata.rs runtime/src/srr/crypto.rs runtime/src/srr/provision.rs | wc -l) (expect 0)"
echo "floors_path( / join(\"floors\") outside state.rs, excluding breakglass::SECTION_6_SIGNATURES (a marker table, not a writer) (expect 0): $(code | grep -E 'floors_path\(|join\("floors"\)' | grep -v 'runtime/src/srr/state.rs' | grep -vc '&\["floors_path(')"
echo "## §5 allow-list (OWNER-DECISION-0006 §5) — breakglass.rs PERMITTED_OPERATIONS"
git diff --stat "$BASE" -- runtime/src/srr/breakglass.rs | tail -1; echo "(empty line above = breakglass.rs byte-identical to base)"
sed -n '/^pub const PERMITTED_OPERATIONS/,/^];/p' runtime/src/srr/breakglass.rs
echo "## D-0007 separation: kernel_trust.rs free of SRR verdict vocabulary"
for w in srr::admit AuthenticatedRelease Authenticity breakglass below_floor Floors; do echo "  $w: $(grep -c "$w" runtime/src/kernel_trust.rs)"; done
echo "## no signing capability"
echo "SigningKey / ed25519_dalek::Signer in product source (expect 0): $(code | grep -cE 'SigningKey|ed25519_dalek::Signer')"
echo "## OWNER-DECISION-0007 §1 / SRR2-R1-C1 owner-closed functions byte-identical"
for fn in resolve_state_root default_state_root; do
  a=$(git show "$BASE":runtime/src/srr/state.rs | awk "/fn $fn\(/,/^}/" | sha256sum | cut -c1-16); b=$(awk "/fn $fn\(/,/^}/" runtime/src/srr/state.rs | sha256sum | cut -c1-16)
  echo "state::$fn identical: $([ "$a" = "$b" ] && echo yes || echo NO)"
done
