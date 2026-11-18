#!/bin/sh
# The scripts were written for one flat working directory (scripts, data and coding side by side).
# This rebuilds that layout in ./work without touching the published files.
set -e
mkdir -p work
cp scripts/*.py data/* protocol/coder_instructions.md work/
cp -R coding work/coding
echo "work/ ready: cd work && python3 agreement.py   (no network, no model calls)"
