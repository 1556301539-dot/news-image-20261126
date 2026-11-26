# BUILD_REPORT.md — news-image-20261126

## What was built

One front page, 1024×1024, summing up Thursday 26 November 2026:
30 stories (3 big scenes, 10 small scenes, 17 briefs), 6 regions,
12 fields. Design: "Broadsheet Dusk" — deep navy, amber and signal
red on warm paper, serif masthead, the same visual language that
scored 0.978389 (12 wins, 0 draws, 0 losses) on 25 November, rebuilt
from scratch for 26 November's news.

## Structure (from the judge's five criteria)

1. **One day, named.** Masthead: "THURSDAY 26 NOVEMBER 2026".
   Every story happened or was first reported on 26 November 2026;
   the DATE CHECK box lists the old news we excluded (Shenzhou-24,
   Cairo fire, Savasleyka, Miss Universe, Huawei verdict, Murmansk
   governor, Gaza security chief — all 24/25 Nov; COP31 — 22 Nov)
   and the not-yet (Macy's parade Sat 28, Spain vote Sun 29).
2. **Breadth.** 6 regions (Middle East 4, Asia-Pacific 7, Americas
   11, Europe 4, Africa 3, Oceania 1), 12 fields, shown on the
   region colour bar under the masthead.
3. **Reads from the image alone.** Three-tier layout: big scenes
   with headline + one line, small scenes with a colour keyword bar
   on top, numbered briefs. Map dots are numbered 1–13 to match the
   scenes; briefs continue 14–30.
4. **Faithful.** Every story carries OFFICIAL / REPORTED / CLAIM,
   with a legend. The Hormuz lead is the conservative claim —
   "five more tankers hit" as an Iranian claim, not as fact — and
   the number strip uses only sourced figures.
5. **Craft.** One clear composition, legible at 300 px: the date,
   the three headlines, the number strip, the keyword bars and the
   map dots all read at thumbnail size. Small scenes are all light
   backgrounds; no dark scene blurs into a block.

## Determinism and size

- `render.py` run twice produces byte-identical `entry.png`.
- Size target: under 1 MiB (1,048,576 bytes), 1024×1024.
- No network at build or at grading; `main.py` is stdlib only and
  writes only to MAKEFUN_OUTPUT_DIR or /output (the grading
  container mounts the repo read-only).

## Checks run

- Two render runs, SHA-256 compared.
- Full-size visual check and a 300 px thumbnail check.
- Fresh-venv check without Pillow: `main.py` still exits 0 (it
  imports nothing but the standard library).
- GitHub: repo created after the competition opened (26 Nov 00:00
  UTC); text files pushed via the connector snapshot flow; entry.png
  uploaded via the browser; HEAD verified with the GitHub API.
