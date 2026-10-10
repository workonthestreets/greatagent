#!/usr/bin/env bash
# Fetch the organisers' public example cases into data/public-cases (gitignored).
set -euo pipefail
dest="${1:-data/public-cases}"
if [ -d "$dest/.git" ]; then git -C "$dest" pull -q; else git clone -q --depth 1 https://github.com/DwellyOrg/HackatonPublicCases "$dest"; fi
echo "cases in $dest"
