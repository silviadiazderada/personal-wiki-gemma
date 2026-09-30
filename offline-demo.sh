#!/usr/bin/env bash
# Offline demonstration: run with the internet disconnected.
# Every `wiki` call below is a fresh process, so the CLI is restarted for each step.
# The full terminal output is saved to evidence/offline-run/transcript.txt.
set -u
cd "$(dirname "$0")"
source .venv/bin/activate
export COLUMNS=120
OUT=evidence/offline-run
mkdir -p "$OUT"

{
  echo "# Offline demonstration transcript ($(date '+%Y-%m-%d %H:%M %Z'))"
  echo
  for cmd in \
    'wiki --help' \
    'wiki status' \
    'wiki ingest vault/raw/POLECON156_Week4_Reflection.pptx --force' \
    'wiki eval --label offline' \
    'wiki search "Stanford land lease" -k 3 --save' \
    'wiki ask "Where did students have to upload their Week 2 reflection?" --save'
  do
    echo "\$ $cmd"
    eval "$cmd"
    echo
  done
} 2>&1 | tee "$OUT/transcript.txt"

echo
echo "Done. Saved $OUT/transcript.txt — you can turn Wi-Fi back on."
