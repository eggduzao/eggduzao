# SPDX-License-Identifier: MIT
# dictionary_mapper.py
"""
StackOverflow Challenges | Alien Dictionary | Mapper
====================================================

Usage:
    python mapper.py input_path.txt dictionary_path.txt output_path.txt

Example:

python mapper.py \
    './input/original-so.txt' \
    './dictionary/alien-so.txt' \
    './output/translation.txt'

Metadata
--------
- Project: StackOverflow Challenges
- License: MIT
"""


# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from pathlib import Path
import sys

# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def load_dictionary(dict_path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    with dict_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            src, dst = line.split("\t")
            mapping[src] = dst
    return mapping


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def map_file(
    input_path: Path,
    mapping: dict[str, str],
    output_path: Path,
) -> None:
    with input_path.open("r", encoding="utf-8") as fin, \
         output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            translated = "".join(mapping.get(ch, ch) for ch in line)
            fout.write(translated)

# -------------------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: python symbol_mapper.py <input> <dictionary> <output>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    dict_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    mapping = load_dictionary(dict_path)
    map_file(input_path, mapping, output_path)


# -------------------------------------------------------------------------------------
# Test | python challenge_15.py input-utf8.txt > out.txt 2>&1
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
