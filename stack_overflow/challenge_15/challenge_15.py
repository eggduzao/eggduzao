# SPDX-License-Identifier: MIT
# challenge15.py
"""
StackOverflow Challenges | Alien Dictionary
===========================================

Compute a valid symbol ordering (an "alphabet") from an *alien dictionary*-a list of
words already sorted according to some unknown lexicographic order.

This module provides a robust, production-friendly implementation based on a
seed-aware variant of **Kahn's topological sorting algorithm**. It extracts the
minimal precedence constraints implied by the sorted word list and returns one
valid ordering of all symbols observed in the input.

Overview
--------
Given a list of words sorted in an unknown alphabet, we can infer ordering
constraints by comparing each pair of *adjacent* words:

- Find the first position where two adjacent words differ.
- If word₁ has symbol `a` and word₂ has symbol `b` at that position, then we must
  have `a -> b` (meaning `a` comes before `b`).
- Only the *first* differing position matters-everything after it is unconstrained
  by lexicographic comparison.
- Additionally, the dictionary is **invalid** if a longer word appears before its
  exact prefix (e.g., `"abcd"` before `"ab"`). In that case, no ordering can
  satisfy the given sorting.

All inferred constraints form a directed graph over symbols. Any valid alphabet
corresponds to a **topological ordering** of that graph.

Algorithm
---------
This implementation uses a seed-aware Kahn's algorithm:

1. **Initialize vertices**
   Collect every distinct symbol that appears anywhere in the input. This ensures
   the result includes symbols even if they have no edges.

2. **Build edges from adjacent words**
   For each consecutive pair `(w1, w2)`, locate the first differing symbol
   `(c1, c2)` and add a directed edge `c1 -> c2`. Maintain indegree counts.

3. **Topological sort (Kahn)**
   Start with all symbols whose indegree is zero. Repeatedly remove one such
   symbol, append it to the output, and decrement the indegree of its outgoing
   neighbors. When a neighbor reaches indegree zero, enqueue it.

4. **Cycle detection**
   If we cannot output all symbols (i.e., output length < number of symbols),
   the constraints contain a cycle and there is no valid ordering.

Seed-aware behavior
-------------------
Topological sorting is not necessarily unique. When multiple symbols are eligible
(indegree zero), this implementation can be made deterministic by seeding the
selection order (e.g., sorting candidates or using a stable tie-break rule).
A deterministic tie-break makes results reproducible across runs, which is often
useful for testing and for downstream pipelines.

Complexity
----------
Let:

- `C` be the total number of characters across all words (including duplicates),
- `V` be the number of unique symbols (vertices),
- `E` be the number of precedence constraints (edges).

Then:

- Building the symbol set is **O(C)**.
- Building constraints from adjacent words is **O(C)** in total, because each
  character position is inspected at most a constant number of times across the
  adjacent comparisons.
- Kahn's algorithm runs in **O(V + E)**.

Overall time complexity: **O(C + V + E)**.

Space complexity is **O(V + E)** for the adjacency representation and indegree
map (the input words dominate separately as **O(C)**).

API
---
- ``alien_order_robust(words: list[str]) -> list[str] | None``

  Returns a valid ordering as a list of symbols (strings of length 1), or ``None``
  if the dictionary is inconsistent.

Examples
--------
Minimal usage (in Python):

>>> words = ["wrt", "wrf", "er", "ett", "rftt"]
>>> order = alien_order_robust(words)
>>> order is not None
True
>>> "".join(order)  # one valid answer
'wertf'

Invalid prefix case:

>>> alien_order_robust(["abcd", "ab"]) is None
True

Cycle / contradiction:

>>> alien_order_robust(["z", "x", "z"]) is None
True

Command-line usage (typical pattern)
------------------------------------
Assuming you expose a CLI entry point that:
1) reads one word per line from a file, and
2) prints the discovered alphabet as a single line,

you might run:

$ python -m xxxxx.xxxxx.alien_dictionary input.txt
$ python xxxxx/xxxxx/alien_dictionary.py input.txt
$ python xxxxx/xxxxx/alien_dictionary.py input.txt -o out.txt

Input format example (input.txt):

wrt
wrf
er
ett
rftt

Output (one possible):

wertf

Notes
-----
- This solver is Unicode-safe at the symbol level: Python ``str`` elements are
  Unicode code points. If your "symbols" are multi-codepoint graphemes, you
  should pre-tokenize accordingly.
- Determinism is optional. If you need a stable order when ties occur, apply a
  deterministic policy (e.g., sorting the zero-indegree queue).

Metadata
--------
- Project: StackOverflow Challenges
- License: MIT
"""

# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

import argparse
import sys
from collections import defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence, DefaultDict


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
# Common "invisible" troublemakers you may want to treat explicitly.
_BOMS: Final[tuple[str, ...]] = (
    "\ufeff",  # UTF-8 BOM *as decoded text*, also used in UTF-16/32 decoded contexts
)

_LINE_SEPARATORS: Final[tuple[str, ...]] = (
    "\r\n", "\n", "\r",          # usual
    "\u2028", "\u2029",          # Unicode line/paragraph separators
)


# -------------------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------------------
def _as_path(value: str) -> Path:
    return Path(value).expanduser()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="challenge15",
        description="Alien Dictionary solver (robust I/O + ordering).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument("--version", action="version", version="0.1.1")

    p.add_argument(
        "input_path",
        type=_as_path,
        metavar="PATH",
        help="Input file containing the dictionary words (one per line).",
    )

    p.add_argument(
        "-o",
        "--output-path",
        dest="output_path",
        type=_as_path,
        default=None,
        metavar="PATH",
        help="Optional output path for the ordered alphabet.",
    )

    return p


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
@dataclass(slots=True)
class ReadStats:
    encoding_used: str
    total_lines: int
    kept_lines: int
    skipped_empty_or_ws: int
    unique_symbols: set[str]


def _normalize_line(line: str) -> str:
    """
    Normalize a raw line into a comparable form without changing its symbols.
    - Removes BOM if present at the beginning.
    - Removes only newline-like terminators (keeps leading/trailing spaces).
    """
    if not line:
        return ""

    # Remove BOM only at the beginning
    for bom in _BOMS:
        if line.startswith(bom):
            line = line.removeprefix(bom)
            break

    # Usually unnecessary if we used splitlines(), but safe if called elsewhere
    for sep in _LINE_SEPARATORS:
        if line.endswith(sep):
            line = line[: -len(sep)]

    return line


def _read_words_robust(path: Path | None) -> tuple[list[str], ReadStats]:
    """
    Read a dictionary file (one word per line), returning a list[str] words.

    Design goals:
    - Unicode-safe, best-effort decode.
    - Preserve meaningful spaces inside words (we only drop empty/whitespace-only lines).
    - Do not invent a C matrix or pad anything; Part 3 should work from Python strings.
    """
    if not isinstance(path, Path):
        raise TypeError("read_words_robust(path): path must be a pathlib.Path")
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"Expected a file, got: {path}")

    data = path.read_bytes()

    # Prefer encodings that commonly appear in real-world text files.
    # Note: 'utf-8-sig' strips BOM cleanly for UTF-8.
    candidates: tuple[str, ...] = (
        "utf-8-sig",
        "utf-8",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
        "utf-32",
        "utf-32-le",
        "utf-32-be",
        "latin-1",  # last resort, lossless byte mapping
    )

    text: str | None = None
    encoding_used = "utf-8"

    for enc in candidates:
        try:
            text = data.decode(enc, errors="strict")
            encoding_used = enc
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        # Absolute fallback: preserve shape even if some chars are undecodable
        text = data.decode("utf-8", errors="replace")
        encoding_used = "utf-8(replace)"

    raw_lines = text.splitlines()  # handles \n, \r\n, \r, and Unicode separators
    words: list[str] = []

    unique_symbols: set[str] = set()
    skipped = 0

    for raw in raw_lines:
        line = _normalize_line(raw)

        # Skip empty or whitespace-only lines
        if not line or line.isspace():
            skipped += 1
            continue

        words.append(line)
        unique_symbols.update(line)

    stats = ReadStats(
        encoding_used=encoding_used,
        total_lines=len(raw_lines),
        kept_lines=len(words),
        skipped_empty_or_ws=skipped,
        unique_symbols=unique_symbols,
    )
    return words, stats


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def alien_order_robust(words: list[str]) -> list[str] | None:
    """
    Derive a valid ordering of symbols given a sorted alien dictionary.

    Returns
    -------
    list[str] | None
        - list[str]: one valid topological ordering of all symbols encountered
        - None: if the input implies a contradiction (cycle) or invalid prefix rule
    """
    if not words:
        return []

    # 1) Collect all unique symbols with indegree initialized to 0
    in_degree: dict[str, int] = {}
    for w in words:
        for ch in w:
            in_degree.setdefault(ch, 0)

    # 2) Build directed edges from adjacent word pairs
    adj: DefaultDict[str, set[str]] = defaultdict(set)

    for w1, w2 in zip(words, words[1:]):
        # Invalid prefix case: longer word before its exact prefix
        if len(w1) > len(w2) and w1.startswith(w2):
            return None

        # Find first differing character and add constraint
        for c1, c2 in zip(w1, w2):
            if c1 != c2:
                if c2 not in adj[c1]:
                    adj[c1].add(c2)
                    in_degree[c2] += 1
                break
        # If no break happens, either w1==w2 or one is prefix of the other (valid)

    # 3) Kahn's algorithm (BFS)
    q: deque[str] = deque([ch for ch, deg in in_degree.items() if deg == 0])
    order: list[str] = []

    while q:
        ch = q.popleft()
        order.append(ch)

        for nb in adj.get(ch, ()):
            in_degree[nb] -= 1
            if in_degree[nb] == 0:
                q.append(nb)

    # 4) Cycle detection
    if len(order) != len(in_degree):
        return None

    return order


def main(argv: Sequence[str] | None = None) -> int:
    """
    """
    # Part 1 - Reading arguments
    argv = sys.argv[1:] if argv is None else list(argv)
    args = _build_parser().parse_args(argv)

    # Part 2 - Treating data
    words, stats = _read_words_robust(args.input_path)

    # Part 3 - Performing Alien Dictionary Ordering
    order: list[str] = alien_order_robust(words)

    if args.output_path is None:
        # print to stdout
        sys.stdout.write("".join(order) + "\n")
    else:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text("".join(order) + "\n", encoding="utf-8")

    return 0


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "main",
]


# -------------------------------------------------------------------------------------
# Test | python challenge_15.py input-utf8.txt > out.txt 2>&1
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(main())
