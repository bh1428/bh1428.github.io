#!/usr/bin/env python3
"""Dump a directory (including file content) as text.

(c) 2025 Ben Hattem

The main application for this script is to show the content of a small
filesystem tree. The content of each file will be shown, either as text
or as hex dump. This script is not optimized for large files / trees.
Limited effort is done to consider memory usage. File content is not
streamed but read entirely into memory (as lists of str).

This is meant as a quick and dirty script to dump a file tree. Error
handling (file authorization) is not implemented: every file and directory
is supposed to be readable.
"""

import sys
import textwrap
from pathlib import Path


def guess_text_encoding(path: Path, sample_size: int = 5 * 1024) -> str:
    """Guesstimate file encoding.

    The algorithm is very basic: if the first `sample_size` bytes of a file
    can be converted to Unicode ('UTF-8') the file is considered to be in
    text format. Otherwise the file is supposed to be binary. Although this
    is a huge simplification it is good enough for our purposes.

    Args:
        path (Path): file to be checked
        sample_size (int, optional): number of bytes to sample (default 5K).

    Returns:
        str: encoding, either 'UTF-8', or 'BINARY'
    """
    with open(path, "rb") as fh_in:
        chunk = fh_in.read(sample_size)
        try:
            if chunk.decode("UTF-8-SIG"):
                return "UTF-8"
        except UnicodeError:
            pass
    return "BINARY"


def hex_dump(path: Path, bytes_per_line: int = 25) -> str:
    """Dump the content of a file as a hexadecimal dump.

    Only 7-bit printable ASCII characters are shown in the dump. Of course,
    we could extend this to more characters, but then we may get issues with
    multiple character Unicode code points. This is supposed to be a basic
    hex dumper and not a full blown application.

    Args:
        path (Path): file to be hex dumped
        bytes_per_line (int, optional): number of bytes per line (default 25)

    Returns:
        str: hex dump lines ready to be printed (including line endings)
    """
    hex_width = bytes_per_line * 3
    hex_str_lines: list[str] = []
    offset_width = len(hex(path.stat().st_size)) - 2
    with open(path, "rb", buffering=10 * 1024 * 1024) as f:  # with 10MB buffer
        offset = 0
        while True:
            chunk = f.read(bytes_per_line)
            if not chunk:  # EOF
                break
            hex_values = " ".join(f"{b:02x}" for b in chunk)
            printable = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            hex_str_lines.append(f"{offset:0{offset_width}x}: {hex_values:<{hex_width}} {printable}")
            offset += bytes_per_line
    return "\n".join(hex_str_lines)


def text_dump(path: Path, line_width: int = 120) -> str:
    """Dump the content of a (UTF-8 encoded) file with line numbers.

    Args:
        path (Path): file to be 'dumped'
        line_width (int, optional): maximum line width (default 80)

    Returns:
        str: text dump lines ready to be printed (including line endings)
    """
    file_content = path.read_text(encoding="UTF-8-SIG").splitlines()
    line_counter_width = len(str(len(file_content)))
    subsequent_indent = " " * (line_counter_width + 2)
    text_width = line_width - line_counter_width - 2
    text_lines: list[str] = []
    for line_nr, line in enumerate(file_content, 1):
        if line:
            text_lines.append(
                "\n".join(
                    textwrap.wrap(
                        line,
                        width=text_width,
                        initial_indent=f"{line_nr:0{line_counter_width}}: ",
                        subsequent_indent=subsequent_indent,
                        tabsize=4,
                        replace_whitespace=False,
                        drop_whitespace=False,
                    )
                )
            )
        else:
            text_lines.append(f"{line_nr:0{line_counter_width}}:")
    return "\n".join(text_lines)


def dump_file_tree(root: str | Path) -> None:
    """Dump the content of a filesystem tree.

    Binary files will be shown as hex dump, text files as lines of text.

    Args:
        root (str | Path): root of the tree to dump
    """
    root = Path(root).resolve()
    for path, _, files in root.walk(on_error=print):
        for file in files:
            full_name = path / file
            full_name_to_print = str(full_name)
            encoding = guess_text_encoding(full_name)
            file_size = full_name.stat().st_size
            print(f">>> {full_name_to_print} ({encoding}: {file_size} byte{'s' if file_size != 1 else ''})")
            if encoding == "BINARY":
                print(hex_dump(full_name))
            else:
                print(text_dump(full_name))
            print(f"<<< {full_name_to_print}")
            print()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        dump_file_tree(".")
    else:
        for start_dir in sys.argv[1:]:
            dump_file_tree(start_dir)
