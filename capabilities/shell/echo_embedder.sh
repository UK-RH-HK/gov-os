#!/usr/bin/env bash
# gov-capability/1 protocol proof in a non-Python language: a deterministic "embedder" written in bash.
# Entry i of each vector is ((cksum of text) + i) mod 7 / 6. Not a real embedder; it proves the plugin host is
# language-neutral. One external process (cksum) per text; everything else is shell arithmetic.
REQ=$(cat)
case "$REQ" in *'"protocol"'*'"gov-capability/1"'*) ;; *)
  printf '{"protocol":"gov-capability/1","ok":false,"provider":{"id":"echo-embedder-sh","version":"1"},"error":{"code":"PROTOCOL_MISMATCH","message":"bad protocol"}}'; exit 0;;
esac
dim=$(printf '%s' "$REQ" | sed -n 's/.*"dimensions"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p'); dim=${dim:-8}
texts=$(printf '%s' "$REQ" | sed -n 's/.*"texts"[[:space:]]*:[[:space:]]*\[\(.*\)\].*/\1/p')
# split on the JSON string delimiters `","` after trimming the outer quotes; escaped quotes are irrelevant for the checksum
texts=${texts#\"}; texts=${texts%\"}
vectors=""
IFS=$'\x1f'
while IFS= read -r -d $'\x1e' t || [ -n "$t" ]; do
  sum=$(printf '%s' "$t" | cksum); sum=${sum%% *}
  v=""
  for ((i=0; i<dim; i++)); do
    val=$(( (sum + i) % 7 )); scaled=$(( val * 1000000 / 6 ))
    printf -v entry '%d.%06d' $(( scaled / 1000000 )) $(( scaled % 1000000 ))
    v+="$entry,"
  done
  vectors+="[${v%,}],"
done < <(printf '%s' "$texts" | sed 's/"[[:space:]]*,[[:space:]]*"/\x1e/g'; printf '\x1e')
printf '{"protocol":"gov-capability/1","ok":true,"provider":{"id":"echo-embedder-sh","version":"1"},"outputs":{"vectors":[%s],"dim":%s}}' "${vectors%,}" "$dim"
