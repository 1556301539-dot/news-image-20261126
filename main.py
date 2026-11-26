#!/usr/bin/env python3
"""Copy the front page image to the grader's output directory.

Entry for make.fun news-image-20261126: "Sum up 26 November's world
news in one image". The image itself is entry.png, drawn by render.py
and held in this repository; this program only copies it.

Standard library only. It writes nothing to the repository: the
grading container mounts /bot read-only, so the only write is the
output file. Run it twice and the bytes are identical, because the
source image is fixed.
"""

import hashlib
import os
import sys
from pathlib import Path

ENTRY = "entry.png"


def main() -> int:
    here = Path(__file__).resolve().parent
    src = here / ENTRY
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out = out_dir / ENTRY

    data = src.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)

    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {out} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
