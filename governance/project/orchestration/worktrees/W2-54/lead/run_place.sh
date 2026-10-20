#!/bin/sh
# Where the models sit: both servers' /api/ps, the GPU memory and the Ollama processes. $1 names the output file.
{
  date +%T
  uptime
  echo "shared 11434:"; curl -s --noproxy '*' http://127.0.0.1:11434/api/ps; echo
  echo "cpu 11435:"; curl -s --noproxy '*' http://127.0.0.1:11435/api/ps; echo
  nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
  ps -eo pid,rss,etime,args | grep -E "ollama (serve|runner)|llama-server" | grep -v grep | cut -c1-160
} > "$1" 2>&1
