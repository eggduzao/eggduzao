#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# switcheroo.py
#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# switcheroo.py
"""
Recursive, case-preserving find/replace across:
- directory names
- file names
- UTF-8 text file contents

What this version fixes vs the previous one
-------------------------------------------
1) Matches `old_string` ANYWHERE (prefix/mid/suffix) in:
   - dir names
   - file names
   - file contents

2) Matches "fuzzy" spellings where the letters of `old_string` are separated by
   '-', '_' or whitespace, e.g.:
   - tensor-flow
   - tensor_flow
   - F-A-B-R-I-C
   - f a b r i c
   - also matches as a prefix within a longer token: fabricate, fabricated, fabrics, etc.

3) Replacement casing is decided by the *letters in the matched span* (separators ignored):
   - If all cased letters are UPPER -> NEW is UPPER
   - Else if first cased letter is Upper -> New is Capitalized
   - Else -> new is lower

So:
- "TensorFlow"   -> "Jax"
- "tensor-flow"  -> "jax"
- "F-A-B-R-I-C"  -> "APOLLO"
- "fabricated"   -> "apolloated"
- "something-fabric" -> "something-apollo"

Safety / traversal
------------------
- Walk is bottom-up (topdown=False) to avoid missing children when renaming parents.
- Contents are edited BEFORE renaming file names.
- Skips symlinks.
- Only edits files decodable as UTF-8 (BOM allowed). Others are skipped.
- If a rename would collide with an existing path, it is skipped (logged).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Stats:
    renamed_paths: int = 0
    edited_files: int = 0
    skipped_binary_or_nonutf8: int = 0
    rename_collisions: int = 0


def _compile_fuzzy_old_pattern(old_string: str) -> re.Pattern[str]:
    """
    Regex that matches `old_string` case-insensitively, allowing separators between letters.

    Example: old="fabric"
      matches: "fabric", "Fabric", "FABRIC", "F-A-B-R-I-C", "fabri_c", "f a b r i c"
      and matches as substring: "fabricate", "refabricated", "my-fabric-module", etc.
    """
    if not old_string or not old_string.islower():
        raise ValueError("old_string must be a non-empty lowercase string")

    sep = r"[-_\s]*"
    pattern = sep.join(re.escape(ch) for ch in old_string)
    return re.compile(pattern, flags=re.IGNORECASE)


def _styled_replacement(matched: str, new_string: str) -> str:
    """
    Decide replacement casing based on matched span, ignoring separators.

    Rules:
    - If all cased letters in match are upper -> NEW.upper()
    - Else if first cased letter is upper -> New.capitalize()
    - Else -> new.lower()
    """
    if not new_string or not new_string.islower():
        raise ValueError("new_string must be a non-empty lowercase string")

    letters = [c for c in matched if c.isalpha()]
    cased = [c for c in letters if c.isupper() or c.islower()]

    if not cased:
        return new_string.lower()

    if all(c.isupper() for c in cased):
        return new_string.upper()

    first_cased = cased[0]
    if first_cased.isupper():
        return new_string[:1].upper() + new_string[1:].lower()

    return new_string.lower()


def _replace_in_text(text: str, pat: re.Pattern[str], new_string: str) -> tuple[str, bool]:
    def repl(m: re.Match[str]) -> str:
        return _styled_replacement(m.group(0), new_string)

    new_text, n = pat.subn(repl, text)
    return new_text, (n > 0)


def _read_utf8_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return None


def _write_utf8_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def switcheroo(
    *,
    input_path: Path,
    old_string: str,
    new_string: str,
    dry_run: bool = False,
) -> Stats:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))
    if not input_path.is_dir():
        raise NotADirectoryError(str(input_path))
    if not new_string or not new_string.islower():
        raise ValueError("new_string must be a non-empty lowercase string")

    pat = _compile_fuzzy_old_pattern(old_string)

    renamed = 0
    edited = 0
    skipped = 0
    collisions = 0

    # Bottom-up: rename children before parents so traversal isn't disrupted.
    for root, dirnames, filenames in os.walk(input_path, topdown=False, followlinks=False):
        root_path = Path(root)

        # 1) Edit file contents first (paths stable).
        for fname in filenames:
            fpath = root_path / fname
            if fpath.is_symlink():
                continue

            text = _read_utf8_text(fpath)
            if text is None:
                skipped += 1
                continue

            new_text, changed = _replace_in_text(text, pat, new_string)
            if changed:
                edited += 1
                if not dry_run:
                    _write_utf8_text(fpath, new_text)

        # 2) Rename files (after content edits).
        for fname in filenames:
            old_path = root_path / fname
            if old_path.is_symlink():
                continue

            new_name, changed = _replace_in_text(fname, pat, new_string)
            if not changed or new_name == fname:
                continue

            new_path = root_path / new_name
            if new_path.exists():
                collisions += 1
                print(f"[collision] skip rename file: {old_path} -> {new_path}")
                continue

            renamed += 1
            print(f"[rename] file: {old_path} -> {new_path}")
            if not dry_run:
                old_path.rename(new_path)

        # 3) Rename directories in this root (still bottom-up overall).
        for dname in dirnames:
            old_dir = root_path / dname
            if old_dir.is_symlink():
                continue

            new_dname, changed = _replace_in_text(dname, pat, new_string)
            if not changed or new_dname == dname:
                continue

            new_dir = root_path / new_dname
            if new_dir.exists():
                collisions += 1
                print(f"[collision] skip rename dir: {old_dir} -> {new_dir}")
                continue

            renamed += 1
            print(f"[rename] dir:  {old_dir} -> {new_dir}")
            if not dry_run:
                old_dir.rename(new_dir)

    # Rename the root directory name itself (optional, but you asked "including root directory given").
    parent = input_path.parent
    root_name = input_path.name
    new_root_name, changed = _replace_in_text(root_name, pat, new_string)
    if changed and new_root_name != root_name:
        new_root = parent / new_root_name
        if new_root.exists():
            collisions += 1
            print(f"[collision] skip rename root: {input_path} -> {new_root}")
        else:
            renamed += 1
            print(f"[rename] root: {input_path} -> {new_root}")
            if not dry_run:
                input_path.rename(new_root)

    return Stats(
        renamed_paths=renamed,
        edited_files=edited,
        skipped_binary_or_nonutf8=skipped,
        rename_collisions=collisions,
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Recursive case-preserving replace in dir/file names + UTF-8 text contents."
    )
    p.add_argument("input_path", type=Path, help="Root directory to process (inclusive).")
    p.add_argument("old_string", type=str, help="Lowercase old string to replace (e.g. 'fabric').")
    p.add_argument("new_string", type=str, help="Lowercase new string (e.g. 'apollo').")
    p.add_argument("--dry-run", action="store_true", help="Print actions, do not modify filesystem.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        stats = switcheroo(
            input_path=args.input_path,
            old_string=args.old_string,
            new_string=args.new_string,
            dry_run=bool(args.dry_run),
        )
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(
        f"[done] renamed={stats.renamed_paths} edited_files={stats.edited_files} "
        f"skipped_nonutf8_or_binary={stats.skipped_binary_or_nonutf8} collisions={stats.rename_collisions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
Recursive case-preserving find/replace for:
- directory names
- file names
- text file contents

Rules
-----
- Match is case-insensitive for `old_string`
- Replacement preserves "style" using these heuristics:
  - If match contains separators like "-" "_" (or whitespace): replace with **lowercase** `new_string`
  - Else if match is ALLCAPS: replace with `new_string.upper()`
  - Else if match starts with an uppercase letter: replace with `new_string.capitalize()`
  - Else: replace with `new_string.lower()`

Example (old="tensorflow", new="jax"):
- "tensorflow"   -> "jax"
- "Tensorflow"   -> "Jax"
- "TensorFlow"   -> "Jax"
- "TENSORFLOW"   -> "JAX"
- "tensor-flow"  -> "jax"
- "tensor_flow"  -> "jax"
- "WeiRD_CaS-ES" -> if starts lower => "jax"; else => "Jax" (and if separators exist => "jax")

Safety
------
- Only edits text files that can be decoded as UTF-8 (with BOM allowed).
  Non-UTF8 / binary files are skipped.
- Renames are done bottom-up to avoid breaking traversal.
- If a rename would collide with an existing path, it is skipped (logged).

Python
------
3.12+

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Stats:
    renamed_paths: int = 0
    edited_files: int = 0
    skipped_binary_or_nonutf8: int = 0
    rename_collisions: int = 0


def _compile_fuzzy_old_pattern(old_string: str) -> re.Pattern[str]:
    "" "
    Build a regex that matches `old_string` case-insensitively, allowing optional
    separators (hyphen/underscore/space) between characters.

    Example: old="tensorflow"
      matches "TensorFlow", "tensor-flow", "tensor_flow", "t e n s o r f l o w"
    "" "
    if not old_string or not old_string.islower():
        raise ValueError("old_string must be a non-empty lowercase string")

    sep = r"[-_\\s]*"
    parts = [re.escape(ch) for ch in old_string]
    pattern = sep.join(parts)
    return re.compile(pattern, flags=re.IGNORECASE)


def _styled_replacement(matched: str, new_string: str) -> str:
    "" "
    Decide how to case the replacement based on the matched text.

    Heuristics:
    - If separators exist in the match: lowercase new_string
    - Else if match is upper: upper new_string
    - Else if match starts uppercase: capitalize new_string
    - Else: lowercase new_string
    "" "
    if any(c in matched for c in "-_ ") or any(c.isspace() for c in matched):
        return new_string.lower()

    if matched.isupper():
        return new_string.upper()

    if matched[:1].isupper():
        # "Tensorflow" or "TensorFlow" -> "Jax"
        return new_string[:1].upper() + new_string[1:].lower()

    return new_string.lower()


def _replace_in_text(text: str, pat: re.Pattern[str], new_string: str) -> tuple[str, bool]:
    def repl(m: re.Match[str]) -> str:
        return _styled_replacement(m.group(0), new_string)

    new_text, n = pat.subn(repl, text)
    return new_text, (n > 0)


def _replace_in_name(name: str, pat: re.Pattern[str], new_string: str) -> tuple[str, bool]:
    new_name, changed = _replace_in_text(name, pat, new_string)
    return new_name, changed


def _read_utf8_text(path: Path) -> str | None:
    "" "
    Read UTF-8 text (BOM allowed). If decoding fails, return None.
    "" "
    try:
        return path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, OSError):
        return None


def _write_utf8_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def switcheroo(
    *,
    input_path: Path,
    old_string: str,
    new_string: str,
    dry_run: bool = False,
) -> Stats:
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))
    if not input_path.is_dir():
        raise NotADirectoryError(str(input_path))

    if not new_string or not new_string.islower():
        raise ValueError("new_string must be a non-empty lowercase string")

    pat = _compile_fuzzy_old_pattern(old_string)

    renamed = 0
    edited = 0
    skipped = 0
    collisions = 0

    # Walk bottom-up so we can safely rename children before parents.
    for root, dirnames, filenames in os.walk(input_path, topdown=False, followlinks=False):
        root_path = Path(root)

        # --- 1) Edit file contents (text files only) ---
        for fname in filenames:
            fpath = root_path / fname

            # Skip symlinks (avoid surprising behavior)
            if fpath.is_symlink():
                continue

            text = _read_utf8_text(fpath)
            if text is None:
                skipped += 1
                continue

            new_text, changed = _replace_in_text(text, pat, new_string)
            if changed:
                edited += 1
                if not dry_run:
                    _write_utf8_text(fpath, new_text)

        # --- 2) Rename files ---
        for fname in filenames:
            old_path = root_path / fname
            if old_path.is_symlink():
                continue

            new_name, changed = _replace_in_name(fname, pat, new_string)
            if not changed or new_name == fname:
                continue

            new_path = root_path / new_name
            if new_path.exists():
                collisions += 1
                print(f"[collision] skip rename file: {old_path} -> {new_path}")
                continue

            renamed += 1
            print(f"[rename] file: {old_path} -> {new_path}")
            if not dry_run:
                old_path.rename(new_path)

        # --- 3) Rename directories in this root ---
        for dname in dirnames:
            old_dir = root_path / dname
            if old_dir.is_symlink():
                continue

            new_dname, changed = _replace_in_name(dname, pat, new_string)
            if not changed or new_dname == dname:
                continue

            new_dir = root_path / new_dname
            if new_dir.exists():
                collisions += 1
                print(f"[collision] skip rename dir: {old_dir} -> {new_dir}")
                continue

            renamed += 1
            print(f"[rename] dir:  {old_dir} -> {new_dir}")
            if not dry_run:
                old_dir.rename(new_dir)

    # Finally rename the root directory name itself (if caller passed a directory whose name includes old_string)
    parent = input_path.parent
    root_name = input_path.name
    new_root_name, changed = _replace_in_name(root_name, pat, new_string)
    if changed and new_root_name != root_name:
        new_root = parent / new_root_name
        if new_root.exists():
            collisions += 1
            print(f"[collision] skip rename root: {input_path} -> {new_root}")
        else:
            renamed += 1
            print(f"[rename] root: {input_path} -> {new_root}")
            if not dry_run:
                input_path.rename(new_root)

    return Stats(
        renamed_paths=renamed,
        edited_files=edited,
        skipped_binary_or_nonutf8=skipped,
        rename_collisions=collisions,
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Recursive case-preserving replace in names + UTF-8 text contents.")
    p.add_argument("input_path", type=Path, help="Root directory to process (inclusive).")
    p.add_argument("old_string", type=str, help="Lowercase old string to replace (e.g. 'tensorflow').")
    p.add_argument("new_string", type=str, help="Lowercase new string (e.g. 'jax').")
    p.add_argument("--dry-run", action="store_true", help="Print actions, do not modify filesystem.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        stats = switcheroo(
            input_path=args.input_path,
            old_string=args.old_string,
            new_string=args.new_string,
            dry_run=bool(args.dry_run),
        )
    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    print(
        f"[done] renamed={stats.renamed_paths} edited_files={stats.edited_files} "
        f"skipped_nonutf8_or_binary={stats.skipped_binary_or_nonutf8} collisions={stats.rename_collisions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""