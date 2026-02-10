#!/bin/bash
# Create Alien Dictionaries given known answers
# to test algorithm solution

echo "✨ Running Switcheroo ✨"
# python switcheroo.py /Users/egg/Desktop/Polars polars apollo --dry-run > apollo_polars.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Polars polars apollo > apollo_polars_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Pytorch pytorch blacksmith --dry-run > blacksmith_pytorch.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Pytorch pytorch blacksmith > blacksmith_pytorch_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Fanc fanc bloom --dry-run > bloom_fanc.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Fanc fanc bloom > bloom_fanc_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Pysam pysam calibre --dry-run > calibre_pysam.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Pysam pysam calibre > calibre_pysam_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Biopython biopython fabric --dry-run > fabric_biopython.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Biopython biopython fabric > fabric_biopython_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Scipy scipy musique --dry-run > musique_scipy.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Scipy scipy musique > musique_scipy_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Jax jax olympus --dry-run > olympus_jax.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Jax jax olympus > olympus_jax_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Fabric fabric wildlife --dry-run  > wildlife_fabric.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Fabric fabric wildlife  > wildlife_fabric_run.txt 2>&1

# python switcheroo.py /Users/egg/Desktop/Calibre calibre fabric --dry-run > fabric_calibre.txt 2>&1
# python switcheroo.py /Users/egg/Desktop/Calibre calibre fabric > fabric_calibre_run.txt 2>&1

# Apolo
# Musique
# Olympus
# Bloom
# Wildlife - Biopython
# Fabric - Pysam
# Blacksmith
# Apollo

#!/usr/bin/env bash
set -euo pipefail

echo "✨ Running cleanup routine ✨"

ROOT_LOC="/Users/egg/Desktop"
PROJ_LOC="/Users/egg/projects"

SRC="${ROOT_LOC}/Apollo"
DST="${PROJ_LOC}/Apollo"
LEGACY="${DST}/_legacy"
PROCS="${DST}/_procedures"

# --- sanity checks ---
if [[ ! -d "$SRC" ]]; then
  echo "ERROR: source dir not found: $SRC" >&2
  exit 1
fi
if [[ ! -d "$DST" ]]; then
  echo "ERROR: destination repo dir not found: $DST" >&2
  exit 1
fi

mkdir -p "$LEGACY" "$PROCS"

# 1) Move selected *apollo*.txt into _procedures/ (if any exist)
shopt -s nullglob dotglob

apollo_txt=( "$SRC"/*apollo*.txt )
if (( ${#apollo_txt[@]} > 0 )); then
  mv -v "${apollo_txt[@]}" "$PROCS/"
else
  echo "INFO: no *apollo*.txt found in $SRC"
fi

# 1b) Move everything else into _legacy/, excluding .git and excluding the folders we just created
# NOTE: if SRC has .git, we keep it in place (don't move it).
items=( "$SRC"/* "$SRC"/.* )
for p in "${items[@]}"; do
  name="$(basename "$p")"
  case "$name" in
    "."|".."|".git") continue ;;
  esac

  # If user accidentally created _legacy/_procedures in SRC, don't move them (avoid recursion).
  if [[ "$p" == "$SRC/_legacy" || "$p" == "$SRC/_procedures" ]]; then
    continue
  fi

  mv -v "$p" "$LEGACY/"
done

# 2) Copy clean.sh into repo (overwrite), then run it from repo root
if [[ ! -f "${PROJ_LOC}/Organization/clean.sh" ]]; then
  echo "ERROR: clean.sh not found at ${PROJ_LOC}/Organization/clean.sh" >&2
  exit 1
fi

cp -f "${PROJ_LOC}/Organization/clean.sh" "${DST}/clean.sh"
cd "$DST"
bash "./clean.sh"

# 3) git "dry-run" equivalents
git status
echo
echo "INFO: git add --all (dry-run):"
git add --all --dry-run || true
echo
echo "INFO: what would be committed:"
git diff --cached --stat || true

# 4) Add/commit/push (only if there are staged changes)
git add --all
if git diff --cached --quiet; then
  echo "INFO: nothing to commit."
  exit 0
fi

git commit -m "chore: cleaning for private status"
git push

echo "✅ Everything Done Under the Sun."
