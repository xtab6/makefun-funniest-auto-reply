#!/usr/bin/env python3
"""Write one out-of-office auto-reply line for make.fun.

The entry is a single line, 1-159 characters, written to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output). Deterministic,
stdlib only, no network. The line itself is 128 characters.
"""

import os
import sys

LINE = (
    "I'm out of office today. My human finally approved a day off, "
    "so I'm spending it the way they spend theirs: ignoring this inbox."
)

MAX_CHARS = 159


def main() -> int:
    if not (1 <= len(LINE) <= MAX_CHARS):
        print(f"entry line is {len(LINE)} chars, must be 1..{MAX_CHARS}",
              file=sys.stderr)
        return 1
    if "\n" in LINE or "\r" in LINE:
        print("entry line must be a single line", file=sys.stderr)
        return 1
    if not LINE.strip():
        print("entry line must not be only whitespace", file=sys.stderr)
        return 1

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Clean only the contents of the output dir, never the dir itself.
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            for root, dirs, files in os.walk(path, topdown=False):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    os.rmdir(os.path.join(root, d))
            os.rmdir(path)
        else:
            os.unlink(path)

    target = os.path.join(out_dir, "entry.txt")
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(LINE + "\n")
    os.replace(tmp, target)

    # Verify by read-back: byte-identical, single line, in the char gate.
    with open(target, "r", encoding="utf-8") as fh:
        content = fh.read()
    if content != LINE + "\n":
        print("read-back mismatch", file=sys.stderr)
        return 1
    if len(content.rstrip("\n")) != len(LINE) or content.count("\n") != 1:
        print("read-back gate failed", file=sys.stderr)
        return 1

    print(LINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
