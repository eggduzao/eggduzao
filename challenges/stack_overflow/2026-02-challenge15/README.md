# GusmaoLab • Stack Overflow Monthly Challenge • February 2026 👽

## Challenge 15: Alien Dictionary (with Smartly-Harsh Generators)

> *"What if the alphabet itself was the puzzle?"*

This folder contains my solution to **Stack Overflow's February 2026 Monthly Challenge (#15)**, along with a set of input generators ranging from gentle sanity checks to deliberately smartly-harsh (but valid) stress cases.

The goal is not just to solve the Alien Dictionary problem -  
but to explore its algorithmic boundaries.

---

## Solution Overview (**tl;dr**)

- Correct order: ⪏⊚⊕⊟⊞⨙⊛∭↔⊠⊝৲⊣⊗⇲⊥⊢◉⊡⊤◴⚆⊜↪
- Mystery language: Greek
- 'Chameleon' character: Sigma - final-sigma (I do not speek greek, but worked in a lab with many greeks).

---

## Table of Contents

- [Overview](#overview)
- [The Alien Dictionary Problem](#the-alien-dictionary-problem)
- [Solution Summary](#solution-summary)
- [Algorithmic Approach](#algorithmic-approach)
  - [Constraint Extraction](#constraint-extraction)
  - [Topological Sorting (Kahn's Algorithm)](#topological-sorting-kahns-algorithm)
  - [Computational Complexity](#computational-complexity)
  - [Determinism and Ambiguity](#determinism-and-ambiguity)
- [Command-Line Usage](#command-line-usage)
  - [Running Input Dictionaries](#running-input-dictionaries)
  - [Generating Inputs: Unicode Characters](#generating-inputs-unicode-characters)
  - [Generating Inputs: Nice Dictionaries](#generating-inputs-nice-dictionaries)
  - [Generating Inputs: Nightmare Dictionaries](#generating-inputs-nightmare-dictionaries)
- [Input & Output Structure](#input--output-structure)
- [Generators](#generators)
  - [Unicode Symbol Generator](#unicode-symbol-generator)
  - [Easy Dictionary Generator](#easy-dictionary-generator)
  - [Smartly-Harsh Dictionary Generator](#smartly-harsh-dictionary-generator)
- [Mystery Language: Greek](#mystery-language-greek)
- [What This Challenge Tests](#what-this-challenge-tests)
- [Disclaimer](#disclaimer)
- [Final Note](#final-note)

---

## Overview

This challenge asks us to **infer an unknown alphabet order** from a list
of words that are already sorted according to that unknown order.

You are given:
- a list of words (strings),
- sorted lexicographically in an alien language,
- with no direct knowledge of the character ordering.

Your task:
Recover one valid ordering of the symbols - or detect that none exists.

This repository contains:
- a robust solver,
- multiple generators (easy -> hard),
- and tooling to explore correctness, ambiguity, and performance.

---

## The Alien Dictionary Problem

Given a dictionary sorted according to an unknown alphabet:

```
wrt
wrf
er
ett
rftt
```

You must infer a valid character order, e.g.:

```
wertf
```

Key constraints:
- Only the first differing character between adjacent words gives information.
- A word cannot appear before its own prefix (``"abcd"`` before ``"ab"`` is invalid).
- The inferred constraints form a directed acyclic graph (DAG) - or else no solution exists.

---

## Solution Summary

- Approach: Graph construction + topological sorting
- Algorithm: Kahn's Algorithm (BFS-based topo sort)
- Supports:
  - Unicode symbols
  - Deterministic tie-breaking
  - Detection of invalid prefix cases
  - Cycle detection

**Entry point**:  
``2026-02-challenge15/main.py``

---

## Algorithmic Approach

### Constraint Extraction

For each adjacent word pair ``(w₁, w₂)``:

1. Scan left to right.
2. Find the first differing position.
3. If ``w₁[i] = a`` and ``w₂[i] = b``, add constraint:

``a`` -> ``b``

If no difference is found and ``len(w₁) > len(w₂)``:
- The dictionary is **invalid**.

---

### Topological Sorting (Kahn's Algorithm)

1. Collect all distinct symbols.
2. Track indegrees.
3. Initialize a queue with zero-indegree nodes.
4. Repeatedly:
   - remove one node,
   - append it to the result,
   - decrement neighbors' indegrees.

If not all symbols are emitted -> cycle detected -> no valid order.

---

### Computational Complexity

Let:
- ``C`` be the total number of characters across all words (including duplicates),
- ``V`` be the number of unique symbols (vertices),
- ``E`` be the number of precedence constraints (edges).

Then:
- Building the symbol set is 𝒪(``C``).
- Building constraints from adjacent words is 𝒪(``C``) in total, because each
  character position is inspected at most a constant number of times across the
  adjacent comparisons.
- Kahn's algorithm runs in 𝒪(``V`` + ``E``).

Overall time complexity: 𝒪(``C`` + ``V`` + ``E``).

Space complexity is 𝒪(``V`` + ``E``) for the adjacency representation and indegree
map (the input words dominate separately as 𝒪(``C``)).

---

### Determinism and Ambiguity

Topological sorts are **not unique**.

This implementation:
- supports deterministic ordering via stable selection,
- intentionally exposes ambiguity when constraints are sparse,
- and allows testing of solver robustness under multiple valid outputs.

---

## Command-Line Usage

All commands are executed via the **parent runner**:

``challenges/stack_overflow/run.sh``

Typical discovery flow:

```bash
./run.sh help
./run.sh list
```

For this challenge specifically:

```bash
./run.sh solve 2026_02_challenge15 --input input/original-so.txt
```

### Running Input Dictionaries



---

### Generating Inputs: Unicode Characters

Unicode ranges for ~20K–80K characters (hex)

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

---

### Generating Inputs: Nice Dictionaries



---

### Generating Inputs: Nightmare Dictionaries

(How to Make It More... ~painful~ interesting)

Below are the levers that shape the difficulty, and where it lies, of the dataset.

#### ``--pain-prefix-len``
Controls how **deep** the first difference between adjacent words occurs.

- Low (0-4): classic Alien Dictionary
- Medium (16-64): long string comparisons
- High (96+): very expensive naive comparisons

Effect:
- stresses implementations that compare character-by-character
- makes prefix scanning the dominant cost

#### ``--clusters``
Splits the alphabet into **clusters**.

- Constraints are mostly **inside clusters**
- Very few edges connect clusters

Effect:
- graph has many weakly-connected components
- Kahn's algorithm queue stays large
- ordering is highly ambiguous

#### ``--enforce-per-cluster``
How many characters per cluster are locally chained.

- 0: almost no structure
- 4-8: light internal order
- 16+: clusters behave like mini alphabets

Effect:
- controls local determinism vs global ambiguity

#### ``--inter-cluster-pairs``
Number of constraints connecting adjacent clusters.

- 0: clusters completely independent
- 1-2: barely connected DAG
- 5+: stronger global structure

Effect:
- determines whether the graph is barely connected or comfortably connected

---

### ``--noise-ratio``
Fraction of generated words that add **no new constraints**.

- 0.5: informative dataset
- 0.8-0.9: sparse signal
- 0.95+: information-theoretic cruelty (still valid... if you're into that stuff...)

Effect:
- inflates input size without helping the solver
- punishes algorithms that assume "more data leads to more information"

---

## Input & Output Structure

```
2026_02_challenge15/
├── input/        # Generated or hand-written dictionaries
├── output/       # Solver results
├── symbols/      # Unicode alphabets (one symbol per line)
└── assets/       # Bonus materials (e.g. Greek mapping and translation)
```

---

## Generators

### Unicode Symbol Generator

File:

``unicode_alphabet.py``

Purpose:
 - generate symbol sets using Unicode ranges
 - visible, invisible, or mixed characters
 - test Unicode safety and robustness

Outputs to:

``symbols/``

---

### Easy Dictionary Generator

File:

``simple_dictionary_generator.py``

Purpose:
 - sanity checks
 - small datasets
 - minimal ambiguity

Command (conceptual):

``./run.sh generate-easy 2026_02_challenge15``


---

### Smartly-Harsh Dictionary Generator

File:

``hard_dictionary_generator.py``

Purpose:
 - stress testing
 - sparse constraints
 - deep common prefixes
 - massive ambiguity

Produces valid but algorithmically annoying datasets.

Think:
 - large Kahn queues
 - low information density
 - many correct answers

---

## Mystery Language: Greek

The challenge's sample dictionary encodes Greek vocabulary,
stripped of accents and normalized (e.g. final sigma).

A mapping between:
 - alien symbols,
 - Greek words,
 - and English *translation attempts*,

is provided in ``assets/`` and previewed in the table below:

| **Alien** | **Greek (no accent)** | **Greek** | **English** |
| ----- |-------------------|-------|---------|
| ⪏⊕⪏⊥⊛ | αγαπη | αγάπη | love (divine/unconditional) |
| ⪏⊕⇲⊢⪏ | αγορα | αγορά | marketplace |
| ⪏⊟⊞⊝◴⇲◉ | αδελφοσ | αδελφός | brother |
| ⪏⊞⊢⪏◉ | αερασ | αέρας | air |
| ⪏⨙↪⊡⇲ | αζωτο | άζωτο | nitrogen |
| ⪏⊛⊟⇲⊣↔ | αηδονι | αηδόνι | nightingale |
| ⪏⊝⊛∭⊞↔⪏ | αληθεια | αλήθεια | truth |
| ⪏⊣⊞৲⇲◉ | ανεμοσ | άνεμος | wind |
| ⊚⪏⊢⇲◉ | βαροσ | βάρος | weight |
| ⊚↔⊚⊝↔⇲ | βιβλιο | βιβλίο | book |
| ⊚⇲⊤⊣⇲ | βουνο | βουνό | mountain |
| ⊚⊢⇲⚆⊛ | βροχη | βροχή | rain |
| ⊕⪏⊝⪏ | γαλα | γάλα | milk |
| ⊕⊛ | γη | γη | earth |
| ⊕⊢⪏৲৲⪏ | γραμμα | γράμμα | letter (character) |
| ⊕⊤⊣⪏↔⊠⪏ | γυναικα | γυναίκα | woman |
| ⊟⪏◉⇲◉ | δασοσ | δάσος | forest |
| ⊟⊞⊣⊡⊢⇲ | δεντρο | δέντρο | tree |
| ⊟⊢⇲৲⇲◉ | δρομοσ | δρόμος | road |
| ⊞⊟↪ | εδω | εδώ | here |
| ⊞↔⊠⇲⊣⪏ | εικονα | εικόνα | image |
| ⊞⊝⊞⊤∭⊞⊢↔⪏ | ελευθερια | ελευθερία | freedom |
| ⊞⊝⊥↔⊟⪏ | ελπιδα | ελπίδα | hope |
| ⊞⊗⇲⊟⇲◉ | εξοδοσ | έξοδος | exit |
| ⊞⊢↪⊡⪏ | ερωτα | έρωτας | passion (romantic love) |
| ⊛⊝↔⇲◉ | ηλιοσ | ήλιος | sun |
| ⊛৲⊞⊢⪏ | ημερα | ημέρα | day |
| ∭⪏⊝⪏◉◉⪏ | θαλασσα | θάλασσα | sea |
| ∭⊞⇲◉ | θεοσ | θεός | god |
| ↔⊟⊞⪏ | ιδεα | ιδέα | idea |
| ↔◉⇲◉ | ισοσ | ίσος | equal |
| ↔◉⊡⇲⊢↔⪏ | ιστορια | ιστορία | history |
| ↔⚆∭⊤◉ | ιχθυσ | ιχθύς | fish (formal) |
| ⊠⪏⨙⪏⊣↔ | καζανι | καζάνι | cauldron |
| ⊠⪏⊠⇲◉ | κακοσ | κακός | bad |
| ⊠⪏⊝⇲◉ | καλοσ | καλός | good |
| ⊠⪏⊢⊟↔⪏ | καρδια | καρδιά | heart |
| ⊠⇲◉৲⇲◉ | κοσμοσ | κόσμος | world |
| ⊝⊞⊗⊛ | λεξη | λέξη | word |
| ⊝↔৲⊣⊛ | λιμνη | λίμνη | lake |
| ⊝⇲⊕⇲◉ | λογοσ | λόγος | reason/speech |
| ৲⪏⨙↔ | μαζι | μαζί | together |
| ৲⪏⊡↔ | ματι | μάτι | eye |
| ৲⊞⊝↔ | μελι | μέλι | honey |
| ৲⊞⊢⪏ | μερα | μέρα | day |
| ⊣⊞⊢⇲ | νερο | νερό | water |
| ⊣⊛◉↔ | νησι | νησί | island |
| ⊣⊤⚆⊡⪏ | νυχτα | νύχτα | night |
| ⊗⊞⊣⇲◉ | ξενοσ | ξένος | stranger |
| ⊗⊤⊝⇲ | ξυλο | ξύλο | wood |
| ⇲৲⇲⊢◴⇲ | ομορφο | όμορφο | beautiful |
| ⇲⊣⊞↔⊢⇲ | ονειρο | όνειρο | dream |
| ⇲⊗⊤ | οξυ | οξύ | sharp |
| ⇲⊢⇲◉ | οροσ | όρος | mountain |
| ⊥⪏↔⊟↔ | παιδι | παιδί | child |
| ⊥⇲⊝⊛ | πολη | πόλη | city |
| ⊥⇲⊡⪏৲⇲◉ | ποταμοσ | ποτάμι | river |
| ⊥⊤⊢ | πυρ | πυρ | fire |
| ⊢↔⨙⪏ | ριζα | ρίζα | root |
| ⊢⇲⊟⇲ | ροδο | ρόδο | rose |
| ◉⊥↔⊡↔ | σπιτι | σπίτι | house |
| ◉⊡⇲৲⪏ | στομα | στόμα | mouth |
| ⊡⪏⊗⊛ | ταξη | τάξη | order |
| ⊡⊞⚆⊣⊛ | τεχνη | τέχνη | art |
| ⊡⇲⊥⇲◉ | τοποσ | τόπος | place |
| ⊤⊕⊢⇲ | υγρο | υγρό | liquid |
| ⊤⊥⊣⇲◉ | υπνοσ | ύπνος | sleep |
| ◴↔⊝⇲◉ | φιλοσ | φίλος | friend |
| ◴⊤◉⊛ | φυση | φύση | breath/nature |
| ◴↪◉ | φωσ | φως | light |
| ⚆⪏⊢⪏ | χαρα | χαρά | joy |
| ⚆⊢⇲⊣⇲◉ | χρονοσ | χρόνος | time |
| ⚆↪⊢⪏ | χωρα | χώρα | country |
| ⊜⪏⊢↔ | ψαρι | ψάρι | fish |
| ⊜⊤⚆⊛ | ψυχη | ψυχή | soul |
| ↪⊠⊞⪏⊣⇲◉ | ωκεανοσ | ωκεανός | ocean |
| ↪⊢⪏ | ωρα | ώρα | hour |

---

## What This Challenge Tests

Educationally, this challenge explores:
 - Graph modeling from partial information
 - Prefix edge cases
 - Cycle detection
 - Ambiguous topological sorts
 - Determinism vs correctness
 - Performance under high ``N``, low ``E``
 - Unicode handling at the symbol level

---

Disclaimer

This repository does not attempt to break machines or people.

Smartly-Harsh generators are:
 - mathematically valid,
 - pedagogical by design,
 - and intended to spark discussion about algorithmic limits.

If something struggles - that's a learning opportunity, not a failure.

---

Final Note

As my fellow Brazilian Paulo Freire would remind us:

>Learning happens where curiosity meets challenge -
>not where fear meets silence.

Thanks for the puzzle, Stack Overflow 👽
And remember: no geography, only graphs.
