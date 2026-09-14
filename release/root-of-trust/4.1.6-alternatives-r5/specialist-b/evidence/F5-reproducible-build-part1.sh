#!/bin/bash
# AR-0010 reproducibility probe: can two independent rebuilders obtain bit-identical `gov` binaries from the same source?
# Scratch only. env -i; no GOV_*; CARGO_HOME copied into scratch; toolchain read-only from RUSTUP_HOME.
set -u
WT=${1:?worktree}; S=${2:?scratch}
RH=/home/usain/.rustup
mkdir -p $S/home $S/out
if [ ! -d $S/cargo-home/registry ]; then mkdir -p $S/cargo-home && cp -r /home/usain/.cargo/registry $S/cargo-home/registry; fi
LOG=$S/out/LOG.txt
log(){ echo "$(date -u +%FT%TZ) $*" >> $LOG; }
git -C $WT archive --format=tar HEAD > $S/out/source.tar
SRC_DIGEST=$(sha256sum $S/out/source.tar | cut -d' ' -f1)
log "source_tree_digest sha256:$SRC_DIGEST commit $(git -C $WT rev-parse HEAD)"
build(){ # name dir rustflags
  local name=$1 dir=$2 flags=$3
  mkdir -p $dir && tar -x -f $S/out/source.tar -C $dir
  local t0=$(date +%s)
  env -i PATH=/home/usain/.cargo/bin:/usr/bin:/bin HOME=$S/home CARGO_HOME=$S/cargo-home RUSTUP_HOME=$RH \
      SOURCE_DATE_EPOCH=1700000000 RUSTFLAGS="$flags" CARGO_INCREMENTAL=0 \
      bash -c "cd $dir && cargo build --release --offline --locked" > $S/out/build-$name.log 2>&1
  local rc=$?
  local bin=$(ls $dir/target/release/gov 2>/dev/null)
  local d=$( [ -n "$bin" ] && sha256sum $bin | cut -d' ' -f1 )
  log "build $name rc=$rc seconds=$(( $(date +%s) - t0 )) dir_len=${#dir} rustflags='$flags' sha256=$d"
  echo "$name $rc $d" >> $S/out/digests.txt
}
build A_plain $S/rbA/src ""
build B_plain $S/rebuilder-two/deeper/path/src ""
build A_remap $S/rbA2/src "--remap-path-prefix=$S/rbA2/src=/build/src --remap-path-prefix=$S/cargo-home=/build/cargo --remap-path-prefix=$RH=/build/rustup"
build B_remap $S/rebuilder-two/deeper/path2/src "--remap-path-prefix=$S/rebuilder-two/deeper/path2/src=/build/src --remap-path-prefix=$S/cargo-home=/build/cargo --remap-path-prefix=$RH=/build/rustup"
log DONE
