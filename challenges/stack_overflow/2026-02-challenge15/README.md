# Alien Dictionary - Solution + Adversarial Dictionary Generator

## Solution Overview (**tl;dr**)

- Correct order: ⪏⊚⊕⊟⊞⨙⊛∭↔⊠⊝৲⊣⊗⇲⊥⊢◉⊡⊤◴⚆⊜↪
- Mystery language: Greek
- 'Chameleon' character: Sigma - final-sigma (I do not speek greek, but worked in a lab with many greeks).

### **README's TOC:**
- Solution's algorithm description
- Mystery language details (translations to English)
- How to generate symbols in Unicode (visible and invisible ranges)
- Development of an 'extreme' dictionary generator
- Generating an 'extreme' case and solving it
- What This Challenge Tests (Educationally)
- Disclaimer
- Final Note

---

## Solution's algorithm description

Compute a valid symbol ordering (an "alphabet") presented in a "dictionary-form":
a list of words already sorted according to some unknown lexicographic order.

This module provides a robust, CLI-friendly implementation based on a
'seed'-aware variant of **Kahn's topological sorting algorithm**. It extracts the
minimal precedence constraints implied by the sorted word list and returns one
valid ordering of all symbols observed in the input.

### Overview

Given a list of words sorted in an unknown alphabet, we can infer ordering
constraints by comparing each pair of adjacent words:

- Find the first position where two adjacent words differ.
- If word₁ has symbol `a` and word₂ has symbol `b` at that position, then we must
  have `a -> b` (meaning `a` comes before `b`).
- Only the first differing position matters-everything after it is unconstrained
  by lexicographic comparison.
- Additionally, the dictionary is invalid if a longer word appears before its
  exact prefix (e.g. `"abcd"` before `"ab"`). In that case, no ordering can
  satisfy the given sorting.

All inferred constraints form a directed graph over symbols. Any valid alphabet
corresponds to a topological ordering of that graph.

### Algorithm

This implementation uses a seed-aware Kahn's algorithm:

1. Initialize vertices
   Collect every distinct symbol that appears anywhere in the input. This ensures
   the result includes symbols even if they have no edges.
2. Build edges from adjacent words
   For each consecutive pair `(w1, w2)`, locate the first differing symbol
   `(c1, c2)` and add a directed edge `c1 -> c2`. Maintain indegree counts.
3. Topological sort (Kahn)
   Start with all symbols whose indegree is zero. Repeatedly remove one such
   symbol, append it to the output, and decrement the indegree of its outgoing
   neighbors. When a neighbor reaches indegree zero, enqueue it.
4. Cycle detection
   If we cannot output all symbols (i.e. output length < number of symbols),
   the constraints contain a cycle and there is no valid ordering.

### Seed-aware behavior

Topological sorting is not necessarily unique. When multiple symbols are eligible
(indegree zero), this implementation can be made deterministic by seeding the
selection order (e.g. sorting candidates or using a stable tie-break rule).
A deterministic tie-break makes results reproducible across runs, which is often
useful for testing and for downstream pipelines.

### Complexity Analysis

Let:
- `C` be the total number of characters across all words (including duplicates),
- `V` be the number of unique symbols (vertices),
- `E` be the number of precedence constraints (edges).

Then:
- Building the symbol set is 𝒪(C).
- Building constraints from adjacent words is 𝒪(C) in total, because each
  character position is inspected at most a constant number of times across the
  adjacent comparisons.
- Kahn's algorithm runs in 𝒪(V + E).

Overall time complexity: 𝒪(C + V + E).

Space complexity is 𝒪(V + E) for the adjacency representation and indegree
map (the input words dominate separately as 𝒪(C)).

### API

Main (Entry Point) is:


Topological Sort Implementation is:
- ``def alien_order_robust_deterministic(words: list[str] | None) -> list[str] | None:``
- Returns a valid ordering as a list of symbols (`str` of length 1),
  or ``None`` if the dictionary is inconsistent.

### Examples

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

### Command-line usage (typical pattern)
Assuming you expose a CLI entry point that:
1) reads one word per line from a file, and
2) prints the discovered alphabet as a single line,

you might run:

$ python challenge_15.py --help
$ python challenge_15 ./input/original-so.txt
$ python challenge_15 ./input/original-so -o ./output/original-so.txt

Input format example (input.txt):

wrt
wrf
er
ett
rftt

Output (one possible):

wertf

### Notes
- This solver is Unicode-safe at the symbol level: Python ``str`` elements are
  Unicode code points. If your "symbols" are multi-codepoint graphemes, you
  should pre-tokenize accordingly.
- Determinism is optional. If you need a stable order when ties occur, apply a
  deterministic policy (e.g. sorting the zero-indegree queue).









---

## Mystery language details (translations to English)

The mistery language is actually Greek, without accents and with the "final sigma" replaced by the "round sigma". All words are in the table below, with their proper Greek equivalent and English "attempted translation" (I am not greek nor speak greek).

| Greek (no accent) | Greek | English |
|-------------------|-------|---------|
| αγαπη | αγάπη | love (divine/unconditional) |
| αγορα | αγορά | marketplace |
| αδελφοσ | αδελφός | brother |
| αερασ | αέρας | air |
| αζωτο | άζωτο | nitrogen |
| αηδονι | αηδόνι | nightingale |
| αληθεια | αλήθεια | truth |
| ανεμοσ | άνεμος | wind |
| βαροσ | βάρος | weight |
| βιβλιο | βιβλίο | book |
| βουνο | βουνό | mountain |
| βροχη | βροχή | rain |
| γαλα | γάλα | milk |
| γη | γη | earth |
| γραμμα | γράμμα | letter (character) |
| γυναικα | γυναίκα | woman |
| δασοσ | δάσος | forest |
| δεντρο | δέντρο | tree |
| δρομοσ | δρόμος | road |
| εδω | εδώ | here |
| εικονα | εικόνα | image |
| ελευθερια | ελευθερία | freedom |
| ελπιδα | ελπίδα | hope |
| εξοδοσ | έξοδος | exit |
| ερωτα | έρωτας | passion (romantic love) |
| ηλιοσ | ήλιος | sun |
| ημερα | ημέρα | day |
| θαλασσα | θάλασσα | sea |
| θεοσ | θεός | god |
| ιδεα | ιδέα | idea |
| ισοσ | ίσος | equal |
| ιστορια | ιστορία | history |
| ιχθυσ | ιχθύς | fish (formal) |
| καζανι | καζάνι | cauldron |
| κακοσ | κακός | bad |
| καλοσ | καλός | good |
| καρδια | καρδιά | heart |
| κοσμοσ | κόσμος | world |
| λεξη | λέξη | word |
| λιμνη | λίμνη | lake |
| λογοσ | λόγος | reason/speech |
| μαζι | μαζί | together |
| ματι | μάτι | eye |
| μελι | μέλι | honey |
| μερα | μέρα | day |
| νερο | νερό | water |
| νησι | νησί | island |
| νυχτα | νύχτα | night |
| ξενοσ | ξένος | stranger |
| ξυλο | ξύλο | wood |
| ομορφο | όμορφο | beautiful |
| ονειρο | όνειρο | dream |
| οξυ | οξύ | sharp |
| οροσ | όρος | mountain |
| παιδι | παιδί | child |
| πολη | πόλη | city |
| ποταμοσ | ποτάμι | river |
| πυρ | πυρ | fire |
| ριζα | ρίζα | root |
| ροδο | ρόδο | rose |
| σπιτι | σπίτι | house |
| στομα | στόμα | mouth |
| ταξη | τάξη | order |
| τεχνη | τέχνη | art |
| τοποσ | τόπος | place |
| υγρο | υγρό | liquid |
| υπνοσ | ύπνος | sleep |
| φιλοσ | φίλος | friend |
| φυση | φύση | breath/nature |
| φωσ | φως | light |
| χαρα | χαρά | joy |
| χρονοσ | χρόνος | time |
| χωρα | χώρα | country |
| ψαρι | ψάρι | fish |
| ψυχη | ψυχή | soul |
| ωκεανοσ | ωκεανός | ocean |
| ωρα | ώρα | hour |

---

## How to generate symbols in Unicode (visible and invisible ranges)

2.  Unicode ranges for ~20K–80K characters (hex)

A quick reality check: Unicode doesn’t have 20K distinct “invisible” characters. There are some invisibles/format controls/space variants, but nowhere near that scale. So for “invisible-only” I’ll give you the best concentrated blocks and you’ll end up with hundreds to low thousands, which is already plenty “weird”.

Also: “visible” is fuzzy (fonts differ), but these ranges are a good practical approximation.

A) Mostly visible (safe-ish) symbol sets

≈20,448 chars (20K-ish):
  • start = 0x0021
  • end   = 0x4FFF

Why: lots of common scripts/symbols; still some oddities but overwhelmingly visible.

≈79,840 chars (80K-ish):
  • start = 0x0021
  • end   = 0x13FFF

This pulls in a huge amount of assigned symbols; you will get some that render as tofu in some fonts, but mostly visible.

If you want “more reliably visible” (fewer tofu boxes), use multiple ranges instead of one giant one:
  • 0x0021–0x007E (Basic Latin, visible punctuation/letters)
  • 0x00A1–0x024F (Latin-1 Supplement + Latin Extended A/B)
  • 0x0370–0x052F (Greek + Cyrillic)
  • 0x2000–0x2BFF (General punctuation + arrows + math-ish + misc symbols)
  • 0x3040–0x30FF (Hiragana + Katakana)
  • 0x4E00–0x9FFF (CJK Unified Ideographs) (big chunk; very visible if you have fonts)

(You can combine these ranges and stop when you reach your target count.)

⸻

B) “Invisible-only” (best-effort, smaller)

You won’t get 20K. Here are the densest “mostly invisible/control/format/space” blocks:
  • 0x0000–0x001F (C0 controls)
  • 0x007F–0x009F (DEL + C1 controls)
  • 0x2000–0x200F (spaces + directional marks)
  • 0x2028–0x202F (line/paragraph separators + narrow no-break space + directional formatting)
  • 0x2060–0x206F (word joiner + invisible operators + formatting)
  • 0xFE00–0xFE0F (variation selectors)
  • 0xFFF0–0xFFFF (specials)

These are “invisible-heavy” and will definitely include classic weirdos like zero-width joiner / non-joiner, BOM, etc. Many will print as nothing, or as replacement glyphs depending on your formatting.

If you want to keep it “not shady,” avoid the bidi override range 0x202A–0x202E and just stick to:
  • 0x2000–0x200F, 0x2060–0x2064, 0xFE00–0xFE0F

⸻

C) Mostly visible + a pinch of invisible (my favorite)

Use a big visible block, then sprinkle a small invisible block:

Visible bulk (choose one):
  • 0x0021–0x4FFF  (≈20K)
  • 0x0021–0x13FFF (≈80K)

Invisible sprinkle:
  • 0x2000–0x200F
  • 0x2060–0x2064
  • 0xFE00–0xFE0F

That gives you a dataset that’s “normal-looking” but still contains a few gremlins for robustness testing.









## Development of an 'extreme' dictionary generator

### Interesting Scripts:

Besides the main script ``challenge_15.py``, I've built a completely harmless **Alien Dictionary Generator Kit**

### What is this?

This project generates **valid Alien Dictionary datasets** (the classic topological-sort / Kahn's Algorithm problem), but with **intentionally adversarial structure**.

The goal is **not** to break machines or people.  
The goal is to explore **algorithmic limits**, **ambiguity**, **graph sparsity**, and **performance traps** in a playful, pedagogical, and slightly theatrical way.

Think of it as:
- a **stress test** for reasoning
- a **benchmark** for implementations
- a **conversation starter** about algorithm design
- a **fantasy boss fight** for graph algorithms

All outputs are **correct alien dictionaries**:  
- lexicographically sorted in a consistent alien order  
- no invalid prefix violations (e.g. `"a"` always comes before `"aba"`)  
- solvable via topological sorting (unless *you* intentionally inject cycles)

---

### Core Idea (High Level)

Given:
- a **true alien alphabet order** (one symbol per line)
- a set of **words already sorted** according to that order

The participant must:
1. infer precedence constraints between characters
2. build a directed graph
3. perform a topological sort

This generator controls:
- **how many constraints exist**
- **where constraints appear**
- **how expensive they are to detect**
- **how ambiguous the final ordering is**



### Modes

1. `unique` ✨
  - Enforces a **total order**
  - Most characters become fully ordered
  - Usually only one valid solution
  - Good for sanity checks and correctness

2. `ambiguous` 💔
  - Enforces order only for a **prefix of the alphabet**
  - Remaining characters are unconstrained
  - Many valid outputs
  - Good for testing determinism, tie-breaking, and correctness under ambiguity

3. `adversarial` 🦄
  - Main idea is to inflict physical and/or mental trauma.

This mode is designed to be **algorithmically annoying but valid**:

- Deep common prefixes (expensive comparisons)
- Sparse constraints (huge Kahn queues)
- Clustered partial orders
- Massive word counts with low information density
- Many valid answers, few guiding edges

---

## Basic Usage

### Step 1 - Prepare the alien alphabet

Create a UTF-8 text file, one character per line, in the **true alien order**:

```
a
b
c
d
...
```

This file defines the *ground truth* ordering.

---

### Step 2 - Generate a dataset

Example (moderately adversarial):


```bash
python alien_generator.py \
  -input-path alien_alphabet.txt \
  -output-path dictionary.txt \
  -mode adversarial \
  -input-words 200000 \
  -min-word-size 16 \
  -max-word-size 64 \
  -pain-prefix-len 48 \
  -clusters 32 \
  -enforce-per-cluster 8 \
  -inter-cluster-pairs 1 \
  -noise-ratio 0.92
```


The output file is already **sorted correctly** (given the order of ``alien_alphabet.txt``).

---

## Adversarial Knobs (How to Make It More... ~painful~ interesting)

Below are the levers that shape the difficulty, and where it lies, of the dataset.

### `--pain-prefix-len`
Controls how **deep** the first difference between adjacent words occurs.

- Low (0-4): classic Alien Dictionary
- Medium (16-64): long string comparisons
- High (96+): very expensive naive comparisons

Effect:
- stresses implementations that compare character-by-character
- makes prefix scanning the dominant cost

---

### `--clusters`
Splits the alphabet into **clusters**.

- Constraints are mostly **inside clusters**
- Very few edges connect clusters

Effect:
- graph has many weakly-connected components
- Kahn's algorithm queue stays large
- ordering is highly ambiguous

---

### `--enforce-per-cluster`
How many characters per cluster are locally chained.

- 0: almost no structure
- 4-8: light internal order
- 16+: clusters behave like mini alphabets

Effect:
- controls local determinism vs global ambiguity

---

### `--inter-cluster-pairs`
Number of constraints connecting adjacent clusters.

- 0: clusters completely independent
- 1-2: barely connected DAG
- 5+: stronger global structure

Effect:
- determines whether the graph is barely connected or comfortably connected

---

### `--noise-ratio`
Fraction of generated words that add **no new constraints**.

- 0.5: informative dataset
- 0.8-0.9: sparse signal
- 0.95+: information-theoretic cruelty (still valid... if you're into that stuff...)

Effect:
- inflates input size without helping the solver
- punishes algorithms that assume "more data leads to more information"

---












## Generating an 'extreme' case and solving it

### Balanced Challenge

```bash
python alien_generator.py \
-mode adversarial \
-input-words 100000 \
-pain-prefix-len 32 \
-clusters 16 \
-enforce-per-cluster 6 \
-inter-cluster-pairs 1 \
-noise-ratio 0.9
```

### Reasoning Stress Test

```bash
python alien_generator.py \
-input-words 300000 \
-pain-prefix-len 64 \
-clusters 32 \
-enforce-per-cluster 8 \
-noise-ratio 0.93
```

### "Final Boss"

```bash
python alien_generator.py \
-input-words 1000000 \
-pain-prefix-len 96 \
-clusters 64 \
-enforce-per-cluster 6 \
-inter-cluster-pairs 1 \
-noise-ratio 0.95
```












---

## What This Tests (Educationally)

- Correct handling of prefix rules
- Sparse vs dense constraint graphs
- Ambiguous topological sorts
- Queue behavior in `Kahn's algorithm`
- Determinism under multiple valid answers
- Performance under high `N`, low `E`
- Separation of time vs space / I/O load vs algorithmic cost

---

## Disclaimer

> [!IMPORTANT]
> This is a **dataset generator**, not an exploit.
> If someone's implementation struggles, that's a teaching moment.

---

## Final Note

As **my fellow Brazilian** Paulo Freire would say (loosely paraphrased):
> learning happens where curiosity meets challenge - not where fear meets silence.

---

Thanks for the puzzle 👽  
And remember: no geography.
