# GusmaoLab • Stack Overflow Monthly Challenges

## Table of Contents
- [Overview](#overview)
- [Challenges Index](#challenges-index)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Example: Alien Dictionary](#example-alien-dictionary)
- [Shameless Plug](#a-small-shameless-plug)
- [Contributing & Collaboration](#contributing--collaboration)
- [Philosophy & Notes](#philosophy--notes)
- [About](#about)

---

## Overview

Hello!

This folder contains my solutions to **Stack Overflow's Monthly Challenges**, approached as a mix of:
- algorithmic problem-solving,
- clean engineering,
- and a bit of playful experimentation.

Each month lives in its own self-contained directory, with:
- a solver,
- input generators (easy -> adversarial),
- outputs,
- and a README explaining the thought process.

The idea is simple:
make the solution correct, readable, reproducible - and occasionally fun to
explore beyond the minimum requirements.

If you're a challenge author, reviewer, or just curious: this README is your
entry point.

---

## Challenges Index

> Think of this as a *"jump menu"* - it will grow over time.
> (In the future, this section will be auto-updated via GitHub Actions.)

- **2026 • February • Challenge 15**
  Alien Dictionary (Topological Sort)
  - [`2026_02_challenge15/`](2026_02_challenge15/)
  - [Challenge README](2026_02_challenge15/README.md)

More challenges will appear here month by month.

---

## Installation

No heavy setup. No frameworks. No surprises.

### 1. Clone the repository

```bash
git clone https://github.com/eggduzao/eggduzao.git
cd eggduzao
```

### 2. (Optional) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
```

### 3. (Optional) Install the local package (editable mode)

```bash
pip install -e .
```

Steps 2 and 3 are optional. They lets challenge scripts import shared utilities
cleanly, while keeping everything local and hackable.

That's it. No extra dependencies are required for Stack Overflow challenges at
the moment.

Take a look at the Challenge's README, all execution info are there.

---

## Quick Start

All Stack Overflow challenges are driven by a single entrypoint:

``./challenges/stack_overflow/run.sh``

To discover what's available:

``./challenges/stack_overflow/run.sh --help``

Typical pattern:

``./challenges/stack_overflow/run.sh <challenge> <command> [options]``

Each monthly challenge exposes:
 - generators (easy / hard / symbols),
 - a solver,
 - and help messages describing inputs and outputs.

---

## Example: Alien Dictionary

The Alien Dictionary challenge is a good first example of how everything fits together.

Explore available commands

``./challenges/stack_overflow/run.sh alien --help``

Generate a Unicode symbol set

``./challenges/stack_overflow/run.sh alien generate-symb``

Generate an easy input

``./challenges/stack_overflow/run.sh alien generate-easy``

Generate an adversarial (stress-test) input

``./challenges/stack_overflow/run.sh alien generate-hard``

Solve the challenge

``./challenges/stack_overflow/run.sh alien solve``

Outputs are written to the challenge's local output/ directory, keeping everything nicely sandboxed.

---

## Shameless Plug

If you enjoyed this challenge or the way it's structured, feel free to explore the rest of the repository.

This project doubles as:
 - a personal playground,
 - a portfolio of problem-solving styles,
 - and a place to experiment with ideas slightly beyond what a prompt strictly asks for.

If something made you think: *"oh, that's neat"* (or someone had to make a
Haimlich Maneuver on you)...

Then mission accomplished!

---

## Contributing & Collaboration

Different interests, different doors:
 - Machine Learning / Algorithms
You might enjoy contributing to challenge solutions, generators, or benchmarks.
 - Bioinformatics / Computational Biology
The main repository contains projects and tooling closer to real-world data problems.
 - Engineering / Tooling
CLI design, automation, testing, and documentation are always welcome areas.

If you're curious:
 - start a discussion,
 - open an issue,
 - or just reach out.

Formal contribution guidelines (style, code of conduct, etc.) live at the main repository level and apply here as well.

---

## Philosophy & Notes

These solutions are intentionally:
 - reproducible,
 - readable,
 - and occasionally playful.

Some challenges include:
 - stress tests,
 - adversarial inputs,
 - or "bonus" explorations that go beyond the strict requirements.

They're meant as learning tools, not as weapons, benchmarks, or gotchas.

---

## About

I'm Eduardo and I will always regret the day I decided on this 'nickname'.

I work at the intersection of:
 - machine learning,
 - data,
 - biology,
 - and software engineering.

This repository is where I:
 - practice,
 - experiment,
 - and share things that I find interesting or instructive.

If you made it this far: thanks for reading - and enjoy the challenges!

