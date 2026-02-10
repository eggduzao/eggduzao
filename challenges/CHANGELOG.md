# Changelog

All notable changes to the **Challenges** section of this repository are documented here.

This file is intentionally concise.  
Entries focus on **milestones, submissions, and meaningful structural changes**, not every commit.

Dates follow ISO format: `YYYY-MM-DD`.

---

## [Unreleased]
- Placeholder for upcoming challenges and improvements.

---

## [2026-02-10] — Stack Overflow Monthly Challenge #15 (Alien Dictionary)

### Added
- Initial solution for **Alien Dictionary** (topological sort, Kahn’s algorithm).
- Unicode-capable symbol handling (including non-ASCII alphabets).
- Deterministic tie-breaking for ambiguous orderings.
- CLI and `run.sh` dispatch infrastructure for Stack Overflow challenges.

### Added (Generators)
- Easy dictionary generator for sanity checks.
- Adversarial dictionary generator for stress-testing and ambiguity exploration.
- Unicode alphabet generator supporting visible and invisible character ranges.

### Documentation
- Challenge-specific README with algorithmic explanation and usage examples.
- Stack Overflow challenges index README.
- Clear input/output directory conventions.

### Notes
- This marks the first Stack Overflow Monthly Challenge included in this repository.
- Future challenges will be added incrementally, one folder per month.

---

