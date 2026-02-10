from pathlib import Path


def write_unicode_range(
    start: int,
    end: int,
    output_path: Path,
) -> None:
    """
    Write Unicode characters from start to end (inclusive) to a file.

    Each line contains:
        U+XXXX | decimal | character (or placeholder)

    Parameters
    ----------
    start : int
        Starting Unicode code point.
    end : int
        Ending Unicode code point (inclusive).
    output_path : Path
        Path to the output text file.
    """
    lines: list[str] = []

    for code in range(start, end + 1):
        try:
            ch = chr(code)
        except ValueError:
            continue  # outside Unicode range

        # Mark common invisibles but still print them
        if ch.isspace() and ch != " ":
            display = repr(ch)
        elif ch.isprintable():
            display = ch
        else:
            display = "�"

        lines.append(f"U+{code:06X}\t{code}\t{display}")

    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_unicode_range(
        start=0,
        end=0x10FFFF,
        output_path=Path("output.txt"),
    )