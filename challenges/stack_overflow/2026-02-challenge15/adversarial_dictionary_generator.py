# SPDX-License-Identifier: MIT
# alien_dictionary_generator.py
"""
StackOverflow Challenges | Alien Dictionary Generator
=====================================================

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

>>> python alien_dictionary_generator.py --input-path symbols.txt --input-words 1000

Write to file, unique-order enforced:

>>> python alien_dictionary_generator.py \
...   --input-path symbols.txt \
...   --output-path alien_words.txt \
...   --input-words 5000 \
...   --min-word-size 3 \
...   --max-word-size 12 \
...   --seed 42 \
...   --mode unique

Create an intentionally ambiguous dictionary (only enforce the chain for the
first 8 symbols; remaining symbols float):

>>> python alien_dictionary_generator.py \
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
# Adversarial additions (drop-in patch style)
# -------------------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
import argparse
import random
import sys


Mode = Literal["unique", "ambiguous", "adversarial"]


@dataclass(frozen=True)
class GeneratorConfig:
    output: Path
    symbols: list[str]
    input_words: int
    min_word_size: int
    max_word_size: int
    seed: int | None
    mode: Mode
    enforce_prefix: int | None
    filler_symbol: str | None

    # --- adversarial knobs ---
    # How deep the first-difference should occur (forces long prefix scans).
    # 0 => like classic (diff at position 0)
    # >=1 => diff near the end (expensive string compares in naive code)
    pain_prefix_len: int = 0

    # Number of clusters to split the alphabet into.
    # Within clusters you may enforce local chains; across clusters you keep edges sparse.
    clusters: int = 8

    # In adversarial mode: only enforce order for the first N symbols globally (rest ambiguous).
    enforce_global: int = 0

    # In adversarial mode: enforce local chains inside each cluster for first K symbols of that cluster.
    enforce_per_cluster: int = 0

    # Produce lots of “edge-barren” words (same first char, long filler tails) to inflate N without adding edges.
    noise_ratio: float = 0.85

    # How often to add a constraint word-pair between clusters (keeps inter-cluster edges very sparse).
    inter_cluster_pairs: int = 2


def _read_symbols(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8").splitlines()
    symbols = [line.strip("\n\r") for line in raw if line.strip("\n\r") != ""]
    if not symbols:
        raise ValueError("Input symbol file is empty or only blank lines.")
    if any(len(s) != 1 for s in symbols):
        bad = next(s for s in symbols if len(s) != 1)
        raise ValueError(f"Each line must be exactly one character; got {bad!r}.")
    if len(set(symbols)) != len(symbols):
        raise ValueError("Duplicate symbols found.")
    return symbols


def _validate_config(cfg: GeneratorConfig) -> None:
    if cfg.input_words == 0:
        Path(cfg.output).touch()
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

    if cfg.mode == "adversarial":
        if cfg.clusters <= 0:
            raise ValueError("clusters must be >= 1")
        if not (0.0 <= cfg.noise_ratio <= 1.0):
            raise ValueError("noise_ratio must be in [0,1]")
        if cfg.pain_prefix_len < 0:
            raise ValueError("pain_prefix_len must be >= 0")


def _sort_by_alien_order(words: list[str], symbols: list[str]) -> list[str]:
    rank = {ch: i for i, ch in enumerate(symbols)}

    # Key ensures prefix-shorter-first when one is prefix.
    def _cmp_key(w: str) -> tuple[tuple[int, ...], int]:
        return (tuple(rank[ch] for ch in w), len(w))

    return sorted(words, key=_cmp_key)


def _mk_word(prefix: str, a: str, total_len: int, filler: str) -> str:
    core = prefix + a
    if len(core) >= total_len:
        return core[:total_len]
    return core + (filler * (total_len - len(core)))


def _deep_diff_pair(
    *,
    a: str,
    b: str,
    filler: str,
    min_len: int,
    pain_prefix_len: int,
) -> tuple[str, str]:
    """
    Create two words whose first difference occurs *late* (after a long common prefix),
    enforcing a < b (since they differ at that position).
    """
    # Ensure the word is long enough to place the difference after pain_prefix_len.
    L = max(min_len, pain_prefix_len + 1)
    prefix = filler * pain_prefix_len
    w1 = _mk_word(prefix=prefix, a=a, total_len=L, filler=filler)
    w2 = _mk_word(prefix=prefix, a=b, total_len=L, filler=filler)
    return w1, w2


def _chain_words(
    symbols: list[str],
    *,
    filler: str,
    min_len: int,
    pain_prefix_len: int,
) -> list[str]:
    """
    Enforce a chain order over `symbols` using *deep* first-difference pairs.
    """
    if len(symbols) == 1:
        L = max(min_len, pain_prefix_len + 1)
        return [_mk_word(prefix=filler * pain_prefix_len, a=symbols[0], total_len=L, filler=filler)]

    words: list[str] = []
    for i in range(len(symbols) - 1):
        a = symbols[i]
        b = symbols[i + 1]
        w1, w2 = _deep_diff_pair(a=a, b=b, filler=filler, min_len=min_len, pain_prefix_len=pain_prefix_len)
        words.append(w1)
        words.append(w2)
    return words


def _partition(symbols: list[str], k: int) -> list[list[str]]:
    """
    Partition symbols into k contiguous clusters (preserves global order within each cluster).
    """
    n = len(symbols)
    k = min(k, n)
    base = n // k
    rem = n % k
    out: list[list[str]] = []
    start = 0
    for i in range(k):
        size = base + (1 if i < rem else 0)
        out.append(symbols[start : start + size])
        start += size
    return out


def _noise_word(
    rng: random.Random,
    *,
    symbols: list[str],
    filler: str,
    min_len: int,
    max_len: int,
    pain_prefix_len: int,
) -> str:
    """
    Create a word that tends to add *no new constraints*:
    - very long filler prefix
    - first char chosen from a small early subset (so many words share the same first symbol)
    - rest mostly filler
    """
    L = rng.randint(min_len, max_len)
    L = max(L, pain_prefix_len + 1)

    # Concentrate first symbol in early ranks -> many adjacent words share same first char.
    # This makes first-difference frequently happen deep (or not at all), reducing edge yield.
    head_pool = symbols[: max(2, min(16, len(symbols)))]
    first = rng.choice(head_pool)

    # Deep common prefix:
    prefix = filler * pain_prefix_len
    # Then some filler tail with very rare random spice:
    tail_len = max(0, L - len(prefix) - 1)
    tail = "".join(filler if rng.random() < 0.98 else rng.choice(symbols) for _ in range(tail_len))
    return prefix + first + tail


def _adversarial_backbone(cfg: GeneratorConfig, rng: random.Random, filler: str) -> list[str]:
    """
    Create a painful-but-valid backbone:
    - split symbols into clusters
    - enforce only local chains (optional) + few inter-cluster edges
    - deep first-difference (pain_prefix_len) makes comparisons expensive
    - leave most of the alphabet unconstrained (ambiguity + huge Kahn queue)
    """
    clusters = _partition(cfg.symbols, cfg.clusters)
    words: list[str] = []

    # 1) Optional tiny global chain for first `enforce_global` symbols.
    if cfg.enforce_global > 0:
        gsyms = cfg.symbols[: cfg.enforce_global]
        words.extend(_chain_words(gsyms, filler=filler, min_len=cfg.min_word_size, pain_prefix_len=cfg.pain_prefix_len))

    # 2) Local chains inside each cluster for first `enforce_per_cluster`.
    if cfg.enforce_per_cluster > 0:
        for cl in clusters:
            if not cl:
                continue
            local = cl[: cfg.enforce_per_cluster]
            if local:
                words.extend(_chain_words(local, filler=filler, min_len=cfg.min_word_size, pain_prefix_len=cfg.pain_prefix_len))

    # 3) Very sparse inter-cluster constraints (keeps graph “clustered”).
    # We pick just a few edges from last of cluster i to first of cluster i+1, deep difference.
    pairs = max(0, cfg.inter_cluster_pairs)
    if pairs > 0 and len(clusters) >= 2:
        for i in range(len(clusters) - 1):
            left = clusters[i]
            right = clusters[i + 1]
            if not left or not right:
                continue
            a = left[-1]
            b = right[0]
            for _ in range(pairs):
                w1, w2 = _deep_diff_pair(a=a, b=b, filler=filler, min_len=cfg.min_word_size, pain_prefix_len=cfg.pain_prefix_len)
                words.append(w1)
                words.append(w2)

    # Ensure we at least include *some* representative words for symbols so they appear as vertices.
    # (One per cluster is enough to introduce characters without forcing edges.)
    for cl in clusters:
        if not cl:
            continue
        ch = cl[len(cl) // 2]
        L = max(cfg.min_word_size, cfg.pain_prefix_len + 1)
        words.append(_mk_word(prefix=filler * cfg.pain_prefix_len, a=ch, total_len=L, filler=filler))

    return words


def generate_alien_dictionary(cfg: GeneratorConfig) -> list[str]:
    _validate_config(cfg)
    rng = random.Random(cfg.seed)
    filler = cfg.filler_symbol or cfg.symbols[0]

    if cfg.mode == "unique":
        backbone_symbols = cfg.symbols
        backbone = _chain_words(
            backbone_symbols or [cfg.symbols[0]],
            filler=filler,
            min_len=cfg.min_word_size,
            pain_prefix_len=0,
        )

    elif cfg.mode == "ambiguous":
        backbone_symbols = cfg.symbols[: (cfg.enforce_prefix or 0)]
        backbone = _chain_words(
            backbone_symbols or [cfg.symbols[0]],
            filler=filler,
            min_len=cfg.min_word_size,
            pain_prefix_len=0,
        )

    else:  # adversarial
        backbone = _adversarial_backbone(cfg, rng, filler)

    words = list(backbone)

    # Fill with mostly edge-barren noise to blow up N without making the graph easier.
    while len(words) < cfg.input_words:
        if cfg.mode == "adversarial" and rng.random() < cfg.noise_ratio:
            words.append(
                _noise_word(
                    rng,
                    symbols=cfg.symbols,
                    filler=filler,
                    min_len=cfg.min_word_size,
                    max_len=cfg.max_word_size,
                    pain_prefix_len=cfg.pain_prefix_len,
                )
            )
        else:
            # mild non-adversarial filler word
            L = rng.randint(cfg.min_word_size, cfg.max_word_size)
            w = "".join(rng.choice(cfg.symbols) for _ in range(L))
            words.append(w)

    return _sort_by_alien_order(words, cfg.symbols)


# -------------------------------------------------------------------------------------
# CLI patch for absurd pain management
# -------------------------------------------------------------------------------------
def build_cli(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Alien dictionary generator (test data).")
    p.add_argument("--input-path", type=Path, required=True, help="UTF-8 file: one symbol per line, in correct alien order.")
    p.add_argument("--output-path", type=Path, default=None, help="Output dictionary file (UTF-8). If omitted, prints to stdout.")
    p.add_argument("--input-words", type=int, default=1000)
    p.add_argument("--min-word-size", type=int, default=3)
    p.add_argument("--max-word-size", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--mode", choices=("unique", "ambiguous", "adversarial"), default="unique")
    p.add_argument("--enforce-prefix", type=int, default=None)
    p.add_argument("--filler-symbol", type=str, default=None)

    # adversarial knobs
    p.add_argument("--pain-prefix-len", type=int, default=64, help="Common-prefix length before first difference (deep comparisons).")
    p.add_argument("--clusters", type=int, default=16, help="Number of symbol clusters (graph becomes clustered partial order).")
    p.add_argument("--enforce-global", type=int, default=0, help="Enforce chain only for first N symbols globally (rest ambiguous).")
    p.add_argument("--enforce-per-cluster", type=int, default=8, help="Enforce chain for first K symbols inside each cluster.")
    p.add_argument("--noise-ratio", type=float, default=0.90, help="Fraction of filler words that add few edges.")
    p.add_argument("--inter-cluster-pairs", type=int, default=1, help="How many deep-diff pairs per adjacent cluster boundary.")

    ns = p.parse_args(argv)
    symbols = _read_symbols(ns.input_path)

    filler_symbol = ns.filler_symbol
    if filler_symbol is not None:
        if len(filler_symbol) != 1:
            raise SystemExit("--filler-symbol must be exactly one character.")
        if filler_symbol not in symbols:
            raise SystemExit("--filler-symbol must be present in the input symbol list.")

    cfg = GeneratorConfig(
        output=Path(ns.output_path),
        symbols=symbols,
        input_words=int(ns.input_words),
        min_word_size=int(ns.min_word_size),
        max_word_size=int(ns.max_word_size),
        seed=int(ns.seed),
        mode=ns.mode,
        enforce_prefix=(int(ns.enforce_prefix) if ns.enforce_prefix is not None else None),
        filler_symbol=filler_symbol,
        pain_prefix_len=int(ns.pain_prefix_len),
        clusters=int(ns.clusters),
        enforce_global=int(ns.enforce_global),
        enforce_per_cluster=int(ns.enforce_per_cluster),
        noise_ratio=float(ns.noise_ratio),
        inter_cluster_pairs=int(ns.inter_cluster_pairs),
    )

    words = generate_alien_dictionary(cfg)
    text = "\n".join(words) + "\n"
    if ns.output_path is None:
        sys.stdout.write(text)
    else:
        Path(ns.output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.output_path).write_text(text, encoding="utf-8")
    return 0
