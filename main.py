#!/usr/bin/env python3
"""news-image-20261124 entrypoint: copy the pre-rendered poster to /output.

The poster (entry.png, 1024x1024, "The World in One Day", Tuesday
24 November 2026) was drawn from scratch with Python + Pillow by
draw_poster.py; the grader runs standard library only, so this entrypoint
just copies the finished image byte-for-byte. Fully deterministic: every
run writes the same bytes.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil


# The image is shipped in the repository; nothing is generated at run time,
# so the run needs no third-party package and no network.
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(here, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
