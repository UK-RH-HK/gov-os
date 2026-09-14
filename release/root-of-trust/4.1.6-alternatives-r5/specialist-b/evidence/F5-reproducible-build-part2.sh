#!/bin/bash
# AR-0010 reproducibility probe, part 2: vary CARGO_HOME location too (independent rebuilder with its own registry copy).
set -u
S=${1:?scratch}; RH=/home/usain/.rustup; LOG=$S/out/LOG.txt
log(){ echo "$(date -u +%FT%TZ) $*" >> $LOG; }
for H in cargo-home-rebuilder3 other/root/cargo-home-rebuilder4; do [ -d $S/$H/registry ] || { mkdir -p $S/$H && cp -r /home/usain/.cargo/registry $S/$H/registry; }; done
build(){ local name=$1 dir=$2 ch=$3 flags=$4
  mkdir -p $dir && tar -x -f $S/out/source.tar -C $dir
  local t0=$(date +%s)
  env -i PATH=/home/usain/.cargo/bin:/usr/bin:/bin HOME=$S/home CARGO_HOME=$ch RUSTUP_HOME=$RH SOURCE_DATE_EPOCH=1700000000 RUSTFLAGS="$flags" CARGO_INCREMENTAL=0 \
      bash -c "cd $dir && cargo build --release --offline --locked" > $S/out/build-$name.log 2>&1
  local rc=$?; local d=$(sha256sum $dir/target/release/gov 2>/dev/null | cut -d' ' -f1)
  log "build $name rc=$rc seconds=$(( $(date +%s) - t0 )) cargo_home_len=${#ch} rustflags='$flags' sha256=$d"
  echo "$name $rc $d" >> $S/out/digests.txt
  strings -n 8 $dir/target/release/gov | grep -c -E '/tmp/claude|/home/usain|cargo-home' > $S/out/pathstrings-$name.txt
}
build C_plain_otherhome $S/rb3/src $S/cargo-home-rebuilder3 ""
build D_plain_otherhome2 $S/x/y/z/rb4/src $S/other/root/cargo-home-rebuilder4 ""
build C_remap_otherhome $S/rb5/src $S/cargo-home-rebuilder3 "--remap-path-prefix=$S/rb5/src=/build/src --remap-path-prefix=$S/cargo-home-rebuilder3=/build/cargo --remap-path-prefix=$RH=/build/rustup"
build D_remap_otherhome2 $S/x/y/z/rb6/src $S/other/root/cargo-home-rebuilder4 "--remap-path-prefix=$S/x/y/z/rb6/src=/build/src --remap-path-prefix=$S/other/root/cargo-home-rebuilder4=/build/cargo --remap-path-prefix=$RH=/build/rustup"
for f in rbA/src rebuilder-two/deeper/path/src; do strings -n 8 $S/$f/target/release/gov | grep -c -E '/tmp/claude|/home/usain|cargo-home' >> $S/out/pathstrings-part1.txt; done
log DONE2
