# SPDX-License-Identifier: MIT
# easy_dictionary_generator.py
"""
StackOverflow Challenges | Alien Dictionary | Easy Dictionary Generator
=======================================================================

Generate a synthetic "alien dictionary" (a list of words) whose implied character
ordering (via the classic Alien Dictionary constraints) is consistent with a
given target order.

The generator supports two main modes:

1) **Unique-order mode** (default):
   Produces a word list that enforces a *single* total order over all symbols
   (the exact order given in the input file). It does this by emitting a chain
   of pairwise constraints that force `s0 < s1 < s2 < ...`.

2) **Ambiguous-order mode** (optional):
   Produces a word list that leaves parts of the alphabet unconstrained (multiple
   valid topological sorts). Useful for testing "non-unique order" handling.

The resulting dictionary is already sorted in the "alien lexicographic order"
that corresponds to the target symbol order (i.e., it is valid input to an
Alien Dictionary solver).

Notes
-----
- This is a **test-data generator**, not a natural-language word generator.
  Words are programmatic but valid.
- UTF-8 is supported; symbols are treated as single Unicode codepoints.
- The generator is deterministic given `seed` and identical inputs.

Examples
--------
Minimal (read symbols, write 1000 words to stdout):

>>> python easy_dictionary_generator.py --input-path symbols.txt --input-words 1000

Write to file, unique-order enforced:

>>> python easy_dictionary_generator.py \
...   --input-path symbols.txt \
...   --output-path alien_words.txt \
...   --input-words 5000 \
...   --min-word-size 3 \
...   --max-word-size 12 \
...   --seed 42 \
...   --mode unique

Create an intentionally ambiguous dictionary (only enforce the chain for the
first 8 symbols; remaining symbols float):

>>> python easy_dictionary_generator.py \
...   --input-path symbols.txt \
...   --output-path alien_words_ambiguous.txt \
...   --input-words 2000 \
...   --mode ambiguous \
...   --enforce-prefix 8

See also
--------
This generator is designed to test an Alien Dictionary solver (topological sort
approach). It can also emit invalid dictionaries (prefix invalidity, cycles)
if you extend it (hooks provided).

Metadata
--------
- Project: StackOverflow Challenges
- License: MIT
"""


# -------------------------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import argparse
import random
import sys


# -------------------------------------------------------------------------------------
# Constants
# -------------------------------------------------------------------------------------
Mode = Literal["unique", "ambiguous"]


@dataclass(frozen=True)
class GeneratorConfig:
    """Configuration for the alien dictionary generator."""

    output: Path
    symbols: list[str]
    input_words: int
    min_word_size: int
    max_word_size: int
    seed: int | None
    mode: Mode
    enforce_prefix: int | None  # used in ambiguous mode: chain length to enforce
    filler_symbol: str | None   # optional explicit filler (defaults to first symbol)


# -------------------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------------------
def _read_symbols(path: Path) -> list[str]:
    """
    Read one symbol per line from a UTF-8 text file.

    Parameters
    ----------
    path : Path
        File containing one character per line (UTF-8).

    Returns
    -------
    list[str]
        Symbols in the intended alien order.

    Raises
    ------
    ValueError
        If file contains empty lines or duplicate symbols.
    """
    raw = path.read_text(encoding="utf-8").splitlines()
    symbols = [line.strip("\n\r") for line in raw if line.strip("\n\r") != ""]
    if not symbols:
        raise ValueError("Input symbol file is empty or only blank lines.")

    if any(len(s) != 1 for s in symbols):
        bad = next(s for s in symbols if len(s) != 1)
        raise ValueError(f"Each line must be exactly one character; got {bad!r}.")

    dup = {s for s in symbols if symbols.count(s) > 1}
    if dup:
        raise ValueError(f"Duplicate symbols found: {sorted(dup)!r}")

    return symbols


def _validate_config(cfg: GeneratorConfig) -> None:

    if cfg.input_words == 0:
        output_path: Path = Path(cfg.output)
        output_path.touch()
        sys.exit(0)
    if cfg.input_words < 0:
        raise ValueError("input_words must be >= 0")
    if cfg.max_word_size < cfg.min_word_size:
        raise ValueError("max_word_size must be >= min_word_size")
    if len(cfg.symbols) < 1:
        raise ValueError("Need at least one symbol")

    if cfg.mode == "ambiguous":
        if cfg.enforce_prefix is None:
            raise ValueError("ambiguous mode requires enforce_prefix")
        if cfg.enforce_prefix < 0:
            raise ValueError("enforce_prefix must be >= 0")
        if cfg.enforce_prefix > len(cfg.symbols):
            raise ValueError("enforce_prefix cannot exceed number of symbols")


def _mk_word(prefix: str, a: str, total_len: int, filler: str) -> str:
    """
    Create a word `prefix + a + filler...` of exact length `total_len`.
    """
    core = prefix + a
    if len(core) >= total_len:
        return core[:total_len]
    return core + (filler * (total_len - len(core)))


def _chain_words(symbols: list[str], *, filler: str, min_len: int) -> list[str]:
    """
    Construct a minimal set of words that enforce the total order of `symbols`.

    For each consecutive pair (si, s(i+1)) we emit two words that first differ at
    position 0: `si...` then `s(i+1)...`, enforcing si < s(i+1).
    """
    words: list[str] = []
    L = max(min_len, 2)
    for i in range(len(symbols) - 1):
        a = symbols[i]
        b = symbols[i + 1]
        words.append(_mk_word(prefix="", a=a, total_len=L, filler=filler))
        words.append(_mk_word(prefix="", a=b, total_len=L, filler=filler))
    if not words:
        # Only one symbol: still emit at least one word.
        words.append(_mk_word(prefix="", a=symbols[0], total_len=L, filler=filler))
    return words


def _make_random_word(
    rng: random.Random,
    symbols: list[str],
    *,
    min_len: int,
    max_len: int,
    filler: str,
) -> str:
    """
    Make a random word that is *consistent* with the symbol set.

    We bias toward using earlier symbols as fillers to keep ordering stable.
    """
    L = rng.randint(min_len, max_len)
    # First char: random
    first = rng.choice(symbols)
    # Remaining: mostly filler + a few randoms
    rest: list[str] = []
    for _ in range(L - 1):
        rest.append(filler if rng.random() < 0.75 else rng.choice(symbols))
    return first + "".join(rest)


# --------------------------------------------------------------------------------------
# Functions
# --------------------------------------------------------------------------------------
def _sort_by_alien_order(words: list[str], symbols: list[str]) -> list[str]:
    """
    Sort words by the alien lexicographic order defined by `symbols`.

    This ensures the output file is a valid "dictionary" in that alien order.
    """
    rank = {ch: i for i, ch in enumerate(symbols)}

    # We want prefix behavior: Python tuple comparison doesn't directly encode
    # prefix-shorter-first when one is prefix of the other unless lengths are compared.
    # Do it explicitly:
    def _cmp_key(w: str) -> tuple[tuple[int, ...], int]:
        return (tuple(rank[ch] for ch in w), len(w))

    return sorted(words, key=_cmp_key)


def generate_alien_dictionary(cfg: GeneratorConfig) -> list[str]:
    """
    Generate an alien dictionary word list based on configuration.

    Parameters
    ----------
    cfg : GeneratorConfig
        Generator configuration.

    Returns
    -------
    list[str]
        Generated dictionary (sorted by alien order).
    """
    _validate_config(cfg)

    rng = random.Random(cfg.seed)

    filler = cfg.filler_symbol or cfg.symbols[0]

    # Build the constraint backbone.
    if cfg.mode == "unique":
        backbone_symbols = cfg.symbols
    else:
        backbone_symbols = cfg.symbols[: cfg.enforce_prefix or 0]

    backbone = _chain_words(backbone_symbols or [cfg.symbols[0]], filler=filler, min_len=cfg.min_word_size)

    # Fill up to requested word count with random-ish words.
    words = list(backbone)
    while len(words) < cfg.input_words:
        words.append(
            _make_random_word(
                rng,
                cfg.symbols,
                min_len=cfg.min_word_size,
                max_len=cfg.max_word_size,
                filler=filler,
            )
        )

    # Sort into alien dictionary order
    return _sort_by_alien_order(words, cfg.symbols)


# -------------------------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------------------------
def _write_words(words: list[str], output_path: Path | None) -> None:
    text = "\n".join(words) + "\n"
    if output_path is None:
        sys.stdout.write(text)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")


def build_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Alien dictionary generator (test data)."
    )
    p.add_argument(
        "--input-path",
        type=Path,
        required=True,
        help="UTF-8 file: one symbol per line, in correct alien order."
    )
    p.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help="Output dictionary file (UTF-8). If omitted, prints to stdout."
    )
    p.add_argument(
        "--input-words",
        type=int,
        default=1000,
        help="Number of words to generate (>=0)."
    )
    p.add_argument(
        "--min-word-size",
        type=int,
        default=3,
        help="Minimum word length (>0)."
    )
    p.add_argument(
        "--max-word-size",
        type=int,
        default=10,
        help="Maximum word length (>=min-word-size)."
    )
    p.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed (>=0)."
    )
    p.add_argument(
        "--mode",
        choices=("unique", "ambiguous"),
        default="unique",
        help="unique=force total order; ambiguous=leave some unconstrained."
    )
    p.add_argument(
        "--enforce-prefix",
        type=int,
        default=None,
        help="In ambiguous mode: enforce chain only for first N symbols."
    )
    p.add_argument(
        "--filler-symbol",
        type=str,
        default=None,
        help="Optional filler symbol (single char). Defaults to the first symbol."
    )

    ns = p.parse_args(argv)

    symbols = _read_symbols(ns.input_path)

    filler_symbol = ns.filler_symbol
    if filler_symbol is not None:
        if len(filler_symbol) != 1:
            raise SystemExit("--filler-symbol must be exactly one character.")
        if filler_symbol not in symbols:
            raise SystemExit("--filler-symbol must be present in the input symbol list.")

    seed = None if ns.seed is None else int(ns.seed)

    cfg = GeneratorConfig(
        output=Path(ns.output_path),
        symbols=symbols,
        input_words=int(ns.input_words),
        min_word_size=int(ns.min_word_size),
        max_word_size=int(ns.max_word_size),
        seed=seed,
        mode=ns.mode,
        enforce_prefix=(
            int(ns.enforce_prefix) if ns.enforce_prefix is not None else None
        ),
        filler_symbol=filler_symbol,
    )

    words = generate_alien_dictionary(cfg)
    _write_words(words, ns.output_path)
    return 0


# --------------------------------------------------------------------------------------
# Exports
# --------------------------------------------------------------------------------------
__all__: list[str] = [
    "generate_alien_dictionary",
    "build_cli",
]


# -------------------------------------------------------------------------------------
# Test | python challenge_15.py input-utf8.txt > out.txt 2>&1
# -------------------------------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(build_cli())
